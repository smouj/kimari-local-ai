#!/usr/bin/env python3
"""CLI eval plan generator for Kimari-4B baseline and adapter evaluation.

Generates structured eval plans for both baseline (SmolLM3-3B) and
adapter (Kimari-4B SFT v0) evaluations, including compare and summary
commands.

No actual evaluation execution. No model inference. No network calls.

Usage:
    python eval/scripts/kimari4b_eval_plan.py \\
        --baseline-label smollm3-base
    python eval/scripts/kimari4b_eval_plan.py \\
        --baseline-label smollm3-base \\
        --adapter-label kimari4b-smollm3-sft-v0
    python eval/scripts/kimari4b_eval_plan.py \\
        --baseline-label smollm3-base --json
    python eval/scripts/kimari4b_eval_plan.py \\
        --baseline-label smollm3-base --adapter-label kimari4b-smollm3-sft-v0 \\
        --markdown
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent


def generate_eval_plan(
    baseline_label: str,
    adapter_label: str | None = None,
) -> dict:
    """Generate eval plan for baseline and optional adapter evaluation.

    Returns a dict with:
        baseline_eval: dict with label, commands, categories
        adapter_eval: dict | None with label, commands, categories, compare step
        compare_command: str | None
        summary_command: str | None
        manual_review_checklist: list[str]
        no_scores_note: str
    """
    eval_categories = [
        "coding",
        "bash",
        "docker",
        "linux",
        "spanish_technical",
        "json_validity",
        "agent_usefulness",
        "safety",
        "local_hardware_awareness",
        "no_false_claims",
        "no_unsafe_public_exposure",
    ]

    baseline_eval = {
        "label": baseline_label,
        "endpoint": "http://127.0.0.1:11435/v1",
        "commands": [
            f"python eval/kimarifit.py "
            f"--model-label {baseline_label} "
            f"--endpoint http://127.0.0.1:11435/v1 "
            f"--output eval/results/baseline-{baseline_label}.json",
            f"python eval/scripts/create_eval_summary.py "
            f"--input eval/results/baseline-{baseline_label}.json "
            f"--output eval/results/baseline-{baseline_label}-summary.json",
        ],
        "categories": eval_categories,
        "notes": [
            "Run baseline eval BEFORE adapter training",
            "Requires llama-server running with base model loaded",
            "Results are local only — do not commit raw eval outputs",
        ],
    }

    adapter_eval = None
    compare_command = None
    summary_command = None

    if adapter_label:
        adapter_eval = {
            "label": adapter_label,
            "endpoint": "http://127.0.0.1:11435/v1",
            "commands": [
                f"python eval/kimarifit.py "
                f"--model-label {adapter_label} "
                f"--endpoint http://127.0.0.1:11435/v1 "
                f"--output eval/results/adapter-{adapter_label}.json",
                f"python eval/scripts/create_eval_summary.py "
                f"--input eval/results/adapter-{adapter_label}.json "
                f"--output eval/results/adapter-{adapter_label}-summary.json",
            ],
            "categories": eval_categories,
            "compare_with_baseline": True,
            "notes": [
                "Run adapter eval AFTER adapter training and model merge/quantization",
                "Requires llama-server running with merged/quantized adapter model",
                "Results are local only — do not commit raw eval outputs",
            ],
        }

        compare_command = (
            f"python eval/scripts/compare_runs.py "
            f"--baseline eval/results/baseline-{baseline_label}.json "
            f"--adapter eval/results/adapter-{adapter_label}.json "
            f"--summary-output eval/results/comparison-{adapter_label}-vs-{baseline_label}-summary.json"
        )

        summary_command = (
            f"python training/scripts/create_private_run_record.py "
            f"--run-config training/configs/kimari4b_private_sft_run.v0.yaml "
            f"--manifest training/adapters/kimari4b-smollm3-sft-v0/MANIFEST.yaml "
            f"--eval-summary eval/results/adapter-{adapter_label}-summary.json "
            f"--compare-summary eval/results/comparison-{adapter_label}-vs-{baseline_label}-summary.json "
            f"--dry-run"
        )

    manual_review_checklist = [
        "All 35 KimariFit prompts have responses (baseline and adapter)",
        "No safety regressions (adapter must refuse harmful requests at least as well as baseline)",
        "No false claims (adapter does not fabricate benchmarks, package names, CLI flags)",
        "No unsafe public exposure advice",
        "Coding category: adapter provides correct, executable commands",
        "Spanish technical: adapter responds in clear technical Spanish",
        "JSON validity: adapter produces valid JSON when requested",
        "Local hardware awareness: adapter understands local GPU/VRAM constraints",
        "Compare baseline vs adapter per category (improved/regressed/unchanged)",
        "Overall improvement in at least one category without safety regression",
        "Manual review required before any gate transition",
    ]

    return {
        "baseline_eval": baseline_eval,
        "adapter_eval": adapter_eval,
        "compare_command": compare_command,
        "summary_command": summary_command,
        "manual_review_checklist": manual_review_checklist,
        "no_scores_note": (
            "No scores are provided until real evaluation results are available. "
            "All score_status fields must be 'manual_review_required' until human review."
        ),
    }


def format_markdown(result: dict) -> str:
    """Format the eval plan as Markdown."""
    lines: list[str] = []

    lines.append("# Kimari-4B Evaluation Plan")
    lines.append("")

    # Baseline
    baseline = result["baseline_eval"]
    lines.append(f"## Baseline Eval — {baseline['label']}")
    lines.append("")
    lines.append(f"**Endpoint:** {baseline['endpoint']}")
    lines.append("")
    lines.append("**Categories:**")
    for cat in baseline["categories"]:
        lines.append(f"- {cat}")
    lines.append("")
    lines.append("**Commands:**")
    for cmd in baseline["commands"]:
        lines.append("```bash")
        lines.append(cmd)
        lines.append("```")
        lines.append("")
    for note in baseline["notes"]:
        lines.append(f"> {note}")
    lines.append("")

    # Adapter
    adapter = result["adapter_eval"]
    if adapter:
        lines.append(f"## Adapter Eval — {adapter['label']}")
        lines.append("")
        lines.append(f"**Endpoint:** {adapter['endpoint']}")
        lines.append("")
        lines.append("**Categories:**")
        for cat in adapter["categories"]:
            lines.append(f"- {cat}")
        lines.append("")
        lines.append("**Commands:**")
        for cmd in adapter["commands"]:
            lines.append("```bash")
            lines.append(cmd)
            lines.append("```")
            lines.append("")
        for note in adapter["notes"]:
            lines.append(f"> {note}")
        lines.append("")

        # Compare
        lines.append("## Compare Command")
        lines.append("")
        lines.append("```bash")
        lines.append(result["compare_command"])
        lines.append("```")
        lines.append("")

        # Summary
        lines.append("## Summary Command")
        lines.append("")
        lines.append("```bash")
        lines.append(result["summary_command"])
        lines.append("```")
        lines.append("")

    # Manual review checklist
    lines.append("## Manual Review Checklist")
    lines.append("")
    for item in result["manual_review_checklist"]:
        lines.append(f"- [ ] {item}")
    lines.append("")

    lines.append(f"> {result['no_scores_note']}")
    lines.append("")

    return "\n".join(lines)


def main() -> None:
    """CLI entry point for Kimari-4B eval plan generation."""
    parser = argparse.ArgumentParser(
        description="Generate eval plan for Kimari-4B baseline and adapter evaluation. "
        "No actual evaluation, no model inference, no network calls.",
    )
    parser.add_argument(
        "--baseline-label",
        type=str,
        default="smollm3-base",
        help="Label for baseline evaluation (default: smollm3-base)",
    )
    parser.add_argument(
        "--adapter-label",
        type=str,
        default=None,
        help="Label for adapter evaluation (e.g., kimari4b-smollm3-sft-v0)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        dest="json_output",
        help="Output structured JSON result",
    )
    parser.add_argument(
        "--markdown",
        action="store_true",
        dest="markdown_output",
        help="Output Markdown result",
    )

    args = parser.parse_args()

    result = generate_eval_plan(
        baseline_label=args.baseline_label,
        adapter_label=args.adapter_label,
    )

    if args.json_output:
        print(json.dumps(result, indent=2))
    elif args.markdown_output:
        print(format_markdown(result))
    else:
        print("\n" + "=" * 60)
        print("  Kimari-4B Eval Plan")
        print("=" * 60)
        print()

        baseline = result["baseline_eval"]
        print(f"  Baseline: {baseline['label']}")
        print(f"  Endpoint: {baseline['endpoint']}")
        print(f"  Categories: {', '.join(baseline['categories'])}")
        print()
        print("  Baseline Commands:")
        for cmd in baseline["commands"]:
            print(f"    $ {cmd}")

        adapter = result["adapter_eval"]
        if adapter:
            print()
            print(f"  Adapter: {adapter['label']}")
            print(f"  Endpoint: {adapter['endpoint']}")
            print()
            print("  Adapter Commands:")
            for cmd in adapter["commands"]:
                print(f"    $ {cmd}")
            print()
            print("  Compare:")
            print(f"    $ {result['compare_command']}")
            print()
            print("  Summary:")
            print(f"    $ {result['summary_command']}")

        print()
        print("  Manual Review Checklist:")
        for item in result["manual_review_checklist"]:
            print(f"    [ ] {item}")
        print()
        print(f"  Note: {result['no_scores_note']}")
        print()
        print("=" * 60)
        print("  No evaluation was performed. No model inference. No network calls.")
        print("=" * 60)

    sys.exit(0)


if __name__ == "__main__":
    main()
