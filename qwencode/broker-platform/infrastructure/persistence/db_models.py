from sqlalchemy import Column, Integer, String, Numeric, DateTime, Boolean, Text, ForeignKey, Index, func
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.sql import func
from decimal import Decimal
import enum


class Base(DeclarativeBase):
    pass


class AccountModel(Base):
    """Database model for trading Account."""
    __tablename__ = "accounts"
    login = Column(String(32), primary_key=True)
    group_name = Column(String(128), ForeignKey("groups.name"), nullable=False)
    account_type = Column(String(32), nullable=False, default="REAL")
    balance = Column(Numeric(18, 8), nullable=False, default=0)
    credit = Column(Numeric(18, 8), nullable=False, default=0)
    equity = Column(Numeric(18, 8), nullable=False, default=0)
    margin_used = Column(Numeric(18, 8), nullable=False, default=0)
    margin_free = Column(Numeric(18, 8), nullable=False, default=0)
    leverage = Column(Integer, nullable=False, default=100)
    is_enabled = Column(Boolean, nullable=False, default=True)
    kyc_verified = Column(Boolean, nullable=False, default=False)
    currency = Column(String(3), nullable=False, default="USD")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class GroupModel(Base):
    """Database model for Group (rule engine)."""
    __tablename__ = "groups"
    name = Column(String(128), primary_key=True)
    leverage = Column(Integer, nullable=False, default=100)
    margin_call_level = Column(Numeric(6, 2), nullable=False, default=60)
    stop_out_level = Column(Numeric(6, 2), nullable=False, default=30)
    stop_out_mode = Column(String(16), nullable=False, default="PERCENT")
    commission_type = Column(String(16), nullable=False, default="MONEY")
    commission_value = Column(Numeric(18, 8), nullable=False, default=0)
    commission_currency = Column(String(3), nullable=False, default="USD")
    execution_mode = Column(String(32), nullable=False, default="MARKET")
    position_mode = Column(String(16), nullable=False, default="HEDGING")
    allow_hedging = Column(Boolean, default=True)
    allow_scalping = Column(Boolean, default=True)
    slippage_points = Column(Integer, default=0)
    permissions_json = Column(Text, default="{}")
    swap_enable = Column(Boolean, default=True)
    swap_type = Column(String(16), default="POINTS")
    swap_long = Column(Numeric(18, 8), default=0)
    swap_short = Column(Numeric(18, 8), default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class SymbolModel(Base):
    """Database model for tradable Symbol."""
    __tablename__ = "symbols"
    name = Column(String(32), primary_key=True)
    path = Column(String(128), nullable=False)
    tick_size = Column(Numeric(18, 8), nullable=False)
    tick_value = Column(Numeric(18, 8), nullable=False)
    contract_size = Column(Numeric(18, 8), nullable=False, default=100000)
    digits = Column(Integer, nullable=False, default=5)
    volume_min = Column(Numeric(18, 8), nullable=False, default=Decimal('0.01'))
    volume_max = Column(Numeric(18, 8), nullable=False, default=Decimal('100'))
    volume_step = Column(Numeric(18, 8), nullable=False, default=Decimal('0.01'))
    margin_initial_percent = Column(Numeric(6, 2), nullable=False, default=Decimal('3.33'))
    margin_maintenance_percent = Column(Numeric(6, 2), nullable=False, default=Decimal('1.67'))
    is_trade_allowed = Column(Boolean, nullable=False, default=True)
    fill_mode = Column(String(16), nullable=False, default="FOK")
    sessions_json = Column(Text, default="[]")
    created_at = Column(DateTime(timezone=True), server_default=func.now())


# Find the existing OrderModel class and REPLACE it with:

class OrderModel(Base):
    """SQLAlchemy model for Order entity (MT5 IMTOrder)."""
    __tablename__ = "orders"

    # Identity
    ticket_id = Column(String, primary_key=True)
    external_id = Column(String, nullable=True)  # Exchange/ECN order ID
    gateway_id = Column(String, nullable=True)   # Gateway execution order ID
    
    # Account & Symbol
    account_login = Column(BigInteger, nullable=False, index=True)
    dealer_login = Column(BigInteger, nullable=True)
    symbol = Column(String, nullable=False, index=True)
    
    # Order details
    order_type = Column(String, nullable=False)  # OrderType enum value
    reason = Column(String, nullable=False, default="CLIENT")  # OrderReason enum
    state = Column(String, nullable=False, default="NEW")  # OrderState enum
    
    # Volume (split into initial/current for partial fills)
    volume_initial = Column(Numeric(20, 8), nullable=False)
    volume_current = Column(Numeric(20, 8), nullable=False)
    
    # Pricing (Price value objects stored as Numeric)
    price_order = Column(Numeric(20, 8), nullable=False)  # Limit/Stop price
    price_sl = Column(Numeric(20, 8), nullable=True)
    price_tp = Column(Numeric(20, 8), nullable=True)
    price_trigger = Column(Numeric(20, 8), nullable=True)  # For STOP_LIMIT
    
    # Time
    time_setup = Column(DateTime(timezone=True), nullable=False)
    time_setup_msc = Column(BigInteger, nullable=False, default=0)
    time_expiration = Column(DateTime(timezone=True), nullable=True)
    time_done = Column(DateTime(timezone=True), nullable=True)
    
    # Time in force
    time_in_force = Column(String, nullable=False, default="GTC")
    
    # ATM Activation
    activation_mode = Column(String, nullable=False, default="NONE")
    activation_time = Column(DateTime(timezone=True), nullable=True)
    activation_price = Column(Numeric(20, 8), nullable=True)
    activation_flags = Column(Integer, nullable=False, default=0)
    
    # Symbol metadata snapshot
    digits = Column(Integer, nullable=False, default=5)
    digits_currency = Column(Integer, nullable=False, default=2)
    contract_size = Column(Numeric(20, 8), nullable=False, default=100000)
    
    # Expert/Plugin info
    expert_id = Column(String, nullable=True)
    expert_name = Column(String, nullable=True)
    comment = Column(Text, nullable=True)
    
    # Matching
    order_matching = Column(String, nullable=True)  # Opposite order ticket
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        Index("idx_orders_account_state", "account_login", "state"),
        Index("idx_orders_symbol_state", "symbol", "state"),
        Index("idx_orders_time_setup", "time_setup"),
    )


# Find the existing DealModel class and REPLACE it with:

class DealModel(Base):
    """SQLAlchemy model for Deal entity (MT5 IMTDeal)."""
    __tablename__ = "deals"

    # Identity
    deal_id = Column(String, primary_key=True)
    order_id = Column(String, nullable=True, index=True)
    position_id = Column(String, nullable=True, index=True)
    
    # Account
    account_login = Column(BigInteger, nullable=False, index=True)
    dealer_login = Column(BigInteger, nullable=True)
    
    # Symbol & trade
    symbol = Column(String, nullable=False, index=True)
    deal_type = Column(String, nullable=False)  # DealType enum
    entry = Column(String, nullable=False, default="IN")  # DealEntry enum
    reason = Column(String, nullable=False, default="CLIENT")  # DealReason enum
    
    # Volume & price
    volume = Column(Numeric(20, 8), nullable=False)
    price = Column(Numeric(20, 8), nullable=False)
    
    # External references
    external_id = Column(String, nullable=True)
    order_ticket = Column(String, nullable=True)
    
    # Financial (Money value objects)
    profit = Column(Numeric(20, 8), nullable=False, default=0)
    swap = Column(Numeric(20, 8), nullable=False, default=0)
    commission = Column(Numeric(20, 8), nullable=False, default=0)
    currency = Column(String, nullable=False, default="USD")
    
    # Symbol metadata
    digits = Column(Integer, nullable=False, default=5)
    digits_currency = Column(Integer, nullable=False, default=2)
    contract_size = Column(Numeric(20, 8), nullable=False, default=100000)
    
    # Comment
    comment = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        Index("idx_deals_account_time", "account_login", "created_at"),
        Index("idx_deals_symbol_time", "symbol", "created_at"),
        Index("idx_deals_type", "deal_type"),
    )


# Find the existing PositionModel class and REPLACE it with:

class PositionModel(Base):
    """SQLAlchemy model for Position entity (MT5 IMTPosition)."""
    __tablename__ = "positions"

    # Identity
    position_id = Column(String, primary_key=True)
    external_id = Column(String, nullable=True)
    identifier = Column(String, nullable=True, index=True)  # For netting
    
    # Account
    account_login = Column(BigInteger, nullable=False, index=True)
    
    # Symbol & side
    symbol = Column(String, nullable=False, index=True)
    action = Column(String, nullable=False)  # PositionAction enum (BUY/SELL)
    reason = Column(String, nullable=False, default="CLIENT")  # PositionReason enum
    
    # Volume
    volume = Column(Numeric(20, 8), nullable=False)
    
    # Pricing (Price value objects)
    price_open = Column(Numeric(20, 8), nullable=False)
    price_current = Column(Numeric(20, 8), nullable=False)
    price_sl = Column(Numeric(20, 8), nullable=True)
    price_tp = Column(Numeric(20, 8), nullable=True)
    
    # Financial (Money value objects)
    profit = Column(Numeric(20, 8), nullable=False, default=0)
    swap = Column(Numeric(20, 8), nullable=False, default=0)
    commission = Column(Numeric(20, 8), nullable=False, default=0)
    currency = Column(String, nullable=False, default="USD")
    
    # Symbol metadata
    digits = Column(Integer, nullable=False, default=5)
    digits_currency = Column(Integer, nullable=False, default=2)
    contract_size = Column(Numeric(20, 8), nullable=False, default=100000)
    
    # Links
    deal_open = Column(String, nullable=True)
    deal_close = Column(String, nullable=True)
    position_by_id = Column(String, nullable=True)  # For close-by
    
    # Timestamps
    time_create = Column(DateTime(timezone=True), nullable=False)
    time_update = Column(DateTime(timezone=True), nullable=False)
    time_done = Column(DateTime(timezone=True), nullable=True)
    
    # Metadata
    comment = Column(Text, nullable=True)
    magic_number = Column(Integer, nullable=False, default=0)

    __table_args__ = (
        Index("idx_positions_account_symbol", "account_login", "symbol"),
        Index("idx_positions_action", "action"),
        Index("idx_positions_time_create", "time_create"),
    )


class DealModel(Base):
    """Database model for Deal (immutable execution record)."""
    __tablename__ = "deals"
    deal_id = Column(String(32), primary_key=True)
    order_id = Column(String(32), ForeignKey("orders.ticket_id"), nullable=False)
    account_login = Column(String(32), ForeignKey("accounts.login"), nullable=False)
    symbol = Column(String(32), ForeignKey("symbols.name"), nullable=False)
    deal_type = Column(String(32), nullable=False)
    volume = Column(Numeric(18, 8), nullable=False)
    price = Column(Numeric(18, 8), nullable=False)
    commission = Column(Numeric(18, 8), nullable=False, default=0)
    swap = Column(Numeric(18, 8), nullable=False, default=0)
    profit = Column(Numeric(18, 8), nullable=False, default=0)
    currency = Column(String(3), nullable=False, default="USD")
    original_deal_id = Column(String(32), nullable=True)
    reason = Column(String(256), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    __table_args__ = (
        Index("idx_deals_login", "account_login"),
        Index("idx_deals_order", "order_id"),
        Index("idx_deals_symbol", "symbol"),
    )


class PositionModel(Base):
    """Database model for Position (aggregate open state)."""
    __tablename__ = "positions"
    id = Column(String(64), primary_key=True)
    account_login = Column(String(32), ForeignKey("accounts.login"), nullable=False)
    symbol = Column(String(32), ForeignKey("symbols.name"), nullable=False)
    volume = Column(Numeric(18, 8), nullable=False)
    side = Column(String(8), nullable=False)
    average_price = Column(Numeric(18, 8), nullable=False)
    unrealized_pnl = Column(Numeric(18, 8), nullable=False, default=0)
    swap_accumulated = Column(Numeric(18, 8), nullable=False, default=0)
    contract_size = Column(Numeric(18, 8), nullable=False, default=100000)
    opened_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    __table_args__ = (
        Index("idx_positions_login", "account_login"),
        Index("idx_positions_symbol", "symbol"),
    )


class BalanceOperationModel(Base):
    """Database model for immutable BalanceOperation (ledger)."""
    __tablename__ = "balance_operations"
    operation_id = Column(String(32), primary_key=True)
    account_login = Column(String(32), ForeignKey("accounts.login"), nullable=False)
    operation_type = Column(String(32), nullable=False)
    amount = Column(Numeric(18, 8), nullable=False)
    currency = Column(String(3), nullable=False, default="USD")
    balance_after = Column(Numeric(18, 8), nullable=False)
    reference_id = Column(String(64), nullable=True)
    comment = Column(String(256), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    __table_args__ = (
        Index("idx_balance_ops_login", "account_login"),
        Index("idx_balance_ops_type", "operation_type"),
        Index("idx_balance_ops_reference", "reference_id"),
    )


class RoutingRuleModel(Base):
    """Database model for RoutingRule."""
    __tablename__ = "routing_rules"
    rule_id = Column(String(32), primary_key=True)
    priority = Column(Integer, nullable=False)
    destination = Column(String(32), nullable=False)
    group_filter = Column(String(128), nullable=True)
    symbol_filter = Column(String(64), nullable=True)
    volume_min = Column(Numeric(18, 8), nullable=True)
    volume_max = Column(Numeric(18, 8), nullable=True)
    gateway_id = Column(String(64), nullable=True)
    coverage_account_id = Column(String(64), nullable=True)
    is_enabled = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class CoverageAccountModel(Base):
    """Database model for CoverageAccount (broker risk account)."""
    __tablename__ = "coverage_accounts"
    account_id = Column(String(64), primary_key=True)
    name = Column(String(128), nullable=False)
    currency = Column(String(3), nullable=False, default="USD")
    net_exposure_json = Column(Text, default="{}")
    margin_level = Column(Numeric(18, 8), nullable=False, default=0)
    trading_state = Column(String(32), nullable=False, default="NEUTRAL")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class DomainEventModel(Base):
    """Database model for event sourcing / audit trail."""
    __tablename__ = "domain_events"
    event_id = Column(String(64), primary_key=True)
    event_type = Column(String(64), nullable=False)
    aggregate_id = Column(String(64), nullable=False)
    payload_json = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    __table_args__ = (
        Index("idx_events_type", "event_type"),
        Index("idx_events_aggregate", "aggregate_id"),
    )


class BarModel(Base):
    """Database model for aggregated OHLCV bars."""
    __tablename__ = "bars"
    id = Column(Integer, primary_key=True, autoincrement=True)
    symbol = Column(String(32), nullable=False, index=True)
    timeframe = Column(String(10), nullable=False, index=True)
    open = Column(Numeric(18, 8), nullable=False)
    high = Column(Numeric(18, 8), nullable=False)
    low = Column(Numeric(18, 8), nullable=False)
    close = Column(Numeric(18, 8), nullable=False)
    tick_volume = Column(Integer, nullable=False, default=0)
    open_time = Column(DateTime(timezone=True), nullable=False, index=True)
    close_time = Column(DateTime(timezone=True), nullable=True)
    __table_args__ = (
        Index("idx_bars_symbol_timeframe_time", "symbol", "timeframe", "open_time"),
    )


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