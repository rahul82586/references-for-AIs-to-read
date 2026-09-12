#!/usr/bin/env bash
# Run every proof gate, plus the test suite and the lint gate.
#
# This exists because the milestone reports kept re-typing the same for-loop, and
# because the m1-m4 proofs went missing from the tree once already (they survived
# only in git history at b324ba9, after HEAD reorganised into work/bp and dropped
# the top-level scripts/). One entry point means one thing to remember and one
# thing to run before claiming a milestone is green.
#
# Usage:
#   scripts/run_all_proofs.sh              # everything
#   scripts/run_all_proofs.sh quick        # proofs only, skip the test suite
#
# Environment:
#   BROKER_MT5_FIXTURES   the DECODED (UTF-8) mt5-format-structure tree.
#                         Defaults to ../decoded/mt5-format-structure.
#                         The raw export is UTF-16; m3_proof_currencies reads the
#                         fixtures as utf-8-sig and dies on the BOM. Decode with
#                         scripts/decode_mt5_json.py first.
set -u

BP="$(cd "$(dirname "$0")/.." && pwd)"
cd "$BP" || { echo "FATAL: bp tree not visible at $BP"; exit 1; }

export PYTHONPATH="$BP"
export BROKER_MT5_FIXTURES="${BROKER_MT5_FIXTURES:-$BP/../decoded/mt5-format-structure}"
# The fail-hard secrets gate (M5) refuses to boot without these. They are
# generated fresh per run and used only by in-process proofs.
export SECRET_KEY="${SECRET_KEY:-$(python3 -c 'import secrets;print(secrets.token_hex(32))')}"
export ADMIN_API_KEY="${ADMIN_API_KEY:-$(python3 -c 'import secrets;print(secrets.token_hex(24))')}"

MODE="${1:-all}"

if [ ! -d "$BROKER_MT5_FIXTURES" ]; then
  echo "FATAL: BROKER_MT5_FIXTURES not found: $BROKER_MT5_FIXTURES"
  echo "       decode the raw UTF-16 export first: python3 scripts/decode_mt5_json.py"
  exit 1
fi

PASS=0; FAIL=0; SKIP=0; FAILED_LIST=""; SKIPPED_LIST=""
run() {  # run <label> <command...>
  # exit 0 = pass, exit 2 = deliberately skipped (e.g. a trading-session proof on
  # a weekend, which m4_proof_order_executes does), anything else = fail.
  # Treating a skip as a failure made the whole gate cry wolf every Saturday.
  local label="$1"; shift
  printf "  %-38s " "$label"
  local log; log="$(mktemp)"
  timeout 900 "$@" >"$log" 2>&1
  local rc=$?
  if [ $rc -eq 0 ]; then
    local summary
    summary="$(grep -oE '[0-9]+ passed|[0-9]+/[0-9]+|All checks passed' "$log" | tail -1)"
    echo "PASS  ${summary:-}"
    PASS=$((PASS+1))
  elif [ $rc -eq 2 ]; then
    local reason
    reason="$(grep -oiE 'SKIPPED.*|outside its trading session.*|market closed.*' "$log" | head -1)"
    echo "SKIP  ${reason:-exit 2}"
    SKIP=$((SKIP+1)); SKIPPED_LIST="$SKIPPED_LIST $label"
  else
    echo "FAIL"
    FAIL=$((FAIL+1)); FAILED_LIST="$FAILED_LIST $label"
    echo "    --- last lines ---"
    tail -6 "$log" | sed 's/^/    /'
  fi
  rm -f "$log"
}

echo "bp        : $BP"
echo "fixtures  : $BROKER_MT5_FIXTURES"
echo

echo "== lint gate (the one CI enforces) =="
run "ruff E9,F63,F7,F82" python3 -m ruff check --select E9,F63,F7,F82 .

if [ "$MODE" != "quick" ]; then
  echo
  echo "== test suite =="
  run "pytest tests" python3 -m pytest tests -q --no-header -p no:cacheprovider
fi

echo
echo "== legacy proofs (M1-M4) =="
run "m1_proof_roundtrip"        python3 scripts/m1_proof_roundtrip.py "$BP"
run "m1_roundtrip_all_sections" python3 scripts/m1_proof_roundtrip_all_sections.py "$BROKER_MT5_FIXTURES"
run "m2_proof_seed"             python3 scripts/m2_proof_seed.py "$BP"
run "m3_proof_currencies"       python3 scripts/m3_proof_currencies.py "$BP"
run "m3_proof_uow"              python3 scripts/m3_proof_uow.py "$BP"
run "m3_proof_margin"           python3 scripts/m3_proof_margin.py "$BP"
run "m4_proof_order_executes"   python3 scripts/m4_proof_order_executes.py "$BP"

echo
echo "== milestone proofs (M8-M11) =="
run "m8_proof_routing"          python3 scripts/m8_proof_routing.py
run "m9_proof_sltp_expiration"  python3 scripts/m9_proof_sltp_expiration.py
run "m10_proof_adapters"        python3 scripts/m10_proof_adapters.py
run "m11_proof_a_book"            python3 scripts/m11_proof_a_book.py

echo
echo "== live HTTP, no credentials needed (SQLite + mock feed) =="
run "local_e2e"                 bash scripts/local_e2e.sh

echo
echo "============================================================"
echo " $PASS passed, $FAIL failed, $SKIP skipped"
if [ -n "$SKIPPED_LIST" ]; then
  echo " skipped:$SKIPPED_LIST"
  echo " (a skip is deliberate - usually a trading-session proof run at the weekend)"
fi
if [ "$FAIL" -ne 0 ]; then
  echo " failed:$FAILED_LIST"
  echo "============================================================"
  exit 1
fi
[ "$SKIP" -eq 0 ] && echo " all gates green" || echo " all runnable gates green"
echo "============================================================"
echo
echo "Not run here (they need real infrastructure):"
echo "  scripts/m5_proof_cloud.sh        Neon PostgreSQL + Upstash Redis   (33 checks)"
echo "  scripts/m10_proof_cloud_ws.sh    the above + a live WS price feed  (14 checks)"
echo "  scripts/d12_proof_cloud_close.sh the above + the MT5 tunnel: open a"
echo "                                   position at a live price and CLOSE it over"
echo "                                   HTTP, then read the OUT deals back out of"
echo "                                   Neon (41 checks; found D13, D14 and D15)"
