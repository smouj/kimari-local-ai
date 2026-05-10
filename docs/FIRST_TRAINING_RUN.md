# First Training Run Guide

> **Version:** v0.1.18-alpha
> **Last Updated:** 2026-05-20
> **Status:** Guide only — no training has been executed

---

## ⚠️ Safety Reminders

- **Do NOT train real models in CI.** Training scripts support `--dry-run` for CI validation only.
- **Do NOT download models automatically.** Base model selection requires manual license review.
- **Do NOT upload weights to Hugging Face** until license and evaluation pass.
- **Do NOT commit GGUF files** or any model weights to this repository.
- **Do NOT fabricate benchmark scores.** All results must come from actual evaluation runs.
- **Do NOT bind servers to 0.0.0.0** without authentication.

---

## Prerequisites

Before starting your first training run, ensure you have:

1. **GPU Hardware:** NVIDIA GPU with at least 8 GB VRAM (GTX 1080 or better recommended)
2. **CUDA Toolkit:** Compatible with your GPU driver
3. **Python 3.10+:** With pip and venv
4. **Disk Space:** At least 20 GB free for model checkpoints and datasets
5. **Base model license review completed:** See ADR-001 in `docs/MODEL_DECISION_RECORD.md`

---

## Step 1: Choose Base Model

Review the candidates in `training/configs/base_candidates.yaml`:

```bash
python training/scripts/select_base_model.py --json
```

**Do not proceed until:**
- A license review has been completed for the selected candidate
- The ADR-001 status has been updated from "Proposed" to "Accepted"
- The `license_verified` field is set to `true` in `base_candidates.yaml`

Currently, no base model has been selected. All candidates are under review.

---

## Step 2: Prepare Dataset Seed

Validate the seed datasets:

```bash
# Validate SFT seed
python training/scripts/prepare_dataset.py \
    --input dataset/samples/sft_seed.jsonl \
    --output dataset/build/sft.validated.jsonl \
    --schema sft \
    --report dataset/build/sft_report.json

# Validate preference seed
python training/scripts/prepare_dataset.py \
    --input dataset/samples/preference_seed.jsonl \
    --output dataset/build/preference.validated.jsonl \
    --schema preference \
    --report dataset/build/preference_report.json
```

Build the dataset mix:

```bash
python training/scripts/build_dataset_mix.py \
    --sft dataset/samples/sft_seed.jsonl \
    --preference dataset/samples/preference_seed.jsonl \
    --output-dir dataset/build \
    --report
```

> **Note:** The seed datasets (30 SFT + 20 preference samples) are synthetic and minimal. Real training requires significantly more data.

---

## Step 3: Dry-Run Training

Validate the training pipeline without actually training:

```bash
python training/scripts/train_sft_lora.py \
    --dry-run \
    --config training/configs/kimari_sft_lora.example.yaml
```

This should print "DRY RUN" and exit successfully. If it fails, check:
- The config file exists and is valid YAML
- The `base_model` field is set (even to TBD for dry-run)
- Required Python packages are available

---

## Step 4: Real Training (Outside CI)

> **This step requires GPU hardware and cannot run in CI.**

After selecting a base model and preparing datasets:

```bash
# 1. Download the base model (manual step)
# Follow the license terms for the selected base model

# 2. Update training config with real paths
# Edit training/configs/kimari_sft_lora.example.yaml:
#   - Set base_model to the downloaded model path
#   - Set dataset paths

# 3. Run SFT training
python training/scripts/train_sft_lora.py \
    --config training/configs/kimari_sft_lora.example.yaml

# 4. Monitor training
# Watch loss curves, checkpoint sizes, and GPU utilization
```

**Important:**
- Start with a small number of epochs (1-2) to validate the pipeline
- Save checkpoints regularly
- Monitor for loss spikes or NaN values
- Keep training logs for reproducibility

---

## Step 5: Evaluation with KimariFit

After training, evaluate the model:

```bash
# Dry-run to validate evaluation pipeline
python eval/kimarifit.py \
    --prompts eval/kimarifit_prompts.jsonl \
    --dry-run

# Evaluate against local server
python eval/kimarifit.py \
    --prompts eval/kimarifit_prompts.jsonl \
    --endpoint http://localhost:8080/v1 \
    --output eval/results/kimarifit_results.json \
    --json
```

Score results against the rubric in `eval/rubrics/kimarifit_rubric.md`.

---

## Step 6: Export GGUF

Plan and execute GGUF conversion:

```bash
# Dry-run to see planned commands
python training/scripts/export_gguf_plan.py \
    --model-dir /path/to/fine-tuned/model \
    --output-dir /path/to/gguf-output \
    --dry-run

# Actual conversion (requires llama.cpp tools)
python training/scripts/export_gguf_plan.py \
    --model-dir /path/to/fine-tuned/model \
    --output-dir /path/to/gguf-output \
    --quant Q4_K_M,Q5_K_M
```

**After conversion:**
1. Compute SHA-256 hashes for all GGUF files: `sha256sum *.gguf`
2. Pin hashes in the model registry
3. Test inference on target hardware (GTX 1060, GTX 1080)
4. Verify VRAM usage and tokens/second

---

## Step 7: Hash and Pin

For each GGUF file:

```bash
sha256sum model-q4_k_m.gguf > model-q4_k_m.gguf.sha256
sha256sum model-q5_k_m.gguf > model-q5_k_m.gguf.sha256
```

Update the model registry with verified hashes. Never invent or fabricate hashes.

---

## Step 8: Hugging Face Release (Conditional)

> **Only proceed if BOTH license and evaluation pass.**

Refer to `docs/HUGGINGFACE_RELEASE.md` for the full release checklist.

**Hard blocks (must pass before release):**
- [ ] Base model license permits derivative distribution
- [ ] License compatibility confirmed for all formats (GGUF, safetensors)
- [ ] Safety evaluation completed with acceptable scores
- [ ] No GGUF files committed to the repository
- [ ] Benchmark results are from actual evaluation runs (not fabricated)
- [ ] Model card updated with real results and proper disclaimers

**If any hard block fails, do not release weights.**

---

## Checklist Summary

| Step | Command | Status |
|------|---------|--------|
| 1. Choose base | `select_base_model.py --json` | Under review |
| 2. Prepare data | `prepare_dataset.py` + `build_dataset_mix.py` | Seed only |
| 3. Dry-run SFT | `train_sft_lora.py --dry-run` | Validated |
| 4. Real training | `train_sft_lora.py` (requires GPU) | Not started |
| 5. Evaluate | `kimarifit.py` | Dry-run only |
| 6. Export GGUF | `export_gguf_plan.py` | Plan only |
| 7. Hash & pin | `sha256sum` | Not started |
| 8. HF release | See HUGGINGFACE_RELEASE.md | Not started |

---

*No training has been executed. This guide describes the planned process for a future training run. All steps are subject to change based on base model selection and evaluation results.*
