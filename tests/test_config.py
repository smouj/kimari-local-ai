"""Tests for Kimari config loading and validation."""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from kimari.config.loader import get_config_path, validate_config  # noqa: E402


def test_load_config_exists(sample_config):
    """Config loads successfully (is a dict and non-empty)."""
    assert isinstance(sample_config, dict)
    assert len(sample_config) > 0


def test_load_config_has_profiles(sample_config):
    """Config has a 'profiles' dict."""
    assert "profiles" in sample_config
    assert isinstance(sample_config["profiles"], dict)


def test_load_config_has_default_profile(sample_config):
    """Config has a 'default_profile' key."""
    assert "default_profile" in sample_config
    assert isinstance(sample_config["default_profile"], str)
    assert len(sample_config["default_profile"]) > 0


def test_default_profile_exists_in_profiles(sample_config):
    """The default_profile key exists in the profiles dict."""
    default = sample_config["default_profile"]
    assert default in sample_config["profiles"]


def test_all_profiles_have_required_fields(sample_config):
    """Every profile has name, model, ctx, batch, ubatch, host, port, gpu_layers, quantization."""
    required_fields = {"name", "model", "ctx", "batch", "ubatch", "host", "port", "gpu_layers", "quantization"}
    for profile_name, profile in sample_config["profiles"].items():
        missing = required_fields - set(profile.keys())
        assert not missing, f"Profile '{profile_name}' is missing fields: {missing}"


def test_profile_model_paths_relative(sample_config):
    """All model paths are relative (start with 'models/')."""
    for profile_name, profile in sample_config["profiles"].items():
        model_path = profile["model"]
        assert model_path.startswith("models/"), (
            f"Profile '{profile_name}' model path '{model_path}' does not start with 'models/'"
        )


def test_port_ranges_valid(sample_config):
    """All ports are in valid range 1024-65535."""
    for profile_name, profile in sample_config["profiles"].items():
        port = profile["port"]
        assert 1024 <= port <= 65535, f"Profile '{profile_name}' has invalid port: {port}"


def test_config_has_config_version(sample_config):
    """Config has config_version field (v2+)."""
    assert "config_version" in sample_config
    assert isinstance(sample_config["config_version"], int)
    assert sample_config["config_version"] >= 2


def test_validate_config_passes(sample_config):
    """validate_config returns no errors for the current config."""
    is_valid, errors = validate_config(sample_config)
    assert is_valid, f"Config validation failed: {errors}"


def test_get_config_path():
    """get_config_path returns an absolute path that exists."""
    path = get_config_path()
    assert path.is_absolute()
    assert path.exists()


def test_validate_config_catches_missing_default():
    """validate_config catches missing default_profile."""
    bad_config = {
        "version": "1.0.0",
        "config_version": 2,
        "default_profile": "nonexistent",
        "server": {
            "health_endpoint": "/health",
            "chat_endpoint": "/v1/chat/completions",
            "models_endpoint": "/v1/models",
        },
        "profiles": {
            "test": {
                "name": "Test",
                "model": "models/test.gguf",
                "ctx": 4096,
                "batch": 128,
                "ubatch": 64,
                "host": "127.0.0.1",
                "port": 11435,
                "gpu_layers": "all",
                "quantization": "Q4_K_M",
            }
        },
    }
    is_valid, errors = validate_config(bad_config)
    assert not is_valid
    assert any("default_profile" in e for e in errors)


def test_migrate_config_current_no_changes():
    """migrate_config returns no changes when config is already current."""
    from kimari.config.loader import migrate_config

    changed, info = migrate_config(dry_run=True)
    assert changed is False
    assert "already up to date" in info.get("message", "").lower() or info.get("changes") == []


def test_validate_config_catches_0000_host():
    """validate_config catches 0.0.0.0 on non-docker profile."""
    bad_config = {
        "version": "1.0.0",
        "config_version": 2,
        "default_profile": "test",
        "server": {
            "health_endpoint": "/health",
            "chat_endpoint": "/v1/chat/completions",
            "models_endpoint": "/v1/models",
        },
        "profiles": {
            "test": {
                "name": "Test",
                "model": "models/test.gguf",
                "ctx": 4096,
                "batch": 128,
                "ubatch": 64,
                "host": "0.0.0.0",
                "port": 11435,
                "gpu_layers": "all",
                "quantization": "Q4_K_M",
            }
        },
    }
    is_valid, errors = validate_config(bad_config)
    assert not is_valid
    assert any("0.0.0.0" in e for e in errors)


def test_validate_config_catches_absolute_path():
    """validate_config catches absolute model paths."""
    bad_config = {
        "version": "1.0.0",
        "config_version": 2,
        "default_profile": "test",
        "server": {
            "health_endpoint": "/health",
            "chat_endpoint": "/v1/chat/completions",
            "models_endpoint": "/v1/models",
        },
        "profiles": {
            "test": {
                "name": "Test",
                "model": "/absolute/path/model.gguf",
                "ctx": 4096,
                "batch": 128,
                "ubatch": 64,
                "host": "127.0.0.1",
                "port": 11435,
                "gpu_layers": "all",
                "quantization": "Q4_K_M",
            }
        },
    }
    is_valid, errors = validate_config(bad_config)
    assert not is_valid
    assert any("absolute" in e.lower() for e in errors)


def test_validate_config_catches_invalid_port():
    """validate_config catches port outside valid range."""
    bad_config = {
        "version": "1.0.0",
        "config_version": 2,
        "default_profile": "test",
        "server": {
            "health_endpoint": "/health",
            "chat_endpoint": "/v1/chat/completions",
            "models_endpoint": "/v1/models",
        },
        "profiles": {
            "test": {
                "name": "Test",
                "model": "models/test.gguf",
                "ctx": 4096,
                "batch": 128,
                "ubatch": 64,
                "host": "127.0.0.1",
                "port": 80,
                "gpu_layers": "all",
                "quantization": "Q4_K_M",
            }
        },
    }
    is_valid, errors = validate_config(bad_config)
    assert not is_valid
    assert any("port" in e.lower() for e in errors)
