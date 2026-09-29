# IDENTITY & CONFIG PLANE — build plan (files, order, contracts)

Covers: Group, Client, Account, Manager creation + the permissions model + Allocations.
Companion to `ACCOUNT-GROUP-CREATION-SPEC.md` (the MT5 field reference).

---

## 0. First, the DI question — three different things, only one needs DI

`IMTUser`, `IMTConGroup`, `IMTConManager`, `IMTClient` are **C++ interfaces** in the MT5 SDK —
contracts, not dependencies. In our Python code the same idea splits into three things:

| Thing | Example | Import it directly? | Needs DI? |
|---|---|---|---|
| **Domain entity** — data + rules | `Account`, `Group`, `Client`, `ManagerAccount`, `ManagerRightsMask` | ✅ yes, plain `from core.domains… import …` | ❌ no |
| **Port** — a contract | `IAccountRepository`, `IGroupRepository`, `IClientRepository` | ✅ yes, for type hints | ❌ no |
| **Adapter** — the implementation | `SqlAccountRepository`, `InMemoryAccountRepository`, `SqlManagerRepository` | ❌ never import these in `api/` or `application/` | ✅ **this is what DI is for** |

**Rule:** entities and ports are plain imports, usable in any file. DI exists only so the *adapter*
can be swapped — Postgres in production, SQLite in a proof, in-memory in a unit test. If you find
yourself putting a dataclass into the container, stop; that's just an import.

Where our DI lives today:
- `core/ports/interfaces.py` — 24 ports, 852 lines
- `api/di_providers.py` — a process-wide `_container` dict keyed by string, plus `_ContainerView.resolve(port)` which **fails loudly on an unregistered port** (keep that behaviour)
- `application/di/{trading_setup,market_data_setup,pricing_setup}.py` — build the stacks and return provider dicts
- `api/main.py` startup — calls `register_di_providers(...)`

This plan adds **`application/di/identity_setup.py`** following exactly that pattern.

---

## 1. The permissions model — you were right, and our code is wrong

MT5's Manager → **Permissions** tab, verbatim from the Administrator guide:

> *"**Role** — here you can select one of predefined sets of permissions. Using buttons **Save As**
> and **Delete** you can save and delete your own sets of permissions. These sets are saved in
> `/roles` folder of the directory where the terminal information in the user's profile is stored."*

So **admin / manager / dealer / accountant are saved preset files, not built-in roles.** An admin
can create a new one, name it, and delete it. Exactly what you said.

**Our code does the opposite.** `core/domains/identity/models.py`:

```python
class ManagerRole(str, Enum):
 SUPER_ADMIN, DEALER, SUPPORT, RISK_MANAGER, READ_ONLY # five hardcoded values
```

That enum cannot express "Save As", cannot express your live export's 39-bit `M Manager`, and
`SUPPORT` isn't an MT5 concept at all. And the 128-bit `rights` array we already store correctly in
the database is **only ever counted for display** — `grep rights api/ application/` returns four
hits, all inside `list_managers`'s serializer. **Nothing enforces a single right.**

### Target model

```
ManagerAccount
 rights: ManagerRightsMask # the 128 bits. The ONLY source of truth.
 role_preset: str | None # a label for the UI. Cosmetic. Changing it does NOT
 # change rights; it just loads a preset into them.
 group_scope: list[str] # MT5 masks: "demo*", "!managers*,*"
 request_limit_logs: int # "Available logs" period
 request_limit_reports: int # "Available reports" period
```

A **preset** is data, loaded from YAML, editable at runtime through the API:
`{name, description, rights: [names], builtin: bool}`. Builtin presets ship with the code and
cannot be deleted; saved ones can. MT5's rule copied exactly: *the strictest limit always applies*
— so an effective report window is `min(manager.request_limit_reports, per_report_limit)`.

### The three Manager tabs

| Tab | Fields |
|---|---|
| **Common** | Login (**must be an existing account in a `managers\…` group**), Mailbox name (empty ⇒ cannot send internal mail), Groups (the scope, with `*` wildcard and `!` negation — `"!managers*,*"` = everything except managers) |
| **Permissions** | Available logs (period), Available reports (period), **Role** (preset picker + Save As + Delete), then the checkbox tree of ~100 rights grouped by plane |
| **IP access list** | Per-manager allowed CIDRs. We already store `allowed_ips` and have an `IIPWhitelist` port — it is not enforced on any route |

Two more MT5 rules to encode:
* *"A manager can service only those accounts that belong to the server to which the group the
 manager is included in refers."* — group scope is intersected with server.
* Supervision: every manager search query, export, clipboard copy and table filter is **logged**.
 That's the audit journal (debt item), and the manager plane is where it must start.

### Allocations is a separate thing (not a manager tab)

`Accounts → Allocation of accounts` controls **self-service opening from the client terminal**:
which demo/preliminary groups a client may open into, filtered by **country**, with a per-entry
**leverage list**, description shown in the terminal's "Account type" dropdown, **Company**
(white-label) filter, "require ID + proof of address", "start KYC automatically", "use advanced
registration form" (citizenship/employment/income/experience), email+phone **confirmation** with a
mail server, and a **Demo account allocation URL** which — if set — *disables all other allocation
settings* and redirects to your website. Plus Deposit/Withdrawal URLs (real accounts only).
Multiple groups in one entry = **balanced distribution (sharding)**.

We have none of this. It is its own table (`account_allocations`) and its own small CRUD; scope it
separately from manager permissions.

---

## 2. Files to write, by layer

### Layer 1 — `core/domains/` (plain dataclasses, no DI)

| File | Status | Contents |
|---|---|---|
| `core/domains/identity/rights.py` | **NEW** | `ManagerRight` (index ↔ name ↔ description ↔ plane) loaded from YAML · `ManagerRightsMask` VO: `from_names/to_names/from_array/to_array/to_masks/from_masks/has/grant/revoke/merge` · `UserRight` IntFlag (the 16 account bits) with `from_flags/to_flags` |
| `core/domains/identity/role_presets.py` | **NEW** | `RolePreset` dataclass + loader + the 5 builtin presets, decoded from your live export (Administrator = 110 bits, Manager = the 39-bit `M Manager`, Dealer = Manager + 37/42/31, Accountant = + 24, Risk = + 32) |
| `core/domains/identity/group_type.py` | **NEW** | `derive_group_type(name) -> GroupType` — **one** function. Today the rule lives inline in the seeder; both the seeder and `CreateGroupHandler` must call this |
| `core/domains/identity/password_policy.py` | **NEW** | 4 character classes, min = `group.auth_password_min` (floor 8), max 16 · `generate(length)` · `validate(pw, group)` · `hash`/`verify` wrappers over the existing `Argon2PasswordHasher` |
| `core/domains/identity/models.py` | **FIX** | `ManagerAccount` **declares** `name, mailbox, server_id, rights: ManagerRightsMask, group_scope, request_limit_logs, request_limit_reports, must_change_password` — today `db_to_manager` attaches them dynamically, so every consumer uses `getattr`. Delete `ManagerRole` or demote it to a display label |
| `core/domains/accounts/account.py` | **FIX** | add `rights: UserRight`, `color`, `agent_login`, `bank_account`, `limit_orders: int\|None`, `limit_positions_value: Decimal\|None`, `status` (RE/NR), `language`, `id_number`, `lead_source`, `lead_campaign`, `mqid`, `last_access`, `last_ip`, `last_pass_change`, `registration`, `interest_rate`. **Move `investor_password_hash`, `phone_password_hash`, `otp_secret` here from `Client`** (MT5 has them on `IMTUser`, i.e. per account, not per person) |
| `core/domains/accounts/client.py` | **FIX** | add `middle_name`, `state`, `id_number`, `lead_source`, `lead_campaign`; remove the three password fields |
| `core/domains/accounts/group.py` | **FIX** | add `auth_mode`, `auth_password_min`, `auth_otp_mode`, the 8 `company_*` fields, `reports_mode/flags/email`, `mail_mode`, `demo_leverage`, `demo_deposit`, `demo_trades_clean`, `limit_history`, `limit_positions_volume` |
| `core/domains/accounts/login_allocator.py` | **NEW** | the "Next" rule: closest free login above the group floor, **never reuse a deleted login** |

### Layer 2 — `core/ports/interfaces.py`

Add `IClientRepository` (the existing `SqlClientRepository` docstring already says it's waiting for
this). Add `IAccountRepository.find_all` — **the SQL impl has it and `admin_router` calls it, but the
port never declared it.** Add `ILoginAllocator`. Extend `IManagerRepository` with `next_login` and
`find_by_rights(right)`.

### Layer 3 — `infrastructure/`

| File | Contents |
|---|---|
| `alembic/versions/009_identity_plane.py` | new columns on `accounts` / `clients` / `groups`; move password columns client→account; new `role_presets` and `account_allocations` tables. ⚠️ remember migration 001's PG-only `'{}'::jsonb` default breaks SQLite (D3) — use a Python-side default |
| `infrastructure/persistence/account_models.py` | the columns above |
| `infrastructure/persistence/mappers.py` | `account_to_db`/`db_to_account` for the new fields; **delete the dynamic attribute attaching in `db_to_manager`** |
| `infrastructure/persistence/repositories/client_repository.py` | **NEW** — promote `SqlClientRepository` out of `manager_repository.py` and give it the port |
| `infrastructure/persistence/repositories/manager_repository.py` | add race-safe login allocation. **Not `MAX(login)+1`** — a sequence table or `SELECT … FOR UPDATE`, or two admins creating managers at once get the same login |

### Layer 4 — `application/` (this is where DI applies)

| File | Contents |
|---|---|
| `application/commands/create_client.py` | **NEW** |
| `application/commands/create_account.py` | **NEW** — the §6 sequence from the spec. Returns the plaintext passwords **once** |
| `application/commands/create_manager.py` | **NEW** — refuses unless the target account is in a `managers\…` group |
| `application/commands/update_account.py` | **NEW** — accepts per-tab partial bodies; enforces the two move rules (currency change ⇒ zero balance + no positions; never across trade servers) |
| `application/commands/update_group.py`, `delete_group.py` | **NEW** — delete refuses if the group has accounts |
| `application/commands/update_manager.py` | **NEW** — rights + scope + presets |
| `application/commands/save_role_preset.py`, `delete_role_preset.py` | **NEW** — MT5's Save As / Delete |
| `application/commands/balance_operation.py` | exists — wire it to `POST /admin/accounts/{login}/balance`, and make it **always** write a ledger row |
| `application/queries/get_account_detail.py` | **NEW** — the whole 6-tab payload in one read |
| `application/queries/get_client_detail.py`, `get_manager_detail.py` | **NEW** — manager detail returns rights **decoded to names**, grouped by plane |
| `application/queries/list_accounts.py`, `list_clients.py` | **NEW** — filters (group, type, enabled, country) + pagination. Today `list_accounts` does `find_all()[:limit]`, which loads every row then throws most away |
| `application/queries/list_deals.py`, `list_orders.py`, `list_positions.py` | **NEW** — the reads your UI has no source for |
| `application/queries/get_field_schema.py` | **NEW** — serves the descriptor lists the UI renders forms from |
| `application/di/identity_setup.py` | **NEW** — `build_identity_stack(container) -> dict` of providers, same shape as `trading_setup.py` |

### Layer 5 — `config/` (presets and schemas as DATA, so the UI never hardcodes)

```
config/identity/manager_rights.yaml ~100 rights: index, name, description, plane
config/identity/role_presets.yaml Administrator / Manager / Dealer / Accountant / Risk + user-saved
config/identity/account_rights.yaml the 16 USER_RIGHT_* flags: bit, label, which UI tab, inverted?
config/schemas/account_fields.yaml field, type, unit, enum, tab, gating right, mt5_name
config/schemas/group_fields.yaml the 44 MT5 group fields, same shape
config/schemas/client_fields.yaml
config/allocations.yaml (later) which groups clients may self-open into
```

`manager_rights.yaml` and `account_rights.yaml` are **generated from the SDK tables**, not typed by
hand — the extraction script already exists in spirit; keep it in `scripts/dev/`.

### Layer 6 — `api/`

| File | Contents |
|---|---|
| `api/routers/admin/groups.py` | **exists, unmounted.** Extend with `PUT`, `DELETE`, `/schema`, `/{name}/symbols`, then **mount it** |
| `api/routers/admin/accounts.py` | **NEW** — create / list / detail / update / delete / next-login / password / balance / schema |
| `api/routers/admin/clients.py` | **NEW** |
| `api/routers/admin/managers.py` | **NEW** — create / list / detail / update / `/rights` / `/presets` (+ save/delete preset) |
| `api/routers/admin/allocations.py` | **NEW, later** |
| `api/main.py` | **mount all of the above** (this fixes bug F3) and call `build_identity_stack` in startup |
| `api/schemas/admin/{accounts,clients,managers,groups}.py` | **NEW** — Pydantic models. Use `serialization_alias` for the exact MT5 names (`ZIPCode`, `EMail`, `LimitPositionsValue`) so the wire matches the SDK |
| `api/auth/admin_dependencies.py` | **ADD** `require_right(RIGHT_ACC_MANAGER)` — a dependency factory that reads the caller's mask and 403s. **This is the line that turns 128 stored bits into actual authorisation.** Also enforce `allowed_ips` |

### Layer 7 — `tests/` and `scripts/`

```
tests/unit/domains/identity/test_manager_rights_mask.py names <-> array <-> 3 masks, both directions
tests/unit/domains/identity/test_role_presets.py ADMINISTRATOR == 110 bits, MANAGER == 39,
 and both match the LIVE EXPORT exactly
tests/unit/domains/identity/test_password_policy.py 4 classes, group min, max 16
tests/unit/domains/identity/test_group_type.py demo\forex / demo-USD / real\demoforex-USD
 are demo; Demoforex / fx-USD are NOT (guide's own examples)
tests/unit/domains/accounts/test_user_rights.py the 16 flags, incl. the two inverted ones
tests/integration/test_identity_creation.py client -> account -> login with returned password
 -> investor password cannot trade
 -> must_change_password blocks everything
tests/integration/test_manager_rights_enforcement.py a 39-bit manager gets 403 on an admin-only route
scripts/p1_proof_identity.py import your 9 real managers, re-export,
 assert byte-identical; then create+login+trade
```

The preset test is the important one: **your live export is the fixture.** If
`RolePreset.ADMINISTRATOR.to_array()` doesn't equal login 1000's `Rights` array bit for bit, the
model is wrong. That's a real MT5 server's answer, not a guess.

---

## 3. Build order

| # | Step | Why here | Size |
|---|---|---|---|
| **1** | `rights.py` + `manager_rights.yaml` + the preset test against your live export | Nothing else can be authorised until the mask has names. And it's verifiable against real data on day one | M |
| **2** | `group_type.py` + `password_policy.py` | Two tiny pure modules both create-paths need. No DB, no DI | S |
| **3** | `ManagerAccount` declares its fields; delete the dynamic attaching; `require_right()` | Turns stored bits into enforcement. Fixes the `getattr` fragility | M |
| **4** | Mount `admin/groups.py` + `PUT`/`DELETE` + `/schema` | **Group first** — smallest object, everything hangs off it, and `CreateGroupHandler` already exists. Proves the whole pattern end to end | M |
| **5** | Migration 009 + entity fields + mappers (account/client/group) | One schema change, not five | L |
| **6** | `CreateClientHandler` → `CreateAccountHandler` → login → passwords | The flow you actually asked for | L |
| **7** | `CreateManagerHandler` + presets API + IP allow-list enforcement | Needs 1, 3 and 6 | M |
| **8** | The read queries + `/schema` endpoints for account/client/manager | Unblocks the UI | L |
| **9** | Allocations | Independent; do it when the client terminal story starts | M |

**Do 1–4 before anything else.** That's the skeleton: a named rights mask, a pure group-type rule, a
password policy, real enforcement, and one complete create path with a schema endpoint. Everything
after that is the same shape repeated.

---

## 4. The rules that make it fireproof

. **One writer per number.** `accounts.rights` is written only by the identity commands. Margin only
 by RMS. This is the rule whose absence produced D8b, D13, D15, D16 and F8.
. **Refuse, don't guess.** No login allocator race, no default password, no silent group-type
 fallback, no `getattr(..., default)` on a field that should be declared.
. **Presets are data.** If adding a role needs a code change, the model is wrong.
. **The live export is the fixture.** Every rights/preset/group-type assertion is checked against
 your real TCTrader-Live file, not against my reading of the docs.
. **Round-trip after every write.** Create a group, re-export it, assert byte-identical. That is the
 project's signature guarantee and a new write path is exactly where it breaks.
. **The UI renders forms from `/schema`.** No field list hardcoded in TypeScript. That's what stops
 the 0/1 problem from ever reaching the browser.
. **Plaintext passwords exist only in the create response.** Argon2 in the DB, printed once, never
 retrievable — the `cli seed` first-admin pattern, applied to everything.
