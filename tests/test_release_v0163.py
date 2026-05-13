"""Release tests for v0.1.63-alpha.

SFT v1 real short run completed:
- Job 6a0fd8ae48bea4538b9c17a on a10g-small
- 10 steps micro-run, loss 2.753→2.652
- training_performed=true, adapter_generated=true
- adapter_committed=false, gate BLOCKED
"""

import json
import re
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SUMMARY_PATH = PROJECT_ROOT / "docs" / "assets" / "results" / "sft_v1_run_summary.json"
RESULT_DOC = PROJECT_ROOT / "docs" / "KIMARI_RUNTIME_15B_SFT_V1_RESULT.md"
CONFIG_PATH = PROJECT_ROOT / "training" / "configs" / "kimari_runtime_15b_sft_v1.yaml"
HF_WRAPPER = PROJECT_ROOT / "training" / "scripts" / "hf_jobs_sft_v1.py"


def test_version_is_0163():
    """Package version must be 0.1.63-alpha."""
    import kimari

    assert kimari.__version__ == "0.1.63-alpha", f"Expected 0.1.63-alpha, got {kimari.__version__}"


def test_pyproject_version():
    """pyproject.toml version must be 0.1.63-alpha."""
    pyproject = (PROJECT_ROOT / "pyproject.toml").read_text()
    assert 'version = "0.1.63-alpha"' in pyproject, "pyproject.toml version mismatch"


def test_summary_exists():
    """SFT v1 run summary JSON must exist."""
    assert SUMMARY_PATH.exists(), f"Summary not found: {SUMMARY_PATH}"


def test_summary_valid_json():
    """Summary must be valid JSON."""
    data = json.loads(SUMMARY_PATH.read_text())
    assert isinstance(data, dict), "Summary must be a JSON dict"


def test_summary_job_id():
    """Summary must have the actual job_id."""
    data = json.loads(SUMMARY_PATH.read_text())
    assert "job_id" in data, "Summary missing job_id"
    assert data["job_id"] == "6a0501dae48bea4538b9c17a", f"Unexpected job_id: {data['job_id']}"


def test_summary_training_performed():
    """Summary must report training_performed=true."""
    data = json.loads(SUMMARY_PATH.read_text())
    assert data.get("training_performed") is True, "training_performed must be true"


def test_summary_adapter_generated():
    """Summary must report adapter_generated=true."""
    data = json.loads(SUMMARY_PATH.read_text())
    assert data.get("adapter_generated") is True, "adapter_generated must be true"


def test_summary_adapter_not_committed():
    """Summary must report adapter_committed=false."""
    data = json.loads(SUMMARY_PATH.read_text())
    assert data.get("adapter_committed") is False, "adapter_committed must be false"


def test_summary_no_public_upload():
    """Summary must report hf_public_upload_performed=false."""
    data = json.loads(SUMMARY_PATH.read_text())
    assert data.get("hf_public_upload_performed") is False, "hf_public_upload_performed must be false"


def test_summary_gate_blocked():
    """Summary must report gate_state=BLOCKED."""
    data = json.loads(SUMMARY_PATH.read_text())
    assert data.get("gate_state") == "BLOCKED", "gate_state must be BLOCKED"


def test_summary_no_gguf():
    """Summary must report gguf_generated=false."""
    data = json.loads(SUMMARY_PATH.read_text())
    assert data.get("gguf_generated") is False, "gguf_generated must be false"


def test_summary_manual_review():
    """Summary must require manual_review_required=true."""
    data = json.loads(SUMMARY_PATH.read_text())
    assert data.get("manual_review_required") is True, "manual_review_required must be true"


def test_summary_base_model():
    """Summary must have base_model=Qwen/Qwen2.5-1.5B-Instruct."""
    data = json.loads(SUMMARY_PATH.read_text())
    assert data.get("base_model") == "Qwen/Qwen2.5-1.5B-Instruct", f"Unexpected base_model: {data.get('base_model')}"


def test_summary_micro_run():
    """Summary must report micro_run=true."""
    data = json.loads(SUMMARY_PATH.read_text())
    assert data.get("micro_run") is True, "micro_run must be true"


def test_result_doc_exists():
    """SFT v1 result document must exist."""
    assert RESULT_DOC.exists(), f"Result doc not found: {RESULT_DOC}"


def test_result_doc_completed():
    """Result doc must show COMPLETED status."""
    text = RESULT_DOC.read_text()
    assert "COMPLETED" in text, "Result doc must have COMPLETED status"


def test_result_doc_job_id():
    """Result doc must contain the actual job_id."""
    text = RESULT_DOC.read_text()
    assert "6a0501dae48bea4538b9c17a" in text, "Result doc must contain the job_id"


def test_result_doc_gate_blocked():
    """Result doc must show gate BLOCKED."""
    text = RESULT_DOC.read_text().lower()
    assert "blocked" in text, "Result doc must show gate BLOCKED"


def test_config_dataset_path():
    """Config must use dataset_path (not dataset_train)."""
    text = CONFIG_PATH.read_text()
    assert "dataset_path:" in text, "Config must have dataset_path key"
    assert "dataset_train:" not in text, "Config must not have dataset_train key"


def test_hf_wrapper_bash_c():
    """HF Jobs wrapper must use bash -c for compound commands."""
    text = HF_WRAPPER.read_text()
    assert '"bash"' in text, "HF wrapper must use bash"
    assert '"-c"' in text, "HF wrapper must use -c flag"


def test_hf_wrapper_git_clone():
    """HF Jobs wrapper must clone the repo."""
    text = HF_WRAPPER.read_text()
    assert "git clone" in text, "HF wrapper must include git clone step"


def test_hf_wrapper_micro_run():
    """HF Jobs wrapper must include --micro-run flag."""
    text = HF_WRAPPER.read_text()
    assert "--micro-run" in text, "HF wrapper must include --micro-run flag"


def test_hf_wrapper_yes_flag():
    """HF Jobs wrapper must include --yes flag."""
    text = HF_WRAPPER.read_text()
    assert '"--yes"' in text, "HF wrapper must include --yes flag"


def test_no_public_weights():
    """No public weights/adapters/GGUF in repo."""
    patterns = ["*.safetensors", "*.gguf", "adapter_model.bin"]
    for pattern in patterns:
        matches = list(PROJECT_ROOT.rglob(pattern))
        matches = [m for m in matches if ".venv" not in str(m) and "deps" not in str(m)]
        assert len(matches) == 0, f"Found public artifact: {matches}"


def test_no_secrets_in_summary():
    """Summary must not contain tokens or secrets."""
    text = SUMMARY_PATH.read_text()
    secret_patterns = [
        r"sk-proj-",
        r"ghp_",
        r"hf_[a-zA-Z]{30,}",
        r"AKIA[0-9A-Z]{16}",
    ]
    for pattern in secret_patterns:
        assert not re.search(pattern, text), f"Summary contains secret pattern: {pattern}"


def test_dataset_files_tracked():
    """Dataset build files must be tracked in git."""
    import subprocess

    result = subprocess.run(
        ["git", "ls-files", "dataset/build/kimari_sft_v1/"],
        capture_output=True,
        text=True,
        cwd=PROJECT_ROOT,
    )
    files = result.stdout.strip().split("\n")
    expected = [
        "dataset/build/kimari_sft_v1/train.jsonl",
        "dataset/build/kimari_sft_v1/validation.jsonl",
        "dataset/build/kimari_sft_v1/dataset_summary.json",
    ]
    for f in expected:
        assert f in files, f"Dataset file not tracked: {f}"
