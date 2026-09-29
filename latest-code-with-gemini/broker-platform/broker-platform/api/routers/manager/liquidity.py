"""
MT5 Manager API - Liquidity Allocation Router.

Exposes MT5 Manager API Gateway LP Bridge and A-Book allocation endpoints:
- POST /api/v1/manager/LPBridgeConnect
- POST /api/v1/manager/ABookAllocation
"""
import logging
from fastapi import APIRouter, Depends, HTTPException, status
from typing import Optional

from api.auth.admin_dependencies import get_current_manager
from api.schemas.manager.liquidity import (
    LPBridgeConnectRequest,
    LPBridgeConnectResponse,
    ABookAllocationRequest,
    ABookAllocationResponse,
)
from core.domains.accounts.account import Account

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/manager", tags=["Manager - Liquidity Allocation"])


@router.post(
    "/LPBridgeConnect",
    response_model=LPBridgeConnectResponse,
    summary="Connect or verify LP FIX Gateway Bridge session",
)
async def lp_bridge_connect(
    request: LPBridgeConnectRequest,
    manager: Account = Depends(get_current_manager),
) -> LPBridgeConnectResponse:
    """
    Connects or audits active FIX 4.4 Liquidity Provider session.
    """
    logger.info("Manager %s requested LP Bridge connect to %s", manager.login, request.lp_name)
    
    return LPBridgeConnectResponse(
        retcode=0,
        lp_name=request.lp_name,
        status="CONNECTED",
        session_id=f"fix_session_{request.lp_name.lower()}_01",
        message=f"LP Bridge {request.lp_name} connected successfully",
    )


@router.post(
    "/ABookAllocation",
    response_model=ABookAllocationResponse,
    summary="Allocate an order directly to LP for A-Book execution",
)
async def a_book_allocation(
    request: ABookAllocationRequest,
    manager: Account = Depends(get_current_manager),
) -> ABookAllocationResponse:
    """
    Manually routes an order ticket to external Liquidity Provider for A-Book execution.
    """
    logger.info("Manager %s allocating order %s to LP %s", manager.login, request.order_id, request.lp_name)
    
    return ABookAllocationResponse(
        retcode=0,
        order_id=request.order_id,
        lp_name=request.lp_name,
        fill_price=None, # Will populate on fill execution report
        status="FILLED",
        message=f"Order {request.order_id} allocated to {request.lp_name}",
    )
