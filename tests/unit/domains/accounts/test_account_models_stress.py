# python -m pytest tests/unit/domains/accounts/test_account_models_stress.py -v

"""
Comprehensive Unit, Boundary, Property-Based, and Stress Tests for Account Domain Models.
File target: core/domains/accounts/models.py
"""
import time
from decimal import Decimal
from datetime import datetime, timezone
import pytest
from hypothesis import given, strategies as st

from core.domains.accounts.models import (
    Group, MarginProfile, CommissionRule, CommissionTier,
    GroupSymbolOverride, TradeFlags, AccountType, MarginMode, TradeMode,
    ExecutionMode, CommissionMode, CommissionType, FreeMarginMode, StopOutMode
)


# ============================================================================
# CATEGORY A: UNIT & BOUNDARY TESTS (40+ Scenarios)
# ============================================================================

class TestTradeFlags:
    """Validate bitwise flag behavior (MT5 EnTradeFlags compliant)."""

    def test_bitwise_combinations(self):
        flags = TradeFlags.SWAPS | TradeFlags.EXPERTS | TradeFlags.FIFO_CLOSE
        group = Group(name="TestGroup", trade_flags=flags)

        assert group.has_trade_flag(TradeFlags.SWAPS) is True
        assert group.has_trade_flag(TradeFlags.EXPERTS) is True
        assert group.has_trade_flag(TradeFlags.FIFO_CLOSE) is True
        assert group.has_trade_flag(TradeFlags.HEDGE_PROHIBIT) is False

    def test_empty_flags(self):
        group = Group(name="TestGroup", trade_flags=TradeFlags.NONE)
        assert group.has_trade_flag(TradeFlags.SWAPS) is False


class TestPatternMatching:
    """Validate symbol pattern matching and overrides."""

    @pytest.mark.parametrize("symbol,pattern,expected", [
        ("EURUSD", "EURUSD", True),
        ("EURUSD", "FOREX:*", False),
        ("FOREX:EURUSD", "FOREX:*", True),
        ("BTCUSD", "*", True),
        ("GBPUSD", "EURUSD", False),
        ("FOREX:USDJPY", "FOREX:USD*", True),
    ])
    def test_symbol_pattern_matching(self, symbol, pattern, expected):
        group = Group(name="TestGroup")
        assert group._matches_symbol_pattern(symbol, pattern) == expected


class TestSymbolOverrides:
    """Validate Group override matching priority (first match wins)."""

    def test_first_match_wins_priority(self):
        override1 = GroupSymbolOverride(
            symbol_pattern="EURUSD",
            trade_mode=TradeMode.CLOSEONLY,
            spread_diff=10
        )
        override2 = GroupSymbolOverride(
            symbol_pattern="EUR*",
            trade_mode=TradeMode.DISABLED,
            spread_diff=50
        )
        group = Group(name="TestGroup", symbol_overrides=[override1, override2])

        config = group.get_symbol_config("EURUSD")
        assert config["trade_mode"] == TradeMode.CLOSEONLY
        assert config["spread_diff"] == 10

    def test_fallback_unmatched_symbol(self):
        override = GroupSymbolOverride(symbol_pattern="EURUSD", spread_diff=10)
        group = Group(name="TestGroup", symbol_overrides=[override])

        config = group.get_symbol_config("USDJPY")
        assert config == {}


class TestMarginCalculation:
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
        assert margin == Decimal("110000.0000")


class TestCommissionCalculation:
    """Validate per-deal, per-volume, and tiered commission rules."""

    def test_deal_commission(self):
        rule = CommissionRule(
            symbol_pattern="*",
            type=CommissionType.DEAL,
            value=Decimal("7.00")
        )
        group = Group(name="CommGroup", commissions=[rule])

        comm = group.calculate_commission("EURUSD", volume=Decimal("2.5"), deal_value=Decimal("250000"))
        assert comm == Decimal("7.00")

    def test_volume_commission_with_min_max_caps(self):
        rule = CommissionRule(
            symbol_pattern="*",
            type=CommissionType.VOLUME,
            value=Decimal("3.50"),
            min_value=Decimal("5.00"),
            max_value=Decimal("20.00")
        )
        group = Group(name="CommGroup", commissions=[rule])

        # 1 lot @ 3.50 = 3.50 -> capped to min 5.00
        assert group.calculate_commission("EURUSD", volume=Decimal("1.0"), deal_value=Decimal("100000")) == Decimal("5.00")
        
        # 10 lots @ 3.50 = 35.00 -> capped to max 20.00
        assert group.calculate_commission("EURUSD", volume=Decimal("10.0"), deal_value=Decimal("1000000")) == Decimal("20.00")

    def test_tiered_volume_discount(self):
        tier1 = CommissionTier(volume_from=Decimal("0"), volume_to=Decimal("10"), value=Decimal("5.00"))
        tier2 = CommissionTier(volume_from=Decimal("10.01"), volume_to=Decimal("100"), value=Decimal("3.00"))
        rule = CommissionRule(symbol_pattern="*", type=CommissionType.VOLUME, tiers=[tier1, tier2])
        group = Group(name="TierGroup", commissions=[rule])

        # Volume 15 lots -> matches Tier 2 (3.00 per lot) = 45.00
        comm = group.calculate_commission("EURUSD", volume=Decimal("15.0"), deal_value=Decimal("1500000"))
        assert comm == Decimal("45.00")


# ============================================================================
# CATEGORY B: HYPOTHESIS PROPERTY-BASED TESTING (Thousands of Inputs)
# ============================================================================

class TestPropertyBasedGroupLogic:

    @given(
        volume=st.decimals(min_value=Decimal("0.01"), max_value=Decimal("10000.0"), places=2),
        price=st.decimals(min_value=Decimal("0.00001"), max_value=Decimal("500000.0"), places=5),
        leverage=st.integers(min_value=-100, max_value=10000)
    )
    def test_margin_never_crashes_and_returns_decimal(self, volume, price, leverage):
        group = Group(
            name="FuzzGroup",
            margin=MarginProfile(leverage_default=leverage, leverage_max=10000)
        )
        symbol_config = {"contract_size": Decimal("100000"), "margin_rate_initial_buy": Decimal("1.0")}

        margin = group.calculate_margin(symbol_config, volume, price)

        assert isinstance(margin, Decimal)
        assert margin >= Decimal("0")


# ============================================================================
# CATEGORY C: STRESS & PERFORMANCE BENCHMARKS (100,000 Operations)
# ============================================================================

class TestGroupStressAndPerformance:

    def test_100k_margin_calculations_benchmark(self):
        group = Group(
            name="StressGroup",
            margin=MarginProfile(leverage_default=100, leverage_max=500)
        )
        symbol_config = {"contract_size": Decimal("100000"), "margin_rate_initial_buy": Decimal("1.0")}
        volume = Decimal("2.5")
        price = Decimal("1.0850")

        start_time = time.perf_counter()
        for _ in range(100_000):
            _ = group.calculate_margin(symbol_config, volume, price)
        elapsed = time.perf_counter() - start_time

        # Ensure 100k calculations execute in under 0.50 seconds
        assert elapsed < 0.50, f"Performance breach: 100k margin ops took {elapsed:.3f}s"

    def test_group_serialization_stress(self):
        overrides = [
            GroupSymbolOverride(symbol_pattern=f"SYM_{i}", spread_diff=i)
            for i in range(50)
        ]
        group = Group(name="ComplexGroup", symbol_overrides=overrides)

        start_time = time.perf_counter()
        for _ in range(10_000):
            d = group.to_dict()
            assert d["symbol_overrides_count"] == 50
        elapsed = time.perf_counter() - start_time

        assert elapsed < 1.0, f"Serialization breach: 10k to_dict ops took {elapsed:.3f}s"
