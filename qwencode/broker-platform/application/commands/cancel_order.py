"""
Cancel Order Command Handler.

Cancels a pending order by:
1. Validating order exists and belongs to account
2. Validating order is in a cancellable state (not terminal)
3. Transitioning order state to CANCELLED
4. Releasing reserved margin (if margin was reserved)
5. Emitting OrderCancelled event

Architectural Note:
Only PENDING orders can be cancelled. Market orders that have already
been filled cannot be cancelled — they must be closed via ClosePosition.
"""
import logging
from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal
from typing import Optional

from core.domains.accounts.account import Account
from core.domains.common.value_objects import Money
from core.domains.oms.entities.order import Order
from core.domains.oms.enums import OrderState, OrderType
from core.events.domain_events import OrderCancelled
from core.ports.interfaces import (
    IAccountRepository,
    IEventBus,
    IOrderRepository,
)
from application.services.risk_service import PreTradeRiskService

logger = logging.getLogger(__name__)


@dataclass
class CancelOrderCommand:
    """Command to cancel a pending order."""
    account_login: int
    ticket_id: str
    reason: Optional[str] = None


class CancelOrderHandler:
    """Handler for CancelOrderCommand."""

    def __init__(
        self,
        account_repo: IAccountRepository,
        order_repo: IOrderRepository,
        risk_service: PreTradeRiskService,
        event_bus: IEventBus,
    ):
        self.account_repo = account_repo
        self.order_repo = order_repo
        self.risk_service = risk_service
        self.event_bus = event_bus

    async def handle(self, command: CancelOrderCommand) -> Order:
        """Execute the cancel order command."""
        # 1. Fetch order
        order = await self.order_repo.find_by_id(command.ticket_id)
        if not order:
            raise ValueError(f"Order {command.ticket_id} not found")

        # 2. Verify ownership
        if order.account_login != command.account_login:
            raise ValueError(
                f"Order {command.ticket_id} does not belong to account {command.account_login}"
            )

        # 3. Validate state (only non-terminal orders can be cancelled)
        if order.is_terminal():
            raise ValueError(
                f"Cannot cancel order in state {order.state.value}. "
                f"Order is already {order.state.value}."
            )

        # 4. Calculate reserved margin to release
        # (Only for pending orders that had margin reserved)
        reserved_margin = Decimal('0')
        if order.state in [OrderState.PLACED, OrderState.PARTIALLY_FILLED]:
            # Calculate how much margin was reserved for unfilled portion
            unfilled_volume = order.volume_current.value
            if unfilled_volume > Decimal('0'):
                # Simplified: use price_order * contract_size / leverage
                # In production, this should match the original reservation logic
                reserved_margin = (
                    order.price_order.value *
                    unfilled_volume *
                    order.contract_size
                ) / Decimal(str(100))  # Simplified leverage

        # 5. Cancel the order (inside per-account lock)
        async with self.risk_service.account_lock(command.account_login):
            # Transition state
            order.cancel(reason=command.reason or "Client cancellation")

            # Release reserved margin
            if reserved_margin > Decimal('0'):
                account = await self.account_repo.find_by_login(command.account_login)
                if account:
                    account.margin_used = Money(
                        max(account.margin_used.amount - reserved_margin, Decimal('0')),
                        account.currency
                    )
                    account.margin_free = Money(
                        account.margin_free.amount + reserved_margin,
                        account.currency
                    )
                    if account.margin_used.amount > Decimal('0'):
                        account.margin_level = account.equity.amount / account.margin_used.amount
                    else:
                        account.margin_level = Decimal('999999')
                    await self.account_repo.save(account)

            # Persist order
            saved_order = await self.order_repo.save(order)

        # 6. Emit event
        event = OrderCancelled(
            aggregate_id=saved_order.ticket_id,
            payload={
                "ticket_id": saved_order.ticket_id,
                "account_login": command.account_login,
                "symbol": saved_order.symbol,
                "volume_initial": str(saved_order.volume_initial.value),
                "volume_current": str(saved_order.volume_current.value),
                "reason": command.reason,
            }
        )
        await self.event_bus.publish(event)

        logger.info(f"Order {command.ticket_id} cancelled")

        return saved_order