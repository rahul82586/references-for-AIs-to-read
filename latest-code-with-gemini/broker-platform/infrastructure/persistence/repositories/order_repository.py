from datetime import datetime
from typing import List, Optional
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from core.domains.oms.entities.order import Order, OrderState
from core.ports.interfaces import IOrderRepository
from ..mappers import order_to_db, db_to_order
from ..db_models import OrderModel

class SqlOrderRepository(IOrderRepository[Order]):
    """PostgreSQL implementation of IOrderRepository."""

    def __init__(self, session_factory):
        self.session_factory = session_factory

    async def save(self, order: Order, session: Optional[AsyncSession] = None) -> Order:
        """Save or update an order."""
        async def _save(sess: AsyncSession):
            model = order_to_db(order)
            await sess.merge(model)
            return order

        if session:
            return await _save(session)
        async with self.session_factory() as sess:
            result = await _save(sess)
            await sess.commit()
            return result

    async def find_by_id(self, order_id: str, session: Optional[AsyncSession] = None) -> Optional[Order]:
        """One order by ticket. Accepts the unit-of-work session the port declares.

        IOrderRepository declares `find_by_id(order_id, session=None)`, and this did not
        take the parameter. RecordDealHandler probes for it and passes it through when a
        unit of work is active, so recording a fill inside a transaction raised
        TypeError. The probe is what made this survivable outside a UoW - and the probe
        itself was broken, see _accepts_session().
        """
        async def _find(sess: AsyncSession):
            result = await sess.execute(
                select(OrderModel).where(OrderModel.ticket_id == order_id)
            )
            model = result.scalar_one_or_none()
            return db_to_order(model) if model else None

        if session is not None:
            return await _find(session)
        async with self.session_factory() as sess:
            return await _find(sess)

    #: MT5 order states split: terminal states belong to HISTORY, the rest are
    #: the active book. Stored values are the enum's .value strings.
    _TERMINAL_STATES = ("CANCELLED", "FILLED", "REJECTED", "EXPIRED")
    _ACTIVE_STATES = ("STARTED", "PLACED", "PARTIALLY_FILLED")

    async def find_page(
        self,
        limit: int = 100,
        offset: int = 0,
        account_login: Optional[int] = None,
        symbol: Optional[str] = None,
        state: Optional[str] = None,
        history: Optional[bool] = None,
        session: Optional[AsyncSession] = None,
    ):
        """Paged cross-account order read (ENDPOINTS B2).

        `history` is a TRI-STATE, because the UI has two pages: None = every
        order, False = the active book (STARTED/PLACED/PARTIALLY_FILLED),
        True = history (CANCELLED/FILLED/REJECTED/EXPIRED). `state` narrows
        further and is refused if it contradicts `history` - serving the
        intersection of "active" and "FILLED" as an empty page that looks like
        a filter result would be the silent-lie pattern again.
        """
        if state is not None and history is not None:
            in_terminal = state in self._TERMINAL_STATES
            if in_terminal != bool(history):
                raise ValueError(
                    f"state={state!r} contradicts history={history!r}: "
                    f"terminal states are {self._TERMINAL_STATES}"
                )
        async def _page(sess: AsyncSession):
            conds = []
            if account_login is not None:
                conds.append(OrderModel.account_login == int(account_login))
            if symbol is not None:
                conds.append(OrderModel.symbol == symbol)
            if state is not None:
                conds.append(OrderModel.state == state)
            elif history is not None:
                states = self._TERMINAL_STATES if history else self._ACTIVE_STATES
                conds.append(OrderModel.state.in_(states))
            count_stmt = select(func.count()).select_from(OrderModel)
            stmt = select(OrderModel)
            for c in conds:
                count_stmt = count_stmt.where(c)
                stmt = stmt.where(c)
            total = (await sess.execute(count_stmt)).scalar() or 0
            stmt = stmt.order_by(OrderModel.time_setup.desc(), OrderModel.ticket_id).limit(limit).offset(offset)
            models = (await sess.execute(stmt)).scalars().all()
            return [db_to_order(m) for m in models], int(total)

        if session:
            return await _page(session)
        async with self.session_factory() as sess:
            return await _page(sess)

    async def find_by_account(self, account_login: int) -> List[Order]:
        async with self.session_factory() as session:
            result = await session.execute(
                select(OrderModel).where(OrderModel.account_login == account_login)
            )
            models = result.scalars().all()
            return [db_to_order(m) for m in models]

    async def find_pending_orders(self, account_login: int) -> List[Order]:
        """Get all pending orders (not in terminal state)."""
        from core.domains.oms.enums import OrderState
        terminal_states = [OrderState.FILLED.value, OrderState.CANCELLED.value,
                          OrderState.REJECTED.value, OrderState.EXPIRED.value]
        
        async with self.session_factory() as session:
            result = await session.execute(
                select(OrderModel).where(
                    (OrderModel.account_login == account_login) &
                    (OrderModel.state.notin_(terminal_states))
                )
            )
            models = result.scalars().all()
            return [db_to_order(m) for m in models]

    async def find_by_symbol_and_state(self, symbol: str, state: str) -> List[Order]:
        async with self.session_factory() as session:
            result = await session.execute(
                select(OrderModel).where(
                    (OrderModel.symbol == symbol) &
                    (OrderModel.state == state)
                )
            )
            models = result.scalars().all()
            return [db_to_order(m) for m in models]

    async def find_expired_orders(self, before_time: datetime) -> List[Order]:
        """Get orders that have expired."""
        async with self.session_factory() as session:
            result = await session.execute(
                select(OrderModel).where(
                    (OrderModel.time_expiration < before_time) &
                    (OrderModel.state.in_(["STARTED", "NEW", "PLACED", "PARTIALLY_FILLED"]))
                )
            )
            models = result.scalars().all()
            return [db_to_order(m) for m in models]

    async def delete(self, order_id: str) -> bool:
        async with self.session_factory() as session:
            result = await session.execute(
                select(OrderModel).where(OrderModel.ticket_id == order_id)
            )
            model = result.scalar_one_or_none()
            if model:
                await session.delete(model)
                await session.commit()
                return True
            return False