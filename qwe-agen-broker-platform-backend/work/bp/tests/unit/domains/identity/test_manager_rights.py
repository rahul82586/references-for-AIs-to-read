"""ManagerRightsMask / UserRight - the named 128-bit mask (identity plane, step 1).

The load-bearing assertions here are the CROSS-CHECKS against the storage
layer: the mask's to_masks/from_masks must pack bits exactly like
infrastructure.persistence.account_models' rights_to_masks/masks_to_rights, or
the DB's three BigInteger columns and the domain silently disagree - the
project's signature defect class.
"""
from __future__ import annotations

import pytest

from core.domains.identity.rights import (
    DEFAULT_NEW_ACCOUNT_RIGHTS,
    MT5_USER_RIGHT_ALL,
    MT5_USER_RIGHT_DEFAULT,
    RIGHTS_COUNT,
    ManagerRightsMask,
    UnknownRightError,
    UserRight,
    get_manager_rights,
    user_right_descriptors,
)


def test_registry_loads_the_sdk_table():
    registry = get_manager_rights()
    names = {r.name for r in registry.all()}
    # spot-checks across every plane of the enum
    for expected in (
        "RIGHT_ADMIN", "RIGHT_MANAGER", "RIGHT_CFG_GROUPS", "RIGHT_ACC_MANAGER",
        "RIGHT_TRADES_DEALER", "RIGHT_QUOTES", "RIGHT_RISK_MANAGER",
        "RIGHT_ACCOUNTANT", "RIGHT_CLIENTS_KYC", "RIGHT_LAST",
    ):
        assert expected in names, expected
    # the guide's role bits are at the documented indices
    assert registry.by_name("RIGHT_ADMIN").index == 0
    assert registry.by_name("RIGHT_MANAGER").index == 1
    assert registry.by_name("RIGHT_ACCOUNTANT").index == 24
    assert registry.by_name("RIGHT_RISK_MANAGER").index == 32
    assert registry.by_name("RIGHT_TRADES_DEALER").index == 37


def test_sentinel_is_never_grantable():
    registry = get_manager_rights()
    assert registry.by_name("RIGHT_LAST").sentinel
    with pytest.raises(UnknownRightError):
        registry.resolve("RIGHT_LAST")
    with pytest.raises(UnknownRightError):
        ManagerRightsMask.from_names(["RIGHT_LAST"])
    # ...but a WIRE array carrying a 1 at 128 cannot exist (array is 128 long,
    # indices 0..127), and from_indices refuses out-of-range outright:
    with pytest.raises(UnknownRightError):
        ManagerRightsMask.from_indices([128])


def test_names_array_masks_round_trip():
    mask = ManagerRightsMask.from_names(
        ["RIGHT_MANAGER", "RIGHT_CFG_GROUPS", "RIGHT_TRADES_DEALER", "RIGHT_CLIENTS_KYC"]
    )
    assert mask.to_names() == [
        "RIGHT_MANAGER", "RIGHT_CFG_GROUPS", "RIGHT_TRADES_DEALER", "RIGHT_CLIENTS_KYC"
    ]
    array = mask.to_array()
    assert len(array) == RIGHTS_COUNT
    assert array[1] == "1" and array[16] == "1" and array[37] == "1" and array[109] == "1"
    assert sum(1 for v in array if v == "1") == 4
    assert ManagerRightsMask.from_array(array) == mask

    masks = mask.to_masks()
    assert len(masks) == 3
    for word in masks:
        assert word.bit_length() <= 63, "a mask word must fit a signed BigInteger"
    assert ManagerRightsMask.from_masks(masks) == mask


def test_mask_packing_matches_the_storage_layer_bit_for_bit():
    """The DB columns and the domain mask are ONE encoding, pinned both ways."""
    from infrastructure.persistence.account_models import masks_to_rights, rights_to_masks

    for mask in (
        ManagerRightsMask.empty(),
        ManagerRightsMask.all_rights(),
        ManagerRightsMask.from_indices([0]),
        ManagerRightsMask.from_indices([127]),
        ManagerRightsMask.from_indices(list(range(0, 128, 7))),
        ManagerRightsMask.from_names(["RIGHT_ADMIN", "RIGHT_FINTEZA_REPORTS", "RIGHT_PAYMENTS_DELETE"]),
    ):
        assert rights_to_masks(mask.to_array()) == list(mask.to_masks())
        assert masks_to_rights(list(mask.to_masks())) == mask.to_array()


def test_from_array_preserves_unnamed_wire_bits():
    """The live export's administrators have 68/69 set - indices MT5's enum
    leaves unassigned. Preservation beats naming: the array must survive."""
    array = ["0"] * RIGHTS_COUNT
    for i in (0, 68, 69, 109, 127):
        array[i] = "1"
    mask = ManagerRightsMask.from_array(array)
    assert mask.to_array() == array
    assert mask.count == 5
    assert mask.unnamed_indices() == [68, 69, 127]
    assert "RIGHT_ADMIN" in mask.to_names() and mask.has("RIGHT_ADMIN")
    assert len(mask.to_names()) == 2  # only 0 and 109 have names


def test_refusals():
    with pytest.raises(UnknownRightError):
        ManagerRightsMask.from_names(["RIGHT_NOT_A_THING"])
    with pytest.raises(UnknownRightError):
        ManagerRightsMask.from_indices([-1])
    with pytest.raises(UnknownRightError):
        ManagerRightsMask.from_array(["1"] * (RIGHTS_COUNT + 1))
    with pytest.raises(UnknownRightError):
        ManagerRightsMask.empty().has(True)  # bool is an int; refuse explicitly
    empty = ManagerRightsMask.empty()
    assert empty.count == 0
    assert empty.grant("RIGHT_ADMIN").has(0)
    assert not empty.has("RIGHT_ADMIN")          # immutable: grant returned a NEW mask
    assert empty.grant("RIGHT_ADMIN").revoke("RIGHT_ADMIN") == empty


def test_merge_and_all_rights():
    a = ManagerRightsMask.from_names(["RIGHT_MANAGER"])
    b = ManagerRightsMask.from_names(["RIGHT_CFG_GROUPS"])
    assert a.merge(b).to_names() == ["RIGHT_MANAGER", "RIGHT_CFG_GROUPS"]
    everything = ManagerRightsMask.all_rights()
    assert everything.has("RIGHT_ADMIN") and everything.has("RIGHT_PAYMENTS_DELETE")
    assert everything.to_array()[0] == "1"
    # all_rights never includes the sentinel position (index 128 does not exist
    # in a 128-long array; unassigned-but-in-range indices stay unset)
    assert everything.count == len(get_manager_rights().grantable())


# ---------------------------------------------------------------------------
# UserRight - the account's own mask
# ---------------------------------------------------------------------------

def test_user_right_values_are_mt5s():
    assert UserRight.ENABLED.value == 0x1
    assert UserRight.TRADE_DISABLED.value == 0x4
    assert UserRight.RESET_PASS.value == 0x400
    assert UserRight.TECHNICAL.value == 0x10000
    assert UserRight.EXCLUDE_REPORTS.value == 0x20000


def test_user_right_default_is_the_sdks_not_a_guess():
    """Pin USER_RIGHT_DEFAULT and USER_RIGHT_ALL to Include.md's own expressions.

    Step 5 corrected this: ACCOUNT-GROUP-CREATION-SPEC §6 asserted the creation
    default was ENABLED|PASSWORD (0x3), which was written before Include.md was
    read member by member. The SDK says

        USER_RIGHT_DEFAULT = ENABLED|PASSWORD|TRAILING|EXPERT|REPORTS

    - exactly the five boxes MT5's Limits tab shows ticked on a fresh account.
    The old value silently stripped trailing stops, Expert Advisors and daily
    reports from every account this platform created. The magic numbers below
    are computed from the SDK's member list, not retyped, so this test fails if
    either the enum or the constant drifts.
    """
    sdk_default = 0x1 | 0x2 | 0x20 | 0x40 | 0x100
    assert int(MT5_USER_RIGHT_DEFAULT) == sdk_default == 0x163
    assert MT5_USER_RIGHT_DEFAULT == (
        UserRight.ENABLED
        | UserRight.PASSWORD
        | UserRight.TRAILING
        | UserRight.EXPERT
        | UserRight.REPORTS
    )
    assert DEFAULT_NEW_ACCOUNT_RIGHTS is MT5_USER_RIGHT_DEFAULT or (
        DEFAULT_NEW_ACCOUNT_RIGHTS == MT5_USER_RIGHT_DEFAULT
    )

    # USER_RIGHT_ALL deliberately OMITS USER_RIGHT_OBSOLETE (0x80).
    sdk_all = (
        0x1 | 0x2 | 0x4 | 0x8 | 0x10 | 0x20 | 0x40 | 0x100 | 0x200 | 0x400
        | 0x800 | 0x2000 | 0x4000 | 0x8000 | 0x10000 | 0x20000
    )
    assert int(MT5_USER_RIGHT_ALL) == sdk_all == 0x3EF7F
    assert UserRight.OBSOLETE not in MT5_USER_RIGHT_ALL
    # Every named member except OBSOLETE is grantable through ALL.
    for member in UserRight:
        if member is UserRight.OBSOLETE or member.value == 0:
            continue
        assert member in MT5_USER_RIGHT_ALL, member.name


def test_user_right_flag_round_trip_and_refusal():
    flags = (UserRight.ENABLED | UserRight.PASSWORD | UserRight.EXPERT).to_flags()
    assert UserRight.from_flags(flags) == (UserRight.ENABLED | UserRight.PASSWORD | UserRight.EXPERT)
    assert UserRight.from_flags(0) is UserRight.NONE
    assert UserRight.from_flags(None) is UserRight.NONE
    with pytest.raises(ValueError):
        UserRight.from_flags(0x40000)  # a bit outside EnUsersRights: refuse, never coerce


def test_user_right_descriptors_match_the_flags():
    descriptors = {d.name: d for d in user_right_descriptors()}
    assert descriptors["USER_RIGHT_TRADE_DISABLED"].inverted is True   # UI shows "Enable trading"
    assert descriptors["USER_RIGHT_TECHNICAL"].inverted is True        # UI shows "Show to regular managers"
    assert descriptors["USER_RIGHT_ENABLED"].tab == "account"
    for member in UserRight:
        if member is UserRight.NONE:
            continue
        assert f"USER_RIGHT_{member.name}" in descriptors, member
