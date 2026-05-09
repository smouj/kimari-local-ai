"""
Tests for Kimari log error parsing.
"""

import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "cli"))

from kimari_cli import parse_log_errors


def test_parse_log_errors_oom(tmp_path):
    """Detects 'CUDA out of memory' in log."""
    log_file = tmp_path / "test.log"
    log_file.write_text("llama_model_load: loading model\nCUDA out of memory: no more VRAM\n")

    result = parse_log_errors(log_file)
    assert result is not None
    assert result["error_type"] == "OOM"
    assert "CUDA out of memory" in result["pattern"]


def test_parse_log_errors_port_busy(tmp_path):
    """Detects 'address already in use' in log."""
    log_file = tmp_path / "test.log"
    log_file.write_text("bind: address already in use (errno 98)\n")

    result = parse_log_errors(log_file)
    assert result is not None
    assert result["error_type"] == "PORT_BUSY"


def test_parse_log_errors_model_not_found(tmp_path):
    """Detects 'failed to load model' in log."""
    log_file = tmp_path / "test.log"
    log_file.write_text("error: failed to load model from models/test.gguf\n")

    result = parse_log_errors(log_file)
    assert result is not None
    assert result["error_type"] == "MODEL_NOT_FOUND"


def test_parse_log_errors_no_file(tmp_path):
    """Returns None when log file doesn't exist."""
    log_file = tmp_path / "nonexistent.log"
    result = parse_log_errors(log_file)
    assert result is None


def test_parse_log_errors_empty_log(tmp_path):
    """Returns None for empty log file."""
    log_file = tmp_path / "empty.log"
    log_file.write_text("")

    result = parse_log_errors(log_file)
    assert result is None
