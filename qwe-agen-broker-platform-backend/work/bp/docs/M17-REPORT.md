# M17 — F8/F9 rebuilt + step 8: the admin read plane (session 7, 2026-09-14)

**Scope delivered:** the F8/F9 fix, REBUILT from session 6's transcript (its
commit died with that sandbox and never reached GitHub) · `find_page` SQL-level
paging on all six repositories · the eight step-8 read queries · the admin
read plane: paged accounts/clients/managers lists, the six-tab account
detail, the client detail + `/schema`, and the B2 trade reads
(`/admin/{positions,deals,orders,orders/history}`) · `client_fields.yaml`
grounded in IMTClient's 63 real accessors · a new proof gate.

**Gates after this milestone:** `pytest tests` **788 passed / 0 failed /
0 skipped** (740 on GitHub HEAD at session start; +19 F8/F9, +29 step 8) ·
ruff E9,F63,F7,F82 **clean** · round-trip **392/392** · m2 ✅ · m8 18/18 ·
m9 14/14 · m10 19/19 · m11 39/39 · m4 weekend-skip (correct — the sandbox
clock is Sunday UTC) · p1_migration **24/24** · p1_identity **59/59** ·
p1_account_creation **72/72** · p1_manager_creation **80/80** ·
**p1_proof_read_plane 55/55 (NEW, in CI)** ·
**f8f9_proof_live_position_get 10/10 against live Neon** (not in CI — needs
DATABASE_URL).

---

## 0. What happened before anything was written

Session 6 ended mid-step-8. Its tail — the F8/F9 fix (committed in that
sandbox, **755 passed**, proven live) and the first paged-read work — was
never pushed; GitHub HEAD `475c14b` still had the broken `PositionGet`. The
full session-6 transcript survived as the user's HTML attachment, so the fix
was **rebuilt to its recorded design**, not reinvented: shared serializer,
cross-account handler, HTTP-level regressions, live-Neon proof.

Everything else was re-verified before building (session 7): all four P1
proofs and the whole M-series re-run green on `475c14b`; live Neon re-probed
— every PROJECT-STATE-v6 claim reproduced exactly (18 tables, accounts 67
cols / 45 rows, clients **0 rows**, `login_counters` EMPTY, 31 open positions
/ 24 NULL `price_current`, 37 IN / 9 OUT deals, 9 breaks OPEN, `bars` = 0,
**D16 live: 24/45 accounts**, deltas `+800.70 ×10, −749.20 ×9, +798.90 ×2,
+2.10, −0.50, +2.30`); CI green on `dd27011` and `475c14b`; the `.env` at
`39c7eaf2` still fetchable (rotation remains a user action).

**Workspace credential sweep (user request).** The session workspace was
scanned and scrubbed: `live_env.txt` deleted; the raw session-2/3 captures
deleted; the session-6 attachment and both extracted transcripts redacted
(47/108/170/10/5/4 secret values → `REDACTED_*` placeholders); final sweep
**0 remaining secret values**. The repo clone itself carries no real
credentials in tracked code — only synthetic fixtures in
`test_m5_deployment.py` and the documented public-repo leak (rotation = the
standing P0 user action). **Why this mattered beyond hygiene:** the chat
input filter was rejecting messages containing secret-shaped strings
(`Content Security Warning`); with the workspace clean, session captures can
be handled again without tripping it. Rule going forward: live proofs read
DATABASE_URL from the environment at run time — never a workspace file, never
echoed.

---

## 1. F8/F9 — `PositionGet` rebuilt (`07c0c27`)

The endpoint returned `[]` + `ticket=0` against a live book of 31 open
positions — four stacked faults, all hidden by one blanket `except Exception`:

1. the route built `GetPositionsQuery(account_login=login, symbol=symbol)` —
   the client-plane query declares **no** `symbol` field and requires
   `account_login: str`, so EVERY call raised TypeError;
2. the client-plane handler returns **dicts**; the route then read entity
   attributes (`.action.value`, `.price_open.value`) off them;
3. `ticket=int(position_id) if isdigit() else 0` — `position_id` is a UUID or
   `{login}_{SYMBOL}_{hex}`, never numeric; the real venue ticket lives in
   `external_id` (**F9**);
4. `price_current` is Optional on the entity (None until the first tick — 24
   of the 31 live rows) and the required `.value` access raised on exactly
   those rows.

**The fix, per session 6's recorded design:**

* `GetManagerPositionsQuery` + `GetManagerPositionsQueryHandler` — the
  manager plane's cross-account read, dispatching to the repository's OWN
  SQL-level methods (`get_open_positions` / `get_positions_by_account` /
  `get_by_symbol` / `get_by_account_and_symbol`). The client-plane handler is
  untouched: it values ONE account through the RiskEngine and refuses without
  one — correct for its purpose, wrong for the book.
* `position_to_info()` — the ONE Position→PositionInfo serializer (D18's
  lesson: never two builders of one shape). Volume/Price `.value`, Money
  `.amount`; Optional prices stay `null` — never 0, never `price_open`
  (inventing a current price the market never sent is the D13/D16 class).
* `PositionInfo` gains `position_id` (the canonical row key — a UI keying by
  `ticket=null` collapses rows; keying by position_id cannot) and honest
  Optional `ticket`/`price_current`.
* The `/account/positions` error contract (M5/D2): **503** unwired, **500** on
  failure, `[]` ONLY for a genuinely flat book. An empty list is an answer;
  it must never be an error in disguise.

**Proven:** 19 HTTP-level regressions (each fails against the old code) +
`scripts/f8f9_proof_live_position_get.py` **10/10 on live Neon**: the whole
31-row book across 30 logins, 24 honest `null` price currents, filters
matching SQL counts, and a poisoned handler producing the route's 500 — not
`[]`. (One design note: the proof drives the route coroutine directly in one
event loop; TestClient's portal thread has its own loop and asyncpg binds
connections to theirs — the HTTP transport itself is covered by the 19 unit
tests.)

---

## 2. Step 8 — the admin read plane (`69915d7`)

### 2a. Repository layer: `find_page`

Declared on all six ports (the extended-surface pattern: default refuses
loudly) and implemented in SQL on all six repositories:

```
find_page(limit=100, offset=0, **filters) -> (rows, total_matching)
```

* WHERE/LIMIT/OFFSET/COUNT push into SQL. `total` counts ALL matches, not the
  page — a pager whose total is the page size is a lie.
* **Both test suites poison `find_all`** on every double and every real repo
  instance: if a route reaches for load-everything-then-slice, the test
  explodes. The trap cannot come back.
* Accounts order **numerically** (`CAST(login AS BIGINT)` — legal on
  PostgreSQL and SQLite): lexicographic order serves 10, 1000, 885863, 9.
* Filters: accounts (group_name, account_type, enabled — the `is_enabled`
  MIRROR column, correct for legacy `rights=0` rows AND new ones, because
  step 5 made the mask write through), deals (account_login, symbol, entry),
  orders (account_login, symbol, state, history tri-state), positions
  (account_login, symbol, include_closed). An **unknown filter is refused**
  (`ValueError`), never ignored — silently dropping a filter serves an
  unfiltered page that looks filtered.
* Orders' `history` is a TRI-STATE: None = all, False = active
  (STARTED/PLACED/PARTIALLY_FILLED), True = terminal
  (CANCELLED/FILLED/REJECTED/EXPIRED). A `state` contradicting `history` is
  refused — serving the intersection as an empty page would look like a
  filter result.

### 2b. Query layer

The plan's eight files: `list_accounts`, `list_clients`, `list_managers`,
`list_deals`, `list_orders`, `list_positions`, `get_account_detail`,
`get_client_detail` — thin handlers over the ports; unwired repo = raise
(route turns it into 503). Serialization stays in the API layer, one function
per wire shape.

### 2c. HTTP: three read routers + the managers list

```
GET /api/v1/admin/accounts            RIGHT_ACC_READ (25)   paged, filtered, bare array + X-Total-Count
GET /api/v1/admin/accounts/{login}    RIGHT_ACC_READ        the six-tab payload
GET /api/v1/admin/clients             RIGHT_CLIENTS_ACCESS (96)
GET /api/v1/admin/clients/schema      RIGHT_CLIENTS_ACCESS  client_fields.yaml (before /{client_id})
GET /api/v1/admin/clients/{id}        RIGHT_CLIENTS_ACCESS
GET /api/v1/admin/positions           RIGHT_TRADES_READ (29)
GET /api/v1/admin/deals               RIGHT_TRADES_READ     (filters: login, symbol, entry)
GET /api/v1/admin/orders              RIGHT_TRADES_READ     (filters: login, symbol, state, history)
GET /api/v1/admin/orders/history      RIGHT_TRADES_READ     terminal states, pinned
GET /api/v1/admin/managers            RIGHT_CFG_MANAGERS    the list step 7 lacked (before /{login})
```

45 → **52 OpenAPI paths**.

**Decisions, each deliberate:**

* **Bare arrays + `X-Total-Count` header**, not an envelope. The UI does
  `setPositions(data)` today — an envelope breaks every page at once — and
  MT5's own Web API returns bare arrays. `limit`/`offset` page.
* **Reads are gated by the READING rights** (ACC_READ / CLIENTS_ACCESS /
  TRADES_READ — the SDK's own names), the writes keep their stronger step-6/7
  bits. A read bit never opens a write plane (pinned: ACC_READ manager → 403
  on `POST /accounts`), and `must_change_password` blocks reads too (the
  step-3 rule, unchanged).
* **The six-tab account detail** follows ACCOUNT-GROUP-CREATION-SPEC §2b
  exactly, `rights` DECODED server-side (names, bits, labels, tabs,
  `inverted` flags, granted state) — the 0/1 problem stops at the API.
  `subscriptions` is an honest `[]`: the platform models no subscriptions,
  and inventing a shape the domain cannot fill is how schemas start lying.
* **Credential material never serializes.** Security tabs are booleans
  (`master_password_set`); a proof check sweeps the whole response text for
  the seeded hash. The client's four password columns are the DEPRECATED
  location (step 5) and are documented as such in the schema.
* **The F9 rule extends to deals and orders**: `ticket` = the venue's number
  from `external_id` or `null`, with `deal_id`/`order_id` as canonical keys.
  `external_ticket()` — one function, one rule.
* **Mount order** keeps every lesson: the step-6 write router first (its
  `GET /accounts/schema` keeps the ACC_MANAGER gate), the read routers next,
  `admin_router` last — so the legacy `find_all()[:limit]` `GET /accounts`
  is **shadowed, not deleted** (removing it is a separate decision; two
  duplicate-operation-id warnings in OpenAPI are the visible trace, and the
  new handlers are renamed `*_paged` to keep them unique).
* **`Client.status` is a domain ENUM** (`ClientStatus`, its own value mapping
  — not the raw SDK ordinals); the payload serves value AND name, and the
  yaml descriptor expands it **from the domain code** at read time, so the
  schema endpoint cannot drift.

### 2d. `client_fields.yaml`

30 descriptors over the 32 ClientModel columns, each with the exact IMTClient
accessor (`PersonName`, `PersonMiddleName`, `CompanyName`, `AddressCountry/
State/City/Postcode/Street`, `ContactPhone/Email/Language`,
`PersonDocumentNumber`, `LeadSource/LeadCampaign`, `ClientExternalID`,
`ClientStatus`, `RecordID`) — read member-by-member from `Include.md`
(IMTClient at 6067: 63 const accessors), not guessed. `mt5: null` marks our
additions (mqid, comments, timestamps). The unmodelled SDK families
(Person* demographics, Company* registry, Contact* extras, Experience*,
ClientType/KYC/Compliance/AssignedManager) are listed **honestly at the
bottom** rather than as `modelled: false` rows — clients have no wire import
in the live export, so unlike groups there is no quarantine behind them.

---

## 3. 🟠 D20 (NEW, found this session, NOT fixed — needs migration 010)

`Order.price_order` is **Optional on the entity** (M10: "None means not yet
priced"; the old `Price(Decimal('0'))` default crashed the positivity guard)
but the **column is NOT NULL** and `order_to_db` dereferences `.value`
unconditionally — an order without a price cannot be stored, and the read
path can never see None. Production never hits it (market orders carry the
request price; fills stamp the execution price — M7), but it is the same
entity/schema disagreement class as D19. The honest fix is a nullable column
in migration 010 (which the gateway config plane needs anyway) + a
None-tolerant mapper pair. Recorded here so it is not rediscovered; the SQL
paging test documents why its fixture supplies a price.

---

## 4. Session-infrastructure findings (the death protocol, amended)

* **`.git` does not survive turn boundaries** in this workspace — not just
  session death. Session 7's first F8/F9 commit evaporated between messages;
  the working tree survived and the commit was recreated (`07c0c27`).
  Protocol amendment: **bundle after EVERY commit** (the bundle file lives at
  `work/patches/repo-full-history.bundle` and survives as a plain file), and
  ask the user to push at the first natural pause, not at the milestone end.
* **Installed packages do not survive turns either** — `pip install -e
  ".[dev]"` must re-run each turn before gates.
* **The chat input filter blocks messages containing secret-shaped strings**
  (the `Content Security Warning` the user hit). Keep credentials out of
  pasted text; the workspace sweep above removed the standing sources.
* D17 confirmed again (literal `/home/user` in heredocs → `"$ARENA_WORKSPACE"`
  SyntaxError; `HOME=/tmp`). All new scripts resolve paths at runtime.

---

## 5. New / changed files

```
NEW  application/queries/{list_accounts,list_clients,list_managers,
                          list_deals,list_orders,list_positions,
                          get_account_detail,get_client_detail}.py
NEW  api/routers/admin/reads.py               the three read routers + serializers
NEW  config/schemas/client_fields.yaml        30 descriptors, IMTClient-grounded
NEW  scripts/p1_proof_read_plane.py           55 checks (in CI)
NEW  scripts/f8f9_proof_live_position_get.py  10 checks on live Neon (out of CI)
NEW  scripts/patch_step8_paging.py            the idempotent repo-layer patch
NEW  tests/unit/api/test_f8f9_position_get.py            19 tests
NEW  tests/unit/api/test_step8_read_plane.py             22 tests
NEW  tests/unit/persistence/test_step8_sql_paging.py      7 tests
MOD  application/queries/get_positions.py     + manager-plane query/handler (F8)
MOD  api/schemas/manager/main.py              PositionInfo contract + position_to_info
MOD  api/routers/manager/main.py              PositionGet rebuilt
MOD  api/routers/admin/managers.py            + GET "" list (paged, decoded)
MOD  api/di_providers.py                      + manager-positions provider, client/deal/order getters
MOD  api/main.py                              + read-router mounts, F8 registration
MOD  core/ports/interfaces.py                 find_page on six ports
MOD  infrastructure/persistence/repositories/{account,manager,deal,order,position}_repository.py
MOD  .github/workflows/ci.yml                 + p1_proof_read_plane
```

## 6. Still open (unchanged unless noted)

**User decisions:** the `clients = 0` backfill (the read plane is honest
either way — it serves `total: 0` today) · credential rotation / `39c7eaf2`
purge · D16 (24/45 accounts, ~20-line fix, re-measured live this session).

**Next in the plan:** step 9 (Allocations) · `UpdateAccountHandler` +
growing `UpdateGroupCommand` to the 27 modelled fields · B1 manager-on-
behalf-of trading (target `login` on `/manager/*` writes, authorised against
group scope — the dealer UI's blocker) · B3 `GET /admin/ticks` (cheapest
high-value UI endpoint) · D20 with migration 010 · the legacy `admin_router`
shadowed-reads cleanup · everything else per PROJECT-STATE-v7 §5.
