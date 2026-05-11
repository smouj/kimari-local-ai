"""
Release validation tests for Kimari Local AI v0.1.14-alpha.

Verifies community standards, packaging polish, CI configuration,
and contributor readiness for the v0.1.13 release.
"""

import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent


class TestCommunityFiles:
    """Community standard files exist and have proper content."""

    def test_code_of_conduct_exists(self):
        assert (PROJECT_ROOT / "CODE_OF_CONDUCT.md").exists(), "CODE_OF_CONDUCT.md missing"

    def test_code_of_conduct_mentions_contributor_covenant(self):
        text = (PROJECT_ROOT / "CODE_OF_CONDUCT.md").read_text().lower()
        assert "contributor covenant" in text, "Contributor Covenant attribution missing"

    def test_code_of_conduct_has_scope(self):
        text = (PROJECT_ROOT / "CODE_OF_CONDUCT.md").read_text()
        assert "Scope" in text, "Scope section missing"

    def test_code_of_conduct_has_enforcement(self):
        text = (PROJECT_ROOT / "CODE_OF_CONDUCT.md").read_text()
        assert "Enforcement" in text, "Enforcement section missing"

    def test_code_of_conduct_no_public_issue_reporting(self):
        text = (PROJECT_ROOT / "CODE_OF_CONDUCT.md").read_text().lower()
        assert "github issue" not in text or "do not" in text, "Should not direct reports to public issues"

    def test_support_md_exists(self):
        assert (PROJECT_ROOT / "SUPPORT.md").exists(), "SUPPORT.md missing"

    def test_support_mentions_security(self):
        text = (PROJECT_ROOT / "SUPPORT.md").read_text()
        assert "SECURITY.md" in text, "SUPPORT.md should reference SECURITY.md"

    def test_support_mentions_code_of_conduct(self):
        text = (PROJECT_ROOT / "SUPPORT.md").read_text()
        assert "CODE_OF_CONDUCT" in text, "SUPPORT.md should reference CODE_OF_CONDUCT.md"

    def test_contributing_exists(self):
        assert (PROJECT_ROOT / "CONTRIBUTING.md").exists(), "CONTRIBUTING.md missing"

    def test_contributing_mentions_default_profile_rule(self):
        text = (PROJECT_ROOT / "CONTRIBUTING.md").read_text().lower()
        assert "test" in text and "default_profile" in text, "Should mention default_profile=test rule"

    def test_contributing_mentions_ruff(self):
        text = (PROJECT_ROOT / "CONTRIBUTING.md").read_text().lower()
        assert "ruff" in text, "Should mention ruff linting"

    def test_governance_exists(self):
        assert (PROJECT_ROOT / "GOVERNANCE.md").exists(), "GOVERNANCE.md missing"

    def test_governance_mentions_maintainer(self):
        text = (PROJECT_ROOT / "GOVERNANCE.md").read_text()
        assert "Smouj" in text, "Should mention Smouj as maintainer"

    def test_maintainers_exists(self):
        assert (PROJECT_ROOT / "MAINTAINERS.md").exists(), "MAINTAINERS.md missing"

    def test_maintainers_mentions_smouj(self):
        text = (PROJECT_ROOT / "MAINTAINERS.md").read_text()
        assert "Smouj" in text, "Should mention Smouj as maintainer"


class TestIssueTemplates:
    """GitHub issue templates exist with required fields."""

    TEMPLATE_DIR = PROJECT_ROOT / ".github" / "ISSUE_TEMPLATE"

    def test_bug_report_yml_exists(self):
        assert (self.TEMPLATE_DIR / "bug_report.yml").exists()

    def test_feature_request_yml_exists(self):
        assert (self.TEMPLATE_DIR / "feature_request.yml").exists()

    def test_performance_report_yml_exists(self):
        assert (self.TEMPLATE_DIR / "performance_report.yml").exists()

    def test_integration_request_yml_exists(self):
        assert (self.TEMPLATE_DIR / "integration_request.yml").exists()

    def test_config_yml_exists(self):
        assert (self.TEMPLATE_DIR / "config.yml").exists()

    def test_bug_report_has_name(self):
        text = (self.TEMPLATE_DIR / "bug_report.yml").read_text()
        assert "name:" in text

    def test_bug_report_has_gpu_field(self):
        text = (self.TEMPLATE_DIR / "bug_report.yml").read_text().lower()
        assert "gpu" in text, "Bug report should ask for GPU info"

    def test_bug_report_has_version_field(self):
        text = (self.TEMPLATE_DIR / "bug_report.yml").read_text().lower()
        assert "version" in text, "Bug report should ask for Kimari version"

    def test_performance_report_has_model_field(self):
        text = (self.TEMPLATE_DIR / "performance_report.yml").read_text().lower()
        assert "model" in text and "quantiz" in text, "Should ask for model and quantization"

    def test_integration_request_has_tool_field(self):
        text = (self.TEMPLATE_DIR / "integration_request.yml").read_text().lower()
        assert "tool" in text, "Should ask for tool name"

    def test_config_yml_disables_blank_issues(self):
        text = (self.TEMPLATE_DIR / "config.yml").read_text()
        assert "blank_issues_enabled: false" in text, "Should disable blank issues"


class TestPRTemplate:
    """Pull request template exists with checklist."""

    def test_pr_template_exists(self):
        assert (PROJECT_ROOT / ".github" / "pull_request_template.md").exists()

    def test_pr_template_has_checklist(self):
        text = (PROJECT_ROOT / ".github" / "pull_request_template.md").read_text()
        assert "- [ ]" in text, "Should have checklist items"

    def test_pr_template_mentions_no_gguf(self):
        text = (PROJECT_ROOT / ".github" / "pull_request_template.md").read_text().lower()
        assert "gguf" in text, "Should mention no GGUF files"

    def test_pr_template_mentions_no_secrets(self):
        text = (PROJECT_ROOT / ".github" / "pull_request_template.md").read_text().lower()
        assert "secret" in text, "Should mention no secrets"


class TestPackagingPolish:
    """Packaging improvements for v0.1.13."""

    def test_pyproject_uses_spdx_license(self):
        text = (PROJECT_ROOT / "pyproject.toml").read_text()
        assert 'license = "MIT"' in text, "Should use SPDX license format"

    def test_pyproject_no_license_classifier(self):
        text = (PROJECT_ROOT / "pyproject.toml").read_text()
        assert "License ::" not in text, "License classifier should be removed with SPDX format"

    def test_manifest_in_exists(self):
        assert (PROJECT_ROOT / "MANIFEST.in").exists(), "MANIFEST.in missing"

    def test_manifest_in_includes_community_files(self):
        text = (PROJECT_ROOT / "MANIFEST.in").read_text()
        for f in ["CODE_OF_CONDUCT.md", "CONTRIBUTING.md", "SUPPORT.md", "GOVERNANCE.md", "MAINTAINERS.md"]:
            assert f in text, f"MANIFEST.in should include {f}"

    def test_manifest_in_excludes_gguf(self):
        text = (PROJECT_ROOT / "MANIFEST.in").read_text()
        assert "gguf" in text.lower(), "MANIFEST.in should exclude GGUF files"

    def test_pyproject_package_data_includes_defaults(self):
        text = (PROJECT_ROOT / "pyproject.toml").read_text()
        assert "defaults" in text, "package-data should include defaults/*.json"


class TestCIWheelInstall:
    """CI configuration includes wheel install smoke test."""

    def test_ci_yml_exists(self):
        assert (PROJECT_ROOT / ".github" / "workflows" / "ci.yml").exists()

    def test_ci_has_wheel_install_smoke_job(self):
        text = (PROJECT_ROOT / ".github" / "workflows" / "ci.yml").read_text()
        assert "wheel-install-smoke" in text, "wheel-install-smoke job missing from CI"

    def test_ci_wheel_install_tests_version(self):
        text = (PROJECT_ROOT / ".github" / "workflows" / "ci.yml").read_text()
        assert "kimari --version" in text, "Wheel install should test kimari --version"

    def test_ci_wheel_install_tests_token(self):
        text = (PROJECT_ROOT / ".github" / "workflows" / "ci.yml").read_text()
        assert "token create" in text or "token" in text, "Wheel install should test token commands"


class TestReadmeCommunityLinks:
    """README links to community documentation."""

    def test_readme_links_to_code_of_conduct(self):
        text = (PROJECT_ROOT / "README.md").read_text()
        assert "CODE_OF_CONDUCT.md" in text, "README should link to CODE_OF_CONDUCT.md"

    def test_readme_links_to_contributing(self):
        text = (PROJECT_ROOT / "README.md").read_text()
        assert "CONTRIBUTING.md" in text, "README should link to CONTRIBUTING.md"

    def test_readme_links_to_support(self):
        text = (PROJECT_ROOT / "README.md").read_text()
        assert "SUPPORT.md" in text, "README should link to SUPPORT.md"


class TestVersionConsistency:
    """Version is consistent across all files."""

    def test_pyproject_version(self):
        text = (PROJECT_ROOT / "pyproject.toml").read_text()
        assert "0.1.22-alpha" in text

    def test_init_version(self):
        text = (PROJECT_ROOT / "kimari" / "__init__.py").read_text()
        assert "0.1.22-alpha" in text

    def test_readme_version_badge(self):
        text = (PROJECT_ROOT / "README.md").read_text()
        assert "0.1.22-alpha" in text

    def test_index_html_version(self):
        text = (PROJECT_ROOT / "docs" / "index.html").read_text()
        assert "0.1.22-alpha" in text


class TestNoFalseClaims:
    """Critical rules: no false claims about Kimari-4B or Responses API."""

    def test_no_kimari4b_released_claim(self):
        all_text = ""
        for f in ["README.md", "CHANGELOG.md", "docs/index.html"]:
            path = PROJECT_ROOT / f
            if path.exists():
                all_text += path.read_text().lower() + " "
        false_patterns = [
            "kimari-4b is available now",
            "kimari-4b can be downloaded",
            "download kimari-4b",
            "kimari-4b weights available",
            "kimari-4b has been released",
        ]
        for p in false_patterns:
            assert p not in all_text, f"False claim found: {p}"

    def test_no_responses_api_supported_claim(self):
        all_text = ""
        for f in ["README.md", "CHANGELOG.md", "docs/index.html"]:
            path = PROJECT_ROOT / f
            if path.exists():
                all_text += path.read_text().lower() + " "
        false_patterns = [
            "responses api supported",
            "responses api is supported",
        ]
        for p in false_patterns:
            assert p not in all_text, f"False claim found: {p}"

    def test_default_profile_is_test(self):
        config_path = PROJECT_ROOT / "config" / "kimari.profiles.json"
        if config_path.exists():
            config = json.loads(config_path.read_text())
            assert config.get("default_profile") == "test"
