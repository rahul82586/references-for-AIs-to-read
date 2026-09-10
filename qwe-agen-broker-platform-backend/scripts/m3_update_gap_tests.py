"""
Step M3 part 9 - two M1 tests asserted a known GAP as a permanent fact.

    test_symbol_coverage_is_reported_honestly
        for known_gap in ("CurrencyProfit", "CurrencyMargin", ...):
            assert known_gap in report["missing_fields"]
    test_unmodelled_mt5_fields_survive_a_symbol_round_trip
        assert row.mt5_extra["CurrencyProfit"] == "USD"
        assert row.mt5_extra["CurrencyMargin"] == "EUR"

Both were written in M1 to prove the coverage report told the truth about what was NOT
modelled, and both picked the symbol currencies as their examples - a fair choice, since
fieldmap.py itself named CurrencyProfit and CurrencyMargin as the root cause of the
cross-currency PnL and margin bugs.

M3 has now mapped them, so the assertions are inverted by their own success. Rather than
delete them, they are rewritten to assert the stronger property: that all three currencies
ARE modelled, are NOT reported missing, and travel through real columns rather than the
quarantine. Both tests would now fail if the mapping were dropped again, which is the
regression that matters.

The round-trip test also has to pass the currencies into its `Symbol(...)` construction,
because previously it relied on them landing in the quarantine. IETimeout stays as the
genuine unmodelled field, so the test still proves the pass-through works.
"""

from __future__ import annotations

import pathlib
import sys

ROOT = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else pathlib.Path.cwd()
if not (ROOT / "tests").is_dir():
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
            raise SystemExit(f"[FAIL] {rel}: pattern not found ({why}):\n{old[:300]!r}")
        print(f"  skip {rel}: {why}")
        return
    save(rel, work.replace(old, new, 1), crlf)
    print(f"  ok  {rel}: {why}")


# ---------------------------------------------------------------------------
# 1. coverage report
# ---------------------------------------------------------------------------

sub(
    "tests/unit/infrastructure/mt5/test_wire_codec.py",
    '''    for known_gap in ("CurrencyProfit", "CurrencyMargin", "SwapRateWednesday", "IETimeout"):
        assert known_gap in report["missing_fields"]''',
    '''    # These are genuinely still unmodelled, so this keeps the report honest: it must not
    # claim coverage it does not have.
    for known_gap in ("SwapRateWednesday", "IETimeout"):
        assert known_gap in report["missing_fields"]

    # The three symbol currencies WERE gaps in M1 - fieldmap.py named CurrencyProfit and
    # CurrencyMargin as the root cause of the cross-currency PnL and margin bugs - and are
    # mapped as of M3. Asserting they are absent from missing_fields is what stops the
    # mapping being silently dropped again: without CurrencyMargin a symbol's margin
    # requirement is computed in the wrong currency, and without CurrencyProfit its PnL is
    # valued in the wrong one.
    for now_modelled in ("CurrencyBase", "CurrencyProfit", "CurrencyMargin"):
        assert now_modelled not in report["missing_fields"], (
            f"{now_modelled} must be modelled; discarding it is what made cross-currency "
            "PnL and margin uncomputable"
        )''',
    "coverage test asserts the three currencies ARE modelled; SwapRateWednesday/IETimeout remain the honest gaps",
)

# ---------------------------------------------------------------------------
# 2. round trip
# ---------------------------------------------------------------------------

sub(
    "tests/unit/persistence/test_m1_schema_and_units.py",
    '''    symbol = Symbol(
        name=domain["name"],
        path=domain.get("path", ""),
        base_currency=domain.get("base_currency", "USD"),
        tick_size=domain["tick_size"],
        contract_size=domain["contract_size"],
    )
    row = symbol_to_db(symbol, mt5_extra=quarantine, mt5_scale=scale)

    assert row.mt5_extra["CurrencyProfit"] == "USD"
    assert row.mt5_extra["CurrencyMargin"] == "EUR"
    assert row.mt5_extra["IETimeout"] == 7''',
    '''    symbol = Symbol(
        name=domain["name"],
        path=domain.get("path", ""),
        base_currency=domain.get("base_currency", ""),
        # MT5 CurrencyProfit and CurrencyMargin are modelled fields as of M3, so they are
        # passed in explicitly rather than left to land in the quarantine.
        quote_currency=domain.get("quote_currency", ""),
        margin_currency=domain.get("margin_currency", ""),
        tick_size=domain["tick_size"],
        contract_size=domain["contract_size"],
    )
    row = symbol_to_db(symbol, mt5_extra=quarantine, mt5_scale=scale)

    # The currencies travel through real columns, not the pass-through. This is the
    # assertion that would fail if the fieldmap entries were dropped again.
    assert row.base_currency == "EUR"
    assert row.quote_currency == "USD", "CurrencyProfit must land in quote_currency"
    assert row.margin_currency == "EUR", "CurrencyMargin must be its own column"
    for modelled in ("CurrencyBase", "CurrencyProfit", "CurrencyMargin"):
        assert modelled not in row.mt5_extra, f"{modelled} is modelled, not quarantined"

    # IETimeout is still genuinely unmodelled, so the pass-through must keep working.
    assert row.mt5_extra["IETimeout"] == 7''',
    "round-trip test asserts the currencies are modelled columns; IETimeout still proves the pass-through",
)

# The restored symbol must carry them back.
sub(
    "tests/unit/persistence/test_m1_schema_and_units.py",
    '''    restored = db_to_symbol(row)
    assert restored.name == "EURUSD"
    assert restored.tick_size == Decimal("0.00001000")''',
    '''    restored = db_to_symbol(row)
    assert restored.name == "EURUSD"
    assert restored.tick_size == Decimal("0.00001000")
    # The three currencies survive the full trip, which is what makes a EURJPY position on
    # a USD account computable after an import/export cycle.
    assert restored.base_currency == "EUR"
    assert restored.quote_currency == "USD"
    assert restored.margin_currency == "EUR"''',
    "restored symbol carries all three currencies back",
    required=False,
)

# The docstring still says they are unmodelled.
sub(
    "tests/unit/persistence/test_m1_schema_and_units.py",
    '''    """CurrencyProfit / CurrencyMargin / IETimeout are not modelled yet.''',
    '''    """IETimeout is not modelled; the three symbol currencies now are.''',
    "docstring corrected",
    required=False,
)
