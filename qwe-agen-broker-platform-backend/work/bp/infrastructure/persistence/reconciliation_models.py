"""The reconciliation_breaks table and its mappers.

Kept in its own module rather than folded into db_models.py: a break is an
operational record with its own lifecycle, and the M1 lesson about four competing
schemas applies just as much to where a model lives as to what columns it has.

JSONB renders as JSON on SQLite through the compile hook in
infrastructure/persistence/database.py, so create_tables() works on both.
"""
from __future__ import annotations

import uuid
from datetime import datetime, timezone
from decimal import Decimal
from typing import Any, Optional

from sqlalchemy import (
    BigInteger,
    Column,
    DateTime,
    Index,
    Integer,
    Numeric,
    String,
    Text,
    func,
)

from core.domains.reconciliation.engine import (
    BreakKind,
    BreakStatus,
    ReconciliationBreak,
    Severity,
)
from infrastructure.persistence.database import Base


class ReconciliationBreakModel(Base):
    __tablename__ = "reconciliation_breaks"

    break_id = Column(String(length=64), primary_key=True)
    identity = Column(String(length=512), nullable=False, index=True)
    kind = Column(String(length=40), nullable=False)
    severity = Column(String(length=16), nullable=False, default="MEDIUM")
    status = Column(String(length=16), nullable=False, default="OPEN")
    symbol = Column(String(length=64), nullable=False, default="")
    venue = Column(String(length=64), nullable=False, default="")
    detail = Column(Text, nullable=False, default="")
    our_key = Column(String(length=128), nullable=True)
    venue_key = Column(String(length=128), nullable=True)
    our_volume = Column(Numeric, nullable=True)
    venue_volume = Column(Numeric, nullable=True)
    our_price = Column(Numeric, nullable=True)
    venue_price = Column(Numeric, nullable=True)
    account_login = Column(BigInteger, nullable=True)
    occurrences = Column(Integer, nullable=False, default=1)
    first_seen = Column(DateTime(timezone=True), nullable=False)
    last_seen = Column(DateTime(timezone=True), nullable=True)
    resolution = Column(Text, nullable=True)
    resolved_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False,
                        default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), nullable=False,
                        default=lambda: datetime.now(timezone.utc),
                        onupdate=lambda: datetime.now(timezone.utc))

    __table_args__ = (
        Index("ix_recon_breaks_status", "status", "severity"),
        Index("ix_recon_breaks_symbol", "symbol"),
    )


def _dec(value: Any) -> Optional[Decimal]:
    if value is None or value == "":
        return None
    try:
        return Decimal(str(value))
    except (ArithmeticError, ValueError, TypeError):
        return None


def break_to_db(brk: ReconciliationBreak) -> ReconciliationBreakModel:
    now = datetime.now(timezone.utc)
    return ReconciliationBreakModel(
        break_id=brk.break_id or uuid.uuid4().hex,
        identity=brk.identity,
        kind=brk.kind.value,
        severity=brk.severity.value,
        status=brk.status.value,
        symbol=brk.symbol or "",
        venue="",
        detail=brk.detail or "",
        our_key=brk.our_key,
        venue_key=brk.venue_key,
        our_volume=brk.our_volume,
        venue_volume=brk.venue_volume,
        our_price=brk.our_price,
        venue_price=brk.venue_price,
        account_login=brk.account_login,
        occurrences=brk.occurrences,
        first_seen=brk.first_seen or now,
        last_seen=brk.last_seen or now,
        resolution=brk.resolution,
        resolved_at=brk.resolved_at,
        created_at=now,
        updated_at=now,
    )


def db_to_break(model: ReconciliationBreakModel) -> ReconciliationBreak:
    def _enum(cls, value, default):
        try:
            return cls(value)
        except ValueError:
            return default

    return ReconciliationBreak(
        break_id=model.break_id,
        kind=_enum(BreakKind, model.kind, BreakKind.UNKNOWN_HEDGE),
        severity=_enum(Severity, model.severity, Severity.MEDIUM),
        symbol=model.symbol or "",
        detail=model.detail or "",
        our_key=model.our_key,
        venue_key=model.venue_key,
        our_volume=_dec(model.our_volume),
        venue_volume=_dec(model.venue_volume),
        our_price=_dec(model.our_price),
        venue_price=_dec(model.venue_price),
        account_login=model.account_login,
        status=_enum(BreakStatus, model.status, BreakStatus.OPEN),
        first_seen=model.first_seen or datetime.now(timezone.utc),
        last_seen=model.last_seen,
        occurrences=int(model.occurrences or 1),
        resolution=model.resolution,
        resolved_at=model.resolved_at,
    )
