# M4 — Does an order execute?

**Status: COMPLETE.** 274 tests pass (was 210), 6 of 6 proofs green, 187/187 modules import.

The milestone question was "can I place an order and end up holding a position". The answer
before M4 was **no** — and not because a feature was missing. The execution path existed on
paper, from `CreateOrderHandler` through `PreTradeRiskService`, `SmartOrderRouter`,
`ExecutionOrchestrator`, `RecordDealHandler` and `LiquidationWorker`, and **not one line of
it had ever run**. Every step raised, called a method that did not exist, or read a field
that did not exist. The API papered over all of it by returning a mock order with
`state="FILLED"`.

What follows is what was broken, what was built, what is proven, and what is still debt.

---

## 1. The headline finding

`POST /api/v1/trade/orders` returned **HTTP 200 and a filled ticket for an order that was
never risk-checked, priced, persisted or hedged.**

```python
class FallbackCreateOrderHandler:            # api/di_providers.py, before M4
    async def handle(self, command):
        class MockOrder:
            ticket_id = 1001
            state = 'FILLED'
            price = Decimal('1.0850')
        return MockOrder(command)
```

`get_create_order_handler()` returned it whenever the container had no real handler — which
was always, because nothing ever built one. A client placing an order was told it held a
position that did not exist, and no log line anywhere said so. Both fallbacks (order and
close-position) are gone; the providers now raise and name what is missing.

---

## 2. What was built

Five new modules, all in the layer the architecture already reserved for them:

| Module | Port | What it does |
|---|---|---|
| `infrastructure/engines/book_matching_engine.py` | `IMatchingEngine` | Prices and internalises B-Book fills; rests pending orders and activates them on later ticks. **Was an empty directory.** |
| `infrastructure/gateways/stub_liquidity_gateway.py` | `ILiquidityGateway` | A-Book stub that **refuses** to fake a hedge in strict mode. **Was an empty directory.** |
| `infrastructure/messaging/inprocess_event_bus.py` | `IEventBus` | Single-node bus with the same dispatch semantics as `RedisEventBus`. Only Redis existed, so nothing could run without a Redis server. |
| `core/domains/market_data/feed_access.py` | — | One place that knows how to read a price from either feed shape, and how to rebuild a `Tick` from an event payload. |
| `application/di/trading_setup.py` | — | The composition root: `build_trading_stack()` assembles risk → routing → matching → execution → liquidation and subscribes it to the bus. |

Plus `alembic/versions/002_position_price_current_nullable.py` and four test files.

The matching engine is deliberately **not** a price-time-priority CLOB. It internalises
B-Book flow and rests pending orders; client-vs-client netting is the ECN the user deferred.
Its module docstring says so rather than implying otherwise.

---

## 3. Defects fixed

Thirty-five, grouped by what they broke. Every one is covered by a test or by the proof.

### 3.1 The path could not be traversed at all (each was a hard exception)

| # | Where | Defect |
|---|---|---|
| 1 | `execution/router.py:74` | Read `account.login_id`; `Account` has `login`. `AttributeError` on **every** `route()` call. |
| 2 | `risk_service.validate_order` | Called `symbol.is_within_session()`; `Symbol` has `is_trade_session_active()`. `AttributeError` at check 4 of 6. |
| 3 | `create_order.py` | Built `Price(Decimal('0'))` for market orders; `Price` rejects non-positive. **Every market order** died constructing the entity. |
| 4 | `create_order.py` | Read `symbol.digits_currency`. That is an MT5 *group* property (`CurrencyDigits`); `Symbol` has no such field. |
| 5 | 9 call sites | Read `order.volume`; `Order` declares `volume_initial`/`volume_current`. Included `_check_volume_limits` and `basic_margin` — no order could be risk-checked. Fixed by adding `Order.volume` as the `VolumeCurrent` reading, which is also the *correct* semantic (MT5 margins the remaining volume). |
| 6 | `execution_orchestrator` | Called `matching_engine.execute_internal()`; the port did not declare it and no engine existed. |
| 7 | `execution_orchestrator` | Read `account.group.commission.value`; `Group` has `commissions` (a list of rules) and `calculate_commission()`. |
| 8 | `record_deal`, `liquidation_worker` | `await feed.get_latest_tick(...)` against `MarketDataEngine`, whose getter is **synchronous**. `TypeError: object Tick can't be used in 'await' expression` — on the write path of every fill, and on the stop-out path. |
| 9 | `symbol.py` session checks | Called `.get(day)` on `trade_sessions`. Every real producer (YAML loader, MT5 importer, DB mapper) builds a **flat list**; only the dataclass default is a dict. `AttributeError` for any configured symbol. |
| 10 | `symbol.py` session checks | Used Python's Monday-first `weekday()` as MT5's **Sunday-first** day index. Looked up the wrong day for every symbol: Monday refused, Saturday allowed. |
| 11 | `symbol.validate_volume`, `Volume.is_valid_step` | `volume % volume_step` with `volume_step = 0` raised `decimal.InvalidOperation` instead of returning a verdict. Zero is legitimate — real MT5 exports carry it. |
| 12 | `SqlSymbolRepository` | No `find_by_name`, and the port never declared it — yet five callers await exactly that. |

### 3.2 Silent wrong numbers (worse than the crashes)

| # | Where | Defect |
|---|---|---|
| 13 | `SqlPositionRepository` | Exposed only `get_by_account`. `_recalculate_account_margin` probed `get_positions_by_account` then `find_by_account` and fell back to `[]`. Against real repositories it recomputed margin over **zero positions** and wrote `margin_used = 0, margin_free = equity` after every fill. The account looked flat and unleveraged the moment it opened a trade, and stop-out could never fire. Invisible because the probe's fallback was silent and every test double defined the probed name. |
| 14 | `record_deal` position writes | Assigned `Position.action` a **`DealType`** (hedging) or an **`OrderType`** (netting) instead of `PositionAction`. All three spell "BUY"/"SELL", so nothing raised — the values just were not equal. `Position.reverse()` computed the *same* side; netting never netted; `LiquidationWorker`'s `p.action == PositionAction.BUY` was False for every position so it valued longs at the **ask**; `close_position` chose the wrong closing side. |
| 15 | `record_deal` repository probe | `'session' in method.__code__.co_varnames` matches a method's **local variables**, not just parameters. `SqlOrderRepository.find_by_id(self, order_id)` binds `async with ... as session` in its body, so the probe passed `session=None` to a method that could not accept it. Replaced with `inspect.signature`. |
| 16 | `liquidation_worker` | Wrote the closing deal straight to the repository and never booked the realised PnL to balance. The position — and the loss with it — disappeared, then step 6 recomputed equity over the *remaining* positions. **The client's realised loss was deleted** and the account could keep trading with money it had already lost. |
| 17 | `liquidation_worker` step 6 | Recomputed `margin_used` with `Position.calculate_margin_required()` — a sixth independent margin formula using `price_open`, no currency conversion, no maintenance rates. Those are the exact numbers the stop-out recovery check compares against. Now delegates to `RiskEngine.calculate_margin_level`. |
| 18 | `api/routers/trade.py` | Read `order.price` and `order.filled_volume`, neither of which exists. Every response reported `price: null, filled_volume: 0` — including for genuinely filled orders. |
| 19 | `db_to_account` | Returned `login` as the raw `String(32)` primary key, while `Order`/`Deal`/`Position.account_login` and their columns are `BigInteger`. `get_by_account(account.login)` compared TEXT to BIGINT and came back empty — defect 13 again, by a different route. |
| 20 | `mappers.position_to_db` / `db_to_position` | Dereferenced `price_current`, which the domain declares `Optional` and documents as `None` until the first tick. Crashed persisting the first position any account ever opened. |
| 21 | `positions.price_current` | Column was `NOT NULL`. Model + migration 002 make it nullable; the domain was right. |

### 3.3 Wiring — components that never met

| # | Where | Defect |
|---|---|---|
| 22 | `create_order.py` | **Never published `OrderApproved`.** The orchestrator subscribes to exactly that event, so a created order sat in `PLACED` forever. |
| 23 | `risk_service._publish_approval` | Published the id as `ticket_id`; the orchestrator read `order_id`, logged "missing order_id" and returned. |
| 24 | `risk_service.validate_order` | Published the approval **inside the per-account lock** and before the order was persisted. The bus delivers inline, so the orchestrator took the same lock (deadlock) and then could not find the order. Added `publish_events=False`; the handler validates under the lock, persists, then publishes. |
| 25 | `market_data_setup` | Bridged ticks with `event.payload.get("tick")`. `MarketDataEngine` publishes flat string fields (`symbol`/`bid`/`ask`) so the event survives JSON onto Redis — there is no `"tick"` key. **The margin-call / stop-out state machine never ran**, silently, because an empty payload and an account with no positions look identical from the inside. |
| 26 | `domain_events.py` | `MarginCallEntered`, `MarginCallExited`, `StopOutEntered`, `StopOutExited`, `HolidayCreated` never overrode `event_type` and inherited the default **`ORDER_CREATED`**. In-process subscribers registered by class still heard them; Redis routes on the channel string, so across processes a stop-out notified every `OrderCreated` listener and reached no `LiquidationWorker`. |
| 27 | `execution/router.py` | The NOP thresholds (70% warn / 85% auto-hedge / 95% block) lived **inside the rule-matching loop**, so they only ran for an order that matched a rule. A server with no rules — the freshly seeded default — fell through to `default_destination` unchecked. The broker's exposure limit did not apply to exactly the configuration someone stands up first. |
| 28 | `execution/router.py` | `route()` raised `RuntimeError` when the rule table was empty rather than falling back to the configured default. "Install, seed, start, trade" was impossible without hand-writing a rule. |
| 29 | `api/main.py` | Startup wired a `ConfigCache` and a WebSocket bridge, then stopped. No orchestrator, router, engine, gateway or worker was ever constructed outside a test. |
| 30 | `api/main.py` | `app = create_app()` at module scope passed **no container**, so startup raised `KeyError('IGroupRepository')`. `cli start` runs `uvicorn api.main:app` — the one command meant to start the platform could not. Added `default_providers()`. |
| 31 | `di_setup` / `market_data_setup` | `build_tick_margin_pipeline` resolves `RiskEngine` **by class**, which `_ContainerView` turns into the key `"RiskEngine"`. Nothing registered it → `KeyError` at startup, before any tick could be processed. |
| 32 | `trading_setup` (new) | `RiskEngine` reads symbols **synchronously** and refuses a coroutine. Every repository is async, including `SqlSymbolRepository.get_symbol`, so `calculate_margin_level` raised — and `_check_margin_requirement` treats a failed snapshot as a **rejection**. Any account already holding a position could never open another. Now handed the `ConfigCache`. |
| 33 | `seeder.py` | `ensure_coverage_account` creates a trading *Account* in `coverage\house`. The router and orchestrator read a *CoverageAccount* **risk entity** from a different table by id `DEFAULT_COVERAGE`, which nothing ever created. B-Book exposure was untracked and the NOP thresholds could never fire. |
| 34 | `RedisEventBus` | No `unsubscribe`, so `LiquidationWorker.stop()` raised `AttributeError` on shutdown. A worker that cannot be stopped cannot be restarted. |
| 35 | `OrderRequest.order_type` | Typed as `str`, passed straight to `CreateOrderCommand`. The `Order` carried `"BUY"`, so `is_market()` was False and a market order was priced as a pending one with no price. Now typed `OrderType` (invalid side → 422 at the edge) and the command coerces defensively. |

Also removed: the CLI's private `InProcessEventBus`, which dispatched on `type(event)` only
and could not deliver to a handler registered under `EventType.ORDER_APPROVED.value`.

---

## 4. What is proven

**`scripts/m4_proof_order_executes.py`** — runs against the **real SQL repositories**
(SQLite standing in for PostgreSQL, same mappers, same `Base.metadata`, same seeded
`config/`). This is what caught defects 12, 13, 15, 19, 20, 21 and 9–11: the in-memory
doubles in the unit tests defined the method names the production code probes for, and the
production repositories did not.

```
[1]  seed the configuration plane          7 groups, 5 symbols, DEFAULT_COVERAGE created
[2]  market hours                          EURUSD open; demo\Standard call 10% stop 1%
[3]  open an account                       reads back by int login, group attached
[4]  assemble the trading plane            exactly 1 orchestrator on ORDER_APPROVED
[5]  buy 0.10 EURUSD                       FILLED at the ASK 1.10010, not the bid
[6]  rows are real                         order FILLED, 1 deal, 1 position (PositionAction.BUY)
[7]  margin to the cent                    110.01 USD  (100 EUR × ask), equity 9,999.00
[8]  broker exposure                       coverage −0.10  (client long ⇒ broker short)
[9]  second order                          330.03 USD — recomputed over BOTH positions
[10] pending order                         rests, no deal, no exposure; activates on the
                                           tick and fills at the better ask 1.08910
[11] A-Book, no LP connected               REJECTED after genuinely attempting to send
[12] unmarginable order                    rejected, balance untouched, no position
[13] event chain                           created → approved → routed → deal, in order;
                                           no risk event on the order.created channel
=== M4 proof PASSED ===
```

Margin at step 7 is the M3 maths reached from the trading path: 0.10 × 100,000 / 100
= 100 EUR, converted EUR→USD at the **ask** because MT5 converts a buy deal at the ask,
× initial_buy rate 1.0 = **110.01**. Step 9 confirms the same engine aggregates.

**Test suite: 274 passed, 0 failed** (210 before M4).

| File | Tests | Covers |
|---|---|---|
| `tests/unit/infrastructure/test_book_matching_engine.py` | 27 | Buy at ask / sell at bid; limits fill at limit **or better**, never worse; stops fill at **market**, not the stop price; slippage refusal; resting and tick activation; cancel/replace loses queue position; sync and async feeds. |
| `tests/integration/test_order_execution_e2e.py` | 27 | Full B-Book lifecycle to the cent; cross-currency (USDJPY margin is 100 USD, not 15,000 or 0.67); hedging stacks margin; rejections leave nothing behind; pending rest→activate; A-Book strict/non-strict; routing by symbol and priority; NOP 85% auto-hedge and 95% block; post-fill failure must not un-fill; **stop-out closes the worst loss first and books the realised loss**; unwired DI refuses. |
| `tests/unit/api/test_trade_endpoint.py` | 9 | Real HTTP through FastAPI's own startup: 200 with a real ticket and the live ask; 400 with no price; 422 on an unknown side; 401 unauthenticated; pending reports `PLACED`; insufficient margin is a 400. |
| `tests/integration/trading_harness.py` | — | In-memory doubles mirroring the **real** repository signatures, and a `build()` that wires ConfigCache + trading stack + tick pipeline exactly as `api/main.py` does. |

The stop-out test is worked by hand, because the shape is counter-intuitive: closing a
position does **not** improve equity (the unrealised loss becomes realised and moves onto
the balance). What improves is the denominator. So recovery depends on how much margin is
released, and the scenario is built so releasing half of it is enough — 40.2% → margin
call → 19.2% → stop out → close the worse of two longs → 38.4%, recovered.

The five earlier proofs still pass unchanged: MT5 round-trip 362/362 symbols and 20/20
groups field-identical, three-currency survival, M2 seed/read-back/idempotence, unit-of-work
atomicity, and margin maths against MT5's published examples.

---

## 5. Known debt — found, not fixed

Stated plainly, because a report that lists only successes is not describing a real system.

**On the execution path:**

1. **No margin reservation.** Between risk approval and the deal being booked there is no
   reserved-margin hold on the account. With the in-process bus the orchestrator runs
   inline, so the fill is booked before `handle()` returns and the window is closed. Across
   a Redis bus it is open: two concurrent orders could both pass the same free-margin check.
   Closing it needs a `margin_reserved` column and a release on fill/reject. The existing
   per-account `asyncio.Lock` only serialises one process.
2. **Netting does not book realised PnL.** `_apply_deal_netting_mode` reduces or deletes a
   position without writing the realised result to the balance — the same class of defect as
   #16, on the netting branch. Hedging (the retail default, and what the tests exercise) is
   correct. Netting needs the same treatment before an institutional account uses it.
3. **`volume_min` and `volume_step` are lost on the database round trip.** A YAML-seeded
   EURUSD has `0.01` for both in `config/`, and reads back as `0`. `volume_max` survives.
   This is a config-plane defect (M1/M2 remit) in the codec's scaled `*Ext` handling, not an
   execution one — `validate_volume` now treats 0 as "unset" so it cannot crash on it, but
   the limits are not being enforced from the database. **This is the most consequential
   item on this list** and should be fixed before production seeding.
4. **Two margin monitors.** `TickMarginPipeline` (tick-driven, the one now wired) and
   `risk_worker.py` (which publishes `MARGIN_CALL_TRIGGERED`/`STOP_OUT_INITIATED` itself)
   both implement the state machine. Only the pipeline is subscribed. One should be deleted.
5. **Swap is not charged at fill.** Deliberate — `swap_worker` owns it and booking twice
   would be worse than booking late — but `swap_worker` is not wired into
   `build_trading_stack` yet, so nothing currently charges swap.
6. **`api/main.py` uses deprecated `on_event`.** FastAPI wants lifespan handlers. Works,
   warns, and will eventually break.

**Deferred by the user, and genuinely not built:**

7. The A-Book gateway is a **stub**. Strict mode rejects rather than faking a hedge; there
   is no Centroid Bridge or FIX adapter.
8. No ECN / CLOB — the matching engine internalises and rests, it does not match client
   against client.
9. No dealer-intervention UI behind `DealerQueueService`, no client terminal, no reporting,
   no cluster, no AI layer.

---

## 6. Where this leaves the four-stage plan

| Stage | Before M4 | Now |
|---|---|---|
| 1. MT5 install / import | done (M0–M1) | unchanged, 362/362 lossless |
| 2. Admin / manager setup | done (M2) | unchanged, plus `DEFAULT_COVERAGE` now seeded |
| 3. Brokerage configuration | done (M2–M3) | margin maths now reachable *from the trading path*, not only from tests |
| 4. Routing / A-B book / matching | **nothing ran** | B-Book executes end to end; routing rules, NOP thresholds and pending activation work; A-Book routes and honestly refuses |

`cli migrate && cli seed && cli start` now stands up a server that can take an order and
hold a position. That is the "set up and run" target.

**Next milestone (M5)** would be deployment: PostgreSQL + Redis under compose, the
reservation column from debt #1, the codec fix from debt #3, and a real LP adapter or an
explicit decision to run B-Book only.

---

## 7. Security — unchanged and still open

The public reference repository still contains a real MT5 server export with **15 plaintext
server passwords and a live JWT**. M4 did not touch it. Rotate those credentials, make the
repository private, and rewrite history; a force-push does not remove what is already cloned.

The seeder prints the first administrator's password once, to stdout, and stores only an
Argon2 hash — that part is correct and is worth keeping.
