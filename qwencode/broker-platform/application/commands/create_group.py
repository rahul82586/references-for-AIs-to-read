"""
Create Group Command Handler.

Creates a new Group configuration, persists it to PostgreSQL (source of truth),
updates the in-memory ConfigCache (for instant read availability), 
and publishes a domain event (for cluster sync).
"""
import logging
from dataclasses import dataclass
from decimal import Decimal

from core.domains.accounts.group import Group, MarginProfile, GroupPermissions
from core.domains.accounts.enums import AccountType, MarginMode, StopOutMode, FreeMarginMode
from core.events.domain_events import GroupCreated
from core.ports.interfaces import IGroupRepository, IEventBus
from application.cache.config_cache import get_config_cache

logger = logging.getLogger(__name__)


@dataclass
class CreateGroupCommand:
    """Command to create a new Group."""
    name: str
    account_type: AccountType = AccountType.REAL
    currency: str = "USD"
    leverage_default: int = 100
    leverage_max: int = 500
    margin_call_level: Decimal = Decimal('0.8')
    stop_out_level: Decimal = Decimal('0.5')
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
        
        # 1. Validate
        if not command.name.strip():
            raise ValueError("Group name is required")
        
        # 2. Create domain entity
        group = Group(
            name=command.name.strip(),
            account_type=command.account_type,
            currency=command.currency,
            margin=MarginProfile(
                mode=MarginMode.RETAIL,
                leverage_default=command.leverage_default,
                leverage_max=command.leverage_max,
                margin_call_level=command.margin_call_level,
                stop_out_level=command.stop_out_level,
                stop_out_mode=StopOutMode.PERCENT,
                free_margin_mode=FreeMarginMode.USE_PL,
            ),
            permissions=GroupPermissions(
                trade_allowed=command.trade_allowed,
            ),
        )

        # 3. Persist to PostgreSQL (Source of Truth)
        saved_group = await self.group_repo.save(group)
        logger.info(f"Group '{saved_group.name}' saved to PostgreSQL with ID: {saved_group.id}")

        # 4. Update In-Memory Cache (Instant Availability for Reads)
        self.cache.upsert_group(saved_group)
        logger.debug(f"Group '{saved_group.name}' updated in ConfigCache")

        # 5. Publish Domain Event (For other nodes/services to sync their caches)
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