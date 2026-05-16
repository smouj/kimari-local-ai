"""Tests for README reorganization — ensures README structure is maintained."""

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
README = REPO_ROOT / "README.md"
PYPROJECT = REPO_ROOT / "pyproject.toml"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_readme_has_required_headings():
    """README must have all required top-level sections."""
    content = _read(README)
    required = [
        "## What is Kimari?",
        "## Current Status",
        "## Quick Start",
        "## Screenshots",
        "## Gateway Dashboard",
        "## Local Runtime Validation",
        "## What Works Today",
        "## Model Status",
        "## Training and Evaluation Status",
        "## Documentation",
        "## Roadmap",
        "## Safety",
        "## License",
    ]
    for heading in required:
        assert heading in content, f"README missing required heading: {heading}"


def test_readme_has_compact_quick_start():
    """README Quick Start must be compact — not exceed 80 lines from heading to next ##."""
    content = _read(README)
    lines = content.split("\n")
    start_idx = None
    end_idx = None
    for i, line in enumerate(lines):
        if line.strip() == "## Quick Start":
            start_idx = i
        elif start_idx is not None and line.startswith("## ") and i > start_idx:
            end_idx = i
            break
    assert start_idx is not None, "Quick Start section not found"
    assert end_idx is not None, "Could not find end of Quick Start section"
    section_length = end_idx - start_idx
    assert section_length <= 80, f"Quick Start section too long: {section_length} lines (max 80)"


def test_readme_has_current_status_table():
    """README must have a Current Status table."""
    content = _read(README)
    assert "Release gate" in content or "gate" in content.lower()
    assert "BLOCKED" in content


def test_readme_has_screenshots_section():
    """README must have a Screenshots section with image references."""
    content = _read(README)
    assert "## Screenshots" in content
    # Must reference gateway screenshots
    assert "gateway-dashboard" in content or "qa-r12" in content


def test_readme_links_cli_reference():
    """README must link to CLI_REFERENCE.md."""
    content = _read(README)
    assert "CLI_REFERENCE.md" in content


def test_readme_says_kimari_4b_not_released():
    """README must clearly state Kimari-4B is not released."""
    content = _read(README)
    assert "Not released" in content or "not released" in content
    assert "Kimari-4B" in content


def test_readme_says_gate_blocked():
    """README must state the release gate is BLOCKED."""
    content = _read(README)
    assert "BLOCKED" in content


def test_readme_no_npm_as_primary_quickstart():
    """README must not mention npm as primary user flow in Quick Start."""
    content = _read(README)
    quick_start_match = re.search(r"## Quick Start(.*?)## ", content, re.DOTALL)
    if quick_start_match:
        quick_start_section = quick_start_match.group(1)
        assert "npm" not in quick_start_section, "npm should not appear in Quick Start section"


def test_readme_version_matches_pyproject():
    """Version badge in README must match pyproject.toml."""
    readme_content = _read(README)
    pyproject_content = _read(PYPROJECT)

    # Extract version from README shield URL, e.g. version-v0.1.83--alpha-9b59b6.svg
    readme_version_match = re.search(r"version-v?([0-9.]+(?:--|-)?alpha)", readme_content)
    assert readme_version_match, "Version badge not found in README"
    readme_version = readme_version_match.group(1).replace("--", "-")

    # Extract version from pyproject.toml
    pyproject_version_match = re.search(r'version\s*=\s*"([^"]+)"', pyproject_content)
    assert pyproject_version_match, "Version not found in pyproject.toml"
    pyproject_version = pyproject_version_match.group(1)

    assert readme_version == pyproject_version, (
        f"Version mismatch: README={readme_version}, pyproject={pyproject_version}"
    )


def test_cli_reference_exists():
    """docs/CLI_REFERENCE.md must exist."""
    cli_ref = REPO_ROOT / "docs" / "CLI_REFERENCE.md"
    assert cli_ref.exists(), "docs/CLI_REFERENCE.md does not exist"


def test_content_map_exists():
    """docs/README_CONTENT_MAP.md must exist."""
    content_map = REPO_ROOT / "docs" / "README_CONTENT_MAP.md"
    assert content_map.exists(), "docs/README_CONTENT_MAP.md does not exist"


def test_gateway_dashboard_doc_exists():
    """docs/GATEWAY_DASHBOARD.md must exist."""
    gateway_doc = REPO_ROOT / "docs" / "GATEWAY_DASHBOARD.md"
    assert gateway_doc.exists(), "docs/GATEWAY_DASHBOARD.md does not exist"


def test_readme_has_honesty_claims():
    """README must not contain false claims about public weights or GGUF."""
    content = _read(README).lower()
    # These phrases should NOT appear
    assert "public gguf available" not in content
    assert "kimari-4b released" not in content
    assert "kimari-4b is released" not in content
    assert "weights available" not in content


def test_readme_has_gpu_profiles():
    """README must have GPU Profiles section."""
    content = _read(README)
    assert "## GPU Profiles" in content


def test_readme_has_documentation_links():
    """README must have grouped documentation links."""
    content = _read(README)
    assert "## Documentation" in content
    assert "### Getting started" in content
    assert "### Integrations" in content or "Integration" in content


def test_readme_has_huggingface_section():
    """README must have Hugging Face section."""
    content = _read(README)
    assert "## Hugging Face" in content
    assert "huggingface.co" in content
