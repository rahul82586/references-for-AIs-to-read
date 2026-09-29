"""M9 proof: SL/TP fire server-side at the market, expiration cancels GTD pendings,
routing reads live position counts. Real stack, real balance effects - no mocks.

Usage:  PYTHONPATH=. python3 scripts/m9_proof_sltp_expiration.py
"""
import asyncio
import os
import sys
from datetime import datetime, timedelta, timezone
from decimal import Decimal

sys.path.insert(0, os.getcwd())

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
from tests.integration.trading_harness import (
    DEFAULT_LOGIN,
    build_harness,
    make_account,
    make_group,
)

BID = Decimal("1.10000")
ASK = Decimal("1.10010")
CHECKS = {"pass": 0, "fail": 0}


def check(name, ok, detail=""):
    CHECKS["pass" if ok else "fail"] += 1
    print(f"[{'PASS' if ok else 'FAIL'}] {name}" + (f" -- {detail}" if detail else ""))
    return ok


def coverage():
    return [CoverageAccount(account_id="DEFAULT_COVERAGE", name="c", currency="USD",
                            nop_limit=Decimal("100"))]


async def place(h, order_type, volume="0.10", **kw):
    return await h.stack.create_order_handler.handle(
        CreateOrderCommand(account_login=DEFAULT_LOGIN, symbol="EURUSD",
                           order_type=order_type, volume=Decimal(volume), **kw)
    )


async def balance(h):
    return (await h.account_repo.find_by_login(DEFAULT_LOGIN)).balance.amount


async def scenario_sltp():
    """SL/TP on a BUY: carry, quiet ticks, then the stop firing at the market."""
    h = await build_harness(coverage=coverage())
    await h.publish_tick("EURUSD", BID, ASK)
    await place(h, OrderType.BUY, stop_loss=Decimal("1.09500"), take_profit=Decimal("1.10500"))

    position = (await h.position_repo.get_by_account(DEFAULT_LOGIN))[0]
    check("SL/TP carried from the order onto the position",
          position.price_sl.value == Decimal("1.09500") and position.price_tp.value == Decimal("1.10500"))

    await h.publish_tick("EURUSD", Decimal("1.10200"), Decimal("1.10210"))
    check("quiet tick inside the corridor fires nothing",
          len(await h.position_repo.get_by_account(DEFAULT_LOGIN)) == 1
          and await balance(h) == Decimal("10000"))

    await h.publish_tick("EURUSD", Decimal("1.09490"), Decimal("1.09500"))  # bid crosses the stop
    deals = await h.deal_repo.find_by_account(DEFAULT_LOGIN)
    bal = await balance(h)
    check("SL fired: position closed at the MARKET bid, not the stop level",
          not await h.position_repo.get_by_account(DEFAULT_LOGIN)
          and bal == Decimal("9948.00"),
          f"balance {bal} = 10000 + (1.09490-1.10010)x0.10x100000 = -52.00")
    check("closing deal is booked with reason SL",
          deals[-1].reason == DealReason.SL and deals[-1].profit.amount == Decimal("-52"))
    check("closing order carries reason SL",
          any(o.reason == OrderReason.SL for o in h.order_repo.orders.values()))


async def scenario_sell_tp():
    """SELL side: the take profit fires on the ASK and books the gain."""
    h = await build_harness(coverage=coverage())
    await h.publish_tick("EURUSD", BID, ASK)
    await place(h, OrderType.SELL, take_profit=Decimal("1.09500"))

    await h.publish_tick("EURUSD", Decimal("1.09490"), Decimal("1.09500"))  # ask touches the TP
    deals = await h.deal_repo.find_by_account(DEFAULT_LOGIN)
    bal = await balance(h)
    check("SELL TP fired on the ask, gain booked in the account currency",
          not await h.position_repo.get_by_account(DEFAULT_LOGIN)
          and bal == Decimal("10000") + Decimal("50")   # closed at ASK: (1.10000-1.09500)x0.10x100000
          and deals[-1].reason == DealReason.TP,
          f"balance {bal}")


async def scenario_gap():
    """Weekend-gap honesty: the trigger is not a price promise."""
    h = await build_harness(coverage=coverage())
    await h.publish_tick("EURUSD", BID, ASK)
    await place(h, OrderType.BUY, stop_loss=Decimal("1.09500"))
    await h.publish_tick("EURUSD", Decimal("1.08000"), Decimal("1.08010"))
    bal = await balance(h)
    check("gapped market closes at the market: loss -201.00, not the -51 the stop implied",
          bal == Decimal("10000") - Decimal("201"), f"balance {bal}")


async def scenario_expiration():
    """GTD pendings die when their time passes; GTC and future-GTD survive."""
    h = await build_harness(coverage=coverage())
    await h.publish_tick("EURUSD", BID, ASK)

    past = datetime.now(timezone.utc) - timedelta(minutes=5)
    expired = await place(h, OrderType.BUY_LIMIT, price=Decimal("1.05000"), expiration=past)
    future = datetime.now(timezone.utc) + timedelta(hours=1)
    alive = await place(h, OrderType.SELL_LIMIT, price=Decimal("1.15000"), expiration=future)
    gtc = await place(h, OrderType.BUY_LIMIT, price=Decimal("1.04000"))
    check("all three pendings are resting PLACED before the sweep",
          expired.state == OrderState.PLACED and alive.state == OrderState.PLACED
          and gtc.state == OrderState.PLACED)

    worker = ExpirationWorker(order_repo=h.order_repo, event_bus=h.event_bus, sweep_seconds=999)
    n = await worker.sweep_once()
    expired_stored = await h.order_repo.find_by_id(expired.ticket_id)
    alive_stored = await h.order_repo.find_by_id(alive.ticket_id)
    gtc_stored = await h.order_repo.find_by_id(gtc.ticket_id)
    check("sweep cancels exactly the expired order (1), leaves future-GTD and GTC resting",
          n == 1 and expired_stored.state == OrderState.CANCELLED
          and alive_stored.state == OrderState.PLACED and gtc_stored.state == OrderState.PLACED,
          f"cancelled={n}, comment='{expired_stored.comment}'")
    types = [e.event_type.value if hasattr(e.event_type, "value") else str(e.event_type)
             for e in h.event_bus.published]
    check("OrderCancelled published for the expired order",
          types.count("order.cancelled") >= 1)
    check("an expired pending never executed: zero deals",
          await h.deal_repo.find_by_account(DEFAULT_LOGIN) == [])


async def scenario_counts():
    """MT5 routing condition 4006 (POSITION_TOTAL_SYMBOL >= 1) against the live
    cache: first order fills, the DealCreated refresh makes the second one match."""
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
    second = await place(h, OrderType.BUY)
    check("first buy fills while the position count is 0", first.state == OrderState.FILLED)
    check("second buy is rejected by POSITION_TOTAL_SYMBOL >= 1 (counts refreshed via events)",
          second.state == OrderState.REJECTED and "max 1 position" in (second.comment or ""),
          f"comment='{second.comment}'")
    check("exactly one position open - the table enforced its limit",
          len(await h.position_repo.get_by_account(DEFAULT_LOGIN)) == 1)


async def main():
    print("=" * 78)
    print("M9 PROOF - server-side SL/TP triggers, expiration, routing position counts")
    print("=" * 78)
    await scenario_sltp()
    await scenario_sell_tp()
    await scenario_gap()
    await scenario_expiration()
    await scenario_counts()
    print("=" * 78)
    print(f"RESULT: {CHECKS['pass']} passed, {CHECKS['fail']} failed")
    return 0 if CHECKS["fail"] == 0 else 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
