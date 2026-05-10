"""
Settings recommendation functions for Kimari.

All functions are pure — no side effects, no network calls, no subprocess.
Recommendations are heuristic-based approximations and should be validated
against actual runtime behavior.
"""

from kimari.performance.estimator import (
    estimate_ram_usage,
    estimate_vram_usage,
    vram_safe_budget,
)


def recommend_context(
    vram_total_gb: float,
    model_size_gb: float,
    cache_type_k: str = "q8_0",
) -> dict:
    """Recommend a context size based on available VRAM and model size.

    Tries context sizes from largest to smallest and picks the largest
    that fits within the safe VRAM budget. Uses default total_layers=32
    and assumes full GPU offload for a conservative estimate.

    Args:
        vram_total_gb: Total GPU VRAM in GiB.
        model_size_gb: Model file size in GiB.
        cache_type_k: KV cache key dtype (affects cache size).

    Returns:
        dict with keys:
            ctx (int): Recommended context size in tokens.
            reasoning (str): Explanation of the recommendation.
            tried_sizes (list[int]): Context sizes that were evaluated.
    """
    safe = vram_safe_budget(vram_total_gb)
    # Candidate context sizes (descending)
    candidates = [32768, 16384, 8192, 4096, 2048, 1024]

    # Assume full offload with 32 layers for the estimate
    default_layers = 32
    tried: list[int] = []

    for ctx in candidates:
        tried.append(ctx)
        est = estimate_vram_usage(
            model_size_gb=model_size_gb,
            gpu_layers="all",
            total_layers=default_layers,
            ctx_size=ctx,
            cache_type_k=cache_type_k,
        )
        if est["expected_vram_gb"] <= safe:
            reasoning = (
                f"Context {ctx} fits in safe VRAM budget ({safe:.2f} GiB); "
                f"estimated usage {est['expected_vram_gb']:.2f} GiB"
            )
            return {
                "ctx": ctx,
                "reasoning": reasoning,
                "tried_sizes": tried,
            }

    # Fallback: smallest context
    reasoning = (
        f"Even ctx=1024 may not fit in safe VRAM budget ({safe:.2f} GiB); "
        f"use minimal context and consider a smaller model or quantization"
    )
    return {
        "ctx": 1024,
        "reasoning": reasoning,
        "tried_sizes": tried,
    }


def recommend_kv_cache(
    vram_total_gb: float,
    model_size_gb: float,
) -> dict:
    """Recommend KV cache types based on available VRAM and model size.

    Tight VRAM → quantized cache (q8_0) to save memory.
    Comfortable VRAM → f16 for best quality.

    Args:
        vram_total_gb: Total GPU VRAM in GiB.
        model_size_gb: Model file size in GiB.

    Returns:
        dict with keys:
            cache_type_k (str): Recommended key cache dtype.
            cache_type_v (str): Recommended value cache dtype.
            reasoning (str): Explanation of the recommendation.
    """
    safe = vram_safe_budget(vram_total_gb)

    # Estimate model footprint with full offload and moderate context
    est = estimate_vram_usage(
        model_size_gb=model_size_gb,
        gpu_layers="all",
        total_layers=32,
        ctx_size=4096,
        cache_type_k="f16",
        cache_type_v="f16",
    )

    headroom = safe - est["expected_vram_gb"]

    if headroom >= 1.5:
        # Comfortable: use f16 for quality
        return {
            "cache_type_k": "f16",
            "cache_type_v": "f16",
            "reasoning": (
                f"Sufficient VRAM headroom ({headroom:.2f} GiB remaining); "
                f"f16 cache recommended for best inference quality"
            ),
        }
    elif headroom >= 0.5:
        # Moderate: use q8_0 for keys, f16 for values (good balance)
        return {
            "cache_type_k": "q8_0",
            "cache_type_v": "f16",
            "reasoning": (
                f"Moderate VRAM headroom ({headroom:.2f} GiB remaining); "
                f"q8_0 key cache saves ~50% KV memory with minimal quality loss"
            ),
        }
    else:
        # Tight: use q8_0 for both
        return {
            "cache_type_k": "q8_0",
            "cache_type_v": "q8_0",
            "reasoning": (
                f"Tight VRAM headroom ({headroom:.2f} GiB remaining); "
                f"q8_0 cache recommended to maximize available context size"
            ),
        }


def recommend_batch(
    vram_total_gb: float,
    performance_mode: str = "balanced",
) -> dict:
    """Recommend batch and ubatch sizes based on VRAM and performance mode.

    Args:
        vram_total_gb: Total GPU VRAM in GiB.
        performance_mode: One of "safe", "balanced", or "fast".

    Returns:
        dict with keys:
            batch (int): Recommended batch size.
            ubatch (int): Recommended micro-batch size.
            reasoning (str): Explanation of the recommendation.
    """
    # Base batch sizes per performance mode
    _BATCH_PROFILES: dict[str, dict[str, int]] = {  # noqa: N806
        "safe": {"batch": 128, "ubatch": 64},
        "balanced": {"batch": 256, "ubatch": 128},
        "fast": {"batch": 512, "ubatch": 256},
    }

    mode = performance_mode.lower()
    if mode not in _BATCH_PROFILES:
        mode = "balanced"

    profile = _BATCH_PROFILES[mode]

    # Scale down for very low VRAM
    if vram_total_gb < 4.0:
        batch = min(profile["batch"], 128)
        ubatch = min(profile["ubatch"], 64)
        reasoning = f"Low VRAM ({vram_total_gb:.1f} GiB); batch sizes capped at {batch}/{ubatch} to avoid OOM"
    elif vram_total_gb < 6.0:
        batch = min(profile["batch"], 256)
        ubatch = min(profile["ubatch"], 128)
        reasoning = f"Moderate VRAM ({vram_total_gb:.1f} GiB); batch sizes capped at {batch}/{ubatch} for {mode} mode"
    else:
        batch = profile["batch"]
        ubatch = profile["ubatch"]
        reasoning = f"Sufficient VRAM ({vram_total_gb:.1f} GiB); {mode} mode batch sizes: {batch}/{ubatch}"

    return {
        "batch": batch,
        "ubatch": ubatch,
        "reasoning": reasoning,
    }


def recommend_gpu_layers(
    model_size_gb: float,
    vram_total_gb: float,
) -> dict:
    """Recommend number of GPU layers to offload.

    If the entire model fits in VRAM (with overhead), recommends "all".
    Otherwise, calculates approximate number of layers that can fit.

    Args:
        model_size_gb: Model file size in GiB.
        vram_total_gb: Total GPU VRAM in GiB.

    Returns:
        dict with keys:
            gpu_layers (str | int): "all" if model fits, or approximate layer count.
            notes (str): Additional notes about the recommendation.
    """
    safe = vram_safe_budget(vram_total_gb)

    # Estimate with full offload and moderate context to see if it fits
    est = estimate_vram_usage(
        model_size_gb=model_size_gb,
        gpu_layers="all",
        total_layers=32,
        ctx_size=4096,
        cache_type_k="q8_0",
        cache_type_v="q8_0",
    )

    if est["expected_vram_gb"] <= safe:
        return {
            "gpu_layers": "all",
            "notes": (
                f"Model (~{model_size_gb:.2f} GiB) fits within safe VRAM budget "
                f"({safe:.2f} GiB) with full offload; estimated VRAM usage "
                f"{est['expected_vram_gb']:.2f} GiB"
            ),
        }

    # Model doesn't fit entirely — calculate partial layers
    # Available for model weights = safe - kv_cache - overheads
    kv_cache = est["kv_cache_gb"]
    overheads = est["compute_overhead_gb"] + est["cuda_overhead_gb"]
    available_for_model = safe - kv_cache - overheads

    if available_for_model <= 0:
        return {
            "gpu_layers": 0,
            "notes": (
                f"Insufficient VRAM for any GPU offload; safe budget ({safe:.2f} GiB) "
                f"consumed by overheads and KV cache alone. Consider a smaller model "
                f"or quantized cache."
            ),
        }

    # Estimate layers proportionally (using repack_factor=1.08)
    repack = 1.08
    model_per_layer = (model_size_gb * repack) / 32  # assume 32 layers
    gpu_layer_count = int(available_for_model / model_per_layer)
    gpu_layer_count = max(0, min(gpu_layer_count, 32))

    notes = (
        f"Partial offload recommended: ~{gpu_layer_count} of ~32 layers. "
        f"Available for model weights: {available_for_model:.2f} GiB "
        f"(safe budget {safe:.2f} GiB minus KV cache {kv_cache:.2f} GiB "
        f"and overheads {overheads:.2f} GiB). "
        f"Remaining layers will run on CPU (slower)."
    )

    return {
        "gpu_layers": gpu_layer_count,
        "notes": notes,
    }


def recommend_profile_settings(
    vram_total_gb: float,
    model_size_gb: float,
    performance_mode: str = "balanced",
) -> dict:
    """Combine all recommendation functions into a single profile settings dict.

    Calls recommend_context, recommend_kv_cache, recommend_batch,
    recommend_gpu_layers, and estimate_vram_usage/estimate_ram_usage
    to produce a complete set of recommended settings.

    Args:
        vram_total_gb: Total GPU VRAM in GiB.
        model_size_gb: Model file size in GiB.
        performance_mode: One of "safe", "balanced", or "fast".

    Returns:
        dict with keys:
            ctx (int): Recommended context size.
            batch (int): Recommended batch size.
            ubatch (int): Recommended micro-batch size.
            cache_type_k (str): Recommended KV key cache dtype.
            cache_type_v (str): Recommended KV value cache dtype.
            gpu_layers (str | int): Recommended GPU layers.
            flash_attn (bool): Whether to enable flash attention.
            parallel (int): Recommended parallel sequences.
            expected_vram_gb (float): Estimated VRAM usage.
            expected_ram_gb (float): Estimated RAM usage.
            warnings (list[str]): Combined warnings.
            confidence (str): Overall confidence level.
    """
    ctx_rec = recommend_context(vram_total_gb, model_size_gb)
    kv_rec = recommend_kv_cache(vram_total_gb, model_size_gb)
    batch_rec = recommend_batch(vram_total_gb, performance_mode)
    gpu_rec = recommend_gpu_layers(model_size_gb, vram_total_gb)

    # Determine total_layers for estimation (default 32 if unknown)
    total_layers = 32
    gpu_layers_value: int | str = gpu_rec["gpu_layers"]
    if isinstance(gpu_layers_value, str) and gpu_layers_value == "all":
        gpu_layers_for_est = "all"
    else:
        gpu_layers_for_est = int(gpu_layers_value)

    # Estimate VRAM with recommended settings
    vram_est = estimate_vram_usage(
        model_size_gb=model_size_gb,
        gpu_layers=gpu_layers_for_est,
        total_layers=total_layers,
        ctx_size=ctx_rec["ctx"],
        cache_type_k=kv_rec["cache_type_k"],
        cache_type_v=kv_rec["cache_type_v"],
    )

    # Estimate RAM
    ram_est = estimate_ram_usage(
        model_size_gb=model_size_gb,
        gpu_layers=gpu_layers_for_est,
        total_layers=total_layers,
        no_mmap=False,
    )

    # Flash attention: enable if VRAM is comfortable
    safe = vram_safe_budget(vram_total_gb)
    headroom = safe - vram_est["expected_vram_gb"]
    flash_attn = headroom > 0.3  # Enable if at least 0.3 GiB headroom

    # Parallel sequences: 1 for tight VRAM, 2 for comfortable
    parallel = 2 if headroom > 1.0 else 1

    # Combine warnings
    all_warnings: list[str] = []
    all_warnings.extend(vram_est["warnings"])
    all_warnings.extend(ram_est["warnings"])

    # Overall confidence: use the lower of the two
    confidence_rank = {"high": 3, "medium": 2, "low": 1}
    vram_conf = confidence_rank.get(vram_est["confidence"], 1)
    ram_conf = confidence_rank.get(ram_est["confidence"], 1)
    overall_conf = min(vram_conf, ram_conf)
    confidence = {3: "high", 2: "medium", 1: "low"}[overall_conf]

    # Additional warnings
    if not flash_attn:
        all_warnings.append(
            "Flash attention disabled due to tight VRAM; enabling it may improve speed but requires more memory"
        )

    if parallel == 1 and performance_mode == "fast":
        all_warnings.append("Fast mode requested but only 1 parallel sequence recommended due to VRAM constraints")

    return {
        "ctx": ctx_rec["ctx"],
        "batch": batch_rec["batch"],
        "ubatch": batch_rec["ubatch"],
        "cache_type_k": kv_rec["cache_type_k"],
        "cache_type_v": kv_rec["cache_type_v"],
        "gpu_layers": gpu_rec["gpu_layers"],
        "flash_attn": flash_attn,
        "parallel": parallel,
        "expected_vram_gb": vram_est["expected_vram_gb"],
        "expected_ram_gb": ram_est["expected_ram_gb"],
        "warnings": all_warnings,
        "confidence": confidence,
    }
