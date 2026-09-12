# M9 — Server-side SL/TP, order expiration, routing position counts

**Question this milestone answers:** *when the client disconnects, does the
server still honour the stop the client set?*

Before M9 the answer was no. Three pieces of the execution plane were
decoration:

1. **SL/TP were dropped.** `CreateOrderCommand` carried `stop_loss`/
   `take_profit` onto the order, but `record_deal` never transferred them to
   the position it created, and nothing watched ticks. A stop set over HTTP
   was stored and then ignored forever.
2. **Expiration was a column nothing read.** `Order.time_expiration` existed,
   `find_expired_orders` existed in the repository, and no caller existed.
3. **Routing conditions 4005/4006 had no data source.** `POSITION_TOTAL` and
   `POSITION_TOTAL_SYMBOL` were parsed and compared, but the router's context
   never supplied counts, so any rule using them silently matched nothing.

## What changed

### 1. SL/TP carry onto positions
`record_deal.py` now threads the originating `order` through
`_apply_deal_hedging` / `_apply_deal_netting`, and the new position is
constructed with `price_sl=order.price_sl, price_tp=order.price_tp`. Applies to
both the hedging open and the netting reversal (which creates a position in the
opposite direction).

### 2. `SlTpWorker` (`application/workers/sltp_worker.py`)
Subscribes to `TICK_RECEIVED` and, for every open position with an SL or TP,
checks the correct side of the quote:

| position | SL fires on | TP fires on |
|---|---|---|
| BUY  | bid ≤ `price_sl` | bid ≥ `price_tp` |
| SELL | ask ≥ `price_sl` | ask ≤ `price_tp` |

It closes through `ClosePositionHandler` at the **market price of that tick**,
not at the trigger level. The trigger is not a price promise: on a weekend gap
a stop at 1.09500 with the market at 1.08000 books a −201.00 loss, not the
−51.00 the stop implied. The proof pins that number.

In-flight position ids are tracked in a set so two ticks arriving before the
first close is persisted cannot close the same position twice.

### 3. Close reasons
`OrderReason` gained `SL`, `TP`, `SO`. `ClosePositionCommand.reason` now flows
to both the closing deal's reason and the closing order's reason, so a position
closed by a stop is auditable as `SL` in the deal history, the order history,
and the `PositionClosed` event. Stop-out liquidation passes `SO`.

### 4. `ExpirationWorker` (`application/workers/expiration_worker.py`)
Sweeps on a timer (default 60 s) and cancels pendings whose `time_expiration`
has passed. The first sweep is immediate, so expirations that passed **while
the server was down** fire on boot rather than being silently forgotten. Each
cancellation publishes `OrderCancelled` and stamps the comment. An expired
pending never executes: zero deals.

`find_expired_orders` in `SqlOrderRepository` filtered on
`["NEW", "PLACED", "PARTIALLY_FILLED"]`, but the engine creates orders in state
`STARTED`. Added `STARTED` to the filter — without it a resting order placed
moments before shutdown was invisible to the sweeper.

### 5. End-to-end expiration
`CreateOrderCommand.expiration` → `Order.time_expiration` →
`CreateOrderRequest.expiration` (Pydantic, ISO-8601 UTC) → router. A client can
now place a real GTD order over HTTP.

### 6. Routing position counts
`SmartOrderRouter` takes an optional `counts_fn(login, symbol) -> (total,
symbol)` and puts both numbers in the routing context, which makes conditions
4005/4006 live. In `trading_setup` that function reads the `ConfigCache`
positions slice — synchronous, no `await` inside the router's condition loop.

The cache stays honest because it now refreshes its positions slice on
`DealCreated` and `PositionClosed`, not only on account/group/symbol changes.
Without that, the count-based rule would be one fill stale and would let a
second position through.

### 7. `ClosePositionHandler` registration
The manager `OrderClose` endpoint had been refusing since M2 because no DI
provider registered a close handler. `trading_setup` now builds
`ClosePositionHandler` with the risk engine (so realised PnL goes through the
M6 currency conversion path) and the SL/TP worker, exports both in
`as_providers()`, and `wire_trading_subscriptions` starts the worker.

### 8. Clean shutdown
`api/main.py` stops both new workers on shutdown. `SlTpWorker.stop()`
unsubscribes from the tick stream, so it cannot outlive the bus it publishes
closes onto. The cloud proof gained 4 checks covering boot and stop for both.

## Proofs

```
PYTHONPATH=$PWD python3 scripts/m9_proof_sltp_expiration.py
```
14 checks, 0 failures:

```
[PASS] SL/TP carried from the order onto the position
[PASS] quiet tick inside the corridor fires nothing
[PASS] SL fired: position closed at the MARKET bid, not the stop level -- balance 9948.0
[PASS] closing deal is booked with reason SL
[PASS] closing order carries reason SL
[PASS] SELL TP fired on the ask, gain booked in the account currency -- balance 10050.0
[PASS] gapped market closes at the market: loss -201.00, not the -51 the stop implied
[PASS] all three pendings are resting PLACED before the sweep
[PASS] sweep cancels exactly the expired order (1), leaves future-GTD and GTC resting
[PASS] OrderCancelled published for the expired order
[PASS] an expired pending never executed: zero deals
[PASS] first buy fills while the position count is 0
[PASS] second buy is rejected by POSITION_TOTAL_SYMBOL >= 1 (counts refreshed via events)
[PASS] exactly one position open - the table enforced its limit
```

## Verification

| gate | result |
|---|---|
| full suite | **384 passed** (was 374; +10 in `tests/integration/test_m9_sltp_expiration.py`) |
| `ruff check --select E9,F63,F7,F82 .` | All checks passed |
| legacy proofs m1–m4, m8 | 7/7 PASSED |
| cloud proof `scripts/m5_proof_cloud.sh` | **33 passed, 0 failed** (was 29; +4 M9 worker lifecycle checks) |

The cloud run exercises Neon Postgres, Upstash Redis, real HTTP auth, a real
market fill, and now confirms both new workers arm on the live tick stream and
stop cleanly on shutdown.

## Known debt

- **SL/TP are not persisted-and-rearmed across restarts on the in-memory
  harness path.** The SQL repository loads positions on boot and the worker
  reads the cache, so the production path does rearm; there is no test proving
  a restart-with-open-SL fires the stop. That is an M10+ boot-recovery test.
- **No trailing stops, no SL/TP modification endpoint.** MT5 supports
  `TradeAction.SLTP`; `PositionModify` is not exposed over HTTP yet.
- **Expiration sweep granularity is the sweep interval** (default 60 s). An
  order expiring at 12:00:30 is cancelled by the 12:01:00 sweep. MT5 does this
  on the tick too, so it is not wrong, but it is not documented to clients.
- **`counts_fn` reads a cache, not the database.** If the cache is cold or a
  position was written by another process, a count-based rule can be stale.
  The refresh-on-event path covers the single-process case; a multi-worker
  deployment needs the cache to subscribe to the Redis bus (it does when
  `EVENT_BUS=redis`, but that is untested for positions specifically).
- **`OrderReason.SO` is emitted by the liquidation worker but no proof
  exercises stop-out end-to-end at the deal-reason level.** The M3 margin
  proofs cover the liquidation mechanics.
- Two patch scripts (`scripts/m9_patch_sltp_expiration.py`,
  `scripts/m9_patch_part2.py`) are one-shot and are kept for the audit trail,
  not for re-running.

## Files touched

New: `application/workers/sltp_worker.py`,
`application/workers/expiration_worker.py`,
`tests/integration/test_m9_sltp_expiration.py`,
`scripts/m9_proof_sltp_expiration.py`.

Modified: `api/main.py`, `api/routers/trade.py`, `api/schemas/trade.py`,
`application/cache/config_cache.py`,
`application/commands/{close_position,create_order,record_deal}.py`,
`application/di/trading_setup.py`, `core/domains/execution/router.py`,
`core/domains/oms/enums.py`,
`infrastructure/persistence/repositories/order_repository.py`,
`scripts/m5_proof_cloud.sh`, `tests/integration/trading_harness.py`.
