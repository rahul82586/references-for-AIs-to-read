"""Reconciliation: does our book match the venue's, and what do we do when it doesn't?

WHY THIS EXISTS
===============
M11 made an A-Book trade real: a client order becomes a hedge at the venue, and
the client side is booked from the venue's own report. It also made failures
*visible* - a `FixTimeout` or a transport error leaves the order PLACED with its
margin held and publishes `HEDGE_STATE_UNKNOWN` with `reconciliation_required`.
And `TradeServerLiquidityGateway` has no idempotency key at all (trade-server
hardcodes `magic` and `comment` and accepts no client order id), so a blind retry
could double-hedge.

But nothing ever *resolved* any of it. A flagged break held its margin forever;
nobody compared our positions against the venue's; and after a restart every
account showed the equity and margin last computed before the shutdown, because
valuation only happens on a tick while the server runs (observed live: an account
holding an open BTCUSD position still read equity=100000, profit=0 ten hours
later, while the terminal's own book was current).

So the two books silently diverge, in both directions:
  * we think we are hedged and the venue has no such position;
  * the venue holds a hedge we never booked a client side for.

MT5 does not have this gap. Its gateways carry live counters (`TicksCount`,
`TradeRequestsCount`, `BytesSent`, `SysConnection`, `SysLastTime`) and the history
server owns a journal; the backup server reconciles and fails over. This module is
the first piece of that: a comparison, a persisted break, and a resolution.

DESIGN
======
Pure domain, no I/O. `ReconciliationEngine.compare()` takes two position sets and
returns breaks. The service layer fetches, persists and resolves; the engine
decides. That split is what makes the comparison testable without a venue.

Breaks are keyed by a stable identity (venue ticket where there is one, else
symbol+side+our reference) so the same difference found on two consecutive runs
updates one row rather than creating a second - a break that flaps every sweep is
noise, and an operator needs to see its AGE, not a pile of duplicates.

Severity is a decision, not a label:
  CRITICAL  money or risk is wrong right now - a hedge we don't know about, or a
            client position with no hedge on an A-Book book
  HIGH      an unresolved unknown - we cannot say whether the venue holds it
  MEDIUM    the volumes or prices disagree but both sides exist
  LOW       valuation drift; the books agree, our numbers are stale
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from decimal import Decimal
from enum import Enum
from typing import Any, Dict, Iterable, List, Optional, Sequence

logger = logging.getLogger(__name__)

__all__ = [
    "BreakKind",
    "BreakStatus",
    "ReconciliationBreak",
    "ReconciliationEngine",
    "ReconciliationRun",
    "SidePosition",
    "Severity",
]


class Severity(Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class BreakKind(Enum):
    """What disagrees. Named for the question an operator asks, not the code path."""

    #: The venue holds a position we have no client side for. Naked hedge.
    UNMATCHED_AT_VENUE = "UNMATCHED_AT_VENUE"
    #: We booked a client position that should be hedged, and the venue has none.
    UNMATCHED_LOCALLY = "UNMATCHED_LOCALLY"
    #: Both sides exist but the volumes differ. Partial fill, or a lost leg.
    VOLUME_MISMATCH = "VOLUME_MISMATCH"
    #: Both sides exist but the prices differ by more than tolerance.
    PRICE_MISMATCH = "PRICE_MISMATCH"
    #: An order we sent whose outcome we never learned (M11's HEDGE_STATE_UNKNOWN).
    UNKNOWN_HEDGE = "UNKNOWN_HEDGE"
    #: The books agree; our valuation is stale (D9 - nothing revalued on boot).
    STALE_VALUATION = "STALE_VALUATION"


class BreakStatus(Enum):
    OPEN = "OPEN"
    RESOLVED = "RESOLVED"
    IGNORED = "IGNORED"


@dataclass(frozen=True)
class SidePosition:
    """One side's view of a position, normalised so the two can be compared.

    `key` is the identity used for matching. The venue side keys on its own
    ticket; our side keys on the position id. A link between them is carried in
    `linked_key` when we know it (M11 stores the LP ticket on the DEAL_CREATED
    event), and matching prefers the link over symbol+side+volume guessing.
    """

    key: str
    symbol: str
    side: str                      # "BUY" / "SELL", uppercased
    volume: Decimal
    price: Optional[Decimal] = None
    venue: str = ""                # which book this came from
    linked_key: Optional[str] = None
    raw: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_venue(cls, row: Dict[str, Any], venue: str = "LP") -> "SidePosition":
        """Normalise a trade-server / MT5 position row.

        MT5 reports `type` as "buy"/"sell" (or 0/1 on some builds) and `ticket` as
        a number; our own rows use `action` and a string position_id. Both shapes
        are accepted here so the engine does not have to know which venue it is
        talking to.
        """
        ticket = row.get("ticket") or row.get("position_id") or row.get("id")
        side_raw = row.get("type") if row.get("type") is not None else row.get("action")
        side = _normalise_side(side_raw)
        volume = _dec(row.get("volume"), Decimal("0"))
        price = row.get("price_open")
        if price is None:
            price = row.get("average_price")
        return cls(
            key=str(ticket) if ticket is not None else f"{row.get('symbol')}:{side}:{volume}",
            symbol=str(row.get("symbol") or "").upper(),
            side=side,
            volume=volume,
            price=_dec(price, None),
            venue=venue,
            linked_key=None,
            raw=dict(row),
        )

    @classmethod
    def from_local(cls, position: Any, venue: str = "BROKER") -> "SidePosition":
        """Normalise our own Position entity."""
        action = getattr(position, "action", None)
        side = _normalise_side(getattr(action, "value", action))
        volume = getattr(getattr(position, "volume", None), "value", None)
        price_open = getattr(getattr(position, "price_open", None), "value", None)
        pid = getattr(position, "position_id", None) or getattr(position, "id", None)
        return cls(
            key=str(pid),
            symbol=str(getattr(position, "symbol", "") or "").upper(),
            side=side,
            volume=_dec(volume, Decimal("0")),
            price=_dec(price_open, None),
            venue=venue,
            linked_key=(str(position.external_id)
                        if getattr(position, "external_id", None) else None),
            raw={},
        )


def _normalise_side(value: Any) -> str:
    s = str(value if value is not None else "").strip().upper()
    if s in ("0", "BUY", "B", "POSITION_TYPE_BUY"):
        return "BUY"
    if s in ("1", "SELL", "S", "POSITION_TYPE_SELL"):
        return "SELL"
    return s


def _dec(value: Any, default: Optional[Decimal]) -> Optional[Decimal]:
    if value is None or value == "":
        return default
    try:
        return Decimal(str(value))
    except (ArithmeticError, ValueError, TypeError):
        return default


@dataclass
class ReconciliationBreak:
    """One difference between the two books, and what was done about it."""

    break_id: str
    kind: BreakKind
    severity: Severity
    symbol: str
    detail: str
    our_key: Optional[str] = None
    venue_key: Optional[str] = None
    our_volume: Optional[Decimal] = None
    venue_volume: Optional[Decimal] = None
    our_price: Optional[Decimal] = None
    venue_price: Optional[Decimal] = None
    account_login: Optional[int] = None
    status: BreakStatus = BreakStatus.OPEN
    first_seen: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    last_seen: Optional[datetime] = None
    occurrences: int = 1
    resolution: Optional[str] = None
    resolved_at: Optional[datetime] = None

    @property
    def identity(self) -> str:
        """Stable key so the same difference found twice updates one row.

        Includes the kind, both sides' keys, and - for a break with NO venue key -
        the account. That last part matters: six clients each holding an unhedged
        0.01 BTCUSD position are SIX separate problems for six separate clients,
        not one. Without the account in the key they collapse into a single row
        whose `occurrences` counts six clients, which reads like one recurring
        break and hides five of them.

        A venue-keyed break does not need the account: the ticket already
        identifies one specific position.
        """
        discriminator = self.our_key or (
            f"acct:{self.account_login}" if self.account_login is not None else "-"
        )
        return "|".join([
            self.kind.value,
            self.symbol or "-",
            discriminator,
            self.venue_key or "-",
        ])


@dataclass
class ReconciliationRun:
    """The result of one comparison - what a `cli sync` prints."""

    started_at: datetime
    finished_at: Optional[datetime] = None
    venue: str = ""
    our_positions: int = 0
    venue_positions: int = 0
    breaks: List[ReconciliationBreak] = field(default_factory=list)
    #: breaks that were already open and are still open (aged, not new)
    recurring: int = 0
    #: breaks that disappeared this run, so they were auto-resolved
    cleared: List[str] = field(default_factory=list)
    error: Optional[str] = None

    @property
    def clean(self) -> bool:
        return self.error is None and not self.breaks

    def by_severity(self) -> Dict[str, int]:
        out = {s.value: 0 for s in Severity}
        for b in self.breaks:
            out[b.severity.value] += 1
        return out


class ReconciliationEngine:
    """Compare two books. Pure: no I/O, no clock beyond what it is given."""

    def __init__(
        self,
        *,
        price_tolerance: Decimal = Decimal("0"),
        volume_tolerance: Decimal = Decimal("0"),
        hedged_symbols: Optional[Iterable[str]] = None,
    ) -> None:
        self.price_tolerance = price_tolerance
        self.volume_tolerance = volume_tolerance
        #: Symbols expected to be hedged at the venue. A local position in a
        #: symbol NOT in this set is B-Book - the broker is the counterparty, so
        #: the venue having nothing is correct and must not be reported.
        #: None = not configured (assume all hedged); empty set = pure B-Book.
        self.hedged_symbols = (
            None if hedged_symbols is None
            else {str(s).upper() for s in hedged_symbols}
        )

    def compare(
        self,
        ours: Sequence[SidePosition],
        theirs: Sequence[SidePosition],
        *,
        now: Optional[datetime] = None,
    ) -> List[ReconciliationBreak]:
        """Return every difference between the two books.

        Matching is by explicit link first (our position's stored venue ticket),
        then by symbol+side. Volume is compared only between matched pairs, so a
        partial fill shows as VOLUME_MISMATCH rather than as two unmatched legs.
        """
        stamp = now or datetime.now(timezone.utc)
        breaks: List[ReconciliationBreak] = []

        theirs_by_key = {p.key: p for p in theirs}
        theirs_by_link: Dict[str, SidePosition] = {}
        for p in theirs:
            theirs_by_link.setdefault(p.key, p)

        used_theirs: set = set()

        for mine in ours:
            counterpart = self._match(mine, theirs_by_key, theirs_by_link, used_theirs)
            if counterpart is not None:
                used_theirs.add(counterpart.key)
                b = self._compare_pair(mine, counterpart, stamp)
                if b is not None:
                    breaks.append(b)
                continue

            # No counterpart. Only a break if this symbol is meant to be hedged;
            # a B-Book position has no venue leg by design, and reporting it would
            # bury the real breaks in noise.
            #
            # `hedged_symbols is None` means "not configured, assume everything is
            # hedged" - the safe default for a sweep run against an A-Book broker
            # that has not listed its symbols yet. An EMPTY set means "nothing is
            # hedged", i.e. a pure B-Book book, where a missing venue leg is
            # correct. The two must not behave the same, and the earlier version
            # treated both as "no filter", so an unconfigured sweep reported every
            # B-Book position in the house as a naked CRITICAL break.
            if self.hedged_symbols is not None and mine.symbol not in self.hedged_symbols:
                continue
            breaks.append(ReconciliationBreak(
                break_id="", kind=BreakKind.UNMATCHED_LOCALLY, severity=Severity.CRITICAL,
                symbol=mine.symbol,
                detail=(
                    f"we hold {mine.side} {mine.volume} {mine.symbol} that should be "
                    f"hedged, and the venue has no matching position - the broker is "
                    f"naked on this flow"
                ),
                our_key=mine.key, our_volume=mine.volume, our_price=mine.price,
                account_login=_login_of(mine), first_seen=stamp, last_seen=stamp,
            ))

        for theirs_pos in theirs:
            if theirs_pos.key in used_theirs:
                continue
            breaks.append(ReconciliationBreak(
                break_id="", kind=BreakKind.UNMATCHED_AT_VENUE, severity=Severity.CRITICAL,
                symbol=theirs_pos.symbol,
                detail=(
                    f"the venue holds {theirs_pos.side} {theirs_pos.volume} "
                    f"{theirs_pos.symbol} (ticket {theirs_pos.key}) with no client "
                    f"position on our side - an orphaned hedge"
                ),
                venue_key=theirs_pos.key, venue_volume=theirs_pos.volume,
                venue_price=theirs_pos.price, first_seen=stamp, last_seen=stamp,
            ))

        return breaks

    def _match(self, mine: SidePosition, by_key: Dict[str, SidePosition],
               by_link: Dict[str, SidePosition], used: set) -> Optional[SidePosition]:
        # 1. an explicit link: we recorded the venue's ticket when we hedged
        if mine.linked_key:
            cand = by_key.get(mine.linked_key) or by_link.get(mine.linked_key)
            if cand is not None and cand.key not in used:
                return cand
        # 2. same symbol and side, closest volume. Deliberately conservative: a
        #    guess that pairs the wrong legs hides a real break, so this only runs
        #    when there is no link at all.
        candidates = [p for p in by_key.values()
                      if p.key not in used and p.symbol == mine.symbol and p.side == mine.side]
        if not candidates:
            return None
        if len(candidates) == 1:
            return candidates[0]
        return min(candidates,
                   key=lambda p: abs(p.volume - mine.volume))

    def _compare_pair(self, mine: SidePosition, theirs: SidePosition,
                      stamp: datetime) -> Optional[ReconciliationBreak]:
        dv = abs(mine.volume - theirs.volume)
        if dv > self.volume_tolerance:
            return ReconciliationBreak(
                break_id="", kind=BreakKind.VOLUME_MISMATCH,
                severity=Severity.MEDIUM if dv <= mine.volume else Severity.HIGH,
                symbol=mine.symbol,
                detail=(
                    f"{mine.symbol} {mine.side}: ours {mine.volume} vs venue "
                    f"{theirs.volume} (difference {dv}) - a partial fill nobody "
                    f"applied, or a lost leg"
                ),
                our_key=mine.key, venue_key=theirs.key,
                our_volume=mine.volume, venue_volume=theirs.volume,
                our_price=mine.price, venue_price=theirs.price,
                account_login=_login_of(mine), first_seen=stamp, last_seen=stamp,
            )
        if (mine.price is not None and theirs.price is not None
                and abs(mine.price - theirs.price) > self.price_tolerance):
            return ReconciliationBreak(
                break_id="", kind=BreakKind.PRICE_MISMATCH, severity=Severity.MEDIUM,
                symbol=mine.symbol,
                detail=(
                    f"{mine.symbol} {mine.side}: our open price {mine.price} vs the "
                    f"venue's {theirs.price}. Expected when a markup is configured - "
                    f"if none is, one side booked the wrong fill."
                ),
                our_key=mine.key, venue_key=theirs.key,
                our_volume=mine.volume, venue_volume=theirs.volume,
                our_price=mine.price, venue_price=theirs.price,
                account_login=_login_of(mine), first_seen=stamp, last_seen=stamp,
            )
        return None


def _login_of(pos: SidePosition) -> Optional[int]:
    raw = pos.raw or {}
    for key in ("account_login", "login"):
        if raw.get(key) is not None:
            try:
                return int(raw[key])
            except (TypeError, ValueError):
                return None
    return None
