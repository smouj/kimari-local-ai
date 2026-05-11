"""
Kimari Gateway Module — Planned REST API gateway for local AI management.

**STATUS**: Design / dry-run only. No real server is started.

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

from kimari.gateway.plan import gateway_plan
from kimari.gateway.state import gateway_status

__all__ = ["gateway_status", "gateway_plan"]
