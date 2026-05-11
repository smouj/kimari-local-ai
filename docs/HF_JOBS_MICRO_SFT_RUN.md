# HF Jobs Micro SFT Run — Kimari Local AI

> **Document Type:** Guide for running Kimari-4B micro SFT on Hugging Face Jobs  
> **Version:** v0.1.32-alpha  
> **Date:** 2026-06-02  
> **Status:** Active — governs micro SFT execution on HF Jobs  
> **Gate State:** BLOCKED — no public release, no HF upload

---

## 1. What is Micro SFT?

Micro SFT is a **minimal, private training run** that validates the entire training pipeline on HF Jobs infrastructure with very few steps. It is:

- **Not a release** — No model is published or announced
- **Not a benchmark** — No official metrics are claimed
- **Not a full training run** — Only 10 steps to validate the pipeline
- **Private** — All outputs stay in the HF Jobs environment

The purpose is to prove that the pipeline works end-to-end:

```
HF Jobs → SmolLM3-3B → dataset v0 → LoRA micro-run → adapter (local/temp) → sanitized summary → gate BLOCKED
```

---

## 2. Prerequisites

### Smoke Test Must Pass First

**Critical gate:** The HF Jobs smoke test must be completed with ALL checks passing before proceeding to micro SFT:

| Check | Required Value |
|-------|---------------|
| gpu_detected | `true` |
| torch_cuda_available | `true` |
| repo_installed | `true` |
| dataset_dryrun_passed | `true` |
| sft_dryrun_passed | `true` |

If any check fails, fix the issue and re-run the smoke test. Do NOT proceed to micro SFT.

### HF Login (Required)

```bash
# Verify you are logged in
hf auth whoami

# If not logged in, authenticate locally
hf auth login
```

**CRITICAL RULES:**
- **Never paste your token in the repo, chat, issues, logs, or screenshots**
- **Never pass `--token` as a command-line argument**
- **Only login on machines you control**
- See `docs/HF_TOKEN_SAFETY.md` for comprehensive token safety

### Budget

- **Micro SFT budget cap:** $10 USD
- **Expected cost:** Under $5 (very short runtime, small GPU)
- **Use cheapest available flavor** (a10g-small recommended)

---

## 3. Configuration

The micro SFT is configured in `training/configs/hf_jobs_kimari4b_micro_sft.v0.yaml`:

| Field | Value | Notes |
|-------|-------|-------|
| job_name | `kimari4b-micro-sft-v0` | Identifies this run |
| run_type | `micro_sft_private` | Private, not public |
| allow_training | `true` | Training IS allowed (unlike smoke) |
| allow_hf_upload | `false` | **Never upload** |
| allow_public_release | `false` | **Never publish** |
| preview_gate_state | `BLOCKED` | **Gate stays BLOCKED** |
| max_budget_usd | `10` | Budget cap |
| max_runtime_minutes | `30` | Runtime cap |
| base_model | `HuggingFaceTB/SmolLM3-3B` | Base model |
| micro_sft_steps | `10` | Only 10 training steps |
| flavor | `a10g-small` | Cheapest GPU |

---

## 4. Execution Steps

### Step 1: Validate Smoke Summary

Before micro SFT, verify the smoke test passed:

```bash
python training/scripts/validate_hf_jobs_smoke_summary.py \
    --summary /tmp/hf_jobs_smoke_summary.json \
    --json
```

If validation fails, do NOT proceed. Fix the smoke test first.

### Step 2: Dry-Run (No Execution)

```bash
python training/scripts/hf_jobs_micro_sft.py \
    --config training/configs/hf_jobs_kimari4b_micro_sft.v0.yaml \
    --dry-run --json
```

Review the output carefully. Confirm:
- `allow_training: true` (expected for micro SFT)
- `allow_hf_upload: false`
- `preview_gate_state: BLOCKED`
- Budget is acceptable
- Forbidden actions list is correct

### Step 3: Print Command (Review Before Execution)

```bash
python training/scripts/hf_jobs_micro_sft.py \
    --config training/configs/hf_jobs_kimari4b_micro_sft.v0.yaml \
    --print-command
```

Review the exact `hf jobs run` command. Confirm:
- Flavor is correct
- Image is correct
- Command sequence is correct
- No tokens in the command

### Step 4: Submit (Requires Double Confirmation)

Only when ready, submit with both required flags:

```bash
python training/scripts/hf_jobs_micro_sft.py \
    --config training/configs/hf_jobs_kimari4b_micro_sft.v0.yaml \
    --allow-submit --yes
```

**If either `--allow-submit` or `--yes` is missing, the job will NOT be submitted.**

### Step 5: Check Job Status

```bash
# Quick status check
python training/scripts/hf_jobs_status.py --job-id <job-id> --json

# View logs (sanitized)
python training/scripts/hf_jobs_status.py --job-id <job-id> --logs --sanitize-logs --tail 50
```

### Step 6: Create Sanitized Summary

After the job completes:

```bash
# For completed micro SFT
python training/scripts/create_hf_jobs_micro_sft_summary.py \
    --job-id <job-id> \
    --status completed \
    --flavor a10g-small \
    --adapter-generated true \
    --output /tmp/micro_sft_summary.json \
    --json

# For pending status
python training/scripts/create_hf_jobs_micro_sft_summary.py \
    --status pending \
    --json
```

### Step 7: Validate Summary

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

### Step 8: Scan for Secrets

```bash
python scripts/security/scan_for_secrets.py \
    --paths docs training/templates \
    --json
```

---

## 5. What the Micro SFT Does

The micro SFT validates:

1. **GPU + CUDA** — nvidia-smi and torch.cuda work
2. **Repo Install** — pip install -e . succeeds
3. **Dataset Build** — build_dataset_mix.py works
4. **Training Pipeline** — train_sft_lora.py runs for 10 steps
5. **Adapter Generation** — LoRA adapter is created (local only)

---

## 6. What the Micro SFT Does NOT Do

- No HF Hub upload
- No GGUF export
- No public release
- No official benchmarks
- No gate advancement
- No adapter commit to repository
- No checkpoint commit to repository

---

## 7. Forbidden Actions

| Action | Forbidden | Why |
|--------|-----------|-----|
| `hf upload` | ✗ Never | No public upload |
| `huggingface-cli upload` | ✗ Never | No public upload |
| `git push` | ✗ Never | No code push from jobs |
| Commit adapter weights | ✗ Never | Stays in HF Jobs |
| Commit checkpoints | ✗ Never | Stays in HF Jobs |
| GGUF export | ✗ Never | No quantized export |
| Pass `--token` | ✗ Never | Visible in ps/history |
| Publish results | ✗ Never | Not a release |

---

## 8. Expected Results

If the micro SFT completes successfully:

- An adapter was generated in the HF Jobs environment
- The training pipeline is validated end-to-end
- A sanitized summary can be committed
- Gate remains BLOCKED
- Manual review is required

The adapter itself is **not** brought into the repository. Only the sanitized summary is safe to commit.

---

## 9. Override Smoke Gate

If you need to run micro SFT without a validated smoke summary (not recommended):

```bash
python training/scripts/hf_jobs_micro_sft.py \
    --config training/configs/hf_jobs_kimari4b_micro_sft.v0.yaml \
    --allow-submit --yes --override-smoke-gate
```

**Warning:** Overriding the smoke gate means you skip the infrastructure validation. This is only appropriate if you've already manually verified the environment.

---

## 10. After Micro SFT

After a successful micro SFT:

1. **Review the summary** — Check all safety fields are correct
2. **Validate the summary** — Run the validator
3. **Scan for secrets** — Ensure no tokens leaked
4. **Commit summary only** — Only the sanitized JSON summary
5. **Gate stays BLOCKED** — Micro SFT does not advance the gate

---

## Difference Between Smoke, Micro SFT, and Full SFT

| Aspect | Smoke Test | Micro SFT | Full SFT |
|--------|-----------|-----------|----------|
| Training | No | 10 steps | Full epochs |
| Adapter | No | Maybe (temp) | Yes |
| Budget | <$1 | <$10 | TBD |
| Runtime | <5 min | <30 min | Hours |
| Purpose | Validate env | Validate pipeline | Produce model |
| Gate after | BLOCKED | BLOCKED | BLOCKED → review |
| Commit adapter | Never | Never | Never (until approved) |

---

## Cross-Reference

| Document | Relationship |
|----------|-------------|
| [HF_JOBS_PRIVATE_RUN.md](HF_JOBS_PRIVATE_RUN.md) | General HF Jobs guide |
| [HF_JOBS_SMOKE_RUNBOOK.md](HF_JOBS_SMOKE_RUNBOOK.md) | Smoke test runbook |
| [HF_JOBS_SMOKE_EXECUTION_RECORD.md](HF_JOBS_SMOKE_EXECUTION_RECORD.md) | Smoke execution record |
| [HF_JOBS_MICRO_SFT_RESULT.md](HF_JOBS_MICRO_SFT_RESULT.md) | Micro SFT result template |
| [KIMARI4B_PRIVATE_SFT_RUN.md](KIMARI4B_PRIVATE_SFT_RUN.md) | Full private SFT guide |
| [HF_TOKEN_SAFETY.md](HF_TOKEN_SAFETY.md) | Token safety procedures |
| [ADAPTER_PREVIEW_GATE.md](ADAPTER_PREVIEW_GATE.md) | Gate state machine (BLOCKED) |

---

*Micro SFT validates the pipeline. No upload. No export. No commit. Gate BLOCKED. Manual review required. Not a release.*
