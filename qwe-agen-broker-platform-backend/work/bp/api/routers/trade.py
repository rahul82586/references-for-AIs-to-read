"""
Trade REST API Router

Exposes client endpoints for order placement, modification, and cancellation.

Architectural Rule: Invokes Application Command Handlers, zero direct DB access.
"""
import logging
from datetime import datetime, timezone
from decimal import Decimal
from typing import Any, Dict, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from api.auth.dependencies import get_current_user
from api.di_providers import get_create_order_handler
from api.schemas.trade import ModifyOrderRequest, OrderRequest, OrderResponse
from application.commands.cancel_order import CancelOrderCommand
from application.commands.close_position import ClosePositionCommand
from application.commands.create_order import CreateOrderCommand, CreateOrderCommandHandler
from application.commands.modify_order import ModifyOrderCommand
from core.domains.accounts.models import Account

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/trade", tags=["Trade"])


# ------------------------------------------------------------------ D11 schemas

class ClosePositionRequest(BaseModel):
    """Client request to close an open position, fully or partly."""

    #: omit for a full close
    volume: Optional[Decimal] = Field(None, gt=0, description="Lots to close; omit = all")
    #: omit to close at market
    price: Optional[Decimal] = Field(None, gt=0)
    comment: str = ""


class ClosePositionResponse(BaseModel):
    position_id: str
    symbol: str
    volume_closed: Decimal
    volume_remaining: Decimal
    close_price: Decimal
    realized_pnl: Decimal
    deal_id: str
    fully_closed: bool
    message: str = "Position closed"


class OrderActionResponse(BaseModel):
    """The truthful result of a modify or a cancel."""

    status: str
    ticket_id: str
    order_state: str
    price: Optional[str] = None
    stop_loss: Optional[str] = None
    take_profit: Optional[str] = None
    volume_current: Optional[str] = None
    comment: Optional[str] = None


# ----------------------------------------------------------------- D11 helpers

def _handler(key: str, what: str) -> Any:
    """Resolve a command handler, or 503.

    An unwired handler must be a loud server error, never a route that quietly
    returns a hardcoded body - which is precisely what the stubs below used to do.
    """
    from api.di_providers import _container  # local import: avoids a cycle

    handler = _container.get(key)
    if handler is None:
        logger.error("%s is not registered; the trading plane is not wired", key)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"{what} is not available on this server",
        )
    return handler


def _login_of(account: Account) -> int:
    """The authenticated login - never taken from a request body.

    Ownership is enforced by threading this into every command: a client cannot
    close or modify another client\'s position by guessing an id, because the
    handler checks the login it is given against the order/position it loads.
    """
    login = getattr(account, "login_id", None) or getattr(account, "login", None)
    try:
        return int(login)
    except (TypeError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not resolve the authenticated account",
        )


def _domain_error_to_http(exc: ValueError, what: str) -> HTTPException:
    """Map a domain refusal onto 404 vs 400 by what it says."""
    msg = str(exc)
    code = (status.HTTP_404_NOT_FOUND if "not found" in msg.lower()
            else status.HTTP_400_BAD_REQUEST)
    return HTTPException(status_code=code, detail=f"{what}: {msg}")


def _dec(value: Any) -> Optional[str]:
    """A Money/Quantity/value-object, or a bare number, as a string."""
    v = getattr(value, "value", value)
    return str(v) if v is not None else None


def _order_response(order: Any, action: str) -> OrderActionResponse:
    state = getattr(getattr(order, "state", None), "value", None) or str(
        getattr(order, "state", ""))
    return OrderActionResponse(
        status=action,
        ticket_id=str(getattr(order, "ticket_id", "")),
        order_state=str(state),
        price=_dec(getattr(order, "price_order", None)),
        stop_loss=_dec(getattr(order, "price_sl", None)),
        take_profit=_dec(getattr(order, "price_tp", None)),
        volume_current=_dec(getattr(order, "volume_current", None)),
        comment=getattr(order, "comment", None),
    )


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
        comment=request.comment,
        expiration=request.expiration
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


async def _position_repo_volume(handler: Any, position_id: str) -> Optional[Decimal]:
    """The position's volume before a close, or None if it cannot be read.

    D12 needs the closed amount, and the only honest way to get it is
    `volume_before - volume_after`. This reads through the same repository the
    handler is bound to, so it sees the same world the close will act on. A failure
    here must not fail the close - the close is the thing that matters - so it
    degrades to None and the response falls back to what it can say.
    """
    repo = getattr(handler, "position_repo", None)
    finder = getattr(repo, "find_by_id", None)
    if finder is None:
        return None
    try:
        existing = await finder(position_id)
    except Exception:  # noqa: BLE001
        logger.warning("could not pre-read position %s for the close response", position_id)
        return None
    if existing is None:
        return None
    value = getattr(getattr(existing, "volume", None), "value", None)
    return Decimal(str(value)) if value is not None else None


@router.post("/positions/{position_id}/close", response_model=ClosePositionResponse)
async def close_position(
    position_id: str,
    request: ClosePositionRequest,
    current_user: Account = Depends(get_current_user)
):
    """Close an open position, fully or partly, and book the OUT deal.

    This route did not exist, which is why the database held 31 IN deals and no OUT
    deals. It drives the same ClosePositionHandler the SL/TP worker, the liquidation
    worker and the manager OrderClose endpoint use, so a client close produces
    exactly the same deal, position and margin treatment as a server-side one -
    including D10's margin release.

    POST with a body rather than DELETE, because a partial close carries a volume and
    DELETE-with-body is not reliably supported by clients and proxies. DELETE stays
    for cancelling a resting order, which is what it always meant.
    """
    handler = _handler("close_position_handler", "Position closing")
    login = _login_of(current_user)

    # D12: the handler returns the position AFTER it reduced the volume, so the
    # amount actually closed has to be read before the call - on a full close the
    # returned volume is 0, and `request.volume` is None whenever the client asked
    # to close "all", which is the normal case. Both fallbacks below were therefore
    # empty exactly when the response mattered most.
    _before = await _position_repo_volume(handler, position_id)

    # D14: the handler fills this with what the close actually did. Reading the
    # returned Position instead is what made a partial close report the remainder's
    # floating PnL and an empty deal id.
    result: Dict[str, Any] = {}

    try:
        position = await handler.handle(ClosePositionCommand(
            account_login=login,
            position_id=position_id,
            volume=request.volume,
            price=request.price,
            comment=request.comment or "",
            reason="CLIENT",
            result=result,
        ))
    except ValueError as exc:
        raise _domain_error_to_http(exc, "cannot close position")
    except HTTPException:
        raise
    except Exception:
        logger.exception("close_position failed for %s (account %s)", position_id, login)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not close the position",
        )

    remaining = getattr(getattr(position, "volume", None), "value", Decimal("0"))
    fully = bool(getattr(position, "time_done", None))

    # Every figure below comes from the deal the handler booked, so a partial and a
    # full close are described the same way. The position-derived reads stay as
    # fallbacks for a handler that does not fill the sink (a double, or a caller
    # wired before D14) - they are right for a full close and wrong for a partial,
    # which is the defect.
    realized = result.get("realized_pnl")
    if realized is None:
        realized = getattr(getattr(position, "profit", None), "amount", Decimal("0"))
    price = result.get("price")
    if price is None:
        price = getattr(getattr(position, "price_current", None), "value", None)
    deal_id = result.get("deal_id") or getattr(position, "deal_close", None) or ""

    # What was closed is the difference, not the remainder and not the request:
    # `request.volume` is None for a full close, and `remaining` is 0 after one.
    closed = result.get("volume_closed")
    if closed is None:
        closed = request.volume
    if closed is None:
        closed = (_before - remaining) if _before is not None else remaining

    return ClosePositionResponse(
        position_id=str(getattr(position, "position_id", position_id)),
        symbol=str(getattr(position, "symbol", "")),
        volume_closed=Decimal(str(closed)),
        volume_remaining=remaining,
        close_price=(Decimal(str(price)) if price is not None
                     else (request.price or Decimal("0"))),
        realized_pnl=Decimal(str(realized)),
        deal_id=str(deal_id),
        fully_closed=fully,
        message=("Position closed" if fully else "Position partially closed"),
    )


@router.put("/orders/{ticket_id}", response_model=OrderActionResponse)
async def modify_order(
    ticket_id: str,
    request: ModifyOrderRequest,
    current_user: Account = Depends(get_current_user)
):
    """Modify a pending order's price, SL, TP or expiration - for real.

    This used to echo the request back as {"status": "modified"} without persisting
    anything. A client that moved its stop loss believed it was protected and was not.
    """
    handler = _handler("modify_order_handler", "Order modification")
    login = _login_of(current_user)

    if all(v is None for v in (request.price, request.stop_loss, request.take_profit)):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="nothing to modify: supply price, stop_loss or take_profit",
        )

    try:
        order = await handler.handle(ModifyOrderCommand(
            account_login=login,
            ticket_id=ticket_id,
            new_price=request.price,
            new_stop_loss=request.stop_loss,
            new_take_profit=request.take_profit,
            reason="CLIENT",
        ))
    except ValueError as exc:
        raise _domain_error_to_http(exc, "cannot modify order")
    except HTTPException:
        raise
    except Exception:
        logger.exception("modify_order failed for %s (account %s)", ticket_id, login)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not modify the order",
        )

    return _order_response(order, "modified")


@router.delete("/orders/{ticket_id}", response_model=OrderActionResponse)
async def cancel_order(
    ticket_id: str,
    current_user: Account = Depends(get_current_user)
):
    """Cancel a resting order - for real.

    This returned {"status": "cancelled"} for ANY ticket id, including one that did
    not exist or belonged to another client. Nothing was cancelled and nothing was
    logged.
    """
    handler = _handler("cancel_order_handler", "Order cancellation")
    login = _login_of(current_user)

    try:
        order = await handler.handle(CancelOrderCommand(
            account_login=login, ticket_id=ticket_id, reason="CLIENT",
        ))
    except ValueError as exc:
        raise _domain_error_to_http(exc, "cannot cancel order")
    except HTTPException:
        raise
    except Exception:
        logger.exception("cancel_order failed for %s (account %s)", ticket_id, login)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not cancel the order",
        )

    return _order_response(order, "cancelled")
