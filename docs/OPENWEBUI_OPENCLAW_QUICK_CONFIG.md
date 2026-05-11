# Quick Config Guide — Open WebUI, OpenClaw, and Hermes

Get your Kimari local AI server connected to Open WebUI, OpenClaw, and Hermes in minutes.

---

## Prerequisites

Kimari server must be running before configuring any integration:

```bash
kimari start
```

Verify the server is responding:

```bash
curl http://127.0.0.1:11435/v1/models
```

If this returns a model list, you're ready to configure integrations.

---

## Open WebUI Configuration

Open WebUI connects to Kimari via the OpenAI-compatible API.

### Settings

| Setting | Value |
|---------|-------|
| Base URL | `http://127.0.0.1:11435/v1` |
| API Key | Not required for local |
| Model name | From your profile (e.g., `kimari` or the model filename) |

### Setup Steps

1. Start Kimari:
   ```bash
   kimari start
   ```

2. Open Open WebUI settings → Connections → OpenAI API

3. Set the Base URL to `http://127.0.0.1:11435/v1`

4. Leave the API Key field empty (or enter any placeholder like `kimari-local`)

5. Set the model name to match your profile's model:
   ```bash
   # Check your current model
   kimari status --json
   ```

6. Save and verify the connection

### Verify

```bash
kimari doctor
```

The doctor command checks that the server is running and the API is reachable.

### Troubleshooting

| Problem | Solution |
|---------|----------|
| Connection refused | Run `kimari start` first |
| Model not found in Open WebUI | Check model name with `kimari models` — use the exact filename or alias |
| Slow responses | Try `kimari optimize` for tuning advice |
| Open WebUI in Docker | Use `http://host.docker.internal:11435/v1` instead of `127.0.0.1` |

---

## OpenClaw Configuration

OpenClaw connects to Kimari as an OpenAI-compatible provider.

### Configuration File

A reference configuration file is provided at:

```
config/integrations/openclaw.kimari.example.json
```

### Settings

| Setting | Value |
|---------|-------|
| Endpoint | `http://127.0.0.1:11435/v1` |
| API Key | `kimari-local` (dummy, no auth enforced) |
| API type | OpenAI Completions |
| Timeout | 300+ seconds |

### Example Configuration

```json
{
  "baseUrl": "http://127.0.0.1:11435/v1",
  "apiKey": "kimari-local",
  "api": "openai-completions",
  "timeoutSeconds": 300,
  "model": "kimari",
  "_kimari_profile": "openclaw-local",
  "_notes": "Start Kimari with: kimari start --profile openclaw-local"
}
```

### Start Kimari for OpenClaw

```bash
kimari start --profile openclaw-local
```

Or use the test profile during alpha:

```bash
kimari start --profile test
```

### Verify

```bash
# Check server is running
curl http://127.0.0.1:11435/v1/models

# Test a completion
curl http://127.0.0.1:11435/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model":"kimari","messages":[{"role":"user","content":"Hello"}]}'
```

### Important Notes

- **Use Chat Completions** (`/v1/chat/completions`). Do NOT configure OpenClaw to use the Responses API.
- **Timeout**: Local inference is slower than cloud APIs. Set `timeoutSeconds` to at least 300.
- **No tokens in config files**: The `apiKey` is a dummy value. Do NOT put real API tokens or secrets in integration config files.

See also: [docs/integrations/OPENCLAW.md](integrations/OPENCLAW.md)

---

## Hermes Configuration

Hermes Agent connects to Kimari as an OpenAI-compatible Chat Completions backend.

### Settings

| Setting | Value |
|---------|-------|
| Endpoint | `http://127.0.0.1:11435/v1` |
| API Key | `kimari-local` (dummy, no auth enforced) |
| API Type | OpenAI Chat Completions |
| Timeout | 300+ seconds |

### Start Kimari for Hermes

```bash
kimari start --profile hermes-local
```

Or use the test profile during alpha:

```bash
kimari start --profile test
```

### Verify

```bash
curl http://127.0.0.1:11435/v1/models
```

### Important Notes

- Configure Hermes to use **OpenAI-compatible server mode** (Chat Completions)
- Quantized models will have lower quality than full-precision cloud models
- Local inference latency depends on GPU capability — use `kimari optimize` to find the best settings

See also: [docs/integrations/HERMES.md](integrations/HERMES.md)

---

## General Notes

### OpenAI-Compatible API

All integrations use the **OpenAI-compatible API** provided by llama-server. This means:

- Endpoint: `http://127.0.0.1:11435/v1`
- Supports: `/v1/chat/completions`, `/v1/models`
- Does NOT support: `/v1/responses` (Responses API)

### No Authentication Required for Localhost

When running on `127.0.0.1`, no API key or token is required. Any value (like `kimari-local`) works as a placeholder.

### Security Warnings

> ⚠️ **Do NOT expose the API to `0.0.0.0` unless you understand the risks.**

Binding to `0.0.0.0` makes your Kimari server accessible to other machines on your network. If you must do this:

1. Use a reverse proxy with authentication (see [docs/REVERSE_PROXY_AUTH.md](REVERSE_PROXY_AUTH.md))
2. Set up Bearer token authentication: `kimari token create`
3. Never leave an unauthenticated server exposed on a public network

### Do NOT Put Real Tokens in Integration Config Files

Integration config files (OpenClaw JSON, Hermes YAML, etc.) are not secure storage. Do not put real API keys, cloud tokens, or any secrets in these files. Use dummy values like `kimari-local` for local connections.

### Do NOT Modify Production Environments Automatically

These configuration guides are for **local development and testing**. Do not apply them to production environments without manual review and testing.

### Verify Setup with Deep Doctor

After configuring all integrations, run a deep check:

```bash
kimari doctor --deep
```

This validates:
- Server is running
- API is reachable
- Models are available
- Configuration is valid
- GPU and CUDA are detected
- Integration endpoints are reachable (when possible)

See also: [docs/DOCTOR_DEEP.md](DOCTOR_DEEP.md)

---

## Quick Reference Table

| Integration | Endpoint | Auth | Config File | Profile |
|-------------|----------|------|-------------|---------|
| Open WebUI | `http://127.0.0.1:11435/v1` | None (local) | Open WebUI settings | Any |
| OpenClaw | `http://127.0.0.1:11435/v1` | Dummy key | `config/integrations/openclaw.kimari.example.json` | `openclaw-local` |
| Hermes | `http://127.0.0.1:11435/v1` | Dummy key | See [HERMES.md](integrations/HERMES.md) | `hermes-local` |

---

## Further Reading

- [OpenAI-Compatible Clients](integrations/OPENAI_COMPATIBLE_CLIENTS.md) — Other compatible tools
- [Architecture](00-03_architecture.md) — How Kimari works
- [REVERSE_PROXY_AUTH.md](REVERSE_PROXY_AUTH.md) — Securing network-exposed setups
- [DOCTOR_DEEP.md](DOCTOR_DEEP.md) — Advanced diagnostics
