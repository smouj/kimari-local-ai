"""Release tests for v0.1.65-alpha.

SFT v1 eval subset10 infrastructure:
- Eval runner exists
- Adapter load checker exists
- Summary template + validator
- Report directory + summary
- Eval result doc
- Gate BLOCKED
"""

import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

SUMMARY_PATH = PROJECT_ROOT / "docs" / "assets" / "results" / "sft_v1_run_summary.json"
EVAL_CONFIG = PROJECT_ROOT / "eval" / "configs" / "kimari_runtime_15b_sft_v1_eval_subset10.yaml"
EVAL_RUNNER = PROJECT_ROOT / "eval" / "scripts" / "run_sft_v1_eval.py"
LOAD_CHECKER = PROJECT_ROOT / "eval" / "scripts" / "check_sft_v1_adapter_load.py"
SUMMARY_TEMPLATE = PROJECT_ROOT / "eval" / "templates" / "sft_v1_eval_summary.template.json"
SUMMARY_VALIDATOR = PROJECT_ROOT / "eval" / "scripts" / "validate_sft_v1_eval_summary.py"
REPORT_DIR = PROJECT_ROOT / "reports" / "evals" / "kimari_runtime_15b_sft_v1_subset10"
REPORT_SUMMARY = REPORT_DIR / "summary.json"
EVAL_RESULT_DOC = PROJECT_ROOT / "docs" / "KIMARI_RUNTIME_15B_SFT_V1_EVAL_RESULT.md"


def test_version_is_0165():
    """Package version must be 0.1.65-alpha."""
    import kimari

    assert kimari.__version__ == "0.1.65-alpha", f"Expected 0.1.65-alpha, got {kimari.__version__}"


def test_pyproject_version():
    """pyproject.toml version must be 0.1.65-alpha."""
    pyproject = (PROJECT_ROOT / "pyproject.toml").read_text()
    assert 'version = "0.1.65-alpha"' in pyproject, "pyproject.toml version mismatch"


def test_eval_runner_exists():
    """Eval runner script must exist."""
    assert EVAL_RUNNER.exists(), f"Eval runner not found: {EVAL_RUNNER}"


def test_eval_runner_no_shell_true():
    """Eval runner must not use shell=True in subprocess calls."""
    if EVAL_RUNNER.exists():
        text = EVAL_RUNNER.read_text()
        # Check for actual usage (in subprocess calls), not docstrings/comments
        lines = text.splitlines()
        for i, line in enumerate(lines):
            if (
                "shell=True" in line
                and not line.strip().startswith("#")
                and not line.strip().startswith('"')
                and "No shell" not in line
            ):
                raise AssertionError(f"Eval runner must not use shell=True (line {i + 1})")


def test_eval_runner_no_token_flag():
    """Eval runner must not accept --token flag."""
    if EVAL_RUNNER.exists():
        text = EVAL_RUNNER.read_text()
        assert '"--token"' not in text and "'--token'" not in text, "Eval runner must not accept --token flag"


def test_load_checker_exists():
    """Adapter load checker must exist."""
    assert LOAD_CHECKER.exists(), f"Load checker not found: {LOAD_CHECKER}"


def test_load_checker_has_dry_run():
    """Load checker must support --dry-run."""
    if LOAD_CHECKER.exists():
        text = LOAD_CHECKER.read_text()
        assert "--dry-run" in text, "Load checker must support --dry-run"


def test_summary_template_exists():
    """Eval summary template must exist."""
    assert SUMMARY_TEMPLATE.exists(), f"Summary template not found: {SUMMARY_TEMPLATE}"


def test_summary_template_valid_json():
    """Summary template must be valid JSON."""
    data = json.loads(SUMMARY_TEMPLATE.read_text())
    assert isinstance(data, dict), "Template must be a JSON dict"


def test_summary_template_safety_flags():
    """Summary template must have correct safety flags."""
    data = json.loads(SUMMARY_TEMPLATE.read_text())
    assert data.get("raw_outputs_committed") is False, "raw_outputs_committed must be false"
    assert data.get("public_benchmark_allowed") is False, "public_benchmark_allowed must be false"
    assert data.get("manual_review_required") is True, "manual_review_required must be true"
    assert data.get("gate_state") == "BLOCKED", "gate_state must be BLOCKED"
    assert data.get("subset_size") == 10, "subset_size must be 10"


def test_summary_validator_exists():
    """Summary validator must exist."""
    assert SUMMARY_VALIDATOR.exists(), f"Summary validator not found: {SUMMARY_VALIDATOR}"


def test_report_dir_exists():
    """Report directory must exist."""
    assert REPORT_DIR.exists(), f"Report dir not found: {REPORT_DIR}"


def test_report_summary_exists():
    """Report summary.json must exist."""
    assert REPORT_SUMMARY.exists(), f"Report summary not found: {REPORT_SUMMARY}"


def test_report_summary_safety_flags():
    """Report summary must have correct safety flags."""
    data = json.loads(REPORT_SUMMARY.read_text())
    assert data.get("raw_outputs_committed") is False, "raw_outputs_committed must be false"
    assert data.get("public_benchmark_allowed") is False, "public_benchmark_allowed must be false"
    assert data.get("gate_state") == "BLOCKED", "gate_state must be BLOCKED"


def test_eval_result_doc_exists():
    """Eval result doc must exist."""
    assert EVAL_RESULT_DOC.exists(), f"Eval result doc not found: {EVAL_RESULT_DOC}"


def test_eval_result_doc_gate_blocked():
    """Eval result doc must show gate BLOCKED."""
    text = EVAL_RESULT_DOC.read_text().lower()
    assert "blocked" in text, "Eval result doc must show gate BLOCKED"


def test_eval_result_doc_no_public_benchmark():
    """Eval result doc must address no public benchmark."""
    text = EVAL_RESULT_DOC.read_text().lower()
    assert "no public" in text or "public_benchmark_allowed" in text, "Eval result doc must address no public benchmark"


def test_no_public_weights():
    """No public weights/adapters/GGUF in repo."""
    patterns = ["*.safetensors", "*.gguf", "adapter_model.bin"]
    for pattern in patterns:
        matches = list(PROJECT_ROOT.rglob(pattern))
        matches = [m for m in matches if ".venv" not in str(m) and "deps" not in str(m)]
        assert len(matches) == 0, f"Found public artifact: {matches}"


def test_no_secrets_in_report():
    """Report summary must not contain tokens or secrets."""
    if REPORT_SUMMARY.exists():
        import re

        text = REPORT_SUMMARY.read_text()
        secret_patterns = [r"sk-proj-", r"ghp_", r"hf_[a-zA-Z]{30,}", r"AKIA[0-9A-Z]{16}"]
        for pattern in secret_patterns:
            assert not re.search(pattern, text), f"Report contains secret pattern: {pattern}"


def test_check_release_handles_completed():
    """check-release.py must handle COMPLETED status conditionally for v0.1.62."""
    check_release = (PROJECT_ROOT / "scripts" / "release" / "check-release.py").read_text()
    assert "result_completed" in check_release, "check-release must handle COMPLETED status conditionally"
