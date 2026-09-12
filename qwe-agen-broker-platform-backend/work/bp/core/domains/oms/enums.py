"""OMS domain enumerations - MT5-accurate."""
from enum import Enum, IntFlag


class OrderType(Enum):
    """Order types (IMTOrder::EnOrderType)."""
    BUY = "BUY"
    SELL = "SELL"
    BUY_LIMIT = "BUY_LIMIT"
    SELL_LIMIT = "SELL_LIMIT"
    BUY_STOP = "BUY_STOP"
    SELL_STOP = "SELL_STOP"
    BUY_STOP_LIMIT = "BUY_STOP_LIMIT"
    SELL_STOP_LIMIT = "SELL_STOP_LIMIT"


class OrderState(Enum):
    """Order states (IMTOrder::EnOrderState)."""
    STARTED = "STARTED"           # Order adding started
    NEW = "STARTED"               # Alias for STARTED
    PLACED = "PLACED"             # Order placed in system
    CANCELLED = "CANCELLED"       # Cancelled by client
    PARTIALLY_FILLED = "PARTIALLY_FILLED"  # Partially filled
    FILLED = "FILLED"             # Fully filled
    REJECTED = "REJECTED"         # Rejected by broker
    EXPIRED = "EXPIRED"           # Expired by time


class OrderReason(Enum):
    """Who/what placed the order (IMTOrder::EnOrderReason)."""
    CLIENT = "CLIENT"             # Terminal
    EXPERT = "EXPERT"             # Expert Advisor
    DEALER = "DEALER"             # Dealer terminal
    GATEWAY = "GATEWAY"           # Gateway/external system
    SIGNAL = "SIGNAL"             # Trade signal
    API = "API"                   # Manager API
    MOBILE = "MOBILE"             # Mobile terminal
    SL = "SL"                   # Stop Loss triggered (server-side, M9)
    TP = "TP"                   # Take Profit triggered (server-side, M9)
    SO = "SO"                   # Stop Out (liquidation worker)
    WEB = "WEB"                   # Web terminal
    PLUGIN = "PLUGIN"             # Server plugin


class TimeInForce(Enum):
    """Order time-in-force (IMTOrder::EnOrderTimeType)."""
    GTC = "GTC"                   # Good till cancelled
    DAY = "DAY"                   # Good for the day
    SPECIFIED = "SPECIFIED"       # Good till specified date
    SPECIFIED_DAY = "SPECIFIED_DAY"  # Good till specified day


class ActivationMode(Enum):
    """Order activation mode for ATM orders (IMTOrder::EnOrderActivationMode)."""
    NONE = "NONE"                 # Not activated
    TIME = "TIME"                 # Activated by time
    PRICE = "PRICE"               # Activated by price
    TIME_PRICE = "TIME_PRICE"     # Activated by both


class DealType(Enum):
    """Deal types (IMTDeal::EnDealType)."""
    # Trading deals
    BUY = "BUY"
    SELL = "SELL"
    # Non-trading deals
    BALANCE = "BALANCE"
    CREDIT = "CREDIT"
    CHARGE = "CHARGE"
    CORRECTION = "CORRECTION"
    BONUS = "BONUS"
    COMMISSION = "COMMISSION"
    COMMISSION_DAILY = "COMMISSION_DAILY"
    COMMISSION_MONTHLY = "COMMISSION_MONTHLY"
    COMMISSION_AGENT_DAILY = "COMMISSION_AGENT_DAILY"
    COMMISSION_AGENT_MONTHLY = "COMMISSION_AGENT_MONTHLY"
    INTEREST = "INTEREST"
    BUY_CANCELED = "BUY_CANCELED"
    SELL_CANCELED = "SELL_CANCELED"
    REBATE = "REBATE"
    COMPENSATION = "COMPENSATION"
    # Rollover
    ROLLOVER_PROFIT = "ROLLOVER_PROFIT"
    ROLLOVER_LOSS = "ROLLOVER_LOSS"


class DealEntry(Enum):
    """Deal entry type - how deal affects position (IMTDeal::EnDealEntry)."""
    IN = "IN"           # Open position
    OUT = "OUT"         # Close position
    INOUT = "INOUT"     # Reverse position
    OUT_BY = "OUT_BY"   # Close by opposite position


class DealReason(Enum):
    """Deal reason (IMTDeal::EnDealReason)."""
    CLIENT = "CLIENT"
    EXPERT = "EXPERT"
    DEALER = "DEALER"
    SL = "SL"           # Stop loss triggered
    TP = "TP"           # Take profit triggered
    SO = "SO"           # Stop out triggered
    ROLLOVER = "ROLLOVER"
    VMARGIN = "VMARGIN"  # Margin call / daily margin
    STOP_OUT = "STOP_OUT"
    GATEWAY = "GATEWAY"
    SIGNAL = "SIGNAL"
    API = "API"
    MOBILE = "MOBILE"
    WEB = "WEB"
    PLUGIN = "PLUGIN"
    SPLIT = "SPLIT"


class PositionAction(Enum):
    """Position side (IMTPosition::EnPositionAction)."""
    BUY = "BUY"
    SELL = "SELL"


class PositionReason(Enum):
    """Position opening reason."""
    CLIENT = "CLIENT"
    EXPERT = "EXPERT"
    DEALER = "DEALER"
    GATEWAY = "GATEWAY"
    SIGNAL = "SIGNAL"
    API = "API"


class OrderFlags(IntFlag):
    """Order activation flags (IMTOrder::EnOrderActivationFlags)."""
    NONE = 0x00000000
    NO_SL = 0x00000001
    NO_TP = 0x00000002
    NO_SLTP_BY_TICK = 0x00000004