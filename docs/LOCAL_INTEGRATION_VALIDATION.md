# Local Integration Validation

> **Validated on NVIDIA GeForce GTX 1060 6GB (WSL2 Ubuntu 24.04)** with llama-server CUDA and TinyLlama 1.1B Q4_K_M.

This document describes how to connect Kimari Local AI's OpenAI-compatible endpoint to popular local AI tools.

## ⚠️ Important

- The `test` profile uses **TinyLlama 1.1B Q4_K_M** — a validation model, **NOT Kimari-4B**.
- The `gtx1060` profile targets **Kimari-4B** which is not yet available. Use `--profile test` until Kimari-4B GGUF is released.
- No API key is required for local usage on `127.0.0.1`.

## Endpoint Details

| Field | Value |
|-------|-------|
| Base URL | `http://127.0.0.1:11435/v1` |
| Health | `http://127.0.0.1:11435/health` |
| Models | `http://127.0.0.1:11435/v1/models` |
| Chat Completions | `http://127.0.0.1:11435/v1/chat/completions` |
| Model name (test) | `tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf` |
| API Key | Not required (localhost only) |
| Protocol | OpenAI-compatible |

## Start the Server

```bash
cd ~/.openclaw/workspace/kimari-local-ai
source .venv/bin/activate
kimari start --profile test
```

## Verify the Endpoint

```bash
# Health check
curl http://127.0.0.1:11435/health
# {"status":"ok"}

# List models
curl http://127.0.0.1:11435/v1/models

# Chat completion
curl http://127.0.0.1:11435/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model":"tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf","messages":[{"role":"user","content":"Hello"}],"max_tokens":50}'
```

## Integration Guides

| Tool | Setup Guide |
|------|-------------|
| **Open WebUI** | [OPENWEBUI_LOCAL_SETUP.md](OPENWEBUI_LOCAL_SETUP.md) |
| **OpenClaw** | [OPENCLAW_LOCAL_SETUP.md](OPENCLAW_LOCAL_SETUP.md) |
| **Continue.dev** | [CONTINUE_LOCAL_SETUP.md](CONTINUE_LOCAL_SETUP.md) |
| **curl / OpenAI SDK** | [LOCAL_OPENAI_ENDPOINT_TEST.md](LOCAL_OPENAI_ENDPOINT_TEST.md) |

## Stop the Server

```bash
kimari stop
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| `Connection refused` | Run `kimari start --profile test` first |
| `Model not found` | Run `kimari setup --write --yes` to download TinyLlama |
| `CUDA out of memory` | Use `--profile gtx1060-safe` with smaller context |
| `nvidia-smi not found` | In WSL2, try `/usr/lib/wsl/lib/nvidia-smi` |
| Slow first response | Normal — model loads into VRAM on first request |

## No Claims

- This uses TinyLlama, a general-purpose test model, **not Kimari-4B**.
- No weights, adapters, or checkpoints are uploaded or published.
- Gate remains **BLOCKED** until Kimari-4B is ready.