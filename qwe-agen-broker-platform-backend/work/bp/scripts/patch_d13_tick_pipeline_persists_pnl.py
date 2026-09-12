#!/usr/bin/env python3
"""D13: the tick pipeline computed position PnL and then threw it away.  Idempotent.

`TickMarginPipeline.process_tick()` repriced the positions it fetched in step 4,
then in step 5 fetched the account's positions AGAIN and summed/saved those. A SQL
repository builds a new `Position` per fetch (`db_to_position(model)`), so the
second read came straight from the database with `profit` 0 and `price_current`
NULL - the step-4 objects were never saved by anyone.

Live against Neon with a real MT5 feed (`scripts/probe_position_repricing.py`):

    row price_current=None profit=0E-8 | account equity=100000.0000
    /account/positions unrealized_pnl=-0.5116        <- on-demand, correct

Three consequences: a market close has no price and falls back to `price_open`
(booking zero PnL - this is what the D12 cloud proof tripped over), account equity
is written as balance so it never reflects open PnL, and `evaluate_margin_state()`
sees a flat equity, which makes the margin-call / stop-out machine unreachable from
ticks.

Every existing test missed it because `MockPositionRepository` returns the SAME
objects from both fetches. `tests/integration/test_d13_tick_pipeline_persists_pnl.py`
adds a copy-on-read double that behaves like the database; all four of its tests
fail against the unfixed pipeline.

Run:  python3 scripts/patch_d13_tick_pipeline_persists_pnl.py
"""
from __future__ import annotations

import sys
from pathlib import Path

BP = Path(__file__).resolve().parent.parent
TARGET = BP / "application" / "services" / "tick_margin_pipeline.py"

OLD = """        # 5. Update Account Equity and Evaluate Margin State\r
        for login, account in accounts.items():\r
            # Get ALL positions for this account (not just the current symbol)\r
            all_positions = await self.position_repo.get_by_account(login)\r
            \r
            # Calculate total unrealized PnL in account currency\r
"""

NEW = """        # 4b. Keep the objects step 4 just repriced.\r
        #\r
        # D13: step 5 fetches this account's positions AGAIN, and a SQL repository\r
        # builds a NEW Position per fetch (db_to_position(model)), so that second\r
        # read came back with the values still in the database - profit 0,\r
        # price_current NULL. Equity was summed from those, they were what got\r
        # saved, and the PnL step 4 had just computed was dropped on the floor.\r
        # Every test missed it because the mock repository handed back the SAME\r
        # objects from both fetches; the double was more coherent than the database.\r
        #\r
        # The overlay is what makes the two reads agree: positions of THIS symbol\r
        # come from the repriced objects, every other symbol comes from the fresh\r
        # read (and keeps the PnL its own last tick gave it). One fetch, one save,\r
        # no double write.\r
        repriced: Dict[str, Position] = {p.position_id: p for p in positions}\r
\r
        # 5. Update Account Equity and Evaluate Margin State\r
        for login, account in accounts.items():\r
            # Get ALL positions for this account (not just the current symbol),\r
            # then replace the ones this tick repriced with the objects that hold\r
            # the new numbers.\r
            fetched = await self.position_repo.get_by_account(login)\r
            seen = {x.position_id for x in fetched}\r
            all_positions = [repriced.get(x.position_id, x) for x in fetched]\r
            # A position this tick repriced that the account read did not return\r
            # (it closed between the two fetches) is not resurrected: it is no\r
            # longer part of this account's open exposure.\r
            all_positions.extend(\r
                p for pid, p in repriced.items()\r
                if p.account_login == login and pid not in seen and p.time_done is None\r
            )\r
\r
            # Calculate total unrealized PnL in account currency\r
"""


def main() -> int:
    # newline="" : the file is CRLF, and universal-newline reading would turn every
    # \r\n into \n so the anchor above could never match.
    with TARGET.open(newline="") as fh:
        text = fh.read()
    if "D13: step 5 fetches this account's positions AGAIN" in text:
        print("  = already patched")
        return 0
    if OLD not in text:
        print("  ! anchor not found - refusing to guess", file=sys.stderr)
        return 1
    with TARGET.open("w", newline="") as fh:
        fh.write(text.replace(OLD, NEW, 1))
    print(f"  + {TARGET.relative_to(BP)}: step 5 now sums and saves the repriced positions")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
