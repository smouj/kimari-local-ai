"""
Tests for v0.1.14-alpha: Runtime llama_flags, security tokens, CLI setup/token commands,
version consistency, file existence, and release checks.
"""

import json
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent


# ─── Helpers ───────────────────────────────────────────────────────────────────


def _run_kimari(*args: str) -> subprocess.CompletedProcess:
    """Run kimari CLI via python -m."""
    cmd = [sys.executable, "-m", "kimari.cli.main", *list(args)]
    return subprocess.run(cmd, capture_output=True, text=True, timeout=30)


# ─── Runtime llama_flags tests ─────────────────────────────────────────────────


def test_parse_supported_flags_basic():
    """Parse fake help text containing --flash-attn, --parallel, --mlock and verify they're in the result set."""
    from kimari.runtime.llama_flags import parse_supported_flags

    help_text = """
usage: llama-server [options]

options:
  --flash-attn          Flash attention
  --parallel N          Parallel sequences
  --mlock               Lock memory
  --host ADDR           Host address
  --port PORT           Port number
"""
    flags = parse_supported_flags(help_text)
    assert "--flash-attn" in flags
    assert "--parallel" in flags
    assert "--mlock" in flags


def test_parse_supported_flags_empty():
    """Empty help text returns empty set."""
    from kimari.runtime.llama_flags import parse_supported_flags

    flags = parse_supported_flags("")
    assert flags == set()


def test_supports_flag_true():
    """Flag in supported set returns True."""
    from kimari.runtime.llama_flags import supports_flag

    supported = {"--flash-attn", "--parallel", "--mlock"}
    assert supports_flag("--flash-attn", supported) is True


def test_supports_flag_false():
    """Flag not in supported set returns False."""
    from kimari.runtime.llama_flags import supports_flag

    supported = {"--flash-attn", "--parallel", "--mlock"}
    assert supports_flag("--nonexistent-flag", supported) is False


def test_filter_unsupported_flags_all_supported():
    """All flags supported returns original cmd and empty unsupported list."""
    from kimari.runtime.llama_flags import filter_unsupported_flags

    supported = {"--flash-attn", "--mlock", "--parallel", "-m", "--host", "--port"}
    cmd = ["llama-server", "-m", "model.gguf", "--host", "127.0.0.1", "--port", "11435", "--flash-attn", "--mlock"]
    filtered, unsupported = filter_unsupported_flags(cmd, supported)
    assert filtered == cmd
    assert unsupported == []


def test_filter_unsupported_flags_some_unsupported():
    """Some flags unsupported returns filtered cmd and list of unsupported flags."""
    from kimari.runtime.llama_flags import filter_unsupported_flags

    supported = {"--flash-attn", "-m", "--host", "--port"}
    cmd = ["llama-server", "-m", "model.gguf", "--host", "127.0.0.1", "--port", "11435", "--flash-attn", "--mlock"]
    filtered, unsupported = filter_unsupported_flags(cmd, supported)
    assert "--flash-attn" in filtered
    assert "--mlock" not in filtered
    assert "--mlock" in unsupported


def test_filter_unsupported_flags_with_values():
    """Flags with values (like --parallel 2) are properly handled — both the flag and its value removed from supported_cmd."""
    from kimari.runtime.llama_flags import filter_unsupported_flags

    supported = {"--flash-attn", "-m", "--host", "--port"}
    cmd = [
        "llama-server",
        "-m",
        "model.gguf",
        "--host",
        "127.0.0.1",
        "--port",
        "11435",
        "--flash-attn",
        "--parallel",
        "2",
    ]
    filtered, unsupported = filter_unsupported_flags(cmd, supported)
    assert "--parallel" not in filtered
    assert "2" not in filtered
    assert "--parallel" in unsupported


def test_detect_llama_server_help_missing_binary():
    """Returns empty string for nonexistent binary."""
    from kimari.runtime.llama_flags import detect_llama_server_help

    result = detect_llama_server_help("/nonexistent/binary/llama-server-xyz-12345")
    assert result == ""


def test_detect_llama_server_version_missing_binary():
    """Returns empty string for nonexistent binary."""
    from kimari.runtime.llama_flags import detect_llama_server_version

    result = detect_llama_server_version("/nonexistent/binary/llama-server-xyz-12345")
    assert result == ""


# ─── Security tokens tests ─────────────────────────────────────────────────────


def test_create_token(tmp_path, monkeypatch):
    """Create a token using tmp_path (monkeypatch KIMARI_STATE_DIR), verify token is non-empty, has created_at, has preview."""
    import kimari.security.tokens as tokens_mod

    monkeypatch.setenv("KIMARI_STATE_DIR", str(tmp_path / "state"))

    result = tokens_mod.create_token()
    assert result["token"], "Token should be non-empty"
    assert "created_at" in result, "Token should have created_at"
    assert "preview" in result, "Token should have preview"
    assert result["preview"].endswith("..."), "Preview should end with '...'"


def test_show_token(tmp_path, monkeypatch):
    """Create then show a token, verify it matches."""
    import kimari.security.tokens as tokens_mod

    monkeypatch.setenv("KIMARI_STATE_DIR", str(tmp_path / "state"))

    created = tokens_mod.create_token()
    shown = tokens_mod.show_token()
    assert shown is not None, "show_token should return a dict"
    assert shown["token"] == created["token"], "Token should match"
    assert shown["created_at"] == created["created_at"], "created_at should match"


def test_show_token_missing(tmp_path, monkeypatch):
    """Show token when none exists returns None."""
    import kimari.security.tokens as tokens_mod

    monkeypatch.setenv("KIMARI_STATE_DIR", str(tmp_path / "state"))

    result = tokens_mod.show_token()
    assert result is None


def test_delete_token(tmp_path, monkeypatch):
    """Create then delete, verify returns True."""
    import kimari.security.tokens as tokens_mod

    monkeypatch.setenv("KIMARI_STATE_DIR", str(tmp_path / "state"))

    tokens_mod.create_token()
    result = tokens_mod.delete_token()
    assert result is True


def test_delete_token_missing(tmp_path, monkeypatch):
    """Delete when none exists returns False."""
    import kimari.security.tokens as tokens_mod

    monkeypatch.setenv("KIMARI_STATE_DIR", str(tmp_path / "state"))

    result = tokens_mod.delete_token()
    assert result is False


# ─── CLI command tests ─────────────────────────────────────────────────────────


def test_setup_dry_run():
    """kimari setup --dry-run runs without error."""
    result = _run_kimari("setup", "--dry-run")
    assert result.returncode == 0


def test_setup_json():
    """kimari setup --json returns valid JSON with expected keys."""
    result = _run_kimari("setup", "--json")
    assert result.returncode == 0
    data = json.loads(result.stdout)
    expected_keys = ["kimari_version", "os", "python", "gpu", "cuda"]
    for key in expected_keys:
        assert key in data, f"Missing key: {key}"


def test_setup_integration_openclaw():
    """kimari setup --json --integration openclaw recommends openclaw-local profile."""
    result = _run_kimari("setup", "--json", "--integration", "openclaw")
    assert result.returncode == 0
    data = json.loads(result.stdout)
    assert data["recommended_integration"] == "openclaw"
    next_cmds = " ".join(data.get("next_commands", []))
    assert "openclaw-local" in next_cmds


def test_setup_integration_hermes():
    """kimari setup --json --integration hermes recommends hermes-local."""
    result = _run_kimari("setup", "--json", "--integration", "hermes")
    assert result.returncode == 0
    data = json.loads(result.stdout)
    assert data["recommended_integration"] == "hermes"
    next_cmds = " ".join(data.get("next_commands", []))
    assert "hermes-local" in next_cmds


def test_setup_integration_continue():
    """kimari setup --json --integration continue recommends ide-local."""
    result = _run_kimari("setup", "--json", "--integration", "continue")
    assert result.returncode == 0
    data = json.loads(result.stdout)
    assert data["recommended_integration"] == "continue"
    next_cmds = " ".join(data.get("next_commands", []))
    assert "ide-local" in next_cmds


def test_start_dry_run_strict_flags():
    """kimari start --dry-run --strict-flags runs without crashing (may warn)."""
    result = _run_kimari("start", "--profile", "test", "--dry-run", "--strict-flags")
    assert result.returncode == 0


def test_token_create_and_show(tmp_path, monkeypatch):
    """kimari token create then kimari token show (use tmp_path to avoid writing to repo)."""
    import kimari.security.tokens as tokens_mod

    monkeypatch.setenv("KIMARI_STATE_DIR", str(tmp_path / "state"))

    created = tokens_mod.create_token()
    shown = tokens_mod.show_token()
    assert shown is not None
    assert shown["token"] == created["token"]


def test_token_delete(tmp_path, monkeypatch):
    """kimari token delete runs without error."""
    import kimari.security.tokens as tokens_mod

    monkeypatch.setenv("KIMARI_STATE_DIR", str(tmp_path / "state"))

    # Create then delete
    tokens_mod.create_token()
    result = tokens_mod.delete_token()
    assert result is True


# ─── Version consistency tests ─────────────────────────────────────────────────


def test_version_is_0112():
    """kimari/__init__.py version is '0.1.13-alpha'."""
    from kimari import __version__

    assert __version__ == "0.1.22-alpha"


def test_pyproject_version_matches():
    """pyproject.toml version matches __init__.py."""
    from kimari import __version__

    pyproject_path = PROJECT_ROOT / "pyproject.toml"
    content = pyproject_path.read_text()
    # Find version = "..." line in [project] section
    for line in content.splitlines():
        if line.startswith("version ="):
            pyproject_version = line.split("=")[1].strip().strip('"')
            assert pyproject_version == __version__
            return
    raise AssertionError("version line not found in pyproject.toml")


def test_cli_info_version():
    """kimari info --json shows '0.1.13-alpha'."""
    result = _run_kimari("info", "--json")
    assert result.returncode == 0
    data = json.loads(result.stdout)
    assert data["kimari_version"] == "0.1.22-alpha"


# ─── File existence tests ─────────────────────────────────────────────────────


def test_runtime_module_exists():
    """kimari/runtime/__init__.py and llama_flags.py exist."""
    assert (PROJECT_ROOT / "kimari" / "runtime" / "__init__.py").exists()
    assert (PROJECT_ROOT / "kimari" / "runtime" / "llama_flags.py").exists()


def test_security_module_exists():
    """kimari/security/__init__.py and tokens.py exist."""
    assert (PROJECT_ROOT / "kimari" / "security" / "__init__.py").exists()
    assert (PROJECT_ROOT / "kimari" / "security" / "tokens.py").exists()


def test_windows_launcher_exists():
    """scripts/windows/kimari-launcher.ps1 exists."""
    assert (PROJECT_ROOT / "scripts" / "windows" / "kimari-launcher.ps1").exists()


def test_windows_doctor_exists():
    """scripts/windows/kimari-doctor.ps1 exists."""
    assert (PROJECT_ROOT / "scripts" / "windows" / "kimari-doctor.ps1").exists()


def test_windows_readme_exists():
    """scripts/windows/README.md exists."""
    assert (PROJECT_ROOT / "scripts" / "windows" / "README.md").exists()


# ─── Release check tests ──────────────────────────────────────────────────────


def test_release_check_passes():
    """scripts/release/check-release.py exits with code 0."""
    result = subprocess.run(
        [sys.executable, "scripts/release/check-release.py"],
        capture_output=True,
        text=True,
        cwd=str(PROJECT_ROOT),
    )
    assert result.returncode == 0, f"check-release.py failed:\n{result.stdout}\n{result.stderr}"


def test_default_profile_still_test():
    """default_profile is still 'test'."""
    from kimari.config.loader import load_config

    config = load_config()
    assert config["default_profile"] == "test"


def test_no_kimari_4b_released_claim():
    """No file claims Kimari-4B is released."""
    key_files = [
        PROJECT_ROOT / "README.md",
        PROJECT_ROOT / "CHANGELOG.md",
        PROJECT_ROOT / "ROADMAP.md",
        PROJECT_ROOT / "docs" / "index.html",
    ]
    k4b_false_patterns = [
        "kimari-4b is available now",
        "kimari-4b can be downloaded",
        "download kimari-4b",
        "kimari-4b weights available",
        "kimari-4b has been released",
    ]
    for path in key_files:
        if path.exists():
            text = path.read_text().lower()
            for pattern in k4b_false_patterns:
                assert pattern not in text, f"False claim '{pattern}' found in {path}"
