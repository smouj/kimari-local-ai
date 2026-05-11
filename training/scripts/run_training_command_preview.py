#!/usr/bin/env python3
"""CLI that prints the recommended training command for a config.

Reads a training config YAML and produces:
- recommended_command (full CLI command to run)
- recommended_environment (GPU requirements)
- expected_outputs (list of files that will be produced)
- forbidden_commit_patterns (patterns that must not be committed)
- safety_warnings (list of warnings)

No training, no downloads, no model access.

Usage:
    python training/scripts/run_training_command_preview.py \\
        --config training/configs/kimari_sft_lora.v0.example.yaml
    python training/scripts/run_training_command_preview.py \\
        --config training/configs/kimari_sft_lora.v0.example.yaml --json
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

DEFAULT_CONFIG = PROJECT_ROOT / "training" / "configs" / "kimari_sft_lora.v0.example.yaml"

FORBIDDEN_COMMIT_PATTERNS = [
    "*.safetensors",
    "*.bin",
    "*.pt",
    "*.ckpt",
    "*.gguf",
    "wandb/",
    "runs/",
]

SAFETY_WARNINGS = [
    "Real training must not run in CI",
    "No model weights should be committed to the repository",
    "output_dir must be gitignored before training",
    "No GGUF or adapter weights should be tracked in git",
    "Ensure public_release_allowed=false and hf_upload_allowed=false",
    "Preview gate must remain BLOCKED during private training",
    "Never upload private training artifacts to Hugging Face",
    "Run --dry-run first to validate config before real training",
]


# ---------------------------------------------------------------------------
# YAML parser with pyyaml fallback
# ---------------------------------------------------------------------------


def parse_simple_yaml(path: Path) -> dict | None:
    """Parse YAML with pyyaml fallback to simple line parser."""
    try:
        import yaml

        with open(path) as f:
            return yaml.safe_load(f)
    except ImportError:
        pass

    text = path.read_text(encoding="utf-8")
    result: dict = {}
    current_list_key: str | None = None
    current_list: list | None = None

    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue

        if stripped.startswith("- ") and current_list_key is not None:
            item = stripped[2:].strip().strip('"').strip("'")
            if current_list is not None:
                current_list.append(item)
            continue

        if ":" in stripped:
            if current_list_key is not None and current_list is not None:
                result[current_list_key] = current_list
                current_list_key = None
                current_list = None

            key, _, value = stripped.partition(":")
            key = key.strip()
            value = value.strip().strip('"').strip("'")

            if not value:
                current_list_key = key
                current_list = []
            else:
                if value.lower() == "true":
                    result[key] = True
                elif value.lower() == "false":
                    result[key] = False
                elif value.lower() in ("null", "~", "none"):
                    result[key] = None
                else:
                    try:
                        result[key] = int(value)
                    except ValueError:
                        try:
                            result[key] = float(value)
                        except ValueError:
                            result[key] = value

    if current_list_key is not None and current_list is not None:
        result[current_list_key] = current_list

    return result


# ---------------------------------------------------------------------------
# Preview builder
# ---------------------------------------------------------------------------


def build_command_preview(config_path: Path, config: dict) -> dict:
    """Build the full training command preview from config."""
    config_rel = str(config_path)

    # Build the recommended command
    cmd_parts = ["python", "training/scripts/train_sft_lora.py", f"--config {config_rel}"]

    # Add optional flags based on config content
    if config.get("output_dir"):
        cmd_parts.append(f"# output_dir: {config['output_dir']}")

    recommended_command = " \\\n  ".join(cmd_parts)

    # Determine GPU requirements
    base_model = config.get("base_model", "unknown")
    max_seq = config.get("max_seq_length", 2048)
    lora_r = config.get("lora_r", 0)
    bf16 = config.get("bf16", False)

    if "3b" in base_model.lower() or "3B" in base_model:
        gpu_rec = "NVIDIA GPU with 12GB+ VRAM (RTX 3060 12GB or better) for QLoRA; 24GB+ for LoRA"
    elif "7b" in base_model.lower() or "7B" in base_model:
        gpu_rec = "NVIDIA GPU with 24GB+ VRAM (RTX 3090, RTX 4090, A5000) for QLoRA"
    else:
        gpu_rec = "NVIDIA GPU with CUDA support — VRAM depends on model size and LoRA config"

    recommended_environment = {
        "gpu": gpu_rec,
        "cuda": "Required for training (inference-only for GTX 1060/1080)",
        "python": ">= 3.10",
        "packages": ["torch", "transformers", "peft", "trl", "accelerate", "datasets"],
        "notes": f"base_model={base_model}, max_seq_length={max_seq}, lora_r={lora_r}, bf16={bf16}",
    }

    # Expected outputs
    output_dir = config.get("output_dir", "training/adapters/output")
    expected_outputs = [
        f"{output_dir}/adapter_config.json",
        f"{output_dir}/adapter_model.safetensors",
        f"{output_dir}/tokenizer.json",
        f"{output_dir}/tokenizer_config.json",
        f"{output_dir}/special_tokens_map.json",
        f"{output_dir}/trainer_state.json",
        f"{output_dir}/training_args.bin",
        f"{output_dir}/all_results.json",
    ]

    return {
        "recommended_command": recommended_command,
        "recommended_environment": recommended_environment,
        "expected_outputs": expected_outputs,
        "forbidden_commit_patterns": FORBIDDEN_COMMIT_PATTERNS,
        "safety_warnings": SAFETY_WARNINGS,
        "config_path": str(config_path),
        "base_model": base_model,
    }


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main() -> None:
    """CLI entry point for training command preview."""
    parser = argparse.ArgumentParser(
        description="Print the recommended training command for a config. No training, no downloads, no model access.",
    )
    parser.add_argument(
        "--config",
        type=Path,
        default=DEFAULT_CONFIG,
        help="Path to training config YAML (default: training/configs/kimari_sft_lora.v0.example.yaml)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        dest="json_output",
        help="Output structured JSON result",
    )

    args = parser.parse_args()

    config_path = args.config
    if not config_path.exists():
        print(f"ERROR: Config file not found: {config_path}", file=sys.stderr)
        sys.exit(1)

    config = parse_simple_yaml(config_path)
    if config is None or not isinstance(config, dict):
        print(f"ERROR: Failed to parse config file: {config_path}", file=sys.stderr)
        sys.exit(1)

    preview = build_command_preview(config_path, config)

    if args.json_output:
        print(json.dumps(preview, indent=2, default=str))
    else:
        print()
        print("=" * 60)
        print("  Training Command Preview")
        print("=" * 60)
        print()

        print("Recommended Command:")
        print(f"  {preview['recommended_command']}")
        print()

        print("Recommended Environment:")
        env = preview["recommended_environment"]
        print(f"  GPU:     {env['gpu']}")
        print(f"  CUDA:    {env['cuda']}")
        print(f"  Python:  {env['python']}")
        print(f"  Packages: {', '.join(env['packages'])}")
        print(f"  Notes:   {env['notes']}")
        print()

        print("Expected Outputs:")
        for out in preview["expected_outputs"]:
            print(f"  - {out}")
        print()

        print("Forbidden Commit Patterns:")
        for pattern in preview["forbidden_commit_patterns"]:
            print(f"  [NEVER COMMIT] {pattern}")
        print()

        print("Safety Warnings:")
        for warning in preview["safety_warnings"]:
            print(f"  \u26a0 {warning}")

        print()
        print("=" * 60)
        print("  No training will be performed. This is a preview only.")
        print("=" * 60)

    sys.exit(0)


if __name__ == "__main__":
    main()
