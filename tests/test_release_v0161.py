"""Release tests for v0.1.61-alpha — First SFT v1 real short run."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TRAINING_DIR = ROOT / "training"
CONFIGS_DIR = TRAINING_DIR / "configs"
SCRIPTS_DIR = TRAINING_DIR / "scripts"
TEMPLATES_DIR = TRAINING_DIR / "templates"
DOCS_DIR = ROOT / "docs"
DATASET_BUILD_DIR = ROOT / "dataset" / "build" / "kimari_sft_v1"

CONFIG_PATH = CONFIGS_DIR / "kimari_runtime_15b_sft_v1.yaml"
PREFLIGHT_PATH = SCRIPTS_DIR / "preflight_sft_v1.py"
COMMAND_PREVIEW_PATH = SCRIPTS_DIR / "sft_v1_command_preview.py"
HF_JOBS_WRAPPER_PATH = SCRIPTS_DIR / "hf_jobs_sft_v1.py"
SUMMARY_CREATOR_PATH = SCRIPTS_DIR / "create_sft_v1_run_summary.py"
SUMMARY_VALIDATOR_PATH = SCRIPTS_DIR / "validate_sft_v1_run_summary.py"
SUMMARY_TEMPLATE_PATH = TEMPLATES_DIR / "sft_v1_run_summary.template.json"
COMPLETED_TEMPLATE_PATH = TEMPLATES_DIR / "sft_v1_completed_summary.template.json"
RESULT_DOC_PATH = DOCS_DIR / "KIMARI_RUNTIME_15B_SFT_V1_RESULT.md"
PLAN_DOC_PATH = DOCS_DIR / "KIMARI_RUNTIME_15B_SFT_V1_PLAN.md"
ARTIFACT_POLICY_PATH = DOCS_DIR / "KIMARI_RUNTIME_15B_SFT_V1_ARTIFACT_POLICY.md"


def test_version_matches():
    """Package version must be 0.1.61-alpha."""
    import kimari

    assert kimari.__version__ == "0.1.61-alpha", f"Expected 0.1.61-alpha, got {kimari.__version__}"


def test_config_exists():
    """SFT v1 training config YAML exists."""
    assert CONFIG_PATH.exists(), f"Missing config: {CONFIG_PATH}"


def test_config_base_is_apache():
    """Base model must be Qwen2.5-1.5B-Instruct with Apache-2.0 license."""
    content = CONFIG_PATH.read_text()
    assert "Qwen/Qwen2.5-1.5B-Instruct" in content, "Base model must be Qwen2.5-1.5B-Instruct"
    assert "Apache-2.0" in content, "Base license must be Apache-2.0"


def test_config_safety_flags():
    """Config must have all safety flags set correctly."""
    content = CONFIG_PATH.read_text()
    assert "push_to_hub: false" in content, "push_to_hub must be false"
    assert "report_to: none" in content, "report_to must be none"
    assert "public_release_allowed: false" in content, "public_release_allowed must be false"
    assert "hf_public_upload_allowed: false" in content, "hf_public_upload_allowed must be false"
    assert "gguf_export_allowed: false" in content, "gguf_export_allowed must be false"
    assert "gate_state: BLOCKED" in content, "gate_state must be BLOCKED"


def test_preflight_exists():
    """Preflight script exists."""
    assert PREFLIGHT_PATH.exists(), f"Missing preflight script: {PREFLIGHT_PATH}"


def test_command_preview_exists():
    """Command preview script exists."""
    assert COMMAND_PREVIEW_PATH.exists(), f"Missing command preview: {COMMAND_PREVIEW_PATH}"


def test_hf_jobs_wrapper_exists():
    """HF Jobs wrapper script exists."""
    assert HF_JOBS_WRAPPER_PATH.exists(), f"Missing HF Jobs wrapper: {HF_JOBS_WRAPPER_PATH}"


def test_hf_jobs_wrapper_allows_submit():
    """HF Jobs wrapper must allow real submission with safeguards."""
    content = HF_JOBS_WRAPPER_PATH.read_text()
    assert "--allow-submit" in content, "HF Jobs wrapper must support --allow-submit"
    assert "--yes" in content, "HF Jobs wrapper must support --yes"
    assert "v0.1.60-alpha" not in content, "HF Jobs wrapper must not contain v0.1.60-alpha block message"


def test_summary_creator_exists():
    """Run summary creator script exists."""
    assert SUMMARY_CREATOR_PATH.exists(), f"Missing summary creator: {SUMMARY_CREATOR_PATH}"


def test_summary_validator_exists():
    """Run summary validator script exists."""
    assert SUMMARY_VALIDATOR_PATH.exists(), f"Missing summary validator: {SUMMARY_VALIDATOR_PATH}"


def test_completed_template_exists():
    """Completed summary template exists."""
    assert COMPLETED_TEMPLATE_PATH.exists(), f"Missing completed template: {COMPLETED_TEMPLATE_PATH}"


def test_completed_template_safety_defaults():
    """Completed template safety defaults must be safe."""
    content = COMPLETED_TEMPLATE_PATH.read_text()
    template = json.loads(content)
    assert template["adapter_committed_public"] is False, "adapter_committed_public must default to false"
    assert template["hf_public_upload_performed"] is False, "hf_public_upload_performed must default to false"
    assert template["gguf_generated"] is False, "gguf_generated must default to false"
    assert template["raw_logs_committed"] is False, "raw_logs_committed must default to false"
    assert template["public_benchmark_allowed"] is False, "public_benchmark_allowed must default to false"
    assert template["gate_state"] == "BLOCKED", "gate_state must default to BLOCKED"
    assert template["manual_review_required"] is True, "manual_review_required must default to true"


def test_result_doc_exists():
    """SFT v1 result document exists."""
    assert RESULT_DOC_PATH.exists(), f"Missing result doc: {RESULT_DOC_PATH}"


def test_result_doc_gate_blocked():
    """Result doc must mention gate BLOCKED and no public release."""
    content = RESULT_DOC_PATH.read_text().lower()
    assert "blocked" in content, "Result doc must mention gate BLOCKED"
    assert "no public" in content or "not public" in content or "private" in content, (
        "Result doc must mention no public release"
    )


def test_plan_doc_exists():
    """SFT v1 plan document exists."""
    assert PLAN_DOC_PATH.exists(), f"Missing plan doc: {PLAN_DOC_PATH}"


def test_artifact_policy_exists():
    """Artifact policy document exists."""
    assert ARTIFACT_POLICY_PATH.exists(), f"Missing artifact policy: {ARTIFACT_POLICY_PATH}"


def test_dataset_build_exists():
    """Dataset build output must exist."""
    assert DATASET_BUILD_DIR.exists(), f"Missing dataset build dir: {DATASET_BUILD_DIR}"
    assert (DATASET_BUILD_DIR / "train.jsonl").exists(), "Missing train.jsonl"
    assert (DATASET_BUILD_DIR / "validation.jsonl").exists(), "Missing validation.jsonl"


def test_no_training_artifacts():
    """No training run artifacts should exist (except .gitkeep)."""
    runs_dir = TRAINING_DIR / "runs"
    if runs_dir.exists():
        real_files = [f for f in runs_dir.iterdir() if f.name != ".gitkeep"]
        assert len(real_files) == 0, f"Training runs directory has unexpected files: {real_files}"


def test_no_public_weights():
    """No safetensors, GGUF, or adapter_model.bin files should exist."""
    excluded_patterns = ("*.safetensors", "*.gguf", "adapter_model.bin")
    for pattern in excluded_patterns:
        for path in ROOT.rglob(pattern):
            if ".venv" not in path.parts and "deps" not in path.parts:
                raise AssertionError(f"Found public model artifact: {path.relative_to(ROOT)}")


def test_no_secrets_in_config():
    """Config must not contain secrets."""
    content = CONFIG_PATH.read_text()
    secret_patterns = ["sk-proj-", "sk-sb-", "ghp_", "gho_", "AKIA", "private_key_pem"]
    for pattern in secret_patterns:
        assert pattern not in content, f"Secret pattern found in config: {pattern}"


def test_scripts_no_shell_true():
    """Training scripts must not use shell=True."""
    for script_name, script_path in [
        ("preflight", PREFLIGHT_PATH),
        ("command_preview", COMMAND_PREVIEW_PATH),
        ("hf_jobs_wrapper", HF_JOBS_WRAPPER_PATH),
        ("summary_creator", SUMMARY_CREATOR_PATH),
        ("summary_validator", SUMMARY_VALIDATOR_PATH),
    ]:
        content = script_path.read_text()
        assert "shell=True" not in content, f"{script_name} must not use shell=True"


def test_scripts_no_token_arg():
    """Training scripts must not accept --token argument."""
    for script_name, script_path in [
        ("preflight", PREFLIGHT_PATH),
        ("hf_jobs_wrapper", HF_JOBS_WRAPPER_PATH),
        ("summary_creator", SUMMARY_CREATOR_PATH),
    ]:
        content = script_path.read_text()
        assert "--token" not in content, f"{script_name} must not accept --token argument"


def test_output_dir_gitignored():
    """Training output directory should be in .gitignore."""
    gitignore = (ROOT / ".gitignore").read_text()
    assert "training/runs" in gitignore, "training/runs must be in .gitignore"


def test_gate_blocked_in_config():
    """Gate must remain BLOCKED in config."""
    content = CONFIG_PATH.read_text()
    assert "gate_state: BLOCKED" in content, "gate_state must be BLOCKED"


def test_max_steps_reasonable():
    """Max steps should be reasonable for seed dataset (≤500)."""
    content = CONFIG_PATH.read_text()
    for line in content.split("\n"):
        if line.strip().startswith("max_steps:"):
            steps = int(line.split(":")[1].strip())
            assert steps <= 500, f"max_steps {steps} too high for seed dataset (max 500)"
            assert steps >= 10, f"max_steps {steps} too low (min 10)"
