#!/usr/bin/env python3
"""Validate a screenshot manifest for Kimari Local AI.

Checks that manifest entries follow naming conventions, contain no secrets,
and are marked as public_safe before they can be committed.

Usage:
    python scripts/docs/validate_screenshot_manifest.py --manifest <path>
    python scripts/docs/validate_screenshot_manifest.py --manifest <path> --json
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

# Patterns that should never appear in public screenshots
_SECRET_PATTERNS = [
    "sk-",
    "hf_",
    "api_key",
    "apikey",
    "password",
    "bearer",
    "authorization",
]


def validate_manifest(manifest_path: Path) -> dict:
    """Validate a screenshot manifest JSON file.

    Returns a dict with:
        - valid: bool
        - errors: list[str]
        - warnings: list[str]
        - entry_count: int
        - entries_checked: int
    """
    result = {
        "valid": True,
        "errors": [],
        "warnings": [],
        "entry_count": 0,
        "entries_checked": 0,
    }

    if not manifest_path.exists():
        result["valid"] = False
        result["errors"].append(f"Manifest not found: {manifest_path}")
        return result

    try:
        data = json.loads(manifest_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        result["valid"] = False
        result["errors"].append(f"Invalid JSON: {e}")
        return result

    screenshots = data.get("screenshots", [])
    result["entry_count"] = len(screenshots)

    required_fields = ["filename", "command", "contains_secret", "contains_token", "public_safe"]

    for i, entry in enumerate(screenshots):
        result["entries_checked"] += 1
        entry_label = entry.get("filename", f"entry_{i}")

        # Check required fields
        for field in required_fields:
            if field not in entry:
                result["errors"].append(f"{entry_label}: missing required field '{field}'")
                result["valid"] = False

        # Check contains_secret is False
        if entry.get("contains_secret") is True:
            result["errors"].append(f"{entry_label}: contains_secret must be False")
            result["valid"] = False

        # Check contains_token is False
        if entry.get("contains_token") is True:
            result["errors"].append(f"{entry_label}: contains_token must be False")
            result["valid"] = False

        # Check public_safe is True
        if entry.get("public_safe") is False:
            result["warnings"].append(f"{entry_label}: public_safe is False — review before committing")

        # Check filename follows naming convention (lowercase, hyphens, .png/.webp)
        filename = entry.get("filename", "")
        if filename:
            ext = Path(filename).suffix.lower()
            if ext not in (".png", ".webp", ".jpg", ".jpeg"):
                result["warnings"].append(f"{entry_label}: unexpected extension '{ext}' (expected .png/.webp/.jpg)")

        # Check command doesn't contain secrets
        command = entry.get("command", "")
        for pattern in _SECRET_PATTERNS:
            if pattern in command.lower():
                result["errors"].append(f"{entry_label}: command contains secret pattern '{pattern}'")
                result["valid"] = False

        # Check notes don't claim Kimari-4B is released
        notes = entry.get("notes", "")
        if "kimari-4b" in notes.lower() and ("released" in notes.lower() or "available" in notes.lower()):
            result["errors"].append(f"{entry_label}: notes claim Kimari-4B is released")
            result["valid"] = False

    # Check meta section
    meta = data.get("meta", {})
    if meta.get("gate", "").upper() != "BLOCKED":
        result["warnings"].append("meta.gate should be BLOCKED")

    model = meta.get("model", "")
    if "kimari-4b" in model.lower() and "not" not in model.lower():
        result["errors"].append("meta.model claims Kimari-4B is released")
        result["valid"] = False

    return result


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Validate a screenshot manifest for Kimari Local AI. "
        "Checks naming conventions, no secrets, and public safety."
    )
    parser.add_argument(
        "--manifest",
        type=Path,
        required=True,
        help="Path to screenshot manifest JSON file",
    )
    parser.add_argument("--json", action="store_true", help="JSON output")
    args = parser.parse_args()

    result = validate_manifest(args.manifest)

    if args.json:
        print(json.dumps(result, indent=2))
        sys.exit(0 if result["valid"] else 1)

    # Human-readable output
    print(f"\nScreenshot Manifest Validation: {args.manifest}")
    print(f"  Entries: {result['entries_checked']}/{result['entry_count']}")

    if result["errors"]:
        print(f"\n  ERRORS ({len(result['errors'])}):")
        for e in result["errors"]:
            print(f"    ✗ {e}")

    if result["warnings"]:
        print(f"\n  WARNINGS ({len(result['warnings'])}):")
        for w in result["warnings"]:
            print(f"    ⚠ {w}")

    if result["valid"]:
        print("\n  ✓ Manifest is valid")
    else:
        print("\n  ✗ Manifest has errors — fix before committing")

    sys.exit(0 if result["valid"] else 1)


if __name__ == "__main__":
    main()
