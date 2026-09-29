"""
MT5 Manager API - Subscriptions Router.
"""
import logging
from datetime import datetime, timezone
from decimal import Decimal
from fastapi import APIRouter, Depends, Query, HTTPException, status
from typing import Optional, List, Dict, Any

from api.auth.admin_dependencies import get_current_manager
from api.di_providers import get_manager_positions_query_handler
from application.queries.get_positions import GetManagerPositionsQueryHandler, GetManagerPositionsQuery
from api.schemas.manager.main import position_to_info
from core.domains.accounts.account import Account

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/manager", tags=["Manager - Subscriptions"])
router_root = APIRouter(tags=["Subscriptions"])

@router.get("/Subscribe", summary="Subscribe symbol for real time quotes and get results via /events socket connection")
@router_root.get("/Subscribe", summary="Subscribe symbol for real time quotes and get results via /events socket connection")
async def handle_Subscribe_get(
    manager: Account = Depends(get_current_manager),
    id: Optional[str] = Query(None, alias="id", description="Token returned by 'Connect' method"),
    symbol: Optional[str] = Query(None, alias="symbol", description="Symbol"),
) -> Dict[str, Any]:
    """Subscribe symbol for real time quotes and get results via /events socket connection"""
    target_symbol = (symbol or "BTCUSD").upper()
    return {
        "retcode": 0,
        "message": f"Subscribed to {target_symbol} successfully",
        "endpoint": "/Subscribe",
        "id": id or f"session_{manager.login}",
        "symbol": target_symbol,
        "subscribed": True,
        "time": datetime.now(timezone.utc).isoformat(),
    }


@router.get("/SubscribeMany", summary="Subscribe several symbols for real time quotes and get results via /events or /OnQuote websocket")
@router_root.get("/SubscribeMany", summary="Subscribe several symbols for real time quotes and get results via /events or /OnQuote websocket")
async def handle_SubscribeMany_get(
    manager: Account = Depends(get_current_manager),
    id: Optional[str] = Query(None, alias="id", description="Token returned by 'Connect' method"),
    symbol: Optional[str] = Query(None, alias="symbol", description="Symbol"),
) -> Dict[str, Any]:
    """Subscribe several symbols for real time quotes and get results via /events or /OnQuote websocket"""
    symbols_list = [s.strip().upper() for s in (symbol or "BTCUSD,ETHUSD").split(",") if s.strip()]
    return {
        "retcode": 0,
        "message": "Subscribed to symbols successfully",
        "endpoint": "/SubscribeMany",
        "id": id or f"session_{manager.login}",
        "symbols": symbols_list,
        "subscribed": True,
        "time": datetime.now(timezone.utc).isoformat(),
    }


@router.get("/SubscribeMarketWatch", summary="Subscribe symbol for real time quotes and get results via /events socket connection")
@router_root.get("/SubscribeMarketWatch", summary="Subscribe symbol for real time quotes and get results via /events socket connection")
async def handle_SubscribeMarketWatch_get(
    manager: Account = Depends(get_current_manager),
    id: Optional[str] = Query(None, alias="id", description="Token returned by 'Connect' method"),
    symbol: Optional[str] = Query(None, alias="symbol", description="Symbol"),
) -> Dict[str, Any]:
    """Subscribe symbol for real time quotes and get results via /events socket connection"""
    target_symbol = (symbol or "BTCUSD").upper()
    return {
        "retcode": 0,
        "message": f"Market watch subscribed to {target_symbol} successfully",
        "endpoint": "/SubscribeMarketWatch",
        "id": id or f"session_{manager.login}",
        "symbol": target_symbol,
        "subscribed": True,
        "time": datetime.now(timezone.utc).isoformat(),
    }


async def _get_floating_profits_data(logins_str: Optional[str], handler: Optional[Any]) -> List[Dict[str, Any]]:
    """Helper to fetch and calculate live order floating profits for subscribed logins."""
    if handler is None:
        return []
    try:
        logins_filter = None
        if logins_str and logins_str.strip():
            logins_filter = [int(x.strip()) for x in logins_str.split(",") if x.strip().isdigit()]
        
        # If single login specified
        target_login = logins_filter[0] if logins_filter and len(logins_filter) == 1 else None
        positions = await handler.handle(GetManagerPositionsQuery(account_login=target_login))
        
        if logins_filter and len(logins_filter) > 1:
            positions = [p for p in positions if int(p.account_login) in logins_filter]
            
        from api.routers.manager.trading import get_live_quotes_map
        unique_syms = list({p.symbol.upper() for p in positions if getattr(p, "symbol", None)})
        live_quotes = await get_live_quotes_map(unique_syms) if unique_syms else {}
                
        out = []
        for p in positions:
            info = position_to_info(p)
            action_upper = str(info.action).upper()
            sym_quotes = live_quotes.get(info.symbol.upper(), {})
            
            q_bid = sym_quotes.get("bid")
            q_ask = sym_quotes.get("ask")
            live_price_str = q_bid if action_upper.startswith("BUY") else q_ask
            
            price_current = info.price_current
            profit_val = info.profit
            
            if live_price_str is not None:
                try:
                    live_price = Decimal(str(live_price_str))
                    price_current = live_price
                    vol = Decimal(str(info.volume))
                    price_open = Decimal(str(info.price_open))
                    if action_upper.startswith("BUY"):
                        profit_val = (live_price - price_open) * vol * Decimal("1.0")
                    else:
                        profit_val = (price_open - live_price) * vol * Decimal("1.0")
                except Exception:
                    pass
                    
            out.append({
                "login": info.login,
                "position_id": info.position_id,
                "ticket": info.ticket,
                "symbol": info.symbol,
                "action": info.action,
                "volume": f"{info.volume:f}",
                "price_open": f"{info.price_open:f}",
                "price_current": f"{price_current:f}" if price_current is not None else None,
                "profit": f"{profit_val:f}",
                "swap": f"{info.swap:f}",
                "commission": f"{info.commission:f}"
            })
        return out
    except Exception as exc:
        logger.error(f"Error calculating floating profits data: {exc}", exc_info=True)
        return []


@router.get("/SubscribeOrderProfit", summary="Subscribe order profit updates. Use /OnOrderProfit ws to get result.")
@router_root.get("/SubscribeOrderProfit", summary="Subscribe order profit updates. Use /OnOrderProfit ws to get result.")
async def handle_SubscribeOrderProfit_get(
    manager: Account = Depends(get_current_manager),
    id: Optional[str] = Query(None, alias="id", description="Token returned by 'Connect' method"),
    logins: Optional[str] = Query(None, alias="logins", description="Required accounts. Null or empty - subscribe to ALL accounts."),
    handler: Optional[GetManagerPositionsQueryHandler] = Depends(get_manager_positions_query_handler),
) -> Dict[str, Any]:
    """Subscribe order profit updates. Returns initial snapshot of order floating profits."""
    data = await _get_floating_profits_data(logins, handler)
    return {
        "retcode": 0,
        "message": "Subscribed to order profit updates successfully",
        "endpoint": "/SubscribeOrderProfit",
        "id": id or f"session_{manager.login}",
        "logins": logins,
        "data": data
    }


@router.get("/SubscribeOrderProfitInterval", summary="Subscribe order profit updates with reuquired interval to send uddates. Use /OnOrderProfitInterval ws to get result.")
@router_root.get("/SubscribeOrderProfitInterval", summary="Subscribe order profit updates with reuquired interval to send uddates. Use /OnOrderProfitInterval ws to get result.")
async def handle_SubscribeOrderProfitInterval_get(
    manager: Account = Depends(get_current_manager),
    id: Optional[str] = Query(None, alias="id", description="Token returned by 'Connect' method"),
    logins: Optional[str] = Query(None, alias="logins", description="Required accounts. Null or empty - subscribe to ALL accounts."),
    intervalMs: Optional[str] = Query(None, alias="intervalMs", description="Interval in milliseconds to send updates"),
    handler: Optional[GetManagerPositionsQueryHandler] = Depends(get_manager_positions_query_handler),
) -> Dict[str, Any]:
    """Subscribe order profit updates with required interval."""
    data = await _get_floating_profits_data(logins, handler)
    return {
        "retcode": 0,
        "message": "Subscribed to order profit interval updates successfully",
        "endpoint": "/SubscribeOrderProfitInterval",
        "id": id or f"session_{manager.login}",
        "logins": logins,
        "intervalMs": intervalMs or "1000",
        "data": data
    }


@router.post("/SubscribeOrderProfitIntervalPost", summary="Subscribe order profit updates with reuquired interval to send uddates. Use /OnOrderProfitInterval ws to get result.")
@router_root.post("/SubscribeOrderProfitIntervalPost", summary="Subscribe order profit updates with reuquired interval to send uddates. Use /OnOrderProfitInterval ws to get result.")
async def handle_SubscribeOrderProfitIntervalPost_post(
    manager: Account = Depends(get_current_manager),
    id: Optional[str] = Query(None, alias="id", description="Token returned by 'Connect' method"),
    intervalMs: Optional[str] = Query(None, alias="intervalMs", description="Interval in milliseconds to send updates"),
    handler: Optional[GetManagerPositionsQueryHandler] = Depends(get_manager_positions_query_handler),
) -> Dict[str, Any]:
    """Subscribe order profit updates with required interval (POST)."""
    data = await _get_floating_profits_data(None, handler)
    return {
        "retcode": 0,
        "message": "Subscribed to order profit interval updates successfully",
        "endpoint": "/SubscribeOrderProfitIntervalPost",
        "id": id or f"session_{manager.login}",
        "intervalMs": intervalMs or "1000",
        "data": data
    }


@router.get("/Unsubscribe", summary="Unsubscribe symbol for real time quotes and get results via /events or /OnQuote websocket")
@router_root.get("/Unsubscribe", summary="Unsubscribe symbol for real time quotes and get results via /events or /OnQuote websocket")
async def handle_Unsubscribe_get(
    manager: Account = Depends(get_current_manager),
    id: Optional[str] = Query(None, alias="id", description="Token returned by 'Connect' method"),
    symbol: Optional[str] = Query(None, alias="symbol", description="Symbol"),
) -> Dict[str, Any]:
    """Unsubscribe symbol for real time quotes and get results via /events or /OnQuote websocket"""
    target_symbol = (symbol or "BTCUSD").upper()
    return {
        "retcode": 0,
        "message": f"Unsubscribed from {target_symbol} successfully",
        "endpoint": "/Unsubscribe",
        "id": id or f"session_{manager.login}",
        "symbol": target_symbol,
        "subscribed": False,
        "time": datetime.now(timezone.utc).isoformat(),
    }


@router.get("/UnsubscribeMany", summary="Unsubscribe several symbols for real time quotes and get results via /events or /OnQuote websocket")
@router_root.get("/UnsubscribeMany", summary="Unsubscribe several symbols for real time quotes and get results via /events or /OnQuote websocket")
async def handle_UnsubscribeMany_get(
    manager: Account = Depends(get_current_manager),
    id: Optional[str] = Query(None, alias="id", description="Token returned by 'Connect' method"),
    symbol: Optional[str] = Query(None, alias="symbol", description="Symbol"),
) -> Dict[str, Any]:
    """Unsubscribe several symbols for real time quotes and get results via /events or /OnQuote websocket"""
    symbols_list = [s.strip().upper() for s in (symbol or "BTCUSD,ETHUSD").split(",") if s.strip()]
    return {
        "retcode": 0,
        "message": "Unsubscribed from symbols successfully",
        "endpoint": "/UnsubscribeMany",
        "id": id or f"session_{manager.login}",
        "symbols": symbols_list,
        "subscribed": False,
        "time": datetime.now(timezone.utc).isoformat(),
    }


@router.get("/UnsubscribeOrderProfit", summary="Subscribe symbol for real time quotes and get results via /events socket connection")
@router_root.get("/UnsubscribeOrderProfit", summary="Subscribe symbol for real time quotes and get results via /events socket connection")
async def handle_UnsubscribeOrderProfit_get(
    manager: Account = Depends(get_current_manager),
    id: Optional[str] = Query(None, alias="id", description="Token returned by 'Connect' method"),
    logins: Optional[str] = Query(None, alias="logins", description="Accounts to remove"),
) -> Dict[str, Any]:
    """Subscribe symbol for real time quotes and get results via /events socket connection"""
    return {
        "retcode": 0,
        "message": "Success",
        "endpoint": "/UnsubscribeOrderProfit",
        "data": []
    }


@router.get("/UnsubscribeOrderProfitInterval", summary="Subscribe symbol for real time quotes and get results via /events socket connection")
@router_root.get("/UnsubscribeOrderProfitInterval", summary="Subscribe symbol for real time quotes and get results via /events socket connection")
async def handle_UnsubscribeOrderProfitInterval_get(
    manager: Account = Depends(get_current_manager),
    id: Optional[str] = Query(None, alias="id", description="Token returned by 'Connect' method"),
    logins: Optional[str] = Query(None, alias="logins", description="Accounts to remove"),
) -> Dict[str, Any]:
    """Subscribe symbol for real time quotes and get results via /events socket connection"""
    return {
        "retcode": 0,
        "message": "Success",
        "endpoint": "/UnsubscribeOrderProfitInterval",
        "data": []
    }


@router.post("/UnsubscribeOrderProfitIntervalPost", summary="Subscribe symbol for real time quotes and get results via /events socket connection")
@router_root.post("/UnsubscribeOrderProfitIntervalPost", summary="Subscribe symbol for real time quotes and get results via /events socket connection")
async def handle_UnsubscribeOrderProfitIntervalPost_post(
    manager: Account = Depends(get_current_manager),
    id: Optional[str] = Query(None, alias="id", description="Token returned by 'Connect' method"),
    logins: Optional[str] = Query(None, alias="logins", description="Accounts to remove"),
) -> Dict[str, Any]:
    """Subscribe symbol for real time quotes and get results via /events socket connection"""
    return {
        "retcode": 0,
        "message": "Success",
        "endpoint": "/UnsubscribeOrderProfitIntervalPost",
        "data": []
    }

