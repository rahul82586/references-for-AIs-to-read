# Forex Broker Platform — PROJECT STATE & CONTEXT ANCHOR v4

**Reconstructed:** 2026-09-12 (session 4)
**Sources:** GitHub `rahul82586/references-for-AIs-to-read` @ `38dc30b0` (HEAD, single commit
"Add files via upload", 2026-09-12 19:45 IST) · Drive capture of Qwen session 2
(`da26741e…`, MHTML, saved 11 Sep 21:14 IST) · Drive capture of Qwen session 3
(`64c3e2ce…`, SingleFile, saved 12 Sep 19:46 IST) · **gates re-run, live infra re-probed.**

> Supersedes `Reports/PROJECT-STATE.md` (M10-era), `2-PROJECT-STATE.md` (M10+D1/D2),
> `3-PROJECT-STATE.md` (M11+D6+D9). **No pushed anchor covered M12–M14 / D10–D15** —
> session 3 wrote its update to the workspace root, which is not in the repo. This file closes that.

---

## 0. Verified current state — everything below was RUN, not read

Tree: `qwe-agen-broker-platform-backend/work/bp` — **329 py files**, migrations **001→008**.

| Gate | Result |
|---|---|
| `pytest tests` (fixtures decoded) | **621 passed, 0 failed, 0 skipped** — matches D13–D15's 596+25 |
| `pytest tests` (no `BROKER_MT5_FIXTURES`) | 586 passed / 35 skipped (all skips = fixture path) |
| `ruff --select E9,F63,F7,F82` | **clean** |
| `m1_proof_roundtrip` | **362/362** byte-identical |
| `m1_roundtrip_all_sections` | **392/392** byte-identical (Symbols 362, Groups 20, Routing 2, Holidays 1, Gateways 3, Feeders 4) |
| `m2_proof_seed` | 7 groups / 5 symbols, idempotent |
| `m3_proof_currencies` | 362/362 |
| `m3_proof_uow`, `m3_proof_margin` | pass |
| `m4_proof_order_executes` | **SKIP** — EURUSD outside session (Saturday). Correct behaviour. |
| `m8_proof_routing` | 18/18 |
| `m9_proof_sltp_expiration` | 14/14 |
| `m10_proof_adapters` | 19/19 |
| `m11_proof_a_book` | 39/39 |
| `local_e2e.sh` | **22/22** once a writable log dir exists — but see **D17**, it cannot run on a normal machine |

Fixtures: `mt5-format-structure/` is **UTF-16LE**. Decode to UTF-8 first
(`BROKER_MT5_FIXTURES=<decoded dir>`). 362 symbols × 121 fields, 20 groups, 3 gateways,
4 feeders, 2 routing rules, 1 holiday set.

Deps actually required but **NOT declared in `pyproject.toml`**: `argon2-cffi`, `pyotp`,
`hypothesis`, `aiosqlite`, `asyncpg`. (`psycopg2-binary` is declared but the code dials
`postgresql+asyncpg`.) ⇒ `pip install -e ".[dev]"` does **not** yield a runnable test suite.
This is an M5-class regression ("does it start on a machine that isn't yours").

## 0b. Live infrastructure — probed 2026-09-12 14:54 UTC

| Thing | State |
|---|---|
| Neon PostgreSQL | ✅ **18.6**, reachable, alembic head `008_reconciliation_breaks`, 17 tables |
| Upstash Redis | ✅ `ping` True |
| ngrok tunnel (trade-server) | ✅ up — `openapi` title "Trade Server Backend", 18 routes |
| MT5 terminal behind it | ✅ **`connected`**, login **50080**, server `86.104.251.194:443` |
| Market | Saturday — FX closed; BTCUSD/ETHUSD trade 24/7 |

Neon contents: **37 IN / 9 OUT deals** · 46 FILLED + 4 REJECTED orders · 45 accounts ·
**31 open positions** (24 EURUSD, 7 BTCUSD) · **9 reconciliation breaks OPEN** (8 CRITICAL,
1 MEDIUM; first_seen 08:18, last_seen 08:23 UTC) · **`bars` = 0 rows** ·
newest deal 12:38 UTC (= the D13–D15 cloud proof; nothing has traded since).
D8b signature (open position + `margin_used = 0`): **0 accounts** — the fix holds.

---

## 1. Milestone ledger (complete, M0 → M14 + D1 → D15)

| # | Question answered | Result | Tests |
|---|---|---|---|
| M0 | does it import | 93/180 → 187/187 + CI import gate | ran |
| M1 | one schema + MT5 wire codec | 4 schemas → 1; lossless import/export with quarantine | — |
| M2 | config plane runnable | loader, seeder, 7 admin endpoints, ConfigCache | — |
| M3 | risk maths correct | 4-stage MT5 margin to the cent; 3 symbol currencies; commission tiers | — |
| M4 | does an order execute | HTTP → risk → route → fill → deal → position → margin; stop-out books losses | 274 |
| M5 | runs on a machine that isn't yours | Dockerfile, compose+Caddy, Kafka deleted, CI, fail-hard secrets, real `/health`, `MARKET_DATA_SOURCE` | 297 |
| M6 | debt paid | volume 10⁴ scaling; netting realised PnL; margin **reservation** (atomic UPDATE); swap worker rewritten+wired; **Argon2 login** | 326 |
| M7 | broker earns its spread | `core/domains/pricing/` — fixed spread + SpreadDiff + SpreadDiffBalance, group-after-symbol, stale-quote refusal | 349 |
| M8 | routing table like MT5 | `routing_mt5.py` — full action/condition code space, top-down first-match, OR-within/AND-across, ≤31-char reasons, unsupported ⇒ skip+warn | 374 |
| M9 | server honours the stop | `SlTpWorker` (closes at **market**), `ExpirationWorker` (fires on boot), `OrderReason.SL/TP/SO`, GTD, counts 4005/4006 | 384 |
| M10 | real adapters | `TradeServerTickFeed` (WS+msgpack) · dependency-free **FIX 4.4** · `FixLiquidityGateway` | 422 |
| M11 | is A-Book a trade | 4 explicit outcomes; FILLED/PARTIAL book the client side; ACK rests; `FixTimeout` = `HEDGE_STATE_UNKNOWN` (neither booked nor rejected); definite refusal rejects via one funnel. First partial-fill path. | 448 |
| M12 | reconciliation | breaks table (migration 008), engine, service, ages + auto-clears; `cli sync` = revalue + reconcile (D9) | 519 |
| M13 | markup, MT5-shaped | `pricing/translation.py` — Translates semantics (points of **source** symbol, first-match-by-order, single `*`, bid−/ask+, clamp, never compounded) + `pricing/a_book.py`. `TRANSLATE_FIELDS` modelled; round-trip still 392/392 | 558 |
| M14 | D5 + D11 | Redis single-reader bus; three real client trade routes | 586 |
| D15 era | first real close | D12/D13/D14/D15 + cloud close proof 41/41 | **596** (+25 skipped) |

**Defect ledger:** D1 margin_level never written ✅ · D2 `/account/info` unreachable 5 ways ✅ ·
D3 `cli migrate` on SQLite ❌ OPEN · D4 `.env` tracked 🔴 · D5 Redis pubsub ✅ (0/5 → 5/5 cross-process) ·
D6 two hard-coded 10s staleness literals dropped 497/497 live ticks ✅ · D8 A-Book stale account ✅ ·
D8b tick pipeline erased a fill's margin (lost update) ✅ · D9 no boot revaluation / no sync ✅ (`cli sync`) ·
D10 close never released margin ✅ · D11 no client close/modify/cancel routes ✅ ·
D12 close response read the post-close Position ✅ · D13 tick pipeline computed PnL and threw it away ✅ ·
D14 partial close reported the remainder's floating PnL ✅ · D15 a tick could undo a close ✅ ·
**D16 (NEW, this session) ❌ OPEN** · **D17 (NEW, this session) ❌ OPEN**

---

## 2. NEW FINDINGS this session (2026-09-12, session 4)

### 🔴 D16 — the valuation sweep writes account equity and never writes the positions

`application/services/reconciliation_service.py :: ValuationService._revalue_one`
computes `total_pnl` per account from live prices, calls `account.update_equity(...)`,
persists via `account_repo.update_valuation(...)` — and **never touches the position rows**.
`self.position_repo` is read-only in that file; there is no `save()` / `update_valuation()`
call against it anywhere.

Measured in Neon right now:

```
accounts where (equity - balance) != SUM(open position profit):  24 of 45
distinct phantom deltas:  +800.70 (10 accounts)   -749.20 (9)   +798.90 (2)   +2.10 (1)
all 24 open EURUSD positions:  price_current = NULL,  profit = 0E-8
```

The arithmetic identifies the writer exactly:

```
+800.70 = (1.15968 - 1.07961) x 0.10 lots x 100,000      <- live EURUSD vs the mock open price
-749.20 = (1.15968 - 1.23460) x 0.10 lots x 100,000      <- the m10 simulator's open price
```

So the D9 sweep repriced those positions at live ticks, wrote the result into
`accounts.equity`, and left `positions.price_current` NULL / `profit` 0. **This is D13's
exact class** — a number computed correctly in one place and stored from another — in the
*sweep* rather than the *tick pipeline*. D13 fixed the pipeline; the sweep was written
afterwards and inherited the same bug.

Worse than D13 in one respect: the sweep exists (D9) precisely to make stored values
trustworthy after a restart, so it is actively manufacturing the inconsistency it was built
to remove. And a second-order problem: those 24 positions were opened by the **mock** feed
(1.07961 / 1.23460), so valuing them against live MT5 prices is faithful arithmetic on
fiction.

**Fix is cheap** — D15 already added `SqlPositionRepository.update_valuation()` (atomic,
`time_done IS NULL`, `RETURNING`). The sweep should call it per priced position before
writing the account, so the two rows can never disagree. Also: never sweep a position whose
`price_open` came from `source=MOCK` against a live tick (or re-source it deliberately).

### 🟠 D17 — `make proofs` cannot pass on any machine that isn't the agent sandbox

`scripts/local_e2e.sh`, `scripts/d12_proof_cloud_close.sh` and
`scripts/patch_local_e2e_close_gate.py` hard-code **`$ARENA_WORKSPACE`** — an env var that
exists only inside the Qwen/Arena sandbox. The scripts are `set -u`, so on the user's own
machine or in CI:

```
$ env -u ARENA_WORKSPACE bash scripts/local_e2e.sh
scripts/local_e2e.sh: line 8: ARENA_WORKSPACE: unbound variable      <- dies instantly
```

With `ARENA_WORKSPACE` pointed at a dir containing `work/logs/`, the same script is
**22/22 green** — so the code is fine and only the gate is not portable. This is the
sandbox's literal-path rewriting leaking into a committed file (the same mechanism that
duplicated `_improvement_to_client` in M13 and a block in `.env.example`). It also means the
"13 gates, ~50 s, no credentials" claim in `run_all_proofs.sh`'s header has never been true
outside the sandbox.

**Fix:** `WS="${ARENA_WORKSPACE:-$BP/..}"` + `mkdir -p "$WS/work/logs"`, or simply
`LOGDIR="${LOGDIR:-$BP/.logs}"`.

### 🔴 The repo lost its history, its dotfiles, and its backup — and the leak is still live

HEAD is a **single commit** `38dc30b0 "Add files via upload"`. The 14-commit history that
session 3 built is gone from the branch. Consequences, all verified:

| Missing | Why it matters |
|---|---|
| `.github/workflows/ci.yml` | **gone for the second time.** Session 3 recovered all 83 lines from the dead session's HTML; the web upload dropped it again. Nothing runs CI. |
| `.env.example` | not in the repo (you pasted its content in chat, so it exists locally) |
| `.gitignore` | gone — so the next `.env` can be committed again (D4) |
| `work/patches/bp-full-history.bundle` | **the safety net is gone.** Session 3 verified it cloned back to 11 commits / 321 py files. It was never pushed. |

🔴 **The credentials are still publicly fetchable.** Replacing the branch did not remove the
old objects; they are reachable by SHA:

```
GET https://raw.githubusercontent.com/rahul82586/references-for-AIs-to-read/39c7eaf2/qwe-agen-broker-platform-backend/work/bp/.env
-> 200, 523 bytes, contains the Neon password, the Upstash token AND SECRET_KEY
```

(`a054423c` is the scrubbed 140-byte version; `38dc30b0` has no `.env` at all.) You have said
these are disposable test credentials, so this is not an emergency — but the repo is public,
`39c7eaf2` will stay reachable until GitHub GCs it, and `mt5-format-structure/` still holds a
real TCTrader-Live export with 15 plaintext server passwords + a live JWT. Rotate, go private,
and if it matters, ask GitHub Support to purge the dangling commits.

### 🟠 The state anchor is 5 milestones stale

`Reports/3-PROJECT-STATE.md` stops at M11 + D6 + D9 and still lists as OPEN things that are
now fixed (D5, D8b, D9, and debt items 14/15). M12–M14 and D10–D15 exist only in
`work/bp/docs/{M14,D12,D13-D15}-REPORT.md` plus this file. Per rule 3 of the session-death
protocol, the anchor must be updated — **this file is that update; it has not been pushed.**

---

## 3. Architecture as it stands

```
POST /api/v1/trade/orders                     POST /api/v1/trade/positions/{id}/close   (D11)
PUT  /api/v1/trade/orders/{id}   (D11)        DELETE /api/v1/trade/orders/{id}          (D11)
  -> CreateOrderHandler
  -> PreTradeRiskService       6 checks, per-account asyncio.Lock, atomic margin reservation
  -> OrderApproved
  -> ExecutionOrchestrator
  -> SmartOrderRouter          MT5 request-policy table (M8) -> house rules + NOP 70/85/95% -> default
       |-- B-Book -> BookMatchingEngine        quote_provider = client pricing (M7)
       `-- A-Book -> ILiquidityGateway         stub (strict refusal) | fix (FIX 4.4) | trade_server (Centroid pattern)
                     client booked at the CLIENT price, venue sent/filled at the SOURCE price,
                     difference = markup revenue on the deal event (M13).  Floor: never worse than
                     quote + allowed slippage; BROKER_ABOOK_IMPROVEMENT=client|broker
  -> RecordDealHandler          deal + position + SL/TP + margin recompute + commission
  -> LiquidationWorker / SlTpWorker / ExpirationWorker / SwapWorker / TickMarginPipeline
  -> ValuationService (D9) + ReconciliationService (M12) via `cli sync`
  -> coverage account tracks broker exposure (client long => broker short)
```

Composition root `application/di/trading_setup.py :: build_trading_stack`.
Ports `core/ports/interfaces.py`. Bus in-process by default; `RedisEventBus` when
`EVENT_BUS=redis` (single reader, channel-keyed dispatch, exponential-backoff reconnect — D5).

**The design law, applied consistently: refuse rather than fake.** No LP ⇒ reject, don't invent
a fill. No price source ⇒ orders refused. Unsupported routing condition ⇒ skip with a warning.
`FixTimeout` ⇒ hedge state UNKNOWN, margin held. Stale quote ⇒ reject. Not-wired ⇒ loud 503,
never a plausible-looking number. **Keep this.**

**The recurring defect class (D1, D2, D8b, D12, D13, D14, D15, D16):** *a value computed
correctly in one place and served, stored or written from another.* The durable defence, applied
each time: derive at the point of consumption, give each writer a **disjoint column set**
(`update_valuation`), and make "not wired" a 503.

---

## 4. MT5 configuration model (corrected — `docs/MT5-CONFIG-MODEL.md` is authoritative)

```
data feed / gateway -> symbol mapping (Source -> Symbol)
                    -> Translations   (RENAMES primarily; carries Bid/AskMarkup)
                    -> GROUP settings (spread, commission, swap, margin, netting/hedging,
                                       stop-out, volumes)   <- where the money is configured
                    -> ROUTING rules  (B-Book / A-Book / matching engine / dealer)
```

* **Groups do NOT decide A/B book — routing does.** Verified in the live export: the `dealer`
  rule carries `Dealers=[{"Login":"3","Name":"MetaTrader 5 Gateway clone"}]`; the group appears
  only as a *condition* (`Condition 1001` = GROUP, `ValueString "real\real"`) that selects the rule.
  A gateway is reached as a **dealer** in a routing rule. M8 is correct; do not change it.
* **Translates are for renaming**, not primarily markup. All three gateway configs and three of
  four feeders in the live export have `Translates: []`; the one populated row is
  `{"Source":"*","Symbol":"*!","BidMarkup":"0","AskMarkup":"0","Digits":"0"}` — zero markup and a
  `!` mask the platform ignores. This broker marks up through **group SpreadDiff**.
* Per-group gateway markup = **clone the gateway config per group**, each with its own Translates
  and `Groups` list ("The unlimited number of configurations … can be created for each module").
* B-Book markup = group `SpreadDiff` / `SpreadDiffBalance` (M7). A-Book markup = M13's
  client-price-vs-source-price split. Commission = Group → Commissions (M3).
* MT5 conventions locked in: margin level in **PERCENT**; day index **0 = Sunday**; volume fields
  are **integers scaled 10⁴** (`*Ext` at 10⁸); unknown wire fields **quarantine** into `mt5_extra`
  and re-export byte-identically. **Do not "fix" `symbols.volume_min = 100` — the column holds the
  wire literal; `db_to_symbol` unscales it to 0.01.**

---

## 5. What is genuinely still open

**P0 — security**
1. 🔴 D4 + the still-fetchable `.env` at `39c7eaf2`; 15 plaintext server passwords + live JWT in
   `mt5-format-structure/`. Rotate, go private, purge.
2. Manager JWT + rights-bitmask enforcement; `must_change_password` stored but not enforced;
   static `ADMIN_API_KEY` is still the admin auth path.

**P1 — money & correctness**
3. 🔴 **D16** — sweep writes equity, never the positions (24/45 accounts inconsistent in Neon now).
4. 🟠 **D17** — `local_e2e.sh` / `d12_proof_cloud_close.sh` die without `$ARENA_WORKSPACE`.
5. 🟠 Undeclared deps (`argon2-cffi`, `pyotp`, `hypothesis`, `aiosqlite`, `asyncpg`) — `pip install -e .` is not sufficient.
6. **`margin_free` / `margin_level` have four writers that disagree** (`record_deal._recalculate_account_margin`,
   `ClosePositionHandler._revalue_after_close`, `account.update_equity()` in the tick pipeline, the
   valuation sweep). Observed: `margin_free 99923.16` against `equity 100000.50` with `margin_used 0`;
   `margin_level 129305.98` where the sentinel is `999999`. **Needs one owner — a design decision, not a patch.**
7. **Stop-out has never been driven by a live price.** Reachable from ticks for the first time since
   D13; no live-fire gate.
8. **A-Book close does not unwind the hedge.** `TradeServerLiquidityGateway.close_position()` exists and
   reaches the terminal; nothing calls it. The broker stays long/short at the LP forever.
9. **Reconciliation**: no FIX drop-copy (`35=Z`), no EOD schedule, no automatic resolution of
   `HEDGE_STATE_UNKNOWN`. `TradeServerLiquidityGateway` has **no idempotency key** (trade-server
   hardcodes `magic`/`comment`), so it must never retry blind. **9 breaks OPEN in Neon**, and the
   engine cannot yet tell your personal XAUUSD trades from orphaned hedges.
10. **No resting-order lifecycle at the LP** — an ACK leaves the order PLACED forever; a later
    ExecutionReport that fills it is not consumed.
11. D3 — `cli migrate` cannot run on SQLite (migration 001 emits PG-only `DEFAULT '{}'::jsonb`).
12. **Gateway config plane** (`mt5_gateways` table + loader + repository + admin CRUD) — migration
    009. Codec/`TRANSLATE_FIELDS` and the maths exist (M13); there is nowhere to put a row.
13. **Commission types & charge modes** — standard/agent/fee × instant/daily/monthly; only instant
    standard is exercised. Separate `Fee` field not modelled. Agent commission is a whole IB subsystem.
14. `Use default spreads` / `Use default volumes` / `Use default limit` toggles unverified.
15. `bars` table = **0 rows** on 30+ fills; WS feed drops every ~60 s (`keepalive ping timeout` —
    trade-server doesn't answer pings); 24 positions on unsubscribed symbols never revalued.

**P2 — carried forward**
16. Post-trade valuation still reads **raw** ticks; only pre-trade is client-priced (M7 gap #1).
17. SL/TP: no trailing stops, no `PositionModify` endpoint, no restart-rearm test.
18. Swap: per-day `SwapRate{Sun..Sat}` not modelled, holiday doubling not applied, `REOPEN_*` unimplemented.
19. Stale margin reservations after a node crash — needs an ops sweep for stranded PLACED orders.
20. `counts_fn` reads ConfigCache, not the DB ⇒ count-based routing rules stale in multi-worker.
21. No `CreateAccountHandler` / `CreateClientHandler` / `CreateSymbolHandler`; no investor password.
22. OMS: idempotency keys, FOK/IOC, self-trade prevention, **audit journal**.
23. RMS: Layer-2 authoritative margin reconciliation, leverage **tiers**, NOP 100% force-close,
    client risk profiles, auto-hedge *execution* at 85%, notional gate, fat-finger check.

**P3 — structural / deferred by decision**
24. Journal + snapshot + replay (crash recovery; prerequisite for backup/failover).
25. History plane: tick/bar storage (ClickHouse, `PARTITION BY toYYYYMM`); `LPTickFeed` still `NotImplementedError`.
26. Process roles → cluster (`broker/{trade,history,access,worker}.py`, `$BROKER_HOME`).
    Decision: **modular monolith + process roles; extract later** (gateway → datafeed → history → access; trade last).
27. Dealer terminal/sessions, ECN/CLOB (~5%), admin GUI, client terminal, reporting.
    (`mt5-admin-fontend-for-testing/` = a 124-file / ~13.9k-line **Theia** extension prototype with
    modules for symbols, groups, clients, deals, orders, positions, routing, gateways, data-feeds,
    network-cluster, market-watch — present in the repo, referenced by no doc, built by nothing.)
28. `docker build` has never run (no daemon in the agent workspace). CI inert until `bp` is a repo root
    **and** `.github/workflows/ci.yml` is restored.

## 6. Decisions already made — do not re-litigate

Path B (reimplement MT5 semantics in Python; do not install MT5) · schema authority = **the MT5 SDK**,
not mtapi-docs (kept for REST ergonomics + the 124-endpoint checklist) · payload field names should
become exact MT5 names via `serialization_alias` (known drift) · unknown wire fields quarantine, never
drop · margin level in PERCENT · day index 0 = Sunday · volumes 10⁴ · clustering additive later ·
`BROKER_ABOOK_IMPROVEMENT` defaults to **client** (configurable later; a group-level
`abook_improvement` attribute already takes precedence) · deferred by explicit user decision:
ECN/CLOB, UIs, `intelligence/`, load testing, KYC/backoffice.

**What to steal next:** tfrmma `margin_monitor.hpp` (Layer-2) + `notional_gate.hpp` · rabbittrix
`fx-pricing` (risk adjuster) · matching-core `journal.rs`+`snapshot.rs` · nautilus `event_store ≠
persistence` · hft-clob-core `BENCH.md` discipline.

## 7. Reproducing the gates

```bash
cd qwe-agen-broker-platform-backend/work/bp
pip install -e ".[dev]"
pip install argon2-cffi pyotp hypothesis aiosqlite asyncpg     # <- undeclared, required
export PYTHONPATH=$PWD
python3 scripts/decode_mt5_json.py            # UTF-16LE -> UTF-8 (hard-coded paths; see note)
export BROKER_MT5_FIXTURES=<decoded>/mt5-format-structure
export SECRET_KEY=$(python3 -c "import secrets;print(secrets.token_hex(32))")
export ADMIN_API_KEY=$(python3 -c "import secrets;print(secrets.token_hex(24))")
python3 -m pytest tests -q                                     # 621 passed
python3 -m ruff check --select E9,F63,F7,F82 .                 # clean
export ARENA_WORKSPACE=<writable dir whose work/logs exists>   # <- D17, or the e2e dies
bash scripts/run_all_proofs.sh                                 # 13/0/1 (m4 weekend skip)
# needs real infra:
scripts/m5_proof_cloud.sh            # 33 checks, Neon + Upstash
scripts/m10_proof_cloud_ws.sh        # 14 checks, + live WS
scripts/d12_proof_cloud_close.sh     # 41 checks, + MT5 tunnel; found D13/D14/D15
scripts/m11_proof_live_mt5.sh        # 15 checks, real terminal
scripts/m11_proof_live_hedge.py      # real hedges on the terminal - places REAL orders
scripts/d5_redis_live_proof.py       # 2-process cross-delivery, exit 0 = green
```

⚠️ `scripts/decode_mt5_json.py` hard-codes `/home/user/refs/...` → `/home/user/decoded/...`;
in the agent sandbox those literals get rewritten, so pass paths explicitly or symlink
`~/refs` → the repo root and create `~/decoded/`.

## 8. Session-death protocol (why this file exists)

Every session has died the same way: ~500 tool calls, ~2.8 MB of transcript, history exceeds the
window, the UI returns *"The current content is empty, please regenerate."* (Session 2 died exactly
there on "Proposed M11 → YES", twice; M11 was never generated.)

1. **`git push` at the end of every milestone** — and push with `git push`, **never the GitHub web
   upload**. The web upload is why CI is missing twice, why `.gitignore`/`.env.example` are gone, and
   why 14 commits of history are now 1.
2. Write `work/bp/docs/Mn-REPORT.md` **before** the session gets long.
3. Update **this** anchor at the same time, and push it.
4. Start new sessions from a **fresh chat** with this file pasted.
5. Prefer `scripts/patch_*.py` one-shot idempotent patch scripts over long inline heredocs.
6. Keep a `git bundle` (`work/patches/bp-full-history.bundle`) **inside the repo and pushed** — a diff
   cannot capture the root commit, and the last bundle was never pushed and is now gone.
7. Anything outside the repo gets lost: `.git` and `.git/config` are **not** in the workspace snapshot,
   so the origin URL and local history do not survive between sessions.
