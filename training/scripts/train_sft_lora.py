#!/usr/bin/env python3
"""Kimari SFT LoRA Training Script (Skeleton).

This is an experimental training script. It:
- Reads configuration from a YAML file
- Validates config and dependencies
- Supports --dry-run for config validation without training
- Must NOT execute real training in CI
- Fails clearly if dependencies are missing
- Does NOT hardcode any base model

Dry-run mode (--dry-run):
- Reads config and validates every item with clear status
- Checks base_model is not "TBD" (warns clearly if it is)
- Checks dataset_path exists on disk if not "TBD" (warns if missing)
- Prints a complete training plan with estimated steps
- Does NOT import transformers / torch / peft / trl / accelerate
- Returns exit 0 even if training dependencies are not installed
- Makes no network calls, no model downloads, no real training

No network calls. No downloads.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Dependency helpers
# ---------------------------------------------------------------------------


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


def check_dependencies() -> list[str]:
    """Check for required training dependencies.

    Returns a list of missing package names. Empty list means all OK.
    Only call this when actually training — dry-run skips it.
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


# ---------------------------------------------------------------------------
# Config loading
# ---------------------------------------------------------------------------


def load_config(config_path: str) -> dict:
    """Load a YAML configuration file and return it as a dict.

    Exits with a clear error message if the file cannot be loaded.
    """
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


# ---------------------------------------------------------------------------
# Config validation (returns structured results for dry-run reporting)
# ---------------------------------------------------------------------------


class ConfigItem:
    """A single config check result."""

    def __init__(self, key: str, value: object, status: str, message: str = "") -> None:
        self.key = key
        self.value = value
        self.status = status  # "ok", "warn", "fail"
        self.message = message

    @property
    def symbol(self) -> str:
        return {"ok": "\u2713", "warn": "\u26a0", "fail": "\u2717"}.get(self.status, "?")

    def __str__(self) -> str:
        val_repr = json.dumps(self.value) if not isinstance(self.value, str) else self.value
        line = f"  {self.symbol} {self.key:<22s} {val_repr}"
        if self.message:
            line += f"  ({self.message})"
        return line


def validate_config_items(config: dict) -> list[ConfigItem]:
    """Validate every important config key and return structured results.

    Each returned ConfigItem has a status of "ok", "warn", or "fail" with a
    human-readable message explaining any issues.
    """
    items: list[ConfigItem] = []

    # --- Base model ---
    base_model = config.get("base_model") or config.get("base_model_or_adapter")
    if not base_model:
        items.append(
            ConfigItem("base_model", "NOT SET", "fail", "No 'base_model' or 'base_model_or_adapter' key found")
        )
    elif base_model == "TBD":
        items.append(
            ConfigItem("base_model", "TBD", "warn", "Base model is TBD — you must select a model before training")
        )
    else:
        items.append(ConfigItem("base_model", base_model, "ok"))

    # --- Output dir ---
    output_dir = config.get("output_dir")
    if not output_dir:
        items.append(ConfigItem("output_dir", "NOT SET", "fail", "No output directory specified"))
    else:
        items.append(ConfigItem("output_dir", output_dir, "ok"))

    # --- Dataset path ---
    dataset_path = config.get("dataset_path") or config.get("preference_dataset_path")
    if not dataset_path:
        items.append(
            ConfigItem("dataset_path", "NOT SET", "fail", "No 'dataset_path' or 'preference_dataset_path' specified")
        )
    elif dataset_path == "TBD":
        items.append(
            ConfigItem("dataset_path", "TBD", "warn", "Dataset path is TBD — provide a real path before training")
        )
    else:
        p = Path(dataset_path)
        if p.exists():
            items.append(ConfigItem("dataset_path", dataset_path, "ok"))
        else:
            items.append(ConfigItem("dataset_path", dataset_path, "warn", "Path does not exist on disk"))

    # --- Max seq length ---
    max_seq = config.get("max_seq_length")
    if max_seq is not None:
        items.append(ConfigItem("max_seq_length", max_seq, "ok"))
    else:
        items.append(ConfigItem("max_seq_length", "NOT SET", "warn", "Will use model default"))

    # --- Precision ---
    bf16 = config.get("bf16")
    fp16 = config.get("fp16")
    if bf16 and fp16:
        items.append(ConfigItem("precision", "bf16+fp16", "warn", "Both bf16 and fp16 enabled — pick one"))
    elif bf16:
        items.append(ConfigItem("precision", "bf16", "ok"))
    elif fp16:
        items.append(ConfigItem("precision", "fp16", "ok"))
    else:
        items.append(ConfigItem("precision", "fp32", "ok"))

    # --- LoRA params ---
    lora_r = config.get("lora_r")
    if lora_r is not None:
        if lora_r <= 0:
            items.append(ConfigItem("lora_r", lora_r, "fail", "Must be positive"))
        else:
            items.append(ConfigItem("lora_r", lora_r, "ok"))
    else:
        items.append(ConfigItem("lora_r", "NOT SET", "warn", "Will use PEFT default"))

    lora_alpha = config.get("lora_alpha")
    if lora_alpha is not None:
        if lora_alpha <= 0:
            items.append(ConfigItem("lora_alpha", lora_alpha, "fail", "Must be positive"))
        else:
            items.append(ConfigItem("lora_alpha", lora_alpha, "ok"))
    else:
        items.append(ConfigItem("lora_alpha", "NOT SET", "warn", "Will use PEFT default"))

    lora_dropout = config.get("lora_dropout")
    if lora_dropout is not None:
        items.append(ConfigItem("lora_dropout", lora_dropout, "ok"))

    lora_targets = config.get("lora_target_modules")
    if lora_targets:
        items.append(
            ConfigItem(
                "lora_target_modules", ", ".join(lora_targets) if isinstance(lora_targets, list) else lora_targets, "ok"
            )
        )
    else:
        items.append(ConfigItem("lora_target_modules", "NOT SET", "warn", "Will use PEFT default"))

    # --- Training hyper-params ---
    lr = config.get("learning_rate")
    if lr is not None:
        if lr <= 0:
            items.append(ConfigItem("learning_rate", lr, "fail", "Must be positive"))
        else:
            items.append(ConfigItem("learning_rate", lr, "ok"))
    else:
        items.append(ConfigItem("learning_rate", "NOT SET", "warn", "No learning rate specified"))

    epochs = config.get("num_train_epochs")
    items.append(
        ConfigItem(
            "num_train_epochs", epochs if epochs is not None else "NOT SET", "ok" if epochs is not None else "warn"
        )
    )

    batch_size = config.get("per_device_train_batch_size")
    items.append(
        ConfigItem(
            "batch_size",
            batch_size if batch_size is not None else "NOT SET",
            "ok" if batch_size is not None else "warn",
        )
    )

    grad_accum = config.get("gradient_accumulation_steps")
    items.append(
        ConfigItem(
            "grad_accum",
            grad_accum if grad_accum is not None else "NOT SET",
            "ok" if grad_accum is not None else "warn",
        )
    )

    # --- Misc ---
    items.append(ConfigItem("seed", config.get("seed", "NOT SET"), "ok" if config.get("seed") is not None else "warn"))
    items.append(
        ConfigItem(
            "gradient_checkpointing",
            config.get("gradient_checkpointing", "NOT SET"),
            "ok" if config.get("gradient_checkpointing") is not None else "warn",
        )
    )
    items.append(
        ConfigItem(
            "report_to", config.get("report_to", "NOT SET"), "ok" if config.get("report_to") is not None else "warn"
        )
    )

    beta = config.get("beta")
    if beta is not None:
        items.append(ConfigItem("ORPO beta", beta, "ok"))

    return items


# ---------------------------------------------------------------------------
# Training plan & estimated steps
# ---------------------------------------------------------------------------


def count_dataset_records(dataset_path: str) -> int | None:
    """Try to count records in a dataset without importing heavy libraries.

    Supports:
    - JSON / JSONL files  (counts lines/entries)
    - Directories with .arrow / .parquet files (counts files as a rough proxy)
    Returns None if the path cannot be inspected.
    """
    p = Path(dataset_path)
    if not p.exists():
        return None

    # JSONL: count lines
    if p.is_file() and p.suffix in (".jsonl", ".json", ".ndjson"):
        try:
            with p.open("r", encoding="utf-8") as f:
                return sum(1 for _ in f)
        except Exception:
            return None

    # JSON array
    if p.is_file() and p.suffix == ".json":
        try:
            import json as _json

            data = _json.loads(p.read_text(encoding="utf-8"))
            if isinstance(data, list):
                return len(data)
        except Exception:
            pass
        return None

    # Directory: look for arrow/parquet files
    if p.is_dir():
        arrow_files = list(p.glob("*.arrow")) + list(p.glob("*.parquet"))
        if arrow_files:
            # Rough heuristic: we can't easily count rows from arrow/parquet
            # without pyarrow, so return the file count as a signal.
            # The user should inspect manually for exact counts.
            return None  # Can't count without pyarrow
        # Maybe a JSONL inside
        for ext in ("*.jsonl", "*.json", "*.ndjson"):
            inner = list(p.glob(ext))
            if inner:
                total = 0
                for fp in inner:
                    try:
                        with fp.open("r", encoding="utf-8") as f:
                            total += sum(1 for _ in f)
                    except Exception:
                        pass
                return total if total > 0 else None
        return None

    # CSV
    if p.is_file() and p.suffix == ".csv":
        try:
            with p.open("r", encoding="utf-8") as f:
                return sum(1 for _ in f) - 1  # subtract header
        except Exception:
            return None

    return None


def estimate_steps(config: dict) -> int | None:
    """Calculate estimated training steps from config + dataset size.

    Formula: steps = ceil(num_records * epochs / (batch_size * grad_accum))
    Returns None if any required value is missing.
    """
    import math

    dataset_path = config.get("dataset_path") or config.get("preference_dataset_path")
    if not dataset_path or dataset_path == "TBD":
        return None

    num_records = count_dataset_records(dataset_path)
    if num_records is None or num_records == 0:
        return None

    epochs = config.get("num_train_epochs")
    batch_size = config.get("per_device_train_batch_size")
    grad_accum = config.get("gradient_accumulation_steps")

    if not all(v is not None for v in (epochs, batch_size, grad_accum)):
        return None

    if batch_size <= 0 or grad_accum <= 0:
        return None

    steps = math.ceil(num_records * epochs / (batch_size * grad_accum))
    return steps


def print_training_plan(config: dict) -> None:
    """Print a structured training plan with status for each config item."""
    items = validate_config_items(config)

    print("=" * 60)
    print("  Kimari SFT LoRA Training Plan")
    print("=" * 60)
    print()

    has_warnings = False
    has_failures = False

    for item in items:
        print(item)
        if item.status == "warn":
            has_warnings = True
        elif item.status == "fail":
            has_failures = True

    print()

    # --- Estimated steps ---
    est = estimate_steps(config)
    dataset_path = config.get("dataset_path") or config.get("preference_dataset_path")

    batch_size = config.get("per_device_train_batch_size", "?")
    grad_accum = config.get("gradient_accumulation_steps", "?")

    if est is not None:
        effective_batch = (
            batch_size * grad_accum if isinstance(batch_size, int) and isinstance(grad_accum, int) else "?"
        )
        num_records = count_dataset_records(dataset_path) if dataset_path and dataset_path != "TBD" else None
        epochs = config.get("num_train_epochs", "?")

        print("-" * 60)
        print("  Step Estimation")
        print("-" * 60)
        if num_records is not None:
            print(f"  Dataset records:     {num_records}")
        print(f"  Epochs:              {epochs}")
        print(f"  Per-device batch:    {batch_size}")
        print(f"  Grad accum:          {grad_accum}")
        print(f"  Effective batch:     {effective_batch}")
        print(f"  Estimated steps:     ~{est}")
        print()
    else:
        print("-" * 60)
        print("  Step Estimation: SKIPPED (missing dataset path or params)")
        print("-" * 60)
        print()

    # --- Summary ---
    print("=" * 60)
    if has_failures:
        print("  Status: FAIL — fix the items marked with \u2717 above")
    elif has_warnings:
        print("  Status: PASS WITH WARNINGS — review items marked with \u26a0")
    else:
        print("  Status: ALL CHECKS PASSED \u2713")
    print("=" * 60)

    return has_warnings, has_failures


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> None:
    """CLI entry point for SFT LoRA training."""
    parser = argparse.ArgumentParser(
        description="Kimari SFT LoRA Training Script (Skeleton). "
        "Experimental \u2014 no training has been performed yet. "
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
        help="Validate config and show training plan without starting training. "
        "Does not require transformers/torch to be installed.",
    )

    args = parser.parse_args()

    # Step 1: Check PyYAML first (needed to load config — even for dry-run)
    check_yaml()

    # Step 2: Load config
    print(f"Loading config: {args.config}")
    config = load_config(args.config)

    # Step 3: Print training plan with per-item status
    print()
    has_warnings, has_failures = print_training_plan(config)

    # -------------------------------------------------------------------
    # --dry-run path: validate config, show plan, then exit 0
    # -------------------------------------------------------------------
    if args.dry_run:
        print()
        print("[DRY RUN] Config validated. No training was performed.")
        print("[DRY RUN] No model downloads. No network calls.")
        if has_warnings or has_failures:
            print("[DRY RUN] Review the warnings/failures above before training for real.")
        # Check if training deps are installed (informational only — still exit 0)
        missing = check_dependencies()
        if missing:
            print(f"[DRY RUN] NOTE: Training dependencies not installed: {', '.join(missing)}")
            print("[DRY RUN]       Install them before running without --dry-run.")
        sys.exit(0)

    # -------------------------------------------------------------------
    # Real training path (not dry-run)
    # -------------------------------------------------------------------

    # Step 4: Check training dependencies (only needed for real training)
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

    # Step 5: Block training if base model is TBD
    base_model = config.get("base_model") or config.get("base_model_or_adapter")
    if not base_model or base_model == "TBD":
        print(
            "\nERROR: Base model is 'TBD'. Select a base model before training.",
            file=sys.stderr,
        )
        sys.exit(1)

    # Step 6: Warn about experimental status
    print(
        "\n\u26a0  WARNING: This training code is EXPERIMENTAL.",
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

    # Step 7: Actual training would go here
    # This is a skeleton — the real training loop is not implemented.
    print(
        "\nNOTE: The actual training loop is not yet implemented. This is a skeleton script.",
    )
    print("To implement training, add the SFTTrainer setup and training call here.")
    print("See docs/MODEL_TRAINING_PLAN.md for the full training plan.")


if __name__ == "__main__":
    main()
