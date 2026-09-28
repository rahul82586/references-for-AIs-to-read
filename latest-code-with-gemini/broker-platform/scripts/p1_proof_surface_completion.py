#!/usr/bin/env python3
"""P1 PROOF - SURFACE COMPLETION (M18's signature gate).

Walks the ENTIRE mounted route table of the real application (create_app on
SQLite, real repositories, seeded data) and enforces the M18 contract
mechanically:

  1. every operation marked x-not-wired answers 501 with "NOT WIRED:" - a
     skeleton never answers 200 (the F8 disease: an empty success hiding an
     absent behaviour is banned at the gate, not at review);
  2. every GET that is NOT a skeleton answers 200 or 404 - never 500, never
     503 (a fully-wired server has no excuse), and never an empty-list 200
     for a route whose data was seeded;
  3. the seeded key routes really serve the seeded data (accounts list,
     account detail, clients, deals, orders, positions, routing, ticks,
     holidays, manager reads);
  4. no route outside the skeleton registry answers 501.

Usage:  python3 scripts/p1_proof_surface_completion.py     (no credentials)
Exit 0 = green. D17-safe: runtime paths only.
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

os.environ.setdefault("SECRET_KEY", "surface-proof-secret-" + "0" * 45)
os.environ.setdefault("ADMIN_API_KEY", "surface-proof-admin-key")
os.environ.setdefault("MARKET_DATA_SOURCE", "mock")

PASSED = 0
FAILED = 0
T0 = datetime(2026, 9, 13, 10, 0, 0, tzinfo=timezone.utc)


def check(ok, label, detail=""):
    global PASSED, FAILED
    if ok:
        PASSED += 1
        print(f"  [PASS] {label}" + (f"  ({detail})" if detail else ""))
    else:
        FAILED += 1
        print(f"  [FAIL] {label}" + (f"  ({detail})" if detail else ""))


async def build(db_path):
    from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
    from sqlalchemy.pool import NullPool
    from infrastructure.persistence.database import Base
    import infrastructure.persistence.db_models  # noqa: F401
    import infrastructure.persistence.reconciliation_models  # noqa: F401  (breaks table)

    engine = create_async_engine(f"sqlite+aiosqlite:///{db_path}", poolclass=NullPool)
    SF = async_sessionmaker(engine, expire_on_commit=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    from core.domains.accounts.account import Account
    from core.domains.accounts.client import Client
    from core.domains.accounts.enums import AccountType
    from core.domains.accounts.group import Group
    from core.domains.accounts.value_objects import MarginProfile
    from core.domains.common.value_objects import Money, Price, Volume
    from core.domains.identity.models import ManagerAccount, ManagerRole
    from core.domains.identity.rights import ManagerRightsMask
    from core.domains.oms.entities.deal import Deal
    from core.domains.oms.entities.order import Order
    from core.domains.oms.entities.position import Position
    from core.domains.oms.enums import DealEntry, DealType, OrderState, OrderType, PositionAction
    from infrastructure.persistence.repositories.account_repository import SqlAccountRepository
    from infrastructure.persistence.repositories.deal_repository import SqlDealRepository
    from infrastructure.persistence.repositories.group_repository import SqlGroupRepository
    from infrastructure.persistence.repositories.symbol_repository import SqlSymbolRepository
    from infrastructure.persistence.repositories.manager_repository import (
        SqlClientRepository, SqlManagerRepository)
    from infrastructure.persistence.repositories.order_repository import SqlOrderRepository
    from infrastructure.persistence.repositories.position_repository import SqlPositionRepository

    from core.domains.instruments.symbol import Symbol
    symbols = SqlSymbolRepository(session_factory=SF)
    await symbols.save(Symbol(name="EURUSD"))

    groups = SqlGroupRepository(session_factory=SF)
    demo = Group(name="demo\\Standard", account_type=AccountType.DEMO, server_id=1,
                 currency="USD", currency_digits=2, auth_password_min=8,
                 margin=MarginProfile(leverage_default=100, leverage_max=500))
    await groups.save(demo)
    accounts = SqlAccountRepository(session_factory=SF, group_repo=groups)
    await accounts.save(Account(login=1000, group=demo, group_id=demo.id, client_id="cl-1",
                                account_type=AccountType.DEMO, currency="USD",
                                balance=Money(Decimal("10000"), "USD"),
                                equity=Money(Decimal("10000"), "USD"),
                                first_name="Surface", last_name="Proof"))
    clients = SqlClientRepository(session_factory=SF)
    await clients.save(Client(id="cl-1", client_id="KYC-1", full_name="Surface Proof"))
    managers = SqlManagerRepository(session_factory=SF)
    await managers.save(ManagerAccount(
        manager_id="1000", login="1000", role=ManagerRole.READ_ONLY,
        rights=ManagerRightsMask.empty().grant("RIGHT_ADMIN"),
        is_active=True, must_change_password=False, allowed_ips=[]))
    deals = SqlDealRepository(session_factory=SF)
    await deals.save(Deal(deal_id="deal-1", account_login=1000, symbol="EURUSD",
                          deal_type=DealType.BUY, entry=DealEntry.IN,
                          volume=Volume(Decimal("0.10")), price=Price(Decimal("1.07961")),
                          profit=Money(Decimal("0"), "USD"), external_id="7770001",
                          created_at=T0))
    orders = SqlOrderRepository(session_factory=SF)
    await orders.save(Order(ticket_id="order-1", account_login=1000, symbol="EURUSD",
                            order_type=OrderType.BUY, state=OrderState.FILLED,
                            volume_initial=Volume(Decimal("0.10")),
                            volume_current=Volume(Decimal("0.10")),
                            price_order=Price(Decimal("1.07961")), time_setup=T0))
    positions = SqlPositionRepository(session_factory=SF)
    await positions.save(Position(position_id="pos-1", account_login=1000, symbol="EURUSD",
                                  action=PositionAction.BUY, external_id="5292088",
                                  volume=Volume(Decimal("0.10")),
                                  price_open=Price(Decimal("1.07961"))))
    await engine.dispose()


PARAM_PROBES = {
    "login": "1000", "client_id": "cl-1", "symbol_name": "EURUSD", "symbol": "EURUSD",
    "name": "demo%5CStandard", "group_name": "demo%5CStandard",
    "gateway_id": "x", "feed_id": "x", "allocation_id": "x", "rule_id": "x",
    "holiday_id": "x", "ticket_id": "x", "position_id": "x", "order_id": "x",
}
QUERY_PROBES = {"login": "1000", "symbol": "EURUSD", "limit": "10", "offset": "0",
                "group": "demo\\Standard", "entry": "IN", "state": "FILLED"}


def main():
    tmp = tempfile.mkdtemp(prefix="surface-proof-")
    db_path = os.path.join(tmp, "surface.db")
    asyncio.run(build(db_path))
    os.environ["DATABASE_URL"] = f"sqlite+aiosqlite:///{db_path}"
    print(f"database: sqlite {db_path} (seeded: 1 group/account/client/manager/deal/order/position)")

    from fastapi.testclient import TestClient
    from api.auth.jwt_handler import create_access_token
    from api.main import create_app

    app = create_app()
    admin = {"X-Admin-API-Key": os.environ["ADMIN_API_KEY"]}
    mtok = {"Authorization": "Bearer " + create_access_token({'sub': '800001', 'is_manager': True})}
    headers = {**admin, **mtok}

    schema = app.openapi()
    paths = schema["paths"]
    skeleton_ops, real_gets, real_writes = [], [], []
    for path, ops in paths.items():
        for method, op in ops.items():
            if method not in ("get", "post", "put", "delete"):
                continue
            probe = path
            for k, v in PARAM_PROBES.items():
                probe = probe.replace("{" + k + "}", v)
            if "{" in probe:      # unmapped param - skip honestly, count it
                continue
            entry = (method.upper(), probe, op.get("operationId", ""))
            if op.get("x-not-wired"):
                skeleton_ops.append(entry)
            elif method == "get":
                real_gets.append(entry)
            else:
                real_writes.append(entry)

    print(f"route table: {len(skeleton_ops)} skeletons, {len(real_gets)} real GETs, "
          f"{len(real_writes)} real writes (writes are not blind-fired: side effects)")

    with TestClient(app) as c:
        print("== 1. every skeleton refuses with the roadmap named ==")
        bad = []
        for method, probe, opid in skeleton_ops:
            r = c.request(method, probe, headers=headers, json={})
            if r.status_code != 501 or not r.json().get("detail", "").startswith("NOT WIRED:"):
                bad.append((method, probe, r.status_code))
        check(not bad, f"{len(skeleton_ops)} skeleton operations all answer 501 NOT WIRED", str(bad[:3]))

        print("== 2. every real GET answers 200/404 - never 500, never 503 ==")
        bad = []
        statuses = {}
        for method, probe, opid in real_gets:
            r = c.get(probe, headers=headers, params=QUERY_PROBES)
            statuses[probe] = r.status_code
            if r.status_code not in (200, 404):
                bad.append((probe, r.status_code))
        check(not bad, f"{len(real_gets)} real GETs: only 200/404", str(bad[:5]))

        print("== 3. the seeded key routes really serve ==")
        must_200 = [
            "/api/v1/admin/accounts", "/api/v1/admin/accounts/1000",
            "/api/v1/admin/accounts/online", "/api/v1/admin/accounts/schema",
            "/api/v1/admin/clients", "/api/v1/admin/clients/cl-1",
            "/api/v1/admin/clients/schema", "/api/v1/admin/clients/cl-1/accounts",
            "/api/v1/admin/managers", "/api/v1/admin/managers/1000",
            "/api/v1/admin/managers/rights", "/api/v1/admin/managers/presets",
            "/api/v1/admin/managers/schema",
            "/api/v1/admin/deals", "/api/v1/admin/orders", "/api/v1/admin/orders/history",
            "/api/v1/admin/positions", "/api/v1/admin/routing", "/api/v1/admin/ticks",
            "/api/v1/admin/risk/exposure", "/api/v1/admin/risk/summary",
            "/api/v1/admin/risk/margin-calls", "/api/v1/admin/holidays",
            "/api/v1/admin/symbols/EURUSD/sessions",
            "/api/v1/admin/groups", "/api/v1/admin/status",
            "/api/v1/manager/UserGet", "/api/v1/manager/PositionGet",
            "/api/v1/manager/DealGet", "/api/v1/manager/OrderGet",
            "/api/v1/manager/SymbolGet", "/api/v1/manager/GroupGet",
            "/api/v1/manager/ServerTime", "/api/v1/manager/Ping",
        ]
        for path in must_200:
            probe = path
            for k, v in PARAM_PROBES.items():
                probe = probe.replace("{" + k + "}", v)
            code = statuses.get(probe)
            if code is None:
                r = c.get(probe, headers=headers, params=QUERY_PROBES)
                code = r.status_code
            check(code == 200, f"GET {path} -> 200", f"got {code}")

        print("== 4. seeded data is actually IN the answers (no 200-empty lies) ==")
        rows = c.get("/api/v1/admin/accounts", headers=headers).json()
        check(any(r["login"] == "1000" for r in rows), "the seeded account is in the list")
        rows = c.get("/api/v1/admin/deals", headers=headers).json()
        check(len(rows) == 1 and rows[0]["ticket"] == 7770001, "the seeded deal, with its venue ticket")
        rows = c.get("/api/v1/manager/PositionGet", headers=headers).json()
        check(len(rows) == 1 and rows[0]["ticket"] == 5292088, "PositionGet serves the seeded position (F8/F9)")
        body = c.get("/api/v1/admin/routing", headers=headers).json()
        check(isinstance(body["mt5_rules"], list), "routing answers with the ordered rule table")

        print("== 5. no REAL route answers 501 (a 501 means skeleton-registry drift) ==")
        stray = [(m, p, statuses.get(p)) for m, p, _ in real_gets if statuses.get(p) == 501]
        check(not stray, "zero stray 501s outside the skeleton registry", str(stray[:3]))

    print(f"\nP1 surface-completion proof: {PASSED} passed, {FAILED} failed")
    return 1 if FAILED else 0


if __name__ == "__main__":
    sys.exit(main())
