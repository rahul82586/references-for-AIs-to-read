"""A manager's Groups scope — MT5's mask list, with the guide's validity rules.

Administrator guide, *Managers → Common*:

    "In the 'Groups' field, groups of accounts that will be serviced by the
     manager should be specified … You can use mask '*' and negation sign '!' to
     set up groups. For example, if you specify 'demo*' it will indicate all
     groups, whose name (including path) starts with 'demo' … If you specify
     '!managers*,*', it will indicate all groups except those, whose name starts
     with 'managers'.

     * Rules for the groups are checked **from top to bottom**. If you allow all
       groups in the first row, you will not be able to prohibit some of them in
       the next rules.
     * **A rule cannot consist of prohibition only.** For example, the rule
       '!demo*' is not valid. A prohibition can be used together with a
       permission to see some other groups. For example, '!demo*,real*'."

Two separate facts are encoded here, and they are easy to conflate:

1. **Matching** is first-match-wins over the comma-separated list, a `!` match
   excluding and a plain match including; nothing matched means *not in scope*
   (fail closed). `ManagerAccount.in_group_scope` already implements this - it
   reproduces the guide's `"!managers*,*"` example exactly, and M15 pinned it
   with a test. This module does not duplicate it; it imports the same matcher so
   there is ONE implementation of MT5's scope semantics.

2. **Validity** is a property of the list as a whole, and nothing checked it
   before. `"!demo*"` alone is refused by MT5; `"*"` followed by `"!demo*"` is
   accepted but the second rule is dead. Both are operator mistakes that look
   like working configuration, and the second one silently grants more than the
   operator intended - a manager who believes they excluded demo would not have.

So `validate_group_scope` refuses the invalid list outright and *reports* the
unreachable rules, because refusing a list MT5 itself accepts would be inventing
a restriction, while silently keeping dead rules would be hiding one.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Optional, Sequence

from core.domains.identity.models import _mask_matches


class InvalidGroupScopeError(ValueError):
    """The scope list breaks one of MT5's rules. The message lists every reason."""

    def __init__(self, reasons: Sequence[str]) -> None:
        self.reasons = list(reasons)
        super().__init__("; ".join(self.reasons))


#: MT5 stores the scope in its own wire shape: [{"Group": "*"}]. Keeping that
#: shape is what makes a manager row re-export byte-identically, so the domain
#: speaks it too rather than translating at the edge.
def to_wire(patterns: Iterable[str]) -> List[Dict[str, str]]:
    """`["!managers*", "*"]` -> `[{"Group": "!managers*"}, {"Group": "*"}]`."""
    return [{"Group": str(p)} for p in patterns]


def from_wire(scope: Optional[Iterable[Any]]) -> List[str]:
    """The wire scope as a flat, ordered pattern list.

    Accepts both MT5's `[{"Group": "..."}]` and a plain list of strings, because
    an API body and a stored row arrive differently and the ORDER is meaningful
    (first match wins) - so this must never sort or deduplicate.
    """
    out: List[str] = []
    for entry in scope or []:
        if isinstance(entry, dict):
            value = entry.get("Group", entry.get("group"))
            if value is None:
                continue
            raw = str(value)
        else:
            raw = str(entry)
        # A single stored row may itself be a comma list - MT5's own example is
        # the ONE string "!managers*,*". Split it, preserving order.
        for part in raw.split(","):
            part = part.strip()
            if part:
                out.append(part)
    return out


@dataclass(frozen=True)
class ScopeAnalysis:
    """What a scope list actually does, for the UI to show before it is saved."""

    patterns: List[str]
    #: Indices of rules that can never decide anything, because an earlier rule
    #: already matches everything they could.
    unreachable: List[int]
    #: True when the list is a bare "*" - every group, which is what all nine
    #: live managers carry.
    allows_all: bool


def analyse_scope(scope: Optional[Iterable[Any]]) -> ScopeAnalysis:
    """Find the rules that can never fire.

    MT5: "If you allow all groups in the first row, you will not be able to
    prohibit some of them in the next rules." Generalised: any rule after an
    unconditional `*` is dead, because `*` matches every name and first match
    decides. This is a WARNING, not a refusal - MT5 accepts the list - but an
    operator who wrote `"*,!managers*"` believes they excluded staff groups and
    did not.
    """
    patterns = from_wire(scope)
    unreachable: List[int] = []
    seen_bare_wildcard = False
    for index, pattern in enumerate(patterns):
        if seen_bare_wildcard:
            unreachable.append(index)
        elif pattern == "*":
            seen_bare_wildcard = True
    return ScopeAnalysis(
        patterns=patterns,
        unreachable=unreachable,
        allows_all=seen_bare_wildcard,
    )


def validate_group_scope(
    scope: Optional[Iterable[Any]],
    *,
    allow_empty: bool = False,
) -> List[str]:
    """Normalise and validate a manager's Groups scope. Returns the pattern list.

    Refuses, with EVERY violation listed at once:

    * an empty scope, unless the caller opts in - an empty list matches nothing
      under first-match-wins, so it is a manager who can see no accounts at all.
      `manager_to_db` defaults it to `[{"Group": "*"}]`, so an empty scope
      arriving here is almost always a caller bug rather than an intent.
    * **prohibition-only**, the guide's own example: `"!demo*"` is not valid.
      A negation must be accompanied by at least one permission, because under
      first-match-wins a list of only negations excludes everything and grants
      nothing - MT5 refuses it rather than create a manager with no scope.
    * an empty pattern (`""`, or `"demo*,,"`), which would match nothing and
      silently truncate the list.
    * a pattern with more than one `*` or a `!` anywhere but the front. The
      matcher treats those literally, so `"de*mo"` would silently match nothing
      either - a typo that looks like a wildcard.

    Does NOT refuse unreachable rules; `analyse_scope` reports them.
    """
    patterns = from_wire(scope)
    reasons: List[str] = []

    if not patterns:
        if not allow_empty:
            reasons.append(
                "the Groups scope is empty; under MT5's first-match-wins rule an "
                "empty list matches nothing, so this manager could service no "
                "accounts at all. Use [\"*\"] for every group."
            )
        else:
            return []

    for pattern in patterns:
        if not pattern.strip():
            reasons.append("the scope contains an empty pattern")
            continue
        body = pattern[1:] if pattern.startswith("!") else pattern
        if "!" in body:
            reasons.append(
                f"{pattern!r}: '!' is only valid as the FIRST character of a rule "
                "(a later '!' is matched literally, so the rule would grant nothing)"
            )
        # _mask_matches honours a '*' only at the START, the END, or BOTH
        # ("*demo", "demo*", "*demo*" = contains). Anywhere else it is compared
        # literally, so "de*mo" matches a group literally named "de*mo" and
        # nothing else - a typo that reads like a wildcard and silently grants
        # nothing. Checked by stripping at most one leading and one trailing '*'
        # and requiring no '*' to survive, rather than by counting them, because
        # "*demo*" has two and is valid.
        stripped = body
        if stripped.startswith("*"):
            stripped = stripped[1:]
        if stripped.endswith("*"):
            stripped = stripped[:-1]
        if "*" in stripped:
            reasons.append(
                f"{pattern!r}: '*' is a wildcard only at the start, the end, or "
                "both ('demo*', '*demo', '*demo*'). A '*' anywhere else is matched "
                "LITERALLY, so this rule would grant nothing - it reads like a "
                "wildcard and is not one."
            )
        if not body.replace("*", ""):
            # "*" or "!*" - a bare wildcard is legal as a permission, but "!*"
            # prohibits everything and is therefore prohibition-only.
            if pattern.startswith("!"):
                reasons.append(
                    f"{pattern!r}: prohibits every group; a rule cannot consist of "
                    "prohibition only (MT5's own example: '!demo*' is not valid, "
                    "'!demo*,real*' is)"
                )

    if patterns and all(p.startswith("!") for p in patterns):
        reasons.append(
            "the scope consists only of prohibitions "
            f"({patterns}); MT5 requires at least one permission, e.g. "
            "'!demo*,real*'. As written this manager could service nothing."
        )

    if reasons:
        raise InvalidGroupScopeError(reasons)
    return patterns


def scope_matches(scope: Optional[Iterable[Any]], group_name: str) -> bool:
    """Does this scope include `group_name`? Delegates to the ONE matcher.

    `ManagerAccount.in_group_scope` is the implementation M15 pinned against the
    guide's `"!managers*,*"` example; calling anything else here would create a
    second opinion about MT5's scope semantics, and the two would eventually
    disagree.
    """
    for pattern in from_wire(scope):
        negate = pattern.startswith("!")
        bare = pattern[1:] if negate else pattern
        if _mask_matches(bare, group_name):
            return not negate
    return False
