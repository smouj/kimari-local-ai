"""Release validation tests for v0.1.86-alpha."""

from __future__ import annotations

import json
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
VERSION = "0.1.86-alpha"


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
    """Public models must have real SHA256 hashes."""
    models = json.loads((REPO / "config" / "kimari.models.json").read_text())["models"]
    for m in models:
        if m["id"] in ("recommended", "smollm3-3b-q4"):
            assert m["sha256"] is not None, f"Model {m['id']} has null sha256"
            assert len(m["sha256"]) == 64, f"Model {m['id']} has invalid sha256 length"


def test_inference_validation_doc_exists():
    assert (REPO / "docs" / "CPU_INFERENCE_VALIDATION_V0186.md").exists()


def test_inference_validation_doc_is_honest():
    doc = (REPO / "docs" / "CPU_INFERENCE_VALIDATION_V0186.md").read_text()
    # Must NOT claim GPU inference was tested
    assert "NOT TESTED" in doc or "not tested" in doc.lower() or "no GPU" in doc.lower()
    # Must mention CPU-only
    assert "CPU" in doc
    # Must have endpoint verification
    assert "/health" in doc
    assert "/v1/chat/completions" in doc


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
