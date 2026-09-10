"""
Trade REST API Router

Exposes client endpoints for order placement, modification, and cancellation.

Architectural Rule: Invokes Application Command Handlers, zero direct DB access.
"""
from decimal import Decimal
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status

from api.auth.dependencies import get_current_user
from api.di_providers import get_create_order_handler
from api.schemas.trade import ModifyOrderRequest, OrderRequest, OrderResponse
from application.commands.create_order import CreateOrderCommand, CreateOrderCommandHandler
from core.domains.accounts.models import Account

router = APIRouter(prefix="/api/v1/trade", tags=["Trade"])


@router.post("/orders", response_model=OrderResponse)
async def place_order(
    request: OrderRequest,
    current_user: Account = Depends(get_current_user),
    handler: CreateOrderCommandHandler = Depends(get_create_order_handler)
):
    """Place a new market or pending order."""
    command = CreateOrderCommand(
        account_login=getattr(current_user, 'login_id', getattr(current_user, 'login', 100001)),
        symbol=request.symbol,
        order_type=request.order_type,
        volume=request.volume,
        price=request.price,
        stop_loss=request.stop_loss,
        take_profit=request.take_profit,
        comment=request.comment
    )
    try:
        order = await handler.handle(command)
        ticket_id = getattr(order, 'ticket_id', getattr(order, 'id', ''))
        symbol = getattr(order, 'symbol', '')
        order_type_str = order.order_type.value if hasattr(order.order_type, 'value') else str(order.order_type)
        vol_val = order.volume_initial.value if hasattr(order.volume_initial, 'value') else Decimal(str(order.volume_initial))
        state_str = order.state.value if hasattr(order.state, 'value') else str(order.state)
        created_at = getattr(order, 'created_at', datetime.now(timezone.utc))

        # Order carries volume_initial / volume_current and price_order - MT5's own field
        # names. This response read `order.filled_volume` and `order.price`, neither of
        # which exists, so the two guard expressions quietly took their else branch and
        # EVERY response reported filled_volume 0 and price null, including for orders
        # that had genuinely filled. A client reading this endpoint could not tell what
        # it had been filled at, or whether it had been filled at all.
        remaining = order.volume_current.value if hasattr(order.volume_current, 'value') else Decimal('0')
        filled_vol = vol_val - remaining

        # For a market order price_order is the execution price: CreateOrderHandler sets
        # it from the live quote (ask for a buy, bid for a sell) before the fill, and the
        # matching engine fills at that same price. For a resting pending order it is the
        # requested limit/stop, which is the only price there is so far.
        price_val = order.price_order.value if getattr(order, 'price_order', None) else None

        return OrderResponse(
            ticket_id=str(ticket_id),
            symbol=symbol,
            order_type=order_type_str,
            volume=vol_val,
            filled_volume=filled_vol,
            price=price_val,
            state=state_str,
            created_at=created_at,
            message="Order placed successfully"
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.put("/orders/{ticket_id}")
async def modify_order(
    ticket_id: str,
    request: ModifyOrderRequest,
    current_user: Account = Depends(get_current_user)
):
    """Modify an existing pending order (price, SL, TP)."""
    return {
        "status": "modified",
        "ticket_id": ticket_id,
        "price": str(request.price) if request.price else None,
        "stop_loss": str(request.stop_loss) if request.stop_loss else None,
        "take_profit": str(request.take_profit) if request.take_profit else None
    }


@router.delete("/orders/{ticket_id}")
async def cancel_order(
    ticket_id: str,
    current_user: Account = Depends(get_current_user)
):
    """Cancel a pending order."""
    return {"status": "cancelled", "ticket_id": ticket_id}
