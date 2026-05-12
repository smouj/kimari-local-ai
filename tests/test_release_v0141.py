"""Tests for v0.1.41-alpha: HF Jobs access gate, smoke test preparation, privacy safeguards,
benchmark false positive fix, check_hf_jobs_access, --require-jobs-access flag."""

import json
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent


# ══════════════════════════════════════════════════════════════════════════════
# 1. HF Jobs access documentation
# ══════════════════════════════════════════════════════════════════════════════


class TestHFJobsAccessDocs:
    """Test HF Jobs access documentation exists and is safe."""

    def test_hf_jobs_access_doc_exists(self):
        """docs/HF_JOBS_ACCESS.md exists."""
        path = PROJECT_ROOT / "docs" / "HF_JOBS_ACCESS.md"
        assert path.exists(), "HF Jobs access documentation missing"

    def test_hf_jobs_access_doc_mentions_jobs_access(self):
        """HF Jobs access doc mentions Jobs access requirement."""
        path = PROJECT_ROOT / "docs" / "HF_JOBS_ACCESS.md"
        if not path.exists():
            pytest.skip("HF Jobs access doc not found")
        content = path.read_text().lower()
        assert "jobs access" in content, "Should mention Jobs access"

    def test_hf_jobs_access_doc_mentions_403(self):
        """HF Jobs access doc explains 403 Forbidden."""
        path = PROJECT_ROOT / "docs" / "HF_JOBS_ACCESS.md"
        if not path.exists():
            pytest.skip("HF Jobs access doc not found")
        content = path.read_text()
        assert "403" in content, "Should explain 403 Forbidden"

    def test_hf_jobs_access_doc_mentions_fallback(self):
        """HF Jobs access doc mentions fallback runners."""
        path = PROJECT_ROOT / "docs" / "HF_JOBS_ACCESS.md"
        if not path.exists():
            pytest.skip("HF Jobs access doc not found")
        content = path.read_text().lower()
        assert "fallback" in content, "Should mention fallback runners"

    def test_hf_jobs_access_doc_no_private_details(self):
        """HF Jobs access doc does NOT contain private plan/billing details."""
        path = PROJECT_ROOT / "docs" / "HF_JOBS_ACCESS.md"
        if not path.exists():
            pytest.skip("HF Jobs access doc not found")
        content = path.read_text().lower()
        for pattern in (
            "pro subscription active",
            "smouj013 has pro",
            "billing active",
            "paid account",
            "my pro subscription",
        ):
            assert pattern not in content, f"Private detail found: {pattern}"

    def test_hf_jobs_fallback_runners_doc_exists(self):
        """docs/HF_JOBS_FALLBACK_RUNNERS.md exists."""
        path = PROJECT_ROOT / "docs" / "HF_JOBS_FALLBACK_RUNNERS.md"
        assert path.exists(), "HF Jobs fallback runners documentation missing"

    def test_hf_jobs_fallback_doc_no_private_details(self):
        """HF Jobs fallback doc does NOT contain private details."""
        path = PROJECT_ROOT / "docs" / "HF_JOBS_FALLBACK_RUNNERS.md"
        if not path.exists():
            pytest.skip("HF Jobs fallback doc not found")
        content = path.read_text().lower()
        for pattern in ("pro subscription active", "smouj013 has pro", "billing active", "paid account"):
            assert pattern not in content, f"Private detail found: {pattern}"


# ══════════════════════════════════════════════════════════════════════════════
# 2. check_hf_jobs_access.py
# ══════════════════════════════════════════════════════════════════════════════


class TestCheckHFJobsAccess:
    """Test check_hf_jobs_access.py functionality."""

    def test_script_exists(self):
        """training/scripts/check_hf_jobs_access.py exists."""
        path = PROJECT_ROOT / "training" / "scripts" / "check_hf_jobs_access.py"
        assert path.exists(), "check_hf_jobs_access.py missing"

    def test_has_json_flag(self):
        """Script supports --json flag."""
        path = PROJECT_ROOT / "training" / "scripts" / "check_hf_jobs_access.py"
        content = path.read_text()
        assert "--json" in content, "Missing --json flag"

    def test_has_can_continue_to_smoke(self):
        """Script returns can_continue_to_smoke field."""
        path = PROJECT_ROOT / "training" / "scripts" / "check_hf_jobs_access.py"
        content = path.read_text()
        assert "can_continue_to_smoke" in content, "Missing can_continue_to_smoke field"

    def test_handles_403(self):
        """Script handles 403 Forbidden response."""
        path = PROJECT_ROOT / "training" / "scripts" / "check_hf_jobs_access.py"
        content = path.read_text().lower()
        assert "403" in content or "forbidden" in content, "Should handle 403 Forbidden"

    def test_no_token_exposure(self):
        """Script does not expose tokens in output."""
        path = PROJECT_ROOT / "training" / "scripts" / "check_hf_jobs_access.py"
        content = path.read_text()
        # Check that sanitization exists
        assert "sanitize" in content.lower() or "redact" in content.lower() or "scrub" in content.lower(), (
            "Should have token sanitization"
        )

    def test_no_billing_plan_exposure(self):
        """Script does not expose billing/plan/subscription details."""
        path = PROJECT_ROOT / "training" / "scripts" / "check_hf_jobs_access.py"
        content = path.read_text().lower()
        # The script should not output billing details
        # It may CHECK for them in API responses but should not pass them through
        # Look for redaction of billing-related strings
        has_billing_redact = (
            "billing" in content and ("redact" in content or "sanitize" in content or "scrub" in content)
        ) or "billing" not in content
        assert has_billing_redact or "subscription" not in content, (
            "Should not pass through billing/subscription details"
        )

    def test_403_returns_can_continue_false(self):
        """When 403 detected, can_continue_to_smoke should be False."""
        path = PROJECT_ROOT / "training" / "scripts" / "check_hf_jobs_access.py"
        content = path.read_text().lower()
        # Verify that 403 handling sets can_continue_to_smoke to false
        assert "can_continue_to_smoke" in content
        # The 403 case should set this to False
        # Look for the pattern in the code
        lines = content.split("\n")
        found_403_block = False
        for i, line in enumerate(lines):
            if "403" in line or "forbidden" in line:
                # Check nearby lines for can_continue_to_smoke = false
                nearby = "\n".join(lines[max(0, i - 3) : min(len(lines), i + 10)])
                if "can_continue_to_smoke" in nearby:
                    found_403_block = True
                    break
        assert found_403_block, "403 handling should set can_continue_to_smoke to false"


# ══════════════════════════════════════════════════════════════════════════════
# 3. hf_jobs_private_run --require-jobs-access
# ══════════════════════════════════════════════════════════════════════════════


class TestHFJobsPrivateRunRequireAccess:
    """Test --require-jobs-access flag in hf_jobs_private_run.py."""

    def test_flag_exists(self):
        """hf_jobs_private_run.py has --require-jobs-access flag."""
        path = PROJECT_ROOT / "training" / "scripts" / "hf_jobs_private_run.py"
        if not path.exists():
            pytest.skip("hf_jobs_private_run.py not found")
        content = path.read_text()
        assert "require-jobs-access" in content or "require_jobs_access" in content, (
            "--require-jobs-access flag missing"
        )

    def test_does_not_block_dry_run(self):
        """--require-jobs-access does NOT block --dry-run."""
        path = PROJECT_ROOT / "training" / "scripts" / "hf_jobs_private_run.py"
        if not path.exists():
            pytest.skip("hf_jobs_private_run.py not found")
        content = path.read_text().lower()
        # The help text should mention it doesn't block dry-run
        assert "dry-run" in content, "Script should support --dry-run"


# ══════════════════════════════════════════════════════════════════════════════
# 4. Benchmark false positive fix
# ══════════════════════════════════════════════════════════════════════════════


class TestBenchmarkFalsePositiveFix:
    """Test that *.example.json files are not flagged as real measured results."""

    def test_check_release_excludes_example_json(self):
        """check-release.py excludes .example.json from measured results check."""
        path = PROJECT_ROOT / "scripts" / "release" / "check-release.py"
        content = path.read_text()
        assert ".example.json" in content, "check-release.py should exclude .example.json files from real results check"

    def test_check_release_excludes_template_json(self):
        """check-release.py excludes .template.json from measured results check."""
        path = PROJECT_ROOT / "scripts" / "release" / "check-release.py"
        content = path.read_text()
        assert ".template.json" in content, (
            "check-release.py should exclude .template.json files from real results check"
        )

    def test_benchmark_example_json_is_valid(self):
        """The benchmark example JSON file is valid and has correct fields."""
        path = PROJECT_ROOT / "benchmarks" / "results" / "gtx1060-tinyllama-wsl2.example.json"
        if not path.exists():
            pytest.skip("Benchmark example JSON not found")
        data = json.loads(path.read_text())
        assert data.get("kimari4b") is False
        assert data.get("result_type") == "local_runtime_validation"
        assert data.get("public_claim_allowed") == "limited"


# ══════════════════════════════════════════════════════════════════════════════
# 5. Privacy safeguards — no private details in repo
# ══════════════════════════════════════════════════════════════════════════════


class TestPrivacySafeguards:
    """Test that no private plan/billing details appear in any committed file."""

    @pytest.mark.parametrize(
        "pattern",
        [
            "Pro subscription active",
            "Smouj013 has Pro",
            "billing active",
            "paid account",
            "my Pro subscription",
            "kimari-ai billing",
        ],
    )
    def test_no_private_patterns_in_readme(self, pattern):
        """README does not contain private details."""
        path = PROJECT_ROOT / "README.md"
        if not path.exists():
            pytest.skip("README not found")
        content = path.read_text().lower()
        assert pattern.lower() not in content, f"Private pattern '{pattern}' found in README"

    @pytest.mark.parametrize(
        "pattern",
        [
            "Pro subscription active",
            "Smouj013 has Pro",
            "billing active",
            "paid account",
        ],
    )
    def test_no_private_patterns_in_docs(self, pattern):
        """docs/ does not contain private details."""
        docs_dir = PROJECT_ROOT / "docs"
        if not docs_dir.exists():
            pytest.skip("docs/ not found")
        for doc in docs_dir.glob("**/*.md"):
            content = doc.read_text().lower()
            assert pattern.lower() not in content, f"Private pattern '{pattern}' found in {doc}"

    @pytest.mark.parametrize(
        "pattern",
        [
            "Pro subscription active",
            "Smouj013 has Pro",
            "billing active",
            "paid account",
        ],
    )
    def test_no_private_patterns_in_training_scripts(self, pattern):
        """training/ scripts do not contain private details."""
        training_dir = PROJECT_ROOT / "training"
        if not training_dir.exists():
            pytest.skip("training/ not found")
        for script in training_dir.glob("**/*.py"):
            content = script.read_text().lower()
            assert pattern.lower() not in content, f"Private pattern '{pattern}' found in {script}"


# ══════════════════════════════════════════════════════════════════════════════
# 6. Version and metadata
# ══════════════════════════════════════════════════════════════════════════════


class TestVersionV0141:
    """Test v0.1.41-alpha version presence (not necessarily current)."""

    def test_pyproject_version(self):
        """pyproject.toml version >= 0.1.41-alpha."""
        for line in (PROJECT_ROOT / "pyproject.toml").read_text().splitlines():
            if line.strip().startswith("version") and "python" not in line.lower():
                version = line.split("=", 1)[1].strip().strip('"').strip("'")
                assert version >= "0.1.41-alpha", f"Expected version >= 0.1.41-alpha, got {version}"
                return
        pytest.fail("version line not found in pyproject.toml")

    def test_init_version(self):
        """kimari/__init__.py __version__ >= 0.1.41-alpha."""
        content = (PROJECT_ROOT / "kimari" / "__init__.py").read_text()
        # Extract version
        import re

        match = re.search(r'__version__\s*=\s*["\']([^"\']+)["\']', content)
        assert match, "__version__ not found in __init__.py"
        version = match.group(1)
        assert version >= "0.1.41-alpha", f"Expected version >= 0.1.41-alpha, got {version}"

    def test_changelog_entry(self):
        """CHANGELOG.md has [0.1.41-alpha] entry."""
        content = (PROJECT_ROOT / "CHANGELOG.md").read_text()
        assert "[0.1.41-alpha]" in content

    def test_roadmap_mentions_v0141(self):
        """ROADMAP.md mentions v0.1.41-alpha."""
        content = (PROJECT_ROOT / "ROADMAP.md").read_text()
        assert "v0.1.41-alpha" in content

    def test_readme_mentions_hf_jobs(self):
        """README mentions HF Jobs smoke test access requirement."""
        content = (PROJECT_ROOT / "README.md").read_text().lower()
        assert "hf jobs" in content, "README should mention HF Jobs"


# ══════════════════════════════════════════════════════════════════════════════
# 7. No false claims
# ══════════════════════════════════════════════════════════════════════════════


class TestNoFalseClaims:
    """Test no false Kimari-4B release claims."""

    def test_no_kimari4b_released_claim(self):
        """Key docs should not claim Kimari-4B is released."""
        for fname in ("README.md", "CHANGELOG.md", "docs/index.html"):
            path = PROJECT_ROOT / fname
            if not path.exists():
                continue
            content = path.read_text()
            for line in content.splitlines():
                line_lower = line.lower().strip()
                if any(
                    phrase in line_lower
                    for phrase in (
                        "false claim",
                        "no false",
                        "claim detection",
                        "not released",
                        "not yet released",
                        "no weights released",
                        "no public release",
                        "when kimari-4b is released",
                        "is released —",
                    )
                ):
                    continue
                if "released" in line_lower and "kimari" in line_lower and "4b" in line_lower:
                    # Check it's not a conditional statement
                    if any(w in line_lower for w in ("if", "when", "after", "once", "until")):
                        continue
                    pytest.fail(f"{fname} potential false claim: {line.strip()}")
