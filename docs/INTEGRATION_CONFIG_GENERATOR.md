# Integration Config Generator — `kimari integrations generate`

> **Document Type:** Feature guide
> **Applies to:** Kimari Local AI v0.1.27-alpha
> **Related:** [Quick Config Guide](OPENWEBUI_OPENCLAW_QUICK_CONFIG.md), [OpenAI-Compatible Clients](integrations/OPENAI_COMPATIBLE_CLIENTS.md)

---

## Overview

The integration config generator produces ready-to-use configuration snippets for local AI tools that connect to Kimari's llama-server instance. Instead of manually copying endpoint URLs and model names, you can generate a validated config snippet for your preferred tool and paste it into the right location.

**What it does:**

- Generates JSON configuration snippets for local AI tools that connect to llama-server
- Outputs configurations that are safe, local-only, and contain **no tokens or API keys**
- Validates that base URLs point to localhost
- Supports writing output to a file with explicit `--output` and `--write` flags

**What it does NOT do:**

- Does not auto-write configuration files (requires explicit `--write` and `--output`)
- Does not generate or embed API keys, tokens, or secrets
- Does not start the server or make network calls
- Does not modify your existing tool settings

---

## Supported Targets

| Target | Config Format | Description |
|--------|--------------|-------------|
| `openwebui` | JSON | Open WebUI OpenAI API connection settings |
| `openclaw` | JSON | OpenClaw provider configuration (Chat Completions) |
| `hermes` | JSON | Hermes Agent OpenAI-compatible backend config |
| `continue` | JSON | Continue.dev model configuration (VS Code / JetBrains) |

---

## Usage

### Basic usage — generate a config snippet for one target

```bash
kimari integrations generate --target openwebui --json
```

This prints a JSON configuration snippet for Open WebUI to stdout. No files are written.

### Generate configs for all targets

```bash
kimari integrations generate --all --json
```

This prints a JSON object with a key for each supported target, each containing the full config snippet.

### Write a config to a file

```bash
kimari integrations generate --target openwebui --output /tmp/openwebui.json --write
```

The `--write` flag requires an explicit `--output` path. Without `--write`, the output is printed to stdout only. The `--write` flag will not overwrite existing files without confirmation.

### Override the base URL

```bash
kimari integrations generate --target openclaw --base-url http://127.0.0.1:11435/v1 --json
```

By default, the base URL is `http://127.0.0.1:11435/v1` (the standard llama-server endpoint). Use `--base-url` to specify a different local endpoint.

---

## Example Outputs

### Open WebUI

```json
{
  "target": "openwebui",
  "config": {
    "type": "openai",
    "baseUrl": "http://127.0.0.1:11435/v1",
    "apiKey": "kimari-local",
    "modelName": "kimari",
    "notes": "Set in Open WebUI > Settings > Connections > OpenAI API. Leave API key as placeholder for local use."
  },
  "security": {
    "base_url_is_localhost": true,
    "contains_no_tokens": true,
    "contains_no_api_keys": true
  }
}
```

### OpenClaw

```json
{
  "target": "openclaw",
  "config": {
    "baseUrl": "http://127.0.0.1:11435/v1",
    "apiKey": "kimari-local",
    "api": "openai-completions",
    "timeoutSeconds": 300,
    "model": "kimari",
    "_kimari_profile": "openclaw-local",
    "_notes": "Start Kimari with: kimari start --profile openclaw-local"
  },
  "security": {
    "base_url_is_localhost": true,
    "contains_no_tokens": true,
    "contains_no_api_keys": true
  }
}
```

### Hermes

```json
{
  "target": "hermes",
  "config": {
    "endpoint": "http://127.0.0.1:11435/v1",
    "apiKey": "kimari-local",
    "apiType": "openai-chat-completions",
    "timeoutSeconds": 300,
    "model": "kimari",
    "_kimari_profile": "hermes-local",
    "_notes": "Start Kimari with: kimari start --profile hermes-local"
  },
  "security": {
    "base_url_is_localhost": true,
    "contains_no_tokens": true,
    "contains_no_api_keys": true
  }
}
```

### Continue.dev

```json
{
  "target": "continue",
  "config": {
    "models": [
      {
        "title": "Kimari Local",
        "provider": "openai",
        "model": "kimari",
        "apiBase": "http://127.0.0.1:11435/v1",
        "apiKey": "kimari-local"
      }
    ],
    "_kimari_profile": "ide-local",
    "_notes": "Add to ~/.continue/config.json. Start Kimari with: kimari start --profile ide-local"
  },
  "security": {
    "base_url_is_localhost": true,
    "contains_no_tokens": true,
    "contains_no_api_keys": true
  }
}
```

---

## Security

### No tokens, no API keys

Generated configurations **never** contain real API keys, tokens, or secrets. The `apiKey` field is always set to the placeholder value `"kimari-local"`, which is sufficient for localhost connections where llama-server does not enforce authentication.

### Base URL must be localhost

The generator validates that `base_url` resolves to a localhost address (`127.0.0.1`, `localhost`, or `[::1]`). If a non-local base URL is provided:

```
WARN  Base URL is not localhost: http://192.168.1.100:11435/v1
      Non-local endpoints expose your inference server to the network.
      See docs/REVERSE_PROXY_AUTH.md for securing network-accessible setups.
```

The config is still generated (you may intentionally be using a LAN setup), but the warning ensures you are aware of the exposure.

### --write requires explicit output path

The `--write` flag must be paired with `--output`:

```bash
# This works — explicit output path
kimari integrations generate --target openwebui --output /tmp/openwebui.json --write

# This fails — no output path specified
kimari integrations generate --target openwebui --write
# ERROR: --write requires --output to specify the destination file
```

### Sensitive paths are rejected

The `--output` path is validated against known sensitive locations:

| Rejected path | Reason |
|---------------|--------|
| `/etc/`, `/usr/`, `/var/` | System directories |
| `~/.ssh/`, `~/.gnupg/` | Credential stores |
| `~/.aws/`, `~/.config/gcloud/` | Cloud credentials |
| Any path containing `.env` | Environment variable files |

If a sensitive path is detected, the command exits with an error and no file is written.

---

## Validation After Config Generation

After generating and applying a configuration snippet, validate your setup:

### Quick validation

```bash
kimari status
```

This shows whether the server is running, which profile is active, and the model in use.

### Deep validation

```bash
kimari doctor --deep
```

The deep doctor checks:
- Server is running and healthy
- API is reachable at the configured endpoint
- Models are available
- Configuration is valid
- Integration documentation exists

### Manual verification

You can also verify the integration manually:

```bash
# Check that llama-server is responding
curl http://127.0.0.1:11435/v1/models

# Test a chat completion
curl http://127.0.0.1:11435/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model":"kimari","messages":[{"role":"user","content":"Hello"}]}'
```

---

## Command Reference

```
kimari integrations generate [OPTIONS]

Options:
  --target TARGET     Generate config for a specific target
                      (openwebui, openclaw, hermes, continue)
  --all               Generate configs for all supported targets
  --base-url URL      Override the base URL (default: http://127.0.0.1:11435/v1)
  --output FILE       Write output to FILE (required with --write)
  --write             Write the config to the --output path
  --json              Output as structured JSON
```

---

## Related Documentation

- [Quick Config Guide](OPENWEBUI_OPENCLAW_QUICK_CONFIG.md) — Step-by-step setup for Open WebUI, OpenClaw, and Hermes
- [OpenAI-Compatible Clients](integrations/OPENAI_COMPATIBLE_CLIENTS.md) — Other compatible tools
- [Reverse Proxy Auth](REVERSE_PROXY_AUTH.md) — Securing network-accessible setups
- [Deep Doctor](DOCTOR_DEEP.md) — Comprehensive environment diagnostics
- [Security Policy](../SECURITY.md) — Project-wide security guidelines
