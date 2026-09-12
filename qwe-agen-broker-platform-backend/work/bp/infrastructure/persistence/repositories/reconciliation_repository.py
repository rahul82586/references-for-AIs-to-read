"""Break storage, and the valuation sweep that D9 says was missing.

Two repositories in one module because they are the two halves of the same
question - "do our numbers match reality?" - and both are read by `cli sync`.

`SqlReconciliationRepository` persists breaks with dedupe on `identity`, so a
difference found on six consecutive sweeps is ONE row with `occurrences=6` and a
`first_seen` six sweeps old. That age is the useful signal; six identical rows
are noise an operator will learn to ignore, which is how breaks survive.
"""
from __future__ import annotations

import logging
import uuid
from datetime import datetime, timezone
from decimal import Decimal
from typing import Any, List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.domains.reconciliation.engine import (
    BreakStatus,
    ReconciliationBreak,
    Severity,
)
from infrastructure.persistence.reconciliation_models import (
    ReconciliationBreakModel,
    break_to_db,
    db_to_break,
)

logger = logging.getLogger(__name__)


class SqlReconciliationRepository:
    """PostgreSQL/SQLite storage for reconciliation breaks."""

    def __init__(self, session_factory=None) -> None:
        self.session_factory = session_factory

    async def upsert(self, brk: ReconciliationBreak,
                     session: Optional[AsyncSession] = None) -> ReconciliationBreak:
        """Insert, or age the existing open break with the same identity.

        Returns the break as stored, so the caller sees the real first_seen and
        occurrence count rather than the values it constructed.
        """
        identity = brk.identity
        now = datetime.now(timezone.utc)

        async def _do(sess: AsyncSession) -> ReconciliationBreak:
            existing = (await sess.execute(
                select(ReconciliationBreakModel)
                .where(ReconciliationBreakModel.identity == identity)
                .where(ReconciliationBreakModel.status == BreakStatus.OPEN.value)
            )).scalars().first()

            if existing is None:
                brk.break_id = brk.break_id or uuid.uuid4().hex
                brk.first_seen = brk.first_seen or now
                brk.last_seen = now
                brk.occurrences = max(1, brk.occurrences)
                sess.add(break_to_db(brk))
                return brk

            # Age it. The detail and volumes may have moved (a volume mismatch can
            # grow), so refresh those, but keep first_seen and break_id: this is
            # the same break getting older, not a new one.
            existing.severity = brk.severity.value
            existing.detail = brk.detail
            existing.our_volume = brk.our_volume
            existing.venue_volume = brk.venue_volume
            existing.our_price = brk.our_price
            existing.venue_price = brk.venue_price
            existing.account_login = brk.account_login
            existing.occurrences = int(existing.occurrences or 1) + 1
            existing.last_seen = now
            existing.updated_at = now
            brk.break_id = existing.break_id
            brk.first_seen = existing.first_seen
            brk.occurrences = existing.occurrences
            return brk

        if session is not None:
            return await _do(session)
        async with self.session_factory() as sess:
            out = await _do(sess)
            await sess.commit()
            return out

    async def find_open(self, *, severity: Optional[Severity] = None,
                        symbol: Optional[str] = None) -> List[ReconciliationBreak]:
        async with self.session_factory() as sess:
            stmt = select(ReconciliationBreakModel).where(
                ReconciliationBreakModel.status == BreakStatus.OPEN.value)
            if severity is not None:
                stmt = stmt.where(ReconciliationBreakModel.severity == severity.value)
            if symbol:
                stmt = stmt.where(ReconciliationBreakModel.symbol == symbol.upper())
            stmt = stmt.order_by(ReconciliationBreakModel.first_seen)
            return [db_to_break(m) for m in (await sess.execute(stmt)).scalars().all()]

    async def find_by_id(self, break_id: str) -> Optional[ReconciliationBreak]:
        async with self.session_factory() as sess:
            m = (await sess.execute(
                select(ReconciliationBreakModel)
                .where(ReconciliationBreakModel.break_id == break_id)
            )).scalars().first()
            return db_to_break(m) if m is not None else None

    async def resolve(self, break_id: str, resolution: str,
                      status: BreakStatus = BreakStatus.RESOLVED) -> bool:
        """Close a break with a human-readable resolution. Never deletes: the
        record of what diverged and what was done about it is the audit trail."""
        async with self.session_factory() as sess:
            m = (await sess.execute(
                select(ReconciliationBreakModel)
                .where(ReconciliationBreakModel.break_id == break_id)
            )).scalars().first()
            if m is None:
                return False
            m.status = status.value
            m.resolution = resolution
            m.resolved_at = datetime.now(timezone.utc)
            m.updated_at = m.resolved_at
            await sess.commit()
            return True

    async def auto_clear(self, identities: List[str], note: str) -> int:
        """Resolve open breaks that this run did NOT find - they fixed themselves.

        Auto-clearing matters as much as raising: a break that silently stops
        being reported is indistinguishable from one nobody looked at, and an
        operator who cannot tell those apart stops trusting the report.
        """
        if not identities:
            return 0
        async with self.session_factory() as sess:
            rows = (await sess.execute(
                select(ReconciliationBreakModel)
                .where(ReconciliationBreakModel.status == BreakStatus.OPEN.value)
            )).scalars().all()
            cleared = 0
            now = datetime.now(timezone.utc)
            for m in rows:
                if m.identity in identities:
                    continue
                m.status = BreakStatus.RESOLVED.value
                m.resolution = note
                m.resolved_at = now
                m.updated_at = now
                cleared += 1
            if cleared:
                await sess.commit()
            return cleared

    async def counts(self) -> dict:
        """One row per (status, severity) for a dashboard or `cli status`."""
        async with self.session_factory() as sess:
            rows = (await sess.execute(select(ReconciliationBreakModel))).scalars().all()
        out: dict = {}
        for m in rows:
            key = f"{m.status}/{m.severity}"
            out[key] = out.get(key, 0) + 1
        return out


class InMemoryReconciliationRepository(SqlReconciliationRepository):
    """The same contract without a database, for tests and the harness."""

    def __init__(self) -> None:
        super().__init__(session_factory=None)
        self.rows: dict = {}

    async def upsert(self, brk, session=None):
        identity = brk.identity
        now = datetime.now(timezone.utc)
        existing = next((b for b in self.rows.values()
                         if b.identity == identity
                         and b.status is BreakStatus.OPEN), None)
        if existing is None:
            brk.break_id = brk.break_id or uuid.uuid4().hex
            brk.first_seen = brk.first_seen or now
            brk.last_seen = now
            brk.occurrences = max(1, brk.occurrences)
            self.rows[brk.break_id] = brk
            return brk
        existing.severity = brk.severity
        existing.detail = brk.detail
        existing.our_volume = brk.our_volume
        existing.venue_volume = brk.venue_volume
        existing.our_price = brk.our_price
        existing.venue_price = brk.venue_price
        existing.occurrences += 1
        existing.last_seen = now
        brk.break_id = existing.break_id
        brk.first_seen = existing.first_seen
        brk.occurrences = existing.occurrences
        return brk

    async def find_open(self, *, severity=None, symbol=None):
        out = [b for b in self.rows.values() if b.status is BreakStatus.OPEN]
        if severity is not None:
            out = [b for b in out if b.severity is severity]
        if symbol:
            out = [b for b in out if b.symbol == symbol.upper()]
        return sorted(out, key=lambda b: b.first_seen)

    async def find_by_id(self, break_id):
        return self.rows.get(break_id)

    async def resolve(self, break_id, resolution, status=BreakStatus.RESOLVED):
        b = self.rows.get(break_id)
        if b is None:
            return False
        b.status = status
        b.resolution = resolution
        b.resolved_at = datetime.now(timezone.utc)
        return True

    async def auto_clear(self, identities, note):
        cleared = 0
        for b in list(self.rows.values()):
            if b.status is BreakStatus.OPEN and b.identity not in identities:
                b.status = BreakStatus.RESOLVED
                b.resolution = note
                b.resolved_at = datetime.now(timezone.utc)
                cleared += 1
        return cleared

    async def counts(self):
        out: dict = {}
        for b in self.rows.values():
            key = f"{b.status.value}/{b.severity.value}"
            out[key] = out.get(key, 0) + 1
        return out
