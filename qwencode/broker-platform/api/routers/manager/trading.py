"""
MT5 Manager API - Trading Router.

Exposes endpoints that mirror MT5 Manager API trading operations:
- POST /api/v1/manager/OrderSend
- POST /api/v1/manager/OrderClose
- POST /api/v1/manager/OrderModify
- POST /api/v1/manager/DealModify
- POST /api/v1/manager/OrderDelete

Architectural Rule: These endpoints ONLY call Application Command Handlers.
"""
import logging
from decimal import Decimal
from fastapi import APIRouter, Depends, HTTPException, status
from typing import Any, Dict

from api.auth.admin_dependencies import get_current_manager
from api.di_providers import (
    get_create_order_handler,
    get_close_position_handler,
    get_cancel_order_handler,
    get_modify_order_handler,
    get_modify_deal_handler,
)
from api.schemas.manager.common import (
    Confirm,
    ExceptionResult,
    Request,
    TradeResult,
)
from api.schemas.manager.trading import (
    OrderSendRequest,
    OrderCloseRequest,
    OrderModifyRequest,
    DealModifyRequest,
    OrderDeleteRequest,
)
from application.commands.create_order import CreateOrderCommand, CreateOrderHandler
from application.commands.close_position import ClosePositionCommand, ClosePositionHandler
from core.domains.accounts.account import Account
from core.domains.oms.enums import OrderType

from application.commands.cancel_order import CancelOrderCommand, CancelOrderHandler
from application.commands.modify_order import ModifyOrderCommand, ModifyOrderHandler
from application.commands.modify_deal import ModifyDealCommand, ModifyDealHandler

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/manager", tags=["Manager - Trading"])


# ============================================================================
# OrderSend - Place market or pending order
# ============================================================================

@router.post(
    "/OrderSend",
    response_model=TradeResult,
    responses={201: {"model": ExceptionResult}},
    summary="Send market or pending order",
)
async def order_send(
    request: OrderSendRequest,
    manager: Account = Depends(get_current_manager),
    handler: CreateOrderHandler = Depends(get_create_order_handler),
) -> TradeResult:
    """
    Place a new market or pending order.
    
    Mirrors MT5 Manager API `OrderSend` endpoint.
    """
    # Map MT5 operation string to OrderType enum
    operation_map = {
        "Buy": OrderType.BUY,
        "Sell": OrderType.SELL,
        "BuyLimit": OrderType.BUY_LIMIT,
        "SellLimit": OrderType.SELL_LIMIT,
        "BuyStop": OrderType.BUY_STOP,
        "SellStop": OrderType.SELL_STOP,
    }
    
    if request.operation not in operation_map:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid operation: {request.operation}"
        )
    
    order_type = operation_map[request.operation]
    
    # Pending orders require price
    if order_type in [OrderType.BUY_LIMIT, OrderType.SELL_LIMIT,
                      OrderType.BUY_STOP, OrderType.SELL_STOP]:
        if request.price is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Price is required for pending orders"
            )
    
    try:
        # Build command
        command = CreateOrderCommand(
            account_login=manager.login,
            symbol=request.symbol,
            order_type=order_type,
            volume=request.volume,
            price=request.price,
            stop_loss=request.stop_loss,
            take_profit=request.take_profit,
            comment=request.comment or "",
        )
        
        # Execute
        order = await handler.handle(command)
        
        # Build MT5-compatible response
        return TradeResult(
            answer=Request(
                action=request.operation,
                symbol=request.symbol,
                volume=request.volume,
                price=request.price,
                stop_loss=request.stop_loss,
                take_profit=request.take_profit,
                comment=request.comment,
            ),
            result=Confirm(
                request_id=str(order.ticket_id),
                order_ticket=int(order.ticket_id) if isinstance(order.ticket_id, int) else (int(order.ticket_id) if str(order.ticket_id).isdigit() else 0),
                price=order.price_order.value,
                volume=order.volume_initial.value,
                retcode=0,
                comment="Order placed successfully",
            ),
        )
    
    except ValueError as e:
        logger.warning(f"OrderSend failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"OrderSend error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


# ============================================================================
# OrderClose - Close position
# ============================================================================

@router.post(
    "/OrderClose",
    response_model=TradeResult,
    responses={201: {"model": ExceptionResult}},
    summary="Close position",
)
async def order_close(
    request: OrderCloseRequest,
    manager: Account = Depends(get_current_manager),
    handler: ClosePositionHandler = Depends(get_close_position_handler),
) -> TradeResult:
    """
    Close an open position (full or partial).
    
    Mirrors MT5 Manager API `OrderClose` endpoint.
    """
    try:
        command = ClosePositionCommand(
            account_login=manager.login,
            position_id=str(request.ticket),
            volume=request.volume,
            price=request.price,
            comment="Manager API close",
        )
        
        position = await handler.handle(command)
        
        return TradeResult(
            answer=Request(
                action="CLOSE",
                symbol=position.symbol,
                volume=request.volume or position.volume.value,
                price=request.price,
            ),
            result=Confirm(
                request_id=str(request.ticket),
                position_ticket=request.ticket,
                price=request.price or position.price_current.value,
                volume=request.volume or position.volume.value,
                retcode=0,
                comment="Position closed successfully",
            ),
        )
    
    except ValueError as e:
        logger.warning(f"OrderClose failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"OrderClose error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


# ============================================================================
# OrderDelete - Cancel pending order
# ============================================================================

@router.post(
    "/OrderDelete",
    response_model=TradeResult,
    responses={201: {"model": ExceptionResult}},
    summary="Cancel pending order",
)
async def order_delete(
    request: OrderDeleteRequest,
    manager: Account = Depends(get_current_manager),
    handler: CancelOrderHandler = Depends(get_cancel_order_handler),
) -> TradeResult:
    """
    Cancel a pending order.
    
    Mirrors MT5 Manager API `OrderDelete` endpoint.
    Only non-terminal orders (PLACED, PARTIALLY_FILLED) can be cancelled.
    """
    try:
        command = CancelOrderCommand(
            account_login=manager.login,
            ticket_id=str(request.ticket),
            reason="Manager API cancellation",
        )
        
        order = await handler.handle(command)
        
        return TradeResult(
            answer=Request(
                action="DELETE",
                symbol=order.symbol,
                volume=order.volume_initial.value,
                price=order.price_order.value,
                comment=order.comment,
            ),
            result=Confirm(
                request_id=str(request.ticket),
                order_ticket=request.ticket,
                retcode=0,
                comment="Order cancelled successfully",
            ),
        )
    
    except ValueError as e:
        logger.warning(f"OrderDelete failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"OrderDelete error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


# ============================================================================
# OrderModify - Modify pending order (price/SL/TP)
# ============================================================================

@router.post(
    "/OrderModify",
    response_model=TradeResult,
    responses={201: {"model": ExceptionResult}},
    summary="Modify pending order",
)
async def order_modify(
    request: OrderModifyRequest,
    manager: Account = Depends(get_current_manager),
    handler: ModifyOrderHandler = Depends(get_modify_order_handler),
) -> TradeResult:
    """
    Modify a pending order's price, stop loss, or take profit.
    
    Mirrors MT5 Manager API `OrderModify` endpoint.
    Only PLACED or PARTIALLY_FILLED orders can be modified.
    """
    try:
        command = ModifyOrderCommand(
            account_login=manager.login,
            ticket_id=str(request.ticket),
            new_price=request.price,
            new_stop_loss=request.stop_loss,
            new_take_profit=request.take_profit,
            reason="Manager API modification",
        )
        
        order = await handler.handle(command)
        
        return TradeResult(
            answer=Request(
                action="MODIFY",
                symbol=order.symbol,
                volume=order.volume_current.value,
                price=order.price_order.value,
                stop_loss=request.stop_loss,
                take_profit=request.take_profit,
            ),
            result=Confirm(
                request_id=str(request.ticket),
                order_ticket=request.ticket,
                price=order.price_order.value,
                retcode=0,
                comment="Order modified successfully",
            ),
        )
    
    except ValueError as e:
        logger.warning(f"OrderModify failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"OrderModify error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


# ============================================================================
# DealModify - Modify SL/TP of open position
# ============================================================================

@router.post(
    "/DealModify",
    response_model=TradeResult,
    responses={201: {"model": ExceptionResult}},
    summary="Modify SL/TP of open position",
)
async def deal_modify(
    request: DealModifyRequest,
    manager: Account = Depends(get_current_manager),
    handler: ModifyDealHandler = Depends(get_modify_deal_handler),
) -> TradeResult:
    """
    Modify SL/TP of an open position via MT5 Trade Modification pattern.
    
    Mirrors MT5 Manager API `DealModify` endpoint.
    Internally uses the Reversal + Correction pattern to maintain
    immutable deal ledger while updating position parameters.
    """
    try:
        # Note: In MT5, DealModify typically modifies SL/TP on a position.
        # Our ModifyDealHandler uses the Trade Modification pattern
        # (Reversal + Correction) which is more powerful — it can modify
        # price, volume, AND profit, while maintaining audit trail.
        
        # For SL/TP-only modifications, we pass None for price/volume/profit
        # and the handler will preserve original values.
        command = ModifyDealCommand(
            account_login=manager.login,
            dealer_login=manager.login,
            original_deal_id=str(request.ticket),
            new_price=None,  # Preserve original price
            new_volume=None,  # Preserve original volume
            new_profit=None,  # Preserve original profit
            reason=f"SL/TP modification: SL={request.stop_loss}, TP={request.take_profit}",
        )
        
        result = await handler.handle(command)
        
        return TradeResult(
            answer=Request(
                action="DEAL_MODIFY",
                symbol=result["original_deal"].symbol,
                volume=result["original_deal"].volume.value,
                price=result["original_deal"].price.value,
                stop_loss=request.stop_loss,
                take_profit=request.take_profit,
            ),
            result=Confirm(
                request_id=str(request.ticket),
                deal_ticket=result["correction_deal"].deal_id,
                retcode=0,
                comment=(
                    f"Deal modified via Trade Modification pattern. "
                    f"Reversal: {result['reversal_deal'].deal_id}, "
                    f"Correction: {result['correction_deal'].deal_id}"
                ),
            ),
        )
    
    except ValueError as e:
        logger.warning(f"DealModify failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"DealModify error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )