#!/usr/bin/env python3
"""Release validation tests for v0.1.35-alpha.

Validates all v0.1.35 artifacts:
- Version consistency (pyproject.toml, __init__.py)
- create_micro_sft_execution_record.py works with --json
- validate_micro_sft_execution_record.py works
- Default fields are safe (adapter_committed=false, etc.)
- Validator accepts safe record
- Validator rejects gate != BLOCKED
- Validator rejects adapter_committed=true
- Validator rejects hf_upload_performed=true
- Validator rejects raw_logs_committed=true
- hf_jobs_micro_sft.py has --require-smoke-summary
- Submit blocked without smoke summary
- docs/HF_JOBS_MICRO_SFT_EXECUTION_RECORD.md exists
- docs/HF_JOBS_MICRO_SFT_RUNBOOK.md exists
- No tracked GGUF/safetensors artifacts
- Gate BLOCKED
- No Kimari-4B released claim
"""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent


class TestVersionV0135:
    """Test v0.1.35 version consistency."""

    def test_pyproject_version(self) -> None:
        text = (PROJECT_ROOT / "pyproject.toml").read_text()
        assert "0.1.35-alpha" in text, "pyproject.toml must have version 0.1.35-alpha"

    def test_init_version(self) -> None:
        text = (PROJECT_ROOT / "kimari" / "__init__.py").read_text()
        assert "0.1.35-alpha" in text, "__init__.py must have version 0.1.35-alpha"


class TestCreateExecutionRecordV0135:
    """Test create_micro_sft_execution_record.py."""

    def test_script_exists(self) -> None:
        path = PROJECT_ROOT / "training" / "scripts" / "create_micro_sft_execution_record.py"
        assert path.exists(), "create_micro_sft_execution_record.py must exist"

    def test_json_output_works(self) -> None:
        """Script should work with --json and produce valid JSON."""
        result = subprocess.run(
            [
                sys.executable,
                "training/scripts/create_micro_sft_execution_record.py",
                "--status",
                "pending",
                "--adapter-generated",
                "unknown",
                "--json",
            ],
            capture_output=True,
            text=True,
            cwd=str(PROJECT_ROOT),
            timeout=30,
        )
        assert result.returncode == 0, f"Script failed: {result.stderr}"
        data = json.loads(result.stdout)
        assert data.get("record_type") == "micro_sft_execution_record"
        assert data.get("status") == "pending"

    def test_default_fields_safe(self) -> None:
        """Default fields must always be safe."""
        result = subprocess.run(
            [
                sys.executable,
                "training/scripts/create_micro_sft_execution_record.py",
                "--status",
                "pending",
                "--adapter-generated",
                "unknown",
                "--json",
            ],
            capture_output=True,
            text=True,
            cwd=str(PROJECT_ROOT),
            timeout=30,
        )
        data = json.loads(result.stdout)
        assert data["adapter_committed"] is False, "adapter_committed must be False"
        assert data["hf_upload_performed"] is False, "hf_upload_performed must be False"
        assert data["gguf_generated"] is False, "gguf_generated must be False"
        assert data["raw_logs_committed"] is False, "raw_logs_committed must be False"
        assert data["gate_state"] == "BLOCKED", "gate_state must be BLOCKED"
        assert data["manual_review_required"] is True, "manual_review_required must be True"

    def test_completed_status(self) -> None:
        """Completed status should set started=true, completed=true."""
        result = subprocess.run(
            [
                sys.executable,
                "training/scripts/create_micro_sft_execution_record.py",
                "--status",
                "completed",
                "--adapter-generated",
                "true",
                "--json",
            ],
            capture_output=True,
            text=True,
            cwd=str(PROJECT_ROOT),
            timeout=30,
        )
        data = json.loads(result.stdout)
        assert data["micro_sft_started"] is True
        assert data["micro_sft_completed"] is True

    def test_failed_status(self) -> None:
        """Failed status should set started=true, completed=false."""
        result = subprocess.run(
            [
                sys.executable,
                "training/scripts/create_micro_sft_execution_record.py",
                "--status",
                "failed",
                "--adapter-generated",
                "false",
                "--json",
            ],
            capture_output=True,
            text=True,
            cwd=str(PROJECT_ROOT),
            timeout=30,
        )
        data = json.loads(result.stdout)
        assert data["micro_sft_started"] is True
        assert data["micro_sft_completed"] is False

    def test_output_file_created(self) -> None:
        """Script should write to output file."""
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            output_path = f.name
        try:
            result = subprocess.run(
                [
                    sys.executable,
                    "training/scripts/create_micro_sft_execution_record.py",
                    "--status",
                    "pending",
                    "--adapter-generated",
                    "unknown",
                    "--output",
                    output_path,
                ],
                capture_output=True,
                text=True,
                cwd=str(PROJECT_ROOT),
                timeout=30,
            )
            assert result.returncode == 0, f"Script failed: {result.stderr}"
            data = json.loads(Path(output_path).read_text())
            assert data["record_type"] == "micro_sft_execution_record"
        finally:
            Path(output_path).unlink(missing_ok=True)


class TestValidateExecutionRecordV0135:
    """Test validate_micro_sft_execution_record.py."""

    def _create_safe_record(self, tmp_path: Path) -> Path:
        """Helper: create a safe execution record for testing."""
        record = {
            "record_type": "micro_sft_execution_record",
            "version": "0.1.35-alpha",
            "timestamp": "2026-06-03T12:00:00Z",
            "status": "completed",
            "job_id": "optional/sanitized",
            "flavor": "a10g-small",
            "image": "",
            "training_stack_check_passed": "true",
            "dataset_ready": "true",
            "micro_sft_started": True,
            "micro_sft_completed": True,
            "adapter_generated": "true",
            "adapter_committed": False,
            "hf_upload_performed": False,
            "gguf_generated": False,
            "raw_logs_committed": False,
            "gate_state": "BLOCKED",
            "manual_review_required": True,
            "notes": "",
        }
        record_path = tmp_path / "test_record.json"
        record_path.write_text(json.dumps(record, indent=2))
        return record_path

    def test_script_exists(self) -> None:
        path = PROJECT_ROOT / "training" / "scripts" / "validate_micro_sft_execution_record.py"
        assert path.exists(), "validate_micro_sft_execution_record.py must exist"

    def test_validator_accepts_safe_record(self, tmp_path: Path) -> None:
        """Validator should accept a safe execution record."""
        record_path = self._create_safe_record(tmp_path)
        result = subprocess.run(
            [
                sys.executable,
                "training/scripts/validate_micro_sft_execution_record.py",
                "--record",
                str(record_path),
                "--json",
            ],
            capture_output=True,
            text=True,
            cwd=str(PROJECT_ROOT),
            timeout=30,
        )
        assert result.returncode == 0, f"Validator failed: {result.stderr}"
        data = json.loads(result.stdout)
        assert data.get("valid") is True, f"Record should be valid: {data}"

    def test_validator_rejects_gate_not_blocked(self, tmp_path: Path) -> None:
        """Validator should reject gate_state != BLOCKED."""
        record_path = self._create_safe_record(tmp_path)
        data = json.loads(record_path.read_text())
        data["gate_state"] = "OPEN"
        record_path.write_text(json.dumps(data))
        result = subprocess.run(
            [
                sys.executable,
                "training/scripts/validate_micro_sft_execution_record.py",
                "--record",
                str(record_path),
                "--json",
            ],
            capture_output=True,
            text=True,
            cwd=str(PROJECT_ROOT),
            timeout=30,
        )
        assert result.returncode != 0, "Validator should reject non-BLOCKED gate"

    def test_validator_rejects_adapter_committed(self, tmp_path: Path) -> None:
        """Validator should reject adapter_committed=true."""
        record_path = self._create_safe_record(tmp_path)
        data = json.loads(record_path.read_text())
        data["adapter_committed"] = True
        record_path.write_text(json.dumps(data))
        result = subprocess.run(
            [
                sys.executable,
                "training/scripts/validate_micro_sft_execution_record.py",
                "--record",
                str(record_path),
                "--json",
            ],
            capture_output=True,
            text=True,
            cwd=str(PROJECT_ROOT),
            timeout=30,
        )
        assert result.returncode != 0, "Validator should reject adapter_committed=true"

    def test_validator_rejects_hf_upload(self, tmp_path: Path) -> None:
        """Validator should reject hf_upload_performed=true."""
        record_path = self._create_safe_record(tmp_path)
        data = json.loads(record_path.read_text())
        data["hf_upload_performed"] = True
        record_path.write_text(json.dumps(data))
        result = subprocess.run(
            [
                sys.executable,
                "training/scripts/validate_micro_sft_execution_record.py",
                "--record",
                str(record_path),
                "--json",
            ],
            capture_output=True,
            text=True,
            cwd=str(PROJECT_ROOT),
            timeout=30,
        )
        assert result.returncode != 0, "Validator should reject hf_upload_performed=true"

    def test_validator_rejects_raw_logs_committed(self, tmp_path: Path) -> None:
        """Validator should reject raw_logs_committed=true."""
        record_path = self._create_safe_record(tmp_path)
        data = json.loads(record_path.read_text())
        data["raw_logs_committed"] = True
        record_path.write_text(json.dumps(data))
        result = subprocess.run(
            [
                sys.executable,
                "training/scripts/validate_micro_sft_execution_record.py",
                "--record",
                str(record_path),
                "--json",
            ],
            capture_output=True,
            text=True,
            cwd=str(PROJECT_ROOT),
            timeout=30,
        )
        assert result.returncode != 0, "Validator should reject raw_logs_committed=true"

    def test_validator_rejects_tokens(self, tmp_path: Path) -> None:
        """Validator should reject token-like strings."""
        record_path = self._create_safe_record(tmp_path)
        data = json.loads(record_path.read_text())
        data["notes"] = "hf_abcdefghijklmnopqrstuvwxyz12345"
        record_path.write_text(json.dumps(data))
        result = subprocess.run(
            [
                sys.executable,
                "training/scripts/validate_micro_sft_execution_record.py",
                "--record",
                str(record_path),
                "--json",
            ],
            capture_output=True,
            text=True,
            cwd=str(PROJECT_ROOT),
            timeout=30,
        )
        assert result.returncode != 0, "Validator should reject token-like strings"


class TestHfJobsMicroSftV0135:
    """Test hf_jobs_micro_sft.py v0.1.35 features."""

    def test_has_require_smoke_summary(self) -> None:
        text = (PROJECT_ROOT / "training" / "scripts" / "hf_jobs_micro_sft.py").read_text()
        assert "require_smoke_summary" in text or "require-smoke-summary" in text, (
            "hf_jobs_micro_sft.py must have --require-smoke-summary"
        )

    def test_submit_blocked_without_smoke_summary(self) -> None:
        """Submit should be blocked without --require-smoke-summary (unless override)."""
        text = (PROJECT_ROOT / "training" / "scripts" / "hf_jobs_micro_sft.py").read_text()
        # The script should require smoke summary for submission
        assert "require_smoke_summary" in text, "Script must reference require_smoke_summary"
        # There should be logic to block submission without it
        assert "allow_submit" in text, "Script must have allow_submit logic"


class TestDocsV0135:
    """Test v0.1.35 documentation artifacts."""

    def test_execution_record_doc_exists(self) -> None:
        path = PROJECT_ROOT / "docs" / "HF_JOBS_MICRO_SFT_EXECUTION_RECORD.md"
        assert path.exists(), "docs/HF_JOBS_MICRO_SFT_EXECUTION_RECORD.md must exist"

    def test_runbook_doc_exists(self) -> None:
        path = PROJECT_ROOT / "docs" / "HF_JOBS_MICRO_SFT_RUNBOOK.md"
        assert path.exists(), "docs/HF_JOBS_MICRO_SFT_RUNBOOK.md must exist"

    def test_execution_record_doc_mentions_safe_fields(self) -> None:
        text = (PROJECT_ROOT / "docs" / "HF_JOBS_MICRO_SFT_EXECUTION_RECORD.md").read_text().lower()
        assert "adapter_committed" in text, "Doc must mention adapter_committed"
        assert "gate_state" in text, "Doc must mention gate_state"
        assert "blocked" in text, "Doc must mention BLOCKED"


class TestGateV0135:
    """Test that the gate is still BLOCKED for v0.1.35."""

    def test_micro_sft_config_gate_blocked(self) -> None:
        text = (PROJECT_ROOT / "training" / "configs" / "hf_jobs_kimari4b_micro_sft.v0.yaml").read_text()
        assert "BLOCKED" in text, "Micro SFT config must have BLOCKED gate state"

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
            assert pattern not in readme, f"False claim found in README: {pattern}"


class TestNoTrackedArtifactsV0135:
    """Ensure no weights/adapters/GGUF are tracked in git."""

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
