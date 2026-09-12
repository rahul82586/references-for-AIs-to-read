"""Symbol entity (IMTConSymbol)."""
from dataclasses import dataclass, field
from datetime import datetime, timezone, date, time
from decimal import Decimal
from typing import Any, Dict, List, Optional
import uuid

from core.domains.common.value_objects import Money
from .enums import (
    CalculationMode, ExecutionMode, TradeMode, FillingFlags,
    ExpirationFlags, GTCMode, SwapMode, OrderTypeFlags, OptionMode
)
from .value_objects import TradingSession, QuoteSession, MarginRates


def mt5_day_index(check_datetime: datetime) -> int:
    """MT5's Sunday-first day index for a datetime.

    MT5 stores SessionsQuotes / SessionsTrades as a 7-element array indexed
    SUNDAY-FIRST (0=Sunday .. 6=Saturday); Python's weekday() is MONDAY-first
    (0=Monday .. 6=Sunday). infrastructure.mt5.wire.WEEKDAY_SUNDAY_FIRST is the
    authority and TradingSession's own docstring says so explicitly.

    Both session checks below used `check_datetime.weekday()` directly as the MT5 index,
    which looked up the WRONG DAY for every symbol: a Monday order consulted the Sunday
    session, a Friday order consulted Thursday. On a configuration that closes the
    market at the weekend - which is every real FX server - that meant Monday trading
    was refused and Saturday trading was allowed.
    """
    return (check_datetime.weekday() + 1) % 7


def sessions_for_day(container: Any, day_index: int) -> list:
    """The sessions for one day, from either shape the field actually holds.

    Symbol declares `Dict[int, List[TradingSession]]`, but every producer of real
    symbols - the YAML loader's parse_sessions(), the MT5 importer, and the database
    mapper's sessions_from_days() - builds a FLAT LIST whose members carry
    `day_of_week`. Both session checks called `container.get(day)`, so against any
    symbol loaded from configuration or from the database they raised
    `AttributeError: 'list' object has no attribute 'get'`.

    That is not a corner case: CreateOrderHandler checks the session at step 2 and
    PreTradeRiskService checks it at step 4, so no order could be placed against a real
    configuration at all. Accepting both shapes means the declared default keeps working
    and the three real producers start working.
    """
    if not container:
        return []
    if isinstance(container, dict):
        return list(container.get(day_index) or [])
    out = []
    for session in container:
        try:
            index = int(getattr(session, "day_of_week", 0))
        except (TypeError, ValueError):
            index = 0
        if index == day_index:
            out.append(session)
    return out


def _session_covers(session: Any, check_time: Any) -> bool:
    """Does one session cover this time? Prefers is_within, which handles overnight."""
    is_within = getattr(session, "is_within", None)
    if callable(is_within):
        return bool(is_within(check_time))
    open_time = getattr(session, "open_time", None)
    close_time = getattr(session, "close_time", None)
    if open_time is None or close_time is None:
        return False
    if open_time > close_time:  # wraps past midnight
        return check_time >= open_time or check_time <= close_time
    return open_time <= check_time <= close_time


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
    # MT5 distinguishes THREE symbol currencies and they are not interchangeable:
    #   CurrencyBase    the base leg
    #   CurrencyProfit  the currency PnL is denominated in
    #   CurrencyMargin  the currency the margin requirement is computed in
    # For a plain FX pair they line up with base/quote; for indices, single equities and
    # bonds they do not. Measured on the 362 reference symbols, deriving them from the
    # symbol NAME gets 109 right, 60 wrong and cannot parse 193 at all - so these are
    # populated from MT5's own values on import, and the name heuristic below is only a
    # fallback for hand-written configs that omit them.
    #
    # These default to "" and NOT to "USD". Defaulting to "USD" made __post_init__'s
    # `if not self.base_currency` permanently False, so the parser never ran and every
    # symbol created without explicit currencies silently became USD/USD - EURJPY
    # included, which is what broke cross-currency PnL. A default that defeats the
    # fallback guarding it is worse than no default.
    base_currency: str = ""  # MT5 CurrencyBase, e.g. "EUR" for EURUSD
    quote_currency: str = ""  # MT5 CurrencyProfit, e.g. "USD" for EURUSD
    #: MT5 CurrencyMargin. When empty, margin is denominated in the base currency, which
    #: MT5 says is the usual case.
    margin_currency: str = ""
    
    # Calculation mode
    calc_mode: CalculationMode = CalculationMode.FOREX
    
    # Pricing
    digits: int = 5  # Decimal places (5 for forex, 2 for stocks)
    # MT5 Point: the price-precision step. Always populated. This is what price
    # quantisation must use - see the note on mt5_tick_size below.
    tick_size: Decimal = field(default_factory=lambda: Decimal('0.00001'))
    # MT5 TickSize: the tick ALIGNMENT step, and a DIFFERENT field from Point. It is
    # frequently zero (every crypto symbol in the reference export has TickSize = 0
    # while Point carries the real step) and the two differ on all 362 symbols there.
    # Kept separate so an MT5 import can round-trip and so nothing quantises to zero.
    mt5_tick_size: Decimal = field(default_factory=lambda: Decimal('0'))
    tick_value: Decimal = field(default_factory=lambda: Decimal('1.0'))
    contract_size: Decimal = field(default_factory=lambda: Decimal('100000'))
    
    # Spread
    spread: int = 0  # Fixed spread in points; 0 = floating (MT5 Symbol Spread)
    spread_balance: int = 0  # Points of the FIXED spread placed below the bid
    #: MT5 SpreadDiff / SpreadDiffBalance at the SYMBOL level (group overrides
    #: live on GroupSymbolOverride). Modelled as of M7: before that they were
    #: quarantined - lossless on the wire, invisible to the pricing engine.
    spread_diff: int = 0
    spread_diff_balance: int = 0
    
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
    gtc_mode: GTCMode = GTCMode.GTC
    fill_flags: FillingFlags = FillingFlags.FOK
    expiration_flags: ExpirationFlags = ExpirationFlags.GTC
    # MT5 EnOrderFlags is a bitmask of WHICH ORDER TYPES the symbol accepts, and
    # every symbol in the reference export carries 127 (all seven bits). The old
    # default of OrderFlags.TRADE came from an enum describing who placed an order.
    order_flags: OrderTypeFlags = OrderTypeFlags(127)
    
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
        """Fill in currencies that were not supplied.

        MT5's own CurrencyBase / CurrencyProfit / CurrencyMargin always win - they are
        authoritative and the name heuristic is wrong for 253 of the 362 reference
        symbols. The parse runs only for what is still missing, which in practice means
        hand-written YAML that omits currencies.
        """
        if not self.base_currency or not self.quote_currency:
            parsed_base, parsed_quote = self._parse_currencies_from_name()
            self.base_currency = self.base_currency or parsed_base
            self.quote_currency = self.quote_currency or parsed_quote
        # A margin currency MT5 did not specify falls back to the base currency, per
        # Platform-Setup.md: "Generally, margin requirements currency and symbol's base
        # currency are the same."
        if not self.margin_currency:
            self.margin_currency = self.base_currency
    
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
        
        check_time = check_datetime.time()

        sessions = sessions_for_day(self.quote_sessions, mt5_day_index(check_datetime))
        if not sessions:
            return False

        return any(_session_covers(session, check_time) for session in sessions)
    
    def is_trade_session_active(self, check_datetime: Optional[datetime] = None) -> bool:
        """Check if trade session is active at a given datetime."""
        if check_datetime is None:
            check_datetime = datetime.now(timezone.utc)
        
        if not self.is_trade_allowed:
            return False
        
        if self.trade_mode == TradeMode.DISABLED:
            return False
        
        check_time = check_datetime.time()

        sessions = sessions_for_day(self.trade_sessions, mt5_day_index(check_datetime))
        if not sessions:
            return False

        return any(_session_covers(session, check_time) for session in sessions)
    
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
        """Validate order volume.

        A zero limit means UNSET, not "nothing is allowed". MT5's own exports carry
        VolumeMin / VolumeStep / VolumeLimit of 0 on plenty of symbols (every crypto
        symbol in the reference export has TickSize 0 as well), and the seeded YAML loses
        volume_min and volume_step on a database round trip - so a zero arrives here in
        normal operation, not only in malformed configuration.

        `volume % self.volume_step` with a zero step raised decimal.InvalidOperation
        rather than returning a rejection, which propagated out of CreateOrderHandler as
        an unhandled exception: a 500 instead of a 400, and no rejected-order record.
        """
        if volume <= 0:
            return False, f"Volume must be positive, got {volume}"
        if self.volume_min and self.volume_min > 0 and volume < self.volume_min:
            return False, f"Volume {volume} below minimum {self.volume_min}"
        if self.volume_max and self.volume_max > 0 and volume > self.volume_max:
            return False, f"Volume {volume} exceeds maximum {self.volume_max}"

        step = self.volume_step
        if step and step > 0:
            remainder = volume % step
            if remainder != 0 and abs(remainder - step) > Decimal('1E-8'):
                return False, f"Volume {volume} not a multiple of step {step}"

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