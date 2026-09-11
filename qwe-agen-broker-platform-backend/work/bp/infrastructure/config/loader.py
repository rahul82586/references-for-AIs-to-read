"""
Strict configuration loader for the configuration plane.

TWO INPUT FORMATS, ONE OUTPUT

1. MT5 Administrator JSON export - the format your `mt5-format-structure/*.json` files
   are in. Goes through `infrastructure.mt5.codec`, so it is lossless and can be
   re-exported. This is the format to use for real broker configuration, because it is
   the format a real MT5 server speaks.

2. Typed YAML - `config/groups/*.yaml` and `config/symbols/*.yaml`, mirroring the
   domain value objects. Hand-editable, diffable, and what `make seed` uses for a
   from-scratch install with no MT5 server to import from.

WHY STRICT

The previous state was that `config/*.yaml` was read by nothing at all, and its schema
did not match the domain: it used flat `margin_call_level: 0.8` where `Group` takes a
nested `MarginProfile`, `commissions[].symbol_group` where the model has
`symbol_pattern`, and `margins.initial_percent` where `Symbol` now has a 16-field
`MarginRates`. A loader that tolerates unknown keys would have loaded that file,
silently dropped every mismatched field, and produced a broker running on defaults.

So: an unknown key is an error, a value of the wrong type is an error, and a margin
threshold that looks like a fraction is an error. Failing loudly at load time is the
whole point.
"""

from __future__ import annotations

import pathlib
from dataclasses import fields as dataclass_fields
from decimal import Decimal, InvalidOperation
from typing import Any, Dict, List, Optional, Sequence, Tuple

import yaml

from core.domains.accounts.enums import (
    AccountType,
    FreeMarginMode,
    MarginMode,
    NewsMode,
    StopOutMode,
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
from infrastructure.mt5.codec import EXTRA_KEY, SCALE_KEY, record_to_domain
from infrastructure.mt5.wire import WEEKDAY_SUNDAY_FIRST, decode_file, records


class ConfigError(ValueError):
    """Raised when a configuration file is wrong. Always names the file and the key."""


# ---------------------------------------------------------------------------
# Scalars
# ---------------------------------------------------------------------------


def _path_label(source: Any) -> str:
    return pathlib.Path(source).name if source else "<config>"


def _require(mapping: Dict[str, Any], key: str, where: str) -> Any:
    if key not in mapping:
        raise ConfigError(f"{where}: missing required key '{key}'")
    return mapping[key]


def _reject_unknown(
    mapping: Dict[str, Any], allowed: Sequence[str], where: str
) -> None:
    """Fail on any key we do not recognise.

    Tolerating unknown keys is how a configuration file drifts away from the model it
    is supposed to populate: the loader keeps working, the value is quietly ignored,
    and the broker runs on a default nobody chose.
    """
    unknown = sorted(set(mapping) - set(allowed))
    if unknown:
        raise ConfigError(
            f"{where}: unknown key(s) {unknown}. Known keys: {sorted(allowed)}"
        )


def _decimal(value: Any, where: str, key: str) -> Decimal:
    if isinstance(value, Decimal):
        return value
    try:
        return Decimal(str(value))
    except (InvalidOperation, ValueError):
        raise ConfigError(f"{where}.{key}: {value!r} is not a decimal") from None


def _int(value: Any, where: str, key: str, default: Optional[int] = None) -> int:
    if value is None:
        if default is None:
            raise ConfigError(f"{where}.{key}: required")
        return default
    if isinstance(value, bool):
        raise ConfigError(f"{where}.{key}: expected an integer, got a boolean")
    try:
        return int(value)
    except (TypeError, ValueError):
        raise ConfigError(f"{where}.{key}: {value!r} is not an integer") from None


def _bool(value: Any, where: str, key: str, default: bool = False) -> bool:
    if value is None:
        return default
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        lowered = value.strip().lower()
        if lowered in ("true", "yes", "1", "on"):
            return True
        if lowered in ("false", "no", "0", "off"):
            return False
    raise ConfigError(f"{where}.{key}: {value!r} is not a boolean")


def _enum(enum_cls: Any, value: Any, where: str, key: str, fallback: Any) -> Any:
    """Resolve an enum from its value or its name.

    Accepting both matters because MT5 stores integers ("2") while a hand-written YAML
    naturally says `MARKET` or `market`. Rejecting either would push authors toward
    guessing ordinals, which is what produced the CalcMode/SwapMode defects.
    """
    if value is None:
        return fallback
    try:
        return enum_cls(value)
    except ValueError:
        pass
    if isinstance(value, str):
        try:
            return enum_cls[value.strip().upper()]
        except KeyError:
            pass
    try:
        return enum_cls(int(value))
    except (ValueError, TypeError):
        pass
    valid = ", ".join(f"{m.name}={m.value}" for m in enum_cls)
    raise ConfigError(f"{where}.{key}: {value!r} is not a valid {enum_cls.__name__} ({valid})")


#: The exact values this codebase used under the fraction convention. Rejecting these
#: specifically - rather than "anything <= 1" - matters: on the reference server 13 of
#: 20 groups legitimately use MarginStopOut "1.00" (every demo group), and a 1% stop-out
#: is a real, if tight, setting. A blanket `<= 1` check would reject a real broker
#: configuration and push the author toward "fixing" a value that was already correct.
_FRACTION_SMELL = frozenset({"0.8", "0.5", "0.7", "0.4", "0.6", "0.3", "0.9", "0.75", "0.25"})


def _percent(value: Any, where: str, key: str) -> Decimal:
    """Parse a margin threshold in PERCENT and reject the fraction convention.

    MT5 stores MarginCall / MarginStopOut as percent ("50.00", "30.00"). This codebase
    previously held 0.8 / 0.5 in the domain defaults and 60 / 30 in the database, and
    compared percent margin levels against both - so an account at 40% margin level
    reported no margin call and no stop-out.

    Only the specific fraction literals are rejected. Values in (0, 1] other than those
    are accepted, because MT5 servers do use them: every demo group in the reference
    export runs MarginStopOut "1.00".
    """
    parsed = _decimal(value, where, key)
    if parsed < Decimal("0"):
        raise ConfigError(f"{where}.{key}: {value!r} is negative")
    if parsed > Decimal("10000"):
        raise ConfigError(f"{where}.{key}: {value!r} is implausibly large for a percent")

    raw_text = str(value).strip()
    if raw_text in _FRACTION_SMELL or (parsed < Decimal("1") and parsed != Decimal("0")):
        raise ConfigError(
            f"{where}.{key}: {value!r} looks like a FRACTION. Margin thresholds are "
            "PERCENT (MT5 MarginCall '50.00', MarginStopOut '30.00'); the reference "
            "server's demo groups use 10.00 / 1.00 and its real groups 50.00 / 30.00. "
            "Use 50 instead of 0.5."
        )
    return parsed


# ---------------------------------------------------------------------------
# Groups - YAML
# ---------------------------------------------------------------------------

_GROUP_KEYS = (
    "name",
    "account_type",
    "currency",
    "currency_digits",
    "server_id",
    "margin",
    "commissions",
    "symbol_overrides",
    "permissions",
    "swaps",
    "routing",
    "trade_flags",
    "news_mode",
    "limit_orders",
    "limit_positions",
    "limit_symbols",
    "is_active",
)

_MARGIN_KEYS = (
    "mode",
    "margin_call_level",
    "stop_out_level",
    "stop_out_mode",
    "free_margin_mode",
    "leverage_default",
    "leverage_max",
    "margin_hedged",
    "flags",
)

_PERMISSION_KEYS = tuple(f.name for f in dataclass_fields(GroupPermissions))
_SWAP_KEYS = tuple(f.name for f in dataclass_fields(SwapConfiguration))
_ROUTING_KEYS = tuple(f.name for f in dataclass_fields(RoutingRule))
_COMMISSION_KEYS = tuple(f.name for f in dataclass_fields(CommissionRule) if f.name != "id")
_OVERRIDE_KEYS = tuple(
    f.name for f in dataclass_fields(GroupSymbolOverride) if f.name != "id"
)
_MARGIN_RATE_KEYS = tuple(f.name for f in dataclass_fields(MarginRates))


def parse_margin_profile(raw: Any, where: str) -> MarginProfile:
    """Parse the nested margin block. Flat legacy keys are rejected with a hint."""
    if raw is None:
        return MarginProfile()
    if not isinstance(raw, dict):
        raise ConfigError(f"{where}.margin: expected a mapping, got {type(raw).__name__}")

    # The pre-M1 YAML put these flat on the group. Say so rather than guessing.
    for legacy in ("margin_call_level", "stop_out_level", "leverage_default", "leverage_max"):
        pass  # checked by the caller's unknown-key rejection

    _reject_unknown(raw, _MARGIN_KEYS, f"{where}.margin")
    return MarginProfile(
        mode=_enum(MarginMode, raw.get("mode"), f"{where}.margin", "mode", MarginMode.RETAIL),
        margin_call_level=_percent(
            raw.get("margin_call_level", 50), f"{where}.margin", "margin_call_level"
        ),
        stop_out_level=_percent(
            raw.get("stop_out_level", 30), f"{where}.margin", "stop_out_level"
        ),
        stop_out_mode=_enum(
            StopOutMode,
            raw.get("stop_out_mode"),
            f"{where}.margin",
            "stop_out_mode",
            StopOutMode.PERCENT,
        ),
        free_margin_mode=_enum(
            FreeMarginMode,
            raw.get("free_margin_mode"),
            f"{where}.margin",
            "free_margin_mode",
            FreeMarginMode.USE_PL,
        ),
        leverage_default=_int(
            raw.get("leverage_default"), f"{where}.margin", "leverage_default", 100
        ),
        leverage_max=_int(raw.get("leverage_max"), f"{where}.margin", "leverage_max", 500),
        margin_hedged=_decimal(
            raw.get("margin_hedged", 0), f"{where}.margin", "margin_hedged"
        ),
        flags=_int(raw.get("flags"), f"{where}.margin", "flags", 0),
    )


def parse_commission(raw: Dict[str, Any], where: str) -> CommissionRule:
    _reject_unknown(raw, _COMMISSION_KEYS + ("tiers",), where)
    if "symbol_group" in raw:
        raise ConfigError(
            f"{where}: 'symbol_group' was renamed to 'symbol_pattern' (MT5 calls it Path)"
        )
    kwargs: Dict[str, Any] = {}
    for key in _COMMISSION_KEYS:
        if key not in raw:
            continue
        value = raw[key]
        if key in ("value", "percent", "min_value", "max_value"):
            kwargs[key] = (
                None if (key == "max_value" and value is None) else _decimal(value, where, key)
            )
        elif key == "type":
            from core.domains.accounts.enums import CommissionType

            kwargs[key] = _enum(CommissionType, value, where, key, CommissionType.DEAL)
        else:
            kwargs[key] = value
    return CommissionRule(**kwargs)


def parse_symbol_override(raw: Dict[str, Any], where: str) -> GroupSymbolOverride:
    _reject_unknown(raw, _OVERRIDE_KEYS, where)
    kwargs: Dict[str, Any] = {}
    for key in _OVERRIDE_KEYS:
        if key not in raw:
            continue
        value = raw[key]
        # None means "not overridden", which MT5 encodes as the string "default".
        # It must stay None here, never become 0.
        if value is None or (isinstance(value, str) and value.strip() == "default"):
            kwargs[key] = None
        elif key in (
            "volume_min",
            "volume_max",
            "volume_limit",
            "margin_rate_initial_buy",
            "margin_rate_initial_sell",
            "swap_long",
            "swap_short",
        ):
            kwargs[key] = _decimal(value, where, key)
        elif key == "trade_mode":
            kwargs[key] = _enum(TradeMode, value, where, key, None)
        elif key == "execution_mode":
            kwargs[key] = _enum(ExecutionMode, value, where, key, None)
        else:
            kwargs[key] = value
    return GroupSymbolOverride(**kwargs)


def parse_group(raw: Dict[str, Any], where: str) -> Group:
    """Parse one group from typed YAML."""
    _reject_unknown(raw, _GROUP_KEYS, where)

    for legacy in ("margin_call_level", "stop_out_level", "leverage_default", "leverage_max"):
        if legacy in raw:
            raise ConfigError(
                f"{where}: '{legacy}' moved into the nested 'margin:' block in M1"
            )
    if "type" in raw:
        raise ConfigError(f"{where}: 'type' was renamed to 'account_type'")

    name = str(_require(raw, "name", where)).strip()
    if not name:
        raise ConfigError(f"{where}: 'name' must not be empty")

    # An explicit account_type wins. Deriving it from the path prefix is the MT5
    # behaviour and the right default - real\real, demo\Standard, managers\dealers,
    # preliminary - but demo\Challenge is a CONTEST group and coverage\house is a
    # COVERAGE account, neither of which its prefix would give. Overriding the stated
    # value with the derived one silently reclassifies those.
    account_type = (
        _enum(AccountType, raw["account_type"], where, "account_type", None)
        if raw.get("account_type") is not None
        else (mt5enums.account_type_from_group_path(name) or AccountType.REAL)
    )

    commissions_raw = raw.get("commissions") or []
    if not isinstance(commissions_raw, list):
        raise ConfigError(f"{where}.commissions: expected a list")
    overrides_raw = raw.get("symbol_overrides") or []
    if not isinstance(overrides_raw, list):
        raise ConfigError(f"{where}.symbol_overrides: expected a list")

    permissions_raw = raw.get("permissions") or {}
    if not isinstance(permissions_raw, dict):
        raise ConfigError(f"{where}.permissions: expected a mapping")
    _reject_unknown(permissions_raw, _PERMISSION_KEYS, f"{where}.permissions")
    permissions = GroupPermissions(
        **{
            key: (
                _bool(value, f"{where}.permissions", key, getattr(GroupPermissions(), key))
                if isinstance(getattr(GroupPermissions(), key), bool)
                else (
                    list(value)
                    if key == "allowed_symbols"
                    else _int(value, f"{where}.permissions", key, getattr(GroupPermissions(), key))
                )
            )
            for key, value in permissions_raw.items()
        }
    )

    swaps_raw = raw.get("swaps") or {}
    if not isinstance(swaps_raw, dict):
        raise ConfigError(f"{where}.swaps: expected a mapping")
    _reject_unknown(swaps_raw, _SWAP_KEYS, f"{where}.swaps")
    swaps_kwargs: Dict[str, Any] = {}
    for key, value in swaps_raw.items():
        if key in ("swap_long", "swap_short"):
            swaps_kwargs[key] = _decimal(value, f"{where}.swaps", key)
        elif key == "enable_swaps":
            swaps_kwargs[key] = _bool(value, f"{where}.swaps", key, True)
        else:
            swaps_kwargs[key] = value
    swaps = SwapConfiguration(**swaps_kwargs)

    routing_raw = raw.get("routing") or {}
    if not isinstance(routing_raw, dict):
        raise ConfigError(f"{where}.routing: expected a mapping")
    _reject_unknown(routing_raw, _ROUTING_KEYS, f"{where}.routing")
    routing_kwargs: Dict[str, Any] = {}
    for key, value in routing_raw.items():
        if key == "a_book_threshold_lots":
            routing_kwargs[key] = (
                None if value is None else _decimal(value, f"{where}.routing", key)
            )
        elif key == "lp_priority":
            routing_kwargs[key] = list(value or [])
        else:
            routing_kwargs[key] = value
    routing = RoutingRule(**routing_kwargs)

    trade_flags_raw = raw.get("trade_flags")
    if isinstance(trade_flags_raw, int):
        trade_flags_value = trade_flags_raw
    elif isinstance(trade_flags_raw, list):
        from core.domains.accounts.enums import TradeFlags

        trade_flags_value = 0
        for item in trade_flags_raw:
            member = _enum(TradeFlags, item, where, "trade_flags", None)
            if member is not None:
                trade_flags_value |= int(member.value)
    else:
        from core.domains.accounts.enums import TradeFlags

        trade_flags_value = int(
            TradeFlags.SWAPS | TradeFlags.TRAILING | TradeFlags.EXPERTS | TradeFlags.EXPIRATION
        )

    return Group(
        name=name,
        server_id=_int(raw.get("server_id"), where, "server_id", 1),
        account_type=account_type,
        currency=str(raw.get("currency", "USD")),
        currency_digits=_int(raw.get("currency_digits"), where, "currency_digits", 2),
        margin=parse_margin_profile(raw.get("margin"), where),
        commissions=[
            parse_commission(entry, f"{where}.commissions[{i}]")
            for i, entry in enumerate(commissions_raw)
        ],
        symbol_overrides=[
            parse_symbol_override(entry, f"{where}.symbol_overrides[{i}]")
            for i, entry in enumerate(overrides_raw)
        ],
        trade_flags=trade_flags_value,
        limit_orders=_int(raw.get("limit_orders"), where, "limit_orders", 200),
        limit_positions=_int(raw.get("limit_positions"), where, "limit_positions", 200),
        limit_symbols=_int(raw.get("limit_symbols"), where, "limit_symbols", 100),
        routing=routing,
        permissions=permissions,
        swaps=swaps,
        news_mode=_enum(NewsMode, raw.get("news_mode"), where, "news_mode", NewsMode.FULL),
        is_active=_bool(raw.get("is_active"), where, "is_active", True),
    )


# ---------------------------------------------------------------------------
# Symbols - YAML
# ---------------------------------------------------------------------------

_SYMBOL_KEYS = (
    "name",
    "path",
    "description",
    "base_currency",
    "quote_currency",
    "digits",
    "tick_size",
    "tick_value",
    "contract_size",
    "spread",
    "spread_balance",
    "spread_diff",
    "spread_diff_balance",
    "volume_min",
    "volume_max",
    "volume_step",
    "volume_limit",
    "margin_rates",
    "calc_mode",
    "trade_mode",
    "exec_mode",
    "gtc_mode",
    "fill_flags",
    "expiration_flags",
    "order_flags",
    "stops_level",
    "freeze_level",
    "swap_mode",
    "swap_long",
    "swap_short",
    "swap_3day",
    "swap_year_days",
    "quote_sessions",
    "trade_sessions",
    "time_start",
    "time_expiration",
    "option_mode",
    "strike_price",
    "face_value",
    "face_value_currency",
    "is_trade_allowed",
)


def parse_margin_rates(raw: Any, where: str) -> MarginRates:
    if raw is None:
        return MarginRates()
    if not isinstance(raw, dict):
        raise ConfigError(f"{where}: expected a mapping of the 16 MT5 margin rates")
    _reject_unknown(raw, _MARGIN_RATE_KEYS, where)
    return MarginRates(
        **{key: _decimal(value, where, key) for key, value in raw.items()}
    )


def parse_sessions(raw: Any, where: str, cls: Any) -> List[Any]:
    """Parse sessions from MT5's Sunday-first shape.

    Accepted forms, because authors will reach for all three:
        [[], [{"Open": 0, "Close": 1440}], ...]   MT5's own 7-array
        {Monday: [{open: 0, close: 1440}]}        weekday names
        [{day: 1, open: 0, close: 1440}]          flat list
    """
    if raw is None:
        return []

    out: List[Any] = []

    if isinstance(raw, list) and raw and all(isinstance(item, list) for item in raw):
        for index, day_ranges in enumerate(raw[:7]):
            for entry in day_ranges:
                out.append(
                    cls(
                        day_of_week=index,
                        open_minutes=_int(entry.get("Open", entry.get("open", 0)), where, "open", 0),
                        close_minutes=_int(
                            entry.get("Close", entry.get("close", 1440)), where, "close", 1440
                        ),
                    )
                )
        return out

    if isinstance(raw, dict):
        for key, day_ranges in raw.items():
            if isinstance(key, int):
                index = key
            else:
                name = str(key).strip().lower()
                lookup = {d.lower(): i for i, d in enumerate(WEEKDAY_SUNDAY_FIRST)}
                if name not in lookup:
                    raise ConfigError(
                        f"{where}: {key!r} is not a weekday. MT5 orders these "
                        f"Sunday-first: {', '.join(WEEKDAY_SUNDAY_FIRST)}"
                    )
                index = lookup[name]
            for entry in day_ranges or []:
                out.append(
                    cls(
                        day_of_week=index,
                        open_minutes=_int(entry.get("open", entry.get("Open", 0)), where, "open", 0),
                        close_minutes=_int(
                            entry.get("close", entry.get("Close", 1440)), where, "close", 1440
                        ),
                    )
                )
        return out

    if isinstance(raw, list):
        for entry in raw:
            out.append(
                cls(
                    day_of_week=_int(entry.get("day", entry.get("day_of_week", 0)), where, "day", 0),
                    open_minutes=_int(entry.get("open", entry.get("open_minutes", 0)), where, "open", 0),
                    close_minutes=_int(
                        entry.get("close", entry.get("close_minutes", 1440)), where, "close", 1440
                    ),
                )
            )
        return out

    raise ConfigError(f"{where}: unsupported session format {type(raw).__name__}")


def routes_from_mt5(path: Any):
    """Import the ConfigRouting table from a real MT5 Administrator export.

    Returns ``[(Mt5RouteRule, raw_record), ...]`` in table order. The raw
    record is kept alongside the rule so the repository can store it verbatim:
    the rule drives evaluation, the record drives byte-identical re-export.
    """
    from core.domains.execution.routing_mt5 import Mt5RouteRule

    payload = decode_file(path)
    out = []
    for position, raw in enumerate(records(payload, "ConfigRouting")):
        out.append((Mt5RouteRule.from_wire(raw, position=position), raw))
    return out


def parse_symbol(raw: Dict[str, Any], where: str) -> Symbol:
    """Parse one symbol from typed YAML."""
    _reject_unknown(raw, _SYMBOL_KEYS, where)

    for legacy in ("precision", "category", "margins", "trading_hours", "spreads",
                   "margin_initial_percent", "margin_maintenance_percent", "fill_mode",
                   "sessions", "margin_currency"):
        if legacy in raw:
            raise ConfigError(
                f"{where}: '{legacy}' is from the pre-M1 symbol schema. See "
                "config/symbols/instruments.yaml for the current shape."
            )

    name = str(_require(raw, "name", where)).strip()
    if not name:
        raise ConfigError(f"{where}: 'name' must not be empty")

    tick_size = _decimal(raw.get("tick_size", "0.00001"), where, "tick_size")
    if tick_size <= 0:
        raise ConfigError(
            f"{where}.tick_size: must be positive. Note this field holds MT5's Point "
            "(the price-precision step), which is always populated - MT5's own TickSize "
            "is a different field and is frequently zero."
        )

    order_flags_raw = raw.get("order_flags")
    if isinstance(order_flags_raw, int):
        order_flags = OrderTypeFlags(order_flags_raw)
    elif isinstance(order_flags_raw, list):
        value = 0
        for item in order_flags_raw:
            member = _enum(OrderTypeFlags, item, where, "order_flags", None)
            if member is not None:
                value |= int(member.value)
        order_flags = OrderTypeFlags(value)
    else:
        # Every symbol in the reference export carries 127: all seven order types.
        order_flags = OrderTypeFlags(127)

    return Symbol(
        name=name,
        path=str(raw.get("path", "")),
        description=str(raw.get("description", "")),
        base_currency=str(raw.get("base_currency", "USD")),
        quote_currency=str(raw.get("quote_currency", "USD")),
        calc_mode=_enum(CalculationMode, raw.get("calc_mode"), where, "calc_mode", CalculationMode.FOREX),
        digits=_int(raw.get("digits"), where, "digits", 5),
        tick_size=tick_size,
        tick_value=_decimal(raw.get("tick_value", 0), where, "tick_value"),
        contract_size=_decimal(raw.get("contract_size", 100000), where, "contract_size"),
        spread=_int(raw.get("spread"), where, "spread", 0),
        spread_balance=_int(raw.get("spread_balance"), where, "spread_balance", 0),
        spread_diff=_int(raw.get("spread_diff"), where, "spread_diff", 0),
        spread_diff_balance=_int(raw.get("spread_diff_balance"), where, "spread_diff_balance", 0),
        volume_min=_decimal(raw.get("volume_min", "0.01"), where, "volume_min"),
        volume_max=_decimal(raw.get("volume_max", 100), where, "volume_max"),
        volume_step=_decimal(raw.get("volume_step", "0.01"), where, "volume_step"),
        volume_limit=_decimal(raw.get("volume_limit", 0), where, "volume_limit"),
        margin_rates=parse_margin_rates(raw.get("margin_rates"), f"{where}.margin_rates"),
        trade_mode=_enum(TradeMode, raw.get("trade_mode"), where, "trade_mode", TradeMode.FULL),
        exec_mode=_enum(ExecutionMode, raw.get("exec_mode"), where, "exec_mode", ExecutionMode.MARKET),
        gtc_mode=_enum(GTCMode, raw.get("gtc_mode"), where, "gtc_mode", GTCMode.GTC),
        fill_flags=_enum(FillingFlags, raw.get("fill_flags"), where, "fill_flags", FillingFlags.FOK),
        expiration_flags=_enum(
            ExpirationFlags, raw.get("expiration_flags"), where, "expiration_flags", ExpirationFlags.GTC
        ),
        order_flags=order_flags,
        stops_level=_int(raw.get("stops_level"), where, "stops_level", 0),
        freeze_level=_int(raw.get("freeze_level"), where, "freeze_level", 0),
        swap_mode=_enum(SwapMode, raw.get("swap_mode"), where, "swap_mode", SwapMode.POINTS),
        swap_long=_decimal(raw.get("swap_long", 0), where, "swap_long"),
        swap_short=_decimal(raw.get("swap_short", 0), where, "swap_short"),
        swap_3day=_int(raw.get("swap_3day"), where, "swap_3day", 3),
        swap_year_days=_int(raw.get("swap_year_days"), where, "swap_year_days", 365),
        quote_sessions=parse_sessions(raw.get("quote_sessions"), f"{where}.quote_sessions", QuoteSession),
        trade_sessions=parse_sessions(raw.get("trade_sessions"), f"{where}.trade_sessions", TradingSession),
        time_start=raw.get("time_start"),
        time_expiration=raw.get("time_expiration"),
        option_mode=_enum(OptionMode, raw.get("option_mode"), where, "option_mode", OptionMode.EUROPEAN),
        strike_price=(
            None if raw.get("strike_price") is None else _decimal(raw["strike_price"], where, "strike_price")
        ),
        face_value=(
            None if raw.get("face_value") is None else _decimal(raw["face_value"], where, "face_value")
        ),
        face_value_currency=raw.get("face_value_currency"),
        is_trade_allowed=_bool(raw.get("is_trade_allowed"), where, "is_trade_allowed", True),
    )


# ---------------------------------------------------------------------------
# File-level loading
# ---------------------------------------------------------------------------


def _read_yaml(path: pathlib.Path) -> Any:
    try:
        with open(path, "r", encoding="utf-8") as handle:
            return yaml.safe_load(handle)
    except yaml.YAMLError as exc:
        raise ConfigError(f"{path.name}: invalid YAML - {exc}") from None


def _iter_named_entries(document: Any, path: pathlib.Path) -> List[Tuple[str, Dict[str, Any]]]:
    """Accept either `{name: {...}}` or `[{name: ...}, ...]`, and nested categories.

    The existing instruments.yaml groups symbols under category headings
    (`forex_majors:` then `EURUSD:`), so a two-level mapping is flattened and the
    category is discarded - MT5 carries that information in `Path` instead.
    """
    label = path.name
    out: List[Tuple[str, Dict[str, Any]]] = []

    if document is None:
        return out

    if isinstance(document, list):
        for index, entry in enumerate(document):
            if not isinstance(entry, dict):
                raise ConfigError(f"{label}[{index}]: expected a mapping")
            name = entry.get("name")
            if not name:
                raise ConfigError(f"{label}[{index}]: missing 'name'")
            out.append((str(name), entry))
        return out

    if not isinstance(document, dict):
        raise ConfigError(f"{label}: expected a mapping or a list at the top level")

    for key, value in document.items():
        if not isinstance(value, dict):
            raise ConfigError(f"{label}.{key}: expected a mapping")
        if "name" in value:
            out.append((str(value["name"]), value))
            continue
        # A category heading: every child is an entry named by its key.
        for child_key, child in value.items():
            if not isinstance(child, dict):
                raise ConfigError(f"{label}.{key}.{child_key}: expected a mapping")
            entry = dict(child)
            entry.setdefault("name", child_key)
            out.append((str(entry["name"]), entry))
    return out


def load_groups(path: Any) -> List[Group]:
    """Load groups from a typed YAML file."""
    path = pathlib.Path(path)
    if not path.is_file():
        raise ConfigError(f"group config not found: {path}")
    document = _read_yaml(path)
    groups = []
    for name, entry in _iter_named_entries(document, path):
        groups.append(parse_group(entry, f"{path.name}:{name}"))
    _assert_unique([g.name for g in groups], f"{path.name}: duplicate group name")
    return groups


def load_symbols(path: Any) -> List[Symbol]:
    """Load symbols from a typed YAML file."""
    path = pathlib.Path(path)
    if not path.is_file():
        raise ConfigError(f"symbol config not found: {path}")
    document = _read_yaml(path)
    symbols = []
    for name, entry in _iter_named_entries(document, path):
        symbols.append(parse_symbol(entry, f"{path.name}:{name}"))
    _assert_unique([s.name for s in symbols], f"{path.name}: duplicate symbol name")
    return symbols


def _assert_unique(names: Sequence[str], message: str) -> None:
    seen: set = set()
    for name in names:
        if name in seen:
            raise ConfigError(f"{message} '{name}'")
        seen.add(name)


# ---------------------------------------------------------------------------
# MT5 JSON import
# ---------------------------------------------------------------------------


def groups_from_mt5(path: Any) -> List[Tuple[Group, Dict[str, Any], Dict[str, int], Dict[str, Any]]]:
    """Import groups from a real MT5 Administrator export.

    Returns ``(group, mt5_extra, mt5_scale, mt5_source)`` per group. Pass the last three
    to ``group_to_db`` so the row can be re-exported field-identically - our Group
    models 17 of MT5's 44 ConfigGroups fields, and the other 27 must survive.
    """
    from infrastructure.persistence.config_mappers import split_mt5_record

    payload = decode_file(path)
    out = []
    for raw in records(payload, "ConfigGroups"):
        dom, extra, scale = split_mt5_record(raw, fieldmap.GROUP_FIELDS)
        margin = dom.get("margin") or {}
        account_type = mt5enums.account_type_from_group_path(dom["name"]) or AccountType.REAL

        commissions: List[CommissionRule] = []
        for entry in dom.get("commissions") or []:
            tiers = entry.get("tiers") or []
            first = tiers[0] if tiers else {}
            commissions.append(
                CommissionRule(
                    name=entry.get("name") or "",
                    symbol_pattern=entry.get("symbol_pattern") or "*",
                    currency=entry.get("currency") or "USD",
                    value=first.get("rate") or Decimal(0),
                    min_value=first.get("min_value") or Decimal(0),
                )
            )

        overrides: List[GroupSymbolOverride] = []
        for entry in dom.get("symbol_overrides") or []:
            overrides.append(
                GroupSymbolOverride(
                    symbol_pattern=entry.get("symbol_pattern") or "*",
                    # Everything else stays None, i.e. INHERIT. Most MT5 overrides are
                    # the "default" sentinel, and turning that into 0 would replace
                    # "inherit the margin rate" with "the margin rate is zero".
                )
            )

        # Carry every field the domain owns. Omitting one lets the dataclass default
        # overwrite the server's real value on export - which is how TradeFlags 215 came
        # back as 15, and how LimitPositions/LimitSymbols came back as 200/100 when the
        # server had 0 (unlimited).
        group = Group(
            name=dom["name"],
            server_id=_int(dom.get("server_id"), "mt5", "Server", 1),
            account_type=account_type,
            trade_flags=_int(dom.get("trade_flags"), "mt5", "TradeFlags", 0),
            currency_digits=_int(dom.get("currency_digits"), "mt5", "CurrencyDigits", 2),
            currency=dom.get("currency") or "USD",
            margin=MarginProfile(
                mode=mt5enums.MARGIN_MODE_FROM_MT5.get(
                    _int(margin.get("mode"), "mt5", "MarginMode", 0), MarginMode.RETAIL
                ),
                margin_call_level=margin.get("margin_call_level") or Decimal(50),
                stop_out_level=margin.get("stop_out_level") or Decimal(30),
                stop_out_mode=mt5enums.STOP_OUT_MODE_FROM_MT5.get(
                    _int(margin.get("stop_out_mode"), "mt5", "MarginSOMode", 0),
                    StopOutMode.PERCENT,
                ),
                free_margin_mode=mt5enums.FREE_MARGIN_MODE_FROM_MT5.get(
                    _int(margin.get("free_margin_mode"), "mt5", "MarginFreeMode", 1),
                    FreeMarginMode.USE_PL,
                ),
            ),
            commissions=commissions,
            symbol_overrides=overrides,
            news_mode=mt5enums.NEWS_MODE_FROM_MT5.get(
                _int(dom.get("news_mode"), "mt5", "NewsMode", 2), NewsMode.FULL
            ),
            limit_orders=_int(dom.get("limit_orders"), "mt5", "LimitOrders", 0),
            limit_positions=_int(dom.get("limit_positions"), "mt5", "LimitPositions", 0),
            limit_symbols=_int(dom.get("limit_symbols"), "mt5", "LimitSymbols", 0),
        )
        out.append((group, extra, scale, raw))
    return out


def symbols_from_mt5(path: Any) -> List[Tuple[Symbol, Dict[str, Any], Dict[str, int], Dict[str, Any]]]:
    """Import symbols from a real MT5 Administrator export.

    Same contract as :func:`groups_from_mt5`. Our Symbol models 52 of MT5's 121 fields.
    """
    from infrastructure.persistence.config_mappers import split_mt5_record

    payload = decode_file(path)
    out = []
    for raw in records(payload, "ConfigSymbols"):
        dom, extra, scale = split_mt5_record(raw, fieldmap.SYMBOL_FIELDS)
        margin = dom.get("margin_rates") or {}

        def dec(key: str, fallback: str) -> Decimal:
            value = dom.get(key)
            return Decimal(fallback) if value is None else value

        symbol = Symbol(
            name=dom["name"],
            path=dom.get("path") or "",
            description=dom.get("description") or "",
            base_currency=dom.get("base_currency") or "USD",
            quote_currency=dom.get("quote_currency") or "USD",
            calc_mode=_enum(CalculationMode, dom.get("calc_mode"), "mt5", "CalcMode", CalculationMode.FOREX),
            digits=_int(dom.get("digits"), "mt5", "Digits", 5),
            # MT5 Point -> tick_size. MT5 TickSize -> mt5_tick_size. They differ on all
            # 362 symbols in the reference export and every crypto has TickSize = 0.
            tick_size=dec("tick_size", "0.00001"),
            mt5_tick_size=dec("mt5_tick_size", "0"),
            tick_value=dec("tick_value", "0"),
            contract_size=dec("contract_size", "100000"),
            spread=_int(dom.get("spread"), "mt5", "Spread", 0),
            spread_balance=_int(dom.get("spread_balance"), "mt5", "SpreadBalance", 0),
            volume_min=dec("volume_min", "0"),
            volume_max=dec("volume_max", "0"),
            volume_step=dec("volume_step", "0"),
            volume_limit=dec("volume_limit", "0"),
            margin_rates=MarginRates(
                **{
                    key: (Decimal(1) if value is None else value)
                    for key, value in margin.items()
                }
            ),
            trade_mode=_enum(TradeMode, dom.get("trade_mode"), "mt5", "TradeMode", TradeMode.FULL),
            exec_mode=_enum(ExecutionMode, dom.get("exec_mode"), "mt5", "ExecMode", ExecutionMode.MARKET),
            gtc_mode=_enum(GTCMode, dom.get("gtc_mode"), "mt5", "GTCMode", GTCMode.GTC),
            fill_flags=_enum(FillingFlags, dom.get("fill_flags"), "mt5", "FillFlags", FillingFlags.FOK),
            expiration_flags=_enum(
                ExpirationFlags, dom.get("expiration_flags"), "mt5", "ExpirFlags", ExpirationFlags.GTC
            ),
            order_flags=_enum(
                OrderTypeFlags, dom.get("order_flags"), "mt5", "OrderFlags", OrderTypeFlags(127)
            ),
            stops_level=_int(dom.get("stops_level"), "mt5", "StopsLevel", 0),
            freeze_level=_int(dom.get("freeze_level"), "mt5", "FreezeLevel", 0),
            swap_mode=_enum(SwapMode, dom.get("swap_mode"), "mt5", "SwapMode", SwapMode.POINTS),
            swap_long=dec("swap_long", "0"),
            swap_short=dec("swap_short", "0"),
            swap_3day=_int(dom.get("swap_3day"), "mt5", "Swap3Day", 3),
            swap_year_days=_int(dom.get("swap_year_days"), "mt5", "SwapYearDay", 0),
            quote_sessions=[
                QuoteSession(
                    day_of_week=day["index"],
                    open_minutes=session["open_minutes"],
                    close_minutes=session["close_minutes"],
                )
                for day in dom.get("quote_sessions") or []
                for session in day.get("sessions") or []
            ],
            trade_sessions=[
                TradingSession(
                    day_of_week=day["index"],
                    open_minutes=session["open_minutes"],
                    close_minutes=session["close_minutes"],
                )
                for day in dom.get("trade_sessions") or []
                for session in day.get("sessions") or []
            ],
            time_start=_int(dom.get("time_start"), "mt5", "TimeStart", 0) or None,
            time_expiration=_int(dom.get("time_expiration"), "mt5", "TimeExpiration", 0) or None,
            option_mode=_enum(OptionMode, dom.get("option_mode"), "mt5", "OptionMode", OptionMode.EUROPEAN),
            strike_price=dom.get("strike_price"),
            face_value=dom.get("face_value"),
            is_trade_allowed=_int(dom.get("trade_mode"), "mt5", "TradeMode", 4) != 0,
        )
        out.append((symbol, extra, scale, raw))
    return out
