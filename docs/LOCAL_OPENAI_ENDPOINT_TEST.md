# Local OpenAI-Compatible Endpoint Test

> **Validated on NVIDIA GeForce GTX 1060 6GB (WSL2 Ubuntu 24.04)** with llama-server CUDA build.

This document describes how to test the local OpenAI-compatible endpoint provided by Kimari Local AI.

## ⚠️ Important

- The `test` profile uses **TinyLlama 1.1B Q4_K_M** — a validation model, **NOT Kimari-4B**.
- The `gtx1060` profile targets **Kimari-4B** which is not yet available. Use `--profile test` until Kimari-4B GGUF is released.

## Prerequisites

- Kimari Local AI installed (`pip install -e .` or editable install)
- llama-server compiled with CUDA (or CPU-only fallback)
- A GGUF model downloaded (TinyLlama provided by `test` profile)

## Step 1: Start the Server

```bash
# Activate venv
cd ~/.openclaw/workspace/kimari-local-ai
source .venv/bin/activate

# Start with test profile (TinyLlama 1.1B)
kimari start --profile test

# Or dry-run first to see what command would run
kimari start --profile test --dry-run
```

Expected output:
```
Starting llama-server with profile 'test'...
Model: /home/user/.local/share/kimari/models/tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf
Host: 127.0.0.1:11435
```

## Step 2: Health Check

```bash
curl http://127.0.0.1:11435/health
```

Expected:
```json
{"status":"ok"}
```

## Step 3: List Models

```bash
curl http://127.0.0.1:11435/v1/models
```

Expected:
```json
{
  "object": "list",
  "data": [
    {
      "id": "tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf",
      "object": "model",
      "owned_by": "kimari-local",
      "permission": []
    }
  ]
}
```

## Step 4: Chat Completion

```bash
curl http://127.0.0.1:11435/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf",
    "messages": [
      {"role": "system", "content": "You are Kimari Local AI running locally."},
      {"role": "user", "content": "Explain in one sentence what local AI is."}
    ],
    "max_tokens": 80
  }'
```

Expected: A JSON response with `choices[0].message.content` containing a short answer about local AI.

## Step 5: Stop the Server

```bash
kimari stop
```

## Validated Performance (GTX 1060 CUDA)

| Metric | CUDA GTX 1060 | CPU-only |
|--------|---------------|----------|
| Prompt processing | 228 tok/s | 77 tok/s |
| Token generation | 73 tok/s | 33 tok/s |
| Model VRAM | 1221 MiB | — |

## Integration with Open WebUI / OpenClaw

The endpoint at `http://127.0.0.1:11435` is OpenAI-compatible. Configure it as an OpenAI API endpoint:

- **Base URL**: `http://127.0.0.1:11435/v1`
- **API Key**: Not required (local only)
- **Model name**: As returned by `/v1/models`

## Troubleshooting

| Issue | Solution |
|-------|----------|
| `Connection refused` | Server not started — run `kimari start --profile test` |
| `Model not found` | Run `kimari setup --write --yes` to download TinyLlama |
| `CUDA out of memory` | Use `--profile gtx1060-safe` with smaller context |
| `nvidia-smi not found` | In WSL2, try `/usr/lib/wsl/lib/nvidia-smi` |

## No Claims

- This uses TinyLlama, a general-purpose test model, **not Kimari-4B**.
- No weights, adapters, or checkpoints are uploaded or published.
- Gate remains **BLOCKED** until Kimari-4B is ready.