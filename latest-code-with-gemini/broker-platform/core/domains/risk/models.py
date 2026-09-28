from enum import Enum
from dataclasses import dataclass, field
from decimal import Decimal
from datetime import datetime, timezone
from typing import List


class RiskStatus(Enum):
    """Enumeration of account risk states."""
    NORMAL = "NORMAL"
    MARGIN_CALL = "MARGIN_CALL"
    STOP_OUT_PENDING = "STOP_OUT_PENDING"
    STOPPED_OUT = "STOPPED_OUT"
    BLOCKED = "BLOCKED"


@dataclass
class MarginSnapshot:
    """
    Real-time snapshot of an account's margin state.
    Immutable once created to ensure consistency during risk checks.
    """
    account_login: str
    balance: Decimal
    equity: Decimal  # Balance + Unrealized PnL
    margin_used: Decimal
    margin_free: Decimal
    margin_level: Decimal  # (Equity / Margin Used) × 100, or ∞ if no positions
    status: RiskStatus
    calculated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def __post_init__(self):
        """Ensure all financial values are Decimal."""
        for field_name in ['balance', 'equity', 'margin_used', 'margin_free', 'margin_level']:
            value = getattr(self, field_name)
            if not isinstance(value, Decimal):
                object.__setattr__(self, field_name, Decimal(str(value)))
