#!/usr/bin/env python3
"""CLI command generator for Kimari-4B first private SFT run.

Reads the private SFT run config YAML and generates the exact commands
for the full private SFT execution pipeline.

Prints:
  - environment setup commands
  - dataset build command
  - preflight command
  - training dry-run command
  - real training command
  - baseline eval command
  - adapter eval command
  - manifest command
  - summary command
  - secret scan command
  - forbidden actions

No actual training, no downloads, no network.

Usage:
    python training/scripts/kimari4b_private_sft_command.py \\
        --config training/configs/kimari4b_private_sft_run.v0.yaml
    python training/scripts/kimari4b_private_sft_command.py \\
        --config training/configs/kimari4b_private_sft_run.v0.yaml --json
    python training/scripts/kimari4b_private_sft_command.py \\
        --config training/configs/kimari4b_private_sft_run.v0.yaml --markdown
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent


def parse_simple_yaml(path: Path) -> dict | None:
    """Parse YAML with PyYAML fallback to simple parser.

    Returns None if parsing fails.
    """
    try:
        import yaml

        with open(path) as f:
            return yaml.safe_load(f)
    except ImportError:
        pass

    text = path.read_text()
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


def generate_commands(config: dict, config_path: Path) -> dict:
    """Generate all commands for the private SFT run.

    Returns a dict with:
        run_id: str
        base_model: str
        environment_setup: list[str]
        dataset_build: list[str]
        preflight: list[str]
        training_dryrun: list[str]
        training_real: list[str]
        baseline_eval: list[str]
        adapter_eval: list[str]
        manifest: list[str]
        summary: list[str]
        secret_scan: list[str]
        forbidden_actions: list[str]
        gate_state: str
        public_release_allowed: bool
        hf_upload_allowed: bool
    """
    run_id = config.get("run_id", "kimari4b-smollm3-sft-v0-private-001")
    base_model = config.get("base_model", "HuggingFaceTB/SmolLM3-3B")
    sft_config = config.get("sft_config", "training/configs/kimari_sft_lora.v0.example.yaml")
    output_dir = config.get("output_dir", "training/adapters/kimari4b-smollm3-sft-v0")
    dataset_build_dir = config.get("dataset_build_dir", "dataset/build/kimari-v0")
    config_flag = f"--config {config_path}"

    environment_setup = [
        "git clone https://github.com/smouj/kimari-local-ai.git",
        "cd kimari-local-ai",
        "pip install -e .",
        "pip install -r training/requirements-training.txt",
    ]

    dataset_build = [
        f"python training/scripts/build_dataset_mix.py "
        f"--sft dataset/v0/sft_v0.jsonl "
        f"--preference dataset/v0/preference_v0.jsonl "
        f"--output-dir {dataset_build_dir} "
        f"--holdout dataset/v0/eval_holdout.jsonl",
        "python training/scripts/validate_training_ready.py --json",
    ]

    preflight = [
        f"python training/scripts/preflight_private_sft.py --run-config {config_path} --json",
    ]

    training_dryrun = [
        f"python training/scripts/kimari4b_private_sft_command.py {config_flag} --json",
        f"python training/scripts/train_sft_lora.py --config {sft_config} --dry-run",
    ]

    training_real = [
        f"python training/scripts/train_sft_lora.py "
        f"--config {sft_config} "
        f"--dataset-path {dataset_build_dir}/sft.train.jsonl "
        f"--eval-dataset-path {dataset_build_dir}/sft.eval.jsonl "
        f"--output-dir {output_dir}",
    ]

    baseline_eval = [
        "python eval/scripts/kimari4b_eval_plan.py --baseline-label smollm3-base --json",
        "python eval/kimarifit.py "
        "--model-label smollm3-base "
        "--endpoint http://127.0.0.1:11435/v1 "
        "--output eval/results/baseline-smollm3-q4km.json",
    ]

    adapter_eval = [
        "python eval/scripts/kimari4b_eval_plan.py "
        "--baseline-label smollm3-base "
        "--adapter-label kimari4b-smollm3-sft-v0 --json",
        "python eval/kimarifit.py "
        "--model-label kimari4b-smollm3-sft-v0 "
        "--endpoint http://127.0.0.1:11435/v1 "
        "--output eval/results/adapter-smollm3-sft-v0-q4km.json",
    ]

    manifest = [
        f"python training/scripts/create_adapter_manifest.py "
        f"--run-config {config_path} "
        f"--adapter-dir {output_dir} --dry-run",
    ]

    summary = [
        f"python training/scripts/postrun_private_sft.py "
        f"--run-config {config_path} "
        f"--adapter-dir {output_dir} --dry-run",
        "python eval/scripts/create_eval_summary.py "
        "--input eval/results/adapter-smollm3-sft-v0-q4km.json "
        "--output eval/results/adapter-smollm3-sft-v0-q4km-summary.json",
        "python eval/scripts/compare_runs.py "
        "--baseline eval/results/baseline-smollm3-q4km.json "
        "--adapter eval/results/adapter-smollm3-sft-v0-q4km.json "
        "--summary-output eval/results/comparison-sft-v0-vs-baseline-summary.json",
        f"python training/scripts/create_private_run_record.py "
        f"--run-config {config_path} "
        f"--manifest {output_dir}/MANIFEST.yaml "
        f"--eval-summary eval/results/adapter-smollm3-sft-v0-q4km-summary.json "
        f"--compare-summary eval/results/comparison-sft-v0-vs-baseline-summary.json "
        f"--dry-run",
    ]

    secret_scan = [
        "python scripts/security/scan_for_secrets.py --paths README.md docs training eval tests --json",
    ]

    forbidden_actions = [
        "DO NOT run training in CI",
        "DO NOT commit adapter weights (.safetensors, .bin)",
        "DO NOT commit training checkpoints (checkpoint-*/)",
        "DO NOT commit GGUF exports (*.gguf)",
        "DO NOT commit raw eval outputs (*-raw.json)",
        "DO NOT upload anything to Hugging Face",
        "DO NOT advance the preview gate automatically",
        "DO NOT claim Kimari-4B is published or available",
        "DO NOT save HF tokens in any file",
        "DO NOT share adapter weights outside private environment",
    ]

    return {
        "run_id": run_id,
        "base_model": base_model,
        "environment_setup": environment_setup,
        "dataset_build": dataset_build,
        "preflight": preflight,
        "training_dryrun": training_dryrun,
        "training_real": training_real,
        "baseline_eval": baseline_eval,
        "adapter_eval": adapter_eval,
        "manifest": manifest,
        "summary": summary,
        "secret_scan": secret_scan,
        "forbidden_actions": forbidden_actions,
        "gate_state": config.get("preview_gate_state", "BLOCKED"),
        "public_release_allowed": bool(config.get("public_release_allowed", False)),
        "hf_upload_allowed": bool(config.get("hf_upload_allowed", False)),
    }


def format_markdown(result: dict) -> str:
    """Format the command result as Markdown."""
    lines: list[str] = []

    lines.append(f"# Kimari-4B Private SFT Commands — {result['run_id']}")
    lines.append("")
    lines.append(f"- **Base model:** {result['base_model']}")
    lines.append(f"- **Gate state:** {result['gate_state']}")
    lines.append(f"- **Public release allowed:** {result['public_release_allowed']}")
    lines.append(f"- **HF upload allowed:** {result['hf_upload_allowed']}")
    lines.append("")

    sections = [
        ("Environment Setup", "environment_setup"),
        ("Dataset Build", "dataset_build"),
        ("Preflight", "preflight"),
        ("Training Dry-Run", "training_dryrun"),
        ("Real Training", "training_real"),
        ("Baseline Eval", "baseline_eval"),
        ("Adapter Eval", "adapter_eval"),
        ("Manifest", "manifest"),
        ("Summary", "summary"),
        ("Secret Scan", "secret_scan"),
    ]

    for title, key in sections:
        commands = result[key]
        lines.append(f"## {title}")
        lines.append("")
        for cmd in commands:
            lines.append("```bash")
            lines.append(cmd)
            lines.append("```")
            lines.append("")

    lines.append("## Forbidden Actions")
    lines.append("")
    for action in result["forbidden_actions"]:
        lines.append(f"- {action}")
    lines.append("")

    return "\n".join(lines)


def main() -> None:
    """CLI entry point for Kimari-4B private SFT command generation."""
    parser = argparse.ArgumentParser(
        description="Generate exact commands for Kimari-4B first private SFT run. "
        "No actual training, no downloads, no network.",
    )
    parser.add_argument(
        "--config",
        type=Path,
        required=True,
        help="Path to kimari4b_private_sft_run.v0.yaml config file",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        dest="json_output",
        help="Output structured JSON result",
    )
    parser.add_argument(
        "--markdown",
        action="store_true",
        dest="markdown_output",
        help="Output Markdown result",
    )

    args = parser.parse_args()

    # Load config
    config_path = args.config
    if not config_path.exists():
        print(f"ERROR: Config file not found: {config_path}", file=sys.stderr)
        sys.exit(1)

    config = parse_simple_yaml(config_path)

    if config is None:
        print(f"ERROR: Failed to parse config file: {config_path}", file=sys.stderr)
        sys.exit(1)

    if not isinstance(config, dict):
        print("ERROR: Config file does not contain a valid YAML mapping.", file=sys.stderr)
        sys.exit(1)

    # Generate commands
    result = generate_commands(config, config_path)

    # Output
    if args.json_output:
        print(json.dumps(result, indent=2))
    elif args.markdown_output:
        print(format_markdown(result))
    else:
        print("\n" + "=" * 60)
        print(f"  Kimari-4B Private SFT Commands — {result['run_id']}")
        print("=" * 60)
        print()
        print(f"  Base model: {result['base_model']}")
        print(f"  Gate state: {result['gate_state']}")
        print(f"  Public release: {result['public_release_allowed']}")
        print(f"  HF upload: {result['hf_upload_allowed']}")
        print()

        sections = [
            ("Environment Setup", "environment_setup"),
            ("Dataset Build", "dataset_build"),
            ("Preflight", "preflight"),
            ("Training Dry-Run", "training_dryrun"),
            ("Real Training", "training_real"),
            ("Baseline Eval", "baseline_eval"),
            ("Adapter Eval", "adapter_eval"),
            ("Manifest", "manifest"),
            ("Summary", "summary"),
            ("Secret Scan", "secret_scan"),
        ]

        for title, key in sections:
            commands = result[key]
            print(f"  {title}:")
            for cmd in commands:
                print(f"    $ {cmd}")
            print()

        print("  Forbidden Actions:")
        for action in result["forbidden_actions"]:
            print(f"    X {action}")
        print()
        print("=" * 60)
        print("  No training was performed. No downloads. No network calls.")
        print("=" * 60)

    sys.exit(0)


if __name__ == "__main__":
    main()
