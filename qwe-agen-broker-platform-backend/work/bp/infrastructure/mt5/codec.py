"""
Typed conversion between MT5 Administrator records and our domain model.

Two directions, deliberately asymmetric:

``record_to_domain``  MT5 record (all-strings) -> nested Python dict with real types
                      (Decimal / int / bool / list). The IMPORT direction.

``domain_to_record``  domain values -> MT5 record with every scalar rendered as a
                      string at MT5's own scale. The EXPORT direction, which must be
                      exact or MT5 Administrator will reject the file.

The asymmetry is intentional: an import may normalise, an export may not guess. If a
value cannot be rendered unambiguously, ``domain_to_record`` raises rather than
emitting something plausible.

TWO EMPIRICAL FACTS drove this design. Both were measured against a live server
export (362 symbols, 20 groups), not assumed from documentation:

1. DECIMAL SCALE IS PER FIELD *AND* PER RECORD.
   ``Point``, ``TickValue``, ``ContractSize``, ``SwapLong`` always carry 8 places.
   ``VolumeMin`` / ``VolumeMax`` / ``VolumeStep`` and the ``Filter*`` fields carry
   ZERO places ("100", "40" - not "100.00000000"). ``FaceValue`` always carries 2.
   ``AccruedInterest`` carries 2, 5, 8 or 0 depending on the record. A single global
   scale therefore cannot round-trip. We capture each decimal's scale on the way in
   (``_mt5_scale``) and replay it on the way out. Fresh records with no captured
   scale fall back to ``SCALE``, then to ``DEFAULT_SCALE``.

2. ``Point`` AND ``TickSize`` ARE DIFFERENT FIELDS AND MUST NOT BE MERGED.
   They differ for 131 of 362 symbols; every crypto has ``TickSize`` = 0 while
   ``Point`` is the real precision step. See ``fieldmap.SYMBOL_FIELDS``.

Unit rules enforced here:
  * ``MarginCall`` / ``MarginStopOut`` are PERCENT on both sides. Never 0.8 / 0.5.
  * Flag fields are decimal-encoded bitmasks; ``flags_to_set`` expands them so no
    caller hand-rolls bit arithmetic.
  * Sessions are Sunday-first, minutes from midnight, 0..1440.
"""

from __future__ import annotations

from decimal import Decimal, InvalidOperation
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

from . import wire
from .fieldmap import (
    BOOL01,
    COMMISSION_FIELDS,
    COMMISSION_TIER_FIELDS,
    DEC,
    FEEDER_FIELDS,
    FLAGS,
    GATEWAY_FIELDS,
    GROUP_FIELDS,
    GROUP_SYMBOL_FIELDS,
    HOLIDAY_FIELDS,
    INT,
    MANAGER_FIELDS,
    NESTED,
    ROUTING_CONDITION_FIELDS,
    ROUTING_DEALER_FIELDS,
    ROUTING_FIELDS,
    SESSIONS,
    SYMBOL_FIELDS,
    STR,
    STRLIST,
    Field,
)

# Fallback wire scale for freshly-created records that were never decoded from an MT5
# export, so there is no captured scale to replay. Derived from the reference export:
# these are the scales MT5 itself uses when it writes the field.
SCALE: Dict[str, int] = {
    # Group margin / money - 2 places
    "MarginCall": 2,
    "MarginStopOut": 2,
    "TradeInterestrate": 2,
    "TradeVirtualCredit": 2,
    "DemoDeposit": 2,
    "LimitPositionsVolume": 2,
    "ActionValueFloat": 2,
    # Symbol money / rates - 8 places
    "Point": 8,
    "TickValue": 8,
    "ContractSize": 8,
    "SwapLong": 8,
    "SwapShort": 8,
    "MarginInitial": 8,
    "MarginMaintenance": 8,
    "MarginLiquidity": 8,
    "MarginHedged": 8,
    "MarginCurrency": 8,
    "PriceSettle": 8,
    "PriceLimitMax": 8,
    "PriceLimitMin": 8,
    "MarginInitialBuy": 8,
    "MarginInitialSell": 8,
    "FaceValue": 2,
    "AccruedInterest": 2,
    # Commission tiers - 8 places
    "Value": 8,
    "Minimal": 8,
    "Maximal": 8,
    "RangeFrom": 8,
    "RangeTo": 8,
    # Integer-valued decimals - MT5 writes these with NO decimal places
    "TickSize": 0,
    "VolumeMin": 0,
    "VolumeMax": 0,
    "VolumeStep": 0,
    "VolumeLimit": 0,
    "IEVolumeMax": 0,
    "FilterSoft": 0,
    "FilterHard": 0,
    "FilterDiscard": 0,
    "FilterSpreadMax": 0,
    "FilterSpreadMin": 0,
    "FilterGap": 0,
    "PriceStrike": 0,
    "SpreadDiff": 0,
    "SpreadDiffBalance": 0,
}

#: Default scale for a decimal field absent from :data:`SCALE`.
DEFAULT_SCALE = 8

#: MT5 writes Volume{Min,Max,Step,Limit} as INTEGERS scaled 10^4 against the lot,
#: with *Ext siblings at 10^8 (measured on the reference export: Ext == bare x
#: 10^4 for all 362 symbols x 4 fields, zero violations). EURUSD carries
#: VolumeMin="100" / VolumeMinExt="1000000" - a 0.01-lot minimum. They are NOT
#: decimals at scale 0; reading them as such made an imported EURUSD enforce a
#: 100-lot minimum, and rendering a YAML-seeded 0.01 at scale 0 wrote "0".
VOLUME_SCALED_FIELDS = frozenset({"VolumeMin", "VolumeMax", "VolumeStep", "VolumeLimit"})
VOLUME_WIRE_EXPONENT = 4
VOLUME_EXT_EXPONENT = 8

#: Nested section -> the field table describing its records.
#:
#: A nested field that is NOT listed here is passed through verbatim, which keeps an
#: unmodelled structure lossless on re-export. But it also means a domain-shaped dict
#: placed there would be emitted with domain keys and unquoted numbers, violating the
#: wire contract. Every nested field we build ourselves must be registered here:
#: "Commissions"/"Tiers" for group commissions, "Symbols" for per-group symbol
#: overrides (MT5 calls the override array "Symbols" inside a group record).
NESTED_TABLES: Dict[str, Tuple[Field, ...]] = {
    "Commissions": COMMISSION_FIELDS,
    "Tiers": COMMISSION_TIER_FIELDS,
    "Symbols": GROUP_SYMBOL_FIELDS,
    "Conditions": ROUTING_CONDITION_FIELDS,
    "Dealers": ROUTING_DEALER_FIELDS,
}

#: Key under which decoded-but-unmodelled MT5 fields are quarantined, so an export can
#: restore them instead of silently truncating the record.
EXTRA_KEY = "_mt5_extra"

#: Key under which the observed wire scale of each decimal is remembered.
SCALE_KEY = "_mt5_scale"

#: MT5's "inherit from the base symbol" sentinel, used in per-group symbol overrides.
#:
#: This is NOT an empty string and NOT zero. In the reference export 60 of the 64
#: override fields carry the literal string "default" for most groups, meaning "use
#: whatever the Symbol itself specifies". Coercing it to 0 would turn
#: "inherit the margin rate" into "the margin rate is zero", which is the difference
#: between a correct margin calculation and letting a client open an unbounded
#: position. It is preserved verbatim in both directions, and callers should test with
#: :func:`is_inherited` before using an override value.
INHERIT = "default"


def is_inherited(value: Any) -> bool:
    """True when an MT5 group-override value means "inherit from the base symbol"."""
    return isinstance(value, str) and value.strip() == INHERIT


class MT5ConversionError(ValueError):
    """Raised when a value cannot be converted without guessing."""


# ---------------------------------------------------------------------------
# Scalar conversion - inbound
# ---------------------------------------------------------------------------


def _to_decimal(raw: Any, field_name: str) -> Decimal:
    if isinstance(raw, Decimal):
        return raw
    if isinstance(raw, bool):
        raise MT5ConversionError(f"{field_name}: booleans are not part of the MT5 format")
    if isinstance(raw, (int, float)):
        return Decimal(str(raw))
    if not isinstance(raw, str):
        raise MT5ConversionError(f"{field_name}: expected a string, got {type(raw).__name__}")
    text = raw.strip()
    if text == "":
        return Decimal(0)
    try:
        return Decimal(text)
    except InvalidOperation as exc:
        raise MT5ConversionError(f"{field_name}: {raw!r} is not a decimal") from exc


def _to_int(raw: Any, field_name: str) -> int:
    if isinstance(raw, bool):
        raise MT5ConversionError(f"{field_name}: booleans are not part of the MT5 format")
    if isinstance(raw, int):
        return raw
    if not isinstance(raw, str):
        raise MT5ConversionError(f"{field_name}: expected a string, got {type(raw).__name__}")
    text = raw.strip()
    if text == "":
        return 0
    try:
        return int(text, 10)
    except ValueError as exc:
        raise MT5ConversionError(f"{field_name}: {raw!r} is not an integer") from exc


def wire_scale(raw: Any) -> Optional[int]:
    """Number of decimal places in an MT5 wire literal, or None if not applicable."""
    if not isinstance(raw, str):
        return None
    text = raw.strip()
    if not text:
        return None
    return len(text.split(".", 1)[1]) if "." in text else 0


def flags_to_set(raw: Any, field_name: str) -> Dict[str, bool]:
    """Expand a decimal bitmask into ``{"bit0": bool, ...}``.

    MT5 flag fields (TradeFlags, PermissionsFlags, MarginFlags, SwapFlags, REFlags,
    IEFlags, FillFlags, ExpirFlags, OrderFlags) are one decimal string whose bits each
    mean something. Consult the SDK's ``EnTradeFlags`` / ``EnGroupFlags`` enums for bit
    meanings; this helper only does the expansion.
    """
    value = _to_int(raw, field_name)
    if value == 0:
        return {}
    return {f"bit{i}": bool(value >> i & 1) for i in range(value.bit_length())}


def _to_bool01(raw: Any, field_name: str) -> bool:
    return _to_int(raw, field_name) != 0


# ---------------------------------------------------------------------------
# Sessions
# ---------------------------------------------------------------------------


def parse_sessions(raw: Any, field_name: str) -> List[Dict[str, Any]]:
    """Convert MT5's Sunday-first 7-array into explicit per-day session dicts.

    MT5 stores ``SessionsQuotes`` / ``SessionsTrades`` as seven arrays, index 0 =
    Sunday, each holding ``{"Open": "<minutes>", "Close": "<minutes>"}`` ranges counted
    from midnight over a 0..1440 minute day. An empty array means "closed".

    The returned structure names the weekday, so downstream code can never mistake
    MT5's Sunday-first ordering for Python's Monday-first ``weekday()``.
    """
    if raw is None:
        return []
    if not isinstance(raw, list):
        raise MT5ConversionError(f"{field_name}: expected a 7-element array")

    days: List[Dict[str, Any]] = []
    for index, day_ranges in enumerate(raw):
        name = (
            wire.WEEKDAY_SUNDAY_FIRST[index]
            if index < len(wire.WEEKDAY_SUNDAY_FIRST)
            else f"day{index}"
        )
        sessions = [
            {
                "open_minutes": _to_int(r.get("Open", "0"), f"{field_name}.{name}.Open"),
                "close_minutes": _to_int(r.get("Close", "0"), f"{field_name}.{name}.Close"),
            }
            for r in (day_ranges or [])
            if isinstance(r, dict)
        ]
        days.append({"day": name, "index": index, "closed": not sessions, "sessions": sessions})
    return days


def render_sessions(days: Sequence[Dict[str, Any]]) -> List[List[Dict[str, str]]]:
    """Inverse of :func:`parse_sessions`, in MT5's exact wire shape."""
    out: List[List[Dict[str, str]]] = []
    for index in range(7):
        entry = days[index] if index < len(days) else None
        ranges: List[Dict[str, str]] = []
        for session in (entry or {}).get("sessions", []):
            ranges.append(
                {
                    "Open": str(int(session["open_minutes"])),
                    "Close": str(int(session["close_minutes"])),
                }
            )
        out.append(ranges)
    return out


# ---------------------------------------------------------------------------
# Record -> domain
# ---------------------------------------------------------------------------


def record_to_domain(
    record: Dict[str, Any],
    table: Sequence[Field],
    *,
    keep_unmapped: bool = True,
) -> Dict[str, Any]:
    """Convert one MT5 record into a nested domain-shaped dict.

    ``keep_unmapped=True`` retains MT5 fields we have not modelled under
    ``EXTRA_KEY``, and remembers every decimal's wire scale under ``SCALE_KEY``, so a
    decode -> encode round trip is lossless even while the domain model is incomplete.
    Pass ``keep_unmapped=False`` to see exactly what our model can represent.
    """
    out: Dict[str, Any] = {}
    extra: Dict[str, Any] = {}
    scales: Dict[str, int] = {}
    known = {f.mt5 for f in table}

    for field in table:
        if field.mt5 not in record:
            continue
        raw = record[field.mt5]

        observed = wire_scale(raw)
        if observed is not None:
            scales[field.mt5] = observed

        try:
            value = _convert_inbound(raw, field)
        except MT5ConversionError:
            # Never let one bad field abort a whole import; surface it verbatim.
            value = raw

        if field.mt5 in VOLUME_SCALED_FIELDS and isinstance(value, Decimal):
            # Scaled-integer wire fields: prefer the 10^8 Ext sibling when present
            # and non-zero (it carries more precision), else the 10^4 bare field.
            ext_value = None
            ext_raw = record.get(field.mt5 + "Ext")
            if ext_raw is not None:
                try:
                    ext_value = Decimal(str(ext_raw))
                except (InvalidOperation, ValueError, TypeError):
                    ext_value = None
            if ext_value is not None and ext_value != 0:
                value = ext_value / Decimal(10) ** VOLUME_EXT_EXPONENT
            else:
                value = value / Decimal(10) ** VOLUME_WIRE_EXPONENT

        if field.domain:
            if _has(out, field.domain):
                # Two MT5 fields claiming one domain slot (Point vs TickSize). The
                # first mapping in the table wins and the loser is quarantined, so no
                # data is lost and the collision is visible rather than silent.
                extra[field.mt5] = value
            else:
                _assign(out, field.domain, value)
        else:
            extra[field.mt5] = value

    if keep_unmapped:
        for key, value in record.items():
            if key not in known:
                extra[key] = value
        if extra:
            out[EXTRA_KEY] = extra
        if scales:
            out[SCALE_KEY] = scales

    return out


def _convert_inbound(raw: Any, field: Field) -> Any:
    # The inherit sentinel is a string even in numeric fields, and must stay a string.
    if is_inherited(raw):
        return INHERIT
    if field.kind == STR:
        return raw if isinstance(raw, str) else str(raw)
    if field.kind == DEC:
        return _to_decimal(raw, field.mt5)
    if field.kind in (INT, FLAGS):
        return _to_int(raw, field.mt5)
    if field.kind == BOOL01:
        return _to_bool01(raw, field.mt5)
    if field.kind == SESSIONS:
        return parse_sessions(raw, field.mt5)
    if field.kind == STRLIST:
        return list(raw) if isinstance(raw, list) else []
    if field.kind == NESTED:
        sub_table = NESTED_TABLES.get(field.mt5)
        if isinstance(raw, dict):
            # e.g. ConfigGateways.State is a single object, not an array. With no table
            # for it yet, keep it verbatim so the round trip stays exact.
            if sub_table is None:
                return dict(raw)
            return record_to_domain(raw, sub_table)
        if not isinstance(raw, list):
            return []
        if sub_table is None:
            return list(raw)
        return [record_to_domain(r, sub_table) for r in raw if isinstance(r, dict)]
    return raw


def _assign(target: Dict[str, Any], dotted: str, value: Any) -> None:
    parts = dotted.split(".")
    cursor = target
    for part in parts[:-1]:
        cursor = cursor.setdefault(part, {})
    cursor[parts[-1]] = value


# ---------------------------------------------------------------------------
# Domain -> record
# ---------------------------------------------------------------------------


def domain_to_record(
    domain: Dict[str, Any],
    table: Sequence[Field],
    *,
    include_unmapped: bool = True,
) -> Dict[str, Any]:
    """Render a domain dict back into an MT5 record.

    Every scalar becomes a string. Decimals are rendered at the scale observed on
    import when we have one, otherwise at :data:`SCALE`, otherwise
    :data:`DEFAULT_SCALE`.
    """
    out: Dict[str, Any] = {}
    scales: Dict[str, int] = domain.get(SCALE_KEY) or {}
    extra: Dict[str, Any] = domain.get(EXTRA_KEY) or {}
    rendered: set = set()

    for field in table:
        if field.kind == SESSIONS:
            value = _lookup(domain, field.domain) if field.domain else None
            if value is not None:
                out[field.mt5] = render_sessions(value)
                rendered.add(field.mt5)
            continue

        if field.kind == NESTED:
            value = _lookup(domain, field.domain) if field.domain else extra.get(field.mt5)
            sub_table = NESTED_TABLES.get(field.mt5)
            if isinstance(value, dict):
                out[field.mt5] = (
                    domain_to_record(value, sub_table) if sub_table else dict(value)
                )
                rendered.add(field.mt5)
            elif isinstance(value, list):
                out[field.mt5] = [
                    domain_to_record(v, sub_table) if (sub_table and isinstance(v, dict)) else v
                    for v in value
                ]
                rendered.add(field.mt5)
            continue

        if not field.domain:
            continue
        # A field that lost a mapping collision lives in extra, not in the domain path.
        if field.mt5 in extra:
            continue
        if not _has(domain, field.domain):
            continue

        if field.mt5 in VOLUME_SCALED_FIELDS:
            from decimal import ROUND_HALF_UP

            raw_value = _lookup(domain, field.domain)
            dec = None
            if not is_inherited(raw_value):
                try:
                    dec = Decimal(str(raw_value))
                except (InvalidOperation, ValueError, TypeError):
                    dec = None
            if dec is not None:
                bare = (dec * Decimal(10) ** VOLUME_WIRE_EXPONENT).to_integral_value(
                    rounding=ROUND_HALF_UP
                )
                ext = (dec * Decimal(10) ** VOLUME_EXT_EXPONENT).to_integral_value(
                    rounding=ROUND_HALF_UP
                )
                out[field.mt5] = str(int(bare))
                # Derive the Ext sibling from the SAME domain value and mark it
                # rendered, so a quarantined (possibly stale) Ext literal from
                # import can never contradict an edited volume on export.
                ext_key = field.mt5 + "Ext"
                out[ext_key] = str(int(ext))
                rendered.add(ext_key)
                rendered.add(field.mt5)
                continue

        out[field.mt5] = _render_scalar(
            _lookup(domain, field.domain), field, scales.get(field.mt5)
        )
        rendered.add(field.mt5)

    if include_unmapped:
        for key, value in extra.items():
            if key in rendered:
                continue
            out[key] = _render_extra(key, value, scales.get(key))

    return out


def render_decimal(value: Any, field_name: str, scale: Optional[int] = None) -> str:
    """Render a decimal exactly as MT5 would write it for ``field_name``.

    ``scale`` is the number of decimal places observed on import and takes priority;
    it is what makes the round trip byte-exact even for fields whose scale varies
    between records (``AccruedInterest`` uses 2, 5, 8 and 0 places in one export).
    """
    if isinstance(value, str):
        value = _to_decimal(value, field_name)
    if isinstance(value, bool):
        raise MT5ConversionError(f"{field_name}: refusing to export a boolean as a decimal")
    if not isinstance(value, Decimal):
        value = Decimal(str(value))
    if scale is None:
        scale = SCALE.get(field_name, DEFAULT_SCALE)
    return f"{value:.{scale}f}"


def _render_scalar(value: Any, field: Field, scale: Optional[int]) -> Any:
    if is_inherited(value):
        return INHERIT
    if field.kind == DEC:
        return render_decimal(value, field.mt5, scale)
    if field.kind in (INT, FLAGS):
        if isinstance(value, bool):
            raise MT5ConversionError(
                f"{field.mt5}: refusing to export a boolean as an integer; "
                "pass 0/1 explicitly so the intent is unambiguous"
            )
        return str(_to_int(value, field.mt5))
    if field.kind == BOOL01:
        return value if isinstance(value, str) else ("1" if value else "0")
    if field.kind == STRLIST:
        return list(value) if isinstance(value, (list, tuple)) else []
    if value is None:
        return ""
    return value if isinstance(value, str) else str(value)


def _render_extra(key: str, value: Any, scale: Optional[int]) -> Any:
    """Re-render an unmapped field exactly as it arrived."""
    if isinstance(value, str) or isinstance(value, (list, dict)):
        return value
    if isinstance(value, bool):
        return "1" if value else "0"
    if isinstance(value, Decimal):
        places = DEFAULT_SCALE if scale is None else scale
        return f"{value:.{places}f}"
    if isinstance(value, int):
        return str(value)
    return "" if value is None else str(value)


def _lookup(domain: Dict[str, Any], dotted: str) -> Any:
    cursor: Any = domain
    for part in dotted.split("."):
        if not isinstance(cursor, dict) or part not in cursor:
            return None
        cursor = cursor[part]
    return cursor


def _has(domain: Dict[str, Any], dotted: str) -> bool:
    cursor: Any = domain
    for part in dotted.split("."):
        if not isinstance(cursor, dict) or part not in cursor:
            return False
        cursor = cursor[part]
    return True


# ---------------------------------------------------------------------------
# File-level convenience
# ---------------------------------------------------------------------------


def import_section(path: Any, section: str, table: Sequence[Field]) -> List[Dict[str, Any]]:
    """Read an MT5 export file and convert one section into domain dicts."""
    payload = wire.decode_file(path)
    return [record_to_domain(r, table) for r in wire.records(payload, section)]


def import_file(path: Any) -> Dict[str, List[Dict[str, Any]]]:
    """Import every recognised section of an MT5 export into domain dicts."""
    payload = wire.decode_file(path)
    by_section: Dict[str, Tuple[Field, ...]] = {
        "ConfigSymbols": SYMBOL_FIELDS,
        "ConfigGroups": GROUP_FIELDS,
        "ConfigRouting": ROUTING_FIELDS,
        "ConfigGateways": GATEWAY_FIELDS,
        "ConfigFeeders": FEEDER_FIELDS,
        "ConfigHolidays": HOLIDAY_FIELDS,
        "ConfigManagers": MANAGER_FIELDS,
    }
    out: Dict[str, List[Dict[str, Any]]] = {}
    for section, table in by_section.items():
        recs = wire.records(payload, section)
        if recs:
            out[section] = [record_to_domain(r, table) for r in recs]
    return out


def export_section(
    path: Any,
    section: str,
    table: Sequence[Field],
    rows: Iterable[Dict[str, Any]],
    *,
    utf16: bool = True,
) -> None:
    """Write domain dicts to ``path`` as an MT5-importable export for one section.

    Validates against the wire contract first and refuses to write a file that MT5
    Administrator would reject.
    """
    payload = wire.build(section, [domain_to_record(r, table) for r in rows])
    problems = wire.validate(payload)
    if problems:
        raise MT5ConversionError(
            "refusing to write a non-conformant MT5 export: " + "; ".join(problems[:5])
        )
    wire.encode_file(path, payload, utf16=utf16)


__all__ = [
    "DEFAULT_SCALE",
    "EXTRA_KEY",
    "MT5ConversionError",
    "SCALE",
    "SCALE_KEY",
    "domain_to_record",
    "export_section",
    "flags_to_set",
    "import_file",
    "import_section",
    "is_inherited",
    "INHERIT",
    "parse_sessions",
    "record_to_domain",
    "render_decimal",
    "render_sessions",
    "wire_scale",
]