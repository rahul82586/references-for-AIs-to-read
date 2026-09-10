"""
Step M3 part 16 - the last two tests, both of which could not fail as written.

1. `test_event_bridge_routes_tick` called `bridge._handle_tick(event_dict)`, a method that
   has never existed - the real handler is `_on_tick_received(event: DomainEvent)`. Worse,
   it asserted on a local `manager = AsyncMock()` that was never connected to the bridge:
   WebSocketEventBridge resolves its own subscription manager internally via
   `get_manager_subscription_manager()`, a module-level singleton, and takes only
   `event_bus`. So the assertion inspected an object nothing ever called. Even had the
   method name been right, the test would have passed against a mock that was never
   exercised - the same failure mode as the "25/25 PASS" in api_test_results.md.

   Rewritten to patch the singleton the bridge actually uses, call the real handler with a
   real DomainEvent, and assert the broadcast that genuinely happens.

2. `test_concurrent_deal_execution_atomicity_and_locking` built `Order(volume=, price=)`.
   MT5's order fields - and the entity's - are `volume_initial` / `volume_current` and
   `price_order`. The distinction matters: volume_initial is what was requested and
   volume_current is what remains, and collapsing them is how partial fills get lost.
"""

from __future__ import annotations

import pathlib
import re
import sys

ROOT = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else pathlib.Path.cwd()
if not (ROOT / "tests").is_dir():
    raise SystemExit(f"not a broker-platform root: {ROOT}")


def load(rel: str) -> str:
    with open(ROOT / rel, encoding="utf-8", newline="") as fh:
        return fh.read()


def save(rel: str, text: str, crlf: bool) -> None:
    norm = text.replace("\r\n", "\n")
    with open(ROOT / rel, "w", encoding="utf-8", newline="") as fh:
        fh.write(norm.replace("\n", "\r\n") if crlf else norm)


# ---------------------------------------------------------------------------
# 1. Order field names in the concurrency test
# ---------------------------------------------------------------------------

REL = "tests/unit/concurrency/test_execution_concurrency.py"
text = load(REL)
crlf = "\r\n" in text
work = text.replace("\r\n", "\n")
before = work

# volume= -> volume_initial= and price= -> price_order=, but only inside Order(...) calls.
def _balanced(source: str, name: str):
    spans = []
    for match in re.finditer(re.escape(name) + r"\(", source):
        i = match.end()
        depth = 1
        while i < len(source) and depth:
            if source[i] == "(":
                depth += 1
            elif source[i] == ")":
                depth -= 1
            i += 1
        spans.append((match.start(), i))
    return spans


for start, end in reversed(_balanced(work, "Order")):
    call = work[start:end]
    fixed = re.sub(r"\bvolume=", "volume_initial=", call)
    fixed = re.sub(r"\bprice=(?!_)", "price_order=", fixed)
    work = work[:start] + fixed + work[end:]

if work != before:
    save(REL, work, crlf)
    print(f"  ok  {REL}: Order(volume=/price=) -> volume_initial=/price_order=")
else:
    print(f"  --  {REL}: nothing to change")

# ---------------------------------------------------------------------------
# 2. The event-bridge test
# ---------------------------------------------------------------------------

REL = "tests/unit/api/test_api.py"
text = load(REL)
crlf = "\r\n" in text
work = text.replace("\r\n", "\n")

start = work.find("async def test_event_bridge_routes_tick")
if start == -1:
    raise SystemExit("[FAIL] test_api.py: test_event_bridge_routes_tick was not found")
# Bound the replacement at the next section banner or test definition.
tail = work[start:]
match = re.search(r"\n# -{10,}\n# Test \d+", tail)
if match is None:
    match = re.search(r"\n(?:@pytest\.mark\.asyncio\n)?(?:async )?def (?!test_event_bridge)", tail)
end = start + match.start() if match else len(work)

NEW = '''async def test_event_bridge_routes_tick():
    """A tick event on the bus must reach the WebSocket subscribers.

    The previous version of this test called `bridge._handle_tick(...)`, a method that has
    never existed, and asserted on a local `manager = AsyncMock()` that was never connected
    to the bridge - WebSocketEventBridge resolves its own subscription manager internally
    via get_manager_subscription_manager(). So the assertion inspected an object nothing
    ever called, and the test could not have failed no matter what the bridge did.

    This version patches the singleton the bridge actually uses, calls the real handler
    with a real DomainEvent, and asserts the broadcast that genuinely occurs.
    """
    from unittest.mock import patch

    from core.events.domain_events import DomainEvent, EventType

    event_bus = AsyncMock()
    manager = AsyncMock()

    with patch(
        "api.websockets.event_bridge.get_manager_subscription_manager",
        return_value=manager,
    ):
        bridge = WebSocketEventBridge(event_bus=event_bus)

    assert bridge.subscription_manager is manager, (
        "the bridge must use the patched singleton; if this fails the test is asserting "
        "against a manager the bridge never touches"
    )

    payload = {
        "symbol": "EURUSD",
        "bid": "1.0800",
        "ask": "1.0802",
        "spread": "0.0002",
    }
    event = DomainEvent(event_type=EventType.TICK_RECEIVED, payload=payload)

    await bridge._on_tick_received(event)

    manager.broadcast.assert_awaited_once_with("ticks", payload)


'''

work = work[:start] + NEW + work[end:]

save(REL, work, crlf)
print(f"  ok  {REL}: event-bridge test now exercises the real handler and the real manager")

# ---------------------------------------------------------------------------
# 3. The concurrency test skips a state in the order lifecycle
# ---------------------------------------------------------------------------
#
# Order._VALID_TRANSITIONS is:
#     STARTED          -> PLACED | REJECTED | CANCELLED
#     PLACED           -> PARTIALLY_FILLED | FILLED | ...
#     PARTIALLY_FILLED -> PARTIALLY_FILLED | FILLED | ...
#     FILLED           -> (terminal)
#
# The test created its orders in state NEW and then had RecordDealHandler fill them,
# which is STARTED -> FILLED: two steps at once. The state machine correctly refused, so
# the failure is the test skipping a state, not the machine being too strict. An order
# that has not been placed on the market cannot be filled against it.
#
# The orders are moved through PLACED before the deals are recorded, which is what a real
# execution path does.

REL = "tests/unit/concurrency/test_execution_concurrency.py"
text = load(REL)
crlf = "\r\n" in text
work = text.replace("\r\n", "\n")
before = work

OLD = '''    order_repo = MockOrderRepository()
    await order_repo.save(order1)
    await order_repo.save(order2)'''
NEW = '''    # An order cannot go STARTED -> FILLED. Order._VALID_TRANSITIONS requires it to be
    # PLACED first, which is correct: an order that was never sent to the market cannot be
    # filled against it. The test previously relied on the transition being allowed, so it
    # was really asserting that the state machine was too permissive.
    order1.transition_to(OrderState.PLACED)
    order2.transition_to(OrderState.PLACED)

    order_repo = MockOrderRepository()
    await order_repo.save(order1)
    await order_repo.save(order2)'''

if OLD in work:
    work = work.replace(OLD, NEW, 1)
else:
    raise SystemExit("[FAIL] concurrency test: the order_repo setup anchor was not found")

# `state=OrderState.NEW` - the entity's own initial state is STARTED, and NEW is not a
# member of the transition table, so an order built with it can never move anywhere.
work = work.replace("state=OrderState.NEW", "state=OrderState.STARTED")

if work != before:
    save(REL, work, crlf)
    print(f"  ok  {REL}: orders transition through PLACED; state=NEW -> STARTED")
