"""
MT5 Manager API - Subscriptions Router (WebSocket).

Exposes WebSocket endpoints for real-time event streaming:
- WS /api/v1/manager/ws/subscriptions

Mirrors MT5 Manager API subscription endpoints:
- SubscribeAccount, SubscribeDeals, SubscribeGroup
- SubscribeOrderProfit, SubscribePositions, SubscribeRequests
- SubscribeSymbol, SubscribeTicks, SubscribeUser
"""
import logging
from typing import List
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from pydantic import BaseModel

from api.auth.admin_dependencies import verify_manager_token
from api.websockets.manager_subscriptions import get_manager_subscription_manager

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/manager", tags=["Manager - Subscriptions"])


class SubscribeRequest(BaseModel):
    """Request to subscribe to event types."""
    event_types: List[str]


class UnsubscribeRequest(BaseModel):
    """Request to unsubscribe from event types."""
    event_types: List[str] = None  # None = unsubscribe from all


@router.websocket("/ws/subscriptions")
async def manager_subscriptions_websocket(
    websocket: WebSocket,
):
    """
    WebSocket endpoint for Manager API subscriptions.
    
    Client must send authentication message first:
    {"action": "auth", "token": "<JWT>"}
    
    Then can subscribe/unsubscribe:
    {"action": "subscribe", "event_types": ["ticks", "orders", "deals"]}
    {"action": "unsubscribe", "event_types": ["ticks"]}
    """
    await websocket.accept()
    
    subscription_manager = get_manager_subscription_manager()
    client_id = None
    authenticated = False
    
    try:
        while True:
            # Receive message
            data = await websocket.receive_json()
            action = data.get("action")
            
            # Handle authentication
            if action == "auth":
                token = data.get("token")
                if not token:
                    await websocket.send_json({
                        "status": "error",
                        "message": "Token required"
                    })
                    continue
                
                # Verify JWT token
                try:
                    payload = verify_manager_token(token)
                    client_id = f"manager_{payload.get('sub')}"
                    authenticated = True
                    
                    await websocket.send_json({
                        "status": "success",
                        "message": "Authenticated",
                        "client_id": client_id
                    })
                    logger.info(f"Manager client {client_id} authenticated")
                except Exception as e:
                    await websocket.send_json({
                        "status": "error",
                        "message": f"Authentication failed: {str(e)}"
                    })
                    continue
            
            # Handle subscription
            elif action == "subscribe":
                if not authenticated:
                    await websocket.send_json({
                        "status": "error",
                        "message": "Not authenticated"
                    })
                    continue
                
                event_types = data.get("event_types", [])
                await subscription_manager.subscribe(client_id, websocket, event_types)
                
                await websocket.send_json({
                    "status": "success",
                    "message": f"Subscribed to {event_types}",
                    "subscriptions": subscription_manager.get_client_subscriptions(client_id)
                })
            
            # Handle unsubscription
            elif action == "unsubscribe":
                if not authenticated:
                    await websocket.send_json({
                        "status": "error",
                        "message": "Not authenticated"
                    })
                    continue
                
                event_types = data.get("event_types")
                await subscription_manager.unsubscribe(client_id, event_types)
                
                await websocket.send_json({
                    "status": "success",
                    "message": "Unsubscribed",
                    "subscriptions": subscription_manager.get_client_subscriptions(client_id)
                })
            
            # Handle ping
            elif action == "ping":
                await websocket.send_json({
                    "status": "success",
                    "message": "pong"
                })
            
            else:
                await websocket.send_json({
                    "status": "error",
                    "message": f"Unknown action: {action}"
                })
    
    except WebSocketDisconnect:
        logger.info(f"Manager client {client_id} disconnected")
        if client_id:
            await subscription_manager.unsubscribe(client_id)
    except Exception as e:
        logger.error(f"WebSocket error: {e}", exc_info=True)
        if client_id:
            await subscription_manager.unsubscribe(client_id)