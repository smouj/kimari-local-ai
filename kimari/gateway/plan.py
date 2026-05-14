"""
Gateway plan and endpoint specification for Kimari.

Provides the ``gateway_plan()`` function that returns the full planned
endpoint map, security constraints, integration relationships, and
future development notes for the gateway module.

The Next.js Gateway Dashboard is implemented and managed by
``kimari.gateway.dashboard_manager``. The management HTTP API described here
remains **planned**: no API endpoints are served by this module.
"""

from __future__ import annotations

# ─── Planned Endpoints ────────────────────────────────────────────────────────

_PLANNED_ENDPOINTS: list[dict[str, str]] = [
    {"method": "GET", "path": "/health", "description": "Health check", "status": "planned"},
    {"method": "GET", "path": "/status", "description": "Server status", "status": "planned"},
    {"method": "GET", "path": "/profiles", "description": "Available profiles", "status": "planned"},
    {"method": "GET", "path": "/models", "description": "Available models", "status": "planned"},
    {"method": "GET", "path": "/config", "description": "Current configuration", "status": "planned"},
    {"method": "GET", "path": "/logs", "description": "Recent log entries", "status": "planned"},
    {"method": "GET", "path": "/integrations", "description": "Integration status", "status": "planned"},
    {"method": "POST", "path": "/server/start", "description": "Start llama-server", "status": "planned"},
    {"method": "POST", "path": "/server/stop", "description": "Stop llama-server", "status": "planned"},
    {"method": "POST", "path": "/benchmark/run", "description": "Run benchmark", "status": "planned"},
]

# ─── Security Constraints ─────────────────────────────────────────────────────

_SECURITY: dict = {
    "default_host": "127.0.0.1",
    "default_port": 11436,
    "bind_localhost_only": True,
    "no_public_exposure": True,
    "no_token_storage": True,
    "no_model_upload": True,
    "no_training_execution": True,
    "no_hf_publishing": True,
}

# ─── Integration Relationships ────────────────────────────────────────────────

_RELATIONSHIP: dict = {
    "fastapi_experimental": "Gateway will use FastAPI (currently in kimari/api as experimental)",
    "open_webui": "Gateway will help configure and monitor the local OpenAI-compatible llama-server endpoint used by Open WebUI",
    "openclaw": "Gateway may expose integration status and config for OpenClaw",
    "hermes": "Gateway may expose integration status and config for Hermes",
}

# ─── Future Notes ─────────────────────────────────────────────────────────────

_FUTURE_NOTES: list[str] = [
    "Gateway Dashboard is implemented; Gateway API server is planned for a future release",
    "All API endpoints are design-only; none are served at runtime",
    "FastAPI dependency is not required until the gateway is implemented",
    "Security: gateway binds to 127.0.0.1 only — no public network exposure",
    "Security: no token storage, no model upload, no training execution, no HF publishing",
    "Server start/stop endpoints will manage llama-server subprocess lifecycle",
    "Benchmark endpoint will integrate with kimari.benchmarks module",
    "Integration endpoints will report status of OpenClaw, Hermes, and other tools",
    "OpenAPI schema will be auto-generated from FastAPI route definitions",
    "Authentication may be added for non-localhost access in future versions",
]


def gateway_plan(config: dict | None = None) -> dict:
    """Return the planned gateway configuration and endpoint map.

    This function performs no network operations and starts no server.
    It reports the *planned* design of the gateway module.

    Args:
        config: Optional configuration dict (as loaded by
            ``kimari.config.loader.load_config()``).  Currently unused
            but accepted for forward-compatibility.

    Returns:
        A dict with the following keys:

        - **planned_endpoints** (list[dict]): Each dict has
          ``method``, ``path``, ``description``, and ``status`` keys.
        - **security** (dict): Security constraints enforced by design.
        - **relationship** (dict): Integration relationships with other
          Kimari modules and external tools.
        - **api_planned_only** (bool): Always ``True`` — no management API server exists.
        - **dashboard_status** (dict): Dashboard implementation status.
        - **future_notes** (list[str]): Development notes about the
          planned gateway.
    """
    return {
        "planned_endpoints": list(_PLANNED_ENDPOINTS),
        "security": dict(_SECURITY),
        "relationship": dict(_RELATIONSHIP),
        "planned_only": True,
        "api_planned_only": True,
        "dashboard_status": {
            "implemented": True,
            "command": "kimari gateway start",
            "default_url": "http://127.0.0.1:3105",
            "local_only_default": True,
        },
        "future_notes": list(_FUTURE_NOTES),
    }
