"""Reconciliation and valuation: the two services that answer "are we current?"

D9 - valuation was never refreshed except on a tick
====================================================
`equity`, `profit`, `margin_free` and `margin_level` are recomputed by
`TickMarginPipeline` on TICK_RECEIVED, while the server runs. Nothing recomputes
them at boot. Observed live after a 10-hour shutdown: an account holding an open
BTCUSD position still read `equity=100000, profit=0, margin_used=0`, while the
venue's own book was current. `cli sync` was an honest stub that exited 2.

So `ValuationService` exists: revalue every account that holds an open position,
from the best price currently known, and stamp `last_valuation_at` so "current"
and "frozen since Friday" are distinguishable. It is called on startup (after the
feed has had a chance to deliver) and on a timer, and it is the same maths the
tick pipeline uses - one source of truth, two triggers.

It refuses to invent a price. A symbol with no tick known is skipped and counted,
because writing an equity computed from nothing is worse than leaving a stale one:
the stale number is at least a real number from a real moment.

M12 - reconciliation
====================
`ReconciliationService` compares our open positions against the venue's and
persists the differences as breaks. It also resolves the M11 `HEDGE_STATE_UNKNOWN`
orders: those are the ones where we genuinely cannot say whether the venue holds a
hedge, and asking the venue is the only way to find out.

The venue book comes from `ILiquidityGateway.positions()` where the adapter
supports it (TradeServerLiquidityGateway does; the FIX gateway cannot until
drop-copy exists, and says so rather than returning an empty list that would look
like "no breaks").
"""
from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timezone
from decimal import Decimal
from typing import Any, Dict, List, Optional

from core.domains.reconciliation.engine import (
    BreakKind,
    BreakStatus,
    ReconciliationBreak,
    ReconciliationEngine,
    ReconciliationRun,
    Severity,
    SidePosition,
)

logger = logging.getLogger(__name__)


class ValuationService:
    """Revalue accounts from the prices we currently hold. D9."""

    def __init__(self, *, account_repo, position_repo, symbol_repo,
                 market_data_engine, risk_engine=None, interval_s: float = 300.0) -> None:
        self.account_repo = account_repo
        self.position_repo = position_repo
        self.symbol_repo = symbol_repo
        self.market_data_engine = market_data_engine
        self.risk_engine = risk_engine
        self.interval_s = float(interval_s)
        self._task: Optional[asyncio.Task] = None
        self._running = False
        self.last_run: Optional[datetime] = None
        self.last_run_stats: Dict[str, int] = {}

    async def revalue_all(self) -> Dict[str, int]:
        """One pass over every account holding an open position.

        Returns counts rather than raising: a valuation sweep is a maintenance job,
        and one account failing to price must not stop the others.
        """
        stats = {"accounts": 0, "positions": 0, "revalued": 0,
                 "skipped_no_price": 0, "errors": 0}
        try:
            positions = await self._open_positions()
        except Exception as exc:  # noqa: BLE001
            logger.error("valuation sweep could not read open positions: %s", exc)
            stats["errors"] += 1
            self.last_run = datetime.now(timezone.utc)
            self.last_run_stats = stats
            return stats

        stats["positions"] = len(positions)
        by_login: Dict[Any, List[Any]] = {}
        for p in positions:
            login = getattr(p, "account_login", None)
            if login is None:
                continue
            by_login.setdefault(login, []).append(p)
        stats["accounts"] = len(by_login)

        for login, own in by_login.items():
            try:
                if not await self._revalue_one(login, own, stats):
                    continue
                stats["revalued"] += 1
            except Exception as exc:  # noqa: BLE001
                stats["errors"] += 1
                logger.error("valuation of account %s failed: %s", login, exc)

        self.last_run = datetime.now(timezone.utc)
        self.last_run_stats = stats
        if stats["skipped_no_price"]:
            logger.warning(
                "valuation sweep: %d position(s) could not be revalued because no "
                "price is known for their symbol - their accounts still carry the "
                "previous figures. Prices arrive with the feed; a symbol that is "
                "never subscribed is never revalued.",
                stats["skipped_no_price"],
            )
        else:
            logger.info(
                "valuation sweep: %d account(s) revalued over %d position(s)",
                stats["revalued"], stats["positions"],
            )
        return stats

    async def _revalue_one(self, login: Any, positions: List[Any],
                           stats: Dict[str, int]) -> bool:
        account = await self.account_repo.find_by_login(login)
        if account is None:
            logger.warning("valuation sweep: positions exist for unknown account %s", login)
            stats["errors"] += 1
            return False

        from core.domains.market_data.margin import position_pnl, MarginCalculationError

        total_pnl = Decimal("0")
        priced_any = False
        for p in positions:
            price = self._price_for(getattr(p, "symbol", ""))
            if price is None:
                stats["skipped_no_price"] += 1
                continue
            bid, ask = price
            symbol = await self._symbol(getattr(p, "symbol", ""))
            contract = Decimal(str(getattr(symbol, "contract_size", 1) or 1)) if symbol else Decimal("1")
            action = getattr(p, "action", None)
            side = str(getattr(action, "value", action) or "BUY").upper()
            quote_ccy = str(getattr(symbol, "quote_currency", "") or "") if symbol else ""
            try:
                total_pnl += position_pnl(
                    side=side,
                    volume_lots=getattr(getattr(p, "volume", None), "value", Decimal("0")),
                    open_price=getattr(getattr(p, "price_open", None), "value", Decimal("0")),
                    bid=bid, ask=ask, contract_size=contract,
                    quote_currency=quote_ccy,
                    deposit_currency=getattr(account, "currency", "USD"),
                    rate_lookup=(self.risk_engine._rate_lookup
                                 if self.risk_engine is not None else None),
                )
                priced_any = True
            except (MarginCalculationError, ArithmeticError, ValueError, TypeError) as exc:
                stats["skipped_no_price"] += 1
                logger.warning("cannot value position %s: %s",
                               getattr(p, "position_id", "?"), exc)

        if not priced_any:
            return False

        from core.domains.common.value_objects import Money
        currency = getattr(account, "currency", "USD")

        # update_equity is the same entry point the tick pipeline uses: it sets
        # profit, equity, margin_free (per the group's free-margin mode) and
        # margin_level. One implementation, two triggers.
        account.update_equity(Money(total_pnl, currency))

        # margin_used is NOT recomputed on the ordinary path. It belongs to
        # record_deal, and D8b exists precisely because a sweep that wrote it
        # erased what a fill had written.
        #
        # There is exactly one exception, and it is a repair rather than a
        # recompute: open positions exist but margin_used is zero. No legitimate
        # state looks like that - a flat account has no open positions - so it can
        # only mean a fill's margin write was lost. Leaving it would leave the
        # account overstating its free margin and pinned at the 999999 sentinel,
        # where stop-out can never fire. Recomputing it here is the difference
        # between a self-healing sweep and one that faithfully preserves a bug.
        if positions and account.margin_used.amount <= 0 and self.risk_engine is None:
            logger.warning(
                "account %s holds %d open position(s) with margin_used = 0 and no "
                "risk engine is wired into this sweep, so it cannot be repaired. "
                "Run the sweep inside the server (which wires one) or pass "
                "risk_engine explicitly.", login, len(positions),
            )
            stats["margin_unrepaired"] = stats.get("margin_unrepaired", 0) + 1
        elif positions and account.margin_used.amount <= 0 and self.risk_engine is not None:
            try:
                snapshot = self.risk_engine.calculate_margin_level(
                    account, await self._as_position_entities(positions))
                account.margin_used = Money(snapshot.margin_used, currency)
                account.margin_free = Money(
                    max(Decimal("0"), account.equity.amount - snapshot.margin_used), currency)
                account.recompute_margin_level()
                stats["margin_repaired"] = stats.get("margin_repaired", 0) + 1
                logger.warning(
                    "account %s held %d open position(s) with margin_used = 0; "
                    "recomputed to %s. A fill's margin write was lost - this sweep "
                    "repaired it, but the write path should be investigated.",
                    login, len(positions), account.margin_used.amount,
                )
            except Exception as exc:  # noqa: BLE001
                logger.error(
                    "account %s has open positions and zero margin_used, and the "
                    "repair recompute failed: %s - the account is under-margined "
                    "and stop-out cannot fire", login, exc,
                )

        setter = getattr(self.account_repo, "update_valuation", None)
        if setter is not None:
            # include_margin only on the repair path above, so the ordinary sweep
            # still cannot touch margin_used (D8b).
            repaired = stats.get("margin_repaired", 0) > 0
            try:
                await setter(account, include_margin=repaired)
            except TypeError:
                # a repository whose update_valuation predates include_margin
                await setter(account)
                if repaired:
                    await self.account_repo.save(account)
        else:
            await self.account_repo.save(account)
        stamp = getattr(self.account_repo, "mark_valued", None)
        if stamp is not None:
            try:
                await stamp(login, self.last_run or datetime.now(timezone.utc))
            except Exception as exc:  # noqa: BLE001
                logger.debug("could not stamp last_valuation_at for %s: %s", login, exc)
        return True

    async def _as_position_entities(self, rows: List[Any]) -> List[Any]:
        """The risk engine wants Position entities, not repository rows.

        It reads `position.symbol`, `.action`, `.volume.value`, `.price_open.value`
        and `.price_current.value`. A duck-typed row from a repository usually has
        all of these, but a raw dict or a partial projection does not, and passing
        one makes the repair raise - which would be reported as a valuation error
        and hide the fact that the account is under-margined. So anything missing a
        required attribute is dropped, and dropping all of them is reported rather
        than silently repairing nothing.
        """
        out = []
        for r in rows:
            needed = ("symbol", "action", "volume", "price_open")
            if all(hasattr(r, n) for n in needed):
                out.append(r)
        if len(out) != len(rows):
            logger.warning(
                "%d of %d position row(s) could not be margined: they are missing "
                "symbol/action/volume/price_open", len(rows) - len(out), len(rows),
            )
        return out

    async def _open_positions(self) -> List[Any]:
        repo = self.position_repo
        for name in ("get_open_positions", "get_all_open"):
            method = getattr(repo, name, None)
            if method is not None:
                return list(await method())
        raise TypeError(
            f"{type(repo).__name__} exposes no way to list open positions; "
            "the valuation sweep cannot run"
        )

    def _price_for(self, symbol: str):
        """Best (bid, ask) we currently hold for a symbol, or None.

        Never invents one: an equity computed from a made-up price is worse than a
        stale equity, because a stale number is at least a real number from a real
        moment, and it is stamped with when.
        """
        if not symbol:
            return None
        tick = None
        getter = getattr(self.market_data_engine, "get_latest_tick", None)
        if getter is not None:
            try:
                tick = getter(symbol)
            except Exception:  # noqa: BLE001
                tick = None
        if tick is None:
            ticks = getattr(self.market_data_engine, "ticks", None)
            if isinstance(ticks, dict):
                tick = ticks.get(symbol) or ticks.get(symbol.upper())
        if tick is None:
            return None
        if isinstance(tick, dict):
            bid, ask = tick.get("bid"), tick.get("ask")
        else:
            bid, ask = getattr(tick, "bid", None), getattr(tick, "ask", None)
        if bid is None or ask is None:
            return None
        try:
            return Decimal(str(bid)), Decimal(str(ask))
        except (ArithmeticError, ValueError, TypeError):
            return None

    async def _symbol(self, name: str):
        if not name or self.symbol_repo is None:
            return None
        try:
            return await self.symbol_repo.find_by_name(name)
        except Exception:  # noqa: BLE001
            return None

    async def start(self) -> None:
        """Run once soon after boot, then on a timer."""
        if self._running:
            return
        self._running = True
        self._task = asyncio.create_task(self._loop())
        logger.info("ValuationService started (first sweep shortly, then every %.0fs)",
                    self.interval_s)

    async def _loop(self) -> None:
        # Give the feed a moment to deliver before the first sweep, otherwise the
        # first pass after every boot skips everything for want of a price.
        try:
            await asyncio.sleep(min(15.0, self.interval_s))
            while self._running:
                await self.revalue_all()
                await asyncio.sleep(self.interval_s)
        except asyncio.CancelledError:
            logger.info("ValuationService stopped")

    async def stop(self) -> None:
        self._running = False
        if self._task is not None and not self._task.done():
            self._task.cancel()
            try:
                await self._task
            except (asyncio.CancelledError, Exception):  # noqa: BLE001
                pass
        self._task = None


class ReconciliationService:
    """Compare our book against the venue's and persist what disagrees. M12."""

    def __init__(self, *, position_repo, break_repo, engine: Optional[ReconciliationEngine] = None,
                 gateway=None, hedged_symbols: Optional[List[str]] = None,
                 event_bus=None, venue_name: str = "LP") -> None:
        self.position_repo = position_repo
        self.break_repo = break_repo
        self.engine = engine or ReconciliationEngine(
            hedged_symbols=(hedged_symbols or []))
        if hedged_symbols:
            self.engine.hedged_symbols = {s.upper() for s in hedged_symbols}
        self.gateway = gateway
        self.event_bus = event_bus
        self.venue_name = venue_name

    async def run(self) -> ReconciliationRun:
        """One reconciliation pass. Never raises: a sweep that dies on a venue
        outage is worse than one that reports the outage as a break."""
        started = datetime.now(timezone.utc)
        run = ReconciliationRun(started_at=started, venue=self.venue_name)

        theirs, err = await self._venue_positions()
        if err is not None:
            run.error = err
            run.finished_at = datetime.now(timezone.utc)
            logger.error("reconciliation could not read the venue book: %s", err)
            return run

        ours = await self._our_positions()
        run.our_positions = len(ours)
        run.venue_positions = len(theirs)

        found = self.engine.compare(ours, theirs, now=started)
        run.breaks = found

        identities = []
        for brk in found:
            identities.append(brk.identity)
            stored = await self.break_repo.upsert(brk)
            run.breaks[found.index(brk)] = stored

        # Ageing: how many of these were already open before this run?
        open_now = await self.break_repo.find_open()
        ids_now = {b.identity for b in open_now}
        run.recurring = sum(1 for b in open_now
                            if b.occurrences > 1 and b.identity in ids_now)

        cleared = await self.break_repo.auto_clear(
            identities, "no longer present in the %s reconciliation run" % self.venue_name)
        if cleared:
            run.cleared = [f"{cleared} break(s) auto-resolved"]

        run.finished_at = datetime.now(timezone.utc)
        await self._publish(run)
        self._log(run)
        return run

    async def _our_positions(self) -> List[SidePosition]:
        repo = self.position_repo
        rows: List[Any] = []
        for name in ("get_open_positions", "get_all_open"):
            method = getattr(repo, name, None)
            if method is not None:
                rows = list(await method())
                break
        out = []
        for p in rows:
            sp = SidePosition.from_local(p)
            login = getattr(p, "account_login", None)
            if login is not None:
                # SidePosition is frozen (it is compared and hashed by identity), so
                # the account reference is carried by rebuilding, not by assignment.
                from dataclasses import replace as _replace
                sp = _replace(sp, raw={"account_login": login})
            out.append(sp)
        return out

    async def _venue_positions(self):
        """(positions, error). An adapter that cannot report its book is an error,
        not an empty list - "no breaks" and "could not look" must not print the
        same thing. That is the exact confusion M5 fixed on /account/positions."""
        if self.gateway is None:
            return [], "no liquidity gateway is configured; nothing to reconcile against"
        reader = getattr(self.gateway, "positions", None)
        if reader is None:
            return [], (
                f"{type(self.gateway).__name__} cannot report the venue's positions "
                "(no positions() and no drop-copy). Reconciliation is unavailable "
                "for this adapter rather than clean."
            )
        try:
            rows = await reader()
        except Exception as exc:  # noqa: BLE001
            return [], f"{type(exc).__name__}: {exc}"
        return [SidePosition.from_venue(r, venue=self.venue_name) for r in (rows or [])], None

    async def resolve_unknown_hedges(self, order_repo) -> int:
        """Ask the venue about orders M11 left in HEDGE_STATE_UNKNOWN.

        M11 deliberately neither books nor rejects those: the hedge may or may not
        exist. This is the step that finds out. An order whose venue position now
        exists gets booked; one whose venue side is confirmed absent gets rejected
        and its margin released. Anything still ambiguous stays open and becomes an
        UNKNOWN_HEDGE break, so it ages visibly instead of holding margin silently.
        """
        finder = getattr(order_repo, "find_unresolved_hedges", None)
        if finder is None:
            logger.debug("order repository has no find_unresolved_hedges(); "
                         "unknown-hedge resolution is not wired")
            return 0
        try:
            orders = list(await finder())
        except Exception as exc:  # noqa: BLE001
            logger.error("could not list unresolved hedges: %s", exc)
            return 0
        if not orders:
            return 0
        logger.info("%d order(s) are still in an unknown hedge state", len(orders))
        for o in orders:
            await self.break_repo.upsert(ReconciliationBreak(
                break_id="", kind=BreakKind.UNKNOWN_HEDGE, severity=Severity.HIGH,
                symbol=str(getattr(o, "symbol", "") or "").upper(),
                detail=(
                    f"order {getattr(o, 'ticket_id', '?')} was sent to the venue and "
                    f"its outcome was never learned. Margin is still held. Resolve "
                    f"against the venue before retrying - this gateway has no "
                    f"idempotency key, so a blind retry could double-hedge."
                ),
                our_key=str(getattr(o, "ticket_id", "")),
                our_volume=getattr(getattr(o, "volume_current", None), "value", None),
                account_login=getattr(o, "account_login", None),
            ))
        return len(orders)

    async def _publish(self, run: ReconciliationRun) -> None:
        if self.event_bus is None:
            return
        try:
            from core.events.domain_events import DomainEvent, EventType
            await self.event_bus.publish(DomainEvent(
                event_type=EventType.RISK_STATUS_UPDATED,
                aggregate_id="reconciliation",
                payload={
                    "venue": run.venue,
                    "our_positions": run.our_positions,
                    "venue_positions": run.venue_positions,
                    "breaks": len(run.breaks),
                    "by_severity": run.by_severity(),
                    "error": run.error,
                    "started_at": run.started_at.isoformat(),
                },
            ))
        except Exception as exc:  # noqa: BLE001
            logger.error("could not publish the reconciliation result: %s", exc)

    def _log(self, run: ReconciliationRun) -> None:
        if run.error:
            return
        counts = run.by_severity()
        if run.clean:
            logger.info(
                "reconciliation clean: our %d position(s) match the venue's %d",
                run.our_positions, run.venue_positions)
        else:
            logger.warning(
                "reconciliation found %d break(s): CRITICAL=%d HIGH=%d MEDIUM=%d LOW=%d",
                len(run.breaks), counts["CRITICAL"], counts["HIGH"],
                counts["MEDIUM"], counts["LOW"])
