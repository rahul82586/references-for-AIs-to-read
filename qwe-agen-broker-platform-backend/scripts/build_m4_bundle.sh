#!/usr/bin/env bash
# Build the M4 deliverable bundle. Plain cp + find; no rsync in this sandbox.
set -uo pipefail

STAGE=/home/user/_stage/M4-BUNDLE
SRC=/home/user/work/bp
BASE=/home/user/refs/qwencode/broker-platform

prune() {
  find "$1" \( -name '__pycache__' -o -name '.pytest_cache' -o -name '.broker' -o -name '.git' \) \
       -type d -prune -exec rm -rf {} + 2>/dev/null
  find "$1" \( -name '*.pyc' -o -name '*.db' \) -type f -delete 2>/dev/null
  return 0
}

rm -rf "$STAGE"
mkdir -p "$STAGE/git" "$STAGE/scripts" "$STAGE/reports" "$STAGE/decoded"

echo "[1] copying the M4 tree"
cp -a "$SRC" "$STAGE/broker-platform-M4"
prune "$STAGE/broker-platform-M4"
echo "    files: $(find "$STAGE/broker-platform-M4" -type f | wc -l)"

echo "[2] copying scripts"
cp /home/user/scripts/*.py "$STAGE/scripts/" 2>/dev/null
cp /home/user/scripts/*.sh "$STAGE/scripts/" 2>/dev/null

echo "[3] copying reports"
for f in ANALYSIS.md M0-REPORT.md M1-REPORT.md M2-REPORT.md M3-REPORT.md M4-REPORT.md \
         MASTER-MIND-MAP.md SHORT-ANSWERS.md STATUS-INVENTORY.csv; do
  [ -f "/home/user/$f" ] && cp "/home/user/$f" "$STAGE/reports/"
done
ls "$STAGE/reports" | sed 's/^/      /'

echo "[4] copying decoded fixtures"
cp -a /home/user/decoded/mt5-format-structure "$STAGE/decoded/"
prune "$STAGE/decoded"

echo "[5] building git history"
WORK=$(mktemp -d)
git init -q "$WORK/repo"
cd "$WORK/repo" || exit 1
git config user.email "m4@broker-platform.local"
git config user.name  "M0-M4 work"

cp -a "$BASE"/. ./
prune .
git add -A
git commit -qm "upstream baseline: qwencode/broker-platform as delivered

93 of 180 modules did not import. Five independent margin formulas. The execution
path had never run: the trade endpoint returned a mock order with state=FILLED."

find . -maxdepth 1 -mindepth 1 ! -name '.git' -exec rm -rf {} +
cp -a "$SRC"/. ./
prune .
git add -A
git commit -qm "M0-M4: importable, one schema, config plane, trustworthy risk maths, orders execute

M0  93/180 modules importing -> all of them; DI factories, port segregation, event models
M1  one Base.metadata schema; MT5 wire format preserved (362/362 symbols field-identical)
M2  configuration plane seeds and reads back; thresholds are PERCENT; CLI that admits stubs
M3  margin maths == MT5's published examples; three symbol currencies survive; UoW atomic
M4  the trading plane exists and an order executes end to end: matching engine, LP gateway
    stub, in-process bus, composition root, and 35 defects fixed on the execution path.
    274 tests pass; 6 proofs green."

git format-patch --stdout HEAD~1 > "$STAGE/git/m0-m4-work.format-patch.txt"
git diff HEAD~1 HEAD             > "$STAGE/git/M0-M4-plain-diff.patch"
git bundle create "$STAGE/git/m0-m4-work.bundle" --all
echo "    commits: $(git rev-list --count HEAD)"
git diff --shortstat HEAD~1 HEAD | sed 's/^/      /'

cd /home/user || exit 1
rm -rf "$WORK"

echo "[6] sizes"
du -sh "$STAGE"/* | sed 's/^/      /'
echo "BUILD OK: $STAGE"
