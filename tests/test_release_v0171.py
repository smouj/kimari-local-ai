"""Release tests for v0.1.71-alpha.

Focus: private scoring/quality eval infrastructure.
"""

import json
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SCRIPT = PROJECT_ROOT / "eval" / "scripts" / "hf_jobs_run_kimari_scoring_eval.py"
CONFIG = PROJECT_ROOT / "eval" / "configs" / "kimari_runtime_15b_sft_v1_eval_subset10.yaml"


def test_version_bumped():
    assert 'version = "0.1.71-alpha"' in (PROJECT_ROOT / "pyproject.toml").read_text()
    assert '__version__ = "0.1.71-alpha"' in (PROJECT_ROOT / "kimari" / "__init__.py").read_text()


def test_scoring_script_exists_and_has_safety_markers():
    text = SCRIPT.read_text()
    assert "raw_outputs_private.json" in text
    assert "scoring_summary.json" in text
    assert "SCORING_SUMMARY_JSON_START" in text
    assert "public_benchmark_allowed" in text
    assert "gate_state" in text
    assert "BLOCKED" in text


def test_scoring_script_dry_run_json():
    proc = subprocess.run(
        [sys.executable, str(SCRIPT), "--config", str(CONFIG), "--subset-size", "30", "--dry-run", "--json"],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        check=True,
    )
    data = json.loads(proc.stdout)
    assert data["run_type"] == "dry-run"
    assert data["subset_size"] == 30
    assert data["raw_outputs_committed"] is False
    assert data["public_benchmark_allowed"] is False
    assert data["gate_state"] == "BLOCKED"
    assert "hf jobs uv run" in data["command"]


def test_scoring_script_uses_private_adapter_repo():
    text = SCRIPT.read_text()
    config = CONFIG.read_text()
    assert "adapter_repo_private" in text
    assert "Smouj013/kimari-runtime-15b-sft-v1-adapter" in config


def test_no_public_model_artifacts():
    dangerous = []
    for pattern in ("*.safetensors", "*.gguf", "adapter_model.bin"):
        for path in PROJECT_ROOT.rglob(pattern):
            if ".venv" not in path.parts and "deps" not in path.parts:
                dangerous.append(str(path))
    assert not dangerous, f"Found public artifacts: {dangerous}"
