"""D11 - give the client the three trade routes it never had.

WHAT WAS THERE
==============
`api/routers/trade.py` had three routes. One was real, two were theatre, and the
one that mattered most did not exist:

    POST   /api/v1/trade/orders                real
    PUT    /api/v1/trade/orders/{id}           -> {"status":"modified"}   touched nothing
    DELETE /api/v1/trade/orders/{id}           -> {"status":"cancelled"}  touched nothing
    (close a position)                         no such route

Which is why the live Neon database reads:

    deals by entry : IN 31        <- and nothing else
    positions      : OPEN 31, CLOSED 0
    deal_close set : 0

The report this answers - "only IN deals were visible, no OUT deal" - was not a
broken close. There was no client-facing close to break. `ClosePositionHandler`
works (D10 fixed its margin release and its `price_current` dereference), and
`ModifyOrderHandler` / `CancelOrderHandler` are both complete. None of the three was
reachable from a client: only `close_position_handler` was registered in the DI
container, and only the MANAGER OrderClose endpoint used it.

Same class as D2 (`/account/info` serving a JWT snapshot because its handler was
never registered) and the M4 `FallbackCreateOrderHandler` that answered every order
with a mock FILLED ticket. A 200 with a plausible body over absent behaviour is
worse than a 501, because the client believes the trade happened.

WHAT THIS DOES
==============
Registers the two missing handlers in the trading stack, and replaces all three
routes with real ones:

    POST   /api/v1/trade/positions/{position_id}/close   full or partial close
    PUT    /api/v1/trade/orders/{ticket_id}              modify a pending order
    DELETE /api/v1/trade/orders/{ticket_id}              cancel a pending order

Every route follows the contract M5 established on /account/positions:
  no handler registered -> 503 with a logged error. A misconfigured server must not
                           look like a healthy one.
  ValueError            -> 404 if it says "not found", else 400 with the reason.
  anything else         -> 500, traceback logged.
  never a silent fallback, never a success body for work not done.

Ownership is enforced on all three: `account_login` comes from the authenticated
token, never from the request body, so one client cannot close or modify another's
position by guessing an id. The handlers check that login against the record they
load.

Close is POST-with-body rather than DELETE, because a partial close carries a volume
and DELETE-with-body is not reliably supported by clients or proxies. DELETE stays
for cancelling a resting order, which is what it always meant.

Idempotent: each anchor is applied once; a re-run detects the new text and skips.
Proven by tests/integration/test_d11_client_trade_routes.py (10 tests) over real
HTTP against a whole in-memory broker.
"""
import ast
import io
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
sys.path.insert(0, ROOT)

PATCHES = {
    "api/routers/trade.py": [
        (
'Architectural Rule: Invokes Application Command Handlers, zero direct DB access.\r\n"""\r\nfrom decimal import Decimal\r\nfrom datetime import datetime, timezone\r\nfrom fastapi import APIRouter, Depends, HTTPException, status\r\n\r\nfrom api.auth.dependencies import get_current_user\r\nfrom api.di_providers import get_create_order_handler\r\nfrom api.schemas.trade import ModifyOrderRequest, OrderRequest, OrderResponse\r\nfrom application.commands.create_order import CreateOrderCommand, CreateOrderCommandHandler\r\nfrom core.domains.accounts.models import Account\r\n\r\nrouter = APIRouter(prefix="/api/v1/trade", tags=["Trade"])\r\n\r\n\r',
'Architectural Rule: Invokes Application Command Handlers, zero direct DB access.\r\n"""\r\nimport logging\r\nfrom datetime import datetime, timezone\r\nfrom decimal import Decimal\r\nfrom typing import Any, Optional\r\n\r\nfrom fastapi import APIRouter, Depends, HTTPException, status\r\nfrom pydantic import BaseModel, Field\r\n\r\nfrom api.auth.dependencies import get_current_user\r\nfrom api.di_providers import get_create_order_handler\r\nfrom api.schemas.trade import ModifyOrderRequest, OrderRequest, OrderResponse\r\nfrom application.commands.cancel_order import CancelOrderCommand\r\nfrom application.commands.close_position import ClosePositionCommand\r\nfrom application.commands.create_order import CreateOrderCommand, CreateOrderCommandHandler\r\nfrom application.commands.modify_order import ModifyOrderCommand\r\nfrom core.domains.accounts.models import Account\r\n\r\nlogger = logging.getLogger(__name__)\r\n\r\nrouter = APIRouter(prefix="/api/v1/trade", tags=["Trade"])\r\n\r\n\r\n# ------------------------------------------------------------------ D11 schemas\r\n\r\nclass ClosePositionRequest(BaseModel):\r\n    """Client request to close an open position, fully or partly."""\r\n\r\n    #: omit for a full close\r\n    volume: Optional[Decimal] = Field(None, gt=0, description="Lots to close; omit = all")\r\n    #: omit to close at market\r\n    price: Optional[Decimal] = Field(None, gt=0)\r\n    comment: str = ""\r\n\r\n\r\nclass ClosePositionResponse(BaseModel):\r\n    position_id: str\r\n    symbol: str\r\n    volume_closed: Decimal\r\n    volume_remaining: Decimal\r\n    close_price: Decimal\r\n    realized_pnl: Decimal\r\n    deal_id: str\r\n    fully_closed: bool\r\n    message: str = "Position closed"\r\n\r\n\r\nclass OrderActionResponse(BaseModel):\r\n    """The truthful result of a modify or a cancel."""\r\n\r\n    status: str\r\n    ticket_id: str\r\n    order_state: str\r\n    price: Optional[str] = None\r\n    stop_loss: Optional[str] = None\r\n    take_profit: Optional[str] = None\r\n    volume_current: Optional[str] = None\r\n    comment: Optional[str] = None\r\n\r\n\r\n# ----------------------------------------------------------------- D11 helpers\r\n\r\ndef _handler(key: str, what: str) -> Any:\r\n    """Resolve a command handler, or 503.\r\n\r\n    An unwired handler must be a loud server error, never a route that quietly\r\n    returns a hardcoded body - which is precisely what the stubs below used to do.\r\n    """\r\n    from api.di_providers import _container  # local import: avoids a cycle\r\n\r\n    handler = _container.get(key)\r\n    if handler is None:\r\n        logger.error("%s is not registered; the trading plane is not wired", key)\r\n        raise HTTPException(\r\n            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,\r\n            detail=f"{what} is not available on this server",\r\n        )\r\n    return handler\r\n\r\n\r\ndef _login_of(account: Account) -> int:\r\n    """The authenticated login - never taken from a request body.\r\n\r\n    Ownership is enforced by threading this into every command: a client cannot\r\n    close or modify another client\\\'s position by guessing an id, because the\r\n    handler checks the login it is given against the order/position it loads.\r\n    """\r\n    login = getattr(account, "login_id", None) or getattr(account, "login", None)\r\n    try:\r\n        return int(login)\r\n    except (TypeError, ValueError):\r\n        raise HTTPException(\r\n            status_code=status.HTTP_401_UNAUTHORIZED,\r\n            detail="Could not resolve the authenticated account",\r\n        )\r\n\r\n\r\ndef _domain_error_to_http(exc: ValueError, what: str) -> HTTPException:\r\n    """Map a domain refusal onto 404 vs 400 by what it says."""\r\n    msg = str(exc)\r\n    code = (status.HTTP_404_NOT_FOUND if "not found" in msg.lower()\r\n            else status.HTTP_400_BAD_REQUEST)\r\n    return HTTPException(status_code=code, detail=f"{what}: {msg}")\r\n\r\n\r\ndef _dec(value: Any) -> Optional[str]:\r\n    """A Money/Quantity/value-object, or a bare number, as a string."""\r\n    v = getattr(value, "value", value)\r\n    return str(v) if v is not None else None\r\n\r\n\r\ndef _order_response(order: Any, action: str) -> OrderActionResponse:\r\n    state = getattr(getattr(order, "state", None), "value", None) or str(\r\n        getattr(order, "state", ""))\r\n    return OrderActionResponse(\r\n        status=action,\r\n        ticket_id=str(getattr(order, "ticket_id", "")),\r\n        order_state=str(state),\r\n        price=_dec(getattr(order, "price_order", None)),\r\n        stop_loss=_dec(getattr(order, "price_sl", None)),\r\n        take_profit=_dec(getattr(order, "price_tp", None)),\r\n        volume_current=_dec(getattr(order, "volume_current", None)),\r\n        comment=getattr(order, "comment", None),\r\n    )\r\n\r\n\r',
        ),
        (
'\r\n\r\n@router.put("/orders/{ticket_id}")\r\nasync def modify_order(\r\n    ticket_id: str,\r',
'\r\n\r\n@router.post("/positions/{position_id}/close", response_model=ClosePositionResponse)\r\nasync def close_position(\r\n    position_id: str,\r\n    request: ClosePositionRequest,\r\n    current_user: Account = Depends(get_current_user)\r\n):\r\n    """Close an open position, fully or partly, and book the OUT deal.\r\n\r\n    This route did not exist, which is why the database held 31 IN deals and no OUT\r\n    deals. It drives the same ClosePositionHandler the SL/TP worker, the liquidation\r\n    worker and the manager OrderClose endpoint use, so a client close produces\r\n    exactly the same deal, position and margin treatment as a server-side one -\r\n    including D10\'s margin release.\r\n\r\n    POST with a body rather than DELETE, because a partial close carries a volume and\r\n    DELETE-with-body is not reliably supported by clients and proxies. DELETE stays\r\n    for cancelling a resting order, which is what it always meant.\r\n    """\r\n    handler = _handler("close_position_handler", "Position closing")\r\n    login = _login_of(current_user)\r\n\r\n    try:\r\n        position = await handler.handle(ClosePositionCommand(\r\n            account_login=login,\r\n            position_id=position_id,\r\n            volume=request.volume,\r\n            price=request.price,\r\n            comment=request.comment or "",\r\n            reason="CLIENT",\r\n        ))\r\n    except ValueError as exc:\r\n        raise _domain_error_to_http(exc, "cannot close position")\r\n    except HTTPException:\r\n        raise\r\n    except Exception:\r\n        logger.exception("close_position failed for %s (account %s)", position_id, login)\r\n        raise HTTPException(\r\n            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,\r\n            detail="Could not close the position",\r\n        )\r\n\r\n    remaining = getattr(getattr(position, "volume", None), "value", Decimal("0"))\r\n    realized = getattr(getattr(position, "profit", None), "amount", Decimal("0"))\r\n    price = getattr(getattr(position, "price_current", None), "value", None)\r\n    fully = bool(getattr(position, "time_done", None))\r\n\r\n    return ClosePositionResponse(\r\n        position_id=str(getattr(position, "position_id", position_id)),\r\n        symbol=str(getattr(position, "symbol", "")),\r\n        # a full close leaves volume 0, so report what was actually closed\r\n        volume_closed=(request.volume if request.volume is not None else remaining),\r\n        volume_remaining=remaining,\r\n        close_price=(Decimal(str(price)) if price is not None\r\n                     else (request.price or Decimal("0"))),\r\n        realized_pnl=Decimal(str(realized)),\r\n        deal_id=str(getattr(position, "deal_close", None) or ""),\r\n        fully_closed=fully,\r\n        message=("Position closed" if fully else "Position partially closed"),\r\n    )\r\n\r\n\r\n@router.put("/orders/{ticket_id}", response_model=OrderActionResponse)\r\nasync def modify_order(\r\n    ticket_id: str,\r',
        ),
        (
'    current_user: Account = Depends(get_current_user)\r\n):\r\n    """Modify an existing pending order (price, SL, TP)."""\r\n    return {\r\n        "status": "modified",\r\n        "ticket_id": ticket_id,\r\n        "price": str(request.price) if request.price else None,\r\n        "stop_loss": str(request.stop_loss) if request.stop_loss else None,\r\n        "take_profit": str(request.take_profit) if request.take_profit else None\r\n    }\r\n\r\n\r\n@router.delete("/orders/{ticket_id}")\r\nasync def cancel_order(\r\n    ticket_id: str,\r\n    current_user: Account = Depends(get_current_user)\r\n):\r\n    """Cancel a pending order."""\r\n    return {"status": "cancelled", "ticket_id": ticket_id}\r\n',
'    current_user: Account = Depends(get_current_user)\r\n):\r\n    """Modify a pending order\'s price, SL, TP or expiration - for real.\r\n\r\n    This used to echo the request back as {"status": "modified"} without persisting\r\n    anything. A client that moved its stop loss believed it was protected and was not.\r\n    """\r\n    handler = _handler("modify_order_handler", "Order modification")\r\n    login = _login_of(current_user)\r\n\r\n    if all(v is None for v in (request.price, request.stop_loss, request.take_profit)):\r\n        raise HTTPException(\r\n            status_code=status.HTTP_400_BAD_REQUEST,\r\n            detail="nothing to modify: supply price, stop_loss or take_profit",\r\n        )\r\n\r\n    try:\r\n        order = await handler.handle(ModifyOrderCommand(\r\n            account_login=login,\r\n            ticket_id=ticket_id,\r\n            new_price=request.price,\r\n            new_stop_loss=request.stop_loss,\r\n            new_take_profit=request.take_profit,\r\n            reason="CLIENT",\r\n        ))\r\n    except ValueError as exc:\r\n        raise _domain_error_to_http(exc, "cannot modify order")\r\n    except HTTPException:\r\n        raise\r\n    except Exception:\r\n        logger.exception("modify_order failed for %s (account %s)", ticket_id, login)\r\n        raise HTTPException(\r\n            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,\r\n            detail="Could not modify the order",\r\n        )\r\n\r\n    return _order_response(order, "modified")\r\n\r\n\r\n@router.delete("/orders/{ticket_id}", response_model=OrderActionResponse)\r\nasync def cancel_order(\r\n    ticket_id: str,\r\n    current_user: Account = Depends(get_current_user)\r\n):\r\n    """Cancel a resting order - for real.\r\n\r\n    This returned {"status": "cancelled"} for ANY ticket id, including one that did\r\n    not exist or belonged to another client. Nothing was cancelled and nothing was\r\n    logged.\r\n    """\r\n    handler = _handler("cancel_order_handler", "Order cancellation")\r\n    login = _login_of(current_user)\r\n\r\n    try:\r\n        order = await handler.handle(CancelOrderCommand(\r\n            account_login=login, ticket_id=ticket_id, reason="CLIENT",\r\n        ))\r\n    except ValueError as exc:\r\n        raise _domain_error_to_http(exc, "cannot cancel order")\r\n    except HTTPException:\r\n        raise\r\n    except Exception:\r\n        logger.exception("cancel_order failed for %s (account %s)", ticket_id, login)\r\n        raise HTTPException(\r\n            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,\r\n            detail="Could not cancel the order",\r\n        )\r\n\r\n    return _order_response(order, "cancelled")\r\n',
        ),
    ],
    "application/di/trading_setup.py": [
        (
'from typing import Any, Dict, Optional\n\nfrom application.commands.close_position import ClosePositionHandler\nfrom application.commands.create_order import CreateOrderHandler\nfrom application.commands.record_deal import RecordDealHandler\nfrom application.services.dealer_queue_service import DealerQueueService',
'from typing import Any, Dict, Optional\n\nfrom application.commands.cancel_order import CancelOrderHandler\nfrom application.commands.close_position import ClosePositionHandler\nfrom application.commands.create_order import CreateOrderHandler\nfrom application.commands.modify_order import ModifyOrderHandler\nfrom application.commands.record_deal import RecordDealHandler\nfrom application.services.dealer_queue_service import DealerQueueService',
        ),
        (
'    sltp_worker: Optional[Any] = None\n    close_position_handler: Optional[Any] = None\n    warnings: list = field(default_factory=list)\n',
'    sltp_worker: Optional[Any] = None\n    close_position_handler: Optional[Any] = None\n    #: D11: the order-lifecycle commands the client routes drive.\n    modify_order_handler: Optional[Any] = None\n    cancel_order_handler: Optional[Any] = None\n    #: D11: the order-lifecycle commands the client routes drive.\n    modify_order_handler: Optional[Any] = None\n    cancel_order_handler: Optional[Any] = None\n    warnings: list = field(default_factory=list)\n',
        ),
        (
'            "liquidity_gateway": self.liquidity_gateway,\n            "close_position_handler": self.close_position_handler,\n            "sltp_worker": self.sltp_worker,\n            "smart_order_router": self.router,',
'            "liquidity_gateway": self.liquidity_gateway,\n            "close_position_handler": self.close_position_handler,\n            "modify_order_handler": self.modify_order_handler,\n            "cancel_order_handler": self.cancel_order_handler,\n            "sltp_worker": self.sltp_worker,\n            "smart_order_router": self.router,',
        ),
        (
'    )\n\n    liquidation_service = _resolve(container, "liquidation_service", required=False, default=LiquidationService())\n    liquidation_worker = LiquidationWorker(',
'    )\n\n    # D11: modify and cancel existed and were complete, but nothing ever built\n    # them, so the two client routes that were supposed to use them had no handler\n    # to reach and returned a hardcoded success body instead. Built here, next to\n    # the close handler, so all three order-lifecycle commands come from one place.\n    modify_order_handler = ModifyOrderHandler(\n        account_repo=account_repo,\n        order_repo=order_repo,\n        risk_service=risk_service,\n        event_bus=event_bus,\n    )\n    cancel_order_handler = CancelOrderHandler(\n        account_repo=account_repo,\n        order_repo=order_repo,\n        risk_service=risk_service,\n        event_bus=event_bus,\n    )\n\n    # D11: modify and cancel existed and were complete, but nothing ever built\n    # them, so the two client routes that were supposed to use them had no handler\n    # to reach and returned a hardcoded success body instead. Built here, next to\n    # the close handler, so all three order-lifecycle commands come from one place.\n    modify_order_handler = ModifyOrderHandler(\n        account_repo=account_repo,\n        order_repo=order_repo,\n        risk_service=risk_service,\n        event_bus=event_bus,\n    )\n    cancel_order_handler = CancelOrderHandler(\n        account_repo=account_repo,\n        order_repo=order_repo,\n        risk_service=risk_service,\n        event_bus=event_bus,\n    )\n\n    liquidation_service = _resolve(container, "liquidation_service", required=False, default=LiquidationService())\n    liquidation_worker = LiquidationWorker(',
        ),
        (
'        sltp_worker=sltp_worker,\n        close_position_handler=close_position_handler,\n        warnings=warnings,\n    )',
'        sltp_worker=sltp_worker,\n        close_position_handler=close_position_handler,\n        modify_order_handler=modify_order_handler,\n        cancel_order_handler=cancel_order_handler,\n        warnings=warnings,\n    )',
        ),
    ],
}

applied = []
for path, pairs in PATCHES.items():
    src = io.open(path, encoding="utf-8", newline="").read()
    changed = False
    for old, new in pairs:
        if src.count(old) == 1:
            src = src.replace(old, new, 1)
            changed = True
        elif src.count(old) == 0 and src.count(new) >= 1:
            print(f"  skip (already patched): {path}")
        else:
            raise AssertionError(
                f"{path}: anchor found {src.count(old)}x (new text {src.count(new)}x): "
                f"{old[:70]!r}")
    if changed:
        ast.parse(src.replace("\r\n", "\n"))
        io.open(path, "w", encoding="utf-8", newline="").write(src)
        applied.append(path)

print(f"applied to {len(applied)} file(s):")
for f in applied:
    print("  ", f)
