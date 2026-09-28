#!/usr/bin/env python3
"""D16 patch: the valuation sweep writes the POSITIONS, not only the account.

The defect, measured live on Neon (24 of 45 accounts): _revalue_one computed
each position's PnL from live prices, summed it into account.equity - and
never touched the position rows, which kept profit=0 / price_current NULL.
equity - balance != SUM(open profit): the sweep built to make stored values
trustworthy was manufacturing the very inconsistency it exists to remove
(D13's class, in the sweep instead of the tick pipeline).

The fix mirrors D15's rule in the tick pipeline:
  * write the position row FIRST through the column-scoped
    update_valuation (atomic, computes profit in SQL from the row's own
    volume at write time, refuses closed rows, hands back what it wrote);
  * the account total is the sum of WHAT WAS WRITTEN - or, where nothing was
    written (no price / failed write / MOCK-over-live skip), the row's STORED
    profit, preserved rather than dropped;
  * a position closed mid-sweep is excluded entirely - its close already
    booked the realised PnL into the balance;
  * a MOCK-labelled tick never re-values a position that already carries a
    real price_current (restarting with MARKET_DATA_SOURCE=mock must not
    degrade live-valued rows to fiction).

The invariant becomes structural: after a sweep,
    account.equity - account.balance == SUM(open positions' stored profit)
on EVERY branch.

_price_for gains the tick's source label as a third element (its only caller
is this loop).

Idempotent; run from the bp root.
"""
import os
import sys

path = os.path.join(os.getcwd(), "application", "services", "reconciliation_service.py")
src = open(path, encoding="utf-8", newline="").read()
if "D16" in src and "pos_setter" in src:
    print("already applied")
    sys.exit(0)

OLD_LOOP = '''        total_pnl = Decimal("0")
        priced_any = False
        for p in positions:
            price = self._price_for(getattr(p, "symbol", ""))
            if price is None:
                stats["skipped_no_price"] += 1
                continue
            bid, ask = price
            symbol = await self._symbol(getattr(p, "symbol", ""))
            contract = Decimal(str(getattr(symbol, "contract_size", 1) or 1)) if symbol else Decimal("1")
            action = getattr(p, "action", None)
            side = str(getattr(action, "value", action) or "BUY").upper()
            quote_ccy = str(getattr(symbol, "quote_currency", "") or "") if symbol else ""
            try:
                total_pnl += position_pnl(
                    side=side,
                    volume_lots=getattr(getattr(p, "volume", None), "value", Decimal("0")),
                    open_price=getattr(getattr(p, "price_open", None), "value", Decimal("0")),
                    bid=bid, ask=ask, contract_size=contract,
                    quote_currency=quote_ccy,
                    deposit_currency=getattr(account, "currency", "USD"),
                    rate_lookup=(self.risk_engine._rate_lookup
                                 if self.risk_engine is not None else None),
                )
                priced_any = True
            except (MarginCalculationError, ArithmeticError, ValueError, TypeError) as exc:
                stats["skipped_no_price"] += 1
                logger.warning("cannot value position %s: %s",
                               getattr(p, "position_id", "?"), exc)'''

NEW_LOOP = '''        total_pnl = Decimal("0")
        priced_any = False
        # D16: the position rows are written FIRST, and the account's total is
        # derived from what was ACTUALLY WRITTEN - the tick pipeline's D13/D15
        # rule, applied to the sweep. Before this fix the sweep computed each
        # PnL, wrote only account.equity, and left the rows at profit=0 /
        # price_current NULL: 24 of 45 live accounts ended up where
        # equity - balance != SUM(open profit). The invariant is now
        # structural: every open position's STORED profit enters the account
        # total - revalued (what the writer returned), preserved (no price,
        # failed write, MOCK-over-live skip) or excluded (closed mid-sweep:
        # the close already booked its realised PnL into the balance).
        pos_setter = getattr(self.position_repo, "update_valuation", None)
        if pos_setter is None:
            logger.warning(
                "position repository exposes no update_valuation; this sweep can "
                "only compute the account side (the D16 shape). Acceptable for "
                "in-memory doubles; unacceptable for a SQL deployment."
            )
        for p in positions:
            stored_profit = getattr(getattr(p, "profit", None), "amount", Decimal("0")) or Decimal("0")
            price = self._price_for(getattr(p, "symbol", ""))
            if price is None:
                stats["skipped_no_price"] += 1
                # preserve the row's truth: dropping an unpriced position's
                # stored profit would silently zero it out of the equity
                total_pnl += stored_profit
                continue
            bid, ask, source = price
            if source == "MOCK" and getattr(p, "price_current", None) is not None:
                # a MOCK tick must never degrade a position a real price has
                # already valued (e.g. the server restarted with
                # MARKET_DATA_SOURCE=mock). Fiction is allowed to value only
                # what holds nothing real yet.
                stats["skipped_mock_over_live"] = stats.get("skipped_mock_over_live", 0) + 1
                total_pnl += stored_profit
                continue
            symbol = await self._symbol(getattr(p, "symbol", ""))
            contract = Decimal(str(getattr(symbol, "contract_size", 1) or 1)) if symbol else Decimal("1")
            action = getattr(p, "action", None)
            side = str(getattr(action, "value", action) or "BUY").upper()
            quote_ccy = str(getattr(symbol, "quote_currency", "") or "") if symbol else ""

            if pos_setter is not None:
                try:
                    written = await pos_setter(
                        getattr(p, "position_id", ""),
                        side,
                        # MT5 valuation rule (same as the tick pipeline): a long
                        # is valued at the price it can SELL at (bid), a short
                        # at the price it can BUY BACK at (ask).
                        bid if side.startswith("BUY") else ask,
                    )
                except Exception as exc:  # noqa: BLE001
                    logger.error(
                        "sweep could not revalue position %s: %s - keeping its "
                        "stored profit rather than writing the account side alone",
                        getattr(p, "position_id", "?"), exc,
                    )
                    stats["positions_write_failed"] = stats.get("positions_write_failed", 0) + 1
                    total_pnl += stored_profit
                    continue
                if written is None:
                    # closed between the sweep's read and its write; its close
                    # already booked the realised PnL - any number here would
                    # be a double-count
                    stats["closed_mid_sweep"] = stats.get("closed_mid_sweep", 0) + 1
                    continue
                total_pnl += written["profit"]
                priced_any = True
                continue

            # legacy path (in-memory doubles without the column-scoped writer):
            # compute, and be honest that only the account side is written
            try:
                total_pnl += position_pnl(
                    side=side,
                    volume_lots=getattr(getattr(p, "volume", None), "value", Decimal("0")),
                    open_price=getattr(getattr(p, "price_open", None), "value", Decimal("0")),
                    bid=bid, ask=ask, contract_size=contract,
                    quote_currency=quote_ccy,
                    deposit_currency=getattr(account, "currency", "USD"),
                    rate_lookup=(self.risk_engine._rate_lookup
                                 if self.risk_engine is not None else None),
                )
                priced_any = True
            except (MarginCalculationError, ArithmeticError, ValueError, TypeError) as exc:
                stats["skipped_no_price"] += 1
                total_pnl += stored_profit
                logger.warning("cannot value position %s: %s",
                               getattr(p, "position_id", "?"), exc)'''

OLD_PRICE_TAIL = '''        if tick is None:
            return None
        if isinstance(tick, dict):
            bid, ask = tick.get("bid"), tick.get("ask")
        else:
            bid, ask = getattr(tick, "bid", None), getattr(tick, "ask", None)
        if bid is None or ask is None:
            return None
        try:
            return Decimal(str(bid)), Decimal(str(ask))
        except (ArithmeticError, ValueError, TypeError):
            return None'''

NEW_PRICE_TAIL = '''        if tick is None:
            return None
        if isinstance(tick, dict):
            bid, ask = tick.get("bid"), tick.get("ask")
            source = str(tick.get("source") or "")
        else:
            bid, ask = getattr(tick, "bid", None), getattr(tick, "ask", None)
            source = str(getattr(tick, "source", "") or "")
        if bid is None or ask is None:
            return None
        try:
            # D16: the source label rides along so the sweep can refuse to let
            # a MOCK tick overwrite a live-valued position
            return Decimal(str(bid)), Decimal(str(ask)), source
        except (ArithmeticError, ValueError, TypeError):
            return None'''

for old, new, tag in [(OLD_LOOP, NEW_LOOP, "loop"), (OLD_PRICE_TAIL, NEW_PRICE_TAIL, "price_for")]:
    if new in src:
        print(f"{tag}: already applied"); continue
    if old not in src:
        print(f"ANCHOR MISSING: {tag}"); sys.exit(1)
    src = src.replace(old, new, 1)
    print(f"{tag}: patched")

# docstring of _price_for: (bid, ask) -> (bid, ask, source)
src = src.replace('"""Best (bid, ask) we currently hold for a symbol, or None.',
                  '"""Best (bid, ask, source) we currently hold for a symbol, or None.')
open(path, "w", encoding="utf-8", newline="").write(src)
print("D16 patch complete")
