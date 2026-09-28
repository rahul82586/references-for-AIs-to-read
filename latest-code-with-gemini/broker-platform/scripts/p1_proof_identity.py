#!/usr/bin/env python3
"""P1 proof: the identity plane against the LIVE TCTrader-Live export.

The fixture is the point (IDENTITY-BUILD-PLAN rule 4): every rights/preset
assertion is checked against the nine real managers on the user's server, not
against a reading of the docs. If RolePreset.Administrator does not equal login
1000's Rights array bit for bit, the model is wrong.

Covers, offline except for the fixture files:
  1. all 9 export managers survive array -> mask -> array byte-identically
  2. the DB storage path (three 43-bit mask words) round-trips the same arrays
  3. the builtin presets EQUAL the export's admin (1000) and M Manager (208011)
  4. rights are decodable to names and back (the 39-bit manager lacks
     RIGHT_CFG_GROUPS - the fact the enforcement demo turns on)
  5. require_right(): the named bit is enforced over real HTTP (200/403/401),
     an unknown manager is NEVER fabricated (anti-F2)
  6. a group created through the new write path exports to a wire-valid
     ConfigGroups record (the signature guarantee, where it could break)

Run:
    PYTHONPATH=<bp> BROKER_MT5_FIXTURES=<decoded dir> python3 scripts/p1_proof_identity.py

Exit 0 = every check passed.
"""
from __future__ import annotations

import json
import os
import pathlib
import sys

BP = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BP))

FIXTURES = pathlib.Path(os.environ.get("BROKER_MT5_FIXTURES", ""))
if not FIXTURES.is_dir():
    print("BROKER_MT5_FIXTURES must point at the DECODED mt5-format-structure directory")
    sys.exit(2)

CHECKS = {"pass": 0, "fail": 0}


def check(label: str, ok: bool, detail: str = "") -> None:
    CHECKS["pass" if ok else "fail"] += 1
    print(f"  [{'PASS' if ok else 'FAIL'}] {label}" + (f" - {detail}" if detail else ""))


def main() -> int:
    from core.domains.identity.models import ManagerAccount, ManagerRole
    from core.domains.identity.rights import ManagerRightsMask
    from core.domains.identity.role_presets import builtin_presets
    from infrastructure.persistence.account_models import (
        masks_to_rights, rights_to_masks, db_to_manager, manager_to_db, manager_mt5_record,
    )

    export = json.loads(
        (FIXTURES / "Clients and accounts TCTrader-Live.json").read_text(encoding="utf-8")
    )
    managers = export["Server"][0]["ConfigManagers"]
    check("live export carries 9 managers", len(managers) == 9, f"found {len(managers)}")

    print("== 1+2. every real manager survives mask and DB packing ==")
    masks_by_login = {}
    for m in managers:
        login = str(m["Login"])
        array = [str(v) for v in m["Rights"]]
        mask = ManagerRightsMask.from_array(array)
        check(f"{login}: array round-trip", mask.to_array() == array,
              f"{mask.count} bits")
        words = mask.to_masks()
        check(f"{login}: 43-bit words round-trip", masks_to_rights(list(words)) == array)
        check(f"{login}: storage packing agrees", rights_to_masks(array) == list(words))
        masks_by_login[login] = mask

    print("== 3. the builtin presets ARE the export's arrays ==")
    presets = builtin_presets()
    check("Administrator == login 1000 (110 bits)",
          presets["Administrator"].rights == masks_by_login["1000"]
          and presets["Administrator"].count == 110)
    check("Manager == login 208011 (39 bits)",
          presets["Manager"].rights == masks_by_login["208011"]
          and presets["Manager"].count == 39)
    for login in ("2000", "3000", "19226", "208013", "123333"):
        check(f"login {login} equals the Administrator preset",
              masks_by_login[login] == presets["Administrator"].rights)
    # the export's two special managers, per ACCOUNT-GROUP-CREATION-SPEC §1.
    # 400036 is a bespoke 46-bit set (it is NOT Manager+RISK: it also carries
    # EMAIL/ACC_ONLINE/QUOTES/REPORTS/EXPORT/SYMBOL_DETAILS/GRP_MARGIN/
    # CONFIRM_ACTIONS/CLIENTS_DELETE and lacks TRADES_SUPERVISOR + the two
    # ACC_TECHNICAL bits) - assert the role analysis, not a false equation.
    m36 = masks_by_login["400036"]
    check("400036 = 46 bits, MANAGER + RISK present, ADMIN/ACCOUNTANT/DEALER absent",
          m36.count == 46 and m36.has("RIGHT_MANAGER") and m36.has("RIGHT_RISK_MANAGER")
          and not m36.has("RIGHT_ADMIN") and not m36.has("RIGHT_ACCOUNTANT")
          and not m36.has("RIGHT_TRADES_DEALER"))
    check("400034 holds no role bit (41 bits, API/technical login)",
          masks_by_login["400034"].count == 41
          and not masks_by_login["400034"].has("RIGHT_ADMIN")
          and not masks_by_login["400034"].has("RIGHT_MANAGER"))

    print("== 4. names decode and re-encode ==")
    mm = masks_by_login["208011"]
    names = mm.to_names()
    unnamed = mm.unnamed_indices()
    check("39-bit manager decodes to 31 names + the 8 reserved bits 2-9",
          len(names) == 31 and unnamed == [2, 3, 4, 5, 6, 7, 8, 9],
          f"{len(names)} names, unnamed={unnamed}")
    check("re-encoding the names reproduces every NAMED bit (wire bits survive via the array)",
          ManagerRightsMask.from_names(names) == ManagerRightsMask.from_indices(
              [i for i in mm.indices if i not in unnamed]))
    check("the full mask still round-trips through the wire array", mm.to_array() == mm.to_array()
          and ManagerRightsMask.from_array(mm.to_array()) == mm)
    check("it lacks RIGHT_CFG_GROUPS", not mm.has("RIGHT_CFG_GROUPS"))
    check("it holds RIGHT_TRADES_READ", mm.has("RIGHT_TRADES_READ"))
    check("admins carry the two unassigned bits 68/69 (wire preservation)",
          masks_by_login["1000"].has(68) and masks_by_login["1000"].has(69)
          and 68 in masks_by_login["1000"].unnamed_indices())

    print("== 5. manager_mt5_record re-exports a stored manager losslessly ==")
    for m in managers:
        login = str(m["Login"])
        entity = ManagerAccount(
            manager_id=login, login=login, role=ManagerRole.READ_ONLY,
            password_hash="x", name=str(m.get("Name", "")),
            mailbox=str(m.get("Mailbox", "")), server_id=int(m.get("Server", 1) or 1),
            rights=masks_by_login[login],
            group_scope=list(m.get("Groups") or []),
            request_limit_logs=int(m.get("RequestLimitLogs", 0) or 0),
            request_limit_reports=int(m.get("RequestLimitReports", 0) or 0),
        )
        record = manager_mt5_record(manager_to_db(entity, mt5_source=dict(m)))
        same = all(str(record.get(k)) == str(v) for k, v in m.items()
                   if k in {"Login", "Name", "Mailbox", "Server", "Rights",
                            "RequestLimitLogs", "RequestLimitReports", "Groups"})
        check(f"{login}: owned wire fields re-export identical", same)

    print("== 6. require_right enforced over real HTTP ==")
    from fastapi import Depends, FastAPI
    from fastapi.testclient import TestClient

    from api.auth.admin_dependencies import require_right
    from api.auth.jwt_handler import create_access_token
    from api.di_providers import _container, register_di_providers

    class _Repo:
        def __init__(self, managers):
            self.by_login = {str(x.login): x for x in managers}

        async def find_by_login(self, login):
            return self.by_login.get(str(login))

    with_cfg = ManagerAccount(
        manager_id="777", login="777", role=ManagerRole.READ_ONLY, password_hash="x",
        rights=ManagerRightsMask.from_names(["RIGHT_CFG_GROUPS"]),
    )
    without_cfg = ManagerAccount(
        manager_id="208011", login="208011", role=ManagerRole.READ_ONLY, password_hash="x",
        rights=masks_by_login["208011"],  # the REAL 39-bit mask from the export
    )
    saved = _container.get("manager_repo")
    register_di_providers({"manager_repo": _Repo([with_cfg, without_cfg])})
    app = FastAPI()

    @app.get("/cfg")
    async def cfg_route(principal=Depends(require_right("RIGHT_CFG_GROUPS"))):
        return {"login": principal.login}

    try:
        with TestClient(app) as client:
            def bearer(login):
                return {"Authorization": f"Bearer {create_access_token({'sub': login, 'is_manager': True})}"}

            r = client.get("/cfg", headers=bearer("777"))
            check("manager WITH the right -> 200", r.status_code == 200)
            r = client.get("/cfg", headers=bearer("208011"))
            check("the real 39-bit M Manager -> 403 naming the right",
                  r.status_code == 403 and "RIGHT_CFG_GROUPS" in r.json().get("detail", ""))
            r = client.get("/cfg", headers=bearer("100001"))
            check("unknown manager -> 401, never fabricated (anti-F2)", r.status_code == 401)
            r = client.get("/cfg")
            check("no credentials -> 401", r.status_code == 401)
    finally:
        if saved is None:
            _container.pop("manager_repo", None)
        else:
            _container["manager_repo"] = saved

    print("== 7. a created group still exports to a valid MT5 record ==")
    from core.domains.accounts.enums import AccountType, MarginMode, StopOutMode, FreeMarginMode
    from core.domains.accounts.group import Group, MarginProfile, GroupPermissions
    from core.domains.identity.group_type import derive_group_type
    from decimal import Decimal
    from infrastructure.mt5 import wire
    from infrastructure.persistence.config_mappers import group_mt5_record, group_to_db

    name = "demo" + chr(92) + "proof-group"
    group = Group(
        name=name,
        account_type=derive_group_type(name),
        currency="USD",
        margin=MarginProfile(
            mode=MarginMode.RETAIL, leverage_default=100, leverage_max=500,
            margin_call_level=Decimal("50"), stop_out_level=Decimal("30"),
            stop_out_mode=StopOutMode.PERCENT, free_margin_mode=FreeMarginMode.USE_PL,
        ),
        permissions=GroupPermissions(trade_allowed=True),
    )
    check("group type derived from the name", group.account_type is AccountType.DEMO)
    record = group_mt5_record(group_to_db(group))
    check("export passes the wire validator",
          wire.validate(wire.build("ConfigGroups", [record])) == [])
    check("export carries the percent thresholds",
          record["MarginCall"] == "50.00" and record["MarginStopOut"] == "30.00")

    print(f"\nP1 identity proof: {CHECKS['pass']} passed, {CHECKS['fail']} failed")
    return 1 if CHECKS["fail"] else 0


if __name__ == "__main__":
    sys.exit(main())
