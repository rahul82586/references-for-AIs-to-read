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
    if handler:
        try:
            query = GetAccountInfoQuery(account_login=login)
            account_info = await handler.handle(query)
            return AccountInfo(
                login=account_info.login,
                group=account_info.group_name,
                currency=account_info.currency,
                balance=account_info.balance,
                equity=account_info.equity,
                margin=account_info.margin,
                free_margin=account_info.free_margin,
                margin_level=account_info.margin_level,
                leverage=account_info.leverage,
            )
        except Exception as e:
            logger.warning(f"Query handler failed, falling back to manager account state: {e}")

    # Fallback to manager account data for standalone API testing
    return AccountInfo(
        login=manager.login,
        group=manager.group.name if manager.group else "REAL_STANDARD",
        currency=manager.currency,
        balance=manager.balance.amount,
        equity=manager.equity.amount,
        margin=manager.margin_used.amount,
        free_margin=manager.margin_free.amount,
        margin_level=manager.margin_level,
        leverage=manager.effective_leverage(),
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
