"""Tests for v0.1.39-alpha: safe recovery merge — protected fields never overwritten
by incomplete user config, default_profile validation, and merge_user_config_onto_defaults_safely."""

import json
from pathlib import Path
from unittest.mock import patch

import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent

# ── Packaged defaults stub ────────────────────────────────────────────────────
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
# 1. merge_user_config_onto_defaults_safely — unit tests
# ══════════════════════════════════════════════════════════════════════════════


class TestMergeUserConfigOntoDefaultsSafely:
    """Test merge_user_config_onto_defaults_safely directly."""

    def test_profiles_empty_dict_not_overwritten(self):
        """Incomplete user config with profiles={} does NOT overwrite defaults profiles."""
        from kimari.setup.writer import merge_user_config_onto_defaults_safely

        user_config = {"default_profile": "gtx1060", "profiles": {}}
        result = merge_user_config_onto_defaults_safely(PACKAGED_DEFAULTS, user_config)

        # profiles must come from defaults, NOT from user_config
        assert len(result["profiles"]) > 0, "profiles was overwritten by empty dict from user config"
        assert "gtx1060" in result["profiles"], "profiles missing gtx1060 from defaults"
        assert "test" in result["profiles"], "profiles missing test from defaults"

    def test_version_not_overwritten(self):
        """Incomplete user config with wrong version does NOT overwrite defaults version."""
        from kimari.setup.writer import merge_user_config_onto_defaults_safely

        user_config = {"version": "0.0.1", "default_profile": "gtx1060", "profiles": {}}
        result = merge_user_config_onto_defaults_safely(PACKAGED_DEFAULTS, user_config)

        assert result["version"] == "1.1.0", f"version was overwritten: {result['version']}"

    def test_config_version_not_overwritten(self):
        """Incomplete user config with wrong config_version does NOT overwrite defaults."""
        from kimari.setup.writer import merge_user_config_onto_defaults_safely

        user_config = {"config_version": 0, "default_profile": "gtx1060"}
        result = merge_user_config_onto_defaults_safely(PACKAGED_DEFAULTS, user_config)

        assert result["config_version"] == 3, f"config_version was overwritten: {result['config_version']}"

    def test_server_not_overwritten(self):
        """Incomplete user config with wrong server does NOT overwrite defaults server."""
        from kimari.setup.writer import merge_user_config_onto_defaults_safely

        user_config = {"server": {}, "default_profile": "gtx1060"}
        result = merge_user_config_onto_defaults_safely(PACKAGED_DEFAULTS, user_config)

        assert result["server"]["health_endpoint"] == "/health", "server was overwritten by incomplete user config"

    def test_default_profile_valid_accepted(self):
        """Valid default_profile from user config is accepted if it exists in defaults profiles."""
        from kimari.setup.writer import merge_user_config_onto_defaults_safely

        user_config = {"default_profile": "gtx1060"}
        result = merge_user_config_onto_defaults_safely(PACKAGED_DEFAULTS, user_config)

        assert result["default_profile"] == "gtx1060", "valid default_profile should be accepted"

    def test_default_profile_invalid_rejected(self):
        """Invalid default_profile from user config is rejected if it doesn't exist in defaults profiles."""
        from kimari.setup.writer import merge_user_config_onto_defaults_safely

        user_config = {"default_profile": "nonexistent_profile"}
        result = merge_user_config_onto_defaults_safely(PACKAGED_DEFAULTS, user_config)

        # Should keep defaults' default_profile ("test"), not accept invalid one
        assert result["default_profile"] == "test", f"invalid default_profile was accepted: {result['default_profile']}"

    def test_safe_user_fields_preserved(self):
        """Safe user fields (setup_info, integrations, paths) are preserved from user config."""
        from kimari.setup.writer import merge_user_config_onto_defaults_safely

        user_config = {
            "default_profile": "gtx1060",
            "profiles": {},
            "setup_info": {"last_run": "2026-01-01"},
            "integrations": {"openclaw": True},
            "paths": {"custom_models": "/data/models"},
        }
        result = merge_user_config_onto_defaults_safely(PACKAGED_DEFAULTS, user_config)

        assert result["setup_info"] == {"last_run": "2026-01-01"}, "setup_info not preserved from user config"
        assert result["integrations"] == {"openclaw": True}, "integrations not preserved from user config"
        assert result["paths"] == {"custom_models": "/data/models"}, "paths not preserved from user config"

    def test_unknown_fields_preserved(self):
        """Unknown fields from user config are preserved (assumed to be user metadata)."""
        from kimari.setup.writer import merge_user_config_onto_defaults_safely

        user_config = {
            "default_profile": "gtx1060",
            "custom_metadata": {"user_note": "my setup"},
        }
        result = merge_user_config_onto_defaults_safely(PACKAGED_DEFAULTS, user_config)

        assert result["custom_metadata"] == {"user_note": "my setup"}, "unknown user metadata not preserved"

    def test_no_user_config_fields_overlap(self):
        """When user config has all fields matching defaults, protected ones still come from defaults."""
        from kimari.setup.writer import merge_user_config_onto_defaults_safely

        user_config = {
            "version": "0.0.1",
            "config_version": 0,
            "profiles": {},
            "server": {"health_endpoint": "/bad"},
            "default_profile": "nonexistent",
            "setup_info": {"user": "data"},
        }
        result = merge_user_config_onto_defaults_safely(PACKAGED_DEFAULTS, user_config)

        # All protected fields from defaults
        assert result["version"] == "1.1.0"
        assert result["config_version"] == 3
        assert len(result["profiles"]) > 0
        assert result["server"]["health_endpoint"] == "/health"
        # default_profile: "nonexistent" not in defaults profiles, so keep "test"
        assert result["default_profile"] == "test"
        # Safe user fields preserved
        assert result["setup_info"] == {"user": "data"}

    def test_defaults_not_mutated(self):
        """merge_user_config_onto_defaults_safely does not mutate the defaults dict."""
        from kimari.setup.writer import merge_user_config_onto_defaults_safely

        defaults_copy = json.loads(json.dumps(PACKAGED_DEFAULTS))
        user_config = {"default_profile": "gtx1060", "profiles": {}, "version": "0.0.1"}
        merge_user_config_onto_defaults_safely(defaults_copy, user_config)

        # defaults_copy should not be mutated
        assert defaults_copy["version"] == "1.1.0", "defaults dict was mutated"
        assert len(defaults_copy["profiles"]) > 0, "defaults profiles was mutated"


# ══════════════════════════════════════════════════════════════════════════════
# 2. Integration: write_setup_config / apply_setup_changes with incomplete config
# ══════════════════════════════════════════════════════════════════════════════


class TestWriteSetupConfigSafeMerge:
    """Test write_setup_config and apply_setup_changes with incomplete user config."""

    def test_incomplete_config_profiles_empty_recovered(self, tmp_config_path: Path, patch_data: dict):
        """write_setup_config recovers profiles when user config has profiles={}."""
        from kimari.setup.writer import write_setup_config

        # Write an incomplete user config
        incomplete = {"default_profile": "gtx1060", "profiles": {}}
        tmp_config_path.write_text(json.dumps(incomplete))

        result = write_setup_config(patch_data, tmp_config_path)
        assert result["written"] is True, f"Write failed: {result}"
        assert result["recovery_needed"] is True, "recovery_needed should be True"

        written = json.loads(tmp_config_path.read_text())
        assert len(written["profiles"]) > 0, "profiles still empty after recovery"
        assert "gtx1060" in written["profiles"], "gtx1060 profile missing after recovery"
        assert written["version"] == "1.1.0", f"version not from defaults: {written['version']}"

    def test_incomplete_config_version_preserved(self, tmp_config_path: Path, patch_data: dict):
        """write_setup_config preserves defaults version when user config has wrong version."""
        from kimari.setup.writer import write_setup_config

        # Write incomplete user config with wrong version
        incomplete = {"version": "0.0.1", "default_profile": "gtx1060", "profiles": {}}
        tmp_config_path.write_text(json.dumps(incomplete))

        result = write_setup_config(patch_data, tmp_config_path)
        assert result["written"] is True

        written = json.loads(tmp_config_path.read_text())
        assert written["version"] == "1.1.0", f"version should be from defaults, got: {written['version']}"

    def test_incomplete_config_invalid_default_profile_resolved(
        self, tmp_config_path: Path, patch_data: dict
    ):
        """write_setup_config resolves invalid default_profile from incomplete config."""
        from kimari.setup.writer import write_setup_config

        # Write incomplete user config with invalid default_profile
        incomplete = {"default_profile": "nonexistent_profile", "profiles": {}}
        tmp_config_path.write_text(json.dumps(incomplete))

        result = write_setup_config(patch_data, tmp_config_path)
        assert result["written"] is True

        written = json.loads(tmp_config_path.read_text())
        # default_profile should be resolved to a valid profile (gtx1060 from patch, or test from defaults)
        assert written["default_profile"] in written["profiles"], (
            f"default_profile '{written['default_profile']}' not in profiles"
        )

    def test_apply_setup_changes_safe_merge(self, tmp_config_path: Path, patch_data: dict):
        """apply_setup_changes also uses safe merge for incomplete config."""
        from kimari.setup.writer import apply_setup_changes

        # Write an incomplete user config
        incomplete = {"default_profile": "gtx1060", "profiles": {}}
        tmp_config_path.write_text(json.dumps(incomplete))

        result = apply_setup_changes(patch_data, tmp_config_path)
        assert result["written"] is True

        written = json.loads(tmp_config_path.read_text())
        assert len(written["profiles"]) > 0, "profiles still empty after safe merge"
        assert "gtx1060" in written["profiles"]

    def test_reset_user_config_generates_valid_config(self, tmp_config_path: Path, patch_data: dict):
        """apply_setup_changes with reset=True generates a valid config from defaults."""
        from kimari.setup.writer import apply_setup_changes

        # Write a broken user config first
        broken = {"default_profile": "nonexistent", "profiles": {}, "version": "0.0.1"}
        tmp_config_path.write_text(json.dumps(broken))

        result = apply_setup_changes(patch_data, reset=True, config_path=tmp_config_path)
        assert result["written"] is True
        assert result["recovery_needed"] is True

        written = json.loads(tmp_config_path.read_text())
        assert written["version"] == "1.1.0"
        assert len(written["profiles"]) > 0
        assert written["default_profile"] in written["profiles"]


# ══════════════════════════════════════════════════════════════════════════════
# 3. No config = {} pattern remains
# ══════════════════════════════════════════════════════════════════════════════


class TestNoUnsafeMergePattern:
    """Verify that the unsafe _base.update(config) pattern no longer exists."""

    def test_no_base_update_in_writer(self):
        """writer.py no longer contains the unsafe _base.update(config) pattern."""
        writer_path = PROJECT_ROOT / "kimari" / "setup" / "writer.py"
        writer_text = writer_path.read_text()
        assert "_base.update(config)" not in writer_text, (
            "Unsafe _base.update(config) pattern still found in writer.py"
        )
        assert "_base = defaults.copy()" not in writer_text, (
            "Unsafe _base = defaults.copy() pattern still found in writer.py"
        )

    def test_merge_user_config_onto_defaults_safely_exists(self):
        """merge_user_config_onto_defaults_safely function exists in writer module."""
        from kimari.setup.writer import merge_user_config_onto_defaults_safely

        assert callable(merge_user_config_onto_defaults_safely)

    def test_protected_fields_constant_exists(self):
        """_PROTECTED_FIELDS constant exists and contains expected fields."""
        from kimari.setup.writer import _PROTECTED_FIELDS

        assert "version" in _PROTECTED_FIELDS
        assert "config_version" in _PROTECTED_FIELDS
        assert "profiles" in _PROTECTED_FIELDS
        assert "server" in _PROTECTED_FIELDS

    def test_safe_user_fields_constant_exists(self):
        """_SAFE_USER_FIELDS constant exists and contains expected fields."""
        from kimari.setup.writer import _SAFE_USER_FIELDS

        assert "setup_info" in _SAFE_USER_FIELDS
        assert "integrations" in _SAFE_USER_FIELDS
        assert "paths" in _SAFE_USER_FIELDS
