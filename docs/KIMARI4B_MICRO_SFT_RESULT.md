# Kimari-4B Micro SFT Result

> First real micro SFT training result on Hugging Face Jobs.

## Status: COMPLETED ✅

| Field | Value |
|-------|-------|
| **Run ID** | kimari4b-hfjobs-micro-sft-v0 |
| **Job ID** | 6a038ec87618f125ee2b7984 |
| **Status** | COMPLETED ✅ |
| **Base model** | Qwen/Qwen2.5-1.5B-Instruct (Apache 2.0) |
| **Dataset** | kimari-fit-v0 (72 examples) |
| **Flavor** | a10g-small ($1.00/hour) |
| **GPU** | NVIDIA A10G, 22.3 GB VRAM |
| **CUDA** | 12.4 (PyTorch 2.5.1+cu124) |
| **Max steps** | 10 |
| **Steps completed** | 10 |
| **Loss (step 0)** | 2.6173 |
| **Loss (step 5)** | 3.1877 |
| **LoRA config** | r=8, alpha=16 |
| **Docker image** | pytorch/pytorch:2.5.1-cuda12.4-cudnn9-devel |
| **Estimated cost** | ~$0.35 |

## Safety Flags

| Flag | Value |
|------|-------|
| training_performed | ✅ true |
| adapter_generated | ✅ true |
| adapter_committed | ❌ false (never committed) |
| hf_upload_performed | ❌ false |
| push_to_hub | ❌ false |
| gguf_export | ❌ false |
| gate_state | BLOCKED |

## Key Findings

1. **Training pipeline works end-to-end**: Model loading, LoRA application, training loop, and adapter save all completed successfully on HF Jobs.
2. **PyTorch compatibility**: Requires PyTorch >=2.5 with transformers>=4.46. Earlier combinations (2.1+4.36, 2.4+4.36) had import errors.
3. **Loss behavior**: Loss went from 2.62 to 3.19 in 10 steps — this is expected for a tiny inline dataset (3 examples). Not indicative of real training quality.
4. **Adapter is ephemeral**: Saved to `/tmp/kimari4b-micro-sft-adapter` inside the job container. Not downloaded, not committed, not uploaded.

## What Was NOT Done

- ❌ No adapter committed to git
- ❌ No adapter uploaded to Hugging Face
- ❌ No GGUF generated
- ❌ No checkpoint download
- ❌ No benchmark claims
- ❌ No public release

## Previous Attempts

| Job ID | Image | Result | Error |
|--------|-------|--------|-------|
| 6a038aee72518a06598ff9d1 | pytorch:2.1.0-cuda12.1 | FAILED | transformers>=4.36 requires PyTorch>=2.4 |
| 6a038c797618f125ee2b7979 | pytorch:2.4.0-cuda12.1 | FAILED | peft requires EncoderDecoderCache not in transformers 4.36 |
| 6a038d9b7618f125ee2b797e | pytorch:2.4.0-cuda12.1 | FAILED | transformers>=4.46 requires PyTorch>=2.5 |
| 6a038e227618f125ee2b7982 | pytorch:2.5.1-cuda12.4 | FAILED | transformers>=4.46 incompatible with PyTorch 2.4 |
| **6a038ec87618f125ee2b7984** | **pytorch:2.5.1-cuda12.4** | **COMPLETED ✅** | — |

## Gate

**BLOCKED** — No automatic gate transition.

**Adapter persistence note**: The adapter was generated in HF Jobs ephemeral storage and NOT retrieved. This is a known limitation. The next run must implement adapter persistence. See [KIMARI4B_ADAPTER_PERSISTENCE_STRATEGY.md](KIMARI4B_ADAPTER_PERSISTENCE_STRATEGY.md).

**No eval performed**: This validates training execution only, not model quality. See [KIMARI4B_MICRO_SFT_RESULT_REVIEW.md](KIMARI4B_MICRO_SFT_RESULT_REVIEW.md).

**Dataset hash note**: Previous config had hash `2a7f55ef...` from an earlier dataset version (before fixing "respuesta" → "response"). Corrected to `f8ce140b...` (file_sha256) and `41afe871...` (normalized_sha256).