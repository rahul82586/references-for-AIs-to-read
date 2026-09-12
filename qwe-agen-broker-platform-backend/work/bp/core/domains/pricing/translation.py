"""Price translation: MT5's markup mechanism, in one pure module.

MT5 does NOT have a "markup" field on a group. It has a price-translation table on
each gateway and feeder configuration, and it uses GROUPS to select which
configuration a client's flow reaches. From the Administrator guide, on the gateway
Module field:

    "The unlimited number of configurations with different settings can be created
     for each module."

and on the Groups tab:

    "the groups of clients whose trade operations will be processed by the gateway.
     Orders, deals and positions of clients from these groups will be translated to
     external trade systems through the gateway."

The live TCTrader export shows the pattern directly - two configurations of the
SAME module, distinguished only by their group lists, one of them literally named
"clone":

    [0] 'MetaTrader 5 Gateway'        ID=1  MetaTrader5Gateway64.exe  Groups=[]
    [2] 'MetaTrader 5 Gateway clone'  ID=3  MetaTrader5Gateway64.exe  Groups=['*', 'real\\*']

So: markup lives on the gateway configuration; groups route flow to a
configuration. That is why this module resolves (symbol, group) -> configuration
-> translation row -> markup, and never looks for a markup on the group itself.

RULES, each pinned to the guide and to the live wire data
=========================================================
Wire shape, verbatim from the export (feeder "Feeder"):
    {"Source": "*", "Symbol": "*!", "BidMarkup": "0", "AskMarkup": "0", "Digits": "0"}

* **Source** is the symbol in the EXTERNAL system; **Symbol** is the name on this
  platform. Renaming and markup are the same mechanism.
* **Bid/Ask are in POINTS of the source symbol.** "If a symbol has 4 decimal
  places, the markup of 1 will change prices by 0.0001; for symbols with 5 decimal
  places the markup will be equal to 0.00001." So a markup is meaningless without
  the source symbol's `point` - which is why `apply_translate` requires it and
  refuses rather than assuming 0.00001.
* **Sign convention:** "A positive value increases the price, a negative one
  decreases it." The guide's own example widens outward (Bid -2 / Ask +2) and
  warns that the reverse "may get a negative spread". This module clamps a crossed
  result and reports that it did, rather than silently publishing an inverted
  quote.
* **FIRST MATCH WINS by list order.** "If more than one translation settings match
  the same symbol on the platform side, only the one located higher in the list
  will be applied." The guide's example: `EURUSD.GW -> EURUSD (-1/+1)` beats
  `*.GW -> * (-2/+2)`.
* **Masks support a single `*` only.** "Only simple masks with a single * symbol
  are supported. Settings with more complicated masks (for example, having two *
  or ! negation symbol) are ignored." The live export's own row is `Symbol: "*!"` -
  a negation mask - so it is stored losslessly and SKIPPED at resolution, exactly
  as the platform would. Skipping is not the same as dropping: the row stays in
  the configuration and re-exports byte-identically.
* **A translation must not be applied twice.** "Price markup settings are not
  applied for the ECN symbol, when translated to other symbols... If EURUSD.ECN is
  used as a source in other translation rules, original prices without the markup
  will be translated from it." `apply_chain` therefore resolves at most ONE row per
  hop and never re-feeds its own output.

The order of operations against M7's group spread
================================================
M7 already applies the group's SpreadDiff / SpreadDiffBalance to the CLIENT price,
and the guide is explicit about sequencing: "Price transformation settings for a
group are applied AFTER applying base settings of a symbol." Translation is a
GATEWAY-side transform on the price coming FROM or going TO the venue, so it sits
on the other side of that boundary:

    venue raw  --[translation: gateway markup]-->  platform price
             --[M7: symbol fixed spread, then group SpreadDiff]-->  client price

Two independent layers, one direction each. Conflating them would double-charge or
cancel out depending on signs, which is why `apply_translate` takes and returns a
raw quote and knows nothing about groups' spread settings.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass
from decimal import Decimal
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

logger = logging.getLogger(__name__)

__all__ = [
    "Translation",
    "TranslationResult",
    "apply_translate",
    "mask_matches",
    "resolve_translation",
]


@dataclass(frozen=True)
class Translation:
    """One row of a gateway/feeder Translates table.

    `bid_markup` and `ask_markup` are signed integers in POINTS of the source
    symbol. `digits` is what the wire carries; the platform uses the source
    symbol's own precision, so `point` is supplied by the caller rather than
    derived from `digits` here.
    """

    source: str = ""
    symbol: str = ""
    bid_markup: int = 0
    ask_markup: int = 0
    digits: int = 0
    #: position in the configuration's list - first match wins by this order
    position: int = 0

    @classmethod
    def from_domain(cls, row: Dict[str, Any], position: int = 0) -> "Translation":
        return cls(
            source=str(row.get("source") or ""),
            symbol=str(row.get("symbol") or ""),
            bid_markup=_int(row.get("bid_markup")),
            ask_markup=_int(row.get("ask_markup")),
            digits=_int(row.get("digits")),
            position=position,
        )

    @property
    def is_supported_mask(self) -> bool:
        """True when both patterns are the simple single-`*` form MT5 supports.

        The guide: "Only simple masks with a single * symbol are supported.
        Settings with more complicated masks (for example, having two * or !
        negation symbol) are ignored." The live export ships `Symbol: "*!"`, so
        this is not a hypothetical.
        """
        for pattern in (self.source, self.symbol):
            if not pattern:
                continue
            if "!" in pattern:
                return False
            if pattern.count("*") > 1:
                return False
        return True

    @property
    def has_effect(self) -> bool:
        return bool(self.bid_markup or self.ask_markup)


@dataclass(frozen=True)
class TranslationResult:
    """What a translation did, and why - including why it did nothing."""

    bid: Decimal
    ask: Decimal
    applied: Optional[Translation] = None
    #: why nothing was applied: "no-match", "unsupported-mask", "no-effect",
    #: "no-point". Present so a caller can log the reason instead of guessing.
    skipped: Optional[str] = None
    #: set when the raw markups would have crossed the quote; the result is
    #: clamped, because publishing an inverted price is worse than a loud clamp.
    clamped: bool = False

    @property
    def changed(self) -> bool:
        return self.applied is not None


def mask_matches(pattern: Optional[str], name: str) -> bool:
    """MT5's simple symbol mask: empty or `*` matches all, one `*` is a wildcard.

    A trailing `*` is a prefix match, a leading `*` a suffix match, a single
    interior `*` a contains-with-ends match. Two `*` or any `!` is NOT supported
    and returns False, matching the platform's "are ignored" behaviour.
    """
    if not pattern or pattern == "*":
        return True
    if "!" in pattern or pattern.count("*") > 1:
        return False
    if "*" not in pattern:
        return pattern == name
    head, tail = pattern.split("*", 1)
    if head and tail:
        return name.startswith(head) and name.endswith(tail) and len(name) >= len(head) + len(tail)
    if head:
        return name.startswith(head)
    return name.endswith(tail)


def resolve_translation(
    symbol_name: str,
    translations: Sequence[Any],
    *,
    source_name: Optional[str] = None,
) -> Optional[Translation]:
    """The translation row that applies to `symbol_name`, or None.

    First match wins, in list order - "only the one located higher in the list will
    be applied". Rows whose masks are unsupported are skipped with a warning rather
    than matched loosely: guessing at a `!` negation would apply a markup the
    operator never intended, which is the dangerous direction.

    `source_name` defaults to `symbol_name`, which is the common case (no rename).
    Pass it explicitly when the venue calls the instrument something else.
    """
    source = (source_name or symbol_name)
    rows = _as_translations(translations)
    for row in sorted(rows, key=lambda t: t.position):
        if not row.is_supported_mask:
            logger.warning(
                "translation row %r -> %r uses a mask MT5 does not support (two '*' "
                "or a '!' negation); skipping it rather than guessing. The row is "
                "still stored and re-exports unchanged.",
                row.source, row.symbol,
            )
            continue
        if mask_matches(row.symbol, symbol_name) and mask_matches(row.source, source):
            return row
    return None


def apply_translate(
    raw_bid: Decimal,
    raw_ask: Decimal,
    *,
    point: Decimal,
    translations: Sequence[Any],
    symbol_name: str,
    source_name: Optional[str] = None,
) -> TranslationResult:
    """Apply the venue-side markup to a raw quote.

    `point` is the SOURCE symbol's point, and it is required: a markup is a number
    of points, so without the source precision it has no meaning. Passing 0 or a
    wrong point would silently produce a wrong price, so a non-positive point
    skips the translation and says so.
    """
    bid = Decimal(str(raw_bid))
    ask = Decimal(str(raw_ask))

    row = resolve_translation(symbol_name, translations, source_name=source_name)
    if row is None:
        return TranslationResult(bid=bid, ask=ask, skipped="no-match")
    if not row.is_supported_mask:
        return TranslationResult(bid=bid, ask=ask, applied=None, skipped="unsupported-mask")
    if not row.has_effect:
        # A real row with 0/0 markups - the live export's own row. It renames
        # without repricing, so there is nothing to do to the numbers.
        return TranslationResult(bid=bid, ask=ask, applied=row, skipped="no-effect")

    p = Decimal(str(point))
    if p <= 0:
        logger.error(
            "cannot apply translation %r -> %r to %s: the source point is %s, and a "
            "markup is a number of POINTS. Refusing to guess a precision.",
            row.source, row.symbol, symbol_name, point,
        )
        return TranslationResult(bid=bid, ask=ask, applied=row, skipped="no-point")

    new_bid = bid + Decimal(row.bid_markup) * p
    new_ask = ask + Decimal(row.ask_markup) * p

    clamped = False
    if new_ask < new_bid:
        # The guide warns about exactly this: bid positive / ask negative "may get
        # a negative spread". Clamp and report, never publish an inverted quote.
        logger.error(
            "translation %r -> %r (bid %+d / ask %+d points) crossed the quote for "
            "%s: %s/%s -> %s/%s. Clamped to a zero spread; check the markup signs "
            "(MT5's convention is bid negative, ask positive).",
            row.source, row.symbol, row.bid_markup, row.ask_markup, symbol_name,
            bid, ask, new_bid, new_ask,
        )
        new_ask = new_bid
        clamped = True
    if new_bid <= 0:
        logger.error(
            "translation on %s produced a non-positive bid (%s); refusing to apply "
            "it. The raw quote is returned unchanged.", symbol_name, new_bid,
        )
        return TranslationResult(bid=bid, ask=ask, applied=row,
                                 skipped="non-positive-bid", clamped=clamped)

    return TranslationResult(bid=new_bid, ask=new_ask, applied=row, clamped=clamped)


def _as_translations(rows: Iterable[Any]) -> List[Translation]:
    """Accept Translation objects or the decoded wire dicts the loader produces."""
    out: List[Translation] = []
    for i, r in enumerate(rows or ()):
        if isinstance(r, Translation):
            out.append(r if r.position else Translation(
                r.source, r.symbol, r.bid_markup, r.ask_markup, r.digits, i))
        elif isinstance(r, dict):
            out.append(Translation.from_domain(r, position=i))
    return out


def _int(value: Any) -> int:
    try:
        return int(str(value).strip() or 0)
    except (TypeError, ValueError):
        return 0
