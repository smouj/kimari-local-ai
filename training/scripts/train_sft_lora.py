#!/usr/bin/env python3
"""Kimari SFT LoRA Training Script (Skeleton).

This is an experimental training script. It:
- Reads configuration from a YAML file
- Validates config and dependencies
- Supports --dry-run for config validation without training
- Must NOT execute real training in CI
- Fails clearly if dependencies are missing
- Does NOT hardcode any base model

No network calls. No downloads.
"""

from __future__ import annotations

import argparse
import sys


def check_dependencies() -> list[str]:
    """Check for required training dependencies.

    Returns a list of missing package names. Empty list means all OK.
    """
    required = {
        "transformers": "transformers",
        "datasets": "datasets",
        "peft": "peft",
        "trl": "trl",
        "accelerate": "accelerate",
        "torch": "torch",
    }
    missing: list[str] = []

    for import_name, package_name in required.items():
        try:
            __import__(import_name)
        except ImportError:
            missing.append(package_name)

    return missing


def check_yaml() -> None:
    """Check if PyYAML is installed, exit with clear message if not."""
    try:
        import yaml  # noqa: F401
    except ImportError:
        print(
            "ERROR: PyYAML is not installed. Install it with: pip install pyyaml",
            file=sys.stderr,
        )
        sys.exit(1)


def load_config(config_path: str) -> dict:
    """Load a YAML configuration file and return it as a dict.

    Exits with a clear error message if the file cannot be loaded.
    """
    from pathlib import Path

    import yaml

    config_file = Path(config_path)
    if not config_file.exists():
        print(
            f"ERROR: Config file not found: {config_path}",
            file=sys.stderr,
        )
        sys.exit(1)

    with config_file.open("r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    if not isinstance(config, dict):
        print(
            "ERROR: Config file does not contain a valid YAML mapping.",
            file=sys.stderr,
        )
        sys.exit(1)

    return config


def validate_config(config: dict) -> list[str]:
    """Validate training config and return a list of warnings.

    Does not exit — just collects issues for the user to review.
    """
    warnings: list[str] = []

    base_model = config.get("base_model") or config.get("base_model_or_adapter")
    if not base_model:
        warnings.append("No 'base_model' or 'base_model_or_adapter' key found in config.")
    elif base_model == "TBD":
        warnings.append("Base model is set to 'TBD'. You must select a base model before training.")

    output_dir = config.get("output_dir")
    if not output_dir:
        warnings.append("No 'output_dir' specified in config.")

    dataset_path = config.get("dataset_path") or config.get("preference_dataset_path")
    if not dataset_path:
        warnings.append("No 'dataset_path' or 'preference_dataset_path' specified in config.")

    if config.get("bf16") and config.get("fp16"):
        warnings.append("Both bf16 and fp16 are enabled. Only one precision mode should be active.")

    lora_r = config.get("lora_r")
    if lora_r is not None and lora_r <= 0:
        warnings.append(f"lora_r should be positive, got {lora_r}.")

    lora_alpha = config.get("lora_alpha")
    if lora_alpha is not None and lora_alpha <= 0:
        warnings.append(f"lora_alpha should be positive, got {lora_alpha}.")

    lr = config.get("learning_rate")
    if lr is not None and lr <= 0:
        warnings.append(f"learning_rate should be positive, got {lr}.")

    return warnings


def print_config_summary(config: dict) -> None:
    """Print a human-readable summary of the training configuration."""
    print("=" * 50)
    print("  Kimari Training Configuration Summary")
    print("=" * 50)

    base_model = config.get("base_model") or config.get("base_model_or_adapter", "N/A")
    output_dir = config.get("output_dir", "N/A")
    dataset_path = config.get("dataset_path") or config.get("preference_dataset_path", "N/A")
    max_seq = config.get("max_seq_length", "N/A")

    print(f"  Base model:       {base_model}")
    print(f"  Output dir:       {output_dir}")
    print(f"  Dataset:          {dataset_path}")
    print(f"  Max seq length:   {max_seq}")

    lora_r = config.get("lora_r")
    lora_alpha = config.get("lora_alpha")
    lora_dropout = config.get("lora_dropout")
    lora_targets = config.get("lora_target_modules")

    if lora_r is not None:
        print(f"  LoRA r:           {lora_r}")
        print(f"  LoRA alpha:       {lora_alpha}")
        print(f"  LoRA dropout:     {lora_dropout}")
        if lora_targets:
            print(f"  LoRA targets:     {', '.join(lora_targets)}")

    lr = config.get("learning_rate")
    epochs = config.get("num_train_epochs")
    batch_size = config.get("per_device_train_batch_size")
    grad_accum = config.get("gradient_accumulation_steps")

    if lr is not None:
        print(f"  Learning rate:    {lr}")
        print(f"  Epochs:           {epochs}")
        print(f"  Batch size:       {batch_size}")
        print(f"  Grad accum:       {grad_accum}")
        if batch_size and grad_accum:
            effective = batch_size * grad_accum
            print(f"  Effective batch:  {effective}")

    precision = "bf16" if config.get("bf16") else "fp16" if config.get("fp16") else "fp32"
    print(f"  Precision:        {precision}")
    print(f"  Seed:             {config.get('seed', 'N/A')}")
    print(f"  Grad checkpoint:  {config.get('gradient_checkpointing', 'N/A')}")
    print(f"  Report to:        {config.get('report_to', 'N/A')}")

    beta = config.get("beta")
    if beta is not None:
        print(f"  ORPO beta:        {beta}")

    print("=" * 50)


def main() -> None:
    """CLI entry point for SFT LoRA training."""
    parser = argparse.ArgumentParser(
        description="Kimari SFT LoRA Training Script (Skeleton). "
        "Experimental — no training has been performed yet. "
        "No network calls. No downloads.",
    )
    parser.add_argument(
        "--config",
        required=True,
        help="Path to YAML configuration file",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate config and show summary without starting training",
    )

    args = parser.parse_args()

    # Step 1: Check PyYAML first (needed to load config)
    check_yaml()

    # Step 2: Load config
    print(f"Loading config: {args.config}")
    config = load_config(args.config)

    # Step 3: Print summary
    print()
    print_config_summary(config)

    # Step 4: Validate and show warnings
    warnings = validate_config(config)
    if warnings:
        print("\nConfiguration Warnings:")
        for warning in warnings:
            print(f"  ⚠  {warning}")

    # Step 5: If dry-run, exit here
    if args.dry_run:
        print("\n[DRY RUN] Config validated. No training was performed.")
        if warnings:
            print("[DRY RUN] Fix the warnings above before running for real.")
        sys.exit(0)

    # Step 6: Check training dependencies
    missing = check_dependencies()
    if missing:
        print(
            f"\nERROR: Missing required packages: {', '.join(missing)}",
            file=sys.stderr,
        )
        print(
            f"Install them with: pip install {' '.join(missing)}",
            file=sys.stderr,
        )
        sys.exit(1)

    # Step 7: Warn about experimental status
    print(
        "\n⚠  WARNING: This training code is EXPERIMENTAL.",
        file=sys.stderr,
    )
    print(
        "   No base model has been selected yet.",
        file=sys.stderr,
    )
    print(
        "   Training should NOT run in CI.",
        file=sys.stderr,
    )
    print(
        "   No model weights should be committed to the repository.",
        file=sys.stderr,
    )

    if config.get("base_model") == "TBD" or config.get("base_model_or_adapter") == "TBD":
        print(
            "\nERROR: Base model is 'TBD'. Select a base model before training.",
            file=sys.stderr,
        )
        sys.exit(1)

    # Step 8: Actual training would go here
    # This is a skeleton — the real training loop is not implemented.
    print(
        "\nNOTE: The actual training loop is not yet implemented. This is a skeleton script.",
    )
    print("To implement training, add the SFTTrainer setup and training call here.")
    print("See docs/MODEL_TRAINING_PLAN.md for the full training plan.")


if __name__ == "__main__":
    main()
