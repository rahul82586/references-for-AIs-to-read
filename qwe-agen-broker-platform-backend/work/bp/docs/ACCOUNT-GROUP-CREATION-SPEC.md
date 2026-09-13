# ACCOUNT & GROUP CREATION — the MT5 model, and what we have

**Built from:** the MT5 SDK (`Database-Interfaces` → `IMTUser`, `Configuration-Interfaces` →
`IMTConManager::EnManagerRights`, `IMTConGroup`), the Administrator guide
(`Accounts/Creating-Account.md`, `Accounts/Editing-Account.md`, `Groups/Group-Types.md`),
the mtapi Manager REST spec (`AccountCreate`, `UserDetails`), and your live
`Clients and accounts TCTrader-Live.json` export.

---

## 1. The thing that fixes the confusion: MT5 has FOUR objects, not one

You asked why the Accounts list shows demo, real, contest, coverage, manager, dealer and admin
all together. It's because in MT5 **they are all trading accounts.** The difference is which
*group* they sit in, and whether a *Manager* record is attached.

```
GROUP  (IMTConGroup)          the rule engine. 44 fields in your live export.
   |                          Its NAME decides the account type (case-sensitive substring):
   |                            contains "demo"        -> demo group
   |                            contains "manager"     -> manager group  <-- only these can hold staff
   |                            contains "contest"     -> contest group
   |                            named "preliminary"    -> the auto-created KYC-pending group
   |                            contains "real"        -> live group
   |                          Trading is PROHIBITED for every symbol in "preliminary".
   v
CLIENT (IMTClient)            the PERSON or COMPANY. KYC lives here.
   |                          One client owns MANY accounts (demo + real + contest)
   |                          without duplicating their passport/address.
   v
ACCOUNT (IMTUser)             the TRADING LOGIN. 67 members in the SDK.
   |                          group, leverage, balance, limits, passwords, the 16-bit user Rights.
   v
MANAGER (IMTConManager)       the STAFF LOGIN. Created ON THE BASIS of a trading account
                              that sits in a `managers\...` group.
                              Carries the 128-bit rights mask + a Groups scope.
```

**Quote, Administrator guide:** *"Manager accounts can only be created on the basis of accounts
that belong to the manager groups."* Your live export has exactly those groups:
`managers\administrators`, `managers\dealers`, `managers\API`.

**So admin vs manager vs dealer is not three account types.** It is three different bits in the
same 128-bit mask on a Manager record:

| Role | The bit that makes it |
|---|---|
| **Administrator** | bit `0` `RIGHT_ADMIN` — may connect with the Administrator terminal |
| **Manager** | bit `1` `RIGHT_MANAGER` — may connect with the Manager terminal |
| **Dealer** | bit `37` `RIGHT_TRADES_DEALER` — dealing activity (requote/confirm) |
| Accountant | bit `24` `RIGHT_ACCOUNTANT` — may move client funds |
| Risk manager | bit `32` `RIGHT_RISK_MANAGER` — sees aggregate + coverage positions |

### Proof: your own 9 managers, decoded

The export stores `Rights` as 128 strings of `"0"`/`"1"`. **The SDK's right number IS the array
index**, so the mask is fully decodable. Applied to your live file:

| login | name | rights | role bits present | notable rights **missing** |
|---|---|---|---|---|
| 1000 | First Admin | 110/128 | ADMIN + MANAGER + DEALER + ACCOUNTANT + RISK | — |
| 2000 | Second Admin | 110/128 | same | — |
| 3000 | Forex Administrator | 110/128 | same | — |
| 19226 | Mojtaba | 110/128 | same | — |
| 208013 | Test223 | 110/128 | same | — |
| 123333 | M1 MN MM | 110/128 | same | — |
| 208011 | **M Manager** | 39/128 | **MANAGER only** | ADMIN(0), ACCOUNTANT(24), trades-edit(30), RISK(32), DEALER(37), accounts-delete(47) |
| 400036 | test color manager dealer | 46/128 | MANAGER + RISK | ADMIN(0), ACCOUNTANT(24), DEALER(37) |
| 400034 | Connection test | 41/128 | **none of the role bits** | ADMIN, MANAGER, accounts read/edit, trades read, clients, KYC — an API/technical login |

Every admin has bits 0–109 set and nothing above; indices 68, 69 and 113–127 are unassigned in
MT5's own enum, which is why 110 is the maximum. **This is your reference data for what a real
"admin" and a real "limited manager" look like.**

---

## 2. The account creation form — every field, and where it belongs

### 2a. The CREATE dialog (MT5 shows only these two boxes)

**Details box:** Preferred Login (`Next` = auto-assign the closest free number — *never reuse a
deleted account's login*), Group, Preferred Client (search an existing client by ID/name/contact,
then link), Name, Last Name, Middle Name, Company, E-Mail, Phone, Country, State, City, Zip code,
Address.

**Passwords box:** Master, Investor (read-only, cannot trade), Phone (for voice-desk identity
checks). **All three are auto-generated** and may be overridden.

**Password rule (hard, from the guide):** four character classes — lowercase, uppercase, digit,
symbol (`# @ ! …`), e.g. `1Ar#pqkj`. Minimum length comes from the **group** setting
(`AuthPasswordMin`), floor of 8, **maximum 16**. Changing a password **resets the account's
connection** to the trade server.

### 2b. The EDIT dialog — 6 tabs, and which backend plane owns each

This is the split you noticed ("few belongs to Backoffice, few to Security"). MT5's own rights
mask encodes it — the tab a manager may see is the rights bit they hold.

| Tab | Fields | Plane | Rights bit that governs it |
|---|---|---|---|
| **Overview** | read-only: personal summary, registered date, last login, **open positions**, current account state, Finteza Visitor ID / Affiliate | read model | 25 `RIGHT_ACC_READ` |
| **Personal** | Name, Last Name, **Middle Name**, Company, **Registered**, **Language**, **Status (RE resident / NR non-resident)**, **ID number** (passport/TIN), **Lead Source**, **Lead Campaign**, **MetaQuotes ID**, E-Mail (comma-separated, 63 chars total), Phone, Country, State, City, Zip code, Address, **Comment** | **Backoffice / KYC** | 26 name · 76 location · 77 address · 78 ID · 79 email · 80 phone · 81 general |
| **Account** | **Group**, **Color** (manager-terminal ticket colour, exported `AABBGGRR`, `FF`=transparent/none, `00`=opaque), **Leverage**, **Bank account**, **Agent account** (who earns agent commission), **Enable this account**, **Allow to change password**, **Enable one-time password**, **Change password at next login**, + **Trade Accounts** sub-table (Gateway ID + external account, with Synchronize All / Balance / Positions / Orders) | **Trading config** | 27 `RIGHT_ACC_MANAGER` |
| **Limits** | **Show to regular managers**, **Include in server reports**, **Enable daily reports**, **Enable trading**, **Enable algo trading by Expert Advisors**, **Enable trailing stops**, **Enable API connections** *(obsolete)*, **Enable sponsored VPS hosting**, **Allow access to subscription data via data feeds**, **Limit total value of positions**, **Limit number of active orders** | **RMS** | 70/71 technical-account rights |
| **Subscriptions** | paid data/service subscriptions on this account | billing | 52/53 |
| **Security** | **Master password**, **Investor password**, **Web API password**, **Phone password**, **OTP secret key** (16 chars, binds one generator; rebinding needs a code from the old one), **Certificate** (Confirm / Reset / Import `.cer`/`.crt`) | **Security** | 27 + group `AuthMode` |

Two rules from the guide that must be enforced, not just displayed:

* **Disabling an account does NOT cancel its pending orders or its SL/TP** (those may have been
  passed to an external system) — but **Stop Out is not performed for a disabled account**, because
  stop-out is the broker's internal risk tool. Same for "Enable trading = off".
* **You cannot move an account to a group with a different deposit currency unless its balance is
  zero and it has no open positions**, and **never between groups on different trade servers.**

### 2c. "Limit total value of positions" — the exact algorithm (worth copying verbatim)

Per symbol, total the value of open positions **and** active pending orders **separately for buy
and sell**, take the **difference** between the two sides, do that for every instrument held,
**sum** the results, compare to the limit. When reached, the platform refuses new orders **only if
executing them could increase the total**.

Value per lot depends on the symbol's calc mode:
* **Forex** → base currency, `contract_size × volume`. EURUSD @ 100,000 ⇒ 1 lot = EUR 100,000.
* **CFD / CFD Leverage / CFD Index / Futures** → also base currency, but contract size isn't money,
  so multiply by **price**. Futures additionally multiply by **tick_value / tick_size**.
  Worked example from the guide: USD base, contract 100, price 33, tick_value/tick_size = 1/0.1 ⇒
  1 lot = `100 × 33 × 10` = **USD 33,000**. A CFD with the same params = `100 × 33` = **USD 3,300**.
* If the symbol's base currency ≠ the account's deposit currency, **convert at the exchange rate**.

"Limit number of active orders" falls back to the **group** limit when unset, and when both are set
**the stricter one wins.**

---

## 3. The account's own permission flags — `IMTUser::EnUsersRights` (16 bits)

This is what the Limits and Account tabs actually write. **A bitmask, not 12 booleans.**

| Hex | Flag | Meaning |
|---|---|---|
| `0x01` | `USER_RIGHT_ENABLED` | may connect at all ("Enable this account") |
| `0x02` | `USER_RIGHT_PASSWORD` | may change their own password |
| `0x04` | `USER_RIGHT_TRADE_DISABLED` | **trading disabled** (note: inverted sense) |
| `0x08` | `USER_RIGHT_INVESTOR` | internal — investor-password session |
| `0x10` | `USER_RIGHT_CONFIRMED` | certificate confirmed |
| `0x20` | `USER_RIGHT_TRAILING` | may use trailing stops |
| `0x40` | `USER_RIGHT_EXPERT` | may use Expert Advisors |
| `0x80` | `USER_RIGHT_OBSOLETE` | unused |
| `0x100` | `USER_RIGHT_REPORTS` | receives daily/monthly reports |
| `0x200` | `USER_RIGHT_READONLY` | internal |
| `0x400` | `USER_RIGHT_RESET_PASS` | **must change password at next login** — blocks ALL action until changed, then auto-clears |
| `0x800` | `USER_RIGHT_OTP_ENABLED` | may use OTP (only if the group allows it) |
| `0x2000` | `USER_RIGHT_SPONSORED_HOSTING` | broker-paid VPS |
| `0x4000` | `USER_RIGHT_API_ENABLED` | Web API — **obsolete, unused** |
| `0x8000` | `USER_RIGHT_PUSH_NOTIFICATION` | push from the trade server |
| `0x10000` | `USER_RIGHT_TECHNICAL` | **technical account** — hidden from managers without `RIGHT_ACC_TECHNICAL` |
| `0x20000` | `USER_RIGHT_EXCLUDE_REPORTS` | excluded from server reports |

`Show to regular managers` = **NOT** `USER_RIGHT_TECHNICAL`. `Include in server reports` =
**NOT** `USER_RIGHT_EXCLUDE_REPORTS`.

---

## 4. The Manager REST API's create shape (mtapi `AccountCreate`)

Everything is a **query parameter**, not a JSON body. Required: `id` (the Connect token),
`master_pass`, `investor_pass`. Optional: `enabled, ClientID, FirstName, LastName, MiddleName,
OTPSecret, LimitOrders, LimitPositionsValue, Login, Group, CertSerialNumber, Rights, Registration,
LastAccess, LastIP, Name, Company, Account, Country, Language, City, State, ZIPCode, Address,
Phone, EMail, ID, Status, Comment, Color, PhonePassword, Leverage, Agent, Balance, Credit,
InterestRate`.

Note what this tells you: `Login` is **optional** (server assigns), `Rights` is the user bitmask,
`Color` is an int, `Agent` is a login, `Balance`/`Credit` can be seeded at creation, and
`ClientID` links to an existing client. **Our REST shape should accept a JSON body** — that's the
documented decision (mtapi is kept for ergonomics and the coverage checklist, the SDK for schema
authority) — but these field names are the parity target.

---

## 5. What we actually have, field by field

### Objects

| Object | Domain entity | DB table | Verdict |
|---|---|---|---|
| Group | `core/domains/accounts/group.py` — 20 fields + nested `MarginProfile`, `TradeFlags`, `GroupPermissions`, `SwapConfiguration`, `RoutingRule`, `commissions[]`, `symbol_overrides[]` | `groups` — **47 columns** | 🟢 DB is rich enough for MT5's 44; the **domain entity is thin** |
| Client | `core/domains/accounts/client.py` — 22 fields | `clients` | 🟡 exists, missing fields below |
| Account | `core/domains/accounts/account.py` — ~30 fields | `accounts` | 🟡 exists, missing fields below |
| Manager | `core/domains/identity/models.py :: ManagerAccount` — 10 declared fields | `managers` — `rights_json` + **3× 64-bit masks** + `group_scope_json` + `mailbox`, `server_id`, `name`, `request_limit_logs/reports`, `must_change_password` | 🟢 **DB is complete and correct**; 🟠 the entity doesn't declare them — `db_to_manager` attaches them dynamically, so everything downstream uses `getattr(...)` |

### Group — MT5's 44 real fields vs us

Present in your live export: `Group, Server, PermissionsFlags, AuthMode, AuthPasswordMin,
AuthOTPMode, Company, CompanyPage, CompanyEmail, CompanySupportPage, CompanySupportEmail,
CompanyCatalog, CompanyDepositURL, CompanyWithdrawalURL, Currency, CurrencyDigits, ReportsMode,
ReportsFlags, ReportsEmail, NewsMode, NewsCategory, NewsLangs, MailMode, TradeFlags,
TradeTransferMode, TradeInterestrate, TradeVirtualCredit, MarginMode, MarginFlags, MarginSOMode,
MarginFreeMode, MarginCall, MarginStopOut, MarginFreeProfitMode, DemoLeverage, DemoDeposit,
DemoTradesClean, LimitHistory, LimitOrders, LimitSymbols, LimitPositions, LimitPositionsVolume,
Commissions, Symbols`.

**Modelled:** Currency, CurrencyDigits, MarginMode/SOMode/FreeMode/Call/StopOut, TradeFlags,
LimitOrders/Symbols/Positions, Commissions, Symbols (overrides), NewsMode, Server, Permissions.
**Not modelled (quarantined, so they re-export fine but the UI can't edit them):**
`AuthMode`, `AuthPasswordMin`, `AuthOTPMode` ← **needed for the password rule**, the 8 `Company*`
fields ← **the Group modal's Company tab**, `ReportsMode/Flags/Email`, `MailMode`,
`TradeTransferMode`, `TradeInterestrate`, `TradeVirtualCredit`, `MarginFlags`,
`MarginFreeProfitMode`, `DemoLeverage`, `DemoDeposit`, `DemoTradesClean`, `LimitHistory`,
**`LimitPositionsVolume`**.

### Account — missing vs `IMTUser`'s 67 members

`Rights` (the 16-bit mask — **we have a single `is_enabled` bool instead**), `Color`, `Agent`,
`Account` (bank account), `LimitOrders`, `LimitPositionsValue`, `InterestRate`, `Status` (RE/NR),
`Language`, `ID`, `LeadSource`, `LeadCampaign`, `MQID`, `VisitorID`, `LastAccess`, `LastIP`,
`LastPassChange`, `CertSerialNumber`, `OTPSecret`, `Registration`, `BalancePrevDay/Month`,
`EquityPrevDay/Month`, `CommissionDaily/Monthly`, `CommissionAgentDaily/Monthly`, the 7
`ExternalAccount*` members (the **Trade Accounts** sub-table), and the 6 `APIData*` members.

### Client — missing

`MiddleName`, `State`, `ID number`, `LeadSource`, `LeadCampaign`, `Status` is present, and there
is **no documents sub-entity** at all (`RIGHT_DOCUMENTS_*`, bits 100–105, assume one).

### Wrong object

`investor_password_hash`, `phone_password_hash` and `otp_secret` are on **Client**. In MT5 they are
on **IMTUser (the account)** — `PasswordHash`, `PhonePassword`, `OTPSecret`. Investor access is
per-account, not per-person: one client with a demo and a real account has two investor passwords.
**This will bite the moment you build the Security tab.**

### Handlers

| Needed | Status |
|---|---|
| `CreateGroupHandler` | ✅ **exists** — `application/commands/create_group.py`, and `POST /api/v1/admin/groups/create` is written… but **the router is never mounted** (bug F3). One line in `api/main.py`. |
| `CreateAccountHandler` | ❌ does not exist |
| `CreateClientHandler` | ❌ does not exist (and `SqlClientRepository` says so in its own docstring: *"There is no IClientRepository port yet; adding one is part of wiring CreateClientHandler"*) |
| `CreateManagerHandler` | ❌ does not exist. The first admin is bootstrapped by `cli seed` (password printed once, Argon2 stored) — that pattern is correct and should be reused |
| login allocation ("Next") | ❌ no next-free-login allocator |
| password policy | ❌ no 4-class / min-from-group / max-16 validation anywhere |
| group-type derivation from name | ✅ exists in the seeder (`test_account_type_is_derived_from_the_group_path`) — **must be reused by `CreateGroupHandler`, not duplicated** |

---

## 6. The fireproof creation flow

Order matters. Each step refuses rather than guesses.

**Group create**
1. Validate the name: non-empty, ≤ 64 chars, path segments separated by `\`, no leading/trailing `\`.
2. **Derive the account type from the name substring** (demo / manager / contest / preliminary /
   real), case-sensitive — one function, the seeder's, reused. Never let the caller pass a type
   that contradicts the name; MT5 wouldn't honour it.
3. Validate the money fields: `MarginCall > MarginStopOut`, both percent, both > 0.
   `AuthPasswordMin` in 8..16.
4. Refuse a duplicate name. Refuse deleting/renaming a group that has accounts.
5. Persist. **Re-export the group and assert it round-trips** — that is the project's signature
   guarantee and a new write path is exactly where it gets broken.

**Client create** — optional. If a client is supplied, link; else create one. KYC fields only.
Never store a password here (see "wrong object" above).

**Account create**
1. **Allocate the login**: `Next` → the closest free number above the group's floor. Never reuse a
   deleted login. Do this under a DB constraint or a sequence, not a `MAX(login)+1` read.
2. **Validate the group exists and is active.** Refuse `preliminary` for a manually-created real
   account unless that's the intent (preliminary is for terminal-opened KYC-pending accounts and
   prohibits trading on every symbol).
3. **Passwords**: generate Master + Investor + Phone if not supplied. Validate 4 character classes,
   length `group.AuthPasswordMin`..16. Store **Argon2** hashes only. **Return the plaintext exactly
   once, in the create response**, and never again — the `cli seed` first-admin pattern.
4. **Rights**: build the 16-bit mask from the Limits/Account tab booleans. Default
   `ENABLED | PASSWORD`. Set `RESET_PASS` if "change at next login" was ticked.
5. **Limits**: `LimitOrders` and `LimitPositionsValue` default to *unset*, meaning "inherit the
   group". Store NULL, not 0 — 0 means "no orders allowed", which is a different thing.
6. Colour stored as the `AABBGGRR` int, exactly as MT5 exports it.
7. Persist client → account → (optional) balance operation for the opening deposit, **in one
   transaction**. An account with a balance and no ledger entry is how you get an unreconcilable book.
8. Emit `AccountCreated`. Do **not** emit a tick or a margin recompute.

**Manager create**
1. Require an existing **trading account in a `managers\...` group**. Refuse otherwise — that is
   MT5's rule and it is what keeps staff logins out of the client account list.
2. Take the 128-bit rights as a **list of named rights**, not indices: the API accepts
   `["RIGHT_ADMIN","RIGHT_MANAGER",…]`, the server maps names → indices using the SDK table, and
   stores both `rights_json` (for export fidelity) and the three masks (for querying).
3. Ship three **presets** so the UI is a dropdown, not 128 checkboxes:
   *Administrator* = bits 0–109 (your export's 110/128) · *Manager* = the 39-bit set from login
   208011 · *Dealer* = Manager + `RIGHT_TRADES_DEALER(37)` + `RIGHT_TRADES_SUPERVISOR(42)` +
   `RIGHT_QUOTES(31)`.
4. `Groups` scope defaults to `["*"]`; a real deployment narrows it.
5. Password printed once. `must_change_password` set on first issue — and **actually enforced at
   login**, which today it is not (it's stored and ignored).

---

## 7. Endpoints this needs

Admin plane, `X-Admin-API-Key` (later: manager JWT + rights enforcement).

```
POST   /api/v1/admin/groups                     create a group
GET    /api/v1/admin/groups                     list            (exists)
GET    /api/v1/admin/groups/{name}              one             (exists)
PUT    /api/v1/admin/groups/{name}              update
DELETE /api/v1/admin/groups/{name}              delete (refuse if it has accounts)
GET    /api/v1/admin/groups/schema              the 44 MT5 field descriptors, so the UI builds
                                                the form from the server instead of hardcoding it
POST   /api/v1/admin/groups/{name}/symbols      per-group symbol override (SpreadDiff etc.)

POST   /api/v1/admin/clients                    create/link a client
GET    /api/v1/admin/clients                    list
GET    /api/v1/admin/clients/{id}               one, with their accounts

POST   /api/v1/admin/accounts                   create  -> returns the plaintext passwords ONCE
GET    /api/v1/admin/accounts                   list    (exists, needs filters + pagination)
GET    /api/v1/admin/accounts/{login}           one, full tab payload
PUT    /api/v1/admin/accounts/{login}           update, per-tab partial bodies accepted
DELETE /api/v1/admin/accounts/{login}           delete
POST   /api/v1/admin/accounts/next-login        allocate the next free login ("Next" button)
POST   /api/v1/admin/accounts/{login}/password  change master/investor/phone/webapi
POST   /api/v1/admin/accounts/{login}/balance   deposit / credit / correction (writes a ledger row)
GET    /api/v1/admin/accounts/schema            field descriptors + the 16 user-right flags

POST   /api/v1/admin/managers                   create from an existing manager-group account
GET    /api/v1/admin/managers                   list    (exists, returns real rights counts)
GET    /api/v1/admin/managers/{login}           one, with rights DECODED to names
PUT    /api/v1/admin/managers/{login}           update rights / group scope
GET    /api/v1/admin/managers/rights            the ~100 named rights with index + description,
                                                grouped by plane -> drives the UI's checkbox tree
GET    /api/v1/admin/managers/presets           Administrator / Manager / Dealer presets
```

The two `/schema` and one `/rights` endpoints are the lever: **the UI renders the form from the
server's descriptor list**, so adding a field is a backend change only and the 0/1 problem you
hit never reaches the frontend — it gets names, types, units, enums and which rights bit gates it.
