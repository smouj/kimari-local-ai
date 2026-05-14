"""Release tests for v0.1.78-alpha.

Focus: benchmark-honesty eval hardening after refuse-010 safety regression.
"""

import json
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
REFUSAL_JSONL = PROJECT_ROOT / "eval" / "kimari_private_v1" / "refusal_safety.jsonl"


def _load_refusal_items():
    items = []
    for line in REFUSAL_JSONL.read_text().strip().split("\n"):
        line = line.strip()
        if line:
            items.append(json.loads(line))
    return items


def test_version_bumped_to_v0178():
    assert 'version = "0.1.78-alpha"' in (PROJECT_ROOT / "pyproject.toml").read_text()
    assert '__version__ = "0.1.78-alpha"' in (PROJECT_ROOT / "kimari" / "__init__.py").read_text()


def test_refusal_jsonl_is_valid():
    items = _load_refusal_items()
    assert len(items) >= 21
    ids = [item["id"] for item in items]
    assert len(set(ids)) == len(ids), f"duplicate ids: {[x for x in ids if ids.count(x) > 1]}"


def test_new_benchmark_honesty_cases_exist():
    items = _load_refusal_items()
    by_id = {item["id"]: item for item in items}
    for expected_id in ["refuse-016", "refuse-017", "refuse-018", "refuse-019", "refuse-020", "refuse-021"]:
        assert expected_id in by_id, f"missing {expected_id}"
        item = by_id[expected_id]
        assert "safety" in item["tags"]
        assert "benchmarks" in item["tags"] or "honesty" in item["tags"]


def test_refuse_010_failure_pattern_covered():
    items = _load_refusal_items()
    by_id = {item["id"]: item for item in items}
    # refuse-010 was about affirming unverified benchmark numbers
    # refuse-016 covers fabricated claims, refuse-019 covers Spanish-specific fabricated claims
    for covering_id in ["refuse-016", "refuse-019"]:
        assert covering_id in by_id
        item = by_id[covering_id]
        assert "kimari" in item["tags"]
        assert "honesty" in item["tags"]


def test_dataset_expanded():
    total = 0
    dataset_dir = PROJECT_ROOT / "eval" / "kimari_private_v1"
    for jsonl_file in sorted(dataset_dir.glob("*.jsonl")):
        for line in jsonl_file.read_text().strip().split("\n"):
            if line.strip():
                total += 1
    assert total >= 110


def test_no_raw_outputs_tracked():
    tracked = subprocess.run(["git", "ls-files"], cwd=PROJECT_ROOT, capture_output=True, text=True, timeout=30)
    assert "raw_outputs_private.json" not in tracked.stdout


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
