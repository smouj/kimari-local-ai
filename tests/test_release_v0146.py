"""Tests for v0.1.46-alpha release criteria.

Validates:
- Launch pack docs exist (4 docs)
- Collection seed exists and validates
- All seed entries official_kimari_model=false
- Posts say TinyLlama, not Kimari-4B release
- No token/billing/private plan text
- Version bump
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

LAUNCH_DOCS = [
    "PUBLIC_LAUNCH_PACK.md",
    "POST_X_KIMARI_GTX1060.md",
    "REDDIT_POST_KIMARI.md",
    "HUGGINGFACE_COMMUNITY_POST.md",
]


def test_launch_pack_exists():
    """docs/PUBLIC_LAUNCH_PACK.md must exist."""
    assert (PROJECT_ROOT / "docs" / "PUBLIC_LAUNCH_PACK.md").exists()


def test_x_posts_exist():
    """docs/POST_X_KIMARI_GTX1060.md must exist."""
    assert (PROJECT_ROOT / "docs" / "POST_X_KIMARI_GTX1060.md").exists()


def test_reddit_post_exists():
    """docs/REDDIT_POST_KIMARI.md must exist."""
    assert (PROJECT_ROOT / "docs" / "REDDIT_POST_KIMARI.md").exists()


def test_hf_community_post_exists():
    """docs/HUGGINGFACE_COMMUNITY_POST.md must exist."""
    assert (PROJECT_ROOT / "docs" / "HUGGINGFACE_COMMUNITY_POST.md").exists()


def test_collection_seed_exists():
    """Collection seed example JSON must exist."""
    seed_path = PROJECT_ROOT / "huggingface" / "collections" / "kimari-compatible-gguf.seed.example.json"
    assert seed_path.exists(), "Collection seed not found"


def test_collection_seed_validates():
    """Collection seed must pass validation."""
    seed_path = PROJECT_ROOT / "huggingface" / "collections" / "kimari-compatible-gguf.seed.example.json"
    if not seed_path.exists():
        return  # Previous test covers this
    data = json.loads(seed_path.read_text())
    for i, entry in enumerate(data):
        assert "model_id" in entry, f"Entry {i + 1}: missing model_id"
        assert "license" in entry, f"Entry {i + 1}: missing license"
        assert "official_kimari_model" in entry, f"Entry {i + 1}: missing official_kimari_model"


def test_all_seed_entries_not_official():
    """All collection seed entries must have official_kimari_model=false."""
    seed_path = PROJECT_ROOT / "huggingface" / "collections" / "kimari-compatible-gguf.seed.example.json"
    if not seed_path.exists():
        return
    data = json.loads(seed_path.read_text())
    for i, entry in enumerate(data):
        assert entry.get("official_kimari_model") is False, (
            f"Entry {i + 1} ({entry.get('model_id', 'unknown')}): official_kimari_model must be false"
        )


def test_collection_seed_validator_exists():
    """Collection seed validator script must exist."""
    assert (PROJECT_ROOT / "scripts" / "huggingface" / "validate_collection_seed.py").exists()


def test_posts_say_tinyllama_not_kimari_4b():
    """Launch pack posts must reference TinyLlama, not claim Kimari-4B released."""
    for doc_name in LAUNCH_DOCS:
        doc_path = PROJECT_ROOT / "docs" / doc_name
        if not doc_path.exists():
            continue
        doc_content = doc_path.read_text().lower()
        assert "tinyllama" in doc_content or "tiny llama" in doc_content, (
            f"{doc_name} should reference TinyLlama test model"
        )
        assert "claim kimari-4b is released" not in doc_content, f"{doc_name} must not claim Kimari-4B is released"
        assert "claim kimari-4b is available" not in doc_content, f"{doc_name} must not claim Kimari-4B is available"


def test_no_official_kimari_model_claims():
    """Posts must not claim official Kimari models."""
    for doc_name in LAUNCH_DOCS:
        doc_path = PROJECT_ROOT / "docs" / doc_name
        if not doc_path.exists():
            continue
        doc_content = doc_path.read_text().lower()
        assert "are official kimari models" not in doc_content, f"{doc_name} should not claim official Kimari models"


def test_no_billing_or_tokens_in_launch_docs():
    """No billing/subscription/token values in launch pack docs."""
    forbidden = ["subscription active", "billing active", "paid account", "sk-", 'api_key = "']
    for doc_name in LAUNCH_DOCS:
        doc_path = PROJECT_ROOT / "docs" / doc_name
        if not doc_path.exists():
            continue
        doc_content = doc_path.read_text().lower()
        for pattern in forbidden:
            assert pattern not in doc_content, f"{doc_name} contains forbidden pattern: {pattern[:15]}..."


def test_screenshots_manifest_safe():
    """Screenshots manifest should not contain real paths or tokens."""
    manifest = PROJECT_ROOT / "docs" / "assets" / "screenshots" / "gtx1060-wsl2" / "manifest.example.json"
    if not manifest.exists():
        return  # No manifest to check
    content = manifest.read_text().lower()
    assert "/home/smouj/" not in content, "Manifest contains real home path"
    assert "sk-" not in content, "Manifest contains API key pattern"


def test_version_bump():
    """pyproject.toml and __init__.py must be >= 0.1.46-alpha."""
    import re

    pyproject = (PROJECT_ROOT / "pyproject.toml").read_text()
    init = (PROJECT_ROOT / "kimari" / "__init__.py").read_text()
    match_p = re.search(r'version\s*=\s*["\']([^"\']+)["\']', pyproject)
    match_i = re.search(r'__version__\s*=\s*["\']([^"\']+)["\']', init)
    assert match_p and match_p.group(1) >= "0.1.46-alpha", (
        f"pyproject.toml version must be >= 0.1.46-alpha, got {match_p.group(1) if match_p else 'not found'}"
    )
    assert match_i and match_i.group(1) >= "0.1.46-alpha", (
        f"__init__.py version must be >= 0.1.46-alpha, got {match_i.group(1) if match_i else 'not found'}"
    )


def test_changelog_has_v0146():
    """CHANGELOG.md must have [0.1.46-alpha] entry."""
    changelog = (PROJECT_ROOT / "CHANGELOG.md").read_text()
    assert "[0.1.46-alpha]" in changelog, "CHANGELOG.md missing [0.1.46-alpha] entry"


def test_roadmap_has_v0146():
    """ROADMAP.md must mention v0.1.46-alpha."""
    roadmap = (PROJECT_ROOT / "ROADMAP.md").read_text()
    assert "v0.1.46-alpha" in roadmap, "ROADMAP.md missing v0.1.46-alpha"


if __name__ == "__main__":
    import pytest

    sys.exit(pytest.main([__file__, "-v"]))
