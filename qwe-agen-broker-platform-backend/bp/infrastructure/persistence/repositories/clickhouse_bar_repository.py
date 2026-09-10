"""
ClickHouse Bar Repository Implementation.
"""
from datetime import datetime, timezone
from decimal import Decimal
from typing import Any, List

from core.domains.market_data.models import Bar, BarTimeframe
from core.ports.interfaces import IHistoricalBarRepository
from infrastructure.persistence.clickhouse_client import ClickHouseClient


class ClickHouseBarRepository(IHistoricalBarRepository):
    """
    Persists historical OHLCV rate bars to ClickHouse table `bars`.
    Enforces explicit Decimal <-> float casting for driver compatibility.
    """

    def __init__(self, client: ClickHouseClient):
        self.client = client

    async def save_bar(self, bar: Bar) -> Bar:
        """Saves a single completed bar to ClickHouse."""
        await self.save_bars_batch([bar])
        return bar

    async def save_bars_batch(self, bars: List[Bar]) -> None:
        """Batch insert bars into ClickHouse for high write performance."""
        if not bars:
            return

        columns = ["symbol", "timeframe", "open", "high", "low", "close", "volume", "bar_start", "bar_end"]
        data = []
        for b in bars:
            tf_str = b.timeframe.value if hasattr(b.timeframe, "value") else str(b.timeframe)
            close_time = b.close_time or datetime.now(timezone.utc)
            data.append((
                b.symbol,
                tf_str,
                float(b.open),
                float(b.high),
                float(b.low),
                float(b.close),
                float(b.tick_volume),
                b.open_time,
                close_time,
            ))

        await self.client.insert_batch("bars", columns, data)

    async def get_bars(self, symbol: str, timeframe: Any, limit: int = 1000) -> List[Bar]:
        """Retrieves historical OHLCV bars for a symbol and timeframe."""
        tf_str = timeframe.value if hasattr(timeframe, "value") else str(timeframe)

        query = """
            SELECT symbol, timeframe, open, high, low, close, volume, bar_start, bar_end
            FROM bars
            WHERE symbol = %(symbol)s
              AND timeframe = %(timeframe)s
            ORDER BY bar_start DESC
            LIMIT %(limit)s
        """
        params = {"symbol": symbol, "timeframe": tf_str, "limit": limit}
        rows = await self.client.execute(query, params)

        bars = []
        for row in rows:
            tf_val = str(row.get("timeframe", "1m")).strip()
            tf_obj = BarTimeframe(tf_val) if tf_val in [str(e.value).strip() for e in BarTimeframe] else BarTimeframe.M1
            open_dec = Decimal(str(row["open"]))

            high_dec = Decimal(str(row["high"]))
            low_dec = Decimal(str(row["low"]))
            close_dec = Decimal(str(row["close"]))
            volume_int = int(row.get("volume", 0))

            open_t = row.get("bar_start") or row.get("open_time")
            close_t = row.get("bar_end") or row.get("close_time")

            bars.append(Bar(
                symbol=row["symbol"],
                timeframe=tf_obj,
                open=open_dec,
                high=high_dec,
                low=low_dec,
                close=close_dec,
                tick_volume=volume_int,
                open_time=open_t,
                close_time=close_t,
            ))

        return bars
