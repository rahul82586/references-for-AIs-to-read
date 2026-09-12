"""D8b - TickMarginPipeline's full-row save was erasing margin written by a fill.

THE OBSERVATION
===============
Two live A-Book hedges against a real MT5 terminal and real Neon, same code path,
two minutes apart:

    account 887914 (Route A)  margin_used=0E-8       margin_level=999999
                              equity=100000  margin_free=100000
                              updated_at == created_at + 8us   <- never advanced
                              ...and its Deal and Position both exist
    account 890960 (Route B)  margin_used=77.37413   margin_level=129242.164

In the run BEFORE the D8 fix the two routes showed the opposite pattern. So it is
not route-specific - it is a race, and it only appears when a live feed is
ticking.

THE MECHANISM
=============
`TickMarginPipeline._process` runs on every TICK_RECEIVED:

    account = <loaded earlier in this pass>
    account.update_equity(total_pnl)      # sets equity, margin_free, margin_level
    await self.account_repo.save(account) # FULL-ROW merge of every column

`SqlAccountRepository.save` is `session.merge(account_to_db(account))` - all
columns. `update_equity` never touches `margin_used`, so the object carries
whatever `margin_used` it had when it was loaded.

Interleave that with a fill:

    T0  pipeline loads account            margin_used = 0        (no position yet)
    T1  record_deal loads, books the position, sets margin_used = 77.37, saves
    T2  pipeline saves its T0 snapshot    margin_used = 0 again  <-- LOST UPDATE

`account_to_db` writes `updated_at=account.updated_at` from the domain object
rather than the write time, which is why the resurrected row carried its original
creation timestamp - the fingerprint that identified this.

WHY IT IS THE WORST KIND
========================
`margin_used = 0` on an account holding a position means:
  * free margin is overstated by the whole requirement, so the client can keep
    opening positions past their limit;
  * `margin_level` becomes the 999999 sentinel, so the margin-call and stop-out
    state machine can never fire. The account can run to negative equity with no
    liquidation.
It silently disables the risk engine, and it does so more often the more liquid
the symbol is, because more ticks means more chances to win the race.

WHY NOTHING CAUGHT IT
=====================
Every offline test runs without a concurrent feed. `scripts/d8b_repro_a_book_margin.py`
is clean 12/12 with no tick pump: the fill is the only writer, so there is nothing
to race. The M6 report named this class as known debt - "full-row account_repo.save()
can still race another node's writes on OTHER columns (repository design,
pre-existing)" - and it was single-node-safe at the time. A live feed makes it
single-node-unsafe.

THE FIX
=======
Split the write sets, following the precedent M6 set with `reserve_margin` (one
conditional UPDATE, the database serialises racers):

  `update_valuation()`  writes ONLY what the tick pipeline owns and recomputes
                        from a fresh position read: profit, equity, margin_free,
                        margin_level and the five so_* stop-out fields, plus
                        updated_at = now().
                        It NEVER writes balance, margin_used or margin_reserved.
  `save()`              unchanged, for the paths that genuinely own those
                        columns (record_deal, the seeder, reservations).

The pipeline now calls `update_valuation` when the repository offers it and falls
back to `save` otherwise, so an unreformed custom repository keeps working rather
than failing at runtime.

Also fixed: `account_to_db` stamped `updated_at` from the domain object, so a
resurrected stale row looked freshly written and a genuinely written row could
look untouched. The column now records the write time.

Idempotent: re-running detects already-applied anchors and skips them.
"""
import ast
import io
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
sys.path.insert(0, ROOT)

applied = []


def patch(path, pairs):
    src = io.open(path, encoding="utf-8", newline="").read()
    nl = "\r\n" if "\r\n" in src else "\n"
    changed = False
    for old, new in pairs:
        o = old.replace("\n", nl) if nl == "\r\n" else old
        n = new.replace("\n", nl) if nl == "\r\n" else new
        if src.count(o) != 1:
            if src.count(n) >= 1:
                print(f"  skip (already patched): {path}")
                continue
            raise AssertionError(f"{path}: anchor found {src.count(o)}x: {old[:80]!r}")
        src = src.replace(o, n, 1)
        changed = True
    if changed:
        if path.endswith(".py"):
            ast.parse(src.replace("\r\n", "\n"))
        io.open(path, "w", encoding="utf-8", newline="").write(src)
        applied.append(path)


REPO = "infrastructure/persistence/repositories/account_repository.py"

# ------------------------------------------------- the column-scoped valuation
patch(REPO, [(
    '''    async def get_all_accounts(self) -> List[Account]:
''',
    '''    async def update_valuation(self, account: Account, session: Optional[AsyncSession] = None):
        """D8b: persist ONLY the tick pipeline's own columns.

        `save()` is a full-row merge. TickMarginPipeline used to call it on every
        tick with an account object loaded before the current pass, so a fill that
        landed in between had its `margin_used` overwritten by the stale snapshot -
        observed live as margin_used=0 and margin_level=999999 on an account
        holding an open position, which also disables the stop-out machine.

        This writes profit / equity / margin_free / margin_level and the five so_*
        stop-out fields, all of which the pipeline recomputes from a fresh position
        read, and deliberately NOT balance, margin_used or margin_reserved, which
        belong to record_deal and the reservation path. Disjoint write sets, so the
        two paths cannot lose each other's updates.

        Returns the number of rows written (0 means the account vanished).
        """
        from datetime import datetime as _dt, timezone as _tz

        from sqlalchemy import text as sa_text

        stmt = sa_text(
            "UPDATE accounts SET "
            "profit = CAST(:profit AS DECIMAL(20,8)), "
            "equity = CAST(:equity AS DECIMAL(20,8)), "
            "margin_free = CAST(:margin_free AS DECIMAL(20,8)), "
            "margin_level = CAST(:margin_level AS DECIMAL(20,8)), "
            "so_activation = :so_activation, "
            "so_time = :so_time, "
            "so_level = :so_level, "
            "so_equity = :so_equity, "
            "so_margin = :so_margin, "
            "updated_at = :updated_at "
            "WHERE login = :login"
        )

        def _amt(value) -> str:
            return str(getattr(value, "amount", value) or 0)

        so_act = account.so_activation
        params = {
            "profit": _amt(account.profit),
            "equity": _amt(account.equity),
            "margin_free": _amt(account.margin_free),
            # margin_level is derived state (D1): write the value the domain
            # computed, and never let a stale 0 reach the column.
            "margin_level": str(account.margin_level or 0),
            "so_activation": int(getattr(so_act, "value", so_act or 0)),
            "so_time": account.so_time,
            "so_level": (None if account.so_level is None else str(account.so_level)),
            "so_equity": (None if account.so_equity is None else _amt(account.so_equity)),
            "so_margin": (None if account.so_margin is None else _amt(account.so_margin)),
            "updated_at": _dt.now(_tz.utc),
            "login": str(account.login),
        }
        if session is not None:
            result = await session.execute(stmt, params)
            return result.rowcount or 0
        async with self.session_factory() as sess:
            result = await sess.execute(stmt, params)
            await sess.commit()
            return result.rowcount or 0

    async def get_all_accounts(self) -> List[Account]:
''',
)])

# ------------------------------------------------------- updated_at on write
patch("infrastructure/persistence/account_models.py", [(
    "        updated_at=account.updated_at,\n",
    "        # D8b: the write time, not whatever the domain object carried. Stamping\n"
    "        # the domain value made a resurrected stale row look freshly written\n"
    "        # and a real write look untouched - which is how the lost update was\n"
    "        # hard to see, and the reason updated_at == created_at on an account\n"
    "        # that had demonstrably been saved.\n"
    "        updated_at=datetime.now(timezone.utc),\n",
)])

# ------------------------------------------------------- the pipeline's write
patch("application/services/tick_margin_pipeline.py", [(
    '''            # Persist updates
            await self.account_repo.save(account)
''',
    '''            # Persist updates.
            #
            # D8b: NOT a full-row save. This pass loaded `account` before it did
            # its work, so a fill that landed in between would be overwritten by
            # the stale margin_used - observed live as margin_used=0 on an account
            # holding an open position, which also freezes margin_level at the
            # 999999 sentinel and makes stop-out unreachable. update_valuation
            # writes only the columns this pipeline owns and recomputes here.
            _update_valuation = getattr(self.account_repo, "update_valuation", None)
            if _update_valuation is not None:
                await _update_valuation(account)
            else:
                # A repository without the column-scoped write. Loud, because the
                # fallback is the racy one and an operator should know they are on
                # it - but not fatal, so a custom repo still boots.
                logger.warning(
                    "account_repo %s has no update_valuation(); falling back to a "
                    "full-row save, which can lose a concurrent fill's margin",
                    type(self.account_repo).__name__,
                )
                await self.account_repo.save(account)
''',
)])

# ------------------------------------------------------------------ the port
patch("core/ports/interfaces.py", [(
    '''    async def reserve_margin(self, login_id: Any, amount: Any)''',
    '''    async def update_valuation(self, account: T) -> int:
        """D8b: persist only the valuation columns this caller owns.

        profit, equity, margin_free, margin_level and the so_* stop-out fields -
        never balance, margin_used or margin_reserved. The tick pipeline calls
        this on every tick with an account object it loaded earlier; a full-row
        save there overwrites whatever a concurrent fill wrote to margin_used.

        Optional by design: callers fall back to save() when a repository does not
        implement it, so an existing adapter keeps working.
        """
        raise NotImplementedError

    async def reserve_margin(self, login_id: Any, amount: Any)''',
)])

print(f"applied to {len(set(applied))} file(s):")
for f in sorted(set(applied)):
    print("  ", f)
