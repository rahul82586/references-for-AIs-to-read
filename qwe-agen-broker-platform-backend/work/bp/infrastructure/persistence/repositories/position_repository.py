from datetime import datetime
from decimal import Decimal
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
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

    async def find_by_id(self, position_id: str, session: Optional[AsyncSession] = None) -> Optional[Position]:
        async def _find(sess: AsyncSession):
            result = await sess.execute(
                select(PositionModel).where(PositionModel.position_id == position_id)
            )
            model = result.scalar_one_or_none()
            return db_to_position(model) if model else None

        if session:
            return await _find(session)
        async with self.session_factory() as sess:
            return await _find(sess)

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

    async def get_positions_by_account(
        self, account_login: int, session: Optional[AsyncSession] = None
    ) -> List[Position]:
        """Open positions for one account - the canonical name in IPositionRepository.

        This method did not exist. record_deal._recalculate_account_margin probes for
        `get_positions_by_account`, then `find_by_account`, and falls back to an EMPTY
        list when neither is present - and this repository had neither, only the
        `get_by_account` alias. So after every deal against the real PostgreSQL
        repositories it recomputed margin over zero positions and wrote
        margin_used = 0, margin_free = equity: an account looked flat and unleveraged
        the moment it opened its first trade, and the stop-out logic that reads those
        figures could never fire. The silent `else: []` fallback is what made it
        invisible, and the unit tests passed because their doubles happened to define
        the probed name.
        """
        async def _get(sess: AsyncSession):
            result = await sess.execute(
                select(PositionModel).where(
                    (PositionModel.account_login == account_login) &
                    (PositionModel.time_done.is_(None))
                )
            )
            models = result.scalars().all()
            return [db_to_position(m) for m in models]

        if session:
            return await _get(session)
        async with self.session_factory() as sess:
            return await _get(sess)

    async def find_by_account(
        self, account_login: int, session: Optional[AsyncSession] = None
    ) -> List[Position]:
        """Second name record_deal probes for. Same query as get_positions_by_account."""
        return await self.get_positions_by_account(account_login, session=session)

    async def get_by_account(
        self, account_login: int, session: Optional[AsyncSession] = None
    ) -> List[Position]:
        """Alias kept for the risk engine, liquidation worker and tick pipeline."""
        return await self.get_positions_by_account(account_login, session=session)

    async def update_valuation(self, position_id: str, side: str,
                               price_current: Decimal, when=None,
                               session: Optional[AsyncSession] = None) -> Optional[dict]:
        """D15: write a revaluation without writing the rest of the row.

        `save()` is a full-row merge, and the tick pipeline holds objects it
        fetched before it did its work. Persisting those races anything else that
        moved the position in between - observed live against Neon as a partial
        close being UNDONE by the next tick, so the following close dealt the
        position's ORIGINAL volume. D8b gave accounts a column-scoped write for
        precisely this reason; this is the position equivalent.

        Two things make it safe rather than merely narrower:

        * the PnL is computed IN THE STATEMENT from the volume and open price the
          row holds at write time, so a concurrent partial close changes the result
          instead of being overwritten by it;
        * `time_done IS NULL` means a tick can never reopen or reprice a position
          that a close, the SL/TP worker or the liquidation worker has finished.

        `side` is the position's own action, so the statement can value a long at
        the price it can SELL at and a short at the price it can BUY back at.

        Returns {"volume", "profit", "price_current"} as Decimals for the row that
        was written, or None if it was closed or vanished - the caller must then
        drop the position from its view of the account rather than keep a number
        for a position that no longer exists.
        """
        from datetime import datetime as _dt, timezone as _tz

        from sqlalchemy import text as sa_text

        stmt = sa_text(
            "UPDATE positions SET "
            "price_current = CAST(:price AS DECIMAL(20,8)), "
            "profit = CAST(CASE WHEN :side = 'BUY' "
            "THEN (:price - price_open) "
            "ELSE (price_open - :price) END "
            "* volume * contract_size AS DECIMAL(20,8)), "
            "time_update = :when "
            "WHERE position_id = :position_id AND time_done IS NULL "
            "RETURNING volume, profit, price_current"
        )
        params = {
            "price": str(price_current),
            # normalised: the statement only ever compares against 'BUY'
            "side": "BUY" if str(side).upper().startswith("BUY") else "SELL",
            "when": when or _dt.now(_tz.utc),
            "position_id": position_id,
        }
        return await self._execute_valuation(stmt, params, session)

    async def _execute_valuation(self, stmt, params, session) -> Optional[dict]:
        async def _run(sess):
            result = await sess.execute(stmt, params)
            row = result.first()
            if row is None:
                return None
            return {
                "volume": Decimal(str(row[0])),
                "profit": Decimal(str(row[1])),
                "price_current": Decimal(str(row[2])),
            }

        if session is not None:
            return await _run(session)
        async with self.session_factory() as sess:
            out = await _run(sess)
            await sess.commit()
            return out

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