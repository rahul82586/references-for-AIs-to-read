# M10 — Real adapters: live market data over WebSocket, A-Book hedging over FIX

**Question this milestone answers:** *can the platform take its prices from a
real market-data upstream and hedge client flow at a real liquidity provider —
or is it still wired to the mock and the stub?*

Before M10 both ends of the platform were placeholders that announced
themselves honestly but went nowhere:

1. **Prices came from `MockTickFeed` or from nothing.** `MARKET_DATA_SOURCE`
   accepted exactly one value, `mock`. `LPTickFeed` was a stub whose
   `stream_ticks()` raised `NotImplementedError`.
2. **A-Book flow hit `StubLiquidityGateway`.** In strict mode (the production
   default) it rejected every order rather than fake a hedge — the right
   behaviour for a platform with no LP adapter, and the reason an A-Book
   destination had never actually sent anything anywhere.

Both ports already existed (`ITickFeed`, `ILiquidityGateway`). M10 implements
them, so nothing above the adapters changed.

## What changed

### 1. `TradeServerTickFeed` (`infrastructure/feeds/trade_server_feed.py`)

An `ITickFeed` adapter for the trade-server prototype in `refs/trade-server`: a
FastAPI box with a real MetaTrader5 terminal attached, broadcasting over
WebSocket. The adapter speaks that box's own protocol exactly as
`ws/stream.py` defines it, so the two connect without translation on either
side:

| direction | frame |
|---|---|
| client → server | JSON text: `{"action": "sub", "symbol": "EURUSD"}` (ticks), `"sub_book"` (DOM) |
| server → client | msgpack binary: `{"s","p","b","a","q","ts"}` ticks, `{"type":"book","s","bids","asks"}` DOM |

Behaviour worth naming:

* **Decimal discipline.** Wire floats convert via `Decimal(str(value))` only, so
  `1.23456` reaches the engine as exactly that. No float ever touches a price.
* **One-sided ticks are normalised, crossed ticks are dropped.** A tick with
  `bid=0, ask=1.10010` (market just opened) becomes bid=ask; `ask < bid` is
  logged and dropped rather than passed to the pricing funnel.
* **Bad frames are skipped, not fatal.** An undecodable msgpack frame or a
  text heartbeat must not kill a price stream.
* **Clean EOF raises.** This is the deliberate one. `TickIngestor` reconnects on
  exception and loops immediately on a normal generator exit — so a socket that
  closes cleanly would spin the ingestor in a hot reconnect loop against a
  server that just dropped us. The adapter raises `ConnectionError` at EOF so
  the ingestor takes its 5s backoff. Proof A6 drops the socket from the server
  side and shows the reconnect land.
* **Book streams get their own socket**, because trade-server tracks tick and
  book subscriptions per connection. Levels are sorted best-first and
  re-decimaled, matching the `OrderBook` contract.

Wired in `api/main.py` as `MARKET_DATA_SOURCE=trade_server` (alias `ws`), with
`TRADE_SERVER_WS_URL` **required** — booting that source without a URL is a
startup failure naming the missing variable, not a silent fall back to no
prices. `TRADE_SERVER_WS_SYMBOLS` picks the symbols; unset subscribes the
seeded list capped by `TRADE_SERVER_WS_MAX_SYMBOLS` (50), because a terminal
chokes when asked to select all 362 at once.

### 2. FIX 4.4 layer (`infrastructure/fix/`)

Dependency-free, in three pieces:

* **`messages.py`** — `FixMessage` over an *ordered* field list, so repeating
  groups survive parsing (a dict would collapse the two `MD_ENTRY_TYPE`
  entries of a quote snapshot). Envelope computed on encode, verified on parse
  (BodyLength and CheckSum both checked, both reject). Builders for
  Logon / Heartbeat / Logout / NewOrderSingle / OrderCancelRequest /
  MarketDataRequest; parsers for ExecutionReport and
  MarketDataSnapshotFullRefresh. `Decimal` values are formatted with
  `format(v, "f")`, so a volume of `1E+2` goes on the wire as `100` and never
  in scientific notation.
* **`session.py`** — `IFixSession`, the narrow transport port: connect / send /
  recv / close. Sequencing, logon and heartbeat framing are the transport's
  job, which is exactly what quickfixn already does correctly, so the gateway
  never re-implements it. `QuickFixSession` wraps a `ThreadedSocketInitiator`
  and marshals engine-thread callbacks onto the asyncio loop.
* **`simulated_session.py`** — `SimulatedFixSession`, an in-process LP that
  parses what the gateway sends and answers like a counterparty: market orders
  fill at its ask (client buys) or bid (client sells); a limit fills only when
  it crosses, otherwise it rests; cancels confirm; quote requests return a
  snapshot. It moves no money and its docstring says so.

### 3. `FixLiquidityGateway` (`infrastructure/gateways/fix_gateway.py`)

Implements `ILiquidityGateway` — the same three methods the stub had, so
`ExecutionOrchestrator._execute_a_book` is unchanged and the gateway drops in
under the same DI key. Selected by `BROKER_LP_GATEWAY=fix`.

* **Correlation by ClOrdID.** Outbound orders are matched to inbound
  ExecutionReports through per-request futures.
* **Silence is failure.** No report inside `FIX_ORDER_TIMEOUT_S` raises
  `FixTimeout` whose message says the hedge state is UNKNOWN and must be
  reconciled before a retry. A missing report is never interpreted as a fill.
* **Rejection is rejection.** OrdStatus 4/6/8 raises `FixReject` carrying the
  report and the LP's `Text(58)`, so the orchestrator's A-Book error path
  rejects the client order instead of believing it was hedged.
* **An ack is not an outcome.** A real LP answers a market order with
  `New(39=0)` and then, milliseconds later, `Filled(39=2)`. Resolving on the
  first report would have returned ACK on an order that was actually filled —
  which is what the first run of this gateway did. Non-final reports now start
  a short grace (`ack_grace_s`, 250ms); if no outcome follows, the ack is the
  honest answer and the order is resting at the LP.
* **Session drop fails every pending request** rather than leaving callers
  waiting on futures nobody will resolve, and the next `send_order` re-runs
  `start()`.

Order mapping covers all eight MT5 order types: BUY/SELL → market;
BUY_LIMIT/SELL_LIMIT → limit at `Price(44)`; BUY_STOP/SELL_STOP → stop at
`StopPx(99)`; STOP_LIMIT → OrdType 4 with both. A GTD expiration maps to
`TimeInForce=6` + `ExpireTime(126)`.

**Skeleton scope, stated rather than hidden:** no drop-copy (35=Z)
reconciliation, no allocation blocks, no bracket SL/TP over FIX (4.4 has no
MT5-style paired brackets — the server-side `SlTpWorker` from M9 owns those),
and no session-level resequencing.

## The defect the cloud gate caught

`filled_volume` came back `0E-8` on an order that was genuinely, fully filled —
in the cloud, over real PostgreSQL, with a real WS price source. It was not an
M10 defect and not a race.

`Order.__post_init__` contained a convenience: *initialize `volume_current` to
`volume_initial` for new orders*, implemented as "if `volume_current == 0`, set
it to `volume_initial`". That ran on **every** construction — including
`db_to_order()`, which rebuilds the entity on every SQL read. A fully filled
order legitimately carries `volume_current == 0`, so **every read of a filled
order from PostgreSQL resurrected the initial volume.** The row in the database
was correct (`0E-8`); the entity built from it was not. The HTTP layer then
computed `filled_volume = volume_initial - volume_current = 0` and reported
that an order filled at 1.23460 had filled none of its volume.

Why 422 tests missed it: the harness repositories are in-memory and hand back
the same object they were given. Nothing in the unit or integration suite ever
round-tripped an order through a mapper, and the mock-price cloud runs before
M10 asserted `state` and the fill price but not `filled_volume`. The defect was
invisible exactly where it was harmless and visible exactly where it was not.

Fixed at the entity, not at the mapper: the default now applies only to
`STARTED` orders, which have not been priced, approved or filled. Past entry
into execution, zero is a real value. `tests/unit/test_m10_order_volume_roundtrip.py`
pins `domain → row → domain` for filled, partially-filled and placed orders.

A second, smaller landmine fell out of the same investigation:
`Order.price_order` defaulted to `field(default_factory=lambda: Price(Decimal('0')))`
— and `Price.__post_init__` rejects anything non-positive. Any `Order(...)`
built without an explicit `price_order` therefore raised `ValueError`, which is
why `create_order.py` passes `None` and carries a comment about it. The default
is now `None`, matching what every caller already assumed.

I also left the create handler's post-publish re-read retrying briefly until the
row is self-consistent (`state FILLED` implies `volume_current == 0`). It was
written for the race I first suspected; the real cause was the entity, but on
an async bus the re-read genuinely can land mid-write, and a bounded retry is
still the right defence. It is bounded at 1.5s and logs loudly if it expires.

## Gates

| gate | result |
|---|---|
| unit + integration suite | **422 passed** (was 384) |
| `ruff --select E9,F63,F7,F82` | clean |
| `scripts/m10_proof_adapters.py` | **19/19** |
| `scripts/m10_proof_cloud_ws.sh` (Neon + Upstash + live WS) | **14/14** |
| `scripts/m5_proof_cloud.sh` (regression) | **33/33** |
| `scripts/m8_proof_routing.py` | 18/18 |
| `scripts/m9_proof_sltp_expiration.py` | 14/14 |

New tests: `tests/unit/test_m10_fix_messages.py` (10),
`tests/unit/test_m10_trade_server_feed.py` (10),
`tests/unit/test_m10_fix_gateway.py` (10),
`tests/unit/test_m10_order_volume_roundtrip.py` (5),
`tests/integration/test_m10_adapters_live.py` (2),
`tests/integration/test_m10_order_refresh_race.py` (1).

The two integration tests are the ones that matter. `test_m10_adapters_live.py`
starts a **real uvicorn WebSocket server** speaking the trade-server protocol,
streams msgpack ticks into it, and asserts a client order fills at the ask that
arrived over that socket — no fake connection object anywhere in the path. The
same file drives an A-Book order through the real `trading_setup` wiring with
`BROKER_LP_GATEWAY=fix` and asserts the simulated LP received a NewOrderSingle
whose ClOrdID is the order's ticket.

The cloud gate goes further: it boots the API against Neon PostgreSQL and
Upstash Redis with `MARKET_DATA_SOURCE=trade_server`, confirms the log
announces the live source and **not** the mock, confirms the upstream saw the
EURUSD subscription, and then trades over HTTP — asserting the persisted fill
price equals the price the simulator pushed over the WebSocket, to the digit.
It also proves the fail-hard path first: `MARKET_DATA_SOURCE=trade_server` with
no `TRADE_SERVER_WS_URL` refuses to boot and names the missing variable.

## Known debt

* **`QuickFixSession` has never talked to a real LP.** quickfixn needs a native
  build and there is no FIX endpoint in the test environment, so that class is
  written against the documented API and unexercised. Everything below it —
  message encoding, correlation, timeout, rejection, ack grace — is tested
  against `SimulatedFixSession`. The untested surface is the quickfix callback
  marshalling itself.
* **The A-Book leg still does not book a client-side fill.** The gateway now
  returns a real FILLED execution report, and `_execute_a_book` still only sets
  the order to PLACED and publishes `OrderRouted`. No deal, no position, no
  margin release for A-Book flow. That is the orchestrator's next job, not the
  adapter's — but an A-Book destination is not yet a complete trade.
* **No FIX drop-copy or end-of-day reconciliation**, so a `FixTimeout` leaves
  the hedge state unknown with nothing to resolve it against.
* **The WS feed carries trade-server's protocol only.** A real LP feed (Centroid
  Bridge, LMAX) needs its own adapter behind the same `ITickFeed` port;
  `LPTickFeed` is still the `NotImplementedError` stub.
* **`MARKET_DATA_SOURCE=trade_server` subscribes at startup only.** Symbols
  seeded after boot are not subscribed until a restart.
* **Book (`stream_book`) has no production consumer.** The adapter implements it
  and the tests cover it, but nothing in the tick pipeline subscribes to DOM.

## Files

New: `infrastructure/feeds/trade_server_feed.py`,
`infrastructure/fix/{__init__,messages,session,simulated_session}.py`,
`infrastructure/gateways/fix_gateway.py`,
`scripts/{m10_proof_adapters.py,m10_proof_cloud_ws.sh,m10_ws_simulator.py}`,
six test modules, three one-shot patch scripts kept for audit
(`m10_patch_wiring.py`, `m10_patch_order_refresh.py`,
`m10_patch_order_postinit.py`).

Changed: `api/main.py` (live price source, gateway shutdown),
`application/di/trading_setup.py` (`BROKER_LP_GATEWAY`),
`application/commands/create_order.py` (bounded re-read),
`core/domains/oms/entities/order.py` (the two defect fixes),
`pyproject.toml` (`msgpack`, optional `fix` extra), `.env.example`.