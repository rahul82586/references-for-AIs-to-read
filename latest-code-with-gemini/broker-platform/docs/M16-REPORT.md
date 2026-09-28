# M16 — IDENTITY PLANE steps 5–7: account creation, the group engine, and the manager plane (session 6, 2026-09-13)

**Scope delivered:** the 009 identity columns on the entities, models and mappers,
atomically · the rights mask as the single authority for `is_enabled` · the Group
entity owning all 42 scalar ConfigGroups fields · **D18 found and fixed** ·
**D3 fixed** · `CreateClientHandler` → `CreateAccountHandler` with the race-safe
login allocator, the group-driven password policy and plaintext-returned-once ·
the account/client HTTP plane with `require_right` · `/admin/accounts/schema` ·
two new proof gates.

**Gates after this milestone:** `pytest tests` **740 passed / 0 failed / 0 skipped**
(was 670; **+70**) · ruff E9,F63,F7,F82 **clean** · round-trip **392/392** ·
m2 seed ✅ · m3 currencies 362/362 · m3 margin ✅ · m3 uow ✅ · m8 18/18 ·
m9 14/14 · m10 19/19 · m11 39/39 · **p1_proof_migration_009 24/24** (was 18) ·
**p1_proof_identity 59/59** · **p1_proof_account_creation 72/72 (NEW)** ·
**p1_proof_manager_creation 80/80 (NEW)** · m4 weekend-skip (correct — Sunday).

Everything below was transcribed from `Include.md`, the Administrator guide and
the live TCTrader-Live export. Nothing was inferred from a summary.

---

## 0. What was read before anything was written

| Source | Used for |
|---|---|
| `Include.md` `class IMTUser` (line 10983) | the 67 account members, `EnUsersRights` (18 bits), `EnUsersPasswords`, `USER_RIGHT_DEFAULT`, `USER_RIGHT_ALL` |
| `Include.md` `class IMTClient` (6067) | `EnClientType/Status/Gender/KYCStatus/ClientOrigin`, the Person*/Company*/Contact*/Address* families |
| `Include.md` `class IMTConGroup` (18712) | all 15 group enums verbatim: `EnPermissionsFlags`, `EnAuthMode`, `EnAuthOTPMode`, `EnReportsMode/Flags`, `EnNewsMode`, `EnMailMode`, `EnHistoryLimit`, `EnFreeMarginMode`, `EnTransferMode`, `EnStopOutMode`, `EnMarginFreeProfitMode`, `EnMarginMode`, `EnMarginFlags`, `EnTradeFlags` |
| `Include.md` `class IMTConManager` (19653) | `EnManagerLimit`, `Right(idx)` (there is **no** `Name()`/`Rights()` accessor — the export's `Name`/`Rights` array is an export-format artefact, not SDK surface) |
| live `Groups TCTrader-Live.json` | the **44** ConfigGroups wire names, in order, and their real values (`PermissionsFlags 2`, `TradeFlags 215`, `Company "TC Trader"`, `MarginCall 10.00`, `AuthPasswordMin 8`) |
| live `Clients and accounts TCTrader-Live.json` | **contains only `ConfigManagers` (9 records)** — there is no live account/client export, so account field authority is `IMTUser` + the guide, not a fixture |
| Admin guide `Accounts/Creating-Account.md` | the Details box, the Passwords box, the "Next" rule, the four-character-class password rule |
| Admin guide `Accounts/Editing-Account.md` | the six tabs and the rights bit that gates each |
| migration `009_identity_plane.py` | the column authority: 33 account + 5 client + `login_counters` |

---

## 1. Two SDK corrections — both were silent data corruption

### 1a. `USER_RIGHT_DEFAULT` is 0x163, not 0x3

`Include.md`, verbatim:

```
USER_RIGHT_DEFAULT = USER_RIGHT_ENABLED | USER_RIGHT_PASSWORD |
                     USER_RIGHT_TRAILING | USER_RIGHT_EXPERT | USER_RIGHT_REPORTS
```

`ACCOUNT-GROUP-CREATION-SPEC §6` said the creation default was
`ENABLED | PASSWORD`. That was written before `Include.md` was read member by
member, and it is wrong: every account this platform created would have had
**trailing stops, Expert Advisors and daily reports silently disabled**. Those are
exactly the five boxes MT5's Limits tab shows ticked on a fresh account.

`MT5_USER_RIGHT_DEFAULT = 0x163` is now the constant, and `DEFAULT_NEW_ACCOUNT_
RIGHTS` aliases it so the plan's wording still resolves. `MT5_USER_RIGHT_ALL` is
built by OR-ing the **named** members, because the SDK's own `USER_RIGHT_ALL`
deliberately omits `USER_RIGHT_OBSOLETE` (0x80) — a hand-written magic number got
that wrong on the first attempt and `from_flags` refused it, which is the guard
doing its job.

### 1b. `TradeFlags` was missing two SDK bits

`TRADEFLAGS_DEAL_COST = 0x400` and `TRADEFLAGS_SO_COMPENSATION_CREDIT = 0x800`
were absent, so `int(TradeFlags(x)) != x` for any live group carrying them — a
group's flags changed on a read/write cycle. Both added, plus `DEFAULT = 0x1F`.

---

## 2. Step 5 — entities + models + mappers, atomically

### Account (`core/domains/accounts/account.py`)

All **33** IMTUser identity fields declared, each named for its SDK accessor.
`AccountModel` declares the same 33 columns → **67 columns total, exactly the
live Neon shape**; `ClientModel` → **32**, also exact.

**`rights` is the single authority.** `is_enabled` is no longer a stored field —
it is an `InitVar` on the constructor and a property over the `ENABLED` bit, with
a setter that flips that one bit. Two independent booleans for one MT5 bit is the
D1/D13/D16 class. Derived views added: `trading_disabled`, `may_trade`,
`must_change_password`, `is_technical`, `is_investor_session`, `has_right`,
`display_name`, `effective_limit_orders`.

`can_trade()` now reads the mask: `ENABLED` set, `TRADE_DISABLED` clear, and not
an investor session.

**Legacy rows are handled honestly.** Migration 009 backfilled `rights = 0` for
all 45 live accounts. In MT5 a zero mask is `USER_RIGHT_NONE` — not even allowed
to connect — so trusting it would have silently disabled 45 real accounts on
read. `_user_rights_or_legacy` falls back to `is_enabled` **only for a zero
mask**, reconstructing `USER_RIGHT_DEFAULT`. That is not a guess: it is refusing
to invent a restriction MT5 never recorded.

### Client

Gains `middle_name`, `state`, `id_number`, `lead_source`, `lead_campaign`. Its
four password fields are documented as the **deprecated location** — MT5 puts
`PasswordHash`/`PhonePassword`/`OTPSecret` on `IMTUser`, so one client with a
demo and a real account has two investor passwords. They still round-trip (no
stored value is ever dropped) but nothing new writes them.

### Group — all 42 scalar ConfigGroups fields now domain-owned

27 fields were quarantined into `mt5_extra`: the entity could neither read nor
write them, so `/schema` advertised controls nothing could set. They are now
declared with SDK-typed enums, given a `domain` path in `fieldmap.GROUP_FIELDS`
(**44/44 mapped, 0 unmapped**), written by `group_to_db` and read by
`db_to_group`. `MarginProfile` gains `free_profit_mode`.

Only the two **nested** arrays stay baseline-owned, and deliberately:
`CommissionRule` models 4 of MT5's 12 commission fields and
`GroupSymbolOverride` 11 of 64 override fields, so rebuilding them from the
domain would drop everything else — and unlike a scalar, the domain cannot
distinguish "unchanged" from "set to the same value".

`config/schemas/group_fields.yaml` had 27 entries saying `modelled: false`. All
53 now say `true` — the schema endpoint no longer lies to the UI.

---

## 3. 🔴 D18 (NEW, found this session) — `save()` destroyed an imported group's MT5 baseline

`SqlGroupRepository.save()` did `group_to_db(group)` with **no** `mt5_source` /
`mt5_scale` / `mt5_extra`, then `session.merge(model)`. A full-row merge NULLed
all three. Measured, through the real import path and the real repository, on
`demo\Standard`:

```
one edit: entity.limit_orders = 500 ; await repo.save(entity)

  mt5_source: present -> None        mt5_extra: -> 0 keys     mt5_scale: -> 0 keys
  wire fields differing from the original:  5 -> 14

  Company             "TC Trader"                    -> ""
  CompanyPage         "MT5-COMBA-01-STANDARD"        -> ""
  CompanySupportPage  "https://www.mql5.com/[lang…"  -> ""
  PermissionsFlags    "2"                            -> "0"
  DemoLeverage        "100"                          -> "10"
  DemoDeposit         "10000.00"                     -> "0.00"
  LimitPositionsVolume "0.00"                        -> "0E-8"
  Commissions         12-field records               -> collapsed to the 4 modelled
  Symbols             64-field records               -> collapsed to the 11 modelled
```

**M15 made this reachable over HTTP** by mounting `PUT /api/v1/admin/groups/{name}`.
So between M15 and this fix, one edit through the admin API permanently destroyed
that group's byte-identical re-export — the project's signature guarantee.

This is the D8b/D15 class exactly: a value written in one place and blanked from
another. The durable defence the design law names — *one writer per number,
disjoint column sets* — is what the fix implements: `save()` now calls
`_carry_import_owned()`, which reads the stored row inside the **same session**
and carries `mt5_source` / `mt5_scale` forward, merging `mt5_extra` with the
stored values winning. `SqlSymbolRepository.save()` had the identical latent
shape and is fixed too (no live caller yet).

**Regressed by test:** `test_d18_saving_an_imported_group_preserves_its_mt5_baseline`
asserts the changed-key set is **exactly** `{"LimitOrders"}`.

### The drift that hid it

`tests/unit/persistence/test_m1_schema_and_units.py::_seeder_group` was a
hand-rolled copy of the loader's mapping that set **17 of 44** fields. While 27
were quarantined, nothing noticed. The moment the entity owned them, the omitted
fields arrived as dataclass defaults and overwrote the server's values.

Fixed by extraction, not by patching the copy: `loader.group_from_mt5_record(raw)`
is now the ONE builder, `groups_from_mt5` loops over it, and `_seeder_group`
delegates to it. A test that re-implements the code under test only proves the
test agrees with itself.

---

## 4. 🟠 D3 FIXED — `alembic upgrade head` now runs on SQLite

Migrations 001 and 007 emitted `server_default=sa.text("'{}'::jsonb")`. The
`::jsonb` cast is PostgreSQL-only, so the chain died on SQLite and `cli migrate`
/ `make migrate` only ever worked against PostgreSQL. M5's JSONB→JSON *type*
compile hook handled the column type; the default **text** passed through verbatim.

23 casts removed. This is a **no-op on PostgreSQL** — an untyped string literal
assigned to a jsonb column is implicitly cast, so `DEFAULT '{}'` and
`DEFAULT '{}'::jsonb` store the same default — and legal on SQLite.

**Safe for production:** Neon is already at `009_identity_plane` and alembic never
re-runs an applied revision. A fresh PostgreSQL migration produces a
semantically identical schema.

This unblocked making `p1_proof_migration_009` honest: it used to build its
008-era baseline from `create_all`, which was **circular** — it compared the
models against themselves. It now runs `alembic upgrade 008_reconciliation_breaks`
from an empty database, and adds the check that matters:

```
== models and migration agree (the step-5 atomicity guarantee) ==
  [PASS] both schemas expose the same tables
  [PASS] no column drift between migration 009 and the ORM models
  [PASS] accounts: every model column exists in the migrated schema
  [PASS] clients / groups / managers: likewise
```

That check found a real gap on its first run: **`login_counters` had no ORM
model** — migration 009 created the table and nothing in Python could see it.
`infrastructure/persistence/identity_models.py :: LoginCounterModel` now exists.
18/18 → **24/24**.

---

## 5. Step 6 — the account creation flow

### The login allocator (`core/domains/accounts/login_allocator.py`)

Guide: *"If you specify 'Next' … the closest free number will be assigned. **Do
not use logins of deleted account when creating new ones.**"* Two requirements,
and `MAX(login)+1` satisfies neither — it is a read-then-write race (with
merge-based repositories the loser silently overwrites the winner rather than
raising), and it reuses a deleted login the moment the highest account is
removed, reassigning a real trading history to a different person.

So: a **monotonic counter per scope**, advanced by one statement —

```sql
UPDATE login_counters SET next_login = next_login + 1, updated_at = :now
 WHERE scope = :scope RETURNING next_login
```

— plus a presence check that steps over any login already in `accounts`, which is
what makes the number "free" for a database populated by import rather than by
the allocator. Bounded at 10 000 attempts, then `LoginTakenError`: refusing beats
handing out somebody else's history.

The RULE is in the domain (no SQLAlchemy, so the arithmetic is testable without a
database); the atomic statement is in `SqlLoginAllocatorStore`. `peek()` powers
the "Next" button **without reserving**, and the authoritative allocation happens
inside the create — so two administrators looking at the same suggested number
cannot both get it. Proven: **8 concurrent creates → 8 distinct logins.**

A login reserved by a create that then rolls back is burned, never reused. That
is the safe direction and it is what the guide asks for.

### `CreateAccountHandler` — the eight rules, each enforced

1. **The group decides.** `account_type` is `derive_group_type(group.name)` and
   `currency`/`currency_digits` come from the group. Neither is a field on the
   command, so a caller cannot create a "real" account in `demo\Standard`. A test
   posts both and asserts they are ignored.
2. **`preliminary` is refused** without `allow_preliminary=True` — trading is
   PROHIBITED for every symbol in it, and it exists for terminal-opened
   KYC-pending accounts.
3. **Passwords.** All three generated when omitted, validated against
   `PasswordPolicy.for_group(group.auth_password_min)`, master ≠ investor
   (an investor session that could trade is not an investor session). Argon2
   stored. **Plaintext returned exactly once**, never logged, never on the bus.
4. **Rights from the tabs**, with the two INVERTED SDK bits applied once, here:
   `enable_trading=False` sets `TRADE_DISABLED`; `show_to_regular_managers=False`
   sets `TECHNICAL` (65536 — the bit migration 009's partial index exposes).
5. **NULL ≠ 0** for limits. `limit_orders=None` inherits the group; `0` means
   none allowed. Both survive the round trip as themselves, and
   `effective_limit_orders` applies "the stricter one wins".
6. **Colour** stored as the raw COLORREF AABBGGRR int, validated 0..0xFFFFFFFF,
   and kept separate from the dealer's free-form `color_tag`.
7. **One transaction.** Account + opening deposit's `BalanceOperation` commit
   together via the UoW, so there is no balance without a ledger entry — an
   account with a balance and no entry is how a book becomes unreconcilable,
   which is what M12 exists to detect. If the ledger or UoW is not wired and a
   deposit is requested, the create is **refused**, not half-applied. A zero
   deposit is refused too: it is not a deposit, and writing one would be a ledger
   row saying money moved when none did.
8. **`AccountCreated` and nothing else.** No tick, no margin recompute — a new
   account has no positions, so its margin is zero by construction, and
   triggering a valuation here is how an account ends up priced against a market
   it never traded in (**D16**). `margin_level` is set to the `999999` sentinel.

`CreateClientHandler` refuses an anonymous record (nothing identifying) and a
duplicate `id_number` — a passport identifies one person, two people may share a
name.

### HTTP plane

```
POST /api/v1/admin/accounts            201  require_right(RIGHT_ACC_MANAGER)
POST /api/v1/admin/accounts/create     201  (alias)
POST /api/v1/admin/accounts/next-login 200  advisory, reserved: false
GET  /api/v1/admin/accounts/schema     200  descriptors + all 18 USER_RIGHT bits
POST /api/v1/admin/clients             201  require_right(RIGHT_CLIENTS_CREATE)
POST /api/v1/admin/clients/create      201  (alias)
```

Mounted **before** `admin_router`, the M15 lesson. 33 → 39 HTTP paths.

`/schema` sends each right's **bit as an int** plus `hex`, `label`, `tab`,
`inverted`, `description` and `in_default`. A UI that receives `"0x4"` cannot
mask against it, and a mask rendered from strings is how the 0/1 problem reaches
the browser. Exactly three bits are `inverted: true` —
`USER_RIGHT_TRADE_DISABLED`, `USER_RIGHT_TECHNICAL`, `USER_RIGHT_EXCLUDE_REPORTS`
— and a test pins that set.

Credential fields are `write_only` in the schema; `cert_serial_number` is **not**,
because a certificate serial is a server-maintained identifier an operator needs
to read to match a `.cer` file. A schema that hides the whole Security tab is as
useless as one that hides nothing.

`config/schemas/account_fields.yaml` — 60 descriptors over `IMTUser`, each with
its MT5 accessor name, tab, gating right, column, and whether it is
modelled/writable **today**.

---

## 6. New gates

```
scripts/p1_proof_account_creation.py    72/72   (in CI now)
tests/unit/persistence/test_step5_identity_plane.py   22 tests
tests/unit/api/test_step6_account_creation_api.py     20 tests
tests/unit/domains/identity/test_manager_rights.py    +1 (the SDK default)
```

The step-5 file includes the guard that makes the atomicity rule mechanical
rather than a review comment: it reflects over `AccountModel.__table__.columns`
and fails if any column is not both written by `account_to_db` and read by
`db_to_account`, with an explicit, documented exception list for the two columns
that are written-but-deliberately-not-read (`margin_level` per D1, `is_enabled`
because the mask is the authority) — and a complement test asserting those two
are still **written**, because external SQL consumers read the columns.

---

## 7. Still open

**P0 (user actions, unchanged and still live):** rotate
Neon/Upstash/`SECRET_KEY`/`ADMIN_API_KEY` — `.env` is still fetchable at
`39c7eaf2` (re-verified this session: HTTP 200, 523 bytes, all four populated).
The **15 plaintext passwords** are located exactly: Data Feeds 4 `FeedPassword`
+ 4 `GatewayPassword`, Gateways 3 `GatewayPassword` + 3 `TradingPassword`,
Charts & Ticks 1 `Password`. **Correction to the earlier docs:** the "live JWT"
is *not* in `mt5-format-structure/` — the only JWT in the repo is in
`chat-and-reference-files/api_test_results.md`. **New:**
`Security TCTrader-Live.json` publishes the broker's real `ConfigFirewall`
allow-list (`172.26.0.0/16`, `87.106.157.232` "DB", `162.55.222.194`,
`171.50.169.254` "Krish") — infrastructure disclosure in a public repo.

**P1 money & correctness:** **D16** (re-measured live this session: 24/45 Neon
accounts where `equity − balance ≠ Σ position profit`; deltas `+800.70 ×10`,
`−749.20 ×9`, `+798.90 ×2`, `+2.10 ×1`, `−0.50 ×1`, `+2.30 ×1`) · the
`margin_free`/`margin_level` four-writer problem · **F8/F9** (`PositionGet` `[]`
+ `ticket=0`) · stop-out never live-fired · A-Book close never unwinds the hedge
· 9 reconciliation breaks OPEN · D17 · `bars` = 0 · 19 of ~25 MT5 pre-trade
checks missing.

**Identity plane, remaining plan steps:** 7 (`CreateManagerHandler` + presets API
+ IP allow-list rollout) · 8 (read queries + `/schema` for account/client/manager,
which unblocks the Theia UI and B2's `/admin/{orders,deals,positions}`) ·
9 (Allocations). Plus: `UpdateAccountHandler` (the per-tab partial bodies and the
two move rules), manager JWT rollout beyond the groups/accounts planes, and
**`clients` has 0 rows in Neon while 45 accounts carry `client_id` values that
point at nothing** — that needs an explicit backfill-or-start-clean decision.

**New, from this session:** the manager plane's `require_right` is wired for
accounts and clients, but the existing admin **reads** still use the static key;
and `must_change_password` is enforced in `require_right` but still not at login.


---

## 8. Step 7 — the manager plane (`CreateManagerHandler`, presets, IP allow-list)

Read from `Include.md` `IMTConManager` (line 19653) + `IMTConManagerAccess`
(19633), the guide's *Managers* section (Common / Permissions / Reports / IP
Access List), and all **9 live ConfigManagers records**.

### The rules, each enforced

* **No login allocation.** *"Manager accounts are created only based on accounts
  added in the corresponding section"* and *"the specified account must be
  included to the managers' group"*. So the handler REFUSES unless the named
  account exists AND `derive_group_type(group.name) is MANAGER` — verified
  against your three real staff groups (`managers\administrators`,
  `managers\dealers`, `managers\API`). This is what keeps staff logins out of
  the client account list.
* **`server_id` comes from the account's GROUP.** *"A manager can service only
  those accounts that belong to the server, to which the group the manager is
  included to refers."* Not accepted from the request.
* **Rights by NAME, never indices.** An unknown name is refused with an
  explanation, because a silently-empty mask creates a manager who authenticates
  and then 403s on everything — which reads as a broken server, not a typo.
  `RIGHT_LAST` (128) is asserted non-grantable; the catalogue excludes it so the
  UI cannot render a checkbox for it (**96 grantable of 97**).
* **The Groups scope obeys BOTH guide rules.** *"A rule cannot consist of
  prohibition only"* → `"!demo*"` refused, `"!demo*,real*"` accepted. *"Rules are
  checked top to bottom; if you allow all groups in the first row you will not be
  able to prohibit some in the next"* → `"*,!managers*"` is **accepted but the
  dead rule is reported**, because MT5 accepts it and refusing would be inventing
  a restriction. Also refused: a `*` that is not at an end (`"de*mo"` is matched
  LITERALLY by `_mask_matches`, so it silently grants nothing — a typo that reads
  like a wildcard), `"!"` not first, and empty patterns. Order is preserved, never
  sorted or deduplicated, because first-match-wins makes order semantic.
* **One writer for the credential.** `accounts.password_hash` is the authority;
  `managers.password_hash` is a MIRROR written only here, in the same
  transaction. Omitting a password copies the account's existing hash — no new
  plaintext is invented. Two independent passwords for one login number (one
  checked by `/auth/login`, one by the manager plane) would be the D1/D18 class
  again: a secret written in one place and verified from another.
* **`must_change_password` defaults to False**, and this is a deliberate reversal
  of what the plan implied. MT5 forces the change on the AUTO-created
  administrator (which `cli seed` already does), not on every manager an operator
  provisions. Defaulting it True would lock a new manager out of the entire admin
  plane — `require_right` 403s on the flag — with **no manager password-change
  endpoint to unlock them**. That is a trap, not a control. It is now an explicit
  command field.

### 🟠 D19 (NEW, found this session) — `effective_report_window` compared two different units

`IMTConManager::LimitReports` is documented as *"reports access limit
**EnManagerLimit**"* — an ORDINAL (0=unlimited, 1=1 month, 2=3 months, 3=6
months, 4/5/6=1/2/3 years). M15's `effective_report_window` did
`min(request_limit_reports, per_report_limit_days)`, i.e. min()-ed an **ordinal**
against a **day count**:

```
"Available reports" = 6 months (ordinal 3)  vs  a report limited to 90 days
  before:  min(3, 90)  = 3      -> the manager could request 3 DAYS
  after:   min(180, 90) = 90    -> the guide's own answer
```

The guide states the rule and the example explicitly: *"The strictest limit
always applies. For example, if the 'Available reports' parameter is set to '6
months' and a specific report has a limit of 90 days, the manager will only be
able to request data for the past 90 days."*

Worse, the M15 unit test **encoded the bug**: it constructed
`request_limit_reports=30` — which is not a valid `EnManagerLimit` ordinal at all
— and asserted days back. Nothing validated the field, so an invalid value sat in
a column and was compared against a different unit.

Fix: `LIMIT_PERIOD_DAYS` + `limit_period_to_days()` in `core/domains/accounts/enums.py`
(the ONE place the conversion lives; MT5 publishes no day mapping, so the table is
our documented convention and the guide's example holds under it), and
`_validate_limits` refuses any ordinal outside 0..6 on create and update. The
test now asserts the guide's example verbatim and that ordinal 30 raises.

This is the D1/D13/D16 class again — a number that means one thing where it is
written and another where it is read.

### IP allow-list: From/To **ranges**, not just CIDR

`IMTConManagerAccess` has exactly two members, `From()` and `To()` — a RANGE. The
guide's use case is *"limit managers' access, for example, to the dealing room
only"*, and a CIDR cannot express `10.0.0.5-10.0.0.9`. `_ip_allowed` now accepts
three spellings: the wire dict `{"From":…,"To":…}`, the string `"from-to"`, and
CIDR/single-address. An unparseable entry grants NOTHING; a reversed range is
normalised (an operator typo, not a grant); v4 and v6 never cross-match; an empty
list is unrestricted, which is what all nine live managers carry (`Access: []`).
16 cases pinned.

**A regression caught here:** the first implementation routed CIDR through
`ip_address`, which rejects `"10.0.0.0/24"`, so every prefix allow-list silently
refused. Caught by the proof before commit.

### HTTP plane

```
POST   /api/v1/admin/managers              201  create (on an existing managers-group account)
POST   /api/v1/admin/managers/create       201  alias
GET    /api/v1/admin/managers/{login}      200  rights DECODED to names, grouped by plane
PUT    /api/v1/admin/managers/{login}      200  rights / scope / limits / IPs; refuses a no-op
GET    /api/v1/admin/managers/rights       200  97 rights, index+plane+description, sentinel excluded
GET    /api/v1/admin/managers/presets      200  the Role picker
POST   /api/v1/admin/managers/presets      201  Save As
DELETE /api/v1/admin/managers/presets/{n}  200  Delete (builtins refused)
GET    /api/v1/admin/managers/schema       200  manager_fields.yaml descriptors
```

39 → **45 paths**. Gated by **`RIGHT_CFG_MANAGERS` (17)**, *not*
`RIGHT_ACC_MANAGER` (27) — the SDK keeps them apart, and collapsing them would let
anyone who may edit an account grant themselves more rights. A test asserts a
manager holding only `RIGHT_ACC_MANAGER` gets **403** on this plane, and that the
catalogues are gated too.

Catalogue routes are declared **before** `/{login}` (the M15 `/groups/schema`
lesson) and a test asserts none of them resolves as a login.

`login_manager` now returns `must_change_password` (in the body AND the JWT
claim) so a terminal can show the change-password dialog. Login still SUCCEEDS
with the flag set — a manager who cannot authenticate cannot change their
password; `require_right` is what blocks privileged actions.

### New gates

```
scripts/p1_proof_manager_creation.py       80/80   (in CI now)
tests/unit/api/test_step7_manager_api.py   26 tests
tests/unit/domains/identity/…               +1 (the EnManagerLimit day mapping)
```

The manager proof uses **your nine real managers as the fixture** and re-asserts
that `Administrator` == login 1000's 110 bits and `Manager` == login 208011's 39
bits, bit for bit, plus that all nine masks still round-trip.

### SDK/wire note worth keeping

`IMTConManager` has **no** `Name()` and **no** `Rights()` accessor — it exposes
`Right(index)` one bit at a time. The export's `Name` field and its 128-element
`"0"`/`"1"` array are **export-format artefacts**, not SDK surface.
`manager_fields.yaml` documents this rather than pretending the two agree.
