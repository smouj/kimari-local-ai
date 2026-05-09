"""
Tests for KimariFit score calculation.
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from kimari.benchmarks.kimarifit import quality_factor


def test_quality_factor_q8():
    """Q8 quantization gets highest quality score."""
    assert quality_factor("model-q8_0.gguf") == 95


def test_quality_factor_q4km():
    """Q4_K_M gets 75 quality score."""
    assert quality_factor("model-q4_k_m.gguf") == 75


def test_quality_factor_q5km():
    """Q5_K_M gets 85 quality score."""
    assert quality_factor("model-q5_k_m.gguf") == 85


def test_quality_factor_iq4():
    """IQ4_XS gets 70 quality score."""
    assert quality_factor("model-iq4_xs.gguf") == 70


def test_quality_factor_unknown():
    """Unknown quantization gets 70 default score."""
    assert quality_factor("model.gguf") == 70


def test_quality_factor_q3():
    """Q3 gets 50 quality score."""
    assert quality_factor("model-q3_k_s.gguf") == 50
