"""D11 - the client-facing close/modify/cancel routes must really act.

Before this, `api/routers/trade.py` had three routes and only one did anything:

    POST   /orders              real
    PUT    /orders/{id}         returned {"status":"modified"}   and touched nothing
    DELETE /orders/{id}         returned {"status":"cancelled"}  and touched nothing
    (close a position)          did not exist

which is exactly why the live database reads 31 IN deals, 0 OUT deals, 31 open
positions and `deal_close` never set. The report - "only IN deals were visible, no
OUT deal" - was not a broken close. There was no client-facing close to break.

All three handlers already existed and were complete; only the close one was
registered in the DI container, and only the MANAGER endpoint reached it. So the fix
is registration plus routes, and this drives them over HTTP.

The app is built with `create_app(harness.providers)` and `wire_trading=False`, so
FastAPI's own startup assembles the trading stack from the same container the routes
read. That matters: registering handlers into a module-global container while the
repositories live in a separate harness gives every request a handler bound to an
empty world, and each close 404s on a position that demonstrably exists. One world,
or the test proves nothing.
"""
from decimal import Decimal

import pytest
from fastapi.testclient import TestClient

from api.auth.dependencies import get_current_user
from api.di_providers import _container
from core.domains.oms.enums import OrderState, OrderType
from tests.integration.trading_harness import (
    DEFAULT_LOGIN, build_harness, default_coverage,
)

BID = Decimal("1.10000")
ASK = Decimal("1.10010")
#: where the market moves to before a close, so realised PnL is not zero by construction
BID_MOVED = Decimal("1.10050")
ASK_MOVED = Decimal("1.10060")
LIFECYCLE_KEYS = ("close_position_handler", "modify_order_handler", "cancel_order_handler")


class _Principal:
    """Stands in for the authenticated account; `login_id` is what the routes read."""

    def __init__(self, login_id: int = DEFAULT_LOGIN):
        self.login_id = login_id
        self.login = login_id


@pytest.fixture()
def api():
    """A whole in-memory broker behind real HTTP, auth overridden to DEFAULT_LOGIN."""
    import asyncio

    from api.main import create_app

    harness = asyncio.get_event_loop_policy().new_event_loop().run_until_complete(
        build_harness(coverage=default_coverage(), wire_trading=False))

    saved = {k: _container.get(k) for k in LIFECYCLE_KEYS}
    app = create_app(dict(harness.providers))
    app.dependency_overrides[get_current_user] = lambda: _Principal()

    with TestClient(app) as client:
        yield client, harness

    app.dependency_overrides.pop(get_current_user, None)
    for k, v in saved.items():          # the container is process-global
        if v is None:
            _container.pop(k, None)
        else:
            _container[k] = v


def run(client, coro_fn):
    """Await harness/repository calls from sync test code."""
    import asyncio

    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro_fn())
    finally:
        loop.close()


def quote(client, harness):
    """Publish a live EURUSD quote so a market order has a price to fill at."""
    run(client, lambda: harness.publish_tick("EURUSD", BID, ASK))


def open_buy(client, harness, volume="0.10"):
    """A real filled BUY through the real POST /orders route."""
    quote(client, harness)
    r = client.post("/api/v1/trade/orders", json={
        "symbol": "EURUSD", "order_type": "BUY", "volume": volume})
    assert r.status_code == 200, r.text
    return r.json()


def open_position(client, harness, volume="0.10"):
    open_buy(client, harness, volume)
    positions = run(client, lambda: harness.position_repo.get_by_account(DEFAULT_LOGIN))
    assert positions, "the fill must have created a position"
    return positions[-1]


def resting_limit(client, harness, price="1.05000"):
    """A BUY_LIMIT far below market: it rests, so modify and cancel apply to it."""
    quote(client, harness)
    r = client.post("/api/v1/trade/orders", json={
        "symbol": "EURUSD", "order_type": "BUY_LIMIT",
        "volume": "0.10", "price": price})
    assert r.status_code == 200, r.text
    return r.json()


# ------------------------------------------------------------------- close route

def test_client_close_books_the_out_deal(api):
    """The headline defect: the route that never existed now makes the OUT deal."""
    client, harness = api
    position = open_position(client, harness)

    before = run(client, lambda: harness.deal_repo.find_by_account(DEFAULT_LOGIN))
    assert [d.entry.value for d in before] == ["IN"], "starts with the IN deal only"

    r = client.post(f"/api/v1/trade/positions/{position.position_id}/close", json={})
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["fully_closed"] is True
    assert Decimal(body["volume_remaining"]) == Decimal("0")
    assert body["deal_id"], "the response must carry the OUT deal's id"

    after = run(client, lambda: harness.deal_repo.find_by_account(DEFAULT_LOGIN))
    assert sorted(d.entry.value for d in after) == ["IN", "OUT"], (
        f"closing must add an OUT deal; got {[d.entry.value for d in after]}")

    reloaded = run(client, lambda: harness.position_repo.find_by_id(position.position_id))
    assert reloaded.time_done is not None, "the position must be closed"
    assert reloaded.deal_close == body["deal_id"], "and must point at the OUT deal"


def test_client_close_releases_margin_and_leaves_equity_honest(api):
    """D10 must hold through the HTTP path, not only when a worker closes."""
    client, harness = api
    position = open_position(client, harness)

    held = run(client, lambda: harness.account_repo.find_by_login(DEFAULT_LOGIN)).margin_used.amount
    assert held > Decimal("0"), "the open position holds margin"

    r = client.post(f"/api/v1/trade/positions/{position.position_id}/close", json={})
    assert r.status_code == 200, r.text

    after = run(client, lambda: harness.account_repo.find_by_login(DEFAULT_LOGIN))
    assert after.margin_used.amount == Decimal("0"), (
        f"margin stayed at {after.margin_used.amount}; {held} was never released")
    assert after.equity.amount == after.balance.amount, "no unrealised shadow left"


def test_partial_close_leaves_the_remainder_open(api):
    client, harness = api
    position = open_position(client, harness, volume="0.20")

    r = client.post(f"/api/v1/trade/positions/{position.position_id}/close",
                    json={"volume": "0.05"})
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["fully_closed"] is False
    assert Decimal(body["volume_remaining"]) == Decimal("0.15")

    reloaded = run(client, lambda: harness.position_repo.find_by_id(position.position_id))
    assert reloaded.time_done is None, "the remainder must stay open"
    assert reloaded.volume.value == Decimal("0.15")


def test_close_response_reports_the_trade_it_made(api):
    """D12: the close response must describe the close, not read a zeroed position.

    The first version of the route built its body from the Position the handler
    returns - which by then has `volume` 0 and a `price_current` no tick has set -
    so a real close over real HTTP answered::

        volume_closed 0E-8   close_price 0   realized_pnl 0E-8

    while the OUT deal it had just booked carried the true price and PnL. The
    position was closed correctly and the client was told nothing about it: the
    same class as D1/D2, a value computed properly in one place and served stale
    (here: empty) from another. A close is the moment a client learns its result,
    so those three fields are the point of the endpoint.
    """
    client, harness = api
    position = open_position(client, harness, volume="0.10")
    opened_at = Decimal(str(position.price_open.value))

    # move the market, so the close has a PnL that is not zero by construction
    run(client, lambda: harness.publish_tick("EURUSD", BID_MOVED, ASK_MOVED))

    balance_before = run(
        client, lambda: harness.account_repo.find_by_login(DEFAULT_LOGIN)).balance.amount
    r = client.post(f"/api/v1/trade/positions/{position.position_id}/close", json={})
    assert r.status_code == 200, r.text
    body = r.json()

    # a BUY closes at the bid
    assert Decimal(body["close_price"]) == BID_MOVED, (
        f"close_price must be the price actually dealt, got {body['close_price']}")
    assert Decimal(body["volume_closed"]) == Decimal("0.10"), (
        f"volume_closed must be what was closed, got {body['volume_closed']}")

    # 0.10 lots x 100k contract x (1.10050 - 1.10010) = 4.00 USD
    expected = (BID_MOVED - opened_at) * Decimal("0.10") * Decimal("100000")
    assert Decimal(body["realized_pnl"]) == expected, (
        f"realized_pnl {body['realized_pnl']} != {expected}")

    # and it must agree with the two records that are indisputably real
    deals = run(client, lambda: harness.deal_repo.find_by_account(DEFAULT_LOGIN))
    out = [d for d in deals if d.entry.value == "OUT"]
    assert len(out) == 1
    assert out[0].price.value == BID_MOVED, "the OUT deal carries the close price"
    assert Decimal(body["realized_pnl"]) == out[0].profit.amount, (
        "the response and the OUT deal must state the same realised result")

    balance_after = run(
        client, lambda: harness.account_repo.find_by_login(DEFAULT_LOGIN)).balance.amount
    assert balance_after - balance_before == expected, (
        "the balance moved by the amount the response claimed")

    reloaded = run(client, lambda: harness.position_repo.find_by_id(position.position_id))
    assert reloaded.profit.amount == expected, (
        "a fully closed position's profit is its realised result, as in MT5")
    assert reloaded.price_current.value == BID_MOVED, (
        "and its last price is the price it closed at")


def test_partial_close_response_reports_the_leg_it_closed(api):
    """The partial path must not fall back to the remainder's numbers either."""
    client, harness = api
    position = open_position(client, harness, volume="0.20")

    r = client.post(f"/api/v1/trade/positions/{position.position_id}/close",
                    json={"volume": "0.05"})
    assert r.status_code == 200, r.text
    body = r.json()
    assert Decimal(body["volume_closed"]) == Decimal("0.05")
    assert Decimal(body["volume_remaining"]) == Decimal("0.15")
    assert Decimal(body["close_price"]) > Decimal("0"), (
        f"close_price was {body['close_price']}; the client cannot see its fill")


def test_partial_close_response_reports_the_legs_own_result(api):
    """D14: a partial close must report THAT leg, not the position's floating PnL.

    The route read `position.profit`. On a full close D12 made that the realised
    result, so the full path came out right - but a partial close leaves the
    position open and floating, so `position.profit` is the unrealised PnL of the
    REMAINDER. A client closing half of a losing position was told the loss it had
    not realised, and the deal it had just been given carried a different number.
    `deal_id` was empty for the same reason: it read `position.deal_close`, which
    only a FULL close sets, so every partial close looked like it had booked
    nothing. Measured live against Neon: response `realized_pnl -1.0192` /
    `deal_id ""` while the OUT deal said `+0.50` / `29681303-...`.
    """
    client, harness = api
    position = open_position(client, harness, volume="0.20")

    r = client.post(f"/api/v1/trade/positions/{position.position_id}/close",
                    json={"volume": "0.05"})
    assert r.status_code == 200, r.text
    body = r.json()

    deals = run(client, lambda: harness.deal_repo.find_by_account(DEFAULT_LOGIN))
    outs = [d for d in deals if d.entry.value == "OUT"]
    assert len(outs) == 1, f"one OUT deal, got {len(outs)}"
    leg = outs[0]

    assert Decimal(body["volume_closed"]) == Decimal("0.05")
    assert body["deal_id"] == str(leg.deal_id), (
        f"the response must name the deal it booked; got {body['deal_id']!r}")
    assert Decimal(body["realized_pnl"]) == leg.profit.amount, (
        f"response {body['realized_pnl']} != the OUT deal's {leg.profit.amount}: "
        f"the client was told the remainder's floating PnL")
    assert Decimal(body["close_price"]) == leg.price.value, (
        f"response {body['close_price']} != the OUT deal's {leg.price.value}")

    # and the position that is still open keeps its floating figure, unmoved by the
    # leg that closed: writing the realised number there would be the same lie
    reloaded = run(client, lambda: harness.position_repo.find_by_id(position.position_id))
    assert reloaded.time_done is None
    assert reloaded.volume.value == Decimal("0.15")


def test_closing_an_unknown_position_is_404(api):
    client, _ = api
    r = client.post("/api/v1/trade/positions/POS-DOES-NOT-EXIST/close", json={})
    assert r.status_code == 404, r.text


def test_closing_an_already_closed_position_is_refused(api):
    """A second close must not produce a second OUT deal."""
    client, harness = api
    position = open_position(client, harness)
    path = f"/api/v1/trade/positions/{position.position_id}/close"

    assert client.post(path, json={}).status_code == 200
    second = client.post(path, json={})
    assert second.status_code in (400, 404), second.text

    deals = run(client, lambda: harness.deal_repo.find_by_account(DEFAULT_LOGIN))
    outs = [d for d in deals if d.entry.value == "OUT"]
    assert len(outs) == 1, f"exactly one OUT deal, got {len(outs)}"


# --------------------------------------------------------- cancel / modify routes

def test_cancel_really_cancels(api):
    """DELETE used to answer 200 'cancelled' for any id at all."""
    client, harness = api
    order = resting_limit(client, harness)

    r = client.delete(f"/api/v1/trade/orders/{order['ticket_id']}")
    assert r.status_code == 200, r.text
    assert r.json()["order_state"] == OrderState.CANCELLED.value

    reloaded = run(client, lambda: harness.order_repo.find_by_id(order["ticket_id"]))
    assert reloaded.state == OrderState.CANCELLED, "the cancel must be persisted"


def test_cancelling_an_unknown_ticket_is_404_not_a_fake_success(api):
    """The old stub returned 200 here. That was the whole defect."""
    client, _ = api
    r = client.delete("/api/v1/trade/orders/999999")
    assert r.status_code == 404, r.text


def test_modify_persists_the_new_stop(api):
    """PUT used to echo the request back without saving anything."""
    client, harness = api
    order = resting_limit(client, harness)

    r = client.put(f"/api/v1/trade/orders/{order['ticket_id']}",
                   json={"stop_loss": "1.04000"})
    assert r.status_code == 200, r.text
    assert r.json()["stop_loss"] == "1.04000"

    reloaded = run(client, lambda: harness.order_repo.find_by_id(order["ticket_id"]))
    assert reloaded.price_sl.value == Decimal("1.04000"), "must be persisted, not echoed"


def test_modify_with_nothing_to_change_is_400(api):
    client, harness = api
    order = resting_limit(client, harness)
    r = client.put(f"/api/v1/trade/orders/{order['ticket_id']}", json={})
    assert r.status_code == 400, r.text
    assert "nothing to modify" in r.json()["detail"]


# ------------------------------------------------------------------- unwired plane

def test_every_route_is_503_when_the_trading_plane_is_unwired():
    """No handler -> loud 503. Never a hardcoded success body.

    The client must NOT run startup: since D11, startup itself registers all three
    handlers, so entering the TestClient context would wire the very plane this test
    asserts is missing. Transport-level requests against the ASGI app skip the
    lifespan and leave the container exactly as this test set it.
    """
    from httpx import ASGITransport, AsyncClient

    from api.main import create_app

    # Snapshot and clear: the DI container is process-global, so an earlier test may
    # have left handlers registered. This cannot assume a clean start.
    saved = {k: _container.get(k) for k in LIFECYCLE_KEYS}
    for k in LIFECYCLE_KEYS:
        _container.pop(k, None)
    try:
        app = create_app({"database": None})
        app.dependency_overrides[get_current_user] = lambda: _Principal()
        assert all(_container.get(k) is None for k in LIFECYCLE_KEYS)

        async def probe():
            results = []
            async with AsyncClient(transport=ASGITransport(app=app),
                                   base_url="http://test") as client:
                for method, path, kw in [
                    ("POST", "/api/v1/trade/positions/X/close", {"json": {}}),
                    ("DELETE", "/api/v1/trade/orders/X", {}),
                    ("PUT", "/api/v1/trade/orders/X", {"json": {"price": "1.0"}}),
                ]:
                    r = await client.request(method, path, **kw)
                    results.append((method, path, r.status_code, r.text))
            return results

        for method, path, code, text in _run_standalone(probe()):
            assert code == 503, f"{method} {path} -> {code}: {text}"
    finally:
        app.dependency_overrides.pop(get_current_user, None)
        for k, v in saved.items():
            if v is None:
                _container.pop(k, None)
            else:
                _container[k] = v


def _run_standalone(coro):
    """Run a coroutine on a loop of its own, outside any TestClient lifespan."""
    import asyncio

    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()
