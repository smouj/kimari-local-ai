"""
Terminal color helpers for Kimari CLI.
"""

import sys


class Color:
    """ANSI color codes for terminal output."""

    RESET = "\033[0m"
    BOLD = "\033[1m"
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    MAGENTA = "\033[95m"
    CYAN = "\033[96m"
    DIM = "\033[2m"
    WHITE = "\033[97m"


def supports_color() -> bool:
    """Check if the terminal supports color output."""
    if not hasattr(sys.stdout, "isatty"):
        return False
    if not sys.stdout.isatty():
        return False
    if sys.platform == "win32":
        return True  # Assume modern Windows
    return True


def ok(msg: str):
    """Print a success message."""
    print(f"  {Color.GREEN}[OK]{Color.RESET}   {msg}")


def warn(msg: str):
    """Print a warning message."""
    print(f"  {Color.YELLOW}[WARN]{Color.RESET} {msg}")


def fail(msg: str):
    """Print a failure message."""
    print(f"  {Color.RED}[FAIL]{Color.RESET} {msg}")


def info(msg: str):
    """Print an informational message."""
    print(f"  {Color.CYAN}[INFO]{Color.RESET} {msg}")
