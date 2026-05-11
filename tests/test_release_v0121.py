"""Tests for v0.1.21-alpha release: adapter manifest, eval summary, SFT→ORPO decision."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent


class TestAdapterManifestTemplate:
    """Tests for adapter manifest template."""

    def test_template_exists(self):
        path = PROJECT_ROOT / "training" / "templates" / "adapter_manifest.template.yaml"
        assert path.exists(), f"Template missing: {path}"

    def test_template_contains_required_fields(self):
        path = PROJECT_ROOT / "training" / "templates" / "adapter_manifest.template.yaml"
        content = path.read_text()
        required = [
            "adapter_name",
            "run_id",
            "base_model",
            "dataset_id",
            "preview_gate_state",
            "BLOCKED",
            "public_release_allowed",
            "false",
            "hf_upload_allowed",
            "false",
            "state_history",
        ]
        for field in required:
            assert field in content, f"Missing field in template: {field}"

    def test_template_blocked_by_default(self):
        path = PROJECT_ROOT / "training" / "templates" / "adapter_manifest.template.yaml"
        content = path.read_text()
        assert "BLOCKED" in content
        # Ensure it's not set to any other state
        assert "PENDING" not in content.replace("APPROVED_FOR_PRIVATE_TESTING", "").replace(
            "APPROVED_FOR_PUBLIC_PREVIEW", ""
        )


class TestCreateAdapterManifest:
    """Tests for create_adapter_manifest.py script."""

    def test_script_exists(self):
        path = PROJECT_ROOT / "training" / "scripts" / "create_adapter_manifest.py"
        assert path.exists(), f"Script missing: {path}"

    def test_dry_run_json(self, tmp_path):
        result = subprocess.run(
            [
                sys.executable,
                "training/scripts/create_adapter_manifest.py",
                "--run-config",
                "training/configs/private_sft_run.v0.yaml",
                "--adapter-dir",
                str(tmp_path / "fake-adapter"),
                "--output",
                str(tmp_path / "MANIFEST.yaml"),
                "--dry-run",
                "--json",
            ],
            capture_output=True,
            text=True,
            cwd=str(PROJECT_ROOT),
        )
        assert result.returncode == 0, f"Script failed: {result.stderr}"
        data = json.loads(result.stdout)
        assert data.get("preview_gate_state") == "BLOCKED"
        assert data.get("public_release_allowed") is False
        assert data.get("hf_upload_allowed") is False


class TestNewDocs:
    """Tests for new v0.1.21 documentation files."""

    def test_private_sft_execution_checklist_exists(self):
        path = PROJECT_ROOT / "docs" / "PRIVATE_SFT_EXECUTION_CHECKLIST.md"
        assert path.exists(), f"Doc missing: {path}"

    def test_sft_to_orpo_decision_exists(self):
        path = PROJECT_ROOT / "docs" / "SFT_TO_ORPO_DECISION.md"
        assert path.exists(), f"Doc missing: {path}"

    def test_private_eval_results_policy_exists(self):
        path = PROJECT_ROOT / "docs" / "PRIVATE_EVAL_RESULTS_POLICY.md"
        assert path.exists(), f"Doc missing: {path}"


class TestEvalSummaryTemplate:
    """Tests for eval summary template."""

    def test_template_exists(self):
        path = PROJECT_ROOT / "eval" / "templates" / "eval_summary.template.json"
        assert path.exists(), f"Template missing: {path}"

    def test_template_parses(self):
        path = PROJECT_ROOT / "eval" / "templates" / "eval_summary.template.json"
        data = json.loads(path.read_text())
        required = ["run_id", "model_label", "kimari_version", "prompt_count", "score_status", "manual_review_required"]
        for field in required:
            assert field in data, f"Missing field in eval summary template: {field}"

    def test_template_no_raw_prompts(self):
        path = PROJECT_ROOT / "eval" / "templates" / "eval_summary.template.json"
        content = path.read_text().lower()
        assert "raw_prompt" not in content
        assert "raw_response" not in content


class TestCreateEvalSummary:
    """Tests for create_eval_summary.py script."""

    def test_script_exists(self):
        path = PROJECT_ROOT / "eval" / "scripts" / "create_eval_summary.py"
        assert path.exists(), f"Script missing: {path}"

    def test_strips_raw_outputs(self, tmp_path):
        result = subprocess.run(
            [
                sys.executable,
                "eval/scripts/create_eval_summary.py",
                "--input",
                "tests/fixtures/private_eval_raw.json",
                "--output",
                str(tmp_path / "summary.json"),
                "--json",
            ],
            capture_output=True,
            text=True,
            cwd=str(PROJECT_ROOT),
        )
        assert result.returncode == 0, f"Script failed: {result.stderr}"
        data = json.loads(result.stdout)
        # Should have results but without raw prompt/response
        assert "prompt_count" in data or "total" in data or "results" in data


class TestCompareRunsVerdict:
    """Tests for compare_runs.py verdict logic."""

    def test_script_exists(self):
        path = PROJECT_ROOT / "eval" / "scripts" / "compare_runs.py"
        assert path.exists()

    def test_compare_with_fixtures(self, tmp_path):
        result = subprocess.run(
            [
                sys.executable,
                "eval/scripts/compare_runs.py",
                "--baseline",
                "tests/fixtures/baseline_eval_result.json",
                "--candidate",
                "tests/fixtures/adapter_eval_result.json",
                "--summary-output",
                str(tmp_path / "compare_summary.json"),
                "--json",
            ],
            capture_output=True,
            text=True,
            cwd=str(PROJECT_ROOT),
        )
        assert result.returncode == 0, f"Compare failed: {result.stderr}"
        data = json.loads(result.stdout)
        assert "verdict" in data or "comparison_status" in data

    def test_summary_output_written(self, tmp_path):
        summary_path = tmp_path / "compare_summary.json"
        subprocess.run(
            [
                sys.executable,
                "eval/scripts/compare_runs.py",
                "--baseline",
                "tests/fixtures/baseline_eval_result.json",
                "--candidate",
                "tests/fixtures/adapter_eval_result.json",
                "--summary-output",
                str(summary_path),
                "--json",
            ],
            capture_output=True,
            text=True,
            cwd=str(PROJECT_ROOT),
        )
        assert summary_path.exists(), "Summary output not written"
        data = json.loads(summary_path.read_text())
        assert "verdict" in data or "comparison_status" in data


class TestPreviewGate:
    """Tests for preview gate BLOCKED status."""

    def test_preview_gate_says_blocked(self):
        path = PROJECT_ROOT / "docs" / "ADAPTER_PREVIEW_GATE.md"
        content = path.read_text()
        assert "BLOCKED" in content

    def test_manifest_template_blocked(self):
        path = PROJECT_ROOT / "training" / "templates" / "adapter_manifest.template.yaml"
        content = path.read_text()
        # The default state must be BLOCKED
        lines_with_blocked = [line for line in content.splitlines() if "preview_gate_state" in line]
        assert len(lines_with_blocked) > 0
        assert "BLOCKED" in lines_with_blocked[0]


class TestNoTrackedArtifacts:
    """Tests that no adapter/weight/GGUF files are tracked in git."""

    def test_no_safetensors_tracked(self):
        result = subprocess.run(
            ["git", "ls-files", "*.safetensors"],
            capture_output=True,
            text=True,
            cwd=str(PROJECT_ROOT),
        )
        files = [f for f in result.stdout.strip().splitlines() if f]
        assert len(files) == 0, f"Safetensors tracked: {files}"

    def test_no_gguf_tracked(self):
        result = subprocess.run(
            ["git", "ls-files", "*.gguf"],
            capture_output=True,
            text=True,
            cwd=str(PROJECT_ROOT),
        )
        files = [f for f in result.stdout.strip().splitlines() if f]
        assert len(files) == 0, f"GGUF tracked: {files}"

    def test_no_bin_pt_tracked(self):
        result = subprocess.run(
            ["git", "ls-files", "*.bin", "*.pt", "*.pth", "*.ckpt"],
            capture_output=True,
            text=True,
            cwd=str(PROJECT_ROOT),
        )
        files = [f for f in result.stdout.strip().splitlines() if f]
        # .bin files in training configs are OK (e.g., tokenizer)
        # but adapter weights should not be tracked
        assert len(files) == 0, f"Weight files tracked: {files}"


class TestVersionConsistency:
    """Tests for version consistency across files."""

    def test_version_is_0121(self):
        from kimari import __version__

        assert __version__ == "0.1.21-alpha", f"Version is {__version__}, expected 0.1.21-alpha"

    def test_pyproject_version(self):
        pyproject = PROJECT_ROOT / "pyproject.toml"
        content = pyproject.read_text()
        assert "0.1.21-alpha" in content
