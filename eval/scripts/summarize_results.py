#!/usr/bin/env python3
"""Summarize KimariFit evaluation results.

Reads a KimariFit result JSON file and produces a summary
with category counts, missing outputs, and manual review status.
Does NOT invent scores.

No model required. No network calls.

Usage:
    python eval/scripts/summarize_results.py --input eval/results/some-result.json
    python eval/scripts/summarize_results.py --input eval/results/some-result.json --json
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def summarize_result_file(path: Path) -> dict:
    """Read and summarize a KimariFit result JSON file.

    Returns a summary dict with category breakdowns, missing counts,
    and manual review counts. Does NOT invent scores.
    """
    if not path.exists():
        return {"error": f"File not found: {path}", "status": "not_found"}

    try:
        with open(path) as f:
            data = json.load(f)
    except json.JSONDecodeError as exc:
        return {"error": f"Invalid JSON: {exc}", "status": "parse_error"}

    results = data.get("results", [])
    total = data.get("total", len(results))
    ok_count = data.get("ok", 0)
    error_count = data.get("errors", 0)

    # Category breakdown
    category_stats: dict[str, dict] = {}
    missing_outputs = 0
    manual_review_required = 0

    for result in results:
        category = result.get("category", "unknown")
        status = result.get("status", "unknown")
        response = result.get("response", "")
        score_status = result.get("score_status", "")

        if category not in category_stats:
            category_stats[category] = {"total": 0, "ok": 0, "error": 0, "missing_response": 0}

        category_stats[category]["total"] += 1

        if status == "ok":
            category_stats[category]["ok"] += 1
        else:
            category_stats[category]["error"] += 1

        if not response or not response.strip():
            missing_outputs += 1
            category_stats[category]["missing_response"] += 1

        if score_status == "manual_review_required":
            manual_review_required += 1

    # Also count missing from the ok/error counts
    if not results and total > 0:
        missing_outputs = total

    summary = {
        "total_prompts": total,
        "ok": ok_count,
        "errors": error_count,
        "results_in_file": len(results),
        "missing_outputs": missing_outputs,
        "manual_review_required": manual_review_required,
        "categories": category_stats,
        "has_scores": False,
        "note": "No scores were invented. All score_status values require manual review.",
    }

    return summary


def main() -> None:
    """CLI entry point for summarizing KimariFit results."""
    parser = argparse.ArgumentParser(
        description="Summarize KimariFit evaluation results. No model required. Does NOT invent scores.",
    )
    parser.add_argument("--input", type=Path, required=True, help="Path to KimariFit result JSON file")
    parser.add_argument("--json", action="store_true", dest="json_output", help="Output summary as JSON")

    args = parser.parse_args()

    summary = summarize_result_file(args.input)

    if args.json_output:
        print(json.dumps(summary, indent=2))
    else:
        print("KimariFit Results Summary")
        print("=" * 40)
        if "error" in summary:
            print(f"ERROR: {summary['error']}")
            sys.exit(1)

        print(f"Total prompts:    {summary['total_prompts']}")
        print(f"OK:               {summary['ok']}")
        print(f"Errors:           {summary['errors']}")
        print(f"Results in file:  {summary['results_in_file']}")
        print(f"Missing outputs:  {summary['missing_outputs']}")
        print(f"Manual review:    {summary['manual_review_required']}")
        print()

        if summary["categories"]:
            print("Category Breakdown:")
            for cat, stats in sorted(summary["categories"].items()):
                print(
                    f"  {cat}: {stats['total']} total, {stats['ok']} ok, {stats['error']} error, {stats['missing_response']} missing"
                )
            print()

        print(f"Has scores: {summary['has_scores']}")
        print(f"Note: {summary['note']}")


if __name__ == "__main__":
    main()
