#!/usr/bin/env python3
"""Validate a sanitized Kimari Runtime 1.5B SFT v1 run summary."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

REQUIRED_FIELDS = (
    "run_id",
    "base_model",
    "base_license",
    "dataset_train_sha256",
    "training_performed",
    "adapter_committed_public",
    "hf_public_upload_performed",
    "gguf_generated",
    "gate_state",
    "manual_review_required",
)

SECRET_OR_PII_PATTERNS = (
    re.compile(r"sk-proj-[A-Za-z0-9_-]+"),
    re.compile(r"sk-sb-[A-Za-z0-9_-]+"),
    re.compile(r"ghp_[A-Za-z0-9_]+"),
    re.compile(r"github_pat_[A-Za-z0-9_]+"),
    re.compile(r"AKIA[0-9A-Z]{16}"),
    re.compile(r"[A-Za-z0-9._%+-]+@gmail\.com", re.IGNORECASE),
    re.compile(r"[A-Za-z0-9._%+-]+@hotmail\.com", re.IGNORECASE),
    re.compile(r"[A-Za-z0-9._%+-]+@outlook\.com", re.IGNORECASE),
)

PUBLIC_BENCHMARK_PATTERNS = (
    re.compile(r"public\s+benchmark", re.IGNORECASE),
    re.compile(r"leaderboard", re.IGNORECASE),
    re.compile(r"state[- ]of[- ]the[- ]art", re.IGNORECASE),
    re.compile(r"\bsota\b", re.IGNORECASE),
)


def flatten_values(value: Any) -> list[str]:
    if isinstance(value, dict):
        items: list[str] = []
        for key, nested_value in value.items():
            items.append(str(key))
            items.extend(flatten_values(nested_value))
        return items
    if isinstance(value, list):
        items = []
        for item in value:
            items.extend(flatten_values(item))
        return items
    return [str(value)]


def validate_summary(summary: dict[str, Any], strict: bool) -> tuple[bool, list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []

    for field in REQUIRED_FIELDS:
        if field not in summary:
            errors.append(f"missing required field: {field}")

    if not isinstance(summary.get("training_performed"), bool):
        errors.append("training_performed must be bool")
    if summary.get("adapter_committed_public") is not False:
        errors.append("adapter_committed_public must be false")
    if summary.get("hf_public_upload_performed") is not False:
        errors.append("hf_public_upload_performed must be false")
    if summary.get("gguf_generated") is not False:
        errors.append("gguf_generated must be false")
    if "raw_logs_committed" in summary and summary.get("raw_logs_committed") is not False:
        errors.append("raw_logs_committed must be false when present")
    if summary.get("gate_state") != "BLOCKED":
        errors.append("gate_state must be BLOCKED")
    if summary.get("manual_review_required") is not True:
        errors.append("manual_review_required must be true")
    if summary.get("public_benchmark_allowed") is True:
        errors.append("public_benchmark_allowed must not be true")

    all_text = "\n".join(flatten_values(summary))
    for pattern in SECRET_OR_PII_PATTERNS:
        if pattern.search(all_text):
            errors.append(f"secret/PII pattern found: {pattern.pattern}")
    for pattern in PUBLIC_BENCHMARK_PATTERNS:
        if pattern.search(all_text):
            errors.append(f"public benchmark claim found: {pattern.pattern}")

    if strict:
        sha256_fields = ("dataset_train_sha256", "dataset_validation_sha256")
        for field in sha256_fields:
            value = summary.get(field)
            if not isinstance(value, str) or not re.fullmatch(r"[0-9a-f]{64}", value):
                errors.append(f"{field} must be a lowercase SHA-256 hex digest")
        if not isinstance(summary.get("manual_review_required"), bool):
            errors.append("manual_review_required must be bool")
    elif not isinstance(summary.get("manual_review_required"), bool):
        warnings.append("manual_review_required should be bool")

    return not errors, errors, warnings


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--summary", required=True, help="Summary JSON path")
    parser.add_argument("--json", action="store_true", help="Print validation result as JSON")
    parser.add_argument("--strict", action="store_true", help="Enable stricter structural checks")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    result: dict[str, Any] = {"status": "fail", "errors": [], "warnings": []}
    try:
        summary = json.loads(Path(args.summary).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        result["errors"] = [f"failed to read summary: {exc}"]
    else:
        if not isinstance(summary, dict):
            result["errors"] = ["summary must be a JSON object"]
        else:
            ok, errors, warnings = validate_summary(summary, args.strict)
            result = {"status": "pass" if ok else "fail", "errors": errors, "warnings": warnings}

    if args.json:
        print(json.dumps(result, indent=2, sort_keys=False))
    elif result["status"] == "pass":
        print("PASS: SFT v1 run summary is safe and valid")
    else:
        print("FAIL: SFT v1 run summary is invalid")
        for error in result["errors"]:
            print(f"- {error}")
    return 0 if result["status"] == "pass" else 1


if __name__ == "__main__":
    sys.exit(main())
