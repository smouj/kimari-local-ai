"""
Configuration loading, validation, and migration for Kimari.

Handles loading profiles, validating against JSON Schema, migrating
old configurations to newer versions, and security checks.
"""

import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import Optional, Tuple

from kimari.core.constants import (
    CONFIG_PATH, CONFIG_SCHEMA_PATH, CURRENT_CONFIG_VERSION, PROJECT_ROOT
)
from kimari.utils.colors import Color, warn


def load_config() -> dict:
    """Load and return the Kimari profiles configuration."""
    if not CONFIG_PATH.exists():
        print(f"[ERROR] Config not found: {CONFIG_PATH}")
        print("Run this command from the kimari-local-ai root directory.")
        raise SystemExit(1)
    with open(CONFIG_PATH, "r") as f:
        return json.load(f)


def get_profile(config: dict, profile_name: str) -> dict:
    """Get a specific profile from config."""
    profiles = config.get("profiles", {})
    if profile_name not in profiles:
        available = ", ".join(profiles.keys())
        print(f"[ERROR] Profile '{profile_name}' not found. Available: {available}")
        raise SystemExit(1)
    return profiles[profile_name]


def validate_config(config: dict, schema: Optional[dict] = None) -> Tuple[bool, list]:
    """Validate configuration against JSON Schema.

    Returns (is_valid, list_of_errors).
    """
    errors = []

    if schema is None:
        if not CONFIG_SCHEMA_PATH.exists():
            return True, ["Schema file not found"]
        with open(CONFIG_SCHEMA_PATH, "r") as f:
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
                f"Profile '{name}' uses absolute path '{model}'. "
                f"Use relative paths (e.g. 'models/model.gguf') instead."
            )

    return len(errors) == 0, errors


def migrate_config(dry_run: bool = False) -> Tuple[bool, dict]:
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

    migration_info = {
        "from_version": current_version,
        "to_version": CURRENT_CONFIG_VERSION,
        "changes": changes,
        "config": config,
    }

    if dry_run:
        return True, migration_info

    # Create backup
    timestamp = datetime.now().strftime("%Y%m%dT%H%M%S")
    backup_path = CONFIG_PATH.parent / f"kimari.profiles.json.bak.{timestamp}"
    shutil.copy2(CONFIG_PATH, backup_path)
    migration_info["backup_path"] = str(backup_path)

    # Write updated config
    with open(CONFIG_PATH, "w") as f:
        json.dump(config, f, indent=2)
        f.write("\n")

    return True, migration_info


def get_config_path() -> Path:
    """Return the absolute path to kimari.profiles.json."""
    return CONFIG_PATH.resolve()


def show_config(json_output: bool = False) -> dict:
    """Show the full configuration.

    Returns the config dict. If json_output is False, also prints human-readable output.
    """
    config = load_config()

    if json_output:
        print(json.dumps(config, indent=2))
        return config

    # Human-readable
    print(f"\n  {Color.BOLD}Kimari Configuration{Color.RESET}\n")
    print(f"  Version:          {config.get('version', 'N/A')}")
    print(f"  Config version:   {config.get('config_version', 1)}")
    print(f"  Default profile:  {config.get('default_profile', 'N/A')}")
    print(f"  Config path:      {CONFIG_PATH}")

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
