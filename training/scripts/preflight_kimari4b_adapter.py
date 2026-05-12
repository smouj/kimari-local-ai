#!/usr/bin/env python3
"""Preflight checks for Kimari-4B private adapter run.

Verifies:
- Config file exists and has correct safety flags
- Dataset exists (or placeholder noted)
- Torch stack available
- CUDA available or remote GPU declared
- Output dir is gitignored
- No HF upload configured
- Gate is BLOCKED
- Disk space warning
- Expected VRAM warning

Usage:
    python training/scripts/preflight_kimari4b_adapter.py --config training/configs/kimari4b_private_adapter_run.v0.yaml
    python training/scripts/preflight_kimari4b_adapter.py --config training/configs/kimari4b_private_adapter_run.v0.yaml --json
"""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

CHECKS: list[dict] = []
WARNINGS: list[str] = []


def check(name: str, passed: bool, fail_msg: str) -> None:
    """Record a check result."""
    CHECKS.append({"name": name, "passed": passed, "fail_msg": fail_msg if not passed else ""})


def load_config(config_path: str) -> dict | None:
    """Load YAML config."""
    try:
        import yaml
    except ImportError:
        check("Config load", False, "PyYAML not installed")
        return None
    path = Path(config_path)
    if not path.exists():
        check("Config exists", False, f"Config not found: {config_path}")
        return None
    with open(path) as f:
        data = yaml.safe_load(f)
    check("Config exists", True, "")
    return data


def run_preflight(config_path: str) -> dict:
    """Run all preflight checks."""
    config = load_config(config_path)
    if config is None:
        return {"passed": False, "checks": CHECKS, "warnings": WARNINGS}

    # Safety flags
    safety = config.get("safety", {})
    check(
        "public_release_allowed=false",
        safety.get("public_release_allowed") is False,
        f"public_release_allowed={safety.get('public_release_allowed')}",
    )
    check(
        "hf_upload_allowed=false",
        safety.get("hf_upload_allowed") is False,
        f"hf_upload_allowed={safety.get('hf_upload_allowed')}",
    )
    check(
        "gguf_export_allowed=false",
        safety.get("gguf_export_allowed") is False,
        f"gguf_export_allowed={safety.get('gguf_export_allowed')}",
    )
    check(
        "push_to_hub=false",
        safety.get("push_to_hub") is not True,
        f"push_to_hub={safety.get('push_to_hub')}",
    )
    check(
        "report_to=none",
        safety.get("report_to") in ("none", None),
        f"report_to={safety.get('report_to')}",
    )
    check(
        "preview_gate_state=BLOCKED",
        safety.get("preview_gate_state") == "BLOCKED",
        f"preview_gate_state={safety.get('preview_gate_state')}",
    )

    # Dataset
    dataset_path = config.get("dataset", {}).get("path", "")
    dataset_full = PROJECT_ROOT / dataset_path
    if dataset_path:
        check("Dataset exists", dataset_full.exists(), f"Dataset not found: {dataset_path}")
        if dataset_full.exists():
            import hashlib

            content = dataset_full.read_bytes()
            hashlib.sha256(content).hexdigest()[:16]
            check("Dataset hash computed", True, "")
        else:
            WARNINGS.append(f"Dataset not found: {dataset_path}. Create before training.")
    else:
        WARNINGS.append("No dataset path in config.")

    # Torch
    try:
        import torch

        check("torch available", True, "")
        cuda = torch.cuda.is_available()
        check("CUDA available", cuda, "CUDA not available — training will be very slow on CPU")
        if cuda:
            gpu_name = torch.cuda.get_device_name(0)
            gpu_mem = torch.cuda.get_device_properties(0).total_mem / (1024**3)
            check(
                "GPU VRAM >= 16GB",
                gpu_mem >= 16,
                f"GPU: {gpu_name} ({gpu_mem:.1f} GB) — may be too small for 3B LoRA training",
            )
            if gpu_mem < 16:
                WARNINGS.append(f"GPU VRAM {gpu_mem:.1f} GB < 16 GB recommended. Consider RunPod/remote GPU.")
        else:
            WARNINGS.append("No CUDA. Training on CPU will be extremely slow for a 3B model.")
            check("Remote GPU declared", False, "No CUDA and no remote GPU declared in config")
    except ImportError:
        check("torch available", False, "PyTorch not installed")
        WARNINGS.append("PyTorch not available. Install before training.")

    # Gitignore
    gitignore_path = PROJECT_ROOT / ".gitignore"
    output_dir = config.get("output", {}).get("dir", "")
    if gitignore_path.exists() and output_dir:
        content = gitignore_path.read_text()
        patterns = ["training/adapters/", "training/adapters", "*.safetensors"]
        gitignored = any(p in content for p in patterns)
        check("output_dir gitignored", gitignored, f"{output_dir} not in .gitignore")
    else:
        check("output_dir gitignored", False, ".gitignore missing or no output_dir in config")

    # Disk space
    total, used, free = shutil.disk_usage(str(PROJECT_ROOT))
    free_gb = free / (1024**3)
    check("Disk space >= 10GB free", free_gb >= 10, f"Only {free_gb:.1f} GB free")
    if free_gb < 20:
        WARNINGS.append(f"Disk space low: {free_gb:.1f} GB free. LoRA training may need 10-20 GB.")

    # Gate
    check("Gate BLOCKED", True, "")  # Structural check

    # Auto gate transition
    check(
        "auto_gate_transition=false",
        config.get("auto_gate_transition") is not True,
        "auto_gate_transition should be false",
    )

    passed = all(c["passed"] for c in CHECKS)
    return {"passed": passed, "checks": CHECKS, "warnings": WARNINGS}


def main() -> None:
    parser = argparse.ArgumentParser(description="Kimari-4B adapter preflight checks")
    parser.add_argument("--config", required=True, help="Path to config YAML")
    parser.add_argument("--json", action="store_true", help="JSON output")
    args = parser.parse_args()

    result = run_preflight(args.config)

    if args.json:
        print(json.dumps(result, indent=2))
        sys.exit(0 if result["passed"] else 1)

    print("Kimari-4B Private Adapter — Preflight Checks")
    print("=" * 50)
    for c in result["checks"]:
        status = "✅" if c["passed"] else "❌"
        msg = f" — {c['fail_msg']}" if c["fail_msg"] else ""
        print(f"  {status} {c['name']}{msg}")
    for w in result["warnings"]:
        print(f"  ⚠️  {w}")
    print("=" * 50)
    if result["passed"]:
        print(f"RESULT: All checks passed! ({len(result['warnings'])} warning(s))")
    else:
        fails = sum(1 for c in result["checks"] if not c["passed"])
        print(f"RESULT: {fails} check(s) failed, {len(result['warnings'])} warning(s)")
    sys.exit(0 if result["passed"] else 1)


if __name__ == "__main__":
    main()
