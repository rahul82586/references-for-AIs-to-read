"""
MT5 Administrator wire-format codec.

MetaQuotes' MT5 Administrator exports/imports server configuration as JSON with a
very specific contract. This module reproduces that contract exactly, so that
configuration can be imported from and exported to a real MT5 server without loss.

THE MT5 WIRE CONTRACT, verified against a live server export (14 sections,
362 symbols x 121 fields, 20 groups x 44 fields) rather than assumed from prose:

  1. Envelope        {"Server": [ {"Config<Section>": [ <record>, ... ]} ]}
                     Sections: ConfigGroups, ConfigSymbols, ConfigManagers,
                     ConfigGateways, ConfigFeeders, ConfigRouting, ConfigHolidays,
                     ConfigNetwork, ConfigPlugins, ConfigReports, ConfigFirewall,
                     ConfigSubscriptions, ConfigAutomation, ConfigHistorySync.

  2. EVERY scalar is a JSON string. There are no JSON numbers, no JSON booleans and
                     no nulls anywhere in the format: "50.00", "87", "0", "".

  3. Fixed scale     Decimals carry a fixed number of decimal places that is part of
                     the value ("50.00" not "50", "3.50000000" not "3.5"). The scale
                     is per field AND per record, so round-trip fidelity requires
                     preserving the original literal. See codec.wire_scale.

  4. Lists stay lists Only two shapes appear: arrays of strings (Symbols: ["*"]) and
                     arrays of objects (Commissions, Tiers, Conditions, Dealers).

  5. Sessions        SessionsQuotes / SessionsTrades are a 7-element array indexed
                     Sunday(0) .. Saturday(6). Each element is an array of
                     {"Open": "<minutes>", "Close": "<minutes>"} counted from
                     midnight over a 0..1440 minute day. Empty array == closed.

  6. Bitmasks        Flags fields (TradeFlags, PermissionsFlags, MarginFlags,
                     SwapFlags, REFlags, IEFlags, FillFlags, ExpirFlags, OrderFlags)
                     are decimal-encoded bitmasks as strings, e.g. "87".

  7. Nested paths    Symbol Path uses a backslash separator: "FX\\Forex\\EURUSD".
                     Group names likewise: "real\\real", "managers\\dealers".

Because rules 2 and 3 hold universally, decode/encode here are LOSSLESS BY
CONSTRUCTION: they perform no type coercion at all. Typed access is layered
separately in codec.py, so importing into the domain model can never corrupt an
export.
"""

from __future__ import annotations

import json
import pathlib
from typing import Any, Dict, List, Optional, Tuple, Union

# ---------------------------------------------------------------------------
# Envelope
# ---------------------------------------------------------------------------

#: The single top-level key of every MT5 Administrator config export.
ROOT_KEY = "Server"

#: Section keys, in the order MT5 Administrator presents them.
SECTIONS: Tuple[str, ...] = (
    "ConfigGroups",
    "ConfigSymbols",
    "ConfigManagers",
    "ConfigGateways",
    "ConfigFeeders",
    "ConfigRouting",
    "ConfigHolidays",
    "ConfigNetwork",
    "ConfigPlugins",
    "ConfigReports",
    "ConfigFirewall",
    "ConfigSubscriptions",
    "ConfigAutomation",
    "ConfigHistorySync",
)

#: Weekday ordering used by SessionsQuotes / SessionsTrades. MT5 is SUNDAY-FIRST,
#: which is NOT Python's weekday(). Named explicitly to prevent off-by-one bugs in
#: swap scheduling and session checks.
WEEKDAY_SUNDAY_FIRST: Tuple[str, ...] = (
    "Sunday",
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday",
)

PathLike = Union[str, "pathlib.Path"]


class MT5FormatError(ValueError):
    """Raised when a payload does not conform to the MT5 wire contract."""


# ---------------------------------------------------------------------------
# Decode / encode - lossless, no type coercion
# ---------------------------------------------------------------------------


def decode_text(text: str) -> Dict[str, Any]:
    """Parse an MT5 config export from its JSON text."""
    return json.loads(text)


def decode_bytes(raw: bytes) -> Dict[str, Any]:
    """Parse an MT5 config export from raw bytes.

    MT5 Administrator writes UTF-16LE with a BOM. Detect and normalise it here so
    callers never have to think about encoding, and so a file re-saved as UTF-8 by a
    diff tool or an editor still loads.
    """
    if raw[:2] in (b"\xff\xfe", b"\xfe\xff"):
        text = raw.decode("utf-16", errors="replace")
    elif raw[:1] == b"\x00" or (len(raw) > 1 and raw[1:2] == b"\x00"):
        # BOM-less UTF-16LE, which is what a redirected Windows write produces.
        text = raw.decode("utf-16-le", errors="replace")
    else:
        text = raw.decode("utf-8-sig", errors="replace")
    return decode_text(text.lstrip("\ufeff").strip())


def decode_file(path: PathLike) -> Dict[str, Any]:
    """Read and parse an MT5 config export from ``path``."""
    return decode_bytes(pathlib.Path(path).read_bytes())


def encode_text(payload: Dict[str, Any], *, indent: Optional[int] = 1) -> str:
    """Serialise a config payload back to MT5's JSON text form.

    ``indent=1`` matches the Administrator's own export layout.
    """
    return json.dumps(payload, indent=indent, ensure_ascii=False)


def encode_bytes(payload: Dict[str, Any], *, utf16: bool = True) -> bytes:
    """Serialise to bytes, optionally in MT5 Administrator's UTF-16LE + BOM form.

    Use ``utf16=True`` when writing a file MT5 Administrator must read back.
    Use ``utf16=False`` for diffs, version control and human inspection.
    """
    text = encode_text(payload)
    if utf16:
        return b"\xff\xfe" + text.encode("utf-16-le")
    return text.encode("utf-8")


def encode_file(path: PathLike, payload: Dict[str, Any], *, utf16: bool = True) -> None:
    """Write ``payload`` to ``path`` in MT5 Administrator's own encoding."""
    pathlib.Path(path).write_bytes(encode_bytes(payload, utf16=utf16))


# ---------------------------------------------------------------------------
# Section access
# ---------------------------------------------------------------------------


def sections(payload: Dict[str, Any]) -> List[str]:
    """Return the config section keys present in ``payload``."""
    if ROOT_KEY not in payload:
        raise MT5FormatError(f"missing '{ROOT_KEY}' envelope key")
    found: List[str] = []
    for server in payload[ROOT_KEY]:
        found.extend(k for k in server.keys() if k.startswith("Config"))
    return found


def records(payload: Dict[str, Any], section: str) -> List[Dict[str, Any]]:
    """Return the record list for ``section``, flattening across server entries.

    A real export has exactly one element under ``Server``, but the format allows
    several, so we concatenate rather than silently dropping data.
    """
    if ROOT_KEY not in payload:
        raise MT5FormatError(f"missing '{ROOT_KEY}' envelope key")
    out: List[Dict[str, Any]] = []
    for server in payload[ROOT_KEY]:
        out.extend(server.get(section, []))
    return out


def build(section: str, recs: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Wrap ``recs`` in a minimal valid MT5 export envelope for ``section``."""
    if section not in SECTIONS:
        raise MT5FormatError(
            f"unknown section '{section}'; expected one of {', '.join(SECTIONS)}"
        )
    return {ROOT_KEY: [{section: recs}]}


# ---------------------------------------------------------------------------
# Contract validation
# ---------------------------------------------------------------------------


def validate(payload: Dict[str, Any]) -> List[str]:
    """Check a payload against the MT5 wire contract.

    Returns human-readable violations; empty means conformant. Deliberately strict:
    a file that violates rule 2 will not import into MT5 Administrator, so it is
    better to fail here than in production.
    """
    if ROOT_KEY not in payload:
        return [f"missing '{ROOT_KEY}' envelope key"]

    problems: List[str] = []
    for si, server in enumerate(payload[ROOT_KEY]):
        if not isinstance(server, dict):
            problems.append(f"Server[{si}] is not an object")
            continue
        for section, recs in server.items():
            if not section.startswith("Config"):
                problems.append(f"Server[{si}]: unexpected key '{section}'")
            if not isinstance(recs, list):
                problems.append(f"Server[{si}].{section} is not an array")
                continue
            for ri, rec in enumerate(recs):
                where = f"Server[{si}].{section}[{ri}]"
                if not isinstance(rec, dict):
                    problems.append(f"{where} is not an object")
                    continue
                problems.extend(_validate_record(rec, where))
    return problems


def _validate_record(rec: Dict[str, Any], where: str) -> List[str]:
    problems: List[str] = []
    for key, value in rec.items():
        path = f"{where}.{key}"
        if isinstance(value, str):
            continue
        if isinstance(value, dict):
            problems.extend(_validate_record(value, path))
        elif isinstance(value, list):
            problems.extend(_validate_list(value, path))
        elif isinstance(value, bool):
            problems.append(f"{path}: booleans are not permitted, use '0'/'1'")
        elif isinstance(value, (int, float)):
            problems.append(
                f"{path}: numbers are not permitted, MT5 encodes every scalar as a string"
            )
        elif value is None:
            problems.append(f"{path}: null is not permitted, use the empty string")
        else:
            problems.append(f"{path}: unsupported type {type(value).__name__}")
    return problems


def _validate_list(items: List[Any], path: str) -> List[str]:
    problems: List[str] = []
    for i, item in enumerate(items):
        if isinstance(item, str):
            continue
        if isinstance(item, dict):
            problems.extend(_validate_record(item, f"{path}[{i}]"))
        elif isinstance(item, list):
            # SessionsQuotes / SessionsTrades are lists of lists of objects.
            problems.extend(_validate_list(item, f"{path}[{i}]"))
        else:
            problems.append(f"{path}[{i}]: expected object, array or string")
    return problems

