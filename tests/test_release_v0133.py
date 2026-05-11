"""Release validation tests for v0.1.33-alpha.

Validates all v0.1.33 artifacts:
- Version consistency (pyproject.toml, __init__.py)
- train_sft_lora.py --show-supported-flags (all micro flags, no torch import)
- apply_cli_overrides function and key mapping
- Training protections (--micro-run required, --yes required, CI guard, dry-run)
- validate_micro_sft_readiness.py (script exists, readiness check passes)
- Micro SFT config (--micro-run --yes, no push_to_hub, allow_hf_upload false, gate BLOCKED)
- No --token in training scripts
- Gate BLOCKED across all artifacts
- No tracked GGUF/safetensors artifacts
- MICRO_SFT_IMPLEMENTATION.md documentation
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


class TestVersionV0133:
    """Test v0.1.33 version consistency."""

    def test_pyproject_version(self) -> None:
        text = (PROJECT_ROOT / "pyproject.toml").read_text()
        assert "0.1.33-alpha" in text, "pyproject.toml must have version 0.1.33-alpha"

    def test_init_version(self) -> None:
        text = (PROJECT_ROOT / "kimari" / "__init__.py").read_text()
        assert "0.1.33-alpha" in text, "__init__.py must have version 0.1.33-alpha"


# ---------------------------------------------------------------------------
# --show-supported-flags
# ---------------------------------------------------------------------------


class TestShowSupportedFlagsV0133:
    """Test --show-supported-flags for v0.1.33 micro SFT flags."""

    REQUIRED_FLAGS = [
        "--dataset-path",
        "--eval-dataset-path",
        "--output-dir",
        "--max-steps",
        "--eval-steps",
        "--save-steps",
        "--logging-steps",
        "--per-device-train-batch-size",
        "--gradient-accumulation-steps",
        "--learning-rate",
        "--max-seq-length",
        "--micro-run",
        "--yes",
    ]

    def test_show_supported_flags_json(self) -> None:
        result = subprocess.run(
            [
                sys.executable,
                "training/scripts/train_sft_lora.py",
                "--show-supported-flags",
                "--json",
            ],
            capture_output=True,
            text=True,
            cwd=str(PROJECT_ROOT),
            timeout=30,
        )
        assert result.returncode == 0, f"--show-supported-flags --json failed: {result.stderr}"
        data = json.loads(result.stdout)
        flags = data.get("supported_flags", [])
        for flag in self.REQUIRED_FLAGS:
            assert flag in flags, f"Required flag {flag} missing from --show-supported-flags --json output"

    def test_show_supported_flags_no_torch(self) -> None:
        """--show-supported-flags should not import torch at module level."""
        text = (PROJECT_ROOT / "training" / "scripts" / "train_sft_lora.py").read_text()
        # Check that "import torch" does NOT appear at module level (only inside functions)
        # The script uses lazy imports inside run_sft_training()
        lines = text.splitlines()
        for i, line in enumerate(lines):
            stripped = line.strip()
            # Module-level import would have no indentation
            if stripped.startswith("import torch") and not line.startswith(" ") and not line.startswith("\t"):
                pytest_fail_msg = (
                    f"Module-level 'import torch' found at line {i + 1}. "
                    "torch must only be imported inside functions (lazy import)."
                )
                raise AssertionError(pytest_fail_msg)


# ---------------------------------------------------------------------------
# apply_cli_overrides
# ---------------------------------------------------------------------------


class TestApplyCliOverridesV0133:
    """Test apply_cli_overrides function in train_sft_lora.py."""

    REQUIRED_KEYS = [
        "dataset_path",
        "eval_dataset_path",
        "output_dir",
        "max_steps",
        "eval_steps",
        "save_steps",
        "logging_steps",
        "per_device_train_batch_size",
        "gradient_accumulation_steps",
        "learning_rate",
        "max_seq_length",
    ]

    def test_apply_cli_overrides_function_exists(self) -> None:
        text = (PROJECT_ROOT / "training" / "scripts" / "train_sft_lora.py").read_text()
        assert "def apply_cli_overrides" in text, "apply_cli_overrides function must exist in train_sft_lora.py"

    def test_apply_cli_overrides_keys(self) -> None:
        text = (PROJECT_ROOT / "training" / "scripts" / "train_sft_lora.py").read_text()
        for key in self.REQUIRED_KEYS:
            assert key in text, f"apply_cli_overrides must map CLI arg '{key}' to config key"


# ---------------------------------------------------------------------------
# Training protections
# ---------------------------------------------------------------------------


class TestTrainingProtectionsV0133:
    """Test training protection mechanisms in train_sft_lora.py."""

    def test_train_without_yes_refuses(self) -> None:
        """Training without --yes should refuse."""
        result = subprocess.run(
            [
                sys.executable,
                "training/scripts/train_sft_lora.py",
                "--config",
                "training/configs/kimari_sft_lora.v0.example.yaml",
                "--micro-run",
            ],
            capture_output=True,
            text=True,
            cwd=str(PROJECT_ROOT),
            timeout=30,
        )
        assert result.returncode != 0, "Training without --yes should fail"
        assert "yes" in result.stderr.lower(), "Error message must mention 'yes'"

    def test_train_without_micro_run_refuses(self) -> None:
        """Training without --micro-run should refuse."""
        result = subprocess.run(
            [
                sys.executable,
                "training/scripts/train_sft_lora.py",
                "--config",
                "training/configs/kimari_sft_lora.v0.example.yaml",
                "--yes",
            ],
            capture_output=True,
            text=True,
            cwd=str(PROJECT_ROOT),
            timeout=30,
        )
        assert result.returncode != 0, "Training without --micro-run should fail"
        assert "micro-run" in result.stderr.lower(), "Error message must mention 'micro-run'"

    def test_ci_true_refuses_training(self) -> None:
        """CI=true environment should block training even with --micro-run --yes."""
        result = subprocess.run(
            [
                sys.executable,
                "training/scripts/train_sft_lora.py",
                "--config",
                "training/configs/kimari_sft_lora.v0.example.yaml",
                "--micro-run",
                "--yes",
            ],
            capture_output=True,
            text=True,
            cwd=str(PROJECT_ROOT),
            timeout=30,
            env={**__import__("os").environ, "CI": "true"},
        )
        assert result.returncode != 0, "Training with CI=true should fail"
        assert "ci" in result.stderr.lower(), "Error message must mention 'ci'"

    def test_dry_run_does_not_import_torch(self) -> None:
        """--dry-run should succeed without torch installed."""
        result = subprocess.run(
            [
                sys.executable,
                "training/scripts/train_sft_lora.py",
                "--config",
                "training/configs/kimari_sft_lora.v0.example.yaml",
                "--dry-run",
            ],
            capture_output=True,
            text=True,
            cwd=str(PROJECT_ROOT),
            timeout=30,
        )
        assert result.returncode == 0, f"--dry-run should succeed: {result.stderr}"


# ---------------------------------------------------------------------------
# validate_micro_sft_readiness.py
# ---------------------------------------------------------------------------


class TestValidateMicroSftReadinessV0133:
    """Test validate_micro_sft_readiness.py script."""

    def test_script_exists(self) -> None:
        path = PROJECT_ROOT / "training" / "scripts" / "validate_micro_sft_readiness.py"
        assert path.exists(), "validate_micro_sft_readiness.py must exist"

    def test_readiness_check_passes(self) -> None:
        result = subprocess.run(
            [
                sys.executable,
                "training/scripts/validate_micro_sft_readiness.py",
                "--config",
                "training/configs/hf_jobs_kimari4b_micro_sft.v0.yaml",
                "--json",
            ],
            capture_output=True,
            text=True,
            cwd=str(PROJECT_ROOT),
            timeout=30,
        )
        assert result.returncode == 0, f"Readiness check failed: {result.stderr}"
        data = json.loads(result.stdout)
        assert data.get("ready") is True, f"Micro SFT readiness check returned ready=False: {data}"


# ---------------------------------------------------------------------------
# HF Jobs micro SFT config
# ---------------------------------------------------------------------------


class TestHfJobsConfigV0133:
    """Test HF Jobs micro SFT config for v0.1.33."""

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

    def test_config_includes_micro_run_yes(self) -> None:
        text = (PROJECT_ROOT / "training" / "configs" / "hf_jobs_kimari4b_micro_sft.v0.yaml").read_text()
        assert "--micro-run" in text, "Config must include --micro-run in command"
        assert "--yes" in text, "Config must include --yes in command"

    def test_config_no_push_to_hub(self) -> None:
        text = (PROJECT_ROOT / "training" / "configs" / "hf_jobs_kimari4b_micro_sft.v0.yaml").read_text()
        # push_to_hub should NOT appear in the training command
        # The config itself has allow_push_to_hub: false, but the train command
        # must not include push_to_hub as an argument
        commands_section = False
        for line in text.splitlines():
            stripped = line.strip()
            if stripped.startswith("commands:"):
                commands_section = True
                continue
            if commands_section and stripped.startswith("- "):
                if "push_to_hub" in stripped:
                    raise AssertionError("Training command must not include push_to_hub")
            elif commands_section and not stripped.startswith("-") and ":" in stripped:
                commands_section = False

    def test_config_allow_hf_upload_false(self) -> None:
        path = PROJECT_ROOT / "training" / "configs" / "hf_jobs_kimari4b_micro_sft.v0.yaml"
        config = self._parse_yaml_simple(path)
        assert config.get("allow_hf_upload") is False, "allow_hf_upload must be false"

    def test_config_gate_blocked(self) -> None:
        text = (PROJECT_ROOT / "training" / "configs" / "hf_jobs_kimari4b_micro_sft.v0.yaml").read_text()
        assert "BLOCKED" in text, "Config must contain BLOCKED gate state"


# ---------------------------------------------------------------------------
# No --token
# ---------------------------------------------------------------------------


class TestNoTokenV0133:
    """Test that no --token argument exists in training scripts."""

    def test_train_sft_no_token_arg(self) -> None:
        text = (PROJECT_ROOT / "training" / "scripts" / "train_sft_lora.py").read_text()
        assert '"--token"' not in text, "train_sft_lora.py must not have --token argument"

    def test_hf_jobs_micro_sft_no_token(self) -> None:
        text = (PROJECT_ROOT / "training" / "scripts" / "hf_jobs_micro_sft.py").read_text()
        assert '"--token"' not in text, "hf_jobs_micro_sft.py must not have --token argument"


# ---------------------------------------------------------------------------
# Gate
# ---------------------------------------------------------------------------


class TestGateV0133:
    """Test that the gate is still BLOCKED for v0.1.33."""

    def test_micro_sft_config_gate_blocked(self) -> None:
        text = (PROJECT_ROOT / "training" / "configs" / "hf_jobs_kimari4b_micro_sft.v0.yaml").read_text()
        assert "BLOCKED" in text, "Micro SFT config must have BLOCKED gate state"

    def test_micro_sft_result_gate_blocked(self) -> None:
        text = (PROJECT_ROOT / "docs" / "HF_JOBS_MICRO_SFT_RESULT.md").read_text()
        assert "BLOCKED" in text, "HF_JOBS_MICRO_SFT_RESULT.md must mention BLOCKED"

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


# ---------------------------------------------------------------------------
# No tracked artifacts
# ---------------------------------------------------------------------------


class TestNoTrackedArtifactsV0133:
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


# ---------------------------------------------------------------------------
# Micro SFT docs
# ---------------------------------------------------------------------------


class TestMicroSftDocsV0133:
    """Test MICRO_SFT_IMPLEMENTATION.md documentation for v0.1.33."""

    def test_implementation_doc_exists(self) -> None:
        path = PROJECT_ROOT / "docs" / "MICRO_SFT_IMPLEMENTATION.md"
        assert path.exists(), "docs/MICRO_SFT_IMPLEMENTATION.md must exist"

    def test_implementation_doc_mentions_micro_run(self) -> None:
        text = (PROJECT_ROOT / "docs" / "MICRO_SFT_IMPLEMENTATION.md").read_text().lower()
        assert "micro-run" in text or "micro_run" in text, (
            "MICRO_SFT_IMPLEMENTATION.md must mention micro-run or micro_run"
        )

    def test_implementation_doc_mentions_blocked(self) -> None:
        text = (PROJECT_ROOT / "docs" / "MICRO_SFT_IMPLEMENTATION.md").read_text()
        assert "BLOCKED" in text, "MICRO_SFT_IMPLEMENTATION.md must mention BLOCKED gate state"
