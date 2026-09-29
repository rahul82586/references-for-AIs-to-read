# Forex Broker Platform — PROJECT STATE & CONTEXT ANCHOR v7

**Written:** 2026-09-14 (session 7, at the end of M17 = F8/F9 rebuilt + identity-plan step 8)
**Supersedes:** `PROJECT-STATE-v6.md` (session 6). Read `M17-REPORT.md` for this
milestone in full, `M16-REPORT.md` for steps 5–7, and `IDENTITY-BUILD-PLAN.md`
for step 9. v5's §3 (architecture + design law), §5 (decisions not to
re-litigate) and v6's §6 (step-5/6/7 decisions) all still hold and are not
repeated here.

**Sources:** GitHub `rahul82586/references-for-AIs-to-read` @ `475c14b` (the
HEAD this session started from) · the session-6 HTML attachment (full
transcript parsed — it is the spec the F8/F9 rebuild followed) · Drive
captures of sessions 2 and 3 (re-downloaded, parsed, then **redacted/deleted —
see §7**) · all gates re-run before AND after building · live Neon re-probed.

---

## 0. Verified current state — everything below was RUN, not read

Tree: `qwe-agen-broker-platform-backend/work/bp` — **~370 py files**,
migrations **001→009**, OpenAPI paths **45 → 52**.

| Gate | Result (2026-09-14, session 7) |
|---|---|
| `pip install -e ".[dev]"` | clean (F5 holds; NOTE: packages die between turns — reinstall each turn) |
| `pytest tests` (fixtures decoded) | **788 passed, 0 failed, 0 skipped** (was 740 on `475c14b`; +19 F8/F9, +29 step 8) |
| `ruff --select E9,F63,F7,F82` | clean |
| `m1_proof_roundtrip_all_sections` | **392/392** byte-identical |
| `m2` / `m3` ×3 | ✅ / ✅ |
| `m8` / `m9` / `m10` / `m11` | 18/18 · 14/14 · 19/19 · 39/39 |
| `m4_proof_order_executes` | SKIP — sandbox clock is Sunday UTC. Correct. |
| `p1_proof_migration_009` / `p1_proof_identity` | 24/24 · 59/59 |
| `p1_proof_account_creation` / `p1_proof_manager_creation` | 72/72 · 80/80 |
| **`p1_proof_read_plane` (NEW)** | **55/55** — in CI |
| **`f8f9_proof_live_position_get` (NEW)** | **10/10 on live Neon** — out of CI (needs DATABASE_URL) |
| GitHub Actions CI | ✅ green on `dd27011` and `475c14b` (runs on the M17 commits pending push) |

## 0b. Live infrastructure — probed 2026-09-14 (session 7)

Neon PostgreSQL 18.6 reachable, **every v6 claim reproduced exactly**: head
`009_identity_plane` · 18 tables · accounts 67 cols / 45 rows (`rights=0` on
all 45) · clients 32 cols / **0 rows** · groups 58 / 7 · managers 24 / 1 ·
`login_counters` EMPTY · positions 37 / 31 open / 24 NULL `price_current` ·
37 IN / 9 OUT deals · 9 breaks OPEN · `bars` = 0. **D16 re-measured, still
live: 24/45 accounts**, deltas `+800.70 ×10, −749.20 ×9, +798.90 ×2, +2.10,
−0.50, +2.30`. Join note: `accounts.login` is VARCHAR, `positions.account_login`
BIGINT → join `p.account_login::text = a.login`. **Post-F8/F9, `PositionGet`
now serves this book** (10/10 live proof: 31 rows, 30 logins, honest nulls).

The `.env` at `39c7eaf2` still returns 200 with all four secrets. Rotation /
purge / visibility remain **user actions** (the user states all credentials
are disposable test values).

---

## 1. Milestone ledger delta (M17, this session)

* **F8/F9 REBUILT** — session 6 fixed these and its commit died with the
  sandbox (never pushed; `475c14b` still had the bug). Rebuilt to the
  transcript's recorded design: `GetManagerPositionsQuery(+Handler)`
  cross-account read dispatching to the repository's own SQL methods ·
  `position_to_info` as the ONE serializer · `PositionInfo` gains
  `position_id`, honest Optional `ticket` (from `external_id`) and
  `price_current` · the 503/500/[]-only-when-flat contract. 19 HTTP-level
  regressions + 10/10 live.
* **Step 8 — the admin read plane** — `find_page(limit, offset, **filters) →
  (rows, total)` on all six repositories (SQL-level; unknown filter refused;
  accounts ordered NUMERICALLY; `find_all` poisoned in tests so the
  load-everything trap cannot return) · 8 query files · three read routers
  gated by the READING rights (ACC_READ 25 / CLIENTS_ACCESS 96 / TRADES_READ
  29) + the managers LIST under CFG_MANAGERS · six-tab account detail with
  rights decoded server-side · `/admin/clients/schema` +
  `client_fields.yaml` (IMTClient's 63 accessors, read member-by-member) ·
  B2 trade reads incl. the orders history tri-state and the contradiction-400
  · bare arrays + `X-Total-Count` (the UI's `setPositions(data)` keeps
  working) · credential material never serializes (booleans only).

**Defect ledger delta:** **F8 ✅ F9 ✅ FIXED (rebuilt + proven live)** ·
**D20 🟠 NEW, open** (`Order.price_order` Optional-on-entity vs NOT-NULL-
column + unconditional `.value` in `order_to_db`; fix belongs to migration
010) · D16 ❌ OPEN (re-measured live) · D17 ❌ OPEN (bit twice more this
session) · D4 🟡 unchanged (leak still fetchable; **the session WORKSPACE is
now credential-free — §7**) · F1/F2/F4/F6/F7 ❌ unchanged · everything else
as v6.

## 2. Decisions made this session — do not re-litigate

Everything in v5 §5 and v6 §6 still holds. Added:

* **Lists are bare arrays with `X-Total-Count`**; `limit`/`offset` page. An
  envelope would break every existing UI page at once; MT5's Web API returns
  bare arrays too.
* **Reads are gated by the READING right** (ACC_READ / CLIENTS_ACCESS /
  TRADES_READ); writes keep their stronger bits. A read bit never opens a
  write plane; `must_change_password` blocks reads too.
* **The F9 ticket rule is platform-wide**: venue ticket from `external_id` or
  `null` — never 0 — on positions, deals and orders; our canonical ids ride
  alongside as strings (`position_id`/`deal_id`/`order_id`).
* **`Client.status` serves value AND name** from the domain `ClientStatus`
  enum (its own mapping, NOT the raw SDK ordinals); the yaml expands it from
  code.
* **Legacy `admin_router` reads are shadowed, not deleted** (mount order puts
  the paged reads first). Deleting them is a separate cleanup decision.
* **`GET /accounts/schema` keeps its ACC_MANAGER gate** (form rendering is a
  write-plane concern); the NEW client schema is under CLIENTS_ACCESS.
* `find_page` implementations **refuse unknown filters** — a silently
  dropped filter serves an unfiltered page that looks filtered.

## 3. Session-infrastructure findings — the death protocol, AMENDED

1. **`.git` does not survive TURN boundaries** (not just session death):
   session 7's first F8/F9 commit evaporated between messages; the working
   tree survived and the commit was recreated. ⇒ **bundle after EVERY
   commit** (`work/patches/repo-full-history.bundle`, gitignored, survives as
   a plain file) and ask the user to push at the first pause.
2. **Installed packages do not survive turns** — re-run `pip install -e
   ".[dev]"` each turn before gates.
3. **The chat input filter blocks messages containing secret-shaped strings**
   (`Content Security Warning: ... inappropriate content`). Keep credentials
   out of pasted text; live proofs read DATABASE_URL from the environment at
   run time, never from a workspace file, never echoed.
4. Everything else unchanged: push at every milestone (never web upload),
   write `docs/Mn-REPORT.md` early, update THIS anchor, prefer
   `scripts/patch_*.py`, D17's runtime-path rule (`WS = Path(os.environ.get(
   "ARENA_WORKSPACE") or os.getcwd())`; `HOME=/tmp`; no curl/wget; Drive needs
   the `drive.usercontent.google.com/download?id=…&confirm=t` form; MHTML →
   `email` module, first `text/html` part).

## 4. What is open, in priority order

**P0 — user actions**
1. Rotate Neon/Upstash/SECRET_KEY/ADMIN_API_KEY; purge `39c7eaf2` or go
   private. (Stated disposable; the repo is public.)
2. **PUSH the two M17 commits** (`07c0c27` F8/F9, `69915d7` step 8 + docs
   commit to follow) — or clone the bundle and push that. CI will run
   `p1_proof_read_plane` for the first time.
3. The `clients = 0` backfill decision (the read plane serves `total: 0`
   honestly either way; any client-linked feature blocks on it).

**P1 — money & correctness**
4. **D16** — 24/45 live accounts wrong NOW (~20-line fix: sweep calls
   `SqlPositionRepository.update_valuation` per priced position; never sweep
   MOCK-opened positions against live ticks).
5. **D20** with migration 010 (nullable `orders.price_order` + None-tolerant
   mapper pair) — bundle with the gateway config plane migration.
6. `margin_free`/`margin_level` four-writer problem (design decision) ·
   stop-out never live-fired · A-Book close never unwinds the hedge · 9
   breaks OPEN with no resolution path · `bars` = 0 · WS keepalive ~60 s ·
   19/25 pre-trade checks · commission types/charge modes.

**P1 — identity plane & UI**
7. **Step 9: Allocations** (own table + CRUD; when the client-terminal story
   starts).
8. **B1 manager-on-behalf-of**: `/manager/*` trading writes accept a target
   `login`, authorised against group scope — the dealer UI's blocker.
9. `UpdateAccountHandler` (per-tab partial bodies + the two move rules) +
   `UpdateGroupCommand` grown to the 27 modelled fields.
10. **B3 `GET /admin/ticks`** (cheapest high-value UI endpoint) · legacy
    admin_router shadowed-reads cleanup · manager JWT rollout to the
    remaining static-key admin reads (F2's plane) · F1/F4/F6/F7.

**P2/P3** — unchanged from v4 §5 items 16–28.

## 5. Reproducing the gates

```bash
cd qwe-agen-broker-platform-backend/work/bp
pip install -e ".[dev]"                      # EVERY turn - packages don't persist
export PYTHONPATH=$PWD
python3 - <<'EOF'                            # decode fixtures (UTF-16LE -> UTF-8)
import json, os, pathlib
WS   = pathlib.Path(os.environ.get("ARENA_WORKSPACE") or os.getcwd())
src  = WS/"repo"/"mt5-format-structure"      # or repo-fresh/, wherever the clone is
out  = WS/"decoded"/"mt5-format-structure"; out.mkdir(parents=True, exist_ok=True)
for f in sorted(src.glob("*.json")):
    raw=f.read_bytes()
    txt=raw.decode("utf-16-le" if raw[:2]==b"\xff\xfe" else "utf-8",errors="replace").lstrip("\ufeff")
    json.loads(txt); (out/f.name).write_text(txt,encoding="utf-8")
EOF
export BROKER_MT5_FIXTURES=<that decoded dir>
export SECRET_KEY=$(python3 -c "import secrets;print(secrets.token_hex(32))")
export ADMIN_API_KEY=$(python3 -c "import secrets;print(secrets.token_hex(24))")
python3 -m pytest tests -q                              # 788 passed
python3 -m ruff check --select E9,F63,F7,F82 .          # clean
python3 scripts/p1_proof_read_plane.py                  # 55/55
python3 scripts/p1_proof_account_creation.py            # 72/72
python3 scripts/p1_proof_manager_creation.py            # 80/80
python3 scripts/p1_proof_identity.py                    # 59/59
python3 scripts/p1_proof_migration_009.py               # 24/24
python3 scripts/m1_proof_roundtrip_all_sections.py      # 392/392
# live-infra (env-only credentials, never files):
DATABASE_URL=... python3 scripts/f8f9_proof_live_position_get.py   # 10/10
```

## 6. Session 7 handover state

* **On GitHub:** everything up to `475c14b` (steps 5–7, CI green).
* **To push:** `07c0c27` (F8/F9) · `69915d7` (step 8) · the docs commit that
  follows this file. A verified bundle sits at
  `work/patches/repo-full-history.bundle` — clone it, set origin, push.
* **Workspace credential sweep: DONE** (§7 of M17-REPORT) — `live_env.txt`
  deleted, raw session-2/3 captures deleted, all transcripts + the session-6
  attachment redacted, final sweep zero. Re-downloadable from Drive if ever
  needed; re-fetch the `.env` from `39c7eaf2` into ENV ONLY if a live proof
  needs it.

**Next session: paste THIS file + `docs/M17-REPORT.md` +
`docs/IDENTITY-BUILD-PLAN.md`, then pick:** step 9 (Allocations) · B1
manager-on-behalf-of · D16 · the `clients=0` decision · `UpdateAccountHandler`
+ migration 010 (D20 + gateway config plane).
