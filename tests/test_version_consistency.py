"""Version consistency tests — ensure all version references match the current release."""

from __future__ import annotations

import json
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

# Single source of truth — must match pyproject.toml
EXPECTED_VERSION = "0.1.84-alpha"


def _pyproject_version() -> str:
    for line in (REPO / "pyproject.toml").read_text().splitlines():
        if line.startswith("version ="):
            return line.split('"')[1]
    raise AssertionError("version not found in pyproject.toml")


def test_pyproject_version():
    assert _pyproject_version() == EXPECTED_VERSION


def test_init_version():
    init = (REPO / "kimari" / "__init__.py").read_text()
    assert f'__version__ = "{EXPECTED_VERSION}"' in init


def test_dashboard_package_version():
    pkg = json.loads((REPO / "apps" / "gateway-dashboard" / "package.json").read_text())
    assert pkg["version"] == EXPECTED_VERSION


def test_readme_badge_version():
    readme = (REPO / "README.md").read_text()
    assert f"v{EXPECTED_VERSION}" in readme


def test_check_release_version():
    script = (REPO / "scripts" / "release" / "check-release.py").read_text()
    assert f'current_version = "{EXPECTED_VERSION}"' in script


def test_changelog_has_entry():
    changelog = (REPO / "CHANGELOG.md").read_text()
    assert EXPECTED_VERSION in changelog


def test_no_stale_versions_in_key_files():
    """Key public files should not reference old version strings."""
    stale = ["0.1.83-alpha", "0.1.82-alpha", "0.1.13-alpha"]
    key_files = [
        "README.md",
        "pyproject.toml",
        "kimari/__init__.py",
        "apps/gateway-dashboard/package.json",
        "scripts/release/check-release.py",
    ]
    for path in key_files:
        content = (REPO / path).read_text()
        for old_ver in stale:
            assert old_ver not in content, f"Stale version {old_ver} found in {path}"


def test_project_truth_version():
    content = (REPO / "docs" / "PROJECT_TRUTH.md").read_text()
    assert EXPECTED_VERSION in content


def test_hf_org_card_version():
    content = (REPO / "docs" / "HUGGINGFACE_ORG_CARD.md").read_text()
    assert f"v{EXPECTED_VERSION}" in content


def test_hf_space_readme_version():
    content = (REPO / "huggingface" / "kimari-fit-lab" / "README.md").read_text()
    assert f"v{EXPECTED_VERSION}" in content
