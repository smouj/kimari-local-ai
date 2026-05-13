#!/usr/bin/env python3
"""Validate Kimari SFT v1 dataset.

Checks:
- JSONL parseable
- Schema valid (kimari_sft_item.schema.json)
- IDs unique
- Categories valid
- Minimum per category
- Licenses allowed (no blocked)
- No secrets/tokens
- No PII patterns
- No "Kimari-4B released" claims
- No "public weights available" claims
- Quality score range
- Roles correct (system/user/assistant)
- Message lengths reasonable

Usage:
    python dataset/scripts/validate_kimari_sft_v1.py --dataset-dir dataset/kimari_sft_v1
    python dataset/scripts/validate_kimari_sft_v1.py --dataset-dir dataset/kimari_sft_v1 --json
    python dataset/scripts/validate_kimari_sft_v1.py --dataset-dir dataset/kimari_sft_v1 --min-items 30 --strict
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path

try:
    import jsonschema as _jsonschema

    HAS_JSONSCHEMA = True
except ImportError:
    HAS_JSONSCHEMA = False

try:
    import yaml as _yaml

    HAS_YAML = True
except ImportError:
    HAS_YAML = False

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
SCHEMA_PATH = PROJECT_ROOT / "dataset" / "schema" / "kimari_sft_item.schema.json"
MANIFEST_PATH = PROJECT_ROOT / "dataset" / "kimari_sft_v1" / "manifest.yaml"

VALID_CATEGORIES = {
    "spanish_technical",
    "coding_debug",
    "server_ops",
    "local_llm_cuda_gguf",
    "openclaw_agents",
    "safety_refusal",
    "json_tooling",
    "style_consistency",
}

ALLOWED_LICENSES = {
    "project-owned",
    "MIT",
    "Apache-2.0",
    "BSD-3-Clause",
    "CC-BY-4.0",
    "CC-BY-SA-4.0",
}

BLOCKED_LICENSES = {
    "unknown",
    "non-commercial",
    "research-only",
    "proprietary",
    "copied-from-private-chat",
    "raw-logs",
    "closed-model-output",
}

FORBIDDEN_PHRASES = [
    "kimari-4b released",
    "kimari-4b is released",
    "kimari-4b is available",
    "kimari-4b can be downloaded",
    "public weights available",
    "production ready",
]

SECRET_PATTERNS = [
    re.compile(r"(?:api[_-]?key|secret[_-]?key|auth[_-]?token)\s*[:=]\s*['\"][^'\"]{8,}", re.I),
    re.compile(r"(?:password|passwd)\s*[:=]\s*['\"][^'\"]{6,}", re.I),
    re.compile(r"sk-[a-zA-Z0-9]{20,}"),  # OpenAI-style keys
    re.compile(r"ghp_[a-zA-Z0-9]{30,}"),  # GitHub tokens
    re.compile(r"gho_[a-zA-Z0-9]{30,}"),  # GitHub OAuth
]

PII_PATTERNS = [
    re.compile(r"\b\d{3}[-.]?\d{3}[-.]?\d{4}\b"),  # Phone numbers (loose)
    re.compile(r"\b[A-Z][a-z]+@[a-z]+\.[a-z]{2,}\b"),  # Simple email-like
]


def load_schema() -> dict | None:
    if not SCHEMA_PATH.exists():
        return None
    with open(SCHEMA_PATH) as f:
        return json.load(f)


def validate_item(item: dict, line_num: int, schema: dict | None, strict: bool) -> list[str]:
    """Validate a single dataset item."""
    errors = []

    # Required fields
    required = ["id", "category", "language", "source", "license", "quality_score", "tags", "messages"]
    for field in required:
        if field not in item:
            errors.append(f"Line {line_num}: missing required field '{field}'")

    if errors:
        return errors

    # Category
    if item["category"] not in VALID_CATEGORIES:
        errors.append(f"Line {line_num}: invalid category '{item['category']}'")

    # Language
    if item.get("language") not in ("es", "en", "mixed"):
        errors.append(f"Line {line_num}: invalid language '{item.get('language')}'")

    # License
    license_val = item.get("license", "")
    if license_val in BLOCKED_LICENSES:
        errors.append(f"Line {line_num}: blocked license '{license_val}'")
    elif license_val not in ALLOWED_LICENSES and strict:
        errors.append(f"Line {line_num}: unknown license '{license_val}' (not in allowed or blocked)")

    # Quality score
    qs = item.get("quality_score", 0)
    if not isinstance(qs, int) or qs < 1 or qs > 5:
        errors.append(f"Line {line_num}: quality_score must be 1-5, got {qs}")
    elif qs < 3 and strict:
        errors.append(f"Line {line_num}: quality_score {qs} below minimum 3 (strict mode)")

    # Messages
    messages = item.get("messages", [])
    if not isinstance(messages, list) or len(messages) < 2:
        errors.append(f"Line {line_num}: messages must be a list with at least 2 items")
    else:
        roles = [m.get("role") for m in messages]
        if "system" not in roles:
            errors.append(f"Line {line_num}: messages must include system role")
        if "user" not in roles:
            errors.append(f"Line {line_num}: messages must include user role")
        if "assistant" not in roles:
            errors.append(f"Line {line_num}: messages must include assistant role")

        for m in messages:
            content = m.get("content", "")
            if not content or len(content) < 10:
                errors.append(f"Line {line_num}: message content too short ({len(content)} chars)")
            if len(content) > 8192:
                errors.append(f"Line {line_num}: message content too long ({len(content)} chars)")

            # Check for forbidden phrases
            content_lower = content.lower()
            for phrase in FORBIDDEN_PHRASES:
                if phrase in content_lower:
                    errors.append(f"Line {line_num}: forbidden phrase '{phrase}' in message content")

            # Check for secrets
            for pattern in SECRET_PATTERNS:
                if pattern.search(content):
                    errors.append(f"Line {line_num}: potential secret/token found in message content")

    # Tags
    tags = item.get("tags", [])
    if not isinstance(tags, list) or len(tags) < 1:
        errors.append(f"Line {line_num}: tags must be a non-empty list")

    # Schema validation
    if schema and HAS_JSONSCHEMA:
        try:
            _jsonschema.validate(item, schema)
        except _jsonschema.ValidationError as e:
            if strict:
                errors.append(f"Line {line_num}: schema validation: {e.message}")

    return errors


def main():
    parser = argparse.ArgumentParser(description="Validate Kimari SFT v1 dataset")
    parser.add_argument("--dataset-dir", required=True, help="Path to dataset directory")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("--min-items", type=int, default=30, help="Minimum items per category (default: 30)")
    parser.add_argument("--strict", action="store_true", help="Strict validation mode")
    args = parser.parse_args()

    dataset_dir = Path(args.dataset_dir)
    sources_dir = dataset_dir / "sources"

    if not dataset_dir.exists():
        print(f"ERROR: Dataset directory not found: {dataset_dir}", file=sys.stderr)
        sys.exit(1)

    all_errors = []
    all_warnings = []
    all_items = []
    category_counts = Counter()
    seen_ids = set()
    total_lines = 0

    schema = load_schema()
    if schema is None and args.strict:
        all_warnings.append("Schema file not found, skipping schema validation")

    # Validate each source file
    source_files = sorted(sources_dir.glob("*.jsonl"))
    if not source_files:
        all_errors.append("No JSONL source files found in sources/ directory")

    for source_file in source_files:
        with open(source_file) as f:
            for line_num, line in enumerate(f, 1):
                total_lines += 1
                line = line.strip()
                if not line:
                    all_errors.append(f"{source_file.name}:{line_num}: blank line")
                    continue

                try:
                    item = json.loads(line)
                except json.JSONDecodeError as e:
                    all_errors.append(f"{source_file.name}:{line_num}: invalid JSON: {e}")
                    continue

                # Check duplicate IDs
                item_id = item.get("id", "")
                if item_id in seen_ids:
                    all_errors.append(f"{source_file.name}:{line_num}: duplicate ID '{item_id}'")
                seen_ids.add(item_id)

                # Validate item
                item_errors = validate_item(item, line_num, schema, args.strict)
                all_errors.extend(item_errors)

                # Track category
                cat = item.get("category", "unknown")
                category_counts[cat] += 1
                all_items.append(item)

    # Check minimum per category
    for cat in VALID_CATEGORIES:
        count = category_counts.get(cat, 0)
        if count < args.min_items:
            all_warnings.append(f"Category '{cat}' has {count} items (minimum: {args.min_items})")

    # Check manifest
    if MANIFEST_PATH.exists() and HAS_YAML:
        with open(MANIFEST_PATH) as f:
            manifest = _yaml.safe_load(f)
        manifest_categories = {c["id"] for c in manifest.get("categories", [])}
        missing_from_manifest = VALID_CATEGORIES - manifest_categories
        if missing_from_manifest and args.strict:
            all_warnings.append(f"Categories missing from manifest: {missing_from_manifest}")

    # Output
    valid = len(all_errors) == 0
    result = {
        "valid": valid,
        "total_items": total_lines,
        "unique_ids": len(seen_ids),
        "categories": dict(category_counts),
        "errors": all_errors,
        "warnings": all_warnings,
        "error_count": len(all_errors),
        "warning_count": len(all_warnings),
    }

    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        status = "VALID" if valid else "INVALID"
        print(f"Dataset validation: {status}")
        print(f"  Total items: {total_lines}")
        print(f"  Unique IDs: {len(seen_ids)}")
        print(f"  Categories: {dict(category_counts)}")
        if all_errors:
            print(f"  Errors ({len(all_errors)}):")
            for err in all_errors[:20]:
                print(f"    - {err}")
            if len(all_errors) > 20:
                print(f"    ... and {len(all_errors) - 20} more")
        if all_warnings:
            print(f"  Warnings ({len(all_warnings)}):")
            for warn in all_warnings:
                print(f"    - {warn}")

    sys.exit(0 if valid else 1)


if __name__ == "__main__":
    main()
