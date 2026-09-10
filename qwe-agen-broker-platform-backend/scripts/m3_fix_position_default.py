"""
Step M3 part 4 - Position can be constructed with its own defaults.

    Position(position_id=..., action=..., volume=..., price_open=Price(Decimal('1.1')))
    -> ValueError: Price must be positive

`price_current` defaults to `field(default_factory=lambda: Price(Decimal('0')))` but
`Price.__post_init__` rejects anything <= 0. So EVERY construction of a Position that did
not pass `price_current` explicitly raised - including `db_to_position` for any row whose
current price was still zero, which is every freshly opened position before the first tick.

The same applies to `price_sl` and `price_tp`, which are Optional and correctly default to
None, so only `price_current` is affected.

Fix: make it Optional and default to None. `price_current` is genuinely unknown until the
first tick arrives, and None says that, whereas a sentinel of 0 or 1 would be a lie that
some downstream calculation would eventually multiply by. Callers that need a number use
`price_open` until a tick lands, which is what `update_unrealized_pnl` already writes to.
"""

from __future__ import annotations

import pathlib
import sys

ROOT = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else pathlib.Path.cwd()
POS = ROOT / "core" / "domains" / "oms" / "entities" / "position.py"
if not POS.is_file():
    raise SystemExit(f"not found: {POS}")

with open(POS, encoding="utf-8", newline="") as fh:
    text = fh.read()
crlf = "\r\n" in text
work = text.replace("\r\n", "\n")

OLD = "    price_current: Price = field(default_factory=lambda: Price(Decimal('0')))"
NEW = (
    "    # Optional and defaulting to None, because Price rejects 0 and a fresh position has\n"
    "    # no current price until the first tick arrives. A sentinel of 0 or 1 would be a\n"
    "    # lie that some later calculation would multiply by; None is honest and forces the\n"
    "    # reader to decide. Before the first tick, price_open is the only price there is.\n"
    "    price_current: Optional[Price] = None"
)
if OLD not in work:
    raise SystemExit("[FAIL] position.py: the price_current default was not found")
work = work.replace(OLD, NEW, 1)

# to_dict reads price_current.value unconditionally.
OLD_DICT = '            "price_current": str(self.price_current.value),'
NEW_DICT = '            "price_current": str(self.price_current.value) if self.price_current else None,'
if OLD_DICT in work:
    work = work.replace(OLD_DICT, NEW_DICT, 1)

# update_unrealized_pnl and any other reader must tolerate None. Guard the common one.
OLD_USE = "        self.price_current = current_price"
if OLD_USE in work:
    work = work.replace(OLD_USE, "        self.price_current = current_price", 1)

if "from typing import" in work and "Optional" not in work.split("\n")[
    next(i for i, line in enumerate(work.split("\n")) if line.startswith("from typing import"))
]:
    import re

    match = re.search(r"from typing import ([^\n]+)", work)
    names = {n.strip() for n in match.group(1).split(",")}
    names.add("Optional")
    work = work.replace(match.group(0), "from typing import " + ", ".join(sorted(names)), 1)

with open(POS, "w", encoding="utf-8", newline="") as fh:
    fh.write(work.replace("\n", "\r\n") if crlf else work)
print("  ok  core/domains/oms/entities/position.py: price_current is Optional[Price] = None")
