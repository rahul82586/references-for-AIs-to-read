from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional
from uuid import uuid4
from decimal import Decimal

from core.domains.common.value_objects import Money


class BalanceOperationType(Enum):
    """Mirrors MT5 balance operation types."""
    DEPOSIT = "DEPOSIT"
    WITHDRAWAL = "WITHDRAWAL"
    COMMISSION = "COMMISSION"
    SWAP = "SWAP"
    CORRECTION = "CORRECTION"
    BONUS = "BONUS"
    DEAL_PROFIT = "DEAL_PROFIT"
    DEAL_LOSS = "DEAL_LOSS"


@dataclass
class BalanceOperation:
    """
    Immutable record of a balance change.
    Every operation has a type, amount, and optional reference.
    """
    account_login: str
    operation_type: BalanceOperationType
    amount: Money
    balance_after: Money
    reference_id: Optional[str] = None
    comment: Optional[str] = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    operation_id: str = field(default_factory=lambda: f"OP_{uuid4().hex[:12]}")

    def __post_init__(self):
        """Ensure amount is Money type."""
        if not isinstance(self.amount, Money):
            raise ValueError("amount must be Money type")
        if not isinstance(self.balance_after, Money):
            raise ValueError("balance_after must be Money type")
