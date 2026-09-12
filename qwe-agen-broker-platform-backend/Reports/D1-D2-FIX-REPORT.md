# D1 + D2 — `margin_level` was persisted-but-never-written, and `/account/info` was unreachable five ways

**Status: COMPLETE.** Test suite **422 → 436 passed / 0 failed**. `ruff` clean.
All proofs green: m8 **18/18**, m9 **14/14**, m10 **19/19**, wire round-trip
**392/392 byte-identical**. New credential-free local E2E proof **15/15**, and the
number that started this: `margin_level` over real HTTP went **`0.0000` → `9261.68`**.

Found by independent verification of the M10 state, not reported by any milestone.
Neither defect was on any report's debt list.

---

## D1 — the column nobody wrote

`accounts.margin_level` is a real column (`account_models.py:98`, `default=0`) with
**three readers**:

1. the MT5 routing context — `RouteCondition.MARGIN_LEVEL` (2001), a *supported*
   condition in M8's taxonomy
2. `GET /api/v1/account/info`
3. the manager `UserGet` + the admin account list

Every margin write path refreshed it — `liquidation_worker:261`, `cancel_order:112`,
`modify_order:136`, `modify_deal:121`, and `tick_margin_pipeline` via
`Account.update_equity` — **except `record_deal`, which is the path every fill takes.**
It set `margin_used`, `margin_free` and `equity` and stopped. Measured straight out
of the database after a real fill:

```
login   balance  equity  margin_used  margin_free  margin_level
768577  10000    9999    107.978      9891.022     0            <-- should be 9260.22
```

### Why it was worse than a display bug

`router.py:203` passed `getattr(account, "margin_level", None)` into
`RoutingRequestContext`. `RoutingRequestContext.margin_level` is `Optional[Decimal]`,
and M8's honesty rule is *"missing context (`None`) ⇒ the condition does not
match"*. A stale `Decimal('0')` is **not** missing, so `_compare` ran a real
comparison against zero:

* *"reject if `MARGIN_LEVEL < 20000`"* rejected **every order a client ever placed**
* *"send to dealers if `MARGIN_LEVEL < 500`"* **always fired**, parking the whole
  book in a dealer queue nobody services

Silent flow diversion — precisely the failure mode M8's `UNSUPPORTED`-skip rule was
written to prevent, arriving through the data instead of the taxonomy.

Stop-out itself was safe: `RiskEngine` reads the freshly computed `MarginSnapshot`,
not the stored field. **That is exactly why 422 tests passed** — no test asserted on
the persisted or served `margin_level`.

### The fix, at three layers

One writer could be fixed and another forgotten later, so the derived value is no
longer trusted anywhere it is consumed:

| Layer | Change |
|---|---|
| **write** | `record_deal` now calls `account.recompute_margin_level()` — the only place the formula lives |
| **SQL read** | `db_to_account` **derives** it from `equity / margin_used`; the column is still written for external SQL consumers but the domain object never trusts it |
| **decision** | `SmartOrderRouter` **derives** it in `_margin_level()`. A routing decision must not depend on some earlier writer having refreshed a cached field. `None` still means missing, so M8's guard keeps working |

All three go through `core.domains.market_data.margin.margin_level`, which already
returned the `MARGIN_LEVEL_UNLIMITED` sentinel (999999) rather than 0 when flat —
*"zero would read as fully exhausted and trigger an immediate stop-out on an account
with no positions."* The query handler had its own eighth hand-written copy of the
formula, and that copy returned `0`. It now calls the same function.

---

## D2 — one endpoint, five independent failures

`GET /api/v1/account/info` could not reach its handler for five reasons, **each of
which was sufficient on its own**:

| # | Failure | Symptom |
|---|---|---|
| 1 | `account_info_query_handler` never registered in the DI container | `Depends()` → `None`, so `if handler:` was always false |
| 2 | routers built `GetAccountInfoQuery(account_login=…)`; the dataclass field was `login_id` | `TypeError` on every call |
| 3 | route wrapped the call in `except Exception: pass` | 1 and 2 invisible; client silently served the JWT snapshot |
| 4 | handler returned `account.login` (**int**) into `AccountInfo.login_id` (**str**) | `ValidationError` → 500 |
| 5 | manager `UserGet` read `.login` / `.group_name` / `.margin` off a **dict** keyed `login_id` / `group` / `margin_used` | `AttributeError` → caught → returned **the manager's own balance and equity** for a query about a client, HTTP 200 |

Failure 5 is the one that would have reached production quietly: a manager terminal
asking about account 768577 received the *manager's* money, with a `warning` in the
log and a `200` on the wire.

This is the defect class M5 fixed on `/account/positions` (defects 14 and 15 —
"never registered" and "`except Exception: pass` → `[]`"). **`/info` was missed, and
it is the endpoint carrying the margin numbers.** Failure 4 is the same
int↔`String(32)` login boundary M5 met on the write side, on the read side.

### The fix

Both routes now use the `/positions` contract:

* **503** when the handler is unwired — a server misconfiguration, not "no data"
* **500** with a logged traceback when the handler fails
* **404** for an unknown login (the handler's `ValueError`)
* **no fallback.** Neither route substitutes somebody else's numbers

Plus: the handler is registered next to `positions_query_handler` in `api/main.py`;
`GetAccountInfoQuery.login_id` → `account_login`, matching its sibling
`GetPositionsQuery`; `login_id` is stringified at the read side, which owns the DTO
shape; and the handler now also returns `credit` and `leverage`, which the manager
schema requires and previously had no source for.

---

## What is proven

**New — `tests/integration/test_d1_margin_level_routing.py` (3, through the real stack):**

```
test_a_flat_account_routes_on_the_sentinel_not_on_zero
    flat account -> MARGIN_LEVEL_UNLIMITED, "< 20000" does NOT match, order FILLS
    (with the stale 0 this rejected a client's very first order)
test_the_fill_writes_a_real_margin_level_and_the_next_request_sees_it
    fill 1 -> account.margin_level == compute_margin_level(equity, margin_used),
             != 0, != sentinel
    fill 2 -> the SAME rule now fires with its configured reason; exactly one deal
             and one position exist
test_a_dealer_diversion_rule_no_longer_fires_on_every_request
    "< 500" -> DEALER does not match a healthy account; the order fills
```

**New — `tests/unit/api/test_d2_account_info_contract.py` (9):**

```
test_the_info_query_speaks_the_same_vocabulary_as_its_sibling   (drift guard: both
    read-side queries declare {account_login}; pins failure 2 from returning)
test_the_handler_uses_the_sentinel_when_flat_not_zero
test_the_handler_supplies_what_the_manager_schema_requires
test_client_info_answers_with_the_real_margin_level
test_client_info_is_503_when_unwired_not_a_silent_snapshot
test_client_info_is_500_when_the_handler_fails
test_client_info_maps_an_unknown_login_to_404
test_manager_userget_returns_the_queried_account_not_the_manager   (pins failure 5:
    asserts balance != the manager's 777)
test_manager_userget_is_503_when_unwired / _maps_an_unknown_login_to_404
```

**Updated — two existing tests whose contracts changed:**

* `test_api.py::test_get_account_info_query_handler` — built the query with
  `login_id=`. **This mismatch is why the bug survived:** the test spoke the
  handler's vocabulary while the routers spoke another, so each looked correct.
* `test_m2_config_plane.py::test_stop_out_state_survives_persistence` — asserted a
  hand-assigned `margin_level` round-trips through the column. `margin_level` is
  *derived* state; the five `so_*` fields that test exists to protect are the
  stop-out machine's real *memory*. The test's own numbers (equity 550, margin 2000)
  already give 27.5, so it now sets the inputs and asserts the derivation. Added
  `test_a_stale_margin_level_column_is_never_served` beside it.

**Live — `work/verify/local_e2e.sh`, no cloud credentials, SQLite + in-process bus:**

```
BUY 0.10 EURUSD -> FILLED at 1.07961
GET /account/info -> balance 10000  equity 9999  margin_used 107.961
                     margin_free 9891.039  margin_level 9261.677828   <-- was 0.0000
stored column     -> margin_level 9262.604088513444                    <-- was 0
15 passed, 0 failed
```

## Numbers

| | before | after |
|---|---|---|
| Tests | 422 | **436 passed / 0 failed** |
| `ruff E9,F63,F7,F82` | clean | clean |
| m8 / m9 / m10 proofs | 18 · 14 · 19 | **18 · 14 · 19** |
| Wire round-trip | 362+20 (script missing) | **392/392** (script rebuilt) |
| Local E2E | did not exist | **15/15** |
| `margin_level` served | `0.0000` | **`9261.68`** |

## Files

**New:** `scripts/patch_d1_d2_margin_level.py`, `scripts/patch_d1_routing_and_tests.py`
(both idempotent, kept for the audit trail per project convention) ·
`tests/integration/test_d1_margin_level_routing.py` ·
`tests/unit/api/test_d2_account_info_contract.py`

**Modified:** `application/commands/record_deal.py` · `core/domains/execution/router.py` ·
`infrastructure/persistence/account_models.py` · `application/queries/get_account_info.py` ·
`api/main.py` · `api/routers/account.py` · `api/routers/manager/main.py` ·
`tests/unit/api/test_api.py` · `tests/unit/persistence/test_m2_config_plane.py`

## Still open (unchanged, now re-verified in code)

* **A-Book does not complete a trade** — `_execute_a_book` sets PLACED and publishes
  `OrderRouted`, never calls `RecordDealHandler`. The M10 `FixLiquidityGateway`
  returns a real FILLED report that is then dropped. ← strongest M11 candidate
* `cli migrate` (alembic) cannot run on SQLite — migration 001 emits PG-only
  `DEFAULT '{}'::jsonb`; the M5 JSONB *type* hook does not cover `server_default`
  text. Dev machines must use `DatabaseManager.create_tables()`.
* m1–m4 proof scripts absent from the repo (round-trip rebuilt; the margin,
  currency, UoW and order-executes proofs still are not).
* Post-trade valuation still reads raw ticks (M7 gap #1).
* `.env` credentials remain in public git history at `39c7eaf2`.

**Pattern worth naming:** all five D2 failures and D1 itself are the same class the
project has been hunting since M4 — *a value that is computed correctly somewhere and
served stale from somewhere else.* The durable defence is the one applied here:
derive at the point of consumption, and make "not wired" a loud 503 rather than a
plausible-looking number.