"""CreateAccountHandler — MT5's "New Account" dialog, end to end.

Administrator guide, *Creating Accounts*, and ACCOUNT-GROUP-CREATION-SPEC §6.
This is the flow the identity plane was built for: allocate a login the way MT5's
"Next" button does, generate the three passwords, validate them against the
GROUP's own minimum, build the rights mask from the Limits/Account tabs, and
persist the client, the account and the opening deposit's ledger row in one
transaction.

The rules that matter, and why each is enforced rather than assumed:

* **The login is allocated, never chosen by arithmetic.** `MAX(login)+1` is a
  race between two administrators and reuses the login of a deleted account -
  which the guide explicitly forbids, because that login's trading history and
  every statement referencing it would be reassigned to a different person. See
  core/domains/accounts/login_allocator.py.
* **The group decides the account type and the currency, not the caller.** A
  group's NAME is what makes an account demo/real/contest (Group-Types.md, a
  case-sensitive substring rule), and its Currency is the denomination of every
  balance stored against it. Accepting either from the request body would let an
  API call create a "real" account in `demo\\Standard`.
* **`preliminary` is refused for a manually created account.** The guide: trading
  is PROHIBITED for every symbol in the preliminary group; it exists for
  terminal-opened, KYC-pending accounts. Creating one by hand is almost always a
  mistake, so it needs an explicit `allow_preliminary=True`.
* **Passwords are hashed, and the plaintext exists exactly once** - in the return
  value of this call, and nowhere else. Argon2 in the database, never retrievable,
  the `cli seed` first-admin pattern applied to clients. Changing a password
  resets the account's connection to the trade server, so `last_pass_change` is
  stamped.
* **A limit of NULL means "inherit the group"; 0 means "none allowed".** Those
  are different facts and collapsing them either grants unlimited positions or
  blocks all trading. Both stay Optional to the column.
* **No tick and no margin recompute are emitted.** A fresh account has no
  positions, so its margin is zero by construction. Emitting a recompute here is
  how an account gets valued against a price it never traded at - defect D16.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from typing import Any, Dict, List, Optional

from core.domains.accounts.account import Account
from core.domains.accounts.enums import AccountType
from core.domains.accounts.group import Group
from core.domains.common.value_objects import Money
from core.domains.identity.group_type import derive_group_type
from core.domains.identity.password_policy import (
    PasswordPolicy,
    PasswordPolicyError,
    hash_password,
)
from core.domains.identity.rights import MT5_USER_RIGHT_DEFAULT, UserRight
from core.domains.ledger.models import BalanceOperation, BalanceOperationType
from core.events.domain_events import AccountCreated
from core.ports.interfaces import (
    IAccountRepository,
    IClientRepository,
    IEventBus,
    IGroupRepository,
    ILoginAllocator,
)

logger = logging.getLogger(__name__)


class AccountRefusedError(ValueError):
    """The domain refused the account; the message is the reason (400 at the edge)."""


class GroupNotFoundError(ValueError):
    """No such group (404 at the edge)."""


@dataclass
class CreateAccountCommand:
    """The two boxes of MT5's create dialog: Details and Passwords.

    `login=None` means "Next" - allocate the closest free number. A supplied
    login is honoured only if it is genuinely free.
    """

    group_name: str
    #: Details box
    login: Optional[int] = None
    first_name: str = ""
    last_name: str = ""
    middle_name: str = ""
    company: str = ""
    email: str = ""
    phone: str = ""
    country: str = ""
    state: str = ""
    city: str = ""
    zip_code: str = ""
    address: str = ""
    #: Link an existing client rather than creating one.
    client_id: Optional[str] = None
    #: Create a client inline when there is no existing one to link.
    client: Optional[Any] = None          # a CreateClientCommand
    #: Passwords box - generated when omitted, and then returned exactly once.
    master_password: Optional[str] = None
    investor_password: Optional[str] = None
    phone_password: Optional[str] = None
    #: Account tab
    leverage: Optional[int] = None
    color: Optional[int] = None           # COLORREF, AABBGGRR as MT5 exports it
    agent_login: Optional[int] = None
    bank_account: str = ""
    #: Limits tab. None = inherit the group; False/0 are real values.
    enable_trading: bool = True
    enable_experts: Optional[bool] = None
    enable_trailing: Optional[bool] = None
    enable_reports: Optional[bool] = None
    enable_otp: Optional[bool] = None
    technical_account: bool = False
    exclude_from_reports: bool = False
    show_to_regular_managers: Optional[bool] = None
    include_in_server_reports: Optional[bool] = None
    change_password_at_next_login: bool = False
    limit_orders: Optional[int] = None
    limit_positions_value: Optional[Decimal] = None
    #: Money
    opening_deposit: Optional[Decimal] = None
    credit: Decimal = Decimal("0")
    #: Identity fields
    language: str = "en"
    residency_status: str = ""
    id_number: str = ""
    lead_source: str = ""
    lead_campaign: str = ""
    mqid: str = ""
    comment: str = ""
    #: Escape hatch for the guide's own preliminary-account workflow.
    allow_preliminary: bool = False


@dataclass
class CreatedAccount:
    """The result of a successful create.

    ``passwords`` is the ONLY place the plaintext ever exists. It is returned to
    the caller once, is not logged, is not published on the event bus, and is not
    stored - the database holds Argon2 hashes. An investor password cannot trade;
    that is enforced by the mask, not by the UI.
    """

    account: Account
    login: int
    group_name: str
    account_type: str
    currency: str
    passwords: Dict[str, str] = field(default_factory=dict)
    client_id: Optional[str] = None
    opening_deposit: Optional[str] = None
    #: How many already-taken logins the allocator stepped over. Non-zero means
    #: the counter and the account table disagree, which an operator should see.
    logins_skipped: int = 0


class CreateAccountHandler:
    """Handler for CreateAccountCommand."""

    def __init__(
        self,
        account_repo: IAccountRepository,
        group_repo: IGroupRepository,
        login_allocator: ILoginAllocator,
        event_bus: IEventBus,
        client_repo: Optional[IClientRepository] = None,
        ledger_repo: Optional[Any] = None,
        uow_factory: Optional[Any] = None,
    ) -> None:
        self.account_repo = account_repo
        self.group_repo = group_repo
        self.login_allocator = login_allocator
        self.event_bus = event_bus
        self.client_repo = client_repo
        self.ledger_repo = ledger_repo
        self.uow_factory = uow_factory

    # ------------------------------------------------------------------

    async def handle(self, command: CreateAccountCommand) -> CreatedAccount:
        group = await self._resolve_group(command)
        self._validate_against_group(command, group)

        policy = PasswordPolicy.for_group(group.auth_password_min)
        passwords = self._resolve_passwords(command, policy, group)

        login = await self._allocate_login(command)
        rights = self._build_rights(command)
        deposit = self._validate_deposit(command, group)

        client_id = await self._resolve_client(command)

        account = self._build_account(command, group, login, rights, passwords, client_id, deposit)

        await self._persist(account, client_id, deposit, group)
        await self._publish(account, group)

        logger.info(
            "account %s created in %s (%s, %s) - master/investor/phone passwords "
            "returned once and not logged",
            login, group.name, account.account_type.value, account.currency,
        )
        return CreatedAccount(
            account=account,
            login=login,
            group_name=group.name,
            account_type=account.account_type.value,
            currency=account.currency,
            passwords=passwords,
            client_id=client_id,
            opening_deposit=str(deposit) if deposit is not None else None,
            logins_skipped=getattr(self, "_last_skipped", 0),
        )

    # ------------------------------------------------------------------

    async def _resolve_group(self, command: CreateAccountCommand) -> Group:
        name = str(command.group_name or "").strip()
        if not name:
            raise AccountRefusedError("group_name is required")
        group = await self.group_repo.find_by_name(name)
        if group is None:
            raise GroupNotFoundError(f"no group named {name!r}")
        if not group.is_active:
            raise AccountRefusedError(
                f"group {name!r} is inactive; MT5 will not create an account in it"
            )
        return group

    def _validate_against_group(self, command: CreateAccountCommand, group: Group) -> None:
        """Everything the GROUP decides, checked before anything is written."""
        # The account type is DERIVED from the group name (Group-Types.md, a
        # case-sensitive substring rule). It is never taken from the request:
        # accepting it would let a caller create a "real" account in demo\Standard.
        derived = derive_group_type(group.name)
        if derived == AccountType.PRELIMINARY and not command.allow_preliminary:
            raise AccountRefusedError(
                f"group {group.name!r} is the preliminary group, where trading is "
                "PROHIBITED for every symbol; it exists for terminal-opened, "
                "KYC-pending accounts. Pass allow_preliminary=True only if that is "
                "genuinely what you are creating."
            )
        if command.leverage is not None:
            lev = int(command.leverage)
            if lev <= 0:
                raise AccountRefusedError("leverage must be a positive integer")
            cap = group.margin.leverage_max or 0
            if cap and lev > cap:
                raise AccountRefusedError(
                    f"leverage {lev} exceeds the group maximum of {cap} for {group.name!r}"
                )
        if command.color is not None:
            # COLORREF is a 32-bit AABBGGRR; MT5 exports FF000000 as "transparent".
            if not 0 <= int(command.color) <= 0xFFFFFFFF:
                raise AccountRefusedError(
                    "color must be a 32-bit COLORREF (AABBGGRR), 0..4294967295"
                )
        if command.limit_orders is not None and int(command.limit_orders) < 0:
            raise AccountRefusedError("limit_orders cannot be negative (use None to inherit the group)")
        if command.limit_positions_value is not None:
            try:
                if Decimal(str(command.limit_positions_value)) < 0:
                    raise AccountRefusedError("limit_positions_value cannot be negative")
            except InvalidOperation:
                raise AccountRefusedError("limit_positions_value must be decimal") from None
        if command.residency_status and command.residency_status.upper() not in ("RE", "NR"):
            raise AccountRefusedError(
                f"residency_status must be 'RE' (resident) or 'NR' (non-resident), "
                f"got {command.residency_status!r}"
            )

    def _resolve_passwords(
        self, command: CreateAccountCommand, policy: PasswordPolicy, group: Group
    ) -> Dict[str, str]:
        """Generate what was not supplied, validate all three, return the plaintext.

        The guide: all three passwords - master, investor and phone - are
        auto-generated at creation and may be overridden; all must contain four
        character classes; the minimum length comes from the GROUP; the maximum
        is 16.
        """
        out: Dict[str, str] = {}
        for key, supplied in (
            ("master_password", command.master_password),
            ("investor_password", command.investor_password),
            ("phone_password", command.phone_password),
        ):
            password = str(supplied).strip() if supplied else policy.generate()
            if not password:
                raise AccountRefusedError(f"{key} cannot be empty")
            try:
                policy.validate(password)
            except PasswordPolicyError as exc:
                raise AccountRefusedError(
                    f"{key} rejected by the password policy of group "
                    f"{group.name!r} (min length {policy.min_length} from its "
                    f"AuthPasswordMin, max {policy.max_length}): "
                    + "; ".join(exc.reasons)
                ) from None
            out[key] = password
        if out["master_password"] == out["investor_password"]:
            raise AccountRefusedError(
                "the investor password must differ from the master password; an "
                "investor session that could trade is not an investor session"
            )
        return out

    async def _allocate_login(self, command: CreateAccountCommand) -> int:
        """MT5's "Next": the closest free login, never a reused one."""
        if command.login is None:
            allocated = await self.login_allocator.next_login()
            self._last_skipped = getattr(allocated, "skipped", 0)
            return int(allocated.login)

        wanted = int(command.login)
        if wanted <= 0:
            raise AccountRefusedError("login must be a positive integer")
        if await self.account_repo.find_by_login(str(wanted)) is not None:
            raise AccountRefusedError(
                f"login {wanted} is already taken; MT5 assigns the closest FREE "
                "number and never reuses one"
            )
        self._last_skipped = 0
        return wanted

    def _build_rights(self, command: CreateAccountCommand) -> UserRight:
        """The Limits and Account tabs, as one mask.

        Two of these bits have an INVERTED sense in the SDK and are the classic
        0/1 bug: TRADE_DISABLED means trading is OFF, and TECHNICAL means "hidden
        from regular managers". The command fields are phrased the way the UI
        shows them, so the inversion happens here, once.
        """
        rights = MT5_USER_RIGHT_DEFAULT

        def set_bit(bit: UserRight, on: Optional[bool]) -> None:
            nonlocal rights
            if on is None:
                return
            rights = (rights | bit) if on else (rights & ~bit)

        set_bit(UserRight.ENABLED, True)                     # a created account may connect
        set_bit(UserRight.PASSWORD, True)                    # and may change its own password
        set_bit(UserRight.TRADE_DISABLED, not command.enable_trading)   # INVERTED
        set_bit(UserRight.EXPERT, command.enable_experts)
        set_bit(UserRight.TRAILING, command.enable_trailing)
        set_bit(UserRight.REPORTS, command.enable_reports)
        set_bit(UserRight.OTP_ENABLED, command.enable_otp)
        set_bit(UserRight.TECHNICAL, command.technical_account or None)  # INVERTED sense in the UI
        set_bit(UserRight.EXCLUDE_REPORTS, command.exclude_from_reports or None)
        # "Show to regular managers" is the inverse of TECHNICAL, and
        # "Include in server reports" is the inverse of EXCLUDE_REPORTS. Only
        # apply them when the caller was explicit, so the two spellings of the
        # same bit cannot fight.
        if command.show_to_regular_managers is not None:
            set_bit(UserRight.TECHNICAL, not command.show_to_regular_managers)
        if command.include_in_server_reports is not None:
            set_bit(UserRight.EXCLUDE_REPORTS, not command.include_in_server_reports)
        if command.change_password_at_next_login:
            rights |= UserRight.RESET_PASS
        return rights

    def _validate_deposit(
        self, command: CreateAccountCommand, group: Group
    ) -> Optional[Decimal]:
        if command.opening_deposit is None:
            return None
        try:
            amount = Decimal(str(command.opening_deposit))
        except (InvalidOperation, ValueError, TypeError):
            raise AccountRefusedError(
                f"opening_deposit must be decimal, got {command.opening_deposit!r}"
            ) from None
        if amount < 0:
            raise AccountRefusedError("opening_deposit cannot be negative")
        if amount == 0:
            # A zero deposit is not a deposit. Refuse rather than write a ledger
            # row that says money moved when none did.
            raise AccountRefusedError(
                "opening_deposit of 0 is not a deposit; omit it instead"
            )
        return amount

    async def _resolve_client(self, command: CreateAccountCommand) -> Optional[str]:
        """Link an existing client, create one, or create none."""
        if command.client_id:
            if self.client_repo is None:
                raise AccountRefusedError(
                    "a client was requested but no client repository is wired on "
                    "this server (503 rather than a silently unlinked account)"
                )
            existing = await self.client_repo.find_by_id(command.client_id)
            if existing is None:
                existing = await self.client_repo.find_by_client_id(command.client_id)
            if existing is None:
                raise AccountRefusedError(
                    f"no client {command.client_id!r} to link; create it first or "
                    "pass an inline client"
                )
            return existing.id

        if command.client is not None:
            if self.client_repo is None:
                raise AccountRefusedError(
                    "an inline client was supplied but no client repository is "
                    "wired on this server"
                )
            from application.commands.create_client import CreateClientHandler

            handler = CreateClientHandler(self.client_repo, self.event_bus)
            created = await handler.handle(command.client)
            return created.id

        return None

    def _build_account(
        self,
        command: CreateAccountCommand,
        group: Group,
        login: int,
        rights: UserRight,
        passwords: Dict[str, str],
        client_id: Optional[str],
        deposit: Optional[Decimal],
    ) -> Account:
        currency = group.currency or "USD"
        now = datetime.now(timezone.utc)
        account = Account(
            login=login,
            client_id=client_id or "",
            group_id=group.id,
            group=group,
            # DERIVED from the group name, never from the request body.
            account_type=derive_group_type(group.name),
            currency=currency,
            currency_digits=group.currency_digits,
            leverage=command.leverage,
            rights=rights,
            balance=Money(deposit or Decimal("0"), currency),
            credit=Money(_dec(command.credit), currency),
            equity=Money((deposit or Decimal("0")) + _dec(command.credit), currency),
            margin_level=Decimal("999999"),   # no margin in use -> the sentinel
            password_hash=hash_password(passwords["master_password"]),
            investor_password_hash=hash_password(passwords["investor_password"]),
            phone_password_hash=hash_password(passwords["phone_password"]),
            last_pass_change=now,
            first_name=command.first_name.strip(),
            last_name=command.last_name.strip(),
            middle_name=command.middle_name.strip(),
            company=command.company.strip(),
            country=command.country.strip(),
            state=command.state.strip(),
            city=command.city.strip(),
            zip_code=command.zip_code.strip(),
            address=command.address.strip(),
            phone=command.phone.strip(),
            email=command.email.strip(),
            language=(command.language or "en").strip(),
            residency_status=(command.residency_status or "").strip().upper(),
            id_number=command.id_number.strip(),
            lead_source=command.lead_source.strip(),
            lead_campaign=command.lead_campaign.strip(),
            mqid=command.mqid.strip(),
            comment=command.comment,
            color=command.color,
            agent_login=command.agent_login,
            bank_account=command.bank_account.strip(),
            # NULL means "inherit the group". 0 would mean "none allowed".
            limit_orders=command.limit_orders,
            limit_positions_value=(
                None
                if command.limit_positions_value is None
                else Decimal(str(command.limit_positions_value))
            ),
            registration_date=now,
            created_at=now,
            updated_at=now,
        )
        return account

    async def _persist(
        self,
        account: Account,
        client_id: Optional[str],
        deposit: Optional[Decimal],
        group: Group,
    ) -> None:
        """Account + opening-deposit ledger row in ONE transaction.

        An account with a balance and no ledger entry is how a book becomes
        unreconcilable - the exact thing M12's reconciliation engine exists to
        detect. So the deposit never touches `account.balance` without also
        writing its BalanceOperation, and both commit together or neither does.
        """
        if deposit is None or self.uow_factory is None or self.ledger_repo is None:
            if deposit is not None:
                logger.warning(
                    "account %s opening deposit %s cannot be written atomically: "
                    "uow_factory=%s ledger_repo=%s. Refusing rather than creating a "
                    "balance with no ledger row.",
                    account.login, deposit, bool(self.uow_factory), bool(self.ledger_repo),
                )
                raise AccountRefusedError(
                    "an opening deposit requires the ledger and a unit of work to be "
                    "wired; refusing to create a balance with no ledger entry"
                )
            await self.account_repo.save(account)
            return

        operation = BalanceOperation(
            account_login=str(account.login),
            operation_type=BalanceOperationType.DEPOSIT,
            amount=Money(deposit, account.currency),
            balance_after=Money(account.balance.amount, account.currency),
            comment="opening deposit",
        )
        async with self.uow_factory() as uow:
            session = uow.session
            await self.account_repo.save(account, session=session)
            await self.ledger_repo.save(operation, session=session)

    async def _publish(self, account: Account, group: Group) -> None:
        """AccountCreated - and deliberately nothing else.

        No tick, no margin recompute: a new account has no positions, so its
        margin is zero by construction. Triggering a valuation here is how an
        account ends up priced against a market it never traded in (D16).
        """
        if self.event_bus is None:
            return
        await self.event_bus.publish(
            AccountCreated(
                aggregate_id=str(account.login),
                payload={
                    "login": account.login,
                    "group": group.name,
                    "account_type": account.account_type.value,
                    "currency": account.currency,
                    "client_id": account.client_id or None,
                    "rights": int(account.rights),
                    # NO password material of any kind - see CreatedAccount.
                },
            )
        )


def _dec(value: Any) -> Decimal:
    if value is None:
        return Decimal("0")
    if isinstance(value, Decimal):
        return value
    try:
        return Decimal(str(value))
    except (InvalidOperation, ValueError, TypeError):
        return Decimal("0")
