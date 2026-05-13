"""Release checks for v0.1.55-alpha public HF/GitHub polish."""

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent / "kimari-local-ai"
VERSION = "0.1.59-alpha"
V_VERSION = f"v{VERSION}"


def test_version_bumped_to_v0155():
    assert f'version = "{VERSION}"' in (PROJECT_ROOT / "pyproject.toml").read_text()
    assert f'__version__ = "{VERSION}"' in (PROJECT_ROOT / "kimari" / "__init__.py").read_text()


def test_public_version_consistency_script_passes():
    result = subprocess.run(
        [sys.executable, "scripts/release/check_public_version_consistency.py", "--json"],
        cwd=PROJECT_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    payload = json.loads(result.stdout)
    assert payload["valid"] is True
    assert payload["version"] == "0.1.59-alpha"


def test_public_surfaces_current_and_safe():
    files = [
        "README.md",
        "docs/index.html",
        "docs/HUGGINGFACE_ORG_CARD.md",
        "huggingface/kimari-fit-lab/README.md",
        "docs/HUGGINGFACE_DEPLOYMENT_STATUS.md",
    ]
    combined = "\n".join((PROJECT_ROOT / f).read_text() for f in files)
    for file in files:
        assert V_VERSION in (PROJECT_ROOT / file).read_text(), file
    assert (
        "version-0.1.59--alpha" in (PROJECT_ROOT / "README.md").read_text()
        or "0.1.59" in (PROJECT_ROOT / "README.md").read_text()
    )
    assert "Kimari Local AI v0.1.28-alpha" not in combined
    assert "New in v0.1.28-alpha" not in combined
    assert "v0.1.29-alpha FOCUS" not in combined
    lower = combined.lower()
    assert "kimari-4b is not released" in lower or "kimari-4b is **not released" in lower
    assert "blocked" in lower
    assert "kimari-4b released" not in lower
    assert "public weights available" not in lower
    assert "production ready" not in lower


def test_changelog_has_no_future_dates():
    result = subprocess.run(
        [sys.executable, "scripts/release/check_public_version_consistency.py", "--json"],
        cwd=PROJECT_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    payload = json.loads(result.stdout)
    assert not [e for e in payload["errors"] if "future date" in e]


def test_collection_and_placeholder_docs_are_safe():
    collection = (PROJECT_ROOT / "docs" / "HUGGINGFACE_COLLECTIONS.md").read_text().lower()
    placeholder = (PROJECT_ROOT / "docs" / "KIMARI4B_PLACEHOLDER_MODEL_CARD.md").read_text().lower()
    assert "not an official kimari model" in collection
    assert "reference/community" in collection
    assert "no official kimari model" in collection or "not official kimari" in collection
    assert "not released" in placeholder
    assert "no weights available" in placeholder
    assert "no gguf available" in placeholder
    assert "gate: **blocked**" in placeholder


def test_profile_and_visual_docs_exist():
    assert (PROJECT_ROOT / "docs" / "HUGGINGFACE_PROFILE_SMOUJ013.md").exists()
    assert (PROJECT_ROOT / "docs" / "BRAND_ASSETS_PLAN.md").exists()
    assert (PROJECT_ROOT / "docs" / "KIMARI_FLOW_DIAGRAM.md").exists()
    assert "mermaid" in (PROJECT_ROOT / "docs" / "KIMARI_FLOW_DIAGRAM.md").read_text().lower()


def _load_space_app():
    app_path = PROJECT_ROOT / "huggingface" / "kimari-fit-lab" / "app.py"
    spec = importlib.util.spec_from_file_location("kimari_fit_lab_app", app_path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


def test_fit_lab_gtx1060_and_custom_vram_outputs():
    app = _load_space_app()
    output = app.build_recommendation("NVIDIA GeForce GTX 1060 6GB", 6, 16, "WSL2", "technical", "OpenClaw")
    assert "gtx1060" in output
    assert "TinyLlama" in output
    assert "Kimari-4B is **not released yet**" in output
    custom = app.build_recommendation("Custom GPU", 12, 32, "Linux", "advanced", "coding")
    assert "12 GB" in custom
    assert "Recommended profile" in custom


def test_fit_lab_commands_are_safe_static_and_complete():
    app_text = (PROJECT_ROOT / "huggingface" / "kimari-fit-lab" / "app.py").read_text().lower()
    assert "api_key" not in app_text
    assert "openai.api_key" not in app_text
    assert ".generate(" not in app_text
    assert "from_pretrained" not in app_text
    app = _load_space_app()
    commands = app.get_commands()
    assert "kimari doctor --deep" in commands
    assert "kimari pull test" in commands
    assert "kimari start --profile test" in commands


def test_release_check_mentions_public_v0155_checks():
    text = (PROJECT_ROOT / "scripts" / "release" / "check-release.py").read_text()
    assert "check_public_version_consistency.py" in text
    assert "v0.1.59" in text or "v0.1.57" in text
    assert "HUGGINGFACE_PROFILE_SMOUJ013.md" in text
