# Forex Broker Platform — PROJECT STATE & CONTEXT ANCHOR v8

**Written:** 2026-09-14 (session 7, at the end of M18 = surface completion)
**Supersedes:** `PROJECT-STATE-v7.md` (written earlier THIS session, at M17).
Read `M18-REPORT.md` for this milestone, `M17-REPORT.md` for F8/F9 + step 8,
`docs/ENDPOINT-CATALOG.md` for **the master surface map** (all 231 MT5 Web API
commands dispositioned), and `IDENTITY-BUILD-PLAN.md` for step 9. v5 §3/§5,
v6 §6 and v7 §2 decisions all still hold.

**Sources:** GitHub @ `14100ca` (this session's start) · session-6 transcript
(the F8/F9 spec) · gates re-run before and after · live Neon re-probed ·
the full MT5 Web API + mtapi-124 corpus extracted and mapped.

---

## 0. Verified current state — everything below was RUN

Tree: `qwe-agen-broker-platform-backend/work/bp` · migrations **001→009** ·
**93 OpenAPI paths / 116 operations** (34 of them honest 501 skeletons).

| Gate | Result (2026-09-14, end of M18) |
|---|---|
| `pytest tests` | **835 passed / 0 failed / 0 skipped** (740 at session start; +95) |
| `ruff E9,F63,F7,F82` | clean |
| `p1_proof_migration_009` / `p1_proof_identity` | 24/24 · 59/59 |
| `p1_proof_account_creation` / `p1_proof_manager_creation` | 72/72 · 80/80 |
| `p1_proof_read_plane` | 55/55 |
| **`p1_proof_surface_completion` (NEW)** | **41/41** — walks the whole route table; bans 200-empty-while-unwired |
| `f8f9_proof_live_position_get` | 10/10 on live Neon (run at M17; needs DATABASE_URL) |
| round-trip / m2 / m3 margin / m8 / m9 / m10 / m11 | 392/392 · ✅ · ✅ · 18/18 · 14/14 · 19/19 · 39/39 |
| m4 | weekend-skip (correct) |

## 0b. Live Neon (probed at session start; UNCHANGED since — nothing wrote)

Head `009_identity_plane` · accounts 67 cols/45 rows (rights=0 all 45) ·
clients **0 rows** · groups 58/7 · managers 24/1 · login_counters EMPTY ·
31 open positions (24 NULL price_current) · 37 IN/9 OUT deals · 9 breaks OPEN
· bars=0 · **D16 was 24/45 at probe time — the fix is committed but the live
repair happens at the first priced sweep after market open** (Monday): run
`cli sync` or boot the server once, then re-measure with the v6/v7 query
(`p.account_login::text = a.login` join) — expect **0/45**.
`.env` at `39c7eaf2` still fetchable; rotation remains a user action.
**The session workspace itself is credential-free** (sweep verified 0 secret
values; raw captures deleted; transcripts redacted).

## 1. Ledger delta (M17 + M18, this session)

* **M17** (`07c0c27`, `69915d7`, `14100ca`): F8/F9 rebuilt to session 6's
  recorded design + live-proven · step 8 read plane (find_page on six repos,
  8 queries, 10 endpoints, client_fields.yaml, 52 paths) · D20 found
  (`orders.price_order` Optional-on-entity vs NOT-NULL column — belongs to
  migration 010).
* **M18** (`313cc0c`, `63d90ab`, `755a30c`): **D16 FIXED** (the sweep writes
  positions first and sums what was WRITTEN; MOCK-over-live guard; 9 branch
  tests) · **F1 FIXED** (both client sockets fed; risk events subscribed;
  the leak rule pinned) · **F6 fixed** (empty dirs deleted, duplicate
  webhooks/ deleted, legacy shadowed reads retired, duplicate
  SqlClientRepository killed — one home per capability) · **17 wired
  endpoints** (manager DealGet/OrderGet/SymbolGet/GroupGet/ServerTime;
  routing/ticks/risk×3/calculators×4/balance/holidays/check-password/
  online/client-accounts/sessions) · **34 honest skeletons** (501 + roadmap
  + right-gated) · **p1_proof_surface_completion** in CI.

**Defect ledger:** D16 ✅FIXED (live repair pending market open) · F1 ✅ ·
F6 ✅ · F8/F9 ✅ (M17) · **D20 🟠 open** (migration 010) · D17 ❌ open
(sandbox portability; bit twice more this session) · D4 🟡 (public leak —
user action; workspace itself clean) · F2 ❌ (client/manager-plane
fabrication — Tier 3 #7) · F4 ❌ (history swallows errors) · F7 ❌ (UI
hardcodes an admin key — needs B1's manager logins) · F3/F5 ✅ (earlier).

## 2. Decisions this session — do not re-litigate

v7 §2 all holds (bare arrays + X-Total-Count; reading-rights gating; the F9
ticket rule platform-wide; status value+name; shadowed-then-retired legacy
reads; schema gates). Added by M18 (full list in M18-REPORT §6):
RIGHT_ACCOUNTANT gates funds · RIGHT_ACC_ONLINE gates the online list on top
of ACC_READ · calculators price at the CURRENT market or refuse · the sweep
preserves stored profit when it cannot revalue · balance endpoint takes only
the four human operation types · one SqlClientRepository (identity_repository.py)
· **a skeleton is deleted in the same commit that builds it for real**.

## 3. Session-death protocol (amended in v7 §3 — unchanged, enforced)

`.git` AND installed packages do not survive turn boundaries → bundle after
EVERY commit (`work/patches/repo-full-history.bundle`, gitignored, survives
as a plain file) · push at every milestone, never web upload · write
`docs/Mn-REPORT.md` early · update THIS anchor · prefer `scripts/patch_*.py`
· D17 runtime-path rule · the chat input filter blocks secret-shaped strings
— credentials live in ENV at run time, never in files or chat.

## 4. What is open, in priority order

**P0 user actions:** ① push the four M17/M18 commits (or clone the bundle) —
CI will run both new proofs for the first time · ② after Monday open: one
`cli sync`, then re-measure D16 → expect 0/45 · ③ rotate/purge `39c7eaf2`
when it matters · ④ the `clients=0` backfill decision.

**P1 milestone queue (Tier 3, from ENDPOINT-CATALOG Part 4):**
① **B1 manager-on-behalf-of** (target login on /manager/* writes + group-scope
authorisation + the audit hook; unlocks the dealer UI and the requote/confirm
skeletons) · ② **UpdateAccountHandler + migration 010** (D20, mt5_gateways,
mt5_datafeeds, leverage list, symbol-group tree; unlocks 4 skeleton families)
· ③ **symbol CRUD** after the 121-field/quarantine decision · ④ **audit
journal** (compliance; MT5 logs every manager query/export/filter) ·
⑤ **history plane** (bars=0; charts/tick history skeletons) · ⑥ trade-
modification family (corrections, reopen, close-all, UserBalanceCheck) ·
⑦ **F2** client-auth rebuild (kill the fabrication) · ⑧ step 9 allocations.

**P1 money & correctness (unchanged):** margin_free/margin_level four-writer
design decision · stop-out never live-fired · A-Book close never unwinds the
hedge · 9 breaks OPEN, no resolution workflow · WS keepalive ~60 s · 19/25
pre-trade checks · commission types/charge modes.

**P2/P3:** unchanged from v4 §5 items 16–28.

## 5. Reproducing the gates

```bash
cd qwe-agen-broker-platform-backend/work/bp
pip install -e ".[dev]"                      # EVERY turn - packages don't persist
export PYTHONPATH=$PWD
# decode fixtures (UTF-16LE -> UTF-8) exactly as in v7 §5
export BROKER_MT5_FIXTURES=<decoded dir>
export SECRET_KEY=$(python3 -c "import secrets;print(secrets.token_hex(32))")
export ADMIN_API_KEY=$(python3 -c "import secrets;print(secrets.token_hex(24))")
python3 -m pytest tests -q                          # 835 passed
python3 -m ruff check --select E9,F63,F7,F82 .      # clean
python3 scripts/p1_proof_surface_completion.py      # 41/41
python3 scripts/p1_proof_read_plane.py              # 55/55
python3 scripts/p1_proof_account_creation.py        # 72/72
python3 scripts/p1_proof_manager_creation.py        # 80/80
python3 scripts/p1_proof_identity.py                # 59/59
python3 scripts/p1_proof_migration_009.py           # 24/24
python3 scripts/m1_proof_roundtrip_all_sections.py  # 392/392
# live (ENV-only credentials): DATABASE_URL=... python3 scripts/f8f9_proof_live_position_get.py
```

## 6. Session 7 handover state

* **On GitHub:** through `14100ca` (M17). **To push:** `313cc0c` (D16) ·
  `63d90ab` (cleanup+F1) · `755a30c` (M18 surface) · this docs commit.
* Verified bundle: `work/patches/repo-full-history.bundle` — clone it, set
  origin, `git push origin main`. CI runs all seven P1-style proofs.
* The master map lives at `docs/ENDPOINT-CATALOG.md` — every future endpoint
  decision starts there, not from memory.

**Next session: paste THIS file + `docs/M18-REPORT.md` +
`docs/ENDPOINT-CATALOG.md`, then pick from §4 — the recommended first move
is B1 (manager-on-behalf-of), with the D16 live re-measurement the moment
the market is open.**
