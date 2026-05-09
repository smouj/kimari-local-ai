"""
Tests for system detection functions.
"""

import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from kimari.core.detection import detect_cuda, detect_gpu, detect_llama_server, is_port_free, recommend_profile


def test_detect_cuda_without_tools():
    """detect_cuda returns False when nvcc and nvidia-smi are not in PATH."""
    with patch("shutil.which", return_value=None):
        assert detect_cuda() is False


def test_detect_cuda_with_nvcc():
    """detect_cuda returns True when nvcc is in PATH."""
    with patch("shutil.which", side_effect=lambda x: "/usr/bin/nvcc" if x == "nvcc" else None):
        assert detect_cuda() is True


def test_detect_gpu_without_nvidia_smi():
    """detect_gpu returns None when nvidia-smi is not available."""
    with patch("subprocess.run", side_effect=FileNotFoundError):
        assert detect_gpu() is None


def test_detect_gpu_with_valid_output():
    """detect_gpu returns GPU info when nvidia-smi succeeds."""
    mock_result = MagicMock()
    mock_result.returncode = 0
    mock_result.stdout = "NVIDIA GeForce GTX 1060 6GB, 6144, 535.104.05\n"
    with patch("subprocess.run", return_value=mock_result):
        gpu = detect_gpu()
        assert gpu is not None
        assert "GTX 1060" in gpu["name"]
        assert gpu["vram_mb"] == 6144


def test_detect_llama_server_not_found():
    """detect_llama_server returns None when no binary is found."""
    with patch.dict("os.environ", {}, clear=True):
        with patch("shutil.which", return_value=None):
            with patch.object(Path, "exists", return_value=False):
                assert detect_llama_server() is None


def test_is_port_free_with_unused_port():
    """is_port_free returns True for an unused port."""
    assert is_port_free("127.0.0.1", 59999) is True


def test_recommend_profile_no_gpu(sample_config):
    """recommend_profile returns default profile when no GPU detected."""
    assert recommend_profile(sample_config, None) == "test"


def test_recommend_profile_8gb_vram(sample_config):
    """recommend_profile returns gtx1080 for 8GB VRAM."""
    gpu = {"name": "Generic GPU", "vram_mb": 8192, "driver": "535.0"}
    assert recommend_profile(sample_config, gpu) == "gtx1080"


def test_recommend_profile_6gb_vram(sample_config):
    """recommend_profile returns gtx1060 for 6GB VRAM."""
    gpu = {"name": "Generic GPU", "vram_mb": 6144, "driver": "535.0"}
    assert recommend_profile(sample_config, gpu) == "gtx1060"


def test_recommend_profile_by_name(sample_config):
    """recommend_profile matches by GPU name containing profile key."""
    gpu = {"name": "NVIDIA GeForce GTX 1080 8GB", "vram_mb": 8192, "driver": "535.0"}
    assert recommend_profile(sample_config, gpu) == "gtx1080"
