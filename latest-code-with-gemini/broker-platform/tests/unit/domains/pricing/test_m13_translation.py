"""M13: gateway price translation - MT5's markup mechanism.

MT5 has no markup field on a group. Markup lives on a gateway/feeder
CONFIGURATION's Translates table, and the configuration's Groups list decides
which clients' flow reaches it. Per-group markup is therefore achieved by cloning
a gateway configuration per group - which is exactly what the live TCTrader export
does: two configurations of MetaTrader5Gateway64.exe, one named
"MetaTrader 5 Gateway clone", differing only in Groups ([] vs ['*', 'real\\*']).

Every rule here is pinned to the Administrator guide or to that live wire data.
"""
from decimal import Decimal

import pytest

from core.domains.pricing.translation import (
    Translation,
    apply_translate,
    mask_matches,
    resolve_translation,
)

PT5 = Decimal("0.00001")     # a 5-digit symbol's point
PT4 = Decimal("0.0001")      # a 4-digit symbol's point


def row(source="*", symbol="*", bid=0, ask=0, digits=0, position=0):
    return Translation(source=source, symbol=symbol, bid_markup=bid,
                       ask_markup=ask, digits=digits, position=position)


# ------------------------------------------------- the guide's worked example

def test_the_admin_guide_ecn_translation_example_reproduces_exactly():
    """Platform-Setup.md, Price Translations:

      gateway passes original prices   EURUSD.ECN  1.15651 / 1.15659
      translation -2/+2                EURUSD.USR  1.15649 / 1.15661
      "The broker earns the profit of 2 pips in this case."
    """
    rows = [Translation(source="EURUSD.ECN", symbol="EURUSD.USR",
                        bid_markup=-2, ask_markup=2)]
    r = apply_translate(Decimal("1.15651"), Decimal("1.15659"), point=PT5,
                        translations=rows, symbol_name="EURUSD.USR",
                        source_name="EURUSD.ECN")
    assert r.bid == Decimal("1.15649")
    assert r.ask == Decimal("1.15661")
    assert r.changed and not r.clamped
    # the broker's 2 pips, on each side
    assert r.ask - Decimal("1.15659") == Decimal("0.00002")
    assert Decimal("1.15651") - r.bid == Decimal("0.00002")


def test_a_markup_is_in_the_SOURCE_symbols_points_not_a_fixed_pip():
    """The guide: "if a symbol has 4 decimal places, the markup of 1 will change
    prices by 0.0001; for symbols with 5 decimal places the markup will be equal
    to 0.00001". The same integer markup must move different amounts."""
    rows = [row(bid=-1, ask=1)]
    five = apply_translate(Decimal("1.10000"), Decimal("1.10010"), point=PT5,
                           translations=rows, symbol_name="EURUSD")
    four = apply_translate(Decimal("1.1000"), Decimal("1.1001"), point=PT4,
                           translations=rows, symbol_name="EURUSD")
    assert five.bid == Decimal("1.09999") and five.ask == Decimal("1.10011")
    assert four.bid == Decimal("1.0999") and four.ask == Decimal("1.1002")
    # the same integer markup, two different price movements - the whole point
    assert (five.ask - Decimal("1.10010")) == Decimal("0.00001")   # 1 point @ 5 digits
    assert (four.ask - Decimal("1.1001")) == Decimal("0.0001")     # 1 point @ 4 digits
    assert (four.ask - Decimal("1.1001")) == 10 * (five.ask - Decimal("1.10010"))


def test_without_a_usable_point_the_translation_refuses_rather_than_guesses():
    """A markup is a number of POINTS. With no precision it has no meaning, and
    inventing 0.00001 would silently produce a wrong price on a JPY or crypto
    symbol."""
    rows = [row(bid=-2, ask=2)]
    for bad_point in (Decimal("0"), Decimal("-1")):
        r = apply_translate(Decimal("1.10000"), Decimal("1.10010"), point=bad_point,
                            translations=rows, symbol_name="EURUSD")
        assert r.skipped == "no-point"
        assert r.bid == Decimal("1.10000") and r.ask == Decimal("1.10010")


# --------------------------------------------------------- first match wins

def test_only_the_highest_matching_row_applies():
    """The guide's own example: EURUSD.GW->EURUSD (-1/+1) beats *.GW->* (-2/+2)."""
    rows = [
        row(source="*", symbol="EURUSD", bid=-1, ask=1, position=0),
        row(source="*", symbol="*", bid=-2, ask=2, position=1),
    ]
    r = apply_translate(Decimal("1.10000"), Decimal("1.10010"), point=PT5,
                        translations=rows, symbol_name="EURUSD")
    assert r.bid == Decimal("1.09999"), "the second row must not also apply"
    assert r.applied.symbol == "EURUSD"


def test_list_order_decides_not_specificity():
    """MT5 has no most-specific-wins rule; it is purely list position."""
    rows = [
        row(source="*", symbol="*", bid=-5, ask=5, position=0),
        row(source="*", symbol="EURUSD", bid=-1, ask=1, position=1),
    ]
    r = apply_translate(Decimal("1.10000"), Decimal("1.10010"), point=PT5,
                        translations=rows, symbol_name="EURUSD")
    assert r.bid == Decimal("1.09995"), "the wildcard listed FIRST wins"


def test_position_is_honoured_regardless_of_input_order():
    rows = [row(symbol="*", bid=-9, ask=9, position=7),
            row(symbol="EURUSD", bid=-1, ask=1, position=2)]
    got = resolve_translation("EURUSD", rows)
    assert got is not None and got.bid_markup == -1


# ------------------------------------------------------------- mask language

@pytest.mark.parametrize("pattern,name,expected", [
    ("*", "EURUSD", True),
    ("", "EURUSD", True),
    ("EURUSD", "EURUSD", True),
    ("EURUSD", "EURJPY", False),
    ("EUR*", "EURUSD", True),
    ("EUR*", "USDEUR", False),
    ("*USD", "EURUSD", True),
    ("*USD", "USDJPY", False),
    ("EUR*USD", "EURUSD", True),
    ("EUR*USD", "EURGBPUSD", True),
    ("EUR*USD", "EURJPY", False),
    # unsupported: two wildcards, or a negation
    ("EU*U*D", "EURUSD", False),
    ("!EURUSD", "EURUSD", False),
    ("*!", "EURUSD", False),
])
def test_mask_matching(pattern, name, expected):
    assert mask_matches(pattern, name) is expected


def test_the_live_exports_own_negation_mask_is_skipped_not_guessed():
    """The real TCTrader feeder row is `{"Source":"*","Symbol":"*!"}`. The guide
    says masks with '!' "are ignored", so this must not match anything - and must
    not be reinterpreted as "everything except nothing"."""
    live = [{"source": "*", "symbol": "*!", "bid_markup": 0, "ask_markup": 0,
             "digits": 0}]
    assert resolve_translation("EURUSD", live) is None
    r = apply_translate(Decimal("1.1"), Decimal("1.2"), point=PT5,
                        translations=live, symbol_name="EURUSD")
    assert r.skipped in ("no-match", "unsupported-mask")
    assert r.bid == Decimal("1.1")


def test_an_unsupported_mask_is_still_preserved_on_the_row():
    """Skipping at RESOLUTION must not mean dropping from CONFIG: the row has to
    re-export byte-identically."""
    t = Translation.from_domain({"source": "*", "symbol": "*!", "bid_markup": 0,
                                 "ask_markup": 0, "digits": 0})
    assert t.is_supported_mask is False
    assert t.symbol == "*!", "the mask must survive verbatim for re-export"


# ------------------------------------------------------------- sign handling

def test_a_crossed_quote_is_clamped_and_reported_not_published_inverted():
    """The guide warns bid-positive/ask-negative "may get a negative spread".
    Publishing an inverted quote would let a client buy below the bid."""
    r = apply_translate(Decimal("1.10000"), Decimal("1.10010"), point=PT5,
                        translations=[row(bid=100, ask=-100)], symbol_name="EURUSD")
    assert r.clamped is True
    assert r.ask >= r.bid


def test_a_non_positive_bid_refuses_the_translation():
    r = apply_translate(Decimal("0.00002"), Decimal("0.00003"), point=PT5,
                        translations=[row(bid=-5, ask=5)], symbol_name="SHIB")
    assert r.skipped == "non-positive-bid"
    assert r.bid == Decimal("0.00002"), "the raw quote must come back unchanged"


def test_the_guide_convention_widens_the_spread():
    """bid negative / ask positive is the normal case, and it must widen."""
    raw_spread = Decimal("1.10010") - Decimal("1.10000")
    r = apply_translate(Decimal("1.10000"), Decimal("1.10010"), point=PT5,
                        translations=[row(bid=-2, ask=2)], symbol_name="EURUSD")
    assert (r.ask - r.bid) == raw_spread + Decimal("0.00004")


def test_a_zero_zero_row_renames_without_repricing():
    """The live export's row is 0/0: it maps names, not prices."""
    rows = [{"source": "EURUSD_ABC", "symbol": "EURUSD", "bid_markup": 0,
             "ask_markup": 0, "digits": 0}]
    r = apply_translate(Decimal("1.10000"), Decimal("1.10010"), point=PT5,
                        translations=rows, symbol_name="EURUSD",
                        source_name="EURUSD_ABC")
    assert r.bid == Decimal("1.10000") and r.ask == Decimal("1.10010")
    assert r.applied is not None and r.skipped == "no-effect"


# ------------------------------------------------------------- input shapes

def test_decoded_wire_dicts_are_accepted_as_well_as_translation_objects():
    """The loader hands back dicts; the config plane will hand back objects."""
    as_dicts = [{"source": "*", "symbol": "EURUSD", "bid_markup": "2",
                 "ask_markup": "3", "digits": "5"}]
    as_objs = [Translation(source="*", symbol="EURUSD", bid_markup=2,
                           ask_markup=3, digits=5)]
    a = apply_translate(Decimal("1.1"), Decimal("1.2"), point=PT5,
                        translations=as_dicts, symbol_name="EURUSD")
    b = apply_translate(Decimal("1.1"), Decimal("1.2"), point=PT5,
                        translations=as_objs, symbol_name="EURUSD")
    assert a.bid == b.bid and a.ask == b.ask


def test_markup_arriving_as_a_string_is_parsed():
    """Every field on the wire is a quoted string, including the integers."""
    t = Translation.from_domain({"source": "*", "symbol": "*",
                                 "bid_markup": "-2", "ask_markup": "2",
                                 "digits": "5"})
    assert t.bid_markup == -2 and t.ask_markup == 2 and t.digits == 5


def test_garbage_markup_becomes_zero_not_an_exception():
    t = Translation.from_domain({"source": "*", "symbol": "*",
                                 "bid_markup": "abc", "ask_markup": None})
    assert t.bid_markup == 0 and t.ask_markup == 0


def test_no_rows_means_no_translation():
    r = apply_translate(Decimal("1.1"), Decimal("1.2"), point=PT5,
                        translations=[], symbol_name="EURUSD")
    assert r.skipped == "no-match" and r.bid == Decimal("1.1")


def test_a_rename_only_matches_when_both_sides_agree():
    rows = [Translation(source="EURUSD_ABC", symbol="EURUSD", bid_markup=-1,
                        ask_markup=1)]
    # platform symbol EURUSD fed by venue symbol EURUSD_ABC -> applies
    hit = apply_translate(Decimal("1.1"), Decimal("1.2"), point=PT5,
                          translations=rows, symbol_name="EURUSD",
                          source_name="EURUSD_ABC")
    assert hit.applied is not None
    # a different venue symbol must NOT pick up that row
    miss = apply_translate(Decimal("1.1"), Decimal("1.2"), point=PT5,
                           translations=rows, symbol_name="EURUSD",
                           source_name="SOMETHING_ELSE")
    assert miss.applied is None


def test_translation_is_applied_at_most_once():
    """The guide: a marked-up price is never re-translated. Feeding the result
    back in must not compound - one row, one application."""
    rows = [row(bid=-2, ask=2)]
    once = apply_translate(Decimal("1.10000"), Decimal("1.10010"), point=PT5,
                           translations=rows, symbol_name="EURUSD")
    twice = apply_translate(once.bid, once.ask, point=PT5,
                            translations=[], symbol_name="EURUSD")
    assert twice.bid == once.bid, "a second pass with no rows must be a no-op"
