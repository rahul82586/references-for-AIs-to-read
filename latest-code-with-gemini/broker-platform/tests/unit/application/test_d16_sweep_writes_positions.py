"""D16: the valuation sweep must write the POSITIONS, not only the account.

The live measurement that defined the defect (Neon, re-measured in sessions 5,
6 and 7): 24 of 45 accounts where

    equity - balance  !=  SUM(open positions' profit)

with the deltas identifying the writer exactly (+800.70 = (1.15968 - 1.07961)
x 0.10 x 100000, the mock open price against a live tick). The sweep computed
each position's PnL, wrote ONLY account.equity, and left the rows at
profit=0 / price_current NULL - the sweep built to make stored values
trustworthy was manufacturing the inconsistency it exists to remove. D13 fixed
this class in the tick pipeline; the sweep was written afterwards and
inherited the same bug.

The invariant these tests pin:

    WHEN a sweep writes an account (at least one position revalued),
    account.equity - account.balance == SUM(open positions' STORED profit):
    revalued rows contribute what the WRITER returned (not what the pass
    computed), preserved rows (no price / failed write / MOCK-over-live skip)
    contribute their stored profit, and closed-mid-sweep rows contribute
    nothing (their close already booked the realised PnL).

    WHEN nothing could be revalued, the sweep writes NOTHING - a pass with no
    new information must not restate old numbers from its own arithmetic.

And a MOCK tick never re-values a row that already carries a real
price_current.
"""
from decimal import Decimal

import pytest

from application.services.reconciliation_service import ValuationService
from core.domains.common.value_objects import Money
from tests.integration.trading_harness import build_harness


class _Row:
    """A duck-typed position row, shaped like what a repository hands back."""

    def __init__(self, pid, login, symbol="EURUSD", side="BUY", volume="0.10",
                 open_price="1.10000", stored_profit="0", valued=False):
        self.position_id = pid
        self.account_login = login
        self.symbol = symbol

        class _A:
            value = side
        self.action = _A()

        class _V:
            value = Decimal(volume)
        self.volume = _V()

        class _P:
            value = Decimal(open_price)
        self.price_open = _P()

        class _M:
            amount = Decimal(stored_profit)
        self.profit = _M()
        self.price_current = _P() if valued else None


class _WritingPositions:
    """The position repo WITH the column-scoped writer (the production shape).

    `written_profits` lets a test return a profit DIFFERENT from any local
    computation, proving the account side uses what the ROW says. `fail_ids`
    and `closed_ids` drive the two honest-degradation branches.
    """

    def __init__(self, rows, fail_ids=(), closed_ids=(), written_profits=None):
        self.rows = list(rows)
        self.fail_ids = set(fail_ids)
        self.closed_ids = set(closed_ids)
        self.written_profits = written_profits or {}
        self.calls = []

    async def get_open_positions(self):
        # the mid-sweep close happens BETWEEN this read and the write, so the
        # "gone" row is still in the list the sweep receives
        return list(self.rows)

    async def update_valuation(self, position_id, side, price_current, when=None, session=None):
        self.calls.append((position_id, side, Decimal(str(price_current))))
        if position_id in self.closed_ids:
            return None
        if position_id in self.fail_ids:
            raise RuntimeError("simulated write failure")
        if position_id in self.written_profits:
            profit = Decimal(self.written_profits[position_id])
        else:
            row = next(r for r in self.rows if r.position_id == position_id)
            diff = (Decimal(str(price_current)) - row.price_open.value) if side == "BUY" \
                else (row.price_open.value - Decimal(str(price_current)))
            profit = diff * row.volume.value  # contract_size 1 in the harness maths
        return {"volume": Decimal("0.10"), "profit": profit,
                "price_current": Decimal(str(price_current))}


class _TickEngine:
    """get_latest_tick with an explicit source label - the MOCK guard's input."""

    def __init__(self, ticks):
        self._ticks = ticks  # symbol -> (bid, ask, source)

    def get_latest_tick(self, symbol):
        t = self._ticks.get(symbol)
        if t is None:
            return None

        class _T:
            bid, ask, source = Decimal(str(t[0])), Decimal(str(t[1])), t[2]
        return _T()


def _service(h, positions, engine):
    return ValuationService(
        account_repo=h.account_repo,
        position_repo=positions,
        symbol_repo=h.symbol_repo,
        market_data_engine=engine,
        risk_engine=h.stack.risk_engine,
    )


@pytest.mark.asyncio
async def test_the_sweep_writes_every_priced_position_row():
    """The core of D16: the rows move, at the side-correct price."""
    h = await build_harness()
    login = h.accounts[0].login
    rows = [_Row("p-buy", login, side="BUY", open_price="1.10000"),
            _Row("p-sell", login, side="SELL", open_price="1.10000")]
    repo = _WritingPositions(rows)
    engine = _TickEngine({"EURUSD": ("1.10200", "1.10210", "LIVE")})

    await _service(h, repo, engine).revalue_all()

    by_id = {c[0]: c for c in repo.calls}
    assert by_id["p-buy"][1] == "BUY" and by_id["p-buy"][2] == Decimal("1.10200")   # a long is valued at BID
    assert by_id["p-sell"][1] == "SELL" and by_id["p-sell"][2] == Decimal("1.10210")  # a short at ASK


@pytest.mark.asyncio
async def test_equity_is_the_sum_of_what_the_rows_say_not_what_the_pass_computed():
    """The one-writer rule: the ROW is the authority for its own profit."""
    h = await build_harness()
    login = h.accounts[0].login
    account = await h.account_repo.find_by_login(login)
    rows = [_Row("p1", login, open_price="1.10000")]
    # the writer returns a profit that no local computation would produce
    repo = _WritingPositions(rows, written_profits={"p1": "123.45"})
    engine = _TickEngine({"EURUSD": ("1.10200", "1.10210", "LIVE")})

    await _service(h, repo, engine).revalue_all()

    after = await h.account_repo.find_by_login(login)
    assert after.equity.amount - after.balance.amount == Decimal("123.45")
    assert account is not None


@pytest.mark.asyncio
async def test_a_position_closed_mid_sweep_contributes_nothing():
    """Its close already booked the realised PnL - any number here doubles it."""
    h = await build_harness()
    login = h.accounts[0].login
    rows = [_Row("gone", login, open_price="1.10000", stored_profit="999"),
            _Row("alive", login, open_price="1.10000")]
    repo = _WritingPositions(rows, closed_ids={"gone"}, written_profits={"alive": "10.00"})
    engine = _TickEngine({"EURUSD": ("1.10200", "1.10210", "LIVE")})

    stats = await _service(h, repo, engine).revalue_all()

    after = await h.account_repo.find_by_login(login)
    assert after.equity.amount - after.balance.amount == Decimal("10.00")  # the 999 is NOT in it
    assert stats.get("closed_mid_sweep") == 1


@pytest.mark.asyncio
async def test_a_failed_row_write_mixes_the_stored_profit_into_a_real_sweep():
    """Degrade honestly per-row: the failed row's stored profit rides into the
    account total alongside the row that DID revalue, so the invariant
    equity - balance == SUM(stored profits) holds across the whole book."""
    h = await build_harness()
    login = h.accounts[0].login
    rows = [_Row("bad", login, open_price="1.10000", stored_profit="55.55"),
            _Row("good", login, open_price="1.10000")]
    repo = _WritingPositions(rows, fail_ids={"bad"}, written_profits={"good": "20.00"})
    engine = _TickEngine({"EURUSD": ("1.10200", "1.10210", "LIVE")})

    stats = await _service(h, repo, engine).revalue_all()

    after = await h.account_repo.find_by_login(login)
    assert after.equity.amount - after.balance.amount == Decimal("75.55")  # 20.00 written + 55.55 preserved
    assert stats.get("positions_write_failed") == 1


@pytest.mark.asyncio
async def test_a_sweep_that_revalues_nothing_writes_nothing():
    """Every write failed -> priced_any is False -> the account is untouched.
    A sweep with nothing new to say must not say anything: the stored figures
    are already what they are, and rewriting them from a failed pass would be
    the one-sided write D16 is about."""
    h = await build_harness()
    login = h.accounts[0].login
    before = await h.account_repo.find_by_login(login)
    equity_before = before.equity.amount
    rows = [_Row("bad", login, open_price="1.10000", stored_profit="55.55")]
    repo = _WritingPositions(rows, fail_ids={"bad"})
    engine = _TickEngine({"EURUSD": ("1.10200", "1.10210", "LIVE")})

    stats = await _service(h, repo, engine).revalue_all()

    after = await h.account_repo.find_by_login(login)
    assert after.equity.amount == equity_before
    assert stats.get("positions_write_failed") == 1
    assert stats["revalued"] == 0


@pytest.mark.asyncio
async def test_a_priceless_position_keeps_its_stored_profit():
    """No price => no revaluation - but its stored profit must not be dropped
    from the account either (the old sweep silently zeroed it out of equity)."""
    h = await build_harness()
    login = h.accounts[0].login
    rows = [_Row("priced", login, symbol="EURUSD", open_price="1.10000"),
            _Row("dark", login, symbol="XAUUSD", open_price="2000", stored_profit="77.77")]
    repo = _WritingPositions(rows, written_profits={"priced": "20.00"})
    engine = _TickEngine({"EURUSD": ("1.10200", "1.10210", "LIVE")})  # no XAUUSD price

    stats = await _service(h, repo, engine).revalue_all()

    after = await h.account_repo.find_by_login(login)
    assert after.equity.amount - after.balance.amount == Decimal("20.00") + Decimal("77.77")
    assert stats["skipped_no_price"] >= 1


@pytest.mark.asyncio
async def test_a_mock_tick_never_degrades_a_live_valued_position():
    """Restarting with MARKET_DATA_SOURCE=mock must not overwrite real numbers
    with fiction - the second half of the D16 fix."""
    h = await build_harness()
    login = h.accounts[0].login
    rows = [_Row("valued", login, open_price="1.10000", stored_profit="300.00", valued=True)]
    repo = _WritingPositions(rows, written_profits={"valued": "-999"})
    engine = _TickEngine({"EURUSD": ("1.10200", "1.10210", "MOCK")})

    before = await h.account_repo.find_by_login(login)
    equity_before = before.equity.amount
    stats = await _service(h, repo, engine).revalue_all()

    assert repo.calls == []                                   # never even attempted
    assert stats.get("skipped_mock_over_live") == 1
    after = await h.account_repo.find_by_login(login)
    assert after.equity.amount == equity_before               # nothing written: the real figures stand


@pytest.mark.asyncio
async def test_a_mock_tick_may_value_a_never_valued_position():
    """Fiction is allowed where nothing real exists yet (price_current NULL) -
    a fully-mock world stays internally consistent."""
    h = await build_harness()
    login = h.accounts[0].login
    rows = [_Row("fresh", login, open_price="1.10000", valued=False)]
    repo = _WritingPositions(rows, written_profits={"fresh": "20.00"})
    engine = _TickEngine({"EURUSD": ("1.10200", "1.10210", "MOCK")})

    await _service(h, repo, engine).revalue_all()

    assert len(repo.calls) == 1
    after = await h.account_repo.find_by_login(login)
    assert after.equity.amount - after.balance.amount == Decimal("20.00")


@pytest.mark.asyncio
async def test_a_repo_without_the_writer_falls_back_to_the_computed_account_side():
    """The legacy contract (D9's harness shape): in-memory doubles have no
    update_valuation; the sweep still revalues the account and says so."""
    h = await build_harness()
    login = h.accounts[0].login

    class _Legacy:
        def __init__(self, rows):
            self.rows = rows

        async def get_open_positions(self):
            return list(self.rows)

    rows = [_Row("p1", login, open_price="1.10000")]
    engine = _TickEngine({"EURUSD": ("1.10200", "1.10210", "LIVE")})

    stats = await _service(h, _Legacy(rows), engine).revalue_all()

    assert stats["revalued"] == 1
    after = await h.account_repo.find_by_login(login)
    assert after.equity.amount > after.balance.amount  # computed PnL landed on the account
