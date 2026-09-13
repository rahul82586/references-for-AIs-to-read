# M15 — IDENTITY & CONFIG PLANE, steps 0–4 (session 5, 2026-09-13)

**Scope delivered:** the reconstructed migration 009 · the named rights mask and
live-export-decoded presets · the one group-type rule · the MT5 password policy ·
ManagerAccount's declared fields · `require_right()` (first real authorisation
in the platform's history) · the mounted Group CRUD with `/schema` · the two P1
proof gates · repo hygiene restored (.gitignore, .env.example, CI, F5 deps).

**Gates after this milestone:** `pytest tests` **670 passed / 0 failed / 0 skipped**
(was 621; +49 new) · ruff E9,F63,F7,F82 **clean** · round-trip **392/392** ·
m2 seed ✅ · m8 18/18 · m9 14/14 · m10 19/19 · m11 ✅ · m4 weekend-skip (correct) ·
**p1_proof_migration_009 18/18** · **p1_proof_identity 59/59** (nine real managers
as the fixture).

---

## 0. The discovery that reframed the milestone

**The live Neon database was AHEAD of the repo.** Its `alembic_version` reads
`009_identity_plane` and it carries a `login_counters` table — but the repo had
migrations 001–008 only. The dead session 4 (or its final, unrendered moments)
built and APPLIED a migration 009, then died before pushing; its source existed
only in the lost sandbox. Nothing in any capture contained the code — the
session-4 HTML mentions it only inside the plan text.

Response: the whole live schema was read back from Neon's
`information_schema` (67 accounts columns, 32 clients, 58 groups,
login_counters, every default, every index — including the partial index
`WHERE (rights & 65536) <> 0`, i.e. the USER_RIGHT_TECHNICAL filter), and
`alembic/versions/009_identity_plane.py` was **reconstructed DDL-faithful** to
it, with the same revision id. Consequences, both intended:

* Neon: `alembic upgrade head` is a no-op (version already recorded).
* Fresh DB: converges on exactly Neon's shape — proven by
  `scripts/p1_proof_migration_009.py` on throwaway SQLite (upgrade →
  introspect → re-upgrade idempotent → downgrade clean, 18/18).

The migration is **DDL only**. The SQLAlchemy models deliberately do NOT gain
the new columns yet: `account_to_db()` constructs a fresh model on every save,
so a declared column with no mapper support is a full-row save waiting to blank
it — the D8b/D15 defect class. Models + entities + mappers gain the fields
together in step 5.

## 1. Step 1 — rights as named data (`core/domains/identity/rights.py`)

* `manager_rights.yaml` — **97 rights GENERATED from the SDK**'s
  `IMTConManager::EnManagerRights` (script: `scripts/dev/extract_identity_yaml.py`,
  never hand-typed), each with index, name, plane, description. Indices 2–9,
  68–69, 89–95, 113–127 are unnamed in the SDK; index 128 `RIGHT_LAST` is the
  enum terminator and is **never grantable**.
* `ManagerRightsMask` — immutable VO: names ↔ wire array (128×"0"/"1") ↔ the
  three 43-bit DB words, all three directions pinned **against the existing
  storage packer** (`rights_to_masks`/`masks_to_rights`) by
  `test_mask_packing_matches_the_storage_layer_bit_for_bit`. Strict on names
  (a misspelled right explodes), tolerant on positions (the live admins carry
  1s at unassigned 68/69 — the wire is preserved, `unnamed_indices()` exposes
  it). `grant/revoke/merge` return NEW masks.
* `UserRight` IntFlag — the 18 `IMTUser::EnUsersRights` members with MT5's
  exact bit values; `from_flags` **refuses unknown bits**;
  `DEFAULT_NEW_ACCOUNT_RIGHTS = ENABLED | PASSWORD`.
* `account_rights.yaml` — generated, with the UI metadata: tab, label, and the
  three INVERTED senses (TRADE_DISABLED↔"Enable trading", TECHNICAL↔"Show to
  regular managers", EXCLUDE_REPORTS↔"Include in server reports").
* `role_presets.py` + `role_presets_builtin.yaml` — **decoded from the live
  export**: Administrator = login 1000's exact 110-bit array (0–109), Manager =
  login 208011's exact 39-bit array; Dealer/Accountant/RiskManager = Manager +
  {31,37,42}/{24}/{32}. Save As / Delete semantics per the guide (builtins
  cannot be overwritten or deleted; user presets are YAML data). Presets are
  labels: `apply_preset` loads bits into the mask; the mask stays the only truth.

## 2. Step 2 — the one group-type rule + the password rule

* `group_type.py :: derive_group_type` — MT5 Group-Types.md verbatim:
  **case-sensitive substring** on the full name incl. path; REAL is the
  fallback ("if a group doesn't fall into any category... the system considers
  it a real one"). Documented ambiguity order (the guide forbids mixed markers
  but doesn't rank them): manager > contest > demo > coverage >
  preliminary(exact) > real — toward the MORE restricted type, because a
  misclassified staff group blocks clients visibly while the reverse does not.
  `validate_group_name`: ≤64 chars, backslash segments, no empty segments, no
  `/`, every violation listed at once.
* `infrastructure/mt5/enums.py :: account_type_from_group_path` now **delegates**
  to it (was prefix-based + case-INsensitive — it disagreed with MT5 on the
  guide's own examples: "Demoforex" and "real\demoforex-USD"). All four call
  sites keep working; the m1 derivation test passes unchanged; round-trip 392/392
  unaffected (account_type is derived metadata, not a wire field).
* `password_policy.py` — 4 character classes, min = group `AuthPasswordMin`
  clamped to the platform's 8..16, max 16; `violations()` returns EVERY reason;
  `generate()` uses `secrets` and guarantees all four classes; hash/verify
  wrappers keep empty-hash = refusal (M6's fail-closed rule) and treat a
  corrupt stored hash as a refusal, not a 500.

## 3. Step 3 — ManagerAccount declares its fields; bits become enforcement

* `models.py` — name/mailbox/server_id/rights/group_scope/request limits/
  must_change_password/role_preset are DECLARED fields (the dynamic attaching
  in `db_to_manager` is gone; `getattr(..., default)` fragility with it).
  `ManagerRole` demoted in-place to a cosmetic label (kept: the login token,
  the admin serializer and old tests reference it; authorisation must never
  read it). Helpers: `has_right`, `grant/revoke`, `apply_preset`,
  `in_group_scope` (MT5 mask semantics, first-match-wins — reproduces the
  guide's `"!managers*,*"` example exactly), `effective_report_window`
  (strictest limit wins).
* Mappers updated both directions; `manager_to_db` still accepts a legacy raw
  array; the seeder's first admin keeps its exact legacy wire shape
  (`from_array(["1"]*128)`), so stored rows and re-exports are unchanged.
* `api/auth/admin_dependencies.py :: require_right(name)` — the factory
  resolves the right AT IMPORT (a typo crashes the boot, not every request).
  Two credential paths: the bootstrap `X-Admin-API-Key` (full access until
  CreateManagerHandler provisions real staff logins) or a **manager JWT**
  (`is_manager` claim from the existing `AuthService.login_manager`). Refusals:
  client token → 403; unknown/inactive manager → 401 (**never a fabricated
  identity — the anti-F2 rule**); `must_change_password` → 403 (stored since
  M2, enforced for the first time anywhere); `allowed_ips` configured and the
  client outside it → 403 (MT_RET_AUTH_MANAGER_IPBLOCK semantics); unwired
  manager repo → 503. The 10-case matrix is `test_require_right_matrix`.

## 4. Step 4 — Group CRUD mounted (F3 fixed) with `/schema`

* `api/routers/admin/groups.py` — POST `/api/v1/admin/groups` (+ legacy
  `/create` alias), PUT/DELETE `/{name:path}` (forward-slash form accepted, as
  admin_router does), GET `/schema`. Router-level
  `require_right("RIGHT_CFG_GROUPS")`. Mounted in `api/main.py` **before**
  admin_router so `/schema` is not swallowed by `GET /groups/{group_name:path}`.
* `CreateGroupHandler` hardened: name validation, **type derived from the
  name**, contradicting explicit types refused (one documented exception:
  contest-on-demo, the seeded `demo\Challenge` pattern), margin pair validated
  (call > stop > 0, percent), duplicate refused before any write.
* `UpdateGroupHandler` / `DeleteGroupHandler` (new): partial updates over the
  fields the ENTITY models today (a field the command silently ignored would be
  a UI checkbox that lies — the 009-only columns arrive with step 5);
  MT_RET_REQUEST_NO_CHANGES refusal for a no-op update; currency change
  refused while the group has accounts; delete refused while it has accounts
  **including when emptiness cannot be verified (fail closed)**. Port gained
  `IGroupRepository.delete_by_name` + `IAccountRepository.find_all` (declared —
  the SQL repo had it, admin_router called it, the port never said so) +
  `count_by_group_name` (a COUNT, not find_all()+len).
* `config/schemas/group_fields.yaml` — all **44 MT5 ConfigGroups fields** +
  our additions, each with type/unit/tab/gating-right/modelled/writable;
  `application/queries/get_field_schema.py` expands enums **from the domain
  code** at read time, so the schema endpoint cannot drift from what the
  domain accepts. This is the UI's form-rendering lever.
* Signature guarantee on the new write path: `test_created_group_exports_to_a_
  valid_mt5_record` and P1 §7 — a group created through the API re-exports to a
  `wire.validate`-clean ConfigGroups record with percent thresholds at MT5 scale.

## 5. Repo hygiene (the twice-lost files, restored and tracked)

* `.gitignore` (repo root) — `.env` can never be committed again (D4's vector).
* `bp/.env.example` — the canonical documented template, restored.
* `.github/workflows/ci.yml` — restored for the third time, monorepo-aware:
  ruff gate → full pytest **with decoded fixtures** (0 skips) → the offline
  proofs incl. both new P1 gates.
* `pyproject.toml` — **F5 fixed**: argon2-cffi + pyotp into runtime deps;
  asyncpg, aiosqlite, hypothesis, httpx into dev. `pip install -e ".[dev]"` on
  a clean machine now yields a runnable suite (psycopg2-binary noted as
  declared-but-unused; removal deferred as a separate decision).
* The four session-4 documents (PROJECT-STATE-v4, ENDPOINTS, ACCOUNT-GROUP-
  CREATION-SPEC, **IDENTITY-BUILD-PLAN — recovered from the dead transcript**,
  it existed nowhere else) are committed under `work/bp/docs/`.

## 6. Defect ledger changes

| | |
|---|---|
| **F3** groups router unmounted | ✅ **FIXED** (mounted, authed, extended) |
| **F5** undeclared deps | ✅ **FIXED** |
| IAccountRepository.find_all undeclared | ✅ declared |
| must_change_password stored-not-enforced | ✅ enforced on the require_right path (login-time enforcement arrives with the manager login route rework) |
| group-type rule duplicated/prefix-based | ✅ one function, MT5's rule |
| **D4** | 🟡 vector closed (.gitignore restored) — the leak at `39c7eaf2` and the export's plaintext passwords still need rotation/purge (user action) |
| D3, D16, D17, F1, F2, F4, F6–F9 | unchanged, still open (F2's *class* is now pinned by the anti-fabrication tests on the admin plane; `get_current_user` itself still fabricates on the client/manager planes) |

## 7. What is deliberately NOT in this milestone

Steps 5–9 of IDENTITY-BUILD-PLAN: entity/mapper/model expansion to the 009
columns, `CreateClientHandler`, `CreateAccountHandler` (login allocator on
`login_counters`, passwords printed once), `CreateManagerHandler` + presets
API + IP enforcement rollout, the account/client/manager read queries and
`/schema` files, Allocations. Also untouched: every trading-path defect
(D16's sweep, F8/F9 PositionGet, the margin four-writer problem).

## 8. New files / changed files

```
NEW  alembic/versions/009_identity_plane.py          reconstructed, idempotent, SQLite-safe
NEW  core/domains/identity/rights.py                 ManagerRightsMask + UserRight + registries
NEW  core/domains/identity/role_presets.py           presets decoded from the live export
NEW  core/domains/identity/group_type.py             the ONE derivation rule + name validation
NEW  core/domains/identity/password_policy.py        MT5's 4-class/8..16 rule
NEW  config/identity/{manager_rights,account_rights,role_presets_builtin,role_presets}.yaml
NEW  config/schemas/group_fields.yaml                the 44 MT5 group fields, as data
NEW  application/queries/get_field_schema.py
NEW  application/commands/update_group.py            Update + Delete handlers
NEW  api/schemas/admin/{__init__,groups}.py
NEW  scripts/dev/extract_identity_yaml.py            regenerates the YAMLs from SDK+export
NEW  scripts/p1_proof_migration_009.py               18 checks
NEW  scripts/p1_proof_identity.py                    59 checks vs the nine real managers
NEW  tests/unit/domains/identity/ (4 files, 39 tests) + tests/fixtures/managers_rights_tctrader_live.json
NEW  tests/unit/api/test_admin_groups_api.py          (10 tests)
NEW  .gitignore · .github/workflows/ci.yml · bp/.env.example · docs/{4 anchor docs}
MOD  core/domains/identity/models.py                 declared fields; ManagerRole demoted
MOD  infrastructure/persistence/account_models.py    db_to_manager/manager_to_db mask-aware
MOD  infrastructure/persistence/mappers.py           (re-exports unchanged; source updated)
MOD  infrastructure/persistence/repositories/{group,account}_repository.py  delete_by_name / count_by_group_name
MOD  infrastructure/config/seeder.py                 first admin via constructor + mask
MOD  infrastructure/mt5/enums.py                     account_type_from_group_path delegates
MOD  application/commands/create_group.py            validation + derivation + duplicate refusal
MOD  api/routers/admin/{groups,admin_router}.py      CRUD+schema+mount; mask-aware serializer
MOD  api/auth/admin_dependencies.py                  require_right + AdminPrincipal
MOD  api/di_providers.py · api/main.py               getters; mount order
MOD  core/ports/interfaces.py                        3 port methods declared
MOD  pyproject.toml                                  F5
```
