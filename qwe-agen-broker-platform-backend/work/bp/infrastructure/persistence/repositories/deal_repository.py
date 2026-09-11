from typing import List, Optional, Any
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from core.domains.oms.entities.deal import Deal
from core.ports.interfaces import IDealRepository
from ..mappers import deal_to_db, db_to_deal
from ..db_models import DealModel


class SqlDealRepository(IDealRepository[Deal]):
    """PostgreSQL implementation of IDealRepository."""

    def __init__(self, session_factory):
        self.session_factory = session_factory

    async def save(self, deal: Deal, session: Optional[AsyncSession] = None) -> Deal:
        async def _save(sess: AsyncSession):
            model = deal_to_db(deal)
            await sess.merge(model)
            return deal

        if session:
            return await _save(session)
        async with self.session_factory() as sess:
            result = await _save(sess)
            await sess.commit()
            return result

    async def find_by_id(self, deal_id: str, session: Optional[AsyncSession] = None) -> Optional[Deal]:
        """One deal by id. Accepts the unit-of-work session IDealRepository declares."""
        async def _find(sess: AsyncSession):
            result = await sess.execute(
                select(DealModel).where(DealModel.deal_id == deal_id)
            )
            model = result.scalar_one_or_none()
            return db_to_deal(model) if model else None

        if session is not None:
            return await _find(session)
        async with self.session_factory() as sess:
            return await _find(sess)

    async def find_by_order_id(self, order_id: str) -> List[Deal]:
        async with self.session_factory() as session:
            result = await session.execute(
                select(DealModel).where(DealModel.order_id == order_id)
            )
            models = result.scalars().all()
            return [db_to_deal(m) for m in models]

    async def find_by_position_id(self, position_id: str) -> List[Deal]:
        async with self.session_factory() as session:
            result = await session.execute(
                select(DealModel).where(DealModel.position_id == position_id)
            )
            models = result.scalars().all()
            return [db_to_deal(m) for m in models]

    async def find_by_account(self, account_login: int) -> List[Deal]:
        async with self.session_factory() as session:
            result = await session.execute(
                select(DealModel).where(DealModel.account_login == account_login)
            )
            models = result.scalars().all()
            return [db_to_deal(m) for m in models]

    async def find_by_account_and_symbol(self, account_login: int, symbol: str) -> List[Deal]:
        async with self.session_factory() as session:
            result = await session.execute(
                select(DealModel).where(
                    (DealModel.account_login == account_login) &
                    (DealModel.symbol == symbol)
                )
            )
            models = result.scalars().all()
            return [db_to_deal(m) for m in models]

    async def find_by_entry_type(self, account_login: int, entry: str) -> List[Deal]:
        async with self.session_factory() as session:
            result = await session.execute(
                select(DealModel).where(
                    (DealModel.account_login == account_login) &
                    (DealModel.entry == entry)
                )
            )
            models = result.scalars().all()
            return [db_to_deal(m) for m in models]

    async def find_trade_modifications(self, original_deal_id: str) -> List[Deal]:
        """Get reversal and correction deals linked to original deal."""
        async with self.session_factory() as session:
            # Search for deals with comment containing the original deal_id
            result = await session.execute(
                select(DealModel).where(
                    DealModel.comment.contains(f"[REVERSAL of {original_deal_id}]") |
                    DealModel.comment.contains(f"[CORRECTION of {original_deal_id}]")
                )
            )
            models = result.scalars().all()
            return [db_to_deal(m) for m in models]