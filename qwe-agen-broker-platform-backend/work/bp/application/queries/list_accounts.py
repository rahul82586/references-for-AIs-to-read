"""List Accounts query (plan step 8) - paged, filtered, SQL-level.

The UI's Accounts page had one source: admin_router's GET /accounts doing
find_all()[:limit] - load every row, throw most away, and a `limit` that
silently truncates instead of paging. This query goes through the
repository's find_page: WHERE/LIMIT/OFFSET in SQL, plus an honest total.
"""
from dataclasses import dataclass
from typing import Any, List, Optional, Tuple


@dataclass(frozen=True)
class ListAccountsQuery:
    limit: int = 100
    offset: int = 0
    group_name: Optional[str] = None     # exact MT5 group path
    account_type: Optional[str] = None   # real | demo | ... (derived value)
    enabled: Optional[bool] = None       # the is_enabled mirror column


class ListAccountsQueryHandler:
    def __init__(self, account_repo: Any):
        self.account_repo = account_repo

    async def handle(self, query: ListAccountsQuery) -> Tuple[List[Any], int]:
        if self.account_repo is None:
            raise RuntimeError(
                "ListAccountsQueryHandler has no account repository; refusing "
                "to answer with an empty page (register it, or the route 503s)"
            )
        return await self.account_repo.find_page(
            limit=query.limit,
            offset=query.offset,
            group_name=query.group_name,
            account_type=query.account_type,
            enabled=query.enabled,
        )
