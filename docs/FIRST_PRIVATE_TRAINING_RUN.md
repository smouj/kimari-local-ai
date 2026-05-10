# First Private Training Run — SmolLM3-3B SFT

> **Document Type:** Step-by-step private training guide  
> **Version:** v0.1.19-alpha  
> **Date:** 2026-05-21  
> **Status:** PRIVATE training only — NO public release authorized

---

## ⚠️ Safety Warnings

> **READ THIS BEFORE PROCEEDING.**

- **This is a PRIVATE training run.** The output adapter is for internal evaluation only.
- **Do NOT upload weights to Hugging Face** or any other platform until eval + license pass.
- **Do NOT commit adapters or model weights** to this Git repository.
- **Do NOT claim benchmark scores** until a formal evaluation is completed.
- **Do NOT share the adapter** with anyone outside the project until the pre-release checklist in `docs/BASE_MODEL_ACCEPTANCE.md` is fully satisfied.
- **Do NOT train in CI.** Real training requires GPU hardware. CI validates with `--dry-run` only.
- **Do NOT bind servers to 0.0.0.0** without authentication.
- **Do NOT use private user data, secrets, or copyrighted content** in training data.

---

## Accepted Base

| Field | Value |
|-------|-------|
| **Base Model** | `HuggingFaceTB/SmolLM3-3B` |
| **Acceptance Record** | `docs/BASE_MODEL_ACCEPTANCE.md` |
| **Scope** | Private SFT candidate only |
| **License** | Apache 2.0 |

This guide is authorized under the acceptance record in `docs/BASE_MODEL_ACCEPTANCE.md`. Do not proceed if that document's status is not "Accepted for first private training run."

---

## Step 1: Create Environment

Set up an isolated Python virtual environment for training.

```bash
# From the project root
cd /path/to/kimari-local-ai

# Create virtual environment
python3 -m venv .venv-training

# Activate (Linux/macOS)
source .venv-training/bin/activate

# Activate (Windows PowerShell)
# .\.venv-training\Scripts\Activate.ps1

# Install dependencies
pip install --upgrade pip
pip install torch --index-url https://download.pytorch.org/whl/cu121  # Adjust for your CUDA version
pip install transformers datasets peft trl accelerate bitsandbytes
pip install -e .
```

> **Warning:** Do not install training dependencies in your system Python or development venv. Keep training isolated to prevent dependency conflicts.

---

## Step 2: Build Dataset Mix

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

This script will:

1. Validate all SFT records against the SFT schema
2. Validate all preference records against the preference schema
3. Validate holdout records for evaluation
4. Shuffle the data with a fixed seed for reproducibility
5. Write training-ready JSONL files to `dataset/build/kimari-v0/`
6. Generate `dataset/build/kimari-v0/report.json` with statistics

> **Warning:** Ensure all dataset files in `dataset/v0/` are synthetic and MIT-compatible. See `dataset/v0/README.md` for the data policy. No private data, secrets, or copyrighted content is allowed.

---

## Step 3: Validate Training Readiness

Run the training readiness validator to confirm everything is in place before training.

```bash
python training/scripts/validate_training_ready.py \
    --base-config training/configs/base_candidates.yaml \
    --sft dataset/v0/sft_v0.jsonl \
    --preference dataset/v0/preference_v0.jsonl \
    --holdout dataset/v0/eval_holdout.jsonl \
    --json
```

This script will check:

- Base model configuration is valid and the accepted candidate is marked
- SFT dataset exists and passes schema validation
- Preference dataset exists and passes schema validation
- Holdout dataset exists and passes validation
- No duplicate entries across train and eval splits
- Required fields are present in all records
- Output in JSON format for scripting integration

> **Warning:** Do not proceed to Step 4 if validation fails. Fix all errors before continuing.

---

## Step 4: Dry-Run SFT Config

Validate the training pipeline without actually training. This confirms the configuration file is valid and all dependencies are available.

```bash
python training/scripts/train_sft_lora.py \
    --dry-run \
    --config training/configs/kimari_sft_lora.v0.example.yaml
```

Expected output: the script should print "DRY RUN" and exit successfully. If it fails, check:

- The config file exists and is valid YAML
- The `base_model` field is set to `HuggingFaceTB/SmolLM3-3B`
- All Python dependencies are installed
- GPU is available and CUDA is working

> **Warning:** This step is safe to run in CI. It does NOT download models or train anything. The `--dry-run` flag is a hard requirement for CI environments.

---

## Step 5: Real SFT Command (Outside CI)

> **⚠️ This step requires GPU hardware and MUST NOT run in CI.**

After all validations pass, run the actual SFT training:

```bash
# Ensure training environment is active
source .venv-training/bin/activate

# Run SFT training with LoRA
python training/scripts/train_sft_lora.py \
    --config training/configs/kimari_sft_lora.v0.example.yaml
```

**Before running, update the config file** (`training/configs/kimari_sft_lora.v0.example.yaml`) with:

- `base_model: "HuggingFaceTB/SmolLM3-3B"` — the accepted base model
- `dataset_path` — pointing to the built dataset (`dataset/build/kimari-v0/sft.train.jsonl`)
- `output_dir` — a local directory for adapter output (e.g., `./training/runs/kimari-sft-v0`)

**During training:**

- Start with 1–2 epochs to validate the pipeline
- Monitor loss curves for spikes or NaN values
- Watch GPU utilization (should be near 100% during training)
- Save checkpoints regularly (configured via `save_steps`)
- Keep training logs for reproducibility

> **⚠️ Warning:** This step downloads model weights from Hugging Face (~6 GB for SmolLM3-3B in full precision). Ensure you have sufficient disk space and agree to the Apache 2.0 license terms.

> **⚠️ Warning:** Training on a GTX 1060/1080 with LoRA on a 3B model may take several hours. Monitor GPU temperature and ensure adequate cooling.

---

## Step 6: Eval Plan

After the SFT training completes, evaluate the resulting adapter using KimariFit.

```bash
# Start a local server with the fine-tuned model
# (Merge adapter with base first if required by your serving setup)
kimari start --profile custom --model /path/to/merged/model

# Run KimariFit evaluation
python eval/kimarifit.py \
    --prompts eval/kimarifit_prompts.jsonl \
    --endpoint http://localhost:8080/v1 \
    --output eval/results/kimari-sft-v0-kimarifit.json \
    --json
```

Also run the full evaluation suite:

```bash
python eval/run_eval.py \
    --model-path /path/to/merged/model \
    --output eval/results/kimari-sft-v0-eval.json
```

Score results against the rubric in `eval/rubrics/kimarifit_rubric.md` and check for failure modes documented in `eval/failure_modes.md`.

> **Warning:** Evaluation results are private. Do not publish or claim scores until the pre-release checklist is satisfied.

---

## Step 7: Adapter Output

The LoRA adapter produced by training is stored locally in the `output_dir` specified in the training config (default: `./training/runs/kimari-sft-v0/`).

**Adapter handling rules:**

- The adapter is stored **locally only**.
- It is **NOT committed** to the Git repository.
- It is **NOT uploaded** to Hugging Face or any other platform.
- The adapter directory is excluded via `.gitignore` (`training/runs/` pattern).
- If you need to transfer the adapter between machines, use a secure, private method (not a public URL).

**Adapter contents:**

| File | Description |
|------|-------------|
| `adapter_model.safetensors` | LoRA adapter weights |
| `adapter_config.json` | LoRA configuration (rank, alpha, target modules) |
| `tokenizer.json` + related files | Tokenizer files from base model |
| `training_args.bin` | Training arguments snapshot |
| `trainer_state.json` | Training state (loss, learning rate, etc.) |
| `all_results.json` | Summary of training results |

> **⚠️ Warning:** Do NOT share these files publicly. They are for internal evaluation only.

---

## Step 8: No HF Upload Until Eval + License Pass

**Under no circumstances should the adapter or merged model be uploaded to Hugging Face until BOTH of the following are satisfied:**

1. **Evaluation passes** — The fine-tuned model must achieve acceptable scores on the full KimariFit evaluation suite. Results must be real, measured values — not targets or estimates.

2. **License review passes** — A formal review of the Apache 2.0 license as it applies to fine-tuned derivative works must be completed and documented in `MODEL_LICENSES.md`. While Apache 2.0 is expected to be permissive, the review must be explicit and recorded.

**If either condition is not met:**

- Do not upload weights to Hugging Face
- Do not create a Hugging Face repository with model files
- Do not claim the model is "released" or "available"
- Do not publish benchmark scores

Refer to `docs/BASE_MODEL_ACCEPTANCE.md` for the complete pre-release checklist and `docs/HUGGINGFACE_RELEASE.md` for the full release process.

---

## Summary

| Step | Command | Environment | Status |
|------|---------|-------------|--------|
| 1. Create environment | `python3 -m venv .venv-training` | Local | Required |
| 2. Build dataset mix | `build_dataset_mix.py` | Local | Required |
| 3. Validate readiness | `validate_training_ready.py` | Local / CI | Required |
| 4. Dry-run SFT | `train_sft_lora.py --dry-run` | Local / CI | Required |
| 5. Real SFT | `train_sft_lora.py` (no --dry-run) | **Local only — GPU required** | Pending |
| 6. Eval | `kimarifit.py` + `run_eval.py` | **Local only — requires running server** | Pending |
| 7. Adapter output | Local storage only | Local | Pending |
| 8. HF upload | **Blocked** until eval + license pass | N/A | Blocked |

---

## Related Documents

| Document | Relationship |
|----------|-------------|
| [BASE_MODEL_ACCEPTANCE.md](BASE_MODEL_ACCEPTANCE.md) | Formal acceptance record authorizing this private training run |
| [HF_PLACEHOLDER_PLAN.md](HF_PLACEHOLDER_PLAN.md) | Plan for Hugging Face placeholder repository (docs-only, no weights) |
| [HUGGINGFACE_RELEASE.md](HUGGINGFACE_RELEASE.md) | Full release process for when public release is authorized |
| [MODEL_DECISION_RECORD.md](MODEL_DECISION_RECORD.md) | ADR-001 — base model candidate comparison |
| [FIRST_TRAINING_RUN.md](FIRST_TRAINING_RUN.md) | General training run guide (less specific than this document) |
| [dataset/v0/README.md](../dataset/v0/README.md) | Dataset v0 policy, format, and file descriptions |

---

*This document authorizes a PRIVATE training run only. No weights are to be published, shared, or claimed as released. The adapter output is for internal evaluation exclusively. All safety warnings must be observed throughout the process.*
