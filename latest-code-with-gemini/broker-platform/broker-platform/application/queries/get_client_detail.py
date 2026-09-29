"""Get Client Detail query (plan step 8).

One person/company record (IMTClient). Credential material on the client row
is the DEPRECATED location (step 5: MT5 keeps password material per ACCOUNT on
IMTUser) and is never serialized - the router exposes booleans, not hashes.
"""
from dataclasses import dataclass
from typing import Any


class ClientNotFoundError(ValueError):
    """No client with that id. 404 at the route - never a fabricated record."""


@dataclass(frozen=True)
class GetClientDetailQuery:
    client_id: str


class GetClientDetailQueryHandler:
    def __init__(self, client_repo: Any):
        self.client_repo = client_repo

    async def handle(self, query: GetClientDetailQuery) -> Any:
        if self.client_repo is None:
            raise RuntimeError("GetClientDetailQueryHandler has no client repository")
        client = await self.client_repo.find_by_id(query.client_id)
        if client is None:
            raise ClientNotFoundError(f"no client with id {query.client_id}")
        return client
