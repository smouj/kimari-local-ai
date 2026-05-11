# HF Jobs Micro SFT Result — Kimari Local AI

> **Document Type:** Micro SFT result template and sanitized record  
> **Version:** v0.1.32-alpha  
> **Date:** 2026-06-02  
> **Status:** Active — records micro SFT execution results  
> **Gate State:** BLOCKED — no public release, no HF upload

---

## Overview

This document records the result of the first HF Jobs micro SFT run for Kimari-4B. The micro SFT validates the training pipeline with minimal steps — it is **not** a full training run, **not** a benchmark, and **not** a release.

If the micro SFT has not yet been executed, the status remains `pending`.

---

## Execution Record

| Field | Value |
|-------|-------|
| **status** | `pending` |
| **job_id** | (not yet executed) |
| **run_id** | `micro-sft-v0` |
| **base_model** | `HuggingFaceTB/SmolLM3-3B` |
| **dataset_id** | `kimari-v0` |
| **flavor** | `a10g-small` |
| **training_performed** | `true` (if executed) |
| **adapter_generated** | `unknown` |
| **adapter_committed** | `false` |
| **hf_upload_performed** | `false` |
| **gguf_generated** | `false` |
| **raw_logs_committed** | `false` |
| **eval_performed** | `false` |
| **gate_state** | `BLOCKED` |
| **manual_review_required** | `true` |

---

## Status Values

- **pending** — Micro SFT has not been executed yet
- **completed** — Micro SFT ran to completion (may or may not have generated adapter)
- **failed** — Micro SFT failed

---

## What Must Always Be True

Regardless of status:

- `adapter_committed` = `false` (adapter stays in HF Jobs environment, never committed)
- `hf_upload_performed` = `false` (no HF Hub upload)
- `gguf_generated` = `false` (no GGUF export)
- `raw_logs_committed` = `false` (no raw logs committed)
- `gate_state` = `BLOCKED` (gate does not advance from micro SFT)
- `manual_review_required` = `true` (human must review results)

---

## No Scores

This micro SFT is for pipeline validation only. No benchmark scores are recorded or claimed. No official training metrics are published.

---

## No Adapter Attached

Even if an adapter was generated during the micro SFT, it is **not** attached to this record and **not** committed to the repository. The adapter remains in the HF Jobs environment only.

---

## No Public Release

This micro SFT does **not** constitute a release of Kimari-4B. The model is not published, not available for download, and not announced.

---

## Validation

After creating a micro SFT summary, validate it:

```bash
python training/scripts/validate_hf_jobs_micro_sft_summary.py \
    --summary /tmp/micro_sft_summary.json \
    --json
```

The validator checks:
- `hf_upload_performed` = `false`
- `adapter_committed` = `false`
- `gguf_generated` = `false`
- `raw_logs_committed` = `false`
- `gate_state` = `BLOCKED`
- `manual_review_required` = `true`
- No token-like strings
- No raw logs

---

## Template

The template for this record is: [hf_jobs_micro_sft_summary.template.json](../training/templates/hf_jobs_micro_sft_summary.template.json)

---

## Cross-Reference

| Document | Relationship |
|----------|-------------|
| [HF_JOBS_MICRO_SFT_RUN.md](HF_JOBS_MICRO_SFT_RUN.md) | Micro SFT execution guide |
| [HF_JOBS_SMOKE_EXECUTION_RECORD.md](HF_JOBS_SMOKE_EXECUTION_RECORD.md) | Smoke test execution record |
| [HF_JOBS_SMOKE_RUNBOOK.md](HF_JOBS_SMOKE_RUNBOOK.md) | Smoke test runbook |
| [HF_JOBS_PRIVATE_RUN.md](HF_JOBS_PRIVATE_RUN.md) | General HF Jobs guide |
| [ADAPTER_PREVIEW_GATE.md](ADAPTER_PREVIEW_GATE.md) | Gate state machine (BLOCKED) |

---

*No adapter committed. No HF upload. No GGUF. No raw logs. Gate BLOCKED. Manual review required. Not a release.*
