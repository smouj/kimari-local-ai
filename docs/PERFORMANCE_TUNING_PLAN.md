# Performance Tuning Plan

> **Objective:** Move from estimation to real, reproducible local measurement.

This document defines the plan for measuring and tuning Kimari's inference performance on consumer NVIDIA GPUs. No benchmarks are claimed until they are actually measured.

## Status: Planning (no real benchmarks yet)

---

## What to Measure

| Metric | Description | Unit |
|--------|-------------|------|
| `tokens/s` | Generation throughput | tokens/second |
| `prompt_tokens/s` | Prompt processing speed | tokens/second |
| `TTFT` | Time to first token | milliseconds |
| `VRAM_used` | Peak GPU memory during inference | GiB |
| `RAM_used` | Peak system memory during inference | GiB |
| `context_tested` | Maximum context window tested | tokens |
| `batch` | Batch size used | integer |
| `ubatch` | Micro-batch size used | integer |
| `cache_type_k` | KV cache key dtype | f16/q8_0/q4_0 |
| `cache_type_v` | KV cache value dtype | f16/q8_0/q4_0 |
| `gpu_layers` | Layers offloaded to GPU | integer or "all" |
| `flash_attn` | Flash attention status | on/off/auto |
| `mmap` | Memory-mapped file loading | on/off |
| `mlock` | Lock model in RAM | on/off |
| `stability` | Server stability during test | pass/fail/oom |

---

## Target Hardware Profiles

| Profile | GPU | VRAM | Target Model Size |
|---------|-----|------|-------------------|
| `gtx1060-safe` | GTX 1060 6GB | 4.9 GiB safe | ~2.5 GiB Q4_K_M |
| `gtx1080-balanced` | GTX 1080 8GB | 6.8 GiB safe | ~4.0 GiB Q5_K_M |
| `ide-local` | Any 6GB+ | 4.9 GiB safe | ~2.5 GiB Q4_K_M |
| `agent-local` | Any 6GB+ | 4.9 GiB safe | ~2.5 GiB Q4_K_M |

---

## Benchmark Matrix

The benchmark matrix defines safe parameter combinations to test. Each combination is a "cell" that can be tested independently.

### Context Sizes

- 2048, 4096, 8192

### Batch Sizes

- 128, 256, 512

### Micro-batch Sizes

- 64, 128, 256

### Cache Types

| Combination | Key | Value | Relative Memory |
|-------------|-----|-------|----------------|
| `f16/f16` | f16 | f16 | 1.0x (baseline) |
| `q8_0/f16` | q8_0 | f16 | 0.75x |
| `q8_0/q8_0` | q8_0 | q8_0 | 0.5x |

### GPU Layers

- `all` (full offload)
- `max-safe` (calculated from VRAM budget)

### Flash Attention

- `auto` (let llama-server decide)
- `on` (if binary supports it)
- `off` (fallback)

---

## Benchmark Workflow

### 1. Dry-Run (default)

```bash
kimari benchmark --dry-run
kimari benchmark --profile gtx1060-safe --dry-run --json
kimari benchmark --matrix --dry-run --json
```

Generates a benchmark plan without executing any model. This is the safe default.

### 2. Measured Benchmark (requires running server)

```bash
# Start the server with a specific profile
kimari start --profile gtx1060-safe --daemon

# Run the benchmark
kimari benchmark --profile gtx1060-safe --measure --json

# Stop the server
kimari stop
```

> **Important:** Measured benchmarks only work with a running server. They require a real GGUF model to be loaded. Never claim benchmark results from estimation alone.

### 3. Output Format

```json
{
  "profile": "gtx1060-safe",
  "model": "TinyLlama-1.1B-Q4_K_M.gguf",
  "timestamp": "2026-05-27T12:00:00Z",
  "measurement_type": "dry_run",
  "plan": {
    "recommended_ctx": 4096,
    "recommended_batch": 256,
    "recommended_ubatch": 128,
    "recommended_cache_type_k": "q8_0",
    "recommended_cache_type_v": "q8_0",
    "estimated_vram_gb": 3.2,
    "estimated_ram_gb": 3.8
  },
  "matrix_cells": [
    {
      "ctx": 2048, "batch": 128, "ubatch": 64,
      "cache_k": "q8_0", "cache_v": "q8_0",
      "gpu_layers": "all", "flash_attn": "auto",
      "estimated_vram_gb": 2.8,
      "safe_for_profile": true
    }
  ],
  "warnings": [],
  "measured": false,
  "tokens_per_second": null,
  "ttft_ms": null
}
```

> `measured: false` and `tokens_per_second: null` indicate this is a dry-run plan, not an actual measurement. Never present dry-run output as real benchmark data.

---

## Auto-Tuning Plan

### `kimari tune --dry-run`

Recommends optimal settings based on the existing estimator. Does NOT execute benchmarks.

```bash
kimari tune --dry-run
kimari tune --profile gtx1060-safe --json
```

Output:

```json
{
  "profile": "gtx1060-safe",
  "recommendation_type": "estimated",
  "recommended": {
    "ctx": 4096,
    "batch": 256,
    "ubatch": 128,
    "cache_type_k": "q8_0",
    "cache_type_v": "q8_0",
    "gpu_layers": "all",
    "flash_attn": "auto"
  },
  "estimates": {
    "vram_gb": 3.2,
    "ram_gb": 3.8,
    "confidence": "medium"
  },
  "disclaimer": "These are estimates based on the VRAM/RAM model, not measured benchmarks. Use 'kimari benchmark --measure' for real performance data."
}
```

### `kimari tune --apply` (BLOCKED)

The `--apply` flag is intentionally **blocked** in v0.1.25. It will be enabled in a future version after measured benchmarks are validated.

```
Error: --apply is not yet available. Use --dry-run to see recommendations.
       Measured benchmark support is planned for v0.1.26-alpha.
```

---

## What We Do NOT Do

- ❌ Invent benchmark numbers
- ❌ Claim tokens/s without measuring
- ❌ Compare with other tools using fake data
- ❌ Publish benchmarks from estimation alone
- ❌ Run benchmarks in CI (no GPU available)
- ❌ Download models during benchmark planning

---

## Roadmap

| Version | Capability |
|---------|-----------|
| v0.1.25-alpha | Benchmark plan dry-run, tune dry-run (estimates only) |
| v0.1.26-alpha | Real measured benchmarks, auto-tuning experimental, `kimari doctor --deep` |
| v0.1.27-alpha | First private SFT, local adapter manifest, sanitized eval summary |

---

## See Also

- [Performance Estimation Module](../kimari/performance/) — VRAM/RAM estimation functions
- [GPU Profiles](../config/kimari.profiles.json) — Pre-configured GPU profiles
- [Benchmark Result Format](../benchmarks/RESULT_FORMAT.md) — Standardized result sharing format
- [Showcase Plan](SHOWCASE_PLAN.md) — How to present performance data honestly
