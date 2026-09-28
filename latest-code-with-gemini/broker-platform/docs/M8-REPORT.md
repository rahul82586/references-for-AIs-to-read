# M8 — Does a request flow through the routing table the way MT5 does?

**Status: COMPLETE.** Test suite **349 → 374 passed / 0 failed**. New proof
(`scripts/m8_proof_routing.py`): **18/18**, replaying the broker's OWN two rules from the
live TCTrader export. All six legacy proofs green. Cloud proof **29/29** — migration 007 on
Neon, the live table seeded from the raw UTF-16 export, and the cloud order passing through
`Auto Execution` → FILLED.

Before M8, "routing" meant the house `SmartOrderRouter`: a priority list of A/B/ECN
destinations plus the NOP exposure thresholds. That is exposure governance — it is *not*
MT5's routing table. MT5 evaluates a **request-policy table** (IMTConRoute) top-down on
every request *before* execution: reject-with-reason, delay, strip SL/TP, send to dealers,
requote, confirm, cancel — selected by 24 request-type bits, 8 order-type bits and ~40
condition types. Your live server runs exactly two such rules, and until now the platform
could neither read nor honour them.

---

## 1. What was built

### The taxonomy — `core/domains/execution/routing_mt5.py` (pure, SDK-numbered)

* `RouteRequest` — all 25 `REQUEST_*` bits (the live rules carry `Request=33554431` = ALL)
* `RouteAction` — `DELAY_TIME/TICK(0/1)`, `CLEAR_TP/SL/SLTP(2/3/4)`, `DEALER(1001)`,
  `DEALER_ONLINE(1002)`, `REJECT(1003)`, `REQUOTE(1004)`, `CONFIRM_CLIENT(1005)`,
  `CONFIRM_MARKET(1006)`, `CANCEL_ORDER(1007)`
* `RouteCondition` — the full `EnRouteCondition` code space (0–14 request context,
  1000–1008 client, 2000–2005 money, 3000–3002 activity, 4000–4011 positions/orders,
  5000 spread) and `EnConditionRule` operators (EQ, NOT_EQ, GREATER, NOT_LESS, LESS,
  NOT_GREATER)

### The semantics — per the Administrator guide, pinned by tests

| Rule | Evidence |
|---|---|
| Top-down, **first match wins** | guide: rules execute in order |
| **OR within** a condition type, **AND across** types | your live `dealer` rule carries two `CONDITION_GROUP` entries (`real\real`, `real\real-A`) and means *either* — AND-within would match nobody and make the rule dead |
| `DELAY_*` and `CLEAR_*` are **non-terminal**: "execution continues in accordance with the rules located below" | they accumulate onto the decision; the next rule decides |
| Everything else is terminal | — |
| Reject reasons are **≤31 chars** (client-visible) | guide: "maximum message length is 31" |
| Deviation: Buy → (ask − request), Sell → (request − bid), in points | guide's own worked example (1.2000 vs 1.2008 = 8 points) |
| Comment operators: `=` exact, `>`/`>=` rule-string inside comment, `<`/`<=` comment inside rule-string | guide |
| Weekday = bitmask over MT5 days (0=Sunday) | the M6 wire-verified convention |
| `Mode=0` → disabled, skipped | SDK |

**The honesty rule:** conditions this build cannot evaluate (country/city/colour/zipcode,
daily-deal statistics, position age/modify-time, SL/TP-touch, gap mode, spread-deviation)
are declared `UNSUPPORTED` — a rule carrying one is **skipped with a recorded warning**.
It never silently matches (which would divert flow nobody asked for) and never silently
fires a REJECT (which would turn clients away for the wrong reason). Missing context
(e.g. no client quote for a deviation condition) makes the condition **not match** — the
safe direction, documented on the context dataclass.

### The wire — lossless, both directions

`ROUTING_FIELDS` fully mapped; `Conditions`/`Dealers` registered as codec nested tables.
**The live Routing export re-encodes byte-identically** (proven in the unit suite and the
proof). `loader.routes_from_mt5` + `mt5_routing_rules` table (migration 007: verbatim
record JSONB + typed hot columns name/position/mode/action/masks) + SQL & in-memory repos
+ **`cli seed --mt5-routing <export.json>`** (reads the raw UTF-16 file directly).

### The flow — policy first, governance second

`SmartOrderRouter.route()` now: **MT5 table (request policy) → house rules (destination +
NOP thresholds) → default**. Action mapping, every choice deliberate:

| Action | Behaviour here | Why |
|---|---|---|
| REJECT | rejected, client reason ≤31 chars, persisted | faithful |
| DEALER (no skip flag) | `TO_DEALER` → dealer queue, nothing executes | faithful; queue has no UI yet (documented) |
| DEALER (skip-if-none-online) | **skipped → continues down the table** | no dealer *sessions* exist in this build, so nobody is online: MT5 skips the rule. Parking a client's order in a queue nobody services would be worse than either alternative |
| REQUOTE / CANCEL_ORDER | rejected with an honest reason | both need a dealer terminal protocol that does not exist; refusing beats faking |
| CONFIRM_CLIENT / CONFIRM_MARKET | falls through to normal execution | "confirm execution at the requested/market price" **is** normal execution on a market-execution platform — your live `Auto Execution` rule now replays with exactly that meaning |
| DELAY_TIME | orchestrator sleeps after approval, before execution | where MT5 places it |
| DELAY_TICK | modelled, refused loudly | needs a tick counter; not silently skipped |
| CLEAR_SL/TP/SLTP | stripped from the order, evaluation continues | non-terminal transform |

### M7 gap #1 closed — one price, three consumers

`CreateOrderHandler` now prices market orders for the **risk check** through the same
client-quote provider the matching engine fills through, and the router's
deviation/spread conditions read it too: **engine, risk and router see ONE price**. The
integration test pins it: with a 20-point group markup on a CFD-leverage symbol, reserved
margin is **110.03** (client price), not 110.01 (raw). Stale quotes now refuse at pricing
time — persisted REJECTED + `ValueError` (HTTP 400), the existing no-price contract.

## 2. What is proven

**`scripts/m8_proof_routing.py` — 18/18, the broker's own table:**
```
[1] decode: dealer = DEALER(1001), skip-if-offline, REQUEST_ALL, groups real\real +
    real\real-A, gateway dealer · Auto Execution = CONFIRM_CLIENT(1005)
[2] both records re-export BYTE-IDENTICALLY through the codec
[3] demo\Standard        -> Auto Execution (CONFIRM_CLIENT)
[4] real\real            -> dealer (skip-if-offline)     [5] real\real-A -> dealer
[6] preliminary / coverage\house / demo\Challenge -> Auto Execution via '*'
[7] synthetic REJECT: terminal, reason truncated to 31
[8] DELAY 250ms + CLEAR_SLTP accumulate, evaluation continues to the live verdict
[9] COUNTRY condition: rule skipped with a warning, never guessed
```

**Tests +25:** 17 unit (decode, masks, OR/AND, accumulation, truncation, weekday bitmask,
comment operators, deviation maths, unsupported-skip, missing-context, byte round-trip,
live-table intent) + 8 integration through the real stack (reject stops the order with
the configured reason and moves no money; CONFIRM_CLIENT fills; CLEAR_SLTP strips and
execution continues; a 120 ms delay measurably delays the fill; dealer-with-skip executes
normally when no session exists; dealer-without-skip parks with the queue and books
nothing; margin at the client price).

**Cloud (29/29):** migrate 001→**007** on PostgreSQL 18.6 · `cli seed --mt5-routing` against
the raw UTF-16 export (2 rules) · boot log: `SmartOrderRouter loaded 2 MT5 routing
rule(s): dealer, Auto Execution` · the proof's order logged
`MT5 routing rule 'Auto Execution' confirms execution (CONFIRM_CLIENT) ... proceeding to
normal routing` → FILLED at the live price, margin to the cent · pricing + swap + Redis
bus + clean shutdown as before.

## 3. Known gaps (documented, not hidden)

1. **Dealer sessions don't exist**: `TO_DEALER` parks the order in `DealerQueueService`
   (30 s timeout) with no terminal to service it. The dealer UI/protocol + online
   presence is what makes the live `dealer` rule fully executable; until then its
   skip-if-offline flag is what keeps real-group flow moving (and says so in the log).
2. **Requote / confirm-by-dealer / cancel-on-activation** need the dealer terminal
   protocol; they refuse honestly today.
3. **Rule changes at runtime**: MT5 re-queues in-flight requests when the table changes.
   Rules load at startup (`refresh_rules`); an admin CRUD surface + re-queue semantics
   belong to the dealer/admin milestone. Single-node inline execution has no in-flight
   window to re-queue today.
4. **Delay-in-ticks** needs a per-symbol tick counter (modelled, refused loudly).
5. Context supplies money fields from the account object but **not** position/order
   counts (4005–4008) — those conditions currently cannot match; the router would need a
   synchronous counts view (ConfigCache has positions; M9 wiring).
6. Post-trade valuation (equity loop, position PnL) still reads raw ticks; only the
   pre-trade path is client-priced (M7 gap list, unchanged).

## 4. Where this leaves the plan

| Piece | Status |
|---|---|
| Config · risk maths · B-Book execution · deployment · debt · login · pricing | done (M0–M7) |
| **Routing request-policy table** | **done (M8)** — your live rules load, replay and drive cloud orders |
| SL/TP + expiration execution (server-side) | **next (M9)** — CLEAR_SLTP now has something to clear; triggers still don't fire |
| Adapters: trade-server WS feed · quickfixn FIX gateway | M10 |
| Dealer sessions/terminal · ECN · journal/backup · cluster roles | M11+ |
