"""
Tests for Kimari system detection functions.
"""

import os
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "cli"))

from kimari_cli import detect_cuda, detect_gpu, detect_llama_server, is_port_free


def test_detect_llama_server_returns_none_when_not_found():
    """No llama-server available returns None."""
    with patch("kimari_cli.shutil.which", return_value=None), \
         patch.dict(os.environ, {}, clear=True):
        result = detect_llama_server()
        # Even without any env vars or PATH hits, it still checks file paths
        # In CI/container envs without llama-server, this should return None
        assert result is None


def test_detect_llama_server_with_env_var():
    """LLAMA_SERVER env var pointing to non-existent file returns None."""
    with patch.dict(os.environ, {"LLAMA_SERVER": "/nonexistent/path/llama-server"}):
        result = detect_llama_server()
        # The env var path doesn't exist, so it should fall through
        # and return None (in environments without llama-server)
        assert result is None


def test_detect_cuda_without_nvcc():
    """Returns False when no nvcc/nvidia-smi are available."""
    with patch("kimari_cli.shutil.which", return_value=None):
        result = detect_cuda()
        assert result is False


def test_is_port_free_typically():
    """A high random port should be free (or at least not crash)."""
    # Use a high port that's very unlikely to be in use
    result = is_port_free("127.0.0.1", 59999)
    # We just verify it doesn't crash and returns a bool
    assert isinstance(result, bool)


def test_detect_gpu_without_nvidia_smi():
    """Returns None when no nvidia-smi is available."""
    with patch("kimari_cli.subprocess.run", side_effect=FileNotFoundError):
        result = detect_gpu()
        assert result is None
