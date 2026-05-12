# GTX 1060 Local Runtime Validation Result

**Status:** Local validation (not official benchmark)

---

## Hardware

| Component | Detail |
|-----------|--------|
| GPU | NVIDIA GeForce GTX 1060 6GB |
| VRAM | 6144 MiB |
| OS | WSL2 Ubuntu 24.04 |
| Driver | 581.57 |

## llama-server

| Field | Detail |
|-------|--------|
| Commit | `706fbd8` |
| Build | CUDA |

## Model Tested

**TinyLlama 1.1B Q4_K_M** (`tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf`)

> **This is NOT Kimari-4B.** TinyLlama was used as a test model to validate the runtime pipeline.

---

## Results

| Mode | Prompt (tok/s) | Generation (tok/s) | VRAM |
|------|----------------|---------------------|------|
| **CUDA** | 228 | 73 | 1221 MiB |
| **CPU-only** | 77 | 33 | — |

### CUDA Speedup vs CPU-only

- Prompt: **~2.2x**
- Generation: **~2.2x**

---

## What This Proves

- Kimari framework can run real inference on a consumer GTX 1060 via llama-server CUDA
- CUDA acceleration works on Pascal (compute capability 6.1) under WSL2
- Health endpoint (`/health`) responds correctly

## What This Does NOT Prove

- **NOT** a Kimari-4B result
- **NOT** a benchmark of any Kimari model
- **NOT** comparable to production benchmarks
- **NOT** a claim about model quality or kimarifit performance

## Kimari-4B Status

- Not tested
- Not published
- No weights released

## Gate

**BLOCKED** — Kimari-4B has not been tested. This result cannot be used to gate any Kimari-4B release.

---

**Date:** 2026-03-06

## Disclaimer

This is a local development validation using a test model (TinyLlama 1.1B). No public claims should be derived from this result about Kimari-4B capabilities, benchmark performance, or production readiness.
