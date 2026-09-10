"""Instrument services for session and holiday checking."""
from datetime import datetime, timezone, date
from typing import List, Optional
from decimal import Decimal

from .symbol import Symbol
from .holiday import Holiday


class SessionService:
    """Service for checking trading and quote sessions."""
    
    def __init__(self, holiday_repo):
        self.holiday_repo = holiday_repo
    
    async def is_market_open(
        self,
        symbol: Symbol,
        check_datetime: Optional[datetime] = None
    ) -> bool:
        """
        Check if market is open for a symbol at a given datetime.
        
        Checks:
        1. Symbol trade mode (not DISABLED)
        2. Trade session active
        3. No active holiday
        """
        if check_datetime is None:
            check_datetime = datetime.now(timezone.utc)
        
        # Check trade mode
        if symbol.trade_mode == "DISABLED":
            return False
        
        # Check trade session
        if not symbol.is_trade_session_active(check_datetime):
            return False
        
        # Check holidays
        holidays = await self.holiday_repo.get_active_holidays(check_datetime)
        for holiday in holidays:
            if holiday.applies_to_symbol(symbol.name):
                if holiday.is_active_at(check_datetime):
                    return False
        
        return True
    
    async def get_next_session_open(
        self,
        symbol: Symbol,
        from_datetime: Optional[datetime] = None
    ) -> Optional[datetime]:
        """Get the next time a trading session opens."""
        # Simplified - in production, iterate through days and sessions
        # to find the next open time
        pass


class HolidayService:
    """Service for managing holidays."""
    
    def __init__(self, holiday_repo):
        self.holiday_repo = holiday_repo
    
    async def is_holiday(
        self,
        symbol_name: str,
        check_datetime: Optional[datetime] = None
    ) -> bool:
        """Check if a symbol is on holiday at a given datetime."""
        if check_datetime is None:
            check_datetime = datetime.now(timezone.utc)
        
        holidays = await self.holiday_repo.get_active_holidays(check_datetime)
        for holiday in holidays:
            if holiday.applies_to_symbol(symbol_name):
                if holiday.is_active_at(check_datetime):
                    return True
        
        return False
    
    async def get_holidays_for_symbol(
        self,
        symbol_name: str,
        year: int
    ) -> List[Holiday]:
        """Get all holidays for a symbol in a given year."""
        return await self.holiday_repo.get_holidays_for_symbol(symbol_name, year)