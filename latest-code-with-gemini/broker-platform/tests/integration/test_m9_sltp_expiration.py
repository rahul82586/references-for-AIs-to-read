"""M9: server-side SL/TP triggers, order expiration, routing position counts.

Before M9 a position's Stop Loss / Take Profit were decoration: the opening
deal DROPPED the order's SL/TP (nothing carried them onto the position), and
nothing watched ticks to fire them. A client who set a stop had no stop. GTD
expirations were a column nothing read. These tests drive the real stack:
tick event -> SlTpWorker -> ClosePositionHandler (converted realised PnL, M6)
-> deal/order reasons SL/TP -> balance.
"""
from datetime import datetime, timedelta, timezone
from decimal import Decimal

import pytest

from application.commands.create_order import CreateOrderCommand
from application.workers.expiration_worker import ExpirationWorker
from core.domains.execution.models import CoverageAccount
from core.domains.execution.routing_mt5 import (
    ConditionRule,
    Mt5RouteCondition,
    Mt5RouteRule,
    RouteAction,
    RouteCondition,
    RouteRequest,
)
from core.domains.oms.enums import DealReason, OrderReason, OrderState, OrderType
from core.domains.oms.enums import PositionAction
from tests.integration.trading_harness import (
    DEFAULT_LOGIN,
    build_harness,
    make_account,
    make_group,
)

BID = Decimal("1.10000")
ASK = Decimal("1.10010")
CONTRACT = Decimal("100000")


def coverage():
    return [CoverageAccount(account_id="DEFAULT_COVERAGE", name="c", currency="USD",
                            nop_limit=Decimal("100"))]


async def place(h, order_type, volume="0.10", **kw):
    return await h.stack.create_order_handler.handle(
        CreateOrderCommand(account_login=DEFAULT_LOGIN, symbol="EURUSD",
                           order_type=order_type, volume=Decimal(volume), **kw)
    )


def event_types(h):
    return [
        e.event_type.value if hasattr(e.event_type, "value") else str(e.event_type)
        for e in h.event_bus.published
    ]


async def opened_position(h):
    positions = await h.position_repo.get_by_account(DEFAULT_LOGIN)
    assert len(positions) == 1
    return positions[0]


# ---------------------------------------------------------------------------
# SL/TP carry: order -> position
# ---------------------------------------------------------------------------

async def test_opening_deal_carries_sl_tp_onto_the_position():
    h = await build_harness(coverage=coverage())
    await h.publish_tick("EURUSD", BID, ASK)

    await place(h, OrderType.BUY, stop_loss=Decimal("1.09500"), take_profit=Decimal("1.10500"))

    position = await opened_position(h)
    assert position.price_sl is not None and position.price_sl.value == Decimal("1.09500")
    assert position.price_tp is not None and position.price_tp.value == Decimal("1.10500")


# ---------------------------------------------------------------------------
# SL/TP triggers
# ---------------------------------------------------------------------------

async def test_buy_stop_loss_fires_on_the_bid_and_books_the_realised_loss():
    h = await build_harness(coverage=coverage())
    await h.publish_tick("EURUSD", BID, ASK)
    await place(h, OrderType.BUY, stop_loss=Decimal("1.09500"))

    # the bid crosses the stop: close at the MARKET (1.09490), not at the stop level
    await h.publish_tick("EURUSD", Decimal("1.09490"), Decimal("1.09500"))

    assert await h.position_repo.get_by_account(DEFAULT_LOGIN) == []
    account = await h.account_repo.find_by_login(DEFAULT_LOGIN)
    # (1.09490 - 1.10010) x 0.10 x 100000 = -52.00
    assert account.balance.amount == Decimal("10000") - Decimal("52")

    deals = await h.deal_repo.find_by_account(DEFAULT_LOGIN)
    closing = deals[-1]
    assert closing.reason == DealReason.SL
    assert closing.profit.amount == Decimal("-52")

    closing_orders = [o for o in h.order_repo.orders.values()
                      if o.reason == OrderReason.SL]
    assert len(closing_orders) == 1  # the closing order says why, too
    assert "position.closed" in event_types(h)  # PositionClosed, the close-path event


async def test_buy_take_profit_fires_on_the_bid_and_books_the_gain():
    h = await build_harness(coverage=coverage())
    await h.publish_tick("EURUSD", BID, ASK)
    await place(h, OrderType.BUY, take_profit=Decimal("1.10500"))

    await h.publish_tick("EURUSD", Decimal("1.10510"), Decimal("1.10520"))

    account = await h.account_repo.find_by_login(DEFAULT_LOGIN)
    # (1.10510 - 1.10010) x 0.10 x 100000 = +50.00
    assert account.balance.amount == Decimal("10000") + Decimal("50")
    deals = await h.deal_repo.find_by_account(DEFAULT_LOGIN)
    assert deals[-1].reason == DealReason.TP


async def test_sell_stop_loss_fires_on_the_ask():
    h = await build_harness(coverage=coverage())
    await h.publish_tick("EURUSD", BID, ASK)
    await place(h, OrderType.SELL, stop_loss=Decimal("1.10500"))

    # a short's stop is above the market and fires on the ASK
    await h.publish_tick("EURUSD", Decimal("1.10500"), Decimal("1.10510"))

    account = await h.account_repo.find_by_login(DEFAULT_LOGIN)
    # (1.10000 - 1.10510) x 0.10 x 100000 = -51.00  (closed at the market ask)
    assert account.balance.amount == Decimal("10000") - Decimal("51")
    deals = await h.deal_repo.find_by_account(DEFAULT_LOGIN)
    assert deals[-1].reason == DealReason.SL


async def test_ticks_between_the_levels_fire_nothing():
    h = await build_harness(coverage=coverage())
    await h.publish_tick("EURUSD", BID, ASK)
    await place(h, OrderType.BUY, stop_loss=Decimal("1.09500"), take_profit=Decimal("1.10500"))

    await h.publish_tick("EURUSD", Decimal("1.10200"), Decimal("1.10210"))

    position = await opened_position(h)  # still open
    assert position.price_sl.value == Decimal("1.09500")
    account = await h.account_repo.find_by_login(DEFAULT_LOGIN)
    assert account.balance.amount == Decimal("10000")  # nothing realised


async def test_a_gapped_market_closes_at_the_market_not_at_the_stop_level():
    """The trigger is not a price promise: MT5 closes at the market, and the
    honest realised loss is bigger than the stop level implied."""
    h = await build_harness(coverage=coverage())
    await h.publish_tick("EURUSD", BID, ASK)
    await place(h, OrderType.BUY, stop_loss=Decimal("1.09500"))

    await h.publish_tick("EURUSD", Decimal("1.08000"), Decimal("1.08010"))  # weekend gap

    account = await h.account_repo.find_by_login(DEFAULT_LOGIN)
    # (1.08000 - 1.10010) x 0.10 x 100000 = -201.00, not the -51 the stop implied
    assert account.balance.amount == Decimal("10000") - Decimal("201")


# ---------------------------------------------------------------------------
# Expiration
# ---------------------------------------------------------------------------

async def test_expired_pending_is_cancelled_by_the_sweep():
    h = await build_harness(coverage=coverage())
    await h.publish_tick("EURUSD", BID, ASK)

    past = datetime.now(timezone.utc) - timedelta(minutes=5)
    order = await place(h, OrderType.BUY_LIMIT, price=Decimal("1.05000"), expiration=past)
    assert order.state == OrderState.PLACED  # resting, far below the market

    worker = ExpirationWorker(order_repo=h.order_repo, event_bus=h.event_bus, sweep_seconds=999)
    cancelled = await worker.sweep_once()

    assert cancelled == 1
    stored = await h.order_repo.find_by_id(order.ticket_id)
    assert stored.state == OrderState.CANCELLED
    assert "expired" in (stored.comment or "").lower()
    assert "order.cancelled" in event_types(h)
    assert await h.deal_repo.find_by_account(DEFAULT_LOGIN) == []  # never executed


async def test_unexpired_and_gtc_pendings_survive_the_sweep():
    h = await build_harness(coverage=coverage())
    await h.publish_tick("EURUSD", BID, ASK)

    future = datetime.now(timezone.utc) + timedelta(hours=1)
    gtd = await place(h, OrderType.BUY_LIMIT, price=Decimal("1.05000"), expiration=future)
    gtc = await place(h, OrderType.SELL_LIMIT, price=Decimal("1.15000"))  # no expiration

    worker = ExpirationWorker(order_repo=h.order_repo, event_bus=h.event_bus, sweep_seconds=999)
    assert await worker.sweep_once() == 0
    assert (await h.order_repo.find_by_id(gtd.ticket_id)).state == OrderState.PLACED
    assert (await h.order_repo.find_by_id(gtc.ticket_id)).state == OrderState.PLACED


# ---------------------------------------------------------------------------
# Routing position-count conditions (4005/4006) via the live cache
# ---------------------------------------------------------------------------

async def test_position_count_condition_rejects_the_second_position():
    """POSITION_TOTAL_SYMBOL >= 1: the first buy fills, the DealCreated event
    refreshes the ConfigCache slice, and the second buy is rejected by the
    table - a synchronous counts view, the way the routing engine reads
    everything else."""
    rule = Mt5RouteRule(
        name="one-per-symbol", mode=1, request_mask=int(RouteRequest.ALL), type_mask=255,
        flags=0, action=int(RouteAction.REJECT), action_value_int=0, action_value_uint=0,
        action_value_float=Decimal("0"), action_value_string="max 1 position per symbol",
        conditions=(
            Mt5RouteCondition(code=int(RouteCondition.GROUP), value_string="*"),
            Mt5RouteCondition(code=int(RouteCondition.POSITION_TOTAL_SYMBOL),
                              rule=int(ConditionRule.NOT_LESS), value_int=1),
        ),
        position=0,
    )
    h = await build_harness(coverage=coverage(), mt5_rules=[rule])
    await h.publish_tick("EURUSD", BID, ASK)

    first = await place(h, OrderType.BUY)
    assert first.state == OrderState.FILLED  # count was 0 when it routed

    second = await place(h, OrderType.BUY)
    assert second.state == OrderState.REJECTED
    assert "max 1 position" in (second.comment or "")
    assert len(await h.position_repo.get_by_account(DEFAULT_LOGIN)) == 1


# ---------------------------------------------------------------------------
# Wiring
# ---------------------------------------------------------------------------

async def test_the_stack_registers_the_close_handler_and_sltp_worker():
    """The manager OrderClose endpoint fail-loud-refused before M9 because
    nothing anywhere registered a close handler; the stack does now."""
    from application.commands.close_position import ClosePositionHandler
    from application.workers.sltp_worker import SlTpWorker

    h = await build_harness(coverage=coverage())
    providers = h.providers
    assert isinstance(providers.get("close_position_handler"), ClosePositionHandler)
    assert providers["close_position_handler"].risk_engine is not None  # converted PnL
    assert isinstance(providers.get("sltp_worker"), SlTpWorker)
    assert h.stack.sltp_worker is not None
