#!/usr/bin/env python3
"""D15: the tick pipeline could resurrect a volume a close had just reduced.  Idempotent.

Found by the D12 cloud proof against Neon, on the second of two closes 0.4s apart:

    phase 1  close 0.01 of 0.02  -> OUT deal volume 0.01000000   correct
    phase 2  close the remainder -> OUT deal volume 0.02000000   the ORIGINAL size

`ClosePositionHandler` sets `close_volume = position.volume.value`, so the only way
that deal can be 0.02 is if the row read 0.02 after phase 1 had written 0.01.
`TickMarginPipeline` was writing it back: D13 made it persist the positions it had
repriced, and it persisted them with `save()` - a FULL-ROW merge of objects it had
fetched before the close landed. A tick arriving between a partial close and its
persist puts the old volume back, and the next close then trades a size the client
does not have.

D8b fixed exactly this for accounts (`update_valuation()` writes only the columns
the pipeline owns). Positions never got the equivalent. They do now, and it goes
one better than a column-scoped write: the PnL is computed IN THE STATEMENT from
the volume the row holds at write time, so a concurrent partial close cannot be
clobbered and the profit that lands is the profit of the position that is actually
there. `time_done IS NULL` keeps a tick from reopening a closed position.

Run:  python3 scripts/patch_d15_position_valuation_write.py
"""
from __future__ import annotations

import sys
from pathlib import Path

BP = Path(__file__).resolve().parent.parent
REPO = BP / "infrastructure" / "persistence" / "repositories" / "position_repository.py"
PIPE = BP / "application" / "services" / "tick_margin_pipeline.py"

# ------------------------------------------------------------------- repository

REPO_ANCHOR = """    async def get_by_account_and_symbol(self, account_login: int, symbol: str) -> List[Position]:\r
"""

REPO_METHOD = '''    async def update_valuation(self, position_id: str, price_current: Decimal,
                               profit: Decimal, when=None,
                               session: Optional[AsyncSession] = None) -> Optional[dict]:
        """D15: write a revaluation without writing the rest of the row.

        `save()` is a full-row merge, and the tick pipeline holds objects it
        fetched before it did its work. Persisting those races anything else that
        moved the position in between - observed live against Neon as a partial
        close being UNDONE by the next tick, so the following close dealt the
        position's ORIGINAL volume. D8b gave accounts a column-scoped write for
        precisely this reason; this is the position equivalent.

        Two things make it safe rather than merely narrower:

        * the PnL is computed IN THE STATEMENT from the volume and open price the
          row holds at write time, so a concurrent partial close changes the result
          instead of being overwritten by it;
        * `time_done IS NULL` means a tick can never reopen or reprice a position
          that a close, the SL/TP worker or the liquidation worker has finished.

        Returns {"volume", "profit", "price_current"} as Decimals for the row that
        was written, or None if it was closed or vanished - the caller must then
        drop the position from its view of the account rather than keep a number
        for a position that no longer exists.
        """
        from datetime import datetime as _dt, timezone as _tz

        from sqlalchemy import text as sa_text

        stmt = sa_text(
            "UPDATE positions SET "
            "price_current = CAST(:price AS DECIMAL(20,8)), "
            "profit = CAST(CASE WHEN :side = 'BUY' "
            "THEN (:price - price_open) "
            "ELSE (price_open - :price) END "
            "* volume * contract_size AS DECIMAL(20,8)), "
            "time_update = :when "
            "WHERE position_id = :position_id AND time_done IS NULL "
            "RETURNING volume, profit, price_current"
        )
        params = {
            "price": str(price_current),
            "side": str(position_id_side := "") or "BUY",  # replaced below
            "when": when or _dt.now(_tz.utc),
            "position_id": position_id,
        }
        del position_id_side
        return await self._execute_valuation(stmt, params, session)

    async def _execute_valuation(self, stmt, params, session) -> Optional[dict]:
        async def _run(sess):
            result = await sess.execute(stmt, params)
            row = result.first()
            if row is None:
                return None
            return {
                "volume": Decimal(str(row[0])),
                "profit": Decimal(str(row[1])),
                "price_current": Decimal(str(row[2])),
            }

        if session is not None:
            return await _run(session)
        async with self.session_factory() as sess:
            out = await _run(sess)
            await sess.commit()
            return out

'''

# the side has to come from the caller, not from a placeholder
REPO_METHOD = REPO_METHOD.replace(
    '''    async def update_valuation(self, position_id: str, price_current: Decimal,
                               profit: Decimal, when=None,
                               session: Optional[AsyncSession] = None) -> Optional[dict]:''',
    '''    async def update_valuation(self, position_id: str, side: str,
                               price_current: Decimal, when=None,
                               session: Optional[AsyncSession] = None) -> Optional[dict]:''')
REPO_METHOD = REPO_METHOD.replace(
    '''        params = {
            "price": str(price_current),
            "side": str(position_id_side := "") or "BUY",  # replaced below
            "when": when or _dt.now(_tz.utc),
            "position_id": position_id,
        }
        del position_id_side
        return await self._execute_valuation(stmt, params, session)''',
    '''        params = {
            "price": str(price_current),
            # normalised: the statement only ever compares against 'BUY'
            "side": "BUY" if str(side).upper().startswith("BUY") else "SELL",
            "when": when or _dt.now(_tz.utc),
            "position_id": position_id,
        }
        return await self._execute_valuation(stmt, params, session)''')
REPO_METHOD = REPO_METHOD.replace(
    '        Returns {"volume", "profit", "price_current"} as Decimals',
    '        `side` is the position\'s own action, so the statement can value a long at\n'
    '        the price it can SELL at and a short at the price it can BUY back at.\n\n'
    '        Returns {"volume", "profit", "price_current"} as Decimals')

# --------------------------------------------------------------------- pipeline

PIPE_OLD = """            price_obj = Price(current_price_decimal)\r
            position.update_unrealized_pnl(price_obj, conversion_rate)\r
            \r
        # 4b. Keep the objects step 4 just repriced.\r
"""

PIPE_NEW = """            price_obj = Price(current_price_decimal)\r
\r
            # D15: write the revaluation with a column-scoped statement instead of\r
            # a full-row save. The pipeline is holding an object it fetched before\r
            # it did any work, so `save()` races everything else that moves a\r
            # position - measured live as a partial close being undone by the next\r
            # tick, after which the following close dealt the ORIGINAL volume. The\r
            # statement computes profit from the volume the row holds at write time\r
            # and skips closed positions, and it hands back what it wrote, so the\r
            # in-memory object below carries the row's truth and not this pass's\r
            # stale snapshot.\r
            _update_valuation = getattr(self.position_repo, "update_valuation", None)\r
            if _update_valuation is not None:\r
                try:\r
                    written = await _update_valuation(\r
                        position.position_id, position.action.value, current_price_decimal)\r
                except Exception as exc:  # noqa: BLE001\r
                    logger.error(\r
                        "could not revalue position %s: %s - keeping the stored figures "\r
                        "rather than writing a guess", position.position_id, exc,\r
                    )\r
                    continue\r
                if written is None:\r
                    # closed or gone between this pass's read and its write. Dropping\r
                    # it is the point: keeping it would put a closed position's PnL\r
                    # back into its account's equity.\r
                    logger.debug(\r
                        "position %s was closed while a tick was revaluing it; skipped",\r
                        position.position_id,\r
                    )\r
                    continue\r
                position.volume = Volume(written["volume"])\r
                position.profit = Money(written["profit"], position.profit.currency)\r
                position.price_current = price_obj\r
                repriced[position.position_id] = position\r
                continue\r
\r
            position.update_unrealized_pnl(price_obj, conversion_rate)\r
            repriced[position.position_id] = position\r
            legacy_write = True\r
\r
        # 4b. What step 4 repriced, by id, for step 5 to overlay onto its own read.\r
"""

PIPE_DECL_OLD = """        # 4. Update PnL for each position\r
        for position in positions:\r
"""
PIPE_DECL_NEW = """        # 4. Update PnL for each position\r
        #\r
        # D13: these are the objects that hold the new numbers, so step 5 must use\r
        # them rather than the fresh copies its own read returns - a SQL repository\r
        # builds a new Position per fetch, so the second read came back with profit 0\r
        # and price_current NULL and the PnL computed here was silently dropped.\r
        repriced: Dict[str, Position] = {}\r
        #: set when the repository has no column-scoped write, so step 5 must persist\r
        legacy_write = False\r
        for position in positions:\r
"""

PIPE_4B_OLD = """        # no double write.\r
        repriced: Dict[str, Position] = {p.position_id: p for p in positions}\r
"""
PIPE_4B_NEW = """        # no double write. Under D15 the dict is filled as each write lands, so it\r
        # holds what the DATABASE says - which after a concurrent partial close is\r
        # not what this pass computed.\r
"""

PIPE_SAVE_OLD = """            for p in all_positions:\r
                await self.position_repo.save(p)\r
"""
PIPE_SAVE_NEW = """            if legacy_write:\r
                # No column-scoped write available (a custom or in-memory repo), so\r
                # the repriced objects have not been persisted yet. This is the racy\r
                # path - say so once rather than on every tick of every symbol.\r
                if not self._warned_full_row_save:\r
                    self._warned_full_row_save = True\r
                    logger.warning(\r
                        "position_repo %s has no update_valuation(); falling back to a "\r
                        "full-row save per tick, which can undo a concurrent close's "\r
                        "volume (D15)", type(self.position_repo).__name__,\r
                    )\r
                for p in all_positions:\r
                    await self.position_repo.save(p)\r
"""

PIPE_INIT_OLD = """        self.risk_engine = risk_engine\r
        self.event_bus = event_bus\r
"""
PIPE_INIT_NEW = """        self.risk_engine = risk_engine\r
        self.event_bus = event_bus\r
        #: D15 - whether the full-row fallback warning has already been logged\r
        self._warned_full_row_save = False\r
"""


REPO_IMPORT_OLD = "from datetime import datetime\r\n"
REPO_IMPORT_NEW = "from datetime import datetime\r\nfrom decimal import Decimal\r\n"
PIPE_IMPORT_OLD = "from core.domains.common.value_objects import Money, Price\r\n"
PIPE_IMPORT_NEW = "from core.domains.common.value_objects import Money, Price, Volume\r\n"


def patch(path: Path, old: str, new: str, label: str, *, done: str) -> bool:
    with path.open(newline="") as fh:
        text = fh.read()
    if done in text:
        print(f"  = {label}: already patched")
        return False
    if old not in text:
        print(f"  ! {label}: anchor not found - refusing to guess", file=sys.stderr)
        raise SystemExit(1)
    with path.open("w", newline="") as fh:
        fh.write(text.replace(old, new, 1))
    print(f"  + {label}")
    return True


def main() -> int:
    print(f"patching {REPO.relative_to(BP)}")
    patch(REPO, REPO_ANCHOR, REPO_METHOD + REPO_ANCHOR,
          "update_valuation() on the position repository",
          done="async def update_valuation(self, position_id: str, side: str")
    patch(REPO, REPO_IMPORT_OLD, REPO_IMPORT_NEW, "Decimal import",
          done="from decimal import Decimal")

    print(f"patching {PIPE.relative_to(BP)}")
    patch(PIPE, PIPE_IMPORT_OLD, PIPE_IMPORT_NEW, "Volume import",
          done="import Money, Price, Volume")
    patch(PIPE, PIPE_INIT_OLD, PIPE_INIT_NEW, "pipeline flag",
          done="_warned_full_row_save = False")
    patch(PIPE, PIPE_DECL_OLD, PIPE_DECL_NEW, "step 4 declaration",
          done="legacy_write = False")
    patch(PIPE, PIPE_OLD, PIPE_NEW, "step 4 atomic write",
          done="D15: write the revaluation with a column-scoped statement")
    patch(PIPE, PIPE_4B_OLD, PIPE_4B_NEW, "step 4b: stop rebuilding the dict from stale objects",
          done="holds what the DATABASE says")
    patch(PIPE, PIPE_SAVE_OLD, PIPE_SAVE_NEW, "step 5 conditional save",
          done="if legacy_write:")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
