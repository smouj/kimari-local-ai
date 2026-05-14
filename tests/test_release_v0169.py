"""Release tests for v0.1.69-alpha.

Focus: guarded full-run enablement for Kimari SFT v1 base adapter.
"""

import json
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
TRAIN_SCRIPT = PROJECT_ROOT / "training" / "scripts" / "train_sft_lora.py"
HF_SCRIPT = PROJECT_ROOT / "training" / "scripts" / "hf_jobs_sft_v1.py"
CONFIG = PROJECT_ROOT / "training" / "configs" / "kimari_runtime_15b_sft_v1.yaml"


def test_version_bumped():
    assert 'version = "0.1.69-alpha"' in (PROJECT_ROOT / "pyproject.toml").read_text()
    assert '__version__ = "0.1.69-alpha"' in (PROJECT_ROOT / "kimari" / "__init__.py").read_text()


def test_train_script_supports_full_run_flag():
    text = TRAIN_SCRIPT.read_text()
    assert "--full-run" in text
    assert "choose exactly one training mode" in text
    assert "max_steps <= 500" in text
    assert "micro_run=args.micro_run" in text
    assert '"full_run": not micro_run' in text


def test_supported_flags_lists_full_run():
    proc = subprocess.run(
        [sys.executable, str(TRAIN_SCRIPT), "--show-supported-flags", "--json"],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        check=True,
    )
    data = json.loads(proc.stdout)
    assert "--full-run" in data["supported_flags"]


def test_hf_jobs_wrapper_supports_full_run():
    text = HF_SCRIPT.read_text()
    assert "--full-run" in text
    assert "full_run=args.full_run" in text
    assert "mode_flag = \"--full-run\" if full_run else \"--micro-run\"" in text


def test_hf_jobs_full_run_command_preview():
    proc = subprocess.run(
        [
            sys.executable,
            str(HF_SCRIPT),
            "--config",
            str(CONFIG),
            "--dry-run",
            "--print-command",
            "--persist-adapter",
            "--full-run",
            "--json",
        ],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        check=True,
    )
    data = json.loads(proc.stdout)
    preview = data["hf_jobs_command_preview"]
    assert "--full-run" in preview
    assert "--micro-run" not in preview
    assert "--secrets HF_TOKEN" in preview
    assert data["max_steps"] == 100
    assert data["full_run"] is True


def test_training_config_guarded_for_first_full_run():
    config = CONFIG.read_text()
    assert "max_steps: 100" in config
    assert "gate_state: BLOCKED" in config
    assert "persist_adapter: true" in config
    assert "push_to_hub: false" in config
    assert "gguf_export_allowed: false" in config


def test_no_public_model_artifacts():
    dangerous = []
    for pattern in ("*.safetensors", "*.gguf", "adapter_model.bin"):
        for path in PROJECT_ROOT.rglob(pattern):
            if ".venv" not in path.parts and "deps" not in path.parts:
                dangerous.append(str(path))
    assert not dangerous, f"Found public artifacts: {dangerous}"
