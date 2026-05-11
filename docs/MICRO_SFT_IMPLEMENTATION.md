# Micro SFT Implementation — Kimari Local AI

> **Document Type:** Technical implementation reference for micro SFT training
> **Version:** v0.1.33-alpha
> **Date:** 2026-06-02
> **Status:** Active
> **Gate State:** BLOCKED

---

## 1. Overview

`training/scripts/train_sft_lora.py` now supports **real micro SFT training** with LoRA/QLoRA. Previously a skeleton/dry-run-only script, it now includes a full training loop that can execute a minimal SFT run when invoked with the correct safety flags.

Micro SFT is a **minimal, private training run** (typically 10 steps) that validates the entire training pipeline end-to-end. It is not a release, not a benchmark, and does not advance the preview gate.

---

## 2. Dependencies

Training dependencies are listed in `training/requirements-training.txt`:

| Package | Purpose |
|---------|---------|
| `torch` | PyTorch — CUDA tensor operations and model loading |
| `transformers` | Hugging Face Transformers — model and tokenizer loading |
| `datasets` | Hugging Face Datasets — training data loading |
| `accelerate` | Distributed training and device management |
| `peft` | Parameter-Efficient Fine-Tuning — LoRA/QLoRA adapter support |
| `trl` | Transformer Reinforcement Learning — SFTTrainer |
| `safetensors` | Safe tensor serialization for adapter weights |
| `pyyaml` | YAML config parsing |

**Important notes:**
- These dependencies are **NOT installed by default** — they require `pip install -r training/requirements-training.txt`
- They are **NOT needed for CLI runtime** — the Kimari CLI works without them
- They are **NOT needed for `--dry-run` or `--show-supported-flags`** — these modes work without torch/transformers

---

## 3. CLI Flags

### Original Flags (dry-run / inspection)

| Flag | Purpose |
|------|---------|
| `--config` | Path to YAML training config |
| `--dry-run` | Show training plan without executing |
| `--print-command` | Print recommended training command |
| `--estimate-only` | Print step estimation JSON |
| `--require-dataset` | Fail if dataset is missing |
| `--show-supported-flags` | List all supported flags (no torch import) |
| `--json` | JSON output for automation |

### New Micro SFT Flags (training execution)

| Flag | Purpose |
|------|---------|
| `--dataset-path` | Path to training dataset |
| `--eval-dataset-path` | Path to evaluation dataset |
| `--output-dir` | Directory for adapter output (should be gitignored) |
| `--max-steps` | Maximum training steps |
| `--eval-steps` | Steps between evaluations |
| `--save-steps` | Steps between checkpoint saves |
| `--logging-steps` | Steps between log entries |
| `--per-device-train-batch-size` | Batch size per device |
| `--gradient-accumulation-steps` | Gradient accumulation steps |
| `--learning-rate` | Learning rate |
| `--max-seq-length` | Maximum sequence length |
| `--micro-run` | Enable micro SFT mode (required for training) |
| `--yes` | Confirm training execution (required with --micro-run) |

---

## 4. Micro-Run Only

**v0.1.33 only supports micro-run mode.** Full training is not yet available.

To execute real micro SFT training, both flags are required:

```bash
python training/scripts/train_sft_lora.py \
    --config training/configs/hf_jobs_kimari4b_micro_sft.v0.yaml \
    --micro-run --yes
```

Without `--micro-run`, the script operates in dry-run/inspection mode as before. Without `--yes`, the script will not execute training even with `--micro-run`.

---

## 5. Safety Guards

Multiple safety layers prevent accidental or unauthorized training:

| Guard | Description |
|-------|-------------|
| **CI blocks training** | If `CI=true` is set, the script aborts immediately |
| **`--yes` required** | Training requires explicit `--yes` confirmation |
| **`--micro-run` required** | Training requires explicit `--micro-run` flag |
| **No `--token` argument** | The script accepts no token argument — no HF upload possible |
| **`push_to_hub=false`** | Always false — adapters are never uploaded |
| **`report_to="none"`** | No WandB/TensorBoard reporting — training is fully private |
| **Gate BLOCKED** | Micro SFT does not advance the preview gate |

---

## 6. No CI Training

Training **never runs in CI**. If the `CI` environment variable is set to `true`, the script immediately aborts with an error message. This ensures:

- No training runs in GitHub Actions
- No accidental GPU usage in CI
- No adapter generation in automated pipelines
- CI can safely run `--dry-run`, `--show-supported-flags`, and `--json` modes

---

## 7. No Push to Hub

The script enforces a strict no-upload policy:

- `push_to_hub` is **always `false`** — hardcoded, not configurable
- `report_to` is **always `"none"`** — no WandB, no TensorBoard, no external reporting
- There is **no `--token` argument** — the script cannot authenticate to HF Hub
- Adapters are **saved locally only**

---

## 8. Output Local Only

Adapters are saved to `output_dir` locally:

- `output_dir` should be listed in `.gitignore`
- Adapters are **never committed** to the repository
- No adapter files, checkpoints, or optimizer states should be tracked by git
- After micro SFT, only sanitized summaries may be committed (after human review)

---

## 9. Expected Adapter Files

After a successful micro SFT run, the following files should exist in `output_dir`:

| File | Description |
|------|-------------|
| `adapter_config.json` | LoRA adapter configuration (rank, alpha, target modules, etc.) |
| `adapter_model.safetensors` | LoRA adapter weights in safetensors format |

These files are **local only** and must not be committed to the repository.

---

## 10. Gate BLOCKED

Micro SFT **does not advance the preview gate**. The gate remains BLOCKED after micro SFT execution.

- Micro SFT validates the pipeline — it does not produce a release candidate
- The preview gate requires full training + evaluation + manual review before advancing
- See [ADAPTER_PREVIEW_GATE.md](ADAPTER_PREVIEW_GATE.md) for gate state machine details

---

## 11. validate_micro_sft_readiness.py

The script `training/scripts/validate_micro_sft_readiness.py` performs pre-flight checks before micro SFT execution:

- Verifies training dependencies are installed
- Checks config safety (no push_to_hub, no HF upload)
- Validates dataset paths exist
- Confirms output_dir is gitignored
- Ensures gate is BLOCKED (not attempting to advance)
- Verifies no CI environment

Run this script before executing micro SFT to catch configuration issues early.

---

## 12. Cross-Reference

| Document | Relationship |
|----------|-------------|
| [HF_JOBS_MICRO_SFT_RUN.md](HF_JOBS_MICRO_SFT_RUN.md) | Guide for running micro SFT on HF Jobs |
| [MICRO_SFT_IMPLEMENTATION.md](MICRO_SFT_IMPLEMENTATION.md) | This document — implementation details |
| [ADAPTER_PREVIEW_GATE.md](ADAPTER_PREVIEW_GATE.md) | Gate state machine (BLOCKED) |
| [HF_TOKEN_SAFETY.md](HF_TOKEN_SAFETY.md) | Token safety procedures — no `--token` argument |

---

*Micro SFT training is now real — but guarded. No upload. No export. No commit. No HF token. Gate BLOCKED. Not a release.*
