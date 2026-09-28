# MT5 configuration model — corrected against the SDK, the Admin guide, and the live export

**Status: this supersedes my earlier "markup lives on the gateway" claim, which was wrong.**
Written 2026-09-12 after the user corrected the design twice. Every statement below is
pinned to either the SDK headers, the Administrator guide, or the live TCTrader-Live
export in `refs/mt5-format-structure/`.

---

## 1. The pipeline, in order

```
data feed / gateway          pulls prices from the external system
        |
        v
symbol mapping               Source -> Symbol (rename; prefix/suffix handling)
        |
        v
Translations                 ONLY when names differ or carry a prefix/suffix.
                             Carries Bid/Ask markup fields, but that is not its
                             primary job.
        |
        v
GROUP settings               the main place spread / commission / swap / margin /
                             netting-vs-hedging / stop-out / volumes are set
        |
        v
ROUTING rules                decide B-Book vs A-Book vs matching engine vs dealer.
                             Groups do NOT decide this.
```

**Group does not decide A/B book.** Routing does. Verified in the live export: the
`dealer` rule carries `Dealers=[{"Login":"3","Name":"MetaTrader 5 Gateway clone"}]`
— gateway **ID 3** is reached *through the routing rule*, and the rule's own
`Conditions` carry the group filter (`Condition 1001` = GROUP, `ValueString
"real\\real"`). So the group appears in routing as a *condition that selects the
rule*, not as the thing that picks the destination.

Administrator guide, `Gateways/Setup-of-Routing.md`:

> *"For a gateway to start processing trade requests, you should set up their
> routing in the corresponding section... At this tab you should select the
> gateway as a dealer that processes the requests... In addition to the manager
> logins, the list of dealers contains the gateways (ID and name specified at the
> Common tab)."*

A gateway is a **dealer** in a routing rule. That is the whole mechanism.

---

## 2. What Translations is actually for

`Groups/Group-Symbol-Settings` has five tabs (Common, Trade, Execution, Margin,
Margin Rates, Swaps). Translations are on the **gateway/feeder**, not the group,
and their documented purpose is name mapping:

`Gateways/Symbol-and-Price-Translation.md`:

> *"Gateways are able to import necessary sets of trading symbols, manage their
> settings, update them if necessary and provide quotes. Gateway settings allow you
> to easily change data passed from the external system: **Rename trading symbols**,
> Convert quotes, Copy price data to different symbols."*
>
> *"Data on any symbol can be passed from an external system under any name. For
> example, if the symbol name in an external system is EURUSD_ABC, and it is called
> EURUSD in the MetaTrader 5, enter EURUSD in the Symbol field and EURUSD_ABC in the
> Source field."*

Markup fields exist on the row (`BidMarkup`, `AskMarkup`) and the guide does
describe earning from them on the **ECN** path, but renaming is the primary use —
and the live export agrees: **all three gateway configs and three of four feeders
have `Translates: []`**. The one populated row is `{"Source":"*","Symbol":"*!",
"BidMarkup":"0","AskMarkup":"0","Digits":"0"}` — zero markup, and a `!` mask the
guide says the platform *ignores*.

So this broker marks up through **group SpreadDiff**, exactly as the user said.

### Rules that still hold (already implemented, `core/domains/pricing/translation.py`)
* Bid/Ask are in **points of the source symbol** — 1 point = 0.0001 at 4 digits, 0.00001 at 5.
* **First match wins by list order**, not specificity.
* Masks: a **single `*`** only; two `*` or `!` are ignored by the platform.
* Sign convention bid−/ask+ widens; a crossed result is clamped and logged.
* Never applied twice / never compounded.

---

## 3. Where the money is actually configured — GROUPS

### 3a. Group → Symbol Settings → **Common** tab
* `Use default spreads` — **if enabled, all parameters below become inactive** and
  the spread comes from the symbol's own settings. *(M7 models the inherit case via
  the `"default"` sentinel, but this explicit toggle should be checked against
  `GROUP_SYMBOL_FIELDS`.)*
* `Spread difference` — *"difference of a symbol spread for a certain group of users
  from the basic spread of the symbol"*
* `Difference balance` — *"if you set 3 as the spread difference, then the
  distribution can be the following: 3 bid / 0 ask, 2 bid / 1 ask"*
* `Use default volumes` / Minimum / Step / Maximum
* `Use default limit` / `Limit` — cumulative volume in one direction

> *"Price transformation settings (the Spread difference and the Difference balance)
> for a group are applied **after** applying base settings of a symbol."*

**This is M7, already built and tested.** `resolve_spread_settings` + `client_quote`.

### 3b. Group → **Commissions** tab
> *"Commission for processing trading operations is **the main source of revenue for
> brokers**."*

Three **types**:
| Type | Charged to | Notes |
|---|---|---|
| **Standard** | the client | the broker's revenue |
| **Agent** | the broker's funds → an Agent account | IB/rebate; posted as balance deals |
| **Fee** | the client | like standard, but **Instant only**, and written to a separate `Fee` field for split accounting (e.g. part to the broker, part to an exchange) |

**Charge modes**: Instant (per deal, on entry *and* exit), Daily, Monthly.
> *"In case of an instant charge, commission levels can be specified only as
> volume. No other options are available."*

Symbol selection supports masks, max 127 chars. Description is copied to the deal
comment, **truncated at 31 characters**.

**Already built:** `Group.calculate_commission` stacks every matching rule (M3 fixed
three defects here: a wrong discriminator, a `return` inside the loop that applied
only the first rule, and no tier support). `COMMISSION_FIELDS` + `COMMISSION_TIER_FIELDS`
are modelled and round-trip.

**Gaps to check:** the three *types* (standard/agent/fee), the three *charge modes*,
and the separate `Fee` field.

### 3c. Group → Symbol Settings → other tabs
Trade, Execution, Margin, Margin Rates, Swaps. Margin Rates is the 8+8 initial/
maintenance multipliers (M3, built). Swaps is M6 (built).

### 3d. Group-level (not per-symbol)
Netting vs hedging (`EnMarginMode`: RETAIL/EXCHANGE_DISCOUNT = netting,
RETAIL_HEDGED = hedging — M6 fixed the dispatch), stop-out mode and thresholds
(percent), leverage, currency, permissions.

---

## 4. Markup on A-Book — the two legitimate mechanisms

| Mechanism | Where configured | Status here |
|---|---|---|
| **Group SpreadDiff / SpreadDiffBalance** | Group → Symbols → Common | ✅ M7, built — but applied only on the **B-Book** fill path today |
| **Gateway/ECN Translates markup** | Gateway config → Translations | ✅ maths built (M13 part 1), no config plane to hold rows |
| **Commission** | Group → Commissions | ✅ B-Book path charges it at fill |

The Admin guide's ECN example (`EURUSD.ECN → EURUSD.USR` at −2/+2, *"the broker earns
the profit of 2 pips"*) is the Translates mechanism. Ultency's marketing page adds
*"For each client/group, you can assign liquidity providers to execute their orders,
as well as individual markups"* — which is the **cloned-gateway-per-group** pattern:
two configs of the same module differing only in `Groups`, one named "clone".

### The real gap, measured — and it is not what debt item 14 says

Debt item 14 claims *"A-Book fills at the LP's raw price, so a group markup is not
earned on A-Book flow."* **That is wrong, and the opposite is also wrong.** Measured
against the real stack with a group SpreadDiff of 20 points, raw ask 1.10010, and a
venue whose own ask is 1.10000:

```
raw feed ask               1.10010
group SpreadDiff 20 pts -> client price 1.10030
price we SENT to the LP    1.10030     <-- the CLIENT price, not the raw feed
price the LP FILLED at     1.10000     <-- its own, better than we quoted
price we BOOKED the client 1.10000     <-- the LP's, not the client's
broker margin on the hedge 0.00000 = 0 points
```

Two separate defects, pulling in opposite directions:

1. **We send the marked-up client price to the LP.** The order carries
   `price_order` = the client price (M8 closed the "risk sees the client price"
   gap), and `TradeServerLiquidityGateway`/`FixLiquidityGateway` forward
   `order.price_order.value` as the limit/stop price. So for any price-limited
   instruction we ask the venue to trade 20 points *worse* than the market. A real
   LP either rejects it or fills at market and we have leaked our markup into the
   request. **The hedge leg must be sent the raw or source-side price, never the
   client price.**
2. **We book the client at the LP's fill price, discarding the markup.** M11 books
   at `report["price"]` — the venue's number. So the group SpreadDiff that the
   client was quoted, and that the risk check and margin reservation used, is
   thrown away at booking. When the LP fills better than we quoted, the client
   keeps the improvement and the broker earns nothing; when it fills worse, the
   client is charged worse than quoted.

In the run above the two happen to cancel to exactly zero, which is the worst
outcome: it looks like the markup is "not working" rather than visibly broken, and
no test catches it because both numbers are plausible.

**The correct MT5 shape**, from the guide's ECN example:

```
client is QUOTED and FILLED at the converted price (1.15661)
the venue receives and fills at the ORIGINAL price (1.15659)
"the broker earns the profit of 2 pips"
```

So: client side books at the **client price**, venue side is sent and filled at the
**source price**, and the difference is the broker's. That requires M11's A-Book
booking to stop taking `report["price"]` as the client's fill and instead use the
client quote, while recording the venue's price separately as the hedge cost. The
difference is the markup revenue, and it should be visible as such — not buried in
a fill price.

---

## 5. What this changes in the build plan

**Was:** gateway config plane → wire translation into A-Book.

**Now, in the order MT5 actually does it:**

1. **Apply the group's existing spread transform on the A-Book path.** M7's
   `client_quote` is already correct and already per-group; the A-Book booking just
   doesn't call it. This earns the markup the broker has *already configured*, with
   no new schema. **Highest value, smallest change.**
2. **Commission on A-Book fills.** `_commission_for(order, account)` is already
   called in `_apply_deal_to_account`, so verify it fires on the A-Book path too
   rather than assuming it does.
3. **Gateway config plane** (`mt5_gateways` + `Translates`) — needed for the
   *rename* use case first (venue calls it `EURUSD_ABC`, we call it `EURUSD`), and
   for ECN-style markup second. Migration 009.
4. **Commission types and charge modes** — standard/agent/fee, instant/daily/monthly.
   Agent commission is a whole IB subsystem; scope it separately.
5. **`Use default spreads` / `Use default volumes` / `Use default limit` toggles** —
   verify these explicit flags are modelled, not just inferred from the `"default"`
   sentinel.

Routing stays where it is: **M8 is correct.** Groups select routing rules as a
*condition*; the rule's action and dealer list decide the destination. Nothing in
the group configuration picks A-Book or B-Book.
