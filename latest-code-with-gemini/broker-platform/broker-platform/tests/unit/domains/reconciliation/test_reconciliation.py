"""D9 + M12: valuation on demand, and reconciliation between the two books.

D9 - nothing revalued open positions except a tick. After a 10-hour shutdown an
account holding an open BTCUSD position still read equity=100000, profit=0,
margin_used=0, while the venue's own book was current. `cli sync` was an honest
stub that exited 2.

M12 - M11 made A-Book failures VISIBLE (HEDGE_STATE_UNKNOWN, reconciliation_required,
margin held) but nothing ever RESOLVED them, and nothing compared our positions
against the venue's. An orphaned hedge or a naked client position was invisible
until someone noticed the money.
"""
from datetime import datetime, timezone
from decimal import Decimal

import pytest

from core.domains.reconciliation.engine import (
    BreakKind,
    BreakStatus,
    ReconciliationBreak,
    ReconciliationEngine,
    Severity,
    SidePosition,
)
from infrastructure.persistence.repositories.reconciliation_repository import (
    InMemoryReconciliationRepository,
)


def pos(key, symbol="BTCUSD", side="BUY", volume="0.01", price=None, link=None,
        venue="LP", **raw):
    return SidePosition(key=key, symbol=symbol, side=side, volume=Decimal(volume),
                        price=Decimal(price) if price else None, venue=venue,
                        linked_key=link, raw=raw)


# ------------------------------------------------------------- the comparison

def test_matching_books_produce_no_breaks():
    e = ReconciliationEngine(hedged_symbols=["BTCUSD"])
    ours = [pos("P1", price="77365.83", link="T1")]
    theirs = [pos("T1", price="77365.83")]
    assert e.compare(ours, theirs) == []


def test_an_orphan_hedge_is_critical():
    """The venue holds something we never booked a client side for."""
    e = ReconciliationEngine(hedged_symbols=["BTCUSD"])
    found = e.compare([], [pos("T9", volume="0.05")])
    assert len(found) == 1
    assert found[0].kind is BreakKind.UNMATCHED_AT_VENUE
    assert found[0].severity is Severity.CRITICAL
    assert found[0].venue_key == "T9"


def test_a_naked_client_position_is_critical():
    """We are supposed to be hedged and are not."""
    e = ReconciliationEngine(hedged_symbols=["BTCUSD"])
    found = e.compare([pos("P1", volume="0.05")], [])
    assert len(found) == 1
    assert found[0].kind is BreakKind.UNMATCHED_LOCALLY
    assert found[0].severity is Severity.CRITICAL


def test_a_b_book_position_is_not_a_break():
    """The house is the counterparty, so the venue having nothing is CORRECT.

    Reporting these would bury the real breaks in noise, and noise is how a
    reconciliation report gets ignored.
    """
    e = ReconciliationEngine(hedged_symbols=["BTCUSD"])
    assert e.compare([pos("P1", symbol="EURUSD", volume="0.10")], []) == []


def test_with_no_hedged_symbols_configured_only_venue_orphans_are_reported():
    """An unconfigured sweep must not invent naked-position breaks everywhere."""
    e = ReconciliationEngine(hedged_symbols=[])
    assert e.compare([pos("P1", symbol="EURUSD")], []) == []
    assert len(e.compare([], [pos("T1")])) == 1


def test_a_volume_mismatch_is_reported_with_both_sides():
    e = ReconciliationEngine(hedged_symbols=["BTCUSD"])
    found = e.compare([pos("P1", volume="0.01", link="T1")], [pos("T1", volume="0.03")])
    assert len(found) == 1
    b = found[0]
    assert b.kind is BreakKind.VOLUME_MISMATCH
    assert b.our_volume == Decimal("0.01")
    assert b.venue_volume == Decimal("0.03")
    assert "0.02" in b.detail, "the detail must carry the difference, not just the two"


def test_a_price_mismatch_is_reported():
    e = ReconciliationEngine(hedged_symbols=["BTCUSD"])
    found = e.compare([pos("P1", price="77365.83", link="T1")],
                      [pos("T1", price="77300.00")])
    assert len(found) == 1
    assert found[0].kind is BreakKind.PRICE_MISMATCH


def test_a_price_difference_within_tolerance_is_not_a_break():
    """A configured markup makes the two prices differ BY DESIGN."""
    e = ReconciliationEngine(hedged_symbols=["BTCUSD"], price_tolerance=Decimal("100"))
    assert e.compare([pos("P1", price="77365.83", link="T1")],
                     [pos("T1", price="77300.00")]) == []


def test_an_explicit_link_beats_symbol_side_guessing():
    """Two positions in the same symbol and side must pair by ticket, not by luck."""
    e = ReconciliationEngine(hedged_symbols=["BTCUSD"])
    ours = [pos("P1", volume="0.01", link="T2"), pos("P2", volume="0.02", link="T1")]
    theirs = [pos("T1", volume="0.02"), pos("T2", volume="0.01")]
    assert e.compare(ours, theirs) == [], "linked pairs must match exactly"


# ------------------------------------------------------------ venue normalising

def test_mt5_and_local_row_shapes_both_normalise():
    """MT5 reports type=buy/sell and a numeric ticket; ours reports action and a
    string position_id. The engine must not need to know which venue it is given."""
    v = SidePosition.from_venue({"ticket": 5292093, "symbol": "btcusd", "type": "buy",
                                 "volume": 0.01, "price_open": 77365.83})
    assert v.key == "5292093" and v.symbol == "BTCUSD" and v.side == "BUY"
    assert v.volume == Decimal("0.01") and v.price == Decimal("77365.83")

    v2 = SidePosition.from_venue({"ticket": 1, "symbol": "EURUSD", "type": "1",
                                  "volume": "0.10"})
    assert v2.side == "SELL", "MT5 numeric type 1 is a sell"


# ------------------------------------------------------------- break lifecycle

@pytest.mark.asyncio
async def test_the_same_break_found_twice_ages_instead_of_duplicating():
    """Six identical rows is noise an operator learns to ignore; one row that says
    `occurrences=6, first_seen=six sweeps ago` is a signal."""
    repo = InMemoryReconciliationRepository()
    e = ReconciliationEngine(hedged_symbols=["BTCUSD"])

    first = None
    for _ in range(6):
        found = e.compare([], [pos("T9", volume="0.05")])
        first = await repo.upsert(found[0])

    open_breaks = await repo.find_open()
    assert len(open_breaks) == 1, "a recurring break must not duplicate"
    assert open_breaks[0].occurrences == 6
    assert open_breaks[0].break_id == first.break_id


@pytest.mark.asyncio
async def test_a_break_that_disappears_is_auto_resolved_not_silently_dropped():
    """A break that stops being reported is indistinguishable from one nobody
    looked at, unless the sweep says it cleared."""
    repo = InMemoryReconciliationRepository()
    e = ReconciliationEngine(hedged_symbols=["BTCUSD"])

    found = e.compare([], [pos("T9")])
    await repo.upsert(found[0])
    assert len(await repo.find_open()) == 1

    # next run: the venue position is gone
    still = e.compare([], [])
    cleared = await repo.auto_clear([b.identity for b in still], "no longer present")
    assert cleared == 1
    assert await repo.find_open() == []
    resolved = await repo.find_by_id(found[0].break_id)
    assert resolved.status is BreakStatus.RESOLVED
    assert resolved.resolution


@pytest.mark.asyncio
async def test_resolving_records_what_was_done():
    repo = InMemoryReconciliationRepository()
    e = ReconciliationEngine(hedged_symbols=["BTCUSD"])
    b = await repo.upsert(e.compare([], [pos("T9")])[0])
    assert await repo.resolve(b.break_id, "closed the orphan hedge at the venue")
    after = await repo.find_by_id(b.break_id)
    assert after.status is BreakStatus.RESOLVED
    assert after.resolved_at is not None
    assert "orphan hedge" in after.resolution


@pytest.mark.asyncio
async def test_resolving_an_unknown_id_is_false_not_an_error():
    repo = InMemoryReconciliationRepository()
    assert await repo.resolve("does-not-exist", "x") is False


def test_break_identity_is_stable_across_changing_detail():
    """The dedupe key must not include the prose, or a reworded detail splits one
    break into two."""
    a = ReconciliationBreak(break_id="1", kind=BreakKind.VOLUME_MISMATCH,
                            severity=Severity.MEDIUM, symbol="BTCUSD",
                            detail="ours 0.01 vs venue 0.03", our_key="P1",
                            venue_key="T1")
    b = ReconciliationBreak(break_id="2", kind=BreakKind.VOLUME_MISMATCH,
                            severity=Severity.HIGH, symbol="BTCUSD",
                            detail="completely different wording", our_key="P1",
                            venue_key="T1")
    assert a.identity == b.identity


# ------------------------------------------------------------- the service

@pytest.mark.asyncio
async def test_a_venue_that_cannot_report_is_an_error_not_a_clean_run():
    """"No breaks" and "could not look" must not print the same thing - that is the
    exact confusion M5 fixed on /account/positions."""
    from application.services.reconciliation_service import ReconciliationService

    class NoPositionsGateway:
        async def send_order(self, order, gateway_id):
            return {}

        async def cancel_order(self, order_id, gateway_id):
            return True

        async def get_quotes(self, symbols):
            return {}

    repo = InMemoryReconciliationRepository()
    svc = ReconciliationService(position_repo=_EmptyPositions(), break_repo=repo,
                                gateway=NoPositionsGateway())
    run = await svc.run()
    assert run.error is not None
    assert "cannot report" in run.error
    assert not run.clean


@pytest.mark.asyncio
async def test_no_gateway_at_all_is_also_an_error():
    from application.services.reconciliation_service import ReconciliationService

    repo = InMemoryReconciliationRepository()
    svc = ReconciliationService(position_repo=_EmptyPositions(), break_repo=repo,
                                gateway=None)
    run = await svc.run()
    assert run.error is not None
    assert not run.clean


@pytest.mark.asyncio
async def test_a_venue_outage_is_reported_as_an_error_not_a_crash():
    from application.services.reconciliation_service import ReconciliationService

    class Down:
        async def positions(self):
            raise ConnectionError("venue unreachable")

    svc = ReconciliationService(position_repo=_EmptyPositions(),
                                break_repo=InMemoryReconciliationRepository(),
                                gateway=Down())
    run = await svc.run()
    assert run.error is not None and "venue unreachable" in run.error


@pytest.mark.asyncio
async def test_a_clean_comparison_reports_both_sides_counted():
    from application.services.reconciliation_service import ReconciliationService

    class Venue:
        async def positions(self):
            return [{"ticket": "T1", "symbol": "BTCUSD", "type": "buy",
                     "volume": 0.01, "price_open": 77365.83}]

    svc = ReconciliationService(
        position_repo=_OnePosition(), break_repo=InMemoryReconciliationRepository(),
        gateway=Venue(), hedged_symbols=["BTCUSD"])
    run = await svc.run()
    assert run.error is None
    assert run.our_positions == 1 and run.venue_positions == 1
    assert run.clean


class _EmptyPositions:
    async def get_open_positions(self):
        return []


class _OnePosition:
    async def get_open_positions(self):
        return [_LocalPosition()]


class _LocalPosition:
    position_id = "P1"
    external_id = "T1"
    symbol = "BTCUSD"
    account_login = 880001

    class _A:
        value = "BUY"

    action = _A()

    class _V:
        value = Decimal("0.01")

    volume = _V()

    class _P:
        value = Decimal("77365.83")

    price_open = _P()
