# Kimari Experimental API

> **⚠️ EXPERIMENTAL — DO NOT BUILD CLIENTS AGAINST THIS YET**
>
> This API is under active development. Endpoints, schemas, and behavior
> **may change without notice** between alpha releases. It is NOT stable.
> FastAPI is an **optional** dependency and must NOT be considered stable
> or part of the core package.

---

## Installation

The API requires the optional `[api]` extra, which installs FastAPI and uvicorn:

```bash
pip install "kimari-local-ai[api]"
```

This adds `fastapi>=0.115.0` and `uvicorn>=0.30.0` as dependencies. Without this extra, the `kimari api` command will print an install hint and exit.

---

## Starting the API

```bash
kimari api --experimental
```

The `--experimental` flag is **required**. Without it, the server will not start. This is an explicit opt-in to acknowledge the API's experimental status.

### Options

| Option | Default | Description |
|---|---|---|
| `--host` | `127.0.0.1` | Bind address |
| `--port` | `11436` | API port number |
| `--experimental` | (required) | Must be set to start the server |
| `--dry-run` | Off | Show what would happen without starting |
| `--json` | Off | Output structured JSON |

### Default Port and Host

- **Default port**: `11436`
- **Default host**: `127.0.0.1`
- **Never** `0.0.0.0` by default — binding to a non-localhost address requires explicit `--host` and will trigger a security warning.

### Dry Run

To verify the API can start without actually starting it:

```bash
kimari api --dry-run
```

---

## Available Endpoints

All endpoints return an `experimental: true` field in their response to remind callers this API is not stable.

### `GET /health`

Health check. Always accessible — no auth required even when auth is enabled.

**Response:**

```json
{
  "status": "ok",
  "version": "0.1.16-alpha",
  "experimental": true
}
```

### `GET /status`

Server status — equivalent to `kimari status --json`.

**Response:**

```json
{
  "running": true,
  "pid": 12345,
  "profile": "gtx1060",
  "model": "qwen3-4b-q4_k_m.gguf",
  "host": "127.0.0.1",
  "port": 11435,
  "uptime_s": null,
  "health": null,
  "experimental": true
}
```

### `GET /config`

Current resolved configuration — equivalent to `kimari config show --json`. Sensitive fields are not exposed.

**Response:**

```json
{
  "config_version": 3,
  "default_profile": "test",
  "profiles": [
    {
      "name": "test",
      "model": "tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf",
      "host": "127.0.0.1",
      "port": 11435,
      "ctx": 2048,
      "quantization": "Q4_K_M",
      "estimated_model_size_gb": 0.7
    }
  ],
  "config_path": "/home/user/.config/kimari/kimari.profiles.json",
  "experimental": true
}
```

### `GET /profiles`

List available GPU profiles — equivalent to `kimari profiles --json`.

**Response:**

```json
{
  "default_profile": "test",
  "profiles": [
    {
      "name": "test",
      "model": "tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf",
      "host": "127.0.0.1",
      "port": 11435,
      "ctx": 2048,
      "batch": 128,
      "ubatch": 64,
      "gpu_layers": "all",
      "flash_attn": "off",
      "parallel": 1
    },
    {
      "name": "gtx1060",
      "model": "qwen3-4b-q4_k_m.gguf",
      "host": "127.0.0.1",
      "port": 11435,
      "ctx": 8192,
      "batch": 256,
      "ubatch": 128,
      "gpu_layers": "all",
      "flash_attn": "on",
      "parallel": 4
    }
  ],
  "experimental": true
}
```

### `GET /models`

List available models — equivalent to `kimari models --json`.

**Response:**

```json
{
  "models": [
    {
      "id": "test",
      "display_name": "TinyLlama 1.1B Chat Q4_K_M",
      "filename": "tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf",
      "size_gb": 0.7,
      "status": "test",
      "downloaded": true,
      "sha256_pinned": true
    }
  ],
  "experimental": true
}
```

### `POST /optimize`

Get optimization recommendations — equivalent to `kimari optimize --json`.

**Request body:**

```json
{
  "profile": "gtx1060",
  "mode": "balanced",
  "vram_gb": 6.0
}
```

| Field | Type | Default | Description |
|---|---|---|---|
| `profile` | `string \| null` | Default from config | Profile to optimize for |
| `mode` | `string` | `"balanced"` | One of: `safe`, `balanced`, `fast`, `ide`, `agent` |
| `vram_gb` | `float \| null` | From profile | Override VRAM budget |

**Response:**

```json
{
  "profile": "gtx1060",
  "recommendations": {
    "ctx": 8192,
    "batch": 256,
    "ubatch": 128,
    "cache_type_k": "f16",
    "cache_type_v": "f16",
    "gpu_layers": "all",
    "flash_attn": true,
    "parallel": 4
  },
  "estimates": {
    "expected_vram_gb": 4.8,
    "expected_ram_gb": 2.1
  },
  "confidence": "medium",
  "warnings": [],
  "experimental": true
}
```

### `POST /perf/dry-run`

Performance dry-run — equivalent to `kimari perf --dry-run --json`. Runs performance estimation without starting the server.

**Request body:**

```json
{
  "profile": "gtx1060",
  "matrix": false
}
```

| Field | Type | Default | Description |
|---|---|---|---|
| `profile` | `string \| null` | Default from config | Profile to estimate for |
| `matrix` | `boolean` | `false` | If true, return results for all modes (`safe`, `balanced`, `fast`, `ide`, `agent`) |

**Response:**

```json
{
  "profile": "gtx1060",
  "model": "qwen3-4b-q4_k_m.gguf",
  "vram_total_gb": 6.0,
  "dry_run": true,
  "modes": [
    {
      "mode": "balanced",
      "ctx": 8192,
      "batch": 256,
      "ubatch": 128,
      "cache_type_k": "f16",
      "cache_type_v": "f16",
      "gpu_layers": "all",
      "flash_attn": true,
      "parallel": 4,
      "expected_vram_gb": 4.8,
      "expected_ram_gb": 2.1,
      "confidence": "medium",
      "warnings": []
    }
  ],
  "experimental": true
}
```

---

## Planned Endpoints (501 Not Implemented)

These endpoints are defined in the API but return `501 Not Implemented`. They are planned for a future release.

### `POST /server/start`

Start llama-server with a named profile.

**Request body:**

```json
{
  "profile": "gtx1060",
  "daemon": false
}
```

**Current response (501):**

```json
{
  "status": "planned",
  "detail": "Server start via API is planned for a future release. Use 'kimari start' for now."
}
```

### `POST /server/stop`

Stop the running llama-server.

**Current response (501):**

```json
{
  "status": "planned",
  "detail": "Server stop via API is planned for a future release. Use 'kimari stop' for now."
}
```

---

## Authentication Behavior

### Localhost (Permissive)

When the API is accessed from `127.0.0.1` or `localhost`:

- **No Bearer token required.** Requests are accepted without authentication.
- If a token is present, it is validated — but missing tokens are not rejected.

### Non-localhost (Strict)

When the API is accessed from a non-localhost address:

- **Bearer token required.** Requests without a valid `Authorization: Bearer <token>` header receive a `401 Unauthorized` response.
- The token is validated against the local token store created by `kimari token create`.

### Health Endpoint Exception

`GET /health` is **always accessible** regardless of auth settings. This is by design — health checks should not require auth.

### Managing Tokens

```bash
# Generate a new token
kimari token create

# Show the current token
kimari token show

# Delete the token
kimari token delete
```

---

## What This API Is NOT

### NOT an OpenAI-Compatible API

The Kimari API on port `11436` is a **management and diagnostic API**. It is NOT an OpenAI-compatible chat/completions endpoint.

If you need an OpenAI-compatible API, that is provided by **llama-server** on port `11435` (by default). The Kimari API complements llama-server — it does not replace it.

```
llama-server → 127.0.0.1:11435  →  OpenAI-compatible chat/completions API
Kimari API   → 127.0.0.1:11436  →  Management, diagnostics, optimization
```

### NOT the Responses API

The Kimari API does **NOT** implement the OpenAI Responses API. There is no `/v1/responses` endpoint and no plan to add one.

---

## curl Examples

### Health Check

```bash
curl http://127.0.0.1:11436/health
```

### List Profiles

```bash
curl http://127.0.0.1:11436/profiles
```

### List Models

```bash
curl http://127.0.0.1:11436/models
```

### Optimize a Profile

```bash
curl -X POST http://127.0.0.1:11436/optimize \
  -H "Content-Type: application/json" \
  -d '{"profile": "gtx1060", "mode": "balanced"}'
```

---

## Security Notes

1. **Default binding is localhost only.** The API binds to `127.0.0.1` by default. It will never bind to `0.0.0.0` unless you explicitly pass `--host 0.0.0.0`.
2. **No secrets in responses.** The API never exposes tokens, API keys, or other secrets in its output.
3. **No model downloads via API.** The API does not trigger model downloads. Use `kimari pull` instead.
4. **Process control is not yet available.** The `POST /server/start` and `POST /server/stop` endpoints return 501.
5. **Non-localhost requires auth.** If you bind to a non-localhost address, Bearer token auth is enforced.

---

## Interactive Docs

When the API is running, interactive documentation is available at:

- **Swagger UI**: `http://127.0.0.1:11436/docs`
- **ReDoc**: `http://127.0.0.1:11436/redoc`

---

*This API is experimental and part of Kimari Local AI v0.1.16-alpha. Expect breaking changes before a stable release.*
