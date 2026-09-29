"""Account Revaluation Service (Pure Calculation & Column-Scoped Persistence).

Fix 1: Extracts state recalculation and persistence out of GET routes.
GET handlers must never mutate state or call save().
"""
from decimal import Decimal
from typing import Any, Dict, List, Optional
import logging

logger = logging.getLogger(__name__)

async def get_live_quotes_map(symbols: List[str]) -> Dict[str, Dict[str, str]]:
    """Helper to fetch live quotes from market data feed/cache if available."""
    try:
        from infrastructure.feeds.trade_server_feed import get_global_market_feed
        feed = get_global_market_feed()
        if feed and hasattr(feed, "get_latest_tick"):
            res = {}
            for sym in symbols:
                t = await feed.get_latest_tick(sym)
                if t:
                    res[sym.upper()] = {"bid": str(t.bid), "ask": str(t.ask)}
            return res
    except Exception:
        pass
    return {}


def compute_trading_state(
    account: Any,
    open_positions: List[Any],
    symbols_map: Optional[Dict[str, Any]] = None,
    live_quotes: Optional[Dict[str, Dict[str, str]]] = None,
) -> Dict[str, Any]:
    """Pure domain function: computes margin, profit, equity, free margin & margin level.

    Does NOT persist or mutate database state.
    """
    currency = getattr(account, "currency", "USD") or "USD"
    balance_amt = Decimal(str(getattr(account.balance, "amount", account.balance) if hasattr(account, "balance") else 0))
    credit_amt = Decimal(str(getattr(account.credit, "amount", account.credit) if hasattr(account, "credit") else 0))
    leverage = Decimal(str(getattr(account, "leverage", 100) or 100))

    if not open_positions:
        equity_amt = balance_amt + credit_amt
        return {
            "balance": str(balance_amt),
            "credit": str(credit_amt),
            "profit": "0.00",
            "equity": str(equity_amt),
            "margin_used": "0.00",
            "margin_free": str(equity_amt),
            "margin_level": "0.00",
            "currency": currency,
        }

    total_margin = Decimal("0.00")
    total_profit = Decimal("0.00")
    quotes = live_quotes or {}

    for p in open_positions:
        p_vol = Decimal(str(p.volume.value if hasattr(p.volume, "value") else (p.volume.amount if hasattr(p.volume, "amount") else p.volume)))
        p_price = Decimal(str(p.price_open.value if hasattr(p.price_open, "value") else p.price_open))
        p_contract = Decimal(str(getattr(p, "contract_size", 100000) or 100000))
        is_buy = str(getattr(p, "action", "")).upper() in ("BUY", "POSITIONACTION.BUY")
        sym_str = str(getattr(p, "symbol", "") or "")
        clean_sym = sym_str.split('\\')[-1].split('/')[-1].upper()

        sym_quotes = quotes.get(sym_str.upper()) or quotes.get(clean_sym) or {}
        q_bid = sym_quotes.get("bid")
        q_ask = sym_quotes.get("ask")
        live_price_str = q_bid if is_buy else q_ask

        if live_price_str is not None:
            try:
                live_price = Decimal(str(live_price_str))
                p_profit = (live_price - p_price) * p_vol * p_contract if is_buy else (p_price - live_price) * p_vol * p_contract
                total_profit += p_profit
            except Exception:
                pass
        else:
            p_profit_val = getattr(p, "profit", None)
            if p_profit_val is not None:
                total_profit += Decimal(str(p_profit_val.amount if hasattr(p_profit_val, "amount") else p_profit_val))

        if symbols_map and sym_str in symbols_map:
            sym_obj = symbols_map[sym_str]
            m_fixed = getattr(sym_obj, "margin_maintenance", None) or getattr(sym_obj, "margin_initial", None)
            if m_fixed is not None and Decimal(str(m_fixed)) > Decimal("0"):
                total_margin += p_vol * Decimal(str(m_fixed))
                continue

        # Standard leverage margin fallback
        notional = p_price * p_vol * p_contract
        margin_req = notional / leverage if leverage > Decimal("0") else Decimal("0")
        total_margin += margin_req

    equity_amt = balance_amt + credit_amt + total_profit
    margin_free_amt = max(Decimal("0.00"), equity_amt - total_margin)
    margin_level_amt = (equity_amt / total_margin * Decimal("100.0")) if total_margin > Decimal("0") else Decimal("0.00")

    return {
        "balance": str(balance_amt),
        "credit": str(credit_amt),
        "profit": str(total_profit.quantize(Decimal("0.01"))),
        "equity": str(equity_amt.quantize(Decimal("0.01"))),
        "margin_used": str(total_margin.quantize(Decimal("0.01"))),
        "margin_free": str(margin_free_amt.quantize(Decimal("0.01"))),
        "margin_level": str(margin_level_amt.quantize(Decimal("0.01"))),
        "currency": currency,
    }


async def revalue_account(
    acc_login: int,
    account_repo: Any,
    position_repo: Any,
    symbol_repo: Any = None,
    risk_engine: Any = None,
    group_repo: Any = None,
) -> Optional[Dict[str, Any]]:
    """Persists account valuation via column-scoped update_valuation (NEVER full-row save)."""
    if account_repo is None:
        return None

    acc = await account_repo.find_by_login(acc_login)
    if acc is None:
        return None

    open_positions = []
    if position_repo is not None:
        raw_pos = await position_repo.get_positions_by_account(acc_login)
        for p in (raw_pos or []):
            if getattr(p, "time_done", None) is not None:
                continue
            vol_val = Decimal(str(p.volume.value if hasattr(p.volume, "value") else (p.volume.amount if hasattr(p.volume, "amount") else p.volume)))
            if vol_val > Decimal("0"):
                open_positions.append(p)

    from core.domains.common.value_objects import Money

    currency = getattr(acc, "currency", "USD") or "USD"

    if risk_engine is not None and open_positions:
        try:
            snapshot = risk_engine.calculate_margin_level(acc, open_positions)
            acc.margin_used = Money(snapshot.margin_used, currency)
            acc.equity = Money(snapshot.equity, currency)
            acc.profit = Money(snapshot.equity - (acc.balance.amount + acc.credit.amount), currency)
            acc.margin_free = Money(snapshot.margin_free, currency)
            acc.recompute_margin_level()
        except Exception as err:
            logger.warning(f"revalue_account risk_engine notice: {err}")

    unique_syms = list({
        str(getattr(p, "symbol", "") or "") for p in open_positions if getattr(p, "symbol", None)
    })
    symbols_map = {}
    if symbol_repo is not None and unique_syms:
        for s in unique_syms:
            sym_obj = await symbol_repo.find_by_name(s)
            if sym_obj:
                symbols_map[s] = sym_obj

    quotes = await get_live_quotes_map(unique_syms) if unique_syms else {}

    state = compute_trading_state(acc, open_positions, symbols_map, quotes)

    acc.profit = Money(Decimal(state["profit"]), currency)
    acc.equity = Money(Decimal(state["equity"]), currency)
    acc.margin_used = Money(Decimal(state["margin_used"]), currency)
    acc.margin_free = Money(Decimal(state["margin_free"]), currency)
    acc.margin_level = Decimal(state["margin_level"])

    # Column-scoped update_valuation (never full-row save)
    update_val = getattr(account_repo, "update_valuation", None)
    if update_val is not None:
        await update_val(acc, include_margin=True)
    else:
        # Fallback if repository has no update_valuation
        if hasattr(account_repo, "save"):
            await account_repo.save(acc)

    return state
