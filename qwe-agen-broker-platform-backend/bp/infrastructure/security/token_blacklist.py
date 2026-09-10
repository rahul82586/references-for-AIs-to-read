"""
Redis & In-Memory JWT Token Revocation Blacklist.
"""
import logging
from datetime import datetime, timezone
from typing import Dict, Optional
from core.ports.interfaces import ITokenBlacklist

logger = logging.getLogger(__name__)


class RedisTokenBlacklist(ITokenBlacklist):
    """
    JWT Token Revocation Blacklist backed by Redis,
    with dynamic TTL math to prevent Redis OOM memory leaks.
    """

    def __init__(self, redis_client=None):
        self._redis = redis_client
        self._memory_blacklist: Dict[str, datetime] = {}

    async def add(self, token: str, expires_at: datetime) -> None:
        """
        Blacklists a token until expires_at.
        Calculates dynamic TTL seconds = int((expires_at - now).total_seconds()).
        Skips Redis write if ttl_seconds <= 0.
        """
        now = datetime.now(timezone.utc)

        # Standardize timezone on expires_at
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)

        ttl_seconds = int((expires_at - now).total_seconds())

        if ttl_seconds <= 0:
            logger.debug("Token already expired, skipping blacklist insertion to avoid leak.")
            return

        if self._redis:
            try:
                self._redis.setex(f"blacklist:{token}", ttl_seconds, "revoked")
                return
            except Exception as e:
                logger.warning(f"Redis token blacklist error, falling back to in-memory: {e}")

        # In-memory fallback
        self._memory_blacklist[token] = expires_at

    async def is_blacklisted(self, token: str) -> bool:
        """
        Checks if a token has been blacklisted.
        """
        if self._redis:
            try:
                return bool(self._redis.exists(f"blacklist:{token}"))
            except Exception as e:
                logger.warning(f"Redis token blacklist lookup error, falling back to in-memory: {e}")

        now = datetime.now(timezone.utc)
        if token in self._memory_blacklist:
            exp = self._memory_blacklist[token]
            if exp.tzinfo is None:
                exp = exp.replace(tzinfo=timezone.utc)
            if exp > now:
                return True
            else:
                # Clean up expired entry
                del self._memory_blacklist[token]
                return False

        return False
