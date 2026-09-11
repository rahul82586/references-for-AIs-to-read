"""
Dealer Queue Service.

Implements the MT5-style dealer intervention queue for Request Execution mode.
When an order is routed TO_DEALER, it is locked and placed in a queue waiting
for manual confirmation, rejection, or requote by a dealer.

Architectural Purpose:
Provides a human-in-the-loop mechanism for high-risk or unusual orders.
Decouples the queuing logic from the UI (which will call these methods via API).
"""
import asyncio
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional
from decimal import Decimal
import logging

from core.domains.oms.entities.order import Order, OrderState
from core.domains.execution.models import DealerDecision
from core.events.domain_events import DomainEvent, EventType
from core.ports.interfaces import IEventBus, IOrderRepository

logger = logging.getLogger(__name__)


class DealerQueueService:
    """
    Manages orders routed TO_DEALER (Request Execution mode).
    Mirrors MT5 DealerAnswer workflow:
    1. Order arrives → DealerLock (order is frozen)
    2. Dealer sees it in queue → can CONFIRM, REJECT, or REQUOTE
    3. If no action within timeout → auto-reject or auto-confirm (configurable)
    """

    def __init__(self, event_bus: IEventBus, order_repo: IOrderRepository):
        self.event_bus = event_bus
        self.order_repo = order_repo

        # In-memory dealer queue: ticket_id -> Order
        self.queue: Dict[str, Order] = {}

        # Locks: ticket_id -> lock_expiry_time
        self.locks: Dict[str, datetime] = {}

        # Timeout tasks: ticket_id -> asyncio.Task (for cancellation)
        self.timeout_tasks: Dict[str, asyncio.Task] = {}

        logger.info("DealerQueueService initialized")

    async def enqueue(self, order: Order, timeout_seconds: int = 30):
        """
        Lock order and add to dealer queue.
        Emits DealerInterventionRequiredEvent.

        Args:
            order: The order requiring dealer intervention.
            timeout_seconds: Time before auto-reject (default 30s).
        """
        if order.ticket_id in self.queue:
            logger.warning(f"Order {order.ticket_id} already in dealer queue")
            return

        # Lock the order
        order.state = OrderState.PLACED  # Frozen state waiting for dealer
        self.queue[order.ticket_id] = order
        self.locks[order.ticket_id] = datetime.now(timezone.utc) + timedelta(seconds=timeout_seconds)

        # Create timeout watcher task
        timeout_task = asyncio.create_task(self._watch_timeout(order.ticket_id, timeout_seconds))
        self.timeout_tasks[order.ticket_id] = timeout_task

        # Emit event for UI notification
        event = DomainEvent(
            event_type=EventType.ORDER_QUEUED_FOR_DEALER,
            aggregate_id=order.ticket_id,
            payload={
                "order_id": order.ticket_id,
                "account_login": order.account_login,
                "symbol": order.symbol,
                "volume": str(order.volume.value),
                "timeout_at": self.locks[order.ticket_id].isoformat()
            }
        )
        await self.event_bus.publish(event)

        logger.info(f"Order {order.ticket_id} queued for dealer intervention")

    async def _watch_timeout(self, ticket: str, timeout_seconds: int):
        """Background task to auto-reject if dealer doesn't respond."""
        try:
            await asyncio.sleep(timeout_seconds)
            if ticket in self.queue and ticket in self.locks:
                logger.warning(f"Order {ticket} dealer timeout expired - auto-rejecting")
                await self.dealer_reject(ticket, "SYSTEM", "Dealer response timeout")
        except asyncio.CancelledError:
            pass

    async def dealer_confirm(self, ticket: str, dealer_id: str) -> Order:
        """
        Dealer approves the order.
        Emits OrderDealerConfirmedEvent.
        Returns order for execution.
        """
        if ticket not in self.queue:
            raise ValueError(f"Order {ticket} not found in dealer queue")

        # Cancel timeout watcher
        if ticket in self.timeout_tasks:
            self.timeout_tasks[ticket].cancel()
            del self.timeout_tasks[ticket]

        order = self.queue.pop(ticket)
        self.locks.pop(ticket, None)

        # Emit confirmation event
        event = DomainEvent(
            event_type=EventType.ORDER_DEALER_CONFIRMED,
            aggregate_id=ticket,
            payload={
                "order_id": ticket,
                "dealer_id": dealer_id,
                "action": "CONFIRM"
            }
        )
        await self.event_bus.publish(event)

        logger.info(f"Dealer {dealer_id} confirmed order {ticket}")
        return order

    async def dealer_reject(self, ticket: str, dealer_id: str, reason: str) -> Order:
        """
        Dealer rejects the order.
        Emits OrderRejectedEvent.
        Updates order state to REJECTED.
        """
        if ticket not in self.queue:
            raise ValueError(f"Order {ticket} not found in dealer queue")

        # Cancel timeout watcher
        if ticket in self.timeout_tasks:
            self.timeout_tasks[ticket].cancel()
            del self.timeout_tasks[ticket]

        order = self.queue.pop(ticket)
        self.locks.pop(ticket, None)
        order.state = OrderState.REJECTED

        # Emit rejection event
        event = DomainEvent(
            event_type=EventType.ORDER_REJECTED,
            aggregate_id=ticket,
            payload={
                "order_id": ticket,
                "dealer_id": dealer_id,
                "reason": reason
            }
        )
        await self.event_bus.publish(event)

        # Persist rejection
        await self.order_repo.save(order)

        logger.info(f"Dealer {dealer_id} rejected order {ticket}: {reason}")
        return order

    async def dealer_requote(
        self,
        ticket: str,
        dealer_id: str,
        new_price: Decimal,
        reason: Optional[str] = None
    ) -> Order:
        """
        Dealer offers a new price (requote).
        Emits OrderRequotedEvent.
        Client must accept/reject the new price (handled by client-side logic).
        """
        if ticket not in self.queue:
            raise ValueError(f"Order {ticket} not found in dealer queue")

        # Cancel timeout watcher
        if ticket in self.timeout_tasks:
            self.timeout_tasks[ticket].cancel()
            del self.timeout_tasks[ticket]

        order = self.queue[ticket]  # Keep in queue until client accepts

        # Emit requote event
        event = DomainEvent(
            event_type=EventType.ORDER_REQUOTED,
            aggregate_id=ticket,
            payload={
                "order_id": ticket,
                "dealer_id": dealer_id,
                "new_price": str(new_price),
                "reason": reason
            }
        )
        await self.event_bus.publish(event)

        logger.info(f"Dealer {dealer_id} requoted order {ticket} at {new_price}")
        return order

    async def get_queue(self) -> List[Order]:
        """
        Return all orders waiting for dealer decision (for Dealer UI).
        Filters out expired orders (auto-reject logic could be added here).
        """
        now = datetime.now(timezone.utc)
        active_orders = []

        for ticket, expiry in list(self.locks.items()):
            if now < expiry:
                if ticket in self.queue:
                    active_orders.append(self.queue[ticket])
            else:
                # Timeout expired - could auto-reject here
                logger.warning(f"Order {ticket} dealer timeout expired")
                # Optional: await self.dealer_reject(ticket, "SYSTEM", "Timeout expired")

        return active_orders

    async def check_timeouts(self):
        """
        Background task to check for timed-out orders.
        Should be called periodically (e.g., every 5 seconds).
        Note: This is now redundant with _watch_timeout tasks, but kept for manual checks.
        """
        now = datetime.now(timezone.utc)
        expired_tickets = [
            ticket for ticket, expiry in self.locks.items()
            if now >= expiry and ticket not in self.timeout_tasks  # Only check if no watcher task
        ]

        for ticket in expired_tickets:
            await self.dealer_reject(ticket, "SYSTEM", "Dealer response timeout")
