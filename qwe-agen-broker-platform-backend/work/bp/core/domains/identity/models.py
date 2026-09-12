"""
Manager/Admin Identity Domain Models.
"""
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import List, Optional


class ManagerRole(str, Enum):
    """Roles for admin UI and MT5 manager API access."""
    SUPER_ADMIN = "SUPER_ADMIN"
    DEALER = "DEALER"
    SUPPORT = "SUPPORT"
    RISK_MANAGER = "RISK_MANAGER"
    READ_ONLY = "READ_ONLY"


@dataclass
class ManagerAccount:
    """
    Manager/Admin user identity model for Eclipse Theia Admin UI & Manager APIs.
    """
    manager_id: str
    login: str
    role: ManagerRole
    password_hash: str
    totp_secret: Optional[str] = None
    is_2fa_enabled: bool = False
    allowed_ips: List[str] = field(default_factory=list)
    certificate_fingerprint: Optional[str] = None
    is_active: bool = True
    last_login: Optional[datetime] = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
