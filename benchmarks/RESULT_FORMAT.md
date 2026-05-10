# Benchmark Result Sharing Format

This document defines the JSON format for **sharing** benchmark results publicly (e.g. GitHub issues, community reports). It extends the internal schema with additional fields for reproducibility and privacy considerations.

See [SCHEMA.md](./SCHEMA.md) for the full internal schema produced by `kimari bench`.

---

## Shared Result JSON Structure

When sharing benchmark results, use the following JSON structure:

```json
{
  "kimari_version": "0.1.15-alpha",
  "profile": "gtx1060",
  "model_filename": "qwen3-4b-q4_k_m.gguf",
  "model_sha256": "a1b2c3d4e5f6...",
  "quantization": "Q4_K_M",

  "gpu": "NVIDIA GeForce GTX 1060 6GB",
  "driver": "550.54.14",
  "cuda": "12.4",
  "os": "Linux 5.15.0",
  "python": "3.12.3",

  "ctx": 8192,
  "batch": 256,
  "ubatch": 128,
  "cache_type_k": "f16",
  "cache_type_v": "f16",
  "flash_attn": true,
  "parallel": 4,

  "tokens_per_second": 15.2,
  "prompt_tokens_per_second": 320.5,
  "ttft_ms": 850.0,

  "vram_used_gb": 4.8,
  "ram_used_gb": 2.1,

  "timestamp": "2025-06-15T14:30:00Z",
  "notes": "Stable run, no thermal throttling observed"
}
```

### Field Reference

#### Software & Version

| Field | Type | Required | Description |
|---|---|---|---|
| `kimari_version` | `string` | Yes | Kimari release version (e.g. `"0.1.15-alpha"`) |
| `profile` | `string` | Yes | Active GPU profile name (e.g. `"gtx1060"`, `"gtx1080"`) |
| `model_filename` | `string` | Yes | GGUF model filename only — **no directory path** (e.g. `"qwen3-4b-q4_k_m.gguf"`) |
| `model_sha256` | `string \| null` | No | SHA-256 hash of the model file. Omit if unknown. |
| `quantization` | `string \| null` | No | Quantization method (e.g. `"Q4_K_M"`, `"Q5_K_S"`) |

#### Hardware & Environment

| Field | Type | Required | Description |
|---|---|---|---|
| `gpu` | `string \| null` | Yes | Full GPU name. `null` if no GPU detected. |
| `driver` | `string \| null` | No | GPU driver version. `null` if not available. |
| `cuda` | `string \| null` | No | CUDA runtime version. `null` if not available. |
| `os` | `string` | Yes | Operating system and kernel/version (e.g. `"Linux 5.15.0"`, `"Windows 11"`) |
| `python` | `string` | Yes | Python version (e.g. `"3.12.3"`) |

#### Server Parameters

| Field | Type | Required | Description |
|---|---|---|---|
| `ctx` | `integer \| null` | No | Context window size |
| `batch` | `integer \| null` | No | Batch size |
| `ubatch` | `integer \| null` | No | Micro-batch size |
| `cache_type_k` | `string \| null` | No | KV cache type for keys (e.g. `"f16"`, `"q8_0"`, `"q4_0"`) |
| `cache_type_v` | `string \| null` | No | KV cache type for values |
| `flash_attn` | `boolean \| null` | No | Whether flash attention was enabled |
| `parallel` | `integer \| null` | No | Number of parallel sequences |

#### Performance Metrics

| Field | Type | Required | Description |
|---|---|---|---|
| `tokens_per_second` | `float \| null` | Yes | Average generation speed (tokens/sec). `null` if all prompts failed. |
| `prompt_tokens_per_second` | `float \| null` | No | Prompt evaluation speed (tokens/sec). `null` if not measured. |
| `ttft_ms` | `float \| null` | Yes | Time to first token in milliseconds. `null` if unavailable. |

#### Resource Usage

| Field | Type | Required | Description |
|---|---|---|---|
| `vram_used_gb` | `float \| null` | No | VRAM usage in GiB during benchmark. `null` if not measured. |
| `ram_used_gb` | `float \| null` | No | RAM usage in GiB during benchmark. `null` if not measured. |

#### Metadata

| Field | Type | Required | Description |
|---|---|---|---|
| `timestamp` | `string` | Yes | ISO 8601 datetime of the benchmark run |
| `notes` | `string` | Yes | Free-text context (thermal conditions, hardware details, etc.) |

---

## Privacy

**Before sharing any benchmark result, you must sanitize the data.**

### What NOT to include

- **No private prompts.** The sharing format does not include prompt text or response content. If you add a `notes` field, do not paste actual prompts or model outputs.
- **No sensitive local paths.** Use only filenames, not full filesystem paths. For example:
  - ✅ `"model_filename": "qwen3-4b-q4_k_m.gguf"`
  - ❌ `"model_filename": "/home/user/.kimari/models/qwen3-4b-q4_k_m.gguf"`
- **No auth tokens.** Never include API keys, Bearer tokens, or any authentication credentials in shared results.
- **No personally identifying information.** Do not include usernames, hostnames, IP addresses, or any data that could identify you.

### Sanitization checklist

Before sharing, verify:

1. All file paths are relative or filename-only
2. No prompts or model outputs are included
3. No tokens, keys, or credentials are present
4. No hostnames, IP addresses, or usernames appear
5. The `notes` field contains only performance-relevant context

---

## How to Share

Share benchmark results by opening a GitHub issue using the **`performance_report`** template:

1. Run your benchmark:
   ```bash
   kimari start --profile gtx1060
   kimari bench --profile gtx1060 --json
   ```

2. Transform the output into the sharing format (or use the example file in `benchmarks/examples/perf-result.example.json` as a template).

3. **Sanitize** the result using the checklist above.

4. Open a new issue on GitHub with the **`performance_report`** label and paste your JSON result.

5. Include hardware context in the issue body (GPU model, VRAM, driver version, OS).

Community benchmark results help improve default profiles and KimariFit scores for everyone. Thank you for contributing!
