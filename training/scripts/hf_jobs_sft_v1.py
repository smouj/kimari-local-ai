#!/usr/bin/env python3
"""HF Jobs dry-run wrapper for Kimari Runtime 1.5B SFT v1.

Dry-run by default. In v0.1.60-alpha, real submission is always blocked even
when --allow-submit --yes are provided.
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


def build_training_command_args(config_path: Path) -> list[str]:
    return [
        "python",
        "training/scripts/train_sft_lora.py",
        "--config",
        str(config_path),
    ]


def shell_join(args: list[str]) -> str:
    quoted: list[str] = []
    for arg in args:
        if not arg or any(char.isspace() or char in "'\"$`\\" for char in arg):
            quoted.append("'" + arg.replace("'", "'\\''") + "'")
        else:
            quoted.append(arg)
    return " ".join(quoted)


def build_hf_jobs_command_args(config: dict[str, Any], config_path: Path) -> list[str]:
    run_id = str(config.get("run_id", "kimari-runtime-15b-sft-v1"))
    training_command = shell_join(build_training_command_args(config_path))
    guarded_command = " && ".join(
        [
            "python -m pip install -r training/requirements-training.txt",
            training_command,
            "python training/scripts/preflight_sft_v1.py --config " + shell_join([str(config_path)]),
        ]
    )
    return [
        "hf",
        "jobs",
        "run",
        "--flavor",
        DEFAULT_FLAVOR,
        "--image",
        DEFAULT_IMAGE,
        "--name",
        run_id,
        "--command",
        guarded_command,
    ]


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


def maybe_check_jobs_access(require: bool) -> tuple[bool | None, str]:
    if not require:
        return None, "not requested"
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


def build_result(args: argparse.Namespace, config: dict[str, Any], command_args: list[str]) -> dict[str, Any]:
    safety_errors = validate_safety(config)
    access_ok, access_message = maybe_check_jobs_access(args.require_jobs_access)
    wants_submit = bool(args.allow_submit and args.yes)
    dry_run = args.dry_run or not wants_submit
    return {
        "run_id": config.get("run_id"),
        "base_model": config.get("base_model"),
        "mode": "dry-run" if dry_run else "blocked-real-submit",
        "dry_run": dry_run,
        "print_command": args.print_command,
        "allow_submit_requested": args.allow_submit,
        "yes_confirmed": args.yes,
        "real_submit_allowed": False,
        "message": "Real submit blocked in v0.1.60-alpha" if wants_submit else "Dry-run only. No job submitted.",
        "hf_token_source": "env" if os.environ.get("HF_TOKEN") else "unset",
        "jobs_access_ok": access_ok,
        "jobs_access_message": access_message,
        "safety_errors": safety_errors,
        "hf_jobs_command_args": command_args if args.print_command else None,
        "hf_jobs_command_preview": shell_join(command_args) if args.print_command else None,
        "forbidden": [
            "public upload",
            "GGUF export",
            "gate transition",
            "public adapter repository",
            "token CLI arguments",
        ],
    }


def print_text(result: dict[str, Any]) -> None:
    print(f"HF Jobs SFT v1 wrapper: {result['mode']}")
    print(f"Run: {result.get('run_id')}")
    print(result["message"])
    if result.get("hf_jobs_command_preview"):
        print("\nCommand preview:")
        print(result["hf_jobs_command_preview"])
    if result.get("safety_errors"):
        print("\nSafety errors:")
        for error in result["safety_errors"]:
            print(f"  ✗ {error}")
    print("\nForbidden actions:")
    for item in result["forbidden"]:
        print(f"  ✗ {item}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Dry-run HF Jobs wrapper for SFT v1; real submit blocked in v0.1.60-alpha."
    )
    parser.add_argument("--config", type=Path, required=True, help="Path to SFT v1 YAML config")
    parser.add_argument("--dry-run", action="store_true", help="Dry-run only; default when submit flags are absent")
    parser.add_argument("--json", action="store_true", dest="json_output", help="Emit JSON")
    parser.add_argument("--print-command", action="store_true", help="Include safe HF Jobs command preview")
    parser.add_argument(
        "--allow-submit", action="store_true", help="Request real submission; still blocked in v0.1.60-alpha"
    )
    parser.add_argument(
        "--yes", action="store_true", help="Confirm real submission request; still blocked in v0.1.60-alpha"
    )
    parser.add_argument(
        "--require-jobs-access", action="store_true", help="Check hf jobs access using HF_TOKEN from environment"
    )
    args = parser.parse_args()

    if not args.config.exists():
        message = f"Config not found: {args.config}"
        if args.json_output:
            print(json.dumps({"status": "fail", "message": message}, indent=2))
        else:
            print(f"ERROR: {message}", file=sys.stderr)
        sys.exit(1)

    config = parse_simple_yaml(args.config)
    command_args = build_hf_jobs_command_args(config, args.config)
    result = build_result(args, config, command_args)
    status = "pass" if not result["safety_errors"] else "fail"
    result["status"] = status

    if args.json_output:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print_text(result)

    if args.allow_submit and args.yes:
        sys.exit(1)
    sys.exit(0 if status == "pass" else 1)


if __name__ == "__main__":
    main()
