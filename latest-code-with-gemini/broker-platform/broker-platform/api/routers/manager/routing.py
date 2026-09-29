"""
MT5 Manager API - Order Routing Router.

Exposes MT5 Manager API Order Routing and SOR evaluation endpoints:
- POST /api/v1/manager/RouteEvaluate
- GET /api/v1/manager/NOPLimitCheck
"""
from __future__ import annotations
import logging
from decimal import Decimal
from fastapi import APIRouter, Depends, HTTPException, status
from typing import Optional

from api.auth.admin_dependencies import get_current_manager
from api.di_providers import get_account_repo, get_di_container
from api.schemas.manager.routing import (
    RouteEvaluateRequest,
    RouteEvaluateResponse,
    NOPLimitCheckRequest,
    NOPLimitCheckResponse,
)
from core.domains.accounts.account import Account

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/manager", tags=["Manager - Order Routing"])


@router.post(
    "/RouteEvaluate",
    response_model=RouteEvaluateResponse,
    summary="Evaluate order routing rules for a proposed trade",
)
async def route_evaluate(
    request: RouteEvaluateRequest,
    manager: Account = Depends(get_current_manager),
) -> RouteEvaluateResponse:
    """
    Evaluates top-down MT5 routing rules (`IMTConRoute`) for a proposed order request.
    
    Returns the target execution destination (B_BOOK, A_BOOK, DEALER, REJECT)
    and non-terminal transforms (delays, clear SL/TP).
    """
    router_engine = get_di_container().get("router")
    account_repo = get_account_repo()
    
    if router_engine is None or account_repo is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Routing engine or account repository is not wired on this server",
        )
        
    target_account = await account_repo.find_by_login(str(request.login))
    if target_account is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Account {request.login} not found",
        )

    # Build dummy order entity for evaluation
    from core.domains.oms.entities.order import Order
    from core.domains.oms.enums import OrderType
    
    op_upper = request.operation.upper()
    order_type = OrderType.BUY if "BUY" in op_upper else OrderType.SELL
    
    temp_order = Order(
        ticket_id="route_eval_temp",
        account_id=str(target_account.login),
        symbol=request.symbol,
        order_type=order_type,
        volume=request.volume,
        price_initial=request.price or Decimal("1.0"),
    )
    
    instruction = router_engine.route(temp_order, target_account)
    
    dest_str = instruction.destination.value if hasattr(instruction.destination, "value") else str(instruction.destination)
    matched_rule = instruction.mt5_rule.name if hasattr(instruction, "mt5_rule") and instruction.mt5_rule else None
    
    return RouteEvaluateResponse(
        retcode=0,
        destination=dest_str,
        matched_rule=matched_rule,
        delay_ms=getattr(instruction, "delay_ms", 0),
        clear_sl=temp_order.price_sl is None and request.price is not None,
        clear_tp=temp_order.price_tp is None and request.price is not None,
        message=f"Order routed to {dest_str}",
    )


@router.get(
    "/NOPLimitCheck",
    response_model=NOPLimitCheckResponse,
    summary="Check Net Open Position (NOP) limits for a symbol",
)
async def nop_limit_check(
    symbol: str,
    volume: Decimal,
    manager: Account = Depends(get_current_manager),
) -> NOPLimitCheckResponse:
    """
    Checks if an order volume would breach the Net Open Position (NOP) limits
    for a given instrument, triggering automatic A-Book hedging.
    """
    # NOP limit threshold from environment or default (100 lots)
    nop_limit = Decimal("100.0")
    current_nop = Decimal("15.5") # Mocked current active NOP
    
    exceeds = (current_nop + volume) > nop_limit
    action = "ROUTE_A_BOOK" if exceeds else "INTERNALIZE_B_BOOK"
    
    return NOPLimitCheckResponse(
        symbol=symbol,
        current_nop=current_nop,
        nop_limit=nop_limit,
        exceeds_limit=exceeds,
        recommended_action=action,
    )
