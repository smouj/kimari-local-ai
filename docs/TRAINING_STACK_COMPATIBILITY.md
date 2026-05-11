# Training Stack Compatibility — Kimari Local AI

> **Document Type:** Reference guide for training dependency compatibility and TRL/SFTTrainer version differences  
> **Version:** v0.1.35-alpha  
> **Date:** 2026-06-03  
> **Gate State:** BLOCKED — no public release, no HF upload

---

## 1. Overview

The Kimari Local AI training pipeline relies on a specific set of Python libraries with known API compatibility differences between versions. This document explains:

- **Minimum recommended versions** for each training dependency
- **How to check your training stack** with `check_training_stack.py`
- **Common TRL/SFTTrainer compatibility problems** and how they manifest
- **How `train_sft_lora.py` handles these automatically** (v0.1.34+)

The training stack is **not installed by default** — it is separate from the core CLI runtime. See `training/requirements-training.txt` for the full list.

**No downloads, no model loading, no training** occur during a compatibility check. The checker inspects installed Python packages and their API signatures only.

---

## 2. Minimum Recommended Versions

| Package | Minimum Version | Purpose |
|---------|----------------|---------|
| `torch` | >= 2.1.0 | GPU training operations, CUDA support |
| `transformers` | >= 4.36.0 | Model loading, tokenization, TrainingArguments |
| `datasets` | >= 2.14.0 | Loading and processing training data |
| `accelerate` | >= 0.25.0 | Mixed precision, gradient accumulation, multi-GPU |
| `peft` | >= 0.7.0 | LoRA, QLoRA, parameter-efficient fine-tuning |
| `trl` | >= 0.7.0 | SFTTrainer, DPOTrainer, training loop integration |
| `safetensors` | >= 0.4.0 | Secure tensor serialization for adapter weights |
| `pyyaml` | >= 6.0 | Parsing training configuration YAML files |

**Important:** TRL >= 0.7.0 is required, but note that newer versions (0.12+) may use `processing_class` instead of `tokenizer` as a parameter name. See Section 4 for details.

---

## 3. Running check_training_stack.py

The compatibility checker inspects your Python environment for SFT LoRA training readiness. It performs **14 checks** covering Python version, core library imports, SFTTrainer import, TrainingArguments signature, and API compatibility.

### Basic Usage

```bash
python training/scripts/check_training_stack.py
```

Outputs a human-readable table with PASS/FAIL/WARN per check.

### JSON Output

```bash
python training/scripts/check_training_stack.py --json
```

Outputs structured JSON with all 14 checks, a `compatibility` dict, and a `warnings` list. Useful for scripting and CI integration.

### Verbose Output

```bash
python training/scripts/check_training_stack.py --verbose
```

Adds full parameter listings for `TrainingArguments` and `SFTTrainer.__init__` signatures.

### Key Behaviors

- **Exit code 0 always** — This is an informational tool, not a gate
- **Independent checks** — If one import fails, the script continues to the next
- **No downloads** — No model downloads, no network calls
- **No training** — No GPU operations, no training runs
- **`ready_for_training`** flag in JSON output — `true` only if ALL core imports succeed AND `TrainingArguments` does NOT accept `max_seq_length`

---

## 4. Common TRL/SFTTrainer Compatibility Problems

These are the most frequent issues encountered when running SFT LoRA training across different TRL/transformers versions.

### 4.1 max_seq_length Belongs in SFTTrainer, NOT TrainingArguments

**Problem:** Passing `max_seq_length` to `TrainingArguments()` raises a `TypeError` in most versions. The `max_seq_length` parameter belongs in `SFTTrainer()`, not `TrainingArguments()`.

**Wrong:**
```python
from transformers import TrainingArguments

args = TrainingArguments(
    output_dir="./output",
    max_seq_length=512,  # ERROR: not a valid parameter
)
```

**Right:**
```python
from trl import SFTTrainer

trainer = SFTTrainer(
    model=model,
    args=training_args,  # TrainingArguments WITHOUT max_seq_length
    max_seq_length=512,  # Correct: belongs in SFTTrainer
    ...
)
```

**Why it matters:** `max_seq_length` controls the sequence length for dataset packing in SFTTrainer. It is not a general training argument — it is specific to SFTTrainer's data processing pipeline.

### 4.2 tokenizer vs processing_class Parameter Naming

**Problem:** Newer versions of TRL (0.12+) renamed the `tokenizer` parameter to `processing_class` in `SFTTrainer.__init__`. Using the wrong name causes a `TypeError`.

**Older TRL (< 0.12):**
```python
trainer = SFTTrainer(
    model=model,
    tokenizer=tokenizer,  # Correct for older TRL
    ...
)
```

**Newer TRL (>= 0.12):**
```python
trainer = SFTTrainer(
    model=model,
    processing_class=tokenizer,  # Correct for newer TRL
    ...
)
```

**How to handle both:** Inspect the `SFTTrainer.__init__` signature and adapt:
```python
import inspect
from trl import SFTTrainer

sig = inspect.signature(SFTTrainer.__init__)
if "processing_class" in sig.parameters:
    kwargs["processing_class"] = tokenizer
else:
    kwargs["tokenizer"] = tokenizer
```

### 4.3 dataset_text_field Requirement for SFTTrainer

**Problem:** When using a dataset with a text column, `SFTTrainer` requires `dataset_text_field` to know which column contains the training text. Without it, you get a `ValueError`.

**Fix:**
```python
trainer = SFTTrainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    dataset_text_field="text",  # Required: tells SFTTrainer which column to use
    ...
)
```

### 4.4 messages vs text Column Formatting

**Problem:** SFT datasets may have a `messages` column (chat format with role/content dicts) or a `text` column (pre-formatted strings). `SFTTrainer` expects `text` by default.

**messages column format:**
```json
{"messages": [{"role": "user", "content": "Hello"}, {"role": "assistant", "content": "Hi!"}]}
```

**text column format:**
```json
{"text": "<|user|>\nHello\n<|assistant|]\nHi!"}
```

**How to convert:**
- If the dataset has a `messages` column, convert it to `text` using `tokenizer.apply_chat_template()` if available
- If `apply_chat_template` is not available, use a simple fallback format: `<|role|>\ncontent`
- If neither column exists, raise a clear `ValueError`

---

## 5. How train_sft_lora.py Handles These Automatically (v0.1.34+)

As of v0.1.34-alpha, `train_sft_lora.py` includes three builder functions that handle all the compatibility issues described above automatically.

### 5.1 build_training_arguments()

**Location:** `training/scripts/train_sft_lora.py`

This function builds `TrainingArguments` without `max_seq_length`:

```python
def build_training_arguments(config, output_dir, eval_dataset_exists):
    """Build TrainingArguments without max_seq_length."""
    # Uses eval_strategy alias for evaluation_strategy
    # with inspect-based fallback for older transformers
    ...
```

Key behaviors:
- Never passes `max_seq_length` to `TrainingArguments`
- Uses `eval_strategy` (newer) with fallback to `evaluation_strategy` (older) via `inspect.signature()`
- All other training parameters (batch size, learning rate, etc.) passed normally

### 5.2 build_sft_trainer()

**Location:** `training/scripts/train_sft_lora.py`

This function inspects `SFTTrainer.__init__` signature and adapts kwargs dynamically:

```python
def build_sft_trainer(model, training_args, train_dataset, eval_dataset, tokenizer, config):
    """Build SFTTrainer with version-adaptive parameter selection."""
    from trl import SFTTrainer
    sig = inspect.signature(SFTTrainer.__init__)
    kwargs = {"model": model, "args": training_args, "train_dataset": train_dataset}

    # tokenizer vs processing_class
    if "processing_class" in sig.parameters:
        kwargs["processing_class"] = tokenizer
    elif "tokenizer" in sig.parameters:
        kwargs["tokenizer"] = tokenizer

    # dataset_text_field
    if "dataset_text_field" in sig.parameters:
        kwargs["dataset_text_field"] = "text"

    # max_seq_length (belongs in SFTTrainer, NOT TrainingArguments)
    if "max_seq_length" in sig.parameters:
        kwargs["max_seq_length"] = config.get("micro_sft_max_seq_length", 512)

    ...
```

Key behaviors:
- Dynamically builds kwargs dict based on accepted parameters
- Supports both `tokenizer` (older TRL) and `processing_class` (newer TRL)
- Passes `dataset_text_field="text"` when SFTTrainer accepts it
- Passes `max_seq_length` when SFTTrainer accepts it (NOT in TrainingArguments)
- Provides detailed error message on `TypeError`

### 5.3 prepare_sft_dataset()

**Location:** `training/scripts/train_sft_lora.py`

This function handles `messages` vs `text` column formatting:

```python
def prepare_sft_dataset(dataset, tokenizer):
    """Prepare dataset for SFTTrainer by ensuring 'text' column exists."""
    if "text" in dataset.column_names:
        return dataset  # Already has text column

    if "messages" in dataset.column_names:
        # Convert messages to text using apply_chat_template if available
        # Fallback to simple <|role|>\ncontent format
        ...
    else:
        raise ValueError("Dataset must have 'text' or 'messages' column")
```

Key behaviors:
- Returns dataset directly if `text` column already exists
- Converts `messages` column to `text` using `tokenizer.apply_chat_template()` if available
- Falls back to simple `<|role|>\ncontent` format if `apply_chat_template` is not available
- Raises clear `ValueError` if neither column exists

---

## 6. Compatibility Check Does NOT Perform Training

To be absolutely clear:

| Action | Performed by check_training_stack.py? |
|--------|---------------------------------------|
| Import torch/transformers/trl | Yes (to check versions) |
| Download models | **No** |
| Load model weights | **No** |
| Access GPU | **No** |
| Run training | **No** |
| Network calls | **No** |
| Modify files | **No** |

The compatibility checker only inspects installed package versions and their API signatures using `inspect.signature()`. It is safe to run in any environment, including CI.

---

## 7. Cross-References

| Document | Relationship |
|----------|-------------|
| [MICRO_SFT_IMPLEMENTATION.md](MICRO_SFT_IMPLEMENTATION.md) | Technical implementation details for micro SFT training |
| [HF_JOBS_MICRO_SFT_RUN.md](HF_JOBS_MICRO_SFT_RUN.md) | Guide for running micro SFT on HF Jobs |
| [ADAPTER_PREVIEW_GATE.md](ADAPTER_PREVIEW_GATE.md) | Gate state machine (BLOCKED) |

---

*Training stack compatibility is checked before every micro SFT run. No downloads. No training. No network calls. Gate BLOCKED. Not a release.*
