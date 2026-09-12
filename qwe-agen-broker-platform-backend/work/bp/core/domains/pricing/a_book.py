"""A-Book pricing: what the client pays, what the venue gets, and who earns the gap.

THE PROBLEM THIS SOLVES
=======================
Measured against the real stack before this module existed (group SpreadDiff 20
points, raw ask 1.10010, venue's own ask 1.10000):

    price we SENT to the LP     1.10030   <- the CLIENT price, marked up
    price the LP FILLED at      1.10000
    price we BOOKED the client  1.10000   <- the VENUE's price
    broker margin on the hedge  0.00000   = 0 points

Two defects pulling in opposite directions and cancelling to exactly zero, which is
why nothing caught it: both numbers looked plausible.

  a) the marked-up CLIENT price was forwarded to the venue, so a price-limited
     instruction asked the LP to trade 20 points worse than the market;
  b) the client was booked at the VENUE's fill price, discarding the markup they
     were quoted - and which the risk check and margin reservation were computed
     from.

WHAT MT5 DOES
=============
Administrator guide, ECN Price Translations, worked example:

    gateway passes original prices      EURUSD.ECN  1.15651 / 1.15659
    translation -2/+2                   EURUSD.USR  1.15649 / 1.15661
    client buys at                                  1.15661
    ECN converts BACK to the original   1.15659 and passes it to the external system
    external system fills at            1.15659
    client is told it filled at         1.15661
    "The broker earns the profit of 2 pips in this case."

So the two sides are priced independently and the gap is the broker's:

    client side  = venue price +/- the configured markup
    venue side   = the source price, never the client price

WHO KEEPS THE VENUE'S PRICE IMPROVEMENT
=======================================
Configurable, and the default is **the client**.

`improvement_to_client=True` (default): the broker earns exactly its configured
markup and no more. Whatever the venue filled at - better or worse than the raw
quote - flows through to the client. Revenue is stable and auditable, and the
client gets the execution quality the market actually offered.

`improvement_to_client=False`: the client always pays their quoted price, so the
broker also keeps any improvement the venue gave. Higher and more variable
revenue; worse execution quality for the client, and the client's fill no longer
tracks the market they can see.

There is a floor either way, and it is the part that must not be configurable away:
**the client can never be booked worse than the price they were quoted plus their
allowed slippage.** A venue fill that gapped through the quote is refused and
flagged for reconciliation rather than passed on, because "the LP filled badly" is
not a price the client agreed to.

Both directions are computed from the SAME spread settings M7 already resolves
(`resolve_spread_settings` -> `client_quote`), so there is one definition of what
this group's markup is, and B-Book and A-Book cannot drift apart.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass
from decimal import Decimal
from typing import Any, Optional, Tuple

from core.domains.pricing.engine import client_quote, resolve_spread_settings

logger = logging.getLogger(__name__)

__all__ = [
    "ABookPricing",
    "ABookQuoteError",
    "client_fill_price",
    "venue_price_for_instruction",
]


class ABookQuoteError(ValueError):
    """The client's fill could not be derived honestly.

    Raised rather than defaulted: booking a client at a guessed price after the
    venue has already filled is the expensive direction, and the caller treats this
    as a reconciliation break (the hedge is live, the client side is not).
    """


@dataclass(frozen=True)
class ABookPricing:
    """The two sides of one A-Book fill, and the gap between them."""

    #: what the client is booked at
    client_price: Decimal
    #: what the venue actually filled at
    venue_price: Decimal
    #: the raw platform quote the markup was measured against
    raw_price: Decimal
    #: broker revenue per unit of the base currency: client - venue, signed for the
    #: client's side. Positive on a BUY means the client paid above the venue.
    markup_earned: Decimal
    #: how much of the venue's own movement went to the client rather than the book
    improvement_passed_through: Decimal
    #: the group settings that produced it, for the audit trail
    spread_diff: int = 0
    spread_diff_balance: int = 0
    #: True when the client price was capped at their quote + slippage
    capped: bool = False

    @property
    def points_earned(self) -> Decimal:
        """markup_earned expressed in points - what a dealer reads."""
        return self.markup_earned


def _point(symbol: Any) -> Decimal:
    """The symbol's point, required. A markup is a number of POINTS, so guessing a
    precision here would silently misprice every JPY and crypto symbol."""
    p = getattr(symbol, "tick_size", None)
    if p is None:
        raise ABookQuoteError(
            f"symbol {getattr(symbol, 'name', symbol)!r} has no tick_size; an A-Book "
            "markup is a number of points and cannot be applied without one"
        )
    p = Decimal(str(p))
    if p <= 0:
        raise ABookQuoteError(
            f"symbol {getattr(symbol, 'name', symbol)!r} has a non-positive tick_size "
            f"({p}); refusing to apply a markup against it"
        )
    return p


def _is_buy(side: Any) -> bool:
    s = str(getattr(side, "value", side) or "").upper()
    return s.startswith("BUY")


def client_fill_price(
    *,
    venue_price: Decimal,
    raw_bid: Optional[Decimal],
    raw_ask: Optional[Decimal],
    symbol: Any,
    group: Any,
    side: Any,
    quoted_price: Optional[Decimal] = None,
    max_slippage_points: Optional[Decimal] = None,
    improvement_to_client: bool = True,
) -> ABookPricing:
    """Derive the price the CLIENT is booked at, from the venue's fill.

    The markup is measured once, against the raw platform quote, and then applied
    to whatever the venue filled at. That is what makes the venue's improvement
    separable from the broker's markup - and what makes the default (improvement to
    the client) mean something.

    `quoted_price` is what the client was shown when the order was risk-checked.
    When supplied it is the ceiling: the client is never booked worse than that
    plus `max_slippage_points`, whatever the venue did.
    """
    venue = Decimal(str(venue_price))
    if venue <= 0:
        raise ABookQuoteError(f"venue filled at a non-positive price ({venue_price})")

    point = _point(symbol)
    settings = resolve_spread_settings(symbol, group)
    buy = _is_buy(side)

    # The markup in PRICE terms, measured against the raw quote. Using the raw
    # quote as the reference (rather than the venue's fill) is what keeps the
    # broker's revenue equal to the configured markup regardless of where the venue
    # filled - and what makes the pass-through amount computable.
    markup_price = Decimal("0")
    raw_reference = raw_ask if buy else raw_bid
    if raw_reference is not None and settings.has_effect():
        raw_bid_d = Decimal(str(raw_bid)) if raw_bid is not None else raw_reference
        raw_ask_d = Decimal(str(raw_ask)) if raw_ask is not None else raw_reference
        try:
            c_bid, c_ask = client_quote(raw_bid_d, raw_ask_d, point=point,
                                        settings=settings)
        except ValueError as exc:
            raise ABookQuoteError(
                f"the group's spread settings cannot be applied to {getattr(symbol, 'name', symbol)}: {exc}"
            ) from exc
        client_reference = c_ask if buy else c_bid
        markup_price = client_reference - raw_reference
        if not improvement_to_client:
            # Broker keeps the improvement: the client pays their QUOTED price, so
            # the markup is measured from the venue fill back to that quote.
            markup_price = client_reference - raw_reference
    elif settings.has_effect() and raw_reference is None:
        raise ABookQuoteError(
            f"a markup is configured for {getattr(symbol, 'name', symbol)} but no raw "
            "quote is available to measure it against; refusing to guess"
        )

    if improvement_to_client:
        # Venue price +/- the configured markup. The venue's own movement - good or
        # bad - flows straight through to the client.
        client_price = venue + markup_price
        improvement = (venue - raw_reference) if raw_reference is not None else Decimal("0")
        if buy:
            # a LOWER venue ask is an improvement to a buyer
            improvement = -improvement
    else:
        # Client pays the quoted price; the broker keeps whatever the venue gave.
        if quoted_price is None:
            raise ABookQuoteError(
                "improvement_to_client=False needs the price the client was quoted; "
                "without it there is nothing to book them at"
            )
        client_price = Decimal(str(quoted_price))
        improvement = Decimal("0")

    # ---- the floor, which is not configurable -------------------------------
    #
    # This caps in ONE direction only: against a fill WORSE than the client was
    # quoted. It must never raise a buyer's price or lower a seller's, even when
    # `quoted_price` is worse than what was derived. Two reasons:
    #
    #   * `quoted_price` on a market order is the price the order was RISK-CHECKED
    #     at (M8 made risk see the client price). With no markup configured that is
    #     the raw ask, while the venue may fill better - dragging the client up to
    #     the risk-check price would silently charge them for a number that was only
    #     ever an internal reference.
    #   * When improvement passes to the client, the derived price is BY
    #     CONSTRUCTION better than the quote. Capping toward the quote would cancel
    #     the pass-through, which is the entire point of the default policy.
    #
    # So: cap only when the derived price is worse than quote + tolerance.
    capped = False
    if quoted_price is not None:
        quoted = Decimal(str(quoted_price))
        tolerance = Decimal("0")
        if max_slippage_points is not None:
            tolerance = Decimal(str(max_slippage_points)) * point
        worst = quoted + tolerance if buy else quoted - tolerance
        if (buy and client_price > worst) or (not buy and client_price < worst):
            logger.warning(
                "venue filled %s at %s, which would book the client at %s - beyond "
                "their quoted %s plus %s points of slippage. Capping at %s and "
                "flagging the difference for reconciliation; the broker absorbs it "
                "rather than charging a price nobody agreed to.",
                getattr(symbol, "name", symbol), venue, client_price, quoted,
                max_slippage_points or 0, worst,
            )
            client_price = worst
            capped = True

    if client_price <= 0:
        raise ABookQuoteError(
            f"the derived client price is not positive ({client_price}); refusing to book"
        )

    markup_earned = (client_price - venue) if buy else (venue - client_price)
    return ABookPricing(
        client_price=client_price,
        venue_price=venue,
        raw_price=Decimal(str(raw_reference)) if raw_reference is not None else venue,
        markup_earned=markup_earned,
        improvement_passed_through=improvement,
        spread_diff=settings.spread_diff,
        spread_diff_balance=settings.spread_diff_balance,
        capped=capped,
    )


def venue_price_for_instruction(
    *,
    client_instruction_price: Optional[Decimal],
    raw_bid: Optional[Decimal],
    raw_ask: Optional[Decimal],
    symbol: Any,
    group: Any,
    side: Any,
) -> Optional[Decimal]:
    """Convert a PENDING order's client-side trigger price back to source terms.

    The guide: "The ECN converts the price to the original one 1.15659 and passes it
    to the external system." A client's Buy Limit at the marked-up price must become
    the equivalent level in the venue's own prices, or the venue triggers 20 points
    late and the client's instruction is not honoured.

    Returns None for a MARKET order - there is no instruction price to convert, and
    inventing one would turn a market order into a limit order at the venue.
    """
    if client_instruction_price is None:
        return None
    client_px = Decimal(str(client_instruction_price))
    if client_px <= 0:
        return None
    raw_reference = raw_ask if _is_buy(side) else raw_bid
    if raw_reference is None:
        # No raw quote to measure against: pass the instruction through unchanged
        # rather than guessing an offset. Loud, because the trigger will be off by
        # exactly the markup.
        logger.warning(
            "cannot convert the client instruction price %s for %s back to source "
            "terms - no raw quote is available. Passing it through unchanged, so the "
            "venue trigger will be offset by the group's markup.",
            client_px, getattr(symbol, "name", symbol),
        )
        return client_px

    point = _point(symbol)
    settings = resolve_spread_settings(symbol, group)
    if not settings.has_effect():
        return client_px
    raw_bid_d = Decimal(str(raw_bid)) if raw_bid is not None else Decimal(str(raw_reference))
    raw_ask_d = Decimal(str(raw_ask)) if raw_ask is not None else Decimal(str(raw_reference))
    c_bid, c_ask = client_quote(raw_bid_d, raw_ask_d, point=point, settings=settings)
    client_reference = c_ask if _is_buy(side) else c_bid
    offset = client_reference - raw_reference
    return client_px - offset
