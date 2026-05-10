#!/usr/bin/env python3
"""Kimari Evaluation Runner — Tests model against evaluation dataset.

Usage:
    python run_eval.py                    # Uses default API URL
    python run_eval.py --url http://...   # Custom API endpoint
    python run_eval.py --output my.json   # Custom results file

Results are saved as a JSON file with per-entry scores and an overall summary.
"""

import json
import sys
import time
from pathlib import Path
from typing import Any

try:
    import requests
except ImportError:
    print("[ERROR] Install requests: pip install -r cli/requirements.txt")
    sys.exit(1)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
EVAL_FILE = Path(__file__).parent / "kimari_eval.jsonl"
RESULTS_FILE = Path(__file__).parent / "results.json"
API_URL = "http://127.0.0.1:11435/v1/chat/completions"
MODEL_NAME = "kimari"  # Default model name passed to the API
TIMEOUT_SECONDS = 120  # Max wait time per request
REQUEST_DELAY = 1.0  # Seconds between requests (rate-limit courtesy)


# ---------------------------------------------------------------------------
# Dataset loading
# ---------------------------------------------------------------------------
def load_eval_dataset(path: Path) -> list[dict[str, Any]]:
    """Load JSONL evaluation dataset.

    Each line must be a valid JSON object with keys:
        id, category, prompt, expected_keywords, min_length

    Returns a list of parsed dicts. Exits on missing/empty file.
    """
    if not path.exists():
        print(f"[ERROR] Evaluation dataset not found: {path}")
        sys.exit(1)

    entries: list[dict[str, Any]] = []
    with open(path, encoding="utf-8") as f:
        for line_num, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                entry = json.loads(line)
                entries.append(entry)
            except json.JSONDecodeError as exc:
                print(f"[ERROR] Invalid JSON on line {line_num}: {exc}")
                sys.exit(1)

    if not entries:
        print(f"[ERROR] Evaluation dataset is empty: {path}")
        sys.exit(1)

    print(f"[INFO] Loaded {len(entries)} evaluation entries from {path}")
    return entries


# ---------------------------------------------------------------------------
# API interaction
# ---------------------------------------------------------------------------
def query_model(prompt: str, api_url: str, model: str = MODEL_NAME) -> str:
    """Send a chat completion request and return the assistant's response text.

    Raises SystemExit on network/HTTP errors.
    """
    payload = {
        "model": model,
        "messages": [
            {
                "role": "system",
                "content": "You are Kimari, a focused technical assistant for local LLM setup, GPU benchmarking, and developer tooling. Be concise and accurate.",
            },
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.2,  # Low temperature for deterministic evaluation
        "max_tokens": 1024,
    }

    try:
        resp = requests.post(
            api_url,
            json=payload,
            timeout=TIMEOUT_SECONDS,
            headers={"Content-Type": "application/json"},
        )
    except requests.ConnectionError:
        print(f"[ERROR] Cannot connect to API at {api_url}")
        print("       Make sure the Kimari server is running: kimari start")
        sys.exit(1)
    except requests.Timeout:
        print(f"[ERROR] Request timed out after {TIMEOUT_SECONDS}s")
        sys.exit(1)

    if resp.status_code != 200:
        print(f"[ERROR] API returned HTTP {resp.status_code}: {resp.text[:200]}")
        sys.exit(1)

    data = resp.json()
    try:
        return data["choices"][0]["message"]["content"]
    except (KeyError, IndexError):
        print(f"[ERROR] Unexpected API response format: {json.dumps(data)[:200]}")
        sys.exit(1)


# ---------------------------------------------------------------------------
# Scoring
# ---------------------------------------------------------------------------
def score_response(response_text: str, entry: dict[str, Any]) -> dict[str, Any]:
    """Score a response based on expected keywords and minimum length.

    Returns a dict with:
        keyword_hits    - list of matched keywords
        keyword_misses  - list of unmatched keywords
        keyword_score   - fraction of expected keywords found (0.0 – 1.0)
        length_ok       - bool, True if response meets min_length
        passed          - bool, True if all checks pass
    """
    expected_keywords = entry.get("expected_keywords", [])
    min_length = entry.get("min_length", 0)
    response_lower = response_text.lower()

    # Keyword matching (case-insensitive)
    keyword_hits: list[str] = []
    keyword_misses: list[str] = []

    for kw in expected_keywords:
        if kw.lower() in response_lower:
            keyword_hits.append(kw)
        else:
            keyword_misses.append(kw)

    keyword_score = len(keyword_hits) / max(len(expected_keywords), 1)
    length_ok = len(response_text.strip()) >= min_length
    passed = length_ok and keyword_score >= 0.6  # At least 60% of keywords required

    return {
        "keyword_hits": keyword_hits,
        "keyword_misses": keyword_misses,
        "keyword_score": round(keyword_score, 4),
        "length_ok": length_ok,
        "response_length": len(response_text.strip()),
        "min_length": min_length,
        "passed": passed,
    }


# ---------------------------------------------------------------------------
# Single evaluation
# ---------------------------------------------------------------------------
def evaluate_single(entry: dict[str, Any], api_url: str) -> dict[str, Any]:
    """Send a single evaluation prompt and score the response.

    Returns a result dict containing the entry metadata, the raw response,
    and the scoring breakdown.
    """
    entry_id = entry.get("id", "?")
    category = entry.get("category", "unknown")
    prompt = entry.get("prompt", "")

    print(f"\n{'─' * 60}")
    print(f"[#{entry_id}] Category: {category}")
    print(f"  Prompt: {prompt[:80]}{'...' if len(prompt) > 80 else ''}")

    start = time.time()
    response = query_model(prompt, api_url)
    elapsed = time.time() - start

    score = score_response(response, entry)

    status = "✅ PASS" if score["passed"] else "❌ FAIL"
    print(
        f"  {status} | Keywords: {len(score['keyword_hits'])}/{len(entry.get('expected_keywords', []))}"
        f" | Length: {score['response_length']}/{score['min_length']}"
        f" | Time: {elapsed:.2f}s"
    )

    if score["keyword_misses"]:
        print(f"  Missing keywords: {', '.join(score['keyword_misses'])}")

    return {
        "id": entry_id,
        "category": category,
        "prompt": prompt,
        "response": response,
        "score": score,
        "elapsed_seconds": round(elapsed, 3),
    }


# ---------------------------------------------------------------------------
# Full evaluation run
# ---------------------------------------------------------------------------
def run_evaluation(api_url: str, output_file: Path) -> list[dict[str, Any]]:
    """Run full evaluation and save results to a JSON file.

    Returns the list of per-entry results.
    """
    entries = load_eval_dataset(EVAL_FILE)
    results: list[dict[str, Any]] = []

    print(f"\n{'=' * 60}")
    print("KIMARI EVALUATION RUNNER")
    print(f"API URL : {api_url}")
    print(f"Dataset : {EVAL_FILE} ({len(entries)} entries)")
    print(f"Output  : {output_file}")
    print(f"{'=' * 60}")

    for i, entry in enumerate(entries):
        result = evaluate_single(entry, api_url)
        results.append(result)

        # Rate-limit between requests
        if i < len(entries) - 1:
            time.sleep(REQUEST_DELAY)

    # Save results
    output_file.parent.mkdir(parents=True, exist_ok=True)
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print(f"\n{'=' * 60}")
    print(f"Results saved to: {output_file}")
    print_report(results)

    return results


# ---------------------------------------------------------------------------
# Reporting
# ---------------------------------------------------------------------------
def print_report(results: list[dict[str, Any]]) -> None:
    """Print a human-readable evaluation report with per-category breakdown."""
    if not results:
        print("[WARN] No results to report.")
        return

    total = len(results)
    passed = sum(1 for r in results if r["score"]["passed"])
    failed = total - passed
    pass_rate = passed / total * 100
    total_time = sum(r["elapsed_seconds"] for r in results)
    avg_kw_score = sum(r["score"]["keyword_score"] for r in results) / total

    print(f"\n{'═' * 60}")
    print("  EVALUATION SUMMARY")
    print(f"{'═' * 60}")
    print(f"  Total entries  : {total}")
    print(f"  Passed         : {passed}")
    print(f"  Failed         : {failed}")
    print(f"  Pass rate      : {pass_rate:.1f}%")
    print(f"  Avg keyword    : {avg_kw_score:.1%}")
    print(f"  Total time     : {total_time:.2f}s")
    print(f"  Avg per entry  : {total_time / total:.2f}s")

    # Per-category breakdown
    categories: dict[str, dict[str, int | float]] = {}
    for r in results:
        cat = r["category"]
        if cat not in categories:
            categories[cat] = {"total": 0, "passed": 0, "time": 0.0}
        categories[cat]["total"] += 1  # type: ignore[index]
        if r["score"]["passed"]:
            categories[cat]["passed"] += 1  # type: ignore[index]
        categories[cat]["time"] += r["elapsed_seconds"]  # type: ignore[index]

    print(f"\n  {'Category':<25} {'Total':>5} {'Pass':>5} {'Rate':>7} {'Avg Time':>9}")
    print(f"  {'─' * 25} {'─' * 5} {'─' * 5} {'─' * 7} {'─' * 9}")
    for cat, stats in sorted(categories.items()):
        rate = stats["passed"] / max(stats["total"], 1) * 100  # type: ignore[operator]
        avg_t = stats["time"] / max(stats["total"], 1)  # type: ignore[operator]
        print(f"  {cat:<25} {stats['total']:>5} {stats['passed']:>5} {rate:>6.1f}% {avg_t:>8.2f}s")

    print(f"{'═' * 60}\n")

    # Detailed failures
    failures = [r for r in results if not r["score"]["passed"]]
    if failures:
        print("  FAILED ENTRIES:")
        for r in failures:
            print(f"    #{r['id']} [{r['category']}] — missing: {', '.join(r['score']['keyword_misses'])}")
        print()


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Kimari Evaluation Runner — Tests model against evaluation dataset.")
    parser.add_argument(
        "--url",
        default=API_URL,
        help=f"API endpoint URL (default: {API_URL})",
    )
    parser.add_argument(
        "--output",
        default=str(RESULTS_FILE),
        help=f"Path to save results JSON (default: {RESULTS_FILE})",
    )
    parser.add_argument(
        "--model",
        default=MODEL_NAME,
        help=f"Model name to send to the API (default: {MODEL_NAME})",
    )

    args = parser.parse_args()

    # Override global model name if provided
    if args.model != MODEL_NAME:
        MODEL_NAME = args.model  # type: ignore[misc]

    run_evaluation(args.url, Path(args.output))
