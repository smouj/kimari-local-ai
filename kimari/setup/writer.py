"""
Setup configuration persistence for Kimari.

Builds patches from detected hardware/software information, creates backups,
and writes the setup_info section into the user config file.
"""

import json
import os
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

from kimari.core.paths import get_user_config_path


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

    # Check if default_profile would change
    current_profile = config.get("default_profile")
    if current_profile != recommended_profile:
        changes.append(f"default_profile: {current_profile!r} -> {recommended_profile!r}")

    # Check if setup_info would be added or updated
    existing_setup = config.get("setup_info")
    if existing_setup is None:
        changes.append("setup_info: added")
    else:
        changes.append("setup_info: updated")

    would_write = len(changes) > 0
    config_path = str(get_user_config_path())

    return {
        "recommended_profile": recommended_profile,
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


def write_setup_config(patch: dict, config_path: Path | str) -> dict:
    """Apply a setup patch to the user config file.

    Reads the existing config (or starts from an empty dict), applies the
    patch, creates a backup if the file already exists, and writes the
    result as pretty-printed JSON.

    Parameters
    ----------
    patch:
        The patch dict produced by :func:`build_setup_patch`.
    config_path:
        Path to the config file to write.

    Returns
    -------
    dict
        Result with ``written``, ``config_path``, ``backup_path``, and
        ``changes``.
    """
    config_path = Path(config_path)

    # Read existing config or start fresh
    if config_path.exists():
        with open(config_path) as f:
            config = json.load(f)
        backup_path = backup_config(config_path)
    else:
        config = {}
        backup_path = None
        # Ensure parent directory exists
        config_path.parent.mkdir(parents=True, exist_ok=True)

    # Apply patch — update default_profile if changed
    recommended = patch.get("recommended_profile")
    if recommended is not None and config.get("default_profile") != recommended:
        config["default_profile"] = recommended

    # Write setup_info section with detection metadata
    config["setup_info"] = {
        "recommended_profile": patch.get("recommended_profile"),
        "integration": patch.get("integration"),
        "hardware_summary": patch.get("hardware_summary"),
        "paths": patch.get("paths"),
        "written_at": datetime.now(timezone.utc).isoformat(),
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
    }


def preview_setup_changes(patch: dict, config_path: Path | str) -> dict:
    """Return a preview dict of what would be written, without writing.

    Includes: config_path, backup_path (if config exists), selected_profile,
    integration, models_dir, state_dir, changes, requires_confirmation.

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

    return {
        "config_path": str(config_path),
        "backup_path": backup_path,
        "selected_profile": patch.get("recommended_profile"),
        "integration": patch.get("integration"),
        "models_dir": paths_info.get("models_dir"),
        "state_dir": paths_info.get("state_dir"),
        "changes": patch.get("changes", []),
        "requires_confirmation": len(patch.get("changes", [])) > 0,
    }


def apply_setup_changes(patch: dict, config_path: Path | str) -> dict:
    """Apply setup changes with atomic write (write .tmp then rename).

    Same as :func:`write_setup_config` but uses atomic write to prevent
    corruption.  Writes to a ``.tmp`` file first, then uses
    :func:`os.replace` for an atomic rename.

    Parameters
    ----------
    patch:
        The patch dict produced by :func:`build_setup_patch`.
    config_path:
        Path to the config file to write.

    Returns
    -------
    dict
        Result with ``written``, ``config_path``, ``backup_path``, and
        ``changes``.
    """
    config_path = Path(config_path)

    # Read existing config or start fresh
    if config_path.exists():
        with open(config_path) as f:
            config = json.load(f)
        backup_path = backup_config(config_path)
    else:
        config = {}
        backup_path = None
        # Ensure parent directory exists
        config_path.parent.mkdir(parents=True, exist_ok=True)

    # Apply patch — update default_profile if changed
    recommended = patch.get("recommended_profile")
    if recommended is not None and config.get("default_profile") != recommended:
        config["default_profile"] = recommended

    # Write setup_info section with detection metadata
    config["setup_info"] = {
        "recommended_profile": patch.get("recommended_profile"),
        "integration": patch.get("integration"),
        "hardware_summary": patch.get("hardware_summary"),
        "paths": patch.get("paths"),
        "written_at": datetime.now(timezone.utc).isoformat(),
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
    }


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
