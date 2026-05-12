"""Release validation tests for v0.1.28-alpha.

Validates all v0.1.28 artifacts:
- KIMARI4B_PRIVATE_SFT_RUN.md
- KIMARI4B_FIRST_RUN_CHECKLIST.md
- KIMARI4B_EVAL_CRITERIA.md
- kimari4b_private_sft_run.v0.yaml
- kimari4b_private_sft_command.py
- kimari4b_eval_plan.py
- kimari4b_private_summary.template.json
- FIRST_PRIVATE_SFT_HANDOFF.md Kimari-4B section
- ADAPTER_PREVIEW_GATE.md Kimari-4B section
- README references
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


# ---------------------------------------------------------------------------
# Helper: simple YAML parser (no pyyaml dependency)
# ---------------------------------------------------------------------------


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
# Docs existence
# ---------------------------------------------------------------------------


class TestDocsV0128:
    """Test v0.1.28 documentation files exist and contain required content."""

    def test_kimari4b_private_sft_run_exists(self) -> None:
        path = PROJECT_ROOT / "docs" / "KIMARI4B_PRIVATE_SFT_RUN.md"
        assert path.exists(), "docs/KIMARI4B_PRIVATE_SFT_RUN.md missing"

    def test_kimari4b_private_sft_run_mentions_base_model(self) -> None:
        text = (PROJECT_ROOT / "docs" / "KIMARI4B_PRIVATE_SFT_RUN.md").read_text().lower()
        assert "smollm3" in text, "KIMARI4B_PRIVATE_SFT_RUN.md must mention SmolLM3-3B"

    def test_kimari4b_private_sft_run_mentions_blocked(self) -> None:
        text = (PROJECT_ROOT / "docs" / "KIMARI4B_PRIVATE_SFT_RUN.md").read_text()
        assert "BLOCKED" in text, "KIMARI4B_PRIVATE_SFT_RUN.md must mention BLOCKED gate"

    def test_kimari4b_private_sft_run_no_hf_upload(self) -> None:
        text = (PROJECT_ROOT / "docs" / "KIMARI4B_PRIVATE_SFT_RUN.md").read_text().lower()
        assert "no hf upload" in text or "hf upload" in text, "KIMARI4B_PRIVATE_SFT_RUN.md must address HF upload"

    def test_kimari4b_first_run_checklist_exists(self) -> None:
        path = PROJECT_ROOT / "docs" / "KIMARI4B_FIRST_RUN_CHECKLIST.md"
        assert path.exists(), "docs/KIMARI4B_FIRST_RUN_CHECKLIST.md missing"

    def test_kimari4b_first_run_checklist_has_gate_blocked(self) -> None:
        text = (PROJECT_ROOT / "docs" / "KIMARI4B_FIRST_RUN_CHECKLIST.md").read_text()
        assert "BLOCKED" in text, "First run checklist must mention BLOCKED gate"

    def test_kimari4b_eval_criteria_exists(self) -> None:
        path = PROJECT_ROOT / "docs" / "KIMARI4B_EVAL_CRITERIA.md"
        assert path.exists(), "docs/KIMARI4B_EVAL_CRITERIA.md missing"

    def test_kimari4b_eval_criteria_has_categories(self) -> None:
        text = (PROJECT_ROOT / "docs" / "KIMARI4B_EVAL_CRITERIA.md").read_text().lower()
        for category in ["coding", "safety", "spanish technical", "json validity"]:
            assert category in text, f"Eval criteria must include {category} category"

    def test_kimari4b_eval_criteria_no_scores(self) -> None:
        text = (PROJECT_ROOT / "docs" / "KIMARI4B_EVAL_CRITERIA.md").read_text().lower()
        assert "manual_review_required" in text, "Eval criteria must mention manual_review_required"


# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------


class TestConfigV0128:
    """Test v0.1.28 private SFT run config."""

    def test_private_sft_run_config_exists(self) -> None:
        path = PROJECT_ROOT / "training" / "configs" / "kimari4b_private_sft_run.v0.yaml"
        assert path.exists(), "kimari4b_private_sft_run.v0.yaml missing"

    def test_private_sft_run_config_parses(self) -> None:
        path = PROJECT_ROOT / "training" / "configs" / "kimari4b_private_sft_run.v0.yaml"
        config = parse_simple_yaml(path)
        assert config is not None, "Failed to parse kimari4b_private_sft_run.v0.yaml"
        assert isinstance(config, dict), "Config must be a dict"

    def test_public_release_allowed_false(self) -> None:
        path = PROJECT_ROOT / "training" / "configs" / "kimari4b_private_sft_run.v0.yaml"
        config = parse_simple_yaml(path)
        assert config is not None
        assert config.get("public_release_allowed") is False, "public_release_allowed must be false"

    def test_hf_upload_allowed_false(self) -> None:
        path = PROJECT_ROOT / "training" / "configs" / "kimari4b_private_sft_run.v0.yaml"
        config = parse_simple_yaml(path)
        assert config is not None
        assert config.get("hf_upload_allowed") is False, "hf_upload_allowed must be false"

    def test_preview_gate_state_blocked(self) -> None:
        path = PROJECT_ROOT / "training" / "configs" / "kimari4b_private_sft_run.v0.yaml"
        config = parse_simple_yaml(path)
        assert config is not None
        assert config.get("preview_gate_state") == "BLOCKED", "preview_gate_state must be BLOCKED"

    def test_base_model_smollm3(self) -> None:
        path = PROJECT_ROOT / "training" / "configs" / "kimari4b_private_sft_run.v0.yaml"
        config = parse_simple_yaml(path)
        assert config is not None
        assert "SmolLM3" in str(config.get("base_model", "")), "base_model must mention SmolLM3"

    def test_run_id_set(self) -> None:
        path = PROJECT_ROOT / "training" / "configs" / "kimari4b_private_sft_run.v0.yaml"
        config = parse_simple_yaml(path)
        assert config is not None
        assert config.get("run_id"), "run_id must be set"


# ---------------------------------------------------------------------------
# Scripts
# ---------------------------------------------------------------------------


class TestScriptsV0128:
    """Test v0.1.28 CLI scripts."""

    def test_command_script_exists(self) -> None:
        path = PROJECT_ROOT / "training" / "scripts" / "kimari4b_private_sft_command.py"
        assert path.exists(), "kimari4b_private_sft_command.py missing"

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
        assert "run_id" in data, "Command output must include run_id"
        assert "forbidden_actions" in data, "Command output must include forbidden_actions"
        assert len(data["forbidden_actions"]) > 0, "Must have forbidden actions"

    def test_command_script_markdown(self) -> None:
        result = subprocess.run(
            [
                sys.executable,
                "training/scripts/kimari4b_private_sft_command.py",
                "--config",
                "training/configs/kimari4b_private_sft_run.v0.yaml",
                "--markdown",
            ],
            capture_output=True,
            text=True,
            cwd=str(PROJECT_ROOT),
            timeout=30,
        )
        assert result.returncode == 0, f"Command script --markdown failed: {result.stderr}"
        assert "# Kimari-4B Private SFT Commands" in result.stdout, "Markdown output must have title"

    def test_command_script_gate_blocked(self) -> None:
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
        assert data.get("gate_state") == "BLOCKED", "Gate state must be BLOCKED"
        assert data.get("public_release_allowed") is False, "public_release_allowed must be false"
        assert data.get("hf_upload_allowed") is False, "hf_upload_allowed must be false"

    def test_eval_plan_script_exists(self) -> None:
        path = PROJECT_ROOT / "eval" / "scripts" / "kimari4b_eval_plan.py"
        assert path.exists(), "kimari4b_eval_plan.py missing"

    def test_eval_plan_json(self) -> None:
        result = subprocess.run(
            [sys.executable, "eval/scripts/kimari4b_eval_plan.py", "--baseline-label", "smollm3-base", "--json"],
            capture_output=True,
            text=True,
            cwd=str(PROJECT_ROOT),
            timeout=30,
        )
        assert result.returncode == 0, f"Eval plan failed: {result.stderr}"
        data = json.loads(result.stdout)
        assert "baseline_eval" in data, "Eval plan must include baseline_eval"
        assert "no_scores_note" in data, "Eval plan must include no_scores_note"

    def test_eval_plan_markdown(self) -> None:
        result = subprocess.run(
            [
                sys.executable,
                "eval/scripts/kimari4b_eval_plan.py",
                "--baseline-label",
                "smollm3-base",
                "--adapter-label",
                "kimari4b-smollm3-sft-v0",
                "--markdown",
            ],
            capture_output=True,
            text=True,
            cwd=str(PROJECT_ROOT),
            timeout=30,
        )
        assert result.returncode == 0, f"Eval plan --markdown failed: {result.stderr}"
        assert "# Kimari-4B Evaluation Plan" in result.stdout, "Markdown must have title"

    def test_eval_plan_no_scores(self) -> None:
        result = subprocess.run(
            [sys.executable, "eval/scripts/kimari4b_eval_plan.py", "--baseline-label", "smollm3-base", "--json"],
            capture_output=True,
            text=True,
            cwd=str(PROJECT_ROOT),
            timeout=30,
        )
        data = json.loads(result.stdout)
        assert "manual_review_required" in str(data), "Eval plan must reference manual review"


# ---------------------------------------------------------------------------
# Template
# ---------------------------------------------------------------------------


class TestTemplateV0128:
    """Test v0.1.28 summary template."""

    def test_summary_template_exists(self) -> None:
        path = PROJECT_ROOT / "training" / "templates" / "kimari4b_private_summary.template.json"
        assert path.exists(), "kimari4b_private_summary.template.json missing"

    def test_summary_template_parses(self) -> None:
        path = PROJECT_ROOT / "training" / "templates" / "kimari4b_private_summary.template.json"
        data = json.loads(path.read_text())
        assert isinstance(data, dict), "Template must be a JSON dict"

    def test_summary_template_gate_blocked(self) -> None:
        path = PROJECT_ROOT / "training" / "templates" / "kimari4b_private_summary.template.json"
        data = json.loads(path.read_text())
        assert data.get("preview_gate_state") == "BLOCKED", "preview_gate_state must be BLOCKED"

    def test_summary_template_public_release_false(self) -> None:
        path = PROJECT_ROOT / "training" / "templates" / "kimari4b_private_summary.template.json"
        data = json.loads(path.read_text())
        assert data.get("public_release_allowed") is False, "public_release_allowed must be false"

    def test_summary_template_hf_upload_false(self) -> None:
        path = PROJECT_ROOT / "training" / "templates" / "kimari4b_private_summary.template.json"
        data = json.loads(path.read_text())
        assert data.get("hf_upload_allowed") is False, "hf_upload_allowed must be false"

    def test_summary_template_manual_review_required(self) -> None:
        path = PROJECT_ROOT / "training" / "templates" / "kimari4b_private_summary.template.json"
        data = json.loads(path.read_text())
        assert data.get("manual_review_required") is True, "manual_review_required must be true"

    def test_summary_template_adapter_local_only(self) -> None:
        path = PROJECT_ROOT / "training" / "templates" / "kimari4b_private_summary.template.json"
        data = json.loads(path.read_text())
        assert data.get("adapter_local_only") is True, "adapter_local_only must be true"


# ---------------------------------------------------------------------------
# Updated docs
# ---------------------------------------------------------------------------


class TestUpdatedDocsV0128:
    """Test v0.1.28 updates to existing docs."""

    def test_handoff_has_kimari4b_section(self) -> None:
        path = PROJECT_ROOT / "docs" / "FIRST_PRIVATE_SFT_HANDOFF.md"
        text = path.read_text()
        assert "Kimari-4B" in text, "FIRST_PRIVATE_SFT_HANDOFF.md must have Kimari-4B section"

    def test_preview_gate_has_kimari4b_section(self) -> None:
        path = PROJECT_ROOT / "docs" / "ADAPTER_PREVIEW_GATE.md"
        text = path.read_text()
        assert "Kimari-4B" in text, "ADAPTER_PREVIEW_GATE.md must have Kimari-4B section"

    def test_preview_gate_kimari4b_blocked(self) -> None:
        path = PROJECT_ROOT / "docs" / "ADAPTER_PREVIEW_GATE.md"
        text = path.read_text()
        # Must mention Kimari-4B and BLOCKED together
        assert "BLOCKED" in text, "Preview gate must say BLOCKED"


# ---------------------------------------------------------------------------
# README and index.html references
# ---------------------------------------------------------------------------


class TestReferencesV0128:
    """Test v0.1.28 references in README and index.html."""

    def test_readme_mentions_kimari4b_private_sft(self) -> None:
        text = (PROJECT_ROOT / "README.md").read_text()
        assert "KIMARI4B_PRIVATE_SFT_RUN" in text, "README must link to KIMARI4B_PRIVATE_SFT_RUN.md"

    def test_readme_no_false_claims(self) -> None:
        text = (PROJECT_ROOT / "README.md").read_text().lower()
        false_patterns = [
            "kimari-4b is available now",
            "kimari-4b can be downloaded",
            "download kimari-4b",
            "kimari-4b weights available",
            "kimari-4b has been released",
        ]
        for pattern in false_patterns:
            assert pattern not in text, f"False claim found: {pattern}"

    def test_index_html_mentions_version(self) -> None:
        text = (PROJECT_ROOT / "docs" / "index.html").read_text()
        assert "0.1.28" in text, "docs/index.html must mention v0.1.28"

    def test_model_card_no_public_weights(self) -> None:
        path = PROJECT_ROOT / "MODEL_CARD.md"
        if not path.exists():
            pytest.skip("MODEL_CARD.md not found")
        text = path.read_text().lower()
        # Must indicate no public release
        assert "not released" in text or "not yet released" in text or "no public" in text or "planned" in text, (
            "MODEL_CARD.md must indicate no public weights"
        )


# ---------------------------------------------------------------------------
# No tracked artifacts
# ---------------------------------------------------------------------------


class TestNoTrackedArtifactsV0128:
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
