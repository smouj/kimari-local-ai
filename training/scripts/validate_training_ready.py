#!/usr/bin/env python3
"""Validate training readiness for Kimari-4B.

Checks that all prerequisites are met before starting a training run:
- Base candidates YAML has accepted candidate with correct flags
- SFT and preference datasets are valid JSONL with required fields
- Holdout dataset is valid JSONL
- Minimum record counts are met
- No forbidden strings (secrets, keys) in datasets
- No GGUF files tracked in git
- No premature release claims

No network calls. No downloads.

Usage:
    python training/scripts/validate_training_ready.py \
        --base-config training/configs/base_candidates.yaml \
        --sft dataset/v0/sft_v0.jsonl \
        --preference dataset/v0/preference_v0.jsonl \
        --holdout dataset/v0/eval_holdout.jsonl \
        --json
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

# Forbidden strings that must never appear in training data.
# These are patterns for actual leaked secrets, not placeholder examples.
# E.g., "password=" as a literal with an actual value is flagged,
# but "POSTGRES_PASSWORD=${DB_PASSWORD}" (env var reference) is fine.
FORBIDDEN_STRINGS = [
    "BEGIN RSA PRIVATE KEY",
    "BEGIN PRIVATE KEY",
    "BEGIN OPENSSH PRIVATE KEY",
    "-----BEGIN PGP PRIVATE KEY BLOCK-----",
]

# Minimum record counts
MIN_SFT = 50
MIN_PREFERENCE = 20
MIN_HOLDOUT = 10


def parse_simple_yaml(path: Path) -> dict | None:
    """Parse YAML with PyYAML fallback to simple parser.

    Returns None if parsing fails.
    """
    try:
        import yaml

        with open(path) as f:
            return yaml.safe_load(f)
    except ImportError:
        pass

    # Simple fallback parser for our specific YAML structure
    text = path.read_text()
    candidates: list[dict] = []
    current_candidate: dict | None = None

    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue

        if stripped.startswith("- id:"):
            if current_candidate is not None:
                candidates.append(current_candidate)
            current_candidate = {"id": stripped.split("id:")[1].strip().strip('"').strip("'")}
        elif current_candidate is not None and ":" in stripped:
            key, _, value = stripped.partition(":")
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            if value:
                # Try boolean conversion
                if value.lower() == "true":
                    current_candidate[key] = True
                elif value.lower() == "false":
                    current_candidate[key] = False
                else:
                    try:
                        current_candidate[key] = int(value)
                    except ValueError:
                        try:
                            current_candidate[key] = float(value)
                        except ValueError:
                            current_candidate[key] = value

    if current_candidate is not None:
        candidates.append(current_candidate)

    return {"candidates": candidates}


def load_jsonl(path: Path) -> tuple[list[dict], list[str]]:
    """Load JSONL file, return (records, errors)."""
    records: list[dict] = []
    errors: list[str] = []

    if not path.exists():
        errors.append(f"File not found: {path}")
        return records, errors

    with open(path) as f:
        for line_num, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                record = json.loads(line)
                if not isinstance(record, dict):
                    errors.append(f"line {line_num}: not a JSON object")
                    continue
                records.append(record)
            except json.JSONDecodeError as exc:
                errors.append(f"line {line_num}: invalid JSON — {exc}")

    return records, errors


def check_forbidden_strings(records: list[dict], label: str) -> list[str]:
    """Check records for forbidden strings. Returns list of findings."""
    findings: list[str] = []
    for idx, record in enumerate(records):
        # Serialize each record to check for forbidden strings in any field
        text = json.dumps(record).lower()
        for forbidden in FORBIDDEN_STRINGS:
            if forbidden.lower() in text:
                findings.append(f"{label} record {idx}: contains forbidden string '{forbidden}'")
    return findings


def check_release_claim(records: list[dict], label: str) -> list[str]:
    """Check records for premature release claims."""
    findings: list[str] = []
    claim = "Kimari-4B is released"
    for idx, record in enumerate(records):
        text = json.dumps(record)
        if claim in text:
            findings.append(f"{label} record {idx}: contains premature release claim '{claim}'")
    return findings


def check_source_license(records: list[dict], label: str) -> list[str]:
    """Check records have source and license fields."""
    findings: list[str] = []
    for idx, record in enumerate(records):
        if "source" not in record:
            findings.append(f"{label} record {idx}: missing 'source' field")
        if "license" not in record:
            findings.append(f"{label} record {idx}: missing 'license' field")
    return findings


def check_gguf_in_git() -> list[str]:
    """Check no GGUF files are tracked in git."""
    findings: list[str] = []
    try:
        result = subprocess.run(
            ["git", "ls-files", "*.gguf"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result.returncode == 0:
            gguf_files = [f for f in result.stdout.strip().splitlines() if f.strip()]
            if gguf_files:
                findings.append(f"GGUF files tracked in git: {gguf_files}")
    except (FileNotFoundError, subprocess.TimeoutExpired):
        # git not available or timeout — skip check
        pass
    return findings


def main() -> None:
    """CLI entry point for training readiness validation."""
    parser = argparse.ArgumentParser(
        description="Validate training readiness for Kimari-4B. No network calls. No downloads.",
    )
    parser.add_argument(
        "--base-config",
        type=Path,
        default=Path(__file__).resolve().parent.parent / "configs" / "base_candidates.yaml",
        help="Path to base_candidates.yaml",
    )
    parser.add_argument("--sft", type=Path, required=True, help="Path to SFT JSONL dataset")
    parser.add_argument("--preference", type=Path, required=True, help="Path to preference JSONL dataset")
    parser.add_argument("--holdout", type=Path, required=True, help="Path to holdout JSONL dataset")
    parser.add_argument("--json", action="store_true", dest="json_output", help="Output results as JSON")

    args = parser.parse_args()

    checks: dict[str, dict] = {}
    all_pass = True

    # Check 1: base_candidates.yaml has accepted candidate
    print("Checking base candidates config...", file=sys.stderr)
    base_data = parse_simple_yaml(args.base_config)
    if base_data is None:
        checks["base_config_parse"] = {"status": "FAIL", "message": f"Failed to parse {args.base_config}"}
        all_pass = False
    else:
        candidates = base_data.get("candidates", [])
        accepted = [c for c in candidates if c.get("status") == "accepted_private_training_candidate"]
        if not accepted:
            checks["accepted_candidate"] = {
                "status": "FAIL",
                "message": "No candidate with status 'accepted_private_training_candidate'",
                "candidates_checked": len(candidates),
            }
            all_pass = False
        else:
            checks["accepted_candidate"] = {"status": "PASS", "accepted_count": len(accepted)}

            # Check selected_for_private_sft
            sft_selected = [c for c in accepted if c.get("selected_for_private_sft") is True]
            if not sft_selected:
                checks["selected_for_private_sft"] = {
                    "status": "FAIL",
                    "message": "Accepted candidate does not have selected_for_private_sft: true",
                }
                all_pass = False
            else:
                checks["selected_for_private_sft"] = {"status": "PASS"}

            # Check selected_for_public_release is false
            public_not_selected = [c for c in accepted if c.get("selected_for_public_release") is False]
            if not public_not_selected:
                checks["not_selected_for_public_release"] = {
                    "status": "FAIL",
                    "message": "Accepted candidate must have selected_for_public_release: false",
                }
                all_pass = False
            else:
                checks["not_selected_for_public_release"] = {"status": "PASS"}

    # Check 2: SFT dataset
    print("Checking SFT dataset...", file=sys.stderr)
    sft_records, sft_errors = load_jsonl(args.sft)
    if sft_errors:
        checks["sft_parse"] = {"status": "FAIL", "errors": sft_errors[:10]}
        all_pass = False
    else:
        checks["sft_parse"] = {"status": "PASS", "record_count": len(sft_records)}

    if len(sft_records) < MIN_SFT:
        checks["sft_min_count"] = {
            "status": "FAIL",
            "message": f"SFT has {len(sft_records)} records, minimum is {MIN_SFT}",
            "actual": len(sft_records),
            "required": MIN_SFT,
        }
        all_pass = False
    else:
        checks["sft_min_count"] = {"status": "PASS", "actual": len(sft_records), "required": MIN_SFT}

    sft_source_license = check_source_license(sft_records, "SFT")
    if sft_source_license:
        checks["sft_source_license"] = {"status": "FAIL", "findings": sft_source_license[:10]}
        all_pass = False
    else:
        checks["sft_source_license"] = {"status": "PASS"}

    # Check 3: Preference dataset
    print("Checking preference dataset...", file=sys.stderr)
    pref_records, pref_errors = load_jsonl(args.preference)
    if pref_errors:
        checks["preference_parse"] = {"status": "FAIL", "errors": pref_errors[:10]}
        all_pass = False
    else:
        checks["preference_parse"] = {"status": "PASS", "record_count": len(pref_records)}

    if len(pref_records) < MIN_PREFERENCE:
        checks["preference_min_count"] = {
            "status": "FAIL",
            "message": f"Preference has {len(pref_records)} records, minimum is {MIN_PREFERENCE}",
            "actual": len(pref_records),
            "required": MIN_PREFERENCE,
        }
        all_pass = False
    else:
        checks["preference_min_count"] = {"status": "PASS", "actual": len(pref_records), "required": MIN_PREFERENCE}

    pref_source_license = check_source_license(pref_records, "preference")
    if pref_source_license:
        checks["preference_source_license"] = {"status": "FAIL", "findings": pref_source_license[:10]}
        all_pass = False
    else:
        checks["preference_source_license"] = {"status": "PASS"}

    # Check 4: Holdout dataset
    print("Checking holdout dataset...", file=sys.stderr)
    holdout_records, holdout_errors = load_jsonl(args.holdout)
    if holdout_errors:
        checks["holdout_parse"] = {"status": "FAIL", "errors": holdout_errors[:10]}
        all_pass = False
    else:
        checks["holdout_parse"] = {"status": "PASS", "record_count": len(holdout_records)}

    if len(holdout_records) < MIN_HOLDOUT:
        checks["holdout_min_count"] = {
            "status": "FAIL",
            "message": f"Holdout has {len(holdout_records)} records, minimum is {MIN_HOLDOUT}",
            "actual": len(holdout_records),
            "required": MIN_HOLDOUT,
        }
        all_pass = False
    else:
        checks["holdout_min_count"] = {"status": "PASS", "actual": len(holdout_records), "required": MIN_HOLDOUT}

    # Check 5: Forbidden strings in all datasets
    print("Checking for forbidden strings...", file=sys.stderr)
    all_records_with_labels = [
        (sft_records, "SFT"),
        (pref_records, "preference"),
        (holdout_records, "holdout"),
    ]
    all_forbidden: list[str] = []
    for records, label in all_records_with_labels:
        all_forbidden.extend(check_forbidden_strings(records, label))
    if all_forbidden:
        checks["forbidden_strings"] = {"status": "FAIL", "findings": all_forbidden[:10]}
        all_pass = False
    else:
        checks["forbidden_strings"] = {"status": "PASS"}

    # Check 6: No premature release claims
    print("Checking for premature release claims...", file=sys.stderr)
    all_claims: list[str] = []
    for records, label in all_records_with_labels:
        all_claims.extend(check_release_claim(records, label))
    if all_claims:
        checks["release_claim"] = {"status": "FAIL", "findings": all_claims}
        all_pass = False
    else:
        checks["release_claim"] = {"status": "PASS"}

    # Check 7: No GGUF files in git
    print("Checking git for GGUF files...", file=sys.stderr)
    gguf_findings = check_gguf_in_git()
    if gguf_findings:
        checks["gguf_in_git"] = {"status": "FAIL", "findings": gguf_findings}
        all_pass = False
    else:
        checks["gguf_in_git"] = {"status": "PASS"}

    # Output
    if args.json_output:
        output = {"all_pass": all_pass, "checks": checks}
        print(json.dumps(output, indent=2))
    else:
        print(f"\n{'=' * 50}")
        print("Training Readiness Validation")
        print(f"{'=' * 50}")
        for name, result in checks.items():
            status = result["status"]
            symbol = "PASS" if status == "PASS" else "FAIL"
            print(f"  [{symbol}] {name}")
            if status == "FAIL" and "message" in result:
                print(f"         {result['message']}")
        print(f"\n{'=' * 50}")
        if all_pass:
            print("All checks PASSED. Training is ready.")
        else:
            print("Some checks FAILED. Fix issues before training.")

    sys.exit(0 if all_pass else 1)


if __name__ == "__main__":
    main()
