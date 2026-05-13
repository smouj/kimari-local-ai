#!/usr/bin/env python3
# ruff: noqa: E402
"""Kimari-4B Micro SFT Persisted Training Script.

Runs inside HF Jobs container.
Steps: install deps, verify stack, load model, train LoRA, save adapter, load check, upload private.
"""

import hashlib
import subprocess
import sys
from pathlib import Path

print("=== Kimari-4B Micro SFT Persisted v0 ===")

# Step 1: Install dependencies
print("Step 1: Install dependencies")
subprocess.run(
    [
        sys.executable,
        "-m",
        "pip",
        "install",
        "-q",
        "transformers>=4.46",
        "peft>=0.13",
        "trl>=0.12",
        "accelerate>=1.1",
        "datasets>=3.0",
        "safetensors>=0.4",
        "huggingface_hub",
    ],
    check=True,
)

# Step 2: Verify stack
print("Step 2: Verify stack")
import torch  # noqa: E402

print(f"  PyTorch: {torch.__version__}")
print(f"  CUDA available: {torch.cuda.is_available()}")
if torch.cuda.is_available():
    print(f"  GPU: {torch.cuda.get_device_name(0)}")
    print(f"  VRAM: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.1f} GB")

import peft  # noqa: E402
import transformers  # noqa: E402
import trl  # noqa: E402

print(f"  transformers: {transformers.__version__}")
print(f"  peft: {peft.__version__}")
print(f"  trl: {trl.__version__}")

# Step 3: Load model and tokenizer
print("Step 3: Load model and tokenizer")
from transformers import AutoModelForCausalLM, AutoTokenizer

BASE_MODEL = "Qwen/Qwen2.5-1.5B-Instruct"
OUTPUT_DIR = "/tmp/kimari4b-micro-sft-adapter"
PRIVATE_REPO = "Smouj013/kimari4b-micro-sft-adapter-v0"

tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL)
model = AutoModelForCausalLM.from_pretrained(BASE_MODEL, torch_dtype=torch.float16, device_map="auto")

# Step 4: Apply LoRA
print("Step 4: Apply LoRA")
from peft import LoraConfig, get_peft_model

lora_config = LoraConfig(
    r=8,
    lora_alpha=16,
    target_modules=["q_proj", "v_proj"],
    task_type="CAUSAL_LM",
)
model = get_peft_model(model, lora_config)
model.print_trainable_parameters()

# Step 5: Create inline dataset
print("Step 5: Create inline dataset (21 examples)")
examples = [
    {"instruction": "Detecta si hay GPU disponible", "response": "Usa torch.cuda.is_available() para detectar GPU."},
    {
        "instruction": "Lista modelos GGUF compatibles",
        "response": "Kimari detecta modelos .gguf en el directorio de modelos configurado.",
    },
    {
        "instruction": "Verifica estado del servidor local",
        "response": "Ejecuta kimari doctor para verificar el estado completo del servidor.",
    },
]
from datasets import Dataset

train_data = Dataset.from_list(examples * 7)
print(f"  Dataset size: {len(train_data)}")


def format_example(example):
    return {"text": f"User: {example['instruction']}\nAssistant: {example['response']}"}


train_data = train_data.map(format_example)

# Step 6: Train (LoRA SFT)
print("Step 6: Train (LoRA SFT, 20 steps)")
from trl import SFTConfig, SFTTrainer

training_args = SFTConfig(
    output_dir=OUTPUT_DIR,
    max_steps=20,
    per_device_train_batch_size=4,
    learning_rate=2e-4,
    logging_steps=5,
    save_steps=10,
    report_to="none",
    dataset_text_field="text",
    max_seq_length=512,
)
trainer = SFTTrainer(model=model, args=training_args, train_dataset=train_data)
trainer.train()

# Step 7: Save adapter
print("Step 7: Save adapter")
model.save_pretrained(OUTPUT_DIR)
tokenizer.save_pretrained(OUTPUT_DIR)

# Step 8: Verify adapter files
print("Step 8: Verify adapter files")
adapter_path = Path(OUTPUT_DIR)
adapter_files = list(adapter_path.glob("*"))
print(f"  Files: {[f.name for f in adapter_files]}")

adapter_model_path = adapter_path / "adapter_model.safetensors"
adapter_size = 0
adapter_hash = ""
if adapter_model_path.exists():
    adapter_size = adapter_model_path.stat().st_size
    adapter_hash = hashlib.sha256(adapter_model_path.read_bytes()).hexdigest()
    print(f"  adapter_model.safetensors: {adapter_size} bytes, sha256={adapter_hash[:16]}...")
else:
    print("  WARNING: adapter_model.safetensors not found!")

# Step 9: Adapter load check
print("Step 9: Adapter load check")
adapter_load_ok = False
generation_ok = False
try:
    from peft import PeftModel

    base_model_2 = AutoModelForCausalLM.from_pretrained(BASE_MODEL, torch_dtype=torch.float16, device_map="auto")
    loaded_model = PeftModel.from_pretrained(base_model_2, OUTPUT_DIR)
    print("  Adapter loaded successfully!")
    adapter_load_ok = True

    test_prompt = "User: ¿Qué es Kimari?\nAssistant:"
    inputs = tokenizer(test_prompt, return_tensors="pt").to(loaded_model.device)
    with torch.no_grad():
        outputs = loaded_model.generate(**inputs, max_new_tokens=20, do_sample=False)
    response = tokenizer.decode(outputs[0], skip_special_tokens=True)
    print(f"  Test generation: {response[:80]}...")
    generation_ok = True
except Exception as e:
    print(f"  Adapter load check error: {type(e).__name__}")
    print("  adapter_load_check: PARTIAL")

# Step 10: Upload to private repo
print("Step 10: Upload to private repo")
adapter_persisted = False
try:
    from huggingface_hub import HfApi

    api = HfApi()
    api.create_repo(repo_id=PRIVATE_REPO, private=True, exist_ok=True)
    api.upload_folder(
        folder_path=OUTPUT_DIR,
        repo_id=PRIVATE_REPO,
        commit_message="Micro SFT persisted v0 adapter",
    )
    print(f"  Uploaded to private repo: {PRIVATE_REPO}")
    adapter_persisted = True
except Exception as e:
    print(f"  Private upload error: {type(e).__name__}: {str(e)[:100]}")
    print("  adapter_persisted_private: false (upload failed)")

# Summary
print("\n=== SUMMARY ===")
summary = {
    "run_id": "kimari4b-hfjobs-micro-sft-persisted-v0",
    "status": "completed",
    "training_performed": True,
    "adapter_generated": adapter_model_path.exists(),
    "adapter_persisted_private": adapter_persisted,
    "adapter_private_repo": PRIVATE_REPO if adapter_persisted else "",
    "adapter_hash": adapter_hash[:32] if adapter_hash else "",
    "adapter_size_bytes": adapter_size,
    "adapter_load_check": adapter_load_ok,
    "generation_success": generation_ok,
    "adapter_committed_public": False,
    "hf_public_upload_performed": False,
    "gguf_generated": False,
    "gate_state": "BLOCKED",
    "manual_review_required": True,
    "auto_gate_transition": False,
}
for k, v in summary.items():
    print(f"  {k}: {v}")

print("\n=== DONE ===")
