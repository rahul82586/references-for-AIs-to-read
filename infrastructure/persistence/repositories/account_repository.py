from typing import Optional, List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.domains.accounts.models import Account, Group
from core.ports.interfaces import IAccountRepository, IGroupRepository
from infrastructure.persistence.db_models import AccountModel, GroupModel
from infrastructure.persistence.mappers import account_to_db, db_to_account, group_to_db, db_to_group


class SqlGroupRepository(IGroupRepository):
    """PostgreSQL implementation of IGroupRepository."""

    def __init__(self, session_factory):
        self.session_factory = session_factory

    async def find_by_name(self, name: str) -> Optional[Group]:
        async with self.session_factory() as session:
            model = await session.get(GroupModel, name)
            if not model:
                return None
            return db_to_group(model)

    async def save(self, group: Group) -> Group:
        async with self.session_factory() as session:
            model = group_to_db(group)
            await session.merge(model)
            await session.commit()
            return group

    async def get_all(self) -> List[Group]:
        async with self.session_factory() as session:
            result = await session.execute(select(GroupModel))
            models = result.scalars().all()
            return [db_to_group(m) for m in models]


class SqlAccountRepository(IAccountRepository):
    """PostgreSQL implementation of IAccountRepository."""

    def __init__(self, session_factory=None, group_repo: Optional[IGroupRepository] = None):
        self.session_factory = session_factory
        self.group_repo = group_repo

    async def find_by_login(self, login_id: str, session: Optional[AsyncSession] = None) -> Optional[Account]:
        if session is not None:
            model = await session.get(AccountModel, login_id)
            if not model:
                return None
            group = await self.group_repo.find_by_name(model.group_name) if self.group_repo else None
            return db_to_account(model, group)

        async with self.session_factory() as sess:
            model = await sess.get(AccountModel, login_id)
            if not model:
                return None
            group = await self.group_repo.find_by_name(model.group_name) if self.group_repo else None
            return db_to_account(model, group)

    async def save(self, account: Account, session: Optional[AsyncSession] = None) -> Account:
        model = account_to_db(account)
        if session is not None:
            await session.merge(model)
            return account
        async with self.session_factory() as sess:
            await sess.merge(model)
            await sess.commit()
            return account

    async def get_all_accounts(self) -> List[Account]:
        async with self.session_factory() as session:
            result = await session.execute(select(AccountModel))
            models = result.scalars().all()
            accounts = []
            for model in models:
                group = await self.group_repo.find_by_name(model.group_name)
                accounts.append(db_to_account(model, group))
            return accounts

    async def get_all_with_positions(self) -> List[str]:
        """Return login IDs of all accounts that have open positions."""
        from infrastructure.persistence.db_models import PositionModel
        async with self.session_factory() as session:
            result = await session.execute(
                select(PositionModel.account_login).distinct()
            )
            return [row[0] for row in result.fetchall()]
