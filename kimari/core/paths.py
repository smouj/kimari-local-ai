"""
Kimari user path management.

Provides platform-aware paths for user configuration, state, and cache
directories.  All paths can be overridden via environment variables.

Platform defaults
-----------------
Linux / macOS:
    Config:  ~/.config/kimari/
    State:   ~/.local/state/kimari/
    Cache:   ~/.cache/kimari/
    Models:  ~/.local/share/kimari/models/

Windows:
    Config:  %APPDATA%\\Kimari\\
    State:   %LOCALAPPDATA%\\Kimari\\state\\
    Cache:   %LOCALAPPDATA%\\Kimari\\cache\\
    Models:  %LOCALAPPDATA%\\Kimari\\models\\

Override environment variables
------------------------------
KIMARI_HOME          — Base directory (overrides all defaults)
KIMARI_CONFIG_DIR    — Config directory
KIMARI_STATE_DIR     — State directory
KIMARI_CACHE_DIR     — Cache directory
KIMARI_MODELS_DIR    — Models directory
"""

import os
import sys
from pathlib import Path


def _is_windows() -> bool:
    return sys.platform == "win32"


def get_kimari_home() -> Path:
    """Return the Kimari home directory.

    Priority:
    1. ``KIMARI_HOME`` environment variable
    2. Platform default
    """
    env = os.environ.get("KIMARI_HOME")
    if env:
        return Path(env)
    if _is_windows():
        appdata = os.environ.get("APPDATA", os.path.expanduser("~\\AppData\\Roaming"))
        return Path(appdata) / "Kimari"
    # Linux / macOS — follow XDG
    xdg = os.environ.get("XDG_CONFIG_HOME")
    if xdg:
        return Path(xdg) / "kimari"
    return Path.home() / ".config" / "kimari"


def get_user_config_dir() -> Path:
    """Return the user configuration directory.

    Overridable via ``KIMARI_CONFIG_DIR`` or ``KIMARI_HOME``.
    """
    env = os.environ.get("KIMARI_CONFIG_DIR")
    if env:
        return Path(env)
    # KIMARI_HOME overrides all paths
    home_env = os.environ.get("KIMARI_HOME")
    if home_env:
        return Path(home_env)
    if _is_windows():
        appdata = os.environ.get("APPDATA", os.path.expanduser("~\\AppData\\Roaming"))
        return Path(appdata) / "Kimari"
    xdg = os.environ.get("XDG_CONFIG_HOME")
    if xdg:
        return Path(xdg) / "kimari"
    return Path.home() / ".config" / "kimari"


def get_user_state_dir() -> Path:
    """Return the user state directory (PID files, runtime state, tokens).

    Overridable via ``KIMARI_STATE_DIR`` or ``KIMARI_HOME``.
    """
    env = os.environ.get("KIMARI_STATE_DIR")
    if env:
        return Path(env)
    # KIMARI_HOME overrides all paths
    home_env = os.environ.get("KIMARI_HOME")
    if home_env:
        return Path(home_env) / "state"
    if _is_windows():
        local_appdata = os.environ.get("LOCALAPPDATA", os.path.expanduser("~\\AppData\\Local"))
        return Path(local_appdata) / "Kimari" / "state"
    xdg = os.environ.get("XDG_STATE_HOME")
    if xdg:
        return Path(xdg) / "kimari"
    return Path.home() / ".local" / "state" / "kimari"


def get_user_cache_dir() -> Path:
    """Return the user cache directory.

    Overridable via ``KIMARI_CACHE_DIR`` or ``KIMARI_HOME``.
    """
    env = os.environ.get("KIMARI_CACHE_DIR")
    if env:
        return Path(env)
    # KIMARI_HOME overrides all paths
    home_env = os.environ.get("KIMARI_HOME")
    if home_env:
        return Path(home_env) / "cache"
    if _is_windows():
        local_appdata = os.environ.get("LOCALAPPDATA", os.path.expanduser("~\\AppData\\Local"))
        return Path(local_appdata) / "Kimari" / "cache"
    xdg = os.environ.get("XDG_CACHE_HOME")
    if xdg:
        return Path(xdg) / "kimari"
    return Path.home() / ".cache" / "kimari"


def get_user_models_dir() -> Path:
    """Return the user models directory (where GGUF files are stored).

    Overridable via ``KIMARI_MODELS_DIR`` or ``KIMARI_HOME``.
    """
    env = os.environ.get("KIMARI_MODELS_DIR")
    if env:
        return Path(env)
    # KIMARI_HOME overrides all paths
    home_env = os.environ.get("KIMARI_HOME")
    if home_env:
        return Path(home_env) / "models"
    if _is_windows():
        local_appdata = os.environ.get("LOCALAPPDATA", os.path.expanduser("~\\AppData\\Local"))
        return Path(local_appdata) / "Kimari" / "models"
    xdg = os.environ.get("XDG_DATA_HOME")
    if xdg:
        return Path(xdg) / "kimari" / "models"
    return Path.home() / ".local" / "share" / "kimari" / "models"


def _ensure_dir(path: Path) -> Path:
    """Create directory if it doesn't exist, return the path."""
    path.mkdir(parents=True, exist_ok=True)
    return path


def get_user_config_path() -> Path:
    """Return the path to the user profiles config file."""
    return get_user_config_dir() / "kimari.profiles.json"


def get_user_models_registry_path() -> Path:
    """Return the path to the user models registry file."""
    return get_user_config_dir() / "kimari.models.json"


def get_user_schema_path() -> Path:
    """Return the path to the user schema file."""
    return get_user_config_dir() / "kimari.profiles.schema.json"


def get_auth_dir() -> Path:
    """Return the directory for auth tokens (user state dir)."""
    return _ensure_dir(get_user_state_dir())


def get_auth_path() -> Path:
    """Return the path to the auth token file."""
    return get_auth_dir() / "auth.json"


def get_pid_file_path() -> Path:
    """Return the path to the PID file."""
    return get_user_state_dir() / "kimari-server.pid"


def get_log_file_path() -> Path:
    """Return the path to the log file."""
    return get_user_state_dir() / "kimari-server.log"


def get_state_file_path() -> Path:
    """Return the path to the state file."""
    return get_user_state_dir() / "state.json"


def get_defaults_dir() -> Path:
    """Return the path to the packaged defaults directory inside the kimari package."""
    return Path(__file__).resolve().parent.parent / "defaults"
