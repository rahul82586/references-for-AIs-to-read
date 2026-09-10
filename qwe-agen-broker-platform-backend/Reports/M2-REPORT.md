# M2 — Done. Configuration can now enter the system.

**Tree:** `/home/user/work/bp` · **reproduce:** `./scripts/m0_run_all.sh` (19 steps from pristine)
**Verify the gate:** `./scripts/verify_ci_gate.sh` · **Verify the seed:** `scripts/m2_proof_seed.py`

---

## Result

| | Pristine | After M0 | After M1 | After M2 |
|---|---|---|---|---|
| Modules that import | 93 / 180 | 182 / 182 | 186 / 186 | **193 / 193** |
| `pytest tests` | 0 ran | 86 pass / 12 fail | 126 pass / 12 fail | **154 pass / 12 fail** |
| Can configuration enter the system? | **No** | No | No | **Yes** |
| Tables in the schema | 4 competing defs | 4 | 12 | **14** |
| `alembic` columns | drifted | drifted | 270 | **337** |
| CLI commands that work | 0 of 8 | 0 | 0 | **4 of 8** |
| Admin endpoints reading the DB | 0 (all hardcoded) | 0 | 0 | **7** |

The 12 failures are **byte-for-byte the same pre-existing M3 set** as before M2 — 8 test↔domain constructor drift, 2 real `calculate_commission` bugs, 1 concurrency, 1 event-bridge type error. **Zero regressions across three milestones.**

New tests: **42** (39 codec + 40 schema/units became 111 in `tests/unit/persistence` + `tests/unit/infrastructure`, of which 28 are M2).

---

## The payoff: one command imports a real broker

```
$ python -m cli.main seed \
      --mt5-groups  "Groups TCTrader-Live.json" \
      --mt5-symbols "Symbols TCTrader-Live.json"

         Seed report
┏━━━━━━━━━━━━━━━━━━━┳━━━━━━━┓
┃ Item              ┃ Count ┃
┡━━━━━━━━━━━━━━━━━━━╇━━━━━━━┩
│ groups created    │    21 │     <- 20 from MT5 + coverage\house
│ groups updated    │     6 │     <- the YAML ones MT5 also has
│ symbols created   │   362 │
│ symbols updated   │     5 │
│ coverage accounts │     1 │
│ admin created     │   yes │
└───────────────────┴───────┘

First administrator created
  login    : 1000
  password : XrNzUhTJqViLjTrC
  This is shown ONCE. Save it now - the password must be changed
  on first login, and only the hash is stored.
```

Your **entire live MT5 server configuration — 20 groups and 362 symbols — now loads into the database in one command**, and re-exports field-identically (tested). That was the thing M1 built the codec for, and it is what makes "set up and run" mean something: you are not starting from six hand-written YAML groups, you are starting from a real brokerage's configuration.

And `status` verifies it rather than trusting the seed:

```
$ python -m cli.main status
 groups   21 · symbols  362 · accounts 1 · managers 1

 Groups (margin thresholds are PERCENT)
 real\real       real         50.00   30.00   100
 real\real-A     real         70.00   40.00   200
 demo\Standard   demo         10.00    1.00   100
 demo\Challenge  contest      50.00   30.00   100
 coverage\house  coverage     50.00   30.00  1000
 preliminary     preliminary  50.00   30.00     0

 Symbols
 EURUSD  5  0.00001000  0  100000.00000000  FOREX
 XAUUSD  2  0.01000000  0     100.00000000  CFD
 BTCUSD  0  1.00000000  0       1.00000000  FOREX_NO_LEVERAGE

 Configuration plane is populated.
```

---

## Seven defects found and fixed while building it

Every one of these was a hard blocker on the path to "configuration can enter the system", and none were visible from reading the code.

### 1. `subscribe()` was `async` and **20 of 24 call sites never awaited it**

An unawaited coroutine is a no-op. So:

- **`ConfigCache` never subscribed to anything** — its nine invalidation handlers were dead. A group edited through the API would keep serving the **stale in-memory copy forever**, which is worse than having no cache at all.
- **`LiquidationWorker` never subscribed to `StopOutEntered`** — stop-outs were detected and nothing acted on them.
- **`WebSocketEventBridge` never subscribed** — no client would ever receive a real-time order, deal or position update.

And the channel key was inconsistent across call sites: some passed the event **class** (`GroupCreated`), some the `EventType` **enum**, some its **`.value` string**. `publish` keyed on one convention, `subscribe` on another, so even an awaited subscribe would not have matched.

**Fix:** `subscribe()` is now **synchronous** and returns a self-registering awaitable, so both `bus.subscribe(...)` and `await bus.subscribe(...)` work without renaming anything or breaking a single test mock. `normalize_channel()` reduces class/enum/string to one key, and `publish()` dispatches under all three so any convention a caller picks will match. A test asserts `ConfigCache` actually registers ≥9 handlers — it would have been 0 before.

### 2. `Decimal` is not JSON-serialisable — MT5 import would crash on the first group

`mt5_extra`, `mt5_scale`, `mt5_source` and the nested JSONB columns all receive Decimals from the codec, because **every MT5 wire scalar is a decimal**. SQLite fails immediately with `Object of type Decimal is not JSON serializable`; PostgreSQL's serialiser would too. `seed --mt5-groups` would have died on group 1 of 20.

**Fix:** `_json_safe()` at every JSONB write boundary. Decimals become **strings**, which is also MT5's own wire representation — so a stored value re-exports byte-identically instead of coming back as a rounded float.

### 3. 128 manager rights do not fit in two 64-bit masks

My first design split MT5's 128-position `Rights` array into two `BigInteger` columns at index 63. That leaves **65 rights in the high word**, and bit 63 is the *sign* bit of a signed 64-bit column. SQLite rejects it outright (`Python int too large to convert to SQLite INTEGER`); PostgreSQL would silently store a negative number.

**Fix:** three masks of 43 bits. A test round-trips **every single right index 0..127 individually**, so an off-by-one here cannot recur.

### 4. `SqlRoutingRuleRepository` never implemented `delete()`

`IRoutingRuleRepository` has declared it since before M0. Instantiating the class raised `Can't instantiate abstract class ... with abstract method delete` — and `setup_persistence_di()` constructs it, which is what both the CLI bootstrap and the API's DI wiring call. **Nothing could start.**

**Fix:** implemented, plus a new **CI check that every repository implements its port**. Inherited abstract methods don't appear in a subclass's own `__abstractmethods__`, so the check walks the MRO — that subtlety is why my first version of the check reported "none missing" while the class was still uninstantiable.

### 5. `ConfigCache.initialize()` called two methods that did not exist

It calls `symbol_repo.get_all()` and `account_repo.find_all()`. The symbol repo's method is `get_all_symbols`, and **`find_all` was never implemented at all** — `IAccountRepository` did not even declare it, so no implementation was obliged to provide it. The entire hot path threw `AttributeError` at startup.

**Fix:** `find_all` declared on the port and implemented; `get_all` provided as a concrete alias on `ISymbolRepository`. `test_config_cache_initialize_finds_the_methods_it_calls` now runs the real `initialize()` against a real database.

### 6. An explicit `account_type` was silently overwritten by the path prefix

`demo\Challenge` is a **CONTEST** group and `coverage\house` is a **COVERAGE** account, but neither prefix says so. Both `parse_group` and `db_to_group` derived the type from the path unconditionally, discarding the stated value and reclassifying contest and coverage accounts as plain demo/real.

**Fix:** stored/explicit wins, path derivation is the fallback. Test covers both directions.

### 7. `TradeFlags 215` came back as `15`, and limits came back as 200/200/100

The MT5 loader never read `TradeFlags`, `currency_digits`, `limit_positions` or `limit_symbols` off the wire, so the dataclass defaults overwrote the server's real values on export. Those bits are **actual trading permissions** — `SO_COMPENSATION` allows negative-balance compensation after a stop-out, `HEDGE_PROHIBIT` forbids hedged positions. Losing them silently changes what clients may do. And `LimitPositions: 0` means *unlimited*; the default `200` means a hard cap nobody configured.

**Fix:** every domain-owned field is carried off the wire. A test asserts all 20 groups keep their exact `TradeFlags`.

---

## Also fixed

**`Account` persistence was losing 18 of its 29 fields.** The old `AccountModel` had 14 columns. Gone on every save: the **entire stop-out state machine** (`so_activation`, `so_time`, `so_level`, `so_equity`, `so_margin`), `margin_level`, `profit`, `commission`, `storage`, `credit`, `client_id`, `group_id`, `color_tag`, `dealer_notes`, `is_online`, `last_login`, `registration_date`, `currency_digits`.

The stop-out fields are the serious ones. `evaluate_margin_state()` moves an account NONE → MARGIN_CALL → STOP_OUT and records the equity and margin at the moment of stop-out; `TickMarginPipeline` calls it then persists. On the next tick the account was reloaded with `so_activation = NONE`, so **the state machine restarted from the beginning every tick**: `MarginCallEntered` would fire forever, `StopOutEntered` repeatedly, and `StopOutExited` was unreachable. Now 31 columns, and a test round-trips a stopped-out account.

**`account_to_db` read `account.login_id` and `account.kyc_verified`** — neither exists (the field is `login`, and there is no `kyc_verified`), and `AccountModel` had a `kyc_verified` column nothing could populate. **Saving any account raised `AttributeError`.** Same refactor drift that broke `RiskEngine`.

**The admin API was hardcoded.** `GET /api/v1/admin/groups` returned two invented literals — `demo_group` at `margin_call_level: "60"` and `real_group` at `"80"` — and `GET /admin/symbols` returned five invented symbols, regardless of database contents. **That is exactly where `api_test_results.md`'s "25/25 endpoints PASS" came from**: the endpoints could not fail because they never looked anything up. Seven endpoints now read through the repositories, plus `GET /admin/status` which answers *"is the configuration plane populated?"* — the question you could not previously ask without reading the database by hand.

**Every CLI command was a stub that printed success.** `make setup-dev` chained four no-ops and printed *"Development environment ready!"* over an empty database. `seed`, `status`, `migrate` and `start` are implemented; the other four (`backtest`, `sync`, `export`, `import_data`) now **fail loudly with an explanation** instead of printing a green success line. `setup-dev` ends with `status` as a gate.

**Typer was swallowing tracebacks.** A `TypeError` deep in the bootstrap surfaced as a bare `exit: 1` with no output — which is how I nearly shipped defect #1 above as "working". The CLI now prints the exception and the traceback.

**`.env.example` did not exist**, though the README said `cp .env.example .env`. Created, with every secret and a note that the two defaults compiled into the source (`BROKER_PLATFORM_SECRET_KEY_CHANGE_IN_PRODUCTION`, `ADMIN_SECRET_KEY_12345`) are in git history and must be treated as compromised.

**My own margin guard was too strict.** I initially rejected any threshold `<= 1` as a fraction. That rejected **13 of your 20 real groups** — every demo group legitimately runs `MarginStopOut: 1.00`. Now only the specific literals this codebase used (`0.8`, `0.5`, `0.7`, `0.4`, …) are rejected, so a real 1% stop-out loads and a reintroduced fraction still fails.

**New tables:** `managers` (23 columns, incl. the three rights masks and `group_scope`) and `clients` (27 columns, all of MT5's `IMTUser` fields including `agent_login`, `last_pass_change`, `certificate_fingerprint`). `ManagerAccount` and `Client` already existed as entities — they had no persistence at all.

---

## The YAML, rewritten with real values

`config/groups/default_groups.yaml` — 7 groups, nested shape, percent thresholds, MT5 group paths (`real\real`, `demo\Standard`, `coverage\house`, `preliminary`), `MarginMode RETAIL_HEDGED`, real commission rules, real routing modes.

`config/symbols/instruments.yaml` — 5 symbols with values **taken from your live export**, not invented. Every place the old file guessed, it was wrong:

| Field | Old file | Real server | Impact |
|---|---|---|---|
| `EURUSD` swap_long | `-2.5` | `-7.9` | swaps understated 3× |
| `EURUSD` swap_short | `+0.83` | `-0.83` | **wrong sign** — paying clients instead of charging |
| `swap_3day` | `Wednesday` | `5` (Friday, Sunday-first) | **triple swap on the wrong day** |
| `tick_value` | `10` | `0` | invented value |
| `volume_max` | `100` | `10` lots | 10× the real cap |
| `XAUUSD` base currency | `USD` | `XAU` | backwards |
| `XAUUSD` contract size | `100000` | `100` oz | 1000× wrong margin |
| `XAUUSD` margin rate | `1.0` | `0.02` | 50× wrong margin |
| `BTCUSD` contract size | `100000` | `1` BTC | 100,000× wrong |
| `BTCUSD` digits | `2` | `0` | wrong rounding |

The loader is **strict**: unknown keys are an error naming the key and listing every valid one, a pre-M1 field (`precision`, `margins`, `margin_initial_percent`, `fill_mode`, `margin_call_level` flat) is an error saying what replaced it, a non-positive `tick_size` is an error explaining that it holds MT5's `Point`, and an unmappable enum is an error listing the valid members. Enums accept **both** the name (`MARKET`) and the MT5 integer (`2`), because MT5 stores integers and a hand-written YAML naturally says `MARKET` — forcing one or the other is what pushes authors to guess ordinals, which is how the `CalcMode`/`SwapMode` defects happened.

Sessions accept all three shapes an author will reach for: MT5's Sunday-first 7-array, weekday names, or a flat list with `day`.

---

## Not done

- **`CreateAccountHandler`, `CreateClientHandler`, `CreateSymbolHandler` still don't exist.** Only `CreateGroupHandler` does (fixed). So configuration can be *seeded* but not yet created through an API. `POST /admin/groups/create` exists; `POST /admin/accounts` does not.
- **No `IClientRepository` port** — `SqlClientRepository` exists but is not injectable, so `CreateClientHandler` has nothing to depend on.
- **Manager JWT / role enforcement.** Managers persist with their 128-right bitmask, but `api/auth/admin_dependencies.py` still gates on the static `ADMIN_API_KEY`. Authenticating *as* a manager and enforcing its `group_scope` is the rest of Stage 2.
- **`forced password change` is stored (`must_change_password`) but not enforced** on login.
- **`start` only runs the `api` role.** trade/history/access/worker share the codebase but have no separate entrypoint yet.
- **Still no Dockerfile, no `api` service in compose.** M5.
- **Everything in M3/M4 is untouched:** `RiskEngine` still reads `position.side`; `create_order` still prices market orders at `1.0`; `UnitOfWork` still raises `TypeError`; `liquidation_worker` still hardcodes `conversion_rate = 1.0`; the orchestrator is still unwired.

---

## Next: M3 — make the risk maths trustworthy

M2 got configuration *in*. M3 makes the numbers that come out of it correct. It is the highest-value remaining work because every one of these is a money-losing bug, and all four were identified back in the first analysis:

1. **`RiskEngine` reads `position.side` / `.average_price` / `.id`** — the real entity has `action` / `price_open` / `position_id`. Every position throws, a bare `except` swallows it, and **margin and PnL silently come back zero**.
2. **`create_order` prices market orders at `Decimal('1.0')`** — margin understated 150× on JPY pairs.
3. **`liquidation_worker` hardcodes `conversion_rate = Decimal('1.0')`** — worst-loss-first sorts on unconverted PnL, so it **closes the wrong positions**.
4. **`UnitOfWork` raises `TypeError`** and never shares its session — the "atomic" trade path is not atomic. Plus `create_order` commits margin inside the lock and the order outside it.
5. **`get_conversion_rate` has no cross-rate triangulation** (EURJPY→USD needs EURUSD) and swallows every error with `except Exception: pass`.
6. **`Group.calculate_commission`** returns 0 or the wrong value (2 failing tests) and `return`-in-loop means only the first matching rule applies — MT5 stacks them.

**Gate:** the four validation rows from your own `opencode_summery.md` as real assertions — EURUSD/USD `$10.00`, USDJPY/USD `~$6.67`, EURJPY/USD `~$6.67`, GBPAUD/USD `~$6.50` per pip per lot — plus `test_account_lock_prevents_double_spend` genuinely passing, plus the `pass`-bodied `test_cross_currency_pnl_in_margin_loop` filled in or deleted. That takes the suite from 12 failing to roughly 2, and the remaining 2 are the concurrency and event-bridge tests.
