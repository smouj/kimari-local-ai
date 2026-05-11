#!/usr/bin/env python3
"""Create a committable eval summary from a raw eval result file.

Reads a raw eval result JSON, strips sensitive fields (prompt, response),
and produces a safe summary suitable for committing to the repository.

What is stripped:
- "prompt" fields from individual results
- "response" fields from individual results

What is preserved:
- Category counts
- Score status
- Manual review flags
- Run metadata

Does NOT invent scores. If no scores exist in the raw data, marks
manual_review_required as true.

No model required. No network calls.

Usage:
    python eval/scripts/create_eval_summary.py \\
        --input eval/results/sft-raw.json \\
        --output eval/results/sft-summary.json
    python eval/scripts/create_eval_summary.py \\
        --input eval/results/sft-raw.json \\
        --output eval/results/sft-summary.json \\
        --json
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# Fields to strip from individual results — these are too sensitive to commit
STRIPPED_FIELDS = {"prompt", "response"}

# Default template path
DEFAULT_TEMPLATE = Path(__file__).resolve().parent.parent / "templates" / "eval_summary.template.json"


def load_raw_result(path: Path) -> dict | None:
    """Load a raw eval result JSON file.

    Returns the parsed dict, or None on failure.
    """
    if not path.exists():
        print(f"ERROR: File not found: {path}", file=sys.stderr)
        return None

    try:
        with open(path) as f:
            data = json.load(f)
    except json.JSONDecodeError as exc:
        print(f"ERROR: Invalid JSON in {path}: {exc}", file=sys.stderr)
        return None

    if not isinstance(data, dict):
        print(f"ERROR: {path} does not contain a JSON object", file=sys.stderr)
        return None

    return data


def load_template(path: Path) -> dict | None:
    """Load the eval summary template JSON.

    Returns the template dict, or None if not found.
    """
    if not path.exists():
        print(f"WARNING: Template not found: {path}, using built-in defaults", file=sys.stderr)
        return None

    try:
        with open(path) as f:
            return json.load(f)
    except json.JSONDecodeError as exc:
        print(f"WARNING: Invalid template JSON: {exc}, using built-in defaults", file=sys.stderr)
        return None


def create_summary(raw_data: dict, template_path: Path | None = None) -> dict:
    """Create a safe eval summary from raw eval result data.

    Strips prompt and response fields from individual results.
    Does NOT invent scores. Marks manual_review_required if no scores exist.
    """
    # Start from template or built-in defaults
    if template_path is not None:
        template = load_template(template_path)
        summary = dict(template) if template is not None else _default_summary()
    else:
        summary = _default_summary()

    # Extract run metadata
    results = raw_data.get("results", [])
    total = raw_data.get("total", len(results))

    summary["run_id"] = raw_data.get("run_id", "")
    summary["model_label"] = raw_data.get("model_label", "")
    summary["kimari_version"] = raw_data.get("kimari_version", "")
    summary["prompt_count"] = total

    # Compute category counts from results (stripped of sensitive fields)
    category_counts: dict[str, int] = {}
    has_scores = False
    safety_regression = False
    false_claims = False

    for result in results:
        category = result.get("category", "unknown")
        category_counts[category] = category_counts.get(category, 0) + 1

        # Check if any result has an actual score (not manual_review_required)
        score_status = result.get("score_status", "")
        if score_status and score_status != "manual_review_required":
            has_scores = True

        # Check for safety regression flags
        if result.get("safety_regression_detected", False):
            safety_regression = True

        # Check for false claims flags
        if result.get("false_claims_detected", False):
            false_claims = True

    summary["category_counts"] = category_counts
    summary["safety_regression_detected"] = safety_regression
    summary["false_claims_detected"] = false_claims

    # Score status — do NOT invent scores
    if not has_scores:
        summary["score_status"] = "manual_review_required"
        summary["manual_review_required"] = True
    else:
        summary["score_status"] = raw_data.get("score_status", "manual_review_required")
        summary["manual_review_required"] = raw_data.get("manual_review_required", True)

    # Preserve reviewer and notes if present
    if "reviewer" in raw_data:
        summary["reviewer"] = raw_data["reviewer"]
    if "notes" in raw_data:
        summary["notes"] = raw_data["notes"]

    return summary


def _default_summary() -> dict:
    """Return built-in default summary structure."""
    return {
        "run_id": "",
        "model_label": "",
        "kimari_version": "",
        "prompt_count": 0,
        "category_counts": {},
        "score_status": "manual_review_required",
        "manual_review_required": True,
        "safety_regression_detected": False,
        "false_claims_detected": False,
        "reviewer": "",
        "notes": "",
    }


def main() -> None:
    """CLI entry point for creating eval summaries."""
    parser = argparse.ArgumentParser(
        description="Create a committable eval summary from raw eval results. "
        "Strips prompt and response fields. Does NOT invent scores.",
    )
    parser.add_argument(
        "--input",
        type=Path,
        required=True,
        help="Path to raw eval result JSON file",
    )
    parser.add_argument(
        "--output",
        type=Path,
        required=True,
        help="Path to output summary JSON file",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        dest="json_output",
        help="Also print summary to stdout as JSON",
    )

    args = parser.parse_args()

    # Load raw data
    raw_data = load_raw_result(args.input)
    if raw_data is None:
        sys.exit(1)

    # Create summary
    summary = create_summary(raw_data, template_path=DEFAULT_TEMPLATE)

    # Write to output file
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with open(args.output, "w") as f:
        json.dump(summary, f, indent=2)
        f.write("\n")

    print(f"Summary written to: {args.output}", file=sys.stderr)

    # Also print to stdout if requested
    if args.json_output:
        print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
