# Kimari Architecture

## Document: 00-03 System Architecture
**Version:** 0.1.0
**Status:** Draft
**Last Updated:** 2025

---

## Overview

Kimari follows a layered architecture designed for simplicity, extensibility, and reliability. The system is built around three core layers: the user interface layer, the Kimari management layer, and the inference runtime layer.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    USER INTERFACE LAYER                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐  │
│  │  Kimari CLI  │  │  Open WebUI  │  │ Continue (IDE)   │  │
│  │  (Python)    │  │  (Docker)    │  │ (VS Code/JB)     │  │
│  └──────┬───────┘  └──────┬───────┘  └────────┬─────────┘  │
│         │                 │                    │            │
│         └────────────────┬┴────────────────────┘            │
│                          │                                  │
│                   OpenAI-Compatible API                     │
│                    (HTTP/JSON)                              │
└──────────────────────────┬──────────────────────────────────┘
                           │
┌──────────────────────────┬──────────────────────────────────┐
│                KIMARI MANAGEMENT LAYER                      │
│  ┌────────────┐  ┌──────────────┐  ┌────────────────────┐  │
│  │   Config   │  │   Process    │  │    Health Check    │  │
│  │   Engine   │  │   Manager    │  │    & Monitor       │  │
│  └────────────┘  └──────────────┘  └────────────────────┘  │
│  ┌────────────┐  ┌──────────────┐  ┌────────────────────┐  │
│  │  GPU       │  │   KimariFit  │  │    Benchmark       │  │
│  │  Detector  │  │   Scorer     │  │    Runner          │  │
│  └────────────┘  └──────────────┘  └────────────────────┘  │
└──────────────────────────┬──────────────────────────────────┘
                           │
┌──────────────────────────┬──────────────────────────────────┐
│                 INFERENCE RUNTIME LAYER                     │
│  ┌────────────────────────────────────────────────────┐    │
│  │              llama-server (llama.cpp)               │    │
│  │  ┌─────────┐ ┌─────────┐ ┌──────────┐ ┌────────┐  │    │
│  │  │ Model   │ │ KV      │ │ Sampling │ │ Token  │  │    │
│  │  │ Loader  │ │ Cache   │ │ Pipeline │ │ Stream │  │    │
│  │  └─────────┘ └─────────┘ └──────────┘ └────────┘  │    │
│  └────────────────────────┬───────────────────────────┘    │
│                           │                                 │
│  ┌────────────────────────┴───────────────────────────┐    │
│  │              CUDA / Vulkan Backend                  │    │
│  └────────────────────────┬───────────────────────────┘    │
└──────────────────────────┬──────────────────────────────────┘
                           │
┌──────────────────────────┬──────────────────────────────────┐
│                   HARDWARE LAYER                            │
│  ┌────────────────────────────────────────────────────┐    │
│  │  NVIDIA GPU (GTX 1060 / GTX 1080 / RTX Series)    │    │
│  │  VRAM: 6–8 GB                                       │    │
│  └────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
```

## Components

### 1. Kimari CLI (`cli/kimari_cli.py`)

The primary user interface. Written in Python 3.10+.

**Responsibilities:**
- Parse and route user commands
- Load and validate configuration
- Detect system capabilities (GPU, CUDA, etc.)
- Manage llama-server process lifecycle
- Calculate KimariFit scores
- Run benchmarks
- Provide colored, user-friendly output

**Key Design Decisions:**
- Python chosen for readability and ecosystem
- `subprocess` for process management (no daemon dependency)
- `requests` for HTTP communication (lightweight)
- `argparse` for CLI parsing (no external deps)
- Colors via ANSI escape codes (no `rich` dependency)

### 2. Configuration Engine

Manages GPU profiles and system settings.

**File:** `config/kimari.profiles.json`

**Responsibilities:**
- Store GPU profile definitions
- Provide default settings per hardware tier
- Allow custom profiles for unlisted GPUs
- Store default profile selection

**Data Structure:**
```json
{
  "version": "1.0.0",
  "default_profile": "gtx1060",
  "profiles": {
    "<profile_name>": {
      "name": "Human-readable name",
      "model": "path/to/model.gguf",
      "ctx": 8192,
      "batch": 256,
      "ubatch": 128,
      "cache_type_k": "f16",
      "cache_type_v": "f16",
      "host": "127.0.0.1",
      "port": 11435,
      "gpu_layers": "all",
      "threads": 4,
      "vram_total_gb": 6.0,
      "vram_safe_gb": 5.2,
      "quantization": "Q4_K_M",
      "notes": "Description"
    }
  }
}
```

### 3. Process Manager

Manages the llama-server lifecycle.

**Responsibilities:**
- Start llama-server with correct parameters
- Save PID for later management
- Handle graceful shutdown (SIGTERM → SIGKILL)
- Redirect logs to `server/kimari.log`
- Detect and prevent port conflicts

### 4. GPU Detector

Detects NVIDIA GPU capabilities.

**Methods:**
- Parse `nvidia-smi` output for GPU name, VRAM, driver version
- Check `nvcc` for CUDA compilation support
- Map GPU names to known profiles

### 5. KimariFit Scorer

Calculates hardware fit scores.

**Algorithm:** See [00-02_kimarifit_formula.md](00-02_kimarifit_formula.md)

### 6. Health Monitor

Periodically checks server health.

**Endpoints used:**
- `GET /health` — Server health
- `GET /v1/models` — Available models
- `GET /metrics` — Performance metrics (if available)

### 7. llama-server (llama.cpp)

The inference runtime. Not modified by Kimari; used as a library.

**Key parameters controlled by Kimari:**
- `-m` — Model path
- `-c` — Context size
- `-b` — Batch size
- `-ub` — Ubatch size
- `-ngl` — GPU layers
- `-t` — Thread count
- `--flash-attn` — Flash attention
- `--cache-type-k/v` — KV cache quantization
- `--host` / `--port` — Server binding

## Data Flow

### Starting the Server

```
User: make start-1060
  → Makefile: cd cli && python kimari_cli.py start --profile gtx1060
    → CLI: Load config/kimari.profiles.json
    → CLI: Resolve model path
    → CLI: Validate model exists
    → CLI: Check port availability
    → CLI: Build llama-server command
    → CLI: Launch llama-server (subprocess, background)
    → CLI: Save PID to server/kimari.pid
    → CLI: Poll /health until 200 OK
    → CLI: Print success message
```

### Chatting

```
User: kimari chat "Hello"
  → CLI: Load default profile config
  → CLI: POST /v1/chat/completions
    → llama-server: Receive request
    → llama-server: Tokenize input
    → llama-server: Run inference (CUDA)
    → llama-server: Stream/compose response
    → llama-server: Return JSON response
  → CLI: Extract content
  → CLI: Display to user with token counts
```

### Running Diagnostics

```
User: make doctor
  → CLI: Detect OS
  → CLI: Run nvidia-smi → GPU info
  → CLI: Check nvcc → CUDA availability
  → CLI: Check which llama-server → binary found
  → CLI: Check model file exists
  → CLI: Check port availability
  → CLI: Load config file
  → CLI: Determine recommended profile
  → CLI: Display results with OK/WARN/FAIL
```

## Error Handling

| Scenario | Handling |
|----------|----------|
| Model not found | Print error, suggest downloading model |
| Port in use | Detect existing PID, suggest stopping |
| llama-server not found | Print error, suggest building/installing |
| No NVIDIA GPU | Warn but continue (CPU-only mode) |
| Server crash during start | Show last 20 lines of log |
| Request timeout | Print timeout error with suggestions |
| Invalid JSON response | Print raw response for debugging |
| Config file missing | Create default config |

## Security Model

- Server binds to `127.0.0.1` by default (no external access)
- No authentication required for local use
- No data is sent externally (zero telemetry)
- No logging of conversations by Kimari itself
- Port can be changed via profile configuration

## Extension Points

1. **New GPU Profiles** — Add entries to `config/kimari.profiles.json`
2. **New CLI Commands** — Add handlers to `kimari_cli.py`
3. **New Benchmark Prompts** — Add files to `benchmarks/prompts/`
4. **New Skills** — Add files to `skills/`
5. **New Evaluation Cases** — Add entries to `eval/kimari_eval.jsonl`
6. **Custom Frontend** — Use the OpenAI-compatible API

---

*This architecture is designed for v0.1. Future versions may introduce more sophisticated components.*
