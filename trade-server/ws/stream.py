import logging
import asyncio
import msgpack
import json
from typing import Set, Dict
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from datetime import datetime, timezone

from core.event_bus import bus
from core.events import (
    EVT_MARKET_UPDATE,
    EVT_STATUS_LOG,
    EVT_TRADE_RESULT,
    EVT_CONNECTION_STATUS
)

logger = logging.getLogger(__name__)

router = APIRouter()

class WebSocketManager:
    def __init__(self):
        self.active_connections: Set[WebSocket] = set()
        self.loop = None

        # Subscribe to EventBus events
        bus.subscribe(EVT_MARKET_UPDATE, self._handle_market_update)
        bus.subscribe(EVT_STATUS_LOG, self._handle_status_log)
        bus.subscribe(EVT_TRADE_RESULT, self._handle_trade_result)
        bus.subscribe(EVT_CONNECTION_STATUS, self._handle_connection_status)

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.add(websocket)
        client_host = websocket.client.host if websocket.client else "unknown"
        logger.info(f"WebSocket client connected from {client_host}. Total clients: {len(self.active_connections)}")
        await websocket.send_json({
            "type": "connection_established",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "message": "Welcome to Trade-Server Real-time Stream"
        })

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            logger.info(f"WebSocket client disconnected. Total clients: {len(self.active_connections)}")

    async def broadcast(self, message: dict):
        disconnected = set()
        for connection in list(self.active_connections):
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"Error broadcasting to client: {e}")
                disconnected.add(connection)
                
        for connection in disconnected:
            self.disconnect(connection)

    def _send_sync(self, msg_type: str, data: dict):
        if not self.active_connections:
            return
            
        message = {
            "type": msg_type,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "data": data
        }
        
        try:
            loop = asyncio.get_running_loop()
            loop.create_task(self.broadcast(message))
        except RuntimeError:
            if self.loop and not self.loop.is_closed():
                asyncio.run_coroutine_threadsafe(self.broadcast(message), self.loop)

    def _handle_market_update(self, data: dict):
        self._send_sync("price_tick", data)

    def _handle_status_log(self, data: dict):
        if isinstance(data, str):
            data = {"message": data}
        self._send_sync("system_log", data)

    def _handle_trade_result(self, data: dict):
        self._send_sync("order_result", data)

    def _handle_connection_status(self, data: dict):
        self._send_sync("connection_status", data)

    async def heartbeat_loop(self):
        logger.info("WebSocket Heartbeat loop started.")
        while True:
            await asyncio.sleep(30)
            if self.active_connections:
                message = {
                    "type": "heartbeat",
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
                await self.broadcast(message)

ws_manager = WebSocketManager()

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await ws_manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)

class MarketDataBroadcaster:
    def __init__(self):
        self.active_connections: Set[WebSocket] = set()
        self.subscriptions: Dict[WebSocket, Set[str]] = {}
        self.book_subscriptions: Dict[WebSocket, Set[str]] = {}
        self.loop = None
        bus.subscribe(EVT_MARKET_UPDATE, self._handle_market_update)
        bus.subscribe("market_book_update", self._handle_book_update)
        bus.subscribe(EVT_CONNECTION_STATUS, self._handle_connection_status)

    def _handle_connection_status(self, data: dict):
        message = {
            "type": "connection_status",
            "data": data
        }
        if self.loop and not self.loop.is_closed():
            asyncio.run_coroutine_threadsafe(self._broadcast_status(message), self.loop)
        else:
            try:
                loop = asyncio.get_running_loop()
                loop.create_task(self._broadcast_status(message))
            except RuntimeError:
                pass

    async def _broadcast_status(self, message: dict):
        for ws in list(self.active_connections):
            try:
                await ws.send_json(message)
            except Exception as e:
                logger.debug(f"Failed to send status to client: {e}")

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.add(websocket)
        self.subscriptions[websocket] = set()
        self.book_subscriptions[websocket] = set()
        logger.info(f"MarketData client connected. Total clients: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        self.active_connections.discard(websocket)
        unsub_symbols = self.subscriptions.pop(websocket, set())
        unsub_books = self.book_subscriptions.pop(websocket, set())
        logger.info(f"MarketData client disconnected. Total clients: {len(self.active_connections)}")
        
        # Release symbols subscription in MT5 if no other client needs them
        for symbol in unsub_symbols:
            still_needed = False
            for ws, subs in self.subscriptions.items():
                if symbol in subs:
                    still_needed = True
                    break
            if not still_needed:
                from main import global_connector
                if global_connector and global_connector.is_connected:
                    try:
                        global_connector.unsubscribe_symbol(symbol)
                    except Exception as e:
                        logger.error(f"Error releasing symbol subscription on disconnect: {e}")
                        
        # Release book subscriptions in MT5 if no other client needs them
        for symbol in unsub_books:
            still_needed = False
            for ws, subs in self.book_subscriptions.items():
                if symbol in subs:
                    still_needed = True
                    break
            if not still_needed:
                from main import global_connector
                if global_connector and global_connector.is_connected:
                    try:
                        global_connector.unsubscribe_book(symbol)
                    except Exception as e:
                        logger.error(f"Error releasing book subscription on disconnect: {e}")

    def get_all_subscribed_symbols(self) -> Set[str]:
        all_subs = set()
        for subs in self.subscriptions.values():
            all_subs.update(subs)
        return all_subs

    def get_all_subscribed_book_symbols(self) -> Set[str]:
        all_subs = set()
        for subs in self.book_subscriptions.values():
            all_subs.update(subs)
        return all_subs

    def subscribe(self, websocket: WebSocket, symbol: str):
        if websocket in self.subscriptions:
            symbol_upper = symbol.upper()
            self.subscriptions[websocket].add(symbol_upper)
            logger.info(f"MarketData client subscribed to {symbol_upper}")
            
            # Proactively tell MT5 connection to subscribe to this symbol!
            from main import global_connector
            if global_connector and global_connector.is_connected:
                global_connector.subscribe_symbol(symbol_upper)

    def subscribe_book(self, websocket: WebSocket, symbol: str):
        if websocket in self.book_subscriptions:
            symbol_upper = symbol.upper()
            self.book_subscriptions[websocket].add(symbol_upper)
            logger.info(f"MarketData client subscribed to DOM book: {symbol_upper}")
            
            from main import global_connector
            if global_connector and global_connector.is_connected:
                global_connector.subscribe_book(symbol_upper)

    def unsubscribe_book(self, websocket: WebSocket, symbol: str):
        if websocket in self.book_subscriptions:
            symbol_upper = symbol.upper()
            self.book_subscriptions[websocket].discard(symbol_upper)
            logger.info(f"MarketData client unsubscribed from DOM book: {symbol_upper}")
            
            still_needed = False
            for ws, subs in self.book_subscriptions.items():
                if symbol_upper in subs:
                    still_needed = True
                    break
            if not still_needed:
                from main import global_connector
                if global_connector and global_connector.is_connected:
                    global_connector.unsubscribe_book(symbol_upper)

    def _handle_market_update(self, tick: dict):
        symbol = tick.get("symbol", "").upper()
        bid = float(tick.get("bid", 0.0))
        ask = float(tick.get("ask", 0.0))

        # Skip zero-price ticks (market closed or uninitialized)
        if bid == 0.0 and ask == 0.0:
            return

        # For Forex, mt5 tick.last is always 0 — use bid as the canonical price
        price = bid if bid > 0 else ask

        tv_tick = {
            "s": symbol,
            "p": price,
            "b": bid,
            "a": ask,
            "q": 1.0,
            "ts": int(tick.get("timestamp", 0) * 1000)
        }
        
        encoded_payload = msgpack.packb(tv_tick, use_bin_type=True)
        
        # Safely marshal back to uvicorn's main thread loop
        if self.loop and not self.loop.is_closed():
            asyncio.run_coroutine_threadsafe(self._broadcast_tick(symbol, encoded_payload), self.loop)
        else:
            try:
                loop = asyncio.get_running_loop()
                loop.create_task(self._broadcast_tick(symbol, encoded_payload))
            except RuntimeError:
                pass

    async def _broadcast_tick(self, symbol: str, encoded_payload: bytes):
        dead_connections = set()
        for ws in list(self.active_connections):
            subs = self.subscriptions.get(ws, set())
            if symbol in subs:
                try:
                    await ws.send_bytes(encoded_payload)
                except Exception as e:
                    logger.debug(f"Failed to stream to client: {e}")
                    dead_connections.add(ws)
                    
        for ws in dead_connections:
            self.disconnect(ws)

    def _handle_book_update(self, book_data: dict):
        symbol = book_data.get("symbol", "").upper()
        
        payload = {
            "type": "book",
            "s": symbol,
            "bids": book_data.get("bids", []),
            "asks": book_data.get("asks", [])
        }
        
        encoded_payload = msgpack.packb(payload, use_bin_type=True)
        
        if self.loop and not self.loop.is_closed():
            asyncio.run_coroutine_threadsafe(self._broadcast_book(symbol, encoded_payload), self.loop)
        else:
            try:
                loop = asyncio.get_running_loop()
                loop.create_task(self._broadcast_book(symbol, encoded_payload))
            except RuntimeError:
                pass

    async def _broadcast_book(self, symbol: str, encoded_payload: bytes):
        dead_connections = set()
        for ws in list(self.active_connections):
            subs = self.book_subscriptions.get(ws, set())
            if symbol in subs:
                try:
                    await ws.send_bytes(encoded_payload)
                except Exception as e:
                    logger.debug(f"Failed to stream book to client: {e}")
                    dead_connections.add(ws)
                    
        for ws in dead_connections:
            self.disconnect(ws)

market_broadcaster = MarketDataBroadcaster()

@router.websocket("/ws/marketdata")
async def marketdata_endpoint(websocket: WebSocket):
    await market_broadcaster.connect(websocket)
    try:
        while True:
            data_str = await websocket.receive_text()
            try:
                data = json.loads(data_str)
                action = data.get("action")
                symbol = data.get("symbol")
                if action == "sub":
                    market_broadcaster.subscribe(websocket, symbol)
                elif action == "sub_book":
                    market_broadcaster.subscribe_book(websocket, symbol)
                elif action == "unsub_book":
                    market_broadcaster.unsubscribe_book(websocket, symbol)
            except Exception:
                pass
    except WebSocketDisconnect:
        market_broadcaster.disconnect(websocket)
    except Exception as e:
        logger.error(f"MarketData WebSocket error: {e}")
        market_broadcaster.disconnect(websocket)
