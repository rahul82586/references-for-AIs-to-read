"""D1 + D2 fix: margin_level was persisted-but-never-written, and /account/info
plus the manager UserGet were unreachable four different ways.

WHAT WAS WRONG
==============

D1 - `accounts.margin_level` is a real column, and three consumers read it:
     the MT5 routing context (RouteCondition.MARGIN_LEVEL), GET /account/info,
     and the manager UserGet. Every margin write path refreshes it -
     liquidation_worker, cancel_order, modify_order, modify_deal, and
     tick_margin_pipeline via Account.update_equity - EXCEPT record_deal, which
     is the path every fill takes. It set margin_used / margin_free / equity and
     stopped. The column kept its `default=0` forever.

     Because the routing context carried Decimal('0') rather than None, M8's
     "missing context => the condition does not match" guard never engaged: a
     MARGIN_LEVEL condition performed a real comparison against zero, so
     "reject if level < 200" rejected everything and "dealer if level < 500"
     always fired. Stop-out itself was safe (it reads the MarginSnapshot), which
     is why 422 tests passed.

D2 - GET /api/v1/account/info could not reach its handler for four independent
     reasons, each of which alone was sufficient:
       1. `account_info_query_handler` was never registered in the DI container,
          so the Depends() resolved to None and `if handler:` was always false.
       2. Both routers build `GetAccountInfoQuery(account_login=...)`, but the
          dataclass field is `login_id` -> TypeError on every call.
       3. The route wrapped the call in `except Exception: pass`, so 1 and 2 were
          invisible and the client silently got the JWT snapshot instead.
       4. The manager UserGet read `account_info.login / .group_name / .margin`
          off a return value that is a DICT keyed login_id / group / margin_used
          -> AttributeError -> caught -> and it then returned the MANAGER'S OWN
          balance and equity for a query about a client, with HTTP 200.

     This is the exact defect class M5 fixed on /account/positions (defects 14
     and 15). /info was missed, and it is the endpoint carrying the margin
     numbers.

WHAT THIS DOES
==============
  1. record_deal refreshes margin_level through Account.recompute_margin_level,
     the only place the formula lives.
  2. db_to_account DERIVES margin_level from equity / margin_used instead of
     reading the column, so a stale or defaulted column can never be served or
     routed on again. The column is still written, for external SQL consumers.
  3. GetAccountInfoQuery's field is renamed login_id -> account_login, matching
     its sibling GetPositionsQuery.
  4. The handler's own hand-rolled margin-level formula (the eighth copy, and it
     returned 0 rather than the MARGIN_LEVEL_UNLIMITED sentinel when flat) is
     replaced by core.domains.market_data.margin.margin_level.
  5. The handler also returns credit and leverage, which the manager schema
     requires and previously had no source for.
  6. account_info_query_handler is registered next to positions_query_handler.
  7. Both routes adopt the /positions contract: 503 when unwired, 500 with a
     logged traceback on error, 404 for an unknown login. Neither falls back to
     somebody else's numbers.

Idempotent: safe to re-run (already-patched anchors are detected and skipped).
"""
import ast
import io
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
sys.path.insert(0, ROOT)

applied = []
skipped = []


def patch(path, pairs, replace_all=False):
    src = io.open(path, encoding="utf-8", newline="").read()
    nl = "\r\n" if "\r\n" in src else "\n"
    changed = False
    for old, new in pairs:
        if nl == "\r\n":
            old = old.replace("\n", "\r\n")
            new = new.replace("\n", "\r\n")
        n = src.count(old)
        if n == 0:
            new_n = src.count(new)
            if new_n:
                skipped.append(f"{path}: already patched")
                continue
            raise AssertionError(f"{path}: anchor not found: {old[:90]!r}")
        if not replace_all and n != 1:
            raise AssertionError(f"{path}: anchor appears {n}x: {old[:90]!r}")
        src = src.replace(old, new) if replace_all else src.replace(old, new, 1)
        changed = True
    if changed:
        ast.parse(src.replace("\r\n", "\n"))
        io.open(path, "w", encoding="utf-8", newline="").write(src)
        applied.append(path)


# ---------------------------------------------------------------- 1. record_deal
patch("application/commands/record_deal.py", [(
    """        account.margin_used = Money(total_margin_used, currency)
        account.margin_free = Money(equity - total_margin_used, currency)
        account.equity = Money(equity, currency)
""",
    """        account.margin_used = Money(total_margin_used, currency)
        account.margin_free = Money(equity - total_margin_used, currency)
        account.equity = Money(equity, currency)
        # D1: margin_level is a PERSISTED column with three readers - the MT5
        # routing context (RouteCondition.MARGIN_LEVEL), /account/info and the
        # manager UserGet. Every other margin write path refreshes it; this one,
        # which is the path every fill takes, did not, so the column kept its
        # default 0 and routing money-conditions compared against zero.
        # recompute_margin_level is the only place the formula lives.
        account.recompute_margin_level()
""",
)])

# ------------------------------------------------------- 2. account_models read
patch("infrastructure/persistence/account_models.py", [
    (
        "from core.domains.common.value_objects import Money\n",
        "from core.domains.common.value_objects import Money\n"
        "from core.domains.market_data.margin import margin_level as compute_margin_level\n",
    ),
    (
        '    account.margin_level = _dec(model.margin_level, "0")\n',
        "    # D1, defence in depth: margin_level is DERIVED from equity / margin_used\n"
        "    # rather than read from the column. The column is still written (external\n"
        "    # SQL consumers read it), but the domain object never trusts it: a stale\n"
        "    # or defaulted 0 would be served to clients and, worse, handed to the\n"
        "    # routing engine as a real MARGIN_LEVEL comparison value instead of the\n"
        "    # None that M8's missing-context guard knows to skip.\n"
        "    account.margin_level = compute_margin_level(\n"
        "        account.equity.amount, account.margin_used.amount\n"
        "    )\n",
    ),
])

# ------------------------------------------------------- 3/4/5. the query side
patch("application/queries/get_account_info.py", [
    (
        "from core.ports.interfaces import IAccountRepository, IPositionRepository\n",
        "from core.domains.market_data.margin import margin_level as compute_margin_level\n"
        "from core.ports.interfaces import IAccountRepository, IPositionRepository\n",
    ),
    (
        '@dataclass(frozen=True)\nclass GetAccountInfoQuery:\n'
        '    """Query payload to fetch account financial snapshot."""\n'
        '    login_id: str\n',
        '@dataclass(frozen=True)\nclass GetAccountInfoQuery:\n'
        '    """Query payload to fetch account financial snapshot.\n'
        '\n'
        '    D2: the field was `login_id` while both routers passed `account_login=`,\n'
        '    so every construction raised TypeError - one of the four reasons this\n'
        '    handler was unreachable. Renamed to match its sibling GetPositionsQuery.\n'
        '    """\n'
        '    account_login: str\n',
    ),
    (
        "        # Calculate margin level percentage\n"
        "        if margin_used > Decimal('0'):\n"
        "            margin_level = (equity / margin_used) * Decimal('100')\n"
        "        else:\n"
        "            margin_level = Decimal('0')\n",
        "        # Single source of truth. This was the eighth hand-written copy of the\n"
        "        # formula, and it returned 0 when the account was flat - the exact\n"
        "        # \"reads as fully exhausted\" case MARGIN_LEVEL_UNLIMITED exists to\n"
        "        # prevent (see Account.recompute_margin_level's docstring).\n"
        "        margin_level = compute_margin_level(equity, margin_used)\n",
    ),
    (
        '        group_name = account.group.name if hasattr(account.group, \'name\') else str(account.group)\n'
        '        currency = account.balance.currency if hasattr(account.balance, \'currency\') else "USD"\n',
        '        group_name = account.group.name if hasattr(account.group, \'name\') else str(account.group)\n'
        '        currency = account.balance.currency if hasattr(account.balance, \'currency\') else "USD"\n'
        "        credit = account.credit.amount if hasattr(account.credit, 'amount') else Decimal(str(account.credit))\n"
        "        # The manager UserGet schema requires a leverage; it previously had no\n"
        "        # source for one, which is part of why it fell back to the manager's own\n"
        "        # account. effective_leverage() resolves account-then-group-then-100.\n"
        "        leverage = account.effective_leverage()\n",
    ),
    (
        '            "margin_level": margin_level,\n'
        '            "currency": currency,\n'
        "        }\n",
        '            "margin_level": margin_level,\n'
        '            "currency": currency,\n'
        '            "credit": credit,\n'
        '            "leverage": leverage,\n'
        "        }\n",
    ),
], replace_all=False)

# the login_id -> account_login rename occurs twice inside handle()
patch("application/queries/get_account_info.py",
      [("query.login_id", "query.account_login")], replace_all=True)

# ------------------------------------------------------------- 6. registration
patch("api/main.py", [
    (
        "            from application.queries.get_positions import GetPositionsQueryHandler\n",
        "            from application.queries.get_account_info import GetAccountInfoQueryHandler\n"
        "            from application.queries.get_positions import GetPositionsQueryHandler\n",
    ),
    (
        "                        market_data_engine=stack.market_data_engine,\n"
        "                        risk_engine=stack.risk_engine,\n"
        "                    )\n"
        "                }\n"
        "            )\n",
        "                        market_data_engine=stack.market_data_engine,\n"
        "                        risk_engine=stack.risk_engine,\n"
        "                    ),\n"
        "                    # D2: /account/info and the manager UserGet both ask the\n"
        "                    # container for this key. Nothing ever registered it, so\n"
        "                    # Depends() resolved to None and both routes silently served\n"
        "                    # whatever the JWT happened to carry.\n"
        '                    "account_info_query_handler": GetAccountInfoQueryHandler(\n'
        "                        account_repo=container.resolve(IAccountRepository),\n"
        "                        position_repo=container.resolve(IPositionRepository),\n"
        "                        market_data_engine=stack.market_data_engine,\n"
        "                    ),\n"
        "                }\n"
        "            )\n",
    ),
])

# ------------------------------------------------------- 7a. client /info route
patch("api/routers/account.py", [(
    """    login_val = current_user.login if hasattr(current_user, 'login') else getattr(current_user, 'login_id', 100001)
    if handler:
        try:
            query = GetAccountInfoQuery(account_login=login_val)
            result = await handler.handle(query)
            return AccountInfo(**result)
        except Exception:
            pass

    return AccountInfo(
        login_id=str(login_val),
        group=current_user.group.name if hasattr(current_user, 'group') and current_user.group else "REAL_STANDARD",
        balance=current_user.balance.amount,
        equity=current_user.equity.amount,
        margin_used=current_user.margin_used.amount,
        margin_free=current_user.margin_free.amount,
        margin_level=current_user.margin_level,
        currency=current_user.currency,
    )
""",
    """    login_val = current_user.login if hasattr(current_user, 'login') else getattr(current_user, 'login_id', 100001)
    # D2: this endpoint is the client's view of its own margin. It used to swallow
    # every failure into `except Exception: pass` and fall back to the JWT
    # snapshot, whose margin_level is a stored column - so a client at 9260% was
    # told 0.0000%, which reads as "stopped out". Same contract as /positions
    # (M5 defects 14/15): unwired is a 503, an error is a 500 with a traceback,
    # and a stale snapshot is never a substitute for the real numbers.
    if handler is None:
        logger.error("account_info_query_handler is not registered; /account/info cannot answer")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Account info query is not wired on this server",
        )
    try:
        result = await handler.handle(GetAccountInfoQuery(account_login=login_val))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception:
        logger.exception("get_account_info failed for login=%s", login_val)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not read account information",
        )
    return AccountInfo(**result)
""",
)])

# ------------------------------------------------------- 7b. manager UserGet
patch("api/routers/manager/main.py", [(
    """    if handler:
        try:
            query = GetAccountInfoQuery(account_login=login)
            account_info = await handler.handle(query)
            return AccountInfo(
                login=account_info.login,
                group=account_info.group_name,
                currency=account_info.currency,
                balance=account_info.balance,
                equity=account_info.equity,
                margin=account_info.margin,
                free_margin=account_info.free_margin,
                margin_level=account_info.margin_level,
                leverage=account_info.leverage,
            )
        except Exception as e:
            logger.warning(f"Query handler failed, falling back to manager account state: {e}")

    # Fallback to manager account data for standalone API testing
    return AccountInfo(
        login=manager.login,
        group=manager.group.name if manager.group else "REAL_STANDARD",
        currency=manager.currency,
        balance=manager.balance.amount,
        equity=manager.equity.amount,
        margin=manager.margin_used.amount,
        free_margin=manager.margin_free.amount,
        margin_level=manager.margin_level,
        leverage=manager.effective_leverage(),
    )
""",
    """    # D2: this read `account_info.login / .group_name / .margin` off a return
    # value that is a DICT keyed login_id / group / margin_used. The resulting
    # AttributeError was caught, logged as a warning, and the endpoint then
    # returned the MANAGER'S OWN balance and equity for a query about a client -
    # HTTP 200, wrong account's money. There is no fallback: a manager asking
    # about account N must get account N or an error.
    if handler is None:
        logger.error("account_info_query_handler is not registered; UserGet cannot answer")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Account query is not wired on this server",
        )
    try:
        info = await handler.handle(GetAccountInfoQuery(account_login=login))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception:
        logger.exception("UserGet failed for login=%s", login)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not read account information",
        )
    return AccountInfo(
        login=int(info["login_id"]),
        group=info["group"],
        currency=info["currency"],
        balance=info["balance"],
        credit=info["credit"],
        equity=info["equity"],
        margin=info["margin_used"],
        free_margin=info["margin_free"],
        margin_level=info["margin_level"],
        leverage=info["leverage"],
    )
""",
)])

print(f"applied to {len(set(applied))} file(s):")
for f in sorted(set(applied)):
    print("  ", f)
for s in skipped:
    print("  skipped:", s)
