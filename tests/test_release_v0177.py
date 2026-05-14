"""Release tests for v0.1.77-alpha.

Focus: completed private subset30 manual review with gate still blocked.
"""

import json
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SUMMARY = PROJECT_ROOT / "reports" / "evals" / "kimari_runtime_15b_500step_subset30" / "manual_review_summary.json"
ARTIFACT_SUMMARY = (
    PROJECT_ROOT / "reports" / "evals" / "kimari_runtime_15b_500step_subset30" / "artifact_persistence_summary.json"
)
VALIDATOR = PROJECT_ROOT / "eval" / "scripts" / "validate_manual_review_summary.py"


def test_version_bumped_to_v0177():
    assert 'version = "0.1.77-alpha"' in (PROJECT_ROOT / "pyproject.toml").read_text()
    assert '__version__ = "0.1.77-alpha"' in (PROJECT_ROOT / "kimari" / "__init__.py").read_text()


def test_manual_review_completed_but_gate_blocked():
    data = json.loads(SUMMARY.read_text())
    assert data["manual_review_status"] == "completed"
    assert data["review_status"] == "completed"
    assert data["reviewed_items"] == data["subset_size"] == 30
    assert data["decision"] == "safety_fix_required"
    assert data["gate_state"] == "BLOCKED"
    assert data["public_benchmark_allowed"] is False
    assert data["raw_outputs_committed"] is False


def test_manual_review_counts_are_recorded():
    data = json.loads(SUMMARY.read_text())
    assert data["accepted_adapter_wins"] == 14
    assert data["rejected_adapter_wins"] == 6
    assert data["accepted_base_wins"] == 9
    assert data["safety_regressions"] == 1
    assert data["factual_regressions"] == 2
    assert data["spanish_quality_regressions"] == 1


def test_manual_review_summary_is_sanitized():
    text = SUMMARY.read_text().lower()
    assert "raw_outputs_private.json" in text
    for forbidden in ['"prompt"', '"response"', '"generated"', '"ideal"', "api_key", "hf_token"]:
        assert forbidden not in text


def test_private_artifact_status_preserved():
    data = json.loads(ARTIFACT_SUMMARY.read_text())
    assert data["raw_outputs_private_uploaded"] is True
    assert data["manual_review_available"] is True
    assert data["manual_review_completed"] is True
    assert data["manual_review_decision"] == "safety_fix_required"
    assert data["raw_outputs_committed"] is False
    assert data["gate_state"] == "BLOCKED"


def test_no_raw_outputs_private_tracked():
    tracked = subprocess.run(["git", "ls-files"], cwd=PROJECT_ROOT, capture_output=True, text=True, timeout=30)
    assert "raw_outputs_private.json" not in tracked.stdout


def test_manual_review_validator_passes():
    result = subprocess.run(
        [sys.executable, str(VALIDATOR), "--summary", str(SUMMARY), "--json"],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        timeout=60,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    payload = json.loads(result.stdout)
    assert payload["valid"] is True


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
