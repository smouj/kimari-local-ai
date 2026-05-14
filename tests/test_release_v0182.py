"""Release validation tests for v0.1.82-alpha."""

from __future__ import annotations

import json
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
VERSION = "0.1.82-alpha"


def test_versions_bumped():
    assert f'version = "{VERSION}"' in (REPO / "pyproject.toml").read_text()
    assert f'__version__ = "{VERSION}"' in (REPO / "kimari" / "__init__.py").read_text()
    pkg = json.loads((REPO / "apps" / "gateway-dashboard" / "package.json").read_text())
    assert pkg["version"] == VERSION


def test_public_docs_reference_current_version():
    for path in [
        "README.md",
        "docs/index.html",
        "CHANGELOG.md",
        "ROADMAP.md",
        "RELEASE_CHECKLIST.md",
        "docs/HUGGINGFACE_ORG_CARD.md",
        "docs/HUGGINGFACE_DEPLOYMENT_STATUS.md",
        "docs/KIMARI4B_RUN_HISTORY.md",
        "huggingface/kimari-fit-lab/README.md",
    ]:
        assert VERSION in (REPO / path).read_text(), path


def test_one_command_and_console_docs_exist():
    readme = (REPO / "README.md").read_text()
    assert "install.sh | bash" in readme
    assert "kimari console" in readme
    assert "kimari gateway setup" in readme
    assert "kimari gateway start --open" in readme
    for path in ["docs/INSTALL_ONE_COMMAND.md", "docs/KIMARI_CONSOLE.md", "docs/GATEWAY_DASHBOARD_CLI.md"]:
        assert (REPO / path).exists(), path


def test_console_and_gateway_setup_commands_registered():
    cli = (REPO / "kimari" / "cli" / "main.py").read_text()
    assert 'add_parser("console"' in cli
    assert "console_cmd" in cli
    assert 'add_parser("setup"' in cli
    assert "--dry-run" in cli
    assert "--start" in cli
    assert "--open" in cli
    assert "update_apply" in cli


def test_gate_stays_blocked_and_no_public_bind_default():
    manager = (REPO / "kimari" / "gateway" / "dashboard_manager.py").read_text()
    assert 'DEFAULT_HOST = "127.0.0.1"' in manager
    assert 'GATE_STATE = "BLOCKED"' in manager
    assert "allow_public_bind" in manager
    console = (REPO / "kimari" / "cli" / "console_cmd.py").read_text()
    assert '"gate": "BLOCKED"' in console
    assert '"kimari_4b_released": False' in console
