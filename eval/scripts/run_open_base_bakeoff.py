#!/usr/bin/env python3
"""Open License Base Model Bakeoff Runner for Kimari Local AI.

Evaluates permissive-license base models for Kimari model lines.
Only Apache 2.0 / MIT / BSD bases are allowed.
Gate: BLOCKED. No public benchmark claims.

Usage:
    python eval/scripts/run_open_base_bakeoff.py --config eval/configs/open_base_bakeoff_v1.yaml --dry-run
    python eval/scripts/run_open_base_bakeoff.py --config eval/configs/open_base_bakeoff_v1.yaml --dry-run --json
    python eval/scripts/run_open_base_bakeoff.py --config eval/configs/open_base_bakeoff_v1.yaml --print-command
    python eval/scripts/run_open_base_bakeoff.py --config eval/configs/open_base_bakeoff_v1.yaml --allow-submit --yes
"""

import argparse
import json
import sys
from pathlib import Path

try:
    import yaml as _yaml
except ImportError:
    _yaml = None

ALLOWED_LICENSES = {"apache-2.0", "mit", "bsd-2-clause", "bsd-3-clause", "cc-by-4.0", "cc-by-sa-4.0"}
BLOCKED_LICENSE_KEYWORDS = {"nc", "non-commercial", "research", "research-only", "gemma", "llama", "meta", "custom"}


def load_config(config_path: str) -> dict:
    """Load bakeoff config from YAML file."""
    p = Path(config_path)
    if not p.exists():
        print(f"ERROR: Config not found: {config_path}", file=sys.stderr)
        sys.exit(1)
    if _yaml is None:
        print("ERROR: PyYAML required. Install with: pip install pyyaml", file=sys.stderr)
        sys.exit(1)
    with open(p) as f:
        return _yaml.safe_load(f)


def validate_candidates(config: dict) -> list[str]:
    """Validate that all allowed candidates have permissive licenses."""
    errors = []
    for c in config.get("candidates", []):
        lic = (c.get("license") or "").lower()
        model = c.get("model", "unknown")
        blocked = c.get("blocked", False)
        allowed = c.get("allowed", True)

        if blocked and allowed:
            errors.append(f"Candidate {model} is both blocked and allowed")

        if allowed and not blocked and lic not in ALLOWED_LICENSES:
            # Check if it's close to an allowed license
            is_blocked = any(kw in lic for kw in BLOCKED_LICENSE_KEYWORDS)
            if is_blocked:
                errors.append(f"Candidate {model} has restricted license: {lic}")

    for b in config.get("blocked_candidates", []):
        if b.get("allowed", False):
            errors.append(f"Blocked candidate {b.get('model')} marked as allowed")

    return errors


def generate_plan(config: dict, phase: str = "subset10") -> dict:
    """Generate evaluation plan from config."""
    candidates = config.get("candidates", [])
    subset_size = config.get("subset_size", 10)

    if phase == "smoke":
        subset_size = 5
        eval_candidates = candidates
    elif phase == "subset30":
        subset_size = 30
        eval_candidates = candidates  # Will be filtered to top 2 by user
    else:
        eval_candidates = candidates

    plan = {
        "phase": phase,
        "subset_size": subset_size,
        "temperature": config.get("temperature", 0.2),
        "max_tokens": config.get("max_tokens", 256),
        "seed": config.get("seed", 42),
        "candidates_to_evaluate": [
            {"id": c["id"], "model": c["model"], "license": c["license"], "role": c["role"]}
            for c in eval_candidates
            if c.get("allowed", True) and not c.get("blocked", False)
        ],
        "blocked_candidates": [
            {"model": b["model"], "license": b["license"], "block_reason": b.get("block_reason", "")}
            for b in config.get("blocked_candidates", [])
        ],
        "safety": {
            "raw_outputs_commit_allowed": False,
            "public_benchmark_allowed": False,
            "manual_review_required": True,
            "gate_state": "BLOCKED",
        },
    }
    return plan


def main():
    parser = argparse.ArgumentParser(description="Open License Base Model Bakeoff Runner")
    parser.add_argument("--config", required=True, help="Path to bakeoff config YAML")
    parser.add_argument("--dry-run", action="store_true", default=True, help="Dry run (default: True)")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("--print-command", action="store_true", help="Print the command that would be run")
    parser.add_argument("--allow-submit", action="store_true", help="Allow actual submission (requires --yes)")
    parser.add_argument("--yes", "-y", action="store_true", help="Confirm submission")
    parser.add_argument("--require-jobs-access", action="store_true", help="Require HF Jobs access before submit")
    parser.add_argument("--phase", choices=["smoke", "subset10", "subset30"], default="subset10")
    args = parser.parse_args()

    config = load_config(args.config)

    # Validate candidates
    errors = validate_candidates(config)
    if errors:
        print("ERROR: Candidate validation failed:", file=sys.stderr)
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
        sys.exit(1)

    # Generate plan
    plan = generate_plan(config, phase=args.phase)

    # Safety checks
    if not args.allow_submit:
        args.dry_run = True

    if args.allow_submit and not args.yes:
        print("ERROR: --allow-submit requires --yes to confirm", file=sys.stderr)
        sys.exit(1)

    # Output
    result = {
        "status": "dry_run" if args.dry_run else "ready_to_submit",
        "config": args.config,
        "phase": args.phase,
        "plan": plan,
        "safety": {
            "raw_outputs_commit_allowed": False,
            "public_benchmark_allowed": False,
            "manual_review_required": True,
            "gate_state": "BLOCKED",
            "no_training": True,
            "no_public_weights": True,
            "no_adapter_upload": True,
        },
        "message": "Bakeoff plan generated. Dry run only — no evaluation executed."
        if args.dry_run
        else "Bakeoff plan ready for submission.",
    }

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"Bakeoff: {args.phase} phase")
        print(f"Candidates: {len(plan['candidates_to_evaluate'])} allowed, {len(plan['blocked_candidates'])} blocked")
        print(f"Subset size: {plan['subset_size']}")
        print("Gate: BLOCKED")
        print(f"Dry run: {args.dry_run}")
        if not args.dry_run:
            print("WARNING: Actual submission requires --allow-submit --yes")

    if args.dry_run:
        sys.exit(0)
    else:
        print("NOTE: Actual evaluation not yet implemented. Use --dry-run for planning.")
        sys.exit(0)


if __name__ == "__main__":
    main()
