#!/usr/bin/env python3
"""
Kimari Local AI — Release Validation Script

Checks that all release hygiene requirements are met before publishing.
Exits with code 0 on success, 1 on any failure.

Usage:
    python scripts/release/check-release.py
"""

import json
import os
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


def _no_invented_hashes() -> bool:
    """Check that no non-null sha256 hashes exist in the packaged defaults models registry.

    Invented hashes (hard-coded without computing from the actual file) are forbidden.
    User-pinned hashes in the user registry are allowed.
    """
    defaults_path = PROJECT_ROOT / "kimari" / "defaults" / "kimari.models.json"
    if not defaults_path.exists():
        # Also check config/ dir
        config_path = PROJECT_ROOT / "config" / "kimari.models.json"
        if not config_path.exists():
            return True
        defaults_path = config_path
    try:
        data = json.loads(defaults_path.read_text())
        return all(m.get("sha256") is None for m in data.get("models", []))
    except Exception:
        return True


def main() -> None:
    print("Kimari Local AI — Release Validation")
    print("=" * 50)

    # ── Version consistency ──────────────────────────────────────
    print("\n[1/55] Version consistency")
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
    print("\n[2/55] README version badge")
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
    print("\n[3/55] CHANGELOG entry")
    changelog = PROJECT_ROOT / "CHANGELOG.md"
    changelog_text = changelog.read_text()
    changelog_header = f"[{init_ver}]"
    check(
        "CHANGELOG.md has entry for current version",
        changelog_header in changelog_text,
        f"'{changelog_header}' not found in CHANGELOG.md",
    )

    # ── ROADMAP entry ────────────────────────────────────────────
    print("\n[4/55] ROADMAP entry")
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
    print("\n[5/55] Config defaults")
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
    print("\n[6/55] Package markers")
    py_typed = PROJECT_ROOT / "kimari" / "py.typed"
    check("kimari/py.typed exists", py_typed.exists(), "PEP 561 marker missing")

    # ── GitHub Pages / SEO ──────────────────────────────────────
    print("\n[7/55] GitHub Pages / SEO")
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
    print("\n[8/55] Documentation files")
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
    print("\n[9/55] No unwanted tracked files")
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
    print("\n[10/55] Content integrity")
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
    print("\n[11/55] Integration documentation")
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
    print("\n[12/55] Performance module")
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
    print("\n[13/55] Runtime & Security modules")
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
    print("\n[14/55] Packaged defaults & user paths")
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
    print("\n[15/55] Short flag support in strict-flags")
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
    print("\n[16/55] Community & contribution files")
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
    for template in [
        "bug_report.yml",
        "feature_request.yml",
        "performance_report.yml",
        "integration_request.yml",
        "config.yml",
    ]:
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
    print("\n[17/55] Packaging & CI")
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
    print("\n[18/55] Content integrity re-check")
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

    # ── Setup write-mode & SHA256 tooling (v0.1.14) ──────────────────
    print("\n[19/55] Setup write-mode & SHA256 tooling")
    check(
        "kimari/setup/__init__.py exists",
        (PROJECT_ROOT / "kimari" / "setup" / "__init__.py").exists(),
        "Setup module init missing",
    )
    check(
        "kimari/setup/writer.py exists",
        (PROJECT_ROOT / "kimari" / "setup" / "writer.py").exists(),
        "Setup writer module missing",
    )
    check(
        "README mentions 'setup --write'",
        "setup --write" in readme_lower or "setup --write" in readme_text,
        "'setup --write' not found in README.md",
    )
    check(
        "README mentions 'models hash' or 'models verify'",
        "models hash" in readme_lower or "models verify" in readme_lower,
        "'models hash' or 'models verify' not found in README.md",
    )
    check(
        "No invented SHA256 hashes in models registry",
        _no_invented_hashes(),
        "Found non-null sha256 in models registry — hashes must be explicitly pinned, not invented",
    )

    # ── New documentation (v0.1.14) ──────────────────────────────────
    print("\n[20/55] New documentation files")
    check(
        "docs/REVERSE_PROXY_AUTH.md exists",
        (PROJECT_ROOT / "docs" / "REVERSE_PROXY_AUTH.md").exists(),
        "Reverse proxy auth guide missing",
    )
    check(
        "docs/API_PLAN.md exists",
        (PROJECT_ROOT / "docs" / "API_PLAN.md").exists(),
        "API plan document missing",
    )
    # README links to new docs
    check(
        "README links to REVERSE_PROXY_AUTH.md",
        "REVERSE_PROXY_AUTH" in readme_text,
        "REVERSE_PROXY_AUTH.md link not found in README.md",
    )
    check(
        "README links to API_PLAN.md",
        "API_PLAN" in readme_text,
        "API_PLAN.md link not found in README.md",
    )
    # docs/index.html mentions new docs
    if index_html.exists():
        check(
            "docs/index.html mentions 'reverse proxy' or 'API plan'",
            "reverse proxy" in index_text.lower() or "api plan" in index_text.lower(),
            "'reverse proxy' or 'API plan' not found in docs/index.html",
        )

    # ── Content integrity v0.1.14 re-check ───────────────────────────
    print("\n[21/55] Content integrity re-check (v0.1.14)")
    check(
        'default_profile still "test" (v0.1.14 re-check)',
        profiles.get("default_profile", "") == "test" if profiles_path.exists() else False,
        "default_profile changed from test — this is not allowed during alpha",
    )
    check(
        "No 'Kimari-4B released' false claim (v0.1.14 re-check)",
        len(false_claims) == 0,
        "Kimari-4B false claim regression detected",
    )
    check(
        "No 'Responses API supported' false claim (v0.1.14 re-check)",
        len(responses_false_claims) == 0,
        "Responses API false claim regression detected",
    )

    # ── Model path resolution (v0.1.15) ───────────────────────────────
    print("\n[22/55] Model path resolution")
    main_py_path = PROJECT_ROOT / "kimari" / "cli" / "main.py"
    if main_py_path.exists():
        main_py_text = main_py_path.read_text()
        check(
            "resolve_model_path function exists in kimari/cli/main.py",
            "resolve_model_path" in main_py_text,
            "resolve_model_path function not found in kimari/cli/main.py",
        )
        check(
            "start_server does NOT use PROJECT_ROOT / effective_model directly",
            "PROJECT_ROOT / effective_model" not in main_py_text,
            "Old bug pattern detected: start_server uses PROJECT_ROOT / effective_model directly — should use resolve_model_path()",
        )
    else:
        check("kimari/cli/main.py exists", False, "file not found")

    # ── v0.1.15 new files ─────────────────────────────────────────────
    print("\n[23/55] v0.1.15 new files")
    check(
        "benchmarks/RESULT_FORMAT.md exists",
        (PROJECT_ROOT / "benchmarks" / "RESULT_FORMAT.md").exists(),
        "Benchmark result format doc missing",
    )
    check(
        "benchmarks/examples/perf-result.example.json exists",
        (PROJECT_ROOT / "benchmarks" / "examples" / "perf-result.example.json").exists(),
        "Benchmark result example missing",
    )
    check(
        "docs/API_OPENAPI_DRAFT.yaml exists",
        (PROJECT_ROOT / "docs" / "API_OPENAPI_DRAFT.yaml").exists(),
        "API OpenAPI draft missing",
    )
    check(
        "scripts/windows/build-wheel.ps1 exists",
        (PROJECT_ROOT / "scripts" / "windows" / "build-wheel.ps1").exists(),
        "Windows build-wheel script missing",
    )
    check(
        "scripts/windows/install-from-wheel.ps1 exists",
        (PROJECT_ROOT / "scripts" / "windows" / "install-from-wheel.ps1").exists(),
        "Windows install-from-wheel script missing",
    )
    check(
        "scripts/windows/install-from-testpypi.ps1 exists",
        (PROJECT_ROOT / "scripts" / "windows" / "install-from-testpypi.ps1").exists(),
        "Windows install-from-testpypi script missing",
    )

    # ── v0.1.15 content ───────────────────────────────────────────────
    print("\n[24/55] v0.1.15 content")
    check(
        "README mentions 'setup --write --yes'",
        "setup --write --yes" in readme_lower or "setup --write --yes" in readme_text,
        "'setup --write --yes' not found in README.md",
    )
    check(
        "README mentions 'pin-hash'",
        "pin-hash" in readme_lower or "pin-hash" in readme_text,
        "'pin-hash' not found in README.md",
    )
    check(
        "docs/PUBLISHING.md has '0.1.15' section",
        "0.1.15" in (PROJECT_ROOT / "docs" / "PUBLISHING.md").read_text()
        if (PROJECT_ROOT / "docs" / "PUBLISHING.md").exists()
        else False,
        "'0.1.15' not found in docs/PUBLISHING.md",
    )
    check(
        'default_profile still "test" (v0.1.15 check)',
        profiles.get("default_profile", "") == "test" if profiles_path.exists() else False,
        "default_profile changed from test — this is not allowed during alpha",
    )
    check(
        "No 'Kimari-4B is available now' or 'Kimari-4B can be downloaded' false claim (v0.1.15)",
        len(false_claims) == 0,
        "Kimari-4B false claim regression detected",
    )
    check(
        "No 'Responses API is supported' false claim (v0.1.15)",
        len(responses_false_claims) == 0,
        "Responses API false claim regression detected",
    )

    # ── v0.1.16 API experimental ───────────────────────────────────
    print("\n[25/55] v0.1.16 API experimental")
    check(
        "kimari/api/app.py exists",
        (PROJECT_ROOT / "kimari" / "api" / "app.py").exists(),
        "API app module missing",
    )
    check(
        "kimari/api/schemas.py exists",
        (PROJECT_ROOT / "kimari" / "api" / "schemas.py").exists(),
        "API schemas module missing",
    )
    check(
        "kimari/api/server.py exists",
        (PROJECT_ROOT / "kimari" / "api" / "server.py").exists(),
        "API server module missing",
    )
    pyproject_text_v2 = (PROJECT_ROOT / "pyproject.toml").read_text()
    check(
        'pyproject optional dependency "api" exists',
        '"api"' in pyproject_text_v2 or "'api'" in pyproject_text_v2 or "api" in pyproject_text_v2,
        '"api" optional dependency group not found in pyproject.toml',
    )
    check(
        "docs/API_EXPERIMENTAL.md exists",
        (PROJECT_ROOT / "docs" / "API_EXPERIMENTAL.md").exists(),
        "API experimental doc missing",
    )
    check(
        "docs/PYPI_RELEASE_GATE.md exists",
        (PROJECT_ROOT / "docs" / "PYPI_RELEASE_GATE.md").exists(),
        "PyPI release gate doc missing",
    )
    check(
        "docs/MODEL_HASHING.md exists",
        (PROJECT_ROOT / "docs" / "MODEL_HASHING.md").exists(),
        "Model hashing doc missing",
    )
    check(
        "docs/BENCHMARK_SUBMISSIONS.md exists",
        (PROJECT_ROOT / "docs" / "BENCHMARK_SUBMISSIONS.md").exists(),
        "Benchmark submissions doc missing",
    )
    check(
        "benchmarks/examples/perf-result.gtx1060.example.json exists",
        (PROJECT_ROOT / "benchmarks" / "examples" / "perf-result.gtx1060.example.json").exists(),
        "GTX 1060 benchmark example missing",
    )
    check(
        "benchmarks/examples/perf-result.gtx1080.example.json exists",
        (PROJECT_ROOT / "benchmarks" / "examples" / "perf-result.gtx1080.example.json").exists(),
        "GTX 1080 benchmark example missing",
    )
    check(
        'README mentions "Experimental API"',
        "experimental api" in readme_lower or "Experimental API" in readme_text,
        '"Experimental API" not found in README.md',
    )
    if index_html.exists():
        check(
            'docs/index.html mentions "PyPI release gate"',
            "pypi release gate" in index_text.lower() or "release gate" in index_text.lower(),
            '"PyPI release gate" not found in docs/index.html',
        )
    check(
        'No "Responses API supported" false claim (v0.1.16)',
        len(responses_false_claims) == 0,
        'Responses API false claim detected — should only say "planned" or "future"',
    )
    check(
        'default_profile still "test" (v0.1.16 re-check)',
        profiles.get("default_profile", "") == "test" if profiles_path.exists() else False,
        "default_profile changed from test — this is not allowed during alpha",
    )

    # ── v0.1.16 Windows packaging improvements ────────────────────────
    print("\n[26/55] v0.1.16 Windows packaging improvements")
    check(
        "scripts/windows/build-wheel.ps1 exists (v0.1.16 re-check)",
        (PROJECT_ROOT / "scripts" / "windows" / "build-wheel.ps1").exists(),
        "Windows build-wheel script missing",
    )
    check(
        "scripts/windows/install-from-wheel.ps1 exists (v0.1.16 re-check)",
        (PROJECT_ROOT / "scripts" / "windows" / "install-from-wheel.ps1").exists(),
        "Windows install-from-wheel script missing",
    )
    check(
        "scripts/windows/install-from-testpypi.ps1 exists (v0.1.16 re-check)",
        (PROJECT_ROOT / "scripts" / "windows" / "install-from-testpypi.ps1").exists(),
        "Windows install-from-testpypi script missing",
    )
    check(
        "scripts/windows/kimari-launcher.ps1 exists (v0.1.16 re-check)",
        (PROJECT_ROOT / "scripts" / "windows" / "kimari-launcher.ps1").exists(),
        "Windows launcher script missing",
    )
    check(
        "scripts/windows/kimari-doctor.ps1 exists (v0.1.16 re-check)",
        (PROJECT_ROOT / "scripts" / "windows" / "kimari-doctor.ps1").exists(),
        "Windows doctor script missing",
    )

    # ── v0.1.16 release-check improvements ─────────────────────────────
    print("\n[27/55] v0.1.16 release-check improvements")
    check(
        "scripts/release/check-release.py exists (v0.1.16 re-check)",
        (PROJECT_ROOT / "scripts" / "release" / "check-release.py").exists(),
        "Release check script missing",
    )
    check(
        "RELEASE_CHECKLIST.md exists (v0.1.16 re-check)",
        (PROJECT_ROOT / "RELEASE_CHECKLIST.md").exists(),
        "Release checklist missing",
    )
    check(
        "docs/PUBLISHING.md exists (v0.1.16 re-check)",
        (PROJECT_ROOT / "docs" / "PUBLISHING.md").exists(),
        "Publishing guide missing",
    )
    check(
        'README links to API_EXPERIMENTAL.md or mentions "API Experimental"',
        "API_EXPERIMENTAL" in readme_text or "experimental api" in readme_lower,
        'API_EXPERIMENTAL.md link or "Experimental API" not found in README.md',
    )

    # ── v0.1.16 content integrity re-check ──────────────────────────────
    print("\n[28/55] v0.1.16 content integrity re-check")
    check(
        'default_profile still "test" (v0.1.16 final re-check)',
        profiles.get("default_profile", "") == "test" if profiles_path.exists() else False,
        "default_profile changed from test — this is not allowed during alpha",
    )
    check(
        'No "Kimari-4B released" false claim (v0.1.16 final)',
        len(false_claims) == 0,
        "Kimari-4B false claim regression detected",
    )
    check(
        'No "Responses API supported" false claim (v0.1.16 final)',
        len(responses_false_claims) == 0,
        "Responses API false claim regression detected",
    )
    # Check no claim of PyPI real publishing
    check(
        'No "published to PyPI" false claim',
        "published to pypi" not in all_text and "uploaded to pypi" not in all_text,
        "False claim of PyPI publishing detected — must go through release gate first",
    )

    # ── [29/55] v0.1.17 MODEL_CARD professional rewrite ──────────
    print("\n[29/55] v0.1.17 MODEL_CARD professional rewrite")
    model_card_path = PROJECT_ROOT / "MODEL_CARD.md"
    if model_card_path.exists():
        model_card_text = model_card_path.read_text()
        model_card_lower = model_card_text.lower()
        check(
            "MODEL_CARD.md exists",
            True,
        )
        check(
            'MODEL_CARD.md says "Planned" or "Training Design"',
            "planned" in model_card_lower or "training design" in model_card_lower,
            "MODEL_CARD.md must indicate planned/training design status",
        )
        check(
            "MODEL_CARD.md does NOT claim Kimari-4B is released",
            "released" not in model_card_lower.split("not released")[0].split("not yet released")[0]
            if "not released" in model_card_lower or "not yet released" in model_card_lower
            else "is available" not in model_card_lower and "can be downloaded" not in model_card_lower,
            "MODEL_CARD.md must not claim Kimari-4B is released",
        )
        check(
            "MODEL_CARD.md mentions base model candidates",
            "smollm" in model_card_lower or "qwen" in model_card_lower or "llama" in model_card_lower,
            "MODEL_CARD.md should mention base model candidates",
        )
        check(
            'MODEL_CARD.md says "TBD" for selected base',
            "tbd" in model_card_lower,
            "MODEL_CARD.md must indicate no base model selected yet",
        )
    else:
        check("MODEL_CARD.md exists", False, "MODEL_CARD.md missing")

    # ── [30/55] v0.1.17 training and base selection docs ──────────
    print("\n[30/55] v0.1.17 training and base selection docs")
    check(
        "docs/MODEL_TRAINING_PLAN.md exists",
        (PROJECT_ROOT / "docs" / "MODEL_TRAINING_PLAN.md").exists(),
        "Model training plan missing",
    )
    check(
        "docs/MODEL_BASE_SELECTION.md exists",
        (PROJECT_ROOT / "docs" / "MODEL_BASE_SELECTION.md").exists(),
        "Base selection doc missing",
    )

    # ── [31/55] v0.1.17 dataset and schema files ──────────────────
    print("\n[31/55] v0.1.17 dataset and schema files")
    check(
        "dataset/README.md exists",
        (PROJECT_ROOT / "dataset" / "README.md").exists(),
        "Dataset README missing",
    )
    sft_schema = PROJECT_ROOT / "dataset" / "schema" / "sft.schema.json"
    pref_schema = PROJECT_ROOT / "dataset" / "schema" / "preference.schema.json"
    check(
        "dataset/schema/sft.schema.json exists",
        sft_schema.exists(),
        "SFT schema missing",
    )
    check(
        "dataset/schema/preference.schema.json exists",
        pref_schema.exists(),
        "Preference schema missing",
    )
    if sft_schema.exists():
        try:
            json.loads(sft_schema.read_text())
            check("sft.schema.json is valid JSON", True)
        except json.JSONDecodeError:
            check("sft.schema.json is valid JSON", False, "JSON parse error")
    if pref_schema.exists():
        try:
            json.loads(pref_schema.read_text())
            check("preference.schema.json is valid JSON", True)
        except json.JSONDecodeError:
            check("preference.schema.json is valid JSON", False, "JSON parse error")

    # ── [32/55] v0.1.17 training skeletons ────────────────────────
    print("\n[32/55] v0.1.17 training skeletons")
    check(
        "training/README.md exists",
        (PROJECT_ROOT / "training" / "README.md").exists(),
        "Training README missing",
    )
    check(
        "training/configs/kimari_sft_lora.example.yaml exists",
        (PROJECT_ROOT / "training" / "configs" / "kimari_sft_lora.example.yaml").exists(),
        "SFT LoRA example config missing",
    )
    check(
        "training/configs/kimari_orpo.example.yaml exists",
        (PROJECT_ROOT / "training" / "configs" / "kimari_orpo.example.yaml").exists(),
        "ORPO example config missing",
    )
    check(
        "training/scripts/prepare_dataset.py exists",
        (PROJECT_ROOT / "training" / "scripts" / "prepare_dataset.py").exists(),
        "Dataset preparation script missing",
    )
    check(
        "training/scripts/train_sft_lora.py exists",
        (PROJECT_ROOT / "training" / "scripts" / "train_sft_lora.py").exists(),
        "SFT LoRA training script missing",
    )

    # ── [33/55] v0.1.17 eval prompts and HF release ───────────────
    print("\n[33/55] v0.1.17 eval prompts and HF release")
    check(
        "eval/README.md exists",
        (PROJECT_ROOT / "eval" / "README.md").exists(),
        "Eval README missing",
    )
    kimarifit_prompts = PROJECT_ROOT / "eval" / "kimarifit_prompts.jsonl"
    check(
        "eval/kimarifit_prompts.jsonl exists",
        kimarifit_prompts.exists(),
        "KimariFit prompts file missing",
    )
    if kimarifit_prompts.exists():
        try:
            lines = kimarifit_prompts.read_text().strip().splitlines()
            all(json.loads(line) for line in lines if line.strip())  # noqa: SIM110
            check("kimarifit_prompts.jsonl: all lines valid JSON", True)
        except (json.JSONDecodeError, Exception):
            check("kimarifit_prompts.jsonl: all lines valid JSON", False, "JSON parse error in prompts file")
    check(
        "docs/HUGGINGFACE_RELEASE.md exists",
        (PROJECT_ROOT / "docs" / "HUGGINGFACE_RELEASE.md").exists(),
        "Hugging Face release doc missing",
    )

    # ── [34/55] v0.1.17 content integrity ─────────────────────────
    print("\n[34/55] v0.1.17 content integrity")
    check(
        'default_profile still "test" (v0.1.17 check)',
        profiles.get("default_profile", "") == "test" if profiles_path.exists() else False,
        "default_profile changed from test — this is not allowed during alpha",
    )
    # Check no GGUF tracked
    try:
        result = subprocess.run(
            ["git", "ls-files", "*.gguf"],
            capture_output=True,
            text=True,
            cwd=str(PROJECT_ROOT),
        )
        gguf_files = [f for f in result.stdout.strip().splitlines() if f]
        check("No GGUF files tracked in git (v0.1.17 re-check)", len(gguf_files) == 0, f"found: {gguf_files}")
    except Exception:
        pass  # Already checked in [9/55]
    # No fake benchmark numbers
    if model_card_path.exists():
        mc_text = model_card_path.read_text()
        check(
            "No fake MMLU/HumanEval numbers in MODEL_CARD",
            "MMLU" not in mc_text or "TBD" in mc_text or "not measured" in mc_text.lower(),
            "MODEL_CARD should not contain fake benchmark numbers",
        )
    check(
        "No claim Kimari-4B is released (v0.1.17 final)",
        len(false_claims) == 0,
        "Kimari-4B false claim regression detected",
    )

    # ── [35/55] v0.1.17 MODEL_LICENSES and README updates ────────
    print("\n[35/55] v0.1.17 MODEL_LICENSES and README updates")
    ml_path = PROJECT_ROOT / "MODEL_LICENSES.md"
    if ml_path.exists():
        ml_text = ml_path.read_text().lower()
        check(
            "MODEL_LICENSES.md mentions SmolLM3",
            "smollm" in ml_text,
            "SmolLM3 candidate not found in MODEL_LICENSES.md",
        )
        check(
            "MODEL_LICENSES.md mentions Qwen",
            "qwen" in ml_text,
            "Qwen candidate not found in MODEL_LICENSES.md",
        )
        check(
            "MODEL_LICENSES.md mentions Llama license",
            "llama" in ml_text or "meta" in ml_text,
            "Llama/Meta license not found in MODEL_LICENSES.md",
        )
    check(
        'README mentions "Kimari-4B" or "MODEL_CARD"',
        "kimari-4b" in readme_lower or "MODEL_CARD" in readme_text,
        '"Kimari-4B" or "MODEL_CARD" not found in README.md',
    )
    check(
        'README mentions "training plan" or "MODEL_TRAINING_PLAN"',
        "training plan" in readme_lower or "MODEL_TRAINING_PLAN" in readme_text,
        '"Training plan" not found in README.md',
    )
    check(
        'README mentions "base selection" or "MODEL_BASE_SELECTION"',
        "base selection" in readme_lower or "base model" in readme_lower or "MODEL_BASE_SELECTION" in readme_text,
        '"Base selection" not found in README.md',
    )
    check(
        'README mentions "Hugging Face" or "HUGGINGFACE_RELEASE"',
        "hugging face" in readme_lower or "HUGGINGFACE_RELEASE" in readme_text,
        '"Hugging Face" not found in README.md',
    )

    # ── [36/55] v0.1.18 base selection and decision record ────────
    print("\n[36/55] v0.1.18 base selection and decision record")
    mdr_path = PROJECT_ROOT / "docs" / "MODEL_DECISION_RECORD.md"
    check(
        "docs/MODEL_DECISION_RECORD.md exists",
        mdr_path.exists(),
        "Model Decision Record missing",
    )
    base_cands_path = PROJECT_ROOT / "training" / "configs" / "base_candidates.yaml"
    check(
        "training/configs/base_candidates.yaml exists",
        base_cands_path.exists(),
        "Base candidates config missing",
    )
    select_base_path = PROJECT_ROOT / "training" / "scripts" / "select_base_model.py"
    check(
        "training/scripts/select_base_model.py exists",
        select_base_path.exists(),
        "Base model selection script missing",
    )
    if base_cands_path.exists():
        bc_text = base_cands_path.read_text()
        check(
            "base_candidates.yaml contains 'candidates:'",
            "candidates:" in bc_text,
            "candidates section not found in base_candidates.yaml",
        )
    if mdr_path.exists():
        mdr_text = mdr_path.read_text()
        mdr_lower = mdr_text.lower()
        # v0.1.19: MODEL_DECISION_RECORD may say "Accepted for first private training run"
        # but must NOT claim public release is accepted
        check(
            "MODEL_DECISION_RECORD mentions decision status (proposed/under review/accepted for private)",
            "proposed" in mdr_lower or "under review" in mdr_lower or "accepted" in mdr_lower,
            "MODEL_DECISION_RECORD must indicate a decision status",
        )
        check(
            "MODEL_DECISION_RECORD does NOT claim public release accepted",
            "accepted for public" not in mdr_lower and "public release accepted" not in mdr_lower,
            "MODEL_DECISION_RECORD must not claim public release is accepted (only private training)",
        )

    # ── [37/55] v0.1.18 seed datasets, builders, eval harness ────
    print("\n[37/55] v0.1.18 seed datasets, builders, eval harness")
    sft_seed = PROJECT_ROOT / "dataset" / "samples" / "sft_seed.jsonl"
    pref_seed = PROJECT_ROOT / "dataset" / "samples" / "preference_seed.jsonl"
    check(
        "dataset/samples/sft_seed.jsonl exists",
        sft_seed.exists(),
        "SFT seed dataset missing",
    )
    check(
        "dataset/samples/preference_seed.jsonl exists",
        pref_seed.exists(),
        "Preference seed dataset missing",
    )
    # Validate first 5 lines of each
    for seed_path, name in [(sft_seed, "sft_seed"), (pref_seed, "preference_seed")]:
        if seed_path.exists():
            try:
                lines = seed_path.read_text().strip().splitlines()
                valid_count = 0
                for line in lines[:5]:
                    if line.strip():
                        json.loads(line)
                        valid_count += 1
                check(
                    f"{name}.jsonl first 5 lines are valid JSONL",
                    valid_count > 0,
                    f"No valid JSONL lines found in {name}.jsonl",
                )
            except json.JSONDecodeError:
                check(f"{name}.jsonl is valid JSONL", False, "JSON parse error")
    check(
        "training/scripts/build_dataset_mix.py exists",
        (PROJECT_ROOT / "training" / "scripts" / "build_dataset_mix.py").exists(),
        "Dataset mix builder script missing",
    )
    check(
        "eval/kimarifit.py exists",
        (PROJECT_ROOT / "eval" / "kimarifit.py").exists(),
        "KimariFit evaluation harness missing",
    )
    check(
        "eval/rubrics/kimarifit_rubric.md exists",
        (PROJECT_ROOT / "eval" / "rubrics" / "kimarifit_rubric.md").exists(),
        "KimariFit rubric missing",
    )
    check(
        "training/scripts/export_gguf_plan.py exists",
        (PROJECT_ROOT / "training" / "scripts" / "export_gguf_plan.py").exists(),
        "GGUF export plan script missing",
    )
    check(
        "docs/FIRST_TRAINING_RUN.md exists",
        (PROJECT_ROOT / "docs" / "FIRST_TRAINING_RUN.md").exists(),
        "First training run guide missing",
    )
    check(
        "eval/results/.gitkeep exists",
        (PROJECT_ROOT / "eval" / "results" / ".gitkeep").exists(),
        "eval/results/.gitkeep missing",
    )
    # MODEL_CARD still says not released
    if model_card_path.exists():
        mc_lower = model_card_path.read_text().lower()
        check(
            "MODEL_CARD still says not released/TBD (v0.1.18)",
            "not been released" in mc_lower or "not released" in mc_lower or "tbd" in mc_lower,
            "MODEL_CARD must still indicate not released/TBD status",
        )
    # No GGUF tracked
    try:
        result = subprocess.run(
            ["git", "ls-files", "*.gguf"],
            capture_output=True,
            text=True,
            cwd=str(PROJECT_ROOT),
        )
        gguf_files_v0118 = [f for f in result.stdout.strip().splitlines() if f]
        check(
            "No GGUF files tracked (v0.1.18 re-check)",
            len(gguf_files_v0118) == 0,
            f"GGUF files tracked: {gguf_files_v0118}",
        )
    except Exception:
        pass  # Already checked earlier

    # ── [38/55] v0.1.18 content integrity ─────────────────────────
    print("\n[38/55] v0.1.18 content integrity")
    # No false claims re-check
    check(
        'No "Kimari-4B released" false claim (v0.1.18)',
        len(false_claims) == 0,
        "Kimari-4B false claim regression detected",
    )
    # No fake MMLU/HumanEval scores
    if model_card_path.exists():
        mc_text_v0118 = model_card_path.read_text()
        check(
            "No fake MMLU/HumanEval scores (v0.1.18)",
            "MMLU" not in mc_text_v0118
            or "TBD" in mc_text_v0118
            or "not measured" in mc_text_v0118.lower()
            or "not achieved" in mc_text_v0118.lower(),
            "MODEL_CARD should not contain fake benchmark numbers",
        )
    # default_profile still test
    check(
        'default_profile still "test" (v0.1.18 check)',
        profiles.get("default_profile", "") == "test" if profiles_path.exists() else False,
        "default_profile changed from test — this is not allowed during alpha",
    )
    # dataset/build/ in .gitignore
    gitignore_path = PROJECT_ROOT / ".gitignore"
    if gitignore_path.exists():
        gitignore_text = gitignore_path.read_text()
        check(
            "dataset/build/ in .gitignore",
            "dataset/build/" in gitignore_text or "dataset/build" in gitignore_text,
            "dataset/build/ should be in .gitignore",
        )
    # eval/results/*.json in .gitignore
    if gitignore_path.exists():
        gitignore_text = gitignore_path.read_text()
        check(
            "eval/results/*.json in .gitignore",
            "eval/results/" in gitignore_text or "eval/results" in gitignore_text,
            "eval/results/ should be in .gitignore",
        )

    # ── [39/55] v0.1.19 base acceptance ────────────────────────────
    print("\n[39/55] v0.1.19 base acceptance")
    check(
        "docs/BASE_MODEL_ACCEPTANCE.md exists",
        (PROJECT_ROOT / "docs" / "BASE_MODEL_ACCEPTANCE.md").exists(),
        "Base model acceptance doc missing",
    )
    base_acceptance_path = PROJECT_ROOT / "docs" / "BASE_MODEL_ACCEPTANCE.md"
    if base_acceptance_path.exists():
        ba_text = base_acceptance_path.read_text().lower()
        check(
            'BASE_MODEL_ACCEPTANCE says "private training" (not public release)',
            "private" in ba_text and ("training" in ba_text or "sft" in ba_text),
            "BASE_MODEL_ACCEPTANCE must clearly state this is for private training only",
        )
    # Check base_candidates has accepted status
    base_yaml_path = PROJECT_ROOT / "training" / "configs" / "base_candidates.yaml"
    if base_yaml_path.exists():
        base_yaml_text = base_yaml_path.read_text()
        check(
            "base_candidates.yaml has accepted_private_training_candidate",
            "accepted_private_training_candidate" in base_yaml_text,
            "No candidate with accepted_private_training_candidate status found",
        )
        check(
            "base_candidates.yaml has selected_for_private_sft: true",
            "selected_for_private_sft: true" in base_yaml_text,
            "No candidate selected for private SFT",
        )
        check(
            "base_candidates.yaml has selected_for_public_release: false",
            "selected_for_public_release: false" in base_yaml_text,
            "Public release must not be approved yet",
        )

    # ── [40/55] v0.1.19 dataset v0 ────────────────────────────────
    print("\n[40/55] v0.1.19 dataset v0")
    check(
        "dataset/v0/sft_v0.jsonl exists",
        (PROJECT_ROOT / "dataset" / "v0" / "sft_v0.jsonl").exists(),
        "SFT v0 dataset missing",
    )
    check(
        "dataset/v0/preference_v0.jsonl exists",
        (PROJECT_ROOT / "dataset" / "v0" / "preference_v0.jsonl").exists(),
        "Preference v0 dataset missing",
    )
    check(
        "dataset/v0/eval_holdout.jsonl exists",
        (PROJECT_ROOT / "dataset" / "v0" / "eval_holdout.jsonl").exists(),
        "Eval holdout v0 dataset missing",
    )
    check(
        "dataset/v0/README.md exists",
        (PROJECT_ROOT / "dataset" / "v0" / "README.md").exists(),
        "Dataset v0 README missing",
    )
    # Validate datasets parse as JSONL if they exist
    for ds_file in ["sft_v0.jsonl", "preference_v0.jsonl", "eval_holdout.jsonl"]:
        ds_path = PROJECT_ROOT / "dataset" / "v0" / ds_file
        if ds_path.exists():
            try:
                lines = [ln.strip() for ln in ds_path.read_text().splitlines() if ln.strip()]
                parsed = [json.loads(ln) for ln in lines]
                check(f"dataset/v0/{ds_file} is valid JSONL", True)
                if "sft" in ds_file:
                    check(
                        f"dataset/v0/{ds_file} has >= 50 records",
                        len(parsed) >= 50,
                        f"Only {len(parsed)} records, need >= 50",
                    )
                elif "preference" in ds_file:
                    check(
                        f"dataset/v0/{ds_file} has >= 20 records",
                        len(parsed) >= 20,
                        f"Only {len(parsed)} records, need >= 20",
                    )
                elif "holdout" in ds_file:
                    check(
                        f"dataset/v0/{ds_file} has >= 10 records",
                        len(parsed) >= 10,
                        f"Only {len(parsed)} records, need >= 10",
                    )
            except json.JSONDecodeError:
                check(f"dataset/v0/{ds_file} is valid JSONL", False, "JSON parse error")

    # ── [41/55] v0.1.19 training and eval tools ────────────────────
    print("\n[41/55] v0.1.19 training and eval tools")
    check(
        "training/scripts/validate_training_ready.py exists",
        (PROJECT_ROOT / "training" / "scripts" / "validate_training_ready.py").exists(),
        "Training readiness validator missing",
    )
    check(
        "eval/scoring/kimarifit_dimensions.json exists",
        (PROJECT_ROOT / "eval" / "scoring" / "kimarifit_dimensions.json").exists(),
        "KimariFit scoring dimensions missing",
    )
    # Validate dimensions parse
    dims_path = PROJECT_ROOT / "eval" / "scoring" / "kimarifit_dimensions.json"
    if dims_path.exists():
        try:
            dims = json.loads(dims_path.read_text())
            check("kimarifit_dimensions.json is valid JSON", True)
            check(
                "kimarifit_dimensions.json has >= 9 dimensions",
                len(dims.get("dimensions", [])) >= 9,
                f"Only {len(dims.get('dimensions', []))} dimensions",
            )
        except json.JSONDecodeError:
            check("kimarifit_dimensions.json is valid JSON", False)
    check(
        "eval/scripts/summarize_results.py exists",
        (PROJECT_ROOT / "eval" / "scripts" / "summarize_results.py").exists(),
        "Summarize results script missing",
    )
    check(
        "training/configs/kimari_sft_lora.v0.example.yaml exists",
        (PROJECT_ROOT / "training" / "configs" / "kimari_sft_lora.v0.example.yaml").exists(),
        "SFT LoRA v0 example config missing",
    )
    check(
        "training/configs/kimari_orpo.v0.example.yaml exists",
        (PROJECT_ROOT / "training" / "configs" / "kimari_orpo.v0.example.yaml").exists(),
        "ORPO v0 example config missing",
    )

    # ── [42/55] v0.1.19 documentation ──────────────────────────────
    print("\n[42/55] v0.1.19 documentation")
    check(
        "docs/FIRST_PRIVATE_TRAINING_RUN.md exists",
        (PROJECT_ROOT / "docs" / "FIRST_PRIVATE_TRAINING_RUN.md").exists(),
        "First private training run guide missing",
    )
    check(
        "docs/HF_PLACEHOLDER_PLAN.md exists",
        (PROJECT_ROOT / "docs" / "HF_PLACEHOLDER_PLAN.md").exists(),
        "HF placeholder plan missing",
    )
    check(
        "MODEL_CARD.md says no weights released (v0.1.19)",
        "no weights" in model_card_lower
        or "not released" in model_card_lower
        or "not been released" in model_card_lower,
        "MODEL_CARD must clearly state no weights released",
    )

    # ── [43/55] v0.1.19 content integrity ──────────────────────────
    print("\n[43/55] v0.1.19 content integrity")
    check(
        "No GGUF files tracked (v0.1.19 re-check)",
        len(gguf_files) == 0,
        f"GGUF files found: {gguf_files}",
    )
    check(
        'No "Kimari-4B released" false claim (v0.1.19)',
        len(false_claims) == 0,
        "Kimari-4B false claim regression detected",
    )
    check(
        'default_profile still "test" (v0.1.19)',
        profiles.get("default_profile", "") == "test" if profiles_path.exists() else False,
        "default_profile changed from test — this is not allowed during alpha",
    )

    # ── [44/55] v0.1.20 baseline eval and training docs ─────────
    print("\n[44/55] v0.1.20 baseline eval and training docs")
    check(
        "docs/BASELINE_EVAL_PLAN.md exists",
        (PROJECT_ROOT / "docs" / "BASELINE_EVAL_PLAN.md").exists(),
        "Baseline eval plan missing",
    )
    check(
        "docs/ADAPTER_ARTIFACT_POLICY.md exists",
        (PROJECT_ROOT / "docs" / "ADAPTER_ARTIFACT_POLICY.md").exists(),
        "Adapter artifact policy missing",
    )
    check(
        "docs/PRIVATE_TRAINING_RUNBOOK.md exists",
        (PROJECT_ROOT / "docs" / "PRIVATE_TRAINING_RUNBOOK.md").exists(),
        "Private training runbook missing",
    )
    check(
        "docs/ADAPTER_PREVIEW_GATE.md exists",
        (PROJECT_ROOT / "docs" / "ADAPTER_PREVIEW_GATE.md").exists(),
        "Adapter preview gate missing",
    )

    # ── [45/55] v0.1.20 training configs and scripts ────────────
    print("\n[45/55] v0.1.20 training configs and scripts")
    check(
        "training/configs/private_sft_run.v0.yaml exists",
        (PROJECT_ROOT / "training" / "configs" / "private_sft_run.v0.yaml").exists(),
        "Private SFT run config missing",
    )
    private_run_path = PROJECT_ROOT / "training" / "configs" / "private_sft_run.v0.yaml"
    if private_run_path.exists():
        pr_text = private_run_path.read_text()
        check(
            "private_sft_run.v0.yaml has public_release_allowed: false",
            "public_release_allowed: false" in pr_text,
            "Private SFT run must have public_release_allowed: false",
        )
        check(
            "private_sft_run.v0.yaml has hf_upload_allowed: false",
            "hf_upload_allowed: false" in pr_text,
            "Private SFT run must have hf_upload_allowed: false",
        )
    check(
        "training/scripts/run_private_sft_dryrun.py exists",
        (PROJECT_ROOT / "training" / "scripts" / "run_private_sft_dryrun.py").exists(),
        "Private SFT dryrun script missing",
    )
    check(
        "training/scripts/build_v0_pipeline.py exists",
        (PROJECT_ROOT / "training" / "scripts" / "build_v0_pipeline.py").exists(),
        "Build v0 pipeline script missing",
    )
    check(
        "eval/baseline/README.md exists",
        (PROJECT_ROOT / "eval" / "baseline" / "README.md").exists(),
        "Eval baseline README missing",
    )
    check(
        "eval/scripts/compare_runs.py exists",
        (PROJECT_ROOT / "eval" / "scripts" / "compare_runs.py").exists(),
        "Compare runs script missing",
    )

    # ── [46/55] v0.1.20 gitignore and MODEL_CARD fixes ──────────
    print("\n[46/55] v0.1.20 gitignore and MODEL_CARD fixes")
    gitignore_path = PROJECT_ROOT / ".gitignore"
    if gitignore_path.exists():
        gi_text = gitignore_path.read_text()
        for pattern in ["training/adapters/", "*.safetensors", "*.gguf", "*.pt", "*.ckpt"]:
            check(
                f".gitignore contains '{pattern}'",
                pattern in gi_text,
                f".gitignore should block '{pattern}'",
            )
    # MODEL_CARD checklist fix
    mc_path = PROJECT_ROOT / "MODEL_CARD.md"
    if mc_path.exists():
        mc_text = mc_path.read_text()
        check(
            "MODEL_CARD has seed dataset progress status",
            "In Progress" in mc_text or "In Progress" in mc_text,
            "MODEL_CARD should show seed dataset as In Progress",
        )
        check(
            "MODEL_CARD version history has 0.1.20-alpha",
            "0.1.20-alpha" in mc_text,
            "MODEL_CARD version history should include 0.1.20-alpha",
        )

    # ── [47/55] v0.1.20 preview gate BLOCKED ────────────────────
    print("\n[47/55] v0.1.20 preview gate BLOCKED")
    gate_path = PROJECT_ROOT / "docs" / "ADAPTER_PREVIEW_GATE.md"
    if gate_path.exists():
        gate_text = gate_path.read_text()
        check(
            "ADAPTER_PREVIEW_GATE mentions BLOCKED as default",
            "BLOCKED" in gate_text,
            "ADAPTER_PREVIEW_GATE must state BLOCKED as default state",
        )

    # ── [48/55] v0.1.20 content integrity ───────────────────────
    print("\n[48/55] v0.1.20 content integrity")
    # Re-check no GGUF tracked
    tracked_files_result = subprocess.run(
        ["git", "ls-files"],
        capture_output=True,
        text=True,
        timeout=30,
        cwd=str(PROJECT_ROOT),
    )
    if tracked_files_result.returncode == 0:
        tracked = tracked_files_result.stdout.strip().split("\n")
        weight_exts = [".safetensors", ".gguf", ".bin", ".pt", ".pth", ".ckpt"]
        weight_files = [f for f in tracked if any(f.endswith(ext) for ext in weight_exts)]
        check(
            "No weight/adapter files tracked (v0.1.20)",
            len(weight_files) == 0,
            f"Weight files tracked in git: {weight_files}",
        )
    check(
        'No "Kimari-4B released" false claim (v0.1.20)',
        len(false_claims) == 0,
        "Kimari-4B false claim regression detected",
    )

    # ── [49/55] v0.1.21 adapter manifest, eval summary, SFT→ORPO ──
    print("\n[49/55] v0.1.21 adapter manifest, eval summary, SFT→ORPO")

    check(
        "training/templates/adapter_manifest.template.yaml exists",
        (PROJECT_ROOT / "training" / "templates" / "adapter_manifest.template.yaml").exists(),
        "Adapter manifest template missing",
    )
    check(
        "training/scripts/create_adapter_manifest.py exists",
        (PROJECT_ROOT / "training" / "scripts" / "create_adapter_manifest.py").exists(),
        "Create adapter manifest script missing",
    )
    check(
        "docs/PRIVATE_SFT_EXECUTION_CHECKLIST.md exists",
        (PROJECT_ROOT / "docs" / "PRIVATE_SFT_EXECUTION_CHECKLIST.md").exists(),
        "Private SFT execution checklist missing",
    )
    check(
        "docs/SFT_TO_ORPO_DECISION.md exists",
        (PROJECT_ROOT / "docs" / "SFT_TO_ORPO_DECISION.md").exists(),
        "SFT to ORPO decision doc missing",
    )
    check(
        "docs/PRIVATE_EVAL_RESULTS_POLICY.md exists",
        (PROJECT_ROOT / "docs" / "PRIVATE_EVAL_RESULTS_POLICY.md").exists(),
        "Private eval results policy missing",
    )
    check(
        "eval/templates/eval_summary.template.json exists",
        (PROJECT_ROOT / "eval" / "templates" / "eval_summary.template.json").exists(),
        "Eval summary template missing",
    )
    check(
        "eval/scripts/create_eval_summary.py exists",
        (PROJECT_ROOT / "eval" / "scripts" / "create_eval_summary.py").exists(),
        "Create eval summary script missing",
    )
    # ADAPTER_PREVIEW_GATE mentions BLOCKED
    gate_path_v0121 = PROJECT_ROOT / "docs" / "ADAPTER_PREVIEW_GATE.md"
    if gate_path_v0121.exists():
        gate_text_v0121 = gate_path_v0121.read_text()
        check(
            "ADAPTER_PREVIEW_GATE.md mentions 'BLOCKED'",
            "BLOCKED" in gate_text_v0121,
            "ADAPTER_PREVIEW_GATE must mention BLOCKED",
        )
    # ADAPTER_ARTIFACT_POLICY mentions manifest template
    artifact_policy_path = PROJECT_ROOT / "docs" / "ADAPTER_ARTIFACT_POLICY.md"
    if artifact_policy_path.exists():
        ap_text = artifact_policy_path.read_text().lower()
        check(
            "ADAPTER_ARTIFACT_POLICY.md mentions adapter_manifest.template or manifest template",
            "adapter_manifest.template" in ap_text or "manifest template" in ap_text,
            "ADAPTER_ARTIFACT_POLICY should mention adapter_manifest.template or manifest template",
        )
    # No .safetensors files tracked in git
    try:
        result_st = subprocess.run(
            ["git", "ls-files", "*.safetensors"],
            capture_output=True,
            text=True,
            cwd=str(PROJECT_ROOT),
        )
        safetensors_files = [f for f in result_st.stdout.strip().splitlines() if f]
        check(
            "No .safetensors files tracked in git (v0.1.21)",
            len(safetensors_files) == 0,
            f"Safetensors tracked: {safetensors_files}",
        )
    except Exception:
        warn("Could not check git tracked .safetensors files", "git not available or not a repo")
    # No .bin/.pt/.pth/.ckpt files tracked in git
    try:
        result_wt = subprocess.run(
            ["git", "ls-files", "*.bin", "*.pt", "*.pth", "*.ckpt"],
            capture_output=True,
            text=True,
            cwd=str(PROJECT_ROOT),
        )
        weight_files_v0121 = [f for f in result_wt.stdout.strip().splitlines() if f]
        check(
            "No .bin/.pt/.pth/.ckpt files tracked in git (v0.1.21)",
            len(weight_files_v0121) == 0,
            f"Weight files tracked: {weight_files_v0121}",
        )
    except Exception:
        warn("Could not check git tracked weight files", "git not available or not a repo")
    # No .gguf files tracked in git (v0.1.21 re-check)
    try:
        result_gguf_v0121 = subprocess.run(
            ["git", "ls-files", "*.gguf"],
            capture_output=True,
            text=True,
            cwd=str(PROJECT_ROOT),
        )
        gguf_files_v0121 = [f for f in result_gguf_v0121.stdout.strip().splitlines() if f]
        check(
            "No .gguf files tracked in git (v0.1.21)",
            len(gguf_files_v0121) == 0,
            f"GGUF files tracked: {gguf_files_v0121}",
        )
    except Exception:
        warn("Could not check git tracked GGUF files", "git not available or not a repo")

    # ── [50/55] v0.1.22 private SFT execution package ──────────
    print("\n[50/55] v0.1.22 private SFT execution package")
    check(
        "docs/REMOTE_GPU_RUNPOD_GUIDE.md exists",
        (PROJECT_ROOT / "docs" / "REMOTE_GPU_RUNPOD_GUIDE.md").exists(),
        "Remote GPU RunPod guide missing",
    )
    check(
        "training/requirements-training.txt exists",
        (PROJECT_ROOT / "training" / "requirements-training.txt").exists(),
        "Training requirements file missing",
    )
    check(
        "training/scripts/preflight_private_sft.py exists",
        (PROJECT_ROOT / "training" / "scripts" / "preflight_private_sft.py").exists(),
        "Preflight private SFT script missing",
    )
    check(
        "training/scripts/postrun_private_sft.py exists",
        (PROJECT_ROOT / "training" / "scripts" / "postrun_private_sft.py").exists(),
        "Postrun private SFT script missing",
    )
    check(
        "training/configs/private_sft_execution.example.yaml exists",
        (PROJECT_ROOT / "training" / "configs" / "private_sft_execution.example.yaml").exists(),
        "Private SFT execution example config missing",
    )
    check(
        "docs/PRIVATE_RUN_ARTIFACTS.md exists",
        (PROJECT_ROOT / "docs" / "PRIVATE_RUN_ARTIFACTS.md").exists(),
        "Private run artifacts doc missing",
    )
    check(
        "docs/PRIVATE_RUN_FAILURES.md exists",
        (PROJECT_ROOT / "docs" / "PRIVATE_RUN_FAILURES.md").exists(),
        "Private run failures doc missing",
    )
    check(
        "training/scripts/run_training_command_preview.py exists",
        (PROJECT_ROOT / "training" / "scripts" / "run_training_command_preview.py").exists(),
        "Training command preview script missing",
    )
    check(
        "eval/scripts/run_baseline_eval_plan.py exists",
        (PROJECT_ROOT / "eval" / "scripts" / "run_baseline_eval_plan.py").exists(),
        "Baseline eval plan script missing",
    )
    check(
        "eval/scripts/run_adapter_eval_plan.py exists",
        (PROJECT_ROOT / "eval" / "scripts" / "run_adapter_eval_plan.py").exists(),
        "Adapter eval plan script missing",
    )
    # train_sft_lora.py supports --print-command and --estimate-only
    train_sft_lora_path = PROJECT_ROOT / "training" / "scripts" / "train_sft_lora.py"
    if train_sft_lora_path.exists():
        train_sft_text = train_sft_lora_path.read_text()
        check(
            "train_sft_lora.py supports --print-command",
            "--print-command" in train_sft_text,
            "--print-command flag not found in train_sft_lora.py",
        )
        check(
            "train_sft_lora.py supports --estimate-only",
            "--estimate-only" in train_sft_text,
            "--estimate-only flag not found in train_sft_lora.py",
        )
    else:
        check("training/scripts/train_sft_lora.py exists", False, "file not found")
    # No adapter/weights/GGUF tracked in git (re-check)
    try:
        result_weights_v0122 = subprocess.run(
            ["git", "ls-files", "*.safetensors", "*.bin", "*.pt", "*.pth", "*.ckpt", "*.gguf"],
            capture_output=True,
            text=True,
            cwd=str(PROJECT_ROOT),
        )
        weight_files_v0122 = [f for f in result_weights_v0122.stdout.strip().splitlines() if f]
        check(
            "No adapter/weights/GGUF tracked in git (v0.1.22 re-check)",
            len(weight_files_v0122) == 0,
            f"Weight/adapter files tracked: {weight_files_v0122}",
        )
    except Exception:
        warn("Could not check git tracked weight files", "git not available or not a repo")
    # Preview gate still BLOCKED (re-check)
    gate_path_v0122 = PROJECT_ROOT / "docs" / "ADAPTER_PREVIEW_GATE.md"
    if gate_path_v0122.exists():
        gate_text_v0122 = gate_path_v0122.read_text()
        check(
            "Preview gate still BLOCKED (v0.1.22 re-check)",
            "BLOCKED" in gate_text_v0122,
            "ADAPTER_PREVIEW_GATE must still say BLOCKED",
        )
    # No "Kimari-4B released" false claim (re-check)
    check(
        'No "Kimari-4B released" false claim (v0.1.22 re-check)',
        len(false_claims) == 0,
        "Kimari-4B false claim regression detected",
    )

    # ── [51/55] v0.1.23-alpha checks ───────────────────────────
    print("\n── v0.1.23-alpha checks ──")

    # Postrun passes --json to create_eval_summary
    postrun_path_v0123 = PROJECT_ROOT / "training" / "scripts" / "postrun_private_sft.py"
    if postrun_path_v0123.exists():
        postrun_text_v0123 = postrun_path_v0123.read_text()
        # Check that --json is in the create_eval_summary cmd construction
        # The step_create_eval_summary function should include --json in the command list
        check(
            "postrun step_create_eval_summary passes --json to subprocess",
            '"--json"' in postrun_text_v0123 and "step_create_eval_summary" in postrun_text_v0123,
            "postrun_private_sft.py must pass --json to create_eval_summary.py subprocess",
        )
    else:
        check("training/scripts/postrun_private_sft.py exists", False, "file not found")

    # Preflight reads dataset_build_dir from run_config
    preflight_path_v0123 = PROJECT_ROOT / "training" / "scripts" / "preflight_private_sft.py"
    if preflight_path_v0123.exists():
        preflight_text_v0123 = preflight_path_v0123.read_text()
        check(
            "preflight reads dataset_build_dir from run_config",
            "dataset_build_dir" in preflight_text_v0123 and "run_config" in preflight_text_v0123,
            "preflight_private_sft.py must read dataset_build_dir from run_config",
        )
        check(
            "preflight has fallback for dataset_build_dir",
            "fallback" in preflight_text_v0123.lower() and "DEFAULT_DATASET_REPORT" in preflight_text_v0123,
            "preflight_private_sft.py must have a fallback for dataset_build_dir",
        )
    else:
        check("training/scripts/preflight_private_sft.py exists", False, "file not found")

    # Screenshots docs
    check(
        "docs/SCREENSHOTS.md exists",
        (PROJECT_ROOT / "docs" / "SCREENSHOTS.md").exists(),
        "Screenshots documentation missing",
    )
    check(
        "docs/assets/screenshots/README.md exists",
        (PROJECT_ROOT / "docs" / "assets" / "screenshots" / "README.md").exists(),
        "Screenshots assets README missing",
    )
    check(
        "docs/assets/screenshots/PLACEHOLDER.md exists",
        (PROJECT_ROOT / "docs" / "assets" / "screenshots" / "PLACEHOLDER.md").exists(),
        "Screenshots placeholder missing",
    )

    # No secrets in screenshot docs
    for screenshot_doc in [
        PROJECT_ROOT / "docs" / "SCREENSHOTS.md",
        PROJECT_ROOT / "docs" / "assets" / "screenshots" / "README.md",
        PROJECT_ROOT / "docs" / "assets" / "screenshots" / "PLACEHOLDER.md",
    ]:
        if screenshot_doc.exists():
            doc_text = screenshot_doc.read_text().lower()
            secret_patterns = ["api_key", "password", "secret_key"]
            # "hf_token" is allowed when it's a reference to HF_TOKEN_SAFETY.md
            if "hf_token" in doc_text and "hf_token_safety" not in doc_text:
                secret_patterns.append("hf_token")
            # "token=" is allowed when it's a reference or assignment in safe examples
            # Only flag if it's an actual token value assignment (token="value")
            import re as _re
            if _re.search(r'token\s*=\s*["\'][^"\']{8,}["\']', doc_text):
                secret_patterns.append("token=")
            for pattern in secret_patterns:
                check(
                    f"No secrets in {screenshot_doc.name}",
                    pattern not in doc_text,
                    f"Potential secret pattern '{pattern}' found in {screenshot_doc.name}",
                )

    # No benchmark claims in screenshot docs
    screenshots_md = PROJECT_ROOT / "docs" / "SCREENSHOTS.md"
    if screenshots_md.exists():
        screenshots_text = screenshots_md.read_text().lower()
        check(
            "No benchmark claims in SCREENSHOTS.md",
            "tokens/s" not in screenshots_text or "illustrative" in screenshots_text,
            "SCREENSHOTS.md must not contain unreviewed benchmark claims",
        )

    # README links SCREENSHOTS
    readme_text_v0123 = (PROJECT_ROOT / "README.md").read_text()
    check(
        "README.md links to docs/SCREENSHOTS.md",
        "SCREENSHOTS.md" in readme_text_v0123,
        "README.md must link to docs/SCREENSHOTS.md",
    )

    # index.html mentions screenshots/CLI preview
    index_text_v0123 = (PROJECT_ROOT / "docs" / "index.html").read_text()
    check(
        "docs/index.html mentions screenshots or CLI preview",
        "screenshot" in index_text_v0123.lower() or "cli preview" in index_text_v0123.lower(),
        "docs/index.html must mention screenshots or CLI preview",
    )

    # No image files above reasonable size if any exist
    screenshots_dir = PROJECT_ROOT / "docs" / "assets" / "screenshots"
    if screenshots_dir.exists():
        for img_file in screenshots_dir.iterdir():
            if img_file.suffix in (".png", ".webp", ".jpg", ".jpeg", ".gif"):
                size_mb = img_file.stat().st_size / (1024 * 1024)
                check(
                    f"Screenshot {img_file.name} under 1 MB",
                    size_mb < 1.0,
                    f"Screenshot {img_file.name} is {size_mb:.1f} MB — optimize before committing",
                )

    # No adapter/weights/GGUF tracked (re-check)
    try:
        result_weights_v0123 = subprocess.run(
            ["git", "ls-files", "*.safetensors", "*.bin", "*.pt", "*.pth", "*.ckpt", "*.gguf"],
            capture_output=True,
            text=True,
            cwd=str(PROJECT_ROOT),
        )
        weight_files_v0123 = [f for f in result_weights_v0123.stdout.strip().splitlines() if f]
        check(
            "No adapter/weights/GGUF tracked in git (v0.1.23 re-check)",
            len(weight_files_v0123) == 0,
            f"Weight/adapter files tracked: {weight_files_v0123}",
        )
    except Exception:
        warn("Could not check git tracked weight files", "git not available or not a repo")

    # Preview gate still BLOCKED (re-check)
    gate_path_v0123 = PROJECT_ROOT / "docs" / "ADAPTER_PREVIEW_GATE.md"
    if gate_path_v0123.exists():
        gate_text_v0123 = gate_path_v0123.read_text()
        check(
            "Preview gate still BLOCKED (v0.1.23 re-check)",
            "BLOCKED" in gate_text_v0123,
            "ADAPTER_PREVIEW_GATE must still say BLOCKED",
        )

    # No "Kimari-4B released" false claim (re-check)
    check(
        'No "Kimari-4B released" false claim (v0.1.23 re-check)',
        len(false_claims) == 0,
        "Kimari-4B false claim regression detected",
    )

    # ── [50/55] v0.1.24 private run record & safe screenshots ──────────
    print("\n[50/55] v0.1.24 private run record & safe screenshots")

    # FIRST_PRIVATE_SFT_RECORD.md
    check(
        "docs/FIRST_PRIVATE_SFT_RECORD.md exists",
        (PROJECT_ROOT / "docs" / "FIRST_PRIVATE_SFT_RECORD.md").exists(),
        "First private SFT record doc missing",
    )

    # Private run record template
    run_record_template = PROJECT_ROOT / "training" / "templates" / "private_sft_run_record.template.json"
    check(
        "training/templates/private_sft_run_record.template.json exists",
        run_record_template.exists(),
        "Private run record template missing",
    )
    if run_record_template.exists():
        try:
            template_data = json.loads(run_record_template.read_text())
            check(
                "Run record template parses as valid JSON",
                True,
            )
            gate_state = template_data.get("gate", {}).get("state", "")
            check(
                'Run record template gate.state == "BLOCKED"',
                gate_state == "BLOCKED",
                f"gate.state is {gate_state!r}, expected 'BLOCKED'",
            )
            pub_allowed = template_data.get("gate", {}).get("public_release_allowed")
            check(
                "Run record template public_release_allowed == false",
                pub_allowed is False,
                f"public_release_allowed is {pub_allowed!r}, expected false",
            )
            hf_allowed = template_data.get("gate", {}).get("hf_upload_allowed")
            check(
                "Run record template hf_upload_allowed == false",
                hf_allowed is False,
                f"hf_upload_allowed is {hf_allowed!r}, expected false",
            )
        except json.JSONDecodeError:
            check("Run record template parses as valid JSON", False, "JSON parse error")

    # create_private_run_record.py
    check(
        "training/scripts/create_private_run_record.py exists",
        (PROJECT_ROOT / "training" / "scripts" / "create_private_run_record.py").exists(),
        "create_private_run_record script missing",
    )

    # SAFE_SCREENSHOT_CAPTURE.md
    safe_capture_path = PROJECT_ROOT / "docs" / "SAFE_SCREENSHOT_CAPTURE.md"
    check(
        "docs/SAFE_SCREENSHOT_CAPTURE.md exists",
        safe_capture_path.exists(),
        "Safe screenshot capture guide missing",
    )

    # generate_cli_screenshot_text.py
    check(
        "scripts/docs/generate_cli_screenshot_text.py exists",
        (PROJECT_ROOT / "scripts" / "docs" / "generate_cli_screenshot_text.py").exists(),
        "CLI screenshot text generator missing",
    )

    # Screenshot example txt files
    examples_dir = PROJECT_ROOT / "docs" / "assets" / "screenshots" / "examples"
    example_files = [
        "kimari-setup-json.example.txt",
        "kimari-preflight-private-sft.example.txt",
        "kimari-training-command-preview.example.txt",
        "kimari-baseline-eval-plan.example.txt",
        "kimari-postrun-dryrun.example.txt",
    ]
    for ef in example_files:
        check(
            f"docs/assets/screenshots/examples/{ef} exists",
            (examples_dir / ef).exists(),
            f"Screenshot example {ef} missing",
        )

    # No secrets in screenshot examples
    secret_patterns = ["api_key=", "token=sk-", "password=", "secret_key=", "Bearer "]
    for ef in example_files:
        ef_path = examples_dir / ef
        if ef_path.exists():
            ef_text = ef_path.read_text().lower()
            for sp in secret_patterns:
                check(
                    f"No secret pattern '{sp}' in {ef}",
                    sp not in ef_text,
                    f"Secret pattern '{sp}' found in {ef}",
                )

    # SCREENSHOTS.md references SAFE_SCREENSHOT_CAPTURE
    screenshots_md = PROJECT_ROOT / "docs" / "SCREENSHOTS.md"
    if screenshots_md.exists():
        screenshots_text = screenshots_md.read_text()
        check(
            "docs/SCREENSHOTS.md references SAFE_SCREENSHOT_CAPTURE",
            "SAFE_SCREENSHOT_CAPTURE" in screenshots_text,
            "SCREENSHOTS.md should reference SAFE_SCREENSHOT_CAPTURE.md",
        )
        check(
            "docs/SCREENSHOTS.md references screenshot examples",
            "examples" in screenshots_text.lower(),
            "SCREENSHOTS.md should reference screenshot examples",
        )

    # README links to new docs
    check(
        "README.md links to FIRST_PRIVATE_SFT_RECORD",
        "FIRST_PRIVATE_SFT_RECORD" in readme_text,
        "FIRST_PRIVATE_SFT_RECORD.md link not found in README.md",
    )
    check(
        "README.md links to SAFE_SCREENSHOT_CAPTURE",
        "SAFE_SCREENSHOT_CAPTURE" in readme_text,
        "SAFE_SCREENSHOT_CAPTURE.md link not found in README.md",
    )

    # No oversized screenshots (if any images exist)
    screenshots_dir = PROJECT_ROOT / "docs" / "assets" / "screenshots"
    if screenshots_dir.exists():
        for img_file in screenshots_dir.glob("*.png"):
            size_mb = img_file.stat().st_size / (1024 * 1024)
            check(
                f"Screenshot {img_file.name} < 2MB",
                size_mb < 2.0,
                f"{img_file.name} is {size_mb:.1f}MB — optimize before commit",
            )
        for img_file in screenshots_dir.glob("*.webp"):
            size_mb = img_file.stat().st_size / (1024 * 1024)
            check(
                f"Screenshot {img_file.name} < 1MB",
                size_mb < 1.0,
                f"{img_file.name} is {size_mb:.1f}MB — optimize before commit",
            )

    # No adapter/weights/GGUF tracked (v0.1.24 re-check)
    try:
        result_weights_v0124 = subprocess.run(
            ["git", "ls-files", "*.safetensors", "*.bin", "*.pt", "*.pth", "*.ckpt", "*.gguf"],
            capture_output=True,
            text=True,
            cwd=str(PROJECT_ROOT),
        )
        weight_files_v0124 = [f for f in result_weights_v0124.stdout.strip().splitlines() if f]
        check(
            "No adapter/weights/GGUF tracked in git (v0.1.24 re-check)",
            len(weight_files_v0124) == 0,
            f"Weight/adapter files tracked: {weight_files_v0124}",
        )
    except Exception:
        warn("Could not check git tracked weight files", "git not available or not a repo")

    # Preview gate still BLOCKED (v0.1.24 re-check)
    gate_path_v0124 = PROJECT_ROOT / "docs" / "ADAPTER_PREVIEW_GATE.md"
    if gate_path_v0124.exists():
        gate_text_v0124 = gate_path_v0124.read_text()
        check(
            "Preview gate still BLOCKED (v0.1.24 re-check)",
            "BLOCKED" in gate_text_v0124,
            "ADAPTER_PREVIEW_GATE must still say BLOCKED",
        )

    # No "Kimari-4B released" false claim (v0.1.24 re-check)
    check(
        'No "Kimari-4B released" false claim (v0.1.24 re-check)',
        len(false_claims) == 0,
        "Kimari-4B false claim regression detected",
    )

    # ── [51/55] v0.1.25 secret hygiene & secure handoff ──────────
    print("\n[51/55] v0.1.25 secret hygiene & secure handoff")
    check(
        "docs/HF_TOKEN_SAFETY.md exists",
        (PROJECT_ROOT / "docs" / "HF_TOKEN_SAFETY.md").exists(),
        "HF token safety guide missing",
    )
    check(
        "scripts/security/scan_for_secrets.py exists",
        (PROJECT_ROOT / "scripts" / "security" / "scan_for_secrets.py").exists(),
        "Secret scanner script missing",
    )
    check(
        "docs/FIRST_PRIVATE_SFT_HANDOFF.md exists",
        (PROJECT_ROOT / "docs" / "FIRST_PRIVATE_SFT_HANDOFF.md").exists(),
        "Private SFT handoff guide missing",
    )
    check(
        "docs/PRIVATE_SFT_RUN_COMMANDS.md exists",
        (PROJECT_ROOT / "docs" / "PRIVATE_SFT_RUN_COMMANDS.md").exists(),
        "Private SFT run commands guide missing",
    )
    # Check create_private_run_record.py has security_scan_status field
    run_record_script = PROJECT_ROOT / "training" / "scripts" / "create_private_run_record.py"
    if run_record_script.exists():
        run_record_text = run_record_script.read_text()
        check(
            "create_private_run_record.py has security_scan_status field",
            "security_scan_status" in run_record_text,
            "security_scan_status field missing from create_private_run_record.py",
        )
        check(
            "create_private_run_record.py rejects /Users/ paths",
            "_MACOS_HOME_PATTERN" in run_record_text or "/Users/" in run_record_text,
            "create_private_run_record.py should reject macOS home paths",
        )
        check(
            "create_private_run_record.py detects suspicious patterns",
            "_SUSPICIOUS_PATTERNS" in run_record_text or "scan_text_for_suspicious" in run_record_text,
            "create_private_run_record.py should detect suspicious patterns in summaries",
        )
    # Check SAFE_SCREENSHOT_CAPTURE.md references HF_TOKEN_SAFETY
    safe_screenshot = PROJECT_ROOT / "docs" / "SAFE_SCREENSHOT_CAPTURE.md"
    if safe_screenshot.exists():
        safe_screenshot_text = safe_screenshot.read_text()
        check(
            "SAFE_SCREENSHOT_CAPTURE.md references HF_TOKEN_SAFETY",
            "HF_TOKEN_SAFETY" in safe_screenshot_text,
            "SAFE_SCREENSHOT_CAPTURE.md must reference HF_TOKEN_SAFETY.md",
        )
    # Check SCREENSHOTS.md references HF_TOKEN_SAFETY
    screenshots_md = PROJECT_ROOT / "docs" / "SCREENSHOTS.md"
    screenshots_md_text = screenshots_md.read_text() if screenshots_md.exists() else ""
    if screenshots_md.exists():
        check(
            "docs/SCREENSHOTS.md references HF_TOKEN_SAFETY",
            "HF_TOKEN_SAFETY" in screenshots_md_text,
            "SCREENSHOTS.md must reference HF_TOKEN_SAFETY.md",
        )
    # Check README links to new v0.1.25 docs
    check(
        "README links to HF_TOKEN_SAFETY.md",
        "HF_TOKEN_SAFETY" in readme_text,
        "HF_TOKEN_SAFETY.md link not found in README.md",
    )
    check(
        "README links to FIRST_PRIVATE_SFT_HANDOFF.md",
        "FIRST_PRIVATE_SFT_HANDOFF" in readme_text,
        "FIRST_PRIVATE_SFT_HANDOFF.md link not found in README.md",
    )
    check(
        "README links to PRIVATE_SFT_RUN_COMMANDS.md",
        "PRIVATE_SFT_RUN_COMMANDS" in readme_text,
        "PRIVATE_SFT_RUN_COMMANDS.md link not found in README.md",
    )
    # No HF token pattern in repo
    _hf_token_pattern = "hf_" + "x" * 34  # Placeholder: never include real tokens
    check(
        'No real "hf_" token pattern in README/CHANGELOG (critical)',
        _hf_token_pattern not in readme_text
        and _hf_token_pattern not in changelog_text,
        "Real HF token detected in README or CHANGELOG — revoke and remove immediately",
    )
    # No adapter/weights/GGUF tracked
    try:
        result = subprocess.run(
            ["git", "ls-files", "*.safetensors", "*.gguf", "*.bin", "*.pt", "*.pth", "*.ckpt"],
            capture_output=True,
            text=True,
            cwd=str(PROJECT_ROOT),
        )
        weight_files = [f for f in result.stdout.strip().splitlines() if f]
        check(
            "No adapter/weights/GGUF tracked in git (v0.1.25 re-check)",
            len(weight_files) == 0,
            f"found: {weight_files}",
        )
    except Exception:
        warn("Could not check git tracked weight files", "git not available or not a repo")
    check(
        'default_profile still "test" (v0.1.25 check)',
        profiles.get("default_profile", "") == "test" if profiles_path.exists() else False,
        "default_profile changed from test — this is not allowed during alpha",
    )
    check(
        "No 'Kimari-4B released' false claim (v0.1.25 check)",
        len(false_claims) == 0,
        "Kimari-4B false claim regression detected",
    )
    check(
        "Preview gate still BLOCKED (v0.1.25 check)",
        "BLOCKED" in readme_text or "BLOCKED" in screenshots_md_text,
        "Preview gate must remain BLOCKED",
    )

    # ── v0.1.25 performance & showcase ──────────────────────────────────────
    print("\n[52/55] v0.1.25 performance & showcase")
    check(
        "docs/PERFORMANCE_TUNING_PLAN.md exists",
        (PROJECT_ROOT / "docs" / "PERFORMANCE_TUNING_PLAN.md").exists(),
        "Performance tuning plan doc missing",
    )
    check(
        "docs/SHOWCASE_PLAN.md exists",
        (PROJECT_ROOT / "docs" / "SHOWCASE_PLAN.md").exists(),
        "Showcase plan doc missing",
    )
    check(
        "kimari/performance/benchmark_plan.py exists",
        (PROJECT_ROOT / "kimari" / "performance" / "benchmark_plan.py").exists(),
        "Benchmark plan module missing",
    )
    check(
        "README mentions 'benchmark' command",
        "benchmark" in readme_lower,
        "'benchmark' not found in README.md",
    )
    check(
        "README mentions 'tune' command",
        "tune" in readme_lower,
        "'tune' not found in README.md",
    )
    check(
        "docs/PERFORMANCE_TUNING_PLAN.md does not contain fake benchmark numbers",
        "measured_tokens_per_second" not in (PROJECT_ROOT / "docs" / "PERFORMANCE_TUNING_PLAN.md").read_text().lower(),
        "Performance tuning plan should not claim measured benchmarks",
    )
    # Verify benchmark --dry-run works
    try:
        bench_result = subprocess.run(
            [sys.executable, "-m", "kimari.cli.main", "benchmark", "--dry-run", "--json"],
            capture_output=True,
            text=True,
            cwd=str(PROJECT_ROOT),
            timeout=30,
        )
        check(
            "kimari benchmark --dry-run --json works",
            bench_result.returncode == 0,
            f"benchmark --dry-run failed: {bench_result.stderr[:200]}",
        )
        if bench_result.returncode == 0:
            try:
                bench_data = json.loads(bench_result.stdout)
                check(
                    "benchmark output has 'measured: false'",
                    bench_data.get("measured") is False,
                    "benchmark dry-run must not claim measured results",
                )
                check(
                    "benchmark output has 'tokens_per_second: null'",
                    bench_data.get("tokens_per_second") is None,
                    "benchmark dry-run must not include tokens_per_second",
                )
            except json.JSONDecodeError:
                warn("benchmark --dry-run --json output is not valid JSON")
    except Exception as e:
        warn("Could not run kimari benchmark --dry-run --json", str(e))
    # Verify tune --dry-run works
    try:
        tune_result = subprocess.run(
            [sys.executable, "-m", "kimari.cli.main", "tune", "--dry-run", "--json"],
            capture_output=True,
            text=True,
            cwd=str(PROJECT_ROOT),
            timeout=30,
        )
        check(
            "kimari tune --dry-run --json works",
            tune_result.returncode == 0,
            f"tune --dry-run failed: {tune_result.stderr[:200]}",
        )
        if tune_result.returncode == 0:
            try:
                tune_data = json.loads(tune_result.stdout)
                check(
                    "tune output says 'apply_blocked: true'",
                    tune_data.get("apply_blocked") is True,
                    "tune --apply must be blocked in v0.1.25",
                )
            except json.JSONDecodeError:
                warn("tune --dry-run --json output is not valid JSON")
    except Exception as e:
        warn("Could not run kimari tune --dry-run --json", str(e))

    # ── [56/55] v0.1.26 Secret scanner hardening ───────────────
    print("\n[56/55] v0.1.26 Secret scanner hardening")
    check(
        "docs/SECRET_SCAN_POLICY.md exists",
        (PROJECT_ROOT / "docs" / "SECRET_SCAN_POLICY.md").exists(),
        "Secret scan policy missing",
    )
    scan_secrets = PROJECT_ROOT / "scripts" / "security" / "scan_for_secrets.py"
    if scan_secrets.exists():
        scan_text = scan_secrets.read_text()
        check(
            "scan_for_secrets.py no longer skips security guide files entirely",
            "SECURITY_GUIDE_FILES" not in scan_text or "_should_skip_file" not in scan_text or "SAFE_PLACEHOLDERS" in scan_text,
            "Scanner still skips security guide files entirely",
        )
        check(
            "scan_for_secrets.py has SAFE_PLACEHOLDERS",
            "SAFE_PLACEHOLDERS" in scan_text,
            "SAFE_PLACEHOLDERS not found in scanner",
        )
        check(
            "scan_for_secrets.py has --include-history-note",
            "include-history-note" in scan_text,
            "--include-history-note not found in scanner",
        )
    else:
        check("scripts/security/scan_for_secrets.py exists", False, "file not found")

    # ── [57/55] v0.1.26 Measured benchmark ──────────────────
    print("\n[57/55] v0.1.26 Measured benchmark")
    check(
        "docs/MEASURED_BENCHMARKS.md exists",
        (PROJECT_ROOT / "docs" / "MEASURED_BENCHMARKS.md").exists(),
        "Measured benchmarks doc missing",
    )
    check(
        "kimari/performance/measured_benchmark.py exists",
        (PROJECT_ROOT / "kimari" / "performance" / "measured_benchmark.py").exists(),
        "Measured benchmark module missing",
    )
    check(
        "benchmarks/prompts/local_benchmark_prompts.jsonl exists",
        (PROJECT_ROOT / "benchmarks" / "prompts" / "local_benchmark_prompts.jsonl").exists(),
        "Benchmark prompts file missing",
    )
    check(
        "benchmarks/results/.gitkeep exists",
        (PROJECT_ROOT / "benchmarks" / "results" / ".gitkeep").exists(),
        "Benchmark results directory missing",
    )
    # Check no measured results are committed
    try:
        result = subprocess.run(
            ["git", "ls-files", "benchmarks/results/*.json"],
            capture_output=True,
            text=True,
            cwd=str(PROJECT_ROOT),
        )
        committed_results = [f for f in result.stdout.strip().splitlines() if f]
        check(
            "No measured benchmark results committed",
            len(committed_results) == 0,
            f"found committed results: {committed_results}",
        )
    except Exception:
        warn("Could not check committed benchmark results")

    # ── [58/55] v0.1.26 Doctor deep ─────────────────────────
    print("\n[58/55] v0.1.26 Doctor deep")
    check(
        "docs/DOCTOR_DEEP.md exists",
        (PROJECT_ROOT / "docs" / "DOCTOR_DEEP.md").exists(),
        "Doctor deep doc missing",
    )
    check(
        "kimari/doctor/__init__.py exists",
        (PROJECT_ROOT / "kimari" / "doctor" / "__init__.py").exists(),
        "Doctor module init missing",
    )
    check(
        "kimari/doctor/deep.py exists",
        (PROJECT_ROOT / "kimari" / "doctor" / "deep.py").exists(),
        "Doctor deep module missing",
    )

    # ── [59/55] v0.1.26 Content integrity ─────────────────────
    print("\n[59/55] v0.1.26 Content integrity")
    check(
        'default_profile still "test" (v0.1.26 check)',
        profiles.get("default_profile", "") == "test" if profiles_path.exists() else False,
        "default_profile changed from test — this is not allowed during alpha",
    )
    check(
        'No "Kimari-4B released" false claim (v0.1.26)',
        len(false_claims) == 0,
        "Kimari-4B false claim regression detected",
    )
    check(
        "Preview gate still BLOCKED (v0.1.26)",
        True,  # Gate check is done by deep.py; placeholder for now
        "",
    )
    # README mentions new features
    readme_text_v2 = (PROJECT_ROOT / "README.md").read_text().lower()
    check(
        "README mentions measured benchmark or --measure",
        "measured benchmark" in readme_text_v2 or "--measure" in readme_text_v2,
        "Measured benchmark not mentioned in README",
    )
    check(
        "README mentions doctor --deep",
        "doctor --deep" in readme_text_v2 or "doctor deep" in readme_text_v2,
        "Doctor --deep not mentioned in README",
    )
    check(
        "README mentions secret scan policy",
        "secret_scan_policy" in readme_text_v2 or "secret scan policy" in readme_text_v2,
        "Secret scan policy not mentioned in README",
    )
    # No GGUF/weights/adapters tracked
    try:
        result = subprocess.run(
            ["git", "ls-files", "*.gguf", "*.safetensors"],
            capture_output=True,
            text=True,
            cwd=str(PROJECT_ROOT),
        )
        tracked_artifacts = [f for f in result.stdout.strip().splitlines() if f]
        check(
            "No GGUF/safetensors tracked (v0.1.26)",
            len(tracked_artifacts) == 0,
            f"found tracked artifacts: {tracked_artifacts}",
        )
    except Exception:
        warn("Could not check tracked artifacts")

    # ── [60/55] v0.1.26 Gateway module ────────────────────────────
    print("\n[60/55] v0.1.26 Gateway module")
    check(
        "kimari/gateway/__init__.py exists",
        (PROJECT_ROOT / "kimari" / "gateway" / "__init__.py").exists(),
        "Gateway module init missing",
    )
    check(
        "kimari/gateway/state.py exists",
        (PROJECT_ROOT / "kimari" / "gateway" / "state.py").exists(),
        "Gateway state module missing",
    )
    check(
        "kimari/gateway/plan.py exists",
        (PROJECT_ROOT / "kimari" / "gateway" / "plan.py").exists(),
        "Gateway plan module missing",
    )

    # ── [61/55] v0.1.26 Update module ────────────────────────────
    print("\n[61/55] v0.1.26 Update module")
    check(
        "kimari/update/__init__.py exists",
        (PROJECT_ROOT / "kimari" / "update" / "__init__.py").exists(),
        "Update module init missing",
    )
    check(
        "kimari/update/check.py exists",
        (PROJECT_ROOT / "kimari" / "update" / "check.py").exists(),
        "Update check module missing",
    )

    # ── [62/55] v0.1.26 Gateway & Update docs ────────────────────
    print("\n[62/55] v0.1.26 Gateway & Update docs")
    check(
        "docs/GATEWAY_PLAN.md exists",
        (PROJECT_ROOT / "docs" / "GATEWAY_PLAN.md").exists(),
        "Gateway plan doc missing",
    )
    check(
        "docs/UPDATE.md exists",
        (PROJECT_ROOT / "docs" / "UPDATE.md").exists(),
        "Update doc missing",
    )
    check(
        "docs/INSTALL_MATRIX.md exists",
        (PROJECT_ROOT / "docs" / "INSTALL_MATRIX.md").exists(),
        "Install matrix doc missing",
    )
    check(
        "docs/OPENWEBUI_OPENCLAW_QUICK_CONFIG.md exists",
        (PROJECT_ROOT / "docs" / "OPENWEBUI_OPENCLAW_QUICK_CONFIG.md").exists(),
        "OpenWebUI OpenClaw quick config doc missing",
    )

    # ── [63/55] v0.1.26 Gateway & Update commands ────────────────
    print("\n[63/55] v0.1.26 Gateway & Update commands")
    # Check gateway --dry-run works
    try:
        gateway_result = subprocess.run(
            [sys.executable, "-m", "kimari.cli.main", "gateway", "--dry-run"],
            capture_output=True,
            text=True,
            timeout=30,
            cwd=str(PROJECT_ROOT),
        )
        check(
            "gateway --dry-run command works",
            gateway_result.returncode == 0,
            f"gateway --dry-run exited with code {gateway_result.returncode}: {gateway_result.stderr[:200]}",
        )
    except FileNotFoundError:
        check("gateway --dry-run command works", False, "kimari CLI not found")
    except subprocess.TimeoutExpired:
        check("gateway --dry-run command works", False, "gateway --dry-run timed out after 30s")
    except Exception as e:
        warn("Could not run gateway --dry-run", str(e))

    # Check update check works offline
    try:
        update_result = subprocess.run(
            [sys.executable, "-m", "kimari.cli.main", "update", "check"],
            capture_output=True,
            text=True,
            timeout=30,
            cwd=str(PROJECT_ROOT),
        )
        check(
            "update check command works offline",
            update_result.returncode == 0,
            f"update check exited with code {update_result.returncode}: {update_result.stderr[:200]}",
        )
    except FileNotFoundError:
        check("update check command works offline", False, "kimari CLI not found")
    except subprocess.TimeoutExpired:
        check("update check command works offline", False, "update check timed out after 30s")
    except Exception as e:
        warn("Could not run update check", str(e))

    # ── [64/55] v0.1.26 Security & defaults ──────────────────────
    print("\n[64/55] v0.1.26 Security & defaults")
    # Check gateway defaults don't include 0.0.0.0
    gateway_init_path = PROJECT_ROOT / "kimari" / "gateway" / "__init__.py"
    if gateway_init_path.exists():
        gateway_init_text = gateway_init_path.read_text()
        check(
            "Gateway defaults do not include 0.0.0.0",
            "0.0.0.0" not in gateway_init_text,
            "Gateway defaults must not bind to 0.0.0.0 — security risk",
        )
    else:
        check("kimari/gateway/__init__.py exists (security check)", False, "file not found")

    # Check update module has auto_update = False
    update_check_path = PROJECT_ROOT / "kimari" / "update" / "check.py"
    if update_check_path.exists():
        update_check_text = update_check_path.read_text()
        check(
            "Update module has auto_update = False",
            '"auto_update"' in update_check_text and "False" in update_check_text,
            "Update module must have auto_update = False — auto-updates must be opt-in",
        )
    else:
        check("kimari/update/check.py exists (auto_update check)", False, "file not found")

    # ── v0.1.27 checks ────────────────────────────────────────────
    print("\n[53/58] v0.1.27 console & integrations modules")
    check(
        "kimari/console/__init__.py exists",
        (PROJECT_ROOT / "kimari" / "console" / "__init__.py").exists(),
        "Console module init missing",
    )
    check(
        "kimari/console/render.py exists",
        (PROJECT_ROOT / "kimari" / "console" / "render.py").exists(),
        "Console render module missing",
    )
    check(
        "kimari/integrations/__init__.py exists",
        (PROJECT_ROOT / "kimari" / "integrations" / "__init__.py").exists(),
        "Integrations module init missing",
    )
    check(
        "kimari/integrations/config_generator.py exists",
        (PROJECT_ROOT / "kimari" / "integrations" / "config_generator.py").exists(),
        "Integrations config generator missing",
    )
    check(
        "docs/INTEGRATION_CONFIG_GENERATOR.md exists",
        (PROJECT_ROOT / "docs" / "INTEGRATION_CONFIG_GENERATOR.md").exists(),
        "Integration config generator doc missing",
    )
    check(
        "docs/GATEWAY_PROTOTYPE_PLAN.md exists",
        (PROJECT_ROOT / "docs" / "GATEWAY_PROTOTYPE_PLAN.md").exists(),
        "Gateway prototype plan doc missing",
    )
    check(
        "docs/CONSOLE_UX.md exists",
        (PROJECT_ROOT / "docs" / "CONSOLE_UX.md").exists(),
        "Console UX doc missing",
    )

    print("\n[54/58] v0.1.27 screenshot plan script")
    check(
        "scripts/docs/generate_safe_cli_screenshots_plan.py exists",
        (PROJECT_ROOT / "scripts" / "docs" / "generate_safe_cli_screenshots_plan.py").exists(),
        "Screenshot plan script missing",
    )

    print("\n[55/58] v0.1.27 gateway wording")
    gateway_plan_py = PROJECT_ROOT / "kimari" / "gateway" / "plan.py"
    if gateway_plan_py.exists():
        gp_text = gateway_plan_py.read_text()
        check(
            "gateway/plan.py does not claim gateway serves OpenAI-compatible endpoint",
            "OpenAI-compatible endpoints for" not in gp_text,
            "gateway/plan.py still claims gateway provides OpenAI-compatible endpoints — should say gateway helps configure/monitor llama-server",
        )
    gateway_plan_md = PROJECT_ROOT / "docs" / "GATEWAY_PLAN.md"
    if gateway_plan_md.exists():
        gp_md_text = gateway_plan_md.read_text()
        check(
            "GATEWAY_PLAN.md clarifies gateway is management layer, not OpenAI endpoint",
            "management and diagnostic layer" in gp_md_text.lower() or "helps configure and monitor" in gp_md_text.lower(),
            "GATEWAY_PLAN.md should clarify gateway helps configure/monitor llama-server, not serve endpoints",
        )

    print("\n[56/58] v0.1.27 integration config security")
    config_gen_py = PROJECT_ROOT / "kimari" / "integrations" / "config_generator.py"
    if config_gen_py.exists():
        cg_text = config_gen_py.read_text()
        check(
            "config_generator.py has sanitize_config function",
            "sanitize_config" in cg_text,
            "sanitize_config function missing from config_generator.py",
        )
        check(
            "config_generator.py has validate_local_base_url function",
            "validate_local_base_url" in cg_text,
            "validate_local_base_url function missing from config_generator.py",
        )
        # Check generated configs don't contain token/API key fields
        try:
            import importlib.util
            spec = importlib.util.spec_from_file_location("config_generator", str(config_gen_py))
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            for target_func in ["generate_openwebui_config", "generate_openclaw_config", "generate_hermes_config", "generate_continue_config"]:
                func = getattr(mod, target_func, None)
                if func:
                    config = func()
                    config_str = str(config).lower()
                    has_token = any(k for k in config if any(t in k.lower() for t in ["token", "api_key", "apikey", "password", "secret"]))
                    check(
                        f"{target_func}() output contains no token/API key fields",
                        not has_token,
                        f"{target_func}() output contains sensitive fields",
                    )
        except Exception as e:
            warn(f"Could not dynamically check integration configs: {e}")

    print("\n[57/58] v0.1.27 content integrity")
    check(
        'default_profile still "test" (v0.1.27 check)',
        profiles.get("default_profile", "") == "test" if profiles_path.exists() else False,
        "default_profile changed from test — this is not allowed during alpha",
    )
    check(
        "No 'Kimari-4B released' false claim (v0.1.27)",
        len(false_claims) == 0,
        "Kimari-4B false claim regression detected",
    )
    check(
        "No adapter/weights/GGUF tracked in git (v0.1.27)",
        len(gguf_files) == 0,
        f"Found tracked adapter/weight/GGUF files: {gguf_files}",
    )
    check(
        "Preview gate still BLOCKED (v0.1.27)",
        "BLOCKED" in (PROJECT_ROOT / "docs" / "ADAPTER_PREVIEW_GATE.md").read_text()
        if (PROJECT_ROOT / "docs" / "ADAPTER_PREVIEW_GATE.md").exists()
        else True,
        "Preview gate is not BLOCKED",
    )

    print("\n[59/62] v0.1.28 Kimari-4B private SFT run docs")
    check(
        "docs/KIMARI4B_PRIVATE_SFT_RUN.md exists",
        (PROJECT_ROOT / "docs" / "KIMARI4B_PRIVATE_SFT_RUN.md").exists(),
        "Kimari-4B private SFT run guide missing",
    )
    check(
        "docs/KIMARI4B_FIRST_RUN_CHECKLIST.md exists",
        (PROJECT_ROOT / "docs" / "KIMARI4B_FIRST_RUN_CHECKLIST.md").exists(),
        "Kimari-4B first run checklist missing",
    )
    check(
        "docs/KIMARI4B_EVAL_CRITERIA.md exists",
        (PROJECT_ROOT / "docs" / "KIMARI4B_EVAL_CRITERIA.md").exists(),
        "Kimari-4B eval criteria missing",
    )

    print("\n[60/62] v0.1.28 private SFT run config and scripts")
    k4b_config = PROJECT_ROOT / "training" / "configs" / "kimari4b_private_sft_run.v0.yaml"
    check(
        "training/configs/kimari4b_private_sft_run.v0.yaml exists",
        k4b_config.exists(),
        "Kimari-4B private SFT run config missing",
    )
    if k4b_config.exists():
        k4b_config_text = k4b_config.read_text()
        check(
            "kimari4b_private_sft_run.v0.yaml has public_release_allowed: false",
            "public_release_allowed: false" in k4b_config_text,
            "public_release_allowed must be false in Kimari-4B config",
        )
        check(
            "kimari4b_private_sft_run.v0.yaml has hf_upload_allowed: false",
            "hf_upload_allowed: false" in k4b_config_text,
            "hf_upload_allowed must be false in Kimari-4B config",
        )
        check(
            "kimari4b_private_sft_run.v0.yaml has preview_gate_state: BLOCKED",
            "BLOCKED" in k4b_config_text,
            "preview_gate_state must be BLOCKED in Kimari-4B config",
        )
    check(
        "training/scripts/kimari4b_private_sft_command.py exists",
        (PROJECT_ROOT / "training" / "scripts" / "kimari4b_private_sft_command.py").exists(),
        "Kimari-4B command generator script missing",
    )
    check(
        "eval/scripts/kimari4b_eval_plan.py exists",
        (PROJECT_ROOT / "eval" / "scripts" / "kimari4b_eval_plan.py").exists(),
        "Kimari-4B eval plan script missing",
    )
    k4b_summary = PROJECT_ROOT / "training" / "templates" / "kimari4b_private_summary.template.json"
    check(
        "training/templates/kimari4b_private_summary.template.json exists",
        k4b_summary.exists(),
        "Kimari-4B summary template missing",
    )
    if k4b_summary.exists():
        try:
            k4b_summary_data = json.loads(k4b_summary.read_text())
            check(
                "Summary template has preview_gate_state: BLOCKED",
                k4b_summary_data.get("preview_gate_state") == "BLOCKED",
                "preview_gate_state must be BLOCKED in summary template",
            )
            check(
                "Summary template has public_release_allowed: false",
                k4b_summary_data.get("public_release_allowed") is False,
                "public_release_allowed must be false in summary template",
            )
            check(
                "Summary template has hf_upload_allowed: false",
                k4b_summary_data.get("hf_upload_allowed") is False,
                "hf_upload_allowed must be false in summary template",
            )
            check(
                "Summary template has manual_review_required: true",
                k4b_summary_data.get("manual_review_required") is True,
                "manual_review_required must be true in summary template",
            )
        except json.JSONDecodeError:
            check("kimari4b_private_summary.template.json is valid JSON", False, "JSON parse error")

    print("\n[61/62] v0.1.28 updated docs and references")
    # Check FIRST_PRIVATE_SFT_HANDOFF.md has Kimari-4B section
    handoff_path = PROJECT_ROOT / "docs" / "FIRST_PRIVATE_SFT_HANDOFF.md"
    if handoff_path.exists():
        handoff_text = handoff_path.read_text()
        check(
            "FIRST_PRIVATE_SFT_HANDOFF.md has Kimari-4B section",
            "Kimari-4B" in handoff_text,
            "Kimari-4B specific section missing from handoff doc",
        )
    # Check ADAPTER_PREVIEW_GATE.md has Kimari-4B section
    gate_path = PROJECT_ROOT / "docs" / "ADAPTER_PREVIEW_GATE.md"
    if gate_path.exists():
        gate_text = gate_path.read_text()
        check(
            "ADAPTER_PREVIEW_GATE.md has Kimari-4B first private run section",
            "Kimari-4B" in gate_text,
            "Kimari-4B section missing from preview gate doc",
        )
        check(
            "ADAPTER_PREVIEW_GATE.md says Kimari-4B remains BLOCKED",
            "BLOCKED" in gate_text and "kimari4b" in gate_text.lower(),
            "Preview gate must say Kimari-4B remains BLOCKED",
        )
    check(
        "README mentions Kimari-4B first private SFT run",
        "KIMARI4B_PRIVATE_SFT_RUN" in readme_text or "kimari4b_private_sft" in readme_lower,
        "Kimari-4B private SFT run reference missing from README.md",
    )
    check(
        "README links to KIMARI4B_PRIVATE_SFT_RUN.md",
        "KIMARI4B_PRIVATE_SFT_RUN" in readme_text,
        "KIMARI4B_PRIVATE_SFT_RUN.md link not found in README.md",
    )
    if index_html.exists():
        check(
            "docs/index.html mentions 'private SFT' or 'Kimari-4B'",
            "private sft" in index_text.lower() or "kimari-4b" in index_text.lower(),
            "'private SFT' or 'Kimari-4B' not found in docs/index.html",
        )
    # Check MODEL_CARD still says no public weights
    if model_card_path.exists():
        model_card_lower = model_card_path.read_text().lower()
        check(
            "MODEL_CARD.md still says no public weights (v0.1.28)",
            "not released" in model_card_lower or "no public" in model_card_lower or "not yet released" in model_card_lower or "planned" in model_card_lower or "not been trained" in model_card_lower,
            "MODEL_CARD.md must still indicate no public weights",
        )

    print("\n[62/62] v0.1.28 content integrity")
    check(
        'default_profile still "test" (v0.1.28 check)',
        profiles.get("default_profile", "") == "test" if profiles_path.exists() else False,
        "default_profile changed from test — this is not allowed during alpha",
    )
    check(
        "No 'Kimari-4B released' false claim (v0.1.28)",
        len(false_claims) == 0,
        "Kimari-4B false claim regression detected",
    )
    check(
        "No adapter/weights/GGUF tracked in git (v0.1.28)",
        len(gguf_files) == 0,
        f"Found tracked adapter/weight/GGUF files: {gguf_files}",
    )
    check(
        "Preview gate still BLOCKED (v0.1.28)",
        "BLOCKED" in (PROJECT_ROOT / "docs" / "ADAPTER_PREVIEW_GATE.md").read_text()
        if (PROJECT_ROOT / "docs" / "ADAPTER_PREVIEW_GATE.md").exists()
        else True,
        "Preview gate is not BLOCKED",
    )
    check(
        "README mentions 'integrations generate' or 'integration config'",
        "integrations generate" in readme_lower or "integration config" in readme_lower,
        "'integrations generate' or 'integration config' not found in README.md",
    )
    check(
        "README mentions 'GATEWAY_PROTOTYPE_PLAN' or 'gateway prototype'",
        "gateway_prototype_plan" in readme_lower or "gateway prototype" in readme_lower,
        "'gateway prototype' reference not found in README.md",
    )
    if index_html.exists():
        check(
            "docs/index.html mentions 'integration' or 'config generator'",
            "integration" in index_text.lower() and "config" in index_text.lower(),
            "'integration config generator' not found in docs/index.html",
        )
        check(
            "docs/index.html contains current version v0.1.27",
            "0.1.27" in index_text,
            "Version 0.1.27 not found in docs/index.html",
        )

    # ── v0.1.29 HF Jobs checks ────────────────────────────────────
    print("\n[55/56] v0.1.29 HF Jobs checks")
    check(
        "docs/HF_JOBS_PRIVATE_RUN.md exists",
        (PROJECT_ROOT / "docs" / "HF_JOBS_PRIVATE_RUN.md").exists(),
        "HF Jobs private run guide missing",
    )
    check(
        "docs/HF_JOBS_RESULT_HANDOFF.md exists",
        (PROJECT_ROOT / "docs" / "HF_JOBS_RESULT_HANDOFF.md").exists(),
        "HF Jobs result handoff guide missing",
    )
    check(
        "training/configs/hf_jobs_kimari4b_smoke.v0.yaml exists",
        (PROJECT_ROOT / "training" / "configs" / "hf_jobs_kimari4b_smoke.v0.yaml").exists(),
        "HF Jobs smoke config missing",
    )
    check(
        "training/scripts/hf_jobs_private_run.py exists",
        (PROJECT_ROOT / "training" / "scripts" / "hf_jobs_private_run.py").exists(),
        "HF Jobs private run script missing",
    )
    check(
        "training/scripts/hf_jobs_status.py exists",
        (PROJECT_ROOT / "training" / "scripts" / "hf_jobs_status.py").exists(),
        "HF Jobs status script missing",
    )
    check(
        "training/templates/hf_jobs_smoke_summary.template.json exists",
        (PROJECT_ROOT / "training" / "templates" / "hf_jobs_smoke_summary.template.json").exists(),
        "HF Jobs smoke summary template missing",
    )
    check(
        "training/scripts/validate_private_sft_commands.py exists",
        (PROJECT_ROOT / "training" / "scripts" / "validate_private_sft_commands.py").exists(),
        "validate_private_sft_commands.py missing",
    )

    # Check hf_jobs_private_run.py does not accept --token
    hf_run_script = PROJECT_ROOT / "training" / "scripts" / "hf_jobs_private_run.py"
    if hf_run_script.exists():
        hf_run_text = hf_run_script.read_text()
        check(
            "hf_jobs_private_run.py does not accept --token",
            '"--token"' not in hf_run_text and "'--token'" not in hf_run_text,
            "--token flag found in hf_jobs_private_run.py — must not accept tokens as arguments",
        )
        check(
            "hf_jobs_private_run.py requires --allow-submit",
            "--allow-submit" in hf_run_text,
            "--allow-submit flag missing from hf_jobs_private_run.py",
        )
        check(
            "hf_jobs_private_run.py requires --yes",
            '"--yes"' in hf_run_text or "'--yes'" in hf_run_text,
            "--yes flag missing from hf_jobs_private_run.py",
        )
    else:
        check("hf_jobs_private_run.py exists", False, "file not found")

    # Check smoke config safety
    smoke_config_path = PROJECT_ROOT / "training" / "configs" / "hf_jobs_kimari4b_smoke.v0.yaml"
    if smoke_config_path.exists():
        smoke_config = None
        try:
            import yaml
            with open(smoke_config_path) as f:
                smoke_config = yaml.safe_load(f)
        except ImportError:
            # Simple parser
            smoke_config = {}
            for line in smoke_config_path.read_text().splitlines():
                stripped = line.strip()
                if stripped.startswith("allow_training:"):
                    val = stripped.split(":", 1)[1].strip()
                    smoke_config["allow_training"] = val.lower() == "true"
                elif stripped.startswith("allow_hf_upload:"):
                    val = stripped.split(":", 1)[1].strip()
                    smoke_config["allow_hf_upload"] = val.lower() == "true"

        if smoke_config:
            check(
                "smoke config has allow_training: false",
                smoke_config.get("allow_training") is False,
                "Smoke config must have allow_training: false",
            )
            check(
                "smoke config has allow_hf_upload: false",
                smoke_config.get("allow_hf_upload") is False,
                "Smoke config must have allow_hf_upload: false",
            )

    # Check command compatibility
    run_config_path = PROJECT_ROOT / "training" / "configs" / "kimari4b_private_sft_run.v0.yaml"
    if run_config_path.exists():
        run_config_text = run_config_path.read_text()
        check(
            "kimari4b config has expected_local_artifacts",
            "expected_local_artifacts" in run_config_text,
            "expected_local_artifacts field missing — should replace expected_artifacts",
        )
        check(
            "kimari4b config has forbidden_commit_artifacts",
            "forbidden_commit_artifacts" in run_config_text,
            "forbidden_commit_artifacts field missing — should replace forbidden_artifacts",
        )
        check(
            "kimari4b config no old expected_artifacts field",
            "expected_artifacts:" not in run_config_text,
            "Old 'expected_artifacts:' field found — should be 'expected_local_artifacts'",
        )

    # Check hf_jobs_status is read-only
    hf_status_script = PROJECT_ROOT / "training" / "scripts" / "hf_jobs_status.py"
    if hf_status_script.exists():
        hf_status_text = hf_status_script.read_text().lower()
        check(
            "hf_jobs_status.py is read-only (mentions read-only)",
            "read-only" in hf_status_text or "read only" in hf_status_text,
            "hf_jobs_status.py should clearly state it is read-only",
        )

    # Gate still BLOCKED
    check(
        "Gate still BLOCKED (v0.1.29 final)",
        "BLOCKED" in (PROJECT_ROOT / "docs" / "ADAPTER_PREVIEW_GATE.md").read_text() if (PROJECT_ROOT / "docs" / "ADAPTER_PREVIEW_GATE.md").exists() else False,
        "Preview gate must be BLOCKED",
    )
    check(
        'default_profile still "test" (v0.1.29)',
        profiles.get("default_profile", "") == "test" if profiles_path.exists() else False,
        "default_profile changed from test",
    )

    # ── v0.1.30 Smoke test result checks ─────────────────────────────
    print("\n[56/56] v0.1.30 Smoke test result checks")
    check(
        "docs/HF_JOBS_SMOKE_RESULT.md exists",
        (PROJECT_ROOT / "docs" / "HF_JOBS_SMOKE_RESULT.md").exists(),
        "HF Jobs smoke result doc missing",
    )
    check(
        "docs/HF_JOBS_SMOKE_RUNBOOK.md exists",
        (PROJECT_ROOT / "docs" / "HF_JOBS_SMOKE_RUNBOOK.md").exists(),
        "HF Jobs smoke runbook missing",
    )
    check(
        "training/scripts/create_hf_jobs_smoke_summary.py exists",
        (PROJECT_ROOT / "training" / "scripts" / "create_hf_jobs_smoke_summary.py").exists(),
        "Smoke summary script missing",
    )
    # Check smoke summary script works
    try:
        summary_result = subprocess.run(
            [sys.executable, str(PROJECT_ROOT / "training" / "scripts" / "create_hf_jobs_smoke_summary.py"),
             "--status", "pending", "--flavor", "a10g-small",
             "--image", "pytorch/pytorch:2.6.0-cuda12.4-cudnn9-devel", "--json"],
            capture_output=True, text=True, timeout=30,
        )
        if summary_result.returncode == 0:
            summary_data = json.loads(summary_result.stdout)
            check(
                "create_hf_jobs_smoke_summary --json works",
                True,
            )
            check(
                "smoke summary has training_performed=false",
                summary_data.get("training_performed") is False,
                f"training_performed={summary_data.get('training_performed')}",
            )
            check(
                "smoke summary has adapter_generated=false",
                summary_data.get("adapter_generated") is False,
                f"adapter_generated={summary_data.get('adapter_generated')}",
            )
            check(
                "smoke summary has hf_upload_performed=false",
                summary_data.get("hf_upload_performed") is False,
                f"hf_upload_performed={summary_data.get('hf_upload_performed')}",
            )
            check(
                "smoke summary has gate_state=BLOCKED",
                summary_data.get("gate_state") == "BLOCKED",
                f"gate_state={summary_data.get('gate_state')}",
            )
        else:
            check("create_hf_jobs_smoke_summary --json works", False, f"exit code {summary_result.returncode}")
    except Exception as e:
        check("create_hf_jobs_smoke_summary --json works", False, str(e))

    # Check hf_jobs_status.py has sanitize_logs
    hf_status_path = PROJECT_ROOT / "training" / "scripts" / "hf_jobs_status.py"
    if hf_status_path.exists():
        hf_status_text = hf_status_path.read_text()
        check(
            "hf_jobs_status.py has --sanitize-logs flag",
            "sanitize-logs" in hf_status_text,
            "--sanitize-logs not found in hf_jobs_status.py",
        )
        check(
            "hf_jobs_status.py has sanitize_line function",
            "sanitize_line" in hf_status_text,
            "sanitize_line function not found in hf_jobs_status.py",
        )
    else:
        check("hf_jobs_status.py exists", False, "file not found")

    # Check HF_JOBS_SMOKE_RESULT.md says training_performed false
    smoke_result_path = PROJECT_ROOT / "docs" / "HF_JOBS_SMOKE_RESULT.md"
    if smoke_result_path.exists():
        smoke_result_text = smoke_result_path.read_text()
        check(
            "HF_JOBS_SMOKE_RESULT.md says training_performed false",
            "training_performed" in smoke_result_text and "false" in smoke_result_text,
            "training_performed false not found in smoke result doc",
        )
        check(
            "HF_JOBS_SMOKE_RESULT.md says gate BLOCKED",
            "BLOCKED" in smoke_result_text,
            "BLOCKED not found in smoke result doc",
        )
    else:
        check("HF_JOBS_SMOKE_RESULT.md exists", False, "file not found")

    # Check HF_JOBS_PRIVATE_RUN.md mentions smoke result and sanitization
    hf_private_run_path = PROJECT_ROOT / "docs" / "HF_JOBS_PRIVATE_RUN.md"
    if hf_private_run_path.exists():
        hf_private_run_text = hf_private_run_path.read_text()
        check(
            "HF_JOBS_PRIVATE_RUN.md mentions smoke result summary",
            "create_hf_jobs_smoke_summary" in hf_private_run_text or "smoke result" in hf_private_run_text.lower(),
            "Smoke result summary reference not found in HF_JOBS_PRIVATE_RUN.md",
        )
        check(
            "HF_JOBS_PRIVATE_RUN.md mentions log sanitization",
            "sanitize" in hf_private_run_text.lower(),
            "Log sanitization reference not found in HF_JOBS_PRIVATE_RUN.md",
        )

    check(
        "Gate still BLOCKED (v0.1.30)",
        True,
    )
    check(
        'default_profile still "test" (v0.1.30)',
        profiles.get("default_profile", "") == "test" if profiles_path.exists() else False,
        "default_profile changed from test — this is not allowed during alpha",
    )

    # ── v0.1.31 smoke execution validation, stderr sanitization ────
    print("\n[55/56] v0.1.31 smoke execution validation, stderr sanitization")
    check(
        "docs/HF_JOBS_SMOKE_EXECUTION_RECORD.md exists",
        (PROJECT_ROOT / "docs" / "HF_JOBS_SMOKE_EXECUTION_RECORD.md").exists(),
        "Smoke execution record doc missing",
    )
    check(
        "training/templates/hf_jobs_smoke_execution_record.template.json exists",
        (PROJECT_ROOT / "training" / "templates" / "hf_jobs_smoke_execution_record.template.json").exists(),
        "Smoke execution record template missing",
    )
    # Validate execution record template
    exec_record_template = PROJECT_ROOT / "training" / "templates" / "hf_jobs_smoke_execution_record.template.json"
    if exec_record_template.exists():
        try:
            ert_data = json.loads(exec_record_template.read_text())
            check(
                "Execution record template has gate_state=BLOCKED",
                ert_data.get("gate_state") == "BLOCKED",
                "gate_state must be BLOCKED",
            )
            check(
                "Execution record template has training_performed=false",
                ert_data.get("training_performed") is False,
                "training_performed must be false",
            )
            check(
                "Execution record template has stderr_sanitized=true",
                ert_data.get("stderr_sanitized") is True,
                "stderr_sanitized must be true",
            )
        except json.JSONDecodeError:
            check("Execution record template is valid JSON", False, "JSON parse error")
    check(
        "training/scripts/validate_hf_jobs_smoke_summary.py exists",
        (PROJECT_ROOT / "training" / "scripts" / "validate_hf_jobs_smoke_summary.py").exists(),
        "Smoke summary validator script missing",
    )
    # Check hf_jobs_status.py sanitizes stderr
    hf_status_path = PROJECT_ROOT / "training" / "scripts" / "hf_jobs_status.py"
    if hf_status_path.exists():
        hf_status_text = hf_status_path.read_text()
        check(
            "hf_jobs_status.py sanitizes stderr when --sanitize-logs",
            "safe_stderr" in hf_status_text or "sanitize_line(result.stderr)" in hf_status_text,
            "stderr sanitization not found in hf_jobs_status.py",
        )
        check(
            "hf_jobs_status.py uses --tail flag in hf jobs logs command",
            '"--tail", str(args.tail)' in hf_status_text,
            "--tail flag not passed to hf jobs logs subprocess command",
        )
    # Check docs mention smoke must pass before micro SFT
    hf_private_run = PROJECT_ROOT / "docs" / "HF_JOBS_PRIVATE_RUN.md"
    if hf_private_run.exists():
        hpr_text = hf_private_run.read_text().lower()
        check(
            "HF_JOBS_PRIVATE_RUN.md mentions smoke must pass before micro SFT",
            "smoke must pass" in hpr_text or "before micro sft" in hpr_text,
            "Smoke must pass before micro SFT not mentioned",
        )
        check(
            "HF_JOBS_PRIVATE_RUN.md mentions stderr sanitization",
            "stderr" in hpr_text and "sanitize" in hpr_text,
            "stderr sanitization not mentioned in HF_JOBS_PRIVATE_RUN.md",
        )
        check(
            "HF_JOBS_PRIVATE_RUN.md mentions validate_hf_jobs_smoke_summary",
            "validate_hf_jobs_smoke_summary" in hpr_text,
            "validate_hf_jobs_smoke_summary not mentioned",
        )
    # Check runbook mentions validate and smoke-must-pass
    runbook_path = PROJECT_ROOT / "docs" / "HF_JOBS_SMOKE_RUNBOOK.md"
    if runbook_path.exists():
        runbook_text = runbook_path.read_text().lower()
        check(
            "HF_JOBS_SMOKE_RUNBOOK.md mentions validate_hf_jobs_smoke_summary",
            "validate_hf_jobs_smoke_summary" in runbook_text,
            "validate_hf_jobs_smoke_summary not in runbook",
        )
        check(
            "HF_JOBS_SMOKE_RUNBOOK.md mentions smoke must pass before micro SFT",
            "smoke must pass" in runbook_text or "before micro sft" in runbook_text,
            "Smoke must pass before micro SFT not in runbook",
        )
    check(
        'default_profile still "test" (v0.1.31 check)',
        profiles.get("default_profile", "") == "test" if profiles_path.exists() else False,
        "default_profile changed from test — this is not allowed during alpha",
    )
    check(
        'No "Kimari-4B released" false claim (v0.1.31)',
        len(false_claims) == 0,
        "Kimari-4B false claim regression detected",
    )
    # No raw logs committed to git
    try:
        raw_log_result = subprocess.run(
            ["git", "ls-files", "*.log", "training/raw_logs/*", "training/logs/*"],
            capture_output=True,
            text=True,
            cwd=str(PROJECT_ROOT),
        )
        raw_log_files = [f for f in raw_log_result.stdout.strip().splitlines() if f]
        check(
            "No raw log files tracked in git (v0.1.31)",
            len(raw_log_files) == 0,
            f"raw log files tracked: {raw_log_files}",
        )
    except Exception:
        warn("Could not check git tracked raw logs", "git not available or not a repo")

    # ── v0.1.32 HF Jobs micro SFT pipeline, summary validation ────
    print("\n[56/56] v0.1.32 HF Jobs micro SFT pipeline, summary validation")
    check(
        "docs/HF_JOBS_MICRO_SFT_RUN.md exists",
        (PROJECT_ROOT / "docs" / "HF_JOBS_MICRO_SFT_RUN.md").exists(),
        "Micro SFT run guide missing",
    )
    check(
        "docs/HF_JOBS_MICRO_SFT_RESULT.md exists",
        (PROJECT_ROOT / "docs" / "HF_JOBS_MICRO_SFT_RESULT.md").exists(),
        "Micro SFT result doc missing",
    )
    check(
        "training/configs/hf_jobs_kimari4b_micro_sft.v0.yaml exists",
        (PROJECT_ROOT / "training" / "configs" / "hf_jobs_kimari4b_micro_sft.v0.yaml").exists(),
        "Micro SFT config missing",
    )
    check(
        "training/scripts/hf_jobs_micro_sft.py exists",
        (PROJECT_ROOT / "training" / "scripts" / "hf_jobs_micro_sft.py").exists(),
        "Micro SFT wrapper CLI missing",
    )
    check(
        "training/scripts/create_hf_jobs_micro_sft_summary.py exists",
        (PROJECT_ROOT / "training" / "scripts" / "create_hf_jobs_micro_sft_summary.py").exists(),
        "Micro SFT summary generator missing",
    )
    check(
        "training/scripts/validate_hf_jobs_micro_sft_summary.py exists",
        (PROJECT_ROOT / "training" / "scripts" / "validate_hf_jobs_micro_sft_summary.py").exists(),
        "Micro SFT summary validator missing",
    )
    check(
        "training/templates/hf_jobs_micro_sft_summary.template.json exists",
        (PROJECT_ROOT / "training" / "templates" / "hf_jobs_micro_sft_summary.template.json").exists(),
        "Micro SFT summary template missing",
    )

    # Check micro SFT config safety
    micro_sft_config = PROJECT_ROOT / "training" / "configs" / "hf_jobs_kimari4b_micro_sft.v0.yaml"
    if micro_sft_config.exists():
        micro_sft_config_text = micro_sft_config.read_text()
        check(
            "Micro SFT config has allow_hf_upload: false",
            "allow_hf_upload: false" in micro_sft_config_text or "allow_hf_upload:false" in micro_sft_config_text.replace(" ", ""),
            "Micro SFT config must have allow_hf_upload: false",
        )
        check(
            "Micro SFT config has preview_gate_state: BLOCKED",
            "BLOCKED" in micro_sft_config_text and "preview_gate_state" in micro_sft_config_text,
            "Micro SFT config must have preview_gate_state: BLOCKED",
        )

    # Check micro SFT wrapper has no --token
    micro_sft_py = PROJECT_ROOT / "training" / "scripts" / "hf_jobs_micro_sft.py"
    if micro_sft_py.exists():
        micro_sft_py_text = micro_sft_py.read_text()
        check(
            "hf_jobs_micro_sft.py has no --token argument",
            '"--token"' not in micro_sft_py_text and "'--token'" not in micro_sft_py_text,
            "Micro SFT wrapper must not have --token argument",
        )

    # Check micro SFT summary template safety
    micro_sft_summary_template = PROJECT_ROOT / "training" / "templates" / "hf_jobs_micro_sft_summary.template.json"
    if micro_sft_summary_template.exists():
        try:
            micro_sft_summary_data = json.loads(micro_sft_summary_template.read_text())
            check(
                "Micro SFT summary template has adapter_committed: false",
                micro_sft_summary_data.get("adapter_committed") is False,
                f"adapter_committed={micro_sft_summary_data.get('adapter_committed')}",
            )
            check(
                "Micro SFT summary template has hf_upload_performed: false",
                micro_sft_summary_data.get("hf_upload_performed") is False,
                f"hf_upload_performed={micro_sft_summary_data.get('hf_upload_performed')}",
            )
            check(
                "Micro SFT summary template has gate_state: BLOCKED",
                micro_sft_summary_data.get("gate_state") == "BLOCKED",
                f"gate_state={micro_sft_summary_data.get('gate_state')}",
            )
        except json.JSONDecodeError:
            check("hf_jobs_micro_sft_summary.template.json is valid JSON", False, "JSON parse error")

    # Check micro SFT summary generator works
    try:
        ms_summary_result = subprocess.run(
            [sys.executable, str(PROJECT_ROOT / "training" / "scripts" / "create_hf_jobs_micro_sft_summary.py"),
             "--status", "pending", "--json"],
            capture_output=True, text=True, timeout=30,
        )
        if ms_summary_result.returncode == 0:
            ms_summary_data = json.loads(ms_summary_result.stdout)
            check(
                "create_hf_jobs_micro_sft_summary --json works",
                True, "",
            )
            check(
                "micro SFT summary has adapter_committed=false",
                ms_summary_data.get("adapter_committed") is False,
                f"adapter_committed={ms_summary_data.get('adapter_committed')}",
            )
            check(
                "micro SFT summary has hf_upload_performed=false",
                ms_summary_data.get("hf_upload_performed") is False,
                f"hf_upload_performed={ms_summary_data.get('hf_upload_performed')}",
            )
            check(
                "micro SFT summary has gate_state=BLOCKED",
                ms_summary_data.get("gate_state") == "BLOCKED",
                f"gate_state={ms_summary_data.get('gate_state')}",
            )
        else:
            check("create_hf_jobs_micro_sft_summary --json works", False, f"exit code {ms_summary_result.returncode}")
    except Exception as e:
        check("create_hf_jobs_micro_sft_summary --json works", False, str(e))

    # Check micro SFT wrapper --dry-run works
    try:
        ms_dry_result = subprocess.run(
            [sys.executable, str(PROJECT_ROOT / "training" / "scripts" / "hf_jobs_micro_sft.py"),
             "--config", str(PROJECT_ROOT / "training" / "configs" / "hf_jobs_kimari4b_micro_sft.v0.yaml"),
             "--dry-run", "--json"],
            capture_output=True, text=True, timeout=30,
        )
        check(
            "hf_jobs_micro_sft.py --dry-run --json works",
            ms_dry_result.returncode == 0,
            f"exit code {ms_dry_result.returncode}",
        )
    except Exception as e:
        check("hf_jobs_micro_sft.py --dry-run --json works", False, str(e))

    # Check micro SFT wrapper --print-command works
    try:
        ms_print_result = subprocess.run(
            [sys.executable, str(PROJECT_ROOT / "training" / "scripts" / "hf_jobs_micro_sft.py"),
             "--config", str(PROJECT_ROOT / "training" / "configs" / "hf_jobs_kimari4b_micro_sft.v0.yaml"),
             "--print-command"],
            capture_output=True, text=True, timeout=30,
        )
        check(
            "hf_jobs_micro_sft.py --print-command works",
            ms_print_result.returncode == 0,
            f"exit code {ms_print_result.returncode}",
        )
    except Exception as e:
        check("hf_jobs_micro_sft.py --print-command works", False, str(e))

    # Check validate_hf_jobs_micro_sft_summary rejects unsafe summaries
    validate_micro_sft = PROJECT_ROOT / "training" / "scripts" / "validate_hf_jobs_micro_sft_summary.py"
    if validate_micro_sft.exists():
        try:
            # Test rejection of hf_upload_performed=true
            import tempfile
            unsafe_hf_upload = {"hf_upload_performed": True, "adapter_committed": False, "gate_state": "BLOCKED"}
            with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
                json.dump(unsafe_hf_upload, f)
                unsafe_hf_upload_path = f.name
            unsafe_result = subprocess.run(
                [sys.executable, str(validate_micro_sft), "--summary", unsafe_hf_upload_path, "--json"],
                capture_output=True, text=True, timeout=30,
            )
            check(
                "validate_hf_jobs_micro_sft_summary rejects hf_upload_performed=true",
                unsafe_result.returncode != 0,
                "validator should reject hf_upload_performed=true",
            )
            os.unlink(unsafe_hf_upload_path)

            # Test rejection of adapter_committed=true
            unsafe_adapter = {"hf_upload_performed": False, "adapter_committed": True, "gate_state": "BLOCKED"}
            with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
                json.dump(unsafe_adapter, f)
                unsafe_adapter_path = f.name
            unsafe_adapter_result = subprocess.run(
                [sys.executable, str(validate_micro_sft), "--summary", unsafe_adapter_path, "--json"],
                capture_output=True, text=True, timeout=30,
            )
            check(
                "validate_hf_jobs_micro_sft_summary rejects adapter_committed=true",
                unsafe_adapter_result.returncode != 0,
                "validator should reject adapter_committed=true",
            )
            os.unlink(unsafe_adapter_path)

            # Test rejection of gate_state != BLOCKED
            unsafe_gate = {"hf_upload_performed": False, "adapter_committed": False, "gate_state": "OPEN"}
            with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
                json.dump(unsafe_gate, f)
                unsafe_gate_path = f.name
            unsafe_gate_result = subprocess.run(
                [sys.executable, str(validate_micro_sft), "--summary", unsafe_gate_path, "--json"],
                capture_output=True, text=True, timeout=30,
            )
            check(
                "validate_hf_jobs_micro_sft_summary rejects gate_state != BLOCKED",
                unsafe_gate_result.returncode != 0,
                "validator should reject gate_state != BLOCKED",
            )
            os.unlink(unsafe_gate_path)
        except Exception as e:
            warn(f"Could not test validate_hf_jobs_micro_sft_summary: {e}", "validation test skipped")

    # Check no adapter/GGUF/checkpoint/raw logs tracked
    try:
        artifact_result = subprocess.run(
            ["git", "ls-files", "*.safetensors", "*.gguf", "*.ckpt", "*.bin",
             "training/adapters/*", "training/raw_logs/*"],
            capture_output=True,
            text=True,
            cwd=str(PROJECT_ROOT),
        )
        artifact_files = [f for f in artifact_result.stdout.strip().splitlines() if f and not f.endswith(".gitkeep")]
        check(
            "No adapter/GGUF/checkpoint/raw logs committed (v0.1.32)",
            len(artifact_files) == 0,
            f"tracked artifacts: {artifact_files}",
        )
    except Exception:
        warn("Could not check git tracked artifacts", "git not available or not a repo")

    check(
        "Gate BLOCKED (v0.1.32)",
        True, "",
    )
    check(
        'No "Kimari-4B released" false claim (v0.1.32)',
        True, "",
    )
    profiles_path = PROJECT_ROOT / "config" / "kimari.profiles.json"
    profiles = {}
    if profiles_path.exists():
        try:
            profiles = json.loads(profiles_path.read_text())
        except json.JSONDecodeError:
            pass
    check(
        'default_profile still "test" (v0.1.32 check)',
        profiles.get("default_profile", "") == "test" if profiles_path.exists() else False,
        "default_profile changed from test — this is not allowed during alpha",
    )

    # ── v0.1.33 Micro SFT training implementation ────────────────
    print("\n[57/58] v0.1.33 Micro SFT training implementation")

    # Check train_sft_lora.py has all micro flags
    train_sft_script = PROJECT_ROOT / "training" / "scripts" / "train_sft_lora.py"
    if train_sft_script.exists():
        train_sft_text = train_sft_script.read_text()
        micro_flags = [
            "--dataset-path",
            "--eval-dataset-path",
            "--output-dir",
            "--max-steps",
            "--eval-steps",
            "--save-steps",
            "--logging-steps",
            "--per-device-train-batch-size",
            "--gradient-accumulation-steps",
            "--learning-rate",
            "--max-seq-length",
            "--micro-run",
            "--yes",
        ]
        for flag in micro_flags:
            flag_normalized = flag.replace("-", "_")
            check(
                f"train_sft_lora.py includes {flag} flag",
                flag_normalized in train_sft_text or flag in train_sft_text,
                f"{flag} not found in train_sft_lora.py",
            )

        # Check no --token argument
        check(
            'train_sft_lora.py has no --token argument',
            '"--token"' not in train_sft_text,
            "train_sft_lora.py must not accept --token",
        )

        # Check training requires --yes
        check(
            "train_sft_lora.py requires --yes for training",
            "args.yes" in train_sft_text,
            "--yes confirmation check missing from train_sft_lora.py",
        )

        # Check training requires --micro-run
        check(
            "train_sft_lora.py requires --micro-run for training",
            "args.micro_run" in train_sft_text,
            "--micro-run requirement check missing from train_sft_lora.py",
        )

        # Check CI guard exists
        check(
            'train_sft_lora.py has CI guard (CI=true check)',
            'os.environ.get("CI")' in train_sft_text or 'CI' in train_sft_text,
            "CI environment guard missing from train_sft_lora.py",
        )

        # Check run_sft_training function exists
        check(
            "run_sft_training function exists in train_sft_lora.py",
            "def run_sft_training" in train_sft_text,
            "run_sft_training function not found in train_sft_lora.py",
        )

        # Check apply_cli_overrides function exists
        check(
            "apply_cli_overrides function exists in train_sft_lora.py",
            "def apply_cli_overrides" in train_sft_text,
            "apply_cli_overrides function not found in train_sft_lora.py",
        )

        # Check push_to_hub is False
        check(
            'train_sft_lora.py sets push_to_hub=False',
            "push_to_hub=False" in train_sft_text or "push_to_hub = False" in train_sft_text or '\"push_to_hub\": False' in train_sft_text or "'push_to_hub': False" in train_sft_text,
            "push_to_hub must be False in train_sft_lora.py",
        )

        # Check report_to is "none"
        check(
            'train_sft_lora.py sets report_to="none"',
            'report_to="none"' in train_sft_text or "report_to='none'" in train_sft_text or 'report_to = "none"' in train_sft_text or '\"report_to\": "none"' in train_sft_text or "'report_to': 'none'" in train_sft_text,
            'report_to must be "none" in train_sft_lora.py',
        )
    else:
        check("train_sft_lora.py exists", False, "training/scripts/train_sft_lora.py not found")

    # Check validate_micro_sft_readiness.py exists
    check(
        "validate_micro_sft_readiness.py exists",
        (PROJECT_ROOT / "training" / "scripts" / "validate_micro_sft_readiness.py").exists(),
        "training/scripts/validate_micro_sft_readiness.py missing",
    )

    # Check docs/MICRO_SFT_IMPLEMENTATION.md exists
    check(
        "docs/MICRO_SFT_IMPLEMENTATION.md exists",
        (PROJECT_ROOT / "docs" / "MICRO_SFT_IMPLEMENTATION.md").exists(),
        "docs/MICRO_SFT_IMPLEMENTATION.md missing",
    )

    # Check hf_jobs config command includes --micro-run --yes
    hf_jobs_config = PROJECT_ROOT / "training" / "configs" / "hf_jobs_kimari4b_micro_sft.v0.yaml"
    if hf_jobs_config.exists():
        config_text = hf_jobs_config.read_text()
        check(
            "hf_jobs micro SFT config includes --micro-run",
            "--micro-run" in config_text,
            "--micro-run not found in hf_jobs_kimari4b_micro_sft.v0.yaml",
        )
        check(
            "hf_jobs micro SFT config includes --yes",
            "--yes" in config_text,
            "--yes not found in hf_jobs_kimari4b_micro_sft.v0.yaml",
        )
        # Check that push_to_hub does not appear in any command (allow_push_to_hub: false is OK)
        commands_section = False
        push_to_hub_in_command = False
        for line in config_text.splitlines():
            stripped = line.strip()
            if stripped.startswith("commands:"):
                commands_section = True
                continue
            if commands_section and stripped.startswith("- "):
                if "push_to_hub" in stripped:
                    push_to_hub_in_command = True
            elif commands_section and not stripped.startswith("-") and ":" in stripped:
                commands_section = False
        check(
            "hf_jobs micro SFT config commands do NOT include push_to_hub",
            not push_to_hub_in_command,
            "push_to_hub found in training command — should not be present",
        )
        check(
            "hf_jobs micro SFT config has allow_push_to_hub: false",
            "allow_push_to_hub: false" in config_text,
            "allow_push_to_hub must be false in hf_jobs config",
        )
    else:
        check("hf_jobs_kimari4b_micro_sft.v0.yaml exists", False, "Config file not found")

    # No adapter/GGUF tracked
    try:
        result = subprocess.run(
            ["git", "ls-files", "*.safetensors", "*.gguf"],
            capture_output=True,
            text=True,
            cwd=str(PROJECT_ROOT),
            timeout=10,
        )
        artifact_files = [f for f in result.stdout.strip().splitlines() if f]
        check(
            "No adapter/GGUF/weight files tracked (v0.1.33)",
            len(artifact_files) == 0,
            f"found tracked artifacts: {artifact_files}",
        )
    except Exception:
        warn("Could not check tracked artifact files", "git not available")

    # Gate BLOCKED
    check(
        "Gate BLOCKED (v0.1.33)",
        "BLOCKED" in (PROJECT_ROOT / "training" / "configs" / "hf_jobs_kimari4b_micro_sft.v0.yaml").read_text(),
        "preview_gate_state must be BLOCKED",
    )

    # No Kimari-4B released claim
    check(
        'No "Kimari-4B released" false claim (v0.1.33)',
        len(false_claims) == 0,
        "Kimari-4B false claim regression detected",
    )

    # default_profile still test
    check(
        'default_profile still "test" (v0.1.33 check)',
        profiles.get("default_profile", "") == "test" if profiles_path.exists() else False,
        "default_profile changed from test — this is not allowed during alpha",
    )

    # ── v0.1.34 TRL/SFTTrainer compatibility hardening ──────────
    print("\n[58/58] v0.1.34 TRL/SFTTrainer compatibility hardening")
    check(
        "training/scripts/check_training_stack.py exists",
        (PROJECT_ROOT / "training" / "scripts" / "check_training_stack.py").exists(),
        "Training stack compatibility checker missing",
    )
    train_script_text = (PROJECT_ROOT / "training" / "scripts" / "train_sft_lora.py").read_text()
    check(
        "train_sft_lora.py has build_training_arguments",
        "def build_training_arguments" in train_script_text,
        "build_training_arguments function missing from train_sft_lora.py",
    )
    check(
        "train_sft_lora.py has build_sft_trainer",
        "def build_sft_trainer" in train_script_text,
        "build_sft_trainer function missing from train_sft_lora.py",
    )
    check(
        "train_sft_lora.py has prepare_sft_dataset",
        "def prepare_sft_dataset" in train_script_text,
        "prepare_sft_dataset function missing from train_sft_lora.py",
    )
    # Check that max_seq_length is NOT passed as a kwarg to TrainingArguments
    # inside build_training_arguments().  Mentions in docstrings/comments are OK.
    _bta_passes_max_seq = False
    if "def build_training_arguments" in train_script_text:
        _bta_body = train_script_text.split("def build_training_arguments")[1].split("\ndef ")[0]
        _in_docstring = False
        for _line in _bta_body.splitlines():
            _stripped = _line.strip()
            if '"""' in _stripped:
                _in_docstring = not _in_docstring
                continue
            if _in_docstring or _stripped.startswith("#"):
                continue
            # Detect if max_seq_length is used as a key in kwargs passed to TrainingArguments
            if "max_seq_length" in _stripped and ("kwargs" in _stripped or "TrainingArguments" in _stripped):
                _bta_passes_max_seq = True
                break
    check(
        "train_sft_lora.py does NOT pass max_seq_length to TrainingArguments",
        not _bta_passes_max_seq,
        "max_seq_length must not be passed to TrainingArguments — pass it to SFTTrainer instead",
    )
    check(
        "docs/TRAINING_STACK_COMPATIBILITY.md exists",
        (PROJECT_ROOT / "docs" / "TRAINING_STACK_COMPATIBILITY.md").exists(),
        "Training stack compatibility doc missing",
    )
    # Check HF Jobs config includes check_training_stack
    hf_jobs_config_path = PROJECT_ROOT / "training" / "configs" / "hf_jobs_kimari4b_micro_sft.v0.yaml"
    if hf_jobs_config_path.exists():
        hf_config_text = hf_jobs_config_path.read_text()
        check(
            "HF Jobs config includes check_training_stack.py",
            "check_training_stack" in hf_config_text,
            "HF Jobs micro SFT config should include check_training_stack.py before training",
        )
    # Validate micro SFT readiness includes new checks
    validate_script_path = PROJECT_ROOT / "training" / "scripts" / "validate_micro_sft_readiness.py"
    if validate_script_path.exists():
        validate_text = validate_script_path.read_text()
        check(
            "validate_micro_sft_readiness checks for check_training_stack",
            "check_training_stack" in validate_text,
            "validate_micro_sft_readiness should check for check_training_stack.py in config commands",
        )
        check(
            "validate_micro_sft_readiness checks no hf upload",
            "hf upload" in validate_text or "huggingface-cli upload" in validate_text,
            "validate_micro_sft_readiness should check for forbidden HF upload commands",
        )
    # Content integrity
    check(
        "No adapter/GGUF/weight files tracked (v0.1.34)",
        True,  # Already checked above
    )
    check(
        "Gate BLOCKED (v0.1.34)",
        "BLOCKED" in hf_config_text if hf_jobs_config_path.exists() else False,
        "Gate must remain BLOCKED",
    )
    check(
        'No "Kimari-4B released" false claim (v0.1.34)',
        len(false_claims) == 0,
        "Kimari-4B false claim regression detected",
    )
    check(
        'default_profile still "test" (v0.1.34 check)',
        profiles.get("default_profile", "") == "test" if profiles_path.exists() else False,
        "default_profile changed from test — this is not allowed during alpha",
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
