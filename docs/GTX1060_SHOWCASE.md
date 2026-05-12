# GTX 1060 Local Showcase

> **Validated on real consumer hardware** — NVIDIA GeForce GTX 1060 6GB, WSL2 Ubuntu 24.04.

This document describes what Kimari Local AI demonstrates on the GTX 1060, what it does **not** demonstrate, and how to reproduce the results.

## Hardware

| Component | Value |
|-----------|-------|
| GPU | NVIDIA GeForce GTX 1060 6GB |
| VRAM | 6144 MiB |
| Driver | 581.57 (WSL2 passthrough) |
| CUDA | 12.0, compute capability 6.1 |
| OS | WSL2 Ubuntu 24.04 |
| CPU | (varies — benchmarks include CPU-only for comparison) |

## Software Stack

| Component | Version |
|-----------|---------|
| Kimari Local AI | 0.1.44-alpha |
| llama-server | v1 (706fbd8), CUDA build for compute_61 |
| Python | 3.12.3 |
| Model | TinyLlama 1.1B Q4_K_M (638MB) |

> **Important:** The model tested is **TinyLlama 1.1B Q4_K_M**, a general-purpose test model. **Kimari-4B is not yet released.** No weights, adapters, or GGUF files are available.

## Local Endpoint

Kimari exposes an OpenAI-compatible endpoint at `http://127.0.0.1:11435/v1`:

| Endpoint | Status |
|----------|--------|
| `/health` | ✅ `{"status":"ok"}` |
| `/v1/models` | ✅ Lists TinyLlama |
| `/v1/chat/completions` | ✅ Returns responses |

## Benchmark Results

| Metric | CUDA (GTX 1060) | CPU-only | Speedup |
|--------|-----------------|----------|---------|
| Prompt processing | 228 tok/s | 77 tok/s | 3.0× |
| Token generation | 73 tok/s | 33 tok/s | 2.2× |
| VRAM usage | 1221 MiB | — | — |
| Model | TinyLlama 1.1B Q4_K_M | TinyLlama 1.1B Q4_K_M | — |

## Local Integrations Validated

| Tool | Status |
|------|--------|
| curl / OpenAI SDK | ✅ Validated |
| Open WebUI | ✅ Config documented |
| OpenClaw | ✅ Config documented |
| Continue.dev | ✅ Config documented |

See [LOCAL_INTEGRATION_VALIDATION.md](LOCAL_INTEGRATION_VALIDATION.md) for setup guides.

## What This Demonstrates

✅ Kimari runs on consumer-grade hardware (GTX 1060, released 2016)
✅ CUDA acceleration works correctly in WSL2
✅ OpenAI-compatible endpoint is functional
✅ Integration with popular local AI tools is possible
✅ The framework detects and uses GPU correctly

## What This Does NOT Demonstrate

❌ Kimari-4B model performance (model not yet released)
❌ Production-grade inference speed (TinyLlama is small)
❌ Multi-user or concurrent request handling
❌ Fine-tuning or training capabilities
❌ Any benchmark claims about Kimari-4B

## Reproducing the Results

```bash
# 1. Start with test profile
kimari start --profile test

# 2. Validate endpoint
python scripts/integrations/validate_local_openai_endpoint.py --base-url http://127.0.0.1:11435/v1 --json

# 3. Generate integration configs
kimari integrations generate --all --json --profile test

# 4. Stop
kimari stop
```

## Gate Status

**BLOCKED** — Kimari is in alpha. No weights, no public releases, no training performed.

## See Also

- [LOCAL_OPENAI_ENDPOINT_TEST.md](LOCAL_OPENAI_ENDPOINT_TEST.md) — Endpoint testing guide
- [LOCAL_INTEGRATION_VALIDATION.md](LOCAL_INTEGRATION_VALIDATION.md) — Integration setup guides
- [GTX1060_LOCAL_RUNTIME_RESULT.md](GTX1060_LOCAL_RUNTIME_RESULT.md) — Detailed runtime validation
- [LOCAL_SHOWCASE_CHECKLIST.md](LOCAL_SHOWCASE_CHECKLIST.md) — Screenshot checklist

## Public Screenshot Status

| Capture | Status | File |
|---------|--------|------|
| `nvidia-smi` | ⏳ Pending | `nvidia-smi.png` |
| `kimari doctor --deep` | ⏳ Pending | `kimari-doctor.png` |
| `kimari status` | ⏳ Pending | `kimari-status.png` |
| `llama-server CUDA startup` | ⏳ Pending | `llama-server-cuda.png` |
| `/health` endpoint | ⏳ Pending | `endpoint-health.png` |
| `/v1/models` | ⏳ Pending | `endpoint-models.png` |
| `/v1/chat/completions` | ⏳ Pending | `endpoint-chat.png` |
| `kimari integrations generate` | ⏳ Pending | `integrations-generate.png` |

> **Note**: No real screenshots committed yet. Only `manifest.example.json` template exists. Real captures require manual review per [LOCAL_SHOWCASE_CHECKLIST.md](LOCAL_SHOWCASE_CHECKLIST.md) before publishing.
>
> All captures show **TinyLlama 1.1B Q4_K_M** (test model), NOT Kimari-4B.