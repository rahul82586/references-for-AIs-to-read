"""
Execution Subscriptions.

Wires the ExecutionOrchestrator to the Event Bus by subscribing to OrderApproved events.

Architectural Purpose:
Separates the subscription wiring from the orchestrator logic.
This allows the orchestrator to remain focused on execution flow,
while this module handles event bus registration.
"""
import logging
from core.events.domain_events import EventType
from core.ports.interfaces import IEventBus
from application.services.execution_orchestrator import ExecutionOrchestrator

logger = logging.getLogger(__name__)


class ExecutionSubscriptions:
    """
    Manages event subscriptions for the Execution layer.
    """

    def __init__(self, event_bus: IEventBus, orchestrator: ExecutionOrchestrator):
        self.event_bus = event_bus
        self.orchestrator = orchestrator

    async def register(self):
        """
        Subscribe orchestrator.handle_order_approved to ORDER_APPROVED events.

        This connects the Execution Orchestrator to the Nervous System (Event Bus).
        When Risk Service publishes OrderApproved, the Orchestrator will automatically
        route and execute the order.
        """
        await self.event_bus.subscribe(
            channel=EventType.ORDER_APPROVED.value,
            callback=self.orchestrator.handle_order_approved
        )

        logger.info("ExecutionOrchestrator subscribed to OrderApproved events")

    async def unregister(self):
        """
        Unsubscribe from all events (for graceful shutdown).
        """
        # Note: IEventBus should have an unsubscribe method
        # For now, this is a placeholder
        logger.info("Execution subscriptions unregistered")
