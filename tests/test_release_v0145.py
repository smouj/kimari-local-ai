"""Tests for v0.1.45-alpha release criteria.

Validates:
- HF deployment doc exists with URLs
- README links to HF Space
- Collection doc says reference/community models
- Social proof snippets exist
- No billing/plan mentions in new docs
- No tokens in new docs
- Version bump
"""

from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def test_hf_deployment_status_exists():
    """docs/HUGGINGFACE_DEPLOYMENT_STATUS.md must exist."""
    assert (PROJECT_ROOT / "docs" / "HUGGINGFACE_DEPLOYMENT_STATUS.md").exists()


def test_hf_collections_doc_exists():
    """docs/HUGGINGFACE_COLLECTIONS.md must exist."""
    assert (PROJECT_ROOT / "docs" / "HUGGINGFACE_COLLECTIONS.md").exists()


def test_social_proof_snippets_exists():
    """docs/SOCIAL_PROOF_SNIPPETS.md must exist."""
    assert (PROJECT_ROOT / "docs" / "SOCIAL_PROOF_SNIPPETS.md").exists()


def test_readme_links_hf_space():
    """README must link to the HF Space."""
    readme = (PROJECT_ROOT / "README.md").read_text()
    assert "huggingface.co/spaces/kimari-ai/kimari-fit-lab" in readme, (
        "README should link to kimari-ai/kimari-fit-lab Space"
    )


def test_readme_says_kimari_4b_not_released():
    """README must say Kimari-4B is not released."""
    readme = (PROJECT_ROOT / "README.md").read_text().lower()
    assert "not released" in readme or "not yet released" in readme, "README should say Kimari-4B is not released"


def test_collection_doc_says_reference():
    """Collection doc must say reference/community models, not official."""
    doc = (PROJECT_ROOT / "docs" / "HUGGINGFACE_COLLECTIONS.md").read_text().lower()
    assert "reference" in doc or "community" in doc, "Collection doc should mention reference/community models"
    # Check that there are no AFFIRMATIVE claims of official models
    # (Negations like "NOT official" or "Do not claim" are fine)
    affirmative_patterns = ["are official kimari models", "is an official kimari model", "official kimari release"]
    for pattern in affirmative_patterns:
        assert pattern not in doc, f"Collection doc should not affirmatively claim: {pattern}"


def test_no_billing_mentions():
    """No billing/plan/subscription mentions in HF docs."""
    billing_patterns = ["subscription active", "billing active", "paid account", "pro subscription"]
    for doc_name in [
        "HUGGINGFACE_DEPLOYMENT_STATUS.md",
        "HUGGINGFACE_SPACE_KIMARI_FIT_LAB.md",
        "HUGGINGFACE_ORG_CARD.md",
        "HUGGINGFACE_COLLECTIONS.md",
        "SOCIAL_PROOF_SNIPPETS.md",
    ]:
        doc_path = PROJECT_ROOT / "docs" / doc_name
        if doc_path.exists():
            doc_content = doc_path.read_text().lower()
            for pattern in billing_patterns:
                assert pattern not in doc_content, f"{doc_name} contains billing pattern: {pattern}"


def test_no_tokens_in_hf_docs():
    """No API key values in HF docs."""
    api_key_patterns = ["sk-", 'api_key = "', 'apiKey = "', '"key": "sk-']
    for doc_name in [
        "HUGGINGFACE_DEPLOYMENT_STATUS.md",
        "HUGGINGFACE_SPACE_KIMARI_FIT_LAB.md",
        "HUGGINGFACE_ORG_CARD.md",
        "HUGGINGFACE_COLLECTIONS.md",
        "SOCIAL_PROOF_SNIPPETS.md",
    ]:
        doc_path = PROJECT_ROOT / "docs" / doc_name
        if doc_path.exists():
            doc_content = doc_path.read_text()
            for pattern in api_key_patterns:
                assert pattern not in doc_content, f"{doc_name} contains API key pattern: {pattern[:10]}..."


def test_hf_deployment_doc_has_space_url():
    """HF deployment doc must have Space URL."""
    doc = (PROJECT_ROOT / "docs" / "HUGGINGFACE_DEPLOYMENT_STATUS.md").read_text()
    assert "kimari-ai/kimari-fit-lab" in doc, "Deployment doc should mention kimari-ai/kimari-fit-lab"


def test_hf_deployment_doc_has_org_card_url():
    """HF deployment doc must have org card URL."""
    doc = (PROJECT_ROOT / "docs" / "HUGGINGFACE_DEPLOYMENT_STATUS.md").read_text()
    assert "kimari-ai/README" in doc, "Deployment doc should mention kimari-ai/README org card"


def test_version_bump():
    """pyproject.toml and __init__.py must be >= 0.1.45-alpha."""
    pyproject = (PROJECT_ROOT / "pyproject.toml").read_text()
    init = (PROJECT_ROOT / "kimari" / "__init__.py").read_text()
    import re

    match_p = re.search(r'version\s*=\s*["\']([^"\']+)["\']', pyproject)
    match_i = re.search(r'__version__\s*=\s*["\']([^"\']+)["\']', init)
    assert match_p and match_p.group(1) >= "0.1.45-alpha", (
        f"pyproject.toml version must be >= 0.1.45-alpha, got {match_p.group(1) if match_p else 'not found'}"
    )
    assert match_i and match_i.group(1) >= "0.1.45-alpha", (
        f"__init__.py version must be >= 0.1.45-alpha, got {match_i.group(1) if match_i else 'not found'}"
    )


def test_changelog_has_v0145():
    """CHANGELOG.md must have [0.1.45-alpha] entry."""
    changelog = (PROJECT_ROOT / "CHANGELOG.md").read_text()
    assert "[0.1.45-alpha]" in changelog, "CHANGELOG.md missing [0.1.45-alpha] entry"


def test_roadmap_has_v0145():
    """ROADMAP.md must mention v0.1.45-alpha."""
    roadmap = (PROJECT_ROOT / "ROADMAP.md").read_text()
    assert "v0.1.45-alpha" in roadmap, "ROADMAP.md missing v0.1.45-alpha"


if __name__ == "__main__":
    import pytest

    sys.exit(pytest.main([__file__, "-v"]))
