#!/usr/bin/env python3
"""CLI script to generate a private SFT run record from template.

Reads the run config YAML to extract run_id, base_model, dataset_id, etc.
If manifest/eval-summary/compare-summary files exist, computes their SHA-256.
Builds a run record JSON and writes it to --output or prints with --json.

Gate is always BLOCKED. public_release_allowed is always false.
hf_upload_allowed is always false. No secrets. No real training.
No model downloads. No HF uploads.

Rejects paths that look like absolute home directory paths
(e.g., /home/username/...).

Works with or without PyYAML (simple line parser fallback).

Usage:
    python training/scripts/create_private_run_record.py \\
        --run-config training/configs/private_sft_run.v0.yaml \\
        --manifest training/adapters/kimari-smollm3-sft-v0/MANIFEST.yaml \\
        --eval-summary eval/results/eval_summary.json \\
        --compare-summary eval/results/compare_summary.json \\
        --output /tmp/private_run_record.json
    python training/scripts/create_private_run_record.py \\
        --run-config training/configs/private_sft_run.v0.yaml \\
        --dry-run
    python training/scripts/create_private_run_record.py \\
        --run-config training/configs/private_sft_run.v0.yaml \\
        --json
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

DEFAULT_RUN_CONFIG = PROJECT_ROOT / "training" / "configs" / "private_sft_run.v0.yaml"
DEFAULT_OUTPUT = Path("/tmp/private_run_record.json")

# Pattern for absolute home directory paths like /home/username/...
_HOME_DIR_PATTERN = re.compile(r"^/home/[^/]+/")


# ---------------------------------------------------------------------------
# YAML parser with pyyaml fallback
# ---------------------------------------------------------------------------


def parse_simple_yaml(path: Path) -> dict | None:
    """Parse YAML with pyyaml fallback to simple line parser.

    Returns None if the file cannot be parsed.
    """
    try:
        import yaml

        with open(path) as f:
            return yaml.safe_load(f)
    except ImportError:
        pass

    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return None

    result: dict = {}
    current_list_key: str | None = None
    current_list: list | None = None

    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue

        if stripped.startswith("- ") and current_list_key is not None:
            item = stripped[2:].strip().strip('"').strip("'")
            if current_list is not None:
                current_list.append(item)
            continue

        if ":" in stripped:
            if current_list_key is not None and current_list is not None:
                result[current_list_key] = current_list
                current_list_key = None
                current_list = None

            key, _, value = stripped.partition(":")
            key = key.strip()
            value = value.strip().strip('"').strip("'")

            if not value:
                current_list_key = key
                current_list = []
            else:
                if value.lower() == "true":
                    result[key] = True
                elif value.lower() == "false":
                    result[key] = False
                elif value.lower() in ("null", "~", "none"):
                    result[key] = None
                else:
                    try:
                        result[key] = int(value)
                    except ValueError:
                        try:
                            result[key] = float(value)
                        except ValueError:
                            result[key] = value

    if current_list_key is not None and current_list is not None:
        result[current_list_key] = current_list

    return result


# ---------------------------------------------------------------------------
# SHA-256 helpers
# ---------------------------------------------------------------------------


def sha256_file(path: Path) -> str:
    """Compute SHA-256 hex digest of a file."""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def sha256_if_exists(path: Path | None, dry_run: bool) -> dict:
    """Return a dict with path, exists, and sha256 (if file exists).

    In dry-run mode, does not require the file to exist.
    """
    result: dict = {
        "path": str(path) if path else None,
        "exists": False,
        "sha256": None,
    }

    if path is None:
        return result

    if dry_run and not path.exists():
        result["exists"] = False
        result["sha256"] = None
        return result

    if path.exists() and path.is_file():
        try:
            result["sha256"] = sha256_file(path)
            result["exists"] = True
        except OSError as exc:
            print(f"WARNING: Could not hash {path}: {exc}", file=sys.stderr)

    return result


# ---------------------------------------------------------------------------
# Path validation
# ---------------------------------------------------------------------------


def is_rejectable_home_path(path: Path | None) -> bool:
    """Reject paths that look like absolute home directory paths.

    E.g. /home/username/something is rejected.
    /tmp/output.json is fine.
    Relative paths are fine.
    """
    if path is None:
        return False
    path_str = str(path)
    return bool(_HOME_DIR_PATTERN.match(path_str))


def validate_paths(**paths: Path | None) -> list[str]:
    """Validate all provided paths. Returns list of error messages."""
    errors: list[str] = []
    for name, path in paths.items():
        if is_rejectable_home_path(path):
            errors.append(
                f"--{name.replace('_', '-')}={path} looks like an absolute home "
                "directory path — use a project-relative or /tmp path instead"
            )
    return errors


# ---------------------------------------------------------------------------
# Run record builder
# ---------------------------------------------------------------------------


def build_run_record(
    run_config_path: Path,
    manifest_path: Path | None,
    eval_summary_path: Path | None,
    compare_summary_path: Path | None,
    dry_run: bool,
    now_iso: str | None = None,
) -> dict:
    """Build the private SFT run record dict.

    Gate is always BLOCKED.
    public_release_allowed is always false.
    hf_upload_allowed is always false.
    """
    if now_iso is None:
        now_iso = datetime.now(timezone.utc).isoformat()

    # Load run config
    config: dict = {}
    if run_config_path.exists() or dry_run:
        if run_config_path.exists():
            parsed = parse_simple_yaml(run_config_path)
            if parsed and isinstance(parsed, dict):
                config = parsed

    # Compute SHA-256 of manifest / eval-summary / compare-summary if they exist
    manifest_info = sha256_if_exists(manifest_path, dry_run)
    eval_info = sha256_if_exists(eval_summary_path, dry_run)
    compare_info = sha256_if_exists(compare_summary_path, dry_run)

    # Try to load eval_summary data if it exists
    eval_data: dict | None = None
    if eval_summary_path is not None and eval_summary_path.exists() and eval_summary_path.is_file():
        try:
            eval_data = json.loads(eval_summary_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError) as exc:
            print(f"WARNING: Could not parse eval summary: {exc}", file=sys.stderr)

    # Try to load compare_summary data if it exists
    compare_data: dict | None = None
    if compare_summary_path is not None and compare_summary_path.exists() and compare_summary_path.is_file():
        try:
            compare_data = json.loads(compare_summary_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError) as exc:
            print(f"WARNING: Could not parse compare summary: {exc}", file=sys.stderr)

    # Derive dataset_id from dataset_build_dir if not in config
    dataset_id = config.get("dataset_id")
    if not dataset_id:
        dataset_build_dir = config.get("dataset_build_dir", "")
        if dataset_build_dir:
            dataset_id = Path(dataset_build_dir).name

    # Build the run record
    record: dict = {
        "record_type": "private_sft_run_record",
        "record_version": "0.1.0",
        "generated_at": now_iso,
        "generator": "create_private_run_record.py",
        # Run identity
        "run_id": config.get("run_id", ""),
        "status": config.get("status", "unknown"),
        # Model info
        "base_model": config.get("base_model", ""),
        "base_model_license": config.get("base_model_license", ""),
        "base_model_status": config.get("base_model_status", ""),
        # Dataset info
        "dataset_id": dataset_id or "",
        "dataset_build_dir": config.get("dataset_build_dir", ""),
        # Training config
        "sft_config": config.get("sft_config", ""),
        "output_dir": config.get("output_dir", ""),
        # Artifact references with SHA-256
        "manifest": manifest_info,
        "eval_summary": eval_info,
        "compare_summary": compare_info,
        # Eval data (embedded if available)
        "eval_data": eval_data,
        "compare_data": compare_data,
        # Safety constraints — ALWAYS these values
        "preview_gate_state": "BLOCKED",
        "public_release_allowed": False,
        "hf_upload_allowed": False,
        # Metadata
        "eval_plan": config.get("eval_plan", ""),
        "artifact_policy": config.get("artifact_policy", ""),
        "preview_gate": config.get("preview_gate", ""),
        "notes": config.get("notes", ""),
        "created_date": config.get("created_date", ""),
        # Dry-run marker
        "dry_run": dry_run,
    }

    return record


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main() -> None:
    """CLI entry point for creating private SFT run records."""
    parser = argparse.ArgumentParser(
        description="Generate a private SFT run record from template. "
        "No real training. No model downloads. No HF uploads. No secrets.",
    )
    parser.add_argument(
        "--run-config",
        type=Path,
        default=DEFAULT_RUN_CONFIG,
        help="Path to run config YAML (default: training/configs/private_sft_run.v0.yaml)",
    )
    parser.add_argument(
        "--manifest",
        type=Path,
        default=None,
        help="Path to MANIFEST.yaml",
    )
    parser.add_argument(
        "--eval-summary",
        type=Path,
        default=None,
        help="Path to eval_summary.json",
    )
    parser.add_argument(
        "--compare-summary",
        type=Path,
        default=None,
        help="Path to compare_summary.json",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help="Output path (default: /tmp/private_run_record.json)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Don't write anything, just show what would be generated",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        dest="json_output",
        help="Output structured JSON to stdout",
    )

    args = parser.parse_args()

    # Validate user-supplied paths — reject absolute home directory paths.
    # Only check paths the user explicitly provided (not defaults, which are
    # safe by construction: DEFAULT_RUN_CONFIG comes from PROJECT_ROOT,
    # DEFAULT_OUTPUT is /tmp/...).
    user_paths: dict[str, Path | None] = {}
    if args.manifest is not None:
        user_paths["manifest"] = args.manifest
    if args.eval_summary is not None:
        user_paths["eval-summary"] = args.eval_summary
    if args.compare_summary is not None:
        user_paths["compare-summary"] = args.compare_summary
    if args.output != DEFAULT_OUTPUT:
        user_paths["output"] = args.output
    if args.run_config != DEFAULT_RUN_CONFIG:
        user_paths["run-config"] = args.run_config

    path_errors = validate_paths(**user_paths)
    if path_errors:
        for err in path_errors:
            print(f"ERROR: {err}", file=sys.stderr)
        sys.exit(1)

    # Build the run record
    record = build_run_record(
        run_config_path=args.run_config,
        manifest_path=args.manifest,
        eval_summary_path=args.eval_summary,
        compare_summary_path=args.compare_summary,
        dry_run=args.dry_run,
    )

    # Format as JSON
    record_json = json.dumps(record, indent=2, default=str)

    if args.dry_run and not args.json_output:
        print("=== DRY-RUN: would generate the following run record ===")
        print(record_json)
        print()
        print(f"Would write to: {args.output}")
        print("No files were written (dry-run mode).")
    elif args.dry_run and args.json_output:
        # --json takes precedence: just output the structured JSON
        print(record_json)
    elif args.json_output:
        print(record_json)
    else:
        # Write to --output
        if args.output is None:
            print("ERROR: --output is required when not using --dry-run or --json", file=sys.stderr)
            sys.exit(1)

        try:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(record_json + "\n", encoding="utf-8")
            print(f"Run record written to: {args.output}", file=sys.stderr)
        except OSError as exc:
            print(f"ERROR: Could not write to {args.output}: {exc}", file=sys.stderr)
            sys.exit(1)


if __name__ == "__main__":
    main()
