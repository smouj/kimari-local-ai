#!/usr/bin/env python3
"""Evaluate Kimari-4B adapter vs baseline.

Compares responses from baseline and adapter endpoints.
Defaults to dry-run (no actual API calls).

Usage:
    python eval/scripts/evaluate_kimari4b_adapter.py --baseline-endpoint http://localhost:11435/v1 --adapter-endpoint http://localhost:11436/v1 --dry-run
    python eval/scripts/evaluate_kimari4b_adapter.py --baseline-endpoint ... --adapter-endpoint ... --json
    python eval/scripts/evaluate_kimari4b_adapter.py --dry-run --summary-output eval/results/summary.json
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

PROMPTS_DIR = PROJECT_ROOT / "eval" / "prompts"
RESULTS_DIR = PROJECT_ROOT / "eval" / "results"
DEFAULT_PROMPTS = PROMPTS_DIR / "kimarifit-v0.jsonl"


def dry_run_eval(config: dict) -> dict:
    """Simulate evaluation without API calls."""
    result = {
        "mode": "dry-run",
        "baseline_endpoint": config.get("baseline_endpoint", ""),
        "adapter_endpoint": config.get("adapter_endpoint", ""),
        "prompts_file": str(config.get("prompts_file", DEFAULT_PROMPTS)),
        "summary_output": config.get("summary_output", ""),
        "prompts_exist": Path(config.get("prompts_file", "") or str(DEFAULT_PROMPTS)).exists(),
        "eval_categories": [
            "kimarifit",
            "safety_regression",
            "spanish_technical",
            "coding_sysadmin",
            "json_mode",
        ],
        "scoring_dimensions": ["correctness", "helpfulness", "safety", "format"],
        "note": "Dry-run. No API calls made. No scores invented.",
    }
    return result


def real_eval(config: dict) -> dict:
    """Run real evaluation against both endpoints."""
    baseline = config.get("baseline_endpoint", "")
    adapter = config.get("adapter_endpoint", "")

    if not baseline or not adapter:
        return {"error": "Both --baseline-endpoint and --adapter-endpoint required for real eval"}

    prompts_file = Path(config.get("prompts_file", "") or str(DEFAULT_PROMPTS))
    if not prompts_file.exists():
        return {"error": f"Prompts file not found: {prompts_file}"}

    # Load prompts
    prompts = []
    with open(prompts_file) as f:
        for line in f:
            if line.strip():
                prompts.append(json.loads(line))

    if not prompts:
        return {"error": "No prompts loaded from file"}

    # Run evaluation
    results = []
    for prompt_data in prompts:
        prompt_text = prompt_data.get("prompt", "")
        category = prompt_data.get("category", "unknown")

        # Call baseline
        baseline_resp = _call_endpoint(baseline, prompt_text)
        # Call adapter
        adapter_resp = _call_endpoint(adapter, prompt_text)

        results.append(
            {
                "category": category,
                "prompt_preview": prompt_text[:80] + "..." if len(prompt_text) > 80 else prompt_text,
                "baseline_length": len(baseline_resp),
                "adapter_length": len(adapter_resp),
                # Scores would be assigned by human review, not automatically
                "auto_scored": False,
            }
        )

    summary = {
        "mode": "real-eval",
        "total_prompts": len(prompts),
        "categories": list(set(p.get("category", "unknown") for p in prompts)),
        "baseline_endpoint": baseline,
        "adapter_endpoint": adapter,
        "evaluated_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "results_count": len(results),
        "note": "Results recorded. Scoring requires manual human review. No auto-scores.",
        "gate_state": "BLOCKED",
    }

    # Save raw results (gitignored)
    if config.get("summary_output"):
        output_path = Path(config["summary_output"])
        output_path.parent.mkdir(parents=True, exist_ok=True)
        # Only save summary, not raw outputs
        with open(output_path, "w") as f:
            json.dump(summary, f, indent=2)

    return summary


def _call_endpoint(endpoint: str, prompt: str) -> str:
    """Make an OpenAI-compatible chat completion call."""
    try:
        import urllib.request

        url = f"{endpoint}/chat/completions"
        data = json.dumps(
            {
                "model": "default",
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 512,
                "temperature": 0.3,
            }
        ).encode()
        req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=30) as resp:
            result = json.loads(resp.read())
            return result.get("choices", [{}])[0].get("message", {}).get("content", "")
    except Exception as e:
        return f"[ERROR: {e}]"


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate Kimari-4B adapter")
    parser.add_argument("--baseline-endpoint", default="", help="Baseline model endpoint URL")
    parser.add_argument("--adapter-endpoint", default="", help="Adapter model endpoint URL")
    parser.add_argument("--dry-run", action="store_true", default=True, help="Dry-run (default)")
    parser.add_argument("--prompts-file", default=str(DEFAULT_PROMPTS), help="Path to prompts JSONL")
    parser.add_argument("--summary-output", default="", help="Path to save summary JSON")
    parser.add_argument("--json", action="store_true", help="JSON output")
    args = parser.parse_args()

    config = {
        "baseline_endpoint": args.baseline_endpoint,
        "adapter_endpoint": args.adapter_endpoint,
        "prompts_file": args.prompts_file,
        "summary_output": args.summary_output,
    }

    if args.dry_run or not (args.baseline_endpoint and args.adapter_endpoint):
        result = dry_run_eval(config)
    else:
        result = real_eval(config)

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print("Kimari-4B Adapter Evaluation")
        print("=" * 50)
        for key, value in result.items():
            print(f"  {key}: {value}")
        print("=" * 50)

    if result.get("error"):
        sys.exit(1)


if __name__ == "__main__":
    main()
