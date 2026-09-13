# Forex Broker Platform — PROJECT STATE & CONTEXT ANCHOR v6

**Written:** 2026-09-13 (session 6, at the end of M16 = identity-plan steps 5–7)
**Supersedes:** `PROJECT-STATE-v5.md` (session 5). Read `M16-REPORT.md` for this
milestone in full, and `IDENTITY-BUILD-PLAN.md` for what step 7 onward needs.
v5's §3 (architecture + design law), §5 (decisions not to re-litigate) and §7
(session-death protocol) all still hold unchanged and are not repeated here.

**Sources:** GitHub `rahul82586/references-for-AIs-to-read` @ `e361299` (M15, the
HEAD this session started from) · Drive captures of Qwen sessions 2 and 3 ·
the attached session-5 HTML · gates re-run · **live Neon re-probed column by
column** · `Include.md`, the Administrator guide and the live TCTrader-Live
export read directly, not via a summary.

---

## 0. Verified current state — everything below was RUN, not read

Tree: `qwe-agen-broker-platform-backend/work/bp` — **360 py files / ~73k LOC**,
migrations **001→009**, HTTP paths **33 → 45**.

| Gate | Result (2026-09-13, session 6) |
|---|---|
| `pip install -e ".[dev]"` | clean, no manual extras (F5 fix holds) |
| `pytest tests` (fixtures decoded) | **740 passed, 0 failed, 0 skipped** (was 670; **+70**) |
| `ruff --select E9,F63,F7,F82` | clean |
| `m1_proof_roundtrip_all_sections` | **392/392** byte-identical |
| `m2_proof_seed` / `m3_proof_currencies` / `m3_proof_margin` / `m3_proof_uow` | pass / 362/362 / pass / pass |
| `m8` / `m9` / `m10` / `m11` | 18/18 · 14/14 · 19/19 · 39/39 |
| `m4_proof_order_executes` | SKIP — weekend. Correct. |
| `p1_proof_migration_009` | **24/24** (was 18/18 — restructured, see §3) |
| `p1_proof_identity` | **59/59** |
| **`p1_proof_account_creation` (NEW)** | **72/72** — in CI |
| **`p1_proof_manager_creation` (NEW)** | **80/80** — in CI; your nine real managers as the fixture |
| GitHub Actions CI | ✅ **2 runs `completed/success` on `e361299`** — CI is alive for the first time since M5 built it |

## 0b. Live infrastructure — probed 2026-09-13 (session 6)

Neon PostgreSQL **18.6** reachable. **Every PROJECT-STATE-v5 claim reproduced
exactly:** alembic head `009_identity_plane` · 18 tables · accounts **67** cols ·
clients **32** · groups **58** · managers **24** · `accounts.rights = 0` on all
45 · `login_counters` **EMPTY** · `bars` **0** · 31 open positions, 24 with
`price_current` NULL · 9 reconciliation breaks, all **OPEN** · 37 IN / 9 OUT
deals · 50 orders · 1 manager (login 1000, `First Admin`, `must_change_password`
TRUE, masks `8796093022207 / 8796093022207 / 4398046511103`) · the partial index
`idx_accounts_rights_technical ... WHERE ((rights & 65536)::bigint <> 0)`.

**D16 re-measured, still live:** 24 of 45 accounts where
`equity − balance ≠ Σ(open position profit)`. Deltas: `+800.70 ×10`,
`−749.20 ×9`, `+798.90 ×2`, `+2.10 ×1`, `−0.50 ×1`, `+2.30 ×1`. The first four
match v5's arithmetic exactly (`(1.15968 − 1.07961) × 0.10 × 100 000` and
`(1.15968 − 1.23460) × 0.10 × 100 000`); the last two are small and were not
listed in v5.

**Two facts not in v5:**
* `clients` has **0 rows**, while 45 accounts carry `client_id` values that point
  at nothing. Step 6's `CreateClientHandler` starts from an empty table; the 45
  orphans need an explicit **backfill-or-leave** decision before any client-linked
  read is built (plan step 8).
* The seeded manager row carries **all 128 bits** (`2⁴³−1 / 2⁴³−1 / 2⁴²−1`),
  which is the deliberate legacy wire shape `from_array(["1"]*128)` from M15 §1 —
  **not** the 110-bit Administrator preset decoded from the live export. The
  preset test asserts against the export fixture, so the DB row and the preset are
  different objects by design. Do not "reconcile" them.

---

## 1. Milestone ledger (M0 → M16 + D1 → D18)

M0–M14 and the D15 era are in v5 §1 and are unchanged. **M15** (session 5) =
identity & config plane steps 0–4. **M16 (this session) = steps 5–6:**

* **Step 5** — the 33 IMTUser identity fields on `Account`, the 5 IMTClient
  fields on `Client`, the 27 quarantined ConfigGroups fields on `Group`;
  `AccountModel` 67 columns and `ClientModel` 32, matching live Neon exactly;
  both mapper directions for all of it, in the same change. `rights` is now the
  **single authority** and `is_enabled` a derived view of the `ENABLED` bit.
  All 44 ConfigGroups wire fields have a domain path (0 unmapped); all 53
  `group_fields.yaml` entries are `modelled: true`.
* **Step 6** — `LoginAllocator` (monotonic, atomic `UPDATE…RETURNING`, never
  `MAX+1`, never a reused login) · `CreateClientHandler` ·
  `CreateAccountHandler` (group decides type+currency, `preliminary` refused,
  three passwords generated/group-validated/Argon2-hashed/**plaintext once**,
  rights from the tabs with the two INVERTED bits applied once, NULL≠0 limits,
  COLORREF validated, deposit+ledger in **one transaction**, `AccountCreated`
  and no tick/recompute) · the account/client HTTP plane under `require_right` ·
  `GET /admin/accounts/schema` · `POST /admin/accounts/next-login` ·
  `config/schemas/account_fields.yaml` (60 descriptors) · `LoginCounterModel` ·
  `IClientRepository` + `ILoginAllocator` ports · identity events.

**Defect ledger delta:** **D18 ❌→✅ FIXED (found this session)** ·
**D19 ❌→✅ FIXED (found this session)** · **D3 ❌→✅ FIXED** · D16 ❌ OPEN · D17 ❌ OPEN · D4 🟡 (vector closed, the leak
is still fetchable) · F1/F2/F4/F6/F7/F8/F9 ❌ OPEN · F3 ✅ (M15) · F5 ✅ (M15) ·
everything else as v5.

---

## 2. 🔴 D18 — the defect found and fixed this session

`SqlGroupRepository.save()` rebuilt the row from the entity alone and merged it,
NULLing `mt5_source` / `mt5_scale` / `mt5_extra`. **One** edit to an imported
group (`limit_orders = 500`) erased `Company "TC Trader"`, `CompanyPage`,
`CompanySupportPage`, `PermissionsFlags 2→0`, `DemoLeverage 100→10`,
`DemoDeposit 10000.00→0.00`, `LimitPositionsVolume "0.00"→"0E-8"`, and collapsed
both nested arrays (12-field commissions → 4, 64-field overrides → 11). Wire
fields differing from the original: **5 → 14**. The byte-identical re-export —
the project's signature guarantee — was destroyed for that group.

**M15 made it reachable over HTTP** by mounting `PUT /api/v1/admin/groups/{name}`.

Fix: `save()` calls `_carry_import_owned()`, which reads the stored row inside
the **same session** and carries the import-owned columns forward (merging
`mt5_extra`, stored values winning). `SqlSymbolRepository.save()` had the same
latent shape and is fixed too.

**Root cause of why nothing caught it:** `_seeder_group` in the M1 test file was
a hand-rolled copy of the loader's mapping that set 17 of 44 fields. Fixed by
extraction — `loader.group_from_mt5_record()` is now the ONE builder and the test
delegates to it. *A test that re-implements the code under test only proves the
test agrees with itself.*

**Regressed by:** `test_d18_saving_an_imported_group_preserves_its_mt5_baseline`
(changed-key set must be exactly `{"LimitOrders"}`) and
`test_imported_group_entity_carries_the_servers_real_values`.

---

## 3. Two SDK corrections — both were silent corruption

1. **`USER_RIGHT_DEFAULT` is `0x163`, not `0x3`.** `Include.md`:
   `ENABLED|PASSWORD|TRAILING|EXPERT|REPORTS` — the five boxes MT5's Limits tab
   shows ticked on a fresh account. `ACCOUNT-GROUP-CREATION-SPEC §6` said
   `ENABLED|PASSWORD`, a guess made before `Include.md` was read member by
   member; it would have silently stripped trailing stops, EAs and daily reports
   from every account created. `MT5_USER_RIGHT_DEFAULT` is now the constant and
   `DEFAULT_NEW_ACCOUNT_RIGHTS` aliases it.
2. **`TradeFlags` was missing `DEAL_COST (0x400)` and
   `SO_COMPENSATION_CREDIT (0x800)`**, so `int(TradeFlags(x)) != x` for a live
   group carrying them — flags changed on a read/write cycle.

`MT5_USER_RIGHT_ALL` is built by OR-ing the **named** members because the SDK's
`USER_RIGHT_ALL` deliberately omits `USER_RIGHT_OBSOLETE (0x80)`; a hand-written
magic number got that wrong and `from_flags` **refused** it, which is the guard
working.

**Also:** `Clients and accounts TCTrader-Live.json` contains **only
`ConfigManagers` (9 records)** — there is no live account/client export. Account
field authority is `IMTUser` + the Administrator guide, not a fixture. And
`IMTConManager` has **no** `Name()`/`Rights()` accessor (it has `Right(idx)`);
the export's `Name` and 128-element `Rights` array are export-format artefacts.

---

## 4. 🟠 D3 FIXED — `alembic upgrade head` runs on SQLite

Migrations 001/007 emitted `server_default=sa.text("'{}'::jsonb")`; the cast is
PostgreSQL-only, so `cli migrate` / `make migrate` only ever worked against
PostgreSQL. 23 casts removed — a **no-op on PostgreSQL** (an untyped literal
assigned to a jsonb column is implicitly cast) and legal on SQLite. Neon is at
009 and never re-runs an applied revision, so production is untouched.

That let `p1_proof_migration_009` stop being circular: it built its 008-era
baseline from `create_all`, i.e. **compared the models against themselves**. It
now runs `alembic upgrade 008_reconciliation_breaks` from an empty database and
adds the check that matters — *models and migration agree* — which on its first
run found that **`login_counters` had no ORM model at all**.
`infrastructure/persistence/identity_models.py :: LoginCounterModel` now exists.
18/18 → 24/24.

---

## 5. What is open, in priority order

**P0 — security (user actions; re-verified live this session)**
1. `.env` at `39c7eaf2` still returns **HTTP 200, 523 bytes**, all four secrets
   populated. Rotate Neon/Upstash/`SECRET_KEY`/`ADMIN_API_KEY`; go private or ask
   GitHub Support to purge.
2. The **15 plaintext passwords**, located exactly: `Data Feeds` 4
   `FeedPassword` + 4 `GatewayPassword`; `Gateways` 3 `GatewayPassword` + 3
   `TradingPassword`; `Charts & Ticks` 1 `Password`.
   **Correction to earlier docs:** the "live JWT" is *not* in
   `mt5-format-structure/`; the only JWT in the repo is in
   `chat-and-reference-files/api_test_results.md`.
   **New:** `Security TCTrader-Live.json` publishes the broker's real
   `ConfigFirewall` allow-list — `172.26.0.0/16`, `87.106.157.232` ("DB"),
   `162.55.222.194`, `171.50.169.254` ("Krish").
3. Manager JWT rollout beyond groups/accounts: the admin **reads** still use the
   static key; `must_change_password` is enforced in `require_right` but not at
   login; the client/manager planes still run on `get_current_user` (**F2**
   fabrication).

**P1 — identity plane, plan step 8 onward (step 7 is DONE)**
5. **Step 8:** read queries + `/schema` for account/client/manager — unblocks the
   Theia UI and B2's `/admin/{orders,deals,positions}`. Also fix **F8/F9**
   first: they are the only cross-account positions read the UI has.
6. **`UpdateAccountHandler`:** per-tab partial bodies + the two move rules
   (currency change ⇒ zero balance and no open positions; never across trade
   servers). `UpdateGroupCommand` should also grow the 27 now-modelled fields —
   it is still limited to the pre-step-5 subset, which its own docstring says.
7. **Step 9:** Allocations.
8. **The `clients` = 0 decision** (§0b) before any client-linked read is built.

**P1 — money & correctness (unchanged from v5 §4)**
9. **D16** — the sweep writes equity and never the positions. Fix = call
   `SqlPositionRepository.update_valuation` per priced position; never sweep a
   MOCK-opened position against a live tick. 24/45 Neon accounts are wrong now.
10. The `margin_free`/`margin_level` **four-writer** problem — a design decision,
    not a patch.
11. Stop-out never live-fired · A-Book close never unwinds the hedge
    (`TradeServerLiquidityGateway.close_position` called by nothing) · no
    resting-order lifecycle at the LP · 9 breaks OPEN with no drop-copy/EOD/
    UNKNOWN-resolution · **D17** script portability · `bars` = 0 · WS keepalive
    drops every ~60 s · 19 of ~25 MT5 pre-trade checks missing · commission
    types/charge modes · the gateway config plane (`mt5_gateways` = migration 010).

**P2/P3** — unchanged from v4 §5 items 16–28.

---

## 6. Decisions made this session — do not re-litigate

Everything in v5 §5 still holds. Added:

* `rights` is the **one writer** of `is_enabled`; the column is a mirror for
  external SQL consumers and is **never read back** into the domain.
  `margin_level` is likewise written-but-not-read (D1). Both are pinned by test.
* A **zero** `rights` mask on read falls back to `is_enabled` — for legacy rows
  only. Trusting 0 would silently disable 45 live accounts; that is inventing a
  restriction MT5 never recorded, not refusing to fake one.
* The Group entity owns all **42 scalar** ConfigGroups fields. The nested
  `Commissions` / `Symbols` arrays stay **baseline-owned** and must not be
  rebuilt from the domain until `CommissionRule` models 12 fields and
  `GroupSymbolOverride` models 64.
* `save()` preserves import-owned columns; a repository must never blank what
  only an import can write.
* Login allocation is a **monotonic counter**, never `MAX(login)+1`. A burned
  login (reserved, then the create rolled back) is never reused.
* Plaintext passwords exist only in the create response. There is deliberately
  **no** reveal endpoint — MT5 has none either.
* `/schema` sends right bits as **ints** with an `inverted` flag; credential
  fields are `write_only` but `cert_serial_number` is not.
* Migrations already applied to Neon are edited only when the edit is a provable
  no-op on PostgreSQL (the D3 cast removal).

---

## 7. Reproducing the gates

```bash
cd qwe-agen-broker-platform-backend/work/bp
pip install -e ".[dev]"                      # sufficient since M15 (F5)
export PYTHONPATH=$PWD
python3 - <<'EOF'                            # decode fixtures (UTF-16LE -> UTF-8)
import json, os, pathlib
WS   = pathlib.Path(os.environ.get("ARENA_WORKSPACE") or os.getcwd())
src  = WS/"repo"/"mt5-format-structure"      # or the repo root, wherever it is
out  = WS/"decoded"/"mt5-format-structure"; out.mkdir(parents=True, exist_ok=True)
for f in sorted(src.glob("*.json")):
    raw=f.read_bytes()
    txt=raw.decode("utf-16-le" if raw[:2]==b"\xff\xfe" else "utf-8",errors="replace").lstrip("\ufeff")
    json.loads(txt); (out/f.name).write_text(txt,encoding="utf-8")
EOF
export BROKER_MT5_FIXTURES=<that decoded dir>
export SECRET_KEY=$(python3 -c "import secrets;print(secrets.token_hex(32))")
export ADMIN_API_KEY=$(python3 -c "import secrets;print(secrets.token_hex(24))")
python3 -m pytest tests -q                              # 713 passed
python3 -m ruff check --select E9,F63,F7,F82 .          # clean
python3 scripts/p1_proof_migration_009.py               # 24/24
python3 scripts/p1_proof_identity.py                    # 59/59
python3 scripts/p1_proof_account_creation.py            # 72/72
python3 scripts/m1_proof_roundtrip_all_sections.py      # 392/392
```

### ⚠️ D17 is worse than documented — read this before running anything

The agent sandbox rewrites the **literal string** `/home/user` inside a heredoc
into `"$ARENA_WORKSPACE"`, which produces `SyntaxError` in Python and
`unbound variable` in `set -u` bash. **`HOME` is also `/tmp` in the sandbox**, so
`os.path.expanduser("~")` resolves to the WRONG directory and silently writes
elsewhere. Portable patterns that work in both worlds:

```python
WS = pathlib.Path(os.environ.get("ARENA_WORKSPACE") or os.getcwd())
```
```bash
WS="${ARENA_WORKSPACE:-$(cd "$(dirname "$0")/.." && pwd)}"
```

Also: `curl`/`wget` are absent; use `python3 -m urllib`. `api.wormhole.app` does
not resolve (sandbox DNS allowlist), so a wormhole.app bundle cannot be fetched
from inside a session.

---

## 8. Session-death protocol (unchanged, enforced)

~500 tool calls / ~2.8 MB of transcript kills a session. 1) `git push` at every
milestone, **never the web upload** (it lost CI twice, `.gitignore`/`.env.example`,
and 14 commits → 1). 2) Write `docs/Mn-REPORT.md` early. 3) Update THIS anchor
and push it. 4) New sessions start from a fresh chat with this file pasted.
5) Prefer `scripts/patch_*.py` one-shot idempotent patches over long heredocs.
6) Keep a pushed git bundle. 7) Anything outside the repo is lost — `.git` does
not survive workspace snapshots.

**Note on the wormhole bundle from session 5:** it is **redundant**. Session 5's
handover said pushing would publish `e361299` (M15) + `d13a981` (the bundle).
GitHub HEAD *is* `e361299`; `d13a981` returns 422 and `work/patches/` 404s — so
the bundle's only extra commit is the bundle file itself. All 14 M15 artifacts
were verified present in the clone. **Nothing was lost.**

**Session 6 handover state:** steps 5, 6 and 7 are all committed.

* **On GitHub already:** `fd1b512` (step 5), `dd27011` (step 6). CI is green on
  `dd2701138`.
* **To push:** `ba9505b` (step 7 — the manager plane) and `987255d` (stop
  tracking bundles). Two commits.
* A verified bundle is at `work/patches/repo-full-history.bundle` (5.49 MB,
  "records a complete history", clone-tested: 56 commits, every step-5/6/7 file
  present).

**Bundles are now gitignored, deliberately.** `git bundle create --all` includes
every committed object, so a committed bundle contains the previous bundle and
the file doubles each milestone — measured 5.7 MB → 11.4 MB, which reaches
GitHub's 100 MB hard limit in about five milestones and bloats every clone
forever. An earlier attempt committed one (`fe37bac`); it was never pushed, so
that 5.7 MB blob was rewritten out of the branch rather than published, and
`987255d` records why. The bundle is still created and verified at the end of
every milestone — it just is not tracked. What survives a dead sandbox is
`git push`, which is protocol rule 1.

**Next session: paste THIS file + `docs/M16-REPORT.md` +
`docs/IDENTITY-BUILD-PLAN.md`, then start at plan step 8** — the read queries and
`/schema` endpoints for account/client/manager, which unblock the Theia UI and
B2's `/admin/{orders,deals,positions}`. Fix **F8/F9 first**: `PositionGet` is the
only cross-account positions read the UI has and it currently returns `[]` with
`ticket=0`.

Two things to decide before step 8: the **`clients` = 0 backfill** (§0b), and
`UpdateAccountHandler` (the per-tab partial bodies plus the two move rules) —
plus growing `UpdateGroupCommand` to the 27 fields the entity now models, since
its own docstring still says it is limited to the pre-step-5 subset.
