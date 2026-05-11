"""Release validation tests for v0.1.30-alpha.

Validates all v0.1.30 artifacts:
- create_hf_jobs_smoke_summary.py
- Smoke summary has training_performed=false, gate BLOCKED
- hf_jobs_status.py --sanitize-logs
- Smoke result doc exists
- Smoke runbook exists
- No false claims
- Gate BLOCKED
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent


# ---------------------------------------------------------------------------
# Version
# ---------------------------------------------------------------------------


class TestVersionV0130:
    """Test v0.1.30 version consistency."""

    def test_pyproject_version(self) -> None:
        text = (PROJECT_ROOT / "pyproject.toml").read_text()
        assert "0.1.30-alpha" in text, "pyproject.toml must have version 0.1.30-alpha"

    def test_init_version(self) -> None:
        text = (PROJECT_ROOT / "kimari" / "__init__.py").read_text()
        assert "0.1.30-alpha" in text, "__init__.py must have version 0.1.30-alpha"


# ---------------------------------------------------------------------------
# create_hf_jobs_smoke_summary
# ---------------------------------------------------------------------------


class TestCreateSmokeSummaryV0130:
    """Test create_hf_jobs_smoke_summary.py."""

    def test_script_exists(self) -> None:
        path = PROJECT_ROOT / "training" / "scripts" / "create_hf_jobs_smoke_summary.py"
        assert path.exists(), "create_hf_jobs_smoke_summary.py missing"

    def test_pending_summary_json(self) -> None:
        result = subprocess.run(
            [
                sys.executable,
                "training/scripts/create_hf_jobs_smoke_summary.py",
                "--status",
                "pending",
                "--flavor",
                "a10g-small",
                "--image",
                "pytorch/pytorch:2.6.0-cuda12.4-cudnn9-devel",
                "--json",
            ],
            capture_output=True,
            text=True,
            cwd=str(PROJECT_ROOT),
            timeout=30,
        )
        assert result.returncode == 0, f"Smoke summary failed: {result.stderr}"
        data = json.loads(result.stdout)
        assert data.get("status") == "pending"
        assert data.get("training_performed") is False
        assert data.get("adapter_generated") is False
        assert data.get("hf_upload_performed") is False
        assert data.get("gate_state") == "BLOCKED"
        assert data.get("flavor") == "a10g-small"

    def test_completed_summary_json(self) -> None:
        result = subprocess.run(
            [
                sys.executable,
                "training/scripts/create_hf_jobs_smoke_summary.py",
                "--job-id",
                "test-job-123",
                "--status",
                "completed",
                "--flavor",
                "a10g-small",
                "--image",
                "pytorch/pytorch:2.6.0-cuda12.4-cudnn9-devel",
                "--gpu-detected",
                "--torch-cuda",
                "--repo-installed",
                "--dataset-dryrun",
                "--sft-dryrun",
                "--json",
            ],
            capture_output=True,
            text=True,
            cwd=str(PROJECT_ROOT),
            timeout=30,
        )
        assert result.returncode == 0, f"Completed summary failed: {result.stderr}"
        data = json.loads(result.stdout)
        assert data.get("status") == "completed"
        assert data.get("job_id") == "test-job-123"
        assert data.get("gpu_detected") is True
        assert data.get("torch_cuda_available") is True
        assert data.get("repo_installed") is True
        assert data.get("dataset_dryrun_passed") is True
        assert data.get("sft_dryrun_passed") is True
        # These must always be false regardless of status
        assert data.get("training_performed") is False
        assert data.get("adapter_generated") is False
        assert data.get("hf_upload_performed") is False
        assert data.get("gate_state") == "BLOCKED"
        assert data.get("logs_sanitized") is True

    def test_output_to_file(self, tmp_path: Path) -> None:
        output_path = tmp_path / "smoke_summary.json"
        result = subprocess.run(
            [
                sys.executable,
                "training/scripts/create_hf_jobs_smoke_summary.py",
                "--status",
                "pending",
                "--flavor",
                "a10g-small",
                "--image",
                "pytorch/pytorch:2.6.0-cuda12.4-cudnn9-devel",
                "--output",
                str(output_path),
                "--json",
            ],
            capture_output=True,
            text=True,
            cwd=str(PROJECT_ROOT),
            timeout=30,
        )
        assert result.returncode == 0
        assert output_path.exists()
        data = json.loads(output_path.read_text())
        assert data.get("status") == "pending"

    def test_no_tokens_in_output(self) -> None:
        result = subprocess.run(
            [
                sys.executable,
                "training/scripts/create_hf_jobs_smoke_summary.py",
                "--status",
                "pending",
                "--flavor",
                "a10g-small",
                "--image",
                "pytorch/pytorch:2.6.0-cuda12.4-cudnn9-devel",
                "--json",
            ],
            capture_output=True,
            text=True,
            cwd=str(PROJECT_ROOT),
            timeout=30,
        )
        assert result.returncode == 0
        # Check no token patterns in output
        output = result.stdout
        assert "hf_" not in output or "NOT_AVAILABLE" in output, "No HF tokens in summary output"
        assert "api_key" not in output.lower() or "no api_key" in output.lower(), "No API keys in summary output"

    def test_training_performed_always_false(self) -> None:
        """Even with completed status, training_performed must be false."""
        result = subprocess.run(
            [
                sys.executable,
                "training/scripts/create_hf_jobs_smoke_summary.py",
                "--status",
                "completed",
                "--flavor",
                "a10g-small",
                "--image",
                "pytorch/pytorch:2.6.0-cuda12.4-cudnn9-devel",
                "--json",
            ],
            capture_output=True,
            text=True,
            cwd=str(PROJECT_ROOT),
            timeout=30,
        )
        data = json.loads(result.stdout)
        assert data.get("training_performed") is False, "training_performed must always be false in v0.1.30"

    def test_adapter_generated_always_false(self) -> None:
        result = subprocess.run(
            [
                sys.executable,
                "training/scripts/create_hf_jobs_smoke_summary.py",
                "--status",
                "completed",
                "--flavor",
                "a10g-small",
                "--image",
                "pytorch/pytorch:2.6.0-cuda12.4-cudnn9-devel",
                "--json",
            ],
            capture_output=True,
            text=True,
            cwd=str(PROJECT_ROOT),
            timeout=30,
        )
        data = json.loads(result.stdout)
        assert data.get("adapter_generated") is False, "adapter_generated must always be false in v0.1.30"

    def test_hf_upload_performed_always_false(self) -> None:
        result = subprocess.run(
            [
                sys.executable,
                "training/scripts/create_hf_jobs_smoke_summary.py",
                "--status",
                "completed",
                "--flavor",
                "a10g-small",
                "--image",
                "pytorch/pytorch:2.6.0-cuda12.4-cudnn9-devel",
                "--json",
            ],
            capture_output=True,
            text=True,
            cwd=str(PROJECT_ROOT),
            timeout=30,
        )
        data = json.loads(result.stdout)
        assert data.get("hf_upload_performed") is False, "hf_upload_performed must always be false in v0.1.30"

    def test_gate_state_always_blocked(self) -> None:
        result = subprocess.run(
            [
                sys.executable,
                "training/scripts/create_hf_jobs_smoke_summary.py",
                "--status",
                "completed",
                "--flavor",
                "a10g-small",
                "--image",
                "pytorch/pytorch:2.6.0-cuda12.4-cudnn9-devel",
                "--json",
            ],
            capture_output=True,
            text=True,
            cwd=str(PROJECT_ROOT),
            timeout=30,
        )
        data = json.loads(result.stdout)
        assert data.get("gate_state") == "BLOCKED", "gate_state must always be BLOCKED"


# ---------------------------------------------------------------------------
# hf_jobs_status --sanitize-logs
# ---------------------------------------------------------------------------


class TestHFJobsStatusSanitizeV0130:
    """Test hf_jobs_status.py --sanitize-logs."""

    def test_sanitize_logs_flag_exists(self) -> None:
        text = (PROJECT_ROOT / "training" / "scripts" / "hf_jobs_status.py").read_text()
        assert "--sanitize-logs" in text, "--sanitize-logs flag not found in hf_jobs_status.py"

    def test_sanitize_line_function_exists(self) -> None:
        text = (PROJECT_ROOT / "training" / "scripts" / "hf_jobs_status.py").read_text()
        assert "sanitize_line" in text, "sanitize_line function not found in hf_jobs_status.py"

    def test_sanitize_patterns_defined(self) -> None:
        text = (PROJECT_ROOT / "training" / "scripts" / "hf_jobs_status.py").read_text()
        assert "SANITIZE_PATTERNS" in text, "SANITIZE_PATTERNS not defined in hf_jobs_status.py"

    def test_sanitizes_fake_token(self) -> None:
        """Test that sanitize_line removes fake HF token patterns."""
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "hf_jobs_status",
            PROJECT_ROOT / "training" / "scripts" / "hf_jobs_status.py",
        )
        assert spec is not None
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)  # type: ignore[union-attr]

        # Test HF token pattern
        assert "[REDACTED]" in module.sanitize_line("hf_abc123def456ghi789jkl012mno345")
        # Test that normal text passes through
        assert "nvidia-smi" in module.sanitize_line("nvidia-smi output")
        assert "torch.cuda" in module.sanitize_line("torch.cuda.is_available()")

    def test_sanitizes_api_key_pattern(self) -> None:
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "hf_jobs_status",
            PROJECT_ROOT / "training" / "scripts" / "hf_jobs_status.py",
        )
        assert spec is not None
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)  # type: ignore[union-attr]

        result = module.sanitize_line('api_key = "test_fake_key_abcdefghijklmnopqrstuvwxyz123456"')
        assert "[REDACTED]" in result

    def test_sanitizes_authorization_header(self) -> None:
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "hf_jobs_status",
            PROJECT_ROOT / "training" / "scripts" / "hf_jobs_status.py",
        )
        assert spec is not None
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)  # type: ignore[union-attr]

        result = module.sanitize_line("Authorization: Bearer hf_abc123def456ghi789jkl012mno345pqr678")
        assert "[REDACTED]" in result


# ---------------------------------------------------------------------------
# Smoke result doc
# ---------------------------------------------------------------------------


class TestSmokeResultDocV0130:
    """Test HF_JOBS_SMOKE_RESULT.md."""

    def test_doc_exists(self) -> None:
        path = PROJECT_ROOT / "docs" / "HF_JOBS_SMOKE_RESULT.md"
        assert path.exists(), "docs/HF_JOBS_SMOKE_RESULT.md missing"

    def test_doc_mentions_pending(self) -> None:
        text = (PROJECT_ROOT / "docs" / "HF_JOBS_SMOKE_RESULT.md").read_text()
        assert "pending" in text.lower()

    def test_doc_says_training_performed_false(self) -> None:
        text = (PROJECT_ROOT / "docs" / "HF_JOBS_SMOKE_RESULT.md").read_text()
        assert "training_performed" in text
        assert "false" in text.lower()

    def test_doc_says_gate_blocked(self) -> None:
        text = (PROJECT_ROOT / "docs" / "HF_JOBS_SMOKE_RESULT.md").read_text()
        assert "BLOCKED" in text

    def test_doc_mentions_create_summary(self) -> None:
        text = (PROJECT_ROOT / "docs" / "HF_JOBS_SMOKE_RESULT.md").read_text()
        assert "create_hf_jobs_smoke_summary" in text or "smoke summary" in text.lower()


# ---------------------------------------------------------------------------
# Smoke runbook
# ---------------------------------------------------------------------------


class TestSmokeRunbookV0130:
    """Test HF_JOBS_SMOKE_RUNBOOK.md."""

    def test_runbook_exists(self) -> None:
        path = PROJECT_ROOT / "docs" / "HF_JOBS_SMOKE_RUNBOOK.md"
        assert path.exists(), "docs/HF_JOBS_SMOKE_RUNBOOK.md missing"

    def test_runbook_has_login_step(self) -> None:
        text = (PROJECT_ROOT / "docs" / "HF_JOBS_SMOKE_RUNBOOK.md").read_text()
        assert "login" in text.lower() or "auth" in text.lower()

    def test_runbook_has_sanitize_step(self) -> None:
        text = (PROJECT_ROOT / "docs" / "HF_JOBS_SMOKE_RUNBOOK.md").read_text()
        assert "sanitize" in text.lower() or "sanitiz" in text.lower()

    def test_runbook_has_scan_secrets_step(self) -> None:
        text = (PROJECT_ROOT / "docs" / "HF_JOBS_SMOKE_RUNBOOK.md").read_text()
        assert "scan_for_secrets" in text or "scan for secrets" in text.lower()

    def test_runbook_mentions_blocked(self) -> None:
        text = (PROJECT_ROOT / "docs" / "HF_JOBS_SMOKE_RUNBOOK.md").read_text()
        assert "BLOCKED" in text

    def test_runbook_no_training(self) -> None:
        text = (PROJECT_ROOT / "docs" / "HF_JOBS_SMOKE_RUNBOOK.md").read_text().lower()
        assert "no training" in text or "not train" in text or "training_performed" in text


# ---------------------------------------------------------------------------
# Updated docs
# ---------------------------------------------------------------------------


class TestUpdatedDocsV0130:
    """Test updates to existing docs for v0.1.30."""

    def test_hf_jobs_private_run_mentions_smoke_result(self) -> None:
        text = (PROJECT_ROOT / "docs" / "HF_JOBS_PRIVATE_RUN.md").read_text().lower()
        assert "create_hf_jobs_smoke_summary" in text or "smoke result" in text or "smoke summary" in text

    def test_hf_jobs_private_run_mentions_sanitization(self) -> None:
        text = (PROJECT_ROOT / "docs" / "HF_JOBS_PRIVATE_RUN.md").read_text().lower()
        assert "sanitize" in text

    def test_readme_mentions_smoke_test_status(self) -> None:
        text = (PROJECT_ROOT / "README.md").read_text()
        assert "smoke" in text.lower() and ("result" in text.lower() or "status" in text.lower())

    def test_readme_version_0130(self) -> None:
        text = (PROJECT_ROOT / "README.md").read_text()
        assert "0.1.30" in text, "README must mention v0.1.30"

    def test_index_html_version_0130(self) -> None:
        text = (PROJECT_ROOT / "docs" / "index.html").read_text()
        assert "0.1.30" in text, "docs/index.html must mention v0.1.30"


# ---------------------------------------------------------------------------
# No tracked artifacts
# ---------------------------------------------------------------------------


class TestNoTrackedArtifactsV0130:
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


# ---------------------------------------------------------------------------
# Gate
# ---------------------------------------------------------------------------


class TestGateV0130:
    """Test that the gate is still BLOCKED."""

    def test_smoke_config_gate_blocked(self) -> None:
        text = (PROJECT_ROOT / "training" / "configs" / "hf_jobs_kimari4b_smoke.v0.yaml").read_text()
        assert "BLOCKED" in text

    def test_smoke_result_doc_gate_blocked(self) -> None:
        text = (PROJECT_ROOT / "docs" / "HF_JOBS_SMOKE_RESULT.md").read_text()
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
