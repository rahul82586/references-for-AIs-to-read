"""List Clients query (plan step 8) - paged, SQL-level.

The clients table has 0 rows in live Neon while 45 accounts carry client_ids
that point at nothing (PROJECT-STATE-v6 §0b) - the backfill-or-start-clean
decision is still the user's. Either way this read is the same: an honest
page of whatever the table holds, total included, so a UI can show "0 of 0"
instead of guessing.
"""
from dataclasses import dataclass
from typing import Any, List, Tuple


@dataclass(frozen=True)
class ListClientsQuery:
    limit: int = 100
    offset: int = 0


class ListClientsQueryHandler:
    def __init__(self, client_repo: Any):
        self.client_repo = client_repo

    async def handle(self, query: ListClientsQuery) -> Tuple[List[Any], int]:
        if self.client_repo is None:
            raise RuntimeError(
                "ListClientsQueryHandler has no client repository; refusing to "
                "answer with an empty page (register it, or the route 503s)"
            )
        return await self.client_repo.find_page(limit=query.limit, offset=query.offset)
