#!/usr/bin/env python3
"""Build dataset mix for Kimari training.

Validates SFT and preference datasets against their schemas,
cleans records, splits into train/eval, and writes training-ready
JSONL files with a report.

No network calls. No downloads. All data must be local.

Usage:
    python training/scripts/build_dataset_mix.py --sft PATH --preference PATH
        --output-dir DIR [--max-sft N] [--max-preference N] [--report]
        [--train-ratio 0.9] [--eval-ratio 0.1] [--shuffle] [--seed 42]
        [--holdout PATH]
"""

from __future__ import annotations

import argparse
import json
import random
import shutil
import sys
from pathlib import Path


def validate_sft_record(record: dict) -> str | None:
    """Validate a single SFT record. Returns error message or None."""
    messages = record.get("messages")
    if not messages or not isinstance(messages, list):
        return "missing or empty 'messages' field"
    if len(messages) < 2:
        return "'messages' must have at least 2 turns"
    for idx, msg in enumerate(messages):
        if not isinstance(msg, dict):
            return f"message[{idx}] is not a dict"
        role = msg.get("role")
        content = msg.get("content")
        if not role or not isinstance(role, str):
            return f"message[{idx}] missing or invalid 'role'"
        if content is None or not isinstance(content, str) or not content.strip():
            return f"message[{idx}] missing or empty 'content'"
    if "license" not in record:
        return "missing 'license' field"
    if "source" not in record:
        return "missing 'source' field"
    return None


def validate_preference_record(record: dict) -> str | None:
    """Validate a single preference record. Returns error message or None."""
    for field in ("prompt", "chosen", "rejected"):
        value = record.get(field)
        if value is None or not isinstance(value, str) or not value.strip():
            return f"missing or empty '{field}' field"
    if "license" not in record:
        return "missing 'license' field"
    if "source" not in record:
        return "missing 'source' field"
    return None


def load_and_validate(path: Path, validator: callable, max_records: int | None = None) -> tuple[list[dict], dict]:
    """Load JSONL, validate records, return (valid_records, stats)."""
    stats = {"input_records": 0, "valid_records": 0, "invalid_records": 0, "errors": []}
    valid = []

    if not path.exists():
        print(f"  WARNING: {path} not found, skipping", file=sys.stderr)
        return valid, stats

    with open(path) as f:
        for line_num, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue

            stats["input_records"] += 1

            try:
                record = json.loads(line)
            except json.JSONDecodeError as exc:
                stats["invalid_records"] += 1
                stats["errors"].append(f"line {line_num}: invalid JSON — {exc}")
                continue

            if not isinstance(record, dict):
                stats["invalid_records"] += 1
                stats["errors"].append(f"line {line_num}: not a JSON object")
                continue

            error = validator(record)
            if error:
                stats["invalid_records"] += 1
                stats["errors"].append(f"line {line_num}: {error}")
                continue

            stats["valid_records"] += 1
            valid.append(record)

    if max_records is not None and max_records > 0:
        valid = valid[:max_records]

    return valid, stats


def split_records(
    records: list[dict],
    train_ratio: float,
    eval_ratio: float,
    shuffle: bool,
    seed: int,
) -> tuple[list[dict], list[dict]]:
    """Split records into train and eval sets."""
    if shuffle:
        rng = random.Random(seed)
        rng.shuffle(records)

    total = len(records)
    train_count = int(total * train_ratio)
    train_records = records[:train_count]
    eval_records = records[train_count:]

    return train_records, eval_records


def write_jsonl(path: Path, records: list[dict]) -> int:
    """Write records to JSONL file. Returns count written."""
    with open(path, "w") as f:
        for record in records:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
    return len(records)


def main() -> None:
    """CLI entry point for building dataset mix."""
    parser = argparse.ArgumentParser(
        description="Build dataset mix for Kimari training. No network calls. No downloads. All data must be local.",
    )
    parser.add_argument("--sft", type=Path, required=True, help="Path to SFT JSONL dataset")
    parser.add_argument("--preference", type=Path, required=True, help="Path to preference JSONL dataset")
    parser.add_argument("--output-dir", type=Path, required=True, help="Directory for output files")
    parser.add_argument("--max-sft", type=int, default=None, help="Maximum SFT records to include")
    parser.add_argument("--max-preference", type=int, default=None, help="Maximum preference records to include")
    parser.add_argument("--report", action="store_true", help="Write report.json with statistics")
    parser.add_argument("--train-ratio", type=float, default=0.9, help="Ratio for train split (default: 0.9)")
    parser.add_argument("--eval-ratio", type=float, default=0.1, help="Ratio for eval split (default: 0.1)")
    parser.add_argument("--shuffle", action="store_true", help="Shuffle records before splitting")
    parser.add_argument("--seed", type=int, default=42, help="Random seed for reproducibility (default: 42)")
    parser.add_argument(
        "--holdout", type=Path, default=None, help="Path to eval holdout JSONL, copied to output as holdout.jsonl"
    )

    args = parser.parse_args()

    print("Kimari Dataset Mix Builder")
    print("=" * 40)

    # Load and validate SFT
    print("\nValidating SFT dataset...")
    sft_records, sft_stats = load_and_validate(args.sft, validate_sft_record, args.max_sft)
    print(
        f"  Input: {sft_stats['input_records']} | Valid: {sft_stats['valid_records']} | Invalid: {sft_stats['invalid_records']}"
    )
    if sft_stats["errors"]:
        for err in sft_stats["errors"][:10]:
            print(f"    {err}", file=sys.stderr)

    # Load and validate preference
    print("\nValidating preference dataset...")
    pref_records, pref_stats = load_and_validate(args.preference, validate_preference_record, args.max_preference)
    print(
        f"  Input: {pref_stats['input_records']} | Valid: {pref_stats['valid_records']} | Invalid: {pref_stats['invalid_records']}"
    )
    if pref_stats["errors"]:
        for err in pref_stats["errors"][:10]:
            print(f"    {err}", file=sys.stderr)

    # Split SFT into train/eval
    print("\nSplitting datasets...")
    print(
        f"  Train ratio: {args.train_ratio} | Eval ratio: {args.eval_ratio} | Shuffle: {args.shuffle} | Seed: {args.seed}"
    )
    sft_train, sft_eval = split_records(sft_records, args.train_ratio, args.eval_ratio, args.shuffle, args.seed)
    pref_train, pref_eval = split_records(pref_records, args.train_ratio, args.eval_ratio, args.shuffle, args.seed)
    print(f"  SFT: {len(sft_train)} train / {len(sft_eval)} eval")
    print(f"  Preference: {len(pref_train)} train / {len(pref_eval)} eval")

    # Write output
    args.output_dir.mkdir(parents=True, exist_ok=True)

    sft_train_out = args.output_dir / "sft.train.jsonl"
    sft_eval_out = args.output_dir / "sft.eval.jsonl"
    pref_train_out = args.output_dir / "preference.train.jsonl"
    pref_eval_out = args.output_dir / "preference.eval.jsonl"

    write_jsonl(sft_train_out, sft_train)
    write_jsonl(sft_eval_out, sft_eval)
    write_jsonl(pref_train_out, pref_train)
    write_jsonl(pref_eval_out, pref_eval)

    print(f"\nWrote {len(sft_train)} SFT train records to {sft_train_out}")
    print(f"Wrote {len(sft_eval)} SFT eval records to {sft_eval_out}")
    print(f"Wrote {len(pref_train)} preference train records to {pref_train_out}")
    print(f"Wrote {len(pref_eval)} preference eval records to {pref_eval_out}")

    # Handle holdout
    holdout_stats: dict | None = None
    if args.holdout:
        holdout_out = args.output_dir / "holdout.jsonl"
        if args.holdout.exists():
            shutil.copy2(args.holdout, holdout_out)
            # Count records in holdout
            with open(holdout_out) as f:
                holdout_count = sum(1 for line in f if line.strip())
            holdout_stats = {"input": str(args.holdout), "records": holdout_count}
            print(f"Copied holdout ({holdout_count} records) to {holdout_out}")
        else:
            print(f"  WARNING: Holdout file {args.holdout} not found, skipping", file=sys.stderr)

    # Always write report
    report = {
        "sft": {
            "input": str(args.sft),
            "valid": sft_stats["valid_records"],
            "train_count": len(sft_train),
            "eval_count": len(sft_eval),
        },
        "preference": {
            "input": str(args.preference),
            "valid": pref_stats["valid_records"],
            "train_count": len(pref_train),
            "eval_count": len(pref_eval),
        },
        "config": {
            "train_ratio": args.train_ratio,
            "eval_ratio": args.eval_ratio,
            "seed": args.seed,
            "shuffled": args.shuffle,
        },
    }
    if holdout_stats is not None:
        report["holdout"] = holdout_stats

    report_path = args.output_dir / "report.json"
    with open(report_path, "w") as f:
        json.dump(report, f, indent=2)
    print(f"Wrote report to {report_path}")

    print("\nDone.")


if __name__ == "__main__":
    main()
