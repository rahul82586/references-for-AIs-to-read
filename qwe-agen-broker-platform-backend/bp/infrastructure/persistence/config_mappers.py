"""
Domain <-> database mappers for the CONFIGURATION PLANE (Group, Symbol).

THE ROUTING RULE: every conversion goes through the MT5 wire codec.

    domain Group --(MT5-shaped record)--> codec.domain_to_record --> GroupModel columns
    GroupModel   --(MT5 wire record)----> codec.record_to_domain --> domain Group

That detour is deliberate and buys three things:

1. The database row and an MT5 export are the SAME shape by construction, so there is
   no second independent mapping to drift. Drift between four competing `groups`
   schemas is what made this codebase unrunnable.
2. Persistence is lossless for MT5 fields we do not model yet. `mt5_extra` JSONB holds
   the codec's quarantine and `mt5_scale` its observed decimal scales, so a group
   imported from a real server exports back byte-identically even though our domain
   covers only 17 of MT5's 44 ConfigGroups fields.
3. Enum conversion is centralised in `infrastructure.mt5.enums`, where every value
   comes from the MT5 SDK headers. Nothing here hand-rolls an ordinal mapping.

THE SHAPE CONTRACT, because it is easy to get wrong and was gotten wrong once already:

    codec.domain_to_record(DOMAIN-shaped dict, table)  ->  MT5 wire record
        keys are dotted DOMAIN paths: {"name": ..., "margin": {"margin_call_level": ...}}

    codec.record_to_domain(MT5 wire record, table)     ->  DOMAIN-shaped dict
        keys are MT5 names on the way in: {"Group": "real\\real", "MarginCall": "50.00"}

So the encode direction takes domain paths and the decode direction takes MT5 names.
`_group_domain_record` and `_symbol_domain_record` below build the FORMER; the two
`db_to_*` functions build the LATTER from table columns. Feeding MT5 names to
domain_to_record silently renders almost nothing, which is how the first version of
this module lost every commission path and every session.

JSONB stores MT5 wire records (all-string scalars), not domain dicts. Strings are what
make the round trip exact: a Decimal written as JSON comes back as a float.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from decimal import Decimal
from typing import Any, Dict, List, Optional

from core.domains.accounts.enums import (
    AccountType,
    FreeMarginMode,
    MarginMode,
    NewsMode,
    StopOutMode,
    TradeFlags,
)
from core.domains.accounts.group import Group
from core.domains.accounts.value_objects import (
    CommissionRule,
    GroupPermissions,
    GroupSymbolOverride,
    MarginProfile,
    RoutingRule,
    SwapConfiguration,
)
from core.domains.instruments.enums import (
    CalculationMode,
    ExecutionMode,
    ExpirationFlags,
    FillingFlags,
    GTCMode,
    OptionMode,
    OrderTypeFlags,
    SwapMode,
    TradeMode,
)
from core.domains.instruments.symbol import Symbol
from core.domains.instruments.value_objects import MarginRates, QuoteSession, TradingSession

from infrastructure.mt5 import enums as mt5enums
from infrastructure.mt5 import fieldmap
from infrastructure.mt5.codec import (
    EXTRA_KEY,
    INHERIT,
    SCALE_KEY,
    domain_to_record,
    is_inherited,
    record_to_domain,
)
from infrastructure.mt5.wire import WEEKDAY_SUNDAY_FIRST

from .config_models import GroupModel, SymbolModel


# ---------------------------------------------------------------------------
# Small conversion helpers
# ---------------------------------------------------------------------------


def _json_safe(value: Any) -> Any:
    """Recursively convert a structure so it can be stored in a JSONB column.

    MT5 import produces Decimals everywhere - every wire scalar is a decimal or an int -
    and neither the SQLite nor the PostgreSQL JSON serialiser accepts a Decimal. Without
    this, `seed --mt5-groups` fails on the first group with
    "Object of type Decimal is not JSON serializable".

    Decimals become strings, which is also what the MT5 wire format uses, so the stored
    value re-exports byte-identically rather than coming back as a float with rounding
    damage.
    """
    if isinstance(value, Decimal):
        return str(value)
    if isinstance(value, dict):
        return {str(k): _json_safe(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_safe(v) for v in value]
    if isinstance(value, (str, int, bool)) or value is None:
        return value
    if isinstance(value, float):
        # A float in a financial config is already a smell; render it exactly rather
        # than letting repr() choose a precision.
        return repr(value)
    return str(value)


def _dec(value: Any, default: str = "0") -> Decimal:
    """Coerce a DB Numeric (or None) to Decimal without going through float."""
    if value is None:
        return Decimal(default)
    if isinstance(value, Decimal):
        return value
    return Decimal(str(value))


def _enum(enum_cls: Any, raw: Any, fallback: Any) -> Any:
    """Resolve an int or string from the DB to an enum member, with a safe fallback."""
    if raw is None:
        return fallback
    try:
        return enum_cls(raw)
    except ValueError:
        try:
            return enum_cls(int(raw))
        except (ValueError, TypeError):
            return fallback


def _int(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _loads(raw: Any, default: Any) -> Any:
    """JSONB arrives as dict/list on PostgreSQL and as text on SQLite."""
    if raw is None:
        return default
    if isinstance(raw, (dict, list)):
        return raw
    try:
        return json.loads(raw)
    except (TypeError, ValueError):
        return default


def _scaled(value: Any, field_name: str, scales: Dict[str, int], default: str = "0") -> str:
    """Render a Decimal column at the wire scale MT5 used when we imported it.

    A Decimal column cannot remember that MT5 wrote "0.00" rather than "0", so the
    observed scale is stored alongside it in mt5_scale and replayed here. Without this
    a symbol re-exports PriceStrike as "0" where the server had "0.00", and MT5
    Administrator compares those literally.
    """
    from infrastructure.mt5.codec import render_decimal

    if value is None:
        return default
    return render_decimal(_dec(value, default), field_name, scales.get(field_name))


def _epoch(value: Any) -> int:
    """MT5 stores TimeStart / TimeExpiration as epoch seconds; the domain uses datetime.

    None means "not set", which MT5 encodes as 0. An int passes through unchanged so a
    value that came off the wire is not mangled.
    """
    if value is None:
        return 0
    if isinstance(value, bool):
        return int(value)
    if isinstance(value, (int, float)):
        return int(value)
    if isinstance(value, str):
        return int(value) if value.lstrip("-").isdigit() else 0
    if isinstance(value, datetime):
        aware = value if value.tzinfo else value.replace(tzinfo=timezone.utc)
        return int(aware.timestamp())
    return 0


def _wire(mapping: Dict[Any, int], member: Any, default: int = 0) -> int:
    """Domain enum member -> MT5 integer, falling back rather than raising.

    Mapping failures here mean "we have no MT5 equivalent", which is not worth
    aborting a persist for; the value is still preserved in mt5_extra.
    """
    if member is None:
        return default
    for key, value in mapping.items():
        if key is member or key == member:
            return int(value)
    return default


# ---------------------------------------------------------------------------
# Sessions
# ---------------------------------------------------------------------------


def days_from_sessions(sessions: Any) -> List[Dict[str, Any]]:
    """Group flat per-day session objects into the shape codec.render_sessions wants.

    ``render_sessions`` expects ``[{"sessions": [{"open_minutes":..,"close_minutes":..}]}, ...]``
    indexed Sunday-first. The domain stores a flat list of TradingSession/QuoteSession
    each carrying ``day_of_week``, so bucket them here. Passing the already-flattened
    wire array to the codec makes it call .get() on a list.
    """
    days: List[Dict[str, Any]] = [{"sessions": []} for _ in range(7)]
    for session in sessions or []:
        index = _int(getattr(session, "day_of_week", 0), 0)
        if not 0 <= index <= 6:
            continue
        days[index]["sessions"].append(
            {
                "open_minutes": _int(getattr(session, "open_minutes", 0), 0),
                "close_minutes": _int(getattr(session, "close_minutes", 1440), 1440),
            }
        )
    return days


def sessions_from_days(days: Any, cls: Any) -> List[Any]:
    """Expand the codec's per-day structure into flat session objects."""
    out: List[Any] = []
    for day in days or []:
        index = _int(day.get("index"), 0)
        for entry in day.get("sessions") or []:
            out.append(
                cls(
                    day_of_week=index,
                    open_minutes=_int(entry.get("open_minutes"), 0),
                    close_minutes=_int(entry.get("close_minutes"), 0),
                )
            )
    return out


# ---------------------------------------------------------------------------
# Group
# ---------------------------------------------------------------------------


def _group_domain_record(group: Group) -> Dict[str, Any]:
    """Build the DOMAIN-shaped record that codec.domain_to_record expects."""
    margin = group.margin
    return {
        "name": group.name,
        "server_id": _int(group.server_id, 1),
        "currency": group.currency or "USD",
        "currency_digits": _int(getattr(group, "currency_digits", 2), 2),
        "trade_flags": int(group.trade_flags or 0),
        "news_mode": _wire(mt5enums.NEWS_MODE_TO_MT5, group.news_mode, 2),
        "limit_orders": _int(group.limit_orders, 0),
        "limit_symbols": _int(group.limit_symbols, 0),
        "limit_positions": _int(group.limit_positions, 0),
        "margin": {
            "mode": _wire(mt5enums.MARGIN_MODE_TO_MT5, margin.mode, 0),
            "flags": _int(margin.flags, 0),
            "stop_out_mode": _wire(mt5enums.STOP_OUT_MODE_TO_MT5, margin.stop_out_mode, 0),
            "free_margin_mode": _wire(
                mt5enums.FREE_MARGIN_MODE_TO_MT5, margin.free_margin_mode, 1
            ),
            # PERCENT. MT5 writes "50.00" / "30.00"; never 0.8 / 0.5.
            "margin_call_level": margin.margin_call_level,
            "stop_out_level": margin.stop_out_level,
        },
        "commissions": [
            {
                "name": rule.name,
                "symbol_pattern": rule.symbol_pattern,
                "currency": rule.currency,
                "tiers": [
                    {
                        "type": 0,
                        "rate": rule.value,
                        "min_value": rule.min_value or Decimal(0),
                        "max_value": rule.max_value if rule.max_value is not None else Decimal(0),
                        "volume_min": Decimal(0),
                        "volume_max": Decimal(0),
                        "currency": rule.currency,
                        EXTRA_KEY: {"Mode": "0"},
                    }
                ],
                EXTRA_KEY: {
                    "Description": "",
                    "Mode": "0",
                    "RangeMode": "0",
                    "ChargeMode": "0",
                    "EntryMode": "0",
                    "ActionMode": "0",
                    "ProfitMode": "0",
                    "ReasonMode": "127",
                },
            }
            for rule in group.commissions
        ],
        # Per-group symbol overrides. These are built in DOMAIN shape and let the codec
        # translate them, because GROUP_SYMBOL_FIELDS is registered in
        # codec.NESTED_TABLES. Fields our GroupSymbolOverride does not model are
        # preserved by the codec's per-record quarantine, so an override imported from
        # MT5 keeps all 64 of its fields even though the domain holds 11.
        #
        # Note codec.INHERIT: MT5 writes the literal string "default" in an override
        # field to mean "inherit from the base symbol". That is not zero. 60 of the 64
        # override fields carry it in the reference export.
        # None means "not overridden", which MT5 encodes as the literal string
        # "default" (codec.INHERIT) - NOT as zero. Emitting 0 here would turn
        # "inherit the base symbol's margin rate" into "the margin rate is 0",
        # which is the difference between a correct margin call and letting a client
        # open an unbounded position. 60 of MT5's 64 override fields carry the
        # sentinel in the reference export.
        "symbol_overrides": [
            {
                "symbol_pattern": override.symbol_pattern,
                "trade_mode": INHERIT
                if override.trade_mode is None
                else _wire(mt5enums.TRADE_MODE_TO_MT5, override.trade_mode, 0),
                "execution_mode": INHERIT
                if override.execution_mode is None
                else _wire(mt5enums.EXECUTION_MODE_TO_MT5, override.execution_mode, 0),
                "spread_diff": INHERIT
                if override.spread_diff is None
                else _int(override.spread_diff, 0),
                **{
                    key: (INHERIT if value is None else value)
                    for key, value in (
                        ("volume_min", override.volume_min),
                        ("volume_max", override.volume_max),
                        ("volume_limit", override.volume_limit),
                        ("margin_rate_initial_buy", override.margin_rate_initial_buy),
                        ("margin_rate_initial_sell", override.margin_rate_initial_sell),
                        ("swap_long", override.swap_long),
                        ("swap_short", override.swap_short),
                    )
                },
            }
            for override in group.symbol_overrides
        ],
    }


def split_mt5_record(
    record: Dict[str, Any], table: Any
) -> "tuple[Dict[str, Any], Dict[str, Any], Dict[str, int]]":
    """Partition an imported MT5 record into (domain fields, quarantine, scales).

    This is the entry point for seeding from a real MT5 export, and it exists because
    the alternative is a silent data-loss trap. A Group or Symbol imported from MT5
    carries fields our domain does not model - 27 of 44 for ConfigGroups, 70 of 121 for
    ConfigSymbols. If the caller builds a domain object and forgets to hand those
    fields to ``group_to_db(mt5_extra=...)``, they vanish from the row and the next
    export ships zeros and empty strings in their place.

    Returns:
        domain   - the codec-typed domain dict, safe to read modelled fields from
        extra    - every field the domain cannot represent, to pass as ``mt5_extra``
        scales   - the observed wire scale per decimal, to pass as ``mt5_scale``

    Usage::

        record  = wire.records(payload, "ConfigGroups")[0]
        domain, extra, scales = split_mt5_record(record, fieldmap.GROUP_FIELDS)
        group = Group(name=domain["name"], ...)          # build the domain object
        row   = group_to_db(group, mt5_extra=extra, mt5_scale=scales)

    ``group_mt5_record(row)`` then reproduces the original, because the quarantine is
    stored verbatim and overlaid on export.
    """
    domain = record_to_domain(record, table)
    extra = dict(domain.get(EXTRA_KEY) or {})
    scales = dict(domain.get(SCALE_KEY) or {})

    # A field the domain record did not populate is, by definition, not ours to
    # reproduce - so it belongs in the quarantine even if it has a domain path.
    rebuilt = domain_to_record(domain, table)
    for key, value in record.items():
        if key in rebuilt and rebuilt[key] == value:
            continue
        extra.setdefault(key, value)
    return domain, extra, scales


def group_to_db(
    group: Group,
    *,
    mt5_extra: Optional[Dict[str, Any]] = None,
    mt5_scale: Optional[Dict[str, int]] = None,
    mt5_source: Optional[Dict[str, Any]] = None,
) -> GroupModel:
    """Map a domain Group onto the MT5-aligned GroupModel.

    ``mt5_extra`` / ``mt5_scale`` carry the MT5 fields our domain does not model, plus
    the wire scale each decimal arrived with. Pass them when persisting a group that
    was imported from a real MT5 export, or re-exporting it would drop every unmodelled
    field. See codec.EXTRA_KEY / codec.SCALE_KEY.
    """
    record = _group_domain_record(group)
    wire_record = domain_to_record(record, fieldmap.GROUP_FIELDS)
    extra = dict(record.get(EXTRA_KEY) or {})
    scale = dict(record.get(SCALE_KEY) or {})
    if mt5_extra:
        extra.update(mt5_extra)
    if mt5_scale:
        scale.update(mt5_scale)

    margin = group.margin

    def col(name: str, default: Any = "") -> Any:
        return wire_record.get(name, default)

    return GroupModel(
        name=group.name,
        group_id=group.id,
        server_id=_int(col("Server", "1"), 1),
        account_type=margin_account_type_value(group.account_type),
        is_active=bool(group.is_active),
        auth_mode=_int(col("AuthMode", "0")),
        auth_password_min=_int(col("AuthPasswordMin", "8"), 8),
        auth_otp_mode=_int(col("AuthOTPMode", "0")),
        permissions_flags=_int(col("PermissionsFlags", "0")),
        company=col("Company", ""),
        company_page=col("CompanyPage", ""),
        company_email=col("CompanyEmail", ""),
        company_support_page=col("CompanySupportPage", ""),
        company_support_email=col("CompanySupportEmail", ""),
        company_catalog=col("CompanyCatalog", ""),
        company_deposit_url=col("CompanyDepositURL", ""),
        company_withdrawal_url=col("CompanyWithdrawalURL", ""),
        currency=col("Currency", "USD"),
        currency_digits=_int(col("CurrencyDigits", "2"), 2),
        reports_mode=_int(col("ReportsMode", "0")),
        reports_flags=_int(col("ReportsFlags", "0")),
        reports_email=col("ReportsEmail", ""),
        news_mode=_int(col("NewsMode", "2"), 2),
        news_category=col("NewsCategory", ""),
        news_langs=_json_safe(_loads(col("NewsLangs", []), [])),
        mail_mode=_int(col("MailMode", "1"), 1),
        trade_flags=_int(col("TradeFlags", "0")),
        trade_transfer_mode=_int(col("TradeTransferMode", "0")),
        trade_interestrate=_dec(col("TradeInterestrate", "0")),
        trade_virtual_credit=_dec(col("TradeVirtualCredit", "0")),
        margin_mode=_int(col("MarginMode", "0")),
        margin_flags=_int(margin.flags, 0),
        margin_so_mode=_int(col("MarginSOMode", "0")),
        margin_free_mode=_int(col("MarginFreeMode", "1"), 1),
        margin_call=_dec(col("MarginCall", "50"), "50"),
        margin_stop_out=_dec(col("MarginStopOut", "30"), "30"),
        margin_free_profit_mode=_int(col("MarginFreeProfitMode", "0")),
        leverage_default=_int(margin.leverage_default, 100),
        leverage_max=_int(margin.leverage_max, 500),
        demo_leverage=_int(col("DemoLeverage", "10"), 10),
        demo_deposit=_dec(col("DemoDeposit", "0")),
        demo_trades_clean=_int(col("DemoTradesClean", "0")),
        limit_history=_int(col("LimitHistory", "0")),
        limit_orders=_int(col("LimitOrders", "0")),
        limit_symbols=_int(col("LimitSymbols", "0")),
        limit_positions=_int(col("LimitPositions", "0")),
        limit_positions_volume=_dec(col("LimitPositionsVolume", "0")),
        margin_json={
            "leverage_default": _int(margin.leverage_default, 100),
            "leverage_max": _int(margin.leverage_max, 500),
            "margin_hedged": str(margin.margin_hedged or 0),
            "flags": _int(margin.flags, 0),
        },
        commissions_json=_json_safe(_loads(col("Commissions", []), [])),
        symbol_overrides_json=_json_safe(_loads(col("Symbols", []), [])),
        permissions_json={
            "allowed_symbols": list(group.permissions.allowed_symbols or []),
            "max_positions": _int(group.permissions.max_positions, 0),
            "max_orders": _int(group.permissions.max_orders, 0),
            "allow_hedging": bool(group.permissions.allow_hedging),
            "allow_short_selling": bool(group.permissions.allow_short_selling),
            "allow_pending_orders": bool(group.permissions.allow_pending_orders),
            "deposit_allowed": bool(group.permissions.deposit_allowed),
            "withdraw_allowed": bool(group.permissions.withdraw_allowed),
            "trade_allowed": bool(group.permissions.trade_allowed),
            "view_only": bool(group.permissions.view_only),
            "internal_only": bool(group.permissions.internal_only),
            "negative_balance_protection": bool(
                group.permissions.negative_balance_protection
            ),
        },
        swaps_json={
            "calculation_mode": group.swaps.calculation_mode,
            "rollover_time": group.swaps.rollover_time,
            "triple_swap_day": group.swaps.triple_swap_day,
            "enable_swaps": bool(group.swaps.enable_swaps),
            "swap_type": group.swaps.swap_type,
            "swap_long": str(group.swaps.swap_long or 0),
            "swap_short": str(group.swaps.swap_short or 0),
        },
        routing_json={
            "default_mode": group.routing.default_mode,
            "a_book_threshold_lots": str(group.routing.a_book_threshold_lots)
            if group.routing.a_book_threshold_lots is not None
            else None,
            "lp_priority": list(group.routing.lp_priority or []),
        },
        mt5_extra=_json_safe(extra),
        mt5_scale=_json_safe(scale),
        mt5_source=_json_safe(mt5_source) if mt5_source else None,
        created_at=group.created_at,
        updated_at=group.updated_at,
    )


def margin_account_type_value(account_type: Any) -> str:
    """AccountType -> its stored string."""
    return account_type.value if hasattr(account_type, "value") else str(account_type)


#: MT5 wire fields the domain can actually edit, so the only ones an export should
#: overwrite on top of an imported baseline.
_GROUP_OWNED_WIRE_KEYS = frozenset(
    {
        "Group",
        "Server",
        "Currency",
        "CurrencyDigits",
        "NewsMode",
        "TradeFlags",
        "MarginMode",
        "MarginFlags",
        "MarginSOMode",
        "MarginFreeMode",
        "MarginCall",
        "MarginStopOut",
        "LimitOrders",
        "LimitSymbols",
        "LimitPositions",
        "Commissions",
        "Symbols",
    }
)


def group_mt5_record(row: GroupModel) -> Dict[str, Any]:
    """Rebuild the MT5 wire record for a stored group row.

    This is the export path. When the row was imported from a real MT5 server, the
    complete original record is stored in ``mt5_source`` and used as the baseline, so
    the 27 fields our domain does not model are reproduced exactly as they arrived -
    including their wire scale, which is why ``TradeInterestrate`` comes back as
    "0.00" and not "0". Domain-owned columns are then overlaid, so an edit made
    through our own API is reflected in the export.

    Rows created natively have no baseline and are built from the columns alone.
    """
    margin_json = _loads(row.margin_json, {})
    scales = _loads(getattr(row, "mt5_scale", None), {})
    baseline = _loads(getattr(row, "mt5_source", None), None)
    scales = _loads(getattr(row, "mt5_scale", None), {})
    record: Dict[str, Any] = dict(baseline) if isinstance(baseline, dict) else {}
    owned: Dict[str, Any] = {
        "Group": row.name,
        "Server": str(_int(row.server_id, 1)),
        "PermissionsFlags": str(_int(row.permissions_flags, 0)),
        "AuthMode": str(_int(row.auth_mode, 0)),
        "AuthPasswordMin": str(_int(row.auth_password_min, 8)),
        "AuthOTPMode": str(_int(row.auth_otp_mode, 0)),
        "Company": row.company or "",
        "CompanyPage": row.company_page or "",
        "CompanyEmail": row.company_email or "",
        "CompanySupportPage": row.company_support_page or "",
        "CompanySupportEmail": row.company_support_email or "",
        "CompanyCatalog": row.company_catalog or "",
        "CompanyDepositURL": row.company_deposit_url or "",
        "CompanyWithdrawalURL": row.company_withdrawal_url or "",
        "Currency": row.currency or "USD",
        "CurrencyDigits": str(_int(row.currency_digits, 2)),
        "ReportsMode": str(_int(row.reports_mode, 0)),
        "ReportsFlags": str(_int(row.reports_flags, 0)),
        "ReportsEmail": row.reports_email or "",
        "NewsMode": str(_int(row.news_mode, 2)),
        "NewsCategory": row.news_category or "",
        "NewsLangs": _loads(row.news_langs, []),
        "MailMode": str(_int(row.mail_mode, 1)),
        "TradeFlags": str(_int(row.trade_flags, 0)),
        "TradeTransferMode": str(_int(row.trade_transfer_mode, 0)),
        "TradeInterestrate": _scaled(row.trade_interestrate, "TradeInterestrate", scales, "0"),
        "TradeVirtualCredit": _scaled(row.trade_virtual_credit, "TradeVirtualCredit", scales, "0"),
        "MarginMode": str(_int(row.margin_mode, 0)),
        "MarginFlags": str(_int(margin_json.get("flags", row.margin_flags), 0)),
        "MarginSOMode": str(_int(row.margin_so_mode, 0)),
        "MarginFreeMode": str(_int(row.margin_free_mode, 1)),
        "MarginCall": _scaled(row.margin_call, "MarginCall", scales, "50"),
        "MarginStopOut": _scaled(row.margin_stop_out, "MarginStopOut", scales, "30"),
        "MarginFreeProfitMode": str(_int(row.margin_free_profit_mode, 0)),
        "DemoLeverage": str(_int(row.demo_leverage, 0)),
        "DemoDeposit": _scaled(row.demo_deposit, "DemoDeposit", scales, "0"),
        "DemoTradesClean": str(_int(row.demo_trades_clean, 0)),
        "LimitHistory": str(_int(row.limit_history, 0)),
        "LimitOrders": str(_int(row.limit_orders, 0)),
        "LimitSymbols": str(_int(row.limit_symbols, 0)),
        "LimitPositions": str(_int(row.limit_positions, 0)),
        "LimitPositionsVolume": str(
            row.limit_positions_volume if row.limit_positions_volume is not None else 0
        ),
        "Commissions": _loads(row.commissions_json, []),
        "Symbols": _loads(row.symbol_overrides_json, []),
    }

    # Only overlay the fields the domain genuinely owns. Everything else - the 27
    # unmodelled ConfigGroups fields - keeps its imported literal, scale included.
    # Overwriting those from a Decimal column would turn "0.00" into "0" and break
    # byte-identical re-export, for fields we cannot edit anyway.
    if baseline:
        # Commissions and Symbols stay as imported. Our CommissionRule models 4 of
        # MT5's 12 commission fields and GroupSymbolOverride 11 of 64 override fields,
        # so rebuilding those arrays from the domain would drop everything else - and
        # unlike the scalar columns, the domain genuinely cannot express the difference
        # between "unchanged" and "set to the same value". Editing them through our own
        # API is M2 work; until then an imported group exports its nested arrays intact.
        owned = {
            k: v
            for k, v in owned.items()
            if k in _GROUP_OWNED_WIRE_KEYS and k not in ("Commissions", "Symbols")
        }
    record.update(owned)
    for key, value in _loads(row.mt5_extra, {}).items():
        record.setdefault(key, value)
    return record


def db_to_group(model: GroupModel) -> Group:
    """Map a GroupModel row back onto the domain Group, via the MT5 codec."""
    if model is None:
        return None

    domain = record_to_domain(group_mt5_record(model), fieldmap.GROUP_FIELDS)
    scale = _loads(getattr(model, "mt5_scale", None), {})
    if scale:
        domain[SCALE_KEY] = scale

    margin_json = _loads(model.margin_json, {})
    margin_dom = domain.get("margin") or {}

    # The stored column wins; the group path prefix is only a fallback. Deriving from
    # the path unconditionally discards an explicit choice - demo\Challenge is a CONTEST
    # group and coverage\house is a COVERAGE account, and neither prefix says so.
    account_type = _enum(AccountType, model.account_type, None)
    if account_type is None:
        account_type = (
            mt5enums.account_type_from_group_path(model.name) or AccountType.REAL
        )

    permissions_raw = _loads(model.permissions_json, {})
    swaps_raw = _loads(model.swaps_json, {})
    routing_raw = _loads(model.routing_json, {})

    commissions: List[CommissionRule] = []
    for raw in domain.get("commissions") or []:
        tiers = raw.get("tiers") or []
        first = tiers[0] if tiers else {}
        pattern = raw.get("symbol_pattern") or (raw.get(EXTRA_KEY) or {}).get("Path") or "*"
        max_value = first.get("max_value")
        commissions.append(
            CommissionRule(
                name=raw.get("name") or "",
                symbol_pattern=pattern,
                currency=raw.get("currency") or first.get("currency") or "USD",
                value=_dec(first.get("rate"), "0"),
                min_value=_dec(first.get("min_value"), "0"),
                max_value=_dec(max_value) if max_value not in (None, "") else None,
            )
        )

    overrides: List[GroupSymbolOverride] = []
    for raw in domain.get("symbol_overrides") or []:
        overrides.append(
            GroupSymbolOverride(
                symbol_pattern=raw.get("symbol_pattern", "*"),
                trade_mode=raw.get("trade_mode"),
                execution_mode=raw.get("execution_mode"),
                volume_min=raw.get("volume_min"),
                volume_max=raw.get("volume_max"),
                volume_limit=raw.get("volume_limit"),
                spread_diff=raw.get("spread_diff"),
                margin_rate_initial_buy=raw.get("margin_rate_initial_buy"),
                margin_rate_initial_sell=raw.get("margin_rate_initial_sell"),
                swap_long=raw.get("swap_long"),
                swap_short=raw.get("swap_short"),
            )
        )

    return Group(
        id=model.group_id or model.name,
        name=model.name,
        server_id=_int(model.server_id, 1),
        account_type=account_type,
        currency=model.currency or "USD",
        margin=MarginProfile(
            mode=_enum(
                MarginMode,
                mt5enums.MARGIN_MODE_FROM_MT5.get(_int(model.margin_mode, 0)),
                MarginMode.RETAIL,
            ),
            margin_call_level=_dec(margin_dom.get("margin_call_level"), "50"),
            stop_out_level=_dec(margin_dom.get("stop_out_level"), "30"),
            stop_out_mode=_enum(
                StopOutMode,
                mt5enums.STOP_OUT_MODE_FROM_MT5.get(_int(model.margin_so_mode, 0)),
                StopOutMode.PERCENT,
            ),
            free_margin_mode=_enum(
                FreeMarginMode,
                mt5enums.FREE_MARGIN_MODE_FROM_MT5.get(_int(model.margin_free_mode, 1)),
                FreeMarginMode.USE_PL,
            ),
            leverage_default=_int(
                margin_json.get("leverage_default", model.leverage_default), 100
            ),
            leverage_max=_int(margin_json.get("leverage_max", model.leverage_max), 500),
            margin_hedged=_dec(margin_json.get("margin_hedged"), "0"),
            flags=_int(margin_json.get("flags", model.margin_flags), 0),
        ),
        commissions=commissions,
        symbol_overrides=overrides,
        trade_flags=TradeFlags(_int(model.trade_flags, 0)),
        limit_orders=_int(model.limit_orders, 200),
        limit_positions=_int(model.limit_positions, 200),
        limit_symbols=_int(model.limit_symbols, 100),
        routing=RoutingRule(
            default_mode=routing_raw.get("default_mode", "b_book"),
            a_book_threshold_lots=_dec(routing_raw["a_book_threshold_lots"])
            if routing_raw.get("a_book_threshold_lots")
            else None,
            lp_priority=list(routing_raw.get("lp_priority") or []),
        ),
        permissions=GroupPermissions(
            allowed_symbols=list(permissions_raw.get("allowed_symbols") or ["*"]),
            max_positions=_int(permissions_raw.get("max_positions"), 200),
            max_orders=_int(permissions_raw.get("max_orders"), 100),
            allow_hedging=bool(permissions_raw.get("allow_hedging", True)),
            allow_short_selling=bool(permissions_raw.get("allow_short_selling", True)),
            allow_pending_orders=bool(permissions_raw.get("allow_pending_orders", True)),
            deposit_allowed=bool(permissions_raw.get("deposit_allowed", True)),
            withdraw_allowed=bool(permissions_raw.get("withdraw_allowed", True)),
            trade_allowed=bool(permissions_raw.get("trade_allowed", True)),
            view_only=bool(permissions_raw.get("view_only", False)),
            internal_only=bool(permissions_raw.get("internal_only", False)),
            negative_balance_protection=bool(
                permissions_raw.get("negative_balance_protection", True)
            ),
        ),
        swaps=SwapConfiguration(
            calculation_mode=swaps_raw.get("calculation_mode", "points"),
            rollover_time=swaps_raw.get("rollover_time", "22:00"),
            triple_swap_day=swaps_raw.get("triple_swap_day", "Wednesday"),
            enable_swaps=bool(swaps_raw.get("enable_swaps", True)),
            swap_type=swaps_raw.get("swap_type", "POINTS"),
            swap_long=_dec(swaps_raw.get("swap_long"), "0"),
            swap_short=_dec(swaps_raw.get("swap_short"), "0"),
        ),
        news_mode=_enum(
            NewsMode, mt5enums.NEWS_MODE_FROM_MT5.get(_int(model.news_mode, 2)), NewsMode.FULL
        ),
        created_at=model.created_at or datetime.now(timezone.utc),
        updated_at=model.updated_at or datetime.now(timezone.utc),
        is_active=bool(model.is_active),
    )


# ---------------------------------------------------------------------------
# Symbol
# ---------------------------------------------------------------------------

#: domain MarginRates field -> SymbolModel column
_MARGIN_RATE_COLUMNS = {
    "initial_buy": "margin_initial_buy",
    "initial_sell": "margin_initial_sell",
    "initial_buy_limit": "margin_initial_buy_limit",
    "initial_sell_limit": "margin_initial_sell_limit",
    "initial_buy_stop": "margin_initial_buy_stop",
    "initial_sell_stop": "margin_initial_sell_stop",
    "initial_buy_stop_limit": "margin_initial_buy_stop_limit",
    "initial_sell_stop_limit": "margin_initial_sell_stop_limit",
    "maintenance_buy": "margin_maintenance_buy",
    "maintenance_sell": "margin_maintenance_sell",
    "maintenance_buy_limit": "margin_maintenance_buy_limit",
    "maintenance_sell_limit": "margin_maintenance_sell_limit",
    "maintenance_buy_stop": "margin_maintenance_buy_stop",
    "maintenance_sell_stop": "margin_maintenance_sell_stop",
    "maintenance_buy_stop_limit": "margin_maintenance_buy_stop_limit",
    "maintenance_sell_stop_limit": "margin_maintenance_sell_stop_limit",
}

#: domain MarginRates field -> MT5 ConfigSymbols field
_MARGIN_RATE_TO_MT5 = {
    "initial_buy": "MarginInitialBuy",
    "initial_sell": "MarginInitialSell",
    "initial_buy_limit": "MarginInitialBuyLimit",
    "initial_sell_limit": "MarginInitialSellLimit",
    "initial_buy_stop": "MarginInitialBuyStop",
    "initial_sell_stop": "MarginInitialSellStop",
    "initial_buy_stop_limit": "MarginInitialBuyStopLimit",
    "initial_sell_stop_limit": "MarginInitialSellStopLimit",
    "maintenance_buy": "MarginMaintenanceBuy",
    "maintenance_sell": "MarginMaintenanceSell",
    "maintenance_buy_limit": "MarginMaintenanceBuyLimit",
    "maintenance_sell_limit": "MarginMaintenanceSellLimit",
    "maintenance_buy_stop": "MarginMaintenanceBuyStop",
    "maintenance_sell_stop": "MarginMaintenanceSellStop",
    "maintenance_buy_stop_limit": "MarginMaintenanceBuyStopLimit",
    "maintenance_sell_stop_limit": "MarginMaintenanceSellStopLimit",
}
_MT5_TO_MARGIN_RATE = {v: k for k, v in _MARGIN_RATE_TO_MT5.items()}

#: SwapMode members that are deprecated aliases sharing a value with a canonical
#: member. Excluded when building the reverse map so the alias cannot win.
_SWAP_MODE_ALIASES = ("CURRENCY", "REOPEN_CURRENT")


def _symbol_domain_record(symbol: Symbol) -> Dict[str, Any]:
    """Build the DOMAIN-shaped record that codec.domain_to_record expects."""
    record: Dict[str, Any] = {
        "name": symbol.name,
        "path": symbol.path or "",
        "description": symbol.description or "",
        "base_currency": symbol.base_currency or "USD",
        "quote_currency": symbol.quote_currency or "USD",
        "digits": _int(symbol.digits, 5),
        # MT5's Point is our tick_size (the price-precision step). MT5's TickSize is a
        # distinct field - the tick alignment step - and now has its own domain field.
        "tick_size": symbol.tick_size,
        "mt5_tick_size": symbol.mt5_tick_size,
        "tick_value": symbol.tick_value,
        "contract_size": symbol.contract_size,
        "spread": _int(symbol.spread, 0),
        "spread_balance": _int(symbol.spread_balance, 0),
        "volume_min": symbol.volume_min,
        "volume_max": symbol.volume_max,
        "volume_step": symbol.volume_step,
        "volume_limit": symbol.volume_limit,
        "stops_level": _int(symbol.stops_level, 0),
        "freeze_level": _int(symbol.freeze_level, 0),
        "swap_long": symbol.swap_long,
        "swap_short": symbol.swap_short,
        "swap_3day": _int(symbol.swap_3day, 3),
        "swap_year_days": _int(symbol.swap_year_days, 0),
        "time_start": _epoch(symbol.time_start),
        "time_expiration": _epoch(symbol.time_expiration),
        "calc_mode": _int(getattr(symbol.calc_mode, "value", symbol.calc_mode), 0),
        "trade_mode": _wire(mt5enums.TRADE_MODE_TO_MT5, symbol.trade_mode, 4),
        "exec_mode": _wire(mt5enums.EXECUTION_MODE_TO_MT5, symbol.exec_mode, 2),
        "gtc_mode": _wire(mt5enums.GTC_MODE_TO_MT5, symbol.gtc_mode, 0),
        "swap_mode": _wire(
            {
                m: int(m.value)
                for m in SwapMode
                if m.name not in _SWAP_MODE_ALIASES
            },
            symbol.swap_mode,
            0,
        ),
        "option_mode": _int(getattr(symbol.option_mode, "value", symbol.option_mode), 0),
        "fill_flags": int(symbol.fill_flags or 0),
        "expiration_flags": int(symbol.expiration_flags or 0),
        "order_flags": int(symbol.order_flags or 0),
        "margin_rates": {
            name: getattr(symbol.margin_rates, name) for name in _MARGIN_RATE_TO_MT5
        },
        # Bucketed per-day, which is what codec.render_sessions consumes.
        "quote_sessions": days_from_sessions(symbol.quote_sessions),
        "trade_sessions": days_from_sessions(symbol.trade_sessions),
    }
    if symbol.strike_price is not None:
        record["strike_price"] = symbol.strike_price
    if symbol.face_value is not None:
        record["face_value"] = symbol.face_value
    return record


def symbol_to_db(
    symbol: Symbol,
    *,
    mt5_extra: Optional[Dict[str, Any]] = None,
    mt5_scale: Optional[Dict[str, int]] = None,
    mt5_source: Optional[Dict[str, Any]] = None,
) -> SymbolModel:
    """Map a domain Symbol onto the MT5-aligned SymbolModel.

    ``mt5_extra`` / ``mt5_scale`` behave as for :func:`group_to_db`.
    """
    record = _symbol_domain_record(symbol)
    wire_record = domain_to_record(record, fieldmap.SYMBOL_FIELDS)
    extra = dict(record.get(EXTRA_KEY) or {})
    scale = dict(record.get(SCALE_KEY) or {})
    if mt5_extra:
        extra.update(mt5_extra)
    if mt5_scale:
        scale.update(mt5_scale)

    def col(name: str, default: Any = "0") -> Any:
        return wire_record.get(name, default)

    kwargs: Dict[str, Any] = dict(
        name=symbol.name,
        path=col("Path", "") or "",
        symbol_id=symbol.id,
        description=col("Description", "") or "",
        # MT5's wire fields are CurrencyBase / CurrencyProfit / CurrencyMargin. There is
        # no CurrencyQuote in the export, so the previous `extra.get("CurrencyQuote")`
        # lookup always missed and fell through to "USD" - silently making every imported
        # symbol USD-quoted, which is the persistence half of the cross-currency bug.
        # The domain symbol's own value wins when it is set, because that is what the
        # codec populated from the wire record.
        base_currency=symbol.base_currency or col("CurrencyBase", "USD") or "USD",
        quote_currency=(
            symbol.quote_currency
            or extra.get("CurrencyProfit")
            or col("CurrencyProfit", "")
            or "USD"
        ),
        margin_currency=(
            symbol.margin_currency
            or extra.get("CurrencyMargin")
            or col("CurrencyMargin", "")
            or ""
        ),
        digits=_int(col("Digits", "5"), 5),
        point=_dec(col("Point", "0")),
        # MT5's TickSize is a distinct, often-zero field. It is not our tick_size.
        mt5_tick_size=_dec(col("TickSize", "0")),
        tick_value=_dec(col("TickValue", "0")),
        contract_size=_dec(col("ContractSize", "100000"), "100000"),
        calc_mode=_int(col("CalcMode", "0")),
        trade_mode=_int(col("TradeMode", "4"), 4),
        exec_mode=_int(col("ExecMode", "2"), 2),
        gtc_mode=_int(col("GTCMode", "0")),
        fill_flags=_int(col("FillFlags", "0")),
        expiration_flags=_int(col("ExpirFlags", "0")),
        order_flags=_int(col("OrderFlags", "127"), 127),
        is_trade_allowed=_int(col("TradeMode", "4"), 4) != 0,
        spread=_int(col("Spread", "0")),
        spread_balance=_int(col("SpreadBalance", "0")),
        stops_level=_int(col("StopsLevel", "0")),
        freeze_level=_int(col("FreezeLevel", "0")),
        volume_min=_dec(col("VolumeMin", "0")),
        volume_max=_dec(col("VolumeMax", "0")),
        volume_step=_dec(col("VolumeStep", "0")),
        volume_limit=_dec(col("VolumeLimit", "0")),
        swap_mode=_int(col("SwapMode", "0")),
        swap_long=_dec(col("SwapLong", "0")),
        swap_short=_dec(col("SwapShort", "0")),
        swap_3day=_int(col("Swap3Day", "3"), 3),
        swap_year_days=_int(col("SwapYearDay", "0")),
        sessions_quotes_json=_loads(col("SessionsQuotes", []), []),
        sessions_trades_json=_loads(col("SessionsTrades", []), []),
        time_start=_int(col("TimeStart", "0")),
        time_expiration=_int(col("TimeExpiration", "0")),
        option_mode=_int(col("OptionMode", "0")),
        strike_price=_dec(col("PriceStrike", "0")),
        face_value=_dec(col("FaceValue", "0")),
        face_value_currency=symbol.face_value_currency or "USD",
        mt5_extra=_json_safe(extra),
        mt5_scale=_json_safe(scale),
        mt5_source=_json_safe(mt5_source) if mt5_source else None,
        created_at=symbol.created_at,
        updated_at=symbol.updated_at,
    )
    for domain_name, column in _MARGIN_RATE_COLUMNS.items():
        kwargs[column] = _dec(col(_MARGIN_RATE_TO_MT5[domain_name], "1"), "1")

    return SymbolModel(**kwargs)


#: MT5 wire fields the domain can actually edit, so the only ones an export should
#: overwrite on top of an imported baseline. Everything else - CurrencyProfit,
#: CurrencyMargin, the Filter* tick filtration, the IE*/RE* execution controls, the
#: per-day SwapRate curve, the *Ext integer-scaled volumes - keeps its imported literal
#: and its imported scale.
_SYMBOL_OWNED_WIRE_KEYS = frozenset(
    {
        "Symbol",
        "Path",
        "Description",
        "CurrencyBase",
        "Digits",
        "Point",
        "TickValue",
        "ContractSize",
        "CalcMode",
        "TradeMode",
        "ExecMode",
        "GTCMode",
        "SwapMode",
        "SwapLong",
        "SwapShort",
        "Swap3Day",
        "Spread",
        "SpreadBalance",
        "StopsLevel",
        "FreezeLevel",
        "VolumeMin",
        "VolumeMax",
        "VolumeStep",
        "VolumeLimit",
        "SessionsQuotes",
        "SessionsTrades",
        "TimeStart",
        "TimeExpiration",
        "OptionMode",
        "PriceStrike",
        "FaceValue",
    }
)


def symbol_mt5_record(row: SymbolModel) -> Dict[str, Any]:
    """Rebuild the MT5 wire record for a stored symbol row (the export path).

    Mirrors :func:`group_mt5_record`. MT5 has 121 symbol fields and our domain models
    51, so an imported symbol exports from its stored baseline with only the
    domain-owned fields overlaid. Without the baseline, 70 fields would come back as
    zeros and empty strings.
    """
    baseline = _loads(getattr(row, "mt5_source", None), None)
    scales = _loads(getattr(row, "mt5_scale", None), {})
    record: Dict[str, Any] = dict(baseline) if isinstance(baseline, dict) else {}
    owned: Dict[str, Any] = {
        "Symbol": row.name,
        "Path": row.path or "",
        "Description": row.description or "",
        "CurrencyBase": row.base_currency or "USD",
        # MT5 keeps three symbol currencies and they are not interchangeable. These two
        # were modelled as of M3; before that they survived the round trip only inside the
        # mt5_source baseline, so a symbol created through the admin API - which has no
        # baseline - would have exported them as absent and MT5 would read them as empty.
        # Only overlaid when the column actually holds a value, so an empty column leaves
        # the baseline's original string untouched and the export stays byte-identical.
        **({"CurrencyProfit": row.quote_currency} if row.quote_currency else {}),
        **({"CurrencyMargin": row.margin_currency} if row.margin_currency else {}),
        "Digits": str(_int(row.digits, 5)),
        # Point is the precision step; TickSize is separate and frequently zero.
        "Point": _scaled(row.point, "Point", scales, "0"),
        "TickSize": _scaled(row.mt5_tick_size, "TickSize", scales, "0"),
        "TickValue": _scaled(row.tick_value, "TickValue", scales, "0"),
        "ContractSize": str(row.contract_size if row.contract_size is not None else 100000),
        "CalcMode": str(_int(row.calc_mode, 0)),
        "TradeMode": str(_int(row.trade_mode, 4)),
        "ExecMode": str(_int(row.exec_mode, 2)),
        "GTCMode": str(_int(row.gtc_mode, 0)),
        "FillFlags": str(_int(row.fill_flags, 0)),
        "ExpirFlags": str(_int(row.expiration_flags, 0)),
        "OrderFlags": str(_int(row.order_flags, 127)),
        "Spread": str(_int(row.spread, 0)),
        "SpreadBalance": str(_int(row.spread_balance, 0)),
        "StopsLevel": str(_int(row.stops_level, 0)),
        "FreezeLevel": str(_int(row.freeze_level, 0)),
        "VolumeMin": _scaled(row.volume_min, "VolumeMin", scales, "0"),
        "VolumeMax": _scaled(row.volume_max, "VolumeMax", scales, "0"),
        "VolumeStep": _scaled(row.volume_step, "VolumeStep", scales, "0"),
        "VolumeLimit": _scaled(row.volume_limit, "VolumeLimit", scales, "0"),
        "SwapMode": str(_int(row.swap_mode, 0)),
        "SwapLong": _scaled(row.swap_long, "SwapLong", scales, "0"),
        "SwapShort": _scaled(row.swap_short, "SwapShort", scales, "0"),
        "Swap3Day": str(_int(row.swap_3day, 3)),
        "SwapYearDay": str(_int(row.swap_year_days, 0)),
        "SessionsQuotes": _loads(row.sessions_quotes_json, []),
        "SessionsTrades": _loads(row.sessions_trades_json, []),
        "TimeStart": str(_int(row.time_start, 0)),
        "TimeExpiration": str(_int(row.time_expiration, 0)),
        "OptionMode": str(_int(row.option_mode, 0)),
        "PriceStrike": _scaled(row.strike_price, "PriceStrike", scales, "0"),
        "FaceValue": _scaled(row.face_value, "FaceValue", scales, "0"),
    }
    for mt5_name, domain_name in _MT5_TO_MARGIN_RATE.items():
        owned[mt5_name] = _scaled(
            getattr(row, _MARGIN_RATE_COLUMNS[domain_name], 1), mt5_name, scales, "1"
        )

    if baseline:
        owned = {k: v for k, v in owned.items() if k in _SYMBOL_OWNED_WIRE_KEYS}
    record.update(owned)
    for key, value in _loads(row.mt5_extra, {}).items():
        record.setdefault(key, value)
    return record


def db_to_symbol(model: SymbolModel) -> Symbol:
    """Map a SymbolModel row back onto the domain Symbol, via the MT5 codec."""
    if model is None:
        return None

    domain = record_to_domain(symbol_mt5_record(model), fieldmap.SYMBOL_FIELDS)
    scale = _loads(getattr(model, "mt5_scale", None), {})
    if scale:
        domain[SCALE_KEY] = scale

    rates = domain.get("margin_rates") or {}

    return Symbol(
        id=model.symbol_id or model.name,
        name=model.name,
        path=model.path or "",
        description=model.description or "",
        base_currency=domain.get("base_currency") or "USD",
        quote_currency=domain.get("quote_currency") or "USD",
        # MT5 CurrencyMargin. Empty means "same as the base currency", which Symbol's own
        # __post_init__ resolves - so it is passed through rather than defaulted here.
        margin_currency=domain.get("margin_currency") or "",
        calc_mode=_enum(CalculationMode, domain.get("calc_mode"), CalculationMode.FOREX),
        digits=_int(domain.get("digits"), 5),
        # Point -> tick_size (the precision step). TickSize -> mt5_tick_size.
        tick_size=_dec(domain.get("tick_size"), "0.00001"),
        mt5_tick_size=_dec(domain.get("mt5_tick_size"), "0"),
        tick_value=_dec(domain.get("tick_value"), "1"),
        contract_size=_dec(domain.get("contract_size"), "100000"),
        spread=_int(domain.get("spread"), 0),
        spread_balance=_int(domain.get("spread_balance"), 0),
        volume_min=_dec(domain.get("volume_min"), "0.01"),
        volume_max=_dec(domain.get("volume_max"), "100"),
        volume_step=_dec(domain.get("volume_step"), "0.01"),
        volume_limit=_dec(domain.get("volume_limit"), "0"),
        margin_rates=MarginRates(**{k: _dec(v, "1") for k, v in rates.items()}),
        trade_mode=_enum(TradeMode, domain.get("trade_mode"), TradeMode.FULL),
        exec_mode=_enum(ExecutionMode, domain.get("exec_mode"), ExecutionMode.MARKET),
        gtc_mode=_enum(GTCMode, domain.get("gtc_mode"), GTCMode.GTC),
        fill_flags=_enum(FillingFlags, domain.get("fill_flags"), FillingFlags.FOK),
        expiration_flags=_enum(
            ExpirationFlags, domain.get("expiration_flags"), ExpirationFlags.GTC
        ),
        order_flags=_enum(OrderTypeFlags, domain.get("order_flags"), OrderTypeFlags(127)),
        stops_level=_int(domain.get("stops_level"), 0),
        freeze_level=_int(domain.get("freeze_level"), 0),
        swap_mode=_enum(SwapMode, domain.get("swap_mode"), SwapMode.POINTS),
        swap_long=_dec(domain.get("swap_long"), "0"),
        swap_short=_dec(domain.get("swap_short"), "0"),
        swap_3day=_int(domain.get("swap_3day"), 3),
        swap_year_days=_int(domain.get("swap_year_days"), 365),
        quote_sessions=sessions_from_days(domain.get("quote_sessions"), QuoteSession),
        trade_sessions=sessions_from_days(domain.get("trade_sessions"), TradingSession),
        time_start=_int(domain.get("time_start"), 0),
        time_expiration=_int(domain.get("time_expiration"), 0),
        option_mode=_enum(OptionMode, domain.get("option_mode"), OptionMode.EUROPEAN),
        strike_price=_dec(domain.get("strike_price"), "0"),
        face_value=_dec(domain.get("face_value"), "0"),
        face_value_currency=model.face_value_currency or "USD",
        is_trade_allowed=bool(model.is_trade_allowed),
        created_at=model.created_at or datetime.now(timezone.utc),
        updated_at=model.updated_at or datetime.now(timezone.utc),
    )
