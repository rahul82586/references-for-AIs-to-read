# BACKEND ENDPOINT REFERENCE — for the MT5 Admin frontend

**Generated:** 2026-09-12 · **From:** `qwe-agen-broker-platform-backend/work/bp` @ `38dc30b0`
**Method:** the OpenAPI spec was dumped from the *real* `api.main:app` object (not read off docs),
then cross-checked against router source for the things OpenAPI does not capture — auth, the
503/404/400/500 contract, and the untyped admin responses.

**Surface:** 33 HTTP routes + 3 WebSocket routes. Machine-readable copy: `openapi.json`.

---

## 0. Five things that will save you a day

1. **Your `api.ts` is missing the `/api/v1` prefix.** It calls `/admin/accounts`; the server
   serves `/api/v1/admin/accounts`. Every single call in `api.ts` currently 404s. One-line fix:
   `const BASE_URL = 'http://localhost:8000/api/v1';`
2. **There are two auth schemes, not one.** `/api/v1/admin/*` takes the header
   `X-Admin-API-Key`. Everything under `/api/v1/manager/*`, `/api/v1/trade/*` and
   `/api/v1/account/*` takes `Authorization: Bearer <jwt>` from `POST /api/v1/auth/login`.
   Your `api.ts` sends only the admin key, so the manager/trade/account planes are unreachable
   from it as written.
3. **Every decimal is a STRING.** `"1.15945"`, `"107.96100000"`, `"0E-8"`. This is deliberate —
   JSON floats lose trailing zeros (`1.10000` → `1.1`) and this is money. Parse with a decimal
   library, never `parseFloat`. `0E-8` is a legitimate zero.
4. **The error contract is meaningful — do not treat 503 as "not found".**
   `503` = the handler/repository is **not wired on this server** (a deployment fault, retrying
   will not help). `404` = the domain said "not found". `400` = the domain refused (e.g. stale
   quote, insufficient margin, market closed). `500` = unexpected, traceback is in the server log.
   `422` = Pydantic validation. `401` = bad/missing credentials. `403` = bad admin key.
   This is the project's design law: *refuse rather than fake*. A 200 always means it really happened.
5. **The admin plane is READ-ONLY today**, except `set-password`. 7 GETs + 1 POST. There is no
   admin create/update/delete for accounts, symbols, groups, routing or gateways. See §3.

**Margin levels and thresholds are PERCENT everywhere** (MT5 convention): `margin_call_level: "50.00"`,
`stop_out_level: "30.00"`, and `margin_level: "9261.677828…"` means 9261%. The sentinel for
"no margin used" is `999999`.

**CORS** is `allow_origins=["*"]`, `allow_methods=["*"]`, `allow_headers=["*"]`,
`allow_credentials=True`. Your `X-Admin-API-Key` header will preflight fine. (Note: `*` together
with `allow_credentials=True` is rejected by browsers *if* you send cookies — you don't, you send
a header, so this works. Don't switch the frontend to cookie auth without fixing it.)

---

## 1. Complete route table

| # | Method | Path | Auth | Purpose |
|---|---|---|---|---|
| 1 | GET | `/health` | none | liveness + real DB/Redis probes |
| 2 | POST | `/api/v1/auth/login` | none | issue a client/manager JWT |
| 3 | GET | `/api/v1/admin/status` | AdminKey | is the config plane seeded? |
| 4 | GET | `/api/v1/admin/groups` | AdminKey | list groups |
| 5 | GET | `/api/v1/admin/groups/{group_name}` | AdminKey | one group |
| 6 | GET | `/api/v1/admin/symbols` | AdminKey | list symbols |
| 7 | GET | `/api/v1/admin/symbols/{symbol_name}` | AdminKey | one symbol |
| 8 | GET | `/api/v1/admin/accounts` | AdminKey | list accounts |
| 9 | GET | `/api/v1/admin/managers` | AdminKey | list managers |
| 10 | POST | `/api/v1/admin/accounts/set-password` | AdminKey | set/rotate an account password |
| 11 | POST | `/api/v1/manager/Connect` | Bearer | open a manager session |
| 12 | POST | `/api/v1/manager/Disconnect` | Bearer | close it |
| 13 | GET | `/api/v1/manager/IsConnected` | Bearer | session state |
| 14 | GET | `/api/v1/manager/SessionInfo` | Bearer | session detail |
| 15 | GET | `/api/v1/manager/UserGet` | Bearer | **account info for ANY login** |
| 16 | GET | `/api/v1/manager/PositionGet` | Bearer | **open positions, filterable by login/symbol** |
| 17 | POST | `/api/v1/manager/OrderSend` | Bearer | place market/pending order |
| 18 | POST | `/api/v1/manager/OrderClose` | Bearer | close a position (full/partial) |
| 19 | POST | `/api/v1/manager/OrderDelete` | Bearer | cancel a pending order |
| 20 | POST | `/api/v1/manager/OrderModify` | Bearer | modify a pending order |
| 21 | POST | `/api/v1/manager/DealModify` | Bearer | modify SL/TP (Reversal+Correction) |
| 22 | GET | `/api/v1/manager/Ping` | none | keep-alive + server time |
| 23 | GET | `/api/v1/manager/StartTimeUtc` | none | server start + uptime |
| 24 | GET | `/api/v1/manager/MemoryUsage` | none | process RSS/VMS/CPU |
| 25 | GET | `/api/v1/manager/Version` | none | server/API version |
| 26 | POST | `/api/v1/trade/orders` | Bearer | client places an order |
| 27 | PUT | `/api/v1/trade/orders/{ticket_id}` | Bearer | client modifies price/SL/TP |
| 28 | DELETE | `/api/v1/trade/orders/{ticket_id}` | Bearer | client cancels a resting order |
| 29 | POST | `/api/v1/trade/positions/{position_id}/close` | Bearer | client closes own position |
| 30 | GET | `/api/v1/account/info` | Bearer | own balance/equity/margin |
| 31 | GET | `/api/v1/account/positions` | Bearer | own open positions |
| 32 | GET | `/api/v1/market-data/history/{symbol}/ticks` | none | historical ticks |
| 33 | GET | `/api/v1/market-data/history/{symbol}/bars` | none | historical OHLCV |
| WS1 | WS | `/ws/stream` | none | **DEAD — see §5** |
| WS2 | WS | `/ws/user` | token in first frame | **DEAD — see §5** |
| WS3 | WS | `/api/v1/manager/ws/subscriptions` | token in first `auth` frame | **the only live socket** |

Interactive docs when the server runs: `GET /docs` (Swagger), `GET /redoc`, `GET /openapi.json`.

---

## 2. Endpoint reference

### 2.1 Health

**`GET /health`** — no auth.
```json
{"status":"healthy","service":"broker-platform-api","version":"1.0.0",
 "checks":{"database":{"status":"ok","latency_ms":1.2},
           "event_bus":{"status":"in-process"}}}
```
`event_bus.status` is `"in-process"` or `"ok"` (Redis). **A degraded dependency returns HTTP 503**,
not 200 — so use this as your "is the backend usable" gate before rendering anything.

### 2.2 Auth

**`POST /api/v1/auth/login`** — no auth. Accepts **three** content types:

| Content-Type | Fields |
|---|---|
| `application/json` | `login_id` **or** `username`, `password` |
| `application/x-www-form-urlencoded` / `multipart/form-data` | `username` **or** `login_id`, `password` |
| (fallback) query string | `?username=…&password=…` |

Response `200`:
```json
{"access_token":"<jwt>","token_type":"bearer","expires_in":86400}
```
**Every** failure returns the identical `401 {"detail":"Invalid credentials"}` — unknown login,
wrong password, disabled account, and "no password provisioned" are deliberately
indistinguishable (no login enumeration). The real reason goes to the server log only.

Password is verified against an **Argon2** hash (M6). An account with no hash cannot log in;
provision one with endpoint #10. Use this token as `Authorization: Bearer <access_token>` for
planes 2.4–2.6 **and** for the WS `auth` frame.

### 2.3 Admin plane — `X-Admin-API-Key` header

Router-level dependency: if `ADMIN_API_KEY` is **unset on the server**, every admin request
returns `503 "ADMIN_API_KEY is not configured on this server"` (fail-closed, M5). A wrong or
missing header returns `403`. The header name is exactly `X-Admin-API-Key`.

> These endpoints return `List[Dict[str, Any]]` — **no `response_model`**, so OpenAPI carries no
> schema for them. The field tables below are taken from the serializers in
> `api/routers/admin/admin_router.py` and are authoritative.

**`GET /api/v1/admin/status`** — hit this after seeding.
```json
{"groups":7,"symbols":5,"accounts":45,
 "has_real_group":true,"has_demo_group":true,"has_coverage_group":true,
 "ready_to_trade":true}
```

**`GET /api/v1/admin/groups?account_type={REAL|DEMO|PRELIMINARY|COVERAGE|CONTEST}`** → array of:

| field | type | note |
|---|---|---|
| `id` | uuid str | |
| `name` | str | **MT5 path with a backslash**, e.g. `demo\Standard` |
| `account_type` | str | enum value |
| `currency`, `currency_digits`, `server_id` | str, int, int | |
| `leverage_default`, `leverage_max` | int | e.g. `100` |
| `margin_call_level` | **str** | **percent** |
| `stop_out_level` | **str** | **percent** |
| `stop_out_mode`, `free_margin_mode`, `margin_mode` | str | `margin_mode` = netting vs hedging |
| `trade_flags` | int | bitmask |
| `limit_orders`, `limit_positions`, `limit_symbols` | int | |
| `commissions`, `symbol_overrides` | int | **counts only, not the rules** — see gap G7 |
| `allowed_symbols` | str[] | |
| `trade_allowed`, `allow_hedging`, `is_active` | bool | |
| `routing_mode` | str | the group's *default*; routing rules override it |

**`GET /api/v1/admin/groups/{group_name}`** — same object, `404` if absent.
⚠️ A backslash cannot appear in a URL path segment, so **pass the forward-slash form**:
`GET /api/v1/admin/groups/real/real` resolves `real\real`. The route is declared
`{group_name:path}` and translates `/` → `\`, falling back to the literal. Your
`encodeURIComponent(name)` will produce `real%5Creal`, which also works via the fallback —
but `real/real` is the intended form.

**`GET /api/v1/admin/symbols`** → array of:

| field | type | note |
|---|---|---|
| `id`, `name`, `path`, `description` | str | `path` is the MT5 folder path the tree UI wants |
| `base_currency`, `quote_currency` | str | |
| `digits` | int | |
| `tick_size` | **str** | MT5's **Point** — the price-precision step; quantise with this |
| `mt5_tick_size` | **str** | MT5's separate `TickSize` field, frequently `0`. **They differ on every symbol in the reference export — do not conflate them.** |
| `tick_value`, `contract_size` | str | |
| `calc_mode`, `trade_mode`, `exec_mode` | str | enum values |
| `order_flags` | int | bitmask |
| `spread` | int | points; `0` = floating |
| `volume_min`, `volume_max`, `volume_step` | **str** | **already unscaled lots** — `"0.01"`, not `100` |
| `swap_mode`, `swap_long`, `swap_short`, `swap_3day` | str, str, str, int | `swap_3day` is a day index, **0 = Sunday** |
| `margin_initial_buy`, `margin_maintenance_buy` | str | the 8+8 margin-rate multipliers (sell side not exposed — gap G8) |
| `trade_sessions` | int | **count only** — gap G8 |
| `is_trade_allowed` | bool | |

⚠️ The DB *column* `symbols.volume_min` stores MT5's wire-scaled integer (`100` = 0.01 lots).
The repository unscales it, so **this endpoint returns `0.01`.** Do not "fix" the column.

**`GET /api/v1/admin/symbols/{symbol_name}`** — same object, `404` if absent.

**`GET /api/v1/admin/accounts?limit=1..1000`** (default 100) → array of:

| field | type |
|---|---|
| `login` | str |
| `group` | str (backslash form) or null |
| `account_type`, `currency` | str |
| `balance`, `credit`, `equity`, `margin_used`, `margin_free` | str |
| `margin_level` | str — **percent**, derived on read (never the stored column, D1) |
| `so_activation` | str — stop-out state machine position |
| `leverage` | int — effective (account, else group) |
| `is_enabled` | bool |

No pagination beyond `limit`, no offset, no filter by group/client. `password_hash` is never returned.

**`GET /api/v1/admin/managers`** → array of:
`login`(str), `name`, `mailbox`, `server_id`(int), `role`, `rights_granted`(int),
`rights_total`(int, 128), `group_scope`(str[]), `is_2fa_enabled`(bool),
`must_change_password`(bool), `is_active`(bool), `last_login`(ISO str or null).

**`POST /api/v1/admin/accounts/set-password`**
```json
{"login":"887914","new_password":"…"}     // new_password: 8..128 chars, login: 1..64
→ 200 {"status":"password set","login":"887914"}
→ 404 account not found   → 503 no account repository wired
```
Stores only the Argon2 hash. This is the **only** write on the admin plane, and it exists because
login requires a hash — there is no `CreateAccountHandler` yet.

### 2.4 Manager plane (MT5-shaped) — `Authorization: Bearer`

Response envelope for the five trading calls is MT5's own:
```json
{"answer":{"action":"Buy","symbol":"EURUSD","volume":"0.10","price":null,
           "stop_loss":null,"take_profit":null,"comment":null},
 "result":{"request_id":"<uuid>","order_ticket":0,"deal_ticket":null,
           "position_ticket":null,"price":"1.15945","volume":"0.10",
           "retcode":0,"comment":"Order placed successfully","timestamp":null}}
```
`retcode: 0` = success. Errors surface as HTTP `400` (domain refusal, `detail` = the reason) or
`500`. The declared `201 ExceptionResult {message, code, stackTrace}` is an MT5-compatibility shape.

🔴 **Read this before building a dealer ticket:** `get_current_manager` is literally
`get_current_user`, and every trading handler does `account_login=manager.login`. **These endpoints
trade on the CALLER's own account — there is no way to name a target client.** For an admin UI that
must act on behalf of clients, that is the single biggest functional gap (§4, B1).

| Endpoint | Body / Query | Notes |
|---|---|---|
| `POST /manager/Connect` | `{version, clientAgent, clientIP}` | → `ConnectResponse{retcode, sessionId, accessLevel, userLogin, userGroup, userName, userEmail, permissions, serverTime, message}` |
| `POST /manager/Disconnect` | — | → `{retcode, message, sessionId}` |
| `GET /manager/IsConnected` | — | → `{connected, sessionId, userLogin, serverTime}` |
| `GET /manager/SessionInfo` | — | → `{sessionId, userLogin, userGroup, accessLevel, clientAgent, clientIP, connectedAt, lastActivity, expiresAt}` |
| `GET /manager/UserGet?login=123` | **required** `login:int` | → **any** account: `{login, group, currency, balance, credit, equity, margin, free_margin, margin_level, leverage, enable, enable_charts, enable_news, enable_trades, password_phone, email, country, city, address, phone, registration, last_visit, last_pass_change, comment}` · 503 unwired / 404 unknown / 500 |
| `GET /manager/PositionGet?login=&symbol=` | both optional | → `PositionInfo[]{ticket:int, login:int, symbol, action, volume, price_open, price_current, sl, tp, swap, profit, commission, magic:int, comment, time_create, time_update}`. **With no filters this is your cross-account positions list** — but 🔴 it is broken today, see **F8/F9**. Do not wire the Positions page to it until those are fixed. |
| `POST /manager/OrderSend` | `{symbol, operation, volume, price?, stoploss?, takeprofit?, deviation?, comment?}` | `operation` ∈ `Buy, Sell, BuyLimit, SellLimit, BuyStop, SellStop` (case-sensitive). Pending types **require** `price` → else 400. Wire aliases: `stoploss`/`takeprofit` (the model also accepts `stop_loss`/`take_profit` via `populate_by_name`). |
| `POST /manager/OrderClose` | `{ticket:int, volume?, price?, deviation?}` | omit `volume` for a full close |
| `POST /manager/OrderDelete` | `{ticket:int}` | only PLACED / PARTIALLY_FILLED |
| `POST /manager/OrderModify` | `{ticket:int, price?, stoploss?, takeprofit?, expiration?}` | only PLACED / PARTIALLY_FILLED |
| `POST /manager/DealModify` | `{ticket:int, stoploss?, takeprofit?}` | SL/TP on an open position, via Reversal + Correction so the deal ledger stays immutable. Response `result.comment` carries both new deal ids. |
| `GET /manager/Ping` | — | `{retcode, serverTime, status, latencyMs}` |
| `GET /manager/StartTimeUtc` | — | `{serverName, serverVersion, startTimeUtc, uptimeSeconds, uptimeHuman, buildNumber, apiVersion, pythonVersion}` |
| `GET /manager/MemoryUsage` | — | `{retcode, rssMb, vmsMb, sharedMb, textMb, dataMb, percent, cpuPercent, openFiles, numThreads}` |
| `GET /manager/Version` | — | `{serverName, serverVersion, apiVersion, buildNumber, pythonVersion, buildDate}` |

### 2.5 Client trade plane — `Authorization: Bearer`

Ownership is enforced server-side: `account_login` comes **from the token, never the body**. You
cannot close or modify another client's position by guessing an id.

**`POST /api/v1/trade/orders`**
```json
{"symbol":"EURUSD","order_type":"BUY","volume":"0.10",
 "price":null,"type_filling":"FOK","stop_loss":null,"take_profit":null,
 "comment":null,"expiration":null}
```
`order_type` ∈ `BUY, SELL, BUY_LIMIT, SELL_LIMIT, BUY_STOP, SELL_STOP, BUY_STOP_LIMIT, SELL_STOP_LIMIT`.
`volume`/`price`/SL/TP may be numbers or strings — **send strings**. `price` is required for pendings.
→ `200`
```json
{"ticket_id":"4abc285b-…","symbol":"EURUSD","order_type":"BUY","volume":"0.10000000",
 "filled_volume":"0.10000000","price":"1.15945","state":"FILLED",
 "created_at":"2026-09-12T14:…","message":null}
```
`state` ∈ `PLACED, PARTIALLY_FILLED, FILLED, CANCELLED, REJECTED, EXPIRED`. A resting pending
returns `PLACED`. → `400` with the domain reason (insufficient margin, stale quote, market closed,
volume out of bounds) · `401` unresolvable login · `503` unwired · `500` unexpected.

**`POST /api/v1/trade/positions/{position_id}/close`** — `POST`, not `DELETE`, because a partial
close carries a volume and DELETE-with-body is unreliable through proxies.
```json
{"volume":"0.01","price":"77384.23","comment":"…"}   // both optional; omit price = at market
```
→ `200`
```json
{"position_id":"886098_BTCUSD_…","symbol":"BTCUSD","volume_closed":"0.01000000",
 "volume_remaining":"0.01000000","close_price":"77384.23","realized_pnl":"0.50000000",
 "deal_id":"86555a10-…","fully_closed":false,"message":"Position closed"}
```
`volume_closed` = `volume_before − volume_remaining`. `realized_pnl` and `deal_id` come from the
**booked OUT deal** (D14), so a partial close reports the leg's realised PnL, not the remainder's
floating PnL. → `404` unknown/foreign position · `400` domain refusal · `503` · `500`.

**`PUT /api/v1/trade/orders/{ticket_id}`** — `{"price":…,"stop_loss":…,"take_profit":…}` (all optional)
→ `OrderActionResponse{status:"modified", ticket_id, order_state, price, stop_loss, take_profit, volume_current, comment}`

**`DELETE /api/v1/trade/orders/{ticket_id}`** — no body → same shape with `status:"cancelled"`.

### 2.6 Client account plane — `Authorization: Bearer`

**`GET /api/v1/account/info`** →
`{login_id, group, balance, equity, margin_used, margin_free, margin_level, currency}` — all strings,
`margin_level` in percent, **derived on read** (D1/D2). `503` if unwired, `500` on error — it never
falls back to a stale JWT snapshot.

**`GET /api/v1/account/positions`** →
`PositionResponse[]{position_id, symbol, side, volume, average_price, unrealized_pnl, swap}`.
Note `side` here vs `action` on the manager plane — the two planes use different words.
`unrealized_pnl` is valued on demand through the risk engine, so it is correct even when the stored
`positions.profit` is stale (which is exactly how D13 hid for months).

### 2.7 Market data — no auth

**`GET /api/v1/market-data/history/{symbol}/ticks?start=&end=&limit=1..100000`** (default limit 10000,
default window = last 24 h) →
```json
{"symbol":"EURUSD","count":2,
 "ticks":[{"bid":"1.15931","ask":"1.15938","spread":"0.00007",
           "timestamp":"2026-09-12T12:31:09+00:00","source":"TRADE_SERVER"}]}
```
`source` ∈ `MOCK | TRADE_SERVER` — **every tick is self-labelled**, so the UI can badge simulated
data. This is the honest way to show provenance; surface it.

**`GET /api/v1/market-data/history/{symbol}/bars?timeframe=&limit=1..10000`** →
```json
{"symbol":"EURUSD","timeframe":"1m","count":0,"bars":[]}
```
`timeframe` ∈ `1m, 5m, 15m, 30m, 1h, 4h, 1d, 1w, 1M`.
🔴 **`bars` is empty in practice — the table has 0 rows in Neon after 30+ fills.** Nothing persists
bar history yet. Do not build a chart page against this until it does.

⚠️ Both endpoints swallow repository exceptions and return `200` with `count: 0`. That breaks the
project's own "refuse rather than fake" law: a dead history store is indistinguishable from
"no data in range". Treat `count: 0` as *unknown*, not *empty* — and see §5.

### 2.8 WebSockets

**`WS /api/v1/manager/ws/subscriptions` — the only working socket.** JSON frames both ways.

Client → server:
```json
{"action":"auth","token":"<jwt>"}                                  → {"status":"success","message":"Authenticated","client_id":"manager_<sub>"}
{"action":"subscribe","event_types":["ticks","orders","deals","positions"]}
                                                                    → {"status":"success","message":"Subscribed to […]","subscriptions":[…]}
{"action":"unsubscribe","event_types":["ticks"]}                     → same shape
{"action":"ping"}                                                    → {"status":"success","message":"pong"}
```
`subscribe`/`unsubscribe` before `auth` → `{"status":"error","message":"Not authenticated"}`.

Server → client, pushed by `WebSocketEventBridge` from the domain event bus:

| `event_type` | payload |
|---|---|
| `ticks` | the raw `TICK_RECEIVED` payload |
| `orders` | `{"action":"created"｜"cancelled"｜"modified", …order payload}` |
| `deals` | `{"action":"created", …deal payload}` |
| `positions` | `{"action":"opened"｜"closed", …position payload}` |

Enveloped as `{"event_type": …, "payload": …, …}` by `ManagerSubscriptionManager.broadcast`.
Subscribe to exactly the event types the page needs — this is a fan-out, not a firehose.

**`WS /ws/stream`** (public, no auth) and **`WS /ws/user`** (send `{"token":"…"}` as the first text
frame; replies `{"status":"authenticated","user_id":…}`; bad token → close code `1008`):
🔴 **both accept connections and then never send anything.** See §5.

---

## 3. Frontend gap matrix — every call in `src/browser/modules/api.ts`

✅ usable now (prefix fix only) · ⚠️ usable via a different endpoint · ❌ does not exist

| `API.*` method | Frontend calls | Backend reality | |
|---|---|---|---|
| `getAccounts` | `GET /admin/accounts` | `/api/v1/admin/accounts?limit=` | ✅ |
| `getAccountDetail(login)` | `GET /admin/accounts/{login}` | `GET /api/v1/manager/UserGet?login=` (Bearer, richer) | ⚠️ |
| `createAccount` | `POST /admin/accounts` | nothing — no `CreateAccountHandler` | ❌ |
| `updateAccount` | `PUT /admin/accounts/{login}` | nothing | ❌ |
| `deleteAccount` | `DELETE /admin/accounts/{login}` | nothing | ❌ |
| `getPositions` | `GET /admin/positions` | `GET /api/v1/manager/PositionGet` (no filters = all accounts) — **broken today: returns `[]` + `ticket:0`, see F8/F9** | ⚠️🔴 |
| `getDeals` | `GET /admin/deals` | **nothing anywhere.** No deal-read endpoint on any plane | ❌ |
| `getOrders` | `GET /admin/orders` | nothing | ❌ |
| `getOrderHistory` | `GET /admin/orders/history` | nothing | ❌ |
| `cancelOrder(ticket)` | `POST /admin/orders/{t}/cancel` | `POST /api/v1/manager/OrderDelete {ticket}` — caller's own account only | ⚠️ |
| `placeOrder` | `POST /admin/trade/order` | `POST /api/v1/manager/OrderSend` — **caller's own account only**; body shape differs (`operation` not `type`, `stoploss` not `price_sl`) | ⚠️ |
| `getSymbols` | `GET /admin/symbols` | `/api/v1/admin/symbols` | ✅ |
| `getSymbolDetail` | `GET /admin/symbols/{s}` | `/api/v1/admin/symbols/{s}` | ✅ |
| `createSymbol` | `POST /admin/symbols` | nothing — no `CreateSymbolHandler` | ❌ |
| `updateSymbol` | `PUT /admin/symbols/{s}` | nothing | ❌ |
| `deleteSymbol` | `DELETE /admin/symbols/{s}` | nothing | ❌ |
| `getGroups` | `GET /admin/groups` | `/api/v1/admin/groups` | ✅ |
| `getGroupDetail` | `GET /admin/groups/{n}` | `/api/v1/admin/groups/real/real` (slash form) | ✅ |
| `createGroup` | `POST /admin/groups` | **code exists but is not mounted** — `api/routers/admin/groups.py` declares `POST /api/v1/admin/groups/create` and `main.py` never imports it | ⚠️🔴 |
| `updateGroup` | `PUT /admin/groups/{n}` | nothing | ❌ |
| `createGroupSymbolOverride` | `POST /admin/groups/{n}/symbols` | nothing | ❌ |
| `getRoutingRules` | `GET /admin/routing` | nothing over HTTP — the data **is** there (`mt5_routing_rules` + `routing_rules` tables, M8 loader, `cli seed --mt5-routing`) | ❌ |
| `createRoutingRule` | `POST /admin/routing` | nothing | ❌ |
| `updateRoutingRule` | `PUT /admin/routing/{id}` | nothing | ❌ |
| `deleteRoutingRule` | `DELETE /admin/routing/{id}` | nothing | ❌ |
| `enableRoutingRule` | `POST /admin/routing/{id}/enable` | nothing | ❌ |
| `disableRoutingRule` | `POST /admin/routing/{id}/disable` | nothing | ❌ |
| `reorderRoutingRules` | `POST /admin/routing/reorder` | nothing — and **order is the whole semantic** (M8 is top-down first-match), so this one matters most | ❌ |
| `getGateways` | `GET /admin/gateways` | nothing — no gateway config plane at all (no `mt5_gateways` table; migration 009 not written). The 3 gateways exist only in the MT5 export fixtures | ❌ |
| `createGateway` | `POST /admin/gateways` | nothing | ❌ |
| `updateGateway` | `PUT /admin/gateways/{id}` | nothing | ❌ |
| `testGateway` | `POST /admin/gateways/{id}/test` | nothing | ❌ |
| `getTicks` | `GET /admin/ticks` | **no live-tick snapshot endpoint exists.** Only WS, and only `/manager/ws/subscriptions` works | ❌ |
| `getRiskSummary` | `GET /admin/risk/summary` | nothing | ❌ |
| `getRiskExposure` | `GET /admin/risk/exposure` | nothing over HTTP — the coverage account's `exposure` JSON **is** maintained in the domain | ❌ |
| `getRiskMarginCalls` | `GET /admin/risk/margin-calls` | nothing | ❌ |

**Score: 5 ✅ · 6 ⚠️ · 25 ❌.** Also unmapped from your UI: the entire `data-feeds` page
(no feeder endpoints), `network-cluster` (probes `localhost:8000/8001/8002/8004` with `HEAD`;
`infrastructure/cluster/` is empty and `cli sync` is the only cluster-ish command),
and the `market-watch` page (needs `getTicks`).

Backend endpoints your `api.ts` does **not** use yet and should: `/api/v1/admin/status`,
`/api/v1/admin/managers`, `/api/v1/manager/{Ping,Version,StartTimeUtc,MemoryUsage,SessionInfo}`
(a whole "server status" strip for free), `/api/v1/market-data/history/*`, and
`WS /api/v1/manager/ws/subscriptions`.

---

## 4. What has to be built, in the order the UI needs it

**Tier A — the UI is unusable without these**

| | Build | Why first |
|---|---|---|
| **B0** | **Fix `PositionGet` (F8 + F9).** Guard the nullable `price_current`, adopt the `/account/positions` contract (503 unwired, 500 on error, never a silent `[]`), and expose `position_id` as a string. | It is the only cross-account positions read the backend has, your Positions/Exposure/Margin-Call pages all depend on it, and today it returns `[]` + `ticket: 0` against your live database. Roughly 20 lines. |
| **B1** | **Manager-on-behalf-of.** Every `/manager/*` trading call must accept a target `login`. Today `account_login = manager.login`, so an admin can only trade their own account. Add `login` to `OrderSend/OrderClose/OrderDelete/OrderModify/DealModify`, authorise it against the manager's `group_scope` + rights bitmask. | Nothing in a dealer/admin UI works otherwise. Also finally makes the Manager `Rights` bitmask mean something. |
| **B2** | **`GET /api/v1/admin/orders`, `/deals`, `/positions`** (+ history variants, filters: login/symbol/state/date range, pagination). | Your Orders, Deals and Positions pages have no data source at all. `/deals` is the worst — there is no deal-read endpoint on *any* plane, so the IN/OUT lifecycle you just fixed in D11–D15 is invisible to the UI. |
| **B3** | **`GET /api/v1/admin/ticks`** — a snapshot of the last known bid/ask/age per symbol from `MarketDataEngine`, plus `source`. | Market Watch page. Cheapest high-value endpoint: the engine already holds the ticks; it just isn't exposed. |
| **B4** | **Mount `api/routers/admin/groups.py`.** One line in `api/main.py`. Then align the path (`/groups/create` vs the frontend's `POST /groups`) and add `PUT`. | `CreateGroupHandler` already exists and is already tested — this is free. |

**Tier B — the config plane the UI is shaped around**

| | Build | Notes |
|---|---|---|
| **B5** | Symbol CRUD (`POST/PUT/DELETE /admin/symbols`) + a `CreateSymbolHandler`. | Your Symbols page has 13 tabs (Common, Currency, Quotes, Sessions, Trade, Execution, Margin, Margin Rates, Swaps, Options, Bonds, Futures). Only ~45 of MT5's 121 symbol fields are modelled; the rest live in the `mt5_extra` quarantine. **Decide now whether the UI edits quarantined fields** — if yes, the write path must round-trip them or you will silently lose wire fidelity, which is the project's signature claim (392/392 byte-identical). |
| **B6** | Group CRUD + `PUT /admin/groups/{n}` + `POST /admin/groups/{n}/symbols` (per-group symbol overrides) + expose the **commission rules** and **symbol override** contents, not just their counts. | Your Groups modal has 9 tabs. `SpreadDiff`/`SpreadDiffBalance` per group-symbol is where B-Book markup lives (M7) — that is the money control and it has no UI write path today. |
| **B7** | Routing CRUD + **reorder**. | M8 evaluates top-down first-match, so list order *is* semantics. The table exists (`mt5_routing_rules`) and replays your broker's two real rules (18/18 proof) — it just has no HTTP. |
| **B8** | Gateway config plane: `mt5_gateways` table (migration 009) + loader + repository + CRUD + `POST /{id}/test`. | Blocks your Gateways page **and** the Translates/symbol-rename work. `TRANSLATE_FIELDS` and the markup maths already exist from M13; there is nowhere to put a row. |
| **B9** | Risk endpoints: `/admin/risk/{summary,exposure,margin-calls}`. | The coverage account's `exposure` JSON is already maintained (`{"EURUSD":"-2.30","BTCUSD":"-0.01"}`) — `/exposure` is mostly a read. `margin-calls` needs a query over `so_activation`. |

**Tier C — make the live stuff real**

| | Build |
|---|---|
| **B10** | Fix or delete `/ws/stream` + `/ws/user` (§5). Bridge `WebSocketEventBridge` to `ConnectionManager` too, or remove them so the UI can't connect to a dead socket. |
| **B11** | Bar persistence (`bars` = 0 rows) before any charting page. |
| **B12** | Feeder endpoints for the Data Feeds page; cluster/node endpoints for Network Cluster. |

---

## 5. Bugs found while mapping this (new — not in any report)

**🔴 F1 — `/ws/stream` and `/ws/user` are dead sockets.** `ConnectionManager.broadcast_tick()` and
`.send_user_update()` are defined in `api/websockets/manager.py` and **called nowhere** outside
`api/websockets/manager.py` itself. `WebSocketEventBridge` broadcasts exclusively to
`get_manager_subscription_manager()`, i.e. to `/api/v1/manager/ws/subscriptions`. So the two public
sockets accept a connection, register it, and then never send a frame — forever, with no error.
A Market Watch page wired to `/ws/stream` shows a connected socket and no prices. **This is the exact
shape of D6 and of M5 defect 9** (healthy-looking connection, silent absence of data), and it is why
B3 (`GET /admin/ticks`) matters: a polling snapshot is honest in a way this socket currently isn't.

**🔴 F2 — `get_current_user` fabricates an account.** `api/auth/dependencies.py`: if the repository
is missing, or the lookup raises, or the login is unknown, it does **not** 401 — it constructs
`Account(login=100001, balance=10000, equity=10000, margin_level=999999)` and returns it. Since
`get_current_manager = get_current_user`, every manager endpoint inherits this. A manager call with a
valid-signature token for an unknown login operates on an invented account with invented money, and
returns 200. This directly contradicts D2's fix ("never a silent fallback") and the project's design
law. It also means `POST /manager/OrderSend` can appear to succeed against nothing.

**🟠 F3 — `api/routers/admin/groups.py` is never mounted.** `POST /api/v1/admin/groups/create` and
`CreateGroupHandler` exist and are imported by nothing; `api/main.py` imports only `admin_router`.
Same class as D2/D11 ("handler complete, never registered"). One-line fix (B4).

**🟠 F4 — market-data history swallows failures.** Both routes wrap the repository call in
`except Exception: pass` and return `200 {"count":0}`. A dead history store is indistinguishable from
"no data in this range". Should be the `/account/positions` contract: 503 unwired, 500 on error.

**🟠 F5 — `pyproject.toml` does not declare the dependencies the API needs.** `argon2-cffi`, `pyotp`,
`hypothesis`, `aiosqlite`, `asyncpg` are all required; `psycopg2-binary` is declared but unused (the
code dials `postgresql+asyncpg`). `pip install -e .` on a clean machine yields an app that cannot
import its own auth module. This will bite whoever sets up the frontend's dev backend first.

**🟡 F6 — naming drift between planes.** The manager plane says `action`/`sl`/`tp`/`ticket`; the
client plane says `side`/`stop_loss`/`take_profit`/`position_id`. Both are defensible (manager mirrors
MT5), but the frontend will need two mappers. Worth deciding before the UI hardcodes either.

**🔴 F8 — `GET /api/v1/manager/PositionGet` returns `[]` for the entire book, with HTTP 200.**
Verified against your live Neon, not inferred. The serializer dereferences a nullable column
unguarded:

```python
price_current=p.price_current.value      # migration 002 made price_current NULLABLE
```

and the route wraps the whole list comprehension in `except Exception: logger.warning(...)` and then
falls through to `return []`. So **one position with `price_current IS NULL` anywhere in the result
set blanks the entire response.** Right now:

```
open positions in Neon: 31 total · 24 with price_current NULL · => PositionGet would return []
```

Two more silences in the same 12 lines: `if handler:` (not `is None`) means an **unwired** handler
also returns `[]` rather than the 503 that D2/D11 established, and any repository error is a
`logger.warning` plus `[]`. This is precisely the anti-pattern M14 named — *"a 200 with a plausible
body over absent behaviour is worse than a 501"* — and it is the endpoint §3 offers as the substitute
for your missing `GET /admin/positions`, so it has to be fixed before the Positions page can use it.
Same unguarded `.value` on a nullable `price_current` was already found once, in `close_position.py`
(D10); this is the second instance of it.

**🔴 F9 — every `PositionInfo.ticket` is `0`.** The serializer does
`int(p.position_id) if p.position_id.isdigit() else 0`, but position ids are
`{login}_{SYMBOL}_{8 hex}` — measured: **0 of 31** open position ids are numeric. So the field is
always `0`. A table keyed on `ticket` collapses every row into one, and
`POST /manager/OrderClose {"ticket": …}` can never address a position, because the only id the UI was
given is `0`. Root cause is a schema mismatch: `PositionInfo.ticket` is typed `int` (MT5's shape)
while the platform's real identifier is the string `position_id`. Either add `position_id: str` to
`PositionInfo` and key the UI on that, or make `ticket` a string. Note the client plane already does
this correctly — `PositionResponse.position_id` is the string.

**🟡 F7 — your `api.ts` ships a hardcoded admin key.**
`ADMIN_API_KEY = 'default_admin_api_key_token_change_in_production'`. Correction to what I first
wrote: the boot gate does **not** reject that literal — `check_server_secrets()` only refuses a
`SECRET_KEY` beginning `BROKER_PLATFORM_SECRET_KEY`, an unset/short `SECRET_KEY`, or an *unset*
`ADMIN_API_KEY`. So if someone started the server with that exact literal, the frontend would
authenticate. It won't match a properly generated key, which is what M5's fail-hard forces you to
set. The real problem is unchanged and worse: **an admin API key cannot live in a browser bundle** —
it ships to every client and grants the whole config plane. The MT5 admin UI needs a real manager
login (session + rights bitmask), which is B1's authorisation work. Until then the Theia extension is
a development tool only and must never be exposed beyond localhost.

---

## 6. Frontend quickstart

```ts
// 1. Base URL — the prefix your api.ts is missing
const BASE = 'http://localhost:8000/api/v1';

// 2. Two auth schemes
const adminHeaders = { 'Content-Type': 'application/json',
                       'X-Admin-API-Key': import.meta.env.ADMIN_API_KEY };   // never a hardcoded literal
const bearer = (jwt: string) => ({ 'Content-Type': 'application/json',
                                   Authorization: `Bearer ${jwt}` });

// 3. Login (manager sessions use the same token today)
const { access_token } = await fetch(`${BASE}/auth/login`, {
  method: 'POST', headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ login_id: '887914', password: '…' }),
}).then(r => { if (!r.ok) throw new Error('Invalid credentials'); return r.json(); });

// 4. Config plane (admin key)
const status  = await fetch(`${BASE}/admin/status`,  { headers: adminHeaders }).then(r => r.json());
const groups  = await fetch(`${BASE}/admin/groups`,  { headers: adminHeaders }).then(r => r.json());
const oneGrp  = await fetch(`${BASE}/admin/groups/real/real`, { headers: adminHeaders }).then(r => r.json());
const symbols = await fetch(`${BASE}/admin/symbols`, { headers: adminHeaders }).then(r => r.json());
const accts   = await fetch(`${BASE}/admin/accounts?limit=200`, { headers: adminHeaders }).then(r => r.json());

// 5. Cross-account reads the UI needs (bearer)
const pos  = await fetch(`${BASE}/manager/PositionGet`, { headers: bearer(access_token) }).then(r => r.json());
const acct = await fetch(`${BASE}/manager/UserGet?login=887914`, { headers: bearer(access_token) }).then(r => r.json());

// 6. Live updates — the ONLY working socket
const ws = new WebSocket('ws://localhost:8000/api/v1/manager/ws/subscriptions');
ws.onopen = () => {
  ws.send(JSON.stringify({ action: 'auth', token: access_token }));
  ws.send(JSON.stringify({ action: 'subscribe', event_types: ['ticks', 'orders', 'deals', 'positions'] }));
};
ws.onmessage = (e) => { const m = JSON.parse(e.data); /* m.event_type, m.payload */ };

// 7. Decimals: ALWAYS strings. Never parseFloat money.
//    "0E-8" is zero. margin_level "999999" is the no-margin sentinel, not a real level.
```

**Backend the frontend dev needs running:**
```bash
cd qwe-agen-broker-platform-backend/work/bp
pip install -e . && pip install argon2-cffi pyotp aiosqlite asyncpg hypothesis   # F5
export SECRET_KEY=$(python3 -c "import secrets;print(secrets.token_hex(32))")
export ADMIN_API_KEY=$(python3 -c "import secrets;print(secrets.token_hex(24))")   # give THIS to the UI
export DATABASE_URL="postgresql://…/neondb?sslmode=require"    # or sqlite+aiosqlite:///./dev.db
export MARKET_DATA_SOURCE=mock                                 # labelled ticks, no terminal needed
export MOCK_TICK_RATE_MS=250
python3 -m uvicorn api.main:app --host 0.0.0.0 --port 8000
# then: http://localhost:8000/docs  — Swagger, and the Authorize button takes the admin key
```
Accounts have no password until you set one:
`POST /api/v1/admin/accounts/set-password {"login":"…","new_password":"…"}` — then login works.
(`cli seed` creates 7 groups / 5 symbols / the coverage account / the first admin.)
