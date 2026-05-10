"""
Llama-server flag detection and validation for Kimari.

Detects supported flags from llama-server --help output, validates
individual flags against the supported set, and filters command lists
to remove unsupported flags (including their values where applicable).

All subprocess calls are guarded with timeouts and exception handlers
so they never raise on missing binaries or slow execution.
"""

import re
import subprocess

# Flags that take a value argument (the next item in the command list).
# All other `--` flags are treated as boolean (standalone).
FLAGS_WITH_VALUES: set[str] = {
    "--parallel",
    "--cache-type-k",
    "--cache-type-v",
    "-t",
    "-b",
    "-ub",
    "-c",
    "-ngl",
    "--host",
    "--port",
    "-m",
}


def detect_llama_server_help(binary_path: str) -> str:
    """Run ``llama-server --help`` and return its stdout text.

    Args:
        binary_path: Absolute or relative path to the llama-server binary.

    Returns:
        The stdout text from ``--help``, or an empty string if the binary
        does not exist, times out (10 s), or returns a non-zero exit code.
    """
    try:
        result = subprocess.run(
            [binary_path, "--help"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result.returncode == 0:
            return result.stdout
        # Some builds emit help on stderr; try to capture it anyway.
        if result.stderr and not result.stdout:
            return result.stderr
        return result.stdout
    except FileNotFoundError:
        return ""
    except subprocess.TimeoutExpired:
        return ""
    except OSError:
        return ""


def detect_llama_server_version(binary_path: str) -> str:
    """Run ``llama-server --version`` and return its stdout text.

    Args:
        binary_path: Absolute or relative path to the llama-server binary.

    Returns:
        The stdout text from ``--version``, or an empty string if the binary
        does not exist, times out (10 s), or returns a non-zero exit code.
    """
    try:
        result = subprocess.run(
            [binary_path, "--version"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result.returncode == 0:
            return result.stdout
        # Some builds emit version on stderr.
        if result.stderr and not result.stdout:
            return result.stderr
        return result.stdout
    except FileNotFoundError:
        return ""
    except subprocess.TimeoutExpired:
        return ""
    except OSError:
        return ""


def parse_supported_flags(help_text: str) -> set[str]:
    """Parse ``--help`` text to extract all supported flags.

    Scans each line for tokens that start with ``--`` and collects them
    into a set.  Handles the common help-text formatting where a flag
    may appear as ``--flag``, ``--flag VALUE``, or ``--flag=VALUE`` —
    only the ``--flag`` portion is retained.

    Args:
        help_text: The raw stdout from ``llama-server --help``.

    Returns:
        A set of flag strings (e.g. ``{"--flash-attn", "--parallel", "--mlock"}``).
    """
    flags: set[str] = set()
    for line in help_text.splitlines():
        # Find all tokens starting with '--' on this line.
        for token in line.split():
            if token.startswith("--"):
                # Strip trailing punctuation (commas, brackets, etc.)
                clean = token.rstrip(",;]|)")
                # Strip inline value (e.g. --flag=VALUE → --flag)
                if "=" in clean:
                    clean = clean.split("=")[0]
                # Only keep if it looks like a genuine flag (letters/hyphens after --)
                if re.match(r"^--[a-zA-Z]", clean):
                    flags.add(clean)
    return flags


def supports_flag(flag: str, supported_flags: set[str]) -> bool:
    """Check whether a flag is in the supported set.

    Args:
        flag: The flag to check (e.g. ``"--flash-attn"``).
        supported_flags: The set returned by :func:`parse_supported_flags`.

    Returns:
        ``True`` if *flag* is present in *supported_flags*, ``False`` otherwise.
    """
    return flag in supported_flags


def filter_unsupported_flags(cmd: list[str], supported_flags: set[str]) -> tuple[list[str], list[str]]:
    """Filter a command list, removing unsupported flags and their values.

    Given a command-line argument list (e.g. ``["llama-server", "-m", "model.gguf",
    "--flash-attn", "--parallel", "2"]``), returns a tuple of:

    1. **supported_cmd** — the command list with unsupported flags (and their
       value arguments, if applicable) removed.
    2. **unsupported_flags** — a list of flag names that were present in *cmd*
       but not in *supported_flags*.

    Flags with values are defined in :data:`FLAGS_WITH_VALUES`.  All other ``--``
    flags are assumed to be boolean (standalone).  Short flags (single ``-``)
    listed in :data:`FLAGS_WITH_VALUES` are also handled correctly.

    Args:
        cmd: The full command argument list.
        supported_flags: The set returned by :func:`parse_supported_flags`.

    Returns:
        A ``(supported_cmd, unsupported_flags)`` tuple.
    """
    supported_cmd: list[str] = []
    unsupported_flags: list[str] = []
    skip_next = False

    i = 0
    while i < len(cmd):
        item = cmd[i]

        # If the previous item was an unsupported flag-with-value, skip this value.
        if skip_next:
            skip_next = False
            i += 1
            continue

        # Check if this item is a flag (-- or - prefix).
        if item.startswith("-"):
            is_known_with_value = item in FLAGS_WITH_VALUES

            if is_known_with_value:
                # It's a flag that takes a value.
                if item in supported_flags:
                    # Supported — keep flag and its value.
                    supported_cmd.append(item)
                    if i + 1 < len(cmd) and not cmd[i + 1].startswith("-"):
                        i += 1
                        supported_cmd.append(cmd[i])
                else:
                    # Unsupported — discard flag and its value.
                    unsupported_flags.append(item)
                    # Mark next item for skipping (if it's a value, not another flag).
                    if i + 1 < len(cmd) and not cmd[i + 1].startswith("-"):
                        skip_next = True
            else:
                # Boolean flag (or unknown short flag not in FLAGS_WITH_VALUES).
                if item in supported_flags:
                    supported_cmd.append(item)
                else:
                    unsupported_flags.append(item)
        else:
            # Non-flag argument (binary path, model path, etc.) — always keep.
            supported_cmd.append(item)

        i += 1

    return supported_cmd, unsupported_flags
