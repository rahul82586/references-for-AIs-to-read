"""
In-Process Event Bus - the single-node IEventBus implementation.

Why this exists
---------------
The only IEventBus in the tree was RedisEventBus. That made every "set up and run"
step depend on a Redis server, and it made the execution path untestable without one:
`publish()` connects on first call and re-raises when the connection fails, so an
order placed on a machine with only PostgreSQL running died in the event bus rather
than in the trade.

This bus keeps the SAME dispatch semantics as RedisEventBus._dispatch_local, so a
deployment can move from one node to many by swapping the class and nothing else:

  * registration is synchronous, because an `async def subscribe` that 20 of 24 call
    sites did not await silently registered nothing (see IEventBus.subscribe);
  * a handler may be registered under an event class, an EventType member or that
    member's string value, and all three normalise to the same key;
  * one failing handler is logged and skipped rather than aborting the fan-out;
  * an awaitable handler is awaited, so publishing an OrderApprovedEvent returns only
    once the ExecutionOrchestrator has finished executing it. That is what makes
    "place an order, then assert the position exists" a synchronous test instead of a
    race against a background task.

The bus also records every event it has seen. That is not a test convenience bolted
onto production code: it is the audit trail of a single node, and the Redis bus keeps
the same information server-side.
"""
from __future__ import annotations

import inspect
import logging
from typing import Any, Callable, Dict, List, Optional

from core.events.domain_events import DomainEvent
from core.ports.interfaces import IEventBus, normalize_channel

logger = logging.getLogger(__name__)


class _Subscription:
    """Awaitable, cancellable registration handle.

    `subscribe()` must return immediately so registration completes before the caller
    publishes anything, but call sites both `await` it and ignore it. Returning an
    object that is awaitable AND already registered satisfies both without making an
    unawaited call a no-op.
    """

    def __init__(self, bus: "InProcessEventBus", key: str, callback: Callable[[Any], Any]) -> None:
        self._bus = bus
        self._key = key
        self._callback = callback

    def __await__(self):
        async def _ready() -> "_Subscription":
            return self

        return _ready().__await__()

    def cancel(self) -> None:
        """Remove this registration. Idempotent."""
        self._bus.unsubscribe(self._key, self._callback)


class InProcessEventBus(IEventBus):
    """Single-process fan-out bus. No broker required."""

    def __init__(self, *, record_events: bool = True) -> None:
        #: channel key -> handlers, in registration order
        self._handlers: Dict[str, List[Callable[[Any], Any]]] = {}
        #: every event published, oldest first
        self.published: List[DomainEvent] = []
        self._record_events = record_events
        #: guard against a handler that publishes the event it subscribes to
        self._depth = 0
        self._max_depth = 32

    # ------------------------------------------------------------------
    # IEventBus
    # ------------------------------------------------------------------

    async def publish(self, event: DomainEvent) -> None:
        """Deliver to every in-process subscriber, awaiting async handlers."""
        if self._record_events:
            self.published.append(event)

        self._depth += 1
        try:
            if self._depth > self._max_depth:
                logger.error(
                    "event dispatch depth exceeded %s at %s; dropping to break a "
                    "publish/subscribe cycle",
                    self._max_depth,
                    getattr(event, "event_type", type(event).__name__),
                )
                return
            await self._dispatch(event)
        finally:
            self._depth -= 1

    def subscribe(self, channel: Any, callback: Callable[[Any], Any]) -> Any:
        """Register immediately; the returned handle is also awaitable."""
        key = normalize_channel(channel)
        self._handlers.setdefault(key, []).append(callback)
        logger.debug("subscribed %s to channel %s", getattr(callback, "__name__", callback), key)
        return _Subscription(self, key, callback)

    def unsubscribe(self, channel: Any, callback: Callable[[Any], Any]) -> bool:
        """Remove one registration. Returns True if something was removed."""
        key = normalize_channel(channel)
        handlers = self._handlers.get(key)
        if not handlers:
            return False
        try:
            handlers.remove(callback)
            return True
        except ValueError:
            return False

    async def disconnect(self) -> None:
        """Drop every registration."""
        self._handlers.clear()

    # ------------------------------------------------------------------
    # Inspection
    # ------------------------------------------------------------------

    def events_of(self, channel: Any) -> List[DomainEvent]:
        """Every published event registered under this class / EventType / string."""
        key = normalize_channel(channel)
        out: List[DomainEvent] = []
        for event in self.published:
            if key in self._keys_for(event):
                out.append(event)
        return out

    def handler_count(self, channel: Any) -> int:
        return len(self._handlers.get(normalize_channel(channel), []))

    # ------------------------------------------------------------------
    # Internals
    # ------------------------------------------------------------------

    @staticmethod
    def _keys_for(event: Any) -> set:
        """The channel keys an event is delivered under - all three conventions."""
        keys = {normalize_channel(type(event))}
        event_type = getattr(event, "event_type", None)
        if event_type is not None:
            keys.add(normalize_channel(event_type))
            keys.add(normalize_channel(getattr(event_type, "value", event_type)))
        return keys

    async def _dispatch(self, event: Any) -> None:
        for key in self._keys_for(event):
            # Iterate a copy: a handler may subscribe or unsubscribe during dispatch.
            for handler in list(self._handlers.get(key, [])):
                try:
                    result = handler(event)
                    if inspect.isawaitable(result):
                        await result
                except Exception as exc:  # noqa: BLE001 - one bad handler must not stop the rest
                    logger.error(
                        "event handler %s for %s raised %s: %s",
                        getattr(handler, "__name__", handler),
                        key,
                        type(exc).__name__,
                        exc,
                        exc_info=True,
                    )
