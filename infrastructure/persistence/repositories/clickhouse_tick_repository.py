"""
ClickHouse Tick Repository Implementation.
"""
from datetime import datetime
from decimal import Decimal
from typing import List

from core.domains.market_data.models import Tick
from core.ports.interfaces import IHistoricalTickRepository
from infrastructure.persistence.clickhouse_client import ClickHouseClient


class ClickHouseTickRepository(IHistoricalTickRepository):
    """
    Persists high-frequency market ticks to ClickHouse table `ticks`.
    Enforces explicit Decimal <-> float casting for driver compatibility.
    """

    def __init__(self, client: ClickHouseClient):
        self.client = client

    async def save_tick(self, tick: Tick) -> None:
        """Saves a single tick object to ClickHouse."""
        await self.save_ticks_batch([tick])

    async def save_ticks_batch(self, ticks: List[Tick]) -> None:
        """Batch insert ticks into ClickHouse for maximum write throughput."""
        if not ticks:
            return

        columns = ["symbol", "bid", "ask", "spread", "timestamp", "source"]
        data = []
        for t in ticks:
            data.append((
                t.symbol,
                float(t.bid),
                float(t.ask),
                float(t.spread),
                t.timestamp,
                t.source,
            ))

        await self.client.insert_batch("ticks", columns, data)

    async def get_ticks(self, symbol: str, start: datetime, end: datetime, limit: int = 10000) -> List[Tick]:
        """Retrieves historical tick data for a symbol between start and end timestamps."""
        query = """
            SELECT symbol, bid, ask, spread, timestamp, source
            FROM ticks
            WHERE symbol = %(symbol)s
              AND timestamp >= %(start)s
              AND timestamp <= %(end)s
            ORDER BY timestamp DESC
            LIMIT %(limit)s
        """
        params = {"symbol": symbol, "start": start, "end": end, "limit": limit}
        rows = await self.client.execute(query, params)

        ticks = []
        for row in rows:
            bid_dec = Decimal(str(row["bid"]))
            ask_dec = Decimal(str(row["ask"]))
            spread_dec = Decimal(str(row["spread"])) if "spread" in row else (ask_dec - bid_dec)
            ts = row["timestamp"]
            src = str(row.get("source", "CLICKHOUSE"))

            ticks.append(Tick(
                symbol=row["symbol"],
                bid=bid_dec,
                ask=ask_dec,
                spread=spread_dec,
                timestamp=ts,
                source=src,
            ))

        return ticks
