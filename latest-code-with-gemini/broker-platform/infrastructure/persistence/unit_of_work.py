from typing import Optional, Any
from sqlalchemy.ext.asyncio import AsyncSession
from infrastructure.persistence.repositories.order_repository import SqlOrderRepository
from infrastructure.persistence.repositories.deal_repository import SqlDealRepository
from infrastructure.persistence.repositories.position_repository import SqlPositionRepository
from infrastructure.persistence.repositories.account_repository import SqlAccountRepository, SqlGroupRepository


class _SharedSessionFactory:
    """Adapts one AsyncSession to the ``session_factory`` repositories expect.

    Repositories call the factory to obtain a session. Returning the same session every
    time is what makes them participants in one transaction rather than four independent
    ones.

    The session's lifecycle is NOT owned here: ``UnitOfWork.__aexit__`` commits or rolls
    back and closes it. A factory that closed the session on first use would end the
    transaction part-way through, which is the failure mode this exists to prevent.
    """

    def __init__(self, session) -> None:
        self._session = session

    def __call__(self):
        return self._session

    def __getattr__(self, name):
        # Anything else a repository might expect of a sessionmaker (e.g. `.kw`) falls
        # through to the session itself rather than raising AttributeError.
        return getattr(self._session, name)


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

        if self.session is None:
            raise RuntimeError(
                "UnitOfWork entered with neither a session nor a session_factory; there is "
                "nothing to bind the repositories to"
            )

        # Bind every repository to THIS session, not to the factory. Handing them the
        # factory - as this did - makes each one open its own session, which defeats the
        # unit of work: the margin reserve and the order persist would commit separately,
        # so a failure between them leaves margin reserved against an order that was never
        # written. The shim adapts the session to the session_factory argument the
        # repositories expect, so their internals are untouched.
        shared = _SharedSessionFactory(self.session)
        self.orders = SqlOrderRepository(shared)
        self.deals = SqlDealRepository(shared)
        self.positions = SqlPositionRepository(shared)
        group_repo = SqlGroupRepository(shared)
        self.accounts = SqlAccountRepository(session_factory=shared, group_repo=group_repo)

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
