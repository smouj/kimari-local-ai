# Open WebUI Local Setup

> **How to connect Open WebUI to Kimari Local AI's OpenAI-compatible endpoint.**

## ⚠️ Important

- Uses **TinyLlama 1.1B Q4_K_M** as the validation model — **NOT Kimari-4B**.
- No API key is required for localhost connections.
- Open WebUI must be running and accessible from the same machine.

## Prerequisites

- Kimari Local AI installed and TinyLlama model downloaded
- Open WebUI installed (`pip install open-webui` or Docker)
- llama-server running on `127.0.0.1:11435`

## Step 1: Start Kimari

```bash
cd ~/.openclaw/workspace/kimari-local-ai
source .venv/bin/activate
kimari start --profile test
```

Verify it's running:

```bash
curl http://127.0.0.1:11435/health
# {"status":"ok"}
```

## Step 2: Configure Open WebUI

1. Open Open WebUI in your browser (default: `http://localhost:8080`)
2. Go to **Settings** → **Connections**
3. Add a new OpenAI API connection:

| Field | Value |
|-------|-------|
| API Base URL | `http://127.0.0.1:11435/v1` |
| API Key | *(leave empty or enter any placeholder)* |
| Model name | `tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf` |

4. Click **Save** and verify the connection shows as active.

## Step 3: Use the Model

1. Start a new chat in Open WebUI
2. Select `tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf` from the model dropdown
3. Send a message — responses come from Kimari's local endpoint

## Docker Setup (Alternative)

If running Open WebUI in Docker, use `host.docker.internal` instead of `127.0.0.1`:

```
API Base URL: http://host.docker.internal:11435/v1
```

## Common Errors

| Error | Cause | Solution |
|-------|-------|----------|
| `Connection refused` | Kimari not started | Run `kimari start --profile test` |
| `Model not in dropdown` | Model name mismatch | Check `curl http://127.0.0.1:11435/v1/models` |
| `401 Unauthorized` | API key mismatch | Leave API key empty or enter any placeholder text |
| Docker can't reach host | Network isolation | Use `host.docker.internal` or `--network host` |
| Slow responses | Model loading on first request | Normal — subsequent requests are faster |

## No Claims

- Open WebUI connects to Kimari's local endpoint using TinyLlama.
- **Kimari-4B is not released.** When available, update the model name in settings.
- No API keys, tokens, or private data are committed.