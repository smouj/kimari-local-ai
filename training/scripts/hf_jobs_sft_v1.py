#!/usr/bin/env python3
"""HF Jobs wrapper for Kimari Runtime 1.5B SFT v1.

Dry-run by default. Real submission requires --allow-submit --yes --require-jobs-access.
In v0.1.61-alpha, real submission is allowed with all safeguards in place.
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
DEFAULT_ADAPTER_REPO = "Smouj013/kimari-runtime-15b-sft-v1-adapter"


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


def shell_join(args: list[str]) -> str:
    quoted: list[str] = []
    for arg in args:
        if not arg or any(char.isspace() or char in "'\"$`\\" for char in arg):
            quoted.append("'" + arg.replace("'", "'\\''") + "'")
        else:
            quoted.append(arg)
    return " ".join(quoted)


def build_hf_jobs_command_args(config: dict[str, Any], config_path: Path, persist_adapter: bool = False, adapter_repo: str = "", full_run: bool = False) -> list[str]:
    training_command = shell_join(build_training_command_args(config_path, full_run=full_run))
    config_path_str = str(config_path)
    output_dir = config.get("output_dir", "training/runs/kimari-runtime-15b-sft-v1")

    steps = [
        "apt-get update && apt-get install -y git",
        f"git clone {DEFAULT_REPO_URL} /workspace",
        "cd /workspace",
        "python -m pip install -r training/requirements-training.txt",
        f"python training/scripts/preflight_sft_v1.py --config {config_path_str} --strict --json",
        training_command,
    ]

    if persist_adapter and adapter_repo:
        # Upload adapter to private repo after training
        # Note: repo must already exist (created manually as private)
        # upload_folder doesn't need private=True if repo is already private
        steps.extend([
            f"python -c \"from huggingface_hub import HfApi; HfApi().upload_folder(folder_path='{output_dir}', repo_id='{adapter_repo}', repo_type='model')\"",
        ])

    guarded_command = " && ".join(steps)
    cmd = [
        "hf",
        "jobs",
        "run",
        "--flavor",
        DEFAULT_FLAVOR,
    ]

    # When persisting adapter to HF repo, we need HF_TOKEN with write access
    if persist_adapter:
        cmd.extend(["--secrets", "HF_TOKEN"])

    cmd.extend([
        DEFAULT_IMAGE,
        "bash",
        "-c",
        guarded_command,
    ])
    return cmd


def validate_safety(config: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    expected_false = ["push_to_hub", "public_release_allowed", "hf_public_upload_allowed", "gguf_export_allowed"]
    for key in expected_false:
        if config.get(key) is not False:
            errors.append(f"{key} must be false")
    if config.get("report_to") != "none":
        errors.append("report_to must be none")
    if config.get("gate_state") != "BLOCKED":
        errors.append("gate_state must be BLOCKED")
    if int(config.get("max_steps", 999999)) > 500:
        errors.append("max_steps must be <= 500")
    return errors


def validate_execution_order(command_str: str) -> list[str]:
    """Validate that preflight runs before training in the HF Jobs command."""
    errors: list[str] = []
    preflight_pos = command_str.find("preflight_sft_v1")
    training_pos = command_str.find("train_sft_lora")
    if preflight_pos == -1:
        errors.append("preflight_sft_v1 not found in execution command")
    if training_pos == -1:
        errors.append("train_sft_lora not found in execution command")
    if preflight_pos != -1 and training_pos != -1 and preflight_pos > training_pos:
        errors.append("preflight must run before training (preflight_after_training)")
    return errors


def check_jobs_access() -> tuple[bool, str]:
    """Check HF Jobs access using HF_TOKEN from environment."""
    if not os.environ.get("HF_TOKEN"):
        return False, "HF_TOKEN is not set; set it in the environment, never as a CLI argument"
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
        return True, "hf jobs access check passed"
    return False, "hf jobs access check failed; stderr redacted"


def submit_hf_job(command_args: list[str]) -> tuple[bool, str, str | None]:
    """Submit an HF Jobs run. Returns (success, message, job_id)."""
    # The hf jobs run CLI takes: --flavor FLAVOR IMAGE COMMAND
    # We need to pass IMAGE and COMMAND as separate args after flags.
    # command_args = ["hf", "jobs", "run", "--flavor", FLAVOR, IMAGE, COMMAND]
    # But the command string can be very long, so we pass it as a single arg.
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
    # Parse job ID from output like "Job started with ID: xxx"
    for line in output.splitlines():
        line = line.strip()
        if "Job started with ID" in line or "job_id" in line.lower():
            # Extract job ID
            parts = line.split()
            for part in parts:
                # Job IDs are hex strings like 6a04fedbe48bea4538b9c149
                if len(part) >= 24 and all(c in "0123456789abcdef" for c in part):
                    job_id = part
                    break

    if proc.returncode == 0:
        return True, f"Job submitted successfully{f' (job_id: {job_id})' if job_id else ''}", job_id
    return False, f"hf jobs run failed (exit {proc.returncode}): {output[:500]}", job_id


def main() -> None:
    parser = argparse.ArgumentParser(
        description="HF Jobs wrapper for SFT v1. Dry-run by default; "
        "real submission requires --allow-submit --yes --require-jobs-access."
    )
    parser.add_argument("--config", type=Path, required=True, help="Path to SFT v1 YAML config")
    parser.add_argument("--dry-run", action="store_true", help="Dry-run only; default when submit flags are absent")
    parser.add_argument("--json", action="store_true", dest="json_output", help="Emit JSON")
    parser.add_argument("--print-command", action="store_true", help="Include safe HF Jobs command preview")
    parser.add_argument("--allow-submit", action="store_true", help="Request real submission")
    parser.add_argument("--yes", action="store_true", help="Confirm real submission request")
    parser.add_argument(
        "--require-jobs-access", action="store_true", help="Check HF jobs access (required for real submit)"
    )
    parser.add_argument("--persist-adapter", action="store_true", help="Upload adapter to private HF repo after training")
    parser.add_argument("--adapter-repo", type=str, default=DEFAULT_ADAPTER_REPO, help="Private HF repo for adapter upload")
    parser.add_argument("--full-run", action="store_true", help="Submit guarded full-run instead of micro-run")
    args = parser.parse_args()

    if not args.config.exists():
        message = f"Config not found: {args.config}"
        if args.json_output:
            print(json.dumps({"status": "fail", "message": message}, indent=2))
        else:
            print(f"ERROR: {message}", file=sys.stderr)
        sys.exit(1)

    config = parse_simple_yaml(args.config)
    command_args = build_hf_jobs_command_args(config, args.config, persist_adapter=args.persist_adapter, adapter_repo=args.adapter_repo, full_run=args.full_run)
    safety_errors = validate_safety(config)
    command_str = shell_join(command_args) if args.print_command else ""
    execution_order_errors = validate_execution_order(command_str) if command_str else []
    all_errors = safety_errors + execution_order_errors

    wants_submit = bool(args.allow_submit and args.yes)
    is_dry_run = args.dry_run or not wants_submit

    # Check HF Jobs access if required
    access_ok: bool | None = None
    access_message: str = "not requested"
    if args.require_jobs_access or wants_submit:
        access_ok, access_message = check_jobs_access()

    # Determine if real submit can proceed
    submit_allowed = wants_submit and not is_dry_run and len(all_errors) == 0 and access_ok is True

    result: dict[str, Any] = {
        "run_id": config.get("run_id"),
        "base_model": config.get("base_model"),
        "mode": "real-submit" if submit_allowed else ("blocked-real-submit" if wants_submit else "dry-run"),
        "dry_run": is_dry_run,
        "print_command": args.print_command,
        "allow_submit_requested": args.allow_submit,
        "yes_confirmed": args.yes,
        "real_submit_allowed": submit_allowed,
        "safety_errors": all_errors,
        "hf_token_source": "env" if os.environ.get("HF_TOKEN") else "unset",
        "jobs_access_ok": access_ok,
        "jobs_access_message": access_message,
        "forbidden": [
            "public upload",
            "GGUF export",
            "gate transition",
            "public adapter repository",
            "token CLI arguments",
        ],
        "execution_order": [
            "install_training_requirements",
            "preflight_strict",
            "train_sft_lora",
        ],
        "preflight_before_training": True,
        "training_after_preflight": True,
        "full_run": args.full_run,
        "max_steps": config.get("max_steps"),
    }

    if args.print_command:
        result["hf_jobs_command_args"] = command_args
        result["hf_jobs_command_preview"] = shell_join(command_args)

    # Submit if allowed
    if submit_allowed:
        success, msg, job_id = submit_hf_job(command_args)
        result["submit_success"] = success
        result["submit_message"] = msg
        result["job_id"] = job_id
        if not success:
            result["status"] = "fail"
            result["message"] = f"Submit failed: {msg}"
        else:
            result["status"] = "pass"
            result["message"] = msg
    else:
        if wants_submit and not submit_allowed:
            blockers = []
            if all_errors:
                blockers.append(f"safety/execution errors: {all_errors}")
            if access_ok is not True:
                blockers.append(f"jobs access: {access_message}")
            result["message"] = f"Real submit blocked: {'; '.join(blockers)}"
            result["status"] = "fail"
        else:
            result["message"] = "Dry-run only. No job submitted."
            result["status"] = "pass" if not all_errors else "fail"

    if args.json_output:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(f"HF Jobs SFT v1: {result['mode']}")
        print(f"Run: {result.get('run_id')}")
        print(result["message"])
        if result.get("hf_jobs_command_preview"):
            print(f"\nCommand preview:\n{result['hf_jobs_command_preview']}")
        if all_errors:
            print("\nSafety errors:")
            for error in all_errors:
                print(f"  ✗ {error}")
        print("\nForbidden actions:")
        for item in result["forbidden"]:
            print(f"  ✗ {item}")

    sys.exit(0 if result.get("status") == "pass" and not (wants_submit and not submit_allowed) else 1)


if __name__ == "__main__":
    main()
