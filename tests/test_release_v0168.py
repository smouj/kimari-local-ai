"""Release tests for v0.1.68-alpha.

Focus: SFT v1 eval subset10 submission, adapter persisted, --secrets HF_TOKEN fix.
"""

import json
import re
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def test_version():
    pyproject = (PROJECT_ROOT / "pyproject.toml").read_text()
    assert 'version = "0.1.68-alpha"' in pyproject, "pyproject.toml version mismatch"


def test_init_version():
    init = (PROJECT_ROOT / "kimari" / "__init__.py").read_text()
    assert "__version__ = \"0.1.68-alpha\"" in init, "__init__.py version mismatch"


def test_eval_config_exists():
    config = PROJECT_ROOT / "eval" / "configs" / "kimari_runtime_15b_sft_v1_eval_subset10.yaml"
    assert config.exists(), "eval config missing"


def test_eval_config_adapter_repo():
    config = (PROJECT_ROOT / "eval" / "configs" / "kimari_runtime_15b_sft_v1_eval_subset10.yaml").read_text()
    assert "Smouj013/kimari-runtime-15b-sft-v1-adapter" in config, "adapter_repo_private missing from eval config"


def test_eval_config_version():
    config = (PROJECT_ROOT / "eval" / "configs" / "kimari_runtime_15b_sft_v1_eval_subset10.yaml").read_text()
    assert "0.1.68-alpha" in config, "eval config version not 0.1.68-alpha"


def test_eval_config_safety():
    config = (PROJECT_ROOT / "eval" / "configs" / "kimari_runtime_15b_sft_v1_eval_subset10.yaml").read_text()
    assert "gate_state:" in config and "BLOCKED" in config
    assert "public_benchmark_allowed: false" in config
    assert "manual_review_required: true" in config


def test_sft_summary_adapter_persisted():
    summary = json.loads((PROJECT_ROOT / "docs" / "assets" / "results" / "sft_v1_run_summary.json").read_text())
    assert summary["adapter_persisted_private"] is True, "adapter_persisted_private must be true"
    assert summary["adapter_private_repo"] == "Smouj013/kimari-runtime-15b-sft-v1-adapter", "adapter repo mismatch"


def test_sft_summary_training_performed():
    summary = json.loads((PROJECT_ROOT / "docs" / "assets" / "results" / "sft_v1_run_summary.json").read_text())
    assert summary["training_performed"] is True
    assert summary["adapter_generated"] is True


def test_eval_summary_ready():
    summary = json.loads(
        (PROJECT_ROOT / "reports" / "evals" / "kimari_runtime_15b_sft_v1_subset10" / "summary.json").read_text()
    )
    assert summary["status"] == "ready", f"Expected status 'ready', got '{summary['status']}'"
    assert summary["adapter_private_repo"] == "Smouj013/kimari-runtime-15b-sft-v1-adapter"
    assert summary["gate_state"] == "BLOCKED"


def test_eval_result_doc_ready():
    result = (PROJECT_ROOT / "docs" / "KIMARI_RUNTIME_15B_SFT_V1_EVAL_RESULT.md").read_text()
    assert "READY FOR EVALUATION" in result.upper(), "Eval result doc not ready"


def test_hf_jobs_sft_secrets_flag():
    """Verify --secrets HF_TOKEN is added when persist_adapter is True."""
    script = (PROJECT_ROOT / "training" / "scripts" / "hf_jobs_sft_v1.py").read_text()
    assert "--secrets" in script, "--secrets flag missing from hf_jobs_sft_v1.py"
    assert "HF_TOKEN" in script, "HF_TOKEN missing from hf_jobs_sft_v1.py"


def test_no_public_weights():
    """Ensure no .safetensors or .gguf files in repo (excluding .venv and deps)."""
    dangerous = []
    for pattern in ("*.safetensors", "*.gguf", "adapter_model.bin"):
        for path in PROJECT_ROOT.rglob(pattern):
            if ".venv" not in path.parts and "deps" not in path.parts:
                dangerous.append(str(path))
    assert not dangerous, f"Found public artifacts: {dangerous}"


def test_gate_blocked():
    gate = (PROJECT_ROOT / "docs" / "KIMARI4B_RELEASE_GATE.md").read_text()
    assert "BLOCKED" in gate, "Gate must be BLOCKED"