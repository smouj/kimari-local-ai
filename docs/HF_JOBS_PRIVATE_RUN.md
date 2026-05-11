# Hugging Face Jobs Private Run — Kimari Local AI

> **Document Type:** Guide for running Kimari-4B smoke tests on Hugging Face Jobs  
> **Version:** v0.1.31-alpha  
> **Date:** 2026-06-02  
> **Status:** Active — governs HF Jobs usage for Kimari-4B  
> **Gate State:** BLOCKED — no public release, no HF upload

---

## 1. What is HF Jobs in This Project?

Hugging Face Jobs allows running workloads on HF infrastructure using the `hf jobs` CLI. In this project, HF Jobs is used **exclusively** for:

- **Smoke testing** the training environment before any real training
- **Validating** that GPU, torch, CUDA, and the repo work together
- **Dry-running** dataset build and SFT training commands

HF Jobs is **NOT** used for:
- Actual model training (that requires explicit approval and budget)
- Uploading any files to Hugging Face
- Running CI/CD pipelines
- Any automated or scheduled execution

---

## 2. Prerequisites

### HF Login (Required)

Before using HF Jobs, you must authenticate locally:

```bash
# Option 1: Using the new HF CLI
hf auth login

# Option 2: Using the classic CLI
huggingface-cli login
```

**CRITICAL RULES:**
- **Never paste your token in the repo, chat, issues, logs, or screenshots**
- **Never pass `--token` as a command-line argument** — tokens are visible in `ps` output and shell history
- **Only login on machines you control** — never on shared servers or CI runners
- **Prefer local login** over environment variables when possible
- See `docs/HF_TOKEN_SAFETY.md` for comprehensive token safety procedures

### HF Pro/Team Account

HF Jobs is available for users with **Pro** accounts or organizations with **Team/Enterprise** plans. Cost is pay-as-you-go per seconds used.

---

## 3. Budget

- **Recommended starting budget:** $10 USD for smoke tests
- **Smoke test cost:** Typically under $1 (short runtime, small GPU)
- **Flavor selection matters:** Larger GPUs cost more per second
- **Use the cheapest available flavor** for smoke tests
- **Do not spend the entire budget on one attempt**

### Recommended Flavors

| Flavor | GPU | Use Case | Estimated Cost |
|--------|-----|----------|---------------|
| `a10g-small` | A10G | Smoke test (preferred if available) | ~$0.30/hr |
| `l4x1` | L4 | Smoke test (alternative) | ~$0.40/hr |
| `a100` | A100 | Training only (NOT for smoke) | ~$2.00/hr |

> **Only use A100 if you decide to do real training.** For smoke tests, A10G or L4 is sufficient and much cheaper.

---

## 4. Running a Smoke Test

### Step 1: Generate Commands (No Execution)

```bash
# See what the smoke test will do without submitting anything
python training/scripts/hf_jobs_private_run.py \
    --config training/configs/hf_jobs_kimari4b_smoke.v0.yaml \
    --dry-run --json
```

### Step 2: Print the HF Jobs Command

```bash
# Print the exact hf jobs command that would be run
python training/scripts/hf_jobs_private_run.py \
    --config training/configs/hf_jobs_kimari4b_smoke.v0.yaml \
    --print-command
```

### Step 3: Submit (Requires Double Confirmation)

```bash
# Actually submit the job — requires BOTH flags
python training/scripts/hf_jobs_private_run.py \
    --config training/configs/hf_jobs_kimari4b_smoke.v0.yaml \
    --allow-submit --yes
```

> **If either --allow-submit or --yes is missing, the job will NOT be submitted.**

### Step 4: Check Status

```bash
# Check job status
python training/scripts/hf_jobs_status.py --job-id <job-id> --json

# View logs
python training/scripts/hf_jobs_status.py --job-id <job-id> --logs

# View last 50 lines of logs
python training/scripts/hf_jobs_status.py --job-id <job-id> --logs --tail 50
```

---

## 5. What the Smoke Test Checks

The smoke test validates:

1. **GPU Detection** — `nvidia-smi` shows a GPU
2. **Torch CUDA** — `torch.cuda.is_available()` returns True
3. **Repo Install** — `pip install -e .` succeeds
4. **Dataset Build** — `build_dataset_mix.py` runs (dry-run)
5. **SFT Dry-Run** — `train_sft_lora.py --dry-run` validates the config

The smoke test does **NOT**:
- Train any model
- Upload any files
- Export GGUF
- Commit anything
- Advance the preview gate

---

## 6. Forbidden Actions

The following actions are **never** permitted in HF Jobs for this project:

| Action | Forbidden |
|--------|-----------|
| `hf upload` | ✗ Never |
| `huggingface-cli upload` | ✗ Never |
| `git push` | ✗ Never |
| Committing adapter weights | ✗ Never |
| GGUF export | ✗ Never |
| Passing `--token` in commands | ✗ Never |
| Running training without approval | ✗ Never |

---

## 7. After the Smoke Test

After a successful smoke test:

1. **Save the job ID** for reference
2. **Fill the smoke summary template** — `training/templates/hf_jobs_smoke_summary.template.json`
3. **Sanitize logs** — Remove any tokens, local paths, or sensitive data
4. **Run `scan_for_secrets.py`** on any files before committing
5. **Gate stays BLOCKED** — Smoke test success does NOT advance the gate

See `docs/HF_JOBS_RESULT_HANDOFF.md` for the full handoff process.

---

## 8. Security Checklist

Before running any HF Job:

- [ ] HF token not in any file, argument, or log
- [ ] Using `hf auth login` or `huggingface-cli login` (local only)
- [ ] No `--token` flag in any command
- [ ] Smoke config has `allow_training: false`
- [ ] Smoke config has `allow_hf_upload: false`
- [ ] Budget confirmed (start with $10)
- [ ] Using cheapest available flavor
- [ ] Preview gate is BLOCKED

---

## 9. Smoke Test Result Summary

After executing the HF Jobs smoke test, create a sanitized summary:

```bash
python training/scripts/create_hf_jobs_smoke_summary.py \
    --job-id <job-id> \
    --status completed \
    --flavor a10g-small \
    --image pytorch/pytorch:2.6.0-cuda12.4-cudnn9-devel \
    --output /tmp/hf_jobs_smoke_summary.json \
    --json
```

The summary includes:
- job_id, flavor, image, status
- gpu_detected, torch_cuda_available, repo_installed
- dataset_dryrun_passed, sft_dryrun_passed
- training_performed: false (always)
- adapter_generated: false (always)
- hf_upload_performed: false (always)
- gate_state: BLOCKED (always)

See [HF_JOBS_SMOKE_RESULT.md](HF_JOBS_SMOKE_RESULT.md) for the result template.

### Log Sanitization

When viewing HF Jobs logs, always use `--sanitize-logs`:

```bash
python training/scripts/hf_jobs_status.py --job-id <job-id> --logs --sanitize-logs --json
```

This removes:
- HF tokens (hf_...)
- API keys
- Passwords
- Authorization headers

Never commit raw logs. Only sanitized summaries are safe to commit.

### Stderr Sanitization

As of v0.1.31, `--sanitize-logs` also sanitizes stderr (error messages from HF CLI). This prevents accidental token exposure in error output:

```bash
# Both stdout and stderr are sanitized
python training/scripts/hf_jobs_status.py --job-id <job-id> --logs --sanitize-logs --json

# Even inspect errors are sanitized
python training/scripts/hf_jobs_status.py --job-id <job-id> --sanitize-logs --json
```

### Validate Summary Before Committing

After creating the smoke summary, validate it:

```bash
python training/scripts/validate_hf_jobs_smoke_summary.py \
    --summary /tmp/hf_jobs_smoke_summary.json \
    --json
```

The validator checks: training_performed=false, adapter_generated=false, hf_upload_performed=false, gate_state=BLOCKED, logs_sanitized=true, no token-like strings, no raw logs.

---

## 10. Smoke Must Pass Before Micro SFT

**Critical gate:** Do NOT proceed to micro SFT until the HF Jobs smoke test is completed with ALL checks passing:

| Check | Required Value |
|-------|---------------|
| gpu_detected | `true` |
| torch_cuda_available | `true` |
| repo_installed | `true` |
| dataset_dryrun_passed | `true` |
| sft_dryrun_passed | `true` |

If any check fails:
1. Fix the issue (config, image, flavor, code)
2. Re-run the smoke test
3. Validate the new summary
4. Only proceed to micro SFT when all checks pass

The smoke test validates the infrastructure. Micro SFT requires that infrastructure to be proven working first.

See [HF_JOBS_SMOKE_EXECUTION_RECORD.md](HF_JOBS_SMOKE_EXECUTION_RECORD.md) for the execution record template.

---

## Cross-Reference

| Document | Relationship |
|----------|-------------|
| [HF_TOKEN_SAFETY.md](HF_TOKEN_SAFETY.md) | Comprehensive HF token safety procedures |
| [HF_JOBS_RESULT_HANDOFF.md](HF_JOBS_RESULT_HANDOFF.md) | How to bring sanitized results from HF Jobs |
| [HF_JOBS_SMOKE_RESULT.md](HF_JOBS_SMOKE_RESULT.md) | Smoke test result template |
| [HF_JOBS_SMOKE_EXECUTION_RECORD.md](HF_JOBS_SMOKE_EXECUTION_RECORD.md) | Smoke execution record |
| [HF_JOBS_SMOKE_RUNBOOK.md](HF_JOBS_SMOKE_RUNBOOK.md) | Step-by-step runbook |
| [KIMARI4B_PRIVATE_SFT_RUN.md](KIMARI4B_PRIVATE_SFT_RUN.md) | Full private SFT execution guide |
| [KIMARI4B_FIRST_RUN_CHECKLIST.md](KIMARI4B_FIRST_RUN_CHECKLIST.md) | Pre-flight checklist |
| [ADAPTER_PREVIEW_GATE.md](ADAPTER_PREVIEW_GATE.md) | Gate state machine (BLOCKED) |
| [FIRST_PRIVATE_SFT_HANDOFF.md](FIRST_PRIVATE_SFT_HANDOFF.md) | General handoff procedures |

---

*HF Jobs is used for smoke tests only. No training. No upload. No export. Gate BLOCKED. Never pass tokens as arguments.*
