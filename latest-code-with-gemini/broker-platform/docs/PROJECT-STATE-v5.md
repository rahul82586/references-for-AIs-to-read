# Forex Broker Platform — PROJECT STATE & CONTEXT ANCHOR v5

**Written:** 2026-09-13 (session 5, at the end of M15 steps 0–4)
**Supersedes:** `PROJECT-STATE-v4.md` (session 4) — which is committed at
`work/bp/docs/PROJECT-STATE-v4.md` together with `ENDPOINTS.md`,
`ACCOUNT-GROUP-CREATION-SPEC.md` and the recovered `IDENTITY-BUILD-PLAN.md`.
Read those four for the full endpoint contract, the MT5 account/group field
model, and the remaining identity-plane build order. This file is the delta plus
everything a fresh session needs to start cold.

**Sources:** GitHub `rahul82586/references-for-AIs-to-read` @ `38dc30b0` ·
Drive captures of Qwen sessions 2/3/4 (all three parsed to text this session) ·
gates re-run, live infra re-probed, **live Neon schema read back column-by-column**.

---

## 0. Verified current state — everything below was RUN, not read

Tree: `qwe-agen-broker-platform-backend/work/bp` — **~350 py files**, migrations **001→009**.

| Gate | Result (2026-09-13, session 5) |
|---|---|
| `pytest tests` (fixtures decoded) | **670 passed, 0 failed, 0 skipped** (was 621; +49 identity/API tests) |
| `ruff --select E9,F63,F7,F82` | clean |
| `m1_proof_roundtrip_all_sections` | **392/392** byte-identical |
| `m2_proof_seed` | pass (first admin now built via declared fields; wire shape unchanged) |
| `m8_proof_routing` / `m9` / `m10` / `m11` | 18/18 · 14/14 · 19/19 · pass |
| `m4_proof_order_executes` | SKIP — weekend. Correct. |
| **`p1_proof_migration_009.py` (NEW)** | **18/18** — fresh SQLite: upgrade→introspect→re-upgrade idempotent→downgrade clean |
| **`p1_proof_identity.py` (NEW)** | **59/59** — the nine real TCTrader-Live managers as fixture; presets equal login 1000 (110 bits) and 208011 (39 bits) bit for bit; require_right enforced over HTTP; created group re-exports wire-valid |

## 0b. Live infrastructure — probed 2026-09-13 (session 5)

| Thing | State |
|---|---|
| Neon PostgreSQL | ✅ 18.6 reachable · **alembic head `009_identity_plane`** · 18 tables (incl. `login_counters`) |
| Upstash Redis | ✅ (session 4 probe; not re-pinged this session) |
| ngrok tunnel / MT5 terminal | not re-probed this session (was ✅ 09-12: connected, login 50080) |
| Neon data | 45 accounts · 31 open positions (24 with `price_current` NULL) · 37 IN / 9 OUT deals · 50 orders · `bars` 0 · **9 breaks OPEN** · **D16 still live: 24/45 accounts where equity−balance ≠ Σ position profit** · `login_counters` EMPTY · `accounts.rights` 0 everywhere · 1 manager (login 1000, seeded) |

### 🔴 The discovery that reframed session 5: the live DB was AHEAD of the repo

Neon already carried migration **`009_identity_plane`** (accounts 67 cols,
clients 32, login_counters) while the repo had only 001–008. The dead session 4
applied it in its final, unrendered moments; its source died with the sandbox.
Session 5 **read the live schema back from `information_schema` (every column,
default, index — including the partial index `WHERE (rights & 65536) <> 0` =
USER_RIGHT_TECHNICAL) and reconstructed the migration DDL-faithful**, same
revision id, idempotent, SQLite-safe. Neon: no-op. Fresh DB: converges on
Neon's exact shape (proof 18/18).

**Deliberate limit:** migration 009 is DDL-only. The SQLAlchemy models do NOT
declare the new columns yet, because `account_to_db()` builds a fresh model per
save — a declared column with no mapper support is a full-row save waiting to
blank it (D8b/D15 class). Models + entities + mappers gain the fields together
in plan step 5.

## 1. Milestone ledger (M0 → M15 + D1 → D17)

M0 imports · M1 one schema + lossless MT5 codec (quarantine) · M2 config plane ·
M3 margin to the cent + 3 symbol currencies + commission tiers · M4 order
executes e2e · M5 deployability (fail-hard secrets, real /health, CI) · M6 debt
(volume 10⁴, netting PnL, margin RESERVATION, swap worker, Argon2) · M7 pricing
(SpreadDiff/SpreadDiffBalance, stale-quote refusal) · M8 MT5 routing table
(top-down first-match, 18/18 on the real rules) · M9 SL/TP + expiration workers ·
M10 real adapters (trade-server WS + dependency-free FIX 4.4) · M11 A-Book as a
trade (4 explicit outcomes, FixTimeout = HEDGE_STATE_UNKNOWN) · M12
reconciliation breaks · M13 A-Book markup MT5-shaped (client booked at CLIENT
price, venue at SOURCE price; Translates semantics) · M14 Redis single-reader
bus + three client trade routes · D15-era: first real close (D12–D15 + 41/41
cloud proof) · **M15 (this session): identity & config plane steps 0–4 — see
`docs/M15-REPORT.md`**.

**Defect ledger:** D1✅ D2✅ D3❌OPEN (cli migrate SQLite — 001's `'{}'::jsonb`;
009 itself is SQLite-safe) · D4🟡 (vector closed: `.gitignore` restored &
tracked; **the leak at `39c7eaf2` + the export's 15 plaintext passwords + live
JWT still need rotation/purge — user action**) · D5✅ D6✅ D8✅ D8b✅ D9✅ D10✅
D11✅ D12✅ D13✅ D14✅ D15✅ · **D16❌OPEN** (valuation sweep writes equity, never
positions — 24/45 Neon accounts inconsistent RIGHT NOW) · **D17❌OPEN**
(`$ARENA_WORKSPACE` hard-coded in e2e scripts) · F1❌ (dead /ws/stream +
/ws/user) · **F2❌** (`get_current_user` fabricates account 100001 — the
ADMIN plane is now fabrication-free via require_right; client/manager planes
still exposed) · **F3✅FIXED** (groups router mounted, authed, extended) ·
F4❌ (history swallows errors) · **F5✅FIXED** (pyproject declares argon2-cffi,
pyotp, asyncpg, aiosqlite, hypothesis, httpx) · F6❌ (plane naming drift) ·
F7❌ (Theia api.ts hardcodes an admin key; must move to manager logins —
require_right now makes that possible) · F8/F9❌ (PositionGet `[]` + ticket=0).

## 2. What M15 built (steps 0–4 of IDENTITY-BUILD-PLAN)

1. **Rights as named data.** `core/domains/identity/rights.py`:
   `ManagerRightsMask` (immutable; names ↔ 128×"0"/"1" wire array ↔ the three
   43-bit DB words; packing pinned against the storage layer by test; strict on
   names, tolerant on positions — the live admins carry 1s at unassigned 68/69
   and that survives every round trip) + `UserRight` IntFlag (18 IMTUser bits,
   `from_flags` refuses unknown bits) + registries loaded from
   `config/identity/*.yaml` **generated from the SDK** by
   `scripts/dev/extract_identity_yaml.py` (97 manager rights; RIGHT_LAST=128 is
   a never-grantable sentinel).
2. **Presets decoded from the live server.** `role_presets.py` +
   `role_presets_builtin.yaml`: Administrator = login 1000's exact 110-bit
   array; Manager = login 208011's exact 39 bits; Dealer/Accountant/RiskManager
   = Manager + {31,37,42}/{24}/{32}. Save As/Delete per the guide (builtins
   untouchable; saved presets are YAML data). A preset is a LABEL: only
   `apply_preset` moves bits.
3. **The one group-type rule.** `group_type.py :: derive_group_type` = MT5
   Group-Types.md verbatim (case-SENSITIVE substring on the full path; REAL is
   the fallback; documented ambiguity order manager>contest>demo>coverage>
   preliminary>real). `mt5/enums.account_type_from_group_path` now delegates
   (it used to be prefix-based/case-insensitive and disagreed with MT5 on the
   guide's own examples). `validate_group_name` lists every violation at once.
4. **The password rule.** `password_policy.py`: 4 classes, min = group
   `AuthPasswordMin` clamped 8..16, max 16, every violation reported,
   `secrets`-based generator, empty/corrupt hash = refusal.
5. **ManagerAccount declares its fields** (dynamic attaching deleted;
   ManagerRole demoted to cosmetic; helpers: has_right/apply_preset/
   in_group_scope with MT5 `!managers*,*` first-match semantics/
   effective_report_window strictest-wins). Mappers mask-aware both directions;
   seeder wire shape unchanged.
6. **`require_right()` — authorisation exists for the first time.** Bootstrap
   admin key = full access; manager JWT (`is_manager` claim) = the mask decides;
   unknown/inactive → 401 never fabricated (anti-F2); `must_change_password`
   → 403 (enforced anywhere for the first time since M2); `allowed_ips` →
   enforced (MT_RET_AUTH_MANAGER_IPBLOCK); unwired repo → 503. Right resolved
   at import: a typo crashes the boot.
7. **Group CRUD mounted (F3 fixed).** POST `/api/v1/admin/groups` (+`/create`
   alias), PUT/DELETE `/{name:path}`, GET `/schema` — router-level
   `require_right("RIGHT_CFG_GROUPS")`, mounted BEFORE admin_router. Create:
   derived type, contradiction refused (exception: contest-on-demo), margin
   pair validated, duplicate refused. Update: partial, NO_CHANGES refused
   (10025), currency change refused while accounts exist. Delete: refused while
   accounts exist **or emptiness unverifiable**. Ports gained
   `delete_by_name`, declared `find_all`, `count_by_group_name`.
8. **`/schema` = the UI lever.** `config/schemas/group_fields.yaml` (all 44 MT5
   ConfigGroups fields + ours; tab/gating-right/modelled/writable per field),
   enums expanded from domain code at read time.
9. **Repo hygiene restored & tracked:** `.gitignore` · `bp/.env.example` ·
   `.github/workflows/ci.yml` (ruff → full pytest with decoded fixtures →
   offline proofs incl. both P1 gates) · F5 deps · the four session-4 anchor
   docs committed under `work/bp/docs/`.

## 3. Architecture (unchanged) + the design law

Order path: trade routes → CreateOrderHandler → PreTradeRiskService (6 checks,
per-account lock, atomic reservation) → ExecutionOrchestrator →
SmartOrderRouter (MT5 request-policy table; NOP 70/85/95%) → B-Book
(BookMatchingEngine at the CLIENT price) or A-Book (ILiquidityGateway:
stub-refuses / FIX 4.4 / trade_server Centroid-pattern; client booked at client
price, venue at source price, difference = markup; floor = quote+slippage;
`BROKER_ABOOK_IMPROVEMENT=client|broker`) → RecordDealHandler → workers
(Liquidation/SlTp/Expiration/Swap/TickMarginPipeline) → ValuationService +
Reconciliation via `cli sync` → coverage account tracks broker exposure.

**Design law: refuse rather than fake.** No LP ⇒ reject. No price ⇒ refuse.
Stale quote ⇒ reject. FixTimeout ⇒ UNKNOWN. Not-wired ⇒ loud 503. A 200 always
means it really happened. **Recurring defect class (D1,D2,D8b,D12–D16,F8): a
value computed correctly in one place and served/stored from another. Durable
defence: ONE WRITER PER NUMBER, derive at consumption, disjoint column sets,
not-wired = 503.**

MT5 config model (authoritative: `docs/MT5-CONFIG-MODEL.md`): feed/gateway →
symbol mapping → Translates (RENAMES; markup fields exist but this broker marks
up through **group SpreadDiff**) → GROUP settings (where the money is) →
ROUTING rules decide A/B-book (group appears only as condition 1001; a gateway
is reached as a DEALER in a routing rule). Conventions locked: margin level in
PERCENT · day index 0=Sunday · volumes 10⁴ (Ext 10⁸) · unknown wire fields
quarantine into `mt5_extra` · `symbols.volume_min` column holds the wire
literal (never "fix" the 100).

## 4. What is open, in priority order

**P0 — security/user actions**
1. Rotate Neon/Upstash/SECRET_KEY/ADMIN_API_KEY (still fetchable at
   `39c7eaf2`); ask GitHub to purge or go private; the `mt5-format-structure`
   export still holds 15 plaintext server passwords + a live JWT.
2. Manager JWT + rights rollout beyond the groups plane: existing admin reads
   still use the static key; `must_change_password` enforced in require_right
   but not yet at login; client/manager planes still run on `get_current_user`
   (F2 fabrication).

**P1 — identity plane, plan steps 5–9 (`docs/IDENTITY-BUILD-PLAN.md`)**
3. Step 5: entities+mappers+models for the 009 columns (Account gains ~16
   declared fields incl. `rights: UserRight`; the three password fields move
   Client→Account semantically; Group gains ~19) — ATOMICALLY (one writer per
   number; no model column without its mapper).
4. Step 6: `CreateClientHandler` → `CreateAccountHandler`: login allocator on
   `login_counters` (race-safe `UPDATE ... RETURNING`, never MAX+1, never reuse
   a deleted login), password policy, **plaintext returned exactly once**
   (cli-seed pattern), rights mask from the Limits/Account tabs, NULL=inherit
   limits, opening deposit in one transaction with its ledger row.
5. Step 7: `CreateManagerHandler` (refuses unless the account sits in a
   `managers\…` group) + presets API + IP allow-list rollout.
6. Step 8: read queries + `/schema` for account/client/manager (unblocks the
   Theia UI; also B2's `/admin/{orders,deals,positions}` reads).
7. Step 9: Allocations (own table; when the client-terminal story starts).

**P1 — money & correctness (unchanged)**
8. **D16** sweep writes equity, never positions (24/45 Neon accounts wrong now;
   fix = call `SqlPositionRepository.update_valuation` per priced position;
   never sweep MOCK-opened positions against live ticks).
9. **margin_free/margin_level four-writer problem** — needs one owner (design
   decision, not a patch).
10. **F8/F9** PositionGet `[]`+ticket=0 (the UI's only cross-account positions
    read; ~20 lines) · stop-out never live-fired · A-Book close never unwinds
    the hedge (`TradeServerLiquidityGateway.close_position` called by nothing) ·
    no resting-order lifecycle at the LP · 9 reconciliation breaks OPEN, no
    drop-copy/EOD/UNKNOWN-resolution · D17 script portability · D3 · bars=0 ·
    WS keepalive drops every ~60 s · 19 of ~25 MT5 pre-trade checks missing +
    the exchange-style guards (fat finger, throttle, kill switch, self-trade,
    mass cancel) — see session-4 transcript analysis in `docs/ENDPOINTS.md`
    neighbours; commission types/charge modes; gateway config plane
    (mt5_gateways table = migration 010).

**P2/P3** — unchanged from v4 §5 items 16–28 (post-trade client pricing,
trailing stops, per-day swaps, journal/snapshot/replay, history plane, process
roles → cluster, dealer terminal, ECN/CLOB, UIs, docker build never run).

## 5. Decisions already made — do not re-litigate

Path B (reimplement MT5 semantics; do not install MT5) · SDK = schema authority,
mtapi = REST ergonomics + the 124-endpoint checklist · quarantine unknown wire
fields · margin level PERCENT · 0=Sunday · volumes 10⁴ · modular monolith +
process roles later · `BROKER_ABOOK_IMPROVEMENT` default **client** · presets
are DATA, role is a label, the mask is the only truth · group type is DERIVED
from the name (case-sensitive substring), contradictions refused except
contest-on-demo · UI renders forms from `/schema` · plaintext passwords exist
only in the create response · deferred by explicit user decision: ECN/CLOB,
UIs, intelligence/, load testing, KYC/backoffice.

## 6. Reproducing the gates

```bash
cd qwe-agen-broker-platform-backend/work/bp
pip install -e ".[dev]"                      # F5 fixed: this is now sufficient
export PYTHONPATH=$PWD
python3 - <<'EOF'                            # decode fixtures (UTF-16LE -> UTF-8)
import json, pathlib
src = pathlib.Path("../../mt5-format-structure")   # repo-root copy
out = pathlib.Path.home()/"decoded/mt5-format-structure"; out.mkdir(parents=True, exist_ok=True)
for f in sorted(src.glob("*.json")):
    raw=f.read_bytes(); txt=raw.decode("utf-16-le" if raw[:2]==b"\xff\xfe" else "utf-8",errors="replace").lstrip("\ufeff")
    json.loads(txt); (out/f.name).write_text(txt,encoding="utf-8")
EOF
export BROKER_MT5_FIXTURES=~/decoded/mt5-format-structure
export SECRET_KEY=$(python3 -c "import secrets;print(secrets.token_hex(32))")
export ADMIN_API_KEY=$(python3 -c "import secrets;print(secrets.token_hex(24))")
python3 -m pytest tests -q                              # 670 passed
python3 -m ruff check --select E9,F63,F7,F82 .          # clean
python3 scripts/p1_proof_migration_009.py               # 18/18
python3 scripts/p1_proof_identity.py                    # 59/59
python3 scripts/m1_proof_roundtrip_all_sections.py      # 392/392
bash scripts/run_all_proofs.sh                          # still D17: needs $ARENA_WORKSPACE
# live-infra gates: m5_proof_cloud.sh · m10_proof_cloud_ws.sh · d12_proof_cloud_close.sh · m11_proof_live_mt5.sh
```

Regenerate the identity YAMLs after any SDK/export change:
`python3 scripts/dev/extract_identity_yaml.py <repo_root> <decoded_fixtures>` —
then the preset tests decide whether the server's answer changed.

## 7. Session-death protocol (unchanged, enforced)

~500 tool calls / ~2.8 MB transcript kills a session; sessions 2 and 4 died
mid-answer. 1) `git push` at every milestone, **never the web upload** (it lost
CI twice, .gitignore/.env.example, and 14 commits → 1). 2) Write
`docs/Mn-REPORT.md` early. 3) Update THIS anchor and push it. 4) New sessions
start from a fresh chat with this file pasted. 5) Prefer `scripts/patch_*.py`
one-shot idempotent patches over long heredocs. 6) Keep a pushed git bundle
(`work/patches/`). 7) Anything outside the repo is lost — `.git` does not
survive workspace snapshots.

**Session 5 handover state:** all M15 work is committed locally in the clone at
`/home/user/repo` (branch `main`), with a bundle at
`work/patches/repo-full-history.bundle`. The user pushes (credentials never
live in the sandbox). Next session: paste THIS file + `docs/M15-REPORT.md` +
`docs/IDENTITY-BUILD-PLAN.md`, then start at plan step 5.
