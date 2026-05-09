"""
Kimari constants — paths, version, ASCII art.

All paths are resolved relative to the project root, which is detected
as the directory containing the config/ folder.
"""

from pathlib import Path

from kimari import __version__ as KIMARI_VERSION

# ─── Project Root Detection ─────────────────────────────────────────────────

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

# ─── Paths ────────────────────────────────────────────────────────────────────

CONFIG_PATH = PROJECT_ROOT / "config" / "kimari.profiles.json"
CONFIG_SCHEMA_PATH = PROJECT_ROOT / "config" / "kimari.profiles.schema.json"
MODELS_REGISTRY_PATH = PROJECT_ROOT / "config" / "kimari.models.json"
MODELS_DIR = PROJECT_ROOT / "models"
PID_FILE = PROJECT_ROOT / ".kimari-server.pid"
LOG_FILE = PROJECT_ROOT / "kimari-server.log"
STATE_DIR = PROJECT_ROOT / ".kimari"
STATE_FILE = STATE_DIR / "state.json"

# ─── Version ──────────────────────────────────────────────────────────────────

KIMARI_ASCII = f"""
 ██████╗██╗  ██╗██████╗  ██████╗ ███╗   ██╗ █████╗
██╔════╝██║  ██║██╔══██╗██╔═══██╗████╗  ██║██╔══██╗
██║     ███████║██████╔╝██║   ██║██╔██╗ ██║███████║
██║     ██╔══██║██╔══██╗██║   ██║██║╚██╗██║██╔══██║
╚██████╗██║  ██║██║  ██║╚██████╔╝██║ ╚████║██║  ██║
 ╚═════╝╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═══╝╚═╝  ╚═╝
   Local AI for Consumer GPUs — v{KIMARI_VERSION}
   Created by Smouj (https://x.com/smouj013)
"""

# ─── Config Version ───────────────────────────────────────────────────────────

CURRENT_CONFIG_VERSION = 2
