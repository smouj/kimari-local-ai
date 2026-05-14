"""Release tests for v0.1.70-alpha.

Focus: subset30 completion evaluation after 100-step full-run.
"""

import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SUMMARY = PROJECT_ROOT / "reports" / "evals" / "kimari_runtime_15b_sft_v1_subset30" / "summary.json"


def test_version_bumped():
    assert 'version = "0.1.70-alpha"' in (PROJECT_ROOT / "pyproject.toml").read_text()
    assert '__version__ = "0.1.70-alpha"' in (PROJECT_ROOT / "kimari" / "__init__.py").read_text()


def test_subset30_summary_exists_and_completed():
    assert SUMMARY.exists()
    data = json.loads(SUMMARY.read_text())
    assert data["status"] == "completed"
    assert data["job_id"] == "6a05236ee48bea4538b9c315"
    assert data["subset_size"] == 30
    assert data["adapter_source_training_job"] == "6a052235e48bea4538b9c309"


def test_subset30_completion_rates():
    data = json.loads(SUMMARY.read_text())
    assert data["baseline_completion_rate"] == 1.0
    assert data["adapter_completion_rate"] == 1.0
    assert data["baseline_completed_items"] == 30
    assert data["adapter_completed_items"] == 30


def test_subset30_safety_flags():
    data = json.loads(SUMMARY.read_text())
    assert data["score_status"] == "not_scored"
    assert data["manual_review_required"] is True
    assert data["raw_outputs_committed"] is False
    assert data["public_benchmark_allowed"] is False
    assert data["gate_state"] == "BLOCKED"


def test_eval_docs_updated():
    result = (PROJECT_ROOT / "docs" / "KIMARI_RUNTIME_15B_SFT_V1_EVAL_RESULT.md").read_text()
    plan = (PROJECT_ROOT / "docs" / "KIMARI_RUNTIME_15B_SFT_V1_EVAL_PLAN.md").read_text()
    assert "SUBSET30 COMPLETED" in result
    assert "6a05236ee48bea4538b9c315" in result
    assert "30/30 (1.0)" in result
    assert "Phase 4: Subset30 Evaluation" in plan
    assert "Scoring/Quality Evaluation" in plan


def test_no_public_model_artifacts():
    dangerous = []
    for pattern in ("*.safetensors", "*.gguf", "adapter_model.bin"):
        for path in PROJECT_ROOT.rglob(pattern):
            if ".venv" not in path.parts and "deps" not in path.parts:
                dangerous.append(str(path))
    assert not dangerous, f"Found public artifacts: {dangerous}"
