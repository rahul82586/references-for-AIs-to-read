# Forex Broker Platform — PROJECT STATE & CONTEXT ANCHOR

**Reconstructed:** 2026-09-12
**Source:** SingleFile capture of Qwen session `da26741e-ba21-4cff-aa23-99cbf237b598`
(saved 2026-09-11 21:44 IST) + GitHub `rahul82586/references-for-AIs-to-read` @ `a054423c`.

> **Purpose of this file:** every Qwen session on this project has died from context
> exhaustion. Paste this file first in any new session and the whole state transfers.
> It is the single anchor. Keep it updated at the end of every milestone.

---

## 0. Where the code actually lives (verified 2026-09-12)

| Thing | Location | State |
|---|---|---|
| **The working engine (M0–M11 + D1/D2/D6 + proofs)** | `github.com/rahul82586/references-for-AIs-to-read` → `qwe-agen-broker-platform-backend/work/bp/` | ✅ pushed 2026-09-11 16:10 UTC. Local working tree `work/bp` is **5 commits ahead** (`aaff07e`) — *not yet pushed* |
| Milestone reports | same repo → `qwe-agen-broker-platform-backend/Reports/` (M0–M4, ANALYSIS, MASTER-MIND-MAP) and `work/bp/docs/` (M5–M10) | ✅ |
| Reference corpus | same repo root: `Single_MetaTrader5Administrator/`, `mt5 sdk single md file/`, `mt5-format-structure/`, `mtapi-docs/`, `single_centroid_bridge_md_files/`, `chat-and-reference-files/`, `code files/` | ✅ |
| Original hand-built V1 | `refs/qwencode/broker-platform` (180 py files) | ⚠️ pristine/broken — 93/180 modules imported, 0 tests ran. Superseded. |
| trade-server prototype | `refs/trade-server` | ✅ working sidecar; now consumed by M10's `TradeServerTickFeed` |

**Nothing was lost.** The two dead sessions produced no orphaned work — the M10 state was
pushed to GitHub before the session died.

---

## 1. What the three versions are

| | What | Verdict |
|---|---|---|
| **V1** — original build | Chat-assisted (Gemini et al.) DDD/hexagonal/CQRS broker platform, 180 py files | Domain models good, everything touching them broken. Never ran. |
| **V2** — trade-server | FastAPI + `MetaTrader5` python pkg → real MT5 terminal, WS tick/book streaming | Working prototype, *not* the broker platform. Repurposed as the M10 data-feed adapter. |
| **V3** — Qwen agent build | V1 taken from pristine → running, milestones M0–M10 | ✅ **This is the project.** 209 → ~250 py files, 422 tests. |

---

## 2. Milestone ledger

| # | Question it answered | Result | Tests | Cloud proof |
|---|---|---|---|---|
| M0 | Does it import? | 93/180 → **187/187**, CI import gate | 0 → ran | — |
| M1 | One schema + MT5 wire codec | 4 competing schemas → 1; lossless import/export with quarantine | — | round-trip 362/362 symbols + 20/20 groups |
| M2 | Config plane runnable | loader + seeder + 7 admin endpoints + ConfigCache hot path | — | — |
| M3 | Risk maths correct | 4-stage MT5 margin pipeline **to the cent**; 3 symbol currencies; commission tiers | — | reproduces MT5's published examples |
| M4 | Does an order execute? | Full path HTTP → risk → route → fill → deal → position → margin; B-Book real, A-Book honest refusal; stop-out books losses | **274** | 6/6 proofs |
| M5 | Does it start on a machine that isn't yours? | Dockerfile (multi-stage, non-root), compose + Caddy TLS, Kafka/ZK deleted, CI, fail-hard secrets, real `/health`, `MARKET_DATA_SOURCE` | **297** | 28/28 on Neon PG 18.6 + Upstash |
| M6 | Is the debt paid? | volume_min/step 10⁴ scaling fixed both directions; netting books realised PnL; margin **reservation** (atomic conditional UPDATE); swap worker rewritten to MT5 spec + wired; **login password verified** (Argon2); lifespan handlers | **326** | 29/29, migrations → 005 |
| M7 | Does the broker earn its spread? | `core/domains/pricing/` — fixed spread + SpreadDiff + SpreadDiffBalance, group-after-symbol, inheritance never zeroes, stale-quote refusal; `quote_provider` at the single fill funnel | **349** | 29/29, migration → 006 |
| M8 | Does a request flow through the routing table like MT5? | `core/domains/execution/routing_mt5.py` — full `EnRouteAction`/`EnRouteCondition` code space, top-down first-match, OR-within/AND-across, non-terminal DELAY/CLEAR, ≤31-char reject reasons, **UNSUPPORTED conditions skip with a warning rather than guess**; live TCTrader rules replay | **374** | 18/18 routing proof, migration → 007 |
| M9 | When the client disconnects, does the server honour the stop? | `SlTpWorker` (closes at **market**, not the trigger level), `ExpirationWorker` (fires on boot for downtime), `OrderReason.SL/TP/SO`, GTD over HTTP, routing position counts 4005/4006 | **384** | 14/14 proof, cloud 33/33 |
| M10 | Real adapters? | `TradeServerTickFeed` (WS + msgpack, Decimal-only, crossed ticks dropped, EOF raises to force backoff) · dependency-free **FIX 4.4** layer (`messages`/`session`/`simulated_session`) · `FixLiquidityGateway` (ClOrdID correlation, ack-grace, silence = UNKNOWN) | **422** | 19/19 adapters, 14/14 cloud-WS, 33/33 regression |
| **D1+D2** | Was `margin_level` ever written? Could `/account/info` answer? | `record_deal` recomputes; the SQL read **and the router** derive it (never trust the column); `/info` + manager `UserGet` adopt the `/positions` 503/500/404 contract with no silent fallback | **436** | local E2E 15/15 · `margin_level` `0.0000` → `9261.68` |
| **Proofs** | Can every claim be re-run? | m1–m4 proofs restored from git history `b324ba9`; `.github/workflows/ci.yml` + `m10_debug_cloud_order.py` recovered from the session capture (never pushed); new `make proofs` entry point | 436 | **13/13 gates green** in ~50 s |
| **D6** | Can a REAL terminal feed the engine? | Two hard-coded 10s staleness literals dropped 497/497 live MT5 ticks and 500'd position valuation. One shared resolver (`quote_freshness.py`), default 60s, `MARKET_DATA_MAX_TICK_AGE_SECONDS`, drops now log at WARNING | **462** | `m11_proof_live_mt5.sh` **15/15** against a real terminal |
| **M11** | Is an A-Book destination a trade? | Four explicit outcomes: FILLED/PARTIAL book the client side through the same path B-Book uses; ACK rests at the LP and keeps its reservation; `FixTimeout` is **neither booked nor rejected** (flagged `HEDGE_STATE_UNKNOWN`); a definite LP refusal rejects via the single funnel. Coverage moves only when nothing was hedged. First partial-fill path in the codebase. | **448** | `m11_proof_a_book` **39/39** · `make proofs` **14/14** |

---

## 3. Architecture as it stands

```
POST /api/v1/trade/orders
  → CreateOrderHandler
  → PreTradeRiskService        (6 checks, per-account asyncio.Lock, margin reservation)
  → OrderApproved
  → ExecutionOrchestrator
  → SmartOrderRouter           MT5 request-policy table (M8) → house rules + NOP 70/85/95% → default
       ├─ B-Book → BookMatchingEngine   (quote_provider = client pricing, M7)
       └─ A-Book → FixLiquidityGateway  (M10) / StubLiquidityGateway (strict: refuses)
  → RecordDealHandler          deal + position + SL/TP carried + margin recompute
  → LiquidationWorker / SlTpWorker / ExpirationWorker / SwapWorker
  → coverage account tracks broker exposure (client long ⇒ broker short)
```

**Composition root:** `application/di/trading_setup.py` (`build_trading_stack`).
**Ports:** `core/ports/interfaces.py` — `ITickFeed`, `ILiquidityGateway`, `IFixSession`, repos.
**Bus:** in-process by default; `RedisEventBus` when `EVENT_BUS=redis` (identical semantics —
this is what makes later clustering additive, not a rewrite).
**Key env:** `MARKET_DATA_SOURCE=mock|trade_server`, `TRADE_SERVER_WS_URL`,
`BROKER_LP_GATEWAY=stub|fix`, `PRICING_MAX_TICK_AGE_SECONDS`, `SWAP_ROLLOVER_HOUR_UTC`,
`BROKER_MT5_FIXTURES` (tests need the UTF-16 export).

**The project's design law, applied consistently:** *refuse rather than fake.* A-Book with no
LP rejects instead of inventing a fill. No price source ⇒ orders refused, not guessed.
Unsupported routing conditions skip with a warning. `FixTimeout` says hedge state is UNKNOWN.
Stale quotes reject. INTEREST swap with no price refuses. **Keep this.**

---

## 4. What is genuinely still missing (consolidated debt, all sources)

### P0 — security
1. 🔴 **`.env` credentials are in public git HISTORY.** HEAD's `.env` is correctly scrubbed (all values empty), but it was committed with live Neon + Upstash values at `39c7eaf2` (16:07 UTC) and only scrubbed at `a054423c` (17:38 UTC). Both commits are public ⇒ rotate both credentials, make the repo private, rewrite history.
2. 🔴 `mt5-format-structure/` holds a real TCTrader-Live export with **15 plaintext server passwords + a live JWT**. Still unrotated since the M4 audit.
3. Manager JWT + rights-bitmask enforcement; `must_change_password` stored but not enforced. Static `ADMIN_API_KEY` is still the admin auth path.

### P1 — the biggest functional hole
4. 🔴 **Nothing revalues open positions at boot, and there is no sync command** *(D9, confirmed 2026-09-12 after a 10-hour shutdown)*. `cli sync` is an honest stub that exits 2 (`infrastructure/cluster/` is empty). Equity, profit, `margin_free` and `margin_level` are only recomputed by `TickMarginPipeline` **on a tick, while the server runs**. So after a restart every account shows its last-computed values until a tick arrives for a symbol it holds — and if that symbol is not subscribed, never. Observed: an account holding an open BTCUSD position still read `equity=100000, profit=0` ten hours later. Meanwhile the MT5 terminal's own book *was* current (the broker keeps it), so the two books silently diverge. **This is the same gap as the missing reconciler (item 11) and should be built with it**: on boot, read positions and revalue; then periodically compare against the venue.
5. ✅ **FIXED (D8b) — the tick pipeline was erasing margin written by a fill.** `TickMarginPipeline` ended each pass with a **full-row** `account_repo.save()` on an account object loaded at the start of that pass, and `Account.update_equity` never touches `margin_used`. So a fill landing between the load and the save had its margin overwritten by the stale snapshot — a lost update. Live signature: `margin_used=0E-8`, `margin_level=999999`, `updated_at == created_at`, with the Deal and Position both present. Worst kind: `margin_used=0` overstates free margin by the whole requirement **and** freezes `margin_level` at the sentinel, so margin-call and stop-out can never fire — the account can run negative with no liquidation. It happens *more* often the more liquid the symbol. Fix: `IAccountRepository.update_valuation()` writes only the columns the pipeline owns (profit, equity, margin_free, margin_level, the five `so_*`), never balance/margin_used/margin_reserved — disjoint write sets, following M6's `reserve_margin` precedent. Capability-probed, so an unreformed repo degrades loudly instead of failing. `account_to_db` also stamps `updated_at` with the write time, not the domain value (that lie is what made the resurrected row hard to see). 7 deterministic tests; verified to fail without the fix.
6. ✅ **FIXED (D8)** — `_execute_a_book` booked against the account instance the dispatcher loaded *before* risk reserved margin; `_on_internal_fill` (B-Book) has always re-read. Now re-reads. **Deliberately has no unit test** — three attempts all passed with the bug present, because the in-memory repo's `release_margin` mutates the stored object and `save` stores by reference. Recorded in the test file; pinned by the live proof.
7. ✅ **FIXED (D6)** — two hard-coded **10.0s** staleness literals (`MarketDataEngine._is_stale` and `RiskEngine._verify_tick_freshness`) silently discarded **497/497 real MT5 ticks**. Now one shared resolver (`core/domains/market_data/quote_freshness.py`), default **60s** matching M7, knob `MARKET_DATA_MAX_TICK_AGE_SECONDS`, drops log at **WARNING**.
8. 🔴 **`RedisEventBus` cannot receive cross-process events on more than one channel** *(D5)*. One `listen()` loop per channel over one shared `self._pubsub`; redis-py PubSub is single-reader, so all but the first die with `readuntil() called while another coroutine is already waiting`. Same-process delivery is unaffected, which is why every test and proof passes. **Silently breaks the multi-process deployment `EVENT_BUS=redis` exists for.** Fix: one shared listen loop dispatching to `_local_handlers`.
9. ~~`accounts.margin_level` persisted, served, never written~~ ✅ **FIXED (D1)**
10. ~~`/api/v1/account/info` unreachable~~ ✅ **FIXED (D2)**
11. ~~**A-Book does not complete a trade.**~~ ✅ **FIXED (M11) and PROVEN LIVE** — real BTCUSD hedges on a real MT5 terminal, both routes, client booked at the terminal's exact price (drift `0E-8`), coverage unchanged.
12. **No FIX drop-copy (35=Z) / EOD reconciliation.** M11 makes a `FixTimeout` break *visible* (`HEDGE_STATE_UNKNOWN` + `reconciliation_required`, margin held) but nothing **resolves** it. Same gap applies to `TradeServerLiquidityGateway`, which has **no idempotency key at all** (trade-server hardcodes `magic`/`comment`, takes no client order id), so it must never retry blind. ← **strongest M12 candidate; build with D9**
13. **No resting-order lifecycle at the LP.** An ACK leaves the order PLACED forever; a later ExecutionReport that fills it is not consumed, and partial-then-complete is not wired.
14. **A-Book fills at the LP's raw price.** M7's group spread transform prices the order for risk and for B-Book fills, but the A-Book booking takes the terminal's price as-is — so a group markup is not earned on A-Book flow. **This is the markup/commission work the user asked for next.**
15. **No A-Book position close.** `TradeServerLiquidityGateway.close_position()` exists and reaches the terminal, but nothing calls it: closing a client A-Book position does not unwind the hedge. The broker stays long/short at the LP forever. **6 live hedges are open on the terminal because of this.**
16. `QuickFixSession` has never talked to a real LP (untested surface = the callback marshalling).
17. `_execute_in_house` (ECN) and `_send_to_dealer` still do not book. ECN remains ~5%.
18. 🟠 **`cli migrate` cannot run on SQLite** *(D3)* — migration 001 emits PG-only `DEFAULT '{}'::jsonb`. The M5 JSONB *type* compile hook doesn't cover `server_default` text. SQLite dev must use `DatabaseManager.create_tables()`; `make setup-dev` therefore needs a DB server.
19. ✅ **RESOLVED 2026-09-12** — the m1–m4 proofs were never lost, only orphaned: they survived in git history at `b324ba9` under the *old* top-level `scripts/`, which HEAD dropped when it reorganised into `work/bp`. Restored verbatim (all 6 pass, including against the D1/D2 changes). Also recovered from the dead session's HTML capture, because they were **never pushed at all**: `.github/workflows/ci.yml` (the M5 three-job gate — it exists at no ref in the repo) and `scripts/m10_debug_cloud_order.py`. Both are dotfile/debug paths a GitHub web upload skips. New single entry point: **`make proofs`** → `scripts/run_all_proofs.sh`, 13 gates.

### P2 — correctness gaps carried forward
20. Post-trade valuation (equity loop, position PnL) still reads **raw** ticks; only the pre-trade path is client-priced (M7 gap #1, still open).
21. SL/TP: no trailing stops, no modify endpoint (`TradeAction.SLTP` / `PositionModify` not exposed), no restart-rearm test.
22. Swap: per-day `SwapRate{Sun..Sat}` table not modelled, holiday doubling not applied, `REOPEN_*` modes unimplemented, no server-level swap control.
23. Stale margin reservations: a node crash between approval and terminal state strands a hold. Needs an ops sweep for stale PLACED orders.
24. `counts_fn` reads ConfigCache, not the DB ⇒ count-based routing rules can be stale in a multi-worker deployment.
25. `CreateAccountHandler` / `CreateClientHandler` / `CreateSymbolHandler` don't exist — admin `set-password` is the interim provisioning path. No investor (read-only) password.
26. OMS still missing: idempotency keys, FOK/IOC, self-trade prevention, **audit journal**. (Partial fills now exist on the A-Book path as of M11 — `_apply_deal_to_account` takes a volume and the reservation releases proportionally; B-Book still fills complete-or-rests.)
27. RMS still missing: Layer-2 authoritative margin reconciliation (tfrmma `margin_monitor`), leverage **tiers**, NOP 100% force-close, client risk profiles (TOXIC/PROFITABLE/RETAIL/PRO), auto-hedge *execution* at 85% (exposure is tracked, nothing hedges), standalone notional gate, fat-finger check.

### P3 — structural / deferred by decision
28. Journal + snapshot + replay (crash recovery; prerequisite for backup/failover). *Steal from `matching-core/journal.rs` + `snapshot.rs`.*
29. History plane: tick/bar storage (ClickHouse cold path, `PARTITION BY toYYYYMM`), real datafeed connector. `LPTickFeed` is still `NotImplementedError`.
30. Process roles → cluster (`broker/{trade,history,access,worker}.py`, `$BROKER_HOME`). Decision: **modular monolith + process roles; extract later** (gateway → datafeed → history → access; trade last).
31. Dealer terminal/sessions (requote, confirm, dealer mods with audit + balance recalc, 30s timer-wheel), ECN/CLOB (~5%, models exist unused), admin GUI, client terminal, reporting.
32. `docker build` has never run (no daemon in the agent workspace); CI only activates when `bp` is a repo root.
33. WS feed subscribes at startup only; DOM/`stream_book` has no production consumer.

---

## 5. Decisions already made — do not re-litigate

- **`symbols.volume_min` / `volume_step` / `volume_max` / `volume_limit` COLUMNS store MT5's wire-scaled integers** (10⁴), so `volume_min = 100` in the DB means **0.01 lots**. This is deliberate, not the M6 scaling bug: the columns hold wire literals so re-export stays byte-identical, and `db_to_symbol` unscales them through `record_to_domain`. Read through the repository the domain value is `0.01`. **Do not "fix" the column.**

- **Path B:** reimplement MT5 semantics in Python; do **not** install MT5.
- **Schema authority = the MT5 SDK**, not mtapi-docs. mtapi-docs is kept only for (a) REST ergonomics, (b) the 124-endpoint coverage checklist, (c) client-side docs if ever bridging through mtapi.io.
- Payload field names should become **exact MT5 names** via Pydantic `serialization_alias` (current schemas are snake_case — known drift, not yet fixed).
- Unknown wire fields → **quarantine pass-through** (`mt5_extra`), never dropped. This is why round-trip stays byte-identical at ~45/121 symbol fields.
- Margin level is in **PERCENT** everywhere (MT5 convention).
- MT5 day index is **0 = Sunday** (wire-verified: EURUSD `Swap3Day=5` pairs with `SwapRateFriday=3.0`).
- MT5 volume fields are **integers scaled 10⁴** (`*Ext` siblings at 10⁸).
- Clustering: additive later, not a rewrite. No microservice split now.
- Deferred by explicit user decision: ECN/CLOB, UIs, intelligence/, load testing, KYC/backoffice.

**What to steal next, in order:** tfrmma `margin_monitor.hpp` (Layer-2) + `notional_gate.hpp`
· rabbittrix `fx-pricing` (risk adjuster) · matching-core `journal.rs`+`snapshot.rs` ·
nautilus `event_store ≠ persistence` · hft-clob-core `BENCH.md` discipline (seeded LCG,
synthetic clock, p50/p99/p99.9 only).

---

## 6. Reproducing the gates

**One command runs everything: `make proofs`** (≈50 s, no credentials). For single gates:

```bash
cd work/bp
export PYTHONPATH=$PWD
# the DECODED (UTF-8) tree - the raw export is UTF-16 and m3_proof_currencies dies on it
export BROKER_MT5_FIXTURES=<repo>/qwe-agen-broker-platform-backend/work/decoded/mt5-format-structure
# the fail-hard secrets gate (M5) refuses to boot without these:
export SECRET_KEY=$(python3 -c "import secrets;print(secrets.token_hex(32))")
export ADMIN_API_KEY=$(python3 -c "import secrets;print(secrets.token_hex(24))")

python3 -m pytest tests -q                                  # 436 passed
python3 -m ruff check --select E9,F63,F7,F82 .              # clean
python3 scripts/m1_proof_roundtrip.py "$PWD"                # 362/362 + 20/20
python3 scripts/m1_proof_roundtrip_all_sections.py "$BROKER_MT5_FIXTURES"   # 392/392
python3 scripts/m2_proof_seed.py "$PWD"                     # 7 groups / 5 symbols, idempotent
python3 scripts/m3_proof_currencies.py "$PWD"               # 3 currencies over 362
python3 scripts/m3_proof_uow.py "$PWD"                      # one session, atomic rollback
python3 scripts/m3_proof_margin.py "$PWD"                   # MT5's examples to the cent
python3 scripts/m4_proof_order_executes.py "$PWD"           # 13 steps, real SQL repos
python3 scripts/m8_proof_routing.py                         # 18/18
python3 scripts/m9_proof_sltp_expiration.py                 # 14/14
python3 scripts/m10_proof_adapters.py                       # 19/19
bash    scripts/local_e2e.sh                                # 15/15, live HTTP trade

./scripts/m5_proof_cloud.sh                                 # 33/33 (needs Neon + Upstash)
./scripts/m10_proof_cloud_ws.sh                             # 14/14 (needs live WS)
```

⚠️ **`cli migrate` (alembic) cannot run on SQLite** — migration 001 emits PG-only
`DEFAULT '{}'::jsonb`. On SQLite use `DatabaseManager.create_tables()` (that is what
`local_e2e.sh` does). See D3 in `VERIFICATION-FINDINGS.md`.

✅ **All of the above is now one command: `make proofs`** (or
`bash scripts/run_all_proofs.sh`). 13 gates, no credentials, ~50 s:

```
ruff E9,F63,F7,F82 · pytest (436) · m1_proof_roundtrip (362/362 + 20/20)
m1_roundtrip_all_sections (392/392) · m2_proof_seed · m3_proof_currencies (362/362)
m3_proof_uow · m3_proof_margin · m4_proof_order_executes (13 steps)
m8_proof_routing (18/18) · m9_proof_sltp_expiration (14/14)
m10_proof_adapters (19/19) · local_e2e (15/15, live HTTP trade)
```

⚠️ The M1–M4 proofs need the **decoded (UTF-8)** fixture tree —
`m3_proof_currencies` reads them as `utf-8-sig` and dies on the raw export's UTF-16
BOM. `run_all_proofs.sh` defaults `BROKER_MT5_FIXTURES` to
`../decoded/mt5-format-structure` and fails loudly if it is absent. Decode with
`scripts/decode_mt5_json.py`.

⚠️ `.github/workflows/ci.yml` only runs if `bp` is the **repository root** — GitHub
ignores workflows in subdirectories. It is currently nested at
`qwe-agen-broker-platform-backend/work/bp/`, so CI is inert. Either promote `bp` to
its own repo (recommended — it is the product) or add `defaults.run.working-directory`
at the root. The file's own header says this.

---

## 7. Session-death protocol (why this file exists)

Every session on this project has died the same way: agent mode generates ~500 tool calls and
~2.8 MB of transcript per session, the history exceeds the window, and the UI starts returning
*"The current content is empty, please regenerate."*

Rules to stop it recurring:
1. **Commit + push to GitHub at the end of every milestone.** This is the only durable memory. It worked — M10 survived.
2. Write the milestone report to `work/bp/docs/Mn-REPORT.md` **before** the session gets long.
3. Update this `PROJECT-STATE.md` ledger row at the same time.
4. Start new sessions from a **fresh chat** with this file pasted, not by continuing a long one.
5. Prefer `python3 scripts/mN_patch_*.py` one-shot patch scripts over long inline heredocs — they land as reviewable files and survive capture.

---

## 8. Artifacts produced by independent verification (2026-09-12)

| File | What it is |
|---|---|
| `VERIFICATION-FINDINGS.md` | Gate reproduction, the four defects (D1–D4), and what is confirmed still open |
| `work/bp/docs/D1-D2-FIX-REPORT.md` | The D1+D2 fix, in the project's milestone-report style |
| `work/bp/scripts/run_all_proofs.sh` | **`make proofs`** — every gate in one command. **14/14** |
| `work/bp/docs/M11-REPORT.md` | M11: the A-Book completion, in milestone-report style |
| `work/bp/scripts/m11_proof_a_book.py` | **39 checks** across 7 outcome classes, through the real stack |
| `work/bp/scripts/m11_proof_live_mt5.sh` | **The real thing.** Real MT5 terminal → trade-server → tunnel → Neon + Upstash → HTTP fill at the live ask. **15/15** |
| `work/bp/scripts/live_trade_multisymbol.py` | Trades a list of `SYMBOL:VOLUME` pairs live. Verified **EURUSD @ 1.15998 + BTCUSD @ 77,310.83**, margin reconciling to the cent across two calc modes |
| `work/bp/core/domains/market_data/quote_freshness.py` | One staleness resolver shared by ingestion and valuation (D6) |
| `work/bp/tests/unit/domains/market_data/test_d6_quote_freshness.py` | 14 tests |
| `work/bp/scripts/m11_patch_a_book_completion.py` | The M11 change, as an idempotent patch script |
| `work/bp/tests/integration/test_m11_a_book_completion.py` | 12 tests |
| `work/bp/scripts/local_e2e.sh` | **New gate.** `m5_proof_cloud.sh`'s twin on SQLite + in-process bus + mock feed — boots the API and trades over real HTTP, **no credentials needed**. 15/15 |
| `work/bp/scripts/m1_proof_roundtrip_all_sections.py` | Extends the M1 proof from 2 sections to 6 → **392/392 byte-identical** |
| `work/bp/scripts/{m1..m4}_proof_*.py` · `decode_mt5_json.py` · `verify_ci_gate.sh` | Restored verbatim from git history `b324ba9` |
| `work/bp/.github/workflows/ci.yml` | Recovered from the session capture — was never pushed at any ref |
| `work/bp/scripts/patch_d1_d2_margin_level.py` · `patch_d1_routing_and_tests.py` | The fix, as idempotent patch scripts (project convention) |
| `work/bp/tests/integration/test_d1_margin_level_routing.py` | 3 tests through the real stack |
| `work/bp/tests/unit/api/test_d2_account_info_contract.py` | 9 tests pinning the route contract |
| `recovered/docs/` · `recovered/transcript/` | 12 reports + transcripts extracted from the dead session |

`work/verify/` holds the first drafts of `local_e2e.sh` and the round-trip proof; the
canonical copies now live in `work/bp/scripts/` so they are committed and cannot be
orphaned again.

**Local git:** `work/bp` carries the D1/D2, restored-proofs, M11, D6, live-hedge and
D8b work on top of GitHub `a054423c`, and is **not pushed**.

⚠️ **`.git` does not survive in this workspace** - the snapshot excludes it, so local
commit history is lost between sessions even though every source file persists. A
full-diff backup is kept at `work/patches/github-a054423_to_local.patch` (3.7 MB,
`git apply`-able against a fresh clone). **Push to GitHub; do not rely on local git.** Push before starting anything else — that is rule 1 of §7, and it is the only
reason M10 survived the last session death. **Push with `git push`, not the GitHub web
upload:** the web upload is what silently dropped `.github/` and the dotfiles this time.

**The pattern to keep hunting:** D1, and all five layers of D2, are one class — *a value
computed correctly somewhere and served stale from somewhere else.* The durable defence is
what was applied here: derive at the point of consumption, and make "not wired" a loud 503
rather than a plausible-looking number.
