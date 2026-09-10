import inspect
import asyncio
"""
Redis Event Bus - High-Performance Pub/Sub Implementation

This adapter implements the IEventBus interface using redis.asyncio.
It provides a scalable, distributed event routing mechanism for the platform.
"""
import json
import logging
from typing import Callable, Any, Optional

import redis.asyncio as redis

from core.events.domain_events import DomainEvent
from core.ports.interfaces import IEventBus, normalize_channel

logger = logging.getLogger(__name__)


class RedisEventBus(IEventBus):
    """
    Redis-based implementation of the Event Bus.

    Architectural Purpose:
    Provides a high-performance, pub/sub mechanism for distributing domain events.
    Uses Redis Pub/Sub to fan-out messages to multiple subscribers
    (Analytics, AI, Notifications) in real-time.
    """

    def __init__(self, host: str = "localhost", port: int = 6379, db: int = 0):
        # In-process typed dispatch, keyed by every convention a caller might use.
        # Redis pub/sub remains the cross-process transport; this is what makes a
        # same-process subscriber actually receive anything.
        self._local_handlers: dict = {}
        self._pending_redis_channels: set = set()
        self._host = host
        self._port = port
        self._db = db
        self._redis_client: Optional[redis.Redis] = None
        self._pubsub: Optional[redis.client.PubSub] = None

    async def connect(self) -> None:
        """Establishes connection to Redis."""
        self._redis_client = redis.Redis(
            host=self._host,
            port=self._port,
            db=self._db,
            decode_responses=False
        )
        logger.info(f"Connected to Redis at {self._host}:{self._port}")

    async def _dispatch_local(self, event: Any) -> None:
        """Deliver to in-process handlers registered under any of the three conventions."""
        keys = set()
        keys.add(normalize_channel(type(event)))
        event_type = getattr(event, "event_type", None)
        if event_type is not None:
            keys.add(normalize_channel(event_type))
            keys.add(normalize_channel(getattr(event_type, "value", event_type)))

        for key in keys:
            for handler in list(self._local_handlers.get(key, [])):
                try:
                    result = handler(event)
                    if inspect.isawaitable(result):
                        await result
                except Exception as exc:  # noqa: BLE001 - one bad handler must not stop the rest
                    logger.error("event handler for %s raised: %s", key, exc)

    async def publish(self, event: DomainEvent) -> None:
        """
        Serializes the event to JSON and publishes it to a channel named after its type.

        Example Channel: "order.created"

        This is non-blocking and fire-and-forget, ensuring high throughput
        even under heavy load.
        """
        await self._dispatch_local(event)
        if not self._redis_client:
            await self.connect()

        channel = event.event_type.value
        message = json.dumps(event.to_dict()).encode('utf-8')

        try:
            await self._redis_client.publish(channel, message)
            logger.debug(f"Event published to {channel}: {event.event_id}")
        except Exception as e:
            logger.error(f"Failed to publish event {event.event_id}: {e}")
            raise

    def subscribe(self, channel: Any, callback: Callable[[Any], None]) -> None:
        """Register a handler. Synchronous, so registration cannot be silently dropped.

        The channel may be an event class (GroupCreated), an EventType member
        (EventType.TICK_RECEIVED) or its string value ("market.tick_received"). All
        three normalise to the same key, and publish() registers the event under each of
        them, so any convention a caller chooses will match.

        The previous signature was `async def`. Twenty of twenty-four call sites did not
        await it, so those subscriptions never happened: ConfigCache never invalidated,
        LiquidationWorker never saw a stop-out, and no WebSocket client ever received an
        update. Making registration synchronous means an unawaited call still works.
        """
        key = normalize_channel(channel)
        self._local_handlers.setdefault(key, []).append(callback)
        logger.debug("subscribed %s to channel %s", getattr(callback, "__name__", callback), key)

        # Redis delivery is scheduled, not awaited: subscribe() must return immediately
        # so the caller's registration is complete before it publishes anything.
        self._schedule_redis_subscription(key, callback)
        return _Subscription()

    def unsubscribe(self, channel: Any, callback: Callable[[Any], None]) -> bool:
        """Remove one local registration. Returns True if something was removed.

        IEventBus never declared this and RedisEventBus never had it, so
        LiquidationWorker.stop() - which calls it - raised AttributeError on shutdown.
        A worker that cannot be stopped cannot be restarted, and a graceful shutdown
        that throws is not graceful. Only the in-process registration is removed: the
        Redis pubsub channel is shared and may still have other subscribers.
        """
        key = normalize_channel(channel)
        handlers = self._local_handlers.get(key)
        if not handlers:
            return False
        try:
            handlers.remove(callback)
            return True
        except ValueError:
            return False

    def _schedule_redis_subscription(self, key: str, callback: Callable[[Any], None]) -> None:
        """Attach a Redis pub/sub listener without blocking the caller."""
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            # No loop yet (e.g. during construction outside asyncio). The local registry
            # still works; Redis delivery starts when connect() runs inside a loop.
            self._pending_redis_channels.add(key)
            return
        loop.create_task(self._redis_subscribe(key, callback))

    async def _redis_subscribe(self, key: str, callback: Callable[[Any], None]) -> None:
        """Transport-level subscription. Runs its own listening loop."""
        try:
            if not self._redis_client:
                await self.connect()
            if self._pubsub is None:
                self._pubsub = self._redis_client.pubsub()
            await self._pubsub.subscribe(key)
            logger.info("Redis subscribed to channel: %s", key)
            async for message in self._pubsub.listen():
                if message.get("type") != "message":
                    continue
                try:
                    payload = json.loads(message["data"])
                except (TypeError, ValueError):
                    payload = {"raw": message["data"]}
                result = callback(payload)
                if inspect.isawaitable(result):
                    await result
        except Exception as exc:  # noqa: BLE001 - a transport failure must not kill the loop
            logger.error("Redis subscription for %s failed: %s", key, exc)


class _Subscription:
    """Returned by subscribe() so that both awaited and unawaited calls work.

    Registration already happened inside subscribe(); this exists purely so that
    `await bus.subscribe(...)` - which four call sites and several tests do - keeps
    working without a second method name for mocks to implement.
    """

    __slots__ = ()

    def __await__(self):
        async def _done():
            return None

        return _done().__await__()

    async def disconnect(self) -> None:
        """Closes the Redis connection and cleans up resources."""
        if self._pubsub:
            await self._pubsub.unsubscribe()
            await self._pubsub.close()
            self._pubsub = None

        if self._redis_client:
            await self._redis_client.close()
            self._redis_client = None

        logger.info("Redis Event Bus disconnected")
