"""
Tests for Kimari config loading and validation.
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "cli"))

from kimari_cli import load_config


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
    """All ports are in valid range 1-65535."""
    for profile_name, profile in sample_config["profiles"].items():
        port = profile["port"]
        assert 1 <= port <= 65535, (
            f"Profile '{profile_name}' has invalid port: {port}"
        )
