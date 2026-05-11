"""
Kimari performance estimation module.

Pure functions for estimating VRAM, RAM, and recommending optimal
settings for local LLM inference on consumer NVIDIA GPUs.

All functions are side-effect-free: no network calls, no subprocess,
no model execution. Estimates are approximate and should be validated
against actual runtime behavior.
"""

from kimari.performance.benchmark_plan import (
    BenchmarkCell,
    BenchmarkPlan,
    generate_benchmark_plan,
    generate_tune_recommendation,
)
from kimari.performance.estimator import (
    estimate_ram_usage,
    estimate_vram_usage,
    vram_safe_budget,
)
from kimari.performance.gguf_metadata import read_gguf_metadata
from kimari.performance.recommender import (
    recommend_batch,
    recommend_context,
    recommend_gpu_layers,
    recommend_kv_cache,
    recommend_profile_settings,
)

__all__ = [
    # Estimation
    "estimate_vram_usage",
    "estimate_ram_usage",
    "vram_safe_budget",
    # Recommendation
    "recommend_context",
    "recommend_kv_cache",
    "recommend_batch",
    "recommend_gpu_layers",
    "recommend_profile_settings",
    # Metadata
    "read_gguf_metadata",
    # Benchmark Plan
    "BenchmarkCell",
    "BenchmarkPlan",
    "generate_benchmark_plan",
    "generate_tune_recommendation",
]
