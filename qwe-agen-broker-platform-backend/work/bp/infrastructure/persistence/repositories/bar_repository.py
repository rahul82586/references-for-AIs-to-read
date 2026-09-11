"""
PostgreSQL Bar Repository Implementation

Provides database persistence and querying for aggregated OHLCV rate bars using SQLAlchemy.

Architectural Rule: Infrastructure repository adapter implementing IBarRepository port.
"""
from decimal import Decimal
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.domains.market_data.models import Bar, BarTimeframe
from core.ports.interfaces import IBarRepository
from infrastructure.persistence.db_models import BarModel


class BarRepository(IBarRepository):
    """
    SQLAlchemy async repository for OHLCV bars.
    """
    def __init__(self, session_factory):
        self.session_factory = session_factory

    async def save_bar(self, bar: Bar) -> Bar:
        """Persist or update an OHLCV bar in PostgreSQL."""
        tf_str = bar.timeframe.value if isinstance(bar.timeframe, BarTimeframe) else str(bar.timeframe)
        async with self.session_factory() as session:
            async with session.begin():
                db_bar = BarModel(
                    symbol=bar.symbol,
                    timeframe=tf_str,
                    open=bar.open,
                    high=bar.high,
                    low=bar.low,
                    close=bar.close,
                    tick_volume=bar.tick_volume,
                    open_time=bar.open_time,
                    close_time=bar.close_time
                )
                session.add(db_bar)
            await session.commit()
        return bar

    async def get_bars(self, symbol: str, timeframe: BarTimeframe, count: int = 100) -> List[Bar]:
        """Retrieve recent historical bars for a symbol and timeframe sorted chronologically."""
        tf_str = timeframe.value if isinstance(timeframe, BarTimeframe) else str(timeframe)
        async with self.session_factory() as session:
            stmt = (
                select(BarModel)
                .where(BarModel.symbol == symbol, BarModel.timeframe == tf_str)
                .order_by(BarModel.open_time.desc())
                .limit(count)
            )
            result = await session.execute(stmt)
            db_bars = result.scalars().all()

        # Convert to domain objects and reverse to ascending chronological order
        domain_bars = [
            Bar(
                symbol=row.symbol,
                timeframe=BarTimeframe(row.timeframe),
                open=Decimal(str(row.open)),
                high=Decimal(str(row.high)),
                low=Decimal(str(row.low)),
                close=Decimal(str(row.close)),
                tick_volume=row.tick_volume,
                open_time=row.open_time,
                close_time=row.close_time
            )
            for row in reversed(db_bars)
        ]
        return domain_bars

    async def get_latest_bar(self, symbol: str, timeframe: BarTimeframe) -> Optional[Bar]:
        """Retrieve the latest bar for a symbol and timeframe."""
        tf_str = timeframe.value if isinstance(timeframe, BarTimeframe) else str(timeframe)
        async with self.session_factory() as session:
            stmt = (
                select(BarModel)
                .where(BarModel.symbol == symbol, BarModel.timeframe == tf_str)
                .order_by(BarModel.open_time.desc())
                .limit(1)
            )
            result = await session.execute(stmt)
            row = result.scalars().first()

        if not row:
            return None

        return Bar(
            symbol=row.symbol,
            timeframe=BarTimeframe(row.timeframe),
            open=Decimal(str(row.open)),
            high=Decimal(str(row.high)),
            low=Decimal(str(row.low)),
            close=Decimal(str(row.close)),
            tick_volume=row.tick_volume,
            open_time=row.open_time,
            close_time=row.close_time
        )
