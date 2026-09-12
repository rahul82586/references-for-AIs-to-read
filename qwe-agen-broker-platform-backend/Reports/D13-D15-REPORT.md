# D13 · D14 · D15 — what the first real close uncovered

**Date:** 2026-09-12
**Trigger:** running the cloud proof of a client close for the first time —
`scripts/d12_proof_cloud_close.sh`, live MT5 terminal → Neon → Upstash → real HTTP.
**Result:** 596 tests pass, `make proofs` 13/0/1, cloud close proof **41/41**.

The close route worked. Everything underneath it that a close touches for the first
time did not. Three defects, all found in one run, all of the same family the project
has been hunting since D1: *a number computed correctly in one place and served,
stored or written from another.*

---

## D13 — the tick pipeline computed position PnL and threw it away

```
step 4   positions = await position_repo.get_by_symbol(symbol)
         for p in positions: p.update_unrealized_pnl(price, rate)     # in memory
step 5   all_positions = await position_repo.get_by_account(login)     # SECOND fetch
         total = sum(p.profit.amount for p in all_positions)           # reads the DB again
         account.update_equity(total)
         for p in all_positions: await position_repo.save(p)           # saves the STALE rows
```

A SQL repository builds a **new** `Position` on every fetch (`db_to_position(model)`),
so step 5 got fresh copies straight from the database — `profit` 0, `price_current`
NULL — summed those into equity and wrote them back. The objects step 4 had just
repriced were never saved by anyone.

Measured live against Neon with BTCUSD ticks arriving every ~0.6 s
(`scripts/probe_position_repricing.py`):

```
row price_current=None profit=0E-8 | account equity=100000.0000
/account/positions unrealized_pnl=-0.5116        <- computed on demand, correct
```

The client-facing query was right the whole time (M12 revalues on demand), which is
exactly why nobody noticed: **the read path masked the write path.**

Consequences:

* `price_current` stayed NULL for the life of every position, so a market close had
  no price and fell back to `price_open`, booking **zero PnL** — this is what the
  D12 cloud proof tripped over;
* account `equity` was written as `balance`, so it never reflected open PnL;
* `evaluate_margin_state()` saw a flat equity, which made the **margin-call /
  stop-out machine unreachable from ticks**. The heartbeat of the broker was
  decorative.

Why every test missed it: `MockPositionRepository` returns the *same* objects from
both fetches, so the in-memory mutation was visible to step 5. The double was more
coherent than the database. `CopyOnReadPositionRepository` in the new test file is
the honest double — it hands back a new object per read, like `db_to_position()`.

**Fix:** step 5 overlays the repriced objects onto its own read. One fetch, one save.

## D15 — and then the tick pipeline could undo a close

Found by the *same* cloud proof, on the second of two closes 0.4 s apart:

```
phase 1  close 0.01 of 0.02  ->  OUT deal volume 0.01000000   correct
phase 2  close the remainder ->  OUT deal volume 0.02000000   the ORIGINAL size
```

`ClosePositionHandler` sets `close_volume = position.volume.value`, so that deal can
only be 0.02 if the row read 0.02 *after* phase 1 had written 0.01. The tick pipeline
wrote it back: D13 made it persist the positions it had repriced, and it persisted
them with `save()` — a **full-row merge** of objects fetched before the close landed.

A tick arriving between a partial close and its persist restored the old volume, and
the next close dealt a size the client did not have. The balance stayed honest (the
PnL came from the deal), but the position row lied, and a client could have been
filled twice on the same lots.

This is **D8b again, on the other table.** D8b gave accounts a column-scoped
`update_valuation()` for precisely this reason; positions never got the equivalent.

**Fix:** `SqlPositionRepository.update_valuation()`, and it goes one better than a
narrower write:

```sql
UPDATE positions
   SET price_current = :price,
       profit = CASE WHEN :side = 'BUY' THEN (:price - price_open)
                     ELSE (price_open - :price) END
              * volume * contract_size,
       time_update = :when
 WHERE position_id = :id AND time_done IS NULL
RETURNING volume, profit, price_current
```

* profit is computed **in the statement** from the volume the row holds at write
  time, so a concurrent partial close changes the result instead of being
  overwritten by it;
* `time_done IS NULL` means a tick can never reprice or resurrect a closed position;
* `RETURNING` hands the pipeline what the database now says, so its in-memory view
  converges on the row rather than competing with it.

The full-row `save()` fallback stays for repositories without the scoped write, and
now logs a WARNING the first time it runs — being silently on the racy path is how
D8b survived.

## D14 — a partial close reported the remainder's floating PnL and no deal

```
response:  realized_pnl -1.01920000     deal_id ""
OUT deal:  profit        +0.50000000    deal_id 29681303-d6e1-4b02-8742-9eb1e412e666
```

The route described the close by reading the **Position**. D12 made that work for a
full close, by stamping the realised result onto the closed position (which is what
MT5 reports). But a partial close leaves the position open and floating, so:

* `position.profit` was the *unrealised* PnL of the remainder — a client that closed
  half of a losing position was handed the loss it had **not** realised, while its
  balance moved by the leg's own +0.50;
* `position.deal_close` is only set by a full close, so every partial close looked
  like it had booked nothing at all.

The same stamp cannot simply be applied to an open position: writing a realised
number into a floating field is the same lie inverted.

**Fix:** `ClosePositionCommand` grows an optional `result` sink that the handler
fills from the deal it just booked (`deal_id`, `price`, `realized_pnl`,
`volume_closed`). The route reads the sink and keeps the position-derived reads as
fallbacks. The handler's contract stays "return the Position", so the SL/TP worker,
the liquidation worker and the manager route are untouched.

---

## The cloud proof

`scripts/d12_proof_cloud_close.sh` — 7 shell gates + 41 driver checks:

| Step | What it proves |
|---|---|
| 1 | the MT5 terminal behind the tunnel is `connected` |
| 2 | the API boots on Neon + Upstash with the live price source |
| 3 | `/health` measures real database and bus latency |
| 4 | **WS ground-truth probe:** connects to the tunnel itself, counts frames and reports the newest quote's age — the difference between "our engine drops ticks" and "there is nothing live to drop" |
| 5 | open at a live price → partial close at an explicit price → market close, then read Neon directly |

Final run (Saturday, BTCUSD, account 886098):

```
WS probe: 188 BTCUSD frames in 10s, newest quote stamped 12:31:09 UTC (3s old)
BUY 0.02 filled at 77334.23      margin_used 154.66846000
tick pipeline wrote the reprice: price_current=77284.07 profit=-1.00320000   (D13)
phase 1  close 0.01 @ 77384.23 explicit -> realized_pnl 0.50000000, deal 86555a10…
         balance 100000.00 -> 100000.50, margin still held for the remainder
phase 2  close 0.01 @ 77284.07 at market -> realized_pnl -0.50160000, deal feb4d093…
         volume 0.01000000, not 0.02000000                                  (D15)
Neon: IN, OUT, OUT · reason CLIENT · comments carried · deal_close = last OUT deal
      position volume 0 · profit -0.5016 · price_current 77284.07
      account margin_used 0 · equity == balance · margin_level 999999
=== 41/41 checks passed, driver exit 0 ===
```

Two proof-hygiene lessons, both now encoded in the scripts:

1. **`grep -ci tick` on the server log is not evidence of anything.** A healthy tick
   logs nothing at INFO, and the startup banner contains the word several times — the
   first version of gate 4 declared "tick activity" on a feed that had delivered
   nothing. The gate now probes the socket itself.
2. **"The price moved" is not a check you can make on a quiet Saturday.** The
   live-price assertion now asks whether the close dealt at the repriced
   `price_current` rather than falling back to `price_open`, and says so plainly when
   the market simply did not move.

Also observed, not defects but worth knowing: the WS feed drops every ~60 s with
`keepalive ping timeout` (the trade-server does not answer pings) and reconnects
after the 5 s backoff; and the `bars` table has **0 rows** on a database that has
taken 30+ fills, so nothing persists bar history.

## Files

| File | What |
|---|---|
| `application/services/tick_margin_pipeline.py` | D13 overlay + D15 atomic write, loud legacy fallback |
| `infrastructure/persistence/repositories/position_repository.py` | D15 `update_valuation()` |
| `application/commands/close_position.py` | D14 result sink |
| `api/routers/trade.py` | D14 reads the sink |
| `scripts/patch_d13_tick_pipeline_persists_pnl.py` | idempotent |
| `scripts/patch_d14_close_result_sink.py` | idempotent |
| `scripts/patch_d15_position_valuation_write.py` | idempotent; all three reproduce the tree byte-exactly from HEAD |
| `tests/integration/test_d13_tick_pipeline_persists_pnl.py` | 7 tests, copy-on-read double, incl. the two race tests |
| `tests/integration/test_d11_client_trade_routes.py` | 13 tests (+ the D14 partial-close leg) |
| `scripts/d12_proof_cloud_close.sh` · `scripts/d12_cloud_close_driver.py` | the cloud proof |
| `scripts/probe_position_repricing.py` | the diagnostic that found D13 |

**Test count:** 588 → **596**. `make proofs` **13/0/1** (the one skip is
`m4_proof_order_executes`, weekend session).

## What this changes about the remaining queue

* **Stop-out is now actually reachable from ticks.** The liquidation worker has real
  equity to act on for the first time. It has no live-fire proof — that is the
  obvious next gate (drive an account below its stop-out level with live ticks and
  watch it liquidate).
* **A-Book position close** is still open, and now more visible: a client close on an
  A-Book position still does not call `TradeServerLiquidityGateway.close_position()`.
* The valuation sweep's `last_valuation_at` was NULL throughout the run, and it
  logged *"24 position(s) could not be revalued because no price is known for their
  symbol"* — those are EURUSD/XAUUSD positions from earlier proofs while the feed
  was subscribed to BTCUSD only. Expected, but it means 24 rows in Neon are valued
  from stale numbers.