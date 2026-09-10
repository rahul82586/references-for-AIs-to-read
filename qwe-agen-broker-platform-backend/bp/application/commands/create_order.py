"""
Create Order Command Handler - The Entry Point for All Trading.

This handler orchestrates the full order lifecycle:
1. Validate symbol (session, trade mode, volume limits)
2. Pre-trade risk check (inside per-account lock)
3. Persist order
4. Execute (B-Book internalization or A-Book routing)
5. Record deal and update position
6. Emit domain events

Architectural Note:
This handler uses TWO-PHASE LOCKING to prevent deadlocks:
- Phase 1: Acquire lock → Check risk → Reserve margin → Release lock
- Phase 2: Execute trade (may involve slow LP network calls)
- Phase 3: Acquire lock → Record deal → Finalize balance → Release lock
"""
import logging
from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal
from typing import Any, Optional

from core.domains.accounts.account import Account
from core.domains.common.value_objects import Money, Price, Volume
from core.domains.instruments.symbol import Symbol
from core.domains.oms.entities.order import Order
from core.domains.oms.enums import OrderState, OrderType, OrderReason
from core.domains.risk.engine import RiskEngine
from core.events.domain_events import OrderApproved, OrderCreated, OrderRejected
from core.ports.interfaces import (
    IAccountRepository,
    IEventBus,
    IOrderRepository,
    IPositionRepository,
    ISymbolRepository,
)
from application.services.risk_service import PreTradeRiskService
from core.domains.market_data.feed_access import await_tick, tick_bid, tick_ask

logger = logging.getLogger(__name__)


def _digits_currency(account: Any, symbol: Any) -> int:
    """MT5 DigitsCurrency for this trade: account currency digits, from the group.

    Order, Deal and Position each snapshot it, and the database columns are NOT NULL,
    so it has to be resolved at order time. It lives on the Group in MT5
    (ConfigGroups.CurrencyDigits), never on the symbol.
    """
    for holder in (account, getattr(account, "group", None)):
        digits = getattr(holder, "currency_digits", None)
        if isinstance(digits, int) and digits >= 0:
            return digits
    return 2


@dataclass
class CreateOrderCommand:
    """Command to create a new order."""
    account_login: int
    symbol: str
    order_type: OrderType
    volume: Decimal
    price: Optional[Decimal] = None  # For limit/stop orders
    stop_loss: Optional[Decimal] = None
    take_profit: Optional[Decimal] = None
    comment: str = ""
    reason: OrderReason = OrderReason.CLIENT

    def __post_init__(self) -> None:
        """Coerce the enums a caller may have passed as strings.

        The HTTP boundary handed `order_type` through as the raw request string, and an
        Order built with `order_type="BUY"` fails every enum comparison silently:
        `is_market()` said False, so a market order was priced as a pending one and the
        matching engine could not price it at all. Coercing here means a string is a
        convenience rather than a way to build an order that cannot execute.
        """
        if not isinstance(self.order_type, OrderType):
            self.order_type = OrderType(str(self.order_type).upper())
        if not isinstance(self.reason, OrderReason):
            self.reason = OrderReason(str(self.reason).upper())


class CreateOrderHandler:
    """Handler for CreateOrderCommand."""

    def __init__(
        self,
        account_repo: IAccountRepository,
        symbol_repo: ISymbolRepository,
        order_repo: IOrderRepository,
        position_repo: IPositionRepository,
        risk_service: PreTradeRiskService,
        event_bus: IEventBus,
        market_feed: Optional[Any] = None,
    ):
        self.account_repo = account_repo
        self.symbol_repo = symbol_repo
        self.order_repo = order_repo
        self.position_repo = position_repo
        self.risk_service = risk_service
        self.event_bus = event_bus
        #: used to price a market order and to margin it at a real price. Optional only
        #: so existing construction sites keep working; without it a market order cannot
        #: be priced and is rejected rather than filled at a guess.
        self.market_feed = market_feed

    async def handle(self, command: CreateOrderCommand) -> Order:
        """
        Execute the create order command.
        
        Returns the created Order entity.
        Raises ValueError if validation fails.
        """
        # 1. Fetch account and symbol
        account = await self.account_repo.find_by_login(command.account_login)
        if not account:
            raise ValueError(f"Account {command.account_login} not found")

        symbol = await self.symbol_repo.find_by_name(command.symbol)
        if not symbol:
            raise ValueError(f"Symbol {command.symbol} not found")

        # 2. Validate symbol session and trade mode
        now = datetime.now(timezone.utc)
        if not symbol.is_trade_session_active(now):
            raise ValueError(f"Market closed for {command.symbol}")

        side = "BUY" if command.order_type.value.startswith("BUY") else "SELL"
        if not symbol.can_trade_direction(side):
            raise ValueError(f"Trade direction {side} not allowed for {command.symbol}")

        # Validate volume
        volume_valid, volume_reason = symbol.validate_volume(command.volume)
        if not volume_valid:
            raise ValueError(f"Invalid volume: {volume_reason}")

        # 3. Create Order entity
        order = Order(
            account_login=command.account_login,
            symbol=command.symbol,
            order_type=command.order_type,
            reason=command.reason,
            volume_initial=Volume(command.volume),
            volume_current=Volume(command.volume),
            # A market order has no price yet: it is priced from the feed in step 4
            # below. This used to construct Price(Decimal('0')) as the placeholder, and
            # Price.__post_init__ rejects anything non-positive - so EVERY market order
            # raised ValueError("Price must be positive") while building the entity,
            # before any validation ran. None is the honest value for "not yet priced".
            price_order=Price(command.price) if command.price else None,
            price_sl=Price(command.stop_loss) if command.stop_loss else None,
            price_tp=Price(command.take_profit) if command.take_profit else None,
            comment=command.comment,
            digits=symbol.digits,
            # MT5 DigitsCurrency is a GROUP property (ConfigGroups.CurrencyDigits), not a
            # symbol one - Symbol has no such field, and reading it raised AttributeError
            # for every order. Resolve account -> group -> 2.
            digits_currency=_digits_currency(account, symbol),
            contract_size=symbol.contract_size,
        )

        # 4. Price the order. A market order has no client-supplied price, and margin
        #    cannot be computed without one: the previous code substituted Decimal('1.0')
        #    "for market orders", which understated EURUSD margin by ~1x and JPY margin by
        #    ~150x, so the check passed for almost anything.
        is_market = order.is_market()
        price_for_risk: Optional[Price] = None
        if is_market:
            try:
                price_for_risk = await self._market_price(command.symbol, side)
            except ValueError as exc:
                # No price means no trade. Reject and PERSIST it, the same as every other
                # rejection: an order that vanishes leaves no audit trail, and MT5 keeps
                # rejected orders in the history. Raising straight out of here - which is
                # what this did - lost the order entirely.
                await self._reject(order, str(exc))
                raise
            order.price_order = price_for_risk
        elif command.price:
            price_for_risk = Price(command.price)

        # 5. Pre-trade risk, under the per-account lock, through the one margin path the
        #    platform has. This handler used to carry its own inline formula - one of five
        #    in the tree - which ignored the symbol's three currencies, the group's
        #    per-symbol overrides and the maintenance/initial distinction. validate_order
        #    delegates to core.domains.market_data.margin, where MT5's own published
        #    examples are asserted.
        #
        #    publish_events=False: the approval must go out AFTER the order is persisted,
        #    because the ExecutionOrchestrator that consumes it calls
        #    order_repo.find_by_id(). Publishing from inside validate_order - which holds
        #    the per-account lock and runs before the save - deadlocked on that same lock
        #    and handed the orchestrator an order it could not find.
        approved = await self.risk_service.validate_order(
            order=order,
            account=account,
            symbol=symbol,
            current_price=price_for_risk,
            publish_events=False,
        )
        if not approved:
            # validate_order was called with publish_events=False, so it did not publish
            # the rejection; do it here, with the reason it recorded, so subscribers and
            # the audit log see the same thing they would have seen otherwise.
            reason = getattr(self.risk_service, "last_rejection_reason", None) or (
                f"Pre-trade risk check failed for {command.symbol}"
            )
            await self._reject(order, reason)
            raise ValueError(f"Order rejected: {reason}")

        # 6. Persist the order.
        order.state = OrderState.PLACED
        saved_order = await self.order_repo.save(order)

        # 7. Publish OrderCreated.
        await self.event_bus.publish(OrderCreated(
            aggregate_id=saved_order.ticket_id,
            payload={
                "order_id": saved_order.ticket_id,
                "account_login": command.account_login,
                "symbol": command.symbol,
                "order_type": command.order_type.value,
                "volume": str(command.volume),
                "price": str(price_for_risk.value) if price_for_risk else None,
            }
        ))

        # 8. Publish OrderApproved - this is what the ExecutionOrchestrator listens for.
        #    Nothing published it before, so a created order sat in PLACED forever and no
        #    deal, position or coverage movement ever happened. Both identifier spellings
        #    are carried because consumers read both.
        await self.event_bus.publish(OrderApproved(
            aggregate_id=saved_order.ticket_id,
            payload={
                "order_id": saved_order.ticket_id,
                "ticket_id": saved_order.ticket_id,
                "account_login": command.account_login,
                "symbol": command.symbol,
                "volume": str(command.volume),
                "price": str(price_for_risk.value) if price_for_risk else None,
                "approved_at": saved_order.updated_at.isoformat(),
            }
        ))

        # 9. Re-read the order: with an in-process bus the orchestrator has already run,
        #    so the entity the caller receives reflects the fill rather than the intent.
        final_order = saved_order
        if is_market:
            try:
                refreshed = await self.order_repo.find_by_id(saved_order.ticket_id)
                if refreshed is not None:
                    final_order = refreshed
            except Exception as exc:  # noqa: BLE001 - the saved order is still a valid answer
                logger.debug("could not re-read order %s after execution: %s", saved_order.ticket_id, exc)

        logger.info(
            "Order %s created for account %s: state=%s",
            final_order.ticket_id,
            command.account_login,
            getattr(final_order.state, "value", final_order.state),
        )
        return final_order

    async def _reject(self, order: Order, reason: str) -> None:
        """Move an order to REJECTED, persist it, and publish OrderRejected.

        One path for every rejection reason, so a rejected order is always recorded and
        always announced. Before this, an unpriceable market order raised out of step 4
        with nothing persisted, while an insufficient-margin order was persisted with no
        event - two different half-behaviours for the same outcome.
        """
        if not order.is_terminal():
            order.reject(reason)
        try:
            await self.order_repo.save(order)
        except Exception as exc:  # noqa: BLE001 - the rejection must still be published
            logger.error("could not persist rejected order %s: %s", order.ticket_id, exc)
        await self.event_bus.publish(OrderRejected(
            aggregate_id=order.ticket_id,
            payload={
                "order_id": order.ticket_id,
                "ticket_id": order.ticket_id,
                "account_login": order.account_login,
                "symbol": order.symbol,
                "reason": reason,
            },
        ))
        logger.warning("Order %s rejected: %s", order.ticket_id, reason)

    async def _market_price(self, symbol_name: str, side: str) -> Price:
        """Current execution price for a market order: BUY at the ask, SELL at the bid.

        Raises when there is no price. Filling at the order's own (zero) price, or at
        1.0, creates a position the client never agreed to and a margin requirement
        that is wrong by orders of magnitude.
        """
        tick = await await_tick(self.market_feed, symbol_name)
        bid, ask = tick_bid(tick), tick_ask(tick)
        if side == "BUY":
            if ask is None:
                raise ValueError(f"No ask price available for {symbol_name}; cannot execute a market BUY")
            return Price(Decimal(str(ask)))
        if bid is None:
            raise ValueError(f"No bid price available for {symbol_name}; cannot execute a market SELL")
        return Price(Decimal(str(bid)))


CreateOrderCommandHandler = CreateOrderHandler
