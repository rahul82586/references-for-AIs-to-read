"""
Step M0 part 1 - make the codebase importable.

Fixes the nine missing-import defects and merges the duplicate definitions that an
append-instead-of-merge refactor left behind. In every merge the MT5-accurate
definition survives, and where both halves had methods worth keeping the survivor is
the union, so no call site breaks.

Usage:  cd <broker-platform root> && python3 /path/to/m0_fix_imports.py
"""

from __future__ import annotations

import pathlib
import sys

ROOT = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else pathlib.Path.cwd()
if not (ROOT / "core" / "ports" / "interfaces.py").is_file():
    raise SystemExit(f"not a broker-platform root: {ROOT}")

log: list[str] = []


def read(rel: str) -> str:
    # newline="" preserves CRLF exactly, so patches never rewrite line endings.
    with open(ROOT / rel, "r", encoding="utf-8", newline="") as handle:
        return handle.read()


def write(rel: str, text: str) -> None:
    with open(ROOT / rel, "w", encoding="utf-8", newline="") as handle:
        handle.write(text)


def sub(rel: str, old: str, new: str) -> None:
    """Replace one occurrence, tolerating CRLF or LF line endings in the target."""
    text = read(rel)
    for old_v, new_v in ((old, new), (old.replace("\n", "\r\n"), new.replace("\n", "\r\n"))):
        if old_v in text:
            write(rel, text.replace(old_v, new_v, 1))
            log.append(f"{rel}: patched")
            return
    raise SystemExit(f"[FAIL] {rel}: pattern not found:\n  {old[:160]!r}")


def nl(rel: str, s: str) -> str:
    """Render a block with the target file's own line ending."""
    return s.replace("\n", "\r\n") if "\r\n" in read(rel) else s


# ===========================================================================
# 1. core/ports/interfaces.py
#    - `Any` used in signatures but never imported -> NameError at class-body
#      evaluation, which broke every module importing ports and all 10 test modules.
#    - IOrderRepository / IDealRepository / IPositionRepository each defined twice;
#      the appended (MT5-accurate) definition silently shadowed the original.
#    - IGroupRepository never defined at all, yet imported by six modules.
# ===========================================================================

IFACE = "core/ports/interfaces.py"

sub(
    IFACE,
    "from typing import List, Optional, TypeVar, Generic, Callable, AsyncIterator",
    "from typing import Any, List, Optional, TypeVar, Generic, Callable, AsyncIterator",
)

text = read(IFACE)

# The appended block begins at this banner and runs to EOF.
banner_variants = [
    "# ============================================================================",
]
appended_start = -1
for marker in ("# ORDER REPOSITORY - Add these methods",):
    at = text.find(marker)
    if at != -1:
        appended_start = text.rfind("\n", 0, text.rfind("\n", 0, at))
        break
if appended_start == -1:
    raise SystemExit("[FAIL] could not locate the appended repository block")

appended = text[appended_start:]


def extract(source: str, name: str) -> str:
    start = source.find(f"class {name}(ABC, Generic[T]):")
    if start == -1:
        raise SystemExit(f"[FAIL] appended class {name} not found")
    ends = [
        e
        for e in (source.find("\nclass ", start + 1), source.find("\n# =====", start + 1))
        if e != -1
    ]
    return source[start: min(ends)] if ends else source[start:]


# Sanity check: confirm the appended block really held all three duplicates.
for name in ("IOrderRepository", "IDealRepository", "IPositionRepository"):
    if f"class {name}(ABC, Generic[T]):" not in appended:
        raise SystemExit(f"[FAIL] appended block does not contain {name}")

text = text[:appended_start]
log.append(f"{IFACE}: dropped appended duplicate block ({len(appended)} chars)")

MERGED_ORDER = '''class IOrderRepository(ABC, Generic[T]):
    """
    Contract for Order persistence (MT5 IMTOrder).

    Architectural Purpose:
    Hides the database technology from the Domain. The OMS calls save() or
    find_by_id(), unaware of SQL or ORM, so the store can be swapped without
    touching business logic.
    """

    @abstractmethod
    async def save(self, order: T, session: Optional[Any] = None) -> T:
        """Persists an order aggregate. Handles both inserts and updates."""
        pass

    @abstractmethod
    async def find_by_id(self, order_id: str, session: Optional[Any] = None) -> Optional[T]:
        """Retrieves an order by its unique identifier, or None."""
        pass

    @abstractmethod
    async def find_by_account(self, account_login: int) -> List[T]:
        """Retrieves every order belonging to an account."""
        pass

    @abstractmethod
    async def find_active_orders_by_account(self, account_login: int) -> List[T]:
        """Retrieves open/pending orders for an account. Used by risk checks and UI."""
        pass

    @abstractmethod
    async def find_pending_orders(self, account_login: int) -> List[T]:
        """Get all pending orders (not filled/cancelled/rejected/expired)."""
        pass

    @abstractmethod
    async def find_by_symbol_and_state(self, symbol: str, state: str) -> List[T]:
        """Get orders by symbol and state."""
        pass

    @abstractmethod
    async def find_expired_orders(self, before_time: datetime) -> List[T]:
        """Get orders past their time_expiration, for the expiry sweeper."""
        pass

    @abstractmethod
    async def get_next_ticket_id(self) -> str:
        """Allocate the next sequential ticket id (MT5 style). Must be atomic."""
        pass

    @abstractmethod
    async def delete(self, order_id: str) -> bool:
        """Remove an order record. Returns True if a row was deleted."""
        pass
'''

MERGED_DEAL = '''class IDealRepository(ABC, Generic[T]):
    """
    Contract for Deal persistence (MT5 IMTDeal).

    Deals are immutable execution records: an append-only log. MT5 trade
    modification is a reversal plus a correction deal chained through
    original_deal_id, never a mutation of an existing deal.
    """

    @abstractmethod
    async def save(self, deal: T, session: Optional[Any] = None) -> T:
        """Persists an immutable deal entity."""
        pass

    @abstractmethod
    async def find_by_id(self, deal_id: str, session: Optional[Any] = None) -> Optional[T]:
        """Retrieves a deal by its unique identifier."""
        pass

    @abstractmethod
    async def find_by_order_id(self, order_id: str) -> List[T]:
        """Retrieves all deals generated by a given order."""
        pass

    @abstractmethod
    async def find_by_position_id(self, position_id: str) -> List[T]:
        """Get all deals that make up a position."""
        pass

    @abstractmethod
    async def find_by_account(self, account_login: int) -> List[T]:
        """Retrieves all deals executed for an account."""
        pass

    @abstractmethod
    async def find_by_account_and_symbol(self, account_login: int, symbol: str) -> List[T]:
        """Get deals for an account and symbol."""
        pass

    @abstractmethod
    async def find_by_entry_type(self, account_login: int, entry: str) -> List[T]:
        """Get deals by entry type (IN, OUT, INOUT, OUT_BY)."""
        pass

    @abstractmethod
    async def find_trade_modifications(self, original_deal_id: str) -> List[T]:
        """Get reversal and correction deals chained to an original deal."""
        pass
'''

MERGED_POSITION = '''class IPositionRepository(ABC, Generic[T]):
    """
    Contract for Position persistence (MT5 IMTPosition).

    Used by the risk engine and the margin loop to fetch open positions.
    """

    @abstractmethod
    async def save(self, position: T, session: Optional[Any] = None) -> T:
        """Persists a position (create or update)."""
        pass

    @abstractmethod
    async def find_by_id(self, position_id: str, session: Optional[Any] = None) -> Optional[T]:
        """Retrieves a position by id."""
        pass

    @abstractmethod
    async def get_open_positions(self, session: Optional[Any] = None) -> List[T]:
        """Returns all open positions across all accounts."""
        pass

    @abstractmethod
    async def get_positions_by_account(self, account_login: int) -> List[T]:
        """Returns all open positions for one account."""
        pass

    @abstractmethod
    async def get_by_account(self, account_login: int) -> List[T]:
        """Alias of get_positions_by_account, kept so existing callers do not break."""
        pass

    @abstractmethod
    async def get_by_account_and_symbol(self, account_login: int, symbol: str) -> List[T]:
        """Get positions for an account and symbol."""
        pass

    @abstractmethod
    async def get_by_symbol(self, symbol: str) -> List[T]:
        """Get all open positions in a symbol, for NOP/exposure calculation."""
        pass

    @abstractmethod
    async def get_closed_positions(
        self, account_login: int, from_time: datetime, to_time: datetime
    ) -> List[T]:
        """Get closed positions within a time range."""
        pass

    @abstractmethod
    async def close(self, position_id: str) -> bool:
        """Marks a position closed. Returns True on success."""
        pass

    @abstractmethod
    async def delete(self, position_id: str) -> bool:
        """Remove a position record."""
        pass
'''

GROUP_PORT = '''# =========================================================================
# GROUP REPOSITORY
# =========================================================================

class IGroupRepository(ABC, Generic[T]):
    """
    Contract for Group persistence.

    In MT5 a Group IS the rule engine: it carries leverage, margin call and
    stop-out levels, free-margin mode, commissions, swaps, trade permissions,
    per-symbol overrides and routing. This port is what ConfigCache loads at
    startup so the hot path never touches the database.
    """

    @abstractmethod
    async def save(self, group: T, session: Optional[Any] = None) -> T:
        """Persists a group (create or update)."""
        pass

    @abstractmethod
    async def find_by_id(self, group_id: str) -> Optional[T]:
        """Retrieves a group by its surrogate id."""
        pass

    @abstractmethod
    async def find_by_name(self, name: str) -> Optional[T]:
        """Retrieves a group by MT5 path-style name, e.g. 'real\\\\real'."""
        pass

    @abstractmethod
    async def get_all(self) -> List[T]:
        """Returns every group. Called once at startup to warm the ConfigCache."""
        pass

    @abstractmethod
    async def get_all_groups(self) -> List[T]:
        """Alias of get_all, kept so existing callers do not break."""
        pass

    @abstractmethod
    async def delete(self, group_id: str) -> bool:
        """Remove a group. Returns True on success."""
        pass


'''

# Replace each stale first definition with its merged survivor.
for stale, merged in (
    ("IOrderRepository", MERGED_ORDER),
    ("IDealRepository", MERGED_DEAL),
    ("IPositionRepository", MERGED_POSITION),
):
    start = text.find(f"class {stale}(ABC, Generic[T]):")
    if start == -1:
        raise SystemExit(f"[FAIL] stale {stale} not found")
    end = text.find("\nclass ", start + 1)
    if end == -1:
        raise SystemExit(f"[FAIL] could not find the end of stale {stale}")
    text = text[:start] + merged.rstrip("\n") + text[end:]
    log.append(f"{IFACE}: merged duplicate {stale} (union of both method sets)")

anchor = "class ISymbolRepository(ABC, Generic[T]):"
at = text.find(anchor)
if at == -1:
    raise SystemExit("[FAIL] ISymbolRepository anchor not found")
banner_at = text.rfind("# =====", 0, at)
insert_at = banner_at if banner_at != -1 else at
text = text[:insert_at] + GROUP_PORT + text[insert_at:]
log.append(f"{IFACE}: added the missing IGroupRepository port")

# The merged blocks were authored with LF; normalise the whole file to CRLF so it
# matches every other file in the repo and no diff is polluted by line endings.
write(IFACE, text.replace("\r\n", "\n").replace("\n", "\r\n"))

# ===========================================================================
# 2. The remaining missing imports
# ===========================================================================

sub(
    "application/commands/record_deal.py",
    "from typing import List, Optional",
    "from typing import Any, List, Optional",
)
sub(
    "core/domains/execution/router.py",
    "from typing import List, Optional",
    "from typing import Any, List, Optional",
)
sub(
    "application/services/execution_orchestrator.py",
    "from typing import Optional",
    "from typing import Any, Optional",
)
sub(
    "application/services/commission_service.py",
    "import logging\nfrom decimal import Decimal",
    "import logging\nfrom decimal import Decimal\nfrom typing import Any, Optional",
)
sub(
    "core/domains/ledger/engine.py",
    "from typing import Optional",
    "from typing import Optional\nfrom decimal import Decimal",
)
sub(
    "infrastructure/persistence/repositories/order_repository.py",
    "from typing import List, Optional",
    "from datetime import datetime\nfrom typing import List, Optional",
)
sub(
    "infrastructure/persistence/repositories/position_repository.py",
    "from typing import List, Optional",
    "from datetime import datetime\nfrom typing import List, Optional",
)
sub(
    "infrastructure/persistence/db_models.py",
    "from sqlalchemy import Column, Integer, String, Numeric, DateTime, Boolean, Text, ForeignKey, Index, func",
    "from sqlalchemy import (\n    BigInteger,\n    Boolean,\n    Column,\n    DateTime,\n    ForeignKey,\n    Index,\n    Integer,\n    Numeric,\n    String,\n    Text,\n    func,\n)",
)
# core.domains.oms.models does not exist; OrderType lives in the enums module.
sub(
    "application/services/swap_worker.py",
    "from core.domains.oms.models import OrderType",
    "from core.domains.oms.enums import OrderType",
)

print("\n".join(f"  ok  {entry}" for entry in log))
print(f"\n{len(log)} edits applied.")
