"""
Unit tests for BookMatchingEngine - the pricing rules, in isolation.

These are the rules that decide what price a client actually gets, so each one is
asserted against the MT5 convention rather than against whatever the code happens to do:

  * a client BUY fills at the ASK and a SELL at the BID (the broker keeps the spread);
  * a limit order fills at its limit price OR BETTER, never worse;
  * a stop order fills at the MARKET price once triggered, never at the stop price;
  * an order the market has not reached rests instead of filling;
  * a stop that gaps beyond the slippage tolerance is refused, not filled silently.

No repositories, no bus, no async plumbing beyond the calls themselves.
"""
from decimal import Decimal

import pytest

from core.domains.common.value_objects import Price, Volume
from core.domains.oms.entities.order import Order
from core.domains.oms.enums import OrderState, OrderType
from infrastructure.engines.book_matching_engine import BookMatchingEngine, NoQuoteError


def make_order(
    order_type: OrderType,
    *,
    symbol: str = "EURUSD",
    volume: Decimal = Decimal("0.10"),
    price: Decimal | None = None,
    trigger: Decimal | None = None,
) -> Order:
    return Order(
        account_login=100001,
        symbol=symbol,
        order_type=order_type,
        volume_initial=Volume(volume),
        volume_current=Volume(volume),
        price_order=Price(price) if price else None,
        price_trigger=Price(trigger) if trigger else None,
        state=OrderState.STARTED,
    )


def engine_with(bid: str, ask: str, symbol: str = "EURUSD") -> BookMatchingEngine:
    engine = BookMatchingEngine()
    engine.set_quote(symbol, Decimal(bid), Decimal(ask))
    return engine


# ---------------------------------------------------------------------------
# Market orders: the spread goes to the broker
# ---------------------------------------------------------------------------


async def test_market_buy_fills_at_the_ask():
    engine = engine_with("1.10000", "1.10010")
    price = await engine.execute_internal(make_order(OrderType.BUY))
    assert price.value == Decimal("1.10010")


async def test_market_sell_fills_at_the_bid():
    engine = engine_with("1.10000", "1.10010")
    price = await engine.execute_internal(make_order(OrderType.SELL))
    assert price.value == Decimal("1.10000")


async def test_buy_and_sell_differ_by_exactly_the_spread():
    """If these were equal the broker would be giving the spread away on every trade."""
    engine = engine_with("1.10000", "1.10020")
    buy = await engine.execute_internal(make_order(OrderType.BUY))
    sell = await engine.execute_internal(make_order(OrderType.SELL))
    assert buy.value - sell.value == Decimal("0.00020")


async def test_execute_internal_with_record_false_leaves_the_order_untouched():
    """The orchestrator owns the state transition; the engine must not pre-empt it."""
    engine = engine_with("1.10000", "1.10010")
    order = make_order(OrderType.BUY)
    await engine.execute_internal(order, record=False)
    assert engine.fills == []
    assert order.state == OrderState.STARTED


async def test_execute_internal_with_record_true_logs_the_fill():
    engine = engine_with("1.10000", "1.10010")
    await engine.execute_internal(make_order(OrderType.BUY))
    assert len(engine.fills) == 1
    assert engine.fills[0]["venue"] == "B_BOOK"
    assert engine.fills[0]["price"] == "1.10010"


async def test_no_quote_anywhere_raises_rather_than_inventing_a_price():
    """A fill price the engine made up is a position the client never agreed to."""
    engine = BookMatchingEngine()
    order = make_order(OrderType.BUY)
    order.price_order = None
    with pytest.raises(NoQuoteError):
        await engine.execute_internal(order)


async def test_quote_derives_from_the_order_price_when_no_feed_exists():
    """A seeded server with no feed yet prices off the symbol spread around the request."""
    engine = BookMatchingEngine()
    engine.set_spread("EURUSD", 10, tick_size=Decimal("0.00001"))
    order = make_order(OrderType.BUY, price=Decimal("1.10000"))
    price = await engine.execute_internal(order)
    # mid 1.10000, 10 points of spread -> ask is 5 points above the mid
    assert price.value == Decimal("1.10005")


# ---------------------------------------------------------------------------
# Limit orders: the client's price, or better
# ---------------------------------------------------------------------------


async def test_buy_limit_rests_while_the_ask_is_above_it():
    engine = engine_with("1.10000", "1.10010")
    order = make_order(OrderType.BUY_LIMIT, price=Decimal("1.09000"))
    await engine.submit_order(order)
    assert engine.get_market_state("EURUSD")["resting_orders"] == 1
    assert order.state == OrderState.PLACED
    assert engine.fills == []


async def test_buy_limit_fills_at_the_limit_when_the_ask_is_above_it():
    engine = engine_with("1.09500", "1.09510")
    order = make_order(OrderType.BUY_LIMIT, price=Decimal("1.09000"))
    # ask 1.09510 is still above the 1.09000 limit -> not yet
    assert engine.price_order(order) is None

    engine.set_quote("EURUSD", Decimal("1.08900"), Decimal("1.08910"))
    price = engine.price_order(order)
    # ask 1.08910 is below the limit, so the client gets the BETTER ask
    assert price.value == Decimal("1.08910")


async def test_buy_limit_never_pays_more_than_its_limit():
    engine = engine_with("1.08995", "1.09000")
    order = make_order(OrderType.BUY_LIMIT, price=Decimal("1.09000"))
    assert engine.price_order(order).value == Decimal("1.09000")


async def test_sell_limit_fills_at_the_bid_when_the_market_is_above_it():
    engine = engine_with("1.11000", "1.11010")
    order = make_order(OrderType.SELL_LIMIT, price=Decimal("1.12000"))
    assert engine.price_order(order) is None

    engine.set_quote("EURUSD", Decimal("1.12500"), Decimal("1.12510"))
    # bid 1.12500 is above the 1.12000 limit -> the client gets the better bid
    assert engine.price_order(order).value == Decimal("1.12500")


async def test_sell_limit_never_receives_less_than_its_limit():
    engine = engine_with("1.12000", "1.12010")
    order = make_order(OrderType.SELL_LIMIT, price=Decimal("1.12000"))
    assert engine.price_order(order).value == Decimal("1.12000")


async def test_limit_order_without_a_price_is_refused():
    engine = engine_with("1.10000", "1.10010")
    order = make_order(OrderType.BUY_LIMIT)
    order.price_order = None
    with pytest.raises(ValueError, match="no limit price"):
        engine.price_order(order)


# ---------------------------------------------------------------------------
# Stop orders: the market price, not the stop price
# ---------------------------------------------------------------------------


async def test_buy_stop_rests_below_the_market():
    engine = engine_with("1.10000", "1.10010")
    order = make_order(OrderType.BUY_STOP, trigger=Decimal("1.11000"))
    assert engine.price_order(order) is None


async def test_buy_stop_fills_at_the_market_not_the_stop():
    """This is the point of a stop order: it becomes a market order on trigger."""
    engine = engine_with("1.11020", "1.11030")
    order = make_order(OrderType.BUY_STOP, trigger=Decimal("1.11000"))
    assert engine.price_order(order).value == Decimal("1.11030")


async def test_sell_stop_fills_at_the_market_not_the_stop():
    engine = engine_with("1.08980", "1.08990")
    order = make_order(OrderType.SELL_STOP, trigger=Decimal("1.09000"))
    assert engine.price_order(order).value == Decimal("1.08980")


async def test_stop_that_gaps_past_the_slippage_tolerance_is_refused():
    engine = BookMatchingEngine(max_slippage_points=5)
    engine.set_quote("EURUSD", Decimal("1.12000"), Decimal("1.12010"))
    order = make_order(OrderType.BUY_STOP, trigger=Decimal("1.11000"))
    with pytest.raises(NoQuoteError, match="points beyond its stop"):
        engine.price_order(order)


async def test_stop_within_the_slippage_tolerance_fills():
    engine = BookMatchingEngine(max_slippage_points=50)
    engine.set_quote("EURUSD", Decimal("1.11020"), Decimal("1.11030"))
    order = make_order(OrderType.BUY_STOP, trigger=Decimal("1.11000"))
    assert engine.price_order(order).value == Decimal("1.11030")


# ---------------------------------------------------------------------------
# Book mechanics
# ---------------------------------------------------------------------------


async def test_on_tick_activates_a_resting_limit_order():
    engine = engine_with("1.10000", "1.10010")
    order = make_order(OrderType.BUY_LIMIT, price=Decimal("1.09000"))
    await engine.submit_order(order)
    assert engine.get_market_state("EURUSD")["resting_orders"] == 1

    class _Tick:
        symbol = "EURUSD"
        bid = Decimal("1.08900")
        ask = Decimal("1.08910")

    filled = await engine.on_tick(_Tick())
    assert len(filled) == 1
    assert filled[0][0].ticket_id == order.ticket_id
    assert filled[0][1].value == Decimal("1.08910")
    assert engine.get_market_state("EURUSD")["resting_orders"] == 0


async def test_on_tick_leaves_an_unreached_order_resting():
    engine = engine_with("1.10000", "1.10010")
    order = make_order(OrderType.BUY_LIMIT, price=Decimal("1.09000"))
    await engine.submit_order(order)

    class _Tick:
        symbol = "EURUSD"
        bid = Decimal("1.09800")
        ask = Decimal("1.09810")

    assert await engine.on_tick(_Tick()) == []
    assert engine.get_market_state("EURUSD")["resting_orders"] == 1


async def test_fill_listener_is_called_for_a_resting_order_that_activates():
    engine = engine_with("1.10000", "1.10010")
    seen = []
    engine.on_fill(lambda order, price: seen.append((order.ticket_id, price)))

    order = make_order(OrderType.SELL_LIMIT, price=Decimal("1.12000"))
    await engine.submit_order(order)
    assert seen == []

    class _Tick:
        symbol = "EURUSD"
        bid = Decimal("1.12100")
        ask = Decimal("1.12110")

    await engine.on_tick(_Tick())
    assert seen == [(order.ticket_id, Decimal("1.12100"))]


async def test_cancel_order_removes_a_resting_order():
    engine = engine_with("1.10000", "1.10010")
    order = make_order(OrderType.BUY_LIMIT, price=Decimal("1.09000"))
    await engine.submit_order(order)
    assert await engine.cancel_order(order.ticket_id) is True
    assert engine.get_market_state("EURUSD")["resting_orders"] == 0
    assert await engine.cancel_order(order.ticket_id) is False


async def test_modify_order_is_cancel_replace_so_queue_position_is_lost():
    engine = engine_with("1.10000", "1.10010")
    first = make_order(OrderType.BUY_LIMIT, price=Decimal("1.09000"))
    second = make_order(OrderType.BUY_LIMIT, price=Decimal("1.09100"))
    await engine.submit_order(first)
    await engine.submit_order(second)

    assert await engine.modify_order(first.ticket_id, Decimal("1.09200"), 0) is True
    book = engine._books["EURUSD"]
    # second kept its place; the modified order went to the back of the queue
    assert [o.ticket_id for o in book] == [second.ticket_id, first.ticket_id]
    assert first.price_order.value == Decimal("1.09200")


async def test_market_state_reports_both_sides():
    engine = engine_with("1.10000", "1.10010")
    await engine.submit_order(make_order(OrderType.BUY_LIMIT, price=Decimal("1.09000")))
    await engine.submit_order(make_order(OrderType.SELL_LIMIT, price=Decimal("1.12000"), volume=Decimal("0.20")))

    state = engine.get_market_state("EURUSD")
    assert state["resting_orders"] == 2
    assert state["buy_orders"] == 1
    assert state["sell_orders"] == 1
    assert Decimal(state["total_resting_volume"]) == Decimal("0.30")
    assert state["bid"] == "1.10000"
    assert state["ask"] == "1.10010"


async def test_feed_supplied_tick_wins_over_an_installed_quote():
    class _Feed:
        def get_latest_tick(self, symbol):
            class _T:
                bid = Decimal("1.20000")
                ask = Decimal("1.20010")
            return _T()

    engine = BookMatchingEngine(market_feed=_Feed())
    engine.set_quote("EURUSD", Decimal("1.10000"), Decimal("1.10010"))
    price = await engine.execute_internal(make_order(OrderType.BUY))
    assert price.value == Decimal("1.20010")


async def test_async_feed_is_accepted_too():
    class _Feed:
        async def get_latest_tick(self, symbol):
            class _T:
                bid = Decimal("1.30000")
                ask = Decimal("1.30010")
            return _T()

    engine = BookMatchingEngine(market_feed=_Feed())
    price = await engine.execute_internal(make_order(OrderType.BUY))
    assert price.value == Decimal("1.30010")


async def test_inverted_quote_is_rejected():
    engine = BookMatchingEngine()
    with pytest.raises(ValueError, match="below bid"):
        engine.set_quote("EURUSD", Decimal("1.10010"), Decimal("1.10000"))
