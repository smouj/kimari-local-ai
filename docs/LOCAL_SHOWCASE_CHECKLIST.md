# Local Showcase Checklist

> **Checklist for preparing public screenshots and demonstrations of Kimari Local AI.**

## ⚠️ Safety Rules

1. **No secrets** — API keys, tokens, local paths, or user names must not appear
2. **No real training outputs** — Loss curves, adapter weights, and raw eval outputs stay local
3. **No real benchmarks** — Benchmark claims require measured, reviewed data
4. **Kimari-4B not released** — Screenshots must not imply the model is available
5. **No real screenshots without review** — Do not commit screenshot images until they have been manually reviewed
6. **Optimize image size** — Compress PNGs, prefer WebP for large images
7. **Alt text required** — Every image must have descriptive alt text
8. **Illustrative only** — Code blocks in docs are examples, not actual outputs

## Required Screenshots

### 1. GPU Detection (WSL2)

**Command:** `/usr/lib/wsl/lib/nvidia-smi` (or `nvidia-smi` if on PATH)

**What to show:**
- GPU name: NVIDIA GeForce GTX 1060 6GB
- Driver version
- CUDA version
- VRAM

**What to redact:**
- Any user-specific paths
- Process list if it contains private info

### 2. Kimari Doctor

**Command:** `kimari doctor --deep`

**What to show:**
- 14 PASS, 1 WARN output
- CUDA/NVIDIA detection
- GPU compute capability

**What to redact:**
- Any local paths you don't want public

### 3. Kimari Start (dry-run)

**Command:** `kimari start --profile test --dry-run`

**What to show:**
- Profile, model, host, port, binary path

**What to redact:**
- Any user-specific paths if desired

### 4. Health Endpoint

**Command:** `curl http://127.0.0.1:11435/health`

**Expected:** `{"status":"ok"}`

### 5. Models Endpoint

**Command:** `curl http://127.0.0.1:11435/v1/models`

**What to show:**
- Model list with metadata

**What to redact:**
- Nothing — model IDs are public (TinyLlama GGUF names)

### 6. Chat Completion

**Command:** `curl http://127.0.0.1:11435/v1/chat/completions -H "Content-Type: application/json" -d '{"model":"tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf","messages":[{"role":"user","content":"Hello"}],"max_tokens":50}'`

**What to show:**
- Response JSON with timing info

### 7. GTX 1060 Benchmark Results

**What to show:**
- CUDA vs CPU comparison table
- 228 tok/s prompt, 73 tok/s generation (CUDA)
- 77 tok/s prompt, 33 tok/s generation (CPU)

### 8. Open WebUI Connected (if available)

**What to show:**
- Open WebUI chat with Kimari model selected
- Response from local TinyLlama

**What to redact:**
- Any personal conversation content
- API key fields (should be empty)

### 9. OpenClaw Connected (if available)

**What to show:**
- OpenClaw status showing Kimari provider
- Model list including local endpoint

## Recommended Tools

| Tool | Purpose |
|------|---------|
| `nvidia-smi` | GPU detection |
| `kimari doctor --deep` | Full diagnostic |
| `kimari start --profile test --dry-run` | Start command preview |
| `curl /health` | Health check |
| `curl /v1/models` | Model listing |
| `curl /v1/chat/completions` | Chat completion |

## After Screenshots

1. Review each screenshot for secrets/private data
2. Compress images (WebP preferred for large images)
3. Add descriptive alt text
4. Update `docs/SCREENSHOTS.md` with new captures
5. Commit reviewed screenshots only