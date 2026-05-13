#!/usr/bin/env python3
"""Validate Kimari evaluation dataset items.

Usage:
    python eval/scripts/validate_kimari_eval.py --dataset-dir eval/kimari_private_v1 --json
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REQUIRED_FIELDS = ["id", "prompt", "ideal", "tags", "difficulty"]
VALID_DIFFICULTIES = ["easy", "medium", "hard"]
FORBIDDEN_PATTERNS = ["sk-", "api_key", "password", "credential", "/home/"]


def validate_item(item: dict, line_num: int, filename: str) -> list[str]:
    """Validate a single eval item."""
    errors = []

    # Required fields
    for field in REQUIRED_FIELDS:
        if field not in item:
            errors.append(f"{filename}:{line_num}: missing required field '{field}'")

    if errors:
        return errors

    # ID format
    if not isinstance(item["id"], str) or len(item["id"]) < 5:
        errors.append(f"{filename}:{line_num}: id must be a string >= 5 chars")

    # Prompt not empty
    if not isinstance(item["prompt"], str) or len(item["prompt"]) < 10:
        errors.append(f"{filename}:{line_num}: prompt must be a string >= 10 chars")

    # Ideal not empty
    if not isinstance(item["ideal"], str) or len(item["ideal"]) < 20:
        errors.append(f"{filename}:{line_num}: ideal must be a string >= 20 chars")

    # Tags
    if not isinstance(item["tags"], list) or len(item["tags"]) < 1:
        errors.append(f"{filename}:{line_num}: tags must be a non-empty list")

    # Difficulty
    if item.get("difficulty") not in VALID_DIFFICULTIES:
        errors.append(f"{filename}:{line_num}: difficulty must be one of {VALID_DIFFICULTIES}")

    # No tokens/secrets (allow 'no ' prefix context, and allow in safety/refusal categories)
    content_lower = json.dumps(item).lower()
    for pattern in FORBIDDEN_PATTERNS:
        if pattern in content_lower:
            # Allow patterns in refusal/safety context (teaching what NOT to do)
            tags_lower = [t.lower() for t in item.get("tags", [])]
            if any(t in tags_lower for t in ["refusal", "safety", "security", "ssh", "observability", "logging"]):
                continue
            if "no " + pattern in content_lower or "never " + pattern in content_lower:
                continue
            errors.append(f"{filename}:{line_num}: potential sensitive pattern: {pattern}")

    # No Kimari-4B release claims (allow questions that refute claims)
    if "kimari-4b" in content_lower:
        # Allow if the prompt refutes the claim
        if any(
            phrase in content_lower
            for phrase in ["not been publicly released", "not been released", "has not been", "no benchmark"]
        ):
            pass  # OK - refuting the claim
        elif (
            any(phrase in content_lower for phrase in ["achieved", "scored", "better than"])
            and "no " not in content_lower
            and "not " not in content_lower
        ):
            errors.append(f"{filename}:{line_num}: Kimari-4B claim without refutation")

    return errors


def validate_dataset(dataset_dir: str) -> dict:
    """Validate all eval items in a dataset directory."""
    dataset_path = Path(dataset_dir)
    if not dataset_path.exists():
        return {"valid": False, "errors": [f"Dataset directory not found: {dataset_dir}"], "warnings": [], "stats": {}}

    all_errors = []
    all_warnings = []
    total_items = 0
    categories = {}
    ids = set()

    for jsonl_file in sorted(dataset_path.glob("*.jsonl")):
        category = jsonl_file.stem
        items = []
        for line_num, line in enumerate(jsonl_file.read_text().strip().split("\n"), 1):
            if not line.strip():
                continue
            try:
                item = json.loads(line)
                items.append(item)
                total_items += 1

                # Check for duplicate IDs
                if item.get("id") in ids:
                    all_errors.append(f"{jsonl_file.name}:{line_num}: duplicate id '{item.get('id')}'")
                ids.add(item.get("id"))

                # Validate item
                item_errors = validate_item(item, line_num, jsonl_file.name)
                all_errors.extend(item_errors)
            except json.JSONDecodeError as e:
                all_errors.append(f"{jsonl_file.name}:{line_num}: invalid JSON: {e}")

        categories[category] = len(items)

    stats = {
        "total_items": total_items,
        "categories": categories,
        "unique_ids": len(ids),
    }

    # Minimum items per category
    for cat, count in categories.items():
        if count < 10:
            all_warnings.append(f"Category '{cat}' has only {count} items (minimum: 10)")

    # Minimum total
    if total_items < 100:
        all_warnings.append(f"Total items is {total_items} (minimum recommended: 100)")

    return {
        "valid": len(all_errors) == 0,
        "errors": all_errors,
        "warnings": all_warnings,
        "stats": stats,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate Kimari eval dataset")
    parser.add_argument("--dataset-dir", default="eval/kimari_private_v1", help="Dataset directory")
    parser.add_argument("--json", action="store_true", help="JSON output")
    args = parser.parse_args()

    result = validate_dataset(args.dataset_dir)

    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        for e in result["errors"]:
            print(f"  FAIL: {e}")
        for w in result["warnings"]:
            print(f"  WARN: {w}")
        print(f"\nStats: {result['stats']}")
        err_count = len(result["errors"])
        print("RESULT: Valid!" if result["valid"] else f"RESULT: {err_count} error(s)")

    sys.exit(0 if result["valid"] else 1)


if __name__ == "__main__":
    main()
