"""
Shared fixtures for Kimari Local AI test suite.
"""

import json
import sys
from pathlib import Path

import pytest

# Add project root to sys.path so we can import the kimari package
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


@pytest.fixture
def project_root() -> Path:
    """Path to the project root directory."""
    return PROJECT_ROOT


@pytest.fixture
def sample_config() -> dict:
    """Loads the actual kimari.profiles.json config."""
    config_path = PROJECT_ROOT / "config" / "kimari.profiles.json"
    with open(config_path, "r") as f:
        return json.load(f)


@pytest.fixture
def sample_models_registry() -> dict:
    """Loads the actual kimari.models.json registry."""
    registry_path = PROJECT_ROOT / "config" / "kimari.models.json"
    with open(registry_path, "r") as f:
        return json.load(f)


@pytest.fixture
def tmp_state_dir(tmp_path: Path) -> Path:
    """Creates a temp directory for state files and patches constants."""
    from kimari.core import state as state_module

    state_dir = tmp_path / ".kimari"
    state_dir.mkdir()
    state_file = state_dir / "state.json"

    original_state_dir = state_module.STATE_DIR
    original_state_file = state_module.STATE_FILE

    state_module.STATE_DIR = state_dir
    state_module.STATE_FILE = state_file

    yield state_dir

    state_module.STATE_DIR = original_state_dir
    state_module.STATE_FILE = original_state_file


@pytest.fixture
def sample_profile(sample_config: dict) -> dict:
    """Returns the 'test' profile from config."""
    return sample_config["profiles"]["test"]
