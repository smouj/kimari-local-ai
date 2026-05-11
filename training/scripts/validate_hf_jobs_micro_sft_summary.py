#!/usr/bin/env python3
"""Validate HF Jobs micro SFT summary for safety and correctness.

Checks that the micro SFT summary has:
- hf_upload_performed=false
- adapter_committed=false
- gguf_generated=false
- raw_logs_committed=false
- gate_state=BLOCKED
- manual_review_required=true
- No token-like strings
- No raw logs

Usage:
    python training/scripts/validate_hf_jobs_micro_sft_summary.py --summary /tmp/micro_sft_summary.json --json
    python training/scripts/validate_hf_jobs_micro_sft_summary.py --summary /tmp/micro_sft_summary.json
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

# Token-like patterns that must NOT appear in a safe summary
TOKEN_PATTERNS = [
    re.compile(r"hf_[a-zA-Z0-9]{20,}"),
    re.compile(r"sk-[a-zA-Z0-9]{20,}"),
    re.compile(r"api_key[\s]*[=:][\s]*[\"']?[a-zA-Z0-9_\-]{20,}[\"']?", re.IGNORECASE),
    re.compile(r"token[\s]*[=:][\s]*[\"']?[a-zA-Z0-9_\-]{20,}[\"']?", re.IGNORECASE),
    re.compile(r"password[\s]*[=:][\s]*[\"']?[a-zA-Z0-9_\-]{8,}[\"']?", re.IGNORECASE),
]


def validate_summary(data: dict) -> list[str]:
    """Validate a micro SFT summary and return a list of errors."""
    errors: list[str] = []

    # Required safety fields
    if data.get("hf_upload_performed") is not False:
        errors.append("hf_upload_performed must be false")

    if data.get("adapter_committed") is not False:
        errors.append("adapter_committed must be false")

    if data.get("gguf_generated") is not False:
        errors.append("gguf_generated must be false")

    if data.get("raw_logs_committed") is not False:
        errors.append("raw_logs_committed must be false")

    if data.get("gate_state") != "BLOCKED":
        errors.append("gate_state must be BLOCKED")

    if data.get("manual_review_required") is not True:
        errors.append("manual_review_required must be true")

    # Check no raw logs
    if data.get("raw_logs") is not None:
        errors.append("raw_logs must not be present in summary")

    if data.get("raw_logs_included") is True:
        errors.append("raw_logs_included must be false or absent")

    # Check no token-like strings in the entire JSON
    summary_text = json.dumps(data)
    for pattern in TOKEN_PATTERNS:
        match = pattern.search(summary_text)
        if match:
            # Allow the string "NOT_AVAILABLE" and safe placeholders
            matched_text = match.group(0)
            if matched_text not in ("NOT_AVAILABLE",):
                errors.append(f"Token-like string detected: {matched_text[:20]}...")

    return errors


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Validate HF Jobs micro SFT summary for safety and correctness. "
        "Ensures hf_upload_performed=false, adapter_committed=false, gate BLOCKED, "
        "manual_review_required=true, no tokens, no raw logs."
    )
    parser.add_argument(
        "--summary",
        type=Path,
        required=True,
        help="Path to micro SFT summary JSON file to validate",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        dest="json_output",
        help="Output validation result as JSON",
    )

    args = parser.parse_args()

    # Read summary
    if not args.summary.exists():
        print(f"ERROR: Summary file not found: {args.summary}", file=sys.stderr)
        sys.exit(1)

    try:
        data = json.loads(args.summary.read_text())
    except json.JSONDecodeError as e:
        print(f"ERROR: Invalid JSON in summary: {e}", file=sys.stderr)
        sys.exit(1)

    # Validate
    errors = validate_summary(data)
    valid = len(errors) == 0

    result = {
        "valid": valid,
        "errors": errors,
        "summary_path": str(args.summary),
        "checked_fields": [
            "hf_upload_performed",
            "adapter_committed",
            "gguf_generated",
            "raw_logs_committed",
            "gate_state",
            "manual_review_required",
            "no_raw_logs",
            "no_token_patterns",
        ],
    }

    if args.json_output:
        print(json.dumps(result, indent=2))
    else:
        if valid:
            print("✅ Micro SFT summary is VALID")
            print(f"  All safety checks passed for: {args.summary}")
        else:
            print("❌ Micro SFT summary is INVALID")
            for error in errors:
                print(f"  - {error}")

    sys.exit(0 if valid else 1)


if __name__ == "__main__":
    main()
