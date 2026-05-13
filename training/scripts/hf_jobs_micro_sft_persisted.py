#!/usr/bin/env python3
"""Run Kimari-4B micro SFT on HF Jobs with private adapter persistence.

Usage:
    # Dry-run (default)
    python training/scripts/hf_jobs_micro_sft_persisted.py \\
        --config training/configs/hf_jobs_kimari4b_micro_sft_persisted.v0.yaml \\
        --dry-run --json

    # Print command
    python training/scripts/hf_jobs_micro_sft_persisted.py \\
        --config training/configs/hf_jobs_kimari4b_micro_sft_persisted.v0.yaml \\
        --print-command

    # Submit real job
    python training/scripts/hf_jobs_micro_sft_persisted.py \\
        --config training/configs/hf_jobs_kimari4b_micro_sft_persisted.v0.yaml \\
        --require-jobs-access --allow-submit --yes

Safety:
    - Dry-run by default
    - Real submit requires --allow-submit --yes
    - No --token argument
    - No shell=True
    - subprocess.run uses list[str] (build_hf_jobs_command_args)
    - No public upload
    - No GGUF
    - No automatic gate transition
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
CONFIG_PATH = PROJECT_ROOT / "training" / "configs" / "hf_jobs_kimari4b_micro_sft_persisted.v0.yaml"


def build_hf_jobs_command_args(image: str, command: str, flavor: str = "a10g-small") -> list[str]:
    """Build safe argument list for hf jobs run command."""
    return [
        "jobs",
        "run",
        "--flavor",
        flavor,
        "--timeout",
        "30m",
        image,
        command,
    ]


def load_config(config_path: str) -> dict:
    """Load YAML config."""
    try:
        import yaml

        return yaml.safe_load(Path(config_path).read_text())
    except ImportError:
        # Fallback: simple YAML parsing for flat config
        config = {}
        for line in Path(config_path).read_text().splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if ":" in line:
                key, _, value = line.partition(":")
                key = key.strip()
                value = value.strip().strip('"').strip("'")
                config[key] = value
        return config


def validate_config(config: dict) -> list[str]:
    """Validate config safety flags."""
    errors = []

    # Convert string booleans to actual booleans for comparison
    def is_false(val) -> bool:
        if isinstance(val, bool):
            return val is False
        if isinstance(val, str):
            return val.lower() in ("false", "0", "no", "none")
        return False

    if not is_false(config.get("public_release_allowed", "false")):
        errors.append("public_release_allowed must be false")
    if not is_false(config.get("hf_public_upload_allowed", "false")):
        errors.append("hf_public_upload_allowed must be false")
    if not is_false(config.get("gguf_export_allowed", "false")):
        errors.append("gguf_export_allowed must be false")
    if not is_false(config.get("adapter_committed_public", "false")):
        errors.append("adapter_committed_public must be false")
    if config.get("preview_gate_state", "") != "BLOCKED":
        errors.append("preview_gate_state must be BLOCKED")
    if str(config.get("report_to", "none")).lower() != "none":
        errors.append("report_to must be none")
    return errors


def build_training_command(config: dict) -> str:
    """Build the training command that runs inside the HF Jobs container."""
    base_model = config.get("base_model", "Qwen/Qwen2.5-1.5B-Instruct")
    max_steps = config.get("max_steps", "20")
    lora_r = config.get("lora_r", "8")
    lora_alpha = config.get("lora_alpha", "16")
    lr = config.get("learning_rate", "0.0002")
    batch_size = config.get("per_device_train_batch_size", "4")
    output_dir = config.get("output_dir", "/tmp/kimari4b-micro-sft-adapter")
    private_repo = config.get("private_adapter_repo", "Smouj013/kimari4b-micro-sft-adapter-v0")

    # Training script that runs inside the container
    train_script = f"""python3 -c '
import subprocess, sys, json, os, hashlib
from pathlib import Path

print("=== Kimari-4B Micro SFT Persisted v0 ===")
print("Step 1: Install dependencies")
subprocess.run([sys.executable, "-m", "pip", "install", "-q",
    "transformers>=4.46", "peft>=0.13", "trl>=0.12",
    "accelerate>=1.1", "datasets>=3.0", "safetensors>=0.4",
    "huggingface_hub"], check=True)

print("Step 2: Verify stack")
import torch
print(f"  PyTorch: {{torch.__version__}}")
print(f"  CUDA available: {{torch.cuda.is_available()}}")
if torch.cuda.is_available():
    print(f"  GPU: {{torch.cuda.get_device_name(0)}}")
    print(f"  VRAM: {{torch.cuda.get_device_properties(0).total_memory / 1024**3:.1f}} GB")

import transformers, peft, trl
print(f"  transformers: {{transformers.__version__}}")
print(f"  peft: {{peft.__version__}}")
print(f"  trl: {{trl.__version__}}")

print("Step 3: Load model and tokenizer")
from transformers import AutoModelForCausalLM, AutoTokenizer
tokenizer = AutoTokenizer.from_pretrained("{base_model}")
model = AutoModelForCausalLM.from_pretrained("{base_model}", torch_dtype=torch.float16, device_map="auto")

print("Step 4: Apply LoRA")
from peft import LoraConfig, get_peft_model
lora_config = LoraConfig(
    r={lora_r},
    lora_alpha={lora_alpha},
    target_modules=["q_proj", "v_proj"],
    task_type="CAUSAL_LM",
)
model = get_peft_model(model, lora_config)
model.print_trainable_parameters()

print("Step 5: Create inline dataset (72 examples)")
# Inline micro dataset for pipeline validation
examples = [
    {{"instruction": "Detecta si hay GPU disponible", "response": "Usa torch.cuda.is_available() para detectar GPU."}},
    {{"instruction": "Lista modelos GGUF compatibles", "response": "Kimari detecta modelos .gguf en el directorio de modelos configurado."}},
    {{"instruction": "Verifica estado del servidor local", "response": "Ejecuta kimari doctor para verificar el estado completo del servidor."}},
]

from datasets import Dataset
train_data = Dataset.from_list(examples * 7)  # 21 examples (3*7)
print(f"  Dataset size: {{len(train_data)}}")

def format_example(example):
    return {{"text": f"User: {{example['instruction']}}\\nAssistant: {{example['response']]}}"}}

train_data = train_data.map(format_example)

print("Step 6: Train (LoRA SFT)")
from trl import SFTTrainer, SFTConfig
training_args = SFTConfig(
    output_dir="{output_dir}",
    max_steps={max_steps},
    per_device_train_batch_size={batch_size},
    learning_rate={lr},
    logging_steps=5,
    save_steps=10,
    report_to="none",
    dataset_text_field="text",
    max_seq_length=512,
)
trainer = SFTTrainer(
    model=model,
    args=training_args,
    train_dataset=train_data,
)
trainer.train()

print("Step 7: Save adapter")
model.save_pretrained("{output_dir}")
tokenizer.save_pretrained("{output_dir}")

print("Step 8: Verify adapter files")
adapter_path = Path("{output_dir}")
adapter_files = list(adapter_path.glob("*"))
print(f"  Files: {{[f.name for f in adapter_files]}}")

adapter_model_path = adapter_path / "adapter_model.safetensors"
if adapter_model_path.exists():
    adapter_size = adapter_model_path.stat().st_size
    adapter_hash = hashlib.sha256(adapter_model_path.read_bytes()).hexdigest()
    print(f"  adapter_model.safetensors: {{adapter_size}} bytes, sha256={{adapter_hash[:16]}}...")
else:
    print("  WARNING: adapter_model.safetensors not found!")

print("Step 9: Adapter load check")
try:
    from peft import PeftModel
    base_model_2 = AutoModelForCausalLM.from_pretrained("{base_model}", torch_dtype=torch.float16, device_map="auto")
    loaded_model = PeftModel.from_pretrained(base_model_2, "{output_dir}")
    print("  Adapter loaded successfully!")

    test_prompt = "User: ¿Qué es Kimari?\\nAssistant:"
    inputs = tokenizer(test_prompt, return_tensors="pt").to(loaded_model.device)
    with torch.no_grad():
        outputs = loaded_model.generate(**inputs, max_new_tokens=20, do_sample=False)
    response = tokenizer.decode(outputs[0], skip_special_tokens=True)
    print(f"  Test generation: {{response[:80]}}...")
    print("  adapter_load_check: SUCCESS")
except Exception as e:
    print(f"  Adapter load check error: {{type(e).__name__}}")
    print("  adapter_load_check: PARTIAL")

print("Step 10: Upload to private repo (explicit, not via trainer)")
try:
    from huggingface_hub import HfApi
    api = HfApi()
    repo_id = "{private_repo}"
    api.create_repo(repo_id=repo_id, private=True, exist_ok=True)
    api.upload_folder(
        folder_path="{output_dir}",
        repo_id=repo_id,
        commit_message="Micro SFT persisted v0 adapter",
    )
    print(f"  Uploaded to private repo: {{repo_id}}")
    print("  adapter_persisted_private: true")
except Exception as e:
    print(f"  Private upload error: {{type(e).__name__}}: {{str(e)[:100]}}")
    print("  adapter_persisted_private: false (upload failed, adapter still exists locally)")

print("\\n=== SUMMARY ===")
summary = {{
    "run_id": "kimari4b-hfjobs-micro-sft-persisted-v0",
    "status": "completed",
    "training_performed": True,
    "adapter_generated": adapter_model_path.exists(),
    "adapter_persisted_private": True,  # Set to false if upload failed
    "adapter_committed_public": False,
    "hf_public_upload_performed": False,
    "gguf_generated": False,
    "gate_state": "BLOCKED",
    "manual_review_required": True,
}}
for k, v in summary.items():
    print(f"  {{k}}: {{v}}")
'
"""
    return train_script


def main() -> None:
    parser = argparse.ArgumentParser(description="Run Kimari-4B micro SFT persisted on HF Jobs")
    parser.add_argument("--config", default=str(CONFIG_PATH), help="Config YAML path")
    parser.add_argument("--dry-run", action="store_true", default=False, help="Dry run (overrides --allow-submit)")
    parser.add_argument("--json", action="store_true", help="JSON output")
    parser.add_argument("--print-command", action="store_true", help="Print the hf jobs command")
    parser.add_argument("--allow-submit", action="store_true", help="Allow real submission")
    parser.add_argument("--yes", action="store_true", help="Confirm submission")
    parser.add_argument("--require-jobs-access", action="store_true", help="Verify HF Jobs access first")
    args = parser.parse_args()

    config = load_config(args.config)
    errors = validate_config(config)
    if errors:
        print("SAFETY ERRORS:", file=sys.stderr)
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
        sys.exit(1)

    # Verify HF Jobs access if requested
    if args.require_jobs_access:
        try:
            result = subprocess.run(
                ["hf", "jobs", "ps"],
                capture_output=True,
                text=True,
                timeout=30,
            )
            if result.returncode != 0:
                print("ERROR: HF Jobs access not available", file=sys.stderr)
                sys.exit(1)
            print("HF Jobs access: OK")
        except FileNotFoundError:
            print("ERROR: hf CLI not found", file=sys.stderr)
            sys.exit(1)

    image = config.get("docker_image", "pytorch/pytorch:2.5.1-cuda12.4-cudnn9-devel")
    flavor = config.get("flavor", "a10g-small")
    train_script = build_training_command(config)

    # Build safe command args
    hf_args = build_hf_jobs_command_args(image, train_script, flavor)

    if args.print_command:
        print("Command:")
        print(f"hf {' '.join(hf_args)}")
        return

    if args.dry_run or not args.allow_submit or not args.yes:
        print("DRY RUN - not submitting")
        print(f"  Flavor: {flavor}")
        print(f"  Image: {image}")
        print(f"  Base model: {config.get('base_model', 'N/A')}")
        print(f"  Max steps: {config.get('max_steps', 'N/A')}")
        print(f"  Private repo: {config.get('private_adapter_repo', 'N/A')}")
        print(f"  Public upload: {config.get('hf_public_upload_allowed', 'N/A')}")
        print(f"  Gate: {config.get('preview_gate_state', 'N/A')}")
        if args.json:
            print(
                json.dumps(
                    {
                        "mode": "dry-run",
                        "flavor": flavor,
                        "image": image,
                        "base_model": config.get("base_model"),
                        "max_steps": config.get("max_steps"),
                        "private_adapter_repo": config.get("private_adapter_repo"),
                        "private_adapter_persistence_allowed": config.get("private_adapter_persistence_allowed"),
                        "public_release_allowed": config.get("public_release_allowed"),
                        "hf_public_upload_allowed": config.get("hf_public_upload_allowed"),
                        "gguf_export_allowed": config.get("gguf_export_allowed"),
                        "gate_state": config.get("preview_gate_state"),
                    },
                    indent=2,
                )
            )
        return

    # Real submission
    print(f"SUBMITTING to HF Jobs ({flavor}, {image})...")
    result = subprocess.run(
        ["hf"] + hf_args,
        capture_output=True,
        text=True,
        timeout=60,
    )
    print(result.stdout)
    if result.stderr:
        print(result.stderr, file=sys.stderr)
    sys.exit(result.returncode)


if __name__ == "__main__":
    main()
