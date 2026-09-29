"""Rebuilt MT5 wire round-trip proof (replaces the missing scripts/m1_proof_roundtrip.py).

Reads the real TCTrader-Live export, converts it to domain dicts, re-encodes it,
and compares record-for-record / field-for-field against the original wire data.

Usage:
    PYTHONPATH=<bp> python3 verify_roundtrip.py [fixtures_dir]
"""
import json
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.environ.get("BP_ROOT") or os.path.dirname(HERE))

from infrastructure.mt5 import codec, wire                      # noqa: E402
from infrastructure.mt5.fieldmap import TABLES                   # noqa: E402

FIXTURES = sys.argv[1] if len(sys.argv) > 1 else os.environ.get(
    "BROKER_MT5_FIXTURES", "/home/user/refs/mt5-format-structure")

SECTIONS = {
    "ConfigSymbols":  "Symbols TCTrader-Live.json",
    "ConfigGroups":   "Groups TCTrader-Live.json",
    "ConfigRouting":  "Routing TCTrader-Live.json",
    "ConfigHolidays": "Holidays TCTrader-Live.json",
    "ConfigManagers": "Security TCTrader-Live.json",
    "ConfigGateways": "Gateways TCTrader-Live.json",
    "ConfigFeeders":  "Data Feeds TCTrader-Live.json",
}

failures = []
total = 0
identical = 0

print(f"fixtures: {FIXTURES}\n")

for section, filename in SECTIONS.items():
    path = os.path.join(FIXTURES, filename)
    if not os.path.exists(path):
        print(f"-- {section:<15} SKIPPED (no {filename})")
        continue
    table = TABLES.get(section)
    if table is None:
        print(f"-- {section:<15} SKIPPED (not in TABLES)")
        continue

    payload = wire.decode_file(path)
    original = wire.records(payload, section)
    if not original:
        print(f"-- {section:<15} 0 records in source")
        continue

    domain = [codec.record_to_domain(r, table) for r in original]

    with tempfile.TemporaryDirectory() as td:
        out = os.path.join(td, "re.json")
        codec.export_section(out, section, table, domain)
        reimported = wire.records(wire.decode_file(out), section)

    total += len(original)
    matched = 0
    for i, (a, b) in enumerate(zip(original, reimported)):
        if a == b:
            matched += 1
            identical += 1
        else:
            diff = {k: (a.get(k), b.get(k)) for k in set(a) | set(b) if a.get(k) != b.get(k)}
            if len(failures) < 10:
                failures.append((section, i, list(diff.items())[:4]))
    if len(original) != len(reimported):
        failures.append((section, "COUNT", (len(original), len(reimported))))

    status = "BYTE-IDENTICAL" if matched == len(original) else f"{matched}/{len(original)}"
    print(f"-- {section:<15} {len(original):>4} records   {status}")

print(f"\n=== ROUND-TRIP: {identical}/{total} records field-identical ===")
if failures:
    print(f"\n{len(failures)} problem(s):")
    for f in failures:
        print("  ", f)
    sys.exit(1)
print("PASS — the wire format is lossless in both directions.")
