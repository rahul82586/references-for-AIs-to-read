"""
MT5 Manager API - Service schemas.

Mirrors MT5 endpoints:
- Ping (health check)
- StartTimeUtc (server start time)
- MemoryUsage (process memory stats)
- Version (server version info)

These endpoints are used for:
- Health monitoring (load balancers, Kubernetes probes)
- Server diagnostics
- Client keep-alive
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class PingResponse(BaseModel):
    """MT5 Ping response - health check."""
    retcode: int = 0
    server_time: datetime = Field(..., alias="serverTime")
    status: str = "OK"
    latency_ms: Optional[float] = Field(
        None,
        alias="latencyMs",
        description="Server processing latency in milliseconds"
    )

    class Config:
        populate_by_name = True


class ServerInfo(BaseModel):
    """Server information (StartTimeUtc + Version combined)."""
    server_name: str = Field(..., alias="serverName")
    server_version: str = Field(..., alias="serverVersion")
    start_time_utc: datetime = Field(..., alias="startTimeUtc")
    uptime_seconds: int = Field(..., alias="uptimeSeconds")
    uptime_human: str = Field(..., alias="uptimeHuman")
    build_number: Optional[str] = Field(None, alias="buildNumber")
    api_version: str = Field(..., alias="apiVersion")
    python_version: str = Field(..., alias="pythonVersion")

    class Config:
        populate_by_name = True


class MemoryUsage(BaseModel):
    """Process memory usage statistics."""
    retcode: int = 0
    rss_mb: float = Field(..., alias="rssMb", description="Resident Set Size in MB")
    vms_mb: float = Field(..., alias="vmsMb", description="Virtual Memory Size in MB")
    shared_mb: Optional[float] = Field(None, alias="sharedMb")
    text_mb: Optional[float] = Field(None, alias="textMb")
    data_mb: Optional[float] = Field(None, alias="dataMb")
    percent: float = Field(..., description="Memory usage as % of total system RAM")
    cpu_percent: float = Field(
        ...,
        alias="cpuPercent",
        description="Current CPU usage %"
    )
    open_files: int = Field(..., alias="openFiles")
    num_threads: int = Field(..., alias="numThreads")

    class Config:
        populate_by_name = True


class VersionInfo(BaseModel):
    """Server version information."""
    server_name: str = Field(..., alias="serverName")
    server_version: str = Field(..., alias="serverVersion")
    api_version: str = Field(..., alias="apiVersion")
    build_number: Optional[str] = Field(None, alias="buildNumber")
    python_version: str = Field(..., alias="pythonVersion")
    build_date: Optional[datetime] = Field(None, alias="buildDate")

    class Config:
        populate_by_name = True