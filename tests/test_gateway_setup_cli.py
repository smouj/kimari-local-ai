"""Gateway setup CLI tests for v0.1.83-alpha."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent


def test_gateway_setup_dry_run_json_works():
    completed = subprocess.run(
        [sys.executable, "-m", "kimari", "gateway", "setup", "--dry-run", "--json"],
        cwd=REPO,
        text=True,
        capture_output=True,
        check=True,
    )
    data = json.loads(completed.stdout)
    assert data["status"] == "dry-run"
    assert ["npm", "install"] in data["commands"]
    assert ["npm", "run", "db:setup"] in data["commands"]
    assert ["npm", "run", "build"] in data["commands"]
    assert data["gate_state"] == "BLOCKED"


def test_gateway_start_dry_run_json_works():
    completed = subprocess.run(
        [sys.executable, "-m", "kimari", "gateway", "start", "--dry-run", "--json"],
        cwd=REPO,
        text=True,
        capture_output=True,
        check=True,
    )
    data = json.loads(completed.stdout)
    assert data["status"] == "dry-run"
    assert data["host"] == "127.0.0.1"
    assert data["gate_state"] == "BLOCKED"
