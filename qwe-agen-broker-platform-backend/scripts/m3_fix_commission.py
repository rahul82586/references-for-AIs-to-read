"""
Step M3 part 5 - commission calculation, aligned to MT5's real schema.

THREE DEFECTS

1. THE DISCRIMINATOR NEVER MATCHED. `calculate_commission` compared `rule.type` against
   the strings "per_lot", "per_deal" and "percent". But `CommissionType` values are
   "deal", "volume" and "percent". So DEAL and VOLUME rules fell through to
   `else: commission = Decimal('0')` and every commission except a percent one came back
   as ZERO. A broker charging nothing is not a rounding error.

2. `return` INSIDE THE LOOP meant only the first matching rule was ever applied. MT5
   stacks commission rules: the live export's real\\real group has THREE Commissions
   entries (Forex, and two others) with different Path masks, and a deal can match more
   than one. Summing is the correct behaviour.

3. `CommissionRule` had no `tiers` field at all, so the tiered commission MT5 actually
   uses could not be represented. The live export's Forex commission is
   `Value 3.50000000` over `RangeFrom 0 / RangeTo 1000` - a volume-banded rate. The test
   suite constructed `CommissionRule(tiers=[...])` and got a TypeError.

MT5's ConfigGroupCommission fields, from the live export:
    Name, Description, Path, Mode, RangeMode, ChargeMode, TurnoverCurrency,
    EntryMode, ActionMode, ProfitMode, ReasonMode, Tiers[]
and each Tier:
    Mode, Type, Value, Minimal, Maximal, RangeFrom, RangeTo, Currency

`ChargeMode` selects money / pips / percent; `Type` on the tier selects per-deal vs
per-lot; `RangeFrom`/`RangeTo` band it by volume; `Minimal`/`Maximal` cap it. We model
those and keep the rest in the codec's quarantine.
"""

from __future__ import annotations

import pathlib
import sys

ROOT = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else pathlib.Path.cwd()
if not (ROOT / "core" / "domains" / "accounts" / "value_objects.py").is_file():
    raise SystemExit(f"not a broker-platform root: {ROOT}")


def load(rel: str) -> str:
    with open(ROOT / rel, encoding="utf-8", newline="") as fh:
        return fh.read()


def save(rel: str, text: str, crlf: bool) -> None:
    norm = text.replace("\r\n", "\n")
    with open(ROOT / rel, "w", encoding="utf-8", newline="") as fh:
        fh.write(norm.replace("\n", "\r\n") if crlf else norm)


def sub(rel: str, old: str, new: str, why: str, *, required: bool = True) -> None:
    text = load(rel)
    crlf = "\r\n" in text
    work = text.replace("\r\n", "\n")
    if old not in work:
        if required:
            raise SystemExit(f"[FAIL] {rel}: pattern not found ({why}):\n{old[:240]!r}")
        print(f"  skip {rel}: {why}")
        return
    save(rel, work.replace(old, new, 1), crlf)
    print(f"  ok  {rel}: {why}")


# ---------------------------------------------------------------------------
# 1. CommissionTier: MT5's real fields, with the old names kept as aliases
# ---------------------------------------------------------------------------

sub(
    "core/domains/accounts/value_objects.py",
    '''@dataclass
class CommissionTier:
    """Volume-based commission tier."""
    volume_min: Decimal = field(default_factory=lambda: Decimal('0'))
    volume_max: Decimal = field(default_factory=lambda: Decimal('0'))
    rate: Decimal = field(default_factory=lambda: Decimal('0'))''',
    '''@dataclass
class CommissionTier:
    """One volume band of an MT5 commission (MT5 ConfigGroupCommissionTier).

    MT5 fields: Mode, Type, Value, Minimal, Maximal, RangeFrom, RangeTo, Currency.
    ``RangeFrom``/``RangeTo`` band the tier by volume; ``Value`` is the rate;
    ``Minimal``/``Maximal`` cap the result. The live export's Forex commission is
    Value 3.5 over RangeFrom 0 / RangeTo 1000.
    """

    #: MT5 RangeFrom / RangeTo - the volume band this tier applies to.
    volume_min: Decimal = field(default_factory=lambda: Decimal('0'))
    volume_max: Decimal = field(default_factory=lambda: Decimal('0'))
    #: MT5 Value - the rate. Money per lot, pips, or percent, per CommissionType.
    rate: Decimal = field(default_factory=lambda: Decimal('0'))
    #: MT5 Minimal / Maximal - caps applied to this tier's result.
    min_value: Decimal = field(default_factory=lambda: Decimal('0'))
    max_value: Optional[Decimal] = None
    #: MT5 Type on the tier, and Currency for a money-denominated rate.
    tier_type: int = 0
    currency: str = ""

    def applies_to(self, volume: Decimal) -> bool:
        """Whether a volume falls in this band. An unbounded max matches everything."""
        if volume < self.volume_min:
            return False
        if self.volume_max and self.volume_max > 0:
            return volume <= self.volume_max
        return True''',
    "CommissionTier gains MT5's Minimal/Maximal/Type/Currency and a band test",
)

sub(
    "core/domains/accounts/value_objects.py",
    '''@dataclass
class CommissionRule:
    """Commission configuration."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    symbol_pattern: str = "*"
    type: CommissionType = CommissionType.DEAL
    value: Decimal = field(default_factory=lambda: Decimal('0'))
    currency: str = "USD"
    percent: Decimal = field(default_factory=lambda: Decimal('0'))
    min_value: Decimal = field(default_factory=lambda: Decimal('0'))
    max_value: Optional[Decimal] = None''',
    '''@dataclass
class CommissionRule:
    """One MT5 commission entry (ConfigGroupCommission).

    A group may hold several of these with different Path masks, and a deal can match
    more than one - MT5 stacks them, so Group.calculate_commission sums every match
    rather than returning the first.
    """

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    #: MT5 Path - the symbol mask, e.g. "FX\\\\*".
    symbol_pattern: str = "*"
    type: CommissionType = CommissionType.DEAL
    #: MT5 Value on a rule with no tiers.
    value: Decimal = field(default_factory=lambda: Decimal('0'))
    currency: str = "USD"
    percent: Decimal = field(default_factory=lambda: Decimal('0'))
    min_value: Decimal = field(default_factory=lambda: Decimal('0'))
    max_value: Optional[Decimal] = None
    #: MT5 Tiers - volume-banded rates. When present these take precedence over `value`.
    tiers: List["CommissionTier"] = field(default_factory=list)
    #: MT5 ChargeMode / EntryMode / ActionMode / ProfitMode / ReasonMode. Modelled as
    #: ints because their meanings are SDK enum values we have not mapped yet; keeping
    #: them means an imported commission can be re-exported unchanged.
    charge_mode: int = 0
    entry_mode: int = 0
    action_mode: int = 0
    profit_mode: int = 0
    reason_mode: int = 127''',
    "CommissionRule gains tiers and MT5's mode fields",
)

# CommissionTier is declared after CommissionRule in this module, so the new
# `tiers: List["CommissionTier"]` is a forward reference. Resolve it now that both exist.
sub(
    "core/domains/accounts/value_objects.py",
    """@dataclass
class SpreadProfile:""",
    """# CommissionRule references CommissionTier, which is declared further down this module.
# Resolving the forward reference here rather than moving the class keeps the file's
# existing ordering (and any diff against it) intact.
CommissionRule.__dataclass_fields__["tiers"].type = List[CommissionTier]

@dataclass
class SpreadProfile:""",
    "CommissionRule.tiers forward reference resolved",
    required=False,
)

# ---------------------------------------------------------------------------
# 2. calculate_commission: match the real discriminator, sum every rule, use tiers
# ---------------------------------------------------------------------------

sub(
    "core/domains/accounts/group.py",
    '''    def calculate_commission(
        self,
        symbol: str,
        volume: Decimal,
        deal_value: Decimal
    ) -> Decimal:
        """Calculate commission for a deal."""
        for rule in self.commissions:
            if not self._matches_symbol_pattern(symbol, rule.symbol_pattern):
                continue
            
            if rule.type == "per_lot":
                commission = volume * rule.value
            elif rule.type == "per_deal":
                commission = rule.value + (deal_value * rule.percent / Decimal('100.0'))
            elif rule.type == "percent":
                commission = deal_value * rule.percent / Decimal('100.0')
            else:
                commission = Decimal('0')
            
            commission = max(commission, rule.min_value)
            if rule.max_value is not None:
                commission = min(commission, rule.max_value)
            
            return commission
        
        return Decimal('0')''',
    '''    def calculate_commission(
        self,
        symbol: str,
        volume: Decimal,
        deal_value: Decimal,
    ) -> Decimal:
        """Total commission for a deal: the SUM of every matching rule.

        Three defects fixed here:

        * The discriminator compared against "per_lot"/"per_deal"/"percent" while
          CommissionType's values are "deal"/"volume"/"percent", so DEAL and VOLUME rules
          fell through to zero. A broker charging no commission is not a rounding error.
        * `return` inside the loop applied only the FIRST matching rule. MT5 stacks them:
          the live export's real\\\\real group has three Commissions with different Path
          masks, and a deal can match more than one.
        * Tiered commissions could not be represented at all.

        Comparison is against the enum's VALUE, and a rule whose type is given as a bare
        string is normalised first, so both `CommissionType.VOLUME` and `"volume"` work.
        """
        total = Decimal('0')
        for rule in self.commissions:
            if not self._matches_symbol_pattern(symbol, rule.symbol_pattern):
                continue
            total += self._commission_for_rule(rule, volume, deal_value)
        return total

    def _commission_for_rule(
        self, rule: "CommissionRule", volume: Decimal, deal_value: Decimal
    ) -> Decimal:
        """One rule's commission, tiered if it has tiers, plus its min/max caps."""
        rule_type = rule.type.value if hasattr(rule.type, "value") else str(rule.type)

        if rule.tiers:
            # Volume-banded. The first band the volume falls in applies; MT5's RangeFrom
            # / RangeTo are inclusive at the low end.
            rate = None
            tier_min = Decimal('0')
            tier_max = None
            for tier in rule.tiers:
                if tier.applies_to(volume):
                    rate = tier.rate
                    tier_min = tier.min_value
                    tier_max = tier.max_value
                    break
            if rate is None:
                return Decimal('0')
            commission = self._apply_rate(rule_type, rate, rule.percent, volume, deal_value)
            commission = max(commission, tier_min)
            if tier_max is not None and tier_max > 0:
                commission = min(commission, tier_max)
        else:
            commission = self._apply_rate(
                rule_type, rule.value, rule.percent, volume, deal_value
            )

        commission = max(commission, rule.min_value)
        if rule.max_value is not None:
            commission = min(commission, rule.max_value)
        return commission

    @staticmethod
    def _apply_rate(
        rule_type: str,
        rate: Decimal,
        percent: Decimal,
        volume: Decimal,
        deal_value: Decimal,
    ) -> Decimal:
        """Apply a rate according to CommissionType.

            VOLUME   per lot            -> volume * rate
            DEAL     flat per deal      -> rate (+ percent of deal value if configured)
            PERCENT  of the deal value  -> deal_value * percent / 100
        """
        if rule_type == CommissionType.VOLUME.value:
            return volume * rate
        if rule_type == CommissionType.DEAL.value:
            result = rate
            if percent:
                result += deal_value * percent / Decimal('100.0')
            return result
        if rule_type == CommissionType.PERCENT.value:
            basis = percent if percent else rate
            return deal_value * basis / Decimal('100.0')
        raise ValueError(
            f"unknown CommissionType {rule_type!r}; expected one of "
            f"{[m.value for m in CommissionType]}"
        )''',
    "calculate_commission sums every matching rule, matches the real enum values, and honours tiers",
)

# Group needs CommissionType imported for the value comparisons.
text = load("core/domains/accounts/group.py")
work = text.replace("\r\n", "\n")
# Check only the import line, not the whole file: _apply_rate mentions CommissionType,
# so a whole-file check passes before the import is ever added.
IMPORT_OLD = "from .enums import AccountType, TradeFlags, NewsMode"
IMPORT_NEW = "from .enums import AccountType, CommissionType, TradeFlags, NewsMode"
if IMPORT_OLD in work:
    work = work.replace(IMPORT_OLD, IMPORT_NEW, 1)
    save("core/domains/accounts/group.py", work, crlf="\r\n" in text)
    print("  ok  core/domains/accounts/group.py: CommissionType imported")
elif IMPORT_NEW in work:
    print("  ok  core/domains/accounts/group.py: CommissionType already imported")
else:
    raise SystemExit("[FAIL] group.py: the .enums import line was not recognised")
