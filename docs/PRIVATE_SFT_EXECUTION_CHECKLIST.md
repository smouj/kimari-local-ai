# Private SFT Execution Checklist — First Run

> **Document Type:** Pre-flight checklist for first private SFT run
> **Version:** v0.1.21-alpha
> **Date:** 2026-05-22
> **Status:** Active — must be completed before starting training

---

## Purpose

This checklist ensures that all prerequisites are met before executing the first private supervised fine-tuning (SFT) run. Every item must be verified. If any item cannot be checked off, **do not start training**.

---

## 1. GPU Environment

- [ ] Rented GPU machine has CUDA installed and working
- [ ] `nvidia-smi` reports the expected GPU and driver version
- [ ] CUDA version is compatible with PyTorch / training framework
- [ ] Sufficient GPU memory for LoRA/QLoRA on SmolLM3-3B (minimum 16 GB recommended, 24 GB preferred)
- [ ] Python 3.10+ installed on the training machine
- [ ] Required Python packages installed (transformers, peft, trl, torch, accelerate)

---

## 2. License Review

- [ ] SmolLM3-3B license (Apache 2.0) has been reviewed and permits private fine-tuning
- [ ] License permits creation of derivative weights for private evaluation
- [ ] `MODEL_LICENSES.md` reflects current understanding of Apache 2.0 applicability
- [ ] No redistribution of SmolLM3-3B weights or derivative weights without compliance

---

## 3. Dataset Validation

- [ ] `dataset/v0/sft_v0.jsonl` has been validated with `training/scripts/validate_training_ready.py`
- [ ] All records have required fields (source, license, instruction, output)
- [ ] No forbidden strings (private keys, tokens) in dataset
- [ ] No premature release claims in dataset
- [ ] Dataset build pipeline (`training/scripts/build_v0_pipeline.py`) produces valid output
- [ ] Minimum record counts met (50 SFT, 20 preference, 10 holdout)

---

## 4. Baseline Eval Plan

- [ ] `docs/BASELINE_EVAL_PLAN.md` has been read and understood
- [ ] Baseline evaluation of SmolLM3-3B will be run before or alongside SFT
- [ ] Baseline results will be saved to `eval/results/baseline-smollm3-*.json`

---

## 5. Run Config Review

- [ ] `training/configs/private_sft_run.v0.yaml` has been reviewed
- [ ] `run_id` is set to `kimari-smollm3-sft-v0-private-001`
- [ ] `public_release_allowed` is `false`
- [ ] `hf_upload_allowed` is `false`
- [ ] SFT config (`training/configs/kimari_sft_lora.v0.example.yaml`) reviewed — starting point only

---

## 6. Output Directory Safety

- [ ] `output_dir` (training/adapters/kimari-smollm3-sft-v0) is outside git or gitignored
- [ ] `training/adapters/` is listed in `.gitignore`
- [ ] No adapter weights will be accidentally committed
- [ ] Sufficient disk storage for adapter output (estimate: 2–5 GB for LoRA adapter + checkpoints)

---

## 7. Experiment Tracking

- [ ] No WandB public mode by default — set `WANDB_MODE=disabled` or `WANDB_MODE=offline`
- [ ] No automatic uploads to any experiment tracking platform
- [ ] If WandB is used locally, credentials are not committed

---

## 8. Hugging Face

- [ ] No HF upload will be performed
- [ ] `hf_upload_allowed: false` is confirmed in run config
- [ ] No HF token is needed or used during training
- [ ] Base model (SmolLM3-3B) will be downloaded locally by the training framework, not committed

---

## 9. Training Command

The training command is:

```bash
python training/scripts/train_sft_lora.py \
    --config training/configs/kimari_sft_lora.v0.example.yaml
```

Before running:

- [ ] Dry-run has been tested with `training/scripts/run_private_sft_dryrun.py`
- [ ] Dry-run completed without errors
- [ ] Ready to execute actual training

---

## 10. Post-Run Manifest Creation

After training completes:

- [ ] Run `create_adapter_manifest.py` to generate the manifest:

```bash
python training/scripts/create_adapter_manifest.py \
    --run-config training/configs/private_sft_run.v0.yaml \
    --adapter-dir training/adapters/kimari-smollm3-sft-v0 \
    --output training/adapters/kimari-smollm3-sft-v0/MANIFEST.yaml
```

- [ ] Verify manifest has `preview_gate_state: BLOCKED`
- [ ] Verify manifest has `public_release_allowed: false`
- [ ] Verify manifest has `hf_upload_allowed: false`
- [ ] Verify no weight files are listed in `adapter_files`

---

## 11. Post-Run Evaluation

- [ ] Run KimariFit evaluation on the trained adapter:

```bash
python eval/kimarifit.py --model-path training/adapters/kimari-smollm3-sft-v0/merged/
```

- [ ] Compare results against baseline using `eval/scripts/compare_runs.py`
- [ ] Run `eval/scripts/create_eval_summary.py` to produce a committable summary
- [ ] Verify eval summary contains no raw prompts or responses

---

## 12. Preview Gate

- [ ] Preview gate stays **BLOCKED** after training
- [ ] No automatic transition — see `docs/ADAPTER_PREVIEW_GATE.md`
- [ ] Transition to PENDING requires explicit human decision (license verified, no secrets, hashes recorded)

---

## Quick Reference: What to Check Before Training

| # | Check | Pass? |
|---|-------|-------|
| 1 | GPU + CUDA ready | ☐ |
| 2 | SmolLM3 license reviewed | ☐ |
| 3 | Dataset v0 validated | ☐ |
| 4 | Baseline eval plan read | ☐ |
| 5 | Run config reviewed | ☐ |
| 6 | output_dir gitignored | ☐ |
| 7 | Sufficient storage | ☐ |
| 8 | No WandB public | ☐ |
| 9 | No HF upload | ☐ |
| 10 | Dry-run passed | ☐ |

**All 10 must be checked before starting training.**

---

## Related Documents

| Document | Relationship |
|----------|-------------|
| [ADAPTER_PREVIEW_GATE.md](ADAPTER_PREVIEW_GATE.md) | State machine for adapter release — all adapters start BLOCKED |
| [ADAPTER_ARTIFACT_POLICY.md](ADAPTER_ARTIFACT_POLICY.md) | What can and cannot be committed |
| [PRIVATE_TRAINING_RUNBOOK.md](PRIVATE_TRAINING_RUNBOOK.md) | Step-by-step runbook for first private SFT |
| [BASELINE_EVAL_PLAN.md](BASELINE_EVAL_PLAN.md) | Baseline evaluation plan |
| [MODEL_LICENSES.md](../MODEL_LICENSES.md) | License documentation for base model candidates |
| [PRIVATE_EVAL_RESULTS_POLICY.md](PRIVATE_EVAL_RESULTS_POLICY.md) | What eval results can be committed |

---

*This checklist must be completed before the first private SFT run. Do not skip any item. All adapters start in BLOCKED state and require explicit human approval before any form of distribution.*
