"""
Step M3 part 13 - the last two renames.

1. `CommissionTier(..., value=Decimal("5.00"))` - the field is `rate`. The previous
   step's rewrite ran against an already-modified line and its `[^()]*` pattern stopped at
   the first nested `Decimal(` parenthesis, so the argument list was never fully scanned.

2. `Position(average_price=Price(...))` - the field is `price_open`. `average_price` is
   the name from the deleted duplicate PositionModel, and it is the same stale vocabulary
   that made RiskEngine read `.average_price` and get zero for every position's PnL. The
   tests were written against the model that no longer exists.

Both are pure renames; no expectation changes.
"""

from __future__ import annotations

import pathlib
import re
import sys

ROOT = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else pathlib.Path.cwd()
if not (ROOT / "core").is_dir():
    raise SystemExit(f"not a broker-platform root: {ROOT}")


def load(rel: str) -> str:
    with open(ROOT / rel, encoding="utf-8", newline="") as fh:
        return fh.read()


def save(rel: str, text: str, crlf: bool) -> None:
    norm = text.replace("\r\n", "\n")
    with open(ROOT / rel, "w", encoding="utf-8", newline="") as fh:
        fh.write(norm.replace("\n", "\r\n") if crlf else norm)


# ---------------------------------------------------------------------------
# 1. CommissionTier(value=) -> rate=, scanning past nested parens
# ---------------------------------------------------------------------------

REL = "tests/unit/domains/accounts/test_account_models_stress.py"
text = load(REL)
crlf = "\r\n" in text
work = text.replace("\r\n", "\n")
before = work


def _balanced_call(source: str, name: str) -> list:
    """Yield (start, end) spans of `name(...)` including nested parentheses."""
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


# Rewrite right-to-left so earlier spans stay valid.
for start, end in reversed(_balanced_call(work, "CommissionTier")):
    call = work[start:end]
    fixed = re.sub(r"\bvalue=", "rate=", call)
    work = work[:start] + fixed + work[end:]

if work != before:
    save(REL, work, crlf)
    print(f"  ok  {REL}: CommissionTier(value=) -> rate= (scanning past nested Decimal(...) parens)")
else:
    print(f"  --  {REL}: no CommissionTier(value=) left")

# ---------------------------------------------------------------------------
# 2. Position(average_price=) -> price_open=
# ---------------------------------------------------------------------------

for REL in (
    "tests/unit/domains/risk/test_cross_currency_pnl.py",
    "tests/unit/domains/risk/test_audit3_hardening.py",
):
    path = ROOT / REL
    if not path.is_file():
        continue
    text = load(REL)
    crlf = "\r\n" in text
    work = text.replace("\r\n", "\n")
    before = work

    # average_price was the deleted duplicate PositionModel's field name; the domain
    # entity uses price_open. Same stale vocabulary that made RiskEngine's PnL zero.
    work = re.sub(r"\baverage_price=", "price_open=", work)
    # opened_at is likewise not a Position field. MT5's own name is TimeCreate, which is
    # what the entity uses - keeping the wire vocabulary avoids inventing a third name for
    # the same concept (the codebase already had time_create, created_at and opened_at).
    work = re.sub(r"\bopened_at=", "time_create=", work)
    work = re.sub(r"\bclosed_at=", "time_done=", work)
    # A Position also needs `action`, not `side`, and it takes a PositionAction.
    work = re.sub(r"\bside=PositionSide\.(BUY|SELL|LONG|SHORT)\b",
                  lambda m: f"action=PositionAction.{'BUY' if m.group(1) in ('BUY','LONG') else 'SELL'}",
                  work)

    if work != before:
        save(REL, work, crlf)
        print(f"  ok  {REL}: average_price -> price_open")
    else:
        print(f"  --  {REL}: nothing to change")
