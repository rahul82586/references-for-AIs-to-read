"""
Update / Delete Group Command Handlers (identity plane, step 4).

MT5 rules encoded here, from the Administrator guide:

* A group's NAME is its identity (the path is the natural key). There is no
  rename: renaming means create + move every account + delete, and moving an
  account across groups has its own currency/server rules. The update command
  therefore refuses a name change outright.
* "You cannot change binding to a trade server of a group that contains
  accounts" - and by the same reasoning (deposit currency), an update may not
  change the CURRENCY of a group that has accounts: every stored balance is
  denominated in the old one.
* MT5 refuses a request that changes nothing (MT_RET_REQUEST_NO_CHANGES,
  10025). So do we, instead of writing a fresh updated_at and publishing a
  GroupUpdated event that invalidates caches on every node for nothing.
* Delete refuses while the group has accounts. "Refuse" includes "cannot
  verify": if no account count is reachable, the delete does not happen.
  One writer per number - the group row is written only by these commands.

Both handlers follow the create pattern: persist -> update ConfigCache ->
publish the domain event (GroupUpdated / GroupDeleted already exist; nodes
invalidate their caches from them).
"""
import logging
from dataclasses import dataclass, field
from decimal import Decimal, InvalidOperation
from typing import Any, List, Optional

from core.domains.accounts.group import Group
from core.domains.identity.group_type import validate_group_name
from core.events.domain_events import GroupDeleted, GroupUpdated
from core.ports.interfaces import IAccountRepository, IEventBus, IGroupRepository
from application.cache.config_cache import get_config_cache

logger = logging.getLogger(__name__)


class GroupNotFoundError(ValueError):
    """No group with that name (404 at the API edge)."""


class GroupRefusedError(ValueError):
    """The domain refused the change; the message is the reason (400 at the edge)."""


def _dec(value: Any, what: str) -> Decimal:
    try:
        return Decimal(str(value))
    except (InvalidOperation, ValueError, TypeError):
        raise GroupRefusedError(f"{what}: {value!r} is not a decimal") from None


@dataclass
class UpdateGroupCommand:
    """Partial update: every field is optional; only supplied fields change.

    Deliberately limited to what the Group ENTITY models today. The 19 group
    columns migration 009 guarantees (company_*, reports_*, auth_*, demo_*)
    become editable when the entity declares them (plan step 5) - a field this
    command silently ignored would be a UI checkbox that lies.
    """

    name: str
    currency: Optional[str] = None
    currency_digits: Optional[int] = None
    leverage_default: Optional[int] = None
    leverage_max: Optional[int] = None
    margin_call_level: Optional[Any] = None      # PERCENT
    stop_out_level: Optional[Any] = None         # PERCENT
    limit_orders: Optional[int] = None
    limit_positions: Optional[int] = None
    limit_symbols: Optional[int] = None
    trade_allowed: Optional[bool] = None
    allowed_symbols: Optional[List[str]] = None
    is_active: Optional[bool] = None


class UpdateGroupHandler:
    """Handler for UpdateGroupCommand."""

    def __init__(
        self,
        group_repo: IGroupRepository,
        event_bus: IEventBus,
        account_repo: Optional[IAccountRepository] = None,
    ) -> None:
        self.group_repo = group_repo
        self.event_bus = event_bus
        self.account_repo = account_repo
        self.cache = get_config_cache()

    async def handle(self, command: UpdateGroupCommand) -> Group:
        name = validate_group_name(command.name)
        group = await self.group_repo.find_by_name(name)
        if group is None:
            raise GroupNotFoundError(f"no group named {name!r}")

        changes: List[str] = []
        if command.currency is not None and command.currency != group.currency:
            if await self._group_has_accounts(name):
                raise GroupRefusedError(
                    f"cannot change the deposit currency of {name!r} while it has "
                    "accounts: every balance is denominated in "
                    f"{group.currency} (MT5 forbids moving accounts between "
                    "different-currency groups for the same reason)"
                )
            group.currency = str(command.currency).strip().upper()
            changes.append("currency")
        if command.currency_digits is not None and int(command.currency_digits) != group.currency_digits:
            if not 0 <= int(command.currency_digits) <= 8:
                raise GroupRefusedError("currency_digits must be within 0..8")
            group.currency_digits = int(command.currency_digits)
            changes.append("currency_digits")

        margin = group.margin
        new_call = (
            _dec(command.margin_call_level, "margin_call_level")
            if command.margin_call_level is not None
            else margin.margin_call_level
        )
        new_stop = (
            _dec(command.stop_out_level, "stop_out_level")
            if command.stop_out_level is not None
            else margin.stop_out_level
        )
        if command.margin_call_level is not None or command.stop_out_level is not None:
            # Both are PERCENT (MT5 convention), and the call must fire before
            # the stop-out: MarginCall > MarginStopOut, both > 0.
            if new_stop <= 0:
                raise GroupRefusedError("stop_out_level must be greater than 0 percent")
            if new_call <= new_stop:
                raise GroupRefusedError(
                    f"margin_call_level ({new_call}) must be greater than "
                    f"stop_out_level ({new_stop}); the call must warn before the "
                    "stop-out liquidates"
                )
            if new_call != margin.margin_call_level:
                margin.margin_call_level = new_call
                changes.append("margin_call_level")
            if new_stop != margin.stop_out_level:
                margin.stop_out_level = new_stop
                changes.append("stop_out_level")

        if command.leverage_default is not None and int(command.leverage_default) != margin.leverage_default:
            if int(command.leverage_default) <= 0:
                raise GroupRefusedError("leverage_default must be positive")
            margin.leverage_default = int(command.leverage_default)
            changes.append("leverage_default")
        if command.leverage_max is not None and int(command.leverage_max) != margin.leverage_max:
            if int(command.leverage_max) <= 0:
                raise GroupRefusedError("leverage_max must be positive")
            if margin.leverage_default > int(command.leverage_max):
                raise GroupRefusedError(
                    "leverage_max cannot be lowered below the group's leverage_default"
                )
            margin.leverage_max = int(command.leverage_max)
            changes.append("leverage_max")

        for attr in ("limit_orders", "limit_positions", "limit_symbols"):
            value = getattr(command, attr)
            if value is not None and int(value) != getattr(group, attr):
                if int(value) < 0:
                    raise GroupRefusedError(f"{attr} cannot be negative")
                setattr(group, attr, int(value))
                changes.append(attr)

        if command.trade_allowed is not None and bool(command.trade_allowed) != group.permissions.trade_allowed:
            group.permissions.trade_allowed = bool(command.trade_allowed)
            changes.append("trade_allowed")
        if command.allowed_symbols is not None and list(command.allowed_symbols) != list(
            group.permissions.allowed_symbols
        ):
            group.permissions.allowed_symbols = [str(s) for s in command.allowed_symbols]
            changes.append("allowed_symbols")
        if command.is_active is not None and bool(command.is_active) != group.is_active:
            group.is_active = bool(command.is_active)
            changes.append("is_active")

        if not changes:
            # MT_RET_REQUEST_NO_CHANGES (10025): refusing is not an error page,
            # it is the honest answer - nothing was written, no event was fired.
            raise GroupRefusedError(
                "request does not contain changes (MT_RET_REQUEST_NO_CHANGES)"
            )

        # The margin memoisation on Group keys on symbol-config dicts, but the
        # margin PROFILE itself changed; drop any cached specs so the next
        # pre-trade check recomputes with the new thresholds.
        group.invalidate_margin_spec_cache()

        saved = await self.group_repo.save(group)
        self.cache.upsert_group(saved)
        await self.event_bus.publish(
            GroupUpdated(
                aggregate_id=saved.id,
                payload={"group_id": saved.id, "name": saved.name, "changes": changes},
            )
        )
        logger.info("group %s updated: %s", saved.name, ", ".join(changes))
        return saved

    async def _group_has_accounts(self, name: str) -> bool:
        """Fail closed: an unverifiable answer is treated as 'has accounts'."""
        if self.account_repo is None:
            return True
        counter = getattr(self.account_repo, "count_by_group_name", None)
        if counter is not None:
            try:
                return int(await counter(name)) > 0
            except NotImplementedError:
                pass
            except Exception:
                logger.warning("account count for group %s failed; assuming non-empty", name)
                return True
        try:
            accounts = await self.account_repo.find_all()
        except NotImplementedError:
            return True
        except Exception:
            logger.warning("find_all failed while checking group %s; assuming non-empty", name)
            return True
        return any((a.group.name if a.group else None) == name for a in accounts)


@dataclass
class DeleteGroupCommand:
    name: str


class DeleteGroupHandler:
    """Handler for DeleteGroupCommand. Refuses while the group has accounts."""

    def __init__(
        self,
        group_repo: IGroupRepository,
        event_bus: IEventBus,
        account_repo: Optional[IAccountRepository] = None,
    ) -> None:
        self.group_repo = group_repo
        self.event_bus = event_bus
        self.account_repo = account_repo
        self.cache = get_config_cache()
        self._update_helper = UpdateGroupHandler(group_repo, event_bus, account_repo)

    async def handle(self, command: DeleteGroupCommand) -> str:
        name = validate_group_name(command.name)
        group = await self.group_repo.find_by_name(name)
        if group is None:
            raise GroupNotFoundError(f"no group named {name!r}")

        if await self._update_helper._group_has_accounts(name):
            raise GroupRefusedError(
                f"group {name!r} still has accounts; move or delete them first "
                "(an empty group is the only deletable group)"
            )

        deleted = False
        delete_by_name = getattr(self.group_repo, "delete_by_name", None)
        if delete_by_name is not None:
            try:
                deleted = bool(await delete_by_name(name))
            except NotImplementedError:
                deleted = False
        if not deleted and group.id:
            deleted = bool(await self.group_repo.delete(group.id))
        if not deleted:
            raise GroupRefusedError(
                f"group {name!r} could not be deleted: the repository reports no row "
                "removed; nothing was published"
            )

        self.cache.delete_group(group.id)
        await self.event_bus.publish(
            GroupDeleted(aggregate_id=group.id, payload={"group_id": group.id, "name": name})
        )
        logger.info("group %s deleted", name)
        return name
