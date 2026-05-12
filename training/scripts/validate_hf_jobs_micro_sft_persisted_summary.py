#!/usr/bin/env python3
"""Validate micro SFT persisted summary for safety compliance.

Usage:
    python training/scripts/validate_hf_jobs_micro_sft_persisted_summary.py \
        --summary docs/assets/results/hf_jobs_micro_sft_persisted_summary.json \
        --json
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

MUST_BE_FALSE = [
    "adapter_committed_public",
    "hf_public_upload_performed",
    "gguf_generated",
    "auto_gate_transition",
]

MUST_BE_VALUES = {
    "gate_state": "BLOCKED",
    "manual_review_required": True,
}

FORBIDDEN_PATTERNS = [
    "sk-", "api_key", "password", "credential", "/home/",
    "hf_", "ghp_", "glpat-",
]


def validate_summary(summary_path: str) -> dict:
    """Validate summary against safety rules."""
    data = json.loads(Path(summary_path).read_text())
    errors = []
    warnings = []

    # Must-be-false checks
    for field in MUST_BE_FALSE:
        if data.get(field, None) is not False:
            errors.append(f"{field} must be false, got {data.get(field)}")

    # Must-be-value checks
    for field, expected in MUST_BE_VALUES.items():
        if data.get(field) != expected:
            errors.append(f"{field} must be {expected}, got {data.get(field)}")

    # Check for forbidden patterns in string values
    content = json.dumps(data).lower()
    for pattern in FORBIDDEN_PATTERNS:
        if pattern in content:
            # Allow known safe contexts
            if pattern in ["no private", "no secret", "forbidden", "must not"]:
                continue
            warnings.append(f"Potential sensitive pattern in summary: {pattern}")

    # Required fields
    required = [
        "run_id", "job_id", "status", "base_model",
        "adapter_generated", "adapter_persisted_private",
        "adapter_committed_public", "hf_public_upload_performed",
        "gguf_generated", "gate_state",
    ]
    for field in required:
        if field not in data:
            errors.append(f"Missing required field: {field}")

    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings,
        "summary_path": str(summary_path),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--summary", required=True, help="Path to summary JSON")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    result = validate_summary(args.summary)
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        for e in result["errors"]:
            print(f"  FAIL: {e}")
        for w in result["warnings"]:
            print(f"  WARN: {w}")
        print("RESULT:", "Valid!" if result["valid"] else f"{len(result['errors'])} error(s)")

    sys.exit(0 if result["valid"] else 1)


if __name__ == "__main__":
    main()