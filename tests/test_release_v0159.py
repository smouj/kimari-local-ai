"""Release validation tests for v0.1.59-alpha — Kimari SFT v1 Dataset."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

VERSION = "0.1.59-alpha"
VERSION_V = f"v{VERSION}"

DATASET_DIR = ROOT / "dataset" / "kimari_sft_v1"
SOURCES_DIR = DATASET_DIR / "sources"
BUILD_DIR = ROOT / "dataset" / "build" / "kimari_sft_v1"
SCHEMA_PATH = ROOT / "dataset" / "schema" / "kimari_sft_item.schema.json"
VALIDATOR_PATH = ROOT / "dataset" / "scripts" / "validate_kimari_sft_v1.py"
BUILDER_PATH = ROOT / "dataset" / "scripts" / "build_kimari_sft_v1.py"

VALID_CATEGORIES = {
    "spanish_technical",
    "coding_debug",
    "server_ops",
    "local_llm_cuda_gguf",
    "openclaw_agents",
    "safety_refusal",
    "json_tooling",
    "style_consistency",
}

ALLOWED_LICENSES = {
    "project-owned",
    "MIT",
    "Apache-2.0",
    "BSD-3-Clause",
    "CC-BY-4.0",
    "CC-BY-SA-4.0",
}

SOURCE_FILES = {
    "spanish_technical": "spanish_technical.jsonl",
    "coding_debug": "coding_debug.jsonl",
    "server_ops": "server_ops.jsonl",
    "local_llm_cuda_gguf": "local_llm_cuda_gguf.jsonl",
    "openclaw_agents": "openclaw_agents.jsonl",
    "safety_refusal": "safety_refusal.jsonl",
    "json_tooling": "json_tooling.jsonl",
    "style_consistency": "style_consistency.jsonl",
}


def test_pyproject_version():
    content = (ROOT / "pyproject.toml").read_text()
    assert f'version = "{VERSION}"' in content, "pyproject.toml version mismatch"


def test_init_version():
    content = (ROOT / "kimari" / "__init__.py").read_text()
    assert f'__version__ = "{VERSION}"' in content, "__init__.py version mismatch"


def test_readme_version():
    content = (ROOT / "README.md").read_text()
    assert VERSION_V in content or VERSION in content, "README missing version"


def test_index_html_version():
    content = (ROOT / "docs" / "index.html").read_text()
    assert VERSION_V in content, "index.html missing version"


def test_changelog_has_v0159():
    content = (ROOT / "CHANGELOG.md").read_text()
    assert "0.1.59-alpha" in content, "CHANGELOG missing v0.1.59-alpha entry"


def test_dataset_dir_exists():
    assert DATASET_DIR.exists(), "Dataset directory missing"
    assert SOURCES_DIR.exists(), "Sources directory missing"


def test_schema_exists():
    assert SCHEMA_PATH.exists(), "Schema file missing"


def test_schema_is_valid_json():
    data = json.loads(SCHEMA_PATH.read_text())
    assert data.get("title") == "KimariSFTItem", "Schema title mismatch"
    assert "properties" in data, "Schema missing properties"


def test_validator_exists():
    assert VALIDATOR_PATH.exists(), "Validator script missing"


def test_builder_exists():
    assert BUILDER_PATH.exists(), "Builder script missing"


def test_all_source_files_exist():
    for _category, filename in SOURCE_FILES.items():
        filepath = SOURCES_DIR / filename
        assert filepath.exists(), f"Source file missing: {filename}"


def test_source_files_are_valid_jsonl():
    for _category, filename in SOURCE_FILES.items():
        filepath = SOURCES_DIR / filename
        with open(filepath) as f:
            lines = [line.strip() for line in f if line.strip()]
        assert len(lines) >= 30, f"{filename}: expected >= 30 items, got {len(lines)}"
        for i, line in enumerate(lines):
            try:
                json.loads(line)
            except json.JSONDecodeError as e:
                raise AssertionError(f"{filename}:{i + 1}: invalid JSON: {e}") from None


def test_source_items_have_required_fields():
    required_fields = {"id", "category", "language", "source", "license", "quality_score", "tags", "messages"}
    for _category, filename in SOURCE_FILES.items():
        filepath = SOURCES_DIR / filename
        with open(filepath) as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue
                item = json.loads(line)
                missing = required_fields - set(item.keys())
                assert not missing, f"{filename}:{line_num}: missing fields: {missing}"


def test_source_items_have_valid_categories():
    for _category, filename in SOURCE_FILES.items():
        filepath = SOURCES_DIR / filename
        with open(filepath) as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                item = json.loads(line)
                assert item["category"] in VALID_CATEGORIES, f"{filename}: invalid category '{item['category']}'"


def test_source_items_have_allowed_licenses():
    for _category, filename in SOURCE_FILES.items():
        filepath = SOURCES_DIR / filename
        with open(filepath) as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                item = json.loads(line)
                assert item["license"] in ALLOWED_LICENSES, f"{filename}: invalid license '{item['license']}'"


def test_source_items_have_valid_messages():
    for _category, filename in SOURCE_FILES.items():
        filepath = SOURCES_DIR / filename
        with open(filepath) as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                item = json.loads(line)
                messages = item.get("messages", [])
                assert len(messages) >= 2, f"{filename}: messages too short"
                roles = {m.get("role") for m in messages}
                assert "user" in roles, f"{filename}: missing user role"
                assert "assistant" in roles, f"{filename}: missing assistant role"


def test_source_items_have_quality_scores():
    for _category, filename in SOURCE_FILES.items():
        filepath = SOURCES_DIR / filename
        with open(filepath) as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                item = json.loads(line)
                qs = item.get("quality_score", 0)
                assert isinstance(qs, int) and 1 <= qs <= 5, f"{filename}: quality_score must be 1-5, got {qs}"


def test_no_kimari4b_released_claims():
    for _category, filename in SOURCE_FILES.items():
        filepath = SOURCES_DIR / filename
        content = filepath.read_text().lower()
        assert "kimari-4b released" not in content, f"{filename}: Kimari-4B released claim"
        assert "kimari-4b is released" not in content, f"{filename}: Kimari-4B is released claim"
        assert "kimari-4b is available" not in content, f"{filename}: Kimari-4B available claim"
        assert "public weights available" not in content, f"{filename}: public weights claim"


def test_manifest_exists():
    assert (DATASET_DIR / "manifest.yaml").exists(), "Manifest missing"
    assert (DATASET_DIR / "license_manifest.yaml").exists(), "License manifest missing"
    assert (DATASET_DIR / "LICENSE_NOTES.md").exists(), "LICENSE_NOTES.md missing"


def test_readme_exists():
    assert (DATASET_DIR / "README.md").exists(), "Dataset README missing"


def test_docs_exist():
    assert (ROOT / "docs" / "KIMARI_SFT_V1_DATASET.md").exists(), "Dataset doc missing"
    assert (ROOT / "docs" / "KIMARI_SFT_V1_QUALITY_GUIDE.md").exists(), "Quality guide missing"


def test_validator_runs():
    result = subprocess.run(
        [sys.executable, str(VALIDATOR_PATH), "--dataset-dir", str(DATASET_DIR), "--json"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
        timeout=60,
    )
    assert result.returncode == 0, f"Validator failed: {result.stdout}\n{result.stderr}"


def test_builder_runs():
    result = subprocess.run(
        [
            sys.executable,
            str(BUILDER_PATH),
            "--dataset-dir",
            str(DATASET_DIR),
            "--output-dir",
            str(BUILD_DIR),
            "--train-ratio",
            "0.9",
            "--seed",
            "42",
            "--json",
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
        timeout=60,
    )
    assert result.returncode == 0, f"Builder failed: {result.stdout}\n{result.stderr}"


def test_build_output_exists():
    # Builder must have been run first (test_builder_runs)
    assert (BUILD_DIR / "train.jsonl").exists(), "train.jsonl missing"
    assert (BUILD_DIR / "validation.jsonl").exists(), "validation.jsonl missing"
    assert (BUILD_DIR / "dataset_summary.json").exists(), "dataset_summary.json missing"
    assert (BUILD_DIR / "license_manifest.json").exists(), "license_manifest.json missing"
    assert (BUILD_DIR / "quality_report.json").exists(), "quality_report.json missing"


def test_build_output_has_items():
    train_path = BUILD_DIR / "train.jsonl"
    val_path = BUILD_DIR / "validation.jsonl"

    train_count = sum(1 for line in train_path.read_text().strip().split("\n") if line.strip())
    val_count = sum(1 for line in val_path.read_text().strip().split("\n") if line.strip())

    assert train_count >= 250, f"Train set too small: {train_count}"
    assert val_count >= 20, f"Validation set too small: {val_count}"


def test_build_summary_valid():
    summary_path = BUILD_DIR / "dataset_summary.json"
    data = json.loads(summary_path.read_text())
    assert data.get("dataset") == "kimari_sft_v1", "Summary dataset name mismatch"
    assert data.get("total_items", 0) >= 300, f"Total items too low: {data.get('total_items')}"
    assert data.get("safety", {}).get("gate") == "BLOCKED", "Gate must be BLOCKED"
    assert data.get("safety", {}).get("no_training") is True, "no_training must be True"


def test_license_manifest_valid():
    manifest_path = BUILD_DIR / "license_manifest.json"
    data = json.loads(manifest_path.read_text())
    assert data.get("all_permissive") is True, "Not all licenses are permissive"
    assert data.get("blocked_found") is False, "Blocked licenses found"


def test_no_training_artifacts():
    """No training config or run artifacts should exist."""
    runs_dir = ROOT / "training" / "runs"
    if runs_dir.exists():
        # .gitkeep is fine, actual training outputs are not
        real_files = [f for f in runs_dir.iterdir() if f.name != ".gitkeep"]
        assert len(real_files) == 0, f"Training runs directory has unexpected files: {real_files}"


def test_kimari4b_not_released():
    readme = (ROOT / "README.md").read_text()
    assert "not released" in readme.lower(), "README missing 'not released'"


if __name__ == "__main__":
    sys.exit(subprocess.run([sys.executable, "-m", "pytest", __file__, "-v"], check=False).returncode)
