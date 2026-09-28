"""M6: MT5's volume fields are scaled integers (10^4 bare, 10^8 Ext), not decimals.

Measured on the reference export: Ext == bare x 10^4 for all 362 symbols x 4
fields, zero violations. EURUSD carries VolumeMin="100" / Ext="1000000" — a
0.01-lot minimum. Before this fix the codec read them as plain decimals:

  * imported EURUSD enforced a 100-LOT minimum (10,000x too large), invisible
    to the round-trip proof because the same wrong literal re-exported
    byte-identically;
  * YAML-seeded 0.01 rendered "0" into the column (scale-0 fallback) and read
    back as 0 — the M4 debt-3 symptom: limits not enforced from the database.
"""
from decimal import Decimal

import pytest

from infrastructure.mt5 import fieldmap
from infrastructure.mt5.codec import domain_to_record, record_to_domain


def _wire(volume_min="100", volume_min_ext="1000000", **over):
    rec = {"Symbol": "TEST", "VolumeMin": volume_min, "VolumeMinExt": volume_min_ext}
    rec.update(over)
    return rec


def test_import_prefers_the_ext_sibling():
    dom = record_to_domain(_wire(), fieldmap.SYMBOL_FIELDS)
    assert dom["volume_min"] == Decimal("0.01")


def test_import_falls_back_to_bare_when_ext_missing_or_zero():
    dom = record_to_domain(_wire(volume_min_ext=None), fieldmap.SYMBOL_FIELDS)
    assert dom["volume_min"] == Decimal("0.01")
    dom = record_to_domain(_wire(volume_min="250", volume_min_ext="0"), fieldmap.SYMBOL_FIELDS)
    assert dom["volume_min"] == Decimal("0.025")


def test_export_renders_both_literals_from_the_domain_value():
    dom = {"name": "TEST", "volume_min": Decimal("0.01")}
    rec = domain_to_record(dom, fieldmap.SYMBOL_FIELDS)
    assert rec["VolumeMin"] == "100"
    assert rec["VolumeMinExt"] == "1000000"


def test_export_never_leaks_a_stale_ext_literal():
    """An edited volume must not export a contradictory quarantined pair."""
    dom = {
        "name": "TEST",
        "volume_min": Decimal("0.02"),  # admin doubled the minimum
        "_mt5_extra": {"VolumeMinExt": "1000000"},  # stale literal from import
    }
    rec = domain_to_record(dom, fieldmap.SYMBOL_FIELDS)
    assert rec["VolumeMin"] == "200"
    assert rec["VolumeMinExt"] == "2000000"


def test_yaml_symbol_survives_the_column_round_trip():
    """The M4 debt-3 repro, end to end through the mappers (no DB needed)."""
    from infrastructure.config.loader import parse_symbol
    from infrastructure.persistence.config_mappers import (
        db_to_symbol,
        symbol_mt5_record,
        symbol_to_db,
    )

    raw = {
        "name": "EURUSD", "digits": 5, "tick_size": "0.00001", "contract_size": 100000,
        "volume_min": "0.01", "volume_max": 100, "volume_step": "0.01",
        "base_currency": "EUR", "quote_currency": "USD",
    }
    sym = parse_symbol(raw, "test")
    model = symbol_to_db(sym)
    assert Decimal(str(model.volume_min)) == Decimal("100")      # wire int in the column
    assert Decimal(str(model.volume_step)) == Decimal("100")
    back = db_to_symbol(model)
    assert back.volume_min == Decimal("0.01")                    # true lots in the domain
    assert back.volume_step == Decimal("0.01")
    assert back.volume_max == Decimal("100")
    rec = symbol_mt5_record(model)
    assert rec["VolumeMin"] == "100" and rec["VolumeMinExt"] == "1000000"
    assert rec["VolumeStep"] == "100" and rec["VolumeStepExt"] == "1000000"
    assert rec["VolumeMax"] == "1000000" and rec["VolumeMaxExt"] == "10000000000"


FIXTURES = __import__("os").environ.get("BROKER_MT5_FIXTURES", "")
requires_fixtures = pytest.mark.skipif(
    not FIXTURES or not __import__("os").path.isdir(FIXTURES),
    reason="MT5 export fixtures not found; set BROKER_MT5_FIXTURES",
)


@requires_fixtures
def test_real_eurusd_export_reads_as_hundredths_of_a_lot():
    import os

    from infrastructure.mt5 import wire

    payload = wire.decode_file(os.path.join(FIXTURES, "Symbols TCTrader-Live.json"))
    recs = wire.records(payload, "ConfigSymbols")
    eur = next(r for r in recs if r.get("Symbol") == "EURUSD")
    dom = record_to_domain(eur, fieldmap.SYMBOL_FIELDS)
    assert dom["volume_min"] == Decimal("0.01")
    assert dom["volume_step"] == Decimal("0.01")
    assert dom["volume_max"] == Decimal("10")  # 100000 / 10^4 on this server


@requires_fixtures
def test_ext_equals_bare_times_10_4_across_the_whole_export():
    """The invariant the conversion rests on, re-verified at test time."""
    import os

    from infrastructure.mt5 import wire

    payload = wire.decode_file(os.path.join(FIXTURES, "Symbols TCTrader-Live.json"))
    for r in wire.records(payload, "ConfigSymbols"):
        for base in ("VolumeMin", "VolumeMax", "VolumeStep", "VolumeLimit"):
            bare, ext = r.get(base), r.get(base + "Ext")
            if bare is None or ext is None:
                continue
            assert Decimal(bare) * Decimal(10000) == Decimal(ext), (r.get("Symbol"), base)
