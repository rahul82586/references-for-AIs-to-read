"""
Create Group Command Handler.

Creates a new Group configuration, persists it to PostgreSQL (source of truth),
updates the in-memory ConfigCache (for instant read availability),
and publishes a domain event (for cluster sync).

Identity-plane step 4 hardened this path per ACCOUNT-GROUP-CREATION-SPEC §6:

* The name is validated the way MT5 wants it (non-empty, <= 64 chars,
  backslash path, no empty segments) - validate_group_name.
* The account type is DERIVED from the name with the ONE canonical rule
  (core.domains.identity.group_type - MT5 Group-Types.md, case-sensitive
  substring). A caller-supplied type that CONTRADICTS the name is refused:
  MT5 would not honour it, and honouring it here would mean the UI shows a
  "demo" group whose accounts behave real. The single documented exception is
  the broker's own contest pattern ("demo\\Challenge" is created as CONTEST by
  explicit configuration in the live export's YAML) - contest-on-demo.
* Margin thresholds are checked as a pair (MarginCall > MarginStopOut > 0,
  PERCENT) instead of each in isolation.
* A duplicate name is refused before anything is written.
"""
import logging
from dataclasses import dataclass
from decimal import Decimal
from typing import Optional

from core.domains.accounts.group import Group, MarginProfile, GroupPermissions
from core.domains.accounts.enums import AccountType, MarginMode, StopOutMode, FreeMarginMode
from core.domains.identity.group_type import derive_group_type, validate_group_name
from core.events.domain_events import GroupCreated
from core.ports.interfaces import IGroupRepository, IEventBus
from application.cache.config_cache import get_config_cache

logger = logging.getLogger(__name__)


class GroupRefusedError(ValueError):
    """The domain refused the creation; the message is the reason (400 at the edge)."""


@dataclass
class CreateGroupCommand:
    """Command to create a new Group.

    ``account_type`` is OPTIONAL: omitted (the normal case, and what the UI
    should send) it is derived from the name exactly as MT5 derives it.
    """

    name: str
    account_type: Optional[AccountType] = None
    currency: str = "USD"
    leverage_default: int = 100
    leverage_max: int = 500
    margin_call_level: Decimal = Decimal('80')   # percent, MT5 convention
    stop_out_level: Decimal = Decimal('50')      # percent, MT5 convention
    trade_allowed: bool = True


class CreateGroupHandler:
    """Handler for CreateGroupCommand."""

    def __init__(
        self,
        group_repo: IGroupRepository,
        event_bus: IEventBus,
    ):
        self.group_repo = group_repo
        self.event_bus = event_bus
        # NOTE: We fetch the cache dynamically here to avoid circular import
        # errors during module initialization, since the cache is set at startup.
        self.cache = get_config_cache()

    async def handle(self, command: CreateGroupCommand) -> Group:
        """Execute the create group command."""

        # 1. Validate the name (MT5's shape) and derive the type from it.
        name = validate_group_name(command.name)
        derived = derive_group_type(name)

        account_type = derived
        if command.account_type is not None:
            explicit = command.account_type
            if isinstance(explicit, str):  # tolerate the enum's value over the wire
                try:
                    explicit = AccountType(explicit)
                except ValueError:
                    raise GroupRefusedError(
                        f"account_type {command.account_type!r} is not one of "
                        f"{[t.value for t in AccountType]}"
                    ) from None
            if explicit is not derived:
                # The one documented exception: contest groups live under demo
                # paths by broker convention (the seeded demo\Challenge is a
                # CONTEST group). Anything else that contradicts the name is
                # refused - MT5 derives the type from the name and would not
                # honour the contradiction either.
                if not (derived is AccountType.DEMO and explicit is AccountType.CONTEST):
                    raise GroupRefusedError(
                        f"account_type {explicit.value!r} contradicts the group name "
                        f"{name!r}, which MT5 classifies as {derived.value!r} "
                        "(group type is derived from the name; only contest-on-demo "
                        "may be stated explicitly)"
                    )
                account_type = explicit

        # 2. Validate the money fields as a pair, in PERCENT.
        try:
            call = Decimal(str(command.margin_call_level))
            stop = Decimal(str(command.stop_out_level))
        except Exception:
            raise GroupRefusedError("margin thresholds must be decimal percents") from None
        if stop <= 0:
            raise GroupRefusedError("stop_out_level must be greater than 0 percent")
        if call <= stop:
            raise GroupRefusedError(
                f"margin_call_level ({call}) must be greater than stop_out_level ({stop})"
            )
        if int(command.leverage_default) <= 0 or int(command.leverage_max) <= 0:
            raise GroupRefusedError("leverage values must be positive")
        if int(command.leverage_default) > int(command.leverage_max):
            raise GroupRefusedError(
                "leverage_default cannot exceed leverage_max"
            )

        # 3. Refuse a duplicate before writing anything.
        if await self.group_repo.find_by_name(name) is not None:
            raise GroupRefusedError(f"group {name!r} already exists")

        # 4. Create domain entity
        group = Group(
            name=name,
            account_type=account_type,
            currency=command.currency,
            margin=MarginProfile(
                mode=MarginMode.RETAIL,
                leverage_default=command.leverage_default,
                leverage_max=command.leverage_max,
                margin_call_level=call,
                stop_out_level=stop,
                stop_out_mode=StopOutMode.PERCENT,
                free_margin_mode=FreeMarginMode.USE_PL,
            ),
            permissions=GroupPermissions(
                trade_allowed=command.trade_allowed,
            ),
        )

        # 5. Persist to PostgreSQL (Source of Truth)
        saved_group = await self.group_repo.save(group)
        logger.info(f"Group '{saved_group.name}' saved to PostgreSQL with ID: {saved_group.id}")

        # 6. Update In-Memory Cache (Instant Availability for Reads)
        self.cache.upsert_group(saved_group)
        logger.debug(f"Group '{saved_group.name}' updated in ConfigCache")

        # 7. Publish Domain Event (For other nodes/services to sync their caches)
        event = GroupCreated(
            aggregate_id=saved_group.id,
            payload={
                "group_id": saved_group.id,
                "name": saved_group.name,
                "account_type": saved_group.account_type.value,
            }
        )
        await self.event_bus.publish(event)
        logger.info(f"GroupCreated event published for '{saved_group.name}'")

        return saved_group
