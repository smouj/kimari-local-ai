# Measured Benchmarks

> **Experimental** — Measured benchmarks are introduced in v0.1.26-alpha. The CLI interface, output format, and sanitization behavior may change before a stable release.

---

## Overview

Measured benchmarks send **real chat completion requests** to a running OpenAI-compatible local endpoint and record timing and token metrics. Unlike `kimari bench` (which uses server-side metrics from llama.cpp) and `kimari benchmark --dry-run` (which only estimates), measured benchmarks produce actual end-to-end performance numbers from the client's perspective.

The measured benchmark flow:

1. Reads standard prompts from `benchmarks/prompts/local_benchmark_prompts.jsonl`.
2. Sends each prompt as a non-streaming chat completion request to your endpoint.
3. Records wall-clock time, token usage, and tokens-per-second for each request.
4. Outputs sanitized results to the console or a JSON file.

This is the most realistic way to measure how your local model performs under typical usage conditions.

---

## How to Execute

### Step 1: Start a local server

Before running a measured benchmark, you need a running OpenAI-compatible server. Use whichever server and profile you want to test:

```bash
# Using Kimari's built-in server (default port 11435)
kimari start
kimari start --profile gtx1060

# Or use llama-server directly
llama-server -m models/qwen3-4b-q4_k_m.gguf --port 11435 -ngl all -c 8192
```

Verify the server is ready:

```bash
kimari status
```

### Step 2: Run the measured benchmark

```bash
kimari benchmark --measure --endpoint http://127.0.0.1:11435/v1 --model test --yes
```

**Required flags:**

| Flag | Purpose |
|---|---|
| `--measure` | Switches from dry-run estimation to actual measurement. Sends real HTTP requests. |
| `--endpoint` | Base URL of the OpenAI-compatible chat completions endpoint. Must include `/v1`. |
| `--model` | Model identifier passed in the request body. This is the `model` field the server uses to select the loaded model (e.g., `test`, `kimari`, or the model's alias). |
| `--yes` | **Explicit confirmation** that you want to execute a real benchmark. Without this flag, the command will refuse to run. This prevents accidental benchmark execution. |

### Step 3: Review the output

By default, results are printed to the console in a human-readable format. Use `--json` for structured output:

```bash
kimari benchmark --measure --endpoint http://127.0.0.1:11435/v1 --model test --yes --json
```

Use `--output` to save results to a file:

```bash
kimari benchmark --measure --endpoint http://127.0.0.1:11435/v1 --model test --yes --output benchmarks/results/my-test.json
```

---

## Supported Endpoints

Any server that implements the **OpenAI Chat Completions API** (`POST /v1/chat/completions`) can be used as a benchmark target. The measured benchmark module sends standard requests and reads back `usage` data from the response.

| Server | Default Port | Notes |
|---|---|---|
| **llama-server** (Kimari default) | `11435` | Primary target. Started by `kimari start`. |
| **Ollama** | `11434` | Set `--endpoint http://127.0.0.1:11434/v1`. Use the Ollama model name for `--model`. |
| **vLLM** | `8000` | Set `--endpoint http://127.0.0.1:8000/v1`. |
| **LM Studio** | `1234` | Set `--endpoint http://127.0.0.1:1234/v1`. |
| **Any OpenAI-compatible server** | varies | As long as it supports `/v1/chat/completions` with `usage` in the response. |

### Endpoint URL format

The `--endpoint` value should be the **base URL including `/v1`**:

```
http://<host>:<port>/v1
```

The benchmark appends `/chat/completions` automatically. Do **not** include `/chat/completions` in the `--endpoint` value.

---

## Do NOT Share Private Prompts

The measured benchmark uses **standard prompts only** from:

```
benchmarks/prompts/local_benchmark_prompts.jsonl
```

This file contains 8 curated, non-sensitive prompts covering categories like greeting, structured output, Python coding, bash, Spanish technical, Docker, and Linux commands. These prompts are designed to be:

- **Non-private** — They contain no personal, sensitive, or proprietary information.
- **Reproducible** — Anyone can use the same prompts to reproduce your results.
- **Diverse** — They test different types of generation (short answers, code, JSON, multilingual).

**Never use private or sensitive prompts for benchmarking.** If you need to test with your own prompts for internal purposes, do not share those results publicly. Only results using the standard prompt set should be submitted to the project.

---

## Do NOT Treat Local Measurements as Universal Benchmarks

A measured benchmark reflects **your specific hardware and configuration at a single point in time**. It is not a universal benchmark.

A single measurement is influenced by:

- **GPU model and VRAM** — Different GPUs produce different results.
- **CPU and RAM** — Affects prompt evaluation and offloading.
- **Driver and CUDA version** — Performance varies across driver releases.
- **Model and quantization** — Q4_K_M vs Q5_K_S vs F16 produce very different speeds.
- **Server configuration** — Context size, batch size, cache types, flash attention, parallelism.
- **System load** — Background processes, thermal throttling, power management.
- **llama.cpp version** — Different builds and compile flags affect performance.

### What to do instead

- **Always include hardware and configuration details** when sharing results.
- **Run multiple times** and report the median or average.
- **Use the `notes` field** to document your test conditions (thermal state, background load, etc.).
- **Compare across identical configurations** — a GTX 1060 result is only comparable to other GTX 1060 results with the same model and settings.

---

## How to Save Sanitized Results

### Saving to a file

```bash
kimari benchmark --measure \
  --endpoint http://127.0.0.1:11435/v1 \
  --model test \
  --yes \
  --output benchmarks/results/my-test.json
```

### Automatic sanitization

Results saved via `--output` are **automatically sanitized** by the `sanitize_benchmark_result()` function. The sanitization process:

1. **Removes full prompt text** — Only `prompt_preview` (first 50 characters) is retained.
2. **Removes response content** — No model output text is included in the result.
3. **Strips endpoint paths** — The endpoint is reduced to `host:port` only (e.g., `127.0.0.1:11435` instead of `http://127.0.0.1:11435/v1`).
4. **Keeps only allowed fields** — Any unexpected or extra fields are dropped.

The allowed fields in a sanitized result:

| Field | Description |
|---|---|
| `endpoint` | Host and port only (path removed) |
| `model` | Model identifier |
| `prompt_preview` | First 50 characters of the prompt |
| `max_tokens` | Maximum tokens requested |
| `prompt_tokens` | Token count from response usage |
| `completion_tokens` | Token count from response usage |
| `total_tokens` | Token count from response usage |
| `tokens_per_second` | Calculated tokens/second |
| `ttft_ms` | Time to first token (if available) |
| `elapsed_s` | Wall-clock request duration |
| `score_status` | `"measured"`, `"incomplete_response"`, or `"error"` |
| `timestamp` | When the measurement was taken |
| `error` | Error message if the request failed |

### .gitignore protection

Benchmark results in `benchmarks/results/` are **.gitignored by default**:

```gitignore
benchmarks/results/*.json
benchmarks/results/*.csv
```

This prevents accidental commits of benchmark data. If you want to share a result, use the GitHub issue process described below.

---

## How to Share

Share your sanitized benchmark results by opening a GitHub issue using the **`performance_report.yml`** issue template.

### Step-by-step sharing process

1. **Run the measured benchmark** and save the output:
   ```bash
   kimari benchmark --measure \
     --endpoint http://127.0.0.1:11435/v1 \
     --model test \
     --yes \
     --output benchmarks/results/my-gtx1060.json
   ```

2. **Review the output file** and verify it contains no private data (the automatic sanitization should handle this, but always double-check).

3. **Add hardware and configuration context.** At minimum, include:
   - GPU model and VRAM
   - Driver version
   - CUDA version
   - OS and kernel version
   - CPU and RAM (optional but helpful)
   - Model filename and quantization
   - Server configuration (ctx, batch, ubatch, cache types, flash attention)

4. **Open a GitHub issue:**
   - Go to the Kimari Local AI repository → **Issues** → **New Issue**.
   - Select the **`performance_report`** template.
   - Paste your sanitized JSON result.
   - Include the hardware and config details.

5. **Use the standard issue title format:**
   ```
   [BENCH] <GPU model> — <model> — <tokens/s> t/s
   ```
   Example:
   ```
   [BENCH] GTX 1060 6GB — Qwen3-4B-Q4_K_M — 15.2 t/s
   ```

---

## Security Notes

Measured benchmarks involve sending HTTP requests to local endpoints and recording responses. Follow these security guidelines:

### Never include tokens in benchmark results

- Do not include API keys, Bearer tokens, or auth tokens.
- Do not include the output of `kimari token show` in any shared result.
- The sanitization process strips unknown fields, but always verify manually.

### Never share full prompt/response content

- The standard prompt set in `local_benchmark_prompts.jsonl` is non-sensitive by design.
- The `sanitize_benchmark_result()` function removes full prompt text and response content.
- Never manually add prompt text or model output to a shared result JSON.

### Never share private paths

- Full filesystem paths can reveal usernames and directory structures.
- The sanitization process reduces endpoints to `host:port` only.
- In the `notes` field, use only filenames or `~/` paths — never absolute paths like `/home/yourname/...` or `C:\Users\YourName\...`.

### Pre-submission security checklist

Before sharing any benchmark result, verify:

1. ✅ No API keys, tokens, or credentials are present
2. ✅ No full prompt text or model output is included
3. ✅ No real filesystem paths (only filenames or `~/` relative paths)
4. ✅ No usernames, hostnames, or IP addresses appear
5. ✅ The `notes` field contains only performance-relevant information
6. ✅ The `endpoint` field shows only `host:port` (no full URL)

### Additional security considerations

- **Local endpoints only.** Measured benchmarks are designed for local servers (`127.0.0.1` or `localhost`). Do not point `--endpoint` at remote or public servers.
- **No authentication.** The benchmark does not send authentication headers. If your endpoint requires auth, the benchmark will fail with a connection or authorization error.
- **Network isolation.** Run benchmarks in a trusted network environment. The benchmark sends prompt text over HTTP (not HTTPS) to local endpoints.

---

## Measured vs. Other Benchmark Modes

| Feature | `kimari bench` | `kimari benchmark --dry-run` | `kimari benchmark --measure` |
|---|---|---|---|
| Type | Server-side metrics | Estimation | Client-side measurement |
| Requires running server | Yes (for real data) | No | Yes |
| Sends HTTP requests | No | No | Yes |
| Uses standard prompts | No | No | Yes (from `local_benchmark_prompts.jsonl`) |
| Tokens/second source | llama.cpp output | Estimated | Real HTTP response |
| TTFT measurement | From llama.cpp | N/A | From request timing |
| Configuration | Profile-based | Profile-based | Endpoint + model flags |
| Safety confirmation | No | No | `--yes` required |
| Result sanitization | Manual | N/A | Automatic |

---

## Troubleshooting

### "Connection refused" error

The endpoint is not reachable. Ensure:
- The server is running: `kimari status`
- The port is correct (Kimari default: 11435, Ollama: 11434)
- The `--endpoint` URL includes `/v1` (e.g., `http://127.0.0.1:11435/v1`)

### "Response lacks usage information" error

The server did not return token usage data. This happens when:
- The server does not support the `usage` field in chat completions responses
- The server is configured to omit usage data
- The request timed out or returned an error

### "--yes flag is required" error

The `--yes` flag is a safety measure. Add it to confirm you want to execute real benchmark requests:

```bash
kimari benchmark --measure --endpoint ... --model ... --yes
```

### Inconsistent results between runs

This is normal. Local inference performance varies based on:
- System load and background processes
- GPU thermal state (throttling)
- Memory fragmentation and garbage collection
- OS scheduling

For the most consistent results:
1. Start the server fresh before each benchmark run
2. Close other GPU-intensive applications
3. Run 3-5 times and report the median
4. Document any anomalies in the `notes` field

---

*Measured benchmarks are part of Kimari Local AI v0.1.26-alpha. The command interface and output format are experimental and may change before a stable release. Feedback is welcome via GitHub issues.*
