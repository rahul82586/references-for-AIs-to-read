# ENDPOINT CATALOG — THE COMPLETE SURFACE MAP
**Written:** 2026-09-14 (session 7) · **Status: DRAFT for user approval — the master map every future milestone codes against.**

**Sources (all from the repo's own corpus, nothing guessed):**
- MT5 **Web API**: 231 commands / 44 noun families (`Web-API.md`, exact `/api/{noun}/{verb}` list extracted)
- MT5 **Manager API** (C++): IMTManagerAPI / IMTAdminAPI / IMTDealerSink / IMTManagerSink families (`Manager-API.md`)
- **mtapi.io** commercial wrapper: the 124-endpoint checklist (`mtapi-docs/swagger.json` — the REST-ergonomics ruler, per the locked decision)
- **Ours today**: 61 operations / 52 paths (enumerated from the live OpenAPI schema, session 7)

**Legend:**
✅ BUILT (mounted, tested) · 🔵 M18-T1 (pure wiring — logic exists) · 🟡 M18-SKEL (honest 501 skeleton) · 🟠 M19+ (named future milestone) · ⚪ DEFERRED (explicit user decision) · ⛔ N/A (architecture: MT5's Windows-process topology; our equivalent is ops/config/process-roles, not an HTTP endpoint)

**Dialect doctrine (A5):** `admin/*` = REST dialect for the Theia UI (≈ MT5 Web API's role) · `manager/*` = MT5 method-name dialect for terminal/dealer tooling (≈ Manager API DLL's role) · `trade/account/auth/market-data` = client dialect · WS = the sink/subscription system. One application layer under all of them.

---

## PART 1 — ALL 44 MT5 WEB API FAMILIES → OUR SURFACE

### Identity & config

| MT5 family (verbs) | Our surface | Status |
|---|---|---|
| **auth** (start, answer) | `POST /auth/login` (client JWT) · `POST /manager/Connect` · bootstrap admin key. Dialect difference: JWT instead of challenge-hash — noted, deliberate; challenge-hash only needed if drop-in MT5 tooling must auth against us | ✅ |
| **user** (19: get, get_batch, total, add, update, delete, account, group, logins, change_password, check_password, check_balance, archive, restore, backup, certificate, otp_secret, get_external, sync_external) | `GET /admin/accounts` (paged=get_batch+total) · `GET /admin/accounts/{login}` (=account, the 6 tabs) · `POST /admin/accounts` (=add, step 6) · `POST /admin/accounts/next-login` (=logins "Next") · `POST /admin/accounts/set-password` (=change_password) · `manager/UserGet` | ✅ reads+create |
| ↳ user verbs not yet served | `PUT /admin/accounts/{login}` (update: per-tab partials + the 2 move rules) · `DELETE` (delete-vs-archive rule) · `POST /admin/accounts/{login}/check-password` (verify against Argon2 — **logic exists** in password_policy) · `GET /admin/accounts/{login}/otp` provisioning (ITwoFactorService exists) · archive/restore · check_balance (=UserBalanceCheck: balance vs ledger audit — **audit milestone**) · certificate | 🟡 update/delete skeletons (C1) · 🔵 check-password + otp (M18-T1, pure wiring) · 🟠 archive/restore/check_balance |
| ↳ ⛔ user.backup, get_external, sync_external | external-system sync & file backup = ops | ⛔ |
| **client** (add, get, get_ids, update, delete, history, user) | `POST /admin/clients` ✅ · `GET /admin/clients` (=get_ids, paged) ✅ · `GET /admin/clients/{id}` ✅ · `GET /admin/clients/schema` ✅ · `GET /admin/clients/{id}/accounts` (=client/user backlink — **find_page + one additive filter**) | ✅ + 🔵 backlink (M18) |
| ↳ client.update / client.delete / client.history | ClientUpdateHandler missing → skeleton; history = KYC/documents trail → backoffice | 🟡 · ⚪ |
| **group** (add, get, delete, next/shift/total, add_batch, delete_batch) | full CRUD + `/schema` + paged list. MT5's cursor pagination (next/shift) = our limit/offset + X-Total-Count (dialect difference, same capability). Batch variants = import tooling (cli) | ✅ (batch ⚪ low value) |
| **manager** (add, get, delete, next/shift/total) | `POST/GET/PUT /admin/managers…` full plane (step 7) + paged list (step 8) + rights + presets + schema. **delete missing** | ✅ + 🟡 DELETE skeleton |
| **symbol** (add, get, list, delete, get_group, next/shift/total, *_batch) | `GET /admin/symbols` + `/{name}` ✅ reads. **Writes missing** — the 121-field/quarantine decision must be made first (does the UI edit quarantined fields?) | ✅ reads · 🟡 writes skeleton (C2) · 🟠 real symbol CRUD |
| **symbol_group** (add, delete, list, …) | The Market-Watch symbol tree. **Not modelled at all** — no table, no entity | 🟠 config-plane milestone (with symbols) |
| **leverage** (add, delete, get, …) | The server-wide available-leverage list (the group dialog's dropdown source). We have per-group leverage_default/max only | 🟠 migration 010 (small) |
| **spread** (add, delete, …) | MT5's separate spread objects. **By architecture ⛔**: our spread lives on symbol + GroupSymbolOverride (M7). BUT the group-symbol-override WRITE endpoint (`POST /admin/groups/{n}/symbols` — where B-Book markup is configured, ENDPOINTS B6) is missing | ⛔ separate object · 🟡 override writes skeleton → 🟠 B6 |
| **holiday** (add, delete, …) | `create_holiday` command + repo reads/delete **exist with NO route** (verified) | 🔵 M18 B11 (full CRUD) |
| **route** (add, delete, get, …) | Routing rules: M8 engine + loader + table exist. **No HTTP.** `GET /admin/routing` in evaluation order = pure wiring; writes/reorder need a command layer | 🔵 GET (M18 B5) · 🟡 writes+reorder skeleton (C3) → 🟠 B7 |
| **common** (get, set) | Server common config. Read side = `/admin/status` + `/manager/SessionInfo/Version`; our config = settings.yaml + env (ops-owned writes) | ✅ partial · ⛔ writes |
| **time** (get, server, set) | `manager/StartTimeUtc` ✅ · **`GET /manager/ServerTime` missing (trivial)** · set = ops | 🔵 ServerTime (M18 micro) |
| **setting** (get, set, delete) | Per-manager UI settings store (MT5 keeps arbitrary per-manager blobs) | 🟠 low priority (UI convenience) |
| **firewall** (add, delete, …) | **Server-level ⛔** (deployment/Caddy). **Manager-level ✅** — the step-7 From/To IP allow-list per manager IS our firewall analogue | ✅ manager-level |
| **tls_certificate / history_sync / server (add/delete/restart) / plugin / test / logger / minwinbase** | MT5's Windows cluster topology: certificates, inter-server sync, server registry, DLL plugin hosting, diagnostics | ⛔ by architecture — our equivalents: Caddy TLS, process-roles milestone, entrypoints, ops tooling |

### Trading & dealer

| MT5 family (verbs) | Our surface | Status |
|---|---|---|
| **order** (get, get_batch, get_page, get_total, cancel, delete, update, reopen, backup) | reads: `GET /admin/orders` + `/orders/history` (paged, tri-state) ✅ · `manager/OrderGet` = docstring stub | ✅ admin · 🔵 OrderGet (M18 B2) |
| ↳ order actions | `manager/OrderSend/OrderClose/OrderDelete/OrderModify` ✅ **but caller's-own-account only**. On-behalf-of (`login` param + group-scope authorisation + audit) = **B1, the keystone milestone**. reopen = rare dealer op | ✅ self · 🟠 B1 · 🟠 reopen |
| ↳ order.update (admin correction) | `AdmTradeRecordModify` equivalent = trade modifications. `DealModify` ✅ exists in manager plane; admin-dialect correction endpoints | ✅ partial · 🟠 trade-modification milestone |
| **deal** (get*, update, delete, backup) | reads: `GET /admin/deals` ✅ (paged, entry filter) · `manager/DealGet` stub · update = `manager/DealModify` ✅ · **delete ⛔ BY DESIGN — a deal is an immutable fact; corrections only (domain docstring)** | ✅ · 🔵 DealGet (M18 B1) |
| **position** (get*, update, check, fix, delete, backup) | reads: `GET /admin/positions` ✅ + `manager/PositionGet` ✅ (F8/F9, live-proven) · close = OrderClose/`trade/positions/{id}/close` ✅ · check/fix = reconciliation repair (breaks exist, resolution workflow missing) · update = dealer correction · delete ⛔ (facts) | ✅ reads · 🟠 check/fix with audit · 🟠 correction |
| **trade** (balance, calc_profit, calc_rate_buy, calc_rate_sell, check_margin) | **The manager terminal's calculators.** balance = the ledger-backed `BalanceOperationCommandHandler` (built M16, **never mounted**). calc_* / check_margin = RiskEngine's pure functions (margin pipeline reproduces MT5 to the cent) — **all exist, none exposed** | 🔵 ALL FIVE (M18 B10 + new B12: `POST /admin/trade/{calc-margin, calc-profit, calc-rate, check-margin}` — pure reads on the engine, gated RIGHT_RISK_MANAGER / RIGHT_ACCOUNTANT for balance) |
| **dealer** (send_request, get_request_result) | Dealer intervention (requote/confirm workflow). Internal `dealer_queue` exists; no HTTP; needs B1's authorisation story | 🟡 skeleton (C11) → 🟠 B1+ |

### Market data & history

| MT5 family (verbs) | Our surface | Status |
|---|---|---|
| **tick** (last, last_group, history, stat) | `last/last_group` = `GET /admin/ticks` — engine's `get_latest_tick` per symbol + source + age, **pure wiring** · history/stat = the history plane (bars=0 today; client routes `/market-data/history/*` exist but read empty repos) | 🔵 last (M18 B6) · 🟠 history/stat |
| **chart** (get) · **history** (get*, delete, update) | Bars/OHLC storage + serving = the history-plane milestone (ClickHouse decision pending) | 🟡 skeleton (C9) → 🟠 |
| **book** (get) | Depth of market. No DOM aggregation; tied to the ECN decision | ⚪ deferred (ECN) |
| **subscription** (add, cancel, get, exist, config, history, join, update) | The sink system: `WS /manager/ws/subscriptions` + the registry (mirrors Subscribe{Account,Deals,Group,OrderProfit,Positions,Requests,Symbol,Ticks,User}) ✅ working. REST-style subscribe verbs = dialect difference (we push over WS, mtapi polls) | ✅ |
| ↳ client-plane sockets | `/ws/stream` + `/ws/user` **dead (F1)** | 🔵 M18 A4: fix or refuse honestly |
| **IsTradeSession / IsQuoteSession** (mtapi) | Symbol sessions ARE modelled (pre-trade checks use them) — expose `GET /admin/symbols/{s}/sessions` + the two boolean checks | 🔵 M18 (micro, pure read) |

### Risk & supervision

| MT5 family (verbs) | Our surface | Status |
|---|---|---|
| (mtapi) **OnAccountUpdate** margin-call events | SO state machine runs internally; events on the bus; no manager subscription for them | 🟠 (with WS event taxonomy) |
| **AccountsOnline** (mtapi; RIGHT_ACC_ONLINE=28 exists) | `is_online`/`last_login` are stored columns — a filtered find_page | 🔵 M18 (`GET /admin/accounts/online`) |
| risk reads (our own, per ENDPOINTS B9) | `/admin/risk/exposure` (coverage JSON maintained) · `/admin/risk/summary` (counts from existing repos) · `/admin/risk/margin-calls` (so_activation filter) | 🔵 ALL THREE (M18 B7-B9) |
| **UserBalanceCheck / position.check/fix** | Balance-vs-ledger and position-vs-deal audits — the reconciliation-breaks table exists; the *resolution* workflow doesn't | 🟠 audit milestone |

### Operations, content & compliance

| MT5 family | Our surface | Status |
|---|---|---|
| **report** (7 verbs) + mtapi DailyRequest×12 + SummaryGet | Report engine | ⚪ deferred by decision · 🟡 skeleton (C8) |
| **mail / email / messenger / news / notification** (24 verbs) | Internal mail, push, news | ⚪ deferred by decision · 🟡 skeletons (C10) |
| **journal/audit** (mtapi TradeJournal; MT5 logs every manager query/export/filter) | Nothing. The compliance gap; grows with B1 | 🟡 skeleton (C7) → 🟠 audit milestone |
| **document / attachment / comment** (13 verbs) | KYC document sub-entity missing (spec §5 says so); comments = plain columns on our entities ✅ dialect difference | ⚪ backoffice · ✅ comments-as-fields |
| **gateway** (10 verbs) | The LP config plane: `mt5_gateways` table doesn't exist (migration 010). TRANSLATE_FIELDS + markup maths exist (M13). module/restart = process control ⛔ | 🟡 skeletons (C4) → 🟠 M-010 |
| **feeder** (8 verbs) | Datafeed config plane — same story | 🟡 (C5) → 🟠 M-010 |
| **Allocations** (Admin-terminal feature, not a Web-API family) | Plan step 9 | 🟡 skeleton (C6) → 🟠 step 9 |

---

## PART 2 — THE mtapi-124 CHECKLIST, MAPPED

| mtapi group | Endpoints | Ours |
|---|---|---|
| Connect/Health/Status | Connect, Disconnect, IsConnected, ConnectionStatus, Ping, Health, MemoryUsage, StartTimeUtc, ServerTimezone, SessionInfo (10) | ✅ all (SessionInfo+ServerTime cover timezone) |
| Accounts/Users | Accounts, AccountDetails(+Many), UserDetails(+Many,+Pagination), AccountsSummary, AccountsOnline, UserGroups, UserPasswordChange, UserPasswordCheck, UserUpdate, UserArchive, UserBalanceCheck, AccountCreate(+AndDeposit), AccountDelete (17) | ✅ list/detail/create/next-login/set-password · 🔵 online, password-check · 🟡 update/delete · 🟠 archive/balance-check |
| Trading reads | Positions(+MT4Format), Orders, OpenedOrders(+Pagination), OrderHistory(+Pagination), PendingOrderHistory, DealHistory, PositionHistoryMT4Format (9) | ✅ all except MT4-format dialects ⛔ |
| Trading writes | OrderSend, OrderClose, OrderCloseAll, OrderDelete, OrderModify, ModifyOrder, ModifyDeal, OrderActivate, OrderUpdate, DealAdd(+Batch), DealPerform(+Batch), DealUpdate(+Batch), DealDeleteBatch, AdmTradeRecordModify(+Ex), AdmTradesDelete, Deposit, BalanceAdjustment (18) | ✅ OrderSend/Close/Delete/Modify/DealModify (self-account) · 🔵 Deposit/BalanceAdjustment (=B10) · 🟠 the dealer-correction family + CloseAll (with B1) · ⛔ DealDelete (facts are immutable) · ⛔ MT4-format |
| Symbols | SymbolGet, SymbolsList, SymbolsParams, SymbolGroups, SymbolGroupsForUserGroup, SymbolSessions, SummaryGet(+All), IsQuoteSession, IsTradeSession, SymbolGroupExecutionSet (10) | ✅ get/list/params · 🔵 sessions/is-trade/is-quote · 🟠 symbol-group tree + summaries(=reports) |
| Market data | Subscribe(+Many,+MarketWatch,+OrderProfit×3), Unsubscribe(×4), On* websockets (24), TickLast, TickAdd, TickHistory(+ByTime), TickStat, ChartRequest (33) | ✅ manager WS subscription system · 🔵 TickLast(=/admin/ticks) · 🟠 tick history/stat/chart (history plane) · ⛔ TickAdd (feed injection = datafeed plane, M-010) |
| Content/Compliance | EmailSend, MessengerSend, News, Holidays, TradeJournal, Segregated, OnAccountUpdate (7) | 🔵 Holidays · 🟡 TradeJournal skeleton · ⚪ Email/Messenger/News · 🟠 Segregated(=reports)/OnAccountUpdate |

**mtapi coverage after M18: ~55% served, ~15% honest-skeleton, ~20% future milestones, ~10% refused-by-design** (MT4 dialects, deal deletion, tick injection, file backup — things our domain deliberately does not do).

---

## PART 3 — OUR CURRENT 61 OPERATIONS (for the record)

client dialect: auth/login · trade/orders (POST/PUT/DELETE) · trade/positions/{id}/close · account/info · account/positions · market-data/history/{symbol}/{bars,ticks} · health
admin dialect: accounts (GET list/detail/schema, POST ×2+next-login+set-password) · clients (GET list/detail/schema, POST ×2) · groups (GET ×2+schema, POST ×2, PUT, DELETE) · managers (GET list/detail/rights/presets/schema, POST ×2+presets, PUT, DELETE preset) · status · symbols (GET ×2) · deals/orders/orders-history/positions (GET)
manager dialect: Connect · Disconnect · IsConnected · SessionInfo · Ping · Version · StartTimeUtc · MemoryUsage · UserGet · PositionGet · OrderSend · OrderClose · OrderDelete · OrderModify · DealModify · WS /ws/subscriptions

## PART 4 — M18 FINAL SCOPE (after this catalog audit)

**Prerequisites:** A1 D16 fix · A2 folder cleanup · A3 legacy fold-in · A4 sockets fix-or-refuse · A5 doctrine table.

**Tier 1 — wiring (grew from 11 to 17 items — the catalog found 6 more pure-wiring endpoints):**
B1 manager/DealGet · B2 manager/OrderGet · B3 manager/SymbolGet · B4 manager/GroupGet · B5 GET /admin/routing (ordered) · B6 GET /admin/ticks · B7-B9 risk exposure/summary/margin-calls · B10 POST /admin/accounts/{login}/balance (RIGHT_ACCOUNTANT) · B11 holidays CRUD · **B12 trade calculators (calc-margin/calc-profit/calc-rate/check-margin — RiskEngine pure reads)** · **B13 POST /admin/accounts/{login}/check-password** · **B14 GET /admin/accounts/online** · **B15 GET /admin/clients/{id}/accounts** · **B16 GET /admin/symbols/{s}/sessions + is-trade/is-quote checks** · **B17 GET /manager/ServerTime**

**Tier 2 — honest skeletons (501 + exact reason):** C1 account update/delete · C2 symbol writes · C3 routing writes+reorder · C4 gateways · C5 datafeeds · C6 allocations · C7 journal · C8 reports · C9 charts/history · C10 mail/news · C11 dealer requote/confirm · **C12 manager DELETE · C13 group-symbol overrides (B6 markup writes) · C14 account archive/restore**

**Tier 3 — milestone queue (order recommended):** ① B1 on-behalf-of + dealer authorisation · ② UpdateAccountHandler + migration 010 (D20, gateways, feeders, leverage list, symbol_group tree) · ③ symbol CRUD (after the 121-field decision) · ④ audit journal · ⑤ history plane (bars/ticks/chart) · ⑥ trade-modification family (corrections, reopen, close-all) · ⑦ F2 client-auth rebuild · ⑧ step 9 allocations logic · ⚪ deferred-by-decision: reports engine, mail/news/messenger, book/DOM+ECN, backoffice/documents, batch config imports.

**Post-M18 surface: 52 → ~80 paths. Post-Tier-3: ≈ full MT5 Web-API parity minus the deliberately-refused families.**

## PART 5 — STANDING RULES FOR EVERY ROW ABOVE

1. An endpoint is a promise: it works, or it refuses with the exact missing piece named (501/503). **Never 200-empty while unwired** (F8's shape — the new surface-completion proof bans it mechanically).
2. Every route has exactly one home (one dialect owns it; the other dialect may alias only where MT5 tooling compatibility demands, sharing ONE serializer).
3. Every gate is a named MT5 right from the 97-catalogue; reads use read-rights, writes use write-rights, funds use RIGHT_ACCOUNTANT.
4. Ticket rule platform-wide: venue number from external_id or null; canonical ids alongside.
5. Decimals as strings; rights as ints with decoded names; time as ISO-8601 UTC.
6. Every new route ships with HTTP-level tests + proof coverage in the same commit.
