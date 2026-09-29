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
# F1: the client-plane sockets (/ws/stream public ticks, /ws/user private trade
# updates) are served by the ConnectionManager singleton the endpoint module
# registered in the app. The bridge used to broadcast EXCLUSIVELY to the
# manager subscription manager, so those two sockets accepted connections and
# then never sent a frame - a healthy-looking connection over a silent absence
# of data (the D6/M5-defect-9 shape). One bridge, both audiences.
from api.websockets.endpoints import manager as client_sockets

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
            self.event_bus.subscribe(EventType.MARGIN_CALL_TRIGGERED, self._on_margin_call_triggered)
            self.event_bus.subscribe(EventType.STOP_OUT_INITIATED, self._on_stop_out_initiated)
            logger.info("WebSocketEventBridge started")
        except Exception as e:
            logger.warning(f"Failed to subscribe event handlers in WebSocketEventBridge: {e}")
    
    async def stop(self) -> None:
        """Stop listening to domain events."""
        logger.info("WebSocketEventBridge stopped")
    
    async def _on_tick_received(self, event: DomainEvent) -> None:
        payload = getattr(event, 'payload', {})
        await self.subscription_manager.broadcast("ticks", payload)
        symbol = payload.get("symbol")
        bid, ask = payload.get("bid"), payload.get("ask")
        if symbol is not None and bid is not None and ask is not None:
            await client_sockets.broadcast_tick(
                str(symbol), str(bid), str(ask),
                str(payload["spread"]) if payload.get("spread") is not None else None,
            )
    
    async def _on_order_created(self, event: DomainEvent) -> None:
        payload = getattr(event, 'payload', {})
        await self.subscription_manager.broadcast("orders", {"action": "created", **payload})
        await self._user_update(payload, "order_created")
    
    async def _on_order_cancelled(self, event: DomainEvent) -> None:
        payload = getattr(event, 'payload', {})
        await self.subscription_manager.broadcast("orders", {"action": "cancelled", **payload})
        await self._user_update(payload, "order_cancelled")
    
    async def _on_order_modified(self, event: DomainEvent) -> None:
        payload = getattr(event, 'payload', {})
        await self.subscription_manager.broadcast("orders", {"action": "modified", **payload})
        await self._user_update(payload, "order_modified")
    
    async def _on_deal_created(self, event: DomainEvent) -> None:
        payload = getattr(event, 'payload', {})
        await self.subscription_manager.broadcast("deals", {"action": "created", **payload})
        await self._user_update(payload, "deal_created")
    
    async def _on_position_opened(self, event: DomainEvent) -> None:
        payload = getattr(event, 'payload', {})
        await self.subscription_manager.broadcast("positions", {"action": "opened", **payload})
        await self._user_update(payload, "position_opened")

    async def _user_update(self, payload: dict, event_type: str) -> None:
        """F1: route an event to its account's PRIVATE socket (/ws/user) when
        the payload identifies one. No login -> no delivery, never a broadcast:
        one account's trade event reaching every connected user would be a
        leak, not a feature."""
        login = payload.get("account_login", payload.get("login"))
        if login is None:
            return
        try:
            await client_sockets.send_user_update(str(login), event_type, payload)
        except Exception as exc:  # noqa: BLE001
            logger.debug("could not deliver %s to user socket for %s: %s", event_type, login, exc)

    async def _on_margin_call_triggered(self, event: DomainEvent) -> None:
        payload = getattr(event, 'payload', {})
        await self.subscription_manager.broadcast("accounts", {"action": "margin_call", **payload})
        await self._user_update(payload, "margin_call")

    async def _on_stop_out_initiated(self, event: DomainEvent) -> None:
        payload = getattr(event, 'payload', {})
        await self.subscription_manager.broadcast("accounts", {"action": "stop_out", **payload})
        await self._user_update(payload, "stop_out")
    
    async def _on_position_closed(self, event: DomainEvent) -> None:
        payload = getattr(event, 'payload', {})
        await self.subscription_manager.broadcast("positions", {"action": "closed", **payload})
