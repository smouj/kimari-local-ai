#!/usr/bin/env python3
"""Validate private artifact repo structure for Kimari-4B.

Checks that the private repo has the expected structure,
no forbidden files, and proper LFS configuration.

Usage:
    python training/scripts/validate_private_artifact_repo.py --json
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PRIVATE_REPO = Path.home() / ".openclaw" / "workspace" / "kimari-4b-artifacts"
EXPECTED_DIRS = ["adapters", "training/results", "eval/baselines", "eval/comparisons"]
EXPECTED_FILES = ["README.md", ".gitattributes", ".gitignore"]
FORBIDDEN_EXTENSIONS = [".gguf", ".bin", ".pt", ".pth"]
FORBIDDEN_PATTERNS = ["sk-", "api_key", "password", "credential"]


def validate_repo() -> dict:
    """Validate private artifact repo structure."""
    errors = []
    warnings = []

    if not PRIVATE_REPO.exists():
        return {"valid": False, "errors": [f"Private repo not found: {PRIVATE_REPO}"], "warnings": []}

    # Check expected directories
    for d in EXPECTED_DIRS:
        dir_path = PRIVATE_REPO / d
        if not dir_path.exists():
            warnings.append(f"Missing directory: {d} (will be created on first use)")

    # Check expected files
    for f in EXPECTED_FILES:
        file_path = PRIVATE_REPO / f
        if not file_path.exists():
            errors.append(f"Missing file: {f}")

    # Check .gitattributes has LFS for safetensors
    gitattr = PRIVATE_REPO / ".gitattributes"
    if gitattr.exists():
        content = gitattr.read_text()
        if "*.safetensors" not in content:
            errors.append(".gitattributes missing LFS for *.safetensors")

    # Check for forbidden files
    for f in PRIVATE_REPO.rglob("*"):
        if f.is_file() and f.suffix in FORBIDDEN_EXTENSIONS:
            errors.append(f"Forbidden file: {f.name} ({f.suffix})")

    # Check for secrets
    for f in PRIVATE_REPO.rglob("*.md"):
        try:
            content = f.read_text().lower()
            for pattern in FORBIDDEN_PATTERNS:
                if pattern in content and pattern not in ["no tokens", "no private data", "no secret", "forbidden"]:
                    warnings.append(f"Potential secret pattern in {f.name}: {pattern}")
        except Exception:
            pass

    # Check .gitignore
    gitignore = PRIVATE_REPO / ".gitignore"
    if gitignore.exists():
        content = gitignore.read_text()
        if "*.gguf" not in content:
            warnings.append(".gitignore missing *.gguf")

    # Check no safetensors in public repo
    public_repo = Path.home() / ".openclaw" / "workspace" / "kimari-local-ai"
    for f in public_repo.rglob("*.safetensors"):
        if ".git" not in str(f) and "node_modules" not in str(f):
            errors.append(f"safetensors in public repo: {f.relative_to(public_repo)}")

    return {"valid": len(errors) == 0, "errors": errors, "warnings": warnings}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    result = validate_repo()
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        for e in result["errors"]:
            print(f"  FAIL: {e}")
        for w in result["warnings"]:
            print(f"  WARN: {w}")
        print("RESULT:", "All checks passed!" if result["valid"] else f"{len(result['errors'])} error(s)")
    sys.exit(0 if result["valid"] else 1)


if __name__ == "__main__":
    main()
