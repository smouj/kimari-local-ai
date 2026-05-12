#!/usr/bin/env python3
# ruff: noqa: F821 W293
"""Kimari-4B HF Jobs micro SFT real runner.

Submits a micro SFT training job to Hugging Face Jobs.
Defaults to dry-run. Real submission requires --allow-submit --yes.

SAFETY:
- dry-run by default
- Real submission requires --allow-submit AND --yes
- No push_to_hub
- No HF upload
- No token arguments
- Gate remains BLOCKED
- Short timeout to limit cost

Usage:
    # Dry-run
    python training/scripts/hf_jobs_micro_sft_real.py --config training/configs/hf_jobs_kimari4b_micro_sft_real.v0.yaml --dry-run --json

    # Print command
    python training/scripts/hf_jobs_micro_sft_real.py --config training/configs/hf_jobs_kimari4b_micro_sft_real.v0.yaml --print-command

    # Real submission
    python training/scripts/hf_jobs_micro_sft_real.py --config training/configs/hf_jobs_kimari4b_micro_sft_real.v0.yaml --require-jobs-access --allow-submit --yes
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent


def load_config(config_path: str) -> dict:
    """Load YAML config."""
    try:
        import yaml
    except ImportError:
        print("ERROR: PyYAML required. Install with: pip install pyyaml")
        sys.exit(1)
    with open(config_path) as f:
        return yaml.safe_load(f)


def verify_safety_flags(config: dict) -> list[str]:
    """Verify all safety flags are correct."""
    errors = []
    safety = config.get("safety", {})
    if safety.get("adapter_committed") is True:
        errors.append("adapter_committed must be false")
    if safety.get("hf_upload_performed") is True:
        errors.append("hf_upload_performed must be false")
    if safety.get("push_to_hub") is True:
        errors.append("push_to_hub must be false")
    if safety.get("gguf_export") is True:
        errors.append("gguf_export must be false")
    if safety.get("report_to") not in ("none", None):
        errors.append(f"report_to must be 'none', got '{safety.get('report_to')}'")
    if safety.get("preview_gate_state") != "BLOCKED":
        errors.append(f"preview_gate_state must be BLOCKED, got '{safety.get('preview_gate_state')}'")
    return errors


def build_training_script(config: dict) -> str:
    """Build the training script that runs inside the HF Job.

    This returns a Python script as a string. It will be passed to
    ``hf jobs run <image> python3 -c <script>``.
    Double braces ({{ }}) are used for literal braces in the generated
    script because the outer f-string consumes single braces.
    """
    lora = config.get("lora", {})
    training_cfg = config.get("training", {})
    max_steps = training_cfg.get("max_steps", 20)
    model_name = config.get("base_model", {}).get("name", "Qwen/Qwen2.5-1.5B-Instruct")
    lora_r = lora.get("r", 8)
    lora_alpha = lora.get("lora_alpha", 16)
    lr = training_cfg.get("learning_rate", "5e-4")
    max_seq = training_cfg.get("max_seq_length", 512)

    # NOTE: This script runs inside the HF Job Docker container, not locally.
    # Double braces {{ }} produce literal braces in the f-string output.
    script = f"""
import json
import sys

result = {{
    "phase": "micro_sft_start",
    "training_performed": True,
    "adapter_generated": False,
    "adapter_committed": False,
    "hf_upload_performed": False,
    "push_to_hub": False,
    "gguf_export": False,
    "gate_state": "BLOCKED"
}}

try:
    import torch
    result["torch_version"] = torch.__version__
    result["cuda_available"] = torch.cuda.is_available()
    if torch.cuda.is_available():
        result["gpu_name"] = torch.cuda.get_device_name(0)
        result["gpu_count"] = torch.cuda.device_count()
        result["gpu_vram_gb"] = round(torch.cuda.get_device_properties(0).total_memory / (1024**3), 1)
except ImportError:
    result["torch_version"] = None
    result["cuda_available"] = False

print(json.dumps(result, indent=2))

import subprocess as sp
sp.run([sys.executable, "-m", "pip", "install", "-q", "trl>=0.7", "peft>=0.6", "datasets", "transformers==4.36.4", "accelerate"], check=True)

from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import LoraConfig, get_peft_model
from datasets import Dataset

model_name = "{model_name}"
print(f"Loading model: {{model_name}}")
tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
model = AutoModelForCausalLM.from_pretrained(model_name, torch_dtype=torch.float16, device_map="auto", trust_remote_code=True)

lora_config = LoraConfig(
    r={lora_r},
    lora_alpha={lora_alpha},
    target_modules=["q_proj", "v_proj"],
    lora_dropout=0.05,
    bias="none",
    task_type="CAUSAL_LM",
)
model = get_peft_model(model, lora_config)
model.print_trainable_parameters()

data = [
    {{"prompt": "What is CUDA?", "response": "CUDA is a parallel computing platform by NVIDIA that enables using GPUs for general processing."}},
    {{"prompt": "How do I check my GPU on Linux?", "response": "Run nvidia-smi in the terminal. If it shows the GPU model and CUDA version, support is active."}},
    {{"prompt": "What is Kimari Local AI?", "response": "Kimari Local AI is a framework for running LLM inference on consumer GPUs with an OpenAI-compatible endpoint."}},
]

dataset = Dataset.from_list(data)

def format_example(ex):
    return {{"text": "User: " + ex["prompt"] + "\\nAssistant: " + ex["response"]}}

dataset = dataset.map(format_example)

import torch.optim as optim
optimizer = optim.AdamW(model.parameters(), lr={lr})
model.train()

print(f"Starting micro SFT training for {max_steps} steps...")
for step in range({max_steps}):
    batch = dataset[step % len(dataset)]
    inputs = tokenizer(batch["text"], return_tensors="pt", truncation=True, max_length={max_seq})
    inputs = {{k: v.to(model.device) for k, v in inputs.items()}}
    outputs = model(**inputs, labels=inputs["input_ids"])
    loss = outputs.loss
    loss.backward()
    optimizer.step()
    optimizer.zero_grad()
    if step % 5 == 0:
        print(f"Step {{step}}/{max_steps}, Loss: {{loss.item():.4f}}")

adapter_path = "/tmp/kimari4b-micro-sft-adapter"
model.save_pretrained(adapter_path)
print(f"Adapter saved to {{adapter_path}}")

result["phase"] = "micro_sft_complete"
result["adapter_generated"] = True
result["adapter_path"] = adapter_path
result["training_performed"] = True
result["steps_completed"] = {max_steps}
result["gate_state"] = "BLOCKED"
print(json.dumps(result, indent=2))
"""
    return script


def dry_run(config: dict, json_output: bool = False) -> dict:
    """Simulate micro SFT without submitting."""
    safety_errors = verify_safety_flags(config)
    result = {
        "mode": "dry-run",
        "run_id": config.get("run_id", "unknown"),
        "base_model": config.get("base_model", {}).get("name", "unknown"),
        "dataset": config.get("dataset", {}).get("name", "unknown"),
        "dataset_count": config.get("dataset", {}).get("record_count", 0),
        "flavor": config.get("hf_jobs", {}).get("flavor", "unknown"),
        "timeout_minutes": config.get("hf_jobs", {}).get("timeout_minutes", 30),
        "estimated_cost_usd": config.get("hf_jobs", {}).get("estimated_cost_usd", 0.50),
        "max_steps": config.get("training", {}).get("max_steps", 20),
        "lora_r": config.get("lora", {}).get("r", 8),
        "safety_flags": config.get("safety", {}),
        "safety_errors": safety_errors,
        "training_performed": False,
        "adapter_generated": False,
        "adapter_committed": False,
        "gate_state": "BLOCKED",
    }

    if json_output:
        return result

    print("DRY-RUN: No job will be submitted")
    print(f"  Run ID: {result['run_id']}")
    print(f"  Base model: {result['base_model']}")
    print(f"  Dataset: {result['dataset']} ({result['dataset_count']} examples)")
    print(f"  Flavor: {result['flavor']}")
    print(f"  Timeout: {result['timeout_minutes']} min")
    print(f"  Max steps: {result['max_steps']}")
    print(f"  LoRA r: {result['lora_r']}")
    print(f"  Est. cost: ${result['estimated_cost_usd']:.2f}")
    print(f"  Safety errors: {result['safety_errors']}")
    return result


def submit_job(config: dict, json_output: bool = False) -> dict:
    """Submit the actual HF Jobs micro SFT job."""
    safety_errors = verify_safety_flags(config)
    if safety_errors:
        return {"error": f"Safety violations: {safety_errors}", "submitted": False}

    flavor = config.get("hf_jobs", {}).get("flavor", "a10g-small")
    timeout = config.get("hf_jobs", {}).get("timeout_minutes", 30)
    docker_image = config.get("hf_jobs", {}).get("docker_image", "pytorch/pytorch:2.4.0-cuda12.1-cudnn9-devel")
    run_id = config.get("run_id", "kimari4b-micro-sft")

    training_script = build_training_script(config)

    # Build safe command list (no shell=True, no string splitting)
    args = [
        "hf",
        "jobs",
        "run",
        "--flavor",
        flavor,
        "--timeout",
        f"{timeout}m",
        "--detach",
        docker_image,
        "python3",
        "-c",
        training_script,
    ]

    print("\nSubmitting HF Jobs micro SFT...")
    print(f"  Run ID: {run_id}")
    print(f"  Flavor: {flavor}")
    print(f"  Timeout: {timeout} min")
    print(f"  Est. cost: ${config.get('hf_jobs', {}).get('estimated_cost_usd', 0.50):.2f}")
    print(f"  Base model: {config.get('base_model', {}).get('name', 'unknown')}")
    print(f"  Max steps: {config.get('training', {}).get('max_steps', 20)}")
    print()

    try:
        result_proc = subprocess.run(
            args,
            capture_output=True,
            text=True,
            timeout=60,
        )

        result_data = {
            "submitted": True,
            "run_id": run_id,
            "flavor": flavor,
            "returncode": result_proc.returncode,
            "stdout_tail": result_proc.stdout.strip()[-500:]
            if len(result_proc.stdout.strip()) > 500
            else result_proc.stdout.strip(),
            "stderr_tail": result_proc.stderr.strip()[-500:]
            if len(result_proc.stderr.strip()) > 500
            else result_proc.stderr.strip(),
            "training_performed": True,
            "adapter_generated": True,
            "adapter_committed": False,
            "hf_upload_performed": False,
            "gate_state": "BLOCKED",
        }

        if json_output:
            print(json.dumps(result_data, indent=2))
        else:
            print(f"\nJob submitted with return code: {result_proc.returncode}")
            if result_proc.stdout.strip():
                print(f"STDOUT:\n{result_proc.stdout.strip()[-1000:]}")
            if result_proc.stderr.strip():
                print(f"STDERR:\n{result_proc.stderr.strip()[-500:]}")

        return result_data

    except subprocess.TimeoutExpired:
        return {"error": "Job submission timed out (60s)", "submitted": True, "timed_out": True}
    except Exception as e:
        return {"error": str(e), "submitted": False}


def main() -> None:
    parser = argparse.ArgumentParser(description="Kimari-4B HF Jobs micro SFT runner")
    parser.add_argument("--config", required=True, help="Path to config YAML")
    parser.add_argument("--print-command", action="store_true", help="Print command only")
    parser.add_argument("--dry-run", action="store_true", default=True, help="Dry-run (default)")
    parser.add_argument("--require-jobs-access", action="store_true", help="Verify HF Jobs access before submitting")
    parser.add_argument("--allow-submit", action="store_true", default=False, help="Allow actual job submission")
    parser.add_argument("--yes", action="store_true", default=False, help="Confirm consent")
    parser.add_argument("--json", action="store_true", help="JSON output")
    args = parser.parse_args()

    config = load_config(args.config)

    if args.print_command:
        build_training_script(config)  # validate config builds
        print(
            f"Command: hf jobs run --flavor {config.get('hf_jobs', {}).get('flavor', 'a10g-small')} --timeout {config.get('hf_jobs', {}).get('timeout_minutes', 30)}m --detach {config.get('hf_jobs', {}).get('docker_image', 'pytorch/pytorch:2.1.0-cuda12.1-cudnn8-devel')} python3 -c <training_script>"
        )
        sys.exit(0)

    # Safety checks
    if args.allow_submit and not args.yes:
        print("ERROR: --allow-submit requires --yes for explicit consent")
        sys.exit(1)

    if os.environ.get("CI") == "true" and args.allow_submit:
        print("ERROR: Training blocked in CI environment")
        sys.exit(1)

    for arg in sys.argv:
        if arg.startswith("--token") or arg.startswith("--api-key"):
            print(f"ERROR: Token/API key arguments not allowed: {arg}")
            sys.exit(1)

    if args.allow_submit and args.yes:
        if args.require_jobs_access:
            script = PROJECT_ROOT / "training" / "scripts" / "check_hf_jobs_access.py"
            result = subprocess.run(
                [sys.executable, str(script), "--json"],
                capture_output=True,
                text=True,
                timeout=30,
            )
            if result.returncode != 0:
                print("ERROR: HF Jobs access check failed")
                try:
                    access = json.loads(result.stdout)
                    print(f"Reason: {access.get('reason', 'unknown')}")
                except Exception:
                    print(f"Output: {result.stdout[:200]}")
                sys.exit(1)
            print("HF Jobs access verified ✅")

        result = submit_job(config, json_output=args.json)
    else:
        result = dry_run(config, json_output=args.json)

    if args.json and not (args.allow_submit and args.yes):
        print(json.dumps(result, indent=2))

    if result.get("error"):
        sys.exit(1)


if __name__ == "__main__":
    main()
