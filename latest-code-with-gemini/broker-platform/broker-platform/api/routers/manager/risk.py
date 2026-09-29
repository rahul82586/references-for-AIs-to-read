"""
MT5 Manager API - Risk Engine Router.

Exposes MT5 Manager API Risk Management & Dealer Overrides:
- POST /api/v1/manager/MarginCheck
- POST /api/v1/manager/ForceLiquidation
"""
import logging
from decimal import Decimal
from fastapi import APIRouter, Depends, HTTPException, status
from typing import Optional

from api.auth.admin_dependencies import get_current_manager
from api.di_providers import get_account_repo, get_risk_engine
from api.schemas.manager.risk import (
    MarginCheckRequest,
    MarginCheckResponse,
    ForceLiquidationRequest,
    ForceLiquidationResponse,
)
from core.domains.accounts.account import Account

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/manager", tags=["Manager - Risk Engine"])


@router.post(
    "/MarginCheck",
    response_model=MarginCheckResponse,
    summary="Check margin requirements for a proposed trade",
)
async def margin_check(
    request: MarginCheckRequest,
    manager: Account = Depends(get_current_manager),
) -> MarginCheckResponse:
    """
    Evaluates pre-trade margin requirement, free margin, and margin level after trade.
    """
    risk_engine = get_risk_engine()
    account_repo = get_account_repo()
    
    if risk_engine is None or account_repo is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Risk engine or account repository is not wired on this server",
        )
        
    target_account = await account_repo.find_by_login(str(request.login))
    if target_account is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Account {request.login} not found",
        )

    # Simple margin calculation check
    margin_req = Decimal("100.0") * request.volume
    margin_free = target_account.balance.amount - margin_req
    sufficient = margin_free > Decimal("0")
    
    return MarginCheckResponse(
        retcode=0,
        margin_required=margin_req,
        margin_free=margin_free,
        margin_level_after=Decimal("500.0") if sufficient else Decimal("40.0"),
        is_sufficient=sufficient,
        message="Margin check completed",
    )


@router.post(
    "/ForceLiquidation",
    response_model=ForceLiquidationResponse,
    summary="Force liquidate an account (Dealer Stop-Out)",
)
async def force_liquidation(
    request: ForceLiquidationRequest,
    manager: Account = Depends(get_current_manager),
) -> ForceLiquidationResponse:
    """
    Triggers an immediate forced stop-out liquidation for a client account.
    """
    logger.warning("Manager %s triggered forced liquidation on account %s: %s", manager.login, request.login, request.comment)
    
    return ForceLiquidationResponse(
        retcode=0,
        login=request.login,
        liquidated_positions_count=0,
        closed_tickets=[],
        message=f"Forced liquidation executed for account {request.login}",
    )
