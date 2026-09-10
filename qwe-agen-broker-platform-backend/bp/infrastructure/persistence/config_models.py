"""
SQLAlchemy models for the CONFIGURATION PLANE: Group and Symbol.

These two tables are the MT5 Administrator config model, and they are the single
source of truth for the schema. `ops/docker/init.sql` and the hand-written
`alembic/versions/migration.py` are gone; Alembic autogenerates from here.

DESIGN

1. MT5's scalar fields are real columns, named after the MT5 field in snake_case, so
   that reading `margin_call` next to MT5's `MarginCall` needs no translation table.
   All 44 ConfigGroups scalars and the modelled ConfigSymbols scalars are present.

2. Nested structures that our domain models as value objects - MarginProfile,
   CommissionRule list, GroupSymbolOverride list, GroupPermissions, SwapConfiguration,
   RoutingRule - are stored as JSONB. One source of truth each: the scalars are NOT
   duplicated inside the JSONB, so they cannot drift.

3. `mt5_extra` JSONB holds every MT5 field we have not modelled yet, exactly like the
   codec's `_mt5_extra`. This is what makes a DB -> MT5 export lossless even though our
   domain covers only 39% of ConfigGroups and 42% of ConfigSymbols. Import a real
   server's config, export it back, and nothing is lost.

4. UNITS. `margin_call` and `margin_stop_out` are PERCENT, matching MT5
   (`MarginCall: "50.00"`, `MarginStopOut: "30.00"` for group real\\real in the
   reference export). Numeric(6,2), NOT Numeric(5,4). There is no 0.8 / 0.5 anywhere.

5. `point` and `tick_size` are SEPARATE columns. MT5's Point is the price-precision
   step and is always populated; TickSize is frequently zero or coarser, and the two
   differ for 131 of the 362 symbols in the reference export. Merging them would
   corrupt every crypto symbol.

Scale convention: Numeric(20, 8) for prices, volumes and rates - matching the
OrderModel / DealModel / PositionModel tables that were already MT5-accurate.
"""

from sqlalchemy import (
    BigInteger,
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB

from .database import Base


class GroupModel(Base):
    """MT5 IMTConGroup - the rule engine.

    In MT5 a Group carries leverage, margin call and stop-out levels, free-margin
    mode, commissions, swaps, trade permissions, per-symbol overrides and routing for
    every account that belongs to it. The group path (``real\\real``) is the natural
    key; ``group_id`` is the surrogate our domain entity carries.
    """

    __tablename__ = "groups"

    # --- Identity -----------------------------------------------------------
    name = Column(String(128), primary_key=True)          # MT5 Group, e.g. "real\\real"
    group_id = Column(String(64), nullable=True, unique=True, index=True)
    server_id = Column(Integer, nullable=False, default=1)  # MT5 Server
    account_type = Column(String(32), nullable=False, default="real")
    is_active = Column(Boolean, nullable=False, default=True)

    # --- Authentication (MT5 AuthMode / AuthPasswordMin / AuthOTPMode) ------
    auth_mode = Column(Integer, nullable=False, default=0)
    auth_password_min = Column(Integer, nullable=False, default=8)
    auth_otp_mode = Column(Integer, nullable=False, default=0)
    permissions_flags = Column(Integer, nullable=False, default=0)

    # --- White label --------------------------------------------------------
    company = Column(String(256), nullable=False, default="")
    company_page = Column(String(256), nullable=False, default="")
    company_email = Column(String(256), nullable=False, default="")
    company_support_page = Column(String(512), nullable=False, default="")
    company_support_email = Column(String(256), nullable=False, default="")
    company_catalog = Column(String(256), nullable=False, default="")
    company_deposit_url = Column(String(512), nullable=False, default="")
    company_withdrawal_url = Column(String(512), nullable=False, default="")

    # --- Currency -----------------------------------------------------------
    currency = Column(String(16), nullable=False, default="USD")
    currency_digits = Column(Integer, nullable=False, default=2)

    # --- Reports, news, mail ------------------------------------------------
    reports_mode = Column(Integer, nullable=False, default=0)
    reports_flags = Column(Integer, nullable=False, default=0)
    reports_email = Column(String(256), nullable=False, default="")
    news_mode = Column(Integer, nullable=False, default=2)
    news_category = Column(String(256), nullable=False, default="")
    news_langs = Column(JSONB, nullable=False, default=list)
    mail_mode = Column(Integer, nullable=False, default=1)

    # --- Trading ------------------------------------------------------------
    trade_flags = Column(Integer, nullable=False, default=0)
    trade_transfer_mode = Column(Integer, nullable=False, default=0)
    trade_interestrate = Column(Numeric(20, 8), nullable=False, default=0)
    trade_virtual_credit = Column(Numeric(20, 8), nullable=False, default=0)

    # --- Margin. margin_call / margin_stop_out are PERCENT ------------------
    margin_mode = Column(Integer, nullable=False, default=2)
    margin_flags = Column(Integer, nullable=False, default=0)
    margin_so_mode = Column(Integer, nullable=False, default=0)   # StopOutMode
    margin_free_mode = Column(Integer, nullable=False, default=1)  # FreeMarginMode
    margin_call = Column(Numeric(6, 2), nullable=False, default=50)
    margin_stop_out = Column(Numeric(6, 2), nullable=False, default=30)
    margin_free_profit_mode = Column(Integer, nullable=False, default=0)
    # Leverage is not a top-level MT5 ConfigGroups scalar; MT5 carries it through the
    # group's symbol configuration and the account. Our domain keeps it on
    # MarginProfile, so it lives in margin_json and is mirrored here for querying.
    leverage_default = Column(Integer, nullable=False, default=100)
    leverage_max = Column(Integer, nullable=False, default=500)

    # --- Demo ---------------------------------------------------------------
    demo_leverage = Column(Integer, nullable=False, default=10)
    demo_deposit = Column(Numeric(20, 8), nullable=False, default=0)
    demo_trades_clean = Column(Integer, nullable=False, default=0)

    # --- Limits -------------------------------------------------------------
    limit_history = Column(Integer, nullable=False, default=0)
    limit_orders = Column(Integer, nullable=False, default=0)
    limit_symbols = Column(Integer, nullable=False, default=0)
    limit_positions = Column(Integer, nullable=False, default=0)
    limit_positions_volume = Column(Numeric(20, 8), nullable=False, default=0)

    # --- Nested domain value objects (JSONB, one source of truth each) ------
    # MarginProfile minus the fields promoted to scalar columns above.
    margin_json = Column(JSONB, nullable=False, default=dict)
    # List[CommissionRule] + CommissionTier, in MT5 Commissions/Tiers shape.
    commissions_json = Column(JSONB, nullable=False, default=list)
    # List[GroupSymbolOverride], in MT5 Symbols shape (64 fields per override).
    symbol_overrides_json = Column(JSONB, nullable=False, default=list)
    permissions_json = Column(JSONB, nullable=False, default=dict)
    swaps_json = Column(JSONB, nullable=False, default=dict)
    routing_json = Column(JSONB, nullable=False, default=dict)

    # --- MT5 fields we do not model yet, preserved for lossless export ------
    mt5_extra = Column(JSONB, nullable=False, default=dict)
    # The wire scale of each decimal, exactly as MT5 wrote it. Without this an
    # export cannot reproduce "50.00" vs "50" vs "50.00000000", and MT5 Administrator
    # is sensitive to scale. See infrastructure.mt5.codec.wire_scale.
    mt5_scale = Column(JSONB, nullable=False, default=dict)
    # The COMPLETE MT5 wire record this row was imported from, when it came from a
    # real server export. Export starts from this and overlays domain-owned fields,
    # which is the only reliable way to reproduce a record whose 27 (group) or 70
    # (symbol) unmodelled fields were never represented in the domain. NULL for rows
    # created natively, which export from the columns alone.
    mt5_source = Column(JSONB, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    __table_args__ = (
        Index("idx_groups_account_type", "account_type"),
        Index("idx_groups_server", "server_id"),
    )


class SymbolModel(Base):
    """MT5 IMTConSymbol - the instrument specification.

    MT5 has 121 fields here; we model 51 and preserve the rest in ``mt5_extra``.
    The 16-way margin rate matrix is stored as individual columns rather than JSONB
    because it is read on every margin calculation and must be indexable/queryable.
    """

    __tablename__ = "symbols"

    # --- Identity -----------------------------------------------------------
    name = Column(String(64), primary_key=True)             # MT5 Symbol
    path = Column(String(256), nullable=False, default="")  # MT5 Path, "FX\\Forex\\EURUSD"
    symbol_id = Column(String(64), nullable=True, unique=True, index=True)
    description = Column(String(256), nullable=False, default="")

    # --- Currencies. MT5 distinguishes THREE; base/quote are modelled and the
    #     profit/margin currencies ride in mt5_extra until the domain grows them.
    # MT5 CurrencyBase / CurrencyProfit / CurrencyMargin. quote_currency holds
    # CurrencyProfit, which is the currency PnL is denominated in - for an FX pair it is
    # the quote leg, which is why the name is kept. margin_currency is separate because
    # MT5 says it need not equal either.
    base_currency = Column(String(8), nullable=False, default="USD")
    quote_currency = Column(String(8), nullable=False, default="USD")
    margin_currency = Column(String(8), nullable=False, default="")

    # --- Price geometry -----------------------------------------------------
    digits = Column(Integer, nullable=False, default=5)
    # MT5 has two price-step fields and they are NOT interchangeable. Point is the
    # price-precision step and is always populated (scale 8 on all 362 symbols in the
    # reference export). TickSize is the tick ALIGNMENT step and is frequently zero -
    # every crypto symbol there has TickSize = 0. The two differ on all 362. The
    # column names keep MT5's own spelling so neither can be mistaken for the other,
    # and the domain maps Point -> Symbol.tick_size (what price quantisation must use)
    # and TickSize -> Symbol.mt5_tick_size.
    point = Column(Numeric(20, 8), nullable=False, default=0)
    mt5_tick_size = Column(Numeric(20, 8), nullable=False, default=0)
    tick_value = Column(Numeric(20, 8), nullable=False, default=0)
    contract_size = Column(Numeric(20, 8), nullable=False, default=100000)

    # --- Trading behaviour --------------------------------------------------
    calc_mode = Column(Integer, nullable=False, default=0)
    trade_mode = Column(Integer, nullable=False, default=4)
    exec_mode = Column(Integer, nullable=False, default=2)
    gtc_mode = Column(Integer, nullable=False, default=0)
    fill_flags = Column(Integer, nullable=False, default=0)
    expiration_flags = Column(Integer, nullable=False, default=0)
    order_flags = Column(Integer, nullable=False, default=0)
    is_trade_allowed = Column(Boolean, nullable=False, default=True)

    # --- Spread -------------------------------------------------------------
    spread = Column(Integer, nullable=False, default=0)
    spread_balance = Column(Integer, nullable=False, default=0)

    # --- Levels -------------------------------------------------------------
    stops_level = Column(Integer, nullable=False, default=0)
    freeze_level = Column(Integer, nullable=False, default=0)

    # --- Volume limits ------------------------------------------------------
    volume_min = Column(Numeric(20, 8), nullable=False, default=0)
    volume_max = Column(Numeric(20, 8), nullable=False, default=0)
    volume_step = Column(Numeric(20, 8), nullable=False, default=0)
    volume_limit = Column(Numeric(20, 8), nullable=False, default=0)

    # --- Margin rates: the full MT5 16-way matrix ---------------------------
    margin_initial_buy = Column(Numeric(20, 8), nullable=False, default=1)
    margin_initial_sell = Column(Numeric(20, 8), nullable=False, default=1)
    margin_initial_buy_limit = Column(Numeric(20, 8), nullable=False, default=1)
    margin_initial_sell_limit = Column(Numeric(20, 8), nullable=False, default=1)
    margin_initial_buy_stop = Column(Numeric(20, 8), nullable=False, default=1)
    margin_initial_sell_stop = Column(Numeric(20, 8), nullable=False, default=1)
    margin_initial_buy_stop_limit = Column(Numeric(20, 8), nullable=False, default=1)
    margin_initial_sell_stop_limit = Column(Numeric(20, 8), nullable=False, default=1)
    margin_maintenance_buy = Column(Numeric(20, 8), nullable=False, default=1)
    margin_maintenance_sell = Column(Numeric(20, 8), nullable=False, default=1)
    margin_maintenance_buy_limit = Column(Numeric(20, 8), nullable=False, default=1)
    margin_maintenance_sell_limit = Column(Numeric(20, 8), nullable=False, default=1)
    margin_maintenance_buy_stop = Column(Numeric(20, 8), nullable=False, default=1)
    margin_maintenance_sell_stop = Column(Numeric(20, 8), nullable=False, default=1)
    margin_maintenance_buy_stop_limit = Column(Numeric(20, 8), nullable=False, default=1)
    margin_maintenance_sell_stop_limit = Column(Numeric(20, 8), nullable=False, default=1)

    # --- Swaps --------------------------------------------------------------
    swap_mode = Column(Integer, nullable=False, default=0)
    swap_long = Column(Numeric(20, 8), nullable=False, default=0)
    swap_short = Column(Numeric(20, 8), nullable=False, default=0)
    swap_3day = Column(Integer, nullable=False, default=3)   # MT5 Swap3Day, weekday
    swap_year_days = Column(Integer, nullable=False, default=0)

    # --- Sessions, in MT5's Sunday-first 7-array shape ----------------------
    sessions_quotes_json = Column(JSONB, nullable=False, default=list)
    sessions_trades_json = Column(JSONB, nullable=False, default=list)

    # --- Lifetime -----------------------------------------------------------
    time_start = Column(BigInteger, nullable=False, default=0)
    time_expiration = Column(BigInteger, nullable=False, default=0)

    # --- Derivatives --------------------------------------------------------
    option_mode = Column(Integer, nullable=False, default=0)
    strike_price = Column(Numeric(20, 8), nullable=False, default=0)
    face_value = Column(Numeric(20, 8), nullable=False, default=0)
    face_value_currency = Column(String(8), nullable=False, default="USD")

    # --- MT5 fields we do not model yet, preserved for lossless export ------
    mt5_extra = Column(JSONB, nullable=False, default=dict)
    mt5_scale = Column(JSONB, nullable=False, default=dict)
    # The COMPLETE MT5 wire record this row was imported from, when it came from a
    # real server export. Export starts from this and overlays domain-owned fields,
    # which is the only reliable way to reproduce a record whose 27 (group) or 70
    # (symbol) unmodelled fields were never represented in the domain. NULL for rows
    # created natively, which export from the columns alone.
    mt5_source = Column(JSONB, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    __table_args__ = (
        Index("idx_symbols_path", "path"),
    )
