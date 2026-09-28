"""F8/F9 over real HTTP: the manager plane's cross-account positions read.

`GET /api/v1/manager/PositionGet` is the ONLY cross-account positions endpoint
the platform has - the Theia UI's Positions, Exposure and Margin-Call pages all
read it (ENDPOINTS.md §3, gap matrix B0). Before this fix it returned `[]` +
`ticket=0` against a live book of 31 open positions, because four faults sat
behind one blanket `except Exception`:

1. the route constructed `GetPositionsQuery(account_login=..., symbol=...)` -
   the client-plane query has no `symbol` field and requires `account_login`
   as a str, so EVERY call raised TypeError;
2. the client-plane handler returns dicts; the route then read entity
   ATTRIBUTES (`.action.value`, `.price_open.value`) off them;
3. `ticket=int(position_id) if isdigit() else 0` - position_id is a UUID or
   `{login}_{SYMBOL}_{hex}`, never numeric, so ticket was 0 for every row
   (F9); the real venue ticket lives in `external_id`;
4. `price_current` is Optional on the entity (None until the first tick - 24 of
   the 31 live open rows) and the old required `.value` access raised on them.

These tests pin the rebuilt contract: one shared serializer, a cross-account
handler that dispatches to the repository's own SQL-level reads, and the
/account/positions error contract - 503 unwired, 500 on failure, `[]` ONLY for
a genuinely flat book. An empty list is an answer; it must never be an error
in disguise.
"""
from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal
from typing import Any, Dict, List, Optional

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from api.auth.jwt_handler import create_access_token
from api.di_providers import register_di_providers
from api.routers.manager import main as manager_main
from application.queries.get_positions import GetManagerPositionsQueryHandler
from core.domains.common.value_objects import Money, Price, Volume
from core.domains.oms.entities.position import Position
from core.domains.oms.enums import PositionAction

URL = "/api/v1/manager/PositionGet"


# ---------------------------------------------------------------------------
# doubles
# ---------------------------------------------------------------------------


class MemPositionRepo:
    """Stands in for SqlPositionRepository; records WHICH read was dispatched.

    The dispatch record matters: the handler must use the repository's own
    scoped reads (get_positions_by_account / get_by_symbol /
    get_by_account_and_symbol / get_open_positions - the last filtered on
    `time_done IS NULL` in SQL), never find-everything-then-filter-in-Python.
    """

    def __init__(self, rows: List[Position]) -> None:
        self.rows = rows
        self.calls: List[str] = []
        self.raise_on: Optional[str] = None

    async def get_open_positions(self, session=None):
        self.calls.append("get_open_positions")
        if self.raise_on == "get_open_positions":
            raise RuntimeError("db is on fire")
        return [p for p in self.rows if p.time_done is None]

    async def get_positions_by_account(self, account_login: int, session=None):
        self.calls.append("get_positions_by_account")
        if self.raise_on == "get_positions_by_account":
            raise RuntimeError("db is on fire")
        return [p for p in self.rows if p.account_login == account_login and p.time_done is None]

    async def get_by_symbol(self, symbol: str):
        self.calls.append("get_by_symbol")
        if self.raise_on == "get_by_symbol":
            raise RuntimeError("db is on fire")
        return [p for p in self.rows if p.symbol == symbol and p.time_done is None]

    async def get_by_account_and_symbol(self, account_login: int, symbol: str):
        self.calls.append("get_by_account_and_symbol")
        return [
            p for p in self.rows
            if p.account_login == account_login and p.symbol == symbol and p.time_done is None
        ]


def _position(
    login: int,
    symbol: str,
    action: PositionAction = PositionAction.BUY,
    *,
    external_id: Optional[str] = None,
    price_current: Optional[Decimal] = None,
    sl: Optional[Decimal] = None,
    tp: Optional[Decimal] = None,
    volume: str = "0.10",
    price_open: str = "1.07961",
    profit: str = "0",
    swap: str = "0",
    commission: str = "0",
    magic: int = 0,
    comment: str = "",
    closed: bool = False,
) -> Position:
    pos = Position(
        account_login=login,
        symbol=symbol,
        action=action,
        external_id=external_id,
        volume=Volume(Decimal(volume)),
        price_open=Price(Decimal(price_open)),
        price_current=Price(price_current) if price_current is not None else None,
        price_sl=Price(sl) if sl is not None else None,
        price_tp=Price(tp) if tp is not None else None,
        profit=Money(Decimal(profit), "USD"),
        swap=Money(Decimal(swap), "USD"),
        commission=Money(Decimal(commission), "USD"),
        magic_number=magic,
        comment=comment,
    )
    if closed:
        pos.time_done = datetime(2026, 9, 12, 12, 0, 0, tzinfo=timezone.utc)
    return pos


@pytest.fixture()
def world():
    """A book shaped like the live one: two accounts, a real venue ticket,
    a NULL price_current row, SL/TP set on one, and one CLOSED position that
    must never appear."""
    rows = [
        _position(886152, "EURUSD", PositionAction.BUY, external_id="5292088",
                  price_current=Decimal("1.15968"), sl=Decimal("1.05000"),
                  tp=Decimal("1.20000"), profit="800.70", swap="-1.25",
                  commission="-7.00", magic=20260913, comment="trade-server"),
        _position(886152, "BTCUSD", PositionAction.SELL,
                  price_open="77403.93", volume="0.01"),          # no ticket, no current price
        _position(900003, "EURUSD", PositionAction.BUY, external_id="pos-abc",
                  price_current=Decimal("1.15970")),               # non-numeric external id
        _position(900003, "XAUUSD", PositionAction.SELL, closed=True),
    ]
    repo = MemPositionRepo(rows)
    handler = GetManagerPositionsQueryHandler(position_repo=repo)
    register_di_providers({
        "manager_positions_query_handler": handler,
        "account_repo": None,
        "token_blacklist": None,
    })
    app = FastAPI()
    app.include_router(manager_main.router)
    client = TestClient(app)
    token = create_access_token({"sub": "800001", "is_manager": True})
    headers = {"Authorization": f"Bearer {token}"}
    yield {"client": client, "repo": repo, "headers": headers, "rows": rows}
    register_di_providers({"manager_positions_query_handler": None})


def _get(world, **params):
    return world["client"].get(URL, headers=world["headers"], params=params or None)


# ---------------------------------------------------------------------------
# the cross-account read and its filter routing
# ---------------------------------------------------------------------------


def test_unfiltered_returns_the_whole_book_across_accounts(world):
    """The bug it replaces: [] against a live book of 31. F8."""
    r = _get(world)
    assert r.status_code == 200, r.text
    body = r.json()
    assert len(body) == 3                                    # the CLOSED row is not in the book
    assert {p["login"] for p in body} == {886152, 900003}    # cross-account, not caller-scoped
    assert world["repo"].calls == ["get_open_positions"]     # SQL-level read, not find-all-then-filter


def test_login_filter_routes_to_the_account_scoped_read(world):
    r = _get(world, login=886152)
    assert r.status_code == 200
    body = r.json()
    assert len(body) == 2 and all(p["login"] == 886152 for p in body)
    assert world["repo"].calls == ["get_positions_by_account"]


def test_symbol_filter_is_cross_account(world):
    r = _get(world, symbol="EURUSD")
    assert r.status_code == 200
    body = r.json()
    assert {p["login"] for p in body} == {886152, 900003}
    assert world["repo"].calls == ["get_by_symbol"]


def test_login_and_symbol_together_route_to_the_scoped_pair_read(world):
    r = _get(world, login=900003, symbol="EURUSD")
    assert r.status_code == 200
    assert len(r.json()) == 1
    assert world["repo"].calls == ["get_by_account_and_symbol"]


def test_blank_symbol_is_no_symbol_filter(world):
    """`?symbol=` (empty) must not become a filter for the symbol named ''."""
    r = _get(world, symbol="")
    assert r.status_code == 200
    assert len(r.json()) == 3
    assert world["repo"].calls == ["get_open_positions"]


# ---------------------------------------------------------------------------
# F9: the ticket
# ---------------------------------------------------------------------------


def test_ticket_is_the_real_external_ticket(world):
    body = _get(world).json()
    by_symbol = {p["symbol"]: p for p in body if p["login"] == 886152}
    assert by_symbol["EURUSD"]["ticket"] == 5292088          # the venue's own number


def test_ticket_is_null_not_zero_when_there_is_no_external_ticket(world):
    """F9's regression pin: 0 is a fabricated ticket; a UI keying rows by
    ticket would collapse every internal position into one."""
    body = _get(world).json()
    btc = next(p for p in body if p["symbol"] == "BTCUSD")
    assert btc["ticket"] is None


def test_a_non_numeric_external_id_never_crashes_and_never_invents_a_ticket(world):
    body = _get(world, login=900003, symbol="EURUSD").json()
    assert body[0]["ticket"] is None                          # "pos-abc" is not a ticket


def test_position_id_is_exposed_as_the_canonical_row_key(world):
    body = _get(world).json()
    assert all(isinstance(p["position_id"], str) and p["position_id"] for p in body)
    assert len({p["position_id"] for p in body}) == len(body)  # unique keys, unlike ticket=None


# ---------------------------------------------------------------------------
# honest values: the entity's Optional stays Optional, the VOs serialize right
# ---------------------------------------------------------------------------


def test_price_current_null_stays_null(world):
    """24 of the 31 live open positions have never seen a tick. Serving 0 or
    price_open would invent a market price - the D13/D16 class."""
    body = _get(world).json()
    btc = next(p for p in body if p["symbol"] == "BTCUSD")
    assert btc["price_current"] is None
    assert btc["price_open"] == "77403.93"


def test_price_current_present_serializes_its_value(world):
    body = _get(world, login=886152, symbol="EURUSD").json()
    assert body[0]["price_current"] == "1.15968"


def test_sl_tp_commission_swap_are_populated(world):
    """Declared-but-never-populated was fault (c): the old route never even
    passed these to the schema."""
    body = _get(world, login=886152, symbol="EURUSD").json()
    p = body[0]
    assert p["sl"] == "1.05000" or p["price_sl"] == "1.05000"  # alias or name
    assert p["tp"] == "1.20000" or p["price_tp"] == "1.20000"
    assert p["commission"] == "-7.00"
    assert p["swap"] == "-1.25"
    assert p["profit"] == "800.70"


def test_volume_and_prices_use_the_value_objects_vocabulary(world):
    """Volume/Price carry .value, Money carries .amount - the serializer's one
    real bug in session 6, caught by its own tests then, pinned here now."""
    body = _get(world, login=886152, symbol="EURUSD").json()
    p = body[0]
    assert p["volume"] == "0.10"
    assert p["price_open"] == "1.07961"


def test_action_serializes_as_the_mt5_word(world):
    body = _get(world).json()
    actions = {p["symbol"]: p["action"] for p in body if p["login"] == 886152}
    assert actions == {"EURUSD": "BUY", "BTCUSD": "SELL"}


def test_metadata_rides_along(world):
    body = _get(world, login=886152, symbol="EURUSD").json()
    p = body[0]
    assert p["magic"] == 20260913
    assert p["comment"] == "trade-server"
    assert p["time_create"] is not None and p["time_update"] is not None


# ---------------------------------------------------------------------------
# the error contract: [] is an answer, never an error in disguise
# ---------------------------------------------------------------------------


def test_unwired_handler_is_a_loud_503_not_an_empty_list(world):
    register_di_providers({"manager_positions_query_handler": None})
    r = _get(world)
    assert r.status_code == 503
    assert "not wired" in r.json()["detail"]


def test_repository_failure_is_a_500_not_an_empty_list(world):
    """The blanket `except Exception: return []` is what hid all four faults
    for the endpoint's entire life."""
    world["repo"].raise_on = "get_open_positions"
    r = _get(world)
    assert r.status_code == 500
    assert r.json()["detail"] == "Could not read positions"


def test_a_genuinely_flat_book_answers_200_with_an_empty_list(world):
    world["repo"].rows = []
    r = _get(world)
    assert r.status_code == 200
    assert r.json() == []


def test_closed_positions_are_not_in_the_book(world):
    """The double mirrors the repository contract (time_done IS NULL); the
    seeded CLOSED row must never surface on any filter combination."""
    for params in ({}, {"login": 900003}, {"symbol": "XAUUSD"}, {"login": 900003, "symbol": "XAUUSD"}):
        r = _get(world, **params)
        assert r.status_code == 200
        assert all(p["symbol"] != "XAUUSD" for p in r.json()), params
