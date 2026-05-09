# KimariFit Formula

## Document: 00-02 KimariFit Scoring Formula
**Version:** 0.1.0
**Status:** Draft
**Last Updated:** 2025

---

## Overview

KimariFit is a scoring system that predicts how well a given model configuration will perform on your specific hardware. It answers the question: *"Will this model run well on my GPU?"*

The score ranges from **0 to 100**, where higher is better. It takes into account VRAM utilization, quantization quality, context window size, and estimated throughput.

## Score Interpretation

| Score Range | Rating | Meaning |
|-------------|--------|---------|
| **90–100** | Optimal | Model fits perfectly. Expect best performance. |
| **70–89** | Good | Minor compromises. Should work well for most tasks. |
| **50–69** | Usable | Significant quantization or reduced context. Acceptable for basic use. |
| **30–49** | Poor | Likely to be slow or may OOM. Not recommended for regular use. |
| **0–29** | Not Recommended | Will not fit in VRAM or will be unusably slow. |

## Formula

### VRAM Estimation

The total VRAM needed is estimated as:

```
VRAM_total = VRAM_model × 1.15 + VRAM_kv_cache + 0.5 GB
```

Where:
- `VRAM_model` = Model file size in GB (from the GGUF file, or estimated from parameter count and quantization)
- `1.15` = ~15% overhead factor for CUDA runtime
- `VRAM_kv_cache` = KV cache size based on context length
- `0.5 GB` = Safety buffer for CUDA context and other overhead

### KV Cache Estimation

The KV cache size depends on context length, number of layers, and hidden dimension:

```
VRAM_kv_cache = (2 × n_layers × hidden_dim × 2 × ctx_size) / (1024³)
```

For a typical 4B parameter model:
- `n_layers` ≈ 32
- `hidden_dim` ≈ 2560
- Factor of 2 = key + value
- Factor of 2 = bytes per element (f16)

### Quantization Bytes per Parameter

| Quantization | Bytes/Param | Relative Quality |
|-------------|-------------|-----------------|
| Q2_K | 2.5 | Low |
| Q3_K_S | 3.0 | Low-Medium |
| Q3_K_M | 3.5 | Medium |
| Q3_K_L | 3.8 | Medium |
| Q4_0 | 4.0 | Medium |
| Q4_K_S | 4.0 | Medium |
| **Q4_K_M** | **4.5** | **Good (recommended)** |
| Q5_0 | 5.0 | Good |
| Q5_K_S | 5.0 | Good |
| **Q5_K_M** | **5.5** | **Very Good** |
| Q6_K | 6.5 | Excellent |
| Q8_0 | 8.0 | Near-lossless |
| IQ4_XS | 3.8 | Medium (efficient) |

### Utilization Score

The base score is calculated from VRAM utilization:

```
utilization = VRAM_total / (VRAM_safe × 100)
```

Where `VRAM_safe = VRAM_total_gpu × 0.90` (use 90% of available VRAM).

```
base_score:
  if utilization ≤ 0.95:  95
  if utilization ≤ 1.05:  80 - (utilization - 0.95) × 400
  if utilization ≤ 1.15:  40 - (utilization - 1.05) × 300
  otherwise:               10
```

### Quality Adjustment

An adjustment is added based on quantization quality:

| Quantization | Adjustment |
|-------------|------------|
| Q2_K | -15 |
| Q3_K_S | -8 |
| Q3_K_M | -5 |
| Q3_K_L | -3 |
| Q4_0 | 0 |
| Q4_K_S | 0 |
| Q4_K_M | +2 |
| Q5_0 | +3 |
| Q5_K_S | +3 |
| Q5_K_M | +5 |
| Q6_K | +5 |
| Q8_0 | +5 |
| IQ4_XS | -3 |

### Context Bonus

| Context Size | Adjustment |
|-------------|------------|
| < 4,096 | -5 |
| 4,096–8,191 | 0 |
| 8,192–16,383 | +3 |
| ≥ 16,384 | +3 |

### Final Score

```
kimarifit = clamp(base_score + quality_adjustment + context_bonus, 0, 100)
```

## Practical Examples

### Example 1: GTX 1060, Kimari-4B-Q4_K_M, ctx=8192

```
Model size:      4B params × 4.5 bytes = 2.25 GB
VRAM_model:      2.25 × 1.15 = 2.59 GB
KV cache:        ~1.0 GB
VRAM_total:      2.59 + 1.0 + 0.5 = 4.09 GB
VRAM_safe:       6.0 × 0.90 = 5.40 GB
Utilization:     4.09 / 5.40 = 75.7%
Base score:      95
Quality adj:     +2 (Q4_K_M)
Context adj:     0 (8192)
KimariFit:       97 → OPTIMAL
```

### Example 2: GTX 1060, Kimari-4B-Q5_K_M, ctx=16384

```
Model size:      4B params × 5.5 bytes = 2.75 GB
VRAM_model:      2.75 × 1.15 = 3.16 GB
KV cache:        ~2.0 GB
VRAM_total:      3.16 + 2.0 + 0.5 = 5.66 GB
VRAM_safe:       6.0 × 0.90 = 5.40 GB
Utilization:     5.66 / 5.40 = 104.8%
Base score:      80 - (104.8 - 95) × 400 / 100 = 80 - 39.2 = 40.8
Quality adj:     +5 (Q5_K_M)
Context adj:     +3 (16384)
KimariFit:       48.8 → POOR (will likely OOM)
```

### Example 3: GTX 1080, Kimari-4B-Q5_K_M, ctx=16384

```
Model size:      4B params × 5.5 bytes = 2.75 GB
VRAM_model:      2.75 × 1.15 = 3.16 GB
KV cache:        ~2.0 GB
VRAM_total:      3.16 + 2.0 + 0.5 = 5.66 GB
VRAM_safe:       8.0 × 0.90 = 7.20 GB
Utilization:     5.66 / 7.20 = 78.6%
Base score:      95
Quality adj:     +5 (Q5_K_M)
Context adj:     +3 (16384)
KimariFit:       100 → OPTIMAL
```

## Using KimariFit from CLI

```bash
cd cli

# Calculate score for a specific model and context
python kimari_cli.py fit --model models/Kimari-4B-Q4_K_M.gguf --ctx 8192

# Specify VRAM manually (if GPU not detected)
python kimari_cli.py fit --model models/Kimari-4B-Q4_K_M.gguf --ctx 8192 --vram 6.0
```

## Limitations

1. **Estimates, not guarantees** — Actual VRAM usage may vary due to fragmentation
2. **Model-specific** — Assumes typical transformer architecture; custom architectures may differ
3. **Throughput not measured** — KimariFit predicts fit, not speed (use `kimari bench` for that)
4. **Single GPU** — Does not account for multi-GPU setups

## Future Improvements

- Actual VRAM measurement via CUDA API
- Multi-GPU scoring
- Temperature / power limit considerations
- Memory fragmentation modeling
- Machine learning-based prediction from real benchmarks

---

*This formula will be refined based on empirical benchmarking data.*
