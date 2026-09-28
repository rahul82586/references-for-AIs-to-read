"""List Orders query (plan step 8 / ENDPOINTS B2).

Two UI pages, one query: getOrders (the active book) and getOrderHistory
(terminal states). `history` is a TRI-STATE - None = everything, False =
active (STARTED/PLACED/PARTIALLY_FILLED), True = terminal (CANCELLED/
FILLED/REJECTED/EXPIRED) - and a `state` that contradicts `history` is
refused by the repository, not silently intersected into a confusing empty
page.
"""
from dataclasses import dataclass
from typing import Any, List, Optional, Tuple


@dataclass(frozen=True)
class ListOrdersQuery:
    limit: int = 100
    offset: int = 0
    account_login: Optional[int] = None
    symbol: Optional[str] = None
    state: Optional[str] = None
    history: Optional[bool] = None


class ListOrdersQueryHandler:
    def __init__(self, order_repo: Any):
        self.order_repo = order_repo

    async def handle(self, query: ListOrdersQuery) -> Tuple[List[Any], int]:
        if self.order_repo is None:
            raise RuntimeError(
                "ListOrdersQueryHandler has no order repository; refusing to "
                "answer with an empty page (register it, or the route 503s)"
            )
        return await self.order_repo.find_page(
            limit=query.limit,
            offset=query.offset,
            account_login=query.account_login,
            symbol=query.symbol,
            state=query.state,
            history=query.history,
        )
