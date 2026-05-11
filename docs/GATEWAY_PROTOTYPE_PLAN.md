# Gateway Prototype Plan — Phased Implementation

> **Document Type:** Development plan
> **Applies to:** Kimari Local AI v0.1.26-alpha through v0.2.0-alpha
> **Supersedes:** [Gateway Plan](GATEWAY_PLAN.md) (this document adds the phased prototype roadmap)
> **Related:** [API Experimental](API_EXPERIMENTAL.md), [Reverse Proxy Auth](REVERSE_PROXY_AUTH.md)

---

## Purpose

This document defines the **phased gateway prototype plan** for Kimari. It replaces the flat endpoint list in `docs/GATEWAY_PLAN.md` with a step-by-step implementation roadmap that gates each phase on the success of the previous one.

**Key principle:** The gateway does NOT serve OpenAI-compatible endpoints. That is llama-server's job on port `11435`. The gateway is a **management and diagnostic layer** running on port `11436` that helps configure and monitor llama-server.

---

## Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                        User Tools                             │
│                                                              │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐    │
│  │Open WebUI│  │ OpenClaw │  │  Hermes  │  │Continue  │    │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘    │
│       │              │              │              │           │
│       │   Chat/Completions (port 11435)           │           │
│       └──────────────┼──────────────┴──────────────┘           │
│                      │                                        │
│                      ▼                                        │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │     llama-server — OpenAI-compatible API                 │ │
│  │     http://127.0.0.1:11435/v1                            │ │
│  └──────────────────────────────────────────────────────────┘ │
│                                                              │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐    │
│  │Open WebUI│  │ OpenClaw │  │  Hermes  │  │ Dashboard│    │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘    │
│       │              │              │              │           │
│       │   Config/Status/Mgmt (port 11436)         │           │
│       └──────────────┼──────────────┴──────────────┘           │
│                      │                                        │
│                      ▼                                        │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │     Kimari Gateway — Management & Diagnostics            │ │
│  │     http://127.0.0.1:11436                               │ │
│  └──────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────┘
```

---

## Phased Plan

### Phase 1: Dry-run / Status / Plan (Current — v0.1.26–v0.1.27)

**Status:** Implemented

The gateway exists as a CLI-only feature with no running HTTP server. All gateway interactions are through `kimari gateway` subcommands.

| Command | What It Does |
|---------|-------------|
| `kimari gateway --dry-run` | Shows gateway dry-run summary without starting a server |
| `kimari gateway --status` | Shows current gateway status (state, planned host/port) |
| `kimari gateway --plan` | Shows the full planned endpoint map |
| `kimari gateway --plan --json` | JSON output of the planned endpoint map |

**Endpoints in this phase:** None (CLI only — no HTTP server)

**Security:** No network surface at all. Purely local CLI.

**Exit criteria:**
- `kimari gateway --dry-run` runs without error
- `kimari gateway --status --json` returns valid JSON
- `kimari gateway --plan --json` returns the full endpoint map
- All existing tests pass

---

### Phase 2: Local Read-Only FastAPI Gateway

**Status:** Planned

A real FastAPI server starts on `127.0.0.1:11436` and serves **GET endpoints only**. No state mutation, no process management.

| Method | Path | Description | Returns |
|--------|------|-------------|---------|
| `GET` | `/health` | Health check | `{"status": "ok", "version": "0.1.x-alpha"}` |
| `GET` | `/status` | Server status | Running state, PID, port, profile, uptime |
| `GET` | `/profiles` | Available profiles | List of profiles with hardware targets |
| `GET` | `/models` | Available models | Model registry with sizes and status |
| `GET` | `/config` | Current configuration | Resolved config (sensitive fields masked) |

**Security:**
- Binds to `127.0.0.1:11436` only — **never** `0.0.0.0`
- No authentication required for localhost connections
- No CORS headers (same-origin only)
- Sensitive fields in `/config` are masked (tokens, API keys replaced with `***`)
- Read-only: no POST, PUT, DELETE, or PATCH endpoints

**Exit criteria:**
- `kimari gateway --start` starts a FastAPI server on 127.0.0.1:11436
- All 5 GET endpoints return correct data
- `/config` does not expose tokens or secrets
- Server refuses to bind to 0.0.0.0
- Non-localhost binding triggers security warning
- Process cleanly stops on SIGINT/SIGTERM
- Integration tests for all endpoints pass

---

### Phase 3: Controlled Process Start/Stop

**Status:** Planned

Add POST endpoints for starting and stopping llama-server. These are the first mutation endpoints and include safety checks.

| Method | Path | Description | Safety Checks |
|--------|------|-------------|---------------|
| `POST` | `/server/start` | Start llama-server with a named profile | Profile must exist, server must not already be running, port must be free |
| `POST` | `/server/stop` | Stop the running llama-server | Server must be running, PID must be alive |

**Request/Response:**

```json
// POST /server/start
// Request:
{"profile": "gtx1060"}

// Response (success):
{"status": "started", "profile": "gtx1060", "port": 11435, "pid": 12345}

// Response (already running):
{"status": "error", "message": "Server already running on port 11435 (PID 12345)"}
```

```json
// POST /server/stop
// Response (success):
{"status": "stopped", "profile": "gtx1060", "pid": 12345}

// Response (not running):
{"status": "error", "message": "No server is running"}
```

**Security:**
- Still binds to `127.0.0.1:11436` only — **never** `0.0.0.0`
- POST endpoints only accept JSON bodies with required fields
- `/server/start` validates the profile exists before starting
- `/server/start` refuses to start if another instance is already running
- `/server/stop` validates the PID is alive before sending SIGTERM
- No arbitrary command execution — only `llama-server` can be started/stopped
- Rate limiting: max 1 start/stop request per 5 seconds

**Exit criteria:**
- `/server/start` successfully starts llama-server with a valid profile
- `/server/start` returns 409 if server already running
- `/server/start` returns 400 for invalid profile name
- `/server/stop` successfully stops a running server
- `/server/stop` returns 404 if no server is running
- State is correctly written to `.kimari/state.json`
- Process lifecycle is managed cleanly (no zombie processes)
- All GET endpoints still work correctly

---

### Phase 4: Benchmark Execution

**Status:** Planned

Add a POST endpoint for running benchmarks with result storage.

| Method | Path | Description | Safety Checks |
|--------|------|-------------|---------------|
| `POST` | `/benchmark/run` | Run a benchmark and store results | Server must be running, profile must exist, dry-run mode available |

**Request/Response:**

```json
// POST /benchmark/run
// Request:
{"profile": "gtx1060", "mode": "standard"}

// Response (success):
{
  "status": "completed",
  "profile": "gtx1060",
  "results": { "... benchmark data ..." },
  "saved_to": "benchmarks/results/gtx1060-2025-03-04.json"
}

// Response (dry-run):
{
  "status": "dry_run",
  "profile": "gtx1060",
  "estimated_duration_s": 120,
  "prompts_count": 7
}
```

**Security:**
- Still binds to `127.0.0.1:11436` only — **never** `0.0.0.0`
- Benchmark results are stored locally only — no network transmission
- No access to raw model weights through the endpoint
- Results are written to `benchmarks/results/` with standard naming convention
- Dry-run mode is available and is the default for unattended runs

**Exit criteria:**
- `/benchmark/run` with `dry_run: true` returns the plan without executing
- `/benchmark/run` executes benchmark and returns results
- Results are saved to `benchmarks/results/` in the standard format
- Results conform to the schema in `benchmarks/SCHEMA.md`
- Concurrent benchmark runs are prevented (one at a time)
- Server must be running (READY status) for non-dry-run benchmarks
- All previous GET and POST endpoints still work

---

### Phase 5: Dashboard / Web UI

**Status:** Planned

A frontend dashboard for managing Kimari through a browser interface, served by the gateway.

| Feature | Description |
|---------|-------------|
| Status dashboard | Real-time server status, health, uptime |
| Profile selector | Switch between GPU profiles |
| Model browser | View available models and pull new ones |
| Benchmark viewer | View benchmark results and history |
| Configuration editor | Edit Kimari configuration with validation |
| Log viewer | Stream server logs in real-time |

**Security:**
- Still binds to `127.0.0.1:11436` only — **never** `0.0.0.0`
- Static assets served from `kimari/gateway/static/`
- No external CDN dependencies — all assets are local
- WebSocket support for real-time log streaming (same-origin only)
- CORS headers limited to `http://127.0.0.1:11436`
- No authentication for localhost, Bearer token required for non-localhost

**Exit criteria:**
- Dashboard loads at `http://127.0.0.1:11436/`
- All Phase 2-4 endpoints are accessible through the dashboard
- Dashboard works without internet access (no CDN dependencies)
- No secrets visible in the dashboard UI
- Responsive design for common screen sizes

---

## Endpoints by Phase

| Method | Path | Phase 1 | Phase 2 | Phase 3 | Phase 4 | Phase 5 |
|--------|------|---------|---------|---------|---------|---------|
| `GET` | `/health` | CLI | Server | Server | Server | Server |
| `GET` | `/status` | CLI | Server | Server | Server | Server |
| `GET` | `/profiles` | CLI | Server | Server | Server | Server |
| `GET` | `/models` | CLI | Server | Server | Server | Server |
| `GET` | `/config` | CLI | Server | Server | Server | Server |
| `GET` | `/logs` | — | — | — | — | Server |
| `GET` | `/integrations` | — | — | — | — | Server |
| `POST` | `/server/start` | — | — | Server | Server | Server |
| `POST` | `/server/stop` | — | — | Server | Server | Server |
| `POST` | `/benchmark/run` | — | — | — | Server | Server |

---

## Security Per Phase

| Policy | Phase 1 | Phase 2 | Phase 3 | Phase 4 | Phase 5 |
|--------|---------|---------|---------|---------|---------|
| Bind address | N/A (CLI) | `127.0.0.1` | `127.0.0.1` | `127.0.0.1` | `127.0.0.1` |
| Bind port | N/A (CLI) | `11436` | `11436` | `11436` | `11436` |
| `0.0.0.0` binding | N/A | **Never** | **Never** | **Never** | **Never** |
| Auth for localhost | N/A | None | None | None | None |
| Auth for non-localhost | N/A | Blocked | Blocked | Blocked | Bearer token |
| Sensitive data exposure | N/A | Masked | Masked | Masked | Masked |

### Binding Policy

The gateway **always** binds to `127.0.0.1:11436`. There is no default or fallback to `0.0.0.0`.

If a user explicitly requests a non-localhost bind address via `--host`:
1. A security warning is printed on startup
2. The `--auth` flag becomes mandatory (Bearer token enforced)
3. The warning references `docs/REVERSE_PROXY_AUTH.md`
4. The gateway logs the non-localhost binding at WARN level

### No 0.0.0.0 — Ever

`0.0.0.0` is never a valid bind address for the gateway. If a user passes `--host 0.0.0.0`:

```
ERROR  Refusing to bind to 0.0.0.0 — this exposes the gateway to all network interfaces.
       Use --host 127.0.0.1 for local access, or a specific IP for LAN access with --auth.
       See docs/REVERSE_PROXY_AUTH.md for secure network setups.
```

---

## Gateway vs. llama-server

It is critical to understand the separation:

| Aspect | llama-server (port 11435) | Kimari Gateway (port 11436) |
|--------|--------------------------|----------------------------|
| Role | Inference server | Management and diagnostics |
| Protocol | OpenAI-compatible API | Kimari management API |
| Endpoints | `/v1/chat/completions`, `/v1/models` | `/status`, `/profiles`, `/config`, etc. |
| Used by | Open WebUI, OpenClaw, Hermes, Continue | Dashboard, CLI, integrations (for config) |
| Auth | Optional (Bearer token) | None for localhost, Bearer for non-localhost |
| Started by | `kimari start` or gateway `/server/start` | `kimari gateway --start` |

The gateway **helps configure and monitor** llama-server. It does NOT serve OpenAI-compatible endpoints.

---

## Relationship to Existing Experimental API

The current experimental API (`kimari/api/`) provides working GET endpoints. The gateway will evolve from this codebase:

1. **v0.1.x-alpha**: Experimental API (`kimari api --experimental`) — current state
2. **Phase 2**: Gateway refactored from `kimari/api/` to `kimari/gateway/`
3. **Phase 3+**: New endpoints added to the gateway module

During the transition, `kimari/api/` and `kimari/gateway/` may coexist temporarily. See `docs/API_EXPERIMENTAL.md` for the current experimental API status.

---

## Out of Scope

These features are explicitly NOT planned for the gateway:

- **OpenAI-compatible chat/completions** — that is llama-server's job
- **Model training** — separate CLI workflow
- **Hugging Face publishing** — separate CLI workflow
- **Multi-user authentication** — single-user local tool
- **Database/persistence layer** — file-based config is sufficient
- **Docker-specific endpoints** — out of scope
- **Remote management** — gateway is local-only

---

*This document is a plan, not a commitment. Implementation details will change during development. Each phase must pass its exit criteria before the next phase begins.*
