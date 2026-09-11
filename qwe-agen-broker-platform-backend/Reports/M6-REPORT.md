# M6 — Is the debt paid?

**Status: COMPLETE.** Test suite **297 → 326 passed / 0 failed**. All six legacy proofs
green. Cloud proof **29/29** against Neon PostgreSQL 18.6 + Upstash Redis, now including
migrations 004–005 and a password-verified trade.

M6 was the debt queue from the M4 report plus the login hole M5 flagged. Every item is
fixed, and — as usual — fixing them exposed defects underneath, all listed below.

---

## 1. Item-by-item

### ① `volume_min`/`volume_step` lost on the DB round trip — FIXED (and it was worse than reported)

The M4 report called this "the most consequential item". Investigation showed the defect
ran in BOTH directions, from one root cause: MT5 writes `Volume{Min,Max,Step,Limit}` as
**integers scaled 10^4 against the lot**, with `*Ext` siblings at 10^8. Measured on your
real export: `Ext == bare × 10^4` for all **362 symbols × 4 fields, zero violations**
(EURUSD: `VolumeMin="100"`, `VolumeMinExt="1000000"` = 0.01 lots).

The codec read them as plain decimals:
* **Import:** domain `volume_min = 100` — a 10,000×-too-large minimum. Invisible to the
  round-trip proof, which re-exported the same wrong literal *byte-identically*. Wire
  fidelity had been masking a semantic error since M1.
* **YAML seed:** 0.01 rendered `"0"` at the scale-0 fallback — the reported symptom.

Fix: conversion in one place (`codec.py`). Import unscales (preferring Ext); export scales
and derives **both** literals from the domain value, so a stale quarantined Ext can never
contradict an edited volume; fresh rows export a complete, self-consistent pair.
Round-trip proof unchanged: **362/362 + 20/20 byte-identical**. Verified in the cloud DB:
seeded EURUSD now reads back `volume_min=0.01, volume_step=0.01` (was `0/0`).

### ② Netting doesn't book realised PnL — FIXED (netting was unreachable in the first place)

Two defects, one hiding the other:
* The mode dispatch read `account.group.execution.mode` — **an attribute Group does not
  have**. The hasattr guard yielded None and every account silently ran hedging. The
  netting branch was dead code, which is why its money bug survived M4's audit. Dispatch
  now follows the MT5 SDK (`IMTConGroup::EnMarginMode`): `MarginMode.RETAIL(0)` and
  `EXCHANGE_DISCOUNT` = netting, `RETAIL_HEDGED(2)` = hedging, unknown keeps hedging.
* The netting branch reduced/deleted positions **without booking the realised result** —
  the client's P&L vanished. Now computed by the new `RiskEngine.realized_pnl` →
  `margin.position_pnl` (the single source of truth; quote→deposit converted), carried on
  the OUT deal, and booked once by the existing central balance step.

Found by the new tests en route: full-close used an `hasattr(pos_repo,'delete')` probe
that **silently skipped** on repos without delete (ghost margined positions — closes now
mark the row like every other closing path), and the reversal branch computed the
remainder **after** zeroing the old volume (reopened leg was the full deal volume).
`ClosePositionHandler` also gained an optional `risk_engine`: its raw add would have put
JPY amounts on USD balances.

Proven: flat close books −1.00; partial books only the closed volume; reversal realises
the old side and reopens the remainder at the deal price; **USDJPY books 4,800 JPY as
≈31.9 USD** (conversion, not raw quote amounts); hedging groups unaffected.

### ③ Duplicate margin monitor — DELETED

`risk_worker.py` (polling, instantiated nowhere, publishing its own MARGIN_CALL_TRIGGERED)
removed. `TickMarginPipeline` (tick-driven, wired, tested) is the single state machine.

### ④ `on_event` → lifespan — DONE

Startup/shutdown are now a FastAPI `lifespan` context manager. Deprecation warnings gone
(suite warnings 59 → 19).

### ⑤ Swap never charged — FIXED (worker rewritten to MT5's spec, wired at startup)

The old worker had never run: every line spoke the pre-M3 vocabulary (`position.side`,
`.average_price`, `.id`), it constructed the base `DomainEvent` with an `init=False`
event_type, it read a **group-level** swap profile MT5 does not have (swap is per-symbol
with group overrides), and nothing instantiated it.

Rewritten against the MT5 Administrator guide (Symbols → Swaps):
* **POINTS:** `volume × contract × point` in the profit currency, converted to deposit, × rate (the guide's USDTRY example shape)
* **Money modes** (SYMBOL/MARGIN/GROUP/PROFIT_CURRENCY): `rate × volume`, converted at the rate **unfavoured to the trader** (positive swap sells the swap currency)
* **INTEREST_CURRENT/OPEN:** annual % ÷ `SwapYearDay`; Forex lot cost = contract size, CFD-family = contract × price
* **Day multipliers:** weekday 1, `Swap3Day` 3, weekend 0 — MT5's day index is **0=Sunday**, wire-verified (EURUSD `Swap3Day=5` pairs with `SwapRateFriday=3.0`)
* Group symbol overrides on swap_long/short; group `enable_swaps` kill-switch
* Charged through the **LedgerEngine**: immutable SWAP BalanceOperation + balance movement in one call; `position.swap` accumulates for statements; `SwapApplied` event on its own channel; rollover hour via `SWAP_ROLLOVER_HOUR_UTC` (default 22)
* INTEREST with no price **refuses rather than guesses**; unimplemented REOPEN_* modes log loudly once

Tests force the rollover with a fixed clock (Wednesday ×1 = −0.79, Friday ×3 = −2.37,
Saturday ×0, short rate, group disable, JPY conversion).

### ⑥ No margin reservation — FIXED (the multi-node race is closed)

`accounts.margin_reserved` (total hold) + `orders.reserved_margin` (whose hold), migration
004. Approval reserves the exact requirement; the fill releases it **inside the deal
transaction**; the orchestrator's single rejection funnel and a failed persist release it;
the pre-trade check subtracts in-flight holds in both availability paths.

Cross-node atomicity: `SqlAccountRepository.reserve_margin` is **one conditional
UPDATE … WHERE free ≥ amt RETURNING margin_reserved** — the database serialises racers.
Contract lesson (caught by a new test): repo methods own the stored state and return the
**new total**; helpers SET (never add) the in-flight object — adding double-counted
against in-memory doubles that mutate the same object. Bind lesson: untyped text vs
numeric compares by **text order** in SQLite (and is a type error in PG) — `CAST(:amt AS
DECIMAL(20,8))` on both dialects.

Proven: two concurrent validations approve **exactly one** (balance 1200, requirement
1100.10); fill releases to zero with `margin_used=110.01` intact; A-Book refusal releases;
two SQL racers on one row — one winner; double release clamps at zero.

### ⑦ Login without a password — FIXED (the M5-flagged hole)

`POST /api/v1/auth/login` had been issuing a JWT to **anyone who named an existing
login_id** — the route never read the password its own schema declared required, and
defaulted login_id to `100001`. Now: password required, verified against
`accounts.password_hash` (Argon2 — the manager bootstrap's hasher, migration 005), and
**every failure returns one generic 401** (unknown login / wrong password / disabled /
unprovisioned are indistinguishable to the caller; the specific reason goes to the log).
An unset hash **fail-closes**. `POST /api/v1/admin/accounts/set-password` (admin key,
min length 8) provisions/rotates; `last_login` stamped for audit.

---

## 2. Numbers

| | before M6 | after M6 |
|---|---|---|
| Tests | 297 | **326 passed / 0 failed** |
| Legacy proofs | 6/6 | **6/6** (round-trip still 362/362 + 20/20 byte-identical) |
| Cloud proof | 28/28 | **29/29** (adds wrong-password 401) |
| Migrations on Neon | 003 | **005** |
| Ruff fatal gate | clean | clean |
| Suite warnings | 59 | 19 |

Cloud proof highlights (Neon PG 18.6 + Upstash, real TLS): migrate 001→005 · seed
idempotent (symbols re-seeded with corrected wire ints) · boot (trading plane, Redis bus,
SwapWorker started/stopped, mock source announced) · /health db 14.6ms / bus 62.2ms ·
account+Argon2 hash persisted · login 200 / wrong password 401 · BUY 0.10 FILLED at
1.07961, margin 107.961 USD, equity 9,999.00 · positions_count=1 · external subscriber
saw 5 ticks through Upstash pub/sub · clean shutdown.

Also fixed en route: JSONB→JSON SQLite compile hook moved from the M4 proof script into
`infrastructure/persistence/database.py` (any sqlite `create_all` works now).

## 3. Remaining debt (found, documented, not hidden)

**Swap:** per-day `SwapRate{Sun..Sat}` multiplier table not modelled (quarantines
losslessly; the swap_3day/weekend rule reproduces your server's actual curve) · holiday
doubling not applied · REOPEN_* modes unimplemented · no server-level swap control.
**Reservation:** a node crash between approval and terminal state strands a hold until
the order is closed out — an ops sweep for stale PLACED orders is the answer (M7+) ·
full-row `account_repo.save()` can still race another node's writes on OTHER columns
(repository design, pre-existing).
**Accounts:** no `CreateAccountHandler` yet — the admin set-password endpoint is the
interim provisioning path; generated-password-printed-once (the manager pattern) belongs
to account creation · no investor (read-only) password.
**Feeds:** MockTickFeed quantises to spread, not `symbol.tick_size` (fine for a labelled
mock; must not be copied into a real adapter).
**Still pending from M5:** docker build/run on a machine with a daemon (`make
docker-build && make up && make health`) · CI activates when `bp` is pushed as a repo.

## 4. Next

**M7 — the pricing/spread/markup module** (the largest functional zero: every real order
flows through it, the broker earns nothing on spread today, and the routing engine's
deviation-from-market conditions need priced quotes). Then the routing rules engine
(MT5 action/condition taxonomy), then server-side SL/TP + expiration execution, then the
adapter registry (trade-server WS feed + quickfixn FIX gateway).