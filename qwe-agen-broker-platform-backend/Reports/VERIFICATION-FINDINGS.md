# Independent Verification & Findings — 2026-09-12

Fresh clone of `rahul82586/references-for-AIs-to-read` @ `a054423c`, working tree at
`work/bp`. Everything below was **run**, not read.

---

## 1. Gates reproduced

| Gate | Claimed (M10 report) | Measured here | |
|---|---|---|---|
| `pytest tests` | 422 passed | **422 passed / 0 failed** (25.5 s) | ✅ |
| `ruff --select E9,F63,F7,F82` | clean | **All checks passed** | ✅ |
| `m8_proof_routing.py` | 18/18 | **18 passed, 0 failed** | ✅ |
| `m9_proof_sltp_expiration.py` | 14/14 | **14 PASS / 0 FAIL** | ✅ |
| `m10_proof_adapters.py` | 19/19 | **19/19** | ✅ |
| MT5 wire round-trip | 362 symbols + 20 groups | **392/392 records byte-identical** | ✅ **stronger than claimed** |
| Live HTTP trade (local) | cloud only | **15/15** — see §3 | ✅ new |

The round-trip proof script (`m1_proof_roundtrip.py`) is **missing from the repo**; I rebuilt
it as `work/verify/verify_roundtrip.py`. It covers more sections than the reports ever cited:

```
ConfigSymbols    362 records   BYTE-IDENTICAL
ConfigGroups      20 records   BYTE-IDENTICAL
ConfigRouting      2 records   BYTE-IDENTICAL
ConfigHolidays     1 records   BYTE-IDENTICAL
ConfigGateways     3 records   BYTE-IDENTICAL
ConfigFeeders      4 records   BYTE-IDENTICAL
=== ROUND-TRIP: 392/392 records field-identical ===
```

Also missing from the repo: `m2_proof_seed`, `m3_proof_currencies`, `m3_proof_uow`,
`m3_proof_margin`, `m4_proof_order_executes`. The m1–m4 proofs exist only in the dead
session's workspace. **Worth rebuilding** — they are the regression net for the margin maths.

## 2. Scale

273 py files / 46,433 LOC. `infrastructure` 11,195 · `tests` 10,086 · `core` 8,001 ·
`application` 6,429 · `api` 3,830 · `scripts` 5,068. Migration chain 001→007 clean.
34 test files. 21 HTTP routes + 3 WS routes.

Empty by design (deferred): `intelligence/` (7 files, 0 LOC), `infrastructure/cluster/`,
`core/domains/backoffice/`, `api/grpc/`, `api/fix/`. `LPTickFeed` still `NotImplementedError`.
Only 6 real stub markers in non-test code — the codebase is not littered with TODOs.

---

## 3. New artifact: credential-free local E2E proof

`work/verify/local_e2e.sh` — mirrors `m5_proof_cloud.sh` but runs on **SQLite + in-process
bus + mock feed**, so it needs no Neon/Upstash. Result: **15 passed, 0 failed.**

```
schema created (create_tables)          seed: 7 groups / 5 symbols
cli status: configuration populated     uvicorn booted, trading plane wired
/health 200  database ok 1.2ms  event_bus in-process
mock price source announced
login (Argon2-verified) 200             wrong password 401
POST /api/v1/trade/orders  BUY 0.10 EURUSD -> 200
   state FILLED  price 1.07978  filled_volume 0.10000000
GET /account/positions -> 1
GET /account/info -> balance 10000  equity 9999  margin_used 107.978  margin_free 9891.022
clean shutdown
```

Margin cross-check: `0.10 × 100,000 / 100 = 100 EUR × 1.07978 = 107.978 USD`. The M3
4-stage pipeline, reached from a local HTTP request. ✅

---

## 4. DEFECTS FOUND (new — not in any report's debt list)

### 🔴 D1 — `accounts.margin_level` is persisted, served, and **never written**

Measured straight out of the database after a real fill:

```
login   balance  equity  margin_used  margin_free  margin_level
768577  10000    9999    107.978      9891.022     0            <-- should be 9260.22
```

**Root cause.** `RiskEngine.calculate_margin_level()` computes the level into a
`MarginSnapshot` (`core/domains/risk/engine.py:419,441`) and the deal/margin write path
persists `balance`, `equity`, `margin_used`, `margin_free` — but never assigns
`account.margin_level`. `Account.recompute_margin_level()` (`core/domains/accounts/account.py:91`)
*does* set the field, and **nothing on the trading path calls it**. The column keeps its
`default=0` (`account_models.py:98`) forever, and the mapper faithfully round-trips the 0
(`:179` write, `:243` read).

**Blast radius — three consumers, one of them serious:**

1. **MT5 routing money conditions evaluate against 0.** `core/domains/execution/router.py:203`
   builds the routing context with `margin_level=getattr(account,"margin_level",None)`, and
   `routing_mt5.py:474` feeds `ctx.margin_level` to `RouteCondition.MARGIN_LEVEL`. Because the
   value is `Decimal('0')` and **not `None`**, the M8 "missing context ⇒ condition does not
   match" safety rule does *not* engage — it performs a real comparison against zero.
   A rule like *"reject if MARGIN_LEVEL < 200"* rejects **every** order; *"route to dealer if
   MARGIN_LEVEL < 500"* **always** fires. This is silent flow-diversion, exactly the failure
   mode M8's honesty rule was written to prevent.
2. `GET /api/v1/account/info` reports `margin_level: 0.0000`. A client terminal reading that
   shows an account at 9260% as instantly stopped-out.
3. Manager `AccountGet` (`api/routers/manager/main.py:63`) and the admin account list
   (`admin_router.py:231`) report the same 0.

**Not affected:** the margin-call / stop-out state machine, which consumes the freshly
computed `MarginSnapshot` rather than the stored field. That is precisely why 422 tests pass —
**no test asserts on the persisted or served `margin_level`.**

**Fix shape (small):** call `account.recompute_margin_level()` in the same place the margin
write path sets `margin_used`/`margin_free`, so the stored column and the snapshot can never
diverge; then add a test that reads the column back after a fill, and a routing test with a
`MARGIN_LEVEL` condition. Better still: stop storing a derived value — compute it in the mapper
on read — so there is one source of truth, which is the rule this codebase already follows for
PnL (`RiskEngine.calculate_position_pnl`).

### 🔴 D2 — `/account/info` still has the exact anti-pattern M5 fixed on `/positions`

```python
# api/routers/account.py:29-36
if handler:
    try:
        result = await handler.handle(query)
        return AccountInfo(**result)
    except Exception:
        pass            # <-- swallowed; silently falls back to the JWT snapshot
```

And the handler is **never registered**: `api/di_providers.py:142` does
`_container.get("account_info_query_handler")` → verified to return `None` at runtime.
So `if handler:` is always false and the endpoint *always* serves the fallback branch —
which is where the `margin_level: 0` in D1 reaches the client.

M5 defect #14 fixed precisely this on `/positions` (now 503 when unwired, 500 with a logged
traceback). **`/info` was missed**, and it is the endpoint that carries the margin numbers.
The correct `GetAccountInfoQueryHandler` maths at `application/queries/get_account_info.py:47`
is right and unreachable.

**Fix shape:** register `account_info_query_handler` in `trading_setup.as_providers()`;
replace `except Exception: pass` with the `/positions` contract (503 unwired / 500 logged).

### 🟠 D3 — `cli migrate` (alembic) cannot run on SQLite

```
Running upgrade -> 001_initial_schema
sqlite3.OperationalError: ... DEFAULT '{}'::jsonb ...
```

Migration 001 emits PostgreSQL-cast `server_default`s for the JSONB columns. The M5 fix added
a JSONB→JSON *type* compile hook (`infrastructure/persistence/database.py:11`) which makes
`create_all` work on SQLite — but `server_default` text is passed through verbatim, so alembic
still fails. Consequence: `make setup-dev` / `make migrate` only work against PostgreSQL; a
dev machine without a DB server cannot bootstrap via the documented path. `create_tables()`
works (that is what §3 uses). Either dialect-guard the defaults in 001 or document that SQLite
dev uses `create_tables`.

### 🟡 D4 — `.env` credentials are in public git **history**

HEAD's `.env` is correctly scrubbed (all values empty). But it was created with live values at
`39c7eaf2` (2026-09-11 16:07 UTC) and scrubbed at `a054423c` (17:38 UTC). Both commits are
public, so the Neon + Upstash credentials are retrievable from history. Separately,
`mt5-format-structure/` still ships the real TCTrader-Live export with 15 plaintext server
passwords + a live JWT — flagged since the M4 audit, still open.

---

## 5. Confirmed-still-open (verified in code, matching the reports)

* **A-Book does not complete a trade.** `execution_orchestrator._execute_a_book` sends to the
  gateway, sets the order PLACED, publishes `OrderRouted` — and never calls `RecordDealHandler`.
  No deal, no position, no margin release. Contrast `_execute_b_book`, which does all three.
  The M10 `FixLiquidityGateway` returns a real FILLED report that is then dropped on the floor.
* Post-trade valuation (equity loop, position PnL) still reads **raw** ticks; only the pre-trade
  path is client-priced (M7 gap #1, unchanged).
* `LPTickFeed.stream_ticks/stream_book` → `NotImplementedError`.
* No trailing stops, no SL/TP modify endpoint, no idempotency keys, no partial fills, no
  FOK/IOC, no self-trade prevention, no audit journal.
* `intelligence/`, `cluster/`, ECN/CLOB, dealer terminal — empty, deferred by decision.

## 6. Artifacts produced this pass

```
work/bp/                          working tree, git baseline 8746a26 (== GitHub a054423c)
work/verify/verify_roundtrip.py   rebuilt M1 wire round-trip proof  -> 392/392
work/verify/local_e2e.sh          new credential-free local E2E     -> 15/15
recovered/docs/                   12 reports extracted from the dead session
recovered/transcript/             full + condensed session transcripts
PROJECT-STATE.md                  context anchor for future sessions
```
