"""
Execution Orchestrator.

The master conductor that receives OrderApprovedEvent and routes it
to the correct execution destination based on the Smart Order Router's decision.

Architectural Purpose:
Orchestrates the flow from approved order to final execution (A-Book, B-Book, ECN, or Dealer).
Acts as the central hub connecting Risk, Routing, and Execution layers.
"""
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
            await self._execute_a_book(order, instruction)
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

    async def _execute_a_book(self, order: Order, instruction: ExecutionInstruction):
        """
        Send to external Liquidity Provider (LP).
        Emits OrderRoutedEvent.
        """
        logger.info(f"Executing order {order.ticket_id} via A-Book gateway {instruction.gateway_id}")

        try:
            # Send to external LP via FIX/REST gateway
            execution_report = await self.liquidity_gateway.send_order(
                order=order,
                gateway_id=instruction.gateway_id
            )

            # Update order state through the state machine, not by assignment: a direct
            # write skips the transition table, so an already-FILLED order could be set
            # back to PLACED and a second fill would then be accepted.
            if order.state is not OrderState.PLACED and not order.is_terminal():
                order.transition_to(OrderState.PLACED)
            await self.order_repo.save(order)

            # Emit success event
            event = DomainEvent(
                event_type=EventType.ORDER_ROUTED,
                aggregate_id=order.ticket_id,
                payload={
                    "order_id": order.ticket_id,
                    "destination": ExecutionDestination.A_BOOK.value,
                    "gateway_id": instruction.gateway_id,
                    "execution_report": execution_report,
                    "stub": bool(isinstance(execution_report, dict) and execution_report.get("stub")),
                }
            )
            await self.event_bus.publish(event)

        except Exception as e:
            logger.error(f"A-Book execution failed for {order.ticket_id}: {e}")
            await self._reject_order(order, f"A-Book gateway error: {str(e)}")

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

    async def _apply_deal_to_account(self, order: Order, fill_price, account) -> Optional[Any]:
        """Record the fill: order state, immutable Deal, Position, account margin.

        Returns the Deal, or None when no recording path is wired - which the caller
        treats as a failure rather than a silent success.
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
            volume=order.volume_initial.value,
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
