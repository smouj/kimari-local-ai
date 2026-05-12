"""Tests for v0.1.38-alpha: setup writer — no empty config invariant, config completeness,
profile resolution, validation, and config recovery."""

import json
from pathlib import Path
from unittest.mock import patch

import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent

# ── Packaged defaults stub ────────────────────────────────────────────────────
# Minimal valid config that mirrors the structure of kimari/defaults/kimari.profiles.json
PACKAGED_DEFAULTS = {
    "version": "1.1.0",
    "config_version": 3,
    "default_profile": "test",
    "server": {
        "health_endpoint": "/health",
        "chat_endpoint": "/v1/chat/completions",
        "models_endpoint": "/v1/models",
    },
    "profiles": {
        "gtx1060": {"name": "GTX 1060 (6 GB)", "model": "models/Kimari-4B-Q4_K_M.gguf"},
        "gtx1080": {"name": "GTX 1080 (8 GB)", "model": "models/Kimari-4B-Q5_K_M.gguf"},
        "turbo": {"name": "Turbo (IQ4_XS)", "model": "models/Kimari-4B-IQ4_XS.gguf"},
        "test": {"name": "Test Model", "model": "models/tinyllama.gguf"},
        "docker": {"name": "Docker/Open WebUI", "model": "models/tinyllama.gguf"},
        "gtx1060-safe": {"name": "GTX 1060 Safe", "model": "models/Kimari-4B-Q4_K_M.gguf"},
        "gtx1060-fast": {"name": "GTX 1060 Fast", "model": "models/Kimari-4B-Q4_K_M.gguf"},
        "gtx1080-balanced": {"name": "GTX 1080 Balanced", "model": "models/Kimari-4B-Q5_K_M.gguf"},
        "gtx1080-longctx": {"name": "GTX 1080 Long Context", "model": "models/Kimari-4B-Q5_K_M.gguf"},
        "ide-local": {"name": "IDE Local", "model": "models/tinyllama.gguf"},
        "agent-local": {"name": "Agent Local", "model": "models/tinyllama.gguf"},
        "openclaw-local": {"name": "OpenClaw Local", "model": "models/tinyllama.gguf"},
        "hermes-local": {"name": "Hermes Agent Local", "model": "models/tinyllama.gguf"},
    },
}


def _mock_load_packaged_defaults():
    """Return our deterministic packaged defaults instead of reading disk."""
    return json.loads(json.dumps(PACKAGED_DEFAULTS))


# ── Fixtures ──────────────────────────────────────────────────────────────────


@pytest.fixture(autouse=True)
def _patch_packaged_defaults():
    """Patch _load_packaged_defaults in the writer module for every test."""
    with patch("kimari.setup.writer._load_packaged_defaults", side_effect=_mock_load_packaged_defaults):
        yield


@pytest.fixture
def tmp_config_path(tmp_path: Path) -> Path:
    """Return a temporary config file path (no file created yet)."""
    return tmp_path / "kimari.profiles.json"


@pytest.fixture
def patch_data() -> dict:
    """Return a minimal valid patch dict as produced by build_setup_patch."""
    return {
        "recommended_profile": "gtx1060",
        "resolved_profile": "gtx1060",
        "profile_exists": True,
        "integration": None,
        "hardware_summary": {"gpu": "GTX 1060"},
        "paths": {"models_dir": "/tmp/models"},
        "would_write": True,
        "config_path": "/tmp/kimari.profiles.json",
        "changes": ["default_profile: 'test' -> 'gtx1060'"],
    }


# ══════════════════════════════════════════════════════════════════════════════
# 1–2. write_setup_config / apply_setup_changes never produce empty config
# ══════════════════════════════════════════════════════════════════════════════


class TestNoEmptyConfig:
    """Writer functions must never produce an empty/incomplete config (no config={})."""

    def test_write_setup_config_no_empty_config(self, tmp_config_path: Path, patch_data: dict):
        """write_setup_config does NOT create an empty/incomplete config."""
        from kimari.setup.writer import write_setup_config

        result = write_setup_config(patch_data, tmp_config_path)
        assert result["written"] is True, f"Write failed: {result}"

        written = json.loads(tmp_config_path.read_text())
        assert written != {}, "Written config is an empty dict"
        assert "version" in written, "Written config missing 'version'"
        assert "profiles" in written and written["profiles"], "Written config missing or empty 'profiles'"
        assert "default_profile" in written, "Written config missing 'default_profile'"

    def test_apply_setup_changes_no_empty_config(self, tmp_config_path: Path, patch_data: dict):
        """apply_setup_changes does NOT create an empty/incomplete config."""
        from kimari.setup.writer import apply_setup_changes

        result = apply_setup_changes(patch_data, tmp_config_path)
        assert result["written"] is True, f"Apply failed: {result}"

        written = json.loads(tmp_config_path.read_text())
        assert written != {}, "Written config is an empty dict"
        assert "version" in written, "Written config missing 'version'"
        assert "profiles" in written and written["profiles"], "Written config missing or empty 'profiles'"
        assert "default_profile" in written, "Written config missing 'default_profile'"


# ══════════════════════════════════════════════════════════════════════════════
# 3–5. Generated config structure
# ══════════════════════════════════════════════════════════════════════════════


class TestGeneratedConfigStructure:
    """Verify that the config written by writer has required structural keys."""

    def test_generated_config_has_version(self, tmp_config_path: Path, patch_data: dict):
        """Config written by writer has a 'version' key."""
        from kimari.setup.writer import write_setup_config

        write_setup_config(patch_data, tmp_config_path)
        written = json.loads(tmp_config_path.read_text())
        assert "version" in written, "Written config missing 'version' key"
        assert written["version"], "'version' key is empty or falsy"

    def test_generated_config_has_profiles(self, tmp_config_path: Path, patch_data: dict):
        """Config written by writer has 'profiles' that is non-empty."""
        from kimari.setup.writer import write_setup_config

        write_setup_config(patch_data, tmp_config_path)
        written = json.loads(tmp_config_path.read_text())
        assert "profiles" in written, "Written config missing 'profiles' key"
        assert isinstance(written["profiles"], dict), "'profiles' is not a dict"
        assert len(written["profiles"]) > 0, "'profiles' dict is empty"

    def test_default_profile_exists_in_profiles(self, tmp_config_path: Path, patch_data: dict):
        """default_profile value is present in the profiles dict."""
        from kimari.setup.writer import write_setup_config

        write_setup_config(patch_data, tmp_config_path)
        written = json.loads(tmp_config_path.read_text())
        dp = written.get("default_profile")
        assert dp is not None, "'default_profile' is missing"
        assert dp in written["profiles"], (
            f"default_profile '{dp}' not found in profiles: {list(written['profiles'].keys())}"
        )


# ══════════════════════════════════════════════════════════════════════════════
# 6–7. resolve_recommended_profile
# ══════════════════════════════════════════════════════════════════════════════


class TestResolveRecommendedProfile:
    """Test resolve_recommended_profile resolution logic."""

    def test_recommended_gtx1060_resolves_to_safe(self):
        """'gtx1060' resolves to 'gtx1060-safe' when gtx1060-safe exists in profiles."""
        from kimari.setup.writer import resolve_recommended_profile

        profiles = PACKAGED_DEFAULTS["profiles"].copy()
        # Remove "gtx1060" so the mapping to "gtx1060-safe" kicks in
        profiles_without_gtx1060 = {k: v for k, v in profiles.items() if k != "gtx1060"}
        result = resolve_recommended_profile("gtx1060", profiles_without_gtx1060)
        assert result == "gtx1060-safe", f"Expected 'gtx1060-safe', got '{result}'"

    def test_recommended_gtx1060_resolves_to_test(self):
        """'gtx1060' resolves to 'test' when neither gtx1060 nor gtx1060-safe exists."""
        from kimari.setup.writer import resolve_recommended_profile

        profiles = {"test": {"name": "Test"}, "turbo": {"name": "Turbo"}}
        result = resolve_recommended_profile("gtx1060", profiles)
        assert result == "test", f"Expected 'test', got '{result}'"

    def test_resolve_recommended_profile_exists(self):
        """Returns profile directly when it exists in profiles."""
        from kimari.setup.writer import resolve_recommended_profile

        profiles = PACKAGED_DEFAULTS["profiles"]
        result = resolve_recommended_profile("gtx1080", profiles)
        assert result == "gtx1080", f"Expected 'gtx1080', got '{result}'"

    def test_resolve_recommended_profile_gtx1080_balanced(self):
        """'gtx1080' resolves to 'gtx1080-balanced' when gtx1080 doesn't exist but gtx1080-balanced does."""
        from kimari.setup.writer import resolve_recommended_profile

        profiles = {k: v for k, v in PACKAGED_DEFAULTS["profiles"].items() if k != "gtx1080"}
        result = resolve_recommended_profile("gtx1080", profiles)
        assert result == "gtx1080-balanced", f"Expected 'gtx1080-balanced', got '{result}'"

    def test_resolve_recommended_profile_fallback_first(self):
        """Returns first available profile when no mapping or 'test' profile exists."""
        from kimari.setup.writer import resolve_recommended_profile

        profiles = {"custom-a": {"name": "A"}, "custom-b": {"name": "B"}}
        result = resolve_recommended_profile("gtx1060", profiles)
        assert result == "custom-a", f"Expected 'custom-a', got '{result}'"


# ══════════════════════════════════════════════════════════════════════════════
# 8. Reset regenerates from defaults
# ══════════════════════════════════════════════════════════════════════════════


class TestResetUserConfig:
    """Test that reset=True regenerates config from packaged defaults."""

    def test_reset_user_config_regenerates_from_defaults(self, tmp_config_path: Path, patch_data: dict):
        """apply_setup_changes with reset=True regenerates from defaults."""
        from kimari.setup.writer import apply_setup_changes

        # Write a user config first (simulating an existing config with custom data)
        existing_config = {
            "version": "0.9.0",
            "default_profile": "docker",
            "profiles": {"docker": {"name": "Docker"}},
        }
        tmp_config_path.write_text(json.dumps(existing_config))

        result = apply_setup_changes(patch_data, reset=True, config_path=tmp_config_path)
        assert result["written"] is True, f"Write failed: {result}"
        assert result["recovery_needed"] is True, "reset=True should set recovery_needed"

        written = json.loads(tmp_config_path.read_text())
        # Should have the full profiles from defaults, not just "docker"
        assert "gtx1060" in written["profiles"], "Missing gtx1060 profile — config not regenerated from defaults"
        assert "test" in written["profiles"], "Missing test profile — config not regenerated from defaults"
        # Version should come from defaults, not the old user config
        assert written["version"] == "1.1.0", f"Version not from defaults: {written['version']}"


# ══════════════════════════════════════════════════════════════════════════════
# 9–14. is_config_complete
# ══════════════════════════════════════════════════════════════════════════════


class TestIsConfigComplete:
    """Test is_config_complete validation function."""

    def test_incomplete_user_config_detected(self):
        """is_config_complete returns False for incomplete configs."""
        from kimari.setup.writer import is_config_complete

        incomplete = {"default_profile": "test"}
        assert is_config_complete(incomplete) is False, "Incomplete config not detected"

    def test_is_config_complete_valid(self):
        """is_config_complete returns True for valid configs."""
        from kimari.setup.writer import is_config_complete

        valid = {
            "version": "1.1.0",
            "default_profile": "test",
            "profiles": {"test": {"name": "Test"}, "gtx1060": {"name": "GTX 1060"}},
        }
        assert is_config_complete(valid) is True, "Valid config marked as incomplete"

    def test_is_config_complete_empty(self):
        """is_config_complete returns False for empty dict."""
        from kimari.setup.writer import is_config_complete

        assert is_config_complete({}) is False, "Empty dict marked as complete"

    def test_is_config_complete_no_version(self):
        """is_config_complete returns False when version is missing."""
        from kimari.setup.writer import is_config_complete

        config = {
            "default_profile": "test",
            "profiles": {"test": {"name": "Test"}},
        }
        assert is_config_complete(config) is False, "Config without version marked as complete"

    def test_is_config_complete_no_profiles(self):
        """is_config_complete returns False when profiles is empty."""
        from kimari.setup.writer import is_config_complete

        config = {
            "version": "1.1.0",
            "default_profile": "test",
            "profiles": {},
        }
        assert is_config_complete(config) is False, "Config with empty profiles marked as complete"

    def test_is_config_complete_default_not_in_profiles(self):
        """is_config_complete returns False when default_profile is not in profiles."""
        from kimari.setup.writer import is_config_complete

        config = {
            "version": "1.1.0",
            "default_profile": "nonexistent",
            "profiles": {"test": {"name": "Test"}},
        }
        assert is_config_complete(config) is False, "Config with bad default_profile marked as complete"


# ══════════════════════════════════════════════════════════════════════════════
# 18–19. load_base_config_for_setup
# ══════════════════════════════════════════════════════════════════════════════


class TestLoadBaseConfigForSetup:
    """Test load_base_config_for_setup loading and recovery logic."""

    def test_load_base_config_for_setup_no_user_config(self, tmp_path: Path):
        """Loads packaged defaults when no user config exists."""
        from kimari.setup.writer import load_base_config_for_setup

        with patch("kimari.setup.writer.get_user_config_path", return_value=tmp_path / "nonexistent.json"):
            config = load_base_config_for_setup()
        assert "version" in config, "Loaded config missing 'version'"
        assert "profiles" in config and config["profiles"], "Loaded config missing or empty 'profiles'"
        assert config.get("default_profile") == "test", f"Expected default_profile='test', got {config.get('default_profile')}"

    def test_load_base_config_for_setup_incomplete(self, tmp_path: Path):
        """Loads defaults and marks recovery_needed when user config is incomplete."""
        from kimari.setup.writer import load_base_config_for_setup

        # Write an incomplete user config
        user_config_path = tmp_path / "kimari.profiles.json"
        incomplete = {"default_profile": "test"}
        user_config_path.write_text(json.dumps(incomplete))

        with patch("kimari.setup.writer.get_user_config_path", return_value=user_config_path):
            config = load_base_config_for_setup()

        assert config.get("recovery_needed") is True, "recovery_needed not set for incomplete config"
        assert "version" in config, "Recovered config missing 'version'"
        assert "profiles" in config and config["profiles"], "Recovered config missing or empty 'profiles'"


# ══════════════════════════════════════════════════════════════════════════════
# 20. _validate_config_for_write
# ══════════════════════════════════════════════════════════════════════════════


class TestValidateConfigForWrite:
    """Test _validate_config_for_write catches invalid configs."""

    def test_validate_config_for_write(self):
        """_validate_config_for_write catches missing version, empty profiles, invalid default_profile."""
        from kimari.setup.writer import _validate_config_for_write

        # Missing version
        no_version = {"profiles": {"test": {"name": "Test"}}, "default_profile": "test"}
        is_valid, errors = _validate_config_for_write(no_version)
        assert is_valid is False, "Config without version passed validation"
        assert any("version" in str(e).lower() for e in errors), f"No version error in: {errors}"

        # Empty profiles
        empty_profiles = {"version": "1.1.0", "profiles": {}, "default_profile": "test"}
        is_valid, errors = _validate_config_for_write(empty_profiles)
        assert is_valid is False, "Config with empty profiles passed validation"
        assert any("profiles" in str(e).lower() for e in errors), f"No profiles error in: {errors}"

        # Invalid default_profile
        bad_default = {
            "version": "1.1.0",
            "profiles": {"test": {"name": "Test"}},
            "default_profile": "nonexistent",
        }
        is_valid, errors = _validate_config_for_write(bad_default)
        assert is_valid is False, "Config with invalid default_profile passed validation"
        assert any("default_profile" in str(e).lower() for e in errors), f"No default_profile error in: {errors}"

        # Empty config
        is_valid, errors = _validate_config_for_write({})
        assert is_valid is False, "Empty config passed validation"
        assert any("empty" in str(e).lower() for e in errors), f"No empty error in: {errors}"

        # Valid config
        valid = {
            "version": "1.1.0",
            "profiles": {"test": {"name": "Test"}},
            "default_profile": "test",
        }
        is_valid, errors = _validate_config_for_write(valid)
        assert is_valid is True, f"Valid config failed validation: {errors}"
