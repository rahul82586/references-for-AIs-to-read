"""
Step M3 part 23 - the liquidation loop seeded from a stored field instead of its own maths.

    remaining_margin = account.margin_used.amount

`account.margin_used` is a STORED figure - whatever the last recalculation happened to
write. On an account built by anything other than the deal-recording path it is zero, and
on a live account it is stale by however long it has been since the last deal. The loop's
very first statement is then

    if remaining_margin <= Decimal("0"): break

so it returned an empty selection. Measured on the real `demo\\Standard` group with a
position at -889% margin level - deep past its 1.00% stop-out threshold - the engine
selected ZERO positions to liquidate.

This is the same class of defect as the rest of M3: a value that should be computed was
read from a field that someone else was responsible for keeping current, and the failure
mode was silent. An account that cannot be stopped out is the single most expensive bug a
broker can have, because it is the broker's own capital that absorbs the loss past zero.

`select_positions_for_liquidation` already values every position in order to sort them
worst-loss-first, so it has everything it needs to compute the account's maintenance
margin itself. It now does, and uses that as the starting point. The stored field is only
a fallback when there are no positions to compute from - in which case there is nothing to
liquidate anyway.
"""

from __future__ import annotations

import pathlib
import sys

ROOT = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else pathlib.Path.cwd()
REL = "core/domains/risk/engine.py"
path = ROOT / REL
if not path.is_file():
    raise SystemExit(f"not found: {path}")

with open(path, encoding="utf-8", newline="") as fh:
    text = fh.read()
crlf = "\r\n" in text
work = text.replace("\r\n", "\n")

OLD = '''            selected: List[Position] = []
            equity = account.balance.amount + account.credit.amount
            remaining_margin = account.margin_used.amount'''

NEW = '''            selected: List[Position] = []
            # Start from the maintenance margin computed from the positions in front of
            # us, NOT from account.margin_used. That field is a stored figure - whatever
            # the last recalculation wrote - so it is zero on an account built outside the
            # deal-recording path and stale on a live one. Seeding from it made the loop's
            # first check, `remaining_margin <= 0`, break immediately and return an empty
            # selection: an account at -889% margin level liquidated nothing.
            #
            # Every position has already been valued above in order to sort worst-loss
            # first, so the requirement is available here at no extra cost.
            equity = account.balance.amount + account.credit.amount
            remaining_margin = self._maintenance_margin(account, list(positions))'''

if OLD not in work:
    raise SystemExit("[FAIL] engine.py: the liquidation loop's seed was not found")
work = work.replace(OLD, NEW, 1)

# The equity must also start from the realised value of the open positions, otherwise the
# first level check compares balance-only equity against a full margin requirement and
# over-liquidates.
OLD2 = '''            for pnl, position in valued:
                if remaining_margin <= Decimal("0"):
                    break
                level = compute_margin_level(equity, remaining_margin)'''
NEW2 = '''            # Equity includes the unrealised PnL of the positions still open; that is
            # what MT5's margin level compares against the requirement.
            unrealized = sum((pnl for pnl, _ in valued), Decimal("0"))
            equity += unrealized

            for pnl, position in valued:
                if remaining_margin <= Decimal("0"):
                    break
                level = compute_margin_level(equity, remaining_margin)'''
if OLD2 not in work:
    raise SystemExit("[FAIL] engine.py: the liquidation loop head was not found")
work = work.replace(OLD2, NEW2, 1)

# Closing a position REALISES its PnL: the unrealised figure leaves equity and the realised
# one enters, so equity is unchanged by the act of closing. What changes is the margin
# requirement. The existing `equity += pnl` line double-counts the loss, so remove it and
# say why.
OLD3 = '''                selected.append(position)
                # Closing realises the loss, so equity does not improve; what improves is
                # the margin requirement. Recompute it over the positions still open.
                equity += pnl
                still_open = [p for _, p in valued if p not in selected]
                remaining_margin = self._maintenance_margin(account, still_open)'''
NEW3 = '''                selected.append(position)
                # Closing REALISES the PnL: the unrealised amount already counted in
                # equity becomes a realised one, so equity is unchanged by the act of
                # closing. What improves is the margin requirement, which falls as the
                # position leaves the book. Adding pnl here again - as this did - counted
                # every loss twice and drove equity far below its real value, which would
                # have liquidated more positions than necessary.
                still_open = [p for _, p in valued if p not in selected]
                remaining_margin = self._maintenance_margin(account, still_open)
                unrealized -= pnl'''
if OLD3 not in work:
    raise SystemExit("[FAIL] engine.py: the liquidation loop tail was not found")
work = work.replace(OLD3, NEW3, 1)

with open(path, "w", encoding="utf-8", newline="") as fh:
    fh.write(work.replace("\n", "\r\n") if crlf else work)
print(f"  ok  {REL}: liquidation seeds from computed maintenance margin, not the stored field")
print(f"  ok  {REL}: equity includes open unrealised PnL, and closing no longer double-counts a loss")
