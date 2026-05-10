#!/usr/bin/env python3
"""Prepare and validate JSONL datasets for Kimari training.

Reads a raw JSONL file, validates records against the specified schema
(sft or preference), filters invalid entries, and writes a clean JSONL
output file. Reports statistics on records read, valid, invalid, and written.

No network calls. No downloads. All data must be local.
"""

from __future__ import annotations

import argparse
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


def prepare_dataset(
    input_path: str,
    output_path: str,
    schema: str,
) -> dict[str, int]:
    """Read, validate, filter, and write a JSONL dataset.

    Returns statistics dict with keys: read, valid, invalid, written.
    """
    validator = validate_sft_record if schema == "sft" else validate_preference_record

    stats = {"read": 0, "valid": 0, "invalid": 0, "written": 0}

    input_file = Path(input_path)
    output_file = Path(output_path)

    if not input_file.exists():
        print(f"ERROR: Input file not found: {input_path}", file=sys.stderr)
        sys.exit(1)

    output_file.parent.mkdir(parents=True, exist_ok=True)

    with (
        input_file.open("r", encoding="utf-8") as fin,
        output_file.open("w", encoding="utf-8") as fout,
    ):
        for line_num, line in enumerate(fin, start=1):
            line = line.strip()
            if not line:
                continue

            stats["read"] += 1

            try:
                record = json.loads(line)
            except json.JSONDecodeError as exc:
                stats["invalid"] += 1
                print(
                    f"  Line {line_num}: invalid JSON — {exc}",
                    file=sys.stderr,
                )
                continue

            if not isinstance(record, dict):
                stats["invalid"] += 1
                print(
                    f"  Line {line_num}: record is not a JSON object",
                    file=sys.stderr,
                )
                continue

            error = validator(record)
            if error:
                stats["invalid"] += 1
                print(
                    f"  Line {line_num}: {error}",
                    file=sys.stderr,
                )
                continue

            stats["valid"] += 1
            fout.write(json.dumps(record, ensure_ascii=False) + "\n")
            stats["written"] += 1

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

    args = parser.parse_args()

    print(f"Schema:    {args.schema}")
    print(f"Input:     {args.input}")
    print(f"Output:    {args.output}")
    print()

    stats = prepare_dataset(args.input, args.output, args.schema)

    print()
    print("=== Dataset Preparation Summary ===")
    print(f"Records read:     {stats['read']}")
    print(f"Records valid:    {stats['valid']}")
    print(f"Records invalid:  {stats['invalid']}")
    print(f"Records written:  {stats['written']}")

    if stats["read"] == 0:
        print("\nWARNING: No records read from input file.", file=sys.stderr)
        sys.exit(1)

    if stats["invalid"] > 0:
        print(
            f"\nWARNING: {stats['invalid']} invalid record(s) were skipped.",
            file=sys.stderr,
        )

    if stats["written"] == 0:
        print(
            "\nERROR: No valid records written to output file.",
            file=sys.stderr,
        )
        sys.exit(1)

    print("\nDone.")


if __name__ == "__main__":
    main()
