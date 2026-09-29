from datetime import datetime
from typing import List, Optional, Any
from sqlalchemy import func, select, or_
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

    async def find_page(
        self,
        limit: int = 100,
        offset: int = 0,
        account_login: Optional[int] = None,
        account_logins: Optional[List[int]] = None,
        ticket: Optional[str] = None,
        symbol: Optional[str] = None,
        entry: Optional[str] = None,
        from_time: Optional[datetime] = None,
        to_time: Optional[datetime] = None,
        session: Optional[AsyncSession] = None,
    ):
        """Paged cross-account deal read (ENDPOINTS B2 - the UI's Deals page had
        NO data source on any plane). Filters: account_login, symbol, entry
        (IN/OUT/INOUT/OUT_BY). Newest first: created_at desc, deal_id tie-break.
        """
        async def _page(sess: AsyncSession):
            conds = []
            if account_logins:
                conds.append(DealModel.account_login.in_(account_logins))
            elif account_login is not None:
                conds.append(DealModel.account_login == int(account_login))
            if ticket is not None and ticket.strip():
                t = ticket.strip()
                conds.append(or_(
                    DealModel.deal_id == t,
                    DealModel.order_id == t,
                    DealModel.position_id == t,
                    DealModel.external_id == t
                ))
            if symbol is not None and symbol.strip() and symbol.strip() != "*":
                sym_clean = symbol.strip()
                if sym_clean.endswith("*"):
                    prefix = sym_clean[:-1].replace("/", "\\")
                    conds.append(or_(DealModel.symbol.like(f"{prefix}%"), DealModel.symbol.ilike(f"%\\{prefix}%")))
                else:
                    leaf = sym_clean.split("\\")[-1].split("/")[-1].strip()
                    conds.append(or_(DealModel.symbol == sym_clean, DealModel.symbol == leaf, DealModel.symbol.ilike(f"%\\{leaf}")))
            if entry is not None:
                conds.append(DealModel.entry == entry)
            if from_time is not None:
                conds.append(DealModel.created_at >= from_time)
            if to_time is not None:
                conds.append(DealModel.created_at <= to_time)
            count_stmt = select(func.count()).select_from(DealModel)
            stmt = select(DealModel)
            for c in conds:
                count_stmt = count_stmt.where(c)
                stmt = stmt.where(c)
            total = (await sess.execute(count_stmt)).scalar() or 0
            stmt = stmt.order_by(DealModel.created_at.desc(), DealModel.deal_id).limit(limit).offset(offset)
            models = (await sess.execute(stmt)).scalars().all()
            return [db_to_deal(m) for m in models], int(total)

        if session:
            return await _page(session)
        async with self.session_factory() as sess:
            return await _page(sess)

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