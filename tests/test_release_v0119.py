"""Release validation tests for Kimari Local AI v0.1.19-alpha.

Tests cover:
- Version consistency (0.1.19-alpha)
- Base model acceptance (SmolLM3-3B as private training candidate)
- Dataset v0 (SFT, preference, eval holdout)
- Training readiness validation
- KimariFit scoring plan and dimensions
- Summarize results script
- v0 training config examples (SFT LoRA, ORPO)
- Documentation (FIRST_PRIVATE_TRAINING_RUN, HF_PLACEHOLDER_PLAN, BASE_MODEL_ACCEPTANCE)
- Model card and decision record updates
- Content integrity (no GGUF, no false claims, no forbidden strings)
- Changelog and roadmap updates
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

        assert __version__ == "0.1.19-alpha"

    def test_version_in_pyproject(self):
        text = (PROJECT_ROOT / "pyproject.toml").read_text()
        assert 'version = "0.1.19-alpha"' in text


# ─── Base Model Acceptance ─────────────────────────────────────────────


class TestBaseModelAcceptance:
    def test_base_model_acceptance_doc_exists(self):
        assert (PROJECT_ROOT / "docs" / "BASE_MODEL_ACCEPTANCE.md").exists()

    def test_base_model_acceptance_contains_smollm3(self):
        content = (PROJECT_ROOT / "docs" / "BASE_MODEL_ACCEPTANCE.md").read_text()
        assert "SmolLM3" in content
        assert "private" in content.lower()

    def test_base_candidates_smollm3_accepted(self):
        content = (PROJECT_ROOT / "training" / "configs" / "base_candidates.yaml").read_text()
        data = yaml.safe_load(content)
        candidates = data.get("candidates", [])
        smollm3 = next((c for c in candidates if c["id"] == "smollm3-3b"), None)
        assert smollm3 is not None, "SmolLM3-3B not found in base_candidates.yaml"
        assert smollm3["status"] == "accepted_private_training_candidate"
        assert smollm3["selected_for_private_sft"] is True
        assert smollm3["selected_for_public_release"] is False

    def test_base_candidates_smollm3_has_required_fields(self):
        content = (PROJECT_ROOT / "training" / "configs" / "base_candidates.yaml").read_text()
        data = yaml.safe_load(content)
        candidates = data.get("candidates", [])
        smollm3 = next((c for c in candidates if c["id"] == "smollm3-3b"), None)
        assert smollm3 is not None
        assert "license_review_status" in smollm3
        assert "hf_url" in smollm3
        assert "last_reviewed_date" in smollm3

    def test_no_public_release_approved(self):
        content = (PROJECT_ROOT / "training" / "configs" / "base_candidates.yaml").read_text()
        data = yaml.safe_load(content)
        candidates = data.get("candidates", [])
        for c in candidates:
            assert c.get("selected_for_public_release") is False, (
                f"{c['id']} has selected_for_public_release=True — not allowed yet"
            )

    def test_model_decision_record_accepted(self):
        content = (PROJECT_ROOT / "docs" / "MODEL_DECISION_RECORD.md").read_text()
        assert "Accepted for first private training run" in content


# ─── Dataset v0 ─────────────────────────────────────────────────────────


class TestDatasetV0SFT:
    def test_sft_v0_jsonl_exists(self):
        assert (PROJECT_ROOT / "dataset" / "v0" / "sft_v0.jsonl").exists()

    def test_sft_v0_validates(self):
        path = PROJECT_ROOT / "dataset" / "v0" / "sft_v0.jsonl"
        lines = path.read_text().strip().splitlines()
        records = []
        for line in lines:
            record = json.loads(line)
            assert "source" in record, "missing 'source' field"
            assert "license" in record, "missing 'license' field"
            records.append(record)
        assert len(records) >= 50, f"Expected >= 50 SFT records, got {len(records)}"


class TestDatasetV0Preference:
    def test_preference_v0_jsonl_exists(self):
        assert (PROJECT_ROOT / "dataset" / "v0" / "preference_v0.jsonl").exists()

    def test_preference_v0_validates(self):
        path = PROJECT_ROOT / "dataset" / "v0" / "preference_v0.jsonl"
        lines = path.read_text().strip().splitlines()
        records = []
        for line in lines:
            record = json.loads(line)
            assert "prompt" in record, "missing 'prompt' field"
            assert "chosen" in record, "missing 'chosen' field"
            assert "rejected" in record, "missing 'rejected' field"
            assert "source" in record, "missing 'source' field"
            assert "license" in record, "missing 'license' field"
            records.append(record)
        assert len(records) >= 20, f"Expected >= 20 preference records, got {len(records)}"


class TestDatasetV0Holdout:
    def test_eval_holdout_jsonl_exists(self):
        assert (PROJECT_ROOT / "dataset" / "v0" / "eval_holdout.jsonl").exists()

    def test_eval_holdout_validates(self):
        path = PROJECT_ROOT / "dataset" / "v0" / "eval_holdout.jsonl"
        lines = path.read_text().strip().splitlines()
        records = []
        for line in lines:
            record = json.loads(line)
            assert "id" in record, "missing 'id' field"
            assert "category" in record, "missing 'category' field"
            assert "prompt" in record, "missing 'prompt' field"
            assert "expected_traits" in record, "missing 'expected_traits' field"
            assert "forbidden_traits" in record, "missing 'forbidden_traits' field"
            assert isinstance(record["expected_traits"], list), "expected_traits must be a list"
            assert isinstance(record["forbidden_traits"], list), "forbidden_traits must be a list"
            records.append(record)
        assert len(records) >= 10, f"Expected >= 10 holdout records, got {len(records)}"

    def test_eval_holdout_not_in_sft(self):
        """Holdout examples must not appear in SFT training data."""
        holdout_path = PROJECT_ROOT / "dataset" / "v0" / "eval_holdout.jsonl"
        sft_path = PROJECT_ROOT / "dataset" / "v0" / "sft_v0.jsonl"
        holdout_ids = set()
        sft_ids = set()
        for line in holdout_path.read_text().strip().splitlines():
            record = json.loads(line)
            holdout_ids.add(record.get("id", ""))
        for line in sft_path.read_text().strip().splitlines():
            record = json.loads(line)
            sft_ids.add(record.get("id", ""))
        overlap = holdout_ids & sft_ids
        assert len(overlap) == 0, f"Holdout IDs found in SFT: {overlap}"


class TestDatasetV0Readme:
    def test_dataset_v0_readme_exists(self):
        assert (PROJECT_ROOT / "dataset" / "v0" / "README.md").exists()


# ─── Training Readiness Validation ─────────────────────────────────────


class TestValidateTrainingReady:
    def test_validate_training_ready_script_exists(self):
        assert (PROJECT_ROOT / "training" / "scripts" / "validate_training_ready.py").exists()

    def test_validate_training_ready_help(self):
        result = _run_script(
            str(PROJECT_ROOT / "training" / "scripts" / "validate_training_ready.py"),
            "--help",
        )
        assert result.returncode == 0

    def test_validate_training_ready_json(self):
        result = _run_script(
            str(PROJECT_ROOT / "training" / "scripts" / "validate_training_ready.py"),
            "--base-config",
            str(PROJECT_ROOT / "training" / "configs" / "base_candidates.yaml"),
            "--sft",
            str(PROJECT_ROOT / "dataset" / "v0" / "sft_v0.jsonl"),
            "--preference",
            str(PROJECT_ROOT / "dataset" / "v0" / "preference_v0.jsonl"),
            "--holdout",
            str(PROJECT_ROOT / "dataset" / "v0" / "eval_holdout.jsonl"),
            "--json",
        )
        assert result.returncode == 0, f"validate_training_ready.py --json failed:\n{result.stdout}\n{result.stderr}"
        data = json.loads(result.stdout)
        assert data.get("all_pass") is True, f"Training readiness validation failed: {data}"
        assert "checks" in data


# ─── KimariFit Scoring Plan ────────────────────────────────────────────


class TestKimariFitScoring:
    def test_kimarifit_score_plan(self):
        result = _run_script(
            str(PROJECT_ROOT / "eval" / "kimarifit.py"),
            "--prompts",
            str(PROJECT_ROOT / "eval" / "kimarifit_prompts.jsonl"),
            "--dry-run",
            "--score-plan",
            "--json",
        )
        assert result.returncode == 0, f"kimarifit --score-plan --json failed:\n{result.stdout}\n{result.stderr}"
        data = json.loads(result.stdout)
        assert "scoring_dimensions" in data or "dimensions" in data or "score_plan" in data

    def test_kimarifit_dimensions_json_exists(self):
        assert (PROJECT_ROOT / "eval" / "scoring" / "kimarifit_dimensions.json").exists()

    def test_kimarifit_dimensions_valid(self):
        path = PROJECT_ROOT / "eval" / "scoring" / "kimarifit_dimensions.json"
        data = json.loads(path.read_text())
        assert "dimensions" in data or isinstance(data, list)
        dims = data["dimensions"] if isinstance(data, dict) else data
        assert len(dims) >= 9, f"Expected >= 9 scoring dimensions, got {len(dims)}"
        for dim in dims:
            assert "name" in dim or "id" in dim, f"Dimension missing name/id: {dim}"
            assert "max_score" in dim, f"Dimension missing max_score: {dim}"
            assert dim["max_score"] == 5, f"Dimension max_score should be 5, got {dim['max_score']}"


# ─── Summarize Results ──────────────────────────────────────────────────


class TestSummarizeResults:
    def test_summarize_results_script_exists(self):
        assert (PROJECT_ROOT / "eval" / "scripts" / "summarize_results.py").exists()

    def test_summarize_results_help(self):
        result = _run_script(
            str(PROJECT_ROOT / "eval" / "scripts" / "summarize_results.py"),
            "--help",
        )
        assert result.returncode == 0

    def test_summarize_results_on_fixture(self):
        fixture = PROJECT_ROOT / "tests" / "fixtures" / "synthetic_eval_result.json"
        if not fixture.exists():
            return  # Skip if fixture doesn't exist yet
        result = _run_script(
            str(PROJECT_ROOT / "eval" / "scripts" / "summarize_results.py"),
            "--input",
            str(fixture),
            "--json",
        )
        assert result.returncode == 0, f"summarize_results.py failed:\n{result.stdout}\n{result.stderr}"
        data = json.loads(result.stdout)
        assert isinstance(data, dict)


# ─── v0 Training Config Examples ────────────────────────────────────────


class TestTrainingConfigs:
    def test_sft_lora_v0_config_exists(self):
        assert (PROJECT_ROOT / "training" / "configs" / "kimari_sft_lora.v0.example.yaml").exists()

    def test_sft_lora_v0_config_content(self):
        content = (PROJECT_ROOT / "training" / "configs" / "kimari_sft_lora.v0.example.yaml").read_text()
        assert "SmolLM3" in content
        assert "lora_r" in content or "lora" in content.lower()
        assert "example" in content.lower() or "starting point" in content.lower()

    def test_orpo_v0_config_exists(self):
        assert (PROJECT_ROOT / "training" / "configs" / "kimari_orpo.v0.example.yaml").exists()

    def test_orpo_v0_config_content(self):
        content = (PROJECT_ROOT / "training" / "configs" / "kimari_orpo.v0.example.yaml").read_text()
        assert "orpo" in content.lower() or "ORPO" in content
        assert "experimental" in content.lower() or "example" in content.lower()


# ─── Build Dataset Mix v0 ───────────────────────────────────────────────


class TestBuildDatasetMixV0:
    def test_build_dataset_mix_v0_with_holdout(self):
        import tempfile

        with tempfile.TemporaryDirectory() as tmpdir:
            result = _run_script(
                str(PROJECT_ROOT / "training" / "scripts" / "build_dataset_mix.py"),
                "--sft",
                str(PROJECT_ROOT / "dataset" / "v0" / "sft_v0.jsonl"),
                "--preference",
                str(PROJECT_ROOT / "dataset" / "v0" / "preference_v0.jsonl"),
                "--holdout",
                str(PROJECT_ROOT / "dataset" / "v0" / "eval_holdout.jsonl"),
                "--output-dir",
                tmpdir,
                "--shuffle",
                "--seed",
                "42",
                "--report",
            )
            assert result.returncode == 0, f"build_dataset_mix.py v0 failed:\n{result.stdout}\n{result.stderr}"
            assert (Path(tmpdir) / "sft.train.jsonl").exists(), "sft.train.jsonl not produced"
            assert (Path(tmpdir) / "sft.eval.jsonl").exists(), "sft.eval.jsonl not produced"
            assert (Path(tmpdir) / "preference.train.jsonl").exists(), "preference.train.jsonl not produced"
            assert (Path(tmpdir) / "preference.eval.jsonl").exists(), "preference.eval.jsonl not produced"
            assert (Path(tmpdir) / "holdout.jsonl").exists(), "holdout.jsonl not produced"
            assert (Path(tmpdir) / "report.json").exists(), "report.json not produced"


# ─── Documentation ──────────────────────────────────────────────────────


class TestDocumentation:
    def test_first_private_training_run_exists(self):
        assert (PROJECT_ROOT / "docs" / "FIRST_PRIVATE_TRAINING_RUN.md").exists()

    def test_first_private_training_run_contains_private(self):
        content = (PROJECT_ROOT / "docs" / "FIRST_PRIVATE_TRAINING_RUN.md").read_text()
        assert "private" in content.lower()
        assert "SmolLM3" in content

    def test_hf_placeholder_plan_exists(self):
        assert (PROJECT_ROOT / "docs" / "HF_PLACEHOLDER_PLAN.md").exists()

    def test_hf_placeholder_plan_contains_placeholder(self):
        content = (PROJECT_ROOT / "docs" / "HF_PLACEHOLDER_PLAN.md").read_text()
        assert "placeholder" in content.lower()

    def test_base_model_acceptance_exists(self):
        assert (PROJECT_ROOT / "docs" / "BASE_MODEL_ACCEPTANCE.md").exists()

    def test_model_card_says_no_weights(self):
        content = (PROJECT_ROOT / "MODEL_CARD.md").read_text().lower()
        assert "not been released" in content or "not released" in content or "no weights" in content

    def test_model_card_says_not_trained(self):
        content = (PROJECT_ROOT / "MODEL_CARD.md").read_text().lower()
        assert "not been trained" in content or "not started" in content or "not trained" in content


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

    def test_no_false_claims_in_tracked_files(self):
        result = subprocess.run(
            ["git", "ls-files"],
            capture_output=True,
            text=True,
            timeout=30,
            cwd=str(PROJECT_ROOT),
        )
        tracked = result.stdout.strip().split("\n") if result.stdout.strip() else []
        # Check for present-tense false claims (past/present tense "is released" as fact)
        # Allow future-tense references like "for when Kimari-4B is released"
        false_claim_patterns = [
            "Kimari-4B has been released",
            "Kimari-4B is now available",
            "Kimari-4B weights are available",
        ]
        for filepath in tracked:
            if not filepath.endswith((".md", ".py", ".yaml", ".yml", ".json", ".jsonl", ".txt", ".html")):
                continue
            try:
                content = (PROJECT_ROOT / filepath).read_text()
            except (UnicodeDecodeError, FileNotFoundError):
                continue
            for claim in false_claim_patterns:
                assert claim not in content, f"False claim '{claim}' found in {filepath}"

    def test_no_forbidden_strings_in_datasets(self):
        """Check for forbidden strings in dataset files.

        In preference pairs, forbidden strings may appear in 'rejected' responses
        (that's the point - teaching the model NOT to output them). They must NOT
        appear in 'chosen' responses or in non-preference datasets.
        """
        forbidden_strings = ["BEGIN RSA PRIVATE KEY", "PRIVATE KEY-----"]
        # For preference data, also check chosen responses don't contain secrets
        pref_forbidden = ["password=", "api_key=", "secret_key="]

        # Check SFT and holdout for ALL forbidden strings
        non_pref_files = [
            PROJECT_ROOT / "dataset" / "v0" / "sft_v0.jsonl",
            PROJECT_ROOT / "dataset" / "v0" / "eval_holdout.jsonl",
        ]
        for path in non_pref_files:
            if not path.exists():
                continue
            content = path.read_text()
            for forbidden_str in forbidden_strings + pref_forbidden:
                assert forbidden_str not in content, f"Forbidden string '{forbidden_str}' found in {path}"

        # For preference data, check that chosen responses don't contain secrets
        pref_path = PROJECT_ROOT / "dataset" / "v0" / "preference_v0.jsonl"
        if pref_path.exists():
            for line in pref_path.read_text().strip().splitlines():
                record = json.loads(line)
                chosen = record.get("chosen", "")
                for forbidden_str in pref_forbidden:
                    assert forbidden_str not in chosen, (
                        f"Forbidden string '{forbidden_str}' in CHOSEN response of {record.get('id', 'unknown')}"
                    )


# ─── Changelog and Roadmap ─────────────────────────────────────────────


class TestChangelogAndRoadmap:
    def test_changelog_has_v0119(self):
        content = (PROJECT_ROOT / "CHANGELOG.md").read_text()
        assert "0.1.19-alpha" in content

    def test_roadmap_has_v0119(self):
        content = (PROJECT_ROOT / "ROADMAP.md").read_text()
        assert "0.1.19" in content


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
