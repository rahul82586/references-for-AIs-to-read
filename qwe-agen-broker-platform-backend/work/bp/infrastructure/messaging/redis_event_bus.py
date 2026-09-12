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


def _mask_url(url: str) -> str:
    """Strip credentials so a Redis URL is safe to log."""
    try:
        from urllib.parse import urlsplit

        parts = urlsplit(url)
        host = parts.hostname or ""
        if parts.port:
            host = f"{host}:{parts.port}"
        return f"{parts.scheme}://{host}"
    except ValueError:
        return "<unparseable url>"


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
        # D5: channel -> callbacks, and the ONE task that reads the connection.
        # Previously each subscribe() spawned its own listen() loop over the shared
        # pubsub; redis-py permits a single reader, so every loop after the first
        # died with "readuntil() called while another coroutine is already waiting"
        # and the survivor delivered other channels' messages to its own callback.
        self._redis_handlers: dict = {}
        self._reader_task: Optional[asyncio.Task] = None
        # M5: every production caller passes a URL (REDIS_URL, e.g. rediss://
        # for TLS providers like Upstash) as the first positional argument,
        # but connect() used it as a bare hostname - DNS could never resolve
        # it, so the REDIS_URL path had never actually been exercised. A URL
        # is now detected and routed through from_url(); host/port stay for
        # direct construction.
        self._url: Optional[str] = (
            host
            if isinstance(host, str)
            and host.startswith(("redis://", "rediss://", "unix://"))
            else None
        )
        self._host = host
        self._port = port
        self._db = db
        self._redis_client: Optional[redis.Redis] = None
        self._pubsub: Optional[redis.client.PubSub] = None

    async def connect(self) -> None:
        """Establishes connection to Redis (URL or host/port)."""
        if self._url is not None:
            self._redis_client = redis.Redis.from_url(
                self._url, decode_responses=False
            )
            where = _mask_url(self._url)
        else:
            self._redis_client = redis.Redis(
                host=self._host,
                port=self._port,
                db=self._db,
                decode_responses=False
            )
            where = f"{self._host}:{self._port}"
        # Fail at startup, not at first publish: a URL that cannot be reached
        # must stop the boot rather than silently degrade the bus.
        await self._redis_client.ping()
        logger.info(f"Connected to Redis at {where}")

    async def ping(self) -> bool:
        """Liveness probe for /health. False when not connected."""
        if self._redis_client is None:
            return False
        return bool(await self._redis_client.ping())

    async def disconnect(self) -> None:
        """Closes the Redis connection and cleans up resources."""
        # D5: cancel the reader first. Closing the connection under a live
        # get_message() would otherwise surface as a transport error and a
        # reconnect attempt against a bus that is shutting down.
        reader, self._reader_task = self._reader_task, None
        if reader is not None and not reader.done():
            reader.cancel()
            try:
                await reader
            except (asyncio.CancelledError, Exception):  # noqa: BLE001 - shutting down
                pass

        if self._pubsub:
            try:
                await self._pubsub.unsubscribe()
                await self._pubsub.close()
            finally:
                self._pubsub = None

        if self._redis_client:
            try:
                await self._redis_client.close()
            finally:
                self._redis_client = None

        logger.info("Redis Event Bus disconnected")

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
        self._redis_handlers.setdefault(key, []).append(callback)
        logger.debug("subscribed %s to channel %s", getattr(callback, "__name__", callback), key)

        # Registration is complete at this point, so subscribe() can return
        # immediately. Only the SUBSCRIBE command and the reader task are deferred.
        self._schedule_redis_subscription(key)
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
        # Detach the Redis-side registration too, or the reader keeps calling a
        # callback its owner believes it unsubscribed. Done first: the local list is
        # the return value's source of truth, and this must not change that.
        self._unsubscribe_redis(key, callback)
        handlers = self._local_handlers.get(key)
        if not handlers:
            return False
        try:
            handlers.remove(callback)
            return True
        except ValueError:
            return False

    def _unsubscribe_redis(self, key: str, callback: Callable[[Any], None]) -> None:
        """Remove one callback from a channel, and UNSUBSCRIBE when it was the last.

        Best-effort: a failure here must not stop the local unregister that already
        happened, and the reader tolerates a channel it is no longer subscribed to.
        """
        handlers = self._redis_handlers.get(key)
        if not handlers:
            return
        try:
            handlers.remove(callback)
        except ValueError:
            return
        if handlers:
            return
        self._redis_handlers.pop(key, None)
        pubsub = self._pubsub
        if pubsub is None:
            return

        async def _do_unsubscribe() -> None:
            try:
                await pubsub.unsubscribe(key)
            except Exception as exc:  # noqa: BLE001 - cleanup must not raise into a caller
                logger.warning("Redis unsubscribe for %s failed: %s", key, exc)

        try:
            asyncio.get_running_loop().create_task(_do_unsubscribe())
        except RuntimeError:
            pass

    def _schedule_redis_subscription(self, key: str) -> None:
        """Issue SUBSCRIBE and make sure exactly one reader exists.

        This used to take the callback and start a listen() loop for it. Now the
        callback lives in `_redis_handlers` and this only has to guarantee the
        connection is subscribed to `key` and that the single reader is running,
        however many channels are added.
        """
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            # No loop yet (e.g. during construction outside asyncio). The local registry
            # still works; Redis delivery starts when connect() runs inside a loop.
            self._pending_redis_channels.add(key)
            return
        loop.create_task(self._ensure_subscribed(key))

    async def _ensure_subscribed(self, key: str) -> None:
        """SUBSCRIBE to one channel and start the reader if it is not running."""
        try:
            if not self._redis_client:
                await self.connect()
            if self._pubsub is None:
                self._pubsub = self._redis_client.pubsub()
            await self._pubsub.subscribe(key)
            logger.info("Redis subscribed to channel: %s", key)
        except asyncio.CancelledError:
            raise
        except Exception as exc:  # noqa: BLE001 - registration already happened locally
            logger.error("Redis SUBSCRIBE for %s failed: %s", key, exc)
            return

        self._start_reader()
        # Channels queued before any loop existed are now reachable: subscribe them too.
        pending = {k for k in self._pending_redis_channels if k != key}
        if pending:
            self._pending_redis_channels = {key}
            for pending_key in sorted(pending):
                await self._ensure_subscribed(pending_key)

    def _start_reader(self) -> None:
        """Guarantee exactly one reader task for this connection.

        Idempotent: a second call while the reader lives does nothing. That is the
        whole point - the reader count must not scale with the channel count.
        """
        task = self._reader_task
        if task is not None and not task.done():
            return
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            return
        self._reader_task = loop.create_task(self._read_loop())

    async def _read_loop(self) -> None:
        """The only reader on the pubsub connection.

        Dispatches on the arriving message's own channel, so a handler can never be
        handed another channel's payload - the leakage the per-channel loops caused.
        Restarts itself if the connection drops, because losing the reader silently
        is exactly the failure this fix exists to prevent.
        """
        backoff = 0.25
        while True:
            pubsub = self._pubsub
            if pubsub is None:
                logger.debug("Redis reader exiting: no pubsub connection")
                return
            try:
                while True:
                    message = await pubsub.get_message(
                        ignore_subscribe_messages=True, timeout=1.0)
                    if message is None:
                        # idle tick: lets the loop notice disconnect() and cancellation
                        continue
                    if message.get("type") != "message":
                        continue
                    backoff = 0.25
                    await self._deliver(message)
            except asyncio.CancelledError:
                raise
            except Exception as exc:  # noqa: BLE001 - reconnect rather than die
                if self._pubsub is None:
                    return  # disconnect() ran; exiting is correct
                logger.error("Redis reader failed (%s); reconnecting in %.1fs", exc, backoff)
                await asyncio.sleep(backoff)
                backoff = min(backoff * 2, 10.0)
                try:
                    await self._reset_pubsub()
                except Exception as rexc:  # noqa: BLE001
                    logger.error("Redis reader could not re-subscribe: %s", rexc)

    async def _reset_pubsub(self) -> None:
        """Rebuild the pubsub connection and re-SUBSCRIBE every known channel."""
        old, self._pubsub = self._pubsub, None
        if old is not None:
            try:
                await old.close()
            except Exception:  # noqa: BLE001 - a broken connection may not close cleanly
                pass
        if not self._redis_client:
            await self.connect()
        self._pubsub = self._redis_client.pubsub()
        channels = sorted(self._redis_handlers)
        if channels:
            await self._pubsub.subscribe(*channels)
            logger.info("Redis reader re-subscribed to %d channel(s)", len(channels))

    async def _deliver(self, message: dict) -> None:
        """Hand one message to the callbacks registered for ITS channel."""
        channel = message.get("channel")
        if isinstance(channel, bytes):
            channel = channel.decode("utf-8", "replace")
        handlers = list(self._redis_handlers.get(channel) or ())
        if not handlers:
            logger.debug("Redis message on %s with no local handler", channel)
            return

        event = self._rehydrate(message.get("data"))
        for handler in handlers:
            try:
                result = handler(event)
                if inspect.isawaitable(result):
                    await result
            except asyncio.CancelledError:
                raise
            except Exception as exc:  # noqa: BLE001 - one bad handler must not stop the rest
                logger.error("Redis handler for %s raised: %s", channel, exc)

    @staticmethod
    def _rehydrate(data: Any) -> Any:
        """Turn wire bytes back into the DomainEvent the publisher sent.

        Falls back to the parsed dict for anything this process cannot deserialise,
        so an unfamiliar payload is still delivered rather than dropped.
        """
        try:
            payload = json.loads(data) if isinstance(data, (bytes, str)) else data
        except (TypeError, ValueError):
            return data
        if isinstance(payload, dict):
            try:
                return DomainEvent.from_dict(payload)
            except Exception:  # noqa: BLE001 - never lose a message over the envelope
                return payload
        return payload


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
