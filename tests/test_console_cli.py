"""Kimari console CLI tests."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from kimari.cli.console_cmd import MENU_ITEMS, collect_console_status

REPO = Path(__file__).resolve().parent.parent


def test_console_status_imports_and_contains_safety_labels():
    status = collect_console_status()
    assert status["gate"] == "BLOCKED"
    assert status["kimari_4b_released"] is False
    assert status["version"]
    assert "Run doctor" in status["menu_items"]


def test_console_json_works():
    completed = subprocess.run(
        [sys.executable, "-m", "kimari", "console", "--json"],
        cwd=REPO,
        text=True,
        capture_output=True,
        check=True,
    )
    data = json.loads(completed.stdout)
    assert data["gate"] == "BLOCKED"
    assert data["kimari_4b_released"] is False
    assert "gpu" in data
    assert "gateway" in data


def test_console_menu_items_exist():
    expected = [
        "Run doctor",
        "Setup/write config",
        "Download test model",
        "Start local API",
        "Stop local API",
        "Gateway setup",
        "Gateway start/open",
        "Generate integrations",
        "Exit",
    ]
    assert expected == MENU_ITEMS
