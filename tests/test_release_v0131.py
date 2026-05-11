"""Release validation tests for v0.1.31-alpha.

Validates all v0.1.31 artifacts:
- validate_hf_jobs_smoke_summary.py
- hf_jobs_status.py sanitizes stderr
- Smoke execution record doc and template
- No false claims
- Gate BLOCKED
"""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent


# ---------------------------------------------------------------------------
# Version
# ---------------------------------------------------------------------------


class TestVersionV0131:
    """Test v0.1.31 version consistency."""

    def test_pyproject_version(self) -> None:
        text = (PROJECT_ROOT / "pyproject.toml").read_text()
        assert "0.1.31-alpha" in text, "pyproject.toml must have version 0.1.31-alpha"

    def test_init_version(self) -> None:
        text = (PROJECT_ROOT / "kimari" / "__init__.py").read_text()
        assert "0.1.31-alpha" in text, "__init__.py must have version 0.1.31-alpha"


# ---------------------------------------------------------------------------
# validate_hf_jobs_smoke_summary
# ---------------------------------------------------------------------------


class TestValidateSmokeSummaryV0131:
    """Test validate_hf_jobs_smoke_summary.py."""

    def test_script_exists(self) -> None:
        path = PROJECT_ROOT / "training" / "scripts" / "validate_hf_jobs_smoke_summary.py"
        assert path.exists(), "validate_hf_jobs_smoke_summary.py missing"

    def test_accepts_safe_summary(self) -> None:
        """Validator should accept a safe summary."""
        safe_summary = {
            "job_id": "test-job-123",
            "status": "pending",
            "flavor": "a10g-small",
            "training_performed": False,
            "adapter_generated": False,
            "hf_upload_performed": False,
            "gate_state": "BLOCKED",
            "logs_sanitized": True,
        }
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(safe_summary, f)
            summary_path = f.name

        try:
            result = subprocess.run(
                [
                    sys.executable,
                    "training/scripts/validate_hf_jobs_smoke_summary.py",
                    "--summary",
                    summary_path,
                    "--json",
                ],
                capture_output=True,
                text=True,
                cwd=str(PROJECT_ROOT),
                timeout=30,
            )
            assert result.returncode == 0, f"Safe summary rejected: {result.stdout}"
            data = json.loads(result.stdout)
            assert data.get("valid") is True, f"Expected valid=true: {data}"
        finally:
            Path(summary_path).unlink(missing_ok=True)

    def test_rejects_training_performed_true(self) -> None:
        """Validator should reject training_performed=true."""
        bad_summary = {
            "job_id": "test-job-123",
            "status": "completed",
            "training_performed": True,
            "adapter_generated": False,
            "hf_upload_performed": False,
            "gate_state": "BLOCKED",
            "logs_sanitized": True,
        }
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(bad_summary, f)
            summary_path = f.name

        try:
            result = subprocess.run(
                [
                    sys.executable,
                    "training/scripts/validate_hf_jobs_smoke_summary.py",
                    "--summary",
                    summary_path,
                    "--json",
                ],
                capture_output=True,
                text=True,
                cwd=str(PROJECT_ROOT),
                timeout=30,
            )
            assert result.returncode != 0, "Should reject training_performed=true"
            data = json.loads(result.stdout)
            assert data.get("valid") is False
            assert any("training_performed" in e for e in data.get("errors", []))
        finally:
            Path(summary_path).unlink(missing_ok=True)

    def test_rejects_adapter_generated_true(self) -> None:
        """Validator should reject adapter_generated=true."""
        bad_summary = {
            "job_id": "test-job-123",
            "status": "completed",
            "training_performed": False,
            "adapter_generated": True,
            "hf_upload_performed": False,
            "gate_state": "BLOCKED",
            "logs_sanitized": True,
        }
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(bad_summary, f)
            summary_path = f.name

        try:
            result = subprocess.run(
                [
                    sys.executable,
                    "training/scripts/validate_hf_jobs_smoke_summary.py",
                    "--summary",
                    summary_path,
                    "--json",
                ],
                capture_output=True,
                text=True,
                cwd=str(PROJECT_ROOT),
                timeout=30,
            )
            assert result.returncode != 0, "Should reject adapter_generated=true"
            data = json.loads(result.stdout)
            assert data.get("valid") is False
            assert any("adapter_generated" in e for e in data.get("errors", []))
        finally:
            Path(summary_path).unlink(missing_ok=True)

    def test_rejects_hf_upload_performed_true(self) -> None:
        """Validator should reject hf_upload_performed=true."""
        bad_summary = {
            "job_id": "test-job-123",
            "status": "completed",
            "training_performed": False,
            "adapter_generated": False,
            "hf_upload_performed": True,
            "gate_state": "BLOCKED",
            "logs_sanitized": True,
        }
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(bad_summary, f)
            summary_path = f.name

        try:
            result = subprocess.run(
                [
                    sys.executable,
                    "training/scripts/validate_hf_jobs_smoke_summary.py",
                    "--summary",
                    summary_path,
                    "--json",
                ],
                capture_output=True,
                text=True,
                cwd=str(PROJECT_ROOT),
                timeout=30,
            )
            assert result.returncode != 0, "Should reject hf_upload_performed=true"
            data = json.loads(result.stdout)
            assert data.get("valid") is False
            assert any("hf_upload_performed" in e for e in data.get("errors", []))
        finally:
            Path(summary_path).unlink(missing_ok=True)

    def test_rejects_token_like_strings(self) -> None:
        """Validator should reject token-like strings."""
        bad_summary = {
            "job_id": "test-job-123",
            "status": "pending",
            "training_performed": False,
            "adapter_generated": False,
            "hf_upload_performed": False,
            "gate_state": "BLOCKED",
            "logs_sanitized": True,
            "secret": "hf_abc123def456ghi789jkl012mno345pqr678",
        }
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(bad_summary, f)
            summary_path = f.name

        try:
            result = subprocess.run(
                [
                    sys.executable,
                    "training/scripts/validate_hf_jobs_smoke_summary.py",
                    "--summary",
                    summary_path,
                    "--json",
                ],
                capture_output=True,
                text=True,
                cwd=str(PROJECT_ROOT),
                timeout=30,
            )
            assert result.returncode != 0, "Should reject token-like strings"
            data = json.loads(result.stdout)
            assert data.get("valid") is False
        finally:
            Path(summary_path).unlink(missing_ok=True)


# ---------------------------------------------------------------------------
# hf_jobs_status stderr sanitization
# ---------------------------------------------------------------------------


class TestHFJobsStatusStderrV0131:
    """Test hf_jobs_status.py stderr sanitization."""

    def test_sanitize_stderr_code_exists(self) -> None:
        text = (PROJECT_ROOT / "training" / "scripts" / "hf_jobs_status.py").read_text()
        assert "safe_stderr" in text or "sanitize_line(result.stderr)" in text, "stderr sanitization code not found"

    def test_uses_tail_flag(self) -> None:
        """Verify that --tail is passed to the hf jobs logs subprocess command."""
        text = (PROJECT_ROOT / "training" / "scripts" / "hf_jobs_status.py").read_text()
        # Must find --tail in the actual subprocess command, not just argparse definition
        assert '"--tail", str(args.tail)' in text, "--tail flag not passed to hf jobs logs subprocess command"

    def test_sanitize_line_on_stderr(self) -> None:
        """Test that sanitize_line works on fake stderr content."""
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "hf_jobs_status",
            PROJECT_ROOT / "training" / "scripts" / "hf_jobs_status.py",
        )
        assert spec is not None
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)  # type: ignore[union-attr]

        result = module.sanitize_line("error: token=hf_abc123def456ghi789jkl012mno345pqr678")
        assert "[REDACTED]" in result
        assert "hf_abc123" not in result


# ---------------------------------------------------------------------------
# Smoke execution record
# ---------------------------------------------------------------------------


class TestSmokeExecutionRecordV0131:
    """Test smoke execution record doc and template."""

    def test_doc_exists(self) -> None:
        path = PROJECT_ROOT / "docs" / "HF_JOBS_SMOKE_EXECUTION_RECORD.md"
        assert path.exists(), "docs/HF_JOBS_SMOKE_EXECUTION_RECORD.md missing"

    def test_doc_mentions_pending(self) -> None:
        text = (PROJECT_ROOT / "docs" / "HF_JOBS_SMOKE_EXECUTION_RECORD.md").read_text()
        assert "pending" in text.lower()

    def test_doc_says_training_performed_false(self) -> None:
        text = (PROJECT_ROOT / "docs" / "HF_JOBS_SMOKE_EXECUTION_RECORD.md").read_text()
        assert "training_performed" in text
        assert "false" in text.lower()

    def test_doc_says_gate_blocked(self) -> None:
        text = (PROJECT_ROOT / "docs" / "HF_JOBS_SMOKE_EXECUTION_RECORD.md").read_text()
        assert "BLOCKED" in text

    def test_template_exists(self) -> None:
        path = PROJECT_ROOT / "training" / "templates" / "hf_jobs_smoke_execution_record.template.json"
        assert path.exists(), "hf_jobs_smoke_execution_record.template.json missing"

    def test_template_is_valid_json(self) -> None:
        path = PROJECT_ROOT / "training" / "templates" / "hf_jobs_smoke_execution_record.template.json"
        data = json.loads(path.read_text())
        assert data.get("training_performed") is False
        assert data.get("adapter_generated") is False
        assert data.get("hf_upload_performed") is False
        assert data.get("gate_state") == "BLOCKED"
        assert data.get("stderr_sanitized") is True


# ---------------------------------------------------------------------------
# Updated docs
# ---------------------------------------------------------------------------


class TestUpdatedDocsV0131:
    """Test updates to existing docs for v0.1.31."""

    def test_runbook_mentions_validate(self) -> None:
        text = (PROJECT_ROOT / "docs" / "HF_JOBS_SMOKE_RUNBOOK.md").read_text().lower()
        assert "validate_hf_jobs_smoke_summary" in text

    def test_runbook_mentions_smoke_must_pass(self) -> None:
        text = (PROJECT_ROOT / "docs" / "HF_JOBS_SMOKE_RUNBOOK.md").read_text().lower()
        assert "smoke must pass" in text or "before micro sft" in text

    def test_private_run_mentions_smoke_must_pass(self) -> None:
        text = (PROJECT_ROOT / "docs" / "HF_JOBS_PRIVATE_RUN.md").read_text().lower()
        assert "smoke must pass" in text or "before micro sft" in text

    def test_private_run_mentions_stderr_sanitization(self) -> None:
        text = (PROJECT_ROOT / "docs" / "HF_JOBS_PRIVATE_RUN.md").read_text().lower()
        assert "stderr" in text and "sanitize" in text

    def test_private_run_mentions_validate(self) -> None:
        text = (PROJECT_ROOT / "docs" / "HF_JOBS_PRIVATE_RUN.md").read_text().lower()
        assert "validate_hf_jobs_smoke_summary" in text

    def test_readme_mentions_smoke_execution(self) -> None:
        text = (PROJECT_ROOT / "README.md").read_text().lower()
        assert "smoke" in text and ("execution" in text or "validate" in text)

    def test_readme_version_0131(self) -> None:
        text = (PROJECT_ROOT / "README.md").read_text()
        assert "0.1.31" in text, "README must mention v0.1.31"

    def test_index_html_version_0131(self) -> None:
        text = (PROJECT_ROOT / "docs" / "index.html").read_text()
        assert "0.1.31" in text, "docs/index.html must mention v0.1.31"


# ---------------------------------------------------------------------------
# No tracked artifacts
# ---------------------------------------------------------------------------


class TestNoTrackedArtifactsV0131:
    """Ensure no weights/adapters/GGUF are tracked."""

    def test_no_gguf_tracked(self) -> None:
        result = subprocess.run(
            ["git", "ls-files", "*.gguf"],
            capture_output=True,
            text=True,
            cwd=str(PROJECT_ROOT),
            timeout=10,
        )
        gguf_files = [f for f in result.stdout.strip().splitlines() if f]
        assert len(gguf_files) == 0, f"GGUF files tracked: {gguf_files}"

    def test_no_safetensors_tracked(self) -> None:
        result = subprocess.run(
            ["git", "ls-files", "*.safetensors"],
            capture_output=True,
            text=True,
            cwd=str(PROJECT_ROOT),
            timeout=10,
        )
        files = [f for f in result.stdout.strip().splitlines() if f]
        assert len(files) == 0, f"Safetensors files tracked: {files}"

    def test_no_raw_log_files_tracked(self) -> None:
        """No raw log files should be tracked in git."""
        result = subprocess.run(
            ["git", "ls-files", "*.log", "training/raw_logs/*", "training/logs/*"],
            capture_output=True,
            text=True,
            cwd=str(PROJECT_ROOT),
            timeout=10,
        )
        files = [f for f in result.stdout.strip().splitlines() if f]
        assert len(files) == 0, f"Raw log files tracked: {files}"


# ---------------------------------------------------------------------------
# Gate
# ---------------------------------------------------------------------------


class TestGateV0131:
    """Test that the gate is still BLOCKED."""

    def test_smoke_config_gate_blocked(self) -> None:
        text = (PROJECT_ROOT / "training" / "configs" / "hf_jobs_kimari4b_smoke.v0.yaml").read_text()
        assert "BLOCKED" in text

    def test_execution_record_gate_blocked(self) -> None:
        text = (PROJECT_ROOT / "docs" / "HF_JOBS_SMOKE_EXECUTION_RECORD.md").read_text()
        assert "BLOCKED" in text

    def test_no_kimari_4b_released_claim(self) -> None:
        readme = (PROJECT_ROOT / "README.md").read_text().lower()
        false_patterns = [
            "kimari-4b is available now",
            "kimari-4b can be downloaded",
            "download kimari-4b",
            "kimari-4b weights available",
            "kimari-4b has been released",
        ]
        for pattern in false_patterns:
            assert pattern not in readme, f"False claim found: {pattern}"
