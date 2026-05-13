#!/usr/bin/env python3
"""Validate public GitHub/Hugging Face version consistency.

This checker intentionally focuses on public-facing current surfaces, not full
historical docs. Historical changelog/roadmap entries may mention older versions,
but active public pages must show the package version from pyproject.toml.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import sys
from pathlib import Path

try:
    import tomllib
except ModuleNotFoundError:  # Python 3.10 compatibility
    import tomli as tomllib

PROJECT_ROOT = Path(__file__).resolve().parents[2]
TODAY = dt.date(2026, 5, 13)
PUBLIC_FILES = [
    Path("README.md"),
    Path("docs/index.html"),
    Path("docs/HUGGINGFACE_ORG_CARD.md"),
    Path("huggingface/kimari-fit-lab/README.md"),
    Path("docs/HUGGINGFACE_DEPLOYMENT_STATUS.md"),
]
FORBIDDEN_ACTIVE_PATTERNS = [
    "Kimari-4B released",
    "public weights available",
    "production ready",
]
STALE_ACTIVE_PATTERNS = [
    "Kimari Local AI v0.1.28-alpha",
    "New in v0.1.28-alpha",
    "v0.1.29-alpha FOCUS",
]


def read_version() -> str:
    data = tomllib.loads((PROJECT_ROOT / "pyproject.toml").read_text())
    return data["project"]["version"]


def init_version() -> str:
    text = (PROJECT_ROOT / "kimari" / "__init__.py").read_text()
    match = re.search(r'__version__\s*=\s*["\']([^"\']+)["\']', text)
    return match.group(1) if match else ""


def future_changelog_dates() -> list[str]:
    findings = []
    changelog = PROJECT_ROOT / "CHANGELOG.md"
    for line_no, line in enumerate(changelog.read_text().splitlines(), start=1):
        for y, m, d in re.findall(r"(20\d{2})-(\d{2})-(\d{2})", line):
            date = dt.date(int(y), int(m), int(d))
            if date > TODAY:
                findings.append(f"CHANGELOG.md:{line_no}: future date {date}: {line.strip()}")
    return findings


def public_version_findings(version: str) -> list[str]:
    findings = []
    v_version = f"v{version}"
    badge = f"version-{version.replace('-', '--')}"
    for rel in PUBLIC_FILES:
        path = PROJECT_ROOT / rel
        text = path.read_text()
        if v_version not in text and version not in text:
            findings.append(f"{rel}: missing current version {v_version}")
        for pattern in FORBIDDEN_ACTIVE_PATTERNS + STALE_ACTIVE_PATTERNS:
            if pattern.lower() in text.lower():
                findings.append(f"{rel}: forbidden/stale active phrase: {pattern}")
        if rel == Path("README.md") and badge not in text:
            findings.append(f"README.md: badge does not use {badge}")
    return findings


def safety_findings() -> list[str]:
    findings = []
    combined = "\n".join((PROJECT_ROOT / rel).read_text() for rel in PUBLIC_FILES).lower()
    if "kimari-4b is not released" not in combined and "kimari-4b is **not released" not in combined:
        findings.append("public files must explicitly state Kimari-4B is not released")
    if "blocked" not in combined:
        findings.append("public files must mention gate BLOCKED")
    return findings


def main() -> int:
    parser = argparse.ArgumentParser(description="Check public version consistency")
    parser.add_argument("--json", action="store_true", help="Emit JSON")
    args = parser.parse_args()

    version = read_version()
    errors = []
    if init_version() != version:
        errors.append(f"kimari/__init__.py version {init_version()!r} != pyproject {version!r}")
    errors.extend(public_version_findings(version))
    errors.extend(future_changelog_dates())
    errors.extend(safety_findings())

    payload = {
        "valid": not errors,
        "version": version,
        "errors": errors,
        "checked_files": [str(p) for p in PUBLIC_FILES],
    }
    if args.json:
        print(json.dumps(payload, indent=2))
    else:
        if errors:
            print("Public version consistency: FAIL")
            for error in errors:
                print(f"  FAIL: {error}")
        else:
            print(f"Public version consistency: OK ({version})")
    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main())
