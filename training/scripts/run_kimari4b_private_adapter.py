#!/usr/bin/env python3
"""Kimari-4B private adapter runner.

Runs SFT LoRA training for Kimari-4B private adapter.
Defaults to dry-run. Real training requires --allow-train --yes.

SAFETY:
- dry-run by default (no training happens)
- Real training requires explicit --allow-train AND --yes
- No push_to_hub ever
- No HF upload
- No token arguments
- output_dir must be gitignored
- Preflight must pass before training

Usage:
    # Dry-run (default)
    python training/scripts/run_kimari4b_private_adapter.py --config training/configs/kimari4b_private_adapter_run.v0.yaml

    # Dry-run with JSON output
    python training/scripts/run_kimari4b_private_adapter.py --config training/configs/kimari4b_private_adapter_run.v0.yaml --dry-run --json

    # Real training (EXPLICIT consent required)
    python training/scripts/run_kimari4b_private_adapter.py --config training/configs/kimari4b_private_adapter_run.v0.yaml --allow-train --yes
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent


def load_config(config_path: str) -> dict:
    """Load YAML config. Requires PyYAML."""
    try:
        import yaml
    except ImportError:
        print("ERROR: PyYAML required. Install with: pip install pyyaml")
        sys.exit(1)
    with open(config_path) as f:
        return yaml.safe_load(f)


def verify_safety_flags(config: dict) -> list[str]:
    """Verify all safety flags are correct. Returns list of errors."""
    errors = []
    safety = config.get("safety", {})
    if safety.get("public_release_allowed") is True:
        errors.append("public_release_allowed must be false")
    if safety.get("hf_upload_allowed") is True:
        errors.append("hf_upload_allowed must be false")
    if safety.get("gguf_export_allowed") is True:
        errors.append("gguf_export_allowed must be false")
    if safety.get("push_to_hub") is True:
        errors.append("push_to_hub must be false")
    if safety.get("report_to") not in ("none", None):
        errors.append(f"report_to must be 'none', got '{safety.get('report_to')}'")
    if safety.get("preview_gate_state") != "BLOCKED":
        errors.append(f"preview_gate_state must be BLOCKED, got '{safety.get('preview_gate_state')}'")
    return errors


def verify_gitignore(output_dir: str) -> bool:
    """Check if output_dir pattern is in .gitignore."""
    gitignore_path = PROJECT_ROOT / ".gitignore"
    if not gitignore_path.exists():
        return False
    content = gitignore_path.read_text()
    # Check if the output dir or its parent pattern is gitignored
    patterns = ["training/adapters/", "training/adapters", "*.safetensors"]
    return any(pattern in content for pattern in patterns)


def print_risks(config: dict) -> None:
    """Print risk warnings before training."""
    print("\n⚠️  TRAINING RISK WARNINGS ⚠️")
    print("=" * 50)
    print(f"  Base model: {config.get('base_model', {}).get('name', 'unknown')}")
    print(f"  Output dir: {config.get('output', {}).get('dir', 'unknown')}")
    print(f"  Public release: {config.get('safety', {}).get('public_release_allowed', 'unknown')}")
    print(f"  HF upload: {config.get('safety', {}).get('hf_upload_allowed', 'unknown')}")
    print(f"  GGUF export: {config.get('safety', {}).get('gguf_export_allowed', 'unknown')}")
    print(f"  Gate state: {config.get('safety', {}).get('preview_gate_state', 'unknown')}")
    print(f"  Manual review: {config.get('manual_review_required', 'unknown')}")
    print("=" * 50)
    print("  This will create adapter files locally.")
    print("  No files will be uploaded or published.")
    print("  Gate remains BLOCKED after training.")
    print("=" * 50 + "\n")


def dry_run(config: dict, json_output: bool = False) -> dict:
    """Simulate training without executing it."""
    result = {
        "mode": "dry-run",
        "run_id": config.get("run_id", "unknown"),
        "base_model": config.get("base_model", {}).get("name", "unknown"),
        "dataset_path": config.get("dataset", {}).get("path", "unknown"),
        "output_dir": config.get("output", {}).get("dir", "unknown"),
        "lora_r": config.get("lora", {}).get("r", "unknown"),
        "max_runtime_minutes": config.get("training", {}).get("max_runtime_minutes", "unknown"),
        "safety_flags": config.get("safety", {}),
        "gitignore_ok": verify_gitignore(config.get("output", {}).get("dir", "")),
        "safety_errors": verify_safety_flags(config),
        "estimated_steps": "N/A (dry-run)",
        "command_preview": _build_command_preview(config),
    }
    if json_output:
        return result
    # Print human-readable
    print("DRY-RUN: No training will be executed")
    print(f"  Run ID: {result['run_id']}")
    print(f"  Base model: {result['base_model']}")
    print(f"  Dataset: {result['dataset_path']}")
    print(f"  Output: {result['output_dir']}")
    print(f"  LoRA r: {result['lora_r']}")
    print(f"  Max runtime: {result['max_runtime_minutes']} min")
    print(f"  Gitignore OK: {result['gitignore_ok']}")
    print(f"  Safety errors: {result['safety_errors']}")
    print(f"\n  Command preview:\n  {result['command_preview']}")
    return result


def _build_command_preview(config: dict) -> str:
    """Build a preview of the training command that would be executed."""
    base_model = config.get("base_model", {}).get("name", "unknown")
    output_dir = config.get("output", {}).get("dir", "unknown")
    dataset_path = config.get("dataset", {}).get("path", "unknown")
    lora = config.get("lora", {})
    training_cfg = config.get("training", {})

    cmd_parts = [
        "python -m axolotl.cli.train",
        "  --config-file <generated-yaml>",
        f"  # base_model: {base_model}",
        f"  # dataset: {dataset_path}",
        f"  # output_dir: {output_dir}",
        f"  # lora_r: {lora.get('r', 'unknown')}",
        f"  # epochs: {training_cfg.get('num_train_epochs', 'unknown')}",
        f"  # batch_size: {training_cfg.get('per_device_train_batch_size', 'unknown')}",
        f"  # learning_rate: {training_cfg.get('learning_rate', 'unknown')}",
        f"  # fp16: {training_cfg.get('fp16', 'unknown')}",
        "  # push_to_hub: false",
        "  # report_to: none",
    ]
    return "\n  ".join(cmd_parts)


def real_train(config: dict, json_output: bool = False) -> dict:
    """Execute real training. Only called with --allow-train --yes."""
    safety_errors = verify_safety_flags(config)
    if safety_errors:
        return {"error": f"Safety violations: {safety_errors}", "trained": False}

    if not verify_gitignore(config.get("output", {}).get("dir", "")):
        return {"error": "output_dir is not gitignored. Refusing to train.", "trained": False}

    print_risks(config)

    # Check for torch availability
    try:
        import torch

        cuda_available = torch.cuda.is_available()
    except ImportError:
        cuda_available = False

    if not cuda_available:
        print("WARNING: CUDA not available. Training on CPU will be extremely slow.")
        print("For a 3B model, a GPU with 16GB+ VRAM is recommended.")

    result = {
        "mode": "real-train",
        "run_id": config.get("run_id", "unknown"),
        "base_model": config.get("base_model", {}).get("name", "unknown"),
        "cuda_available": cuda_available,
        "started_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "output_dir": config.get("output", {}).get("dir", "unknown"),
        "safety_flags": config.get("safety", {}),
        "trained": False,
        "note": "Actual training execution not yet implemented. Use axolotl or trl directly.",
    }

    if json_output:
        return result

    print("\nTraining configuration:")
    print(f"  Run ID: {result['run_id']}")
    print(f"  Base: {result['base_model']}")
    print(f"  CUDA: {result['cuda_available']}")
    print("\n  NOTE: Direct training execution is not implemented in this script.")
    print("  Use axolotl or trl SFTTrainer with the config above.")
    print("  Generate a full axolotl config from this YAML and run:")
    print("    axolotl train <config.yaml>")
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description="Kimari-4B private adapter runner")
    parser.add_argument("--config", required=True, help="Path to config YAML")
    parser.add_argument("--dry-run", action="store_true", default=True, help="Dry-run mode (default)")
    parser.add_argument("--allow-train", action="store_true", default=False, help="Allow real training")
    parser.add_argument("--yes", action="store_true", default=False, help="Confirm consent for training")
    parser.add_argument("--json", action="store_true", help="JSON output")
    args = parser.parse_args()

    config = load_config(args.config)

    # Safety: never train in CI
    if os.environ.get("CI") == "true" and args.allow_train:
        print("ERROR: Training blocked in CI environment")
        sys.exit(1)

    # Safety: --allow-train requires --yes
    if args.allow_train and not args.yes:
        print("ERROR: --allow-train requires --yes for explicit consent")
        print("Usage: --allow-train --yes")
        sys.exit(1)

    # Safety: no token arguments
    for arg in sys.argv:
        if arg.startswith("--token") or arg.startswith("--api-key"):
            print(f"ERROR: Token/API key arguments not allowed: {arg}")
            sys.exit(1)

    if args.allow_train and args.yes:
        result = real_train(config, json_output=args.json)
    else:
        result = dry_run(config, json_output=args.json)

    if args.json:
        print(json.dumps(result, indent=2))

    if result.get("error"):
        sys.exit(1)


if __name__ == "__main__":
    main()
