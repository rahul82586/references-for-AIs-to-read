# M11 — Is an A-Book destination a trade?

**Question this milestone answers:** *when the platform hedges client flow at a real
liquidity provider, does the client actually get a trade?*

**Status: COMPLETE.** Test suite **436 → 448 passed / 0 failed**. New proof
`scripts/m11_proof_a_book.py`: **39/39**. All legacy proofs green (m1 362/362,
m1-all-sections 392/392, m2, m3 ×3, m4). `m8` 18/18, `m9` 14/14, `m10` 19/19.
Local E2E 15/15. **`make proofs` → 14/14 gates green.**

Before M11 the answer was no. M10 built a real FIX 4.4 gateway that returns a real
FILLED execution report — and `ExecutionOrchestrator._execute_a_book` dropped it on
the floor:

```python
execution_report = await self.liquidity_gateway.send_order(order=order, gateway_id=...)
if order.state is not OrderState.PLACED and not order.is_terminal():
    order.transition_to(OrderState.PLACED)
await self.order_repo.save(order)
await self.event_bus.publish(DomainEvent(event_type=EventType.ORDER_ROUTED, ...))
```

No deal. No position. No margin recompute. No release of the M6 reservation. The
client's order sat at PLACED forever while the LP held a live hedge against nothing.
**An A-Book destination was not a trade.**

Worse, the blanket `except Exception` rejected the client order on a `FixTimeout` —
whose own message reads *"hedge state UNKNOWN; reconcile before retrying"*. Rejecting
the client while the LP may be holding the hedge leaves the broker with naked risk
and no record of either side. That is the most expensive failure mode in the file.

---

## 1. The four outcomes, each handled explicitly

| LP result | Client side | Reservation | Coverage |
|---|---|---|---|
| **FILLED / PARTIAL** | booked through the **same path B-Book uses** (`_apply_deal_to_account` → `RecordDealHandler`) at the LP's own price and volume | released (proportionally, on a partial) | **unchanged** — a real hedge means the risk was passed on |
| **ACK / ACK_STUB** | nothing booked; the order rests at the LP | **kept** — still live, still needs margin | unchanged |
| **`FixTimeout`** (hedge state UNKNOWN) | **neither booked nor rejected**; order left as-is and flagged `HEDGE_STATE_UNKNOWN` + `reconciliation_required` | **kept** until the break is resolved | unchanged |
| **anything else** | the LP definitively refused → client order rejected through the existing single funnel | released by that funnel | unchanged |

The UNKNOWN branch is the one that matters most. Rejecting invents a client-side
cancel of a hedge that may exist; booking invents a client position against a hedge
that may not. Leaving it alone, holding the margin, and flagging it is the only
honest outcome — and it is what the gateway's own exception message asks for.

`OrderState` was **not** extended with an `UNKNOWN` member: that enum mirrors
`IMTOrder::EnOrderState` and adding to it would break the wire fidelity the whole
project is built on. The state lives in the event payload instead.

## 2. Coverage semantics — the easy thing to get backwards

**B-Book:** the broker *is* the counterparty, so client BUY → broker SHORT and the
coverage account moves. Existing, correct, untouched.

**A-Book, real hedge:** the broker passed the risk **on**, so its net exposure is
unchanged and the coverage account must **not** move. Moving it would double-count
risk the broker no longer holds and would drive the NOP 70/85/95% thresholds against
a position that does not exist.

**A-Book, `stub: True`:** there is no hedge, so the broker has in fact kept the
client's risk — economically a B-Book fill. Coverage moves exactly as B-Book does
(client BUY → broker SHORT → negative delta) and the log says the flow is unhedged.
Silently booking it as "hedged" would understate broker exposure, which is the
dangerous direction.

Proof B pins all three, including the sign.

## 3. Recognition without coupling

The orchestrator must not import `FixTimeout` to be correct — a stub-only or REST
deployment has no such class. So:

```python
def _hedge_state_unknown(exc: BaseException) -> bool:
    if getattr(exc, "hedge_state_unknown", False):
        return True
    return type(exc).__name__ == "FixTimeout"
```

Any adapter can opt in by setting `hedge_state_unknown = True` on the exception it
raises, which is the honest signal: **only the adapter knows whether it had already
written to the socket.** The same predicate covers a non-dict report, which is
treated as UNKNOWN rather than as a fill.

## 4. Malformed reports are refused, never guessed

* **FILLED with no `AvgPx`** — the hedge is live, so refusing to book is worse than
  booking. It books at the order's own price and adds a reconciliation flag. Loud.
* **LP over-reports volume** (says 0.50 against 0.10 requested) — clamped to what is
  outstanding and flagged. The LP may not create client volume the client never asked
  for.
* **Zero-volume "fill"** — nothing booked, flagged `NO_FILLED_VOLUME`.
* **Account not loadable / booking fails after the LP filled** — **not** rejected
  (that would cancel the client side of a live hedge). Logged as an error and
  published as `RECONCILIATION_REQUIRED` with the reason. A break for the back
  office, not a trading decision.

This is the project's *refuse rather than fake* law applied to the LP boundary.

## 5. Two defects fixed en route

**`_apply_deal_to_account` hard-coded `volume=order.volume_initial.value`**, so it
could only ever book a complete fill; a second partial would have raised *"fill
volume exceeds remaining"* inside `Order.apply_fill`. It now takes the volume to
book. This is the first partial-fill path in the codebase — the OMS gap list has
carried "no partial fills" since M4.

**`RecordDealHandler._release_order_reservation` released the order's ENTIRE hold on
any deal.** Correct for a full fill, wrong for a partial: the remainder is still live
at the LP and still needs margin, and releasing the whole hold would leave it
reserved by nothing at all. It now releases in proportion to the volume that actually
filled — **identical to today's behaviour when the order completes**, so B-Book is
unaffected. Proof C4/C5 pin it: a 0.04 partial on a 0.10 order leaves
`reserved=66.006` (60% of the original 110.01), and the account hold equals the order
hold.

## 6. What is proven

**`scripts/m11_proof_a_book.py` — 39/39, through the real stack** (CreateOrderHandler
→ risk → SmartOrderRouter → orchestrator → RecordDealHandler) with a scripted
`ILiquidityGateway` so every branch is reachable deterministically:

```
A  the LP fills            order FILLED · 1 deal at the LP's price · 1 position ·
                           margin recomputed · margin_level derived not 0 (D1) ·
                           reservation released · hedge context on the event
B  coverage semantics      real hedge -> 0 movement, no exposure_updates
                           stub fill  -> -0.10, hedged=False, delta -0.10
C  partial fills           PARTIALLY_FILLED · 0.06 outstanding · deal for 0.04 ·
                           remainder keeps a proportional reservation (66.006)
D  ACK / resting           PLACED · no deal · no position · reservation KEPT ·
                           RESTING_AT_LP, not flagged
E  hedge state UNKNOWN     NOT rejected · no OrderRejected · nothing booked ·
                           reservation survives · HEDGE_STATE_UNKNOWN flagged
F  LP definitely refused   REJECTED · reason names the gateway · nothing booked ·
                           reservation released
G  malformed reports       no AvgPx -> books + flags · over-report -> clamped +
                           flags · zero volume -> nothing + NO_FILLED_VOLUME ·
                           non-dict -> UNKNOWN not a fill
```

**`tests/integration/test_m11_a_book_completion.py` — 12 tests** covering the same
ground inside the suite.

**Two existing assertions were strengthened, not deleted.** `test_m10_adapters_live.py`
and `m10_proof_adapters.py` B2/B3 both asserted on the old `ORDER_ROUTED` payload key
`execution_report` — i.e. they proved *the LP received a NewOrderSingle*, which passed
for the whole of M10 **while the client received no trade at all**. They now assert the
A-Book `DEAL_CREATED` event, a real deal at the LP's price, a real position, and zero
coverage movement. `m10_proof_adapters` is still **19/19**.

That is the honest reading of this milestone: the M10 gate was green and the feature
was absent, because the gate measured the message rather than the trade.

## 7. Known debt (documented, not hidden)

1. **No drop-copy (35=Z) or EOD reconciliation.** A `HEDGE_STATE_UNKNOWN` break is now
   correctly flagged and holds its margin, but nothing *resolves* it. There is no
   reconciler, no LP status-request (`35=H`) sweep, and no operator surface. This is
   the natural next increment.
2. **No resting-order lifecycle at the LP.** An ACK leaves the order PLACED forever.
   Nothing consumes a later ExecutionReport that fills it, and `cancel_order` is not
   reachable from a client cancel for A-Book orders. Partial-then-complete is not wired.
3. **The client fills at the LP's raw price.** M7's group spread transform is applied
   when *pricing* the order for risk and for B-Book fills, but the A-Book booking takes
   `AvgPx` from the report as-is. If a group's markup is meant to be earned on A-Book
   flow too, that is a separate decision and is not implemented.
4. **`QuickFixSession` still has never talked to a real LP** (M10 debt, unchanged).
   Everything above it is now tested against `SimulatedFixSession` and the scripted
   gateway; the untested surface remains the quickfix callback marshalling.
5. **`_execute_in_house` (ECN) and `_send_to_dealer` still do not book** either. M11
   closed the A-Book path; the ECN destination remains at ~5%.
6. Post-trade valuation still reads raw ticks (M7 gap #1, unchanged).

## 8. Files

**New:** `scripts/m11_proof_a_book.py` · `scripts/m11_patch_a_book_completion.py`
(idempotent, kept for the audit trail) · `tests/integration/test_m11_a_book_completion.py`

**Modified:** `application/services/execution_orchestrator.py` (the A-Book path,
`_apply_deal_to_account`, the `_hedge_state_unknown` predicate) ·
`application/commands/record_deal.py` (proportional reservation release) ·
`scripts/run_all_proofs.sh` (M11 wired into the gate) ·
`scripts/m10_proof_adapters.py` · `tests/integration/test_m10_adapters_live.py`
(both strengthened to assert the trade)

## 9. Where this leaves the plan

| Piece | Status |
|---|---|
| Config · risk maths · B-Book execution · deployment · debt · login · pricing · routing · SL/TP · adapters | done (M0–M10) |
| `margin_level` written, derived and served correctly · `/account/info` reachable | done (D1+D2) |
| All proofs restorable and runnable from one command | done (`make proofs`, 14 gates) |
| **A-Book completion** | **done (M11)** — an LP fill is now a client trade |
| Drop-copy + reconciliation (resolve `HEDGE_STATE_UNKNOWN`) | **next** |
| Resting-order lifecycle at the LP · ECN booking · dealer terminal | M12+ |
| Journal + snapshot + replay · history plane · process roles → cluster | deferred |