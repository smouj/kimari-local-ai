"""
Configuration loading, validation, and migration for Kimari.

Handles loading profiles, validating against JSON Schema, migrating
old configurations to newer versions, and security checks.

Config resolution order:
1. User config directory (``~/.config/kimari/kimari.profiles.json`` or ``%APPDATA%\\Kimari\\``)
2. Repo-root ``config/kimari.profiles.json`` (editable installs / development)
3. Packaged defaults (``kimari/defaults/kimari.profiles.json``)
"""

import json
import shutil
from datetime import datetime
from pathlib import Path

from kimari.core.constants import CURRENT_CONFIG_VERSION
from kimari.core.paths import get_defaults_dir, get_user_config_dir, get_user_config_path
from kimari.utils.colors import Color


def _resolve_config_path() -> Path:
    """Resolve the config file path using the standard resolution order.

    1. User config dir
    2. Repo-root config/ (editable installs)
    3. Packaged defaults
    """
    # 1. User config dir
    user_path = get_user_config_path()
    if user_path.exists():
        return user_path

    # 2. Repo-root config/ (for editable installs / development)
    from kimari.core.constants import PROJECT_ROOT

    repo_path = PROJECT_ROOT / "config" / "kimari.profiles.json"
    if repo_path.exists():
        return repo_path

    # 3. Packaged defaults
    defaults_path = Path(get_defaults_dir()) / "kimari.profiles.json"
    if defaults_path.exists():
        return defaults_path

    return user_path  # Return user path even if it doesn't exist (will fail gracefully)


def _ensure_user_config() -> Path:
    """Ensure user config exists by copying from defaults if needed.

    Returns the path to the user config file.
    """
    user_path = get_user_config_path()
    if user_path.exists():
        return user_path

    # Try to copy from defaults
    defaults_dir = get_defaults_dir()
    defaults_path = defaults_dir / "kimari.profiles.json"

    if defaults_path.exists():
        user_config_dir = get_user_config_dir()
        user_config_dir.mkdir(parents=True, exist_ok=True)
        shutil.copy2(defaults_path, user_path)
        # Also copy schema and models registry if they don't exist
        for name in ("kimari.profiles.schema.json", "kimari.models.json"):
            src = defaults_dir / name
            dst = user_config_dir / name
            if src.exists() and not dst.exists():
                shutil.copy2(src, dst)
        return user_path

    # Fallback: try repo-root config
    from kimari.core.constants import PROJECT_ROOT

    repo_path = PROJECT_ROOT / "config" / "kimari.profiles.json"
    if repo_path.exists():
        user_config_dir = get_user_config_dir()
        user_config_dir.mkdir(parents=True, exist_ok=True)
        shutil.copy2(repo_path, user_path)
        for name in ("kimari.profiles.schema.json", "kimari.models.json"):
            src = PROJECT_ROOT / "config" / name
            dst = user_config_dir / name
            if src.exists() and not dst.exists():
                shutil.copy2(src, dst)
        return user_path

    return user_path


def load_config() -> dict:
    """Load and return the Kimari profiles configuration.

    Resolution order:
    1. User config directory (platform-specific)
    2. Repo-root config/ (editable installs / development)
    3. Packaged defaults (kimari/defaults/)

    If no config is found, attempts to copy defaults to user config dir.
    """
    config_path = _resolve_config_path()
    if not config_path.exists():
        # Try to copy defaults
        config_path = _ensure_user_config()
    if not config_path.exists():
        print("[ERROR] Config not found. Searched:")
        print(f"  User config: {get_user_config_path()}")
        print(f"  Defaults:    {get_defaults_dir() / 'kimari.profiles.json'}")
        print("  Run 'kimari config path' to see where Kimari looks for config.")
        raise SystemExit(1)
    with open(config_path) as f:
        return json.load(f)


def get_profile(config: dict, profile_name: str) -> dict:
    """Get a specific profile from config."""
    profiles = config.get("profiles", {})
    if profile_name not in profiles:
        available = ", ".join(profiles.keys())
        print(f"[ERROR] Profile '{profile_name}' not found. Available: {available}")
        raise SystemExit(1)
    return profiles[profile_name]


def _resolve_schema_path() -> Path:
    """Resolve the schema file path."""
    from kimari.core.paths import get_user_schema_path

    # 1. User schema
    user_schema = get_user_schema_path()
    if user_schema.exists():
        return user_schema

    # 2. Repo-root schema
    from kimari.core.constants import PROJECT_ROOT

    repo_schema = PROJECT_ROOT / "config" / "kimari.profiles.schema.json"
    if repo_schema.exists():
        return repo_schema

    # 3. Packaged defaults
    defaults_schema = Path(get_defaults_dir()) / "kimari.profiles.schema.json"
    if defaults_schema.exists():
        return defaults_schema

    return user_schema


def validate_config(config: dict, schema: dict | None = None) -> tuple[bool, list]:
    """Validate configuration against JSON Schema.

    Returns (is_valid, list_of_errors).
    """
    errors = []

    if schema is None:
        schema_path = _resolve_schema_path()
        if not schema_path.exists():
            return True, ["Schema file not found"]
        with open(schema_path) as f:
            schema = json.load(f)

    try:
        import jsonschema

        jsonschema.validate(config, schema)
    except jsonschema.ValidationError as e:
        errors.append(f"Schema validation: {e.message}")
    except Exception as e:
        errors.append(f"Validation error: {e}")

    # Additional checks beyond schema
    # Check default_profile exists
    default = config.get("default_profile", "")
    if default and default not in config.get("profiles", {}):
        errors.append(f"default_profile '{default}' not found in profiles")

    # Security checks
    for name, profile in config.get("profiles", {}).items():
        host = profile.get("host", "127.0.0.1")
        if host == "0.0.0.0" and name != "docker":
            errors.append(
                f"Profile '{name}' uses host 0.0.0.0 but is not the 'docker' profile. "
                f"This exposes the API to all network interfaces."
            )
        port = profile.get("port", 0)
        if port < 1024 or port > 65535:
            errors.append(f"Profile '{name}' has port {port} outside valid range 1024-65535")

    # Check for absolute paths
    for name, profile in config.get("profiles", {}).items():
        model = profile.get("model", "")
        if model.startswith("/"):
            errors.append(
                f"Profile '{name}' uses absolute path '{model}'. Use relative paths (e.g. 'models/model.gguf') instead."
            )

    return len(errors) == 0, errors


def migrate_config(dry_run: bool = False) -> tuple[bool, dict]:
    """Migrate configuration to the current version.

    If dry_run is True, returns the changes that would be made without modifying the file.

    Returns (changed, migration_info) where migration_info contains details about changes.
    """
    config = load_config()
    current_version = config.get("config_version", 1)
    changes = []

    if current_version >= CURRENT_CONFIG_VERSION:
        return False, {"message": "Configuration is already up to date", "changes": []}

    # Migration from v1 to v2
    if current_version < 2:
        # Add config_version field
        changes.append("Added config_version field")

        # Add port range validation note
        changes.append("Validated port ranges (1024-65535)")

        # Ensure all profiles have vram_safe_gb if missing
        for name, profile in config.get("profiles", {}).items():
            if "vram_safe_gb" not in profile and "vram_total_gb" in profile:
                profile["vram_safe_gb"] = round(profile["vram_total_gb"] * 0.87, 1)
                changes.append(f"Added vram_safe_gb to profile '{name}'")

        # Set config_version
        config["config_version"] = 2

    # Migration from v2 to v3
    if current_version < 3:
        # Add optional performance fields to existing profiles
        optional_fields = {
            "performance_mode": "balanced",
            "flash_attn": "auto",
            "parallel": 1,
            "mlock": False,
            "no_mmap": False,
        }
        for name, profile in config.get("profiles", {}).items():
            for field, default in optional_fields.items():
                if field not in profile:
                    profile[field] = default
                    changes.append(f"Added '{field}' to profile '{name}'")

        # Set config_version
        config["config_version"] = 3
        changes.append("Upgraded config_version to 3 (performance fields)")

    migration_info = {
        "from_version": current_version,
        "to_version": CURRENT_CONFIG_VERSION,
        "changes": changes,
        "config": config,
    }

    if dry_run:
        return True, migration_info

    # Create backup at user config location
    config_path = _resolve_config_path()
    timestamp = datetime.now().strftime("%Y%m%dT%H%M%S")
    backup_path = config_path.parent / f"kimari.profiles.json.bak.{timestamp}"
    shutil.copy2(config_path, backup_path)
    migration_info["backup_path"] = str(backup_path)

    # Write updated config
    with open(config_path, "w") as f:
        json.dump(config, f, indent=2)
        f.write("\n")

    return True, migration_info


def get_config_path() -> Path:
    """Return the absolute path to the active kimari.profiles.json."""
    return _resolve_config_path().resolve()


def show_config(json_output: bool = False) -> dict:
    """Show the full configuration.

    Returns the config dict. If json_output is False, also prints human-readable output.
    """
    config = load_config()

    if json_output:
        print(json.dumps(config, indent=2))
        return config

    # Human-readable
    config_path = _resolve_config_path()
    print(f"\n  {Color.BOLD}Kimari Configuration{Color.RESET}\n")
    print(f"  Version:          {config.get('version', 'N/A')}")
    print(f"  Config version:   {config.get('config_version', 1)}")
    print(f"  Default profile:  {config.get('default_profile', 'N/A')}")
    print(f"  Config path:      {config_path}")

    print(f"\n  {Color.BOLD}Server Endpoints{Color.RESET}")
    server = config.get("server", {})
    print(f"  Health:  {server.get('health_endpoint', '/health')}")
    print(f"  Chat:    {server.get('chat_endpoint', '/v1/chat/completions')}")
    print(f"  Models:  {server.get('models_endpoint', '/v1/models')}")

    print(f"\n  {Color.BOLD}Profiles{Color.RESET}")
    for name, profile in config.get("profiles", {}).items():
        default_marker = " (default)" if name == config.get("default_profile") else ""
        print(f"  {Color.CYAN}{name}{Color.RESET}{default_marker}")
        print(f"    Name:   {profile.get('name', 'N/A')}")
        print(f"    Model:  {profile.get('model', 'N/A')}")
        print(f"    Host:   {profile.get('host', '127.0.0.1')}:{profile.get('port', 11435)}")
        print(f"    Ctx:    {profile.get('ctx', 'N/A')}")
        print(f"    Quant:  {profile.get('quantization', 'N/A')}")
        print()

    return config
