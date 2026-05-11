"""Release validation tests for Kimari Local AI v0.1.23-alpha.

Tests cover:
- Base candidates YAML and selection script
- SFT and preference seed datasets
- Dataset building and preparation
- KimariFit dry-run evaluation harness
- Training and GGUF export dry-runs
- Model decision record (ADR-001)
- First training run guide
- KimariFit rubric
- No GGUF tracked, no false claims
- Version consistency
- Release check passes
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def _run_script(*args: str, timeout: int = 30) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, *args],
        capture_output=True,
        text=True,
        timeout=timeout,
        cwd=str(PROJECT_ROOT),
    )


# ─── Base Candidates ────────────────────────────────────────────────────


class TestBaseCandidates:
    def test_base_candidates_yaml_exists(self):
        assert (PROJECT_ROOT / "training" / "configs" / "base_candidates.yaml").exists()

    def test_base_candidates_yaml_parseable(self):
        content = (PROJECT_ROOT / "training" / "configs" / "base_candidates.yaml").read_text()
        assert "candidates:" in content
        assert "smollm3-3b" in content

    def test_select_base_model_script_exists(self):
        assert (PROJECT_ROOT / "training" / "scripts" / "select_base_model.py").exists()

    def test_select_base_model_json_output(self):
        result = _run_script(
            str(PROJECT_ROOT / "training" / "scripts" / "select_base_model.py"),
            "--json",
        )
        assert result.returncode == 0, f"select_base_model.py --json failed:\n{result.stdout}\n{result.stderr}"
        data = json.loads(result.stdout)
        assert "ranking" in data
        assert len(data["ranking"]) >= 1


# ─── SFT Seed Dataset ──────────────────────────────────────────────────


class TestSFTSeed:
    def test_sft_seed_jsonl_exists(self):
        assert (PROJECT_ROOT / "dataset" / "samples" / "sft_seed.jsonl").exists()

    def test_sft_seed_validates(self):
        path = PROJECT_ROOT / "dataset" / "samples" / "sft_seed.jsonl"
        lines = path.read_text().strip().splitlines()
        records = []
        for line in lines:
            record = json.loads(line)
            assert "messages" in record, "missing 'messages' field"
            assert "source" in record, "missing 'source' field"
            assert "license" in record, "missing 'license' field"
            records.append(record)
        assert len(records) >= 30


# ─── Preference Seed Dataset ────────────────────────────────────────────


class TestPreferenceSeed:
    def test_preference_seed_jsonl_exists(self):
        assert (PROJECT_ROOT / "dataset" / "samples" / "preference_seed.jsonl").exists()

    def test_preference_seed_validates(self):
        path = PROJECT_ROOT / "dataset" / "samples" / "preference_seed.jsonl"
        lines = path.read_text().strip().splitlines()
        records = []
        for line in lines:
            record = json.loads(line)
            assert "prompt" in record, "missing 'prompt' field"
            assert "chosen" in record, "missing 'chosen' field"
            assert "rejected" in record, "missing 'rejected' field"
            assert "source" in record, "missing 'source' field"
            assert "license" in record, "missing 'license' field"
            records.append(record)
        assert len(records) >= 20


# ─── Dataset Preparation and Building ───────────────────────────────────


class TestDatasetBuild:
    def test_prepare_dataset_with_report(self):
        import tempfile

        with tempfile.TemporaryDirectory() as tmpdir:
            report_path = Path(tmpdir) / "report.json"
            output_path = Path(tmpdir) / "output.jsonl"
            result = _run_script(
                str(PROJECT_ROOT / "training" / "scripts" / "prepare_dataset.py"),
                "--input",
                str(PROJECT_ROOT / "dataset" / "samples" / "sft_seed.jsonl"),
                "--output",
                str(output_path),
                "--schema",
                "sft",
                "--report",
                str(report_path),
            )
            assert result.returncode == 0, f"prepare_dataset.py failed:\n{result.stdout}\n{result.stderr}"

    def test_build_dataset_mix_works(self):
        import tempfile

        with tempfile.TemporaryDirectory() as tmpdir:
            result = _run_script(
                str(PROJECT_ROOT / "training" / "scripts" / "build_dataset_mix.py"),
                "--sft",
                str(PROJECT_ROOT / "dataset" / "samples" / "sft_seed.jsonl"),
                "--preference",
                str(PROJECT_ROOT / "dataset" / "samples" / "preference_seed.jsonl"),
                "--output-dir",
                tmpdir,
                "--report",
            )
            assert result.returncode == 0, f"build_dataset_mix.py failed:\n{result.stdout}\n{result.stderr}"
            assert (Path(tmpdir) / "sft.train.jsonl").exists()
            assert (Path(tmpdir) / "preference.train.jsonl").exists()
            assert (Path(tmpdir) / "report.json").exists()


# ─── KimariFit Evaluation ──────────────────────────────────────────────


class TestKimariFit:
    def test_kimarifit_dry_run(self):
        result = _run_script(
            str(PROJECT_ROOT / "eval" / "kimarifit.py"),
            "--prompts",
            str(PROJECT_ROOT / "eval" / "kimarifit_prompts.jsonl"),
            "--dry-run",
        )
        assert result.returncode == 0, f"kimarifit.py --dry-run failed:\n{result.stdout}\n{result.stderr}"

    def test_kimarifit_dry_run_json(self):
        result = _run_script(
            str(PROJECT_ROOT / "eval" / "kimarifit.py"),
            "--prompts",
            str(PROJECT_ROOT / "eval" / "kimarifit_prompts.jsonl"),
            "--dry-run",
            "--json",
        )
        assert result.returncode == 0, f"kimarifit.py --dry-run --json failed:\n{result.stdout}\n{result.stderr}"
        data = json.loads(result.stdout)
        assert data["mode"] == "dry-run"
        assert data["total_prompts"] > 0
        assert data["category_count"] > 0


# ─── Training and Export Dry-Runs ───────────────────────────────────────


class TestTrainingDryRun:
    def test_train_sft_lora_dry_run(self):
        config_path = PROJECT_ROOT / "training" / "configs" / "kimari_sft_lora.example.yaml"
        result = _run_script(
            str(PROJECT_ROOT / "training" / "scripts" / "train_sft_lora.py"),
            "--dry-run",
            "--config",
            str(config_path),
        )
        assert result.returncode == 0, f"train_sft_lora.py --dry-run failed:\n{result.stdout}\n{result.stderr}"

    def test_export_gguf_plan_dry_run(self):
        result = _run_script(
            str(PROJECT_ROOT / "training" / "scripts" / "export_gguf_plan.py"),
            "--model-dir",
            "/tmp/nonexistent-model",
            "--output-dir",
            "/tmp/nonexistent-output",
            "--dry-run",
        )
        assert result.returncode == 0, f"export_gguf_plan.py --dry-run failed:\n{result.stdout}\n{result.stderr}"


# ─── Model Card and Decision Record ────────────────────────────────────


class TestModelCardAndDecision:
    def test_model_card_says_no_weights(self):
        content = (PROJECT_ROOT / "MODEL_CARD.md").read_text().lower()
        assert "not been released" in content or "not released" in content or "no weights" in content

    def test_model_decision_record_exists(self):
        assert (PROJECT_ROOT / "docs" / "MODEL_DECISION_RECORD.md").exists()

    def test_model_decision_record_not_accepted(self):
        content = (PROJECT_ROOT / "docs" / "MODEL_DECISION_RECORD.md").read_text()
        assert "Accepted" not in [line.strip() for line in content.splitlines() if "Status" in line]


# ─── Documentation ─────────────────────────────────────────────────────


class TestDocumentation:
    def test_first_training_run_exists(self):
        assert (PROJECT_ROOT / "docs" / "FIRST_TRAINING_RUN.md").exists()

    def test_kimarifit_rubric_exists(self):
        assert (PROJECT_ROOT / "eval" / "rubrics" / "kimarifit_rubric.md").exists()


# ─── No GGUF Tracked ───────────────────────────────────────────────────


class TestNoGGUF:
    def test_no_gguf_tracked(self):
        result = subprocess.run(
            ["git", "ls-files"],
            capture_output=True,
            text=True,
            timeout=30,
            cwd=str(PROJECT_ROOT),
        )
        tracked = result.stdout.strip().split("\n") if result.stdout.strip() else []
        gguf_files = [f for f in tracked if f.lower().endswith(".gguf")]
        assert gguf_files == [], f"GGUF files tracked in git: {gguf_files}"


# ─── Version Consistency ───────────────────────────────────────────────


class TestVersion:
    def test_version_consistency(self):
        from kimari import __version__

        assert __version__ == "0.1.23-alpha"
        pyproject = PROJECT_ROOT / "pyproject.toml"
        text = pyproject.read_text()
        assert 'version = "0.1.23-alpha"' in text


# ─── Release Check ─────────────────────────────────────────────────────


class TestReleaseCheck:
    def test_release_check_passes(self):
        result = subprocess.run(
            [sys.executable, "scripts/release/check-release.py"],
            capture_output=True,
            text=True,
            timeout=60,
            cwd=str(PROJECT_ROOT),
        )
        assert result.returncode == 0, f"check-release.py failed:\n{result.stdout}\n{result.stderr}"
