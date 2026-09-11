# Forex Broker Platform — Full Context Recovery & Knowledge Base

**Recovered:** 2026-09-11
**Sources:** (1) SingleFile capture of the dead Qwen session `9da0d236-7fa9-44e6-a16b-12ff61d85e78`
(31 MB Drive file → parsed into `transcript/`), (2) GitHub repo
`rahul82586/references-for-AIs-to-read` (cloned to `/home/user/refs`, 36 MB).

---

## 1. Verification result — the GitHub `bp` tree IS the final M4 state ✅

Run fresh in this workspace on 2026-09-11 (Python 3.11, deps installed incl. asyncpg,
pyotp, hypothesis, clickhouse-driver, aiosqlite):

| Check | Expected (M4 report) | Actual | Status |
|---|---|---|---|
| `pytest tests` | 274 passed / 0 failed | **274 passed / 0 failed** (18s) | ✅ |
| M4 proof (`m4_proof_order_executes.py`, 13 steps) | PASSED | **PASSED** | ✅ |
| MT5 round-trip (`m1_proof_roundtrip.py`) | 362/362 symbols, 20/20 groups field-identical | **362/362, 20/20** | ✅ |
| M3 margin proof (`m3_proof_margin.py`) | PASSED | **PASSED** | ✅ |

Env needed: `PYTHONPATH=<bp>` and `BROKER_MT5_FIXTURES=/home/user/refs/mt5-format-structure`
(fixtures are UTF-16 JSON; `scripts/decode_mt5_json.py` handles decoding).

---

## 2. The three versions of the project

| Version | Where | What it is | State |
|---|---|---|---|
| **V1 — Original build** | `refs/qwencode/broker-platform` (180 py files) | Chat-assisted build (Gemini et al., logged in `latest_chat-MT5 Broker Platform Development (1).md` + `chat-Digital Communication Trends`). DDD/hexagonal/CQRS design, MT5-parity domain enrichment (Accounts→Instruments→OMS), Manager API, Paths A/B/C | **Pristine/broken**: doesn't import (93/180 modules), tests 0-run. ANALYSIS.md verdict: *"domain models ~good, everything that touches them ~broken"* — the earlier "25/25 endpoints PASS / 75% complete" claims were of an older snapshot |
| **V2 — trade-server prototype** | `refs/trade-server` | Separate track: FastAPI + `MetaTrader5` python pkg connecting to a REAL MT5 account as a client, WS tick streaming, client dashboard | Working prototype, not the broker platform |
| **V3 — Qwen agent build (M0–M4)** | `refs/qwe-agen-broker-platform-backend/bp` (209 py files) + `Reports/` + `scripts/` | V1 taken from pristine → running: M0 imports, M1 one schema + MT5 codec, M2 config plane, M3 risk maths, M4 order execution | **✅ VERIFIED WORKING — 274/274, all proofs green** |

`bp` = `qwencode/broker-platform` + M0–M4 additions: `infrastructure/mt5/` (codec, wire,
fieldmap, enums), `infrastructure/config/` (loader, seeder), `core/domains/market_data/margin.py`
(the 4-stage MT5 margin engine), `engines/book_matching_engine.py`, `gateways/stub_liquidity_gateway.py`,
`messaging/inprocess_event_bus.py`, `application/di/trading_setup.py` (composition root),
`feed_access.py`, manager/account models + repositories, migration 002, 10 new test files.

Reproduce from pristine: `./scripts/m0_run_all.sh` (21 numbered steps + CI gate + proofs).

---

## 3. The reference corpus (all read/skimmed)

| Dir | Contents | Role |
|---|---|---|
| `Single_MetaTrader5Administrator/` | Official MT5 Admin guide as MD. **Platform-Setup.md (2.1 MB)** = the authority: Margin-Calculation/{Basic, Retail-Forex-CFD-Futures—Hedging, —Netting, Stock-Exchange}, Leverages (tier examples), Groups, Accounts, Managers, Gateways, Network-cluster, Platform-Components/Installation | Domain authority — margin 4-stage pipeline, group rule engine, server topology |
| `mt5 sdk single md file/` | Include.md (1.1 MB C++ headers) + 21 formatted MDs: Manager-API, Server-API, Gateway-API, Report-API, Web-API, Database-Interfaces, Configuration-Interfaces, Structures, List-of-Events/Hooks, Return-Codes, SQL-Export | IMTUser/IMTAccount/IMTGroup/IMTConSymbol structures → domain model parity |
| `mt5-format-structure/` | **Real TCTrader-Live server export** (UTF-16 JSON): Symbols (362), Groups (20), Subscriptions, Automation, Clients, Data Feeds, Gateways, Holidays, Network Cluster, Plugins, Reports, Routing, Security | The round-trip fixtures (`BROKER_MT5_FIXTURES`). ⚠️ contains leaked secrets |
| `mtapi-docs/` | MT5 Manager REST API offline pack (mng5.mtapi.io): 124 endpoints, 128 schemas, swagger.json, QUICKSTART (Connect→token→OrderSend→WS) | Target shape for our Manager API |
| `single_centroid_bridge_md_files/` | Centroid Bridge manual (24 files): Hub, Makers, Takers, Risk accounts, Trade Copier, Giveup, Filtration pool, Stale prices, Monitoring, API | The future real A-Book LP bridge reference |
| `chat-and-reference-files/` | `opencode_summery.md` (research: broker-killer math bugs, A/B-book definitions, NOP triggers 70/85/95/100%, two-layer margin, battle-test scenarios: EURUSD $10/pip/lot, USDJPY ~$6.67...), `links-from-opencode-chat-file.md` (~90 curated links), raw opencode session (553 KB), Digital Communication Trends chats, `qwen-chat-Document Analysis Request` (MT5 native B-book RMS/dealer workflow), `api_test_results.md` (V1's 25-endpoint report) | Research + prior-session knowledge |
| `code files/` | 9 implementation docs from V1: groups/accounts, symbols, OMS, market-data & margin loop, risk & liquidation, CQRS handlers, Manager API, subscriptions router, **MT5 Storage Architecture vs. Our Best Approach** | V1's design rationale |
| `qwe-agen-broker-platform-backend/Reports/` | ANALYSIS.md, MASTER-MIND-MAP.md (blocker chain B1–B24, milestones M0–M5, repo comparisons), SHORT-ANSWERS.md (rabbittrix verdict: latency reference NOT broker reference; MT5 server topology: trade/history/access/backup; clustering decision: modular monolith + process roles, don't split now), STATUS-INVENTORY.csv, M0–M4 reports | The distilled engineering record |

Key open-source references established: `tfrmma/oms` (two-layer margin, conservatism rule),
`nautilus_trader` (position-reducing orders skip margin check; Python-first/Rust-hot-path),
`llc-993/matching-core` (journal+snapshot discipline; its MarginEngine is `todo!()`),
`joaquinbejar/hft-clob-core` (tokio confined to gateway; deterministic replay),
`FTHTrading/Broker-Dealer` (broker semantics), `rabbittrix` (crate boundaries, `venue`
concept, fx-pricing, liquidity-graph only).

---

## 4. Domain knowledge core (what the system implements)

**MT5 margin = 4-stage pipeline** (not a formula): ① Basic — Forex `vol×contract/leverage`
(no price term!), CFD `×price`, CFD-leverage `×price/leverage`, Futures `vol×initial_margin`;
② Conversion — margin ccy → deposit ccy, **ask for buys, bid for sells**; ③ Rate — ×8 initial
+ 8 maintenance multipliers, zero maintenance inherits initial; ④ Aggregation — same direction
weighted-avg price, opposite → hedged margin, pendings always at initial.
Verified examples: `1×100000/100 = EUR 1000`, `×1.2790 = 1279 USD`, `×1.15 = 1470.85`,
`2315.00+770.60 = 3085.60`. **Gap: leverage TIERS not implemented** (no ref group uses them).

**Three symbol currencies** (`CurrencyBase/CurrencyProfit/CurrencyMargin`) — name-heuristic
gets only 109/362 right; the discarded fields were the root cause of all cross-currency bugs.

**Margin level in PERCENT** (MT5 convention: MarginCall 50/30, demo\Standard 10/1).
Equity = balance + credit + profit. Stop-out closes **worst loss first**, books realised PnL
to balance, recovery via margin denominator (closing doesn't improve equity).

**Execution flow (M4, working):** `POST /api/v1/trade/orders` → CreateOrderHandler →
PreTradeRiskService (6 checks, per-account asyncio.Lock, publish_events=False then persist
then publish OrderApproved) → ExecutionOrchestrator (subscribed to ORDER_APPROVED) →
SmartOrderRouter (rules + NOP thresholds 70% warn / 85% auto-hedge / 95% block, default
destination fallback) → B-Book: BookMatchingEngine (fills at ask/bid, slippage, rests
pendings, activates on ticks) / A-Book: StubLiquidityGateway (strict mode REJECTS, never
fakes) → RecordDealHandler (deal + position + margin recompute via RiskEngine) →
LiquidationWorker on margin events → coverage account tracks broker exposure (client long
⇒ broker short).

**MT5 server topology** (target for clustering later): Trade (config owner, auth, trade
records), History (gateways+datafeeds live HERE, ticks/bars/news, ECN matching), Access
(proxy/firewall/cache/failover witness), Backup (failover + SQL export). Everything hot =
flat `.dat`+`.idx` memory-loaded; history sharded `history/EU/EURUSD/2026.hsc`. Decision
taken: **modular monolith with process roles** (`broker/{trade,history,access,worker}.py`
entrypoints), state under `$BROKER_HOME`, one config dir per role, daily-rotating logs.
Extract services only when scaling demands: gateway → datafeed → history → access; trade last.

---

## 5. State at session end + next steps

**Done:** Stages 1–3 of the 4-stage plan complete; Stage 4 (routing/A-B-book/matching)
complete for B-Book. `cli migrate && cli seed && cli start` stands up a server that takes
an order and holds a position. 274 tests, 6 proofs, 187/187 modules import.

**M5 (proposed, never started):** Dockerfile (multi-stage, non-root), compose `api` service
+ postgres/redis healthchecks, delete Kafka+Zookeeper, `.env.example` + fail-hard secrets,
TLS (Caddy/Traefik), GitHub Actions (lint→typecheck→test→build), Makefile `test-e2e`/`--cov`
fixes. Gate: clean VM `git clone && cp .env.example .env && make setup-dev` → `curl
https://localhost/health` healthy with real DB+Redis checks.

**M4 debt queue (report §5), in priority order:**
1. `volume_min`/`volume_step` lost on DB round trip (codec scaled `*Ext` handling) — **most consequential**
2. Margin reservation column (race across Redis nodes; safe single-node today)
3. Netting branch doesn't book realised PnL (hedging correct)
4. Delete one of two margin monitors (`TickMarginPipeline` wired; `risk_worker.py` redundant)
5. Wire `swap_worker` into `build_trading_stack` (nothing charges swap today)
6. `api/main.py` deprecated `on_event` → lifespan handlers

**Deferred by user decision:** intelligence/, reports, FIX, gRPC/cluster, ECN/CLOB, real LP
(Centroid Bridge docs ready), ClickHouse, dealer UI, client terminal, load testing, KYC/backoffice.

## 6. ⚠️ OPEN SECURITY ISSUES (flagged in ANALYSIS.md §2 + M4 report §7 — STILL UNFIXED)

1. **Public repo leaks:** `mt5-format-structure/` holds a real TCTrader-Live export with
   **15 plaintext server passwords + a live JWT** → rotate credentials, make repo private,
   rewrite git history (force-push ≠ un-clone).
2. V1 hardcoded secrets: `api/auth/jwt_handler.py:12` SECRET_KEY, `admin_dependencies.py:10`
   ADMIN_API_KEY default (and `test_api.py:77` asserts against the default).
3. Correct pattern already in place: seeder prints first admin password once to stdout,
   stores Argon2 hash — keep.

---

## 7. Workspace layout (this session)

```
/home/user/
├── refs/                          # GitHub clone (read-only reference)
└── forex_engine/
    ├── qwen_session.html          # raw Drive capture (31 MB)
    ├── transcript/                # full transcript, user msgs, file lists
    ├── reconstructed/             # 9 reports recovered from the capture
    ├── RECOVERY-SUMMARY.md        # this file (supersedes earlier version)
    └── extract_reports.py
```