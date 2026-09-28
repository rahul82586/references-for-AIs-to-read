"""
M4 Integration Proof: does an order actually execute?

This is the test that answers the milestone question. It drives the WHOLE trading plane
- the same `build_trading_stack()` the API server runs at startup - against in-memory
repositories, and asserts on what a broker would actually care about: the fill price,
the deal, the position, the margin numbers, and whose side of the trade the broker ended
up on.

Every assertion here corresponds to something that was broken. The file doubles as the
regression suite for the twelve defects found while wiring M4; each of those is named in
the test that covers it.

Nothing here needs PostgreSQL, Redis or a network. If this file passes, "install, seed,
start, place an order, hold a position" works on one machine.
"""
from decimal import Decimal

import pytest

from application.commands.create_order import CreateOrderCommand
from core.domains.execution.models import CoverageAccount, ExecutionDestination, RoutingRule
from core.domains.oms.enums import DealType, OrderState, OrderType, PositionAction
from core.events.domain_events import EventType
from tests.integration.trading_harness import (
    DEFAULT_LOGIN,
    build_harness,
    make_account,
    make_eurusd,
    make_group,
    make_usdjpy,
)

#: bid/ask used by most tests: a 1.0 pip spread on EURUSD
BID = Decimal("1.10000")
ASK = Decimal("1.10010")


def coverage(nop_limit: str = "100") -> list:
    return [
        CoverageAccount(
            account_id="DEFAULT_COVERAGE",
            name="Default Coverage",
            currency="USD",
            nop_limit=Decimal(nop_limit),
        )
    ]


async def buy(harness, volume="0.10", symbol="EURUSD", **kwargs):
    return await harness.stack.create_order_handler.handle(
        CreateOrderCommand(
            account_login=kwargs.pop("login", DEFAULT_LOGIN),
            symbol=symbol,
            order_type=OrderType.BUY,
            volume=Decimal(volume),
            **kwargs,
        )
    )


async def sell(harness, volume="0.10", symbol="EURUSD", **kwargs):
    return await harness.stack.create_order_handler.handle(
        CreateOrderCommand(
            account_login=kwargs.pop("login", DEFAULT_LOGIN),
            symbol=symbol,
            order_type=OrderType.SELL,
            volume=Decimal(volume),
            **kwargs,
        )
    )


def event_types(harness) -> list:
    return [
        e.event_type.value if hasattr(e.event_type, "value") else str(e.event_type)
        for e in harness.event_bus.published
    ]


# ===========================================================================
# 1. The happy path, end to end
# ===========================================================================


async def test_market_buy_executes_end_to_end():
    """The M4 question: place an order, end up holding a correctly-margined position."""
    h = await build_harness(coverage=coverage())
    await h.publish_tick("EURUSD", BID, ASK)

    order = await buy(h)

    # --- the order -------------------------------------------------------
    assert order.state == OrderState.FILLED
    # A client BUY is filled at the ASK. Filling at the bid would hand the client the
    # spread and produce a broker that cannot lose money on the crossing.
    assert order.price_order.value == ASK
    assert order.volume_current.value == Decimal("0")

    # --- the deal --------------------------------------------------------
    deals = h.deals_for()
    assert len(deals) == 1
    assert deals[0].deal_type == DealType.BUY
    assert deals[0].volume.value == Decimal("0.10")
    assert deals[0].price.value == ASK

    # --- the position ----------------------------------------------------
    positions = h.open_positions()
    assert len(positions) == 1
    assert positions[0].symbol == "EURUSD"
    assert positions[0].action == PositionAction.BUY
    assert positions[0].volume.value == Decimal("0.10")
    assert positions[0].price_open.value == ASK

    # --- the margin, to the cent ----------------------------------------
    # MT5 stage 1: 0.10 lots * 100,000 / 100 leverage = 100 EUR
    # MT5 stage 2: margin currency EUR -> deposit currency USD at the ASK (a buy deal
    #              converts at the ask, per MT5) = 100 * 1.10010 = 110.01 USD
    # MT5 stage 3: initial_buy rate 1.0 -> unchanged
    account = await h.account()
    assert account.margin_used.amount == Decimal("110.01")
    # Equity is balance + unrealised PnL; bought at the ask and valued at the bid, the
    # client is immediately down the spread: 0.10 * 100,000 * (1.10000 - 1.10010) = -1.00
    assert account.equity.amount == Decimal("9999.00")
    assert account.margin_free.amount == Decimal("9888.99")

    # --- the broker's own exposure --------------------------------------
    # Client BOUGHT, so the broker SOLD: negative delta, broker is short.
    assert h.coverage_exposure("EURUSD") == Decimal("-0.10")


async def test_market_sell_mirrors_the_buy():
    h = await build_harness(coverage=coverage())
    await h.publish_tick("EURUSD", BID, ASK)

    order = await sell(h)

    assert order.state == OrderState.FILLED
    assert order.price_order.value == BID  # a client SELL fills at the BID
    positions = h.open_positions()
    assert positions[0].action == PositionAction.SELL
    # Client SOLD, so the broker BOUGHT: positive delta, broker is long.
    assert h.coverage_exposure("EURUSD") == Decimal("0.10")

    account = await h.account()
    # A sell deal converts margin at the BID: 100 EUR * 1.10000 = 110.00
    assert account.margin_used.amount == Decimal("110.00")


async def test_the_event_chain_runs_in_order():
    """Risk -> Orchestrator -> Deal. Nothing published OrderApproved before M4."""
    h = await build_harness(coverage=coverage())
    await h.publish_tick("EURUSD", BID, ASK)
    await buy(h)

    seen = event_types(h)
    for expected in (
        EventType.ORDER_CREATED.value,
        EventType.ORDER_APPROVED.value,
        EventType.ORDER_ROUTED.value,
        EventType.DEAL_CREATED.value,
        EventType.POSITION_UPDATED.value,
    ):
        assert expected in seen, f"{expected} missing from {seen}"

    # causality, not just presence
    assert seen.index(EventType.ORDER_CREATED.value) < seen.index(EventType.ORDER_APPROVED.value)
    assert seen.index(EventType.ORDER_APPROVED.value) < seen.index(EventType.ORDER_ROUTED.value)
    assert seen.index(EventType.ORDER_ROUTED.value) < seen.index(EventType.DEAL_CREATED.value)

    # the routed event names where it went and why
    routed = [e for e in h.event_bus.published if e.event_type == EventType.ORDER_ROUTED][0]
    assert routed.payload["destination"] == ExecutionDestination.B_BOOK.value


async def test_hedging_mode_opens_one_position_per_deal():
    """demo\\Standard is HEDGING: two buys are two independent positions, margin stacked."""
    h = await build_harness(coverage=coverage())
    await h.publish_tick("EURUSD", BID, ASK)

    await buy(h, "0.10")
    await buy(h, "0.20")

    positions = h.open_positions()
    assert len(positions) == 2
    assert {p.volume.value for p in positions} == {Decimal("0.10"), Decimal("0.20")}
    assert len(h.deals_for()) == 2

    account = await h.account()
    # (0.10 + 0.20) lots * 100,000 / 100 = 300 EUR, converted at the ASK because the
    # position is long (MT5: "the Ask price is used for buy deals"): 300 * 1.10010 = 330.03
    assert account.margin_used.amount == Decimal("330.03")
    assert h.coverage_exposure("EURUSD") == Decimal("-0.30")


# ===========================================================================
# 2. Cross-currency margin (the defect M3 fixed the maths for; M4 proves it is
#    what the trading path actually uses)
# ===========================================================================


async def test_usdjpy_margin_is_not_multiplied_by_the_jpy_price():
    """USDJPY on a USD account: margin is 100.00 USD, NOT 100 * 150 or 100 / 150.

    The old market-order placeholder price of Decimal('1.0'), and the hardcoded 1.0
    conversion rate it sat next to, made this figure wrong by ~150x in one direction or
    the other. USDJPY's margin currency is USD and the account currency is USD, so MT5
    stage 2 is a no-op and the JPY price must not appear anywhere in the requirement.
    """
    h = await build_harness(coverage=coverage())
    # make_usdjpy carries a FIXED spread of 12 points (spread=12), and since M7
    # the matching engine honours it: the client ask is bid + 12 points whatever
    # the feed says. Quoting a 12-point feed keeps this test about the margin
    # conversion it was written for - the fill lands on the raw ask exactly
    # because the feed and the symbol configuration agree.
    await h.publish_tick("USDJPY", Decimal("149.988"), Decimal("150.000"))

    order = await buy(h, "0.10", symbol="USDJPY")
    assert order.state == OrderState.FILLED
    assert order.price_order.value == Decimal("150.000")

    account = await h.account()
    # 0.10 * 100,000 / 100 = 100 USD, no conversion needed
    assert account.margin_used.amount == Decimal("100")
    # PnL is in JPY and must convert: bought at 150.000, bid 149.988, so the client
    # is down 0.10 * 100,000 * 0.012 JPY = 120 JPY, about -0.80 USD at ~149.99
    assert Decimal("-2") < (account.equity.amount - Decimal("10000")) < Decimal("0")


async def test_eurusd_margin_uses_the_ask_for_a_buy_and_the_bid_for_a_sell():
    """The two sides must differ by the spread, or the conversion side was dropped."""
    h_buy = await build_harness(coverage=coverage())
    await h_buy.publish_tick("EURUSD", BID, ASK)
    await buy(h_buy, "1.00")
    buy_margin = (await h_buy.account()).margin_used.amount

    h_sell = await build_harness(coverage=coverage())
    await h_sell.publish_tick("EURUSD", BID, ASK)
    await sell(h_sell, "1.00")
    sell_margin = (await h_sell.account()).margin_used.amount

    # 1.0 lot: 1000 EUR at the ask (1.10010) vs at the bid (1.10000)
    assert buy_margin == Decimal("1100.10")
    assert sell_margin == Decimal("1100.00")
    assert buy_margin > sell_margin


# ===========================================================================
# 3. Rejections must leave nothing behind
# ===========================================================================


async def test_insufficient_margin_rejects_and_books_nothing():
    h = await build_harness(
        accounts=[make_account(group=make_group(), balance=Decimal("100"))],
        coverage=coverage(),
    )
    await h.publish_tick("EURUSD", BID, ASK)

    with pytest.raises(ValueError, match="rejected"):
        await buy(h, "1.00")  # needs ~1,100 USD against a 100 USD balance

    assert h.open_positions() == []
    assert h.deals_for() == []
    assert h.coverage_exposure("EURUSD") == Decimal("0")
    account = await h.account()
    assert account.margin_used.amount == Decimal("0")
    assert account.balance.amount == Decimal("100")  # untouched
    assert EventType.ORDER_REJECTED.value in event_types(h)


async def test_market_order_with_no_quote_is_rejected_not_filled_at_a_guess():
    """No tick, no configured quote -> refuse. Filling at 1.0 or at the client's own
    (absent) price would create a position nobody agreed to."""
    h = await build_harness(coverage=coverage())
    # deliberately no publish_tick

    with pytest.raises(ValueError):
        await buy(h, "0.10")

    assert h.open_positions() == []
    assert h.deals_for() == []
    # the rejection is persisted, so it leaves an audit trail like every other rejection
    order = h.orders()[0]
    assert order.state == OrderState.REJECTED
    assert "no ask price" in order.comment.lower()
    assert EventType.ORDER_REJECTED.value in event_types(h)


async def test_volume_above_the_symbol_maximum_is_rejected():
    h = await build_harness(coverage=coverage())
    await h.publish_tick("EURUSD", BID, ASK)

    with pytest.raises(ValueError):
        await buy(h, "500.00")  # EURUSD volume_max is 100

    assert h.open_positions() == []
    assert h.deals_for() == []


async def test_volume_off_the_step_is_rejected():
    h = await build_harness(coverage=coverage())
    await h.publish_tick("EURUSD", BID, ASK)

    with pytest.raises(ValueError):
        await buy(h, "0.105")  # volume_step is 0.01

    assert h.open_positions() == []


# ===========================================================================
# 4. Pending orders: rest, then activate on a later tick
# ===========================================================================


async def test_buy_limit_rests_until_the_market_reaches_it():
    """Before M4 every pending order was rejected: the orchestrator demanded an
    immediate internal fill for all destinations."""
    h = await build_harness(coverage=coverage())
    await h.publish_tick("EURUSD", BID, ASK)

    order = await h.stack.create_order_handler.handle(
        CreateOrderCommand(
            account_login=DEFAULT_LOGIN,
            symbol="EURUSD",
            order_type=OrderType.BUY_LIMIT,
            volume=Decimal("0.10"),
            price=Decimal("1.09000"),
        )
    )

    # resting, not filled, not rejected
    assert order.state == OrderState.PLACED
    assert h.open_positions() == []
    assert h.deals_for() == []
    assert h.coverage_exposure("EURUSD") == Decimal("0")
    assert h.stack.matching_engine.get_market_state("EURUSD")["resting_orders"] == 1

    routed = [e for e in h.event_bus.published if e.event_type == EventType.ORDER_ROUTED][-1]
    assert routed.payload["status"] == "RESTING_IN_BOOK"

    # ... then the market comes down to it
    await h.publish_tick("EURUSD", Decimal("1.08900"), Decimal("1.08910"))

    assert h.stack.matching_engine.get_market_state("EURUSD")["resting_orders"] == 0
    positions = h.open_positions()
    assert len(positions) == 1
    assert positions[0].price_open.value == Decimal("1.08910")  # the better ask
    assert len(h.deals_for()) == 1
    # the broker's exposure moves when the fill happens, not when the order was placed
    assert h.coverage_exposure("EURUSD") == Decimal("-0.10")


async def test_pending_order_never_activates_above_its_limit():
    h = await build_harness(coverage=coverage())
    await h.publish_tick("EURUSD", BID, ASK)

    await h.stack.create_order_handler.handle(
        CreateOrderCommand(
            account_login=DEFAULT_LOGIN,
            symbol="EURUSD",
            order_type=OrderType.BUY_LIMIT,
            volume=Decimal("0.10"),
            price=Decimal("1.09000"),
        )
    )

    for bid, ask in [("1.09900", "1.09910"), ("1.09500", "1.09510"), ("1.09020", "1.09030")]:
        await h.publish_tick("EURUSD", Decimal(bid), Decimal(ask))
        assert h.open_positions() == [], f"filled at ask {ask}, above the 1.09000 limit"

    assert h.stack.matching_engine.get_market_state("EURUSD")["resting_orders"] == 1


# ===========================================================================
# 5. A-Book routing and the stub gateway
# ===========================================================================


def a_book_rule(gateway="LP_TEST") -> list:
    return [
        RoutingRule(
            rule_id="R-A-BOOK-EUR",
            priority=100,
            destination=ExecutionDestination.A_BOOK,
            symbol_filter="EUR*",
            gateway_id=gateway,
        )
    ]


async def test_a_book_order_is_refused_when_no_lp_is_connected():
    """The dangerous version of a stub gateway is one that reports a fill. In strict mode
    it raises instead, so the order is rejected and the client is not told it is hedged."""
    h = await build_harness(rules=a_book_rule(), coverage=coverage(), lp_strict=True)
    await h.publish_tick("EURUSD", BID, ASK)

    order = await buy(h, "0.10")

    assert order.state == OrderState.REJECTED
    assert h.open_positions() == []
    assert h.deals_for() == []
    # the attempt was made and recorded, so an operator can see what the router did
    assert len(h.stack.liquidity_gateway.sent_orders) == 1
    assert h.stack.liquidity_gateway.sent_orders[0]["gateway_id"] == "LP_TEST"
    assert "liquidity provider" in order.comment.lower()


async def test_a_book_order_is_acknowledged_when_the_stub_is_explicitly_trusted():
    h = await build_harness(rules=a_book_rule(), coverage=coverage(), lp_strict=False)
    await h.publish_tick("EURUSD", BID, ASK)

    order = await buy(h, "0.10")

    assert order.state == OrderState.PLACED  # sent out, no internal position
    assert h.open_positions() == []
    assert h.coverage_exposure("EURUSD") == Decimal("0")  # not internalised
    routed = [e for e in h.event_bus.published if e.event_type == EventType.ORDER_ROUTED][-1]
    assert routed.payload["destination"] == ExecutionDestination.A_BOOK.value
    assert routed.payload["stub"] is True


async def test_routing_rule_is_matched_by_symbol_and_reported():
    h = await build_harness(
        rules=[
            RoutingRule(
                rule_id="R-JPY-DEALER",
                priority=50,
                destination=ExecutionDestination.TO_DEALER,
                symbol_filter="*JPY",
            ),
            RoutingRule(
                rule_id="R-DEFAULT-B",
                priority=10,
                destination=ExecutionDestination.B_BOOK,
            ),
        ],
        coverage=coverage(),
    )
    await h.publish_tick("EURUSD", BID, ASK)
    await h.publish_tick("USDJPY", Decimal("149.990"), Decimal("150.000"))

    await buy(h, "0.10", symbol="EURUSD")
    await buy(h, "0.10", symbol="USDJPY")

    routed = [e for e in h.event_bus.published if e.event_type == EventType.ORDER_ROUTED]
    by_symbol = {e.payload.get("order_id"): e.payload for e in routed}
    destinations = [p["destination"] for p in by_symbol.values()]
    assert ExecutionDestination.B_BOOK.value in destinations
    assert ExecutionDestination.TO_DEALER.value in destinations

    # the JPY order went to the dealer queue and did NOT fill internally
    dealer_orders = list(h.stack.dealer_queue.queue.values())
    assert len(dealer_orders) == 1
    assert dealer_orders[0].symbol == "USDJPY"
    assert len([p for p in h.open_positions() if p.symbol == "USDJPY"]) == 0


async def test_highest_priority_rule_wins():
    h = await build_harness(
        rules=[
            RoutingRule(rule_id="LOW", priority=1, destination=ExecutionDestination.B_BOOK),
            RoutingRule(
                rule_id="HIGH",
                priority=999,
                destination=ExecutionDestination.REJECT,
                symbol_filter="EUR*",
            ),
        ],
        coverage=coverage(),
    )
    await h.publish_tick("EURUSD", BID, ASK)

    order = await buy(h, "0.10")
    assert order.state == OrderState.REJECTED
    assert h.open_positions() == []


# ===========================================================================
# 6. Net Open Position thresholds
# ===========================================================================


async def test_nop_at_85_percent_auto_hedges_to_a_book():
    """0.90 lots against a 1.0 lot NOP limit is 90% - past the 85% auto-hedge trigger.

    The rule says B-Book; the coverage account overrides it. An A-Book rule would never
    reach the threshold check at all, since there is nothing to divert.
    """
    h = await build_harness(
        rules=[
            RoutingRule(
                rule_id="R-B-BOOK-EUR",
                priority=100,
                destination=ExecutionDestination.B_BOOK,
                symbol_filter="EUR*",
                gateway_id="LP_HEDGE",
            )
        ],
        coverage=coverage(nop_limit="1.0"),
        lp_strict=False,
    )
    await h.publish_tick("EURUSD", BID, ASK)

    order = await buy(h, "0.90")

    routed = [e for e in h.event_bus.published if e.event_type == EventType.ORDER_ROUTED]
    hedge = [e for e in routed if "85%" in (e.payload.get("reason") or "")]
    assert hedge, f"no auto-hedge routing event in {[e.payload for e in routed]}"
    assert hedge[0].payload["destination"] == ExecutionDestination.A_BOOK.value
    assert order.state == OrderState.PLACED
    # diverted to the LP, so the broker did NOT internalise it
    assert h.coverage_exposure("EURUSD") == Decimal("0")
    assert h.open_positions() == []


async def test_nop_at_95_percent_blocks_the_order():
    h = await build_harness(coverage=coverage(nop_limit="1.0"))
    await h.publish_tick("EURUSD", BID, ASK)

    order = await buy(h, "0.96")

    assert order.state == OrderState.REJECTED
    assert "95%" in order.comment
    assert h.open_positions() == []
    assert h.coverage_exposure("EURUSD") == Decimal("0")


async def test_nop_below_the_threshold_stays_b_book():
    h = await build_harness(coverage=coverage(nop_limit="10.0"))
    await h.publish_tick("EURUSD", BID, ASK)

    order = await buy(h, "0.90")  # 9% of a 10 lot limit

    assert order.state == OrderState.FILLED
    assert h.coverage_exposure("EURUSD") == Decimal("-0.90")


# ===========================================================================
# 7. Post-fill failures must not un-fill a trade
# ===========================================================================


async def test_coverage_failure_after_a_fill_does_not_reject_the_filled_order():
    """The client holds the position. Rejecting it would leave them holding a position
    the server called rejected - and the state machine refuses that transition anyway."""
    h = await build_harness(coverage=coverage())

    class _BrokenCoverage:
        async def find_by_id(self, account_id, session=None):
            return h.coverage_repo.accounts["DEFAULT_COVERAGE"]

        async def update_exposure(self, account_id, symbol, volume_delta):
            raise RuntimeError("coverage store is down")

    h.stack.orchestrator.coverage_repo = _BrokenCoverage()
    await h.publish_tick("EURUSD", BID, ASK)

    order = await buy(h, "0.10")

    assert order.state == OrderState.FILLED
    assert len(h.open_positions()) == 1
    assert len(h.deals_for()) == 1
    assert EventType.ORDER_REJECTED.value not in event_types(h)


async def test_booking_failure_before_any_deal_still_rejects():
    """The other side of the same rule: if nothing was booked, rejection is honest."""
    h = await build_harness(coverage=coverage())
    await h.publish_tick("EURUSD", BID, ASK)

    h.stack.orchestrator.record_deal_handler = None
    h.stack.orchestrator.position_repo = None  # no way to build one either

    order = await buy(h, "0.10")

    assert order.state == OrderState.REJECTED
    assert h.deals_for() == []
    assert h.coverage_exposure("EURUSD") == Decimal("0")


# ===========================================================================
# 8. The stop-out chain, from a tick all the way to a closed position
# ===========================================================================


async def test_stop_out_liquidates_the_worst_loss_first_and_books_it():
    """Tick -> PnL -> equity -> margin call -> stop out -> LiquidationWorker -> close.

    Two long positions opened a tenth of a cent apart, so they carry almost - but not
    quite - the same loss, and "worst first" is a real decision rather than a coin toss.

    The numbers are worked by hand, because the shape of a stop-out is counter-intuitive:
    closing a position does NOT improve equity (the unrealised loss becomes a realised
    one and moves onto the balance). What improves is the DENOMINATOR - the margin the
    remaining positions need. So recovery is about how much margin is released, and the
    scenario has to be built so that releasing half of it is enough:

      balance 10,000, leverage 1:100, call 50%, stop out 30%, two 3.60-lot longs
      A entered at 1.10000, B entered at 1.10100

      tick 1  bid 1.09100 / ask 1.09110
              losses  A -3,240   B -3,600   equity 3,160
              margin  7,200 EUR * 1.09110 = 7,855.92      level 40.2%
              -> below the 50% call level, above the 30% stop-out: MARGIN CALL only

      tick 2  bid 1.08870 / ask 1.08880
              losses  A -4,068   B -4,428   equity 1,504
              margin  7,200 EUR * 1.08880 = 7,839.36      level 19.2%
              -> below 30%: STOP OUT. B is the worse loss, so B closes first.
              balance 10,000 - 4,428 = 5,572; equity unchanged at 1,504
              margin  3,600 EUR * 1.08880 = 3,919.68      level 38.4% -> recovered
    """
    group = make_group(leverage=100, margin_call=Decimal("50"), stop_out=Decimal("30"))
    h = await build_harness(
        groups=[group],
        symbols=[make_eurusd()],
        accounts=[make_account(group=group, balance=Decimal("10000"))],
        coverage=coverage(),
    )

    # A: the better entry
    await h.publish_tick("EURUSD", Decimal("1.09990"), Decimal("1.10000"))
    await buy(h, "3.60")
    # B: a tenth of a cent worse, so it loses slightly more in any fall
    await h.publish_tick("EURUSD", Decimal("1.10090"), Decimal("1.10100"))
    await buy(h, "3.60")

    opened = h.open_positions()
    assert len(opened) == 2
    better_entry = min(p.price_open.value for p in opened)
    worse_entry = max(p.price_open.value for p in opened)
    assert better_entry == Decimal("1.10000")
    assert worse_entry == Decimal("1.10100")

    # --- tick 1: margin call, and nothing may be closed yet -----------------
    await h.publish_tick("EURUSD", Decimal("1.09100"), Decimal("1.09110"))
    account = await h.account()
    assert Decimal("30") < account.margin_level < Decimal("50"), account.margin_level
    assert EventType.MARGIN_CALL_TRIGGERED.value in event_types(h)
    assert len(h.open_positions()) == 2, "a margin call must not close anything"
    assert EventType.STOP_OUT_INITIATED.value not in event_types(h)

    # --- tick 2: stop out. The MT5 state machine only reaches stop-out FROM a
    # --- margin call, so this second tick is what triggers the liquidation.
    await h.publish_tick("EURUSD", Decimal("1.08870"), Decimal("1.08880"))
    assert EventType.STOP_OUT_INITIATED.value in event_types(h)

    remaining = h.open_positions()
    assert len(remaining) == 1, (
        f"expected only the worst position closed, got {len(remaining)} still open"
    )
    # the survivor is the BETTER entry, i.e. the smaller loss
    assert remaining[0].price_open.value == better_entry
    assert worse_entry not in [p.price_open.value for p in remaining]

    account = await h.account()
    # the realised loss landed on the balance instead of vanishing with the position
    assert account.balance.amount == Decimal("5572"), account.balance.amount
    # and the released margin brought the level back above the 30% stop-out threshold
    assert account.margin_level >= Decimal("30"), account.margin_level
    assert EventType.POSITION_CLOSED.value in event_types(h)

    # a closing deal was written, marked as a stop-out and as an exit
    closing = [d for d in h.deal_repo.deals.values() if d.entry.name == "OUT"]
    assert len(closing) == 1
    assert closing[0].reason.name == "SO"
    assert closing[0].profit.amount == Decimal("-4428")


# ===========================================================================
# 9. Wiring honesty
# ===========================================================================


def test_unwired_container_refuses_to_serve_orders_instead_of_returning_a_mock():
    """`get_create_order_handler` used to hand back a MockOrder with state='FILLED', so
    POST /api/v1/trade/orders returned HTTP 200 and a filled ticket for an order that was
    never risk-checked, priced, persisted or hedged."""
    from api import di_providers

    saved = dict(di_providers._container)
    di_providers._container.clear()
    try:
        with pytest.raises(RuntimeError, match="trading plane is not wired"):
            di_providers.get_create_order_handler()
        with pytest.raises(RuntimeError, match="trading plane is not wired"):
            di_providers.get_close_position_handler()
    finally:
        di_providers._container.clear()
        di_providers._container.update(saved)


async def test_trading_stack_names_the_component_it_is_missing():
    from application.di.trading_setup import build_trading_stack
    from infrastructure.messaging.inprocess_event_bus import InProcessEventBus

    with pytest.raises(KeyError, match="order_repo"):
        await build_trading_stack({"event_bus": InProcessEventBus(), "account_repo": object()})


async def test_real_position_repository_exposes_every_name_the_margin_recalculation_probes():
    """Regression guard for the defect that wrote margin_used = 0 after every deal.

    `_recalculate_account_margin` probes get_positions_by_account, then get_by_account,
    then find_by_account. SqlPositionRepository had only `get_by_account`, so the probe
    fell through to an empty list and recomputed margin over zero positions - against the
    real database, silently, on the write path of every fill.
    """
    from infrastructure.persistence.repositories.position_repository import SqlPositionRepository

    for name in ("get_positions_by_account", "get_by_account", "find_by_account"):
        method = getattr(SqlPositionRepository, name, None)
        assert callable(method), f"SqlPositionRepository is missing {name}"
        # signature inspection, not co_varnames: co_varnames includes a method's LOCAL
        # variables, and these repositories bind `async with ... as session` in the body,
        # so the loose check passed for methods that could not take the argument at all.
        import inspect

        params = inspect.signature(method).parameters
        assert "session" in params or any(
            p.kind is inspect.Parameter.VAR_KEYWORD for p in params.values()
        ), f"{name} must accept a UoW session"


def test_every_imatchingengine_implementation_can_internalise_b_book_flow():
    """The orchestrator calls execute_internal(); no engine had it, so every B-Book order
    died with AttributeError. Anything claiming the port must answer it."""
    from core.ports.interfaces import IMatchingEngine
    from infrastructure.engines.book_matching_engine import BookMatchingEngine

    assert callable(getattr(BookMatchingEngine, "execute_internal", None))
    assert callable(getattr(IMatchingEngine, "execute_internal", None))
    assert isinstance(BookMatchingEngine(), IMatchingEngine)


def test_account_login_exists_on_the_router_path():
    """`router.route()` read `account.login_id`, which Account does not have."""
    from core.domains.accounts.account import Account

    assert hasattr(Account(login=1), "login")
    assert not hasattr(Account(login=1), "login_id")


async def test_client_close_position_handler_executes_and_books_the_loss():
    """M5 regression: a client-initiated close crashed with NameError.

    `ClosePositionHandler` built its closing order with `reason=OrderReason.CLIENT`,
    but `OrderReason` was never imported - every call raised NameError. Nothing
    caught it because the e2e suite only ever closed positions through the
    LiquidationWorker (stop-out), and the HTTP close path was never exercised.
    The ruff F821 gate in CI now catches this class at lint time; this test
    catches it at run time and pins the money behaviour: the realised loss is
    booked to the balance and an OUT deal is written.
    """
    from application.commands.close_position import (
        ClosePositionCommand,
        ClosePositionHandler,
    )
    from core.domains.oms.enums import DealEntry

    h = await build_harness(coverage=coverage())
    await h.publish_tick("EURUSD", BID, ASK)
    await buy(h)

    open_positions = await h.position_repo.get_by_account(DEFAULT_LOGIN)
    assert len(open_positions) == 1
    position = open_positions[0]
    account_before = await h.account_repo.find_by_login(DEFAULT_LOGIN)
    balance_before = account_before.balance.amount

    handler = ClosePositionHandler(
        account_repo=h.account_repo,
        position_repo=h.position_repo,
        order_repo=h.order_repo,
        deal_repo=h.deal_repo,
        event_bus=h.event_bus,
    )
    closed = await handler.handle(
        ClosePositionCommand(
            account_login=DEFAULT_LOGIN,
            position_id=position.position_id,
            price=BID,
        )
    )

    # fully closed and no longer listed as open
    assert closed.time_done is not None
    assert closed.volume.value == Decimal("0")
    assert await h.position_repo.get_by_account(DEFAULT_LOGIN) == []

    # bought at the ASK, closed at the BID: -0.00010 x 0.10 x 100000 = -1.00 USD
    realised = (BID - ASK) * Decimal("0.10") * Decimal("100000")
    account_after = await h.account_repo.find_by_login(DEFAULT_LOGIN)
    assert account_after.balance.amount == balance_before + realised

    # an OUT deal was written alongside the opening IN deal
    deals = await h.deal_repo.find_by_account(DEFAULT_LOGIN)
    assert len(deals) == 2
    out_deals = [d for d in deals if d.entry == DealEntry.OUT]
    assert len(out_deals) == 1
    assert out_deals[0].profit.amount == realised

    # and the close was announced on its own channel (M4 defect-26 class)
    assert "position.closed" in event_types(h)


async def test_positions_query_values_the_open_position_in_the_deposit_currency():
    """M5: /account/positions answered [] while the account held a real position.

    Layer 3 of that defect: the query handler still spoke the PRE-M3 vocabulary
    (pos.side / pos.average_price / pos.id), so every attribute access raised,
    and the route swallowed it into an empty list. Rewritten onto the real
    entity and onto RiskEngine.calculate_position_pnl - the same single source
    of truth the margin loop uses, with currency conversion.
    """
    from application.queries.get_positions import (
        GetPositionsQuery,
        GetPositionsQueryHandler,
    )

    h = await build_harness(coverage=coverage())
    await h.publish_tick("EURUSD", BID, ASK)
    await buy(h)

    handler = GetPositionsQueryHandler(
        position_repo=h.position_repo,
        account_repo=h.account_repo,
        risk_engine=h.stack.risk_engine,
        market_data_engine=h.stack.market_data_engine,
    )
    rows = await handler.handle(GetPositionsQuery(account_login=DEFAULT_LOGIN))

    assert len(rows) == 1
    row = rows[0]
    assert row["side"] == "BUY"
    assert row["symbol"] == "EURUSD"
    assert row["volume"] == Decimal("0.10")
    assert row["average_price"] == ASK
    # bought at the ask, valued at the bid: the spread, and nothing but the spread
    assert row["unrealized_pnl"] == Decimal("-1")
    assert row["position_id"]  # the real id, not ''


async def test_positions_query_refuses_to_report_zero_without_a_valuation_engine():
    """A handler with no RiskEngine must refuse, not report comfortable zeros.

    Reporting unrealized_pnl=0 for a real position is the silent-wrong-number
    class M3/M4 hunted; the refusal names what is missing.
    """
    from application.queries.get_positions import (
        GetPositionsQuery,
        GetPositionsQueryHandler,
    )

    h = await build_harness(coverage=coverage())
    await h.publish_tick("EURUSD", BID, ASK)
    await buy(h)

    handler = GetPositionsQueryHandler(position_repo=h.position_repo)
    with pytest.raises(RuntimeError, match="risk_engine"):
        await handler.handle(GetPositionsQuery(account_login=DEFAULT_LOGIN))
