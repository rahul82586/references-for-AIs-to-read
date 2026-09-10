"""
Step M3 part 21 - the conversion side was being thrown away.

`RiskEngine._rate_lookup` accepts the `side` argument that
core.domains.market_data.margin passes it - the side that selects which half of the spread
to convert at - and then drops it:

    def _rate_lookup(self, from_currency, to_currency, side):
        return self.get_conversion_rate(from_currency, to_currency)   # side discarded

`get_conversion_rate` in turn always took the direct pair at its BID. So every margin
conversion in the system used the bid, for buys and sells alike.

MT5 says otherwise, in `Margin-Calculation/Retail-Forex-CFD-Futures-—-Hedging.md`:

    "The current exchange rate of margin currency to deposit currency is used for
     conversion. The Ask price is used for buy deals, and the Bid price is used for sell
     deals."

This is not a rounding detail. Converting a buy at the bid instead of the ask understates
the margin requirement by the width of the spread, on every buy, in every symbol whose
margin currency differs from the account currency. On a 5-pip EURUSD spread that is ~0.05%
of the requirement; on an illiquid cross with a 50-pip spread it is materially more, and
it is systematically in the client's favour - which is exactly the direction a broker
cannot afford to be systematically wrong in.

The failing assertion that exposed it expected 2201.00 for two 1-lot EURUSD buys on a USD
account:

    basic   2 * (1 * 100,000 / 100)          = 2,000 EUR
    convert 2,000 EUR * ASK 1.1005           = 2,201.00 USD   <- MT5, buy deal
    (the engine was returning 2,000 * 1.1000 = 2,200.00, the bid)

So the test was right and the new engine was wrong. The side now flows through:
`_rate_lookup` passes it to `get_conversion_rate`, which passes it to `_pair_rate`, which
takes the ASK of the direct pair for a buy and the BID for a sell - and correspondingly
1/BID or 1/ASK on the inverse pair, since inverting swaps the side of the spread.

`side` may also be "PROFIT", used when converting PnL. There MT5 uses the profit-currency
rate and the same rate must apply to gains and losses, or equity would depend on its own
sign; that case takes the bid, matching the pre-existing behaviour and the PnL test that
already asserts it.
"""

from __future__ import annotations

import pathlib
import sys

ROOT = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else pathlib.Path.cwd()
REL = "core/domains/risk/engine.py"
path = ROOT / REL
if not path.is_file():
    raise SystemExit(f"not found: {path}")

with open(path, encoding="utf-8", newline="") as fh:
    text = fh.read()
crlf = "\r\n" in text
work = text.replace("\r\n", "\n")


def sub(old: str, new: str, why: str) -> None:
    global work
    if old not in work:
        raise SystemExit(f"[FAIL] {REL}: pattern not found ({why}):\n{old[:300]!r}")
    work = work.replace(old, new, 1)
    print(f"  ok  {REL}: {why}")


# ---------------------------------------------------------------------------
# 1. _rate_lookup must pass the side through
# ---------------------------------------------------------------------------

sub(
    '''    def _rate_lookup(self, from_currency: str, to_currency: str, side: str) -> Decimal:
        """Adapter matching the callable signature core.domains.market_data.margin wants."""
        return self.get_conversion_rate(from_currency, to_currency)''',
    '''    def _rate_lookup(self, from_currency: str, to_currency: str, side: str) -> Decimal:
        """Adapter matching the callable signature core.domains.market_data.margin wants.

        ``side`` is not decoration. MT5 converts a BUY deal's margin at the ASK and a SELL
        deal's at the BID, so dropping it - as this did - understated every buy's margin
        requirement by the width of the spread.
        """
        return self.get_conversion_rate(from_currency, to_currency, side=side)''',
    "_rate_lookup forwards the side instead of discarding it",
)

# ---------------------------------------------------------------------------
# 2. get_conversion_rate accepts and propagates it
# ---------------------------------------------------------------------------

sub(
    '''    def get_conversion_rate(
        self,
        from_currency: str,
        to_currency: str,
        market_feed: Optional[Any] = None,
    ) -> Decimal:''',
    '''    def get_conversion_rate(
        self,
        from_currency: str,
        to_currency: str,
        market_feed: Optional[Any] = None,
        side: str = "BUY",
    ) -> Decimal:''',
    "get_conversion_rate takes a side (defaulting to BUY, the conservative direction)",
)

sub(
    '''        Tries, in order:
          1. the direct pair   {from}{to}   at its bid
          2. the inverse pair  {to}{from}   as 1 / ask
          3. TRIANGULATION through an intermediate currency: from->X and X->to, so that a
             EURJPY position on a USD account resolves via EURUSD. This is the case the
             original audit flagged and the previous implementation could not do at all.''',
    '''        Tries, in order:
          1. the direct pair   {from}{to}
          2. the inverse pair  {to}{from}, inverted
          3. TRIANGULATION through an intermediate currency: from->X and X->to, so that a
             EURJPY position on a USD account resolves via EURUSD. This is the case the
             original audit flagged and the previous implementation could not do at all.

        Which half of the spread is used depends on ``side``, per MT5: "The Ask price is
        used for buy deals, and the Bid price is used for sell deals." ``side="PROFIT"``
        is used for PnL conversion, where gains and losses must convert at the SAME rate
        or equity would depend on its own sign.''',
    "docstring states the side rule",
)

sub(
    '''            direct = self._pair_rate(from_currency, to_currency)
            if direct is not None:
                return direct

            for intermediate in TRIANGULATION_CURRENCIES:
                if intermediate in (from_currency, to_currency):
                    continue
                first = self._pair_rate(from_currency, intermediate)
                if first is None:
                    continue
                second = self._pair_rate(intermediate, to_currency)
                if second is None:
                    continue
                return first * second''',
    '''            direct = self._pair_rate(from_currency, to_currency, side)
            if direct is not None:
                return direct

            for intermediate in TRIANGULATION_CURRENCIES:
                if intermediate in (from_currency, to_currency):
                    continue
                first = self._pair_rate(from_currency, intermediate, side)
                if first is None:
                    continue
                second = self._pair_rate(intermediate, to_currency, side)
                if second is None:
                    continue
                return first * second''',
    "both the direct and the triangulated lookups honour the side",
)

# ---------------------------------------------------------------------------
# 3. _pair_rate takes the correct half of the spread
# ---------------------------------------------------------------------------

sub(
    '''    def _pair_rate(self, from_currency: str, to_currency: str) -> Optional[Decimal]:
        """Direct or inverse rate for one currency pair, or None if unavailable.

        Tries the direct pair at its bid, then the inverse pair as 1/ask. A symbol named
        exactly "{from}{to}" is the normal case - EURUSD for EUR -> USD - so this is what
        resolves most conversions without any triangulation.
        """
        for suffix in self.PAIR_SUFFIXES:
            direct = f"{from_currency}{to_currency}{suffix}"
            try:
                bid = self._side_price(direct, "bid", fresh=False)
                if bid > 0:
                    return bid
            except (PositionValuationError, StaleQuoteError):
                pass

            inverse = f"{to_currency}{from_currency}{suffix}"
            try:
                ask = self._side_price(inverse, "ask", fresh=False)
                if ask > 0:
                    return Decimal("1") / ask
            except (PositionValuationError, StaleQuoteError):
                pass
        return None''',
    '''    def _pair_rate(
        self, from_currency: str, to_currency: str, side: str = "BUY"
    ) -> Optional[Decimal]:
        """Direct or inverse rate for one currency pair, or None if unavailable.

        A symbol named exactly "{from}{to}" is the normal case - EURUSD for EUR -> USD -
        so this resolves most conversions with no triangulation.

        Which side of the spread is taken follows MT5: the ASK for buy deals, the BID for
        sell deals. Inverting the pair swaps the side, because the broker's ask on USDJPY
        is the broker's bid on JPYUSD - so an inverse lookup for a buy takes 1/BID.

        "PROFIT" is the PnL case: one rate for gains and losses alike, so that equity does
        not depend on its own sign.
        """
        want_ask = str(side).upper().startswith("BUY")
        for suffix in self.PAIR_SUFFIXES:
            direct = f"{from_currency}{to_currency}{suffix}"
            try:
                price = self._side_price(direct, "ask" if want_ask else "bid", fresh=False)
                if price > 0:
                    return price
            except (PositionValuationError, StaleQuoteError):
                pass

            inverse = f"{to_currency}{from_currency}{suffix}"
            try:
                price = self._side_price(inverse, "bid" if want_ask else "ask", fresh=False)
                if price > 0:
                    return Decimal("1") / price
            except (PositionValuationError, StaleQuoteError):
                pass
        return None''',
    "_pair_rate takes the ASK for buys and the BID for sells (and inverts correctly)",
)

with open(path, "w", encoding="utf-8", newline="") as fh:
    fh.write(work.replace("\n", "\r\n") if crlf else work)

# ---------------------------------------------------------------------------
# 4. The margin module's own tests asserted bid-for-both; the rule is side-dependent
# ---------------------------------------------------------------------------

REL2 = "tests/unit/domains/market_data/test_mt5_margin.py"
path2 = ROOT / REL2
if path2.is_file():
    with open(path2, encoding="utf-8", newline="") as fh:
        t2 = fh.read()
    crlf2 = "\r\n" in t2
    w2 = t2.replace("\r\n", "\n")
    # The JPY/USD triangulation fixtures in the EURJPY test resolve JPY->USD via the
    # inverse of USDJPY. That test asserts 1/150 with a constant lookup, which is
    # unaffected. Nothing to change unless a lookup ignores side.
    print(f"  --  {REL2}: side-independent fixtures, no change needed")
