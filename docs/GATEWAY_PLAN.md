# Kimari Gateway Plan — Local Controller for the Kimari Runtime

> **Status**: Gateway Dashboard implemented and managed by `kimari gateway ...`. The management API server remains planning-only; all API endpoints listed below are **planned** and have not been implemented.
>
> **Version target**: v0.2.0-alpha (stable gateway release)

---

## Objective

Kimari Gateway has two surfaces:

1. **Gateway Dashboard** — implemented Next.js UI at `127.0.0.1:3105`, managed by `kimari gateway setup/start/stop/status/logs/open/reset`.
2. **Gateway API** — planned local controller API at `127.0.0.1:11436`. It will provide a unified API surface for starting/stopping the inference server, inspecting configuration, querying profiles and models, running benchmarks, and exposing integration-ready status information to tools like Open WebUI, OpenClaw, and Hermes.

The planned Gateway API is NOT an OpenAI-compatible chat API — that role belongs to llama-server on port `11435`. The gateway is a **management and diagnostic layer** running on port `11436`.

---

## Planned Endpoints

| Method | Path | Description | Status |
|--------|------|-------------|--------|
| `GET` | `/health` | Health check — returns `{"status": "ok"}` | Planned |
| `GET` | `/status` | Server status — running state, PID, port, profile, uptime | Planned |
| `GET` | `/profiles` | List available GPU profiles | Planned |
| `GET` | `/models` | List available models (local + metadata) | Planned |
| `GET` | `/config` | Current resolved configuration (sensitive fields masked) | Planned |
| `GET` | `/logs` | Recent gateway and server logs | Planned |
| `GET` | `/integrations` | Integration status (Open WebUI, OpenClaw, Hermes) | Planned |
| `POST` | `/server/start` | Start llama-server with a named profile | Planned |
| `POST` | `/server/stop` | Stop the running llama-server | Planned |
| `POST` | `/benchmark/run` | Run a benchmark and return results | Planned |

### Endpoint Details

#### `GET /health`
- No auth required (even when auth is enabled)
- Returns: `{"status": "ok", "version": "0.2.0-alpha"}`

#### `GET /status`
- Returns running state, PID, port, current profile, uptime
- Equivalent to `kimari status --json`

#### `GET /profiles`
- Returns list of profiles with hardware targets and model associations
- Equivalent to `kimari profiles --json`

#### `GET /models`
- Returns model registry: available models, sizes, quantization levels
- Equivalent to `kimari models --json`

#### `GET /config`
- Returns the resolved configuration Kimari is using
- Sensitive fields (tokens, API keys) are masked
- Equivalent to `kimari config show --json`

#### `GET /logs`
- Returns recent log entries from the gateway and llama-server
- Planned with pagination support

#### `GET /integrations`
- Returns connection status for configured integrations
- Shows Open WebUI, OpenClaw, and Hermes endpoint reachability

#### `POST /server/start`
- Body: `{"profile": "<profile_name>"}`
- Starts llama-server with the specified profile
- Returns: `{"status": "started", "profile": "...", "port": ...}`
- Returns 409 if server is already running

#### `POST /server/stop`
- Stops the currently running llama-server
- Returns: `{"status": "stopped"}`
- Returns 404 if no server is running

#### `POST /benchmark/run`
- Body: `{"profile": "<profile_name>", "mode": "<benchmark_mode>"}`
- Runs a benchmark and returns results
- Equivalent to `kimari benchmark run --json`

---

## Security

The dashboard and planned API follow Kimari's local-first security model:

| Policy | Detail |
|--------|--------|
| Dashboard default bind address | `127.0.0.1:3105` |
| Planned API default bind address | `127.0.0.1:11436` |
| Bind scope | Localhost only — never `0.0.0.0` by default |
| Public exposure | **No** — the gateway must not be exposed to public networks |
| Token storage | **No** — the gateway does not store or manage authentication tokens |
| Model upload | **No** — the gateway does not accept model file uploads |
| Training execution | **No** — the gateway does not trigger training runs |
| Hugging Face publishing | **No** — the gateway has no HF upload capability |

### Rationale

- **Local-first**: Most users run Kimari on a single machine. The gateway adds no network-facing attack surface.
- **No token storage**: Authentication (when needed) delegates to `kimari/security/tokens.py` — the gateway itself is stateless regarding auth.
- **No model upload**: Models are managed via `kimari pull` and the local filesystem. The gateway is read-only for model data.
- **No training execution**: Training is a separate, deliberate workflow. The gateway does not expose it as an endpoint.
- **No HF publishing**: Publishing to Hugging Face requires explicit CLI action (`kimari publish`). The gateway will never automate this.

### Binding to Non-localhost

Binding to `0.0.0.0` or any non-localhost address:

1. Triggers a security warning on startup
2. Requires explicit `--host` flag
3. For the dashboard CLI, requires `--allow-public-bind`
4. For the future API, will require auth before non-localhost exposure
4. Is documented in `docs/REVERSE_PROXY_AUTH.md` for users who need network access

---

## Relationship with Existing FastAPI Experimental (kimari/api/)

The current experimental API (`kimari/api/`) provides:

- `GET /health` — working
- `GET /status` — working
- `GET /profiles` — working
- `GET /models` — working
- `GET /config` — working
- `POST /optimize` — working
- `POST /perf/dry-run` — working
- `POST /server/start` — returns 501 (planned)
- `POST /server/stop` — returns 501 (planned)

See `docs/API_EXPERIMENTAL.md` for the current state of the experimental API.

### Evolution Path

The planned Gateway API will **evolve from** the existing experimental FastAPI implementation:

1. **v0.1.x-alpha**: Experimental API (`kimari api --experimental`) — current state
2. **v0.1.81-alpha**: `kimari gateway` manages the local Dashboard; API endpoints remain planned
3. **v0.2.0-alpha**: Gateway API replaces `kimari api` — stable endpoint set
4. **v0.3.0**: Gateway gains integration endpoints and deeper web UI support

The `kimari/api/` module will be refactored into `kimari/gateway/` when the gateway becomes the primary API surface. During the transition, both `kimari api --experimental` and `kimari gateway` may coexist temporarily.

### What Changes

- Command: `kimari api --experimental` → `kimari gateway`
- Module: `kimari/api/` → `kimari/gateway/`
- Port: Stays `11436`
- New endpoints: `/logs`, `/integrations`, `/benchmark/run`
- Auth: Same model — localhost permissive, non-localhost strict

### What Stays the Same

- FastAPI framework
- Pydantic schemas
- Shared backend logic (no duplication)
- Port `11436`
- Localhost-only default binding

---

## Relationship with Open WebUI, OpenClaw, Hermes

The gateway helps configure and monitor the local OpenAI-compatible llama-server endpoint used by these integrations. It does **not** serve as an OpenAI-compatible endpoint itself — that role belongs to llama-server on port `11435`. The gateway is a **management and diagnostic layer** running on port `11436`.

### Architecture

```
┌──────────────────────────────────────────────────────────┐
│                     User Tools                            │
│                                                          │
│  ┌───────────┐  ┌───────────┐  ┌───────────┐           │
│  │ Open WebUI │  │  OpenClaw  │  │   Hermes   │           │
│  └─────┬─────┘  └─────┬─────┘  └─────┬─────┘           │
│        │               │               │                  │
│        │  Chat/Completions (port 11435)│                  │
│        └───────────────┼───────────────┘                  │
│                        │                                  │
│                        ▼                                  │
│  ┌────────────────────────────────────────────────────┐  │
│  │        llama-server — OpenAI-compatible API         │  │
│  │        http://127.0.0.1:11435/v1                    │  │
│  └────────────────────────────────────────────────────┘  │
│                                                          │
│  ┌───────────┐  ┌───────────┐  ┌───────────┐           │
│  │ Open WebUI │  │  OpenClaw  │  │   Hermes   │           │
│  └─────┬─────┘  └─────┬─────┘  └─────┬─────┘           │
│        │               │               │                  │
│        │  Config/Status (port 11436)   │                  │
│        └───────────────┼───────────────┘                  │
│                        │                                  │
│                        ▼                                  │
│  ┌────────────────────────────────────────────────────┐  │
│  │        Kimari Gateway — Management & Diagnostics    │  │
│  │        http://127.0.0.1:11436                       │  │
│  └────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────┘
```

### Gateway Provides

| Integration | Gateway Role |
|-------------|-------------|
| Open WebUI | `/status` for server state, `/config` for model info, `/models` for model list |
| OpenClaw | `/integrations` for connection status, `/status` for server availability |
| Hermes | `/health` for liveness, `/status` for runtime info |

All three integrations connect to **llama-server** (port `11435`) for chat/completions. The gateway (port `11436`) is for management only.

---

## Current State

The gateway is in **dry-run only** mode. No real server is running yet.

- The `kimari gateway` command exists but only supports dry-run and planning modes
- All endpoints are planned — none are served by a real HTTP server
- The experimental API (`kimari api --experimental`) provides working GET endpoints but is not the gateway yet
- See `docs/API_EXPERIMENTAL.md` for what currently works

---

## How to Use

### Dry Run

Verify the gateway can start without actually starting it:

```bash
kimari gateway --dry-run
```

This checks configuration, profiles, models, and port availability without binding to any port.

### Status Check

View the current gateway status in JSON format:

```bash
kimari gateway --status --json
```

This returns structured information about the runtime state without requiring a running gateway server.

### Plan View

View the planned endpoint configuration:

```bash
kimari gateway --plan --json
```

This returns the full list of planned endpoints, their current implementation status, and configuration defaults.

---

## Future Development Path

### Phase 1: Gateway Foundation (v0.2.0-alpha)

- Refactor `kimari/api/` into `kimari/gateway/`
- Stabilize existing working endpoints from experimental API
- Implement `POST /server/start` and `POST /server/stop`
- Add `/logs` endpoint
- Add proper error handling and validation
- Write comprehensive tests

### Phase 2: Integration Support (v0.2.0-beta)

- Add `/integrations` endpoint
- Add `/benchmark/run` endpoint
- Integration health checks for Open WebUI, OpenClaw, Hermes
- CORS support for local web UI
- WebSocket support for real-time status updates (investigate)

### Phase 3: Web UI Integration (v0.3.0)

- Gateway serves as backend for Kimari web dashboard
- Full feature parity with CLI for management operations
- Rate limiting (if needed for multi-tab browser usage)
- Session management

### Out of Scope

These are explicitly NOT planned for the gateway:

- **OpenAI-compatible chat/completions** — that's llama-server's job
- **Model training** — separate CLI workflow
- **Hugging Face publishing** — separate CLI workflow
- **Multi-user authentication** — single-user local tool
- **Database/persistence layer** — file-based config is sufficient
- **Docker-specific endpoints** — out of scope

---

*This document is a plan, not a commitment. Implementation details will change during development.*
