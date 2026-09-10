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