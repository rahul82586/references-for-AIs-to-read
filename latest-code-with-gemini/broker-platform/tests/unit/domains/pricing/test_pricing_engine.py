"""M7: the pricing engine — MT5's spread transformation maths, pure units.

Every formula here is pinned to the MT5 Administrator guide:
* fixed spread (Symbols, Common): non-zero Spread makes the spread EXACTLY
  Spread points, distributed by SpreadBalance ("2 bid / 2 ask" style);
* spread difference (Groups, Group Symbol Settings, Common): "if you set 3 as
  the spread difference, then the distribution can be 3 bid / 0 ask, 2 bid /
  1 ask" — Difference Balance points lower the bid, the rest raise the ask;
* group settings apply AFTER the symbol's base settings;
* "default" (None) inherits, never zeroes.
"""
from dataclasses import replace
from decimal import Decimal

import pytest

from core.domains.accounts.value_objects import GroupSymbolOverride
from core.domains.pricing.engine import (
    SpreadSettings,
    client_quote,
    pattern_matches,
    resolve_spread_settings,
)

POINT = Decimal("0.00001")
BID = Decimal("1.10000")
ASK = Decimal("1.10010")


class _Sym:
    def __init__(self, name="EURUSD", spread=0, spread_balance=0, spread_diff=0, spread_diff_balance=0):
        self.name = name
        self.spread = spread
        self.spread_balance = spread_balance
        self.spread_diff = spread_diff
        self.spread_diff_balance = spread_diff_balance


class _Grp:
    def __init__(self, overrides):
        self.symbol_overrides = overrides


def quote(settings, bid=BID, ask=ASK, point=POINT):
    return client_quote(bid, ask, point=point, settings=settings)


# --- the transform ------------------------------------------------------------

def test_no_settings_passes_the_feed_through():
    assert quote(SpreadSettings()) == (BID, ASK)


def test_fixed_spread_replaces_the_feed_spread_exactly():
    """Spread=30, Balance=10: 10 points below the raw bid, 20 above it.
    The feed's own ask is discarded — the spread is FIXED at 30 points."""
    bid, ask = quote(SpreadSettings(fixed_spread=30, fixed_balance=10))
    assert bid == BID - Decimal("0.00010")
    assert ask == BID + Decimal("0.00020")
    assert (ask - bid) / POINT == 30


def test_spread_difference_distribution_follows_the_guide_example():
    """Diff=3 with balance 2 -> '2 bid / 1 ask' from the guide's own example."""
    bid, ask = quote(SpreadSettings(spread_diff=3, spread_diff_balance=2))
    assert bid == BID - 2 * POINT
    assert ask == ASK + 1 * POINT


def test_spread_difference_all_ask_when_balance_zero():
    bid, ask = quote(SpreadSettings(spread_diff=20, spread_diff_balance=0))
    assert bid == BID            # the client sells at the raw bid
    assert ask == ASK + 20 * POINT  # and buys 20 points up


def test_fixed_spread_then_difference_stack_in_the_guides_order():
    settings = SpreadSettings(fixed_spread=30, fixed_balance=10, spread_diff=4, spread_diff_balance=4)
    bid, ask = quote(settings)
    base_bid = BID - 10 * POINT
    assert bid == base_bid - 4 * POINT
    assert ask == base_bid + 30 * POINT + 0 * POINT  # (4-4) on the ask side


def test_negative_difference_tightens_and_never_inverts():
    bid, ask = quote(SpreadSettings(spread_diff=-100, spread_diff_balance=0))
    assert ask == bid  # clamped: a 100-point discount exceeds the 10-point raw spread
    bid, ask = quote(SpreadSettings(spread_diff=-5, spread_diff_balance=0))
    assert ask == ASK - 5 * POINT and bid == BID  # a sane discount survives


def test_zero_point_is_a_no_op_not_a_crash():
    assert quote(SpreadSettings(spread_diff=20), point=Decimal("0")) == (BID, ASK)


def test_transform_cannot_produce_a_non_positive_bid():
    with pytest.raises(ValueError):
        # diff=1 with balance=5 puts 5 points on the bid and credits 1 back:
        # net -4 points on a 1-point bid -> non-positive
        client_quote(Decimal("0.00001"), Decimal("0.00002"), point=Decimal("0.00001"),
                     settings=SpreadSettings(spread_diff=1, spread_diff_balance=5))


# --- resolution: symbol base, group override, inheritance ----------------------

def test_symbol_settings_are_the_base():
    s = resolve_spread_settings(_Sym(spread=30, spread_balance=10, spread_diff=2, spread_diff_balance=1), None)
    assert s == SpreadSettings(30, 10, 2, 1)


def test_group_override_replaces_only_what_it_sets():
    group = _Grp([GroupSymbolOverride(symbol_pattern="EURUSD", spread_diff=20)])
    s = resolve_spread_settings(_Sym(spread_diff=2, spread_diff_balance=1), group)
    assert s.spread_diff == 20          # overridden
    assert s.spread_diff_balance == 1   # inherited (None = "default")


def test_override_balance_is_independent_of_override_diff():
    group = _Grp([GroupSymbolOverride(symbol_pattern="*", spread_diff_balance=7)])
    s = resolve_spread_settings(_Sym(spread_diff=5), group)
    assert (s.spread_diff, s.spread_diff_balance) == (5, 7)


def test_first_matching_override_wins_and_patterns_follow_masks():
    group = _Grp([
        GroupSymbolOverride(symbol_pattern="EUR*", spread_diff=10),
        GroupSymbolOverride(symbol_pattern="*", spread_diff=99),
    ])
    assert resolve_spread_settings(_Sym(name="EURUSD"), group).spread_diff == 10
    assert resolve_spread_settings(_Sym(name="GBPUSD"), group).spread_diff == 99


def test_pattern_matching():
    assert pattern_matches("", "EURUSD") and pattern_matches("*", "EURUSD")
    assert pattern_matches("EUR*", "EURUSD") and not pattern_matches("EUR*", "GBPUSD")
    assert pattern_matches("EURUSD", "EURUSD") and not pattern_matches("EURUSD", "EURUSD.a")


# --- codec: the fields round-trip instead of quarantining ----------------------

def test_wire_record_models_spread_diff_both_ways():
    from infrastructure.mt5 import fieldmap
    from infrastructure.mt5.codec import domain_to_record, record_to_domain

    rec = {"Symbol": "TEST", "Spread": "0", "SpreadDiff": "20", "SpreadDiffBalance": "5"}
    dom = record_to_domain(rec, fieldmap.SYMBOL_FIELDS)
    assert dom["spread_diff"] == 20
    assert dom["spread_diff_balance"] == 5
    assert "SpreadDiff" not in (dom.get("_mt5_extra") or {})  # no longer quarantined

    out = domain_to_record({"name": "TEST", "spread_diff": 20, "spread_diff_balance": 5},
                           fieldmap.SYMBOL_FIELDS)
    assert out["SpreadDiff"] == "20"
    assert out["SpreadDiffBalance"] == "5"


def test_mapper_round_trip_keeps_the_fields():
    from infrastructure.config.loader import parse_symbol
    from infrastructure.persistence.config_mappers import db_to_symbol, symbol_to_db

    sym = parse_symbol(
        {"name": "EURUSD", "digits": 5, "tick_size": "0.00001", "spread_diff": 20,
         "spread_diff_balance": 5, "base_currency": "EUR", "quote_currency": "USD"},
        "test",
    )
    back = db_to_symbol(symbol_to_db(sym))
    assert (back.spread_diff, back.spread_diff_balance) == (20, 5)


def test_override_round_trip_preserves_inherit_sentinel():
    """An unset override balance must persist as MT5's "default", never as 0."""
    from infrastructure.persistence.config_mappers import db_to_group, group_to_db
    from tests.integration.trading_harness import make_group

    group = make_group()
    group.symbol_overrides = [
        GroupSymbolOverride(symbol_pattern="*", spread_diff=20),          # balance: inherit
        GroupSymbolOverride(symbol_pattern="GBP*", spread_diff_balance=3)  # diff: inherit
    ]
    back = db_to_group(group_to_db(group))
    first = next(o for o in back.symbol_overrides if o.symbol_pattern == "*")
    second = next(o for o in back.symbol_overrides if o.symbol_pattern == "GBP*")
    assert (first.spread_diff, first.spread_diff_balance) == (20, None)
    assert (second.spread_diff, second.spread_diff_balance) == (None, 3)
