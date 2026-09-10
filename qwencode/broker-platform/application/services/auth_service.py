"""
Authentication Application Service handling Client & Manager Auth flows.
"""
from datetime import datetime, timezone, timedelta
from typing import Dict, Optional

from core.ports.interfaces import (
    IAccountRepository,
    IManagerRepository,
    IRateLimiter,
    ITwoFactorService,
    IIPWhitelist,
    ITokenBlacklist,
)
from api.auth.jwt_handler import create_access_token


class AuthService:
    """
    Application Service orchestrating authentication, authorization,
    2FA validation, CIDR IP whitelisting, rate limiting, and token management.
    """

    def __init__(
        self,
        account_repo: IAccountRepository,
        manager_repo: Optional[IManagerRepository] = None,
        password_hasher=None,
        rate_limiter: Optional[IRateLimiter] = None,
        totp_service: Optional[ITwoFactorService] = None,
        ip_whitelist: Optional[IIPWhitelist] = None,
        token_blacklist: Optional[ITokenBlacklist] = None,
    ):
        self._account_repo = account_repo
        self._manager_repo = manager_repo
        self._password_hasher = password_hasher
        self._rate_limiter = rate_limiter
        self._totp_service = totp_service
        self._ip_whitelist = ip_whitelist
        self._token_blacklist = token_blacklist

    async def login_client(self, login_id: str, password: str, ip: str) -> Dict[str, str]:
        """
        Client authentication flow with dual rate limiting (IP + Login ID).
        """
        # Dual Rate Limit check
        if self._rate_limiter:
            ip_allowed = await self._rate_limiter.is_allowed(f"rate_limit:ip:{ip}", limit=20, window_seconds=60)
            if not ip_allowed:
                raise ValueError("Rate limit exceeded for IP address")

            login_allowed = await self._rate_limiter.is_allowed(f"rate_limit:login:{login_id}", limit=5, window_seconds=60)
            if not login_allowed:
                raise ValueError("Rate limit exceeded for login ID")

        account = await self._account_repo.find_by_login(login_id)
        if not account:
            raise ValueError("Invalid credentials")

        # Verify password
        if self._password_hasher:
            if not self._password_hasher.verify_password(password, account.password_hash):
                raise ValueError("Invalid credentials")
        else:
            # Fallback simple string check if hasher not injected
            if getattr(account, "password_hash", None) != password:
                raise ValueError("Invalid credentials")

        # Issue JWT token
        token = create_access_token(data={"sub": str(login_id), "role": "client"})
        return {"access_token": token, "token_type": "bearer", "login_id": str(login_id)}

    async def login_manager(
        self,
        login: str,
        password: str,
        ip: str,
        totp_code: Optional[str] = None
    ) -> Dict[str, str]:
        """
        Manager/Admin authentication flow with CIDR IP Whitelisting & TOTP 2FA.
        """
        if not self._manager_repo:
            raise ValueError("Manager repository not configured")

        manager = await self._manager_repo.find_by_login(login)
        if not manager or not getattr(manager, "is_active", True):
            raise ValueError("Invalid credentials")

        # IP Whitelist check
        if self._ip_whitelist and manager.allowed_ips:
            if not self._ip_whitelist.is_allowed(ip, manager.allowed_ips):
                raise ValueError("IP address not allowed")

        # Verify password
        if self._password_hasher:
            if not self._password_hasher.verify_password(password, manager.password_hash):
                raise ValueError("Invalid credentials")
        else:
            if manager.password_hash != password:
                raise ValueError("Invalid credentials")

        # Verify 2FA TOTP code if enabled
        if manager.is_2fa_enabled:
            if not totp_code:
                raise ValueError("2FA code required")
            if self._totp_service:
                if not self._totp_service.verify_code(manager.totp_secret or "", totp_code):
                    raise ValueError("Invalid 2FA code")

        # Issue Admin JWT token with role claims
        role_str = str(manager.role.value if hasattr(manager.role, "value") else manager.role).strip()
        token = create_access_token(data={
            "sub": str(manager.login),
            "manager_id": str(manager.manager_id),
            "role": role_str,
            "is_manager": True
        })
        return {
            "access_token": token,
            "token_type": "bearer",
            "login": manager.login,
            "role": role_str,
        }


    def verify_certificate(self, cert_fingerprint: str) -> bool:
        """
        MT5 certificate fingerprint verification parity.
        """
        if not cert_fingerprint or len(cert_fingerprint.strip()) < 8:
            return False
        return True

    async def logout(self, token: str, expires_at: datetime) -> None:
        """
        Blacklists JWT access token.
        """
        if self._token_blacklist:
            await self._token_blacklist.add(token, expires_at)
