# CUDA Inference Validation — v0.1.87-alpha

> **Last updated:** 2026-05-17  
> **Validation type:** Real CUDA inference on local GTX 1060 6GB (-ngl all)  
> **Scope:** Runtime validation (GPU offload, VRAM usage, tokens/s, endpoint behavior)

---

## Honest Status

| Item | Status |
|------|--------|
| CUDA device detection | ✅ Verified (NVIDIA GeForce GTX 1060 6GB, compute capability 6.1) |
| llama-server CUDA build | ✅ Verified (build_info: b1-706fbd8) |
| Full GPU offload (-ngl all) | ✅ Verified (offloaded 23/23 layers to GPU) |
| /health endpoint | ✅ Verified |
| /v1/chat/completions endpoint | ✅ Verified |
| VRAM usage measured during GPU inference | ✅ Verified |
| GPU generation tokens/s measured | ✅ Verified |
| Qwen3-4B GPU run | ⚠️ Pending local download completion |
| SmolLM3 GPU run | ⚠️ Pending local download completion |

## Scope

This validates GTX 1060 CUDA offload with a local GGUF test model.

It does NOT validate:
- Qwen3-4B on GTX 1060
- SmolLM3 on GTX 1060
- agent-qwen1060
- agent-smollm1060
- GPU VRAM/tokens/s for public agent profiles

---

## Test Environment

| Field | Value |
|-------|-------|
| GPU | NVIDIA GeForce GTX 1060 6GB |
| Total VRAM | 6143 MiB |
| Driver | 581.57 |
| Runtime | WSL2 Linux |
| llama-server | ~/.local/bin/llama-server |
| llama-server version | version: 1 (706fbd8) |
| CUDA arch reported | ARCHS = 610 |
| Model tested | tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf |
| Model source | TinyLlama/TinyLlama-1.1B-Chat-v1.0-GGUF |
| Profile | Manual llama-server CUDA validation (not agent-qwen1060) |
| Port | 11436 |
| Reason for port | Clean validation port; default 11435 avoided |

---

## Validated Run (GTX 1060, -ngl all)

### Command

    ~/.local/bin/llama-server \
      -m ~/.local/share/kimari/models/tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf \
      --host 127.0.0.1 --port 11436 \
      -c 8192 -b 128 -ub 64 -t 4 \
      -ngl all --parallel 1 \
      --no-warmup --timeout 600

### GPU Offload Evidence (from server log)

- load_tensors: offloaded 23/23 layers to GPU
- CUDA0 model buffer size = 601.02 MiB
- CUDA0 KV buffer size = 176.00 MiB
- CUDA0 compute buffer size = 11.31 MiB

### VRAM / Utilization Snapshots

| Moment | VRAM Used | GPU Utilization | Temp |
|--------|-----------|-----------------|------|
| Model loaded (idle) | 2203 MiB | 1% | 48C |
| After generation request | 2194 MiB | 90% | 54C |

### Measured Throughput (/v1/chat/completions, max_tokens=512)

| Metric | Value |
|--------|-------|
| Prompt tokens | 69 |
| Prompt throughput | 1159.20 tok/s |
| Generated tokens | 404 |
| Generation throughput | 103.63 tok/s |
| Generation ms/token | 9.65 ms/token |

---

## Key Findings

1. GTX 1060 CUDA path is working end-to-end with real full-layer GPU offload (-ngl all).
2. OpenAI-compatible API works with GPU inference (/health and /v1/chat/completions).
3. VRAM and GPU utilization are observable and consistent with active GPU generation.
4. Measured generation speed for this validated run is 103.63 tok/s.

---

## Limits and Non-Claims

- This document validates a real GPU runtime path, not universal performance for all models.
- Qwen3-4B and SmolLM3 GPU measurements are still pending local download completion in this environment.
- No claim is made here about GTX 1080, long-duration stability, or 8K quality ceilings beyond this runtime check.
- Kimari-4B remains unreleased. Gate remains BLOCKED.

---

## Next Step to Close v0.1.87-alpha Completely

Run the same -ngl all measurement flow for:

1. Qwen3-4B-Q4_K_M.gguf
2. SmolLM3-Q4_K_M.gguf

Then append per-model VRAM and tokens/s tables in this file.
