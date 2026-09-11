"""
MT5 Manager API - Connection schemas.

Mirrors MT5 endpoints:
- Connect (session creation)
- Disconnect (session termination)
- IsConnected (status check)
- SessionInfo (current session details)

Architectural Note:
While MT5 uses token-based authentication via /Connect, our system uses JWT.
The /Connect endpoint here provides MT5-compatible session metadata while
leveraging our existing JWT infrastructure for actual authentication.
"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


class ConnectRequest(BaseModel):
    """MT5 Connect request body."""
    version: str = Field(
        ...,
        description="Client API version (e.g., '5.0.0')"
    )
    client_agent: Optional[str] = Field(
        None,
        alias="clientAgent",
        description="Client application identifier"
    )
    client_ip: Optional[str] = Field(
        None,
        alias="clientIP",
        description="Client IP address (auto-detected if not provided)"
    )

    class Config:
        populate_by_name = True


class ConnectResponse(BaseModel):
    """MT5 Connect response - session metadata."""
    retcode: int = Field(0, description="Return code (0 = OK)")
    session_id: str = Field(..., alias="sessionId")
    access_level: str = Field(..., alias="accessLevel")
    user_login: int = Field(..., alias="userLogin")
    user_group: Optional[str] = Field(None, alias="userGroup")
    user_name: Optional[str] = Field(None, alias="userName")
    user_email: Optional[str] = Field(None, alias="userEmail")
    permissions: List[str] = Field(default_factory=list)
    server_time: datetime = Field(..., alias="serverTime")
    message: str = Field("Connected successfully")

    class Config:
        populate_by_name = True


class SessionInfo(BaseModel):
    """Current session information."""
    session_id: str = Field(..., alias="sessionId")
    user_login: int = Field(..., alias="userLogin")
    user_group: Optional[str] = Field(None, alias="userGroup")
    access_level: str = Field(..., alias="accessLevel")
    client_agent: Optional[str] = Field(None, alias="clientAgent")
    client_ip: Optional[str] = Field(None, alias="clientIP")
    connected_at: datetime = Field(..., alias="connectedAt")
    last_activity: datetime = Field(..., alias="lastActivity")
    expires_at: datetime = Field(..., alias="expiresAt")

    class Config:
        populate_by_name = True


class ConnectionStatus(BaseModel):
    """Connection status response."""
    connected: bool
    session_id: Optional[str] = Field(None, alias="sessionId")
    user_login: Optional[int] = Field(None, alias="userLogin")
    server_time: datetime = Field(..., alias="serverTime")

    class Config:
        populate_by_name = True


class DisconnectResponse(BaseModel):
    """Disconnect response."""
    retcode: int = 0
    message: str = "Disconnected successfully"
    session_id: Optional[str] = Field(None, alias="sessionId")

    class Config:
        populate_by_name = True