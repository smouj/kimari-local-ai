"""Tests for v0.1.50-alpha release criteria.

Validates:
- Dataset hash consistency
- Adapter persistence strategy docs
- Private repo policy
- Package adapter script safety
- No safetensors/GGUF in public repo
- Version bump
- Gate BLOCKED
"""

from __future__ import annotations

import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent / "kimari-local-ai"


def test_hash_dataset_script_exists():
    assert (PROJECT_ROOT / "training" / "scripts" / "hash_dataset.py").exists()


def test_no_contradictory_dataset_hashes():
    config_path = PROJECT_ROOT / "training" / "configs" / "hf_jobs_kimari4b_micro_sft_real.v0.yaml"
    report_path = PROJECT_ROOT / "dataset" / "build" / "kimari-fit-v0" / "report.json"

    try:
        import yaml

        config = yaml.safe_load(config_path.read_text())
    except ImportError:
        return

    report = json.loads(report_path.read_text())

    # Config hash should match report file_sha256 (prefix comparison since config may truncate)
    config_hash = config.get("dataset", {}).get("hash", "")
    report_hash = report.get("file_sha256", report.get("sha256", ""))

    assert config_hash == report_hash[: len(config_hash)], (
        f"Config hash {config_hash} != report hash {report_hash[: len(config_hash)]}"
    )


def test_result_review_exists():
    assert (PROJECT_ROOT / "docs" / "KIMARI4B_MICRO_SFT_RESULT_REVIEW.md").exists()


def test_persistence_strategy_exists():
    assert (PROJECT_ROOT / "docs" / "KIMARI4B_ADAPTER_PERSISTENCE_STRATEGY.md").exists()


def test_private_repo_policy_exists():
    assert (PROJECT_ROOT / "docs" / "PRIVATE_ARTIFACT_REPO_POLICY.md").exists()


def test_package_adapter_script_exists():
    script = PROJECT_ROOT / "training" / "scripts" / "package_private_adapter.py"
    assert script.exists()
    text = script.read_text()
    assert "--write" in text
    assert "--yes" in text


def test_validate_private_repo_script_exists():
    assert (PROJECT_ROOT / "training" / "scripts" / "validate_private_artifact_repo.py").exists()


def test_next_run_plan_exists():
    assert (PROJECT_ROOT / "docs" / "KIMARI4B_NEXT_RUN_PLAN.md").exists()


def test_no_safetensors_in_public_repo():
    safetensors = list(PROJECT_ROOT.rglob("*.safetensors"))
    assert len(safetensors) == 0, f"Found {len(safetensors)} .safetensors files"


def test_no_gguf_in_public_repo():
    gguf = [f for f in PROJECT_ROOT.rglob("*.gguf") if "deps" not in str(f) and "node_modules" not in str(f)]
    assert len(gguf) == 0, f"Found {len(gguf)} .gguf files (excluding deps/)"


def test_version_bump():
    import re

    pyproject = (PROJECT_ROOT / "pyproject.toml").read_text()
    init = (PROJECT_ROOT / "kimari" / "__init__.py").read_text()
    match_p = re.search(r'version\s*=\s*["\']([^"\']+)["\']', pyproject)
    match_i = re.search(r'__version__\s*=\s*["\']([^"\']+)["\']', init)
    assert match_p and match_p.group(1) >= "0.1.50-alpha"
    assert match_i and match_i.group(1) >= "0.1.50-alpha"


def test_changelog_has_v0150():
    changelog = (PROJECT_ROOT / "CHANGELOG.md").read_text()
    assert "[0.1.50-alpha]" in changelog


def test_roadmap_has_v0150():
    roadmap = (PROJECT_ROOT / "ROADMAP.md").read_text()
    assert "v0.1.50-alpha" in roadmap


def test_result_says_adapter_ephemeral():
    result = (PROJECT_ROOT / "docs" / "KIMARI4B_MICRO_SFT_RESULT.md").read_text().lower()
    assert "ephemeral" in result or "not retained" in result


def test_summary_has_explicit_hashes():
    summary = json.loads((PROJECT_ROOT / "docs" / "KIMARI4B_MICRO_SFT_RESULT_SUMMARY.json").read_text())
    assert "dataset_file_sha256" in summary
    assert "dataset_normalized_sha256" in summary


def test_gate_blocked():
    summary = json.loads((PROJECT_ROOT / "docs" / "KIMARI4B_MICRO_SFT_RESULT_SUMMARY.json").read_text())
    assert summary.get("gate_state") == "BLOCKED"
    assert summary.get("adapter_committed") is False
    assert summary.get("hf_upload_performed") is False


if __name__ == "__main__":
    import sys

    import pytest

    sys.exit(pytest.main([__file__, "-v"]))
