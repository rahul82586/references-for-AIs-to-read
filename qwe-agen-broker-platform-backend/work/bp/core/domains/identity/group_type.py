"""The ONE group-type rule - MT5's, verbatim, in one function.

Administrator guide, ``Groups/Group-Types.md``:

    "A created group is considered a demo one if its name (including path)
     includes 'demo' symbols (case sensitive). For example, the 'demo\\forex',
     'demo-USD' and 'real\\demoforex-USD' groups are demo and the 'Demoforex'
     'fx-USD' groups are not."

    "Groups are considered manager ones if their names (including path) include
     'manager' symbols (case sensitive)."  ...contest: "include 'contest'"...
     coverage: "include 'coverage'"...

    "If a group doesn't fall into any category by its name among the ones
     mentioned above, then the system considers it a real one."

Why this module exists: the rule lived inline (prefix-based and case-INsensitive)
in ``infrastructure.mt5.enums.account_type_from_group_path`` and would have been
re-typed a third time inside CreateGroupHandler. Two copies of a money rule drift;
the seeder, the loader, the create path and the tests now all call
:func:`derive_group_type`, and that function delegates nothing.

Divergences from the old prefix rule, both in MT5's favour and both pinned by
tests:
    * "Demoforex"          old: DEMO (case-insensitive)   MT5: REAL (case-SENSITIVE)
    * "real\\demoforex-USD" old: REAL (prefix 'real')      MT5: DEMO (substring)

Ambiguity: the guide forbids mixing type markers in one name ("Do not use
indications of different group types within the name of a group. For example,
managers\\demo") but does not define who wins if you do anyway. Our documented
order is manager > contest > demo > coverage > preliminary > real-fallback:
misclassifying toward the MORE restricted type is the safe failure (a demo group
mistaken for a manager group blocks client self-opening, which is visible; the
reverse would let clients open staff accounts, which is not).
"""
from __future__ import annotations

from typing import Optional

from core.domains.accounts.enums import AccountType

#: MT5's maximum group name length (SDK IMTConGroup). Our column is String(128);
#: the wire and the UI honour 64.
GROUP_NAME_MAX_LENGTH = 64


class InvalidGroupNameError(ValueError):
    """A group name MT5 would refuse. Carries every reason, not just the first."""


def derive_group_type(name: str) -> AccountType:
    """The AccountType MT5 assigns to a group with this name.

    Case-sensitive substring match on the FULL name including path, exactly as
    Group-Types.md specifies. Never returns None: an unmarked name is REAL by
    MT5's own fallback rule. The single "preliminary" group is matched on its
    exact name - the guide says one group called "preliminary" is auto-created,
    not that any name containing the word is preliminary.
    """
    if not name or not str(name).strip():
        raise InvalidGroupNameError("group name must not be empty")
    text = str(name)

    # Manager first: only manager groups may hold staff logins, and the guide's
    # own example ("manager_real") proves 'manager' outranks 'real'.
    if "manager" in text:
        return AccountType.MANAGER
    if "contest" in text:
        return AccountType.CONTEST
    if "demo" in text:
        return AccountType.DEMO
    if "coverage" in text:
        return AccountType.COVERAGE
    if text.replace("/", "\\").strip("\\") == "preliminary":
        return AccountType.PRELIMINARY
    # "real" substring and everything else: MT5's fallback is real either way.
    return AccountType.REAL


def validate_group_name(name: str) -> str:
    """Validate a group name/path the way the create and update paths must.

    Returns the trimmed name. Raises InvalidGroupNameError listing EVERY problem
    (an operator fixing one at a time through a UI is a support ticket per round
    trip). Rules: non-empty; <= 64 chars; backslash-separated path segments; no
    leading/trailing separator; no empty segments; no forward slashes (MT5's
    separator is "\\"; the REST layer translates "/" forms before this point).
    """
    reasons = []
    text = (name or "").strip()
    if not text:
        raise InvalidGroupNameError("group name must not be empty")
    if len(text) > GROUP_NAME_MAX_LENGTH:
        reasons.append(
            f"longer than {GROUP_NAME_MAX_LENGTH} characters ({len(text)})"
        )
    if "/" in text:
        reasons.append("contains '/': MT5 group paths use '\\' as the separator")
    if text.startswith("\\") or text.endswith("\\"):
        reasons.append("must not start or end with '\\'")
    if "\\" in text and any(not seg.strip() for seg in text.split("\\")):
        reasons.append("contains an empty path segment ('a\\\\\\\\b' style double separator)")
    if reasons:
        raise InvalidGroupNameError(
            f"invalid group name {name!r}: " + "; ".join(reasons)
        )
    return text


def is_manager_group(name: str) -> bool:
    """MT5's staff rule: 'Manager accounts can only be created on the basis of
    accounts that belong to the manager groups.' CreateManagerHandler refuses
    without this."""
    return "manager" in str(name or "")


def derive_group_type_optional(name: str) -> Optional[AccountType]:
    """derive_group_type for callers that must tolerate an empty name (imports of
    half-formed rows). Empty -> None; anything else follows the same rule."""
    if not name or not str(name).strip():
        return None
    return derive_group_type(name)
