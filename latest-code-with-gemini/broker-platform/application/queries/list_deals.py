"""List Deals query (plan step 8 / ENDPOINTS B2).

The UI's Deals page had NO data source on ANY plane - the IN/OUT lifecycle
fixed in D11-D15 was invisible to it. Cross-account, paged, filtered by
login / symbol / entry (IN, OUT, INOUT, OUT_BY), newest first.
"""
from dataclasses import dataclass
from typing import Any, List, Optional, Tuple


@dataclass(frozen=True)
class ListDealsQuery:
    limit: int = 100
    offset: int = 0
    account_login: Optional[int] = None
    symbol: Optional[str] = None
    entry: Optional[str] = None


class ListDealsQueryHandler:
    def __init__(self, deal_repo: Any):
        self.deal_repo = deal_repo

    async def handle(self, query: ListDealsQuery) -> Tuple[List[Any], int]:
        if self.deal_repo is None:
            raise RuntimeError(
                "ListDealsQueryHandler has no deal repository; refusing to "
                "answer with an empty page (register it, or the route 503s)"
            )
        return await self.deal_repo.find_page(
            limit=query.limit,
            offset=query.offset,
            account_login=query.account_login,
            symbol=query.symbol,
            entry=query.entry,
        )
