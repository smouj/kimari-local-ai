#!/usr/bin/env python3
"""CLI for adapter eval planning.

Produces an evaluation plan for an adapter (after SFT):
- model_label
- prompts_path
- prompt_count (counted from the prompts file)
- categories (extracted from prompts)
- recommended_endpoint
- recommended_output
- score_status
- steps (list of steps to execute)

In dry-run: does NOT call any endpoint, just prints the plan.

No real training. No model downloads. No HF uploads.

Usage:
    python eval/scripts/run_adapter_eval_plan.py \\
        --model-label kimari-smollm3-sft-v0 \\
        --prompts eval/kimarifit_prompts.jsonl
    python eval/scripts/run_adapter_eval_plan.py \\
        --model-label kimari-smollm3-sft-v0 \\
        --prompts eval/kimarifit_prompts.jsonl \\
        --dry-run --json
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

DEFAULT_PROMPTS = PROJECT_ROOT / "eval" / "kimarifit_prompts.jsonl"
DEFAULT_ENDPOINT = "http://127.0.0.1:8080/v1"

BASELINE_RESULT_PATH = PROJECT_ROOT / "eval" / "results" / "baseline-smollm3-private.json"


# ---------------------------------------------------------------------------
# Prompt loading and analysis
# ---------------------------------------------------------------------------


def load_prompts(path: Path) -> tuple[list[dict], list[str]]:
    """Load JSONL prompts file. Returns (records, errors)."""
    records: list[dict] = []
    errors: list[str] = []

    if not path.exists():
        errors.append(f"Prompts file not found: {path}")
        return records, errors

    with open(path) as f:
        for line_num, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                record = json.loads(line)
                if not isinstance(record, dict):
                    errors.append(f"line {line_num}: not a JSON object")
                    continue
                records.append(record)
            except json.JSONDecodeError as exc:
                errors.append(f"line {line_num}: invalid JSON — {exc}")

    return records, errors


def extract_categories(records: list[dict]) -> dict[str, int]:
    """Extract category counts from prompt records."""
    categories: dict[str, int] = {}
    for record in records:
        cat = record.get("category", "unknown")
        categories[cat] = categories.get(cat, 0) + 1
    return categories


# ---------------------------------------------------------------------------
# Plan builder
# ---------------------------------------------------------------------------


def build_adapter_eval_plan(
    model_label: str,
    prompts_path: Path,
    dry_run: bool,
) -> dict:
    """Build the adapter eval plan."""
    # Load prompts
    records, errors = load_prompts(prompts_path)
    categories = extract_categories(records)

    # Recommended output path
    safe_label = model_label.replace("/", "-").replace(" ", "-").lower()
    recommended_output = PROJECT_ROOT / "eval" / "results" / f"adapter-{safe_label}-private.json"

    # Steps to execute
    steps = [
        {
            "step": 1,
            "action": "merge_adapter",
            "description": "Merge adapter weights with base model for inference",
            "command": "# Merge using PEFT: model = PeftModel.from_pretrained(base, adapter_path)",
            "dry_run_skip": True,
        },
        {
            "step": 2,
            "action": "start_server",
            "description": "Start llama-server with the merged model",
            "command": "kimari start --profile <profile> --model <merged_model_path>",
            "dry_run_skip": True,
        },
        {
            "step": 3,
            "action": "verify_endpoint",
            "description": f"Verify the server is running at {DEFAULT_ENDPOINT}",
            "command": f"curl -s {DEFAULT_ENDPOINT}/models | python -m json.tool",
            "dry_run_skip": True,
        },
        {
            "step": 4,
            "action": "run_eval",
            "description": "Run KimariFit eval against the adapter model",
            "command": f"python eval/kimarifit.py --endpoint {DEFAULT_ENDPOINT} "
            f"--prompts {prompts_path} --output {recommended_output}",
            "dry_run_skip": True,
        },
        {
            "step": 5,
            "action": "create_summary",
            "description": "Create eval summary from raw results",
            "command": f"python eval/scripts/create_eval_summary.py "
            f"--input {recommended_output} --output eval/results/adapter-{safe_label}-summary.json",
            "dry_run_skip": True,
        },
        {
            "step": 6,
            "action": "compare_with_baseline",
            "description": "Compare adapter results with baseline (if baseline exists)",
            "command": f"python eval/scripts/compare_runs.py "
            f"--baseline {BASELINE_RESULT_PATH} --candidate {recommended_output} --json",
            "dry_run_skip": True,
        },
        {
            "step": 7,
            "action": "check_safety",
            "description": "Check for safety regressions in adapter results",
            "command": "# Manual review of safety-related categories (local_security, refusal)",
            "dry_run_skip": False,
        },
        {
            "step": 8,
            "action": "manual_review",
            "description": "Manually review eval results for quality and safety",
            "command": "# Manual step — no automated command",
            "dry_run_skip": False,
        },
        {
            "step": 9,
            "action": "commit_summary",
            "description": "Commit the eval summary (NOT raw results with prompts/responses)",
            "command": f"git add eval/results/adapter-{safe_label}-summary.json",
            "dry_run_skip": True,
        },
    ]

    has_baseline = BASELINE_RESULT_PATH.exists()

    plan: dict = {
        "model_label": model_label,
        "prompts_path": str(prompts_path),
        "prompt_count": len(records),
        "categories": categories,
        "category_count": len(categories),
        "recommended_endpoint": DEFAULT_ENDPOINT,
        "recommended_output": str(recommended_output),
        "baseline_available": has_baseline,
        "baseline_path": str(BASELINE_RESULT_PATH) if has_baseline else None,
        "score_status": "manual_review_required",
        "steps": steps,
        "dry_run": dry_run,
        "errors": errors if errors else None,
    }

    return plan


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main() -> None:
    """CLI entry point for adapter eval planning."""
    parser = argparse.ArgumentParser(
        description="Adapter eval planning for Kimari models. No real training. No model downloads. No HF uploads.",
    )
    parser.add_argument(
        "--model-label",
        default="kimari-smollm3-sft-v0",
        help="Label for the adapter model being evaluated (default: kimari-smollm3-sft-v0)",
    )
    parser.add_argument(
        "--prompts",
        type=Path,
        default=DEFAULT_PROMPTS,
        help="Path to KimariFit prompts JSONL file (default: eval/kimarifit_prompts.jsonl)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        default=True,
        help="Dry-run mode — do not call any endpoint (default: True)",
    )
    parser.add_argument(
        "--no-dry-run",
        action="store_false",
        dest="dry_run",
        help="Disable dry-run (plan will list steps that would be executed)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        dest="json_output",
        help="Output structured JSON plan",
    )

    args = parser.parse_args()

    plan = build_adapter_eval_plan(
        model_label=args.model_label,
        prompts_path=args.prompts,
        dry_run=args.dry_run,
    )

    if args.json_output:
        print(json.dumps(plan, indent=2, default=str))
    else:
        print()
        print("=" * 60)
        mode = "DRY-RUN" if plan["dry_run"] else "LIVE"
        print(f"  Adapter Eval Plan [{mode}]")
        print("=" * 60)
        print()
        print(f"  Model:              {plan['model_label']}")
        print(f"  Prompts:            {plan['prompts_path']}")
        print(f"  Prompt Count:       {plan['prompt_count']}")
        print(f"  Categories:         {plan['category_count']}")
        print()
        print("  Category Breakdown:")
        for cat, count in sorted(plan["categories"].items()):
            print(f"    {cat:<28s} {count}")
        print()
        print(f"  Recommended Endpoint: {plan['recommended_endpoint']}")
        print(f"  Recommended Output:   {plan['recommended_output']}")
        print(f"  Baseline Available:   {plan['baseline_available']}")
        if plan["baseline_available"]:
            print(f"  Baseline Path:        {plan['baseline_path']}")
        print(f"  Score Status:         {plan['score_status']}")
        print()
        print("  Steps:")
        for step in plan["steps"]:
            skip_marker = " [SKIP IN DRY-RUN]" if step["dry_run_skip"] and plan["dry_run"] else ""
            print(f"    {step['step']}. {step['action']}: {step['description']}{skip_marker}")
            if step.get("command"):
                print(f"       $ {step['command']}")

        if plan.get("errors"):
            print()
            print("  Errors:")
            for err in plan["errors"]:
                print(f"    \u2717 {err}")

        print()
        print("=" * 60)
        if plan["dry_run"]:
            print("  This is a dry-run. No endpoints were called.")
            print("  Use --no-dry-run to execute the plan.")
        else:
            print("  Ensure the merged adapter model is served via llama-server.")
        print("=" * 60)

    sys.exit(0)


if __name__ == "__main__":
    main()
