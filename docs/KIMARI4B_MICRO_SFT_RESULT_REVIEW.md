# Kimari-4B Micro SFT Result Review

> Post-run review of the first real micro SFT training on Hugging Face Jobs.

## What Was Validated ✅

| Capability | Result |
|-----------|--------|
| HF Jobs submission | ✅ Works (5 attempts, 4 failed, 1 succeeded) |
| GPU detection on A10G | ✅ NVIDIA A10G, 22.3 GB VRAM, CUDA 12.4 |
| PyTorch CUDA inference | ✅ torch.cuda.is_available() = true |
| Model loading (Qwen2.5-1.5B) | ✅ Downloaded and loaded successfully |
| LoRA application | ✅ 1,089,536 trainable params (0.07% of total) |
| Training loop (10 steps) | ✅ Completed without errors |
| Adapter save | ✅ Saved to /tmp/kimari4b-micro-sft-adapter |
| Cost control | ✅ ~$0.35 for 10 steps on a10g-small |
| Safety flags | ✅ All false (adapter_committed, hf_upload, push_to_hub, gguf) |
| Gate | ✅ BLOCKED |

## What Was NOT Validated ❌

| Capability | Reason |
|-----------|--------|
| Adapter quality | Loss went from 2.62 to 3.19 — not meaningful (tiny inline dataset) |
| Adapter persistence | Ephemeral storage only, adapter was not retrieved |
| Baseline comparison | No baseline eval was run before or after training |
| Real dataset training | Only 3 inline examples used, not the full 72-example dataset |
| Adapter retrieval | No mechanism to download adapter from HF Jobs ephemeral storage |
| Model convergence | 10 steps on 3 examples is insufficient for any quality assessment |

## Failed Attempts (Stack Compatibility)

| Attempt | Docker Image | Error | Resolution |
|---------|-------------|-------|------------|
| 1 | pytorch:2.1.0-cuda12.1 | transformers≥4.36 requires PyTorch≥2.4 | Upgrade Docker image |
| 2 | pytorch:2.4.0-cuda12.1 | transformers==4.36.4 not on PyPI | Pin transformers==4.36.2 |
| 3 | pytorch:2.4.0-cuda12.1 | peft needs EncoderDecoderCache from newer transformers | Upgrade transformers |
| 4 | pytorch:2.4.0-cuda12.1 | transformers>=4.46 incompatible with PyTorch 2.4 | Upgrade Docker image |
| **5** | **pytorch:2.5.1-cuda12.4** | **WORKS** | ✅ |

**Working stack**: `pytorch/pytorch:2.5.1-cuda12.4-cudnn9-devel` + `transformers>=4.46` + `trl` + `peft` + `accelerate`

## Dataset Hash Documentation

| Field | Value | Description |
|-------|-------|-------------|
| `file_sha256` | `f8ce140b5e2e127e4324f3a7c4785480...` | SHA256 of the raw JSONL file |
| `normalized_sha256` | `41afe87152d0291e97d445369d251bd1...` | SHA256 of sorted-keys normalized JSON |
| `record_count` | 72 | Number of examples |
| `byte_size` | 28,692 | Raw file size in bytes |

**Note**: The previous config had hash `2a7f55ef157e1be68d1e01daa715d9ae` which was from an earlier version of the dataset (before fixing "respuesta" → "response"). This has been corrected to `f8ce140b...` (file_sha256 prefix) in all files.

## Key Takeaways

1. **Training pipeline works end-to-end** on HF Jobs with A10G GPU
2. **Adapter was generated** but stored in ephemeral `/tmp/` — not retrievable
3. **Loss is not meaningful** — 3 inline examples, 10 steps, not the real 72-example dataset
4. **No benchmark claims** — this validates the pipeline, not the model quality
5. **Gate remains BLOCKED** — no automatic transition

## Next Steps

1. **v0.1.50-alpha**: Adapter persistence strategy, hash consistency, eval preparation
2. **v0.1.51-alpha**: Second micro SFT run with adapter retrieval
3. **v0.1.52-alpha**: Baseline vs adapter eval