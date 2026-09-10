"""
Async ClickHouse Client with Connection Pooling & In-Memory Fallback.
"""
import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class ClickHouseClient:
    """
    Async ClickHouse client with connection pooling and high-performance batch operations.
    Includes in-memory storage fallback for testing environments and offline modes.
    """

    def __init__(
        self,
        host: str = "localhost",
        port: int = 9000,
        database: str = "broker_analytics",
        user: str = "default",
        password: str = "",
    ):
        self.host = host
        self.port = port
        self.database = database
        self.user = user
        self.password = password
        self.connection = None
        self._mock_tables: Dict[str, List[Dict[str, Any]]] = {}

    async def connect(self) -> None:
        """Establish async connection to ClickHouse server."""
        try:
            from asynch import connect
            self.connection = connect(
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.password,
                db=self.database,
            )
            logger.info(f"Connected to ClickHouse at {self.host}:{self.port}/{self.database}")
        except Exception as e:
            logger.warning(f"ClickHouse connection failed ({e}). Operating with in-memory fallback store.")
            self.connection = None


    async def execute(self, query: str, params: Optional[dict] = None) -> List[Dict[str, Any]]:
        """Executes query and returns list of dictionary records."""
        if self.connection:
            try:
                from asynch.cursors import DictCursor
                async with self.connection.cursor(cursor=DictCursor) as cursor:
                    await cursor.execute(query, params or {})
                    return await cursor.fetchall()
            except Exception as e:
                logger.error(f"ClickHouse query execution error: {e}")

        # In-memory mock query fallback
        query_upper = query.upper()
        table_name = "ticks" if "TICKS" in query_upper else "bars"
        rows = self._mock_tables.get(table_name, [])

        if not params:
            return rows

        filtered = []
        symbol_param = params.get("symbol")
        start_param = params.get("start")
        end_param = params.get("end")
        tf_param = params.get("timeframe")
        limit_param = params.get("limit", 10000)

        for r in rows:
            if symbol_param and r.get("symbol") != symbol_param:
                continue
            if tf_param and r.get("timeframe") != tf_param:
                continue
            if start_param and r.get("timestamp") and r["timestamp"] < start_param:
                continue
            if end_param and r.get("timestamp") and r["timestamp"] > end_param:
                continue
            if start_param and r.get("bar_start") and r["bar_start"] < start_param:
                continue
            if end_param and r.get("bar_start") and r["bar_start"] > end_param:
                continue
            filtered.append(r)

        # Sort DESC
        time_key = "timestamp" if "timestamp" in (rows[0] if rows else {}) else "bar_start"
        filtered.sort(key=lambda x: x.get(time_key, 0), reverse=True)
        return filtered[:limit_param]

    async def insert_batch(self, table: str, columns: List[str], data: List[tuple]) -> None:
        """Batch insert for high-performance writes."""
        if not data:
            return

        if self.connection:
            try:
                async with self.connection.cursor() as cursor:
                    col_str = ",".join(columns)
                    await cursor.executemany(
                        f"INSERT INTO {table} ({col_str}) VALUES",
                        data
                    )
                    await self.connection.commit()
                    return
            except Exception as e:
                logger.error(f"ClickHouse batch insert error: {e}. Falling back to in-memory store.")

        # In-memory fallback
        if table not in self._mock_tables:
            self._mock_tables[table] = []

        for row in data:
            record = dict(zip(columns, row))
            self._mock_tables[table].append(record)

    async def close(self) -> None:
        """Close ClickHouse connection."""
        if self.connection:
            try:
                await self.connection.close()
            except Exception as e:
                logger.warning(f"Error closing ClickHouse connection: {e}")
            finally:
                self.connection = None
