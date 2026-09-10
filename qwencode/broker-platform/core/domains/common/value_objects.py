from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from typing import Union

@dataclass(frozen=True)
class Money:
    """
    Value Object for Currency.
    Ensures no floating point math occurs on balances.

    CRITICAL FIX: Negative amounts ARE allowed to represent losses,
    withdrawals, fees, and commissions in double-entry accounting.
    The Account Balance logic (not this VO) prevents negative equity.
    """
    amount: Decimal
    currency: str = "USD"

    def __post_init__(self):
        if not isinstance(self.amount, Decimal):
            object.__setattr__(self, 'amount', Decimal(str(self.amount)))
        # REMOVED: if self.amount < 0: raise ValueError(...)
        # Negative money is valid for accounting entries

    def __add__(self, other: 'Money') -> 'Money':
        if self.currency != other.currency:
            raise ValueError("Cannot add money with different currencies")
        return Money(self.amount + other.amount, self.currency)

    def __sub__(self, other: 'Money') -> 'Money':
        if self.currency != other.currency:
            raise ValueError("Cannot subtract money with different currencies")
        return Money(self.amount - other.amount, self.currency)

    def __neg__(self) -> 'Money':
        """Allows negation: -Money(50) = Money(-50)"""
        return Money(-self.amount, self.currency)

@dataclass(frozen=True)
class Price:
    """
    Value Object for Asset Price.
    Handles tick precision implicitly via string conversion.
    """
    value: Decimal

    def __post_init__(self):
        if not isinstance(self.value, Decimal):
            object.__setattr__(self, 'value', Decimal(str(self.value)))
        if self.value <= 0:
            raise ValueError("Price must be positive")

@dataclass(frozen=True)
class Volume:
    """
    Value Object for Trade Volume (Lots).
    Enforces minimum lot steps (e.g., 0.01).
    """
    value: Decimal

    def __post_init__(self):
        if not isinstance(self.value, Decimal):
            object.__setattr__(self, 'value', Decimal(str(self.value)))
        if self.value < 0:
            raise ValueError("Volume cannot be negative")

    def is_valid_step(self, step: Decimal) -> bool:
        """Checks if volume aligns with symbol step (e.g., 0.01)"""
        remainder = self.value % step
        # Allow for minor decimal precision issues
        return remainder == 0 or abs(remainder - step) < Decimal('1E-8')
