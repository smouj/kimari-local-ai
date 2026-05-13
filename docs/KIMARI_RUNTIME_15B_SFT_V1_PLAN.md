# Kimari Runtime 1.5B SFT v1 Plan

## Objective

Create the first SFT v1 training configuration for Kimari Runtime 1.5B, with a guarded QLoRA setup and dry-run-only execution path for v0.1.60-alpha.

## Base Model

- Model: `Qwen/Qwen2.5-1.5B-Instruct`
- License: Apache-2.0
- License status: approved in `docs/KIMARI_BASE_MODEL_LICENSE_MATRIX.md`

## Dataset

- Dataset: Kimari SFT v1 seed
- Path: `dataset/build/kimari_sft_v1/`
- Size: 320 examples
- Split: 288 train / 32 validation
- Safety gate: BLOCKED

## Config Details

- Config: `training/configs/kimari_runtime_15b_sft_v1.yaml`
- Method: QLoRA
- Max sequence length: 2048
- Max steps: 100
- Epochs: 1
- Learning rate: `5.0e-5`
- LoRA rank: 16
- LoRA alpha: 32
- LoRA dropout: 0.05
- Batch size: 1
- Gradient accumulation: 8
- Scheduler: cosine
- Seed: 42

Safety flags:

- `push_to_hub: false`
- `report_to: none`
- `public_release_allowed: false`
- `hf_public_upload_allowed: false`
- `gguf_export_allowed: false`
- `gate_state: BLOCKED`

## Estimated Cost

Estimated cost is approximately $0.50-2.00 for 100 steps on A10G via HF Jobs.

## Validation Targets

Future real training output will be validated for:

- Loss curve shape and obvious instability
- Adapter coherence on held-out prompts
- No new hallucination patterns
- No safety regression on refusal examples
- No claims of benchmarks or public readiness before eval

## Not Published

For this gate, the following will not be published:

- No adapter repository
- No GGUF file
- No public benchmark claims
- No public weights or checkpoints

## Gate

Current gate: BLOCKED.

Training scripts and wrappers are dry-run-only for v0.1.60-alpha. Public release requires eval, manual review, and an explicit gate transition.
