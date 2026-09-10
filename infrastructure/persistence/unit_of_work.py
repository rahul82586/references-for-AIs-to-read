from typing import Optional, Any
from sqlalchemy.ext.asyncio import AsyncSession
from infrastructure.persistence.repositories.order_repository import SqlOrderRepository
from infrastructure.persistence.repositories.deal_repository import SqlDealRepository
from infrastructure.persistence.repositories.position_repository import SqlPositionRepository
from infrastructure.persistence.repositories.account_repository import SqlAccountRepository, SqlGroupRepository


class UnitOfWork:
    """
    Unit of Work Pattern.
    Manages a single database session transaction spanning multiple repositories.
    Guarantees atomic commit/rollback across Order, Deal, Position, and Account updates.
    """

    def __init__(self, session_factory=None, session: Optional[AsyncSession] = None):
        self.session_factory = session_factory
        self._external_session = session
        self.session: Optional[AsyncSession] = None

    async def __aenter__(self) -> 'UnitOfWork':
        if self._external_session is not None:
            self.session = self._external_session
        elif self.session_factory is not None:
            self.session = self.session_factory()
            if hasattr(self.session, '__aenter__'):
                self.session = await self.session.__aenter__()

        # Instantiate repositories bound to this shared session
        self.orders = SqlOrderRepository()
        self.deals = SqlDealRepository()
        self.positions = SqlPositionRepository()
        group_repo = SqlGroupRepository(self.session_factory)
        self.accounts = SqlAccountRepository(group_repo=group_repo)

        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            await self.rollback()
        else:
            await self.commit()

        if self._external_session is None and self.session is not None:
            if hasattr(self.session, '__aexit__'):
                await self.session.__aexit__(exc_type, exc_val, exc_tb)
            elif hasattr(self.session, 'close'):
                await self.session.close()

    async def commit(self):
        if self.session is not None and hasattr(self.session, 'commit'):
            await self.session.commit()

    async def rollback(self):
        if self.session is not None and hasattr(self.session, 'rollback'):
            await self.session.rollback()
