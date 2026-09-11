"""Client quote transformation — MT5's spread semantics, in one pure module.

Before M7 the matching engine filled every order at the RAW feed price: group
`SpreadDiff` was quarantined out of the wire format and never applied, symbol
`Spread`/`SpreadBalance` were stored but read by nothing, and the broker earned
nothing on spread. This module is the single place a raw (bid, ask) becomes the
price a CLIENT of a given group sees.

Semantics, from the MT5 Administrator guide in the reference corpus:

* Symbol settings, Common (Platform-Setup.md, "Spread — spread size in
  points"): a non-zero `Spread` makes the spread FIXED — it is "calculated
  using the Spread balance parameter", i.e. `SpreadBalance` points of it sit
  below the raw bid and the remainder above it, so the client spread is
  exactly `Spread` points regardless of the feed's own spread. `Spread = 0`
  means FLOATING: the feed's bid/ask pass through (then the difference below).

* Group symbol settings, Common: "Spread difference — difference of a symbol
  spread for a certain group of users from the basic spread of the symbol;
  Difference balance — balance of spread difference distribution between bid
  and ask prices... if you set 3 as the spread difference, then the
  distribution can be the following: 3 bid / 0 ask, 2 bid / 1 ask". So
  `SpreadDiffBalance` points of the difference lower the client BID and the
  remainder raise the client ASK. And: "Price transformation settings for a
  group are applied AFTER applying base settings of a symbol."

* A group override value of MT5's `"default"` sentinel (None in the domain)
  INHERITS the symbol's setting — it never means zero.

The ECN translation example in the guide (client 1.14059 ↔ ECN 1.14053 via
2 points spread balance + 4 points ECN markup) is the same transform; the ECN
markup layer itself is deferred with the ECN work.
"""
from dataclasses import dataclass, replace
from decimal import Decimal
from typing import Any, Optional, Tuple

__all__ = [
    "SpreadSettings",
    "resolve_spread_settings",
    "client_quote",
    "pattern_matches",
]


@dataclass(frozen=True)
class SpreadSettings:
    """The effective spread configuration for one (symbol, group) pair.

    All values are in POINTS (multiples of the symbol's tick_size, which is
    MT5's Point). `fixed_*` come from the symbol's Spread/SpreadBalance;
    `spread_diff*` are the group-after-symbol transform.
    """

    fixed_spread: int = 0          # symbol Spread; 0 = floating
    fixed_balance: int = 0         # symbol SpreadBalance: points of the fixed spread on the bid side
    spread_diff: int = 0           # effective SpreadDiff (group override wins)
    spread_diff_balance: int = 0   # effective SpreadDiffBalance (points of the diff on the bid side)

    def has_effect(self) -> bool:
        return bool(self.fixed_spread or self.spread_diff)


def pattern_matches(pattern: Optional[str], symbol_name: str) -> bool:
    """MT5-style symbol mask: empty or '*' matches everything; a trailing '*'
    matches a prefix; otherwise exact. (The full mask language also supports
    '!' negation — not exercised by any configured override yet, documented
    rather than guessed.)
    """
    if not pattern or pattern == "*":
        return True
    if pattern.endswith("*"):
        return symbol_name.startswith(pattern[:-1])
    return symbol_name == pattern


def resolve_spread_settings(symbol: Any, group: Any) -> SpreadSettings:
    """Symbol base settings, then the first matching group override on top.

    None on an override field means MT5's "default" sentinel: inherit the
    symbol's value. A missing symbol or group degrades to whatever is known —
    pricing must never crash a fill because a cache entry is absent.
    """
    settings = SpreadSettings(
        fixed_spread=_as_int(getattr(symbol, "spread", 0)),
        fixed_balance=_as_int(getattr(symbol, "spread_balance", 0)),
        spread_diff=_as_int(getattr(symbol, "spread_diff", 0)),
        spread_diff_balance=_as_int(getattr(symbol, "spread_diff_balance", 0)),
    ) if symbol is not None else SpreadSettings()

    if group is None or symbol is None:
        return settings

    symbol_name = getattr(symbol, "name", "")
    for override in getattr(group, "symbol_overrides", None) or []:
        if not pattern_matches(getattr(override, "symbol_pattern", ""), symbol_name):
            continue
        diff = getattr(override, "spread_diff", None)
        balance = getattr(override, "spread_diff_balance", None)
        if diff is not None:
            settings = replace(settings, spread_diff=_as_int(diff))
        if balance is not None:
            settings = replace(settings, spread_diff_balance=_as_int(balance))
        break  # first matching override wins

    return settings


def client_quote(
    raw_bid: Decimal,
    raw_ask: Decimal,
    *,
    point: Decimal,
    settings: SpreadSettings,
) -> Tuple[Decimal, Decimal]:
    """Transform a raw feed quote into the client quote for these settings.

    Order of operations is the guide's: the symbol's base (fixed) spread
    first, the group's spread difference after. The client ask can never end
    below the client bid (a negative spread is not a thing); the clamp is the
    only silent adjustment and it can only trigger on a negative SpreadDiff
    larger than the raw spread.
    """
    bid = Decimal(str(raw_bid))
    ask = Decimal(str(raw_ask))
    point = Decimal(str(point))
    if point <= 0:
        return bid, ask  # an unconfigurable point means no transform is possible

    if settings.fixed_spread > 0:
        # Fixed spread: exactly `fixed_spread` points wide, `fixed_balance` of
        # them below the raw bid. The feed's own ask is replaced, per the guide:
        # "the spread will be considered fixed".
        below = Decimal(settings.fixed_balance) * point
        bid = bid - below
        ask = bid + Decimal(settings.fixed_spread) * point

    if settings.spread_diff:
        total = Decimal(settings.spread_diff) * point
        below = Decimal(settings.spread_diff_balance) * point
        bid = bid - below
        ask = ask + (total - below)

    if ask < bid:
        ask = bid
    if bid <= 0:
        raise ValueError(
            f"client bid is not positive ({bid}) after spread transformation — "
            "check SpreadDiff/SpreadBalance configuration"
        )
    return bid, ask


def _as_int(value: Any) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0
