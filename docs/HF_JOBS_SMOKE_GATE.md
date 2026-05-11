# HF Jobs Smoke Gate — Kimari Local AI

> **Document Type:** Smoke gate resolution reference  
> **Version:** v0.1.36-alpha  
> **Date:** 2026-06-03  
> **Status:** Active — governs smoke gate resolution for micro SFT submission  
> **Gate State:** BLOCKED — no public release, no HF upload

---

## 1. Overview

The smoke gate ensures that a validated smoke test has been completed before a micro SFT job is submitted to Hugging Face Jobs. This document explains the three ways to resolve the smoke gate and the recommended approach.

The `resolve_smoke_gate()` function in `hf_jobs_micro_sft.py` handles gate resolution with a single code path, eliminating duplicate checks.

---

## 2. Explicit Path (Recommended)

```bash
python training/scripts/hf_jobs_micro_sft.py \
  --config training/configs/hf_jobs_kimari4b_micro_sft.v0.yaml \
  --require-smoke-summary /path/to/smoke_summary.json \
  --allow-submit --yes
```

**Why this is recommended:**

- The path is explicit and verifiable
- Works across machines (not dependent on `/tmp` state)
- No ambiguity about which smoke summary is being used
- The `smoke_gate_source` field in JSON output will be `"explicit"`

**Validation rules:**

- File must exist at the given path
- File must contain valid JSON
- `status` must be `"completed"`
- `gate_state` must be `"BLOCKED"`

---

## 3. Default /tmp Fallback

If `--require-smoke-summary` is not provided and `--override-smoke-gate` is not used, the gate falls back to checking `/tmp/hf_jobs_smoke_summary.json`.

```bash
python training/scripts/hf_jobs_micro_sft.py \
  --config training/configs/hf_jobs_kimari4b_micro_sft.v0.yaml \
  --allow-submit --yes
```

**Why this is NOT recommended across machines:**

- `/tmp` is machine-local — the file won't exist on a different machine
- The file can be accidentally deleted
- Harder to audit which summary was used
- The `smoke_gate_source` field in JSON output will be `"default_tmp"`

This fallback exists for convenience when working on the same machine where the smoke test was run, but should not be relied upon for production workflows.

---

## 4. Override (Last Resort)

```bash
python training/scripts/hf_jobs_micro_sft.py \
  --config training/configs/hf_jobs_kimari4b_micro_sft.v0.yaml \
  --override-smoke-gate \
  --allow-submit --yes
```

**⚠️ WARNING:** This bypasses the smoke gate entirely. Use only in exceptional circumstances where:

- A smoke test has been completed but the summary file is unavailable
- You are in a development/testing environment and understand the risks
- You have manually verified that the smoke test conditions are met

The `smoke_gate_source` field in JSON output will be `"override"`.

**Do not use `--override-smoke-gate` if:**

- You have not run a smoke test at all
- You are unsure whether the smoke test passed
- You are in a production or CI environment

---

## 5. Gate Resolution Logic

The `resolve_smoke_gate()` function follows this decision tree:

1. If `--override-smoke-gate` is set → return `(True, "override message", "override")`
2. If `--require-smoke-summary PATH` is provided → validate that path → return `(result, message, "explicit")`
3. If neither → fall back to `/tmp/hf_jobs_smoke_summary.json` → validate → return `(result, message, "default_tmp")`

**Key fix in v0.1.36-alpha:** Previously, the code checked BOTH the `/tmp` path AND the explicit path. This meant that even if you provided a valid explicit path, a missing `/tmp/hf_jobs_smoke_summary.json` could block submission. Now, only ONE path is checked.

---

## 6. When Smoke Gate Blocks

The smoke gate will block submission if:

- The smoke summary file does not exist (explicit or /tmp path)
- The smoke summary file is not valid JSON
- `status` is not `"completed"` — do not advance if the smoke status is anything other than `"completed"`
- `gate_state` is not `"BLOCKED"`

**Gate remains BLOCKED.** Smoke gate validation does not change the gate state. The gate stays BLOCKED regardless of smoke test outcome.

---

## 7. JSON Output Fields

When using `--json`, the following fields are included:

| Field | Type | Description |
|-------|------|-------------|
| `smoke_gate_source` | `string \| null` | How the gate was resolved: `"explicit"`, `"default_tmp"`, `"override"`, or `null` |
| `smoke_gate_validated` | `bool` | Whether the smoke gate passed |
| `smoke_gate_message` | `string` | Human-readable message about the gate result |
| `smoke_summary_path` | `string \| null` | The path used for validation (explicit or `/tmp`) |

---

## 8. Cross-References

| Document | Relationship |
|----------|-------------|
| [HF_JOBS_MICRO_SFT_RUNBOOK.md](HF_JOBS_MICRO_SFT_RUNBOOK.md) | Step-by-step execution runbook |
| [HF_JOBS_MICRO_SFT_RUN.md](HF_JOBS_MICRO_SFT_RUN.md) | Micro SFT guide |
| [HF_JOBS_SMOKE_RUNBOOK.md](HF_JOBS_SMOKE_RUNBOOK.md) | Smoke test execution runbook |
| [ADAPTER_PREVIEW_GATE.md](ADAPTER_PREVIEW_GATE.md) | Gate state machine (BLOCKED) |
| [HF_TOKEN_SAFETY.md](HF_TOKEN_SAFETY.md) | Token safety procedures |

---

*This document governs smoke gate resolution for HF Jobs micro SFT submission. Explicit path is recommended. /tmp fallback is supported but not recommended across machines. Override is a last resort. Gate remains BLOCKED.*
