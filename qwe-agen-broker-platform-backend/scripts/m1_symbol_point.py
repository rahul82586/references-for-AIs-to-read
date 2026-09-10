"""
Step M1 part 7 - give Symbol a distinct MT5 TickSize, and stop default-overwriting
imported values.

MT5 has TWO price-step fields and they are not the same thing:

    Point     the price-precision step. Always populated (scale 8 on all 362 symbols
              in the reference export). This is what our domain calls tick_size, and
              what price quantisation must use.
    TickSize  the tick alignment step. Frequently ZERO or coarser, and it differs from
              Point on all 362 symbols in the reference export (every crypto has
              TickSize = 0 while Point is the real step).

The domain had one field, so TickSize was quarantined in mt5_extra and could not be
edited or queried. It now has a real field.

Also: symbol_to_db was writing the domain DEFAULT for fields the importer did not
populate - volume_limit 1000 over a server 0, stops_level 0 over a server 10,
FaceValue at scale 0 over a server "0.00". An import must never invent a value.
"""

from __future__ import annotations

import pathlib
import sys

ROOT = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else pathlib.Path.cwd()
SYM = ROOT / "core" / "domains" / "instruments" / "symbol.py"
if not SYM.is_file():
    raise SystemExit(f"not found: {SYM}")


def load(path: pathlib.Path) -> str:
    with open(path, encoding="utf-8", newline="") as fh:
        return fh.read()


def save(path: pathlib.Path, text: str, crlf: bool) -> None:
    norm = text.replace("\r\n", "\n")
    with open(path, "w", encoding="utf-8", newline="") as fh:
        fh.write(norm.replace("\n", "\r\n") if crlf else norm)


text = load(SYM)
crlf = "\r\n" in text
work = text.replace("\r\n", "\n")

OLD = """    digits: int = 5  # Decimal places (5 for forex, 2 for stocks)
    tick_size: Decimal = field(default_factory=lambda: Decimal('0.00001'))"""
NEW = """    digits: int = 5  # Decimal places (5 for forex, 2 for stocks)
    # MT5 Point: the price-precision step. Always populated. This is what price
    # quantisation must use - see the note on mt5_tick_size below.
    tick_size: Decimal = field(default_factory=lambda: Decimal('0.00001'))
    # MT5 TickSize: the tick ALIGNMENT step, and a DIFFERENT field from Point. It is
    # frequently zero (every crypto symbol in the reference export has TickSize = 0
    # while Point carries the real step) and the two differ on all 362 symbols there.
    # Kept separate so an MT5 import can round-trip and so nothing quantises to zero.
    mt5_tick_size: Decimal = field(default_factory=lambda: Decimal('0'))"""

if OLD not in work:
    raise SystemExit("[FAIL] symbol.py: tick_size declaration not found")
work = work.replace(OLD, NEW, 1)
save(SYM, work, crlf)
print("  ok  core/domains/instruments/symbol.py: added mt5_tick_size, distinct from Point")
