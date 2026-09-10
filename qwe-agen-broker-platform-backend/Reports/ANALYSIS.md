# Repository Analysis — `rahul82586/references-for-AIs-to-read`

**Analysed:** 2026-09-10 · commit `3a92031` · 31 MB, 220 files
**Method:** full clone → static AST analysis of all 180 Python files → dependency install → **actual test execution** → runtime proof-of-bug scripts → cross-check of code claims against the MT5 reference corpus.

---

## 1. What this repository actually is

It is **not one project** — it is five different things in one repo:

| Folder | What it is | Size | Role |
|---|---|---|---|
| `qwencode/broker-platform/` | **Your actual product** — Python DDD/CQRS broker backend | 180 `.py`, ~18,000 LOC | The thing being built |
| `mt5 sdk single md file/` | MetaQuotes **MT5 SDK** docs (C++ Manager/Server/Gateway/Report/Web API), machine-converted to MD | ~13 MB, 6,000+ source pages | Ground truth for API parity |
| `Single_MetaTrader5Administrator/` | **MT5 Administrator** admin guide (platform setup, components, MT4 migration) | ~3.3 MB | Ground truth for server config |
| `mt5-format-structure/` | **Real MT5 server config export** from a live server (`TCTrader-Live`), UTF-16LE JSON | 3.9 MB, 14 sections | Ground truth for data model |
| `single_centroid_bridge_md_files/` | **Centroid Bridge** manual (LP bridge, makers/takers, risk accounts, give-up, filtration) | ~500 KB | Ground truth for A-book bridging |
| `chat-and-reference-files/` + `code files/` | **AI conversation logs** (Qwen, Gemini, opencode/Nemotron) and per-module extracts | ~2.5 MB | The build history / decisions |

The three files you flagged as most important:
- `latest_chat-MT5 Broker Platform Development (1).md` — 16,662 lines, ~40 turns. The master build log. Duplicated byte-identically inside `chat-and-reference-files/` (same git blob `162970e`).
- `opencode_summery.md` — the Nemotron audit that found the "4 critical math bugs" + the A-book/B-book/matching-engine definitions + the NOP/hedge-trigger model.
- `links-from-opencode-chat-file.md` — ~90 curated reference repos/docs (Rust OMS/LOB, Track360, Soft-FX, Match-Trade, 奥兴科技, MT5 Manager API vendors).

**What you're building:** a Tier-1 institutional brokerage backend that reimplements MT5's rule-based core (Groups as rule engines, hedging/netting, coverage accounts, trade modification, stop-out state machine, Manager API) in Python, with a planned Rust hot-path swap, plus a modern intelligence layer (ClickHouse, LLM agents, portfolio analytics).

---

## 2. 🔴 URGENT — security exposure in this public repo

`mt5-format-structure/*.json` is a **real MT5 Administrator server export** from a server named `TCTrader-Live`. It is committed to a **public** repository and contains:

| Exposure | Count |
|---|---|
| Plaintext gateway/feeder/trading passwords (`GatewayPassword`, `FeedPassword`, `TradingPassword`, `Password`) | **15 non-empty values** |
| Password hashes (`PasswordHash`) | 3 |
| Public trade-server / gateway IPs and ports | several (e.g. a Hetzner and an OVH range) |
| Manager accounts with rights arrays | 9 (`Clients and accounts` → `ConfigManagers`) |
| Internal firewall allow-list | 4 rules (`Security` → `ConfigFirewall`) |
| Full broker commercial config: 20 groups, 362 symbols, 138 subscriptions, 63 reports, routing rules, plugins (FXConnect, DynamicMargin) | complete |

**Recommended actions, in order:**
1. **Rotate every credential** in that export — gateway, feeder, trading, manager. Treat them as compromised.
2. **Delete the folder from the repo** — and note that deleting the file is not enough: it stays in git history (19 commits). Either make the repo private, or rewrite history (`git filter-repo`) and force-push.
3. Also scrub `chat-and-reference-files/api_test_results.md`, which contains a live JWT, the admin login `100001` and the password `password123`.
4. Going forward: if you want the MT5 *schema* as a reference (which is genuinely valuable — see §5), keep the **field names** and strip all **values**. A redacted schema file is safe to publish; a live config export is not.

I have decoded the UTF-16 files to readable UTF-8 in `/home/user/decoded/mt5-format-structure/` for analysis. Secret values are redacted in everything I produce.

---

## 3. Headline verdict on `qwencode/broker-platform`

> **The codebase does not currently import, and the test suite does not currently run.**

The chat logs record *"34/34 unit tests passed"*, *"TWO CRITICAL INTEGRATION TESTS PASSED"*, *"~75% complete"*, *"25/25 endpoints PASS"*. Those statements were true of an **earlier snapshot**. They are **not true of the code in this repo**. The later "MT5-parity enrichment" of the domain layer (Accounts → Instruments → OMS) changed entity constructors and moved fields into nested value objects, and **the callers, repositories, DB models, migrations and tests were never updated to match.**

Measured on this commit:

```
pytest tests                        →  10 collection ERRORS, 0 tests run
  after fixing 7 missing-import bugs  →  12 failed, 40 passed
  tests/unit/api/test_api.py          →  cannot be fixed without adding domain events
import infrastructure.persistence.db_models  →  NameError: BigInteger
import api.main                              →  ImportError: GroupCreated
```

So the honest completion figure is not 75%. It is: **domain models ~good, everything that touches them ~broken.**

This is the single most important thing to understand before asking any further questions: **you have a design/documentation asset that is excellent, and a running system that is currently at zero.** The gap is mechanical, not architectural — it is fixable in a focused pass, and §7 sequences it.

---

## 4. Defects, by severity, with proof

### P0 — Blocks import / startup

| # | File | Defect | Proof |
|---|---|---|---|
| 1 | `core/ports/interfaces.py:9` | `Any` used in signatures but not imported | `NameError: name 'Any' is not defined` — **breaks every module that imports ports, i.e. the whole codebase and all 10 test modules** |
| 2 | `infrastructure/persistence/db_models.py:1` | `BigInteger` used (5 columns) but not imported | `NameError: name 'BigInteger' is not defined` — **the entire persistence layer cannot be imported** |
| 3 | `core/events/domain_events.py` | `GroupCreated`, `GroupUpdated`, `GroupDeleted`, `SymbolCreated`, `SymbolUpdated`, `SymbolDeleted`, `HolidayUpdated`, `HolidayDeleted` are imported by 3 modules but **never defined** | `import api.main` → `ImportError: cannot import name 'GroupCreated'` — **the API server cannot start** |
| 4 | `api/di_providers.py` | `get_di_container` imported by `api/main.py:12` but not defined | ImportError |
| 5 | `core/ports/interfaces.py` | **`IGroupRepository` is never defined**, yet imported by `api/main.py`, `api/di_providers.py`, `application/cache/config_cache.py`, `application/commands/create_group.py`, `infrastructure/.../account_repository.py`, `.../group_repository.py` | ImportError ×6 |
| 6 | `infrastructure/persistence/repositories/group_repository.py` | imports `CommissionProfile`, `ExecutionProfile` from `core.domains.accounts.models` — those classes were renamed/removed during the refactor | ImportError |
| 7 | `application/services/swap_worker.py` | imports `core.domains.oms.models`, which does not exist | ImportError |
| 8 | `application/commands/record_deal.py:10`, `application/services/commission_service.py`, `application/services/execution_orchestrator.py`, `core/domains/execution/router.py`, `core/domains/ledger/engine.py` | `Any` / `Optional` / `Decimal` used without import | NameError at class-definition time |
| 9 | `infrastructure/persistence/repositories/order_repository.py`, `position_repository.py` | `datetime` used in annotations without import | NameError |
| 10 | `infrastructure/persistence/db_models.py` | **`DealModel` and `PositionModel` are each defined twice** with the same `__tablename__` (`deals`, `positions`) — an append-instead-of-merge artefact | even after fixing #2, SQLAlchemy raises `InvalidRequestError: Table 'deals' is already defined` |

The same append-instead-of-merge pattern also produced **duplicate definitions** of `IOrderRepository`, `IDealRepository`, `IPositionRepository` (`interfaces.py` lines 65/108/272 vs 582/621/665), `OrderCancelled` + `OrderModified` (`domain_events.py`), and `get_cancel_order_handler` (`di_providers.py`). In each case the **second definition silently wins**, so the "MT5-accurate" method sets added later shadow the earlier ones — or vice versa. This needs a deliberate merge, not a delete.

### P1 — Runtime correctness (would break in production even after P0 is fixed)

**11. `RiskEngine` was written against an older `Position` API and never updated.**
`core/domains/risk/engine.py` reads `position.side.name`, `position.average_price.value`, `position.id`. The real `Position` entity has `action`, `price_open`, `position_id`.
```
hasattr(Position, 'side')          → False
hasattr(Position, 'average_price') → False
hasattr(Position, 'id')            → False
```
`calculate_margin_level()` therefore throws `AttributeError` on **every** position, which its bare `except Exception` swallows and converts into `has_calculation_error = True` → the account is marked `RiskStatus.BLOCKED` and PnL/margin come back as **zero**. Silent, total failure of the risk engine.

**12. `RiskEngine.detect_margin_call()` / `detect_stop_out()` always crash.**
They read `account.group.margin_call_level`, but those fields live at `account.group.margin.margin_call_level`.
```
detect_margin_call → AttributeError: 'Group' object has no attribute 'margin_call_level'
detect_stop_out    → AttributeError: 'Group' object has no attribute 'stop_out_level'
```
`application/services/risk_worker.py:113,134` calls both. **The risk worker is dead code that throws.**

**13. `has_calculation_error` is never initialised.** In `calculate_margin_level`, it is assigned only inside `except`. If no position errors, line ~180 evaluates `RiskStatus.BLOCKED if has_calculation_error else ...` → `NameError` (or `UnboundLocalError`). The happy path is the one that crashes.

**14. Margin level is expressed in two incompatible units.**

| Location | Convention | Value for equity 10k / margin 25k |
|---|---|---|
| `account.py:117`, `create_order.py:181`, `cancel_order.py:112`, `modify_order.py:136`, `liquidation_worker.py:202` | **ratio** (`equity/margin`) | `0.40` |
| `risk/engine.py:182`, `get_account_info.py:47` | **percent** (`equity/margin*100`) | `40.0` |
| `MarginProfile` defaults, `config/settings.yaml` | **ratio** (`0.8` / `0.5`) | — |
| `alembic/versions/001_initial_schema.py` DB defaults | **percent** (`60` / `30`) | — |
| Real MT5 (`Groups TCTrader-Live.json`) | **percent** (`MarginCall 50.00`, `MarginStopOut 30.00`) | — |

Executed proof: with a deeply underwater account, `RiskEngine`'s percent value `40.0` is compared against fraction thresholds `0.8`/`0.5` → `margin call? False`, `stop out? False`. **No stop-out ever fires on that path.** Conversely, load groups from the DB (defaults 60/30) into the account path and `0.40 < 60` is always true → **every account is permanently in stop-out.** Pick one convention — MT5's is percent — and enforce it in one place.

**15. `Position` cannot be constructed with its own defaults.**
`price_current: Price = field(default_factory=lambda: Price(Decimal('0')))` but `Price.__post_init__` raises on `value <= 0`.
```
Position(position_id=..., action=..., volume=..., price_open=Price(Decimal('1.1')))
→ ValueError: Price must be positive
```
Any code path that builds a `Position` without explicitly passing `price_current` fails — including `db_to_position` mappers for rows with a zero/null current price. `Price` also implements **no arithmetic operators**, so `tick.bid - avg_price` (Decimal − Price) is a `TypeError`.

**16. `get_positions.py` still has the cross-currency PnL bug that the audit declared fixed.**
```python
unrealized_pnl = (tick.bid - avg_price) * vol * Decimal(str(contract_size))
```
No `conversion_rate`, no `quote_currency` — plus the Decimal−Price type error from #15. This is the *client-facing* positions endpoint. The fix was applied to `risk/engine.py` and `tick_margin_pipeline.py` but **not here**.

**17. `liquidation_worker.py:158` hardcodes the conversion rate.**
```python
conversion_rates[symbol_name] = Decimal('1.0')  # Assume same currency for now
```
So worst-loss-first ordering is computed on **unconverted** PnL. On a USD account holding USDJPY and EURUSD, a −100,000 JPY loss (≈ −$667) sorts as worse than a −$900 loss. **The liquidation engine closes the wrong positions first.** The comment says "in production, use RiskEngine" — `RiskEngine.get_conversion_rate()` exists and works; it just isn't called.

**18. `select_positions_for_liquidation()` returns *all* positions, sorted.** It never stops when the margin level recovers. The docstring says "close worst-loss positions first **until margin level recovers**". The loop that would implement the "until" is in `liquidation_service.py`, but the engine method's contract is misleading and `risk_worker.py:141` consumes it directly → **full account liquidation on any stop-out.**

**19. `create_order.py` — market orders get margin computed at price 1.0.**
```python
price_for_margin = command.price if command.price else Decimal('1.0')  # Simplified for market orders
```
For a market order (`price=None`) on EURUSD, notional = `volume × 100000 × 1.0` instead of `× 1.10` → margin **understated**, and for JPY pairs (price ≈ 150) **understated by 150×**. The current tick is available via the market data engine; it is not fetched. This is the same class of bug as the "double-counted margin" the audit caught — reintroduced in a different file.

**20. `create_order.py` — margin is committed inside the lock, the order outside it.**
```python
async with self.risk_service.account_lock(...):
    ...
    await self.account_repo.save(live_account)   # margin reserved & COMMITTED
# 5. Persist order (outside lock ...)
saved_order = await self.order_repo.save(order)  # if this fails → margin leaks forever
```
No compensating action, no unit of work, no saga. Any exception between the two commits permanently strands client margin. The `UnitOfWork` that was built for exactly this is **not used here** (only `record_deal.py` uses it).

**21. `UnitOfWork` cannot work as written.**
```python
self.orders = SqlOrderRepository()      # TypeError: __init__ missing 'session_factory'
self.deals  = SqlDealRepository()       # TypeError
self.positions = SqlPositionRepository()# TypeError
```
Every repository requires `session_factory`. And even if constructed, they are **not given the shared session** — each method does `async with self.session_factory() as sess`, opening its own connection and committing independently. `record_deal.py` works around this by introspecting `find_by_id.__code__.co_varnames` for a `session` parameter — a fragile hack that only covers `save`/`find_by_id`, not the rest. **The atomicity claim ("✅ Atomic via Unit of Work") is not real.**

**22. Margin is calculated in two places that can drift.** `Group.calculate_margin()` (correct MT5 form: `notional / effective_leverage × margin_rate`) and an inline recomputation in `create_order.py:151`. Only one is tested. `Group.calculate_margin` also ignores per-account leverage (`account.effective_leverage()`) and symbol-level max leverage — MT5 uses the *minimum* of account, group and symbol leverage.

**23. `get_conversion_rate` handles only direct and inverse pairs.** `EURJPY → USD` needs `EURUSD`; the code tries `JPYUSD` then `USDJPY` and raises `CurrencyConversionError`. It has **no cross-rate triangulation**, which is precisely the case `opencode_summery.md` documented. Both lookup blocks are wrapped in `except Exception: pass`, so a genuine feed error is indistinguishable from a missing pair.

**24. Two of the four original audit bugs were never fixed at all.**

| Audit bug | Status in this commit |
|---|---|
| 1. Double-counted margin | ✅ **Fixed** — `Group.calculate_margin` uses `notional / leverage`. ⚠️ but reintroduced differently in `create_order.py` (#19) |
| 2. Cross-currency PnL | 🟡 **Partially fixed** — `risk/engine.py` + `tick_margin_pipeline.py` yes; `get_positions.py` (#16) and `liquidation_worker.py` (#17) no |
| 3. Mock feed quantises to spread, not tick size | ❌ **Not fixed** — `mock_feed.py:65` still `.quantize(spread)` |
| 4. Hardcoded secrets | ❌ **Not fixed** — `jwt_handler.py:12` `SECRET_KEY = "BROKER_PLATFORM_SECRET_KEY_CHANGE_IN_PRODUCTION"`; `admin_dependencies.py:10` `os.getenv("ADMIN_API_KEY", "ADMIN_SECRET_KEY_12345")`. Worse, `tests/unit/api/test_api.py:77` asserts against that default, so the test *locks in* the insecure behaviour |

**25. `alembic/versions/migration.py` has no `revision` / `down_revision` variables** — only prose in the docstring (`Revises: previous_revision`, `Create Date: 2026-01-XX`). Alembic cannot build a revision graph → `alembic upgrade head` fails. And `001_initial_schema.py` still creates `symbols.margin_initial_percent` / `margin_maintenance_percent` — fields the `Symbol` entity **no longer has** (replaced by the 16-field `MarginRates`). Schema and domain model have diverged.

**26. `alembic.ini:5`** hardcodes `postgresql+asyncpg://user:password@localhost:5432/broker_db`.

**27. `api/main.py`** — `CORS allow_origins=["*"]` combined with `allow_credentials=True` (browsers reject this pairing; it signals the intent is wrong), and deprecated `@app.on_event("startup")` instead of a lifespan handler.

### P2 — Structural / wiring

**28. The A-book / B-book execution path is never started.** `ExecutionOrchestrator` is complete and well-designed (SOR → A_BOOK gateway / B_BOOK internal fill + coverage update / dealer queue / reject). It is wired only in `application/subscriptions/execution_subscriptions.py` — and **nothing imports that module.** `grep` for it outside itself returns zero hits. So orders are created, margin is reserved, and then **nothing ever executes them.**

**29. The liquidation worker is never started.** `LiquidationWorker` subscribes to `StopOutEntered` — but it is instantiated **only in tests**. There is no production wiring in `api/main.py`, `di_providers.py` or `cli/`. **Stop-outs are detected and then nothing acts on them.**

**30. `RiskWorker` is dead code** (see #12) and is also never instantiated outside tests.

**31. `ConfigCache`** — the "MT5-like speed" layer from the last chat turn — is initialised in `api/main.py` startup, which cannot be reached because of #3/#4/#5. It also depends on the eight undefined domain events.

**32. Six tests are empty or assertion-free:**
- `tests/integration/test_margin_loop.py:366` `test_cross_currency_pnl_in_margin_loop` — body is literally `pass`, with the comment *"we'll skip it and focus on the main test above"*. It reports **PASSED**. This is the *only* end-to-end cross-currency test, and the chat log cites it as evidence the feature works.
- `test_event_bridge_routes_tick`, `test_tick_ask_greater_than_bid`, `test_empty_orderbook_to_tick_raises`, `test_tick_ingestor_reconnect_loop`, `test_stale_quote_rejection` — statements but **zero assertions**.

**33. Test/domain drift.** 8 of the 12 real failures are `TypeError: __init__() got an unexpected keyword argument` — tests still pass `Symbol(margin_initial_percent=...)`, `TradingSession(start=...)`, `Group(margin_call_level=..., leverage_default=...)`, `CommissionTier(volume_from=...)`, and expect `to_dict()["symbol_overrides_count"]`. The tests encode the **pre-refactor** API.

**34. Two genuine commission bugs** surface once the constructor mismatches are set aside:
- `Group.calculate_commission('EURUSD', volume, deal_value)` returns `Decimal('0')` where `7.00` is expected.
- Returns `5.00` where `20.00` is expected.
The `type` discriminator (`per_lot` / `per_deal` / `percent`) falls through to `else: commission = 0`, and `return` inside the loop means **only the first matching rule is ever applied** — MT5 stacks commission rules.

**35. `tick_margin_pipeline.process_tick` is O(N) DB round-trips per tick:** 1 symbol read + N account reads + N × all-position reads + N account writes + N × M position writes. Its own docstring admits this should be cache-backed. At 10k TPS this is the bottleneck, and `ConfigCache` (which would fix the read side) is unreachable (#31).

**36. `intelligence/` is 100% empty `__init__.py` files** — 8 packages, zero implementation. Consistent with the "10%" in the status report, but worth stating plainly: ClickHouse analytics, LLM agents, VaR/Greeks, news NLP, screening and reporting **do not exist yet**. Also empty: `infrastructure/cluster`, `gateways`, `engines`, `notifications`, `api/fix`, `api/grpc`, `api/client`, `core/domains/backoffice`, `core/domains/identity`.

**37. `infrastructure/feeds/lp_feed.py`** raises `NotImplementedError("Real LP feed integration is pending.")` for both methods — so there is **no real LP connectivity**; only `mock_feed.py` works (and it has bug #24.3).

**38. Cosmetic but telling:** `core/domains/risk/engine.py` contains **one bare `\r`** mid-file (line ~214) where a `\n` should be. Python's universal-newline handling absorbs it at import time, but any tool doing byte-level patching will corrupt the file. Given the project's own "trailing space / whitespace contamination" audit task, line endings deserve a repo-wide normalisation pass + `.gitattributes`.

---

## 5. The reference corpus — quality and how to use it

This is the strongest asset in the repo, and it is under-used by the code.

**`mt5-format-structure/` is the most valuable file set you have**, because it is *reality* rather than documentation. Decoded contents:

| Section | Records | Why it matters |
|---|---|---|
| `Symbols` | **362 symbols × 121 fields** | The complete real symbol schema: `CurrencyBase/CurrencyProfit/CurrencyMargin` (+digits each), `CalcMode`, `ExecMode`, `FillFlags`, `ExpirFlags`, `OrderFlags`, full `MarginInitial*/MarginMaintenance*` matrix (16 variants), `MarginHedged`, `MarginLiquidity`, `SwapRate{Sunday..Saturday}`, `SessionsQuotes`/`SessionsTrades` (7×arrays), `REFlags/RETimeout`, `IECheckMode/IETimeout/IESlipProfit/IESlipLosing/IEVolumeMax`, `Filter{Soft,Hard,Discard,SpreadMax,SpreadMin,Gap,GapTicks}`, `QuotesTimeout`, `VolumeMinExt/MaxExt/StepExt/LimitExt` (integer-scaled), `PriceLimitMax/Min`, `PriceSettle`, `AccruedInterest`, `Splice*`, `ISIN`, `CFI`, `Sector`, `Industry`, `Country`, `Basis` |
| `Groups` | **20 groups × 44 fields** + nested `Commissions` (12 fields + `Tiers`) + `Symbols` overrides (**65 fields each**) | Real group names: `demo\Standard`, `demo\SWAPFree`, `demo\Challenge`, `managers\administrators`, `managers\dealers`, `managers\API`, `real\real`, `real\real-SF`, `real\real-A`, `preliminary`. Real values: `MarginMode 2`, `MarginSOMode 0`, `MarginFreeMode 1`, `MarginCall 50.00`, `MarginStopOut 30.00`, `TradeFlags 87`, `PermissionsFlags 22`, `NewsMode 2`, `LimitHistory/LimitOrders/LimitSymbols/LimitPositions/LimitPositionsVolume` |
| `Subscriptions` | 138 | Manager API subscription model |
| `Reports` | 63 | Report definitions |
| `Automation` | 27 | Scheduled server tasks |
| `Routing` | 2 (`dealer`, `Auto Execution`) | **Real MT5 routing rules**: `Mode`, `Request` bitmask, `Type`, `Action`, `Conditions[]`, `Dealers[]` — the pattern your `RoutingRule` should follow |
| `Gateways` | 3 | LP gateway config incl. `Translates[]`, `Symbols[]`, `Groups[]`, `State`, reconnect/timeout params |
| `Data Feeds`, `Network Cluster`, `Plugins`, `Security`, `Holidays`, `Charts & Ticks`, `Clients and accounts` | 4/3/3/4/1/2/9 | Cluster topology, firewall, manager rights |

**Coverage gap, quantified.** Your `Symbol` entity has **42 fields vs MT5's 121**. Your `GroupSymbolOverride` has **12 fields vs MT5's 65**. Your `Group` has 19 top-level fields (+nested VOs) vs MT5's **44 + Commissions + Symbols**. The highest-value missing pieces, in priority order:

1. **Per-day swap rates** (`SwapRateSunday..Saturday`) — you have `swap_long/swap_short/swap_3day` but no per-day curve. The chat log itself flagged this as Priority 1. The real export confirms MT5 stores all seven.
2. **Instant Execution controls** (`IECheckMode`, `IETimeout`, `IESlipProfit`, `IESlipLosing`, `IEVolumeMax`) — needed for the "stale quote / slippage rejection" scenario in your battle-test list.
3. **Request Execution controls** (`REFlags`, `RETimeout`), `QuotesTimeout`, `FillFlags`, `ExpirFlags`, `OrderFlags`.
4. **`CurrencyProfit` and `CurrencyMargin`** — you have `base_currency`/`quote_currency` only. MT5 distinguishes three, and **margin currency ≠ quote currency** is exactly what makes cross-currency margin hard. This is a root cause of bug #16/#17/#23.
5. **`MarginHedged` / `MarginLiquidity` / `MarginFlags`** — required for hedged-margin mode (your Scenario 2) and for the "Margin Profile Consolidation" gap the chat log identified.
6. **Tick filters** (`FilterSoft/Hard/Discard/SpreadMax/SpreadMin/Gap`) — the "stale/spike quote rejection" logic; `market_data/engine.py:76` still has `# TODO: Phase 11 - Implement spike filter`.
7. **Integer-scaled volume fields** (`VolumeMinExt`, `VolumeMaxExt`, `VolumeStepExt`, `VolumeLimitExt`) — MT5 stores volumes as scaled integers to avoid float error. Directly relevant to your "float contamination" audit task.
8. **Commission `Tiers`** with the real 12-field schema (`Mode`, `RangeMode`, `ChargeMode`, `TurnoverCurrency`, `EntryMode`, `ActionMode`, `ProfitMode`, `ReasonMode`) — your `CommissionRule` has 9 flat fields and the tiering test already fails (#34).

**The other corpora:** the MT5 SDK MD dump (~13 MB, 6,000+ pages across Manager/Server/Gateway/Report/Web API, Configuration-Interfaces 3.1 MB, Database-Interfaces 2.7 MB) is complete and well-converted — `converted-file-count.md` shows the exact page counts per section. `Single_MetaTrader5Administrator/Platform-Setup.md` is 2.1 MB and is the authoritative source for the *Administrator UI* semantics behind every JSON field above. `single_centroid_bridge_md_files/` (24 chapters: makers, takers, risk accounts, risk users, give-up rule, filtration pool, action scheduler, stale prices, trade copier, 2FA, monitoring, reports, API) is the best available reference for the **A-book bridge layer** you haven't built — particularly `45-stale-prices.md`, `42-giveup-rule.md`, `43-filtration-pool.md` and `32-risk-accounts.md` (coverage accounts).

---

## 6. What is genuinely good

Worth saying clearly, because the P0 list above could read as "start over". **Don't.**

- **The architecture is correct and consistently applied.** `core/` is genuinely framework-free — no SQLAlchemy, no FastAPI, no Redis imports in the domain layer. Ports-and-adapters is real, not aspirational. The Python→Rust swap story is credible *because* of this discipline.
- **`Decimal` discipline is real.** Money/Price/Volume value objects, `Numeric(18,8)` / `Numeric(20,8)` columns, no `float` in the financial path. The `Price`/`Volume` invariant checks are the right instinct (the `Price > 0` rule just needs a `Price.zero()` escape hatch, #15).
- **The domain modelling of MT5 is unusually faithful** for a from-scratch build: `Account` carries the full stop-out state fields (`so_activation`, `so_time`, `so_level`, `so_equity`, `so_margin`), `FreeMarginMode` with `USE_PL`/profit-and-loss variants, `SOActivation`, `TradeFlags` as a bitwise IntFlag, `MarginRates` with all 16 initial/maintenance × buy/sell × market/limit/stop/stop-limit combinations. That last one **matches the MT5 export field-for-field** — someone did the work.
- **`Position.apply_deal()`** correctly implements hedging vs netting, including the reversal case (`_create_opposite_position`, `_create_opposite_position_with_remaining`) and `close_by()`. This is the hardest part of an OMS and it is thoughtfully done.
- **`TickMarginPipeline`** is the best-designed component: correct bid/ask valuation side per MT5, conversion-rate lookup with an explicit typed error, `evaluate_margin_state()` as a proper state machine emitting entered/exited transitions, persistence then event publication. It is also the only path that is actually tested end-to-end.
- **`SmartOrderRouter`** implements the Track360/Soft-FX NOP model faithfully — 70% warn / 85% auto-hedge to A-book / 95% block — with priority-ordered rules, wildcard group/symbol filters and LP-priority fallback. (Missing: the 100% force-close tier, and client risk profiling TOXIC/PROFITABLE/RETAIL/PRO from `opencode_summery.md`.)
- **`ExecutionOrchestrator`** has the right shape: A-book → gateway, B-book → internal fill + coverage exposure update, dealer → queue with 30s timeout, else reject.
- **Test intent is excellent.** The scenario names are the right ones (`test_account_lock_prevents_double_spend`, `test_stale_quote_rejection`, `test_cross_currency_pnl_missing_rate_raises_error`, `test_liquidation_worker_closes_worst_loss_first`, `test_group_and_account_decimal_precision`). They are failing on constructor signatures, not on concepts. Fixing them is a few hours, not a rewrite.
- **The reference corpus is exceptional** — I have not seen a better private MT5 knowledge base. §5 is a map of it.

---

## 7. Recommended remediation sequence

Ordered so that each step produces something verifiable. Steps 1–3 are "make it true that the code runs"; 4–7 are "make it true that the code is right".

**Step 1 — Restore importability (~1 day, mechanical).**
Fix #1–#10. Concretely: add `Any` to `interfaces.py` and the five other typing imports; add `BigInteger` to `db_models.py`; **merge** (don't delete) the duplicate `DealModel`/`PositionModel`/`IOrderRepository`/`IDealRepository`/`IPositionRepository`/`OrderCancelled`/`OrderModified`/`get_cancel_order_handler` pairs; define `IGroupRepository` in `core/ports/interfaces.py`; add the eight missing group/symbol/holiday domain events; point `group_repository.py` at the current VO names; fix `swap_worker.py`'s import. **Gate: `python -c "import api.main"` succeeds and `pytest` collects all 10 modules.** Add this as a CI job — a repo that cannot import should never have been mergeable.

**Step 2 — Add a compile/collect gate (~1 hour, prevents recurrence).**
`python -m compileall -q .` + `pytest --collect-only -q` + `ruff check` + `mypy core/` in CI. Every defect class in P0 is caught by one of these in under a second. Also add `.gitattributes` (`* text=auto eol=lf`) and normalise, to close #38.

**Step 3 — Resynchronise tests with the domain (~1 day).**
Fix the 8 constructor-signature failures (#33) and delete or `@pytest.mark.skip(reason=...)` the six assertion-free tests (#32) so a green suite means something. **Gate: `pytest` runs, 0 errors, and every passing test has ≥1 assertion.**

**Step 4 — Pick ONE margin-level convention and enforce it (~half day).**
Recommendation: **percent**, matching MT5 (`MarginCall 50.00`, `MarginStopOut 30.00`). Change `MarginProfile` defaults `0.8→80`, `0.5→50`; change `settings.yaml`; change `account.py:117`, `create_order.py:181`, `cancel_order.py:112`, `modify_order.py:136`, `liquidation_worker.py:202` to multiply by 100; keep the DB defaults at 60/30 (already percent). Add a single `Account.recompute_margin_level()` used by all callers so the formula exists once. **Gate: a test that builds an account at 40% margin level with MT5-real 50/30 thresholds and asserts MarginCall fires; another at 25% and asserts StopOut fires.**

**Step 5 — Reconcile `RiskEngine` with the real entities (~1–2 days).** This is the highest-value correctness work.
Rename to `position.action` / `position.price_open` / `position.position_id` (#11); read thresholds via `account.group.margin.*` (#12); initialise `has_calculation_error = False` before the loop and **stop swallowing exceptions** — a position that cannot be valued must fail the calculation loudly, not silently zero out margin (#13); use `account.effective_leverage()` and honour symbol max leverage; add maintenance margin and hedged margin; include `credit` in equity (MT5: `equity = balance + credit + profit`, and `Account.update_equity` already does this correctly — `RiskEngine` does not); add cross-rate triangulation to `get_conversion_rate` (#23) and remove the `except Exception: pass` blocks. **Gate: the four validation rows from `opencode_summery.md` — EURUSD/USD $10.00, USDJPY/USD ~$6.67, EURJPY/USD ~$6.67, GBPAUD/USD ~$6.50 per pip per lot — as real assertions.**

**Step 6 — Fix the execution path and actually start it (~2 days).**
Fetch the live tick for market-order margin instead of `Decimal('1.0')` (#19). Wrap margin-reserve + order-persist in the unit of work, and fix `UnitOfWork` to pass the shared session into repositories (#20, #21) — the current form is a TypeError at runtime. Route `create_order` through `Group.calculate_margin()` so there is one margin formula (#22). Then **wire `execution_subscriptions` and `LiquidationWorker` into `api/main.py` startup** (#28, #29) — without this, nothing executes and nothing liquidates. Replace `conversion_rates[...] = Decimal('1.0')` in the liquidation worker with a real `RiskEngine.get_conversion_rate()` call (#17), and implement "close until recovered" (#18).

**Step 7 — Close the remaining audit items and the schema drift (~1 day).**
`mock_feed.py` → quantise to `symbol.tick_size` (#24.3). Secrets → env-only with a hard failure if unset, and fix the test that asserts the insecure default (#24.4). Give `migration.py` real `revision`/`down_revision` and regenerate the schema from the current models — `symbols.margin_initial_percent` no longer exists in the domain (#25). Externalise the `alembic.ini` URL (#26). Tighten CORS (#27). Fix the two commission bugs (#34).

**Then, and only then, resume feature work** — Manager query/config endpoints, Reports, the Centroid-style LP bridge (`infrastructure/gateways/`, `feeds/lp_feed.py`), FIX, cluster, and the `intelligence/` layer.

**Realistic re-estimate:** core backend is not 95%. Accounting for #11–#23 (the risk/execution path does not function) and #28–#31 (nothing is wired), I'd put **runnable-but-unproven at ~35–40%**, with the caveat that the *design* is far further along than the *code* — the domain models and reference understanding are genuinely at 80%+.

---

## 8. Workspace artefacts

| Path | What |
|---|---|
| `/home/user/refs/` | Full clone of the repo (31 MB) |
| `/home/user/decoded/mt5-format-structure/` | The 14 MT5 config exports decoded from UTF-16LE → readable UTF-8 JSON |
| `/home/user/work/bp/` | **Scratch copy** of `broker-platform` with the 7 import bugs patched, used to get the test suite to run. Your repo is untouched. |
| `/home/user/ANALYSIS.md` | This report |

Test run command used:
```bash
cd /home/user/work/bp
PYTHONPATH=/home/user/work/bp python3 -m pytest tests -q --ignore=tests/unit/api/test_api.py
# → 12 failed, 40 passed
```
