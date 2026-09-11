"""Margin reservation helpers (M6, M4 debt #1).

Between a risk approval and the fill being booked there was no hold on the
account's free margin. On one node with the in-process bus the orchestrator
runs inline and the window is closed; across a Redis bus - or across two API
nodes - two concurrent orders could both pass the same free-margin check and
both book, leveraging the account past its limit.

The fix has two halves:

* an ATOMIC conditional UPDATE in the SQL repository
  (`reserve_margin`: increment only while free margin still covers it - one
  statement, so two nodes cannot both win), and
* these helpers, which every reserve/release site goes through. They prefer
  the repository's atomic method and fall back to mutating the in-memory
  account (correct on one node under the per-account lock) when a test double
  or an older repository does not implement it - loudly, never silently.

In-flight state lives in two columns: `accounts.margin_reserved` (the account's
total hold) and `orders.reserved_margin` (how much THIS order holds, so the
release is exact). The pre-trade margin check subtracts the account's reserved
total from availability, so a second concurrent order sees the first one's
hold whether or not it has filled yet.

Known residual (documented, not hidden): a full-row `account_repo.save()`
concurrent with another node's reservation can still resurrect stale values on
OTHER columns - that is the repository design, not the reservation; single-
writer-per-account flows (the per-account lock, the UoW) are consistent.
A node crash between approval and terminal state strands a reservation until
the order is closed out; an ops sweep for stale PLACED orders is the M7+
answer (nothing silently frees margin here).
"""
import inspect
import logging
from decimal import Decimal, InvalidOperation
from typing import Any, Optional

logger = logging.getLogger(__name__)

#: distinguishes "repository does not implement this" from "returned None"
_UNSUPPORTED = object()


def _dec(value: Any) -> Decimal:
    try:
        return Decimal(str(value))
    except (InvalidOperation, ValueError, TypeError):
        return Decimal("0")


def _set_local(account: Any, total: Any) -> None:
    """SET the in-flight object's hold from the repository's authoritative total.

    Setting (not adding) is what makes the helper safe for BOTH repository
    kinds: a SQL repo updates a row the caller cannot see (the object is
    stale), while an in-memory double mutates the very same object the caller
    holds (adding would double-count).
    """
    from core.domains.common.value_objects import Money

    account.margin_reserved = Money(
        max(Decimal("0"), _dec(total)), getattr(account, "currency", "USD")
    )


def _add_local(account: Any, delta: Decimal) -> None:
    """Fallback path only (repo without reservation support): mutate under the
    caller's per-account lock."""
    from core.domains.common.value_objects import Money

    current = _dec(getattr(getattr(account, "margin_reserved", None), "amount", 0))
    account.margin_reserved = Money(
        max(Decimal("0"), current + delta), getattr(account, "currency", "USD")
    )


def _accepts_session(method: Any) -> bool:
    try:
        return "session" in inspect.signature(method).parameters
    except (TypeError, ValueError):
        return False


async def reserve_margin(account_repo: Any, account: Any, amount: Any) -> bool:
    """Hold `amount` of free margin for an in-flight order. True when held."""
    amount = _dec(amount)
    if amount <= 0:
        return True
    if account_repo is None:
        logger.warning(
            "no account repository in scope; margin of %s approved WITHOUT an "
            "atomic hold (safe on one node under the account lock, not across nodes)",
            amount,
        )
        _add_local(account, amount)
        return True

    method = getattr(account_repo, "reserve_margin", None)
    if method is not None:
        try:
            new_total = await method(account.login, amount)
        except NotImplementedError:
            new_total = _UNSUPPORTED
        if new_total is not _UNSUPPORTED:
            if new_total is None:
                return False  # refused: free margin no longer covers it
            _set_local(account, new_total)
            return True

    # In-process fallback: the caller holds the per-account lock, so this is
    # correct on a single node.
    free = _dec(getattr(getattr(account, "margin_free", None), "amount", 0))
    reserved = _dec(getattr(getattr(account, "margin_reserved", None), "amount", 0))
    if free - reserved < amount:
        return False
    _add_local(account, amount)
    return True


async def release_margin(
    account_repo: Any,
    login: Any,
    amount: Any,
    account: Any = None,
    session: Any = None,
) -> None:
    """Release a hold placed by reserve_margin (on fill or rejection)."""
    amount = _dec(amount)
    if amount <= 0:
        return

    method = getattr(account_repo, "release_margin", None) if account_repo else None
    if method is not None:
        try:
            if session is not None and _accepts_session(method):
                new_total = await method(login, amount, session=session)
            else:
                new_total = await method(login, amount)
        except NotImplementedError:
            new_total = _UNSUPPORTED
        if new_total is not _UNSUPPORTED:
            if new_total is None:
                logger.warning(
                    "release of %s for account %s matched no row", amount, login
                )
            elif account is not None:
                _set_local(account, new_total)
            return

    if account is not None:
        _add_local(account, -amount)
    else:
        logger.warning(
            "cannot release the margin reservation of %s for account %s: the "
            "repository does not support it and no account object is in scope",
            amount, login,
        )
