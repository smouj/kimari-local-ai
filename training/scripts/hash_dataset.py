#!/usr/bin/env python3
"""Compute dataset hashes for Kimari SFT datasets.

Usage:
    python training/scripts/hash_dataset.py --path dataset/build/kimari-fit-v0/sft_micro.jsonl --json
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def compute_hashes(filepath: str) -> dict:
    """Compute file and normalized SHA256 hashes for a dataset file."""
    p = Path(filepath)
    if not p.exists():
        return {"error": f"File not found: {filepath}"}

    raw = p.read_bytes()
    file_sha256 = hashlib.sha256(raw).hexdigest()

    # Normalized: re-parse each line, sort keys, re-serialize
    lines = raw.decode("utf-8").strip().split("\n")
    normalized_lines = []
    for line in lines:
        obj = json.loads(line)
        normalized_lines.append(json.dumps(obj, sort_keys=True, ensure_ascii=False))

    normalized_content = "\n".join(normalized_lines) + "\n"
    normalized_sha256 = hashlib.sha256(normalized_content.encode("utf-8")).hexdigest()

    record_count = len(lines)
    byte_size = len(raw)

    return {
        "path": str(filepath),
        "file_sha256": file_sha256,
        "normalized_sha256": normalized_sha256,
        "record_count": record_count,
        "byte_size": byte_size,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Compute dataset hashes")
    parser.add_argument("--path", required=True, help="Path to dataset JSONL file")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args()

    result = compute_hashes(args.path)
    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        for k, v in result.items():
            print(f"  {k}: {v}")


if __name__ == "__main__":
    main()
