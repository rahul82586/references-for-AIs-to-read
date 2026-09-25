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
    get_manager_positions_query_handler,
)
from api.schemas.manager.common import PaginatedResult
from api.schemas.manager.main import (
    AccountInfo,
    PositionInfo,
    DealInfo,
    OrderInfo,
    position_to_info,
)
from application.queries.get_account_info import GetAccountInfoQuery, GetAccountInfoQueryHandler
from application.queries.get_positions import (
    GetManagerPositionsQuery,
    GetManagerPositionsQueryHandler,
)
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
    summary="Get open positions (all accounts; optional login/symbol filters)",
)
async def position_get(
    login: Optional[int] = Query(None, description="Filter by account login"),
    symbol: Optional[str] = Query(None, description="Filter by symbol"),
    manager: Account = Depends(get_current_manager),
    handler: Optional[GetManagerPositionsQueryHandler] = Depends(get_manager_positions_query_handler),
) -> List[PositionInfo]:
    """The cross-account positions read (F8/F9).

    This is the ONLY cross-account positions endpoint the platform has - the
    UI's Positions, Exposure and Margin-Call pages all read it. It returned
    ``[]`` + ``ticket=0`` against a live book of 31 open positions because of
    four stacked faults hidden by one blanket ``except Exception``:

    1. ``GetPositionsQuery`` has no ``symbol`` field (and requires
       ``account_login: str``), so the constructor raised TypeError on EVERY
       call - filtered or not;
    2. the client-plane handler returns DICTs; this route then read
       ``p.position_id`` / ``p.action.value`` attributes off them;
    3. ``ticket=int(position_id) if isdigit() else 0`` - position_id is a UUID
       or ``{login}_{SYMBOL}_{hex}``, never numeric, so ticket was always 0;
       the real venue ticket lives in ``external_id``;
    4. ``price_current`` is Optional on the entity (None until the first tick)
       and the old required ``.value`` access raised on exactly those rows.

    The contract is now the /account/positions one (M5/D2): 503 when the query
    is not wired, 500 on a real failure - and ``[]`` ONLY when the book is
    genuinely flat. An empty list is an answer; it must never be an error in
    disguise.
    """
    if handler is None:
        logger.error("manager_positions_query_handler is not registered; PositionGet cannot answer")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Positions query is not wired on this server",
        )
    try:
        positions = await handler.handle(
            GetManagerPositionsQuery(account_login=login, symbol=symbol)
        )
    except Exception:
        logger.exception("PositionGet failed (login=%s symbol=%s)", login, symbol)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not read positions",
        )
    return [position_to_info(p) for p in positions]
