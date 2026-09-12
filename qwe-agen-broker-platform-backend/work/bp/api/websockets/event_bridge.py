"""
Event-to-WebSocket Bridge.

Subscribes to domain events from the EventBus and routes them
to the appropriate WebSocket subscribers.
"""
import logging
from core.events.domain_events import (
    DomainEvent,
    EventType,
    TickReceived,
    OrderCreated,
    OrderCancelled,
    OrderModified,
    DealCreated,
    TradeModified,
    PositionOpened,
    PositionClosed,
    MarginCallEntered,
    StopOutEntered,
)
from core.ports.interfaces import IEventBus
from api.websockets.manager_subscriptions import get_manager_subscription_manager

logger = logging.getLogger(__name__)


class WebSocketEventBridge:
    """
    Bridges domain events to WebSocket subscribers.
    
    Subscribes to EventBus events and broadcasts them to
    Manager API WebSocket clients.
    """
    
    def __init__(self, event_bus: IEventBus):
        self.event_bus = event_bus
        self.subscription_manager = get_manager_subscription_manager()
    
    async def start(self) -> None:
        """Start listening to domain events."""
        try:
            self.event_bus.subscribe(EventType.TICK_RECEIVED, self._on_tick_received)
            self.event_bus.subscribe(EventType.ORDER_CREATED, self._on_order_created)
            self.event_bus.subscribe(EventType.ORDER_CANCELLED, self._on_order_cancelled)
            self.event_bus.subscribe(EventType.ORDER_MODIFIED, self._on_order_modified)
            self.event_bus.subscribe(EventType.DEAL_CREATED, self._on_deal_created)
            self.event_bus.subscribe(EventType.POSITION_OPENED, self._on_position_opened)
            self.event_bus.subscribe(EventType.POSITION_CLOSED, self._on_position_closed)
            logger.info("WebSocketEventBridge started")
        except Exception as e:
            logger.warning(f"Failed to subscribe event handlers in WebSocketEventBridge: {e}")
    
    async def stop(self) -> None:
        """Stop listening to domain events."""
        logger.info("WebSocketEventBridge stopped")
    
    async def _on_tick_received(self, event: DomainEvent) -> None:
        payload = getattr(event, 'payload', {})
        await self.subscription_manager.broadcast("ticks", payload)
    
    async def _on_order_created(self, event: DomainEvent) -> None:
        payload = getattr(event, 'payload', {})
        await self.subscription_manager.broadcast("orders", {"action": "created", **payload})
    
    async def _on_order_cancelled(self, event: DomainEvent) -> None:
        payload = getattr(event, 'payload', {})
        await self.subscription_manager.broadcast("orders", {"action": "cancelled", **payload})
    
    async def _on_order_modified(self, event: DomainEvent) -> None:
        payload = getattr(event, 'payload', {})
        await self.subscription_manager.broadcast("orders", {"action": "modified", **payload})
    
    async def _on_deal_created(self, event: DomainEvent) -> None:
        payload = getattr(event, 'payload', {})
        await self.subscription_manager.broadcast("deals", {"action": "created", **payload})
    
    async def _on_position_opened(self, event: DomainEvent) -> None:
        payload = getattr(event, 'payload', {})
        await self.subscription_manager.broadcast("positions", {"action": "opened", **payload})
    
    async def _on_position_closed(self, event: DomainEvent) -> None:
        payload = getattr(event, 'payload', {})
        await self.subscription_manager.broadcast("positions", {"action": "closed", **payload})
