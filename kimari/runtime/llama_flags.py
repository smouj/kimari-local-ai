"""
Llama-server flag detection and validation for Kimari.

Detects supported flags from llama-server --help output, validates
individual flags against the supported set, and filters command lists
to remove unsupported flags (including their values where applicable).

All subprocess calls are guarded with timeouts and exception handlers
so they never raise on missing binaries or slow execution.

Short flag aliases
------------------
llama-server uses both short (``-m``, ``-c``, ``-ngl``, etc.) and long
(``--model``, ``--ctx-size``, ``--n-gpu-layers``, etc.) forms.  The
``parse_supported_flags`` function extracts *both* from ``--help`` text,
and the ``SHORT_TO_LONG`` mapping ensures that a short flag in the
command list is recognised even if only the long form appeared in the
help output (and vice versa).
"""

import re
import subprocess

# ── Short ↔ Long flag aliases ────────────────────────────────────────────────
# Maps short flags to their canonical long form, so strict-flags
# correctly recognises both variants.

SHORT_TO_LONG: dict[str, str] = {
    "-m": "--model",
    "-c": "--ctx-size",
    "-ngl": "--n-gpu-layers",
    "-b": "--batch-size",
    "-ub": "--ubatch-size",
    "-t": "--threads",
}

LONG_TO_SHORT: dict[str, str] = {v: k for k, v in SHORT_TO_LONG.items()}

# Flags that take a value argument (the next item in the command list).
# All other `--` flags are treated as boolean (standalone).
FLAGS_WITH_VALUES: set[str] = {
    "--parallel",
    "--cache-type-k",
    "--cache-type-v",
    "--host",
    "--port",
    "--model",
    "--ctx-size",
    "--n-gpu-layers",
    "--batch-size",
    "--ubatch-size",
    "--threads",
    # Short forms
    "-t",
    "-b",
    "-ub",
    "-c",
    "-ngl",
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
    """Parse ``--help`` text to extract all supported flags (long and short).

    Scans each line for tokens that start with ``--`` (long) or ``-``
    followed by a letter (short), and collects them into a set.

    Handles the common help-text formatting:
    - ``--flag`` — boolean long flag
    - ``--flag VALUE`` — long flag with value
    - ``--flag=VALUE`` — inline value
    - ``-m FNAME, --model FNAME`` — short + long on same line
    - ``-c N, --ctx-size N`` — short + long on same line
    - ``--flash-attn`` — standalone boolean

    Also registers aliases via ``SHORT_TO_LONG`` / ``LONG_TO_SHORT``
    so that both ``-m`` and ``--model`` are in the returned set even
    if only one form appeared in the help text.

    Args:
        help_text: The raw stdout from ``llama-server --help``.

    Returns:
        A set of flag strings (e.g. ``{"--flash-attn", "--parallel", "-m", "--model"}``).
    """
    flags: set[str] = set()
    for line in help_text.splitlines():
        for token in line.split():
            # ── Long flags: --something ──────────────────────────────────
            if token.startswith("--"):
                clean = token.rstrip(",;]|)")
                if "=" in clean:
                    clean = clean.split("=")[0]
                if re.match(r"^--[a-zA-Z]", clean):
                    flags.add(clean)
                    # Register alias
                    if clean in LONG_TO_SHORT:
                        flags.add(LONG_TO_SHORT[clean])

            # ── Short flags: -x (single letter) or -xyz (multi-letter like -ngl) ──
            elif re.match(r"^-[a-zA-Z]", token):
                clean = token.rstrip(",;]|)")
                # Only register known short flags to avoid false positives
                # from help-text artefacts like "-v" meaning "verbose" etc.
                if clean in SHORT_TO_LONG:
                    flags.add(clean)
                    flags.add(SHORT_TO_LONG[clean])
    return flags


def supports_flag(flag: str, supported_flags: set[str]) -> bool:
    """Check whether a flag is in the supported set.

    Also checks via alias mapping so that ``-m`` matches ``--model``
    and vice versa.

    Args:
        flag: The flag to check (e.g. ``"--flash-attn"`` or ``"-m"``).
        supported_flags: The set returned by :func:`parse_supported_flags`.

    Returns:
        ``True`` if *flag* (or its alias) is present in *supported_flags*.
    """
    if flag in supported_flags:
        return True
    # Check alias
    alias = SHORT_TO_LONG.get(flag) or LONG_TO_SHORT.get(flag)
    return bool(alias and alias in supported_flags)


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
                if supports_flag(item, supported_flags):
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
                if supports_flag(item, supported_flags):
                    supported_cmd.append(item)
                else:
                    unsupported_flags.append(item)
        else:
            # Non-flag argument (binary path, model path, etc.) — always keep.
            supported_cmd.append(item)

        i += 1

    return supported_cmd, unsupported_flags
