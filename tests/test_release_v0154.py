"""Tests for v0.1.54-alpha release criteria.

Validates the real subset10 baseline vs adapter private evaluation:
- Safe subset10 config exists
- Sanitized result summary exists and validates
- Result docs exist
- No raw outputs, public benchmark claims, public weights, or GGUF artifacts
- Gate remains BLOCKED
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import yaml

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent / "kimari-local-ai"
SUMMARY_PATH = PROJECT_ROOT / "reports" / "evals" / "kimari_v0154_baseline_vs_adapter_subset10" / "summary.json"
CONFIG_PATH = PROJECT_ROOT / "eval" / "configs" / "kimari_eval_v1_baseline_vs_adapter_subset10.yaml"
RESULT_DOC = PROJECT_ROOT / "docs" / "KIMARI_EVAL_V0154_RESULT.md"
REPORT_README = PROJECT_ROOT / "reports" / "evals" / "kimari_v0154_baseline_vs_adapter_subset10" / "README.md"
JOB_ID = "6a03be047618f125ee2b7a5a"


def test_version_bumped_to_v0154():
    assert (
        'version = "0.1.54-alpha"' in (PROJECT_ROOT / "pyproject.toml").read_text()
        or 'version = "0.1.56-alpha"' in (PROJECT_ROOT / "pyproject.toml").read_text()
    )
    assert (
        '__version__ = "0.1.54-alpha"' in (PROJECT_ROOT / "kimari" / "__init__.py").read_text()
        or '__version__ = "0.1.56-alpha"' in (PROJECT_ROOT / "kimari" / "__init__.py").read_text()
    )


def test_subset10_config_exists_and_scope():
    assert CONFIG_PATH.exists()
    config = yaml.safe_load(CONFIG_PATH.read_text())
    assert config["base_model"] == "Qwen/Qwen2.5-1.5B-Instruct"
    assert config["adapter_repo_private"] == "Smouj013/kimari4b-micro-sft-adapter-v0"
    assert config["dataset_dir"] == "eval/kimari_private_v1"
    assert config["subset_size"] == 10
    assert config["temperature"] == 0.2
    assert config["max_tokens"] == 256


def test_subset10_config_safety_flags():
    config = yaml.safe_load(CONFIG_PATH.read_text())
    assert config["raw_outputs_commit_allowed"] is False
    assert config["public_benchmark_allowed"] is False
    assert config["manual_review_required"] is True
    assert config["gate_state"] == "BLOCKED"


def test_summary_exists_and_core_fields():
    assert SUMMARY_PATH.exists()
    data = json.loads(SUMMARY_PATH.read_text())
    assert data["job_id"] == JOB_ID
    assert data["hf_job_status"] == "COMPLETED"
    assert data["subset_size"] == 10
    assert data["item_count"] == 10
    assert data["baseline_completion_rate"] == 1.0
    assert data["adapter_completion_rate"] == 1.0
    assert data["adapter_loaded"] is True
    assert data["adapter_load_status"] == "loaded"


def test_summary_safety_flags():
    data = json.loads(SUMMARY_PATH.read_text())
    assert data["score_status"] == "not_scored"
    assert data["manual_review_required"] is True
    assert data["raw_outputs_committed"] is False
    assert data["public_benchmark_allowed"] is False
    assert data["gate_state"] == "BLOCKED"
    assert data["no_public_weights_or_gguf"] is True


def test_summary_validator_passes():
    result = subprocess.run(
        [
            sys.executable,
            "eval/scripts/validate_kimari_eval_summary.py",
            "--summary",
            str(SUMMARY_PATH.relative_to(PROJECT_ROOT)),
            "--json",
        ],
        cwd=PROJECT_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    payload = json.loads(result.stdout)
    assert payload["valid"] is True


def test_result_docs_exist_and_include_required_status():
    assert RESULT_DOC.exists()
    assert REPORT_README.exists()
    text = RESULT_DOC.read_text() + "\n" + REPORT_README.read_text()
    assert JOB_ID in text
    assert "subset" in text.lower() and "10" in text
    assert "100%" in text or "1.0" in text
    assert "adapter" in text.lower() and ("loaded" in text.lower() or "carg" in text.lower())
    assert "BLOCKED" in text
    assert "ready_for_subset30" in text


def test_no_raw_outputs_committed_in_report_tree():
    report_dir = SUMMARY_PATH.parent
    forbidden_names = {"raw_outputs.json", "raw_outputs.jsonl", "raw_responses.json", "generated_text.jsonl"}
    found = [path.name for path in report_dir.rglob("*") if path.name in forbidden_names]
    assert found == []
    summary_text = SUMMARY_PATH.read_text().lower()
    assert "raw_outputs" not in json.loads(SUMMARY_PATH.read_text())
    assert "generated_text" not in summary_text


def test_no_public_benchmark_claim_in_v0154_docs():
    text = (RESULT_DOC.read_text() + "\n" + REPORT_README.read_text()).lower()
    forbidden_claims = ["outperforms", "beats", "sota", "benchmark score", "public benchmark"]
    # The phrase "no public benchmark" is allowed because it is a denial, not a claim.
    normalized = (
        text.replace("no public benchmark", "no-public-eval")
        .replace("not a public benchmark", "not-a-public-eval")
        .replace("public_benchmark_allowed", "public_eval_allowed")
    )
    assert all(claim not in normalized for claim in forbidden_claims)


def test_no_weights_or_gguf_committed():
    safetensors = [p for p in PROJECT_ROOT.rglob("*.safetensors") if ".venv" not in p.parts]
    gguf = [p for p in PROJECT_ROOT.rglob("*.gguf") if ".venv" not in p.parts and "deps" not in p.parts]
    assert safetensors == []
    assert gguf == []


def test_public_docs_show_current_version_and_not_released():
    readme = (PROJECT_ROOT / "README.md").read_text()
    docs_index = (PROJECT_ROOT / "docs" / "index.html").read_text()
    org_card = (PROJECT_ROOT / "docs" / "HUGGINGFACE_ORG_CARD.md").read_text()
    deploy = (PROJECT_ROOT / "docs" / "HUGGINGFACE_DEPLOYMENT_STATUS.md").read_text()
    space = (PROJECT_ROOT / "huggingface" / "kimari-fit-lab" / "README.md").read_text()
    assert "v0.1.54-alpha" in readme or "v0.1.56-alpha" in readme
    assert (
        "version-0.1.54--alpha" in readme
        or "version-0.1.56--alpha" in readme
    )
    assert "version-v0.1.53--alpha" not in readme
    assert "v0.1.54-alpha" in docs_index or "v0.1.56-alpha" in docs_index
    assert "Kimari Local AI v0.1.28-alpha" not in docs_index
    assert "New in v0.1.28-alpha" not in docs_index
    assert "v0.1.54-alpha" in org_card or "v0.1.56-alpha" in org_card
    assert "v0.1.54-alpha" in deploy or "v0.1.56-alpha" in deploy
    assert "v0.1.54-alpha" in space or "v0.1.56-alpha" in space
    combined = (readme + docs_index + org_card + deploy + space).lower()
    assert "not released" in combined
    assert "blocked" in combined


def test_release_check_script_has_v0154_checks():
    script = (PROJECT_ROOT / "scripts" / "release" / "check-release.py").read_text()
    assert "v0.1.54" in script
    assert "kimari_v0154_baseline_vs_adapter_subset10" in script
    assert "baseline_completion_rate" in script
    assert "adapter_completion_rate" in script


if __name__ == "__main__":
    import pytest

    sys.exit(pytest.main([__file__, "-v"]))
