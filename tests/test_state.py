"""
Tests for Kimari state management (write, read, clear).
"""

import json
import sys
from pathlib import Path

import kimari_cli
from kimari_cli import clear_state, read_state, write_state

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "cli"))


def test_write_and_read_state(tmp_state_dir):
    """Write then read state round-trip."""
    write_state("STARTING", profile="test", model="models/test.gguf",
                host="127.0.0.1", port=11435)

    state = read_state()
    assert state is not None
    assert state["status"] == "STARTING"
    assert state["profile"] == "test"
    assert state["model"] == "models/test.gguf"
    assert state["host"] == "127.0.0.1"
    assert state["port"] == 11435


def test_read_state_no_file(tmp_state_dir):
    """Returns None when no state file exists."""
    # tmp_state_dir is empty (no state.json yet)
    result = read_state()
    assert result is None


def test_clear_state(tmp_state_dir):
    """clear_state removes file."""
    write_state("READY", pid=12345, profile="test", model="models/test.gguf",
                host="127.0.0.1", port=11435)

    # Verify file was created
    assert kimari_cli.STATE_FILE.exists()

    clear_state()

    # Verify file was removed
    assert not kimari_cli.STATE_FILE.exists()


def test_write_state_ready_has_timestamp(tmp_state_dir):
    """READY state with a PID has started_at timestamp."""
    write_state("READY", pid=12345, profile="test", model="models/test.gguf",
                host="127.0.0.1", port=11435)

    state = read_state()
    assert state is not None
    assert state["status"] == "READY"
    assert state["started_at"] is not None
    # Should be ISO format with Z suffix
    assert state["started_at"].endswith("Z")
    assert "T" in state["started_at"]
