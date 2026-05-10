"""
VRAM and RAM estimation functions for Kimari.

All functions are pure — no side effects, no network calls, no subprocess.
Estimates are approximate and should not be treated as exact measurements.
"""

# Known GPU VRAM safe budgets (in GB)
_KNOWN_GPU_BUDGETS: dict[str, float] = {
    "GTX 1060": 4.9,
    "GTX 1060 6GB": 4.9,
    "GTX 1080": 6.8,
    "GTX 1080 8GB": 6.8,
}

# KV cache dtype factors relative to f16
_KV_DTYPE_FACTORS: dict[str, float] = {
    "f16": 1.0,
    "q8_0": 0.5,
    "q4_0": 0.30,
    "q4_1": 0.30,
    "f32": 2.0,
}

# Baseline KV cache usage per 1K tokens (GB), approximated for a ~4B model
_KV_PER_1K_TOKENS_GB: float = 0.0625


def vram_safe_budget(total_vram_gb: float) -> float:
    """Calculate the safe VRAM budget (usable VRAM after driver/reserve overhead).

    Uses conservative multipliers:
      - 6 GB cards: 82% usable (driver overhead is proportionally larger)
      - 8 GB cards: 86% usable
      - Default:     85% usable

    Args:
        total_vram_gb: Total VRAM of the GPU in GiB.

    Returns:
        Approximate safe VRAM budget in GiB.
    """
    if total_vram_gb <= 6.0:
        return round(total_vram_gb * 0.82, 2)
    elif total_vram_gb <= 8.0:
        return round(total_vram_gb * 0.86, 2)
    else:
        return round(total_vram_gb * 0.85, 2)


def estimate_vram_usage(
    model_size_gb: float,
    gpu_layers: int | str,
    total_layers: int,
    ctx_size: int,
    cache_type_k: str = "f16",
    cache_type_v: str = "f16",
    repack_factor: float = 1.08,
    compute_overhead_gb: float = 0.35,
    cuda_overhead_gb: float = 0.45,
) -> dict:
    """Estimate VRAM usage for a model with given configuration.

    Formula:
        VRAM_total ≈ model_gpu_part + kv_cache + compute_overhead + cuda_overhead

    All estimates are approximate. Confidence reflects the reliability of
    the estimate based on model size.

    Args:
        model_size_gb: Size of the GGUF model file in GiB.
        gpu_layers: Number of layers offloaded to GPU (int), or "all".
        total_layers: Total number of layers in the model.
        ctx_size: Context window size in tokens.
        cache_type_k: KV cache key dtype (f16, q8_0, q4_0, q4_1, f32).
        cache_type_v: KV cache value dtype (f16, q8_0, q4_0, q4_1, f32).
        repack_factor: Weight repacking overhead multiplier (default 1.08).
        compute_overhead_gb: Overhead for compute/activations in GiB.
        cuda_overhead_gb: CUDA context and driver overhead in GiB.

    Returns:
        dict with keys:
            expected_vram_gb (float): Total estimated VRAM in GiB.
            model_gpu_part_gb (float): Model weights on GPU in GiB.
            kv_cache_gb (float): KV cache estimated usage in GiB.
            compute_overhead_gb (float): Compute overhead in GiB.
            cuda_overhead_gb (float): CUDA overhead in GiB.
            confidence (str): "low", "medium", or "high".
            warnings (list[str]): List of warning messages.
    """
    # Resolve gpu_layers ratio
    if isinstance(gpu_layers, str) and gpu_layers == "all":
        offload_ratio = 1.0
    elif isinstance(gpu_layers, (int, float)) and total_layers > 0:
        offload_ratio = min(gpu_layers / total_layers, 1.0)
    else:
        offload_ratio = 0.0

    # Model part on GPU
    model_gpu_part = model_size_gb * offload_ratio * repack_factor

    # KV cache estimation
    k_factor = _KV_DTYPE_FACTORS.get(cache_type_k, 1.0)
    v_factor = _KV_DTYPE_FACTORS.get(cache_type_v, 1.0)
    avg_dtype_factor = (k_factor + v_factor) / 2.0
    kv_cache = _KV_PER_1K_TOKENS_GB * (ctx_size / 1024) * avg_dtype_factor

    # Total
    expected_vram = model_gpu_part + kv_cache + compute_overhead_gb + cuda_overhead_gb

    # Confidence
    if model_size_gb < 2:
        confidence = "high"
    elif model_size_gb < 5:
        confidence = "medium"
    else:
        confidence = "low"

    # Warnings
    warnings: list[str] = []

    if cache_type_k not in _KV_DTYPE_FACTORS:
        warnings.append(
            f"Unknown cache_type_k '{cache_type_k}'; defaulting to f16 factor. "
            f"Supported: {', '.join(_KV_DTYPE_FACTORS.keys())}"
        )
    if cache_type_v not in _KV_DTYPE_FACTORS:
        warnings.append(
            f"Unknown cache_type_v '{cache_type_v}'; defaulting to f16 factor. "
            f"Supported: {', '.join(_KV_DTYPE_FACTORS.keys())}"
        )

    for gpu_name, budget in _KNOWN_GPU_BUDGETS.items():
        if expected_vram > budget:
            warnings.append(
                f"Estimated VRAM ({expected_vram:.2f} GiB) may exceed safe budget for {gpu_name} ({budget:.1f} GiB)"
            )

    if offload_ratio < 1.0 and offload_ratio > 0:
        warnings.append(f"Partial GPU offload ({offload_ratio:.0%}); RAM will also be needed for CPU layers")

    return {
        "expected_vram_gb": round(expected_vram, 3),
        "model_gpu_part_gb": round(model_gpu_part, 3),
        "kv_cache_gb": round(kv_cache, 3),
        "compute_overhead_gb": compute_overhead_gb,
        "cuda_overhead_gb": cuda_overhead_gb,
        "confidence": confidence,
        "warnings": warnings,
    }


def estimate_ram_usage(
    model_size_gb: float,
    gpu_layers: int | str,
    total_layers: int,
    no_mmap: bool = False,
    os_margin_gb: float = 3.0,
) -> dict:
    """Estimate RAM usage for a model with given configuration.

    Formula:
        RAM ≈ model_cpu_part + mmap_overhead + os_margin

    Where:
        - model_cpu_part = model_size_gb * (1 - offload_ratio)
        - If mmap is active (no_mmap=False): mmap_overhead ≈ 0.1 GiB (mmap is efficient)
        - If mmap is disabled (no_mmap=True): mmap_overhead = model_cpu_part (full copy in RAM)

    Args:
        model_size_gb: Size of the GGUF model file in GiB.
        gpu_layers: Number of layers offloaded to GPU (int), or "all".
        total_layers: Total number of layers in the model.
        no_mmap: If True, mmap is disabled and model is loaded entirely into RAM.
        os_margin_gb: OS and system overhead margin in GiB (default 3.0).

    Returns:
        dict with keys:
            expected_ram_gb (float): Total estimated RAM in GiB.
            offload_ratio (float): Fraction of model offloaded to GPU.
            uses_mmap (bool): Whether mmap is being used.
            confidence (str): "low", "medium", or "high".
            warnings (list[str]): List of warning messages.
    """
    # Resolve offload ratio
    if isinstance(gpu_layers, str) and gpu_layers == "all":
        offload_ratio = 1.0
    elif isinstance(gpu_layers, (int, float)) and total_layers > 0:
        offload_ratio = min(gpu_layers / total_layers, 1.0)
    else:
        offload_ratio = 0.0

    uses_mmap = not no_mmap

    # CPU-side model part
    model_cpu_part = model_size_gb * (1 - offload_ratio)

    # mmap overhead
    mmap_overhead = 0.1 if uses_mmap else model_cpu_part

    expected_ram = model_cpu_part + mmap_overhead + os_margin_gb

    # Confidence
    if model_size_gb < 2:
        confidence = "high"
    elif model_size_gb < 5:
        confidence = "medium"
    else:
        confidence = "low"

    # Warnings
    warnings: list[str] = []

    if no_mmap and offload_ratio < 1.0:
        warnings.append(
            "mmap is disabled (no_mmap=True); model will be fully loaded into RAM, "
            "significantly increasing memory usage"
        )

    if offload_ratio == 1.0:
        # All layers on GPU, minimal RAM needed
        if no_mmap:
            warnings.append(
                "All layers offloaded to GPU but mmap is disabled; RAM may still be needed for initial model loading"
            )
    elif offload_ratio == 0.0:
        warnings.append("No GPU offload; entire model will run on CPU — performance will be significantly slower")

    return {
        "expected_ram_gb": round(expected_ram, 3),
        "offload_ratio": round(offload_ratio, 4),
        "uses_mmap": uses_mmap,
        "confidence": confidence,
        "warnings": warnings,
    }
