#!/usr/bin/env python3
"""
Kimari CLI — Backward-compatible entry point.

This file is kept for backward compatibility with `python cli/kimari_cli.py`.
The main CLI is now in the `kimari` package: `kimari.cli.main:main`.

New entry point: `kimari` (via pip install)
Legacy entry point: `python cli/kimari_cli.py`
"""

import sys
from pathlib import Path

# Add project root to path so the kimari package can be found
_project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_project_root))

from kimari.cli.main import main  # noqa: E402

if __name__ == "__main__":
    main()
