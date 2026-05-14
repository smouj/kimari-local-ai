#!/usr/bin/env python3
"""Validate sanitized Kimari manual review summaries.

This validator intentionally rejects raw prompt/response bodies, tokens, public
benchmark claims, and gate advancement for private eval review artifacts.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ALLOWED_DECISIONS = {
    "continue_to_subset60",
    "continue_to_full104",
    "dataset_fix_required",
    "safety_fix_required",
    "training_config_fix_required",
    "inconclusive",
    "blocked_missing_raw_outputs",
}
ALLOWED_REVIEW_STATUSES = {
    "completed",
    "pending_manual_classification",
    "ready",
    "ready_for_private_manual_review",
    "blocked_pending_private_raw_outputs",
    "blocked_missing_raw_outputs",
}
FORBIDDEN_KEYS = {
    "prompt",
    "prompts",
    "response",
    "responses",
    "raw_output",
    "raw_outputs",
    "raw_responses",
    "generated_text",
    "model_output",
    "model_outputs",
    "completion",
    "completions",
    "input_ids",
    "token_ids",
    "access_token",
    "hf_token",
    "api_key",
}
FORBIDDEN_TEXT = [
    "public benchmark",
    "benchmark claim",
    "outperforms",
    "sota",
    "gguf released",
    "public weights",
    "hf_",
    "huggingface_token",
]


def walk(obj, path="$"):
    if isinstance(obj, dict):
        for key, value in obj.items():
            yield path, key, value
            yield from walk(value, f"{path}.{key}")
    elif isinstance(obj, list):
        for idx, value in enumerate(obj):
            yield from walk(value, f"{path}[{idx}]")


def validate(data: dict) -> list[str]:
    errors: list[str] = []
    if data.get("raw_outputs_committed") is not False:
        errors.append("raw_outputs_committed must be false")
    if data.get("public_benchmark_allowed") is not False:
        errors.append("public_benchmark_allowed must be false")
    if data.get("gate_state") != "BLOCKED":
        errors.append("gate_state must be BLOCKED")
    if data.get("decision") not in ALLOWED_DECISIONS:
        errors.append(f"decision must be one of {sorted(ALLOWED_DECISIONS)}")
    review_status = data.get("manual_review_status", data.get("review_status"))
    if review_status not in ALLOWED_REVIEW_STATUSES:
        errors.append(f"manual_review_status/review_status must be one of {sorted(ALLOWED_REVIEW_STATUSES)}")
    subset_size = data.get("subset_size")
    reviewed_items = data.get("reviewed_items")
    if not isinstance(subset_size, int) or subset_size < 0:
        errors.append("subset_size must be a non-negative integer")
    if not isinstance(reviewed_items, int) or reviewed_items < 0:
        errors.append("reviewed_items must be a non-negative integer")
    if isinstance(subset_size, int) and isinstance(reviewed_items, int) and reviewed_items > subset_size:
        errors.append("reviewed_items must be <= subset_size")
    if review_status == "completed" and reviewed_items != subset_size:
        errors.append("completed manual review must have reviewed_items == subset_size")

    for _, key, value in walk(data):
        key_l = str(key).lower()
        if key_l in FORBIDDEN_KEYS:
            errors.append(f"forbidden raw/sensitive key present: {key}")
        if re.search(r"(^|_)(prompt|response|generated|completion|token)(_body|_text|s)?$", key_l):
            errors.append(f"forbidden raw body key pattern present: {key}")
        if isinstance(value, str):
            value_l = value.lower()
            for forbidden in FORBIDDEN_TEXT:
                if forbidden in value_l:
                    # Allow explicit negated/safety statements.
                    safe_prefixes = ("no ", "not a ", "without ", "forbid", "forbidden", "false")
                    idx = value_l.find(forbidden)
                    context = value_l[max(0, idx - 12) : idx]
                    if not any(prefix in context for prefix in safe_prefixes):
                        errors.append(f"forbidden claim/token-like text present near: {forbidden}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--summary", required=True, type=Path)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    data = json.loads(args.summary.read_text())
    errors = validate(data)
    payload = {"valid": not errors, "errors": errors, "summary": str(args.summary)}
    if args.json:
        print(json.dumps(payload, indent=2))
    else:
        print("manual review summary: OK" if not errors else "manual review summary: FAIL")
        for error in errors:
            print(f"  FAIL: {error}")
    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main())
