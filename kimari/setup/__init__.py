"""
Kimari setup persistence module.

Provides functions for persisting detected setup configuration
to the user config directory, with backup support.
"""

from kimari.setup.writer import backup_config, build_setup_patch, load_setup_summary, write_setup_config

__all__ = ["build_setup_patch", "write_setup_config", "backup_config", "load_setup_summary"]
