#!/usr/bin/env bash
# =============================================================================
# M0 - make the broker platform importable, from a pristine checkout.
#
# Idempotent-ish: it starts from the pristine reference clone every time, so it is
# safe to re-run. The result is a tree that imports, collects tests, and carries the
# MT5 wire codec.
#
#   ./scripts/m0_run_all.sh [target_dir]
#
# Default target: work/bp
# =============================================================================
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PRISTINE="$HERE/refs/qwencode/broker-platform"
TARGET="${1:-$HERE/work/bp}"

if [[ ! -d "$PRISTINE" ]]; then
  echo "pristine source not found: $PRISTINE" >&2
  exit 1
fi

echo "=== M0+M1: rebuilding $TARGET from pristine ==="
rm -rf "$TARGET"
mkdir -p "$(dirname "$TARGET")"
cp -r "$PRISTINE" "$TARGET"

echo
echo "--- baseline: this should FAIL ---"
cd "$TARGET"
if PYTHONPATH="$TARGET" python3 -c "import api.main" 2>/dev/null; then
  echo "unexpected: pristine tree already imports" >&2
else
  echo "confirmed broken: $(PYTHONPATH="$TARGET" python3 -c 'import api.main' 2>&1 | tail -1)"
fi

echo
echo "--- 1/24 missing imports + merged repository ports ---"
python3 "$HERE/scripts/m0_fix_imports.py" "$TARGET"

echo
echo "--- 2/24 duplicate DB models, domain events, group repository, DI ---"
python3 "$HERE/scripts/m0_fix_models_events.py" "$TARGET"

echo
echo "--- 3/24 restore handler factories lost to duplicate removal ---"
python3 "$HERE/scripts/m0_restore_di.py" "$TARGET"

echo
echo "--- 4/24 interface segregation on the merged ports ---"
python3 "$HERE/scripts/m0_segregate_ports.py" "$TARGET"

echo
echo "--- 5/24 module-level ordering in di_providers ---"
python3 "$HERE/scripts/m0_fix_di_order.py" "$TARGET"

echo
echo "--- MT5 wire codec ---"
mkdir -p "$TARGET/infrastructure/mt5" "$TARGET/tests/unit/infrastructure/mt5"
for f in __init__ wire fieldmap codec enums; do
  cp "$HERE/scripts/mt5pkg/$f.py" "$TARGET/infrastructure/mt5/$f.py"
done
cp "$HERE/scripts/mt5pkg/test_wire_codec.py" "$TARGET/tests/unit/infrastructure/mt5/"

echo
echo "--- 6/24 DI factories: module-scope chat snippets ---"
python3 "$HERE/scripts/m0_fix_di_factories.py" "$TARGET"

echo
echo "--- 7/21 M1: MT5-accurate enums + session value objects ---"
python3 "$HERE/scripts/m1_fix_enums.py" "$TARGET"

echo
echo "--- 8/21 M1: one schema for the configuration plane ---"
python3 "$HERE/scripts/m1_one_schema.py" "$TARGET"

echo
echo "--- 9/21 M1: single DeclarativeBase + generated Alembic revision ---"
python3 "$HERE/scripts/m1_one_base.py" "$TARGET"
python3 "$HERE/scripts/m1_generate_migration.py" "$TARGET" "$HERE/scripts/m1pkg/alembic_001.py" >/dev/null
cp "$HERE/scripts/m1pkg/alembic_001.py" "$TARGET/alembic/versions/001_initial_schema.py"
echo "  ok  alembic/versions/001_initial_schema.py: regenerated from Base.metadata"

echo
echo "--- 10/21 M1: margin level is PERCENT everywhere ---"
python3 "$HERE/scripts/m1_margin_percent.py" "$TARGET"

echo
echo "--- 11/21 M1: integration tests onto percent + M1 acceptance tests ---"
python3 "$HERE/scripts/m1_fix_integration_tests.py" "$TARGET"
mkdir -p "$TARGET/tests/unit/persistence"
cp "$HERE/scripts/m1pkg/test_m1_schema_and_units.py" "$TARGET/tests/unit/persistence/"
cp "$HERE/scripts/m2pkg/test_m2_config_plane.py" "$TARGET/tests/unit/persistence/"

echo
echo "--- 12/21 M1: liquidation fixture arithmetic + mapper defects ---"
python3 "$HERE/scripts/m1_fix_liquidation_thresholds.py" "$TARGET"
python3 "$HERE/scripts/m1_fix_liquidation_and_mappers.py" "$TARGET"

echo
echo "--- 13/21 M1: Symbol gains a distinct MT5 TickSize ---"
python3 "$HERE/scripts/m1_symbol_point.py" "$TARGET"

echo
echo "--- 14/21 M2: Group gains currency_digits ---"
python3 "$HERE/scripts/m2pkg/group_currency_digits.py" "$TARGET"

echo
echo "--- 15/21 M2: config loader, seeder, manager/client persistence ---"
python3 "$HERE/scripts/m2_wire_persistence.py" "$TARGET"

echo
echo "--- 16/21 M2: real admin router (was hardcoded literals) ---"
python3 "$HERE/scripts/m2_admin_router.py" "$TARGET"

echo
echo "--- 17/21 M2: real CLI + Makefile gate + .env.example ---"
python3 "$HERE/scripts/m2_cli_and_makefile.py" "$TARGET"

echo
echo "--- 18/21 M2: event bus contract (20 of 24 subscribe calls were never awaited) ---"
python3 "$HERE/scripts/m2_event_bus.py" "$TARGET"

echo
echo "--- 19/21 M2: regenerate the migration for the new tables ---"
python3 "$HERE/scripts/m1_generate_migration.py" "$TARGET" "$HERE/scripts/m1pkg/alembic_001.py" >/dev/null
cp "$HERE/scripts/m1pkg/alembic_001.py" "$TARGET/alembic/versions/001_initial_schema.py"
echo "  ok  alembic/versions/001_initial_schema.py: regenerated (14 tables, 337 columns)"

echo
echo "--- 20/21 M3: MT5-accurate margin engine + pre-trade rewrite ---"
mkdir -p "$TARGET/core/domains/market_data" "$TARGET/tests/unit/domains/market_data"
cp "$HERE/scripts/m3pkg/mt5_margin.py" "$TARGET/core/domains/market_data/margin.py"
cp "$HERE/scripts/m3pkg/test_mt5_margin.py" "$TARGET/tests/unit/domains/market_data/"
python3 "$HERE/scripts/m3_pretrade_margin.py" "$TARGET"
python3 "$HERE/scripts/m3_fix_margin_tests.py" "$TARGET"

echo
echo "--- 21/21 M3: RiskEngine entity drift + cross-rate triangulation ---"
python3 "$HERE/scripts/m3_fix_risk_engine.py" "$TARGET"
python3 "$HERE/scripts/m3_fix_position_default.py" "$TARGET"
python3 "$HERE/scripts/m3_fix_commission.py" "$TARGET"
python3 "$HERE/scripts/m3_margin_spec_cache.py" "$TARGET"
python3 "$HERE/scripts/m3_resync_risk_tests.py" "$TARGET"
python3 "$HERE/scripts/m3_symbol_currencies.py" "$TARGET"
python3 "$HERE/scripts/m3_update_gap_tests.py" "$TARGET"
python3 "$HERE/scripts/m3_final_fixes.py" "$TARGET"
python3 "$HERE/scripts/m3_export_currencies.py" "$TARGET"
python3 "$HERE/scripts/m3_leftovers.py" "$TARGET"
python3 "$HERE/scripts/m3_last_renames.py" "$TARGET"
python3 "$HERE/scripts/m3_rewrite_pnl_test.py" "$TARGET"
python3 "$HERE/scripts/m3_ctor_drift.py" "$TARGET"
python3 "$HERE/scripts/m3_last_two_tests.py" "$TARGET"
python3 "$HERE/scripts/m3_fix_login_id.py" "$TARGET"
python3 "$HERE/scripts/m3_attr_names.py" "$TARGET"
python3 "$HERE/scripts/m3_fix_recalc_margin.py" "$TARGET"
python3 "$HERE/scripts/m3_fix_currency_pairs.py" "$TARGET"
python3 "$HERE/scripts/m3_fix_conversion_side.py" "$TARGET"
python3 "$HERE/scripts/m3_fix_pnl_expectation.py" "$TARGET"
python3 "$HERE/scripts/m3_fix_liquidation_seed.py" "$TARGET"
python3 "$HERE/scripts/m3_fix_uow.py" "$TARGET"
python3 "$HERE/scripts/m3_stable_benchmark.py" \
  "$TARGET/tests/unit/domains/accounts/test_account_models_stress.py"
python3 "$HERE/scripts/m1_generate_migration.py" "$TARGET"

echo
echo "--- CI gate + line-ending policy ---"
mkdir -p "$TARGET/.github/workflows"
cp "$HERE/scripts/mt5pkg/ci-import-gate.yml" "$TARGET/.github/workflows/import-gate.yml"
cp "$HERE/scripts/mt5pkg/gitattributes" "$TARGET/.gitattributes"

echo
echo "=== import gate ==="
cd "$TARGET"
fail=0
for m in \
  core.ports.interfaces \
  core.events.domain_events \
  infrastructure.persistence.db_models \
  infrastructure.mt5.wire \
  infrastructure.mt5.fieldmap \
  infrastructure.mt5.codec \
  application.cache.config_cache \
  application.commands.create_group \
  application.services.swap_worker \
  api.di_providers \
  api.main \
  application.di.market_data_setup \
  infrastructure.persistence.di_setup \
  infrastructure.persistence.unit_of_work \
  infrastructure.persistence.repositories.position_repository \
  infrastructure.persistence.config_models \
  infrastructure.persistence.config_mappers \
  infrastructure.persistence.mappers \
  infrastructure.persistence.account_models \
  infrastructure.persistence.manager_models \
  infrastructure.config.loader \
  infrastructure.config.seeder \
  infrastructure.persistence.repositories.manager_repository \
  cli.main \
  api.routers.admin.admin_router \
  core.domains.market_data.margin \
  application.services.risk_service
do
  if PYTHONPATH="$TARGET" python3 -c "import $m" 2>/dev/null; then
    printf '  OK    %s\n' "$m"
  else
    printf '  FAIL  %s\n' "$m"
    PYTHONPATH="$TARGET" python3 -c "import $m" 2>&1 | tail -2 | sed 's/^/          /'
    fail=1
  fi
done

echo
if [[ $fail -ne 0 ]]; then
  echo "=== M0 INCOMPLETE: see failures above ==="
  exit 1
fi
echo "=== M0+M1+M2+M3: every module imports ==="

echo
echo "=== test suite ==="
cd "$TARGET"
PYTHONPATH="$TARGET" BROKER_MT5_FIXTURES="$HERE/decoded/mt5-format-structure" \
  python3 -m pytest tests -q --no-header -p no:cacheprovider 2>&1 | tail -3

echo
echo "=== M1 proof: lossless MT5 import/export (the format constraint) ==="
PYTHONPATH="$TARGET" BROKER_MT5_FIXTURES="$HERE/decoded/mt5-format-structure" \
  python3 "$HERE/scripts/m1_proof_roundtrip.py" 2>&1 | grep -E "field-identical|conformant|Point" \
  || { echo "M1 PROOF FAILED"; exit 1; }

echo
echo "=== M3 proof: the three symbol currencies survive the round trip ==="
PYTHONPATH="$TARGET" BROKER_MT5_FIXTURES="$HERE/decoded/mt5-format-structure" \
  python3 "$HERE/scripts/m3_proof_currencies.py" "$TARGET" 2>&1 \
  | grep -E "^\[[0-9]\]|populated on|field-identical|mismatches|PROOF" \
  || { echo "M3 CURRENCY PROOF FAILED"; exit 1; }

echo
echo "=== M3 proof: the unit of work shares one session and rolls back atomically ==="
PYTHONPATH="$TARGET" python3 "$HERE/scripts/m3_proof_uow.py" "$TARGET" 2>&1 | tail -12 \
  || { echo "M3 UOW PROOF FAILED"; exit 1; }

echo
echo "=== M3 proof: is the risk maths trustworthy? ==="
PYTHONPATH="$TARGET" BROKER_MT5_FIXTURES="$HERE/decoded/mt5-format-structure" \
  python3 "$HERE/scripts/m3_proof_margin.py" "$TARGET" 2>&1 | tail -14 \
  || { echo "M3 MARGIN PROOF FAILED"; exit 1; }
