"""Identity plane step 6 over real HTTP: account & client creation.

What these tests pin, and why each one exists:

* The routers are MOUNTED. F3 was a complete, correct groups router that
  api/main.py never imported, so the endpoint and its handler were unreachable;
  the same mistake on the account plane would be invisible to every unit test of
  the handler. These go through TestClient.
* require_right gates the write path with the SDK's own bit - RIGHT_ACC_MANAGER
  (27) for accounts, RIGHT_CLIENTS_CREATE for clients - and the refusals are the
  anti-F2 ones: a manager without the bit is 403, an unknown manager is 401 and
  is NEVER a fabricated identity.
* THE PASSWORD CONTRACT: the plaintext appears in the create response and
  nowhere else. No GET returns it, the event bus never sees it, and the log never
  does. A password that can be read back is not a secret, and MT5 has no
  "reveal" endpoint either - which is why its own dialog says "save it now".
* The group decides account_type and currency; the caller cannot override either.
* /schema serves the descriptor list INCLUDING which USER_RIGHT bits are
  inverted, so the two SDK bits whose sense is opposite to their label
  (TRADE_DISABLED, TECHNICAL) cannot reach the browser as a bare 0/1.
* next-login is advisory: it does not reserve.

Repositories are in-memory doubles, the pattern test_admin_groups_api.py
established: one world, no event-loop affinity, and the doubles implement only
what the ports declare.
"""
from __future__ import annotations

from decimal import Decimal
from typing import Any, Dict, List, Optional

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from api.auth import admin_dependencies
from api.auth.jwt_handler import create_access_token
from api.di_providers import _container, register_di_providers
from api.routers.admin import accounts as accounts_router
from application.cache.config_cache import ConfigCache, set_config_cache
from core.domains.accounts.account import Account
from core.domains.accounts.client import Client
from core.domains.accounts.enums import AccountType
from core.domains.accounts.group import Group
from core.domains.accounts.login_allocator import AllocatedLogin
from core.domains.accounts.value_objects import MarginProfile
from core.domains.identity.models import ManagerAccount, ManagerRole
from core.domains.identity.rights import ManagerRightsMask
from core.domains.identity.role_presets import builtin_presets

ADMIN_KEY = admin_dependencies.ADMIN_API_KEY_ENV or "test-admin-api-key"
ADMIN_HEADERS = {"X-Admin-API-Key": ADMIN_KEY}
PRESETS = builtin_presets()


# ---------------------------------------------------------------------------
# doubles
# ---------------------------------------------------------------------------


class NullEventBus:
    def __init__(self) -> None:
        self.published: List[Any] = []

    async def publish(self, event) -> None:
        self.published.append(event)

    def subscribe(self, *a, **k):  # pragma: no cover
        pass

    async def subscribe_async(self, *a, **k):  # pragma: no cover
        pass


class MemGroupRepo:
    def __init__(self, groups: List[Group]) -> None:
        self.groups = {g.name: g for g in groups}

    async def find_by_name(self, name, session=None):
        return self.groups.get(name)

    async def get_all(self, session=None):
        return list(self.groups.values())

    async def find_all(self, session=None):
        return list(self.groups.values())

    async def find_by_id(self, gid, session=None):
        return next((g for g in self.groups.values() if g.id == gid), None)

    async def save(self, group, session=None):
        self.groups[group.name] = group
        return group

    async def count_by_group_name(self, name, session=None):
        return 0

    async def delete_by_name(self, name, session=None):  # pragma: no cover
        return self.groups.pop(name, None) is not None


class MemAccountRepo:
    def __init__(self) -> None:
        self.accounts: Dict[str, Account] = {}

    async def find_by_login(self, login, session=None):
        return self.accounts.get(str(login))

    async def save(self, account, session=None):
        self.accounts[str(account.login)] = account
        return account

    async def find_all(self, session=None):
        return list(self.accounts.values())

    async def count_by_group_name(self, name, session=None):
        return sum(1 for a in self.accounts.values() if a.group_id == name)

    async def update_valuation(self, account, session=None, include_margin=False):  # pragma: no cover
        return 1


class MemClientRepo:
    def __init__(self) -> None:
        self.clients: Dict[str, Client] = {}

    async def find_by_id(self, cid):
        return self.clients.get(cid)

    async def find_by_client_id(self, cid):
        return next((c for c in self.clients.values() if c.client_id == cid), None)

    async def save(self, client, session=None):
        self.clients[client.id] = client
        return client

    async def delete(self, cid):  # pragma: no cover
        return self.clients.pop(cid, None) is not None

    async def find_all(self):
        return list(self.clients.values())

    async def count(self):
        return len(self.clients)


class MemLoginAllocator:
    """Port-shaped: next_login reserves, peek does not."""

    def __init__(self, floor: int = 100000) -> None:
        self.floor = floor
        self.cursor = floor
        self.reserved: List[int] = []
        self.peeks = 0

    async def next_login(self, scope=None, *, login_floor=None):
        login = self.cursor
        self.cursor += 1
        self.reserved.append(login)
        return AllocatedLogin(login=login, scope=scope or "global", skipped=0)

    async def peek(self, scope=None, *, login_floor=None):
        self.peeks += 1
        return self.cursor


class MemLedgerRepo:
    def __init__(self) -> None:
        self.rows: List[Any] = []

    async def save(self, operation, session=None):
        self.rows.append(operation)
        return operation

    async def get_by_account(self, login):
        return [r for r in self.rows if r.account_login == str(login)]

    async def get_by_reference(self, ref):  # pragma: no cover
        return None


class FakeUoW:
    """Just enough of UnitOfWork for the handler's `async with uow_factory()`."""

    def __init__(self) -> None:
        self.session = object()
        self.committed = False

    async def __aenter__(self):
        return self

    async def __aexit__(self, *exc):
        self.committed = exc[0] is None
        return False


# ---------------------------------------------------------------------------
# fixture
# ---------------------------------------------------------------------------


def _group(name: str, **kw) -> Group:
    defaults = dict(
        name=name,
        currency="USD",
        currency_digits=2,
        auth_password_min=8,
        margin=MarginProfile(
            margin_call_level=Decimal("50"),
            stop_out_level=Decimal("30"),
            leverage_default=100,
            leverage_max=500,
        ),
    )
    defaults.update(kw)
    return Group(**defaults)


@pytest.fixture()
def world():
    groups = [
        _group("demo\\Standard", account_type=AccountType.DEMO, company="TC Trader"),
        _group("real\\real", account_type=AccountType.REAL),
        _group("preliminary", account_type=AccountType.PRELIMINARY),
        _group("managers\\administrators", account_type=AccountType.MANAGER),
    ]
    bus = NullEventBus()
    providers = {
        "group_repo": MemGroupRepo(groups),
        "account_repo": MemAccountRepo(),
        "client_repo": MemClientRepo(),
        "ledger_repo": MemLedgerRepo(),
        "login_allocator": MemLoginAllocator(),
        "event_bus": bus,
        "uow_factory": FakeUoW,
        "manager_repo": None,
    }
    register_di_providers(providers)
    set_config_cache(ConfigCache(
        group_repo=providers["group_repo"],
        account_repo=providers["account_repo"],
        symbol_repo=None,
        holiday_repo=None,
        position_repo=None,
        event_bus=bus,
    ))

    app = FastAPI()
    app.include_router(accounts_router.accounts_router)
    app.include_router(accounts_router.clients_router)
    providers["_app"] = app
    providers["_client"] = TestClient(app)
    yield providers
    _container.clear() if hasattr(_container, "clear") else None


def _manager_token(rights_names: List[str], login: int = 700001, **kw):
    mask = ManagerRightsMask.empty().grant(*rights_names) if rights_names else ManagerRightsMask.empty()
    defaults = dict(is_active=True, must_change_password=False, allowed_ips=[])
    defaults.update(kw)   # a caller may override must_change_password / allowed_ips
    manager = ManagerAccount(
        manager_id=str(login), login=str(login), role=ManagerRole.READ_ONLY,
        rights=mask, **defaults
    )
    return manager, create_access_token({"sub": str(login), "is_manager": True})


# ---------------------------------------------------------------------------
# 1. the happy path, and the password contract
# ---------------------------------------------------------------------------


def test_create_account_returns_the_plaintext_passwords_exactly_once(world):
    client = world["_client"]
    r = client.post("/api/v1/admin/accounts", headers=ADMIN_HEADERS, json={
        "group_name": "demo\\Standard",
        "first_name": "Priya", "last_name": "Sharma",
        "opening_deposit": "10000.00",
    })
    assert r.status_code == 201, r.text
    body = r.json()
    assert body["login"] == 100000
    assert body["group"] == "demo\\Standard"
    assert body["account_type"] == "demo"          # DERIVED from the group name
    assert body["currency"] == "USD"               # and the currency from the group
    assert set(body["passwords"]) == {"master_password", "investor_password", "phone_password"}
    assert len(set(body["passwords"].values())) == 3
    assert body["warning"], "the response must tell the caller this is the only showing"
    assert body["opening_deposit"] == "10000.00"

    # the ledger row was written in the same call
    assert len(world["ledger_repo"].rows) == 1
    assert world["ledger_repo"].rows[0].amount.amount == Decimal("10000.00")


def test_no_get_returns_the_password_and_the_event_carries_no_secret(world):
    client = world["_client"]
    created = client.post("/api/v1/admin/accounts", headers=ADMIN_HEADERS, json={
        "group_name": "demo\\Standard", "master_password": "S3cret#pass1",
    }).json()
    plaintext = created["passwords"]["master_password"]
    assert plaintext == "S3cret#pass1"

    # the stored account holds a hash, never the plaintext
    stored = world["account_repo"].accounts[str(created["login"])]
    assert stored.password_hash.startswith("$argon2")
    assert plaintext not in stored.password_hash

    # the published event carries no secret of any kind
    events = world["event_bus"].published
    assert len(events) == 1
    assert events[0].event_type.value == "identity.account_created"
    blob = repr(events[0].payload)
    assert plaintext not in blob and "$argon2" not in blob
    assert events[0].payload["login"] == created["login"]


def test_a_created_account_can_be_read_back_but_never_with_its_password(world):
    client = world["_client"]
    created = client.post("/api/v1/admin/accounts", headers=ADMIN_HEADERS,
                          json={"group_name": "real\\real"}).json()
    schema = client.get("/api/v1/admin/accounts/schema", headers=ADMIN_HEADERS).json()
    # Every SECRET descriptor is flagged write_only, so a UI built from the
    # schema knows not to render one as a readable field. The filter is on the
    # Security tab, not on the substring "password": may_change_password and
    # must_change_password are rights-mask booleans whose names merely contain
    # the word, and are correctly readable.
    secrets = [f for f in schema["fields"] if f.get("tab") == "security"]
    assert secrets, "the schema must describe the security tab"
    assert {f["field"] for f in secrets} >= {
        "master_password", "investor_password", "phone_password",
        "webapi_password", "otp_secret", "cert_serial_number",
    }
    # The credential material - and ONLY the credential material - is write_only.
    # A certificate serial number is not a secret (it is a server-maintained
    # identifier an operator needs to read to match a .cer file), so it must NOT
    # be swept into the same flag; a schema that hides everything on the Security
    # tab is as useless to a UI as one that hides nothing.
    CREDENTIALS = {
        "master_password", "investor_password", "phone_password",
        "webapi_password", "otp_secret",
    }
    by_field = {f["field"]: f for f in secrets}
    for name in CREDENTIALS:
        assert name in by_field, f"{name} missing from the security tab"
        assert by_field[name].get("write_only") is True, f"{name} is readable"
    assert by_field["cert_serial_number"].get("write_only") in (None, False)
    # a readable credential would be the leak this whole contract exists to prevent
    leaked = [f["field"] for f in secrets
              if f["field"] in CREDENTIALS and not f.get("write_only")]
    assert not leaked, leaked


# ---------------------------------------------------------------------------
# 2. the group decides, the caller does not
# ---------------------------------------------------------------------------


def test_account_type_and_currency_cannot_be_overridden_by_the_caller(world):
    client = world["_client"]
    r = client.post("/api/v1/admin/accounts", headers=ADMIN_HEADERS, json={
        "group_name": "demo\\Standard",
        "account_type": "real",      # ignored: not a field on the command
        "currency": "EUR",           # ignored: the group's currency wins
    })
    assert r.status_code == 201, r.text
    assert r.json()["account_type"] == "demo"
    assert r.json()["currency"] == "USD"


def test_preliminary_is_refused_without_an_explicit_override(world):
    client = world["_client"]
    r = client.post("/api/v1/admin/accounts", headers=ADMIN_HEADERS,
                    json={"group_name": "preliminary"})
    assert r.status_code == 400
    assert "PROHIBITED" in r.json()["detail"]

    ok = client.post("/api/v1/admin/accounts", headers=ADMIN_HEADERS,
                     json={"group_name": "preliminary", "allow_preliminary": True})
    assert ok.status_code == 201
    assert ok.json()["account_type"] == "preliminary"


def test_unknown_group_is_404_and_a_taken_login_is_400(world):
    client = world["_client"]
    assert client.post("/api/v1/admin/accounts", headers=ADMIN_HEADERS,
                       json={"group_name": "no\\such"}).status_code == 404
    first = client.post("/api/v1/admin/accounts", headers=ADMIN_HEADERS,
                        json={"group_name": "demo\\Standard"}).json()
    r = client.post("/api/v1/admin/accounts", headers=ADMIN_HEADERS,
                    json={"group_name": "demo\\Standard", "login": first["login"]})
    assert r.status_code == 400 and "already taken" in r.json()["detail"]


def test_a_weak_password_is_refused_citing_the_groups_minimum(world):
    client = world["_client"]
    r = client.post("/api/v1/admin/accounts", headers=ADMIN_HEADERS,
                    json={"group_name": "demo\\Standard", "master_password": "abc"})
    assert r.status_code == 400
    detail = r.json()["detail"]
    # The group name arrives repr-escaped (the handler uses !r), so match on the
    # distinctive part rather than on a backslash count.
    assert "min length 8" in detail, detail
    assert "AuthPasswordMin" in detail, detail
    assert "demo" in detail and "Standard" in detail, detail
    # and it lists EVERY violation at once, not just the first - the guide's
    # password rule has four character classes and a length, and a UI that shows
    # one at a time makes the user guess five times.
    assert "no uppercase letter" in detail and "no digit" in detail and "no symbol" in detail


def test_leverage_above_the_group_maximum_is_refused(world):
    client = world["_client"]
    r = client.post("/api/v1/admin/accounts", headers=ADMIN_HEADERS,
                    json={"group_name": "demo\\Standard", "leverage": 10000})
    assert r.status_code == 400 and "exceeds the group maximum" in r.json()["detail"]


# ---------------------------------------------------------------------------
# 3. the rights mask, with the inverted bits the right way round
# ---------------------------------------------------------------------------


def test_limits_tab_booleans_become_the_mask_with_the_inversions_applied(world):
    client = world["_client"]
    plain = client.post("/api/v1/admin/accounts", headers=ADMIN_HEADERS,
                        json={"group_name": "demo\\Standard"}).json()
    stored = world["account_repo"].accounts[str(plain["login"])]
    assert plain["rights"] == int(stored.rights) == 0x163      # SDK USER_RIGHT_DEFAULT
    assert stored.is_enabled and stored.may_trade and not stored.is_technical

    off = client.post("/api/v1/admin/accounts", headers=ADMIN_HEADERS, json={
        "group_name": "demo\\Standard",
        "enable_trading": False,
        "show_to_regular_managers": False,
        "change_password_at_next_login": True,
    }).json()
    acct = world["account_repo"].accounts[str(off["login"])]
    assert acct.trading_disabled is True        # INVERTED bit set by a "false"
    assert acct.is_enabled is True              # ...while it may still connect
    assert acct.may_trade is False
    assert acct.is_technical is True            # INVERTED from show_to_regular_managers
    assert acct.must_change_password is True


def test_schema_marks_exactly_the_two_inverted_bits(world):
    client = world["_client"]
    r = client.get("/api/v1/admin/accounts/schema", headers=ADMIN_HEADERS)
    assert r.status_code == 200
    schema = r.json()
    inverted = {u["name"] for u in schema["user_rights"] if u["inverted"]}
    assert inverted == {"USER_RIGHT_TRADE_DISABLED", "USER_RIGHT_TECHNICAL", "USER_RIGHT_EXCLUDE_REPORTS"}
    # bits are INTS, so a UI can mask against them; strings cannot be masked
    assert all(isinstance(u["bit"], int) for u in schema["user_rights"])
    by_name = {u["name"]: u for u in schema["user_rights"]}
    assert by_name["USER_RIGHT_TECHNICAL"]["bit"] == 65536   # the partial index's bit
    assert schema["default_rights"] == 0x163
    assert "USER_RIGHT_EXPERT" in schema["default_rights_names"]
    assert "USER_RIGHT_TRADE_DISABLED" not in schema["default_rights_names"]
    # and the field list the form renders from
    fields = {f["field"]: f for f in schema["fields"]}
    for needed in ("login", "group_name", "first_name", "residency_status",
                   "limit_orders", "color", "agent_login", "bank_account"):
        assert needed in fields, needed
    assert fields["limit_orders"]["description"].startswith("NULL = inherit")


# ---------------------------------------------------------------------------
# 4. authorisation
# ---------------------------------------------------------------------------


def test_a_manager_without_the_account_bit_gets_403(world):
    client = world["_client"]
    manager, token = _manager_token(["RIGHT_CFG_GROUPS"])       # groups, not accounts
    world["_managers"] = {manager.login: manager}
    _install_manager_lookup(world, {"700001": manager})
    r = client.post("/api/v1/admin/accounts",
                    headers={"Authorization": f"Bearer {token}"},
                    json={"group_name": "demo\\Standard"})
    assert r.status_code == 403, r.text


def test_a_manager_with_the_account_bit_succeeds(world):
    client = world["_client"]
    manager, token = _manager_token(["RIGHT_ACC_MANAGER", "RIGHT_ACC_READ"])
    _install_manager_lookup(world, {"700001": manager})
    r = client.post("/api/v1/admin/accounts",
                    headers={"Authorization": f"Bearer {token}"},
                    json={"group_name": "demo\\Standard"})
    assert r.status_code == 201, r.text


def _install_manager_lookup(world, managers: Dict[str, ManagerAccount]) -> None:
    """Give require_right somewhere to resolve the JWT's manager against.

    Without a wired repository the dependency returns 503 - which is correct and
    is itself asserted below - so an authorisation test has to provide one.
    """
    class _Mem:
        async def find_by_login(self, login, session=None):
            return managers.get(str(login))

        async def get_all(self, session=None):
            return list(managers.values())

    world["manager_repo"] = _Mem()
    register_di_providers({k: v for k, v in world.items() if not k.startswith("_")})


def test_an_unwired_manager_repository_is_503_never_a_fabricated_identity(world):
    """The anti-F2 rule: no manager record means refuse, do not invent one."""
    client = world["_client"]
    _manager, token = _manager_token(["RIGHT_ACC_MANAGER"])
    world["manager_repo"] = None
    register_di_providers({k: v for k, v in world.items() if not k.startswith("_")})
    r = client.post("/api/v1/admin/accounts",
                    headers={"Authorization": f"Bearer {token}"},
                    json={"group_name": "demo\\Standard"})
    assert r.status_code in (401, 503), r.text
    assert r.status_code != 201


def test_must_change_password_blocks_the_create(world):
    client = world["_client"]
    manager, token = _manager_token(["RIGHT_ACC_MANAGER"], login=700002, must_change_password=True)
    _install_manager_lookup(world, {"700002": manager})
    r = client.post("/api/v1/admin/accounts",
                    headers={"Authorization": f"Bearer {token}"},
                    json={"group_name": "demo\\Standard"})
    assert r.status_code == 403, r.text


# ---------------------------------------------------------------------------
# 5. next-login is advisory
# ---------------------------------------------------------------------------


def test_next_login_does_not_reserve(world):
    client = world["_client"]
    alloc = world["login_allocator"]
    before = alloc.cursor
    r = client.post("/api/v1/admin/accounts/next-login", headers=ADMIN_HEADERS)
    assert r.status_code == 200
    assert r.json() == {"login": before, "scope": "global", "reserved": False}
    assert alloc.cursor == before, "peeking must not consume a login"
    assert alloc.peeks == 1 and alloc.reserved == []

    created = client.post("/api/v1/admin/accounts", headers=ADMIN_HEADERS,
                          json={"group_name": "demo\\Standard"}).json()
    assert created["login"] == before, "the create gets the number the button showed"
    assert alloc.reserved == [before]


# ---------------------------------------------------------------------------
# 6. clients
# ---------------------------------------------------------------------------


def test_create_client_then_link_it_to_an_account(world):
    client = world["_client"]
    c = client.post("/api/v1/admin/clients", headers=ADMIN_HEADERS, json={
        "full_name": "Priya Sharma", "middle_name": "R", "country": "India",
        "state": "MH", "city": "Pune", "id_number": "PASS-1", "external_id": "KYC-1",
    })
    assert c.status_code == 201, c.text
    cid = c.json()["id"]
    assert c.json()["middle_name"] == "R" and c.json()["state"] == "MH"

    a = client.post("/api/v1/admin/accounts", headers=ADMIN_HEADERS,
                    json={"group_name": "real\\real", "client_id": cid})
    assert a.status_code == 201, a.text
    assert a.json()["client_id"] == cid


def test_an_inline_client_is_created_with_the_account(world):
    client = world["_client"]
    r = client.post("/api/v1/admin/accounts", headers=ADMIN_HEADERS, json={
        "group_name": "real\\real",
        "client": {"full_name": "Inline Person", "id_number": "PASS-2"},
    })
    assert r.status_code == 201, r.text
    assert r.json()["client_id"]
    assert len(world["client_repo"].clients) == 1


def test_an_anonymous_client_is_refused(world):
    client = world["_client"]
    r = client.post("/api/v1/admin/clients", headers=ADMIN_HEADERS, json={})
    assert r.status_code == 400 and "identifying field" in r.json()["detail"]


def test_a_duplicate_passport_is_refused(world):
    client = world["_client"]
    first = {"full_name": "A", "id_number": "PASS-DUP"}
    assert client.post("/api/v1/admin/clients", headers=ADMIN_HEADERS, json=first).status_code == 201
    r = client.post("/api/v1/admin/clients", headers=ADMIN_HEADERS,
                    json={"full_name": "B", "id_number": "PASS-DUP"})
    assert r.status_code == 400 and "already exists" in r.json()["detail"]


def test_client_create_needs_the_clients_right_not_the_account_right(world):
    """A manager who may create accounts may not necessarily create client records."""
    client = world["_client"]
    manager, token = _manager_token(["RIGHT_ACC_MANAGER"], login=700003)
    _install_manager_lookup(world, {"700003": manager})
    r = client.post("/api/v1/admin/clients",
                    headers={"Authorization": f"Bearer {token}"},
                    json={"full_name": "No Right"})
    assert r.status_code == 403, r.text
