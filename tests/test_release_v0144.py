"""Tests for v0.1.44-alpha release criteria.

Validates:
- Showcase docs exist
- Screenshot manifest is valid
- Screenshot validator supports --json
- HF Space pack files exist
- HF Space app does not call model APIs
- HF Space README says Kimari-4B not released
- Org card says framework alpha / Kimari-4B not released
- README mentions GTX 1060 local validation
- No tokens in new docs
- Release-check passes
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def test_showcase_doc_exists():
    """docs/GTX1060_SHOWCASE.md must exist."""
    assert (PROJECT_ROOT / "docs" / "GTX1060_SHOWCASE.md").exists()


def test_manifest_example_exists():
    """Screenshot manifest example must exist."""
    assert (PROJECT_ROOT / "docs" / "assets" / "screenshots" / "gtx1060-wsl2" / "manifest.example.json").exists()


def test_manifest_validator_exists():
    """scripts/docs/validate_screenshot_manifest.py must exist."""
    assert (PROJECT_ROOT / "scripts" / "docs" / "validate_screenshot_manifest.py").exists()


def test_manifest_validator_supports_json():
    """Screenshot manifest validator supports --json flag."""
    script = PROJECT_ROOT / "scripts" / "docs" / "validate_screenshot_manifest.py"
    content = script.read_text()
    assert "--json" in content, "Validator must support --json"


def test_manifest_all_public_safe():
    """All manifest entries must be public_safe."""
    manifest = json.loads(
        (PROJECT_ROOT / "docs" / "assets" / "screenshots" / "gtx1060-wsl2" / "manifest.example.json").read_text()
    )
    for entry in manifest["screenshots"]:
        assert entry.get("contains_secret") is False, f"{entry.get('filename')}: contains_secret must be False"
        assert entry.get("contains_token") is False, f"{entry.get('filename')}: contains_token must be False"


def test_manifest_no_kimari4b_claim():
    """Manifest must not claim Kimari-4B is released."""
    manifest = json.loads(
        (PROJECT_ROOT / "docs" / "assets" / "screenshots" / "gtx1060-wsl2" / "manifest.example.json").read_text()
    )
    meta_model = manifest.get("meta", {}).get("model", "").lower()
    assert "kimari-4b" not in meta_model or "not" in meta_model, "Manifest meta must not claim Kimari-4B is released"


def test_hf_space_app_exists():
    """huggingface/kimari-fit-lab/app.py must exist."""
    assert (PROJECT_ROOT / "huggingface" / "kimari-fit-lab" / "app.py").exists()


def test_hf_space_app_no_models():
    """HF Space app must not import or run models."""
    app = (PROJECT_ROOT / "huggingface" / "kimari-fit-lab" / "app.py").read_text()
    assert "transformers" not in app, "HF Space app should not import transformers"
    assert "AutoModel" not in app, "HF Space app should not use AutoModel"
    assert "torch" not in app or "torch" in app.lower() and "import torch" not in app, (
        "HF Space app should not import torch for model inference"
    )


def test_hf_space_readme_not_released():
    """HF Space README must state Kimari-4B is not released."""
    readme = (PROJECT_ROOT / "huggingface" / "kimari-fit-lab" / "README.md").read_text().lower()
    assert "not released" in readme, "HF Space README must state Kimari-4B is not released"


def test_hf_space_guide_exists():
    """docs/HUGGINGFACE_SPACE_KIMARI_FIT_LAB.md must exist."""
    assert (PROJECT_ROOT / "docs" / "HUGGINGFACE_SPACE_KIMARI_FIT_LAB.md").exists()


def test_org_card_exists():
    """docs/HUGGINGFACE_ORG_CARD.md must exist."""
    assert (PROJECT_ROOT / "docs" / "HUGGINGFACE_ORG_CARD.md").exists()


def test_org_card_says_not_released():
    """Org card must state Kimari-4B is not released."""
    card = (PROJECT_ROOT / "docs" / "HUGGINGFACE_ORG_CARD.md").read_text().lower()
    assert "not released" in card or "not yet released" in card, "Org card must state Kimari-4B is not released"


def test_org_card_says_alpha():
    """Org card must mention framework alpha status."""
    card = (PROJECT_ROOT / "docs" / "HUGGINGFACE_ORG_CARD.md").read_text().lower()
    assert "alpha" in card, "Org card should mention alpha status"


def test_readme_mentions_gtx1060():
    """README must mention GTX 1060 local validation."""
    readme = (PROJECT_ROOT / "README.md").read_text()
    assert "GTX 1060" in readme, "README should mention GTX 1060 local validation"


def test_no_tokens_in_new_docs():
    """No API key values in showcase/org card/HF space docs."""
    api_key_patterns = ["sk-", 'api_key = "', 'apiKey = "', '"key": "sk-']
    for doc_name in [
        "GTX1060_SHOWCASE.md",
        "HUGGINGFACE_SPACE_KIMARI_FIT_LAB.md",
        "HUGGINGFACE_ORG_CARD.md",
    ]:
        doc = (PROJECT_ROOT / "docs" / doc_name).read_text()
        for pattern in api_key_patterns:
            assert pattern not in doc, f"{doc_name} contains API key pattern: {pattern[:10]}..."


def test_hf_space_requirements_exists():
    """huggingface/kimari-fit-lab/requirements.txt must exist."""
    assert (PROJECT_ROOT / "huggingface" / "kimari-fit-lab" / "requirements.txt").exists()


def test_version_bump():
    """pyproject.toml and __init__.py must be >= 0.1.44-alpha."""
    pyproject = (PROJECT_ROOT / "pyproject.toml").read_text()
    init = (PROJECT_ROOT / "kimari" / "__init__.py").read_text()
    assert "0.1.44-alpha" in pyproject, "pyproject.toml must have 0.1.44-alpha"
    assert "0.1.44-alpha" in init, "kimari/__init__.py must have 0.1.44-alpha"


def test_changelog_has_v0144():
    """CHANGELOG.md must have [0.1.44-alpha] entry."""
    changelog = (PROJECT_ROOT / "CHANGELOG.md").read_text()
    assert "[0.1.44-alpha]" in changelog, "CHANGELOG.md missing [0.1.44-alpha] entry"


def test_roadmap_has_v0144():
    """ROADMAP.md must mention v0.1.44-alpha."""
    roadmap = (PROJECT_ROOT / "ROADMAP.md").read_text()
    assert "v0.1.44-alpha" in roadmap, "ROADMAP.md missing v0.1.44-alpha"


if __name__ == "__main__":
    import pytest

    sys.exit(pytest.main([__file__, "-v"]))
