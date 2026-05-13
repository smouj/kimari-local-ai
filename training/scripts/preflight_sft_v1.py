#!/usr/bin/env python3
"""Preflight checks for Kimari Runtime 1.5B SFT v1.

This script validates config, dataset, license, and artifact safety before any
training can be considered. It never downloads models, runs training, or submits
HF Jobs.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from contextlib import suppress
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[2]
LICENSE_MATRIX = PROJECT_ROOT / "docs" / "KIMARI_BASE_MODEL_LICENSE_MATRIX.md"
BLOCKED_LICENSE_MARKERS = (
    "cc-by-nc",
    "non-commercial",
    "noncommercial",
    "research-only",
    "qwen-research",
    "gemma license",
    "meta llama license",
    "unknown",
)


def parse_simple_yaml(path: Path) -> dict[str, Any]:
    data: dict[str, Any] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or ":" not in stripped:
            continue
        key, _, raw_value = stripped.partition(":")
        key = key.strip()
        value = raw_value.strip().strip('"').strip("'")
        lowered = value.lower()
        if lowered == "true":
            data[key] = True
        elif lowered == "false":
            data[key] = False
        elif lowered in {"null", "~"}:
            data[key] = None
        else:
            try:
                data[key] = int(value)
            except ValueError:
                try:
                    data[key] = float(value)
                except ValueError:
                    data[key] = value
    return data


def project_path(path_value: str) -> Path:
    path = Path(path_value)
    if path.is_absolute():
        return path
    return PROJECT_ROOT / path


def check_gitignored(path: Path) -> tuple[bool, str]:
    rel = path
    with suppress(ValueError):
        rel = path.relative_to(PROJECT_ROOT)

    try:
        proc = subprocess.run(
            ["git", "check-ignore", str(rel)],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            timeout=10,
        )
        if proc.returncode == 0:
            return True, proc.stdout.strip() or str(rel)
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass

    gitignore = PROJECT_ROOT / ".gitignore"
    if not gitignore.exists():
        return False, ".gitignore missing"

    rel_str = str(rel)
    for raw in gitignore.read_text(encoding="utf-8").splitlines():
        pattern = raw.strip()
        if not pattern or pattern.startswith("#") or pattern.startswith("!"):
            continue
        if pattern.endswith("/") and rel_str.startswith(pattern.rstrip("/") + "/"):
            return True, pattern
        if rel_str == pattern or rel_str.startswith(pattern + "/"):
            return True, pattern
        if pattern.startswith("*.") and rel_str.endswith(pattern[1:]):
            return True, pattern
    return False, f"not ignored: {rel_str}"


def model_is_apache_approved(base_model: str) -> tuple[bool, str]:
    if not LICENSE_MATRIX.exists():
        return False, f"missing license matrix: {LICENSE_MATRIX}"
    text = LICENSE_MATRIX.read_text(encoding="utf-8")
    for line in text.splitlines():
        if f"`{base_model}`" in line:
            normalized = line.lower().replace("-", " ")
            if "apache 2.0" in normalized and "approved" in normalized:
                return True, "base model is listed as Apache 2.0 and approved"
            return False, f"base model row is not approved Apache 2.0: {line.strip()}"
    return False, f"base model not found in license matrix: {base_model}"


def validate_manifest(path: Path) -> tuple[bool, list[str]]:
    errors: list[str] = []
    try:
        manifest = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return False, [f"license manifest invalid JSON: {exc}"]
    if not isinstance(manifest, dict):
        return False, ["license manifest must be a JSON object"]
    if manifest.get("all_permissive") is not True:
        errors.append("license manifest all_permissive must be true")
    if manifest.get("blocked_found") is not False:
        errors.append("license manifest blocked_found must be false")
    sources = manifest.get("sources")
    if not isinstance(sources, list) or not sources:
        errors.append("license manifest sources must be a non-empty list")
        return False, errors
    for source in sources:
        if not isinstance(source, dict):
            errors.append("license manifest source entry must be an object")
            continue
        license_name = str(source.get("license", "")).lower()
        if any(marker in license_name for marker in BLOCKED_LICENSE_MARKERS):
            errors.append(f"blocked license marker found: {source.get('source_id')}={source.get('license')}")
        if source.get("redistribution_allowed") is not True:
            errors.append(f"redistribution not allowed: {source.get('source_id')}")
        if source.get("commercial_use_allowed") is not True:
            errors.append(f"commercial use not allowed: {source.get('source_id')}")
    return not errors, errors


def validate_sft_jsonl(path: Path, strict: bool) -> tuple[bool, list[str], int]:
    errors: list[str] = []
    count = 0
    allowed_roles = {"system", "user", "assistant"}
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            if strict:
                errors.append(f"{path.name}:{line_number} blank line")
            continue
        count += 1
        try:
            item = json.loads(line)
        except json.JSONDecodeError as exc:
            errors.append(f"{path.name}:{line_number} invalid JSON: {exc}")
            continue
        if not isinstance(item, dict):
            errors.append(f"{path.name}:{line_number} item must be an object")
            continue
        messages = item.get("messages")
        if not isinstance(messages, list) or len(messages) < 2:
            errors.append(f"{path.name}:{line_number} messages must be a list with at least 2 entries")
            continue
        has_user = False
        has_assistant = False
        for index, message in enumerate(messages):
            if not isinstance(message, dict):
                errors.append(f"{path.name}:{line_number} message {index} must be an object")
                continue
            role = message.get("role")
            content = message.get("content")
            if role not in allowed_roles:
                errors.append(f"{path.name}:{line_number} message {index} invalid role: {role}")
            if not isinstance(content, str) or not content.strip():
                errors.append(f"{path.name}:{line_number} message {index} content must be non-empty string")
            has_user = has_user or role == "user"
            has_assistant = has_assistant or role == "assistant"
        if not has_user or not has_assistant:
            errors.append(f"{path.name}:{line_number} must include user and assistant messages")
    if count == 0:
        errors.append(f"{path.name} has no JSONL records")
    return not errors, errors[:50], count


def validate(config_path: Path, strict: bool) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    checks: dict[str, Any] = {}

    if not config_path.exists():
        return {"status": "fail", "errors": [f"config not found: {config_path}"], "warnings": [], "checks": {}}

    config = parse_simple_yaml(config_path)
    checks["config_loaded"] = True

    required = [
        "run_id",
        "base_model",
        "base_license",
        "dataset_train",
        "dataset_validation",
        "dataset_summary",
        "method",
        "max_steps",
        "push_to_hub",
        "report_to",
        "public_release_allowed",
        "hf_public_upload_allowed",
        "gguf_export_allowed",
        "gate_state",
        "output_dir",
    ]
    for key in required:
        if key not in config:
            errors.append(f"missing config key: {key}")

    base_model = str(config.get("base_model", ""))
    approved, message = model_is_apache_approved(base_model)
    checks["base_model_license"] = {"ok": approved, "message": message}
    if not approved or config.get("base_license") != "Apache-2.0":
        errors.append("base model must be approved Apache-2.0")

    train_path = project_path(str(config.get("dataset_train", "")))
    validation_path = project_path(str(config.get("dataset_validation", "")))
    summary_path = project_path(str(config.get("dataset_summary", "")))
    manifest_path = summary_path.parent / "license_manifest.json"

    for label, path in (
        ("train", train_path),
        ("validation", validation_path),
        ("summary", summary_path),
        ("license_manifest", manifest_path),
    ):
        exists = path.exists()
        checks[f"{label}_exists"] = exists
        if not exists:
            errors.append(f"{label} file missing: {path}")

    if train_path.exists():
        ok, sft_errors, train_count = validate_sft_jsonl(train_path, strict)
        checks["train_sft_format"] = {"ok": ok, "count": train_count}
        errors.extend(sft_errors)
    if validation_path.exists():
        ok, sft_errors, validation_count = validate_sft_jsonl(validation_path, strict)
        checks["validation_sft_format"] = {"ok": ok, "count": validation_count}
        errors.extend(sft_errors)
    if summary_path.exists():
        try:
            summary = json.loads(summary_path.read_text(encoding="utf-8"))
            checks["dataset_summary"] = {
                "total_items": summary.get("total_items"),
                "train_items": summary.get("train_items"),
                "validation_items": summary.get("validation_items"),
                "gate": summary.get("safety", {}).get("gate") if isinstance(summary.get("safety"), dict) else None,
            }
            if strict and summary.get("safety", {}).get("gate") != "BLOCKED":
                errors.append("dataset summary safety gate must be BLOCKED")
        except json.JSONDecodeError as exc:
            errors.append(f"dataset summary invalid JSON: {exc}")
    if manifest_path.exists():
        ok, manifest_errors = validate_manifest(manifest_path)
        checks["license_manifest"] = {"ok": ok}
        errors.extend(manifest_errors)

    if config.get("push_to_hub") is not False:
        errors.append("push_to_hub must be false")
    if config.get("report_to") != "none":
        errors.append("report_to must be none")
    if config.get("gate_state") != "BLOCKED":
        errors.append("gate_state must be BLOCKED")
    if config.get("public_release_allowed") is not False:
        errors.append("public_release_allowed must be false")
    if config.get("hf_public_upload_allowed") is not False:
        errors.append("hf_public_upload_allowed must be false")
    if config.get("gguf_export_allowed") is not False:
        errors.append("gguf_export_allowed must be false")
    if config.get("max_steps", 999999) > 500:
        errors.append("max_steps must be <= 500 for the seed dataset")
    if config.get("save_adapter") is not True:
        warnings.append("save_adapter is not true; expected private local adapter output for real future runs")

    output_dir = project_path(str(config.get("output_dir", "")))
    ignored, ignore_detail = check_gitignored(output_dir)
    checks["output_dir_gitignored"] = {"ok": ignored, "detail": ignore_detail}
    if not ignored:
        errors.append(f"output_dir is not gitignored: {output_dir}")

    return {
        "status": "pass" if not errors else "fail",
        "config": str(config_path),
        "strict": strict,
        "errors": errors,
        "warnings": warnings,
        "checks": checks,
    }


def print_text(result: dict[str, Any]) -> None:
    print(f"SFT v1 preflight: {result['status'].upper()}")
    print(f"Config: {result.get('config')}")
    for error in result.get("errors", []):
        print(f"  ✗ {error}")
    for warning in result.get("warnings", []):
        print(f"  ⚠ {warning}")
    if result["status"] == "pass":
        print("  ✓ config, dataset, license, and artifact safety checks passed")


def main() -> None:
    parser = argparse.ArgumentParser(description="Preflight validation for Kimari Runtime 1.5B SFT v1.")
    parser.add_argument("--config", type=Path, required=True, help="Path to SFT v1 YAML config")
    parser.add_argument("--json", action="store_true", dest="json_output", help="Emit structured JSON")
    parser.add_argument("--strict", action="store_true", help="Enable stricter dataset summary checks")
    args = parser.parse_args()

    result = validate(args.config, args.strict)
    if args.json_output:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print_text(result)
    sys.exit(0 if result["status"] == "pass" else 1)


if __name__ == "__main__":
    main()
