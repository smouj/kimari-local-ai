# Kimari API Plan — Technical Design for v0.2.0-alpha

> **Status**: This is a DESIGN DOCUMENT. No implementation yet. Planned for v0.2.0-alpha.

---

## Overview

A local REST API via FastAPI (`kimari api`) that provides programmatic access to Kimari's CLI capabilities. This enables automation, scripting, and future web UI integration without requiring direct CLI interaction.

The API runs as a companion service alongside llama-server, exposing management and diagnostic endpoints that the CLI currently handles interactively.

---

## Proposed Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/health` | Health check — returns `{"status": "ok"}` |
| `GET` | `/status` | Server status — wraps `kimari status` output |
| `GET` | `/config` | Current configuration (resolved, not raw files) |
| `GET` | `/profiles` | List available GPU profiles |
| `GET` | `/models` | List available models (local + metadata) |
| `POST` | `/server/start` | Start server with a named profile |
| `POST` | `/server/stop` | Stop the running server |
| `POST` | `/optimize` | Get optimization recommendations for current hardware |
| `POST` | `/perf/dry-run` | Performance diagnostic without starting the server |

### Endpoint Details

#### `GET /health`
- No auth required (even when auth is enabled)
- Returns: `{"status": "ok", "version": "0.2.0-alpha"}`

#### `GET /status`
- Returns running state, PID, port, current profile, uptime
- Equivalent to `kimari status --json`

#### `GET /config`
- Returns the resolved configuration Kimari is using
- Sensitive fields (tokens, API keys) are masked

#### `GET /profiles`
- Returns list of profiles with hardware targets and model associations
- Equivalent to `kimari profiles list --json`

#### `GET /models`
- Returns model registry: available models, sizes, quantization levels
- Equivalent to `kimari models list --json`

#### `POST /server/start`
- Body: `{"profile": "<profile_name>"}`
- Starts llama-server with the specified profile
- Returns: `{"status": "started", "profile": "...", "port": ...}`
- Returns 409 if server is already running

#### `POST /server/stop`
- Stops the currently running llama-server
- Returns: `{"status": "stopped"}`
- Returns 404 if no server is running

#### `POST /optimize`
- Body: `{"model": "<model_name>"}` (optional)
- Returns optimization recommendations for current hardware
- Equivalent to `kimari optimize --json`

#### `POST /perf/dry-run`
- Runs performance estimation without starting the server
- Returns predicted tokens/s, memory usage, context window
- Equivalent to `kimari perf dry-run --json`

---

## Authentication

### Bearer Token (Optional)

- **Default**: Disabled. The API runs locally and requires no auth.
- **Enable**: Set `api.auth_enabled = true` in Kimari config.
- **Token**: Generated via `kimari token generate`, stored in the existing token system.
- **Validation**: Uses the same `kimari/security/tokens.py` module the CLI already uses.
- **Header**: `Authorization: Bearer <token>`
- **Scope**: When enabled, applies to all endpoints except `GET /health`.

### Design Rationale

- Local-first: most users run on a single machine, auth adds friction.
- Optional for network-exposed setups (binding to `0.0.0.0`).
- Reuses existing token infrastructure — no new dependency.

---

## Architecture

```
┌──────────────────────────────────────────────────┐
│                  Kimari Process                   │
│                                                   │
│  ┌─────────────┐      ┌──────────────────────┐   │
│  │  CLI (Typer) │      │  API (FastAPI)        │   │
│  │  : main CLI  │      │  : port 11436         │   │
│  └──────┬───────┘      └──────────┬───────────┘   │
│         │                         │               │
│         └─────────┬───────────────┘               │
│                   ▼                               │
│  ┌────────────────────────────────────────────┐   │
│  │        Shared Backend Logic                │   │
│  │  (state, profiles, detection, config,      │   │
│  │   runtime, performance, security)          │   │
│  └────────────────────────────────────────────┘   │
│                                                   │
│  ┌────────────────────────────────────────────┐   │
│  │        llama-server (subprocess)           │   │
│  │        OpenAI-compatible API on :8080       │   │
│  └────────────────────────────────────────────┘   │
└──────────────────────────────────────────────────┘
```

### Key Points

- **FastAPI app runs on a separate port** (default: `11436`).
- **Does NOT replace** llama-server's OpenAI-compatible API (that stays on its port).
- **Complements** llama-server with management/diagnostic endpoints.
- **Runs as a separate process** (`kimari api`) or as a thread within the main process.
- **Shares backend logic** with the CLI — no duplication of business logic.

### Startup

```
$ kimari api [--port 11436] [--host 127.0.0.1] [--auth]
```

- `--port`: API port (default 11436)
- `--host`: Bind address (default 127.0.0.1)
- `--auth`: Enable bearer token authentication

---

## Risks and Considerations

### Local Process Management Security
- Starting/stopping llama-server via API means the API has process control.
- On multi-user systems, this is a real risk.
- Mitigation: default to localhost-only binding; require explicit `--host 0.0.0.0`.

### CORS for Local Web UI
- A future web UI (v0.3) will need to call this API from a browser.
- Plan: enable CORS for `localhost` origins by default.
- Do NOT wildcard `*` — be explicit about allowed origins.

### 0.0.0.0 Binding Risks
- Binding to `0.0.0.0` exposes the API to the local network.
- The `POST /server/start` and `POST /server/stop` endpoints are powerful.
- Mitigation: warn on startup when bound to `0.0.0.0`; require `--auth` flag if non-localhost.

### Windows Process Handling Differences
- `subprocess` behavior differs on Windows (no SIGTERM, process groups work differently).
- The existing `kimari/core/state.py` already handles some of this; the API must use the same logic.
- Test on Windows before release.

### No External Dependencies During Alpha
- FastAPI and uvicorn are the only new dependencies.
- Both are lightweight and well-maintained.
- Do NOT add database layers, ORMs, or message queues during alpha.

---

## Testing Plan

### Unit Tests
- Test each endpoint handler in isolation.
- Mock the shared backend logic (state, profiles, detection).
- Validate request/response schemas with Pydantic models.

### Integration Tests
- Use FastAPI's `TestClient` (backed by `httpx`).
- Test full request/response cycles.
- Verify that API correctly wraps CLI-equivalent logic.

### Auth Token Validation Tests
- Test with auth disabled (default).
- Test with auth enabled + valid token.
- Test with auth enabled + invalid/missing token.
- Verify `GET /health` is always accessible.

### No Real llama-server Needed
- All tests should run without an actual llama-server instance.
- Mock subprocess calls for server start/stop.
- Mock hardware detection for optimize/perf endpoints.

### Test Structure
```
tests/
  test_api/
    test_health.py
    test_status.py
    test_config.py
    test_profiles.py
    test_models.py
    test_server.py
    test_optimize.py
    test_perf.py
    test_auth.py
    conftest.py
```

---

## Migration Path from CLI

### Principles

1. **CLI remains the primary interface.** The API does not replace it.
2. **API provides programmatic access.** For scripts, automation, and future UI.
3. **Shared backend logic.** Both CLI and API call the same functions — no duplication.
4. **Gradual feature parity.** Not every CLI command needs an API endpoint on day one.

### Phasing

- **v0.2.0-alpha**: Core endpoints (health, status, config, profiles, models, server control, optimize, perf).
- **v0.2.0-beta**: Additional endpoints based on user feedback (logs, benchmarks, model pull).
- **v0.3.0**: Full feature parity with CLI; web UI integration.

### No Breaking Changes
- Adding the API layer does not change any existing CLI behavior.
- The shared backend logic is imported, not modified.
- CLI commands continue to work exactly as before.

---

## NOT Included Yet

These are explicitly out of scope for v0.2.0-alpha:

- **Dashboard/web UI** — planned for v0.3.0
- **WebSocket support** — no real-time streaming needed for management endpoints
- **Multi-user authentication** — single-user local tool; one token is sufficient
- **Rate limiting** — local API with a single user; no need
- **OpenAI-compatible chat endpoints** — that's llama-server's job, not ours
- **Database/persistence layer** — file-based config is sufficient
- **Docker-specific endpoints** — out of scope

---

*This document is a plan, not a commitment. Implementation details will change during development.*
