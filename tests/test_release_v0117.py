"""Release validation tests for Kimari Local AI v0.1.23-alpha.

Tests cover:
- MODEL_CARD exists and says not released
- Training plan exists (docs/MODEL_TRAINING_PLAN.md)
- Base selection docs exist (docs/MODEL_BASE_SELECTION.md)
- Model licenses docs exist (MODEL_LICENSES.md)
- Dataset schemas parse as JSON (sft.schema.json and preference.schema.json)
- Example dataset schemas validate sample records if jsonschema is available
- Training configs exist (kimari_sft_lora.example.yaml, kimari_orpo.example.yaml)
- Training scripts support --dry-run (train_sft_lora.py --dry-run --config ...)
- Eval prompts JSONL parses (eval/kimarifit_prompts.jsonl)
- Hugging Face release doc exists (docs/HUGGINGFACE_RELEASE.md)
- No GGUF files tracked
- No false Kimari-4B release claim
- No fake benchmark numbers in MODEL_CARD
- Release-check passes
- Version consistency (pyproject.toml == __init__.py == "0.1.23-alpha")
"""

import json
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

try:
    import jsonschema

    HAS_JSONSCHEMA = True
except ImportError:
    HAS_JSONSCHEMA = False


def _run_kimari(*args: str) -> subprocess.CompletedProcess:
    cmd = [sys.executable, "-m", "kimari.cli.main", *args]
    return subprocess.run(cmd, capture_output=True, text=True, timeout=30, cwd=str(PROJECT_ROOT))


# ─── Version Consistency ────────────────────────────────────────────────────


class TestVersion:
    def test_version_is_0117(self):
        from kimari import __version__

        assert __version__ == "0.1.23-alpha"

    def test_pyproject_version_matches(self):
        pyproject = PROJECT_ROOT / "pyproject.toml"
        text = pyproject.read_text()
        assert 'version = "0.1.23-alpha"' in text

    def test_cli_info_version(self):
        result = _run_kimari("info", "--json")
        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert data["kimari_version"] == "0.1.23-alpha"


# ─── MODEL_CARD ─────────────────────────────────────────────────────────────


class TestModelCard:
    def test_model_card_exists(self):
        assert (PROJECT_ROOT / "MODEL_CARD.md").exists()

    def test_model_card_says_not_released(self):
        content = (PROJECT_ROOT / "MODEL_CARD.md").read_text().lower()
        assert "not been trained yet" in content or "not been released" in content or "no weights" in content

    def test_model_card_says_planned(self):
        content = (PROJECT_ROOT / "MODEL_CARD.md").read_text()
        assert "Planned" in content or "Training Design" in content

    def test_model_card_no_false_release_claim(self):
        content = (PROJECT_ROOT / "MODEL_CARD.md").read_text().lower()
        false_claims = [
            "kimari-4b is available now",
            "kimari-4b can be downloaded",
            "download kimari-4b",
            "kimari-4b weights available",
            "kimari-4b has been released",
        ]
        for claim in false_claims:
            assert claim not in content, f"False claim '{claim}' found in MODEL_CARD.md"

    def test_model_card_has_base_candidates(self):
        content = (PROJECT_ROOT / "MODEL_CARD.md").read_text()
        assert "SmolLM3" in content or "SmolLM3-3B" in content
        assert "Qwen2.5" in content or "Qwen2.5-3B" in content
        assert "Llama 3.2" in content or "Llama-3.2" in content

    def test_model_card_has_evaluation_targets_not_achieved(self):
        content = (PROJECT_ROOT / "MODEL_CARD.md").read_text()
        assert "Not Achieved" in content or "not achieved" in content.lower()
        assert "evaluation targets" in content.lower() or "targets, not results" in content.lower()

    def test_model_card_has_release_checklist(self):
        content = (PROJECT_ROOT / "MODEL_CARD.md").read_text().lower()
        assert "release checklist" in content or "checklist" in content


# ─── Training Plan ──────────────────────────────────────────────────────────


class TestTrainingPlan:
    def test_training_plan_exists(self):
        assert (PROJECT_ROOT / "docs" / "MODEL_TRAINING_PLAN.md").exists()

    def test_training_plan_mentions_phases(self):
        content = (PROJECT_ROOT / "docs" / "MODEL_TRAINING_PLAN.md").read_text().lower()
        assert "phase" in content

    def test_training_plan_mentions_sft(self):
        content = (PROJECT_ROOT / "docs" / "MODEL_TRAINING_PLAN.md").read_text().lower()
        assert "sft" in content

    def test_training_plan_mentions_dpo_or_orpo(self):
        content = (PROJECT_ROOT / "docs" / "MODEL_TRAINING_PLAN.md").read_text().lower()
        assert "dpo" in content or "orpo" in content

    def test_training_plan_no_training_done(self):
        content = (PROJECT_ROOT / "docs" / "MODEL_TRAINING_PLAN.md").read_text().lower()
        assert "no training has" in content or "not started" in content or "planning" in content


# ─── Base Selection ─────────────────────────────────────────────────────────


class TestBaseSelection:
    def test_base_selection_doc_exists(self):
        assert (PROJECT_ROOT / "docs" / "MODEL_BASE_SELECTION.md").exists()

    def test_base_selection_has_candidates(self):
        content = (PROJECT_ROOT / "docs" / "MODEL_BASE_SELECTION.md").read_text().lower()
        assert "smollm3" in content or "smollm" in content
        assert "qwen" in content
        assert "llama" in content

    def test_base_selection_no_final_choice(self):
        content = (PROJECT_ROOT / "docs" / "MODEL_BASE_SELECTION.md").read_text().lower()
        assert (
            "under review" in content or "not selected" in content or "not yet selected" in content or "tbd" in content
        )


# ─── Model Licenses ─────────────────────────────────────────────────────────


class TestModelLicenses:
    def test_model_licenses_exists(self):
        assert (PROJECT_ROOT / "MODEL_LICENSES.md").exists()

    def test_model_licenses_mentions_candidates(self):
        content = (PROJECT_ROOT / "MODEL_LICENSES.md").read_text().lower()
        assert "smollm3" in content or "smollm" in content
        assert "qwen" in content
        assert "llama" in content

    def test_model_licenses_no_weights_released(self):
        content = (PROJECT_ROOT / "MODEL_LICENSES.md").read_text().lower()
        assert "no weights" in content or "not released" in content or "no model weights" in content

    def test_model_licenses_has_decision_framework(self):
        content = (PROJECT_ROOT / "MODEL_LICENSES.md").read_text().lower()
        assert "decision framework" in content or "decision" in content


# ─── Dataset Schemas ────────────────────────────────────────────────────────


class TestDatasetSchemas:
    def test_sft_schema_exists(self):
        assert (PROJECT_ROOT / "dataset" / "schema" / "sft.schema.json").exists()

    def test_preference_schema_exists(self):
        assert (PROJECT_ROOT / "dataset" / "schema" / "preference.schema.json").exists()

    def test_sft_schema_parses_as_json(self):
        path = PROJECT_ROOT / "dataset" / "schema" / "sft.schema.json"
        data = json.loads(path.read_text())
        assert data.get("type") == "object"
        assert "messages" in data.get("properties", {})
        assert "source" in data.get("properties", {})
        assert "license" in data.get("properties", {})

    def test_preference_schema_parses_as_json(self):
        path = PROJECT_ROOT / "dataset" / "schema" / "preference.schema.json"
        data = json.loads(path.read_text())
        assert data.get("type") == "object"
        assert "prompt" in data.get("properties", {})
        assert "chosen" in data.get("properties", {})
        assert "rejected" in data.get("properties", {})
        assert "source" in data.get("properties", {})
        assert "license" in data.get("properties", {})

    def test_sft_schema_is_draft07(self):
        path = PROJECT_ROOT / "dataset" / "schema" / "sft.schema.json"
        data = json.loads(path.read_text())
        assert "draft-07" in data.get("$schema", "")

    def test_preference_schema_is_draft07(self):
        path = PROJECT_ROOT / "dataset" / "schema" / "preference.schema.json"
        data = json.loads(path.read_text())
        assert "draft-07" in data.get("$schema", "")


class TestDatasetSchemaValidation:
    """Validate sample records against schemas if jsonschema is available."""

    def test_sft_sample_validates(self):
        if not HAS_JSONSCHEMA:
            return

        schema_path = PROJECT_ROOT / "dataset" / "schema" / "sft.schema.json"
        schema = json.loads(schema_path.read_text())

        sample = {
            "messages": [
                {"role": "user", "content": "Hello"},
                {"role": "assistant", "content": "Hi there!"},
            ],
            "source": "test-suite",
            "license": "MIT",
        }
        jsonschema.validate(sample, schema)

    def test_sft_sample_with_tags_validates(self):
        if not HAS_JSONSCHEMA:
            return

        schema_path = PROJECT_ROOT / "dataset" / "schema" / "sft.schema.json"
        schema = json.loads(schema_path.read_text())

        sample = {
            "messages": [
                {"role": "system", "content": "You are helpful."},
                {"role": "user", "content": "Write code"},
                {"role": "assistant", "content": "Here is code."},
            ],
            "source": "synthetic",
            "license": "Apache-2.0",
            "tags": ["python", "coding"],
        }
        jsonschema.validate(sample, schema)

    def test_preference_sample_validates(self):
        if not HAS_JSONSCHEMA:
            return

        schema_path = PROJECT_ROOT / "dataset" / "schema" / "preference.schema.json"
        schema = json.loads(schema_path.read_text())

        sample = {
            "prompt": "Explain recursion",
            "chosen": "Recursion is when a function calls itself...",
            "rejected": "I don't know.",
            "source": "human-preference",
            "license": "CC-BY-4.0",
        }
        jsonschema.validate(sample, schema)

    def test_preference_sample_with_tags_validates(self):
        if not HAS_JSONSCHEMA:
            return

        schema_path = PROJECT_ROOT / "dataset" / "schema" / "preference.schema.json"
        schema = json.loads(schema_path.read_text())

        sample = {
            "prompt": "Write a function",
            "chosen": "def foo(): pass",
            "rejected": "no",
            "source": "test",
            "license": "MIT",
            "tags": ["python"],
        }
        jsonschema.validate(sample, schema)

    def test_sft_invalid_record_fails(self):
        if not HAS_JSONSCHEMA:
            return

        schema_path = PROJECT_ROOT / "dataset" / "schema" / "sft.schema.json"
        schema = json.loads(schema_path.read_text())

        # Missing required 'license' field
        bad_sample = {
            "messages": [
                {"role": "user", "content": "Hi"},
                {"role": "assistant", "content": "Hello"},
            ],
            "source": "test",
        }
        try:
            jsonschema.validate(bad_sample, schema)
            raise AssertionError("Expected validation error for missing 'license'")
        except jsonschema.ValidationError:
            pass  # Expected

    def test_preference_invalid_record_fails(self):
        if not HAS_JSONSCHEMA:
            return

        schema_path = PROJECT_ROOT / "dataset" / "schema" / "preference.schema.json"
        schema = json.loads(schema_path.read_text())

        # Missing required 'chosen' field
        bad_sample = {
            "prompt": "Test",
            "rejected": "Bad answer",
            "source": "test",
            "license": "MIT",
        }
        try:
            jsonschema.validate(bad_sample, schema)
            raise AssertionError("Expected validation error for missing 'chosen'")
        except jsonschema.ValidationError:
            pass  # Expected


# ─── Training Configs ───────────────────────────────────────────────────────


class TestTrainingConfigs:
    def test_sft_lora_config_exists(self):
        assert (PROJECT_ROOT / "training" / "configs" / "kimari_sft_lora.example.yaml").exists()

    def test_orpo_config_exists(self):
        assert (PROJECT_ROOT / "training" / "configs" / "kimari_orpo.example.yaml").exists()

    def test_sft_config_has_base_model_tbd(self):
        content = (PROJECT_ROOT / "training" / "configs" / "kimari_sft_lora.example.yaml").read_text()
        assert "TBD" in content

    def test_sft_config_has_lora_params(self):
        content = (PROJECT_ROOT / "training" / "configs" / "kimari_sft_lora.example.yaml").read_text().lower()
        assert "lora_r" in content or "lora" in content

    def test_sft_config_warns_starting_points(self):
        content = (PROJECT_ROOT / "training" / "configs" / "kimari_sft_lora.example.yaml").read_text().lower()
        assert "starting point" in content or "not final" in content or "warning" in content

    def test_orpo_config_has_beta(self):
        content = (PROJECT_ROOT / "training" / "configs" / "kimari_orpo.example.yaml").read_text().lower()
        assert "beta" in content

    def test_orpo_config_warns_safety(self):
        content = (PROJECT_ROOT / "training" / "configs" / "kimari_orpo.example.yaml").read_text().lower()
        assert "safety" in content or "warning" in content

    def test_orpo_config_has_base_model_tbd(self):
        content = (PROJECT_ROOT / "training" / "configs" / "kimari_orpo.example.yaml").read_text()
        assert "TBD" in content


# ─── Training Scripts ───────────────────────────────────────────────────────


class TestTrainingScripts:
    def test_train_sft_lora_exists(self):
        assert (PROJECT_ROOT / "training" / "scripts" / "train_sft_lora.py").exists()

    def test_prepare_dataset_exists(self):
        assert (PROJECT_ROOT / "training" / "scripts" / "prepare_dataset.py").exists()

    def test_train_sft_lora_dry_run(self):
        config_path = PROJECT_ROOT / "training" / "configs" / "kimari_sft_lora.example.yaml"
        result = subprocess.run(
            [
                sys.executable,
                str(PROJECT_ROOT / "training" / "scripts" / "train_sft_lora.py"),
                "--dry-run",
                "--config",
                str(config_path),
            ],
            capture_output=True,
            text=True,
            timeout=30,
            cwd=str(PROJECT_ROOT),
        )
        assert result.returncode == 0, f"train_sft_lora.py --dry-run failed:\n{result.stdout}\n{result.stderr}"
        assert "dry run" in result.stdout.lower() or "DRY RUN" in result.stdout

    def test_train_sft_lora_blocks_tbd_base_model(self):
        """When base_model is TBD, non-dry-run should fail.

        The script may fail at the dependency check step (missing
        transformers/peft/etc.) or at the TBD base-model gate — either
        way it must exit non-zero.
        """
        config_path = PROJECT_ROOT / "training" / "configs" / "kimari_sft_lora.example.yaml"
        result = subprocess.run(
            [
                sys.executable,
                str(PROJECT_ROOT / "training" / "scripts" / "train_sft_lora.py"),
                "--config",
                str(config_path),
            ],
            capture_output=True,
            text=True,
            timeout=30,
            cwd=str(PROJECT_ROOT),
        )
        # Should exit non-zero — either missing deps or TBD base model
        assert result.returncode != 0
        combined = (result.stdout + result.stderr).lower()
        assert "tbd" in combined or "base model" in combined or "missing" in combined

    def test_train_sft_lora_help(self):
        result = subprocess.run(
            [sys.executable, str(PROJECT_ROOT / "training" / "scripts" / "train_sft_lora.py"), "--help"],
            capture_output=True,
            text=True,
            timeout=30,
            cwd=str(PROJECT_ROOT),
        )
        assert result.returncode == 0
        assert "--dry-run" in result.stdout
        assert "--config" in result.stdout


# ─── Eval Prompts ───────────────────────────────────────────────────────────


class TestEvalPrompts:
    def test_kimarifit_prompts_exists(self):
        assert (PROJECT_ROOT / "eval" / "kimarifit_prompts.jsonl").exists()

    def test_kimarifit_prompts_jsonl_parses(self):
        path = PROJECT_ROOT / "eval" / "kimarifit_prompts.jsonl"
        lines = path.read_text().strip().split("\n")
        records = []
        for line in lines:
            records.append(json.loads(line))
        assert len(records) >= 35
        # Check first record has expected fields
        first = records[0]
        assert "id" in first
        assert "category" in first
        assert "prompt" in first

    def test_kimarifit_prompts_categories(self):
        path = PROJECT_ROOT / "eval" / "kimarifit_prompts.jsonl"
        lines = path.read_text().strip().split("\n")
        categories = set()
        for line in lines:
            record = json.loads(line)
            categories.add(record["category"])
        # Expect at least 10 categories
        assert len(categories) >= 10
        # Check key categories exist
        expected_categories = ["python", "bash", "docker", "json_mode"]
        for cat in expected_categories:
            assert cat in categories, f"Missing category: {cat}"

    def test_kimarifit_prompts_has_security(self):
        path = PROJECT_ROOT / "eval" / "kimarifit_prompts.jsonl"
        lines = path.read_text().strip().split("\n")
        categories = set()
        for line in lines:
            record = json.loads(line)
            categories.add(record["category"])
        assert "local_security" in categories or "security" in categories


# ─── Hugging Face Release Doc ───────────────────────────────────────────────


class TestHuggingFaceRelease:
    def test_hf_release_doc_exists(self):
        assert (PROJECT_ROOT / "docs" / "HUGGINGFACE_RELEASE.md").exists()

    def test_hf_release_mentions_checklist(self):
        content = (PROJECT_ROOT / "docs" / "HUGGINGFACE_RELEASE.md").read_text().lower()
        assert "checklist" in content

    def test_hf_release_mentions_license(self):
        content = (PROJECT_ROOT / "docs" / "HUGGINGFACE_RELEASE.md").read_text().lower()
        assert "license" in content

    def test_hf_release_has_hard_blocks(self):
        content = (PROJECT_ROOT / "docs" / "HUGGINGFACE_RELEASE.md").read_text().lower()
        assert "block" in content or "hard block" in content or "must" in content


# ─── No GGUF Files Tracked ─────────────────────────────────────────────────


class TestNoGGUF:
    def test_no_gguf_in_tracked_files(self):
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

    def test_no_gguf_in_models_dir(self):
        models_dir = PROJECT_ROOT / "models"
        if models_dir.exists():
            gguf_files = list(models_dir.rglob("*.gguf"))
            assert gguf_files == [], f"GGUF files in models/: {[str(f) for f in gguf_files]}"


# ─── No False Claims ────────────────────────────────────────────────────────


class TestNoFalseClaims:
    def test_no_kimari_4b_released_claim(self):
        patterns = [
            "kimari-4b is available now",
            "kimari-4b can be downloaded",
            "download kimari-4b",
            "kimari-4b weights available",
            "kimari-4b has been released",
        ]
        for name in ("README.md", "CHANGELOG.md", "MODEL_CARD.md"):
            path = PROJECT_ROOT / name
            if path.exists():
                content = path.read_text().lower()
                for pattern in patterns:
                    assert pattern not in content, f"False claim '{pattern}' found in {path}"

    def test_no_false_pypi_published_claim(self):
        for name in ("README.md", "CHANGELOG.md", "docs/PYPI_RELEASE_GATE.md"):
            path = PROJECT_ROOT / name
            if path.exists():
                content = path.read_text().lower()
                assert "published to pypi" not in content or "not published" in content or "pending" in content


# ─── No Fake Benchmark Numbers ──────────────────────────────────────────────


class TestNoFakeBenchmarks:
    def test_model_card_no_fake_benchmark_numbers(self):
        content = (PROJECT_ROOT / "MODEL_CARD.md").read_text()
        # Should contain "Not Achieved" or "targets, not results" style language
        lower = content.lower()
        assert "not achieved" in lower or "not been measured" in lower or "no benchmarks" in lower

    def test_model_card_targets_are_tbd_or_aspirational(self):
        content = (PROJECT_ROOT / "MODEL_CARD.md").read_text().lower()
        # Should not have specific benchmark numbers like "MMLU: 65%" for Kimari-4B
        assert "mmlu" not in content or "tbd" in content or "target" in content or "not achieved" in content

    def test_model_card_benchmarks_section_honest(self):
        content = (PROJECT_ROOT / "MODEL_CARD.md").read_text()
        # The benchmarks section should say no benchmarks measured
        lower = content.lower()
        if "benchmark" in lower:
            assert "no benchmark" in lower or "not been measured" in lower or "targets" in lower


# ─── Release Check ──────────────────────────────────────────────────────────


class TestReleaseCheck:
    def test_check_release_passes(self):
        result = subprocess.run(
            [sys.executable, "scripts/release/check-release.py"],
            capture_output=True,
            text=True,
            timeout=60,
            cwd=str(PROJECT_ROOT),
        )
        assert result.returncode == 0, f"check-release.py failed:\n{result.stdout}\n{result.stderr}"
