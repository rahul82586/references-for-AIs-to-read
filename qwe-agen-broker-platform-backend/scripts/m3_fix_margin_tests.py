"""
Step M3 part 2 - correct the two tests that asserted the wrong margin formula.

`TestMarginCalculation` encoded the defect rather than the requirement. Both of its
tests expect margin for a Forex symbol to be computed as

    volume * contract_size * PRICE / leverage     -> 1 * 100,000 * 1.1 / 100 = 1,100

but MT5's documented Forex formula has no price term:

    volume * contract_size / leverage             -> 1 * 100,000 / 100       = 1,000

Platform-Setup.md, `Margin-Calculation/Basic`, uses this exact case:

    "let's calculate the margin requirements for buying one lot of EURUSD, while the
     size of one contract is 100,000 and the leverage is 1:100 ...
     1 * 100000 / 100 = EUR 1000"

The price-dependent formula belongs to CFD (CalcMode 2) and CFD-leverage (CalcMode 4).
Applying it to every symbol meant Forex margin was over-charged by a factor of the price:
~1.1x on EURUSD, ~150x on USDJPY, ~2000x on BTCUSD. A test asserting 1,100 for a Forex
symbol was therefore locking in a systematic over-charge, and would have failed the
moment the calculation became correct.

Both tests are rewritten to state the MT5 expectation, with the price-independence that
makes the distinction observable asserted explicitly, and a CFD case added so the
price-dependent path stays covered rather than simply deleted.
"""

from __future__ import annotations

import pathlib
import sys

ROOT = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else pathlib.Path.cwd()
REL = "tests/unit/domains/accounts/test_account_models_stress.py"
path = ROOT / REL
if not path.is_file():
    raise SystemExit(f"not found: {path}")

with open(path, encoding="utf-8", newline="") as fh:
    text = fh.read()
crlf = "\r\n" in text
work = text.replace("\r\n", "\n")

OLD = '''class TestMarginCalculation:
    """Validate margin calculation formulas & leverage caps."""

    def test_standard_retail_margin(self):
        group = Group(
            name="RetailGroup",
            margin=MarginProfile(leverage_default=100, leverage_max=500)
        )
        symbol_config = {"contract_size": Decimal("100000"), "margin_rate_initial_buy": Decimal("1.0")}
        
        # Notional: 1.0 lot * 100,000 * 1.1000 = $110,000
        # Leverage: 100
        # Expected Margin = 110,000 / 100 = 1,100
        margin = group.calculate_margin(
            symbol_config=symbol_config,
            volume=Decimal("1.0"),
            price=Decimal("1.1000")
        )
        assert margin == Decimal("1100.0000")

    def test_zero_or_negative_leverage_fallback(self):
        group = Group(
            name="ZeroLevGroup",
            margin=MarginProfile(leverage_default=0, leverage_max=0)
        )
        symbol_config = {"contract_size": Decimal("100000"), "margin_rate_initial_buy": Decimal("1.0")}
        
        # Should fallback to leverage 1.0 without dividing by zero
        margin = group.calculate_margin(
            symbol_config=symbol_config,
            volume=Decimal("1.0"),
            price=Decimal("1.1000")
        )
        assert margin == Decimal("110000.0000")'''

NEW = '''class TestMarginCalculation:
    """Margin formulas, asserted against MT5's own published examples.

    The expectations here come from Platform-Setup.md, Margin-Calculation/Basic - not
    from the implementation. An earlier version of this class expected 1,100 for one lot
    of a 100,000-contract Forex symbol at 1:100, which is the CFD formula
    (volume * contract * PRICE / leverage). MT5's Forex formula has no price term and
    its worked example for exactly these inputs says 1,000:

        "1 * 100000 / 100 = EUR 1000"

    The distinction is not academic: applying the price-dependent formula to every
    symbol over-charges Forex margin by a factor of the price, ~150x on USDJPY and
    ~2000x on BTCUSD.
    """

    def test_forex_margin_is_volume_contract_over_leverage(self):
        """MT5 Forex: volume * contract_size / leverage. No price term."""
        group = Group(
            name="RetailGroup",
            margin=MarginProfile(leverage_default=100, leverage_max=500),
        )
        symbol_config = {
            "contract_size": Decimal("100000"),
            "calc_mode": 0,  # Forex
            "margin_rate_initial_buy": Decimal("1.0"),
        }

        margin = group.calculate_margin(
            symbol_config=symbol_config, volume=Decimal("1.0"), price=Decimal("1.1000")
        )
        # 1 * 100,000 / 100 = 1,000
        assert margin == Decimal("1000")

    def test_forex_margin_is_independent_of_price(self):
        """The price term belongs to CFD modes; a Forex margin must not move with price.

        This is the assertion that distinguishes the two formulas. Under the old
        calculation a EURUSD margin changed with the EURUSD rate, and a BTCUSD margin was
        ~2000x too large.
        """
        group = Group(name="G", margin=MarginProfile(leverage_default=100, leverage_max=500))
        symbol_config = {"contract_size": Decimal("100000"), "calc_mode": 0}

        at_1_10 = group.calculate_margin(symbol_config, Decimal("1"), Decimal("1.10"))
        at_1_50 = group.calculate_margin(symbol_config, Decimal("1"), Decimal("1.50"))
        assert at_1_10 == at_1_50 == Decimal("1000")

    def test_cfd_margin_does_use_the_price(self):
        """MT5 CFD (CalcMode 2): volume * contract_size * open market price."""
        group = Group(name="G", margin=MarginProfile(leverage_default=100, leverage_max=500))
        oil = {"contract_size": Decimal("100"), "calc_mode": 2}

        # 1 lot of oil, 100 barrels, $80 -> 8,000. MT5's own example.
        assert group.calculate_margin(oil, Decimal("1"), Decimal("80")) == Decimal("8000")

    def test_cfd_leverage_margin_divides_by_leverage(self):
        """MT5 CFD-leverage (CalcMode 4) - and 245 of the 362 reference symbols use it."""
        group = Group(name="G", margin=MarginProfile(leverage_default=100, leverage_max=500))
        spec = {"contract_size": Decimal("5000"), "calc_mode": 4}

        margin = group.calculate_margin(spec, Decimal("3"), Decimal("15.433333333"))
        assert margin.quantize(Decimal("0.01")) == Decimal("2315.00")

    def test_zero_or_negative_leverage_falls_back_without_dividing_by_zero(self):
        """The `preliminary` group on the reference server carries leverage 0."""
        group = Group(
            name="ZeroLevGroup",
            margin=MarginProfile(leverage_default=0, leverage_max=0),
        )
        symbol_config = {"contract_size": Decimal("100000"), "calc_mode": 0}

        # Leverage 0 resolves to 1, so the full notional is required. That is the safe
        # direction: an account with no leverage may not open a leveraged position.
        margin = group.calculate_margin(
            symbol_config=symbol_config, volume=Decimal("1.0"), price=Decimal("1.1000")
        )
        assert margin == Decimal("100000")

    def test_leverage_default_is_capped_by_leverage_max(self):
        group = Group(
            name="CappedGroup",
            margin=MarginProfile(leverage_default=1000, leverage_max=100),
        )
        margin = group.calculate_margin(
            {"contract_size": Decimal("100000"), "calc_mode": 0},
            Decimal("1"),
            Decimal("1.1"),
        )
        # Capped at 100, not the requested 1000.
        assert margin == Decimal("1000")

    def test_explicit_leverage_overrides_the_group(self):
        """MT5 resolves leverage per account, so the caller's value must win."""
        group = Group(name="G", margin=MarginProfile(leverage_default=100, leverage_max=500))
        margin = group.calculate_margin(
            {"contract_size": Decimal("100000"), "calc_mode": 0},
            Decimal("1"),
            Decimal("1.1"),
            leverage=500,
        )
        assert margin == Decimal("200")

    def test_margin_rate_multiplies_the_result(self):
        """MT5 stage 3: 1279 * 1.15 = 1470.85."""
        group = Group(name="G", margin=MarginProfile(leverage_default=100, leverage_max=500))
        margin = group.calculate_margin(
            {
                "contract_size": Decimal("100000"),
                "calc_mode": 0,
                "margin_rate_initial_buy": Decimal("1.15"),
            },
            Decimal("1"),
            Decimal("1.2790"),
        )
        assert margin == Decimal("1150.00")

    def test_sell_uses_the_sell_rate_not_the_buy_rate(self):
        """The old implementation always took margin_rate_initial_buy."""
        group = Group(name="G", margin=MarginProfile(leverage_default=100, leverage_max=500))
        symbol_config = {
            "contract_size": Decimal("100000"),
            "calc_mode": 0,
            "margin_rate_initial_buy": Decimal("1.0"),
            "margin_rate_initial_sell": Decimal("2.0"),
        }
        buy = group.calculate_margin(symbol_config, Decimal("1"), Decimal("1.1"), operation="BUY")
        sell = group.calculate_margin(symbol_config, Decimal("1"), Decimal("1.1"), operation="SELL")
        assert buy == Decimal("1000")
        assert sell == Decimal("2000")'''

if OLD not in work:
    raise SystemExit("[FAIL] TestMarginCalculation did not match; it may already be rewritten")
work = work.replace(OLD, NEW, 1)

with open(path, "w", encoding="utf-8", newline="") as fh:
    fh.write(work.replace("\n", "\r\n") if crlf else work)
print("  ok  test_account_models_stress.py: TestMarginCalculation now asserts MT5's formulas")
print("      (the old expectations of 1,100 and 110,000 encoded the CFD-formula defect)")
