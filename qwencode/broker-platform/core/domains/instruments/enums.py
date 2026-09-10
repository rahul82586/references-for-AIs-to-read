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