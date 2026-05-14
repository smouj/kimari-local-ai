"""Release tests for v0.1.75-alpha.

Focus: private raw-output retrieval attempt and safe blocked manual review state.
"""

import json
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SUMMARY = PROJECT_ROOT / "reports" / "evals" / "kimari_runtime_15b_500step_subset30" / "manual_review_summary.json"
DOC = PROJECT_ROOT / "docs" / "KIMARI_RUNTIME_15B_500STEP_MANUAL_REVIEW.md"
VALIDATOR = PROJECT_ROOT / "eval" / "scripts" / "validate_manual_review_summary.py"
GENERATOR = PROJECT_ROOT / "eval" / "scripts" / "create_manual_review_from_private_raw.py"


def test_version_at_least_v0175():
    pyproject = (PROJECT_ROOT / "pyproject.toml").read_text()
    init = (PROJECT_ROOT / "kimari" / "__init__.py").read_text()
    assert 'version = "0.1.7' in pyproject
    assert '__version__ = "0.1.7' in init


def test_manual_review_tooling_exists():
    assert SUMMARY.exists()
    assert DOC.exists()
    assert VALIDATOR.exists()
    assert GENERATOR.exists()


def test_manual_review_summary_records_missing_raw_outputs_safely():
    data = json.loads(SUMMARY.read_text())
    assert data["scoring_job_id"] in {"6a052f5ce48bea4538b9c37d", "6a0590cce48bea4538b9c7b9"}
    assert data["training_job_id"] == "6a052ce6e48bea4538b9c365"
    assert data["subset_size"] == 30
    assert data["adapter_500_wins"] == 17
    assert data["base_wins"] == 12
    assert data["ties"] == 1
    assert data["manual_review_status"] in {"blocked_missing_raw_outputs", "ready", "completed"}
    assert 0 <= data["reviewed_items"] <= data["subset_size"]
    assert data["decision"] in {"blocked_missing_raw_outputs", "inconclusive", "safety_fix_required"}
    assert data["raw_outputs_committed"] is False
    assert data["public_benchmark_allowed"] is False
    assert data["gate_state"] == "BLOCKED"


def test_validator_passes():
    result = subprocess.run(
        [sys.executable, str(VALIDATOR), "--summary", str(SUMMARY), "--json"],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert json.loads(result.stdout)["valid"] is True


def test_no_raw_outputs_in_repo_or_summary():
    tracked = subprocess.run(
        ["git", "ls-files"],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )
    assert "raw_outputs_private.json" not in tracked.stdout
    text = SUMMARY.read_text().lower()
    forbidden = ['"prompt"', '"response"', '"generated"', '"ideal"', '"token"', "hf_"]
    for needle in forbidden:
        assert needle not in text


def test_no_public_benchmark_claim_or_public_artifacts():
    combined = (SUMMARY.read_text() + "\n" + DOC.read_text()).lower()
    for forbidden in ["outperforms", "sota", "public weights available", "gguf released"]:
        assert forbidden not in combined

    artifacts = []
    for pattern in ("*.safetensors", "*.gguf", "adapter_model.bin"):
        for path in PROJECT_ROOT.rglob(pattern):
            if ".venv" not in path.parts and "deps" not in path.parts:
                artifacts.append(str(path.relative_to(PROJECT_ROOT)))
    assert not artifacts, f"Found public artifacts: {artifacts}"


def test_gate_blocked_in_doc():
    text = DOC.read_text().lower()
    assert "gate: **blocked**" in text
    assert "blocked_missing_raw_outputs" in text or "ready_for_private_manual_review" in text
    assert "not allowed" in text


def test_release_check_passes():
    result = subprocess.run(
        [sys.executable, "scripts/release/check-release.py"],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        timeout=120,
        check=False,
    )
    assert result.returncode == 0, (result.stdout + result.stderr)[-3000:]
