# WHAT IS BUILT · WHAT IS LEFT · MT5 PARITY · REPO COMPARISON
### Post-M4 status, re-verified by running the code (2026-09-11)

Baseline for all "before" numbers: `MASTER-MIND-MAP.md` + `STATUS-INVENTORY.csv` (written pre-M0).
Current numbers: verified in this workspace — **274/274 tests pass, 6/6 proofs green,
362/362 symbols + 20/20 groups round-trip field-identical.**

---

## 1. WHAT IS BUILT (verified by execution, not by reading)

### Stage 1 — MT5 install & cluster → N/A (you chose Path B: reimplement, not install MT5)
Your *equivalents* of what Stage 1 gives MT5:
| Piece | Status |
|---|---|
| Cluster (trade/history/access/backup roles) | ❌ 0% — `infrastructure/cluster/` empty; decision made: modular monolith + process roles, extract later (gateway → datafeed → history → access) |
| Journal / snapshot / backup-failover | ❌ 0% — no WAL, no replay, no backup server equivalent |
| Console/ops entrypoint | ✅ `cli` (typer): `migrate`, `seed`, `status`, `start` work; `backtest`, `sync`, `export`, `import_data` are honest stubs |

### Stage 2 — Admin / manager credentials → was ~15%, now ~70%
| Piece | Status |
|---|---|
| Manager entity + Rights bitmask (from your real `ConfigManagers` export) | ✅ built (M2) |
| First-admin bootstrap, MT5 "login 1000" pattern: password printed once to stdout, Argon2 hash stored | ✅ built (M2) |
| Admin auth | 🟡 static `ADMIN_API_KEY` — manager JWT + role enforcement NOT done |
| `must_change_password` on first login | ❌ stored but not enforced |
| Client auth (JWT login) | ✅ (but hardcoded `SECRET_KEY` at `jwt_handler.py:12` — flagged since the original audit, still open) |
| 2FA, rate limit, IP whitelist, token blacklist | ✅ exist and import (were unreachable pre-M0) |

### Stage 3 — Brokerage configuration → was "models 35–60%, **0% runnable**", now runnable end-to-end
| Piece | Status |
|---|---|
| One DB schema (was 4 competing), 14 tables, alembic 001+002 resolvable | ✅ (M1/M4) |
| Margin level in PERCENT everywhere (MT5 convention) | ✅ (M1) |
| MT5 wire codec: lossless import/export, quarantine for unmodelled fields | ✅ 362/362 + 20/20 (M1, re-verified) |
| Three symbol currencies (`CurrencyBase/Profit/Margin`) modelled | ✅ (M3 — was the root cause of all cross-currency bugs) |
| Config loader (Pydantic, fails loudly on unknown keys) + seeder (7 groups, 5 symbols, holidays, `DEFAULT_COVERAGE`, first admin; idempotent) | ✅ (M2) |
| Admin REST endpoints reading the real DB | ✅ 7 endpoints (M2) |
| ConfigCache hot path reachable, loaded at startup | ✅ (M2/M4) |
| **Field parity vs real MT5** | 🟡 symbols ~45/121 fields, groups ~19+/44, group symbol overrides 12/65, commissions have tiers now (M3) — wire stays lossless because unmodelled fields quarantine and re-export byte-identical |
| Spread / markup / pricing engine | ❌ **0% — no pricing module anywhere** (MT5 has Spreads + markups; rabbittrix has `fx-pricing`) |
| Per-day swap rates `SwapRate{Sun..Sat}`, EOD schedule | ❌ not modelled |
| Leverage **tiers** (volume-banded margin rates) | ❌ documented gap (no reference group uses them; `MarginBreakdown` can carry them) |
| Data feeds | 🟡 mock feed (tick_size bug fixed M3); LP feed still `NotImplementedError` |
| LP gateways config (`ConfigGateways` with Translates/Symbols/Groups) | ❌ 0% config plane; execution stub only (see Stage 4) |

### Stage 4 — Routing / A-B book / matching → was ~20% and nothing ran, now B-Book executes end to end
| Piece | Status |
|---|---|
| Full order path: `POST /api/v1/trade/orders` → risk (6 checks, per-account lock) → `OrderApproved` → orchestrator → router → fill → deal → position → margin recompute | ✅ **PROVEN** (M4 proof, 13 steps, real SQL repositories) |
| B-Book matching engine: fills at correct spread side, slippage refusal, pendings rest & activate on ticks, cancel/replace loses queue | ✅ 27 unit tests |
| A-Book: routes, attempts send, **refuses rather than fakes** in strict mode (no LP connected) | ✅ honest stub |
| Routing: priority rules, wildcards, NOP thresholds 70% warn / 85% auto-hedge / 95% block, **works with empty rule table** (default destination — fixed M4) | ✅ |
| Coverage account tracks broker exposure (client long ⇒ broker short −0.10) | ✅ |
| Stop-out: margin call → stop out → closes **worst loss first** → books realised PnL to balance → recovery via released margin | ✅ hand-worked e2e test (40.2% → 19.2% → 38.4%) |
| Event chain in causal order: created → approved → routed → deal; risk events on own channels (5 event-type bugs fixed M4) | ✅ |
| Commission charged at fill, stacking rules + volume tiers (was: always 0, first-rule-only) | ✅ (M3) |
| 4-stage MT5 margin pipeline (Basic → Conversion ask/bid → Rate 8+8 → Aggregation hedging/netting), reproduces MT5's published examples **to the cent**, 0.5s/100k-calls budget kept | ✅ (M3, 37 tests) |
| UnitOfWork atomicity (shared session, was unenterable `TypeError`) | ✅ proven (M3) |
| A-Book **real** LP (Centroid Bridge / FIX) | ❌ stub only |
| ECN / CLOB (price-time priority, order book, MT5 ECN matching rules, providers, activation timeout) | ❌ ~5% (models exist unused) |
| MT5 routing action taxonomy (delay ms/ticks, clear SLTP, reject-with-reason, requote, confirm@request/market, cancel) + condition taxonomy (24 request types, deviation-in-points, placed-by-expert, comment masks) | ❌ basic modes only |
| NOP 100% force-close tier; client risk profiling (TOXIC/PROFITABLE/RETAIL/PRO) | ❌ spec'd in research, never built |
| Auto-hedge execution at 85% (exposure tracked, nothing hedges) | ❌ |
| Dealer workflow: queue service + router exist; requote/confirm UI path, timer-wheel 30s timeout | 🟡 ~50%, no UI |

### Cross-cutting
| Area | Before M0 | Now |
|---|---|---|
| Imports | 93/180 modules | **187/187** + CI import gate |
| Tests | 0 ran (10 collection errors) | **274 pass / 0 fail**, 17 test files, incl. 1 hypothesis property-stress file |
| Proofs | none | 6 green (round-trip, currencies, UoW, margin, seed, order-executes) |
| DB | 4 conflicting schemas | 1 schema, 2 migrations, SQLite proofs / PostgreSQL target |
| Hot path | ConfigCache unreachable | loaded at startup, used by trading stack |
| Cold path (ClickHouse) | config exists | deferred (compose service present, unused) |
| Networking | FastAPI+WS on paper | API boots with real trading plane (`test_startup_wires_a_real_trading_plane`) |
| TLS / certificates | ❌ | ❌ 0% — M5 via reverse proxy |
| Docker / deploy | compose w/o app service, no Dockerfile | **unchanged — this is M5** (Kafka+Zookeeper still in compose, unused) |
| Observability | structured logging | + margin perf benchmark; no metrics/tracing/journal |
| Secrets | hardcoded JWT key + admin default | **still hardcoded** (`jwt_handler.py:12` verified today) + public-repo credential leak |
| Swap | worker broken import | imports; **deliberately not wired** (booking twice worse than late) — nothing charges swap today |

---

## 2. COMPARISON VS REAL MT5 (feature parity matrix)

| MT5 capability | You | Note |
|---|---|---|
| Config wire format compatibility | 🟢 **100% lossless** | 362/362 symbols, 20/20 groups re-export field-identical — *no open-source repo has this* |
| Symbol config (121 fields) | 🟡 ~45 modelled | rest quarantined losslessly; missing: IE*/RE*, StopsLevel/FreezeLevel, per-day swaps, SpreadDiffBalance |
| Group config (44 + Commissions + 65-field overrides) | 🟡 ~19 + tiers + 12/65 | enough to run; not enough to *be* MT5 |
| Margin engine (4-stage, hedging/netting, percent) | 🟢 ~95% | only leverage tiers missing |
| Account types (real/demo/preliminary/coverage/contest + manager/dealer) | 🟢 enum + coverage working | contest logic not exercised |
| Managers/rights/bitmask | 🟡 entity+bootstrap | enforcement partial |
| Routing engine (actions/conditions/dealers/ECN entry) | 🟡 ~30% | NOP thresholds ✅; MT5 taxonomy ❌ |
| B-Book internalisation | 🟢 working | MT5 does this via group/routing too |
| A-Book via gateways (`MT5APIGateway64.dll`, Translates) | 🔴 stub | Centroid Bridge docs ready in repo |
| ECN matching (depth-driven, providers, activation timeouts) | 🔴 ~5% | MT5 hosts ECN on history server |
| Trade server topology (trade/history/access/backup, failover witness) | 🔴 single process | decision: process roles later |
| History server (ticks/bars storage, `history/EU/EURUSD/2026.hsc` sharding, news, Live Updates) | 🔴 mock feed only | ClickHouse planned as equivalent |
| Datafeeds (`MetaTrader5Feeder64.exe` etc.) | 🔴 mock | |
| Backup server (real-time + daily + SQL export to 6 DBs) | 🔴 none | needs journal+snapshot first |
| Swap charging (per-day rates, 3-day swap, SwapRate*) | 🔴 modelled partially, not charged | |
| Dealer intervention (requote/confirm, colour tickets) | 🟡 queue only | |
| Plugins / Reports / Automations DLLs | 🔴 0% | deferred |
| Manager API surface | 🟡 your FastAPI manager routers vs MT5's 124-endpoint REST (mtapi-docs pack) | shapes aligned, coverage partial |
| Admin GUI (MT5 Administrator) | 🔴 none | deferred (Theia) |
| Client terminal | 🔴 none | deferred |

**Honest summary vs MT5:** you have a *runnable vertical slice* of the MT5 trade-server
semantics — config in, order in, position out, margin/stop-out correct to the cent — with
byte-perfect MT5 config compatibility. You do **not** have: the server topology, history/tick
storage, real gateways/feeds, ECN, swaps, dealer ops, or any UI. MT5 is ~25 years of C++;
the slice you have is the part every competitor repo lacks.

---

## 3. COMPARISON VS THE OPEN-SOURCE REPOS (updated post-M4)

| | **You (now)** | rabbittrix | nautilus_trader | matching-core | hft-clob-core | tfrmma/oms |
|---|---|---|---|---|---|---|
| Functional size | 209 py files | ~50 rs | 23 crates | ~30 rs | 8 crates | ~25 files |
| Runs today | ✅ **verified** | ✅ | ✅ | ✅ | ✅ | ✅ |
| Tests | ✅ 274 + 6 proofs | ✅ | ✅ high | ✅ high | ✅ + proptest | ✅ ~1:2 ratio |
| CI | 🟡 import gate only | ✅ | ✅ full | — | ✅ | ✅ |
| Dockerfile / deploy | ❌ **M5** | — | ✅ | — | ✅ | — |
| Matching engine | ✅ B-Book internalising (deliberate; not CLOB) | ✅ 232-LOC book | ✅ full | ✅ 5 book variants | ✅ HFT CLOB | — |
| LP gateway | 🟡 honest stub | ✅ fx-lp | ✅ adapters | — | ✅ gateway | ✅ sor |
| Journal / snapshot / recovery | ❌ | — | ✅ event_store | ✅ journal+snapshot | — | — |
| Pricing / spread / markup module | ❌ | ✅ fx-pricing | ✅ | — | — | — |
| Margin: 2-layer (fast local + authoritative) | 🟡 Layer 1 only | — | ✅ | ✅ | ✅ | ✅ margin_monitor |
| **Broker domain semantics** (groups-as-rules, A/B book, coverage, stop-out, MT5 margin, wire compat) | 🟢 **unique — none of them have it** | ❌ 0 hits | ❌ | ❌ | ❌ | 🟡 margin/risk only |
| Property / fuzz tests | 🟡 1 hypothesis file | — | ✅ | — | ✅ | — |
| Tail-latency benchmarks | 🟡 margin budget 0.5s/100k | — | ✅ | ✅ 4 benches | ✅ BENCH.md discipline | — |

**What changed since the mind-map's §8:** the two columns that were your shame — *"Runs
today: ❌"* and *"Matching engine / LP gateway: none"* — are fixed. The consistent signal
before was *"they are smaller and they run"*; now you run too, and you carry domain
semantics none of them carry.

**What to steal from each, in order of usefulness to you now:**
1. **tfrmma `margin_monitor.hpp`** — Layer-2 authoritative reconciliation (your docstring claims it, code doesn't have it) + `notional_gate.hpp` (extract NOP limits from the router into a testable gate).
2. **rabbittrix `fx-pricing`** — spread/markup/risk-adjuster as its own module; your Stage-3.8 zero.
3. **matching-core `journal.rs` + `snapshot.rs`** — the crash-recovery story you must build on Path B (MT5's backup server does this for real brokers).
4. **nautilus `event_store` ≠ `persistence`** — journal is not the database; also their PyO3 stub-drift machinery for your eventual Rust hot path.
5. **hft-clob-core `BENCH.md`** — seeded LCG, synthetic clock, p50/p99/p99.9 only; adopt the discipline before the performance work.

---

## 4. WHAT IS LEFT — prioritized

### P0 — Security (before anything else, ~½ day)
1. Rotate the **15 plaintext server passwords + live JWT** leaked in the public repo; make it private; rewrite history.
2. `SECRET_KEY` → env, fail-hard (`jwt_handler.py:12`); same for `ADMIN_API_KEY` default; fix the test that asserts the default.

### P1 — M5: deployment ("starts on a machine that isn't yours", ~1 day)
Dockerfile (multi-stage, non-root) · `api` service in compose with postgres/redis healthchecks · delete Kafka+Zookeeper · `.env.example` · TLS via Caddy/Traefik · GitHub Actions lint→typecheck→test→build · Makefile `test-e2e`/`--cov` fixes.
**Gate:** clean VM → `make setup-dev` → `curl https://localhost/health` healthy with real DB+Redis checks.

### P2 — M4 debt queue (correctness before features)
1. `volume_min`/`volume_step` lost on DB round trip (codec scaled-`*Ext` handling) — **most consequential**; limits aren't enforced from DB
2. Margin **reservation** column + release on fill/reject (race across Redis nodes; safe single-node)
3. Netting branch: book realised PnL (hedging is correct)
4. Delete one of two margin monitors (`risk_worker.py` is the unwired duplicate)
5. Wire `swap_worker` into `build_trading_stack` (nothing charges swap today) + per-day `SwapRate{Sun..Sat}` + 3-day swap
6. `on_event` → FastAPI lifespan handlers

### P3 — Feature gaps in MT5-parity order (each is its own milestone-sized)
1. **Pricing/spread/markup module** (Stage 3.8 — zero today; every real order flows through it)
2. Manager JWT + roles enforcement, `must_change_password`
3. Routing taxonomy: MT5 actions (delay, clear SLTP, reject-with-reason, requote, confirm, cancel) + conditions (deviation-in-points, placed-by-expert, day-of-week, comment masks) + NOP 100% force-close + client risk profiles
4. Real A-Book: Centroid Bridge adapter (docs in repo) or FIX; gateway config plane (`ConfigGateways` shape)
5. Journal + snapshot + replay (crash recovery; prerequisite for backup/failover)
6. History plane: tick/bar storage (ClickHouse cold path, `PARTITION BY toYYYYMM` + symbol bucketing), real datafeed connector
7. Leverage tiers; symbol field coverage (IE*/RE*, StopsLevel/FreezeLevel); group field coverage
8. Auto-hedge execution at 85% trigger (coverage exposure already tracked)
9. Process roles (`broker/{trade,history,access,worker}.py` entrypoints, `$BROKER_HOME` layout) — the clustering precursor
10. ECN/CLOB, dealer UI, admin GUI, client terminal, reporting, intelligence — deferred by your own instruction, correctly

### The one-line answer
**Built:** a running, tested, MT5-wire-compatible broker core — config plane, risk maths to
the cent, B-Book order execution end-to-end, honest A-Book refusal, stop-out that books
losses. **Left:** deployment (M5), six known debts, security remediation, then the pricing
module and routing/LP depth — everything else was deferred by design and remains deferred.