# HF Jobs Micro SFT Runbook — Kimari Local AI

> **Document Type:** Step-by-step runbook for HF Jobs micro SFT execution  
> **Version:** v0.1.35-alpha  
> **Date:** 2026-06-03  
> **Status:** Active — governs micro SFT execution procedure  
> **Gate State:** BLOCKED — no public release, no HF upload

---

## 1. Overview

This runbook describes the exact steps to execute a micro SFT run on Hugging Face Jobs. Every step includes safety checks to ensure no adapters, raw logs, tokens, or model artifacts are committed to the repository.

**Principle:** Only sanitized execution records may be committed. Everything else stays in the HF Jobs environment.

---

## 2. Prerequisites

- HF CLI installed (`pip install huggingface_hub`)
- HF account with Jobs access
- Training dependencies installed locally
- Smoke test completed and validated

---

## 3. Step-by-Step Procedure

### Step 1: Login (Secure)

```bash
huggingface-cli login
# Paste token when prompted — NEVER pass token as CLI argument
```

### Step 2: Validate Smoke Summary

```bash
python training/scripts/validate_hf_jobs_smoke_summary.py \
  --summary /tmp/hf_jobs_smoke_summary.json \
  --json
```

If validation fails, do NOT proceed. Fix smoke test first.

### Step 3: Check Training Stack

```bash
python training/scripts/check_training_stack.py --json
```

Verify all core imports succeed and compatibility is confirmed.

### Step 4: Validate Micro SFT Readiness

```bash
python training/scripts/validate_micro_sft_readiness.py \
  --config training/configs/hf_jobs_kimari4b_micro_sft.v0.yaml \
  --json
```

All checks must pass.

### Step 5: Create Pending Execution Record

```bash
python training/scripts/create_micro_sft_execution_record.py \
  --status pending \
  --adapter-generated unknown \
  --output /tmp/micro_sft_execution_record.json \
  --json
```

### Step 6: Print Command (Review Before Submit)

```bash
python training/scripts/hf_jobs_micro_sft.py \
  --config training/configs/hf_jobs_kimari4b_micro_sft.v0.yaml \
  --require-smoke-summary /tmp/hf_jobs_smoke_summary.json \
  --print-command
```

Review the command carefully. Verify:
- No push_to_hub
- No huggingface-cli upload
- --micro-run --yes are present
- Budget is ≤$10

### Step 7: Submit (Requires Double Confirmation)

```bash
python training/scripts/hf_jobs_micro_sft.py \
  --config training/configs/hf_jobs_kimari4b_micro_sft.v0.yaml \
  --require-smoke-summary /tmp/hf_jobs_smoke_summary.json \
  --allow-submit \
  --yes
```

The `--require-smoke-summary` flag ensures a validated smoke test exists before submission. Without it (or without `--override-smoke-gate`), submission is blocked.

### Step 8: Check Status / Collect Sanitized Logs

```bash
python training/scripts/hf_jobs_status.py --job-id <id> --json --sanitize-logs
```

### Step 9: Update Execution Record

```bash
python training/scripts/create_micro_sft_execution_record.py \
  --status completed \
  --adapter-generated true \
  --job-id <sanitized-job-id> \
  --flavor a10g-small \
  --training-stack-check-passed true \
  --dataset-ready true \
  --output /tmp/micro_sft_execution_record.json \
  --json
```

### Step 10: Validate Execution Record

```bash
python training/scripts/validate_micro_sft_execution_record.py \
  --record /tmp/micro_sft_execution_record.json \
  --json
```

Must pass all checks before committing.

### Step 11: Scan for Secrets

```bash
python scripts/security/scan_for_secrets.py \
  --paths /tmp/micro_sft_execution_record.json \
  --json
```

### Step 12: Commit ONLY Execution Record

```bash
# Copy the validated record to a known location
cp /tmp/micro_sft_execution_record.json training/records/

# Add only the execution record
git add training/records/micro_sft_execution_record.json

# Verify nothing else is staged
git diff --cached --stat

# Commit
git commit -m "micro SFT execution record: status=completed, gate=BLOCKED"
```

**NEVER commit:**
- Adapter files (*.safetensors, adapter_config.json)
- Checkpoint directories
- GGUF files
- Raw logs
- Token files

---

## 4. Troubleshooting

| Problem | Solution |
|---------|----------|
| Smoke summary not found | Run smoke test first, see HF_JOBS_MICRO_SFT_RUN.md |
| Training stack check fails | Install missing deps: `pip install -r training/requirements-training.txt` |
| Submit blocked | Ensure `--require-smoke-summary` points to valid summary, or use `--override-smoke-gate` (not recommended) |
| Job fails | Create record with `--status failed`, review sanitized logs |
| Token detected in record | Review and recreate — token scanning is automatic but verify manually |

---

## 5. Safety Checklist

Before committing any execution record:

- [ ] `validate_micro_sft_execution_record.py` passes all checks
- [ ] `scan_for_secrets.py` finds no issues
- [ ] No adapter/GGUF/checkpoint files are staged
- [ ] `gate_state == "BLOCKED"` in the record
- [ ] `adapter_committed == false` in the record
- [ ] `hf_upload_performed == false` in the record
- [ ] `raw_logs_committed == false` in the record
- [ ] Manual review performed

---

## 6. Cross-References

| Document | Relationship |
|----------|-------------|
| [HF_JOBS_MICRO_SFT_RUN.md](HF_JOBS_MICRO_SFT_RUN.md) | Micro SFT guide |
| [HF_JOBS_MICRO_SFT_EXECUTION_RECORD.md](HF_JOBS_MICRO_SFT_EXECUTION_RECORD.md) | Execution record format |
| [TRAINING_STACK_COMPATIBILITY.md](TRAINING_STACK_COMPATIBILITY.md) | Training stack compatibility |
| [HF_TOKEN_SAFETY.md](HF_TOKEN_SAFETY.md) | Token safety procedures |
| [ADAPTER_PREVIEW_GATE.md](ADAPTER_PREVIEW_GATE.md) | Gate state machine (BLOCKED) |

---

*This runbook governs micro SFT execution on HF Jobs. Only sanitized records may be committed. No adapters. No raw logs. No tokens. Gate BLOCKED.*
