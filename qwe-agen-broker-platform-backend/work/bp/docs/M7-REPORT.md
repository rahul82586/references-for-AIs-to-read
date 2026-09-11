# M7 — Does the broker earn its spread?

**Status: COMPLETE.** Test suite **326 → 349 passed / 0 failed**. All six legacy proofs
green — including the wire round-trip (**362/362 symbols + 20/20 groups byte-identical**)
with two more fields moved OUT of quarantine INTO the domain. Cloud proof **29/29** on
Neon + Upstash, migration chain now at **006**, and the live server log shows
`client pricing enabled` at boot.

The milestone question: every fill left the house at the RAW feed price. Group `SpreadDiff`
was quarantined out of the wire format and never applied, symbol `Spread`/`SpreadBalance`
were stored but read by nothing, and the broker earned nothing on spread. It was the
largest functional zero left, and the routing engine's deviation-from-market conditions
(M8) need priced quotes to mean anything.

---

## 1. What was built

### The maths — `core/domains/pricing/` (pure domain, pinned to the Administrator guide)

| Rule | Source | Behaviour |
|---|---|---|
| **Fixed spread** | Symbols → Common: "If the value of this field is non-zero, the spread will be considered fixed… calculated using the Spread balance parameter" | `Spread > 0` ⇒ client spread is **exactly** Spread points: `SpreadBalance` of them below the raw bid, the rest above it. The feed's own ask is replaced |
| **Spread difference** | Groups → Group Symbol Settings → Common: "if you set 3 as the spread difference, the distribution can be 3 bid/0 ask, 2 bid/1 ask" | `SpreadDiffBalance` points lower the client **bid**; the remainder raise the client **ask** |
| **Order of application** | "Price transformation settings for a group are applied AFTER base settings of a symbol" | fixed spread first, then the difference |
| **Inheritance** | "Default… the basic symbol configuration will be used" | an override of `None`/"default" inherits — it never means zero |
| **Guards** | — | negative diff tightens the spread; `ask ≥ bid` clamped; a non-positive client bid raises rather than trading |

### The model — four quarantined wire fields promoted

`Symbol.spread_diff` + `spread_diff_balance` (fieldmap → loader keys → columns +
**migration 006** → all five mapper hops → export) and
`GroupSymbolOverride.spread_diff_balance`. The reference export's EURUSD carries
`SpreadDiff="0"`, `SpreadDiffBalance="0"` — those literals now flow through the domain
and re-export byte-identically, which the round-trip proof re-verified.

### The application point — one funnel, per group

`BookMatchingEngine` gained an optional `quote_provider(symbol, account_login)`, consulted
at the top of `_quote_for` — the single method every fill price flows through (market
fills, limit/stop activation, slippage checks). `trading_setup` wires the provider
whenever a ConfigCache exists; without one the engine prices raw, as before. The raw
`_quotes` store stays raw: **the transform is per group, the store is shared** — two
clients on two groups see two prices off the same tick, which is what MT5 does.

### Stale quotes refuse (the Centroid rule)

`PRICING_MAX_TICK_AGE_SECONDS` (default 60; 0 disables). The engine already filtered old
ticks **at ingestion**; this covers the other half — a quote that *was* fresh while the
market went quiet. A market order against a stale quote is REJECTED with the reason in the
comment; resting pendings survive the stale tick and activate on a fresh one (tested both
ways). Same honesty as the A-Book stub: refuse rather than fake.

### Two semantics fixed en route (found by the new tests)

* `Order.apply_fill` received the fill price and **ignored it**: a filled market order
  kept its request-time price, so the API response and the deal could disagree once
  fills are marked up. Market orders now stamp the execution price (MT5: a market
  order's price IS its execution price); pendings keep the client's instruction.
* The provider's group lookup used `cache.get_group(account.group_id)` — the cache keys
  groups by **uuid** while `account.group_id` holds the **name**, so it never resolved
  and every order priced without group overrides. Now `account.group` first (attached by
  both the SQL mapper and the harness), cache as fallback. Plus: override
  deserialization leaked the `"default"` sentinel string into VOs (now `None`).

## 2. What is proven

**Units (13):** the guide's own distribution example (diff 3 = 2 bid/1 ask) · fixed
spread exactly N points around the raw bid · stacking order · negative diff clamps ·
zero point no-ops · non-positive bid raises · resolution (base → first-match override →
inheritance) · mask patterns · codec both ways · mapper round trip · INHERIT sentinel
survives storage.

**Integration (7, through the real stack):** group `SpreadDiff=20` raises the buyer's
price to `ASK+20pts` and leaves the seller at the raw bid · `balance=20` moves the bid
instead · symbol fixed spread 30/10 replaces the feed spread · **default config
reproduces pre-M7 fills exactly** (the whole existing e2e suite is the regression proof)
· stale quote rejects the order and books nothing · resting pending survives staleness
and fills at the group-priced `min(client ask, limit)` · an account missing from the
cache prices at symbol settings rather than being refused.

**Cloud (29/29):** migrate 001→006 on PostgreSQL 18.6 · seed idempotent · boot with
`client pricing enabled` + SwapWorker · health db 14.6ms/bus 62.2ms · password-verified
login · BUY 0.10 EURUSD FILLED (seeded symbols float: `spread: 0`, so the fill price is
unchanged — the seeded broker runs raw spreads until you configure a diff) · positions
API truthful · cross-process ticks via Upstash · clean shutdown.

## 3. Known gaps (documented, not hidden)

1. **Margin/risk still values at raw ticks.** Pre-trade margin, the equity loop and
   position PnL read `MarketDataEngine` directly. The inconsistency is bounded by the
   spread width and leans conservative for the broker (entry priced with markup, margin
   without), but M8 should route the risk engine's price reads through the same
   provider for the ordering account.
2. Per-day `SwapRate{Sun..Sat}`-style **markup curves** and percent/absolute markups
   beyond SpreadDiff: the wire in your export has no separate markup fields; ECN
   translation markups arrive with the ECN work.
3. Mask language supports `*` and prefix; `!` negation is documented, not implemented.
4. Client-facing quote endpoints (WS market data, `/market-data/history`) still serve
   raw ticks; per-subscriber group pricing there belongs to the client-terminal work.

## 4. Where this leaves the plan

| Piece | Status |
|---|---|
| Config plane · risk maths · B-Book execution · deployment · debt queue · login | done (M0–M6) |
| **Pricing / spread / markup** | **done (M7)** — the broker earns its spread the moment a group carries a SpreadDiff |
| Routing rules engine (MT5 action/condition taxonomy) | **next (M8)** — deviation-in-points conditions now have priced quotes to check against |
| SL/TP + expiration execution | M9 candidate |
| Adapters: trade-server WS feed · quickfixn FIX gateway | M10 |
