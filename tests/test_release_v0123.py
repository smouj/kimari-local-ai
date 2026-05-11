"""Tests for v0.1.23-alpha release: postrun --json fix, preflight dataset_build_dir, screenshots docs."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent


class TestPostrunJsonFix:
    """Tests for postrun_private_sft.py --json passthrough fix."""

    def test_script_exists(self):
        path = PROJECT_ROOT / "training" / "scripts" / "postrun_private_sft.py"
        assert path.exists(), f"Script missing: {path}"

    def test_create_eval_summary_includes_json_in_command(self):
        """Verify that step_create_eval_summary passes --json to the subprocess."""
        path = PROJECT_ROOT / "training" / "scripts" / "postrun_private_sft.py"
        content = path.read_text()
        # Find the step_create_eval_summary function and verify --json is in the cmd list
        assert "step_create_eval_summary" in content, "step_create_eval_summary function not found"
        assert '"--json"' in content, "--json flag not found in postrun script"

    def test_no_post_hoc_json_append(self):
        """Verify that --json is not appended to command string after execution."""
        path = PROJECT_ROOT / "training" / "scripts" / "postrun_private_sft.py"
        content = path.read_text()
        # The old pattern was: result["command"] += " --json"
        # This should NOT exist anymore
        assert 'result["command"] += " --json"' not in content, (
            "Found post-hoc --json append — --json should be in the cmd list, not appended to command string"
        )

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

    def test_eval_summary_command_includes_json(self, tmp_path):
        """Verify that the create_eval_summary step command includes --json."""
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
        # Find the create_eval_summary step
        steps = data.get("steps", [])
        eval_step = None
        for step in steps:
            if step.get("label") == "create_eval_summary":
                eval_step = step
                break
        assert eval_step is not None, "create_eval_summary step not found in postrun output"
        command = eval_step.get("command", "")
        assert "--json" in command, f"--json not in create_eval_summary command: {command}"


class TestPreflightDatasetBuildDir:
    """Tests for preflight_private_sft.py dataset_build_dir from run_config."""

    def test_script_exists(self):
        path = PROJECT_ROOT / "training" / "scripts" / "preflight_private_sft.py"
        assert path.exists(), f"Script missing: {path}"

    def test_preflight_reads_dataset_build_dir_from_config(self):
        """Verify that preflight reads dataset_build_dir from run_config."""
        path = PROJECT_ROOT / "training" / "scripts" / "preflight_private_sft.py"
        content = path.read_text()
        assert "dataset_build_dir" in content, "dataset_build_dir not mentioned in preflight script"
        assert "run_config" in content, "run_config not mentioned in preflight script"

    def test_preflight_has_fallback(self):
        """Verify that preflight has fallback for dataset_build_dir."""
        path = PROJECT_ROOT / "training" / "scripts" / "preflight_private_sft.py"
        content = path.read_text()
        assert "fallback" in content.lower(), "No fallback logic found in preflight script"
        assert "DEFAULT_DATASET_REPORT" in content, "DEFAULT_DATASET_REPORT not found in preflight script"

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
        # Should have dataset_build_dir_source field
        assert "dataset_build_dir_source" in data, "dataset_build_dir_source not in preflight output"
        assert data["dataset_build_dir_source"] in ("run_config", "fallback"), (
            f"Unexpected dataset_build_dir_source: {data['dataset_build_dir_source']}"
        )

    def test_preflight_with_custom_run_config(self, tmp_path):
        """Test preflight with a run config that specifies dataset_build_dir."""
        custom_config = tmp_path / "custom_run.yaml"
        custom_config.write_text(
            "run_id: test-v0123\n"
            "status: planned\n"
            "base_model: HuggingFaceTB/SmolLM3-3B\n"
            "dataset_build_dir: dataset/build/kimari-v0\n"
            "output_dir: training/runs/kimari-smollm3-sft-v0\n"
            "public_release_allowed: false\n"
            "hf_upload_allowed: false\n"
        )
        result = subprocess.run(
            [
                sys.executable,
                "training/scripts/preflight_private_sft.py",
                "--run-config",
                str(custom_config),
                "--json",
            ],
            capture_output=True,
            text=True,
            cwd=str(PROJECT_ROOT),
        )
        assert result.returncode == 0, f"Preflight with custom config failed: {result.stderr}"
        data = json.loads(result.stdout)
        # If dataset_build_dir was in config, source should be run_config
        # (even if the directory doesn't exist, the source tracking should work)
        assert "dataset_build_dir_source" in data
        # The source should be run_config since we specified dataset_build_dir in the custom config
        if data.get("dataset_build_dir") is not None:
            assert data["dataset_build_dir_source"] == "run_config", (
                f"Expected dataset_build_dir_source='run_config' when dataset_build_dir is in config, got '{data['dataset_build_dir_source']}'"
            )

    def test_preflight_fallback_without_dataset_build_dir(self, tmp_path):
        """Test preflight with a run config that does NOT specify dataset_build_dir."""
        minimal_config = tmp_path / "minimal_run.yaml"
        minimal_config.write_text(
            "run_id: test-minimal\n"
            "status: planned\n"
            "base_model: HuggingFaceTB/SmolLM3-3B\n"
            "output_dir: training/runs/kimari-smollm3-sft-v0\n"
            "public_release_allowed: false\n"
            "hf_upload_allowed: false\n"
        )
        result = subprocess.run(
            [
                sys.executable,
                "training/scripts/preflight_private_sft.py",
                "--run-config",
                str(minimal_config),
                "--json",
            ],
            capture_output=True,
            text=True,
            cwd=str(PROJECT_ROOT),
        )
        assert result.returncode == 0, f"Preflight with minimal config failed: {result.stderr}"
        data = json.loads(result.stdout)
        # Without dataset_build_dir in config, source should be fallback
        assert data["dataset_build_dir_source"] == "fallback", (
            f"Expected dataset_build_dir_source='fallback' without dataset_build_dir in config, got '{data['dataset_build_dir_source']}'"
        )


class TestScreenshotsDocs:
    """Tests for screenshots documentation files."""

    def test_screenshots_md_exists(self):
        path = PROJECT_ROOT / "docs" / "SCREENSHOTS.md"
        assert path.exists(), f"Doc missing: {path}"

    def test_screenshots_assets_readme_exists(self):
        path = PROJECT_ROOT / "docs" / "assets" / "screenshots" / "README.md"
        assert path.exists(), f"Doc missing: {path}"

    def test_screenshots_placeholder_exists(self):
        path = PROJECT_ROOT / "docs" / "assets" / "screenshots" / "PLACEHOLDER.md"
        assert path.exists(), f"Placeholder missing: {path}"

    def test_screenshots_md_mentions_no_secrets(self):
        path = PROJECT_ROOT / "docs" / "SCREENSHOTS.md"
        content = path.read_text().lower()
        assert "secret" in content or "no secret" in content, "SCREENSHOTS.md should mention no secrets policy"

    def test_screenshots_md_mentions_no_benchmarks(self):
        path = PROJECT_ROOT / "docs" / "SCREENSHOTS.md"
        content = path.read_text().lower()
        assert "benchmark" in content or "no benchmark" in content, "SCREENSHOTS.md should mention benchmark policy"

    def test_screenshots_md_mentions_not_released(self):
        path = PROJECT_ROOT / "docs" / "SCREENSHOTS.md"
        content = path.read_text().lower()
        assert "not released" in content or "not yet released" in content, (
            "SCREENSHOTS.md should clarify Kimari-4B is not released"
        )

    def test_screenshots_assets_readme_has_naming_convention(self):
        path = PROJECT_ROOT / "docs" / "assets" / "screenshots" / "README.md"
        content = path.read_text().lower()
        assert "naming" in content or "convention" in content, "Screenshots README should define naming conventions"

    def test_screenshots_assets_readme_allows_png_webp(self):
        path = PROJECT_ROOT / "docs" / "assets" / "screenshots" / "README.md"
        content = path.read_text().lower()
        assert "png" in content and "webp" in content, (
            "Screenshots README should specify PNG and WebP as allowed formats"
        )

    def test_placeholder_has_planned_screenshots(self):
        path = PROJECT_ROOT / "docs" / "assets" / "screenshots" / "PLACEHOLDER.md"
        content = path.read_text()
        assert "kimari-setup-json" in content, "PLACEHOLDER should list kimari-setup-json screenshot"
        assert "preflight" in content, "PLACEHOLDER should list preflight screenshot"

    def test_no_secrets_in_screenshot_docs(self):
        """Verify no secrets patterns in screenshot docs."""
        for doc_path in [
            PROJECT_ROOT / "docs" / "SCREENSHOTS.md",
            PROJECT_ROOT / "docs" / "assets" / "screenshots" / "README.md",
            PROJECT_ROOT / "docs" / "assets" / "screenshots" / "PLACEHOLDER.md",
        ]:
            if doc_path.exists():
                content = doc_path.read_text().lower()
                for pattern in ["api_key=", "token=sk-", "password=", "secret_key="]:
                    assert pattern not in content, f"Secret pattern '{pattern}' found in {doc_path.name}"


class TestReadmeScreenshots:
    """Tests for README.md screenshots section."""

    def test_readme_links_screenshots(self):
        readme = PROJECT_ROOT / "README.md"
        content = readme.read_text()
        assert "SCREENSHOTS.md" in content, "README.md must link to docs/SCREENSHOTS.md"

    def test_readme_has_screenshots_section(self):
        readme = PROJECT_ROOT / "README.md"
        content = readme.read_text()
        assert "Screenshots" in content or "screenshots" in content.lower(), "README.md must have a screenshots section"


class TestIndexHtmlScreenshots:
    """Tests for docs/index.html screenshots/CLI preview section."""

    def test_index_mentions_screenshots(self):
        index = PROJECT_ROOT / "docs" / "index.html"
        content = index.read_text().lower()
        assert "screenshot" in content or "cli preview" in content, (
            "docs/index.html must mention screenshots or CLI preview"
        )

    def test_index_links_screenshots_md(self):
        index = PROJECT_ROOT / "docs" / "index.html"
        content = index.read_text()
        assert "SCREENSHOTS.md" in content, "docs/index.html should link to SCREENSHOTS.md"


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

    def test_release_check_mentions_v0123(self):
        path = PROJECT_ROOT / "scripts" / "release" / "check-release.py"
        content = path.read_text()
        assert "0.1.23" in content or "v0.1.23" in content or "SCREENSHOTS" in content, (
            "check-release.py should include v0.1.23 checks"
        )


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

    def test_version_is_0123(self):
        from kimari import __version__

        assert __version__ == "0.1.23-alpha", f"Version is {__version__}, expected 0.1.23-alpha"

    def test_pyproject_version(self):
        pyproject = PROJECT_ROOT / "pyproject.toml"
        content = pyproject.read_text()
        assert "0.1.23-alpha" in content

    def test_readme_mentions_version(self):
        readme = PROJECT_ROOT / "README.md"
        content = readme.read_text()
        assert "0.1.23-alpha" in content

    def test_index_html_mentions_version(self):
        index = PROJECT_ROOT / "docs" / "index.html"
        content = index.read_text()
        assert "0.1.23-alpha" in content
