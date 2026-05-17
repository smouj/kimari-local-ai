"""Release validation tests for v0.1.84-alpha."""

from __future__ import annotations

import json
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
VERSION = "0.1.84-alpha"


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


def test_agent_profiles_exist():
    profiles = json.loads((REPO / "config" / "kimari.profiles.json").read_text())["profiles"]
    for name in ["agent-qwen1060", "agent-qwen1080", "agent-smollm1060"]:
        assert name in profiles, f"Profile {name} missing"


def test_run_agents_now_doc_exists():
    assert (REPO / "docs" / "RUN_AGENTS_NOW.md").exists()


def test_dashboard_node_requirement():
    readme = (REPO / "apps" / "gateway-dashboard" / "README.md").read_text()
    assert "20.9+" in readme, "Dashboard README must reference Node 20.9+"


def test_cuda_arch_support_in_build_script():
    script = (REPO / "scripts" / "linux" / "build-llamacpp-cuda.sh").read_text()
    assert "KIMARI_CUDA_ARCH" in script, "Build script must reference KIMARI_CUDA_ARCH"
    assert "CMAKE_CUDA_ARCHITECTURES" in script, "Build script must use CMAKE_CUDA_ARCHITECTURES"


def test_gate_stays_blocked():
    manager = (REPO / "kimari" / "gateway" / "dashboard_manager.py").read_text()
    assert 'GATE_STATE = "BLOCKED"' in manager


def test_no_kimari4b_in_agent_profiles():
    profiles = json.loads((REPO / "config" / "kimari.profiles.json").read_text())["profiles"]
    for name in ["agent-qwen1060", "agent-qwen1080", "agent-smollm1060"]:
        assert "Kimari" not in profiles[name]["model"]
