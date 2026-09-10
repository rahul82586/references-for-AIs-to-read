"""
Step M3 part 20 - the concurrency test's fixtures, and one real engine limitation.

The engine now refuses to guess a conversion rate, which is correct behaviour, and this
test hit it: a EURUSD position on a USD account needs EUR -> USD, and the test's fixtures
could not supply it. Two fixture defects and one engine gap:

1. `MockMarketFeed.get_latest_tick` is `async`, but RiskEngine reads the feed
   SYNCHRONOUSLY - deliberately, because margin is on the pre-trade hot path and an await
   there would put the feed's latency in front of every order. The engine therefore saw no
   tick at all. The mock gets a synchronous `get_latest_tick` plus `get_bid` / `get_ask`,
   which is the shape the engine accepts. The async method is kept because
   RecordDealHandler still awaits the feed directly.

2. `Symbol(name="EURUSD", ...)` did not declare its currencies. Now that Symbol's
   currencies default to "" rather than "USD", the name heuristic runs - but EURUSD's
   margin currency is EUR while the account is USD, so a rate is genuinely required. The
   fixture now states MT5's own values explicitly, which is what an imported symbol carries.

3. THE ENGINE GAP, and the reason this is a product fix rather than only a test fix:
   triangulation only tried currency PAIRS (EURUSD, USDEUR, EURJPY...). It never tried a
   bare CURRENCY symbol. Real servers list both - the reference export has `EURUSD` and
   also currency-only instruments - and more importantly the DIRECT pair is the normal
   case: EURUSD for EUR -> USD, USDJPY for USD -> JPY. Adding bare currency names to the
   candidate list means EUR -> USD resolves from an "EURUSD" quote with no triangulation
   at all, which is how MT5 itself does it.

   Without this, any account whose deposit currency differs from a symbol's margin
   currency would have been unable to record a deal at all.
"""

from __future__ import annotations

import pathlib
import re
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


def sub(rel: str, old: str, new: str, why: str, *, required: bool = True) -> None:
    text = load(rel)
    crlf = "\r\n" in text
    work = text.replace("\r\n", "\n")
    if old not in work:
        if required:
            raise SystemExit(f"[FAIL] {rel}: pattern not found ({why}):\n{old[:300]!r}")
        print(f"  skip {rel}: {why}")
        return
    save(rel, work.replace(old, new, 1), crlf)
    print(f"  ok  {rel}: {why}")


# ---------------------------------------------------------------------------
# 1. The engine: try the bare currency pair as well as the suffixed one
# ---------------------------------------------------------------------------

sub(
    "core/domains/risk/engine.py",
    '''    def _pair_rate(self, from_currency: str, to_currency: str) -> Optional[Decimal]:
        """Direct or inverse rate for one currency pair, or None if unavailable."""
        direct = f"{from_currency}{to_currency}"
        try:
            bid = self._side_price(direct, "bid", fresh=False)
            if bid > 0:
                return bid
        except (PositionValuationError, StaleQuoteError):
            pass

        inverse = f"{to_currency}{from_currency}"
        try:
            ask = self._side_price(inverse, "ask", fresh=False)
            if ask > 0:
                return Decimal("1") / ask
        except (PositionValuationError, StaleQuoteError):
            pass
        return None''',
    '''    #: Suffixes some servers append to a bare currency pair. Tried after the plain name.
    PAIR_SUFFIXES = ("", ".spot", ".m", "_", "-")

    def _pair_rate(self, from_currency: str, to_currency: str) -> Optional[Decimal]:
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
    "_pair_rate tries the bare currency pair (EURUSD for EUR->USD) plus common suffixes",
)

# ---------------------------------------------------------------------------
# 2. The test's market feed must be readable synchronously
# ---------------------------------------------------------------------------

sub(
    "tests/unit/concurrency/test_execution_concurrency.py",
    '''class MockMarketFeed:
    async def get_latest_tick(self, symbol: str):
        return {"bid": "1.1000", "ask": "1.1005"}''',
    '''class MockMarketFeed:
    """A feed readable both ways.

    RecordDealHandler awaits `get_latest_tick`. RiskEngine reads the feed SYNCHRONOUSLY -
    deliberately, since margin sits on the pre-trade hot path and an await there would put
    the feed's latency in front of every order. A mock that only offered the async form
    gave the engine no tick at all, so it could not price or convert anything.

    EURUSD is present because EUR -> USD is a real conversion for a USD account: the
    symbol's margin currency is EUR, and the engine refuses to assume 1.0.
    """

    _TICKS = {
        "EURUSD": {"bid": "1.1000", "ask": "1.1005"},
        "USDJPY": {"bid": "149.990", "ask": "150.000"},
    }

    async def get_latest_tick(self, symbol: str):
        return self._TICKS.get(symbol)

    def get_bid(self, symbol: str):
        tick = self._TICKS.get(symbol)
        return Decimal(tick["bid"]) if tick else None

    def get_ask(self, symbol: str):
        tick = self._TICKS.get(symbol)
        return Decimal(tick["ask"]) if tick else None''',
    "MockMarketFeed is readable synchronously and carries EURUSD",
)

# ---------------------------------------------------------------------------
# 3. The test's symbol must declare its currencies
# ---------------------------------------------------------------------------

sub(
    "tests/unit/concurrency/test_execution_concurrency.py",
    '''    symbol = Symbol(
        name="EURUSD",
        path="Forex" + chr(92) + "EURUSD",
        tick_size=Decimal('0.00001'),''',
    '''    symbol = Symbol(
        name="EURUSD",
        path="Forex" + chr(92) + "EURUSD",
        # MT5's own values for EURUSD. The margin currency is EUR while the account is
        # USD, so converting the requirement is not optional - it is the case that makes
        # cross-currency margin real rather than theoretical.
        base_currency="EUR",
        quote_currency="USD",
        margin_currency="EUR",
        tick_size=Decimal('0.00001'),''',
    "the test symbol declares EUR/USD/EUR as its three currencies",
    required=False,
)
