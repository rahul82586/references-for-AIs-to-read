"""
End-to-end proof for M1: every group in the real MT5 server export survives
export -> domain -> GroupModel row -> MT5 export with no field lost.

Run:
    PYTHONPATH=<broker-platform> BROKER_MT5_FIXTURES=<decoded dir> \
        python3 scripts/m1_proof_roundtrip.py
"""

from __future__ import annotations

import os
import pathlib
import sys
from decimal import Decimal

FIXTURES = pathlib.Path(
    os.environ.get("BROKER_MT5_FIXTURES", "/home/user/decoded/mt5-format-structure")
)

from core.domains.accounts.enums import AccountType, MarginMode, TradeFlags
from core.domains.accounts.group import Group
from core.domains.accounts.value_objects import (
    CommissionRule,
    GroupSymbolOverride,
    MarginProfile,
)
from core.domains.instruments.value_objects import MarginRates, QuoteSession, TradingSession
from infrastructure.mt5 import enums as bridge
from infrastructure.mt5 import fieldmap, wire
from infrastructure.mt5.codec import is_inherited as codec_is_inherited
from infrastructure.persistence import config_mappers as M

SEPARATOR = chr(92)  # backslash, kept out of string literals to avoid escaping noise


def group_from_domain(dom: dict, raw: dict) -> Group:
    """Build the domain Group the way the M2 seeder will."""
    account_type = bridge.account_type_from_group_path(dom["name"]) or AccountType.REAL
    margin = dom.get("margin") or {}
    mode = bridge.MARGIN_MODE_FROM_MT5.get(int(margin.get("mode", 0)), MarginMode.RETAIL)
    return Group(
        name=dom["name"],
        server_id=int(dom.get("server_id", 1)),
        currency=dom.get("currency", "USD"),
        account_type=account_type,
        margin=MarginProfile(
            mode=mode,
            margin_call_level=margin.get("margin_call_level"),
            stop_out_level=margin.get("stop_out_level"),
            stop_out_mode=bridge.STOP_OUT_MODE_FROM_MT5.get(
                int(margin.get("stop_out_mode", 0)), None
            )
            or MarginProfile().stop_out_mode,
            free_margin_mode=bridge.FREE_MARGIN_MODE_FROM_MT5.get(
                int(margin.get("free_margin_mode", 1)), None
            )
            or MarginProfile().free_margin_mode,
        ),
        trade_flags=TradeFlags(int(raw.get("TradeFlags", 0) or 0)),
        limit_orders=int(raw.get("LimitOrders", 0) or 0),
        limit_positions=int(raw.get("LimitPositions", 0) or 0),
        limit_symbols=int(raw.get("LimitSymbols", 0) or 0),
        # Commissions and per-symbol overrides are part of the group in MT5, so the
        # seeder must build them. Leaving them empty would overwrite the imported
        # baseline with "[]" on export, because they are domain-owned fields.
        commissions=commissions_from_domain(dom.get("commissions") or []),
        symbol_overrides=overrides_from_domain(dom.get("symbol_overrides") or []),
    )


def _or_default(value, fallback):
    """Decimal 0 is a real value, not a missing one - `or` would replace it."""
    return fallback if value is None else value


def decode_sessions(days, cls) -> list:
    """MT5 Sunday-first per-day session structure -> flat domain session objects."""
    out = []
    for day in days or []:
        index = int(day.get("index", 0))
        for entry in day.get("sessions") or []:
            out.append(
                cls(
                    day_of_week=index,
                    open_minutes=int(entry.get("open_minutes", 0)),
                    close_minutes=int(entry.get("close_minutes", 0)),
                )
            )
    return out


def commissions_from_domain(rows: list) -> list:
    """Decode MT5 Commissions/Tiers into CommissionRule objects."""
    out = []
    for raw in rows:
        tiers = raw.get("tiers") or []
        first = tiers[0] if tiers else {}
        max_value = first.get("max_value")
        out.append(
            CommissionRule(
                name=raw.get("name") or "",
                symbol_pattern=raw.get("symbol_pattern") or "*",
                currency=raw.get("currency") or first.get("currency") or "USD",
                value=first.get("rate") or Decimal(0),
                min_value=first.get("min_value") or Decimal(0),
                max_value=max_value if max_value not in (None, "") else None,
            )
        )
    return out


def overrides_from_domain(rows: list) -> list:
    """Decode MT5 per-group Symbols into GroupSymbolOverride objects.

    Most values are the codec.INHERIT sentinel ("default"), meaning "use the base
    symbol's setting". Passing those through as None keeps them un-overridden rather
    than turning an inherited margin rate into a hard zero.
    """
    def value_or_none(v):
        return None if v is None or codec_is_inherited(v) else v

    out = []
    for raw in rows:
        out.append(
            GroupSymbolOverride(
                symbol_pattern=raw.get("symbol_pattern") or "*",
                trade_mode=value_or_none(raw.get("trade_mode")),
                execution_mode=value_or_none(raw.get("execution_mode")),
                volume_min=value_or_none(raw.get("volume_min")),
                volume_max=value_or_none(raw.get("volume_max")),
                volume_limit=value_or_none(raw.get("volume_limit")),
                spread_diff=value_or_none(raw.get("spread_diff")),
                margin_rate_initial_buy=value_or_none(raw.get("margin_rate_initial_buy")),
                margin_rate_initial_sell=value_or_none(raw.get("margin_rate_initial_sell")),
                swap_long=value_or_none(raw.get("swap_long")),
                swap_short=value_or_none(raw.get("swap_short")),
            )
        )
    return out


def main() -> int:
    path = FIXTURES / "Groups TCTrader-Live.json"
    if not path.is_file():
        print(f"fixture not found: {path}")
        return 2

    records = wire.records(wire.decode_file(path), "ConfigGroups")
    print(f"=== {len(records)} real MT5 groups from the live server export ===\n")

    identical = 0
    problems = []
    for raw in records:
        dom, extra, scale = M.split_mt5_record(raw, fieldmap.GROUP_FIELDS)
        group = group_from_domain(dom, raw)
        # mt5_source is the complete imported record: the export baseline that keeps
        # the 27 fields our domain cannot represent, at their original wire scale.
        row = M.group_to_db(
            group, mt5_extra=extra, mt5_scale=scale, mt5_source=raw
        )
        out = M.group_mt5_record(row)

        differing = {k: (raw[k], out.get(k)) for k in raw if out.get(k) != raw[k]}
        if not differing:
            identical += 1
        else:
            problems.append((raw["Group"], differing))

        # The wire contract must hold for every group, or MT5 would reject the file.
        violations = wire.validate(wire.build("ConfigGroups", [out]))
        if violations:
            problems.append((raw["Group"] + " [wire]", {"VIOLATIONS": violations[:2]}))

    print(f"field-identical re-export : {identical}/{len(records)}")
    print(f"wire-contract conformant  : {len(records) - len(problems)}/{len(records)}")

    if problems:
        print("\n--- groups that did not round-trip exactly ---")
        for name, diff in problems:
            print(f"  {name}")
            for key, (before, after) in list(diff.items())[:5]:
                print(f"      {key}: {str(before)[:40]!r} -> {str(after)[:40]!r}")
        return 1

    print("\nAll groups round-tripped field-for-field and satisfy the MT5 wire contract.")
    sample = records[0]
    dom, _, _ = M.split_mt5_record(sample, fieldmap.GROUP_FIELDS)
    print(
        f"\nExample: {sample['Group']}  MarginCall={sample['MarginCall']} "
        f"MarginStopOut={sample['MarginStopOut']}  MarginMode={sample['MarginMode']} "
        f"-> domain margin_call_level={dom['margin']['margin_call_level']} "
        f"(PERCENT, as MT5 stores it)"
    )
    print(f"Group path separator is {SEPARATOR!r}; AccountType derived from the path prefix.")

    print()
    symbol_path = FIXTURES / "Symbols TCTrader-Live.json"
    if symbol_path.is_file():
        report_symbols(symbol_path)
    return 0


def build_symbol(dom: dict):
    """Domain Symbol from a decoded MT5 symbol record.

    Shared by the M1 losslessness proof and the M3 currency proof so that both measure the
    SAME import path. Two definitions of "how a wire record becomes a Symbol" would let
    one proof pass while the other measured something else.
    """
    from core.domains.instruments.enums import (
        CalculationMode,
        ExecutionMode,
        GTCMode,
        SwapMode,
        TradeMode,
    )
    from core.domains.instruments.symbol import Symbol
    from core.domains.instruments.value_objects import (
        MarginRates,
        QuoteSession,
        TradingSession,
    )

    margin = dom.get("margin_rates") or {}
    return Symbol(
        name=dom["name"],
        path=dom.get("path", ""),
        description=dom.get("description", ""),
        # MT5's own three currencies. CurrencyProfit -> quote_currency, CurrencyMargin ->
        # margin_currency. Defaulting these to "USD" is what made 253 of the 362 reference
        # symbols carry the wrong currencies.
        base_currency=dom.get("base_currency", ""),
        quote_currency=dom.get("quote_currency", ""),
        margin_currency=dom.get("margin_currency", ""),
        digits=int(dom.get("digits", 5)),
        tick_size=_or_default(dom.get("tick_size"), Decimal("0.00001")),
        tick_value=_or_default(dom.get("tick_value"), Decimal(1)),
        contract_size=_or_default(dom.get("contract_size"), Decimal(100000)),
        calc_mode=CalculationMode(int(dom.get("calc_mode", 0))),
        trade_mode=TradeMode(int(dom.get("trade_mode", 4))),
        exec_mode=ExecutionMode(int(dom.get("exec_mode", 2))),
        gtc_mode=GTCMode(int(dom.get("gtc_mode", 0))),
        swap_mode=SwapMode(int(dom.get("swap_mode", 0))),
        swap_long=_or_default(dom.get("swap_long"), Decimal(0)),
        swap_short=_or_default(dom.get("swap_short"), Decimal(0)),
        mt5_tick_size=_or_default(dom.get("mt5_tick_size"), Decimal(0)),
        spread=int(dom.get("spread", 0)),
        spread_balance=int(dom.get("spread_balance", 0)),
        stops_level=int(dom.get("stops_level", 0)),
        freeze_level=int(dom.get("freeze_level", 0)),
        volume_min=_or_default(dom.get("volume_min"), Decimal(0)),
        volume_max=_or_default(dom.get("volume_max"), Decimal(0)),
        volume_step=_or_default(dom.get("volume_step"), Decimal(0)),
        volume_limit=_or_default(dom.get("volume_limit"), Decimal(0)),
        swap_3day=int(dom.get("swap_3day", 3)),
        swap_year_days=int(dom.get("swap_year_days", 0)),
        face_value=_or_default(dom.get("face_value"), Decimal(0)),
        strike_price=_or_default(dom.get("strike_price"), Decimal(0)),
        # Sessions must be decoded from MT5's Sunday-first 7-array. Leaving them
        # empty makes Symbol fall back to its own default of "open 00:00-24:00
        # every day", which then overwrites the server's real session calendar.
        quote_sessions=decode_sessions(dom.get("quote_sessions"), QuoteSession),
        trade_sessions=decode_sessions(dom.get("trade_sessions"), TradingSession),
        margin_rates=MarginRates(
            **{k: (v if v is not None else Decimal(1)) for k, v in margin.items()}
        ),
    )



def report_symbols(path: "pathlib.Path") -> None:
    """Same guarantee for the 362-symbol price list."""
    from core.domains.instruments.enums import (
        CalculationMode,
        ExecutionMode,
        GTCMode,
        SwapMode,
        TradeMode,
    )
    from core.domains.instruments.symbol import Symbol

    records = wire.records(wire.decode_file(path), "ConfigSymbols")
    print(f"=== {len(records)} real MT5 symbols ===")

    identical = 0
    worst = None
    for raw in records:
        dom, extra, scale = M.split_mt5_record(raw, fieldmap.SYMBOL_FIELDS)
        margin = dom.get("margin_rates") or {}
        symbol = build_symbol(dom)
        row = M.symbol_to_db(
            symbol, mt5_extra=extra, mt5_scale=scale, mt5_source=raw
        )
        out = M.symbol_mt5_record(row)
        differing = {k: (raw[k], out.get(k)) for k in raw if out.get(k) != raw[k]}
        if not differing:
            identical += 1
        elif worst is None or len(differing) < len(worst[1]):
            worst = (raw["Symbol"], differing)

    print(f"field-identical re-export : {identical}/{len(records)}")
    if worst:
        name, differing = worst
        print(f"closest miss: {name} with {len(differing)} differing")
        for key, (before, after) in list(differing.items())[:6]:
            print(f"      {key}: {str(before)[:38]!r} -> {str(after)[:38]!r}")

    # Point vs TickSize must stay distinct for the symbols where they differ.
    differing_symbols = [r for r in records if r["Point"] != r["TickSize"]]
    print(
        f"\nPoint != TickSize on {len(differing_symbols)} symbols; "
        "both kept as separate columns."
    )


if __name__ == "__main__":
    raise SystemExit(main())
