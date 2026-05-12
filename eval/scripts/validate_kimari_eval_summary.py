#!/usr/bin/env python3
"""Validate KimariEval summary JSON files.

Usage:
    python eval/scripts/validate_kimari_eval_summary.py \
        --summary reports/evals/kimari_v0153_baseline_vs_adapter/summary.pending.json \
        --json
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REQUIRED_FIELDS = [
    "run_id", "model_label", "base_model", "dataset_id",
    "item_count", "completion_rate", "score_status",
    "manual_review_required", "raw_outputs_committed",
    "public_benchmark_allowed", "gate_state",
]

FORBIDDEN_FIELDS = ["raw_outputs", "raw_responses", "generated_text", "model_responses"]


def validate_summary(summary: dict, filename: str = "") -> list[str]:
    """Validate a single eval summary."""
    errors = []

    # Required fields
    for field in REQUIRED_FIELDS:
        if field not in summary:
            errors.append(f"{filename}: missing required field '{field}'")

    # Safety flags must be correct
    if summary.get("manual_review_required") is not True:
        errors.append(f"{filename}: manual_review_required must be true")

    if summary.get("public_benchmark_allowed") is True:
        errors.append(f"{filename}: public_benchmark_allowed must be false")

    if summary.get("raw_outputs_committed") is True:
        errors.append(f"{filename}: raw_outputs_committed must be false")

    if summary.get("gate_state") != "BLOCKED":
        errors.append(f"{filename}: gate_state must be BLOCKED")

    # Item count must be positive (or 0 for pending)
    if summary.get("item_count", 0) < 0:
        errors.append(f"{filename}: item_count must be >= 0")
    # Warn if 0 (pending)
    if summary.get("item_count", 0) == 0 and summary.get("score_status") != "not_scored":
        errors.append(f"{filename}: item_count is 0 but score_status is not 'not_scored'")

    # No forbidden fields (raw outputs)
    for field in FORBIDDEN_FIELDS:
        if field in summary:
            errors.append(f"{filename}: forbidden field '{field}' (no raw outputs)")

    # No tokens or secrets
    content = json.dumps(summary).lower()
    for pattern in ["sk-", "api_key", "hf_token", "password"]:
        if pattern in content:
            errors.append(f"{filename}: potential sensitive pattern: {pattern}")

    # No benchmark claims
    if ("achieved" in content or "outperforms" in content or "beats" in content) and "no benchmark" not in content and "not scored" not in content:
        errors.append(f"{filename}: potential benchmark claim detected")

    return errors


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate KimariEval summary")
    parser.add_argument("--summary", required=True, help="Summary JSON file path")
    parser.add_argument("--json", action="store_true", help="JSON output")
    args = parser.parse_args()

    path = Path(args.summary)
    if not path.exists():
        result = {"valid": False, "errors": [f"File not found: {args.summary}"]}
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print(f"  FAIL: File not found: {args.summary}")
        sys.exit(1)

    summary = json.loads(path.read_text())
    errors = validate_summary(summary, path.name)

    result = {
        "valid": len(errors) == 0,
        "errors": errors,
        "summary_fields": list(summary.keys()),
        "item_count": summary.get("item_count"),
        "gate_state": summary.get("gate_state"),
        "score_status": summary.get("score_status"),
    }

    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        for e in result["errors"]:
            print(f"  FAIL: {e}")
        print(f"\nFields: {len(result['summary_fields'])}")
        print(f"Items: {result['item_count']}")
        print(f"Gate: {result['gate_state']}")
        print(f"Score: {result['score_status']}")
        err_count = len(result['errors'])
        print("RESULT: Valid!" if result['valid'] else f"RESULT: {err_count} error(s)")

    sys.exit(0 if result["valid"] else 1)


if __name__ == "__main__":
    main()
