"""The ONE group-type rule and MT5's password rule (identity plane, step 2).

The group-type cases are the Administrator guide's OWN examples, verbatim from
Groups/Group-Types.md - including the two where the old prefix-based,
case-insensitive derivation disagreed with MT5 ("Demoforex" and
"real\\demoforex-USD").
"""
from __future__ import annotations

import pytest

from core.domains.accounts.enums import AccountType
from core.domains.identity.group_type import (
    GROUP_NAME_MAX_LENGTH,
    InvalidGroupNameError,
    derive_group_type,
    derive_group_type_optional,
    is_manager_group,
    validate_group_name,
)
from core.domains.identity.password_policy import (
    PASSWORD_MAX_LENGTH,
    PASSWORD_MIN_LENGTH_FLOOR,
    PasswordPolicy,
    PasswordPolicyError,
    hash_password,
    verify_password,
)


# ---------------------------------------------------------------------------
# derive_group_type - the guide's examples
# ---------------------------------------------------------------------------

def test_guide_examples_demo():
    # "the 'demo\forex', 'demo-USD' and 'real\demoforex-USD' groups are demo"
    assert derive_group_type("demo\\forex") is AccountType.DEMO
    assert derive_group_type("demo-USD") is AccountType.DEMO
    assert derive_group_type("real\\demoforex-USD") is AccountType.DEMO
    # "and the 'Demoforex' 'fx-USD' groups are not"
    assert derive_group_type("Demoforex") is not AccountType.DEMO
    assert derive_group_type("fx-USD") is not AccountType.DEMO


def test_guide_examples_manager():
    # "For example, 'manager_CFD' or 'manager_real'."
    assert derive_group_type("manager_CFD") is AccountType.MANAGER
    assert derive_group_type("manager_real") is AccountType.MANAGER
    assert derive_group_type("managers\\dealers") is AccountType.MANAGER
    assert derive_group_type("managers\\administrators") is AccountType.MANAGER
    assert derive_group_type("managers\\API") is AccountType.MANAGER


def test_guide_examples_contest_coverage_preliminary():
    assert derive_group_type("contest_forex") is AccountType.CONTEST
    assert derive_group_type("contest\\USD") is AccountType.CONTEST
    assert derive_group_type("coverage\\forex") is AccountType.COVERAGE
    assert derive_group_type("coverage\\house") is AccountType.COVERAGE
    assert derive_group_type("preliminary") is AccountType.PRELIMINARY
    # the preliminary group is the ONE group with that exact name; a subgroup
    # merely containing the word is not it
    assert derive_group_type("real\\preliminary-vip") is AccountType.REAL


def test_real_is_the_fallback():
    # "If a group doesn't fall into any category by its name ... the system
    # considers it a real one."
    assert derive_group_type("real\\real") is AccountType.REAL
    assert derive_group_type("real\\real-SF") is AccountType.REAL
    assert derive_group_type("fx-USD") is AccountType.REAL
    assert derive_group_type("anything_at_all") is AccountType.REAL


def test_case_sensitivity_is_mt5s():
    # case-SENSITIVE per the guide: capital-D "Demoforex" is not a demo group
    assert derive_group_type("Demoforex") is AccountType.REAL
    assert derive_group_type("DEMO\\X") is AccountType.REAL
    assert derive_group_type("Managers\\dealers") is AccountType.REAL


def test_documented_ambiguity_order():
    # The guide forbids mixing markers ("Do not use indications of different
    # group types within the name, for example managers\demo"); our documented
    # order resolves toward the MORE restricted type.
    assert derive_group_type("managers\\demo") is AccountType.MANAGER
    assert derive_group_type("demo\\contest-2026") is AccountType.CONTEST


def test_empty_name_refuses_and_optional_variant_tolerates():
    with pytest.raises(InvalidGroupNameError):
        derive_group_type("")
    assert derive_group_type_optional("") is None
    assert derive_group_type_optional(None) is None
    assert derive_group_type_optional("demo\\x") is AccountType.DEMO


def test_is_manager_group():
    assert is_manager_group("managers\\dealers")
    assert not is_manager_group("real\\real")
    assert not is_manager_group("Managers\\x")  # case-sensitive, like everything else


def test_legacy_entry_point_delegates():
    """infrastructure.mt5.enums.account_type_from_group_path now delegates to
    the canonical rule - one function, two names, no drift."""
    from infrastructure.mt5.enums import account_type_from_group_path

    assert account_type_from_group_path("") is None
    assert account_type_from_group_path("real\\demoforex-USD") is AccountType.DEMO
    assert account_type_from_group_path("Demoforex") is AccountType.REAL
    assert account_type_from_group_path("demo\\Standard") is AccountType.DEMO
    assert account_type_from_group_path("managers\\dealers") is AccountType.MANAGER
    assert account_type_from_group_path("preliminary") is AccountType.PRELIMINARY


# ---------------------------------------------------------------------------
# validate_group_name
# ---------------------------------------------------------------------------

def test_validate_group_name_accepts_mt5_shapes():
    for name in ("real\\real", "demo\\Standard", "preliminary", "managers\\API", "coverage\\house"):
        assert validate_group_name(name) == name
    assert validate_group_name("  real\\real  ") == "real\\real"


def test_validate_group_name_refuses_every_bad_shape_with_all_reasons():
    with pytest.raises(InvalidGroupNameError):
        validate_group_name("")
    with pytest.raises(InvalidGroupNameError):
        validate_group_name("   ")
    with pytest.raises(InvalidGroupNameError, match="longer than"):
        validate_group_name("a" * (GROUP_NAME_MAX_LENGTH + 1))
    with pytest.raises(InvalidGroupNameError, match="separator"):
        validate_group_name("real/real")
    with pytest.raises(InvalidGroupNameError, match="start or end"):
        validate_group_name("\\real")
    with pytest.raises(InvalidGroupNameError, match="start or end"):
        validate_group_name("real\\")
    with pytest.raises(InvalidGroupNameError, match="empty path segment"):
        validate_group_name("real\\\\vip")


# ---------------------------------------------------------------------------
# password policy
# ---------------------------------------------------------------------------

GOOD = "1Ar#pqkj"  # the guide's own example


def test_guide_example_passes():
    assert PasswordPolicy().validate(GOOD) == GOOD


def test_four_character_classes_are_all_required():
    for bad, missing in (
        ("ar#pqkjj", "uppercase"),
        ("1AR#PQKJ", "lowercase"),
        ("1Arupqkj", "symbol"),
        ("lAr#pqkj", "digit"),
    ):
        with pytest.raises(PasswordPolicyError) as exc:
            PasswordPolicy().validate(bad)
        assert any(missing in r for r in exc.value.reasons), (bad, exc.value.reasons)


def test_bounds_come_from_the_group_with_the_platform_floor():
    policy = PasswordPolicy.for_group(12)
    assert policy.min_length == 12
    with pytest.raises(PasswordPolicyError) as exc:
        policy.validate(GOOD)  # 8 chars < 12
    assert any("minimum of 12" in r for r in exc.value.reasons)

    # a group cannot go below the floor of 8 or above the max of 16
    assert PasswordPolicy.for_group(4).min_length == PASSWORD_MIN_LENGTH_FLOOR
    assert PasswordPolicy.for_group(64).min_length == PASSWORD_MAX_LENGTH
    assert PasswordPolicy.for_group(None).min_length == PASSWORD_MIN_LENGTH_FLOOR

    with pytest.raises(PasswordPolicyError) as exc:
        PasswordPolicy().validate("1A#" + "x" * 20)
    assert any("maximum of 16" in r for r in exc.value.reasons)


def test_every_violation_is_reported_at_once():
    with pytest.raises(PasswordPolicyError) as exc:
        PasswordPolicy().validate("abc")
    reasons = " ".join(exc.value.reasons)
    assert "minimum" in reasons and "uppercase" in reasons and "digit" in reasons and "symbol" in reasons


def test_generate_satisfies_the_policy_it_is_given():
    for min_length in (8, 10, 12, 16):
        policy = PasswordPolicy.for_group(min_length)
        for _ in range(40):
            pw = policy.generate()
            assert min_length <= len(pw) <= PASSWORD_MAX_LENGTH
            assert not policy.violations(pw), pw


def test_hash_and_verify_round_trip_with_argon2():
    from infrastructure.security.password_hasher import Argon2PasswordHasher

    hasher = Argon2PasswordHasher(time_cost=1, memory_cost=8192, parallelism=1)
    stored = hash_password(GOOD, hasher)
    assert stored != GOOD and stored.startswith("$argon2")
    assert verify_password(GOOD, stored, hasher) is True
    assert verify_password("wrong", stored, hasher) is False
    # an EMPTY stored hash is a refusal, not a match (M6's fail-closed rule)
    assert verify_password(GOOD, "", hasher) is False
    # a corrupt stored hash fails closed instead of raising a 500
    assert verify_password(GOOD, "PLAINTEXT-REPLACE-ME:whatever", hasher) is False
