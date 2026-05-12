#!/usr/bin/env python3
"""Validate a collection seed JSON file.

Checks:
- Valid JSON
- Each entry has required fields
- official_kimari_model is always false
- No Kimari-4B references
- License field present
- recommended_vram_gb is reasonable (1-16 GB)
- model_id looks like a HuggingFace repo ID

Usage:
    python scripts/huggingface/validate_collection_seed.py --input <seed.json> [--json]
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REQUIRED_FIELDS = [
    "model_id",
    "reason",
    "license",
    "official_kimari_model",
    "recommended_vram_gb",
    "kimari_profile",
]

ERRORS: list[str] = []
WARNINGS: list[str] = []


def validate_entry(idx: int, entry: dict) -> None:
    """Validate a single collection seed entry."""
    prefix = f"Entry {idx + 1}"

    # Check required fields
    for field in REQUIRED_FIELDS:
        if field not in entry:
            ERRORS.append(f"{prefix}: missing required field '{field}'")

    # official_kimari_model must be false
    if entry.get("official_kimari_model") is True:
        ERRORS.append(
            f"{prefix}: official_kimari_model must be false (got true for {entry.get('model_id', 'unknown')})"
        )

    # No Kimari-4B references
    model_id = entry.get("model_id", "").lower()
    reason = entry.get("reason", "").lower()
    notes = entry.get("notes", "").lower()
    for text in [model_id, reason, notes]:
        if "kimari-4b" in text:
            WARNINGS.append(f"{prefix}: references Kimari-4B (model: {entry.get('model_id', 'unknown')})")

    # License must be present and non-empty
    license_val = entry.get("license", "")
    if not license_val or license_val.strip() == "":
        ERRORS.append(f"{prefix}: license field is empty")

    # VRAM must be reasonable
    vram = entry.get("recommended_vram_gb", 0)
    if not isinstance(vram, (int, float)) or vram < 0.5 or vram > 64:
        ERRORS.append(f"{prefix}: recommended_vram_gb out of range ({vram})")

    # model_id should look like HF repo (owner/name)
    if "/" not in entry.get("model_id", ""):
        ERRORS.append(f"{prefix}: model_id should be 'owner/name' format")

    # notes field should exist
    if "notes" not in entry:
        WARNINGS.append(f"{prefix}: no 'notes' field")


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate collection seed JSON")
    parser.add_argument("--input", required=True, help="Path to seed JSON file")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args()

    seed_path = Path(args.input)
    if not seed_path.exists():
        if args.json:
            print(json.dumps({"valid": False, "error": f"File not found: {args.input}"}))
        else:
            print(f"FAIL: File not found: {args.input}")
        sys.exit(1)

    try:
        data = json.loads(seed_path.read_text())
    except json.JSONDecodeError as e:
        if args.json:
            print(json.dumps({"valid": False, "error": f"Invalid JSON: {e}"}))
        else:
            print(f"FAIL: Invalid JSON: {e}")
        sys.exit(1)

    if not isinstance(data, list):
        ERRORS.append("Seed file must be a JSON array of entries")

    if isinstance(data, list):
        if len(data) == 0:
            WARNINGS.append("Seed file is empty")
        for i, entry in enumerate(data):
            if not isinstance(entry, dict):
                ERRORS.append(f"Entry {i + 1}: must be a JSON object")
            else:
                validate_entry(i, entry)

    valid = len(ERRORS) == 0

    if args.json:
        print(
            json.dumps(
                {
                    "valid": valid,
                    "errors": ERRORS,
                    "warnings": WARNINGS,
                    "entries_checked": len(data) if isinstance(data, list) else 0,
                },
                indent=2,
            )
        )
    else:
        for e in ERRORS:
            print(f"  FAIL: {e}")
        for w in WARNINGS:
            print(f"  WARN: {w}")
        if valid:
            print(f"RESULT: All checks passed! ({len(WARNINGS)} warning(s))")
        else:
            print(f"RESULT: {len(ERRORS)} error(s), {len(WARNINGS)} warning(s)")

    sys.exit(0 if valid else 1)


if __name__ == "__main__":
    main()
