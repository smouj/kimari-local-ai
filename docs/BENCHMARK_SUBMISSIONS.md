# Benchmark Submissions

This guide explains how to run benchmarks, export results, sanitize them for privacy, and submit them to the Kimari project.

Community benchmark results help improve default profiles and KimariFit scores for everyone. Thank you for contributing!

---

## Running a Benchmark

### 1. Start the Server

Start the Kimari server with the profile you want to benchmark:

```bash
kimari start --profile gtx1060
```

Or use the default profile:

```bash
kimari start
```

Wait for the server to be ready before benchmarking:

```bash
kimari status
```

### 2. Run the Benchmark

```bash
kimari perf --profile gtx1060
```

This runs a performance benchmark against the active server and displays the results.

### 3. Export the Result

To produce a structured JSON result file:

```bash
kimari perf --profile gtx1060 --json
```

To save to a specific file:

```bash
kimari perf --profile gtx1060 --json --output benchmarks/results/gtx1060-$(date +%Y%m%d).json
```

Without `--output`, results are auto-saved to `benchmarks/results/<profile>-<YYYYMMDD-HHMMSS>.json`.

---

## Anonymizing Paths

**Before sharing any benchmark result, you must sanitize local paths.** Replace any real filesystem paths with anonymized equivalents.

### Path Replacement Rules

| Real Path | Replace With |
|---|---|
| `/home/yourname/` | `~/` |
| `/home/user/` | `~/` |
| `C:\Users\YourName\` | `~/` |
| `/Users/yourname/` | `~/` |
| Any full absolute path | Relative or `~/` equivalent |

### Example

Before sanitization:
```json
{
  "notes": "Model at /home/alice/.local/share/kimari/models/qwen3-4b-q4_k_m.gguf"
}
```

After sanitization:
```json
{
  "notes": "Model at ~/.local/share/kimari/models/qwen3-4b-q4_k_m.gguf"
}
```

Or even better, use only the filename:
```json
{
  "notes": "Model: qwen3-4b-q4_k_m.gguf"
}
```

---

## Opening a Performance Report Issue

Share your benchmark results by opening a GitHub issue:

1. Go to the Kimari Local AI GitHub repository.
2. Click **Issues** → **New Issue**.
3. Select the **`performance_report`** template/label.
4. Paste your sanitized benchmark JSON into the issue body.
5. Include hardware context in the issue description:
   - GPU model and VRAM
   - Driver version
   - CUDA version
   - OS and kernel version
   - CPU and RAM (optional but helpful)

### Issue Title Format

```
[BENCH] <GPU model> — <model> — <tokens/s> t/s
```

Example:
```
[BENCH] GTX 1060 6GB — Qwen3-4B-Q4_K_M — 15.2 t/s
```

---

## What NOT to Share

**Never include the following in a shared benchmark result:**

| Category | Examples | Why |
|---|---|---|
| **API keys / tokens** | Bearer tokens, API keys, `kimari token show` output | Security risk |
| **Private prompts** | Actual prompt text, model outputs, conversation content | Privacy |
| **Real filesystem paths** | `/home/yourname/`, `C:\Users\YourName\` | Identifying |
| **Usernames / hostnames** | Shell prompts, hostnames in paths | Identifying |
| **IP addresses** | Local or public IPs | Identifying / security |
| **Environment variables with secrets** | `HF_TOKEN`, `OPENAI_API_KEY`, etc. | Security |

### Pre-submission Checklist

Before sharing, verify:

1. ✅ All file paths are relative or use `~/` (no real usernames)
2. ✅ No prompts or model outputs are included
3. ✅ No tokens, keys, or credentials are present
4. ✅ No hostnames, IP addresses, or usernames appear
5. ✅ The `notes` field contains only performance-relevant context
6. ✅ The `model_filename` field contains only the filename (no directory path)

---

## Required Format

All shared benchmark results must conform to the format defined in [benchmarks/RESULT_FORMAT.md](../benchmarks/RESULT_FORMAT.md).

### Required Fields

| Field | Type | Description |
|---|---|---|
| `kimari_version` | `string` | Kimari release version (e.g. `"0.1.16-alpha"`) |
| `profile` | `string` | Active GPU profile name |
| `model_filename` | `string` | GGUF model filename only — **no directory path** |
| `gpu` | `string \| null` | Full GPU name. `null` if no GPU. |
| `os` | `string` | Operating system and kernel/version |
| `python` | `string` | Python version |
| `tokens_per_second` | `float \| null` | Average generation speed |
| `ttft_ms` | `float \| null` | Time to first token in milliseconds |
| `timestamp` | `string` | ISO 8601 datetime of the benchmark run |
| `notes` | `string` | Free-text context (performance-relevant only) |

### Optional but Helpful Fields

| Field | Type | Description |
|---|---|---|
| `model_sha256` | `string \| null` | SHA-256 hash of the model file |
| `quantization` | `string \| null` | Quantization method |
| `driver` | `string \| null` | GPU driver version |
| `cuda` | `string \| null` | CUDA runtime version |
| `ctx` | `integer \| null` | Context window size |
| `batch` | `integer \| null` | Batch size |
| `ubatch` | `integer \| null` | Micro-batch size |
| `cache_type_k` | `string \| null` | KV cache type for keys |
| `cache_type_v` | `string \| null` | KV cache type for values |
| `flash_attn` | `boolean \| null` | Whether flash attention was enabled |
| `parallel` | `integer \| null` | Number of parallel sequences |
| `prompt_tokens_per_second` | `float \| null` | Prompt evaluation speed |
| `vram_used_gb` | `float \| null` | VRAM usage in GiB |
| `ram_used_gb` | `float \| null` | RAM usage in GiB |

### Example Files

See the `benchmarks/examples/` directory for complete example results:

- `perf-result.gtx1060.example.json` — GTX 1060 6GB example
- `perf-result.gtx1080.example.json` — GTX 1080 8GB example
- `perf-result.example.json` — Generic example

---

## Criteria for Accepting Community Benchmarks

A community benchmark submission will be accepted if it meets **all** of the following criteria:

### 1. Valid Format

- The result JSON conforms to the schema in [benchmarks/RESULT_FORMAT.md](../benchmarks/RESULT_FORMAT.md).
- All required fields are present and have the correct types.
- The `model_filename` field is a filename only (no paths).

### 2. Privacy Clean

- No private prompts, model outputs, tokens, API keys, or Bearer tokens.
- No real filesystem paths (must use `~/` or filename-only).
- No usernames, hostnames, or IP addresses.
- The `notes` field contains only performance-relevant information.

### 3. Reproducible

- The GPU model, driver version, and CUDA version are specified.
- The OS and Python version are specified.
- The Kimari version is specified.
- The profile name and model filename are specified.
- Server parameters (ctx, batch, ubatch, etc.) are included or inferable from the profile.

### 4. Realistic Values

- `tokens_per_second` and `ttft_ms` values are realistic for the claimed hardware.
- Values are not obviously fabricated (e.g., 999999 t/s is not realistic).
- The benchmark was run on an actual system, not invented.

### 5. No Model File Included

- The submission does not include or link to a `.gguf` model file.
- Only the filename and optionally the SHA-256 hash are included.

### 6. License-Compatible

- If the model's license is mentioned, it must not restrict sharing benchmark metadata.
- Benchmark metadata (speeds, hardware info) is not subject to model licenses, but the submitter should be aware of the model's terms.

---

## Tips for Consistent Results

- **Start the server fresh** before benchmarking — don't reuse a long-running instance.
- **Close other GPU-intensive applications** (games, other AI tools, etc.).
- **Run on a stable system** — no background updates, no thermal throttling.
- **Record ambient conditions** in the `notes` field if relevant (e.g., "thermal throttling observed after 5 minutes").
- **Run multiple times** and report the median or average if possible.
- **Use the same model and profile** when comparing across hardware.

---

*Community benchmarks are part of Kimari Local AI v0.1.16-alpha. The submission format and criteria may evolve before a stable release.*
