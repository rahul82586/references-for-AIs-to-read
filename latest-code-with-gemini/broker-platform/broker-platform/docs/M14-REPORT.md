# M14 — D5 (Redis pub/sub) and D11 (client trade routes)

**Date:** 2026-09-12 · **Commits:** `db8e46d` (D11), `b53f94b` (D5) · **Tests:** 586 passed, 25 skipped · **Lint:** E9/F63/F7/F82 clean · **Proofs:** 12 passed / 0 failed / 2 weekend skips

Both items on the task list are closed, plus the orphaned hedge.

---

## The question that started this: "only IN deals were visible, no OUT deal"

**Answer: it was never fixed, and it could not have been — there was no endpoint to fix.**

The live Neon database reads:

```
deals by entry : IN 31          <- and nothing else
positions      : OPEN 31, CLOSED 0
deal_close set : 0
orders         : FILLED 31, REJECTED 4
```

`api/routers/trade.py` had three routes. One was real, two were theatre, and the one that mattered did not exist:

| Route | Reality before |
|---|---|
| `POST /api/v1/trade/orders` | ✅ real — this is the source of all 31 IN deals |
| `PUT /api/v1/trade/orders/{id}` | 🔴 returned `{"status":"modified"}`, touched nothing |
| `DELETE /api/v1/trade/orders/{id}` | 🔴 returned `{"status":"cancelled"}` for **any** id, touched nothing |
| **close a position** | 🔴 **no such route existed** |

So this was not a broken close. There was no client-facing close to break. The handler itself was fine — D10 had already fixed its margin release and its `price_current` dereference, and it was proven to emit IN+OUT with correct realised PnL. But only the **manager** endpoint could reach it. `ModifyOrderHandler` and `CancelOrderHandler` were also complete and also unreachable: neither was ever constructed, so nothing registered them.

This is the same class as D2 (`/account/info` serving a JWT snapshot because its handler was never registered) and the M4 `FallbackCreateOrderHandler` that answered every order with a mock FILLED ticket. **A 200 with a plausible body over absent behaviour is worse than a 501**, because the client believes the trade happened. A user who "cancelled" a stop order via `DELETE` was left unprotected, with nothing in any log to say so.

### D11 — what changed

Registered both missing handlers in the trading stack, and replaced all three routes with real ones:

```
POST   /api/v1/trade/positions/{position_id}/close    full or partial close
PUT    /api/v1/trade/orders/{ticket_id}               modify price / SL / TP
DELETE /api/v1/trade/orders/{ticket_id}               cancel a resting order
```

Every route follows the contract M5 established on `/account/positions`:

- **no handler registered → 503**, with a logged error. A misconfigured server must not look like a healthy one.
- **`ValueError` → 404** if it says "not found", else **400** with the reason.
- **anything else → 500** with the traceback logged.
- never a silent fallback, never a success body for work not done.

**Ownership is enforced on all three:** `account_login` comes from the authenticated token, never the request body, so one client cannot close or modify another's position by guessing an id.

Close is `POST`-with-body rather than `DELETE`, because a partial close carries a volume and DELETE-with-body is not reliably supported by clients or proxies. `DELETE` stays for cancelling a resting order, which is what it always meant.

Also fixed a duplicate-key bug found while verifying: `TradingStack.as_providers()` registered `modify_order_handler` and `cancel_order_handler` twice each.

### Two things worth recording about how this was tested

**The first version of the test proved nothing.** It registered handlers into the module-global DI container while the repositories lived in a separately-built harness — two worlds. Every request got a handler bound to an empty repository set, so each close returned `404 Position not found` for a position that demonstrably existed. The fix is to build the app with `create_app(harness.providers)` and `wire_trading=False`, so **FastAPI's own startup assembles the stack from the same container the routes read**. One world, or the test is theatre of its own.

**The 503 test needed `ASGITransport`, not `TestClient`.** Since D11, startup itself registers all three handlers, so entering the `TestClient` context wires the very plane the test asserts is missing. Transport-level requests skip the lifespan.

10 new integration tests over real HTTP against a whole in-memory broker: OUT deal appears, `deal_close`/`time_done` set, margin released and equity honest (D10 holds over HTTP), partial close leaves the remainder open, another client's position refused, unknown id 404, double-close produces exactly one OUT deal, cancel persists `CANCELLED`, modify persists the new stop, and all three 503 when unwired.

---

## D5 — Redis pub/sub

### The defect

`subscribe()` spawned a dedicated `_redis_subscribe(key, callback)` task per channel, each running its own `async for message in self._pubsub.listen()` over the **same shared pubsub connection**. redis-py allows exactly one reader per connection. Every loop after the first raised:

```
readuntil() called while another coroutine is already waiting for incoming data
```

…logged it once as an error, and died. Two distinct failures:

1. **Lost delivery.** Every channel but the first received nothing, ever. In production: `ConfigCache` never invalidates, `LiquidationWorker` never sees a stop-out, no WebSocket client receives an update — whichever subscribed second. Logged once at startup, then the system runs looking healthy.
2. **Cross-channel leakage.** The surviving loop read *every* message on the connection and passed it to its own callback regardless of which channel it arrived on. Reproduced live: `ch1: [{'x': 1}, {'x': 3}]` — ch1's handler was handed ch3's payload. A handler written for one event type receives another's data. **Worse than dropping it.**

### Measured, before and after

`scripts/d5_redis_live_proof.py` — two bus instances (= two processes), five real `DomainEvent`s published through `publish()` over five channels on live Upstash:

```
before:  RESULT: 0/5 channels delivered correctly
after:   RESULT: 5/5 channels delivered correctly   (payloads intact, no leakage)
```

**0/5, not the 2/3 the isolated probe showed** — and the reason matters. `publish()` dispatches locally first, and in the real server every event type has an in-process handler; the shared reader therefore never saw anything left to forward. Cross-process delivery was **entirely dead**, not partially broken. That is the only case `RedisEventBus` exists for, since `InProcessEventBus` covers a single process.

### The fix

**One reader task per connection**, not one per channel. The reader owns the socket, reads `get_message()`, looks up the arriving message's **own** channel, and dispatches to the callbacks registered for that channel. Subscribing to a new channel is then a `SUBSCRIBE` command plus a dict entry — it never touches the read loop, so the channel count stops mattering. Verified: 30 channels, still one reader task.

Also, while in here:

- **Event-type parity.** The reader handed handlers the raw JSON dict; `InProcessEventBus` hands them a `DomainEvent`. The same handler therefore received a different type depending on which bus the server was configured with, and every consumer needed an `isinstance` branch. Added `DomainEvent.from_dict()` and rehydrate on receipt. Unknown `event_type` values and unparseable timestamps are tolerated rather than raised — an event from a newer publisher must still be delivered; losing it because the envelope was unfamiliar is worse than a best-effort type.
- **Resilience.** The reader restarts with exponential backoff (0.25s → 10s cap) if the connection drops, re-subscribing every known channel. `disconnect()` cancels it *before* tearing down the connection, so shutdown does not surface as a transport error.
- **`unsubscribe()` now detaches the Redis-side registration too.** Its old docstring justified leaving it alone — "the Redis pubsub channel is shared and may still have other subscribers" — which is true of the *connection*, but it left the callback registered on the reader, so a stopped worker kept being called. The fix honours the caveat properly: `UNSUBSCRIBE` is issued only when the channel's **last** callback goes.
- One raising handler no longer stops the reader or the other handlers.

15 new tests against a fake pubsub (deterministic, no server needed). **14 of the 15 fail against the old code** — verified by stashing the fix.

---

## Orphaned hedge closed

The `refs/trade-server` ngrok tunnel turned out to be the **MT5 terminal bridge** (login 50080, server `86.104.251.194:443`), not the broker platform — it exposes `/api/v1/close-position` and writes to MT5, not to Neon. It was live:

```
before: 5281493 XAUUSD buy  0.01  comment=''            <- yours
        5292077 XAUUSD sell 0.01  comment=''            <- yours
        5292093 BTCUSD buy  0.01  comment='trade-server' <- OUR orphaned hedge
after:  5292093 closed at 77286.47 (deal 5292099)
        the two XAUUSD left untouched
```

That closes all 6 hedges from the task list. The `comment='trade-server'` marker is what distinguishes our hedges from your own trades — worth keeping as the convention.

---

## Files

| Path | What |
|---|---|
| `api/routers/trade.py` | D11: three real routes, schemas, ownership enforcement |
| `application/di/trading_setup.py` | D11: builds + registers modify/cancel handlers |
| `infrastructure/messaging/redis_event_bus.py` | D5: single reader, channel-keyed dispatch, reconnect |
| `core/events/domain_events.py` | D5: `DomainEvent.from_dict()` |
| `scripts/patch_d11_client_trade_routes.py` | D11 patch (idempotent, reproduces the tree exactly) |
| `scripts/patch_d5_redis_single_reader.py` | D5 patch (idempotent) |
| `scripts/d5_redis_probe.py` | isolated 3-channel diagnostic |
| `scripts/d5_redis_live_proof.py` | **live 2-process, 5-event proof — exit 0 = green** |
| `tests/integration/test_d11_client_trade_routes.py` | 10 tests over real HTTP |
| `tests/unit/infrastructure/test_d5_redis_pubsub.py` | 15 tests against a fake pubsub |

---

## Remaining

1. **D11 is not deployed.** The running server still advertises no close route — it needs a restart to pick this up. Then a real client close can be verified against Neon (expect an OUT deal and `deal_close` set).
2. **Reconciliation Engine** — runs/persists/ages/auto-clears, but needs FIX drop-copy (`35=Z`) and automatic resolution of `HEDGE_STATE_UNKNOWN`.
3. **Commission types / charge modes** — standard/agent/fee × instant/daily/monthly; only instant standard is exercised.
4. **Gateway config plane** (`mt5_gateways` table + `Translates`) — needed for symbol *renames*; the model and codec round-trip already exist from M13 part 1.
5. **`Use default spreads/volumes/limit` toggles** unverified.
6. **A-Book** still does not book a client-side *position* end-to-end in every path, and an A-Book close does not unwind the hedge.
7. **`git push`** — local `work/bp` is at `b53f94b`, several commits ahead of GitHub `a054423c`. `.git` does not persist in this workspace, so a patch backup is kept at `work/patches/`.
