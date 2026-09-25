"""List Positions query (plan step 8 / ENDPOINTS B2) - the ADMIN plane read.

Complements the manager plane's PositionGet (F8/F9): same repository, same
honest values, plus SQL-level paging and an include_closed switch for the
history view. The UI's Positions page reads this; the Exposure and
Margin-Call pages read the same rows.
"""
from dataclasses import dataclass
from typing import Any, List, Optional, Tuple


@dataclass(frozen=True)
class ListPositionsQuery:
    limit: int = 100
    offset: int = 0
    account_login: Optional[int] = None
    symbol: Optional[str] = None
    include_closed: bool = False


class ListPositionsQueryHandler:
    def __init__(self, position_repo: Any):
        self.position_repo = position_repo

    async def handle(self, query: ListPositionsQuery) -> Tuple[List[Any], int]:
        if self.position_repo is None:
            raise RuntimeError(
                "ListPositionsQueryHandler has no position repository; refusing "
                "to answer with an empty page (register it, or the route 503s)"
            )
        return await self.position_repo.find_page(
            limit=query.limit,
            offset=query.offset,
            account_login=query.account_login,
            symbol=query.symbol,
            include_closed=query.include_closed,
        )
