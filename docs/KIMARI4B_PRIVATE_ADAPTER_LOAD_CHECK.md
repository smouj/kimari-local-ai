# Kimari-4B Private Adapter Load Check

> How we verify that a LoRA adapter loads correctly on its base model.

## Purpose

The load check validates that:

1. The adapter files are intact (not corrupted)
2. The adapter is compatible with its base model
3. The model + adapter can generate text (basic sanity check)

## What Load Check Is NOT

- **Not a benchmark** — Does not measure quality, accuracy, or capability
- **Not an evaluation** — Does not compare base vs adapter performance
- **Not a release criterion** — Passing load check does NOT advance the gate

## How It Works

```python
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel

# 1. Load base model
tokenizer = AutoTokenizer.from_pretrained("Qwen/Qwen2.5-1.5B-Instruct")
model = AutoModelForCausalLM.from_pretrained("Qwen/Qwen2.5-1.5B-Instruct", ...)

# 2. Load adapter on top
model = PeftModel.from_pretrained(model, "/tmp/kimari4b-micro-sft-adapter")
# OR from private HF repo:
# model = PeftModel.from_pretrained(model, "Smouj013/kimari4b-micro-sft-adapter-v0")

# 3. Generate a test prompt
response = model.generate(...)
```

## Results Format

```json
{
  "adapter_load_success": true,
  "generation_success": true,
  "error_sanitized": null
}
```

- `adapter_load_success`: Whether `PeftModel.from_pretrained()` succeeded
- `generation_success`: Whether `model.generate()` produced output
- `error_sanitized`: Error class name only (no private paths, no tokens)

## Running Load Check

```bash
# From local directory
python training/scripts/check_private_adapter_load.py \
    --base-model Qwen/Qwen2.5-1.5B-Instruct \
    --adapter-dir /tmp/kimari4b-micro-sft-adapter \
    --json

# From HF private repo
python training/scripts/check_private_adapter_load.py \
    --base-model Qwen/Qwen2.5-1.5B-Instruct \
    --adapter-repo Smouj013/kimari4b-micro-sft-adapter-v0 \
    --json
```

## Gate

**BLOCKED** — Load check does not advance the gate.