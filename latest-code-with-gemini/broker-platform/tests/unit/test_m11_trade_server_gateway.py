"""The trade-server A-Book gateway: outcome mapping, without a terminal.

`TradeServerLiquidityGateway` hedges through a real MT5 terminal, so most of its
risk is in one question: can it tell *the terminal said no* from *we do not know*?
Getting that wrong is expensive in a specific direction - treating an unknown as a
rejection makes the orchestrator cancel the client side of a hedge that may be
live, leaving the broker naked with no record.

Every branch is pinned here against an injected transport, so the mapping is
proven before a single real order is placed. The live path is
`scripts/m11_proof_live_hedge.py`.
"""
from decimal import Decimal

import pytest

from core.domains.oms.entities.order import Order
from core.domains.oms.enums import OrderType
from core.domains.common.value_objects import Price, Volume
from infrastructure.gateways.trade_server_gateway import (
    HedgeStateUnknown,
    TradeServerLiquidityGateway,
    TradeServerReject,
)

URL = "https://tunnel.example"


def buy(volume="0.01", symbol="BTCUSD", order_type=OrderType.BUY):
    return Order(
        ticket_id="TCK-1", account_login=885863, symbol=symbol, order_type=order_type,
        volume_initial=Volume(Decimal(volume)), volume_current=Volume(Decimal(volume)),
        price_order=None,
    )


def gateway(handler):
    """A gateway whose transport is `handler(method, path, payload) -> (status, body)`."""
    return TradeServerLiquidityGateway(URL, session=handler)


def ok_body(ticket=5300001, price=77310.83, volume=0.01, side="buy"):
    return (200, {"status": "success",
                  "data": {"success": True, "ticket": ticket, "price": price,
                           "volume": volume, "side": side}})


# ------------------------------------------------------------------- success

@pytest.mark.asyncio
async def test_a_terminal_fill_becomes_the_report_m11_books_from():
    seen = {}

    async def transport(method, path, payload):
        seen.update(method=method, path=path, payload=payload)
        return ok_body()

    report = await gateway(transport).send_order(buy(), gateway_id="MT5")

    assert report["status"] == "FILLED"
    assert report["stub"] is False, "a real terminal hedge must not be marked stub"
    assert report["price"] == "77310.83", "the client books at the TERMINAL's price"
    assert report["volume"] == "0.01"
    assert report["order_id"] == "5300001"
    assert report["venue"] == "TradeServerMT5"
    # the request trade-server actually expects
    assert seen["path"] == "/api/v1/place-order"
    assert seen["payload"]["symbol"] == "BTCUSD"
    assert seen["payload"]["side"] == "buy"
    assert seen["payload"]["volume"] == 0.01
    assert seen["payload"]["type_filling"] == "FOK"


@pytest.mark.asyncio
async def test_a_sell_maps_to_the_terminal_side():
    async def transport(method, path, payload):
        assert payload["side"] == "sell"
        return ok_body(side="sell")

    report = await gateway(transport).send_order(
        buy(order_type=OrderType.SELL), gateway_id="MT5")
    assert report["side"] == "SELL"


@pytest.mark.asyncio
async def test_a_smaller_fill_is_reported_partial_not_full():
    """The terminal's own volume is authoritative - a partial must be visible."""
    async def transport(method, path, payload):
        return ok_body(volume=0.004)

    report = await gateway(transport).send_order(buy("0.01"), gateway_id="MT5")
    assert report["status"] == "PARTIAL"
    assert Decimal(report["volume"]) == Decimal("0.004")


@pytest.mark.asyncio
async def test_price_survives_as_an_exact_decimal_not_a_float():
    async def transport(method, path, payload):
        return ok_body(price=77310.83)

    report = await gateway(transport).send_order(buy(), gateway_id="MT5")
    assert Decimal(report["price"]) == Decimal("77310.83")
    assert "E" not in report["price"] and "e" not in report["price"]


# ------------------------------------------------- definite rejection branches

@pytest.mark.asyncio
async def test_an_mt5_retcode_is_a_definite_rejection():
    """The terminal answered, so rejecting the client is honest."""
    async def transport(method, path, payload):
        return (500, {"detail": "Invalid volume (10014)"})

    with pytest.raises(TradeServerReject) as ei:
        await gateway(transport).send_order(buy(), gateway_id="MT5")
    assert ei.value.retcode == 10014
    assert not getattr(ei.value, "hedge_state_unknown", False)


@pytest.mark.asyncio
async def test_unsupported_filling_mode_is_a_rejection_not_an_unknown():
    async def transport(method, path, payload):
        return (500, {"detail": "Unsupported filling mode (10030)"})

    with pytest.raises(TradeServerReject) as ei:
        await gateway(transport).send_order(buy(), gateway_id="MT5")
    assert ei.value.retcode == 10030


@pytest.mark.asyncio
async def test_no_active_mt5_connection_is_a_rejection():
    """400 means the terminal was never asked, so nothing can be live."""
    async def transport(method, path, payload):
        return (400, {"detail": "No active trade connection"})

    with pytest.raises(TradeServerReject):
        await gateway(transport).send_order(buy(), gateway_id="MT5")


@pytest.mark.asyncio
async def test_a_structured_success_false_is_a_rejection():
    async def transport(method, path, payload):
        return (200, {"status": "success", "data": {"success": False, "error": "Market closed"}})

    with pytest.raises(TradeServerReject) as ei:
        await gateway(transport).send_order(buy(), gateway_id="MT5")
    assert "Market closed" in str(ei.value)


# ------------------------------------------------------- unknown-state branches

@pytest.mark.asyncio
async def test_a_500_without_a_retcode_is_unknown_not_a_rejection():
    """trade-server itself failed; order_send may still have run."""
    async def transport(method, path, payload):
        return (500, {"detail": "Internal Server Error"})

    with pytest.raises(HedgeStateUnknown) as ei:
        await gateway(transport).send_order(buy(), gateway_id="MT5")
    assert ei.value.hedge_state_unknown is True


@pytest.mark.asyncio
async def test_an_unexpected_status_is_unknown():
    async def transport(method, path, payload):
        return (422, {"detail": "validation failed"})

    with pytest.raises(HedgeStateUnknown):
        await gateway(transport).send_order(buy(), gateway_id="MT5")


@pytest.mark.asyncio
async def test_a_transport_failure_is_unknown():
    """The real urllib path: DNS/refused/reset must not become a rejection."""
    import urllib.error

    gw = TradeServerLiquidityGateway("http://127.0.0.1:1", timeout_s=2.0)
    with pytest.raises(HedgeStateUnknown) as ei:
        await gw.send_order(buy(), gateway_id="MT5")
    assert ei.value.hedge_state_unknown is True


@pytest.mark.asyncio
async def test_the_orchestrator_predicate_recognises_it():
    """M11 keys off the attribute, not the class - prove the contract holds."""
    from application.services.execution_orchestrator import _hedge_state_unknown

    assert _hedge_state_unknown(HedgeStateUnknown("x")) is True
    assert _hedge_state_unknown(TradeServerReject("y", retcode=10014)) is False
    assert _hedge_state_unknown(RuntimeError("z")) is False


# ------------------------------------------------------------------ construction

def test_a_missing_url_refuses_to_construct():
    with pytest.raises(ValueError):
        TradeServerLiquidityGateway("")


def test_a_non_http_url_refuses_to_construct():
    with pytest.raises(ValueError):
        TradeServerLiquidityGateway("wss://tunnel.example/ws/marketdata")


def test_the_env_builder_reuses_the_ws_origin(monkeypatch):
    from infrastructure.gateways.trade_server_gateway import (
        build_trade_server_gateway_from_env,
    )

    monkeypatch.delenv("TRADE_SERVER_API_URL", raising=False)
    monkeypatch.setenv("TRADE_SERVER_WS_URL", "wss://tunnel.example/ws/marketdata")
    gw = build_trade_server_gateway_from_env()
    assert gw.base_url == "https://tunnel.example"


def test_the_env_builder_refuses_with_no_url_at_all(monkeypatch):
    from infrastructure.gateways.trade_server_gateway import (
        build_trade_server_gateway_from_env,
    )

    monkeypatch.delenv("TRADE_SERVER_API_URL", raising=False)
    monkeypatch.delenv("TRADE_SERVER_WS_URL", raising=False)
    with pytest.raises(RuntimeError) as ei:
        build_trade_server_gateway_from_env()
    assert "TRADE_SERVER_API_URL" in str(ei.value)


@pytest.mark.asyncio
async def test_get_quotes_does_not_hit_the_rest_api_or_invent_a_price():
    """Quotes come off the market-data socket, never derived from `spread`.

    trade-server's REST /api/v1/symbols returns symbol SPECS with bid/ask absent,
    so a gateway that "computed" a price from the spread would be a second,
    disagreeing price source. With no socket configured this returns empty and
    says why - it does not guess. (`cli sync` sets TRADE_SERVER_WS_URL and gets
    real prices; that path is covered by the live proof.)
    """
    async def transport(method, path, payload):
        raise AssertionError("get_quotes must not call the REST API")

    gw = gateway(transport)
    gw.base_url = "https://tunnel.example"          # not a ws origin
    import os
    os.environ.pop("TRADE_SERVER_WS_URL", None)
    assert await gw.get_quotes(["BTCUSD"]) == {}


def test_the_ws_url_is_derived_from_an_http_base():
    """Both endpoints live on the same box, so one variable can configure them."""
    gw = TradeServerLiquidityGateway("https://tunnel.example")
    import os
    os.environ.pop("TRADE_SERVER_WS_URL", None)
    assert gw._ws_url() == "wss://tunnel.example/ws/marketdata"


def test_an_explicit_ws_url_wins_over_the_derivation(monkeypatch):
    gw = TradeServerLiquidityGateway("https://tunnel.example")
    monkeypatch.setenv("TRADE_SERVER_WS_URL", "wss://other.example/ws/marketdata")
    assert gw._ws_url() == "wss://other.example/ws/marketdata"


@pytest.mark.asyncio
async def test_no_symbols_requested_means_no_socket_opened():
    async def transport(method, path, payload):
        raise AssertionError("an empty request must not connect")

    assert await gateway(transport).get_quotes([]) == {}


@pytest.mark.asyncio
async def test_cancel_confirms_only_on_a_real_success():
    async def transport(method, path, payload):
        assert path == "/api/v1/cancel-order"
        assert payload == {"ticket": "5300001"}
        return (200, {"status": "success", "data": {"success": True}})

    assert await gateway(transport).cancel_order("5300001", "MT5") is True


@pytest.mark.asyncio
async def test_positions_reads_the_terminal_book():
    async def transport(method, path, payload):
        assert method == "GET" and path == "/api/v1/positions"
        return (200, {"status": "success", "data": [{"symbol": "BTCUSD", "volume": 0.01}]})

    got = await gateway(transport).positions()
    assert got[0]["symbol"] == "BTCUSD"
