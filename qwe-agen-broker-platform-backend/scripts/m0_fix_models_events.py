"""
Step M0 part 2 - finish the import gate.

  * db_models.py   drop the stale duplicate DealModel / PositionModel (they used
                   side / average_price / id, which is where RiskEngine picked up
                   attribute names the real Position entity does not have), keep the
                   MT5-accurate ones, preserve original_deal_id, and delete the three
                   leftover AI-chat instruction comments.
  * domain_events  drop the duplicate OrderCancelled / OrderModified (they omitted
                   event_type, so they silently serialised as "order.created" because
                   DomainEvent defaults event_type to ORDER_CREATED), keep TradeModified,
                   and add the eight config-plane events that three modules import.
  * group_repository  point at the current value-object names.
  * di_providers      drop the duplicate get_cancel_order_handler, add get_di_container.
"""

from __future__ import annotations

import pathlib
import sys

ROOT = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else pathlib.Path.cwd()
if not (ROOT / "infrastructure" / "persistence" / "db_models.py").is_file():
    raise SystemExit(f"not a broker-platform root: {ROOT}")

log: list[str] = []


def read(rel: str) -> str:
    with open(ROOT / rel, "r", encoding="utf-8", newline="") as handle:
        return handle.read()


def write(rel: str, text: str) -> None:
    with open(ROOT / rel, "w", encoding="utf-8", newline="") as handle:
        handle.write(text)


def cut(rel: str, start: str, end: str, why: str) -> None:
    """Delete the half-open region [start, end)."""
    text = read(rel)
    a = text.find(start)
    if a == -1:
        raise SystemExit(f"[FAIL] {rel}: start not found: {start[:70]!r}")
    b = text.find(end, a)
    if b == -1:
        raise SystemExit(f"[FAIL] {rel}: end not found: {end[:70]!r}")
    write(rel, text[:a] + text[b:])
    log.append(f"{rel}: removed {b - a} chars - {why}")


def replace(rel: str, old: str, new: str, why: str) -> None:
    text = read(rel)
    for old_v, new_v in ((old, new), (old.replace("\n", "\r\n"), new.replace("\n", "\r\n"))):
        if old_v in text:
            write(rel, text.replace(old_v, new_v, 1))
            log.append(f"{rel}: {why}")
            return
    raise SystemExit(f"[FAIL] {rel}: pattern not found: {old[:120]!r}")


def append_block(rel: str, anchor: str, block: str, why: str) -> None:
    text = read(rel)
    crlf = "\r\n" in text
    if crlf:
        anchor = anchor.replace("\n", "\r\n")
        block = block.replace("\n", "\r\n")
    at = text.find(anchor)
    if at == -1:
        raise SystemExit(f"[FAIL] {rel}: anchor not found: {anchor[:70]!r}")
    write(rel, text[:at] + block + text[at:])
    log.append(f"{rel}: {why}")


# ===========================================================================
# db_models.py
# ===========================================================================

DBM = "infrastructure/persistence/db_models.py"

# The stale duplicates start at the second `class DealModel` and end where
# BalanceOperationModel begins.
text = read(DBM)
first_deal = text.find("class DealModel(Base):")
second_deal = text.find("class DealModel(Base):", first_deal + 1)
if second_deal == -1:
    raise SystemExit("[FAIL] db_models.py: second DealModel not found")
end_of_stale = text.find("class BalanceOperationModel(Base):", second_deal)
if end_of_stale == -1:
    raise SystemExit("[FAIL] db_models.py: BalanceOperationModel anchor not found")
stale = text[second_deal:end_of_stale]
for expected in ("class DealModel(Base):", "class PositionModel(Base):", "original_deal_id"):
    if expected not in stale:
        raise SystemExit(f"[FAIL] stale region does not contain {expected!r}")
write(DBM, text[:second_deal] + text[end_of_stale:])
log.append(f"db_models.py: removed {len(stale)} chars of stale duplicate DealModel + PositionModel")

# Keep the one column from the stale model that the MT5-accurate model lacks. It is
# the link that makes MT5 trade modification (reversal + correction) queryable.
replace(
    DBM,
    "    # External references\n    external_id = Column(String, nullable=True)\n    order_ticket = Column(String, nullable=True)",
    "    # External references\n"
    "    external_id = Column(String, nullable=True)\n"
    "    order_ticket = Column(String, nullable=True)\n"
    "    # MT5 trade modification chains a reversal + correction deal back to the\n"
    "    # deal it corrects. IDealRepository.find_trade_modifications() reads this.\n"
    "    original_deal_id = Column(String, nullable=True, index=True)",
    "preserved original_deal_id on the surviving DealModel",
)

# Leftover AI-chat instructions pasted into production source.
for marker in (
    "# Find the existing OrderModel class and REPLACE it with:",
    "# Find the existing DealModel class and REPLACE it with:",
    "# Find the existing PositionModel class and REPLACE it with:",
):
    text = read(DBM)
    for variant in (marker, marker.replace(":", ":")):
        if variant in text:
            text = text.replace(variant + "\r\n", "").replace(variant + "\n", "")
            text = text.replace(variant, "")
            write(DBM, text)
            log.append("db_models.py: deleted leftover chat instruction comment")
            break

# ===========================================================================
# domain_events.py
# ===========================================================================

EVT = "core/events/domain_events.py"

text = read(EVT)
marker_variants = [
    "# Add these to core/events/domain_events.py",
]
found = None
for marker in marker_variants:
    for variant in (marker, marker.replace("\n", "\r\n")):
        at = text.find(variant)
        if at != -1:
            found = (variant, at)
            break
    if found:
        break
if not found:
    raise SystemExit("[FAIL] domain_events.py: could not locate the appended event block")
marker, at = found
tail = text[at:]
if "class TradeModified" not in tail:
    raise SystemExit("[FAIL] domain_events.py: appended block does not hold TradeModified")
text = text[:at].rstrip("\r\n") + "\r\n"
write(EVT, text)
log.append(f"domain_events.py: dropped appended block ({len(tail)} chars) with the duplicate OrderCancelled/OrderModified")

# TradeModified was only defined in the block we just removed, and modify_deal.py
# publishes it. Re-add it properly, with an event_type like every other event.
replace(
    EVT,
    "    DEAL_MODIFIED = \"deal.modified\"  # For MT5-style trade corrections",
    "    DEAL_MODIFIED = \"deal.modified\"  # For MT5-style trade corrections\n"
    "    TRADE_MODIFIED = \"trade.modified\"  # MT5 reversal + correction pair",
    "added EventType.TRADE_MODIFIED",
)

# Config-plane events imported by config_cache.py, create_group.py and api/main.py
# but never defined. Without these the API server cannot start.
CONFIG_EVENTS = '''

# =============================================================================
# CONFIGURATION PLANE Events
# =============================================================================
# These drive ConfigCache invalidation. MT5's equivalent is the sink pattern:
# IMTConGroupSink::OnGroupUpdate, IMTConSymbolSink::OnSymbolUpdate and so on, which
# notify every connected manager terminal when a configuration object changes.
# Publishing them on the event bus is how our nodes stay in step.
# =============================================================================

@dataclass(frozen=True)
class GroupCreated(DomainEvent):
    """A new Group (rule engine) was created."""
    event_type: EventType = field(default=EventType.GROUP_CREATED, init=False)


@dataclass(frozen=True)
class GroupUpdated(DomainEvent):
    """A Group's configuration changed. Every node must invalidate its cache."""
    event_type: EventType = field(default=EventType.GROUP_UPDATED, init=False)


@dataclass(frozen=True)
class GroupDeleted(DomainEvent):
    """A Group was removed."""
    event_type: EventType = field(default=EventType.GROUP_DELETED, init=False)


@dataclass(frozen=True)
class SymbolCreated(DomainEvent):
    """A new Symbol was added to the price list."""
    event_type: EventType = field(default=EventType.SYMBOL_CREATED, init=False)


@dataclass(frozen=True)
class SymbolUpdated(DomainEvent):
    """A Symbol's specification changed (sessions, margin rates, swaps, limits)."""
    event_type: EventType = field(default=EventType.SYMBOL_UPDATED, init=False)


@dataclass(frozen=True)
class SymbolDeleted(DomainEvent):
    """A Symbol was removed from the price list."""
    event_type: EventType = field(default=EventType.SYMBOL_DELETED, init=False)


@dataclass(frozen=True)
class HolidayUpdated(DomainEvent):
    """A holiday was changed, affecting sessions and triple-swap scheduling."""
    event_type: EventType = field(default=EventType.HOLIDAY_UPDATED, init=False)


@dataclass(frozen=True)
class HolidayDeleted(DomainEvent):
    """A holiday was removed."""
    event_type: EventType = field(default=EventType.HOLIDAY_DELETED, init=False)


@dataclass(frozen=True)
class TradeModified(DomainEvent):
    """A dealer corrected a trade via the MT5 reversal + correction pattern."""
    event_type: EventType = field(default=EventType.TRADE_MODIFIED, init=False)
'''

text = read(EVT)
text = text.rstrip("\r\n") + CONFIG_EVENTS.replace("\n", "\r\n") + "\r\n"
write(EVT, text)
log.append("domain_events.py: added GroupCreated/Updated/Deleted, SymbolCreated/Updated/Deleted, HolidayUpdated/Deleted, TradeModified")

replace(
    EVT,
    "    BALANCE_CORRECTED = \"ledger.balance_corrected\"",
    "    BALANCE_CORRECTED = \"ledger.balance_corrected\"\n"
    "\n"
    "    # Configuration plane events (drive ConfigCache invalidation)\n"
    "    GROUP_CREATED = \"config.group_created\"\n"
    "    GROUP_UPDATED = \"config.group_updated\"\n"
    "    GROUP_DELETED = \"config.group_deleted\"\n"
    "    SYMBOL_CREATED = \"config.symbol_created\"\n"
    "    SYMBOL_UPDATED = \"config.symbol_updated\"\n"
    "    SYMBOL_DELETED = \"config.symbol_deleted\"\n"
    "    HOLIDAY_UPDATED = \"config.holiday_updated\"\n"
    "    HOLIDAY_DELETED = \"config.holiday_deleted\"",
    "added the eight config-plane EventType members",
)

replace(
    EVT,
    "# Add to core/events/domain_events.py",
    "# Margin state machine transitions, published by TickMarginPipeline",
    "replaced a leftover chat instruction comment",
)

# ===========================================================================
# group_repository.py - imports value objects that were renamed away
# ===========================================================================

replace(
    "infrastructure/persistence/repositories/group_repository.py",
    "from core.domains.accounts.models import Group, MarginProfile, CommissionProfile, ExecutionProfile, ExecutionMode",
    "from core.domains.accounts.models import Group",
    "group_repository now imports only the names that still exist",
)

replace(
    "infrastructure/persistence/repositories/group_repository.py",
    "    async def get_all_groups(self) -> List[Group]:",
    "    async def get_all(self) -> List[Group]:\n"
    "        \"\"\"Every group. Called once at startup to warm the ConfigCache.\"\"\"\n"
    "        return await self.get_all_groups()\n"
    "\n"
    "    async def find_by_id(self, group_id: str) -> Optional[Group]:\n"
    "        \"\"\"Look a group up by its surrogate id.\"\"\"\n"
    "        async with self.session_factory() as session:\n"
    "            result = await session.execute(\n"
    "                select(GroupModel).where(GroupModel.group_id == group_id)\n"
    "            )\n"
    "            model = result.scalar_one_or_none()\n"
    "            return db_to_group(model) if model else None\n"
    "\n"
    "    async def delete(self, group_id: str) -> bool:\n"
    "        async with self.session_factory() as session:\n"
    "            result = await session.execute(\n"
    "                select(GroupModel).where(GroupModel.group_id == group_id)\n"
    "            )\n"
    "            model = result.scalar_one_or_none()\n"
    "            if model is None:\n"
    "                return False\n"
    "            await session.delete(model)\n"
    "            await session.commit()\n"
    "            return True\n"
    "\n"
    "    async def get_all_groups(self) -> List[Group]:",
    "group_repository satisfies the merged IGroupRepository contract",
)

# ===========================================================================
# di_providers.py - duplicate handler factory, and the missing container getter
# ===========================================================================

DI = "api/di_providers.py"
text = read(DI)
first = text.find("def get_cancel_order_handler(")
second = text.find("def get_cancel_order_handler(", first + 1)
if second != -1:
    end = text.find("\ndef ", second + 1)
    if end == -1:
        raise SystemExit("[FAIL] di_providers.py: could not bound the duplicate")
    # Keep the later definition: it is the one that resolves from the container.
    text = text[:first] + text[end + 1:]
    write(DI, text)
    log.append("di_providers.py: removed the earlier duplicate get_cancel_order_handler")

# GroupModel needs a surrogate id column for IGroupRepository.find_by_id / delete.
# The MT5 natural key is the group path ("real\\real"), which stays the primary key;
# this is the uuid our domain Group.id already carries.
replace(
    "infrastructure/persistence/db_models.py",
    'class GroupModel(Base):\n    """Database model for Group (rule engine)."""\n    __tablename__ = "groups"\n    name = Column(String(128), primary_key=True)',
    'class GroupModel(Base):\n'
    '    """Database model for Group (rule engine)."""\n'
    '    __tablename__ = "groups"\n'
    '    # MT5\'s natural key for a group is its path, e.g. "real\\\\real".\n'
    '    name = Column(String(128), primary_key=True)\n'
    '    # Surrogate id carried by the domain Group entity.\n'
    '    group_id = Column(String(64), nullable=True, unique=True, index=True)',
    "added GroupModel.group_id so IGroupRepository.find_by_id/delete can work",
)

if "def get_di_container" not in read(DI):
    block_path = pathlib.Path(__file__).resolve().parent / "blocks" / "di_container.py.txt"
    block = block_path.read_text(encoding="utf-8")
    append_block(
        DI,
        "def get_account_repo()",
        block,
        "added get_di_container + a resolve()-capable view over the dict container",
    )
    replace(
        DI,
        "def register_di_providers(providers: dict[str, Any]) -> None:\n"
        '    """Register runtime dependencies (repos, handlers, engines) into global container."""\n'
        "    _container.update(providers)",
        "# Port classes resolved through get_di_container().resolve(...), mapped to the\n"
        "# string keys the dict container actually uses. Extending this table is how a new\n"
        "# port becomes resolvable at startup.\n"
        "register_port_keys(\n"
        "    {\n"
        "        IGroupRepository: \"group_repo\",\n"
        "        IEventBus: \"event_bus\",\n"
        "    }\n"
        ")\n"
        "\n"
        "\n"
        "def register_di_providers(providers: dict[str, Any]) -> None:\n"
        '    """Register runtime dependencies (repos, handlers, engines) into global container."""\n'
        "    _container.update(providers)",
        "registered the port -> container-key mappings resolve() needs",
    )
    replace(
        DI,
        "from core.ports.interfaces import IGroupRepository, IEventBus",
        "from core.ports.interfaces import (\n"
        "    IGroupRepository,\n"
        "    IEventBus,\n"
        "    IAccountRepository,\n"
        "    ISymbolRepository,\n"
        "    IHolidayRepository,\n"
        "    IPositionRepository,\n"
        ")",
        "imported the ports api/main.py resolves at startup",
    )
    replace(
        DI,
        "        IGroupRepository: \"group_repo\",\n"
        "        IEventBus: \"event_bus\",",
        "        IGroupRepository: \"group_repo\",\n"
        "        IEventBus: \"event_bus\",\n"
        "        IAccountRepository: \"account_repo\",\n"
        "        ISymbolRepository: \"symbol_repo\",\n"
        "        IHolidayRepository: \"holiday_repo\",\n"
        "        IPositionRepository: \"position_repo\",",
        "mapped every startup port to its container key",
    )

print("\n".join(f"  ok  {entry}" for entry in log))
print(f"\n{len(log)} edits applied.")
