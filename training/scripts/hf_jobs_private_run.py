#!/usr/bin/env python3
"""CLI wrapper for running Kimari-4B smoke tests on Hugging Face Jobs.

Reads a smoke test config YAML and generates/submits HF Jobs commands.
By default does NOT submit any job. Requires --allow-submit --yes for actual submission.

IMPORTANT SECURITY RULES:
- No tokens accepted as arguments
- No tokens printed or logged
- No --token flag accepted
- Actual submission requires --allow-submit AND --yes
- No files uploaded

Usage:
    python training/scripts/hf_jobs_private_run.py \
        --config training/configs/hf_jobs_kimari4b_smoke.v0.yaml \
        --dry-run --json
    python training/scripts/hf_jobs_private_run.py \
        --config training/configs/hf_jobs_kimari4b_smoke.v0.yaml \
        --print-command
    python training/scripts/hf_jobs_private_run.py \
        --config training/configs/hf_jobs_kimari4b_smoke.v0.yaml \
        --allow-submit --yes
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

# Ensure sibling scripts (e.g. check_hf_jobs_access) are importable
sys.path.insert(0, str(Path(__file__).resolve().parent))

from check_hf_jobs_access import run_check as check_hf_jobs_access

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent


def parse_simple_yaml(path: Path) -> dict | None:
    """Parse YAML with PyYAML fallback to simple parser."""
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


def build_hf_jobs_command(config: dict) -> str:
    """Build the hf jobs run command from config."""
    flavor = config.get("flavor", "a10g-small")
    image = config.get("image", "pytorch/pytorch:2.6.0-cuda12.4-cudnn9-devel")
    commands = config.get("commands", [])

    # Build the command string that runs inside the container
    inner_cmd = " && ".join(commands)

    # Build the full hf jobs run command
    hf_cmd = f"hf jobs run --flavor {flavor} {image} bash -lc '{inner_cmd}'"
    return hf_cmd


def check_hf_cli() -> bool:
    """Check if hf CLI is available."""
    try:
        result = subprocess.run(
            ["hf", "--version"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        return result.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


def check_hf_auth() -> bool:
    """Check if user is authenticated with hf CLI."""
    for cmd in [["hf", "auth", "whoami"], ["huggingface-cli", "whoami"]]:
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=10,
            )
            if result.returncode == 0 and result.stdout.strip():
                return True
        except (FileNotFoundError, subprocess.TimeoutExpired):
            continue
    return False


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run Kimari-4B smoke test on Hugging Face Jobs. "
        "By default does NOT submit. Requires --allow-submit --yes for actual submission. "
        "No tokens accepted as arguments."
    )
    parser.add_argument(
        "--config",
        type=Path,
        required=True,
        help="Path to HF Jobs smoke config YAML",
    )
    parser.add_argument(
        "--print-command",
        action="store_true",
        help="Print the hf jobs run command without executing it",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        dest="json_output",
        help="Output structured JSON result",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate config and show plan without submitting",
    )
    parser.add_argument(
        "--allow-submit",
        action="store_true",
        help="Allow actual job submission (requires --yes)",
    )
    parser.add_argument(
        "--yes",
        action="store_true",
        help="Confirm submission (requires --allow-submit)",
    )
    parser.add_argument(
        "--require-jobs-access",
        action="store_true",
        help="Verify HF Jobs access before submission; does NOT block --dry-run or --print-command",
    )
    # NOTE: No --token flag is accepted. Auth must be done via hf auth login.

    args = parser.parse_args()

    # Load config
    config_path = args.config
    if not config_path.exists():
        print(f"ERROR: Config file not found: {config_path}", file=sys.stderr)
        sys.exit(1)

    config = parse_simple_yaml(config_path)
    if config is None:
        print(f"ERROR: Failed to parse config: {config_path}", file=sys.stderr)
        sys.exit(1)

    # Validate config safety constraints
    if config.get("allow_training") is not False:
        print("ERROR: Smoke config must have allow_training: false", file=sys.stderr)
        sys.exit(1)
    if config.get("allow_hf_upload") is not False:
        print("ERROR: Smoke config must have allow_hf_upload: false", file=sys.stderr)
        sys.exit(1)

    # Build command
    hf_cmd = build_hf_jobs_command(config)

    # Prepare result
    result = {
        "job_name": config.get("job_name", "unknown"),
        "flavor": config.get("flavor", "a10g-small"),
        "image": config.get("image"),
        "max_budget_usd": config.get("max_budget_usd"),
        "run_type": config.get("run_type", "smoke_test"),
        "allow_training": config.get("allow_training", False),
        "allow_hf_upload": config.get("allow_hf_upload", False),
        "preview_gate_state": config.get("preview_gate_state", "BLOCKED"),
        "command_count": len(config.get("commands", [])),
        "forbidden_actions": config.get("forbidden", []),
        "hf_jobs_command": hf_cmd,
        "mode": "dry_run",
        "submitted": False,
        "job_id": None,
    }

    # --print-command: just print the command
    if args.print_command:
        print(hf_cmd)
        if not args.json_output:
            sys.exit(0)

    # --dry-run or default: validate and show plan, no submission
    if args.dry_run or (not args.allow_submit and not args.yes):
        result["mode"] = "dry_run"
        result["submitted"] = False
        if args.json_output:
            print(json.dumps(result, indent=2))
        else:
            print("\n" + "=" * 60)
            print("  HF Jobs Private Run — DRY RUN")
            print("=" * 60)
            print(f"\n  Job name:    {result['job_name']}")
            print(f"  Flavor:      {result['flavor']}")
            print(f"  Image:       {result['image']}")
            print(f"  Budget:      ${result['max_budget_usd']}")
            print(f"  Training:    {result['allow_training']}")
            print(f"  HF Upload:   {result['allow_hf_upload']}")
            print(f"  Gate:        {result['preview_gate_state']}")
            print(f"  Commands:    {result['command_count']}")
            print(f"\n  HF Command:\n    {hf_cmd}")
            print("\n  Forbidden:")
            for f in result["forbidden_actions"]:
                print(f"    X {f}")
            print("\n  No job was submitted. Use --allow-submit --yes to submit.")
            print("=" * 60)
        sys.exit(0)

    # Actual submission: requires both --allow-submit AND --yes
    if args.allow_submit and not args.yes:
        print("ERROR: --allow-submit requires --yes to confirm submission.", file=sys.stderr)
        print("Usage: --allow-submit --yes", file=sys.stderr)
        sys.exit(1)

    if args.yes and not args.allow_submit:
        print("ERROR: --yes requires --allow-submit.", file=sys.stderr)
        sys.exit(1)

    # Both flags present — check prerequisites
    if not check_hf_cli():
        print("ERROR: 'hf' CLI not found. Install with: pip install huggingface_hub[cli]", file=sys.stderr)
        sys.exit(1)

    if not check_hf_auth():
        print("ERROR: Not authenticated with HF. Run: hf auth login", file=sys.stderr)
        print("  Or: huggingface-cli login", file=sys.stderr)
        print("  NEVER pass tokens as arguments or in commands.", file=sys.stderr)
        sys.exit(1)

    # --require-jobs-access: verify Jobs access before actual submission
    if args.require_jobs_access:
        access_result = check_hf_jobs_access()
        if not access_result.get("can_continue_to_smoke", False):
            likely_reason = access_result.get("likely_reason", "unknown reason")
            print(
                f"ERROR: HF Jobs access check failed: {likely_reason}. "
                f"Use --dry-run or --print-command to proceed without submission, "
                f"or use a fallback runner.",
                file=sys.stderr,
            )
            sys.exit(1)

    # Submit the job
    result["mode"] = "submit"
    print(f"Submitting job: {result['job_name']}")
    print(f"Command: {hf_cmd}")

    try:
        submit_result = subprocess.run(
            hf_cmd.split(),
            capture_output=True,
            text=True,
            timeout=300,
        )
        result["submit_exit_code"] = submit_result.returncode
        result["submit_stdout"] = submit_result.stdout.strip()
        result["submit_stderr"] = submit_result.stderr.strip()
        result["submitted"] = submit_result.returncode == 0

        # Try to extract job_id from output
        for line in submit_result.stdout.splitlines():
            if "job" in line.lower() and "id" in line.lower():
                result["job_id"] = line.strip()
                break

        if args.json_output:
            print(json.dumps(result, indent=2))
        else:
            if result["submitted"]:
                print("\n  Job submitted successfully!")
                if result["job_id"]:
                    print(f"  Job ID: {result['job_id']}")
                print("  Check status: python training/scripts/hf_jobs_status.py --job-id <id>")
            else:
                print("\n  Job submission failed!")
                print(f"  Error: {submit_result.stderr}")

    except subprocess.TimeoutExpired:
        print("ERROR: Job submission timed out", file=sys.stderr)
        result["submitted"] = False
        result["error"] = "timeout"
        if args.json_output:
            print(json.dumps(result, indent=2))
        sys.exit(1)
    except FileNotFoundError:
        print("ERROR: 'hf' command not found", file=sys.stderr)
        result["submitted"] = False
        result["error"] = "hf_not_found"
        if args.json_output:
            print(json.dumps(result, indent=2))
        sys.exit(1)


if __name__ == "__main__":
    main()
