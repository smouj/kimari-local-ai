"""
Kimari Local AI — Update check functions.

Provides version introspection, remote update checking, and report building.
Offline by default; online checks require explicit opt-in via ``online=True``.
This module NEVER auto-updates or installs anything.
"""

from __future__ import annotations

import re
from typing import Any

import kimari

_GITHUB_TAGS_URL = "https://api.github.com/repos/smouj/kimari-local-ai/tags"
_HTTP_TIMEOUT_SECONDS = 10


def get_current_version() -> str:
    """Return the current Kimari version string from ``kimari.__version__``."""
    return kimari.__version__


def parse_version(version_str: str) -> dict[str, Any]:
    """Parse a version string like ``"0.1.26-alpha"`` into its components.

    Returns a dict with keys ``major``, ``minor``, ``patch``, ``pre``, and ``full``.
    If no pre-release suffix is present, ``pre`` is ``None``.
    """
    match = re.match(r"^(\d+)\.(\d+)\.(\d+)(?:-([a-zA-Z0-9.]+))?$", version_str)
    if not match:
        return {
            "major": None,
            "minor": None,
            "patch": None,
            "pre": None,
            "full": version_str,
        }

    return {
        "major": int(match.group(1)),
        "minor": int(match.group(2)),
        "patch": int(match.group(3)),
        "pre": match.group(4),
        "full": version_str,
    }


def check_update_sources(online: bool = False) -> dict[str, Any]:
    """Check for available updates.

    Parameters
    ----------
    online : bool
        If ``False`` (default), returns an offline status without making any
        network requests.  If ``True``, attempts to query the GitHub API for
        the latest release tag.

    Returns
    -------
    dict
        Status dictionary with ``current_version``, ``latest_github_tag``,
        ``pypi_available``, ``update_available``, ``recommended_action``,
        and ``online`` keys.

    Notes
    -----
    This function NEVER auto-updates or installs anything.
    """
    current = get_current_version()

    if not online:
        return {
            "current_version": current,
            "latest_github_tag": None,
            "pypi_available": None,
            "update_available": None,
            "recommended_action": "Use --online to check for updates",
            "online": False,
        }

    # --- Online check ---------------------------------------------------
    latest_tag: str | None = None
    try:
        import requests  # lazy import so offline use never requires requests

        resp = requests.get(_GITHUB_TAGS_URL, timeout=_HTTP_TIMEOUT_SECONDS)
        resp.raise_for_status()
        tags = resp.json()
        if isinstance(tags, list) and len(tags) > 0:
            latest_tag = tags[0].get("name")
    except Exception:
        return {
            "current_version": current,
            "latest_github_tag": None,
            "pypi_available": None,
            "update_available": None,
            "recommended_action": "Failed to reach GitHub API. Check network or try later.",
            "online": True,
        }

    # Compare versions
    update_available = False
    recommended_action = "No update required"

    if latest_tag:
        # Strip leading 'v' for comparison
        tag_version = latest_tag.lstrip("v")
        parsed_current = parse_version(current)
        parsed_remote = parse_version(tag_version)

        if parsed_remote.get("major") is not None and parsed_current.get("major") is not None:
            remote_tuple = (
                parsed_remote["major"],
                parsed_remote["minor"],
                parsed_remote["patch"],
            )
            current_tuple = (
                parsed_current["major"],
                parsed_current["minor"],
                parsed_current["patch"],
            )
            if remote_tuple > current_tuple:
                update_available = True
                recommended_action = "Update available"

    return {
        "current_version": current,
        "latest_github_tag": latest_tag,
        "pypi_available": False,
        "update_available": update_available,
        "recommended_action": recommended_action,
        "online": True,
    }


def build_update_report(online: bool = False) -> dict[str, Any]:
    """Build a full update report combining version info and source checks.

    Parameters
    ----------
    online : bool
        Passed through to :func:`check_update_sources`.

    Returns
    -------
    dict
        Complete report with current version, parsed version, GitHub tag,
        PyPI availability, update status, and policy notes.
    """
    current = get_current_version()
    parsed = parse_version(current)
    sources = check_update_sources(online=online)

    return {
        "current_version": current,
        "parsed_version": parsed,
        "latest_github_tag": sources["latest_github_tag"],
        "pypi_available": sources["pypi_available"] or False,
        "update_available": sources["update_available"] or False,
        "recommended_action": sources["recommended_action"],
        "online": sources["online"],
        "auto_update": False,
        "note": "Kimari does not auto-update. Use pip install --upgrade or git pull.",
    }
