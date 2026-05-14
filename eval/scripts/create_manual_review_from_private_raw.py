#!/usr/bin/env python3
"""Create a sanitized manual-review summary from private Kimari raw outputs.

The raw file must live outside the public repository. This script never writes
prompts, ideals, generated text, tokens, or response bodies. It only emits
aggregate metadata and optional sanitized per-item decisions.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[2]

ALLOWED_WINNERS = {"base", "adapter", "tie"}
ALLOWED_REJECTION_REASONS = {
    "none",
    "style_only",
    "factual_error",
    "safety_issue",
    "coding_bug",
    "format_violation",
    "hallucination",
    "weaker_than_base",
    "unclear",
}
ALLOWED_DECISIONS = {
    "continue_to_subset60",
    "continue_to_full104",
    "dataset_fix_required",
    "safety_fix_required",
    "training_config_fix_required",
    "inconclusive",
    "blocked_missing_raw_outputs",
}

BASE_SUMMARY: dict[str, Any] = {
    "review_id": "kimari-runtime-15b-500step-subset30-manual-review-v0175",
    "scoring_job_id": "6a052f5ce48bea4538b9c37d",
    "training_job_id": "6a052ce6e48bea4538b9c365",
    "subset_size": 30,
    "base_score": 0.3158,
    "adapter_100_score": 0.3286,
    "adapter_500_score": 0.3404,
    "adapter_500_delta_vs_base": 0.0246,
    "base_wins": 12,
    "adapter_500_wins": 17,
    "ties": 1,
    "reviewed_items": 0,
    "accepted_adapter_wins": 0,
    "rejected_adapter_wins": 0,
    "accepted_base_wins": 0,
    "safety_regressions": 0,
    "factual_regressions": 0,
    "coding_regressions": 0,
    "spanish_quality_regressions": 0,
    "json_tooling_regressions": 0,
    "categories_improved": [],
    "categories_regressed": [],
    "manual_review_required": True,
    "public_benchmark_allowed": False,
    "raw_outputs_committed": False,
    "gate_state": "BLOCKED",
}


def is_inside(path: Path, parent: Path) -> bool:
    try:
        path.resolve().relative_to(parent.resolve())
        return True
    except ValueError:
        return False


def load_json(path: Path) -> Any:
    return json.loads(path.read_text())


def proxy_winner(base_row: dict[str, Any], adapter_row: dict[str, Any]) -> str:
    base_score = float(base_row.get("score", {}).get("proxy_score", 0.0))
    adapter_score = float(adapter_row.get("score", {}).get("proxy_score", 0.0))
    if adapter_score > base_score:
        return "adapter"
    if base_score > adapter_score:
        return "base"
    return "tie"


def category_from_row(row: dict[str, Any]) -> str:
    tags = row.get("tags") or []
    if isinstance(tags, list) and tags:
        return str(tags[0])
    return "uncategorized"


def sanitized_items(raw: dict[str, Any]) -> list[dict[str, Any]]:
    baseline_rows = raw.get("baseline_rows") or []
    adapter_rows = raw.get("adapter_rows") or []
    items: list[dict[str, Any]] = []
    for base_row, adapter_row in zip(baseline_rows, adapter_rows, strict=False):
        row_id = str(adapter_row.get("id") or base_row.get("id") or "unknown")
        category = category_from_row(adapter_row or base_row)
        winner = proxy_winner(base_row, adapter_row)
        items.append(
            {
                "item_id": row_id,
                "category": category,
                "winner": winner,
                "base_proxy_score": base_row.get("score", {}).get("proxy_score"),
                "adapter_proxy_score": adapter_row.get("score", {}).get("proxy_score"),
                "accepted": None,
                "rejection_reason": "unclear",
                "safety_issue": False,
                "factual_issue": False,
                "coding_issue": False,
                "spanish_quality_issue": False,
                "json_tooling_issue": False,
                "notes_sanitized": "pending private manual review; no raw text included",
            }
        )
    return items


def validate_review_item(item: dict[str, Any]) -> None:
    if item.get("winner") not in ALLOWED_WINNERS:
        raise ValueError(f"invalid winner for {item.get('item_id')}: {item.get('winner')}")
    reason = item.get("rejection_reason", "none")
    if reason not in ALLOWED_REJECTION_REASONS:
        raise ValueError(f"invalid rejection_reason for {item.get('item_id')}: {reason}")
    notes = str(item.get("notes_sanitized", ""))
    if len(notes) > 240:
        raise ValueError(f"notes_sanitized too long for {item.get('item_id')}")
    forbidden = ("prompt", "response", "generated", "ideal", "hf_", "api_key", "token")
    lowered = notes.lower()
    if any(word in lowered for word in forbidden):
        raise ValueError(f"notes_sanitized may contain raw/sensitive wording for {item.get('item_id')}")


def aggregate_decisions(review_items: list[dict[str, Any]]) -> dict[str, Any]:
    reviewed = [item for item in review_items if item.get("accepted") is not None]
    for item in reviewed:
        validate_review_item(item)

    accepted_adapter = 0
    rejected_adapter = 0
    accepted_base = 0
    ties = 0
    regressions_by_category: Counter[str] = Counter()
    improvements_by_category: Counter[str] = Counter()

    for item in reviewed:
        winner = item["winner"]
        accepted = item.get("accepted") is True
        category = str(item.get("category") or "uncategorized")
        if winner == "adapter":
            if accepted:
                accepted_adapter += 1
                improvements_by_category[category] += 1
            else:
                rejected_adapter += 1
                regressions_by_category[category] += 1
        elif winner == "base" and accepted:
            accepted_base += 1
            regressions_by_category[category] += 1
        elif winner == "tie":
            ties += 1

    safety = sum(1 for item in reviewed if item.get("safety_issue"))
    factual = sum(1 for item in reviewed if item.get("factual_issue"))
    coding = sum(1 for item in reviewed if item.get("coding_issue"))
    spanish = sum(1 for item in reviewed if item.get("spanish_quality_issue"))
    json_tooling = sum(1 for item in reviewed if item.get("json_tooling_issue"))

    return {
        "reviewed_items": len(reviewed),
        "accepted_adapter_wins": accepted_adapter,
        "rejected_adapter_wins": rejected_adapter,
        "accepted_base_wins": accepted_base,
        "ties": ties if reviewed else BASE_SUMMARY["ties"],
        "safety_regressions": safety,
        "factual_regressions": factual,
        "coding_regressions": coding,
        "spanish_quality_regressions": spanish,
        "json_tooling_regressions": json_tooling,
        "categories_improved": sorted([cat for cat, count in improvements_by_category.items() if count > 0]),
        "categories_regressed": sorted([cat for cat, count in regressions_by_category.items() if count > 0]),
    }


def infer_decision(summary: dict[str, Any], requested: str | None) -> str:
    if requested:
        if requested not in ALLOWED_DECISIONS:
            raise ValueError(f"decision must be one of {sorted(ALLOWED_DECISIONS)}")
        return requested
    if summary["reviewed_items"] < summary["subset_size"]:
        return "inconclusive"
    if summary["safety_regressions"] > 0:
        return "safety_fix_required"
    if summary["factual_regressions"] or summary["coding_regressions"]:
        return "dataset_fix_required"
    if summary["accepted_adapter_wins"] >= 12:
        return "continue_to_subset60"
    return "inconclusive"


def write_summary(args: argparse.Namespace) -> dict[str, Any]:
    raw_path = args.raw_private_path.expanduser().resolve()
    output_summary = args.output_summary.resolve()

    if is_inside(raw_path, PROJECT_ROOT):
        raise SystemExit("raw private path must be outside the public repository")
    if is_inside(output_summary, raw_path.parent):
        raise SystemExit("output summary must not be written into the private raw directory")

    summary = dict(BASE_SUMMARY)
    summary.update(
        {
            "manual_review_status": "blocked_missing_raw_outputs",
            "review_status": "blocked_missing_raw_outputs",
            "raw_output_location_status": "not_found_at_private_path",
            "decision": "blocked_missing_raw_outputs",
            "private_review_dir": "outside_public_repo",
            "notes": [
                "No raw prompts, ideals, generated text, tokens, or private bodies are included.",
                "Raw outputs were not available at the provided private path.",
                "Gate remains BLOCKED; no public benchmark, weights, or GGUF are allowed.",
            ],
        }
    )

    if raw_path.exists():
        raw = load_json(raw_path)
        review_items = sanitized_items(raw)
        decisions_path = args.review_decisions.expanduser().resolve() if args.review_decisions else None
        if decisions_path and decisions_path.exists():
            decisions = load_json(decisions_path)
            if not isinstance(decisions, list):
                raise SystemExit("review decisions must be a JSON list")
            by_id = {str(item.get("item_id")): item for item in decisions}
            for item in review_items:
                if item["item_id"] in by_id:
                    item.update(by_id[item["item_id"]])
        aggregate = aggregate_decisions(review_items)
        summary.update(aggregate)
        completed = summary["reviewed_items"] == summary["subset_size"]
        summary.update(
            {
                "manual_review_status": "completed" if completed else "pending_manual_classification",
                "review_status": "completed" if completed else "pending_manual_classification",
                "raw_output_location_status": "available_outside_public_repo",
                "decision": infer_decision(summary, args.decision),
                "notes": [
                    "Private raw outputs were read from outside the public repository.",
                    "This summary contains only sanitized aggregate metadata and no raw text.",
                    "Gate remains BLOCKED; no public benchmark, weights, or GGUF are allowed.",
                ],
            }
        )
        if not args.no_raw_output:
            summary["sanitized_review_items"] = review_items

    output_summary.parent.mkdir(parents=True, exist_ok=True)
    output_summary.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n")
    return summary


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--raw-private-path", required=True, type=Path)
    parser.add_argument("--output-summary", required=True, type=Path)
    parser.add_argument("--review-decisions", type=Path)
    parser.add_argument("--decision", choices=sorted(ALLOWED_DECISIONS))
    parser.add_argument("--json", action="store_true")
    parser.add_argument(
        "--redact", action="store_true", help="Accepted for explicit safety; raw text is never emitted."
    )
    parser.add_argument(
        "--no-raw-output", action="store_true", help="Do not include sanitized per-item rows in output."
    )
    args = parser.parse_args()

    summary = write_summary(args)
    payload = {
        "ok": True,
        "manual_review_status": summary.get("manual_review_status"),
        "reviewed_items": summary.get("reviewed_items"),
        "decision": summary.get("decision"),
        "output_summary": str(args.output_summary),
        "raw_outputs_committed": summary.get("raw_outputs_committed"),
        "gate_state": summary.get("gate_state"),
    }
    if args.json:
        print(json.dumps(payload, indent=2))
    else:
        print(payload)
    return 0


if __name__ == "__main__":
    sys.exit(main())
