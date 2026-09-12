"""
WebSocket Connection Manager

Manages active WebSocket connections for public market data streaming and
private authenticated user trade event updates.
"""
import json
import logging
from typing import Dict, List, Optional, Set
from fastapi import WebSocket

logger = logging.getLogger(__name__)


class ConnectionManager:
    """
    Tracks and distributes messages to public broadcast streams and user-specific streams.
    """
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.user_connections: Dict[str, Set[WebSocket]] = {}

    async def connect_public(self, websocket: WebSocket) -> None:
        """Register an unauthenticated public stream connection."""
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.debug(f"Public WebSocket connected. Total active: {len(self.active_connections)}")

    async def connect_user(self, websocket: WebSocket, user_id: str) -> None:
        """Register an authenticated private user stream connection."""
        if user_id not in self.user_connections:
            self.user_connections[user_id] = set()
        self.user_connections[user_id].add(websocket)
        logger.debug(f"User WebSocket connected for login '{user_id}'")

    def disconnect(self, websocket: WebSocket, user_id: Optional[str] = None) -> None:
        """Unregister a disconnected WebSocket connection."""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

        if user_id and user_id in self.user_connections:
            self.user_connections[user_id].discard(websocket)
            if not self.user_connections[user_id]:
                del self.user_connections[user_id]

    async def broadcast_tick(self, symbol: str, bid: str, ask: str, spread: Optional[str] = None) -> None:
        """Broadcast a price tick to ALL public WebSocket connections."""
        message = json.dumps({
            "type": "tick",
            "symbol": symbol,
            "bid": bid,
            "ask": ask,
            "spread": spread
        })
        to_remove = []
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except Exception:
                to_remove.append(connection)

        for closed_conn in to_remove:
            self.disconnect(closed_conn)

    async def send_user_update(self, user_id: str, event_type: str, payload: dict) -> None:
        """Send a private trade/risk update event to a specific user's WebSockets."""
        if user_id not in self.user_connections:
            return

        message = json.dumps({
            "type": event_type,
            "data": payload
        })
        to_remove = []
        for connection in self.user_connections[user_id]:
            try:
                await connection.send_text(message)
            except Exception:
                to_remove.append(connection)

        for closed_conn in to_remove:
            self.disconnect(closed_conn, user_id=user_id)
