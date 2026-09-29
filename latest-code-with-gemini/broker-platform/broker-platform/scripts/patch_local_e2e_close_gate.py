#!/usr/bin/env python3
"""Add the D11 close gate to scripts/local_e2e.sh.  Idempotent.

Why this exists
---------------
`local_e2e.sh` is the no-credentials gate: SQLite + in-process bus + mock feed,
real HTTP.  It opened a position and stopped there.  Closing is not a detail of
opening - it is the only place realised PnL is booked and D10's margin is
released - so a gate that never closes proves half the order path, and that is
precisely the half D11 was about (the cloud database held 31 IN deals and zero
OUT deals because no client close route existed).

Two changes:

1. A `3b` step that widens the seeded Mon-Fri trade sessions to 7x24 **in the
   disposable local proof DB only**.  The seeded sessions are correct MT5
   behaviour, but they make the trade half of the gate unrunnable on a weekend,
   which is when the gate is most likely to be re-run.  This is a config value,
   not a bypass: CreateOrderHandler and PreTradeRiskService still check the
   session, they just find it open.  `E2E_FORCE_SESSIONS=0` keeps the weekend
   refusal under test instead.

2. The close sequence itself, plus assertions: 200, `fully_closed`, the OUT deal
   id, the position gone from `/account/positions`, margin released (D10), and a
   close against someone else's position id refused.

Run:  python3 scripts/patch_local_e2e_close_gate.py
"""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
TARGET = HERE / "local_e2e.sh"

SESSIONS_ANCHOR = 'echo "== 4. boot API =="'

SESSIONS_BLOCK = r'''echo "== 3b. trade sessions =="
# The seeded sessions are Mon-Fri, which is correct MT5 behaviour, but it makes
# the whole trade half of this gate unrunnable at a weekend - and the close half
# (D11) is exactly the part that was never proven end to end. This edits the
# DISPOSABLE local SQLite config only, never a cloud database, and it is a config
# value rather than a bypass: CreateOrderHandler and PreTradeRiskService still
# check the session, they just find it open. E2E_FORCE_SESSIONS=0 keeps the
# weekend refusal under test instead (the trade checks then skip, as before).
if [ "${E2E_FORCE_SESSIONS:-1}" = "1" ]; then
  python3 - >"$ARENA_WORKSPACE/work/logs/sessions.log" 2>&1 <<'PY'
import json, os, sqlite3
path = os.environ["DATABASE_URL"].split("sqlite+aiosqlite:///")[-1]
db = sqlite3.connect(path)
db.execute("update symbols set sessions_trades_json = ?",
           (json.dumps([[{"Open": "0", "Close": "1440"}] for _ in range(7)]),))
db.commit()
print("sessions widened:", db.execute("select count(*) from symbols").fetchone()[0], "symbols")
db.close()
PY
  grep -q "sessions widened" "$ARENA_WORKSPACE/work/logs/sessions.log" \
    && ok "trade sessions widened to 7x24 in the local proof DB" \
    || { bad "widen trade sessions"; tail -5 "$ARENA_WORKSPACE/work/logs/sessions.log"; }
else
  echo "  [SKIP] E2E_FORCE_SESSIONS=0 - seeded Mon-Fri sessions kept"
fi

'''

CLOSE_ANCHOR = 'echo "$T" | grep -qi \'FILLED\' && ok "order FILLED" || bad "order filled"\n'

CLOSE_BLOCK = r'''
echo "== 6b. D11: the client closes its own position over HTTP =="
# Before D11 this route did not exist, so PUT/DELETE returned a hardcoded success
# and a client could never close. These checks fail against the pre-D11 tree.
echo "$T" | grep -q '"close_status": 200' \
  && ok "POST /trade/positions/{id}/close returned 200" || bad "close route answered"
echo "$T" | grep -q '"fully_closed": true' \
  && ok "close reported fully_closed" || bad "fully_closed"
echo "$T" | grep -q '"positions_after_close": 0' \
  && ok "position gone from /account/positions" || bad "position still open after close"
if echo "$T" | grep -q '"deal_id": ""'; then
  bad "close returned no OUT deal id"
else
  ok "close returned the OUT deal id"
fi
python3 - <<'PY' && ok "margin released by the close (D10)" || bad "margin not released"
import json, os, sys
d = json.load(open(os.path.join(os.environ["ARENA_WORKSPACE"], "work/logs/trade.json")))
try:
    before, after = float(d["margin_before_close"]), float(d["margin_after_close"])
except (KeyError, TypeError, ValueError):
    sys.exit(1)
sys.exit(0 if (before > 0 and after < before) else 1)
PY
echo "$T" | grep -qE '"foreign_close_status": (403|404)' \
  && ok "closing someone else's position refused" \
  || bad "foreign position close not refused"
'''

PY_ANCHOR = '''st,info=get("/api/v1/account/info",token)
out["account_info_status"]=st; out["account_info"]=info if st==200 else str(info)[:200]
print(json.dumps(out, default=str))'''

PY_BLOCK = '''st,info=get("/api/v1/account/info",token)
out["account_info_status"]=st; out["account_info"]=info if st==200 else str(info)[:200]
out["margin_before_close"]=(info.get("margin_used") if isinstance(info,dict) else None)

# --- D11: the client closes its own position over HTTP ----------------------
pid = pos[0].get("position_id") if isinstance(pos, list) and pos else None
out["position_id"] = pid
if pid:
    st, cbody = post(f"/api/v1/trade/positions/{pid}/close", {}, token)
    out["close_status"] = st
    out["close"] = cbody if st == 200 else str(cbody)[:400]
    st, pos2 = get("/api/v1/account/positions", token)
    out["positions_after_close"] = len(pos2) if isinstance(pos2, list) else str(pos2)[:200]
    st, info2 = get("/api/v1/account/info", token)
    out["margin_after_close"] = (info2.get("margin_used") if isinstance(info2, dict)
                                 else str(info2)[:200])
# ownership: the same call against a position this token does not own must not
# succeed. 404 (unknown id) and 403 (known, not yours) are both a refusal.
st, foreign = post("/api/v1/trade/positions/999999_XAUUSD_deadbeef/close", {}, token)
out["foreign_close_status"] = st
print(json.dumps(out, default=str))'''


def main() -> int:
    if not TARGET.exists():
        print(f"FATAL: {TARGET} not found", file=sys.stderr)
        return 1
    text = TARGET.read_text()
    changed = False

    if "3b. trade sessions" not in text:
        if SESSIONS_ANCHOR not in text:
            print("FATAL: boot-API anchor not found", file=sys.stderr)
            return 1
        text = text.replace(SESSIONS_ANCHOR, SESSIONS_BLOCK + SESSIONS_ANCHOR, 1)
        changed = True
        print("added step 3b (widen local trade sessions)")
    else:
        print("step 3b already present")

    if 'out["close_status"]' not in text:
        if PY_ANCHOR not in text:
            print("FATAL: python trade-step anchor not found", file=sys.stderr)
            return 1
        text = text.replace(PY_ANCHOR, PY_BLOCK, 1)
        changed = True
        print("added the close sequence to the trade step")
    else:
        print("close sequence already present")

    if "6b. D11" not in text:
        if CLOSE_ANCHOR not in text:
            print("FATAL: FILLED assertion anchor not found", file=sys.stderr)
            return 1
        text = text.replace(CLOSE_ANCHOR, CLOSE_ANCHOR + CLOSE_BLOCK, 1)
        changed = True
        print("added gate 6b (close assertions)")
    else:
        print("gate 6b already present")

    if changed:
        TARGET.write_text(text)
        print(f"wrote {TARGET}")
    else:
        print("nothing to do")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
