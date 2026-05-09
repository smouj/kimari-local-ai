# Benchmark Result JSON Schema

This document defines the standardized JSON schema for `kimari bench` results. All benchmark result files **must** conform to this schema.

## Schema Definition

| Field | Type | Required | Description |
|---|---|---|---|
| `date` | `string` | Yes | ISO 8601 datetime of the benchmark run (`YYYY-MM-DDTHH:MM:SS`). Auto-populated. |
| `kimari_version` | `string` | Yes | Kimari release version (e.g. `"0.1.4-alpha"`). Auto-populated. |
| `os` | `string` | Yes | Operating system and kernel version (e.g. `"Linux 5.10.0"`). Auto-populated. |
| `gpu_name` | `string \| null` | Yes | Full NVIDIA GPU name (e.g. `"NVIDIA GeForce GTX 1060 6GB"`). `null` if no GPU detected. |
| `vram_total_mb` | `integer \| null` | Yes | Total VRAM in megabytes (e.g. `6144`). `null` if no GPU detected. |
| `driver_version` | `string \| null` | Yes | NVIDIA driver version (e.g. `"535.104.05"`). `null` if no GPU detected. |
| `cuda_version` | `string \| null` | Yes | CUDA runtime version (e.g. `"12.4"`). `null` if CUDA is not installed. |
| `model_name` | `string` | Yes | Model identifier derived from the model file stem (e.g. `"Kimari-4B-Q4_K_M"`). |
| `model_size_gb` | `float \| null` | No | Estimated model size in gigabytes (e.g. `3.1`). `null` if not set in profile. |
| `quantization` | `string \| null` | No | Quantization method (e.g. `"Q4_K_M"`). `null` if not set in profile. |
| `ctx` | `integer \| null` | No | Context window size (e.g. `8192`). `null` if not set in profile. |
| `batch` | `integer \| null` | No | Batch size (e.g. `256`). `null` if not set in profile. |
| `ubatch` | `integer \| null` | No | Micro-batch size (e.g. `128`). `null` if not set in profile. |
| `prompt_tokens` | `integer \| null` | Yes | Number of tokens in the input prompt. Always `null` — the CLI cannot count prompt tokens from the API response. |
| `generated_tokens` | `integer \| null` | Yes | Total completion tokens across all benchmark prompts. `null` if all prompts failed. |
| `tokens_per_second` | `float \| null` | Yes | Average generation speed across successful prompts (e.g. `15.2`). `null` if all prompts failed. |
| `time_to_first_token_ms` | `float \| null` | Yes | Average time from request to first streamed token, in milliseconds (e.g. `850.0`). `null` if streaming was unavailable or all prompts failed. |
| `peak_vram_mb` | `integer \| null` | Yes | Peak VRAM usage in megabytes. Always `null` — cannot be measured from the CLI currently (requires `nvidia-smi` polling or llama.cpp internal reporting). |
| `notes` | `string` | Yes | Free-text description or context (e.g. `"Automated benchmark via 'kimari bench'"`). |

### Nullable Fields Summary

Several fields may be `null` for different reasons:

| Field | Reason for `null` |
|---|---|
| `gpu_name`, `vram_total_mb`, `driver_version` | No NVIDIA GPU detected on the system. |
| `cuda_version` | CUDA toolkit not installed or not on `PATH`. |
| `model_size_gb`, `quantization` | Not configured in the active profile. |
| `ctx`, `batch`, `ubatch` | Not configured in the active profile. |
| `prompt_tokens` | **Always `null`.** The CLI sends prompts via the API and cannot retrieve the exact prompt token count from llama.cpp's response. |
| `peak_vram_mb` | **Always `null`.** The CLI currently has no mechanism to poll VRAM usage during inference. Future versions may integrate `nvidia-smi` sampling or llama.cpp metrics. |
| `generated_tokens`, `tokens_per_second`, `time_to_first_token_ms` | All benchmark prompts failed (server error, timeout, etc.). |

## Example Result

```json
{
  "date": "2025-05-09T12:00:00",
  "kimari_version": "0.1.4-alpha",
  "os": "Linux 5.10.0",
  "gpu_name": "NVIDIA GeForce GTX 1060 6GB",
  "vram_total_mb": 6144,
  "driver_version": "535.104.05",
  "cuda_version": "12.4",
  "model_name": "Kimari-4B-Q4_K_M",
  "model_size_gb": 3.1,
  "quantization": "Q4_K_M",
  "ctx": 8192,
  "batch": 256,
  "ubatch": 128,
  "prompt_tokens": null,
  "generated_tokens": 1500,
  "tokens_per_second": 15.2,
  "time_to_first_token_ms": 850.0,
  "peak_vram_mb": null,
  "notes": "Automated benchmark via 'kimari bench'"
}
```

## Reproducing Benchmarks

1. **Start the server** with the profile you want to benchmark:
   ```bash
   kimari start                    # Default profile (test)
   kimari start --profile gtx1060  # Specific profile
   ```

2. **Run the benchmark** with `--json` and `--output` to produce a standardized result file:
   ```bash
   kimari bench --profile gtx1060 --json --output benchmarks/results/gtx1060-20250509.json
   ```

3. Without `--output`, results are auto-saved to `benchmarks/results/<profile>-<YYYYMMDD-HHMMSS>.json`.

### Tips for Consistent Results

- Start the server fresh before benchmarking — don't reuse a long-running instance.
- Close other GPU-intensive applications.
- Run on a stable system (no background updates, no thermal throttling).
- Record ambient conditions in the `notes` field if relevant (e.g. thermal throttling observed).

## Contributing Benchmark Results

Community benchmark results are welcome! To contribute:

1. **Run the benchmark** as described above on your hardware.
2. **Rename the result file** to follow the naming convention: `<profile>-<date>.json`
   - Example: `gtx1060-20250509.json`
   - The profile name should match your GPU or hardware configuration.
   - Date format: `YYYYMMDD`.
3. **Place the file** in `benchmarks/results/`.
4. **Validate** the JSON against this schema — all required fields must be present.
5. **Submit a pull request** with the result file.

Alternatively, you can start from a template in `benchmarks/templates/` and fill in your measured values manually.

## File Naming Convention

Result files are stored in `benchmarks/results/` using the pattern:

```
<profile>-<date>.json
```

- `<profile>`: lowercase GPU profile name (e.g. `gtx1060`, `gtx1080`, `rtx3060`)
- `<date>`: `YYYYMMDD` or `YYYYMMDD-HHMMSS` for auto-saved files

Examples:
- `benchmarks/results/gtx1060-20250509.json`
- `benchmarks/results/gtx1080-20250509-143000.json`

## Templates

Pre-filled example templates are available in `benchmarks/templates/`:

- `gtx1060-result.example.json` — GTX 1060 6GB template
- `gtx1080-result.example.json` — GTX 1080 8GB template

Use these as a starting point when manually recording benchmark results.
