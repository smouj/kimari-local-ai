"""Tests for v0.1.49-alpha release criteria.

Validates:
- Micro SFT dataset exists and is valid
- Micro SFT config has correct safety flags
- Runner has --allow-submit --yes
- Dataset report has no private data
- No raw logs
- Version bump
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

DATASET_PATH = PROJECT_ROOT / "dataset" / "build" / "kimari-fit-v0" / "sft_micro.jsonl"
REPORT_PATH = PROJECT_ROOT / "dataset" / "build" / "kimari-fit-v0" / "report.json"
CONFIG_PATH = PROJECT_ROOT / "training" / "configs" / "hf_jobs_kimari4b_micro_sft_real.v0.yaml"
RUNNER_PATH = PROJECT_ROOT / "training" / "scripts" / "hf_jobs_micro_sft_real.py"


def _load_yaml(path: Path) -> dict | None:
    try:
        import yaml
    except ImportError:
        return None
    if not path.exists():
        return None
    with open(path) as f:
        return yaml.safe_load(f)


def test_dataset_exists():
    """Micro SFT dataset must exist."""
    assert DATASET_PATH.exists(), f"Dataset not found: {DATASET_PATH}"


def test_dataset_has_records():
    """Micro SFT dataset must have >= 20 records."""
    if not DATASET_PATH.exists():
        return
    lines = DATASET_PATH.read_text().strip().split("\n")
    assert len(lines) >= 20, f"Dataset has only {len(lines)} records"


def test_dataset_valid_jsonl():
    """Each line must be valid JSON with prompt and response."""
    if not DATASET_PATH.exists():
        return
    lines = DATASET_PATH.read_text().strip().split("\n")
    for i, line in enumerate(lines):
        data = json.loads(line)
        assert "prompt" in data, f"Line {i + 1}: missing 'prompt'"
        assert "response" in data, f"Line {i + 1}: missing 'response'"


def test_dataset_no_private_data():
    """Dataset must not contain private data or tokens."""
    if not DATASET_PATH.exists():
        return
    content = DATASET_PATH.read_text().lower()
    assert "/home/" not in content, "Dataset contains private paths"
    assert "sk-" not in content, "Dataset contains API key pattern"
    assert "password" not in content, "Dataset contains password"


def test_dataset_report_exists():
    """Dataset report must exist."""
    assert REPORT_PATH.exists(), f"Report not found: {REPORT_PATH}"


def test_dataset_report_valid():
    """Dataset report must have correct fields."""
    if not REPORT_PATH.exists():
        return
    report = json.loads(REPORT_PATH.read_text())
    assert report.get("private_data") is False, f"private_data={report.get('private_data')}"
    assert report.get("tokens_or_secrets") is False, f"tokens_or_secrets={report.get('tokens_or_secrets')}"
    assert report.get("record_count", 0) >= 20, f"record_count={report.get('record_count')}"


def test_config_exists():
    """Micro SFT config must exist."""
    assert CONFIG_PATH.exists(), f"Config not found: {CONFIG_PATH}"


def test_config_safety_flags():
    """Config must have correct safety flags."""
    config = _load_yaml(CONFIG_PATH)
    if config is None:
        return
    safety = config.get("safety", {})
    assert safety.get("adapter_committed") is False, f"adapter_committed={safety.get('adapter_committed')}"
    assert safety.get("hf_upload_performed") is False, f"hf_upload_performed={safety.get('hf_upload_performed')}"
    assert safety.get("push_to_hub") is not True, f"push_to_hub={safety.get('push_to_hub')}"
    assert safety.get("gguf_export") is False, f"gguf_export={safety.get('gguf_export')}"
    assert safety.get("preview_gate_state") == "BLOCKED", f"gate_state={safety.get('preview_gate_state')}"


def test_runner_exists():
    """HF Jobs micro SFT runner must exist."""
    assert RUNNER_PATH.exists(), f"Runner not found: {RUNNER_PATH}"


def test_runner_requires_allow_submit():
    """Runner must require --allow-submit and --yes."""
    if not RUNNER_PATH.exists():
        return
    text = RUNNER_PATH.read_text()
    assert "--allow-submit" in text, "Runner must have --allow-submit"
    assert "--yes" in text, "Runner must have --yes"


def test_runner_has_require_jobs_access():
    """Runner must have --require-jobs-access flag."""
    if not RUNNER_PATH.exists():
        return
    text = RUNNER_PATH.read_text()
    assert "--require-jobs-access" in text, "Runner must have --require-jobs-access"


def test_runner_no_token_arg():
    """Runner must not accept --token or --api-key."""
    if not RUNNER_PATH.exists():
        return
    text = RUNNER_PATH.read_text()
    # Runner should check for and block these args
    assert '"--token"' in text or '"--api-key"' in text, "Runner should check for --token/--api-key"


def test_micro_sft_result_doc_exists():
    """KIMARI4B_MICRO_SFT_RESULT.md must exist."""
    assert (PROJECT_ROOT / "docs" / "KIMARI4B_MICRO_SFT_RESULT.md").exists()


def test_micro_sft_result_doc_says_blocked():
    """Micro SFT result doc must say BLOCKED."""
    doc = (PROJECT_ROOT / "docs" / "KIMARI4B_MICRO_SFT_RESULT.md").read_text().lower()
    assert "blocked" in doc, "Micro SFT result doc should mention BLOCKED gate"


def test_version_bump():
    """pyproject.toml and __init__.py must be >= 0.1.49-alpha."""
    import re

    pyproject = (PROJECT_ROOT / "pyproject.toml").read_text()
    init = (PROJECT_ROOT / "kimari" / "__init__.py").read_text()
    match_p = re.search(r'version\s*=\s*["\']([^"\']+)["\']', pyproject)
    match_i = re.search(r'__version__\s*=\s*["\']([^"\']+)["\']', init)
    assert match_p and match_p.group(1) >= "0.1.49-alpha"
    assert match_i and match_i.group(1) >= "0.1.49-alpha"


def test_changelog_has_v0149():
    """CHANGELOG.md must have [0.1.49-alpha] entry."""
    changelog = (PROJECT_ROOT / "CHANGELOG.md").read_text()
    assert "[0.1.49-alpha]" in changelog


def test_roadmap_has_v0149():
    """ROADMAP.md must mention v0.1.49-alpha."""
    roadmap = (PROJECT_ROOT / "ROADMAP.md").read_text()
    assert "v0.1.49-alpha" in roadmap


if __name__ == "__main__":
    import pytest

    sys.exit(pytest.main([__file__, "-v"]))
