"""Trade calculators (M18 B12) - MT5's `trade/calc_*` family over HTTP.

The Manager terminal's calculator buttons, backed by the SAME canonical
maths the trading path uses (RiskEngine's 4-stage margin pipeline and its
PnL function) - never a parallel formula. A calculator that disagrees with
the risk engine by a cent is how a client learns the platform's two answers
to one question (the D1/D13/D16 class, in a read-only costume).

All four are PURE READS: nothing is persisted, no order is created. The
hypothetical leg is a transient domain object, priced at the CURRENT market
(the engine refuses when there is no price - a margin number invented from a
stale or absent tick is worse than no answer).
"""
from dataclasses import dataclass
from decimal import Decimal
from typing import Any, Dict, Optional


class CalculatorRefusedError(ValueError):
    """The calculator refuses: unknown symbol/group/account, or no live price."""


@dataclass(frozen=True)
class CalcMarginQuery:
    group_name: str
    symbol: str
    side: str                 # BUY | SELL
    volume: Decimal           # lots
    currency: Optional[str] = None    # deposit currency; default = the group's


@dataclass(frozen=True)
class CalcProfitQuery:
    symbol: str
    side: str
    volume: Decimal
    open_price: Decimal
    currency: Optional[str] = None    # account/deposit currency; default USD


@dataclass(frozen=True)
class CalcRateQuery:
    from_currency: str
    to_currency: str
    side: str = "BUY"


@dataclass(frozen=True)
class CheckMarginQuery:
    login: int
    symbol: str
    side: str
    volume: Decimal


class TradeCalculatorHandler:
    """One handler, four calculations, one authority: the RiskEngine."""

    def __init__(self, risk_engine: Any, group_repo: Any, account_repo: Any,
                 position_repo: Any):
        self.risk_engine = risk_engine
        self.group_repo = group_repo
        self.account_repo = account_repo
        self.position_repo = position_repo

    def _require_engine(self):
        if self.risk_engine is None:
            raise CalculatorRefusedError(
                "no risk engine is wired on this server; the calculator refuses "
                "rather than approximate"
            )

    def _hypothetical(self, symbol: str, side: str, volume: Decimal, open_price: Decimal):
        from core.domains.common.value_objects import Price, Volume
        from core.domains.oms.entities.position import Position
        from core.domains.oms.enums import PositionAction

        action = PositionAction.BUY if str(side).upper().startswith("BUY") else PositionAction.SELL
        return Position(
            position_id="hypothetical", account_login=0, symbol=symbol, action=action,
            volume=Volume(Decimal(str(volume))), price_open=Price(Decimal(str(open_price))),
        )

    def _synthetic_account(self, currency: str, group: Any, login: int = 0):
        from core.domains.accounts.account import Account

        return Account(login=login, currency=currency, group=group,
                       group_id=getattr(group, "id", "") if group is not None else "")

    async def calc_margin(self, q: CalcMarginQuery) -> Dict[str, Any]:
        self._require_engine()
        group = await self.group_repo.find_by_name(q.group_name) if self.group_repo else None
        if group is None:
            raise CalculatorRefusedError(f"no group {q.group_name!r}")
        currency = q.currency or group.currency
        try:
            price = self.risk_engine.get_ask(q.symbol) if str(q.side).upper().startswith("BUY") \
                else self.risk_engine.get_bid(q.symbol)
        except Exception as exc:
            raise CalculatorRefusedError(f"no live price for {q.symbol}: {exc}")
        account = self._synthetic_account(currency, group)
        position = self._hypothetical(q.symbol, q.side, q.volume, price)
        try:
            snapshot = self.risk_engine.calculate_margin_level(account, [position])
        except Exception as exc:
            raise CalculatorRefusedError(f"margin calculation refused: {exc}")
        return {
            "margin_required": str(snapshot.margin_used),
            "symbol": q.symbol, "side": q.side.upper(), "volume": str(q.volume),
            "price_used": str(price),
            "group": q.group_name, "currency": currency,
            "note": "priced at the CURRENT market; the trading path re-checks at order time",
        }

    async def calc_profit(self, q: CalcProfitQuery) -> Dict[str, Any]:
        self._require_engine()
        try:
            price = self.risk_engine.get_bid(q.symbol) if str(q.side).upper().startswith("BUY") \
                else self.risk_engine.get_ask(q.symbol)
        except Exception as exc:
            raise CalculatorRefusedError(f"no live price for {q.symbol}: {exc}")
        account = self._synthetic_account(q.currency or "USD", None)
        position = self._hypothetical(q.symbol, q.side, q.volume, q.open_price)
        try:
            pnl = self.risk_engine.calculate_position_pnl(account, position)
        except Exception as exc:
            raise CalculatorRefusedError(f"profit calculation refused: {exc}")
        return {
            "profit": str(pnl), "symbol": q.symbol, "side": q.side.upper(),
            "volume": str(q.volume), "open_price": str(q.open_price),
            "close_price_used": str(price), "currency": account.currency,
            "note": "valued at the CURRENT market, through the engine the margin loop uses",
        }

    async def calc_rate(self, q: CalcRateQuery) -> Dict[str, Any]:
        self._require_engine()
        try:
            rate = self.risk_engine.get_conversion_rate(q.from_currency, q.to_currency, side=q.side)
        except Exception as exc:
            raise CalculatorRefusedError(str(exc))
        return {"from": q.from_currency, "to": q.to_currency, "rate": str(rate), "side": q.side}

    async def check_margin(self, q: CheckMarginQuery) -> Dict[str, Any]:
        """Can this account open this position right now? The same snapshot
        maths the pre-trade check runs, exposed read-only."""
        self._require_engine()
        account = await self.account_repo.find_by_login(q.login)
        if account is None:
            account = await self.account_repo.find_by_login(str(q.login))
        if account is None:
            raise CalculatorRefusedError(f"no account with login {q.login}")
        open_positions = await self.position_repo.get_positions_by_account(int(q.login))
        try:
            price = self.risk_engine.get_ask(q.symbol) if str(q.side).upper().startswith("BUY") \
                else self.risk_engine.get_bid(q.symbol)
        except Exception as exc:
            raise CalculatorRefusedError(f"no live price for {q.symbol}: {exc}")
        new_leg = self._hypothetical(q.symbol, q.side, q.volume, price)
        try:
            before = self.risk_engine.calculate_margin_level(account, list(open_positions))
            after = self.risk_engine.calculate_margin_level(account, list(open_positions) + [new_leg])
        except Exception as exc:
            raise CalculatorRefusedError(f"margin calculation refused: {exc}")
        margin_required = after.margin_used - before.margin_used
        return {
            "login": int(q.login), "symbol": q.symbol, "side": q.side.upper(),
            "volume": str(q.volume), "price_used": str(price),
            "margin_required": str(margin_required),
            "margin_used_current": str(before.margin_used),
            "margin_used_after": str(after.margin_used),
            "equity": str(after.equity),
            "margin_free_after": str(after.margin_free),
            "margin_level_after": str(after.margin_level),
            "sufficient": after.margin_free > Decimal("0"),
        }
