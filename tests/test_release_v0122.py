"""Tests for v0.1.22-alpha release: private SFT execution package, preflight/postrun, eval plans."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent


class TestPreflightScript:
    """Tests for preflight_private_sft.py script."""

    def test_script_exists(self):
        path = PROJECT_ROOT / "training" / "scripts" / "preflight_private_sft.py"
        assert path.exists(), f"Script missing: {path}"

    def test_preflight_json_without_torch(self):
        result = subprocess.run(
            [
                sys.executable,
                "training/scripts/preflight_private_sft.py",
                "--run-config",
                "training/configs/private_sft_run.v0.yaml",
                "--json",
            ],
            capture_output=True,
            text=True,
            cwd=str(PROJECT_ROOT),
        )
        assert result.returncode == 0, f"Preflight failed: {result.stderr}"
        data = json.loads(result.stdout)
        assert "checks" in data or "status" in data or "python_version" in data

    def test_preflight_warns_about_missing_torch(self):
        result = subprocess.run(
            [
                sys.executable,
                "training/scripts/preflight_private_sft.py",
                "--run-config",
                "training/configs/private_sft_run.v0.yaml",
                "--json",
            ],
            capture_output=True,
            text=True,
            cwd=str(PROJECT_ROOT),
        )
        # Should not fail, but should mention torch status
        output = result.stdout + result.stderr
        assert "torch" in output.lower()


class TestPostrunScript:
    """Tests for postrun_private_sft.py script."""

    def test_script_exists(self):
        path = PROJECT_ROOT / "training" / "scripts" / "postrun_private_sft.py"
        assert path.exists(), f"Script missing: {path}"

    def test_postrun_dry_run_json(self, tmp_path):
        result = subprocess.run(
            [
                sys.executable,
                "training/scripts/postrun_private_sft.py",
                "--run-config",
                "training/configs/private_sft_run.v0.yaml",
                "--adapter-dir",
                str(tmp_path / "fake-adapter"),
                "--eval-result",
                "tests/fixtures/private_eval_raw.json",
                "--output-summary",
                str(tmp_path / "adapter-summary.json"),
                "--dry-run",
                "--json",
            ],
            capture_output=True,
            text=True,
            cwd=str(PROJECT_ROOT),
        )
        assert result.returncode == 0, f"Postrun failed: {result.stderr}"
        data = json.loads(result.stdout)
        assert "dry_run" in data or "steps" in data or "status" in data


class TestTrainingCommandPreview:
    """Tests for run_training_command_preview.py script."""

    def test_script_exists(self):
        path = PROJECT_ROOT / "training" / "scripts" / "run_training_command_preview.py"
        assert path.exists(), f"Script missing: {path}"

    def test_command_preview_json(self):
        result = subprocess.run(
            [
                sys.executable,
                "training/scripts/run_training_command_preview.py",
                "--config",
                "training/configs/kimari_sft_lora.v0.example.yaml",
                "--json",
            ],
            capture_output=True,
            text=True,
            cwd=str(PROJECT_ROOT),
        )
        assert result.returncode == 0, f"Command preview failed: {result.stderr}"
        data = json.loads(result.stdout)
        assert "recommended_command" in data or "safety_warnings" in data or "forbidden_commit_patterns" in data


class TestBaselineEvalPlan:
    """Tests for run_baseline_eval_plan.py script."""

    def test_script_exists(self):
        path = PROJECT_ROOT / "eval" / "scripts" / "run_baseline_eval_plan.py"
        assert path.exists(), f"Script missing: {path}"

    def test_baseline_eval_plan_dry_run_json(self):
        result = subprocess.run(
            [
                sys.executable,
                "eval/scripts/run_baseline_eval_plan.py",
                "--model-label",
                "smollm3-base",
                "--prompts",
                "eval/kimarifit_prompts.jsonl",
                "--dry-run",
                "--json",
            ],
            capture_output=True,
            text=True,
            cwd=str(PROJECT_ROOT),
        )
        assert result.returncode == 0, f"Baseline eval plan failed: {result.stderr}"
        data = json.loads(result.stdout)
        assert "model_label" in data or "prompt_count" in data or "score_status" in data


class TestAdapterEvalPlan:
    """Tests for run_adapter_eval_plan.py script."""

    def test_script_exists(self):
        path = PROJECT_ROOT / "eval" / "scripts" / "run_adapter_eval_plan.py"
        assert path.exists(), f"Script missing: {path}"

    def test_adapter_eval_plan_dry_run_json(self):
        result = subprocess.run(
            [
                sys.executable,
                "eval/scripts/run_adapter_eval_plan.py",
                "--model-label",
                "kimari-smollm3-sft-v0",
                "--prompts",
                "eval/kimarifit_prompts.jsonl",
                "--dry-run",
                "--json",
            ],
            capture_output=True,
            text=True,
            cwd=str(PROJECT_ROOT),
        )
        assert result.returncode == 0, f"Adapter eval plan failed: {result.stderr}"
        data = json.loads(result.stdout)
        assert "model_label" in data or "prompt_count" in data or "score_status" in data


class TestPrivateExecutionConfig:
    """Tests for private_sft_execution.example.yaml."""

    def test_config_exists(self):
        path = PROJECT_ROOT / "training" / "configs" / "private_sft_execution.example.yaml"
        assert path.exists(), f"Config missing: {path}"

    def test_config_has_required_fields(self):
        path = PROJECT_ROOT / "training" / "configs" / "private_sft_execution.example.yaml"
        content = path.read_text()
        required = ["provider", "gpu_type", "commands", "preflight", "train", "postrun"]
        for field in required:
            assert field in content, f"Missing field in execution config: {field}"


class TestNewDocs:
    """Tests for new v0.1.22 documentation files."""

    def test_remote_gpu_guide_exists(self):
        path = PROJECT_ROOT / "docs" / "REMOTE_GPU_RUNPOD_GUIDE.md"
        assert path.exists(), f"Doc missing: {path}"

    def test_private_run_artifacts_exists(self):
        path = PROJECT_ROOT / "docs" / "PRIVATE_RUN_ARTIFACTS.md"
        assert path.exists(), f"Doc missing: {path}"

    def test_private_run_failures_exists(self):
        path = PROJECT_ROOT / "docs" / "PRIVATE_RUN_FAILURES.md"
        assert path.exists(), f"Doc missing: {path}"

    def test_remote_gpu_mentions_runpod(self):
        path = PROJECT_ROOT / "docs" / "REMOTE_GPU_RUNPOD_GUIDE.md"
        content = path.read_text().lower()
        assert "runpod" in content
        assert "4090" in content or "a100" in content

    def test_private_run_artifacts_classifies(self):
        path = PROJECT_ROOT / "docs" / "PRIVATE_RUN_ARTIFACTS.md"
        content = path.read_text().lower()
        assert "safetensors" in content
        assert "commit" in content or "committed" in content

    def test_private_run_failures_has_troubleshooting(self):
        path = PROJECT_ROOT / "docs" / "PRIVATE_RUN_FAILURES.md"
        content = path.read_text().lower()
        assert "oom" in content or "out of memory" in content
        assert "cuda" in content


class TestTrainingRequirements:
    """Tests for training/requirements-training.txt."""

    def test_file_exists(self):
        path = PROJECT_ROOT / "training" / "requirements-training.txt"
        assert path.exists(), f"File missing: {path}"

    def test_contains_key_deps(self):
        path = PROJECT_ROOT / "training" / "requirements-training.txt"
        content = path.read_text()
        required = ["torch", "transformers", "peft", "trl", "accelerate", "datasets"]
        for dep in required:
            assert dep in content, f"Missing dependency: {dep}"

    def test_mentions_ci_note(self):
        path = PROJECT_ROOT / "training" / "requirements-training.txt"
        content = path.read_text().lower()
        assert "ci" in content


class TestTrainSftLoraImprovements:
    """Tests for train_sft_lora.py improvements."""

    def test_print_command_flag(self):
        result = subprocess.run(
            [
                sys.executable,
                "training/scripts/train_sft_lora.py",
                "--config",
                "training/configs/kimari_sft_lora.v0.example.yaml",
                "--print-command",
            ],
            capture_output=True,
            text=True,
            cwd=str(PROJECT_ROOT),
        )
        assert result.returncode == 0, f"--print-command failed: {result.stderr}"

    def test_estimate_only_flag(self):
        result = subprocess.run(
            [
                sys.executable,
                "training/scripts/train_sft_lora.py",
                "--config",
                "training/configs/kimari_sft_lora.v0.example.yaml",
                "--estimate-only",
            ],
            capture_output=True,
            text=True,
            cwd=str(PROJECT_ROOT),
        )
        assert result.returncode == 0, f"--estimate-only failed: {result.stderr}"


class TestReleaseCheck:
    """Tests for release check script."""

    def test_release_check_runs(self):
        result = subprocess.run(
            [sys.executable, "scripts/release/check-release.py"],
            capture_output=True,
            text=True,
            cwd=str(PROJECT_ROOT),
        )
        assert result.returncode == 0, f"Release check failed:\n{result.stdout}\n{result.stderr}"

    def test_release_check_mentions_v0122(self):
        path = PROJECT_ROOT / "scripts" / "release" / "check-release.py"
        content = path.read_text()
        assert "0.1.22" in content or "v0.1.22" in content or "REMOTE_GPU_RUNPOD" in content


class TestNoTrackedArtifacts:
    """Tests that no adapter/weight/GGUF files are tracked in git."""

    def test_no_safetensors_tracked(self):
        result = subprocess.run(
            ["git", "ls-files", "*.safetensors"],
            capture_output=True,
            text=True,
            cwd=str(PROJECT_ROOT),
        )
        files = [f for f in result.stdout.strip().splitlines() if f]
        assert len(files) == 0, f"Safetensors tracked: {files}"

    def test_no_gguf_tracked(self):
        result = subprocess.run(
            ["git", "ls-files", "*.gguf"],
            capture_output=True,
            text=True,
            cwd=str(PROJECT_ROOT),
        )
        files = [f for f in result.stdout.strip().splitlines() if f]
        assert len(files) == 0, f"GGUF tracked: {files}"

    def test_no_weight_files_tracked(self):
        result = subprocess.run(
            ["git", "ls-files", "*.bin", "*.pt", "*.pth", "*.ckpt"],
            capture_output=True,
            text=True,
            cwd=str(PROJECT_ROOT),
        )
        files = [f for f in result.stdout.strip().splitlines() if f]
        assert len(files) == 0, f"Weight files tracked: {files}"


class TestVersionConsistency:
    """Tests for version consistency across files."""

    def test_version_is_0122(self):
        from kimari import __version__

        assert __version__ == "0.1.22-alpha", f"Version is {__version__}, expected 0.1.22-alpha"

    def test_pyproject_version(self):
        pyproject = PROJECT_ROOT / "pyproject.toml"
        content = pyproject.read_text()
        assert "0.1.22-alpha" in content

    def test_readme_mentions_version(self):
        readme = PROJECT_ROOT / "README.md"
        content = readme.read_text()
        assert "0.1.22-alpha" in content

    def test_index_html_mentions_version(self):
        index = PROJECT_ROOT / "docs" / "index.html"
        content = index.read_text()
        assert "0.1.22-alpha" in content
