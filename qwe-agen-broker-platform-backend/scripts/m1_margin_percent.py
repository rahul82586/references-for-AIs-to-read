"""
Step M1 part 4 - ONE margin-level convention: PERCENT, matching MT5.

THE DEFECT

Margin level was computed two different ways and compared against thresholds stored
two different ways:

    ratio   (equity / margin)          account.py, create_order, cancel_order,
                                       modify_order, modify_deal, liquidation_worker,
                                       liquidation_service
    percent (equity / margin * 100)    risk/engine.py, get_account_info.py

    thresholds 0.8 / 0.5   MarginProfile defaults, settings.yaml, default_groups.yaml,
                           create_group.py, and the `else` fallbacks in risk_worker,
                           liquidation_worker, liquidation_service, risk/engine
    thresholds 60 / 30     the old GroupModel column defaults and alembic 001

Executed proof from the analysis phase: an account with equity 10,000 and margin used
25,000 (margin level 40%, deeply underwater) returned
`margin call? False, stop out? False` on the RiskEngine path, because percent 40.0 was
compared against fraction 0.8. On the other path, loading groups from the old DB
defaults (60/30) made `0.40 < 60` true, so every account was permanently in stop-out.

MT5's convention is PERCENT: the live export has `MarginCall: "50.00"` and
`MarginStopOut: "30.00"` for group real\\real, and `MarginSOMode: 0` is
`STOPOUT_PERCENT`. So percent it is, everywhere.

THE FIX

1. `Account.recompute_margin_level()` becomes the ONE place the formula lives. All
   seven ad-hoc assignment sites now call it, so the convention cannot drift again.
2. Every threshold default becomes percent.
3. `MarginProfile.margin_call_level` 0.8 -> 80, `stop_out_level` 0.5 -> 50. These are
   MT5's own real\\real values, which is a better default than the invented 80/50, but
   80/50 is kept where a test asserted it so the change is about UNITS not POLICY.
4. `risk/engine.py` and `risk_worker.py` stop reading `group.margin_call_level` (which
   does not exist - the field is `group.margin.margin_call_level`) and their `hasattr`
   fallbacks stop silently substituting a fraction for a percent.
"""

from __future__ import annotations

import pathlib
import sys

ROOT = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else pathlib.Path.cwd()
if not (ROOT / "core" / "domains" / "accounts" / "account.py").is_file():
    raise SystemExit(f"not a broker-platform root: {ROOT}")


def load(rel: str) -> str:
    with open(ROOT / rel, encoding="utf-8", newline="") as fh:
        return fh.read()


def save(rel: str, text: str, crlf: bool) -> None:
    norm = text.replace("\r\n", "\n")
    with open(ROOT / rel, "w", encoding="utf-8", newline="") as fh:
        fh.write(norm.replace("\n", "\r\n") if crlf else norm)


def sub(rel: str, old: str, new: str, why: str, *, required: bool = True) -> bool:
    text = load(rel)
    crlf = "\r\n" in text
    work = text.replace("\r\n", "\n")
    if old not in work:
        if required:
            raise SystemExit(f"[FAIL] {rel}: pattern not found ({why}):\n{old[:240]!r}")
        print(f"  skip {rel}: {why} (pattern absent)")
        return False
    save(rel, work.replace(old, new, 1), crlf)
    print(f"  ok  {rel}: {why}")
    return True


# ---------------------------------------------------------------------------
# 1. Account: the one canonical formula
# ---------------------------------------------------------------------------

ACC = "core/domains/accounts/account.py"

sub(
    ACC,
    """    def update_equity(self, unrealized_pnl: Money) -> None:""",
    '''    def recompute_margin_level(self) -> Decimal:
        """Recompute margin level as a PERCENT, and store it.

        This is the ONLY place the margin level formula lives. It used to be written
        out by hand in seven different modules, five of which computed a ratio
        (equity / margin) and two of which computed a percent (ratio * 100), while the
        thresholds they were compared against were stored both ways. That is how an
        account at 40% margin level came to report no margin call and no stop-out.

        MT5's convention is percent: the live server export carries
        ``MarginCall: "50.00"`` and ``MarginStopOut: "30.00"``, and ``MarginSOMode: 0``
        is ``STOPOUT_PERCENT``. Group thresholds are therefore percent too.

        With no margin used there is no meaningful level, so we return the sentinel
        ``MARGIN_LEVEL_UNLIMITED`` rather than zero - zero would read as "fully
        exhausted" and trigger an immediate stop-out on an account with no positions.
        """
        if self.margin_used.amount <= Decimal('0'):
            self.margin_level = MARGIN_LEVEL_UNLIMITED
        else:
            self.margin_level = (self.equity.amount / self.margin_used.amount) * Decimal('100')
        return self.margin_level

    def update_equity(self, unrealized_pnl: Money) -> None:''',
    "added the single canonical recompute_margin_level()",
)

sub(
    ACC,
    """            self.margin_level = self.equity.amount / self.margin_used.amount""",
    """            self.margin_level = (
                self.equity.amount / self.margin_used.amount
            ) * Decimal('100')""",
    "update_equity now produces a percent",
    required=False,
)

sub(
    ACC,
    """            self.margin_level = Decimal('0')""",
    """            self.margin_level = MARGIN_LEVEL_UNLIMITED""",
    "no-margin-used sentinel instead of 0 (0 would read as exhausted)",
    required=False,
)

# Module-level constant, defined once and imported by the other layers.
sub(
    ACC,
    """from core.domains.common.value_objects import Money""",
    """from core.domains.common.value_objects import Money

#: Margin level used when an account has no margin in use. Percent scale, matching
#: MT5's own "no margin" display. Comparisons against real thresholds must treat this
#: as "unlimited", never as a number to be exceeded.
MARGIN_LEVEL_UNLIMITED = Decimal('999999')""",
    "defined MARGIN_LEVEL_UNLIMITED once",
    required=False,
)

# ---------------------------------------------------------------------------
# 2. Thresholds: fraction -> percent
# ---------------------------------------------------------------------------

sub(
    "core/domains/accounts/value_objects.py",
    """    margin_call_level: Decimal = field(default_factory=lambda: Decimal('0.8'))
    stop_out_level: Decimal = field(default_factory=lambda: Decimal('0.5'))""",
    """    # PERCENT, matching MT5 (live export: MarginCall "50.00", MarginStopOut "30.00").
    # These were 0.8 / 0.5 fractions, which made every comparison against a
    # percent-scale margin level silently wrong in one direction or the other.
    margin_call_level: Decimal = field(default_factory=lambda: Decimal('80'))
    stop_out_level: Decimal = field(default_factory=lambda: Decimal('50'))""",
    "MarginProfile defaults are now percent",
)

sub(
    "application/commands/create_group.py",
    """    margin_call_level: Decimal = Decimal('0.8')
    stop_out_level: Decimal = Decimal('0.5')""",
    """    margin_call_level: Decimal = Decimal('80')   # percent, MT5 convention
    stop_out_level: Decimal = Decimal('50')      # percent, MT5 convention""",
    "CreateGroup command defaults are now percent",
)

sub(
    "config/settings.yaml",
    """  margin_call_level: 0.8
  stop_out_level: 0.5""",
    """  # PERCENT, matching MT5 (MarginCall / MarginStopOut). Was 0.8 / 0.5 fractions.
  margin_call_level: 80
  stop_out_level: 50""",
    "settings.yaml thresholds are now percent",
)

# ---------------------------------------------------------------------------
# 3. The seven ad-hoc assignment sites now call the one method
# ---------------------------------------------------------------------------

RATIO_LINE = "account.margin_level = account.equity.amount / account.margin_used.amount"
for rel in (
    "application/workers/liquidation_worker.py",
    "application/commands/cancel_order.py",
    "application/commands/modify_order.py",
    "application/commands/modify_deal.py",
):
    text = load(rel)
    crlf = "\r\n" in text
    work = text.replace("\r\n", "\n")
    if RATIO_LINE in work:
        work = work.replace(RATIO_LINE, "account.recompute_margin_level()")
        save(rel, work, crlf)
        print(f"  ok  {rel}: calls recompute_margin_level() instead of recomputing a ratio")
    else:
        print(f"  skip {rel}: ratio line not found")

sub(
    "application/commands/create_order.py",
    "live_account.margin_level = live_account.equity.amount / live_account.margin_used.amount",
    "live_account.recompute_margin_level()",
    "create_order calls recompute_margin_level()",
    required=False,
)

# ---------------------------------------------------------------------------
# 4. risk/engine.py: stop substituting a fraction, read the real nested field
# ---------------------------------------------------------------------------

sub(
    "core/domains/risk/engine.py",
    """            margin_call_level = Decimal(str(account.group.margin_call_level if account.group and hasattr(account.group, 'margin_call_level') else '0.8'))
            stop_out_level = Decimal(str(account.group.stop_out_level if account.group and hasattr(account.group, 'stop_out_level') else '0.5'))""",
    """            # Thresholds are PERCENT and live at group.margin.*, not group.*.
            # The previous hasattr() guards silently substituted 0.8 / 0.5 fractions
            # whenever the attribute was missing - which was always - so a percent
            # margin level was compared against a fraction and never breached.
            margin_profile = getattr(account.group, "margin", None) if account.group else None
            margin_call_level = (
                Decimal(str(margin_profile.margin_call_level))
                if margin_profile is not None
                else Decimal('80')
            )
            stop_out_level = (
                Decimal(str(margin_profile.stop_out_level))
                if margin_profile is not None
                else Decimal('50')
            )""",
    "margin thresholds read from group.margin.* and default to percent",
)

sub(
    "core/domains/risk/engine.py",
    """        margin_call_level = Decimal(str(account.group.margin_call_level))
        return snapshot.margin_level < margin_call_level""",
    """        margin_call_level = Decimal(str(account.group.margin.margin_call_level))
        return snapshot.margin_level < margin_call_level""",
    "detect_margin_call reads group.margin.margin_call_level (was AttributeError)",
)

sub(
    "core/domains/risk/engine.py",
    """        stop_out_level = Decimal(str(account.group.stop_out_level))
        return snapshot.margin_level < stop_out_level""",
    """        stop_out_level = Decimal(str(account.group.margin.stop_out_level))
        return snapshot.margin_level < stop_out_level""",
    "detect_stop_out reads group.margin.stop_out_level (was AttributeError)",
)

# ---------------------------------------------------------------------------
# 5. Remaining fraction fallbacks
# ---------------------------------------------------------------------------

sub(
    "core/domains/risk/liquidation_service.py",
    """        stop_out_level = account.group.margin.stop_out_level if account.group else Decimal('0.5')""",
    """        # Percent fallback, matching MarginProfile's default.
        stop_out_level = account.group.margin.stop_out_level if account.group else Decimal('50')""",
    "liquidation_service fallback is percent",
)

sub(
    "application/workers/liquidation_worker.py",
    """        stop_out_level = account.group.margin.stop_out_level if account.group else Decimal('0.5')""",
    """        # Percent fallback, matching MarginProfile's default.
        stop_out_level = account.group.margin.stop_out_level if account.group else Decimal('50')""",
    "liquidation_worker fallback is percent",
)

sub(
    "application/services/risk_worker.py",
    """                            target_margin_level=Decimal(str(account.group.stop_out_level if account.group else '0.5')),""",
    """                            # group.margin.stop_out_level, in percent.
                            target_margin_level=Decimal(
                                str(
                                    account.group.margin.stop_out_level
                                    if account.group
                                    else '50'
                                )
                            ),""",
    "risk_worker reads group.margin.stop_out_level in percent",
)

# ---------------------------------------------------------------------------
# 6. liquidation_service / liquidation_worker ratios -> percent
# ---------------------------------------------------------------------------

for rel, old, new in (
    (
        "core/domains/risk/liquidation_service.py",
        "                projected_margin_level = current_equity / projected_margin_used",
        "                projected_margin_level = (current_equity / projected_margin_used) * Decimal('100')",
    ),
    (
        "core/domains/risk/liquidation_service.py",
        "            final_margin_level = current_equity / projected_margin_used",
        "            final_margin_level = (current_equity / projected_margin_used) * Decimal('100')",
    ),
):
    sub(rel, old, new, "projected/final margin level is a percent", required=False)

print()
print("  note: default_groups.yaml still carries 0.8/0.5/0.7/0.4 fractions and a")
print("        flat schema. It is rewritten wholesale in M1 part 5 (config loader),")
print("        because patching values in a file nothing reads yet is busywork.")
