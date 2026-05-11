#!/usr/bin/env python3
"""HF Jobs micro SFT wrapper for Kimari-4B.

Prepares and optionally submits a micro SFT job to Hugging Face Jobs.
Micro SFT validates the training pipeline with minimal steps.

By default does NOT submit. Requires --allow-submit --yes for actual submission.
No --token argument. No token printing. No file uploads.
--require-smoke-summary is required for submission unless --override-smoke-gate is used.

Usage:
    python training/scripts/hf_jobs_micro_sft.py --config training/configs/hf_jobs_kimari4b_micro_sft.v0.yaml --dry-run --json
    python training/scripts/hf_jobs_micro_sft.py --config training/configs/hf_jobs_kimari4b_micro_sft.v0.yaml --print-command
    python training/scripts/hf_jobs_micro_sft.py --config training/configs/hf_jobs_kimari4b_micro_sft.v0.yaml --require-smoke-summary /tmp/smoke_summary.json --allow-submit --yes
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path


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


def check_smoke_summary_validated(config: dict, override: bool) -> tuple[bool, str]:
    """Check that a validated smoke summary exists before micro SFT."""
    if override:
        return True, "Smoke gate overridden with --override-smoke-gate"

    # Check for validated smoke summary
    smoke_summary_path = Path("/tmp/hf_jobs_smoke_summary.json")
    if not smoke_summary_path.exists():
        return False, "No smoke summary found at /tmp/hf_jobs_smoke_summary.json. Run smoke test first or use --override-smoke-gate."

    try:
        data = json.loads(smoke_summary_path.read_text())
        if data.get("status") != "completed":
            return False, f"Smoke summary status is '{data.get('status')}', not 'completed'. Complete smoke test first."
        if data.get("gate_state") != "BLOCKED":
            return False, f"Smoke summary gate_state is '{data.get('gate_state')}', expected 'BLOCKED'."
    except (json.JSONDecodeError, KeyError) as e:
        return False, f"Cannot read smoke summary: {e}"

    return True, "Smoke summary validated"


def validate_smoke_summary_file(summary_path: Path) -> tuple[bool, str]:
    """Validate a smoke summary JSON file.

    Checks that the file exists, contains valid JSON, has status == "completed",
    and gate_state == "BLOCKED".

    Never raises — always returns a (bool, str) tuple.
    """
    try:
        if not summary_path.exists():
            return False, f"Smoke summary file not found: {summary_path}"

        try:
            data = json.loads(summary_path.read_text())
        except json.JSONDecodeError as e:
            return False, f"Smoke summary file is not valid JSON: {e}"

        if not isinstance(data, dict):
            return False, f"Smoke summary file is not a JSON object, got: {type(data).__name__}"

        status = data.get("status")
        if status != "completed":
            return False, f"Smoke summary status is '{status}', expected 'completed'"

        gate_state = data.get("gate_state")
        if gate_state != "BLOCKED":
            return False, f"Smoke summary gate_state is '{gate_state}', expected 'BLOCKED'"

        return True, f"Smoke summary validated: {summary_path}"
    except Exception as e:
        return False, f"Unexpected error validating smoke summary: {e}"


def main() -> None:
    parser = argparse.ArgumentParser(
        description="HF Jobs micro SFT wrapper for Kimari-4B. "
        "Prepares and optionally submits a micro SFT job. "
        "No tokens accepted as arguments. No file uploads. "
        "Requires --allow-submit --yes for actual submission."
    )
    parser.add_argument(
        "--config",
        type=Path,
        required=True,
        help="Path to micro SFT config YAML",
    )
    parser.add_argument(
        "--print-command",
        action="store_true",
        dest="print_command",
        help="Print the hf jobs command without executing",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        dest="dry_run",
        help="Show what would happen without running",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        dest="json_output",
        help="Output as JSON",
    )
    parser.add_argument(
        "--allow-submit",
        action="store_true",
        dest="allow_submit",
        help="Allow job submission (requires --yes)",
    )
    parser.add_argument(
        "--yes",
        action="store_true",
        help="Confirm job submission (requires --allow-submit)",
    )
    parser.add_argument(
        "--override-smoke-gate",
        action="store_true",
        dest="override_smoke_gate",
        help="Override smoke test gate (not recommended)",
    )
    parser.add_argument(
        "--require-smoke-summary",
        type=Path,
        dest="require_smoke_summary",
        default=None,
        help="Path to validated smoke summary JSON. Required for submission unless --override-smoke-gate is used.",
    )

    args = parser.parse_args()

    # Load config
    if not args.config.exists():
        print(f"ERROR: Config file not found: {args.config}", file=sys.stderr)
        sys.exit(1)

    config = parse_yaml_simple(args.config)

    # Verify config safety constraints
    job_name = config.get("job_name", "unknown")
    flavor = config.get("flavor", "a10g-small")
    image = config.get("image", "")
    max_budget = config.get("max_budget_usd", 10)
    max_runtime = config.get("max_runtime_minutes", 30)
    allow_training = config.get("allow_training", False)
    allow_hf_upload = config.get("allow_hf_upload", True)  # Default to True so we catch missing false
    gate_state = config.get("preview_gate_state", "UNKNOWN")
    forbidden = config.get("forbidden", [])
    base_model = config.get("base_model", "unknown")
    run_type = config.get("run_type", "unknown")

    errors = []
    if not allow_training:
        errors.append("allow_training must be true for micro SFT")
    if allow_hf_upload is not False:
        errors.append("allow_hf_upload must be false")
    if gate_state != "BLOCKED":
        errors.append(f"preview_gate_state must be BLOCKED, got: {gate_state}")

    if errors and not args.dry_run:
        for e in errors:
            print(f"CONFIG ERROR: {e}", file=sys.stderr)
        sys.exit(1)

    # Check smoke summary (only blocks actual submission)
    smoke_ok, smoke_msg = check_smoke_summary_validated(config, args.override_smoke_gate)
    if not smoke_ok and not args.dry_run and not args.print_command and not args.override_smoke_gate:
        print(f"SMOKE GATE: {smoke_msg}", file=sys.stderr)
        sys.exit(1)

    # Validate --require-smoke-summary if provided
    smoke_summary_validated = False
    if args.require_smoke_summary is not None:
        smoke_summary_validated, smoke_summary_validation_msg = validate_smoke_summary_file(args.require_smoke_summary)
        if not smoke_summary_validated and not args.dry_run and not args.print_command and not args.override_smoke_gate:
            print(f"ERROR: {smoke_summary_validation_msg}", file=sys.stderr)
            sys.exit(1)
    else:
        smoke_summary_validation_msg = "--require-smoke-summary not provided"

    # Build the hf jobs command
    # Use a shell script approach: all commands joined by &&
    commands = config.get("commands", [])
    if not commands:
        print("ERROR: No commands defined in config", file=sys.stderr)
        sys.exit(1)

    shell_command = " && ".join(commands)

    # Build hf jobs run command
    hf_cmd = [
        "hf", "jobs", "run",
        "--flavor", flavor,
        "--image", image,
        "--name", job_name,
        "--command", shell_command,
    ]

    # Build result
    result = {
        "job_name": job_name,
        "run_type": run_type,
        "base_model": base_model,
        "flavor": flavor,
        "image": image,
        "max_budget_usd": max_budget,
        "max_runtime_minutes": max_runtime,
        "allow_training": allow_training,
        "allow_hf_upload": allow_hf_upload is False,
        "preview_gate_state": gate_state,
        "smoke_gate": smoke_msg,
        "smoke_summary_path": str(args.require_smoke_summary) if args.require_smoke_summary else None,
        "smoke_summary_validated": smoke_summary_validated if args.require_smoke_summary is not None else False,
        "forbidden_actions": forbidden,
        "safety_warnings": [
            "This will run a micro SFT job on HF Jobs infrastructure.",
            f"Estimated cost: under ${max_budget} USD.",
            "No files will be uploaded to Hugging Face.",
            "No adapters will be committed to the repository.",
            "No GGUF exports will be generated.",
            "Gate remains BLOCKED.",
            "Manual review required after completion.",
        ],
        "config_errors": errors,
    }

    # Print command mode
    if args.print_command:
        cmd_str = " ".join(hf_cmd)
        if args.json_output:
            result["hf_command"] = cmd_str
            print(json.dumps(result, indent=2))
        else:
            print("HF Jobs Command:")
            print("-" * 60)
            print(cmd_str)
            print("-" * 60)
            print()
            print("⚠️  Cost Warning: This will incur HF Jobs charges.")
            print(f"   Estimated budget: ≤${max_budget}")
            print()
            print("⚠️  Privacy Warning: Output stays in HF Jobs environment.")
            print("   No files uploaded to HF Hub.")
            print()
            print("Forbidden actions:")
            for f in forbidden:
                print(f"   ✗ {f}")
        return

    # Dry-run mode
    if args.dry_run:
        result["mode"] = "dry-run"
        result["message"] = "Dry-run only. No job submitted."
        if args.json_output:
            print(json.dumps(result, indent=2))
        else:
            print("=== Micro SFT Dry-Run ===")
            print(f"  Job name:    {job_name}")
            print(f"  Run type:    {run_type}")
            print(f"  Base model:  {base_model}")
            print(f"  Flavor:      {flavor}")
            print(f"  Budget cap:  ${max_budget}")
            print(f"  Runtime cap: {max_runtime} min")
            print(f"  Gate:        {gate_state}")
            print(f"  Smoke gate:  {smoke_msg}")
            print()
            print("  Safety warnings:")
            for w in result["safety_warnings"]:
                print(f"    ⚠️  {w}")
            print()
            print("  Forbidden actions:")
            for f in forbidden:
                print(f"    ✗ {f}")
            if errors:
                print()
                print("  Config errors:")
                for e in errors:
                    print(f"    ✗ {e}")
        return

    # Actual submission requires both flags
    if not args.allow_submit or not args.yes:
        result["mode"] = "blocked"
        result["message"] = "Submission blocked. Requires --allow-submit --yes."
        if args.json_output:
            print(json.dumps(result, indent=2))
        else:
            print("❌ Submission blocked.")
            print("   To submit a micro SFT job, you must use:")
            print(f"   python training/scripts/hf_jobs_micro_sft.py --config {args.config} --allow-submit --yes")
        sys.exit(1)

    # Check for errors before submitting
    if errors:
        for e in errors:
            print(f"CONFIG ERROR: {e}", file=sys.stderr)
        sys.exit(1)

    # Check smoke gate
    if not smoke_ok:
        print(f"SMOKE GATE: {smoke_msg}", file=sys.stderr)
        sys.exit(1)

    # Require --require-smoke-summary for submission
    if not args.override_smoke_gate:
        if args.require_smoke_summary is None:
            print("ERROR: --require-smoke-summary is required for submission. Provide a validated smoke summary path or use --override-smoke-gate.", file=sys.stderr)
            sys.exit(1)
        if not smoke_summary_validated:
            print(f"ERROR: {smoke_summary_validation_msg}", file=sys.stderr)
            sys.exit(1)

    # Verify hf CLI exists
    try:
        subprocess.run(["hf", "--version"], capture_output=True, timeout=10)
    except FileNotFoundError:
        print("ERROR: 'hf' CLI not found. Install with: pip install huggingface_hub", file=sys.stderr)
        sys.exit(1)

    # Submit the job
    if args.json_output:
        print(f"Submitting micro SFT job: {job_name}...", file=sys.stderr)

    try:
        proc = subprocess.run(
            hf_cmd,
            capture_output=True,
            text=True,
            timeout=120,
        )
        result["submission_returncode"] = proc.returncode
        result["submission_stderr_sanitized"] = "[REDACTED]" if proc.stderr else ""
        result["mode"] = "submitted"

        if proc.returncode != 0:
            result["status"] = "submission_failed"
            if args.json_output:
                print(json.dumps(result, indent=2))
            else:
                print(f"❌ Job submission failed (exit code {proc.returncode})")
                print("   Check HF CLI authentication and account.")
            sys.exit(1)

        # Try to extract job ID from output
        job_id = None
        for line in proc.stdout.splitlines():
            if "job" in line.lower() and "id" in line.lower():
                parts = line.split()
                for p in parts:
                    if len(p) > 8 and "-" in p:
                        job_id = p
                        break
        result["job_id"] = job_id
        result["status"] = "submitted"

        if args.json_output:
            print(json.dumps(result, indent=2))
        else:
            print(f"✅ Micro SFT job submitted: {job_name}")
            if job_id:
                print(f"   Job ID: {job_id}")
            print()
            print("   Next steps:")
            print("   1. Check status: python training/scripts/hf_jobs_status.py --job-id <id> --json")
            print("   2. View logs:    python training/scripts/hf_jobs_status.py --job-id <id> --logs --sanitize-logs")
            print("   3. Create summary: python training/scripts/create_hf_jobs_micro_sft_summary.py --job-id <id> --status completed --json")
            print("   4. Validate summary: python training/scripts/validate_hf_jobs_micro_sft_summary.py --summary /tmp/micro_sft_summary.json --json")
            print()
            print("   ⚠️  Gate remains BLOCKED. No adapters committed. No HF upload.")

    except subprocess.TimeoutExpired:
        print("ERROR: Job submission timed out", file=sys.stderr)
        sys.exit(1)
    except FileNotFoundError:
        print("ERROR: 'hf' CLI not found", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
