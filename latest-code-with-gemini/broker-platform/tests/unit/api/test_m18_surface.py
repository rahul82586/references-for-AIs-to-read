"""M18 over real HTTP: the wired B-tier and the honest C-tier skeletons.

The risks these tests exist for:

* **The skeleton contract.** A not-built endpoint answers 501 with the exact
  missing piece named - NEVER 200-empty (the F8 disease) and never a bare 404
  that makes the UI think the path is wrong. `p1_proof_surface_completion`
  walks the whole table; these pin the behaviour per family.
* **Skeletons are gated like the real thing.** A manager without the right
  gets 403 TODAY, so authorisation doesn't change when the logic lands.
* **The new reads follow the house rules**: one serializer per shape, F9
  ticket rule on deals/orders, bare arrays + X-Total-Count, honest nulls on
  the ticks snapshot, refusals as 400s with reasons.
* **Funds move money with a ledger row or not at all** - and the
  system-generated operation types are refused at the door.
"""
from __future__ import annotations

import dataclasses
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from typing import Any, Dict, List, Optional

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from api.auth import admin_dependencies
from api.auth.jwt_handler import create_access_token
from api.di_providers import register_di_providers
from api.routers.admin import accounts as accounts_router
from api.routers.admin import reads as reads_router
from api.routers.admin import skeletons as skeletons_router
from api.routers.manager import main as manager_main
from api.routers.manager import service as manager_service
from core.domains.accounts.account import Account
from core.domains.accounts.enums import AccountType
from core.domains.accounts.group import Group
from core.domains.accounts.value_objects import MarginProfile
from core.domains.common.value_objects import Money, Price, Volume
from core.domains.identity.password_policy import hash_password
from core.domains.oms.entities.deal import Deal
from core.domains.oms.entities.order import Order
from core.domains.oms.enums import DealEntry, DealType, OrderState, OrderType

ADMIN_KEY = admin_dependencies.ADMIN_API_KEY_ENV or "test-admin-api-key"
ADMIN = {"X-Admin-API-Key": ADMIN_KEY}
T0 = datetime(2026, 9, 13, 10, 0, 0, tzinfo=timezone.utc)


# ---------------------------------------------------------------------------
# doubles
# ---------------------------------------------------------------------------


class MemDeals:
    def __init__(self, rows): self.rows = rows
    async def find_page(self, limit=100, offset=0, account_login=None, symbol=None, entry=None, **r):
        rows = self.rows
        if account_login is not None: rows = [d for d in rows if int(d.account_login) == account_login]
        if symbol is not None: rows = [d for d in rows if d.symbol == symbol]
        if entry is not None: rows = [d for d in rows if d.entry.value == entry]
        return rows[offset:offset + limit], len(rows)


class MemOrders:
    TERMINAL = ("CANCELLED", "FILLED", "REJECTED", "EXPIRED")
    def __init__(self, rows): self.rows = rows
    async def find_page(self, limit=100, offset=0, account_login=None, symbol=None,
                        state=None, history=None, **r):
        if state is not None and history is not None and (state in self.TERMINAL) != bool(history):
            raise ValueError(f"state={state!r} contradicts history={history!r}")
        rows = self.rows
        if account_login is not None: rows = [o for o in rows if int(o.account_login) == account_login]
        if symbol is not None: rows = [o for o in rows if o.symbol == symbol]
        if state is not None: rows = [o for o in rows if o.state.value == state]
        elif history is not None:
            want = self.TERMINAL if history else ("STARTED", "PLACED", "PARTIALLY_FILLED")
            rows = [o for o in rows if o.state.value in want]
        return rows[offset:offset + limit], len(rows)


class MemSimple:
    """find_page over a list, no filters (+ the open-book read the risk
    exposure route uses)."""
    def __init__(self, rows): self.rows = rows
    async def find_page(self, limit=100, offset=0, **filters):
        return self.rows[offset:offset + limit], len(self.rows)
    async def get_open_positions(self, session=None):
        return list(self.rows)


class MemAccounts:
    def __init__(self, rows): self.rows = rows; self.saved = []
    async def find_page(self, limit=100, offset=0, group_name=None, account_type=None,
                        enabled=None, so_active=None, online=None, client_id=None, **r):
        rows = self.rows
        if so_active is True:
            rows = [a for a in rows if a.so_activation.name != "NONE"]
        if online is True:
            rows = [a for a in rows if a.is_online]
        if client_id is not None:
            rows = [a for a in rows if a.client_id == client_id]
        rows = sorted(rows, key=lambda a: int(a.login))
        return rows[offset:offset + limit], len(rows)
    async def find_by_login(self, login, session=None):
        return next((a for a in self.rows if str(a.login) == str(login)), None)
    async def save(self, account, session=None):
        self.saved.append(account); return account


class MemSymbols:
    def __init__(self, rows): self.rows = rows
    async def get_all_symbols(self): return list(self.rows)
    async def find_by_name(self, name, session=None):
        return next((s for s in self.rows if s.name == name), None)


from core.domains.instruments.symbol import Symbol as _RealSymbol


class _FakeSymbol(_RealSymbol):
    """A REAL Symbol entity (so _symbol_summary's 25 field accesses all
    resolve) with the two session booleans pinned for the test."""
    def __init__(self, name, trade_open=True, quote_open=True):
        super().__init__(name=name)
        object.__setattr__(self, "_t", trade_open)
        object.__setattr__(self, "_q", quote_open)
    def is_trade_session_active(self, when=None): return self._t
    def is_quote_session_active(self, when=None): return self._q


class _Tick:
    def __init__(self, symbol, bid, ask, source="LIVE", when=None):
        self.symbol, self.bid, self.ask = symbol, Decimal(bid), Decimal(ask)
        self.spread = self.ask - self.bid
        self.source = source
        self.timestamp = when or datetime.now(timezone.utc)


class MemEngine:
    def __init__(self, ticks): self._t = ticks
    def get_latest_tick(self, symbol): return self._t.get(symbol)


class MemRouting:
    def __init__(self, rules): self._r = rules
    async def get_all_ordered(self): return list(self._r)


@dataclasses.dataclass
class _Rule:
    name: str
    action: int = 1001
    priority: int = 0


class MemCoverage:
    def __init__(self, account=None): self._a = account
    async def find_by_id(self, account_id): return self._a


class MemManagers:
    """require_right resolves the JWT's sub against this - the dealer
    skeletons are gated, so the manager must really hold the bit."""
    def __init__(self, rows=None):
        self.rows = {str(m.login): m for m in (rows or [])}
    async def find_by_login(self, login, session=None):
        return self.rows.get(str(login))


class MemBreaks:
    def __init__(self, n): self._n = n
    async def find_open(self, **kw): return [object()] * self._n


class MemLedger:
    def __init__(self): self.rows = []
    async def save(self, operation): self.rows.append(operation); return operation
    async def get_by_account(self, account_login): return list(self.rows)
    async def get_by_reference(self, reference_id): return None


class MemHolidays:
    def __init__(self): self.rows = []; self._n = 0
    async def get_all(self): return list(self.rows)
    async def get_active_holidays(self, check_date): return list(self.rows)
    async def get_holidays_for_symbol(self, symbol_name, year): return list(self.rows)
    async def save(self, holiday, session=None):
        self.rows.append(holiday); return holiday
    async def save_with_session(self, holiday, session): return await self.save(holiday)
    async def find_by_id(self, holiday_id):
        return next((h for h in self.rows if h.id == holiday_id), None)
    async def delete(self, holiday_id):
        before = len(self.rows)
        self.rows = [h for h in self.rows if h.id != holiday_id]
        return len(self.rows) < before


class NullBus:
    def __init__(self): self.published = []
    async def publish(self, event): self.published.append(event)
    def subscribe(self, *a, **k): pass


class FakeRisk:
    """The calculator contract: the four engine methods the handler calls."""
    def __init__(self, prices=None, rate="1.0"):
        self._p = prices or {}
        self._rate = Decimal(rate)
    def get_bid(self, symbol):
        if symbol not in self._p: raise RuntimeError(f"no price for {symbol}")
        return Decimal(self._p[symbol][0])
    def get_ask(self, symbol):
        if symbol not in self._p: raise RuntimeError(f"no price for {symbol}")
        return Decimal(self._p[symbol][1])
    def get_conversion_rate(self, f, t, market_feed=None, side="BUY"): return self._rate
    def calculate_margin_level(self, account, positions):
        used = Decimal("107.96") * len(positions)

        class S:  # MarginSnapshot-shaped
            pass
        S.margin_used = used
        S.balance = account.balance.amount
        S.equity = account.equity.amount
        S.margin_free = account.equity.amount - used
        S.margin_level = Decimal("9999")
        return S()
    def calculate_position_pnl(self, account, position): return Decimal("12.34")


def _dealer_manager(login=800001):
    from core.domains.identity.models import ManagerAccount, ManagerRole
    from core.domains.identity.rights import ManagerRightsMask
    return ManagerAccount(
        manager_id=str(login), login=str(login), role=ManagerRole.READ_ONLY,
        rights=ManagerRightsMask.empty().grant("RIGHT_TRADES_DEALER"),
        is_active=True, must_change_password=False, allowed_ips=[])


def _group(name="demo\\Standard"):
    return Group(name=name, account_type=AccountType.DEMO, server_id=1,
                 currency="USD", currency_digits=2, auth_password_min=8,
                 margin=MarginProfile(leverage_default=100, leverage_max=500))


def _account(login=1000, balance="10000", client_id="", online=False, so=None):
    g = _group()
    a = Account(login=login, group=g, group_id=g.id, client_id=client_id,
                account_type=AccountType.DEMO, currency="USD",
                balance=Money(Decimal(balance), "USD"), equity=Money(Decimal(balance), "USD"),
                first_name="M18", last_name=f"T{login}")
    a.is_online = online
    if so is not None:
        a.so_activation = so
    return a


def _deal(i, login=1000, symbol="EURUSD", entry=DealEntry.IN, ext=None):
    return Deal(deal_id=f"d-{i}", account_login=login, symbol=symbol,
                deal_type=DealType.BUY, entry=entry,
                volume=Volume(Decimal("0.10")), price=Price(Decimal("1.07961")),
                profit=Money(Decimal("0"), "USD"), external_id=ext,
                created_at=T0 + timedelta(minutes=i))


def _order(i, login=1000, state=OrderState.PLACED):
    return Order(ticket_id=f"o-{i}", account_login=login, symbol="EURUSD",
                 order_type=OrderType.BUY, state=state,
                 volume_initial=Volume(Decimal("0.10")), volume_current=Volume(Decimal("0.10")),
                 price_order=Price(Decimal("1.07961")), time_setup=T0 + timedelta(minutes=i))


@pytest.fixture()
def world():
    g = _group()
    from core.domains.accounts.enums import SOActivation
    accounts = [_account(1000, client_id="cl-1", online=True),
                _account(886152, so=SOActivation.MARGIN_CALL)]
    providers = {
        "account_repo": MemAccounts(accounts),
        "client_repo": MemSimple([]),
        "manager_repo": MemManagers([_dealer_manager()]),
        "deal_repo": MemDeals([_deal(1, ext="7770001"), _deal(2, entry=DealEntry.OUT),
                               _deal(3, login=886152, symbol="BTCUSD")]),
        "order_repo": MemOrders([_order(1), _order(2, state=OrderState.FILLED)]),
        "position_repo": MemSimple([]),
        "group_repo": type("G", (), {"find_by_name": staticmethod(lambda n: None),
                                     "get_all": None})(),
        "symbol_repo": MemSymbols([_FakeSymbol("EURUSD"), _FakeSymbol("XAUUSD", trade_open=False, quote_open=False)]),
        "market_data_engine": MemEngine({"EURUSD": _Tick("EURUSD", "1.10200", "1.10210")}),
        "risk_engine": FakeRisk(prices={"EURUSD": ("1.10200", "1.10210")}),
        "mt5_routing_repo": MemRouting([_Rule("dealer", 1001, 0), _Rule("a-book", 1002, 1)]),
        "routing_rule_repo": None,
        "coverage_repo": MemCoverage(None),
        "reconciliation_break_repo": MemBreaks(9),
        "ledger_repo": MemLedger(),
        "holiday_repo": MemHolidays(),
        "event_bus": NullBus(),
    }
    # a real-ish group repo for the calculators
    class _Groups:
        async def find_by_name(self, name, session=None): return g if name == g.name else None
        async def get_all(self): return [g]
    providers["group_repo"] = _Groups()

    register_di_providers(providers)
    admin_app = FastAPI()
    admin_app.include_router(accounts_router.accounts_router)
    admin_app.include_router(accounts_router.clients_router)
    admin_app.include_router(reads_router.account_reads_router)
    admin_app.include_router(reads_router.client_reads_router)
    admin_app.include_router(reads_router.trade_reads_router)
    admin_app.include_router(reads_router.routing_reads_router)
    admin_app.include_router(reads_router.quotes_reads_router)
    admin_app.include_router(reads_router.risk_reads_router)
    admin_app.include_router(reads_router.calc_router)
    admin_app.include_router(reads_router.funds_router)
    admin_app.include_router(reads_router.holidays_router)
    admin_app.include_router(reads_router.symbol_reads_router)
    for sk in skeletons_router.ALL_SKELETON_ROUTERS:
        if sk.prefix.startswith("/api/v1/admin"):
            admin_app.include_router(sk)

    manager_app = FastAPI()
    manager_app.include_router(manager_main.router)
    manager_app.include_router(manager_service.router)
    manager_app.include_router(skeletons_router.dealer_skeleton)

    token = create_access_token({"sub": "800001", "is_manager": True})
    providers["_admin"] = TestClient(admin_app)
    providers["_manager"] = TestClient(manager_app)
    providers["_mtok"] = {"Authorization": f"Bearer {token}"}
    providers["_accounts"] = accounts
    yield providers
    register_di_providers({k: None for k in providers if not k.startswith("_")})


# ---------------------------------------------------------------------------
# manager dialect (B1-B4, B17)
# ---------------------------------------------------------------------------


def test_deal_get_serves_the_book_with_the_f9_rule(world):
    r = world["_manager"].get("/api/v1/manager/DealGet", headers=world["_mtok"])
    assert r.status_code == 200, r.text
    body = r.json()
    assert r.headers["X-Total-Count"] == "3"
    by_id = {d["deal_id"]: d for d in body}
    assert by_id["d-1"]["ticket"] == 7770001        # venue number
    assert by_id["d-2"]["ticket"] is None           # never 0
    out = world["_manager"].get("/api/v1/manager/DealGet", headers=world["_mtok"],
                                params={"entry": "OUT"}).json()
    assert len(out) == 1 and out[0]["entry"] == "OUT"


def test_order_get_and_the_history_tristate(world):
    c, h = world["_manager"], world["_mtok"]
    assert len(c.get("/api/v1/manager/OrderGet", headers=h).json()) == 2
    active = c.get("/api/v1/manager/OrderGet", headers=h, params={"history": "false"}).json()
    assert [o["state"] for o in active] == ["PLACED"]
    r = c.get("/api/v1/manager/OrderGet", headers=h, params={"state": "FILLED", "history": "false"})
    assert r.status_code == 400 and "contradicts" in r.json()["detail"]
    rows = c.get("/api/v1/manager/OrderGet", headers=h).json()
    assert rows[0]["order_id"] and rows[0]["ticket"] is None   # F9 rule on orders too


def test_symbol_and_group_get(world):
    c, h = world["_manager"], world["_mtok"]
    allsyms = c.get("/api/v1/manager/SymbolGet", headers=h).json()
    assert {s["name"] for s in allsyms} == {"EURUSD", "XAUUSD"}
    one = c.get("/api/v1/manager/SymbolGet", headers=h, params={"symbol": "EURUSD"}).json()
    assert one["name"] == "EURUSD"
    assert c.get("/api/v1/manager/SymbolGet", headers=h, params={"symbol": "NOPE"}).status_code == 404
    groups = c.get("/api/v1/manager/GroupGet", headers=h).json()
    assert any(gr["name"] == "demo\\Standard" for gr in groups)


def test_server_time_uses_the_sunday_zero_convention(world):
    body = world["_manager"].get("/api/v1/manager/ServerTime", headers=world["_mtok"]).json()
    assert body["timezone"] == "UTC" and 0 <= body["day_of_week"] <= 6
    assert isinstance(body["timestamp"], int)


def test_manager_reads_503_when_unwired(world):
    register_di_providers({"deal_repo": None})
    r = world["_manager"].get("/api/v1/manager/DealGet", headers=world["_mtok"])
    assert r.status_code == 503


# ---------------------------------------------------------------------------
# admin B-tier
# ---------------------------------------------------------------------------


def test_routing_is_served_in_evaluation_order(world):
    body = world["_admin"].get("/api/v1/admin/routing", headers=ADMIN).json()
    assert [r["name"] for r in body["mt5_rules"]] == ["dealer", "a-book"]  # order IS semantics
    assert body["house_rules"] == []


def test_ticks_snapshot_is_honest_about_absence(world):
    rows = world["_admin"].get("/api/v1/admin/ticks", headers=ADMIN).json()
    by = {r["symbol"]: r for r in rows}
    assert by["EURUSD"]["bid"] == "1.10200" and by["EURUSD"]["source"] == "LIVE"
    assert by["XAUUSD"]["bid"] is None and by["XAUUSD"]["source"] is None  # no tick, no lie


def test_risk_exposure_and_summary(world):
    c = world["_admin"]
    exp = c.get("/api/v1/admin/risk/exposure", headers=ADMIN).json()
    assert exp["coverage_account"] is None and exp["net_open_position"] == {}
    summ = c.get("/api/v1/admin/risk/summary", headers=ADMIN).json()
    assert summ["accounts_total"] == 2 and summ["reconciliation_breaks_open"] == 9


def test_margin_calls_filters_by_so_state(world):
    rows = world["_admin"].get("/api/v1/admin/risk/margin-calls", headers=ADMIN).json()
    assert [r["login"] for r in rows] == ["886152"]


def test_calculators_refuse_without_a_price_and_answer_with_one(world):
    c = world["_admin"]
    r = c.post("/api/v1/admin/trade/calc-margin", headers=ADMIN,
               json={"group_name": "demo\\Standard", "symbol": "EURUSD", "side": "BUY", "volume": "0.10"})
    assert r.status_code == 200 and Decimal(r.json()["margin_required"]) > 0
    r = c.post("/api/v1/admin/trade/calc-margin", headers=ADMIN,
               json={"group_name": "demo\\Standard", "symbol": "XAUUSD", "side": "BUY", "volume": "0.10"})
    assert r.status_code == 400 and "no live price" in r.json()["detail"]   # refuses, never approximates
    r = c.post("/api/v1/admin/trade/calc-rate", headers=ADMIN,
               json={"from_currency": "EUR", "to_currency": "USD"})
    assert r.json()["rate"] == "1.0"
    r = c.post("/api/v1/admin/trade/check-margin", headers=ADMIN,
               json={"login": 424242, "symbol": "EURUSD", "side": "BUY", "volume": "0.10"})
    assert r.status_code == 400 and "no account" in r.json()["detail"]


def test_balance_moves_money_with_a_ledger_row_or_refuses(world):
    c = world["_admin"]
    r = c.post("/api/v1/admin/accounts/1000/balance", headers=ADMIN,
               json={"operation": "DEPOSIT", "amount": "500.00", "comment": "wire-in"})
    assert r.status_code == 201, r.text
    body = r.json()
    assert body["operation_id"].startswith("OP_")
    assert Decimal(body["balance_after"]) == Decimal("10500.00")
    assert len(world["ledger_repo"].rows) == 1                       # the ledger row exists
    r = c.post("/api/v1/admin/accounts/1000/balance", headers=ADMIN,
               json={"operation": "WITHDRAWAL", "amount": "999999"})
    assert r.status_code == 400 and "Insufficient" in r.json()["detail"]
    r = c.post("/api/v1/admin/accounts/1000/balance", headers=ADMIN,
               json={"operation": "SWAP", "amount": "10"})
    assert r.status_code == 400 and "system-generated" in r.json()["detail"]
    r = c.post("/api/v1/admin/accounts/1000/balance", headers=ADMIN,
               json={"operation": "DEPOSIT", "amount": "-5"})
    assert r.status_code == 400
    assert c.post("/api/v1/admin/accounts/424242/balance", headers=ADMIN,
                  json={"operation": "DEPOSIT", "amount": "5"}).status_code == 404


def test_check_password_answers_without_revealing(world):
    world["_accounts"][0].password_hash = hash_password("Str0ng#Pass1")
    c = world["_admin"]
    r = c.post("/api/v1/admin/accounts/1000/check-password", headers=ADMIN,
               json={"password": "Str0ng#Pass1"})
    assert r.status_code == 200 and r.json()["valid"] is True
    r = c.post("/api/v1/admin/accounts/1000/check-password", headers=ADMIN,
               json={"password": "wrong"})
    assert r.json()["valid"] is False
    assert "argon2" not in r.text.lower()
    world["_accounts"][1].password_hash = ""
    r = c.post("/api/v1/admin/accounts/886152/check-password", headers=ADMIN,
               json={"password": "x"})
    assert r.json()["valid"] is False and "provisioned" in r.json()["reason"]


def test_online_accounts_need_the_online_right_too(world):
    rows = world["_admin"].get("/api/v1/admin/accounts/online", headers=ADMIN).json()
    assert [r["login"] for r in rows] == ["1000"]


def test_holidays_crud_end_to_end(world):
    c = world["_admin"]
    r = c.post("/api/v1/admin/holidays", headers=ADMIN,
               json={"description": "Christmas", "month": 12, "day": 25})
    assert r.status_code == 201, r.text
    hid = r.json()["id"]
    rows = c.get("/api/v1/admin/holidays", headers=ADMIN).json()
    assert any(h["id"] == hid and h["description"] == "Christmas" for h in rows)
    assert c.delete(f"/api/v1/admin/holidays/{hid}", headers=ADMIN).status_code == 200
    assert c.delete(f"/api/v1/admin/holidays/{hid}", headers=ADMIN).status_code == 404


def test_client_accounts_backlink(world):
    rows = world["_admin"].get("/api/v1/admin/clients/cl-1/accounts", headers=ADMIN).json()
    assert [r["login"] for r in rows] == ["1000"]


def test_symbol_sessions_answer_from_the_entity_the_risk_gate_uses(world):
    body = world["_admin"].get("/api/v1/admin/symbols/EURUSD/sessions", headers=ADMIN).json()
    assert body["is_trade_session"] is True and body["is_quote_session"] is True
    x = world["_admin"].get("/api/v1/admin/symbols/XAUUSD/sessions", headers=ADMIN).json()
    assert x["is_trade_session"] is False
    assert world["_admin"].get("/api/v1/admin/symbols/NOPE/sessions", headers=ADMIN).status_code == 404


# ---------------------------------------------------------------------------
# C-tier: the honest skeletons
# ---------------------------------------------------------------------------


SKELETON_CASES = [
    ("PUT", "/api/v1/admin/accounts/1000", "UpdateAccountHandler"),
    ("DELETE", "/api/v1/admin/accounts/1000", "deletion"),
    ("POST", "/api/v1/admin/symbols", "CreateSymbolHandler"),
    ("POST", "/api/v1/admin/routing", "routing-rule writes"),
    ("POST", "/api/v1/admin/routing/reorder", "order IS the semantics"),
    ("GET", "/api/v1/admin/gateways", "gateway config plane"),
    ("GET", "/api/v1/admin/datafeeds", "datafeed config plane"),
    ("GET", "/api/v1/admin/allocations", "step 9"),
    ("GET", "/api/v1/admin/journal", "audit journal"),
    ("GET", "/api/v1/admin/reports", "report engine"),
    ("GET", "/api/v1/admin/charts/bars", "bars table has 0 rows"),
    ("POST", "/api/v1/admin/mail", "internal mail"),
    ("POST", "/api/v1/admin/groups/demo%5CStandard/symbols", "SpreadDiff"),
    ("DELETE", "/api/v1/admin/managers/1000", "manager deletion"),
]


@pytest.mark.parametrize("method,path,expect_in_detail", SKELETON_CASES)
def test_skeletons_refuse_with_the_roadmap_named(world, method, path, expect_in_detail):
    r = world["_admin"].request(method, path, headers=ADMIN, json={})
    assert r.status_code == 501, f"{method} {path} -> {r.status_code}"
    detail = r.json()["detail"]
    assert detail.startswith("NOT WIRED:") and expect_in_detail.lower() in detail.lower()


def test_dealer_skeletons_refuse_on_the_manager_dialect(world):
    for path in ("/api/v1/manager/OrderRequote", "/api/v1/manager/OrderConfirm"):
        r = world["_manager"].post(path, headers=world["_mtok"], json={})
        assert r.status_code == 501 and r.json()["detail"].startswith("NOT WIRED:")


def test_no_skeleton_ever_answers_200(world):
    """The F8 ban, at suite level: walk every x-not-wired operation in the
    mounted admin app and assert it refuses."""
    app = world["_admin"].app
    schema = app.openapi()
    checked = 0
    for path, ops in schema["paths"].items():
        for method, op in ops.items():
            if method not in ("get", "post", "put", "delete") or not op.get("x-not-wired"):
                continue
            probe = path.replace("{login}", "1000").replace("{symbol_name}", "EURUSD") \
                        .replace("{group_name}", "demo%5CStandard").replace("{rule_id}", "x") \
                        .replace("{gateway_id}", "x").replace("{feed_id}", "x") \
                        .replace("{allocation_id}", "x").replace("{client_id}", "x")
            r = world["_admin"].request(method.upper(), probe, headers=ADMIN, json={})
            assert r.status_code == 501, f"{method.upper()} {path} answered {r.status_code}"
            checked += 1
    assert checked >= 20, f"only {checked} skeletons walked - the surface shrank?"
