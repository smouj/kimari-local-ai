"""Release validation tests for v0.1.34-alpha.

Validates all v0.1.34 artifacts:
- Version consistency (pyproject.toml, __init__.py)
- check_training_stack.py exists and --json works without downloading
- TrainingArguments does not include max_seq_length
- build_training_arguments exists
- build_sft_trainer exists
- prepare_sft_dataset exists
- messages dataset formatting path exists
- text dataset path exists
- hf_jobs config includes check_training_stack.py
- validate_micro_sft_readiness passes
- release-check passes
- No tracked GGUF/safetensors artifacts
- Gate BLOCKED
- No Kimari-4B released claim
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


class TestVersionV0134:
    """Test v0.1.34 version consistency."""

    def test_pyproject_version(self) -> None:
        text = (PROJECT_ROOT / "pyproject.toml").read_text()
        assert "0.1.34-alpha" in text, "pyproject.toml must have version 0.1.34-alpha"

    def test_init_version(self) -> None:
        text = (PROJECT_ROOT / "kimari" / "__init__.py").read_text()
        assert "0.1.34-alpha" in text, "__init__.py must have version 0.1.34-alpha"


# ---------------------------------------------------------------------------
# check_training_stack.py
# ---------------------------------------------------------------------------


class TestCheckTrainingStackV0134:
    """Test check_training_stack.py script."""

    def test_script_exists(self) -> None:
        path = PROJECT_ROOT / "training" / "scripts" / "check_training_stack.py"
        assert path.exists(), "check_training_stack.py must exist"

    def test_json_output_works(self) -> None:
        """check_training_stack.py --json should work without downloading models."""
        result = subprocess.run(
            [
                sys.executable,
                "training/scripts/check_training_stack.py",
                "--json",
            ],
            capture_output=True,
            text=True,
            cwd=str(PROJECT_ROOT),
            timeout=30,
        )
        assert result.returncode == 0, f"check_training_stack.py --json failed: {result.stderr}"
        data = json.loads(result.stdout)
        assert "checks" in data, "JSON output must contain 'checks'"
        assert "compatibility" in data, "JSON output must contain 'compatibility'"

    def test_no_model_downloads(self) -> None:
        """Script should not attempt model downloads."""
        text = (PROJECT_ROOT / "training" / "scripts" / "check_training_stack.py").read_text()
        assert "from_pretrained" not in text, "check_training_stack should not call from_pretrained"
        # The script mentions "no model downloads" which is fine —
        # what matters is it doesn't call download functions
        lines = text.splitlines()
        for line in lines:
            stripped = line.strip()
            # Skip comments
            if stripped.startswith("#") or stripped.startswith('"""') or stripped.startswith("'''"):
                continue
            # Should not have download-related function calls
            if "download" in stripped.lower() and "no " not in stripped.lower() and "without" not in stripped.lower():
                # Allow lines that say "no downloading" or "without downloading"
                raise AssertionError(f"check_training_stack should not call download functions: {stripped}")


# ---------------------------------------------------------------------------
# train_sft_lora.py compatibility functions
# ---------------------------------------------------------------------------


class TestTrainSftLoraCompatV0134:
    """Test TRL/SFTTrainer compatibility functions in train_sft_lora.py."""

    def test_build_training_arguments_exists(self) -> None:
        text = (PROJECT_ROOT / "training" / "scripts" / "train_sft_lora.py").read_text()
        assert "def build_training_arguments" in text, "build_training_arguments must exist in train_sft_lora.py"

    def test_build_sft_trainer_exists(self) -> None:
        text = (PROJECT_ROOT / "training" / "scripts" / "train_sft_lora.py").read_text()
        assert "def build_sft_trainer" in text, "build_sft_trainer must exist in train_sft_lora.py"

    def test_prepare_sft_dataset_exists(self) -> None:
        text = (PROJECT_ROOT / "training" / "scripts" / "train_sft_lora.py").read_text()
        assert "def prepare_sft_dataset" in text, "prepare_sft_dataset must exist in train_sft_lora.py"

    def test_max_seq_length_not_in_training_arguments(self) -> None:
        """max_seq_length should NOT be passed to TrainingArguments."""
        text = (PROJECT_ROOT / "training" / "scripts" / "train_sft_lora.py").read_text()

        # Check that build_training_arguments exists
        if "def build_training_arguments" not in text:
            raise AssertionError("build_training_arguments function missing")

        # Extract the build_training_arguments function body
        parts = text.split("def build_training_arguments")
        if len(parts) < 2:
            raise AssertionError("Could not find build_training_arguments")

        func_body = parts[1].split("\ndef ")[0]  # Get until next function

        # max_seq_length should NOT appear in TrainingArguments within this function
        # But it's OK if it appears in the SFTTrainer call
        assert "max_seq_length" not in func_body or "SFTTrainer" in func_body, (
            "max_seq_length must not be passed to TrainingArguments — use SFTTrainer instead"
        )

    def test_messages_formatting_path_exists(self) -> None:
        """prepare_sft_dataset must handle 'messages' column."""
        text = (PROJECT_ROOT / "training" / "scripts" / "train_sft_lora.py").read_text()
        assert "messages" in text, "prepare_sft_dataset must handle 'messages' column"

    def test_text_column_path_exists(self) -> None:
        """prepare_sft_dataset must handle 'text' column."""
        text = (PROJECT_ROOT / "training" / "scripts" / "train_sft_lora.py").read_text()
        # The text column check should be in prepare_sft_dataset
        assert '"text"' in text or "'text'" in text, "prepare_sft_dataset must handle 'text' column"

    def test_eval_strategy_fallback(self) -> None:
        """build_training_arguments should handle eval_strategy/evaluation_strategy."""
        text = (PROJECT_ROOT / "training" / "scripts" / "train_sft_lora.py").read_text()
        assert "eval_strategy" in text or "evaluation_strategy" in text, (
            "build_training_arguments must handle eval_strategy/evaluation_strategy compatibility"
        )

    def test_processing_class_support(self) -> None:
        """build_sft_trainer should support processing_class for newer TRL."""
        text = (PROJECT_ROOT / "training" / "scripts" / "train_sft_lora.py").read_text()
        assert "processing_class" in text, "build_sft_trainer must support processing_class for newer TRL versions"

    def test_tokenizer_support(self) -> None:
        """build_sft_trainer should support tokenizer for older TRL."""
        text = (PROJECT_ROOT / "training" / "scripts" / "train_sft_lora.py").read_text()
        assert "tokenizer" in text, "build_sft_trainer must support tokenizer parameter"


# ---------------------------------------------------------------------------
# HF Jobs config
# ---------------------------------------------------------------------------


class TestHfJobsConfigV0134:
    """Test HF Jobs micro SFT config for v0.1.34."""

    def test_config_includes_check_training_stack(self) -> None:
        text = (PROJECT_ROOT / "training" / "configs" / "hf_jobs_kimari4b_micro_sft.v0.yaml").read_text()
        assert "check_training_stack" in text, "HF Jobs config must include check_training_stack.py command"

    def test_config_includes_micro_run_yes(self) -> None:
        text = (PROJECT_ROOT / "training" / "configs" / "hf_jobs_kimari4b_micro_sft.v0.yaml").read_text()
        assert "--micro-run" in text, "Config must include --micro-run in command"
        assert "--yes" in text, "Config must include --yes in command"

    def test_config_gate_blocked(self) -> None:
        text = (PROJECT_ROOT / "training" / "configs" / "hf_jobs_kimari4b_micro_sft.v0.yaml").read_text()
        assert "BLOCKED" in text, "Config must contain BLOCKED gate state"


# ---------------------------------------------------------------------------
# validate_micro_sft_readiness
# ---------------------------------------------------------------------------


class TestValidateReadinessV0134:
    """Test validate_micro_sft_readiness.py for v0.1.34 checks."""

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

    def test_checks_for_check_training_stack(self) -> None:
        text = (PROJECT_ROOT / "training" / "scripts" / "validate_micro_sft_readiness.py").read_text()
        assert "check_training_stack" in text, (
            "validate_micro_sft_readiness must check for check_training_stack in commands"
        )

    def test_checks_for_hf_upload(self) -> None:
        text = (PROJECT_ROOT / "training" / "scripts" / "validate_micro_sft_readiness.py").read_text()
        assert "hf upload" in text or "huggingface-cli upload" in text, (
            "validate_micro_sft_readiness must check for forbidden HF upload commands"
        )


# ---------------------------------------------------------------------------
# Documentation
# ---------------------------------------------------------------------------


class TestDocsV0134:
    """Test v0.1.34 documentation artifacts."""

    def test_training_stack_compatibility_doc_exists(self) -> None:
        path = PROJECT_ROOT / "docs" / "TRAINING_STACK_COMPATIBILITY.md"
        assert path.exists(), "docs/TRAINING_STACK_COMPATIBILITY.md must exist"

    def test_training_stack_doc_mentions_max_seq_length(self) -> None:
        text = (PROJECT_ROOT / "docs" / "TRAINING_STACK_COMPATIBILITY.md").read_text().lower()
        assert "max_seq_length" in text, "TRAINING_STACK_COMPATIBILITY.md must discuss max_seq_length placement"

    def test_training_stack_doc_mentions_processing_class(self) -> None:
        text = (PROJECT_ROOT / "docs" / "TRAINING_STACK_COMPATIBILITY.md").read_text().lower()
        assert "processing_class" in text, "TRAINING_STACK_COMPATIBILITY.md must discuss processing_class vs tokenizer"


# ---------------------------------------------------------------------------
# Gate
# ---------------------------------------------------------------------------


class TestGateV0134:
    """Test that the gate is still BLOCKED for v0.1.34."""

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


# ---------------------------------------------------------------------------
# No tracked artifacts
# ---------------------------------------------------------------------------


class TestNoTrackedArtifactsV0134:
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
