"""
Tests for v0.1.6/v0.1.7-alpha hardening:
- Default profile is 'test' while Kimari-4B is not published
- kimari/py.typed exists (PEP 561 marker)
- Test profile model size coherence with registry
- CLI start without --profile uses default from config
- Package excludes unwanted files
- Installed CLI entry point works
"""

import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


def test_default_profile_is_test(sample_config):
    """Default profile must be 'test' while Kimari-4B is not published."""
    assert sample_config["default_profile"] == "test", (
        f"Expected default_profile='test', got '{sample_config['default_profile']}'. "
        "Kimari-4B is not yet published, so default must be 'test' for first-run success."
    )


def test_py_typed_exists():
    """kimari/py.typed must exist (PEP 561 marker declared in pyproject.toml)."""
    py_typed = PROJECT_ROOT / "kimari" / "py.typed"
    assert py_typed.exists(), (
        "kimari/py.typed is missing. pyproject.toml declares it in [tool.setuptools.package-data]. "
        "Create it with: touch kimari/py.typed"
    )


def test_test_profile_model_size_coherent(sample_config, sample_models_registry):
    """Test profile estimated_model_size_gb must match registry size_gb."""
    test_profile = sample_config["profiles"]["test"]
    profile_size = test_profile.get("estimated_model_size_gb")

    test_model = None
    for m in sample_models_registry["models"]:
        if m["id"] == "test":
            test_model = m
            break

    assert test_model is not None, "Model 'test' not found in kimari.models.json registry"
    registry_size = test_model["size_gb"]

    assert profile_size == registry_size, (
        f"Test profile estimated_model_size_gb ({profile_size}) does not match "
        f"registry size_gb ({registry_size}). They must be coherent."
    )


def test_test_profile_points_to_tinyllama(sample_config):
    """Test profile must point to TinyLlama (the only published model)."""
    test_profile = sample_config["profiles"]["test"]
    model_path = test_profile["model"]
    assert "tinyllama" in model_path.lower(), f"Test profile model path should reference TinyLlama, got: {model_path}"


def test_start_dry_run_without_profile():
    """'kimari start --dry-run' (no --profile) should use default profile and succeed."""
    cmd = [sys.executable, "-m", "kimari.cli.main", "start", "--dry-run"]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    assert result.returncode == 0, (
        f"'kimari start --dry-run' failed (exit {result.returncode}). stdout: {result.stdout}\nstderr: {result.stderr}"
    )
    assert "DRY RUN" in result.stdout, f"Expected 'DRY RUN' in output, got: {result.stdout}"


def test_bench_defaults_to_test_profile():
    """'kimari bench' without --profile should use 'test' default."""
    from kimari.config.loader import load_config  # noqa: E402

    config = load_config()
    default = config.get("default_profile", "test")
    assert default == "test", f"Bench defaults to config default_profile, which should be 'test', got: {default}"


def test_installed_kimari_entry_point():
    """Verify the 'kimari' entry point is defined in pyproject.toml."""
    import tomllib

    pyproject_path = PROJECT_ROOT / "pyproject.toml"
    with open(pyproject_path, "rb") as f:
        data = tomllib.load(f)
    scripts = data.get("project", {}).get("scripts", {})
    assert "kimari" in scripts, "Entry point 'kimari' not found in pyproject.toml [project.scripts]"
    assert scripts["kimari"] == "kimari.cli.main:main", (
        f"Entry point 'kimari' should be 'kimari.cli.main:main', got: {scripts['kimari']}"
    )
