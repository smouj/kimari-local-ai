#!/usr/bin/env python3
"""Compare KimariEval baseline vs adapter evaluation runs.

Usage:
    python eval/scripts/compare_kimari_eval_runs.py \
        --baseline-summary reports/evals/baseline.json \
        --adapter-summary reports/evals/adapter.json \
        --output-md reports/evals/comparison.md \
        --output-json reports/evals/comparison.json
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def load_summary(path: str) -> dict:
    """Load an eval summary JSON file."""
    p = Path(path)
    if not p.exists():
        print(f"ERROR: Summary not found: {path}", file=sys.stderr)
        sys.exit(1)
    return json.loads(p.read_text())


def compare_summaries(baseline: dict, adapter: dict) -> dict:
    """Compare baseline and adapter evaluation summaries."""
    result = {
        "comparison_id": f"compare-{baseline.get('run_id', 'unknown')}-vs-{adapter.get('run_id', 'unknown')}",
        "baseline_run_id": baseline.get("run_id"),
        "adapter_run_id": adapter.get("run_id"),
        "baseline_model": baseline.get("model_label", baseline.get("base_model")),
        "adapter_model": adapter.get("model_label", adapter.get("base_model")),
        "adapter_repo": adapter.get("adapter_repo_private"),
        "dataset_id": baseline.get("dataset_id", "unknown"),
        "baseline_completion_rate": baseline.get("baseline", baseline.get("completion_rate", 0)),
        "adapter_completion_rate": adapter.get("adapter", adapter.get("completion_rate", 0)),
        "baseline_items": baseline.get("total_items", baseline.get("baseline", {}).get("total_items", 0)),
        "adapter_items": adapter.get("total_items", adapter.get("adapter", {}).get("total_items", 0)),
        "baseline_errors": baseline.get("baseline", {}).get("error_items", 0),
        "adapter_errors": adapter.get("adapter", {}).get("error_items", 0),
        "score_status": "not_scored",
        "manual_review_required": True,
        "raw_outputs_committed": False,
        "public_benchmark_allowed": False,
        "gate_state": "BLOCKED",
        "categories_baseline": baseline.get("categories", {}),
        "categories_adapter": adapter.get("categories", {}),
        "notes": "Comparison generated. Scores not computed (requires manual review). No benchmark claims. Gate BLOCKED.",
    }
    return result


def format_markdown(comparison: dict) -> str:
    """Format comparison as Markdown."""
    lines = [
        f"# KimariEval Comparison: {comparison['baseline_model']} vs Adapter",
        "",
        f"- **Baseline run**: {comparison['baseline_run_id']}",
        f"- **Adapter run**: {comparison['adapter_run_id']}",
        f"- **Adapter repo**: {comparison['adapter_repo']}",
        f"- **Dataset**: {comparison['dataset_id']}",
        f"- **Baseline completion rate**: {comparison['baseline_completion_rate']}",
        f"- **Adapter completion rate**: {comparison['adapter_completion_rate']}",
        f"- **Baseline items**: {comparison['baseline_items']} ({comparison['baseline_errors']} errors)",
        f"- **Adapter items**: {comparison['adapter_items']} ({comparison['adapter_errors']} errors)",
        f"- **Score status**: {comparison['score_status']}",
        f"- **Manual review required**: {comparison['manual_review_required']}",
        f"- **Raw outputs committed**: {comparison['raw_outputs_committed']}",
        f"- **Public benchmark allowed**: {comparison['public_benchmark_allowed']}",
        f"- **Gate state**: {comparison['gate_state']}",
        "",
        "## Notes",
        "",
        comparison["notes"],
        "",
        "⚠️ No benchmark claims. Gate BLOCKED. Manual review required.",
    ]
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Compare KimariEval baseline vs adapter")
    parser.add_argument("--baseline-summary", required=True, help="Baseline summary JSON")
    parser.add_argument("--adapter-summary", required=True, help="Adapter summary JSON")
    parser.add_argument("--output-md", help="Output Markdown file")
    parser.add_argument("--output-json", help="Output JSON file")
    parser.add_argument("--json", action="store_true", help="JSON output to stdout")
    args = parser.parse_args()

    baseline = load_summary(args.baseline_summary)
    adapter = load_summary(args.adapter_summary)

    comparison = compare_summaries(baseline, adapter)

    if args.output_json:
        Path(args.output_json).parent.mkdir(parents=True, exist_ok=True)
        Path(args.output_json).write_text(json.dumps(comparison, indent=2, ensure_ascii=False))
        print(f"JSON written to {args.output_json}")

    if args.output_md:
        Path(args.output_md).parent.mkdir(parents=True, exist_ok=True)
        Path(args.output_md).write_text(format_markdown(comparison))
        print(f"Markdown written to {args.output_md}")

    if args.json:
        print(json.dumps(comparison, indent=2, ensure_ascii=False))
    else:
        for k, v in comparison.items():
            if isinstance(v, dict):
                print(f"  {k}:")
                for sk, sv in v.items():
                    print(f"    {sk}: {sv}")
            else:
                print(f"  {k}: {v}")


if __name__ == "__main__":
    main()
