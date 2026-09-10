"""
Manager API Subscription Manager.

Tracks which clients are subscribed to which events and routes
domain events to the appropriate WebSocket connections.

Mirrors MT5 Manager API subscription endpoints:
- SubscribeAccount, SubscribeDeals, SubscribeGroup
- SubscribeOrderProfit, SubscribePositions, SubscribeRequests
- SubscribeSymbol, SubscribeTicks, SubscribeUser
"""
import logging
from datetime import datetime, timezone
from typing import Dict, List, Set
from fastapi import WebSocket

logger = logging.getLogger(__name__)


class ManagerSubscriptionManager:
    """
    Manages WebSocket subscriptions for Manager API clients.
    
    Each client can subscribe to multiple event types:
    - ticks: Real-time price updates
    - orders: Order state changes
    - deals: Deal executions
    - positions: Position updates
    - accounts: Account state changes (margin calls, stop-outs)
    - requests: Trade request updates
    - groups: Group configuration changes
    - symbols: Symbol configuration changes
    """
    
    def __init__(self):
        # Map: event_type -> set of (client_id, websocket)
        self._subscriptions: Dict[str, Set[tuple[str, WebSocket]]] = {
            "ticks": set(),
            "orders": set(),
            "deals": set(),
            "positions": set(),
            "accounts": set(),
            "requests": set(),
            "groups": set(),
            "symbols": set(),
        }
        
        # Map: client_id -> set of event_types
        self._client_subscriptions: Dict[str, Set[str]] = {}
        
        # Map: client_id -> websocket
        self._client_connections: Dict[str, WebSocket] = {}
        
        logger.info("ManagerSubscriptionManager initialized")
    
    async def subscribe(
        self,
        client_id: str,
        websocket: WebSocket,
        event_types: List[str]
    ) -> None:
        """Subscribe a client to specific event types."""
        self._client_connections[client_id] = websocket
        
        if client_id not in self._client_subscriptions:
            self._client_subscriptions[client_id] = set()
        
        for event_type in event_types:
            if event_type in self._subscriptions:
                self._subscriptions[event_type].add((client_id, websocket))
                self._client_subscriptions[client_id].add(event_type)
                logger.debug(f"Client {client_id} subscribed to {event_type}")
            else:
                logger.warning(f"Unknown event type: {event_type}")
    
    async def unsubscribe(
        self,
        client_id: str,
        event_types: List[str] = None
    ) -> None:
        """Unsubscribe a client from specific event types (or all)."""
        if event_types is None:
            # Unsubscribe from all
            event_types = list(self._client_subscriptions.get(client_id, []))
        
        for event_type in event_types:
            if event_type in self._subscriptions:
                # Remove all (client_id, websocket) pairs for this client
                self._subscriptions[event_type] = {
                    (cid, ws) for cid, ws in self._subscriptions[event_type]
                    if cid != client_id
                }
                
                if client_id in self._client_subscriptions:
                    self._client_subscriptions[client_id].discard(event_type)
                
                logger.debug(f"Client {client_id} unsubscribed from {event_type}")
        
        # If no more subscriptions, remove client connection
        if client_id in self._client_subscriptions and not self._client_subscriptions[client_id]:
            del self._client_subscriptions[client_id]
            if client_id in self._client_connections:
                del self._client_connections[client_id]
    
    async def broadcast(self, event_type: str, payload: dict) -> None:
        """Broadcast an event to all subscribers of that event type."""
        if event_type not in self._subscriptions:
            return
        
        subscribers = self._subscriptions[event_type]
        if not subscribers:
            return
        
        message = {
            "event_type": event_type,
            "payload": payload,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        
        # Send to all subscribers
        disconnected = []
        for client_id, websocket in subscribers:
            try:
                await websocket.send_json(message)
            except Exception as e:
                logger.error(f"Failed to send to client {client_id}: {e}")
                disconnected.append((client_id, websocket))
        
        # Clean up disconnected clients
        for client_id, websocket in disconnected:
            await self.unsubscribe(client_id)
    
    def get_subscription_count(self, event_type: str = None) -> int:
        """Get number of subscriptions (optionally for a specific event type)."""
        if event_type:
            return len(self._subscriptions.get(event_type, set()))
        return sum(len(subs) for subs in self._subscriptions.values())
    
    def get_client_subscriptions(self, client_id: str) -> List[str]:
        """Get list of event types a client is subscribed to."""
        return list(self._client_subscriptions.get(client_id, []))


# Singleton instance
_manager_subscription_manager: ManagerSubscriptionManager = None


def get_manager_subscription_manager() -> ManagerSubscriptionManager:
    """Get or create the singleton ManagerSubscriptionManager."""
    global _manager_subscription_manager
    if _manager_subscription_manager is None:
        _manager_subscription_manager = ManagerSubscriptionManager()
    return _manager_subscription_manager