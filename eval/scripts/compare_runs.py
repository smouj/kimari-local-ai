#!/usr/bin/env python3
"""CLI tool for comparing two KimariFit eval result files.

Reads two JSON eval result files (baseline and candidate) and compares:
- prompt_count
- category_coverage
- manual_review_required count
- missing_outputs count
- average_score (if present in both; otherwise omitted)
- verdict (candidate_better, candidate_worse, mixed, insufficient_data,
  manual_review_required)
- safety_regression_detected (if present in candidate data)

If no scores exist in either file, returns comparison_status
"manual_review_required". Never invents scores.

Usage:
    python eval/scripts/compare_runs.py \\
        --baseline eval/results/baseline.json \\
        --candidate eval/results/candidate.json
    python eval/scripts/compare_runs.py \\
        --baseline eval/results/baseline.json \\
        --candidate eval/results/candidate.json --json
    python eval/scripts/compare_runs.py \\
        --baseline eval/results/baseline.json \\
        --candidate eval/results/candidate.json \\
        --summary-output eval/results/comparison-summary.json
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def load_eval_result(path: Path) -> dict | None:
    """Load an eval result JSON file.

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


def compute_stats(data: dict) -> dict:
    """Compute comparison statistics from an eval result dict.

    Returns a stats dict with prompt_count, category_coverage,
    manual_review_required, missing_outputs, and optionally
    average_score. Never invents scores.
    """
    results = data.get("results", [])
    total = data.get("total", len(results))

    # Category coverage
    categories: set[str] = set()
    manual_review_count = 0
    missing_outputs = 0

    for result in results:
        category = result.get("category", "unknown")
        categories.add(category)

        score_status = result.get("score_status", "")
        if score_status == "manual_review_required":
            manual_review_count += 1

        response = result.get("response", "")
        if not response or not str(response).strip():
            missing_outputs += 1

    # If no results but total > 0, all are missing
    if not results and total > 0:
        missing_outputs = total

    stats: dict = {
        "prompt_count": total,
        "category_coverage": sorted(categories),
        "category_count": len(categories),
        "manual_review_required": manual_review_count,
        "missing_outputs": missing_outputs,
    }

    # Only include average_score if it actually exists in the data
    if "average_score" in data:
        stats["average_score"] = data["average_score"]

    return stats


def _compute_category_deltas(baseline: dict, candidate: dict) -> dict[str, float]:
    """Compute per-category score deltas between baseline and candidate.

    Looks at individual result entries that share a category and have
    numeric scores. Returns a dict mapping category name to delta
    (positive = candidate better). Categories with no scorable results
    in either file are omitted.
    """
    baseline_results = baseline.get("results", [])
    candidate_results = candidate.get("results", [])

    # Group scores by category
    baseline_cat_scores: dict[str, list[float]] = {}
    candidate_cat_scores: dict[str, list[float]] = {}

    for r in baseline_results:
        cat = r.get("category", "unknown")
        score = r.get("score")
        if score is not None and isinstance(score, (int, float)):
            baseline_cat_scores.setdefault(cat, []).append(float(score))

    for r in candidate_results:
        cat = r.get("category", "unknown")
        score = r.get("score")
        if score is not None and isinstance(score, (int, float)):
            candidate_cat_scores.setdefault(cat, []).append(float(score))

    deltas: dict[str, float] = {}
    all_cats = set(baseline_cat_scores) | set(candidate_cat_scores)
    for cat in all_cats:
        b_scores = baseline_cat_scores.get(cat, [])
        c_scores = candidate_cat_scores.get(cat, [])
        if b_scores and c_scores:
            b_avg = sum(b_scores) / len(b_scores)
            c_avg = sum(c_scores) / len(c_scores)
            deltas[cat] = round(c_avg - b_avg, 4)

    return deltas


def _determine_verdict(
    baseline_stats: dict,
    candidate_stats: dict,
    candidate_data: dict,
    baseline_has_score: bool,
    candidate_has_score: bool,
    category_deltas: dict[str, float],
) -> str:
    """Determine the comparison verdict.

    Returns one of:
    - "insufficient_data" — no scores in either file AND/OR missing_outputs > 0
      in candidate
    - "candidate_better" — candidate average_score > baseline AND no safety
      regression
    - "candidate_worse" — candidate average_score < baseline OR
      safety_regression_detected=true in candidate
    - "mixed" — some categories improved, some regressed
    - "manual_review_required" — default when data is insufficient to
      determine direction
    """
    # Check for safety regression in candidate data
    safety_regression = candidate_data.get("safety_regression_detected", False)
    if safety_regression:
        return "candidate_worse"

    # Check for insufficient data
    missing_outputs = candidate_stats.get("missing_outputs", 0)
    if (not baseline_has_score and not candidate_has_score) or missing_outputs > 0:
        return "insufficient_data"

    # Need scores in both to determine direction
    if not (baseline_has_score and candidate_has_score):
        return "manual_review_required"

    # Check overall score direction
    baseline_avg = baseline_stats.get("average_score", 0)
    candidate_avg = candidate_stats.get("average_score", 0)

    # Check per-category deltas for mixed verdict
    if category_deltas:
        improved = sum(1 for d in category_deltas.values() if d > 0)
        regressed = sum(1 for d in category_deltas.values() if d < 0)
        if improved > 0 and regressed > 0:
            return "mixed"

    if candidate_avg > baseline_avg:
        return "candidate_better"
    elif candidate_avg < baseline_avg:
        return "candidate_worse"
    else:
        return "manual_review_required"


def compare_eval_results(baseline: dict, candidate: dict) -> dict:
    """Compare two eval result dicts and return structured comparison.

    Never invents scores. If average_score exists in both, includes
    it with delta. Otherwise omits it entirely.

    Adds a "verdict" field based on comparison logic:
    - "insufficient_data" — no scores AND/OR missing_outputs > 0
    - "candidate_better" — candidate > baseline, no safety regression
    - "candidate_worse" — candidate < baseline OR safety regression
    - "mixed" — some categories improved, some regressed
    - "manual_review_required" — default when data is insufficient
    """
    baseline_stats = compute_stats(baseline)
    candidate_stats = compute_stats(candidate)

    comparison: dict = {
        "baseline": baseline_stats,
        "candidate": candidate_stats,
    }

    # Prompt count delta
    prompt_delta = candidate_stats["prompt_count"] - baseline_stats["prompt_count"]
    comparison["prompt_count_delta"] = prompt_delta

    # Category coverage comparison
    baseline_cats = set(baseline_stats["category_coverage"])
    candidate_cats = set(candidate_stats["category_coverage"])
    comparison["categories_added"] = sorted(candidate_cats - baseline_cats)
    comparison["categories_removed"] = sorted(baseline_cats - candidate_cats)
    comparison["categories_shared"] = sorted(baseline_cats & candidate_cats)

    # Manual review delta
    mr_delta = candidate_stats["manual_review_required"] - baseline_stats["manual_review_required"]
    comparison["manual_review_required_delta"] = mr_delta

    # Missing outputs delta
    missing_delta = candidate_stats["missing_outputs"] - baseline_stats["missing_outputs"]
    comparison["missing_outputs_delta"] = missing_delta

    # Average score comparison — only if present in BOTH
    baseline_has_score = "average_score" in baseline_stats
    candidate_has_score = "average_score" in candidate_stats

    if baseline_has_score and candidate_has_score:
        score_delta = candidate_stats["average_score"] - baseline_stats["average_score"]
        comparison["average_score_delta"] = round(score_delta, 4)
    elif baseline_has_score or candidate_has_score:
        comparison["average_score_note"] = "average_score present in only one file — cannot compare"

    # Safety regression detection from candidate data
    safety_regression = candidate.get("safety_regression_detected", False)
    comparison["safety_regression_detected"] = safety_regression

    # Per-category score deltas
    category_deltas = _compute_category_deltas(baseline, candidate)
    if category_deltas:
        comparison["category_score_deltas"] = category_deltas

    # Determine comparison_status (legacy field)
    has_any_score = baseline_has_score or candidate_has_score
    if not has_any_score:
        comparison["comparison_status"] = "manual_review_required"
    elif baseline_has_score and candidate_has_score:
        score_delta = candidate_stats["average_score"] - baseline_stats["average_score"]
        if score_delta > 0:
            comparison["comparison_status"] = "improved"
        elif score_delta < 0:
            comparison["comparison_status"] = "regressed"
        else:
            comparison["comparison_status"] = "unchanged"
    else:
        comparison["comparison_status"] = "manual_review_required"

    # Determine verdict
    comparison["verdict"] = _determine_verdict(
        baseline_stats=baseline_stats,
        candidate_stats=candidate_stats,
        candidate_data=candidate,
        baseline_has_score=baseline_has_score,
        candidate_has_score=candidate_has_score,
        category_deltas=category_deltas,
    )

    return comparison


def _build_summary_output(comparison: dict, candidate: dict) -> dict:
    """Build a safe eval summary from comparison results.

    The summary contains no raw prompts or responses — only
    aggregate metadata safe for committing to the repository.
    """
    candidate_stats = comparison.get("candidate", {})

    summary: dict = {
        "run_id": candidate.get("run_id", ""),
        "model_label": candidate.get("model_label", ""),
        "kimari_version": candidate.get("kimari_version", ""),
        "prompt_count": candidate_stats.get("prompt_count", 0),
        "category_counts": {
            cat: candidate_stats.get("category_coverage", []).count(cat)
            for cat in candidate_stats.get("category_coverage", [])
        },
        "score_status": "manual_review_required"
        if comparison.get("verdict") in ("insufficient_data", "manual_review_required")
        else "scored",
        "manual_review_required": comparison.get("verdict") in ("insufficient_data", "manual_review_required", "mixed"),
        "safety_regression_detected": comparison.get("safety_regression_detected", False),
        "false_claims_detected": candidate.get("false_claims_detected", False),
        "verdict": comparison.get("verdict", "manual_review_required"),
        "reviewer": candidate.get("reviewer", ""),
        "notes": candidate.get("notes", ""),
    }

    return summary


def main() -> None:
    """CLI entry point for comparing eval results."""
    parser = argparse.ArgumentParser(
        description="Compare two KimariFit eval result files. Never invents scores.",
    )
    parser.add_argument(
        "--baseline",
        type=Path,
        required=True,
        help="Path to baseline eval result JSON file",
    )
    parser.add_argument(
        "--candidate",
        type=Path,
        required=True,
        help="Path to candidate eval result JSON file",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        dest="json_output",
        help="Output structured JSON comparison",
    )
    parser.add_argument(
        "--summary-output",
        type=Path,
        default=None,
        help="If provided, write a committable eval summary JSON to this path",
    )

    args = parser.parse_args()

    # Load files
    baseline = load_eval_result(args.baseline)
    candidate = load_eval_result(args.candidate)

    if baseline is None or candidate is None:
        sys.exit(1)

    # Compare
    comparison = compare_eval_results(baseline, candidate)

    # Output
    if args.json_output:
        print(json.dumps(comparison, indent=2))
    else:
        print("KimariFit Eval Comparison")
        print("=" * 50)
        print()

        b = comparison["baseline"]
        c = comparison["candidate"]

        print(f"Baseline:  {args.baseline}")
        print(f"Candidate: {args.candidate}")
        print()

        print("Prompt Count:")
        print(f"  Baseline:  {b['prompt_count']}")
        print(f"  Candidate: {c['prompt_count']}")
        delta = comparison["prompt_count_delta"]
        sign = "+" if delta > 0 else ""
        print(f"  Delta:     {sign}{delta}")
        print()

        print("Category Coverage:")
        print(f"  Baseline:  {b['category_count']} ({', '.join(b['category_coverage'])})")
        print(f"  Candidate: {c['category_count']} ({', '.join(c['category_coverage'])})")
        if comparison["categories_added"]:
            print(f"  Added:     {', '.join(comparison['categories_added'])}")
        if comparison["categories_removed"]:
            print(f"  Removed:   {', '.join(comparison['categories_removed'])}")
        print()

        print("Manual Review Required:")
        print(f"  Baseline:  {b['manual_review_required']}")
        print(f"  Candidate: {c['manual_review_required']}")
        mr_delta = comparison["manual_review_required_delta"]
        sign = "+" if mr_delta > 0 else ""
        print(f"  Delta:     {sign}{mr_delta}")
        print()

        print("Missing Outputs:")
        print(f"  Baseline:  {b['missing_outputs']}")
        print(f"  Candidate: {c['missing_outputs']}")
        missing_delta = comparison["missing_outputs_delta"]
        sign = "+" if missing_delta > 0 else ""
        print(f"  Delta:     {sign}{missing_delta}")
        print()

        if "average_score_delta" in comparison:
            print("Average Score:")
            print(f"  Baseline:  {b['average_score']}")
            print(f"  Candidate: {c['average_score']}")
            delta = comparison["average_score_delta"]
            sign = "+" if delta > 0 else ""
            print(f"  Delta:     {sign}{delta}")
            print()
        elif "average_score_note" in comparison:
            print(f"Score: {comparison['average_score_note']}")
            print()

        print(f"Comparison Status: {comparison['comparison_status']}")
        print(f"Verdict: {comparison['verdict']}")

        if comparison.get("safety_regression_detected"):
            print("\n⚠  Safety regression detected in candidate — verdict: candidate_worse")

        if comparison["comparison_status"] == "manual_review_required":
            print("No scores available — manual review is required.")

        if comparison["verdict"] == "insufficient_data":
            print("Insufficient data to determine comparison direction.")
        elif comparison["verdict"] == "mixed":
            print("Some categories improved, some regressed — manual review required.")

    # Write summary output if requested
    if args.summary_output is not None:
        summary = _build_summary_output(comparison, candidate)
        args.summary_output.parent.mkdir(parents=True, exist_ok=True)
        with open(args.summary_output, "w") as f:
            json.dump(summary, f, indent=2)
            f.write("\n")
        print(f"\nSummary written to: {args.summary_output}", file=sys.stderr)


if __name__ == "__main__":
    main()
