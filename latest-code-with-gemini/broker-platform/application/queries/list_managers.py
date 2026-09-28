"""List Managers query (plan step 8).

Step 7 built the manager WRITES and the single-manager read (GET /{login},
rights decoded to names). The plane had no LIST: an admin UI cannot render
the Managers table, and `admin_router`'s legacy GET /managers counts bits for
display without paging. This is the paged source; the route reuses step 7's
_manager_payload so one serializer owns the manager wire shape (the D18
lesson: never two builders of one shape).
"""
from dataclasses import dataclass
from typing import Any, List, Tuple


@dataclass(frozen=True)
class ListManagersQuery:
    limit: int = 100
    offset: int = 0


class ListManagersQueryHandler:
    def __init__(self, manager_repo: Any):
        self.manager_repo = manager_repo

    async def handle(self, query: ListManagersQuery) -> Tuple[List[Any], int]:
        if self.manager_repo is None:
            raise RuntimeError(
                "ListManagersQueryHandler has no manager repository; refusing "
                "to answer with an empty page (register it, or the route 503s)"
            )
        return await self.manager_repo.find_page(limit=query.limit, offset=query.offset)
