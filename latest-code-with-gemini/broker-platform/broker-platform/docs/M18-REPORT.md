# M18 — SURFACE COMPLETION (session 7, 2026-09-14)

**Scope delivered:** D16 FIXED · the edge-layer cleanup (F6 naming drift, the
duplicate client repository, the shadowed legacy reads, F1 dead sockets
fixed) · 17 wired endpoints from the ENDPOINT-CATALOG audit · 34 honest
skeletons · the surface-completion proof that mechanically bans the F8 shape.
**52 → 93 OpenAPI paths / 116 operations.**

**Gates after this milestone:** `pytest tests` **835 passed / 0 failed** (788
at M17; +9 D16, +6 F1, +32 M18 surface) · ruff clean · **12 proofs green**:
p1_migration 24/24 · p1_identity 59/59 · p1_account 72/72 · p1_manager 80/80 ·
p1_read_plane 55/55 · **p1_surface_completion 41/41 (NEW, in CI)** ·
round-trip 392/392 · m2 · m3 margin · m8 18/18 · m9 14/14 · m10 19/19 ·
m11 39/39 · m4 weekend-skip (correct) · f8f9 live proof 10/10 (run at M17).

---

## 0. The catalog that scoped this milestone

The user asked for the COMPLETE map, not a milestone slice. Built from the
repo's own corpus: all **231 MT5 Web API commands across 44 families**
(`Web-API.md`), the **mtapi 124-endpoint** checklist (`swagger.json`), our
live route table. Result: `notes/ENDPOINT-CATALOG.md` (session workspace) —
every family dispositioned ✅/🔵/🟡/🟠/⚪/⛔, including the families we
refuse BY ARCHITECTURE (deal deletion — a deal is an immutable fact; plugin
hosting; history_sync; MT4 dialects) and those deferred BY USER DECISION
(reports, mail/news, book/DOM, backoffice documents). M18 executed the 🔵
column and skeletoned the 🟡 column.

## 1. A1 — D16 FIXED (the toll, paid first)

`313cc0c`. The sweep computed each position's PnL, wrote ONLY
`account.equity`, left the rows at profit=0/price_current NULL — 24/45 live
accounts inconsistent, measured in three sessions. The fix mirrors D15's rule
in the tick pipeline: write each priced position FIRST through the
column-scoped `update_valuation` (atomic, profit computed in SQL from the
row's own volume, refuses closed rows, returns what it wrote), and the
account total is the sum of WHAT WAS WRITTEN. Every non-writing branch
preserves the row's stored profit in the total (no price / failed write /
MOCK-over-live skip); a closed-mid-sweep row contributes nothing; a sweep
that revalues nothing writes nothing. New: a MOCK-labelled tick never
re-values a row carrying a real `price_current`. The invariant
`equity − balance == Σ stored position profit` is now structural on every
branch — 9 tests pin each one. **Live repair lands automatically with the
first priced sweep after market open** (the 24 rows self-heal; both sides are
recomputed from the same prices).

## 2. A2–A4 — the cleanup

`63d90ab`. Deleted: the unreferenced duplicate `api/webhooks/`, the four
empty V1 placeholder dirs (`api/{admin,client,fix,grpc}`). Retired:
`admin_router`'s shadowed `GET /accounts` + `GET /managers` (canonical homes
are the rights-gated paged reads; `account_summary` gained the legacy
`is_enabled` key so nothing was lost). **F1 FIXED**: the
`WebSocketEventBridge` fed only the manager subscription manager — `/ws/stream`
and `/ws/user` accepted connections and never sent a frame. The bridge now
feeds both audiences: ticks to the public socket, trading events to the
account's private socket keyed by login (no login → no delivery; broadcasting
one account's trades to every socket would be a leak), and the two risk event
types it never subscribed to (MARGIN_CALL_TRIGGERED, STOP_OUT_INITIATED) are
subscribed and delivered. 6 tests.

**Drift killed in the B-tier work:** TWO `SqlClientRepository` classes
existed — the step-6 PROMOTED one (`identity_repository.py`, with the port,
live in DI) and the portless legacy copy (`manager_repository.py`) that step
8's SQL test happened to exercise. The live one lacked `find_page`; the dead
one had it. Legacy deleted, re-exported for import compatibility, one class
owns the shape. This is precisely the D18 disease (two builders of one
shape) caught by a proof before it served a 500 in production.

## 3. B-tier — the 17 wired endpoints (`755a30c`)

Manager dialect (MT5 method names): **DealGet · OrderGet** (step-8 handlers +
the F9 ticket rule via shared `deal_to_info`/`order_to_info`; DealInfo/
OrderInfo gained canonical ids and honest Optional tickets/prices) ·
**SymbolGet · GroupGet** (the admin builders — one shape, one builder) ·
**ServerTime** (day 0 = Sunday).

Admin dialect: **GET /routing** (both tables, in EVALUATION ORDER — top-down
first-match means order IS semantics) · **GET /ticks** (engine snapshot +
source label + honest nulls for un-ticked symbols) · **risk exposure /
summary / margin-calls** (COUNTs and the maintained coverage JSON — no row
loaded that isn't served) · **the four trade calculators** (`calc-margin`,
`calc-profit`, `calc-rate`, `check-margin` — MT5's `trade/calc_*` family over
the RiskEngine's own 4-stage pipeline; refuse without a live price, never
approximate) · **POST /accounts/{login}/balance** (the M16 ledger-backed
operation, finally mounted; **RIGHT_ACCOUNTANT** — MT5's "work with funds"
right, not ACC_MANAGER; system-generated types refused; a ledger row or a
refusal; withdrawal-over-balance is a 400 with the reason) · **holidays
CRUD** (command + repo existed with ZERO routes) · **check-password**
(Argon2 verify; unprovisioned/corrupt hash reported honestly; the hash never
leaves) · **accounts/online** (RIGHT_ACC_ONLINE *on top of* ACC_READ, per
MT5's bit split; declared before `/{login}`) · **clients/{id}/accounts**
backlink · **symbols/{name}/sessions** (answered by the SAME entity methods
the pre-trade gate uses — the UI and the risk engine cannot disagree).

Repository layer grew three additive account filters (`so_active`, `online`,
`client_id`) and `get_all` on holidays. `ListAccountsQuery` carries them.

## 4. C-tier — 34 honest skeletons

Every one: **501**, detail starts `NOT WIRED:` and names the missing piece
and its milestone, `x-not-wired: true` in OpenAPI, and is **gated by the
right its real implementation will use** (so authorisation doesn't change
when the logic lands). Families: account update/delete/archive/restore ·
symbol writes · routing writes + reorder · gateways · datafeeds · allocations
(step 9) · journal (audit) · reports · charts/history · mail/news · group
symbol overrides (the SpreadDiff writes, ENDPOINTS B6) · manager delete ·
dealer requote/confirm. Deliberately NOT skeletoned: on-behalf-of `login` on
OrderSend — B1 adds the parameter together with its authorisation, never
before it.

## 5. The new gate: p1_proof_surface_completion (41 checks, in CI)

Walks the ENTIRE mounted route table on seeded SQLite through the real
`create_app()`: every `x-not-wired` operation answers 501 NOT WIRED · every
real GET answers 200/404 — never 500, never 503 · 34 named key routes serve
their seeded data (PositionGet included, with the real ticket) · zero stray
501s outside the registry. **A route answering 200-empty while unwired — the
F8 shape — now fails the build.**

## 6. Decisions made this milestone — do not re-litigate

* RIGHT_ACCOUNTANT (24) gates funds; RIGHT_ACC_ONLINE (28) gates the online
  list ON TOP of ACC_READ; RIGHT_QUOTES (31) ticks; RIGHT_RISK_MANAGER (32)
  risk reads AND calculators; RIGHT_CFG_REQUESTS (19) routing;
  RIGHT_CFG_HOLIDAYS (13); RIGHT_CFG_SYMBOLS (15) sessions.
* Calculators are priced at the CURRENT market and say so; a calculator that
  disagrees with the risk engine by a cent is two answers to one question.
* The sweep's no-price branch PRESERVES stored profit in the equity total
  (the old code silently dropped it — a second, quieter D16).
* Balance endpoint accepts only DEPOSIT/WITHDRAWAL/CORRECTION/BONUS;
  COMMISSION/SWAP/DEAL_PROFIT belong to the engines that book them.
* One `SqlClientRepository`, in `identity_repository.py`. The re-export in
  `manager_repository.py` is compatibility, not a second home.
* Skeletons are deleted in the same commit that builds them for real.

## 7. Still open

**User actions:** push `313cc0c` + `63d90ab` + `755a30c` + docs commit ·
credential rotation/purge (`39c7eaf2` still live) · the `clients=0` backfill
decision · after Monday's market open: run `cli sync` (or boot the server)
once and re-measure D16 → expect 0/45 (the proof: `f8f9_proof_live_position_get`
+ the D16 query in PROJECT-STATE-v8 §0b).

**Next milestones (Tier 3 queue):** ① B1 manager-on-behalf-of + dealer
authorisation (unblocks the dealer UI and the requote/confirm skeletons) ·
② UpdateAccountHandler + migration 010 (D20 nullable `orders.price_order`,
`mt5_gateways`, `mt5_datafeeds`, the leverage list, symbol-group tree) ·
③ symbol CRUD after the 121-field decision · ④ audit journal · ⑤ history
plane (bars=0) · ⑥ trade-modification family · ⑦ F2 client-auth rebuild ·
⑧ step 9 allocations logic.
