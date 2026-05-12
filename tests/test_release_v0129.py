"""Release validation tests for v0.1.29-alpha.

Validates all v0.1.29 artifacts:
- Artifact field naming changes
- Command compatibility fix
- train_sft_lora --show-supported-flags
- validate_private_sft_commands
- HF Jobs smoke config
- hf_jobs_private_run
- hf_jobs_status
- Smoke summary template
- No false claims
- Gate BLOCKED
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def parse_simple_yaml(path: Path) -> dict | None:
    """Parse a simple YAML file without pyyaml."""
    try:
        import yaml

        with open(path) as f:
            return yaml.safe_load(f)
    except ImportError:
        pass

    text = path.read_text()
    result: dict = {}
    current_list_key: str | None = None
    current_list: list | None = None

    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue

        if stripped.startswith("- ") and current_list_key is not None:
            item = stripped[2:].strip().strip('"').strip("'")
            if current_list is not None:
                current_list.append(item)
            continue

        if ":" in stripped:
            if current_list_key is not None and current_list is not None:
                result[current_list_key] = current_list
                current_list_key = None
                current_list = None

            key, _, value = stripped.partition(":")
            key = key.strip()
            value = value.strip().strip('"').strip("'")

            if not value:
                current_list_key = key
                current_list = []
            else:
                if value.lower() == "true":
                    result[key] = True
                elif value.lower() == "false":
                    result[key] = False
                elif value.lower() in ("null", "~", "none"):
                    result[key] = None
                else:
                    try:
                        result[key] = int(value)
                    except ValueError:
                        try:
                            result[key] = float(value)
                        except ValueError:
                            result[key] = value

    if current_list_key is not None and current_list is not None:
        result[current_list_key] = current_list

    return result


# ---------------------------------------------------------------------------
# Version
# ---------------------------------------------------------------------------


class TestVersionV0129:
    """Test v0.1.29 version consistency."""

    def test_pyproject_version(self) -> None:
        text = (PROJECT_ROOT / "pyproject.toml").read_text()
        assert "0.1.29-alpha" in text, "pyproject.toml must have version 0.1.29-alpha"

    def test_init_version(self) -> None:
        text = (PROJECT_ROOT / "kimari" / "__init__.py").read_text()
        assert "0.1.29-alpha" in text, "__init__.py must have version 0.1.29-alpha"


# ---------------------------------------------------------------------------
# Artifact field naming
# ---------------------------------------------------------------------------


class TestArtifactNamingV0129:
    """Test artifact field name changes."""

    def test_expected_local_artifacts_field(self) -> None:
        config = parse_simple_yaml(PROJECT_ROOT / "training" / "configs" / "kimari4b_private_sft_run.v0.yaml")
        assert config is not None
        assert "expected_local_artifacts" in config, "expected_local_artifacts field must exist"

    def test_forbidden_commit_artifacts_field(self) -> None:
        config = parse_simple_yaml(PROJECT_ROOT / "training" / "configs" / "kimari4b_private_sft_run.v0.yaml")
        assert config is not None
        assert "forbidden_commit_artifacts" in config, "forbidden_commit_artifacts field must exist"

    def test_no_old_expected_artifacts(self) -> None:
        text = (PROJECT_ROOT / "training" / "configs" / "kimari4b_private_sft_run.v0.yaml").read_text()
        lines = [line.strip() for line in text.splitlines() if not line.strip().startswith("#")]
        # Should not have "expected_artifacts:" (without _local_)
        for line in lines:
            if line.startswith("expected_artifacts:"):
                pytest.fail("Old field 'expected_artifacts' found — should be 'expected_local_artifacts'")

    def test_no_old_forbidden_artifacts(self) -> None:
        text = (PROJECT_ROOT / "training" / "configs" / "kimari4b_private_sft_run.v0.yaml").read_text()
        lines = [line.strip() for line in text.splitlines() if not line.strip().startswith("#")]
        for line in lines:
            if line.startswith("forbidden_artifacts:"):
                pytest.fail("Old field 'forbidden_artifacts' found — should be 'forbidden_commit_artifacts'")

    def test_local_only_true(self) -> None:
        config = parse_simple_yaml(PROJECT_ROOT / "training" / "configs" / "kimari4b_private_sft_run.v0.yaml")
        assert config is not None
        assert config.get("local_only") is True, "local_only must be true"

    def test_commit_allowed_false(self) -> None:
        config = parse_simple_yaml(PROJECT_ROOT / "training" / "configs" / "kimari4b_private_sft_run.v0.yaml")
        assert config is not None
        assert config.get("commit_allowed") is False, "commit_allowed must be false"

    def test_publish_allowed_false(self) -> None:
        config = parse_simple_yaml(PROJECT_ROOT / "training" / "configs" / "kimari4b_private_sft_run.v0.yaml")
        assert config is not None
        assert config.get("publish_allowed") is False, "publish_allowed must be false"


# ---------------------------------------------------------------------------
# Command compatibility
# ---------------------------------------------------------------------------


class TestCommandCompatibilityV0129:
    """Test command generator training_real has no unsupported flags."""

    def test_command_script_json(self) -> None:
        result = subprocess.run(
            [
                sys.executable,
                "training/scripts/kimari4b_private_sft_command.py",
                "--config",
                "training/configs/kimari4b_private_sft_run.v0.yaml",
                "--json",
            ],
            capture_output=True,
            text=True,
            cwd=str(PROJECT_ROOT),
            timeout=30,
        )
        assert result.returncode == 0, f"Command script failed: {result.stderr}"
        data = json.loads(result.stdout)
        assert "run_id" in data

    def test_training_real_no_unsupported_flags(self) -> None:
        result = subprocess.run(
            [
                sys.executable,
                "training/scripts/kimari4b_private_sft_command.py",
                "--config",
                "training/configs/kimari4b_private_sft_run.v0.yaml",
                "--json",
            ],
            capture_output=True,
            text=True,
            cwd=str(PROJECT_ROOT),
            timeout=30,
        )
        data = json.loads(result.stdout)
        training_real = data.get("training_real", [])
        unsupported = ["--dataset-path", "--eval-dataset-path", "--output-dir"]
        for cmd in training_real:
            for flag in unsupported:
                assert flag not in cmd, f"Unsupported flag {flag} found in training_real: {cmd}"

    def test_command_compatibility_status(self) -> None:
        result = subprocess.run(
            [
                sys.executable,
                "training/scripts/kimari4b_private_sft_command.py",
                "--config",
                "training/configs/kimari4b_private_sft_run.v0.yaml",
                "--json",
            ],
            capture_output=True,
            text=True,
            cwd=str(PROJECT_ROOT),
            timeout=30,
        )
        data = json.loads(result.stdout)
        assert data.get("command_compatibility_status") == "compatible_with_current_training_skeleton"
        assert "unsupported_flags_removed" in data


# ---------------------------------------------------------------------------
# train_sft_lora --show-supported-flags
# ---------------------------------------------------------------------------


class TestShowSupportedFlagsV0129:
    """Test train_sft_lora.py --show-supported-flags."""

    def test_show_supported_flags(self) -> None:
        result = subprocess.run(
            [sys.executable, "training/scripts/train_sft_lora.py", "--show-supported-flags"],
            capture_output=True,
            text=True,
            cwd=str(PROJECT_ROOT),
            timeout=30,
        )
        assert result.returncode == 0, f"--show-supported-flags failed: {result.stderr}"
        assert "--config" in result.stdout
        assert "--dry-run" in result.stdout

    def test_show_supported_flags_json(self) -> None:
        result = subprocess.run(
            [sys.executable, "training/scripts/train_sft_lora.py", "--show-supported-flags", "--json"],
            capture_output=True,
            text=True,
            cwd=str(PROJECT_ROOT),
            timeout=30,
        )
        assert result.returncode == 0, f"--show-supported-flags --json failed: {result.stderr}"
        data = json.loads(result.stdout)
        assert "supported_flags" in data
        expected_flags = [
            "--config",
            "--dry-run",
            "--print-command",
            "--estimate-only",
            "--require-dataset",
            "--show-supported-flags",
            "--json",
        ]
        for flag in expected_flags:
            assert flag in data["supported_flags"], f"Missing flag: {flag}"


# ---------------------------------------------------------------------------
# validate_private_sft_commands
# ---------------------------------------------------------------------------


class TestValidateCommandsV0129:
    """Test validate_private_sft_commands.py."""

    def test_validate_script_exists(self) -> None:
        path = PROJECT_ROOT / "training" / "scripts" / "validate_private_sft_commands.py"
        assert path.exists(), "validate_private_sft_commands.py missing"

    def test_validate_with_generated_commands(self) -> None:
        import tempfile

        # Generate commands first
        gen_result = subprocess.run(
            [
                sys.executable,
                "training/scripts/kimari4b_private_sft_command.py",
                "--config",
                "training/configs/kimari4b_private_sft_run.v0.yaml",
                "--json",
            ],
            capture_output=True,
            text=True,
            cwd=str(PROJECT_ROOT),
            timeout=30,
        )
        assert gen_result.returncode == 0

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            f.write(gen_result.stdout)
            cmd_json_path = f.name

        try:
            val_result = subprocess.run(
                [
                    sys.executable,
                    "training/scripts/validate_private_sft_commands.py",
                    "--command-json",
                    cmd_json_path,
                    "--training-script",
                    "training/scripts/train_sft_lora.py",
                    "--json",
                ],
                capture_output=True,
                text=True,
                cwd=str(PROJECT_ROOT),
                timeout=30,
            )
            assert val_result.returncode == 0, f"Validation failed: {val_result.stderr}"
            data = json.loads(val_result.stdout)
            assert data.get("valid") is True, f"Validation result: {data}"
            assert data.get("checks", {}).get("gate_blocked") is True
        finally:
            Path(cmd_json_path).unlink(missing_ok=True)


# ---------------------------------------------------------------------------
# HF Jobs smoke config
# ---------------------------------------------------------------------------


class TestHFJobsConfigV0129:
    """Test HF Jobs smoke config."""

    def test_hf_jobs_config_exists(self) -> None:
        path = PROJECT_ROOT / "training" / "configs" / "hf_jobs_kimari4b_smoke.v0.yaml"
        assert path.exists(), "hf_jobs_kimari4b_smoke.v0.yaml missing"

    def test_hf_jobs_config_parses(self) -> None:
        config = parse_simple_yaml(PROJECT_ROOT / "training" / "configs" / "hf_jobs_kimari4b_smoke.v0.yaml")
        assert config is not None
        assert isinstance(config, dict)

    def test_allow_training_false(self) -> None:
        config = parse_simple_yaml(PROJECT_ROOT / "training" / "configs" / "hf_jobs_kimari4b_smoke.v0.yaml")
        assert config is not None
        assert config.get("allow_training") is False

    def test_allow_hf_upload_false(self) -> None:
        config = parse_simple_yaml(PROJECT_ROOT / "training" / "configs" / "hf_jobs_kimari4b_smoke.v0.yaml")
        assert config is not None
        assert config.get("allow_hf_upload") is False

    def test_max_budget_set(self) -> None:
        config = parse_simple_yaml(PROJECT_ROOT / "training" / "configs" / "hf_jobs_kimari4b_smoke.v0.yaml")
        assert config is not None
        assert config.get("max_budget_usd") is not None
        assert config.get("max_budget_usd") <= 10

    def test_run_type_smoke_test(self) -> None:
        config = parse_simple_yaml(PROJECT_ROOT / "training" / "configs" / "hf_jobs_kimari4b_smoke.v0.yaml")
        assert config is not None
        assert config.get("run_type") == "smoke_test"


# ---------------------------------------------------------------------------
# hf_jobs_private_run
# ---------------------------------------------------------------------------


class TestHFJobsPrivateRunV0129:
    """Test hf_jobs_private_run.py."""

    def test_script_exists(self) -> None:
        path = PROJECT_ROOT / "training" / "scripts" / "hf_jobs_private_run.py"
        assert path.exists(), "hf_jobs_private_run.py missing"

    def test_dry_run_json(self) -> None:
        result = subprocess.run(
            [
                sys.executable,
                "training/scripts/hf_jobs_private_run.py",
                "--config",
                "training/configs/hf_jobs_kimari4b_smoke.v0.yaml",
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
        assert data.get("submitted") is False
        assert data.get("mode") == "dry_run"
        assert data.get("allow_training") is False
        assert data.get("allow_hf_upload") is False

    def test_print_command(self) -> None:
        result = subprocess.run(
            [
                sys.executable,
                "training/scripts/hf_jobs_private_run.py",
                "--config",
                "training/configs/hf_jobs_kimari4b_smoke.v0.yaml",
                "--print-command",
            ],
            capture_output=True,
            text=True,
            cwd=str(PROJECT_ROOT),
            timeout=30,
        )
        assert result.returncode == 0, f"print-command failed: {result.stderr}"
        assert "hf jobs run" in result.stdout

    def test_refuses_submit_without_allow_submit(self) -> None:
        result = subprocess.run(
            [
                sys.executable,
                "training/scripts/hf_jobs_private_run.py",
                "--config",
                "training/configs/hf_jobs_kimari4b_smoke.v0.yaml",
                "--yes",
            ],
            capture_output=True,
            text=True,
            cwd=str(PROJECT_ROOT),
            timeout=30,
        )
        # Should fail because --allow-submit is missing
        assert result.returncode != 0

    def test_refuses_submit_without_yes(self) -> None:
        result = subprocess.run(
            [
                sys.executable,
                "training/scripts/hf_jobs_private_run.py",
                "--config",
                "training/configs/hf_jobs_kimari4b_smoke.v0.yaml",
                "--allow-submit",
            ],
            capture_output=True,
            text=True,
            cwd=str(PROJECT_ROOT),
            timeout=30,
        )
        # Should fail because --yes is missing
        assert result.returncode != 0

    def test_no_token_arg(self) -> None:
        text = (PROJECT_ROOT / "training" / "scripts" / "hf_jobs_private_run.py").read_text()
        # Check that there is no argparse --token argument (parser.add_argument with --token)
        lines = text.splitlines()
        for line in lines:
            stripped = line.strip()
            if stripped.startswith("parser.add_argument") and '"--token"' in stripped:
                pytest.fail("hf_jobs_private_run.py must not accept --token flag")


# ---------------------------------------------------------------------------
# hf_jobs_status
# ---------------------------------------------------------------------------


class TestHFJobsStatusV0129:
    """Test hf_jobs_status.py."""

    def test_script_exists(self) -> None:
        path = PROJECT_ROOT / "training" / "scripts" / "hf_jobs_status.py"
        assert path.exists(), "hf_jobs_status.py missing"

    def test_read_only(self) -> None:
        text = (PROJECT_ROOT / "training" / "scripts" / "hf_jobs_status.py").read_text().lower()
        # Should mention "read-only" or "does not modify" or "does not cancel"
        assert "read-only" in text or "read only" in text or "does not modify" in text, (
            "hf_jobs_status must state it is read-only"
        )
        # Should NOT contain subprocess calls that modify jobs (like "hf jobs cancel" or "hf jobs run")
        assert "hf jobs cancel" not in text, "hf_jobs_status must not cancel jobs"
        assert "hf jobs run" not in text, "hf_jobs_status must not run jobs"


# ---------------------------------------------------------------------------
# Smoke summary template
# ---------------------------------------------------------------------------


class TestSmokeSummaryTemplateV0129:
    """Test HF Jobs smoke summary template."""

    def test_template_exists(self) -> None:
        path = PROJECT_ROOT / "training" / "templates" / "hf_jobs_smoke_summary.template.json"
        assert path.exists(), "hf_jobs_smoke_summary.template.json missing"

    def test_template_parses(self) -> None:
        path = PROJECT_ROOT / "training" / "templates" / "hf_jobs_smoke_summary.template.json"
        data = json.loads(path.read_text())
        assert isinstance(data, dict)

    def test_training_performed_false(self) -> None:
        path = PROJECT_ROOT / "training" / "templates" / "hf_jobs_smoke_summary.template.json"
        data = json.loads(path.read_text())
        assert data.get("training_performed") is False

    def test_adapter_generated_false(self) -> None:
        path = PROJECT_ROOT / "training" / "templates" / "hf_jobs_smoke_summary.template.json"
        data = json.loads(path.read_text())
        assert data.get("adapter_generated") is False

    def test_hf_upload_performed_false(self) -> None:
        path = PROJECT_ROOT / "training" / "templates" / "hf_jobs_smoke_summary.template.json"
        data = json.loads(path.read_text())
        assert data.get("hf_upload_performed") is False

    def test_gate_blocked(self) -> None:
        path = PROJECT_ROOT / "training" / "templates" / "hf_jobs_smoke_summary.template.json"
        data = json.loads(path.read_text())
        assert data.get("gate_state") == "BLOCKED"


# ---------------------------------------------------------------------------
# New docs
# ---------------------------------------------------------------------------


class TestDocsV0129:
    """Test v0.1.29 documentation."""

    def test_hf_jobs_private_run_doc_exists(self) -> None:
        path = PROJECT_ROOT / "docs" / "HF_JOBS_PRIVATE_RUN.md"
        assert path.exists(), "docs/HF_JOBS_PRIVATE_RUN.md missing"

    def test_hf_jobs_private_run_mentions_blocked(self) -> None:
        text = (PROJECT_ROOT / "docs" / "HF_JOBS_PRIVATE_RUN.md").read_text()
        assert "BLOCKED" in text

    def test_hf_jobs_private_run_no_upload(self) -> None:
        text = (PROJECT_ROOT / "docs" / "HF_JOBS_PRIVATE_RUN.md").read_text().lower()
        assert "no hf upload" in text or "no upload" in text or "forbidden" in text

    def test_hf_jobs_result_handoff_doc_exists(self) -> None:
        path = PROJECT_ROOT / "docs" / "HF_JOBS_RESULT_HANDOFF.md"
        assert path.exists(), "docs/HF_JOBS_RESULT_HANDOFF.md missing"

    def test_hf_jobs_result_handoff_no_adapters(self) -> None:
        text = (PROJECT_ROOT / "docs" / "HF_JOBS_RESULT_HANDOFF.md").read_text().lower()
        assert "adapter" in text and ("no" in text or "not" in text or "must remain" in text or "forbidden" in text)


# ---------------------------------------------------------------------------
# Updated docs
# ---------------------------------------------------------------------------


class TestUpdatedDocsV0129:
    """Test updates to existing docs."""

    def test_private_sft_run_has_hf_jobs_section(self) -> None:
        text = (PROJECT_ROOT / "docs" / "KIMARI4B_PRIVATE_SFT_RUN.md").read_text()
        assert "HF Jobs" in text or "hf_jobs" in text.lower(), "KIMARI4B_PRIVATE_SFT_RUN must mention HF Jobs"

    def test_first_run_checklist_has_hf_jobs(self) -> None:
        text = (PROJECT_ROOT / "docs" / "KIMARI4B_FIRST_RUN_CHECKLIST.md").read_text()
        assert "HF Jobs" in text or "hf_jobs" in text.lower() or "smoke test" in text.lower()

    def test_hf_token_safety_has_jobs_section(self) -> None:
        text = (PROJECT_ROOT / "docs" / "HF_TOKEN_SAFETY.md").read_text()
        assert "HF Jobs" in text or "hf jobs" in text.lower()


# ---------------------------------------------------------------------------
# No tracked artifacts
# ---------------------------------------------------------------------------


class TestNoTrackedArtifactsV0129:
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
