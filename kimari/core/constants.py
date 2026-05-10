"""
Kimari constants — version, ASCII art.

Path resolution is now handled by ``kimari.core.paths``.
The ``PROJECT_ROOT`` constant is retained for backward compatibility
and for repo-root development (editable installs).

All runtime paths (config, state, logs, PID) are resolved through
the paths module, which supports:
- User config directories (platform-specific)
- KIMARI_HOME / KIMARI_CONFIG_DIR / etc. environment variable overrides
- Packaged defaults (kimari/defaults/) as fallback
- Repo-root config/ for editable installs
"""

from pathlib import Path

from kimari import __version__ as KIMARI_VERSION  # noqa: N812
from kimari.core.paths import (
    get_log_file_path,
    get_pid_file_path,
    get_state_file_path,
    get_user_config_path,
    get_user_models_dir,
    get_user_models_registry_path,
    get_user_schema_path,
    get_user_state_dir,
)

# ─── Project Root Detection (for backward compat / dev mode) ────────────────


def _detect_project_root() -> Path:
    """Detect the project root by searching upward for config/kimari.profiles.json."""
    current = Path(__file__).resolve().parent
    for _ in range(10):  # Walk up at most 10 levels
        if (current / "config" / "kimari.profiles.json").exists():
            return current
        parent = current.parent
        if parent == current:
            break
        current = parent
    # Fallback: assume the repo root is one level up from the kimari/ package
    return Path(__file__).resolve().parent.parent


PROJECT_ROOT = _detect_project_root()

# ─── Paths (resolved via kimari.core.paths) ─────────────────────────────────

# For backward compatibility, provide module-level constants that resolve
# through the paths module. These are evaluated at import time, so env
# overrides set *after* import may not take effect.
CONFIG_PATH = get_user_config_path()
CONFIG_SCHEMA_PATH = get_user_schema_path()
MODELS_REGISTRY_PATH = get_user_models_registry_path()
MODELS_DIR = get_user_models_dir()
PID_FILE = get_pid_file_path()
LOG_FILE = get_log_file_path()
STATE_DIR = get_user_state_dir()
STATE_FILE = get_state_file_path()

# ─── Version ──────────────────────────────────────────────────────────────────

KIMARI_ASCII = f"""
██╗  ██╗██╗███╗   ███╗ █████╗ ██████╗ ██╗
██║ ██╔╝██║████╗ ████║██╔══██╗██╔══██╗██║
█████╔╝ ██║██╔████╔██║███████║██████╔╝██║
██╔═██╗ ██║██║╚██╔╝██║██╔══██║██╔══██╗██║
██║  ██╗██║██║ ╚═╝ ██║██║  ██║██║  ██║██║
╚═╝  ╚═╝╚═╝╚═╝     ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝╚═╝
   Local AI for Consumer GPUs — v{KIMARI_VERSION}
   Created by Smouj (https://x.com/smouj013)
"""

# ─── Config Version ───────────────────────────────────────────────────────────

CURRENT_CONFIG_VERSION = 3
