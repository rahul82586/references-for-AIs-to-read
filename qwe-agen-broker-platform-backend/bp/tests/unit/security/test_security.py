"""
Unit Tests for Phase 11: Security, Auth & Identity Management.
"""
import pytest
import asyncio
from datetime import datetime, timezone, timedelta

from core.domains.identity.models import ManagerAccount, ManagerRole
from infrastructure.security.password_hasher import Argon2PasswordHasher
from infrastructure.security.rate_limiter import RedisRateLimiter
from infrastructure.security.two_factor import TOTPService
from infrastructure.security.ip_whitelist import IPWhitelistService
from infrastructure.security.token_blacklist import RedisTokenBlacklist
from application.services.auth_service import AuthService


class MockAccountRepo:
    def __init__(self):
        self.accounts = {}

    async def find_by_login(self, login_id: str):
        return self.accounts.get(login_id)

    async def save(self, account):
        self.accounts[account.login_id] = account
        return account


class MockManagerRepo:
    def __init__(self):
        self.managers = {}

    async def find_by_login(self, login: str):
        return self.managers.get(login)

    async def save(self, manager):
        self.managers[manager.login] = manager
        return manager


class MockAccount:
    def __init__(self, login_id: str, password_hash: str):
        self.login_id = login_id
        self.password_hash = password_hash


@pytest.mark.asyncio
async def test_argon2_password_hasher():
    hasher = Argon2PasswordHasher(time_cost=1, memory_cost=8192, parallelism=1)
    password = "SuperSecretPassword123!"
    hashed = hasher.hash_password(password)

    assert hashed != password
    assert hasher.verify_password(password, hashed) is True
    assert hasher.verify_password("WrongPassword!", hashed) is False


@pytest.mark.asyncio
async def test_totp_2fa_service():
    totp = TOTPService()
    secret = totp.generate_secret()
    assert len(secret) == 16 or len(secret) == 32

    uri = totp.get_provisioning_uri(secret, "admin@broker.com", "BrokerPlatform")
    assert uri.startswith("otpauth://totp/")
    assert "admin%40broker.com" in uri or "admin@broker.com" in uri

    import pyotp
    code = pyotp.TOTP(secret).now()
    assert totp.verify_code(secret, code) is True
    assert totp.verify_code(secret, "000000") is False


@pytest.mark.asyncio
async def test_ip_whitelisting_service():
    whitelist = IPWhitelistService()

    # Empty whitelist allows all
    assert whitelist.is_allowed("192.168.1.50", []) is True

    allowed_cidrs = ["10.0.0.0/8", "192.168.1.100", "172.16.0.0/12"]

    assert whitelist.is_allowed("10.5.2.1", allowed_cidrs) is True
    assert whitelist.is_allowed("192.168.1.100", allowed_cidrs) is True
    assert whitelist.is_allowed("172.16.10.20", allowed_cidrs) is True
    assert whitelist.is_allowed("192.168.1.101", allowed_cidrs) is False
    assert whitelist.is_allowed("8.8.8.8", allowed_cidrs) is False


@pytest.mark.asyncio
async def test_token_blacklist_dynamic_ttl():
    blacklist = RedisTokenBlacklist(redis_client=None)

    token1 = "valid_jwt_token_1"
    future_exp = datetime.now(timezone.utc) + timedelta(minutes=15)
    await blacklist.add(token1, future_exp)
    assert await blacklist.is_blacklisted(token1) is True

    # Expired token (ttl <= 0) should be ignored and not blacklisted
    token2 = "expired_jwt_token_2"
    past_exp = datetime.now(timezone.utc) - timedelta(minutes=5)
    await blacklist.add(token2, past_exp)
    assert await blacklist.is_blacklisted(token2) is False


@pytest.mark.asyncio
async def test_redis_rate_limiter_in_memory_fallback():
    limiter = RedisRateLimiter(redis_client=None)

    key = "rate_limit:ip:127.0.0.1"
    # Allow max 3 requests per 60 seconds
    for _ in range(3):
        assert await limiter.is_allowed(key, limit=3, window_seconds=60) is True

    # 4th request should be blocked
    assert await limiter.is_allowed(key, limit=3, window_seconds=60) is False


@pytest.mark.asyncio
async def test_auth_service_client_login():
    account_repo = MockAccountRepo()
    hasher = Argon2PasswordHasher(time_cost=1, memory_cost=8192, parallelism=1)
    rate_limiter = RedisRateLimiter(redis_client=None)

    hashed_pw = hasher.hash_password("ClientPass123")
    client_acc = MockAccount("1001", hashed_pw)
    await account_repo.save(client_acc)

    auth_service = AuthService(
        account_repo=account_repo,
        password_hasher=hasher,
        rate_limiter=rate_limiter,
    )

    res = await auth_service.login_client("1001", "ClientPass123", ip="192.168.1.10")
    assert "access_token" in res
    assert res["login_id"] == "1001"

    # Wrong password
    with pytest.raises(ValueError, match="Invalid credentials"):
        await auth_service.login_client("1001", "WrongPass", ip="192.168.1.10")


@pytest.mark.asyncio
async def test_auth_service_manager_login():
    manager_repo = MockManagerRepo()
    hasher = Argon2PasswordHasher(time_cost=1, memory_cost=8192, parallelism=1)
    totp_service = TOTPService()
    ip_whitelist = IPWhitelistService()
    secret = totp_service.generate_secret()

    hashed_pw = hasher.hash_password("ManagerAdmin123")
    manager = ManagerAccount(
        manager_id="mgr_01",
        login="admin_john",
        role=ManagerRole.SUPER_ADMIN,
        password_hash=hashed_pw,
        totp_secret=secret,
        is_2fa_enabled=True,
        allowed_ips=["10.0.0.0/8"],
    )
    await manager_repo.save(manager)

    auth_service = AuthService(
        account_repo=MockAccountRepo(),
        manager_repo=manager_repo,
        password_hasher=hasher,
        totp_service=totp_service,
        ip_whitelist=ip_whitelist,
    )

    import pyotp
    code = pyotp.TOTP(secret).now()

    # Success
    res = await auth_service.login_manager(
        login="admin_john",
        password="ManagerAdmin123",
        ip="10.1.2.3",
        totp_code=code,
    )
    assert "access_token" in res
    assert res["role"] == "SUPER_ADMIN"

    # Blocked by IP whitelist
    with pytest.raises(ValueError, match="IP address not allowed"):
        await auth_service.login_manager(
            login="admin_john",
            password="ManagerAdmin123",
            ip="192.168.1.5",
            totp_code=code,
        )

    # Invalid 2FA code
    with pytest.raises(ValueError, match="Invalid 2FA code"):
        await auth_service.login_manager(
            login="admin_john",
            password="ManagerAdmin123",
            ip="10.1.2.3",
            totp_code="000000",
        )


@pytest.mark.asyncio
async def test_certificate_verification():
    auth_service = AuthService(account_repo=MockAccountRepo())
    assert auth_service.verify_certificate("a1b2c3d4e5f67890") is True
    assert auth_service.verify_certificate("") is False
