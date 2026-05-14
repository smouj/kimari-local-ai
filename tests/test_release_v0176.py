"""Release tests for v0.1.76-alpha.

Focus: private eval artifact persistence hardening for subset30 scoring.
"""

import json
import subprocess
import sys
from pathlib import Path

import yaml

PROJECT_ROOT = Path(__file__).resolve().parent.parent
CONFIG = PROJECT_ROOT / "eval" / "configs" / "kimari_runtime_15b_sft_v1_eval_subset30.yaml"
UPLOAD = PROJECT_ROOT / "eval" / "scripts" / "upload_private_eval_artifacts.py"
VALIDATE = PROJECT_ROOT / "eval" / "scripts" / "validate_private_eval_artifacts.py"
SUMMARY = (
    PROJECT_ROOT / "reports" / "evals" / "kimari_runtime_15b_500step_subset30" / "artifact_persistence_summary.json"
)


def test_version_bumped_to_v0176():
    assert 'version = "0.1.76-alpha"' in (PROJECT_ROOT / "pyproject.toml").read_text()
    assert '__version__ = "0.1.76-alpha"' in (PROJECT_ROOT / "kimari" / "__init__.py").read_text()


def test_private_artifact_tools_exist():
    assert UPLOAD.exists()
    assert VALIDATE.exists()


def test_subset30_config_requires_private_raw_outputs():
    assert CONFIG.exists()
    data = yaml.safe_load(CONFIG.read_text())
    assert data["subset_size"] == 30
    assert data["raw_outputs_private_required"] is True
    assert data["raw_outputs_commit_allowed"] is False
    assert data["public_benchmark_allowed"] is False
    assert data["manual_review_required"] is True
    assert data["gate_state"] == "BLOCKED"


def test_artifact_persistence_summary_is_sanitized():
    assert SUMMARY.exists()
    data = json.loads(SUMMARY.read_text())
    assert "raw_outputs_private_uploaded" in data
    assert "manual_review_available" in data
    assert data["raw_outputs_committed"] is False
    assert data["public_benchmark_allowed"] is False
    assert data["gate_state"] == "BLOCKED"
    text = SUMMARY.read_text().lower()
    for forbidden in ['"prompt"', '"response"', '"generated"', '"ideal"', "hf_"]:
        assert forbidden not in text


def test_no_raw_outputs_private_tracked():
    tracked = subprocess.run(["git", "ls-files"], cwd=PROJECT_ROOT, capture_output=True, text=True, timeout=30)
    assert "raw_outputs_private.json" not in tracked.stdout


def test_runner_dry_run_passes():
    result = subprocess.run(
        [sys.executable, "eval/scripts/run_sft_v1_eval.py", "--config", str(CONFIG), "--dry-run", "--json"],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        timeout=60,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    payload = json.loads(result.stdout)
    assert payload["status"] == "dry_run"
    assert "hf_jobs_run_kimari_scoring_eval.py" in payload["command"]


def test_private_artifact_validator_help():
    result = subprocess.run([sys.executable, str(VALIDATE), "--help"], cwd=PROJECT_ROOT, capture_output=True, text=True)
    assert result.returncode == 0
    assert "--expected-sha256" in result.stdout


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
