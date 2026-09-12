"""
Redis Market Data Cache Adapter

High-speed Redis cache adapter for caching latest ticks, order books (DOM),
and symbol execution statistics for API endpoints and real-time UI display.

Architectural Rule: Infrastructure adapter.
"""
import json
import logging
from typing import Any, Dict, Optional

from core.domains.market_data.models import Tick

logger = logging.getLogger(__name__)


class RedisMarketDataCache:
    """
    Redis-backed cache providing fast reads for the Risk Engine and API layer.
    """
    def __init__(self, redis_client: Any):
        self.redis = redis_client
        self.TICK_PREFIX = "md:tick:"
        self.BOOK_PREFIX = "md:book:"
        self.STATS_PREFIX = "md:stats:"

    async def cache_tick(self, tick: Tick) -> None:
        """Cache the latest tick for a symbol in Redis with a 60s TTL."""
        if not self.redis:
            return

        key = f"{self.TICK_PREFIX}{tick.symbol}"
        data = {
            "symbol": tick.symbol,
            "bid": str(tick.bid),
            "ask": str(tick.ask),
            "spread": str(tick.spread),
            "mid": str(tick.mid),
            "timestamp": tick.timestamp.isoformat(),
            "source": tick.source
        }
        await self.redis.set(key, json.dumps(data), ex=60)

    async def get_tick(self, symbol: str) -> Optional[dict]:
        """Retrieve cached tick payload for a symbol."""
        if not self.redis:
            return None

        key = f"{self.TICK_PREFIX}{symbol}"
        data = await self.redis.get(key)
        return json.loads(data) if data else None

    async def get_all_ticks(self) -> Dict[str, dict]:
        """Retrieve all cached ticks (for Admin UI quotes panel)."""
        if not self.redis:
            return {}

        keys = await self.redis.keys(f"{self.TICK_PREFIX}*")
        result = {}
        for key in keys:
            data = await self.redis.get(key)
            if data:
                parsed = json.loads(data)
                result[parsed["symbol"]] = parsed
        return result
