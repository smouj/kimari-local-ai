"""Tests for v0.1.36-alpha: smoke gate path fix, submit preflight hardening."""

import json
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
HF_SCRIPT = PROJECT_ROOT / "training" / "scripts" / "hf_jobs_micro_sft.py"
CONFIG = PROJECT_ROOT / "training" / "configs" / "hf_jobs_kimari4b_micro_sft.v0.yaml"


def _make_valid_smoke_summary(path: Path) -> None:
    """Create a valid smoke summary JSON file."""
    path.write_text(json.dumps({"status": "completed", "gate_state": "BLOCKED"}))


def _make_invalid_smoke_summary(path: Path) -> None:
    """Create an invalid smoke summary JSON file."""
    path.write_text(json.dumps({"status": "failed", "gate_state": "BLOCKED"}))


class TestResolveSmokeGate:
    """Test the resolve_smoke_gate function."""

    def test_explicit_valid_smoke_summary_passes_without_tmp(self, tmp_path):
        """Explicit valid smoke summary passes even if /tmp file doesn't exist."""
        smoke_file = tmp_path / "smoke.json"
        _make_valid_smoke_summary(smoke_file)
        result = subprocess.run(
            [
                sys.executable,
                str(HF_SCRIPT),
                "--config",
                str(CONFIG),
                "--require-smoke-summary",
                str(smoke_file),
                "--dry-run",
                "--json",
            ],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert data.get("smoke_gate_validated") is True
        assert data.get("smoke_gate_source") == "explicit"

    def test_explicit_invalid_smoke_summary_fails(self, tmp_path):
        """Explicit invalid smoke summary fails."""
        smoke_file = tmp_path / "smoke.json"
        _make_invalid_smoke_summary(smoke_file)
        result = subprocess.run(
            [
                sys.executable,
                str(HF_SCRIPT),
                "--config",
                str(CONFIG),
                "--require-smoke-summary",
                str(smoke_file),
                "--dry-run",
                "--json",
            ],
            capture_output=True,
            text=True,
        )
        # dry-run should still pass but report validation failure
        data = json.loads(result.stdout)
        assert data.get("smoke_gate_validated") is False

    def test_fallback_tmp_valid_summary_passes(self):
        """Fallback /tmp valid summary passes when no explicit path given."""
        # This test uses /tmp which may or may not have the file
        # We create it temporarily
        tmp_path = Path("/tmp/hf_jobs_smoke_summary.json")
        original = None
        if tmp_path.exists():
            original = tmp_path.read_text()
        try:
            _make_valid_smoke_summary(tmp_path)
            result = subprocess.run(
                [sys.executable, str(HF_SCRIPT), "--config", str(CONFIG), "--dry-run", "--json"],
                capture_output=True,
                text=True,
            )
            assert result.returncode == 0
            data = json.loads(result.stdout)
            assert data.get("smoke_gate_validated") is True
            assert data.get("smoke_gate_source") == "default_tmp"
        finally:
            if original is not None:
                tmp_path.write_text(original)
            elif tmp_path.exists():
                tmp_path.unlink()

    def test_override_passes_with_warning(self):
        """Override passes with warning."""
        result = subprocess.run(
            [sys.executable, str(HF_SCRIPT), "--config", str(CONFIG), "--override-smoke-gate", "--dry-run", "--json"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert data.get("smoke_gate_validated") is True
        assert data.get("smoke_gate_source") == "override"

    def test_dry_run_does_not_require_smoke(self):
        """Dry-run mode works without any smoke summary."""
        # Remove /tmp file if it exists temporarily
        tmp_path = Path("/tmp/hf_jobs_smoke_summary.json")
        original = None
        if tmp_path.exists():
            original = tmp_path.read_text()
            tmp_path.unlink()
        try:
            result = subprocess.run(
                [sys.executable, str(HF_SCRIPT), "--config", str(CONFIG), "--dry-run", "--json"],
                capture_output=True,
                text=True,
            )
            assert result.returncode == 0
        finally:
            if original is not None:
                tmp_path.write_text(original)

    def test_print_command_does_not_require_smoke(self):
        """Print-command mode works without any smoke summary."""
        tmp_path = Path("/tmp/hf_jobs_smoke_summary.json")
        original = None
        if tmp_path.exists():
            original = tmp_path.read_text()
            tmp_path.unlink()
        try:
            result = subprocess.run(
                [sys.executable, str(HF_SCRIPT), "--config", str(CONFIG), "--print-command", "--json"],
                capture_output=True,
                text=True,
            )
            assert result.returncode == 0
        finally:
            if original is not None:
                tmp_path.write_text(original)

    def test_submit_without_valid_smoke_blocks(self, tmp_path):
        """Submit without valid smoke summary is blocked."""
        # No smoke summary, no override → should be blocked
        result = subprocess.run(
            [sys.executable, str(HF_SCRIPT), "--config", str(CONFIG), "--allow-submit", "--yes", "--json"],
            capture_output=True,
            text=True,
        )
        assert result.returncode != 0

    def test_json_contains_smoke_gate_source(self, tmp_path):
        """JSON output contains smoke_gate_source field."""
        smoke_file = tmp_path / "smoke.json"
        _make_valid_smoke_summary(smoke_file)
        result = subprocess.run(
            [
                sys.executable,
                str(HF_SCRIPT),
                "--config",
                str(CONFIG),
                "--require-smoke-summary",
                str(smoke_file),
                "--dry-run",
                "--json",
            ],
            capture_output=True,
            text=True,
        )
        data = json.loads(result.stdout)
        assert "smoke_gate_source" in data
        assert "smoke_gate_validated" in data
        assert "smoke_gate_message" in data
        assert "smoke_summary_path" in data


class TestReleaseCheckV0136:
    """Test that release check passes for v0.1.36."""

    def test_release_check_passes(self):
        """Run check-release.py and verify no failures."""
        result = subprocess.run(
            [sys.executable, str(PROJECT_ROOT / "scripts" / "release" / "check-release.py")],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, f"Release check failed:\n{result.stdout}\n{result.stderr}"
