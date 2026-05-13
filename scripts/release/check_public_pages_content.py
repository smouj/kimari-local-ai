#!/usr/bin/env python3
"""Check that docs/index.html contains correct version and no stale versions."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
INDEX = ROOT / "docs" / "index.html"


def main():
    content = INDEX.read_text()
    errors = []
    ok = []

    # Read version from pyproject.toml
    import re

    pyproject = (ROOT / "pyproject.toml").read_text()
    m = re.search(r'version\s*=\s*"([^"]+)"', pyproject)
    if not m:
        errors.append("Cannot find version in pyproject.toml")
        sys.exit(1)
    version = m.group(1)
    version_v = f"v{version}"

    ok.append(f"Current version: {version_v}")

    # Check index.html contains current version
    if version_v in content:
        ok.append(f"index.html contains {version_v} ✓")
    else:
        errors.append(f"index.html does NOT contain {version_v}")

    # Check no stale version references as "current"
    stale_versions = ["v0.1.39", "v0.1.28", "v0.1.21", "v0.1.16"]
    for sv in stale_versions:
        if sv in content:
            # Allow in changelog/history sections only
            # Simple check: if it appears in the visible "hero" or "status" section
            lines = content.split("\n")
            for i, line in enumerate(lines):
                if sv in line and "terminal-highlight" in line:
                    errors.append(
                        f"Stale version {sv} appears as highlighted/visible in line {i + 1}: {line.strip()[:100]}"
                    )

    # Check key content
    checks = {
        "Kimari-4B Not Released": "Kimari-4B" in content
        and ("Not Released" in content or "not released" in content.lower()),
        "Gate BLOCKED": "BLOCKED" in content,
        "HF Space link": "kimari-ai/kimari-fit-lab" in content,
        "GitHub link": "smouj/kimari-local-ai" in content,
        "No public weights claim": "No public weights" in content or "not released" in content.lower(),
    }
    for label, passed in checks.items():
        if passed:
            ok.append(f"  {label} ✓")
        else:
            errors.append(f"  {label} ✗")

    print("\n".join(ok))
    if errors:
        print("\nERRORS:")
        print("\n".join(f"  - {e}" for e in errors))
        sys.exit(1)
    else:
        print("\nPublic pages content check: OK")
        sys.exit(0)


if __name__ == "__main__":
    main()
