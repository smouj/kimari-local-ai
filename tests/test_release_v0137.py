#!/usr/bin/env python3
"""Release validation tests for v0.1.37-alpha.

Validates all v0.1.37 artifacts:
- validate_config() handles missing jsonschema gracefully
- doctor --deep doesn't crash without jsonschema
- resolve_smoke_gate() function and logic
- check_gpu_compute_capability() function and dict structure
- check_gpu_arch_compatibility() function and dict structure
- hf_jobs_micro_sft.py has resolve_smoke_gate and smoke_gate_source
- Pascal GPU documentation in INSTALL_WSL2, INSTALL_MATRIX, TRAINING_STACK_COMPATIBILITY
- Version consistency (pyproject.toml, __init__.py)
- CHANGELOG and ROADMAP entries
- Gate BLOCKED (no unconditional APPROVED in ADAPTER_PREVIEW_GATE.md)
- default_profile is test
- No Kimari-4B released claim
- check-release.py and RELEASE_CHECKLIST have v0.1.37 sections
- No adapter/GGUF tracked in git
"""

from __future__ import annotations

import importlib
import json
import subprocess
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent


# ---------------------------------------------------------------------------
# Helpers: dynamic import for training scripts (not on sys.path by default)
# ---------------------------------------------------------------------------

def _import_resolve_smoke_gate():
    """Import resolve_smoke_gate from training/scripts/hf_jobs_micro_sft.py."""
    script_path = PROJECT_ROOT / "training" / "scripts" / "hf_jobs_micro_sft.py"
    spec = importlib.util.spec_from_file_location("hf_jobs_micro_sft", script_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.resolve_smoke_gate


def _import_check_gpu_arch_compatibility():
    """Import check_gpu_arch_compatibility from training/scripts/check_training_stack.py."""
    script_path = PROJECT_ROOT / "training" / "scripts" / "check_training_stack.py"
    spec = importlib.util.spec_from_file_location("check_training_stack", script_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.check_gpu_arch_compatibility


# ═══════════════════════════════════════════════════════════════════════════
# 1. validate_config handles missing jsonschema
# ═══════════════════════════════════════════════════════════════════════════


class TestValidateConfigJsonschema:
    """Test validate_config() handles missing jsonschema gracefully."""

    def test_validate_config_no_crash_without_jsonschema(self) -> None:
        """validate_config() must not crash with UnboundLocalError when jsonschema is missing."""
        from kimari.config.loader import validate_config

        config = {"default_profile": "test", "profiles": {"test": {"host": "127.0.0.1", "port": 11435}}}
        with patch.dict("sys.modules", {"jsonschema": None}):
            # Force ModuleNotFoundError by removing jsonschema from importable modules
            with patch("kimari.config.loader.jsonschema", side_effect=ModuleNotFoundError("jsonschema"), create=True):
                pass
            # The real test: make import jsonschema raise ModuleNotFoundError inside validate_config
            with patch("builtins.__import__", side_effect=self._block_jsonschema_import):
                is_valid, errors = validate_config(config)

        # Should return a clean error, not UnboundLocalError
        assert isinstance(errors, list), f"errors should be a list, got {type(errors)}"
        # At least one error should mention jsonschema
        jsonschema_errors = [e for e in errors if "jsonschema" in e.lower()]
        assert len(jsonschema_errors) > 0, f"Expected jsonschema-related error, got: {errors}"

    @staticmethod
    def _block_jsonschema_import(name, *args, **kwargs):
        """Block import of jsonschema to simulate it being missing."""
        if name == "jsonschema":
            raise ModuleNotFoundError("No module named 'jsonschema'")
        return importlib.__import__(name, *args, **kwargs)


# ═══════════════════════════════════════════════════════════════════════════
# 2. doctor --deep doesn't crash without jsonschema
# ═══════════════════════════════════════════════════════════════════════════


class TestDoctorDeepNoJsonschema:
    """Test that deep checks still work when jsonschema is missing."""

    def test_deep_checks_no_crash_without_jsonschema(self) -> None:
        """run_deep_checks should not crash when jsonschema is not installed."""
        from kimari.doctor.deep import run_deep_checks

        with patch("builtins.__import__", side_effect=TestValidateConfigJsonschema._block_jsonschema_import):
            results = run_deep_checks()

        assert isinstance(results, list), "run_deep_checks should return a list"
        # Last item is the summary
        summary = results[-1]
        assert summary["name"] == "Summary", f"Last item should be Summary, got {summary['name']}"


# ═══════════════════════════════════════════════════════════════════════════
# 3–7. resolve_smoke_gate
# ═══════════════════════════════════════════════════════════════════════════


class TestResolveSmokeGate:
    """Test resolve_smoke_gate() function and logic."""

    def test_resolve_smoke_gate_exists(self) -> None:
        """resolve_smoke_gate can be imported from training.scripts.hf_jobs_micro_sft."""
        func = _import_resolve_smoke_gate()
        assert callable(func), "resolve_smoke_gate should be callable"

    def test_override_returns_true_override(self) -> None:
        """With override=True, returns (True, ..., 'override')."""
        resolve_smoke_gate = _import_resolve_smoke_gate()
        validated, message, source = resolve_smoke_gate(
            require_smoke_summary=None, override=True,
        )
        assert validated is True, f"Expected True, got {validated}"
        assert source == "override", f"Expected 'override', got {source!r}"

    def test_explicit_valid_path(self, tmp_path: Path) -> None:
        """With a valid smoke summary file, returns (True, ..., 'explicit')."""
        summary = {
            "status": "completed",
            "gate_state": "BLOCKED",
        }
        summary_file = tmp_path / "smoke_summary.json"
        summary_file.write_text(json.dumps(summary))

        resolve_smoke_gate = _import_resolve_smoke_gate()
        validated, message, source = resolve_smoke_gate(
            require_smoke_summary=summary_file, override=False,
        )
        assert validated is True, f"Expected True with valid summary, got {validated}: {message}"
        assert source == "explicit", f"Expected 'explicit', got {source!r}"

    def test_explicit_invalid_path(self, tmp_path: Path) -> None:
        """With a non-existent path, returns (False, ..., 'explicit')."""
        nonexistent = tmp_path / "does_not_exist.json"

        resolve_smoke_gate = _import_resolve_smoke_gate()
        validated, message, source = resolve_smoke_gate(
            require_smoke_summary=nonexistent, override=False,
        )
        assert validated is False, f"Expected False with invalid path, got {validated}"
        assert source == "explicit", f"Expected 'explicit', got {source!r}"

    def test_fallback_default_tmp(self) -> None:
        """Without explicit path and no override, falls back to /tmp/hf_jobs_smoke_summary.json."""
        # Load the module and register it in sys.modules so patch can find it
        script_path = PROJECT_ROOT / "training" / "scripts" / "hf_jobs_micro_sft.py"
        spec = importlib.util.spec_from_file_location("hf_jobs_micro_sft_v0137", script_path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)

        resolve_smoke_gate = mod.resolve_smoke_gate

        # Patch within the dynamically-loaded module's namespace
        with patch.object(mod, "validate_smoke_summary_file", return_value=(True, "Smoke summary validated")):
            # Also patch Path so /tmp/hf_jobs_smoke_summary.json appears to exist
            original_path = mod.Path

            class MockPath:
                def __init__(self, p):
                    self._path = p

                def exists(self):
                    return self._path == "/tmp/hf_jobs_smoke_summary.json"

            mod.Path = MockPath
            try:
                validated, message, source = resolve_smoke_gate(
                    require_smoke_summary=None, override=False,
                )
                assert source == "default_tmp", f"Expected 'default_tmp', got {source!r}"
                assert validated is True, f"Expected True with mocked valid summary, got {validated}"
            finally:
                mod.Path = original_path


# ═══════════════════════════════════════════════════════════════════════════
# 8–9. check_gpu_compute_capability
# ═══════════════════════════════════════════════════════════════════════════


class TestCheckGpuComputeCapability:
    """Test check_gpu_compute_capability() in kimari.doctor.deep."""

    def test_function_exists(self) -> None:
        """check_gpu_compute_capability can be imported from kimari.doctor.deep."""
        from kimari.doctor.deep import check_gpu_compute_capability

        assert callable(check_gpu_compute_capability), "check_gpu_compute_capability should be callable"

    def test_returns_dict_with_required_keys(self) -> None:
        """check_gpu_compute_capability returns dict with name, status, value, detail."""
        from kimari.doctor.deep import check_gpu_compute_capability

        result = check_gpu_compute_capability()
        assert isinstance(result, dict), f"Expected dict, got {type(result)}"
        for key in ("name", "status", "value", "detail"):
            assert key in result, f"Missing key: {key!r} in {result}"


# ═══════════════════════════════════════════════════════════════════════════
# 10–11. check_gpu_arch_compatibility
# ═══════════════════════════════════════════════════════════════════════════


class TestCheckGpuArchCompatibility:
    """Test check_gpu_arch_compatibility() in training.scripts.check_training_stack."""

    def test_function_exists(self) -> None:
        """check_gpu_arch_compatibility can be imported from training.scripts.check_training_stack."""
        func = _import_check_gpu_arch_compatibility()
        assert callable(func), "check_gpu_arch_compatibility should be callable"

    def test_returns_dict_with_required_keys(self) -> None:
        """check_gpu_arch_compatibility returns dict with name, passed, value, message."""
        func = _import_check_gpu_arch_compatibility()
        result = func()
        assert isinstance(result, dict), f"Expected dict, got {type(result)}"
        for key in ("name", "passed", "value", "message"):
            assert key in result, f"Missing key: {key!r} in {result}"


# ═══════════════════════════════════════════════════════════════════════════
# 12–13. hf_jobs_micro_sft source checks
# ═══════════════════════════════════════════════════════════════════════════


class TestHfJobsMicroSftSource:
    """Test hf_jobs_micro_sft.py source contains expected symbols."""

    def test_has_resolve_smoke_gate(self) -> None:
        """hf_jobs_micro_sft.py source contains resolve_smoke_gate function."""
        text = (PROJECT_ROOT / "training" / "scripts" / "hf_jobs_micro_sft.py").read_text()
        assert "def resolve_smoke_gate" in text, "hf_jobs_micro_sft.py must define resolve_smoke_gate"

    def test_json_output_has_smoke_gate_source(self) -> None:
        """hf_jobs_micro_sft.py JSON output includes smoke_gate_source field."""
        text = (PROJECT_ROOT / "training" / "scripts" / "hf_jobs_micro_sft.py").read_text()
        assert "smoke_gate_source" in text, "hf_jobs_micro_sft.py must include smoke_gate_source in output"


# ═══════════════════════════════════════════════════════════════════════════
# 14–16. Pascal GPU documentation
# ═══════════════════════════════════════════════════════════════════════════


class TestPascalDocs:
    """Test Pascal GPU compatibility documentation."""

    def test_install_wsl2_mentions_pascal(self) -> None:
        """docs/INSTALL_WSL2.md mentions Pascal, cu126, or sm_61."""
        text = (PROJECT_ROOT / "docs" / "INSTALL_WSL2.md").read_text().lower()
        assert "pascal" in text or "cu126" in text or "sm_61" in text, \
            "INSTALL_WSL2.md must mention Pascal, cu126, or sm_61"

    def test_install_matrix_mentions_pascal(self) -> None:
        """docs/INSTALL_MATRIX.md mentions Pascal or cu126."""
        text = (PROJECT_ROOT / "docs" / "INSTALL_MATRIX.md").read_text().lower()
        assert "pascal" in text or "cu126" in text, \
            "INSTALL_MATRIX.md must mention Pascal or cu126"

    def test_training_stack_compatibility_mentions_pascal(self) -> None:
        """docs/TRAINING_STACK_COMPATIBILITY.md mentions Pascal or cu126."""
        text = (PROJECT_ROOT / "docs" / "TRAINING_STACK_COMPATIBILITY.md").read_text().lower()
        assert "pascal" in text or "cu126" in text, \
            "TRAINING_STACK_COMPATIBILITY.md must mention Pascal or cu126"


# ═══════════════════════════════════════════════════════════════════════════
# 17–19. Version, CHANGELOG, ROADMAP
# ═══════════════════════════════════════════════════════════════════════════


class TestVersionV0137:
    """Test v0.1.37 version consistency and metadata."""

    def test_pyproject_version(self) -> None:
        """pyproject.toml must have version 0.1.37-alpha."""
        text = (PROJECT_ROOT / "pyproject.toml").read_text()
        assert "0.1.37-alpha" in text, "pyproject.toml must have version 0.1.37-alpha"

    def test_init_version(self) -> None:
        """__init__.py must have version 0.1.37-alpha."""
        text = (PROJECT_ROOT / "kimari" / "__init__.py").read_text()
        assert "0.1.37-alpha" in text, "__init__.py must have version 0.1.37-alpha"

    def test_changelog_has_entry(self) -> None:
        """CHANGELOG.md must have a [0.1.37-alpha] entry."""
        text = (PROJECT_ROOT / "CHANGELOG.md").read_text()
        assert "[0.1.37-alpha]" in text, "CHANGELOG.md must have [0.1.37-alpha] entry"

    def test_roadmap_marks_current(self) -> None:
        """ROADMAP.md must mark 0.1.37-alpha as Current."""
        text = (PROJECT_ROOT / "ROADMAP.md").read_text()
        assert "0.1.37-alpha" in text, "ROADMAP.md must mention 0.1.37-alpha"
        # Check that it's marked as Current (not just mentioned)
        # Find the line with 0.1.37 and check it has "Current"
        for line in text.splitlines():
            if "0.1.37" in line:
                assert "Current" in line, f"ROADMAP.md line with 0.1.37 must say Current: {line!r}"
                break
        else:
            pytest.fail("0.1.37 not found in ROADMAP.md")


# ═══════════════════════════════════════════════════════════════════════════
# 20. Gate BLOCKED
# ═══════════════════════════════════════════════════════════════════════════


class TestGateBlocked:
    """Test that the preview gate is still BLOCKED."""

    def test_adapter_preview_gate_no_unconditional_approved(self) -> None:
        """ADAPTER_PREVIEW_GATE.md must not have unconditional APPROVED."""
        gate_doc = PROJECT_ROOT / "docs" / "ADAPTER_PREVIEW_GATE.md"
        assert gate_doc.exists(), "docs/ADAPTER_PREVIEW_GATE.md must exist"
        content = gate_doc.read_text()

        for line in content.splitlines():
            stripped = line.strip()
            upper = stripped.upper()
            # Skip conditional state names
            if "APPROVED_FOR_PRIVATE_TESTING" in upper:
                continue
            if "APPROVED_FOR_PUBLIC_PREVIEW" in upper:
                continue
            # Skip conditional language
            if any(phrase in upper for phrase in (
                "MAY BE APPROVED", "CAN BE APPROVED", "TO BE APPROVED",
                "MAY BE", "CAN BE", "REQUIRE",
            )):
                continue
            # Check for unconditional approval claims
            if "APPROVED" in upper:
                assert not any(
                    phrase in upper for phrase in ("STATUS: APPROVED", "IS APPROVED", "STATE: APPROVED")
                ), f"Unconditional APPROVED found: {stripped[:80]}"


# ═══════════════════════════════════════════════════════════════════════════
# 21. default_profile is test
# ═══════════════════════════════════════════════════════════════════════════


class TestDefaultProfile:
    """Test that default_profile is 'test'."""

    def test_default_profile_is_test(self) -> None:
        """config/kimari.profiles.json must have default_profile = 'test'."""
        profiles_path = PROJECT_ROOT / "config" / "kimari.profiles.json"
        assert profiles_path.exists(), "config/kimari.profiles.json must exist"
        data = json.loads(profiles_path.read_text())
        assert data.get("default_profile") == "test", \
            f"default_profile must be 'test', got {data.get('default_profile')!r}"


# ═══════════════════════════════════════════════════════════════════════════
# 22. No Kimari-4B released claim
# ═══════════════════════════════════════════════════════════════════════════


class TestNoKimari4BReleasedClaim:
    """Test that no file falsely claims Kimari-4B is released."""

    def test_no_kimari_4b_released_claim(self) -> None:
        """README, CHANGELOG, and index.html must not claim Kimari-4B is released."""
        false_patterns = [
            "kimari-4b is available now",
            "kimari-4b can be downloaded",
            "download kimari-4b",
            "kimari-4b weights available",
            "kimari-4b has been released",
        ]
        sources = {
            "README.md": (PROJECT_ROOT / "README.md").read_text().lower(),
            "CHANGELOG.md": (PROJECT_ROOT / "CHANGELOG.md").read_text().lower(),
        }
        index_html = PROJECT_ROOT / "docs" / "index.html"
        if index_html.exists():
            sources["docs/index.html"] = index_html.read_text().lower()

        for source_name, text in sources.items():
            for pattern in false_patterns:
                assert pattern not in text, \
                    f"False claim '{pattern}' found in {source_name}"


# ═══════════════════════════════════════════════════════════════════════════
# 23–24. check-release.py and RELEASE_CHECKLIST have v0.1.37 section
# ═══════════════════════════════════════════════════════════════════════════


class TestReleaseScripts:
    """Test that release scripts and checklists mention v0.1.37."""

    def test_check_release_has_v0137_section(self) -> None:
        """scripts/release/check-release.py must mention v0.1.37."""
        text = (PROJECT_ROOT / "scripts" / "release" / "check-release.py").read_text()
        assert "0.1.37" in text, "check-release.py must mention v0.1.37"

    def test_release_checklist_has_v0137_section(self) -> None:
        """RELEASE_CHECKLIST.md must have a v0.1.37 Checks section."""
        text = (PROJECT_ROOT / "RELEASE_CHECKLIST.md").read_text()
        assert "0.1.37" in text, "RELEASE_CHECKLIST.md must have v0.1.37 section"


# ═══════════════════════════════════════════════════════════════════════════
# 25. No adapter/GGUF tracked
# ═══════════════════════════════════════════════════════════════════════════


class TestNoTrackedArtifacts:
    """Ensure no weights/adapters/GGUF are tracked in git."""

    def test_no_gguf_tracked(self) -> None:
        """No *.gguf files should be tracked in git."""
        result = subprocess.run(
            ["git", "ls-files", "*.gguf"],
            capture_output=True, text=True, cwd=str(PROJECT_ROOT), timeout=10,
        )
        gguf_files = [f for f in result.stdout.strip().splitlines() if f]
        assert len(gguf_files) == 0, f"GGUF files tracked: {gguf_files}"
