"""Release validation tests for Kimari Local AI v0.1.22-alpha.

Tests cover:
- Version consistency (0.1.22-alpha)
- MODEL_CARD checklist and version history fixes
- Baseline eval plan
- Adapter artifact policy
- Private SFT run config (public_release_allowed=false, hf_upload_allowed=false)
- Private SFT dry-run validation script
- Build v0 pipeline dry-run
- Compare runs tool
- .gitignore blocks adapter/weights/GGUF
- Adapter preview gate (default BLOCKED)
- KimariFit --run-id, --model-label, --output support
- Release check passes
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import yaml

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def _run_script(*args: str, timeout: int = 60) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, *args],
        capture_output=True,
        text=True,
        timeout=timeout,
        cwd=str(PROJECT_ROOT),
    )


# ─── Version Consistency ────────────────────────────────────────────────


class TestVersion:
    def test_version_in_init(self):
        from kimari import __version__

        assert __version__ == "0.1.22-alpha"

    def test_version_in_pyproject(self):
        text = (PROJECT_ROOT / "pyproject.toml").read_text()
        assert 'version = "0.1.22-alpha"' in text


# ─── MODEL_CARD Fixes ──────────────────────────────────────────────────


class TestModelCardFixes:
    def test_model_card_has_seed_dataset_in_progress(self):
        content = (PROJECT_ROOT / "MODEL_CARD.md").read_text()
        assert "In Progress" in content, "MODEL_CARD should show seed dataset as In Progress"

    def test_model_card_has_full_dataset_not_started(self):
        content = (PROJECT_ROOT / "MODEL_CARD.md").read_text()
        assert "Full training dataset curated" in content, "MODEL_CARD should mention full training dataset"

    def test_model_card_version_history_0120(self):
        content = (PROJECT_ROOT / "MODEL_CARD.md").read_text()
        assert "0.1.22-alpha" in content, "MODEL_CARD version history should include 0.1.22-alpha"

    def test_model_card_says_no_weights(self):
        content = (PROJECT_ROOT / "MODEL_CARD.md").read_text().lower()
        assert "not been released" in content or "not released" in content or "no weights" in content


# ─── Baseline Eval Plan ─────────────────────────────────────────────────


class TestBaselineEvalPlan:
    def test_baseline_eval_plan_exists(self):
        assert (PROJECT_ROOT / "docs" / "BASELINE_EVAL_PLAN.md").exists()

    def test_baseline_eval_plan_content(self):
        content = (PROJECT_ROOT / "docs" / "BASELINE_EVAL_PLAN.md").read_text().lower()
        assert "smollm3" in content
        assert "baseline" in content


# ─── Adapter Artifact Policy ────────────────────────────────────────────


class TestAdapterArtifactPolicy:
    def test_adapter_artifact_policy_exists(self):
        assert (PROJECT_ROOT / "docs" / "ADAPTER_ARTIFACT_POLICY.md").exists()

    def test_adapter_artifact_policy_content(self):
        content = (PROJECT_ROOT / "docs" / "ADAPTER_ARTIFACT_POLICY.md").read_text().lower()
        assert "safetensors" in content or "adapter" in content
        assert "gitignore" in content or "commit" in content


# ─── Private Training Runbook ──────────────────────────────────────────


class TestPrivateTrainingRunbook:
    def test_private_training_runbook_exists(self):
        assert (PROJECT_ROOT / "docs" / "PRIVATE_TRAINING_RUNBOOK.md").exists()

    def test_private_training_runbook_content(self):
        content = (PROJECT_ROOT / "docs" / "PRIVATE_TRAINING_RUNBOOK.md").read_text().lower()
        assert "sft" in content or "private" in content


# ─── Adapter Preview Gate ──────────────────────────────────────────────


class TestAdapterPreviewGate:
    def test_adapter_preview_gate_exists(self):
        assert (PROJECT_ROOT / "docs" / "ADAPTER_PREVIEW_GATE.md").exists()

    def test_adapter_preview_gate_default_blocked(self):
        content = (PROJECT_ROOT / "docs" / "ADAPTER_PREVIEW_GATE.md").read_text()
        assert "BLOCKED" in content, "ADAPTER_PREVIEW_GATE must mention BLOCKED as default"


# ─── Private SFT Run Config ────────────────────────────────────────────


class TestPrivateSFTRunConfig:
    def test_private_sft_run_config_exists(self):
        assert (PROJECT_ROOT / "training" / "configs" / "private_sft_run.v0.yaml").exists()

    def test_private_sft_run_public_release_not_allowed(self):
        content = (PROJECT_ROOT / "training" / "configs" / "private_sft_run.v0.yaml").read_text()
        assert "public_release_allowed: false" in content

    def test_private_sft_run_hf_upload_not_allowed(self):
        content = (PROJECT_ROOT / "training" / "configs" / "private_sft_run.v0.yaml").read_text()
        assert "hf_upload_allowed: false" in content

    def test_private_sft_run_parses_as_yaml(self):
        content = (PROJECT_ROOT / "training" / "configs" / "private_sft_run.v0.yaml").read_text()
        data = yaml.safe_load(content)
        assert data.get("run_id") is not None
        assert data.get("status") == "planned"
        assert data.get("base_model") is not None


# ─── Private SFT Dry-Run Script ─────────────────────────────────────────


class TestRunPrivateSFTDryrun:
    def test_script_exists(self):
        assert (PROJECT_ROOT / "training" / "scripts" / "run_private_sft_dryrun.py").exists()

    def test_script_help(self):
        result = _run_script(
            str(PROJECT_ROOT / "training" / "scripts" / "run_private_sft_dryrun.py"),
            "--help",
        )
        assert result.returncode == 0

    def test_script_json_output(self):
        result = _run_script(
            str(PROJECT_ROOT / "training" / "scripts" / "run_private_sft_dryrun.py"),
            "--run-config",
            str(PROJECT_ROOT / "training" / "configs" / "private_sft_run.v0.yaml"),
            "--json",
        )
        # Script may return non-zero if dataset is not built yet (readiness_status != ready)
        # That's expected — we just need valid JSON output
        data = json.loads(result.stdout)
        assert isinstance(data, dict)
        # Key validations: public release and HF upload are blocked
        checks = data.get("checks", {})
        assert checks.get("public_release_allowed", {}).get("status") == "PASS"
        assert checks.get("hf_upload_allowed", {}).get("status") == "PASS"


# ─── Build V0 Pipeline ──────────────────────────────────────────────────


class TestBuildV0Pipeline:
    def test_script_exists(self):
        assert (PROJECT_ROOT / "training" / "scripts" / "build_v0_pipeline.py").exists()

    def test_script_help(self):
        result = _run_script(
            str(PROJECT_ROOT / "training" / "scripts" / "build_v0_pipeline.py"),
            "--help",
        )
        assert result.returncode == 0

    def test_pipeline_dry_run(self):
        result = _run_script(
            str(PROJECT_ROOT / "training" / "scripts" / "build_v0_pipeline.py"),
            "--dry-run",
            "--output-dir",
            "/tmp/kimari-v0-pipeline-test",
            "--json",
        )
        assert result.returncode == 0, (
            f"build_v0_pipeline.py --dry-run --json failed:\n{result.stdout}\n{result.stderr}"
        )


# ─── Compare Runs ───────────────────────────────────────────────────────


class TestCompareRuns:
    def test_script_exists(self):
        assert (PROJECT_ROOT / "eval" / "scripts" / "compare_runs.py").exists()

    def test_compare_runs_json(self):
        result = _run_script(
            str(PROJECT_ROOT / "eval" / "scripts" / "compare_runs.py"),
            "--baseline",
            str(PROJECT_ROOT / "tests" / "fixtures" / "baseline_eval_result.json"),
            "--candidate",
            str(PROJECT_ROOT / "tests" / "fixtures" / "adapter_eval_result.json"),
            "--json",
        )
        assert result.returncode == 0, f"compare_runs.py --json failed:\n{result.stdout}\n{result.stderr}"
        data = json.loads(result.stdout)
        assert "comparison_status" in data or "status" in data


# ─── Gitignore ──────────────────────────────────────────────────────────


class TestGitignore:
    def test_gitignore_blocks_safetensors(self):
        content = (PROJECT_ROOT / ".gitignore").read_text()
        assert "*.safetensors" in content

    def test_gitignore_blocks_gguf(self):
        content = (PROJECT_ROOT / ".gitignore").read_text()
        assert "*.gguf" in content

    def test_gitignore_blocks_training_adapters(self):
        content = (PROJECT_ROOT / ".gitignore").read_text()
        assert "training/adapters/" in content

    def test_gitignore_blocks_pt_pth_ckpt(self):
        content = (PROJECT_ROOT / ".gitignore").read_text()
        assert "*.pt" in content
        assert "*.ckpt" in content

    def test_gitignore_blocks_wandb(self):
        content = (PROJECT_ROOT / ".gitignore").read_text()
        assert "wandb/" in content


# ─── KimariFit Improvements ─────────────────────────────────────────────


class TestKimariFitImprovements:
    def test_kimarifit_run_id(self):
        result = _run_script(
            str(PROJECT_ROOT / "eval" / "kimarifit.py"),
            "--prompts",
            str(PROJECT_ROOT / "eval" / "kimarifit_prompts.jsonl"),
            "--dry-run",
            "--run-id",
            "test-run-001",
            "--json",
        )
        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert data.get("run_id") == "test-run-001"

    def test_kimarifit_model_label(self):
        result = _run_script(
            str(PROJECT_ROOT / "eval" / "kimarifit.py"),
            "--prompts",
            str(PROJECT_ROOT / "eval" / "kimarifit_prompts.jsonl"),
            "--dry-run",
            "--model-label",
            "smollm3-base",
            "--json",
        )
        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert data.get("model_label") == "smollm3-base"

    def test_kimarifit_score_status(self):
        result = _run_script(
            str(PROJECT_ROOT / "eval" / "kimarifit.py"),
            "--prompts",
            str(PROJECT_ROOT / "eval" / "kimarifit_prompts.jsonl"),
            "--dry-run",
            "--json",
        )
        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert data.get("score_status") == "manual_review_required"

    def test_kimarifit_output_plan(self):
        import tempfile

        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "plan.json"
            result = _run_script(
                str(PROJECT_ROOT / "eval" / "kimarifit.py"),
                "--prompts",
                str(PROJECT_ROOT / "eval" / "kimarifit_prompts.jsonl"),
                "--dry-run",
                "--score-plan",
                "--output",
                str(output_path),
                "--json",
            )
            assert result.returncode == 0
            assert output_path.exists(), "Plan file should be written"
            data = json.loads(output_path.read_text())
            assert data["total_prompts"] > 0


# ─── Eval Baseline README ──────────────────────────────────────────────


class TestEvalBaseline:
    def test_eval_baseline_readme_exists(self):
        assert (PROJECT_ROOT / "eval" / "baseline" / "README.md").exists()


# ─── Content Integrity ──────────────────────────────────────────────────


class TestContentIntegrity:
    def test_no_gguf_tracked(self):
        result = subprocess.run(
            ["git", "ls-files"],
            capture_output=True,
            text=True,
            timeout=30,
            cwd=str(PROJECT_ROOT),
        )
        tracked = result.stdout.strip().split("\n") if result.stdout.strip() else []
        gguf_files = [f for f in tracked if f.lower().endswith(".gguf")]
        assert gguf_files == [], f"GGUF files tracked in git: {gguf_files}"

    def test_no_weight_files_tracked(self):
        result = subprocess.run(
            ["git", "ls-files"],
            capture_output=True,
            text=True,
            timeout=30,
            cwd=str(PROJECT_ROOT),
        )
        tracked = result.stdout.strip().split("\n") if result.stdout.strip() else []
        weight_exts = [".safetensors", ".pt", ".pth", ".ckpt"]
        weight_files = [f for f in tracked if any(f.endswith(ext) for ext in weight_exts)]
        assert weight_files == [], f"Weight files tracked in git: {weight_files}"


# ─── Changelog and Roadmap ─────────────────────────────────────────────


class TestChangelogAndRoadmap:
    def test_changelog_has_v0120(self):
        content = (PROJECT_ROOT / "CHANGELOG.md").read_text()
        assert "0.1.22-alpha" in content

    def test_roadmap_has_v0120(self):
        content = (PROJECT_ROOT / "ROADMAP.md").read_text()
        assert "0.1.22" in content


# ─── Release Check ──────────────────────────────────────────────────────


class TestReleaseCheck:
    def test_release_check_passes(self):
        result = subprocess.run(
            [sys.executable, "scripts/release/check-release.py"],
            capture_output=True,
            text=True,
            timeout=120,
            cwd=str(PROJECT_ROOT),
        )
        assert result.returncode == 0, f"check-release.py failed:\n{result.stdout}\n{result.stderr}"
