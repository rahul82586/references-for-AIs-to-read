"""
Step M3 part 8 - carry MT5's three symbol currencies instead of discarding two of them.

THE ROOT CAUSE OF THE CROSS-CURRENCY BUGS, already diagnosed in M1's fieldmap comment
and then left unmapped:

    # Currencies. MT5 distinguishes THREE; we model two. CurrencyProfit and
    # CurrencyMargin are the root cause of our cross-currency PnL and margin bugs:
    # the margin currency need not equal the quote currency.
    Field("CurrencyBase", "base_currency", STR),
    Field("CurrencyProfit", "", STR),        <- discarded
    Field("CurrencyMargin", "", STR),        <- discarded

MT5 keeps three distinct currencies per symbol:

    CurrencyBase    the base leg (EUR for EURUSD)
    CurrencyProfit  the currency PnL is denominated in
    CurrencyMargin  the currency the margin requirement is computed in

For a plain FX pair all three line up with base/quote, which is why the omission went
unnoticed on EURUSD. It does not line up for the majority of a real symbol list. Measured
against the 362 symbols in `Symbols TCTrader-Live.json`:

    the name-parsing heuristic returns a base currency that MATCHES MT5   109
    it returns one that is WRONG                                            60
    it cannot parse the name at all                                        193

Examples of the wrong ones: AUS200.spot parses to ("AUS", "200") where MT5 says
CurrencyBase=USD; EU50.spot parses to ("EU5", "0.S") where MT5 says USD/EUR; BRENT.spot
parses to ("BRE", "NT."). Examples of the unparseable ones: BUND (EUR/EUR), MC (EUR/EUR),
EWT, GRUB, ILMN - single US equities and bonds whose names are not currency pairs at all.

Two bugs follow directly:

1. `Symbol.__post_init__` never ran its parser, because `base_currency` and
   `quote_currency` default to `"USD"` rather than `""`, so `if not self.base_currency`
   was always False. Every symbol created without explicit currencies silently became
   USD/USD - including EURJPY, which is what made the cross-currency PnL tests fail.
   A default that defeats the fallback it guards is worse than no default.

2. Even with the parser running, deriving currencies from a NAME is a heuristic that is
   wrong for 253 of 362 real symbols. MT5 tells us the answer directly. The name parser
   is kept only as a last resort for hand-written configs that omit currencies, and the
   imported path now uses MT5's own values.

The wire format is unaffected: these three fields were already in the symbol field table
and already round-trip through the codec's quarantine, so mapping them to real columns
does not change a single byte of the export. Losslessness is preserved and the 362/362
round-trip proof still holds.
"""

from __future__ import annotations

import pathlib
import sys

ROOT = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else pathlib.Path.cwd()
if not (ROOT / "core").is_dir():
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
            raise SystemExit(f"[FAIL] {rel}: pattern not found ({why}):\n{old[:300]!r}")
        print(f"  skip {rel}: {why}")
        return False
    save(rel, work.replace(old, new, 1), crlf)
    print(f"  ok  {rel}: {why}")
    return True


# ---------------------------------------------------------------------------
# 1. Symbol: currencies default to "" so the parser can actually run, and the
#    two missing MT5 currencies get real fields.
# ---------------------------------------------------------------------------

sub(
    "core/domains/instruments/symbol.py",
    '''    base_currency: str = "USD"  # e.g., "EUR" for EURUSD
    quote_currency: str = "USD"  # e.g., "USD" for EURUSD''',
    '''    # MT5 distinguishes THREE symbol currencies and they are not interchangeable:
    #   CurrencyBase    the base leg
    #   CurrencyProfit  the currency PnL is denominated in
    #   CurrencyMargin  the currency the margin requirement is computed in
    # For a plain FX pair they line up with base/quote; for indices, single equities and
    # bonds they do not. Measured on the 362 reference symbols, deriving them from the
    # symbol NAME gets 109 right, 60 wrong and cannot parse 193 at all - so these are
    # populated from MT5's own values on import, and the name heuristic below is only a
    # fallback for hand-written configs that omit them.
    #
    # These default to "" and NOT to "USD". Defaulting to "USD" made __post_init__'s
    # `if not self.base_currency` permanently False, so the parser never ran and every
    # symbol created without explicit currencies silently became USD/USD - EURJPY
    # included, which is what broke cross-currency PnL. A default that defeats the
    # fallback guarding it is worse than no default.
    base_currency: str = ""  # MT5 CurrencyBase, e.g. "EUR" for EURUSD
    quote_currency: str = ""  # MT5 CurrencyProfit, e.g. "USD" for EURUSD
    #: MT5 CurrencyMargin. When empty, margin is denominated in the base currency, which
    #: MT5 says is the usual case.
    margin_currency: str = ""''',
    "Symbol currencies default to \"\" (the \"USD\" default defeated __post_init__) "
    "and margin_currency added",
)

# The parser must now also fill margin_currency, and must not clobber a value MT5 gave us.
sub(
    "core/domains/instruments/symbol.py",
    '''    def __post_init__(self):
        """Parse base/quote currency from name if not set."""
        if not self.base_currency or not self.quote_currency:
            self.base_currency, self.quote_currency = self._parse_currencies_from_name()''',
    '''    def __post_init__(self):
        """Fill in currencies that were not supplied.

        MT5's own CurrencyBase / CurrencyProfit / CurrencyMargin always win - they are
        authoritative and the name heuristic is wrong for 253 of the 362 reference
        symbols. The parse runs only for what is still missing, which in practice means
        hand-written YAML that omits currencies.
        """
        if not self.base_currency or not self.quote_currency:
            parsed_base, parsed_quote = self._parse_currencies_from_name()
            self.base_currency = self.base_currency or parsed_base
            self.quote_currency = self.quote_currency or parsed_quote
        # A margin currency MT5 did not specify falls back to the base currency, per
        # Platform-Setup.md: "Generally, margin requirements currency and symbol's base
        # currency are the same."
        if not self.margin_currency:
            self.margin_currency = self.base_currency''',
    "__post_init__ fills only what is missing and defaults margin_currency to base",
)

# ---------------------------------------------------------------------------
# 2. fieldmap: map the two discarded currencies
# ---------------------------------------------------------------------------

sub(
    "infrastructure/mt5/fieldmap.py",
    '''    Field("CurrencyBase", "base_currency", STR),
    Field("CurrencyBaseDigits", "", INT),
    Field("CurrencyProfit", "", STR),
    Field("CurrencyProfitDigits", "", INT),
    Field("CurrencyMargin", "", STR),
    Field("CurrencyMarginDigits", "", INT),''',
    '''    # All THREE currencies are now mapped. They were diagnosed in M1 as the root cause of
    # the cross-currency PnL and margin bugs and left unmapped; mapping them is what makes
    # a EURJPY position on a USD account computable at all. The *Digits fields stay in the
    # quarantine: they are presentation precision, not trading semantics.
    Field("CurrencyBase", "base_currency", STR),
    Field("CurrencyBaseDigits", "", INT),
    Field("CurrencyProfit", "quote_currency", STR),
    Field("CurrencyProfitDigits", "", INT),
    Field("CurrencyMargin", "margin_currency", STR),
    Field("CurrencyMarginDigits", "", INT),''',
    "CurrencyProfit -> quote_currency and CurrencyMargin -> margin_currency (were discarded)",
)

# ---------------------------------------------------------------------------
# 3. SymbolModel: columns to hold them
# ---------------------------------------------------------------------------

sub(
    "infrastructure/persistence/config_models.py",
    '''    base_currency = Column(String(8), nullable=False, default="USD")
    quote_currency = Column(String(8), nullable=False, default="USD")''',
    '''    # MT5 CurrencyBase / CurrencyProfit / CurrencyMargin. quote_currency holds
    # CurrencyProfit, which is the currency PnL is denominated in - for an FX pair it is
    # the quote leg, which is why the name is kept. margin_currency is separate because
    # MT5 says it need not equal either.
    base_currency = Column(String(8), nullable=False, default="USD")
    quote_currency = Column(String(8), nullable=False, default="USD")
    margin_currency = Column(String(8), nullable=False, default="")''',
    "SymbolModel gains margin_currency",
)

# ---------------------------------------------------------------------------
# 4. The margin spec must prefer MT5's CurrencyMargin over the base currency
# ---------------------------------------------------------------------------

sub(
    "core/domains/market_data/margin.py",
    '''            # CurrencyMargin is not modelled on Symbol yet (fieldmap records it as a
            # gap), so fall back to the base currency, which MT5 says is the usual case.
            margin_currency=(
                getattr(symbol, "margin_currency", "")
                or getattr(symbol, "base_currency", "")
                or ""
            ),''',
    '''            # MT5 CurrencyMargin, falling back to the base currency - "Generally, margin
            # requirements currency and symbol's base currency are the same."
            margin_currency=(
                getattr(symbol, "margin_currency", "")
                or getattr(symbol, "base_currency", "")
                or ""
            ),''',
    "margin spec comment updated: CurrencyMargin is now modelled",
    required=False,
)
