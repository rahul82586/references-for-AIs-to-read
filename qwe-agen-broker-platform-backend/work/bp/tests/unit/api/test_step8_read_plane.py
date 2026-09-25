"""Identity plane step 8 over real HTTP: the admin READ plane.

The risks these tests exist for:

* **The find_all()[:limit] trap.** The legacy list loaded every row then threw
  most away, and its "total" was the page size. The Mem doubles here POISON
  find_all: if any route reaches for it, the test explodes instead of passing.
* **Bare arrays + X-Total-Count.** The UI does `setPositions(data)`; an
  envelope would break every page at once. Paging metadata rides the header.
* **The F9 rule everywhere.** Tickets are the venue's own number or null -
  never 0, never a hash of our UUID - on deals and orders too, not just
  positions.
* **Credential material never leaves the server.** The account Security tab
  and the client's deprecated password columns serialize as BOOLEANS. One
  assertion sweeps the whole response text for hash material.
* **Rights decode server-side.** The Limits tab receives names, bits, labels
  and the `inverted` flags - the 0/1 problem must not reach the browser.
* **Route order.** /clients/schema before /clients/{client_id}; the managers
  LIST before /{login} (the M15 /groups/schema lesson, twice more).
* **Gating reads by the READING rights.** RIGHT_ACC_READ (25) for accounts,
  RIGHT_CLIENTS_ACCESS (96) for clients, RIGHT_TRADES_READ (29) for
  orders/deals/positions, RIGHT_CFG_MANAGERS (17) for the manager list. A
  read bit must not open a write plane and vice versa.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from decimal import Decimal
from typing import Any, Dict, List, Optional

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from api.auth import admin_dependencies
from api.auth.jwt_handler import create_access_token
from api.di_providers import register_di_providers
from api.routers.admin import accounts as accounts_router
from api.routers.admin import managers as managers_router
from api.routers.admin import reads as reads_router
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
from core.domains.oms.enums import (
    DealEntry,
    DealType,
    OrderState,
    OrderType,
    PositionAction,
)

ADMIN_KEY = admin_dependencies.ADMIN_API_KEY_ENV or "test-admin-api-key"
ADMIN_HEADERS = {"X-Admin-API-Key": ADMIN_KEY}


# ---------------------------------------------------------------------------
# doubles - find_all is POISONED: the read plane must never load every row
# ---------------------------------------------------------------------------


class PoisonedFindAll:
    async def find_all(self, *a, **k):  # pragma: no cover - exploding is the point
        raise AssertionError("route used find_all(); step 8 requires find_page (SQL-level paging)")


class MemPageRepo(PoisonedFindAll):
    """Generic in-memory find_page double mirroring the SQL contract:
    (rows, total_matching), filters applied, limit/offset sliced AFTER count."""

    def __init__(self, rows: List[Any], key=lambda r: 0):
        self.rows = rows
        self._key = key

    def _matches(self, row, filters: Dict[str, Any]) -> bool:
        for field, want in filters.items():
            if want is None:
                continue
            got = getattr(row, field, None)
            got = got.value if hasattr(got, "value") else got
            if str(got) != str(want):
                return False
        return True

    async def find_page(self, limit=100, offset=0, **filters):
        rows = [r for r in self.rows if self._matches(r, filters)]
        rows.sort(key=self._key)
        total = len(rows)
        return rows[offset:offset + limit], total


class MemAccountRepo(MemPageRepo):
    def __init__(self, rows):
        super().__init__(rows, key=lambda a: int(a.login))

    async def find_page(self, limit=100, offset=0, group_name=None, account_type=None, enabled=None, **rest):
        assert not rest, f"unknown account filters: {rest}"
        rows = self.rows
        if group_name is not None:
            rows = [a for a in rows if a.group is not None and a.group.name == group_name]
        if account_type is not None:
            rows = [a for a in rows if a.account_type.value == account_type]
        if enabled is not None:
            rows = [a for a in rows if bool(a.is_enabled) == bool(enabled)]
        rows = sorted(rows, key=lambda a: int(a.login))
        return rows[offset:offset + limit], len(rows)

    async def find_by_login(self, login, session=None):
        return next((a for a in self.rows if str(a.login) == str(login)), None)


class MemClientRepo(MemPageRepo):
    async def find_by_id(self, client_id):
        return next((c for c in self.rows if c.id == client_id), None)


class MemManagerRepo(MemPageRepo):
    def __init__(self, rows):
        super().__init__(rows, key=lambda m: int(m.login))

    async def find_by_login(self, login, session=None):
        return next((m for m in self.rows if str(m.login) == str(login)), None)


class MemOrderRepo(MemPageRepo):
    TERMINAL = ("CANCELLED", "FILLED", "REJECTED", "EXPIRED")
    ACTIVE = ("STARTED", "PLACED", "PARTIALLY_FILLED")

    async def find_page(self, limit=100, offset=0, account_login=None, symbol=None,
                        state=None, history=None, **rest):
        assert not rest, f"unknown order filters: {rest}"
        if state is not None and history is not None and (state in self.TERMINAL) != bool(history):
            raise ValueError(f"state={state!r} contradicts history={history!r}")
        rows = self.rows
        if account_login is not None:
            rows = [o for o in rows if int(o.account_login) == int(account_login)]
        if symbol is not None:
            rows = [o for o in rows if o.symbol == symbol]
        if state is not None:
            rows = [o for o in rows if o.state.value == state]
        elif history is not None:
            want = self.TERMINAL if history else self.ACTIVE
            rows = [o for o in rows if o.state.value in want]
        rows = sorted(rows, key=lambda o: o.time_setup, reverse=True)
        return rows[offset:offset + limit], len(rows)


# ---------------------------------------------------------------------------
# fixtures
# ---------------------------------------------------------------------------


def _group(name: str, account_type: AccountType) -> Group:
    return Group(
        name=name, account_type=account_type, server_id=1,
        currency="USD", currency_digits=2, auth_password_min=8,
        margin=MarginProfile(leverage_default=100, leverage_max=500),
    )


def _account(login: int, group: Group, *, disabled: bool = False, client_id: str = "") -> Account:
    kwargs = {}
    if disabled:
        kwargs = {"rights": UserRight(0), "is_enabled": False}
    return Account(
        login=login, group=group, group_id=group.id, client_id=client_id,
        account_type=group.account_type, currency="USD",
        balance=Money(Decimal("10000"), "USD"), equity=Money(Decimal("10000"), "USD"),
        first_name="Test", last_name=f"Trader{login}", **kwargs,
    )


def _manager(login: int, names: List[str]) -> ManagerAccount:
    mask = ManagerRightsMask.empty().grant(*names) if names else ManagerRightsMask.empty()
    return ManagerAccount(
        manager_id=str(login), login=str(login), role=ManagerRole.READ_ONLY,
        rights=mask, is_active=True, must_change_password=False, allowed_ips=[],
    )


def _deal(i: int, login: int, symbol: str, entry: DealEntry, when: datetime) -> Deal:
    return Deal(
        deal_id=f"deal-{i}", account_login=login, symbol=symbol,
        deal_type=DealType.BUY, entry=entry,
        volume=Volume(Decimal("0.10")), price=Price(Decimal("1.07961")),
        profit=Money(Decimal("1.50"), "USD"),
        external_id=("777000%d" % i) if i % 2 == 0 else None,
        created_at=when,
    )


def _order(i: int, login: int, state: OrderState, when: datetime) -> Order:
    return Order(
        ticket_id=f"order-{i}", account_login=login, symbol="EURUSD",
        order_type=OrderType.BUY, state=state,
        volume_initial=Volume(Decimal("0.10")), volume_current=Volume(Decimal("0.10")),
        time_setup=when,
    )


def _position(i: int, login: int, symbol: str, *, closed: bool = False, ext: Optional[str] = None) -> Position:
    p = Position(
        position_id=f"pos-{i}", account_login=login, symbol=symbol,
        action=PositionAction.BUY, external_id=ext,
        volume=Volume(Decimal("0.10")), price_open=Price(Decimal("1.07961")),
    )
    if closed:
        p.time_done = datetime(2026, 9, 12, tzinfo=timezone.utc)
    return p


T0 = datetime(2026, 9, 13, 10, 0, 0, tzinfo=timezone.utc)


@pytest.fixture()
def world():
    demo = _group("demo\\Standard", AccountType.DEMO)
    real = _group("real\\real", AccountType.REAL)
    accounts = [
        _account(1000, demo), _account(885863, demo), _account(886152, real),
        _account(900003, real, disabled=True), _account(900004, demo, client_id="cl-1"),
    ]
    accounts[0].password_hash = "$argon2id$v=19$m=65536,t=3,p=4$c2FsdA$SUPERSECRETVALUE"
    accounts[0].investor_password_hash = "$argon2id$v=19$m=65536,t=3,p=4$c2FsdA$INVESTORSECRET"
    clients = [
        Client(id="cl-1", client_id="KYC-1", full_name="Ann Example", country="IN",
               email="ann@example.test", password_hash="$argon2id$v=19$LEGACYCLIENTHASH"),
        Client(id="cl-2", client_id="KYC-2", full_name="Bo Sample", country="DE"),
    ]
    managers = [_manager(1000, ["RIGHT_ADMIN"]), _manager(208011, ["RIGHT_ACC_READ", "RIGHT_TRADES_READ"])]
    deals = [
        _deal(1, 886152, "EURUSD", DealEntry.IN, T0),
        _deal(2, 886152, "EURUSD", DealEntry.OUT, T0.replace(hour=11)),
        _deal(3, 1000, "BTCUSD", DealEntry.IN, T0.replace(hour=12)),
    ]
    orders = [
        _order(1, 886152, OrderState.PLACED, T0),
        _order(2, 886152, OrderState.FILLED, T0.replace(hour=11)),
        _order(3, 1000, OrderState.REJECTED, T0.replace(hour=12)),
    ]
    positions = [
        _position(1, 886152, "EURUSD", ext="5292088"),
        _position(2, 1000, "BTCUSD"),
        _position(3, 886152, "EURUSD", closed=True),
    ]

    providers = {
        "account_repo": MemAccountRepo(accounts),
        "client_repo": MemClientRepo(clients, key=lambda c: c.id),
        "manager_repo": MemManagerRepo(managers),
        "deal_repo": MemPageRepo(deals, key=lambda d: d.created_at),
        "order_repo": MemOrderRepo(orders),
        "position_repo": MemPageRepo(
            [p for p in positions],
            key=lambda p: p.time_create,
        ),
        "group_repo": None,
        "event_bus": None,
        "ledger_repo": None,
        "login_allocator": None,
        "uow_factory": None,
    }
    # the position double must honour the open-only default like SQL does
    class _PosRepo(MemPageRepo):
        async def find_page(self, limit=100, offset=0, account_login=None, symbol=None,
                            include_closed=False, **rest):
            assert not rest, f"unknown position filters: {rest}"
            rows = self.rows
            if not include_closed:
                rows = [p for p in rows if p.time_done is None]
            if account_login is not None:
                rows = [p for p in rows if int(p.account_login) == int(account_login)]
            if symbol is not None:
                rows = [p for p in rows if p.symbol == symbol]
            rows = sorted(rows, key=lambda p: p.time_create, reverse=True)
            return rows[offset:offset + limit], len(rows)
    providers["position_repo"] = _PosRepo(positions, key=lambda p: p.time_create)

    register_di_providers(providers)
    app = FastAPI()
    # the step-6 WRITE router too: the read-vs-write gating test must hit the
    # real POST /admin/accounts (405 from an unmounted path proves nothing)
    app.include_router(accounts_router.accounts_router)
    app.include_router(reads_router.account_reads_router)
    app.include_router(reads_router.client_reads_router)
    app.include_router(reads_router.trade_reads_router)
    app.include_router(managers_router.router)
    providers["_client"] = TestClient(app)
    providers["_accounts"] = accounts
    yield providers
    register_di_providers({k: None for k in providers if not k.startswith("_")})


def _mgr_headers(world, names: List[str], login: int = 800001, **kw) -> Dict[str, str]:
    manager = _manager(login, names)
    for k, v in kw.items():
        setattr(manager, k, v)
    world["manager_repo"].rows.append(manager)
    token = create_access_token({"sub": str(login), "is_manager": True})
    return {"Authorization": f"Bearer {token}"}


# ---------------------------------------------------------------------------
# accounts
# ---------------------------------------------------------------------------


def test_account_list_is_a_bare_array_with_an_honest_total(world):
    r = world["_client"].get("/api/v1/admin/accounts", headers=ADMIN_HEADERS)
    assert r.status_code == 200, r.text
    body = r.json()
    assert isinstance(body, list) and len(body) == 5       # bare array: the UI does setAccounts(data)
    assert r.headers["X-Total-Count"] == "5"
    assert [a["login"] for a in body] == ["1000", "885863", "886152", "900003", "900004"]  # NUMERIC order


def test_account_list_pages_with_limit_and_offset(world):
    r = world["_client"].get("/api/v1/admin/accounts", headers=ADMIN_HEADERS,
                             params={"limit": 2, "offset": 0})
    assert len(r.json()) == 2 and r.headers["X-Total-Count"] == "5"   # total is the MATCHING count, not the page
    r2 = world["_client"].get("/api/v1/admin/accounts", headers=ADMIN_HEADERS,
                              params={"limit": 2, "offset": 4})
    assert len(r2.json()) == 1


def test_account_list_filters(world):
    c = world["_client"]
    demo = c.get("/api/v1/admin/accounts", headers=ADMIN_HEADERS, params={"group": "demo\\Standard"}).json()
    assert {a["login"] for a in demo} == {"1000", "885863", "900004"}
    real = c.get("/api/v1/admin/accounts", headers=ADMIN_HEADERS, params={"account_type": "real"}).json()
    assert {a["login"] for a in real} == {"886152", "900003"}
    off = c.get("/api/v1/admin/accounts", headers=ADMIN_HEADERS, params={"enabled": "false"}).json()
    assert [a["login"] for a in off] == ["900003"]


def test_account_row_is_a_legacy_superset(world):
    """Same keys admin_router's list served (the UI reads them), plus identity."""
    row = world["_client"].get("/api/v1/admin/accounts", headers=ADMIN_HEADERS).json()[0]
    for key in ("login", "group", "account_type", "currency", "balance", "credit", "equity",
                "margin_used", "margin_free", "margin_level", "so_activation"):
        assert key in row, key
    assert row["balance"] == "10000"                       # decimals are STRINGS
    assert row["name"] == "Test Trader1000" and row["enabled"] is True
    assert isinstance(row["rights"], int) and row["leverage"] == 100


def test_account_detail_serves_the_six_tabs(world):
    r = world["_client"].get("/api/v1/admin/accounts/886152", headers=ADMIN_HEADERS)
    assert r.status_code == 200, r.text
    body = r.json()
    for tab in ("overview", "personal", "account", "limits", "subscriptions", "security"):
        assert tab in body, tab
    assert body["login"] == 886152
    assert body["group"]["name"] == "real\\real"
    assert body["subscriptions"] == []                     # honest empty, not invented


def test_account_detail_decodes_rights_server_side(world):
    body = world["_client"].get("/api/v1/admin/accounts/1000", headers=ADMIN_HEADERS).json()
    rights = body["limits"]["rights"]
    assert isinstance(rights["mask"], int) and rights["hex"].startswith("0x")
    by_name = {b["name"]: b for b in rights["bits"]}
    assert by_name["USER_RIGHT_ENABLED"]["granted"] is True
    # the two inverted bits carry their flag so the UI renders MT5's own labels
    assert by_name["USER_RIGHT_TRADE_DISABLED"]["inverted"] is True
    assert by_name["USER_RIGHT_TECHNICAL"]["inverted"] is True
    assert "USER_RIGHT_ENABLED" in rights["names"]


def test_account_detail_never_leaks_credential_material(world):
    r = world["_client"].get("/api/v1/admin/accounts/1000", headers=ADMIN_HEADERS)
    text = r.text
    assert "SUPERSECRETVALUE" not in text and "INVESTORSECRET" not in text and "argon2" not in text.lower()
    sec = r.json()["security"]
    assert sec["master_password_set"] is True and sec["investor_password_set"] is True
    assert set(sec) == {"master_password_set", "investor_password_set", "phone_password_set",
                        "webapi_password_set", "otp_enabled", "cert_serial_number",
                        "last_pass_change", "last_ip"}


def test_account_detail_404s_rather_than_fabricating(world):
    r = world["_client"].get("/api/v1/admin/accounts/424242", headers=ADMIN_HEADERS)
    assert r.status_code == 404


# ---------------------------------------------------------------------------
# clients
# ---------------------------------------------------------------------------


def test_client_list_and_detail(world):
    c = world["_client"]
    r = c.get("/api/v1/admin/clients", headers=ADMIN_HEADERS)
    assert r.status_code == 200 and len(r.json()) == 2 and r.headers["X-Total-Count"] == "2"
    d = c.get("/api/v1/admin/clients/cl-1", headers=ADMIN_HEADERS)
    assert d.status_code == 200
    body = d.json()
    assert body["full_name"] == "Ann Example" and body["client_id"] == "KYC-1"
    assert "LEGACYCLIENTHASH" not in d.text and "argon2" not in d.text.lower()
    assert body["security"]["password_set"] is True        # boolean, never the hash
    assert c.get("/api/v1/admin/clients/nope", headers=ADMIN_HEADERS).status_code == 404


def test_client_schema_route_is_not_swallowed_by_the_detail_route(world):
    """/schema BEFORE /{client_id} - the M15 /groups/schema lesson."""
    r = world["_client"].get("/api/v1/admin/clients/schema", headers=ADMIN_HEADERS)
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["object"] == "client" and body["wire_section"] == "IMTClient"
    fields = {f["field"]: f for f in body["fields"]}
    assert fields["full_name"]["mt5"] == "PersonName"      # SDK-grounded, not guessed
    assert fields["zip_code"]["mt5"] == "AddressPostcode"
    assert fields["id_number"]["mt5"] == "PersonDocumentNumber"
    assert fields["password_set"]["write_only"] is True


# ---------------------------------------------------------------------------
# trade reads (ENDPOINTS B2)
# ---------------------------------------------------------------------------


def test_positions_read_is_open_only_unless_asked(world):
    c = world["_client"]
    rows = c.get("/api/v1/admin/positions", headers=ADMIN_HEADERS).json()
    assert len(rows) == 2 and all("pos-3" != p["position_id"] for p in rows)
    everything = c.get("/api/v1/admin/positions", headers=ADMIN_HEADERS,
                       params={"include_closed": "true"}).json()
    assert len(everything) == 3


def test_position_rows_follow_the_f9_rule(world):
    rows = world["_client"].get("/api/v1/admin/positions", headers=ADMIN_HEADERS).json()
    by_id = {p["position_id"]: p for p in rows}
    assert by_id["pos-1"]["ticket"] == 5292088             # the venue's own number
    assert by_id["pos-2"]["ticket"] is None                # never 0


def test_deals_read_with_filters(world):
    c = world["_client"]
    r = c.get("/api/v1/admin/deals", headers=ADMIN_HEADERS)
    assert r.status_code == 200 and r.headers["X-Total-Count"] == "3"
    out = c.get("/api/v1/admin/deals", headers=ADMIN_HEADERS, params={"entry": "OUT"}).json()
    assert len(out) == 1 and out[0]["deal_id"] == "deal-2"
    mine = c.get("/api/v1/admin/deals", headers=ADMIN_HEADERS, params={"login": 1000}).json()
    assert [d["symbol"] for d in mine] == ["BTCUSD"]
    # tickets: deal-2 has external 7770002, deal-1/3 have none
    by_id = {d["deal_id"]: d for d in r.json()}
    assert by_id["deal-2"]["ticket"] == 7770002
    assert by_id["deal-1"]["ticket"] is None


def test_orders_active_vs_history_split(world):
    c = world["_client"]
    everything = c.get("/api/v1/admin/orders", headers=ADMIN_HEADERS).json()
    assert len(everything) == 3
    active = c.get("/api/v1/admin/orders", headers=ADMIN_HEADERS, params={"history": "false"}).json()
    assert [o["state"] for o in active] == ["PLACED"]
    hist = c.get("/api/v1/admin/orders/history", headers=ADMIN_HEADERS).json()
    assert {o["state"] for o in hist} == {"FILLED", "REJECTED"}


def test_contradicting_state_and_history_is_a_400_not_an_empty_page(world):
    r = world["_client"].get("/api/v1/admin/orders", headers=ADMIN_HEADERS,
                             params={"state": "FILLED", "history": "false"})
    assert r.status_code == 400
    assert "contradicts" in r.json()["detail"]


# ---------------------------------------------------------------------------
# managers list
# ---------------------------------------------------------------------------


def test_manager_list_is_paged_and_decoded(world):
    r = world["_client"].get("/api/v1/admin/managers", headers=ADMIN_HEADERS)
    assert r.status_code == 200, r.text
    body = r.json()
    assert isinstance(body, list) and len(body) == 2       # resolves as the LIST, not a login named ""
    assert r.headers["X-Total-Count"] == "2"
    admin = next(m for m in body if m["login"] == 1000)
    assert admin["rights_count"] >= 1 and "RIGHT_ADMIN" in admin["rights_names"]


# ---------------------------------------------------------------------------
# gating: read bits open read planes - and nothing else
# ---------------------------------------------------------------------------


def test_acc_read_manager_sees_accounts_but_not_trades_or_clients(world):
    h = _mgr_headers(world, ["RIGHT_ACC_READ"])
    c = world["_client"]
    assert c.get("/api/v1/admin/accounts", headers=h).status_code == 200
    assert c.get("/api/v1/admin/accounts/1000", headers=h).status_code == 200
    assert c.get("/api/v1/admin/positions", headers=h).status_code == 403
    assert c.get("/api/v1/admin/deals", headers=h).status_code == 403
    assert c.get("/api/v1/admin/clients", headers=h).status_code == 403
    assert c.get("/api/v1/admin/managers", headers=h).status_code == 403


def test_trades_read_manager_sees_the_book_but_not_accounts(world):
    h = _mgr_headers(world, ["RIGHT_TRADES_READ"])
    c = world["_client"]
    for path in ("/api/v1/admin/positions", "/api/v1/admin/deals", "/api/v1/admin/orders"):
        assert c.get(path, headers=h).status_code == 200, path
    assert c.get("/api/v1/admin/accounts", headers=h).status_code == 403


def test_clients_access_manager_sees_clients_including_schema(world):
    h = _mgr_headers(world, ["RIGHT_CLIENTS_ACCESS"])
    c = world["_client"]
    assert c.get("/api/v1/admin/clients", headers=h).status_code == 200
    assert c.get("/api/v1/admin/clients/cl-1", headers=h).status_code == 200
    assert c.get("/api/v1/admin/clients/schema", headers=h).status_code == 200
    assert c.get("/api/v1/admin/accounts", headers=h).status_code == 403


def test_a_read_bit_never_opens_a_write_plane(world):
    """RIGHT_ACC_READ is not RIGHT_ACC_MANAGER: the step-6 create must refuse."""
    h = _mgr_headers(world, ["RIGHT_ACC_READ"])
    r = world["_client"].post("/api/v1/admin/accounts", headers=h, json={"group_name": "demo\\Standard"})
    assert r.status_code == 403


def test_must_change_password_blocks_the_read_plane_too(world):
    h = _mgr_headers(world, ["RIGHT_ACC_READ"], login=800002, must_change_password=True)
    assert world["_client"].get("/api/v1/admin/accounts", headers=h).status_code == 403


def test_unwired_repositories_are_loud_503s(world):
    register_di_providers({"account_repo": None, "client_repo": None})
    c = world["_client"]
    assert c.get("/api/v1/admin/accounts", headers=ADMIN_HEADERS).status_code == 503
    assert c.get("/api/v1/admin/clients", headers=ADMIN_HEADERS).status_code == 503
