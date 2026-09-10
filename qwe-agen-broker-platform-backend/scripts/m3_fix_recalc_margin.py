"""
Step M3 part 19 - the fifth margin formula, in the deal-recording path.

`RecordDealHandler._recalculate_account_margin` called

    symbol.calculate_margin_required(position.volume.value, Decimal(str(current_price)))

`calculate_margin_required` is a method on POSITION, not on Symbol, so this raised
AttributeError for every position. It is the fifth independent copy of the margin formula
in the codebase:

    1. Group.calculate_margin              (volume * contract * price * rate) / leverage
    2. Position.calculate_margin_required  (volume * contract * price_open * rate) / lev
    3. RiskEngine.calculate_margin_level   (price * volume * contract) / leverage
    4. risk_service._check_margin_requirement  its own inline copy
    5. record_deal._recalculate_account_margin  a call to a method on the wrong class

Four of the five applied the CFD formula (with a price term) to every symbol, which
over-charges Forex margin by a factor of the price - ~150x on USDJPY, ~2000x on BTCUSD -
and none of them converted from the margin currency to the deposit currency.

This is the recalculation that runs after EVERY deal, and it sets account.margin_used and
account.margin_free: the two figures the stop-out logic reads. Because it raised, margin
was never updated after a trade, so the stored free margin went stale in whichever
direction it happened to be, and no stop-out could ever fire correctly.

Replaced with a single call into core.domains.market_data.margin, which carries MT5's
formulas, all four stages, and is tested against MT5's own published examples. Equity is
now balance + credit + unrealised PnL, matching MT5 and matching Account.update_equity;
the previous version used balance alone, so a client trading on broker credit looked
poorer than they were and would be stopped out early.
"""

from __future__ import annotations

import pathlib
import sys

ROOT = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else pathlib.Path.cwd()
REL = "application/commands/record_deal.py"
path = ROOT / REL
if not path.is_file():
    raise SystemExit(f"not found: {path}")

with open(path, encoding="utf-8", newline="") as fh:
    text = fh.read()
crlf = "\r\n" in text
work = text.replace("\r\n", "\n")

OLD = '''        for position in all_positions:
            if position.volume.value == 0:
                continue

            tick = await self.market_feed.get_latest_tick(position.symbol) if self.market_feed else None
            current_price = Decimal(tick['ask']) if (tick and isinstance(tick, dict) and 'ask' in tick) else getattr(tick, 'ask', position.price_open.value)

            symbol = await self.symbol_repo.find_by_name(position.symbol)
            if not symbol:
                continue

            position_margin = symbol.calculate_margin_required(
                position.volume.value,
                Decimal(str(current_price))
            )
            total_margin_used += position_margin

        currency = account.balance.currency
        account.margin_used = Money(total_margin_used, currency)
        account.margin_free = Money(account.balance.amount - total_margin_used, currency)'''

NEW = '''        # Margin is computed once for the whole account through the MT5-accurate engine,
        # not per position with a local formula. This used to call
        # symbol.calculate_margin_required(...), a method that exists on Position and not
        # on Symbol, so it raised for every position - and because this is the
        # recalculation that runs after every deal and writes account.margin_used /
        # margin_free, the figures the stop-out logic reads were never updated at all.
        from core.domains.market_data.margin import (
            Leg,
            MarginCalculationError,
            SymbolMarginSpec,
            calculate_account_margin,
        )
        from core.domains.risk.engine import RiskEngine

        legs = []
        specs = {}
        unrealized = Decimal("0")
        conversion = RiskEngine(symbol_repo=self.symbol_repo, market_data_engine=self.market_feed)

        for position in all_positions:
            if position.volume.value == 0:
                continue

            symbol = await self.symbol_repo.find_by_name(position.symbol)
            if not symbol:
                # A position in a symbol that is not configured cannot be margined. Log it
                # loudly rather than skipping it silently: skipping understates the
                # requirement and lets the account trade past its margin.
                logger.error(
                    "position %s is in unconfigured symbol %s; it cannot be margined",
                    position.position_id,
                    position.symbol,
                )
                continue

            spec = SymbolMarginSpec.from_symbol(symbol)
            specs[position.symbol] = spec

            tick = (
                await self.market_feed.get_latest_tick(position.symbol)
                if self.market_feed
                else None
            )
            bid = Decimal(str(tick["bid"])) if isinstance(tick, dict) and tick.get("bid") else None
            ask = Decimal(str(tick["ask"])) if isinstance(tick, dict) and tick.get("ask") else None
            if bid is None:
                bid = getattr(tick, "bid", None)
            if ask is None:
                ask = getattr(tick, "ask", None)

            action = (
                position.action.value if hasattr(position.action, "value") else str(position.action)
            )

            if bid and ask:
                from core.domains.market_data.margin import position_pnl

                try:
                    unrealized += position_pnl(
                        side=action,
                        volume_lots=position.volume.value,
                        open_price=position.price_open.value,
                        bid=Decimal(str(bid)),
                        ask=Decimal(str(ask)),
                        contract_size=spec.contract_size,
                        quote_currency=getattr(symbol, "quote_currency", "") or spec.margin_currency,
                        deposit_currency=account.currency,
                        rate_lookup=conversion._rate_lookup,
                    )
                except MarginCalculationError as exc:
                    logger.error(
                        "cannot value position %s (%s); equity will exclude it: %s",
                        position.position_id,
                        position.symbol,
                        exc,
                    )

            legs.append(
                Leg(
                    symbol=position.symbol,
                    operation=action,
                    volume=position.volume.value,
                    price=position.price_open.value,
                    is_pending=False,
                    spec=spec,
                )
            )

        if legs:
            breakdown = calculate_account_margin(
                legs,
                specs=specs,
                deposit_currency=account.currency,
                rate_lookup=conversion._rate_lookup,
                leverage=account.effective_leverage(),
                # Maintenance margin for positions already open. MT5: "When opening
                # positions, the initial margin is checked. For open positions, the
                # maintenance margin is checked."
                maintenance=True,
            )
            total_margin_used += breakdown.total

        currency = account.balance.currency
        # Equity is balance + credit + unrealised PnL, matching MT5 and matching
        # Account.update_equity. Using balance alone - as this did - ignores both broker
        # credit and open PnL, so a profitable account looked poorer than it was and a
        # client trading on credit was stopped out early.
        equity = account.balance.amount + account.credit.amount + unrealized
        account.margin_used = Money(total_margin_used, currency)
        account.margin_free = Money(equity - total_margin_used, currency)
        account.equity = Money(equity, currency)'''

if OLD not in work:
    raise SystemExit("[FAIL] record_deal.py: the _recalculate_account_margin body was not found")
work = work.replace(OLD, NEW, 1)

with open(path, "w", encoding="utf-8", newline="") as fh:
    fh.write(work.replace("\n", "\r\n") if crlf else work)
print(f"  ok  {REL}: margin recalculation goes through the MT5 engine (was a call to a method on the wrong class)")
