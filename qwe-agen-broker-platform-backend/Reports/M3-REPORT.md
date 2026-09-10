# M3 — Is the risk maths trustworthy?

**Status: COMPLETE.** Test suite **154 passed / 12 failed → 210 passed / 0 failed**.
MT5 format constraint preserved: **362/362 symbols and 20/20 groups still re-export
field-identically**.

M3 was scoped as six items. Delivering them required finding and fixing **five independent
copies of the margin formula**, a **discarded MT5 field** that was the root cause of the
cross-currency bugs, and a **deal-recording handler that could not execute at all**. Several
of the six items turned out to be symptoms rather than causes.

---

## What the reference repos and the MT5 SDK actually said

M3 was built from sources, not from assumption. Four of them changed the design:

**The MT5 Administrator docs (`Platform-Setup.md`)** are the authority, and they specify a
**four-stage pipeline**, not a formula:

| Stage | Rule | Source |
|---|---|---|
| 1. Basic | Forex: `volume × contract / leverage` (no price term). CFD: `× price`. CFD-leverage: `× price / leverage`. Futures: `volume × initial_margin`. | `Margin-Calculation/Basic.md` |
| 2. Conversion | margin currency → deposit currency. **Ask for buy deals, Bid for sell deals.** | `…—Hedging.md #conversion` |
| 3. Rate | × the operation's multiplier. **8 initial + 8 maintenance.** Zero maintenance ⇒ inherit initial. | `…—Hedging.md #rate` |
| 4. Aggregation | same direction ⇒ weighted average price. Opposite ⇒ uncovered + covered volume; covered charged at `Hedged margin`. Pending orders **always at initial**. | `…—Hedging.md #hedging`, `Leverages.md` |

Published worked examples now reproduced to the cent by `scripts/m3_proof_margin.py`:
`1 × 100000 / 100 = EUR 1000` · `1000 EUR × 1.2790 = 1279 USD` · `1279 × 1.15 = 1470.85` ·
`2315.00 + 770.60 = 3085.60` · `22 × 100000 / 100 = 22000`.

**`tfrmma/oms-order-management-system`** contributed the conservatism rule now implemented in
`available_margin()`: *"negative upnl reduces available margin, positive doesn't count"* — a
local estimate that has drifted optimistic must not be allowed to authorise a trade. Its
two-layer model (fast local estimate + authoritative reconciliation) is the shape M4's
orchestrator should follow.

**`nautilus_trader`** (`crates/risk/src/engine/mod.rs`) confirmed three design points:
position-reducing orders **skip** the margin check; free balance is looked up **in the margin
requirement's own currency**; and there are both per-order and cumulative margin checks.

**`llc-993/matching-core`** — its `MarginEngine` is `todo!()` throughout, so it offered no
usable logic. Noted so it isn't revisited.

---

## The root cause: MT5's three symbol currencies were being thrown away

M1's `fieldmap.py` had already diagnosed this and left it unmapped:

```python
# CurrencyProfit and CurrencyMargin are the root cause of our cross-currency
# PnL and margin bugs: the margin currency need not equal the quote currency.
Field("CurrencyProfit", "", STR),     # <- discarded
Field("CurrencyMargin", "", STR),     # <- discarded
```

MT5 keeps **three** currencies per symbol: `CurrencyBase`, `CurrencyProfit` (what PnL is
denominated in), `CurrencyMargin` (what the requirement is computed in). For a plain FX pair
they align with base/quote, which is why the omission survived on EURUSD.

Measured against all 362 reference symbols, the fallback — deriving currencies from the
symbol **name** — is not a minor imprecision:

| | count |
|---|---|
| name heuristic matches MT5 | **109** |
| name heuristic is **wrong** | **60** |
| name heuristic **cannot parse** | **193** |

`AUS200.spot` → `("AUS","200")` where MT5 says USD/USD. `EU50.spot` → `("EU5","0.S")` where
MT5 says USD/**EUR**. `BUND`, `MC.FR`, `EWT`, `GRUB`, `ILMN` — single equities and bonds —
are not currency pairs at all.

Worse, the heuristic **never even ran**: `Symbol.base_currency` defaulted to `"USD"`, so
`__post_init__`'s `if not self.base_currency` was permanently false. Every symbol constructed
without explicit currencies silently became USD/USD — EURJPY included. That is the direct
cause of the two cross-currency test failures that had been sitting in the suite since before
M0.

And a third layer: `symbol_to_db` resolved the quote currency from
`extra.get("CurrencyQuote")` — **a key MT5 never emits** — so even a correctly parsed value
was discarded on the way into the database.

All three now fixed. `scripts/m3_proof_currencies.py` verifies **362/362 populated, 0
currency-field mismatches, 362/362 field-identical on re-export**. The wire format is
unaffected: these fields were already round-tripping through the quarantine, so modelling
them changed no byte of the export.

---

## Five margin formulas, not the two M0 counted

| # | Location | Formula it used | Defect |
|---|---|---|---|
| 1 | `Group.calculate_margin` | `(vol × contract × price × rate) / min(lev_default, lev_max)` | CFD formula applied to Forex; leverage resolution wrong; always the BUY rate |
| 2 | `Position.calculate_margin_required` | `(vol × contract × price_open × rate) / lev` | price term on Forex |
| 3 | `RiskEngine.calculate_margin_level` | `(price × vol × contract) / lev` | no margin rate at all; read `position.side` / `.average_price` / `.id` → **AttributeError → zero** |
| 4 | `risk_service._check_margin_requirement` | inline fourth copy | `order.order_type.startswith("BUY")` on an **enum** → AttributeError on *every* order |
| 5 | `record_deal._recalculate_account_margin` | `symbol.calculate_margin_required(...)` | **method exists on Position, not Symbol** → AttributeError on *every* deal |

Applying the price-dependent formula to every symbol over-charges Forex margin by a factor of
the price: **~1.1× on EURUSD, ~150× on USDJPY, ~2000× on BTCUSD**.

All five now route through `core/domains/market_data/margin.py`, which implements the four
stages and is tested against MT5's published numbers (37 tests).

---

## Bugs found that were not on the M3 list

**`RecordDealHandler` could not execute a single deal.** Beyond the fifth formula above, it
read `account.login_id` at **nine** sites — `Account` has `login` — and constructed
`Position(id=, side=, average_price=, opened_at=)` where the entity has `position_id`,
`action`, `price_open`, `time_create`. Every path raised `AttributeError`: opening, closing
and reversing. The system had never recorded a trade end to end. `get_account_info` had the
same `login_id` read, so the account-info endpoint 500s.

**Conversion side was discarded.** `_rate_lookup(from, to, side)` dropped `side` and always
took the direct pair's **bid**. MT5 requires ask for buys. This understated every buy's margin
requirement by the width of the spread — systematically in the client's favour, which is the
direction a broker cannot afford to be wrong in. Inverting a pair swaps the spread side
(broker's ask on USDJPY = broker's bid on JPYUSD); that is now handled.

**Liquidation seeded from a stored field.** `remaining_margin = account.margin_used.amount`
is whatever the last recalculation wrote — zero on a freshly built account. The loop's first
statement, `if remaining_margin <= 0: break`, returned an empty selection. Measured on the
real `demo\Standard` group at **−889% margin level**, the engine selected **zero** positions
to liquidate. An account that cannot be stopped out is the most expensive bug a broker can
have: past zero, it is the broker's capital absorbing the loss.

**Closing a position double-counted its loss.** `equity += pnl` inside the liquidation loop
added a loss that was already in equity, driving it below its real value and liquidating more
positions than necessary.

**Commission never charged.** `calculate_commission` compared `rule.type` against
`"per_lot"`/`"per_deal"` while `CommissionType`'s values are `"volume"`/`"deal"` — so every
rule fell through to `Decimal('0')`. And `return` inside the loop applied only the *first*
matching rule; MT5 stacks them (`real\real` carries three). `CommissionRule` also had no
`tiers` field, so the volume-banded commission MT5 actually uses — `Value 3.5` over
`RangeFrom 0 / RangeTo 1000` in the live export — could not be represented.

**`Position()` could not be constructed.** `price_current` defaulted to
`Price(Decimal('0'))`, and `Price.__post_init__` rejects `<= 0`. Every construction without an
explicit `price_current` raised — including every freshly opened position before its first
tick.

**Margin level could not be read at all.** `detect_margin_call` read
`account.group.margin_call_level`; the fields live on the nested `MarginProfile`. Both
`detect_*` methods raised on every call, so `risk_worker` was dead code.

---

## Tests that asserted the bug

Three tests were encoding defects rather than requirements, and were rewritten to assert MT5:

- `TestMarginCalculation` expected **1,100** for one lot of a 100,000-contract Forex symbol at
  1:100. MT5's own example for exactly these inputs says **1,000**. The test was locking in
  the CFD-formula over-charge. Now asserts the Forex formula, its price-independence, and the
  CFD/CFD-leverage cases separately.
- `test_account_lock_prevents_double_spend` conceded in its own docstring that *"All 5 succeed
  individually against static free margin."* It never decremented free margin, so five
  concurrent orders each saw the full balance and all five passed **whatever the code did**.
  A test that cannot fail is not coverage. Rewritten so 12 lots against 10,000 USD admits
  exactly 10.
- `test_event_bridge_routes_tick` called `bridge._handle_tick(...)` — a method that never
  existed — and asserted on a local `AsyncMock` never connected to the bridge (which resolves
  its own manager from a module singleton). It could not have failed. Now patches the
  singleton the bridge actually uses.

Two M1 tests asserted a **known gap** as a permanent fact (`assert "CurrencyProfit" in
report["missing_fields"]`). They were inverted by their own success and now assert the
stronger property: that the fields *are* modelled and *aren't* in the quarantine, so a future
removal fails.

The remaining risk-test failures were constructor drift against a vocabulary that never
existed (`margin_initial_percent`, `Group(leverage_default=)`, `_get_bid`, `Position(side=)`,
`OrderState.NEW`, `Order(volume=, price=)`). Resynced to the real entities — including making
orders transition `STARTED → PLACED → FILLED`, since the state machine correctly refuses
`STARTED → FILLED`.

---

## Performance: correctness was not allowed to cost latency

Making `Group.calculate_margin` correct took it from **0.158s → 0.708s** per 100k calls,
breaching the existing 0.50s budget. The old code met the budget but returned **2712.50**
where MT5's formula gives **2500** for the same inputs — fast and wrong.

Profiling showed the cost was not arithmetic (`basic_margin` was 0.064s of 0.429s) but
rebuilding a `SymbolMarginSpec` from the caller's dict on every call. Memoised on the dict's
identity, bounded at 256 entries, with `invalidate_margin_spec_cache()` for reconfiguration:

| | 100k calls | result |
|---|---|---|
| old (buggy) | 0.158s | **2712.50** ✗ |
| correct, uncached | 0.708s | 2500.00 ✓ (budget breached) |
| correct, cached | **0.428s** | **2500.00** ✓ |

The budget was **kept at 0.50s rather than relaxed**. Margin is on the pre-trade path.

---

## Files

**New:** `core/domains/market_data/margin.py` (the engine, ~660 lines, fully documented
against MT5's sections) · `tests/unit/domains/market_data/test_mt5_margin.py` (37 tests) ·
`scripts/m3_proof_margin.py` · `scripts/m3_proof_currencies.py` · `scripts/m3_proof_uow.py`

**Rewritten:** `core/domains/risk/engine.py`

**Patched:** `application/services/risk_service.py` · `application/commands/record_deal.py` ·
`application/workers/liquidation_worker.py` · `core/domains/accounts/group.py` ·
`core/domains/accounts/value_objects.py` · `core/domains/instruments/symbol.py` ·
`core/domains/oms/entities/position.py` · `infrastructure/mt5/fieldmap.py` ·
`infrastructure/persistence/config_models.py` · `infrastructure/persistence/config_mappers.py`

**24 patch scripts** under `scripts/m3_*.py`, all wired into `./scripts/m0_run_all.sh`
(now **21 numbered steps** + the CI gate + four proofs). One command rebuilds and replays everything; exit code
0 means all tests and all proofs pass.

```bash
./scripts/m0_run_all.sh          # 210 passed, 4 proofs PASSED, exit 0
```

---

## Not done (unchanged from the M3 plan, and deliberately)

`CreateAccountHandler` / `CreateClientHandler` / `CreateSymbolHandler` (only
`CreateGroupHandler` exists) · `IClientRepository` port · Manager JWT/role enforcement (still
static `ADMIN_API_KEY`) · `must_change_password` not enforced on login · `start` runs only the
`api` role · no Dockerfile / `api` compose service (M5) · orchestrator unwired (M4).

**Deferred by you:** intelligence layer, reporting, cluster, ECN/matching engine, FIX, client
terminal.

**Known limitation introduced by M3, stated plainly:** the leverage **tier** rule
(`Groups/Leverages.md` — margin rates that step up across volume bands, e.g. 10 lots at rate 1
then 2 lots at rate 2) is **not implemented**. MT5's own example takes `22,000 → 36,000` once
tiers apply. The base formula, conversion, rate multiplier, netting and hedged margin are all
correct; tiers are a documented gap, and `MarginBreakdown` has the structure to carry them.
No reference group in the export configures tiers, so nothing in the current data set is
affected.
