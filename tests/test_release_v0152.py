"""Tests for v0.1.52-alpha release criteria.

Validates:
- Eval dataset exists with 100+ cases
- Eval validator and harness exist
- Baseline plan exists
- No benchmark claims
- Version bump
- Gate BLOCKED
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent / "kimari-local-ai"


def test_eval_dataset_exists():
    assert (PROJECT_ROOT / "eval" / "kimari_private_v1").exists()


def test_eval_dataset_has_100_plus_cases():
    total = 0
    for jsonl_file in (PROJECT_ROOT / "eval" / "kimari_private_v1").glob("*.jsonl"):
        total += len(jsonl_file.read_text().strip().split("\n"))
    assert total >= 100, f"Only {total} eval cases (minimum: 100)"


def test_eval_dataset_has_7_categories():
    jsonl_files = list((PROJECT_ROOT / "eval" / "kimari_private_v1").glob("*.jsonl"))
    assert len(jsonl_files) >= 7, f"Only {len(jsonl_files)} categories (minimum: 7)"


def test_eval_schema_exists():
    assert (PROJECT_ROOT / "eval" / "schema" / "kimari_eval_item.schema.json").exists()


def test_eval_validator_exists():
    assert (PROJECT_ROOT / "eval" / "scripts" / "validate_kimari_eval.py").exists()


def test_eval_harness_exists():
    assert (PROJECT_ROOT / "eval" / "scripts" / "run_kimari_eval.py").exists()


def test_eval_harness_dry_run():
    harness = PROJECT_ROOT / "eval" / "scripts" / "run_kimari_eval.py"
    text = harness.read_text()
    assert "--dry-run" in text
    assert "manual_review_required" in text
    assert "no_benchmark_claim" in text
    assert "not_scored" in text


def test_eval_docs_exist():
    assert (PROJECT_ROOT / "docs" / "KIMARI_EVAL_PRIVATE_V1.md").exists()
    assert (PROJECT_ROOT / "docs" / "KIMARIFIT_SCORE_PLAN.md").exists()
    assert (PROJECT_ROOT / "docs" / "BASELINE_VS_ADAPTER_EVAL_PLAN.md").exists()


def test_baseline_plan_exists():
    assert (PROJECT_ROOT / "reports" / "evals" / "baseline_qwen25_15b" / "baseline_plan.json").exists()
    data = json.loads((PROJECT_ROOT / "reports" / "evals" / "baseline_qwen25_15b" / "baseline_plan.json").read_text())
    assert data.get("status") == "pending"
    assert data.get("manual_review_required") is True
    assert data.get("no_benchmark_claim") is True


def test_no_safetensors_in_public_repo():
    safetensors = list(PROJECT_ROOT.rglob("*.safetensors"))
    assert len(safetensors) == 0, f"Found {len(safetensors)} .safetensors files"


def test_no_gguf_in_public_repo():
    gguf = [f for f in PROJECT_ROOT.rglob("*.gguf") if "deps" not in str(f) and "node_modules" not in str(f)]
    assert len(gguf) == 0, f"Found {len(gguf)} .gguf files"


def test_version_bump():
    import re

    pyproject = (PROJECT_ROOT / "pyproject.toml").read_text()
    init = (PROJECT_ROOT / "kimari" / "__init__.py").read_text()
    match_p = re.search(r'version\s*=\s*["\']([^"\']+)["\']', pyproject)
    match_i = re.search(r'__version__\s*=\s*["\']([^"\']+)["\']', init)
    assert match_p and match_p.group(1) >= "0.1.52-alpha"
    assert match_i and match_i.group(1) >= "0.1.52-alpha"


def test_changelog_has_v0152():
    changelog = (PROJECT_ROOT / "CHANGELOG.md").read_text()
    assert "[0.1.52-alpha]" in changelog


def test_roadmap_has_v0152():
    roadmap = (PROJECT_ROOT / "ROADMAP.md").read_text()
    assert "v0.1.52-alpha" in roadmap


if __name__ == "__main__":
    import pytest

    sys.exit(pytest.main([__file__, "-v"]))
