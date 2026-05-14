#!/usr/bin/env python3
"""Validate private Kimari eval artifacts without exposing raw content."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[2]
RAW_NAME = "raw_outputs_private.json"


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def artifact_uri(repo_id: str, artifact_path: str) -> str:
    clean = artifact_path.strip("/")
    if clean.endswith(RAW_NAME):
        return f"hf://buckets/{repo_id}/{clean}"
    return f"hf://buckets/{repo_id}/{clean}/{RAW_NAME}" if clean else f"hf://buckets/{repo_id}/{RAW_NAME}"


def public_repo_has_raw() -> bool:
    proc = subprocess.run(
        ["git", "ls-files"], cwd=PROJECT_ROOT, capture_output=True, text=True, timeout=30, check=False
    )
    return proc.returncode == 0 and any(Path(line).name == RAW_NAME for line in proc.stdout.splitlines())


def validate(args: argparse.Namespace) -> dict[str, Any]:
    uri = artifact_uri(args.repo_id, args.artifact_path)
    result: dict[str, Any] = {
        "artifact_exists": False,
        "artifact_name": RAW_NAME,
        "private_artifact_path": uri,
        "size_bytes": 0,
        "sha256": None,
        "sha256_matches": False,
        "raw_outputs_publicly_tracked": public_repo_has_raw(),
        "manual_review_available": False,
    }

    if args.local_path:
        local = args.local_path.expanduser().resolve()
        if not local.exists() or local.name != RAW_NAME:
            return result
        result["artifact_exists"] = True
        result["size_bytes"] = local.stat().st_size
        digest = sha256_file(local)
        result["sha256"] = digest
        result["sha256_matches"] = not args.expected_sha256 or digest == args.expected_sha256
        result["manual_review_available"] = bool(
            result["size_bytes"] > 0 and result["sha256_matches"] and not result["raw_outputs_publicly_tracked"]
        )
        return result

    with tempfile.TemporaryDirectory(prefix="kimari-private-artifact-") as tmp:
        tmp_path = Path(tmp)
        proc = subprocess.run(
            ["hf", "buckets", "cp", uri, str(tmp_path / RAW_NAME)],
            capture_output=True,
            text=True,
            timeout=args.timeout_seconds,
            check=False,
        )
        local = tmp_path / RAW_NAME
        if proc.returncode != 0 or not local.exists():
            result["error"] = (proc.stderr or proc.stdout)[-1000:]
            return result
        result["artifact_exists"] = True
        result["size_bytes"] = local.stat().st_size
        digest = sha256_file(local)
        result["sha256"] = digest
        result["sha256_matches"] = not args.expected_sha256 or digest == args.expected_sha256
        result["manual_review_available"] = bool(
            result["size_bytes"] > 0 and result["sha256_matches"] and not result["raw_outputs_publicly_tracked"]
        )
        return result


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate private eval raw output artifact")
    parser.add_argument("--repo-id", required=True)
    parser.add_argument("--artifact-path", required=True)
    parser.add_argument("--expected-sha256")
    parser.add_argument("--local-path", type=Path, help="Optional private local file for validation without download")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--timeout-seconds", type=int, default=120)
    args = parser.parse_args()

    result = validate(args)
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(result)
    return 0 if result.get("manual_review_available") else 1


if __name__ == "__main__":
    sys.exit(main())
