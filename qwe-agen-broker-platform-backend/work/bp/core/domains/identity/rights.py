"""MT5 rights, as named data instead of positional mystery.

Two masks live here, both straight out of the SDK:

``ManagerRightsMask``
    MT5 has no role enum for staff. A manager's permissions are a FIXED-LENGTH
    128-element array of "0"/"1" strings (``IMTConManager::Rights``), positionally
    indexed by ``IMTConManager::EnManagerRights``. The right number IS the array
    index. This VO gives those positions names and refuses to guess: an unknown
    name or an out-of-range index raises ``UnknownRightError`` rather than being
    silently dropped, because a silently dropped bit is either a manager who
    cannot do their job or - worse - one who can do everything.

``UserRight``
    The account's own 16+ bit permission mask (``IMTUser::EnUsersRights``),
    stored in ``accounts.rights``. An IntFlag, because MT5 defines it as one.

The tables come from ``config/identity/*.yaml``, GENERATED from the SDK by
``scripts/dev/extract_identity_yaml.py`` - not typed by hand, per the project
rule that the SDK is the schema authority.

Storage compatibility (pinned by tests, not by hope):
    ``to_masks``/``from_masks`` use the same three-words-of-43-bits packing as
    ``infrastructure.persistence.account_models`` (a BigInteger column is
    64-bit SIGNED; 128 rights do not fit in two words). ``to_array``/
    ``from_array`` are MT5's wire form: 128 strings, "0"/"1".
"""
from __future__ import annotations

import os
from dataclasses import dataclass
from enum import IntFlag
from pathlib import Path
from typing import Any, Dict, Iterable, Iterator, List, Optional, Sequence, Tuple

#: Length of MT5's ConfigManagers Rights array.
RIGHTS_COUNT = 128

#: Mask packing, identical to infrastructure.persistence.account_models:
#: three 43-bit words keep every mask inside signed-64-bit range on both
#: PostgreSQL and SQLite.
RIGHTS_BITS_PER_WORD = 43
RIGHTS_WORDS = 3


class UnknownRightError(ValueError):
    """A right name/index that is not in MT5's enum. Refuse, never coerce."""


# ---------------------------------------------------------------------------
# Config location
# ---------------------------------------------------------------------------

def _config_dir() -> Path:
    override = os.environ.get("BROKER_IDENTITY_CONFIG_DIR")
    if override:
        return Path(override)
    # core/domains/identity/rights.py -> parents[3] is the bp root
    return Path(__file__).resolve().parents[3] / "config" / "identity"


def _load_yaml(name: str) -> Dict[str, Any]:
    import yaml  # declared dependency (pyyaml)

    path = _config_dir() / name
    if not path.exists():
        raise FileNotFoundError(
            f"identity config {path} is missing; regenerate it with "
            "scripts/dev/extract_identity_yaml.py (the tables are generated from "
            "the MT5 SDK, never hand-edited)"
        )
    with path.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle) or {}


# ---------------------------------------------------------------------------
# Manager rights registry (EnManagerRights)
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class ManagerRight:
    """One named position in MT5's 128-element manager rights array."""

    index: int
    name: str
    plane: str = ""
    description: str = ""
    #: RIGHT_LAST (128) is the enum terminator, not a grantable permission.
    sentinel: bool = False


class ManagerRightsRegistry:
    """The EnManagerRights table, loaded once from YAML."""

    def __init__(self, rights: Sequence[ManagerRight]) -> None:
        self._by_index: Dict[int, ManagerRight] = {r.index: r for r in rights}
        self._by_name: Dict[str, ManagerRight] = {r.name: r for r in rights}
        dupes = len(rights) - len(self._by_index)
        if dupes:
            raise ValueError(f"manager_rights.yaml has {dupes} duplicate indices; refusing to load")

    @classmethod
    def load(cls) -> "ManagerRightsRegistry":
        raw = _load_yaml("manager_rights.yaml").get("rights") or []
        rights = [
            ManagerRight(
                index=int(r["index"]),
                name=str(r["name"]),
                plane=str(r.get("plane", "")),
                description=str(r.get("description", "")),
                sentinel=bool(r.get("sentinel", False)),
            )
            for r in raw
        ]
        return cls(rights)

    def all(self) -> List[ManagerRight]:
        return [self._by_index[i] for i in sorted(self._by_index)]

    def grantable(self) -> List[ManagerRight]:
        """Every right except the RIGHT_LAST sentinel."""
        return [r for r in self.all() if not r.sentinel]

    def by_name(self, name: str) -> ManagerRight:
        try:
            return self._by_name[name]
        except KeyError:
            raise UnknownRightError(
                f"unknown manager right {name!r}; not in IMTConManager::EnManagerRights"
            ) from None

    def by_index(self, index: int) -> ManagerRight:
        try:
            return self._by_index[int(index)]
        except KeyError:
            raise UnknownRightError(
                f"index {index!r} is not a manager right in IMTConManager::EnManagerRights"
            ) from None

    def resolve(self, right: Any) -> ManagerRight:
        """Accept a name, an index or a ManagerRight. Refuse anything else."""
        if isinstance(right, ManagerRight):
            return right
        if isinstance(right, bool):  # bool is an int - refuse it explicitly
            raise UnknownRightError(f"{right!r} is not a manager right")
        if isinstance(right, int):
            resolved = self.by_index(right)
        elif isinstance(right, str):
            resolved = self.by_name(right)
        else:
            raise UnknownRightError(f"{right!r} is not a manager right")
        if resolved.sentinel:
            raise UnknownRightError(
                f"{resolved.name} is the enumeration terminator (index {resolved.index}); "
                "it is not a grantable right"
            )
        return resolved


_REGISTRY: Optional[ManagerRightsRegistry] = None


def get_manager_rights() -> ManagerRightsRegistry:
    """Process-wide registry. Loaded on first use; the YAML is part of the repo."""
    global _REGISTRY
    if _REGISTRY is None:
        _REGISTRY = ManagerRightsRegistry.load()
    return _REGISTRY


def reset_manager_rights_cache() -> None:
    """Test hook: drop the cached registry (e.g. after pointing the env var elsewhere)."""
    global _REGISTRY
    _REGISTRY = None


# ---------------------------------------------------------------------------
# The mask VO
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class ManagerRightsMask:
    """An immutable set of granted manager rights.

    Immutable on purpose: ``grant``/``revoke``/``merge`` return NEW masks, so a
    caller holding a manager's authorisation snapshot cannot have it mutated
    underneath them mid-request. Equality is by granted index set - two masks
    built from different representations (names, wire array, DB masks) compare
    equal when they grant the same rights.
    """

    indices: frozenset = frozenset()

    # -- construction -------------------------------------------------------

    @classmethod
    def empty(cls) -> "ManagerRightsMask":
        return cls(frozenset())

    @classmethod
    def all_rights(cls) -> "ManagerRightsMask":
        """Every grantable right (the seeder's first-admin shape)."""
        registry = get_manager_rights()
        return cls(frozenset(r.index for r in registry.grantable()))

    @classmethod
    def from_names(cls, names: Iterable[str]) -> "ManagerRightsMask":
        registry = get_manager_rights()
        return cls(frozenset(registry.resolve(n).index for n in names))

    @classmethod
    def from_indices(cls, indices: Iterable[int]) -> "ManagerRightsMask":
        """Positions are range-checked, NOT registry-checked: the wire is the
        authority on positions. MT5's documented enum leaves indices 2-9 (and
        68-69, 89-95, 113-127) unnamed, yet the live export's administrators
        carry 1s at 2-9 and 68-69 - a mask that refused unnamed positions
        could not represent a real server's admin."""
        out = set()
        for i in indices:
            if not isinstance(i, int) or isinstance(i, bool):
                raise UnknownRightError(f"{i!r} is not a right index")
            if not 0 <= i < RIGHTS_COUNT:
                raise UnknownRightError(
                    f"right index {i} outside 0..{RIGHTS_COUNT - 1} (the wire array length)"
                )
            out.add(i)
        return cls(frozenset(out))

    @classmethod
    def from_array(cls, array: Sequence[Any]) -> "ManagerRightsMask":
        """MT5's wire form: 128 positional "0"/"1" strings (bools/ints accepted)."""
        if array is None:
            return cls.empty()
        items = list(array)
        if len(items) > RIGHTS_COUNT:
            raise UnknownRightError(
                f"rights array has {len(items)} entries; MT5's array is exactly {RIGHTS_COUNT}"
            )
        out = set()
        for index, value in enumerate(items):
            if str(value).strip() in ("1", "true", "True"):
                out.add(index)
        return cls(frozenset(out))

    @classmethod
    def from_masks(cls, masks: Sequence[int]) -> "ManagerRightsMask":
        """Inverse of :meth:`to_masks` (the three DB BigInteger columns)."""
        words = list(masks or [])
        out = set()
        for index in range(RIGHTS_COUNT):
            word, bit = divmod(index, RIGHTS_BITS_PER_WORD)
            value = words[word] if word < len(words) else 0
            if (int(value or 0) >> bit) & 1:
                out.add(index)
        return cls(frozenset(out))

    # -- conversion ---------------------------------------------------------

    def to_names(self) -> List[str]:
        """Granted right names, ordered by index (MT5's own display order).

        Tolerant by design: a wire array may carry "1" at indices MT5's enum
        leaves unassigned (the live export's administrators have 68 and 69 set),
        and preserving those bits is more important than naming them. Unnamed
        bits are skipped here and survive every round trip via to_array().
        """
        registry = get_manager_rights()
        names = []
        for i in sorted(self.indices):
            try:
                names.append(registry.by_index(i).name)
            except UnknownRightError:
                continue
        return names

    def unnamed_indices(self) -> List[int]:
        """Granted indices with no name in EnManagerRights (wire preservation)."""
        registry = get_manager_rights()
        out = []
        for i in sorted(self.indices):
            try:
                registry.by_index(i)
            except UnknownRightError:
                out.append(i)
        return out

    def to_array(self) -> List[str]:
        """MT5's wire form: exactly 128 "0"/"1" strings."""
        return ["1" if i in self.indices else "0" for i in range(RIGHTS_COUNT)]

    def to_masks(self) -> Tuple[int, int, int]:
        """The three signed-64-bit-safe DB words, matching account_models packing."""
        masks = [0] * RIGHTS_WORDS
        for index in self.indices:
            word, bit = divmod(index, RIGHTS_BITS_PER_WORD)
            if word < RIGHTS_WORDS:
                masks[word] |= 1 << bit
        return masks[0], masks[1], masks[2]

    # -- queries & set ops (all return NEW masks) ----------------------------

    @staticmethod
    def _index_of(right: Any) -> int:
        """Name -> registry (strict; a misspelled right must explode, not pass).
        Int -> range check (unnamed positions are legal, see from_indices)."""
        if isinstance(right, ManagerRight):
            return right.index
        if isinstance(right, bool):
            raise UnknownRightError(f"{right!r} is not a manager right")
        if isinstance(right, int):
            if not 0 <= right < RIGHTS_COUNT:
                raise UnknownRightError(
                    f"right index {right} outside 0..{RIGHTS_COUNT - 1}"
                )
            return right
        if isinstance(right, str):
            return get_manager_rights().resolve(right).index
        raise UnknownRightError(f"{right!r} is not a manager right")

    def has(self, right: Any) -> bool:
        return self._index_of(right) in self.indices

    def grant(self, *rights: Any) -> "ManagerRightsMask":
        added = {self._index_of(r) for r in rights}
        return ManagerRightsMask(self.indices | added)

    def revoke(self, *rights: Any) -> "ManagerRightsMask":
        removed = {self._index_of(r) for r in rights}
        return ManagerRightsMask(self.indices - removed)

    def merge(self, other: "ManagerRightsMask") -> "ManagerRightsMask":
        if not isinstance(other, ManagerRightsMask):
            raise TypeError(f"cannot merge ManagerRightsMask with {type(other).__name__}")
        return ManagerRightsMask(self.indices | other.indices)

    def without(self, other: "ManagerRightsMask") -> "ManagerRightsMask":
        return ManagerRightsMask(self.indices - other.indices)

    @property
    def count(self) -> int:
        return len(self.indices)

    # -- dunders -------------------------------------------------------------

    def __contains__(self, right: Any) -> bool:
        return self.has(right)

    def __iter__(self) -> Iterator[int]:
        return iter(sorted(self.indices))

    def __len__(self) -> int:
        return len(self.indices)

    def __repr__(self) -> str:  # pragma: no cover - debugging aid
        return f"ManagerRightsMask({self.count} rights)"


# ---------------------------------------------------------------------------
# Account rights (IMTUser::EnUsersRights)
# ---------------------------------------------------------------------------

class UserRight(IntFlag):
    """The account's own permission mask. Values are MT5's, exactly."""

    NONE = 0x0
    ENABLED = 0x1                  # may connect at all
    PASSWORD = 0x2                 # may change their own password
    TRADE_DISABLED = 0x4           # INVERTED sense: trading is disabled
    INVESTOR = 0x8                 # internal: investor-password session
    CONFIRMED = 0x10               # certificate confirmed
    TRAILING = 0x20                # may use trailing stops
    EXPERT = 0x40                  # may use Expert Advisors
    OBSOLETE = 0x80                # unused
    REPORTS = 0x100                # receives daily reports
    READONLY = 0x200               # internal
    RESET_PASS = 0x400             # must change password at next login
    OTP_ENABLED = 0x800            # may use OTP (if the group allows)
    SPONSORED_HOSTING = 0x2000     # broker-paid VPS
    API_ENABLED = 0x4000           # Web API - obsolete, unused
    PUSH_NOTIFICATION = 0x8000     # push from the trade server
    TECHNICAL = 0x10000            # technical account, hidden from regular managers
    EXCLUDE_REPORTS = 0x20000      # excluded from server reports

    @classmethod
    def from_flags(cls, value: Any) -> "UserRight":
        """Coerce a stored bigint into the flag set. Refuses unknown bits."""
        raw = int(value or 0)
        known = 0
        for member in cls:
            known |= member.value
        unknown = raw & ~known
        if unknown:
            raise ValueError(
                f"accounts.rights carries bits outside IMTUser::EnUsersRights: {unknown:#x}; "
                "refusing to guess what they mean"
            )
        return cls(raw)

    def to_flags(self) -> int:
        return int(self.value)


#: What a brand-new account gets before any Limits/Account tab is touched
#: (ACCOUNT-GROUP-CREATION-SPEC §6: default ENABLED | PASSWORD).
DEFAULT_NEW_ACCOUNT_RIGHTS = UserRight.ENABLED | UserRight.PASSWORD


@dataclass(frozen=True)
class UserRightDescriptor:
    """UI metadata for one USER_RIGHT_* flag (tab, label, inverted sense)."""

    name: str
    bit: int
    flag: str
    tab: Optional[str]
    label: str
    inverted: bool
    description: str = ""


_USER_DESCRIPTORS: Optional[List[UserRightDescriptor]] = None


def user_right_descriptors() -> List[UserRightDescriptor]:
    """The account_rights.yaml table, for the /schema endpoints and the UI."""
    global _USER_DESCRIPTORS
    if _USER_DESCRIPTORS is None:
        raw = _load_yaml("account_rights.yaml").get("flags") or []
        _USER_DESCRIPTORS = [
            UserRightDescriptor(
                name=str(r["name"]),
                bit=int(r["bit"]),
                flag=str(r["flag"]),
                tab=(str(r["tab"]) if r.get("tab") not in (None, "null") else None),
                label=str(r.get("label", r["name"])),
                inverted=bool(r.get("inverted", False)),
                description=str(r.get("description", "")),
            )
            for r in raw
        ]
    return list(_USER_DESCRIPTORS)


def reset_user_rights_cache() -> None:
    """Test hook."""
    global _USER_DESCRIPTORS
    _USER_DESCRIPTORS = None
