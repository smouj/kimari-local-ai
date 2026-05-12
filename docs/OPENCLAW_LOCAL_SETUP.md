# OpenClaw Local Setup

> **How to connect OpenClaw to Kimari Local AI's OpenAI-compatible endpoint.**

## ⚠️ Important

- Uses **TinyLlama 1.1B Q4_K_M** as the validation model — **NOT Kimari-4B**.
- No API key is required for localhost connections.

## Prerequisites

- Kimari Local AI installed and TinyLlama model downloaded
- OpenClaw installed and configured
- llama-server running on `127.0.0.1:11435`

## Step 1: Start Kimari

```bash
cd ~/.openclaw/workspace/kimari-local-ai
source .venv/bin/activate
kimari start --profile test
```

Verify:

```bash
curl http://127.0.0.1:11435/health
# {"status":"ok"}
```

## Step 2: Configure OpenClaw

Add Kimari as an OpenAI-compatible provider in your OpenClaw configuration.

### Via Gateway Config

Set the model configuration to use Kimari's local endpoint:

| Field | Value |
|-------|-------|
| Provider type | OpenAI-compatible |
| Base URL | `http://127.0.0.1:11435/v1` |
| Model | `tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf` |
| API Key | Not required (localhost) |

### Example Configuration

```yaml
# In OpenClaw gateway config, add Kimari as a custom provider
providers:
  kimari-local:
    type: openai-compatible
    base_url: http://127.0.0.1:11435/v1
    models:
      - id: tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf
        name: Kimari Local (TinyLlama)
        context_window: 4096
```

## Step 3: Verify Connection

Use the `/status` command or check the model list in OpenClaw:

```
kimari-local should appear as an available provider
```

## Health Check

OpenClaw can monitor the Kimari endpoint:

- **Health URL**: `http://127.0.0.1:11435/health`
- **Expected response**: `{"status":"ok"}`

## Common Errors

| Error | Cause | Solution |
|-------|-------|----------|
| `Connection refused` | Kimari not started | Run `kimari start --profile test` |
| `Model not found` | Model name mismatch | Check with `curl http://127.0.0.1:11435/v1/models` |
| Timeout on responses | Model loading | Normal for first request; increase timeout |
| Config not found | OpenClaw config path | Check `openclaw gateway status` |

## No Claims

- OpenClaw connects to Kimari's local endpoint using TinyLlama.
- **Kimari-4B is not released.** When available, update the model in config.
- No tokens, API keys, or private data are committed.