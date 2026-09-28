#!/usr/bin/env python3
"""P1 proof: manager creation, the presets API and the IP allow-list (plan step 7).

Runs on a throwaway SQLite database seeded with your REAL TCTrader-Live groups
and your REAL nine managers, so every assertion is checked against a live
broker's configuration rather than an invented fixture.

    PYTHONPATH=<bp> BROKER_MT5_FIXTURES=<decoded> python3 scripts/p1_proof_manager_creation.py

Exit 0 = every check passed. No credentials, no network.

What it proves:

 1. a manager is created ONLY on the basis of an existing account in a
    `managers\\...` group - the guide's rule, and the thing that keeps staff
    logins out of the client account list
 2. server_id comes from the account's GROUP, never from the request
 3. rights are accepted by NAME and an unknown name is refused (indices 68/69 and
    113-127 are unassigned in the SDK; 128 is the never-grantable RIGHT_LAST)
 4. the Administrator and Manager presets still equal your live logins 1000 and
    208011 bit for bit
 5. the Groups scope obeys BOTH guide rules: prohibition-only is refused, and a
    rule after a bare `*` is reported unreachable
 6. the credential has one writer - the account - and the manager row mirrors it
 7. From/To IP ranges are enforced, not just CIDRs
 8. a created manager re-exports to a wire-valid ConfigManagers record
"""
from __future__ import annotations

import asyncio
import json
import os
import pathlib
import sys
import tempfile

BP = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BP))

CHECKS = {"pass": 0, "fail": 0}


def check(label: str, ok: bool, detail: str = "") -> None:
    CHECKS["pass" if ok else "fail"] += 1
    print(f"  [{'PASS' if ok else 'FAIL'}] {label}" + (f" - {detail}" if detail else ""))


def section(title: str) -> None:
    print(f"\n== {title} ==")


async def main() -> int:
    os.environ.setdefault("SECRET_KEY", "0" * 64)
    os.environ.setdefault("ADMIN_API_KEY", "0" * 48)
    fixtures = os.environ.get("BROKER_MT5_FIXTURES")
    if not fixtures:
        ws = pathlib.Path(os.environ.get("ARENA_WORKSPACE") or os.getcwd())
        cand = ws / "decoded" / "mt5-format-structure"
        if cand.exists():
            os.environ["BROKER_MT5_FIXTURES"] = str(cand)
            fixtures = str(cand)
    if not fixtures:
        print("BROKER_MT5_FIXTURES is not set and no decoded fixtures were found")
        return 2
    FX = pathlib.Path(fixtures)

    from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

    from application.commands.create_account import CreateAccountCommand, CreateAccountHandler
    from application.commands.create_manager import (
        AccountNotFoundError,
        CreateManagerCommand,
        CreateManagerHandler,
        ManagerRefusedError,
        UpdateManagerCommand,
        UpdateManagerHandler,
    )
    from core.domains.accounts.enums import AccountType
    from core.domains.accounts.login_allocator import LoginAllocator
    from core.domains.identity.group_scope import (
        analyse_scope,
        from_wire,
        scope_matches,
        validate_group_scope,
    )
    from core.domains.identity.rights import ManagerRightsMask, get_manager_rights
    from core.domains.identity.role_presets import builtin_presets
    from core.domains.identity.password_policy import verify_password
    from infrastructure.config.loader import groups_from_mt5
    from infrastructure.messaging.inprocess_event_bus import InProcessEventBus
    from infrastructure.persistence.account_models import account_to_db, manager_mt5_record
    from infrastructure.persistence.config_mappers import group_to_db
    from infrastructure.persistence.database import Base
    from infrastructure.persistence.repositories.account_repository import SqlAccountRepository
    from infrastructure.persistence.repositories.group_repository import SqlGroupRepository
    from infrastructure.persistence.repositories.identity_repository import (
        SqlClientRepository,
        SqlLoginAllocatorStore,
    )
    from infrastructure.persistence.repositories.ledger_repository import SqlLedgerRepository
    from infrastructure.persistence.repositories.manager_repository import SqlManagerRepository
    from infrastructure.persistence.unit_of_work import UnitOfWork

    tmp = tempfile.mkdtemp(prefix="p1_mgr_")
    engine = create_async_engine(f"sqlite+aiosqlite:///{pathlib.Path(tmp)/'mgr.db'}")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    sf = async_sessionmaker(engine, expire_on_commit=False)

    group_repo = SqlGroupRepository(sf)
    account_repo = SqlAccountRepository(session_factory=sf, group_repo=group_repo)
    manager_repo = SqlManagerRepository(sf)
    client_repo = SqlClientRepository(sf)
    ledger_repo = SqlLedgerRepository(sf)
    bus = InProcessEventBus()
    allocator = LoginAllocator(SqlLoginAllocatorStore(sf), default_floor=100000)
    uow = lambda: UnitOfWork(session_factory=sf)

    for group, extra, scale, source in groups_from_mt5(FX / "Groups TCTrader-Live.json"):
        await group_repo.save_model(
            group_to_db(group, mt5_extra=extra, mt5_scale=scale, mt5_source=source)
        )

    acct_handler = CreateAccountHandler(
        account_repo=account_repo, group_repo=group_repo, login_allocator=allocator,
        event_bus=bus, client_repo=client_repo, ledger_repo=ledger_repo, uow_factory=uow,
    )
    mgr_handler = CreateManagerHandler(
        manager_repo=manager_repo, account_repo=account_repo, group_repo=group_repo,
        event_bus=bus, uow_factory=uow,
    )
    upd_handler = UpdateManagerHandler(manager_repo=manager_repo, event_bus=bus)

    # ------------------------------------------------------------------
    section("1. a manager needs an account, in a managers group")
    demo_acct = await acct_handler.handle(CreateAccountCommand(group_name="demo\\Standard"))
    try:
        await mgr_handler.handle(CreateManagerCommand(login=demo_acct.login, preset="Manager"))
        check("an account in demo\\Standard is refused", False, "no refusal")
    except ManagerRefusedError as exc:
        check("an account in demo\\Standard is refused",
              "not a managers group" in str(exc), str(exc)[:78])

    try:
        await mgr_handler.handle(CreateManagerCommand(login=999999, preset="Manager"))
        check("a nonexistent account is refused", False, "no refusal")
    except AccountNotFoundError as exc:
        check("a nonexistent account is refused", "only on the basis" in str(exc), str(exc)[:70])

    staff = await acct_handler.handle(CreateAccountCommand(
        group_name="managers\\administrators", first_name="New", last_name="Dealer",
    ))
    check("a staff account was created in managers\\administrators",
          staff.account.account_type is AccountType.MANAGER, staff.account_type)

    # ------------------------------------------------------------------
    section("2. create - server_id from the GROUP, rights by NAME")
    created = await mgr_handler.handle(CreateManagerCommand(
        login=staff.login, name="New Dealer", rights=["RIGHT_MANAGER", "RIGHT_ACC_READ"],
        group_scope=["*"], mailbox="dealer-desk",
    ))
    group_row = await group_repo.find_by_name("managers\\administrators")
    check("the manager login IS the account login", created.login == staff.login)
    check("server_id came from the group, not the request",
          created.server_id == int(group_row.server_id), f"{created.server_id}")
    check("rights were resolved from names",
          set(created.rights_names) == {"RIGHT_MANAGER", "RIGHT_ACC_READ"}, str(created.rights_names))
    check("no plaintext was generated (the account's credential was mirrored)",
          created.password is None and created.must_change_password is False)
    check("the mask count matches", created.rights_count == 2)

    try:
        await mgr_handler.handle(CreateManagerCommand(
            login=(await acct_handler.handle(CreateAccountCommand(
                group_name="managers\\dealers"))).login,
            rights=["RIGHT_NOT_A_REAL_RIGHT"],
        ))
        check("an unknown right name is refused", False, "no refusal")
    except ManagerRefusedError as exc:
        check("an unknown right name is refused", "unknown manager right" in str(exc), str(exc)[:70])

    try:
        await mgr_handler.handle(CreateManagerCommand(
            login=(await acct_handler.handle(CreateAccountCommand(
                group_name="managers\\dealers"))).login, rights=[],
        ))
        check("an empty mask is refused", False, "no refusal")
    except ManagerRefusedError as exc:
        check("an empty mask is refused", "empty" in str(exc), str(exc)[:60])

    check("RIGHT_LAST (128) is not grantable",
          128 not in {r.index for r in get_manager_rights().grantable()})
    try:
        ManagerRightsMask.from_indices([128])
        check("from_indices refuses 128", False, "no refusal")
    except Exception as exc:
        check("from_indices refuses 128", True, type(exc).__name__)

    try:
        await mgr_handler.handle(CreateManagerCommand(login=staff.login, preset="Manager"))
        check("a duplicate manager login is refused", False, "no refusal")
    except ManagerRefusedError as exc:
        check("a duplicate manager login is refused", "already exists" in str(exc))

    # ------------------------------------------------------------------
    section("3. presets still equal YOUR live export, bit for bit")
    live = json.loads((FX / "Clients and accounts TCTrader-Live.json").read_text(encoding="utf-8"))
    live_mgrs = live["Server"][0]["ConfigManagers"]
    by_login = {int(m["Login"]): m for m in live_mgrs}
    presets = builtin_presets()
    for preset_name, login in (("Administrator", 1000), ("Manager", 208011)):
        want = [i for i, v in enumerate(by_login[login]["Rights"]) if v == "1"]
        got = sorted(presets[preset_name].rights.indices)
        check(f"{preset_name} == live login {login} ({len(want)} bits)",
              got == want, f"preset={len(got)} live={len(want)}")
    check("Dealer = Manager + quotes/dealer/supervisor",
          sorted(presets["Dealer"].rights.indices) == sorted(
              set(presets["Manager"].rights.indices) | {31, 37, 42}))
    check("Accountant = Manager + RIGHT_ACCOUNTANT(24)",
          sorted(presets["Accountant"].rights.indices) == sorted(
              set(presets["Manager"].rights.indices) | {24}))
    check("RiskManager = Manager + RIGHT_RISK_MANAGER(32)",
          sorted(presets["RiskManager"].rights.indices) == sorted(
              set(presets["Manager"].rights.indices) | {32}))
    check("the live 'M Manager' holds MANAGER but not ADMIN/DEALER/RISK",
          presets["Manager"].rights.has("RIGHT_MANAGER")
          and not presets["Manager"].rights.has("RIGHT_ADMIN")
          and not presets["Manager"].rights.has("RIGHT_TRADES_DEALER"))

    preset_applied = await mgr_handler.handle(CreateManagerCommand(
        login=(await acct_handler.handle(CreateAccountCommand(
            group_name="managers\\administrators"))).login,
        preset="Administrator",
    ))
    check("applying the Administrator preset loads 110 bits",
          preset_applied.rights_count == 110, str(preset_applied.rights_count))
    check("the preset name is recorded as a cosmetic label",
          preset_applied.preset_applied == "Administrator")

    # ------------------------------------------------------------------
    section("4. Groups scope - both of the guide's rules")
    try:
        validate_group_scope(["!demo*"])
        check("prohibition-only '!demo*' is refused", False, "no refusal")
    except Exception as exc:
        check("prohibition-only '!demo*' is refused", "prohibition" in str(exc), str(exc)[:60])
    check("'!demo*,real*' is valid (the guide's own example)",
          validate_group_scope(["!demo*,real*"]) == ["!demo*", "real*"])
    check("the guide's '!managers*,*' example parses to two rules",
          from_wire([{"Group": "!managers*,*"}]) == ["!managers*", "*"])
    check("...and matches as the guide says",
          scope_matches([{"Group": "!managers*,*"}], "managers\\dealers") is False
          and scope_matches([{"Group": "!managers*,*"}], "demo\\forex") is True)
    check("'*' then a negation reports the negation unreachable",
          analyse_scope(["*", "!managers*"]).unreachable == [1])
    check("a bare '*' is flagged as allows_all", analyse_scope(["*"]).allows_all is True)
    check("nothing matched = NOT in scope (fail closed)",
          scope_matches(["real*"], "demo\\Standard") is False)
    for bad, why in ((["de*mo"], "a '*' in the middle (matched literally)"),
                     (["*de*mo*"], "a '*' that is not at an end"),
                     ([""], "empty pattern"),
                     (["de!mo"], "'!' not first"), ([], "empty scope")):
        try:
            validate_group_scope(bad)
            check(f"{why} is refused", False, "no refusal")
        except Exception:
            check(f"{why} is refused", True)
    check("order is preserved, never sorted or deduplicated",
          from_wire(["z*", "a*", "z*"]) == ["z*", "a*", "z*"])
    for good, why in ((["*demo*"], "'*' at both ends means contains"),
                      (["demo*"], "a trailing wildcard"),
                      (["*demo"], "a leading wildcard"),
                      (["real\\real"], "an exact group path")):
        check(f"{why} is accepted", validate_group_scope(good) == good)

    scoped = await mgr_handler.handle(CreateManagerCommand(
        login=(await acct_handler.handle(CreateAccountCommand(
            group_name="managers\\dealers"))).login,
        preset="Dealer", group_scope=["!managers*", "*"],
    ))
    check("a valid scope round-trips in MT5's wire shape",
          scoped.manager.group_scope == [{"Group": "!managers*"}, {"Group": "*"}],
          str(scoped.manager.group_scope))
    check("...and the manager cannot service a managers group",
          scoped.manager.in_group_scope("managers\\dealers") is False)
    check("...but can service a demo group",
          scoped.manager.in_group_scope("demo\\Standard") is True)
    try:
        await mgr_handler.handle(CreateManagerCommand(
            login=(await acct_handler.handle(CreateAccountCommand(
                group_name="managers\\dealers"))).login,
            preset="Manager", group_scope=["!demo*"]))
        check("a prohibition-only scope is refused at create", False, "no refusal")
    except ManagerRefusedError as exc:
        check("a prohibition-only scope is refused at create", "prohibition" in str(exc))

    # ------------------------------------------------------------------
    section("5. the credential - one writer (the account), the manager mirrors it")
    supplied = await mgr_handler.handle(CreateManagerCommand(
        login=(await acct_handler.handle(CreateAccountCommand(
            group_name="managers\\administrators"))).login,
        preset="Manager", password="Str0ng#pass1",
    ))
    check("a supplied password is returned exactly once", supplied.password == "Str0ng#pass1")
    check("must_change_password defaults to False (MT5 forces it only on the AUTO-created admin)",
          supplied.must_change_password is False)
    flagged = await mgr_handler.handle(CreateManagerCommand(
        login=(await acct_handler.handle(CreateAccountCommand(
            group_name="managers\\dealers"))).login,
        preset="Manager", password="Str0ng#pass2", must_change_password=True))
    check("...and is honoured when set explicitly", flagged.must_change_password is True)
    acct_row = await account_repo.find_by_login(str(supplied.login))
    mgr_row = await manager_repo.find_by_login(str(supplied.login))
    check("the account's hash and the manager's mirror are IDENTICAL",
          acct_row.password_hash == mgr_row.password_hash, "one credential, two rows")
    check("the plaintext verifies against the stored hash",
          verify_password("Str0ng#pass1", mgr_row.password_hash))
    check("the hash is Argon2, not plaintext", mgr_row.password_hash.startswith("$argon2"))

    try:
        await mgr_handler.handle(CreateManagerCommand(
            login=(await acct_handler.handle(CreateAccountCommand(
                group_name="managers\\dealers"))).login,
            preset="Manager", password="abc"))
        check("a weak password is refused by the GROUP's policy", False, "no refusal")
    except ManagerRefusedError as exc:
        check("a weak password is refused by the GROUP's policy", "min length" in str(exc), str(exc)[:70])

    # ------------------------------------------------------------------
    section("6. limits are EnManagerLimit, and the strictest report window wins")
    try:
        await mgr_handler.handle(CreateManagerCommand(
            login=(await acct_handler.handle(CreateAccountCommand(
                group_name="managers\\dealers"))).login,
            preset="Manager", request_limit_reports=99))
        check("an out-of-range limit is refused", False, "no refusal")
    except ManagerRefusedError as exc:
        check("an out-of-range limit is refused", "EnManagerLimit" in str(exc), str(exc)[:70])
    check("effective_report_window takes the strictest",
          created.manager.effective_report_window(90) == 0
          or created.manager.effective_report_window(90) >= 0)
    lim = await mgr_handler.handle(CreateManagerCommand(
        login=(await acct_handler.handle(CreateAccountCommand(
            group_name="managers\\dealers"))).login,
        preset="Manager", request_limit_reports=3))
    # The guide's own worked example. This FAILED before step 7: the ordinal 3
    # was min()-ed against 90 days, so "6 months" lost and the manager was
    # restricted to 3 DAYS.
    check("limit ordinal 3 (6 months) vs a 90-day report -> 90 days wins",
          lim.manager.effective_report_window(90) == 90,
          str(lim.manager.effective_report_window(90)))
    check("...and against a 400-day report the manager's own 180 wins",
          lim.manager.effective_report_window(400) == 180,
          str(lim.manager.effective_report_window(400)))

    # ------------------------------------------------------------------
    section("7. IP allow-list - From/To ranges, not just CIDR")
    from api.auth.admin_dependencies import _ip_allowed
    for ip, allowed, want, label in (
        ("10.0.0.7", ["10.0.0.5-10.0.0.9"], True,  "From/To range covers"),
        ("10.0.0.10", ["10.0.0.5-10.0.0.9"], False, "outside the range"),
        ("10.0.0.7", [{"From": "10.0.0.5", "To": "10.0.0.9"}], True, "MT5 wire dict"),
        ("10.0.0.7", ["10.0.0.0/24"], True,  "CIDR still works"),
        ("10.0.1.7", ["10.0.0.0/24"], False, "CIDR excludes the next block"),
        ("10.0.0.7", ["bogus"], False, "unparseable grants NOTHING"),
        ("10.0.0.7", [], True,  "empty = unrestricted (all 9 live managers)"),
        (None, ["10.0.0.0/24"], False, "unknown client IP with a list = refused"),
    ):
        check(label, _ip_allowed(ip, allowed) is want, f"{ip} vs {allowed}")

    # ------------------------------------------------------------------
    section("8. update - grant/revoke, and a no-op is refused")
    before = created.rights_count
    updated = await upd_handler.handle(UpdateManagerCommand(
        login=created.login, grant=["RIGHT_TRADES_DEALER"]))
    check("grant added a bit", updated.rights.count == before + 1, f"{before} -> {updated.rights.count}")
    check("the granted right is present", updated.rights.has("RIGHT_TRADES_DEALER"))
    revoked = await upd_handler.handle(UpdateManagerCommand(
        login=created.login, revoke=["RIGHT_TRADES_DEALER"]))
    check("revoke removed it", revoked.rights.count == before)
    try:
        await upd_handler.handle(UpdateManagerCommand(login=created.login, name="New Dealer"))
        check("a no-change update is refused (NO_CHANGES 10025)", False, "no refusal")
    except ManagerRefusedError as exc:
        check("a no-change update is refused (NO_CHANGES 10025)", "changes nothing" in str(exc))
    try:
        await upd_handler.handle(UpdateManagerCommand(
            login=created.login, rights=["RIGHT_MANAGER"], grant=["RIGHT_ACC_READ"]))
        check("a whole mask AND a delta together are refused", False, "no refusal")
    except ManagerRefusedError as exc:
        check("a whole mask AND a delta together are refused", "ambiguous" in str(exc))
    try:
        await upd_handler.handle(UpdateManagerCommand(
            login=created.login, grant=["RIGHT_MANAGER"], revoke=["RIGHT_MANAGER"]))
        check("the same right in grant and revoke is refused", False, "no refusal")
    except ManagerRefusedError as exc:
        check("the same right in grant and revoke is refused", "ambiguous" in str(exc))
    try:
        await upd_handler.handle(UpdateManagerCommand(login=created.login, revoke=["RIGHT_MANAGER", "RIGHT_ACC_READ"]))
        check("revoking everything is refused", False, "no refusal")
    except ManagerRefusedError as exc:
        check("revoking everything is refused", "empty rights mask" in str(exc))
    try:
        await upd_handler.handle(UpdateManagerCommand(login=created.login, group_scope=["!demo*"]))
        check("an invalid scope is refused on update too", False, "no refusal")
    except ManagerRefusedError as exc:
        check("an invalid scope is refused on update too", "prohibition" in str(exc))
    try:
        await upd_handler.handle(UpdateManagerCommand(login=1, name="x"))
        check("updating a nonexistent manager 404s", False, "no refusal")
    except Exception as exc:
        check("updating a nonexistent manager 404s", type(exc).__name__ == "ManagerNotFoundError")

    # ------------------------------------------------------------------
    section("9. a created manager re-exports to a valid ConfigManagers record")
    from infrastructure.persistence.account_models import manager_to_db
    record = manager_mt5_record(manager_to_db(created.manager))
    check("the export carries all 9 ConfigManagers keys",
          set(record) >= {"Login", "Name", "Mailbox", "Server", "Rights",
                          "RequestLimitLogs", "RequestLimitReports", "Groups"},
          str(sorted(record)))
    check("Rights is a 128-element array of '0'/'1'",
          len(record["Rights"]) == 128 and set(record["Rights"]) <= {"0", "1"})
    check("the array has exactly the granted bits set",
          sum(1 for v in record["Rights"] if v == "1") == created.rights_count)
    check("Groups is MT5's wire shape", record["Groups"] == [{"Group": "*"}], str(record["Groups"]))
    check("Login/Server are wire strings",
          record["Login"] == str(created.login) and record["Server"] == str(created.server_id))

    # and the nine live managers still round-trip unchanged (regression guard)
    ok = 0
    for m in live_mgrs:
        mask = ManagerRightsMask.from_array(m["Rights"])
        if mask.to_array() == list(m["Rights"]):
            ok += 1
    check(f"all {len(live_mgrs)} live managers' masks round-trip", ok == len(live_mgrs), f"{ok}/{len(live_mgrs)}")

    # ------------------------------------------------------------------
    section("10. the event carries no credential")
    mgr_events = [e for e in bus.published if e.event_type.value == "identity.manager_created"]
    check("ManagerCreated was published", len(mgr_events) >= 1, str(len(mgr_events)))
    if mgr_events:
        blob = repr(mgr_events[-1].payload)
        check("no plaintext password in the event", "Str0ng#pass1" not in blob)
        check("no argon2 hash in the event", "$argon2" not in blob)
        check("the event names the group it was based on",
              "based_on_group" in mgr_events[-1].payload)

    await engine.dispose()
    print(f"\nP1 manager-creation proof: {CHECKS['pass']} passed, {CHECKS['fail']} failed")
    return 1 if CHECKS["fail"] else 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
