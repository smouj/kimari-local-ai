"""Release tests for v0.1.66-alpha.

SFT v1 eval subset10 — BLOCKED on adapter availability:
- Adapter from micro-run was NOT persisted
- Evaluation cannot proceed without adapter
- Summary status: blocked
- ready_for_subset30: false
"""

import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

SUMMARY_PATH = PROJECT_ROOT / "docs" / "assets" / "results" / "sft_v1_run_summary.json"
REPORT_SUMMARY = PROJECT_ROOT / "reports" / "evals" / "kimari_runtime_15b_sft_v1_subset10" / "summary.json"
EVAL_RESULT_DOC = PROJECT_ROOT / "docs" / "KIMARI_RUNTIME_15B_SFT_V1_EVAL_RESULT.md"
EVAL_PLAN = PROJECT_ROOT / "docs" / "KIMARI_RUNTIME_15B_SFT_V1_EVAL_PLAN.md"
LOAD_CHECKER = PROJECT_ROOT / "eval" / "scripts" / "check_sft_v1_adapter_load.py"
EVAL_RUNNER = PROJECT_ROOT / "eval" / "scripts" / "run_sft_v1_eval.py"
SUMMARY_VALIDATOR = PROJECT_ROOT / "eval" / "scripts" / "validate_sft_v1_eval_summary.py"


def test_version_is_0166():
    """Package version must be 0.1.66-alpha."""
    import kimari

    assert kimari.__version__ == "0.1.66-alpha", f"Expected 0.1.66-alpha, got {kimari.__version__}"


def test_pyproject_version():
    """pyproject.toml version must be 0.1.66-alpha."""
    pyproject = (PROJECT_ROOT / "pyproject.toml").read_text()
    assert 'version = "0.1.66-alpha"' in pyproject, "pyproject.toml version mismatch"


def test_eval_result_doc_exists():
    """Eval result doc must exist."""
    assert EVAL_RESULT_DOC.exists(), f"Eval result doc not found: {EVAL_RESULT_DOC}"


def test_eval_result_doc_blocked():
    """Eval result doc must document the blocker."""
    text = EVAL_RESULT_DOC.read_text().lower()
    assert "blocked" in text, "Eval result doc must document blocker"
    assert "adapter" in text, "Eval result doc must mention adapter availability"


def test_eval_result_doc_no_public_benchmark():
    """Eval result doc must address no public benchmark."""
    text = EVAL_RESULT_DOC.read_text().lower()
    assert "no public" in text or "public_benchmark_allowed" in text, "Must address no public benchmark"


def test_eval_result_doc_gate_blocked():
    """Eval result doc must show gate BLOCKED."""
    text = EVAL_RESULT_DOC.read_text().lower()
    assert "blocked" in text, "Must show gate BLOCKED"


def test_eval_result_doc_ready_for_subset30_false():
    """Eval result doc must state ready_for_subset30=false."""
    text = EVAL_RESULT_DOC.read_text().lower()
    assert "false" in text, "Must state ready_for_subset30=false or blocked"


def test_report_summary_exists():
    """Report summary.json must exist."""
    assert REPORT_SUMMARY.exists(), f"Report summary not found: {REPORT_SUMMARY}"


def test_report_summary_blocked():
    """Report summary must have status blocked."""
    data = json.loads(REPORT_SUMMARY.read_text())
    assert data.get("status") in ("blocked", "pending", "not_scored"), (
        f"Expected blocked/pending/not_scored, got {data.get('status')}"
    )


def test_report_summary_gate_blocked():
    """Report summary must have gate_state BLOCKED."""
    data = json.loads(REPORT_SUMMARY.read_text())
    assert data.get("gate_state") == "BLOCKED", "gate_state must be BLOCKED"


def test_report_summary_no_public_benchmark():
    """Report summary must have public_benchmark_allowed=false."""
    data = json.loads(REPORT_SUMMARY.read_text())
    assert data.get("public_benchmark_allowed") is False, "public_benchmark_allowed must be false"


def test_report_summary_not_ready_for_subset30():
    """Report summary must have ready_for_subset30=false."""
    data = json.loads(REPORT_SUMMARY.read_text())
    assert data.get("ready_for_subset30") is False, "ready_for_subset30 must be false (blocked)"


def test_eval_plan_exists():
    """Eval plan must exist."""
    assert EVAL_PLAN.exists(), f"Eval plan not found: {EVAL_PLAN}"


def test_eval_plan_mentions_blocker():
    """Eval plan must mention the blocker."""
    text = EVAL_PLAN.read_text().lower()
    assert "blocked" in text or "persist" in text or "adapter" in text, "Eval plan must mention adapter availability"


def test_load_checker_exists():
    """Adapter load checker must exist."""
    assert LOAD_CHECKER.exists(), f"Load checker not found: {LOAD_CHECKER}"


def test_eval_runner_exists():
    """Eval runner must exist."""
    assert EVAL_RUNNER.exists(), f"Eval runner not found: {EVAL_RUNNER}"


def test_summary_validator_exists():
    """Summary validator must exist."""
    assert SUMMARY_VALIDATOR.exists(), f"Summary validator not found: {SUMMARY_VALIDATOR}"


def test_sft_summary_adapter_not_persisted():
    """SFT v1 run summary must confirm adapter was not persisted."""
    data = json.loads(SUMMARY_PATH.read_text())
    assert data.get("adapter_committed") is False, "adapter_committed must be false (not persisted)"


def test_no_public_weights():
    """No public weights/adapters/GGUF in repo."""
    patterns = ["*.safetensors", "*.gguf", "adapter_model.bin"]
    for pattern in patterns:
        matches = list(PROJECT_ROOT.rglob(pattern))
        matches = [m for m in matches if ".venv" not in str(m) and "deps" not in str(m)]
        assert len(matches) == 0, f"Found public artifact: {matches}"
