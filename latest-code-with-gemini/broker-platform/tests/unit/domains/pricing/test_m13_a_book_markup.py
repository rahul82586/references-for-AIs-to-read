"""M13: the A-Book client price and the venue price are different numbers.

Before this, measured against the real stack with a group SpreadDiff of 20 points,
raw ask 1.10010, and a venue filling at 1.10000:

    price we SENT to the LP     1.10030   <- the CLIENT price, marked up
    price the LP FILLED at      1.10000
    price we BOOKED the client  1.10000   <- the VENUE's price
    broker margin on the hedge  0.00000   = 0 points

Two defects pulling in opposite directions and cancelling to EXACTLY zero. That is
why nothing caught it: both numbers looked plausible, and no test asserted on the
difference. The broker earned nothing on hedged flow, silently.

MT5's model, from the Administrator guide's ECN worked example: the client is
quoted and filled at the converted price, the venue receives and fills at the
original, and "the broker earns the profit of 2 pips".

Policy under test: BROKER_ABOOK_IMPROVEMENT, default "client" - the broker earns
exactly its configured markup and the venue's own movement passes through. Set to
"broker" and the client pays their quoted price instead. Either way the client is
never booked worse than their quote plus allowed slippage; that floor is not
configurable.
"""
from decimal import Decimal

import pytest

from core.domains.accounts.value_objects import GroupSymbolOverride
from core.domains.pricing.a_book import (
    ABookQuoteError,
    client_fill_price,
    venue_price_for_instruction,
)

POINT = Decimal("0.00001")
RAW_BID = Decimal("1.10000")
RAW_ASK = Decimal("1.10010")


class _Symbol:
    name = "EURUSD"
    tick_size = POINT
    spread = 0
    spread_balance = 0
    spread_diff = 0
    spread_diff_balance = 0


class _Group:
    def __init__(self, diff=20, balance=0):
        self.symbol_overrides = [GroupSymbolOverride(
            symbol_pattern="EURUSD", spread_diff=diff, spread_diff_balance=balance)]


#: sentinel so `group=None` can mean "no group at all" rather than "use the
#: default 20-point group". A helper that quietly substitutes a default is how a
#: test for the no-group path ends up asserting the with-group behaviour.
NO_GROUP = object()
DEFAULT_GROUP = object()


def price(venue, *, group=DEFAULT_GROUP, side="BUY", quoted=None, slippage=None,
          improvement=True, symbol=None, raw_bid=RAW_BID, raw_ask=RAW_ASK):
    if group is DEFAULT_GROUP:
        group = _Group()
    elif group is NO_GROUP:
        group = None
    return client_fill_price(
        venue_price=venue, raw_bid=raw_bid, raw_ask=raw_ask,
        symbol=symbol if symbol is not None else _Symbol(),
        group=group,
        side=side, quoted_price=quoted, max_slippage_points=slippage,
        improvement_to_client=improvement,
    )


# ------------------------------------------------- the default: client keeps it

def test_the_broker_earns_exactly_its_configured_markup():
    """The headline: 20 points configured, 20 points earned - not 0, not 30."""
    r = price(Decimal("1.10000"))
    assert r.markup_earned == Decimal("0.00020")
    assert r.client_price == Decimal("1.10020")
    assert r.venue_price == Decimal("1.10000")


def test_the_venues_improvement_passes_to_the_client_by_default():
    """Venue filled 1 point better than the raw ask; the client gets that point."""
    r = price(Decimal("1.10000"))
    # client pays 1.10020, not the 1.10030 they were quoted
    assert r.client_price < Decimal("1.10030")
    assert r.improvement_passed_through == Decimal("0.00010")


def test_the_markup_is_the_same_whatever_the_venue_fills_at():
    """Revenue is stable: the markup does not depend on the venue's price."""
    earned = {price(v).markup_earned for v in
              (Decimal("1.09990"), Decimal("1.10000"), Decimal("1.10010"))}
    assert earned == {Decimal("0.00020")}, earned


def test_a_venue_filling_worse_still_costs_the_client_only_the_markup():
    r = price(Decimal("1.10020"), quoted=Decimal("1.10040"))
    assert r.markup_earned == Decimal("0.00020")
    assert r.client_price == Decimal("1.10040")


# ------------------------------------------------- the alternative: broker keeps

def test_broker_keeps_the_improvement_when_configured():
    r = price(Decimal("1.10000"), quoted=Decimal("1.10030"), improvement=False)
    assert r.client_price == Decimal("1.10030"), "the client pays their quoted price"
    assert r.markup_earned == Decimal("0.00030"), "the broker keeps venue + markup"


def test_broker_keeps_requires_the_quoted_price():
    """Without a quote there is nothing to book them at - refuse, don't guess."""
    with pytest.raises(ABookQuoteError):
        price(Decimal("1.10000"), quoted=None, improvement=False)


# ------------------------------------------------------------- the hard floor

def test_a_bad_venue_fill_is_capped_at_the_quote_plus_slippage():
    """The floor is not configurable: 'the LP filled badly' is not a price the
    client agreed to."""
    r = price(Decimal("1.10500"), quoted=Decimal("1.10030"), slippage=Decimal("10"))
    assert r.capped is True
    assert r.client_price == Decimal("1.10040"), "quoted + 10 points, nothing more"


def test_capping_with_zero_slippage_tolerance_holds_the_quoted_price():
    r = price(Decimal("1.10500"), quoted=Decimal("1.10030"), slippage=Decimal("0"))
    assert r.capped and r.client_price == Decimal("1.10030")


def test_a_sell_is_capped_in_the_other_direction():
    r = price(Decimal("1.09500"), side="SELL", quoted=Decimal("1.09990"),
              slippage=Decimal("10"))
    assert r.capped is True
    assert r.client_price == Decimal("1.09980")


def test_a_sell_earns_the_markup_when_the_bid_side_carries_it():
    """Bid-side markup: the client receives less than the venue paid.

    With SpreadDiffBalance = 0 the ENTIRE difference sits on the ask (M7's
    documented distribution: "3 bid / 0 ask"), so a SELL legitimately earns
    nothing. balance=20 moves it to the bid side, and then it does.
    """
    zero = price(Decimal("1.10000"), side="SELL", group=_Group(diff=20, balance=0),
                 quoted=Decimal("1.10000"))
    assert zero.markup_earned == Decimal("0"), (
        "with the whole difference on the ask, a sell must earn nothing"
    )

    r = price(Decimal("1.10000"), side="SELL", group=_Group(diff=20, balance=20),
              quoted=Decimal("1.09970"))
    assert r.client_price < Decimal("1.10000")
    assert r.markup_earned == Decimal("0.00020")


def test_no_cap_when_the_venue_fill_is_within_tolerance():
    r = price(Decimal("1.10015"), quoted=Decimal("1.10030"), slippage=Decimal("10"))
    assert r.capped is False


# ------------------------------------------------------- refusal, never a guess

def test_no_tick_size_refuses_rather_than_assuming_a_point():
    """A markup is a number of POINTS. Assuming 0.00001 would silently misprice
    every JPY and crypto symbol."""
    class NoPoint(_Symbol):
        tick_size = None

    with pytest.raises(ABookQuoteError) as ei:
        price(Decimal("1.10000"), symbol=NoPoint())
    assert "tick_size" in str(ei.value)


def test_a_non_positive_point_refuses():
    class BadPoint(_Symbol):
        tick_size = Decimal("0")

    with pytest.raises(ABookQuoteError):
        price(Decimal("1.10000"), symbol=BadPoint())


def test_a_configured_markup_with_no_raw_quote_refuses():
    """Nothing to measure the markup against. Falling back to the venue price is
    the quiet version of the original bug."""
    with pytest.raises(ABookQuoteError) as ei:
        price(Decimal("1.10000"), raw_bid=None, raw_ask=None)
    assert "no raw quote" in str(ei.value)


def test_a_non_positive_venue_price_refuses():
    with pytest.raises(ABookQuoteError):
        price(Decimal("0"))


def test_a_derived_non_positive_client_price_refuses():
    """A markup so large it drives the client price to zero must not book.

    Driven from the BUY side, where the ask carries the markup: a venue fill of
    0.00001 with a 5-point markup and a tiny quote caps down, so instead assert the
    guard directly on a sell whose bid markup exceeds the venue price.
    """
    # A sell with the whole 5-point difference on the bid drives 0.00002 down past
    # zero. `quoted` is set well above so the one-directional cap cannot rescue it -
    # the guard under test is the non-positive-price refusal, not the cap.
    with pytest.raises(ABookQuoteError):
        price(Decimal("0.00002"), symbol=_Symbol(),
              group=_Group(diff=5, balance=5), side="SELL", quoted=Decimal("0.00001"),
              slippage=Decimal("100000"))


# ------------------------------------------------------------- no markup config

def test_no_group_override_means_the_venue_price_passes_through():
    r = price(Decimal("1.10000"), group=_Group(diff=0), quoted=Decimal("1.10010"))
    assert r.client_price == Decimal("1.10000")
    assert r.markup_earned == Decimal("0")


def test_a_buy_with_no_markup_is_not_capped_by_a_lower_quote():
    """No markup means the venue price IS the client price; a quoted ceiling above
    it must not drag the client up to it."""
    r = price(Decimal("1.10000"), group=_Group(diff=0), quoted=Decimal("1.10010"))
    assert r.client_price == Decimal("1.10000") and r.capped is False


def test_no_group_at_all_is_not_an_error():
    r = price(Decimal("1.10000"), group=NO_GROUP, quoted=Decimal("1.10010"))
    assert r.client_price == Decimal("1.10000")
    assert r.spread_diff == 0


# --------------------------------------------------- pending trigger conversion

def test_a_pending_trigger_is_converted_back_to_source_terms():
    """The guide: 'The ECN converts the price to the original one 1.15659 and
    passes it to the external system.' A client Buy Limit at the marked-up price
    must become the equivalent level in the venue's own prices."""
    got = venue_price_for_instruction(
        client_instruction_price=Decimal("1.09500"), raw_bid=RAW_BID, raw_ask=RAW_ASK,
        symbol=_Symbol(), group=_Group(diff=20), side="BUY")
    assert got == Decimal("1.09480"), "20 points of markup must come back off"


def test_a_sell_pending_trigger_converts_the_other_way():
    """balance=20 so the bid side actually carries markup; with balance=0 the whole
    difference is on the ask and a sell-side conversion is correctly a no-op."""
    got = venue_price_for_instruction(
        client_instruction_price=Decimal("1.10500"), raw_bid=RAW_BID, raw_ask=RAW_ASK,
        symbol=_Symbol(), group=_Group(diff=20, balance=20), side="SELL")
    assert got > Decimal("1.10500")


def test_a_sell_conversion_is_a_no_op_when_the_bid_carries_no_markup():
    got = venue_price_for_instruction(
        client_instruction_price=Decimal("1.10500"), raw_bid=RAW_BID, raw_ask=RAW_ASK,
        symbol=_Symbol(), group=_Group(diff=20, balance=0), side="SELL")
    assert got == Decimal("1.10500")


def test_a_market_order_sends_no_price_at_all():
    """Inventing one would turn a market order into a limit order at the venue."""
    assert venue_price_for_instruction(
        client_instruction_price=None, raw_bid=RAW_BID, raw_ask=RAW_ASK,
        symbol=_Symbol(), group=_Group(diff=20), side="BUY") is None


def test_no_markup_means_the_instruction_is_unchanged():
    got = venue_price_for_instruction(
        client_instruction_price=Decimal("1.09500"), raw_bid=RAW_BID, raw_ask=RAW_ASK,
        symbol=_Symbol(), group=_Group(diff=0), side="BUY")
    assert got == Decimal("1.09500")


def test_conversion_round_trips_against_the_client_price():
    """Converting out and back must return the client's instruction - the two
    functions are inverses, and if they drift the trigger and the booking disagree."""
    instruction = Decimal("1.09500")
    venue = venue_price_for_instruction(
        client_instruction_price=instruction, raw_bid=RAW_BID, raw_ask=RAW_ASK,
        symbol=_Symbol(), group=_Group(diff=20), side="BUY")
    back = price(venue, quoted=Decimal("1.20000"), slippage=Decimal("100000"))
    assert back.client_price == instruction


# ------------------------------------------------------- the policy resolution

def test_the_environment_policy_is_read(monkeypatch):
    from application.services.execution_orchestrator import _improvement_to_client

    monkeypatch.delenv("BROKER_ABOOK_IMPROVEMENT", raising=False)
    assert _improvement_to_client(None) is True, "the default must be the client"
    monkeypatch.setenv("BROKER_ABOOK_IMPROVEMENT", "broker")
    assert _improvement_to_client(None) is False
    monkeypatch.setenv("BROKER_ABOOK_IMPROVEMENT", "client")
    assert _improvement_to_client(None) is True


def test_an_unrecognised_policy_falls_back_to_the_client_and_says_so(monkeypatch, caplog):
    """This decides who keeps real money, so a typo must not quietly change it."""
    import logging

    from application.services.execution_orchestrator import _improvement_to_client

    monkeypatch.setenv("BROKER_ABOOK_IMPROVEMENT", "cleint")   # typo
    with caplog.at_level(logging.ERROR):
        assert _improvement_to_client(None) is True
    assert "BROKER_ABOOK_IMPROVEMENT" in caplog.text


def test_a_group_override_beats_the_environment(monkeypatch):
    """The per-group hook exists so the config plane can own this later without
    touching a call site."""
    from application.services.execution_orchestrator import _improvement_to_client

    monkeypatch.setenv("BROKER_ABOOK_IMPROVEMENT", "client")

    class G:
        abook_improvement = "broker"

    class A:
        group = G()

    assert _improvement_to_client(A()) is False
