"""Release tests for v0.1.73-alpha.

Focus: private scoring result and guarded 500-step improvement path.
"""

import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SUMMARY = PROJECT_ROOT / "reports" / "evals" / "kimari_runtime_15b_sft_v1_scoring_subset30" / "summary.json"
CONFIG = PROJECT_ROOT / "training" / "configs" / "kimari_runtime_15b_sft_v1.yaml"


def test_version_bumped():
    assert 'version = "0.1.73-alpha"' in (PROJECT_ROOT / "pyproject.toml").read_text()
    assert '__version__ = "0.1.73-alpha"' in (PROJECT_ROOT / "kimari" / "__init__.py").read_text()


def test_private_scoring_summary_sanitized_and_adapter_wins():
    data = json.loads(SUMMARY.read_text())
    assert data["status"] == "completed"
    assert data["score_status"] == "scored_private_proxy"
    assert data["raw_outputs_committed"] is False
    assert data["public_benchmark_allowed"] is False
    assert data["gate_state"] == "BLOCKED"
    assert data["adapter"]["proxy_score"] > data["baseline"]["proxy_score"]
    assert data["adapter_proxy_wins"] > data["baseline_proxy_wins"]
    assert data["decision"]["is_adapter_better_than_base"] is True
    assert data["decision"]["is_adapter_much_better_than_base"] is False


def test_no_raw_outputs_committed_in_scoring_report():
    text = SUMMARY.read_text().lower()
    assert "generated" not in text
    assert "prompt" not in text
    assert '"ideal"' not in text
    assert "raw_outputs_private.json" in text


def test_500_step_config_guarded():
    text = CONFIG.read_text()
    assert "max_steps: 500" in text
    assert "gate_state: BLOCKED" in text
    assert "public_release_allowed: false" in text
    assert "hf_public_upload_allowed: false" in text
    assert "gguf_export_allowed: false" in text
    assert "persist_adapter: true" in text


def test_no_public_model_artifacts():
    dangerous = []
    for pattern in ("*.safetensors", "*.gguf", "adapter_model.bin"):
        for path in PROJECT_ROOT.rglob(pattern):
            if ".venv" not in path.parts and "deps" not in path.parts:
                dangerous.append(str(path))
    assert not dangerous, f"Found public artifacts: {dangerous}"
