#!/usr/bin/env python3
"""Package private adapter artifacts for Kimari-4B.

Defaults to dry-run. Use --write --yes to actually write files.
Never commits to the public repo.

Usage:
    # Dry-run (default)
    python training/scripts/package_private_adapter.py --source /tmp/kimari4b-micro-sft-adapter

    # Write to private repo
    python training/scripts/package_private_adapter.py --source /tmp/kimari4b-micro-sft-adapter --write --yes
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

PRIVATE_REPO = Path.home() / ".openclaw" / "workspace" / "kimari-4b-artifacts"
ALLOWED_EXTENSIONS = {".safetensors", ".json", ".txt", ".md"}
FORBIDDEN_PATTERNS = ["sk-", "api_key", "password", "credential", "/home/", ".bin", ".pt", ".pth", ".gguf"]


def compute_file_hash(filepath: Path) -> str:
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def scan_for_secrets(path: Path) -> list[str]:
    """Check a file for forbidden patterns."""
    findings = []
    try:
        content = path.read_text(errors="ignore").lower()
        for pattern in FORBIDDEN_PATTERNS:
            if pattern in content:
                findings.append(f"{path.name}: found '{pattern}'")
    except Exception:
        pass
    return findings


def package_adapter(source: str, write: bool = False) -> dict:
    """Analyze and optionally package adapter artifacts."""
    src = Path(source)
    if not src.exists():
        return {"error": f"Source not found: {source}", "files_found": 0}

    result = {
        "source": str(src),
        "files_found": 0,
        "files": [],
        "total_bytes": 0,
        "secrets_found": [],
        "adapter_committed": False,
        "adapter_file": None,
        "hashes": {},
    }

    for f in sorted(src.rglob("*")):
        if not f.is_file():
            continue
        if f.suffix not in ALLOWED_EXTENSIONS:
            continue

        result["files_found"] += 1
        file_hash = compute_file_hash(f)
        result["total_bytes"] += f.stat().st_size
        result["hashes"][f.name] = file_hash

        secrets = scan_for_secrets(f)
        result["secrets_found"].extend(secrets)

        file_info = {
            "name": f.name,
            "size": f.stat().st_size,
            "hash": file_hash,
            "extension": f.suffix,
        }

        if f.name == "adapter_model.safetensors":
            result["adapter_file"] = str(f)
            file_info["is_adapter"] = True

        result["files"].append(file_info)

    if write and not result["secrets_found"]:
        dest = PRIVATE_REPO / "adapters" / "kimari4b-micro-sft-adapter-v0"
        dest.mkdir(parents=True, exist_ok=True)
        import shutil

        for f in src.rglob("*"):
            if f.is_file() and f.suffix in ALLOWED_EXTENSIONS:
                shutil.copy2(f, dest / f.name)
        result["adapter_committed"] = False  # Never commit to public repo
        result["written_to"] = str(dest)

    return result


def main() -> None:
    parser = argparse.ArgumentParser(description="Package private adapter artifacts")
    parser.add_argument("--source", required=True, help="Path to adapter directory")
    parser.add_argument("--write", action="store_true", help="Write files to private repo")
    parser.add_argument("--yes", action="store_true", help="Confirm write operation")
    parser.add_argument("--json", action="store_true", help="JSON output")
    args = parser.parse_args()

    if args.write and not args.yes:
        print("ERROR: --write requires --yes for confirmation")
        sys.exit(1)

    result = package_adapter(args.source, write=args.write)

    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print(f"Source: {result.get('source', 'N/A')}")
        print(f"Files found: {result.get('files_found', 0)}")
        print(f"Total bytes: {result.get('total_bytes', 0)}")
        print(f"Secrets found: {len(result.get('secrets_found', []))}")
        if result.get("adapter_file"):
            print(f"Adapter file: {result['adapter_file']}")
        if result.get("secrets_found"):
            print("WARNING: Secrets found!")
            for s in result["secrets_found"]:
                print(f"  {s}")
        if args.write:
            print(f"Written to: {result.get('written_to', 'N/A')}")


if __name__ == "__main__":
    main()
