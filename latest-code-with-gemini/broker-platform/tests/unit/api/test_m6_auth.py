"""M6: client login verifies a password — and refuses identically on every failure.

Before M6, POST /api/v1/auth/login issued a JWT to anyone who named an
existing login_id: the route never read the password (the schema's required
`password` field was ignored), and defaulted login_id to "100001" when absent.
These tests pin the new contract: a verified Argon2 hash, fail-closed on
unprovisioned accounts, and ONE generic 401 for every failure mode so the
response cannot be used to enumerate logins or diagnose which leg failed.
"""
import pytest
from fastapi.testclient import TestClient

from infrastructure.security.password_hasher import Argon2PasswordHasher
from tests.integration.trading_harness import DEFAULT_LOGIN, build_harness

PASSWORD = "correct-horse-battery-staple"
GENERIC = "Invalid credentials"


@pytest.fixture
def client_and_harness():
    import asyncio

    from api import di_providers
    from api.main import create_app

    harness = asyncio.run(build_harness(wire_trading=False))
    saved = dict(di_providers._container)
    try:
        app = create_app(harness.providers)
        with TestClient(app) as client:
            yield client, harness
    finally:
        di_providers._container.clear()
        di_providers._container.update(saved)


def _provision(harness, password=PASSWORD):
    account = harness.account_repo.accounts[DEFAULT_LOGIN]
    account.password_hash = Argon2PasswordHasher().hash_password(password)
    return account


def login(client, login_id=str(DEFAULT_LOGIN), password=PASSWORD):
    return client.post("/api/v1/auth/login", json={"login_id": login_id, "password": password})


def test_correct_password_issues_a_working_token(client_and_harness):
    client, harness = client_and_harness
    _provision(harness)

    res = login(client)

    assert res.status_code == 200, res.text
    token = res.json()["access_token"]
    from api.auth.jwt_handler import verify_token

    payload = verify_token(token)
    assert payload["sub"] == str(DEFAULT_LOGIN)


def test_wrong_password_is_refused(client_and_harness):
    client, harness = client_and_harness
    _provision(harness)

    res = login(client, password="wrong-password")

    assert res.status_code == 401
    assert res.json()["detail"] == GENERIC


def test_missing_password_is_refused(client_and_harness):
    client, harness = client_and_harness
    _provision(harness)

    res = client.post("/api/v1/auth/login", json={"login_id": str(DEFAULT_LOGIN)})

    assert res.status_code == 401
    assert res.json()["detail"] == GENERIC


def test_unknown_login_and_unprovisioned_account_are_indistinguishable(client_and_harness):
    client, harness = client_and_harness
    # DEFAULT_LOGIN exists but has NO password hash: fail closed
    unprovisioned = login(client)
    unknown = login(client, login_id="999999")

    assert unprovisioned.status_code == unknown.status_code == 401
    assert unprovisioned.json()["detail"] == unknown.json()["detail"] == GENERIC


def test_disabled_account_is_refused_even_with_the_right_password(client_and_harness):
    client, harness = client_and_harness
    account = _provision(harness)
    account.is_enabled = False

    res = login(client)

    assert res.status_code == 401
    assert res.json()["detail"] == GENERIC


def test_admin_can_provision_a_password_and_the_client_can_then_log_in(client_and_harness):
    client, harness = client_and_harness
    import os

    admin_key = os.environ["ADMIN_API_KEY"]  # set by the root conftest

    # no admin key -> 403
    res = client.post(
        "/api/v1/admin/accounts/set-password",
        json={"login": str(DEFAULT_LOGIN), "new_password": "fresh-secret-123"},
    )
    assert res.status_code == 403

    # with the admin key -> provisioned
    res = client.post(
        "/api/v1/admin/accounts/set-password",
        headers={"X-Admin-API-Key": admin_key},
        json={"login": str(DEFAULT_LOGIN), "new_password": "fresh-secret-123"},
    )
    assert res.status_code == 200, res.text

    # and login now works with the new password ONLY
    assert login(client, password="fresh-secret-123").status_code == 200
    assert login(client, password=PASSWORD).status_code == 401


def test_set_password_rejects_a_too_short_password(client_and_harness):
    client, harness = client_and_harness
    import os

    res = client.post(
        "/api/v1/admin/accounts/set-password",
        headers={"X-Admin-API-Key": os.environ["ADMIN_API_KEY"]},
        json={"login": str(DEFAULT_LOGIN), "new_password": "short"},
    )
    assert res.status_code == 422  # pydantic min_length at the edge
