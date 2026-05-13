#!/usr/bin/env python3
"""Run SFT v1 adapter vs base evaluation on KimariEval subset10.

Safety:
- Dry-run by default (no submission without --allow-submit --yes)
- No --token flag accepted
- No shell=True
- No .split() for command args
- Gate BLOCKED
- No public benchmark claims
- No raw outputs committed
"""

import argparse
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

EVAL_CONFIG = PROJECT_ROOT / "eval" / "configs" / "kimari_runtime_15b_sft_v1_eval_subset10.yaml"


def build_command_args(config_path: str, dry_run: bool = True, allow_submit: bool = False) -> list[str]:
    """Build safe command args list (no shell, no .split())."""
    args = [sys.executable, "-m", "eval.scripts.run_kimari_eval"]
    args.extend(["--config", str(config_path)])

    if dry_run:
        args.append("--dry-run")

    if not allow_submit:
        args.append("--dry-run")

    return args


def run_sft_v1_eval(
    config_path: str | None = None,
    dry_run: bool = True,
    json_output: bool = False,
    print_command: bool = False,
    allow_submit: bool = False,
    yes: bool = False,
    require_jobs_access: bool = False,
) -> bool:
    """Run SFT v1 eval with safety checks."""
    errors = []
    warnings = []

    config = Path(config_path) if config_path else EVAL_CONFIG

    # Safety: dry-run by default
    if not dry_run and not allow_submit:
        errors.append("Cannot run without --allow-submit flag")
    if not dry_run and not yes:
        errors.append("Cannot run without --yes confirmation")

    # Safety: no --token support
    # (This script does not accept --token)

    # Config check
    if not config.exists():
        errors.append(f"Eval config not found: {config}")
    else:
        config_text = config.read_text()
        if "BLOCKED" not in config_text:
            errors.append("Eval config must specify gate_state: BLOCKED")
        if "public_benchmark_allowed" not in config_text:
            errors.append("Eval config must specify public_benchmark_allowed")

    result = {
        "dry_run": dry_run,
        "config": str(config),
        "allow_submit": allow_submit and yes,
        "command": None,
        "errors": errors,
        "warnings": warnings,
    }

    if errors:
        result["status"] = "blocked"
        if json_output:
            print(json.dumps(result, indent=2))
        else:
            print("BLOCKED: Cannot proceed")
            for e in errors:
                print(f"  - {e}")
        return False

    # Build command
    cmd_args = build_command_args(str(config), dry_run=dry_run, allow_submit=allow_submit and yes)
    result["command"] = " ".join(cmd_args)

    if print_command:
        print(" ".join(cmd_args))
        if json_output:
            print(json.dumps(result, indent=2))
        return True

    if dry_run:
        result["status"] = "dry_run"
        result["message"] = "Dry-run: would execute eval with subset10 config"
        if json_output:
            print(json.dumps(result, indent=2))
        else:
            print(f"DRY-RUN: Would execute: {' '.join(cmd_args)}")
        return True

    # Actual execution would go here — for now, infrastructure only
    result["status"] = "not_executed"
    result["message"] = "Eval execution not yet implemented — infrastructure ready"
    if json_output:
        print(json.dumps(result, indent=2))
    else:
        print("Infrastructure ready — eval execution not yet implemented")
    return True


def main():
    parser = argparse.ArgumentParser(description="Run SFT v1 adapter vs base evaluation")
    parser.add_argument("--config", help="Path to eval config", default=None)
    parser.add_argument("--dry-run", action="store_true", help="Dry-run mode (default)")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("--print-command", action="store_true", help="Print command without executing")
    parser.add_argument("--allow-submit", action="store_true", help="Allow actual submission (requires --yes)")
    parser.add_argument("--yes", action="store_true", help="Confirm submission")
    parser.add_argument("--require-jobs-access", action="store_true", help="Validate HF Jobs access before submission")
    args = parser.parse_args()

    success = run_sft_v1_eval(
        config_path=args.config,
        dry_run=args.dry_run or not args.allow_submit,
        json_output=args.json,
        print_command=args.print_command,
        allow_submit=args.allow_submit,
        yes=args.yes,
        require_jobs_access=args.require_jobs_access,
    )
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
