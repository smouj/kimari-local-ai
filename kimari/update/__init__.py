"""
Kimari Local AI — Update check module.

Provides version introspection and update checking for Kimari.
Offline by default; online checks require explicit opt-in.
Never auto-updates or installs anything.
"""

from kimari.update.check import (
    build_update_report,
    check_update_sources,
    get_current_version,
    parse_version,
)

__all__ = [
    "get_current_version",
    "parse_version",
    "check_update_sources",
    "build_update_report",
]
