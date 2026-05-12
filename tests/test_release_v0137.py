"""Tests for v0.1.37-alpha: jsonschema crash fix, GPU compute capability check, Pascal/cu126 compatibility."""

import ast
import json
import subprocess
import sys
from pathlib import Path
from unittest.mock import patch

PROJECT_ROOT = Path(__file__).resolve().parent.parent


# ---------------------------------------------------------------------------
# 1. validate_config jsonschema crash fix
# ---------------------------------------------------------------------------


class TestValidateConfigJsonschema:
    """Test that validate_config handles missing jsonschema gracefully."""

    def test_no_unbound_local_error_without_jsonschema(self):
        """validate_config must not crash with UnboundLocalError when jsonschema is missing."""
        from kimari.config.loader import validate_config

        config = {
            "version": "1",
            "config_version": 3,
            "default_profile": "test",
            "profiles": {
                "test": {
                    "name": "Test",
                    "model": "models/tinyllama.gguf",
                    "host": "127.0.0.1",
                    "port": 11435,
                    "ctx": 2048,
                },
            },
        }
        # Should not raise UnboundLocalError regardless of jsonschema availability
        is_valid, errors = validate_config(config, schema={"type": "object"})
        # With jsonschema installed, validation should pass for valid config
        # Without jsonschema, it should return a clear error message
        if not is_valid:
            # If jsonschema is not installed, check the error message is clean
            assert all("UnboundLocalError" not in str(e) for e in errors), (
                f"UnboundLocalError found in errors: {errors}"
            )

    def test_missing_jsonschema_gives_clear_error(self):
        """When jsonschema is not importable, the error message should be clear."""
        from kimari.config.loader import validate_config

        config = {
            "version": "1",
            "config_version": 3,
            "default_profile": "test",
            "profiles": {
                "test": {
                    "name": "Test",
                    "model": "models/tinyllama.gguf",
                    "host": "127.0.0.1",
                    "port": 11435,
                    "ctx": 2048,
                },
            },
        }

        # Mock jsonschema import failure
        with patch.dict("sys.modules", {"jsonschema": None}):
            # Force reimport to trigger the ModuleNotFoundError path
            is_valid, errors = validate_config(config, schema={"type": "object"})
            # Should have a clear message about jsonschema
            has_jsonschema_msg = any("jsonschema" in str(e).lower() for e in errors)
            if not is_valid:
                assert has_jsonschema_msg, f"Expected jsonschema-related error, got: {errors}"


# ---------------------------------------------------------------------------
# 2. Doctor deep — GPU compute capability check
# ---------------------------------------------------------------------------


class TestCheckGpuComputeCapability:
    """Test check_gpu_compute_capability function in doctor deep."""

    def test_function_exists(self):
        """check_gpu_compute_capability function should exist in deep module."""
        from kimari.doctor.deep import check_gpu_compute_capability

        assert callable(check_gpu_compute_capability)

    def test_returns_dict(self):
        """check_gpu_compute_capability should return a dict with expected keys."""
        from kimari.doctor.deep import check_gpu_compute_capability

        result = check_gpu_compute_capability()
        assert isinstance(result, dict)
        assert "name" in result
        assert "status" in result
        assert "value" in result
        assert "detail" in result
        # Status should be PASS or WARN (never FAIL)
        assert result["status"] in ("PASS", "WARN")

    def test_in_run_deep_checks(self):
        """check_gpu_compute_capability should be in run_deep_checks results."""
        from kimari.doctor.deep import run_deep_checks

        results = run_deep_checks()
        names = [r["name"] for r in results]
        assert "GPU Compute Capability" in names, f"GPU Compute Capability not found in: {names}"


# ---------------------------------------------------------------------------
# 3. check_training_stack — GPU arch compatibility check
# ---------------------------------------------------------------------------


class TestCheckGpuArchCompatibility:
    """Test check_gpu_arch_compatibility function in training stack checker."""

    def test_function_exists(self):
        """check_gpu_arch_compatibility function should exist."""
        from training.scripts.check_training_stack import check_gpu_arch_compatibility

        assert callable(check_gpu_arch_compatibility)

    def test_returns_dict(self):
        """check_gpu_arch_compatibility should return a dict with expected keys."""
        from training.scripts.check_training_stack import check_gpu_arch_compatibility

        result = check_gpu_arch_compatibility()
        assert isinstance(result, dict)
        assert "name" in result
        assert "passed" in result
        assert "value" in result
        assert "message" in result
        assert result["name"] == "gpu_arch_compatibility"

    def test_in_run_all_checks(self):
        """gpu_arch_compatibility should be in run_all_checks results."""
        from training.scripts.check_training_stack import run_all_checks

        result = run_all_checks()
        check_names = [c["name"] for c in result["checks"]]
        assert "gpu_arch_compatibility" in check_names, (
            f"gpu_arch_compatibility not found in: {check_names}"
        )


# ---------------------------------------------------------------------------
# 4. Pascal/cu126 documentation
# ---------------------------------------------------------------------------


class TestPascalDocs:
    """Test that Pascal GPU compatibility is documented."""

    def test_install_wsl2_mentions_pascal(self):
        """INSTALL_WSL2.md should mention Pascal/cu126/sm_61."""
        path = PROJECT_ROOT / "docs" / "INSTALL_WSL2.md"
        content = path.read_text()
        assert "Pascal" in content or "sm_61" in content or "cu126" in content, (
            "INSTALL_WSL2.md missing Pascal/cu126/sm_61 references"
        )

    def test_install_matrix_mentions_pascal(self):
        """INSTALL_MATRIX.md should mention Pascal/cu126/sm_61."""
        path = PROJECT_ROOT / "docs" / "INSTALL_MATRIX.md"
        content = path.read_text()
        assert "Pascal" in content or "sm_61" in content or "cu126" in content, (
            "INSTALL_MATRIX.md missing Pascal/cu126/sm_61 references"
        )

    def test_training_stack_compat_mentions_pascal(self):
        """TRAINING_STACK_COMPATIBILITY.md should mention Pascal/cu126/sm_61."""
        path = PROJECT_ROOT / "docs" / "TRAINING_STACK_COMPATIBILITY.md"
        content = path.read_text()
        assert "Pascal" in content or "sm_61" in content or "cu126" in content, (
            "TRAINING_STACK_COMPATIBILITY.md missing Pascal/cu126/sm_61 references"
        )


# ---------------------------------------------------------------------------
# 5. Version checks
# ---------------------------------------------------------------------------


class TestVersionV0137:
    """Test version is correctly set to v0.1.37-alpha."""

    def test_pyproject_version(self):
        """pyproject.toml should have version 0.1.37-alpha."""
        content = (PROJECT_ROOT / "pyproject.toml").read_text()
        assert 'version = "0.1.37-alpha"' in content, "pyproject.toml version not 0.1.37-alpha"

    def test_init_version(self):
        """__init__.py should have __version__ = '0.1.37-alpha'."""
        content = (PROJECT_ROOT / "kimari" / "__init__.py").read_text()
        assert '__version__ = "0.1.37-alpha"' in content, "__init__.py version not 0.1.37-alpha"

    def test_changelog_has_entry(self):
        """CHANGELOG.md should have a [0.1.37-alpha] entry."""
        content = (PROJECT_ROOT / "CHANGELOG.md").read_text()
        assert "[0.1.37-alpha]" in content, "CHANGELOG.md missing [0.1.37-alpha] entry"

    def test_roadmap_marks_current(self):
        """ROADMAP.md should mark v0.1.37-alpha as Current."""
        content = (PROJECT_ROOT / "ROADMAP.md").read_text()
        assert "v0.1.37-alpha" in content, "ROADMAP.md missing v0.1.37-alpha"
        # Should be marked as Current (not Released)
        lines = content.splitlines()
        for i, line in enumerate(lines):
            if "v0.1.37-alpha" in line:
                # Check if it says "Current"
                assert "Current" in line or any(
                    "Current" in lines[j] for j in range(max(0, i - 2), min(len(lines), i + 2))
                ), "v0.1.37-alpha not marked as Current in ROADMAP.md"
                break


# ---------------------------------------------------------------------------
# 6. Safety checks
# ---------------------------------------------------------------------------


class TestGateBlocked:
    """Test that the preview gate is still BLOCKED."""

    def test_gate_not_approved(self):
        """ADAPTER_PREVIEW_GATE.md should not have unconditional APPROVED."""
        path = PROJECT_ROOT / "docs" / "ADAPTER_PREVIEW_GATE.md"
        if not path.exists():
            return  # No gate doc = assumed BLOCKED
        content = path.read_text()
        upper = content.upper()
        # Should not contain unconditional APPROVED
        assert "STATUS: APPROVED" not in upper, "Gate has unconditional APPROVED"
        assert "IS APPROVED" not in upper, "Gate has unconditional APPROVED"


class TestDefaultProfile:
    """Test default profile is test."""

    def test_default_profile_is_test(self):
        """Default profile should be test during alpha."""
        config_path = PROJECT_ROOT / "config" / "kimari.profiles.json"
        if not config_path.exists():
            config_path = PROJECT_ROOT / "kimari" / "defaults" / "kimari.profiles.json"
        if not config_path.exists():
            return
        config = json.loads(config_path.read_text())
        assert config.get("default_profile") == "test", (
            f"Default profile is '{config.get('default_profile')}', expected 'test'"
        )


class TestNoKimari4BReleasedClaim:
    """Test that no false release claims exist."""

    def test_no_false_release_claims(self):
        """README, CHANGELOG, index.html should not claim Kimari-4B is released."""
        for fname in ("README.md", "CHANGELOG.md", "docs/index.html"):
            path = PROJECT_ROOT / fname
            if not path.exists():
                continue
            content = path.read_text().lower()
            # "kimari-4b released" or "kimari 4b released" would be false
            assert "kimari-4b released" not in content, f"{fname} contains false release claim"
            assert "kimari 4b released" not in content, f"{fname} contains false release claim"


class TestNoTrackedArtifacts:
    """Test that no training artifacts are tracked in git."""

    def test_no_gguf_tracked(self):
        """No *.gguf files should be tracked in git."""
        result = subprocess.run(
            ["git", "ls-files", "*.gguf"],
            capture_output=True,
            text=True,
            cwd=str(PROJECT_ROOT),
        )
        assert result.stdout.strip() == "", f"Tracked GGUF files found: {result.stdout.strip()}"
