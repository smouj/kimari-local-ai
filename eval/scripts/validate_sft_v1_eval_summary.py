#!/usr/bin/env python3
"""Validate SFT v1 eval summary.

Ensures:
- subset_size=10
- raw_outputs_committed=false
- public_benchmark_allowed=false
- manual_review_required=true
- gate_state=BLOCKED
- no benchmark claim
- no public weights
- no tokens/secrets
"""

import argparse
import json
import re
import sys
from pathlib import Path


def validate_sft_v1_eval_summary(summary_path: str, json_output: bool = False) -> bool:
    """Validate SFT v1 eval summary JSON."""
    errors = []
    warnings = []

    summary_file = Path(summary_path)
    if not summary_file.exists():
        errors.append(f"Summary file not found: {summary_path}")
        result = {"status": "fail", "errors": errors, "warnings": warnings}
        if json_output:
            print(json.dumps(result, indent=2))
        else:
            print(f"FAIL: {errors[0]}")
        return False

    try:
        data = json.loads(summary_file.read_text())
    except json.JSONDecodeError as e:
        errors.append(f"Invalid JSON: {e}")
        result = {"status": "fail", "errors": errors, "warnings": warnings}
        if json_output:
            print(json.dumps(result, indent=2))
        else:
            print(f"FAIL: Invalid JSON: {e}")
        return False

    # Required fields
    required_fields = [
        "run_id",
        "base_model",
        "dataset_id",
        "subset_size",
        "comparison_mode",
        "score_status",
        "manual_review_required",
        "raw_outputs_committed",
        "public_benchmark_allowed",
        "gate_state",
    ]
    for field in required_fields:
        if field not in data:
            errors.append(f"Missing required field: {field}")

    # Subset size must be 10
    if data.get("subset_size") != 10:
        errors.append(f"subset_size must be 10, got {data.get('subset_size')}")

    # Safety flags
    if data.get("raw_outputs_committed") is not False:
        errors.append("raw_outputs_committed must be false")

    if data.get("public_benchmark_allowed") is not False:
        errors.append("public_benchmark_allowed must be false")

    if data.get("manual_review_required") is not True:
        errors.append("manual_review_required must be true")

    if data.get("gate_state") != "BLOCKED":
        errors.append("gate_state must be BLOCKED")

    # Score status must be not_scored or manual_review
    valid_scores = {"not_scored", "manual_review"}
    if data.get("score_status") not in valid_scores:
        errors.append(f"score_status must be one of {valid_scores}, got {data.get('score_status')}")

    # No public benchmark claims in notes
    notes = data.get("notes", "").lower()
    if "benchmark" in notes and "no public benchmark" not in notes and "no benchmark" not in notes:
        errors.append("notes must not make public benchmark claims")

    # No tokens/secrets
    text = summary_file.read_text()
    secret_patterns = [
        r"sk-proj-",
        r"ghp_",
        r"hf_[a-zA-Z]{30,}",
        r"AKIA[0-9A-Z]{16}",
    ]
    for pattern in secret_patterns:
        if re.search(pattern, text):
            errors.append(f"Summary contains secret pattern: {pattern}")

    # No public weights
    if data.get("adapter_committed_public") is True:
        errors.append("adapter_committed_public must be false")

    result = {
        "status": "pass" if not errors else "fail",
        "errors": errors,
        "warnings": warnings,
    }

    if json_output:
        print(json.dumps(result, indent=2))
    else:
        if errors:
            print("FAIL: SFT v1 eval summary validation failed")
            for e in errors:
                print(f"  - {e}")
        if warnings:
            print("WARNINGS:")
            for w in warnings:
                print(f"  - {w}")
        if not errors and not warnings:
            print("PASS: SFT v1 eval summary validation passed")

    return len(errors) == 0


def main():
    parser = argparse.ArgumentParser(description="Validate SFT v1 eval summary")
    parser.add_argument("--summary", required=True, help="Path to summary JSON")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args()

    success = validate_sft_v1_eval_summary(
        summary_path=args.summary,
        json_output=args.json,
    )
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
