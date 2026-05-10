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
        if line.startswith("version") and "python" not in line.lower():
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
    print("\n[1/12] Version consistency")
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
    print("\n[2/12] README version badge")
    readme = PROJECT_ROOT / "README.md"
    readme_text = readme.read_text()
    check("README.md exists", readme.exists())
    badge_ver = f"v{init_ver}"
    check(
        "README badge mentions current version",
        badge_ver in readme_text or init_ver in readme_text,
        f"version {init_ver!r} not found in README.md",
    )
    check(
        "README links to Release Checklist",
        "RELEASE_CHECKLIST.md" in readme_text,
        "RELEASE_CHECKLIST.md link not found in README.md",
    )

    # ── CHANGELOG entry ──────────────────────────────────────────
    print("\n[3/12] CHANGELOG entry")
    changelog = PROJECT_ROOT / "CHANGELOG.md"
    changelog_text = changelog.read_text()
    changelog_header = f"[{init_ver}]"
    check(
        "CHANGELOG.md has entry for current version",
        changelog_header in changelog_text,
        f"'{changelog_header}' not found in CHANGELOG.md",
    )

    # ── ROADMAP entry ────────────────────────────────────────────
    print("\n[4/12] ROADMAP entry")
    roadmap = PROJECT_ROOT / "ROADMAP.md"
    roadmap_text = roadmap.read_text()
    check(
        "ROADMAP.md mentions current version",
        init_ver in roadmap_text,
        f"version {init_ver!r} not found in ROADMAP.md",
    )
    check(
        "ROADMAP marks current version",
        "Current" in roadmap_text and init_ver in roadmap_text,
        "current version not marked as 'Current' in ROADMAP.md",
    )

    # ── Config defaults ──────────────────────────────────────────
    print("\n[5/12] Config defaults")
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

    # ── Package markers ─────────────────────────────────────────
    print("\n[6/12] Package markers")
    py_typed = PROJECT_ROOT / "kimari" / "py.typed"
    check("kimari/py.typed exists", py_typed.exists(), "PEP 561 marker missing")

    # ── GitHub Pages / SEO ──────────────────────────────────────
    print("\n[7/12] GitHub Pages / SEO")
    index_html = PROJECT_ROOT / "docs" / "index.html"
    if index_html.exists():
        index_text = index_html.read_text()
        check(
            "docs/index.html contains current version",
            init_ver in index_text,
            f"version {init_ver!r} not found in docs/index.html",
        )
        check(
            "docs/index.html has canonical URL",
            "canonical" in index_text,
            "canonical link not found in docs/index.html",
        )
        check(
            "docs/index.html has og:title",
            "og:title" in index_text,
            "Open Graph title not found in docs/index.html",
        )
        check(
            "docs/index.html has og:image",
            "og:image" in index_text,
            "Open Graph image not found in docs/index.html",
        )
    else:
        check("docs/index.html exists", False, "file not found")

    # ── Documentation files ─────────────────────────────────────
    print("\n[8/12] Documentation files")
    check(
        "docs/INSTALL_WSL2.md exists",
        (PROJECT_ROOT / "docs" / "INSTALL_WSL2.md").exists(),
        "WSL2 installation guide missing",
    )
    check(
        "docs/PUBLISHING.md exists",
        (PROJECT_ROOT / "docs" / "PUBLISHING.md").exists(),
        "Publishing guide missing",
    )
    check(
        "RELEASE_CHECKLIST.md exists",
        (PROJECT_ROOT / "RELEASE_CHECKLIST.md").exists(),
        "Release checklist missing",
    )

    # ── No tracked GGUF / runtime artifacts ──────────────────────
    print("\n[9/12] No unwanted tracked files")
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

    # ── No false claims ─────────────────────────────────────────
    print("\n[10/12] Content integrity")
    readme_lower = readme_text.lower()
    changelog_lower = changelog_text.lower()
    index_lower = (PROJECT_ROOT / "docs" / "index.html").read_text().lower() if index_html.exists() else ""

    # Check that Kimari-4B is not claimed as released
    # These patterns should NOT appear (they claim the model exists/is available)
    k4b_false_patterns = [
        "kimari-4b is available now",
        "kimari-4b can be downloaded",
        "download kimari-4b",
        "kimari-4b weights available",
        "kimari-4b has been released",
    ]
    all_text = f"{readme_lower} {changelog_lower} {index_lower}"
    false_claims = [p for p in k4b_false_patterns if p in all_text]
    check(
        "No 'Kimari-4B released' false claim",
        len(false_claims) == 0,
        f"found false claims: {false_claims}",
    )

    # Check that no file claims "Responses API supported" (case insensitive)
    # It should only say "planned" or "future"
    responses_api_false_patterns = [
        "responses api supported",
        "responses api is supported",
    ]
    responses_false_claims = [p for p in responses_api_false_patterns if p in all_text]
    check(
        "No 'Responses API supported' false claim",
        len(responses_false_claims) == 0,
        f"found false claims: {responses_false_claims} — should only say 'planned' or 'future'",
    )

    # Check that README mentions optimize and perf commands
    check(
        "README mentions 'optimize' command",
        "optimize" in readme_lower,
        "'optimize' not found in README.md",
    )
    check(
        "README mentions 'perf' command",
        "perf" in readme_lower,
        "'perf' not found in README.md",
    )

    # ── Integration documentation ──────────────────────────────────
    print("\n[11/12] Integration documentation")
    check(
        "docs/integrations/OPENCLAW.md exists",
        (PROJECT_ROOT / "docs" / "integrations" / "OPENCLAW.md").exists(),
        "OpenClaw integration doc missing",
    )
    check(
        "docs/integrations/HERMES.md exists",
        (PROJECT_ROOT / "docs" / "integrations" / "HERMES.md").exists(),
        "Hermes integration doc missing",
    )
    check(
        "docs/integrations/CONTINUE.md exists",
        (PROJECT_ROOT / "docs" / "integrations" / "CONTINUE.md").exists(),
        "Continue integration doc missing",
    )
    check(
        "docs/integrations/OPENAI_COMPATIBLE_CLIENTS.md exists",
        (PROJECT_ROOT / "docs" / "integrations" / "OPENAI_COMPATIBLE_CLIENTS.md").exists(),
        "OpenAI compatible clients integration doc missing",
    )
    check(
        "config/integrations/ directory exists",
        (PROJECT_ROOT / "config" / "integrations").is_dir(),
        "config/integrations/ directory missing",
    )
    check(
        "config/integrations/openclaw.kimari.example.json exists",
        (PROJECT_ROOT / "config" / "integrations" / "openclaw.kimari.example.json").exists(),
        "OpenClaw example config missing",
    )

    # ── Performance module ─────────────────────────────────────────
    print("\n[12/12] Performance module")
    check(
        "kimari/performance/__init__.py exists",
        (PROJECT_ROOT / "kimari" / "performance" / "__init__.py").exists(),
        "Performance module init missing",
    )
    check(
        "kimari/performance/estimator.py exists",
        (PROJECT_ROOT / "kimari" / "performance" / "estimator.py").exists(),
        "VRAM/RAM estimator missing",
    )
    check(
        "kimari/performance/recommender.py exists",
        (PROJECT_ROOT / "kimari" / "performance" / "recommender.py").exists(),
        "Settings recommender missing",
    )
    check(
        "kimari/performance/gguf_metadata.py exists",
        (PROJECT_ROOT / "kimari" / "performance" / "gguf_metadata.py").exists(),
        "GGUF metadata reader missing",
    )

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
