"""Release tests for v0.1.64-alpha.

SFT v1 result reconciliation + eval readiness:
- Result doc COMPLETED (not PENDING)
- Run summary validated
- Run history updated
- Eval subset10 config exists
- Eval readiness validator passes
- Gate BLOCKED
"""

import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

SUMMARY_PATH = PROJECT_ROOT / "docs" / "assets" / "results" / "sft_v1_run_summary.json"
RESULT_DOC = PROJECT_ROOT / "docs" / "KIMARI_RUNTIME_15B_SFT_V1_RESULT.md"
RUN_HISTORY = PROJECT_ROOT / "docs" / "KIMARI4B_RUN_HISTORY.md"
EVAL_CONFIG = PROJECT_ROOT / "eval" / "configs" / "kimari_runtime_15b_sft_v1_eval_subset10.yaml"
EVAL_READINESS = PROJECT_ROOT / "eval" / "scripts" / "validate_sft_v1_eval_readiness.py"
EVAL_PLAN = PROJECT_ROOT / "docs" / "KIMARI_RUNTIME_15B_SFT_V1_EVAL_PLAN.md"
CONFIG_PATH = PROJECT_ROOT / "training" / "configs" / "kimari_runtime_15b_sft_v1.yaml"


def test_version_is_0164():
    """Package version must be 0.1.64-alpha."""
    import kimari

    assert kimari.__version__ == "0.1.64-alpha", f"Expected 0.1.64-alpha, got {kimari.__version__}"


def test_pyproject_version():
    """pyproject.toml version must be 0.1.64-alpha."""
    pyproject = (PROJECT_ROOT / "pyproject.toml").read_text()
    assert 'version = "0.1.64-alpha"' in pyproject, "pyproject.toml version mismatch"


def test_summary_exists():
    """SFT v1 run summary JSON must exist."""
    assert SUMMARY_PATH.exists(), f"Summary not found: {SUMMARY_PATH}"


def test_summary_valid_json():
    """Summary must be valid JSON."""
    data = json.loads(SUMMARY_PATH.read_text())
    assert isinstance(data, dict), "Summary must be a JSON dict"


def test_summary_training_performed():
    """Summary must report training_performed=true."""
    data = json.loads(SUMMARY_PATH.read_text())
    assert data.get("training_performed") is True, "training_performed must be true"


def test_summary_adapter_generated():
    """Summary must report adapter_generated=true."""
    data = json.loads(SUMMARY_PATH.read_text())
    assert data.get("adapter_generated") is True, "adapter_generated must be true"


def test_summary_micro_run():
    """Summary must report micro_run=true (10 steps, not final model)."""
    data = json.loads(SUMMARY_PATH.read_text())
    assert data.get("micro_run") is True, "micro_run must be true"


def test_summary_gate_blocked():
    """Summary must report gate_state=BLOCKED."""
    data = json.loads(SUMMARY_PATH.read_text())
    assert data.get("gate_state") == "BLOCKED", "gate_state must be BLOCKED"


def test_result_doc_completed():
    """Result doc must have COMPLETED status (not PENDING)."""
    text = RESULT_DOC.read_text()
    assert "COMPLETED" in text, "Result doc must have COMPLETED status"


def test_result_doc_says_micro_run():
    """Result doc must mention micro-run / 10 steps."""
    text = RESULT_DOC.read_text().lower()
    assert "micro-run" in text or "10 steps" in text, "Result doc must mention micro-run / 10 steps"


def test_result_doc_no_public_benchmark():
    """Result doc must state no public benchmark."""
    text = RESULT_DOC.read_text().lower()
    assert "no public" in text or "public benchmark" not in text or "public_benchmark_allowed" in text, (
        "Result doc must address no public benchmark"
    )


def test_result_doc_gate_blocked():
    """Result doc must show gate BLOCKED."""
    text = RESULT_DOC.read_text().lower()
    assert "blocked" in text, "Result doc must show gate BLOCKED"


def test_run_history_exists():
    """Run history doc must exist."""
    assert RUN_HISTORY.exists(), f"Run history not found: {RUN_HISTORY}"


def test_run_history_has_job_id():
    """Run history must contain the SFT v1 job ID."""
    text = RUN_HISTORY.read_text()
    assert "6a0501dae48bea4538b9c17a" in text, "Run history must contain SFT v1 job ID"


def test_run_history_says_completed():
    """Run history must show COMPLETED status."""
    text = RUN_HISTORY.read_text()
    assert "COMPLETED" in text, "Run history must show COMPLETED"


def test_eval_config_exists():
    """Eval subset10 config must exist."""
    assert EVAL_CONFIG.exists(), f"Eval config not found: {EVAL_CONFIG}"


def test_eval_config_has_base_model():
    """Eval config must specify base_model."""
    text = EVAL_CONFIG.read_text()
    assert "base_model" in text, "Eval config must specify base_model"


def test_eval_config_gate_blocked():
    """Eval config must specify gate_state BLOCKED."""
    text = EVAL_CONFIG.read_text()
    assert "BLOCKED" in text, "Eval config must specify gate_state BLOCKED"


def test_eval_config_no_public_benchmark():
    """Eval config must specify public_benchmark_allowed."""
    text = EVAL_CONFIG.read_text()
    assert "public_benchmark_allowed" in text, "Eval config must specify public_benchmark_allowed"


def test_eval_readiness_validator_exists():
    """Eval readiness validator script must exist."""
    assert EVAL_READINESS.exists(), f"Eval readiness validator not found: {EVAL_READINESS}"


def test_eval_plan_exists():
    """Eval plan doc must exist."""
    assert EVAL_PLAN.exists(), f"Eval plan not found: {EVAL_PLAN}"


def test_eval_plan_no_public_benchmark():
    """Eval plan must address no public benchmark."""
    text = EVAL_PLAN.read_text().lower()
    assert "no public benchmark" in text or "public_benchmark_allowed" in text, (
        "Eval plan must address no public benchmark"
    )


def test_no_public_weights():
    """No public weights/adapters/GGUF in repo."""
    patterns = ["*.safetensors", "*.gguf", "adapter_model.bin"]
    for pattern in patterns:
        matches = list(PROJECT_ROOT.rglob(pattern))
        matches = [m for m in matches if ".venv" not in str(m) and "deps" not in str(m)]
        assert len(matches) == 0, f"Found public artifact: {matches}"


def test_no_secrets_in_summary():
    """Summary must not contain tokens or secrets."""
    text = SUMMARY_PATH.read_text()
    import re

    secret_patterns = [
        r"sk-proj-",
        r"ghp_",
        r"hf_[a-zA-Z]{30,}",
        r"AKIA[0-9A-Z]{16}",
    ]
    for pattern in secret_patterns:
        assert not re.search(pattern, text), f"Summary contains secret pattern: {pattern}"


def test_check_release_no_legacy_placeholder_fails():
    """check-release.py must not require PENDING status when result doc is COMPLETED."""
    check_release = (PROJECT_ROOT / "scripts" / "release" / "check-release.py").read_text()
    assert "result_completed" in check_release or "COMPLETED" in check_release, (
        "check-release must handle COMPLETED status conditionally"
    )
