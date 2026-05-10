"""Smoke tests for the Kimari CLI interface.

Uses subprocess.run with capture_output=True to test the actual CLI.
"""

import json
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
CLI_PATH = PROJECT_ROOT / "cli" / "kimari_cli.py"


def _run_cli(*args: str) -> subprocess.CompletedProcess:
    """Run the kimari CLI with the given arguments and return the result."""
    cmd = [sys.executable, str(CLI_PATH), *list(args)]
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


def test_cli_profiles_json():
    """'profiles --json' outputs valid JSON."""
    result = _run_cli("profiles", "--json")
    assert result.returncode == 0
    data = json.loads(result.stdout)
    assert "profiles" in data


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
        "start",
        "--profile",
        "test",
        "--model",
        "models/x.gguf",
        "--host",
        "0.0.0.0",
        "--port",
        "9999",
        "--ctx",
        "2048",
        "--dry-run",
    )
    assert result.returncode == 0
    assert "DRY RUN" in result.stdout
    assert "0.0.0.0" in result.stdout
    assert "9999" in result.stdout
    assert "2048" in result.stdout


def test_cli_doctor():
    """'doctor' runs (may have warnings, that's ok)."""
    result = _run_cli("doctor")
    assert result.returncode in (0, 1)
    output = result.stdout + result.stderr
    assert "OS" in output or "System Diagnostics" in output


def test_cli_doctor_json():
    """'doctor --json' outputs valid JSON."""
    result = _run_cli("doctor", "--json")
    assert result.returncode in (0, 1)
    data = json.loads(result.stdout)
    assert "checks" in data
    assert "summary" in data


def test_cli_info():
    """'info' command runs and shows version."""
    result = _run_cli("info")
    assert result.returncode == 0
    assert "0.1.13-alpha" in result.stdout


def test_cli_info_json():
    """'info --json' outputs valid JSON."""
    result = _run_cli("info", "--json")
    assert result.returncode == 0
    data = json.loads(result.stdout)
    assert data["kimari_version"] == "0.1.13-alpha"


def test_cli_config_path():
    """'config path' outputs config file path."""
    result = _run_cli("config", "path")
    assert result.returncode == 0
    assert "kimari.profiles.json" in result.stdout


def test_cli_config_validate():
    """'config validate' runs successfully."""
    result = _run_cli("config", "validate")
    assert result.returncode == 0
    assert "valid" in result.stdout.lower()


def test_cli_config_show():
    """'config show' runs and shows config."""
    result = _run_cli("config", "show")
    assert result.returncode == 0
    assert "Kimari Configuration" in result.stdout or "gtx1060" in result.stdout


def test_cli_models():
    """'models' command runs."""
    result = _run_cli("models")
    assert result.returncode == 0


def test_cli_models_json():
    """'models --json' runs."""
    result = _run_cli("models", "--json")
    assert result.returncode == 0
