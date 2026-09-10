from typing import List, Optional
from sqlalchemy import select
from core.domains.oms.entities.position import Position
from core.ports.interfaces import IPositionRepository
from ..mappers import position_to_db, db_to_position
from ..db_models import PositionModel

class SqlPositionRepository(IPositionRepository[Position]):
    """PostgreSQL implementation of IPositionRepository."""

    def __init__(self, session_factory):
        self.session_factory = session_factory

    async def save(self, position: Position, session: Optional[AsyncSession] = None) -> Position:
        async def _save(sess: AsyncSession):
            model = position_to_db(position)
            await sess.merge(model)
            return position

        if session:
            return await _save(session)
        async with self.session_factory() as sess:
            result = await _save(sess)
            await sess.commit()
            return result

    async def find_by_id(self, position_id: str) -> Optional[Position]:
        async with self.session_factory() as session:
            result = await session.execute(
                select(PositionModel).where(PositionModel.position_id == position_id)
            )
            model = result.scalar_one_or_none()
            return db_to_position(model) if model else None

    async def get_open_positions(self, session: Optional[AsyncSession] = None) -> List[Position]:
        """Get all open positions (time_done is NULL)."""
        async def _get(sess: AsyncSession):
            result = await sess.execute(
                select(PositionModel).where(PositionModel.time_done.is_(None))
            )
            models = result.scalars().all()
            return [db_to_position(m) for m in models]

        if session:
            return await _get(session)
        async with self.session_factory() as sess:
            return await _get(sess)

    async def get_by_account(self, account_login: int) -> List[Position]:
        async with self.session_factory() as session:
            result = await session.execute(
                select(PositionModel).where(
                    (PositionModel.account_login == account_login) &
                    (PositionModel.time_done.is_(None))
                )
            )
            models = result.scalars().all()
            return [db_to_position(m) for m in models]

    async def get_by_account_and_symbol(self, account_login: int, symbol: str) -> List[Position]:
        async with self.session_factory() as session:
            result = await session.execute(
                select(PositionModel).where(
                    (PositionModel.account_login == account_login) &
                    (PositionModel.symbol == symbol) &
                    (PositionModel.time_done.is_(None))
                )
            )
            models = result.scalars().all()
            return [db_to_position(m) for m in models]

    async def get_by_symbol(self, symbol: str) -> List[Position]:
        async with self.session_factory() as session:
            result = await session.execute(
                select(PositionModel).where(
                    (PositionModel.symbol == symbol) &
                    (PositionModel.time_done.is_(None))
                )
            )
            models = result.scalars().all()
            return [db_to_position(m) for m in models]

    async def get_closed_positions(self, account_login: int, from_time: datetime, to_time: datetime) -> List[Position]:
        async with self.session_factory() as session:
            result = await session.execute(
                select(PositionModel).where(
                    (PositionModel.account_login == account_login) &
                    (PositionModel.time_done >= from_time) &
                    (PositionModel.time_done <= to_time)
                )
            )
            models = result.scalars().all()
            return [db_to_position(m) for m in models]

    async def delete(self, position_id: str) -> bool:
        async with self.session_factory() as session:
            result = await session.execute(
                select(PositionModel).where(PositionModel.position_id == position_id)
            )
            model = result.scalar_one_or_none()
            if model:
                await session.delete(model)
                await session.commit()
                return True
            return False