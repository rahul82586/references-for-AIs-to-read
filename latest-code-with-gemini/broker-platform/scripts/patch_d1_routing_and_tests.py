"""D1 part 2: the routing context must DERIVE margin_level, never read the column.

`scripts/patch_d1_d2_margin_level.py` fixed the write path (record_deal now calls
recompute_margin_level) and the SQL read path (db_to_account derives). That is
not enough on its own: routing is a DECISION path, and a decision must not depend
on some earlier writer having remembered to refresh a cached field.

The in-memory repositories used by the test harness hand back the object they were
given, whose `margin_level` is the dataclass default Decimal('0') until something
recomputes it. So on a first order the router would still see 0.

Worse, 0 is the dangerous value: `RoutingRequestContext.margin_level` is
Optional[Decimal] and M8's honesty rule is "missing context (None) => the condition
does not match". A stale Decimal('0') is NOT missing, so `_compare` really fires
against zero and a MARGIN_LEVEL rule diverts or rejects real flow.

Fix: derive it from equity / margin_used through the single source of truth, the
same function Account.recompute_margin_level and the read mapper use. None stays
None, so the missing-context guard still works when the account is unknown.

Also updates the two existing tests whose contracts this changes:
  * test_api.py built GetAccountInfoQuery(login_id=...) - the field is now
    account_login, matching the routers and the sibling GetPositionsQuery. This
    mismatch is exactly why the handler was unreachable and nobody noticed: the
    test spoke the handler's vocabulary, the routers spoke another.
  * test_m2_config_plane.py asserted a hand-assigned margin_level round-trips
    through the column. margin_level is DERIVED state, unlike the five so_*
    fields that test exists to protect (those are the stop-out machine's real
    memory). The test's own numbers - equity 550, margin 2000 - already give
    27.5, so it now sets those and asserts the derivation survives, plus that a
    stale column is ignored.
"""
import ast
import io
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
sys.path.insert(0, ROOT)

applied = []


def patch(path, pairs, replace_all=False):
    src = io.open(path, encoding="utf-8", newline="").read()
    nl = "\r\n" if "\r\n" in src else "\n"
    changed = False
    for old, new in pairs:
        if nl == "\r\n":
            old = old.replace("\n", "\r\n")
            new = new.replace("\n", "\r\n")
        n = src.count(old)
        if n == 0:
            if src.count(new):
                print(f"  skip (already patched): {path}")
                continue
            raise AssertionError(f"{path}: anchor not found: {old[:90]!r}")
        if not replace_all and n != 1:
            raise AssertionError(f"{path}: anchor appears {n}x: {old[:90]!r}")
        src = src.replace(old, new) if replace_all else src.replace(old, new, 1)
        changed = True
    if changed:
        ast.parse(src.replace("\r\n", "\n"))
        io.open(path, "w", encoding="utf-8", newline="").write(src)
        applied.append(path)


# ------------------------------------------------------- the routing context
patch("core/domains/execution/router.py", [
    (
        "from core.domains.execution.models import (\n",
        "from core.domains.market_data.margin import margin_level as compute_margin_level\n"
        "from core.domains.execution.models import (\n",
    ),
    (
        '        def _amount(attr):\n'
        '            value = getattr(account, attr, None)\n'
        '            return getattr(value, "amount", None)\n',
        '        def _amount(attr):\n'
        '            value = getattr(account, attr, None)\n'
        '            return getattr(value, "amount", None)\n'
        '\n'
        '        def _margin_level():\n'
        '            # D1: DERIVED, never read from account.margin_level. That field is a\n'
        '            # persisted column refreshed only by whichever write path remembered\n'
        '            # to call recompute_margin_level(); a routing decision cannot depend\n'
        '            # on that. A stale Decimal(\'0\') is worse than None here - None makes\n'
        '            # M8\'s missing-context guard skip the condition, while 0 makes a\n'
        '            # MARGIN_LEVEL comparison really fire against zero.\n'
        '            equity = _amount("equity")\n'
        '            used = _amount("margin_used")\n'
        '            if equity is None or used is None:\n'
        '                return None\n'
        '            return compute_margin_level(equity, used)\n',
    ),
    (
        '            margin_level=getattr(account, "margin_level", None),\n',
        '            margin_level=_margin_level(),\n',
    ),
])

# ------------------------------------------------- test_api.py: field rename
patch("tests/unit/api/test_api.py", [
    (
        '    account_mock.margin_free.amount = Decimal(\'10000.00\')\n',
        '    account_mock.margin_free.amount = Decimal(\'10000.00\')\n'
        '    account_mock.credit.amount = Decimal(\'0.00\')\n'
        '    account_mock.effective_leverage.return_value = 100\n',
    ),
    (
        'GetAccountInfoQuery(login_id="10001")',
        'GetAccountInfoQuery(account_login="10001")',
    ),
    (
        '    assert result["margin_level"] == Decimal(\'2100.00\')\n',
        '    assert result["margin_level"] == Decimal(\'2100.00\')\n'
        '    # D2: the manager UserGet schema needs these; they had no source before.\n'
        '    assert result["credit"] == Decimal(\'0.00\')\n'
        '    assert result["leverage"] == 100\n',
    ),
])

# ------------------------------- test_m2: margin_level is derived, not stored
patch("tests/unit/persistence/test_m2_config_plane.py", [
    (
        '    account.so_activation = SOActivation.STOP_OUT\n'
        '    account.so_level = Decimal("27.5")\n'
        '    account.so_equity = Money(Decimal("550"), account.currency)\n'
        '    account.so_margin = Money(Decimal("2000"), account.currency)\n'
        '    account.margin_level = Decimal("27.5")\n'
        '    account.color_tag = "red"\n'
        '    await providers["account_repo"].save(account)\n'
        '\n'
        '    reloaded = await providers["account_repo"].find_by_login(str(account.login))\n'
        '    assert reloaded.so_activation is SOActivation.STOP_OUT\n'
        '    assert reloaded.so_level == Decimal("27.5")\n'
        '    assert reloaded.so_equity.amount == Decimal("550")\n'
        '    assert reloaded.margin_level == Decimal("27.5")\n'
        '    assert reloaded.color_tag == "red"\n',

        '    account.so_activation = SOActivation.STOP_OUT\n'
        '    account.so_level = Decimal("27.5")\n'
        '    account.so_equity = Money(Decimal("550"), account.currency)\n'
        '    account.so_margin = Money(Decimal("2000"), account.currency)\n'
        '    # D1: margin_level is DERIVED state, not stored state - unlike the five\n'
        '    # so_* fields this test exists to protect, which are the stop-out machine\'s\n'
        '    # real memory. 550 / 2000 * 100 = 27.5, so setting the inputs and asserting\n'
        '    # the output pins the derivation instead of the column.\n'
        '    account.equity = Money(Decimal("550"), account.currency)\n'
        '    account.margin_used = Money(Decimal("2000"), account.currency)\n'
        '    account.margin_level = Decimal("27.5")\n'
        '    account.color_tag = "red"\n'
        '    await providers["account_repo"].save(account)\n'
        '\n'
        '    reloaded = await providers["account_repo"].find_by_login(str(account.login))\n'
        '    assert reloaded.so_activation is SOActivation.STOP_OUT\n'
        '    assert reloaded.so_level == Decimal("27.5")\n'
        '    assert reloaded.so_equity.amount == Decimal("550")\n'
        '    assert reloaded.margin_level == Decimal("27.5")\n'
        '    assert reloaded.color_tag == "red"\n'
        '\n'
        '\n'
        '@pytest.mark.asyncio\n'
        'async def test_a_stale_margin_level_column_is_never_served(providers):\n'
        '    """D1: the column is written for external SQL consumers but the domain\n'
        '    object never trusts it. Before the fix a defaulted 0 was served to clients\n'
        '    and fed to the routing engine as a real comparison value.\n'
        '    """\n'
        '    await _seed(providers)\n'
        '    account = (await providers["account_repo"].find_all())[0]\n'
        '    account.equity = Money(Decimal("9999"), account.currency)\n'
        '    account.margin_used = Money(Decimal("107.978"), account.currency)\n'
        '    account.margin_level = Decimal("0")  # deliberately stale / wrong\n'
        '    await providers["account_repo"].save(account)\n'
        '\n'
        '    reloaded = await providers["account_repo"].find_by_login(str(account.login))\n'
        '    assert reloaded.margin_level == (Decimal("9999") / Decimal("107.978")) * Decimal("100")\n'
        '    assert reloaded.margin_level != Decimal("0")\n',
    ),
])

print(f"applied to {len(set(applied))} file(s):")
for f in sorted(set(applied)):
    print("  ", f)
