#!/usr/bin/env bash
# Verify the CI gate is not decorative: run its checks against BOTH the pristine
# (broken) tree and the M0-fixed tree. The gate must fail on the former and pass on
# the latter. A gate that passes on both is a gate that catches nothing.
set -uo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PRISTINE="$HERE/refs/qwencode/broker-platform"
FIXED="$HERE/work/bp"

run_checks() {
  local dir="$1"
  cd "$dir"

  echo "    [1] compileall"
  if python3 -m compileall -q core application infrastructure api cli tests >/dev/null 2>&1; then
    echo "        pass"
  else
    echo "        FAIL"
  fi

  echo "    [2] import every module"
  PYTHONPATH="$dir" python3 - <<'PY' 2>/dev/null
import pathlib, sys, importlib
root = pathlib.Path(".")
fails = 0
total = 0
for path in sorted(root.rglob("*.py")):
    if any(p in {".venv","build","dist","__pycache__",".github","alembic"} for p in path.parts):
        continue
    rel = path.relative_to(root).with_suffix("")
    parts = list(rel.parts)
    if parts[-1] == "__init__":
        parts = parts[:-1]
    if not parts:
        continue
    total += 1
    try:
        importlib.import_module(".".join(parts))
    except Exception:
        fails += 1
print(f"        {'pass' if fails==0 else 'FAIL'}  ({total-fails}/{total} modules import)")
sys.exit(1 if fails else 0)
PY
  [ $? -ne 0 ] && echo "        (import check failed)"

  echo "    [3] pytest --collect-only"
  if PYTHONPATH="$dir" python3 -m pytest tests --collect-only -q -p no:cacheprovider >/dev/null 2>&1; then
    echo "        pass"
  else
    echo "        FAIL"
  fi

  echo "    [4] no shadowed definitions"
  python3 - <<'PY' 2>/dev/null
import ast, pathlib, sys, collections
bad = []
for path in sorted(pathlib.Path(".").rglob("*.py")):
    if any(p in {".venv","build","dist","__pycache__",".github","alembic"} for p in path.parts):
        continue
    try:
        tree = ast.parse(path.read_text(encoding="utf-8", errors="replace"))
    except SyntaxError:
        continue
    counts = collections.Counter(
        n.name for n in tree.body
        if isinstance(n, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef))
    )
    for name, n in counts.items():
        if n > 1:
            bad.append(f"{path}: {name} x{n}")
if bad:
    print(f"        FAIL  ({len(bad)} shadowed)")
    for b in bad[:8]:
        print(f"            {b}")
    sys.exit(1)
print("        pass")
PY
  cd "$HERE"
}

echo "=== PRISTINE tree (should FAIL the gate) ==="
run_checks "$PRISTINE"
echo
echo "=== M0-FIXED tree (should PASS the gate) ==="
run_checks "$FIXED"
