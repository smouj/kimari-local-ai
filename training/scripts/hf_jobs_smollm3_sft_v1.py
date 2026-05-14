#!/usr/bin/env python3
"""HF Jobs wrapper for Kimari-4B SmolLM3-3B SFT v1 — First Real Training.

This is the serious training run for the Kimari-4B model using SmolLM3-3B
as base with the full kimari_sft_v1 dataset.

Dry-run by default. Real submission requires --allow-submit --yes --require-jobs-access.

Safety gates maintained:
- No public release (gate stays BLOCKED)
- Adapter uploaded to PRIVATE repo only
- No GGUF export
- No public benchmark claims

Changes from 1.5B micro-run:
- Base model: SmolLM3-3B (3B params, Apache-2.0)
- max_steps: up to 1500 (vs 500 micro)
- LoRA r=32, target_modules extended (7 modules)
- Dataset: full kimari_sft_v1 (320 items, 3 epochs)
- max_seq_length: 4096
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_FLAVOR = "a10g-small"
DEFAULT_IMAGE = "pytorch/pytorch:2.5.1-cuda12.4-cudnn9-devel"
DEFAULT_REPO_URL = "https://github.com/smouj/kimari-local-ai.git"
DEFAULT_ADAPTER_REPO = "Smouj013/kimari4b-smollm3-sft-v1-adapter"
DEFAULT_CONFIG = "training/configs/kimari4b_smollm3_sft_v1.yaml"


def parse_simple_yaml(path: Path) -> dict[str, Any]:
    data: dict[str, Any] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or ":" not in stripped:
            continue
        key, _, raw_value = stripped.partition(":")
        value = raw_value.strip().strip('"').strip("'")
        lowered = value.lower()
        if lowered == "true":
            parsed: Any = True
        elif lowered == "false":
            parsed = False
        elif lowered in {"null", "~"}:
            parsed = None
        else:
            try:
                parsed = int(value)
            except ValueError:
                try:
                    parsed = float(value)
                except ValueError:
                    parsed = value
        data[key.strip()] = parsed
    return data


def shell_join(args: list[str]) -> str:
    quoted: list[str] = []
    for arg in args:
        if not arg or any(char.isspace() or char in "'\"$`\\" for char in arg):
            quoted.append("'" + arg.replace("'", "'\\''") + "'")
        else:
            quoted.append(arg)
    return " ".join(quoted)


def build_training_command_args(config_path: Path, full_run: bool = False) -> list[str]:
    mode_flag = "--full-run" if full_run else "--micro-run"
    return [
        "python",
        "training/scripts/train_sft_lora.py",
        "--config",
        str(config_path),
        mode_flag,
        "--yes",
    ]


def build_hf_jobs_command_args(
    config: dict[str, Any],
    config_path: Path,
    persist_adapter: bool = False,
    adapter_repo: str = "",
    full_run: bool = False,
) -> list[str]:
    training_command = shell_join(build_training_command_args(config_path, full_run=full_run))
    config_path_str = str(config_path)
    output_dir = config.get("output_dir", "training/runs/kimari4b-smollm3-sft-v1")

    steps = [
        "set -euo pipefail",
        "echo '=== Kimari-4B SmolLM3-3B SFT v1 ==='",
        "echo 'Base: HuggingFaceTB/SmolLM3-3B (Apache-2.0)'",
        "echo 'Method: QLoRA r=32, 7 target modules'",
        f"echo 'Config: {config_path_str}'",
        "nvidia-smi || echo 'No GPU info available'",
        "echo '--- Installing dependencies ---'",
        "apt-get update -qq && apt-get install -y -qq git",
        f"git clone {DEFAULT_REPO_URL} /workspace",
        "cd /workspace",
        "python -m pip install --quiet -r training/requirements-training.txt",
        "echo '--- Preflight check ---'",
        f"python training/scripts/preflight_sft_v1.py --config {config_path_str} --strict --json",
        "echo '--- Starting training ---'",
        training_command,
        "echo '--- Training complete ---'",
    ]

    if persist_adapter and adapter_repo:
        steps.extend([
            "echo '--- Persisting adapter to private repo ---'",
            f"python -c \"from huggingface_hub import HfApi; HfApi().upload_folder(folder_path='{output_dir}', repo_id='{adapter_repo}', repo_type='model', commit_message='SmolLM3-3B SFT v1 adapter - private')\"",
            f"echo 'Adapter uploaded to {adapter_repo}'",
        ])

    guarded_command = " && ".join(steps)
    cmd = ["hf", "jobs", "run", "--flavor", DEFAULT_FLAVOR]

    if persist_adapter:
        cmd.extend(["--secrets", "HF_TOKEN"])

    cmd.extend([DEFAULT_IMAGE, "bash", "-c", guarded_command])
    return cmd


def validate_safety(config: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    # These must be false — no public release of any kind
    strict_false = ["public_release_allowed", "hf_public_upload_allowed", "gguf_export_allowed"]
    for key in strict_false:
        if config.get(key) is not False:
            errors.append(f"{key} must be false")
    # push_to_hub must be false — we use explicit --persist-adapter instead
    if config.get("push_to_hub") is not False:
        errors.append("push_to_hub must be false (use --persist-adapter for private repo upload)")
    # gate must be BLOCKED
    if config.get("gate_state") != "BLOCKED":
        errors.append("gate_state must be BLOCKED")
    # max_steps sanity check (allow up to 2000 for real training)
    max_steps = int(config.get("max_steps", 999999))
    if max_steps > 2000:
        errors.append(f"max_steps={max_steps} exceeds limit of 2000")
    if max_steps < 100:
        errors.append(f"max_steps={max_steps} is too low for real training (minimum 100)")
    # epochs sanity
    epochs = int(config.get("epochs", 1))
    if epochs > 5:
        errors.append(f"epochs={epochs} exceeds limit of 5")
    return errors


def check_jobs_access() -> tuple[bool, str]:
    if not os.environ.get("HF_TOKEN"):
        return False, "HF_TOKEN is not set"
    try:
        proc = subprocess.run(
            ["hf", "jobs", "ps"],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            timeout=30,
            env=os.environ.copy(),
        )
    except FileNotFoundError:
        return False, "hf CLI not found"
    except subprocess.TimeoutExpired:
        return False, "hf jobs access check timed out"
    if proc.returncode == 0:
        return True, "hf jobs access OK"
    return False, "hf jobs access check failed"


def submit_hf_job(command_args: list[str]) -> tuple[bool, str, str | None]:
    try:
        proc = subprocess.run(
            command_args,
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            timeout=120,
            env=os.environ.copy(),
        )
    except FileNotFoundError:
        return False, "hf CLI not found", None
    except subprocess.TimeoutExpired:
        return False, "hf jobs submit timed out", None

    output = (proc.stdout or "") + (proc.stderr or "")
    job_id = None
    for line in output.splitlines():
        line = line.strip()
        if "Job started with ID" in line or "job_id" in line.lower():
            parts = line.split()
            for part in parts:
                if len(part) >= 24 and all(c in "0123456789abcdef" for c in part):
                    job_id = part
                    break

    if proc.returncode == 0:
        return True, f"Job submitted{f' (job_id: {job_id})' if job_id else ''}", job_id
    return False, f"hf jobs run failed (exit {proc.returncode}): {output[:500]}", job_id


def main() -> None:
    parser = argparse.ArgumentParser(
        description="HF Jobs wrapper for Kimari-4B SmolLM3-3B SFT v1. "
        "First real training run. Dry-run by default."
    )
    parser.add_argument("--config", type=Path, default=Path(PROJECT_ROOT / DEFAULT_CONFIG))
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--json", action="store_true", dest="json_output")
    parser.add_argument("--print-command", action="store_true")
    parser.add_argument("--allow-submit", action="store_true")
    parser.add_argument("--yes", action="store_true")
    parser.add_argument("--require-jobs-access", action="store_true")
    parser.add_argument("--persist-adapter", action="store_true", help="Upload adapter to private HF repo")
    parser.add_argument("--adapter-repo", type=str, default=DEFAULT_ADAPTER_REPO)
    parser.add_argument("--full-run", action="store_true", help="Full run (not micro)")
    args = parser.parse_args()

    if not args.config.exists():
        print(f"ERROR: Config not found: {args.config}", file=sys.stderr)
        sys.exit(1)

    config = parse_simple_yaml(args.config)
    command_args = build_hf_jobs_command_args(
        config, args.config,
        persist_adapter=args.persist_adapter,
        adapter_repo=args.adapter_repo,
        full_run=args.full_run,
    )
    safety_errors = validate_safety(config)
    command_str = shell_join(command_args)

    wants_submit = bool(args.allow_submit and args.yes)
    is_dry_run = args.dry_run or not wants_submit

    access_ok: bool | None = None
    access_message: str = "not requested"
    if args.require_jobs_access or wants_submit:
        access_ok, access_message = check_jobs_access()

    submit_allowed = wants_submit and not is_dry_run and len(safety_errors) == 0 and access_ok is True

    # Cost estimate
    max_steps = int(config.get("max_steps", 1000))
    flavor = DEFAULT_FLAVOR
    cost_per_hour = 1.00  # a10g-small
    # Rough estimate: ~60 steps/min for 3B QLoRA on A10G
    est_minutes = max_steps / 60
    est_cost = (est_minutes / 60) * cost_per_hour

    result: dict[str, Any] = {
        "run_id": config.get("run_id"),
        "base_model": config.get("base_model"),
        "base_license": config.get("base_license"),
        "method": config.get("method"),
        "lora_r": config.get("lora_r"),
        "max_steps": max_steps,
        "epochs": config.get("epochs"),
        "max_seq_length": config.get("max_seq_length"),
        "dataset": "kimari_sft_v1",
        "mode": "real-submit" if submit_allowed else ("blocked" if wants_submit else "dry-run"),
        "dry_run": is_dry_run,
        "real_submit_allowed": submit_allowed,
        "safety_errors": safety_errors,
        "jobs_access_ok": access_ok,
        "jobs_access_message": access_message,
        "hardware": flavor,
        "estimated_cost_usd": round(est_cost, 2),
        "estimated_time_minutes": round(est_minutes, 1),
        "forbidden": [
            "public release",
            "GGUF export",
            "gate transition",
            "public adapter repo",
        ],
        "full_run": args.full_run,
    }

    if args.print_command:
        result["command_preview"] = command_str

    if submit_allowed:
        success, msg, job_id = submit_hf_job(command_args)
        result["submit_success"] = success
        result["submit_message"] = msg
        result["job_id"] = job_id
        result["status"] = "pass" if success else "fail"
    else:
        if wants_submit and not submit_allowed:
            blockers = safety_errors[:]
            if access_ok is not True:
                blockers.append(f"jobs access: {access_message}")
            result["message"] = f"Submit blocked: {'; '.join(blockers)}"
            result["status"] = "fail"
        else:
            result["message"] = "Dry-run. No job submitted."
            result["status"] = "pass" if not safety_errors else "fail"

    if args.json_output:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print("=" * 50)
        print("Kimari-4B SmolLM3-3B SFT v1")
        print("=" * 50)
        print(f"  Base:     {config.get('base_model')} ({config.get('base_license')})")
        print(f"  Method:   {config.get('method').upper()} r={config.get('lora_r')}")
        print(f"  Steps:    {max_steps} ({config.get('epochs')} epochs)")
        print(f"  Seq len:  {config.get('max_seq_length')}")
        print(f"  Hardware: {flavor}")
        print(f"  Est time: ~{est_minutes:.0f} min (~${est_cost:.2f})")
        print(f"  Mode:     {result['mode']}")
        print(f"  Gate:     {config.get('gate_state')}")
        print()
        print(result["message"])
        if safety_errors:
            print("\n  Safety errors:")
            for e in safety_errors:
                print(f"    ✗ {e}")
        if args.print_command:
            print(f"\n  Command:\n  {command_str[:200]}...")

    sys.exit(0 if result.get("status") == "pass" else 1)


if __name__ == "__main__":
    main()
