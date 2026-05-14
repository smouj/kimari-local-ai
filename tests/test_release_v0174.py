"""Release tests for v0.1.74-alpha.

Focus: private manual review gate for 500-step subset30 scoring.
"""

import json
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SUMMARY = PROJECT_ROOT / "reports" / "evals" / "kimari_runtime_15b_500step_subset30" / "manual_review_summary.json"
TEMPLATE = (
    PROJECT_ROOT / "reports" / "evals" / "kimari_runtime_15b_500step_subset30" / "manual_review_summary.template.json"
)
DOC = PROJECT_ROOT / "docs" / "KIMARI_RUNTIME_15B_500STEP_MANUAL_REVIEW.md"
VALIDATOR = PROJECT_ROOT / "eval" / "scripts" / "validate_manual_review_summary.py"


def test_version_at_least_v0174():
    pyproject = (PROJECT_ROOT / "pyproject.toml").read_text()
    init = (PROJECT_ROOT / "kimari" / "__init__.py").read_text()
    assert 'version = "0.1.7' in pyproject
    assert '__version__ = "0.1.7' in init


def test_manual_review_artifacts_exist():
    assert SUMMARY.exists()
    assert TEMPLATE.exists()
    assert DOC.exists()
    assert VALIDATOR.exists()


def test_manual_review_summary_is_sanitized_and_blocked():
    data = json.loads(SUMMARY.read_text())
    assert data["scoring_job_id"] == "6a052f5ce48bea4538b9c37d"
    assert data["training_job_id"] == "6a052ce6e48bea4538b9c365"
    assert data["subset_size"] == 30
    assert data["adapter_500_wins"] == 17
    assert data["base_wins"] == 12
    assert data["ties"] == 1
    assert data["reviewed_items"] <= data["subset_size"]
    assert data["raw_outputs_committed"] is False
    assert data["public_benchmark_allowed"] is False
    assert data["gate_state"] == "BLOCKED"
    assert data["decision"] in {"inconclusive", "blocked_missing_raw_outputs"}


def test_manual_review_validator_passes():
    result = subprocess.run(
        [sys.executable, str(VALIDATOR), "--summary", str(SUMMARY), "--json"],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    payload = json.loads(result.stdout)
    assert payload["valid"] is True


def test_no_raw_outputs_or_benchmark_claims_in_manual_review_summary():
    text = SUMMARY.read_text().lower()
    forbidden = [
        '"prompt"',
        '"response"',
        '"raw_outputs"',
        '"generated_text"',
        '"completion"',
        "outperforms",
        "sota",
        "public weights available",
    ]
    for needle in forbidden:
        assert needle not in text


def test_no_public_weights_or_gguf():
    dangerous = []
    for pattern in ("*.safetensors", "*.gguf", "adapter_model.bin"):
        for path in PROJECT_ROOT.rglob(pattern):
            if ".venv" not in path.parts and "deps" not in path.parts:
                dangerous.append(str(path.relative_to(PROJECT_ROOT)))
    assert not dangerous, f"Found public artifacts: {dangerous}"


def test_gate_blocked_in_manual_review_doc():
    text = DOC.read_text().lower()
    assert "gate: **blocked**" in text
    assert "public benchmark" in text
    assert "not allowed" in text
    assert "no gguf" in text


def test_release_check_passes():
    result = subprocess.run(
        [sys.executable, "scripts/release/check-release.py"],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        timeout=120,
        check=False,
    )
    assert result.returncode == 0, (result.stdout + result.stderr)[-2000:]
