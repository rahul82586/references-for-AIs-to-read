"""
Step M1 part 6 - fix the liquidation fixture arithmetic and its stale commentary.

1. tests/integration/test_liquidation_worker.py
   The fixture could not have worked under any unit convention. Its own docstring says
   "Margin Level = 3000/2200 = 136% (below 50% SO)" - 136% is not below 50% - and
   claims that after closing a position carrying a $5,000 loss the account reaches
   "Equity = $8,000, Level = 727%". Closing a losing position REALISES the loss:
   equity does not go up. The source even contains a 20-line "wait, that's wrong ...
   let me recalculate" monologue that was committed instead of resolved.

   LiquidationService computes equity as balance + floating PnL, so the fixture must
   be internally consistent with that. With balance 10,200, two positions at $1,100
   margin and losses of -$4,000 / -$5,000:

       equity  = 10,200 - 9,000 = 1,200
       margin  = 2,200
       level   = 1,200 / 2,200 = 54.55%   -> below the 80% call, above the 30% SO

   To actually exercise "close the worst one and recover" the account has to start
   BELOW stop-out and finish ABOVE it, so the group uses MT5's real\\real thresholds
   scaled to this fixture: call 80%, stop-out 60%.

       start   54.55%  < 60%  -> liquidate
       close POS_002 (worst, -$5,000), freeing $1,100 of margin
       level   1,200 / 1,100 = 109.09%  >= 60%  -> recovered, stop

   Position 1 stays open. That is the scenario the test was reaching for.

"""

from __future__ import annotations

import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else pathlib.Path.cwd()
if not (ROOT / "tests" / "integration" / "test_liquidation_worker.py").is_file():
    raise SystemExit(f"not a broker-platform root: {ROOT}")


def load(rel: str) -> str:
    with open(ROOT / rel, encoding="utf-8", newline="") as fh:
        return fh.read()


def save(rel: str, text: str, crlf: bool) -> None:
    norm = text.replace("\r\n", "\n")
    with open(ROOT / rel, "w", encoding="utf-8", newline="") as fh:
        fh.write(norm.replace("\n", "\r\n") if crlf else norm)


def sub(rel: str, old: str, new: str, why: str, *, required: bool = True) -> None:
    text = load(rel)
    crlf = "\r\n" in text
    work = text.replace("\r\n", "\n")
    if old not in work:
        if required:
            raise SystemExit(f"[FAIL] {rel}: pattern not found ({why}):\n{old[:240]!r}")
        print(f"  skip {rel}: {why}")
        return
    save(rel, work.replace(old, new, 1), crlf)
    print(f"  ok  {rel}: {why}")


LIQ = "tests/integration/test_liquidation_worker.py"

# --- docstring -------------------------------------------------------------
sub(
    LIQ,
    '''    """
    Test that Liquidation Worker closes positions with worst loss first.
    
    Setup:
    - Account: $10,000 balance, 1:100 leverage, MC=80%, SO=50%
    - Position 1: 1.0 Lot BUY EURUSD at 1.1000, current price 1.0800 (loss = -$2,000)
    - Position 2: 1.0 Lot BUY GBPUSD at 1.3000, current price 1.2500 (loss = -$5,000)
    - Total PnL = -$7,000, Equity = $3,000, Margin Level = 3000/2200 = 136% (below 50% SO)
    
    Expected:
    - Worker closes Position 2 first (worst loss: -$5,000)
    - After closing Position 2: Equity = $8,000, Margin = $1,100, Level = 727% (recovered)
    - Position 1 remains open
    """''',
    '''    """
    LiquidationWorker closes the worst-loss position first, then stops once the
    account recovers above stop-out.

    Setup (all levels are PERCENT, the MT5 convention):
    - Account: balance $10,200, 1:100 leverage, margin call 80%, stop-out 60%
    - Position 1: 1.0 lot BUY EURUSD, margin $1,100, floating loss -$4,000
    - Position 2: 1.0 lot BUY GBPUSD, margin $1,100, floating loss -$5,000  <- worst

    LiquidationService computes equity as balance + floating PnL, so:
        equity = 10,200 - 9,000 = $1,200
        margin = $2,200
        level  = 1,200 / 2,200 = 54.55%   -> below the 60% stop-out, liquidate

    Closing a position REALISES its loss, so equity does not change; what changes is
    the margin requirement. Closing Position 2 frees $1,100:
        level  = 1,200 / 1,100 = 109.09%  -> above 60%, recovered, stop closing

    Expected: Position 2 closed, Position 1 still open, one closing order, one deal
    with reason SO, one PositionClosed event, account back to SOActivation.NONE.
    """''',
    "docstring arithmetic corrected (136% is not below 50%, and 727% was impossible)",
)

# --- account numbers -------------------------------------------------------
sub(
    LIQ,
    """        balance=Money(Decimal('10000.00'), "USD"),
        equity=Money(Decimal('1000.00'), "USD"),
        margin_used=Money(Decimal('2200.00'), "USD"),  # $1,100 per position
        margin_free=Money(Decimal('-1200.00'), "USD"),
        margin_level=Decimal('45.45'),  # percent: below the 80% call, above the 30% stop-out""",
    """        # balance + floating PnL must equal equity, because LiquidationService
        # recomputes equity that way: 10,200 + (-9,000) = 1,200.
        balance=Money(Decimal('10200.00'), "USD"),
        equity=Money(Decimal('1200.00'), "USD"),
        margin_used=Money(Decimal('2200.00'), "USD"),  # $1,100 per position
        margin_free=Money(Decimal('-1000.00'), "USD"),
        margin_level=Decimal('54.55'),  # percent: below the 60% stop-out""",
    "account balance/equity made consistent with balance + floating PnL",
)

# --- the StopOutEntered payload -------------------------------------------
sub(
    LIQ,
    '''            "account_login": 100001,
            "margin_level": "45.45",
            "equity": "1000.00",
            "margin": "2200.00",''',
    '''            "account_login": 100001,
            "margin_level": "54.55",
            "equity": "1200.00",
            "margin": "2200.00",''',
    "StopOutEntered payload matches the fixture",
)

# --- final assertions ------------------------------------------------------
sub(
    LIQ,
    '''    assert updated_account.margin_level > Decimal('30'), \\
        "Margin level should have recovered above the 30% stop-out"''',
    '''    assert updated_account.margin_level > Decimal('60'), \\
        "Margin level should have recovered above the 60% stop-out"''',
    "recovery assertion uses the fixture's stop-out",
)

# --- delete the committed "wait, that's wrong" monologue -------------------
text = load(LIQ)
crlf = "\r\n" in text
work = text.replace("\r\n", "\n")
start = work.find("    # After closing Position 2:\n    # - Realized PnL from Position 2")
if start != -1:
    # It runs to the end of the test function; find the next top-level def or EOF.
    end = work.find("\n\n\n", start)
    if end == -1:
        end = len(work)
    removed = work[start:end]
    work = work[:start] + work[end:]
    save(LIQ, work, crlf)
    print(f"  ok  {LIQ}: deleted {len(removed.splitlines())} lines of unresolved 'wait, that's wrong' commentary")
else:
    print(f"  skip {LIQ}: monologue not found")
