"""
Manager/Admin Identity Domain Models.

Step 3 of the identity plane (IDENTITY-BUILD-PLAN.md): ManagerAccount DECLARES
every field it carries. Before this, ``db_to_manager`` attached name/mailbox/
server_id/rights/group_scope/request limits/must_change_password dynamically
after construction, so every consumer read them through ``getattr(..., default)``
and a typo in a field name silently produced a default instead of an error.
That is the same class as F9 (ticket=0) and the D-family: a value that exists in
one place and is read from another.

The permissions model is MT5's, per the Administrator guide:

* ``rights`` - the 128-position mask (IMTConManager::EnManagerRights) - is the
  ONLY source of truth for what a manager may do.
* ``role`` / ``role_preset`` are COSMETIC labels. Picking a preset loads its
  bits into the mask (see core.domains.identity.role_presets); changing the
  label afterwards changes no permission. ManagerRole survives only as a
  display/back-compat value - nothing may authorise against it.
"""
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional

from core.domains.identity.rights import ManagerRightsMask


class ManagerRole(str, Enum):
    """DEPRECATED as an authorisation input - a cosmetic label only.

    MT5 has no role enum: 'admin / manager / dealer / accountant' are saved
    preset files over the 128-bit rights mask (Permissions tab: 'Role - one of
    predefined sets of permissions... Save As / Delete'). Five hardcoded values
    cannot express a saved preset, cannot express the live export's 39-bit
    'M Manager', and SUPPORT is not an MT5 concept at all. Authorisation reads
    ``ManagerAccount.rights`` - never this enum. Kept because the login token,
    the admin serializer and older tests reference it; demote, do not delete,
    until those callers move to ``role_preset``.
    """

    SUPER_ADMIN = "SUPER_ADMIN"
    DEALER = "DEALER"
    SUPPORT = "SUPPORT"
    RISK_MANAGER = "RISK_MANAGER"
    READ_ONLY = "READ_ONLY"


@dataclass
class ManagerAccount:
    """
    Manager/Admin user identity model for Eclipse Theia Admin UI & Manager APIs.

    Field order keeps the original constructor signature (manager_id, login,
    role, password_hash, ...) source-compatible; everything MT5-shaped that
    used to be attached dynamically is now declared with a safe default.
    """

    manager_id: str
    login: str
    role: ManagerRole = ManagerRole.READ_ONLY  # cosmetic label, see class docstring
    password_hash: str = ""
    totp_secret: Optional[str] = None
    is_2fa_enabled: bool = False
    allowed_ips: List[str] = field(default_factory=list)
    certificate_fingerprint: Optional[str] = None
    is_active: bool = True
    last_login: Optional[datetime] = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    # --- MT5 ConfigManagers fields, DECLARED (were attached dynamically) -----
    #: Display name (MT5 ConfigManagers.Name).
    name: str = ""
    #: Internal-mail mailbox; empty means the manager cannot send mail.
    mailbox: str = ""
    #: The trade server this manager belongs to. MT5: "a manager can service
    #: only those accounts that belong to the server to which the group the
    #: manager is included in refers."
    server_id: int = 1
    #: The 128-bit rights mask - the ONLY authorisation truth.
    rights: ManagerRightsMask = field(default_factory=ManagerRightsMask.empty)
    #: Group scope in MT5's own wire shape: [{"Group": "*"}], with "*" wildcard
    #: and "!" negation ("!managers*,*" = everything except managers).
    group_scope: List[Dict[str, Any]] = field(default_factory=list)
    #: "Available logs (period)" - days of journal this manager may request.
    request_limit_logs: int = 0
    #: "Available reports (period)" - days of reports. MT5: the STRICTEST limit
    #: always applies, so the effective window is min(this, per-report limit).
    request_limit_reports: int = 0
    #: MT5 forces a password change on first connect for an auto-created
    #: administrator; while set, login succeeds but every privileged action is
    #: refused until the password is changed.
    must_change_password: bool = False

    # --- ours ---------------------------------------------------------------
    #: The preset label the UI last applied (Administrator / Manager / Dealer /
    #: a saved preset). Cosmetic: setting it does NOT change ``rights``; the
    #: apply path is ``apply_preset`` below.
    role_preset: Optional[str] = None

    # --- authorisation helpers ------------------------------------------------

    def has_right(self, right: Any) -> bool:
        """Does this manager hold a right (name, index or ManagerRight)?"""
        return self.rights.has(right)

    def grant(self, *rights: Any) -> None:
        """Grant rights in place (identity commands own this mutation)."""
        self.rights = self.rights.grant(*rights)

    def revoke(self, *rights: Any) -> None:
        self.rights = self.rights.revoke(*rights)

    def apply_preset(self, preset: Any) -> None:
        """Load a RolePreset's bits into the mask and record its name as the
        cosmetic label. This is the ONLY sanctioned way a preset changes
        permissions - the label alone never does."""
        self.rights = preset.rights
        self.role_preset = preset.name

    def group_scope_patterns(self) -> List[str]:
        """The scope as plain MT5 mask strings, comma-lists split apart.

        MT5's Groups field is a comma-separated mask list with '*' wildcard and
        '!' negation - the guide's own example is the single string
        ``"!managers*,*"`` ("all groups except those whose name starts with
        managers"). An EMPTY scope follows this platform's stored default
        (``[{"Group": "*"}]`` in manager_to_db) and means "everything".
        """
        out: List[str] = []
        for entry in self.group_scope or []:
            if isinstance(entry, dict):
                value = entry.get("Group", entry.get("group"))
                if value is None:
                    continue
                raw = str(value)
            else:
                raw = str(entry)
            for part in raw.split(","):
                part = part.strip()
                if part:
                    out.append(part)
        return out or ["*"]

    def in_group_scope(self, group_name: str) -> bool:
        """MT5 Groups-scope match: masks evaluated in order, FIRST MATCH DECIDES
        (a '!' match excludes, a plain match includes); nothing matched = not in
        scope (fail closed). Reproduces the guide's example exactly:
        ``"!managers*,*"`` excludes managers\\dealers and includes demo\\forex."""
        name = str(group_name or "")
        for pattern in self.group_scope_patterns():
            negate = pattern.startswith("!")
            bare = pattern[1:] if negate else pattern
            if _mask_matches(bare, name):
                return not negate
        return False

    def effective_report_window(self, per_report_limit: Optional[int]) -> int:
        """MT5: the strictest limit always applies."""
        mine = int(self.request_limit_reports or 0)
        theirs = int(per_report_limit or 0)
        candidates = [v for v in (mine, theirs) if v > 0]
        return min(candidates) if candidates else 0


def _mask_matches(pattern: str, name: str) -> bool:
    """MT5 group mask: a single trailing/leading '*' wildcard, else exact match.
    'demo*' matches demo\\forex and demoforex; '*forex' matches real\\forex."""
    if pattern == "*":
        return True
    if pattern.startswith("*") and pattern.endswith("*") and len(pattern) > 2:
        return pattern[1:-1] in name
    if pattern.endswith("*"):
        return name.startswith(pattern[:-1])
    if pattern.startswith("*"):
        return name.endswith(pattern[1:])
    return name == pattern
