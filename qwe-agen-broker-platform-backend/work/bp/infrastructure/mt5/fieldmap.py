"""
MT5 Administrator field names <-> broker-platform domain field names.

This is the single authoritative translation table between the MT5 wire format and
our domain model. It exists so that import/export to a real MT5 server stays
possible, and so that "which MT5 fields have we not modelled yet?" is answered by
reading one file rather than by grepping.

Field lists were extracted from a live MT5 Administrator export, not from prose
documentation, so they are exact:

    ConfigSymbols         121 fields   (362 symbols in the reference export)
    ConfigGroups           44 fields   (20 groups, incl. Commissions and Symbols)
    Group symbol override  64 fields
    Commission             12 fields + Tiers (8 fields)
    ConfigRouting          12 fields
    ConfigGateways         22 fields
    ConfigHolidays          8 fields
    ConfigManagers          9 fields

Each entry is ``Field(mt5_name, domain_path, kind)``.

``domain_path`` is a dotted path into our domain object, e.g. ``"margin_rates.initial_buy"``
or ``"margin.margin_call_level"``. An EMPTY domain_path means MT5 has the field and we
do not model it yet. Those entries are the gap list, and ``gap_report()`` turns them
into a coverage percentage per entity so the gap is a number you can track.

``kind`` drives typed conversion in ``codec.py``:

    STR       opaque string, passed through
    DEC       decimal; wire scale preserved per field per record
    INT       integer
    FLAGS     decimal-encoded bitmask (e.g. TradeFlags "87")
    BOOL01    "0" / "1"
    SESSIONS  7-element Sunday-first array of {Open, Close} minute ranges
    NESTED    array of objects, with its own field table where we have one
    STRLIST   array of strings

UNIT CONVENTION, decided once and for all here:

    MT5 stores MarginCall and MarginStopOut as PERCENT ("50.00" and "30.00" for
    group real\\real in the reference export). Our domain therefore also stores
    PERCENT. Any code comparing a margin level against 0.8 / 0.5 is wrong.
"""

from __future__ import annotations

from typing import Dict, List, NamedTuple, Tuple

STR = "str"
DEC = "dec"
INT = "int"
FLAGS = "flags"
BOOL01 = "bool01"
SESSIONS = "sessions"
NESTED = "nested"
STRLIST = "strlist"


class Field(NamedTuple):
    """One MT5 field and where it lives in our domain model."""

    mt5: str
    domain: str  # dotted path; "" == not modelled yet
    kind: str = STR


# ---------------------------------------------------------------------------
# ConfigSymbols - 121 fields
# ---------------------------------------------------------------------------

SYMBOL_FIELDS: Tuple[Field, ...] = (
    # Identity & classification
    Field("Symbol", "name", STR),
    Field("Path", "path", STR),
    Field("ISIN", "", STR),
    Field("CFI", "", STR),
    Field("Category", "", STR),
    Field("Exchange", "", STR),
    Field("Description", "description", STR),
    Field("International", "", STR),
    Field("Sector", "", STR),
    Field("Industry", "", STR),
    Field("Country", "", STR),
    Field("Basis", "", STR),
    Field("Source", "", STR),
    Field("Page", "", STR),
    # Currencies. MT5 distinguishes THREE; we model two. CurrencyProfit and
    # CurrencyMargin are the root cause of our cross-currency PnL and margin bugs:
    # the margin currency need not equal the quote currency.
    # All THREE currencies are now mapped. They were diagnosed in M1 as the root cause of
    # the cross-currency PnL and margin bugs and left unmapped; mapping them is what makes
    # a EURJPY position on a USD account computable at all. The *Digits fields stay in the
    # quarantine: they are presentation precision, not trading semantics.
    Field("CurrencyBase", "base_currency", STR),
    Field("CurrencyBaseDigits", "", INT),
    Field("CurrencyProfit", "quote_currency", STR),
    Field("CurrencyProfitDigits", "", INT),
    Field("CurrencyMargin", "margin_currency", STR),
    Field("CurrencyMarginDigits", "", INT),
    # Presentation
    Field("Color", "", STR),
    Field("ColorBackground", "", STR),
    # Price geometry
    Field("Digits", "digits", INT),
    # Point is the price-precision step and is ALWAYS populated (scale 8 on all 362
    # symbols in the reference export). TickSize is a DIFFERENT field and is often
    # zero or coarser: Point != TickSize for 131 of 362 symbols, including every
    # crypto (ADAUSD Point=0.00001000 vs TickSize=0.00000). Our domain has one slot,
    # so Point wins and TickSize is quarantined in _mt5_extra to keep export lossless.
    # Adding a distinct tick_size to Symbol is a tracked gap, not an oversight.
    Field("Point", "tick_size", DEC),
    Field("Multiply", "", INT),
    Field("TickFlags", "", FLAGS),
    Field("TickBookDepth", "", INT),
    Field("TickChartMode", "", INT),
    Field("SubscriptionsDelay", "", INT),
    # Tick filtration - the spike / stale-quote rejection logic.
    # market_data/engine.py still carries "TODO: Phase 11 - Implement spike filter".
    Field("FilterSoft", "", DEC),
    Field("FilterSoftTicks", "", INT),
    Field("FilterHard", "", DEC),
    Field("FilterHardTicks", "", INT),
    Field("FilterDiscard", "", DEC),
    Field("FilterSpreadMax", "", DEC),
    Field("FilterSpreadMin", "", DEC),
    Field("FilterGap", "", DEC),
    Field("FilterGapTicks", "", INT),
    # Trading behaviour
    Field("TradeMode", "trade_mode", INT),
    Field("TradeFlags", "", FLAGS),
    Field("CalcMode", "calc_mode", INT),
    Field("ExecMode", "exec_mode", INT),
    Field("GTCMode", "gtc_mode", INT),
    Field("FillFlags", "fill_flags", FLAGS),
    Field("ExpirFlags", "expiration_flags", FLAGS),
    Field("OrderFlags", "order_flags", FLAGS),
    # Spread
    Field("Spread", "spread", INT),
    Field("SpreadBalance", "spread_balance", INT),
    Field("SpreadDiff", "spread_diff", INT),
    Field("SpreadDiffBalance", "spread_diff_balance", INT),
    # Contract
    Field("TickValue", "tick_value", DEC),
    Field("TickSize", "mt5_tick_size", DEC),  # NOT the same as Point - see note above
    Field("ContractSize", "contract_size", DEC),
    Field("StopsLevel", "stops_level", INT),
    Field("FreezeLevel", "freeze_level", INT),
    Field("QuotesTimeout", "", INT),
    # Volume limits. The *Ext variants are integer-scaled (MT5 multiplies by 10^8 to
    # avoid floating point) and are what a real server actually enforces.
    Field("VolumeMin", "volume_min", DEC),
    Field("VolumeMinExt", "", INT),
    Field("VolumeMax", "volume_max", DEC),
    Field("VolumeMaxExt", "", INT),
    Field("VolumeStep", "volume_step", DEC),
    Field("VolumeStepExt", "", INT),
    Field("VolumeLimit", "volume_limit", DEC),
    Field("VolumeLimitExt", "", INT),
    # Margin - the full 16-way matrix, plus three aggregates we do not model.
    Field("MarginFlags", "", FLAGS),
    Field("MarginInitial", "", DEC),
    Field("MarginMaintenance", "", DEC),
    Field("MarginInitialBuy", "margin_rates.initial_buy", DEC),
    Field("MarginInitialSell", "margin_rates.initial_sell", DEC),
    Field("MarginInitialBuyLimit", "margin_rates.initial_buy_limit", DEC),
    Field("MarginInitialSellLimit", "margin_rates.initial_sell_limit", DEC),
    Field("MarginInitialBuyStop", "margin_rates.initial_buy_stop", DEC),
    Field("MarginInitialSellStop", "margin_rates.initial_sell_stop", DEC),
    Field("MarginInitialBuyStopLimit", "margin_rates.initial_buy_stop_limit", DEC),
    Field("MarginInitialSellStopLimit", "margin_rates.initial_sell_stop_limit", DEC),
    Field("MarginMaintenanceBuy", "margin_rates.maintenance_buy", DEC),
    Field("MarginMaintenanceSell", "margin_rates.maintenance_sell", DEC),
    Field("MarginMaintenanceBuyLimit", "margin_rates.maintenance_buy_limit", DEC),
    Field("MarginMaintenanceSellLimit", "margin_rates.maintenance_sell_limit", DEC),
    Field("MarginMaintenanceBuyStop", "margin_rates.maintenance_buy_stop", DEC),
    Field("MarginMaintenanceSellStop", "margin_rates.maintenance_sell_stop", DEC),
    Field("MarginMaintenanceBuyStopLimit", "margin_rates.maintenance_buy_stop_limit", DEC),
    Field("MarginMaintenanceSellStopLimit", "margin_rates.maintenance_sell_stop_limit", DEC),
    Field("MarginLiquidity", "", DEC),
    Field("MarginHedged", "", DEC),
    Field("MarginCurrency", "", DEC),
    # Swaps - note the per-day rate curve, which we do not model at all.
    Field("SwapMode", "swap_mode", INT),
    Field("SwapLong", "swap_long", DEC),
    Field("SwapShort", "swap_short", DEC),
    Field("SwapFlags", "", FLAGS),
    Field("Swap3Day", "swap_3day", INT),
    Field("SwapYearDay", "swap_year_days", INT),
    Field("SwapRateSunday", "", DEC),
    Field("SwapRateMonday", "", DEC),
    Field("SwapRateTuesday", "", DEC),
    Field("SwapRateWednesday", "", DEC),
    Field("SwapRateThursday", "", DEC),
    Field("SwapRateFriday", "", DEC),
    Field("SwapRateSaturday", "", DEC),
    # Lifetime
    Field("TimeStart", "time_start", INT),
    Field("TimeExpiration", "time_expiration", INT),
    Field("SessionsQuotes", "quote_sessions", SESSIONS),
    Field("SessionsTrades", "trade_sessions", SESSIONS),
    # Request Execution
    Field("REFlags", "", FLAGS),
    Field("RETimeout", "", INT),
    # Instant Execution - needed for slippage and stale-quote rejection.
    Field("IECheckMode", "", INT),
    Field("IETimeout", "", INT),
    Field("IESlipProfit", "", INT),
    Field("IESlipLosing", "", INT),
    Field("IEVolumeMax", "", DEC),
    Field("IEVolumeMaxExt", "", INT),
    # Derivatives & bonds
    Field("PriceSettle", "", DEC),
    Field("PriceLimitMax", "", DEC),
    Field("PriceLimitMin", "", DEC),
    Field("PriceStrike", "strike_price", DEC),
    Field("OptionMode", "option_mode", INT),
    Field("FaceValue", "face_value", DEC),
    Field("AccruedInterest", "", DEC),
    Field("SpliceType", "", INT),
    Field("SpliceTimeType", "", INT),
    Field("SpliceTimeDays", "", INT),
)

# ---------------------------------------------------------------------------
# ConfigGroups - 44 fields
# ---------------------------------------------------------------------------

GROUP_FIELDS: Tuple[Field, ...] = (
    Field("Group", "name", STR),
    Field("Server", "server_id", INT),
    Field("PermissionsFlags", "", FLAGS),
    # Extended authentication. AuthOTPMode is 0 in the reference export, i.e. the
    # reference broker does not use OTP either - safe to defer.
    Field("AuthMode", "", INT),
    Field("AuthPasswordMin", "", INT),
    Field("AuthOTPMode", "", INT),
    # White label
    Field("Company", "", STR),
    Field("CompanyPage", "", STR),
    Field("CompanyEmail", "", STR),
    Field("CompanySupportPage", "", STR),
    Field("CompanySupportEmail", "", STR),
    Field("CompanyCatalog", "", STR),
    Field("CompanyDepositURL", "", STR),
    Field("CompanyWithdrawalURL", "", STR),
    # Currency
    Field("Currency", "currency", STR),
    Field("CurrencyDigits", "currency_digits", INT),
    # Reports & mail - deferred by scope
    Field("ReportsMode", "", INT),
    Field("ReportsFlags", "", FLAGS),
    Field("ReportsEmail", "", STR),
    Field("NewsMode", "news_mode", INT),
    Field("NewsCategory", "", STR),
    Field("NewsLangs", "", STRLIST),
    Field("MailMode", "", INT),
    # Trading
    Field("TradeFlags", "trade_flags", FLAGS),
    Field("TradeTransferMode", "", INT),
    Field("TradeInterestrate", "", DEC),
    Field("TradeVirtualCredit", "", DEC),
    # Margin. MarginCall / MarginStopOut are PERCENT.
    Field("MarginMode", "margin.mode", INT),
    Field("MarginFlags", "margin.flags", FLAGS),
    Field("MarginSOMode", "margin.stop_out_mode", INT),
    Field("MarginFreeMode", "margin.free_margin_mode", INT),
    Field("MarginCall", "margin.margin_call_level", DEC),
    Field("MarginStopOut", "margin.stop_out_level", DEC),
    Field("MarginFreeProfitMode", "", INT),
    # Demo
    Field("DemoLeverage", "", INT),
    Field("DemoDeposit", "", DEC),
    Field("DemoTradesClean", "", INT),
    # Limits
    Field("LimitHistory", "", INT),
    Field("LimitOrders", "limit_orders", INT),
    Field("LimitSymbols", "limit_symbols", INT),
    Field("LimitPositions", "limit_positions", INT),
    Field("LimitPositionsVolume", "", DEC),
    # Nested configuration
    Field("Commissions", "commissions", NESTED),
    Field("Symbols", "symbol_overrides", NESTED),
)

# ---------------------------------------------------------------------------
# Group -> Commissions[] - 12 fields + Tiers
# ---------------------------------------------------------------------------

COMMISSION_FIELDS: Tuple[Field, ...] = (
    Field("Name", "name", STR),
    Field("Description", "", STR),
    Field("Path", "symbol_pattern", STR),
    Field("Mode", "", INT),
    Field("RangeMode", "", INT),
    Field("ChargeMode", "", INT),
    Field("TurnoverCurrency", "currency", STR),
    Field("EntryMode", "", INT),
    Field("ActionMode", "", INT),
    Field("ProfitMode", "", INT),
    Field("ReasonMode", "", FLAGS),
    Field("Tiers", "tiers", NESTED),
)

COMMISSION_TIER_FIELDS: Tuple[Field, ...] = (
    Field("Mode", "", INT),
    Field("Type", "type", INT),
    Field("Value", "rate", DEC),
    Field("Minimal", "min_value", DEC),
    Field("Maximal", "max_value", DEC),
    Field("RangeFrom", "volume_min", DEC),
    Field("RangeTo", "volume_max", DEC),
    Field("Currency", "currency", STR),
)

# ---------------------------------------------------------------------------
# Group -> Symbols[] (per-group symbol overrides) - 64 fields
# We model 12 of these. This is the widest gap in the whole configuration plane.
# ---------------------------------------------------------------------------

GROUP_SYMBOL_FIELDS: Tuple[Field, ...] = (
    Field("Path", "symbol_pattern", STR),
    Field("TradeMode", "trade_mode", INT),
    Field("ExecMode", "execution_mode", INT),
    Field("FillFlags", "", FLAGS),
    Field("ExpirFlags", "", FLAGS),
    Field("OrderFlags", "", FLAGS),
    Field("SpreadDiff", "spread_diff", INT),
    Field("SpreadDiffBalance", "spread_diff_balance", INT),
    Field("StopsLevel", "", INT),
    Field("FreezeLevel", "", INT),
    Field("VolumeMin", "volume_min", DEC),
    Field("VolumeMinExt", "", INT),
    Field("VolumeMax", "volume_max", DEC),
    Field("VolumeMaxExt", "", INT),
    Field("VolumeStep", "", DEC),
    Field("VolumeStepExt", "", INT),
    Field("VolumeLimit", "volume_limit", DEC),
    Field("VolumeLimitExt", "", INT),
    Field("MarginFlags", "", FLAGS),
    Field("MarginInitial", "", DEC),
    Field("MarginMaintenance", "", DEC),
    Field("MarginInitialBuy", "margin_rate_initial_buy", DEC),
    Field("MarginInitialSell", "margin_rate_initial_sell", DEC),
    Field("MarginInitialBuyLimit", "", DEC),
    Field("MarginInitialSellLimit", "", DEC),
    Field("MarginInitialBuyStop", "", DEC),
    Field("MarginInitialSellStop", "", DEC),
    Field("MarginInitialBuyStopLimit", "", DEC),
    Field("MarginInitialSellStopLimit", "", DEC),
    Field("MarginMaintenanceBuy", "", DEC),
    Field("MarginMaintenanceSell", "", DEC),
    Field("MarginMaintenanceBuyLimit", "", DEC),
    Field("MarginMaintenanceSellLimit", "", DEC),
    Field("MarginMaintenanceBuyStop", "", DEC),
    Field("MarginMaintenanceSellStop", "", DEC),
    Field("MarginMaintenanceBuyStopLimit", "", DEC),
    Field("MarginMaintenanceSellStopLimit", "", DEC),
    Field("MarginLiquidity", "", DEC),
    Field("MarginHedged", "", DEC),
    Field("MarginCurrency", "", DEC),
    Field("SwapMode", "", INT),
    Field("SwapLong", "swap_long", DEC),
    Field("SwapShort", "swap_short", DEC),
    Field("Swap3Day", "", INT),
    Field("SwapFlags", "", FLAGS),
    Field("SwapYearDay", "", INT),
    Field("SwapRateSunday", "", DEC),
    Field("SwapRateMonday", "", DEC),
    Field("SwapRateTuesday", "", DEC),
    Field("SwapRateWednesday", "", DEC),
    Field("SwapRateThursday", "", DEC),
    Field("SwapRateFriday", "", DEC),
    Field("SwapRateSaturday", "", DEC),
    Field("REFlags", "", FLAGS),
    Field("RETimeout", "", INT),
    Field("IEFlags", "", FLAGS),
    Field("IECheckMode", "", INT),
    Field("IETimeout", "", INT),
    Field("IESlipProfit", "", INT),
    Field("IESlipLosing", "", INT),
    Field("IEVolumeMax", "", DEC),
    Field("IEVolumeMaxExt", "", INT),
    Field("PermissionsFlags", "", FLAGS),
    Field("PermissionsBookdepth", "", INT),
)

# ---------------------------------------------------------------------------
# ConfigRouting - the A-book / B-book / dealer decision table
# ---------------------------------------------------------------------------

ROUTING_FIELDS: Tuple[Field, ...] = (
    Field("Name", "name", STR),
    Field("Mode", "mode", INT),                     # 0 = disabled, nonzero = enabled
    Field("Request", "request_mask", FLAGS),        # EnRouteFlags bitmask (25 request types)
    Field("Type", "type_mask", FLAGS),              # bitmask over the 8 order types
    Field("Flags", "flags", FLAGS),
    Field("Action", "action", INT),                 # EnRouteAction: 1001 = dealers, 1003 = reject, 1005 = confirm-client...
    Field("ActionValueInt", "action_value_int", INT),
    Field("ActionValueUInt", "action_value_uint", INT),
    Field("ActionValueFloat", "action_value_float", DEC),
    Field("ActionValueString", "action_value_string", STR),
    Field("Conditions", "conditions", NESTED),
    Field("Dealers", "dealers", NESTED),
)

#: Routing rule conditions (IMTConCondition). Rule = EnConditionRule comparison:
#: 0 EQ, 1 NOT_EQ, 2 GREATER, 3 NOT_LESS, 4 LESS, 5 NOT_GREATER.
ROUTING_CONDITION_FIELDS: Tuple[Field, ...] = (
    Field("Condition", "code", INT),
    Field("Rule", "rule", INT),
    Field("ValueInt", "value_int", INT),
    Field("ValueUInt", "value_uint", INT),
    Field("ValueFloat", "value_float", DEC),
    Field("ValueString", "value_string", STR),
)

#: Routing rule dealers: a gateway or a manager with the Dealing right.
ROUTING_DEALER_FIELDS: Tuple[Field, ...] = (
    Field("Login", "login", INT),
    Field("Name", "name", STR),
)

# ---------------------------------------------------------------------------
# ConfigGateways - LP connectors (A-book). No gateway implementation exists yet.
# NOTE: GatewayPassword / TradingPassword are PLAINTEXT in a real export. Never
# commit a populated gateway file; see the security note in the project analysis.
# ---------------------------------------------------------------------------

#: ConfigGatewayTranslates / ConfigFeederTranslates - one price-translation row.
#:
#: Wire shape, verbatim from the live TCTrader export (Data Feeds, feeder "Feeder"):
#:     {"Source": "*", "Symbol": "*!", "BidMarkup": "0", "AskMarkup": "0",
#:      "Digits": "0"}
#:
#: Semantics, from the Administrator guide (Gateways -> Translations, and the ECN
#: Price Translations page):
#:   * Source = the symbol name in the EXTERNAL system; Symbol = the name on this
#:     platform. Renaming and markup are the same mechanism.
#:   * Bid / Ask are markup in POINTS of the SOURCE symbol. "A positive value
#:     increases the price, a negative one decreases it." The guide's convention is
#:     bid negative, ask positive - widening outward - and warns that the reverse
#:     "may get a negative spread".
#:   * ONE point is the source symbol's own precision: "if a symbol has 4 decimal
#:     places, the markup of 1 will change prices by 0.0001; for symbols with 5
#:     decimal places the markup will be equal to 0.00001".
#:   * FIRST MATCH WINS by list order: "If more than one translation settings match
#:     the same symbol on the platform side, only the one located higher in the list
#:     will be applied." EURUSD.GW->EURUSD (-1/+1) beats *.GW->* (-2/+2).
#:   * Masks support a single '*'. The guide says settings with two '*' or a '!'
#:     negation "are ignored by the platform" - so they are stored losslessly and
#:     refused at resolution time rather than guessed at.
TRANSLATE_FIELDS: Tuple[Field, ...] = (
    Field("Source", "source", STR),
    Field("Symbol", "symbol", STR),
    Field("BidMarkup", "bid_markup", INT),
    Field("AskMarkup", "ask_markup", INT),
    Field("Digits", "digits", INT),
)

GATEWAY_FIELDS: Tuple[Field, ...] = (
    Field("Name", "name", STR),
    Field("Module", "", STR),
    Field("GatewayServer", "", STR),
    Field("GatewayLogin", "", INT),
    Field("GatewayPassword", "", STR),
    Field("TradingServer", "", STR),
    Field("TradingLogin", "", INT),
    Field("TradingPassword", "", STR),
    Field("Enable", "is_enabled", BOOL01),
    Field("Flags", "", FLAGS),
    Field("TransactionsCollectDays", "", INT),
    Field("ID", "id", INT),
    Field("Gateway", "", STR),
    Field("AccountSummary", "", BOOL01),
    Field("TimeoutReconnect", "", INT),
    Field("TimeoutSleep", "", INT),
    Field("AttemptsSleep", "", INT),
    Field("State", "", NESTED),
    Field("Params", "", NESTED),
    #: M13: modelled rather than quarantined. Groups is the mechanism MT5 uses to
    #: give different client groups different markups - "the unlimited number of
    #: configurations with different settings can be created for each module", and
    #: the live export has a gateway literally named "MetaTrader 5 Gateway clone"
    #: whose only distinction is Groups=['*', 'real\\*'].
    Field("Symbols", "symbols", STRLIST),
    Field("Groups", "groups", STRLIST),
    Field("Translates", "translates", NESTED),
)

# ---------------------------------------------------------------------------
# ConfigFeeders - price/news sources, hosted on the HISTORY server
# ---------------------------------------------------------------------------

FEEDER_FIELDS: Tuple[Field, ...] = (
    Field("Feeder", "name", STR),
    Field("Module", "", STR),
    Field("GatewayServer", "", STR),
    Field("GatewayLogin", "", INT),
    Field("GatewayPassword", "", STR),
    Field("FeedServer", "", STR),
    Field("FeedLogin", "", INT),
    Field("FeedPassword", "", STR),
    Field("Enable", "is_enabled", BOOL01),
    Field("Mode", "", INT),
    Field("TimeoutReconnect", "", INT),
    #: M13: a feeder's Translations tab has the SAME shape as a gateway's, and the
    #: live export carries a real row on the "Feeder" source:
    #:     {"Source":"*","Symbol":"*!","BidMarkup":"0","AskMarkup":"0","Digits":"0"}
    #: Note Symbol "*!" - a '!' negation mask. The guide says masks with two '*' or
    #: a '!' "are ignored by the platform", so this row is stored losslessly and
    #: refused at resolution time rather than guessed at.
    Field("Symbols", "symbols", STRLIST),
    Field("Groups", "groups", STRLIST),
    Field("Translates", "translates", NESTED),
)

# ---------------------------------------------------------------------------
# ConfigHolidays
# ---------------------------------------------------------------------------

HOLIDAY_FIELDS: Tuple[Field, ...] = (
    Field("Mode", "", INT),
    Field("Year", "year", INT),
    Field("Month", "month", INT),
    Field("Day", "day", INT),
    Field("From", "", INT),
    Field("To", "", INT),
    Field("Description", "description", STR),
    Field("Symbols", "", STRLIST),
)

# ---------------------------------------------------------------------------
# ConfigManagers - administrator / dealer / API accounts
# ---------------------------------------------------------------------------

MANAGER_FIELDS: Tuple[Field, ...] = (
    Field("Login", "login", INT),
    Field("Name", "name", STR),
    Field("Mailbox", "email", STR),
    Field("Server", "server_id", INT),
    # Rights is a FIXED-LENGTH 128-element array of "0"/"1" strings, one element per
    # manager right, positionally indexed - not a list of granted right names. In the
    # reference export all 9 managers have all 128 rights set, which is what an
    # auto-created administrator looks like. A dealer or an API-only manager would
    # have most positions "0". This positional array IS the role model needed for
    # Stage 2 (admin vs dealer vs manager vs read-only).
    Field("Rights", "rights", STRLIST),
    Field("RequestLimitLogs", "", INT),
    Field("RequestLimitReports", "", INT),
    # Groups scopes which client groups this manager may administer; [{"Group":"*"}]
    # means all. Mirrors the MT5 rule that a manager only administers accounts on the
    # trade server where its own account lives.
    Field("Groups", "group_scope", NESTED),
    Field("Access", "", NESTED),
)


#: Registry of every field table, keyed by MT5 config section.
TABLES: Dict[str, Tuple[Field, ...]] = {
    "ConfigSymbols": SYMBOL_FIELDS,
    "ConfigGroups": GROUP_FIELDS,
    "ConfigGatewayTranslates": TRANSLATE_FIELDS,
    "ConfigFeederTranslates": TRANSLATE_FIELDS,
    "ConfigGroupCommissions": COMMISSION_FIELDS,
    "ConfigGroupCommissionTiers": COMMISSION_TIER_FIELDS,
    "ConfigGroupSymbols": GROUP_SYMBOL_FIELDS,
    "ConfigRouting": ROUTING_FIELDS,
    "ConfigGateways": GATEWAY_FIELDS,
    "ConfigFeeders": FEEDER_FIELDS,
    "ConfigHolidays": HOLIDAY_FIELDS,
    "ConfigManagers": MANAGER_FIELDS,
}


def index(table: Tuple[Field, ...]) -> Dict[str, Field]:
    """Look up fields by MT5 name."""
    return {f.mt5: f for f in table}


def domain_index(table: Tuple[Field, ...]) -> Dict[str, Field]:
    """Look up fields by domain path (modelled fields only)."""
    return {f.domain: f for f in table if f.domain}


def gap_report(table: Tuple[Field, ...], label: str) -> Dict[str, object]:
    """Coverage of one MT5 entity by our domain model."""
    modelled = [f.mt5 for f in table if f.domain]
    missing = [f.mt5 for f in table if not f.domain]
    total = len(table)
    return {
        "entity": label,
        "mt5_fields": total,
        "modelled": len(modelled),
        "missing": len(missing),
        "coverage_pct": round(100.0 * len(modelled) / total, 1) if total else 0.0,
        "missing_fields": missing,
    }


def all_gaps() -> List[Dict[str, object]]:
    """Coverage report for every mapped MT5 entity."""
    return [gap_report(table, name) for name, table in TABLES.items()]
