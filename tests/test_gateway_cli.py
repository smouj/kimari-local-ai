"""Gateway Dashboard CLI and manager safety tests."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

from kimari.gateway import dashboard_manager

REPO = Path(__file__).resolve().parent.parent


def test_dashboard_manager_imports():
    assert dashboard_manager.DEFAULT_HOST == "127.0.0.1"
    assert dashboard_manager.DEFAULT_PORT == 3105
    assert dashboard_manager.GATE_STATE == "BLOCKED"


def test_start_dry_run_default_host_port():
    result = dashboard_manager.start(dry_run=True)
    assert result["status"] == "dry-run"
    assert result["host"] == "127.0.0.1"
    assert result["port"] == 3105
    assert result["url"] == "http://127.0.0.1:3105"
    assert result["gate_state"] == "BLOCKED"
    assert result["local_only"] is True
    assert result["command"][:3] == ["npm", "run", "start"]


def test_public_bind_blocked_by_default():
    with pytest.raises(dashboard_manager.DashboardError, match="Refusing non-local"):
        dashboard_manager.start(host="0.0.0.0", dry_run=True)


def test_public_bind_requires_explicit_flag():
    result = dashboard_manager.start(host="0.0.0.0", dry_run=True, allow_public_bind=True)
    assert result["status"] == "dry-run"
    assert result["local_only"] is False
    assert result["command"][-2:] == ["-H", "0.0.0.0"]


def test_status_reports_gate_and_does_not_require_backend():
    result = dashboard_manager.status()
    assert result["gate_state"] == "BLOCKED"
    assert result["kimari_4b_released"] is False
    assert result["local_only"] is True
    assert "backend_reachable" in result


def test_reset_requires_confirmation():
    with pytest.raises(dashboard_manager.DashboardError, match="requires confirmation"):
        dashboard_manager.reset(confirm=False)


def test_reset_safe_with_confirmation():
    result = dashboard_manager.reset(confirm=True, clean_deps=False)
    assert result["status"] == "reset"
    assert result["models_touched"] is False
    assert result["adapters_touched"] is False


def test_cli_gateway_start_dry_run_json():
    completed = subprocess.run(
        [sys.executable, "-m", "kimari", "gateway", "start", "--dry-run", "--json"],
        cwd=REPO,
        text=True,
        capture_output=True,
        check=True,
    )
    data = json.loads(completed.stdout)
    assert data["status"] == "dry-run"
    assert data["url"] == "http://127.0.0.1:3105"
    assert data["gate_state"] == "BLOCKED"
