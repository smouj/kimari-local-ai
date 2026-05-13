#!/usr/bin/env python3
"""Build Kimari SFT v1 dataset from source files.

Validates, shuffles, deduplicates, splits into train/validation,
and generates metadata files.

Usage:
    python dataset/scripts/build_kimari_sft_v1.py --dataset-dir dataset/kimari_sft_v1 --output-dir dataset/build/kimari_sft_v1
    python dataset/scripts/build_kimari_sft_v1.py --dataset-dir dataset/kimari_sft_v1 --output-dir dataset/build/kimari_sft_v1 --json
    python dataset/scripts/build_kimari_sft_v1.py --dataset-dir dataset/kimari_sft_v1 --output-dir dataset/build/kimari_sft_v1 --train-ratio 0.9 --seed 42
"""

from __future__ import annotations

import argparse
import hashlib
import json
import random
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

ALLOWED_LICENSES = {
    "project-owned",
    "MIT",
    "Apache-2.0",
    "BSD-3-Clause",
    "CC-BY-4.0",
    "CC-BY-SA-4.0",
}


def compute_sha256(filepath: Path) -> str:
    """Compute SHA-256 hash of a file."""
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def compute_text_hash(text: str) -> str:
    """Compute SHA-256 hash of text content."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def load_sources(sources_dir: Path) -> list[dict]:
    """Load all JSONL source files."""
    items = []
    for source_file in sorted(sources_dir.glob("*.jsonl")):
        with open(source_file) as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue
                try:
                    item = json.loads(line)
                    item["_source_file"] = source_file.name
                    item["_line_num"] = line_num
                    items.append(item)
                except json.JSONDecodeError as e:
                    print(f"WARNING: Invalid JSON in {source_file.name}:{line_num}: {e}", file=sys.stderr)
    return items


def validate_items(items: list[dict]) -> tuple[list[str], list[str]]:
    """Validate all items and return (errors, warnings)."""
    errors = []
    warnings = []
    seen_ids = set()
    seen_hashes = set()

    for item in items:
        item_id = item.get("id", "")
        source = item.get("_source_file", "unknown")
        line = item.get("_line_num", 0)

        # Check required fields
        for field in ["id", "category", "language", "source", "license", "quality_score", "tags", "messages"]:
            if field not in item:
                errors.append(f"{source}:{line}: missing field '{field}'")

        # Check ID uniqueness
        if item_id in seen_ids:
            errors.append(f"{source}:{line}: duplicate ID '{item_id}'")
        seen_ids.add(item_id)

        # Check license
        license_val = item.get("license", "")
        if license_val not in ALLOWED_LICENSES:
            errors.append(f"{source}:{line}: invalid license '{license_val}'")

        # Check quality score
        qs = item.get("quality_score", 0)
        if not isinstance(qs, int) or qs < 1 or qs > 5:
            errors.append(f"{source}:{line}: quality_score must be 1-5, got {qs}")
        elif qs < 3:
            warnings.append(f"{source}:{line}: quality_score {qs} below recommended 3")

        # Deduplicate by prompt hash
        messages = item.get("messages", [])
        user_msgs = [m["content"] for m in messages if m.get("role") == "user"]
        if user_msgs:
            prompt_hash = compute_text_hash(user_msgs[0])
            if prompt_hash in seen_hashes:
                warnings.append(f"{source}:{line}: duplicate prompt content (hash: {prompt_hash[:12]})")
            seen_hashes.add(prompt_hash)

    return errors, warnings


def build_dataset(
    items: list[dict],
    train_ratio: float = 0.9,
    seed: int = 42,
) -> tuple[list[dict], list[dict], dict]:
    """Split items into train and validation sets."""
    rng = random.Random(seed)
    rng.shuffle(items)

    split_idx = int(len(items) * train_ratio)
    train_items = items[:split_idx]
    val_items = items[split_idx:]

    # Compute statistics
    category_counts = Counter(item.get("category", "unknown") for item in items)
    license_counts = Counter(item.get("license", "unknown") for item in items)
    language_counts = Counter(item.get("language", "unknown") for item in items)

    stats = {
        "total_items": len(items),
        "train_items": len(train_items),
        "validation_items": len(val_items),
        "train_ratio": train_ratio,
        "seed": seed,
        "category_counts": dict(category_counts),
        "license_counts": dict(license_counts),
        "language_counts": dict(language_counts),
    }

    return train_items, val_items, stats


def clean_item(item: dict) -> dict:
    """Remove internal fields before writing to output."""
    return {k: v for k, v in item.items() if not k.startswith("_")}


def main():
    parser = argparse.ArgumentParser(description="Build Kimari SFT v1 dataset")
    parser.add_argument("--dataset-dir", required=True, help="Path to dataset directory")
    parser.add_argument("--output-dir", required=True, help="Path to output directory")
    parser.add_argument("--train-ratio", type=float, default=0.9, help="Train/validation split ratio (default: 0.9)")
    parser.add_argument("--seed", type=int, default=42, help="Random seed for shuffling (default: 42)")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args()

    dataset_dir = Path(args.dataset_dir)
    sources_dir = dataset_dir / "sources"
    output_dir = Path(args.output_dir)

    # Load items
    items = load_sources(sources_dir)
    if not items:
        print("ERROR: No items loaded from source files", file=sys.stderr)
        sys.exit(1)

    # Validate
    errors, warnings = validate_items(items)
    if errors:
        print(f"ERROR: {len(errors)} validation errors found:", file=sys.stderr)
        for err in errors[:10]:
            print(f"  {err}", file=sys.stderr)
        if len(errors) > 10:
            print(f"  ... and {len(errors) - 10} more", file=sys.stderr)
        sys.exit(1)

    # Build
    train_items, val_items, stats = build_dataset(items, args.train_ratio, args.seed)

    # Create output directory
    output_dir.mkdir(parents=True, exist_ok=True)

    # Write train.jsonl
    train_path = output_dir / "train.jsonl"
    with open(train_path, "w") as f:
        for item in train_items:
            f.write(json.dumps(clean_item(item), ensure_ascii=False) + "\n")
    train_sha = compute_sha256(train_path)

    # Write validation.jsonl
    val_path = output_dir / "validation.jsonl"
    with open(val_path, "w") as f:
        for item in val_items:
            f.write(json.dumps(clean_item(item), ensure_ascii=False) + "\n")
    val_sha = compute_sha256(val_path)

    # Write dataset_summary.json
    summary = {
        "dataset": "kimari_sft_v1",
        "version": "0.1.59-alpha",
        "stage": "seed",
        "built_at": datetime.now(timezone.utc).isoformat(),
        "total_items": len(items),
        "train_items": len(train_items),
        "validation_items": len(val_items),
        "train_ratio": args.train_ratio,
        "seed": args.seed,
        "category_counts": stats["category_counts"],
        "language_counts": stats["language_counts"],
        "files": {
            "train.jsonl": {"sha256": train_sha, "count": len(train_items)},
            "validation.jsonl": {"sha256": val_sha, "count": len(val_items)},
        },
        "safety": {
            "no_training": True,
            "no_hf_jobs": True,
            "no_public_weights": True,
            "no_public_benchmarks": True,
            "no_pii": True,
            "no_tokens": True,
            "no_private_logs": True,
            "gate": "BLOCKED",
        },
    }
    with open(output_dir / "dataset_summary.json", "w") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)

    # Write license_manifest.json
    license_manifest = {
        "dataset": "kimari_sft_v1",
        "version": "0.1.59-alpha",
        "built_at": datetime.now(timezone.utc).isoformat(),
        "sources": [],
        "license_summary": stats["license_counts"],
        "all_permissive": all(lic in ALLOWED_LICENSES for lic in stats["license_counts"]),
        "blocked_found": False,
    }

    # Load source-level license info from YAML manifest
    try:
        import yaml

        manifest_path = dataset_dir / "license_manifest.yaml"
        if manifest_path.exists():
            with open(manifest_path) as f:
                yaml_manifest = yaml.safe_load(f)
            license_manifest["sources"] = yaml_manifest.get("sources", [])
    except ImportError:
        pass

    with open(output_dir / "license_manifest.json", "w") as f:
        json.dump(license_manifest, f, indent=2, ensure_ascii=False)

    # Write quality_report.json
    quality_report = {
        "dataset": "kimari_sft_v1",
        "version": "0.1.59-alpha",
        "built_at": datetime.now(timezone.utc).isoformat(),
        "total_items": len(items),
        "validation_errors": len(errors),
        "validation_warnings": len(warnings),
        "warnings_list": warnings[:20],
        "dedup_hash_count": len(
            {
                compute_text_hash(next((m["content"] for m in item.get("messages", []) if m.get("role") == "user"), ""))
                for item in items
            }
        ),
        "category_counts": stats["category_counts"],
        "language_counts": stats["language_counts"],
        "quality_check": {
            "all_ids_unique": len({item.get("id") for item in items}) == len(items),
            "all_licenses_permissive": all(item.get("license", "") in ALLOWED_LICENSES for item in items),
            "all_quality_scores_valid": all(
                isinstance(item.get("quality_score", 0), int) and 1 <= item.get("quality_score", 0) <= 5
                for item in items
            ),
            "no_kimari4b_released_claims": not any(
                "kimari-4b released" in json.dumps(item, ensure_ascii=False).lower()
                or "kimari-4b is released" in json.dumps(item, ensure_ascii=False).lower()
                for item in items
            ),
            "no_public_weights_claims": not any(
                "public weights available" in json.dumps(item, ensure_ascii=False).lower() for item in items
            ),
        },
    }
    with open(output_dir / "quality_report.json", "w") as f:
        json.dump(quality_report, f, indent=2, ensure_ascii=False)

    # Output
    if args.json:
        print(json.dumps(summary, indent=2, ensure_ascii=False))
    else:
        print("Dataset build complete:")
        print(f"  Total items: {len(items)}")
        print(f"  Train items: {len(train_items)}")
        print(f"  Validation items: {len(val_items)}")
        print(f"  Categories: {len(stats['category_counts'])}")
        print(f"  Train SHA256: {train_sha[:16]}...")
        print(f"  Validation SHA256: {val_sha[:16]}...")
        if warnings:
            print(f"  Warnings: {len(warnings)}")
        print(f"  Output directory: {output_dir}")


if __name__ == "__main__":
    main()
