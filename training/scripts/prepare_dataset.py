#!/usr/bin/env python3
"""Prepare and validate JSONL datasets for Kimari training.

Reads a raw JSONL file, validates records against the specified schema
(sft or preference), filters invalid entries, and writes a clean JSONL
output file. Reports statistics on records read, valid, invalid, and written.

Supports deduplication, character-length filtering, tag filtering,
and JSON report output.

No network calls. No downloads. All data must be local.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path


def validate_sft_record(record: dict) -> str | None:
    """Validate a single SFT record. Returns error message or None if valid."""
    messages = record.get("messages")
    if not messages:
        return "missing or empty 'messages' field"
    if not isinstance(messages, list):
        return "'messages' must be a list"
    if len(messages) == 0:
        return "'messages' list is empty"

    for idx, msg in enumerate(messages):
        if not isinstance(msg, dict):
            return f"message[{idx}] is not a dict"
        role = msg.get("role")
        content = msg.get("content")
        if not role or not isinstance(role, str):
            return f"message[{idx}] missing or invalid 'role'"
        if content is None or not isinstance(content, str):
            return f"message[{idx}] missing or invalid 'content'"
        if content.strip() == "":
            return f"message[{idx}] has empty 'content'"

    if "license" not in record:
        return "missing 'license' field"
    if "source" not in record:
        return "missing 'source' field"

    return None


def validate_preference_record(record: dict) -> str | None:
    """Validate a single preference record. Returns error message or None."""
    for field in ("prompt", "chosen", "rejected"):
        value = record.get(field)
        if value is None:
            return f"missing '{field}' field"
        if not isinstance(value, str):
            return f"'{field}' must be a string"
        if value.strip() == "":
            return f"'{field}' is empty"

    if "license" not in record:
        return "missing 'license' field"
    if "source" not in record:
        return "missing 'source' field"

    return None


def content_hash(record: dict, schema: str) -> str:
    """Compute SHA-256 hash of content fields for deduplication."""
    h = hashlib.sha256()
    if schema == "sft":
        for msg in record.get("messages", []):
            h.update(msg.get("role", "").encode())
            h.update(msg.get("content", "").encode())
    else:
        h.update(record.get("prompt", "").encode())
        h.update(record.get("chosen", "").encode())
        h.update(record.get("rejected", "").encode())
    return h.hexdigest()


def total_content_length(record: dict, schema: str) -> int:
    """Compute total character length of content fields."""
    total = 0
    if schema == "sft":
        for msg in record.get("messages", []):
            total += len(msg.get("content", ""))
    else:
        total += len(record.get("prompt", ""))
        total += len(record.get("chosen", ""))
        total += len(record.get("rejected", ""))
    return total


def prepare_dataset(
    input_path: str,
    output_path: str,
    schema: str,
    dedupe: bool = False,
    min_chars: int | None = None,
    max_chars: int | None = None,
    require_tags: list[str] | None = None,
    report_path: str | None = None,
) -> dict[str, int | dict[str, int]]:
    """Read, validate, filter, and write a JSONL dataset.

    Returns statistics dict with processing details.
    """
    validator = validate_sft_record if schema == "sft" else validate_preference_record

    stats: dict[str, int | dict[str, int]] = {
        "input_records": 0,
        "output_records": 0,
        "dropped_empty": 0,
        "dropped_missing_source": 0,
        "dropped_missing_license": 0,
        "dropped_too_short": 0,
        "dropped_too_long": 0,
        "duplicates_removed": 0,
        "tag_counts": {},
    }

    input_file = Path(input_path)
    output_file = Path(output_path)

    if not input_file.exists():
        print(f"ERROR: Input file not found: {input_path}", file=sys.stderr)
        sys.exit(1)

    output_file.parent.mkdir(parents=True, exist_ok=True)

    seen_hashes: set[str] = set()
    valid_records: list[dict] = []

    with input_file.open("r", encoding="utf-8") as fin:
        for line_num, line in enumerate(fin, start=1):
            line = line.strip()
            if not line:
                continue

            stats["input_records"] += 1

            try:
                record = json.loads(line)
            except json.JSONDecodeError as exc:
                print(f"  Line {line_num}: invalid JSON — {exc}", file=sys.stderr)
                continue

            if not isinstance(record, dict):
                print(f"  Line {line_num}: record is not a JSON object", file=sys.stderr)
                continue

            # Validate
            error = validator(record)
            if error:
                print(f"  Line {line_num}: {error}", file=sys.stderr)
                if "missing 'source'" in error:
                    stats["dropped_missing_source"] += 1
                elif "missing 'license'" in error:
                    stats["dropped_missing_license"] += 1
                else:
                    stats["dropped_empty"] += 1
                continue

            # Tag filtering
            if require_tags:
                record_tags = set(record.get("tags", []))
                if not record_tags.intersection(require_tags):
                    continue

            # Track tag counts
            for tag in record.get("tags", []):
                tag_counts = stats["tag_counts"]
                assert isinstance(tag_counts, dict)
                tag_counts[tag] = tag_counts.get(tag, 0) + 1

            # Character length filtering
            content_len = total_content_length(record, schema)
            if min_chars is not None and content_len < min_chars:
                stats["dropped_too_short"] += 1
                continue
            if max_chars is not None and content_len > max_chars:
                stats["dropped_too_long"] += 1
                continue

            # Deduplication
            if dedupe:
                h = content_hash(record, schema)
                if h in seen_hashes:
                    stats["duplicates_removed"] += 1
                    continue
                seen_hashes.add(h)

            valid_records.append(record)

    # Write output
    with output_file.open("w", encoding="utf-8") as fout:
        for record in valid_records:
            fout.write(json.dumps(record, ensure_ascii=False) + "\n")

    stats["output_records"] = len(valid_records)

    # Write report
    if report_path:
        report_file = Path(report_path)
        report_file.parent.mkdir(parents=True, exist_ok=True)
        with open(report_file, "w") as f:
            json.dump(stats, f, indent=2)
        print(f"Report written to {report_path}")

    return stats


def main() -> None:
    """CLI entry point for dataset preparation."""
    parser = argparse.ArgumentParser(
        description="Prepare and validate JSONL datasets for Kimari training. "
        "No network calls. No downloads. All data must be local.",
    )
    parser.add_argument(
        "--input",
        required=True,
        help="Path to input raw JSONL file",
    )
    parser.add_argument(
        "--output",
        required=True,
        help="Path to output cleaned JSONL file",
    )
    parser.add_argument(
        "--schema",
        required=True,
        choices=["sft", "preference"],
        help="Dataset schema type: 'sft' or 'preference'",
    )
    parser.add_argument(
        "--dedupe",
        action="store_true",
        help="Remove duplicates based on SHA-256 content hash",
    )
    parser.add_argument(
        "--min-chars",
        type=int,
        default=None,
        help="Drop records with total content shorter than N characters",
    )
    parser.add_argument(
        "--max-chars",
        type=int,
        default=None,
        help="Drop records with total content longer than N characters",
    )
    parser.add_argument(
        "--require-tags",
        type=str,
        default=None,
        help="Comma-separated tags — only keep records with at least one matching tag",
    )
    parser.add_argument(
        "--report",
        type=str,
        default=None,
        help="Path to write JSON report with processing statistics",
    )

    args = parser.parse_args()

    # Parse require-tags
    require_tags = None
    if args.require_tags:
        require_tags = [t.strip() for t in args.require_tags.split(",") if t.strip()]

    print(f"Schema:    {args.schema}")
    print(f"Input:     {args.input}")
    print(f"Output:    {args.output}")
    if args.dedupe:
        print("Dedup:     enabled")
    if args.min_chars is not None:
        print(f"Min chars: {args.min_chars}")
    if args.max_chars is not None:
        print(f"Max chars: {args.max_chars}")
    if require_tags:
        print(f"Tags:      {require_tags}")
    print()

    stats = prepare_dataset(
        args.input,
        args.output,
        args.schema,
        dedupe=args.dedupe,
        min_chars=args.min_chars,
        max_chars=args.max_chars,
        require_tags=require_tags,
        report_path=args.report,
    )

    print()
    print("=== Dataset Preparation Summary ===")
    print(f"Records read:     {stats['input_records']}")
    print(f"Records written:  {stats['output_records']}")
    if stats["dropped_empty"]:
        print(f"Dropped (empty):  {stats['dropped_empty']}")
    if stats["dropped_missing_source"]:
        print(f"Dropped (source): {stats['dropped_missing_source']}")
    if stats["dropped_missing_license"]:
        print(f"Dropped (license):{stats['dropped_missing_license']}")
    if stats["dropped_too_short"]:
        print(f"Dropped (short):  {stats['dropped_too_short']}")
    if stats["dropped_too_long"]:
        print(f"Dropped (long):   {stats['dropped_too_long']}")
    if stats["duplicates_removed"]:
        print(f"Duplicates removed: {stats['duplicates_removed']}")

    if stats["input_records"] == 0:
        print("\nWARNING: No records read from input file.", file=sys.stderr)
        sys.exit(1)

    if stats["output_records"] == 0:
        print("\nERROR: No valid records written to output file.", file=sys.stderr)
        sys.exit(1)

    print("\nDone.")


if __name__ == "__main__":
    main()
