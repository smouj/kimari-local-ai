"""Tests for GPU profile listing and management."""

import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from kimari.config.loader import get_profile  # noqa: E402


def test_get_profile_gtx1060(sample_config):
    """get_profile returns the gtx1060 profile."""
    profile = get_profile(sample_config, "gtx1060")
    assert profile["name"] == "GTX 1060 (6 GB)"
    assert profile["quantization"] == "Q4_K_M"


def test_get_profile_gtx1080(sample_config):
    """get_profile returns the gtx1080 profile."""
    profile = get_profile(sample_config, "gtx1080")
    assert profile["name"] == "GTX 1080 (8 GB)"
    assert profile["quantization"] == "Q5_K_M"


def test_get_profile_test(sample_config):
    """get_profile returns the test profile."""
    profile = get_profile(sample_config, "test")
    assert profile["name"] == "Test Model"


def test_get_profile_turbo(sample_config):
    """get_profile returns the turbo profile."""
    profile = get_profile(sample_config, "turbo")
    assert profile["name"] == "Turbo (IQ4_XS)"


def test_get_profile_docker(sample_config):
    """get_profile returns the docker profile."""
    profile = get_profile(sample_config, "docker")
    assert profile["name"] == "Docker/Open WebUI"
    assert profile["host"] == "0.0.0.0"


def test_get_profile_invalid(sample_config):
    """get_profile raises SystemExit for invalid profile name."""
    with pytest.raises(SystemExit):
        get_profile(sample_config, "nonexistent")


def test_all_five_profiles_exist(sample_config):
    """All expected profiles exist in config (5 original + 8 new)."""
    expected_original = {"gtx1060", "gtx1080", "turbo", "test", "docker"}
    expected_new = {
        "gtx1060-safe",
        "gtx1060-fast",
        "gtx1080-balanced",
        "gtx1080-longctx",
        "ide-local",
        "agent-local",
        "openclaw-local",
        "hermes-local",
    }
    expected = expected_original | expected_new
    actual = set(sample_config["profiles"].keys())
    assert expected.issubset(actual), f"Missing profiles: {expected - actual}"


def test_docker_profile_uses_0000(sample_config):
    """Docker profile binds to 0.0.0.0."""
    docker = sample_config["profiles"]["docker"]
    assert docker["host"] == "0.0.0.0"
