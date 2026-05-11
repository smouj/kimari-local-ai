"""Release validation tests for v0.1.32-alpha.

Validates all v0.1.32 artifacts:
- Micro SFT config (allow_training=true, allow_hf_upload=false, gate BLOCKED)
- hf_jobs_micro_sft.py (--dry-run, --print-command, no --token, requires --allow-submit --yes)
- create_hf_jobs_micro_sft_summary.py
- validate_hf_jobs_micro_sft_summary.py
- Micro SFT docs and templates
- No tracked artifacts
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


class TestVersionV0132:
    """Test v0.1.32 version consistency."""

    def test_pyproject_version(self) -> None:
        text = (PROJECT_ROOT / "pyproject.toml").read_text()
        assert "0.1.32-alpha" in text, "pyproject.toml must have version 0.1.32-alpha"

    def test_init_version(self) -> None:
        text = (PROJECT_ROOT / "kimari" / "__init__.py").read_text()
        assert "0.1.32-alpha" in text, "__init__.py must have version 0.1.32-alpha"


# ---------------------------------------------------------------------------
# Micro SFT config
# ---------------------------------------------------------------------------


class TestMicroSFTConfigV0132:
    """Test micro SFT config safety constraints."""

    def _parse_yaml_simple(self, path: Path) -> dict:
        """Parse a simple YAML file without PyYAML dependency."""
        data: dict = {}
        current_list_key: str | None = None
        current_list: list = []
        for line in path.read_text().splitlines():
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue
            if line.startswith("  - ") and current_list_key:
                current_list.append(stripped[2:])
                continue
            if current_list_key and current_list:
                data[current_list_key] = current_list
                current_list = []
                current_list_key = None
            if ":" in stripped and not stripped.startswith("-"):
                key, _, value = stripped.partition(":")
                key = key.strip()
                value = value.strip()
                if value == "":
                    current_list_key = key
                    current_list = []
                    continue
                if value.lower() == "true":
                    data[key] = True
                elif value.lower() == "false":
                    data[key] = False
                elif value.lower() == "null":
                    data[key] = None
                else:
                    try:
                        data[key] = int(value)
                    except ValueError:
                        try:
                            data[key] = float(value)
                        except ValueError:
                            data[key] = value.strip("\"'")
        if current_list_key and current_list:
            data[current_list_key] = current_list
        return data

    def test_config_exists(self) -> None:
        path = PROJECT_ROOT / "training" / "configs" / "hf_jobs_kimari4b_micro_sft.v0.yaml"
        assert path.exists(), "Micro SFT config missing"

    def test_config_parses(self) -> None:
        path = PROJECT_ROOT / "training" / "configs" / "hf_jobs_kimari4b_micro_sft.v0.yaml"
        config = self._parse_yaml_simple(path)
        assert config.get("job_name") == "kimari4b-micro-sft-v0"

    def test_allow_training_true(self) -> None:
        path = PROJECT_ROOT / "training" / "configs" / "hf_jobs_kimari4b_micro_sft.v0.yaml"
        config = self._parse_yaml_simple(path)
        assert config.get("allow_training") is True, "allow_training must be true for micro SFT"

    def test_allow_hf_upload_false(self) -> None:
        path = PROJECT_ROOT / "training" / "configs" / "hf_jobs_kimari4b_micro_sft.v0.yaml"
        config = self._parse_yaml_simple(path)
        assert config.get("allow_hf_upload") is False, "allow_hf_upload must be false"

    def test_preview_gate_state_blocked(self) -> None:
        path = PROJECT_ROOT / "training" / "configs" / "hf_jobs_kimari4b_micro_sft.v0.yaml"
        config = self._parse_yaml_simple(path)
        assert config.get("preview_gate_state") == "BLOCKED", "preview_gate_state must be BLOCKED"

    def test_base_model_smollm3(self) -> None:
        path = PROJECT_ROOT / "training" / "configs" / "hf_jobs_kimari4b_micro_sft.v0.yaml"
        config = self._parse_yaml_simple(path)
        assert "SmolLM3-3B" in config.get("base_model", ""), "base_model must be SmolLM3-3B"


# ---------------------------------------------------------------------------
# hf_jobs_micro_sft.py wrapper
# ---------------------------------------------------------------------------


class TestMicroSFTWrapperV0132:
    """Test hf_jobs_micro_sft.py wrapper."""

    def test_script_exists(self) -> None:
        path = PROJECT_ROOT / "training" / "scripts" / "hf_jobs_micro_sft.py"
        assert path.exists(), "hf_jobs_micro_sft.py missing"

    def test_dry_run_works(self) -> None:
        result = subprocess.run(
            [
                sys.executable,
                "training/scripts/hf_jobs_micro_sft.py",
                "--config",
                "training/configs/hf_jobs_kimari4b_micro_sft.v0.yaml",
                "--dry-run",
                "--json",
            ],
            capture_output=True,
            text=True,
            cwd=str(PROJECT_ROOT),
            timeout=30,
        )
        assert result.returncode == 0, f"dry-run failed: {result.stderr}"
        data = json.loads(result.stdout)
        assert data.get("mode") == "dry-run"
        assert data.get("job_name") == "kimari4b-micro-sft-v0"

    def test_print_command_works(self) -> None:
        result = subprocess.run(
            [
                sys.executable,
                "training/scripts/hf_jobs_micro_sft.py",
                "--config",
                "training/configs/hf_jobs_kimari4b_micro_sft.v0.yaml",
                "--print-command",
                "--json",
            ],
            capture_output=True,
            text=True,
            cwd=str(PROJECT_ROOT),
            timeout=30,
        )
        assert result.returncode == 0, f"print-command failed: {result.stderr}"
        data = json.loads(result.stdout)
        assert "hf_command" in data

    def test_refuses_submit_without_flags(self) -> None:
        result = subprocess.run(
            [
                sys.executable,
                "training/scripts/hf_jobs_micro_sft.py",
                "--config",
                "training/configs/hf_jobs_kimari4b_micro_sft.v0.yaml",
                "--json",
            ],
            capture_output=True,
            text=True,
            cwd=str(PROJECT_ROOT),
            timeout=30,
        )
        assert result.returncode != 0, "Should refuse submit without --allow-submit --yes"

    def test_no_token_argument(self) -> None:
        """Wrapper must not accept --token."""
        text = (PROJECT_ROOT / "training" / "scripts" / "hf_jobs_micro_sft.py").read_text()
        assert '"--token"' not in text, "hf_jobs_micro_sft.py must not have --token argument"

    def test_has_override_smoke_gate(self) -> None:
        text = (PROJECT_ROOT / "training" / "scripts" / "hf_jobs_micro_sft.py").read_text()
        assert "override_smoke_gate" in text, "Must have --override-smoke-gate option"


# ---------------------------------------------------------------------------
# create_hf_jobs_micro_sft_summary
# ---------------------------------------------------------------------------


class TestCreateMicroSFTSummaryV0132:
    """Test create_hf_jobs_micro_sft_summary.py."""

    def test_script_exists(self) -> None:
        path = PROJECT_ROOT / "training" / "scripts" / "create_hf_jobs_micro_sft_summary.py"
        assert path.exists(), "create_hf_jobs_micro_sft_summary.py missing"

    def test_generates_pending_summary(self) -> None:
        result = subprocess.run(
            [
                sys.executable,
                "training/scripts/create_hf_jobs_micro_sft_summary.py",
                "--status",
                "pending",
                "--json",
            ],
            capture_output=True,
            text=True,
            cwd=str(PROJECT_ROOT),
            timeout=30,
        )
        assert result.returncode == 0, f"Summary generation failed: {result.stderr}"
        data = json.loads(result.stdout)
        assert data.get("status") == "pending"
        assert data.get("adapter_committed") is False
        assert data.get("hf_upload_performed") is False
        assert data.get("gate_state") == "BLOCKED"
        assert data.get("manual_review_required") is True

    def test_generates_to_file(self) -> None:
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            summary_path = f.name

        try:
            result = subprocess.run(
                [
                    sys.executable,
                    "training/scripts/create_hf_jobs_micro_sft_summary.py",
                    "--status",
                    "pending",
                    "--output",
                    summary_path,
                    "--json",
                ],
                capture_output=True,
                text=True,
                cwd=str(PROJECT_ROOT),
                timeout=30,
            )
            assert result.returncode == 0
            data = json.loads(Path(summary_path).read_text())
            assert data.get("gate_state") == "BLOCKED"
        finally:
            Path(summary_path).unlink(missing_ok=True)


# ---------------------------------------------------------------------------
# validate_hf_jobs_micro_sft_summary
# ---------------------------------------------------------------------------


class TestValidateMicroSFTSummaryV0132:
    """Test validate_hf_jobs_micro_sft_summary.py."""

    def test_script_exists(self) -> None:
        path = PROJECT_ROOT / "training" / "scripts" / "validate_hf_jobs_micro_sft_summary.py"
        assert path.exists(), "validate_hf_jobs_micro_sft_summary.py missing"

    def test_accepts_safe_summary(self) -> None:
        safe_summary = {
            "job_id": "test-job-123",
            "status": "pending",
            "training_performed": True,
            "adapter_generated": "unknown",
            "adapter_committed": False,
            "hf_upload_performed": False,
            "gguf_generated": False,
            "raw_logs_committed": False,
            "gate_state": "BLOCKED",
            "manual_review_required": True,
        }
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(safe_summary, f)
            summary_path = f.name

        try:
            result = subprocess.run(
                [
                    sys.executable,
                    "training/scripts/validate_hf_jobs_micro_sft_summary.py",
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
            assert data.get("valid") is True
        finally:
            Path(summary_path).unlink(missing_ok=True)

    def test_rejects_hf_upload_performed_true(self) -> None:
        bad_summary = {
            "job_id": "test-job-123",
            "status": "completed",
            "adapter_committed": False,
            "hf_upload_performed": True,
            "gguf_generated": False,
            "raw_logs_committed": False,
            "gate_state": "BLOCKED",
            "manual_review_required": True,
        }
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(bad_summary, f)
            summary_path = f.name

        try:
            result = subprocess.run(
                [
                    sys.executable,
                    "training/scripts/validate_hf_jobs_micro_sft_summary.py",
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
        finally:
            Path(summary_path).unlink(missing_ok=True)

    def test_rejects_adapter_committed_true(self) -> None:
        bad_summary = {
            "job_id": "test-job-123",
            "status": "completed",
            "adapter_committed": True,
            "hf_upload_performed": False,
            "gguf_generated": False,
            "raw_logs_committed": False,
            "gate_state": "BLOCKED",
            "manual_review_required": True,
        }
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(bad_summary, f)
            summary_path = f.name

        try:
            result = subprocess.run(
                [
                    sys.executable,
                    "training/scripts/validate_hf_jobs_micro_sft_summary.py",
                    "--summary",
                    summary_path,
                    "--json",
                ],
                capture_output=True,
                text=True,
                cwd=str(PROJECT_ROOT),
                timeout=30,
            )
            assert result.returncode != 0, "Should reject adapter_committed=true"
            data = json.loads(result.stdout)
            assert data.get("valid") is False
        finally:
            Path(summary_path).unlink(missing_ok=True)

    def test_rejects_gate_not_blocked(self) -> None:
        bad_summary = {
            "job_id": "test-job-123",
            "status": "completed",
            "adapter_committed": False,
            "hf_upload_performed": False,
            "gguf_generated": False,
            "raw_logs_committed": False,
            "gate_state": "APPROVED",
            "manual_review_required": True,
        }
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(bad_summary, f)
            summary_path = f.name

        try:
            result = subprocess.run(
                [
                    sys.executable,
                    "training/scripts/validate_hf_jobs_micro_sft_summary.py",
                    "--summary",
                    summary_path,
                    "--json",
                ],
                capture_output=True,
                text=True,
                cwd=str(PROJECT_ROOT),
                timeout=30,
            )
            assert result.returncode != 0, "Should reject gate_state != BLOCKED"
            data = json.loads(result.stdout)
            assert data.get("valid") is False
        finally:
            Path(summary_path).unlink(missing_ok=True)


# ---------------------------------------------------------------------------
# Micro SFT docs and templates
# ---------------------------------------------------------------------------


class TestMicroSFTDocsV0132:
    """Test micro SFT documentation and templates."""

    def test_micro_sft_run_doc_exists(self) -> None:
        path = PROJECT_ROOT / "docs" / "HF_JOBS_MICRO_SFT_RUN.md"
        assert path.exists(), "docs/HF_JOBS_MICRO_SFT_RUN.md missing"

    def test_micro_sft_result_doc_exists(self) -> None:
        path = PROJECT_ROOT / "docs" / "HF_JOBS_MICRO_SFT_RESULT.md"
        assert path.exists(), "docs/HF_JOBS_MICRO_SFT_RESULT.md missing"

    def test_result_doc_says_pending(self) -> None:
        text = (PROJECT_ROOT / "docs" / "HF_JOBS_MICRO_SFT_RESULT.md").read_text()
        assert "pending" in text.lower()

    def test_result_doc_says_gate_blocked(self) -> None:
        text = (PROJECT_ROOT / "docs" / "HF_JOBS_MICRO_SFT_RESULT.md").read_text()
        assert "BLOCKED" in text

    def test_template_exists(self) -> None:
        path = PROJECT_ROOT / "training" / "templates" / "hf_jobs_micro_sft_summary.template.json"
        assert path.exists(), "hf_jobs_micro_sft_summary.template.json missing"

    def test_template_is_valid_json(self) -> None:
        path = PROJECT_ROOT / "training" / "templates" / "hf_jobs_micro_sft_summary.template.json"
        data = json.loads(path.read_text())
        assert data.get("adapter_committed") is False
        assert data.get("hf_upload_performed") is False
        assert data.get("gguf_generated") is False
        assert data.get("gate_state") == "BLOCKED"
        assert data.get("manual_review_required") is True

    def test_runbook_mentions_micro_sft(self) -> None:
        text = (PROJECT_ROOT / "docs" / "HF_JOBS_SMOKE_RUNBOOK.md").read_text().lower()
        assert "micro sft" in text, "Runbook must mention micro SFT"


# ---------------------------------------------------------------------------
# Updated docs
# ---------------------------------------------------------------------------


class TestUpdatedDocsV0132:
    """Test updates to existing docs for v0.1.32."""

    def test_private_run_mentions_micro_sft(self) -> None:
        text = (PROJECT_ROOT / "docs" / "KIMARI4B_PRIVATE_SFT_RUN.md").read_text().lower()
        assert "micro sft" in text, "PRIVATE_SFT_RUN must mention micro SFT"

    def test_checklist_mentions_micro_sft(self) -> None:
        text = (PROJECT_ROOT / "docs" / "KIMARI4B_FIRST_RUN_CHECKLIST.md").read_text().lower()
        assert "micro sft" in text, "FIRST_RUN_CHECKLIST must mention micro SFT"

    def test_readme_mentions_micro_sft(self) -> None:
        text = (PROJECT_ROOT / "README.md").read_text().lower()
        assert "micro sft" in text, "README must mention micro SFT"

    def test_readme_version_0132(self) -> None:
        text = (PROJECT_ROOT / "README.md").read_text()
        assert "0.1.32" in text, "README must mention v0.1.32"

    def test_index_html_version_0132(self) -> None:
        text = (PROJECT_ROOT / "docs" / "index.html").read_text()
        assert "0.1.32" in text, "docs/index.html must mention v0.1.32"


# ---------------------------------------------------------------------------
# No tracked artifacts
# ---------------------------------------------------------------------------


class TestNoTrackedArtifactsV0132:
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


class TestGateV0132:
    """Test that the gate is still BLOCKED."""

    def test_smoke_config_gate_blocked(self) -> None:
        text = (PROJECT_ROOT / "training" / "configs" / "hf_jobs_kimari4b_smoke.v0.yaml").read_text()
        assert "BLOCKED" in text

    def test_micro_sft_config_gate_blocked(self) -> None:
        text = (PROJECT_ROOT / "training" / "configs" / "hf_jobs_kimari4b_micro_sft.v0.yaml").read_text()
        assert "BLOCKED" in text

    def test_micro_sft_result_gate_blocked(self) -> None:
        text = (PROJECT_ROOT / "docs" / "HF_JOBS_MICRO_SFT_RESULT.md").read_text()
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
