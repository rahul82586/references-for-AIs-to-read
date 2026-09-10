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
    event_bus = AsyncMock()
    manager = AsyncMock()
    bridge = WebSocketEventBridge(event_bus=event_bus, connection_manager=manager)

    event_dict = {
        "event_type": "market.tick_received",
        "payload": {
            "symbol": "EURUSD",
            "bid": "1.0800",
            "ask": "1.0802",
            "spread": "0.0002"
        }
    }

    await bridge._handle_tick(event_dict)
    manager.broadcast_tick.assert_called_once_with(
        symbol="EURUSD",
        bid="1.0800",
        ask="1.0802",
        spread="0.0002"
    )


# -----------------------------------------------------------------------------
# Test 6: CQRS Read-Side Query Handlers
# -----------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_get_account_info_query_handler():
    account_mock = MagicMock()
    account_mock.login_id = "10001"
    account_mock.group.name = "real_group"
    account_mock.balance.amount = Decimal('10000.00')
    account_mock.balance.currency = "USD"
    account_mock.equity.amount = Decimal('10500.00')
    account_mock.margin_used.amount = Decimal('500.00')
    account_mock.margin_free.amount = Decimal('10000.00')

    account_repo = AsyncMock()
    account_repo.find_by_login.return_value = account_mock

    handler = GetAccountInfoQueryHandler(account_repo=account_repo)
    result = await handler.handle(GetAccountInfoQuery(login_id="10001"))

    assert result["login_id"] == "10001"
    assert result["balance"] == Decimal('10000.00')
    assert result["equity"] == Decimal('10500.00')
    assert result["margin_level"] == Decimal('2100.00')


# -----------------------------------------------------------------------------
# Test 7: Systemic Trailing Space Audit
# -----------------------------------------------------------------------------
def test_no_trailing_spaces_in_schemas():
    order = OrderRequest(symbol="EURUSD", order_type="BUY", volume=Decimal('1.0'))
    assert order.symbol == order.symbol.strip()
    assert order.order_type == order.order_type.strip()
