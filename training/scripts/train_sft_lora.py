#!/usr/bin/env python3
"""Kimari SFT LoRA Training Script.

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
import os
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

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
            return None
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


def is_gitignored(path: Path) -> bool:
    """Check if a path is covered by .gitignore."""
    try:
        result = subprocess.run(
            ["git", "check-ignore", str(path)],
            capture_output=True,
            text=True,
            cwd=str(PROJECT_ROOT),
            timeout=10,
        )
        return result.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass

    gitignore_path = PROJECT_ROOT / ".gitignore"
    if not gitignore_path.exists():
        return False

    try:
        gitignore_text = gitignore_path.read_text()
    except OSError:
        return False

    try:
        rel_path = path.relative_to(PROJECT_ROOT)
    except ValueError:
        rel_path = path

    rel_str = str(rel_path)

    for pattern in gitignore_text.splitlines():
        pattern = pattern.strip()
        if not pattern or pattern.startswith("#"):
            continue
        if pattern.endswith("/") and (rel_str.startswith(pattern) or rel_str.startswith(pattern.rstrip("/"))):
            return True
        if pattern.startswith("*."):
            suffix = pattern[1:]
            if rel_str.endswith(suffix):
                return True
        if rel_str == pattern or rel_str.startswith(pattern + "/"):
            return True

    return False


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
# CLI overrides
# ---------------------------------------------------------------------------


def apply_cli_overrides(config: dict, args) -> dict:
    """Override config values with explicitly provided CLI arguments.

    Only overrides values where the CLI arg is not None.
    Returns the updated config dict.
    """
    override_map = {
        "dataset_path": "dataset_path",
        "eval_dataset_path": "eval_dataset_path",
        "output_dir": "output_dir",
        "max_steps": "max_steps",
        "eval_steps": "eval_steps",
        "save_steps": "save_steps",
        "logging_steps": "logging_steps",
        "per_device_train_batch_size": "per_device_train_batch_size",
        "gradient_accumulation_steps": "gradient_accumulation_steps",
        "learning_rate": "learning_rate",
        "max_seq_length": "max_seq_length",
    }

    for cli_attr, config_key in override_map.items():
        cli_value = getattr(args, cli_attr, None)
        if cli_value is not None:
            config[config_key] = cli_value

    return config


# ---------------------------------------------------------------------------
# SFT Training
# ---------------------------------------------------------------------------


def run_sft_training(config: dict, micro_run: bool = True) -> dict:
    """Run SFT LoRA training with the given configuration.

    Imports torch/transformers/datasets/peft/trl ONLY inside this function.
    Returns a sanitized summary dict.
    """
    # --- Lazy imports (only inside this function) ---
    try:
        import torch  # noqa: F401
        from datasets import load_dataset
        from peft import LoraConfig, get_peft_model
        from transformers import AutoModelForCausalLM, AutoTokenizer, TrainingArguments
        from trl import SFTTrainer
    except ImportError as e:
        print(
            f"ERROR: Required training dependency not installed: {e}",
            file=sys.stderr,
        )
        print(
            "Install training dependencies with: pip install -r training/requirements-training.txt",
            file=sys.stderr,
        )
        sys.exit(1)

    # --- Determine base model ---
    base_model = config.get("base_model") or config.get("base_model_or_adapter")
    if not base_model or base_model == "TBD":
        print(
            "\nERROR: Base model is 'TBD' or not set. Select a base model before training.",
            file=sys.stderr,
        )
        sys.exit(1)

    output_dir = config.get("output_dir", "training/adapters/micro-sft-output")
    dataset_path = config.get("dataset_path")
    eval_dataset_path = config.get("eval_dataset_path")

    if not dataset_path:
        print(
            "ERROR: No dataset_path specified in config or CLI.",
            file=sys.stderr,
        )
        sys.exit(1)

    # --- Load dataset ---
    try:
        dataset = load_dataset("json", data_files=dataset_path, split="train")
    except Exception as e:
        print(f"ERROR: Failed to load training dataset from {dataset_path}: {e}", file=sys.stderr)
        sys.exit(1)

    eval_dataset = None
    if eval_dataset_path:
        try:
            eval_dataset = load_dataset("json", data_files=eval_dataset_path, split="train")
        except Exception as e:
            print(f"WARNING: Failed to load eval dataset from {eval_dataset_path}: {e}", file=sys.stderr)

    # --- Load tokenizer and model ---
    tokenizer = AutoTokenizer.from_pretrained(base_model, trust_remote_code=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    model = AutoModelForCausalLM.from_pretrained(
        base_model,
        trust_remote_code=True,
        torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
        device_map="auto" if torch.cuda.is_available() else None,
    )

    # --- LoRA config ---
    lora_r = config.get("lora_r", 8)
    lora_alpha = config.get("lora_alpha", 16)
    lora_dropout = config.get("lora_dropout", 0.05)
    lora_target_modules = config.get("lora_target_modules")

    lora_config = LoraConfig(
        r=lora_r,
        lora_alpha=lora_alpha,
        lora_dropout=lora_dropout,
        target_modules=lora_target_modules,
        bias="none",
        task_type="CAUSAL_LM",
    )

    model = get_peft_model(model, lora_config)

    # --- Training arguments ---
    max_steps = config.get("max_steps", 10)
    if micro_run:
        max_steps = min(max_steps, 10)

    training_args = TrainingArguments(
        output_dir=output_dir,
        max_steps=max_steps,
        per_device_train_batch_size=config.get("per_device_train_batch_size", 1),
        gradient_accumulation_steps=config.get("gradient_accumulation_steps", 1),
        learning_rate=config.get("learning_rate", 1e-4),
        logging_steps=config.get("logging_steps", 2),
        eval_steps=config.get("eval_steps", 5) if eval_dataset else None,
        save_steps=config.get("save_steps", 50),
        evaluation_strategy="steps" if eval_dataset else "no",
        report_to="none",
        push_to_hub=False,
        fp16=torch.cuda.is_available(),
        gradient_checkpointing=config.get("gradient_checkpointing", False),
        seed=config.get("seed", 42),
        max_seq_length=config.get("max_seq_length", 512),
    )

    # --- Train ---
    try:
        trainer = SFTTrainer(
            model=model,
            args=training_args,
            train_dataset=dataset,
            eval_dataset=eval_dataset,
            tokenizer=tokenizer,
        )
    except TypeError as e:
        print(
            f"ERROR: SFTTrainer API has changed or is incompatible: {e}",
            file=sys.stderr,
        )
        print(
            "This may be due to a trl version mismatch. Check your trl version and consult the trl changelog.",
            file=sys.stderr,
        )
        sys.exit(1)

    result = trainer.train()

    # --- Save adapter ---
    trainer.model.save_pretrained(output_dir)
    tokenizer.save_pretrained(output_dir)

    # --- Build sanitized summary ---
    adapter_generated = False
    adapter_path = Path(output_dir)
    if adapter_path.exists():
        adapter_files = list(adapter_path.glob("adapter_model.*")) + list(adapter_path.glob("adapter_config.json"))
        adapter_generated = len(adapter_files) > 0

    steps_completed = 0
    if hasattr(result, "global_step"):
        steps_completed = result.global_step
    elif isinstance(result, dict):
        steps_completed = result.get("global_step", max_steps)

    summary = {
        "training_performed": True,
        "adapter_generated": adapter_generated,
        "adapter_committed": False,
        "hf_upload_performed": False,
        "gguf_generated": False,
        "gate_state": "BLOCKED",
        "output_dir": output_dir,
        "micro_run": True,
        "steps_completed": steps_completed,
        "base_model": base_model,
    }

    return summary


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> None:
    """CLI entry point for SFT LoRA training."""
    parser = argparse.ArgumentParser(
        description="Kimari SFT LoRA Training Script. "
        "Experimental \u2014 v0.1.33-alpha supports micro-run mode only. "
        "No network calls in dry-run. No downloads in dry-run.",
    )
    parser.add_argument(
        "--config",
        required=False,
        help="Path to YAML configuration file (required unless --show-supported-flags)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate config and show training plan without starting training. "
        "Does not require transformers/torch to be installed.",
    )
    parser.add_argument(
        "--print-command",
        action="store_true",
        help="Print the recommended training command and exit.",
    )
    parser.add_argument(
        "--estimate-only",
        action="store_true",
        help="Print step estimation and exit (no full plan).",
    )
    parser.add_argument(
        "--require-dataset",
        action="store_true",
        help="Fail if dataset_path does not exist on disk.",
    )
    parser.add_argument(
        "--show-supported-flags",
        action="store_true",
        help="Print all supported CLI flags and exit. Does not require torch/transformers.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        dest="json_output",
        help="Output structured JSON (used with --show-supported-flags).",
    )
    # --- New CLI flags for v0.1.33 ---
    parser.add_argument(
        "--dataset-path",
        dest="dataset_path",
        type=str,
        default=None,
        help="Path to training dataset (JSONL)",
    )
    parser.add_argument(
        "--eval-dataset-path",
        dest="eval_dataset_path",
        type=str,
        default=None,
        help="Path to eval dataset (JSONL)",
    )
    parser.add_argument(
        "--output-dir",
        dest="output_dir",
        type=str,
        default=None,
        help="Output directory for adapter",
    )
    parser.add_argument(
        "--max-steps",
        dest="max_steps",
        type=int,
        default=None,
        help="Maximum training steps",
    )
    parser.add_argument(
        "--eval-steps",
        dest="eval_steps",
        type=int,
        default=None,
        help="Evaluation steps",
    )
    parser.add_argument(
        "--save-steps",
        dest="save_steps",
        type=int,
        default=None,
        help="Save checkpoint steps",
    )
    parser.add_argument(
        "--logging-steps",
        dest="logging_steps",
        type=int,
        default=None,
        help="Logging steps",
    )
    parser.add_argument(
        "--per-device-train-batch-size",
        dest="per_device_train_batch_size",
        type=int,
        default=None,
        help="Per-device training batch size",
    )
    parser.add_argument(
        "--gradient-accumulation-steps",
        dest="gradient_accumulation_steps",
        type=int,
        default=None,
        help="Gradient accumulation steps",
    )
    parser.add_argument(
        "--learning-rate",
        dest="learning_rate",
        type=float,
        default=None,
        help="Learning rate",
    )
    parser.add_argument(
        "--max-seq-length",
        dest="max_seq_length",
        type=int,
        default=None,
        help="Maximum sequence length",
    )
    parser.add_argument(
        "--micro-run",
        dest="micro_run",
        action="store_true",
        help="Enable micro-run mode (required for v0.1.33)",
    )
    parser.add_argument(
        "--yes",
        action="store_true",
        help="Confirm training execution",
    )

    args = parser.parse_args()

    # --show-supported-flags: print supported flags and exit (no imports needed)
    if args.show_supported_flags:
        supported = {
            "script": "training/scripts/train_sft_lora.py",
            "supported_flags": [
                "--config",
                "--dry-run",
                "--print-command",
                "--estimate-only",
                "--require-dataset",
                "--show-supported-flags",
                "--json",
                "--dataset-path",
                "--eval-dataset-path",
                "--output-dir",
                "--max-steps",
                "--eval-steps",
                "--save-steps",
                "--logging-steps",
                "--per-device-train-batch-size",
                "--gradient-accumulation-steps",
                "--learning-rate",
                "--max-seq-length",
                "--micro-run",
                "--yes",
            ],
            "note": "No training is performed by this script. --show-supported-flags does not import torch/transformers.",
        }
        if args.json_output:
            print(json.dumps(supported, indent=2))
        else:
            print("Supported flags for train_sft_lora.py:")
            for flag in supported["supported_flags"]:
                print(f"  {flag}")
        sys.exit(0)

    # Config is required for all other operations
    if not args.config:
        print("ERROR: --config is required", file=sys.stderr)
        sys.exit(1)

    # Step 1: Check PyYAML first (needed to load config — even for dry-run)
    check_yaml()

    # Step 2: Load config
    print(f"Loading config: {args.config}")
    config = load_config(args.config)

    # --require-dataset: fail if dataset_path doesn't exist
    if args.require_dataset:
        dataset_path = config.get("dataset_path") or config.get("preference_dataset_path")
        if not dataset_path or dataset_path == "TBD":
            print(
                "\nERROR: --require-dataset: No dataset_path specified or is TBD",
                file=sys.stderr,
            )
            sys.exit(1)
        dp = Path(dataset_path)
        if not dp.is_absolute():
            dp = PROJECT_ROOT / dp
        if not dp.exists():
            print(
                f"\nERROR: --require-dataset: Dataset path does not exist: {dataset_path}",
                file=sys.stderr,
            )
            sys.exit(1)

    # --print-command: print the recommended training command and exit
    if args.print_command:
        config_path = Path(args.config).resolve()
        cmd_parts = [
            "python",
            "training/scripts/train_sft_lora.py",
            f"--config {config_path}",
        ]
        if config.get("output_dir"):
            cmd_parts.append(f"# output_dir: {config['output_dir']}")
        cmd_parts.append("--micro-run")
        cmd_parts.append("--yes")
        print("# Recommended training command:")
        print(" \\\n  ".join(cmd_parts))
        print()
        print("# IMPORTANT: Real training must not run in CI.")
        print("# Run manually on a GPU machine only.")
        print("# v0.1.33-alpha: micro-run mode required (--micro-run).")
        sys.exit(0)

    # --estimate-only: print step estimation and exit
    if args.estimate_only:
        est = estimate_steps(config)
        dataset_path = config.get("dataset_path") or config.get("preference_dataset_path")
        num_records = count_dataset_records(dataset_path) if dataset_path and dataset_path != "TBD" else None
        epochs = config.get("num_train_epochs")
        batch_size = config.get("per_device_train_batch_size")
        grad_accum = config.get("gradient_accumulation_steps")

        est_info = {
            "dataset_path": dataset_path,
            "dataset_records": num_records,
            "epochs": epochs,
            "per_device_train_batch_size": batch_size,
            "gradient_accumulation_steps": grad_accum,
            "estimated_steps": est,
        }
        print(json.dumps(est_info, indent=2, default=str))
        sys.exit(0)

    # Step 3: Print training plan with per-item status
    print()
    has_warnings, has_failures = print_training_plan(config)

    # output_dir gitignored validation
    output_dir = config.get("output_dir")
    if output_dir:
        od = Path(output_dir)
        if not od.is_absolute():
            od = PROJECT_ROOT / od
        try:
            inside_repo = PROJECT_ROOT in od.resolve().parents or od.resolve() == PROJECT_ROOT
        except (ValueError, OSError):
            inside_repo = False
        if inside_repo:
            if is_gitignored(od):
                print(f"  \u2713 output_dir is gitignored: {output_dir}")
            else:
                print(
                    f"  \u26a0 WARNING: output_dir {output_dir} is inside the repo but NOT gitignored. "
                    "Training artifacts could be committed!",
                    file=sys.stderr,
                )

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

    # -------------------------------------------------------------------
    # v0.1.33 protections (MUST come before dependency check)
    # -------------------------------------------------------------------

    # CI guard: if CI=true, abort training (no deps needed for this check)
    if os.environ.get("CI") == "true":
        print(
            "\nERROR: CI=true detected. Training is not allowed in CI environments.",
            file=sys.stderr,
        )
        print(
            "   Training scripts must only run on dedicated GPU machines, not in CI.",
            file=sys.stderr,
        )
        sys.exit(1)

    # --micro-run required: v0.1.33 only supports micro-run
    if not args.micro_run:
        print(
            "\nERROR: --micro-run is required. v0.1.33-alpha only supports micro-run mode.",
            file=sys.stderr,
        )
        print(
            "   Add --micro-run to your command to enable micro-run training.",
            file=sys.stderr,
        )
        sys.exit(1)

    # --yes required: confirmation needed before training
    if not args.yes:
        print(
            "\nERROR: --yes is required to confirm training execution.",
            file=sys.stderr,
        )
        print(
            "   Add --yes to your command to confirm you want to proceed with training.",
            file=sys.stderr,
        )
        sys.exit(1)

    # output_dir inside repo and not gitignored warning
    output_dir = config.get("output_dir")
    if output_dir:
        od = Path(output_dir)
        if not od.is_absolute():
            od = PROJECT_ROOT / od
        try:
            inside_repo = PROJECT_ROOT in od.resolve().parents or od.resolve() == PROJECT_ROOT
        except (ValueError, OSError):
            inside_repo = False
        if inside_repo and not is_gitignored(od):
            print(
                f"\n\u26a0 WARNING: output_dir {output_dir} is inside the repo but NOT gitignored. "
                "Training artifacts could be committed!",
                file=sys.stderr,
            )
            print(
                "   Add the output directory to .gitignore before proceeding.",
                file=sys.stderr,
            )

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
        "   Real training must not run in CI.",
        file=sys.stderr,
    )
    print(
        "   No model weights should be committed to the repository.",
        file=sys.stderr,
    )

    # Step 7: Apply CLI overrides to config
    config = apply_cli_overrides(config, args)

    # Step 8: Run SFT training
    summary = run_sft_training(config, micro_run=True)

    # Step 9: Print sanitized summary
    print()
    print("=" * 60)
    print("  Training Summary (Sanitized)")
    print("=" * 60)
    for key, value in summary.items():
        print(f"  {key}: {value}")
    print("=" * 60)
    print()
    print("Gate state: BLOCKED — adapter not committed, not uploaded, not exported.")


if __name__ == "__main__":
    main()
