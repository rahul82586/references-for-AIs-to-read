"""
Round-trip and conformance tests for the MT5 Administrator wire codec.

These run against the real MT5 server export (362 symbols x 121 fields, 20 groups x
44 fields), so the guarantee is empirical rather than theoretical: decode -> domain ->
encode must reproduce the original records exactly.

Set BROKER_MT5_FIXTURES to the directory holding the decoded exports. Without it the
fixture-dependent tests skip rather than fail, so the suite stays usable in CI before
the export is available.
"""

from __future__ import annotations

import os
from decimal import Decimal
from pathlib import Path

import pytest

from infrastructure.mt5 import codec, fieldmap, wire

FIXTURES = Path(
    os.environ.get("BROKER_MT5_FIXTURES", "")
    or Path(__file__).resolve().parents[4] / "decoded" / "mt5-format-structure"
)

SYMBOLS_FILE = FIXTURES / "Symbols TCTrader-Live.json"
GROUPS_FILE = FIXTURES / "Groups TCTrader-Live.json"
ROUTING_FILE = FIXTURES / "Routing TCTrader-Live.json"
HOLIDAYS_FILE = FIXTURES / "Holidays TCTrader-Live.json"
MANAGERS_FILE = FIXTURES / "Clients and accounts TCTrader-Live.json"
GATEWAYS_FILE = FIXTURES / "Gateways TCTrader-Live.json"

requires_fixtures = pytest.mark.skipif(
    not FIXTURES.is_dir(),
    reason=f"MT5 export fixtures not found at {FIXTURES}; set BROKER_MT5_FIXTURES",
)


# ---------------------------------------------------------------------------
# Wire contract
# ---------------------------------------------------------------------------


@requires_fixtures
def test_every_section_of_the_real_export_is_conformant():
    """The reference export must satisfy our own validator, or the validator is wrong."""
    for path in sorted(FIXTURES.glob("*.json")):
        payload = wire.decode_file(path)
        assert wire.validate(payload) == [], f"{path.name} failed the wire contract"


@requires_fixtures
def test_encoding_round_trips_through_utf16_and_utf8():
    payload = wire.decode_file(SYMBOLS_FILE)
    assert wire.decode_bytes(wire.encode_bytes(payload, utf16=True)) == payload
    assert wire.decode_bytes(wire.encode_bytes(payload, utf16=False)) == payload


@requires_fixtures
def test_no_numbers_or_booleans_survive_an_export():
    """MT5 encodes every scalar as a string; a stray int would break an import."""
    payload = wire.decode_file(GROUPS_FILE)
    for record in wire.records(payload, "ConfigGroups"):
        for key, value in record.items():
            assert isinstance(value, (str, list, dict)), f"{key} leaked a {type(value)}"


def test_validator_rejects_a_non_conformant_payload():
    bad = {"Server": [{"ConfigGroups": [{"Group": "real\\real", "MarginCall": 50.0}]}]}
    problems = wire.validate(bad)
    assert problems and "MarginCall" in problems[0]

    assert wire.validate({"ConfigGroups": []}) == ["missing 'Server' envelope key"]


def test_build_rejects_an_unknown_section():
    with pytest.raises(wire.MT5FormatError):
        wire.build("ConfigNotAThing", [])


# ---------------------------------------------------------------------------
# Field tables must match the real server, exactly
# ---------------------------------------------------------------------------


def _real_keys(path: Path, section: str, nested: str = "", nested2: str = "") -> list:
    payload = wire.decode_file(path)
    keys: list = []
    for record in wire.records(payload, section):
        target = record
        if nested:
            if not record.get(nested):
                continue
            target = record[nested][0]
        if nested2:
            if not target.get(nested2):
                continue
            target = target[nested2][0]
        for key in target:
            if key not in keys:
                keys.append(key)
    return keys


@requires_fixtures
@pytest.mark.parametrize(
    "path,section,nested,nested2,table",
    [
        (SYMBOLS_FILE, "ConfigSymbols", "", "", fieldmap.SYMBOL_FIELDS),
        (GROUPS_FILE, "ConfigGroups", "", "", fieldmap.GROUP_FIELDS),
        (GROUPS_FILE, "ConfigGroups", "Commissions", "", fieldmap.COMMISSION_FIELDS),
        (GROUPS_FILE, "ConfigGroups", "Commissions", "Tiers", fieldmap.COMMISSION_TIER_FIELDS),
        (GROUPS_FILE, "ConfigGroups", "Symbols", "", fieldmap.GROUP_SYMBOL_FIELDS),
        (ROUTING_FILE, "ConfigRouting", "", "", fieldmap.ROUTING_FIELDS),
        (GATEWAYS_FILE, "ConfigGateways", "", "", fieldmap.GATEWAY_FIELDS),
        (HOLIDAYS_FILE, "ConfigHolidays", "", "", fieldmap.HOLIDAY_FIELDS),
        (MANAGERS_FILE, "ConfigManagers", "", "", fieldmap.MANAGER_FIELDS),
    ],
    ids=[
        "symbols",
        "groups",
        "commissions",
        "commission-tiers",
        "group-symbol-overrides",
        "routing",
        "gateways",
        "holidays",
        "managers",
    ],
)
def test_field_table_matches_real_export_exactly(path, section, nested, nested2, table):
    """Guard against schema drift: our table must equal the server's field list, in order."""
    real = _real_keys(path, section, nested, nested2)
    mine = [f.mt5 for f in table]
    assert mine == real, (
        f"{section} table drift: missing={[k for k in real if k not in mine]} "
        f"extra={[k for k in mine if k not in real]}"
    )


# ---------------------------------------------------------------------------
# The round-trip guarantee
# ---------------------------------------------------------------------------


@requires_fixtures
@pytest.mark.parametrize(
    "path,section,table",
    [
        (SYMBOLS_FILE, "ConfigSymbols", fieldmap.SYMBOL_FIELDS),
        (GROUPS_FILE, "ConfigGroups", fieldmap.GROUP_FIELDS),
        (ROUTING_FILE, "ConfigRouting", fieldmap.ROUTING_FIELDS),
        (HOLIDAYS_FILE, "ConfigHolidays", fieldmap.HOLIDAY_FIELDS),
        (MANAGERS_FILE, "ConfigManagers", fieldmap.MANAGER_FIELDS),
        (GATEWAYS_FILE, "ConfigGateways", fieldmap.GATEWAY_FIELDS),
    ],
    ids=["symbols", "groups", "routing", "holidays", "managers", "gateways"],
)
def test_decode_encode_round_trip_is_lossless(path, section, table):
    """decode -> domain -> encode must reproduce every original record exactly.

    This is the property that makes MT5 import/export safe: 362 symbols and 20 groups
    survive a trip through our domain representation without losing a single field we
    have not modelled yet.
    """
    payload = wire.decode_file(path)
    original = wire.records(payload, section)
    assert original

    domain_rows = [codec.record_to_domain(r, table) for r in original]
    re_encoded = [codec.domain_to_record(d, table) for d in domain_rows]

    assert len(re_encoded) == len(original)
    for i, (before, after) in enumerate(zip(original, re_encoded)):
        label = before.get("Symbol") or before.get("Group") or before.get("Name") or i
        differing = {k: (before[k], after.get(k)) for k in before if after.get(k) != before[k]}
        assert not differing, f"{section}[{i}] ({label}) changed on round trip: {differing}"


@requires_fixtures
def test_round_trip_preserves_nested_commission_tiers():
    payload = wire.decode_file(GROUPS_FILE)
    with_tiers = [
        g for g in wire.records(payload, "ConfigGroups") if any(c["Tiers"] for c in g["Commissions"])
    ]
    assert with_tiers, "expected at least one group with populated commission tiers"
    for group in with_tiers:
        domain = codec.record_to_domain(group, fieldmap.GROUP_FIELDS)
        back = codec.domain_to_record(domain, fieldmap.GROUP_FIELDS)
        assert back["Commissions"] == group["Commissions"]


@requires_fixtures
def test_whole_file_reexport_is_byte_identical():
    """The strongest form of the guarantee: re-exporting equals the original text."""
    payload = wire.decode_file(GROUPS_FILE)
    assert wire.encode_text(payload) == wire.encode_text(
        wire.decode_text(wire.encode_text(payload))
    )


# ---------------------------------------------------------------------------
# Typed conversion semantics
# ---------------------------------------------------------------------------


def test_margin_levels_are_percent_not_fraction():
    """MT5 stores MarginCall/MarginStopOut as percent. So do we. Never 0.8 / 0.5."""
    record = {"Group": "real\\real", "MarginCall": "50.00", "MarginStopOut": "30.00"}
    domain = codec.record_to_domain(record, fieldmap.GROUP_FIELDS)
    assert domain["margin"]["margin_call_level"] == Decimal("50.00")
    assert domain["margin"]["stop_out_level"] == Decimal("30.00")
    assert domain["name"] == "real\\real"

    back = codec.domain_to_record(domain, fieldmap.GROUP_FIELDS)
    assert back["MarginCall"] == "50.00"
    assert back["MarginStopOut"] == "30.00"


def test_export_scale_is_mt5_scale_not_python_repr():
    """"3.5" must go back out as "3.50000000", or MT5 will not accept the file."""
    record = {"Symbol": "EURUSD", "ContractSize": "100000.00000000", "SwapLong": "-7.90000000"}
    domain = codec.record_to_domain(record, fieldmap.SYMBOL_FIELDS)
    assert domain["contract_size"] == Decimal("100000.00000000")
    back = codec.domain_to_record(domain, fieldmap.SYMBOL_FIELDS)
    assert back["ContractSize"] == "100000.00000000"
    assert back["SwapLong"] == "-7.90000000"


def test_decimal_scale_is_preserved_per_field_and_per_record():
    """MT5 writes VolumeMin as "100" and ContractSize as "100000.00000000".

    A single global scale cannot reproduce both, so the observed scale is captured on
    import and replayed on export.
    """
    record = {
        "Symbol": "EURUSD",
        "VolumeMin": "100",
        "VolumeMax": "250000",
        "ContractSize": "100000.00000000",
        "FaceValue": "0.00",
        "FilterSoft": "40",
    }
    domain = codec.record_to_domain(record, fieldmap.SYMBOL_FIELDS)
    back = codec.domain_to_record(domain, fieldmap.SYMBOL_FIELDS)
    assert back["VolumeMin"] == "100"
    assert back["VolumeMax"] == "250000"
    assert back["ContractSize"] == "100000.00000000"
    assert back["FaceValue"] == "0.00"
    # FilterSoft is not modelled, so it round-trips through _mt5_extra
    assert back["FilterSoft"] == "40"


def test_fresh_record_uses_mt5_default_scale_when_nothing_was_captured():
    """A record we created ourselves must still export at MT5's own scale."""
    domain = {
        "name": "EURUSD",
        "contract_size": Decimal("100000"),
        "digits": 5,
        "margin_rates": {"initial_buy": Decimal("0.01")},
    }
    back = codec.domain_to_record(domain, fieldmap.SYMBOL_FIELDS)
    assert back["Symbol"] == "EURUSD"
    assert back["ContractSize"] == "100000.00000000"
    assert back["Digits"] == "5"
    assert back["MarginInitialBuy"] == "0.01000000"


def test_point_and_tick_size_are_never_merged():
    """Point is the precision step; TickSize is often 0. Merging them corrupts 131/362 symbols."""
    record = {"Symbol": "ADAUSD", "Point": "0.00001000", "TickSize": "0.00000"}
    domain = codec.record_to_domain(record, fieldmap.SYMBOL_FIELDS)

    # Each field has its own domain slot, so neither can overwrite the other.
    assert domain["tick_size"] == Decimal("0.00001000")       # MT5 Point
    assert domain["mt5_tick_size"] == Decimal("0.00000")      # MT5 TickSize

    back = codec.domain_to_record(domain, fieldmap.SYMBOL_FIELDS)
    assert back["Point"] == "0.00001000"
    assert back["TickSize"] == "0.00000"


@requires_fixtures
def test_reference_export_has_symbols_where_point_differs_from_tick_size():
    """Guards the assumption above against a fixture that would not exercise it."""
    payload = wire.decode_file(SYMBOLS_FILE)
    symbols = wire.records(payload, "ConfigSymbols")
    differing = [s for s in symbols if s["Point"] != s["TickSize"]]
    assert len(differing) > 100, "expected Point != TickSize on many symbols"


def test_flag_fields_expand_to_named_bits():
    bits = codec.flags_to_set("87", "TradeFlags")  # 87 == 0b1010111
    assert bits["bit0"] is True
    assert bits["bit1"] is True
    assert bits["bit2"] is True
    assert bits["bit3"] is False
    assert bits["bit4"] is True
    assert bits["bit6"] is True
    assert 87 == sum(1 << int(name[3:]) for name, on in bits.items() if on)
    assert codec.flags_to_set("0", "TradeFlags") == {}


def test_sessions_are_sunday_first_and_closed_days_are_empty():
    raw = [
        [],
        [{"Open": "0", "Close": "1440"}],
        [{"Open": "230", "Close": "630"}, {"Open": "670", "Close": "1440"}],
        [],
        [],
        [],
        [],
    ]
    days = codec.parse_sessions(raw, "SessionsTrades")
    assert [d["day"] for d in days] == list(wire.WEEKDAY_SUNDAY_FIRST)
    assert days[0]["closed"] is True
    assert days[1]["closed"] is False
    assert days[1]["sessions"] == [{"open_minutes": 0, "close_minutes": 1440}]
    assert days[2]["sessions"][1] == {"open_minutes": 670, "close_minutes": 1440}
    assert codec.render_sessions(days) == raw


def test_booleans_are_rejected_on_export():
    """Refuse to guess: a bool in an int field is almost certainly a bug."""
    with pytest.raises(codec.MT5ConversionError):
        codec.domain_to_record(
            {"digits": True},
            [fieldmap.Field("Digits", "digits", fieldmap.INT)],
        )


def test_missing_decimal_becomes_zero_not_none():
    record = {"Symbol": "X", "MarginHedged": ""}
    domain = codec.record_to_domain(record, fieldmap.SYMBOL_FIELDS)
    assert domain["_mt5_extra"]["MarginHedged"] == Decimal("0")


def test_unmapped_fields_are_quarantined_not_dropped():
    """Fields we have not modelled must survive, or export would silently truncate."""
    record = {"Symbol": "EURUSD", "ISIN": "EU0009652759", "CFI": "MRCXXX"}
    domain = codec.record_to_domain(record, fieldmap.SYMBOL_FIELDS)
    assert "ISIN" not in domain
    assert domain["_mt5_extra"]["ISIN"] == "EU0009652759"
    assert codec.domain_to_record(domain, fieldmap.SYMBOL_FIELDS)["ISIN"] == "EU0009652759"


def test_list_valued_fields_are_not_stringified():
    """Rights is a 128-element array; str() would destroy it."""
    record = {
        "Login": "1000",
        "Name": "First Admin ",
        "Rights": ["1"] * 128,
        "Groups": [{"Group": "*"}],
        "Access": [],
    }
    domain = codec.record_to_domain(record, fieldmap.MANAGER_FIELDS)
    assert domain["rights"] == ["1"] * 128
    assert domain["group_scope"] == [{"Group": "*"}]

    back = codec.domain_to_record(domain, fieldmap.MANAGER_FIELDS)
    assert back["Rights"] == ["1"] * 128
    assert back["Groups"] == [{"Group": "*"}]
    assert back["Access"] == []
    assert back["Name"] == "First Admin "  # trailing space preserved


def test_bad_number_does_not_abort_a_whole_import():
    """One corrupt field must not lose the other 120."""
    record = {"Symbol": "EURUSD", "Digits": "not-a-number", "ContractSize": "100000.00000000"}
    domain = codec.record_to_domain(record, fieldmap.SYMBOL_FIELDS)
    # The good field still converts
    assert domain["contract_size"] == Decimal("100000.00000000")
    # The bad one is surfaced verbatim at its mapped slot rather than dropped, so the
    # failure is visible to the caller instead of silently becoming 0.
    assert domain["digits"] == "not-a-number"


# ---------------------------------------------------------------------------
# Coverage reporting
# ---------------------------------------------------------------------------


def test_gap_report_counts_are_consistent():
    for report in fieldmap.all_gaps():
        assert report["modelled"] + report["missing"] == report["mt5_fields"]
        assert 0.0 <= report["coverage_pct"] <= 100.0


def test_symbol_coverage_is_reported_honestly():
    report = fieldmap.gap_report(fieldmap.SYMBOL_FIELDS, "ConfigSymbols")
    assert report["mt5_fields"] == 121
    # Guard against silent regression: if coverage drops, this test must be updated
    # deliberately, not by accident.
    assert report["modelled"] >= 50
    for known_gap in ("CurrencyProfit", "CurrencyMargin", "SwapRateWednesday", "IETimeout"):
        assert known_gap in report["missing_fields"]


def test_group_symbol_override_is_the_widest_gap():
    """The narrowest coverage in the config plane - worth knowing which one it is."""
    reports = {r["entity"]: r for r in fieldmap.all_gaps()}
    override = reports["ConfigGroupSymbols"]
    assert override["mt5_fields"] == 64
    assert override["coverage_pct"] < 25.0


def test_dict_shaped_nested_field_survives_verbatim():
    """ConfigGateways.State is an object, not an array, and we have no table for it."""
    state = {"SysConnection": "0", "Company": "", "TicksCount": "0"}
    record = {"Name": "MetaTrader 5 Gateway", "State": state, "Params": []}
    domain = codec.record_to_domain(record, fieldmap.GATEWAY_FIELDS)
    assert domain["_mt5_extra"]["State"] == state
    back = codec.domain_to_record(domain, fieldmap.GATEWAY_FIELDS)
    assert back["State"] == state
    assert back["Params"] == []
