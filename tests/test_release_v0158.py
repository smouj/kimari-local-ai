"""Release validation tests for v0.1.58-alpha — Open-license base bakeoff."""

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


def test_bakeoff_config_exists():
    assert (ROOT / "eval" / "configs" / "open_base_bakeoff_v1.yaml").exists(), "Bakeoff config missing"


def test_bakeoff_runner_exists():
    assert (ROOT / "eval" / "scripts" / "run_open_base_bakeoff.py").exists(), "Bakeoff runner missing"


def test_bakeoff_validator_exists():
    assert (ROOT / "eval" / "scripts" / "validate_open_base_bakeoff_summary.py").exists(), (
        "Bakeoff summary validator missing"
    )


def test_bakeoff_template_exists():
    assert (ROOT / "eval" / "templates" / "open_base_bakeoff_summary.template.json").exists(), (
        "Bakeoff summary template missing"
    )


def test_bakeoff_summary_pending_exists():
    assert (ROOT / "reports" / "evals" / "open_base_bakeoff_v1" / "summary.pending.json").exists(), (
        "Bakeoff summary.pending.json missing"
    )


def test_bakeoff_result_doc_exists():
    assert (ROOT / "docs" / "KIMARI_OPEN_BASE_BAKEOFF_RESULT.md").exists(), "Bakeoff result doc missing"


def test_base_selection_decision_exists():
    assert (ROOT / "docs" / "KIMARI_BASE_SELECTION_DECISION.md").exists(), "Base selection decision doc missing"


def test_allowed_candidates_are_permissive():

    with open(ROOT / "eval" / "configs" / "open_base_bakeoff_v1.yaml") as f:
        import yaml

        config = yaml.safe_load(f)

    allowed_licenses = {"apache-2.0", "mit", "bsd-2-clause", "bsd-3-clause", "cc-by-4.0"}
    for c in config.get("candidates", []):
        assert c.get("allowed", True), f"Candidate {c['model']} not marked as allowed"
        assert not c.get("blocked", False), f"Candidate {c['model']} marked as blocked"
        assert c.get("license", "").lower() in allowed_licenses, (
            f"Candidate {c['model']} has non-permissive license: {c.get('license')}"
        )


def test_blocked_candidates_not_allowed():
    import yaml

    with open(ROOT / "eval" / "configs" / "open_base_bakeoff_v1.yaml") as f:
        config = yaml.safe_load(f)

    for b in config.get("blocked_candidates", []):
        assert not b.get("allowed", False), f"Blocked candidate {b['model']} marked as allowed"
        assert b.get("blocked", True), f"Blocked candidate {b['model']} not marked as blocked"


def test_bakeoff_config_safety():
    import yaml

    with open(ROOT / "eval" / "configs" / "open_base_bakeoff_v1.yaml") as f:
        config = yaml.safe_load(f)

    assert config.get("raw_outputs_commit_allowed") is False, "raw_outputs_commit_allowed must be false"
    assert config.get("public_benchmark_allowed") is False, "public_benchmark_allowed must be false"
    assert config.get("manual_review_required") is True, "manual_review_required must be true"
    assert config.get("gate_state") == "BLOCKED", "gate_state must be BLOCKED"


def test_bakeoff_summary_pending_safety():
    import json

    with open(ROOT / "reports" / "evals" / "open_base_bakeoff_v1" / "summary.pending.json") as f:
        data = json.load(f)

    assert data.get("gate_state") == "BLOCKED", "gate_state must be BLOCKED"
    assert data.get("manual_review_required") is True, "manual_review_required must be true"
    assert data.get("public_benchmark_allowed") is False, "public_benchmark_allowed must be false"
    assert data.get("raw_outputs_committed") is False, "raw_outputs_committed must be false"
    assert data.get("raw_outputs_commit_allowed") is False, "raw_outputs_commit_allowed must be false"


def test_no_public_benchmark_claim():
    """No public benchmark claim in any public doc."""
    readme = (ROOT / "README.md").read_text()
    index = (ROOT / "docs" / "index.html").read_text()
    # "public benchmarks" in the context of "no public claims" is acceptable
    assert "public benchmark" not in readme.lower() or "no public" in readme.lower(), (
        "README has public benchmark claim"
    )
    assert "public benchmark" not in index.lower() or "no public" in index.lower(), (
        "index.html has public benchmark claim"
    )


def test_kimari4b_not_released():
    readme = (ROOT / "README.md").read_text()
    assert "not released" in readme.lower(), "README missing 'not released'"


def test_changelog_has_v0158():
    content = (ROOT / "CHANGELOG.md").read_text()
    assert "0.1.58-alpha" in content, "CHANGELOG missing v0.1.58-alpha entry"


def test_roadmap_has_v0158():
    content = (ROOT / "ROADMAP.md").read_text()
    assert "0.1.58" in content, "ROADMAP missing v0.1.58"
