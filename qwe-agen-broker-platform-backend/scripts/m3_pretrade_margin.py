"""
Step M3 part 1 - route the pre-trade margin check through the MT5-accurate engine.

FOUR DEFECTS IN `_check_margin_requirement`, all of them fatal or money-losing:

1. `order.order_type.startswith("BUY")` - order_type is an OrderType ENUM, not a string,
   so this raised AttributeError on EVERY order. The pre-trade margin check never
   returned True or False; it threw. Depending on the caller's exception handling the
   order was either rejected or, worse, the failure was swallowed upstream and the order
   proceeded unchecked.

2. Margin was computed inline as
   `(volume * contract_size * price * margin_rate) / leverage` - a fourth independent
   copy of the formula, and the CFD formula applied to every symbol. For a Forex symbol
   MT5's formula is `volume * contract_size / leverage` with NO price term, so this
   over-charged Forex margin by a factor of the price (~1.1 for EURUSD, ~150 for USDJPY,
   ~2000 for BTCUSD).

3. It ignored the margin currency entirely. MT5 stage 2 converts margin currency to
   deposit currency using ASK for buys and BID for sells; this multiplied by a rate that
   was never fetched, so every non-USD-margin symbol was wrong.

4. `except Exception` around `calculate_margin_level` fell back to
   `account.margin_free.amount` - a stored figure that may be arbitrarily stale - and
   logged at error level while approving the trade anyway. A risk check that silently
   degrades to a cached number on failure is not a risk check.

Also fixed here: `Group.calculate_margin` had the same inline formula and used
`min(leverage_default, leverage_max)` as the effective leverage, which is not how MT5
resolves leverage (account override, then group, then symbol cap).
"""

from __future__ import annotations

import pathlib
import sys

ROOT = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else pathlib.Path.cwd()
if not (ROOT / "application" / "services" / "risk_service.py").is_file():
    raise SystemExit(f"not a broker-platform root: {ROOT}")


def load(rel: str) -> str:
    with open(ROOT / rel, encoding="utf-8", newline="") as fh:
        return fh.read()


def save(rel: str, text: str, crlf: bool) -> None:
    norm = text.replace("\r\n", "\n")
    with open(ROOT / rel, "w", encoding="utf-8", newline="") as fh:
        fh.write(norm.replace("\n", "\r\n") if crlf else norm)


def replace_span(rel: str, start_marker: str, end_marker: str, new: str, why: str) -> None:
    text = load(rel)
    crlf = "\r\n" in text
    work = text.replace("\r\n", "\n")
    start = work.find(start_marker)
    if start == -1:
        raise SystemExit(f"[FAIL] {rel}: start marker not found: {start_marker[:80]!r}")
    end = work.find(end_marker, start)
    if end == -1:
        raise SystemExit(f"[FAIL] {rel}: end marker not found: {end_marker[:80]!r}")
    save(rel, work[:start] + new + work[end:], crlf)
    print(f"  ok  {rel}: {why}")


# ---------------------------------------------------------------------------
# 1. risk_service._check_margin_requirement
# ---------------------------------------------------------------------------

NEW_CHECK = '''    async def _check_margin_requirement(
        self,
        order: Order,
        account: Account,
        symbol: Symbol,
        price: Price,
    ) -> bool:
        """Pre-trade initial margin check, using the MT5-accurate engine.

        MT5 checks INITIAL margin when opening a position and MAINTENANCE margin for
        positions already open; pending orders are always checked at initial. This is the
        opening path, so it uses initial.

        The calculation runs all four MT5 stages - basic, conversion to the deposit
        currency, the operation's rate multiplier, and aggregation - through
        core.domains.market_data.margin, which is where the formulas and MT5's own
        published worked examples are asserted. Nothing here re-derives a formula.
        """
        from core.domains.market_data.margin import (
            MarginCalculationError,
            SymbolMarginSpec,
            apply_rate,
            basic_margin,
            convert_to_deposit,
            available_margin,
        )

        order_type = order.order_type.value if hasattr(order.order_type, "value") else str(order.order_type)
        operation = order_type.upper()

        # 1. Symbol spec, then group overrides on top. MT5: "To avoid overriding the
        #    coefficient value for a group, leave the value set to Default" - so a None
        #    override means inherit, never zero.
        spec = SymbolMarginSpec.from_symbol(symbol)
        if account.group is not None:
            overrides = account.group.get_symbol_config(symbol.name)
            spec = self._apply_group_overrides(spec, overrides)

        # 2. Leverage resolves account -> group -> symbol cap, not
        #    min(group.default, group.max) which ignores both the account override and
        #    the per-symbol maximum.
        leverage = self._resolve_leverage(account, symbol)

        # 3. Stages 1-3. A market order with no price raises rather than defaulting to
        #    1.0 - that default understated JPY margin by ~150x.
        price_value = price.value if price is not None else None
        try:
            basic = basic_margin(spec, order.volume.value, price_value, leverage=leverage)
            converted = convert_to_deposit(
                basic,
                margin_currency=spec.margin_currency,
                deposit_currency=account.currency,
                side="BUY" if operation.startswith("BUY") else "SELL",
                rate_lookup=self._rate_lookup,
            )
            required = apply_rate(converted, spec, operation, maintenance=False)
        except MarginCalculationError as exc:
            # A margin requirement we cannot compute is a rejection, not an approval.
            # The previous code caught every exception here and fell back to a stored
            # free-margin figure, which approved trades on stale data.
            logger.warning(
                "margin check for order %s could not be computed: %s", order.ticket_id, exc
            )
            return False

        # 4. Available margin. Use the live snapshot when we can build one, and treat a
        #    failure to build it as a rejection rather than silently degrading to a
        #    cached number.
        available = account.margin_free.amount
        if self.risk_engine is not None and self.position_repo is not None:
            try:
                open_positions = await self.position_repo.get_by_account(account.login)
                snapshot = self.risk_engine.calculate_margin_level(account, open_positions)
                # Conservative: a positive unrealised gain is not trusted to authorise a
                # new position, only a loss reduces availability. This is the rule
                # tfrmma/oms margin_monitor.hpp documents - a local estimate that has
                # drifted optimistic must not open trades.
                available = available_margin(
                    equity=snapshot.equity,
                    margin_used=snapshot.margin_used,
                    unrealized_pnl=snapshot.equity - account.balance.amount,
                    conservative=True,
                )
            except Exception as exc:  # noqa: BLE001 - but do NOT approve on failure
                logger.error(
                    "live margin snapshot failed for %s; rejecting rather than trusting "
                    "the stored free margin: %s",
                    account.login,
                    exc,
                )
                return False

        if required > available:
            logger.debug(
                "margin check failed for %s: required %s, available %s",
                order.ticket_id,
                required,
                available,
            )
            return False
        return True

    def _resolve_leverage(self, account: Account, symbol: Symbol) -> int:
        """Account override, then group, then the symbol cap. Never zero.

        MT5 applies the most restrictive of these. The previous code used
        min(group.leverage_default, group.leverage_max), which ignored the account's own
        override entirely.
        """
        candidates = []
        account_leverage = getattr(account, "leverage", None)
        if account_leverage and account_leverage > 0:
            candidates.append(int(account_leverage))
        group = getattr(account, "group", None)
        if group is not None:
            default = getattr(group.margin, "leverage_default", 0) or 0
            maximum = getattr(group.margin, "leverage_max", 0) or 0
            if default > 0:
                candidates.append(int(default))
            if maximum > 0:
                candidates.append(int(maximum))
        symbol_max = getattr(symbol, "leverage_max", 0) or 0
        if symbol_max > 0:
            candidates.append(int(symbol_max))
        if not candidates:
            return 1
        return min(candidates)

    def _apply_group_overrides(self, spec, overrides: dict):
        """Overlay a group's per-symbol overrides onto the symbol spec.

        An override value of None means "inherit from the symbol", which MT5 encodes on
        the wire as the string "default". It must never be read as zero: a zero margin
        rate means "no margin charged for this operation type", which is a real and
        dangerous setting, not an absent one.
        """
        from dataclasses import replace as _replace
        from decimal import Decimal as _Decimal

        rates = dict(spec.rates)
        changes = {}
        for key, value in (overrides or {}).items():
            if value is None:
                continue
            if key.startswith("margin_rate_initial_"):
                rates[key.replace("margin_rate_initial_", "initial_")] = _Decimal(str(value))
            elif key.startswith("margin_rate_maintenance_"):
                rates[key.replace("margin_rate_maintenance_", "maintenance_")] = _Decimal(str(value))
            elif key == "contract_size":
                changes["contract_size"] = _Decimal(str(value))
            elif key == "margin_hedged":
                changes["margin_hedged"] = _Decimal(str(value))
        return _replace(spec, rates=rates, **changes)

    def _rate_lookup(self, from_currency: str, to_currency: str, side: str):
        """Currency conversion for margin, delegating to the risk engine.

        Returns None when no rate is available, which convert_to_deposit turns into a
        rejection. Never returns 1.0 as a guess.
        """
        if self.risk_engine is None:
            return None
        getter = getattr(self.risk_engine, "get_conversion_rate", None)
        if getter is None:
            return None
        try:
            return getter(from_currency, to_currency)
        except Exception:  # noqa: BLE001 - an unresolvable rate is a rejection
            return None

'''

replace_span(
    "application/services/risk_service.py",
    "    async def _check_margin_requirement(",
    "    async def _publish_approval(self, order: Order) -> None:",
    NEW_CHECK,
    "_check_margin_requirement rewritten onto the MT5 engine (order_type was an enum, "
    "so .startswith() raised on every order)",
)

# ---------------------------------------------------------------------------
# 2. Group.calculate_margin delegates instead of re-deriving the formula
# ---------------------------------------------------------------------------

NEW_GROUP_MARGIN = '''    def calculate_margin(
        self,
        symbol_config: Dict[str, Any],
        volume: Decimal,
        price: Decimal,
        *,
        operation: str = "BUY",
        leverage: Optional[int] = None,
        deposit_currency: Optional[str] = None,
        rate_lookup: Optional[Any] = None,
        maintenance: bool = False,
    ) -> Decimal:
        """Required margin for a trade, via the MT5-accurate engine.

        This used to compute `(volume * contract_size * price * rate) / leverage`
        inline. That is the CFD formula, applied to every symbol: for Forex MT5's
        formula has no price term at all, so this over-charged EURUSD margin by ~1.1x,
        USDJPY by ~150x and BTCUSD by ~2000x. It also used
        `min(leverage_default, leverage_max)` as the effective leverage, which is not
        how MT5 resolves leverage, and always took the BUY margin rate regardless of
        side or order type.

        ``leverage`` should be the caller's resolved value (account -> group -> symbol
        cap); when omitted the group default applies, capped by leverage_max.
        """
        from core.domains.market_data.margin import (
            SymbolMarginSpec,
            apply_rate,
            basic_margin,
            convert_to_deposit,
        )

        spec = SymbolMarginSpec(
            name=str(symbol_config.get("name", "")),
            contract_size=Decimal(str(symbol_config.get("contract_size", 100000))),
            calc_mode=int(symbol_config.get("calc_mode", 0) or 0),
            margin_currency=str(
                symbol_config.get("margin_currency")
                or symbol_config.get("base_currency")
                or self.currency
                or ""
            ),
            margin_hedged=Decimal(str(symbol_config.get("margin_hedged", 0) or 0)),
            rates={
                key: Decimal(str(value))
                for key, value in symbol_config.items()
                if key.startswith(("initial_", "maintenance_")) and value is not None
            },
        )
        # Accept the legacy key names this method was always called with.
        for legacy, canonical in (
            ("margin_rate_initial_buy", "initial_buy"),
            ("margin_rate_initial_sell", "initial_sell"),
        ):
            if legacy in symbol_config and canonical not in spec.rates:
                spec.rates[canonical] = Decimal(str(symbol_config[legacy]))

        if leverage is None:
            leverage = self.margin.leverage_default or 1
            if self.margin.leverage_max and self.margin.leverage_max > 0:
                leverage = min(leverage, self.margin.leverage_max)

        basic = basic_margin(
            spec, volume, price, leverage=leverage, maintenance=maintenance
        )
        side = "BUY" if str(operation).upper().startswith("BUY") else "SELL"
        converted = convert_to_deposit(
            basic,
            margin_currency=spec.margin_currency,
            deposit_currency=deposit_currency or self.currency,
            side=side,
            rate_lookup=rate_lookup,
        )
        return apply_rate(converted, spec, str(operation).upper(), maintenance)

'''

replace_span(
    "core/domains/accounts/group.py",
    "    def calculate_margin(",
    "    def calculate_commission(",
    NEW_GROUP_MARGIN,
    "Group.calculate_margin delegates to the MT5 engine (it was applying the CFD "
    "formula to Forex symbols)",
)

# Group needs Optional/Any imported for the new signature.
text = load("core/domains/accounts/group.py")
work = text.replace("\r\n", "\n")
if "from typing import" in work:
    import re

    match = re.search(r"from typing import ([^\n]+)", work)
    names = {n.strip() for n in match.group(1).split(",")}
    names |= {"Optional", "Any"}
    work = work.replace(
        match.group(0), "from typing import " + ", ".join(sorted(names)), 1
    )
    save("core/domains/accounts/group.py", work, crlf="\r\n" in text)
    print("  ok  core/domains/accounts/group.py: typing imports widened")
