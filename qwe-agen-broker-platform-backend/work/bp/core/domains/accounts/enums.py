"""Account domain enumerations."""
from enum import Enum, IntFlag


class AccountType(Enum):
    """Account types as per MT5."""
    REAL = "real"
    DEMO = "demo"
    PRELIMINARY = "preliminary"  # KYC pending
    CONTEST = "contest"
    COVERAGE = "coverage"  # Internal hedge account
    MANAGER = "manager"
    DEALER = "dealer"


class ClientStatus(Enum):
    """Client status (IMTUser::EnClientStatus)."""
    UNREGISTERED = 0
    REGISTERED = 100
    FUNDED = 200
    ACTIVE = 300
    INACTIVE = 400
    SUSPENDED = 500
    CLOSED = 600
    TERMINATED = 700


class SOActivation(Enum):
    """Stop-out activation states (IMTAccount::EnSOActivation)."""
    NONE = 0
    MARGIN_CALL = 1
    STOP_OUT = 2


class MarginMode(Enum):
    """Group margin calculation modes."""
    RETAIL = "retail"
    EXCHANGE_DISCOUNT = "exchange_discount"
    RETAIL_HEDGED = "retail_hedged"


class ExecutionMode(Enum):
    """Order execution modes."""
    REQUEST = "request"
    INSTANT = "instant"
    MARKET = "market"
    EXCHANGE = "exchange"


class TradeMode(Enum):
    """Symbol trade modes."""
    DISABLED = "disabled"
    LONGONLY = "longonly"
    SHORTONLY = "shortonly"
    CLOSEONLY = "closeonly"
    FULL = "full"


class FreeMarginMode(Enum):
    """Free margin calculation modes."""
    NOT_USE_PL = 0
    USE_PL = 1
    PROFIT = 2
    LOSS = 3


class StopOutMode(Enum):
    """Stop-out calculation modes."""
    PERCENT = 0
    MONEY = 1


class CommissionType(Enum):
    """Commission calculation types."""
    DEAL = "deal"
    VOLUME = "volume"
    PERCENT = "percent"


class NewsMode(Enum):
    """News display modes."""
    DISABLED = "disabled"
    HEADERS = "headers"
    FULL = "full"


class TradeFlags(IntFlag):
    """Bitwise trade permission flags."""
    NONE = 0x00000000
    SWAPS = 0x00000001
    TRAILING = 0x00000002
    EXPERTS = 0x00000004
    EXPIRATION = 0x00000008
    SIGNALS_ALL = 0x00000010
    SIGNALS_OWN = 0x00000020
    SO_COMPENSATION = 0x00000040
    SO_FULLY_HEDGED = 0x00000080
    FIFO_CLOSE = 0x00000100
    HEDGE_PROHIBIT = 0x00000200
CommissionMode = CommissionType
