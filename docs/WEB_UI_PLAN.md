# Kimari Web UI Plan

**Version:** 0.1.0 (Planning)
**Status:** Planning — No implementation exists
**Last Updated:** 2025

---

## 1. Objective

Provide an optional local web dashboard for Kimari that allows users to:

- **Start / stop** the llama-server process
- **View server status** (running, model, profile, uptime, health)
- **Manage models** (list downloaded, pull from registry, see sizes)
- **Open Open WebUI** (one-click launch of the existing Docker-based chat UI)
- **Launch benchmarks** (run `kimari bench` and display results)
- **View logs** (tail `kimari-server.log` from the browser)
- **Export diagnostics** (download `kimari doctor --json` output as a JSON file)

The CLI remains the primary and canonical interface. The web UI is an **optional convenience layer** — nothing in the web UI should be the only way to accomplish a task. Every web UI action maps 1:1 to an existing CLI command.

### Relationship to Existing Docs

This plan complements [00-06_web_pwa_desktop.md](00-06_web_pwa_desktop.md), which describes a longer-term PWA chat interface and Tauri desktop app. This document focuses on the **management dashboard** — the control plane for server lifecycle, models, and diagnostics — not the chat interface itself. The two tracks converge at the Tauri phase (v1.0).

---

## 2. Architecture Suggestion

```
┌─────────────────────────────────────────────────────┐
│                  Browser / PWA                       │
│  ┌───────────────────────────────────────────────┐  │
│  │   React + Tailwind (or Svelte + Tailwind)     │  │
│  │   ─ status, start/stop, models, logs, bench ─ │  │
│  └──────────────────┬────────────────────────────┘  │
│                     │ fetch / SSE                    │
│                     ▼                                │
│  ┌───────────────────────────────────────────────┐  │
│  │   FastAPI (localhost:11436)                    │  │
│  │   ─ REST API, token auth, CORS ─              │  │
│  └──────────────────┬────────────────────────────┘  │
│                     │ calls into                     │
│                     ▼                                │
│  ┌───────────────────────────────────────────────┐  │
│  │   kimari.* Python modules                     │  │
│  │   (state, config, detection, models, bench)   │  │
│  └───────────────────────────────────────────────┘  │
│                     │ subprocess / HTTP              │
│                     ▼                                │
│  ┌───────────────────────────────────────────────┐  │
│  │   llama-server (localhost:11435)               │  │
│  └───────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────┘
```

### Key Points

| Aspect | Decision | Rationale |
|--------|----------|-----------|
| Backend | FastAPI | Async, auto-generated OpenAPI docs, Pydantic validation, native WebSocket/SSE — all already in the Python ecosystem Kimari uses |
| Frontend | React + Tailwind (or Svelte + Tailwind) | Component model suits a dashboard; Tailwind for rapid, consistent styling; large ecosystem for charting/log viewers |
| API port | 11436 (one above llama-server) | Avoids conflict with llama-server on 11435; easy to remember |
| CLI primacy | Web UI calls same `kimari.*` modules | No duplication of logic; CLI stays the source of truth |

---

## 3. Roadmap by Phases

### v0.2 — Local REST API (FastAPI)

**Goal:** Programmatic access to start, stop, check status, and list models — no UI yet.

| Deliverable | Description |
|-------------|-------------|
| `kimari api` CLI command | Starts the FastAPI server on `127.0.0.1:11436` |
| Token generation | `kimari api --generate-token` prints a random hex token and stores it in `.kimari/api-token` |
| Core endpoints | `/api/status`, `/api/start`, `/api/stop`, `/api/models`, `/api/config` |
| Auth middleware | Bearer token check on every `/api/*` route |
| CORS config | Allow only `http://127.0.0.1:*` and `http://localhost:*` |
| Tests | Pytest suite for all endpoints |

**Why this phase first:** The REST API is the foundation. It can be consumed by scripts, automation tools, and eventually the frontend. Shipping it independently lets power users build integrations before the UI exists.

### v0.3 — Minimal Dashboard

**Goal:** A single-page status view with start/stop controls.

| Deliverable | Description |
|-------------|-------------|
| React app scaffold | Vite + React + Tailwind, served as static files by FastAPI |
| Status page | Server state (STOPPED / STARTING / READY / ERROR), model, profile, uptime, health |
| Start / Stop buttons | Call `/api/start` and `/api/stop`; show confirmation for stop |
| Model list | Table of downloaded GGUF files with sizes |
| Log viewer | Tail `/api/logs` via SSE; auto-scroll, pause/resume |
| Open WebUI link | Button that opens `http://127.0.0.1:11435` in a new tab |
| Responsive layout | Works on desktop and mobile browsers |

**Not included:** Model downloads, benchmark launcher, diagnostics export — these arrive in v0.4.

### v0.4 — PWA with Model Management

**Goal:** Installable PWA with full model management and benchmark support.

| Deliverable | Description |
|-------------|-------------|
| PWA manifest + service worker | "Add to Home Screen" support; offline shell shows cached status |
| Model pull | `/api/pull/{model_id}` endpoint; progress bar in UI |
| Benchmark launcher | `/api/bench` endpoint; results displayed as a table and simple chart |
| Diagnostics export | `/api/doctor` endpoint; "Download diagnostics JSON" button |
| Settings panel | View/edit config (port, host, context) — writes to `kimari.profiles.json` |
| Toast notifications | Server started, server stopped, model downloaded, benchmark complete |

### v1.0 — Desktop App Integration (Tauri)

**Goal:** Wrap the PWA in a Tauri shell for native OS integration.

| Deliverable | Description |
|-------------|-------------|
| Tauri v2 scaffold | Rust backend, same React frontend as PWA |
| System tray | Minimize to tray; show server status icon |
| Auto-start option | Register as a login item (macOS/Linux/Windows) |
| Native notifications | OS-level notifications for server events |
| GPU monitor overlay | Real-time VRAM/utilization via `nvidia-smi` polling in Rust |
| Single binary distribution | `.deb`, `.dmg`, `.msi` installers |

---

## 4. Security Considerations

The web UI introduces an HTTP server on the local machine. This requires stricter security than the CLI, which runs as a single-user process with no network surface.

### 4.1 Binding

- **Default bind: `127.0.0.1` only.** Never `0.0.0.0`.
- The FastAPI server MUST refuse to start if the bind address is anything other than a loopback address, unless the user explicitly passes `--allow-remote` and acknowledges a warning.
- Rationale: The existing llama-server already follows this principle (see [00-09_security_governance.md](00-09_security_governance.md), "Default Configuration").

### 4.2 Authentication

- **Token-based auth on every `/api/*` route.**
- Token is a 32-byte hex string generated by `kimari api --generate-token` and stored in `.kimari/api-token`.
- Requests must include `Authorization: Bearer <token>`.
- The token file has `0600` permissions (owner read/write only).
- No JWT complexity — a single static token is sufficient for a single-user local tool.
- On first `kimari api` run without a token, the server prints the generated token and instructs the user to save it.

### 4.3 CORS

- **Allow origins:** `http://127.0.0.1:*`, `http://localhost:*` only.
- No wildcard `*` origin.
- If the dashboard is served from the FastAPI server itself (same origin), CORS is not needed for same-origin requests — but the policy is enforced as a defense-in-depth measure for development workflows (e.g., Vite dev server on port 5173).

### 4.4 Data Locality

- **No data leaves the machine.** No analytics, no telemetry, no external API calls.
- The frontend makes requests only to `127.0.0.1:11435` (llama-server) and `127.0.0.1:11436` (FastAPI).
- Model downloads go directly from Hugging Face to the local machine — no proxy through the API server.
- Logs and diagnostics are served from local files; nothing is uploaded.

### 4.5 Rate Limiting & Input Validation

- Pydantic models on every request body (FastAPI default).
- No arbitrary command injection — the API wraps specific `kimari.*` module calls, not `os.system` or `subprocess` with user-supplied strings.
- Rate limit on `/api/start` and `/api/stop` (max 1 request per 3 seconds) to prevent rapid restart loops.

---

## 5. API Endpoints Sketch

This is **planning only** — no implementation exists. All endpoints require `Authorization: Bearer <token>` unless noted.

### `GET /api/status`

Returns current server state aggregated from `.kimari/state.json`, llama-server `/health`, and `/v1/models`.

```json
{
  "status": "READY",
  "pid": 48291,
  "profile": "gtx1060",
  "model": "models/Kimari-4B-Q4_K_M.gguf",
  "host": "127.0.0.1",
  "port": 11435,
  "uptime_s": 3672,
  "started_at": "2025-07-15T09:12:00Z",
  "health": { "status": "ok" },
  "loaded_models": ["Kimari-4B-Q4_K_M"],
  "error": null
}
```

### `POST /api/start`

Start llama-server with a given profile. Mirrors `kimari start --profile <name>`.

```json
// Request
{
  "profile": "gtx1060",
  "model": null,
  "host": null,
  "port": null,
  "ctx": null
}

// Response (202 Accepted — server is starting)
{
  "status": "STARTING",
  "profile": "gtx1060",
  "message": "Server starting. Poll /api/status for readiness."
}
```

### `POST /api/stop`

Stop the running llama-server. Mirrors `kimari stop`.

```json
// Response (200 OK)
{
  "status": "STOPPED",
  "message": "Server stopped."
}
```

### `GET /api/models`

List downloaded GGUF models and registry entries. Mirrors `kimari models`.

```json
{
  "downloaded": [
    { "name": "Kimari-4B-Q4_K_M.gguf", "path": "models/Kimari-4B-Q4_K_M.gguf", "size_mb": 2304.5 }
  ],
  "registry": [
    { "id": "test", "display_name": "TinyLlama 1.1B (Test)", "size_gb": 0.6, "downloaded": true },
    { "id": "qwen-1.5-7b-q4", "display_name": "Qwen 1.5 7B Q4_K_M", "size_gb": 4.4, "downloaded": false }
  ]
}
```

### `POST /api/pull/{model_id}`

Download a model from the registry. Mirrors `kimari pull <model_id>`. Returns a task ID; progress available via SSE or polling.

```json
// Response (202 Accepted)
{
  "task_id": "pull-abc123",
  "model_id": "qwen-1.5-7b-q4",
  "status": "downloading",
  "message": "Pull started. Stream /api/pull/pull-abc123/progress for updates."
}
```

### `GET /api/logs`

Return recent log lines from `kimari-server.log`. Supports query params for pagination and SSE streaming.

```
Query params:
  ?lines=100        (number of lines, default 100)
  ?follow=true      (switch to SSE streaming for real-time tail)

// Response (application/json)
{
  "lines": [
    "llama_server: loading model...",
    "llama_server: model loaded successfully",
    "llama_server: server listening on 127.0.0.1:11435"
  ],
  "total_lines": 1042,
  "truncated": false
}
```

### `POST /api/bench`

Run a benchmark. Mirrors `kimari bench`. Returns a task ID; results available via polling.

```json
// Request
{
  "profile": "gtx1060"
}

// Response (202 Accepted)
{
  "task_id": "bench-def456",
  "status": "running",
  "message": "Benchmark in progress. Poll /api/bench/bench-def456 for results."
}
```

```json
// GET /api/bench/bench-def456 — Result
{
  "task_id": "bench-def456",
  "status": "complete",
  "results": {
    "ttft_ms": 850,
    "generation_time_s": 12.45,
    "tokens_generated": 187,
    "tokens_per_second": 15.0
  }
}
```

### `GET /api/config`

Return the current profile configuration. Mirrors `kimari config show`.

```json
{
  "config_version": 2,
  "default_profile": "gtx1060",
  "profiles": {
    "gtx1060": {
      "name": "GTX 1060 6GB",
      "model": "models/Kimari-4B-Q4_K_M.gguf",
      "ctx": 8192,
      "host": "127.0.0.1",
      "port": 11435
    }
  }
}
```

### Additional Endpoints (v0.4+)

| Endpoint | Method | Phase | Description |
|----------|--------|-------|-------------|
| `/api/doctor` | GET | v0.4 | Run `kimari doctor --json` and return diagnostics |
| `/api/fit` | GET | v0.4 | Calculate KimariFit score (params: model, ctx, vram) |
| `/api/pull/{task_id}/progress` | GET (SSE) | v0.4 | Stream download progress |
| `/api/config` | PATCH | v0.4 | Update config values (writes to `kimari.profiles.json`) |

---

## 6. Technical Decisions

### 6.1 Why FastAPI over Flask

| Factor | FastAPI | Flask |
|--------|---------|-------|
| Async support | Native `async def` handlers; SSE/WebSocket without thread pools | Requires `flask[async]` or gevent; more complex |
| Schema validation | Pydantic models built-in; auto-rejects invalid requests | Requires `marshmallow` or manual validation |
| API documentation | Auto-generated OpenAPI / Swagger UI at `/docs` | Requires `flask-smorest` or `flasgger` |
| Type safety | Pydantic return types; IDE autocomplete for request/response | Dict-based; no structural guarantees |
| Ecosystem alignment | Modern Python (3.10+); aligns with Kimari's Python 3.10 requirement | Mature but synchronous-first; designed for Python 2 era |
| Performance | ASGI (uvicorn); handles concurrent SSE streams efficiently | WSGI; needs gevent/eventlet for long-lived connections |

**Decision:** FastAPI. The async story and auto-docs alone justify it. Kimari already requires Python 3.10+, so there is no compatibility concern.

### 6.2 Why React + Tailwind over Vue + Tailwind

| Factor | React + Tailwind | Vue + Tailwind |
|--------|-------------------|----------------|
| Component ecosystem | Larger library of dashboard components (charts, log viewers, data tables) | Good but smaller ecosystem |
| State management | `useState` + context is sufficient for this app's complexity | Vuex/Pinia is comparable |
| Tauri compatibility | Both work equally well in Tauri's webview | Both work equally well |
| Hiring / contribution | More contributors know React | Fewer contributors know Vue |
| Bundle size (minimal) | ~45 KB gzipped (React 18) | ~33 KB gzipped (Vue 3) |
| Svelte consideration | — | Svelte is smaller (~2 KB) but has fewer dashboard libraries |

**Decision:** React + Tailwind for v0.3–v0.4, with the acknowledgment that Svelte is a valid alternative if bundle size becomes critical. The decision is not irreversible — the frontend is a thin layer over a REST API, and swapping frameworks would not affect the backend.

**Alternative note:** The existing `00-06_web_pwa_desktop.md` suggests Vanilla JS / Lit for the PWA. That recommendation applies to the **chat-focused PWA** (which needs minimal dependencies). This management dashboard has richer UI requirements (data tables, log streaming, charts) where a component framework adds more value than it costs.

### 6.3 Why Tauri over Electron for Desktop

| Factor | Tauri | Electron |
|--------|-------|----------|
| Bundle size | ~5–10 MB | ~150–200 MB |
| Runtime memory | ~50 MB | ~200 MB (Chromium) |
| Backend language | Rust (safe, fast, native FFI) | Node.js |
| GPU monitoring | Direct `nvidia-smi` calls via Rust; low overhead | Child process spawning; higher overhead |
| System tray | Built-in | Requires `electron-tray` or custom code |
| Auto-updates | Built-in | Requires `electron-updater` |
| Security | Rust memory safety; IPC allowlist | Full Node.js access in renderer if misconfigured |
| Kimari alignment | Rust can call llama.cpp C FFI directly (future) | HTTP-only integration |
| Webview | Uses OS webview (WebKitGTK/WebView2/WebKit) | Bundles Chromium |

**Decision:** Tauri. Kimari targets consumer GPUs with limited VRAM (6–8 GB). An Electron app consuming 200 MB of RAM alongside a model that needs 5+ GB of VRAM is wasteful. Tauri's Rust backend also opens the door to direct llama.cpp FFI bindings in a future version, eliminating the subprocess layer entirely.

---

## 7. File Structure (Planned)

This is the intended layout once v0.3 ships. Nothing here exists yet.

```
kimari-local-ai/
├── kimari/
│   ├── api/                    # NEW: FastAPI application
│   │   ├── __init__.py
│   │   ├── app.py              # FastAPI app factory, middleware, CORS
│   │   ├── auth.py             # Token generation and validation
│   │   ├── routes/
│   │   │   ├── status.py       # GET /api/status
│   │   │   ├── server.py       # POST /api/start, POST /api/stop
│   │   │   ├── models.py       # GET /api/models, POST /api/pull/{id}
│   │   │   ├── logs.py         # GET /api/logs (JSON + SSE)
│   │   │   ├── bench.py        # POST /api/bench
│   │   │   └── config.py       # GET /api/config, PATCH /api/config
│   │   └── schemas.py          # Pydantic request/response models
│   ├── cli/
│   │   └── main.py             # Updated: add "kimari api" subcommand
│   └── ...
├── web/                        # NEW: Frontend (v0.3+)
│   ├── package.json
│   ├── vite.config.ts
│   ├── index.html
│   ├── src/
│   │   ├── App.tsx
│   │   ├── api.ts              # Fetch wrapper with token auth
│   │   ├── components/
│   │   │   ├── StatusCard.tsx
│   │   │   ├── ServerControls.tsx
│   │   │   ├── ModelTable.tsx
│   │   │   ├── LogViewer.tsx
│   │   │   ├── BenchResults.tsx
│   │   │   └── OpenWebUIButton.tsx
│   │   └── hooks/
│   │       ├── useStatus.ts    # Poll /api/status every 5s
│   │       └── useSSE.ts       # SSE stream for logs
│   └── public/
│       ├── manifest.json       # PWA manifest (v0.4)
│       └── sw.js               # Service worker (v0.4)
├── tests/
│   ├── test_api.py             # NEW: API endpoint tests
│   └── ...
└── ...
```

---

## 8. Open Questions

These are unresolved decisions that should be settled before v0.2 implementation begins:

1. **Should the FastAPI server be a long-running daemon or started on demand?**
   - Option A: `kimari api` starts it; user keeps it running alongside llama-server.
   - Option B: `kimari start --with-api` starts both llama-server and the API server together.
   - Recommendation: Option A. Separation of concerns. The API server is lightweight and independent.

2. **Should the frontend be served by FastAPI or a separate dev server?**
   - In production (installed app): FastAPI serves the built static files from `web/dist/`.
   - In development: Vite dev server on port 5173, proxying API requests to FastAPI on 11436.

3. **How to handle long-running tasks (benchmarks, model pulls)?**
   - Option A: In-process background tasks with `asyncio.create_task`.
   - Option B: A simple in-memory task registry with status polling.
   - Recommendation: Option B for v0.2–v0.3. If multi-worker deployment is ever needed, migrate to a proper task queue.

4. **Token storage — file vs. environment variable?**
   - File (`.kimari/api-token`): Survives restarts, no env pollution.
   - Environment variable (`KIMARI_API_TOKEN`): Easier for headless/CI use.
   - Recommendation: Both. File is the primary source; env var overrides it if set.

5. **Should `/api/start` block until READY or return immediately?**
   - Recommendation: Return `202 Accepted` immediately. The client polls `/api/status` for readiness. This avoids HTTP timeouts on slow model loads.

---

## 9. What This Plan Does NOT Promise

- No chat interface in the dashboard (that's the PWA track in [00-06](00-06_web_pwa_desktop.md)).
- No multi-user support. Kimari is a single-user local tool.
- No remote access. The API binds to localhost only.
- No real-time GPU utilization graphs (that's v1.0 / Tauri territory).
- No model fine-tuning, RAG, or tool-calling UI (those features don't exist in the CLI yet either).
- No mobile app. The PWA is "installable" but not a native app.

---

*This is a planning document. Nothing described here is implemented. All endpoints, file structures, and technical decisions are subject to change during implementation.*
