"""Tests for v0.1.48-alpha release criteria.

Validates:
- HF Jobs smoke result doc exists
- Smoke summary sanitized
- training_performed=false
- adapter_generated=false
- hf_upload_performed=false
- No raw logs
- Version bump
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def test_smoke_result_doc_exists():
    """docs/HF_JOBS_SMOKE_REAL_RESULT.md must exist."""
    assert (PROJECT_ROOT / "docs" / "HF_JOBS_SMOKE_REAL_RESULT.md").exists()


def test_smoke_summary_exists():
    """training/results/hf_jobs_smoke_summary.json must exist."""
    assert (PROJECT_ROOT / "training" / "results" / "hf_jobs_smoke_summary.json").exists()


def test_smoke_summary_training_performed_false():
    """Smoke summary must have training_performed=false."""
    summary_path = PROJECT_ROOT / "training" / "results" / "hf_jobs_smoke_summary.json"
    if not summary_path.exists():
        return
    data = json.loads(summary_path.read_text())
    assert data.get("training_performed") is False, f"training_performed={data.get('training_performed')}"


def test_smoke_summary_adapter_generated_false():
    """Smoke summary must have adapter_generated=false."""
    summary_path = PROJECT_ROOT / "training" / "results" / "hf_jobs_smoke_summary.json"
    if not summary_path.exists():
        return
    data = json.loads(summary_path.read_text())
    assert data.get("adapter_generated") is False, f"adapter_generated={data.get('adapter_generated')}"


def test_smoke_summary_hf_upload_performed_false():
    """Smoke summary must have hf_upload_performed=false."""
    summary_path = PROJECT_ROOT / "training" / "results" / "hf_jobs_smoke_summary.json"
    if not summary_path.exists():
        return
    data = json.loads(summary_path.read_text())
    assert data.get("hf_upload_performed") is False, f"hf_upload_performed={data.get('hf_upload_performed')}"


def test_smoke_summary_gate_blocked():
    """Smoke summary must have gate_state=BLOCKED."""
    summary_path = PROJECT_ROOT / "training" / "results" / "hf_jobs_smoke_summary.json"
    if not summary_path.exists():
        return
    data = json.loads(summary_path.read_text())
    assert data.get("gate_state") == "BLOCKED", f"gate_state={data.get('gate_state')}"


def test_no_raw_logs():
    """No raw log files in training/results/."""
    import glob

    log_files = glob.glob(str(PROJECT_ROOT / "training" / "results" / "*.log"))
    assert len(log_files) == 0, f"Found {len(log_files)} raw log files"


def test_no_tokens_in_summary():
    """No tokens or private data in smoke summary."""
    summary_path = PROJECT_ROOT / "training" / "results" / "hf_jobs_smoke_summary.json"
    if not summary_path.exists():
        return
    content = summary_path.read_text().lower()
    assert "sk-" not in content, "Summary contains API key pattern"
    assert "/home/" not in content, "Summary contains private path"


def test_smoke_result_doc_no_training_claim():
    """Smoke result doc must not claim training was performed."""
    doc = (PROJECT_ROOT / "docs" / "HF_JOBS_SMOKE_REAL_RESULT.md").read_text().lower()
    assert "training_performed" in doc, "Doc should mention training_performed status"
    assert "no training" in doc or "training_performed: false" in doc, "Doc should state no training was performed"


def test_version_bump():
    """pyproject.toml and __init__.py must be >= 0.1.48-alpha."""
    import re

    pyproject = (PROJECT_ROOT / "pyproject.toml").read_text()
    init = (PROJECT_ROOT / "kimari" / "__init__.py").read_text()
    match_p = re.search(r'version\s*=\s*["\']([^"\']+)["\']', pyproject)
    match_i = re.search(r'__version__\s*=\s*["\']([^"\']+)["\']', init)
    assert match_p and match_p.group(1) >= "0.1.48-alpha"
    assert match_i and match_i.group(1) >= "0.1.48-alpha"


def test_changelog_has_v0148():
    """CHANGELOG.md must have [0.1.48-alpha] entry."""
    changelog = (PROJECT_ROOT / "CHANGELOG.md").read_text()
    assert "[0.1.48-alpha]" in changelog


def test_roadmap_has_v0148():
    """ROADMAP.md must mention v0.1.48-alpha."""
    roadmap = (PROJECT_ROOT / "ROADMAP.md").read_text()
    assert "v0.1.48-alpha" in roadmap


if __name__ == "__main__":
    import pytest

    sys.exit(pytest.main([__file__, "-v"]))
