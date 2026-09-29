"""D5 live proof: two bus instances, real events, real Redis.

This is the deployment shape RedisEventBus exists for - a second process whose
subscribers are the only delivery path. It publishes real DomainEvents through
`publish()` on one bus and asserts the other bus's handlers receive them, on every
channel, with the payload intact.

Run: python3 scripts/d5_redis_live_proof.py     (needs REDIS_URL in .env)
Exit 0 = every channel delivered with the right payload; 1 = something was lost.

The pre-fix behaviour this replaces was 2/3 delivered, with channel 1 receiving
channel 3's message as well.
"""
import asyncio
import re
import sys
from decimal import Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from core.events.domain_events import DomainEvent, EventType  # noqa: E402
from infrastructure.messaging.redis_event_bus import RedisEventBus  # noqa: E402

CHANNELS = [
    (EventType.ORDER_CREATED, "ORD-1", {"symbol": "EURUSD", "volume": "0.10"}),
    (EventType.DEAL_CREATED, "DEAL-1", {"price": "1.10010", "volume": "0.10"}),
    (EventType.TICK_RECEIVED, "TICK-1", {"bid": "1.10000", "ask": "1.10010"}),
    (EventType.POSITION_CLOSED, "POS-1", {"pnl": "-1.23"}),
    (EventType.STOP_OUT_INITIATED, "ACC-1", {"margin_level": "12.5"}),
]


def redis_url() -> str:
    env = (ROOT / ".env").read_text(encoding="utf-8")
    m = re.search(r"rediss?://[^\s\"']+", env)
    if not m:
        raise SystemExit("no REDIS_URL in .env")
    return m.group(0)


async def main() -> int:
    url = redis_url()
    print(f"redis: {url.split('@')[-1]}")

    # Two buses = two processes. The publisher talks to Redis; the subscriber is a
    # separate instance whose only route to these events is the pubsub connection.
    publisher = RedisEventBus(url)
    subscriber = RedisEventBus(url)
    await publisher.connect()
    await subscriber.connect()
    print(f"connected: publisher={await publisher.ping()} subscriber={await subscriber.ping()}")

    received: dict = {et.value: [] for et, _, _ in CHANNELS}
    for event_type, _, _ in CHANNELS:
        subscriber.subscribe(event_type, lambda ev, k=event_type.value: received[k].append(ev))

    await asyncio.sleep(2.0)          # let SUBSCRIBE land before publishing

    # A unique suffix per run, so a previous run's traffic cannot flatter this one.
    run_id = Decimal(asyncio.get_event_loop().time()).as_tuple().exponent
    for event_type, aggregate_id, payload in CHANNELS:
        await publisher.publish(DomainEvent(
            event_type=event_type,
            aggregate_id=f"{aggregate_id}-{run_id}",
            payload=dict(payload, run=str(run_id)),
        ))

    await asyncio.sleep(4.0)          # allow for cross-region latency

    print("\n=== delivery ===")
    failures = []
    for event_type, aggregate_id, payload in CHANNELS:
        key = event_type.value
        events = [e for e in received[key]
                  if isinstance(e, DomainEvent) and e.payload.get("run") == str(run_id)]
        ok = len(events) == 1
        detail = ""
        if ok:
            got = events[0]
            if got.aggregate_id != f"{aggregate_id}-{run_id}":
                ok, detail = False, f"aggregate_id {got.aggregate_id!r}"
            elif not all(got.payload.get(k) == v for k, v in payload.items()):
                ok, detail = False, f"payload {got.payload!r}"
            else:
                detail = f"type={type(got).__name__} aggregate={got.aggregate_id} payload ok"
        else:
            detail = f"expected 1 event, got {len(events)}"
        print(f"  {'PASS' if ok else 'FAIL'}  {key:<24} {detail}")
        if not ok:
            failures.append(key)

    # leakage: no handler may have seen another channel's event
    leaked = []
    for event_type, _, _ in CHANNELS:
        for ev in received[event_type.value]:
            if isinstance(ev, DomainEvent) and ev.event_type != event_type:
                leaked.append((event_type.value, ev.event_type.value))
    if leaked:
        print(f"\n  LEAKED across channels: {leaked}")
        failures.append(f"leakage:{leaked}")

    total = len(CHANNELS)
    good = total - len([f for f in failures if not f.startswith("leakage")])
    print(f"\nRESULT: {good}/{total} channels delivered correctly"
          f"{'' if not failures else '; FAILURES: ' + ', '.join(failures)}")

    await publisher.disconnect()
    await subscriber.disconnect()
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
