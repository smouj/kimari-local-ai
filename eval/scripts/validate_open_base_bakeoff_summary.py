#!/usr/bin/env python3
"""Validate open base bakeoff summary for Kimari Local AI.

Ensures:
- Only permissive-license candidates are marked as allowed
- No blocked model is marked as allowed
- No raw outputs committed
- No public benchmark claims
- Manual review required
- Gate state is BLOCKED

Usage:
    python eval/scripts/validate_open_base_bakeoff_summary.py --summary reports/evals/open_base_bakeoff_v1/summary.pending.json
    python eval/scripts/validate_open_base_bakeoff_summary.py --summary reports/evals/open_base_bakeoff_v1/summary.pending.json --json
"""

import argparse
import json
import sys
from pathlib import Path

ALLOWED_LICENSES = {"apache-2.0", "mit", "bsd-2-clause", "bsd-3-clause", "cc-by-4.0", "cc-by-sa-4.0"}
BLOCKED_LICENSE_KEYWORDS = {"nc", "non-commercial", "research", "research-only", "gemma", "llama", "meta", "custom"}


def validate_summary(summary_path: str, json_output: bool = False) -> tuple[bool, list[str]]:
    """Validate bakeoff summary file."""
    p = Path(summary_path)
    if not p.exists():
        return False, [f"Summary file not found: {summary_path}"]

    with open(p) as f:
        data = json.load(f)

    errors = []
    warnings = []

    # Required fields
    required_fields = [
        "schema",
        "run_id",
        "status",
        "candidates",
        "blocked_candidates",
        "gate_state",
        "manual_review_required",
        "public_benchmark_allowed",
        "raw_outputs_committed",
        "raw_outputs_commit_allowed",
    ]
    for field in required_fields:
        if field not in data:
            errors.append(f"Missing required field: {field}")

    # Gate must be BLOCKED
    if data.get("gate_state") != "BLOCKED":
        errors.append(f"gate_state must be BLOCKED, got: {data.get('gate_state')}")

    # Manual review must be required
    if not data.get("manual_review_required", False):
        errors.append("manual_review_required must be true")

    # Public benchmark must not be allowed
    if data.get("public_benchmark_allowed", True):
        errors.append("public_benchmark_allowed must be false")

    # Raw outputs must not be committed
    if data.get("raw_outputs_committed", False):
        errors.append("raw_outputs_committed must be false")

    # Raw outputs must not be allowed to commit
    if data.get("raw_outputs_commit_allowed", False):
        errors.append("raw_outputs_commit_allowed must be false")

    # Validate allowed candidates
    for c in data.get("candidates", []):
        model = c.get("model", "unknown")
        license_val = (c.get("license") or "").lower()
        allowed = c.get("allowed", True)
        blocked = c.get("blocked", False)

        if blocked and allowed:
            errors.append(f"Candidate {model} is both blocked and allowed")

        if allowed and not blocked and license_val not in ALLOWED_LICENSES:
            is_blocked = any(kw in license_val for kw in BLOCKED_LICENSE_KEYWORDS)
            if is_blocked:
                errors.append(f"Allowed candidate {model} has restricted license: {license_val}")

    # Validate blocked candidates
    for b in data.get("blocked_candidates", []):
        if b.get("allowed", False):
            errors.append(f"Blocked candidate {b.get('model')} marked as allowed")

    # Score status must be not_scored or manual_review
    score_status = data.get("score_status", "")
    if score_status not in ("not_scored", "manual_review", "pending"):
        warnings.append(f"Unexpected score_status: {score_status} (expected: not_scored, manual_review, or pending)")

    # License verification
    if not data.get("license_verified", False):
        warnings.append("license_verified is not true")

    if not data.get("all_candidates_permissive", False):
        warnings.append("all_candidates_permissive is not true")

    return len(errors) == 0, errors + [f"WARNING: {w}" for w in warnings]


def main():
    parser = argparse.ArgumentParser(description="Validate open base bakeoff summary")
    parser.add_argument("--summary", required=True, help="Path to summary JSON file")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args()

    valid, messages = validate_summary(args.summary, json_output=args.json)

    if args.json:
        result = {
            "valid": valid,
            "messages": messages,
            "summary_path": args.summary,
        }
        print(json.dumps(result, indent=2))
    else:
        status = "VALID" if valid else "INVALID"
        print(f"Bakeoff summary validation: {status}")
        for msg in messages:
            if msg.startswith("WARNING:"):
                print(f"  WARN: {msg[9:]}")
            else:
                print(f"  ERROR: {msg}")

    sys.exit(0 if valid else 1)


if __name__ == "__main__":
    main()
