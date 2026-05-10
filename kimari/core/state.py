"""
State management for Kimari server runtime.

Handles state.json for tracking server status, PID, profile, etc.
State is stored in the user state directory (not PROJECT_ROOT).
"""

import json
from datetime import datetime, timezone
from pathlib import Path

from kimari.core.paths import get_user_state_dir


def _get_state_dir() -> Path:
    """Return the state directory, creating it if needed."""
    state_dir = get_user_state_dir()
    state_dir.mkdir(parents=True, exist_ok=True)
    return state_dir


def _get_state_file() -> Path:
    """Return the path to state.json."""
    return _get_state_dir() / "state.json"


def ensure_state_dir():
    """Create state directory if it doesn't exist."""
    _get_state_dir()


def write_state(
    status: str,
    pid: int | None = None,
    profile: str | None = None,
    model: str | None = None,
    host: str | None = None,
    port: int | None = None,
    error: str | None = None,
):
    """Write state to state.json."""
    state_dir = _get_state_dir()
    state_file = state_dir / "state.json"
    state = {
        "status": status,
        "pid": pid,
        "profile": profile,
        "model": model,
        "host": host,
        "port": port,
        "started_at": None,
        "error": error,
        "log_file": str(get_user_state_dir() / "kimari-server.log"),
    }
    if status == "READY" and pid is not None:
        state["started_at"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    with open(state_file, "w") as f:
        json.dump(state, f, indent=2)


def read_state() -> dict | None:
    """Read state from state.json."""
    state_file = _get_state_file()
    if not state_file.exists():
        return None
    try:
        with open(state_file) as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return None


def clear_state():
    """Remove state file."""
    state_file = _get_state_file()
    if state_file.exists():
        state_file.unlink(missing_ok=True)


def is_pid_alive(pid: int) -> bool:
    """Check if a PID is still alive."""
    import os

    try:
        os.kill(pid, 0)
        return True
    except (OSError, ProcessLookupError):
        return False
