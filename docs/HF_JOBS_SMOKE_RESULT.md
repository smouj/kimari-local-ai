# HF Jobs Smoke Test Result — Kimari Local AI

> **Document Type:** Smoke test result template and sanitized summary  
> **Version:** v0.1.30-alpha  
> **Date:** 2026-06-01  
> **Status:** Pending — no smoke test executed yet  
> **Gate State:** BLOCKED — no public release, no HF upload

---

## Result Summary

| Field | Value |
|-------|-------|
| status | `pending` |
| job_id | _(not yet available)_ |
| flavor | _(not yet available)_ |
| image | _(not yet available)_ |
| gpu_detected | _(not yet available)_ |
| torch_cuda_available | _(not yet available)_ |
| repo_installed | _(not yet available)_ |
| dataset_dryrun_passed | _(not yet available)_ |
| sft_dryrun_passed | _(not yet available)_ |
| training_performed | `false` |
| adapter_generated | `false` |
| hf_upload_performed | `false` |
| gate_state | `BLOCKED` |

---

## Status Definitions

- **pending**: Smoke test has not been executed yet. This is the default state.
- **completed**: Smoke test ran successfully. All checks passed.
- **failed**: Smoke test ran but one or more checks failed.

---

## How to Fill This Document

After executing the HF Jobs smoke test:

1. Run `python training/scripts/create_hf_jobs_smoke_summary.py` to generate a sanitized summary
2. Review the summary for any tokens, secrets, or sensitive data
3. Run `python scripts/security/scan_for_secrets.py --paths docs/HF_JOBS_SMOKE_RESULT.md --json`
4. Only commit the sanitized summary — never raw logs or tokens

---

## Important Rules

- **training_performed** must always be `false` in v0.1.30-alpha
- **adapter_generated** must always be `false`
- **hf_upload_performed** must always be `false`
- **gate_state** must always be `BLOCKED`
- No raw logs with tokens should ever be committed
- Only sanitized metadata may be committed after human review

---

## Cross-Reference

| Document | Relationship |
|----------|-------------|
| [HF_JOBS_PRIVATE_RUN.md](HF_JOBS_PRIVATE_RUN.md) | Guide for running HF Jobs smoke tests |
| [HF_JOBS_RESULT_HANDOFF.md](HF_JOBS_RESULT_HANDOFF.md) | How to bring sanitized results from HF Jobs |
| [HF_JOBS_SMOKE_RUNBOOK.md](HF_JOBS_SMOKE_RUNBOOK.md) | Step-by-step runbook for smoke test execution |
| [ADAPTER_PREVIEW_GATE.md](ADAPTER_PREVIEW_GATE.md) | Gate state machine (BLOCKED) |

---

*Smoke test result is pending. No training. No upload. No export. Gate BLOCKED. Never pass tokens as arguments.*
