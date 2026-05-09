"""
Smoke tests for the Kimari CLI interface.
Uses subprocess.run with capture_output=True to test the actual CLI.
"""

import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
CLI_PATH = PROJECT_ROOT / "cli" / "kimari_cli.py"


def _run_cli(*args: str) -> subprocess.CompletedProcess:
    """Run the kimari CLI with the given arguments and return the result."""
    cmd = [sys.executable, str(CLI_PATH)] + list(args)
    return subprocess.run(cmd, capture_output=True, text=True, timeout=30)


def test_cli_version():
    """--version outputs version string."""
    result = _run_cli("--version")
    assert result.returncode == 0
    assert "Kimari CLI" in result.stdout


def test_cli_profiles():
    """'profiles' command runs without error."""
    result = _run_cli("profiles")
    assert result.returncode == 0
    assert "gtx1060" in result.stdout or "GTX 1060" in result.stdout


def test_cli_pull_list():
    """'pull --list' runs without error."""
    result = _run_cli("pull", "--list")
    assert result.returncode == 0
    assert "test" in result.stdout or "TinyLlama" in result.stdout


def test_cli_start_dry_run_test():
    """'start --profile test --dry-run' runs."""
    result = _run_cli("start", "--profile", "test", "--dry-run")
    assert result.returncode == 0
    assert "DRY RUN" in result.stdout


def test_cli_start_dry_run_with_overrides():
    """'start --profile test --model models/x.gguf --host 0.0.0.0 --port 9999 --ctx 2048 --dry-run' runs."""
    result = _run_cli(
        "start", "--profile", "test",
        "--model", "models/x.gguf",
        "--host", "0.0.0.0",
        "--port", "9999",
        "--ctx", "2048",
        "--dry-run"
    )
    assert result.returncode == 0
    assert "DRY RUN" in result.stdout
    assert "0.0.0.0" in result.stdout
    assert "9999" in result.stdout
    assert "2048" in result.stdout


def test_cli_doctor():
    """'doctor' runs (may have warnings, that's ok)."""
    result = _run_cli("doctor")
    # Doctor may exit with 1 if there are failures (like no GPU),
    # but it should not crash with an unhandled exception
    assert result.returncode in (0, 1)
    # Should contain diagnostic output
    output = result.stdout + result.stderr
    assert "OS" in output or "System Diagnostics" in output
