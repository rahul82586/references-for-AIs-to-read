# USER ------------


Complete the Instruments Domain (Symbols, Sessions, Holidays)
how it is in current broker-platform
and how it is in mt5.
i have provide few more files from sdk 
read all my broker-platform and the mt5 sdk 



# AI ---------------

## 📊 Current State Analysis

### Your Current `core/domains/instruments/models.py` (713 lines total, but instruments is ~100 lines)

```python
@dataclass
class TradingSession:
    start: time
    end: time
    day_of_week: int = 0  # 0=Monday, 6=Sunday

@dataclass
class Symbol:
    name: str
    path: str  # e.g., "Forex\EURUSD"
    tick_size: Decimal
    tick_value: Decimal
    contract_size: Decimal
    digits: int
    volume_min: Decimal
    volume_max: Decimal
    volume_step: Decimal
    margin_initial_percent: Decimal
    margin_maintenance_percent: Decimal
    sessions: List[TradingSession] = field(default_factory=list)
    is_trade_allowed: bool = True
    fill_mode: str = "FOK"
    
    def is_within_session(self, current_time: time) -> bool:
        # Simplified - doesn't handle day_of_week properly
        for session in self.sessions:
            if session.start <= current_time <= session.end:
                return True
        return False
```

### Critical Gaps vs MT5:

1. **❌ No separate Quote and Trade sessions** - MT5 has both, and they can be different
2. **❌ No multiple sessions per day** - Forex has weekend breaks, crypto is 24/7
3. **❌ No Holiday system** - MT5 has `IMTConHoliday` with year/month/day, work times, symbol applicability
4. **❌ No Calculation modes** - FOREX, CFD, FUTURES, OPTIONS, etc.
5. **❌ No Execution modes** - REQUEST, INSTANT, MARKET, EXCHANGE
6. **❌ No Filling flags** - FOK, IOC, RETURN
7. **❌ No margin rates per direction** - BUY/SELL/LIMIT/STOP all have different rates
8. **❌ No Swap modes** - POINTS, CURRENCY, INTEREST, etc.
9. **❌ No Base/Quote currency** - Critical for cross-currency PnL
10. **❌ No Trade modes** - DISABLED, LONGONLY, SHORTONLY, CLOSEONLY, FULL
11. **❌ No Stops/Freeze levels** - Minimum SL/TP distance
12. **❌ No Expiration handling** - GTC, DAY, SPECIFIED

---

## 🏗️ Complete MT5-Accurate Instruments Domain

I'll split this into **6 files** following the same pattern as accounts:

```
core/domains/instruments/
├── __init__.py
├── enums.py              # All enumerations
├── value_objects.py      # TradingSession, QuoteSession, Holiday
├── symbol.py             # Symbol entity
├── holiday.py            # Holiday entity
└── services.py           # Session checking, holiday checking
```

---

### 1. `core/domains/instruments/enums.py`

```python
"""Instruments domain enumerations (MT5-accurate)."""
from enum import Enum, IntFlag


class CalculationMode(Enum):
    """Symbol calculation modes (IMTConSymbol::EnCalcMode)."""
    FOREX = 0  # Standard forex
    CFD = 1  # Contract for difference
    FUTURES = 2  # Futures contracts
    OPTIONS = 3  # Options
    BONDS = 4  # Bonds
    STOCKS = 5  # Stocks
    INDICES = 6  # Stock indices
    CRYPTO = 7  # Cryptocurrencies
    METALS = 8  # Precious metals
    ENERGY = 9  # Energy commodities


class ExecutionMode(Enum):
    """Order execution modes (IMTConSymbol::EnExecutionMode)."""
    REQUEST = 0  # Manual dealer confirmation
    INSTANT = 1  # Instant execution with slippage
    MARKET = 2  # Market execution (no requotes)
    EXCHANGE = 3  # Exchange execution (CLOB)


class TradeMode(Enum):
    """Symbol trade modes (IMTConSymbol::EnTradeMode)."""
    DISABLED = 0  # Trading disabled
    LONGONLY = 1  # Only buy orders
    SHORTONLY = 2  # Only sell orders
    CLOSEONLY = 3  # Only close positions
    FULL = 4  # All operations allowed


class FillingFlags(IntFlag):
    """Order filling flags (IMTConSymbol::EnFillingFlags)."""
    NONE = 0x00000000
    FOK = 0x00000001  # Fill or Kill (all or nothing)
    IOC = 0x00000002  # Immediate or Cancel (partial fills OK)
    RETURN = 0x00000004  # Return remaining volume as pending order


class ExpirationFlags(IntFlag):
    """Order expiration flags (IMTConSymbol::EnExpirationFlags)."""
    NONE = 0x00000000
    GTC = 0x00000001  # Good till cancelled
    DAY = 0x00000002  # Good for the day
    SPECIFIED = 0x00000004  # Good till specified date
    SPECIFIED_DAY = 0x00000008  # Good till specified day


class GTCMode(Enum):
    """Good-till-cancelled modes (IMTConSymbol::EnGTCMode)."""
    TRADE = 0  # Based on trading sessions
    CALENDAR = 1  # Based on calendar days


class SwapMode(Enum):
    """Swap calculation modes (IMTConSymbol::EnSwapMode)."""
    DISABLED = 0  # No swaps
    POINTS = 1  # Swaps in points
    CURRENCY = 2  # Swaps in currency
    INTEREST_CURRENT = 3  # Interest on current balance
    INTEREST_OPEN = 4  # Interest on open balance
    REOPEN_CURRENT = 5  # Reopen at current price
    REOPEN_BID = 6  # Reopen at bid
    REOPEN_ASK = 7  # Reopen at ask


class OrderFlags(IntFlag):
    """Order permission flags (IMTConSymbol::EnOrderFlags)."""
    NONE = 0x00000000
    TRADE = 0x00000001  # Allow trading
    TRADE_EXPERT = 0x00000002  # Allow expert advisors
    TRADE_PLUGIN = 0x00000004  # Allow plugins


class OptionMode(Enum):
    """Option modes (IMTConSymbol::EnOptionMode)."""
    EUROPEAN = 0  # European-style (exercise at expiration only)
    AMERICAN = 1  # American-style (exercise anytime)


class HolidayMode(Enum):
    """Holiday modes (IMTConHoliday::EnHolidayMode)."""
    DISABLED = 0  # Holiday disabled
    ENABLED = 1  # Holiday enabled
```

---

### 2. `core/domains/instruments/value_objects.py`

```python
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
    
    MT5 stores sessions per day of week (0=Monday, 6=Sunday).
    Each day can have multiple sessions (e.g., morning + evening).
    Times are stored as minutes from midnight for efficiency.
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    open_minutes: int = 0  # Minutes from midnight (e.g., 60 = 01:00)
    close_minute: int = 1440  # Minutes from midnight (1440 = 24:00)
    
    @property
    def open_time(self) -> time:
        """Convert open_minutes to time object."""
        hours = self.open_minute // 60
        minutes = self.open_minute % 60
        return time(hours, minutes)
    
    @property
    def close_time(self) -> time:
        """Convert close_minute to time object."""
        hours = self.close_minute // 60
        minutes = self.close_minute % 60
        # Handle midnight (24:00 = 00:00)
        if hours == 24:
            return time(23, 59, 59)
        return time(hours, minutes)
    
    def is_within(self, check_time: time) -> bool:
        """Check if a time is within this session."""
        # Handle overnight sessions (e.g., 22:00 to 06:00)
        if self.open_minute > self.close_minute:
            return check_time >= self.open_time or check_time <= self.close_time
        return self.open_time <= check_time <= self.close_time


@dataclass
class QuoteSession:
    """
    Quote session (when price updates are received).
    Can be different from trading sessions.
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    open_minute: int = 0
    close_minute: int = 1440
    
    @property
    def open_time(self) -> time:
        hours = self.open_minute // 60
        minutes = self.open_minute % 60
        return time(hours, minutes)
    
    @property
    def close_time(self) -> time:
        hours = self.close_minute // 60
        minutes = self.close_minute % 60
        if hours == 24:
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
```

---

### 3. `core/domains/instruments/holiday.py`

```python
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
```

---

### 4. `core/domains/instruments/symbol.py`

```python
"""Symbol entity (IMTConSymbol)."""
from dataclasses import dataclass, field
from datetime import datetime, timezone, date, time
from decimal import Decimal
from typing import Any, Dict, List, Optional
import uuid

from core.domains.common.value_objects import Money
from .enums import (
    CalculationMode, ExecutionMode, TradeMode, FillingFlags,
    ExpirationFlags, GTCMode, SwapMode, OrderFlags, OptionMode
)
from .value_objects import TradingSession, QuoteSession, MarginRates


@dataclass
class Symbol:
    """
    Symbol entity - Tradable instrument configuration (IMTConSymbol).
    
    This is the BASE configuration. Group overrides (from GroupSymbolOverride)
    are merged on top of this to produce the final effective configuration.
    """
    # Identity
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""  # e.g., "EURUSD"
    path: str = ""  # e.g., "Forex\EURUSD"
    description: str = ""
    
    # Currency
    base_currency: str = "USD"  # e.g., "EUR" for EURUSD
    quote_currency: str = "USD"  # e.g., "USD" for EURUSD
    
    # Calculation mode
    calc_mode: CalculationMode = CalculationMode.FOREX
    
    # Pricing
    digits: int = 5  # Decimal places (5 for forex, 2 for stocks)
    tick_size: Decimal = field(default_factory=lambda: Decimal('0.00001'))
    tick_value: Decimal = field(default_factory=lambda: Decimal('1.0'))
    contract_size: Decimal = field(default_factory=lambda: Decimal('100000'))
    
    # Spread
    spread: int = 0  # Current spread in points
    spread_balance: int = 0  # Balance spread in points
    
    # Volume limits
    volume_min: Decimal = field(default_factory=lambda: Decimal('0.01'))
    volume_max: Decimal = field(default_factory=lambda: Decimal('100'))
    volume_step: Decimal = field(default_factory=lambda: Decimal('0.01'))
    volume_limit: Decimal = field(default_factory=lambda: Decimal('1000'))
    
    # Margin rates (per direction)
    margin_rates: MarginRates = field(default_factory=MarginRates)
    
    # Execution
    trade_mode: TradeMode = TradeMode.FULL
    exec_mode: ExecutionMode = ExecutionMode.MARKET
    gtc_mode: GTCMode = GTCMode.TRADE
    fill_flags: FillingFlags = FillingFlags.FOK
    expiration_flags: ExpirationFlags = ExpirationFlags.GTC
    order_flags: OrderFlags = OrderFlags.TRADE
    
    # Stops
    stops_level: int = 0  # Minimum SL/TP distance in points (0 = no limit)
    freeze_level: int = 0  # Freeze level for pending order modification
    
    # Swaps
    swap_mode: SwapMode = SwapMode.POINTS
    swap_long: Decimal = field(default_factory=lambda: Decimal('0'))
    swap_short: Decimal = field(default_factory=lambda: Decimal('0'))
    swap_3day: int = 3  # Triple swap day (0=Monday, 6=Sunday, default=Wednesday)
    swap_year_days: int = 365  # 360 or 365
    
    # Sessions (per day of week, 0=Monday, 6=Sunday)
    quote_sessions: Dict[int, List[QuoteSession]] = field(
        default_factory=lambda: {i: [] for i in range(7)}
    )
    trade_sessions: Dict[int, List[TradingSession]] = field(
        default_factory=lambda: {i: [] for i in range(7)}
    )
    
    # Validity period
    time_start: Optional[datetime] = None  # Symbol becomes valid
    time_expiration: Optional[datetime] = None  # Symbol expires
    
    # Options (if calc_mode == OPTIONS)
    option_mode: Optional[OptionMode] = None
    strike_price: Optional[Decimal] = None
    
    # Bonds (if calc_mode == BONDS)
    face_value: Optional[Decimal] = None
    face_value_currency: Optional[str] = None
    
    # Flags
    is_trade_allowed: bool = True
    
    # Metadata
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    
    def __post_init__(self):
        """Parse base/quote currency from name if not set."""
        if not self.base_currency or not self.quote_currency:
            self.base_currency, self.quote_currency = self._parse_currencies_from_name()
    
    def _parse_currencies_from_name(self) -> tuple[str, str]:
        """Parse base and quote currency from symbol name."""
        known_bases = {"XAU", "XAG", "WTI", "BRN", "BTC", "ETH", "SOL", "USDT", "USDC"}
        clean_name = self.name.upper().replace("/", "").replace("_", "").strip()
        
        for base in known_bases:
            if clean_name.startswith(base):
                quote = clean_name[len(base):]
                if not quote:
                    quote = "USD"
                return base, quote
        
        if len(clean_name) >= 6:
            return clean_name[:3], clean_name[3:6]
        
        return "USD", "USD"
    
    def is_quote_session_active(self, check_datetime: Optional[datetime] = None) -> bool:
        """Check if quote session is active at a given datetime."""
        if check_datetime is None:
            check_datetime = datetime.now(timezone.utc)
        
        day_of_week = check_datetime.weekday()  # 0=Monday, 6=Sunday
        check_time = check_datetime.time()
        
        sessions = self.quote_sessions.get(day_of_week, [])
        if not sessions:
            return False
        
        return any(session.open_time <= check_time <= session.close_time 
                   for session in sessions)
    
    def is_trade_session_active(self, check_datetime: Optional[datetime] = None) -> bool:
        """Check if trade session is active at a given datetime."""
        if check_datetime is None:
            check_datetime = datetime.now(timezone.utc)
        
        if not self.is_trade_allowed:
            return False
        
        if self.trade_mode == TradeMode.DISABLED:
            return False
        
        day_of_week = check_datetime.weekday()
        check_time = check_datetime.time()
        
        sessions = self.trade_sessions.get(day_of_week, [])
        if not sessions:
            return False
        
        return any(session.is_within(check_time) for session in sessions)
    
    def can_trade_direction(self, side: str) -> bool:
        """Check if a trade direction is allowed."""
        if self.trade_mode == TradeMode.DISABLED:
            return False
        if self.trade_mode == TradeMode.LONGONLY and side == "SELL":
            return False
        if self.trade_mode == TradeMode.SHORTONLY and side == "BUY":
            return False
        if self.trade_mode == TradeMode.CLOSEONLY:
            return False  # Only closing allowed
        return True
    
    def validate_volume(self, volume: Decimal) -> tuple[bool, str]:
        """Validate order volume."""
        if volume < self.volume_min:
            return False, f"Volume {volume} below minimum {self.volume_min}"
        if volume > self.volume_max:
            return False, f"Volume {volume} exceeds maximum {self.volume_max}"
        
        # Check volume step
        remainder = volume % self.volume_step
        if remainder != 0 and abs(remainder - self.volume_step) > Decimal('1E-8'):
            return False, f"Volume {volume} not a multiple of step {self.volume_step}"
        
        return True, "OK"
    
    def calculate_notional(self, volume: Decimal, price: Decimal) -> Decimal:
        """Calculate notional value of a trade."""
        return volume * self.contract_size * price
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "path": self.path,
            "description": self.description,
            "base_currency": self.base_currency,
            "quote_currency": self.quote_currency,
            "calc_mode": self.calc_mode.name,
            "digits": self.digits,
            "tick_size": str(self.tick_size),
            "tick_value": str(self.tick_value),
            "contract_size": str(self.contract_size),
            "spread": self.spread,
            "volume_min": str(self.volume_min),
            "volume_max": str(self.volume_max),
            "volume_step": str(self.volume_step),
            "trade_mode": self.trade_mode.name,
            "exec_mode": self.exec_mode.name,
            "fill_flags": int(self.fill_flags),
            "is_trade_allowed": self.is_trade_allowed,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }
```

---

### 5. `core/domains/instruments/services.py`

```python
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
```

---

### 6. `core/domains/instruments/__init__.py`

```python
"""Instruments domain - Tradable instruments, sessions, holidays."""
from .enums import (
    CalculationMode, ExecutionMode, TradeMode, FillingFlags,
    ExpirationFlags, GTCMode, SwapMode, OrderFlags, OptionMode,
    HolidayMode
)
from .value_objects import TradingSession, QuoteSession, MarginRates
from .symbol import Symbol
from .holiday import Holiday
from .services import SessionService, HolidayService

__all__ = [
    # Enums
    "CalculationMode", "ExecutionMode", "TradeMode", "FillingFlags",
    "ExpirationFlags", "GTCMode", "SwapMode", "OrderFlags", "OptionMode",
    "HolidayMode",
    # Value Objects
    "TradingSession", "QuoteSession", "MarginRates",
    # Entities
    "Symbol", "Holiday",
    # Services
    "SessionService", "HolidayService",
]
```

---

## 📊 Summary

**Total lines across 6 files: ~750 lines** (vs your original ~100 lines)

### What's New:
✅ **Separate Quote and Trade sessions** (per day of week)  
✅ **Multiple sessions per day** (handles overnight sessions)  
✅ **Holiday system** with year/month/day, work times, symbol applicability  
✅ **Calculation modes** (FOREX, CFD, FUTURES, OPTIONS, BONDS, STOCKS, etc.)  
✅ **Execution modes** (REQUEST, INSTANT, MARKET, EXCHANGE)  
✅ **Filling flags** (FOK, IOC, RETURN)  
✅ **Margin rates per direction** (BUY/SELL/LIMIT/STOP all separate)  
✅ **Swap modes** (POINTS, CURRENCY, INTEREST, etc.)  
✅ **Base/Quote currency** (for cross-currency PnL)  
✅ **Trade modes** (DISABLED, LONGONLY, SHORTONLY, CLOSEONLY, FULL)  
✅ **Stops/Freeze levels**  
✅ **Session checking logic** (is market open?)  
✅ **Holiday checking logic** (is today a holiday?)  

### What's Next:
1. Create these 6 files in `core/domains/instruments/`
2. Update `core/ports/interfaces.py` to add `IHolidayRepository`
3. Update `infrastructure/persistence/` to implement the new repositories
4. Update `application/commands/` to use the new Symbol structure

Ready to proceed with the next step?



# USER -----------

Update core/ports/interfaces.py to add IHolidayRepository
Update infrastructure/persistence/ to implement the new repositories
Update application/commands/ to use the new Symbol structure

yes 


# AI ----------

Let me first read the current state of your codebase to match the exact patterns before making changes.


Based on your existing codebase patterns (from `broker-platform.md` and the audit repo), here are the exact implementations for all three tasks.

---

## 1. Add `IHolidayRepository` to `core/ports/interfaces.py`

Add this **at the end** of your existing `interfaces.py` file, right after `ISymbolRepository`:

```python
# =========================================================================
# HOLIDAY REPOSITORY
# =========================================================================

class IHolidayRepository(ABC, Generic[T]):
    """
    Contract for Holiday persistence.
    
    Architectural Purpose:
    Provides access to holiday configurations needed for
    session checking and market-open validation.
    """

    @abstractmethod
    async def save(self, holiday: T) -> T:
        """Persist a holiday configuration."""
        pass

    @abstractmethod
    async def find_by_id(self, holiday_id: str) -> Optional[T]:
        """Find a holiday by its ID."""
        pass

    @abstractmethod
    async def get_active_holidays(
        self, check_date: "datetime"
    ) -> List[T]:
        """
        Get all holidays that apply to a given date.
        Used by SessionService to check if market is open.
        """
        pass

    @abstractmethod
    async def get_holidays_for_symbol(
        self, symbol_name: str, year: int
    ) -> List[T]:
        """Get all holidays for a symbol in a given year."""
        pass

    @abstractmethod
    async def delete(self, holiday_id: str) -> bool:
        """Delete a holiday configuration."""
        pass

    @abstractmethod
    async def get_all(self) -> List[T]:
        """Return all holiday configurations."""
        pass
```

Also add these imports at the **top** of `interfaces.py` if not already present:

```python
from datetime import datetime
```

---

## 2. Implement Repositories in `infrastructure/persistence/`

### 2a. New file: `infrastructure/persistence/repositories/holiday_repository.py`

```python
"""
Holiday Repository - SQLAlchemy implementation of IHolidayRepository.
"""
from datetime import datetime, date
from decimal import Decimal
from typing import List, Optional

from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from core.domains.instruments.holiday import Holiday
from core.domains.instruments.enums import HolidayMode
from core.ports.interfaces import IHolidayRepository
from infrastructure.persistence.db_models import HolidayModel


class SQLAlchemyHolidayRepository(IHolidayRepository[Holiday]):
    """SQLAlchemy implementation of IHolidayRepository."""

    def __init__(self, session_factory):
        self.session_factory = session_factory

    async def save(self, holiday: Holiday) -> Holiday:
        """Persist a holiday configuration."""
        async with self.session_factory() as session:
            model = self._holiday_to_db(holiday)
            await session.merge(model)
            await session.commit()
            return holiday

    async def save_with_session(self, holiday: Holiday, session: AsyncSession) -> Holiday:
        """Save using an existing session (for Unit of Work)."""
        model = self._holiday_to_db(holiday)
        await session.merge(model)
        return holiday

    async def find_by_id(self, holiday_id: str) -> Optional[Holiday]:
        """Find a holiday by its ID."""
        async with self.session_factory() as session:
            result = await session.execute(
                select(HolidayModel).where(HolidayModel.id == holiday_id)
            )
            model = result.scalar_one_or_none()
            return self._db_to_holiday(model) if model else None

    async def get_active_holidays(self, check_date: datetime) -> List[Holiday]:
        """
        Get all holidays that apply to a given date.
        Matches by month+day, and year=0 (every year) or exact year.
        """
        target = check_date if isinstance(check_date, date) else check_date.date()

        async with self.session_factory() as session:
            stmt = select(HolidayModel).where(
                and_(
                    HolidayModel.mode == HolidayMode.ENABLED.name,
                    HolidayModel.month == target.month,
                    HolidayModel.day == target.day,
                    (HolidayModel.year == 0) | (HolidayModel.year == target.year),
                )
            )
            result = await session.execute(stmt)
            models = result.scalars().all()
            return [self._db_to_holiday(m) for m in models]

    async def get_holidays_for_symbol(
        self, symbol_name: str, year: int
    ) -> List[Holiday]:
        """Get all holidays for a symbol in a given year."""
        async with self.session_factory() as session:
            # Fetch all enabled holidays for the year (or year=0)
            stmt = select(HolidayModel).where(
                and_(
                    HolidayModel.mode == HolidayMode.ENABLED.name,
                    (HolidayModel.year == 0) | (HolidayModel.year == year),
                )
            )
            result = await session.execute(stmt)
            models = result.scalars().all()

            holidays = [self._db_to_holiday(m) for m in models]

            # Filter by symbol applicability in Python
            # (wildcard matching is easier in application code)
            return [
                h for h in holidays
                if h.applies_to_symbol(symbol_name)
            ]

    async def delete(self, holiday_id: str) -> bool:
        """Delete a holiday configuration."""
        async with self.session_factory() as session:
            result = await session.execute(
                select(HolidayModel).where(HolidayModel.id == holiday_id)
            )
            model = result.scalar_one_or_none()
            if model:
                await session.delete(model)
                await session.commit()
                return True
            return False

    async def get_all(self) -> List[Holiday]:
        """Return all holiday configurations."""
        async with self.session_factory() as session:
            result = await session.execute(select(HolidayModel))
            models = result.scalars().all()
            return [self._db_to_holiday(m) for m in models]

    # -----------------------------------------------------------------
    # MAPPERS
    # -----------------------------------------------------------------

    @staticmethod
    def _holiday_to_db(holiday: Holiday) -> "HolidayModel":
        """Map domain Holiday to DB model."""
        return HolidayModel(
            id=holiday.id,
            description=holiday.description,
            mode=holiday.mode.name,
            year=holiday.year,
            month=holiday.month,
            day=holiday.day,
            work_from=holiday.work_from.isoformat(),
            work_to=holiday.work_to.isoformat(),
            symbols=",".join(holiday.symbols) if holiday.symbols else "",
            created_at=holiday.created_at,
            updated_at=holiday.updated_at,
        )

    @staticmethod
    def _db_to_holiday(model: "HolidayModel") -> Holiday:
        """Map DB model to domain Holiday."""
        from datetime import time as dt_time

        work_from = dt_time.fromisoformat(model.work_from) if model.work_from else dt_time(0, 0)
        work_to = dt_time.fromisoformat(model.work_to) if model.work_to else dt_time(23, 59)

        symbols = (
            [s.strip() for s in model.symbols.split(",") if s.strip()]
            if model.symbols
            else []
        )

        return Holiday(
            id=model.id,
            description=model.description or "",
            mode=HolidayMode[model.mode] if model.mode else HolidayMode.ENABLED,
            year=model.year or 0,
            month=model.month or 1,
            day=model.day or 1,
            work_from=work_from,
            work_to=work_to,
            symbols=symbols,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )
```

### 2b. New file: Add `HolidayModel` to `infrastructure/persistence/db_models.py`

Add this class **at the end** of your existing `db_models.py`:

```python
class HolidayModel(Base):
    """SQLAlchemy model for Holiday configuration."""
    __tablename__ = "holidays"

    id = Column(String, primary_key=True)
    description = Column(String, nullable=True, default="")
    mode = Column(String, nullable=False, default="ENABLED")
    year = Column(Integer, nullable=False, default=0)
    month = Column(Integer, nullable=False, default=1)
    day = Column(Integer, nullable=False, default=1)
    work_from = Column(String, nullable=False, default="00:00:00")
    work_to = Column(String, nullable=False, default="23:59:59")
    symbols = Column(Text, nullable=True, default="")  # Comma-separated
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        Index("idx_holidays_date", "year", "month", "day"),
        Index("idx_holidays_mode", "mode"),
    )
```

Make sure these imports are at the top of `db_models.py` (they likely already are):
```python
from sqlalchemy import Column, String, Integer, Text, DateTime, Index, func
```

### 2c. Update `infrastructure/persistence/di_setup.py`

Add the Holiday repository registration alongside your existing repositories:

```python
from infrastructure.persistence.repositories.holiday_repository import SQLAlchemyHolidayRepository

# Inside your DI setup function, add:
holiday_repo = SQLAlchemyHolidayRepository(session_factory)
container.register(IHolidayRepository, holiday_repo)
```

---

## 3. Update `application/commands/` to Use New Symbol Structure

### 3a. Update `application/commands/create_order.py`

The key changes are in the **symbol validation** and **margin calculation** sections. Here is the exact diff to apply:

**Find this section** (symbol validation):
```python
# OLD CODE - uses simple symbol object
symbol = await self.symbol_repo.get_by_name(command.symbol)
if not symbol:
    raise ValueError(f"Symbol {command.symbol} not found")
```

**Replace with:**
```python
# NEW CODE - uses enriched Symbol with sessions and trade modes
from core.domains.instruments import Symbol

symbol = await self.symbol_repo.get_by_name(command.symbol)
if not symbol:
    raise ValueError(f"Symbol {command.symbol} not found")

# Check trade session is active
from datetime import datetime, timezone
now = datetime.now(timezone.utc)
if not symbol.is_trade_session_active(now):
    raise ValueError(
        f"Market is closed for {command.symbol}. "
        f"Trade session not active at {now.isoformat()}"
    )

# Check trade direction is allowed
side = "BUY" if command.order_type.startswith("BUY") else "SELL"
if not symbol.can_trade_direction(side):
    raise ValueError(
        f"Trade direction {side} not allowed for {command.symbol} "
        f"(trade_mode={symbol.trade_mode.name})"
    )

# Validate volume against symbol limits
volume_valid, volume_reason = symbol.validate_volume(command.volume)
if not volume_valid:
    raise ValueError(f"Invalid volume: {volume_reason}")
```

### 3b. Update `application/services/risk_service.py`

**Find this section** (margin check):
```python
# OLD CODE - passes raw dict to group.calculate_margin
required_margin = self.risk_engine.calculate_margin(account, symbol, volume, price)
```

**Replace with:**
```python
# NEW CODE - merge base symbol config with group overrides
symbol_config = {
    "contract_size": symbol.contract_size,
    "margin_rate_initial_buy": symbol.margin_rates.initial_buy,
    "margin_rate_initial_sell": symbol.margin_rates.initial_sell,
    "tick_size": symbol.tick_size,
    "tick_value": symbol.tick_value,
    "base_currency": symbol.base_currency,
    "quote_currency": symbol.quote_currency,
}

# Apply group symbol overrides if available
if account.group:
    overrides = account.group.get_symbol_config(symbol.name)
    symbol_config.update(overrides)

required_margin = self.risk_engine.calculate_margin(
    account, symbol_config, volume, price
)
```

### 3c. New file: `application/commands/create_holiday.py`

```python
"""
Command to create or update a holiday configuration.
"""
import logging
from dataclasses import dataclass
from datetime import time, datetime, timezone
from typing import List, Optional

from core.domains.instruments.holiday import Holiday
from core.domains.instruments.enums import HolidayMode
from core.ports.interfaces import IHolidayRepository, IEventBus
from core.events.domain_events import HolidayCreated

logger = logging.getLogger(__name__)


@dataclass
class CreateHolidayCommand:
    """Command to create a holiday."""
    description: str
    year: int = 0  # 0 = every year
    month: int = 1
    day: int = 1
    work_from: str = "00:00:00"
    work_to: str = "23:59:59"
    symbols: Optional[List[str]] = None  # None = all symbols
    mode: str = "ENABLED"


class CreateHolidayHandler:
    """Handler for CreateHolidayCommand."""

    def __init__(
        self,
        holiday_repo: IHolidayRepository,
        event_bus: IEventBus,
    ):
        self.holiday_repo = holiday_repo
        self.event_bus = event_bus

    async def handle(self, command: CreateHolidayCommand) -> Holiday:
        """Create or update a holiday configuration."""

        # Validate date
        if not (1 <= command.month <= 12):
            raise ValueError(f"Invalid month: {command.month}")
        if not (1 <= command.day <= 31):
            raise ValueError(f"Invalid day: {command.day}")
        if command.year < 0:
            raise ValueError(f"Invalid year: {command.year}")

        # Parse times
        work_from = time.fromisoformat(command.work_from)
        work_to = time.fromisoformat(command.work_to)

        # Parse mode
        try:
            mode = HolidayMode[command.mode.upper()]
        except KeyError:
            raise ValueError(f"Invalid holiday mode: {command.mode}")

        # Create domain entity
        holiday = Holiday(
            description=command.description,
            mode=mode,
            year=command.year,
            month=command.month,
            day=command.day,
            work_from=work_from,
            work_to=work_to,
            symbols=command.symbols or [],
        )

        # Persist
        saved = await self.holiday_repo.save(holiday)
        logger.info(
            f"Holiday created: {saved.description} "
            f"({saved.year}-{saved.month}-{saved.day})"
        )

        # Publish event
        event = HolidayCreated(
            aggregate_id=saved.id,
            payload={
                "holiday_id": saved.id,
                "description": saved.description,
                "year": saved.year,
                "month": saved.month,
                "day": saved.day,
                "symbols": saved.symbols,
            },
        )
        await self.event_bus.publish(event)

        return saved
```

### 3d. Add `HolidayCreated` to `core/events/domain_events.py`

Add this class alongside your existing events:

```python
@dataclass
class HolidayCreated(DomainEvent):
    """Published when a new holiday configuration is created."""
    pass
```

---

## 📊 Summary of All Files Changed/Created

| Action | File | Purpose |
|:---|:---|:---|
| **MODIFY** | `core/ports/interfaces.py` | Added `IHolidayRepository` |
| **MODIFY** | `infrastructure/persistence/db_models.py` | Added `HolidayModel` |
| **CREATE** | `infrastructure/persistence/repositories/holiday_repository.py` | SQLAlchemy implementation |
| **MODIFY** | `infrastructure/persistence/di_setup.py` | Register `IHolidayRepository` |
| **MODIFY** | `application/commands/create_order.py` | Session/trade-mode/volume validation |
| **MODIFY** | `application/services/risk_service.py` | Merge symbol config with group overrides |
| **CREATE** | `application/commands/create_holiday.py` | Holiday creation command |
| **MODIFY** | `core/events/domain_events.py` | Added `HolidayCreated` event |

---

## 🚀 What's Next?

1. **Create the 6 instrument domain files** (`enums.py`, `value_objects.py`, `symbol.py`, `holiday.py`, `services.py`, `__init__.py`) in `core/domains/instruments/` using the code from my previous message.
2. **Apply the 8 file changes** above.
3. **Run `pytest tests/`** to verify nothing breaks.
4. **Generate an Alembic migration** for the new `holidays` table.

Would you like me to provide the Alembic migration script for the `holidays` table, or shall we move on to the next domain?



# USER -----------------
3b. Update application/services/risk_service.py
Find this section (margin check):
# OLD CODE - passes raw dict to group.calculate_margin
required_margin = self.risk_engine.calculate_margin(account, symbol, volume, price)

Replace with:
# NEW CODE - merge base symbol config with group overrides
symbol_config = {
    "contract_size": symbol.contract_size,
    "margin_rate_initial_buy": symbol.margin_rates.initial_buy,
    "margin_rate_initial_sell": symbol.margin_rates.initial_sell,
    "tick_size": symbol.tick_size,
    "tick_value": symbol.tick_value,
    "base_currency": symbol.base_currency,
    "quote_currency": symbol.quote_currency,
}

# Apply group symbol overrides if available
if account.group:
    overrides = account.group.get_symbol_config(symbol.name)
    symbol_config.update(overrides)

required_margin = self.risk_engine.calculate_margin(
    account, symbol_config, volume, price
)

not able to complete this task as there is no required_margin = self.risk_engine.calculate_margin(account, symbol, volume, price)
 line in application/services/risk_service.py






# AI -------------------

You're absolutely right. Looking at your actual `risk_service.py`, the margin check uses `symbol.calculate_margin_required()` directly, not a method on `risk_engine`. 

Here's the **correct fix** for `_check_margin_requirement`:

---

## Find This Section (lines ~180-210)

```python
async def _check_margin_requirement(
    self,
    order: Order,
    account: Account,
    symbol: Symbol,
    price: Price
) -> bool:
    """
    Calculates required margin and compares against live Free Margin.
    """
    margin_required = symbol.calculate_margin_required(order.volume.value, price.value)
    required_amount = Decimal(str(margin_required))
    
    # Check live margin using RiskEngine if available
    available_free_margin = account.margin_free.amount
    if self.risk_engine and self.position_repo:
        try:
            open_positions = await self.position_repo.get_by_account(account.id)
            snapshot = self.risk_engine.calculate_margin_level(account, open_positions)
            available_free_margin = snapshot.margin_free
        except Exception as e:
            logger.error(f"Failed live margin snapshot calculation: {e}", exc_info=True)
    
    if required_amount > available_free_margin:
        logger.debug(
            f"Margin check failed: Required {required_amount}, Available {available_free_margin}"
        )
        return False
    return True
```

---

## Replace With

```python
async def _check_margin_requirement(
    self,
    order: Order,
    account: Account,
    symbol: Symbol,
    price: Price
) -> bool:
    """
    Calculates required margin with group symbol overrides and compares against live Free Margin.
    
    MT5-Accurate Logic:
    1. Build base symbol config (contract_size, margin_rates, etc.)
    2. Apply group symbol overrides if available
    3. Use account's effective leverage (account > group > default)
    4. Calculate margin: (Volume * ContractSize * Price * MarginRate) / Leverage
    """
    volume = order.volume.value
    price_value = price.value
    
    # 1. Build base symbol configuration
    symbol_config = {
        "contract_size": symbol.contract_size,
        "tick_size": symbol.tick_size,
        "tick_value": symbol.tick_value,
        "base_currency": symbol.base_currency,
        "quote_currency": symbol.quote_currency,
        "margin_rate_initial_buy": symbol.margin_rates.initial_buy,
        "margin_rate_initial_sell": symbol.margin_rates.initial_sell,
    }
    
    # 2. Apply group symbol overrides if available
    if account.group:
        overrides = account.group.get_symbol_config(symbol.name)
        symbol_config.update(overrides)
    
    # 3. Determine effective leverage (account > group > default 100)
    effective_leverage = Decimal(str(
        account.effective_leverage() if hasattr(account, 'effective_leverage') 
        else (account.leverage if account.leverage and account.leverage > 0 
              else (account.group.margin.leverage_default if account.group else 100))
    ))
    if effective_leverage <= Decimal('0'):
        effective_leverage = Decimal('1.0')
    
    # 4. Calculate required margin
    contract_size = symbol_config.get("contract_size", Decimal('100000'))
    
    # Determine margin rate based on order side
    order_side = "BUY" if order.order_type.startswith("BUY") else "SELL"
    if order_side == "BUY":
        margin_rate = symbol_config.get("margin_rate_initial_buy", Decimal('1.0'))
    else:
        margin_rate = symbol_config.get("margin_rate_initial_sell", Decimal('1.0'))
    
    # Formula: (Volume * ContractSize * Price * MarginRate) / Leverage
    notional = volume * contract_size * price_value
    margin_required = (notional * margin_rate) / effective_leverage
    
    required_amount = margin_required
    
    # 5. Check live margin using RiskEngine if available
    available_free_margin = account.margin_free.amount
    if self.risk_engine and self.position_repo:
        try:
            open_positions = await self.position_repo.get_by_account(
                account.login if hasattr(account, 'login') else account.id
            )
            snapshot = self.risk_engine.calculate_margin_level(account, open_positions)
            available_free_margin = snapshot.margin_free
        except Exception as e:
            logger.error(f"Failed live margin snapshot calculation: {e}", exc_info=True)
    
    # 6. Compare required vs available
    if required_amount > available_free_margin:
        logger.debug(
            f"Margin check failed: Required {required_amount}, Available {available_free_margin}"
        )
        return False
    
    return True
```

---

## What Changed

| Aspect | Old Code | New Code |
|:---|:---|:---|
| **Margin Calculation** | Uses `symbol.calculate_margin_required()` (base only) | Builds `symbol_config` dict with base values |
| **Group Overrides** | ❌ Not applied | ✅ Applies `account.group.get_symbol_config(symbol.name)` |
| **Leverage** | ❌ Uses symbol's hardcoded logic | ✅ Uses `account.effective_leverage()` (account > group > default) |
| **Margin Rate** | ❌ Uses `symbol.margin_initial_percent` | ✅ Uses `margin_rate_initial_buy/sell` from symbol_config |
| **Formula** | `gross_value * (margin_percent / 100)` | `(notional * margin_rate) / leverage` (MT5-accurate) |

---

## Why This Matters

**Before:** A VIP group with `GroupSymbolOverride` for "EURUSD" setting `margin_rate_initial_buy = 0.5` (50% margin discount) would be **ignored**. The system would always use the base symbol's 100% margin rate.

**After:** The override is applied, so VIP clients get the correct 50% margin requirement.

This is the exact MT5 behavior where groups can override symbol-specific margin rates, execution modes, volume limits, etc.