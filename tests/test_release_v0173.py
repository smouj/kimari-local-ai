"""Release tests for v0.1.73-alpha.

Focus: 500-step training and private scoring result.
"""

import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SUMMARY = PROJECT_ROOT / "reports" / "evals" / "kimari_runtime_15b_sft_v1_500step_scoring_subset30" / "summary.json"


def test_version_bumped():
    pyproject = (PROJECT_ROOT / "pyproject.toml").read_text()
    init = (PROJECT_ROOT / "kimari" / "__init__.py").read_text()
    assert 'version = "0.1.73-alpha"' in pyproject or 'version = "0.1.74-alpha"' in pyproject
    assert '__version__ = "0.1.73-alpha"' in init or '__version__ = "0.1.74-alpha"' in init


def test_500_step_summary_is_sanitized_and_complete():
    data = json.loads(SUMMARY.read_text())
    assert data["status"] == "completed"
    assert data["training_job_id"] == "6a052ce6e48bea4538b9c365"
    assert data["job_id"] == "6a052f5ce48bea4538b9c37d"
    assert data["adapter_training_steps"] == 500
    assert data["raw_outputs_committed"] is False
    assert data["public_benchmark_allowed"] is False
    assert data["gate_state"] == "BLOCKED"


def test_500_step_beats_baseline_and_100_step():
    data = json.loads(SUMMARY.read_text())
    assert data["adapter"]["proxy_score"] > data["baseline"]["proxy_score"]
    assert (
        data["comparison_to_100_step_adapter"]["new_500_step_proxy_score"]
        > data["comparison_to_100_step_adapter"]["previous_100_step_proxy_score"]
    )
    assert data["comparison_to_100_step_adapter"]["relative_delta_multiplier"] > 1.5
    assert data["decision"]["is_adapter_better_than_base"] is True
    assert data["decision"]["is_500_step_better_than_100_step"] is True


def test_training_signal_improved():
    data = json.loads(SUMMARY.read_text())
    training = data["training_summary"]
    assert training["eval_loss_step_500"] < training["eval_loss_step_50"]
    assert training["eval_mean_token_accuracy_step_500"] > training["eval_mean_token_accuracy_step_50"]
    assert training["adapter_upload_completed"] is True


def test_no_raw_outputs_committed_in_500_step_report():
    text = SUMMARY.read_text().lower()
    assert "generated" not in text
    assert "prompt" not in text
    assert '"ideal"' not in text
    assert "raw_outputs_private.json" in text


def test_no_public_model_artifacts():
    dangerous = []
    for pattern in ("*.safetensors", "*.gguf", "adapter_model.bin"):
        for path in PROJECT_ROOT.rglob(pattern):
            if ".venv" not in path.parts and "deps" not in path.parts:
                dangerous.append(str(path))
    assert not dangerous, f"Found public artifacts: {dangerous}"
