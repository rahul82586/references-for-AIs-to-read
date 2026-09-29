"""Identity plane step 7 over real HTTP: the manager plane.

The specific risks these tests exist for:

* **Route order.** `/rights`, `/presets` and `/schema` must be declared BEFORE
  `/{login}`, or a GET for the catalogue resolves as a manager whose login is
  literally "rights" and returns a 404 (or worse, a 422). This is the same trap
  M15 hit with `/groups/schema` being swallowed by `/groups/{group_name:path}`.
* **The gating right is RIGHT_CFG_MANAGERS (17), not RIGHT_ACC_MANAGER (27).** An
  operator who may edit accounts must not thereby be able to grant themselves
  more rights; the SDK keeps the two bits apart and so does this router.
* **The catalogue is server-driven.** 97 named rights with their SDK index,
  plane and description, grouped by plane, so the UI renders a checkbox tree
  instead of hardcoding 128 positions - and RIGHT_LAST is excluded.
* **A manager's rights come back DECODED TO NAMES.** A UI handed a bitmask has to
  decode it, and that is how the 0/1 problem reaches the browser.
* **The password appears once**, and the create response says so.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from api.auth import admin_dependencies
from api.auth.jwt_handler import create_access_token
from api.di_providers import _container, register_di_providers
from api.routers.admin import managers as managers_router
from application.cache.config_cache import ConfigCache, set_config_cache
from core.domains.accounts.account import Account
from core.domains.accounts.enums import AccountType
from core.domains.accounts.group import Group
from core.domains.accounts.value_objects import MarginProfile
from core.domains.identity.models import ManagerAccount, ManagerRole
from core.domains.identity.rights import ManagerRightsMask

ADMIN_KEY = admin_dependencies.ADMIN_API_KEY_ENV or "test-admin-api-key"
ADMIN_HEADERS = {"X-Admin-API-Key": ADMIN_KEY}


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


class MemManagerRepo:
    def __init__(self) -> None:
        self.rows: Dict[str, ManagerAccount] = {}

    async def find_by_login(self, login, session=None):
        return self.rows.get(str(login))

    async def save(self, manager, session=None):
        self.rows[str(manager.login)] = manager
        return manager

    async def save_model(self, model):  # pragma: no cover
        raise NotImplementedError

    async def find_all(self, session=None):
        return list(self.rows.values())

    async def count(self):
        return len(self.rows)


class MemAccountRepo:
    def __init__(self, accounts: List[Account]) -> None:
        self.rows = {str(a.login): a for a in accounts}

    async def find_by_login(self, login, session=None):
        return self.rows.get(str(login))

    async def save(self, account, session=None):
        self.rows[str(account.login)] = account
        return account

    async def find_all(self, session=None):
        return list(self.rows.values())

    async def count_by_group_name(self, name, session=None):  # pragma: no cover
        return 0

    async def update_valuation(self, account, session=None, include_margin=False):  # pragma: no cover
        return 1


class MemGroupRepo:
    def __init__(self, groups: List[Group]) -> None:
        self.rows = {g.name: g for g in groups}

    async def find_by_name(self, name, session=None):
        return self.rows.get(name)

    async def find_by_id(self, gid, session=None):
        return next((g for g in self.rows.values() if g.id == gid), None)

    async def get_all(self, session=None):
        return list(self.rows.values())

    async def find_all(self, session=None):
        return list(self.rows.values())

    async def save(self, group, session=None):  # pragma: no cover
        self.rows[group.name] = group
        return group

    async def count_by_group_name(self, name, session=None):  # pragma: no cover
        return 0

    async def delete_by_name(self, name, session=None):  # pragma: no cover
        return self.rows.pop(name, None) is not None


class FakeUoW:
    def __init__(self) -> None:
        self.session = object()

    async def __aenter__(self):
        return self

    async def __aexit__(self, *exc):
        return False


def _group(name: str, account_type: AccountType, server_id: int = 1) -> Group:
    return Group(
        name=name, account_type=account_type, server_id=server_id,
        currency="USD", currency_digits=2, auth_password_min=8,
        margin=MarginProfile(leverage_default=100, leverage_max=500),
    )


def _account(login: int, group: Group) -> Account:
    return Account(
        login=login, group=group, group_id=group.id,
        account_type=group.account_type, currency="USD",
        password_hash="$argon2id$v=19$m=65536,t=3,p=4$c29tZXNhbHQ$existingaccountcredential",
        first_name="Existing", last_name="Staff",
    )


@pytest.fixture()
def world():
    staff_group = _group("managers\\administrators", AccountType.MANAGER, server_id=1)
    dealer_group = _group("managers\\dealers", AccountType.MANAGER, server_id=1)
    demo_group = _group("demo\\Standard", AccountType.DEMO, server_id=1)
    groups = [staff_group, dealer_group, demo_group]
    accounts = [_account(900001, staff_group), _account(900002, dealer_group), _account(900003, demo_group)]

    bus = NullEventBus()
    providers = {
        "manager_repo": MemManagerRepo(),
        "account_repo": MemAccountRepo(accounts),
        "group_repo": MemGroupRepo(groups),
        "client_repo": None,
        "ledger_repo": None,
        "login_allocator": None,
        "event_bus": bus,
        "uow_factory": FakeUoW,
    }
    register_di_providers(providers)
    set_config_cache(ConfigCache(
        group_repo=providers["group_repo"], account_repo=providers["account_repo"],
        symbol_repo=None, holiday_repo=None, position_repo=None, event_bus=bus,
    ))
    app = FastAPI()
    app.include_router(managers_router.router)
    providers["_client"] = TestClient(app)
    providers["_groups"] = groups
    yield providers


def _manager_token(rights_names: List[str], login: int = 800001, **kw):
    mask = ManagerRightsMask.empty().grant(*rights_names) if rights_names else ManagerRightsMask.empty()
    manager = ManagerAccount(
        manager_id=str(login), login=str(login), role=ManagerRole.READ_ONLY,
        rights=mask, **{**dict(is_active=True, must_change_password=False, allowed_ips=[]), **kw}
    )
    return manager, create_access_token({"sub": str(login), "is_manager": True})


def _install(world, managers: Dict[str, ManagerAccount]) -> None:
    world["manager_repo"].rows = managers
    register_di_providers({k: v for k, v in world.items() if not k.startswith("_")})


# ---------------------------------------------------------------------------
# 1. route order - the catalogues must not resolve as a login
# ---------------------------------------------------------------------------


def test_the_catalogue_routes_are_not_swallowed_by_the_login_route(world):
    """`/rights` before `/{login}`, or the UI gets a 404 for its checkbox tree."""
    client = world["_client"]
    for path in ("/api/v1/admin/managers/rights",
                 "/api/v1/admin/managers/presets",
                 "/api/v1/admin/managers/schema"):
        r = client.get(path, headers=ADMIN_HEADERS)
        assert r.status_code == 200, f"{path} -> {r.status_code} {r.text[:160]}"
        assert "no manager with login" not in r.text, path


def test_rights_catalogue_is_generated_from_the_sdk_and_excludes_the_sentinel(world):
    body = world["_client"].get("/api/v1/admin/managers/rights", headers=ADMIN_HEADERS).json()
    assert body["total"] == 97
    assert body["mask_width"] == 128
    names = {r["name"] for entries in body["planes"].values() for r in entries}
    assert "RIGHT_ADMIN" in names and "RIGHT_CFG_MANAGERS" in names
    assert "RIGHT_LAST" not in names, "the enum terminator is never grantable"
    assert all(r["index"] != 128 for entries in body["planes"].values() for r in entries)
    by_name = {r["name"]: r for entries in body["planes"].values() for r in entries}
    assert by_name["RIGHT_CFG_MANAGERS"]["index"] == 17
    assert by_name["RIGHT_ACC_MANAGER"]["index"] == 27
    assert by_name["RIGHT_CFG_MANAGERS"]["plane"] == "configuration"
    assert by_name["RIGHT_CFG_MANAGERS"]["grantable"] is True
    # grouped by plane, sorted by index within a plane
    for entries in body["planes"].values():
        assert [r["index"] for r in entries] == sorted(r["index"] for r in entries)


def test_presets_catalogue_carries_the_live_export_masks(world):
    body = world["_client"].get("/api/v1/admin/managers/presets", headers=ADMIN_HEADERS).json()
    by_name = {p["name"]: p for p in body["presets"]}
    assert by_name["Administrator"]["rights_count"] == 110
    assert by_name["Manager"]["rights_count"] == 39
    assert by_name["Administrator"]["builtin"] is True
    assert by_name["Administrator"]["deletable"] is False
    assert "RIGHT_ADMIN" in by_name["Administrator"]["rights_names"]
    assert "RIGHT_ADMIN" not in by_name["Manager"]["rights_names"]


def test_schema_serves_the_manager_field_descriptors(world):
    body = world["_client"].get("/api/v1/admin/managers/schema", headers=ADMIN_HEADERS).json()
    assert body["object"] == "manager"
    fields = {f["field"]: f for f in body["fields"]}
    for needed in ("login", "name", "mailbox", "server_id", "group_scope",
                   "rights", "role_preset", "request_limit_logs",
                   "request_limit_reports", "allowed_ips", "must_change_password"):
        assert needed in fields, needed
    assert fields["password"].get("write_only") is True
    assert fields["server_id"]["writable"] is False, "derived from the group"
    assert fields["role_label"]["description"].startswith("COSMETIC")


# ---------------------------------------------------------------------------
# 2. create
# ---------------------------------------------------------------------------


def test_create_manager_on_a_managers_group_account(world):
    client = world["_client"]
    r = client.post("/api/v1/admin/managers", headers=ADMIN_HEADERS, json={
        "login": 900001, "name": "Desk Admin", "preset": "Administrator",
        "mailbox": "desk", "group_scope": ["*"],
    })
    assert r.status_code == 201, r.text
    body = r.json()
    assert body["login"] == 900001
    assert body["based_on_account"] == 900001
    assert body["based_on_group"] == "managers\\administrators"
    assert body["server_id"] == 1
    assert body["rights_count"] == 110
    assert body["preset_applied"] == "Administrator"
    assert body["role_preset"] == "Administrator"
    assert "RIGHT_ADMIN" in body["rights_names"]
    # decoded and grouped, so the UI never has to touch the bitmask
    assert isinstance(body["rights_by_plane"], dict) and body["rights_by_plane"]
    assert all("index" in r and "name" in r for entries in body["rights_by_plane"].values() for r in entries)
    # no password supplied -> the account's credential was mirrored, no plaintext
    assert "password" not in body
    assert body["must_change_password"] is False


def test_create_refuses_an_account_outside_a_managers_group(world):
    r = world["_client"].post("/api/v1/admin/managers", headers=ADMIN_HEADERS,
                              json={"login": 900003, "preset": "Manager"})
    assert r.status_code == 400
    assert "not a managers group" in r.json()["detail"]


def test_create_404s_on_a_nonexistent_account(world):
    r = world["_client"].post("/api/v1/admin/managers", headers=ADMIN_HEADERS,
                              json={"login": 424242, "preset": "Manager"})
    assert r.status_code == 404
    assert "only on the basis" in r.json()["detail"]


def test_create_refuses_an_unknown_right_name(world):
    r = world["_client"].post("/api/v1/admin/managers", headers=ADMIN_HEADERS,
                              json={"login": 900001, "rights": ["RIGHT_NOPE"]})
    assert r.status_code == 400
    assert "unknown manager right" in r.json()["detail"]
    assert "never by index" in r.json()["detail"]


def test_create_returns_a_supplied_password_once_and_says_so(world):
    r = world["_client"].post("/api/v1/admin/managers", headers=ADMIN_HEADERS, json={
        "login": 900002, "preset": "Dealer", "password": "Str0ng#pass1",
    })
    assert r.status_code == 201, r.text
    body = r.json()
    assert body["password"] == "Str0ng#pass1"
    assert "shown exactly once" in body["warning"]
    stored = world["manager_repo"].rows["900002"]
    assert stored.password_hash.startswith("$argon2")
    assert "Str0ng#pass1" not in stored.password_hash


def test_create_refuses_a_prohibition_only_scope(world):
    r = world["_client"].post(
        "/api/v1/admin/managers", headers=ADMIN_HEADERS,
        json={"login": 900001, "preset": "Manager", "group_scope": ["!demo*"]})
    assert r.status_code == 400
    assert "prohibition" in r.json()["detail"]


def test_create_reports_unreachable_scope_rules_rather_than_refusing_them(world):
    """MT5 accepts '*,!managers*'; it just can never fire. Report, don't invent."""
    r = world["_client"].post("/api/v1/admin/managers", headers=ADMIN_HEADERS, json={
        "login": 900001, "preset": "Manager", "group_scope": ["*", "!managers*"],
    })
    assert r.status_code == 201, r.text
    body = r.json()
    assert body["group_scope_unreachable_rules"] == [1]
    assert body["group_scope_allows_all"] is True


def test_create_refuses_an_empty_mask(world):
    r = world["_client"].post("/api/v1/admin/managers", headers=ADMIN_HEADERS,
                              json={"login": 900001, "rights": []})
    assert r.status_code == 400 and "empty" in r.json()["detail"]


def test_a_duplicate_manager_login_is_refused(world):
    client = world["_client"]
    first = client.post("/api/v1/admin/managers", headers=ADMIN_HEADERS,
                        json={"login": 900001, "preset": "Manager"})
    assert first.status_code == 201
    second = client.post("/api/v1/admin/managers", headers=ADMIN_HEADERS,
                         json={"login": 900001, "preset": "Manager"})
    assert second.status_code == 400 and "already exists" in second.json()["detail"]


# ---------------------------------------------------------------------------
# 3. read + update
# ---------------------------------------------------------------------------


def test_get_one_manager_decodes_the_mask_to_names(world):
    client = world["_client"]
    client.post("/api/v1/admin/managers", headers=ADMIN_HEADERS,
                json={"login": 900001, "preset": "Manager", "name": "M Manager"})
    r = client.get("/api/v1/admin/managers/900001", headers=ADMIN_HEADERS)
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["login"] == 900001
    assert body["name"] == "M Manager"
    assert body["rights_count"] == 39
    assert "RIGHT_MANAGER" in body["rights_names"]
    assert "RIGHT_ADMIN" not in body["rights_names"]
    assert body["group_scope"] == ["*"]
    # the honest bit: the mask may carry 1s where the SDK assigns no name
    assert isinstance(body["rights_unnamed_indices"], list)


def test_get_an_unknown_manager_404s(world):
    r = world["_client"].get("/api/v1/admin/managers/123456", headers=ADMIN_HEADERS)
    assert r.status_code == 404


def test_update_grants_and_revokes_and_refuses_a_noop(world):
    client = world["_client"]
    client.post("/api/v1/admin/managers", headers=ADMIN_HEADERS,
                json={"login": 900001, "rights": ["RIGHT_MANAGER"]})
    r = client.put("/api/v1/admin/managers/900001", headers=ADMIN_HEADERS,
                   json={"grant": ["RIGHT_TRADES_DEALER"]})
    assert r.status_code == 200, r.text
    assert r.json()["rights_count"] == 2
    assert "RIGHT_TRADES_DEALER" in r.json()["rights_names"]

    noop = client.put("/api/v1/admin/managers/900001", headers=ADMIN_HEADERS,
                      json={"name": "M Manager"})
    assert noop.status_code == 200          # the name did change

    again = client.put("/api/v1/admin/managers/900001", headers=ADMIN_HEADERS,
                       json={"name": "M Manager"})
    assert again.status_code == 400
    assert "changes nothing" in again.json()["detail"]

    empty = client.put("/api/v1/admin/managers/900001", headers=ADMIN_HEADERS,
                       json={"revoke": ["RIGHT_MANAGER", "RIGHT_TRADES_DEALER"]})
    assert empty.status_code == 400 and "empty rights mask" in empty.json()["detail"]


def test_update_refuses_an_ambiguous_rights_change(world):
    client = world["_client"]
    client.post("/api/v1/admin/managers", headers=ADMIN_HEADERS,
                json={"login": 900001, "rights": ["RIGHT_MANAGER"]})
    r = client.put("/api/v1/admin/managers/900001", headers=ADMIN_HEADERS,
                   json={"rights": ["RIGHT_MANAGER", "RIGHT_ACC_READ"],
                         "grant": ["RIGHT_ADMIN"]})
    assert r.status_code == 400 and "ambiguous" in r.json()["detail"]

    r2 = client.put("/api/v1/admin/managers/900001", headers=ADMIN_HEADERS,
                    json={"grant": ["RIGHT_ADMIN"], "revoke": ["RIGHT_ADMIN"]})
    assert r2.status_code == 400 and "ambiguous" in r2.json()["detail"]


def test_update_accepts_an_ip_range_and_it_is_enforced(world):
    client = world["_client"]
    client.post("/api/v1/admin/managers", headers=ADMIN_HEADERS,
                json={"login": 900001, "rights": ["RIGHT_MANAGER"]})
    r = client.put("/api/v1/admin/managers/900001", headers=ADMIN_HEADERS,
                   json={"allowed_ips": ["10.0.0.5-10.0.0.9"]})
    assert r.status_code == 200, r.text
    assert r.json()["allowed_ips"] == ["10.0.0.5-10.0.0.9"]

    from api.auth.admin_dependencies import _ip_allowed
    stored = world["manager_repo"].rows["900001"]
    assert _ip_allowed("10.0.0.7", stored.allowed_ips) is True
    assert _ip_allowed("10.0.0.50", stored.allowed_ips) is False


# ---------------------------------------------------------------------------
# 4. authorisation - the gate is RIGHT_CFG_MANAGERS, not RIGHT_ACC_MANAGER
# ---------------------------------------------------------------------------


def test_an_account_editor_may_not_create_managers(world):
    """The SDK keeps RIGHT_ACC_MANAGER (27) and RIGHT_CFG_MANAGERS (17) apart.

    Collapsing them would let anyone who may edit an account grant themselves
    more rights - a privilege-escalation path, not a convenience.
    """
    client = world["_client"]
    manager, token = _manager_token(["RIGHT_ACC_MANAGER", "RIGHT_ACC_READ"])
    _install(world, {"800001": manager})
    r = client.post("/api/v1/admin/managers", headers={"Authorization": f"Bearer {token}"},
                    json={"login": 900001, "preset": "Administrator"})
    assert r.status_code == 403, r.text
    assert "RIGHT_CFG_MANAGERS" in r.json()["detail"]


def test_a_manager_holding_the_right_may_create_managers(world):
    client = world["_client"]
    manager, token = _manager_token(["RIGHT_CFG_MANAGERS"])
    _install(world, {"800001": manager})
    r = client.post("/api/v1/admin/managers", headers={"Authorization": f"Bearer {token}"},
                    json={"login": 900001, "preset": "Manager"})
    assert r.status_code == 201, r.text


def test_the_catalogues_are_gated_too(world):
    """A read of the rights catalogue is still configuration of manager rights."""
    client = world["_client"]
    manager, token = _manager_token(["RIGHT_ACC_READ"])
    _install(world, {"800001": manager})
    for path in ("/api/v1/admin/managers/rights", "/api/v1/admin/managers/presets"):
        r = client.get(path, headers={"Authorization": f"Bearer {token}"})
        assert r.status_code == 403, f"{path} -> {r.status_code}"


def test_an_unwired_manager_repository_never_fabricates_an_identity(world):
    """The anti-F2 rule on this plane: no manager row means refuse."""
    client = world["_client"]
    _manager, token = _manager_token(["RIGHT_CFG_MANAGERS"], login=800009)
    world["manager_repo"] = None
    register_di_providers({k: v for k, v in world.items() if not k.startswith("_")})
    r = client.post("/api/v1/admin/managers", headers={"Authorization": f"Bearer {token}"},
                    json={"login": 900001, "preset": "Manager"})
    assert r.status_code in (401, 503), r.text


def test_must_change_password_blocks_a_manager_from_creating_managers(world):
    client = world["_client"]
    manager, token = _manager_token(["RIGHT_CFG_MANAGERS"], login=800002, must_change_password=True)
    _install(world, {"800002": manager})
    r = client.post("/api/v1/admin/managers", headers={"Authorization": f"Bearer {token}"},
                    json={"login": 900001, "preset": "Manager"})
    assert r.status_code == 403
    assert "password change required" in r.json()["detail"]


# ---------------------------------------------------------------------------
# 5. presets: Save As / Delete
# ---------------------------------------------------------------------------


def test_save_as_and_delete_a_preset(world):
    client = world["_client"]
    r = client.post("/api/v1/admin/managers/presets", headers=ADMIN_HEADERS, json={
        "name": "NightDesk", "description": "read + dealing",
        "rights": ["RIGHT_MANAGER", "RIGHT_TRADES_DEALER"],
    })
    assert r.status_code == 201, r.text
    assert r.json()["name"] == "NightDesk"
    assert r.json()["rights_count"] == 2
    assert r.json()["builtin"] is False

    listed = client.get("/api/v1/admin/managers/presets", headers=ADMIN_HEADERS).json()
    assert "NightDesk" in {p["name"] for p in listed["presets"]}

    d = client.delete("/api/v1/admin/managers/presets/NightDesk", headers=ADMIN_HEADERS)
    assert d.status_code == 200 and d.json()["deleted"] == "NightDesk"


def test_a_builtin_preset_cannot_be_overwritten_or_deleted(world):
    client = world["_client"]
    r = client.post("/api/v1/admin/managers/presets", headers=ADMIN_HEADERS,
                    json={"name": "Administrator", "rights": ["RIGHT_MANAGER"]})
    assert r.status_code == 400 and "builtin" in r.json()["detail"]
    d = client.delete("/api/v1/admin/managers/presets/Administrator", headers=ADMIN_HEADERS)
    assert d.status_code == 400 and "builtin" in d.json()["detail"]


def test_an_empty_preset_is_refused(world):
    r = world["_client"].post("/api/v1/admin/managers/presets", headers=ADMIN_HEADERS,
                              json={"name": "Nothing", "rights": []})
    assert r.status_code == 400 and "empty" in r.json()["detail"]
