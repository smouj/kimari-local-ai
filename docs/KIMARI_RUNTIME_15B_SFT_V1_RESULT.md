# Kimari Runtime 1.5B SFT v1 — Result

## Objective

Run the first SFT v1 real short run for Kimari Runtime on `Qwen/Qwen2.5-1.5B-Instruct` (Apache-2.0).

## Base model

- Model: `Qwen/Qwen2.5-1.5B-Instruct`
- License: Apache-2.0

## Dataset

Kimari SFT v1 seed dataset: 320 examples total.

- Train: 288 examples
- Validation: 32 examples

## Config

- Method: QLoRA
- LoRA rank: `r=16`
- LoRA alpha: `32`
- LoRA dropout: `0.05`
- Max steps: `100`

## Run status

Status: **PENDING** — This is a placeholder document. It is **not** evidence of a completed SFT run. No training has been executed yet.

| Field | Value |
| --- | --- |
| job_id | PENDING |
| status | PENDING |
| GPU | PENDING |
| steps | PENDING |
| loss | PENDING |

> **⚠️ This is a pending result placeholder. It is not evidence of a completed SFT run. Do not treat the values below as confirmed until a real job_id replaces the PENDING fields above.**

## What was done

- `training_performed=false`
- `adapter_generated=false`
- `adapter_persisted_private=false`
- `adapter_load_check=false`
- `generation_success=false`

## What was NOT done

- No training has been executed.
- No adapter has been generated.
- No public weights were published.
- No GGUF was generated.
- No benchmark was claimed or published.
- No gate transition was made.

## Gate

BLOCKED

## Next step

After the real SFT v1 run is executed and validated: evaluate baseline vs SFT v1 adapter.