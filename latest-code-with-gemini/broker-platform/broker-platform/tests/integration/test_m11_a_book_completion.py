"""M11: an A-Book destination is a complete trade, or an honest failure.

Before M11 `_execute_a_book` sent the order to the LP, set it PLACED, published
ORDER_ROUTED and stopped. The LP's FILLED report was dropped: no deal, no
position, no margin recompute, no reservation release. And a blanket
`except Exception` rejected the client order on a FixTimeout - whose own message
says "hedge state UNKNOWN" - leaving the broker possibly holding a hedge with no
client position against it and no record of either.

Every outcome the gateway can produce is pinned here against the real stack
(CreateOrderHandler -> risk -> router -> orchestrator), with a scripted gateway so
each branch is reachable deterministically.
"""
import asyncio
from decimal import Decimal

import pytest

from application.commands.create_order import CreateOrderCommand
from core.domains.accounts.account import MARGIN_LEVEL_UNLIMITED
from core.domains.common.value_objects import Money, Volume
from core.domains.execution.models import ExecutionDestination, RoutingRule
from core.events.domain_events import DomainEvent, EventType
from core.domains.oms.enums import OrderState, OrderType
from tests.integration.trading_harness import (
    DEFAULT_LOGIN,
    build_harness,
    default_coverage,
)

BID = Decimal("1.10000")
ASK = Decimal("1.10010")
GATEWAY = "TESTLP"


class ScriptedGateway:
    """An ILiquidityGateway that returns whatever the test asks for."""

    def __init__(self, *, report=None, exc=None):
        self._report = report
        self._exc = exc
        self.sent = []

    async def send_order(self, order, gateway_id):
        self.sent.append((order.ticket_id, gateway_id))
        if self._exc is not None:
            raise self._exc
        return dict(self._report)

    async def cancel_order(self, order_id, gateway_id):
        return True

    async def get_quotes(self, symbols):
        return {}


class UnknownHedge(RuntimeError):
    """Stand-in for FixTimeout: the order reached the LP, its fate is unknown.

    The orchestrator must not depend on the FIX adapter to be correct, so it
    recognises this by the explicit `hedge_state_unknown` attribute.
    """
    hedge_state_unknown = True


def a_book_rule():
    return RoutingRule(
        rule_id="a-book-eurusd", priority=100,
        destination=ExecutionDestination.A_BOOK,
        symbol_filter="EURUSD", gateway_id=GATEWAY,
    )


async def harness_with(gateway):
    """A real stack whose A-Book gateway is the scripted one."""
    h = await build_harness(rules=[a_book_rule()], coverage=default_coverage())
    h.stack.orchestrator.liquidity_gateway = gateway
    await h.publish_tick("EURUSD", BID, ASK)
    return h


async def buy(h, volume="0.10"):
    return await h.stack.create_order_handler.handle(CreateOrderCommand(
        account_login=DEFAULT_LOGIN, symbol="EURUSD",
        order_type=OrderType.BUY, volume=Decimal(volume),
    ))


async def collect(h):
    """Subscribe to the events the A-Book leg publishes."""
    seen = {"routed": [], "deals": [], "rejected": []}

    def on(event: DomainEvent):
        if event.event_type == EventType.ORDER_ROUTED:
            seen["routed"].append(event)
        elif event.event_type == EventType.DEAL_CREATED:
            seen["deals"].append(event)
        elif event.event_type == EventType.ORDER_REJECTED:
            seen["rejected"].append(event)

    for et in (EventType.ORDER_ROUTED, EventType.DEAL_CREATED, EventType.ORDER_REJECTED):
        h.event_bus.subscribe(et, on)
    return seen


def filled_report(**over):
    r = {"status": "FILLED", "cl_ord_id": "x", "order_id": "LP-1", "gateway_id": GATEWAY,
         "symbol": "EURUSD", "side": "BUY", "volume": "0.10", "price": "1.10010",
         "stub": False}
    r.update(over)
    return r


# --------------------------------------------------------------- the core ask

@pytest.mark.asyncio
async def test_a_filled_lp_report_books_a_complete_client_trade():
    """The M11 headline: deal, position, margin and reservation release all land."""
    gw = ScriptedGateway(report=filled_report())
    h = await harness_with(gw)
    seen = await collect(h)

    order = await buy(h)

    assert order.state == OrderState.FILLED
    deals = await h.deal_repo.find_by_account(DEFAULT_LOGIN)
    assert len(deals) == 1, "the LP filled but no client deal was booked"
    assert deals[0].price.value == Decimal("1.10010"), "must book at the LP's price"
    assert deals[0].volume.value == Decimal("0.10")

    positions = await h.position_repo.get_by_account(DEFAULT_LOGIN)
    assert len(positions) == 1, "the client must actually hold the position"
    assert positions[0].volume.value == Decimal("0.10")

    account = await h.account_repo.find_by_login(DEFAULT_LOGIN)
    assert account.margin_used.amount > Decimal("0"), "margin was never recomputed"
    assert account.margin_level != Decimal("0")
    # the single source of truth, not a re-derivation in the test
    from core.domains.market_data.margin import margin_level as compute_margin_level
    assert account.margin_level == compute_margin_level(
        account.equity.amount, account.margin_used.amount
    )
    # the M6 hold must not outlive the fill
    assert order.reserved_margin == Decimal("0")
    assert account.margin_reserved.amount == Decimal("0")

    # the DEAL_CREATED routing event carries the hedge context a reconciler needs
    a_book_deals = [e for e in seen["deals"] if e.payload.get("destination") == "A_BOOK"]
    assert a_book_deals, "no A-Book DEAL_CREATED routing event"
    p = a_book_deals[0].payload
    assert p["lp_order_id"] == "LP-1"
    assert p["hedged"] is True
    assert p["gateway_id"] == GATEWAY


@pytest.mark.asyncio
async def test_a_real_hedge_does_not_move_the_coverage_account():
    """The broker passed the risk ON, so its net exposure is unchanged.

    Moving coverage here would double-count risk the broker no longer holds and
    drive the NOP 70/85/95% thresholds against a position that does not exist.
    """
    gw = ScriptedGateway(report=filled_report())
    h = await harness_with(gw)
    await collect(h)

    await buy(h)

    assert h.coverage_exposure("EURUSD") == Decimal("0")
    assert h.coverage_repo.exposure_updates == []


@pytest.mark.asyncio
async def test_a_stub_fill_moves_coverage_because_nothing_was_hedged():
    """`stub: True` means the broker kept the client's risk - economically B-Book.

    Booking it as "hedged" would understate broker exposure, which is the
    dangerous direction, so coverage moves exactly as B-Book does: client BUY ->
    broker SHORT -> negative delta.
    """
    gw = ScriptedGateway(report=filled_report(stub=True, order_id="STUB-1"))
    h = await harness_with(gw)
    seen = await collect(h)

    order = await buy(h)

    assert order.state == OrderState.FILLED
    assert h.coverage_exposure("EURUSD") == Decimal("-0.10"), "unhedged flow must show up"
    a_book_deals = [e for e in seen["deals"] if e.payload.get("destination") == "A_BOOK"]
    assert a_book_deals[0].payload["hedged"] is False
    assert a_book_deals[0].payload["broker_volume_delta"] == "-0.10000000" or \
        Decimal(a_book_deals[0].payload["broker_volume_delta"]) == Decimal("-0.10")


# ------------------------------------------------------------- partial fills

@pytest.mark.asyncio
async def test_a_partial_fill_books_only_what_filled_and_keeps_the_rest_reserved():
    """First partial fill in the codebase: the remainder stays live at the LP."""
    gw = ScriptedGateway(report=filled_report(status="PARTIAL", volume="0.04"))
    h = await harness_with(gw)
    await collect(h)

    order = await buy(h)

    assert order.state == OrderState.PARTIALLY_FILLED
    assert order.volume_current.value == Decimal("0.06"), "0.06 must still be outstanding"
    deals = await h.deal_repo.find_by_account(DEFAULT_LOGIN)
    assert len(deals) == 1
    assert deals[0].volume.value == Decimal("0.04")

    # The reservation is released proportionally: the outstanding 0.06 is still
    # live at the LP and still needs margin. Releasing the whole hold here would
    # leave it reserved by nothing at all.
    assert order.reserved_margin > Decimal("0"), "the remainder lost its reservation"
    account = await h.account_repo.find_by_login(DEFAULT_LOGIN)
    assert account.margin_reserved.amount == order.reserved_margin


# ---------------------------------------------------------------- resting/ACK

@pytest.mark.asyncio
async def test_an_ack_books_nothing_and_keeps_the_reservation():
    """The LP acknowledged but has not filled: the order rests there."""
    gw = ScriptedGateway(report=filled_report(status="ACK", price=None, order_id="LP-9"))
    h = await harness_with(gw)
    seen = await collect(h)

    order = await buy(h)

    assert order.state == OrderState.PLACED
    assert await h.deal_repo.find_by_account(DEFAULT_LOGIN) == []
    assert await h.position_repo.get_by_account(DEFAULT_LOGIN) == []
    assert order.reserved_margin > Decimal("0"), "a live order must keep its hold"
    resting = [e for e in seen["routed"] if e.payload.get("status") == "RESTING_AT_LP"]
    assert resting, "no RESTING_AT_LP event"
    assert resting[0].payload["reconciliation_required"] is False


@pytest.mark.asyncio
async def test_a_stub_ack_says_the_lp_does_not_exist():
    gw = ScriptedGateway(report=filled_report(status="ACK_STUB", stub=True, price=None))
    h = await harness_with(gw)
    seen = await collect(h)

    order = await buy(h)

    assert order.state == OrderState.PLACED
    assert await h.deal_repo.find_by_account(DEFAULT_LOGIN) == []
    resting = [e for e in seen["routed"] if e.payload.get("status") == "RESTING_AT_LP"]
    assert resting and resting[0].payload["stub"] is True


# ------------------------------------------------------- unknown hedge state

@pytest.mark.asyncio
async def test_an_unknown_hedge_is_neither_booked_nor_rejected():
    """The branch that used to reject the client against a possibly-live hedge.

    Rejecting cancels the client side of a hedge that may exist; booking creates a
    client position against a hedge that may not. The only honest outcome is to
    leave the order alone, keep its reservation, and flag it for reconciliation.
    """
    gw = ScriptedGateway(exc=UnknownHedge("no ExecutionReport within 5s"))
    h = await harness_with(gw)
    seen = await collect(h)

    order = await buy(h)

    assert order.state != OrderState.REJECTED, "must not cancel a possibly-live hedge"
    assert order.state == OrderState.PLACED
    assert await h.deal_repo.find_by_account(DEFAULT_LOGIN) == []
    assert await h.position_repo.get_by_account(DEFAULT_LOGIN) == []
    assert order.reserved_margin > Decimal("0"), "the hold must survive until resolved"

    unknown = [e for e in seen["routed"] if e.payload.get("status") == "HEDGE_STATE_UNKNOWN"]
    assert unknown, "no HEDGE_STATE_UNKNOWN event"
    assert unknown[0].payload["reconciliation_required"] is True
    assert seen["rejected"] == []


@pytest.mark.asyncio
async def test_a_definite_lp_rejection_rejects_the_client_and_releases_margin():
    """The LP said no, so the client's order is rejected and its hold released."""
    gw = ScriptedGateway(exc=RuntimeError("LP rejected: insufficient liquidity"))
    h = await harness_with(gw)
    seen = await collect(h)

    order = await buy(h)

    assert order.state == OrderState.REJECTED
    assert "A-Book gateway error" in (order.comment or "")
    assert await h.deal_repo.find_by_account(DEFAULT_LOGIN) == []
    assert order.reserved_margin == Decimal("0")
    account = await h.account_repo.find_by_login(DEFAULT_LOGIN)
    assert account.margin_reserved.amount == Decimal("0")
    assert len(seen["rejected"]) == 1


# ------------------------------------------------- malformed reports, refused

@pytest.mark.asyncio
async def test_a_fill_with_no_price_books_at_the_order_price_and_flags_it():
    """The hedge is live, so refusing to book is worse than booking and flagging."""
    gw = ScriptedGateway(report=filled_report(price=None))
    h = await harness_with(gw)
    seen = await collect(h)

    order = await buy(h)

    assert order.state == OrderState.FILLED
    deals = await h.deal_repo.find_by_account(DEFAULT_LOGIN)
    assert len(deals) == 1
    a_book_deals = [e for e in seen["deals"] if e.payload.get("destination") == "A_BOOK"]
    flags = a_book_deals[0].payload["reconciliation_flags"]
    assert any("AvgPx" in f for f in flags), flags


@pytest.mark.asyncio
async def test_an_lp_over_report_is_clamped_not_trusted():
    """The LP may not create client volume the client never asked for."""
    gw = ScriptedGateway(report=filled_report(volume="0.50"))
    h = await harness_with(gw)
    seen = await collect(h)

    order = await buy(h)

    assert order.state == OrderState.FILLED
    deals = await h.deal_repo.find_by_account(DEFAULT_LOGIN)
    assert deals[0].volume.value == Decimal("0.10"), "must clamp to what was requested"
    a_book_deals = [e for e in seen["deals"] if e.payload.get("destination") == "A_BOOK"]
    flags = a_book_deals[0].payload["reconciliation_flags"]
    assert any("clamped" in f for f in flags), flags


@pytest.mark.asyncio
async def test_a_zero_volume_fill_books_nothing_and_flags_it():
    gw = ScriptedGateway(report=filled_report(volume="0"))
    h = await harness_with(gw)
    seen = await collect(h)

    order = await buy(h)

    assert await h.deal_repo.find_by_account(DEFAULT_LOGIN) == []
    flagged = [e for e in seen["routed"] if e.payload.get("reconciliation_required")]
    assert flagged
    assert flagged[0].payload["reconciliation_reason"] == "NO_FILLED_VOLUME"


@pytest.mark.asyncio
async def test_a_non_dict_report_is_treated_as_unknown_not_as_a_fill():
    class BadGateway(ScriptedGateway):
        async def send_order(self, order, gateway_id):
            return "FILLED"

    h = await harness_with(BadGateway(report=None))
    seen = await collect(h)

    order = await buy(h)

    assert order.state != OrderState.REJECTED
    assert await h.deal_repo.find_by_account(DEFAULT_LOGIN) == []
    assert [e for e in seen["routed"] if e.payload.get("status") == "HEDGE_STATE_UNKNOWN"]


# ------------------------------------- the stale-account bug found live on MT5

@pytest.mark.asyncio
async def test_a_book_booking_re_reads_the_account_before_it_writes_margin():
    """The rule that prevents a defect only a REAL MT5 hedge exposed.

    `_execute_a_book` used to book against the account instance the dispatcher
    loaded BEFORE risk approval reserved margin. Two live hedges on a real
    terminal showed the consequence against PostgreSQL: one account kept
    77.41353 reserved after the fill, the other stored margin_used = 0 while
    holding an open 0.01 BTC position. B-Book was unaffected because
    `_on_internal_fill` has always re-read the account first.

    What is asserted here is the RULE - that the A-Book booking reads the account
    from the repository rather than trusting the instance it was handed. The
    in-memory repository double cannot reproduce the SQL failure itself: its
    `release_margin` mutates the stored object and its `save` stores by reference,
    so a stale snapshot happens to converge on the right answer. Claiming
    otherwise would be a test that passes with the bug present, which is worse
    than no test. The anomaly itself is pinned by
    `scripts/m11_proof_live_hedge.py` against the real terminal and Neon.
    """
    gw = ScriptedGateway(report=filled_report())
    h = await harness_with(gw)
    await collect(h)

    reads = []
    inner = h.account_repo.find_by_login

    async def spying(login, session=None):
        got = await inner(login, session) if "session" in inner.__code__.co_varnames \
            else await inner(login)
        reads.append(login)
        return got

    # A detached snapshot with pre-reservation numbers, handed in deliberately.
    stored = await h.account_repo.find_by_login(DEFAULT_LOGIN)
    from dataclasses import replace as _replace
    stale = _replace(stored)
    stale.margin_reserved = Money(Decimal("0"), stored.currency)

    h.stack.orchestrator.account_repo.find_by_login = spying
    reads.clear()

    from core.domains.oms.entities.order import Order as _Order
    from core.domains.oms.enums import OrderState as _OS
    from core.domains.common.value_objects import Price as _Price, Volume as _Vol

    order = _Order(ticket_id="REREAD-1", account_login=DEFAULT_LOGIN, symbol="EURUSD",
                   order_type=OrderType.BUY, volume_initial=_Vol(Decimal("0.10")),
                   volume_current=_Vol(Decimal("0.10")), price_order=_Price(ASK))
    order.transition_to(_OS.PLACED)
    await h.order_repo.save(order)

    await h.stack.orchestrator._book_a_book_fill(order, filled_report(), stale, GATEWAY)

    assert reads, (
        "_book_a_book_fill wrote margin without reading the account from the "
        "repository - it trusted the caller's snapshot, which is how the live "
        "anomalies happened"
    )
    assert order.state == _OS.FILLED
