"""
WebSocket Routes for Public Quotes & Private Trade Updates

Includes:
- /ws/stream: Unauthenticated public tick stream.
- /ws/user: Authenticated private stream using secure FIRST-MESSAGE authentication.

Security Rule: JWT is passed via first message {"action": "auth", "token": "..."}, NOT URL query parameters.
"""
import json
import logging
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from api.auth.jwt_handler import verify_token
from api.websockets.manager import ConnectionManager

logger = logging.getLogger(__name__)

router = APIRouter()
manager = ConnectionManager()


@router.websocket("/ws/stream")
async def websocket_public_stream(websocket: WebSocket):
    """Public unauthenticated WebSocket stream for live quotes and DOM updates."""
    await manager.connect_public(websocket)
    try:
        while True:
            # Keep connection alive and process incoming subscription requests if any
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)


@router.websocket("/ws/user")
async def websocket_user_stream(websocket: WebSocket):
    """
    Private authenticated WebSocket stream for user-specific trade & margin events.
    Uses SECURE FIRST-MESSAGE AUTHENTICATION pattern.
    """
    await websocket.accept()
    user_id = None

    try:
        # Step 1: Wait for first authentication message
        auth_text = await websocket.receive_text()
        auth_payload = json.loads(auth_text)

        if auth_payload.get("action") != "auth" or not auth_payload.get("token"):
            logger.warning("WebSocket first message was not a valid auth request. Closing connection.")
            await websocket.close(code=1008)  # Policy Violation
            return

        # Step 2: Verify JWT token
        token = auth_payload["token"]
        token_data = verify_token(token)
        user_id = token_data.get("sub")

        if not user_id:
            await websocket.close(code=1008)
            return

        # Step 3: Register authenticated user connection
        await manager.connect_user(websocket, user_id=user_id)
        await websocket.send_text(json.dumps({"status": "authenticated", "user_id": user_id}))

        # Step 4: Run continuous receive loop
        while True:
            await websocket.receive_text()

    except WebSocketDisconnect:
        if user_id:
            manager.disconnect(websocket, user_id=user_id)
    except Exception as e:
        logger.error(f"WebSocket auth failure or runtime error: {e}")
        try:
            await websocket.close(code=1008)
        except Exception:
            pass
        if user_id:
            manager.disconnect(websocket, user_id=user_id)
