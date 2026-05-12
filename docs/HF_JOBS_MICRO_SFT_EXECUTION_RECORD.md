# HF Jobs Micro SFT Execution Record — Kimari Local AI

> **Document Type:** Template and reference for micro SFT execution records  
> **Version:** v0.1.37-alpha  
> **Date:** 2026-06-03  
> **Status:** Active — governs micro SFT execution record creation and validation  
> **Gate State:** BLOCKED — no public release, no HF upload

---

## 1. Purpose

This document defines the micro SFT execution record format, creation, and validation rules. The execution record captures the outcome of a micro SFT run on Hugging Face Jobs in a safe, sanitized format that may be committed to the repository after manual review.

**Core principle:** The execution record contains NO raw logs, NO tokens, NO secrets, and NO model artifacts. It is metadata only.

---

## 2. Record Format

```json
{
  "record_type": "micro_sft_execution_record",
  "version": "0.1.37-alpha",
  "timestamp": "ISO-8601 timestamp",
  "status": "pending|completed|failed",
  "job_id": "optional/sanitized",
  "flavor": "HF Jobs flavor (e.g., a10g-small)",
  "image": "HF Jobs image name",
  "training_stack_check_passed": "true|false|unknown",
  "dataset_ready": "true|false|unknown",
  "micro_sft_started": false,
  "micro_sft_completed": false,
  "adapter_generated": "true|false|unknown",
  "adapter_committed": false,
  "hf_upload_performed": false,
  "gguf_generated": false,
  "raw_logs_committed": false,
  "gate_state": "BLOCKED",
  "manual_review_required": true,
  "notes": "Optional notes"
}
```

---

## 3. Status Values

| Status | Meaning | micro_sft_started | micro_sft_completed |
|--------|---------|-------------------|---------------------|
| `pending` | Job not yet executed | false | false |
| `completed` | Job finished successfully | true | true |
| `failed` | Job started but failed | true | false |

---

## 4. Invariant Fields

These fields are ALWAYS set to their safe values regardless of input:

| Field | Always | Reason |
|-------|--------|--------|
| `adapter_committed` | `false` | Adapters are never committed to the repo |
| `hf_upload_performed` | `false` | No HF Hub uploads during alpha |
| `gguf_generated` | `false` | No GGUF exports during alpha |
| `raw_logs_committed` | `false` | Raw logs are never committed |
| `gate_state` | `"BLOCKED"` | Gate remains BLOCKED during alpha |
| `manual_review_required` | `true` | Every record requires human review |

---

## 5. Creating a Record

```bash
# Create a pending record before submission
python training/scripts/create_micro_sft_execution_record.py \
  --status pending \
  --adapter-generated unknown \
  --output /tmp/micro_sft_execution_record.json \
  --json

# Update to completed after job finishes
python training/scripts/create_micro_sft_execution_record.py \
  --status completed \
  --adapter-generated true \
  --job-id sanitized-xxx \
  --flavor a10g-small \
  --training-stack-check-passed true \
  --dataset-ready true \
  --output /tmp/micro_sft_execution_record.json \
  --json
```

---

## 6. Validating a Record

```bash
python training/scripts/validate_micro_sft_execution_record.py \
  --record /tmp/micro_sft_execution_record.json \
  --json
```

Validation checks:
- gate_state == "BLOCKED"
- adapter_committed == false
- hf_upload_performed == false
- gguf_generated == false
- raw_logs_committed == false
- manual_review_required == true
- No token-like strings
- No raw logs
- No public release claim
- Correct record_type

---

## 7. Safety Guarantees

| Guarantee | Enforced By |
|-----------|-------------|
| No adapter weights committed | `adapter_committed=false` invariant + gitignore |
| No HF Hub uploads | `hf_upload_performed=false` invariant + config |
| No GGUF exports | `gguf_generated=false` invariant |
| No raw logs | `raw_logs_committed=false` invariant + validator |
| No tokens/secrets | Token pattern scanning in create + validate |
| Gate stays BLOCKED | `gate_state="BLOCKED"` invariant |
| Human review required | `manual_review_required=true` invariant |

---

## 8. Cross-References

| Document | Relationship |
|----------|-------------|
| [HF_JOBS_MICRO_SFT_RUN.md](HF_JOBS_MICRO_SFT_RUN.md) | Guide for running micro SFT on HF Jobs |
| [HF_JOBS_MICRO_SFT_RUNBOOK.md](HF_JOBS_MICRO_SFT_RUNBOOK.md) | Step-by-step runbook |
| [TRAINING_STACK_COMPATIBILITY.md](TRAINING_STACK_COMPATIBILITY.md) | Training dependency compatibility |
| [ADAPTER_PREVIEW_GATE.md](ADAPTER_PREVIEW_GATE.md) | Gate state machine (BLOCKED) |

---

*Execution records are sanitized metadata only. No weights. No logs. No tokens. Gate BLOCKED.*
