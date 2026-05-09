#!/usr/bin/env python3
"""
Kimari Local AI — Release Validation Script

Checks that all release hygiene requirements are met before publishing.
Exits with code 0 on success, 1 on any failure.

Usage:
    python scripts/release/check-release.py
"""

import json
import subprocess
import sys
from pathlib import Path

# Resolve project root (three levels up from this script)
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
ERRORS: list[str] = []
WARNINGS: list[str] = []


def check(name: str, condition: bool, detail: str = "") -> None:
    """Record a check result."""
    if condition:
        print(f"  [OK]   {name}")
    else:
        msg = f"  [FAIL] {name}"
        if detail:
            msg += f" — {detail}"
        print(msg)
        ERRORS.append(name)


def warn(name: str, detail: str = "") -> None:
    """Record a warning (non-blocking)."""
    msg = f"  [WARN] {name}"
    if detail:
        msg += f" — {detail}"
    print(msg)
    WARNINGS.append(name)


def get_pyproject_version() -> str:
    """Extract version from pyproject.toml without toml dependency."""
    pyproject = PROJECT_ROOT / "pyproject.toml"
    for line in pyproject.read_text().splitlines():
        line = line.strip()
        if line.startswith("version"):
            # version = "0.1.8-alpha"
            return line.split("=", 1)[1].strip().strip('"').strip("'")
    return ""


def get_init_version() -> str:
    """Extract __version__ from kimari/__init__.py."""
    init_file = PROJECT_ROOT / "kimari" / "__init__.py"
    for line in init_file.read_text().splitlines():
        line = line.strip()
        if line.startswith("__version__"):
            return line.split("=", 1)[1].strip().strip('"').strip("'")
    return ""


def main() -> None:
    print("Kimari Local AI — Release Validation")
    print("=" * 50)

    # ── Version consistency ──────────────────────────────────────
    print("\n[1/7] Version consistency")
    pyproject_ver = get_pyproject_version()
    init_ver = get_init_version()
    check("pyproject.toml version is set", bool(pyproject_ver), "version field is empty")
    check("kimari/__init__.py version is set", bool(init_ver), "__version__ is empty")
    check(
        "pyproject.toml == kimari/__version__",
        pyproject_ver == init_ver,
        f"pyproject={pyproject_ver!r} != init={init_ver!r}",
    )

    # ── README version badge ─────────────────────────────────────
    print("\n[2/7] README version badge")
    readme = PROJECT_ROOT / "README.md"
    readme_text = readme.read_text()
    check("README.md exists", readme.exists())
    badge_ver = f"v{init_ver}"
    check(
        "README badge mentions current version",
        badge_ver in readme_text or init_ver in readme_text,
        f"version {init_ver!r} not found in README.md",
    )

    # ── CHANGELOG entry ──────────────────────────────────────────
    print("\n[3/7] CHANGELOG entry")
    changelog = PROJECT_ROOT / "CHANGELOG.md"
    changelog_text = changelog.read_text()
    # Look for heading like ## [0.1.8-alpha]
    changelog_header = f"[{init_ver}]"
    check(
        "CHANGELOG.md has entry for current version",
        changelog_header in changelog_text,
        f"'{changelog_header}' not found in CHANGELOG.md",
    )

    # ── ROADMAP entry ────────────────────────────────────────────
    print("\n[4/7] ROADMAP entry")
    roadmap = PROJECT_ROOT / "ROADMAP.md"
    roadmap_text = roadmap.read_text()
    check(
        "ROADMAP.md mentions current version",
        init_ver in roadmap_text,
        f"version {init_ver!r} not found in ROADMAP.md",
    )

    # ── Config defaults ──────────────────────────────────────────
    print("\n[5/7] Config defaults")
    profiles_path = PROJECT_ROOT / "config" / "kimari.profiles.json"
    if profiles_path.exists():
        profiles = json.loads(profiles_path.read_text())
        default_profile = profiles.get("default_profile", "")
        check(
            'default_profile == "test"',
            default_profile == "test",
            f"default_profile is {default_profile!r}, expected 'test'",
        )
    else:
        check("config/kimari.profiles.json exists", False, "file not found")

    # ── py.typed ─────────────────────────────────────────────────
    print("\n[6/7] Package markers")
    py_typed = PROJECT_ROOT / "kimari" / "py.typed"
    check("kimari/py.typed exists", py_typed.exists(), "PEP 561 marker missing")

    # ── No tracked GGUF / runtime artifacts ──────────────────────
    print("\n[7/7] No unwanted tracked files")
    forbidden_patterns = [".kimari/", "kimari-server.log", ".kimari-server.pid"]
    # Check for GGUF files tracked in git
    try:
        result = subprocess.run(
            ["git", "ls-files", "*.gguf"],
            capture_output=True,
            text=True,
            cwd=str(PROJECT_ROOT),
        )
        gguf_files = [f for f in result.stdout.strip().splitlines() if f]
        check("No GGUF files tracked in git", len(gguf_files) == 0, f"found: {gguf_files}")
    except Exception:
        warn("Could not check git tracked GGUF files", "git not available or not a repo")

    # Check models registry for unsafe paths
    models_path = PROJECT_ROOT / "config" / "kimari.models.json"
    if models_path.exists():
        models_data = json.loads(models_path.read_text())
        unsafe_paths = []
        for m in models_data.get("models", []):
            target = m.get("target_path", "")
            if target.startswith("/") or ".." in target:
                unsafe_paths.append(f"{m.get('id', '?')}: {target}")
        check(
            "No unsafe paths in models registry",
            len(unsafe_paths) == 0,
            f"unsafe: {unsafe_paths}",
        )
    else:
        warn("config/kimari.models.json not found", "skipping model path check")

    # Check no runtime artifacts in project root
    for artifact in ["kimari-server.log", ".kimari-server.pid"]:
        artifact_path = PROJECT_ROOT / artifact
        if artifact_path.exists():
            warn(f"{artifact} exists in project root", "should be in .gitignore")

    # Check .kimari directory not tracked
    kimari_dir = PROJECT_ROOT / ".kimari"
    if kimari_dir.exists():
        warn(".kimari/ directory exists in project root", "should be in .gitignore")

    # ── Summary ──────────────────────────────────────────────────
    print("\n" + "=" * 50)
    if ERRORS:
        print(f"RESULT: {len(ERRORS)} error(s), {len(WARNINGS)} warning(s)")
        for e in ERRORS:
            print(f"  FAIL: {e}")
        sys.exit(1)
    else:
        print(f"RESULT: All checks passed! ({len(WARNINGS)} warning(s))")
        for w in WARNINGS:
            print(f"  WARN: {w}")
        sys.exit(0)


if __name__ == "__main__":
    main()
