"""CreateManagerHandler / UpdateManagerHandler — MT5's Managers section.

Administrator guide, *Managers*:

    "Manager accounts are created **only based on accounts** added in the
     corresponding section."
    "Login — manager login, added in the Accounts section. The specified account
     **must be included to the managers' group**."
    "A manager can service only those accounts that belong to **the server**, to
     which the group the manager is included to refers."
    "Mailbox name — … If the mailbox name is not specified, the manager will not
     be able to send emails via the internal mailing system."
    "Role — here you can select one of predefined sets of permissions. Using
     buttons 'Save As' and 'Delete' you can save and delete your own sets."

The rules that shape this handler:

* **No login allocation.** A manager's login IS an existing account's login. That
  is what keeps staff logins out of the client account list and is why MT5 has no
  "New Manager" without a prior account. So this handler REFUSES unless the named
  account exists and sits in a group whose name contains `manager`
  (Group-Types.md, case-sensitive) - the live export has exactly those groups:
  `managers\\administrators`, `managers\\dealers`, `managers\\API`.
* **Rights are named, never indices.** The API accepts
  `["RIGHT_ADMIN", "RIGHT_MANAGER", …]`; the registry maps names to the SDK's
  indices and `from_names` refuses an unknown name. A typo must explode, not
  silently grant nothing - and an index-based API would let a caller write 68 or
  69, which the SDK leaves unassigned.
* **The server_id comes from the account's group**, not from the request. A
  manager services one trade server; accepting it from the caller would let a
  manager be created against a server their group does not belong to.
* **The credential has ONE writer: the account.** `managers.password_hash` is a
  MIRROR of `accounts.password_hash`, written here and nowhere else, in the same
  transaction. Two independent passwords for one login number - one checked by
  `/auth/login` and one by the manager plane - would be the D1/D18 class again:
  a secret written in one place and verified from another. So an omitted password
  copies the account's existing hash (no new plaintext is invented), and a
  supplied one is validated against the GROUP's policy, written to the account,
  and mirrored.
* **`must_change_password` defaults to False and is set explicitly.** MT5 forces
  the change on the AUTO-CREATED administrator (which `cli seed` already does),
  not on every manager an operator provisions. Defaulting it True here would lock
  a new manager out of the entire admin plane - `require_right` 403s on the flag -
  with no manager password-change endpoint to unlock them, which is a trap rather
  than a security control.

`must_change_password` is enforced in `require_right` (M15) and is now surfaced at
login too - but login still SUCCEEDS with it set, because a manager who cannot
authenticate cannot change their password. MT5 does the same: the terminal
connects and presents a change-password dialog.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from core.domains.accounts.enums import AccountType, ManagerLimit
from core.domains.identity.group_scope import (
    InvalidGroupScopeError,
    analyse_scope,
    to_wire,
    validate_group_scope,
)
from core.domains.identity.group_type import derive_group_type
from core.domains.identity.models import ManagerAccount, ManagerRole
from core.domains.identity.password_policy import (
    PasswordPolicy,
    PasswordPolicyError,
    hash_password,
)
from core.domains.identity.rights import (
    ManagerRightsMask,
    UnknownRightError,
    get_manager_rights,
)
from core.domains.identity.role_presets import PresetNotFoundError, get_preset
from core.events.domain_events import ManagerCreated
from core.ports.interfaces import (
    IAccountRepository,
    IEventBus,
    IGroupRepository,
    IManagerRepository,
)

logger = logging.getLogger(__name__)


class ManagerRefusedError(ValueError):
    """The domain refused; the message is the reason (400 at the edge)."""


class ManagerNotFoundError(ValueError):
    """No manager with that login (404 at the edge)."""


class AccountNotFoundError(ValueError):
    """No account with that login (404 at the edge)."""


@dataclass
class CreateManagerCommand:
    """MT5's manager dialog: Common, Permissions, Reports, IP Access List."""

    #: The EXISTING account this manager is created on the basis of. Its login
    #: becomes the manager login; there is no separate allocation.
    login: int
    #: Permissions. Either named rights, or a preset name, or both (the preset
    #: loads first and the explicit names are then granted on top).
    rights: Optional[List[str]] = None
    preset: Optional[str] = None
    #: Groups serviced. Defaults to MT5's own stored default, everything.
    group_scope: Optional[List[str]] = None
    #: Common tab
    name: str = ""
    mailbox: str = ""
    #: Permissions tab periods (IMTConManager::EnManagerLimit, 0=unlimited..6=3y)
    request_limit_logs: int = 0
    request_limit_reports: int = 0
    #: Security
    password: Optional[str] = None
    #: Force a change at first login. Defaults to False: MT5 applies the forced
    #: change to the AUTO-CREATED administrator (which `cli seed` does), not to
    #: every manager an operator provisions. Defaulting it True here would lock a
    #: new manager out of the whole admin plane - require_right 403s on it - with
    #: no manager password-change endpoint to unlock them. Set it explicitly when
    #: you are handing somebody a credential you chose for them.
    must_change_password: bool = False
    allowed_ips: Optional[List[Any]] = None
    is_2fa_enabled: bool = False
    totp_secret: Optional[str] = None
    #: Cosmetic label only - authorisation NEVER reads it (see ManagerRole).
    role_label: Optional[str] = None


@dataclass
class CreatedManager:
    """The result. ``password`` is set ONLY when this call generated one."""

    manager: ManagerAccount
    login: int
    account_login: int
    group_name: str
    server_id: int
    rights_count: int
    rights_names: List[str] = field(default_factory=list)
    preset_applied: Optional[str] = None
    #: The plaintext, exactly once, and only when we generated it. Never logged,
    #: never published, never stored - the row holds an Argon2 hash.
    password: Optional[str] = None
    must_change_password: bool = False
    #: Rules that can never fire (a `*` before them). MT5 accepts the list, so
    #: this is reported rather than refused - but an operator who wrote
    #: "*,!managers*" believes they excluded staff groups and did not.
    unreachable_scope_rules: List[int] = field(default_factory=list)


class CreateManagerHandler:
    """Handler for CreateManagerCommand."""

    def __init__(
        self,
        manager_repo: IManagerRepository,
        account_repo: IAccountRepository,
        group_repo: IGroupRepository,
        event_bus: IEventBus,
        uow_factory: Optional[Any] = None,
    ) -> None:
        self.manager_repo = manager_repo
        self.account_repo = account_repo
        self.group_repo = group_repo
        self.event_bus = event_bus
        self.uow_factory = uow_factory

    async def handle(self, command: CreateManagerCommand) -> CreatedManager:
        account, group = await self._require_manager_account(command)

        if await self.manager_repo.find_by_login(str(command.login)) is not None:
            raise ManagerRefusedError(
                f"a manager with login {command.login} already exists"
            )

        mask, preset_name = self._resolve_rights(command)
        patterns = self._resolve_scope(command)
        analysis = analyse_scope(patterns)
        self._validate_limits(command)

        password, password_hash, credential_set_here = await self._resolve_credential(
            command, account, group
        )

        manager = ManagerAccount(
            manager_id=str(command.login),
            login=str(command.login),
            # Cosmetic. MT5 has no role enum: 'admin/manager/dealer' are saved
            # preset files over the mask, and authorisation must never read this.
            role=self._role_label(command, preset_name),
            role_preset=preset_name,
            rights=mask,
            name=(command.name or account.display_name() or "").strip(),
            mailbox=(command.mailbox or "").strip(),
            # From the account's GROUP, not from the request: "a manager can
            # service only those accounts that belong to the server, to which the
            # group the manager is included to refers."
            server_id=int(group.server_id or 1),
            group_scope=to_wire(patterns),
            request_limit_logs=int(command.request_limit_logs or 0),
            request_limit_reports=int(command.request_limit_reports or 0),
            password_hash=password_hash,
            must_change_password=bool(command.must_change_password),
            allowed_ips=list(command.allowed_ips or []),
            is_2fa_enabled=bool(command.is_2fa_enabled),
            totp_secret=command.totp_secret,
            is_active=True,
        )

        await self._persist(manager, account, credential_set_here, password_hash)
        await self._publish(manager, group)

        logger.info(
            "manager %s created on account %s in %s (server %s) with %d rights%s",
            manager.login, account.login, group.name, manager.server_id, mask.count,
            f", preset {preset_name}" if preset_name else "",
        )
        return CreatedManager(
            manager=manager,
            login=int(command.login),
            account_login=int(account.login),
            group_name=group.name,
            server_id=int(manager.server_id),
            rights_count=mask.count,
            rights_names=mask.to_names(),
            preset_applied=preset_name,
            password=password,
            must_change_password=manager.must_change_password,
            unreachable_scope_rules=analysis.unreachable,
        )

    # ------------------------------------------------------------------

    async def _require_manager_account(self, command: CreateManagerCommand):
        """The account must exist AND sit in a managers group. Both are MT5's rule."""
        if command.login is None:
            raise ManagerRefusedError(
                "login is required: a manager is created ON THE BASIS of an "
                "existing account, so there is no login to allocate"
            )
        try:
            login = int(command.login)
        except (TypeError, ValueError):
            raise ManagerRefusedError(f"login must be an integer, got {command.login!r}") from None
        if login <= 0:
            raise ManagerRefusedError("login must be a positive integer")

        account = await self.account_repo.find_by_login(str(login))
        if account is None:
            raise AccountNotFoundError(
                f"no account with login {login}; MT5 creates a manager only on the "
                "basis of an account that already exists in the Accounts section"
            )
        group = None
        if account.group is not None:
            group = account.group
        elif account.group_id:
            group = await self.group_repo.find_by_id(account.group_id)
        if group is None:
            # An account with no resolvable group cannot tell us its server, and
            # the guide scopes a manager to the server their group refers to.
            raise ManagerRefusedError(
                f"account {login} has no resolvable group, so its trade server "
                "cannot be determined; a manager can service only the accounts of "
                "the server its group refers to"
            )
        if derive_group_type(group.name) is not AccountType.MANAGER:
            raise ManagerRefusedError(
                f"account {login} is in group {group.name!r}, which is not a "
                "managers group. MT5: 'a manager account can be created only based "
                "on the account included to the managers' group' - the group name "
                "must contain 'manager' (case-sensitive). This is what keeps staff "
                "logins out of the client account list."
            )
        return account, group

    def _resolve_rights(self, command: CreateManagerCommand):
        """Preset first, then explicit names granted on top. Names, never indices."""
        registry = get_manager_rights()
        preset_name: Optional[str] = None
        mask = ManagerRightsMask.empty()

        if command.preset:
            try:
                preset = get_preset(command.preset)
            except PresetNotFoundError as exc:
                raise ManagerRefusedError(str(exc)) from None
            mask = preset.rights
            preset_name = preset.name

        if command.rights:
            try:
                mask = mask.grant(*command.rights)
            except UnknownRightError as exc:
                # A typo must explode. Silently granting nothing would create a
                # manager who can authenticate and then 403 on everything, which
                # reads as a broken server rather than a misspelled right.
                raise ManagerRefusedError(
                    f"unknown manager right in {command.rights!r}: {exc}. Rights are "
                    "given by NAME (the SDK's EnManagerRights identifiers), never by "
                    "index - indices 68/69 and 113-127 are unassigned in the SDK and "
                    "128 is the never-grantable RIGHT_LAST sentinel."
                ) from None

        if mask.count == 0:
            raise ManagerRefusedError(
                "the rights mask is empty: this manager could authenticate and then "
                "be refused everything. Apply a preset or name at least one right."
            )
        # RIGHT_LAST (128) is the enum terminator; the registry excludes it from
        # grantable(), so from_names/grant cannot set it. Assert the invariant
        # rather than trusting it - a grantable sentinel would be a silent
        # escalation path.
        if 128 in mask.indices:
            raise ManagerRefusedError("RIGHT_LAST (128) is never grantable")
        del registry  # resolved above for its validation side effects
        return mask, preset_name

    def _resolve_scope(self, command: CreateManagerCommand) -> List[str]:
        scope = command.group_scope
        if scope is None:
            # MT5's own stored default, and what all nine live managers carry.
            return ["*"]
        if isinstance(scope, str):
            scope = [scope]
        try:
            return validate_group_scope(scope)
        except InvalidGroupScopeError as exc:
            raise ManagerRefusedError(
                "invalid Groups scope: " + "; ".join(exc.reasons)
            ) from None

    def _validate_limits(self, command: CreateManagerCommand) -> None:
        """Both periods are IMTConManager::EnManagerLimit: 0 unlimited .. 6 three years."""
        valid = {int(m.value) for m in ManagerLimit}
        for field_name, value in (
            ("request_limit_logs", command.request_limit_logs),
            ("request_limit_reports", command.request_limit_reports),
        ):
            try:
                ivalue = int(value or 0)
            except (TypeError, ValueError):
                raise ManagerRefusedError(f"{field_name} must be an integer") from None
            if ivalue not in valid:
                raise ManagerRefusedError(
                    f"{field_name}={ivalue} is not an EnManagerLimit value; valid: "
                    f"{sorted(valid)} (0=unlimited, 1=1 month ... 6=3 years)"
                )

    def _role_label(self, command: CreateManagerCommand, preset_name: Optional[str]) -> ManagerRole:
        """The cosmetic label. Authorisation NEVER reads it."""
        wanted = (command.role_label or preset_name or "").strip().lower()
        mapping = {
            "administrator": ManagerRole.SUPER_ADMIN,
            "admin": ManagerRole.SUPER_ADMIN,
            "super_admin": ManagerRole.SUPER_ADMIN,
            "dealer": ManagerRole.DEALER,
            "riskmanager": ManagerRole.RISK_MANAGER,
            "risk_manager": ManagerRole.RISK_MANAGER,
            "manager": ManagerRole.READ_ONLY,
            "accountant": ManagerRole.SUPPORT,
            "support": ManagerRole.SUPPORT,
            "read_only": ManagerRole.READ_ONLY,
        }
        return mapping.get(wanted, ManagerRole.READ_ONLY)

    async def _resolve_credential(self, command, account, group) -> tuple:
        """(plaintext_or_None, argon2_hash, generated).

        The account owns the credential; the manager row mirrors it. Omitting a
        password copies the account's existing hash - no new secret is invented,
        and the manager can log in with the credential that already exists.
        """
        existing = str(getattr(account, "password_hash", "") or "")
        if not command.password:
            if not existing:
                raise ManagerRefusedError(
                    f"account {account.login} has no password provisioned, so there "
                    "is nothing for the manager to log in with. Supply a password "
                    "here, or set one on the account first "
                    "(POST /api/v1/admin/accounts/set-password)."
                )
            return None, existing, False

        policy = PasswordPolicy.for_group(getattr(group, "auth_password_min", None))
        try:
            policy.validate(command.password)
        except PasswordPolicyError as exc:
            raise ManagerRefusedError(
                f"password rejected by the policy of group {group.name!r} "
                f"(min length {policy.min_length} from its AuthPasswordMin, max "
                f"{policy.max_length}): " + "; ".join(exc.reasons)
            ) from None
        return command.password, hash_password(command.password), True

    async def _persist(self, manager, account, generated: bool, password_hash: str) -> None:
        """Manager row + (when a password was set) the account's hash, atomically.

        Written together or not at all: a manager whose mirror hash differs from
        the account's is a login that works on one plane and fails on the other.
        """
        if not generated or self.uow_factory is None:
            await self.manager_repo.save(manager)
            return
        # A supplied password is written to the ACCOUNT (the one writer of the
        # credential) and mirrored onto the manager row, in one transaction - so
        # the two planes can never disagree about what logs this login in.
        account.password_hash = password_hash
        async with self.uow_factory() as uow:
            session = uow.session
            if _accepts_session(self.manager_repo.save):
                await self.manager_repo.save(manager, session=session)
            else:
                await self.manager_repo.save(manager)
            await self.account_repo.save(account, session=session)

    async def _publish(self, manager: ManagerAccount, group) -> None:
        if self.event_bus is None:
            return
        await self.event_bus.publish(
            ManagerCreated(
                aggregate_id=str(manager.login),
                payload={
                    "login": manager.login,
                    "name": manager.name,
                    "server_id": manager.server_id,
                    "based_on_group": group.name,
                    "rights_count": manager.rights.count,
                    "role_preset": manager.role_preset,
                    "must_change_password": manager.must_change_password,
                    # NO password, NO hash - see the module docstring.
                },
            )
        )


def _accepts_session(method: Any) -> bool:
    import inspect

    try:
        return "session" in inspect.signature(method).parameters
    except (TypeError, ValueError):
        return False


# ---------------------------------------------------------------------------
# Update
# ---------------------------------------------------------------------------


@dataclass
class UpdateManagerCommand:
    """Partial update. Only supplied fields change; an empty update is refused.

    MT5 refuses a request that changes nothing (MT_RET_REQUEST_NO_CHANGES,
    10025), and so does UpdateGroupHandler - writing a fresh updated_at and
    publishing an event that invalidates caches on every node for nothing is not
    a no-op, it is noise.
    """

    login: int
    rights: Optional[List[str]] = None
    #: Replace the whole mask. Mutually exclusive with grant/revoke below.
    preset: Optional[str] = None
    grant: Optional[List[str]] = None
    revoke: Optional[List[str]] = None
    group_scope: Optional[List[str]] = None
    name: Optional[str] = None
    mailbox: Optional[str] = None
    request_limit_logs: Optional[int] = None
    request_limit_reports: Optional[int] = None
    allowed_ips: Optional[List[str]] = None
    is_active: Optional[bool] = None
    must_change_password: Optional[bool] = None
    is_2fa_enabled: Optional[bool] = None
    totp_secret: Optional[str] = None


class UpdateManagerHandler:
    """Handler for UpdateManagerCommand."""

    def __init__(self, manager_repo: IManagerRepository, event_bus: IEventBus) -> None:
        self.manager_repo = manager_repo
        self.event_bus = event_bus

    async def handle(self, command: UpdateManagerCommand) -> ManagerAccount:
        from core.events.domain_events import ManagerUpdated

        manager = await self.manager_repo.find_by_login(str(command.login))
        if manager is None:
            raise ManagerNotFoundError(f"no manager with login {command.login}")

        changes: List[str] = []

        whole_mask = command.preset is not None or command.rights is not None
        delta = bool(command.grant) or bool(command.revoke)
        if whole_mask and delta:
            raise ManagerRefusedError(
                "supply either a whole mask (preset/rights) or a delta "
                "(grant/revoke), not both - the intent is ambiguous"
            )
        if command.grant and command.revoke:
            overlap = sorted(set(command.grant) & set(command.revoke))
            if overlap:
                raise ManagerRefusedError(
                    f"{overlap} appears in both grant and revoke; the intent is "
                    "ambiguous - the mask cannot both gain and lose the same right"
                )
        if whole_mask:
            new_mask = manager.rights
            preset_name = manager.role_preset
            if command.preset is not None:
                try:
                    preset = get_preset(command.preset)
                except PresetNotFoundError as exc:
                    raise ManagerRefusedError(str(exc)) from None
                new_mask = preset.rights
                preset_name = preset.name
            if command.rights is not None:
                try:
                    new_mask = ManagerRightsMask.from_names(command.rights)
                except UnknownRightError as exc:
                    raise ManagerRefusedError(f"unknown manager right: {exc}") from None
                preset_name = None
            if new_mask.count == 0:
                raise ManagerRefusedError("refusing to set an empty rights mask")
            if new_mask.to_array() != manager.rights.to_array():
                manager.rights = new_mask
                manager.role_preset = preset_name
                changes.append("rights")

        for delta, op in ((command.grant, "grant"), (command.revoke, "revoke")):
            if not delta:
                continue
            try:
                before = manager.rights.to_array()
                manager.rights = (
                    manager.rights.grant(*delta) if op == "grant"
                    else manager.rights.revoke(*delta)
                )
            except UnknownRightError as exc:
                raise ManagerRefusedError(f"unknown manager right in {op}: {exc}") from None
            if manager.rights.count == 0:
                raise ManagerRefusedError(f"{op} would leave an empty rights mask")
            if manager.rights.to_array() != before and "rights" not in changes:
                changes.append("rights")

        if command.group_scope is not None:
            scope = command.group_scope
            if isinstance(scope, str):
                scope = [scope]
            try:
                patterns = validate_group_scope(scope)
            except InvalidGroupScopeError as exc:
                raise ManagerRefusedError(
                    "invalid Groups scope: " + "; ".join(exc.reasons)
                ) from None
            if to_wire(patterns) != list(manager.group_scope or []):
                manager.group_scope = to_wire(patterns)
                changes.append("group_scope")

        for attr, value in (
            ("name", command.name),
            ("mailbox", command.mailbox),
            ("totp_secret", command.totp_secret),
        ):
            if value is not None and getattr(manager, attr) != value:
                setattr(manager, attr, value)
                changes.append(attr)

        for attr, value in (
            ("request_limit_logs", command.request_limit_logs),
            ("request_limit_reports", command.request_limit_reports),
        ):
            if value is None:
                continue
            valid = {int(m.value) for m in ManagerLimit}
            if int(value) not in valid:
                raise ManagerRefusedError(
                    f"{attr}={value} is not an EnManagerLimit value; valid {sorted(valid)}"
                )
            if int(getattr(manager, attr) or 0) != int(value):
                setattr(manager, attr, int(value))
                changes.append(attr)

        if command.allowed_ips is not None:
            wanted = [str(x) for x in command.allowed_ips]
            if wanted != list(manager.allowed_ips or []):
                manager.allowed_ips = wanted
                changes.append("allowed_ips")

        for attr, value in (
            ("is_active", command.is_active),
            ("must_change_password", command.must_change_password),
            ("is_2fa_enabled", command.is_2fa_enabled),
        ):
            if value is not None and bool(getattr(manager, attr)) != bool(value):
                setattr(manager, attr, bool(value))
                changes.append(attr)

        if not changes:
            raise ManagerRefusedError(
                "the request changes nothing (MT_RET_REQUEST_NO_CHANGES, 10025)"
            )

        saved = await self.manager_repo.save(manager)
        if self.event_bus is not None:
            await self.event_bus.publish(
                ManagerUpdated(
                    aggregate_id=str(saved.login),
                    payload={"manager_login": saved.login, "changes": changes},
                )
            )
        logger.info("manager %s updated: %s", saved.login, ", ".join(changes))
        return saved
