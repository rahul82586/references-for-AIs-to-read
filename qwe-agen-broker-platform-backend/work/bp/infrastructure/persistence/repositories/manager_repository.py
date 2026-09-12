"""
Repositories for the Manager (administrator/dealer) and Client planes.

MT5's model, which these follow: a Manager has a login, a positional 128-element rights
array, and a Groups scope limiting which client groups it may administer. A Client is
the person or company (MT5 IMTUser) and owns one or more trading Accounts (IMTAccount).
Keeping those two apart is what lets one person hold a demo, a real and a contest
account without duplicating their KYC data.
"""
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.domains.accounts.client import Client
from core.domains.identity.models import ManagerAccount
from core.ports.interfaces import IManagerRepository

from ..account_models import (
    client_to_db,
    db_to_client,
    db_to_manager,
    manager_to_db,
)
from ..manager_models import ClientModel, ManagerModel


class SqlManagerRepository(IManagerRepository):
    """PostgreSQL implementation of IManagerRepository."""

    def __init__(self, session_factory):
        self.session_factory = session_factory

    async def find_by_login(self, login: str) -> Optional[ManagerAccount]:
        async with self.session_factory() as session:
            result = await session.execute(
                select(ManagerModel).where(ManagerModel.login == int(login))
            )
            model = result.scalar_one_or_none()
            return db_to_manager(model) if model else None

    async def save(self, manager: ManagerAccount) -> ManagerAccount:
        async with self.session_factory() as session:
            model = manager_to_db(manager)
            await session.merge(model)
            await session.commit()
            return manager

    async def save_model(self, model: ManagerModel) -> None:
        """Persist a ManagerModel row directly, preserving imported MT5 metadata."""
        async with self.session_factory() as session:
            await session.merge(model)
            await session.commit()

    async def find_all(self) -> List[ManagerAccount]:
        async with self.session_factory() as session:
            result = await session.execute(select(ManagerModel))
            return [db_to_manager(m) for m in result.scalars().all()]

    async def count(self) -> int:
        """How many managers exist. `seed` uses this to decide on first-admin bootstrap."""
        async with self.session_factory() as session:
            result = await session.execute(select(ManagerModel))
            return len(result.scalars().all())


class SqlClientRepository:
    """PostgreSQL persistence for Client (MT5 IMTUser).

    There is no IClientRepository port yet; adding one is part of wiring
    CreateClientHandler, which needs the port to be injectable.
    """

    def __init__(self, session_factory):
        self.session_factory = session_factory

    async def find_by_id(self, client_id: str) -> Optional[Client]:
        async with self.session_factory() as session:
            result = await session.execute(
                select(ClientModel).where(ClientModel.id == client_id)
            )
            model = result.scalar_one_or_none()
            return db_to_client(model) if model else None

    async def save(self, client: Client) -> Client:
        async with self.session_factory() as session:
            model = client_to_db(client)
            await session.merge(model)
            await session.commit()
            return client

    async def find_all(self) -> List[Client]:
        async with self.session_factory() as session:
            result = await session.execute(select(ClientModel))
            return [db_to_client(m) for m in result.scalars().all()]
