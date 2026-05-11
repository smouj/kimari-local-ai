# HF Jobs Smoke Execution Record — Kimari Local AI

> **Document Type:** Smoke test execution record and result  
> **Version:** v0.1.31-alpha  
> **Date:** 2026-06-02  
> **Status:** Active — records real smoke test execution results  
> **Gate State:** BLOCKED — no public release, no HF upload

---

## Overview

This document records the result of the first HF Jobs smoke test execution for Kimari-4B. The smoke test validates the training environment on HF Jobs infrastructure **without** performing any actual training.

If the smoke test has not yet been executed, the status remains `pending`.

---

## Execution Record

| Field | Value |
|-------|-------|
| **status** | `pending` |
| **job_id** | (not yet executed) |
| **flavor** | `a10g-small` |
| **image** | `pytorch/pytorch:2.6.0-cuda12.4-cudnn9-devel` |
| **gpu_detected** | — |
| **torch_cuda_available** | — |
| **repo_installed** | — |
| **dataset_dryrun_passed** | — |
| **sft_dryrun_passed** | — |
| **training_performed** | `false` |
| **adapter_generated** | `false` |
| **hf_upload_performed** | `false` |
| **gate_state** | `BLOCKED` |
| **stderr_sanitized** | `true` |
| **logs_sanitized** | `true` |
| **notes** | Smoke test not yet executed. Status pending. |

---

## Status Values

- **pending** — Smoke test has not been executed yet
- **completed** — Smoke test passed all checks (GPU, torch, repo, dataset, SFT dry-run)
- **failed** — Smoke test failed one or more checks

---

## Required Fields for Completion

When the smoke test is executed and completed, the following must all be `true`:

1. `gpu_detected` = `true` (nvidia-smi shows a GPU)
2. `torch_cuda_available` = `true` (torch.cuda.is_available())
3. `repo_installed` = `true` (pip install -e . succeeds)
4. `dataset_dryrun_passed` = `true` (build_dataset_mix.py runs in dry-run)
5. `sft_dryrun_passed` = `true` (train_sft_lora.py --dry-run validates config)

---

## What Must Always Be False

Regardless of status:

- `training_performed` = `false` (no training in smoke test)
- `adapter_generated` = `false` (no adapter creation)
- `hf_upload_performed` = `false` (no HF upload)
- `gate_state` = `BLOCKED` (gate does not advance from smoke test)

---

## Validation

After creating a smoke summary, validate it:

```bash
python training/scripts/validate_hf_jobs_smoke_summary.py \
    --summary /tmp/hf_jobs_smoke_summary.json \
    --json
```

The validator checks:
- `training_performed` = `false`
- `adapter_generated` = `false`
- `hf_upload_performed` = `false`
- `gate_state` = `BLOCKED`
- `logs_sanitized` = `true`
- No token-like strings (hf_..., sk_..., api_key assignments)
- No raw logs included

---

## Smoke Must Pass Before Micro SFT

**Important:** Do NOT proceed to micro SFT (v0.1.32+) until the smoke test is completed with all checks passing:

```
gpu_detected=true
torch_cuda_available=true
repo_installed=true
dataset_dryrun_passed=true
sft_dryrun_passed=true
```

If any check fails, fix the issue and re-run the smoke test before proceeding.

---

## Template

The template for this record is: [hf_jobs_smoke_execution_record.template.json](../training/templates/hf_jobs_smoke_execution_record.template.json)

---

## Cross-Reference

| Document | Relationship |
|----------|-------------|
| [HF_JOBS_SMOKE_RESULT.md](HF_JOBS_SMOKE_RESULT.md) | Smoke test result summary |
| [HF_JOBS_SMOKE_RUNBOOK.md](HF_JOBS_SMOKE_RUNBOOK.md) | Step-by-step runbook |
| [HF_JOBS_PRIVATE_RUN.md](HF_JOBS_PRIVATE_RUN.md) | General HF Jobs guide |
| [ADAPTER_PREVIEW_GATE.md](ADAPTER_PREVIEW_GATE.md) | Gate state machine (BLOCKED) |

---

*No training performed. No adapters generated. No HF upload. Gate BLOCKED. No raw logs or tokens in this record.*
