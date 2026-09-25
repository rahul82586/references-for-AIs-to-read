"""
Get Positions Query Handler - CQRS Read Side

Handles querying open positions for a trading account and calculating live unrealized PnL.

Architectural Rule: Application Query handler in application/queries/.
"""
from dataclasses import dataclass
from decimal import Decimal
from typing import Any, List, Optional

from core.ports.interfaces import (
    IAccountRepository,
    IPositionRepository,
    ISymbolRepository,
)


@dataclass(frozen=True)
class GetPositionsQuery:
    """Query payload to fetch open positions for an account."""
    account_login: str


class GetPositionsQueryHandler:
    """Read-side query handler for active open positions.

    M5 rewrite: this handler was written against the pre-M3 Position vocabulary
    (pos.side / pos.average_price / pos.id) and computed PnL without currency
    conversion. The renames made every attribute access raise, and the route
    swallowed it into an empty list, so the endpoint reported "no positions"
    for accounts that held some. Valuation now goes through
    RiskEngine.calculate_position_pnl - the same single source of truth the
    margin loop and the liquidation worker use. Without an engine and an
    account it REFUSES to answer rather than reporting a comfortable zero.
    """

    def __init__(
        self,
        position_repo: IPositionRepository,
        market_data_engine: Optional[Any] = None,
        symbol_repo: Optional[ISymbolRepository] = None,
        account_repo: Optional[IAccountRepository] = None,
        risk_engine: Optional[Any] = None,
    ):
        self.position_repo = position_repo
        self.market_data_engine = market_data_engine
        self.symbol_repo = symbol_repo
        self.account_repo = account_repo
        self.risk_engine = risk_engine

    async def handle(self, query: GetPositionsQuery) -> List[dict]:
        """Process GetPositionsQuery and return open positions list."""
        positions = await self.position_repo.get_positions_by_account(query.account_login)
        if not positions:
            return []

        if self.risk_engine is None or self.account_repo is None:
            raise RuntimeError(
                "GetPositionsQueryHandler cannot value positions without a risk_engine "
                "and an account_repo; refusing to report unrealized_pnl=0 for real "
                "positions (register it with the trading stack, as api/main.py does)"
            )
        account = await self.account_repo.find_by_login(query.account_login)
        if account is None:
            raise RuntimeError(
                f"account {query.account_login} holds {len(positions)} position(s) "
                "but cannot be loaded; refusing to guess its deposit currency"
            )

        results = []
        for pos in positions:
            action = pos.action.value if hasattr(pos.action, "value") else str(pos.action)
            results.append(
                {
                    "position_id": str(pos.position_id),
                    "symbol": pos.symbol,
                    "side": action,
                    "volume": pos.volume.value,
                    "average_price": pos.price_open.value,
                    "unrealized_pnl": self.risk_engine.calculate_position_pnl(account, pos),
                    "swap": (
                        pos.swap.amount
                        if getattr(pos, "swap", None) is not None
                        and hasattr(pos.swap, "amount")
                        else Decimal("0")
                    ),
                }
            )
        return results


# ---------------------------------------------------------------------------
# Manager plane (F8): the cross-account read.
#
# The client-plane handler above is correct FOR ITS PURPOSE - one account,
# valued through the RiskEngine, refusing to answer without one. The manager's
# PositionGet is a different question: show the book (any account, any symbol),
# stored values, no valuation pass. Reusing the client handler for it was the
# original F8 - the route passed `symbol=` to a query that never declared it
# and `account_login=None` to a required str, so EVERY call raised TypeError
# and the route's blanket `except` served [] as if the whole book were flat.
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class GetManagerPositionsQuery:
    """Cross-account open-position read for the manager plane.

    Both filters are optional; None means "no filter". This mirrors MT5's
    PositionGet, which lists the book and lets the terminal filter.
    """
    account_login: Optional[int] = None
    symbol: Optional[str] = None


class GetManagerPositionsQueryHandler:
    """Dispatches to the repository's own SQL-level reads - never find_all()
    plus a Python filter, which is the read-side twin of the paging trap.

    Returns Position ENTITIES. Serialization is the route's job via the one
    shared serializer (api.schemas.manager.main.position_to_info), so every
    consumer sees the same wire shape.
    """

    def __init__(self, position_repo: IPositionRepository):
        self.position_repo = position_repo

    async def handle(self, query: GetManagerPositionsQuery) -> List[Any]:
        login = query.account_login
        symbol = (query.symbol or "").strip() or None
        if login is not None and symbol is not None:
            return await self.position_repo.get_by_account_and_symbol(int(login), symbol)
        if login is not None:
            return await self.position_repo.get_positions_by_account(int(login))
        if symbol is not None:
            return await self.position_repo.get_by_symbol(symbol)
        return await self.position_repo.get_open_positions()
