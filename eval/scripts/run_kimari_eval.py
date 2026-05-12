#!/usr/bin/env python3
"""Run Kimari evaluation on a model endpoint.

Usage:
    # Dry-run (no model calls)
    python eval/scripts/run_kimari_eval.py --model-label qwen25-15b-base --dataset-dir eval/kimari_private_v1 --dry-run --json

    # With endpoint
    python eval/scripts/run_kimari_eval.py --model-label qwen25-15b-base --dataset-dir eval/kimari_private_v1 --endpoint http://127.0.0.1:8080/v1 --output-json reports/evals/baseline.json --json
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

DATASET_DIR = Path(__file__).resolve().parent.parent / "kimari_private_v1"


def load_dataset(dataset_dir: str) -> list[dict]:
    """Load all JSONL files from dataset directory."""
    items = []
    dataset_path = Path(dataset_dir)
    if not dataset_path.exists():
        print(f"ERROR: Dataset directory not found: {dataset_dir}", file=sys.stderr)
        sys.exit(1)

    for jsonl_file in sorted(dataset_path.glob("*.jsonl")):
        for line in jsonl_file.read_text().strip().split("\n"):
            if line.strip():
                items.append(json.loads(line))

    return items


def run_dry_run(model_label: str, dataset_dir: str) -> dict:
    """Generate a dry-run evaluation plan without calling any model."""
    items = load_dataset(dataset_dir)

    categories = {}
    difficulties = {"easy": 0, "medium": 0, "hard": 0}

    for item in items:
        cat = item.get("tags", ["unknown"])[0] if item.get("tags") else "unknown"
        categories[cat] = categories.get(cat, 0) + 1
        diff = item.get("difficulty", "medium")
        difficulties[diff] = difficulties.get(diff, 0) + 1

    result = {
        "eval_id": f"kimari-eval-dry-{model_label}",
        "model_label": model_label,
        "mode": "dry-run",
        "dataset_dir": str(dataset_dir),
        "total_items": len(items),
        "categories": categories,
        "difficulties": difficulties,
        "score_status": "not_scored",
        "manual_review_required": True,
        "no_benchmark_claim": True,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "notes": "Dry-run: no model calls made. Plan generated for review.",
    }

    return result


def run_evaluation(
    model_label: str,
    dataset_dir: str,
    endpoint: str | None = None,
    temperature: float = 0.1,
    max_tokens: int = 512,
) -> dict:
    """Run evaluation against a model endpoint."""
    if endpoint is None:
        return run_dry_run(model_label, dataset_dir)

    items = load_dataset(dataset_dir)

    try:
        import requests
    except ImportError:
        print("ERROR: requests library required for model evaluation", file=sys.stderr)
        sys.exit(1)

    results = []
    for item in items:
        try:
            response = requests.post(
                f"{endpoint}/chat/completions",
                json={
                    "model": model_label,
                    "messages": [{"role": "user", "content": item["prompt"]}],
                    "temperature": temperature,
                    "max_tokens": max_tokens,
                },
                timeout=60,
            )
            response.raise_for_status()
            data = response.json()
            generated = data["choices"][0]["message"]["content"]
        except Exception as e:
            generated = f"ERROR: {type(e).__name__}"

        results.append({
            "id": item["id"],
            "prompt": item["prompt"],
            "ideal": item["ideal"],
            "generated": generated,
            "tags": item.get("tags", []),
            "difficulty": item.get("difficulty", "medium"),
            "score_status": "not_scored",
            "manual_review_required": True,
        })

    categories = {}
    for item in items:
        cat = item.get("tags", ["unknown"])[0]
        categories[cat] = categories.get(cat, 0) + 1

    return {
        "eval_id": f"kimari-eval-{model_label}",
        "model_label": model_label,
        "mode": "endpoint",
        "endpoint": endpoint,
        "dataset_dir": str(dataset_dir),
        "total_items": len(items),
        "categories": categories,
        "results": results,
        "score_status": "not_scored",
        "manual_review_required": True,
        "no_benchmark_claim": True,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "notes": "Evaluation completed. Scores not computed (requires judge model or manual review). No benchmark claims.",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Run Kimari evaluation")
    parser.add_argument("--model-label", required=True, help="Model label for identification")
    parser.add_argument("--dataset-dir", default=str(DATASET_DIR), help="Dataset directory")
    parser.add_argument("--endpoint", help="OpenAI-compatible endpoint URL")
    parser.add_argument("--output-json", help="Output JSON file path")
    parser.add_argument("--output-md", help="Output Markdown file path")
    parser.add_argument("--dry-run", action="store_true", help="Dry run (no model calls)")
    parser.add_argument("--json", action="store_true", help="JSON output")
    args = parser.parse_args()

    if args.dry_run or not args.endpoint:
        result = run_dry_run(args.model_label, args.dataset_dir)
    else:
        result = run_evaluation(args.model_label, args.dataset_dir, args.endpoint)

    if args.output_json:
        output_path = Path(args.output_json)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(result, indent=2, ensure_ascii=False))
        print(f"Results written to {output_path}")

    if args.output_md:
        md_path = Path(args.output_md)
        md_path.parent.mkdir(parents=True, exist_ok=True)
        md_lines = [
            f"# KimariEval Results: {result['model_label']}",
            "",
            f"- **Mode**: {result['mode']}",
            f"- **Total items**: {result['total_items']}",
            f"- **Score status**: {result['score_status']}",
            f"- **Manual review required**: {result['manual_review_required']}",
            f"- **No benchmark claim**: {result['no_benchmark_claim']}",
            f"- **Categories**: {result['categories']}",
            f"- **Created**: {result['created_at']}",
        ]
        md_path.write_text("\n".join(md_lines))
        print(f"Markdown written to {md_path}")

    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        for k, v in result.items():
            if k != "results":
                print(f"  {k}: {v}")

    sys.exit(0)


if __name__ == "__main__":
    main()
