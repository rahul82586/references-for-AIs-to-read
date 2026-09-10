"""Holiday entity (IMTConHoliday)."""
from dataclasses import dataclass, field
from datetime import date, time, datetime, timezone
from typing import List, Optional
import uuid

from .enums import HolidayMode


@dataclass
class Holiday:
    """
    Holiday configuration (IMTConHoliday).
    
    Holidays can apply to:
    - All symbols (if symbols list is empty)
    - Specific symbols (if symbols list is populated)
    - Symbol groups (e.g., "FOREX:*", "METALS:*")
    
    Year = 0 means the holiday repeats every year.
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    description: str = ""
    mode: HolidayMode = HolidayMode.ENABLED
    
    # Date
    year: int = 0  # 0 = every year, otherwise specific year (e.g., 2024)
    month: int = 1  # 1-12
    day: int = 1  # 1-31
    
    # Work times (when market closes/opens)
    work_from: time = time(0, 0)  # When holiday starts
    work_to: time = time(23, 59)  # When holiday ends
    
    # Symbol applicability
    symbols: List[str] = field(default_factory=list)  # Empty = all symbols
    
    # Metadata
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    
    def applies_to_date(self, check_date: date) -> bool:
        """Check if this holiday applies to a specific date."""
        if self.mode != HolidayMode.ENABLED:
            return False
        
        # Check month and day
        if check_date.month != self.month or check_date.day != self.day:
            return False
        
        # Check year (0 = every year)
        if self.year != 0 and check_date.year != self.year:
            return False
        
        return True
    
    def applies_to_symbol(self, symbol_name: str) -> bool:
        """Check if this holiday applies to a specific symbol."""
        # Empty list = applies to all symbols
        if not self.symbols:
            return True
        
        # Check exact match or wildcard pattern
        for pattern in self.symbols:
            if pattern.endswith("*"):
                prefix = pattern[:-1]
                if symbol_name.startswith(prefix):
                    return True
            elif symbol_name == pattern:
                return True
        
        return False
    
    def is_active_at(self, check_datetime: datetime) -> bool:
        """Check if holiday is active at a specific datetime."""
        if not self.applies_to_date(check_datetime.date()):
            return False
        
        check_time = check_datetime.time()
        return self.work_from <= check_time <= self.work_to
    
    def to_dict(self):
        """Convert to dictionary."""
        return {
            "id": self.id,
            "description": self.description,
            "mode": self.mode.name,
            "year": self.year,
            "month": self.month,
            "day": self.day,
            "work_from": self.work_from.isoformat(),
            "work_to": self.work_to.isoformat(),
            "symbols": self.symbols,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }