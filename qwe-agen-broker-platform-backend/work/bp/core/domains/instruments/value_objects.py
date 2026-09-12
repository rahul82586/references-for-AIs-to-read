"""Instruments domain value objects."""
from dataclasses import dataclass, field
from datetime import time
from decimal import Decimal
from typing import List, Optional
import uuid

from .enums import HolidayMode


@dataclass
class TradingSession:
    """
    Trading session for a symbol (IMTConSymbolSession).
    
    MT5 stores SessionsQuotes / SessionsTrades as a 7-element array indexed
    SUNDAY-FIRST: 0=Sunday .. 6=Saturday. This is NOT Python's weekday(), where
    0=Monday. infrastructure.mt5.wire.WEEKDAY_SUNDAY_FIRST is the authority.
    Each day can have multiple sessions (e.g. morning + evening).
    Times are stored as minutes from midnight (0..1440) for efficiency.
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    day_of_week: int = 0  # MT5 order: 0=Sunday .. 6=Saturday
    open_minutes: int = 0  # Minutes from midnight (e.g., 60 = 01:00)
    close_minutes: int = 1440  # Minutes from midnight (1440 = 24:00)

    @property
    def open_time(self) -> time:
        """Convert open_minutes to a time object."""
        return time(self.open_minutes // 60, self.open_minutes % 60)
    
    @property
    def close_time(self) -> time:
        """Convert close_minutes to a time object.

        1440 means end of day, which time() cannot represent, so it clamps to
        23:59:59. Callers comparing against a bare midnight should compare
        close_minutes directly rather than close_time.
        """
        hours = self.close_minutes // 60
        minutes = self.close_minutes % 60
        if hours >= 24:
            return time(23, 59, 59)
        return time(hours, minutes)

    def is_within(self, check_time: time) -> bool:
        """Check whether a time falls inside this session."""
        # Overnight sessions (e.g. 22:00 to 06:00) wrap past midnight.
        if self.open_minutes > self.close_minutes:
            return check_time >= self.open_time or check_time <= self.close_time
        return self.open_time <= check_time <= self.close_time


@dataclass
class QuoteSession:
    """
    Quote session (when price updates are received).
    Can be different from trading sessions.
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    day_of_week: int = 0  # MT5 order: 0=Sunday .. 6=Saturday
    open_minutes: int = 0
    close_minutes: int = 1440

    @property
    def open_time(self) -> time:
        return time(self.open_minutes // 60, self.open_minutes % 60)

    @property
    def close_time(self) -> time:
        hours = self.close_minutes // 60
        minutes = self.close_minutes % 60
        if hours >= 24:
            return time(23, 59, 59)
        return time(hours, minutes)


@dataclass
class MarginRates:
    """
    Margin rates per order direction (IMTConSymbol margin rates).
    
    MT5 allows different margin rates for:
    - BUY (market orders)
    - SELL (market orders)
    - BUY_LIMIT, SELL_LIMIT (limit orders)
    - BUY_STOP, SELL_STOP (stop orders)
    - BUY_STOP_LIMIT, SELL_STOP_LIMIT (stop-limit orders)
    """
    initial_buy: Decimal = field(default_factory=lambda: Decimal('1.0'))
    initial_sell: Decimal = field(default_factory=lambda: Decimal('1.0'))
    initial_buy_limit: Decimal = field(default_factory=lambda: Decimal('1.0'))
    initial_sell_limit: Decimal = field(default_factory=lambda: Decimal('1.0'))
    initial_buy_stop: Decimal = field(default_factory=lambda: Decimal('1.0'))
    initial_sell_stop: Decimal = field(default_factory=lambda: Decimal('1.0'))
    initial_buy_stop_limit: Decimal = field(default_factory=lambda: Decimal('1.0'))
    initial_sell_stop_limit: Decimal = field(default_factory=lambda: Decimal('1.0'))
    
    maintenance_buy: Decimal = field(default_factory=lambda: Decimal('1.0'))
    maintenance_sell: Decimal = field(default_factory=lambda: Decimal('1.0'))
    maintenance_buy_limit: Decimal = field(default_factory=lambda: Decimal('1.0'))
    maintenance_sell_limit: Decimal = field(default_factory=lambda: Decimal('1.0'))
    maintenance_buy_stop: Decimal = field(default_factory=lambda: Decimal('1.0'))
    maintenance_sell_stop: Decimal = field(default_factory=lambda: Decimal('1.0'))
    maintenance_buy_stop_limit: Decimal = field(default_factory=lambda: Decimal('1.0'))
    maintenance_sell_stop_limit: Decimal = field(default_factory=lambda: Decimal('1.0'))
    
    def get_initial_rate(self, order_type: str) -> Decimal:
        """Get initial margin rate for an order type."""
        rates = {
            "BUY": self.initial_buy,
            "SELL": self.initial_sell,
            "BUY_LIMIT": self.initial_buy_limit,
            "SELL_LIMIT": self.initial_sell_limit,
            "BUY_STOP": self.initial_buy_stop,
            "SELL_STOP": self.initial_sell_stop,
            "BUY_STOP_LIMIT": self.initial_buy_stop_limit,
            "SELL_STOP_LIMIT": self.initial_sell_stop_limit,
        }
        return rates.get(order_type, Decimal('1.0'))
    
    def get_maintenance_rate(self, position_side: str) -> Decimal:
        """Get maintenance margin rate for a position side."""
        if position_side in ["BUY", "LONG"]:
            return self.maintenance_buy
        elif position_side in ["SELL", "SHORT"]:
            return self.maintenance_sell
        return Decimal('1.0')