"""
The client-facing trade endpoint, over real HTTP.

Everything else in the M4 suite drives the application layer directly. This file drives
`POST /api/v1/trade/orders` through FastAPI's TestClient, with the app assembled by its
own startup handler - the same path `cli start` / `uvicorn api.main:app` takes.

It exists because the endpoint used to be unable to fail. `get_create_order_handler()`
returned a FallbackCreateOrderHandler whose MockOrder answered every request with ticket
1001 and state "FILLED", so the API returned HTTP 200 and a filled ticket for an order
that was never risk-checked, priced, persisted or hedged. Two further defects sat behind
it: the request schema typed `order_type` as a bare string, so the Order entity carried
"BUY" instead of OrderType.BUY and `is_market()` returned False; and `create_app()` was
called with no container at module scope, so startup raised KeyError before the server
could serve anything at all.

Loop discipline, because it is easy to get wrong here: the harness is built with
`asyncio.run` and the HTTP calls run on TestClient's own portal loop. Prices are
therefore installed into the market data engine's in-memory tick map directly - which is
the state `process_tick` writes - rather than awaited from a second loop, and assertions
read the repositories synchronously. Nothing loop-bound is shared between the two.
"""
import asyncio
from decimal import Decimal

import pytest

from api.auth.jwt_handler import create_access_token
from core.domains.market_data.models import Tick
from core.domains.oms.enums import DealType, OrderState, PositionAction
from tests.integration.trading_harness import DEFAULT_LOGIN, TradingHarness, default_coverage

BID = Decimal("1.10000")
ASK = Decimal("1.10010")


def install_tick(harness, symbol: str, bid: Decimal, ask: Decimal) -> None:
    """Put a price in the engine's tick map, synchronously.

    This is exactly the state `MarketDataEngine.process_tick()` leaves behind for pricing
    purposes (`self.ticks[symbol] = tick`), without needing the loop the engine was built
    on. The margin pipeline is not driven, which these endpoint tests do not need - the
    stop-out chain is proved in test_order_execution_e2e.py.
    """
    harness.market_data_engine.ticks[symbol] = Tick(
        symbol=symbol,
        bid=Decimal(str(bid)),
        ask=Decimal(str(ask)),
        spread=Decimal(str(ask)) - Decimal(str(bid)),
        source="TEST",
    )


def account_of(harness, login: int = DEFAULT_LOGIN):
    """Read an account straight out of the repository, without awaiting."""
    return harness.account_repo.accounts[login]


@pytest.fixture
def client_and_harness():
    """An app whose OWN startup wired the trading plane, plus the harness behind it.

    The provider dict is saved and restored: create_app() registers into process-wide
    state, and leaving a harness in it would let a later test resolve repositories that
    belong to a broker which no longer exists.
    """
    from fastapi.testclient import TestClient

    from api import di_providers
    from api.main import create_app

    saved = dict(di_providers._container)
    harness = asyncio.run(
        TradingHarness(coverage=default_coverage()).build(wire_trading=False)
    )
    try:
        app = create_app(harness.providers)
        with TestClient(app) as client:
            yield client, harness, app
    finally:
        di_providers._container.clear()
        di_providers._container.update(saved)


def auth_headers(login: int = DEFAULT_LOGIN) -> dict:
    token = create_access_token({"sub": str(login), "role": "client"})
    return {"Authorization": f"Bearer {token}"}


def place(client, payload: dict, login: int = DEFAULT_LOGIN):
    return client.post("/api/v1/trade/orders", headers=auth_headers(login), json=payload)


# ---------------------------------------------------------------------------


def test_startup_wires_a_real_trading_plane(client_and_harness):
    """The app that starts is the app that trades: no mocks, and the pieces are present."""
    client, harness, app = client_and_harness

    from api.di_providers import get_create_order_handler
    from application.commands.create_order import CreateOrderHandler

    assert isinstance(get_create_order_handler(), CreateOrderHandler)

    stack = app.state.trading_stack
    assert stack is not None
    assert stack.orchestrator is not None
    assert stack.matching_engine is not None
    assert stack.liquidation_worker is not None
    # the router loaded its (empty) rule table rather than being left unrefreshed
    assert stack.router._rules_loaded is True
    # and the stub LP is announced rather than silently trusted
    assert any("STUB" in w for w in stack.warnings)

    # exactly one orchestrator is listening: wiring the plane twice would execute twice
    assert harness.event_bus.handler_count("order.approved") == 1


def test_post_market_buy_returns_a_real_filled_order(client_and_harness):
    client, harness, app = client_and_harness
    install_tick(harness, "EURUSD", BID, ASK)

    response = place(client, {"symbol": "EURUSD", "order_type": "BUY", "volume": "0.10"})

    assert response.status_code == 200, response.text
    body = response.json()

    # NOT the mock: a real ticket, and the live ask rather than a hardcoded 1.0850
    assert body["ticket_id"] != "1001"
    assert body["state"] == OrderState.FILLED.value
    assert Decimal(body["price"]) == ASK
    assert Decimal(body["volume"]) == Decimal("0.10")
    assert Decimal(body["filled_volume"]) == Decimal("0.10")

    # and it is real all the way down, not only in the response body
    positions = harness.open_positions()
    assert len(positions) == 1
    assert positions[0].action == PositionAction.BUY
    assert positions[0].price_open.value == ASK

    deals = harness.deals_for()
    assert len(deals) == 1
    assert deals[0].deal_type == DealType.BUY
    assert deals[0].price.value == ASK

    account = account_of(harness)
    # 0.10 lots * 100,000 / 100 = 100 EUR, converted at the ask: 100 * 1.10010
    assert account.margin_used.amount == Decimal("110.01")
    # client bought, so the broker is short
    assert harness.coverage_exposure("EURUSD") == Decimal("-0.10")


def test_post_market_sell_fills_at_the_bid(client_and_harness):
    client, harness, app = client_and_harness
    install_tick(harness, "EURUSD", BID, ASK)

    response = place(client, {"symbol": "EURUSD", "order_type": "SELL", "volume": "0.10"})

    assert response.status_code == 200, response.text
    assert Decimal(response.json()["price"]) == BID
    assert harness.open_positions()[0].action == PositionAction.SELL
    assert harness.coverage_exposure("EURUSD") == Decimal("0.10")


def test_post_order_without_a_price_is_rejected_not_faked(client_and_harness):
    """No tick means no execution price. The endpoint must say so, not invent one."""
    client, harness, app = client_and_harness

    response = place(client, {"symbol": "EURUSD", "order_type": "SELL", "volume": "0.10"})

    assert response.status_code == 400, response.text
    detail = response.json()["detail"].lower()
    assert "bid" in detail or "ask" in detail
    assert harness.open_positions() == []
    assert harness.deals_for() == []
    assert harness.coverage_exposure("EURUSD") == Decimal("0")


def test_post_order_with_an_unknown_side_is_a_422(client_and_harness):
    """Typed at the edge: an invalid order_type never reaches the execution path."""
    client, harness, app = client_and_harness
    install_tick(harness, "EURUSD", BID, ASK)

    response = place(client, {"symbol": "EURUSD", "order_type": "BUY_HARD", "volume": "0.10"})

    assert response.status_code == 422, response.text
    assert harness.open_positions() == []


def test_post_order_without_a_token_is_unauthorized(client_and_harness):
    client, harness, app = client_and_harness
    install_tick(harness, "EURUSD", BID, ASK)

    response = client.post(
        "/api/v1/trade/orders",
        json={"symbol": "EURUSD", "order_type": "BUY", "volume": "0.10"},
    )

    assert response.status_code == 401
    assert harness.open_positions() == []


def test_pending_order_over_http_rests_and_reports_placed(client_and_harness):
    """A limit order is accepted, rests in the book, and reports PLACED - not FILLED."""
    client, harness, app = client_and_harness
    install_tick(harness, "EURUSD", BID, ASK)

    response = place(
        client,
        {"symbol": "EURUSD", "order_type": "BUY_LIMIT", "volume": "0.10", "price": "1.09000"},
    )

    assert response.status_code == 200, response.text
    assert response.json()["state"] == OrderState.PLACED.value
    assert harness.open_positions() == []
    assert harness.deals_for() == []
    assert app.state.trading_stack.matching_engine.get_market_state("EURUSD")["resting_orders"] == 1


def test_insufficient_margin_over_http_is_a_400(client_and_harness):
    client, harness, app = client_and_harness
    install_tick(harness, "EURUSD", BID, ASK)

    # 10,000 USD of balance cannot margin 100 lots
    response = place(client, {"symbol": "EURUSD", "order_type": "BUY", "volume": "100"})

    assert response.status_code == 400, response.text
    assert harness.open_positions() == []
    assert account_of(harness).margin_used.amount == Decimal("0")


def test_module_level_app_boots_with_a_default_container():
    """`uvicorn api.main:app` must produce a server, not a KeyError at startup.

    Nothing is queried here - DatabaseManager only builds an engine and a session factory -
    so this asserts the wiring exists without needing PostgreSQL to be running.
    """
    from api import di_providers
    from api.main import default_providers

    saved = dict(di_providers._container)
    di_providers._container.clear()
    try:
        providers = default_providers()
        for key in (
            "event_bus",
            "group_repo",
            "symbol_repo",
            "account_repo",
            "order_repo",
            "deal_repo",
            "position_repo",
            "routing_rule_repo",
            "coverage_repo",
            "holiday_repo",
        ):
            assert key in providers, f"default_providers() is missing {key}"
        assert providers["event_bus"] is not None
    finally:
        di_providers._container.clear()
        di_providers._container.update(saved)
