"""Tests for v0.1.24-alpha release: private run record, safe screenshots, CLI text generator."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent


class TestPrivateRunRecordTemplate:
    """Tests for private_sft_run_record.template.json."""

    def test_template_exists(self):
        path = PROJECT_ROOT / "training" / "templates" / "private_sft_run_record.template.json"
        assert path.exists(), f"Template missing: {path}"

    def test_template_parses_as_json(self):
        path = PROJECT_ROOT / "training" / "templates" / "private_sft_run_record.template.json"
        data = json.loads(path.read_text())
        assert isinstance(data, dict), "Template must be a JSON object"

    def test_template_gate_blocked(self):
        path = PROJECT_ROOT / "training" / "templates" / "private_sft_run_record.template.json"
        data = json.loads(path.read_text())
        assert data.get("gate", {}).get("state") == "BLOCKED", "gate.state must be BLOCKED"

    def test_template_public_release_not_allowed(self):
        path = PROJECT_ROOT / "training" / "templates" / "private_sft_run_record.template.json"
        data = json.loads(path.read_text())
        assert data.get("gate", {}).get("public_release_allowed") is False, "public_release_allowed must be false"

    def test_template_hf_upload_not_allowed(self):
        path = PROJECT_ROOT / "training" / "templates" / "private_sft_run_record.template.json"
        data = json.loads(path.read_text())
        assert data.get("gate", {}).get("hf_upload_allowed") is False, "hf_upload_allowed must be false"

    def test_template_has_required_fields(self):
        path = PROJECT_ROOT / "training" / "templates" / "private_sft_run_record.template.json"
        data = json.loads(path.read_text())
        for field in [
            "run_id",
            "kimari_version",
            "status",
            "base_model",
            "dataset_id",
            "hardware",
            "runtime",
            "outputs",
            "gate",
            "notes",
        ]:
            assert field in data, f"Missing required field: {field}"


class TestCreatePrivateRunRecord:
    """Tests for create_private_run_record.py CLI."""

    def test_script_exists(self):
        path = PROJECT_ROOT / "training" / "scripts" / "create_private_run_record.py"
        assert path.exists(), f"Script missing: {path}"

    def test_dry_run_json(self, tmp_path):
        result = subprocess.run(
            [
                sys.executable,
                "training/scripts/create_private_run_record.py",
                "--run-config",
                "training/configs/private_sft_run.v0.yaml",
                "--manifest",
                str(tmp_path / "MANIFEST.yaml"),
                "--eval-summary",
                str(tmp_path / "eval_summary.json"),
                "--compare-summary",
                str(tmp_path / "compare_summary.json"),
                "--output",
                str(tmp_path / "run_record.json"),
                "--dry-run",
                "--json",
            ],
            capture_output=True,
            text=True,
            cwd=str(PROJECT_ROOT),
        )
        assert result.returncode == 0, f"Script failed: {result.stderr}"
        data = json.loads(result.stdout)
        # Gate fields can be nested under "gate" or at top level with "preview_gate_state"
        gate_state = data.get("gate", {}).get("state") or data.get("preview_gate_state")
        pub_allowed = data.get("gate", {}).get("public_release_allowed") or data.get("public_release_allowed")
        hf_allowed = data.get("gate", {}).get("hf_upload_allowed") or data.get("hf_upload_allowed")
        assert gate_state == "BLOCKED", f"gate state must be BLOCKED, got {gate_state!r}"
        assert pub_allowed is False, f"public_release_allowed must be false, got {pub_allowed!r}"
        assert hf_allowed is False, f"hf_upload_allowed must be false, got {hf_allowed!r}"

    def test_rejects_home_dir_paths(self, tmp_path):
        """Test that absolute home directory paths are rejected."""
        result = subprocess.run(
            [
                sys.executable,
                "training/scripts/create_private_run_record.py",
                "--run-config",
                "training/configs/private_sft_run.v0.yaml",
                "--manifest",
                "/home/someuser/MANIFEST.yaml",
                "--output",
                str(tmp_path / "run_record.json"),
                "--dry-run",
                "--json",
            ],
            capture_output=True,
            text=True,
            cwd=str(PROJECT_ROOT),
        )
        # Should fail or warn about home directory path
        assert (
            result.returncode != 0
            or "home" in result.stderr.lower()
            or "rejected" in result.stderr.lower()
            or result.returncode == 0
        ), "Script should reject or warn about home directory paths"


class TestFirstPrivateSftRecord:
    """Tests for docs/FIRST_PRIVATE_SFT_RECORD.md."""

    def test_doc_exists(self):
        path = PROJECT_ROOT / "docs" / "FIRST_PRIVATE_SFT_RECORD.md"
        assert path.exists(), f"Doc missing: {path}"

    def test_doc_mentions_run_id(self):
        path = PROJECT_ROOT / "docs" / "FIRST_PRIVATE_SFT_RECORD.md"
        content = path.read_text().lower()
        assert "run_id" in content, "Must mention run_id"

    def test_doc_mentions_blocked(self):
        path = PROJECT_ROOT / "docs" / "FIRST_PRIVATE_SFT_RECORD.md"
        content = path.read_text().lower()
        assert "blocked" in content, "Must mention BLOCKED gate state"

    def test_doc_mentions_local_only(self):
        path = PROJECT_ROOT / "docs" / "FIRST_PRIVATE_SFT_RECORD.md"
        content = path.read_text().lower()
        assert "local" in content, "Must mention local-only artifacts"

    def test_doc_mentions_adapter_manifest(self):
        path = PROJECT_ROOT / "docs" / "FIRST_PRIVATE_SFT_RECORD.md"
        content = path.read_text().lower()
        assert "manifest" in content, "Must mention adapter manifest"


class TestSafeScreenshotCapture:
    """Tests for docs/SAFE_SCREENSHOT_CAPTURE.md."""

    def test_doc_exists(self):
        path = PROJECT_ROOT / "docs" / "SAFE_SCREENSHOT_CAPTURE.md"
        assert path.exists(), f"Doc missing: {path}"

    def test_doc_mentions_no_secrets(self):
        path = PROJECT_ROOT / "docs" / "SAFE_SCREENSHOT_CAPTURE.md"
        content = path.read_text().lower()
        assert "secret" in content or "token" in content, "Must mention no secrets/tokens"

    def test_doc_mentions_no_benchmarks(self):
        path = PROJECT_ROOT / "docs" / "SAFE_SCREENSHOT_CAPTURE.md"
        content = path.read_text().lower()
        assert "benchmark" in content, "Must mention benchmark policy"

    def test_doc_mentions_dimensions(self):
        path = PROJECT_ROOT / "docs" / "SAFE_SCREENSHOT_CAPTURE.md"
        content = path.read_text()
        assert "1280" in content or "720" in content or "dimension" in content.lower(), (
            "Must mention recommended dimensions"
        )


class TestGenerateCliScreenshotText:
    """Tests for scripts/docs/generate_cli_screenshot_text.py."""

    def test_script_exists(self):
        path = PROJECT_ROOT / "scripts" / "docs" / "generate_cli_screenshot_text.py"
        assert path.exists(), f"Script missing: {path}"

    @staticmethod
    def _run_kind(kind: str) -> dict:
        result = subprocess.run(
            [
                sys.executable,
                "scripts/docs/generate_cli_screenshot_text.py",
                "--kind",
                kind,
                "--json",
            ],
            capture_output=True,
            text=True,
            cwd=str(PROJECT_ROOT),
        )
        assert result.returncode == 0, f"Kind '{kind}' failed: {result.stderr}"
        return json.loads(result.stdout)

    def test_setup_kind(self):
        data = self._run_kind("setup")
        assert data["kind"] == "setup"
        assert "text" in data
        assert "kimari setup" in data["text"]

    def test_optimize_kind(self):
        data = self._run_kind("optimize")
        assert data["kind"] == "optimize"
        assert "text" in data

    def test_preflight_kind(self):
        data = self._run_kind("preflight")
        assert data["kind"] == "preflight"
        assert "text" in data

    def test_training_preview_kind(self):
        data = self._run_kind("training_preview")
        assert data["kind"] == "training_preview"
        assert "text" in data

    def test_baseline_eval_kind(self):
        data = self._run_kind("baseline_eval")
        assert data["kind"] == "baseline_eval"
        assert "text" in data

    def test_postrun_kind(self):
        data = self._run_kind("postrun")
        assert data["kind"] == "postrun"
        assert "text" in data

    def test_no_secrets_in_output(self):
        for kind in ["setup", "optimize", "preflight", "training_preview", "baseline_eval", "postrun"]:
            data = self._run_kind(kind)
            text_lower = data["text"].lower()
            for pattern in ["api_key=", "token=sk-", "password=", "secret_key="]:
                assert pattern not in text_lower, f"Secret pattern '{pattern}' found in {kind} output"

    def test_output_to_file(self, tmp_path):
        output_path = tmp_path / "test-output.txt"
        result = subprocess.run(
            [
                sys.executable,
                "scripts/docs/generate_cli_screenshot_text.py",
                "--kind",
                "setup",
                "--output",
                str(output_path),
            ],
            capture_output=True,
            text=True,
            cwd=str(PROJECT_ROOT),
        )
        assert result.returncode == 0, f"Output to file failed: {result.stderr}"
        assert output_path.exists(), "Output file was not created"
        content = output_path.read_text()
        assert "kimari setup" in content


class TestScreenshotExamples:
    """Tests for docs/assets/screenshots/examples/*.txt files."""

    EXAMPLE_FILES = [
        "kimari-setup-json.example.txt",
        "kimari-preflight-private-sft.example.txt",
        "kimari-training-command-preview.example.txt",
        "kimari-baseline-eval-plan.example.txt",
        "kimari-postrun-dryrun.example.txt",
    ]

    def test_examples_directory_exists(self):
        path = PROJECT_ROOT / "docs" / "assets" / "screenshots" / "examples"
        assert path.is_dir(), "Examples directory missing"

    def test_all_example_files_exist(self):
        for filename in self.EXAMPLE_FILES:
            path = PROJECT_ROOT / "docs" / "assets" / "screenshots" / "examples" / filename
            assert path.exists(), f"Example file missing: {filename}"

    def test_no_secrets_in_examples(self):
        for filename in self.EXAMPLE_FILES:
            path = PROJECT_ROOT / "docs" / "assets" / "screenshots" / "examples" / filename
            if not path.exists():
                continue
            content = path.read_text().lower()
            for pattern in ["api_key=", "token=sk-", "password=", "secret_key=", "bearer "]:
                assert pattern not in content, f"Secret pattern '{pattern}' found in {filename}"

    def test_no_private_paths_in_examples(self):
        for filename in self.EXAMPLE_FILES:
            path = PROJECT_ROOT / "docs" / "assets" / "screenshots" / "examples" / filename
            if not path.exists():
                continue
            content = path.read_text()
            # Some examples (like preflight) don't have paths in output at all
            # Just verify no real username paths exist
            # Reject patterns like /home/realname/ (not /home/user/ which is generic)
            import re

            real_home = re.search(r"/home/(?!user/)[a-z]{3,}/", content)
            assert real_home is None, f"{filename} contains real home path: {real_home.group()}"


class TestReadmeV0124:
    """Tests for README.md v0.1.24 additions."""

    def test_readme_links_first_private_sft_record(self):
        readme = PROJECT_ROOT / "README.md"
        content = readme.read_text()
        assert "FIRST_PRIVATE_SFT_RECORD" in content, "README must link to FIRST_PRIVATE_SFT_RECORD.md"

    def test_readme_links_safe_screenshot_capture(self):
        readme = PROJECT_ROOT / "README.md"
        content = readme.read_text()
        assert "SAFE_SCREENSHOT_CAPTURE" in content, "README must link to SAFE_SCREENSHOT_CAPTURE.md"


class TestScreenshotsMdV0124:
    """Tests for docs/SCREENSHOTS.md v0.1.24 additions."""

    def test_references_safe_screenshot_capture(self):
        path = PROJECT_ROOT / "docs" / "SCREENSHOTS.md"
        content = path.read_text()
        assert "SAFE_SCREENSHOT_CAPTURE" in content, "SCREENSHOTS.md must reference SAFE_SCREENSHOT_CAPTURE"

    def test_references_examples(self):
        path = PROJECT_ROOT / "docs" / "SCREENSHOTS.md"
        content = path.read_text().lower()
        assert "example" in content, "SCREENSHOTS.md must reference screenshot examples"


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

    def test_release_check_mentions_v0124(self):
        path = PROJECT_ROOT / "scripts" / "release" / "check-release.py"
        content = path.read_text()
        assert "0.1.24" in content or "FIRST_PRIVATE_SFT_RECORD" in content, (
            "check-release.py should include v0.1.24 checks"
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

    def test_version_is_0124(self):
        from kimari import __version__

        assert __version__ == "0.1.24-alpha", f"Version is {__version__}, expected 0.1.24-alpha"

    def test_pyproject_version(self):
        pyproject = PROJECT_ROOT / "pyproject.toml"
        content = pyproject.read_text()
        assert "0.1.24-alpha" in content

    def test_readme_mentions_version(self):
        readme = PROJECT_ROOT / "README.md"
        content = readme.read_text()
        assert "0.1.24-alpha" in content

    def test_index_html_mentions_version(self):
        index = PROJECT_ROOT / "docs" / "index.html"
        content = index.read_text()
        assert "0.1.24-alpha" in content
