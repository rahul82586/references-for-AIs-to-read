"""
Comprehensive Unit Test Suite for Phase 10 API Layer

Validates:
1. Pydantic Decimal preservation (prevents float contamination)
2. JWT token generation & verification
3. Admin API Key authorization & 403 rejection
4. WebSocket first-message authentication security
5. Event-to-WebSocket Bridge event routing
6. CQRS Command/Query handler router invocation
7. Systemic zero trailing spaces audit
"""
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi import HTTPException

from api.auth.admin_dependencies import verify_admin_api_key
from api.auth.jwt_handler import create_access_token, verify_token
from api.schemas.account import AccountInfo, PositionResponse
from api.schemas.trade import OrderRequest
from api.websockets.event_bridge import WebSocketEventBridge
from api.websockets.manager import ConnectionManager
from application.queries.get_account_info import GetAccountInfoQuery, GetAccountInfoQueryHandler
from application.queries.get_positions import GetPositionsQuery, GetPositionsQueryHandler


# -----------------------------------------------------------------------------
# Test 1: Pydantic Decimal Preservation
# -----------------------------------------------------------------------------
def test_pydantic_decimal_preservation():
    order = OrderRequest(
        symbol="EURUSD",
        order_type="BUY",
        volume=Decimal('0.01'),
        price=Decimal('1.0800')
    )
    assert isinstance(order.volume, Decimal)
    assert isinstance(order.price, Decimal)
    assert order.volume == Decimal('0.01')
    assert order.type_filling == "FOK"


# -----------------------------------------------------------------------------
# Test 2: JWT Token Generation & Verification
# -----------------------------------------------------------------------------
def test_jwt_token_flow():
    payload = {"sub": "user_1001"}
    token = create_access_token(payload)

    assert isinstance(token, str)
    decoded = verify_token(token)
    assert decoded["sub"] == "user_1001"

    with pytest.raises(ValueError):
        verify_token("invalid.jwt.token")


# -----------------------------------------------------------------------------
# Test 3 & 4: Admin API Key Authorization
# -----------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_admin_api_key_rejection():
    with pytest.raises(HTTPException) as exc_info:
        await verify_admin_api_key(x_admin_api_key="WRONG_KEY")
    assert exc_info.value.status_code == 403

    with pytest.raises(HTTPException) as exc_info:
        await verify_admin_api_key(x_admin_api_key=None)
    assert exc_info.value.status_code == 403


@pytest.mark.asyncio
async def test_admin_api_key_success():
    from api.auth.admin_dependencies import ADMIN_API_KEY_ENV
    res = await verify_admin_api_key(x_admin_api_key=ADMIN_API_KEY_ENV)
    assert res == ADMIN_API_KEY_ENV


# -----------------------------------------------------------------------------
# Test 5: WebSocket Event Bridge Routing
# -----------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_event_bridge_routes_tick():
    """A tick event on the bus must reach the WebSocket subscribers.

    The previous version of this test called `bridge._handle_tick(...)`, a method that has
    never existed, and asserted on a local `manager = AsyncMock()` that was never connected
    to the bridge - WebSocketEventBridge resolves its own subscription manager internally
    via get_manager_subscription_manager(). So the assertion inspected an object nothing
    ever called, and the test could not have failed no matter what the bridge did.

    This version patches the singleton the bridge actually uses, calls the real handler
    with a real DomainEvent, and asserts the broadcast that genuinely occurs.
    """
    from unittest.mock import patch

    from core.events.domain_events import DomainEvent, EventType

    event_bus = AsyncMock()
    manager = AsyncMock()

    with patch(
        "api.websockets.event_bridge.get_manager_subscription_manager",
        return_value=manager,
    ):
        bridge = WebSocketEventBridge(event_bus=event_bus)

    assert bridge.subscription_manager is manager, (
        "the bridge must use the patched singleton; if this fails the test is asserting "
        "against a manager the bridge never touches"
    )

    payload = {
        "symbol": "EURUSD",
        "bid": "1.0800",
        "ask": "1.0802",
        "spread": "0.0002",
    }
    event = DomainEvent(event_type=EventType.TICK_RECEIVED, payload=payload)

    await bridge._on_tick_received(event)

    manager.broadcast.assert_awaited_once_with("ticks", payload)



# -----------------------------------------------------------------------------
# Test 6: CQRS Read-Side Query Handlers
# -----------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_get_account_info_query_handler():
    account_mock = MagicMock()
    account_mock.login = "10001"
    account_mock.group.name = "real_group"
    account_mock.balance.amount = Decimal('10000.00')
    account_mock.balance.currency = "USD"
    account_mock.equity.amount = Decimal('10500.00')
    account_mock.margin_used.amount = Decimal('500.00')
    account_mock.margin_free.amount = Decimal('10000.00')
    account_mock.credit.amount = Decimal('0.00')
    account_mock.effective_leverage.return_value = 100

    account_repo = AsyncMock()
    account_repo.find_by_login.return_value = account_mock

    handler = GetAccountInfoQueryHandler(account_repo=account_repo)
    result = await handler.handle(GetAccountInfoQuery(account_login="10001"))

    assert result["login_id"] == "10001"
    assert result["balance"] == Decimal('10000.00')
    assert result["equity"] == Decimal('10500.00')
    assert result["margin_level"] == Decimal('2100.00')
    # D2: the manager UserGet schema needs these; they had no source before.
    assert result["credit"] == Decimal('0.00')
    assert result["leverage"] == 100


# -----------------------------------------------------------------------------
# Test 7: Systemic Trailing Space Audit
# -----------------------------------------------------------------------------
def test_no_trailing_spaces_in_schemas():
    order = OrderRequest(symbol="EURUSD", order_type="BUY", volume=Decimal('1.0'))
    assert order.symbol == order.symbol.strip()
    # order_type is an OrderType now, not a str: it was typed as a bare string, so the
    # router handed "BUY" to CreateOrderCommand and the Order entity failed every enum
    # comparison (is_market() said False and a market order was priced as a pending one).
    # An enum cannot carry trailing whitespace, so the old `.strip()` assertion is
    # replaced by the stronger one - it is the enum member itself.
    from core.domains.oms.enums import OrderType

    assert order.order_type is OrderType.BUY


def test_order_request_rejects_an_unknown_side():
    """Whitespace or a typo in the side is a 422 at the edge, not an error mid-execution."""
    import pydantic

    for bad in ("BUY_HARD", "buy ", "", "MARKET"):
        with pytest.raises(pydantic.ValidationError):
            OrderRequest(symbol="EURUSD", order_type=bad, volume=Decimal('1.0'))
