"""Release validation tests for v0.1.57-alpha — Open-license policy checks."""

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

VERSION = "0.1.57-alpha"
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


def test_open_license_policy_exists():
    assert (ROOT / "docs" / "KIMARI_OPEN_LICENSE_POLICY.md").exists(), "KIMARI_OPEN_LICENSE_POLICY.md missing"


def test_base_model_license_matrix_exists():
    assert (ROOT / "docs" / "KIMARI_BASE_MODEL_LICENSE_MATRIX.md").exists(), (
        "KIMARI_BASE_MODEL_LICENSE_MATRIX.md missing"
    )


def test_bakeoff_plan_exists():
    assert (ROOT / "docs" / "KIMARI_OPEN_BASE_BAKEOFF_PLAN.md").exists(), "KIMARI_OPEN_BASE_BAKEOFF_PLAN.md missing"


def test_dataset_license_plan_exists():
    assert (ROOT / "docs" / "KIMARI_SFT_V1_DATASET_LICENSE_PLAN.md").exists(), (
        "KIMARI_SFT_V1_DATASET_LICENSE_PLAN.md missing"
    )


def test_sft_training_plan_exists():
    assert (ROOT / "docs" / "KIMARI_SFT_V1_TRAINING_PLAN.md").exists(), "KIMARI_SFT_V1_TRAINING_PLAN.md missing"


def test_release_gate_has_license_requirements():
    content = (ROOT / "docs" / "KIMARI4B_RELEASE_GATE.md").read_text()
    assert "license" in content.lower(), "Release gate missing license requirements"
    assert "permissive" in content.lower(), "Release gate missing permissive requirement"
    assert "BASE_MODEL_LICENSE_MATRIX" in content or "license matrix" in content.lower(), (
        "Release gate missing license matrix reference"
    )


def test_open_license_policy_content():
    content = (ROOT / "docs" / "KIMARI_OPEN_LICENSE_POLICY.md").read_text()
    # Check key sections
    assert "Apache 2.0" in content, "Policy missing Apache 2.0"
    assert "MIT" in content, "Policy missing MIT"
    assert "non-commercial" in content.lower() or "Non-Commercial" in content, "Policy missing NC blocking"
    assert "research-only" in content.lower() or "Research-Only" in content, "Policy missing research-only blocking"
    # Check approved models
    assert "Qwen2.5-1.5B" in content or "Qwen/Qwen2.5-1.5B-Instruct" in content, "Policy missing Qwen2.5-1.5B"
    assert "SmolLM3-3B" in content or "HuggingFaceTB/SmolLM3-3B" in content, "Policy missing SmolLM3-3B"


def test_license_matrix_content():
    content = (ROOT / "docs" / "KIMARI_BASE_MODEL_LICENSE_MATRIX.md").read_text()
    assert "Apache 2.0" in content, "Matrix missing Apache 2.0"
    assert "Qwen/Qwen2.5-1.5B-Instruct" in content, "Matrix missing Qwen2.5-1.5B"
    assert "SmolLM3-3B" in content or "HuggingFaceTB/SmolLM3-3B" in content, "Matrix missing SmolLM3-3B"
    assert "Qwen3-4B" in content, "Matrix missing Qwen3-4B"
    # Check blocked models
    assert "qwen-research" in content.lower() or "research" in content.lower(), "Matrix missing research-only blocking"
    assert "gemma" in content.lower() or "Gemma" in content, "Matrix missing Gemma reference"


def test_bakeoff_plan_content():
    content = (ROOT / "docs" / "KIMARI_OPEN_BASE_BAKEOFF_PLAN.md").read_text()
    assert "Qwen2.5-1.5B" in content, "Bakeoff plan missing Qwen2.5-1.5B"
    assert "SmolLM2-1.7B" in content or "SmolLM2" in content, "Bakeoff plan missing SmolLM2"
    assert "SmolLM3-3B" in content, "Bakeoff plan missing SmolLM3-3B"
    assert "Qwen3-4B" in content, "Bakeoff plan missing Qwen3-4B"
    assert "BLOCKED" in content, "Bakeoff plan missing BLOCKED"


def test_readme_open_license_section():
    content = (ROOT / "README.md").read_text()
    assert "Open-License" in content or "open-license" in content.lower(), "README missing open-license section"
    assert "Apache 2.0" in content, "README missing Apache 2.0 in license section"


def test_index_html_license_card():
    content = (ROOT / "docs" / "index.html").read_text()
    assert "Open-License" in content or "open-license" in content.lower() or "Open License" in content, (
        "index.html missing license card"
    )
    assert "KIMARI_OPEN_LICENSE_POLICY" in content, "index.html missing policy link"


def test_changelog_has_v0157():
    content = (ROOT / "CHANGELOG.md").read_text()
    assert "0.1.57-alpha" in content, "CHANGELOG missing v0.1.57-alpha entry"


def test_roadmap_has_v0157():
    content = (ROOT / "ROADMAP.md").read_text()
    assert "0.1.57" in content, "ROADMAP missing v0.1.57"


def test_no_blocked_model_marked_public():
    """Verify blocked models are not listed as approved official bases."""
    matrix = (ROOT / "docs" / "KIMARI_BASE_MODEL_LICENSE_MATRIX.md").read_text()
    # Blocked models must NOT appear in the Allowed section
    blocked_models = ["Qwen/Qwen2.5-3B-Instruct", "google/gemma-3-4b-it"]
    for model in blocked_models:
        allowed_section = matrix.split("Blocked")[0] if "Blocked" in matrix else ""
        assert model not in allowed_section, f"Blocked model {model} found in Allowed section"


def test_gate_blocked_in_hf_docs():
    org = (ROOT / "docs" / "HUGGINGFACE_ORG_CARD.md").read_text()
    deploy = (ROOT / "docs" / "HUGGINGFACE_DEPLOYMENT_STATUS.md").read_text()
    assert "BLOCKED" in org.upper(), "HF org card missing BLOCKED"
    assert "BLOCKED" in deploy.upper(), "Deployment status missing BLOCKED"


def test_kimari4b_not_released():
    readme = (ROOT / "README.md").read_text()
    index = (ROOT / "docs" / "index.html").read_text()
    assert "not released" in readme.lower() or "Not Released" in readme, "README missing 'not released'"
    assert "not released" in index.lower() or "Not Released" in index, "index.html missing 'not released'"
