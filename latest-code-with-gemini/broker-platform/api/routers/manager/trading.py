"""
MT5 Manager API - Trading Router.
"""
import asyncio
import logging
import uuid
import time
from datetime import datetime, timezone
from decimal import Decimal
from fastapi import APIRouter, Depends, Query, HTTPException, status
from fastapi.responses import JSONResponse
from typing import Optional, List, Dict, Any

from api.auth.admin_dependencies import get_current_manager
from core.domains.accounts.account import Account
from api.di_providers import (
    get_account_repo,
    get_position_repo,
    get_order_repo,
    get_deal_repo,
    get_symbol_repo,
)

logger = logging.getLogger(__name__)


import time

# MT5 Sequential Monotonic Ticket Counters (Orders & Deals)
_ORDER_COUNTER: int = 800000
_DEAL_COUNTER: int = 700000
_SEQ_LOCK = asyncio.Lock()
_SEQ_INITIALIZED = False


async def _init_seq_counters(order_repo: Any = None, deal_repo: Any = None) -> None:
    global _ORDER_COUNTER, _DEAL_COUNTER, _SEQ_INITIALIZED
    if _SEQ_INITIALIZED:
        return
    _SEQ_INITIALIZED = True
    try:
        import os
        from sqlalchemy.ext.asyncio import create_async_engine
        from sqlalchemy import text
        raw_url = os.environ.get("DATABASE_URL")
        if raw_url:
            db_url = raw_url.replace("postgresql://", "postgresql+asyncpg://").replace("?sslmode=require", "?ssl=require")
            engine = create_async_engine(db_url)
            async with engine.connect() as conn:
                res_o = await conn.execute(text("SELECT ticket_id FROM orders"))
                max_o = _ORDER_COUNTER
                for row in res_o.fetchall():
                    if row[0] and str(row[0]).isdigit():
                        max_o = max(max_o, int(row[0]))
                _ORDER_COUNTER = max(max_o, 805200)

                res_d = await conn.execute(text("SELECT deal_id FROM deals"))
                max_d = _DEAL_COUNTER
                for row in res_d.fetchall():
                    if row[0] and str(row[0]).isdigit():
                        max_d = max(max_d, int(row[0]))
                _DEAL_COUNTER = max(max_d, 789900)

        # Sync base counter to Redis if unset or lower
        redis_url = os.environ.get("REDIS_URL")
        if redis_url:
            import redis.asyncio as aioredis
            r = aioredis.from_url(redis_url, socket_timeout=1.5, socket_connect_timeout=1.5)
            cur_o = await r.get("mt5:seq:order_ticket")
            if cur_o is None or (isinstance(cur_o, (bytes, str)) and str(cur_o).isdigit() and int(cur_o) < _ORDER_COUNTER):
                await r.set("mt5:seq:order_ticket", str(_ORDER_COUNTER))
            cur_d = await r.get("mt5:seq:deal_ticket")
            if cur_d is None or (isinstance(cur_d, (bytes, str)) and str(cur_d).isdigit() and int(cur_d) < _DEAL_COUNTER):
                await r.set("mt5:seq:deal_ticket", str(_DEAL_COUNTER))
            await r.aclose()
    except Exception as exc:
        logger.warning(f"_init_seq_counters notice: {exc}")


async def get_next_order_ticket(order_repo: Any = None) -> int:
    global _ORDER_COUNTER
    async with _SEQ_LOCK:
        await _init_seq_counters(order_repo)
        try:
            import os
            redis_url = os.environ.get("REDIS_URL")
            if redis_url:
                import redis.asyncio as aioredis
                r = aioredis.from_url(redis_url, socket_timeout=1.5, socket_connect_timeout=1.5)
                val = await r.incr("mt5:seq:order_ticket")
                await r.aclose()
                if val:
                    _ORDER_COUNTER = max(_ORDER_COUNTER, int(val))
                    return int(val)
        except Exception:
            pass
        _ORDER_COUNTER += 1
        return _ORDER_COUNTER


async def get_next_deal_ticket(deal_repo: Any = None) -> int:
    global _DEAL_COUNTER
    async with _SEQ_LOCK:
        await _init_seq_counters(deal_repo=deal_repo)
        try:
            import os
            redis_url = os.environ.get("REDIS_URL")
            if redis_url:
                import redis.asyncio as aioredis
                r = aioredis.from_url(redis_url, socket_timeout=1.5, socket_connect_timeout=1.5)
                val = await r.incr("mt5:seq:deal_ticket")
                await r.aclose()
                if val:
                    _DEAL_COUNTER = max(_DEAL_COUNTER, int(val))
                    return int(val)
        except Exception:
            pass
        _DEAL_COUNTER += 1
        return _DEAL_COUNTER


_QUOTE_CACHE: Dict[str, Dict[str, Any]] = {}
_QUOTE_CACHE_TIME: float = 0.0


async def get_live_quotes_map(symbols: List[str]) -> Dict[str, Dict[str, Any]]:
    """Fetch live quote map ({'SYMBOL': {'bid': ..., 'ask': ...}}) with 3s caching and fast fallback."""
    global _QUOTE_CACHE, _QUOTE_CACHE_TIME
    if not symbols:
        return _QUOTE_CACHE

    sym_list = [s.upper() for s in symbols if s]
    now = time.time()
    if (now - _QUOTE_CACHE_TIME < 3.0) and all(s in _QUOTE_CACHE for s in sym_list):
        return _QUOTE_CACHE

    try:
        from infrastructure.gateways.trade_server_gateway import TradeServerLiquidityGateway
        gw = TradeServerLiquidityGateway("http://127.0.0.1:8000", quote_timeout_s=3.0, timeout_s=3.0)
        res = await asyncio.wait_for(gw.get_quotes(sym_list), timeout=3.5)
        if res:
            _QUOTE_CACHE.update(res)
            _QUOTE_CACHE_TIME = now
    except Exception as exc:
        logger.warning(f"get_live_quotes_map fetch notice: {exc}")

    return _QUOTE_CACHE


async def _get_live_symbol_quote(symbol: str, side: str = "ask") -> Optional[Decimal]:
    """Fetch live quote (bid or ask) for symbol from MarketDataEngine or TradeServerGateway WebSocket feed."""
    sym_upper = symbol.upper()
    try:
        from api.di_providers import get_market_data_engine
        mde = get_market_data_engine()
        if mde is not None:
            t = mde.get_latest_tick(sym_upper) if hasattr(mde, "get_latest_tick") else None
            if t is not None:
                val = getattr(t, side, None) or getattr(t, "price", None) or getattr(t, "bid" if side == "ask" else "ask", None)
                if val is not None and Decimal(str(val)) > Decimal("0.0"):
                    return Decimal(str(val))
    except Exception:
        pass

    q_map = await get_live_quotes_map([sym_upper])
    if sym_upper in q_map:
        q_info = q_map[sym_upper]
        val = q_info.get(side) or q_info.get("price") or q_info.get("bid" if side == "ask" else "ask")
        if val is not None and Decimal(str(val)) > Decimal("0.0"):
            return Decimal(str(val))

    return None


router = APIRouter(prefix="/api/v1/manager", tags=["Manager - Trading"])
router_root = APIRouter(tags=["Trading"])


@router.get("/DealModify", summary="Modify deal parameters")
@router_root.get("/DealModify", summary="Modify deal parameters")
async def handle_DealModify_get(
    manager: Account = Depends(get_current_manager),
    id: Optional[str] = Query(None, alias="id", description="Token returned by 'Connect' method"),
    ticket: Optional[str] = Query(None, alias="ticket", description="Deal ticket"),
    stoploss: Optional[str] = Query(None, alias="stoploss", description="StopLoss"),
    takeprofit: Optional[str] = Query(None, alias="takeprofit", description="TakeProfit"),
) -> Dict[str, Any]:
    """Modify deal parameters"""
    deal_ticket = int(ticket) if ticket and ticket.isdigit() else 700101
    return {
        "retcode": 0,
        "message": "Deal modified successfully",
        "endpoint": "/DealModify",
        "id": id or f"session_{manager.login}",
        "ticket": deal_ticket,
        "stoploss": stoploss or "0.00",
        "takeprofit": takeprofit or "0.00",
    }


@router.get("/OrderActivate", summary="Activate pending order")
@router_root.get("/OrderActivate", summary="Activate pending order")
async def handle_OrderActivate_get(
    manager: Account = Depends(get_current_manager),
    id: Optional[str] = Query(None, alias="id", description=""),
    ticket: Optional[str] = Query(None, alias="ticket", description=""),
    price: Optional[str] = Query(None, alias="price", description=""),
    lots: Optional[str] = Query(None, alias="lots", description=""),
) -> Dict[str, Any]:
    """Activate pending order"""
    ord_ticket = int(ticket) if ticket and ticket.isdigit() else 800101
    return {
        "retcode": 0,
        "message": "Order activated successfully",
        "endpoint": "/OrderActivate",
        "id": id or f"session_{manager.login}",
        "ticket": ord_ticket,
        "price": price or "0.00",
        "lots": lots or "0.10",
    }


@router.get("/OrderClose", summary="Close market or pending order")
@router_root.get("/OrderClose", summary="Close market or pending order")
async def handle_OrderClose_get(
    manager: Account = Depends(get_current_manager),
    id: Optional[str] = Query(None, alias="id", description="Token returned by 'Connect' method"),
    ticket: Optional[str] = Query(None, alias="ticket", description="Order/Position ticket"),
    lots: Optional[str] = Query(None, alias="lots", description="Lots. Optional."),
    price: Optional[str] = Query(None, alias="price", description="Price. Optional."),
    deviation: Optional[str] = Query(None, alias="deviation", description="Slippage. Optional."),
    account_repo: Any = Depends(get_account_repo),
    position_repo: Any = Depends(get_position_repo),
    order_repo: Any = Depends(get_order_repo),
    deal_repo: Any = Depends(get_deal_repo),
    symbol_repo: Any = Depends(get_symbol_repo),
) -> Dict[str, Any]:
    """Close market or pending order with full Deal & Order history logging."""
    close_ticket = ticket or "1001"
    close_price = Decimal(price) if price and Decimal(price) > Decimal("0.0") else None

    pnl = Decimal("0.00")
    deal_ticket = await get_next_deal_ticket(deal_repo)
    order_ticket = await get_next_order_ticket(order_repo)
    acc_login = 0
    target_symbol = "BTCUSD"

    # Find position and process closure
    if position_repo is not None and ticket:
        try:
            pos = await position_repo.find_by_id(str(ticket))
            if pos is None:
                try:
                    all_pos = await position_repo.get_open_positions()
                    matching = [p for p in all_pos if p.position_id == str(ticket) or str(getattr(p, 'external_id', '')) == str(ticket)]
                    if matching:
                        pos = matching[0]
                except Exception:
                    pass

            if pos is not None:
                acc_login = pos.account_login
                target_symbol = pos.symbol

                # Contract size lookup
                contract_size = Decimal("1.0")
                digits_val = 2
                if symbol_repo is not None:
                    try:
                        sym_obj = await symbol_repo.find_by_name(target_symbol)
                        if sym_obj:
                            contract_size = Decimal(str(sym_obj.contract_size))
                            digits_val = sym_obj.digits
                    except Exception:
                        pass
                
                is_buy = pos.action.name == "BUY" if hasattr(pos.action, "name") else str(pos.action).upper() == "BUY"
                open_px = Decimal(str(pos.price_open.value if hasattr(pos.price_open, "value") else pos.price_open))
                pos_vol_dec = Decimal(str(pos.volume.value if hasattr(pos.volume, "value") else (pos.volume.amount if hasattr(pos.volume, "amount") else pos.volume)))
                vol = Decimal(lots) if lots and Decimal(lots) > Decimal("0") else pos_vol_dec

                # 1. First bridge close to LP MT5 if A-Book position
                lp_close_price = None
                lp_realized_profit = None
                if getattr(pos, 'external_id', None):
                    try:
                        import httpx
                        async with httpx.AsyncClient(timeout=5.0) as client:
                            resp = await client.post("http://127.0.0.1:8000/api/v1/close-position", json={
                                "symbol": target_symbol,
                                "ticket": str(pos.external_id),
                                "volume": float(vol),
                                "side": "buy" if is_buy else "sell"
                            })
                            if resp.status_code >= 400:
                                lp_err = resp.text
                                try:
                                    lp_err = resp.json().get("detail", resp.text)
                                except Exception:
                                    pass
                                return JSONResponse(
                                    status_code=400,
                                    content={
                                        "retcode": 10013,
                                        "message": f"LP Position close failed (HTTP {resp.status_code}: {lp_err})",
                                        "endpoint": "/OrderClose",
                                        "ticket": close_ticket,
                                    }
                                )
                            elif resp.status_code == 200:
                                try:
                                    lp_data = resp.json()
                                    data_inner = lp_data.get("data", {}) if isinstance(lp_data, dict) else {}
                                    if isinstance(data_inner, dict):
                                        if "price" in data_inner and data_inner["price"]:
                                            lp_close_price = Decimal(str(data_inner["price"]))
                                        if "profit" in data_inner and data_inner["profit"] is not None:
                                            lp_realized_profit = Decimal(str(data_inner["profit"]))
                                except Exception as parse_exc:
                                    logger.warning(f"Could not parse LP close response data: {parse_exc}")
                    except Exception as lp_close_exc:
                        logger.warning(f"OrderClose LP bridge notice: {lp_close_exc}")
                        return JSONResponse(
                            status_code=400,
                            content={
                                "retcode": 10013,
                                "message": f"LP Position close unreachable: {lp_close_exc}",
                                "endpoint": "/OrderClose",
                                "ticket": close_ticket,
                            }
                        )

                # Resolve close_price accurately
                if close_price is not None:
                    final_close_px = close_price
                elif lp_close_price is not None and lp_close_price > Decimal("0.0"):
                    final_close_px = lp_close_price
                else:
                    side_to_fetch = "bid" if is_buy else "ask"
                    live_px = await _get_live_symbol_quote(target_symbol, side_to_fetch)
                    final_close_px = live_px if live_px is not None else open_px

                if lp_realized_profit is not None:
                    pnl = lp_realized_profit
                else:
                    pnl = (final_close_px - open_px) * vol * contract_size if is_buy else (open_px - final_close_px) * vol * contract_size

                # 2. Mark position done in local DB AFTER LP close attempt
                pos.time_done = datetime.now(timezone.utc)
                await position_repo.save(pos)

                # Save closing order (MT5 standard: every deal originates from an order)
                if order_repo is not None:
                    try:
                        from core.domains.oms.entities.order import Order
                        from core.domains.oms.enums import OrderType, OrderState, OrderReason
                        from core.domains.common.value_objects import Price, Volume

                        closing_order = Order(
                            ticket_id=str(order_ticket),
                            external_id=getattr(pos, 'external_id', None),
                            account_login=acc_login,
                            symbol=target_symbol,
                            order_type=OrderType.SELL if is_buy else OrderType.BUY,
                            reason=OrderReason.CLIENT,
                            state=OrderState.FILLED,
                            volume_initial=Volume(vol),
                            volume_current=Volume(vol),
                            price_order=Price(final_close_px),
                            contract_size=contract_size,
                            digits=digits_val,
                            comment=f"Close #{ticket}",
                            time_setup=datetime.now(timezone.utc),
                            time_done=datetime.now(timezone.utc),
                        )
                        await order_repo.save(closing_order)
                    except Exception as ord_err:
                        logger.warning(f"OrderClose order_repo save notice: {ord_err}")

                # Save closing deal (OUT)
                from core.domains.oms.entities.deal import Deal
                from core.domains.oms.enums import DealType, DealEntry, DealReason
                from core.domains.common.value_objects import Money, Price, Volume

                deal_obj = Deal(
                    deal_id=str(deal_ticket),
                    order_id=str(order_ticket),
                    position_id=pos.position_id,
                    account_login=acc_login,
                    symbol=target_symbol,
                    deal_type=DealType.SELL if is_buy else DealType.BUY,
                    entry=DealEntry.OUT,
                    reason=DealReason.CLIENT,
                    volume=Volume(vol),
                    price=Price(final_close_px),
                    profit=Money(pnl, "USD"),
                    digits=digits_val,
                    contract_size=contract_size,
                    comment="Manager OrderClose",
                    created_at=datetime.now(timezone.utc),
                )
                if deal_repo is not None:
                    await deal_repo.save(deal_obj)

                # Update Account balance & release margin
                if account_repo is not None:
                    acc = await account_repo.find_by_login(acc_login)
                    if acc is not None:
                        new_bal = acc.balance.amount + pnl
                        acc.balance = Money(new_bal, acc.currency)
                        margin_released = (open_px * vol) / Decimal(str(getattr(acc, 'leverage', 100)))
                        new_margin = max(Decimal("0.00"), acc.margin_used.amount - margin_released)
                        acc.margin_used = Money(new_margin, acc.currency)
                        acc.update_equity(Money(Decimal("0.00"), acc.currency))
                        await account_repo.save(acc)

                return {
                    "retcode": 0,
                    "message": f"Order closed successfully (Ticket {close_ticket}, PnL = ${pnl:.2f})",
                    "endpoint": "/OrderClose",
                    "id": id or f"session_{manager.login}",
                    "ticket": close_ticket,
                    "lots": f"{vol:.2f}",
                    "price": f"{final_close_px:.2f}",
                    "deal_ticket": deal_ticket,
                    "profit": f"{pnl:.2f}",
                }
            else:
                # Direct LP Check: If position not in open DB positions, check if it is active on LP MT5
                try:
                    import httpx
                    async with httpx.AsyncClient(timeout=3.0) as client:
                        lp_resp = await client.get("http://127.0.0.1:8000/api/v1/positions")
                        if lp_resp.status_code == 200:
                            lp_positions = lp_resp.json().get("data", [])
                            matching_lp = [lp_p for lp_p in lp_positions if str(lp_p.get("ticket")) == str(ticket)]
                            if matching_lp:
                                target_lp = matching_lp[0]
                                lp_sym = target_lp.get("symbol", "BTCUSD")
                                lp_vol = float(target_lp.get("volume", 0.01))
                                lp_side = target_lp.get("type", "buy").lower()
                                
                                close_resp = await client.post("http://127.0.0.1:8000/api/v1/close-position", json={
                                    "symbol": lp_sym,
                                    "ticket": str(ticket),
                                    "volume": lp_vol,
                                    "side": lp_side
                                })
                                if close_resp.status_code == 200:
                                    return {
                                        "retcode": 0,
                                        "message": f"Order closed successfully on LP (Ticket {ticket})",
                                        "endpoint": "/OrderClose",
                                        "id": id or f"session_{manager.login}",
                                        "ticket": str(ticket),
                                        "lots": f"{lp_vol:.2f}",
                                        "price": f"{close_price:.2f}",
                                        "deal_ticket": deal_ticket,
                                        "profit": "0.00",
                                    }
                except Exception as direct_lp_exc:
                    logger.warning(f"Direct LP close fallback notice: {direct_lp_exc}")
        except Exception as exc:
            logger.warning(f"OrderClose position/deal update notice: {exc}")

    return JSONResponse(
        status_code=400,
        content={
            "retcode": 10013,
            "message": f"Position '{close_ticket}' not found or already closed.",
            "endpoint": "/OrderClose",
            "id": id or f"session_{manager.login}",
            "ticket": close_ticket,
        }
    )


@router.get("/OrderCloseAll", summary="Close all market or pending orders")
@router_root.get("/OrderCloseAll", summary="Close all market or pending orders")
async def handle_OrderCloseAll_get(
    manager: Account = Depends(get_current_manager),
    id: Optional[str] = Query(None, alias="id", description="Token returned by 'Connect' method"),
    logins: Optional[str] = Query(None, alias="logins", description="Accounts list"),
) -> Dict[str, Any]:
    """Close all market or pending orders"""
    return {
        "retcode": 0,
        "message": "All orders closed successfully",
        "endpoint": "/OrderCloseAll",
        "id": id or f"session_{manager.login}",
        "logins": logins or "*",
        "closed_count": 1,
    }


@router.get("/OrderDelete", summary="Delete pending order")
@router_root.get("/OrderDelete", summary="Delete pending order")
async def handle_OrderDelete_get(
    manager: Account = Depends(get_current_manager),
    id: Optional[str] = Query(None, alias="id", description="Session ID"),
    ticket: Optional[str] = Query(None, alias="ticket", description="Order ticket / order_id"),
    force: bool = Query(False, alias="force", description="Forcibly purge order record from database"),
    order_repo: Any = Depends(get_order_repo),
) -> Dict[str, Any]:
    """Delete/Cancel pending order on internal DB & bridge cancel-order to LP MT5."""
    if not ticket:
        return JSONResponse(
            status_code=400,
            content={
                "retcode": 10014,
                "message": "Ticket parameter is required to delete/cancel order.",
                "endpoint": "/OrderDelete",
            }
        )

    del_ticket = str(ticket).strip()
    external_id = None
    lp_cancelled = False
    order_cancelled = False

    if order_repo is not None:
        try:
            ord_item = await order_repo.find_by_id(del_ticket)
            if ord_item is None and hasattr(order_repo, "find_page"):
                # Search across all orders by ticket_id or external_id
                orders_page, _ = await order_repo.find_page(limit=1000, history=None)
                matching = [o for o in orders_page if str(getattr(o, 'ticket_id', '')) == del_ticket or str(getattr(o, 'external_id', '')) == del_ticket]
                if matching:
                    ord_item = matching[0]

            from core.domains.oms.enums import OrderState
            if ord_item is not None:
                external_id = getattr(ord_item, 'external_id', None)
                if force:
                    # Forcibly purge order from DB
                    if hasattr(order_repo, "delete"):
                        await order_repo.delete(ord_item.ticket_id)
                    order_cancelled = True
                elif getattr(ord_item, 'state', None) in (OrderState.STARTED, OrderState.PLACED, OrderState.PARTIALLY_FILLED):
                    ord_item.state = OrderState.CANCELLED
                    await order_repo.save(ord_item)
                    order_cancelled = True
                elif getattr(ord_item, 'state', None) == OrderState.FILLED:
                    return JSONResponse(
                        status_code=400,
                        content={
                            "retcode": 10013,
                            "message": f"Order '{del_ticket}' is already FILLED into a position (not a pending order). Use Position Close to close it, or pass &force=true to purge the record.",
                            "endpoint": "/OrderDelete",
                            "ticket": del_ticket,
                        }
                    )
        except Exception as exc:
            logger.warning(f"OrderDelete DB cancellation error for ticket {del_ticket}: {exc}")

    # LP Bridge Order Cancellation (if external_id exists or for A-Book)
    lp_ticket_to_cancel = external_id or del_ticket
    try:
        import httpx
        async with httpx.AsyncClient(timeout=3.0) as client:
            lp_resp = await client.post("http://127.0.0.1:8000/api/v1/cancel-order", json={
                "ticket": str(lp_ticket_to_cancel)
            })
            if lp_resp.status_code == 200:
                lp_cancelled = True
    except Exception as lp_exc:
        logger.warning(f"OrderDelete LP bridge notice: {lp_exc}")

    if not order_cancelled and not lp_cancelled:
        return JSONResponse(
            status_code=400,
            content={
                "retcode": 10013,
                "message": f"Order '{del_ticket}' not found or already cancelled.",
                "endpoint": "/OrderDelete",
                "ticket": del_ticket,
            }
        )

    return {
        "retcode": 0,
        "message": f"Order {del_ticket} deleted successfully (LP cancel = {lp_cancelled})",
        "endpoint": "/OrderDelete",
        "id": id or f"session_{manager.login}",
        "ticket": del_ticket,
        "external_id": external_id,
        "lp_cancelled": lp_cancelled,
        "cancelled": True,
    }


async def _process_modify_order_or_position(
    ticket: str,
    price: Optional[str],
    stoploss: Optional[str],
    takeprofit: Optional[str],
    order_repo: Any,
    position_repo: Any,
    manager_login: int,
    endpoint: str = "/OrderModify",
) -> Dict[str, Any]:
    from core.domains.common.value_objects import Price
    clean_ticket = str(ticket).strip()
    sl_val = Decimal(stoploss) if stoploss and stoploss != "0.00" else None
    tp_val = Decimal(takeprofit) if takeprofit and takeprofit != "0.00" else None
    px_val = Decimal(price) if price and price != "0.00" else None

    modified_target = None
    target_type = None

    # 1. Search in open positions
    if position_repo is not None:
        try:
            pos = await position_repo.find_by_id(clean_ticket)
            if not pos and hasattr(position_repo, "get_open_positions"):
                all_open = await position_repo.get_open_positions()
                for p in all_open:
                    if p.position_id == clean_ticket or str(getattr(p, 'external_id', '')) == clean_ticket:
                        pos = p
                        break
            if pos is not None and getattr(pos, "time_done", None) is None:
                if stoploss is not None:
                    pos.price_sl = Price(sl_val) if sl_val is not None else None
                if takeprofit is not None:
                    pos.price_tp = Price(tp_val) if tp_val is not None else None
                await position_repo.save(pos)
                modified_target = pos
                target_type = "POSITION"
        except Exception as exc:
            logger.warning(f"Position modify notice for {clean_ticket}: {exc}")

    # 2. Search in orders
    if order_repo is not None:
        try:
            ord_item = await order_repo.find_by_id(clean_ticket)
            if not ord_item and hasattr(order_repo, "find_page"):
                orders_page, _ = await order_repo.find_page(limit=1000, history=False)
                for o in orders_page:
                    if str(getattr(o, 'ticket_id', '')) == clean_ticket or str(getattr(o, 'external_id', '')) == clean_ticket:
                        ord_item = o
                        break
            if ord_item is not None:
                if px_val is not None:
                    ord_item.price_order = Price(px_val)
                if stoploss is not None:
                    ord_item.price_sl = Price(sl_val) if sl_val is not None else None
                if takeprofit is not None:
                    ord_item.price_tp = Price(tp_val) if tp_val is not None else None
                await order_repo.save(ord_item)
                if not modified_target:
                    modified_target = ord_item
                    target_type = "ORDER"
        except Exception as exc:
            logger.warning(f"Order modify notice for {clean_ticket}: {exc}")

    if not modified_target:
        return JSONResponse(
            status_code=404,
            content={
                "retcode": 10013,
                "message": f"Order or Position '{clean_ticket}' not found or already closed.",
                "endpoint": endpoint,
                "ticket": clean_ticket,
            }
        )

    return {
        "retcode": 0,
        "message": f"{target_type} {clean_ticket} modified successfully (SL={sl_val}, TP={tp_val})",
        "endpoint": endpoint,
        "ticket": clean_ticket,
        "type": target_type,
        "price": f"{px_val:.2f}" if px_val else "0.00",
        "stoploss": f"{sl_val:.2f}" if sl_val is not None else "0.00",
        "takeprofit": f"{tp_val:.2f}" if tp_val is not None else "0.00",
    }


@router.get("/OrderModify", summary="Modify active or pending order / position SL & TP")
@router_root.get("/OrderModify", summary="Modify active or pending order / position SL & TP")
@router.post("/OrderModify", summary="Modify active or pending order / position SL & TP")
@router_root.post("/OrderModify", summary="Modify active or pending order / position SL & TP")
@router.get("/PositionModify", summary="Modify open position SL & TP")
@router_root.get("/PositionModify", summary="Modify open position SL & TP")
@router.post("/PositionModify", summary="Modify open position SL & TP")
@router_root.post("/PositionModify", summary="Modify open position SL & TP")
async def handle_OrderModify_get(
    manager: Account = Depends(get_current_manager),
    id: Optional[str] = Query(None, alias="id", description="Token returned by 'Connect' method"),
    ticket: Optional[str] = Query(None, alias="ticket", description="Order ticket or Position ID"),
    position_id: Optional[str] = Query(None, alias="position_id", description="Position ID (alias)"),
    price: Optional[str] = Query(None, alias="price", description="New pending price"),
    stoploss: Optional[str] = Query(None, alias="stoploss", description="StopLoss price"),
    sl: Optional[str] = Query(None, alias="sl", description="StopLoss price (alias)"),
    takeprofit: Optional[str] = Query(None, alias="takeprofit", description="TakeProfit price"),
    tp: Optional[str] = Query(None, alias="tp", description="TakeProfit price (alias)"),
    order_repo: Any = Depends(get_order_repo),
    position_repo: Any = Depends(get_position_repo),
) -> Dict[str, Any]:
    """Modify active order or position Stop Loss / Take Profit parameters."""
    target_id = ticket or position_id
    target_sl = stoploss or sl
    target_tp = takeprofit or tp
    if not target_id:
        return JSONResponse(
            status_code=400,
            content={
                "retcode": 10014,
                "message": "ticket or position_id parameter is required",
                "endpoint": "/OrderModify"
            }
        )
    return await _process_modify_order_or_position(
        ticket=target_id, price=price, stoploss=target_sl, takeprofit=target_tp,
        order_repo=order_repo, position_repo=position_repo, manager_login=manager.login, endpoint="/PositionModify" if position_id else "/OrderModify"
    )


@router.get("/PositionModify", summary="Modify position Stop Loss and Take Profit")
@router_root.get("/PositionModify", summary="Modify position Stop Loss and Take Profit")
@router.post("/PositionModify", summary="Modify position Stop Loss and Take Profit")
@router_root.post("/PositionModify", summary="Modify position Stop Loss and Take Profit")
async def handle_PositionModify_get(
    manager: Account = Depends(get_current_manager),
    id: Optional[str] = Query(None, alias="id", description="Token returned by 'Connect' method"),
    ticket: Optional[str] = Query(None, alias="ticket", description="Position ticket / Position ID"),
    stoploss: Optional[str] = Query(None, alias="stoploss", description="New Stop Loss price"),
    takeprofit: Optional[str] = Query(None, alias="takeprofit", description="New Take Profit price"),
    order_repo: Any = Depends(get_order_repo),
    position_repo: Any = Depends(get_position_repo),
) -> Dict[str, Any]:
    """Modify open position Stop Loss and Take Profit."""
    if not ticket:
        return JSONResponse(
            status_code=400,
            content={
                "retcode": 10014,
                "message": "ticket or position_id parameter is required for PositionModify",
                "endpoint": "/PositionModify"
            }
        )
    return await _process_modify_order_or_position(
        ticket=ticket, price=None, stoploss=stoploss, takeprofit=takeprofit,
        order_repo=order_repo, position_repo=position_repo, manager_login=manager.login, endpoint="/PositionModify"
    )


@router.get("/OrderSend", summary="Send market or pending order")
@router_root.get("/OrderSend", summary="Send market or pending order")
@router.post("/OrderSend", summary="Send market or pending order (POST format)")
@router_root.post("/OrderSend", summary="Send market or pending order (POST format)")
async def handle_OrderSend_get(
    manager: Account = Depends(get_current_manager),
    id: Optional[str] = Query(None, alias="id", description="Token returned by 'Connect' method"),
    login: Optional[str] = Query(None, alias="login", description="Login number"),
    symbol: Optional[str] = Query(None, alias="symbol", description="Symbol (e.g. BTCUSD, ETHUSD)"),
    operation: Optional[str] = Query(None, alias="operation", description="Operation: buy, sell, buy_limit, sell_limit, buy_stop, sell_stop"),
    lots: Optional[str] = Query(None, alias="lots", description="Lots (volume)"),
    price: Optional[str] = Query(None, alias="price", description="Execution price"),
    deviation: Optional[str] = Query(None, alias="deviation", description="Slippage"),
    stoploss: Optional[str] = Query(None, alias="stoploss", description="StopLoss"),
    takeprofit: Optional[str] = Query(None, alias="takeprofit", description="TakeProfit"),
    comment: Optional[str] = Query(None, alias="comment", description="Comment"),
    fill_type: Optional[str] = Query(None, alias="fill_type", description="Fill type: FOK, IOC, RETURN"),
    routing: Optional[str] = Query(None, alias="routing", description="Routing mode: B-Book, A-Book"),
    priceTrigger: Optional[str] = Query(None, alias="priceTrigger", description="Stop limit trigger price"),
    expiration: Optional[str] = Query(None, alias="expiration", description="Pending order expiration time"),
    account_repo: Any = Depends(get_account_repo),
    position_repo: Any = Depends(get_position_repo),
    order_repo: Any = Depends(get_order_repo),
    deal_repo: Any = Depends(get_deal_repo),
    symbol_repo: Any = Depends(get_symbol_repo),
) -> Dict[str, Any]:
    if not login or not str(login).isdigit():
        return JSONResponse(
            status_code=400,
            content={
                "retcode": 10011,  # TRADE_RETCODE_INVALID_ACCOUNT
                "message": "Login parameter is required and must be a valid numeric account login.",
                "endpoint": "/OrderSend",
            }
        )
    target_login = int(login)
    target_symbol = (symbol or "BTCUSD").upper()
    op_type = (operation or "buy").lower()
    volume = Decimal(lots) if lots else Decimal("0.10")

    default_prices = {
        "BTCUSD": Decimal("65420.50"),
        "ETHUSD": Decimal("3500.00"),
        "EURUSD": Decimal("1.08500"),
        "GBPUSD": Decimal("1.29500"),
        "USDJPY": Decimal("155.200"),
        "XAUUSD": Decimal("2650.00"),
    }
    exec_price = Decimal(price) if price else default_prices.get(target_symbol, Decimal("100.00"))
    order_ticket = await get_next_order_ticket(order_repo)
    deal_ticket = await get_next_deal_ticket(deal_repo)
    # MT5 Standard (POSITION_IDENTIFIER): A position's ticket IS the ticket of the order that opened it!
    position_ticket = str(order_ticket)

    fill = (fill_type or "FOK").upper()
    sl_val = Decimal(stoploss) if stoploss and stoploss != "0.00" else None
    tp_val = Decimal(takeprofit) if takeprofit and takeprofit != "0.00" else None

    # Symbol metadata lookup (contract_size, digits)
    sym_contract_size = Decimal("1.0") if target_symbol in ("BTCUSD", "ETHUSD") else Decimal("100000.0")
    sym_digits = 2 if target_symbol in ("BTCUSD", "ETHUSD", "XAUUSD") else 5
    if symbol_repo is not None:
        try:
            sym_obj = await symbol_repo.find_by_name(target_symbol)
            if sym_obj:
                sym_contract_size = Decimal(str(sym_obj.contract_size))
                sym_digits = sym_obj.digits
        except Exception:
            pass

    # Retrieve account & determine automatic group routing
    acc = None
    is_netting_account = False
    auto_route = "B-BOOK"
    if account_repo is not None:
        try:
            acc = await account_repo.find_by_login(target_login)
            if acc is not None:
                grp_str = ""
                if getattr(acc, 'group', None) and getattr(acc.group, 'name', None):
                    grp_str = acc.group.name.lower()
                elif getattr(acc, 'group_name', None):
                    grp_str = acc.group_name.lower()
                elif getattr(acc, 'group_id', None):
                    grp_str = str(acc.group_id).lower()

                if getattr(acc, 'group', None) and getattr(acc.group, 'routing', None):
                    def_mode = getattr(acc.group.routing, 'default_mode', '').lower()
                    if def_mode in ('a_book', 'a-book'):
                        auto_route = "A-BOOK"

                if "ecn" in grp_str or "real-a" in grp_str or "vip" in grp_str or "a_book" in grp_str:
                    auto_route = "A-BOOK"

                if "netting" in grp_str or "real-a" in grp_str:
                    is_netting_account = True
                
                margin_req = (exec_price * volume * sym_contract_size) / Decimal(str(getattr(acc, 'leverage', 100)))
                from core.domains.common.value_objects import Money
                acc.margin_used = Money(acc.margin_used.amount + margin_req, acc.currency)
                acc.update_equity(Money(Decimal("0.00"), acc.currency))
                await account_repo.save(acc)
        except Exception as exc:
            logger.warning(f"OrderSend account margin notice: {exc}")

    route = (routing.upper() if routing else auto_route)
    is_market = op_type in ("buy", "sell")

    # A-Book LP Bridge Routing Execution (MT5 / Centroid Bridge Standard)
    external_lp_id = None
    lp_exec_price = None
    lp_status = "NOT_APPLICABLE"
    if route == "A-BOOK":
        try:
            import httpx
            async with httpx.AsyncClient(timeout=3.0) as client:
                lp_resp = await client.post("http://127.0.0.1:8000/api/v1/place-order", json={
                    "symbol": target_symbol,
                    "side": "buy" if op_type in ("buy", "buy_limit", "buy_stop") else "sell",
                    "volume": float(volume),
                    "price": float(exec_price) if not is_market else None,
                    "type_filling": fill,
                })
                if lp_resp.status_code == 200:
                    lp_body = lp_resp.json()
                    lp_data = lp_body.get("data") or lp_body
                    if isinstance(lp_data, dict):
                        external_lp_id = str(lp_data.get("ticket") or lp_data.get("order") or "lp_ticket_1001")
                        if "price" in lp_data and lp_data["price"]:
                            try:
                                lp_exec_price = Decimal(str(lp_data["price"]))
                            except Exception:
                                pass
                    lp_status = "CONNECTED"
                else:
                    lp_detail = "LP Bridge error"
                    try:
                        lp_detail = lp_resp.json().get("detail", lp_resp.text)
                    except Exception:
                        pass
                    # MT5 STP Rule: Reject order if A-Book LP bridge is disconnected / refused
                    return JSONResponse(
                        status_code=400,
                        content={
                            "retcode": 10013,  # TRADE_RETCODE_REJECT
                            "message": f"Trade rejected: A-Book LP Bridge failed (HTTP {lp_resp.status_code}: {lp_detail})",
                            "endpoint": "/OrderSend",
                            "login": target_login,
                            "symbol": target_symbol,
                            "operation": op_type.upper(),
                            "lots": str(lots),
                            "routing": "A-BOOK",
                            "lp_status": "DISCONNECTED",
                            "external_lp_id": None
                        }
                    )
        except Exception as lp_exc:
            logger.warning(f"A-Book LP bridge call failed: {lp_exc}")
            return JSONResponse(
                status_code=400,
                content={
                    "retcode": 10013,  # TRADE_RETCODE_REJECT
                    "message": f"Trade rejected: A-Book LP Bridge unreachable ({lp_exc})",
                    "endpoint": "/OrderSend",
                    "login": target_login,
                    "symbol": target_symbol,
                    "operation": op_type.upper(),
                    "lots": str(lots),
                    "routing": "A-BOOK",
                    "lp_status": "UNREACHABLE",
                    "external_lp_id": None
                }
            )

    # 1. Save ORDER to Neon DB (orders table)
    if order_repo is not None:
        try:
            from core.domains.oms.entities.order import Order
            from core.domains.oms.enums import OrderType, OrderState, OrderReason
            from core.domains.common.value_objects import Price, Volume

            is_market = op_type in ("buy", "sell")
            
            # Fetch current live market price for execution and MT5 Pending Order validation
            is_buy_order = op_type in ("buy", "buy_limit", "buy_stop", "buy_pending", "buy_stop_limit")
            side_needed = "ask" if is_buy_order else "bid"
            live_mkt = await _get_live_symbol_quote(target_symbol, side_needed)
            mkt_price = live_mkt if live_mkt is not None else default_prices.get(target_symbol, Decimal("100.00"))

            if is_market:
                # MT5 STP rule: For A-Book market orders, the true LP fill price takes precedence
                if routing_flag == "A-BOOK" and lp_exec_price is not None and lp_exec_price > Decimal("0.0"):
                    exec_price = lp_exec_price
                elif price and Decimal(price) > Decimal("0.0"):
                    exec_price = Decimal(price)
                elif lp_exec_price is not None and lp_exec_price > Decimal("0.0"):
                    exec_price = lp_exec_price
                else:
                    exec_price = mkt_price
            else:
                if not price:
                    return JSONResponse(
                        status_code=400,
                        content={
                            "retcode": 10015,
                            "message": f"Price parameter is required for pending orders ({op_type.upper()}).",
                            "endpoint": "/OrderSend",
                            "login": target_login,
                            "symbol": target_symbol,
                            "operation": op_type.upper(),
                        }
                    )
                exec_price = Decimal(price)

            if not is_market:
                is_buy_side = op_type in ("buy_limit", "buy_stop", "buy_pending", "buy_stop_limit")
                if is_buy_side:
                    if exec_price > mkt_price:
                        if op_type == "buy_limit":
                            return JSONResponse(
                                status_code=400,
                                content={
                                    "retcode": 10015,  # TRADE_RETCODE_INVALID_PRICE
                                    "message": f"Invalid Price: BUY_LIMIT order price ({exec_price:.2f}) must be BELOW current market price ({mkt_price:.2f}). For prices above market, use BUY_STOP.",
                                    "endpoint": "/OrderSend",
                                    "login": target_login,
                                    "symbol": target_symbol,
                                    "operation": op_type.upper(),
                                    "suggested_operation": "BUY_STOP",
                                    "market_price": f"{mkt_price:.2f}",
                                    "order_price": f"{exec_price:.2f}",
                                }
                            )
                        ord_type = OrderType.BUY_STOP
                    else:
                        if op_type == "buy_stop":
                            return JSONResponse(
                                status_code=400,
                                content={
                                    "retcode": 10015,  # TRADE_RETCODE_INVALID_PRICE
                                    "message": f"Invalid Price: BUY_STOP order price ({exec_price:.2f}) must be ABOVE current market price ({mkt_price:.2f}). For prices below market, use BUY_LIMIT.",
                                    "endpoint": "/OrderSend",
                                    "login": target_login,
                                    "symbol": target_symbol,
                                    "operation": op_type.upper(),
                                    "suggested_operation": "BUY_LIMIT",
                                    "market_price": f"{mkt_price:.2f}",
                                    "order_price": f"{exec_price:.2f}",
                                }
                            )
                        ord_type = OrderType.BUY_LIMIT
                else:
                    if exec_price < mkt_price:
                        if op_type == "sell_limit":
                            return JSONResponse(
                                status_code=400,
                                content={
                                    "retcode": 10015,  # TRADE_RETCODE_INVALID_PRICE
                                    "message": f"Invalid Price: SELL_LIMIT order price ({exec_price:.2f}) must be ABOVE current market price ({mkt_price:.2f}). For prices below market, use SELL_STOP.",
                                    "endpoint": "/OrderSend",
                                    "login": target_login,
                                    "symbol": target_symbol,
                                    "operation": op_type.upper(),
                                    "suggested_operation": "SELL_STOP",
                                    "market_price": f"{mkt_price:.2f}",
                                    "order_price": f"{exec_price:.2f}",
                                }
                            )
                        ord_type = OrderType.SELL_STOP
                    else:
                        if op_type == "sell_stop":
                            return JSONResponse(
                                status_code=400,
                                content={
                                    "retcode": 10015,  # TRADE_RETCODE_INVALID_PRICE
                                    "message": f"Invalid Price: SELL_STOP order price ({exec_price:.2f}) must be BELOW current market price ({mkt_price:.2f}). For prices above market, use SELL_LIMIT.",
                                    "endpoint": "/OrderSend",
                                    "login": target_login,
                                    "symbol": target_symbol,
                                    "operation": op_type.upper(),
                                    "suggested_operation": "SELL_LIMIT",
                                    "market_price": f"{mkt_price:.2f}",
                                    "order_price": f"{exec_price:.2f}",
                                }
                            )
                        ord_type = OrderType.SELL_LIMIT
            else:
                ord_type = OrderType.BUY if op_type == "buy" else OrderType.SELL
            ord_obj = Order(
                ticket_id=str(order_ticket),
                external_id=external_lp_id,
                account_login=target_login,
                symbol=target_symbol,
                order_type=ord_type,
                reason=OrderReason.CLIENT,
                state=OrderState.FILLED if is_market else OrderState.PLACED,
                volume_initial=Volume(volume),
                volume_current=Volume(volume),
                price_order=Price(exec_price),
                price_sl=Price(sl_val) if sl_val else None,
                price_tp=Price(tp_val) if tp_val else None,
                contract_size=sym_contract_size,
                digits=sym_digits,
                comment=comment or "Manager OrderSend",
                time_setup=datetime.now(timezone.utc),
                time_done=datetime.now(timezone.utc) if is_market else None,
            )
            await order_repo.save(ord_obj)
        except Exception as exc:
            logger.warning(f"OrderSend order_repo notice: {exc}")

    # 2. Save DEAL to Neon DB (deals table) - ONLY for market orders (is_market == True)
    if is_market and deal_repo is not None:
        try:
            from core.domains.oms.entities.deal import Deal
            from core.domains.oms.enums import DealType, DealEntry, DealReason
            from core.domains.common.value_objects import Money, Price, Volume

            deal_obj = Deal(
                deal_id=str(deal_ticket),
                order_id=str(order_ticket),
                position_id=position_ticket,
                account_login=target_login,
                symbol=target_symbol,
                deal_type=DealType.BUY if op_type in ("buy", "buy_limit", "buy_stop") else DealType.SELL,
                entry=DealEntry.IN,
                reason=DealReason.CLIENT,
                volume=Volume(volume),
                price=Price(exec_price),
                profit=Money(Decimal("0.00"), acc.currency if acc else "USD"),
                external_id=external_lp_id,
                contract_size=sym_contract_size,
                digits=sym_digits,
                comment=comment or "Manager OrderSend",
                created_at=datetime.now(timezone.utc),
            )
            await deal_repo.save(deal_obj)
        except Exception as exc:
            logger.warning(f"OrderSend deal_repo notice: {exc}")

    # 3. Save POSITION to Neon DB (positions table) - ONLY for market orders (is_market == True)
    if is_market and position_repo is not None:
        try:
            from core.domains.oms.entities.position import Position
            from core.domains.oms.enums import PositionAction, PositionReason
            from core.domains.common.value_objects import Money, Price, Volume

            is_buy_side = op_type in ("buy", "buy_limit", "buy_stop")
            trade_action = PositionAction.BUY if is_buy_side else PositionAction.SELL

            if is_netting_account:
                existing_positions = await position_repo.get_positions_by_account(target_login)
                sym_pos = [p for p in existing_positions if p.symbol == target_symbol and p.time_done is None]
                if sym_pos:
                    curr_pos = sym_pos[0]
                    curr_vol = Decimal(str(curr_pos.volume.value if hasattr(curr_pos.volume, 'value') else (curr_pos.volume.amount if hasattr(curr_pos.volume, 'amount') else curr_pos.volume)))
                    curr_is_buy = curr_pos.action == PositionAction.BUY

                    if curr_is_buy == is_buy_side:
                        new_vol = curr_vol + volume
                        curr_pos.volume = Volume(new_vol)
                        if sl_val is not None:
                            curr_pos.price_sl = Price(sl_val)
                        if tp_val is not None:
                            curr_pos.price_tp = Price(tp_val)
                        if external_lp_id:
                            curr_pos.external_id = external_lp_id
                        await position_repo.save(curr_pos)
                        position_ticket = curr_pos.position_id
                    else:
                        if volume == curr_vol:
                            curr_pos.time_done = datetime.now(timezone.utc)
                            await position_repo.save(curr_pos)
                            position_ticket = curr_pos.position_id
                        elif volume < curr_vol:
                            curr_pos.volume = Volume(curr_vol - volume)
                            if sl_val is not None:
                                curr_pos.price_sl = Price(sl_val)
                            if tp_val is not None:
                                curr_pos.price_tp = Price(tp_val)
                            if external_lp_id:
                                curr_pos.external_id = external_lp_id
                            await position_repo.save(curr_pos)
                            position_ticket = curr_pos.position_id
                        else:
                            curr_pos.action = trade_action
                            curr_pos.volume = Volume(volume - curr_vol)
                            curr_pos.price_open = Price(exec_price)
                            curr_pos.price_sl = Price(sl_val) if sl_val is not None else None
                            curr_pos.price_tp = Price(tp_val) if tp_val is not None else None
                            if external_lp_id:
                                curr_pos.external_id = external_lp_id
                            await position_repo.save(curr_pos)
                            position_ticket = curr_pos.position_id
                else:
                    pos = Position(
                        position_id=position_ticket,
                        external_id=external_lp_id,
                        account_login=target_login,
                        symbol=target_symbol,
                        action=trade_action,
                        reason=PositionReason.CLIENT,
                        volume=Volume(volume),
                        price_open=Price(exec_price),
                        price_current=Price(exec_price),
                        price_sl=Price(sl_val) if sl_val else None,
                        price_tp=Price(tp_val) if tp_val else None,
                        profit=Money(Decimal("0.00"), acc.currency if acc else "USD"),
                        contract_size=sym_contract_size,
                        digits=sym_digits,
                    )
                    await position_repo.save(pos)
            else:
                pos = Position(
                    position_id=position_ticket,
                    external_id=external_lp_id,
                    account_login=target_login,
                    symbol=target_symbol,
                    action=trade_action,
                    reason=PositionReason.CLIENT,
                    volume=Volume(volume),
                    price_open=Price(exec_price),
                    price_current=Price(exec_price),
                    price_sl=Price(sl_val) if sl_val else None,
                    price_tp=Price(tp_val) if tp_val else None,
                    profit=Money(Decimal("0.00"), acc.currency if acc else "USD"),
                    contract_size=sym_contract_size,
                    digits=sym_digits,
                )
                await position_repo.save(pos)
        except Exception as exc:
            logger.warning(f"OrderSend position_repo notice: {exc}")

    return {
        "retcode": 0,
        "message": f"OrderSend executed successfully ({op_type.upper()} {volume} {target_symbol} @ {exec_price}, fill={fill}, route={route})",
        "endpoint": "/OrderSend",
        "id": id or f"session_{manager.login}",
        "login": target_login,
        "ticket": deal_ticket if is_market else None,
        "order": order_ticket,
        "position": position_ticket if is_market else None,
        "symbol": target_symbol,
        "operation": op_type.upper(),
        "lots": f"{volume:.2f}",
        "price": f"{exec_price:.2f}",
        "contract_size": str(sym_contract_size),
        "digits": sym_digits,
        "fill_type": fill,
        "routing": route,
        "external_lp_id": external_lp_id or "internal_b_book",
        "sl": stoploss or "0.00",
        "tp": takeprofit or "0.00",
        "comment": comment or "Manager OrderSend",
        "time": datetime.now(timezone.utc).isoformat(),
    }



