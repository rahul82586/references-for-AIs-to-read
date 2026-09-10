from typing import List, Optional
from sqlalchemy import select
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

    async def find_by_id(self, order_id: str) -> Optional[Order]:
        async with self.session_factory() as session:
            result = await session.execute(
                select(OrderModel).where(OrderModel.ticket_id == order_id)
            )
            model = result.scalar_one_or_none()
            return db_to_order(model) if model else None

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
                    (OrderModel.state.in_(["NEW", "PLACED", "PARTIALLY_FILLED"]))
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