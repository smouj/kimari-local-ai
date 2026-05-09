"""
Tests for state management (write_state, read_state, clear_state).
"""

import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from kimari.core.state import write_state, read_state, clear_state


def test_write_read_state_roundtrip(tmp_state_dir):
    """write_state then read_state returns the same data."""
    from kimari.core import state as state_module
    write_state("READY", pid=12345, profile="gtx1060", model="models/test.gguf",
                host="127.0.0.1", port=11435)
    state = read_state()
    assert state is not None
    assert state["status"] == "READY"
    assert state["pid"] == 12345
    assert state["profile"] == "gtx1060"


def test_read_state_missing_file(tmp_state_dir):
    """read_state returns None when state file doesn't exist."""
    state = read_state()
    assert state is None


def test_clear_state(tmp_state_dir):
    """clear_state removes the state file."""
    write_state("READY", pid=12345)
    assert read_state() is not None
    clear_state()
    assert read_state() is None


def test_ready_state_has_timestamp(tmp_state_dir):
    """READY state includes started_at timestamp."""
    write_state("READY", pid=12345)
    state = read_state()
    assert state is not None
    assert state["started_at"] is not None
    assert "T" in state["started_at"]  # ISO format


def test_starting_state_no_timestamp(tmp_state_dir):
    """STARTING state has no started_at timestamp."""
    write_state("STARTING")
    state = read_state()
    assert state is not None
    assert state["started_at"] is None


def test_error_state(tmp_state_dir):
    """ERROR state stores error information."""
    write_state("ERROR", error="MODEL_NOT_FOUND", profile="test")
    state = read_state()
    assert state is not None
    assert state["status"] == "ERROR"
    assert state["error"] == "MODEL_NOT_FOUND"
