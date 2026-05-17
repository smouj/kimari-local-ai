#!/usr/bin/env python3
"""Release validation script for Kimari Local AI.

Ensures gate safety, version consistency, and no false claims before any push.
"""

import json
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.parent
ERRORS = []
WARNINGS = []
CHECKS_RUN = 0
CHECKS_PASSED = 0


def check(description: str, condition: bool, detail: str = ""):
    global CHECKS_RUN, CHECKS_PASSED
    CHECKS_RUN += 1
    if condition:
        CHECKS_PASSED += 1
    else:
        ERRORS.append(f"  FAIL: {description}" + (f" ({detail})" if detail else ""))


def warn(msg: str):
    WARNINGS.append(f"  WARN: {msg}")


def get_pyproject_version() -> str:
    try:
        text = (PROJECT_ROOT / "pyproject.toml").read_text()
        for line in text.splitlines():
            if line.strip().startswith("version"):
                return line.split("=")[1].strip().strip('"').strip("'")
    except Exception:
        pass
    return "0.0.0"


def get_init_version() -> str:
    try:
        init_path = PROJECT_ROOT / "kimari" / "__init__.py"
        if init_path.exists():
            text = init_path.read_text()
            for line in text.splitlines():
                if "__version__" in line:
                    return line.split("=")[1].strip().strip('"').strip("'")
    except Exception:
        pass
    return "0.0.0"


# ── [1/5] Safety invariants ──────────────────────────────────────────
print("[1/5] Safety invariants")

# No weights/adapters/GGUF
bad_patterns = [".safetensors", ".gguf", ".bin", ".pt", ".pth", ".ckpt"]
bad_files = []
for pattern in bad_patterns:
    for path in PROJECT_ROOT.rglob(pattern):
        parts = path.parts
        if ".venv" in parts or "deps" in parts or "node_modules" in parts or ".git" in parts:
            continue
        if path.name == "kimari.profiles.schema.json":
            continue
        bad_files.append(str(path.relative_to(PROJECT_ROOT)))

check(
    "No public weights/adapters/GGUF tracked",
    len(bad_files) == 0,
    f"found: {bad_files[:5]}",
)

# Gate BLOCKED in key locations
for location, text_getter in [
    ("README.md", lambda: (PROJECT_ROOT / "README.md").read_text()),
    ("CHANGELOG.md", lambda: (PROJECT_ROOT / "CHANGELOG.md").read_text()),
    ("ROADMAP.md", lambda: (PROJECT_ROOT / "ROADMAP.md").read_text()),
    (
        "dashboard_manager.py",
        lambda: (
            (PROJECT_ROOT / "kimari" / "gateway" / "dashboard_manager.py").read_text()
            if (PROJECT_ROOT / "kimari" / "gateway" / "dashboard_manager.py").exists()
            else ""
        ),
    ),
]:
    try:
        text = text_getter()
        check(
            f"Gate BLOCKED in {location}",
            "BLOCKED" in text,
            f"{location} does not mention BLOCKED",
        )
    except FileNotFoundError:
        warn(f"{location} not found, skipping gate check")

# No false claims — check for positive release claims only
for rel_path in ["README.md", "docs/index.html", "CHANGELOG.md"]:
    fpath = PROJECT_ROOT / rel_path
    if fpath.exists():
        text = fpath.read_text()
        lines = text.split("\n")
        has_false_claim = False
        for line in lines:
            low = line.lower()
            if "kimari-4b" in low and "released" in low:
                # Skip if clearly negated
                negations = [
                    "not released",
                    "not yet released",
                    "no public release",
                    "is not released",
                    "not available",
                    "no weights",
                    "has not been",
                    "false claim",
                    "no.*released",
                    "must not",
                    "should not",
                    "does not claim",
                    "claim detection",
                    "❌",
                    "forbidden",
                    "when kimari",
                    "until kimari",
                    "if kimari",
                    "before kimari",
                    "for when kimari",
                    "after kimari",
                ]
                if not any(n in low for n in negations):
                    has_false_claim = True
                    break
            if "kimari-4b is available" in low and "not" not in low:
                has_false_claim = True
                break
            if "production ready" in low and "not" not in low:
                has_false_claim = True
                break
        check(
            f"{rel_path} does not claim Kimari-4B released",
            not has_false_claim,
            f"possible false claim in {rel_path}",
        )

# default_profile is "test"
profiles_path = PROJECT_ROOT / "config" / "kimari.profiles.json"
if profiles_path.exists():
    profiles = json.loads(profiles_path.read_text())
    check(
        'default_profile is "test"',
        profiles.get("default_profile") == "test",
        f"default_profile is {profiles.get('default_profile')}",
    )

# ── [2/5] Version consistency ──────────────────────────────────────────
print("\n[2/5] Version consistency")

current_version = "0.1.84-alpha"
pyproject_version = get_pyproject_version()
init_version = get_init_version()

check(
    f"pyproject.toml version matches {current_version}",
    pyproject_version == current_version,
    f"got {pyproject_version}",
)
check(
    f"kimari/__init__.py version matches {current_version}",
    init_version == current_version,
    f"got {init_version}",
)

# README badge
readme_path = PROJECT_ROOT / "README.md"
if readme_path.exists():
    readme_text = readme_path.read_text()
    check(
        f"README version badge shows {current_version}",
        f"version-v{current_version.replace('-', '--')}" in readme_text
        or f"version-{current_version.replace('-', '--')}" in readme_text,
        "badge URL mismatch",
    )
    check(
        "README contains Gateway Dashboard section",
        "Gateway Dashboard" in readme_text or "gateway dashboard" in readme_text.lower(),
        "missing Gateway Dashboard section",
    )
    check(
        "README has Quick Start section",
        "Quick Start" in readme_text
        or "quick start" in readme_text.lower()
        or "one-command install" in readme_text.lower(),
        "missing Quick Start section",
    )
    check(
        "README has Safety section",
        "Safety" in readme_text or "safety" in readme_text.lower(),
        "missing Safety section",
    )
    check(
        "README links to CLI_REFERENCE.md",
        "CLI_REFERENCE.md" in readme_text,
        "missing CLI reference link",
    )

# CHANGELOG
changelog_path = PROJECT_ROOT / "CHANGELOG.md"
if changelog_path.exists():
    changelog_text = changelog_path.read_text()
    check(
        f"CHANGELOG has [{current_version}] entry",
        f"[{current_version}]" in changelog_text,
        f"missing [{current_version}] entry",
    )

# ROADMAP
roadmap_path = PROJECT_ROOT / "ROADMAP.md"
if roadmap_path.exists():
    roadmap_text = roadmap_path.read_text()
    check(
        f"ROADMAP mentions {current_version}",
        current_version in roadmap_text,
        f"missing {current_version} in ROADMAP",
    )

# ── [3/5] Current release features ──────────────────────────────────────────
print("\n[3/5] Current release features (v0.1.83)")

# Install scripts
install_sh = PROJECT_ROOT / "install.sh"
install_ps1 = PROJECT_ROOT / "install.ps1"
check("install.sh exists", install_sh.exists(), "missing install.sh")
check("install.ps1 exists", install_ps1.exists(), "missing install.ps1")
if install_sh.exists():
    install_text = install_sh.read_text()
    check("install.sh has strict bash mode", "set -euo pipefail" in install_text, "missing strict mode")
    check("install.sh has --dry-run", "--dry-run" in install_text, "missing --dry-run")
    check("install.sh has WITH_TEST_MODEL gate", "WITH_TEST_MODEL" in install_text, "missing model gate")
    check("install.sh has WITH_DASHBOARD gate", "WITH_DASHBOARD" in install_text, "missing dashboard gate")
if install_ps1.exists():
    ps1_text = install_ps1.read_text()
    check("install.ps1 does not alter execution policy", "Set-ExecutionPolicy" not in ps1_text, "must not alter policy")

# Console
console_cmd = PROJECT_ROOT / "kimari" / "cli" / "console_cmd.py"
check("console_cmd.py exists", console_cmd.exists(), "missing console_cmd.py")
if console_cmd.exists():
    console_text = console_cmd.read_text()
    for token in ["collect_console_status", "MENU_ITEMS", "BLOCKED"]:
        check(f"console_cmd contains {token}", token in console_text, f"missing {token}")

# CLI main
cli_main = PROJECT_ROOT / "kimari" / "cli" / "main.py"
if cli_main.exists():
    cli_text = cli_main.read_text()
    check("CLI registers console command", 'add_parser("console"' in cli_text, "missing console parser")
    check(
        "CLI registers gateway setup",
        "gateway_command" in cli_text or "run_gateway_dashboard" in cli_text,
        "missing gateway",
    )
    check("CLI registers update apply", "run_update_apply" in cli_text, "missing update apply")

# Dashboard manager
dashboard_manager = PROJECT_ROOT / "kimari" / "gateway" / "dashboard_manager.py"
check("dashboard_manager.py exists", dashboard_manager.exists(), "missing dashboard_manager.py")
if dashboard_manager.exists():
    manager_text = dashboard_manager.read_text()
    for token in ["def start(", "def stop(", "def restart(", "def status(", "127.0.0.1", "BLOCKED"]:
        check(f"dashboard_manager contains {token}", token in manager_text, f"missing {token}")
    check("dashboard refuses public bind by default", "allow_public_bind" in manager_text, "missing public bind guard")
    check("dashboard default bind localhost", 'DEFAULT_HOST = "127.0.0.1"' in manager_text, "default bind changed")
    check("gate remains BLOCKED", 'GATE_STATE = "BLOCKED"' in manager_text, "gate changed")

# Dashboard UI
dashboard_overview = PROJECT_ROOT / "apps" / "gateway-dashboard" / "src" / "components" / "dashboard" / "overview.tsx"
if dashboard_overview.exists():
    overview_text = dashboard_overview.read_text()
    check("UI shows Kimari-4B not released", "Kimari-4B not released" in overview_text, "missing not released message")
    check("UI shows Gate BLOCKED", "Gate: BLOCKED" in overview_text, "missing BLOCKED message")
    check("UI shows Local only", "Local only" in overview_text, "missing Local only message")

# Dashboard README
dashboard_readme = PROJECT_ROOT / "apps" / "gateway-dashboard" / "README.md"
if dashboard_readme.exists():
    readme_text = dashboard_readme.read_text()
    check("dashboard README is CLI-first", "kimari gateway setup" in readme_text, "missing CLI setup")

# Landing page (docs/index.html)
index_html = PROJECT_ROOT / "docs" / "index.html"
if index_html.exists():
    docs_index_text = index_html.read_text()
    check(
        "docs/index.html shows current version",
        "v0.1.84-alpha" in docs_index_text,
        "docs/index.html does not show current version",
    )
    check(
        "docs/index.html does not show stale versions",
        "v0.1.28-alpha" not in docs_index_text and "v0.1.56--alpha" not in docs_index_text,
        "docs/index.html shows stale version",
    )

# ── [4/5] Key docs exist ──────────────────────────────────────────
print("\n[4/5] Key documentation")

key_docs = [
    "README.md",
    "CHANGELOG.md",
    "ROADMAP.md",
    "SECURITY.md",
    "PRIVACY.md",
    "LICENSE",
    "docs/KIMARI4B_RELEASE_GATE.md",
    "docs/KIMARI_OPEN_LICENSE_POLICY.md",
    "docs/KIMARI_EVAL_PRIVATE_V1.md",
    "docs/GATEWAY_DASHBOARD.md",
    "docs/INSTALL_ONE_COMMAND.md",
    "docs/KIMARI_CONSOLE.md",
    "docs/SCREENSHOTS.md",
    "docs/CLI_REFERENCE.md",
    "docs/GTX1060_SHOWCASE.md",
    "docs/GTX1060_LOCAL_RUNTIME_RESULT.md",
    "docs/LOCAL_OPENAI_ENDPOINT_TEST.md",
    "docs/OPENWEBUI_LOCAL_SETUP.md",
    "docs/OPENCLAW_LOCAL_SETUP.md",
    "docs/CONTINUE_LOCAL_SETUP.md",
]
for rel in key_docs:
    check(f"{rel} exists", (PROJECT_ROOT / rel).exists(), f"missing {rel}")

# Integration docs
integration_docs = [
    "docs/OPENWEBUI_LOCAL_SETUP.md",
    "docs/OPENCLAW_LOCAL_SETUP.md",
    "docs/CONTINUE_LOCAL_SETUP.md",
]
for rel in integration_docs:
    fpath = PROJECT_ROOT / rel
    if fpath.exists():
        text = fpath.read_text()
        check(f"{rel} has no API key values", "sk-" not in text and 'apiKey = "' not in text, "API key found in doc")

# ── [5/5] Eval & Training safety ──────────────────────────────────────────
print("\n[5/5] Eval & Training safety")

# Eval dataset
eval_dir = PROJECT_ROOT / "eval" / "kimari_private_v1"
if eval_dir.exists():
    jsonl_files = list(eval_dir.glob("*.jsonl"))
    total_items = sum(len(f.read_text().strip().split("\n")) for f in jsonl_files)
    check("Eval dataset has >= 100 items", total_items >= 100, f"only {total_items} items")
    check("Eval dataset has >= 7 categories", len(jsonl_files) >= 7, f"only {len(jsonl_files)} categories")

# Eval config
eval_config = PROJECT_ROOT / "eval" / "configs" / "kimari_eval_v1_baseline_vs_adapter.yaml"
if eval_config.exists():
    config_text = eval_config.read_text().lower()
    check("Eval config gate BLOCKED", "gate_state" in config_text and "blocked" in config_text, "eval config gate")
    check("Eval config blocks public benchmark", "public_benchmark_allowed: false" in config_text, "eval benchmark")
    check("Eval config requires manual review", "manual_review_required: true" in config_text, "eval manual review")

# No raw outputs committed
tracked = subprocess.run(["git", "ls-files"], cwd=PROJECT_ROOT, capture_output=True, text=True, timeout=30)
tracked_files = tracked.stdout.splitlines() if tracked.returncode == 0 else []
raw_outputs = [f for f in tracked_files if "raw_outputs_private.json" in f]
check("No raw_outputs_private.json tracked", not raw_outputs, f"tracked: {raw_outputs}")

# Refusal safety
refusal_jsonl = eval_dir / "refusal_safety.jsonl" if eval_dir.exists() else None
if refusal_jsonl and refusal_jsonl.exists():
    refusal_lines = [line for line in refusal_jsonl.read_text().strip().split("\n") if line.strip()]
    check("Refusal safety has >= 21 items", len(refusal_lines) >= 21, f"only {len(refusal_lines)} items")

# ── Summary ────────────────────────────────────────────────────────────────
print("\n" + "=" * 50)
print(f"Checks: {CHECKS_PASSED}/{CHECKS_RUN} passed")
if WARNINGS:
    print(f"\nWarnings ({len(WARNINGS)}):")
    for w in WARNINGS:
        print(w)
if ERRORS:
    print(f"\nFailures ({len(ERRORS)}):")
    for e in ERRORS:
        print(e)
    sys.exit(1)
else:
    print("\n✅ All checks passed. Release is clean.")
