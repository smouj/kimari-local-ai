"""Release validation tests for v0.1.85-alpha."""

from __future__ import annotations

import json
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
VERSION = "0.1.85-alpha"


def test_versions_bumped():
    assert f'version = "{VERSION}"' in (REPO / "pyproject.toml").read_text()
    assert f'__version__ = "{VERSION}"' in (REPO / "kimari" / "__init__.py").read_text()
    pkg = json.loads((REPO / "apps" / "gateway-dashboard" / "package.json").read_text())
    assert pkg["version"] == VERSION


def test_public_docs_reference_current_version():
    for path in [
        "README.md",
        "CHANGELOG.md",
        "ROADMAP.md",
        "RELEASE_CHECKLIST.md",
        "docs/HUGGINGFACE_ORG_CARD.md",
        "docs/HUGGINGFACE_DEPLOYMENT_STATUS.md",
        "docs/KIMARI4B_RUN_HISTORY.md",
        "huggingface/kimari-fit-lab/README.md",
    ]:
        assert VERSION in (REPO / path).read_text(), path


def test_public_model_hashes_are_real():
    """Public models must have real SHA256 hashes (not null or placeholder)."""
    models = json.loads((REPO / "config" / "kimari.models.json").read_text())["models"]
    for m in models:
        if m["id"] in ("recommended", "smollm3-3b-q4"):
            assert m["sha256"] is not None, f"Model {m['id']} has null sha256"
            assert len(m["sha256"]) == 64, f"Model {m['id']} has invalid sha256 length"
            assert all(c in "0123456789abcdef" for c in m["sha256"]), f"Model {m['id']} has non-hex sha256"


def test_validation_doc_exists():
    assert (REPO / "docs" / "LOW_VRAM_AGENT_VALIDATION_V0185.md").exists()


def test_validation_doc_has_download_verification():
    doc = (REPO / "docs" / "LOW_VRAM_AGENT_VALIDATION_V0185.md").read_text()
    assert "SHA256" in doc or "sha256" in doc
    assert "Download" in doc or "download" in doc


def test_agent_profiles_still_valid():
    profiles = json.loads((REPO / "config" / "kimari.profiles.json").read_text())["profiles"]
    for name in ["agent-qwen1060", "agent-qwen1080", "agent-smollm1060"]:
        assert name in profiles, f"Profile {name} missing"
        assert profiles[name]["host"] == "127.0.0.1"
        assert profiles[name]["parallel"] == 1


def test_gate_stays_blocked():
    manager = (REPO / "kimari" / "gateway" / "dashboard_manager.py").read_text()
    assert 'GATE_STATE = "BLOCKED"' in manager


def test_no_kimari4b_in_agent_profiles():
    profiles = json.loads((REPO / "config" / "kimari.profiles.json").read_text())["profiles"]
    for name in ["agent-qwen1060", "agent-qwen1080", "agent-smollm1060"]:
        assert "Kimari" not in profiles[name]["model"]
