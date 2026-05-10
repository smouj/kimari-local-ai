#!/usr/bin/env python3
"""KimariFit — Evaluation harness for Kimari-4B.

In dry-run mode: validates prompts JSONL, groups by categories,
shows evaluation plan, no network calls.

With --score-plan: also outputs scoring plan with dimensions from
eval/scoring/kimarifit_dimensions.json.

With --endpoint: calls OpenAI-compatible chat completions API.
No model downloads. Does not run in CI.

Usage:
    python eval/kimarifit.py --prompts eval/kimarifit_prompts.jsonl --dry-run
    python eval/kimarifit.py --prompts eval/kimarifit_prompts.jsonl --dry-run --score-plan
    python eval/kimarifit.py --prompts eval/kimarifit_prompts.jsonl --endpoint http://localhost:8080/v1
"""

from __future__ import annotations

import argparse
import json
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

DIMENSIONS_PATH = Path(__file__).resolve().parent / "scoring" / "kimarifit_dimensions.json"


def load_prompts(path: Path) -> list[dict]:
    """Load prompts from JSONL file."""
    prompts = []
    with open(path) as f:
        for line_num, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError as exc:
                print(f"  ERROR: line {line_num}: invalid JSON — {exc}", file=sys.stderr)
                continue
            if "id" not in record or "prompt" not in record or "category" not in record:
                print(f"  ERROR: line {line_num}: missing required fields (id, prompt, category)", file=sys.stderr)
                continue
            prompts.append(record)
    return prompts


def group_by_category(prompts: list[dict]) -> dict[str, list[dict]]:
    """Group prompts by category."""
    categories: dict[str, list[dict]] = {}
    for p in prompts:
        cat = p["category"]
        categories.setdefault(cat, []).append(p)
    return categories


def load_scoring_dimensions() -> list[dict]:
    """Load scoring dimensions from eval/scoring/kimarifit_dimensions.json.

    Returns list of dimension dicts with id, max_score, description.
    Falls back to empty list if file not found.
    """
    if not DIMENSIONS_PATH.exists():
        return []
    try:
        with open(DIMENSIONS_PATH) as f:
            data = json.load(f)
        return [
            {
                "name": d.get("id", d.get("name", "unknown")),
                "max_score": d.get("max_score", 5),
                "description": d.get("description", ""),
            }
            for d in data.get("dimensions", [])
        ]
    except (json.JSONDecodeError, OSError):
        return []


def call_chat_completion(
    endpoint: str,
    prompt: str,
    model: str = "local-model",
    timeout: int = 60,
    temperature: float = 0.7,
    max_tokens: int = 256,
) -> dict:
    """Call OpenAI-compatible chat completions API using urllib.

    Returns a dict with 'response' or 'error'.
    """
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": temperature,
        "max_tokens": max_tokens,
    }
    url = f"{endpoint.rstrip('/')}/chat/completions"
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            body = json.loads(resp.read().decode("utf-8"))
            content = body.get("choices", [{}])[0].get("message", {}).get("content", "")
            return {"response": content, "status": "ok"}
    except urllib.error.URLError as exc:
        return {"error": f"URL error: {exc}", "status": "error"}
    except TimeoutError:
        return {"error": f"Request timed out after {timeout}s", "status": "timeout"}
    except Exception as exc:
        return {"error": f"Unexpected error: {exc}", "status": "error"}


def main() -> None:
    """CLI entry point for KimariFit evaluation harness."""
    parser = argparse.ArgumentParser(
        description="KimariFit evaluation harness. "
        "In dry-run: validates prompts and shows plan. "
        "With --endpoint: calls OpenAI-compatible API. "
        "No model downloads. Does not run in CI.",
    )
    parser.add_argument("--prompts", type=Path, required=True, help="Path to prompts JSONL file")
    parser.add_argument(
        "--dry-run", action="store_true", help="Validate prompts and show plan without making API calls"
    )
    parser.add_argument(
        "--endpoint", type=str, default=None, help="OpenAI-compatible API endpoint URL (e.g. http://localhost:8080/v1)"
    )
    parser.add_argument("--json", action="store_true", dest="json_output", help="Output results as JSON")
    parser.add_argument("--output", type=Path, default=None, help="Path to save results JSON")
    parser.add_argument("--timeout", type=int, default=60, help="Request timeout in seconds (default: 60)")
    parser.add_argument(
        "--model", type=str, default="local-model", help="Model name for API calls (default: local-model)"
    )
    parser.add_argument("--max-tokens", type=int, default=256, help="Max tokens per response (default: 256)")
    parser.add_argument(
        "--score-plan", action="store_true", help="In dry-run, also output scoring plan with dimensions"
    )
    parser.add_argument("--rubric", type=Path, default=None, help="Path to rubric markdown file")

    args = parser.parse_args()

    # Load prompts
    if not args.prompts.exists():
        print(f"ERROR: Prompts file not found: {args.prompts}", file=sys.stderr)
        sys.exit(1)

    prompts = load_prompts(args.prompts)
    if not prompts:
        print("ERROR: No valid prompts loaded", file=sys.stderr)
        sys.exit(1)

    categories = group_by_category(prompts)

    # Dry-run mode
    if args.dry_run:
        plan = {
            "total_prompts": len(prompts),
            "categories": {cat: len(prompts_list) for cat, prompts_list in categories.items()},
            "category_count": len(categories),
            "mode": "dry-run",
            "endpoint": args.endpoint or "not specified",
        }

        if args.score_plan:
            # Load scoring dimensions
            dimensions = load_scoring_dimensions()
            max_total = sum(d["max_score"] for d in dimensions) if dimensions else 0

            # Build warnings
            warnings: list[str] = []
            if not args.endpoint:
                warnings.append("no evaluator endpoint specified")
            warnings.append("scoring requires manual review")

            plan["prompt_count"] = len(prompts)
            plan["category_counts"] = {cat: len(prompts_list) for cat, prompts_list in categories.items()}
            plan["scoring_dimensions"] = dimensions
            plan["max_total_score"] = max_total
            plan["warnings"] = warnings

        if args.json_output:
            print(json.dumps(plan, indent=2))
        else:
            print("KimariFit Dry-Run Evaluation Plan")
            print("=" * 40)
            print(f"Total prompts: {plan['total_prompts']}")
            print(f"Categories: {plan['category_count']}")
            print()
            for cat, count in sorted(plan["categories"].items()):
                print(f"  {cat}: {count} prompts")
            print()
            print(f"Endpoint: {plan['endpoint']}")

            if args.score_plan:
                dimensions = plan.get("scoring_dimensions", [])
                max_total = plan.get("max_total_score", 0)
                warnings = plan.get("warnings", [])
                print()
                print("Scoring Plan:")
                print(f"  Dimensions: {len(dimensions)}")
                print(f"  Max total score: {max_total}")
                for dim in dimensions:
                    print(f"    {dim['name']}: max {dim['max_score']} — {dim['description']}")
                if warnings:
                    print("  Warnings:")
                    for w in warnings:
                        print(f"    - {w}")

            print()
            print("Dry-run complete. No API calls were made.")

        if args.output:
            with open(args.output, "w") as f:
                json.dump(plan, f, indent=2)
            if not args.json_output:
                print(f"Plan saved to {args.output}")
        return

    # Live evaluation mode
    if not args.endpoint:
        print("ERROR: --endpoint is required for live evaluation (or use --dry-run)", file=sys.stderr)
        sys.exit(1)

    results = []
    errors = 0

    for i, prompt_record in enumerate(prompts):
        prompt_id = prompt_record["id"]
        prompt_text = prompt_record["prompt"]
        category = prompt_record["category"]

        if not args.json_output:
            print(f"  [{i + 1}/{len(prompts)}] {prompt_id} ({category})...", end=" ", flush=True)

        start = time.time()
        result = call_chat_completion(
            endpoint=args.endpoint,
            prompt=prompt_text,
            model=args.model,
            timeout=args.timeout,
            max_tokens=args.max_tokens,
        )
        elapsed = time.time() - start

        if result.get("status") == "ok":
            if not args.json_output:
                print(f"OK ({elapsed:.1f}s)")
        else:
            errors += 1
            if not args.json_output:
                print(f"ERROR ({result.get('error', 'unknown')})")

        results.append(
            {
                "id": prompt_id,
                "category": category,
                "prompt": prompt_text,
                "response": result.get("response", ""),
                "status": result.get("status", "error"),
                "error": result.get("error", ""),
                "elapsed_seconds": round(elapsed, 2),
                "score_status": "manual_review_required",
            }
        )

    # Summary
    summary = {
        "total": len(prompts),
        "ok": len(prompts) - errors,
        "errors": errors,
        "categories": {cat: len(prompts_list) for cat, prompts_list in categories.items()},
        "results": results,
    }

    if args.json_output:
        print(json.dumps(summary, indent=2))
    else:
        print(f"\n{'=' * 40}")
        print(f"Results: {summary['ok']}/{summary['total']} successful, {summary['errors']} errors")
        print("Score status: manual_review_required — no automatic scoring applied")

    if args.output:
        with open(args.output, "w") as f:
            json.dump(summary, f, indent=2)
        if not args.json_output:
            print(f"Results saved to {args.output}")


if __name__ == "__main__":
    main()
