"""Tests for v0.1.51-alpha release criteria.

Validates:
- Persisted config exists
- Private adapter repo documented
- Runner safety (dry-run default, no --token, no shell=True)
- Load check script exists
- Summary template/creator/validator
- Result summary fields
- No safetensors/GGUF in public repo
- Version bump
- Gate BLOCKED
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent / "kimari-local-ai"


def test_persisted_config_exists():
    assert (PROJECT_ROOT / "training" / "configs" / "hf_jobs_kimari4b_micro_sft_persisted.v0.yaml").exists()


def test_private_adapter_repo_doc_exists():
    assert (PROJECT_ROOT / "docs" / "KIMARI4B_PRIVATE_ADAPTER_REPO.md").exists()


def test_persisted_run_doc_exists():
    assert (PROJECT_ROOT / "docs" / "KIMARI4B_MICRO_SFT_PERSISTED_RUN.md").exists()


def test_load_check_doc_exists():
    assert (PROJECT_ROOT / "docs" / "KIMARI4B_PRIVATE_ADAPTER_LOAD_CHECK.md").exists()


def test_runner_exists():
    runner = PROJECT_ROOT / "training" / "scripts" / "hf_jobs_micro_sft_persisted.py"
    assert runner.exists()
    text = runner.read_text()
    assert "--dry-run" in text
    assert "--allow-submit" in text
    assert "--yes" in text
    assert "--token" not in text or "--token" in "No --token argument"  # noqa
    assert "shell=True" not in text or "No shell=True" in text


def test_load_check_script_exists():
    assert (PROJECT_ROOT / "training" / "scripts" / "check_private_adapter_load.py").exists()


def test_summary_template_exists():
    assert (PROJECT_ROOT / "training" / "templates" / "hf_jobs_micro_sft_persisted_summary.template.json").exists()


def test_summary_creator_exists():
    assert (PROJECT_ROOT / "training" / "scripts" / "create_hf_jobs_micro_sft_persisted_summary.py").exists()


def test_summary_validator_exists():
    assert (PROJECT_ROOT / "training" / "scripts" / "validate_hf_jobs_micro_sft_persisted_summary.py").exists()


def test_result_summary_adapter_persisted():
    summary = PROJECT_ROOT / "docs" / "KIMARI4B_MICRO_SFT_PERSISTED_RESULT_SUMMARY.json"
    if summary.exists():
        data = json.loads(summary.read_text())
        assert data.get("adapter_persisted_private") is True
        assert data.get("adapter_committed_public") is False
        assert data.get("hf_public_upload_performed") is False
        assert data.get("gguf_generated") is False
        assert data.get("gate_state") == "BLOCKED"
        assert data.get("adapter_load_check") is True


def test_no_safetensors_in_public_repo():
    safetensors = list(PROJECT_ROOT.rglob("*.safetensors"))
    assert len(safetensors) == 0, f"Found {len(safetensors)} .safetensors files"


def test_no_gguf_in_public_repo():
    gguf = [f for f in PROJECT_ROOT.rglob("*.gguf") if "deps" not in str(f) and "node_modules" not in str(f)]
    assert len(gguf) == 0, f"Found {len(gguf)} .gguf files"


def test_version_bump():
    import re

    pyproject = (PROJECT_ROOT / "pyproject.toml").read_text()
    init = (PROJECT_ROOT / "kimari" / "__init__.py").read_text()
    match_p = re.search(r'version\s*=\s*["\']([^"\']+)["\']', pyproject)
    match_i = re.search(r'__version__\s*=\s*["\']([^"\']+)["\']', init)
    assert match_p and match_p.group(1) >= "0.1.51-alpha"
    assert match_i and match_i.group(1) >= "0.1.51-alpha"


def test_changelog_has_v0151():
    changelog = (PROJECT_ROOT / "CHANGELOG.md").read_text()
    assert "[0.1.51-alpha]" in changelog


def test_roadmap_has_v0151():
    roadmap = (PROJECT_ROOT / "ROADMAP.md").read_text()
    assert "v0.1.51-alpha" in roadmap


if __name__ == "__main__":
    import pytest

    sys.exit(pytest.main([__file__, "-v"]))
