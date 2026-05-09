"""
Tests for model registry and pull functionality.
"""

import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from kimari.models.registry import load_models_registry


def test_load_models_registry():
    """Models registry loads successfully."""
    registry = load_models_registry()
    assert isinstance(registry, dict)
    assert "models" in registry


def test_registry_has_expected_model_ids(sample_models_registry):
    """Registry contains expected model IDs."""
    model_ids = [m["id"] for m in sample_models_registry["models"]]
    assert "test" in model_ids
    assert "recommended" in model_ids


def test_registry_models_have_required_fields(sample_models_registry):
    """All models in registry have required fields."""
    required_fields = {"id", "display_name", "url", "filename", "target_path", "size_gb", "recommended_profile"}
    for model in sample_models_registry["models"]:
        missing = required_fields - set(model.keys())
        assert not missing, f"Model '{model.get('id', '?')}' is missing fields: {missing}"


def test_registry_models_have_status(sample_models_registry):
    """All models in registry have status field."""
    for model in sample_models_registry["models"]:
        assert "status" in model, f"Model '{model.get('id', '?')}' is missing 'status' field"
        assert model["status"] in ("test", "recommended", "experimental", "planned")


def test_registry_models_have_family(sample_models_registry):
    """All models in registry have family field."""
    for model in sample_models_registry["models"]:
        assert "family" in model, f"Model '{model.get('id', '?')}' is missing 'family' field"


def test_registry_urls_are_https(sample_models_registry):
    """All model download URLs use HTTPS."""
    for model in sample_models_registry["models"]:
        assert model["url"].startswith("https://"), (
            f"Model '{model['id']}' uses non-HTTPS URL: {model['url']}"
        )


def test_pull_unknown_model_exits():
    """pull_model raises SystemExit for unknown model ID."""
    from kimari.models.registry import pull_model
    with pytest.raises(SystemExit):
        pull_model("nonexistent_model_12345")
