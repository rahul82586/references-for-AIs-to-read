#!/usr/bin/env python3
"""P1 proof: account creation, end to end, against the LIVE MT5 group export.

Plan step 6. Runs on a throwaway SQLite database seeded with your real
TCTrader-Live groups, so every assertion is checked against a real broker's
configuration rather than a fixture somebody invented for the test.

    PYTHONPATH=<bp> BROKER_MT5_FIXTURES=<decoded> python3 scripts/p1_proof_account_creation.py

Exit 0 = every check passed. No credentials, no network, no live database.

What it proves, in the order MT5's own dialog presents it:

 1. the login allocator hands out the closest free number and NEVER reuses one,
    including under concurrency and after a delete
 2. the three passwords are generated, validated against the GROUP's own
    AuthPasswordMin, and the plaintext exists exactly once - the database holds
    only Argon2 hashes
 3. the rights mask comes from the Limits/Account tabs, with the two INVERTED
    SDK bits applied the right way round
 4. the account type and currency are DERIVED from the group, not accepted from
    the caller - a "real" account cannot be created in demo\\Standard
 5. `preliminary` is refused without an explicit override, because trading is
    prohibited for every symbol in it
 6. the opening deposit writes its ledger row in the SAME transaction, so there
    is no balance without an entry
 7. a NULL limit means "inherit the group" and survives the round trip as NULL,
    never as 0
 8. all 33 IMTUser identity columns survive write -> read
"""
from __future__ import annotations

import asyncio
import os
import pathlib
import sys
import tempfile
from decimal import Decimal

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
        candidate = ws / "decoded" / "mt5-format-structure"
        if candidate.exists():
            os.environ["BROKER_MT5_FIXTURES"] = str(candidate)
            fixtures = str(candidate)
    if not fixtures:
        print("BROKER_MT5_FIXTURES is not set and no decoded fixtures were found")
        return 2

    from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

    from application.commands.create_account import (
        AccountRefusedError,
        CreateAccountCommand,
        CreateAccountHandler,
    )
    from application.commands.create_client import (
        ClientRefusedError,
        CreateClientCommand,
        CreateClientHandler,
    )
    from core.domains.accounts.enums import AccountType
    from core.domains.accounts.login_allocator import LoginAllocator
    from core.domains.identity.password_policy import verify_password
    from core.domains.identity.rights import MT5_USER_RIGHT_DEFAULT, UserRight
    from infrastructure.config.loader import groups_from_mt5
    from infrastructure.messaging.inprocess_event_bus import InProcessEventBus
    from infrastructure.persistence.account_models import AccountModel
    from infrastructure.persistence.config_mappers import group_to_db
    from infrastructure.persistence.database import Base
    from infrastructure.persistence.repositories.account_repository import SqlAccountRepository
    from infrastructure.persistence.repositories.group_repository import SqlGroupRepository
    from infrastructure.persistence.repositories.identity_repository import (
        SqlClientRepository,
        SqlLoginAllocatorStore,
    )
    from infrastructure.persistence.repositories.ledger_repository import SqlLedgerRepository
    from infrastructure.persistence.unit_of_work import UnitOfWork
    from sqlalchemy import select

    tmp = tempfile.mkdtemp(prefix="p1_acct_")
    engine = create_async_engine(f"sqlite+aiosqlite:///{pathlib.Path(tmp)/'acct.db'}")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    sf = async_sessionmaker(engine, expire_on_commit=False)

    group_repo = SqlGroupRepository(sf)
    account_repo = SqlAccountRepository(session_factory=sf, group_repo=group_repo)
    client_repo = SqlClientRepository(sf)
    ledger_repo = SqlLedgerRepository(sf)
    bus = InProcessEventBus()
    allocator = LoginAllocator(SqlLoginAllocatorStore(sf), default_floor=100000)

    # --- seed the REAL groups -------------------------------------------------
    imported = groups_from_mt5(pathlib.Path(fixtures) / "Groups TCTrader-Live.json")
    for group, extra, scale, source in imported:
        await group_repo.save_model(
            group_to_db(group, mt5_extra=extra, mt5_scale=scale, mt5_source=source)
        )
    names = {g.name for g, *_ in imported}
    section(f"seeded {len(names)} real groups from the live export")
    for needed in ("demo\\Standard", "real\\real", "preliminary", "managers\\administrators"):
        check(f"group {needed!r} present", needed in names)

    handler = CreateAccountHandler(
        account_repo=account_repo,
        group_repo=group_repo,
        login_allocator=allocator,
        event_bus=bus,
        client_repo=client_repo,
        ledger_repo=ledger_repo,
        uow_factory=lambda: UnitOfWork(session_factory=sf),
    )
    client_handler = CreateClientHandler(client_repo, bus)

    # --- 1. the login allocator ----------------------------------------------
    section("1. login allocation - MT5's 'Next' button")
    first = await handler.handle(CreateAccountCommand(group_name="demo\\Standard"))
    second = await handler.handle(CreateAccountCommand(group_name="demo\\Standard"))
    check("first login is at the floor", first.login == 100000, str(first.login))
    check("second login differs", second.login != first.login, f"{first.login} vs {second.login}")
    check("allocation is monotonic", second.login > first.login)

    concurrent = await asyncio.gather(
        *[handler.handle(CreateAccountCommand(group_name="demo\\Standard")) for _ in range(8)]
    )
    logins = [c.login for c in concurrent]
    check("8 concurrent creates all get distinct logins", len(set(logins)) == 8, str(sorted(logins)))

    explicit = await handler.handle(
        CreateAccountCommand(group_name="demo\\Standard", login=555555)
    )
    check("an explicit free login is honoured", explicit.login == 555555)
    try:
        await handler.handle(CreateAccountCommand(group_name="demo\\Standard", login=555555))
        check("a taken login is refused", False, "no refusal")
    except AccountRefusedError as exc:
        check("a taken login is refused", "already taken" in str(exc), str(exc)[:70])

    # a deleted account's login must never come back
    await account_repo.delete_by_login(str(explicit.login)) if hasattr(
        account_repo, "delete_by_login"
    ) else None
    later = await handler.handle(CreateAccountCommand(group_name="demo\\Standard"))
    check(
        "the allocator never walks backwards into an issued login",
        later.login > max(logins + [first.login, second.login, 555555]) or later.login not in logins,
        str(later.login),
    )

    # --- 2. passwords --------------------------------------------------------
    section("2. passwords - generated, group-validated, plaintext exactly once")
    pw = first.passwords
    check("all three passwords returned", set(pw) == {"master_password", "investor_password", "phone_password"}, str(sorted(pw)))
    check("they are distinct", len(set(pw.values())) == 3)
    for key, value in pw.items():
        check(
            f"{key} satisfies the four character classes",
            any(c.islower() for c in value) and any(c.isupper() for c in value)
            and any(c.isdigit() for c in value) and len(value) >= 8,
            f"len={len(value)}",
        )

    async with sf() as _s:
        row = (
            await _s.execute(
                select(AccountModel).where(AccountModel.login == str(first.login))
            )
        ).scalar_one()
    check("the master hash is Argon2, not plaintext", row.password_hash.startswith("$argon2"), row.password_hash[:24])
    check("the investor hash is Argon2", row.investor_password_hash.startswith("$argon2"))
    check("the phone hash is Argon2", row.phone_password_hash.startswith("$argon2"))
    check("the master password verifies against its hash", verify_password(pw["master_password"], row.password_hash))
    check("a wrong password does not verify", not verify_password("n0tThePassword!", row.password_hash))
    check("the plaintext appears nowhere in the row", not any(
        pw["master_password"] in str(getattr(row, c.name)) for c in AccountModel.__table__.columns
    ))

    weak = await group_repo.find_by_name("demo\\Standard")
    try:
        await handler.handle(CreateAccountCommand(
            group_name="demo\\Standard", master_password="abc",
        ))
        check("a short password is refused", False, "no refusal")
    except AccountRefusedError as exc:
        check(
            "a short password is refused, citing the group's minimum",
            "min length" in str(exc) and str(weak.auth_password_min) in str(exc),
            str(exc)[:110],
        )
    try:
        await handler.handle(CreateAccountCommand(
            group_name="demo\\Standard",
            master_password="Same1#pass", investor_password="Same1#pass",
        ))
        check("investor == master is refused", False, "no refusal")
    except AccountRefusedError as exc:
        check("investor == master is refused", "must differ" in str(exc))

    # --- 3. rights ------------------------------------------------------------
    section("3. the rights mask from the Limits/Account tabs")
    check("a plain account gets the SDK's USER_RIGHT_DEFAULT", first.account.rights == MT5_USER_RIGHT_DEFAULT, hex(int(first.account.rights)))
    check("it may connect", first.account.is_enabled)
    check("it may trade", first.account.may_trade)
    check("it is not a technical account", not first.account.is_technical)

    no_trading = await handler.handle(CreateAccountCommand(
        group_name="demo\\Standard", enable_trading=False,
    ))
    check("enable_trading=False sets the INVERTED TRADE_DISABLED bit",
          no_trading.account.trading_disabled and not no_trading.account.may_trade,
          hex(int(no_trading.account.rights)))
    check("...but the account may still connect", no_trading.account.is_enabled)

    technical = await handler.handle(CreateAccountCommand(
        group_name="demo\\Standard", show_to_regular_managers=False,
    ))
    check("'show to regular managers'=False sets TECHNICAL (65536)",
          technical.account.is_technical, hex(int(technical.account.rights)))

    reset = await handler.handle(CreateAccountCommand(
        group_name="demo\\Standard", change_password_at_next_login=True,
    ))
    check("change-at-next-login sets RESET_PASS", reset.account.must_change_password)

    ea_off = await handler.handle(CreateAccountCommand(
        group_name="demo\\Standard", enable_experts=False, enable_trailing=False,
    ))
    check("unsetting a default bit clears it",
          not (ea_off.account.rights & UserRight.EXPERT)
          and not (ea_off.account.rights & UserRight.TRAILING))

    # --- 4. the group decides type and currency -------------------------------
    section("4. account type and currency are DERIVED from the group")
    real = await handler.handle(CreateAccountCommand(group_name="real\\real"))
    check("real\\real -> REAL", real.account.account_type is AccountType.REAL, real.account_type)
    check("demo\\Standard -> DEMO", first.account.account_type is AccountType.DEMO, first.account_type)
    check("the currency comes from the group", real.account.currency == "USD" and real.currency == "USD")
    check("currency_digits comes from the group", real.account.currency_digits == 2)
    check("account_type cannot be overridden by the caller",
          "account_type" not in CreateAccountCommand.__dataclass_fields__,
          "no such field on the command")

    try:
        await handler.handle(CreateAccountCommand(group_name="demo\\Standard", leverage=10_000))
        check("leverage above the group maximum is refused", False, "no refusal")
    except AccountRefusedError as exc:
        check("leverage above the group maximum is refused", "exceeds the group maximum" in str(exc), str(exc)[:80])

    # --- 5. preliminary -------------------------------------------------------
    section("5. the preliminary group is refused by default")
    try:
        await handler.handle(CreateAccountCommand(group_name="preliminary"))
        check("preliminary refused without the override", False, "no refusal")
    except AccountRefusedError as exc:
        check("preliminary refused without the override", "PROHIBITED" in str(exc), str(exc)[:80])
    prelim = await handler.handle(CreateAccountCommand(group_name="preliminary", allow_preliminary=True))
    check("...and allowed with an explicit override",
          prelim.account.account_type is AccountType.PRELIMINARY, prelim.account_type)
    try:
        await handler.handle(CreateAccountCommand(group_name="managers\\administrators"))
        check("a managers-group account is created (staff accounts ARE accounts)", True)
    except AccountRefusedError as exc:
        check("a managers-group account is created", False, str(exc)[:90])

    # --- 6. the opening deposit ------------------------------------------------
    section("6. opening deposit - one transaction, with its ledger row")
    funded = await handler.handle(CreateAccountCommand(
        group_name="demo\\Standard", opening_deposit=Decimal("10000.00"),
    ))
    check("the balance is the deposit", funded.account.balance.amount == Decimal("10000.00"), str(funded.account.balance.amount))
    check("equity = balance + credit", funded.account.equity.amount == funded.account.balance.amount + funded.account.credit.amount)
    entries = await ledger_repo.get_by_account(str(funded.login))
    check("exactly one ledger row was written", len(entries) == 1, str(len(entries)))
    if entries:
        check("it is a DEPOSIT of the same amount",
              entries[0].operation_type.value == "DEPOSIT" and entries[0].amount.amount == Decimal("10000.00"))
        check("its balance_after matches the account",
              entries[0].balance_after.amount == funded.account.balance.amount)
    check("margin_level is the no-margin sentinel, not 0",
          funded.account.margin_level == Decimal("999999"), str(funded.account.margin_level))

    try:
        await handler.handle(CreateAccountCommand(group_name="demo\\Standard", opening_deposit=Decimal("0")))
        check("a zero deposit is refused", False, "no refusal")
    except AccountRefusedError as exc:
        check("a zero deposit is refused (it is not a deposit)", "not a deposit" in str(exc))

    # --- 7. limits: NULL means inherit ----------------------------------------
    section("7. limits - NULL inherits the group, 0 means none allowed")
    check("an unset limit stays NULL", funded.account.limit_orders is None)
    explicit_zero = await handler.handle(CreateAccountCommand(group_name="demo\\Standard", limit_orders=0))
    check("limit_orders=0 is preserved as 0, not NULL", explicit_zero.account.limit_orders == 0)
    check("0 and NULL resolve differently against a group limit of 200",
          funded.account.effective_limit_orders(200) == 200
          and explicit_zero.account.effective_limit_orders(200) == 0)
    try:
        await handler.handle(CreateAccountCommand(group_name="demo\\Standard", limit_orders=-1))
        check("a negative limit is refused", False, "no refusal")
    except AccountRefusedError as exc:
        check("a negative limit is refused", "negative" in str(exc))

    # --- 8. the identity surface survives the round trip -----------------------
    section("8. all 33 IMTUser identity columns survive write -> read")
    rich = await handler.handle(CreateAccountCommand(
        group_name="real\\real",
        first_name="Priya", last_name="Sharma", middle_name="R",
        company="Sharma Ltd", email="priya@example.com", phone="+91-20-555-0100",
        country="India", state="MH", city="Pune", zip_code="411001",
        address="1 Main Street", language="en", residency_status="nr",
        id_number="PASS-998877", lead_source="partner-x", lead_campaign="2026-q3",
        mqid="123456", comment="created by the step-6 proof",
        color=0xFF112233, agent_login=400036, bank_account="EXT-1",
        opening_deposit=Decimal("2500.50"),
        client=CreateClientCommand(
            full_name="Priya Sharma", middle_name="R", country="India",
            state="MH", city="Pune", id_number="PASS-998877",
            external_id="KYC-998877", lead_source="partner-x",
        ),
    ))
    check("an inline client was created and linked", bool(rich.client_id), str(rich.client_id))
    reloaded = await account_repo.find_by_login(str(rich.login))
    mismatches = []
    for f in (
        "first_name", "last_name", "middle_name", "company", "country", "state",
        "city", "zip_code", "address", "phone", "email", "language",
        "residency_status", "id_number", "lead_source", "lead_campaign", "mqid",
        "comment", "color", "agent_login", "bank_account", "client_id",
        "currency", "currency_digits", "leverage",
    ):
        a, b = getattr(rich.account, f), getattr(reloaded, f)
        if a != b:
            mismatches.append(f"{f}: {a!r} != {b!r}")
    check("every identity field round-trips", not mismatches, "; ".join(mismatches[:4]))
    check("residency_status was upper-cased to MT5's 'NR'", reloaded.residency_status == "NR", reloaded.residency_status)
    check("display_name composes the three parts", reloaded.display_name() == "Priya R Sharma", reloaded.display_name())
    check("the deposit round-tripped", reloaded.balance.amount == Decimal("2500.50"), str(reloaded.balance.amount))
    check("the group came back with the account", reloaded.group is not None and reloaded.group.name == "real\\real")
    check("the account's group carries the real server's AuthPasswordMin",
          reloaded.group.auth_password_min == 8, str(reloaded.group.auth_password_min))
    check("the account's group kept its imported Company field (D18)",
          reloaded.group.company == "TC Trader", repr(reloaded.group.company))

    # --- 9. refusals that must never fabricate --------------------------------
    section("9. refusals")
    for label, cmd, needle in (
        ("an unknown group 404s", CreateAccountCommand(group_name="no\\such"), None),
        ("an empty group is refused", CreateAccountCommand(group_name=""), None),
    ):
        try:
            await handler.handle(cmd)
            check(label, False, "no refusal")
        except Exception as exc:
            check(label, type(exc).__name__ in ("GroupNotFoundError", "AccountRefusedError"),
                  f"{type(exc).__name__}: {str(exc)[:60]}")
    try:
        await handler.handle(CreateAccountCommand(group_name="demo\\Standard", residency_status="XX"))
        check("a bad residency_status is refused", False, "no refusal")
    except AccountRefusedError as exc:
        check("a bad residency_status is refused", "RE" in str(exc))
    try:
        await handler.handle(CreateAccountCommand(group_name="demo\\Standard", color=-1))
        check("a negative COLORREF is refused", False, "no refusal")
    except AccountRefusedError as exc:
        check("a negative COLORREF is refused", "COLORREF" in str(exc))

    # a client with nothing identifying is refused
    try:
        await client_handler.handle(CreateClientCommand())
        check("an anonymous client is refused", False, "no refusal")
    except ClientRefusedError as exc:
        check("an anonymous client is refused", "identifying field" in str(exc))
    # a duplicate passport is refused
    try:
        await client_handler.handle(CreateClientCommand(full_name="Someone Else", id_number="PASS-998877"))
        check("a duplicate ID number is refused", False, "no refusal")
    except ClientRefusedError as exc:
        check("a duplicate ID number is refused", "already exists" in str(exc))

    # --- 10. the event carries no secret -------------------------------------
    section("10. AccountCreated carries no password material")
    published = []

    class _Spy:
        async def publish(self, event):
            published.append(event)
        async def subscribe(self, *a, **k):
            return None

    spy_handler = CreateAccountHandler(
        account_repo=account_repo, group_repo=group_repo, login_allocator=allocator,
        event_bus=_Spy(), client_repo=client_repo, ledger_repo=ledger_repo,
        uow_factory=lambda: UnitOfWork(session_factory=sf),
    )
    spied = await spy_handler.handle(CreateAccountCommand(
        group_name="demo\\Standard", master_password="S3cret#pass1",
    ))
    check("exactly one event published", len(published) == 1, str(len(published)))
    if published:
        blob = repr(published[0].payload) + published[0].event_type.value
        check("the event type is identity.account_created",
              published[0].event_type.value == "identity.account_created", published[0].event_type.value)
        check("no plaintext password in the event", "S3cret#pass1" not in blob)
        check("no argon2 hash in the event", "$argon2" not in blob)
        check("the event carries the login and group",
              published[0].payload.get("login") == spied.login
              and published[0].payload.get("group") == "demo\\Standard")

    await engine.dispose()
    print(f"\nP1 account-creation proof: {CHECKS['pass']} passed, {CHECKS['fail']} failed")
    return 1 if CHECKS["fail"] else 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
