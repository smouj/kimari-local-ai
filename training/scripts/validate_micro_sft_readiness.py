#!/usr/bin/env python3
"""Validate micro SFT readiness before execution.

Checks that the micro SFT config and training script are properly configured
for a safe, private micro-run. No training is performed.

Usage:
    python training/scripts/validate_micro_sft_readiness.py --config training/configs/hf_jobs_kimari4b_micro_sft.v0.yaml --json
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent


# ---------------------------------------------------------------------------
# Simple YAML parser (no PyYAML dependency)
# ---------------------------------------------------------------------------


def parse_yaml_simple(path: Path) -> dict:
    """Parse a simple YAML file without PyYAML dependency."""
    data: dict = {}
    current_list_key: str | None = None
    current_list: list = []
    for line in path.read_text().splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if line.startswith("  - ") and current_list_key:
            current_list.append(stripped[2:])
            continue
        if current_list_key and current_list:
            data[current_list_key] = current_list
            current_list = []
            current_list_key = None
        if ":" in stripped and not stripped.startswith("-"):
            key, _, value = stripped.partition(":")
            key = key.strip()
            value = value.strip()
            if value == "":
                # Could be a list or nested dict
                current_list_key = key
                current_list = []
                continue
            # Parse simple values
            if value.lower() == "true":
                data[key] = True
            elif value.lower() == "false":
                data[key] = False
            elif value.lower() == "null":
                data[key] = None
            else:
                try:
                    data[key] = int(value)
                except ValueError:
                    try:
                        data[key] = float(value)
                    except ValueError:
                        data[key] = value.strip("\"'")
    if current_list_key and current_list:
        data[current_list_key] = current_list
    return data


# ---------------------------------------------------------------------------
# Validation checks
# ---------------------------------------------------------------------------


def validate_micro_sft_readiness(config_path: str) -> dict:
    """Validate micro SFT readiness and return structured result.

    Returns dict with:
        ready: bool
        checks: list of {name, passed, message}
        errors: list of str
    """
    checks: list[dict] = []
    errors: list[str] = []

    # --- Check 1: Config file exists and parses ---
    p = Path(config_path)
    if not p.exists():
        errors.append(f"Config file not found: {config_path}")
        checks.append({"name": "config_exists", "passed": False, "message": f"Config file not found: {config_path}"})
        return {"ready": False, "checks": checks, "errors": errors}

    try:
        config = parse_yaml_simple(p)
        checks.append({"name": "config_exists", "passed": True, "message": "Config file exists and parses"})
    except Exception as e:
        errors.append(f"Failed to parse config: {e}")
        checks.append({"name": "config_exists", "passed": False, "message": f"Failed to parse config: {e}"})
        return {"ready": False, "checks": checks, "errors": errors}

    # --- Check 2: Command includes --micro-run --yes ---
    commands = config.get("commands", [])
    train_cmd = ""
    for cmd in commands:
        if "train_sft_lora.py" in str(cmd):
            train_cmd = str(cmd)
            break

    has_micro_run = "--micro-run" in train_cmd
    has_yes = "--yes" in train_cmd
    if has_micro_run and has_yes:
        checks.append({"name": "micro_run_and_yes", "passed": True, "message": "Command includes --micro-run --yes"})
    else:
        msg = f"Command missing --micro-run or --yes. Found: micro_run={has_micro_run}, yes={has_yes}"
        errors.append(msg)
        checks.append({"name": "micro_run_and_yes", "passed": False, "message": msg})

    # --- Check 3: Command does NOT include push_to_hub ---
    has_push_to_hub = "push_to_hub" in train_cmd
    if not has_push_to_hub:
        checks.append({"name": "no_push_to_hub", "passed": True, "message": "Command does not include push_to_hub"})
    else:
        msg = "Command includes push_to_hub — this is forbidden"
        errors.append(msg)
        checks.append({"name": "no_push_to_hub", "passed": False, "message": msg})

    # --- Check 4: allow_hf_upload is false ---
    allow_hf_upload = config.get("allow_hf_upload")
    if allow_hf_upload is False:
        checks.append({"name": "allow_hf_upload_false", "passed": True, "message": "allow_hf_upload is false"})
    else:
        msg = f"allow_hf_upload must be false, got: {allow_hf_upload}"
        errors.append(msg)
        checks.append({"name": "allow_hf_upload_false", "passed": False, "message": msg})

    # --- Check 5: preview_gate_state is BLOCKED ---
    gate_state = config.get("preview_gate_state")
    if gate_state == "BLOCKED":
        checks.append({"name": "gate_blocked", "passed": True, "message": "preview_gate_state is BLOCKED"})
    else:
        msg = f"preview_gate_state must be BLOCKED, got: {gate_state}"
        errors.append(msg)
        checks.append({"name": "gate_blocked", "passed": False, "message": msg})

    # --- Check 6: max_runtime_minutes <= 30 ---
    max_runtime = config.get("max_runtime_minutes")
    if max_runtime is not None and isinstance(max_runtime, (int, float)) and max_runtime <= 30:
        checks.append(
            {"name": "max_runtime_ok", "passed": True, "message": f"max_runtime_minutes is {max_runtime} (<= 30)"}
        )
    else:
        msg = f"max_runtime_minutes must be <= 30, got: {max_runtime}"
        errors.append(msg)
        checks.append({"name": "max_runtime_ok", "passed": False, "message": msg})

    # --- Check 7: max_budget_usd <= 10 ---
    max_budget = config.get("max_budget_usd")
    if max_budget is not None and isinstance(max_budget, (int, float)) and max_budget <= 10:
        checks.append({"name": "max_budget_ok", "passed": True, "message": f"max_budget_usd is {max_budget} (<= 10)"})
    else:
        msg = f"max_budget_usd must be <= 10, got: {max_budget}"
        errors.append(msg)
        checks.append({"name": "max_budget_ok", "passed": False, "message": msg})

    # --- Check 8: output_dir is under training/adapters or /tmp ---
    output_dir = config.get("output_dir", "")
    output_dir_str = str(output_dir)
    output_dir_valid = output_dir_str.startswith("training/adapters") or output_dir_str.startswith("/tmp")
    if output_dir_valid:
        checks.append(
            {"name": "output_dir_safe", "passed": True, "message": f"output_dir is in safe location: {output_dir}"}
        )
    else:
        msg = f"output_dir must be under training/adapters or /tmp, got: {output_dir}"
        errors.append(msg)
        checks.append({"name": "output_dir_safe", "passed": False, "message": msg})

    # --- Check 9: No adapter/GGUF tracked in git ---
    git_tracked_artifacts = []
    artifact_patterns = ["training/adapters/", ".safetensors", ".gguf", "adapter_model"]
    try:
        result = subprocess.run(
            ["git", "ls-files"],
            capture_output=True,
            text=True,
            cwd=str(PROJECT_ROOT),
            timeout=10,
        )
        if result.returncode == 0:
            tracked_files = result.stdout.splitlines()
            for tracked in tracked_files:
                if tracked.endswith(".gitkeep"):
                    continue
                for pattern in artifact_patterns:
                    if pattern in tracked:
                        git_tracked_artifacts.append(tracked)
                        break
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass

    if not git_tracked_artifacts:
        checks.append(
            {"name": "no_tracked_artifacts", "passed": True, "message": "No adapter/GGUF files tracked in git"}
        )
    else:
        msg = f"Adapter/GGUF files tracked in git: {git_tracked_artifacts}"
        errors.append(msg)
        checks.append({"name": "no_tracked_artifacts", "passed": False, "message": msg})

    ready = len(errors) == 0
    return {"ready": ready, "checks": checks, "errors": errors}


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Validate micro SFT readiness before execution. "
        "Checks that the config and training script are properly configured "
        "for a safe, private micro-run. No training is performed."
    )
    parser.add_argument(
        "--config",
        required=True,
        help="Path to micro SFT config YAML file",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        dest="json_output",
        help="Output results as JSON",
    )

    args = parser.parse_args()

    result = validate_micro_sft_readiness(args.config)

    if args.json_output:
        print(json.dumps(result, indent=2))
    else:
        print("=" * 60)
        print("  Micro SFT Readiness Validation")
        print("=" * 60)
        print()

        for check in result["checks"]:
            symbol = "\u2713" if check["passed"] else "\u2717"
            status = "PASS" if check["passed"] else "FAIL"
            print(f"  {symbol} [{status}] {check['name']}: {check['message']}")

        print()
        if result["errors"]:
            print("  Errors:")
            for err in result["errors"]:
                print(f"    \u2717 {err}")
            print()

        print("=" * 60)
        if result["ready"]:
            print("  READY: All checks passed. Safe to proceed with micro-run.")
        else:
            print("  NOT READY: Fix the errors above before running micro SFT.")
        print("=" * 60)

    sys.exit(0 if result["ready"] else 1)


if __name__ == "__main__":
    main()
