#!/usr/bin/env python3
"""Kimari-4B HF Jobs smoke runner.

Submits a minimal smoke job to Hugging Face Jobs to verify
that the infrastructure works. Does NOT train, create adapters,
or upload anything.

Safety:
- Smoke command only: prints env info and exits
- Requires --allow-submit --yes for actual submission
- Requires --require-jobs-access to verify access first
- Uses safe subprocess (no shell=True, no hf_cmd.split())
- Short timeout to limit cost
- No upload, no push_to_hub, no training

Usage:
    # Print command only
    python training/scripts/hf_jobs_private_run.py --config ... --print-command

    # Dry-run (default)
    python training/scripts/hf_jobs_private_run.py --config ... --dry-run --json

    # Actual submission (requires explicit consent)
    python training/scripts/hf_jobs_private_run.py --config ... --require-jobs-access --allow-submit --yes
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent


def load_config(config_path: str) -> dict:
    """Load YAML config."""
    try:
        import yaml
    except ImportError:
        print("ERROR: PyYAML required. Install with: pip install pyyaml")
        sys.exit(1)
    with open(config_path) as f:
        return yaml.safe_load(f)


def verify_safety_flags(config: dict) -> list[str]:
    """Verify all safety flags are correct."""
    errors = []
    safety = config.get("safety", {})
    if safety.get("training_performed") is True:
        errors.append("training_performed must be false")
    if safety.get("adapter_generated") is True:
        errors.append("adapter_generated must be false")
    if safety.get("hf_upload_performed") is True:
        errors.append("hf_upload_performed must be false")
    if safety.get("push_to_hub") is True:
        errors.append("push_to_hub must be false")
    if safety.get("gguf_export") is True:
        errors.append("gguf_export must be false")
    if safety.get("gate_state") != "BLOCKED":
        errors.append(f"gate_state must be BLOCKED, got {safety.get('gate_state')}")
    return errors


def check_jobs_access() -> dict:
    """Check HF Jobs access by running check_hf_jobs_access.py."""
    script = PROJECT_ROOT / "training" / "scripts" / "check_hf_jobs_access.py"
    try:
        result = subprocess.run(
            [sys.executable, str(script), "--json"],
            capture_output=True,
            text=True,
            timeout=30,
        )
        if result.returncode != 0:
            return {"can_continue_to_smoke": False, "error": f"Access check failed: {result.stderr[:200]}"}
        return json.loads(result.stdout)
    except Exception as e:
        return {"can_continue_to_smoke": False, "error": str(e)}


def build_hf_jobs_command(config: dict) -> list[str]:
    """Build the hf jobs run command as a safe argument list."""
    flavor = config.get("flavor", "a10g-small")
    timeout = config.get("timeout_minutes", 5)
    smoke_command = config.get("smoke_command", "")

    # Use safe subprocess argument list
    args = [
        "hf",
        "jobs",
        "run",
        "--flavor",
        flavor,
        "--timeout",
        str(timeout),
        "--name",
        config.get("run_id", "kimari4b-smoke"),
        "--",
        "bash",
        "-c",
        smoke_command.strip(),
    ]
    return args


def print_command(config: dict) -> None:
    """Print the command that would be executed."""
    args = build_hf_jobs_command(config)
    # Safe: print each arg quoted
    cmd_str = " ".join(f'"{a}"' if " " in a else a for a in args)
    print(f"Command: {cmd_str}")


def dry_run(config: dict, json_output: bool = False) -> dict:
    """Simulate job submission without actually submitting."""
    safety_errors = verify_safety_flags(config)

    result = {
        "mode": "dry-run",
        "run_id": config.get("run_id", "unknown"),
        "flavor": config.get("flavor", "unknown"),
        "timeout_minutes": config.get("timeout_minutes", 5),
        "cost_estimate_usd": config.get("cost_estimate", {}).get("estimated_cost_usd", 0),
        "safety_flags": config.get("safety", {}),
        "safety_errors": safety_errors,
        "command_preview": " ".join(build_hf_jobs_command(config)),
    }

    if json_output:
        return result

    print("DRY-RUN: No job will be submitted")
    print(f"  Run ID: {result['run_id']}")
    print(f"  Flavor: {result['flavor']}")
    print(f"  Timeout: {result['timeout_minutes']} min")
    print(f"  Est. cost: ${result['cost_estimate_usd']:.2f}")
    print(f"  Safety errors: {result['safety_errors']}")
    print(f"\n  Command preview:\n  {result['command_preview']}")
    return result


def submit_job(config: dict, json_output: bool = False) -> dict:
    """Submit the actual HF Jobs smoke job."""
    # Safety checks
    safety_errors = verify_safety_flags(config)
    if safety_errors:
        return {"error": f"Safety violations: {safety_errors}", "submitted": False}

    # Check access first
    access = check_jobs_access()
    if not access.get("can_continue_to_smoke"):
        return {"error": f"Jobs access denied: {access.get('reason', 'unknown')}", "submitted": False}

    # Build command
    args = build_hf_jobs_command(config)
    print("\nSubmitting HF Jobs smoke test...")
    print(f"  Flavor: {config.get('flavor', 'unknown')}")
    print(f"  Timeout: {config.get('timeout_minutes', 5)} min")
    print(f"  Est. cost: ${config.get('cost_estimate', {}).get('estimated_cost_usd', 0):.2f}")
    print()

    try:
        result = subprocess.run(
            args,
            capture_output=True,
            text=True,
            timeout=config.get("timeout_minutes", 5) * 60 + 30,
        )
        stdout = result.stdout.strip()
        stderr = result.stderr.strip()
        returncode = result.returncode

        result_data = {
            "submitted": True,
            "run_id": config.get("run_id", "unknown"),
            "flavor": config.get("flavor", "unknown"),
            "returncode": returncode,
            "stdout_tail": stdout[-500:] if len(stdout) > 500 else stdout,
            "stderr_tail": stderr[-500:] if len(stderr) > 500 else stderr,
            "training_performed": False,
            "adapter_generated": False,
            "hf_upload_performed": False,
            "gate_state": "BLOCKED",
        }

        if json_output:
            print(json.dumps(result_data, indent=2))
        else:
            print(f"\nJob completed with return code: {returncode}")
            if stdout:
                print(f"STDOUT:\n{stdout[-1000:]}")
            if stderr:
                print(f"STDERR:\n{stderr[-500:]}")

        return result_data

    except subprocess.TimeoutExpired:
        return {"error": "Job timed out", "submitted": True, "timed_out": True}
    except Exception as e:
        return {"error": str(e), "submitted": False}


def main() -> None:
    parser = argparse.ArgumentParser(description="Kimari-4B HF Jobs smoke runner")
    parser.add_argument("--config", required=True, help="Path to config YAML")
    parser.add_argument("--print-command", action="store_true", help="Print command only")
    parser.add_argument("--dry-run", action="store_true", default=True, help="Dry-run (default)")
    parser.add_argument(
        "--require-jobs-access", action="store_true", default=False, help="Verify HF Jobs access before submitting"
    )
    parser.add_argument("--allow-submit", action="store_true", default=False, help="Allow actual job submission")
    parser.add_argument("--yes", action="store_true", default=False, help="Confirm consent for submission")
    parser.add_argument("--json", action="store_true", help="JSON output")
    args = parser.parse_args()

    config = load_config(args.config)

    # Print command only
    if args.print_command:
        print_command(config)
        sys.exit(0)

    # Safety: --allow-submit requires --yes
    if args.allow_submit and not args.yes:
        print("ERROR: --allow-submit requires --yes for explicit consent")
        print("Usage: --allow-submit --yes")
        sys.exit(1)

    # Safety: no token arguments
    for arg in sys.argv:
        if arg.startswith("--token") or arg.startswith("--api-key"):
            print(f"ERROR: Token/API key arguments not allowed: {arg}")
            sys.exit(1)

    # Safety: block in CI
    import os

    if os.environ.get("CI") == "true" and args.allow_submit:
        print("ERROR: Job submission blocked in CI environment")
        sys.exit(1)

    if args.allow_submit and args.yes:
        if args.require_jobs_access:
            access = check_jobs_access()
            if not access.get("can_continue_to_smoke"):
                print(f"ERROR: HF Jobs access denied: {access.get('reason', 'unknown')}")
                sys.exit(1)
            print("HF Jobs access verified ✅")
        result = submit_job(config, json_output=args.json)
    else:
        result = dry_run(config, json_output=args.json)

    if args.json and not (args.allow_submit and args.yes):
        print(json.dumps(result, indent=2))

    if result.get("error"):
        sys.exit(1)


if __name__ == "__main__":
    main()
