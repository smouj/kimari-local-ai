#!/usr/bin/env python3
"""Validate a micro SFT execution record for safety and correctness.

Checks that the execution record:
- gate_state == "BLOCKED"
- adapter_committed == false
- hf_upload_performed == false
- gguf_generated == false
- raw_logs_committed == false
- manual_review_required == true
- No token-like strings
- No raw logs
- No public release claim

Usage:
    python training/scripts/validate_micro_sft_execution_record.py --record /tmp/micro_sft_execution_record.json --json
    python training/scripts/validate_micro_sft_execution_record.py --record /tmp/micro_sft_execution_record.json
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

# Token-like patterns that must NOT appear in a safe execution record
TOKEN_PATTERNS = [
    re.compile(r"hf_[a-zA-Z0-9]{20,}"),
    re.compile(r"sk-[a-zA-Z0-9]{20,}"),
    re.compile(r"api_key[\s]*[=:][\s]*[\"']?[a-zA-Z0-9_\-]{20,}[\"']?", re.IGNORECASE),
    re.compile(r"ghp_[a-zA-Z0-9]{20,}"),
    re.compile(r"github_pat_[a-zA-Z0-9_]{20,}"),
]


def validate_record(data: dict) -> tuple[bool, list[dict], list[str]]:
    """Validate a micro SFT execution record.

    Returns (valid, checks, errors) where checks is a list of
    {name, passed, message} dicts and errors is a list of error strings.
    """
    checks: list[dict] = []
    errors: list[str] = []

    # Check 1: gate_state == "BLOCKED"
    gate_blocked = data.get("gate_state") == "BLOCKED"
    checks.append({
        "name": "gate_blocked",
        "passed": gate_blocked,
        "message": "gate_state is BLOCKED" if gate_blocked else "gate_state must be BLOCKED",
    })
    if not gate_blocked:
        errors.append("gate_state must be BLOCKED")

    # Check 2: adapter_committed == false
    adapter_committed = data.get("adapter_committed") is False
    checks.append({
        "name": "adapter_not_committed",
        "passed": adapter_committed,
        "message": "adapter_committed is false" if adapter_committed else "adapter_committed must be false",
    })
    if not adapter_committed:
        errors.append("adapter_committed must be false")

    # Check 3: hf_upload_performed == false
    hf_upload = data.get("hf_upload_performed") is False
    checks.append({
        "name": "no_hf_upload",
        "passed": hf_upload,
        "message": "hf_upload_performed is false" if hf_upload else "hf_upload_performed must be false",
    })
    if not hf_upload:
        errors.append("hf_upload_performed must be false")

    # Check 4: gguf_generated == false
    gguf = data.get("gguf_generated") is False
    checks.append({
        "name": "no_gguf_generated",
        "passed": gguf,
        "message": "gguf_generated is false" if gguf else "gguf_generated must be false",
    })
    if not gguf:
        errors.append("gguf_generated must be false")

    # Check 5: raw_logs_committed == false
    raw_logs = data.get("raw_logs_committed") is False
    checks.append({
        "name": "no_raw_logs_committed",
        "passed": raw_logs,
        "message": "raw_logs_committed is false" if raw_logs else "raw_logs_committed must be false",
    })
    if not raw_logs:
        errors.append("raw_logs_committed must be false")

    # Check 6: manual_review_required == true
    manual_review = data.get("manual_review_required") is True
    checks.append({
        "name": "manual_review_required",
        "passed": manual_review,
        "message": "manual_review_required is true" if manual_review else "manual_review_required must be true",
    })
    if not manual_review:
        errors.append("manual_review_required must be true")

    # Check 7: No token-like strings
    record_text = json.dumps(data)
    token_found = False
    for pattern in TOKEN_PATTERNS:
        match = pattern.search(record_text)
        if match:
            token_found = True
            errors.append(f"Token-like string detected: {match.group(0)[:20]}...")

    checks.append({
        "name": "no_token_patterns",
        "passed": not token_found,
        "message": "No token-like strings detected" if not token_found else "Token-like strings detected",
    })

    # Check 8: No raw logs field or raw_logs field is empty/absent
    has_raw_logs = False
    raw_logs_value = data.get("raw_logs")
    if raw_logs_value is not None and raw_logs_value != "":
        has_raw_logs = True
        errors.append("raw_logs field must be absent or empty")

    checks.append({
        "name": "no_raw_logs",
        "passed": not has_raw_logs,
        "message": "No raw logs present" if not has_raw_logs else "raw_logs field must be absent or empty",
    })

    # Check 9: No "public_release" or "released" claim in any string value
    public_release_found = False
    for key, value in data.items():
        if isinstance(value, str):
            lower_val = value.lower()
            if "public_release" in lower_val or "released" in lower_val:
                public_release_found = True
                errors.append(f"Public release claim found in field '{key}': {value}")

    checks.append({
        "name": "no_public_release_claim",
        "passed": not public_release_found,
        "message": "No public release claim" if not public_release_found else "Public release claim detected",
    })

    # Check 10: record_type == "micro_sft_execution_record"
    record_type_ok = data.get("record_type") == "micro_sft_execution_record"
    checks.append({
        "name": "correct_record_type",
        "passed": record_type_ok,
        "message": "record_type is micro_sft_execution_record" if record_type_ok else "record_type must be micro_sft_execution_record",
    })
    if not record_type_ok:
        errors.append("record_type must be micro_sft_execution_record")

    valid = len(errors) == 0
    return valid, checks, errors


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Validate a micro SFT execution record for safety and correctness. "
        "Ensures gate BLOCKED, no uploads, no tokens, no raw logs, no public release claim."
    )
    parser.add_argument(
        "--record",
        type=Path,
        required=True,
        help="Path to execution record JSON file to validate",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        dest="json_output",
        help="Output validation result as JSON",
    )

    args = parser.parse_args()

    # Read record
    if not args.record.exists():
        print(f"ERROR: Record file not found: {args.record}", file=sys.stderr)
        sys.exit(1)

    try:
        data = json.loads(args.record.read_text())
    except json.JSONDecodeError as e:
        print(f"ERROR: Invalid JSON in record: {e}", file=sys.stderr)
        sys.exit(1)

    # Validate
    valid, checks, errors = validate_record(data)

    result = {
        "valid": valid,
        "checks": checks,
        "errors": errors,
    }

    if args.json_output:
        print(json.dumps(result, indent=2))
    else:
        if valid:
            print("✅ Micro SFT execution record is VALID")
            print(f"  All safety checks passed for: {args.record}")
        else:
            print("❌ Micro SFT execution record is INVALID")
            for error in errors:
                print(f"  - {error}")

    sys.exit(0 if valid else 1)


if __name__ == "__main__":
    main()
