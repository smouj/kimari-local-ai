"""Release validation tests for v0.1.87-alpha."""

from __future__ import annotations

import json
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
VERSION = "0.1.87-alpha"


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


def test_cuda_validation_doc_exists():
    assert (REPO / "docs" / "CUDA_INFERENCE_VALIDATION_V0187.md").exists()


def test_cuda_validation_doc_content():
    doc = (REPO / "docs" / "CUDA_INFERENCE_VALIDATION_V0187.md").read_text()
    assert "GTX 1060" in doc
    assert "CUDA" in doc
    assert ("compute capability 6.1" in doc) or ("cc 6.1" in doc)
    assert "offloaded 23/23 layers to GPU" in doc
    assert "2203 MiB" in doc
    assert "1159.20 tok/s" in doc
    assert "103.63 tok/s" in doc
    assert "11436" in doc

    qwen_pending = ("Qwen3" in doc) and (("Pending" in doc) or ("pending" in doc) or ("not tested" in doc.lower()))
    smol_pending = ("SmolLM3" in doc) and (("Pending" in doc) or ("pending" in doc) or ("not tested" in doc.lower()))
    assert qwen_pending
    assert smol_pending

    assert "Qwen3 GPU validated" not in doc
    assert "SmolLM3 GPU validated" not in doc


def test_gate_stays_blocked():
    manager = (REPO / "kimari" / "gateway" / "dashboard_manager.py").read_text()
    assert 'GATE_STATE = "BLOCKED"' in manager
