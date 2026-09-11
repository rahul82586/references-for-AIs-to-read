"""
Account REST API Router

Exposes client endpoints for querying real-time account snapshots and open positions.
"""
import logging
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status

from api.auth.dependencies import get_current_user
from api.di_providers import get_account_info_query_handler, get_positions_query_handler
from api.schemas.account import AccountInfo, PositionResponse
from application.queries.get_account_info import GetAccountInfoQuery, GetAccountInfoQueryHandler
from application.queries.get_positions import GetPositionsQuery, GetPositionsQueryHandler
from core.domains.accounts.account import Account

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/account", tags=["Account"])


@router.get("/info", response_model=AccountInfo)
async def get_account_info(
    current_user: Account = Depends(get_current_user),
    handler: Optional[GetAccountInfoQueryHandler] = Depends(get_account_info_query_handler)
):
    """Get current account metrics (balance, equity, margin usage, margin level)."""
    login_val = current_user.login if hasattr(current_user, 'login') else getattr(current_user, 'login_id', 100001)
    if handler:
        try:
            query = GetAccountInfoQuery(account_login=login_val)
            result = await handler.handle(query)
            return AccountInfo(**result)
        except Exception:
            pass

    return AccountInfo(
        login_id=str(login_val),
        group=current_user.group.name if hasattr(current_user, 'group') and current_user.group else "REAL_STANDARD",
        balance=current_user.balance.amount,
        equity=current_user.equity.amount,
        margin_used=current_user.margin_used.amount,
        margin_free=current_user.margin_free.amount,
        margin_level=current_user.margin_level,
        currency=current_user.currency,
    )


@router.get("/positions", response_model=List[PositionResponse])
async def get_open_positions(
    current_user: Account = Depends(get_current_user),
    handler: Optional[GetPositionsQueryHandler] = Depends(get_positions_query_handler)
):
    """Get all active open positions for the authenticated user."""
    login_val = current_user.login if hasattr(current_user, 'login') else getattr(current_user, 'login_id', 100001)
    if handler is None:
        # Pre-M5 this silently returned []: "no open positions" and "the query
        # is not wired" looked identical to the client, whose account held a
        # real, margined position. A missing handler is a server misconfiguration.
        logger.error("positions_query_handler is not registered; /account/positions cannot answer")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Positions query is not wired on this server",
        )
    try:
        query = GetPositionsQuery(account_login=login_val)
        positions_list = await handler.handle(query)
    except Exception:
        # Log the traceback and fail loudly. Swallowing into [] told the client
        # it was flat while its margin said otherwise.
        logger.exception("get_positions failed for login=%s", login_val)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not value open positions",
        )
    return [PositionResponse(**p) for p in positions_list]
