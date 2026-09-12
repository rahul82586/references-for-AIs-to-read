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
    # D2: this endpoint is the client's view of its own margin. It used to swallow
    # every failure into `except Exception: pass` and fall back to the JWT
    # snapshot, whose margin_level is a stored column - so a client at 9260% was
    # told 0.0000%, which reads as "stopped out". Same contract as /positions
    # (M5 defects 14/15): unwired is a 503, an error is a 500 with a traceback,
    # and a stale snapshot is never a substitute for the real numbers.
    if handler is None:
        logger.error("account_info_query_handler is not registered; /account/info cannot answer")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Account info query is not wired on this server",
        )
    try:
        result = await handler.handle(GetAccountInfoQuery(account_login=login_val))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception:
        logger.exception("get_account_info failed for login=%s", login_val)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not read account information",
        )
    return AccountInfo(**result)


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
