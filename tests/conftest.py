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
    with open(config_path) as f:
        return json.load(f)


@pytest.fixture
def sample_models_registry() -> dict:
    """Loads the actual kimari.models.json registry."""
    registry_path = PROJECT_ROOT / "config" / "kimari.models.json"
    with open(registry_path) as f:
        return json.load(f)


@pytest.fixture
def tmp_state_dir(tmp_path: Path, monkeypatch) -> Path:
    """Creates a temp directory for state files and patches the paths module.

    Sets KIMARI_STATE_DIR to a temporary directory so state files
    (state.json, PID, log) are written there instead of the real user dir.
    """
    state_dir = tmp_path / "state"
    state_dir.mkdir()
    monkeypatch.setenv("KIMARI_STATE_DIR", str(state_dir))

    yield state_dir

    # monkeypatch automatically restores env


@pytest.fixture
def tmp_kimari_home(tmp_path: Path, monkeypatch) -> Path:
    """Creates a temp Kimari home directory and sets KIMARI_HOME.

    This redirects ALL kimari paths (config, state, cache, models)
    to a temporary directory for testing.
    """
    home_dir = tmp_path / "kimari-home"
    home_dir.mkdir()
    monkeypatch.setenv("KIMARI_HOME", str(home_dir))

    yield home_dir

    # monkeypatch automatically restores env


@pytest.fixture
def sample_profile(sample_config: dict) -> dict:
    """Returns the 'test' profile from config."""
    return sample_config["profiles"]["test"]
