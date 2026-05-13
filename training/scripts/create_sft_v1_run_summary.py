#!/usr/bin/env python3
"""Create a sanitized Kimari Runtime 1.5B SFT v1 run summary."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[2]


def parse_simple_yaml(path: Path) -> dict[str, Any]:
    """Parse the simple key/value YAML used by the SFT v1 config."""
    data: dict[str, Any] = {}
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or ":" not in line:
            continue
        key, _, raw_value = line.partition(":")
        value = raw_value.strip().strip('"').strip("'")
        lowered = value.lower()
        if lowered == "true":
            parsed: Any = True
        elif lowered == "false":
            parsed = False
        elif lowered in {"null", "~"}:
            parsed = None
        else:
            parsed = parse_scalar(value)
        data[key.strip()] = parsed
    return data


def parse_scalar(value: str) -> Any:
    try:
        return int(value)
    except ValueError:
        try:
            return float(value)
        except ValueError:
            return value


def project_path(path_value: str) -> Path:
    path = Path(path_value)
    if path.is_absolute():
        return path
    return PROJECT_ROOT / path


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def parse_bool(value: str | bool) -> bool:
    if isinstance(value, bool):
        return value
    normalized = value.strip().lower()
    if normalized in {"1", "true", "yes", "y", "pass", "passed", "success"}:
        return True
    if normalized in {"0", "false", "no", "n", "fail", "failed", "blocked"}:
        return False
    raise argparse.ArgumentTypeError(f"expected boolean-like value, got: {value}")


def nullable_float(value: str) -> float | None:
    if value.strip().lower() in {"", "none", "null", "n/a", "na"}:
        return None
    return float(value)


def build_summary(args: argparse.Namespace) -> dict[str, Any]:
    config_path = Path(args.config).resolve()
    config = parse_simple_yaml(config_path)
    train_path = project_path(str(config.get("dataset_train", "")))
    validation_path = project_path(str(config.get("dataset_validation", "")))

    status = str(args.status).strip()
    completed = status.lower() == "completed"
    adapter_hash = str(args.adapter_hash).strip()

    return {
        "run_id": str(config.get("run_id", "")),
        "job_id": str(args.job_id).strip(),
        "status": status,
        "base_model": str(args.base_model or config.get("base_model", "")),
        "base_license": str(config.get("base_license", "")),
        "dataset_train_sha256": sha256_file(train_path),
        "dataset_validation_sha256": sha256_file(validation_path),
        "config_path": str(
            config_path.relative_to(PROJECT_ROOT) if config_path.is_relative_to(PROJECT_ROOT) else config_path
        ),
        "method": str(config.get("method", "qlora")),
        "max_steps": int(config.get("max_steps", 100)),
        "gpu_type": str(args.gpu_type).strip(),
        "steps_completed": int(args.steps_completed),
        "final_loss": args.final_loss,
        "training_performed": completed,
        "adapter_generated": completed,
        "adapter_persisted_private": bool(adapter_hash),
        "adapter_private_repo": "",
        "adapter_hash": adapter_hash,
        "adapter_size_bytes": int(args.adapter_size),
        "adapter_load_check": bool(args.adapter_load_check),
        "generation_success": bool(args.generation_success),
        "adapter_committed_public": False,
        "hf_public_upload_performed": False,
        "gguf_generated": False,
        "raw_logs_committed": False,
        "public_benchmark_allowed": False,
        "gate_state": "BLOCKED",
        "manual_review_required": True,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--summary", required=True, help="Output summary JSON path")
    parser.add_argument("--config", required=True, help="SFT v1 config YAML path")
    parser.add_argument("--job-id", required=True)
    parser.add_argument("--status", required=True)
    parser.add_argument("--base-model", required=True)
    parser.add_argument("--steps-completed", required=True, type=int)
    parser.add_argument("--final-loss", required=True, type=nullable_float)
    parser.add_argument("--gpu-type", required=True)
    parser.add_argument("--adapter-hash", default="")
    parser.add_argument("--adapter-size", default=0, type=int)
    parser.add_argument("--adapter-load-check", default=False, type=parse_bool)
    parser.add_argument("--generation-success", default=False, type=parse_bool)
    parser.add_argument("--json", action="store_true", help="Print created summary JSON to stdout")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    summary = build_summary(args)
    summary_path = Path(args.summary)
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    summary_path.write_text(json.dumps(summary, indent=2, sort_keys=False) + "\n", encoding="utf-8")
    if args.json:
        print(json.dumps(summary, indent=2, sort_keys=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
