"""D2: /account/info and the manager UserGet must answer, or say they cannot.

Both routes asked the DI container for `account_info_query_handler`, which nothing
ever registered, so Depends() resolved to None. Both then swallowed the failure -
the client route with a bare `except Exception: pass`, the manager route with a
warning - and served numbers from somewhere else:

  * GET /api/v1/account/info returned the JWT snapshot, whose `margin_level` is
    the stale persisted column. A client at 9260% was told 0.0000%, which on a
    terminal reads as "stopped out".
  * GET .../UserGet read `account_info.login / .group_name / .margin` off a return
    value that is a DICT keyed `login_id / group / margin_used`. The AttributeError
    was caught and the endpoint returned THE MANAGER'S OWN balance and equity for a
    query about a client - HTTP 200, wrong account's money.

Three of the four reasons the handler was unreachable are pinned here; the fourth
(the missing DI registration) is covered by the live local E2E proof.
"""
from dataclasses import fields
from decimal import Decimal

import pytest
from fastapi import HTTPException

from api.routers.account import get_account_info
from api.routers.manager.main import user_get
from application.queries.get_account_info import (
    GetAccountInfoQuery,
    GetAccountInfoQueryHandler,
)
from application.queries.get_positions import GetPositionsQuery
from core.domains.accounts.account import MARGIN_LEVEL_UNLIMITED
from tests.integration.trading_harness import make_account, make_group


def _account(*, equity="10000", margin_used="0", balance="10000"):
    group = make_group()
    a = make_account(login=10001, group=group, balance=Decimal(balance))
    a.equity = Money_(equity, a.currency)
    a.margin_used = Money_(margin_used, a.currency)
    return a


def Money_(amount, currency):
    from core.domains.common.value_objects import Money
    return Money(Decimal(amount), currency)


class _Repo:
    def __init__(self, account):
        self._account = account

    async def find_by_login(self, login):
        if self._account is None or str(login) != str(self._account.login):
            return None
        return self._account


def _handler(account):
    return GetAccountInfoQueryHandler(account_repo=_Repo(account))


# --------------------------------------------------------------- drift guards

def test_the_info_query_speaks_the_same_vocabulary_as_its_sibling():
    """The routers pass `account_login=`; the field used to be `login_id`.

    That mismatch raised TypeError on every call and is why the handler was
    unreachable even once registered. Both read-side queries now agree.
    """
    info_fields = {f.name for f in fields(GetAccountInfoQuery)}
    positions_fields = {f.name for f in fields(GetPositionsQuery)}
    assert info_fields == positions_fields == {"account_login"}
    # and it is constructible exactly the way both routers construct it
    assert GetAccountInfoQuery(account_login=10001).account_login == 10001


def test_the_handler_uses_the_sentinel_when_flat_not_zero():
    """The handler had its own eighth copy of the formula, returning 0 when flat."""
    import asyncio
    result = asyncio.run(_handler(_account()).handle(GetAccountInfoQuery(account_login=10001)))
    assert result["margin_level"] == MARGIN_LEVEL_UNLIMITED


def test_the_handler_supplies_what_the_manager_schema_requires():
    import asyncio
    a = _account(equity="9999", margin_used="107.978")
    result = asyncio.run(_handler(a).handle(GetAccountInfoQuery(account_login=10001)))
    assert result["margin_level"] == (Decimal("9999") / Decimal("107.978")) * Decimal("100")
    assert "credit" in result and "leverage" in result
    assert result["leverage"] == a.effective_leverage()


# ------------------------------------------------------------ client contract

@pytest.mark.asyncio
async def test_client_info_answers_with_the_real_margin_level():
    a = _account(equity="9999", margin_used="107.978")
    resp = await get_account_info(current_user=a, handler=_handler(a))
    assert resp.margin_level == (Decimal("9999") / Decimal("107.978")) * Decimal("100")
    assert resp.margin_level != Decimal("0")
    assert resp.margin_used == Decimal("107.978")


@pytest.mark.asyncio
async def test_client_info_is_503_when_unwired_not_a_silent_snapshot():
    """`except Exception: pass` used to make "unwired" indistinguishable from data."""
    with pytest.raises(HTTPException) as ei:
        await get_account_info(current_user=_account(), handler=None)
    assert ei.value.status_code == 503


@pytest.mark.asyncio
async def test_client_info_is_500_when_the_handler_fails():
    class Boom:
        async def handle(self, query):
            raise RuntimeError("database on fire")

    with pytest.raises(HTTPException) as ei:
        await get_account_info(current_user=_account(), handler=Boom())
    assert ei.value.status_code == 500


@pytest.mark.asyncio
async def test_client_info_maps_an_unknown_login_to_404():
    with pytest.raises(HTTPException) as ei:
        await get_account_info(current_user=_account(), handler=_handler(None))
    assert ei.value.status_code == 404


# ----------------------------------------------------------- manager contract

@pytest.mark.asyncio
async def test_manager_userget_returns_the_queried_account_not_the_manager():
    """The regression that mattered: a manager asking about account 10001 used to
    receive the MANAGER'S OWN balance, because the AttributeError fallback below
    the warning built the response from `manager`."""
    client = _account(balance="10000", equity="9999", margin_used="107.978")
    manager = make_account(login=1000, group=make_group(), balance=Decimal("777"))

    resp = await user_get(login=10001, manager=manager, handler=_handler(client))

    assert resp.login == 10001
    assert resp.balance == Decimal("10000")
    assert resp.balance != Decimal("777"), "served the manager's own money"
    assert resp.margin == Decimal("107.978")
    assert resp.margin_level == (Decimal("9999") / Decimal("107.978")) * Decimal("100")


@pytest.mark.asyncio
async def test_manager_userget_is_503_when_unwired():
    manager = make_account(login=1000, group=make_group())
    with pytest.raises(HTTPException) as ei:
        await user_get(login=10001, manager=manager, handler=None)
    assert ei.value.status_code == 503


@pytest.mark.asyncio
async def test_manager_userget_maps_an_unknown_login_to_404():
    manager = make_account(login=1000, group=make_group())
    with pytest.raises(HTTPException) as ei:
        await user_get(login=99999, manager=manager, handler=_handler(None))
    assert ei.value.status_code == 404
