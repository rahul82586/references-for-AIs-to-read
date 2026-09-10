"""
Redis & In-Memory Sliding Window Rate Limiter implementation.
"""
import time
import uuid
import logging
from typing import Optional, Dict, List
from core.ports.interfaces import IRateLimiter

logger = logging.getLogger(__name__)


class RedisRateLimiter(IRateLimiter):
    """
    Sliding window rate limiter backed by Redis sorted sets (ZSET),
    with automatic in-memory fallback if Redis is unavailable.
    """

    def __init__(self, redis_client=None):
        self._redis = redis_client
        self._fallback_store: Dict[str, List[float]] = {}

    async def is_allowed(self, key: str, limit: int, window_seconds: int) -> bool:
        """
        Determines whether the request is allowed under the sliding window limit.
        """
        now = time.time()
        clear_before = now - window_seconds

        if self._redis:
            try:
                pipe = self._redis.pipeline()
                pipe.zremrangebyscore(key, '-inf', clear_before)
                pipe.zcard(key)
                pipe.zadd(key, {f"{now}-{uuid.uuid4().hex[:8]}": now})
                pipe.expire(key, window_seconds)
                results = pipe.execute()

                # results[1] is the count before adding current request
                count_before = results[1]
                return count_before < limit
            except Exception as e:
                logger.warning(f"Redis rate limiter error, falling back to in-memory: {e}")

        # In-memory sliding window fallback
        timestamps = self._fallback_store.get(key, [])
        valid_timestamps = [ts for ts in timestamps if ts > clear_before]

        if len(valid_timestamps) >= limit:
            self._fallback_store[key] = valid_timestamps
            return False

        valid_timestamps.append(now)
        self._fallback_store[key] = valid_timestamps
        return True
