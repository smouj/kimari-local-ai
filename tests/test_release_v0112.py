"""Tests for v0.1.12-alpha: Packaged defaults, user paths, short flag support, config resolution chain, state/tokens in user dirs, release checks."""

import json
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def _run_kimari(*args: str) -> subprocess.CompletedProcess:
    """Run kimari CLI via python -m."""
    cmd = [sys.executable, "-m", "kimari.cli.main", *list(args)]
    return subprocess.run(cmd, capture_output=True, text=True, timeout=30)


# --- Version consistency tests ---


def test_version_is_0112():
    """kimari/__init__.py version is '0.1.12-alpha'."""
    from kimari import __version__

    assert __version__ == "0.1.12-alpha"


def test_pyproject_version_matches():
    """pyproject.toml version matches __init__.py."""
    from kimari import __version__

    pyproject_path = PROJECT_ROOT / "pyproject.toml"
    content = pyproject_path.read_text()
    for line in content.splitlines():
        if line.startswith("version ="):
            pyproject_version = line.split("=")[1].strip().strip('"')
            assert pyproject_version == __version__
            return
    raise AssertionError("version line not found in pyproject.toml")


def test_cli_info_version():
    """kimari info --json shows '0.1.12-alpha'."""
    result = _run_kimari("info", "--json")
    assert result.returncode == 0
    data = json.loads(result.stdout)
    assert data["kimari_version"] == "0.1.12-alpha"


# --- Packaged defaults tests ---


def test_defaults_directory_exists():
    """kimari/defaults/ directory exists."""
    assert (PROJECT_ROOT / "kimari" / "defaults").is_dir()


def test_defaults_profiles_json_exists():
    """kimari/defaults/kimari.profiles.json exists and is valid."""
    path = PROJECT_ROOT / "kimari" / "defaults" / "kimari.profiles.json"
    assert path.exists()
    data = json.loads(path.read_text())
    assert "profiles" in data
    assert data.get("default_profile") == "test"


def test_defaults_schema_json_exists():
    """kimari/defaults/kimari.profiles.schema.json exists and is valid."""
    path = PROJECT_ROOT / "kimari" / "defaults" / "kimari.profiles.schema.json"
    assert path.exists()
    data = json.loads(path.read_text())
    assert "type" in data


def test_defaults_models_json_exists():
    """kimari/defaults/kimari.models.json exists and is valid."""
    path = PROJECT_ROOT / "kimari" / "defaults" / "kimari.models.json"
    assert path.exists()
    data = json.loads(path.read_text())
    assert "models" in data


def test_defaults_match_config():
    """Packaged defaults match repo config files."""
    for name in ("kimari.profiles.json", "kimari.models.json", "kimari.profiles.schema.json"):
        defaults_path = PROJECT_ROOT / "kimari" / "defaults" / name
        config_path = PROJECT_ROOT / "config" / name
        if defaults_path.exists() and config_path.exists():
            defaults_data = json.loads(defaults_path.read_text())
            config_data = json.loads(config_path.read_text())
            assert defaults_data == config_data, f"{name} defaults don't match config"


# --- Paths module tests ---


def test_paths_module_key_functions():
    """kimari.core.paths exposes key functions that return Path objects."""
    from kimari.core.paths import get_kimari_home, get_user_config_dir, get_user_state_dir

    assert isinstance(get_kimari_home(), Path)
    assert isinstance(get_user_config_dir(), Path)
    assert isinstance(get_user_state_dir(), Path)


def test_kimari_home_override(tmp_path, monkeypatch):
    """KIMARI_HOME override works for all path functions."""
    home_dir = tmp_path / "kimari-home"
    monkeypatch.setenv("KIMARI_HOME", str(home_dir))

    import importlib

    from kimari.core import paths as paths_mod

    importlib.reload(paths_mod)

    assert paths_mod.get_kimari_home() == home_dir
    assert paths_mod.get_user_config_dir() == home_dir
    assert paths_mod.get_user_state_dir() == home_dir / "state"
    assert paths_mod.get_user_cache_dir() == home_dir / "cache"
    assert paths_mod.get_user_models_dir() == home_dir / "models"


def test_kimari_config_dir_override(tmp_path, monkeypatch):
    """KIMARI_CONFIG_DIR override works."""
    import importlib

    config_dir = tmp_path / "custom-config"
    monkeypatch.setenv("KIMARI_CONFIG_DIR", str(config_dir))
    from kimari.core import paths as paths_mod

    importlib.reload(paths_mod)
    assert paths_mod.get_user_config_dir() == config_dir


def test_kimari_state_dir_override(tmp_path, monkeypatch):
    """KIMARI_STATE_DIR override works."""
    import importlib

    state_dir = tmp_path / "custom-state"
    monkeypatch.setenv("KIMARI_STATE_DIR", str(state_dir))
    from kimari.core import paths as paths_mod

    importlib.reload(paths_mod)
    assert paths_mod.get_user_state_dir() == state_dir


def test_defaults_dir_points_to_package():
    """get_defaults_dir() points to kimari/defaults/ inside the package."""
    from kimari.core.paths import get_defaults_dir

    defaults_dir = get_defaults_dir()
    assert defaults_dir.name == "defaults"
    assert (defaults_dir / "kimari.profiles.json").exists()


# --- Config resolution tests ---


def test_config_path_command():
    """kimari config path returns a valid path."""
    result = _run_kimari("config", "path")
    assert result.returncode == 0
    path = result.stdout.strip()
    assert "kimari.profiles.json" in path


def test_load_config_no_repo_root_dependency(tmp_path, monkeypatch):
    """load_config works even without repo-root config/ (uses packaged defaults)."""
    import importlib

    monkeypatch.setenv("KIMARI_HOME", str(tmp_path / "kimari-test"))
    import kimari.config.loader as loader_mod
    import kimari.core.paths as paths_mod

    importlib.reload(paths_mod)
    importlib.reload(loader_mod)

    config = loader_mod.load_config()
    assert "profiles" in config
    assert config.get("default_profile") == "test"


# --- Short flag parsing tests ---


def test_parse_supported_flags_short_and_long():
    """Parse help text with both short and long flags."""
    from kimari.runtime.llama_flags import parse_supported_flags

    help_text = """usage: llama-server [options]

options:
  -m FNAME, --model FNAME       Model path
  -c N, --ctx-size N            Context size
  -ngl N, --n-gpu-layers N     GPU layers
  -b N, --batch-size N          Batch size
  -ub N, --ubatch-size N        Micro batch size
  -t N, --threads N             Threads
  --flash-attn                  Flash attention
  --parallel N                  Parallel sequences
  --mlock                       Lock memory
"""
    flags = parse_supported_flags(help_text)
    # Long flags
    assert "--model" in flags
    assert "--ctx-size" in flags
    assert "--n-gpu-layers" in flags
    assert "--batch-size" in flags
    assert "--ubatch-size" in flags
    assert "--threads" in flags
    assert "--flash-attn" in flags
    assert "--parallel" in flags
    assert "--mlock" in flags
    # Short flags (via alias)
    assert "-m" in flags
    assert "-c" in flags
    assert "-ngl" in flags
    assert "-b" in flags
    assert "-ub" in flags
    assert "-t" in flags


def test_supports_flag_with_alias():
    """supports_flag recognizes both short and long forms."""
    from kimari.runtime.llama_flags import parse_supported_flags, supports_flag

    help_text = "-m FNAME, --model FNAME\n-c N, --ctx-size N\n"
    flags = parse_supported_flags(help_text)
    assert supports_flag("-m", flags)
    assert supports_flag("-c", flags)
    assert supports_flag("--model", flags)
    assert supports_flag("--ctx-size", flags)


def test_strict_flags_no_false_positive_with_base_cmd():
    """strict-flags does not flag base command flags as unsupported."""
    from kimari.runtime.llama_flags import filter_unsupported_flags, parse_supported_flags

    help_text = """-m FNAME, --model FNAME
-c N, --ctx-size N
-ngl N, --n-gpu-layers N
-b N, --batch-size N
-ub N, --ubatch-size N
-t N, --threads N
--host ADDR
--port PORT
--cache-type-k TYPE
--cache-type-v TYPE
"""
    flags = parse_supported_flags(help_text)
    cmd = [
        "llama-server",
        "-m", "model.gguf",
        "--host", "127.0.0.1",
        "--port", "11435",
        "-ngl", "all",
        "-c", "4096",
        "-b", "128",
        "-ub", "64",
        "--cache-type-k", "f16",
        "--cache-type-v", "f16",
        "-t", "4",
    ]
    _, unsupported = filter_unsupported_flags(cmd, flags)
    assert unsupported == [], f"False positive unsupported flags: {unsupported}"


def test_strict_flags_catches_unknown():
    """strict-flags correctly flags unknown flags."""
    from kimari.runtime.llama_flags import filter_unsupported_flags, parse_supported_flags

    help_text = "-m FNAME, --model FNAME\n"
    flags = parse_supported_flags(help_text)
    cmd = ["llama-server", "-m", "model.gguf", "--flash-attn"]
    _, unsupported = filter_unsupported_flags(cmd, flags)
    assert "--flash-attn" in unsupported


# --- Token tests (with KIMARI_STATE_DIR override) ---


def test_token_create_with_state_dir(tmp_path, monkeypatch):
    """Token CRUD works with KIMARI_STATE_DIR override."""
    import importlib

    monkeypatch.setenv("KIMARI_STATE_DIR", str(tmp_path / "state"))
    import kimari.core.paths as paths_mod

    importlib.reload(paths_mod)
    from kimari.security import tokens as tokens_mod

    importlib.reload(tokens_mod)

    result = tokens_mod.create_token()
    assert result["token"], "Token should be non-empty"
    assert "created_at" in result
    assert result["preview"].endswith("...")

    shown = tokens_mod.show_token()
    assert shown is not None
    assert shown["token"] == result["token"]

    assert tokens_mod.delete_token() is True
    assert tokens_mod.show_token() is None


# --- State tests (with KIMARI_STATE_DIR override) ---


def test_state_with_user_dir(tmp_path, monkeypatch):
    """State management works with user state directory."""
    import importlib

    monkeypatch.setenv("KIMARI_STATE_DIR", str(tmp_path / "state"))
    import kimari.core.paths as paths_mod
    import kimari.core.state as state_mod

    importlib.reload(paths_mod)
    importlib.reload(state_mod)

    state_mod.write_state("READY", pid=12345, profile="test")
    state = state_mod.read_state()
    assert state is not None
    assert state["status"] == "READY"
    assert state["pid"] == 12345
    state_mod.clear_state()
    assert state_mod.read_state() is None


# --- File existence tests ---


def test_defaults_init_exists():
    """kimari/defaults/__init__.py exists."""
    assert (PROJECT_ROOT / "kimari" / "defaults" / "__init__.py").exists()


def test_paths_module_exists():
    """kimari/core/paths.py exists."""
    assert (PROJECT_ROOT / "kimari" / "core" / "paths.py").exists()


# --- Release check test ---


def test_release_check_passes():
    """scripts/release/check-release.py exits with code 0."""
    result = subprocess.run(
        [sys.executable, "scripts/release/check-release.py"],
        capture_output=True,
        text=True,
        cwd=str(PROJECT_ROOT),
    )
    assert result.returncode == 0, f"check-release.py failed:\n{result.stdout}\n{result.stderr}"


# --- Default profile test ---


def test_default_profile_still_test():
    """default_profile is still 'test'."""
    from kimari.config.loader import load_config

    config = load_config()
    assert config["default_profile"] == "test"


# --- No false claims ---


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


# --- pyproject.toml package-data ---


def test_pyproject_includes_defaults():
    """pyproject.toml package-data includes defaults/*.json."""
    content = (PROJECT_ROOT / "pyproject.toml").read_text()
    assert "defaults" in content, "defaults/*.json not found in pyproject.toml package-data"
