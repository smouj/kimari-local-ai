"""
Tests for Kimari profile management and recommendation.
"""

import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "cli"))

from kimari_cli import get_profile, recommend_profile


def test_get_profile_valid(sample_config):
    """get_profile returns correct profile for known name."""
    profile = get_profile(sample_config, "gtx1060")
    assert profile["name"] == "GTX 1060 (6 GB)"
    assert profile["quantization"] == "Q4_K_M"


def test_get_profile_invalid(sample_config):
    """get_profile with invalid name calls sys.exit."""
    with pytest.raises(SystemExit):
        get_profile(sample_config, "nonexistent_profile")


def test_profiles_has_gtx1060(sample_config):
    """gtx1060 profile exists."""
    assert "gtx1060" in sample_config["profiles"]


def test_profiles_has_gtx1080(sample_config):
    """gtx1080 profile exists."""
    assert "gtx1080" in sample_config["profiles"]


def test_profiles_has_test(sample_config):
    """test profile exists."""
    assert "test" in sample_config["profiles"]


def test_recommended_profile_with_no_gpu(sample_config):
    """Returns default when no GPU is detected."""
    result = recommend_profile(sample_config, None)
    assert result == sample_config["default_profile"]


def test_recommended_profile_with_8gb(sample_config):
    """Returns gtx1080 for 8GB VRAM GPU."""
    gpu = {"name": "Some GPU", "vram_mb": 8192, "driver": "550.0"}
    result = recommend_profile(sample_config, gpu)
    assert result == "gtx1080"


def test_recommended_profile_with_6gb(sample_config):
    """Returns gtx1060 for 6GB VRAM GPU."""
    gpu = {"name": "Some GPU", "vram_mb": 6144, "driver": "550.0"}
    result = recommend_profile(sample_config, gpu)
    assert result == "gtx1060"
