"""M10 patch part 2: create_order.py market-order re-read waits for a
self-consistent row. On an async bus (Redis) the orchestrator executes in
another task/process, and ONE re-read can catch the order mid-flight: state
already FILLED while volume_current has not been written yet. The HTTP response
then reported filled_volume 0 for a fully filled order (seen on the M10 cloud
gate; the in-process bus awaits subscribers inline, which hid it)."""
import io
import sys

OLD = '''        # 9. Re-read the order: with an in-process bus the orchestrator has already run,
        #    so the entity the caller receives reflects the fill rather than the intent.
        final_order = saved_order
        if is_market:
            try:
                refreshed = await self.order_repo.find_by_id(saved_order.ticket_id)
                if refreshed is not None:
                    final_order = refreshed
            except Exception as exc:  # noqa: BLE001 - the saved order is still a valid answer
                logger.debug("could not re-read order %s after execution: %s", saved_order.ticket_id, exc)
'''

NEW = '''        # 9. Re-read the order: with an in-process bus the orchestrator has already run,
        #    so the entity the caller receives reflects the fill rather than the intent.
        #    On an ASYNC bus (Redis) execution lands in another task/process and a single
        #    re-read can catch the row mid-flight - state already FILLED while
        #    volume_current has not been zeroed yet, which made the HTTP response report
        #    filled_volume 0 for a genuinely filled order. Retry briefly until the row is
        #    self-consistent: a FILLED order always carries volume_current == 0, because
        #    apply_fill() reduces the volume and transitions the state on one object.
        final_order = saved_order
        if is_market:
            deadline = time.monotonic() + _MARKET_REFRESH_WINDOW_S
            while True:
                try:
                    refreshed = await self.order_repo.find_by_id(saved_order.ticket_id)
                except Exception as exc:  # noqa: BLE001 - the saved order is still a valid answer
                    logger.debug("could not re-read order %s after execution: %s", saved_order.ticket_id, exc)
                    break
                if refreshed is None:
                    break
                final_order = refreshed
                inconsistent = (
                    refreshed.state is OrderState.FILLED
                    and refreshed.volume_current.value > Decimal("0")
                )
                if not inconsistent or time.monotonic() >= deadline:
                    if inconsistent:
                        logger.warning(
                            "order %s still reads FILLED with volume_current=%s after %.1fs "
                            "of re-reads; returning it as-is",
                            saved_order.ticket_id, refreshed.volume_current.value,
                            _MARKET_REFRESH_WINDOW_S,
                        )
                    break
                await asyncio.sleep(_MARKET_REFRESH_DELAY_S)
'''

OLD_IMPORTS = '''import logging
from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal
from typing import Any, Optional
'''

NEW_IMPORTS = '''import asyncio
import logging
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal
from typing import Any, Optional
'''

# module-level constants, right after the imports block anchor
ANCHOR = '''logger = logging.getLogger(__name__)
'''
CONSTS = '''logger = logging.getLogger(__name__)

#: How long a market-order response waits for the executed row to become
#: self-consistent on an async bus (M10). Bounded: the response must not hang
#: when the execution plane is genuinely down - it returns the last read.
_MARKET_REFRESH_WINDOW_S = 1.5
_MARKET_REFRESH_DELAY_S = 0.05
'''


def patch(path, replacements):
    with io.open(path, "r", encoding="utf-8", newline="") as f:
        text = f.read()
    crlf = "\r\n" in text
    for old, new in replacements:
        if crlf:
            old = old.replace("\n", "\r\n")
            new = new.replace("\n", "\r\n")
        if text.count(old) != 1:
            print(f"FAIL: pattern occurs {text.count(old)}x in {path}: {old[:80]!r}")
            sys.exit(1)
        text = text.replace(old, new)
    with io.open(path, "w", encoding="utf-8", newline="") as f:
        f.write(text)
    print(f"patched {path} (crlf={crlf})")


patch("application/commands/create_order.py", [
    (OLD_IMPORTS, NEW_IMPORTS),
    (ANCHOR, CONSTS),
    (OLD, NEW),
])
print("OK part2")
