"""D1: margin_level reaches the routing table as the REAL number, not a stale 0.

Before the fix, `accounts.margin_level` was a persisted column that the fill path
never wrote. `SmartOrderRouter` handed it to the MT5 routing context, and because
it was `Decimal('0')` rather than `None`, M8's "missing context => the condition
does not match" guard did not engage: `RouteCondition.MARGIN_LEVEL` (2001) ran a
real comparison against zero.

Concretely, a rule "reject if MARGIN_LEVEL < 20000" rejected EVERY order, and a
rule "send to dealers if MARGIN_LEVEL < 500" ALWAYS fired - silent flow diversion,
the exact failure mode M8's honesty rule was written to prevent. Stop-out itself
was unaffected (it reads the freshly computed MarginSnapshot), which is why 422
tests passed with the column sitting at 0.

These tests run the REAL stack: CreateOrderHandler -> risk -> SmartOrderRouter
(MT5 layer) -> orchestrator -> fill -> record_deal.
"""
from decimal import Decimal

import pytest

from application.commands.create_order import CreateOrderCommand
from core.domains.accounts.account import MARGIN_LEVEL_UNLIMITED
from core.domains.execution.models import CoverageAccount
from core.domains.execution.routing_mt5 import (
    ConditionRule,
    Mt5RouteCondition,
    Mt5RouteRule,
    RouteAction,
    RouteCondition,
    RouteRequest,
)
from core.domains.market_data.margin import margin_level as compute_margin_level
from core.domains.oms.enums import OrderState, OrderType
from tests.integration.trading_harness import (
    DEFAULT_LOGIN,
    build_harness,
)

BID = Decimal("1.10000")
ASK = Decimal("1.10010")
ALL_REQUESTS = int(RouteRequest.ALL)

# Chosen so that a FLAT account (sentinel 999999) does not satisfy it and a
# MARGINED account (~9000%) does. The first test asserts the real level is below
# it, so the assumption fails loudly rather than mysteriously if leverage changes.
THRESHOLD = Decimal("20000")


def coverage():
    return [CoverageAccount(account_id="DEFAULT_COVERAGE", name="c", currency="USD",
                            nop_limit=Decimal("100"))]


def margin_level_rule(action, threshold, *, name="level-guard", reason="margin level guard"):
    """One rule: apply `action` when MARGIN_LEVEL < `threshold`."""
    return Mt5RouteRule(
        name=name, mode=1, request_mask=ALL_REQUESTS, type_mask=255, flags=0,
        action=int(action), action_value_int=0, action_value_uint=0,
        action_value_float=Decimal("0"), action_value_string=reason,
        conditions=(
            Mt5RouteCondition(code=int(RouteCondition.GROUP),
                              rule=int(ConditionRule.EQ), value_string="*"),
            Mt5RouteCondition(code=int(RouteCondition.MARGIN_LEVEL),
                              rule=int(ConditionRule.LESS), value_float=threshold),
        ),
        dealers=(), position=0,
    )


async def buy(h, **kw):
    payload = dict(account_login=DEFAULT_LOGIN, symbol="EURUSD",
                   order_type=OrderType.BUY, volume=Decimal("0.10"))
    payload.update(kw)
    return await h.stack.create_order_handler.handle(CreateOrderCommand(**payload))


async def test_a_flat_account_routes_on_the_sentinel_not_on_zero():
    """No margin in use => MARGIN_LEVEL_UNLIMITED, so "< 20000" must NOT match.

    With the stale column this was Decimal('0'), 0 < 20000 matched, and the very
    first order a client ever placed was rejected by the routing table.
    """
    h = await build_harness(
        coverage=coverage(),
        mt5_rules=[margin_level_rule(RouteAction.REJECT, THRESHOLD)],
    )
    await h.publish_tick("EURUSD", BID, ASK)

    account = await h.account_repo.find_by_login(DEFAULT_LOGIN)
    assert account.margin_used.amount == Decimal("0")

    order = await buy(h)

    assert order.state == OrderState.FILLED, (
        "a flat account must route on MARGIN_LEVEL_UNLIMITED, not on a stale 0"
    )
    assert len(await h.deal_repo.find_by_account(DEFAULT_LOGIN)) == 1


async def test_the_fill_writes_a_real_margin_level_and_the_next_request_sees_it():
    """The write path (record_deal) and the decision path (router) agree.

    Order 1 fills while flat -> sentinel, guard does not fire.
    The fill then recomputes margin_level from the real equity / margin_used.
    Order 2 is routed against THAT number -> the guard fires with its reason.
    """
    h = await build_harness(
        coverage=coverage(),
        mt5_rules=[margin_level_rule(RouteAction.REJECT, THRESHOLD,
                                     reason="level below 20000 percent")],
    )
    await h.publish_tick("EURUSD", BID, ASK)

    first = await buy(h)
    assert first.state == OrderState.FILLED

    account = await h.account_repo.find_by_login(DEFAULT_LOGIN)
    assert account.margin_used.amount > Decimal("0"), "the fill must reserve margin"

    # D1 core assertion: the stored field is the derived value, not the default 0.
    expected = compute_margin_level(account.equity.amount, account.margin_used.amount)
    assert account.margin_level == expected
    assert account.margin_level != Decimal("0")
    assert account.margin_level != MARGIN_LEVEL_UNLIMITED
    # Documents the threshold choice: a margined account really is below it.
    assert account.margin_level < THRESHOLD, (
        f"test assumption broke: level {account.margin_level} is not below {THRESHOLD}"
    )

    second = await buy(h)

    assert second.state == OrderState.REJECTED
    assert "level below 20000 percent" in (second.comment or "")
    # Only the first order traded: the guard stopped the second before execution.
    assert len(await h.deal_repo.find_by_account(DEFAULT_LOGIN)) == 1
    assert len(await h.position_repo.get_by_account(DEFAULT_LOGIN)) == 1


async def test_a_dealer_diversion_rule_no_longer_fires_on_every_request():
    """The other direction: "< 500" must not match a healthy account.

    With the stale 0 this rule matched every request and parked the whole book in
    a dealer queue nobody services.
    """
    h = await build_harness(
        coverage=coverage(),
        mt5_rules=[margin_level_rule(RouteAction.DEALER, Decimal("500"),
                                     name="escalate-weak-accounts")],
    )
    await h.publish_tick("EURUSD", BID, ASK)

    order = await buy(h)

    assert order.state == OrderState.FILLED
    assert len(await h.deal_repo.find_by_account(DEFAULT_LOGIN)) == 1
