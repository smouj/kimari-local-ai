#!/usr/bin/env python3
"""Validate micro SFT real summary."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REQUIRED_FALSE = ["adapter_committed", "hf_upload_performed", "push_to_hub", "gguf_generated"]
REQUIRED_TRUE_MAYBE = ["training_performed", "adapter_generated"]


def validate_summary(summary_path: str) -> dict:
    """Validate micro SFT summary."""
    path = Path(summary_path)
    errors = []
    warnings = []

    if not path.exists():
        return {"valid": False, "errors": [f"File not found: {summary_path}"], "warnings": []}

    try:
        data = json.loads(path.read_text())
    except json.JSONDecodeError as e:
        return {"valid": False, "errors": [f"Invalid JSON: {e}"], "warnings": []}

    # Must be false
    for field in REQUIRED_FALSE:
        if field not in data:
            errors.append(f"Missing field: {field}")
        elif data[field] is not False:
            errors.append(f"{field} must be false, got {data[field]}")

    # Gate must be BLOCKED
    if "gate_state" not in data:
        errors.append("Missing field: gate_state")
    elif data["gate_state"] != "BLOCKED":
        errors.append(f"gate_state must be BLOCKED, got {data['gate_state']}")

    # training_performed and adapter_generated can be true (this IS a training run)
    for field in REQUIRED_TRUE_MAYBE:
        if field not in data:
            warnings.append(f"Missing field: {field}")

    # No forbidden patterns
    content = path.read_text().lower()
    for pattern in ["sk-", "api_key =", "password =", "/home/"]:
        if pattern in content:
            errors.append(f"Found forbidden pattern: {pattern}")

    return {"valid": len(errors) == 0, "errors": errors, "warnings": warnings}


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate micro SFT summary")
    parser.add_argument("--summary", required=True)
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
        print("RESULT: All checks passed!" if result["valid"] else f"RESULT: {len(result['errors'])} error(s)")

    sys.exit(0 if result["valid"] else 1)


if __name__ == "__main__":
    main()
