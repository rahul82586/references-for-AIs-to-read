"""
Step M1 part 6a - rebalance the liquidation fixture's group thresholds.

Kept separate from m1_fix_liquidation_and_mappers.py because the block it replaces
contains a backslash group path ("real\\real"), which is fragile to match inside a
patch script that is itself a Python string. Anchoring on the threshold lines and
walking back over the preceding comment block avoids the escaping entirely.

The fixture account sits at 54.55% and recovers to 109.09% after the worst position
is closed, so stop-out has to sit between the two: 60%.
"""

from __future__ import annotations

import pathlib
import sys

ROOT = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else pathlib.Path.cwd()
LIQ = ROOT / "tests" / "integration" / "test_liquidation_worker.py"
if not LIQ.is_file():
    raise SystemExit(f"not found: {LIQ}")

with open(LIQ, encoding="utf-8", newline="") as fh:
    text = fh.read()

crlf = "\r\n" in text
work = text.replace("\r\n", "\n")

CALL = "            margin_call_level=Decimal('80'),"
STOP = "            stop_out_level=Decimal('30'),"

if STOP not in work:
    if "stop_out_level=Decimal('60')," in work:
        print("  ok  liquidation fixture thresholds already at 80/60")
        raise SystemExit(0)
    raise SystemExit("[FAIL] liquidation test: stop_out_level=Decimal('30') anchor not found")
if CALL not in work:
    raise SystemExit("[FAIL] liquidation test: margin_call_level=Decimal('80') anchor not found")

call_at = work.find(CALL)
stop_end = work.find(STOP) + len(STOP)

# Walk back from the margin_call_level line over the contiguous comment block that
# documents it, so the stale comment goes with the stale value.
block_start = work.rfind("\n", 0, call_at)
while block_start > 0:
    prev = work.rfind("\n", 0, block_start)
    segment = work[prev + 1 : block_start]
    if segment.strip().startswith("#"):
        block_start = prev
    else:
        break
block_start += 1  # keep the leading newline of the first comment line

REPLACEMENT = (
    "            # PERCENT, the MT5 convention. The fixture account sits at 54.55%,\n"
    "            # so stop-out has to be above that for the worker to act at all, and\n"
    "            # below the 109.09% it recovers to once the worst position is closed,\n"
    "            # or the worker would liquidate both positions.\n"
    "            margin_call_level=Decimal('80'),\n"
    "            stop_out_level=Decimal('60'),"
)

work = work[:block_start] + REPLACEMENT + work[stop_end:]

with open(LIQ, "w", encoding="utf-8", newline="") as fh:
    fh.write(work.replace("\n", "\r\n") if crlf else work)

print("  ok  test_liquidation_worker.py: thresholds now 80% call / 60% stop-out")
