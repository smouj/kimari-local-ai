"""Tests for error parsing from logs."""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from kimari.core.errors import parse_log_errors, read_log_tail  # noqa: E402


def test_parse_oom_error(tmp_path):
    """Detects CUDA out of memory in log."""
    log_file = tmp_path / "test.log"
    log_file.write_text("Some log line\nCUDA out of memory: cannot allocate\nAnother line")
    result = parse_log_errors(log_file)
    assert result is not None
    assert result["error_type"] == "OOM"
    assert "CUDA out of memory" in result["pattern"]


def test_parse_port_busy_error(tmp_path):
    """Detects port already in use in log."""
    log_file = tmp_path / "test.log"
    log_file.write_text("Server starting...\nError: address already in use :11435\n")
    result = parse_log_errors(log_file)
    assert result is not None
    assert result["error_type"] == "PORT_BUSY"


def test_parse_model_not_found_error(tmp_path):
    """Detects model not found in log."""
    log_file = tmp_path / "test.log"
    log_file.write_text("failed to load model from models/test.gguf\n")
    result = parse_log_errors(log_file)
    assert result is not None
    assert result["error_type"] == "MODEL_NOT_FOUND"


def test_parse_no_errors(tmp_path):
    """Returns None when no error patterns found."""
    log_file = tmp_path / "test.log"
    log_file.write_text("Server started successfully\nListening on 127.0.0.1:11435\n")
    result = parse_log_errors(log_file)
    assert result is None


def test_parse_missing_file():
    """Returns None when log file doesn't exist."""
    result = parse_log_errors(Path("/nonexistent/log.log"))
    assert result is None


def test_read_log_tail(tmp_path):
    """read_log_tail returns the last N lines."""
    log_file = tmp_path / "test.log"
    lines = [f"Line {i}\n" for i in range(20)]
    log_file.write_text("".join(lines))
    result = read_log_tail(log_file, 5)
    assert len(result) == 5
    assert "Line 19" in result[-1]
