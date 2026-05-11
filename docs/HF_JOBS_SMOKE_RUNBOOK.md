# HF Jobs Smoke Test Runbook — Kimari Local AI

> **Document Type:** Step-by-step runbook for executing HF Jobs smoke test  
> **Version:** v0.1.30-alpha  
> **Date:** 2026-06-01  
> **Status:** Active — governs HF Jobs smoke test execution  
> **Gate State:** BLOCKED — no public release, no HF upload

---

## Overview

This runbook describes how to execute the first HF Jobs smoke test for Kimari-4B. The smoke test validates that the training environment works on HF Jobs infrastructure **without** performing any actual training.

**What the smoke test does:**
- Detects GPU via `nvidia-smi`
- Checks `torch.cuda.is_available()`
- Installs the Kimari repo
- Runs dataset build dry-run
- Runs SFT dry-run

**What the smoke test does NOT do:**
- No training
- No adapter generation
- No HF upload
- No GGUF export
- No gate advancement

---

## Step 1: Secure Login

Before running any HF Job, authenticate securely:

```bash
# Verify you are logged in
hf auth whoami

# If not logged in, authenticate locally
hf auth login
# Or: huggingface-cli login
```

**CRITICAL RULES:**
- NEVER paste your token in the repo, chat, issues, logs, or screenshots
- NEVER pass `--token` as a command-line argument
- Only login on machines you control
- See `docs/HF_TOKEN_SAFETY.md` for comprehensive token safety

---

## Step 2: Print Command (Review Before Execution)

Before submitting, review the exact command that will be run:

```bash
python training/scripts/hf_jobs_private_run.py \
    --config training/configs/hf_jobs_kimari4b_smoke.v0.yaml \
    --print-command
```

Review the output carefully. Confirm:
- Flavor is correct (a10g-small or l4x1)
- Image is correct
- Commands look right
- No tokens in the command

---

## Step 3: Execute with Double Confirmation

Only when you are ready, submit with both required flags:

```bash
python training/scripts/hf_jobs_private_run.py \
    --config training/configs/hf_jobs_kimari4b_smoke.v0.yaml \
    --allow-submit \
    --yes
```

**If either `--allow-submit` or `--yes` is missing, the job will NOT be submitted.**

---

## Step 4: Check Job Status

After submission, check the job status:

```bash
# Quick status check
python training/scripts/hf_jobs_status.py --job-id <job-id> --json

# View logs (sanitized)
python training/scripts/hf_jobs_status.py --job-id <job-id> --logs --sanitize-logs

# View last 50 lines (sanitized)
python training/scripts/hf_jobs_status.py --job-id <job-id> --logs --tail 50 --sanitize-logs
```

**Always use `--sanitize-logs`** when viewing logs that might be shared or committed.

---

## Step 5: Create Sanitized Summary

After the job completes (or fails), create a sanitized summary:

```bash
# For a completed smoke test
python training/scripts/create_hf_jobs_smoke_summary.py \
    --job-id <job-id> \
    --status completed \
    --flavor a10g-small \
    --image pytorch/pytorch:2.6.0-cuda12.4-cudnn9-devel \
    --gpu-detected \
    --torch-cuda \
    --repo-installed \
    --dataset-dryrun \
    --sft-dryrun \
    --output /tmp/hf_jobs_smoke_summary.json \
    --json

# For a pending status (if not yet executed)
python training/scripts/create_hf_jobs_smoke_summary.py \
    --status pending \
    --flavor a10g-small \
    --image pytorch/pytorch:2.6.0-cuda12.4-cudnn9-devel \
    --json
```

---

## Step 6: Scan for Secrets

Before committing anything, scan for secrets:

```bash
python scripts/security/scan_for_secrets.py \
    --paths docs training/templates \
    --json
```

If any secrets are found, do NOT commit. Fix the issue first.

---

## Step 7: What to Commit and What NOT to Commit

### Safe to Commit
- Sanitized smoke summary JSON
- Updated `docs/HF_JOBS_SMOKE_RESULT.md`
- Any updated documentation
- Test files

### NEVER Commit
- Raw logs (even sanitized, prefer summaries)
- Adapter weights, checkpoints, or GGUF files
- Any file containing tokens or API keys
- Complete unredacted job output

---

## Troubleshooting

### Job Submission Fails
- Check `hf auth whoami` — are you authenticated?
- Check HF account type — Jobs requires Pro/Team/Enterprise
- Check your billing/payment method
- Try a different flavor if the selected one is unavailable

### GPU Not Detected
- Try a different GPU flavor
- Check if the Docker image supports the selected GPU

### torch.cuda.is_available() Returns False
- The Docker image may not have CUDA support
- Try a different CUDA-enabled image
- Check the image tag matches your flavor's CUDA version

### Dataset Build Fails
- The dataset files may not exist in the remote environment
- This is expected if the repo is cloned but dataset isn't built yet
- The dry-run should still work if the script handles missing files gracefully

---

## Cross-Reference

| Document | Relationship |
|----------|-------------|
| [HF_JOBS_PRIVATE_RUN.md](HF_JOBS_PRIVATE_RUN.md) | General guide for HF Jobs usage |
| [HF_JOBS_RESULT_HANDOFF.md](HF_JOBS_RESULT_HANDOFF.md) | How to bring sanitized results |
| [HF_JOBS_SMOKE_RESULT.md](HF_JOBS_SMOKE_RESULT.md) | Smoke test result template |
| [HF_TOKEN_SAFETY.md](HF_TOKEN_SAFETY.md) | Comprehensive token safety procedures |
| [ADAPTER_PREVIEW_GATE.md](ADAPTER_PREVIEW_GATE.md) | Gate state machine (BLOCKED) |

---

*Follow this runbook step by step. No shortcuts. No tokens in CLI. Always sanitize logs. Gate BLOCKED.*
