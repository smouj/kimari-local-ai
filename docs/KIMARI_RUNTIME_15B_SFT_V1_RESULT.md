# Kimari Runtime 1.5B SFT v1 — Training Result

> ✅ **Status: FULL-RUN COMPLETED** — First guarded 100-step SFT v1 run completed on HF Jobs and adapter persisted to private repo.

## Run

| Field | Value |
| --- | --- |
| job_id | `6a052235e48bea4538b9c309` |
| Hardware | `a10g-small` |
| Base model | `Qwen/Qwen2.5-1.5B-Instruct` |
| Method | LoRA / SFT |
| Dataset | Kimari SFT v1 seed: 288 train / 32 validation |
| Steps | 100 |
| Adapter repo | `Smouj013/kimari-runtime-15b-sft-v1-adapter` (private) |
| Gate | BLOCKED |

## Training Metrics

| Metric | Value |
| --- | ---: |
| Initial logged train loss | 2.743 |
| Final logged train loss | 2.393 |
| Eval loss @ step 50 | 2.386 |
| Eval loss @ step 100 | 2.240 |
| Eval mean token accuracy @ step 100 | 0.5591 |
| Train runtime | 98.51s |
| Train steps/sec | 1.015 |
| Train samples/sec | 8.121 |

## Safety Assertions

- `training_performed`: true
- `adapter_generated`: true
- `adapter_persisted_private`: true
- `adapter_committed_public: false`
- `hf_public_upload_performed`: false
- `gguf_generated`: false
- `public_benchmark_allowed`: false
- `gate_state`: BLOCKED

## Decision

- The 100-step full-run completed successfully.
- The adapter is now a stronger candidate than the 10-step micro-run.
- Next step: evaluate baseline vs adapter on subset30 before any longer training run.

## No Release Claim

This is **not** a public model release. No public weights, GGUF, raw outputs, or benchmark claims are allowed yet.
