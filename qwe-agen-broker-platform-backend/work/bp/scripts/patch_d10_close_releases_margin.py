"""D10 - closing a position never released its margin, and equity ignored unrealised PnL.

FOUND HOW
=========
The user asked why they only ever see IN deals and no OUT deals. Checking Neon:

    deals by entry : entry='IN' 31 deal(s)      <- and nothing else
    positions      : OPEN 31, CLOSED 0
    orders         : FILLED 31, REJECTED 4
    deal_close set : 0

So no position has EVER been closed in that database. That is the honest answer to
the question asked, and it is not a bug: there is no client-facing endpoint that
closes a position. `DELETE /api/v1/trade/orders/{ticket_id}` is a stub that returns
`{"status": "cancelled"}` without touching anything, and the only real close path is
the manager endpoint `POST /api/v1/manager/OrderClose`.

Driving that real path in a harness then exposed two genuine defects, both visible
in one line of output:

    CLOSED: deals=2 entries=['IN','OUT']  positions_open=[]
       IN   BUY  vol=0.10 px=1.10010 profit=0        reason=CLIENT
       OUT  SELL vol=0.10 px=1.10100 profit=9.00000  reason=CLIENT
       balance 10000 -> 10009.00   margin_used=110.01000000   <-- still held

THE DEFECTS
===========
1. `margin_used` stayed at 110.01 after the position was closed and gone. Step 9 of
   `ClosePositionHandler.handle` updates balance and equity and saves - it never
   recomputes margin. `RecordDealHandler._recalculate_account_margin` is the only
   place that walks the open positions, and a close does not go through it.

   Consequence: every closed position leaves its margin requirement behind forever.
   Free margin only ever shrinks, so an account that trades and closes repeatedly
   eventually cannot open anything - while holding nothing. `margin_level` falls
   with it, so the account drifts toward a stop-out that liquidates positions it
   does not have. On a live book this is a slow leak that ends in a client being
   unable to trade, and it is invisible until then.

2. `equity = balance + account.profit` reads the account's OWN stale `profit`
   field, which is only refreshed by the tick pipeline. Right after a close the
   correct equity is `balance + the unrealised PnL of whatever is still open` -
   and with one position just closed and none left, that is `balance + 0`. Using
   the stored `profit` instead carries the closed position's last floating PnL
   into equity permanently, so a close both realises the result into balance AND
   leaves its unrealised shadow in equity. Double-counted, in the direction that
   flatters the account.

THE FIX
=======
Close now recomputes margin and equity from the positions that are ACTUALLY still
open, through the same MT5-accurate engine the fill path uses - one source of
truth, not a fourth local formula. Where a risk engine is wired it computes the
snapshot; where it is not (a single-currency setup, a test double) it falls back to
releasing the closed leg's requirement proportionally, and says so, because a
silent fallback that gets margin wrong is how this class of bug survives.

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
        ast.parse(src.replace("\r\n", "\n"))
        io.open(path, "w", encoding="utf-8", newline="").write(src)
        applied.append(path)


CP = "application/commands/close_position.py"

patch(CP, [
    (
        "from typing import Optional\n",
        "from typing import Any, Optional\n",
    ),
    (
'''        # 9. Update account balance with realized PnL
        account = account_for_pnl
        if account:
            account.balance = Money(account.balance.amount + realized_pnl, account.currency)
            account.equity = Money(account.balance.amount + account.profit.amount, account.currency)
            await self.account_repo.save(account)
''',
'''        # 9. Update account balance with realized PnL, then RECOMPUTE margin.
        #
        # D10: this step used to set balance and equity and save - it never
        # touched margin. RecordDealHandler._recalculate_account_margin is the
        # only code that walks the open positions, and a close does not go through
        # it, so every closed position left its margin requirement behind forever.
        # Free margin only ever shrank: an account that traded and closed
        # repeatedly eventually could not open anything while holding nothing, and
        # its falling margin_level drifted toward a stop-out that would liquidate
        # positions it did not have.
        #
        # Equity was also wrong: `balance + account.profit` reads the account's own
        # stale profit field, which only the tick pipeline refreshes. That carries
        # the CLOSED position's last floating PnL into equity permanently, so a
        # close realised the result into balance AND left its unrealised shadow in
        # equity - double-counted, in the direction that flatters the account.
        account = account_for_pnl
        if account:
            account.balance = Money(account.balance.amount + realized_pnl, account.currency)
            await self._revalue_after_close(account, position)
            await self.account_repo.save(account)
''',
)])

# the recompute helper
patch(CP, [(
'''    async def handle(self, command: ClosePositionCommand) -> Position:''',
'''    async def _revalue_after_close(self, account: Any, closed_position: Any) -> None:
        """Recompute equity and margin from the positions that are STILL open. D10.

        One source of truth: the same MT5-accurate engine the fill path uses, over
        the same open-position walk. A fourth local formula here is how the three
        previous margin implementations diverged in the first place (see the header
        of core/domains/market_data/margin.py).

        Without a risk engine - a single-currency setup, or a test double - this
        falls back to subtracting the closed leg's own requirement, and logs that
        it did. A silent fallback that gets margin wrong is how this class of bug
        survives; the fallback is better than leaving the hold in place, but an
        operator should know which one ran.
        """
        currency = account.currency

        open_positions = []
        getter = getattr(self.position_repo, "get_by_account", None) or \\
            getattr(self.position_repo, "get_positions_by_account", None)
        if getter is not None:
            try:
                rows = await getter(account.login)
                open_positions = [
                    p for p in (rows or [])
                    if getattr(p, "time_done", None) is None
                    and getattr(getattr(p, "volume", None), "value", None)
                    and getattr(p, "volume").value > 0
                    and getattr(p, "position_id", None) != getattr(closed_position, "position_id", None)
                ]
            except Exception as exc:  # noqa: BLE001
                logger.error(
                    "could not list open positions for account %s after a close: %s - "
                    "margin will be estimated from the closed leg alone", account.login, exc,
                )

        # --- equity: balance + credit + the unrealised PnL of what is STILL open.
        unrealized = Decimal("0")
        if self.risk_engine is not None and open_positions:
            for p in open_positions:
                try:
                    unrealized += self.risk_engine.calculate_position_pnl(account, p)
                except Exception as exc:  # noqa: BLE001
                    logger.warning(
                        "cannot value still-open position %s after a close: %s - equity "
                        "excludes it", getattr(p, "position_id", "?"), exc,
                    )
        account.profit = Money(unrealized, currency)
        account.equity = Money(
            account.balance.amount + account.credit.amount + unrealized, currency)

        # --- margin: recomputed over the still-open positions only.
        if self.risk_engine is not None:
            try:
                snapshot = self.risk_engine.calculate_margin_level(account, open_positions)
                account.margin_used = Money(snapshot.margin_used, currency)
                account.margin_free = Money(
                    max(Decimal("0"), account.equity.amount - snapshot.margin_used), currency)
                account.recompute_margin_level()
                return
            except Exception as exc:  # noqa: BLE001
                logger.error(
                    "margin recompute failed for account %s after a close: %s - falling "
                    "back to subtracting the closed leg, which is approximate",
                    account.login, exc,
                )

        # Fallback: no engine, or the engine failed. Release the closed leg's own
        # requirement rather than leaving it held forever.
        logger.warning(
            "account %s was closed without a risk-engine margin recompute; releasing "
            "the closed leg's requirement approximately. Wire a risk_engine into "
            "ClosePositionHandler for exact figures.", account.login,
        )
        released = self._closed_leg_margin(account, closed_position)
        account.margin_used = Money(
            max(Decimal("0"), account.margin_used.amount - released), currency)
        account.margin_free = Money(
            max(Decimal("0"), account.equity.amount - account.margin_used.amount), currency)
        account.recompute_margin_level()

    @staticmethod
    def _closed_leg_margin(account: Any, position: Any) -> Decimal:
        """The closed leg's margin requirement, for the no-engine fallback.

        Deliberately simple and deliberately conservative: notional / leverage in
        the position's own currency, with no conversion. It is a fallback that must
        never make free margin WORSE than leaving the hold in place, and it is
        labelled approximate wherever it runs.
        """
        try:
            volume = Decimal(str(getattr(getattr(position, "volume", None), "value", 0)))
            price = Decimal(str(getattr(getattr(position, "price_open", None), "value", 0)))
            contract = Decimal(str(getattr(position, "contract_size", 0) or 0))
            if contract <= 0:
                contract = Decimal("1")
            leverage = Decimal(str(account.effective_leverage() or 100))
            if volume <= 0 or price <= 0 or leverage <= 0:
                return Decimal("0")
            return (volume * contract * price) / leverage
        except (ArithmeticError, ValueError, TypeError, AttributeError):
            return Decimal("0")

    async def handle(self, command: ClosePositionCommand) -> Position:''',
)])

print(f"applied to {len(set(applied))} file(s):")
for f in sorted(set(applied)):
    print("  ", f)
