"""
Tests for v0.1.9-alpha: GitHub Pages, SEO, WSL2 guide, publishing docs.
"""

import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def test_index_html_contains_version():
    """docs/index.html contains the current version string."""
    index_html = PROJECT_ROOT / "docs" / "index.html"
    text = index_html.read_text()
    assert "0.1.14-alpha" in text, "Current version not found in docs/index.html"


def test_index_html_has_canonical():
    """docs/index.html has a canonical URL."""
    text = (PROJECT_ROOT / "docs" / "index.html").read_text()
    assert "canonical" in text, "Canonical URL missing from docs/index.html"
    assert "smouj.github.io/kimari-local-ai" in text, "Canonical URL domain not found"


def test_index_html_has_open_graph():
    """docs/index.html has Open Graph metadata."""
    text = (PROJECT_ROOT / "docs" / "index.html").read_text()
    assert "og:title" in text, "og:title missing from docs/index.html"
    assert "og:description" in text, "og:description missing from docs/index.html"
    assert "og:image" in text, "og:image missing from docs/index.html"


def test_index_html_has_twitter_card():
    """docs/index.html has Twitter Card metadata."""
    text = (PROJECT_ROOT / "docs" / "index.html").read_text()
    assert "twitter:card" in text, "twitter:card missing from docs/index.html"


def test_index_html_has_json_ld():
    """docs/index.html has JSON-LD structured data."""
    text = (PROJECT_ROOT / "docs" / "index.html").read_text()
    assert "application/ld+json" in text, "JSON-LD script missing from docs/index.html"
    assert "SoftwareApplication" in text, "SoftwareApplication schema missing"


def test_install_wsl2_exists():
    """docs/INSTALL_WSL2.md exists."""
    assert (PROJECT_ROOT / "docs" / "INSTALL_WSL2.md").exists(), "WSL2 guide missing"


def test_install_wsl2_has_troubleshooting():
    """docs/INSTALL_WSL2.md has troubleshooting section."""
    text = (PROJECT_ROOT / "docs" / "INSTALL_WSL2.md").read_text()
    assert "troubleshoot" in text.lower(), "Troubleshooting section missing from WSL2 guide"
    assert "nvidia-smi" in text.lower(), "nvidia-smi troubleshooting missing"


def test_publishing_guide_exists():
    """docs/PUBLISHING.md exists."""
    assert (PROJECT_ROOT / "docs" / "PUBLISHING.md").exists(), "Publishing guide missing"


def test_publishing_guide_has_testpypi():
    """docs/PUBLISHING.md mentions TestPyPI workflow."""
    text = (PROJECT_ROOT / "docs" / "PUBLISHING.md").read_text()
    assert "testpypi" in text.lower(), "TestPyPI not mentioned in publishing guide"
    assert "twine upload" in text.lower(), "twine upload not mentioned in publishing guide"


def test_release_check_script_passes():
    """scripts/release/check-release.py exits with code 0."""
    result = subprocess.run(
        [sys.executable, "scripts/release/check-release.py"],
        capture_output=True,
        text=True,
        cwd=str(PROJECT_ROOT),
    )
    assert result.returncode == 0, f"check-release.py failed:\n{result.stdout}\n{result.stderr}"


def test_readme_says_kimari_4b_not_released():
    """README.md does not claim Kimari-4B is released."""
    text = (PROJECT_ROOT / "README.md").read_text().lower()
    assert "kimari-4b" in text, "Kimari-4B not mentioned in README"
    # Should contain "not yet released" or "under development"
    assert "not yet released" in text or "not released" in text or "under development" in text, (
        "README does not clarify Kimari-4B is not released"
    )
