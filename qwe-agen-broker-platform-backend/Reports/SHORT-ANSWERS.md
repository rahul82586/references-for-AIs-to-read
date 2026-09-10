# Short Answers — rabbittrix · MT5 operations · clustering · where to start

---

## 1. Is rabbittrix a broker platform like yours? **No.**

I cloned it and scanned the source rather than trusting folder names.

**Broker-feature scan across all 14 platform crates — hits:**

| Feature you're building | Hits in rabbittrix |
|---|---|
| A-book / B-book | **0** |
| Margin call / stop-out / margin level | **0** |
| Swap / rollover | **0** |
| Commission | **0** |
| Coverage / hedge account | **0** |
| Client groups + group leverage | **0** |
| Contract size | **0** |
| Netting / hedging mode | **0** |
| Leverage (anywhere) | **0** |
| KYC | **0** |
| Statements / reports | **0** |

**What it actually is:** two unrelated things in one repo — ① an FX **execution microservices** demo, and ② an **SMC (Smart Money Concepts) algo-strategy** engine. 11,709 LOC / 29 crates, and **14 of the 29 crates (`fx-smc-*`, 6,943 LOC) are the strategy layer**, not brokerage.

**Scale reality check:**

| Crate | LOC | What it really is |
|---|---|---|
| `fx-core` | 553 | `matching.rs` **232 LOC** + `orderbook.rs` **91 LOC** + `order.rs` 52 + audit/trade logs |
| `fx-risk` | 279 | `RiskLimits` has **4 fields**: `max_position_size`, `max_order_size`, `max_daily_loss`, `max_open_orders`. No margin, no leverage, no stop-out. |
| `fx-lp` | 83 | `LpVenue{venue_id, quote_mode(Streaming/Rfq), score, last_look_enabled}` + `best_venue()` + `generate_indicative_quote()` (mid ± bps) |
| `fx-router` | 76 | router + venue |
| `fx-md` | 78 | feed + quote |
| `fx-oms` | 127 | model + oms |
| `fx-exchange` | 62 | book + venue |

**Verdict:** it is a **latency/architecture reference**, not a domain reference. It has *no* MT5-like grouping/symbol system, *no* A/B book, *no* margin/swap/commission, and its "matching engine" is 232 lines.

**Still worth stealing (4 things):** the crate boundaries; **`venue` as a first-class routing concept** (you have none); **`fx-pricing`** (`engine`/`spread`/`risk_adjuster` — you have *no* pricing/spread/markup module anywhere); **`fx-liquidity-graph`** (`graph`/`planner` — your `lp_priority` list is a 1-D stub of this).

**Better references for broker semantics:** `FTHTrading/Broker-Dealer` (OMS/EMS/SOR, 15c3-1, 15c3-3, CAT/TRACE), `tfrmma/oms` (`margin_monitor.hpp`, `notional_gate.hpp`), `nautilus_trader` (`execution/matching_engine`, `protection.rs`, `portfolio`), and **your own MT5 corpus** — which is a better broker-domain reference than any public repo, because it's the real thing.

---

## 2. How MT5 operates — and one correction to your model

You said: *"history server handles data feed, gateway, charting, ticks"* → **correct.**
You said: *"trade server handles logic, calculation"* → **correct, plus it owns the entire configuration.**

| Server | Owns | Folders | Key `.ini` | Key `.dat` |
|---|---|---|---|---|
| **Trade** (`mt5Trade64.exe`) | client records, auth/authz, trade records, **check/manage/execute trade requests**, internal mail. **Main server also manages the whole system config.** | `archive/ bases/ config/ logs/ templates/` + `plugins/ reports/ confirms/ settings/` | `access, common, feeders, groups, history_sync, holidays, managers, performance, requests (=routing), server, servers, symbol_groups, symbols, time, license.lic` — **encrypted** | `users.dat, orders.dat+idx, positions.dat+idx, executions.dat, certificates.dat+idx, kyc.dat, geo.dat, confirmation.dat, daily.dat`, `deals/deals_yyyy.mm.dat+idx`, `history/`, `mail/`, `daily/`, `crm/` (clients + documents + comments + files), `archive/users_archive_yyyy.dat` |
| **History** (`mt5history64.exe`) | **receives & filters price/news from gateways and datafeeds**, packs it, stores/serves 1-min bars + ticks, stores/serves news, distributes Live Updates. **Hosts ECN matching.** | `bases/ config/ datafeed/ gateway/ history/ liveupdate/ logs/ plugins/` | `common, ecn_symbols, mt5srvupdater, history_sync, server, servers, symbol_groups, symbols, time` | `bases/ecn/symbols/{S}/matching.dat`, `filling_items.dat`, `books/yyyymmdd.book`, `filling_orders.dat`, `executions/`, `history/`; `history/[2 chars]/[symbol]/yyyy.hsc` + `yyyy.tkc` |
| **Access** (`mt5access64.exe`) | **proxy + firewall.** Processes client connections, packs auth requests → trade server, antiflood, **caches history/DOM/news to offload history server**, caches+serves Live Update, **monitors trade & history server health (witness → auto-failover)** | `bases/ config/ history/ liveupdate/ logs/` | `server, servers, symbols, time` | `news.dat+idx`, `performance.dat`, `history/[2c]/[sym]/yyyy.hsc|tkc`, `tickers.dat` |
| **Backup** | real-time backup of trade+history; daily DB copies; backs up gateway `settings.dat` + executions DB; **automatic failover**; hardware migration; manual restore *even when the main server is down*; **SQL export → MySQL/MariaDB/PostgreSQL/Firebird/MSSQL/Oracle** | — | — | — |

**The four architectural facts that matter for you:**

1. **Gateways and datafeeds live on the HISTORY server**, not the trade server. They are **separate `.exe` processes**, one folder per instance (`gateway/[name]/[config]/` with its own `logs/yyyymmdd.log` + `*.dat`), loaded via `MT5APIGateway64.dll`. Same for datafeeds.
2. **Plugins = trade-server DLLs (Server API). Reports = DLLs (Report API).** Both are *loaded modules*, not services. Your `DynamicMargin.dll` and `FXConnect.Plugin.MT5.x64.dll` in the live export are exactly this.
3. **Config is per-server, encrypted `.ini`, pushed from the main trade server.** Secondary servers *receive* config + time sync from the main over its port. There is no shared config DB.
4. **Everything hot is a flat binary `.dat` + `.idx` pair, memory-loaded at startup.** History is **sharded by year and by the first 2 characters of the symbol** (`history/EU/EURUSD/2026.hsc`) explicitly *"to reduce load on the file system and provide faster data operations."*

---

## 3. Can we clusterise into MT5's folder format? Yes — but **~80% of it is free**

Python has no compile step, so there is no `mt5trade64.exe` equivalent to wait for. The MT5 layout is **80% data/config/log convention and only 20% binary**. You can adopt the convention **today**, and the "compiled artefact" question disappears:

| MT5 | You | When |
|---|---|---|
| `mt5trade64.exe` | `python -m broker trade` → later a PyInstaller/`shiv`/`pex` onefile, or just a container image | **Now** (entrypoint) · onefile **never needed** if you ship Docker |
| `config/*.ini` (encrypted) | `config/*.yaml` + `.env` (secrets) | **Now** |
| `bases/*.dat` + `*.idx` | PostgreSQL + Redis + ClickHouse | **Now** (already chosen, correctly) |
| `logs/yyyymmdd.log` | `logs/` + structured JSON, daily rotation | **Now** — trivial, do it |
| `plugins/*.dll` (Server API) | Python **entry points** / importable modules | Later |
| `reports/*.dll` (Report API) | report modules | Deferred |
| `gateway/[name]/[cfg]/` | one container per LP connector, own volume | Later |
| `history/[2c]/[sym]/yyyy.hsc` | ClickHouse `PARTITION BY toYYYYMM(ts)` + symbol bucketing | Later |
| `templates/`, `confirms/`, `settings/`, `archive/` | deferred (mail, statements, manager dashboards, archived accounts) | Deferred |

**Target runtime layout** (a *deployment* dir, **not** your source tree):

```
deploy/
├── docker-compose.yml     .env
├── trade/       config/{common,groups,symbols,symbol_groups,managers,requests,holidays,time,access}.yaml
│                bases/  logs/  archive/
├── history/     config/{common,symbols,symbol_groups,time,history_sync}.yaml
│                bases/{ticks,bars,ecn}/  datafeed/<name>/logs/  gateway/<name>/<cfg>/logs/  logs/
├── access/      config/{server,servers,symbols,time}.yaml   bases/{news,performance}/  logs/
└── backup/      config/   snapshots/   logs/
```

**Do these three now (≈2 h), ignore the rest until M5:**
- **Code never writes inside the source tree.** All state under `$BROKER_HOME`.
- **One config dir per role**, loaded by role. This is the *only* thing that later lets one codebase run as 4 processes.
- **Daily-rotating structured logs** to `logs/yyyymmdd.log`.

---

## 4. Should we clusterise the codebase now? **No.**

Splitting into services now would give you **12 broken services instead of 1 broken monolith.** You cannot import a single module today; distributed tracing across services that don't run is pure cost.

**Do this instead — a modular monolith with *process roles*, which is exactly what MT5 is:** one codebase, one domain, **N entrypoints**. Add `broker/{trade,history,access,worker}.py`, each a `main()` that wires only its own slice. That's ~½ a day after M0, and it's the real precursor to clustering. Extract a service **only** when a module needs independent scaling or deployment — for you, in order: **gateway (LP) → datafeed → history → access**. Trade stays last.

**Your stream list, triaged for "make it run":**

| Now (M0–M5) | Parked | Never / out of scope |
|---|---|---|
| config plane (groups/symbols/holidays/managers) · DB single-schema · RMS margin+stopout · OMS order→deal→position · B-book internal fill · routing (SOR + orchestrator **wired**) · data feed (mock, tick_size-fixed) · admin API + first-admin bootstrap · hot cache reachable · docker+TLS+CI | A-book real gateway · matching engine/CLOB · ECN · cluster sync · certificates · ClickHouse cold path · swap worker · dealer UI · backoffice/KYC · coverage auto-hedge execution · pricing/spread module · journal/snapshot/backup | intelligence/ · reports/statements · FIX · gRPC · Theia UI · client terminal · load testing · white-label · payment gateways · Automations · news/mail |

---

## 5. Where to start — complete **ONE** thing 100%

> ### The Configuration Plane. Groups → Symbols → Managers → Accounts, end to end.

**Why this and nothing else:** it is the **only** stream with zero upstream dependencies, and **every other stream reads from it** — RMS needs groups (leverage, margin call/stop-out, free-margin mode), OMS needs symbols (contract size, tick size, margin rates, sessions), routing needs group symbol overrides, feeds need symbols, the API needs managers. It is also **MT5's actual core competency** ("Groups as rule engines") and the thing your reference corpus documents best — you have the real 44-field group and 121-field symbol schemas sitting in `mt5-format-structure/`. And right now it is at **0% runnable**: the YAML is read by nothing, the CLI is 8 stubs, and there are four conflicting DB schemas.

**Tasks, in order:**

| # | Task | Blocks |
|---|---|---|
| 1 | Fix the 9 import errors; **merge** the duplicate `DealModel`/`PositionModel`/`IOrderRepository`/`IDealRepository`/`IPositionRepository`/`OrderCancelled`/`OrderModified` (second def silently wins today). Add CI: `compileall` + `pytest --collect-only` + `ruff` + `mypy core/`. | everything |
| 2 | **One schema.** `db_models.py` = single source of truth. Delete `ops/docker/init.sql` + its compose mount. Delete `alembic/versions/migration.py` (no `revision`/`down_revision` → alembic can't build a graph). Autogenerate. **Margin level = PERCENT** (MT5: `MarginCall 50.00`, `MarginStopOut 30.00`) — today you compute ratio *and* percent against thresholds stored *both* ways. | DB |
| 3 | Pydantic config schemas mirroring the domain VOs; YAML loader that **fails loudly on unknown keys**. | seeding |
| 4 | Rewrite `default_groups.yaml` + `instruments.yaml` to match (`margin: MarginProfile`, `margin_rates: MarginRates`, `symbol_pattern` not `symbol_group`; drop `margins.initial_percent` which `Symbol` no longer has). | seeding |
| 5 | `Manager` entity + `Rights` bitmask (copy `ConfigManagers` from your export) + **first-admin bootstrap** the MT5 way: if no manager exists, create one, print the generated password to stdout **and** the log once, force change on first login. | admin API |
| 6 | Handlers: `CreateGroup` (fix), `CreateSymbol`, `CreateClient`, `CreateAccount`, `CreateManager`. | admin API |
| 7 | `cli seed` for real — idempotent upsert through repositories: groups, symbols, holidays, coverage account, first admin. | running |
| 8 | Admin REST CRUD: `/admin/{groups,symbols,accounts,clients,managers,holidays}`. | demo |
| 9 | Make `ConfigCache` reachable (needs the 8 undefined domain events + `IGroupRepository`) and load it at startup. | hot path |

**Definition of 100% — one command, verifiable:**

```bash
make docker-up && make migrate && make seed && make run
curl /admin/groups    → the 6 groups from YAML, with correct MT5 percent thresholds
curl /admin/symbols   → EURUSD/GBPUSD/USDJPY/XAUUSD/BTCUSD with MarginRates + sessions
curl /admin/accounts  → a real account, in a real group, with a manager who can log in
# restart → identical output (proves persistence, not just in-memory)
```

Then — and only then — M3 (risk maths correct) and M4 (an order actually executes end to end).

**Roughly 3–4 days to a 100%-complete configuration plane**, versus ~15 half-built streams. That is the difference between "we have 180 files" and "we have a system you can set up and run."
