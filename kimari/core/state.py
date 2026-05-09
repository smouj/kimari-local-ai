"""
State management for Kimari server runtime.

Handles .kimari/state.json for tracking server status, PID, profile, etc.
"""

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from kimari.core.constants import STATE_DIR, STATE_FILE


def ensure_state_dir():
    """Create .kimari/ directory if it doesn't exist."""
    STATE_DIR.mkdir(parents=True, exist_ok=True)


def write_state(status: str, pid: Optional[int] = None, profile: Optional[str] = None,
                model: Optional[str] = None, host: Optional[str] = None,
                port: Optional[int] = None, error: Optional[str] = None):
    """Write state to .kimari/state.json."""
    ensure_state_dir()
    state = {
        "status": status,
        "pid": pid,
        "profile": profile,
        "model": model,
        "host": host,
        "port": port,
        "started_at": None,
        "error": error,
        "log_file": "kimari-server.log",
    }
    if status == "READY" and pid is not None:
        state["started_at"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)


def read_state() -> Optional[dict]:
    """Read state from .kimari/state.json."""
    if not STATE_FILE.exists():
        return None
    try:
        with open(STATE_FILE, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return None


def clear_state():
    """Remove state file."""
    if STATE_FILE.exists():
        STATE_FILE.unlink(missing_ok=True)


def is_pid_alive(pid: int) -> bool:
    """Check if a PID is still alive."""
    import os
    try:
        os.kill(pid, 0)
        return True
    except (OSError, ProcessLookupError):
        return False
