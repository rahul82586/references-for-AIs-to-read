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
| **The working engine (M0–M10 + D1/D2 fix)** | `github.com/rahul82586/references-for-AIs-to-read` → `qwe-agen-broker-platform-backend/work/bp/` | ✅ pushed 2026-09-11 16:10 UTC. Local working tree `work/bp` is **1 commit ahead** (`c168564`, the D1+D2 fix) — *not yet pushed* |
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
| **M11** | — | ❌ **NEVER GENERATED.** Both attempts returned *"The current content is empty, please regenerate."* | — | — |

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
4. ✅ **FIXED 2026-09-12** — `accounts.margin_level` was persisted, served, and never written *(full write-up: `work/bp/docs/D1-D2-FIX-REPORT.md`)*. Measured after a real fill: `margin_used=107.978, equity=9999, margin_level=0` — should be **9260.22**. `RiskEngine.calculate_margin_level` puts the value in a `MarginSnapshot`; nothing assigns `account.margin_level`, and `Account.recompute_margin_level()` is never called on the trading path. Consequences: **(a)** `router.py:203` feeds the stale 0 into the MT5 routing context, and because it is `Decimal('0')` not `None`, M8's "missing context ⇒ don't match" guard does *not* fire — `MARGIN_LEVEL` conditions compare against zero and silently divert/reject flow; **(b)** `/api/v1/account/info`, manager `AccountGet` and the admin list all report 0. Stop-out itself is safe (it uses the snapshot) — which is why 422 tests pass.
5. ✅ **FIXED 2026-09-12** — `/api/v1/account/info` was unreachable **five** independent ways *(D2)*. `account_info_query_handler` is never registered (`di_providers.py:142` returns `None`), and the route wraps the handler in `except Exception: pass`, so it always serves the JWT-snapshot fallback. The correct maths in `application/queries/get_account_info.py:47` is unreachable.
6. **A-Book does not complete a trade.** `FixLiquidityGateway` now returns a real FILLED report, but `ExecutionOrchestrator._execute_a_book` still only sets PLACED + publishes `OrderRouted`. No deal, no position, no margin release. *An A-Book destination is not yet a trade.* ← **strongest M11 candidate**
7. No FIX drop-copy (35=Z) / EOD reconciliation ⇒ a `FixTimeout` leaves hedge state unknown with nothing to resolve against.
8. `QuickFixSession` has never talked to a real LP (untested surface = the callback marshalling).
9. 🟠 **`cli migrate` cannot run on SQLite** *(D3)* — migration 001 emits PG-only `DEFAULT '{}'::jsonb`. The M5 JSONB *type* compile hook doesn't cover `server_default` text. SQLite dev must use `DatabaseManager.create_tables()`; `make setup-dev` therefore needs a DB server.
10. **m1–m4 proof scripts are absent from the repo** (`m1_proof_roundtrip`, `m2_proof_seed`, `m3_proof_currencies`, `m3_proof_uow`, `m3_proof_margin`, `m4_proof_order_executes`). Round-trip rebuilt as `work/verify/verify_roundtrip.py` → **392/392 byte-identical**. The margin proofs are the regression net for the M3 maths and should be rebuilt.

### P2 — correctness gaps carried forward
11. Post-trade valuation (equity loop, position PnL) still reads **raw** ticks; only the pre-trade path is client-priced (M7 gap #1, still open).
12. SL/TP: no trailing stops, no modify endpoint (`TradeAction.SLTP` / `PositionModify` not exposed), no restart-rearm test.
13. Swap: per-day `SwapRate{Sun..Sat}` table not modelled, holiday doubling not applied, `REOPEN_*` modes unimplemented, no server-level swap control.
14. Stale margin reservations: a node crash between approval and terminal state strands a hold. Needs an ops sweep for stale PLACED orders.
15. `counts_fn` reads ConfigCache, not the DB ⇒ count-based routing rules can be stale in a multi-worker deployment.
16. `CreateAccountHandler` / `CreateClientHandler` / `CreateSymbolHandler` don't exist — admin `set-password` is the interim provisioning path. No investor (read-only) password.
17. OMS still missing: idempotency keys, partial fills, FOK/IOC, self-trade prevention, **audit journal**.
18. RMS still missing: Layer-2 authoritative margin reconciliation (tfrmma `margin_monitor`), leverage **tiers**, NOP 100% force-close, client risk profiles (TOXIC/PROFITABLE/RETAIL/PRO), auto-hedge *execution* at 85% (exposure is tracked, nothing hedges), standalone notional gate, fat-finger check.

### P3 — structural / deferred by decision
19. Journal + snapshot + replay (crash recovery; prerequisite for backup/failover). *Steal from `matching-core/journal.rs` + `snapshot.rs`.*
20. History plane: tick/bar storage (ClickHouse cold path, `PARTITION BY toYYYYMM`), real datafeed connector. `LPTickFeed` is still `NotImplementedError`.
21. Process roles → cluster (`broker/{trade,history,access,worker}.py`, `$BROKER_HOME`). Decision: **modular monolith + process roles; extract later** (gateway → datafeed → history → access; trade last).
22. Dealer terminal/sessions (requote, confirm, dealer mods with audit + balance recalc, 30s timer-wheel), ECN/CLOB (~5%, models exist unused), admin GUI, client terminal, reporting.
23. `docker build` has never run (no daemon in the agent workspace); CI only activates when `bp` is a repo root.
24. WS feed subscribes at startup only; DOM/`stream_book` has no production consumer.

---

## 5. Decisions already made — do not re-litigate

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

```bash
cd work/bp
export PYTHONPATH=$PWD
export BROKER_MT5_FIXTURES=<repo>/mt5-format-structure      # UTF-16 JSON, read as-is
# the fail-hard secrets gate refuses to boot without these:
export SECRET_KEY=$(python3 -c "import secrets;print(secrets.token_hex(32))")
export ADMIN_API_KEY=$(python3 -c "import secrets;print(secrets.token_hex(24))")

python3 -m pytest tests -q                                  # expect 436 passed
python3 -m ruff check --select E9,F63,F7,F82 .              # expect clean
python3 scripts/m8_proof_routing.py                         # 18/18
python3 scripts/m9_proof_sltp_expiration.py                 # 14/14
python3 scripts/m10_proof_adapters.py                       # 19/19

# credential-free, no Neon/Upstash needed - SQLite + in-process bus + mock feed.
# Boots the API and trades over real HTTP. 15/15.
bash <workspace>/work/verify/local_e2e.sh
# rebuilt M1 wire proof - 392/392 records byte-identical across 6 sections
python3 <workspace>/work/verify/verify_roundtrip.py <repo>/mt5-format-structure

./scripts/m5_proof_cloud.sh                                 # 33/33 (needs Neon + Upstash)
./scripts/m10_proof_cloud_ws.sh                             # 14/14 (needs live WS)
```

⚠️ **`cli migrate` (alembic) cannot run on SQLite** — migration 001 emits PG-only
`DEFAULT '{}'::jsonb`. On SQLite use `DatabaseManager.create_tables()` (that is what
`local_e2e.sh` does). See D3 in `VERIFICATION-FINDINGS.md`.

⚠️ **m1–m4 proof scripts are absent from the repo** (`m1_proof_roundtrip`,
`m2_proof_seed`, `m3_proof_currencies`, `m3_proof_uow`, `m3_proof_margin`,
`m4_proof_order_executes`). The round-trip one is rebuilt above; the margin /
currency / UoW / order-executes proofs still need rebuilding — they are the
regression net for the M3 maths.

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
| `work/verify/local_e2e.sh` | **New gate.** `m5_proof_cloud.sh`'s twin on SQLite + in-process bus + mock feed — boots the API and trades over real HTTP, **no credentials needed**. 15/15 |
| `work/verify/verify_roundtrip.py` | Rebuilt M1 wire proof. 392/392 records byte-identical across 6 sections |
| `work/bp/scripts/patch_d1_d2_margin_level.py` · `patch_d1_routing_and_tests.py` | The fix, as idempotent patch scripts (project convention) |
| `work/bp/tests/integration/test_d1_margin_level_routing.py` | 3 tests through the real stack |
| `work/bp/tests/unit/api/test_d2_account_info_contract.py` | 9 tests pinning the route contract |
| `recovered/docs/` · `recovered/transcript/` | 12 reports + transcripts extracted from the dead session |

**Local git:** `work/bp` is at `c46fa27`, **2 commits ahead of GitHub `a054423c`** and not
pushed. Push before starting anything else — that is rule 1 of §7, and it is the only
reason M10 survived the last session death.

**The pattern to keep hunting:** D1, and all five layers of D2, are one class — *a value
computed correctly somewhere and served stale from somewhere else.* The durable defence is
what was applied here: derive at the point of consumption, and make "not wired" a loud 503
rather than a plausible-looking number.
