"""
Step M3 part 15 - the last two constructor-drift sites.

1. `tests/unit/api/test_api.py`
       bridge = WebSocketEventBridge(event_bus=event_bus, connection_manager=manager)
   The bridge takes only `event_bus`; it resolves its subscription manager internally via
   `get_manager_subscription_manager()`. The earlier regex expected `connection_manager` to
   be the sole argument, so it did not match this two-argument call. The fix drops the
   extra kwarg.

2. `tests/unit/concurrency/test_execution_concurrency.py`
       Symbol(margin_initial_percent=..., margin_maintenance_percent=...)
   Neither field exists - `Symbol` carries `margin_rates` (the 8+8 multipliers), while
   MarginInitial / MarginMaintenance are absolute money amounts that live on the symbol
   CONFIGURATION, not the domain Symbol. The earlier strip covered only the two risk test
   files. Both kwargs are dropped; nothing in this test depends on them, since it exercises
   deal-execution atomicity, not margin.
"""

from __future__ import annotations

import pathlib
import re
import sys

ROOT = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else pathlib.Path.cwd()
if not (ROOT / "tests").is_dir():
    raise SystemExit(f"not a broker-platform root: {ROOT}")

FIXES = [
    "tests/unit/api/test_api.py",
    "tests/unit/concurrency/test_execution_concurrency.py",
    "tests/integration/test_e2e_flow.py",
    "tests/unit/domains/risk/test_cross_currency_pnl.py",
    "tests/unit/domains/risk/test_audit3_hardening.py",
]

for rel in FIXES:
    path = ROOT / rel
    if not path.is_file():
        continue
    with open(path, encoding="utf-8", newline="") as fh:
        text = fh.read()
    crlf = "\r\n" in text
    work = text.replace("\r\n", "\n")
    before = work

    # Drop the two non-existent Symbol margin kwargs, in any argument position.
    work = re.sub(r"^[ \t]*margin_initial(?:_percent)?=.*?,?[ \t]*\n", "", work, flags=re.M)
    work = re.sub(r"^[ \t]*margin_maintenance(?:_percent)?=.*?,?[ \t]*\n", "", work, flags=re.M)
    # A removed final argument can leave a dangling comma before the closing paren.
    work = re.sub(r",(\s*\))", r"\1", work)

    # WebSocketEventBridge takes only event_bus. Drop connection_manager wherever it
    # appears alongside it, and convert a lone connection_manager= into event_bus=.
    work = re.sub(r",\s*connection_manager=[^,)]+(?=\))", "", work)
    work = re.sub(r"connection_manager=([^,)]+),\s*(?=event_bus=)", "", work)
    work = re.sub(
        r"WebSocketEventBridge\(connection_manager=([^,)]+)\)",
        r"WebSocketEventBridge(event_bus=\1)",
        work,
    )

    if work != before:
        with open(path, "w", encoding="utf-8", newline="") as fh:
            fh.write(work.replace("\n", "\r\n") if crlf else work)
        print(f"  ok  {rel}: dropped the non-existent Symbol margin kwargs / bridge kwarg")
    else:
        print(f"  --  {rel}: nothing to change")
