#!/usr/bin/env python3
"""P1 PROOF - the step-8 read plane, end to end on SQLite.

Real Sql repositories (the production adapters), real routers, real HTTP
through TestClient, real manager-JWT gating. The doubles live in the unit
tests; a proof drives the assembled thing.

What it proves (~50 checks):
  * lists are bare arrays with an honest X-Total-Count, paged in SQL
  * accounts sort NUMERICALLY (login is a String column)
  * filters: group / account_type / enabled / login / symbol / entry / state
  * the six-tab account detail, rights decoded server-side, inverted flags
  * credential material never leaves the server (seeded hashes, asserted absent)
  * client schema served from YAML with enums EXPANDED from domain code
  * route order: /clients/schema is not a client_id; the managers LIST is not
    a login
  * the F9 ticket rule on deals/orders/positions
  * orders history split + the state/history contradiction is a 400
  * gating: RIGHT_TRADES_READ opens the book and NOT the accounts;
    RIGHT_ACC_READ opens accounts and NOT the write plane; must_change_password
    blocks; the bootstrap admin key opens everything; unwired repo = loud 503

Usage:  python3 scripts/p1_proof_read_plane.py       (no credentials needed)
Exit 0 = green. D17-safe: every path resolved at runtime.
"""
import asyncio
import os
import sys
import tempfile
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from pathlib import Path

BP = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BP))

os.environ.setdefault("SECRET_KEY", "read-plane-proof-secret-" + "0" * 40)
os.environ.setdefault("ADMIN_API_KEY", "read-plane-proof-admin-key")

PASSED = 0
FAILED = 0


def check(ok, label, detail=""):
    global PASSED, FAILED
    if ok:
        PASSED += 1
        print(f"  [PASS] {label}" + (f"  ({detail})" if detail else ""))
    else:
        FAILED += 1
        print(f"  [FAIL] {label}" + (f"  ({detail})" if detail else ""))


T0 = datetime(2026, 9, 13, 10, 0, 0, tzinfo=timezone.utc)
ARGONISH = "$argon2id$v=19$m=65536,t=3,p=4$c2FsdA$PROOFSECRETHASHVALUE"


async def build_database(db_path):
    from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
    from sqlalchemy.pool import NullPool

    from infrastructure.persistence.database import Base
    import infrastructure.persistence.db_models  # noqa: F401

    engine = create_async_engine(f"sqlite+aiosqlite:///{db_path}", poolclass=NullPool)
    SessionFactory = async_sessionmaker(engine, expire_on_commit=False)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    from core.domains.accounts.account import Account
    from core.domains.accounts.client import Client
    from core.domains.accounts.enums import AccountType
    from core.domains.accounts.group import Group
    from core.domains.accounts.value_objects import MarginProfile
    from core.domains.common.value_objects import Money, Price, Volume
    from core.domains.identity.models import ManagerAccount, ManagerRole
    from core.domains.identity.rights import ManagerRightsMask, UserRight
    from core.domains.oms.entities.deal import Deal
    from core.domains.oms.entities.order import Order
    from core.domains.oms.entities.position import Position
    from core.domains.oms.enums import DealEntry, DealType, OrderState, OrderType, PositionAction
    from infrastructure.persistence.repositories.account_repository import SqlAccountRepository
    from infrastructure.persistence.repositories.deal_repository import SqlDealRepository
    from infrastructure.persistence.repositories.group_repository import SqlGroupRepository
    from infrastructure.persistence.repositories.manager_repository import (
        SqlClientRepository, SqlManagerRepository,
    )
    from infrastructure.persistence.repositories.order_repository import SqlOrderRepository
    from infrastructure.persistence.repositories.position_repository import SqlPositionRepository

    group_repo = SqlGroupRepository(session_factory=SessionFactory)
    demo = Group(name="demo\\Standard", account_type=AccountType.DEMO, server_id=1,
                 currency="USD", currency_digits=2, auth_password_min=8,
                 margin=MarginProfile(leverage_default=100, leverage_max=500))
    real = Group(name="real\\real", account_type=AccountType.REAL, server_id=1,
                 currency="USD", currency_digits=2, auth_password_min=8,
                 margin=MarginProfile(leverage_default=100, leverage_max=500))
    await group_repo.save(demo)
    await group_repo.save(real)

    account_repo = SqlAccountRepository(session_factory=SessionFactory, group_repo=group_repo)
    for i, login in enumerate([9, 10, 1000, 885863, 900003]):
        grp = demo if i % 2 == 0 else real
        acc = Account(
            login=login, group=grp, group_id=grp.id, account_type=grp.account_type,
            currency="USD", balance=Money(Decimal("10000"), "USD"),
            equity=Money(Decimal("10000"), "USD"),
            first_name="Proof", last_name=f"Trader{login}",
            **({"rights": UserRight(0), "is_enabled": False} if login == 900003 else {}),
        )
        if login == 1000:
            acc.password_hash = ARGONISH
            acc.investor_password_hash = ARGONISH
        await account_repo.save(acc)

    client_repo = SqlClientRepository(session_factory=SessionFactory)
    await client_repo.save(Client(id="cl-1", client_id="KYC-1", full_name="Ann Example",
                                  country="IN", email="ann@example.test",
                                  password_hash=ARGONISH))
    await client_repo.save(Client(id="cl-2", client_id="KYC-2", full_name="Bo Sample"))

    manager_repo = SqlManagerRepository(session_factory=SessionFactory)
    await manager_repo.save(ManagerAccount(
        manager_id="1000", login="1000", role=ManagerRole.READ_ONLY,
        rights=ManagerRightsMask.empty().grant("RIGHT_ADMIN"),
        is_active=True, must_change_password=False, allowed_ips=[]))
    await manager_repo.save(ManagerAccount(
        manager_id="700001", login="700001", role=ManagerRole.READ_ONLY,
        rights=ManagerRightsMask.empty().grant("RIGHT_TRADES_READ"),
        is_active=True, must_change_password=False, allowed_ips=[]))
    await manager_repo.save(ManagerAccount(
        manager_id="700002", login="700002", role=ManagerRole.READ_ONLY,
        rights=ManagerRightsMask.empty().grant("RIGHT_ACC_READ"),
        is_active=True, must_change_password=True, allowed_ips=[]))   # must-change blocks

    deal_repo = SqlDealRepository(session_factory=SessionFactory)
    for i in range(4):
        await deal_repo.save(Deal(
            deal_id=f"deal-{i}", account_login=1000 if i < 2 else 885863,
            symbol="EURUSD" if i % 2 == 0 else "BTCUSD",
            deal_type=DealType.BUY, entry=DealEntry.IN if i < 3 else DealEntry.OUT,
            volume=Volume(Decimal("0.10")), price=Price(Decimal("1.07961")),
            profit=Money(Decimal("0"), "USD"),
            external_id="7770001" if i == 0 else None,
            created_at=T0 + timedelta(minutes=i)))

    order_repo = SqlOrderRepository(session_factory=SessionFactory)
    for i, st in enumerate([OrderState.PLACED, OrderState.FILLED, OrderState.REJECTED]):
        await order_repo.save(Order(
            ticket_id=f"order-{i}", account_login=1000, symbol="EURUSD",
            order_type=OrderType.BUY, state=st,
            volume_initial=Volume(Decimal("0.10")), volume_current=Volume(Decimal("0.10")),
            price_order=Price(Decimal("1.07961")),
            time_setup=T0 + timedelta(minutes=i)))

    position_repo = SqlPositionRepository(session_factory=SessionFactory)
    for i, closed in enumerate([False, False, True]):
        p = Position(position_id=f"pos-{i}", account_login=1000 if i else 885863,
                     symbol="EURUSD", action=PositionAction.BUY,
                     external_id="5292088" if i == 0 else None,
                     volume=Volume(Decimal("0.10")), price_open=Price(Decimal("1.07961")))
        if closed:
            p.time_done = T0 + timedelta(hours=1)
        await position_repo.save(p)

    return {
        "engine": engine,
        "account_repo": account_repo, "client_repo": client_repo,
        "manager_repo": manager_repo, "deal_repo": deal_repo,
        "order_repo": order_repo, "position_repo": position_repo,
        "group_repo": group_repo,
    }


def main():
    tmp = tempfile.mkdtemp(prefix="read-plane-proof-")
    db_path = os.path.join(tmp, "proof.db")
    repos = asyncio.run(build_database(db_path))
    print(f"database: sqlite {db_path}")
    print("  seeded: 2 groups, 5 accounts, 2 clients, 3 managers, 4 deals, 3 orders, 3 positions")

    from fastapi import FastAPI
    from fastapi.testclient import TestClient

    from api.auth.jwt_handler import create_access_token
    from api.di_providers import register_di_providers
    from api.routers.admin import accounts as accounts_router
    from api.routers.admin import managers as managers_router
    from api.routers.admin import reads as reads_router

    register_di_providers({
        "account_repo": repos["account_repo"], "client_repo": repos["client_repo"],
        "manager_repo": repos["manager_repo"], "deal_repo": repos["deal_repo"],
        "order_repo": repos["order_repo"], "position_repo": repos["position_repo"],
        "group_repo": repos["group_repo"], "event_bus": None,
        "ledger_repo": None, "login_allocator": None, "uow_factory": None,
    })
    app = FastAPI()
    app.include_router(accounts_router.accounts_router)
    app.include_router(accounts_router.clients_router)
    app.include_router(reads_router.account_reads_router)
    app.include_router(reads_router.client_reads_router)
    app.include_router(reads_router.trade_reads_router)
    app.include_router(managers_router.router)

    ADMIN = {"X-Admin-API-Key": os.environ["ADMIN_API_KEY"]}

    with TestClient(app) as c:
        print("== accounts ==")
        r = c.get("/api/v1/admin/accounts", headers=ADMIN)
        check(r.status_code == 200, "GET /admin/accounts 200")
        body = r.json()
        check(isinstance(body, list), "bare array (the UI does setAccounts(data))")
        check(r.headers.get("X-Total-Count") == "5", "X-Total-Count is the FULL match count", r.headers.get("X-Total-Count", ""))
        logins = [a["login"] for a in body]
        check(logins == ["9", "10", "1000", "885863", "900003"], "NUMERIC login order", str(logins))
        check(all(isinstance(a["balance"], str) for a in body), "decimals are strings")

        r = c.get("/api/v1/admin/accounts", headers=ADMIN, params={"limit": 2, "offset": 0})
        check(len(r.json()) == 2 and r.headers["X-Total-Count"] == "5", "limit=2 pages, total stays 5")
        r = c.get("/api/v1/admin/accounts", headers=ADMIN, params={"limit": 2, "offset": 4})
        check(len(r.json()) == 1, "last page is short, not padded")

        demo = {a["login"] for a in c.get("/api/v1/admin/accounts", headers=ADMIN,
                                          params={"group": "demo\\Standard"}).json()}
        check(demo == {"9", "1000", "900003"}, "group=demo\\Standard -> the three demo accounts", str(demo))
        r = c.get("/api/v1/admin/accounts", headers=ADMIN, params={"account_type": "real"})
        check({a["login"] for a in r.json()} == {"10", "885863"}, "account_type=real filter")
        r = c.get("/api/v1/admin/accounts", headers=ADMIN, params={"enabled": "false"})
        check([a["login"] for a in r.json()] == ["900003"], "enabled=false filter (rights=0 legacy row)")

        print("== account detail ==")
        r = c.get("/api/v1/admin/accounts/1000", headers=ADMIN)
        check(r.status_code == 200, "GET /admin/accounts/1000 200")
        d = r.json()
        check(all(t in d for t in ("overview", "personal", "account", "limits", "subscriptions", "security")),
              "all six tabs present")
        check(d["group"]["name"] == "demo\\Standard", "group summary resolved")
        rights = d["limits"]["rights"]
        bits = {b["name"]: b for b in rights["bits"]}
        check(bits["USER_RIGHT_ENABLED"]["granted"] is True, "rights decoded: ENABLED granted")
        check(bits["USER_RIGHT_TRADE_DISABLED"]["inverted"] is True, "inverted flag served (0/1 problem stops here)")
        check(bits["USER_RIGHT_TECHNICAL"]["inverted"] is True, "TECHNICAL inverted too")
        check("PROOFSECRETHASHVALUE" not in r.text and "argon2" not in r.text.lower(),
              "NO credential material in the account detail")
        check(d["security"]["master_password_set"] is True and d["security"]["investor_password_set"] is True,
              "security tab is booleans")
        check(d["subscriptions"] == [], "subscriptions honestly empty")
        check(c.get("/api/v1/admin/accounts/424242", headers=ADMIN).status_code == 404,
              "unknown login -> 404, never a fabricated row")

        print("== clients ==")
        r = c.get("/api/v1/admin/clients", headers=ADMIN)
        check(r.status_code == 200 and len(r.json()) == 2 and r.headers["X-Total-Count"] == "2",
              "GET /admin/clients paged list")
        r = c.get("/api/v1/admin/clients/cl-1", headers=ADMIN)
        check(r.status_code == 200 and r.json()["full_name"] == "Ann Example", "client detail by id")
        check("PROOFSECRETHASHVALUE" not in r.text, "legacy client hash never served")
        check(r.json()["security"]["password_set"] is True, "client security is booleans")
        r = c.get("/api/v1/admin/clients/schema", headers=ADMIN)
        check(r.status_code == 200, "/clients/schema is NOT swallowed by /{client_id} (route order)")
        schema = r.json()
        check(schema["object"] == "client" and schema["wire_section"] == "IMTClient", "schema identity")
        fields = {f["field"]: f for f in schema["fields"]}
        check(fields["full_name"]["mt5"] == "PersonName", "SDK-grounded accessor names")
        status_f = fields["status"]
        check(status_f.get("enum_values") and any(v["name"] == "REGISTERED" for v in status_f["enum_values"]),
              "ClientStatus enum EXPANDED from domain code", str(len(status_f.get("enum_values") or [])))

        print("== managers list ==")
        r = c.get("/api/v1/admin/managers", headers=ADMIN)
        check(r.status_code == 200 and isinstance(r.json(), list), "GET /admin/managers is the LIST, not a login")
        check(r.headers.get("X-Total-Count") == "3", "manager total", r.headers.get("X-Total-Count", ""))
        admin_row = next(m for m in r.json() if m["login"] == 1000)
        check("RIGHT_ADMIN" in admin_row["rights_names"], "rights decoded to names per row")

        print("== trade reads (ENDPOINTS B2) ==")
        r = c.get("/api/v1/admin/positions", headers=ADMIN)
        check(r.status_code == 200 and len(r.json()) == 2, "open book only by default", str(len(r.json())))
        check(r.headers["X-Total-Count"] == "2", "positions total")
        rows = {p["position_id"]: p for p in r.json()}
        check(rows["pos-0"]["ticket"] == 5292088, "real venue ticket from external_id (F9 rule)")
        check(rows["pos-1"]["ticket"] is None, "no ticket -> null, never 0 (F9 rule)")
        check(len(c.get("/api/v1/admin/positions", headers=ADMIN, params={"include_closed": "true"}).json()) == 3,
              "include_closed adds the closed row")
        check(len(c.get("/api/v1/admin/positions", headers=ADMIN, params={"login": 1000}).json()) == 1,
              "positions login filter")
        check(len(c.get("/api/v1/admin/positions", headers=ADMIN, params={"symbol": "EURUSD"}).json()) == 2,
              "positions symbol filter")

        r = c.get("/api/v1/admin/deals", headers=ADMIN)
        check(r.status_code == 200 and r.headers["X-Total-Count"] == "4", "deals list + total")
        deals = {x["deal_id"]: x for x in r.json()}
        check(deals["deal-0"]["ticket"] == 7770001 and deals["deal-1"]["ticket"] is None,
              "F9 rule on deals too")
        check(len(c.get("/api/v1/admin/deals", headers=ADMIN, params={"entry": "OUT"}).json()) == 1,
              "deals entry filter (the IN/OUT lifecycle is finally visible)")
        check(len(c.get("/api/v1/admin/deals", headers=ADMIN, params={"symbol": "BTCUSD"}).json()) == 2,
              "deals symbol filter")

        r = c.get("/api/v1/admin/orders", headers=ADMIN)
        check(r.status_code == 200 and len(r.json()) == 3, "orders: everything by default")
        active = c.get("/api/v1/admin/orders", headers=ADMIN, params={"history": "false"}).json()
        check([o["state"] for o in active] == ["PLACED"], "history=false -> the active book")
        hist = c.get("/api/v1/admin/orders/history", headers=ADMIN).json()
        check({o["state"] for o in hist} == {"FILLED", "REJECTED"}, "/orders/history -> terminal states")
        r = c.get("/api/v1/admin/orders", headers=ADMIN, params={"state": "FILLED", "history": "false"})
        check(r.status_code == 400 and "contradicts" in r.json()["detail"],
              "state/history contradiction -> 400, never a confusing empty page")

        print("== gating ==")
        trades_tok = {"Authorization": "Bearer " + create_access_token({"sub": "700001", "is_manager": True})}
        check(c.get("/api/v1/admin/positions", headers=trades_tok).status_code == 200, "TRADES_READ opens the book")
        check(c.get("/api/v1/admin/deals", headers=trades_tok).status_code == 200, "TRADES_READ opens deals")
        check(c.get("/api/v1/admin/accounts", headers=trades_tok).status_code == 403, "TRADES_READ does NOT open accounts")
        acc_tok = {"Authorization": "Bearer " + create_access_token({"sub": "700002", "is_manager": True})}
        r = c.get("/api/v1/admin/accounts", headers=acc_tok)
        check(r.status_code == 403, "must_change_password blocks even a holding manager (step-3 rule)")

    # must-change manager with the flag cleared -> ACC_READ works, writes still refused
    async def _clear_flag():
        m = await repos["manager_repo"].find_by_login("700002")
        m.must_change_password = False
        await repos["manager_repo"].save(m)
    asyncio.run(_clear_flag())
    with TestClient(app) as c:
        acc_tok = {"Authorization": "Bearer " + create_access_token({"sub": "700002", "is_manager": True})}
        check(c.get("/api/v1/admin/accounts", headers=acc_tok).status_code == 200, "ACC_READ opens the account list")
        check(c.get("/api/v1/admin/accounts/1000", headers=acc_tok).status_code == 200, "ACC_READ opens the detail")
        r = c.post("/api/v1/admin/accounts", headers=acc_tok, json={"group_name": "demo\\Standard"})
        check(r.status_code == 403, "a READ bit never opens the WRITE plane")
        check(c.get("/api/v1/admin/positions", headers=acc_tok).status_code == 403, "ACC_READ does not open trades")

        print("== unwired ==")
        register_di_providers({"account_repo": None, "client_repo": None})
        check(c.get("/api/v1/admin/accounts", headers=ADMIN).status_code == 503, "unwired repo -> loud 503, never []")
        register_di_providers({"account_repo": repos["account_repo"], "client_repo": repos["client_repo"]})

    asyncio.run(repos["engine"].dispose())
    print(f"\nP1 read-plane proof: {PASSED} passed, {FAILED} failed")
    return 1 if FAILED else 0


if __name__ == "__main__":
    sys.exit(main())
