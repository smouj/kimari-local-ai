"""
Kimari Gateway Module — local dashboard plus planned management API.

**STATUS**: Gateway Dashboard implemented; Gateway API remains planned / dry-run only.

This module provides planning and status utilities for a future FastAPI-based
gateway that will manage llama-server instances, profiles, benchmarks, and
integrations from a local HTTP interface.

Planned defaults:
  - Host: 127.0.0.1 (localhost only, no public exposure)
  - Port: 11436

Security rules enforced by design:
  - Bind 127.0.0.1 only by default
  - No public exposure
  - No token storage
  - No model upload
  - No training execution
  - No Hugging Face publishing
"""

from __future__ import annotations

from kimari.gateway.dashboard_manager import (
    DashboardError,
)
from kimari.gateway.dashboard_manager import (
    logs as dashboard_logs,
)
from kimari.gateway.dashboard_manager import (
    open_browser as dashboard_open_browser,
)
from kimari.gateway.dashboard_manager import (
    reset as dashboard_reset,
)
from kimari.gateway.dashboard_manager import (
    restart as dashboard_restart,
)
from kimari.gateway.dashboard_manager import (
    setup as dashboard_setup,
)
from kimari.gateway.dashboard_manager import (
    start as dashboard_start,
)
from kimari.gateway.dashboard_manager import (
    status as dashboard_status,
)
from kimari.gateway.dashboard_manager import (
    stop as dashboard_stop,
)
from kimari.gateway.plan import gateway_plan
from kimari.gateway.state import gateway_status

__all__ = [
    "DashboardError",
    "dashboard_start",
    "dashboard_stop",
    "dashboard_restart",
    "dashboard_status",
    "dashboard_logs",
    "dashboard_open_browser",
    "dashboard_reset",
    "dashboard_setup",
    "gateway_status",
    "gateway_plan",
]
