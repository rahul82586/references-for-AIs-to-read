from typing import Any, Optional, List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.domains.accounts.models import Account, Group
from core.ports.interfaces import IAccountRepository, IGroupRepository
# SqlGroupRepository lives in group_repository.py. It used to be defined
# here as well, and the two copies drifted.
from .group_repository import SqlGroupRepository  # noqa: F401
from infrastructure.persistence.db_models import AccountModel, GroupModel
from infrastructure.persistence.mappers import account_to_db, db_to_account, group_to_db, db_to_group


class SqlAccountRepository(IAccountRepository):
    """PostgreSQL implementation of IAccountRepository."""

    def __init__(self, session_factory=None, group_repo: Optional[IGroupRepository] = None):
        self.session_factory = session_factory
        self.group_repo = group_repo

    async def find_by_login(self, login_id: Any, session: Optional[AsyncSession] = None) -> Optional[Account]:
        # accounts.login is String(32) - MT5's natural key - but the rest of the platform
        # identifies an account with an int: Order.account_login, Position.account_login,
        # Deal.account_login and their BigInteger columns all are. Every caller on the
        # execution path therefore arrives with an int, and `session.get(AccountModel, 900101)`
        # binds an INTEGER against a TEXT primary key: SQLite compares the two as
        # different types and finds nothing, PostgreSQL raises "operator does not exist:
        # character varying = integer". Coercing here keeps the string key where it
        # belongs - at the storage boundary - instead of leaking into the domain.
        login_id = str(login_id)

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
    async def find_all(self):
        """Every account. ConfigCache loads this once at startup."""
        async with self.session_factory() as session:
            result = await session.execute(select(AccountModel))
            models = result.scalars().all()
            out = []
            for model in models:
                group = None
                if self.group_repo is not None and model.group_name:
                    group = await self.group_repo.find_by_name(model.group_name)
                out.append(db_to_account(model, group))
            return out

    async def save_model(self, model) -> None:
        """Persist an AccountModel row directly."""
        async with self.session_factory() as session:
            await session.merge(model)
            await session.commit()
