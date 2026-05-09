"""
KimariFit — VRAM estimation and fit score calculation.

Estimates whether a given model + context will fit in a GPU's VRAM
and provides a score based on utilization and quantization quality.
"""

import platform
from pathlib import Path
from typing import Optional

from kimari import __version__ as KIMARI_VERSION
from kimari.core.constants import PROJECT_ROOT
from kimari.core.detection import detect_gpu
from kimari.utils.colors import Color


def quality_factor(model_name: str) -> int:
    """Estimate quantization quality factor from model filename.

    Returns a score 0-100 based on the quantization level.
    """
    name = model_name.lower()
    if "q8" in name:
        return 95
    elif "q6" in name or "q5_k_m" in name:
        return 85
    elif "q5" in name:
        return 80
    elif "q4_k_m" in name:
        return 75
    elif "iq4" in name:
        return 70
    elif "q4" in name:
        return 65
    elif "q3" in name:
        return 50
    else:
        return 70  # Unknown


def calculate_kimarifit(model_path: str, ctx_size: int, config: dict,
                         vram_override: Optional[float] = None):
    """Calculate the KimariFit score for a given model and context.

    Args:
        model_path: Path to GGUF model file (relative or absolute).
        ctx_size: Context size in tokens.
        config: Configuration dict (not used directly but kept for interface compatibility).
        vram_override: Override VRAM in GiB (for systems without GPU detection).
    """
    model_file = Path(model_path)
    if not model_file.is_absolute():
        model_file = PROJECT_ROOT / model_path

    if not model_file.exists():
        print(f"[ERROR] Model not found: {model_file}")
        raise SystemExit(1)

    # Get model size in GiB
    model_size_bytes = model_file.stat().st_size
    model_size_gib = model_size_bytes / (1024 ** 3)

    # Detect GPU or use override
    if vram_override is not None:
        total_vram = vram_override
        gpu = None
    else:
        gpu = detect_gpu()
        if not gpu:
            print("[WARN] No GPU detected. Using default 6 GB VRAM.")
            print("       Use --vram to specify your GPU's VRAM manually.")
            total_vram = 6.0
        else:
            total_vram = gpu["vram_mb"] / 1024

    safe_vram = total_vram * 0.87

    # VRAM estimation formula: Mtotal ≈ S_GGUF + C/9709 + overhead
    kv_vram = ctx_size / 9709
    overhead = 1.0  # Conservative estimate
    total_estimated = model_size_gib + kv_vram + overhead

    # Calculate fit score
    if total_estimated <= safe_vram:
        # Score based on how much headroom remains
        utilization = total_estimated / safe_vram
        # Higher score when utilization is good (not too low, not too high)
        if utilization < 0.5:
            score = 60 + (utilization / 0.5) * 20  # 60-80
        elif utilization < 0.85:
            score = 80 + ((utilization - 0.5) / 0.35) * 20  # 80-100
        else:
            score = 100 - ((utilization - 0.85) / 0.15) * 30  # 100-70
    else:
        # Over budget
        over_pct = (total_estimated - safe_vram) / safe_vram * 100
        score = max(0, 40 - over_pct)

    # Quality factor based on quantization name
    qf = quality_factor(model_file.name)

    final_score = (score * 0.7) + (qf * 0.3)

    print(f"\n{Color.BOLD}{Color.CYAN}KimariFit Analysis{Color.RESET}\n")
    print(f"  Model:           {model_file.name}")
    print(f"  Model size:      {model_size_gib:.2f} GiB")
    print(f"  Context:         {ctx_size:,} tokens")
    print(f"  KV cache VRAM:   {kv_vram:.2f} GiB")
    print(f"  Overhead:        {overhead:.2f} GiB")
    print(f"  Total estimated: {total_estimated:.2f} GiB")
    if gpu:
        print(f"  GPU:             {gpu['name']} ({gpu['vram_mb']} MB)")
    elif vram_override:
        print(f"  VRAM (manual):   {vram_override} GiB")
    print(f"  Safe VRAM:       {safe_vram:.2f} GiB ({total_vram:.1f} GiB × 0.87)")
    print(f"  Utilization:     {total_estimated/safe_vram*100:.1f}%")
    print(f"\n  {Color.BOLD}KimariFit Score: {final_score:.0f}/100{Color.RESET}")

    if final_score >= 80:
        print(f"  {Color.GREEN}✓ Excellent fit{Color.RESET}")
    elif final_score >= 60:
        print(f"  {Color.YELLOW}~ Good fit{Color.RESET}")
    elif final_score >= 40:
        print(f"  {Color.YELLOW}⚠ Tight fit — may OOM{Color.RESET}")
    else:
        print(f"  {Color.RED}✗ Poor fit — likely OOM{Color.RESET}")
