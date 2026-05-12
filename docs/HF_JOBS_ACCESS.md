# Hugging Face Jobs Access

## Overview

Kimari's HF Jobs smoke test pipeline requires a Hugging Face account with **Jobs access enabled**. This is an account-level feature that may not be available on all account types.

## Checking Access

### 1. Verify Authentication

```bash
huggingface-cli auth whoami
```

If this fails, you need to log in first:

```bash
huggingface-cli login
```

### 2. Check Jobs Availability

```bash
huggingface-cli jobs ps
```

Or use the Kimari helper:

```bash
python training/scripts/check_hf_jobs_access.py --json
```

### Interpreting Results

| Result | Meaning | Action |
|--------|---------|--------|
| Jobs listed | Jobs access is available | Proceed with smoke test |
| 403 Forbidden | Account does not have Jobs access | Use a fallback runner |
| Timeout/Network | Cannot reach HF API | Check network, retry |
| Not authenticated | No HF token configured | Run `huggingface-cli login` |

## What 403 Means

A 403/Forbidden response from `hf jobs ps` means:

- The authenticated account does not have Jobs access enabled
- This is **not an error** — it simply means this feature is not available for your account
- You can still use all other Kimari features (local inference, doctor, optimization)

## Fallback Runners

If HF Jobs is unavailable, see [HF_JOBS_FALLBACK_RUNNERS.md](HF_JOBS_FALLBACK_RUNNERS.md) for alternatives:

- RunPod GPU rental
- Local GTX 1060 smoke validation
- Generic SSH GPU VM
- Docker-based local testing

## Safety Rules

- **Never** commit HF tokens to the repository
- **Never** include billing, plan, or subscription details in any documentation or code
- If `hf jobs ps` fails, do not proceed with smoke test submission
- All smoke test results must be validated before committing

## Programmatic Check

Use the Kimari access checker for CI/automation:

```bash
# Check access, exit 0 if available
python training/scripts/check_hf_jobs_access.py --json

# Check with custom timeout
python training/scripts/check_hf_jobs_access.py --json --timeout 30
```

The JSON output includes `can_continue_to_smoke` which should be checked before any submission.
