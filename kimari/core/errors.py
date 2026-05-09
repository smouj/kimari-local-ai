"""
Error pattern detection from llama-server logs.

Parses log files for known error patterns (OOM, CUDA errors, port conflicts, etc.)
and provides actionable solutions.
"""

from pathlib import Path

from kimari.core.constants import LOG_FILE

ERROR_PATTERNS = [
    {
        "pattern": "CUDA out of memory",
        "error_type": "OOM",
        "solution": "Use a lower quantization profile or reduce context size",
    },
    {
        "pattern": "no kernel image is available",
        "error_type": "CUDA_ERROR",
        "solution": "Rebuild llama.cpp with -DCMAKE_CUDA_ARCHITECTURES=native",
    },
    {
        "pattern": "failed to load model",
        "error_type": "MODEL_NOT_FOUND",
        "solution": "Verify the GGUF file is valid and not corrupted",
    },
    {
        "pattern": "unknown argument",
        "error_type": "LLAMA_CPP_ERROR",
        "solution": "Check llama.cpp version compatibility",
    },
    {
        "pattern": "address already in use",
        "error_type": "PORT_BUSY",
        "solution": "Stop the existing server with 'kimari stop' or change port",
    },
    {
        "pattern": "model architecture not supported",
        "error_type": "MODEL_NOT_FOUND",
        "solution": "Use a model compatible with this llama.cpp version",
    },
    {
        "pattern": "permission denied",
        "error_type": "PERMISSION_ERROR",
        "solution": "Check file permissions for the model and state directories",
    },
    {
        "pattern": "cannot allocate memory",
        "error_type": "OOM",
        "solution": "System RAM is low. Close other programs or reduce context size",
    },
]


def parse_log_errors(log_path: Path = LOG_FILE) -> dict | None:
    """Read kimari-server.log and detect known error patterns.

    Returns the first matched error dict with 'error_type', 'pattern', and 'solution',
    or None if no errors found.
    """
    if not log_path.exists():
        return None
    try:
        with open(log_path, encoding="utf-8", errors="replace") as f:
            content = f.read()
    except OSError:
        return None

    content_lower = content.lower()
    for entry in ERROR_PATTERNS:
        if entry["pattern"].lower() in content_lower:
            return {
                "error_type": entry["error_type"],
                "pattern": entry["pattern"],
                "solution": entry["solution"],
            }
    return None


def read_log_tail(log_path: Path = LOG_FILE, lines: int = 10) -> list:
    """Read the last N lines of a log file."""
    if not log_path.exists():
        return []
    try:
        with open(log_path, encoding="utf-8", errors="replace") as f:
            all_lines = f.readlines()
        return all_lines[-lines:]
    except OSError:
        return []
