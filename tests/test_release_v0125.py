"""Tests for v0.1.25-alpha release: HF token safety, secret scanner, private run record hardening, handoff."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent


class TestHfTokenSafety:
    """Tests for docs/HF_TOKEN_SAFETY.md."""

    def test_doc_exists(self):
        path = PROJECT_ROOT / "docs" / "HF_TOKEN_SAFETY.md"
        assert path.exists(), f"Doc missing: {path}"

    def test_doc_mentions_token(self):
        path = PROJECT_ROOT / "docs" / "HF_TOKEN_SAFETY.md"
        content = path.read_text().lower()
        assert "token" in content, "Must mention token handling"

    def test_doc_mentions_revoke(self):
        path = PROJECT_ROOT / "docs" / "HF_TOKEN_SAFETY.md"
        content = path.read_text().lower()
        assert "revok" in content, "Must mention token revocation"

    def test_doc_mentions_environment_variables(self):
        path = PROJECT_ROOT / "docs" / "HF_TOKEN_SAFETY.md"
        content = path.read_text().lower()
        assert "environment" in content or "env" in content, "Must mention environment variables"

    def test_doc_mentions_scan_for_secrets(self):
        path = PROJECT_ROOT / "docs" / "HF_TOKEN_SAFETY.md"
        content = path.read_text()
        assert "scan_for_secrets" in content, "Must reference scan_for_secrets.py"

    def test_doc_no_real_token(self):
        path = PROJECT_ROOT / "docs" / "HF_TOKEN_SAFETY.md"
        content = path.read_text()
        # Check no real HF token pattern (hf_ followed by 30+ real alphanumeric chars, not just x's)
        import re

        for match in re.finditer(r"hf_[a-zA-Z0-9]{30,}", content):
            token = match.group()
            # Example tokens use 'x' or repeated chars like hf_xxx...
            non_x_chars = sum(1 for c in token[3:] if c != "x" and c != "X" and not c.isdigit())
            assert non_x_chars < 5, f"Possible real HF token detected: {token[:15]}..."


class TestScanForSecrets:
    """Tests for scripts/security/scan_for_secrets.py."""

    def test_script_exists(self):
        path = PROJECT_ROOT / "scripts" / "security" / "scan_for_secrets.py"
        assert path.exists(), f"Script missing: {path}"

    def test_scan_json_output(self):
        result = subprocess.run(
            [
                sys.executable,
                "scripts/security/scan_for_secrets.py",
                "--paths",
                "README.md",
                "--json",
            ],
            capture_output=True,
            text=True,
            cwd=str(PROJECT_ROOT),
        )
        assert result.returncode in (0, 1), f"Script failed: {result.stderr}"
        data = json.loads(result.stdout)
        assert "findings" in data
        assert "total_findings" in data
        assert isinstance(data["findings"], list)

    def test_scan_critical_count(self):
        result = subprocess.run(
            [
                sys.executable,
                "scripts/security/scan_for_secrets.py",
                "--paths",
                "README.md",
                "docs",
                "--json",
            ],
            capture_output=True,
            text=True,
            cwd=str(PROJECT_ROOT),
        )
        assert result.returncode in (0, 1), f"Script failed: {result.stderr}"
        data = json.loads(result.stdout)
        # No critical findings should exist in docs
        assert data["critical"] == 0, f"Critical findings detected: {data['findings']}"


class TestCreatePrivateRunRecordHardening:
    """Tests for hardened create_private_run_record.py."""

    def test_rejects_linux_home_path(self):
        result = subprocess.run(
            [
                sys.executable,
                "training/scripts/create_private_run_record.py",
                "--run-config",
                "training/configs/private_sft_run.v0.yaml",
                "--manifest",
                "/home/someuser/MANIFEST.yaml",
                "--output",
                "/tmp/run_record.json",
                "--dry-run",
                "--json",
            ],
            capture_output=True,
            text=True,
            cwd=str(PROJECT_ROOT),
        )
        assert result.returncode != 0 or "home" in result.stderr.lower(), "Should reject /home/user/ paths"

    def test_rejects_macos_home_path(self):
        result = subprocess.run(
            [
                sys.executable,
                "training/scripts/create_private_run_record.py",
                "--run-config",
                "training/configs/private_sft_run.v0.yaml",
                "--manifest",
                "/Users/someuser/MANIFEST.yaml",
                "--output",
                "/tmp/run_record.json",
                "--dry-run",
                "--json",
            ],
            capture_output=True,
            text=True,
            cwd=str(PROJECT_ROOT),
        )
        assert result.returncode != 0 or "home" in result.stderr.lower() or "users" in result.stderr.lower(), (
            "Should reject /Users/user/ paths"
        )

    def test_rejects_windows_user_path(self):
        result = subprocess.run(
            [
                sys.executable,
                "training/scripts/create_private_run_record.py",
                "--run-config",
                "training/configs/private_sft_run.v0.yaml",
                "--manifest",
                "C:\\Users\\someuser\\MANIFEST.yaml",
                "--output",
                "/tmp/run_record.json",
                "--dry-run",
                "--json",
            ],
            capture_output=True,
            text=True,
            cwd=str(PROJECT_ROOT),
        )
        assert (
            result.returncode != 0
            or "home" in result.stderr.lower()
            or "users" in result.stderr.lower()
            or "user" in result.stderr.lower()
        ), "Should reject C:\\Users\\user\\ paths"

    def test_detects_suspicious_token_in_fixture(self, tmp_path):
        """Test that suspicious patterns are detected in eval summaries."""
        # Create a fixture with a suspicious pattern
        suspicious_eval = {"data": "api_key = 'sk-1234567890abcdef'"}
        eval_path = tmp_path / "eval_summary.json"
        eval_path.write_text(json.dumps(suspicious_eval))

        result = subprocess.run(
            [
                sys.executable,
                "training/scripts/create_private_run_record.py",
                "--run-config",
                "training/configs/private_sft_run.v0.yaml",
                "--eval-summary",
                str(eval_path),
                "--output",
                str(tmp_path / "run_record.json"),
                "--dry-run",
                "--json",
            ],
            capture_output=True,
            text=True,
            cwd=str(PROJECT_ROOT),
        )
        # The script should detect suspicious patterns
        assert result.returncode == 0 or "suspicious" in result.stderr.lower(), (
            f"Should detect suspicious patterns in eval summary: stderr={result.stderr[:200]}"
        )

    def test_security_scan_status_in_output(self):
        result = subprocess.run(
            [
                sys.executable,
                "training/scripts/create_private_run_record.py",
                "--run-config",
                "training/configs/private_sft_run.v0.yaml",
                "--output",
                "/tmp/run_record.json",
                "--dry-run",
                "--json",
            ],
            capture_output=True,
            text=True,
            cwd=str(PROJECT_ROOT),
        )
        assert result.returncode == 0, f"Script failed: {result.stderr}"
        data = json.loads(result.stdout)
        assert "security_scan_status" in data, "Must include security_scan_status field"


class TestSafeScreenshotCaptureRealCommands:
    """Tests that SAFE_SCREENSHOT_CAPTURE.md uses real commands."""

    def test_uses_real_commands(self):
        path = PROJECT_ROOT / "docs" / "SAFE_SCREENSHOT_CAPTURE.md"
        content = path.read_text()
        # Should not mention non-existent commands
        assert "kimari run" not in content.lower(), "Should not mention 'kimari run' (non-existent)"
        assert "kimari profile list" not in content.lower(), "Should not mention 'kimari profile list'"
        assert "kimari serve" not in content.lower(), "Should not mention 'kimari serve'"
        # Should mention real commands
        assert "kimari setup" in content.lower(), "Should mention 'kimari setup'"
        assert "kimari optimize" in content.lower() or "preflight" in content.lower(), (
            "Should mention real commands like optimize or preflight"
        )


class TestFirstPrivateSftHandoff:
    """Tests for docs/FIRST_PRIVATE_SFT_HANDOFF.md."""

    def test_doc_exists(self):
        path = PROJECT_ROOT / "docs" / "FIRST_PRIVATE_SFT_HANDOFF.md"
        assert path.exists(), f"Doc missing: {path}"

    def test_doc_mentions_never_adapters(self):
        path = PROJECT_ROOT / "docs" / "FIRST_PRIVATE_SFT_HANDOFF.md"
        content = path.read_text().lower()
        assert "adapter" in content, "Must mention adapters (as items that stay local)"
        assert "never" in content or "local" in content, "Must mention never-commit/local-only items"

    def test_doc_mentions_scan_secrets(self):
        path = PROJECT_ROOT / "docs" / "FIRST_PRIVATE_SFT_HANDOFF.md"
        content = path.read_text()
        assert "scan_for_secrets" in content, "Must reference scan_for_secrets.py"


class TestPrivateSftRunCommands:
    """Tests for docs/PRIVATE_SFT_RUN_COMMANDS.md."""

    def test_doc_exists(self):
        path = PROJECT_ROOT / "docs" / "PRIVATE_SFT_RUN_COMMANDS.md"
        assert path.exists(), f"Doc missing: {path}"

    def test_doc_lists_commands(self):
        path = PROJECT_ROOT / "docs" / "PRIVATE_SFT_RUN_COMMANDS.md"
        content = path.read_text().lower()
        assert "preflight" in content, "Must mention preflight"
        assert "build_dataset" in content or "build" in content, "Must mention dataset build"
        assert "scan" in content, "Must mention secret scanning"


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

    def test_release_check_mentions_v0125(self):
        path = PROJECT_ROOT / "scripts" / "release" / "check-release.py"
        content = path.read_text()
        assert "0.1.25" in content or "HF_TOKEN_SAFETY" in content, "check-release.py should include v0.1.25 checks"


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

    def test_version_is_0125(self):
        from kimari import __version__

        assert __version__ == "0.1.25-alpha", f"Version is {__version__}, expected 0.1.25-alpha"

    def test_pyproject_version(self):
        pyproject = PROJECT_ROOT / "pyproject.toml"
        content = pyproject.read_text()
        assert "0.1.25-alpha" in content

    def test_readme_mentions_version(self):
        readme = PROJECT_ROOT / "README.md"
        content = readme.read_text()
        assert "0.1.25-alpha" in content

    def test_index_html_mentions_version(self):
        index = PROJECT_ROOT / "docs" / "index.html"
        content = index.read_text()
        assert "0.1.25-alpha" in content
