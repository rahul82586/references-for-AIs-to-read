"""D5 - Redis pub/sub must deliver to every channel, to the right handler.

The defect, reproduced live against Upstash before the fix:

    ch1: [{'x': 1}, {'x': 3}]     <- received ch3's message as well
    ch2: [{'x': 2}]
    ch3: []                       <- its listener had already died
    RESULT: 2/3 channels delivered

`subscribe()` started one `listen()` loop per channel over a single shared pubsub
connection. redis-py allows one reader per connection, so every loop after the
first raised `readuntil() called while another coroutine is already waiting for
incoming data`, logged it once, and died. The survivor then read every message on
the socket and passed it to its own callback whatever channel it had arrived on -
so a handler written for one event type was handed another's data.

These tests pin the replacement: one reader per connection, dispatch keyed on the
message's own channel.

They run against a fake pubsub, so they are deterministic and need no server;
scripts/d5_redis_probe.py is the live end-to-end check and must report 3/3.
"""
from __future__ import annotations

import asyncio
import json
from typing import Any, Dict, List

import pytest

from core.events.domain_events import DomainEvent, EventType
from core.ports.interfaces import normalize_channel
from infrastructure.messaging.redis_event_bus import RedisEventBus


class FakePubSub:
    """Just enough of redis.asyncio PubSub for the reader loop."""

    def __init__(self) -> None:
        self.subscribed: List[str] = []
        self.queue: asyncio.Queue = asyncio.Queue()
        self.closed = False

    async def subscribe(self, *channels: str) -> None:
        self.subscribed.extend(channels)

    async def unsubscribe(self, *channels: str) -> None:
        for c in channels:
            if c in self.subscribed:
                self.subscribed.remove(c)

    async def get_message(self, ignore_subscribe_messages: bool = True,
                          timeout: float = 0.0) -> Any:
        try:
            return await asyncio.wait_for(self.queue.get(), timeout=timeout or 0.05)
        except asyncio.TimeoutError:
            return None

    async def close(self) -> None:
        self.closed = True

    def push(self, channel: str, payload: Any) -> None:
        data = payload if isinstance(payload, (bytes, str)) else json.dumps(payload).encode()
        self.queue.put_nowait({"type": "message", "channel": channel.encode(), "data": data})


class FakeRedis:
    def __init__(self, pubsub: FakePubSub) -> None:
        self._pubsub = pubsub
        self.published: List[tuple] = []

    def pubsub(self) -> FakePubSub:
        return self._pubsub

    async def publish(self, channel: str, message: bytes) -> int:
        self.published.append((channel, message))
        return 1

    async def close(self) -> None:
        pass


@pytest.fixture()
def bus_and_pubsub():
    """A RedisEventBus wired to a fake connection, with connect() short-circuited."""
    fake = FakePubSub()
    bus = RedisEventBus("redis://localhost:6379")

    async def _fake_connect() -> None:
        bus._redis_client = FakeRedis(fake)
        bus._pubsub = fake

    bus.connect = _fake_connect  # type: ignore[method-assign]
    return bus, fake


async def _drain(bus: RedisEventBus, fake: FakePubSub, settle: float = 0.2) -> None:
    """Let the reader task run until the queue is empty, then a little further."""
    for _ in range(200):
        if fake.queue.empty():
            break
        await asyncio.sleep(0.01)
    await asyncio.sleep(settle)


# --------------------------------------------------------------- the headline bug

@pytest.mark.asyncio
async def test_every_channel_delivers_not_just_the_first(bus_and_pubsub):
    """The defect: only the first subscriber's loop survived."""
    bus, fake = bus_and_pubsub
    got: Dict[str, List[Any]] = {"a": [], "b": [], "c": [], "d": [], "e": []}

    for name in got:
        bus.subscribe(f"d5.{name}", lambda ev, n=name: got[n].append(ev))
    await _drain(bus, fake)

    for name in got:
        fake.push(f"d5.{name}", {"event_type": "order.created", "payload": {"who": name}})
    await _drain(bus, fake)

    empty = [n for n, v in got.items() if not v]
    assert not empty, f"these channels never delivered: {empty}"
    assert len(got) == 5


@pytest.mark.asyncio
async def test_a_handler_never_receives_another_channels_message(bus_and_pubsub):
    """The leakage: ch1's callback was handed ch3's payload."""
    bus, fake = bus_and_pubsub
    got: Dict[str, List[Any]] = {"x": [], "y": []}
    for name in got:
        bus.subscribe(f"d5.leak.{name}", lambda ev, n=name: got[n].append(ev))
    await _drain(bus, fake)

    fake.push("d5.leak.x", {"event_type": "order.created", "payload": {"who": "x"}})
    await _drain(bus, fake)

    assert len(got["x"]) == 1
    assert got["x"][0].payload == {"who": "x"}
    assert got["y"] == [], "y's handler must not see x's message"


@pytest.mark.asyncio
async def test_the_channel_count_does_not_spawn_more_readers(bus_and_pubsub):
    """One reader per connection, however many channels are added."""
    bus, fake = bus_and_pubsub
    for i in range(20):
        bus.subscribe(f"d5.many.{i}", lambda ev: None)
    await _drain(bus, fake)

    reader = bus._reader_task
    assert reader is not None and not reader.done()
    before = sum(1 for t in asyncio.all_tasks() if not t.done())

    for i in range(20, 30):
        bus.subscribe(f"d5.many.{i}", lambda ev: None)
    await _drain(bus, fake)

    assert bus._reader_task is reader, "the reader must be reused, not replaced"
    after = sum(1 for t in asyncio.all_tasks() if not t.done())
    assert after - before < 5, f"10 channels spawned {after - before} tasks"


@pytest.mark.asyncio
async def test_all_channels_actually_reach_redis_subscribe(bus_and_pubsub):
    bus, fake = bus_and_pubsub
    for i in range(6):
        bus.subscribe(f"d5.sub.{i}", lambda ev: None)
    await _drain(bus, fake)
    assert sorted(fake.subscribed) == sorted(f"d5.sub.{i}" for i in range(6))


# ------------------------------------------------------------------- event parity

@pytest.mark.asyncio
async def test_remote_handlers_receive_a_domain_event_like_the_inprocess_bus(bus_and_pubsub):
    """The reader used to pass a raw dict; InProcessEventBus passes a DomainEvent.

    The same handler therefore got a different type depending on which bus the
    server was configured with.
    """
    bus, fake = bus_and_pubsub
    received: List[Any] = []
    bus.subscribe("d5.parity", received.append)
    await _drain(bus, fake)

    original = DomainEvent(event_type=EventType.ORDER_CREATED,
                           aggregate_id="ORD-1", payload={"symbol": "EURUSD"})
    fake.push("d5.parity", original.to_dict())
    await _drain(bus, fake)

    assert len(received) == 1
    ev = received[0]
    assert isinstance(ev, DomainEvent), f"expected a DomainEvent, got {type(ev).__name__}"
    assert ev.event_id == original.event_id
    assert ev.aggregate_id == "ORD-1"
    assert ev.payload == {"symbol": "EURUSD"}
    assert ev.event_type == EventType.ORDER_CREATED
    assert ev.timestamp == original.timestamp


@pytest.mark.asyncio
async def test_an_unparsable_payload_is_delivered_not_dropped(bus_and_pubsub):
    """A malformed envelope must not silently lose the message."""
    bus, fake = bus_and_pubsub
    received: List[Any] = []
    bus.subscribe("d5.junk", received.append)
    await _drain(bus, fake)

    fake.push("d5.junk", b"not json at all")
    await _drain(bus, fake)
    assert len(received) == 1, "junk is still delivered, as raw bytes"

    fake.push("d5.junk", {"event_type": "not.a.real.type", "payload": {"k": 1}})
    await _drain(bus, fake)
    assert len(received) == 2
    assert received[1].payload == {"k": 1}, "an unknown event_type keeps the payload"


@pytest.mark.asyncio
async def test_a_raising_handler_does_not_stop_the_reader(bus_and_pubsub):
    bus, fake = bus_and_pubsub
    ok: List[Any] = []

    def boom(ev: Any) -> None:
        raise RuntimeError("handler is broken")

    bus.subscribe("d5.boom", boom)
    bus.subscribe("d5.fine", ok.append)
    await _drain(bus, fake)

    for ch in ("d5.boom", "d5.fine", "d5.boom", "d5.fine"):
        fake.push(ch, {"event_type": "order.created", "payload": {}})
    await _drain(bus, fake)

    assert len(ok) == 2, "the healthy handler keeps receiving after the other raises"
    assert bus._reader_task is not None and not bus._reader_task.done()


# ------------------------------------------------------------------- async handlers

@pytest.mark.asyncio
async def test_async_handlers_are_awaited(bus_and_pubsub):
    bus, fake = bus_and_pubsub
    done: List[str] = []

    async def slow(ev: Any) -> None:
        await asyncio.sleep(0.01)
        done.append("awaited")

    bus.subscribe("d5.async", slow)
    await _drain(bus, fake)
    fake.push("d5.async", {"event_type": "order.created", "payload": {}})
    await _drain(bus, fake, settle=0.3)
    assert done == ["awaited"]


# ---------------------------------------------------------------------- unsubscribe

@pytest.mark.asyncio
async def test_unsubscribe_stops_delivery_to_that_handler(bus_and_pubsub):
    """The old docstring kept the Redis registration alive after unsubscribe."""
    bus, fake = bus_and_pubsub
    received: List[Any] = []

    def handler(ev: Any) -> None:
        received.append(ev)

    bus.subscribe("d5.off", handler)
    await _drain(bus, fake)

    fake.push("d5.off", {"event_type": "order.created", "payload": {"n": 1}})
    await _drain(bus, fake)
    assert len(received) == 1

    assert bus.unsubscribe("d5.off", handler) is True

    fake.push("d5.off", {"event_type": "order.created", "payload": {"n": 2}})
    await _drain(bus, fake)
    assert len(received) == 1, "an unsubscribed handler must not be called again"


@pytest.mark.asyncio
async def test_unsubscribe_leaves_other_handlers_on_the_channel(bus_and_pubsub):
    """Removing one callback must not unsubscribe the channel out from under another.

    This is the caveat the old docstring cited for never touching Redis at all; the
    fix honours it by issuing UNSUBSCRIBE only when the last callback goes.
    """
    bus, fake = bus_and_pubsub
    first: List[Any] = []
    second: List[Any] = []

    def handler_one(ev: Any) -> None:
        first.append(ev)

    def handler_two(ev: Any) -> None:
        second.append(ev)

    bus.subscribe("d5.shared", handler_one)
    bus.subscribe("d5.shared", handler_two)
    await _drain(bus, fake)

    assert bus.unsubscribe("d5.shared", handler_one) is True
    assert "d5.shared" in fake.subscribed, (
        "the channel must stay subscribed while another handler still wants it")

    fake.push("d5.shared", {"event_type": "order.created", "payload": {}})
    await _drain(bus, fake)
    assert first == [], "the removed handler must not be called"
    assert len(second) == 1, "the remaining handler must still receive"


@pytest.mark.asyncio
async def test_unsubscribing_the_last_handler_releases_the_channel(bus_and_pubsub):
    bus, fake = bus_and_pubsub

    def only(ev: Any) -> None:
        pass

    bus.subscribe("d5.last", only)
    await _drain(bus, fake)
    assert "d5.last" in fake.subscribed

    assert bus.unsubscribe("d5.last", only) is True
    await _drain(bus, fake)
    assert "d5.last" not in fake.subscribed, "no handler left: the channel should go"


# ---------------------------------------------------------------------- disconnect

@pytest.mark.asyncio
async def test_disconnect_stops_the_reader(bus_and_pubsub):
    bus, fake = bus_and_pubsub
    bus.subscribe("d5.bye", lambda ev: None)
    await _drain(bus, fake)
    reader = bus._reader_task
    assert reader is not None and not reader.done()

    await bus.disconnect()
    await asyncio.sleep(0.1)
    assert reader.done(), "the reader must be cancelled on disconnect"
    assert bus._reader_task is None


# -------------------------------------------------------------------- channel keys

@pytest.mark.asyncio
async def test_class_and_enum_and_string_channels_all_match(bus_and_pubsub):
    """A publisher's channel convention must not decide who receives."""
    bus, fake = bus_and_pubsub
    received: List[Any] = []
    bus.subscribe(EventType.TICK_RECEIVED, received.append)
    await _drain(bus, fake)

    key = normalize_channel(EventType.TICK_RECEIVED)
    fake.push(key, {"event_type": EventType.TICK_RECEIVED.value, "payload": {"bid": "1.1"}})
    await _drain(bus, fake)
    assert len(received) == 1
    assert received[0].payload == {"bid": "1.1"}


# ------------------------------------------------------------------- from_dict unit

def test_from_dict_round_trips_every_field():
    original = DomainEvent(event_type=EventType.DEAL_CREATED, aggregate_id="D-9",
                           payload={"volume": "0.10", "price": "1.10010"})
    back = DomainEvent.from_dict(original.to_dict())
    assert back.event_id == original.event_id
    assert back.timestamp == original.timestamp
    assert back.aggregate_id == original.aggregate_id
    assert back.event_type == original.event_type
    assert back.payload == original.payload


def test_from_dict_tolerates_a_missing_or_bad_envelope():
    assert DomainEvent.from_dict({}).payload == {}
    assert DomainEvent.from_dict({"timestamp": "not-a-date"}).payload == {}
    ev = DomainEvent.from_dict({"event_type": "invented.event", "payload": {"a": 1}})
    assert ev.payload == {"a": 1}, "an unknown type must not lose the payload"
