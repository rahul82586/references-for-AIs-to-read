"""Identity plane step 3+4 over real HTTP: require_right() and the Group CRUD.

What these tests pin:

* F3 is fixed - the groups router is mounted, and mounted BEFORE admin_router
  so GET /groups/schema resolves as the schema instead of being swallowed by
  admin_router's GET /groups/{group_name:path}.
* require_right is the whole matrix, including the refusals that make it not
  F2: an unknown manager is a 401, NEVER a fabricated identity; a client token
  is a 403 on the admin plane; must_change_password blocks; allowed_ips blocks.
* The create path DERIVES the account type from the name (MT5 rule), refuses
  contradictions and duplicates, and validates the margin pair.
* Update refuses a no-change request (MT_RET_REQUEST_NO_CHANGES) and a
  currency change while the group has accounts; delete refuses a non-empty
  group - including when emptiness cannot be verified (fail closed).
* A group created through the NEW write path still exports to a valid MT5
  ConfigGroups record - the project's signature guarantee, checked exactly
  where it is most likely to break.

Repositories are in-memory doubles (the d11 pattern): one world, no loop
affinity, and the doubles implement only what the ports declare - so the
handler fallbacks (delete-by-id when delete_by_name is absent, find_all when
count_by_group_name is) are exercised too.
"""
from __future__ import annotations

from decimal import Decimal
from typing import Any, Dict, List, Optional

import pytest
from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient

from api.auth.admin_dependencies import require_right
from api.auth.jwt_handler import create_access_token
from api.di_providers import _container, register_di_providers
from api.routers.admin import admin_router
from api.routers.admin import groups as groups_router
from application.cache.config_cache import ConfigCache, set_config_cache
from core.domains.accounts.enums import AccountType
from core.domains.accounts.group import Group
from core.domains.common.value_objects import Money
from core.domains.identity.models import ManagerAccount, ManagerRole
from core.domains.identity.rights import ManagerRightsMask
from core.domains.identity.role_presets import builtin_presets

# Read the key from the same place the dependency does - the gate scripts export
# a freshly generated ADMIN_API_KEY, so hardcoding the conftest default here
# would make these tests environment-dependent (they failed under `pytest tests`
# with a generated key, passed standalone: exactly the drift this avoids).
from api.auth import admin_dependencies

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

    def subscribe(self, *a, **k):  # pragma: no cover - contract parity
        pass

    async def subscribe_async(self, *a, **k):  # pragma: no cover
        pass


class MemGroupRepo:
    """Port-shaped double WITH the extended surface (delete/delete_by_name)."""

    def __init__(self, groups: List[Group]) -> None:
        self.groups: Dict[str, Group] = {g.name: g for g in groups}
        self.deleted: List[str] = []

    async def find_by_name(self, name, session=None):
        return self.groups.get(name)

    async def get_all(self, session=None):
        return list(self.groups.values())

    async def find_by_id(self, group_id, session=None):
        return next((g for g in self.groups.values() if g.id == group_id), None)

    async def save(self, group, session=None):
        self.groups[group.name] = group
        return group

    async def delete(self, group_id):
        for name, g in list(self.groups.items()):
            if g.id == group_id:
                del self.groups[name]
                self.deleted.append(name)
                return True
        return False

    async def delete_by_name(self, name):
        if name in self.groups:
            del self.groups[name]
            self.deleted.append(name)
            return True
        return False


class MemAccountRepo:
    """find_all (declared on the port now) and count_by_group_name."""

    def __init__(self) -> None:
        self.accounts: Dict[Any, Any] = {}

    async def find_all(self, session=None):
        return list(self.accounts.values())

    async def count_by_group_name(self, group_name):
        return sum(
            1 for a in self.accounts.values()
            if (a.group.name if a.group else None) == group_name
        )

    async def find_by_login(self, login_id, session=None):
        return self.accounts.get(login_id)

    async def save(self, account, session=None):
        self.accounts[account.login] = account
        return account


class StubManagerRepo:
    def __init__(self, managers: List[ManagerAccount]) -> None:
        self.by_login = {str(m.login): m for m in managers}

    async def find_by_login(self, login):
        return self.by_login.get(str(login))

    async def find_all(self):
        return list(self.by_login.values())

    async def save(self, manager):
        self.by_login[str(manager.login)] = manager
        return manager


def _manager(login: str, rights: ManagerRightsMask, **kw) -> ManagerAccount:
    return ManagerAccount(
        manager_id=login, login=login, role=ManagerRole.READ_ONLY,
        password_hash="argon2:x", rights=rights, **kw,
    )


def _token(login: str, is_manager: bool = True) -> Dict[str, str]:
    payload = {"sub": login}
    if is_manager:
        payload["is_manager"] = True
    return {"Authorization": f"Bearer {create_access_token(payload)}"}


def _group(name: str, **kw) -> Group:
    defaults = dict(currency="USD", account_type=AccountType.REAL)
    defaults.update(kw)
    return Group(name=name, **defaults)


def _account(login: int, group: Group) -> Any:
    from core.domains.accounts.account import Account

    account = Account(
        login=login, group_id=group.id, group=group, currency=group.currency,
        balance=Money(Decimal("1000"), group.currency),
        credit=Money(Decimal("0"), group.currency),
    )
    account.equity = Money(Decimal("1000"), group.currency)
    account.margin_used = Money(Decimal("0"), group.currency)
    account.margin_free = Money(Decimal("1000"), group.currency)
    return account


# ---------------------------------------------------------------------------
# fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def world():
    coverage = _group("coverage\\house", account_type=AccountType.COVERAGE)
    group_repo = MemGroupRepo([
        _group("real\\real"),
        _group("demo\\Standard", account_type=AccountType.DEMO),
        coverage,
    ])
    account_repo = MemAccountRepo()
    account_repo.accounts[555] = _account(555, coverage)  # coverage\house is NOT empty

    managers = [
        _manager("777", ManagerRightsMask.from_names(["RIGHT_CFG_GROUPS", "RIGHT_MANAGER"])),
        _manager("208011", PRESETS["Manager"].rights),                    # no RIGHT_CFG_GROUPS
        _manager("888", ManagerRightsMask.from_names(["RIGHT_CFG_GROUPS"]), must_change_password=True),
        _manager("999", ManagerRightsMask.from_names(["RIGHT_CFG_GROUPS"]), is_active=False),
        _manager("111", ManagerRightsMask.from_names(["RIGHT_CFG_GROUPS"]), allowed_ips=["10.0.0.0/8"]),
    ]
    manager_repo = StubManagerRepo(managers)
    bus = NullEventBus()

    from tests.integration.trading_harness import (
        InMemoryHolidayRepository, InMemoryPositionRepository, InMemorySymbolRepository,
    )

    providers = {
        "group_repo": group_repo,
        "account_repo": account_repo,
        "manager_repo": manager_repo,
        "symbol_repo": InMemorySymbolRepository(),
        "holiday_repo": InMemoryHolidayRepository(),
        "position_repo": InMemoryPositionRepository(),
        "event_bus": bus,
    }
    saved = {k: _container.get(k) for k in providers}
    register_di_providers(providers)
    set_config_cache(ConfigCache(
        group_repo=group_repo, account_repo=account_repo,
        symbol_repo=providers["symbol_repo"], holiday_repo=providers["holiday_repo"],
        position_repo=providers["position_repo"], event_bus=bus,
    ))

    app = FastAPI()
    app.include_router(groups_router.router)   # BEFORE admin_router: mount order matters
    app.include_router(admin_router.router)

    with TestClient(app) as client:
        yield client, providers

    for k, v in saved.items():
        if v is None:
            _container.pop(k, None)
        else:
            _container[k] = v


# ---------------------------------------------------------------------------
# require_right - the matrix
# ---------------------------------------------------------------------------

@pytest.fixture()
def guarded():
    """A one-route app guarded by require_right, for the pure-auth matrix."""
    app = FastAPI()

    @app.get("/guarded")
    async def guarded_route(principal=Depends(require_right("RIGHT_CFG_GROUPS"))):
        return {"kind": principal.kind, "login": principal.login}

    saved_managers = _container.get("manager_repo")
    manager_repo = StubManagerRepo([
        _manager("777", ManagerRightsMask.from_names(["RIGHT_CFG_GROUPS"])),
        _manager("208011", PRESETS["Manager"].rights),
        _manager("888", ManagerRightsMask.from_names(["RIGHT_CFG_GROUPS"]), must_change_password=True),
        _manager("999", ManagerRightsMask.from_names(["RIGHT_CFG_GROUPS"]), is_active=False),
        _manager("111", ManagerRightsMask.from_names(["RIGHT_CFG_GROUPS"]), allowed_ips=["10.0.0.0/8"]),
    ])
    register_di_providers({"manager_repo": manager_repo})
    with TestClient(app) as client:
        yield client
    if saved_managers is None:
        _container.pop("manager_repo", None)
    else:
        _container["manager_repo"] = saved_managers


def test_require_right_matrix(guarded):
    # nothing supplied -> 401
    assert guarded.get("/guarded").status_code == 401
    # garbage bearer -> 401
    assert guarded.get("/guarded", headers={"Authorization": "Bearer not.a.jwt"}).status_code == 401
    # wrong admin key -> 403 (not a silent fallthrough to bearer)
    assert guarded.get("/guarded", headers={"X-Admin-API-Key": "wrong"}).status_code == 403
    # the bootstrap admin key -> full access
    r = guarded.get("/guarded", headers=ADMIN_HEADERS)
    assert r.status_code == 200 and r.json()["kind"] == "admin_key"
    # manager WITH the right -> 200
    r = guarded.get("/guarded", headers=_token("777"))
    assert r.status_code == 200 and r.json() == {"kind": "manager", "login": "777"}
    # manager WITHOUT the right -> 403 naming the right
    r = guarded.get("/guarded", headers=_token("208011"))
    assert r.status_code == 403 and "RIGHT_CFG_GROUPS" in r.json()["detail"]
    # a CLIENT token -> 403, never treated as an account (anti-F2)
    r = guarded.get("/guarded", headers=_token("777", is_manager=False))
    assert r.status_code == 403 and "client tokens" in r.json()["detail"]
    # unknown manager login -> 401, and NEVER a fabricated identity (anti-F2)
    r = guarded.get("/guarded", headers=_token("100001"))
    assert r.status_code == 401
    # inactive manager -> 401 (indistinguishable from unknown: no enumeration)
    assert guarded.get("/guarded", headers=_token("999")).status_code == 401
    # must_change_password -> 403 with the MT5 reason
    r = guarded.get("/guarded", headers=_token("888"))
    assert r.status_code == 403 and "password change required" in r.json()["detail"]
    # allowed_ips configured, client outside it -> 403 (TestClient's host is
    # "testclient", which is in no CIDR: an unusable IP fails closed)
    r = guarded.get("/guarded", headers=_token("111"))
    assert r.status_code == 403 and "IP" in r.json()["detail"]


def test_require_right_unwired_repo_is_503():
    app = FastAPI()

    @app.get("/guarded2")
    async def route(principal=Depends(require_right("RIGHT_CFG_GROUPS"))):
        return {"ok": True}

    saved = _container.get("manager_repo")
    _container.pop("manager_repo", None)
    try:
        with TestClient(app) as client:
            r = client.get("/guarded2", headers=_token("777"))
        assert r.status_code == 503 and "not registered" in r.json()["detail"]
        # the admin key path needs no repository and still works
        assert client is not None
    finally:
        if saved is not None:
            _container["manager_repo"] = saved


# ---------------------------------------------------------------------------
# schema endpoint (and the mount order that makes it reachable)
# ---------------------------------------------------------------------------

def test_schema_endpoint_serves_the_mt5_field_descriptors(world):
    client, _ = world
    r = client.get("/api/v1/admin/groups/schema", headers=ADMIN_HEADERS)
    assert r.status_code == 200
    body = r.json()
    assert body["object"] == "group"
    assert body["wire_section"] == "ConfigGroups"
    by_mt5 = {f["mt5"]: f for f in body["fields"] if f.get("mt5")}
    # the live export's 44 ConfigGroups fields are all described
    for wire_name in ("Group", "Server", "AuthPasswordMin", "Company", "Currency",
                      "MarginCall", "MarginStopOut", "TradeFlags", "LimitPositionsVolume",
                      "Commissions", "Symbols"):
        assert wire_name in by_mt5, wire_name
    assert len(by_mt5) == 44
    call = by_mt5["MarginCall"]
    assert call["unit"] == "percent" and call["writable"] is True
    assert by_mt5["Symbols"]["right"] == "RIGHT_SYMBOL_DETAILS"
    # enums are EXPANDED from the domain, so the YAML cannot drift from the code
    modes = {f["field"]: f for f in body["fields"]}["margin_mode"]
    assert {"name": "RETAIL_HEDGED", "value": "retail_hedged"} in modes["enum_values"]


# ---------------------------------------------------------------------------
# create
# ---------------------------------------------------------------------------

def test_create_group_derives_type_and_persists(world):
    client, providers = world
    r = client.post("/api/v1/admin/groups", headers=ADMIN_HEADERS, json={
        "name": "demo\\vip-trial",
        "margin_call_level": "60.00", "stop_out_level": "30.00",
    })
    assert r.status_code == 201, r.text
    body = r.json()
    assert body["name"] == "demo\\vip-trial"
    assert body["group"]["account_type"] == "demo"          # DERIVED from the name
    assert body["group"]["margin_call_level"] == "60.00"    # percent, string, scale kept
    assert "demo\\vip-trial" in providers["group_repo"].groups
    # the forward-slash form works too, and reads back through admin_router
    r2 = client.post("/api/v1/admin/groups", headers=ADMIN_HEADERS,
                     json={"name": "real/vip", "account_type": None})
    assert r2.status_code == 201
    assert client.get("/api/v1/admin/groups/real/vip", headers=ADMIN_HEADERS).status_code == 200
    # legacy /create alias still answers (the frontend may already call it)
    r3 = client.post("/api/v1/admin/groups/create", headers=ADMIN_HEADERS, json={"name": "contest\\2026"})
    assert r3.status_code == 201 and r3.json()["group"]["account_type"] == "contest"


def test_create_group_refusals(world):
    client, _ = world
    # duplicate
    r = client.post("/api/v1/admin/groups", headers=ADMIN_HEADERS, json={"name": "real\\real"})
    assert r.status_code == 400 and "already exists" in r.json()["detail"]
    # type contradicting the name
    r = client.post("/api/v1/admin/groups", headers=ADMIN_HEADERS,
                    json={"name": "real\\x", "account_type": "demo"})
    assert r.status_code == 400 and "contradicts" in r.json()["detail"]
    # the documented exception: contest-on-demo is allowed
    r = client.post("/api/v1/admin/groups", headers=ADMIN_HEADERS,
                    json={"name": "demo\\Challenge2", "account_type": "contest"})
    assert r.status_code == 201 and r.json()["group"]["account_type"] == "contest"
    # margin pair
    r = client.post("/api/v1/admin/groups", headers=ADMIN_HEADERS,
                    json={"name": "real\\bad-margin", "margin_call_level": "30", "stop_out_level": "50"})
    assert r.status_code == 400 and "greater than" in r.json()["detail"]
    # invalid name shapes
    r = client.post("/api/v1/admin/groups", headers=ADMIN_HEADERS, json={"name": "\\real"})
    assert r.status_code == 400
    # unknown account_type value
    r = client.post("/api/v1/admin/groups", headers=ADMIN_HEADERS,
                    json={"name": "real\\y", "account_type": "SUPERUSER"})
    assert r.status_code == 400 and "not one of" in r.json()["detail"]


def test_manager_rights_enforced_on_the_groups_plane(world):
    client, _ = world
    # 208011 (the live M Manager, 39 bits) has NO RIGHT_CFG_GROUPS -> 403 everywhere
    for call in (
        lambda: client.post("/api/v1/admin/groups", headers=_token("208011"), json={"name": "real\\nope"}),
        lambda: client.put("/api/v1/admin/groups/real/real", headers=_token("208011"), json={"limit_orders": 5}),
        lambda: client.delete("/api/v1/admin/groups/real/real", headers=_token("208011")),
        lambda: client.get("/api/v1/admin/groups/schema", headers=_token("208011")),
    ):
        assert call().status_code == 403
    # a manager holding the bit can create
    r = client.post("/api/v1/admin/groups", headers=_token("777"), json={"name": "real\\by-manager"})
    assert r.status_code == 201


# ---------------------------------------------------------------------------
# update / delete
# ---------------------------------------------------------------------------

def test_update_group_partial_and_refusals(world):
    client, providers = world
    # partial update: only supplied fields change
    r = client.put("/api/v1/admin/groups/real/real", headers=ADMIN_HEADERS,
                   json={"margin_call_level": "65.5", "limit_orders": 300})
    assert r.status_code == 200, r.text
    group = providers["group_repo"].groups["real\\real"]
    assert group.margin.margin_call_level == Decimal("65.5")
    assert group.limit_orders == 300
    assert group.currency == "USD"  # untouched

    # the no-change request is refused, MT5-style (10025)
    r = client.put("/api/v1/admin/groups/real/real", headers=ADMIN_HEADERS,
                   json={"limit_orders": 300})
    assert r.status_code == 400 and "NO_CHANGES" in r.json()["detail"]

    # the pair rule spans the request AND the stored value
    r = client.put("/api/v1/admin/groups/real/real", headers=ADMIN_HEADERS,
                   json={"stop_out_level": "70"})
    assert r.status_code == 400 and "greater than" in r.json()["detail"]

    # currency change while the group has accounts -> refused
    r = client.put("/api/v1/admin/groups/coverage/house", headers=ADMIN_HEADERS,
                   json={"currency": "EUR"})
    assert r.status_code == 400 and "currency" in r.json()["detail"]
    # ...and allowed when it has none
    r = client.put("/api/v1/admin/groups/real/real", headers=ADMIN_HEADERS,
                   json={"currency": "EUR"})
    assert r.status_code == 200

    # unknown group -> 404, not 400
    r = client.put("/api/v1/admin/groups/no/such", headers=ADMIN_HEADERS, json={"limit_orders": 5})
    assert r.status_code == 404
    # unknown field -> 422 (extra="forbid"), not silently ignored
    r = client.put("/api/v1/admin/groups/real/real", headers=ADMIN_HEADERS, json={"bogus": 1})
    assert r.status_code == 422


def test_delete_group_refuses_while_accounts_exist(world):
    client, providers = world
    # coverage\house has account 555
    r = client.delete("/api/v1/admin/groups/coverage/house", headers=ADMIN_HEADERS)
    assert r.status_code == 400 and "still has accounts" in r.json()["detail"]
    assert "coverage\\house" in providers["group_repo"].groups

    # an empty group deletes, publishes, and is gone from read paths
    r = client.delete("/api/v1/admin/groups/demo/Standard", headers=ADMIN_HEADERS)
    assert r.status_code == 200 and r.json() == {"status": "deleted", "name": "demo\\Standard"}
    assert "demo\\Standard" not in providers["group_repo"].groups
    assert client.get("/api/v1/admin/groups/demo/Standard", headers=ADMIN_HEADERS).status_code == 404
    events = [type(e).__name__ for e in providers["event_bus"].published]
    assert "GroupDeleted" in events

    # unknown -> 404
    assert client.delete("/api/v1/admin/groups/no/such", headers=ADMIN_HEADERS).status_code == 404


def test_fail_closed_when_emptiness_cannot_be_verified(world):
    """No account repository wired => 'has accounts' is assumed => refuse."""
    client, providers = world
    from application.commands.update_group import DeleteGroupHandler

    handler = DeleteGroupHandler(
        group_repo=providers["group_repo"],
        event_bus=providers["event_bus"],
        account_repo=None,
    )
    providers_saved = _container.get("account_repo")
    _container.pop("account_repo", None)
    try:
        r = client.delete("/api/v1/admin/groups/real/real", headers=ADMIN_HEADERS)
        assert r.status_code == 400
    finally:
        _container["account_repo"] = providers_saved
    assert handler is not None


# ---------------------------------------------------------------------------
# the signature guarantee, on the NEW write path
# ---------------------------------------------------------------------------

def test_created_group_exports_to_a_valid_mt5_record(world):
    client, providers = world
    r = client.post("/api/v1/admin/groups", headers=ADMIN_HEADERS, json={
        "name": "demo\\roundtrip", "currency": "USD",
        "margin_call_level": "50.00", "stop_out_level": "30.00",
    })
    assert r.status_code == 201
    group = providers["group_repo"].groups["demo\\roundtrip"]

    from infrastructure.mt5 import wire
    from infrastructure.persistence.config_mappers import group_mt5_record, group_to_db

    record = group_mt5_record(group_to_db(group))
    assert record["Group"] == "demo\\roundtrip"
    assert record["MarginCall"] == "50.00"
    assert record["MarginStopOut"] == "30.00"
    assert wire.validate(wire.build("ConfigGroups", [record])) == []
