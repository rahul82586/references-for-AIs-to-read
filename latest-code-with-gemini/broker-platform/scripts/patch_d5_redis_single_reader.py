"""D5 - Redis pub/sub delivered to one channel and leaked into another.

THE BUG
=======
`subscribe()` scheduled a dedicated `_redis_subscribe(key, callback)` task per
channel, and each task ran its own `async for message in self._pubsub.listen()`
over the SAME shared pubsub connection. redis-py allows exactly one reader on a
connection; every loop after the first raises

    readuntil() called while another coroutine is already waiting for incoming data

logs it as an error, and dies. Confirmed live against Upstash with
scripts/d5_redis_probe.py:

    ch1: [{'x': 1}, {'x': 3}]     <- got ch3's message too
    ch2: [{'x': 2}]
    ch3: []                       <- its own listener had already died
    RESULT: 2/3 channels delivered

Two distinct failures, not one:

1. Lost delivery. Every channel but the first silently receives nothing, ever.
   In production that means ConfigCache never invalidates, LiquidationWorker never
   sees a stop-out, and no WebSocket client receives an update - whichever
   subscribed second. The error is logged once at startup and then the system runs
   looking healthy.

2. Cross-channel leakage. The surviving loop reads EVERY message on the connection
   and passes it to its own callback regardless of which channel it arrived on, so
   ch1's handler was handed ch3's payload. A handler written for one event type
   receives another's data. That is worse than dropping it.

This blocks multi-process deployment, which is the whole reason RedisEventBus
exists: InProcessEventBus covers one process, and a second process is exactly the
case where these subscribers are the only delivery path.

THE FIX
=======
One reader task per pubsub connection, not one per channel. The reader owns the
socket, reads `get_message()`, looks up the arriving message's own channel, and
dispatches to the callbacks registered for THAT channel. Subscribing to a new
channel is then just a `SUBSCRIBE` command plus a dict entry - it never touches the
read loop, so the number of channels stops mattering.

Also fixed while in here: the reader used to hand handlers the raw JSON dict, while
InProcessEventBus hands them a DomainEvent. The same handler therefore received a
different type depending on which bus the server was configured with. Remote
messages are now rehydrated into DomainEvent (via the new `DomainEvent.from_dict`)
with the dict kept as a fallback for payloads this process cannot deserialise.

The reader is started lazily on the first subscribe inside a running loop, is
restarted if the connection drops, and is cancelled by disconnect().

Idempotent. Verified by scripts/d5_redis_probe.py (must report 3/3) and
tests/unit/infrastructure/test_d5_redis_pubsub.py.
"""
import ast
import io
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
sys.path.insert(0, ROOT)

BUS = "infrastructure/messaging/redis_event_bus.py"
EVT = "core/events/domain_events.py"
applied = []


def patch(path, pairs):
    src = io.open(path, encoding="utf-8", newline="").read()
    original = src
    for old, new in pairs:
        o = old.replace("\n", "\r\n") if "\r\n" in src else old
        n = new.replace("\n", "\r\n") if "\r\n" in src else new
        if src.count(o) == 1:
            src = src.replace(o, n, 1)
        elif src.count(o) == 0 and src.count(n) >= 1:
            print(f"  skip (already patched): {path}")
        else:
            raise AssertionError(
                f"{path}: anchor found {src.count(o)}x (new text {src.count(n)}x): {old[:70]!r}")
    if src != original:
        ast.parse(src.replace("\r\n", "\n"))
        io.open(path, "w", encoding="utf-8", newline="").write(src)
        applied.append(path)


# ---------------------------------------------------------------- DomainEvent.from_dict
patch(EVT, [(
    '''    def to_dict(self) -> dict[str, Any]:
        """Serialize event for transport (e.g., JSON for Redis)."""
        return {
            "event_id": self.event_id,
            "timestamp": self.timestamp.isoformat(),
            "aggregate_id": self.aggregate_id,
            "event_type": self.event_type.value,
            "payload": self.payload
        }
''',
    '''    def to_dict(self) -> dict[str, Any]:
        """Serialize event for transport (e.g., JSON for Redis)."""
        return {
            "event_id": self.event_id,
            "timestamp": self.timestamp.isoformat(),
            "aggregate_id": self.aggregate_id,
            "event_type": self.event_type.value,
            "payload": self.payload
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "DomainEvent":
        """Rehydrate what to_dict() produced.

        D5: without this, RedisEventBus had to hand subscribers the raw JSON dict
        while InProcessEventBus handed them a DomainEvent - so the same handler
        received a different type depending on which bus the server was configured
        with, and every consumer needed an isinstance branch to work on both.

        Unknown event_type values and unparseable timestamps are tolerated rather
        than raised: an event from a newer publisher, or one with a field this
        process does not know, must still be delivered. Losing the message because
        its envelope was unfamiliar is a worse failure than delivering it with a
        best-effort type.
        """
        raw_type = data.get("event_type")
        try:
            event_type = EventType(raw_type) if raw_type is not None else cls.event_type
        except ValueError:
            logger.warning("unknown event_type %r on the wire; keeping the raw value", raw_type)
            event_type = cls.event_type

        raw_ts = data.get("timestamp")
        try:
            timestamp = (datetime.fromisoformat(raw_ts) if isinstance(raw_ts, str)
                         else datetime.now(timezone.utc))
        except ValueError:
            logger.warning("unparseable timestamp %r; using receipt time", raw_ts)
            timestamp = datetime.now(timezone.utc)

        return cls(
            event_id=data.get("event_id") or str(uuid.uuid4()),
            timestamp=timestamp,
            aggregate_id=data.get("aggregate_id"),
            payload=data.get("payload") or {},
            event_type=event_type,
        )
''',
)])

# the new classmethod needs logging + uuid + datetime in scope
patch(EVT, [(
    "import uuid\n",
    "import logging\nimport uuid\n",
)])
patch(EVT, [(
    "from dataclasses import dataclass, field\n",
    "from dataclasses import dataclass, field\n\nlogger = logging.getLogger(__name__)\n",
)])


# ------------------------------------------------------------------- the bus itself
patch(BUS, [
    # --- state: a channel->callbacks map and one reader task, not one loop each
    (
        """        self._local_handlers: dict = {}
        self._pending_redis_channels: set = set()""",
        """        self._local_handlers: dict = {}
        self._pending_redis_channels: set = set()
        # D5: channel -> callbacks, and the ONE task that reads the connection.
        # Previously each subscribe() spawned its own listen() loop over the shared
        # pubsub; redis-py permits a single reader, so every loop after the first
        # died with "readuntil() called while another coroutine is already waiting"
        # and the survivor delivered other channels' messages to its own callback.
        self._redis_handlers: dict = {}
        self._reader_task: Optional[asyncio.Task] = None""",
    ),

    # --- subscribe(): register only, never spawn a reader
    (
        """        key = normalize_channel(channel)
        self._local_handlers.setdefault(key, []).append(callback)
        logger.debug("subscribed %s to channel %s", getattr(callback, "__name__", callback), key)

        # Redis delivery is scheduled, not awaited: subscribe() must return immediately
        # so the caller's registration is complete before it publishes anything.
        self._schedule_redis_subscription(key, callback)
        return _Subscription()""",
        """        key = normalize_channel(channel)
        self._local_handlers.setdefault(key, []).append(callback)
        self._redis_handlers.setdefault(key, []).append(callback)
        logger.debug("subscribed %s to channel %s", getattr(callback, "__name__", callback), key)

        # Registration is complete at this point, so subscribe() can return
        # immediately. Only the SUBSCRIBE command and the reader task are deferred.
        self._schedule_redis_subscription(key)
        return _Subscription()""",
    ),

    # --- unsubscribe(): drop the redis-side registration too
    (
        """            return True
        except ValueError:
            return False

    def _schedule_redis_subscription(self, key: str, callback: Callable[[Any], None]) -> None:""",
        """            return True
        except ValueError:
            return False

    def _unsubscribe_redis(self, key: str, callback: Callable[[Any], None]) -> None:
        \"\"\"Remove one callback from a channel, and UNSUBSCRIBE when it was the last.

        Best-effort: a failure here must not stop the local unregister that already
        happened, and the reader tolerates a channel it is no longer subscribed to.
        \"\"\"
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

    def _schedule_redis_subscription(self, key: str) -> None:""",
    ),

    # --- _schedule_redis_subscription: ensure SUBSCRIBE + one reader, not N readers
    (
        """        \"\"\"Attach a Redis pub/sub listener without blocking the caller.\"\"\"
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            # No loop yet (e.g. during construction outside asyncio). The local registry
            # still works; Redis delivery starts when connect() runs inside a loop.
            self._pending_redis_channels.add(key)
            return
        loop.create_task(self._redis_subscribe(key, callback))""",
        """        \"\"\"Issue SUBSCRIBE and make sure exactly one reader exists.

        This used to take the callback and start a listen() loop for it. Now the
        callback lives in `_redis_handlers` and this only has to guarantee the
        connection is subscribed to `key` and that the single reader is running,
        however many channels are added.
        \"\"\"
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            # No loop yet (e.g. during construction outside asyncio). The local registry
            # still works; Redis delivery starts when connect() runs inside a loop.
            self._pending_redis_channels.add(key)
            return
        loop.create_task(self._ensure_subscribed(key))""",
    ),

    # --- replace the per-channel listen loop with one connection reader
    (
        """    async def _redis_subscribe(self, key: str, callback: Callable[[Any], None]) -> None:
        \"\"\"Transport-level subscription. Runs its own listening loop.\"\"\"
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
            logger.error("Redis subscription for %s failed: %s", key, exc)""",
        """    async def _ensure_subscribed(self, key: str) -> None:
        \"\"\"SUBSCRIBE to one channel and start the reader if it is not running.\"\"\"
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
        \"\"\"Guarantee exactly one reader task for this connection.

        Idempotent: a second call while the reader lives does nothing. That is the
        whole point - the reader count must not scale with the channel count.
        \"\"\"
        task = self._reader_task
        if task is not None and not task.done():
            return
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            return
        self._reader_task = loop.create_task(self._read_loop())

    async def _read_loop(self) -> None:
        \"\"\"The only reader on the pubsub connection.

        Dispatches on the arriving message's own channel, so a handler can never be
        handed another channel's payload - the leakage the per-channel loops caused.
        Restarts itself if the connection drops, because losing the reader silently
        is exactly the failure this fix exists to prevent.
        \"\"\"
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
        \"\"\"Rebuild the pubsub connection and re-SUBSCRIBE every known channel.\"\"\"
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
        \"\"\"Hand one message to the callbacks registered for ITS channel.\"\"\"
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
        \"\"\"Turn wire bytes back into the DomainEvent the publisher sent.

        Falls back to the parsed dict for anything this process cannot deserialise,
        so an unfamiliar payload is still delivered rather than dropped.
        \"\"\"
        try:
            payload = json.loads(data) if isinstance(data, (bytes, str)) else data
        except (TypeError, ValueError):
            return data
        if isinstance(payload, dict):
            try:
                return DomainEvent.from_dict(payload)
            except Exception:  # noqa: BLE001 - never lose a message over the envelope
                return payload
        return payload""",
    ),

    # --- unsubscribe() must also detach the redis-side handler
    (
        """    def unsubscribe(self, channel: Any, callback: Callable[[Any], None]) -> bool:""",
        """    def unsubscribe(self, channel: Any, callback: Callable[[Any], None]) -> bool:""",
    ),

    # --- disconnect(): stop the reader before tearing down the connection
    (
        """        \"\"\"Closes the Redis connection and cleans up resources.\"\"\"
        if self._pubsub:""",
        """        \"\"\"Closes the Redis connection and cleans up resources.\"\"\"
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

        if self._pubsub:""",
    ),
])

# unsubscribe(): remove the redis registration alongside the local one.
# The existing docstring claims only the in-process registration is removed because
# "the Redis pubsub channel is shared and may still have other subscribers" - true of
# the CONNECTION, but it left this callback registered on the reader, so a worker that
# unsubscribed kept being called. _unsubscribe_redis() drops just this callback and
# only issues UNSUBSCRIBE when it was the channel's last one, which is what that
# caveat actually required.
patch(BUS, [(
    """        key = normalize_channel(channel)
        handlers = self._local_handlers.get(key)
        if not handlers:
            return False
        try:
            handlers.remove(callback)
            return True
        except ValueError:
            return False""",
    """        key = normalize_channel(channel)
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
            return False""",
)])

print(f"applied to {len(applied)} file(s):" if applied else "nothing to do: already patched")
for f in applied:
    print("  ", f)
