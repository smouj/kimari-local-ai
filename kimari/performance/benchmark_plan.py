"""
Benchmark plan generation for Kimari Local AI.

All functions are pure — no side effects, no network calls, no subprocess,
no model execution. Generates safe benchmark matrices and recommendations.

Benchmark plans are estimates, not measurements. Never present dry-run
output as real benchmark data.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


# ─── Context sizes to test ───────────────────────────────────────────
CONTEXT_SIZES = [2048, 4096, 8192]

# ─── Batch sizes to test ─────────────────────────────────────────────
BATCH_SIZES = [128, 256, 512]

# ─── Micro-batch sizes to test ───────────────────────────────────────
UBATCH_SIZES = [64, 128, 256]

# ─── Cache type combinations ─────────────────────────────────────────
CACHE_COMBOS = [
    ("f16", "f16"),
    ("q8_0", "f16"),
    ("q8_0", "q8_0"),
]

# ─── Flash attention options ─────────────────────────────────────────
FLASH_ATTN_OPTIONS = ["auto", "on", "off"]

# ─── GPU VRAM safe budgets (GiB) ─────────────────────────────────────
PROFILE_VRAM_BUDGETS: dict[str, float] = {
    "gtx1060-safe": 4.9,
    "gtx1080-balanced": 6.8,
    "ide-local": 4.9,
    "agent-local": 4.9,
}

# ─── Default model sizes per profile (GiB) ───────────────────────────
PROFILE_MODEL_SIZES: dict[str, float] = {
    "gtx1060-safe": 0.7,
    "gtx1080-balanced": 0.7,
    "ide-local": 0.7,
    "agent-local": 0.7,
}


@dataclass
class BenchmarkCell:
    """A single cell in the benchmark matrix."""

    ctx: int
    batch: int
    ubatch: int
    cache_type_k: str
    cache_type_v: str
    gpu_layers: str = "all"
    flash_attn: str = "auto"
    estimated_vram_gb: float = 0.0
    safe_for_profile: bool = False


@dataclass
class BenchmarkPlan:
    """A benchmark plan for a specific profile."""

    profile: str
    model_size_gb: float
    vram_budget_gb: float
    recommended: dict[str, Any] = field(default_factory=dict)
    matrix_cells: list[BenchmarkCell] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    measurement_type: str = "dry_run"
    measured: bool = False
    tokens_per_second: float | None = None
    ttft_ms: float | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON output."""
        return {
            "profile": self.profile,
            "model_size_gb": round(self.model_size_gb, 2),
            "vram_budget_gb": self.vram_budget_gb,
            "measurement_type": self.measurement_type,
            "plan": self.recommended,
            "matrix_cells": [
                {
                    "ctx": cell.ctx,
                    "batch": cell.batch,
                    "ubatch": cell.ubatch,
                    "cache_k": cell.cache_type_k,
                    "cache_v": cell.cache_type_v,
                    "gpu_layers": cell.gpu_layers,
                    "flash_attn": cell.flash_attn,
                    "estimated_vram_gb": round(cell.estimated_vram_gb, 2),
                    "safe_for_profile": cell.safe_for_profile,
                }
                for cell in self.matrix_cells
            ],
            "warnings": self.warnings,
            "measured": self.measured,
            "tokens_per_second": self.tokens_per_second,
            "ttft_ms": self.ttft_ms,
        }


def _estimate_cell_vram(
    model_size_gb: float,
    ctx: int,
    cache_type_k: str,
    cache_type_v: str,
    gpu_layers: str = "all",
) -> float:
    """Estimate VRAM usage for a benchmark cell.

    Uses simplified estimation:
        VRAM ≈ model * repack + kv_cache + overhead

    This is approximate. Real measurement is required for accurate numbers.
    """
    from kimari.performance.estimator import (
        _KV_DTYPE_FACTORS,
        _KV_PER_1K_TOKENS_GB,
    )

    # Model part
    offload_ratio = 1.0 if gpu_layers == "all" else 0.0
    model_gpu_part = model_size_gb * offload_ratio * 1.08

    # KV cache
    k_factor = _KV_DTYPE_FACTORS.get(cache_type_k, 1.0)
    v_factor = _KV_DTYPE_FACTORS.get(cache_type_v, 1.0)
    avg_factor = (k_factor + v_factor) / 2.0
    kv_cache = _KV_PER_1K_TOKENS_GB * (ctx / 1024) * avg_factor

    # Overheads
    compute_overhead = 0.35
    cuda_overhead = 0.45

    return model_gpu_part + kv_cache + compute_overhead + cuda_overhead


def generate_benchmark_plan(
    profile: str,
    model_size_gb: float | None = None,
    vram_budget_gb: float | None = None,
) -> BenchmarkPlan:
    """Generate a benchmark plan for a profile.

    Does NOT execute benchmarks. Returns estimated parameters only.

    Args:
        profile: Profile name (e.g., 'gtx1060-safe').
        model_size_gb: Model file size in GiB. If None, uses profile default.
        vram_budget_gb: VRAM safe budget in GiB. If None, uses profile default.

    Returns:
        BenchmarkPlan with recommended settings and full matrix.
    """
    _model_size = model_size_gb or PROFILE_MODEL_SIZES.get(profile, 0.7)
    _vram_budget = vram_budget_gb or PROFILE_VRAM_BUDGETS.get(profile, 4.9)

    # Generate best recommendation (conservative/safe)
    best_ctx = 4096
    best_batch = 256
    best_ubatch = 128
    best_cache_k = "q8_0"
    best_cache_v = "q8_0"

    # Check if we can go higher
    for ctx in [8192, 4096, 2048]:
        est = _estimate_cell_vram(_model_size, ctx, "q8_0", "q8_0")
        if est <= _vram_budget:
            best_ctx = ctx
            break

    best_estimated_vram = _estimate_cell_vram(_model_size, best_ctx, best_cache_k, best_cache_v)

    from kimari.performance.estimator import estimate_ram_usage

    ram_est = estimate_ram_usage(
        model_size_gb=_model_size,
        gpu_layers="all",
        total_layers=32,
    )

    recommended = {
        "recommended_ctx": best_ctx,
        "recommended_batch": best_batch,
        "recommended_ubatch": best_ubatch,
        "recommended_cache_type_k": best_cache_k,
        "recommended_cache_type_v": best_cache_v,
        "estimated_vram_gb": round(best_estimated_vram, 2),
        "estimated_ram_gb": round(ram_est["expected_ram_gb"], 2),
    }

    # Generate matrix cells
    cells: list[BenchmarkCell] = []
    for ctx in CONTEXT_SIZES:
        for batch in BATCH_SIZES:
            for ubatch in UBATCH_SIZES:
                if ubatch > batch:
                    continue
                for cache_k, cache_v in CACHE_COMBOS:
                    est_vram = _estimate_cell_vram(_model_size, ctx, cache_k, cache_v)
                    cells.append(
                        BenchmarkCell(
                            ctx=ctx,
                            batch=batch,
                            ubatch=ubatch,
                            cache_type_k=cache_k,
                            cache_type_v=cache_v,
                            gpu_layers="all",
                            flash_attn="auto",
                            estimated_vram_gb=est_vram,
                            safe_for_profile=est_vram <= _vram_budget,
                        )
                    )

    # Warnings
    warnings: list[str] = []
    if best_estimated_vram > _vram_budget:
        warnings.append(
            f"Recommended settings may exceed VRAM budget ({best_estimated_vram:.2f} > {_vram_budget:.1f} GiB)"
        )
    warnings.append(
        "These are estimates, not measurements. Use 'kimari benchmark --measure' for real data."
    )

    return BenchmarkPlan(
        profile=profile,
        model_size_gb=_model_size,
        vram_budget_gb=_vram_budget,
        recommended=recommended,
        matrix_cells=cells,
        warnings=warnings,
        measurement_type="dry_run",
        measured=False,
        tokens_per_second=None,
        ttft_ms=None,
    )


def generate_tune_recommendation(
    profile: str,
    model_size_gb: float | None = None,
    vram_budget_gb: float | None = None,
) -> dict[str, Any]:
    """Generate a tune recommendation for a profile.

    Uses the existing performance estimator to recommend settings.
    Does NOT apply changes or execute benchmarks.

    Args:
        profile: Profile name.
        model_size_gb: Model file size in GiB.
        vram_budget_gb: VRAM safe budget in GiB.

    Returns:
        Dictionary with recommendation and disclaimer.
    """
    from kimari.performance import recommend_profile_settings

    _model_size = model_size_gb or PROFILE_MODEL_SIZES.get(profile, 0.7)
    _vram_budget = vram_budget_gb or PROFILE_VRAM_BUDGETS.get(profile, 4.9)

    # Get recommendation for safe mode (most conservative)
    settings = recommend_profile_settings(_vram_budget, _model_size, "safe")

    return {
        "profile": profile,
        "recommendation_type": "estimated",
        "recommended": {
            "ctx": settings["ctx"],
            "batch": settings["batch"],
            "ubatch": settings["ubatch"],
            "cache_type_k": settings["cache_type_k"],
            "cache_type_v": settings["cache_type_v"],
            "gpu_layers": settings["gpu_layers"],
            "flash_attn": settings["flash_attn"],
        },
        "estimates": {
            "vram_gb": round(settings["expected_vram_gb"], 2),
            "ram_gb": round(settings["expected_ram_gb"], 2),
            "confidence": settings["confidence"],
        },
        "disclaimer": (
            "These are estimates based on the VRAM/RAM model, not measured benchmarks. "
            "Use 'kimari benchmark --measure' for real performance data."
        ),
        "warnings": settings["warnings"],
        "apply_blocked": True,
        "apply_blocked_reason": (
            "--apply is not yet available. Use --dry-run to see recommendations. "
            "Measured benchmark support is planned for v0.1.26-alpha."
        ),
    }
