"""Release tests for v0.1.62-alpha — SFT v1 pre-submit hardening."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TRAINING_DIR = ROOT / "training"
SCRIPTS_DIR = TRAINING_DIR / "scripts"
DOCS_DIR = ROOT / "docs"
CONFIG_PATH = TRAINING_DIR / "configs" / "kimari_runtime_15b_sft_v1.yaml"
RESULT_DOC_PATH = DOCS_DIR / "KIMARI_RUNTIME_15B_SFT_V1_RESULT.md"
HF_JOBS_WRAPPER_PATH = SCRIPTS_DIR / "hf_jobs_sft_v1.py"


def test_version_matches():
    """Package version must be 0.1.62-alpha."""
    import kimari

    assert kimari.__version__ == "0.1.62-alpha", f"Expected 0.1.62-alpha, got {kimari.__version__}"


def test_result_placeholder_does_not_claim_training_performed():
    """Result doc placeholder must NOT claim training_performed=true."""
    content = RESULT_DOC_PATH.read_text().lower()
    assert "training_performed=false" in content, "Result doc must say training_performed=false"
    assert "training_performed=true" not in content, "Result doc must NOT say training_performed=true"


def test_result_placeholder_does_not_claim_adapter_generated():
    """Result doc placeholder must NOT claim adapter_generated=true."""
    content = RESULT_DOC_PATH.read_text().lower()
    assert "adapter_generated=false" in content, "Result doc must say adapter_generated=false"
    assert "adapter_generated=true" not in content, "Result doc must NOT say adapter_generated=true"


def test_result_placeholder_status_is_pending():
    """Result doc status must be PENDING, not COMPLETED."""
    content = RESULT_DOC_PATH.read_text()
    assert "PENDING" in content, "Result doc must have PENDING status"
    assert "COMPLETED" not in content or "COMPLETED SFT RUN" in content, "Result doc must NOT claim COMPLETED status"


def test_result_placeholder_has_warning():
    """Result doc must have a warning that it's a placeholder."""
    content = RESULT_DOC_PATH.read_text().lower()
    assert "placeholder" in content, "Result doc must mention 'placeholder'"


def test_hf_jobs_preflight_before_training():
    """HF Jobs wrapper must run preflight before training."""
    content = HF_JOBS_WRAPPER_PATH.read_text()
    # Find the order: preflight should appear before train_sft_lora in guarded_command
    preflight_pos = content.find("preflight_sft_v1")
    training_pos = content.find("train_sft_lora.py")
    assert preflight_pos != -1, "preflight_sft_v1.py must be in the command"
    assert training_pos != -1, "train_sft_lora.py must be in the command"
    # In the guarded_command construction, preflight must come before training
    # Find the guarded_command assembly
    guarded_start = content.find("guarded_command =")
    if guarded_start != -1:
        guarded_section = content[guarded_start : guarded_start + 500]
        preflight_in_section = guarded_section.find("preflight_sft_v1")
        training_in_section = guarded_section.find("train_sft_lora")
        if preflight_in_section != -1 and training_in_section != -1:
            assert preflight_in_section < training_in_section, (
                "preflight must appear before train_sft_lora in guarded_command"
            )


def test_hf_jobs_execution_order_in_dry_run():
    """HF Jobs wrapper dry-run must include execution_order with preflight before training."""
    import subprocess

    result = subprocess.run(
        [
            "python",
            str(HF_JOBS_WRAPPER_PATH),
            "--config",
            str(CONFIG_PATH),
            "--dry-run",
            "--json",
        ],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        timeout=30,
    )
    data = json.loads(result.stdout)
    assert "execution_order" in data, "Dry-run must include execution_order"
    order = data["execution_order"]
    assert order.index("preflight_strict") < order.index("train_sft_lora"), (
        "preflight must come before training in execution_order"
    )


def test_hf_jobs_preflight_before_training_flag():
    """HF Jobs wrapper dry-run must report preflight_before_training=true."""
    import subprocess

    result = subprocess.run(
        [
            "python",
            str(HF_JOBS_WRAPPER_PATH),
            "--config",
            str(CONFIG_PATH),
            "--dry-run",
            "--json",
        ],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        timeout=30,
    )
    data = json.loads(result.stdout)
    assert data.get("preflight_before_training") is True, "preflight_before_training must be true"


def test_hf_jobs_training_after_preflight_flag():
    """HF Jobs wrapper dry-run must report training_after_preflight=true."""
    import subprocess

    result = subprocess.run(
        [
            "python",
            str(HF_JOBS_WRAPPER_PATH),
            "--config",
            str(CONFIG_PATH),
            "--dry-run",
            "--json",
        ],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        timeout=30,
    )
    data = json.loads(result.stdout)
    assert data.get("training_after_preflight") is True, "training_after_preflight must be true"


def test_hf_jobs_validate_execution_order():
    """HF Jobs wrapper must have validate_execution_order function."""
    content = HF_JOBS_WRAPPER_PATH.read_text()
    assert "validate_execution_order" in content, "Must have validate_execution_order function"


def test_no_sft_v1_summary_claims_success_without_job_id():
    """Completed summary template must not claim success by default."""
    template_path = TRAINING_DIR / "templates" / "sft_v1_completed_summary.template.json"
    content = template_path.read_text()
    template = json.loads(content)
    assert template.get("training_performed") is False, "Template must default training_performed=false"
    assert template.get("adapter_generated") is False, "Template must default adapter_generated=false"


def test_no_token_arg():
    """HF Jobs wrapper must not accept --token argument."""
    content = HF_JOBS_WRAPPER_PATH.read_text()
    assert "--token" not in content, "HF Jobs wrapper must not accept --token"


def test_no_shell_true():
    """HF Jobs wrapper must not use shell=True."""
    content = HF_JOBS_WRAPPER_PATH.read_text()
    assert "shell=True" not in content, "HF Jobs wrapper must not use shell=True"


def test_no_hf_cmd_split():
    """HF Jobs wrapper must not use hf_cmd.split()."""
    content = HF_JOBS_WRAPPER_PATH.read_text()
    assert "hf_cmd.split()" not in content, "hf_cmd.split() is forbidden"


def test_gate_blocked_in_config():
    """Gate must remain BLOCKED in config."""
    content = CONFIG_PATH.read_text()
    assert "gate_state: BLOCKED" in content, "gate_state must be BLOCKED"


def test_config_safety_flags():
    """Config must have all safety flags set correctly."""
    content = CONFIG_PATH.read_text()
    assert "push_to_hub: false" in content
    assert "report_to: none" in content
    assert "public_release_allowed: false" in content
    assert "hf_public_upload_allowed: false" in content
    assert "gguf_export_allowed: false" in content


def test_no_public_weights():
    """No safetensors, GGUF, or adapter_model.bin files should exist."""
    for pattern in ("*.safetensors", "*.gguf", "adapter_model.bin"):
        for path in ROOT.rglob(pattern):
            if ".venv" not in path.parts and "deps" not in path.parts:
                raise AssertionError(f"Found public model artifact: {path.relative_to(ROOT)}")
