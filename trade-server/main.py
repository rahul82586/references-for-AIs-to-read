import uvicorn
from fastapi import FastAPI, APIRouter, WebSocket, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import asyncio
import logging
import sys
import time
from typing import Optional, Dict, Any, List

from core.event_bus import bus
from core.events import EVT_CONNECTION_STATUS, EVT_MARKET_UPDATE
from connectors.mt5_connector import MT5Connector
from ws.stream import ws_manager, market_broadcaster, router as ws_router

# Setup beautiful logging
root_logger = logging.getLogger()
root_logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(name)s: %(message)s')

# Clear existing handlers
for handler in root_logger.handlers[:]:
    root_logger.removeHandler(handler)

sh = logging.StreamHandler(sys.stdout)
sh.setFormatter(formatter)
root_logger.addHandler(sh)

logger = logging.getLogger("trade_server")

# Global singleton connection state
global_connector: Optional[MT5Connector] = None

# Lifespan Context Manager
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Trade Server booting...")
    ws_manager.loop = asyncio.get_running_loop()
    market_broadcaster.loop = asyncio.get_running_loop()
    asyncio.create_task(ws_manager.heartbeat_loop())
    
    yield
    
    # Shutdown
    logger.info("Trade Server shutting down...")
    global global_connector
    if global_connector:
        try:
            logger.info("Tearing down global MT5 connection...")
            global_connector.disconnect()
        except Exception as e:
            logger.error(f"Error disconnecting connector on shutdown: {e}")
        global_connector = None

app = FastAPI(title="Trade Server Backend", version="1.0.0", lifespan=lifespan)

# Enable CORS for frontend widgets
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request Models
class ConnectRequest(BaseModel):
    login: int
    password: str
    server: str
    path: str = ""

class SubscribeRequest(BaseModel):
    symbol: str

class OrderRequest(BaseModel):
    symbol: str
    side: str  # buy, sell
    volume: float
    price: Optional[float] = None
    sl: Optional[float] = None
    tp: Optional[float] = None
    type_filling: Optional[str] = "FOK"

class ClosePositionRequest(BaseModel):
    symbol: str
    ticket: str
    volume: float
    side: str

# API Router
api_router = APIRouter(prefix="/api/v1")

@api_router.get("/health")
async def health_check():
    return {"status": "success", "message": "Trade Server running"}

@api_router.post("/connect")
async def connect_mt5(req: ConnectRequest):
    global global_connector
    logger.info(f"Received connect request: account={req.login}, server={req.server}, path='{req.path}', password_length={len(req.password)}")
    
    if global_connector:
        try:
            logger.info("Disconnecting previous active session...")
            global_connector.disconnect()
            
            # Clear all active subscriptions from market_broadcaster to avoid flushing stale symbols
            from ws.stream import market_broadcaster
            for ws in list(market_broadcaster.subscriptions.keys()):
                market_broadcaster.subscriptions[ws].clear()
            for ws in list(market_broadcaster.book_subscriptions.keys()):
                market_broadcaster.book_subscriptions[ws].clear()
            logger.info("Cleared previous session subscriptions from broadcaster")
        except Exception as e:
            logger.warning(f"Error disconnecting previous session: {e}")
        global_connector = None
        
    connector = MT5Connector(config={
        "id": "mt5_main",
        "params": {
            "path": req.path,
            "login": req.login,
            "password": req.password,
            "server": req.server
        }
    })
    global_connector = connector
    
    success = connector.connect()
    if not success:
        global_connector = None
        raise HTTPException(status_code=500, detail="Failed to initialize and spawn MT5Worker process")
        
    # Wait for the worker to report connection success (max 6 seconds)
    start_wait = time.time()
    while time.time() - start_wait < 6.0:
        if global_connector is not connector:
            raise HTTPException(status_code=409, detail="Connection preempted by another request")
        if connector.is_connected:
            break
        await asyncio.sleep(0.1)
        
    if global_connector is connector and connector.is_connected:
        logger.info(f"Successfully authenticated trade account {req.login}")
        
        # Flush active WebSocket subscriptions to the newly connected connector
        try:
            from ws.stream import market_broadcaster
            active_symbols = market_broadcaster.get_all_subscribed_symbols()
            logger.info(f"Flushing {len(active_symbols)} active subscriptions to newly connected account: {active_symbols}")
            for symbol in active_symbols:
                connector.subscribe_symbol(symbol)
                
            active_books = market_broadcaster.get_all_subscribed_book_symbols()
            logger.info(f"Flushing {len(active_books)} active book subscriptions: {active_books}")
            for symbol in active_books:
                connector.subscribe_book(symbol)
        except Exception as e:
            logger.error(f"Error flushing subscriptions on connect: {e}")

        bus.publish(EVT_CONNECTION_STATUS, [{
            "id": "mt5_main",
            "name": "MetaTrader 5",
            "type": "mt5",
            "status": "connected"
        }])
        return {
            "status": "success",
            "message": f"Connected to trade account {req.login} successfully"
        }
    else:
        # Tear down worker since login failed
        if global_connector is connector:
            try: connector.disconnect()
            except: pass
            global_connector = None
            
        err_msg = connector.last_error_msg if connector.last_error_msg else "Authentication failed on MT5 trading server"
        logger.warning(f"Connection failed for account {req.login}: {err_msg}")
        raise HTTPException(status_code=401, detail=err_msg)

@api_router.post("/disconnect")
async def disconnect_mt5():
    global global_connector
    logger.info("Received disconnect request")
    if global_connector:
        try:
            global_connector.disconnect()
        except Exception as e:
            logger.error(f"Error during manual disconnect: {e}")
        global_connector = None
        
    bus.publish(EVT_CONNECTION_STATUS, [{
        "id": "mt5_main",
        "name": "MetaTrader 5",
        "type": "mt5",
        "status": "disconnected"
    }])
    return {"status": "success", "message": "MT5 session disconnected successfully"}

@api_router.get("/status")
async def get_connection_status():
    global global_connector
    if global_connector and global_connector.is_connected:
        return {
            "status": "success",
            "data": {
                "id": "mt5_main",
                "status": "connected",
                "login": global_connector.login,
                "server": global_connector.server
            }
        }
    return {
        "status": "success",
        "data": {
            "id": "mt5_main",
            "status": "disconnected"
        }
    }

@api_router.post("/subscribe")
async def subscribe_symbol(req: SubscribeRequest):
    global global_connector
    if not global_connector or not global_connector.is_connected:
        raise HTTPException(status_code=400, detail="No active trade connection")
        
    logger.info(f"Subscribing symbol: {req.symbol}")
    global_connector.subscribe_symbol(req.symbol)
    return {"status": "success", "message": f"Subscribed {req.symbol}"}

@api_router.post("/unsubscribe")
async def unsubscribe_symbol(req: SubscribeRequest):
    global global_connector
    if not global_connector or not global_connector.is_connected:
        raise HTTPException(status_code=400, detail="No active trade connection")
        
    logger.info(f"Unsubscribing symbol: {req.symbol}")
    global_connector.unsubscribe_symbol(req.symbol)
    return {"status": "success", "message": f"Unsubscribed {req.symbol}"}

@api_router.get("/symbols")
async def get_symbols():
    global global_connector
    if not global_connector or not global_connector.is_connected:
        raise HTTPException(status_code=400, detail="No active trade connection")
        
    symbols = global_connector.get_symbol_list()  # returns List[Dict] with name, digits, description
    return {"status": "success", "data": symbols}

@api_router.get("/balance")
async def get_balance():
    global global_connector
    if not global_connector or not global_connector.is_connected:
        raise HTTPException(status_code=400, detail="No active trade connection")
        
    balance_info = global_connector.get_balance()
    return {"status": "success", "data": balance_info}

@api_router.get("/positions")
async def get_positions():
    global global_connector
    if not global_connector or not global_connector.is_connected:
        raise HTTPException(status_code=400, detail="No active trade connection")
        
    positions = global_connector.get_positions()
    return {"status": "success", "data": positions}

@api_router.post("/place-order")
async def place_order(req: OrderRequest):
    global global_connector
    if not global_connector or not global_connector.is_connected:
        raise HTTPException(status_code=400, detail="No active trade connection")
        
    logger.info(f"Placing order: symbol={req.symbol} side={req.side} vol={req.volume} filling={req.type_filling}")
    res = global_connector.place_order(req.symbol, req.side, req.volume, req.price, req.sl, req.tp, req.type_filling)
    
    if res.get("success"):
        return {"status": "success", "data": res}
    else:
        raise HTTPException(status_code=500, detail=res.get("error", "Failed to place order"))

class CancelOrderRequest(BaseModel):
    ticket: str

@api_router.get("/orders")
async def get_orders():
    global global_connector
    if not global_connector or not global_connector.is_connected:
        raise HTTPException(status_code=400, detail="No active trade connection")
    orders = global_connector.get_orders()
    return {"status": "success", "data": orders}

@api_router.post("/cancel-order")
async def cancel_order(req: CancelOrderRequest):
    global global_connector
    if not global_connector or not global_connector.is_connected:
        raise HTTPException(status_code=400, detail="No active trade connection")
    logger.info(f"Cancelling order: ticket={req.ticket}")
    res = global_connector.cancel_order(req.ticket)
    if res.get("success"):
        return {"status": "success", "data": res}
    else:
        raise HTTPException(status_code=500, detail=res.get("error", "Failed to cancel order"))

@api_router.post("/close-position")
async def close_position(req: ClosePositionRequest):
    global global_connector
    if not global_connector or not global_connector.is_connected:
        raise HTTPException(status_code=400, detail="No active trade connection")
        
    logger.info(f"Closing position: ticket={req.ticket} symbol={req.symbol}")
    res = global_connector.close_position(req.symbol, req.ticket, req.volume, req.side)
    
    if res.get("success"):
        return {"status": "success", "data": res}
    else:
        raise HTTPException(status_code=500, detail=res.get("error", "Failed to close position"))

@api_router.get("/history-deals")
async def get_history_deals(from_time: Optional[int] = None, to_time: Optional[int] = None):
    global global_connector
    if not global_connector or not global_connector.is_connected:
        raise HTTPException(status_code=400, detail="No active trade connection")
        
    if from_time is None:
        from_time = int(time.time() - 30 * 24 * 3600) # Default to 30 days ago
    if to_time is None:
        to_time = int(time.time())
        
    deals = global_connector.get_history_deals(from_time, to_time)
    return {"status": "success", "data": deals}

@app.get("/history")
async def get_tradingview_history(symbol: str, from_time: int, to_time: int):
    global global_connector
    if not global_connector or not global_connector.is_connected:
        return {"s": "no_data", "message": "No active broker connection"}
        
    try:
        bars = global_connector.get_history(symbol.upper(), from_time, to_time)
        if not bars:
            return {"s": "no_data"}
            
        return {
            "s": "ok",
            "t": [b["t"] for b in bars],
            "o": [b["o"] for b in bars],
            "h": [b["h"] for b in bars],
            "l": [b["l"] for b in bars],
            "c": [b["c"] for b in bars],
            "v": [b["v"] for b in bars],
        }
    except Exception as e:
        logger.error(f"Error fetching history: {e}")
        return {"s": "no_data", "error": str(e)}

@app.get("/symbols")
@app.get("/api/symbols")
async def get_market_watch_symbols():
    """
    Returns the initial set of active symbols for the Market Watch panel.
    """
    global global_connector
    if global_connector and global_connector.is_connected:
        try:
            syms = global_connector.get_symbol_list()  # List[Dict] with name, digits, description, selected
            active_list = [s for s in syms if s.get("selected")]
            if not active_list:
                active_list = syms[:8]
            return [{
                "symbol": s["name"],
                "description": s.get("description", s["name"]),
                "exchange": "MT5",
                "type": "forex",
                "digits": s.get("digits", 5)
            } for s in active_list]
        except Exception as e:
            logger.error(f"Error getting symbols from broker: {e}")

    # Not connected — return empty
    return []

@app.get("/api/symbols/all")
async def get_all_broker_symbols():
    """
    Returns the complete broker symbol directory for search/autocomplete.
    Returns an empty list when not connected — no mock/SIM fallback.
    """
    global global_connector
    if global_connector and global_connector.is_connected:
        try:
            syms = global_connector.get_symbol_list()
            return [{
                "symbol": s["name"],
                "description": s.get("description", s["name"]),
                "exchange": s.get("exchange", "MT5"),
                "type": "forex",
                "digits": s.get("digits", 5),
                "selected": s.get("selected", False),
                "path": s.get("path", s["name"]),
                "contract_size": s.get("contract_size", 100000.0),
                "spread": s.get("spread", 0),
                "stops_level": s.get("stops_level", 0),
                "margin_currency": s.get("margin_currency", "USD"),
                "profit_currency": s.get("profit_currency", "USD"),
                "calc_mode": s.get("calc_mode", "Forex"),
                "trade_mode": s.get("trade_mode", "Full Access"),
                "sector": s.get("sector", "Forex"),
                "tick_size": s.get("tick_size", 0.00001),
                "tick_value": s.get("tick_value", 1.0)
            } for s in syms]
        except Exception as e:
            logger.error(f"Error getting all symbols from broker: {e}")

    # Not connected — return empty, no fake data
    return []

# Include both REST endpoints and WebSocket stream
app.include_router(api_router)
app.include_router(ws_router)


if __name__ == "__main__":
    import os
    port = int(os.getenv("PORT", "8003"))
    logger.info(f"Starting Trade Server on http://localhost:{port}")
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=False)
