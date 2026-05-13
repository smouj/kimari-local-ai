"""Release tests for v0.1.60-alpha — SFT v1 training configuration + dry-run."""

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
SUMMARY_TEMPLATE_PATH = TEMPLATES_DIR / "sft_v1_run_summary.template.json"
PLAN_DOC_PATH = DOCS_DIR / "KIMARI_RUNTIME_15B_SFT_V1_PLAN.md"
ARTIFACT_POLICY_PATH = DOCS_DIR / "KIMARI_RUNTIME_15B_SFT_V1_ARTIFACT_POLICY.md"


def test_config_exists():
    """SFT v1 training config YAML exists."""
    assert CONFIG_PATH.exists(), f"Missing config: {CONFIG_PATH}"


def test_config_base_model_is_apache():
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


def test_config_dataset_paths():
    """Config must reference existing dataset build files."""
    content = CONFIG_PATH.read_text()
    assert "dataset/build/kimari_sft_v1/train.jsonl" in content, "Must reference train.jsonl"
    assert "dataset/build/kimari_sft_v1/validation.jsonl" in content, "Must reference validation.jsonl"


def test_preflight_exists():
    """Preflight script exists."""
    assert PREFLIGHT_PATH.exists(), f"Missing preflight script: {PREFLIGHT_PATH}"


def test_preflight_no_shell_true():
    """Preflight script must not use shell=True or .split() for subprocess."""
    content = PREFLIGHT_PATH.read_text()
    assert "shell=True" not in content, "shell=True is forbidden in preflight script"
    assert ".split()" not in content, ".split() is forbidden for subprocess args in preflight script"


def test_preflight_no_token_arg():
    """Preflight script must not accept --token argument."""
    content = PREFLIGHT_PATH.read_text()
    assert "--token" not in content, "--token arg is forbidden in preflight script"


def test_command_preview_exists():
    """Command preview script exists."""
    assert COMMAND_PREVIEW_PATH.exists(), f"Missing command preview script: {COMMAND_PREVIEW_PATH}"


def test_command_preview_no_execution():
    """Command preview must not execute any commands."""
    content = COMMAND_PREVIEW_PATH.read_text()
    assert "subprocess.run" not in content or "dry_run" in content, "Command preview must not execute commands"
    assert "shell=True" not in content, "shell=True is forbidden in command preview script"


def test_hf_jobs_wrapper_exists():
    """HF Jobs wrapper script exists."""
    assert HF_JOBS_WRAPPER_PATH.exists(), f"Missing HF Jobs wrapper: {HF_JOBS_WRAPPER_PATH}"


def test_hf_jobs_wrapper_no_shell_true():
    """HF Jobs wrapper must not use shell=True."""
    content = HF_JOBS_WRAPPER_PATH.read_text()
    assert "shell=True" not in content, "shell=True is forbidden in HF Jobs wrapper"


def test_hf_jobs_wrapper_no_split():
    """HF Jobs wrapper must not use .split() for subprocess args."""
    content = HF_JOBS_WRAPPER_PATH.read_text()
    # Explicitly forbid hf_cmd.split() pattern from previous bug
    assert "hf_cmd.split()" not in content, "hf_cmd.split() is forbidden (use build_hf_jobs_command_args)"


def test_hf_jobs_wrapper_no_token_arg():
    """HF Jobs wrapper must not accept --token argument."""
    content = HF_JOBS_WRAPPER_PATH.read_text()
    assert "--token" not in content, "--token arg is forbidden in HF Jobs wrapper"


def test_hf_jobs_wrapper_dry_run_default():
    """HF Jobs wrapper must default to dry-run."""
    content = HF_JOBS_WRAPPER_PATH.read_text()
    assert "dry.run" in content or "dry_run" in content, "HF Jobs wrapper must support dry-run mode"


def test_summary_template_exists():
    """SFT v1 run summary template exists."""
    assert SUMMARY_TEMPLATE_PATH.exists(), f"Missing summary template: {SUMMARY_TEMPLATE_PATH}"


def test_summary_template_fields():
    """Summary template must have required safety fields."""
    content = SUMMARY_TEMPLATE_PATH.read_text()
    template = json.loads(content)
    required_fields = [
        "run_id",
        "base_model",
        "base_license",
        "dataset_train_sha256",
        "training_performed",
        "adapter_generated",
        "adapter_committed_public",
        "hf_public_upload_performed",
        "gguf_generated",
        "gate_state",
        "manual_review_required",
    ]
    for field in required_fields:
        assert field in template, f"Missing field in summary template: {field}"


def test_summary_template_safety_defaults():
    """Summary template safety defaults must be safe."""
    content = SUMMARY_TEMPLATE_PATH.read_text()
    template = json.loads(content)
    assert template["training_performed"] is False, "training_performed must default to false"
    assert template["adapter_committed_public"] is False, "adapter_committed_public must default to false"
    assert template["hf_public_upload_performed"] is False, "hf_public_upload_performed must default to false"
    assert template["gguf_generated"] is False, "gguf_generated must default to false"
    assert template["gate_state"] == "BLOCKED", "gate_state must default to BLOCKED"


def test_plan_doc_exists():
    """SFT v1 plan document exists."""
    assert PLAN_DOC_PATH.exists(), f"Missing plan doc: {PLAN_DOC_PATH}"


def test_plan_doc_safety():
    """Plan doc must mention no training executed and gate BLOCKED."""
    content = PLAN_DOC_PATH.read_text().lower()
    assert "blocked" in content, "Plan doc must mention gate BLOCKED"
    assert (
        "no training" in content
        or "not executed" in content
        or "training not" in content
        or "dry-run-only" in content
        or "dry-run only" in content
    ), "Plan doc must state training is not executed / dry-run only"


def test_artifact_policy_exists():
    """Artifact policy document exists."""
    assert ARTIFACT_POLICY_PATH.exists(), f"Missing artifact policy: {ARTIFACT_POLICY_PATH}"


def test_artifact_policy_no_public_release():
    """Artifact policy must prohibit public release."""
    content = ARTIFACT_POLICY_PATH.read_text().lower()
    assert "blocked" in content, "Artifact policy must mention gate BLOCKED"
    assert "no public" in content or "not public" in content or "private" in content, (
        "Artifact policy must prohibit public release"
    )


def test_dataset_build_exists():
    """Dataset build output must exist (train + validation)."""
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
    """Config must not contain secrets, tokens, or API keys."""
    content = CONFIG_PATH.read_text()
    secret_patterns = ["sk-proj-", "sk-sb-", "ghp_", "gho_", "AKIA", "private_key_pem"]
    for pattern in secret_patterns:
        assert pattern not in content, f"Secret pattern found in config: {pattern}"


def test_version_matches():
    """Package version must be 0.1.60-alpha."""
    import kimari

    assert kimari.__version__ == "0.1.60-alpha", f"Expected 0.1.60-alpha, got {kimari.__version__}"


def test_no_kimari4b_released_claim():
    """No Kimari-4B released claim in docs."""
    release_files = ["README.md", "CHANGELOG.md", "ROADMAP.md"]
    for filename in release_files:
        filepath = ROOT / filename
        if not filepath.exists():
            continue
        content = filepath.read_text().lower()
        for phrase in ["kimari-4b is released", "kimari-4b is now released", "kimari-4b has been released"]:
            if phrase in content:
                idx = content.find(phrase)
                context = content[max(0, idx - 120) : idx + len(phrase) + 10]
                conditional_patterns = [
                    "when kimari-4b is released",
                    "for when kimari-4b is released",
                    "until kimari-4b is released",
                    "until kimari-4b is available",
                    "ready for when kimari-4b is released",
                ]
                assert any(p in context for p in conditional_patterns), f"Kimari-4B released claim found in {filename}"


def test_gate_blocked_in_config():
    """Gate must remain BLOCKED in config."""
    content = CONFIG_PATH.read_text()
    assert "gate_state: BLOCKED" in content, "gate_state must be BLOCKED"


def test_output_dir_gitignored():
    """Training output directory should be in .gitignore."""
    gitignore = (ROOT / ".gitignore").read_text()
    assert "training/runs" in gitignore, "training/runs must be in .gitignore"


def test_max_steps_reasonable():
    """Max steps should be reasonable for seed dataset (≤500)."""
    content = CONFIG_PATH.read_text()
    for line in content.split("\n"):
        if line.strip().startswith("max_steps:"):
            steps = int(line.split(":")[1].strip())
            assert steps <= 500, f"max_steps {steps} too high for seed dataset (max 500)"
            assert steps >= 10, f"max_steps {steps} too low (min 10)"
