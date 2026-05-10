# Private Training Runbook — First SmolLM3-3B SFT

> **Document Type:** Step-by-step runbook  
> **Version:** v0.1.20-alpha  
> **Date:** 2026-05-22  
> **Status:** Active — governs the first private SFT run from environment setup through ORPO decision

---

## Purpose

This runbook provides a complete, ordered procedure for the first private supervised fine-tuning (SFT) of SmolLM3-3B using the Kimari dataset. It covers every step from environment preparation through the decision on whether to proceed with ORPO preference tuning.

**This is a private training run.** The output adapter is for internal evaluation only. No weights are published, no benchmarks are claimed, and no public release is authorized without passing the `ADAPTER_PREVIEW_GATE`.

---

## Safety Warnings

> **READ BEFORE PROCEEDING.**

- **Private training only.** The adapter output is for internal evaluation — not public distribution.
- **Do NOT upload weights** to Hugging Face or any other platform until the ADAPTER_PREVIEW_GATE is satisfied.
- **Do NOT commit adapters** to the Git repository. See `docs/ADAPTER_ARTIFACT_POLICY.md`.
- **Do NOT claim benchmark scores** until a formal evaluation is completed and verified.
- **Do NOT train in CI.** Real training requires GPU hardware. CI validates with `--dry-run` only.
- **Do NOT bind servers to 0.0.0.0** without authentication.
- **Do NOT use private user data, secrets, or copyrighted content** in training data.
- **Do NOT publish** without explicit approval through `docs/ADAPTER_PREVIEW_GATE.md`.

---

## Prerequisites

Before starting this runbook, confirm:

- [ ] You have read `docs/BASE_MODEL_ACCEPTANCE.md` and the status is "Accepted for first private training run"
- [ ] You have read `docs/ADAPTER_ARTIFACT_POLICY.md` and understand what can and cannot be committed
- [ ] You have read `docs/ADAPTER_PREVIEW_GATE.md` and understand the release state machine
- [ ] You have a GPU with CUDA support (minimum 6 GB VRAM for QLoRA on SmolLM3-3B)
- [ ] You have sufficient disk space (~20 GB for model weights, dataset, and adapter output)
- [ ] You are working in an isolated virtual environment (not system Python)

---

## Step 1: Prepare Environment

Set up an isolated Python virtual environment with all training dependencies.

```bash
# From the project root
cd /path/to/kimari-local-ai

# Create a dedicated training virtual environment
python3 -m venv .venv-training

# Activate (Linux/macOS)
source .venv-training/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install PyTorch with CUDA support
# Adjust the CUDA version for your hardware (cu121 = CUDA 12.1)
pip install torch --index-url https://download.pytorch.org/whl/cu121

# Install training dependencies
pip install transformers datasets peft trl accelerate bitsandbytes pyyaml

# Install Kimari package in development mode
pip install -e .
```

**Verify the environment:**

```bash
# Check Python version (3.10+)
python --version

# Check CUDA availability
python -c "import torch; print(f'CUDA available: {torch.cuda.is_available()}'); print(f'GPU: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else \"N/A\"}')"

# Check TRL is installed
python -c "import trl; print(f'TRL version: {trl.__version__}')"
```

> **Warning:** Do not install training dependencies in your system Python or development venv. Keep training isolated to prevent dependency conflicts.

---

## Step 2: Build Dataset v0

Build the training-ready dataset from the v0 source files.

```bash
python training/scripts/build_dataset_mix.py \
    --sft dataset/v0/sft_v0.jsonl \
    --preference dataset/v0/preference_v0.jsonl \
    --holdout dataset/v0/eval_holdout.jsonl \
    --output-dir dataset/build/kimari-v0 \
    --shuffle \
    --seed 42 \
    --report
```

**Expected output:**

```
Kimari Dataset Mix Builder
========================================

Validating SFT dataset...
  Input: N | Valid: N | Invalid: 0

Validating preference dataset...
  Input: N | Valid: N | Invalid: 0

Splitting datasets...
  Train ratio: 0.9 | Eval ratio: 0.1 | Shuffle: True | Seed: 42
  SFT: N train / N eval
  Preference: N train / N eval

Wrote N SFT train records to dataset/build/kimari-v0/sft.train.jsonl
Wrote N SFT eval records to dataset/build/kimari-v0/sft.eval.jsonl
Wrote N preference train records to dataset/build/kimari-v0/preference.train.jsonl
Wrote N preference eval records to dataset/build/kimari-v0/preference.eval.jsonl
Copied holdout (N records) to dataset/build/kimari-v0/holdout.jsonl
Wrote report to dataset/build/kimari-v0/report.json

Done.
```

**Verify the dataset build:**

```bash
# Check the report
python -m json.tool dataset/build/kimari-v0/report.json

# Verify files exist
ls -la dataset/build/kimari-v0/
```

> **Warning:** Ensure all dataset files in `dataset/v0/` are synthetic and MIT-compatible. See `dataset/v0/README.md` for the data policy. No private data, secrets, or copyrighted content is allowed.

---

## Step 3: Baseline Eval — Base SmolLM3

Evaluate the unmodified SmolLM3-3B model to establish a baseline. **This must be completed before SFT training.**

### 3a: Download and serve the base model

```bash
# Download SmolLM3-3B GGUF (Q4_K_M)
# Adjust the download method based on availability
huggingface-cli download HuggingFaceTB/SmolLM3-3B-GGUF smollm3-3b-q4_k_m.gguf --local-dir models/
```

### 3b: Start llama-server

```bash
./llama-server \
    -m models/smollm3-3b-q4_k_m.gguf \
    --port 8080 \
    --host 127.0.0.1 \
    -c 8192 \
    -ngl 99
```

### 3c: Run baseline evaluation

```bash
# Dry-run first to validate
python eval/kimarifit.py \
    --prompts eval/kimarifit_prompts.jsonl \
    --dry-run \
    --score-plan

# Run the baseline evaluation
python eval/kimarifit.py \
    --prompts eval/kimarifit_prompts.jsonl \
    --endpoint http://127.0.0.1:8080/v1 \
    --model smollm3-3b \
    --output eval/results/baseline-smollm3-q4km.json \
    --json \
    --timeout 120 \
    --max-tokens 512
```

### 3d: Record baseline results

```bash
# Summarize the baseline
python eval/scripts/summarize_results.py \
    --input eval/results/baseline-smollm3-q4km.json \
    --json > eval/results/baseline-smollm3-q4km-summary.json
```

**Do NOT proceed to Step 4 until the baseline evaluation is complete and results are saved.**

> **Full details:** See `docs/BASELINE_EVAL_PLAN.md` for the complete baseline evaluation procedure.

---

## Step 4: Run SFT Private

Train the first SFT adapter using LoRA on SmolLM3-3B.

### 4a: Dry-run the SFT configuration

```bash
python training/scripts/train_sft_lora.py \
    --dry-run \
    --config training/configs/kimari_sft_lora.v0.example.yaml
```

Expected output: the script should print "DRY RUN" and exit successfully.

If the dry-run fails, check:

- The config file exists and is valid YAML
- The `base_model` field is set to `HuggingFaceTB/SmolLM3-3B`
- All Python dependencies are installed
- GPU is available and CUDA is working

### 4b: Run the actual SFT training

> **This step requires GPU hardware and MUST NOT run in CI.**

```bash
# Ensure training environment is active
source .venv-training/bin/activate

# Run SFT training with LoRA
python training/scripts/train_sft_lora.py \
    --config training/configs/kimari_sft_lora.v0.example.yaml
```

**During training, monitor:**

- Loss curves: should decrease steadily without spikes or NaN values
- GPU utilization: should be near 100% during training steps
- GPU temperature: ensure adequate cooling for sustained training
- Disk space: checkpoints can consume significant space
- Training time: on a GTX 1060/1080 with LoRA on a 3B model, expect several hours for 2 epochs

**If training fails:**

- Check CUDA out-of-memory errors → reduce `gradient_accumulation_steps` or enable gradient checkpointing
- Check for NaN loss → reduce `learning_rate` (try 1.0e-4 instead of 2.0e-4)
- Check for disk full → reduce `save_steps` frequency or clear old checkpoints

---

## Step 5: Save Adapter Locally

After training completes, the adapter is saved in the `output_dir` specified in the training config.

**Default location:** `training/adapters/kimari-smollm3-sft-v0/`

### 5a: Verify the adapter output

```bash
# Check adapter directory contents
ls -la training/adapters/kimari-smollm3-sft-v0/

# Expected files:
# adapter_model.safetensors  — LoRA adapter weights
# adapter_config.json        — LoRA configuration
# tokenizer.json             — Tokenizer from base model
# tokenizer_config.json      — Tokenizer configuration
# special_tokens_map.json    — Special tokens mapping
# trainer_state.json         — Training state
# all_results.json           — Training results summary
```

### 5b: Record hashes

```bash
# Compute and record SHA-256 hashes
sha256sum training/adapters/kimari-smollm3-sft-v0/adapter_model.safetensors
sha256sum training/adapters/kimari-smollm3-sft-v0/adapter_config.json
```

Record the hashes in the adapter manifest (see `docs/ADAPTER_ARTIFACT_POLICY.md` for the manifest format).

### 5c: Create adapter manifest

Create `training/adapters/kimari-smollm3-sft-v0/MANIFEST.yaml` following the format in `docs/ADAPTER_ARTIFACT_POLICY.md`. Set `preview_gate_state: BLOCKED`.

### 5d: Verify nothing is committed

```bash
# Confirm adapter files are gitignored
git status training/adapters/

# Should show nothing, or only files that are allowed per ADAPTER_ARTIFACT_POLICY.md
```

> **Warning:** The `training/adapters/` directory is gitignored. Adapter weights must never be committed. See `docs/ADAPTER_ARTIFACT_POLICY.md` for details.

---

## Step 6: Execute KimariFit on Adapter

Evaluate the fine-tuned adapter against the same KimariFit prompts used for the baseline.

### 6a: Merge adapter with base model (if required)

If your serving setup requires a merged model:

```bash
# Using PEFT to merge
python -c "
from peft import PeftModel
from transformers import AutoModelForCausalLM, AutoTokenizer

base = AutoModelForCausalLM.from_pretrained('HuggingFaceTB/SmolLM3-3B')
tokenizer = AutoTokenizer.from_pretrained('HuggingFaceTB/SmolLM3-3B')
model = PeftModel.from_pretrained(base, 'training/adapters/kimari-smollm3-sft-v0')
merged = model.merge_and_unload()
merged.save_pretrained('training/adapters/kimari-smollm3-sft-v0-merged')
tokenizer.save_pretrained('training/adapters/kimari-smollm3-sft-v0-merged')
"
```

### 6b: Convert to GGUF and serve

```bash
# Convert merged model to GGUF
python convert_hf_to_gguf.py training/adapters/kimari-smollm3-sft-v0-merged/ \
    --outfile models/kimari-smollm3-sft-v0-q8_0.gguf \
    --outtype f16

# Quantize to Q4_K_M
llama-quantize models/kimari-smollm3-sft-v0-q8_0.gguf models/kimari-smollm3-sft-v0-q4km.gguf Q4_K_M

# Start llama-server with the adapter model
./llama-server \
    -m models/kimari-smollm3-sft-v0-q4km.gguf \
    --port 8080 \
    --host 127.0.0.1 \
    -c 8192 \
    -ngl 99
```

### 6c: Run KimariFit evaluation

```bash
python eval/kimarifit.py \
    --prompts eval/kimarifit_prompts.jsonl \
    --endpoint http://127.0.0.1:8080/v1 \
    --model kimari-smollm3-sft-v0 \
    --output eval/results/adapter-smollm3-sft-v0-q4km.json \
    --json \
    --timeout 120 \
    --max-tokens 512
```

### 6d: Compare with baseline

```bash
# Summarize adapter results
python eval/scripts/summarize_results.py \
    --input eval/results/adapter-smollm3-sft-v0-q4km.json \
    --json > eval/results/adapter-smollm3-sft-v0-q4km-summary.json

# Compare baseline vs adapter (when compare_runs.py is available)
python eval/scripts/compare_runs.py \
    --baseline eval/results/baseline-smollm3-q4km.json \
    --adapter eval/results/adapter-smollm3-sft-v0-q4km.json \
    --output eval/results/comparison-sft-v0-vs-baseline.json
```

---

## Step 7: Summarize Results

After completing the evaluation, create a results summary documenting:

### 7a: Category-level comparison

For each category, compare the adapter against the baseline:

| Category | Baseline (OK/Total) | Adapter (OK/Total) | Change | Notes |
|----------|--------------------|--------------------|--------|-------|
| python | ?/? | ?/? | ? | |
| typescript | ?/? | ?/? | ? | |
| bash | ?/? | ?/? | ? | |
| docker | ?/? | ?/? | ? | |
| linux_troubleshooting | ?/? | ?/? | ? | |
| windows_troubleshooting | ?/? | ?/? | ? | |
| spanish_technical | ?/? | ?/? | ? | |
| json_mode | ?/? | ?/? | ? | |
| openclaw_agent | ?/? | ?/? | ? | |
| local_security | ?/? | ?/? | ? | |

### 7b: Safety assessment

Specifically verify:

- [ ] Safety refusals (kf-033) are maintained or improved
- [ ] Destructive command warnings (kf-034) are maintained or improved
- [ ] No false claims about benchmarks, packages, or CLI flags
- [ ] No unsafe network exposure recommendations
- [ ] Spanish technical quality is maintained or improved

### 7c: Decision summary

Record the evaluation outcome:

```yaml
# evaluation_summary.yaml (stored locally, not committed)
adapter: kimari-smollm3-sft-v0
baseline: smollm3-3b-q4km
evaluation_date: "2026-05-22"  # Update with actual date
overall_improvement: null  # true/false — set after review
safety_regression: null    # true/false — set after review
categories_improved: []    # List of categories that improved
categories_regressed: []   # List of categories that regressed
recommendation: ""         # "proceed_to_orpo" / "reassess_sft" / "abort"
reviewer: ""               # Name of the reviewer
notes: ""
```

---

## Step 8: Decide if ORPO Proceeds

Based on the evaluation results, make one of the following decisions:

### Decision: Proceed to ORPO

**Conditions:**

- SFT shows measurable improvement over baseline in at least 3 categories
- No safety regression in any category
- No false claims detected in adapter responses
- Manual review confirms the quality improvement is genuine

**Action:** Begin ORPO preference tuning using `training/configs/kimari_orpo.v0.example.yaml`:

```bash
# Dry-run ORPO config
python training/scripts/train_sft_lora.py \
    --dry-run \
    --config training/configs/kimari_orpo.v0.example.yaml

# Run ORPO (requires GPU, NOT in CI)
python training/scripts/train_sft_lora.py \
    --config training/configs/kimari_orpo.v0.example.yaml
```

After ORPO, repeat Steps 5–7 for the ORPO adapter (`kimari-smollm3-orpo-v0`).

### Decision: Reassess SFT

**Conditions:**

- SFT shows minimal or no improvement over baseline
- Safety regression detected in one or more categories
- False claims detected in adapter responses
- Training loss was unstable (spikes, NaN)

**Action:** Before re-running SFT, investigate:

1. Dataset quality — review `dataset/build/kimari-v0/report.json` for anomalies
2. Learning rate — try reducing from 2.0e-4 to 1.0e-4
3. Epochs — try 1 epoch instead of 2 (overfitting may cause regression)
4. LoRA rank — try r=16 instead of r=32 (over-parameterization risk)

Do NOT proceed to ORPO until the SFT results are acceptable.

### Decision: Abort

**Conditions:**

- SFT shows consistent degradation across categories
- Safety regression is severe (e.g., model no longer refuses harmful requests)
- Training failed entirely (NaN loss, OOM, corrupt output)

**Action:** Record the failure, clean up the adapter directory, and reassess the training approach entirely. Consider:

1. Different base model candidate (see `docs/MODEL_DECISION_RECORD.md`)
2. Different dataset composition
3. Different training method (e.g., full fine-tune instead of LoRA)

---

## Never Publish Without ADAPTER_PREVIEW_GATE

Regardless of the evaluation results, **no adapter may be published or shared publicly** without passing through the `ADAPTER_PREVIEW_GATE` defined in `docs/ADAPTER_PREVIEW_GATE.md`.

**The gate states are:**

| State | Meaning |
|-------|---------|
| BLOCKED | Default. No sharing, no upload. |
| PENDING | License verified, no secrets, hashes recorded. |
| APPROVED_FOR_PRIVATE_TESTING | Eval done, no safety regression, manual review passed. |
| APPROVED_FOR_PUBLIC_PREVIEW | Model card updated, HF reviewed, safety review passed. |

**All transitions require explicit human decisions. There are no automatic transitions.**

Even if the SFT adapter performs well and the decision is to proceed to ORPO, both the SFT and ORPO adapters remain in the BLOCKED state until explicitly advanced through the gate.

---

## Run Checklist

Use this checklist to track progress through the runbook:

| # | Step | Command | Status |
|---|------|---------|--------|
| 1 | Prepare environment | `python3 -m venv .venv-training` | ☐ |
| 2 | Build dataset v0 | `build_dataset_mix.py` | ☐ |
| 3 | Baseline eval | `kimarifit.py` with SmolLM3-3B | ☐ |
| 4 | SFT dry-run | `train_sft_lora.py --dry-run` | ☐ |
| 4 | SFT training | `train_sft_lora.py` (GPU required) | ☐ |
| 5 | Save adapter locally | Verify `training/adapters/kimari-smollm3-sft-v0/` | ☐ |
| 5 | Record hashes | `sha256sum` adapter files | ☐ |
| 5 | Create manifest | `MANIFEST.yaml` with BLOCKED state | ☐ |
| 6 | Eval adapter | `kimarifit.py` with adapter model | ☐ |
| 6 | Compare with baseline | Compare category results | ☐ |
| 7 | Summarize results | Record improvement/regression | ☐ |
| 7 | Safety assessment | Verify no safety regression | ☐ |
| 8 | ORPO decision | Proceed / Reassess / Abort | ☐ |

---

## Related Documents

| Document | Relationship |
|----------|-------------|
| [ADAPTER_ARTIFACT_POLICY.md](ADAPTER_ARTIFACT_POLICY.md) | What can and cannot be committed; naming conventions; hash recording |
| [ADAPTER_PREVIEW_GATE.md](ADAPTER_PREVIEW_GATE.md) | State machine for adapter release decisions |
| [BASELINE_EVAL_PLAN.md](BASELINE_EVAL_PLAN.md) | Detailed plan for baseline evaluation of SmolLM3-3B |
| [BASE_MODEL_ACCEPTANCE.md](BASE_MODEL_ACCEPTANCE.md) | Formal acceptance record for SmolLM3-3B |
| [FIRST_PRIVATE_TRAINING_RUN.md](FIRST_PRIVATE_TRAINING_RUN.md) | Alternative training guide with additional detail |
| [HUGGINGFACE_RELEASE.md](HUGGINGFACE_RELEASE.md) | Full release process for when public release is authorized |
| [HF_PLACEHOLDER_PLAN.md](HF_PLACEHOLDER_PLAN.md) | Plan for Hugging Face placeholder repository |
| [training/configs/private_sft_run.v0.yaml](../training/configs/private_sft_run.v0.yaml) | Run manifest for this SFT run |

---

*This runbook governs the first private SFT training of SmolLM3-3B. The output adapter is for internal evaluation only. No weights are published without passing the ADAPTER_PREVIEW_GATE. Every decision point in this runbook requires explicit human judgment.*
