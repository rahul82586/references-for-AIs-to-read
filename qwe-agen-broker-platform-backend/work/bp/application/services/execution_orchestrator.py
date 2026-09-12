"""
Execution Orchestrator.

The master conductor that receives OrderApprovedEvent and routes it
to the correct execution destination based on the Smart Order Router's decision.

Architectural Purpose:
Orchestrates the flow from approved order to final execution (A-Book, B-Book, ECN, or Dealer).
Acts as the central hub connecting Risk, Routing, and Execution layers.
"""
import asyncio
import logging
from typing import Any, Optional
from decimal import Decimal

from core.domains.execution.router import SmartOrderRouter
from core.domains.execution.models import (
    ExecutionInstruction,
    ExecutionDestination,
    CoverageAccount
)
from core.domains.oms.entities.order import Order, OrderState
from core.domains.oms.enums import DealType
from core.domains.accounts.models import Account
from core.events.domain_events import DomainEvent, EventType
from core.ports.interfaces import (
    IEventBus,
    IOrderRepository,
    IAccountRepository,
    ILiquidityGateway,
    IMatchingEngine,
    ICoverageAccountRepository
)
from application.services.dealer_queue_service import DealerQueueService
from core.domains.market_data.feed_access import await_tick, tick_ask, tick_bid
from core.domains.pricing.a_book import (
    ABookQuoteError,
    client_fill_price,
    venue_price_for_instruction,
)
from core.domains.market_data.feed_access import await_tick, tick_ask, tick_bid
from core.domains.pricing.a_book import (
    ABookQuoteError,
    client_fill_price,
    venue_price_for_instruction,
)

# M11: the LP report statuses that mean volume actually filled. Anything else
# (ACK, ACK_STUB, NEW) means the order is resting at the LP and nothing may be
# booked.
_LP_FILL_STATUSES = frozenset({"FILLED", "PARTIAL", "PARTIALLY_FILLED"})

#: M13: who keeps the venue's price improvement. "client" (the default) means the
#: broker earns exactly its configured markup and the venue's own movement flows
#: through to the client; "broker" means the client always pays their quoted price.
#: Configurable per deployment now, per group later - the resolution point is
#: _improvement_to_client(), which is the only place this is read.
_IMPROVEMENT_TO_CLIENT = frozenset({"", "client", "true", "1", "yes", "pass_through"})


def _improvement_to_client(account: Any = None) -> bool:
    """Resolve the improvement policy for this fill.

    Reads the account's group first so a per-group override can be added without
    touching any call site, then the environment. An unrecognised environment value
    fails LOUDLY at first use rather than silently defaulting: this setting decides
    who keeps real money, so a typo must not quietly change the answer.
    """
    import os as _os

    group = getattr(account, "group", None)
    override = getattr(group, "abook_improvement", None)
    if override is not None:
        return str(override).strip().lower() in _IMPROVEMENT_TO_CLIENT
    raw = (_os.environ.get("BROKER_ABOOK_IMPROVEMENT") or "").strip().lower()
    if raw and raw not in _IMPROVEMENT_TO_CLIENT and raw not in {"broker", "false", "0", "no"}:
        logger.error(
            "BROKER_ABOOK_IMPROVEMENT=%r is not recognised; using 'client'. Valid "
            "values are 'client' (default: the venue's improvement passes through) "
            "and 'broker' (the client pays their quoted price).", raw,
        )
        return True
    return raw in _IMPROVEMENT_TO_CLIENT



def _hedge_state_unknown(exc: BaseException) -> bool:
    """True when the order reached the LP and its fate there cannot be known.

    Deliberately not an import of FixTimeout: the orchestrator must not depend on
    the FIX adapter to be correct, and a stub-only or REST deployment has no such
    class. The gateway's own exception is recognised by name, and any adapter can
    opt in explicitly by setting `hedge_state_unknown = True` on the exception it
    raises - which is the honest signal, since only the adapter knows whether it
    had already written to the socket.
    """
    if getattr(exc, "hedge_state_unknown", False):
        return True
    return type(exc).__name__ == "FixTimeout"


logger = logging.getLogger(__name__)


class ExecutionOrchestrator:
    """
    The central conductor that receives OrderApprovedEvent and routes it
    to the correct execution destination.

    Flow:
    OrderApprovedEvent → SmartOrderRouter → ExecutionInstruction
        → A_BOOK: ILiquidityGateway.send_order()
        → B_BOOK: IMatchingEngine.fill_internal() + CoverageAccount.update()
        → IN_HOUSE_ECN: IMatchingEngine.submit_to_book()
        → TO_DEALER: DealerQueueService.enqueue()
        → REJECT: Emit OrderRejectedEvent
    """

    def __init__(
        self,
        router: SmartOrderRouter,
        dealer_queue: DealerQueueService,
        liquidity_gateway: ILiquidityGateway,
        matching_engine: IMatchingEngine,
        event_bus: IEventBus,
        order_repo: IOrderRepository,
        account_repo: IAccountRepository,
        coverage_repo: ICoverageAccountRepository,
        position_repo: Optional[Any] = None,
        symbol_repo: Optional[Any] = None,
        market_feed: Optional[Any] = None,
        record_deal_handler: Optional[Any] = None,
        deal_repo: Optional[Any] = None,
        uow_factory: Optional[Any] = None
    ):
        self.router = router
        self.dealer_queue = dealer_queue
        self.liquidity_gateway = liquidity_gateway
        self.matching_engine = matching_engine
        self.event_bus = event_bus
        self.order_repo = order_repo
        self.account_repo = account_repo
        self.coverage_repo = coverage_repo
        self.position_repo = position_repo
        self.symbol_repo = symbol_repo
        self.market_feed = market_feed
        self.record_deal_handler = record_deal_handler
        self.deal_repo = deal_repo
        self.uow_factory = uow_factory
        #: M13: the last A-Book pricing decision, so the booking path can put the
        #: venue price, the client price and the markup on the deal event. Set per
        #: fill; read immediately after, on the same task.
        self._last_a_book_pricing = None

        # One booking path for every internal fill. The engine calls this when an order
        # crosses on submit OR when a resting pending order is activated by a later tick,
        # so a fill that happens minutes after the client's request still reaches the
        # ledger, the position book and the broker's exposure. Without it a pending order
        # activated by the tick pipeline produced a fill nobody recorded.
        register = getattr(matching_engine, "on_fill", None)
        if callable(register):
            register(self._on_internal_fill)

        logger.info("ExecutionOrchestrator initialized")

    async def handle_order_approved(self, event: DomainEvent):
        """
        Main entry point. Subscribes to OrderApprovedEvent on the bus.
        Routes the order based on SOR decision.
        """
        # Risk published the identifier as `ticket_id`; this handler read `order_id`,
        # logged "missing order_id" and returned - the approval and the execution never
        # met. Accept both, since both names are in circulation.
        order_id = event.payload.get('order_id') or event.payload.get('ticket_id') or event.aggregate_id
        if not order_id:
            logger.error("OrderApprovedEvent carries no order identifier: %s", event.payload)
            return

        # Fetch order and account
        order: Optional[Order] = await self.order_repo.find_by_id(order_id)
        if not order:
            logger.error(f"Order {order_id} not found")
            return

        account: Optional[Account] = await self.account_repo.find_by_login(order.account_login)
        if not account:
            logger.error(f"Account {order.account_login} not found")
            return

        # Fetch coverage account for NOP threshold evaluation if available
        coverage_account = None
        if self.coverage_repo:
            try:
                coverage_account = await self.coverage_repo.find_by_id("DEFAULT_COVERAGE")
            except Exception as e:
                logger.debug(f"Could not load coverage account for routing: {e}")

        # Route the order
        instruction = self.router.route(order, account, coverage_account=coverage_account)

        # M8: ACTION_DELAY_TIME from the MT5 routing table. The delay happens
        # AFTER risk approval and BEFORE execution, which is where MT5 places it.
        if getattr(instruction, "delay_ms", 0):
            logger.info(
                "routing rule delays order %s by %d ms before execution",
                order_id, instruction.delay_ms,
            )
            await asyncio.sleep(instruction.delay_ms / 1000.0)
        if getattr(instruction, "delay_ticks", 0):
            logger.warning(
                "routing rule requested a %d-tick delay for order %s; tick delays "
                "are not executable inline and were skipped",
                instruction.delay_ticks, order_id,
            )


        # Emit routing event
        route_event = DomainEvent(
            event_type=EventType.ORDER_ROUTED,
            aggregate_id=order_id,
            payload={
                "order_id": order_id,
                "destination": instruction.destination.value,
                "rule_id": instruction.rule_id,
                "reason": instruction.reason
            }
        )
        await self.event_bus.publish(route_event)

        # Dispatch to appropriate handler
        if instruction.destination == ExecutionDestination.A_BOOK:
            await self._execute_a_book(order, instruction, account)
        elif instruction.destination == ExecutionDestination.B_BOOK:
            await self._execute_b_book(order, instruction, account)
        elif instruction.destination == ExecutionDestination.IN_HOUSE_ECN:
            await self._execute_in_house(order, instruction)
        elif instruction.destination == ExecutionDestination.TO_DEALER:
            await self._send_to_dealer(order)
        elif instruction.destination == ExecutionDestination.REJECT:
            await self._reject_order(order, instruction.reason or "Blocked by routing rule")
        else:
            logger.error(f"Unknown execution destination: {instruction.destination}")

    async def _execute_a_book(self, order: Order, instruction: ExecutionInstruction,
                              account: Optional[Account] = None):
        """Hedge the client's flow at an external LP, then book the client side.

        M11: this used to send the order and publish ORDER_ROUTED, dropping the
        LP's execution report - so an A-Book destination produced no deal, no
        position, no margin move and no reservation release. Every outcome the
        gateway can return is now handled explicitly, and none is guessed.
        """
        gateway_id = instruction.gateway_id
        logger.info(f"Executing order {order.ticket_id} via A-Book gateway {gateway_id}")

        try:
            report = await self.liquidity_gateway.send_order(
                order=order,
                gateway_id=gateway_id,
            )
        except Exception as exc:  # noqa: BLE001 - the gateway's contract is by exception
            if _hedge_state_unknown(exc):
                # The order reached the LP and we cannot say what happened there.
                await self._a_book_hedge_unknown(order, gateway_id, exc)
                return
            # The LP definitively did not take it. Rejecting is honest, and the
            # single rejection funnel releases the margin reservation.
            logger.error(f"A-Book execution failed for {order.ticket_id}: {exc}")
            await self._reject_order(order, f"A-Book gateway error: {exc}")
            return

        if not isinstance(report, dict):
            logger.error(
                "gateway %s returned a non-dict execution report for %s (%r); cannot "
                "book a fill from it", gateway_id, order.ticket_id, type(report).__name__,
            )
            await self._a_book_hedge_unknown(
                order, gateway_id,
                RuntimeError(f"malformed execution report: {type(report).__name__}"),
            )
            return

        status = str(report.get("status") or "").upper()
        if status in _LP_FILL_STATUSES:
            await self._book_a_book_fill(order, report, account, gateway_id)
        else:
            await self._a_book_resting(order, report, gateway_id, status)

    async def _book_a_book_fill(self, order: Order, report: dict,
                                account: Optional[Account], gateway_id: str) -> None:
        """The LP filled (fully or partly): book the client side at the LP's numbers."""
        # ALWAYS re-read the account; never trust the instance the dispatcher
        # handed us. That one was loaded BEFORE risk approval reserved margin, so
        # its margin_reserved is stale - and M6's contract is that the repository
        # owns the stored total while helpers merely SET the in-flight object.
        # Booking against the stale snapshot was observed live on a real MT5 hedge:
        #   * the release helper set a stale total and a later full-row save
        #     resurrected the hold (77.41353 still reserved after the fill);
        #   * the margin recompute ran against a detached account and stored
        #     margin_used = 0 on an account holding an open 0.01 BTC position.
        # _on_internal_fill re-reads for exactly this reason; the A-Book path now
        # matches it. `account` stays in the signature as the fallback for callers
        # with no repository (tests).
        fresh = await self.account_repo.find_by_login(order.account_login)
        if fresh is not None:
            account = fresh
        if account is None:
            # The LP holds a hedge and we cannot find the client. Do NOT reject:
            # that would cancel the client side of a live hedge. Loud, and flagged.
            logger.error(
                "order %s was FILLED at gateway %s but account %s cannot be loaded; "
                "the client side is unbooked and the hedge is live - reconcile manually",
                order.ticket_id, gateway_id, order.account_login,
            )
            await self._publish_a_book_reconciliation(order, gateway_id, report,
                                                      "ACCOUNT_NOT_FOUND")
            return

        flags = []
        venue_price = self._lp_fill_price(order, report, flags)
        fill_volume = self._lp_fill_volume(order, report, flags)
        # M13: the client is booked at their price, not the venue's. The markup the
        # group configures is what the broker earns on hedged flow; before this the
        # venue's price was booked directly and the markup was discarded.
        fill_price = await self._client_fill_price(order, account, venue_price, flags)
        if fill_price is None:
            logger.error(
                "order %s was FILLED at gateway %s but no honest client price could be "
                "derived; the hedge is live and the client side is unbooked",
                order.ticket_id, gateway_id,
            )
            await self._publish_a_book_reconciliation(
                order, gateway_id, report, "CLIENT_PRICE_UNDERIVABLE")
            return
        if fill_volume <= 0:
            logger.error(
                "gateway %s reported status=%s for %s with no usable volume (%r); "
                "nothing booked", gateway_id, report.get("status"), order.ticket_id,
                report.get("volume"),
            )
            await self._publish_a_book_reconciliation(order, gateway_id, report,
                                                      "NO_FILLED_VOLUME")
            return

        try:
            deal = await self._apply_deal_to_account(
                order, fill_price, account, volume=fill_volume
            )
            if deal is None:
                raise RuntimeError(
                    "no deal-recording path is wired: the orchestrator needs either a "
                    "record_deal_handler or a position_repo to build one"
                )
        except Exception as exc:  # noqa: BLE001
            # Same rule as above: the hedge is live, so the client order must not be
            # rejected. This is a break for the back office, not a trading decision.
            logger.error(
                "order %s FILLED at gateway %s but booking the client side failed: %s - "
                "the hedge is live and the client has no position", order.ticket_id,
                gateway_id, exc, exc_info=True,
            )
            await self._publish_a_book_reconciliation(order, gateway_id, report,
                                                      "BOOKING_FAILED")
            return

        # --- Coverage. A REAL hedge means the broker passed the risk on, so its net
        # --- exposure is unchanged and the coverage account must NOT move; moving it
        # --- would double-count risk the broker no longer holds and drive the NOP
        # --- thresholds against a position that does not exist. A `stub` gateway has
        # --- hedged nothing, so the broker kept the client's risk - economically a
        # --- B-Book fill - and coverage moves exactly as B-Book does.
        hedged = not bool(report.get("stub"))
        volume_delta = Decimal("0")
        coverage_updated = False
        coverage_account_id = getattr(order, "coverage_account_id", None) or "DEFAULT_COVERAGE"
        if not hedged:
            logger.warning(
                "order %s booked as A-Book but gateway %s is a STUB - the flow is NOT "
                "hedged, so broker exposure moves as it would for B-Book",
                order.ticket_id, gateway_id,
            )
            is_buy = order.order_type.name.startswith("BUY")
            volume_delta = -fill_volume if is_buy else fill_volume
            if self.coverage_repo is not None:
                try:
                    await self.coverage_repo.update_exposure(
                        account_id=coverage_account_id,
                        symbol=order.symbol,
                        volume_delta=volume_delta,
                    )
                    coverage_updated = True
                except Exception as exc:  # noqa: BLE001
                    logger.error(
                        "order %s booked but coverage exposure could not be updated on "
                        "%s: %s - broker exposure is understated", order.ticket_id,
                        coverage_account_id, exc,
                    )
                    volume_delta = Decimal("0")

        for flag in flags:
            logger.error("order %s filled at gateway %s: %s", order.ticket_id, gateway_id, flag)

        try:
            await self.event_bus.publish(DomainEvent(
                event_type=EventType.DEAL_CREATED,
                aggregate_id=order.ticket_id,
                payload={
                    "order_id": order.ticket_id,
                    "deal_id": deal.deal_id,
                    "deal_type": deal.deal_type.value,
                    "price": str(fill_price),
                    "volume": str(fill_volume),
                    "destination": ExecutionDestination.A_BOOK.value,
                    "gateway_id": gateway_id,
                    "lp_order_id": report.get("order_id"),
                    "hedged": hedged,
                    "coverage_updated": coverage_updated,
                    "coverage_account_id": coverage_account_id,
                    "broker_volume_delta": str(volume_delta),
                    "remaining_volume": str(order.volume_current.value),
                    "reconciliation_flags": list(flags),
                    # M13: the venue's price and the client's are different numbers,
                    # and the gap is the broker's revenue. Both are carried so the
                    # markup is auditable per deal instead of being buried in a fill
                    # price that looks like any other.
                    "venue_price": str(venue_price),
                    "client_price": str(fill_price),
                    "markup_earned": str(
                        getattr(self, "_last_a_book_pricing", None)
                        and self._last_a_book_pricing.markup_earned or Decimal("0")
                    ),
                    "improvement_to_client": bool(
                        getattr(self, "_last_a_book_pricing", None)
                        and self._last_a_book_pricing.improvement_passed_through
                    ),
                },
            ))
        except Exception as exc:  # noqa: BLE001
            logger.error(
                "order %s filled at the LP but the DEAL_CREATED routing event could not "
                "be published: %s", order.ticket_id, exc,
            )

    @staticmethod
    def _lp_fill_price(order: Order, report: dict, flags: list) -> Decimal:
        """The price the VENUE filled at, or the order's own price if it did not say.

        M13: this is no longer the price the CLIENT is booked at - that is derived
        from it by `_client_fill_price`, which applies the group's markup. This
        method answers only "what did the venue charge us".

        A FILLED report with no AvgPx is a malformed report, not a licence to pick
        a number. But the hedge is already live, so refusing to book is worse than
        booking at the order's instruction price and flagging it for the back
        office - which is what this does, loudly.
        """
        raw = report.get("price")
        if raw is not None:
            try:
                price = Decimal(str(raw))
                if price > 0:
                    return price
            except Exception:  # noqa: BLE001
                pass
        flags.append(
            "LP reported a fill with no usable AvgPx; booked at the order's own price "
            "and flagged for reconciliation"
        )
        price_order = getattr(order, "price_order", None)
        value = getattr(price_order, "value", price_order)
        return Decimal(str(value)) if value is not None else Decimal("0")

    async def _client_fill_price(self, order: Order, account: Any, venue_price: Decimal,
                                 flags: list) -> Optional[Decimal]:
        """What the CLIENT is booked at, given what the venue filled at. M13.

        Returns None when it cannot be derived honestly; the caller treats that as a
        reconciliation break rather than falling back to the venue price, because
        booking the client at the raw venue price is the quiet version of the bug
        this fixes - the broker earns nothing and nobody is told.
        """
        symbol_cfg = None
        if self.symbol_repo is not None:
            try:
                symbol_cfg = await self.symbol_repo.find_by_name(order.symbol)
            except Exception as exc:  # noqa: BLE001
                logger.error("cannot load symbol %s to price an A-Book fill: %s",
                             order.symbol, exc)

        raw_bid = raw_ask = None
        tick = await await_tick(self.market_feed, order.symbol) if self.market_feed else None
        if tick is not None:
            raw_bid, raw_ask = tick_bid(tick), tick_ask(tick)

        is_buy = order.order_type.name.startswith("BUY")
        quoted = getattr(getattr(order, "price_order", None), "value", None)

        try:
            priced = client_fill_price(
                venue_price=venue_price,
                raw_bid=(Decimal(str(raw_bid)) if raw_bid is not None else None),
                raw_ask=(Decimal(str(raw_ask)) if raw_ask is not None else None),
                symbol=symbol_cfg,
                group=getattr(account, "group", None),
                side=("BUY" if is_buy else "SELL"),
                quoted_price=(Decimal(str(quoted)) if quoted else None),
                max_slippage_points=(
                    Decimal(str(order.deviation)) if getattr(order, "deviation", None) else None
                ),
                improvement_to_client=_improvement_to_client(account),
            )
        except ABookQuoteError as exc:
            logger.error(
                "cannot derive a client price for A-Book order %s: %s. The hedge is "
                "live at the venue and the client side is NOT booked - this is a "
                "reconciliation break, not a fallback.", order.ticket_id, exc,
            )
            flags.append(f"client price could not be derived: {exc}")
            return None
        except (ArithmeticError, ValueError, TypeError) as exc:
            logger.error(
                "pricing A-Book order %s raised %s: %s - treating as a break rather "
                "than guessing a price", order.ticket_id, type(exc).__name__, exc,
            )
            flags.append(f"client pricing failed: {type(exc).__name__}: {exc}")
            return None

        if priced.capped:
            flags.append(
                f"venue filled at {priced.venue_price} but the client was capped at "
                f"{priced.client_price} (their quote plus allowed slippage); the "
                f"broker absorbs the difference"
            )
        logger.info(
            "A-Book order %s: venue filled %s at %s, client booked at %s "
            "(markup %s, improvement passed to client %s, SpreadDiff %d)",
            order.ticket_id, order.symbol, priced.venue_price, priced.client_price,
            priced.markup_earned, priced.improvement_passed_through, priced.spread_diff,
        )
        self._last_a_book_pricing = priced
        return priced.client_price

    async def _venue_instruction_price(self, order: Order, account: Any) -> Optional[Decimal]:
        """The trigger price to send the venue for a PENDING order. M13.

        Converts the client's marked-up instruction back to source terms, per the
        guide: "The ECN converts the price to the original one 1.15659 and passes it
        to the external system." Without this the venue triggers a markup late, and
        the client's instruction is not honoured.

        Returns None for a market order - there is nothing to convert, and inventing
        a price would turn a market order into a limit order at the venue.
        """
        if order.is_market():
            return None
        client_px = getattr(getattr(order, "price_order", None), "value", None)
        if client_px is None:
            return None
        symbol_cfg = None
        if self.symbol_repo is not None:
            try:
                symbol_cfg = await self.symbol_repo.find_by_name(order.symbol)
            except Exception:  # noqa: BLE001
                symbol_cfg = None
        raw_bid = raw_ask = None
        tick = await await_tick(self.market_feed, order.symbol) if self.market_feed else None
        if tick is not None:
            raw_bid, raw_ask = tick_bid(tick), tick_ask(tick)
        try:
            return venue_price_for_instruction(
                client_instruction_price=Decimal(str(client_px)),
                raw_bid=(Decimal(str(raw_bid)) if raw_bid is not None else None),
                raw_ask=(Decimal(str(raw_ask)) if raw_ask is not None else None),
                symbol=symbol_cfg,
                group=getattr(account, "group", None),
                side=("BUY" if order.order_type.name.startswith("BUY") else "SELL"),
            )
        except (ABookQuoteError, ArithmeticError, ValueError, TypeError) as exc:
            logger.error(
                "cannot convert the instruction price for pending A-Book order %s: %s "
                "- sending the client price unchanged, so the venue trigger will be "
                "offset by the group's markup", order.ticket_id, exc,
            )
            return Decimal(str(client_px))

    @staticmethod
    def _lp_fill_volume(order: Order, report: dict, flags: list) -> Decimal:
        """The volume that actually filled, clamped to what is still outstanding.

        The LP is authoritative about its own fill, but it may not book more than
        the client asked for: an over-report is clamped and flagged rather than
        trusted, because trusting it would create client volume nobody requested.
        """
        remaining = order.volume_current.value
        raw = report.get("volume")
        try:
            filled = Decimal(str(raw)) if raw is not None else remaining
        except Exception:  # noqa: BLE001
            filled = Decimal("0")
        if filled <= 0:
            return Decimal("0")
        if filled > remaining:
            flags.append(
                f"LP reported {filled} filled against {remaining} outstanding; clamped "
                "to the outstanding volume and flagged for reconciliation"
            )
            return remaining
        return filled

    async def _a_book_resting(self, order: Order, report: dict, gateway_id: str,
                              status: str) -> None:
        """The LP acknowledged but has not filled: the order rests there.

        Nothing is booked and the margin reservation is KEPT - the order is still
        live and still needs its hold. This is the A-Book analogue of the B-Book
        RESTING_IN_BOOK path.
        """
        if report.get("stub"):
            logger.warning(
                "STUB gateway %s acknowledged order %s - no external hedge was placed, "
                "so the order is resting at a liquidity provider that does not exist",
                gateway_id, order.ticket_id,
            )
        else:
            logger.info(
                "order %s is resting at gateway %s (LP status %s); it will fill when "
                "the LP reports an execution", order.ticket_id, gateway_id, status,
            )
        try:
            if order.state is not OrderState.PLACED and not order.is_terminal():
                order.transition_to(OrderState.PLACED)
            await self.order_repo.save(order)
        except Exception as exc:  # noqa: BLE001
            logger.error("could not persist order %s as PLACED at the LP: %s",
                         order.ticket_id, exc)
        await self._publish_order_routed(order, gateway_id, report, "RESTING_AT_LP")

    async def _a_book_hedge_unknown(self, order: Order, gateway_id: str,
                                    exc: BaseException) -> None:
        """The order reached the LP and its fate is unknown.

        Neither reject nor book. Rejecting cancels the client side of a hedge that
        may be live; booking creates a client position against a hedge that may
        not be. The order is left exactly as it is, keeps its reservation, and is
        flagged for reconciliation - the only honest outcome, and the one the
        gateway's own FixTimeout message asks for.
        """
        logger.error(
            "order %s was sent to gateway %s and the hedge state is UNKNOWN: %s. The "
            "order is left PLACED with its margin reservation intact; reconcile against "
            "the LP (drop-copy or a status request) before retrying or cancelling.",
            order.ticket_id, gateway_id, exc,
        )
        try:
            if order.state is OrderState.STARTED and not order.is_terminal():
                order.transition_to(OrderState.PLACED)
            await self.order_repo.save(order)
        except Exception as save_exc:  # noqa: BLE001
            logger.error("could not persist order %s in the unknown-hedge state: %s",
                         order.ticket_id, save_exc)
        await self._publish_order_routed(
            order, gateway_id, {"error": str(exc)}, "HEDGE_STATE_UNKNOWN",
            reconciliation_required=True,
        )

    async def _publish_a_book_reconciliation(self, order: Order, gateway_id: str,
                                             report: dict, reason: str) -> None:
        """Publish an ORDER_ROUTED carrying a reconciliation flag for a break."""
        await self._publish_order_routed(
            order, gateway_id, report, "RECONCILIATION_REQUIRED",
            reconciliation_required=True, reconciliation_reason=reason,
        )

    async def _publish_order_routed(self, order: Order, gateway_id: str, report: dict,
                                    status: str, *, reconciliation_required: bool = False,
                                    reconciliation_reason: Optional[str] = None) -> None:
        payload = {
            "order_id": order.ticket_id,
            "destination": ExecutionDestination.A_BOOK.value,
            "gateway_id": gateway_id,
            "status": status,
            "lp_status": report.get("status"),
            "lp_order_id": report.get("order_id"),
            "stub": bool(report.get("stub")),
            "reconciliation_required": reconciliation_required,
        }
        if reconciliation_reason:
            payload["reconciliation_reason"] = reconciliation_reason
        try:
            await self.event_bus.publish(DomainEvent(
                event_type=EventType.ORDER_ROUTED,
                aggregate_id=order.ticket_id,
                payload=payload,
            ))
        except Exception as exc:  # noqa: BLE001
            logger.error("could not publish ORDER_ROUTED (%s) for %s: %s",
                         status, order.ticket_id, exc)

    async def _execute_b_book(self, order: Order, instruction: ExecutionInstruction, account: Account):
        """
        Internalize the trade (broker is counterparty).

        Order of operations matters and is the reason this is not one call:
          1. price the fill from the matching engine (BUY at ask, SELL at bid);
          2. hand the fill to RecordDealHandler, which applies it to the order, writes
             the immutable Deal, opens or nets the Position and recomputes account
             margin through the MT5-accurate engine;
          3. move the broker's own exposure on the coverage account.

        Step 2 used to be skipped in favour of a Deal built here and thrown away - the
        orchestrator constructed a Deal object, passed only its fields to the handler,
        and the handler built a second Deal with a different id. Nothing persisted the
        first, so a B-Book trade produced no deal record of its own and the commission
        it carried came from `account.group.commission`, an attribute that does not
        exist (Group holds `commissions`, a list of rules).

        SIGN CONVENTION (CRITICAL):
        - Client BUY  -> Broker SELL -> volume_delta NEGATIVE (broker is SHORT)
        - Client SELL -> Broker BUY  -> volume_delta POSITIVE (broker is LONG)
        This matches CoverageAccount: positive means the broker is long.
        """
        logger.info(f"Executing order {order.ticket_id} via B-Book (internal)")

        try:
            # submit_order fills an order that crosses the market and rests one that does
            # not. A MARKET order always crosses or raises NoQuoteError; a PENDING order
            # whose price the market has not reached rests in the book and is activated
            # later by on_tick. Both outcomes are correct, and neither may be reported as
            # a rejection - the previous code called execute_internal() for every
            # destination, which raised "the market has not reached its price" and
            # rejected every limit and stop order the platform was ever sent.
            await self.matching_engine.submit_order(order)
        except Exception as e:
            # Nothing has been booked, so rejecting is still honest.
            logger.error(f"B-Book execution failed for {order.ticket_id}: {e}", exc_info=True)
            await self._reject_order(order, f"B-Book internal error: {str(e)}")
            return

        if order.state in (OrderState.FILLED, OrderState.PARTIALLY_FILLED):
            # _on_internal_fill has already booked the deal, the position and the
            # coverage movement - the bus delivers inline, so it ran inside submit_order.
            return

        # Resting in the book. The order stays PLACED and no deal exists yet.
        logger.info(
            "Order %s is resting in the %s book at %s; it will fill when the market "
            "reaches that price",
            order.ticket_id, order.symbol,
            order.price_order.value if order.price_order else None,
        )
        try:
            await self.event_bus.publish(DomainEvent(
                event_type=EventType.ORDER_ROUTED,
                aggregate_id=order.ticket_id,
                payload={
                    "order_id": order.ticket_id,
                    "destination": ExecutionDestination.B_BOOK.value,
                    "status": "RESTING_IN_BOOK",
                    "symbol": order.symbol,
                    "price": str(order.price_order.value) if order.price_order else None,
                },
            ))
        except Exception as e:  # noqa: BLE001
            logger.error("could not publish RESTING_IN_BOOK for %s: %s", order.ticket_id, e)

    async def _on_internal_fill(self, order: Order, fill_price) -> None:
        """Book one internal fill: deal, position, account margin, broker exposure.

        Called by the matching engine, either from submit_order (the order crossed
        immediately) or from on_tick (a resting pending order was activated later). This
        is the ONLY place a B-Book fill is booked, so a fill cannot be recorded twice or
        not at all depending on which path produced it.
        """
        account = await self.account_repo.find_by_login(order.account_login)
        if account is None:
            logger.error(
                "order %s filled at %s but account %s cannot be loaded; the fill is "
                "unbooked and must be reconciled manually",
                order.ticket_id, fill_price, order.account_login,
            )
            return

        deal = None
        coverage_updated = False
        coverage_account_id = getattr(order, "coverage_account_id", None) or "DEFAULT_COVERAGE"

        try:
            deal = await self._apply_deal_to_account(order, fill_price, account)
            if deal is None:
                raise RuntimeError(
                    "no deal-recording path is wired: the orchestrator needs either a "
                    "record_deal_handler or a position_repo to build one"
                )
        except Exception as e:
            # The engine has filled but nothing is booked. There is no position and no
            # deal, so rejecting the order is the honest outcome - the client does not
            # hold anything.
            logger.error(f"booking fill for {order.ticket_id} failed: {e}", exc_info=True)
            await self._reject_order(order, f"B-Book booking error: {str(e)}")
            return

        # --- Past this point the trade IS DONE. The client holds a position and a deal
        # --- exists, so nothing below may reject the order: an order that reaches
        # --- _reject_order in FILLED state hits the state machine's terminal guard and
        # --- raises, leaving the client holding a position the server called rejected.
        try:
            # SIGN CONVENTION (CRITICAL): client BUY -> broker SELL -> NEGATIVE delta;
            # client SELL -> broker BUY -> POSITIVE delta. Positive means broker is long.
            is_buy = order.order_type.name.startswith("BUY")
            volume_delta = -order.volume_initial.value if is_buy else order.volume_initial.value
            if self.coverage_repo is not None:
                await self.coverage_repo.update_exposure(
                    account_id=coverage_account_id,
                    symbol=order.symbol,
                    volume_delta=volume_delta,
                )
                coverage_updated = True
        except Exception as e:
            # The fill stands; the broker's exposure book is now understated. Loud, but
            # not a rejection - rejecting a filled trade does not restore the exposure.
            logger.error(
                "order %s FILLED but coverage exposure for %s could not be updated on "
                "%s: %s - broker exposure is understated and the NOP thresholds will not "
                "see this trade",
                order.ticket_id, order.symbol, coverage_account_id, e,
            )
            volume_delta = Decimal("0")

        try:
            # RecordDealHandler already published DealCreated for the deal itself; this
            # event carries the routing context a downstream hedger needs.
            await self.event_bus.publish(DomainEvent(
                event_type=EventType.DEAL_CREATED,
                aggregate_id=order.ticket_id,
                payload={
                    "order_id": order.ticket_id,
                    "deal_id": deal.deal_id,
                    "deal_type": deal.deal_type.value,
                    "price": str(fill_price.value if hasattr(fill_price, "value") else fill_price),
                    "volume": str(order.volume_initial.value),
                    "destination": ExecutionDestination.B_BOOK.value,
                    "coverage_updated": coverage_updated,
                    "coverage_account_id": coverage_account_id,
                    "broker_volume_delta": str(volume_delta),
                },
            ))
        except Exception as e:  # noqa: BLE001
            logger.error(
                "order %s filled but the DEAL_CREATED routing event could not be "
                "published: %s", order.ticket_id, e,
            )

    async def _apply_deal_to_account(self, order: Order, fill_price, account,
                                   volume: Optional[Decimal] = None) -> Optional[Any]:
        """Record the fill: order state, immutable Deal, Position, account margin.

        Returns the Deal, or None when no recording path is wired - which the caller
        treats as a failure rather than a silent success.

        `volume` defaults to the order's full initial volume, which is what a B-Book
        crossing produces. M11: an LP partial fill passes the volume that actually
        filled, because Order.apply_fill rejects a volume larger than what is still
        outstanding.
        """
        from application.commands.record_deal import RecordDealCommand, RecordDealHandler

        handler = self.record_deal_handler
        if handler is None:
            if self.position_repo is None:
                return None
            handler = RecordDealHandler(
                order_repo=self.order_repo,
                account_repo=self.account_repo,
                position_repo=self.position_repo,
                event_bus=self.event_bus,
                symbol_repo=self.symbol_repo,
                market_feed=self.market_feed,
                deal_repo=self.deal_repo,
                uow_factory=self.uow_factory,
            )

        price = fill_price.value if hasattr(fill_price, "value") else Decimal(str(fill_price))
        cmd = RecordDealCommand(
            order_id=order.ticket_id,
            account_login=order.account_login,
            symbol=order.symbol,
            volume=order.volume_initial.value if volume is None else Decimal(str(volume)),
            price=price,
            deal_type=DealType.BUY if order.order_type.name.startswith("BUY") else DealType.SELL,
            commission_amount=self._commission_for(order, account),
            swap_amount=Decimal("0"),   # accrued by the swap worker, not at fill time
            profit=Decimal("0"),        # realised PnL is booked when the position closes
        )
        return await handler.execute(cmd)

    @staticmethod
    def _commission_for(order: Order, account) -> Decimal:
        """Commission for this fill, from the group's rules.

        Group holds `commissions` (a list of MT5 ConfigGroupCommission rules) and
        exposes calculate_commission(symbol, volume, deal_value), which sums every
        matching rule the way MT5 stacks them. The previous code read
        `account.group.commission.value` - a singular attribute that has never existed -
        so every B-Book fill raised AttributeError before it reached the ledger.
        Zero is returned only when there is genuinely nothing to charge.
        """
        group = getattr(account, "group", None)
        if group is None:
            return Decimal("0")
        calculator = getattr(group, "calculate_commission", None)
        if calculator is None:
            return Decimal("0")
        try:
            volume = order.volume_initial.value
            price = order.price_order.value if order.price_order else Decimal("0")
            deal_value = volume * getattr(order, "contract_size", Decimal("100000")) * price
            return Decimal(str(calculator(order.symbol, volume, deal_value)))
        except Exception as exc:  # noqa: BLE001 - a commission we cannot compute is zero, logged
            logger.error("commission calculation failed for %s: %s", order.ticket_id, exc)
            return Decimal("0")

    async def _execute_in_house(self, order: Order, instruction: ExecutionInstruction):
        """
        Submit to internal CLOB (Central Limit Order Book) for client-vs-client matching.
        """
        logger.info(f"Submitting order {order.ticket_id} to In-House ECN")

        try:
            # The engine fills an order that crosses the market immediately and rests one
            # that does not; _on_internal_fill books whichever happened. Reading the order
            # state afterwards is what tells the two apart - before, the order was stamped
            # PLACED either way, so a fill in the in-house book left the order looking
            # unfilled and produced no deal.
            await self.matching_engine.submit_order(order)

            was_filled = order.state in (OrderState.FILLED, OrderState.PARTIALLY_FILLED)
            resting = self.matching_engine.get_market_state(order.symbol).get("resting_orders", 0)

            if not was_filled and order.state in (OrderState.STARTED, OrderState.NEW):
                order.transition_to(OrderState.PLACED)
            await self.order_repo.save(order)

            event = DomainEvent(
                event_type=EventType.ORDER_ROUTED,
                aggregate_id=order.ticket_id,
                payload={
                    "order_id": order.ticket_id,
                    "destination": ExecutionDestination.IN_HOUSE_ECN.value,
                    "status": "FILLED_IN_HOUSE" if was_filled else "RESTING_IN_BOOK",
                    "resting_orders_in_symbol": resting,
                }
            )
            await self.event_bus.publish(event)

        except Exception as e:
            logger.error(f"In-House ECN submission failed for {order.ticket_id}: {e}")
            await self._reject_order(order, f"ECN error: {str(e)}")

    async def _send_to_dealer(self, order: Order):
        """
        Route to dealer queue for manual confirmation.
        """
        logger.info(f"Sending order {order.ticket_id} to Dealer Queue")

        try:
            await self.dealer_queue.enqueue(order, timeout_seconds=30)

            # State updated in enqueue()
            await self.order_repo.save(order)

        except Exception as e:
            logger.error(f"Dealer queue enrollment failed for {order.ticket_id}: {e}")
            await self._reject_order(order, f"Dealer queue error: {str(e)}")

    async def _reject_order(self, order: Order, reason: str):
        """
        Reject the order and emit OrderRejectedEvent.
        """
        # M6: a rejected order releases its margin reservation - the hold must
        # not outlive the order, or the account loses free margin forever. This
        # is the single rejection funnel (routing block, A-Book refusal, B-Book
        # error, ECN error, dealer error), so one release here covers them all.
        from decimal import Decimal as _Dec

        reserved = _Dec(str(getattr(order, "reserved_margin", 0) or 0))
        if reserved > 0:
            from application.services.margin_reservation import release_margin

            await release_margin(self.account_repo, order.account_login, reserved)
            order.reserved_margin = _Dec("0")
        if not order.is_terminal():
            order.reject(reason)
        await self.order_repo.save(order)

        event = DomainEvent(
            event_type=EventType.ORDER_REJECTED,
            aggregate_id=order.ticket_id,
            payload={
                "order_id": order.ticket_id,
                "reason": reason
            }
        )
        await self.event_bus.publish(event)

        logger.warning(f"Order {order.ticket_id} rejected: {reason}")
