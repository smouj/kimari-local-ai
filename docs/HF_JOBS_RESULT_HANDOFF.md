# HF Jobs Result Handoff — Kimari Local AI

> **Document Type:** Guide for bringing sanitized results from HF Jobs to the repo  
> **Version:** v0.1.29-alpha  
> **Date:** 2026-05-31  
> **Status:** Active — governs HF Jobs result handoff  
> **Gate State:** BLOCKED

---

## 1. Purpose

This document defines what to bring from an HF Jobs smoke test run to the repository, and what must remain on the remote machine.

---

## 2. What to Bring

| Item | Format | Committable? |
|------|--------|-------------|
| Job ID | Text | Yes (after sanitization) |
| Smoke summary | JSON (from template) | Yes (after review) |
| Sanitized logs | Text (tokens/paths removed) | Only if needed for debugging |

### Smoke Summary Template

Use `training/templates/hf_jobs_smoke_summary.template.json` to record:

- `job_id` — The HF Jobs job identifier
- `job_name` — From config
- `flavor` — GPU flavor used
- `image` — Docker image used
- `started_at` / `finished_at` — Timestamps
- `status` — Job completion status
- `gpu_detected` — Whether GPU was detected
- `torch_cuda_available` — Whether CUDA was available
- `repo_installed` — Whether repo installed successfully
- `dataset_dryrun_passed` — Whether dataset build dry-run passed
- `sft_dryrun_passed` — Whether SFT dry-run passed
- `training_performed` — Must be `false`
- `adapter_generated` — Must be `false`
- `hf_upload_performed` — Must be `false`
- `logs_sanitized` — Must be `true`
- `gate_state` — Must be `BLOCKED`

---

## 3. What NOT to Bring

| Item | Why |
|------|-----|
| Raw logs with tokens | Security risk |
| Adapter weights | Must remain local |
| Checkpoints | Must remain local |
| GGUF exports | Must remain local |
| HF upload artifacts | Must not exist |
| Raw eval outputs | Contains model responses |
| Environment variable dumps | May contain tokens |
| `~/.cache/huggingface/` | Contains cached tokens |

---

## 4. Sanitization Process

Before committing any summary:

1. **Remove all tokens** — Search for `hf_` patterns and remove
2. **Remove local paths** — Replace `/home/user/`, `/Users/user/`, `C:\Users\` with `PLACEHOLDER`
3. **Remove any model outputs** — No responses, no completions, no generated text
4. **Verify gate state** — `gate_state` must be `BLOCKED`
5. **Verify no training** — `training_performed` must be `false`
6. **Verify no upload** — `hf_upload_performed` must be `false`
7. **Run `scan_for_secrets.py`** — `python scripts/security/scan_for_secrets.py --paths <file> --json`

---

## 5. Example Handoff

```bash
# 1. On the HF Jobs machine, collect results
python training/scripts/hf_jobs_status.py --job-id <id> --json > /tmp/hf_job_status.json

# 2. Fill the smoke summary template manually
# Copy training/templates/hf_jobs_smoke_summary.template.json
# Fill in the real values from the job status

# 3. Sanitize
python scripts/security/scan_for_secrets.py --paths /tmp/hf_smoke_summary.json --json

# 4. If clean, bring to local repo
# (Use scp, copy-paste, or other secure transfer — never commit raw logs)

# 5. Review and commit the sanitized summary
git add training/hf_jobs_smoke_summary.json
git commit -m "docs: add HF Jobs smoke test summary"
```

---

## 6. Emergency: Token Found in Handoff

If you discover a token in any file during handoff:

1. **Do NOT commit the file**
2. **Revoke the token immediately** at https://huggingface.co/settings/tokens
3. **Remove the token from the file**
4. **Re-run scan_for_secrets.py**
5. **Follow docs/HF_TOKEN_SAFETY.md** for full incident response

---

## Cross-Reference

| Document | Relationship |
|----------|-------------|
| [HF_JOBS_PRIVATE_RUN.md](HF_JOBS_PRIVATE_RUN.md) | How to run HF Jobs smoke tests |
| [HF_TOKEN_SAFETY.md](HF_TOKEN_SAFETY.md) | Token safety procedures |
| [FIRST_PRIVATE_SFT_HANDOFF.md](FIRST_PRIVATE_SFT_HANDOFF.md) | General handoff procedures |
| [ADAPTER_PREVIEW_GATE.md](ADAPTER_PREVIEW_GATE.md) | Gate state (BLOCKED) |
| [PRIVATE_RUN_ARTIFACTS.md](PRIVATE_RUN_ARTIFACTS.md) | Artifact classification |

---

*Only sanitized summaries may be committed from HF Jobs. No adapters. No checkpoints. No GGUF. No raw logs with tokens. Gate BLOCKED.*
