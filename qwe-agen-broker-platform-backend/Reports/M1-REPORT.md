# M1 — Done. One schema, one margin unit, and MT5 import/export is proven.

**Tree:** `/home/user/work/bp` · **reproduce:** `./scripts/m0_run_all.sh` (13 steps, from pristine)
**Verify the gate:** `./scripts/verify_ci_gate.sh` · **Verify MT5 round-trip:** `scripts/m1_proof_roundtrip.py`

---

## Result

| | Pristine | After M0 | After M1 |
|---|---|---|---|
| Modules that import | 93 / 180 | 182 / 182 | **186 / 186** |
| `pytest tests` | 0 ran (10 collection errors) | 86 passed, 12 failed | **126 passed, 12 failed** |
| Shadowed definitions | 8 | 0 | 0 |
| Competing `groups` schemas | 4 (+1 in YAML) | 4 | **1** |
| Margin-level conventions | 2 (ratio + percent) | 2 | **1 (percent)** |
| Alembic revision graph | unresolvable | unresolvable | **resolvable, generated from models** |
| MT5 round-trip | n/a | lossless (codec only) | **362/362 symbols + 20/20 groups through the DB** |

The 12 remaining failures are **exactly the pre-existing set** from before M0 — 8 test↔domain constructor drift, 2 real `calculate_commission` bugs, 1 concurrency, 1 event-bridge type error. **Zero regressions.** All are M3 work.

**79 new tests** (39 codec + 40 schema/units), all passing.

---

## The headline: your MT5 import/export requirement is proven, not promised

```
=== 20 real MT5 groups from the live server export ===
field-identical re-export : 20/20
wire-contract conformant  : 20/20

=== 362 real MT5 symbols ===
field-identical re-export : 362/362
```

Every group and symbol from your real `TCTrader-Live` server goes **MT5 JSON → domain object → SQLAlchemy row → MT5 JSON** and comes out **field-for-field identical**, while still satisfying the wire contract MT5 Administrator enforces. Locked in as two pytest tests (`test_every_real_mt5_group_round_trips_through_the_database`, `test_every_real_mt5_symbol_round_trips_through_the_database`) so it cannot silently regress.

Getting there exposed four things I would not have found by reading.

### 1. MT5 uses the string `"default"` to mean *inherit* — in 60 of 64 override fields

Per-group symbol overrides mostly don't override anything. They say `"default"`, meaning *use the base symbol's setting*:

```
fields using the "default" sentinel: TradeMode 55, ExecMode 56, FillFlags 55,
  OrderFlags 56, VolumeMin/Max/Step/Limit 56 each, all 16 Margin* rates 56 each,
  SwapMode 47, SwapLong 54, Swap3Day 56, all 7 SwapRate* days 56, REFlags 56,
  IECheckMode/IETimeout/IESlipProfit/IESlipLosing 56, ... (60 of 64 fields)
```

My first typed codec converted `"default"` → `0`. **That turns "inherit the margin rate" into "the margin rate is zero"** — the difference between a correct margin call and letting a client open an unbounded position. The codec now preserves `INHERIT` verbatim in both directions and exposes `is_inherited()`; a test asserts no override field can silently become a number.

This is also why `GroupSymbolOverride` fields must stay `Optional`: `None` means *not overridden*, and the mapper emits `INHERIT` for it — never `0`.

### 2. Decimal scale varies per field **and per record** — no global scale round-trips

```
Point / TickValue / ContractSize / SwapLong   always 8 places
VolumeMin / VolumeMax / VolumeStep / Filter*  always ZERO places ("100", "40")
FaceValue                                     always 2
AccruedInterest                               2, 5, 8 and 0 in the SAME file
```

`PriceStrike` re-exported as `"0"` where the server had `"0.00"`. A `Decimal` column cannot remember which, so the observed scale is stored per row in `mt5_scale` JSONB and replayed on export via `_scaled()`.

### 3. `Point` and `TickSize` are different fields — and merging them corrupts every crypto symbol

I flagged this in M0 from the data; M1 confirmed it is worse than "131 differ":

```
Point != TickSize on 362 symbols   (i.e. all of them)
every crypto: Point = real step, TickSize = 0
  ADAUSD  Point=0.00001000  TickSize=0.00000
  BCHUSD  Point=0.00100000  TickSize=0.00000
```

`Symbol` now has **both** `tick_size` (MT5 `Point`, what price quantisation must use) and `mt5_tick_size` (MT5 `TickSize`). The DB columns are `point` and `mt5_tick_size` — deliberately *not* an unqualified `tick_size`, because that ambiguity is what caused the merge in the first place. A test asserts the column name `tick_size` does not exist.

> This matters for M3: the audit told you to change `mock_feed.py:65` to quantise to `symbol_info.tick_size`. On 362 symbols that is now correct only because `tick_size` means `Point`. Had it meant MT5's `TickSize`, every crypto price would have quantised to zero.

### 4. Your `instruments/enums.py` said "MT5-accurate" and four of them weren't

Values taken from `Include.md` (the SDK C++ headers). Measured impact over your 362 real symbols:

| Enum | Defect | Symbols misread |
|---|---|---|
| `CalculationMode` | Was an asset taxonomy (FOREX/CFD/FUTURES/OPTIONS/**BONDS**/STOCKS/INDICES/CRYPTO/METALS/ENERGY). MT5's is a margin algorithm list. | **245 as BONDS** (really CFDLEVERAGE), **54 as STOCKS** (really FOREX_NO_LEVERAGE), **18 as FUTURES** (really CFD) |
| `SwapMode` | Ordinals diverged from value 2 up; 3 MT5 modes missing | **7 as INTEREST_CURRENT** (really BY_MARGIN_CURRENCY), **5 as REOPEN_CURRENT** (really INTEREST_CURRENT), 2 unmappable |
| `GTCMode` | `TRADE`/`CALENDAR` vs MT5 `GTC`/`DAILY`/`DAILY_NO_STOPS` | safe only by coincidence (all 362 are value 0) |
| `OrderFlags` | `TRADE`/`TRADE_EXPERT`/`TRADE_PLUGIN` describes *who placed* an order. MT5's `EnOrderFlags` is a bitmask of *which order types are allowed*. | all 362 carry `127` = all seven bits |

After correction, **all 362/362 symbols map for CalcMode, SwapMode, GTCMode, TradeMode and ExecMode** — previously 299 had to be quarantined. `OrderTypeFlags` is now a proper `IntFlag`, and `127` decodes to `['MARKET','LIMIT','STOP','STOP_LIMIT','SL','TP','CLOSEBY']`.

Blast radius was 4 default-value references. Cheap now; it would not have been later.

**Also found:** a *third* meaning for the name `OrderFlags` — `core/domains/oms/enums.py` defines `OrderFlags(NO_SL, NO_TP, NO_SLTP_BY_TICK)` and `Order.activation_flags` uses it. So one name, three taxonomies. Left alone (it's OMS-side, M3), but recorded.

---

## One schema

Four definitions of `groups` existed. Now one.

| Source | Before | After |
|---|---|---|
| `ops/docker/init.sql` | UUID PK, `DECIMAL(5,4) DEFAULT 0.8000`, JSONB | **deleted**, compose mount removed |
| `alembic/versions/migration.py` | no `revision`/`down_revision` variables → graph unresolvable | **deleted** |
| `alembic/versions/001_initial_schema.py` | `symbols.margin_initial_percent` (a field `Symbol` no longer has), flat group columns | **regenerated from `Base.metadata`**: 12 tables, 270 columns |
| `db_models.py` `GroupModel`/`SymbolModel` | `name` PK, `Numeric(6,2) DEFAULT 60`, flat | **moved to `config_models.py`**, MT5-aligned |
| `config/groups/default_groups.yaml` | flat, fractions | untouched — **M2** (nothing reads it yet) |

`GroupModel` is now **58 columns**: MT5's 44 `ConfigGroups` scalars under their own names in snake_case (`margin_call`, `margin_stop_out`, `margin_so_mode`, `auth_password_min`, `company_*`, `limit_*`, `demo_*`, `trade_*`), plus JSONB for the nested value objects, plus `mt5_extra` / `mt5_scale` / `mt5_source`.

`SymbolModel` is **61 columns**: `point` **and** `mt5_tick_size` separately, the full 16-way `MarginRates` matrix as real columns (it's read on every margin calculation, so it must be queryable), sessions in MT5's Sunday-first shape, and the same three preservation columns.

The migration is **generated**, not hand-written — `scripts/m1_generate_migration.py` compiles `Base.metadata` through SQLAlchemy's own PostgreSQL DDL compiler and emits the revision, then `compile()`s the result to prove it parses. That check caught a raw `TIMESTAMP WITH TIME ZONE` in a `sa.Column()` call on the first run. Hand-transcribing 270 columns is how the last migration drifted; generating removes the possibility.

A test asserts the migration creates every table in the metadata, and another asserts the revision graph has exactly one root.

### Two `DeclarativeBase` classes

`database.py:7` and `db_models.py` each declared one. **Each owns a separate `MetaData` registry**, so `DatabaseManager.create_tables()` and `alembic/env.py` were creating *different schemas*. `database.Base` is now the single base; `db_models` re-exports it; `alembic/env.py` imports every model module so nothing is invisible to autogenerate. Verified: 12 tables on one metadata.

---

## One margin unit: PERCENT

MT5's convention, confirmed in your export (`MarginCall "50.00"`, `MarginStopOut "30.00"`, `MarginSOMode 0` = `STOPOUT_PERCENT`).

`Account.recompute_margin_level()` is now **the only place the formula lives**. Seven modules hand-rolled it before — five as a ratio, two as a percent. All seven call the method now.

Changed: `MarginProfile` defaults `0.8→80`, `0.5→50`; `create_group.py` command defaults; `settings.yaml`; every `else Decimal('0.5')` fallback in `risk_worker`, `liquidation_worker`, `liquidation_service`, `risk/engine`.

Also fixed while in there — these were the *other* half of the same bug:
- `risk/engine.py` read `account.group.margin_call_level`; the field is `account.group.margin.margin_call_level`. Both `detect_margin_call` and `detect_stop_out` raised `AttributeError` on every call. **They no longer do**, and `risk_worker` is no longer dead-code-that-throws.
- The `hasattr()` guards that silently substituted a fraction for a percent are gone.
- `MARGIN_LEVEL_UNLIMITED` sentinel replaces `Decimal('0')` for "no margin used" — zero read as *fully exhausted* and would stop out an account with no positions.

**The scenario from my earlier analysis now behaves correctly.** Verified by test: equity 10,000 / margin 25,000 = 40% against MT5's 50/30 thresholds → `MarginCallEntered` fires and `detect_margin_call` returns `True`. At 25% → `detect_stop_out` returns `True`. At 400% → neither.

---

## The export baseline: why `mt5_source` exists

My first attempt stored only the *unmodelled* fields in `mt5_extra`. It failed, and the failure is instructive: `split_mt5_record` computed the quarantine by comparing a rebuilt record against the original — but a field that was **never rendered** looked identical to a field that was rendered correctly, so 27 group fields and 70 symbol fields were silently dropped and re-exported as zeros and empty strings.

The fix is the right model anyway: **store the complete imported record as the export baseline**, and overlay only the fields the domain can actually edit.

```python
_GROUP_OWNED_WIRE_KEYS   = 17 of 44   # Group, Currency, MarginCall, TradeFlags, Limits, ...
_SYMBOL_OWNED_WIRE_KEYS  = 31 of 121  # Symbol, Path, Point, ContractSize, CalcMode, Swaps, ...
```

Rows created natively have no baseline and export from columns alone. Rows imported from MT5 export from the baseline with domain edits overlaid — so an admin changing a margin call through your API shows up in the export, and the 27 fields you can't edit yet come back exactly as they arrived, scale included.

`split_mt5_record(record, table)` is the seeder's entry point and returns `(domain, extra, scales)`. It exists because the alternative is a trap: build a `Group`, forget to pass the unmodelled fields, and they vanish.

---

## Also fixed

**`TradingSession` was completely broken.** `open_time`, `close_time` and `is_within()` all read `self.open_minute` (singular) while the field is `open_minutes` (plural) → `AttributeError` on every call. **Every trading-session check in the platform was dead**, including the one in `create_order`. `QuoteSession` used the singular spelling and worked, which is why nobody noticed. Both now use `open_minutes`/`close_minutes`, both gained `day_of_week`, and `close_minutes=1440` clamps to `23:59:59` instead of raising.

**The weekday index was documented backwards.** The docstring said *"MT5 stores sessions per day of week (0=Monday, 6=Sunday)"*. Your live export is **Sunday-first** (`SessionsQuotes[0]` is empty = Sunday closed, `[1..5]` are `0→1440`, `[6]` empty = Saturday closed). Corrected, with `wire.WEEKDAY_SUNDAY_FIRST` as the named authority so nobody can mistake it for Python's `weekday()` again. This would have shifted every session and every triple-swap day by one.

**The liquidation test could never have worked.** Its docstring said *"Margin Level = 3000/2200 = 136% (below 50% SO)"* — 136% is not below 50% — and claimed that after closing a position carrying a $5,000 loss the account reaches *"Equity = $8,000, Level = 727%"*. Closing a losing position **realises** the loss; equity does not rise. The source even contained a 41-line `# wait, that's wrong ... let me recalculate ... Actually, let me think about this more carefully` monologue, committed instead of resolved. Deleted, and the fixture rebuilt so the arithmetic is true:

```
balance 10,200 · floating PnL -9,000 · margin 2,200
equity  = 10,200 - 9,000 = 1,200        (LiquidationService computes it this way)
level   = 1,200 / 2,200  = 54.55%       < 60% stop-out  -> liquidate
close POS_002 (worst, -$5,000), freeing $1,100 of margin
level   = 1,200 / 1,100  = 109.09%      >= 60%          -> recovered, stop
POS_001 stays open
```

Both integration tests pass, and they now prove something.

**`di_setup.py` built `holiday_repo` and never returned it**, so it could not be injected. Fixed.

---

## Files

**New**
```
infrastructure/mt5/wire.py           format contract: envelope, UTF-16LE, validate()
infrastructure/mt5/fieldmap.py       10 field tables, 9 verified exact vs the server
infrastructure/mt5/codec.py          typed conversion, scale capture, INHERIT sentinel
infrastructure/mt5/enums.py          MT5 header values <-> domain enums, bitmasks
infrastructure/persistence/config_models.py    GroupModel (58) + SymbolModel (61)
infrastructure/persistence/config_mappers.py   codec-routed, baseline export
tests/unit/infrastructure/mt5/test_wire_codec.py           39 tests
tests/unit/persistence/test_m1_schema_and_units.py         40 tests
.github/workflows/import-gate.yml    6 checks; verified to fail on pristine
.gitattributes                       eol policy; *.dat/*.idx/*.lic/*.pfx binary
```

**Changed** — `db_models.py`, `mappers.py`, `interfaces.py`, `domain_events.py`, `di_providers.py`, `di_setup.py`, `market_data_setup.py`, `account.py`, `value_objects.py` (accounts + instruments), `enums.py` (instruments), `symbol.py`, `engine.py` (risk), `liquidation_service.py`, `liquidation_worker.py`, `risk_worker.py`, `create_group.py`, `group_repository.py`, 4 command handlers, `settings.yaml`, `docker-compose.dev.yml`, `alembic/env.py`, both integration tests.

**Deleted** — `ops/docker/init.sql`, `alembic/versions/migration.py`, the stale `DealModel`/`PositionModel`/`GroupModel`/`SymbolModel`, 8 shadowed definitions, 5 leftover chat-instruction comments, 41 lines of unresolved monologue.

---

## What M1 did *not* do

- **`config/*.yaml` still isn't read by anything**, and `default_groups.yaml` still has fractions and a flat schema. That is **M2** — patching values in a file nothing loads is busywork.
- **No seeder, no admin bootstrap, no `CreateAccount`/`CreateClient`/`CreateSymbol` handlers.** M2.
- **`RiskEngine` still reads `position.side` / `.average_price` / `.id`** — the stale `PositionModel` names. Fixed the *thresholds* and the *AttributeError* in `detect_*`, but `calculate_margin_level` still can't value a real position. **M3.**
- **`create_order` still prices market orders at `Decimal('1.0')`**, still commits margin inside the lock and the order outside it. **M3.**
- **`UnitOfWork` still raises `TypeError`** and never shares its session. **M3.**
- **`liquidation_worker` still hardcodes `conversion_rate = Decimal('1.0')`** — worst-loss-first still sorts on unconverted PnL. **M3.**
- **Orchestrator and liquidation worker still aren't wired to startup.** **M4.**
- **Still no Dockerfile, no app service in compose, no `.env.example`.** **M5.**
- `Symbol` still lacks `CurrencyProfit` / `CurrencyMargin`, the per-day `SwapRate*` curve, `IE*`/`RE*`, tick filtration, and the `*Ext` integer volumes. They ride in `mt5_source` losslessly; modelling them is incremental now, and `fieldmap.gap_report()` tracks the percentage.

---

## Next: M2 — configuration can enter the system

M1 made the schema and the MT5 boundary real. M2 makes it *loadable*, which is the last thing between you and "set up and run":

1. Pydantic config schemas mirroring the domain VOs; a YAML loader that **fails loudly on unknown keys**.
2. Rewrite `default_groups.yaml` + `instruments.yaml` onto the nested domain shape, in **percent**.
3. `CreateClientHandler`, `CreateAccountHandler`, `CreateSymbolHandler`; fix `CreateGroupHandler`.
4. **`Manager` entity + the 128-position `Rights` bitmask** from `ConfigManagers`, and first-admin bootstrap the MT5 way: generate, print the password once to stdout *and* the log, force change on first login.
5. `cli seed` for real — idempotent upsert through repositories. **And because M1 proved the codec, it can seed straight from a real MT5 export:** 20 groups and 362 symbols, field-identical, already tested.
6. Admin REST CRUD; make `ConfigCache` reachable and load it at startup.

**Gate:** `make docker-up && make migrate && make seed && make run` → `GET /admin/groups` returns your groups with correct percent thresholds, `GET /admin/symbols` returns symbols with `MarginRates` and sessions, `POST /admin/accounts` creates an account, and a restart gives identical output.
