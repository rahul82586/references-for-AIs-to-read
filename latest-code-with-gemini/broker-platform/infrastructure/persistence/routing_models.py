"""MT5 routing rule storage (M8).

The wire record is the source of truth: `record` holds the exact ConfigRouting
JSON (so re-export stays byte-identical and every condition/action code the
codec decoded is preserved), and the typed columns mirror the hot fields for
listing, ordering and debugging without decoding JSON.

Rules evaluate in `position` order — MT5's table order, first match wins.
"""
from sqlalchemy import BigInteger, Boolean, Column, Integer, String
from sqlalchemy.dialects.postgresql import JSONB

from infrastructure.persistence.database import Base


class Mt5RoutingRuleModel(Base):
    """One row of the MT5 routing table (ConfigRouting record)."""

    __tablename__ = "mt5_routing_rules"

    name = Column(String(128), primary_key=True)
    #: evaluation order; MT5 uses the record order in the export
    position = Column(Integer, nullable=False, default=0)
    #: wire Mode: 0 = disabled, nonzero = enabled
    mode = Column(Integer, nullable=False, default=1)
    enabled = Column(Boolean, nullable=False, default=True)
    #: EnRouteAction code (0-4 delay/clear, 1001-1007 dealer/reject/requote/confirm/cancel)
    action = Column(Integer, nullable=False, default=0)
    request_mask = Column(BigInteger, nullable=False, default=0)
    type_mask = Column(Integer, nullable=False, default=0)
    #: the verbatim ConfigRouting record
    record = Column(JSONB, nullable=False, default=dict)
