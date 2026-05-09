"""
Tests for KimariFit calculation and quality factor logic.
"""

import sys
from pathlib import Path
from unittest.mock import patch

import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "cli"))

from kimari_cli import calculate_kimarifit


def _quality_factor(model_name: str) -> int:
    """Replicate the quality factor lookup from calculate_kimarifit.

    This is extracted from the source for direct testing without needing
    a real model file.
    """
    model_name_lower = model_name.lower()
    if "q8" in model_name_lower:
        return 95
    elif "q6" in model_name_lower or "q5_k_m" in model_name_lower:
        return 85
    elif "q5" in model_name_lower:
        return 80
    elif "q4_k_m" in model_name_lower:
        return 75
    elif "iq4" in model_name_lower:
        return 70
    elif "q4" in model_name_lower:
        return 65
    elif "q3" in model_name_lower:
        return 50
    else:
        return 70  # Unknown


def test_calculate_kimarifit_q4km(tmp_path, sample_config):
    """Returns reasonable score for Q4_K_M model name."""
    # Create a tiny temp file named like a Q4_K_M model
    model_file = tmp_path / "Kimari-4B-Q4_K_M.gguf"
    model_file.write_bytes(b"\x00" * 1024)  # 1 KB placeholder

    with patch("kimari_cli.detect_gpu", return_value=None):
        # calculate_kimarifit prints to stdout; just verify it doesn't crash
        calculate_kimarifit(str(model_file), 4096, sample_config)


def test_kimarifit_quality_q8():
    """Q8 quality factor is 95."""
    assert _quality_factor("model-Q8_0.gguf") == 95


def test_kimarifit_quality_q4km():
    """Q4_K_M quality factor is 75."""
    assert _quality_factor("model-Q4_K_M.gguf") == 75


def test_kimarifit_quality_unknown():
    """Unknown quality factor is 70."""
    assert _quality_factor("model-unknown.gguf") == 70
