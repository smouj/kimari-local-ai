"""Release validation tests for v0.1.56-alpha."""

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

VERSION = "0.1.59-alpha"
VERSION_V = f"v{VERSION}"


def test_pyproject_version():
    content = (ROOT / "pyproject.toml").read_text()
    assert f'version = "{VERSION}"' in content, "pyproject.toml version mismatch"


def test_init_version():
    content = (ROOT / "kimari" / "__init__.py").read_text()
    assert f'__version__ = "{VERSION}"' in content, "__init__.py version mismatch"


def test_readme_version():
    content = (ROOT / "README.md").read_text()
    assert VERSION_V in content or VERSION in content, "README missing version"


def test_index_html_version():
    content = (ROOT / "docs" / "index.html").read_text()
    assert VERSION_V in content, "index.html missing version"


def test_index_html_no_stale_highlighted():
    content = (ROOT / "docs" / "index.html").read_text()
    stale = ["v0.1.39", "v0.1.28"]
    for sv in stale:
        assert sv not in content or "terminal-highlight" not in content.split(sv)[0][-50:], (
            f"Stale version {sv} appears highlighted in index.html"
        )


def test_index_html_gate_blocked():
    content = (ROOT / "docs" / "index.html").read_text()
    assert "BLOCKED" in content, "index.html missing BLOCKED"


def test_index_html_not_released():
    content = (ROOT / "docs" / "index.html").read_text()
    assert "not released" in content.lower() or "Not Released" in content, "index.html missing 'not released'"


def test_hf_org_card_version():
    content = (ROOT / "docs" / "HUGGINGFACE_ORG_CARD.md").read_text()
    assert VERSION_V in content or VERSION in content, "HF org card missing version"


def test_deployment_status_version():
    content = (ROOT / "docs" / "HUGGINGFACE_DEPLOYMENT_STATUS.md").read_text()
    assert VERSION_V in content or VERSION in content, "Deployment status missing version"


def test_run_history_exists():
    assert (ROOT / "docs" / "KIMARI4B_RUN_HISTORY.md").exists(), "KIMARI4B_RUN_HISTORY.md missing"


def test_environment_status_exists():
    assert (ROOT / "docs" / "ENVIRONMENT_STATUS.md").exists(), "ENVIRONMENT_STATUS.md missing"


def test_profile_doc_exists():
    assert (ROOT / "docs" / "HUGGINGFACE_PROFILE_SMOUJ013.md").exists(), "HUGGINGFACE_PROFILE_SMOUJ013.md missing"


def test_gate_blocked_in_hf_docs():
    org = (ROOT / "docs" / "HUGGINGFACE_ORG_CARD.md").read_text()
    deploy = (ROOT / "docs" / "HUGGINGFACE_DEPLOYMENT_STATUS.md").read_text()
    assert "BLOCKED" in org.upper(), "HF org card missing BLOCKED"
    assert "BLOCKED" in deploy.upper(), "Deployment status missing BLOCKED"


def test_no_public_weights_claim():
    org = (ROOT / "docs" / "HUGGINGFACE_ORG_CARD.md").read_text()
    deploy = (ROOT / "docs" / "HUGGINGFACE_DEPLOYMENT_STATUS.md").read_text()
    assert "no public weights" in org.lower() or "not released" in org.lower(), "HF org card missing no-public-weights"
    assert "no public weights" in deploy.lower() or "not released" in deploy.lower(), (
        "Deploy status missing no-public-weights"
    )


def test_badge_url_format():
    """Shields.io badge URL should not have 'v' prefix in the version part."""
    content = (ROOT / "README.md").read_text()
    badge_match = re.search(r"shields\.io/badge/version-([^?&]+)", content)
    if badge_match:
        badge_ver = badge_match.group(1)
        assert not badge_ver.startswith("v"), f"Badge URL has 'v' prefix: {badge_ver}"
