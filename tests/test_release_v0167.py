"""Release tests for v0.1.67-alpha.

SFT v1 micro-run with --persist-adapter:
- hf_jobs_sft_v1.py supports --persist-adapter and --adapter-repo flags
- huggingface_hub added to training requirements
- Private HF repo Smouj013/kimari-runtime-15b-sft-v1-adapter created
- Config has persist_adapter and adapter_repo fields
- Adapter upload step included in HF Jobs command
"""

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

HF_JOBS_SCRIPT = PROJECT_ROOT / "training" / "scripts" / "hf_jobs_sft_v1.py"
TRAINING_CONFIG = PROJECT_ROOT / "training" / "configs" / "kimari_runtime_15b_sft_v1.yaml"
TRAINING_REQS = PROJECT_ROOT / "training" / "requirements-training.txt"


def test_version_is_0167():
    """Package version must be 0.1.67-alpha."""
    import kimari

    assert kimari.__version__ == "0.1.67-alpha", f"Expected 0.1.67-alpha, got {kimari.__version__}"


def test_pyproject_version():
    """pyproject.toml version must be 0.1.67-alpha."""
    pyproject = (PROJECT_ROOT / "pyproject.toml").read_text()
    assert 'version = "0.1.67-alpha"' in pyproject, "pyproject.toml version mismatch"


def test_hf_jobs_persist_adapter_flag():
    """hf_jobs_sft_v1.py must support --persist-adapter flag."""
    script = HF_JOBS_SCRIPT.read_text()
    assert "--persist-adapter" in script, "--persist-adapter flag not found in hf_jobs script"
    assert "persist_adapter" in script, "persist_adapter handling not found"


def test_hf_jobs_adapter_repo_flag():
    """hf_jobs_sft_v1.py must support --adapter-repo flag."""
    script = HF_JOBS_SCRIPT.read_text()
    assert "--adapter-repo" in script, "--adapter-repo flag not found in hf_jobs script"
    assert "adapter_repo" in script, "adapter_repo handling not found"


def test_config_persist_adapter():
    """Training config must have persist_adapter field."""
    config = TRAINING_CONFIG.read_text()
    assert "persist_adapter" in config, "persist_adapter not found in config"
    assert "adapter_repo" in config, "adapter_repo not found in config"


def test_config_persist_adapter_true():
    """persist_adapter must be true in config."""
    config = TRAINING_CONFIG.read_text()
    assert "persist_adapter: true" in config, "persist_adapter must be true"


def test_config_adapter_repo_value():
    """adapter_repo must point to the private repo."""
    config = TRAINING_CONFIG.read_text()
    assert "Smouj013/kimari-runtime-15b-sft-v1-adapter" in config, (
        "adapter_repo must be Smouj013/kimari-runtime-15b-sft-v1-adapter"
    )


def test_huggingface_hub_in_requirements():
    """huggingface_hub must be in training requirements."""
    reqs = TRAINING_REQS.read_text()
    assert "huggingface_hub" in reqs, "huggingface_hub not found in training requirements"


def test_no_private_kwarg_in_upload():
    """upload_folder call must NOT use private=True kwarg (not supported)."""
    script = HF_JOBS_SCRIPT.read_text()
    # Check that the upload command doesn't use private=True in actual code
    # (comments mentioning it are OK)
    lines_with_private_true = [
        line for line in script.splitlines() if "private=True" in line and not line.strip().startswith("#")
    ]
    assert len(lines_with_private_true) == 0, (
        f"upload_folder should not use private=True in code: {lines_with_private_true}"
    )


def test_safety_still_blocks_public():
    """Safety checks must still block public release."""
    script = HF_JOBS_SCRIPT.read_text()
    assert "push_to_hub" in script, "push_to_hub safety check not found"
    assert "public_release_allowed" in script, "public_release_allowed safety check not found"


def test_gate_still_blocked():
    """Gate state must still be BLOCKED in config."""
    config = TRAINING_CONFIG.read_text()
    assert "gate_state: BLOCKED" in config, "gate_state must remain BLOCKED"


def test_run_history_has_run_6():
    """Run history must include Run 6 (persist-adapter re-run)."""
    history = (PROJECT_ROOT / "docs" / "KIMARI4B_RUN_HISTORY.md").read_text()
    assert "Run 6" in history, "Run 6 not found in run history"
    assert "persist-adapter" in history, "persist-adapter not mentioned in run history"


def test_result_doc_mentions_persist():
    """SFT v1 result doc must mention adapter persistence in progress."""
    result = (PROJECT_ROOT / "docs" / "KIMARI_RUNTIME_15B_SFT_V1_RESULT.md").read_text()
    assert "IN PROGRESS" in result or "persist" in result, "Result doc must mention adapter persistence status"


def test_changelog_has_0167():
    """CHANGELOG must include v0.1.67-alpha entry."""
    changelog = (PROJECT_ROOT / "CHANGELOG.md").read_text()
    assert "0.1.67-alpha" in changelog, "CHANGELOG missing v0.1.67-alpha entry"
