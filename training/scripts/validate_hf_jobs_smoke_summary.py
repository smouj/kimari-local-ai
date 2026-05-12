#!/usr/bin/env python3
"""Validate HF Jobs smoke summary JSON.

Checks:
- Summary exists and is valid JSON
- training_performed=false
- adapter_generated=false
- hf_upload_performed=false
- gate_state=BLOCKED
- No forbidden patterns (tokens, private paths)

Usage:
    python training/scripts/validate_hf_jobs_smoke_summary.py --summary <file> --json
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

FORBIDDEN_PATTERNS = ["sk-", "api_key =", "password =", "credential"]
REQUIRED_FALSE_FIELDS = ["training_performed", "adapter_generated", "hf_upload_performed", "push_to_hub", "gguf_export"]
REQUIRED_BLOCKED_FIELDS = ["gate_state"]


def validate_summary(summary_path: str) -> dict:
    """Validate a smoke summary JSON file."""
    path = Path(summary_path)
    errors = []
    warnings = []

    if not path.exists():
        return {"valid": False, "errors": [f"File not found: {summary_path}"], "warnings": []}

    try:
        data = json.loads(path.read_text())
    except json.JSONDecodeError as e:
        return {"valid": False, "errors": [f"Invalid JSON: {e}"], "warnings": []}

    # Required false fields
    for field in REQUIRED_FALSE_FIELDS:
        if field not in data:
            errors.append(f"Missing field: {field}")
        elif data[field] is not False:
            errors.append(f"{field} must be false, got {data[field]}")

    # Gate state
    if "gate_state" not in data:
        errors.append("Missing field: gate_state")
    elif data["gate_state"] != "BLOCKED":
        errors.append(f"gate_state must be BLOCKED, got {data['gate_state']}")

    # Forbidden patterns
    content = json.dumps(data).lower()
    for pattern in FORBIDDEN_PATTERNS:
        if pattern.lower() in content:
            errors.append(f"Found forbidden pattern: {pattern}")

    # No private paths
    content_lower = path.read_text().lower()
    if "/home/" in content_lower:
        errors.append("Found private path pattern: /home/")

    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate HF Jobs smoke summary")
    parser.add_argument("--summary", required=True, help="Path to summary JSON")
    parser.add_argument("--json", action="store_true", help="JSON output")
    args = parser.parse_args()

    result = validate_summary(args.summary)

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        for e in result["errors"]:
            print(f"  FAIL: {e}")
        for w in result["warnings"]:
            print(f"  WARN: {w}")
        if result["valid"]:
            print("RESULT: All checks passed!")
        else:
            print(f"RESULT: {len(result['errors'])} error(s)")

    sys.exit(0 if result["valid"] else 1)


if __name__ == "__main__":
    main()
