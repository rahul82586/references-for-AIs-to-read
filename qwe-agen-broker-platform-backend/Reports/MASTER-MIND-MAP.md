# MASTER MIND MAP — Where You Are, Where You're Stuck, What To Set Up Now

**Scope:** get the system to *"set up and run"*. Explicitly out of scope: reporting, AI/intelligence, portfolio analytics, cluster HA, white-label, client terminal.
**Sources:** your repo (`references-for-AIs-to-read` @ `3a92031`), the MT5 Administrator + SDK corpora inside it, the live MT5 config export, and five open-source reference repos I cloned and inspected (`nautilus_trader`, `rabbittrix/ultra-low-latency-fx-etrading-platform`, `llc-993/matching-core`, `joaquinbejar/hft-clob-core`, `tfrmma/oms-order-management-system`).

---

## 0. The one decision that must be made before any more code

Your reference files describe **two different products**, and the codebase currently implements a hybrid of both, which is the root cause of most of the confusion in the logs.

| | **Path A — MT5-adjacent** | **Path B — MT5-replacement** |
|---|---|---|
| What it is | Real MT5 Trade/History/Access/Backup servers run the brokerage. You build the back-office, risk overlay, admin UI and bridges **on top of the MT5 Manager API**. | You build the trade server yourself. No MetaQuotes binaries. Your Python is the platform. |
| Who does Stages 1–2 | **MetaQuotes + your hosting.** You rent servers, run `mt5srvsetup.exe`, get admin login 1000. Not your code. | **You.** You must write the equivalent of trade/history/access/backup servers, cluster sync, certificates, storage engine. |
| Evidence in your files | `opencode_summery.md`: *"Use MT5 Manager API for the admin layer… Poll positions every 15-30s → Redis… Risk engine reads Redis → evaluates → `TradeRequestSend` for stop-outs."* Also `single_centroid_bridge_md_files/` (a bridge product), and the live `TCTrader-Live` export. | `latest_chat…md`: *"Build the Manager API (FastAPI Schemas & Routers)"*, pure `core/` domain, "Python → Rust hot-path swap". |
| What your code actually does | ❌ Nothing. `grep` finds **zero** MT5 connector code — no `httpx`, no Manager API client, no `IMT*` bindings. | 🟡 Domain models ~good; runtime broken (see §6). |
| Time to "runs" | **Weeks.** MT5 does the hard parts. | **Many months.** You own the matching engine, storage, cluster, certs. |
| Risk | Vendor lock-in, license cost, MetaQuotes approval | Enormous surface area; regulatory-grade correctness is on you |

**The trap you are in right now:** `api/routers/manager/*` exposes endpoints named `UserGet`, `PositionGet`, `OrderSend`, `Connect`, `Ping`, `Version` — **MT5 Manager API names** — but they call your *own* query handlers. It is a **mimicry** of the MT5 API, not a **client** of it. So you have paid the naming cost of Path A and the implementation cost of Path B, and gotten the runtime benefit of neither.

**My recommendation for your stated goal ("just set up and run"):**
> **Choose Path B for the codebase, but stop mimicking the MT5 Manager API surface.** Build your *own* admin API (`POST /admin/groups`, `POST /admin/accounts`) with your own names. Keep the MT5 **data model** (which is excellent and which you have already absorbed) but drop the MT5 **protocol cosplay** — it is costing you schemas, routers and confusion, and it will never satisfy a real MT5 client anyway.
>
> If instead you want something a real broker could *use* this quarter, choose **Path A** and the work becomes: an MT5 Manager API HTTP client (`infrastructure/gateways/mt5_manager_client.py`), a position poller → Redis, and a risk overlay. Your domain models then become the config/reporting layer, not the trade server.

Everything below assumes **Path B** (that's where your code is), and flags where Path A would differ.

---

## 1. THE MIND MAP

```
STAGE 1 — MT5 PLATFORM INSTALL & CLUSTER  ← MetaQuotes' work, NOT yours
│   1.1 System preparation (Windows Server, roles, swap, power, firewall ports)
│   1.2 License (.lic) + full installation  → mt5srvsetup.exe /install
│   1.3 Cluster topology: main trade(1) · access(2) · history(3) · backup(4)
│   1.4 Console commands  /start /stop /restart /console /install /info /config /config_main /gui /gui_main
│   1.5 Ports & profiles  441-444 (443 public)  or  1950-1953 (1950 access)
│   1.6 Fast deployment   Deploy_<ID>_<Name>.exe /install  → auto-configured server
│   └─ YOUR STATUS: N/A for Path B.  For Path A: 0% (no MT5 server provisioned in repo)
│
STAGE 2 — ADMIN / MANAGER CREDENTIALS & GUI
│   2.1 Auto-created admin  login "1000" + random password → shown at install end AND in /Logs
│   2.2 Forced password change on first connect
│   2.3 That password is ALSO the internal cluster auth password for every component
│   2.4 Auto-created groups  demo\demoforex-ID · managers\dealers-ID · managers\administrators-ID · real\real-ID
│   2.5 Manager rights bitmask (per-manager permissions)
│   2.6 Activate licenses → removes functional limits
│   └─ YOUR STATUS: 🟡 partial. `AccountType` enum has MANAGER/DEALER. `IManagerRepository` exists.
│      `ConfigManagers` real schema is in your export (9 managers × Rights[]).
│      ❌ MISSING: Manager entity, role/permission model, admin bootstrap ("first admin"),
│         CreateManagerHandler, admin login flow distinct from client login.
│
STAGE 3 — BROKERAGE CONFIGURATION (the real work, one by one)
│   3.1 SYMBOLS          real MT5 = 121 fields × 362 symbols   │ yours = 42 fields   │ 🟡 35%
│   3.2 GROUPS           real MT5 = 44 fields + Commissions(12+Tiers) + SymbolOverrides(65)
│                        yours = 19 fields + 8 VOs (MarginProfile, CommissionRule, SwapConfig,
│                        GroupSymbolOverride 12/65, RoutingRule 3, GroupPermissions 12)      │ 🟡 45%
│   3.3 ACCOUNT TYPES    real/demo/preliminary/coverage/contest/manager/dealer
│                        enum ✅ · Account entity ✅ · Client entity ✅
│                        ❌ CreateAccountHandler · CreateClientHandler · admin endpoints    │ 🟡 60% model / 0% API
│   3.4 MANAGERS/DEALERS ❌ not built                                                        │ 🔴 10%
│   3.5 DATA FEEDS       mock_feed ✅ (buggy) · lp_feed ❌ NotImplementedError
│                        real MT5: ConfigFeeders (4), MetaTrader5Feeder64.exe, as-service   │ 🔴 25%
│   3.6 GATEWAYS (LP)    ❌ infrastructure/gateways/ is an empty __init__.py
│                        real MT5: ConfigGateways (3) with Translates[], Symbols[], Groups[]│ 🔴 0%
│   3.7 HOLIDAYS/SESSIONS Holiday entity ✅ · repo ✅ · create_holiday cmd ✅ · TradingSession 🟡
│                        ❌ per-day SwapRate{Sun..Sat}, server Time/EOD schedule            │ 🟡 55%
│   3.8 SPREADS          ❌ no spread config/markup engine (real MT5 has a Spreads section) │ 🔴 10%
│   3.9 LEVERAGES        MarginProfile.leverage_default/max ✅ · ❌ no leverage table/tiers │ 🟡 50%
│   └─ 3.10 SEEDING      🔴 0% — **this is your Stage-3 blocker.** See §6.
│
STAGE 4 — ROUTING / A-BOOK / B-BOOK / MATCHING
│   4.1 ROUTING RULES    SmartOrderRouter ✅ (priority, wildcards, NOP 70/85/95)
│                        ❌ 100% force-close tier · ❌ client risk profile (TOXIC/PROFITABLE/RETAIL/PRO)
│                        real MT5: ConfigRouting with Request bitmask, Conditions[], Dealers[],
│                        Actions (delay ms/ticks, clear SLTP, reject, requote, confirm, cancel)│ 🟡 40%
│   4.2 A-BOOK (STP)     ExecutionOrchestrator._execute_a_book ✅ code · ❌ ILiquidityGateway has
│                        NO implementation · ❌ no FIX engine · ❌ never wired               │ 🔴 15%
│   4.3 B-BOOK           _execute_b_book ✅ code + coverage exposure update
│                        ❌ IMatchingEngine has NO implementation (`fill_internal` absent)   │ 🟡 35%
│   4.4 COVERAGE/HEDGE   CoverageAccount repo ✅ · model ✅ · ❌ no auto-hedge execution     │ 🟡 40%
│   4.5 IN-HOUSE ECN     _execute_in_house ✅ stub · ❌ no CLOB, no order book, no price-time
│                        real MT5 ECN: matching rules, Providers (MT5 = intra-cluster),
│                        non-aggregated Market Depth, limit activation timeout              │ 🔴 5%
│   4.6 DEALER WORKFLOW  DealerQueueService ✅ · dealer router ✅ · ❌ no requote/confirm UI │ 🟡 50%
│   └─ 4.7 WIRING        🔴 0% — `execution_subscriptions.py` is imported by NOTHING.
│
CROSS-CUTTING
│   X.1 DATABASE / HOT-COLD   4 competing schemas (§5) · ConfigCache built but unreachable  │ 🔴 20%
│   X.2 NETWORKING            FastAPI + WebSocket ✅ · ❌ no TLS, no gRPC, no FIX, no cluster│ 🟡 30%
│   X.3 CERTIFICATES          ❌ 0%. Real MT5: license-based or own-PFX client certs,
│                             trusted CA list, extended auth, SSL for web services         │ 🔴 0%
│   X.4 OPS / "CAN IT RUN"    docker-compose ✅ · Makefile ✅ · Dockerfile ❌ · CI ❌
│                             alembic chain broken ❌ · CLI is all stubs ❌ · seed ❌        │ 🔴 15%
│   X.5 SECURITY              Argon2 ✅ · 2FA ✅ · rate limit ✅ · IP whitelist ✅ · token
│                             blacklist ✅ · BUT hardcoded JWT secret + admin key ❌        │ 🟡 60%
│   X.6 TESTS                 10 modules · currently 10 collection errors (§6)             │ 🔴 broken
│   └─ X.7 OBSERVABILITY      structured logging ✅ · ❌ no metrics, no tracing, no health
│                             beyond /health, no journal (real MT5 has a Journal per config)│ 🔴 15%
```

---

## 2. STAGE 1 — MT5 install & cluster, from scratch, **with the actual commands**

You asked for this specifically. This is verbatim from `Single_MetaTrader5Administrator/Platform-Installation.md` and `Console-Setup.md` in your own repo.

### 2.1 Order of operations (MetaQuotes' prescribed sequence)

```
1. Rent servers per System-Requirements
2. System preparation  (System-Preparation.md)
3. Complete platform installation on the MAIN server   → mt5srvsetup.exe, "Full installation"
4. First connection + necessary actions                → admin login 1000, change password, activate licenses
5. Install additional BACKUP servers                   (mandatory — trade/history servers make no backups)
6. Install additional ACCESS servers                   (all client connections go through access servers only)
7. Install additional TRADE servers                    (scale-out)
8. (optional) Install a free DEVELOPER platform for API work
```

### 2.2 System preparation checklist

- Disable unneeded Windows server roles; remove unneeded programs; configure Windows Update
- **Disable time synchronization** (the platform syncs its own time from the main server)
- Configure network connections; **disable sounds**; power plan → *maximum performance*
- Visual effects → *adjust for best performance*; **page file: initial size = maximum size**
- Startup/recovery → disable "time to display list of operating systems", write debugging info = *None*
- Recycle Bin → *remove files immediately*
- Configure antivirus exclusions; configure remote access; run the Server Configurator

### 2.3 Firewall ports, per component (from the docs' tables)

| Component | Outbound | Inbound |
|---|---|---|
| **Access server** | trade-server ports; history-server port; **443** → `updates.metaquotes.net` | its own listen port (clients connect here) |
| **Trade server** | **25** (report mail), **37** (TIME sync, main only), **123** (NTP, main only), main-server port, history-server port, gateway ports, **443** | its own port (main: all components; secondary: access servers) |
| **History server** | **443**, main-server port, data-feed ports (MT4Feeder 443, TCNewsFeeder FTP 20/21, DJPrimeTass 20000) | its own port + inbound data-feed ports |
| **Backup server** | main-server port, backed-up server's port, history port, gateway ports, **443**, access-server ports (for auto-failover monitoring) | — |

Port **profiles**: default `441–444` with **443 = public access server**; alternative profile `1950–1953` with **1950 = access server**. Full installation is **refused** if any port in the chosen profile is busy on *any* interface — then install components one by one.

### 2.4 Console commands (every server `.exe` supports these)

```bat
:: common — all servers
mt5access.exe /start | /stop | /restart | /console
mt5trade64.exe /install [/name:svc /display:"Access server" /description:"..."]
mt5trade64.exe /uninstall [/name:svc]
mt5trade64.exe /info          :: ID, own address, main server address, bindings

:: re-configure ANY server EXCEPT the main trade server
mt5access64.exe /config /main:192.168.0.1:440 /own:192.168.0.1:443 /id:3 /password:3jdaLjsQ
    /main:ip:port | /main_trade:ip:port   :: for trade servers vs other servers
    /own:ip:port  /history:ip:port  /id:N  /password:pw
    :: multiple addresses allowed: /main:192.168.0.1:440,[2a00:1987:1:30::2a]:440

:: MAIN trade server only — separate command
mt5trade64.exe /config_main /main:ip:port /access:ip:port /history:ip:port /backup:ip:port /password:pw
    :: auto-assigns internal IDs:  1=trade  2=access  3=history  4=backup

:: graphical config
mt5access64.exe /gui           :: secondary servers
mt5trade64.exe  /gui_main      :: MAIN server — using /gui on the main demotes it to secondary!

:: NUMA pinning
mt5trade64.exe /modify /numa_node:X      :: stop server first, then start
```

### 2.5 Fast deployment (the way to add servers 2..N)

```
1. In Administrator → Network → Add: set Type, Name, ID, Password (7–15 chars),
   Outgoing / Listen / Public addresses
2. Context menu → "Deploy..." → save  Deploy_<ID>_<ServerName>.exe
3. Copy to target machine, run:
       D:\MetaTrader 5 Platform\Backup History\Deploy_5_Backup_Server.exe /install
4. Result log written to  Deploy_<ID>_<ServerName>.txt
5. Restart the MAIN trade server — only then does the new server activate
```
Extra switches: `/nochecks` (skip connectivity verification), `/nogui` (no UAC prompt), `/main:ip:port`, `/history:ip:port`, `/name:`, `/display:`, `/desc:`.
Deploying a **trade server auto-creates a manager account** — credentials land in `/Logs` as:
`default manager with login '1000' and password 'lfd5fircvs' added`

### 2.6 Cluster connection order (matters when you reimplement this)

LAN is preferred. Resolution sequence:
1. Are both servers' **outgoing** addresses in `10.*`, `172.16–31.*` or `192.168.*` **with the same first three octets**? → connect via the target's local **listen** addresses.
2. If listen is `0.0.0.0:port` → address becomes `[outgoing address]:[listening port]`.
3. Else → iterate the target's **public addresses in listed order** (domain names resolve all IPs, **IPv6 preferred**).

### 2.7 What Stage 1 means for *you*

**Path B:** you do not install MT5. But you do owe yourself the *equivalents*, and you have almost none of them:

| MT5 concept | Your equivalent | Status |
|---|---|---|
| Main trade server | `api/main.py` + application services | 🔴 cannot import |
| Access server (client connections, caching, anti-DDoS) | FastAPI + WebSocket + rate limiter + IP whitelist | 🟡 exists, no TLS |
| History server (quotes, news, ticks, updates) | ClickHouse + `tick_persistence_worker` + `bar_aggregator` | 🟡 code exists, unreachable |
| Backup server (real-time critical + hourly rest) | ❌ nothing. No WAL, no snapshot, no PITR, no `journal` | 🔴 0% |
| `/config`, `/info`, `/install` console | `cli/main.py` — **every command is a stub with `# Implementation will be added`** | 🔴 0% |
| Cluster sync + IDs + bindings | `infrastructure/cluster/` = empty `__init__.py` | 🔴 0% |
| Fast deployment | `ops/docker/docker-compose.dev.yml` (**infra only — no app service!**) | 🟡 30% |

> ⚠️ **`docker-compose.dev.yml` has no `api` service.** It starts Postgres, Redis, ClickHouse, Kafka, Zookeeper, Adminer — and nothing of yours. There is **no Dockerfile** in the repo. So "run the system" currently has no path at all, even once imports are fixed. Compare nautilus_trader: `.docker/DockerfileUbuntu` + `docker-compose.yml` + `entrypoint.sh` + a Makefile with `install`/`build`/`pytest`/`pre-flight`.

---

## 3. STAGE 2 — Admin & manager credentials

### 3.1 How MT5 does it (facts from your corpus)

- **One administrator, login `1000`, random password**, created automatically during installation. Shown on the final installer screen **and** written to the main trade server's `/Logs` folder. Lose it → you cannot connect.
- **Forced password change** on first connect.
- That same password is used for **internal authentication between all cluster components** — change it per-server on the *Common → Password* tab if you must.
- **Auto-created groups on each new trade server** (ID = the server's internal ID): `demo\demoforex-ID`, `managers\dealers-ID`, `managers\administrators-ID`, `real\real-ID`. These are only created **after you specify the account range** for that server.
- A manager can **only administer accounts on the trade server where its own account lives**. Connecting to the main server does *not* let you create accounts on a secondary trade server.
- Restarting the main trade server is what materialises the new admin account + groups.
- **Extended authentication / certificates:** client & manager certificates can be generated from the **MetaQuotes license**, from **your own PFX** (must contain a private key; its CA must be added to the *Trusted Authorities* list, `.cer`/`.crt`), or **disabled** (then you must issue certificates manually, e.g. on an e-token, and import them per-account via *Accounts → Security → Import*). Until a certificate is **confirmed**, a manager/admin terminal cannot connect at all, and a client terminal connects **investor-only, no trading**. Certificate files live in `/terminal data folder/profiles/<server>/certificates/`.

Your live export confirms the shape: `ConfigManagers` has 9 entries, each with `Login`, `Name`, `Mailbox`, `Server`, and a **`Rights[]` bitmask array**.

### 3.2 Your status

| Piece | Status |
|---|---|
| `AccountType` enum incl. `MANAGER`, `DEALER` | ✅ |
| `IManagerRepository` port | ✅ (defined in `core/ports/interfaces.py:528`) |
| `api/routers/admin/` + `api/auth/admin_dependencies.py` | 🟡 exists but keyed on a **hardcoded static API key** (`ADMIN_SECRET_KEY_12345`), not on manager identity/roles |
| `Manager` **entity** with rights bitmask | ❌ does not exist |
| Role/permission model (admin vs dealer vs manager vs read-only) | ❌ enum only |
| **First-admin bootstrap** (the "login 1000" moment) | ❌ nothing |
| `CreateManagerHandler` / `CreateAccountHandler` / `CreateClientHandler` | ❌ none exist. Only `CreateGroupHandler`, `CreateOrder`, `CreateHoliday`, `RecordDeal`, `ModifyOrder`, `ModifyDeal`, `CancelOrder`, `ClosePosition`, `BalanceOperation` |
| Client login (`api/routers/auth.py`) vs **manager** login | ❌ not separated |
| Certificate / extended auth | ❌ 0% |

**Verdict: Stage 2 is ~15%.** You can authenticate *a client* with JWT. You cannot create a manager, cannot express dealer-vs-admin rights, and cannot bootstrap the first administrator. **Without admin bootstrap you cannot create groups or accounts, so Stage 3 is unreachable too.** This is your second-biggest structural gap after Stage 3's seeding problem.

---

## 4. STAGE 3 & 4 — configuration and routing: what exists, what's missing

### 4.1 Stage 3 field-coverage against the *real* MT5 export

I decoded your UTF-16 export and counted fields. This is the objective gap:

| Entity | Real MT5 (`TCTrader-Live`) | Your Python | Coverage | Highest-value missing fields |
|---|---|---|---|---|
| **Symbol** | **121** fields × 362 symbols | **42** | 35% | `CurrencyProfit`, `CurrencyMargin` (+digits each) — you have base/quote only; `SwapRate{Sunday..Saturday}`; `IECheckMode/IETimeout/IESlipProfit/IESlipLosing/IEVolumeMax`; `REFlags/RETimeout`; `QuotesTimeout`; `FillFlags/ExpirFlags/OrderFlags` (you have some); `Filter{Soft,Hard,Discard,SpreadMax,SpreadMin,Gap,GapTicks}`; `VolumeMinExt/MaxExt/StepExt/LimitExt` (integer-scaled); `MarginHedged/MarginLiquidity/MarginFlags/MarginCurrency`; `PriceLimitMax/Min`, `PriceSettle`, `AccruedInterest`, `Splice*`; `ISIN/CFI/Sector/Industry/Country/Basis` |
| **Group** | **44** fields | **19** + 8 VOs | 45% | `PermissionsFlags`, `AuthMode/AuthPasswordMin/AuthOTPMode`, `ReportsMode/Flags/Email`, `MailMode`, `TradeTransferMode`, `TradeInterestrate`, `TradeVirtualCredit`, `MarginFlags`, `MarginFreeProfitMode`, `DemoLeverage/DemoDeposit/DemoTradesClean`, `LimitHistory/LimitPositionsVolume`, `CurrencyDigits`, `Company*` (6 white-label fields), `NewsCategory/NewsLangs` |
| **Group→Symbol override** | **65** fields | **12** | 18% | the whole `MarginMaintenance*` half, `MarginInitial{Buy,Sell}{Limit,Stop,StopLimit}`, `StopsLevel/FreezeLevel`, `SpreadDiffBalance`, `Swap3Day/SwapFlags/SwapYearDay/SwapRate*`, `REFlags/RETimeout`, `IE*`, `PermissionsFlags/PermissionsBookdepth`, `FillFlags/ExpirFlags/OrderFlags`, `VolumeStep(Ext)` |
| **Commission** | **12** fields + `Tiers[]` | **9** flat (`CommissionRule`) + `CommissionTier(3)` | 50% | `Mode`, `RangeMode`, `ChargeMode`, `TurnoverCurrency`, `EntryMode`, `ActionMode`, `ProfitMode`, `ReasonMode`; tier fields are `volume_min/volume_max/rate` but tests expect `volume_from` → **API drift, tests fail** |
| **Routing rule** | `Name`, `Mode`, `Request` (bitmask, e.g. `33554431`), `Type`, `Flags`, `Action` (e.g. `1001`, `1005`), `ActionValue{Int,UInt,Float,String}`, `Conditions[]`, `Dealers[]` | `RoutingRule(3)`: `default_mode`, `a_book_threshold_lots`, `lp_priority` + a separate `execution/models.RoutingRule` with priority/filters | 25% | the **action taxonomy** and **condition taxonomy** (see §4.3) |
| **Gateway (LP)** | `Name`, `Module`, `GatewayServer`, `GatewayLogin/Password`, `TradingServer/Login/Password`, `Enable`, `Flags`, `ID`, `Gateway`, `TimeoutReconnect/Sleep`, `AttemptsSleep`, `State{}`, `Params[]`, `Symbols[]`, `Groups[]`, **`Translates[]`** | ❌ **empty package** | 0% | everything |
| **Data feeder** | `Feeder`, `Module`, `GatewayServer`, `GatewayLogin/Password`, `FeedServer`, `FeedLogin/Password`, `Enable`, `Mode`, `TimeoutReconnect`, … | `mock_feed.py` ✅ / `lp_feed.py` ❌ `NotImplementedError` | 20% | the real connector |
| **Firewall** | `IPFrom`, `IPTo`, `Action` (block/permit/always-permit), **order matters — last matching instruction wins** | `ip_whitelist.py` (allow-list only) | 40% | block ranges, ordered evaluation, "always permit" |

### 4.2 Stage 3's real blocker: **there is no way to get configuration into the system**

This is the single most important finding for your goal. Four independent facts:

1. **`config/*.yaml` is never read by anything.** `grep -rn "yaml" --include=*.py .` returns exactly **one hit**: `cli/main.py:20`, a string *default value* for a `--config` option in a command whose body is `# Implementation will be added in subsequent steps`. There is no YAML loader, no schema, no validator.
2. **`cli/main.py` is 100% stubs.** `start`, `migrate`, `seed`, `backtest`, `sync`, `export`, `import_data`, `status` — every one prints a Rich-coloured line and returns. `make seed` runs `python -m cli.main seed` → prints "Seeding database…" → does nothing.
3. **The YAML doesn't match the domain model anyway.** `default_groups.yaml` uses `margin_call_level: 0.8` (flat) but `Group` takes `margin: MarginProfile`; `commissions[].symbol_group` but `CommissionRule.symbol_pattern`; `swaps.calculation_mode` but `SwapConfiguration.calculation_mode` ✅; `virtual_balance`, `contest_duration_days`, `lp_priority` — some exist, some don't. `instruments.yaml` uses `margins.initial_percent / maintenance_percent`, which the `Symbol` entity **no longer has** (replaced by the 16-field `MarginRates`). So even a written loader would fail immediately.
4. **There are four mutually incompatible `groups` schemas** (see §5).

> **Consequence:** Stage 3 is not "40% done". It is **0% runnable**. The domain models are 40–60% field-complete, but there is no path from *a configuration file or an admin request* → *a persisted Group/Symbol/Account* → *a running server that uses it*. That path is exactly what "set up and run" means, and it does not exist.

**What Stage 3 needs, concretely, in dependency order:**

```
S3.1  Single source of truth for schema      → make db_models.py THE schema; delete/regenerate init.sql;
                                              fix alembic chain; regenerate migration from models
S3.2  Pydantic config schemas                → config/schemas.py mirroring the domain VOs exactly
S3.3  YAML loader + validator                → infrastructure/config/loader.py; fail loudly on unknown keys
S3.4  Rewrite the 2 YAML files               → to match MarginProfile / MarginRates / CommissionRule
S3.5  CreateClientHandler + CreateAccountHandler + CreateGroupHandler(fix) + CreateSymbolHandler
S3.6  Manager entity + rights + first-admin bootstrap   (Stage 2, but required here)
S3.7  cli/main.py: implement `seed` for real → idempotent upsert of groups, symbols, holidays,
                                              coverage account, first admin
S3.8  Admin REST endpoints                   → POST/GET/PATCH /admin/{groups,symbols,accounts,clients,managers,holidays}
S3.9  ConfigCache reachable                  → needs the 8 missing domain events + IGroupRepository
```

### 4.3 Stage 4 — routing / A-book / B-book / matching

**MT5's routing model, which you should copy (from `Routing/Actions-and-Conditions.md` + your live export):**

- Rules execute **top-down**; first match wins; a rule may **delay** then continue down the table.
- **Any change to the routing table re-queues every in-flight request to the top.**
- Conditions are **AND**-ed within a rule and must not contradict (`real*` AND `demo*` matches nothing).
- **Actions:** `Delay in milliseconds` · `Delay in ticks` (max 60) · `Clear TP` · `Clear SL` · `Clear SLTP` · `Process to dealers` · `Process to online dealers` · `Reject` (with a ≤31-char client-visible reason) · `Requote` · `Confirm by request price` · `Confirm by market price` · `Cancel order` (only on pending activation/modification). Plus *"skip this rule if no dealers online"*.
- **Request-type conditions (24):** price, request execution, instant/market/exchange execution, pending order, SL&TP modification, order modification/removal, Close By, order activation, Stop-Limit activation, SL activation, TP activation, **stop-out order**, **stop-out position**, order expiration, and 9 dealer-initiated variants.
- **Order-type conditions (8):** Buy, Sell, Buy/Sell Limit, Buy/Sell Stop, Buy/Sell Stop Limit. (For SL/TP/stop-out/modification, the order-type condition refers to the **position's** direction, not the closing direction.)
- **Additional conditions:** date/time, symbols (masks with `*` and `!`), request volume, **deviation from market in points** (buy: `ask − request price`; sell: `request price − bid`; positive = client-favourable, negative = broker-favourable), time, day of week, request comment (`=`, `>`/`>=` substring, `<`/`<=` reverse substring), **placed by expert**, **placed by signal**, **dealer processed request**, **dealer placed request**.
- **Dealers tab:** only *gateways* or managers with the **Dealing** permission; a special **`ECN`** entry forwards to ECN matching. **Multiple gateways per rule** → priority resolved from the account's **external accounts** list; a gateway that refuses is removed from the list and the request passes to the next; if all refuse → reject with journal entry `request rejected, due all assigned dealers returned request in queue (…)`.
- Your live export's two real rules: `dealer` (`Mode 1`, `Request 33554431`, `Type 255`, `Action 1001`, dealer = *"MetaTrader 5 Gateway clone"*) and `Auto Execution` (`Action 1005`, dealer = *"First Admin"*).

**MT5's ECN (in-house matching) model** — this is your Stage 4.5 reference:
- Matching only for symbols flagged **ECN**; requests reach ECN via a routing rule with action *Process to dealers* → dealer **`ECN`**.
- Per-ECN-symbol **matching rules**: order direction (Buy/Sell), date/time, time, day of week, client login, client group, volume.
- **Providers tab**: intra-cluster clients = select **`MT5`**; external LPs = select gateway configs. All providers in one rule have **equal priority**; order in the list is irrelevant.
- Matching triggers on **every Market Depth change** (gateway prices, new order, symbol settings change).
- Uses the **non-aggregated** Market Depth (includes hidden levels, **minimum-spread settings do not apply**).
- Limit-order/TP **activation**: mode `Limit` or `Market`, plus a **timeout in ms** (default 5 s) after which the ECN order is cancelled and re-sent on re-activation. **Stop Losses are always market orders** and are unaffected by this setting.
- Limit orders can be kept **outside** ECN until activation, by placing a higher-priority routing rule above the general ECN rule.

**Your status vs that:**

| Piece | Code | Wired | Runnable |
|---|---|---|---|
| `SmartOrderRouter` (priority, wildcards, NOP 70/85/95) | ✅ | via orchestrator only | ❌ |
| NOP **100% force-close** tier | ❌ (spec'd in `opencode_summery.md`, never implemented) | — | — |
| Client risk profile (TOXIC/PROFITABLE/RETAIL/PRO) → A/B decision | ❌ | — | — |
| MT5-style **action taxonomy** (delay, clear SLTP, reject-with-reason, requote, confirm@request/market, cancel) | ❌ only `A_BOOK / B_BOOK / IN_HOUSE / DEALER / REJECT` | — | — |
| MT5-style **condition taxonomy** (deviation-from-market in points, placed-by-expert, day-of-week, comment masks) | ❌ only group/symbol/volume filters | — | — |
| `ExecutionOrchestrator` (A-book / B-book / dealer / reject) | ✅ well-shaped | 🔴 **`execution_subscriptions.py` is imported by NOTHING** | ❌ |
| `ILiquidityGateway` implementation (FIX/REST to an LP) | ❌ none | — | — |
| `IMatchingEngine` implementation (`fill_internal`) | ❌ none — `infrastructure/engines/` is an empty `__init__.py` | — | — |
| Order book / CLOB / price-time priority | ❌ none. `OrderBook` + `BookLevel` **models** exist in `market_data/models.py`, and a `BookUpdated` event exists, but there is no book implementation | — | — |
| Coverage account auto-hedge execution | 🟡 exposure is *updated* by `_execute_b_book`; nothing *hedges* | ❌ | ❌ |
| `DealerQueueService` + dealer endpoints | ✅ | 🟡 | ❌ |
| LP feed | ❌ `NotImplementedError` ×2 | — | — |

**Verdict: Stage 4 is ~20%.** The decision logic (SOR) is decent. Everything that *acts* on the decision — gateway, matching engine, hedge execution — is absent, and the orchestrator that would coordinate them is never started.

---

## 5. CROSS-CUTTING: database, hot/cold paths, file types, networking, certificates

### 5.1 How MT5 actually stores things (from `code files/9 …md` + the SDK corpus)

```
Trade server directory/
├── bases/
│   ├── daily/daily_*.dat     ← binary snapshots of account states
│   ├── groups.dat            ← group config, held IN RAM
│   ├── symbols.dat           ← symbol config, held IN RAM
│   └── holidays.dat          ← holiday config, held IN RAM
├── settings/<manager_login>/ ← per-manager arbitrary files (ini, cfg, dat, json, sqlite, xml)
│                                 accessed via SettingGet / SettingSet
├── configs/access.ini        ← firewall rules (delete this file + restart = reset firewall
│                                 if you lock yourself out)
├── config/                   ← server config; /config and /config_main rewrite it
├── Logs/                     ← journal; first admin password appears here
└── history/<symbol>/ticks.dat
```

Key patterns: **all config loaded into RAM at startup** (`GroupNext(pos, group)` iterates memory, not a DB); **custom binary serialisation** (`#pragma pack(push,1)`, one-byte alignment); **event sinks** (`IMTConGroupSink::OnGroupUpdate`) notify every connected manager; **per-trade-server isolation** of the client DB; **cluster sync by checksum** (`IMTConHistorySync`, `MODE_REPLACE` / `MODE_MERGE`); **backup = real-time for critical/changing data (client & trade DBs, configs, gateway executions) + hourly for the rest (mail, news, files, binaries, gateways, feeds, plugins)**, with daily file copies, configurable retention, and an opt-in tick backup that will eat your disk if you leave it on.

Your own analysis file reached the right conclusion: **copying MT5's `.dat` approach would be a regression** for Python. The correct target is **hybrid: PostgreSQL as source of truth + in-memory cache for the hot path + Redis for the event bus + ClickHouse/Parquet for time-series**. That is exactly what nautilus_trader does (`persistence/src/backend/{parquet,feather,catalog,kmerge_batch}.rs` for cold, `event_store/src/backend/{memory,redb}.rs` for the journal, Postgres+Redis in compose).

### 5.2 Your hot/cold implementation status

| Layer | Intended | Actual |
|---|---|---|
| **Hot config** (groups, symbols, holidays, accounts, positions) | `application/cache/config_cache.py` — in-RAM dicts, loaded at startup, invalidated via event bus | ✅ written (16 KB). 🔴 **unreachable**: `api/main.py` can't import (`GroupCreated` missing, `get_di_container` missing, `IGroupRepository` missing) |
| **Hot market data** | Redis (`redis_market_data.py`) + `MarketDataEngine` in RAM | 🟡 code exists; `Tick`/`OrderBook`/`Bar` models are good; unreachable via the same import chain |
| **Transactional truth** | PostgreSQL via SQLAlchemy async + repositories + mappers | 🔴 `db_models.py` can't import (`BigInteger`); `DealModel`/`PositionModel` defined twice with duplicate `__tablename__` |
| **Event journal** | Redis pub/sub (`redis_event_bus.py`) + `event_store.py` + `DomainEventModel` table | 🟡 exists; `event_store.py` is 4 KB and thin; **no WAL/snapshot/replay** — so no crash recovery and no backup story at all |
| **Cold time-series** | ClickHouse (`clickhouse_client.py`, tick + bar repositories, `clickhouse_init.sql`) | 🟡 code exists; never exercised (`test_clickhouse_persistence` fails on a missing httpx-dependent API test) |
| **Cold archive / statements** | — | ❌ nothing (out of scope per your instruction — fine) |

### 5.3 🔴 Four competing definitions of the same schema

This is why "just run the migration" isn't a thing you can do yet.

| Source | `groups` primary key | margin-call column | units | extra fields |
|---|---|---|---|---|
| `ops/docker/init.sql` (runs on container start) | `id UUID DEFAULT uuid_generate_v4()` | `margin_call_level DECIMAL(5,4) DEFAULT 0.8000` | **fraction** | `permissions/commissions/swaps/routing` as **JSONB**, `contest_duration_days`, `virtual_balance` |
| `infrastructure/persistence/db_models.py` (`GroupModel`) | **`name = Column(String(128), primary_key=True)`** | `margin_call_level Numeric(6,2) DEFAULT 60` | **percent** | flat `commission_type/value/currency`, `execution_mode`, `position_mode`, `allow_hedging`, `allow_scalping`, `slippage_points`, `permissions_json Text`, `swap_*` |
| `alembic/versions/001_initial_schema.py` | (its own variant) | `Numeric(6,2) DEFAULT 60`, `stop_out_level DEFAULT 30` | **percent** | `commission_value`, `swap_long/short` |
| `core/domains/accounts/group.py` (domain) | `id: str` | `margin: MarginProfile(margin_call_level=Decimal('0.8'))` | **fraction** | nested VOs; `symbol_overrides`, `routing`, `swaps`, `trade_flags`, `news_mode` |

Plus a **fifth**: `config/groups/default_groups.yaml` — `margin_call_level: 0.8` (fraction), flat, with `virtual_balance` / `contest_duration_days` / `lp_priority` that no model has.

So: **UUID vs name-as-PK**, **0.8 vs 60**, **JSONB vs flat columns**, **nested VO vs flat**. Postgres gets created by `init.sql` with the UUID/fraction schema; SQLAlchemy then queries it expecting name-PK/percent columns. Every read and write fails. `alembic upgrade head` can't run either, because `alembic/versions/migration.py` has **no `revision` / `down_revision` variables** (only prose in the docstring: `Revises: previous_revision`, `Create Date: 2026-01-XX`) — Alembic cannot build a revision graph.

**Fix (do this once, decisively):** `db_models.py` becomes the single source of truth → `rm ops/docker/init.sql` (let Alembic create the schema; Postgres container starts empty) → delete `migration.py`, run `alembic revision --autogenerate -m "mt5 parity"` against the models → hand-edit the generated migration for `Numeric` precision → `alembic upgrade head` → then write the YAML loader against the *domain* model and let the seeder go through repositories, never through raw SQL.

### 5.4 Networking

| Need | MT5 | You |
|---|---|---|
| Client-facing edge | Access servers, port 443, IPv4+IPv6, public/listen/outgoing address triples, load distribution by observed access-server load, anti-DDoS server | FastAPI + `api/websockets/*` ✅; no TLS, no address model, no anti-DDoS beyond a rate limiter |
| Internal cluster | ID + 7–15 char internal password per server, LAN-preferred connection order, IPv6 preference, `/config` `/config_main` | ❌ `infrastructure/cluster/` empty; `settings.yaml` says `cluster.enabled: true, node_discovery: grpc` — **`api/grpc/` is an empty `__init__.py`** |
| LP connectivity | Gateways: `MetaTrader5Gateway64.exe`, `FTMT5Gateway64.exe`, `GatewayServer 127.0.0.1:1638x`, `TradingServer ip:port`, reconnect/sleep/attempts, `Translates[]` symbol+price mapping, `Symbols[]`/`Groups[]` scoping, weekend operation mode | ❌ `infrastructure/gateways/` empty; `api/fix/` empty; `lp_feed.py` `NotImplementedError` |
| Institutional B2B | FIX via gateway | ❌ 0% |
| Web/API | Web API (REST, text protocol), `/api/callback/automation?login=…`, allowed-callback + allowed-IP lists, SSL cert bound to the access server's public domain | 🟡 you have REST + webhooks package (empty) |

Reference: **rabbittrix** splits this exactly the way you should — `fx-md` (feed/quote), `fx-lp` (lp/quote aggregation), `fx-gateway` (api/handlers/openapi_proxy/proxy_types), `fx-router` (router/venue), `fx-liquidity-graph` (graph/planner/types), `fx-proto` (protobuf). **hft-clob-core** splits it as `wire` / `gateway` / `marketdata` / `matching` / `engine` / `risk` / `domain` / `clob-client`.

### 5.5 Certificates — 0%, and here's the whole picture you need

MT5 uses certificates in **three distinct places**, and you have none of them:

1. **Cluster/internal** — servers authenticate each other by *ID + internal password* and by *outgoing-IP match* ("if no outbound address is specified, the server connects without IP authentication"). Not X.509.
2. **Client & manager extended authentication** — `Security → Certificates`: generate from **license** (default; MetaQuotes' cert in your `.lic` is the CA for all client certs), from **your own PFX** (must contain the private key; its issuer must be added to **Trusted Authorities** via `.cer`/`.crt`), or **disabled** (manual issuance, e.g. e-token, then import per account). Client must place the cert in the terminal's `/certificates` folder, the OS store, or an e-token. Unconfirmed cert → manager/admin **cannot connect**; client connects **investor-only**. Reset → cert invalidated, regenerated on next connect. Group-level `AuthMode` / `AuthOTPMode` / `AuthPasswordMin` govern it (your export: `AuthMode 0`, `AuthPasswordMin 8`, `AuthOTPMode 0`).
3. **Web services / TLS** — bind the access server's public address to a **domain**, upload an **SSL certificate** for it (Let's Encrypt or self-signed; the docs' `curl -k` example shows self-signed), then whitelist allowed callback URLs **and** the source IPs permitted to call them.

**What you actually need for "runs", in priority order:** (a) TLS termination for the API — put nginx/Traefik or Caddy in front in compose and get Let's Encrypt; do **not** hand-roll X.509. (b) The hardcoded `SECRET_KEY` → env var with a hard startup failure if unset. (c) Manager identity + rights (Stage 2) — this is what certificates would eventually protect, and you can't skip it. (d) Client extended auth / OTP — **defer**; `AuthOTPMode 0` in your own live export means the reference broker isn't using it either.

### 5.6 Ops — the "can it run" gap

| Artefact | Status |
|---|---|
| `ops/docker/docker-compose.dev.yml` | 🟡 Postgres 15, Redis 7, ClickHouse 23.8, Kafka+Zookeeper, Adminer. **No application service.** Kafka/Zookeeper are dead weight for your goal — remove them. `init.sql` mount is actively harmful (§5.3). |
| `Dockerfile` | ❌ **does not exist** |
| `.env.example` | ❌ does not exist (README says `cp .env.example .env`) |
| `alembic upgrade head` | ❌ broken revision graph + schema conflict |
| `cli/main.py` (`start`, `seed`, `status`, `migrate`, `export`, `import`, `sync`, `backtest`) | ❌ all 8 commands are stubs |
| `Makefile` | 🟡 good targets (`setup-dev`, `docker-up`, `migrate`, `seed`, `run`, `test`, `lint`, `type-check`) but `setup-dev` chains four things that each fail; `test-e2e` points at a non-existent `tests/e2e/`; `--cov=broker-platform` is not an importable module name |
| CI (`.github/workflows/`) | ❌ none |
| Health/readiness | 🟡 `/health` returns a static dict; no DB/Redis dependency check |
| Metrics / tracing / journal | ❌ none (MT5 has a per-section **Journal**; nautilus has `audit_log.rs`, `trade_log.rs`; matching-core has `core/journal.rs` + `core/snapshot.rs`) |

Compare **nautilus_trader's** run story: `.docker/DockerfileUbuntu` + `docker-compose.yml` (postgres/pgadmin/redis, `no-new-privileges`, `127.0.0.1`-bound ports) + `entrypoint.sh` that sets `PYO3_PYTHON` and prints the exact next commands, + a Makefile with `sync / install / install-debug / build / build-wheel / py-stubs / check-generated-drift / clean / format / pre-commit / check-code / ruff / clippy / pre-flight / security-audit / docs`, + `.pre-commit-config.yaml`, `.gitleaks.toml`, `deny.toml`, `osv-scanner.toml`, `.gitattributes`, `AGENTS.md`/`CLAUDE.md`.
Compare **hft-clob-core**: `docker/Dockerfile` + `docker/docker-compose.yml`, Makefile with **per-crate test targets** (`test-domain`, `test-wire`, `test-matching`, `test-risk`, `test-engine`, `test-gateway`, `test-marketdata`), `test-stress-stp`, `test-proptest`, and a `BENCH.md` with an explicit tail-latency methodology (HDR histogram, 1 ns resolution, p50/p99/p99.9/p99.99/max, **no mean, no stddev**).

---

## 6. WHERE YOU ARE STUCK — the precise, ordered blocker chain

Each item blocks the next. This is your critical path.

```
B1  core/ports/interfaces.py:9 — `Any` not imported
      └─ NameError at class-body evaluation → EVERY module importing ports fails
         → all 10 test modules error at collection → nothing can be verified
B2  infrastructure/persistence/db_models.py:1 — `BigInteger` not imported (used ×5)
      └─ NameError → the whole persistence layer cannot be imported
B3  db_models.py — DealModel & PositionModel each defined TWICE, same __tablename__
      └─ SQLAlchemy InvalidRequestError: Table 'deals' is already defined
B4  core/events/domain_events.py — 8 events imported but never defined
      (GroupCreated/Updated/Deleted, SymbolCreated/Updated/Deleted, HolidayUpdated/Deleted)
      └─ ImportError in config_cache.py, create_group.py, api/main.py → API cannot start
B5  core/ports/interfaces.py — IGroupRepository never defined, imported by 6 modules
      └─ ImportError ×6
B6  api/di_providers.py — get_di_container not defined, imported by api/main.py
B7  group_repository.py — imports CommissionProfile / ExecutionProfile (renamed away)
B8  swap_worker.py — imports core.domains.oms.models (does not exist)
B9  6 more missing typing/datetime imports (record_deal, commission_service,
      execution_orchestrator, execution/router, ledger/engine, order_repository, position_repository)
      ─── after B1–B9: the code imports. Then: ───
B10 FOUR competing schemas (init.sql / db_models / alembic / domain) + broken alembic chain
      └─ no database can be created that the code can talk to
B11 No config loader, no seeder, cli is 8 stubs
      └─ even with a DB, there is nothing IN it: no groups, no symbols, no admin
B12 No Manager entity, no roles, no first-admin bootstrap
      └─ nothing can be created through the API either
B13 RiskEngine written against the pre-refactor Position API (.side/.average_price/.id)
      └─ AttributeError per position, swallowed → margin & PnL silently ZERO
B14 detect_margin_call / detect_stop_out read group.margin_call_level (it's group.margin.*)
      └─ AttributeError → risk_worker is dead code that throws
B15 margin level in two units (ratio 0.4 vs percent 40.0) against thresholds in two units
      (0.8/0.5 in code+YAML vs 60/30 in DB) — real MT5 uses percent (50/30)
      └─ stop-out either never fires or always fires
B16 Position(price_current=Price(Decimal('0'))) violates Price>0 → cannot construct with defaults
B17 liquidation_worker hardcodes conversion_rate = Decimal('1.0')
      └─ worst-loss-first sorts on unconverted PnL → closes the WRONG positions
B18 create_order prices market orders at Decimal('1.0')
      └─ margin understated (150× on JPY pairs)
B19 create_order commits margin INSIDE the lock, order OUTSIDE it, no UoW
      └─ any failure between the two strands client margin permanently
B20 UnitOfWork() → SqlOrderRepository() missing required session_factory → TypeError;
      and repos never receive the shared session → no atomicity at all
B21 execution_subscriptions.py imported by NOTHING → orders are never executed
B22 LiquidationWorker instantiated only in tests → stop-outs are never acted on
B23 ILiquidityGateway and IMatchingEngine have NO implementations
      └─ A-book has nowhere to go; B-book has nothing to fill
B24 No Dockerfile, no app service in compose, no .env.example
      └─ even a fixed codebase has no way to be started
```

**Also unresolved from the original audit (still open in this commit):**
- `mock_feed.py:65` quantises to `spread`, not `symbol.tick_size`
- `jwt_handler.py:12` hardcoded `SECRET_KEY`; `admin_dependencies.py:10` hardcoded admin key default — and `test_api.py:77` asserts against that default, cementing it
- `get_positions.py` computes PnL with **no currency conversion** *and* mixes `Decimal − Price`
- `get_conversion_rate` has **no cross-rate triangulation** (EURJPY→USD needs EURUSD; it tries only `JPYUSD` then `USDJPY`) and swallows all errors with `except Exception: pass`
- `select_positions_for_liquidation` returns **all** positions sorted, not "until margin recovers"
- `Group.calculate_commission` returns 0 or the wrong value (2 real test failures), and `return`-in-loop means **only the first matching rule ever applies** — MT5 stacks rules
- 6 tests are empty or assertion-free — including `test_cross_currency_pnl_in_margin_loop`, whose body is `pass`, which reports **PASSED**, and which the chat log cites as proof cross-currency PnL works
- 8 tests fail on constructor drift (`Symbol(margin_initial_percent=…)`, `TradingSession(start=…)`, `Group(margin_call_level=…, leverage_default=…)`, `CommissionTier(volume_from=…)`, `to_dict()["symbol_overrides_count"]`)
- duplicate class definitions in `interfaces.py` (×3), `domain_events.py` (×2), `di_providers.py` (×1) — **second definition silently wins**
- `core/domains/risk/engine.py` contains one **bare `\r`** at line ~214 (import-safe, but any byte-level patcher will corrupt the file)
- `intelligence/` = 8 empty packages; `infrastructure/{cluster,gateways,engines,notifications}/`, `api/{fix,grpc,client}/`, `core/domains/{backoffice,identity}/` = empty

---

## 7. THE MINIMUM VIABLE "SET UP AND RUN" — 6 milestones

This is the shortest path to *a server that starts, has configuration in it, and can take an order end to end*. Everything not listed is deliberately deferred.

### M0 — Make it import (½–1 day) · *unblocks everything*
Fix B1–B9. **Merge** (do not delete) the duplicate `DealModel`/`PositionModel`/`IOrderRepository`/`IDealRepository`/`IPositionRepository`/`OrderCancelled`/`OrderModified`/`get_cancel_order_handler` pairs — the second definition is currently shadowing the first, so decide which method set survives.
**Gate:** `python -c "import api.main, infrastructure.persistence.db_models"` exits 0.
**Then immediately add CI:** `compileall` + `pytest --collect-only` + `ruff` + `mypy core/`. Every one of B1–B9 is caught by one of these in under a second. This is the single highest-leverage hour in the whole plan.

### M1 — One schema, one migration (1 day) · *unblocks the database*
`db_models.py` = the single source of truth. Delete `ops/docker/init.sql` and its compose mount. Delete `alembic/versions/migration.py`; give `001_initial_schema.py` real ids or regenerate from scratch with `--autogenerate`; fix precision to `Numeric(20,8)`. **Decide the margin-level unit now: percent (MT5's convention).** Change `MarginProfile` defaults `0.8→80`, `0.5→50`; `settings.yaml` likewise; the five ratio call-sites likewise. Add one `Account.recompute_margin_level()` so the formula exists exactly once (fixes B10, B15).
**Gate:** `docker compose up -d postgres && alembic upgrade head` succeeds, and a test asserts an account at 40% margin level with 50/30 thresholds emits `MarginCallEntered`, and at 25% emits `StopOutEntered`.

### M2 — Configuration can enter the system (1–2 days) · *unblocks Stage 3*
Pydantic schemas mirroring the domain VOs → YAML loader that **fails loudly on unknown keys** → rewrite `default_groups.yaml` and `instruments.yaml` to match → implement `cli seed` for real (idempotent upsert through repositories: groups, symbols, holidays, coverage account, **first admin manager**) → `CreateClientHandler`, `CreateAccountHandler`, fix `CreateGroupHandler`, `CreateSymbolHandler` → admin REST endpoints (fixes B11, B12, and Stage 2).
Bootstrap the first admin the way MT5 does: if no manager exists, create one, **print the generated password to stdout and the log once**, force change on first login.
**Gate:** `make docker-up && make migrate && make seed && make run` → `GET /admin/groups` returns the 6 groups from YAML; `GET /admin/symbols` returns the instruments; `POST /admin/accounts` creates a real account.

### M3 — The risk path is real · ✅ **COMPLETE** (see `M3-REPORT.md`)

**Result: 154 passed / 12 failed → 210 passed / 0 failed.** MT5 format preserved: 362/362
symbols and 20/20 groups still re-export field-identically, now including all three symbol
currencies. Four proofs run in the gate: M1 losslessness, M3 currencies, M3 unit-of-work
atomicity, M3 risk maths (the four audit rows + MT5's own published worked examples).

Scope grew because the six listed items were mostly symptoms. The cause was that MT5's
`CurrencyProfit` and `CurrencyMargin` were mapped to `""` and discarded — M1's own fieldmap
comment named them as the root cause and left them unmapped. Deriving currencies from the
symbol *name* instead gets **109 right, 60 wrong and 193 unparseable** of the 362 reference
symbols, and the parser never even ran because `Symbol.base_currency` defaulted to `"USD"`.
There were **five** margin formulas, not two, and `RecordDealHandler` — the whole deal path —
raised `AttributeError` on every call (`account.login_id` at nine sites, `Position(id=, side=,
average_price=, opened_at=)`, and a call to `calculate_margin_required` on Symbol where it
lives on Position). No trade had ever been recorded end to end.

Two M3 items were left deliberately and are documented as gaps: the leverage **tier** rule
(no reference group configures tiers) and `Price.zero()` (made `price_current` Optional
instead). Everything else in the scope list is done, including the UnitOfWork, which was
unenterable (`TypeError`) and would not have shared a session anyway.

<details><summary>original scope</summary>

### M3 — The risk path is real (1–2 days) · *unblocks correctness*
Fix B13–B20. Rename to `action`/`price_open`/`position_id`; read `account.group.margin.*`; initialise `has_calculation_error = False` and **stop swallowing exceptions** (an unvaluable position must fail loudly, not zero out margin); use `account.effective_leverage()`; add `credit` to equity (MT5: `equity = balance + credit + profit` — `Account.update_equity` already does this, `RiskEngine` doesn't); add `Price.zero()` or make `price_current` `Optional`; call the real `get_conversion_rate` in the liquidation worker; fetch the live tick for market-order margin; put margin-reserve + order-persist inside a **working** `UnitOfWork` (pass the shared session into repositories); add cross-rate triangulation.
**Gate:** the four rows from `opencode_summery.md` as real assertions — EURUSD/USD `$10.00`, USDJPY/USD `~$6.67`, EURJPY/USD `~$6.67`, GBPAUD/USD `~$6.50` per pip per lot — plus `test_account_lock_prevents_double_spend` genuinely passing, plus the `pass`-bodied cross-currency test **filled in or deleted**.

</details>

### M4 — An order actually executes (2–3 days) · *unblocks Stage 4*
Implement **one** `IMatchingEngine` — B-book internal fill at current bid/ask with slippage and spread. That's it; no CLOB yet (matching-core's `orderbook/naive.rs` is the right first reference, ~1 file). Implement **one** `ILiquidityGateway` — a *stub* A-book that logs and simulates an LP fill, so the routing branch is exercised. **Wire `execution_subscriptions` and `LiquidationWorker` into `api/main.py` startup** (fixes B21, B22, B23).
**Gate:** `POST /api/v1/trade/orders` → order created → margin reserved → routed → filled → deal recorded → position opened → balance/margin updated → `StopOutEntered` on a losing tick → liquidation worker closes the worst-loss position → margin recovers. **One end-to-end integration test, no mocks below the repository layer.**

### M5 — It starts on a machine that isn't yours (1 day) · *"runs"*
`Dockerfile` (multi-stage: builder → slim runtime, non-root user). Add an `api` service to compose with `depends_on` + `condition: service_healthy` for postgres/redis. **Delete Kafka + Zookeeper** (unused, and `settings.yaml` doesn't reference them). `.env.example` with every secret, and startup **fails hard** if `SECRET_KEY`/`ADMIN_API_KEY` are unset. Remove the `init.sql` mount. Put Caddy or Traefik in front for automatic TLS. GitHub Actions: lint → typecheck → test → build image. Fix `test-e2e` and `--cov` in the Makefile (fixes B24 and the security items).
**Gate:** on a clean VM: `git clone && cp .env.example .env && make setup-dev` → `curl https://localhost/health` → `{"status":"healthy"}` with real DB and Redis checks. **This is your definition of done for "set up and run".**

**Total: roughly 7–11 focused days to a running system**, versus the ~75% figure in the chat log. The reason for the discrepancy is that the log measured *files written*; this measures *paths that execute*.

### Explicitly deferred (your instruction, and I agree)
`intelligence/` entirely · reports & statements · FIX · gRPC/cluster · in-house ECN/CLOB · real LP connectivity · ClickHouse analytics · Kafka · Eclipse Theia admin UI · client terminal · load testing · white-label · certificates beyond API TLS · KYC/backoffice · swap worker correctness beyond it importing · Automations engine · payment gateways · news/mail.

---

## 8. COMPARISON WITH THE OPEN-SOURCE REPOS

I cloned and inspected these rather than relying on the descriptions in `links-from-opencode-chat-file.md`.

### 8.1 `rabbittrix/ultra-low-latency-fx-etrading-platform` — **your closest architectural analogue**

The entire functional platform is **~50 Rust source files**:

| Crate | Files | Maps to your |
|---|---|---|
| `fx-core` | `audit_log`, `matching`, `order`, `orderbook`, `trade_log` | `core/domains/oms` + the missing `infrastructure/engines` |
| `fx-oms` | `model`, `oms` (3 files) | your `application/commands` + `core/domains/oms/services` |
| `fx-risk` | `engine`, `exposure`, `limits` | `core/domains/risk` (**note: `exposure` and `limits` are separate files — your NOP/exposure logic is tangled into the router**) |
| `fx-router` | `router`, `venue` | `core/domains/execution/router.py` (**`venue` is a first-class concept you lack**) |
| `fx-lp` | `lp`, `quote` | your **empty** `infrastructure/gateways` |
| `fx-md` | `feed`, `quote` | `core/domains/market_data` + `infrastructure/feeds` |
| `fx-exchange` | `book`, `venue` | your **missing** matching engine |
| `fx-ems` | `ems`, `strategy` | `application/services/execution_orchestrator.py` |
| `fx-gateway` | `api`, `handlers`, `openapi_proxy`, `proxy_types` | `api/` |
| `fx-pricing` | `engine`, `spread`, `risk_adjuster`, `ai_client` | ❌ **you have no pricing/spread/markup module at all** — Stage 3.8 |
| `fx-liquidity-graph` | `graph`, `planner`, `types` | ❌ your `lp_priority` list is a 1-D stub of this |
| `fx-deterministic-core` | `pinning`, `ring`, `tcp_tune` | ❌ (defer, correctly) |
| `fx-proto` | `generated/fx.etrading.rs` | ❌ `api/grpc` empty |

**Lesson:** a complete FX e-trading platform is ~50 files. You have 180 Python files / ~18,000 LOC and nothing runs. **You have over-built the domain model and under-built the vertical slice.** The fix is not more models — it's M4.
**Steal:** the crate boundaries, especially `fx-pricing` (spread/markup/risk-adjustment as its own concern — you have no equivalent anywhere) and `venue` as a first-class routing concept.

### 8.2 `nautechsystems/nautilus_trader` — **your reference for "Python-first, Rust hot path, and how to run it"**

- **Rust crates:** `core, model, data, execution, risk, portfolio, persistence, event_store, network, serialization, system, trading, backtest, live, adapters, analysis, indicators, infrastructure, plugin, cryptography, cli, pyo3, testkit`. Note **`event_store` and `persistence` are separate crates** — the journal is not the database.
- **Hot/cold, concretely:** `persistence/src/backend/{parquet, feather, catalog, catalog_operations, kmerge_batch, binary_heap, session, compare, custom}.rs` for cold columnar storage + `python/wranglers/{bar, delta, depth, quote, trade}.py` to reshape it; `event_store/src/backend/{memory, redb}.rs` + `capture/{adapter, builtins, encoder, registry}.rs` + `codec/format/headers/hash/manifest/kernel.rs` for the journal (an embedded key-value store, **not** Postgres); Postgres+Redis in `.docker/docker-compose.yml` for transactional/live state.
- **Execution internals worth copying:** `matching_core.rs`, `matching_engine/{config, ids_generator, settlement}.rs`, `order_manager/manager.rs`, `order_emulator/{adapter, emulator, handlers}.rs`, **`protection.rs`**, `models/{fee, fill, latency}.rs`, `engine/position.rs`.
- **Risk:** just `engine/{config, mod}.rs` + `sizing.rs` + `python/{config, sizing}.rs`. **Four files.** Yours is bigger and doesn't work.
- **The "runs" story:** `.docker/{DockerfileUbuntu, docker-compose.yml, entrypoint.sh, nautilus_trader.dockerfile, jupyterlab.dockerfile, preload-base-image.dockerfile}` + Makefile (`sync install install-debug build build-wheel py-stubs check-generated-drift clean format pre-commit check-code ruff clippy pre-flight security-audit cargo-deny cargo-vet docs`) + `.pre-commit-config.yaml`, `.gitleaks.toml`, `deny.toml`, `osv-scanner.toml`, `.gitattributes`, `SECURITY.md`, `ROADMAP.md`, `MIGRATION_V2.md`, `AGENTS.md`/`CLAUDE.md`. Compose binds ports to `127.0.0.1` and sets `security_opt: no-new-privileges:true`.
- **Lesson:** the PyO3 boundary is real and it works — `python/nautilus_trader/__init__.pyi` + `generate_stubs.py` + `py-stubs` + `check-generated-drift` keep Python types honest against Rust. Your "swap Python for Rust later" plan needs **exactly** this machinery, and you have none of it. Also: `pre-flight` and `check-generated-drift` are the gates that would have caught every one of your B1–B9.

### 8.3 `llc-993/matching-core` — **your reference for the journal + snapshot you don't have**

`src/api/{commands, events, market_data, types}.rs`, `src/core/{exchange, journal, orderbook, pipeline, snapshot, users}.rs`, `src/core/orderbook/{naive, direct, direct_optimized, advanced, simd_utils}.rs`, `src/core/processors/{matching_engine, risk_engine, grouping}.rs`, plus `benches/` (4), `examples/` (7), `scripts/`.
**Lesson:** `journal.rs` + `snapshot.rs` is the crash-recovery/backup story that your §5.2 shows you completely lack — MT5's backup server does this for you, and since you're on Path B **you must build it**. Also note `processors/` = an LMAX-Disruptor-style pipeline: risk → grouping → matching as discrete stages. And `orderbook/naive.rs` is the ~1-file first implementation to copy for M4.

### 8.4 `joaquinbejar/hft-clob-core` — **your reference for test & bench discipline**

8 crates: `wire, domain, matching, engine, risk, gateway, marketdata, clob-client`. `docker/{Dockerfile, docker-compose.yml}`. Makefile with **per-crate** test targets plus `test-stress-stp` (self-trade prevention under stress) and `test-proptest`. `BENCH.md` documents the methodology: HDR histogram at 1 ns resolution, 30 s bound, 70% new / 20% cancel / 10% aggressive-cross workload, 1M ops, 5 s warm-up, 10 s window, **seeded LCG (no `rand::*`, deterministic)**, synthetic monotonic `BenchClock`, and an explicit rule: report **p50/p99/p99.9/p99.99/max only — no mean, no stddev**, per its `CLAUDE.md` "tail-latency discipline".
**Lesson:** this is what "institutional-grade" testing actually looks like, and it's the antidote to your 6 assertion-free tests and your `pass`-bodied test that reports PASSED. Deterministic seeded randomness + property-based tests + tail percentiles. Adopt the *discipline* now (cheap), the *performance work* later.

### 8.5 `tfrmma/oms-order-management-system` — **your reference for margin & risk, in ~25 files**

`oms/{execution_core.cpp (27 KB), execution_core.hpp, risk_engine.hpp (7.6 KB), margin_monitor.hpp (6.2 KB), notional_gate.hpp (6.5 KB), order_pool.hpp, position_tracker.hpp, book_snapshot.hpp, timer_wheel.hpp, spsc_queue.hpp, oms_types.hpp, dashboard.hpp, logger.hpp}`, `sor/{routing_engine.cpp (15.5 KB), routing_engine.hpp, normalized_book.hpp, exchange_state.hpp, types.hpp}`, `algos/twap_scheduler.hpp`, `tests/test_oms.cpp (51 KB)`, `.github/workflows/ci.yml`.
**Three files you should read this week:**
- **`margin_monitor.hpp`** — the two-layer margin model your own `opencode_summery.md` prescribed (fast local estimate updated inline on every fill + slower authoritative poll; pre-trade always uses `max(local_used, remote_used)` = the *conservative* one). Your `RiskEngine.calculate_margin_level` docstring says *"Layer 1: Fast local RAM estimate"* — **but there is no Layer 2 anywhere in your codebase.** The comment is aspirational.
- **`notional_gate.hpp`** — pre-trade notional/exposure gating as a separate, testable component. This is exactly where your NOP limits belong; yours are embedded inside `SmartOrderRouter.route()`, which is why you can't test exposure independently.
- **`timer_wheel.hpp`** — for pending-order expiration and the dealer 30 s timeout, instead of polling.
**Lesson:** ~25 files + 51 KB of tests + CI. Note the test file is **half the size of the entire `oms/` directory**. Your tests are ~1/10th of your source and don't run.

### 8.6 Side-by-side

| | You | rabbittrix | nautilus | matching-core | hft-clob | tfrmma |
|---|---|---|---|---|---|---|
| Files (functional) | 180 py | ~50 rs | 23 crates | ~30 rs | 8 crates | ~25 |
| Runs today | ❌ | ✅ | ✅ | ✅ | ✅ | ✅ |
| CI | ❌ | ✅ | ✅ | — | ✅ | ✅ |
| Dockerfile | ❌ | — | ✅ | — | ✅ | — |
| Matching engine | ❌ none | ✅ | ✅ | ✅ (5 variants) | ✅ | — |
| LP gateway | ❌ none | ✅ `fx-lp` | ✅ adapters | — | ✅ `gateway` | ✅ `sor` |
| Journal/snapshot/backup | ❌ none | — | ✅ `event_store` | ✅ | — | — |
| Pricing/spread module | ❌ none | ✅ `fx-pricing` | ✅ | — | — | — |
| Margin monitor (2-layer) | 🟡 Layer 1 only | ✅ | ✅ | ✅ `risk_engine` | ✅ `risk` | ✅ `margin_monitor` |
| Property/fuzz tests | ❌ | — | ✅ | — | ✅ `test-proptest` | — |
| Benchmarks w/ tail latency | ❌ | — | ✅ `BENCHMARKING.md` | ✅ 4 benches | ✅ `BENCH.md` | — |
| Test:source ratio | ~1:10, broken | — | high | high | high | ~1:2 |

**The consistent signal across all five:** they are *smaller* than you and they *run*. Every one of them has a matching engine or an LP gateway — the two things you have zero of. Every one of them has CI. Four of five have a Dockerfile. **Your differentiator (MT5-accurate configuration semantics: Groups as rule engines, per-group symbol overrides, hedging/netting, coverage accounts, trade modification) is genuinely valuable and none of them have it** — but it's worth nothing until M0–M5 are done.

---

## 9. ANSWERING YOUR QUESTION DIRECTLY

> *"where we are and where we are stuck and what is to setup now?"*

**Where you are.** Stage 1: not applicable (MetaQuotes' job) unless you pick Path A, in which case 0%. Stage 2: ~15% — client JWT auth only, no managers, no roles, no first-admin bootstrap. Stage 3: models 35–60% field-complete against the real MT5 schema, but **0% runnable** — no config loader, no seeder, 8 stub CLI commands, 4 conflicting DB schemas, no create-account/create-client/create-symbol handlers, no admin endpoints. Stage 4: ~20% — a decent `SmartOrderRouter`, a well-shaped `ExecutionOrchestrator`, and **nothing that executes**: no matching engine, no LP gateway, no order book, and the orchestrator is never wired to the event bus. Cross-cutting: hot/cold storage designed correctly but unreachable; networking has an edge and no cluster, no TLS, no FIX, no gRPC; certificates 0%; ops has compose-without-an-app, no Dockerfile, no CI, a broken migration chain.

**Where you're stuck.** Not on design — your design is good and your MT5 understanding is better than most. You're stuck on **the last 15% of integration**: 9 one-line import errors that prevent the whole codebase from loading; a domain refactor (flat → nested value objects, renamed `Position` fields) whose callers, repositories, DB models, migrations, seed files and tests were never updated; and **nothing wired to anything at startup** — the orchestrator, the liquidation worker, the risk worker and the config cache are all built and all unreachable. The chat log's "75% complete" counted files written. Measured in *executable paths*, it's ~20%.

**What to set up now.** M0 → M5, in that order, §7. Concretely, this week: fix the 9 import errors and the duplicate model definitions; add CI so it can never regress; collapse the four schemas into one and pick **percent** for margin level; build the YAML loader and a real `seed` command with first-admin bootstrap. That alone takes you from "doesn't import" to "starts, has configuration, and can create an account" — which is the first time this system will have been *set up and run* at all. Then M3/M4 make an order actually execute and make the risk maths trustworthy. Then M5 puts it in Docker with TLS.

**And one thing to decide today,** before writing any of it: **Path A or Path B** (§0). If Path A, most of M3/M4 disappears and is replaced by an MT5 Manager API client + position poller + risk overlay — much faster to something a broker could use. If Path B, drop the MT5 Manager API *protocol mimicry* in `api/routers/manager/*` and build your own admin API; keep the MT5 *data model*, which is your real asset.
