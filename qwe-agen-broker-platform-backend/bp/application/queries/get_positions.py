"""
Get Positions Query Handler - CQRS Read Side

Handles querying open positions for a trading account and calculating live unrealized PnL.

Architectural Rule: Application Query handler in application/queries/.
"""
from dataclasses import dataclass
from decimal import Decimal
from typing import Any, List, Optional

from core.ports.interfaces import IPositionRepository, ISymbolRepository


@dataclass(frozen=True)
class GetPositionsQuery:
    """Query payload to fetch open positions for an account."""
    account_login: str


class GetPositionsQueryHandler:
    """Read-side query handler for active open positions."""

    def __init__(
        self,
        position_repo: IPositionRepository,
        market_data_engine: Optional[Any] = None,
        symbol_repo: Optional[ISymbolRepository] = None
    ):
        self.position_repo = position_repo
        self.market_data_engine = market_data_engine
        self.symbol_repo = symbol_repo

    async def handle(self, query: GetPositionsQuery) -> List[dict]:
        """Process GetPositionsQuery and return open positions list."""
        positions = await self.position_repo.get_positions_by_account(query.account_login)
        results = []

        for pos in positions:
            unrealized_pnl = Decimal('0')

            # Calculate live PnL if market data engine available
            if self.market_data_engine and hasattr(self.market_data_engine, 'get_latest_tick'):
                tick = self.market_data_engine.get_latest_tick(pos.symbol)
                if tick:
                    side_str = pos.side.name if hasattr(pos.side, 'name') else str(pos.side)
                    avg_price = pos.average_price.value if hasattr(pos.average_price, 'value') else Decimal(str(pos.average_price))
                    vol = pos.volume.value if hasattr(pos.volume, 'value') else Decimal(str(pos.volume))

                    contract_size = getattr(pos, 'contract_size', Decimal('100000'))
                    if self.symbol_repo and hasattr(self.symbol_repo, 'get_symbol'):
                        sym_info = self.symbol_repo.get_symbol(pos.symbol)
                        if sym_info and hasattr(sym_info, 'contract_size'):
                            contract_size = sym_info.contract_size

                    if side_str == "BUY":
                        unrealized_pnl = (tick.bid - avg_price) * vol * Decimal(str(contract_size))
                    else:
                        unrealized_pnl = (avg_price - tick.ask) * vol * Decimal(str(contract_size))

            pos_id = getattr(pos, 'id', getattr(pos, 'position_id', ''))
            symbol = getattr(pos, 'symbol', '')
            side = pos.side.name if hasattr(pos.side, 'name') else str(pos.side)
            vol = pos.volume.value if hasattr(pos.volume, 'value') else Decimal(str(pos.volume))
            avg_price = pos.average_price.value if hasattr(pos.average_price, 'value') else Decimal(str(pos.average_price))
            swap = pos.swap.amount if hasattr(pos, 'swap') and hasattr(pos.swap, 'amount') else Decimal('0')

            results.append({
                "position_id": str(pos_id),
                "symbol": symbol,
                "side": side,
                "volume": vol,
                "average_price": avg_price,
                "unrealized_pnl": unrealized_pnl,
                "swap": swap
            })

        return results
