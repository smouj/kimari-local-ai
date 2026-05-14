"""Release validation tests for v0.1.81-alpha."""

from __future__ import annotations

import json
import re
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
VERSION = "0.1.81-alpha"


def test_pyproject_version():
    assert f'version = "{VERSION}"' in (REPO / "pyproject.toml").read_text()


def test_init_version():
    assert f'__version__ = "{VERSION}"' in (REPO / "kimari" / "__init__.py").read_text()


def test_dashboard_package_version():
    pkg = json.loads((REPO / "apps" / "gateway-dashboard" / "package.json").read_text())
    assert pkg["version"] == VERSION


def test_readme_badge_and_gateway_cli_docs():
    readme = (REPO / "README.md").read_text()
    assert "0.1.81--alpha" in readme
    assert "kimari gateway setup" in readme
    assert "kimari gateway start --open" in readme
    assert "Gateway (Dry-Run Only)" not in readme


def test_docs_index_version():
    assert VERSION in (REPO / "docs" / "index.html").read_text()


def test_release_docs_version_references():
    paths = [
        "CHANGELOG.md",
        "ROADMAP.md",
        "RELEASE_CHECKLIST.md",
        "docs/HUGGINGFACE_ORG_CARD.md",
        "docs/HUGGINGFACE_DEPLOYMENT_STATUS.md",
        "docs/KIMARI4B_RUN_HISTORY.md",
        "huggingface/kimari-fit-lab/README.md",
    ]
    for path in paths:
        assert VERSION in (REPO / path).read_text(), path


def test_gateway_dashboard_manager_exists():
    manager = REPO / "kimari" / "gateway" / "dashboard_manager.py"
    text = manager.read_text()
    assert "def start(" in text
    assert "def stop(" in text
    assert "def restart(" in text
    assert "def status(" in text
    assert "def reset(" in text
    assert "127.0.0.1" in text
    assert "BLOCKED" in text


def test_gateway_cli_subcommands_registered():
    cli = (REPO / "kimari" / "cli" / "main.py").read_text()
    for command in ["start", "stop", "restart", "status", "logs", "open", "reset", "setup"]:
        assert re.search(rf'add_parser\("{command}"', cli), command
    assert "--allow-public-bind" in cli


def test_dashboard_ui_safety_labels():
    overview = (REPO / "apps" / "gateway-dashboard" / "src" / "components" / "dashboard" / "overview.tsx").read_text()
    assert "Kimari-4B not released" in overview
    assert "Gate: BLOCKED" in overview
    assert "Local only" in overview
