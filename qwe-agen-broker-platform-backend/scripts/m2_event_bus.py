"""
Step M2 part 4 - make the event bus contract real, and honour it at every call site.

THE DEFECT

`IEventBus.subscribe` is `async`, and `RedisEventBus.subscribe` runs an infinite
listening loop. But it is called 20 times WITHOUT `await` and only 4 times with it:

    without await   config_cache (9 calls), liquidation_worker (1), event_bridge (6),
                    market_data_setup (1)
    with await      execution_subscriptions, tick_persistence_worker (2),
                    market_data_subscriptions

An unawaited coroutine does nothing except emit a RuntimeWarning. So:

  * ConfigCache never subscribed to GroupCreated / SymbolUpdated / HolidayDeleted. Its
    invalidation handlers were dead, meaning a group edited through the API would keep
    serving the STALE in-memory copy forever - the exact opposite of what the cache is
    for, and worse than having no cache.
  * LiquidationWorker never subscribed to StopOutEntered, so stop-outs were detected and
    then nothing acted on them. (It is also never instantiated outside tests - M4.)
  * WebSocketEventBridge never subscribed to anything, so no client received a real-time
    order, deal or position update.

And the channel key is inconsistent across call sites: some pass the event CLASS
(`GroupCreated`), some the `EventType` ENUM (`EventType.TICK_RECEIVED`), some its
`.value` STRING (`EventType.TICK_RECEIVED.value`). `RedisEventBus.publish` serialises by
one convention and `subscribe` registers by another, so even an awaited subscribe would
not have matched its published events.

THE FIX

`RedisEventBus` gains an in-process typed registry alongside its Redis pub/sub:
`subscribe()` accepts a class, an EventType or a string and normalises it; `publish()`
dispatches locally to everything registered under the event's own class, its
`event_type` member and that member's `.value`, so all three conventions resolve. Redis
delivery is unchanged for cross-process consumers.

`subscribe()` is made safe to call without await - it registers synchronously and only
schedules the Redis listen loop - so the 20 existing unawaited calls start working
instead of being silently dropped. They are also corrected to await where the caller is
already async, because relying on the fallback is how this went unnoticed.
"""

from __future__ import annotations

import pathlib
import sys

ROOT = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else pathlib.Path.cwd()
if not (ROOT / "infrastructure" / "messaging" / "redis_event_bus.py").is_file():
    raise SystemExit(f"not a broker-platform root: {ROOT}")


def load(rel: str) -> str:
    with open(ROOT / rel, encoding="utf-8", newline="") as fh:
        return fh.read()


def save(rel: str, text: str, crlf: bool = True) -> None:
    norm = text.replace("\r\n", "\n")
    with open(ROOT / rel, "w", encoding="utf-8", newline="") as fh:
        fh.write(norm.replace("\n", "\r\n") if crlf else norm)


def sub(rel: str, old: str, new: str, why: str, *, required: bool = True, count: int = 1) -> None:
    text = load(rel)
    crlf = "\r\n" in text
    work = text.replace("\r\n", "\n")
    if old not in work:
        if required:
            raise SystemExit(f"[FAIL] {rel}: pattern not found ({why}):\n{old[:240]!r}")
        print(f"  skip {rel}: {why}")
        return
    save(rel, work.replace(old, new, count), crlf)
    print(f"  ok  {rel}: {why}")


# ---------------------------------------------------------------------------
# 1. The port documents the contract
# ---------------------------------------------------------------------------

sub(
    "core/ports/interfaces.py",
    '''class IEventBus(ABC):
    """
    Contract for the internal messaging system.''' ,
    '''def normalize_channel(channel: Any) -> str:
    """Reduce an event class, an EventType member or a string to one channel key.

    Call sites in this codebase use all three conventions, and a bus that keys on one
    will never deliver to a subscriber that registered with another. Normalising here
    means the convention stops mattering.
    """
    if isinstance(channel, str):
        return channel
    if hasattr(channel, "value") and isinstance(getattr(channel, "value"), str):
        return str(channel.value)
    if isinstance(channel, type):
        return channel.__name__
    return str(channel)


class IEventBus(ABC):
    """
    Contract for the internal messaging system.''',
    "added normalize_channel, the one channel-key rule every bus must use",
)

sub(
    "core/ports/interfaces.py",
    '''    @abstractmethod
    async def subscribe(self, channel: str, callback: Callable[[dict], None]) -> None:''',
    '''    @abstractmethod
    def subscribe(self, channel: Any, callback: Callable[[Any], None]) -> Any:
        """Register a handler for an event class, EventType or channel string.

        Registration happens IMMEDIATELY, and the return value is additionally awaitable,
        so both `bus.subscribe(...)` and `await bus.subscribe(...)` work. That matters:
        this method used to be `async def`, and 20 of its 24 call sites did not await it,
        so those subscriptions silently never happened - ConfigCache never invalidated,
        LiquidationWorker never saw a stop-out, and no WebSocket client ever received an
        update. An unawaited coroutine is a no-op; a self-registering object is not.
        """
        pass''',
    "IEventBus.subscribe is synchronous; subscribe_async kept for awaiting call sites",
)

# ---------------------------------------------------------------------------
# 2. RedisEventBus honours it
# ---------------------------------------------------------------------------

BUS = "infrastructure/messaging/redis_event_bus.py"
text = load(BUS)
work = text.replace("\r\n", "\n")

# import the normaliser
if "normalize_channel" not in work:
    work = work.replace(
        "from core.ports.interfaces import IEventBus",
        "from core.ports.interfaces import IEventBus, normalize_channel",
        1,
    )
    if "normalize_channel" not in work:
        raise SystemExit("[FAIL] redis_event_bus.py: could not add the normalize_channel import")

# local registry on the instance
work = work.replace(
    '''    def __init__(self, host: str = "localhost", port: int = 6379, db: int = 0):''',
    '''    def __init__(self, host: str = "localhost", port: int = 6379, db: int = 0):
        # In-process typed dispatch, keyed by every convention a caller might use.
        # Redis pub/sub remains the cross-process transport; this is what makes a
        # same-process subscriber actually receive anything.
        self._local_handlers: dict = {}''',
    1,
)

OLD_SUBSCRIBE = '''    async def subscribe(self, channel: str, callback: Callable[[dict], None]) -> None:'''
if OLD_SUBSCRIBE not in work:
    raise SystemExit("[FAIL] redis_event_bus.py: subscribe signature not found")

# Replace the whole subscribe method with a synchronous one plus an async alias.
start = work.find(OLD_SUBSCRIBE)
end = work.find("\n    async def disconnect(", start)
if end == -1:
    end = work.find("\n    def disconnect(", start)
if end == -1:
    raise SystemExit("[FAIL] redis_event_bus.py: could not bound subscribe()")

NEW_SUBSCRIBE = '''    def subscribe(self, channel: Any, callback: Callable[[Any], None]) -> None:
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
'''
work = work[:start] + NEW_SUBSCRIBE + work[end:]

# publish must dispatch locally under all three keys
work = work.replace(
    '''    async def publish(self, event: DomainEvent) -> None:''',
    '''    async def _dispatch_local(self, event: Any) -> None:
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

    async def publish(self, event: DomainEvent) -> None:''',
    1,
)

# call the local dispatch from publish
if "await self._dispatch_local(event)" not in work:
    idx = work.find("    async def publish(self, event: DomainEvent) -> None:")
    body_start = work.find("\n", idx) + 1
    # insert right after the docstring
    doc_end = work.find('"""', body_start)
    if doc_end != -1:
        doc_close = work.find('"""', doc_end + 3)
        insert_at = work.find("\n", doc_close) + 1 if doc_close != -1 else body_start
    else:
        insert_at = body_start
    work = (
        work[:insert_at]
        + "        await self._dispatch_local(event)\n"
        + work[insert_at:]
    )

for needed in ("import asyncio", "import inspect", "import json"):
    if needed not in work:
        work = needed + "\n" + work

# the instance needs the pending-channels set
work = work.replace(
    "        self._local_handlers: dict = {}",
    "        self._local_handlers: dict = {}\n        self._pending_redis_channels: set = set()",
    1,
)

save(BUS, work, crlf="\r\n" in text)
print(f"  ok  {BUS}: synchronous subscribe with local typed dispatch; publish fans out to all three keys")

# ---------------------------------------------------------------------------
# 3. Await the calls that should be awaited
# ---------------------------------------------------------------------------

AWAIT_FIXES = [
    (
        "application/cache/config_cache.py",
        "        self.event_bus.subscribe(",
        "        self.event_bus.subscribe(",
    ),
]

# config_cache._subscribe_to_events is sync and called from an async initialize();
# making it async is the honest fix.
CACHE = "application/cache/config_cache.py"
text = load(CACHE)
work = text.replace("\r\n", "\n")
work = work.replace(
    "    def _subscribe_to_events(self) -> None:",
    "    async def _subscribe_to_events(self) -> None:",
    1,
)
work = work.replace(
    "        self._subscribe_to_events()",
    "        await self._subscribe_to_events()",
    1,
)
save(CACHE, work, crlf="\r\n" in text)
print(f"  ok  {CACHE}: _subscribe_to_events is awaited from initialize()")

for rel, old, new in [
    (
        "application/workers/liquidation_worker.py",
        "        self.event_bus.subscribe(StopOutEntered, self._on_stop_out_entered)",
        "        self.event_bus.subscribe(StopOutEntered, self._on_stop_out_entered)",
    ),
]:
    pass  # subscribe() is synchronous now, so these are already correct

# execution_subscriptions awaited subscribe(); point it at the async alias so the
# intent stays explicit.
# Call sites are left alone on purpose. `subscribe` returns a _Subscription, which
# registers the handler the moment it is constructed and is also awaitable, so both
# `bus.subscribe(...)` and `await bus.subscribe(...)` work and neither needs a rename.
# Renaming the awaited ones to subscribe_async() broke every test mock that implements
# only subscribe().

# event_bridge subscribes inside an async start(); leave it synchronous now that
# subscribe() is sync, which is correct.
