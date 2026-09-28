"""D5 probe: does Redis pub/sub deliver to more than one channel?

Not a test - a live diagnostic against the real Upstash instance. Two bus
instances (standing in for two processes) subscribe to three channels between
them, then each channel is published once.

Before the fix: one `listen()` loop per channel over a single shared pubsub
connection. redis-py raises `readuntil() called while another coroutine is already
waiting for incoming data` on every loop after the first, so exactly 1 of 3
channels delivers and the other two log an error and die.
"""
import asyncio
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from infrastructure.messaging.redis_event_bus import RedisEventBus  # noqa: E402


def redis_url() -> str:
    env = (ROOT / ".env").read_text(encoding="utf-8")
    m = re.search(r"rediss?://[^\s\"']+", env)
    if not m:
        raise SystemExit("no REDIS_URL in .env")
    return m.group(0)


async def main() -> int:
    url = redis_url()
    print(f"redis: {url.split('@')[-1]}")

    a, b = RedisEventBus(url), RedisEventBus(url)
    await a.connect()
    await b.connect()
    print(f"connected: a={await a.ping()} b={await b.ping()}")

    got = {"ch1": [], "ch2": [], "ch3": []}
    # ch1 and ch3 on bus A, ch2 on bus B - so this also proves cross-instance delivery
    a.subscribe("d5.probe.ch1", lambda p: got["ch1"].append(p))
    b.subscribe("d5.probe.ch2", lambda p: got["ch2"].append(p))
    a.subscribe("d5.probe.ch3", lambda p: got["ch3"].append(p))
    await asyncio.sleep(2.0)

    for i, ch in enumerate(("d5.probe.ch1", "d5.probe.ch2", "d5.probe.ch3"), 1):
        await a._redis_client.publish(ch, json.dumps({"x": i}).encode())
    await asyncio.sleep(3.0)

    for k, v in got.items():
        print(f"  {k}: {v}")
    delivered = sum(1 for v in got.values() if v)
    print(f"\nRESULT: {delivered}/3 channels delivered -> "
          f"{'ALL OK' if delivered == 3 else 'D5 REPRODUCED (only the first loop survives)'}")

    await a.disconnect()
    await b.disconnect()
    return 0 if delivered == 3 else 1


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
