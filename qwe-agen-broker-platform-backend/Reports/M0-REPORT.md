# M0 — Done. The codebase imports, and the MT5 wire format is now a first-class module.

**Tree:** `/home/user/work/bp` (your `refs/` clone is untouched)
**Reproduce from pristine:** `./scripts/m0_run_all.sh`
**15 source files changed · 8 files added**

---

## Result

| | Before M0 | After M0 |
|---|---|---|
| Modules that import | **93 / 180** | **182 / 182** |
| `import api.main` | ❌ `ImportError: GroupCreated` | ✅ |
| `import infrastructure.persistence.db_models` | ❌ `NameError: BigInteger` | ✅ |
| `pytest tests --collect-only` | ❌ 10 collection errors | ✅ |
| `pytest tests` | **0 ran** | **86 passed, 12 failed** |
| Shadowed top-level definitions | 8 | 0 |
| CI gate | none | `.github/workflows/import-gate.yml` |

The 12 remaining failures are all **pre-existing**, and all belong to M1/M3 — not M0:
8 are test↔domain constructor drift (`Symbol(margin_initial_percent=…)`, `Group(margin_call_level=…)`, `TradingSession(start=…)`, `CommissionTier(volume_from=…)`), 2 are the real `Group.calculate_commission` bugs, 1 is the concurrency test, 1 is an event-bridge type error.

**The gate is not decorative** — I verified it against both trees:

```
PRISTINE   [1] compileall      pass
           [2] import modules  FAIL  (93/180)
           [3] collect tests   FAIL
           [4] no shadowing    FAIL  (8 shadowed)

M0-FIXED   [1] compileall      pass
           [2] import modules  pass  (182/182)
           [3] collect tests   pass
           [4] no shadowing    pass
```

Run it yourself: `./scripts/verify_ci_gate.sh`

---

## The MT5 format guarantee you asked for

New package `infrastructure/mt5/`, with **39 tests** that run against your real server export.

### `wire.py` — the format contract, documented and enforced

I verified the contract empirically before writing a line of it:

1. Envelope `{"Server":[{"Config<Section>":[…]}]}` — 14 sections
2. **Every scalar is a JSON string.** No numbers, no booleans, no nulls. `"50.00"`, `"87"`, `"0"`, `""`
3. Decimals carry a **fixed scale that is part of the value**
4. Lists are either arrays of strings or arrays of objects
5. `SessionsQuotes`/`SessionsTrades` = **7-element array, index 0 = Sunday**, `{"Open","Close"}` in minutes 0–1440
6. Flag fields are **decimal-encoded bitmasks** (`TradeFlags: "87"`)
7. Paths are backslash-separated (`FX\Forex\EURUSD`, `real\real`)

`decode_bytes` handles the **UTF-16LE + BOM** that Administrator writes on Windows, and UTF-8, so both the raw export and a re-saved copy load. `validate()` rejects any payload containing a JSON number, boolean or null — because MT5 Administrator would reject that file.

**Because rules 2 and 3 hold universally, decode/encode are lossless by construction: the wire layer performs no type coercion at all.** Typing lives only in the codec, and only inbound, so a lossy import can never corrupt an export.

### `fieldmap.py` — the authoritative translation table

Every MT5 field, extracted from the live export rather than from prose. **9 of 9 tables verified to match the server's field list exactly, in order** — there is a test that fails if the server schema drifts.

| MT5 entity | Fields | Table |
|---|---|---|
| `ConfigSymbols` | 121 | ✅ exact |
| `ConfigGroups` | 44 | ✅ exact |
| Group symbol override | 64 | ✅ exact |
| Commission | 12 | ✅ exact |
| Commission tier | 8 | ✅ exact |
| `ConfigRouting` | 12 | ✅ exact |
| `ConfigGateways` | 22 | ✅ exact |
| `ConfigHolidays` | 8 | ✅ exact |
| `ConfigManagers` | 9 | ✅ exact |

Each entry is `Field(mt5_name, domain_path, kind)`. An empty `domain_path` means *"MT5 has it, we don't model it yet"* — so the gap is a number, not an impression:

```
ConfigSymbols                 51/121   42.1%
ConfigGroups                  17/ 44   38.6%
ConfigGroupCommissions         4/ 12   33.3%
ConfigGroupCommissionTiers     7/  8   87.5%
ConfigGroupSymbols            11/ 64   17.2%   <- widest gap
ConfigRouting                  1/ 12    8.3%   <- Stage 4 is nearly unmodelled
ConfigGateways                 3/ 22   13.6%   <- A-book
ConfigFeeders                  2/ 11   18.2%
ConfigHolidays                 4/  8   50.0%
ConfigManagers                 6/  9   66.7%
```

`gap_report()` / `all_gaps()` produce that table, and a test pins symbol coverage at `>= 50 modelled` so it cannot silently regress.

### `codec.py` — typed conversion, with the round-trip guarantee

```python
test_decode_encode_round_trip_is_lossless[symbols]    362 records x 121 fields   PASSED
test_decode_encode_round_trip_is_lossless[groups]      20 records x 44 fields    PASSED
test_decode_encode_round_trip_is_lossless[routing]                             PASSED
test_decode_encode_round_trip_is_lossless[holidays]                            PASSED
test_decode_encode_round_trip_is_lossless[managers]                             PASSED
test_decode_encode_round_trip_is_lossless[gateways]                             PASSED
test_round_trip_preserves_nested_commission_tiers                               PASSED
test_whole_file_reexport_is_byte_identical                                      PASSED
```

Your entire live server configuration — 362 symbols, 20 groups with their commission tiers and per-symbol overrides, routing, gateways, holidays, managers — goes **MT5 JSON → our domain representation → MT5 JSON** and comes out **identical**. That is the import/export capability you asked for, proven against real data.

Fields we don't model are quarantined under `_mt5_extra` rather than dropped, and each decimal's observed wire scale is remembered under `_mt5_scale`. That is what makes the round trip lossless *while the domain model is still incomplete* — so you can adopt MT5's schema incrementally without ever breaking export.

`export_section()` validates before writing and **refuses** to emit a non-conformant file.

---

## Three things I discovered while building it

These are not codec details. Each one is a real defect or a real design input.

### 1. `Point` and `TickSize` are different fields — and merging them would corrupt 131 of your 362 symbols

My first version mapped both to the domain's single `tick_size`. The round-trip test caught it:

```
Point (rec 16)   orig='0.00001000'   back='0.00000000'
```

Measured across the export: **`Point != TickSize` for 131 / 362 symbols**, including *every* crypto:

```
ADAUSD    Point=0.00001000    TickSize=0.00000
AVEUSD    Point=0.01000000    TickSize=0.00
BCHUSD    Point=0.00100000    TickSize=0.00000
```

`Point` is the price-precision step (populated, scale 8, on all 362). `TickSize` is frequently **zero**.

**This matters beyond the codec:** `mock_feed.py:65` quantises prices to `spread`, and the audit said to change it to `symbol_info.tick_size`. On 131 of 362 symbols that would quantise to **zero** and destroy every price. The correct fix is `Point`, and the domain needs a *separate* `tick_size`. There is now a test (`test_reference_export_has_symbols_where_point_differs_from_tick_size`) that fails if a fixture stops exercising this.

### 2. Decimal scale is per-field **and** per-record — no global scale can round-trip

```
Point              {8: 362}                        always 8 places
TickValue          {8: 362}
ContractSize       {8: 362}
VolumeMin          {0: 362}                        always ZERO places ("100", not "100.00000000")
FilterSoft         {0: 362}
FaceValue          {2: 362}                        always 2
AccruedInterest    {2: 309, 8: 44, 5: 1, 0: 8}     VARIES BY RECORD
TickSize           {0: 16, 2: 232, 1: 13, 3: 37, 5: 46, 4: 17, 8: 1}
```

`AccruedInterest` alone uses four different scales in one file. So the codec captures the observed scale per field per record on import and replays it on export, with a `SCALE` fallback table (derived from the export) for records we create ourselves. `test_decimal_scale_is_preserved_per_field_and_per_record` and `test_fresh_record_uses_mt5_default_scale_when_nothing_was_captured` pin both directions.

### 3. `ConfigManagers.Rights` is a positional 128-element bitmask array — and it *is* your Stage 2 role model

You asked how admin/dealer/manager roles work. The answer is in your own export:

```
Rights: 128 entries, each "0" or "1", POSITIONALLY INDEXED
```

All 9 managers in the reference export have all 128 set — that is what an auto-created administrator looks like. A dealer or an API-only manager would have most positions `"0"`. Plus `Groups: [{"Group": "*"}]` scoping which client groups a manager may administer, mirroring the MT5 rule that a manager only administers accounts on the trade server where its own account lives.

**So don't invent a role enum.** Map the 128 positions from the SDK's manager-rights enum and `Rights` becomes your permission model directly, and it round-trips to MT5 for free.

*(Also note: `State` in `ConfigGateways` is a single object, not an array — the codec now passes dict-shaped nested fields through verbatim rather than blanking them. That was a genuine round-trip bug my own test caught.)*

---

## What was actually broken, and what I did about it

### The 9 missing imports
`Any` in `core/ports/interfaces.py:9` (this one alone broke **every** module importing ports, and all 10 test modules); `BigInteger` in `db_models.py`; `Any`/`Optional`/`Decimal` in `record_deal`, `commission_service`, `execution_orchestrator`, `execution/router`, `ledger/engine`; `datetime` in `order_repository` and `position_repository`; `AsyncSession` in `position_repository`; `swap_worker` importing the non-existent `core.domains.oms.models` (→ `core.domains.oms.enums`).

### The 8 shadowed definitions — merged, not deleted

| File | Duplicates | Resolution |
|---|---|---|
| `db_models.py` | `DealModel` ×2, `PositionModel` ×2 | **Kept the MT5-accurate ones.** The stale pair used `side` / `average_price` / `id` / `unrealized_pnl` / `swap_accumulated` — **which is exactly where `RiskEngine` picked up attribute names the real `Position` entity does not have.** Deleted the stale pair, preserved `original_deal_id` (the MT5 trade-modification chain) onto the survivor. |
| `interfaces.py` | `IOrderRepository` ×2, `IDealRepository` ×2, `IPositionRepository` ×2 | Kept the MT5-accurate definitions, merged in the useful methods from the stale halves (`find_active_orders_by_account`, `get_next_ticket_id`, `close`). |
| `domain_events.py` | `OrderCancelled` ×2, `OrderModified` ×2 | **Kept the originals.** The appended copies omitted `event_type`, so they inherited `DomainEvent`'s default — meaning every cancel/modify event would have serialised to Redis as `"order.created"`. Silent data corruption. |
| `di_providers.py` | `get_cancel_order_handler` ×2 | Kept the container-resolving one, restored the `get_account_query_handler` alias that was sitting between them. |

### Missing symbols that blocked startup
- **`IGroupRepository`** — never defined, imported by 6 modules. Added, with `save` / `find_by_id` / `find_by_name` / `get_all` / `get_all_groups` / `delete`.
- **8 config-plane domain events** — `GroupCreated/Updated/Deleted`, `SymbolCreated/Updated/Deleted`, `HolidayUpdated/Deleted` — imported by `config_cache.py`, `create_group.py` and `api/main.py` but never defined. Added with proper `EventType` members (`config.group_created`, …), documented as the analogue of MT5's sink pattern (`IMTConGroupSink::OnGroupUpdate`).
- **`get_di_container`** — imported by `api/main.py`, never defined. Added, with a `resolve()`-capable view over the existing dict container and a **port → container-key** registry, so `container.resolve(IGroupRepository)` works. Unregistered ports raise `KeyError` listing what *is* available, rather than returning `None`.
- **`CommissionProfile` / `ExecutionProfile`** — `group_repository.py` imported value objects that were renamed away.

### Two chat transcripts pasted into module scope
These executed at import or call time and referenced names that never existed:

- `application/di/market_data_setup.py` — module-level `tick_pipeline = TickMarginPipeline(container.resolve(...))` and `event_bus.subscribe(...)`, with `container`, `event_bus`, three ports and `RiskEngine` all undefined, and the original chat instructions (`# 1. Instantiate the Pipeline`, `# 2. Subscribe to Tick events`) still in the source. **Rewritten as factories** — `build_tick_margin_pipeline()`, `wire_tick_subscriptions()`, `build_market_data_stack()` — which is what the module's own docstring always claimed it was. Nothing touches the DB or event bus at import time now.
- `infrastructure/persistence/di_setup.py` — `container.register(IHolidayRepository, holiday_repo)` inside a function that builds and *returns* a dict. `container` and `IHolidayRepository` undefined → **the entire persistence layer threw the moment it was called.** Also `holiday_repo` was built but never returned, so it could not be injected. Fixed; `holiday_repo` is now in the returned container payload.

Plus 3 leftover `# Find the existing X class and REPLACE it with:` comments and 2 `# Add these to core/events/domain_events.py` comments removed from production source.

### Interface segregation (this one was my own regression, and it's worth knowing about)
Merging the duplicate ports produced the **union** of their methods — the right contract, but marking all ten `@abstractmethod` meant every implementation *and every test mock* had to provide all ten before it could be instantiated at all. That broke a previously-passing integration test:

```
TypeError: Can't instantiate abstract class MockPositionRepository
           with abstract methods close, get_positions_by_account
```

So: the methods the application actually calls stay abstract; the extended MT5 query surface (20 methods) now has a default implementation that raises `NotImplementedError` **naming itself**. An implementation can adopt MT5's full query set incrementally, and a failure tells you exactly which method is missing instead of failing at construction.

### `.gitattributes`
`* text=auto eol=lf`, explicit rules per extension, and `*.lic *.dat *.idx *.pfx` marked **binary** — because MT5 exports are UTF-16LE and git treating them as text would mangle them and break the round-trip guarantee. The file documents *why*: the tree is currently mixed CRLF/LF, AI patches have inserted LF lines into CRLF files, and `core/domains/risk/engine.py` has a bare `\r` mid-file at the `detect_margin_call`/`detect_stop_out` boundary.

---

## What I deliberately did **not** do

- **Did not normalise line endings.** That's a whole-repo diff; it belongs in its own commit after `.gitattributes` lands, not mixed into a functional fix.
- **Did not touch the 4 competing schemas.** `init.sql` (UUID PK, `DECIMAL(5,4)`, `0.8000`, JSONB) vs `db_models.py` (`name` PK, `Numeric(6,2)`, `60`, flat) vs `alembic/001` vs the domain (nested VO, `0.8`) — plus `config/*.yaml` as a fifth. That's **M1**. I only added `GroupModel.group_id` so the new `IGroupRepository.find_by_id`/`delete` have something to query.
- **Did not rewrite `group_to_db` / `db_to_group`.** They still reference `group.leverage_default`, `group.margin_call_level`, `group.swaps.enable_swaps` — fields the domain moved into `MarginProfile`/`SwapConfiguration`. They import fine but **will fail at runtime**. Rewriting them correctly requires the M1 schema decision first; doing it now would mean doing it twice.
- **Did not fix the margin-level unit** (ratio vs percent). The codec and fieldmap now **document and enforce percent** on the MT5 boundary, which is the decision M1 needs to propagate inward.
- **Did not fix `RiskEngine`, `create_order`, `UnitOfWork`, `liquidation_worker`.** Those are M3.
- **Did not wire the orchestrator or liquidation worker.** That's M4.

`SymbolModel` is stale in the same way `GroupModel` is (`margin_initial_percent`, `fill_mode`, `sessions_json` vs the domain's `MarginRates`/`fill_flags`/`quote_sessions`) — also M1.

---

## How to run it

```bash
cd /home/user
./scripts/m0_run_all.sh                 # rebuild work/bp from pristine + apply all 6 steps
./scripts/verify_ci_gate.sh             # prove the gate fails on pristine, passes on fixed

cd work/bp
PYTHONPATH=$PWD BROKER_MT5_FIXTURES=/home/user/decoded/mt5-format-structure \
  python3 -m pytest tests -q            # 86 passed, 12 failed (all pre-existing)

PYTHONPATH=$PWD python3 -m pytest tests/unit/infrastructure -q   # 39 passed
PYTHONPATH=$PWD python3 -c "import api.main; print('api.main OK')"
```

Fixtures are optional: without `BROKER_MT5_FIXTURES` the 12 fixture-dependent tests skip and the other 27 still run.

**Scripts,** so this is repeatable rather than a one-off edit:
`m0_run_all.sh` (orchestrator) → `m0_fix_imports.py` → `m0_fix_models_events.py` → `m0_restore_di.py` → `m0_segregate_ports.py` → `m0_fix_di_order.py` → `m0_fix_di_factories.py`, plus `mt5pkg/` (the codec package, its test, the CI workflow and `.gitattributes`).

---

## Next: M1 — one schema, one migration, one margin unit

Now that the tree imports and the MT5 field map exists as an authoritative spec, M1 is unblocked and well-defined:

1. `db_models.py` becomes the single source of truth, **aligned to `fieldmap.py`** — `GroupModel` gets MT5's 44 scalar columns + JSONB for `Commissions`/`Symbols`, `SymbolModel` gets `Point` **and** `TickSize` as separate columns plus the 16 `MarginRates`.
2. Delete `ops/docker/init.sql` and its compose mount; delete `alembic/versions/migration.py` (no `revision`/`down_revision` → Alembic can't build a graph); autogenerate one migration from the models.
3. **Margin level = PERCENT** everywhere: `MarginProfile` defaults `0.8→50`, `0.5→30`; `settings.yaml`; the five ratio call-sites. One `Account.recompute_margin_level()`.
4. Rewrite `group_to_db`/`db_to_group` and `symbol_to_db`/`db_to_symbol` against the aligned models — and have them go **through `infrastructure/mt5/codec.py`**, so the DB row and the MT5 export are the same shape by construction.

Then M2 (config loader + seeder + first-admin bootstrap) gets you to *"set up and run"*, and the MT5 codec means you can seed **straight from a real MT5 export** — 20 groups and 362 symbols, already proven lossless.
