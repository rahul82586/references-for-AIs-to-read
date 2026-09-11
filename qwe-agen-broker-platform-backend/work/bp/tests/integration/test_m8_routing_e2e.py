"""M8: the routing table drives the REAL trading stack.

Each test replays a semantics the live export or the guide defines, through
CreateOrderHandler -> risk -> SmartOrderRouter (MT5 layer) -> orchestrator:
reject-with-reason, confirm-client (the live `Auto Execution` rule), clear
SL/TP, delay, dealer with and without the skip-if-offline flag, and the
risk price following the client quote (M7 gap #1 closed).
"""
import time
from dataclasses import replace
from decimal import Decimal

import pytest

from application.commands.create_order import CreateOrderCommand
from core.domains.accounts.value_objects import GroupSymbolOverride
from core.domains.execution.models import CoverageAccount
from core.domains.execution.routing_mt5 import (
    ConditionRule,
    Mt5RouteCondition,
    Mt5RouteDealer,
    Mt5RouteRule,
    RouteAction,
    RouteCondition,
    RouteRequest,
)
from core.domains.instruments.enums import CalculationMode
from core.domains.oms.enums import OrderState, OrderType
from tests.integration.trading_harness import (
    DEFAULT_LOGIN,
    build_harness,
    make_account,
    make_eurusd,
    make_group,
)

BID = Decimal("1.10000")
ASK = Decimal("1.10010")
ALL_REQUESTS = int(RouteRequest.ALL)


def coverage():
    return [CoverageAccount(account_id="DEFAULT_COVERAGE", name="c", currency="USD",
                            nop_limit=Decimal("100"))]


def mt5_rule(name, action, *, group="*", conditions=(), dealers=(), action_int=0,
             action_string="", position=0):
    conds = list(conditions)
    if group is not None:
        conds.append(Mt5RouteCondition(code=int(RouteCondition.GROUP),
                                       rule=int(ConditionRule.EQ), value_string=group))
    return Mt5RouteRule(
        name=name, mode=1, request_mask=ALL_REQUESTS, type_mask=255, flags=0,
        action=int(action), action_value_int=action_int, action_value_uint=0,
        action_value_float=Decimal("0"), action_value_string=action_string,
        conditions=tuple(conds), dealers=tuple(dealers), position=position,
    )


async def buy(h, **kw):
    payload = dict(account_login=DEFAULT_LOGIN, symbol="EURUSD",
                   order_type=OrderType.BUY, volume=Decimal("0.10"))
    payload.update(kw)
    return await h.stack.create_order_handler.handle(CreateOrderCommand(**payload))


def harness_kwargs(mt5_rules, **over):
    base = dict(coverage=coverage(), mt5_rules=mt5_rules)
    base.update(over)
    return base


async def test_reject_rule_stops_the_order_with_the_configured_reason():
    h = await build_harness(**harness_kwargs(
        [mt5_rule("block-demo", RouteAction.REJECT, group="demo\\Standard",
                  action_string="demo trading is closed")]
    ))
    await h.publish_tick("EURUSD", BID, ASK)

    order = await buy(h)

    assert order.state == OrderState.REJECTED
    assert "demo trading is closed" in (order.comment or "")
    assert await h.deal_repo.find_by_account(DEFAULT_LOGIN) == []
    assert await h.position_repo.get_by_account(DEFAULT_LOGIN) == []
    account = await h.account_repo.find_by_login(DEFAULT_LOGIN)
    assert account.balance.amount == Decimal("10000")  # nothing moved


async def test_confirm_client_rule_replays_the_live_auto_execution():
    """The live `Auto Execution` rule: confirm at the requested price == normal
    execution on a market-execution platform. The order must FILL, not park."""
    h = await build_harness(**harness_kwargs(
        [mt5_rule("Auto Execution", RouteAction.CONFIRM_CLIENT, group="*",
                  dealers=(Mt5RouteDealer(1000, "First Admin"),))]
    ))
    await h.publish_tick("EURUSD", BID, ASK)

    order = await buy(h)

    assert order.state == OrderState.FILLED
    assert order.price_order.value == ASK
    assert len(await h.deal_repo.find_by_account(DEFAULT_LOGIN)) == 1


async def test_clear_sltp_strips_the_levels_and_execution_continues():
    h = await build_harness(**harness_kwargs(
        [mt5_rule("strip", RouteAction.CLEAR_SLTP, group="*")]
    ))
    await h.publish_tick("EURUSD", BID, ASK)

    order = await buy(h, stop_loss=Decimal("1.09000"), take_profit=Decimal("1.12000"))

    assert order.state == OrderState.FILLED
    assert order.price_sl is None and order.price_tp is None


async def test_delay_action_holds_the_fill_by_the_configured_milliseconds():
    h = await build_harness(**harness_kwargs(
        [mt5_rule("slow", RouteAction.DELAY_TIME, group="*", action_int=120)]
    ))
    await h.publish_tick("EURUSD", BID, ASK)

    started = time.monotonic()
    order = await buy(h)
    elapsed = time.monotonic() - started

    assert order.state == OrderState.FILLED
    assert elapsed >= 0.10, f"the 120 ms routing delay did not happen (elapsed {elapsed:.3f}s)"


async def test_dealer_rule_with_skip_flag_executes_normally_when_no_dealer_session_exists():
    """The live `dealer` rule carries skip-if-none-online. This build has no
    dealer sessions, so MT5's faithful behaviour is: skip the rule, continue
    down the table - NOT park the client's order in a queue nobody services."""
    h = await build_harness(**harness_kwargs(
        [mt5_rule("dealer", RouteAction.DEALER, group="demo\\Standard", action_int=1,
                  dealers=(Mt5RouteDealer(3, "MetaTrader 5 Gateway clone"),))],
    ))
    await h.publish_tick("EURUSD", BID, ASK)

    order = await buy(h)

    assert order.state == OrderState.FILLED
    assert len(await h.deal_repo.find_by_account(DEFAULT_LOGIN)) == 1


async def test_dealer_rule_without_skip_parks_the_order_with_the_dealer_queue():
    h = await build_harness(**harness_kwargs(
        [mt5_rule("desk", RouteAction.DEALER, group="*", action_int=0,
                  dealers=(Mt5RouteDealer(9, "Dealing Desk"),))]
    ))
    await h.publish_tick("EURUSD", BID, ASK)

    order = await buy(h)

    assert order.state not in (OrderState.FILLED, OrderState.REJECTED)
    assert await h.deal_repo.find_by_account(DEFAULT_LOGIN) == []  # nothing executed
    account = await h.account_repo.find_by_login(DEFAULT_LOGIN)
    assert account.balance.amount == Decimal("10000")


async def test_pre_trade_margin_uses_the_client_price_not_the_raw_feed():
    """M7 gap #1 closed: with a group markup, the risk check must see the price
    the client will actually pay. CFD-mode EURUSD (margin = vol x contract x
    price / leverage, all-USD so no conversion noise): raw ask gives 110.01,
    the 20-point markup gives 110.03 - and 110.03 is what must be reserved."""
    group = make_group()
    group.symbol_overrides = [
        GroupSymbolOverride(symbol_pattern="*", spread_diff=20, spread_diff_balance=0)
    ]
    # CFD_LEVERAGE: margin = vol x contract x price / leverage (plain CFD has
    # no leverage divisor and would need the full 11k notional).
    symbol = replace(
        make_eurusd(), calc_mode=CalculationMode.CFD_LEVERAGE,
        base_currency="USD", quote_currency="USD", margin_currency="USD",
    )
    h = await build_harness(groups=[group], symbols=[symbol],
                            accounts=[make_account(group=group)], coverage=coverage())
    await h.publish_tick("EURUSD", BID, ASK)

    order = await buy(h)
    assert order.state == OrderState.FILLED
    assert order.price_order.value == ASK + Decimal("0.00020")  # the client fill

    account = await h.account_repo.find_by_login(DEFAULT_LOGIN)
    # 0.10 x 100000 x 1.10030 / 100 = 110.03 USD (client price), NOT 110.01 (raw)
    assert account.margin_used.amount == Decimal("110.03")
