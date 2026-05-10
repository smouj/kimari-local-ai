"""
Pydantic schemas for the Kimari Experimental API.

These models define the request/response shapes for all API endpoints.
They are intentionally separate from business logic so that the API
layer can evolve without affecting the CLI or core modules.
"""

from __future__ import annotations  # noqa: I001

from typing import Any

from pydantic import BaseModel, Field


# ─── Shared ─────────────────────────────────────────────────────────────────


class ErrorResponse(BaseModel):
    """Standard error response."""

    error: str
    detail: str | None = None


class ExperimentalWarning(BaseModel):
    """Included in every response to remind callers this API is experimental."""

    experimental: bool = Field(default=True, description="API is experimental and may change")


# ─── Health ────────────────────────────────────────────────────────────────


class HealthResponse(BaseModel):
    """Response for GET /health."""

    status: str = "ok"
    version: str
    experimental: bool = Field(default=True)


# ─── Status ────────────────────────────────────────────────────────────────


class StatusResponse(BaseModel):
    """Response for GET /status."""

    running: bool
    pid: int | None = None
    profile: str | None = None
    model: str | None = None
    host: str | None = None
    port: int | None = None
    uptime_s: int | None = None
    health: dict[str, Any] | None = None
    experimental: bool = Field(default=True)


# ─── Config ────────────────────────────────────────────────────────────────


class ConfigResponse(BaseModel):
    """Response for GET /config."""

    config_version: int
    default_profile: str
    profiles: list[dict[str, Any]]
    config_path: str | None = None
    experimental: bool = Field(default=True)


# ─── Profiles ──────────────────────────────────────────────────────────────


class ProfileDetail(BaseModel):
    """A single GPU profile."""

    name: str
    model: str
    host: str = "127.0.0.1"
    port: int = 11435
    ctx: int | None = None
    batch: int | None = None
    ubatch: int | None = None
    gpu_layers: str | int | None = None
    flash_attn: str | None = None
    parallel: int | None = None


class ProfilesResponse(BaseModel):
    """Response for GET /profiles."""

    default_profile: str
    profiles: list[ProfileDetail]
    experimental: bool = Field(default=True)


# ─── Models ────────────────────────────────────────────────────────────────


class ModelEntry(BaseModel):
    """A model from the registry."""

    id: str
    display_name: str
    filename: str
    size_gb: float | None = None
    status: str | None = None
    downloaded: bool = False
    sha256_pinned: bool = False


class ModelsResponse(BaseModel):
    """Response for GET /models."""

    models: list[ModelEntry]
    experimental: bool = Field(default=True)


# ─── Optimize ──────────────────────────────────────────────────────────────


class OptimizeRequest(BaseModel):
    """Request for POST /optimize."""

    profile: str | None = None
    mode: str = "balanced"
    vram_gb: float | None = None


class OptimizeResponse(BaseModel):
    """Response for POST /optimize."""

    profile: str
    recommendations: dict[str, Any]
    estimates: dict[str, Any]
    confidence: str
    warnings: list[str]
    experimental: bool = Field(default=True)


# ─── Perf Dry-Run ──────────────────────────────────────────────────────────


class PerfDryRunRequest(BaseModel):
    """Request for POST /perf/dry-run."""

    profile: str | None = None
    matrix: bool = False


class PerfModeResult(BaseModel):
    """Single performance mode result."""

    mode: str
    ctx: int
    batch: int
    ubatch: int
    cache_type_k: str
    cache_type_v: str
    gpu_layers: str | int
    flash_attn: bool
    parallel: int
    expected_vram_gb: float
    expected_ram_gb: float
    confidence: str
    warnings: list[str]


class PerfDryRunResponse(BaseModel):
    """Response for POST /perf/dry-run."""

    profile: str
    model: str
    vram_total_gb: float
    dry_run: bool = True
    modes: list[PerfModeResult]
    experimental: bool = Field(default=True)


# ─── Server Start/Stop (planned — 501) ────────────────────────────────────


class ServerStartRequest(BaseModel):
    """Request for POST /server/start (planned)."""

    profile: str
    daemon: bool = False


class ServerStartResponse(BaseModel):
    """Response for POST /server/start (planned)."""

    status: str = "planned"
    detail: str = "Server start/stop via API is planned for a future release"


class ServerStopResponse(BaseModel):
    """Response for POST /server/stop (planned)."""

    status: str = "planned"
    detail: str = "Server start/stop via API is planned for a future release"
