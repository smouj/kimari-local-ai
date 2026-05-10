"""
Packaged default configuration files for Kimari.

Contains the default profiles, schema, and models registry that ship
inside the wheel.  At runtime, if no user-level config is found, these
defaults are copied to the user config directory.
"""

from importlib.resources import files as _pkg_files

_DEFAULTS_DIR = _pkg_files("kimari.defaults")


def get_defaults_dir() -> str:
    """Return the filesystem path to the ``kimari/defaults/`` package directory.

    Uses ``importlib.resources`` so it works both in an editable install
    (repo checkout) and in a wheel installed from PyPI.
    """
    # For Python >= 3.10, as_file gives a context manager but for
    # directories we just use the legacy location.
    try:
        return str(_DEFAULTS_DIR.locate(""))
    except (AttributeError, TypeError):
        # Fallback: compute from __file__
        from pathlib import Path

        return str(Path(__file__).resolve().parent)
