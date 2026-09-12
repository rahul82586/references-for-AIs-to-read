"""
MT5 Manager API - Main Router (Queries).

Exposes read-only endpoints that mirror MT5 Manager API:
- GET /api/v1/manager/UserGet
- GET /api/v1/manager/PositionGet
- GET /api/v1/manager/DealGet
- GET /api/v1/manager/OrderGet
- GET /api/v1/manager/SymbolGet
"""
import logging
from fastapi import APIRouter, Depends, HTTPException, Query, status
from typing import List, Optional

from api.auth.admin_dependencies import get_current_manager
from api.di_providers import (
    get_account_query_handler,
    get_positions_query_handler,
)
from api.schemas.manager.common import PaginatedResult
from api.schemas.manager.main import (
    AccountInfo,
    PositionInfo,
    DealInfo,
    OrderInfo,
)
from application.queries.get_account_info import GetAccountInfoQuery, GetAccountInfoQueryHandler
from application.queries.get_positions import GetPositionsQuery, GetPositionsQueryHandler
from core.domains.accounts.account import Account

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/manager", tags=["Manager - Main"])


# ============================================================================
# UserGet - Get account info
# ============================================================================

@router.get(
    "/UserGet",
    response_model=AccountInfo,
    summary="Get account information",
)
async def user_get(
    login: int = Query(..., description="Account login number"),
    manager: Account = Depends(get_current_manager),
    handler: Optional[GetAccountInfoQueryHandler] = Depends(get_account_query_handler),
) -> AccountInfo:
    """Get account information by login."""
    # D2: this read `account_info.login / .group_name / .margin` off a return
    # value that is a DICT keyed login_id / group / margin_used. The resulting
    # AttributeError was caught, logged as a warning, and the endpoint then
    # returned the MANAGER'S OWN balance and equity for a query about a client -
    # HTTP 200, wrong account's money. There is no fallback: a manager asking
    # about account N must get account N or an error.
    if handler is None:
        logger.error("account_info_query_handler is not registered; UserGet cannot answer")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Account query is not wired on this server",
        )
    try:
        info = await handler.handle(GetAccountInfoQuery(account_login=login))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception:
        logger.exception("UserGet failed for login=%s", login)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not read account information",
        )
    return AccountInfo(
        login=int(info["login_id"]),
        group=info["group"],
        currency=info["currency"],
        balance=info["balance"],
        credit=info["credit"],
        equity=info["equity"],
        margin=info["margin_used"],
        free_margin=info["margin_free"],
        margin_level=info["margin_level"],
        leverage=info["leverage"],
    )


# ============================================================================
# PositionGet - Get open positions
# ============================================================================

@router.get(
    "/PositionGet",
    response_model=List[PositionInfo],
    summary="Get open positions",
)
async def position_get(
    login: Optional[int] = Query(None, description="Filter by account login"),
    symbol: Optional[str] = Query(None, description="Filter by symbol"),
    manager: Account = Depends(get_current_manager),
    handler: Optional[GetPositionsQueryHandler] = Depends(get_positions_query_handler),
) -> List[PositionInfo]:
    """Get open positions."""
    if handler:
        try:
            query = GetPositionsQuery(account_login=login, symbol=symbol)
            positions = await handler.handle(query)
            return [
                PositionInfo(
                    ticket=int(p.position_id) if p.position_id.isdigit() else 0,
                    login=p.account_login,
                    symbol=p.symbol,
                    action=p.action.value,
                    volume=p.volume.value,
                    price_open=p.price_open.value,
                    price_current=p.price_current.value,
                    swap=p.swap.amount,
                    profit=p.profit.amount,
                )
                for p in positions
            ]
        except Exception as e:
            logger.warning(f"Positions query handler failed: {e}")

    return []
