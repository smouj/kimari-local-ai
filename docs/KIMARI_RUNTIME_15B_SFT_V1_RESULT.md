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

Status: PLACEHOLDER — fill with actual `job_id`, status, GPU, steps, and loss after the real short run.

| Field | Value |
| --- | --- |
| job_id | PLACEHOLDER |
| status | PLACEHOLDER |
| GPU | PLACEHOLDER |
| steps | PLACEHOLDER |
| loss | PLACEHOLDER |

## What was done

- `training_performed=true`
- `adapter_generated=true`
- `adapter_persisted_private=true`

## What was NOT done

- No public weights were published.
- No GGUF was generated.
- No benchmark was claimed or published.
- No gate transition was made.

## Gate

BLOCKED

## Next step

Evaluate baseline vs SFT v1 adapter.
