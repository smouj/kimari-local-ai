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
    print("\n[1/15] Version consistency")
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
    print("\n[2/13] README version badge")
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
    print("\n[3/13] CHANGELOG entry")
    changelog = PROJECT_ROOT / "CHANGELOG.md"
    changelog_text = changelog.read_text()
    changelog_header = f"[{init_ver}]"
    check(
        "CHANGELOG.md has entry for current version",
        changelog_header in changelog_text,
        f"'{changelog_header}' not found in CHANGELOG.md",
    )

    # ── ROADMAP entry ────────────────────────────────────────────
    print("\n[4/13] ROADMAP entry")
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
    print("\n[5/13] Config defaults")
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
    print("\n[6/13] Package markers")
    py_typed = PROJECT_ROOT / "kimari" / "py.typed"
    check("kimari/py.typed exists", py_typed.exists(), "PEP 561 marker missing")

    # ── GitHub Pages / SEO ──────────────────────────────────────
    print("\n[7/13] GitHub Pages / SEO")
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
        check(
            "docs/index.html mentions 'setup'",
            "setup" in index_text.lower(),
            "'setup' not found in docs/index.html",
        )
        check(
            "docs/index.html mentions 'strict-flags'",
            "strict-flags" in index_text.lower(),
            "'strict-flags' not found in docs/index.html",
        )
        check(
            "docs/index.html mentions 'token'",
            "token" in index_text.lower(),
            "'token' not found in docs/index.html",
        )
    else:
        check("docs/index.html exists", False, "file not found")

    # ── Documentation files ─────────────────────────────────────
    print("\n[8/13] Documentation files")
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
    print("\n[9/13] No unwanted tracked files")
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
    print("\n[10/13] Content integrity")
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

    check(
        "README mentions 'setup' command",
        "setup" in readme_lower,
        "'setup' not found in README.md",
    )
    check(
        "README mentions 'strict-flags'",
        "strict-flags" in readme_lower,
        "'strict-flags' not found in README.md",
    )
    check(
        "README mentions 'token create'",
        "token create" in readme_lower,
        "'token create' not found in README.md",
    )

    # ── Integration documentation ──────────────────────────────────
    print("\n[11/13] Integration documentation")
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
    print("\n[12/13] Performance module")
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

    # ── Runtime & Security modules ──────────────────────────────────
    print("\n[13/15] Runtime & Security modules")
    check(
        "kimari/runtime/__init__.py exists",
        (PROJECT_ROOT / "kimari" / "runtime" / "__init__.py").exists(),
        "Runtime module init missing",
    )
    check(
        "kimari/runtime/llama_flags.py exists",
        (PROJECT_ROOT / "kimari" / "runtime" / "llama_flags.py").exists(),
        "llama-server flag detection module missing",
    )
    check(
        "kimari/security/__init__.py exists",
        (PROJECT_ROOT / "kimari" / "security" / "__init__.py").exists(),
        "Security module init missing",
    )
    check(
        "kimari/security/tokens.py exists",
        (PROJECT_ROOT / "kimari" / "security" / "tokens.py").exists(),
        "Token management module missing",
    )
    check(
        "scripts/windows/kimari-launcher.ps1 exists",
        (PROJECT_ROOT / "scripts" / "windows" / "kimari-launcher.ps1").exists(),
        "Windows launcher script missing",
    )
    check(
        "scripts/windows/kimari-doctor.ps1 exists",
        (PROJECT_ROOT / "scripts" / "windows" / "kimari-doctor.ps1").exists(),
        "Windows doctor script missing",
    )
    check(
        "scripts/windows/README.md exists",
        (PROJECT_ROOT / "scripts" / "windows" / "README.md").exists(),
        "Windows scripts README missing",
    )

    # ── Packaged defaults & paths (v0.1.12) ──────────────────────────
    print("\n[14/15] Packaged defaults & user paths")
    check(
        "kimari/defaults/ directory exists",
        (PROJECT_ROOT / "kimari" / "defaults").is_dir(),
        "Packaged defaults directory missing",
    )
    check(
        "kimari/defaults/kimari.profiles.json exists",
        (PROJECT_ROOT / "kimari" / "defaults" / "kimari.profiles.json").exists(),
        "Default profiles JSON missing from packaged defaults",
    )
    check(
        "kimari/defaults/kimari.profiles.schema.json exists",
        (PROJECT_ROOT / "kimari" / "defaults" / "kimari.profiles.schema.json").exists(),
        "Default schema JSON missing from packaged defaults",
    )
    check(
        "kimari/defaults/kimari.models.json exists",
        (PROJECT_ROOT / "kimari" / "defaults" / "kimari.models.json").exists(),
        "Default models JSON missing from packaged defaults",
    )
    check(
        "kimari/core/paths.py exists",
        (PROJECT_ROOT / "kimari" / "core" / "paths.py").exists(),
        "User paths module missing",
    )
    check(
        "config/ directory still exists (for dev)",
        (PROJECT_ROOT / "config" / "kimari.profiles.json").exists(),
        "config/ directory missing — needed for editable installs",
    )

    # Check pyproject.toml package-data includes defaults
    pyproject_text = (PROJECT_ROOT / "pyproject.toml").read_text()
    check(
        "pyproject.toml includes defaults/*.json in package-data",
        "defaults" in pyproject_text,
        "defaults/*.json not found in pyproject.toml package-data",
    )

    # Check README mentions packaged defaults / user paths
    check(
        "README mentions 'packaged defaults' or 'user paths'",
        "packaged defaults" in readme_lower or "user paths" in readme_lower or "kimari home" in readme_lower,
        "'packaged defaults' or 'user paths' not found in README.md",
    )

    # ── Short flag support in strict-flags (v0.1.12) ──────────────────
    print("\n[15/15] Short flag support in strict-flags")
    llama_flags_path = PROJECT_ROOT / "kimari" / "runtime" / "llama_flags.py"
    if llama_flags_path.exists():
        flags_text = llama_flags_path.read_text()
        check(
            "SHORT_TO_LONG mapping exists in llama_flags.py",
            "SHORT_TO_LONG" in flags_text,
            "SHORT_TO_LONG alias mapping missing from llama_flags.py",
        )
        check(
            "supports_flag checks alias mapping",
            "SHORT_TO_LONG" in flags_text and "LONG_TO_SHORT" in flags_text,
            "Alias checking in supports_flag may be incomplete",
        )
        # Check key short flags are mapped
        for short_flag in ["-m", "-c", "-ngl", "-b", "-ub", "-t"]:
            check(
                f"SHORT_TO_LONG maps {short_flag!r}",
                f'"{short_flag}"' in flags_text,
                f"{short_flag!r} not found in SHORT_TO_LONG mapping",
            )

    # ── Community & contribution files (v0.1.13) ───────────────────
    print("\n[16/18] Community & contribution files")
    check(
        "CODE_OF_CONDUCT.md exists",
        (PROJECT_ROOT / "CODE_OF_CONDUCT.md").exists(),
        "Code of Conduct missing",
    )
    # Check CoC mentions Contributor Covenant
    coc_path = PROJECT_ROOT / "CODE_OF_CONDUCT.md"
    if coc_path.exists():
        coc_text = coc_path.read_text().lower()
        check(
            "CODE_OF_CONDUCT.md mentions Contributor Covenant",
            "contributor covenant" in coc_text,
            "Contributor Covenant attribution missing",
        )
    check(
        "CONTRIBUTING.md exists",
        (PROJECT_ROOT / "CONTRIBUTING.md").exists(),
        "Contributing guide missing",
    )
    check(
        "SUPPORT.md exists",
        (PROJECT_ROOT / "SUPPORT.md").exists(),
        "Support guide missing",
    )
    check(
        "GOVERNANCE.md exists",
        (PROJECT_ROOT / "GOVERNANCE.md").exists(),
        "Governance doc missing",
    )
    check(
        "MAINTAINERS.md exists",
        (PROJECT_ROOT / "MAINTAINERS.md").exists(),
        "Maintainers doc missing",
    )
    check(
        ".github/PULL_REQUEST_TEMPLATE.md exists",
        (PROJECT_ROOT / ".github" / "pull_request_template.md").exists(),
        "PR template missing",
    )
    # Issue templates
    for template in ["bug_report.yml", "feature_request.yml", "performance_report.yml", "integration_request.yml", "config.yml"]:
        check(
            f".github/ISSUE_TEMPLATE/{template} exists",
            (PROJECT_ROOT / ".github" / "ISSUE_TEMPLATE" / template).exists(),
            f"Issue template {template} missing",
        )
    # README links to community docs
    check(
        "README links to Code of Conduct",
        "CODE_OF_CONDUCT.md" in readme_text,
        "CODE_OF_CONDUCT.md link not found in README.md",
    )
    check(
        "README links to Contributing",
        "CONTRIBUTING.md" in readme_text,
        "CONTRIBUTING.md link not found in README.md",
    )
    check(
        "README links to Support",
        "SUPPORT.md" in readme_text,
        "SUPPORT.md link not found in README.md",
    )
    # docs/index.html mentions community
    if index_html.exists():
        check(
            "docs/index.html mentions 'community' or 'Code of Conduct'",
            "community" in index_text.lower() or "code of conduct" in index_text.lower(),
            "'community' or 'Code of Conduct' not found in docs/index.html",
        )

    # ── Packaging & CI (v0.1.13) ──────────────────────────────────
    print("\n[17/18] Packaging & CI")
    # Check SPDX license format
    pyproject_text = (PROJECT_ROOT / "pyproject.toml").read_text()
    check(
        "pyproject.toml uses SPDX license format",
        'license = "MIT"' in pyproject_text,
        'pyproject.toml should use license = "MIT" (SPDX), not license = {text = "MIT"}',
    )
    check(
        "pyproject.toml has no License classifier (superseded by SPDX)",
        "License ::" not in pyproject_text,
        "License classifier should be removed when using SPDX license expression",
    )
    check(
        "MANIFEST.in exists",
        (PROJECT_ROOT / "MANIFEST.in").exists(),
        "MANIFEST.in missing — sdist may not include community files",
    )
    # Check CI has wheel-install-smoke job
    ci_yml = PROJECT_ROOT / ".github" / "workflows" / "ci.yml"
    if ci_yml.exists():
        ci_text = ci_yml.read_text()
        check(
            "CI has wheel-install-smoke job",
            "wheel-install-smoke" in ci_text,
            "wheel-install-smoke CI job missing",
        )
    else:
        warn("CI workflow file not found", "cannot check for wheel-install-smoke job")

    # ── Content integrity re-check (v0.1.13) ───────────────────────
    print("\n[18/18] Content integrity re-check")
    # Re-verify critical rules haven't regressed
    check(
        'default_profile still "test"',
        profiles.get("default_profile", "") == "test" if profiles_path.exists() else False,
        "default_profile changed from test — this is not allowed during alpha",
    )
    check(
        "No 'Kimari-4B released' false claim (re-check)",
        len(false_claims) == 0,
        "Kimari-4B false claim regression detected",
    )
    check(
        "No 'Responses API supported' false claim (re-check)",
        len(responses_false_claims) == 0,
        "Responses API false claim regression detected",
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
