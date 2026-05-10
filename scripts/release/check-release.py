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
    print("\n[1/43] Version consistency")
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
    print("\n[2/43] README version badge")
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
    print("\n[3/43] CHANGELOG entry")
    changelog = PROJECT_ROOT / "CHANGELOG.md"
    changelog_text = changelog.read_text()
    changelog_header = f"[{init_ver}]"
    check(
        "CHANGELOG.md has entry for current version",
        changelog_header in changelog_text,
        f"'{changelog_header}' not found in CHANGELOG.md",
    )

    # ── ROADMAP entry ────────────────────────────────────────────
    print("\n[4/43] ROADMAP entry")
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
    print("\n[5/43] Config defaults")
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
    print("\n[6/43] Package markers")
    py_typed = PROJECT_ROOT / "kimari" / "py.typed"
    check("kimari/py.typed exists", py_typed.exists(), "PEP 561 marker missing")

    # ── GitHub Pages / SEO ──────────────────────────────────────
    print("\n[7/43] GitHub Pages / SEO")
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
    print("\n[8/43] Documentation files")
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
    print("\n[9/43] No unwanted tracked files")
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
    print("\n[10/43] Content integrity")
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
    print("\n[11/43] Integration documentation")
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
    print("\n[12/43] Performance module")
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
    print("\n[13/43] Runtime & Security modules")
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
    print("\n[14/43] Packaged defaults & user paths")
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
    print("\n[15/43] Short flag support in strict-flags")
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
    print("\n[16/43] Community & contribution files")
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
    print("\n[17/43] Packaging & CI")
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
    print("\n[18/43] Content integrity re-check")
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
    print("\n[19/43] Setup write-mode & SHA256 tooling")
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
    print("\n[20/43] New documentation files")
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
    print("\n[21/43] Content integrity re-check (v0.1.14)")
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
    print("\n[22/43] Model path resolution")
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
    print("\n[23/43] v0.1.15 new files")
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
    print("\n[24/43] v0.1.15 content")
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
    print("\n[25/43] v0.1.16 API experimental")
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
    print("\n[26/43] v0.1.16 Windows packaging improvements")
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
    print("\n[27/43] v0.1.16 release-check improvements")
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
    print("\n[28/43] v0.1.16 content integrity re-check")
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

    # ── [29/43] v0.1.17 MODEL_CARD professional rewrite ──────────
    print("\n[29/43] v0.1.17 MODEL_CARD professional rewrite")
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

    # ── [30/43] v0.1.17 training and base selection docs ──────────
    print("\n[30/43] v0.1.17 training and base selection docs")
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

    # ── [31/43] v0.1.17 dataset and schema files ──────────────────
    print("\n[31/43] v0.1.17 dataset and schema files")
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

    # ── [32/43] v0.1.17 training skeletons ────────────────────────
    print("\n[32/43] v0.1.17 training skeletons")
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

    # ── [33/43] v0.1.17 eval prompts and HF release ───────────────
    print("\n[33/43] v0.1.17 eval prompts and HF release")
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

    # ── [34/43] v0.1.17 content integrity ─────────────────────────
    print("\n[34/43] v0.1.17 content integrity")
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
        pass  # Already checked in [9/43]
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

    # ── [35/43] v0.1.17 MODEL_LICENSES and README updates ────────
    print("\n[35/43] v0.1.17 MODEL_LICENSES and README updates")
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

    # ── [36/43] v0.1.18 base selection and decision record ────────
    print("\n[36/43] v0.1.18 base selection and decision record")
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

    # ── [37/43] v0.1.18 seed datasets, builders, eval harness ────
    print("\n[37/43] v0.1.18 seed datasets, builders, eval harness")
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

    # ── [38/43] v0.1.18 content integrity ─────────────────────────
    print("\n[38/43] v0.1.18 content integrity")
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

    # ── [39/43] v0.1.19 base acceptance ────────────────────────────
    print("\n[39/43] v0.1.19 base acceptance")
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

    # ── [40/43] v0.1.19 dataset v0 ────────────────────────────────
    print("\n[40/43] v0.1.19 dataset v0")
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

    # ── [41/43] v0.1.19 training and eval tools ────────────────────
    print("\n[41/43] v0.1.19 training and eval tools")
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

    # ── [42/43] v0.1.19 documentation ──────────────────────────────
    print("\n[42/43] v0.1.19 documentation")
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

    # ── [43/43] v0.1.19 content integrity ──────────────────────────
    print("\n[43/43] v0.1.19 content integrity")
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
