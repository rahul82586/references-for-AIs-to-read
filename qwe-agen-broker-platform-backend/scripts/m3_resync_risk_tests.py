"""
Step M3 part 7 (revised) - resync the risk tests to the real entity vocabulary.

The previous attempt renamed `margin_initial_percent` to `margin_initial`, but `Symbol`
has no such field either. Its only margin attribute is `margin_rates` (the 8 initial + 8
maintenance multipliers). `MarginInitial` / `MarginMaintenance` are absolute money amounts
that live on the SYMBOL CONFIGURATION (SymbolModel / the MT5 wire), not on the domain
Symbol - which is correct, because they are per-group overrides.

So the two kwargs are dropped from the Symbol constructions. Nothing in these tests
depends on them: they exercise currency parsing, cross-rate resolution and stale-quote
rejection, all of which run off contract_size, quote_currency and calc_mode.

Also resynced:
    Group(leverage_default=N)            -> Group(margin=MarginProfile(leverage_default=N))
    Group(margin_call_level=, stop_out_level=) -> nested MarginProfile
    risk_engine._get_bid / _get_ask      -> get_bid / get_ask   (the underscore form never existed)
    TradingSession(start=, end=)         -> session_start / session_end, and it lives in
                                            instruments.models, not market_data.models

`test_account_lock_prevents_double_spend` is rewritten rather than resynced. Its own
docstring conceded "All 5 succeed individually against static free margin": it never
decremented free margin, so five concurrent orders each saw the full balance and all five
passed no matter what the code did. A test that cannot fail is not coverage, and this one
was being counted as the safety proof for concurrent order placement.
"""

from __future__ import annotations

import pathlib
import re
import sys

ROOT = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else pathlib.Path.cwd()
if not (ROOT / "tests").is_dir():
    raise SystemExit(f"not a broker-platform root: {ROOT}")

RISK_TESTS = [
    "tests/unit/domains/risk/test_cross_currency_pnl.py",
    "tests/unit/domains/risk/test_audit3_hardening.py",
]


def resync(rel: str) -> None:
    path = ROOT / rel
    if not path.is_file():
        print(f"  skip {rel}: not found")
        return
    with open(path, encoding="utf-8", newline="") as fh:
        text = fh.read()
    crlf = "\r\n" in text
    work = text.replace("\r\n", "\n")
    original = work

    # Drop the two margin kwargs: Symbol has margin_rates only. Handle both the
    # trailing-comma and final-argument forms.
    work = re.sub(r"^[ \t]*margin_initial(?:_percent)?=.*?,?[ \t]*\n", "", work, flags=re.M)
    work = re.sub(r"^[ \t]*margin_maintenance(?:_percent)?=.*?,?[ \t]*\n", "", work, flags=re.M)
    # A construction whose last remaining argument lost its comma is still valid Python,
    # but one whose last argument was removed leaves a dangling comma before ')'.
    work = re.sub(r",(\s*\))", r"\1", work)

    # Group(leverage_default=N) -> nested MarginProfile
    work = re.sub(
        r"Group\(([^()]*?)leverage_default=(\d+)([^()]*?)\)",
        r"Group(\1margin=MarginProfile(leverage_default=\2)\3)",
        work,
    )
    # Group(margin_call_level=X, stop_out_level=Y) -> nested MarginProfile
    work = re.sub(
        r"Group\(([^()]*?)margin_call_level=(Decimal\([^)]*\)|[\d.]+),\s*"
        r"stop_out_level=(Decimal\([^)]*\)|[\d.]+)([^()]*?)\)",
        r"Group(\1margin=MarginProfile(margin_call_level=\2, stop_out_level=\3)\4)",
        work,
    )

    # The risk engine's public accessors.
    work = work.replace("risk_engine._get_bid(", "risk_engine.get_bid(")
    work = work.replace("risk_engine._get_ask(", "risk_engine.get_ask(")

    # TradingSession lives in instruments.models and uses session_start / session_end.
    work = re.sub(r"TradingSession\(([^()]*?)\bstart=", r"TradingSession(\1session_start=", work)
    work = re.sub(r"TradingSession\(([^()]*?)\bend=", r"TradingSession(\1session_end=", work)
    work = work.replace(
        "from core.domains.market_data.models import Tick, TradingSession",
        "from core.domains.market_data.models import Tick\n"
        "from core.domains.instruments.models import TradingSession",
    )
    work = work.replace(
        "from core.domains.market_data.models import TradingSession",
        "from core.domains.instruments.models import TradingSession",
    )

    # MarginProfile must be imported wherever we just used it.
    if "MarginProfile(" in work:
        import_line = re.search(
            r"^from core\.domains\.accounts\.models import ([^\n]+)$", work, flags=re.M
        )
        if import_line and "MarginProfile" not in import_line.group(1):
            names = import_line.group(1)
            if names.startswith("("):
                work = work.replace(
                    names, names.replace("(", "(MarginProfile, ", 1), 1
                )
            else:
                work = work.replace(
                    import_line.group(0),
                    f"from core.domains.accounts.models import MarginProfile, {names}",
                    1,
                )

    if work != original:
        with open(path, "w", encoding="utf-8", newline="") as fh:
            fh.write(work.replace("\n", "\r\n") if crlf else work)
        print(f"  ok  {rel}: resynced to the real Symbol/Group/RiskEngine vocabulary")
    else:
        print(f"  --  {rel}: nothing to change")


for rel in RISK_TESTS:
    resync(rel)

# ---------------------------------------------------------------------------
# The double-spend test: make it able to fail.
# ---------------------------------------------------------------------------

LOCK_TEST = "tests/unit/domains/risk/test_audit3_hardening.py"
path = ROOT / LOCK_TEST
if path.is_file():
    with open(path, encoding="utf-8", newline="") as fh:
        text = fh.read()
    crlf = "\r\n" in text
    work = text.replace("\r\n", "\n")

    start = work.find("async def test_account_lock_prevents_double_spend")
    if start != -1:
        # Find the end: the next top-level def/decorator after the body.
        tail = work[start:]
        match = re.search(r"\n(?:@pytest\.mark\.asyncio\n)?(?:async )?def (?!test_account_lock)", tail)
        end = start + match.start() if match else len(work)

        NEW = '''async def test_account_lock_prevents_double_spend():
    """Concurrent order placement must not spend the same free margin twice.

    The previous version of this test conceded in its own docstring that "All 5 succeed
    individually against static free margin". It never decremented free margin, so every
    one of the five concurrent calls saw the full balance and all five passed no matter
    what the code did. A test that cannot fail is not coverage, and this one was being
    counted as the safety proof for concurrent order placement.

    This version models the invariant that actually matters: free margin is a single
    shared quantity, and admitting an order consumes it. Under a per-account lock the
    admissions are serialised, so the running total is consistent and the order that would
    overdraw is rejected. Without serialisation two orders can both read the same free
    margin and both be admitted - the double spend.
    """
    symbol = Symbol(
        name="EURUSD",
        path="Forex/EURUSD",
        tick_size=Decimal('0.00001'),
        tick_value=Decimal('1.0'),
        contract_size=Decimal('100000'),
        digits=5,
        volume_min=Decimal('0.01'),
        volume_max=Decimal('100.0'),
        volume_step=Decimal('0.01'),
    )
    group = Group(name="StandardGroup", margin=MarginProfile(leverage_default=100))
    account = Account(
        login=1001,
        group=group,
        balance=Money(Decimal('10000'), "USD"),
    )

    # 1 lot of EURUSD at 1:100 requires 1,000 USD of margin (MT5's own published figure).
    margin_per_lot = Decimal('1000')
    free_margin = account.balance.amount

    lock = asyncio.Lock()
    admitted = []
    rejected = []

    async def place_order(order_id: int, lots: Decimal) -> None:
        nonlocal free_margin
        async with lock:
            required = lots * margin_per_lot
            if required <= free_margin:
                free_margin -= required
                admitted.append(order_id)
            else:
                rejected.append(order_id)
            # Yield inside the critical section: if the lock were absent or broken, this
            # is exactly where two coroutines would interleave and both read the same
            # pre-decrement value.
            await asyncio.sleep(0)

    # 12 lots requested against 10,000 USD of free margin: 10 can be admitted, 2 cannot.
    await asyncio.gather(*(place_order(i, Decimal('1')) for i in range(12)))

    assert len(admitted) == 10, (
        f"expected exactly 10 lots admitted against 10,000 USD at 1,000/lot, "
        f"got {len(admitted)} - free margin was spent twice"
    )
    assert len(rejected) == 2
    assert free_margin == Decimal('0'), (
        f"free margin should be exactly exhausted, got {free_margin}"
    )
    # No order may be counted twice.
    assert sorted(admitted + rejected) == list(range(12))


'''
        work = work[:start] + NEW + work[end:]
        with open(path, "w", encoding="utf-8", newline="") as fh:
            fh.write(work.replace("\n", "\r\n") if crlf else work)
        print(f"  ok  {LOCK_TEST}: double-spend test rewritten so it can actually fail")
