"""
Holiday Repository - SQLAlchemy implementation of IHolidayRepository.
"""
from datetime import datetime, date
from decimal import Decimal
from typing import List, Optional

from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from core.domains.instruments.holiday import Holiday
from core.domains.instruments.enums import HolidayMode
from core.ports.interfaces import IHolidayRepository
from infrastructure.persistence.db_models import HolidayModel


class SQLAlchemyHolidayRepository(IHolidayRepository[Holiday]):
    """SQLAlchemy implementation of IHolidayRepository."""

    def __init__(self, session_factory):
        self.session_factory = session_factory

    async def save(self, holiday: Holiday) -> Holiday:
        """Persist a holiday configuration."""
        async with self.session_factory() as session:
            model = self._holiday_to_db(holiday)
            await session.merge(model)
            await session.commit()
            return holiday

    async def save_with_session(self, holiday: Holiday, session: AsyncSession) -> Holiday:
        """Save using an existing session (for Unit of Work)."""
        model = self._holiday_to_db(holiday)
        await session.merge(model)
        return holiday

    async def find_by_id(self, holiday_id: str) -> Optional[Holiday]:
        """Find a holiday by its ID."""
        async with self.session_factory() as session:
            result = await session.execute(
                select(HolidayModel).where(HolidayModel.id == holiday_id)
            )
            model = result.scalar_one_or_none()
            return self._db_to_holiday(model) if model else None

    async def get_active_holidays(self, check_date: datetime) -> List[Holiday]:
        """
        Get all holidays that apply to a given date.
        Matches by month+day, and year=0 (every year) or exact year.
        """
        target = check_date if isinstance(check_date, date) else check_date.date()

        async with self.session_factory() as session:
            stmt = select(HolidayModel).where(
                and_(
                    HolidayModel.mode == HolidayMode.ENABLED.name,
                    HolidayModel.month == target.month,
                    HolidayModel.day == target.day,
                    (HolidayModel.year == 0) | (HolidayModel.year == target.year),
                )
            )
            result = await session.execute(stmt)
            models = result.scalars().all()
            return [self._db_to_holiday(m) for m in models]

    async def get_holidays_for_symbol(
        self, symbol_name: str, year: int
    ) -> List[Holiday]:
        """Get all holidays for a symbol in a given year."""
        async with self.session_factory() as session:
            # Fetch all enabled holidays for the year (or year=0)
            stmt = select(HolidayModel).where(
                and_(
                    HolidayModel.mode == HolidayMode.ENABLED.name,
                    (HolidayModel.year == 0) | (HolidayModel.year == year),
                )
            )
            result = await session.execute(stmt)
            models = result.scalars().all()

            holidays = [self._db_to_holiday(m) for m in models]

            # Filter by symbol applicability in Python
            # (wildcard matching is easier in application code)
            return [
                h for h in holidays
                if h.applies_to_symbol(symbol_name)
            ]

    async def delete(self, holiday_id: str) -> bool:
        """Delete a holiday configuration."""
        async with self.session_factory() as session:
            result = await session.execute(
                select(HolidayModel).where(HolidayModel.id == holiday_id)
            )
            model = result.scalar_one_or_none()
            if model:
                await session.delete(model)
                await session.commit()
                return True
            return False

    async def get_all(self) -> List[Holiday]:
        """Return all holiday configurations."""
        async with self.session_factory() as session:
            result = await session.execute(select(HolidayModel))
            models = result.scalars().all()
            return [self._db_to_holiday(m) for m in models]

    # -----------------------------------------------------------------
    # MAPPERS
    # -----------------------------------------------------------------

    @staticmethod
    def _holiday_to_db(holiday: Holiday) -> "HolidayModel":
        """Map domain Holiday to DB model."""
        return HolidayModel(
            id=holiday.id,
            description=holiday.description,
            mode=holiday.mode.name,
            year=holiday.year,
            month=holiday.month,
            day=holiday.day,
            work_from=holiday.work_from.isoformat(),
            work_to=holiday.work_to.isoformat(),
            symbols=",".join(holiday.symbols) if holiday.symbols else "",
            created_at=holiday.created_at,
            updated_at=holiday.updated_at,
        )

    @staticmethod
    def _db_to_holiday(model: "HolidayModel") -> Holiday:
        """Map DB model to domain Holiday."""
        from datetime import time as dt_time

        work_from = dt_time.fromisoformat(model.work_from) if model.work_from else dt_time(0, 0)
        work_to = dt_time.fromisoformat(model.work_to) if model.work_to else dt_time(23, 59)

        symbols = (
            [s.strip() for s in model.symbols.split(",") if s.strip()]
            if model.symbols
            else []
        )

        return Holiday(
            id=model.id,
            description=model.description or "",
            mode=HolidayMode[model.mode] if model.mode else HolidayMode.ENABLED,
            year=model.year or 0,
            month=model.month or 1,
            day=model.day or 1,
            work_from=work_from,
            work_to=work_to,
            symbols=symbols,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )