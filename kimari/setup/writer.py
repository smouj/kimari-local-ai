"""
Setup configuration persistence for Kimari.

Builds patches from detected hardware/software information, creates backups,
and writes the setup_info section into the user config file.

Key invariant: writer NEVER starts from an empty dict (``{}``) when building
a config to write.  If no user config exists, packaged defaults are loaded
first, then the setup patch is applied on top.  This prevents the bug where
``kimari setup --write --yes`` would produce an incomplete config with only
``default_profile`` and ``setup_info`` keys (missing ``version``,
``profiles``, ``server``, etc.).
"""

import json
import os
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

from kimari.core.paths import get_defaults_dir, get_user_config_path


# ─── Helper functions ─────────────────────────────────────────────────────────


def is_config_complete(config: dict) -> bool:
    """Return True if *config* has all required top-level keys and is usable.

    A config is considered complete when:
    - ``version`` exists
    - ``profiles`` exists and is not empty
    - ``default_profile`` exists
    - ``default_profile`` value is present in ``profiles``
    """
    if not config:
        return False

    if "version" not in config:
        return False

    profiles = config.get("profiles")
    if not profiles or not isinstance(profiles, dict) or len(profiles) == 0:
        return False

    default = config.get("default_profile")
    if not default:
        return False

    if default not in profiles:
        return False

    return True


def _load_packaged_defaults() -> dict:
    """Load the packaged default config from kimari/defaults/.

    Returns the parsed JSON dict, or an empty dict on failure.
    """
    # Try kimari/defaults/ first
    defaults_path = Path(get_defaults_dir()) / "kimari.profiles.json"
    if defaults_path.exists():
        try:
            with open(defaults_path) as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            pass

    # Try repo-root config/ (editable installs)
    try:
        from kimari.core.constants import PROJECT_ROOT

        repo_path = PROJECT_ROOT / "config" / "kimari.profiles.json"
        if repo_path.exists():
            with open(repo_path) as f:
                return json.load(f)
    except (ImportError, json.JSONDecodeError, OSError):
        pass

    # Last resort: empty dict with a warning flag
    return {"_incomplete_fallback": True}


def load_base_config_for_setup(reset: bool = False) -> dict:
    """Load the base configuration for setup operations.

    Strategy:
    - If *reset* is True: always load packaged defaults.
    - If user config exists and is complete: load user config.
    - If user config exists but is incomplete: load packaged defaults and
      set ``recovery_needed=True``.
    - If no user config: load packaged defaults.

    Never returns ``{}`` unless all sources fail.
    """
    user_path = get_user_config_path()

    if reset:
        defaults = _load_packaged_defaults()
        defaults["recovery_needed"] = True
        defaults["recovery_reason"] = "reset-user-config requested"
        return defaults

    # Try loading user config
    if user_path.exists():
        try:
            with open(user_path) as f:
                user_config = json.load(f)
        except (json.JSONDecodeError, OSError):
            # Corrupt config — fall back to defaults
            defaults = _load_packaged_defaults()
            defaults["recovery_needed"] = True
            defaults["recovery_reason"] = "user config corrupt or unreadable"
            return defaults

        if is_config_complete(user_config):
            return user_config

        # User config exists but is incomplete — recover from defaults
        defaults = _load_packaged_defaults()
        defaults["recovery_needed"] = True
        defaults["recovery_reason"] = "user config incomplete"
        return defaults

    # No user config — load packaged defaults
    defaults = _load_packaged_defaults()
    return defaults


def resolve_recommended_profile(recommended_profile: str, profiles: dict) -> str:
    """Resolve a recommended profile name to one that actually exists.

    Resolution order:
    1. If *recommended_profile* exists in *profiles*, use it.
    2. If *recommended_profile* is ``gtx1060`` and ``gtx1060-safe`` exists, use
       ``gtx1060-safe``.
    3. If *recommended_profile* is ``gtx1080`` and ``gtx1080-balanced`` exists,
       use ``gtx1080-balanced``.
    4. If ``test`` exists, fallback to ``test``.
    5. Otherwise, use the first available profile.
    6. Never return a profile that does not exist in *profiles*.
    """
    if not profiles:
        return recommended_profile  # Can't resolve without profiles

    if recommended_profile in profiles:
        return recommended_profile

    # Common resolution mappings
    safe_mappings = {
        "gtx1060": "gtx1060-safe",
        "gtx1080": "gtx1080-balanced",
    }

    mapped = safe_mappings.get(recommended_profile)
    if mapped and mapped in profiles:
        return mapped

    # Fallback to "test"
    if "test" in profiles:
        return "test"

    # Fallback to first available profile
    first = next(iter(profiles), None)
    if first:
        return first

    # Should not happen, but return as-is
    return recommended_profile


# ─── Patch building ───────────────────────────────────────────────────────────


def build_setup_patch(
    recommended_profile: str,
    integration: str | None,
    hardware_summary: dict,
    paths_info: dict,
    config: dict,
) -> dict:
    """Build a dict describing what would be written to the user config.

    Pure function — does NOT write anything.

    Parameters
    ----------
    recommended_profile:
        The profile name recommended by detection.
    integration:
        Detected IDE integration name, or None.
    hardware_summary:
        Summary dict from hardware detection (GPU, CUDA, etc.).
    paths_info:
        Dict of relevant resolved paths.
    config:
        Current loaded configuration dict (used to compute changes).

    Returns
    -------
    dict
        Patch description with ``recommended_profile``, ``integration``,
        ``hardware_summary``, ``paths``, ``would_write``, ``config_path``,
        and ``changes`` list.
    """
    changes: list[str] = []

    # Resolve recommended profile against available profiles
    profiles = config.get("profiles", {})
    resolved = resolve_recommended_profile(recommended_profile, profiles)

    # Check if default_profile would change
    current_profile = config.get("default_profile")
    if current_profile != resolved:
        changes.append(f"default_profile: {current_profile!r} -> {resolved!r}")
        if resolved != recommended_profile:
            changes.append(f"resolved_profile: {recommended_profile!r} -> {resolved!r} (safe fallback)")

    # Check if setup_info would be added or updated
    existing_setup = config.get("setup_info")
    if existing_setup is None:
        changes.append("setup_info: added")
    else:
        changes.append("setup_info: updated")

    # Check if config is incomplete and would be recovered
    if not is_config_complete(config):
        changes.append("config recovery: incomplete config detected, will merge from packaged defaults")

    would_write = len(changes) > 0
    config_path = str(get_user_config_path())

    return {
        "recommended_profile": recommended_profile,
        "resolved_profile": resolved,
        "profile_exists": recommended_profile in profiles,
        "integration": integration,
        "hardware_summary": hardware_summary,
        "paths": paths_info,
        "would_write": would_write,
        "config_path": config_path,
        "changes": changes,
    }


def backup_config(config_path: Path | str) -> Path | None:
    """Create a timestamped backup of the config file.

    Parameters
    ----------
    config_path:
        Path to the config file to back up.

    Returns
    -------
    Path or None
        The backup path, or None if the config file does not exist.
    """
    config_path = Path(config_path)
    if not config_path.exists():
        return None

    timestamp = datetime.now().strftime("%Y%m%dT%H%M%S")
    backup_path = config_path.parent / f"{config_path.name}.bak.{timestamp}"
    shutil.copy2(config_path, backup_path)
    return backup_path


def write_setup_config(patch: dict, config_path: Path | str, reset: bool = False) -> dict:
    """Apply a setup patch to the user config file.

    Reads the existing config **or loads packaged defaults** (never starts
    from ``{}``), applies the patch, creates a backup if the file already
    exists, validates the result, and writes it as pretty-printed JSON.

    Parameters
    ----------
    patch:
        The patch dict produced by :func:`build_setup_patch`.
    config_path:
        Path to the config file to write.
    reset:
        If True, always start from packaged defaults regardless of existing
        user config.

    Returns
    -------
    dict
        Result with ``written``, ``config_path``, ``backup_path``,
        ``changes``, and ``recovery_needed``.
    """
    config_path = Path(config_path)

    # Load base config — NEVER start from {}
    recovery_needed = False
    recovery_reason = ""

    if config_path.exists() and not reset:
        with open(config_path) as f:
            config = json.load(f)
        backup_path = backup_config(config_path)

        if not is_config_complete(config):
            # Merge: start from defaults, overlay user config on top
            defaults = _load_packaged_defaults()
            recovery_needed = True
            recovery_reason = "user config incomplete — recovered from packaged defaults"
            # Preserve user customizations where possible
            _base = defaults.copy()
            _base.update(config)
            config = _base
    else:
        # No existing config or reset requested — start from packaged defaults
        config = _load_packaged_defaults()
        backup_path = None
        if reset and config_path.exists():
            backup_path = backup_config(config_path)
        recovery_needed = reset
        recovery_reason = "reset-user-config" if reset else "no user config found — initialized from packaged defaults"

    # Ensure parent directory exists
    config_path.parent.mkdir(parents=True, exist_ok=True)

    # Remove internal markers from defaults loading
    config.pop("_incomplete_fallback", None)

    # Apply patch — resolve and update default_profile
    recommended = patch.get("recommended_profile")
    resolved = patch.get("resolved_profile", recommended)
    profiles = config.get("profiles", {})

    # Resolve the profile name
    final_profile = resolve_recommended_profile(recommended, profiles)
    if config.get("default_profile") != final_profile:
        config["default_profile"] = final_profile

    # Write setup_info section with detection metadata
    config["setup_info"] = {
        "recommended_profile": recommended,
        "resolved_profile": final_profile,
        "integration": patch.get("integration"),
        "hardware_summary": patch.get("hardware_summary"),
        "paths": patch.get("paths"),
        "recovery_needed": recovery_needed,
        "recovery_reason": recovery_reason if recovery_needed else "",
        "written_at": datetime.now(timezone.utc).isoformat(),
    }

    # Remove transient markers
    config.pop("recovery_needed", None)
    config.pop("recovery_reason", None)

    # Validate before writing
    is_valid, errors = _validate_config_for_write(config)
    if not is_valid:
        return {
            "written": False,
            "config_path": str(config_path),
            "backup_path": str(backup_path) if backup_path else None,
            "changes": patch.get("changes", []),
            "recovery_needed": recovery_needed,
            "validation_errors": errors,
        }

    # Write config as JSON with indent=2 and trailing newline
    with open(config_path, "w") as f:
        json.dump(config, f, indent=2)
        f.write("\n")

    return {
        "written": True,
        "config_path": str(config_path),
        "backup_path": str(backup_path) if backup_path else None,
        "changes": patch.get("changes", []),
        "recovery_needed": recovery_needed,
    }


def preview_setup_changes(patch: dict, config_path: Path | str) -> dict:
    """Return a preview dict of what would be written, without writing.

    Includes: config_path, backup_path (if config exists), selected_profile,
    resolved_profile, integration, models_dir, state_dir, changes,
    requires_confirmation, user_config_complete, recovery_needed.

    Parameters
    ----------
    patch:
        The patch dict produced by :func:`build_setup_patch`.
    config_path:
        Path to the config file that would be written.

    Returns
    -------
    dict
        Preview dict describing what would change, without side effects.
    """
    config_path = Path(config_path)

    # Determine backup path (only if config already exists)
    backup_path = None
    if config_path.exists():
        timestamp = datetime.now().strftime("%Y%m%dT%H%M%S")
        backup_path = str(config_path.parent / f"{config_path.name}.bak.{timestamp}")

    paths_info = patch.get("paths", {})

    # Check if user config is complete
    user_config_complete = False
    if config_path.exists():
        try:
            with open(config_path) as f:
                existing = json.load(f)
            user_config_complete = is_config_complete(existing)
        except (json.JSONDecodeError, OSError):
            user_config_complete = False

    return {
        "config_path": str(config_path),
        "backup_path": backup_path,
        "selected_profile": patch.get("recommended_profile"),
        "resolved_profile": patch.get("resolved_profile"),
        "profile_exists": patch.get("profile_exists", False),
        "integration": patch.get("integration"),
        "models_dir": paths_info.get("models_dir"),
        "state_dir": paths_info.get("state_dir"),
        "changes": patch.get("changes", []),
        "requires_confirmation": len(patch.get("changes", [])) > 0,
        "user_config_complete": user_config_complete,
        "recovery_needed": not user_config_complete or not config_path.exists(),
    }


def apply_setup_changes(patch: dict, config_path: Path | str, reset: bool = False) -> dict:
    """Apply setup changes with atomic write (write .tmp then rename).

    Same as :func:`write_setup_config` but uses atomic write to prevent
    corruption.  Writes to a ``.tmp`` file first, then uses
    :func:`os.replace` for an atomic rename.

    Never starts from ``{}`` — always loads packaged defaults when no
    user config exists or when the existing config is incomplete.

    Parameters
    ----------
    patch:
        The patch dict produced by :func:`build_setup_patch`.
    config_path:
        Path to the config file to write.
    reset:
        If True, always start from packaged defaults regardless of existing
        user config.

    Returns
    -------
    dict
        Result with ``written``, ``config_path``, ``backup_path``,
        ``changes``, and ``recovery_needed``.
    """
    config_path = Path(config_path)

    # Load base config — NEVER start from {}
    recovery_needed = False
    recovery_reason = ""

    if config_path.exists() and not reset:
        with open(config_path) as f:
            config = json.load(f)
        backup_path = backup_config(config_path)

        if not is_config_complete(config):
            # Merge: start from defaults, overlay user config on top
            defaults = _load_packaged_defaults()
            recovery_needed = True
            recovery_reason = "user config incomplete — recovered from packaged defaults"
            _base = defaults.copy()
            _base.update(config)
            config = _base
    else:
        config = _load_packaged_defaults()
        backup_path = None
        if reset and config_path.exists():
            backup_path = backup_config(config_path)
        recovery_needed = reset
        recovery_reason = "reset-user-config" if reset else "no user config found — initialized from packaged defaults"

    # Ensure parent directory exists
    config_path.parent.mkdir(parents=True, exist_ok=True)

    # Remove internal markers from defaults loading
    config.pop("_incomplete_fallback", None)

    # Apply patch — resolve and update default_profile
    recommended = patch.get("recommended_profile")
    resolved = patch.get("resolved_profile", recommended)
    profiles = config.get("profiles", {})

    # Resolve the profile name
    final_profile = resolve_recommended_profile(recommended, profiles)
    if config.get("default_profile") != final_profile:
        config["default_profile"] = final_profile

    # Write setup_info section with detection metadata
    config["setup_info"] = {
        "recommended_profile": recommended,
        "resolved_profile": final_profile,
        "integration": patch.get("integration"),
        "hardware_summary": patch.get("hardware_summary"),
        "paths": patch.get("paths"),
        "recovery_needed": recovery_needed,
        "recovery_reason": recovery_reason if recovery_needed else "",
        "written_at": datetime.now(timezone.utc).isoformat(),
    }

    # Remove transient markers
    config.pop("recovery_needed", None)
    config.pop("recovery_reason", None)

    # Validate before writing
    is_valid, errors = _validate_config_for_write(config)
    if not is_valid:
        return {
            "written": False,
            "config_path": str(config_path),
            "backup_path": str(backup_path) if backup_path else None,
            "changes": patch.get("changes", []),
            "recovery_needed": recovery_needed,
            "validation_errors": errors,
        }

    # Atomic write: write to .tmp then os.replace()
    tmp_path = config_path.with_suffix(config_path.suffix + ".tmp")
    try:
        with open(tmp_path, "w") as f:
            json.dump(config, f, indent=2)
            f.write("\n")
        os.replace(str(tmp_path), str(config_path))
    except BaseException:
        # Clean up .tmp on failure
        if tmp_path.exists():
            tmp_path.unlink()
        raise

    return {
        "written": True,
        "config_path": str(config_path),
        "backup_path": str(backup_path) if backup_path else None,
        "changes": patch.get("changes", []),
        "recovery_needed": recovery_needed,
    }


def _validate_config_for_write(config: dict) -> tuple[bool, list[str]]:
    """Lightweight validation before writing config.

    Checks essential keys exist. Returns (is_valid, list_of_errors).
    """
    errors = []

    if not config:
        errors.append("config is empty")
        return False, errors

    if "version" not in config:
        errors.append("'version' is missing — config would be incomplete")

    profiles = config.get("profiles")
    if not profiles or not isinstance(profiles, dict) or len(profiles) == 0:
        errors.append("'profiles' is missing or empty — config would be incomplete")

    default = config.get("default_profile")
    if not default:
        errors.append("'default_profile' is missing")
    elif profiles and default not in profiles:
        errors.append(f"default_profile '{default}' not found in profiles")

    return len(errors) == 0, errors


def confirm_setup_write(preview: dict, yes: bool = False) -> bool:
    """Check if write should proceed.

    If *yes* is True, return True immediately.  If a TTY is available
    and *yes* is False, prompt the user for confirmation.  If no TTY
    and *yes* is False, return False (requires ``--yes`` in
    non-interactive mode).

    Parameters
    ----------
    preview:
        The preview dict from :func:`preview_setup_changes`.
    yes:
        Skip the confirmation prompt.

    Returns
    -------
    bool
        Whether the write should proceed.
    """
    if yes:
        return True

    if not preview.get("requires_confirmation", True):
        return True

    if sys.stdin.isatty():
        try:
            response = input("  Write these changes? [y/N] ").strip().lower()
            return response in ("y", "yes")
        except (EOFError, KeyboardInterrupt):
            return False
    else:
        # Non-interactive: refuse without --yes
        return False


def load_setup_summary(config_path: Path | str) -> dict | None:
    """Read config and return the setup_info section if present.

    Parameters
    ----------
    config_path:
        Path to the config file to read.

    Returns
    -------
    dict or None
        The ``setup_info`` section, or None if not found or file missing.
    """
    config_path = Path(config_path)
    if not config_path.exists():
        return None

    with open(config_path) as f:
        config = json.load(f)

    return config.get("setup_info")
