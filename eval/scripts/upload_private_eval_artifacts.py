#!/usr/bin/env python3
"""Upload private Kimari eval artifacts and emit sanitized metadata.

Safety invariants:
- raw outputs must live outside the public repository
- no token CLI argument is accepted; HF_TOKEN/HF cache auth is used by hf CLI
- upload failures exit non-zero
- output contains only path/hash/size metadata, never raw content
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[2]


def is_inside(path: Path, parent: Path) -> bool:
    try:
        path.resolve().relative_to(parent.resolve())
        return True
    except ValueError:
        return False


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def build_bucket_uri(repo_id: str, artifact_path: str, filename: str) -> str:
    prefix = artifact_path.strip("/")
    return f"hf://buckets/{repo_id}/{prefix}/{filename}" if prefix else f"hf://buckets/{repo_id}/{filename}"


def upload(args: argparse.Namespace) -> dict[str, Any]:
    raw_path = args.raw_output_path.expanduser().resolve()
    if not raw_path.exists():
        raise SystemExit(f"raw output file not found: {raw_path}")
    if raw_path.name != "raw_outputs_private.json":
        raise SystemExit("raw output filename must be raw_outputs_private.json")
    if is_inside(raw_path, PROJECT_ROOT):
        raise SystemExit("raw output path must be outside the public repository")
    if raw_path.stat().st_size <= 0:
        raise SystemExit("raw output file must be non-empty")

    digest = sha256_file(raw_path)
    size = raw_path.stat().st_size
    private_uri = build_bucket_uri(args.repo_id, args.artifact_path, raw_path.name)

    if args.dry_run:
        return {
            "uploaded": False,
            "dry_run": True,
            "private_artifact_path": private_uri,
            "sha256": digest,
            "size_bytes": size,
            "raw_outputs_committed": False,
        }

    cmd = ["hf", "buckets", "cp", str(raw_path), private_uri]
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=args.timeout_seconds, check=False)
    if proc.returncode != 0:
        return {
            "uploaded": False,
            "dry_run": False,
            "private_artifact_path": private_uri,
            "sha256": digest,
            "size_bytes": size,
            "error": (proc.stderr or proc.stdout)[-1000:],
            "raw_outputs_committed": False,
        }

    return {
        "uploaded": True,
        "dry_run": False,
        "private_artifact_path": private_uri,
        "sha256": digest,
        "size_bytes": size,
        "raw_outputs_committed": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Upload private eval raw outputs to an HF bucket")
    parser.add_argument("--raw-output-path", required=True, type=Path)
    parser.add_argument("--repo-id", required=True, help="HF bucket id, e.g. Smouj013/jobs-artifacts")
    parser.add_argument("--artifact-path", required=True, help="Private bucket prefix")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--timeout-seconds", type=int, default=120)
    args = parser.parse_args()

    result = upload(args)
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(result)
    return 0 if result.get("uploaded") or args.dry_run else 1


if __name__ == "__main__":
    sys.exit(main())
