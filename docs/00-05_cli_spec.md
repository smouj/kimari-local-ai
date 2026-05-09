# Kimari CLI Specification

## Document: 00-05 CLI Specification
**Version:** 0.1.0
**Status:** Draft
**Last Updated:** 2025

---

## Overview

The Kimari CLI (`kimari_cli.py`) is the primary interface for managing and interacting with the Kimari local AI platform. It provides commands for system diagnostics, server management, chatting, benchmarking, and configuration.

## Commands

### `kimari doctor`

Run system diagnostics to check if Kimari is ready to run.

```bash
cd cli && python kimari_cli.py doctor
```

**What it checks:**
1. Operating system and architecture
2. NVIDIA GPU (name, VRAM via nvidia-smi)
3. NVIDIA driver version
4. CUDA availability (nvcc)
5. llama-server binary in PATH
6. Model file existence
7. Port availability
8. Config file validity
9. Recommended GPU profile

**Output format:**
```
Kimari Doctor v0.1.0

  [OK]   OS: Linux x86_64
  [OK]   GPU: NVIDIA GTX 1080 (8 GB)
  [OK]   Driver: 535.129.03
  [OK]   CUDA: Available (nvcc 12.2)
  [WARN] llama-server: not found in PATH
  [OK]   Model: models/Kimari-4B-Q5_K_M.gguf (2.75 GB)
  [OK]   Port: 11435 available
  [OK]   Config: config/kimari.profiles.json
  [OK]   Recommended profile: gtx1080

  Result: 6 OK, 1 WARN, 0 FAIL
```

**Exit codes:**
- 0: All checks pass
- 1: Warnings or failures detected

---

### `kimari start --profile <name>`

Start llama-server with the specified GPU profile.

```bash
# Use default profile
cd cli && python kimari_cli.py start

# Use specific profile
cd cli && python kimari_cli.py start --profile gtx1080
cd cli && python kimari_cli.py start -p turbo
```

**Behavior:**
1. Load profile from config
2. Validate model file exists
3. Check port is available
4. Build llama-server command with profile parameters
5. Start server in background
6. Save PID to `server/kimari.pid`
7. Poll `/health` endpoint until ready (30s timeout)
8. Print success message with usage hints

**Options:**
| Option | Short | Description | Default |
|--------|-------|-------------|---------|
| `--profile` | `-p` | GPU profile name | Config default |

---

### `kimari stop`

Stop the running llama-server process.

```bash
cd cli && python kimari_cli.py stop
```

**Behavior:**
1. Read PID from `server/kimari.pid`
2. Send SIGTERM to process group
3. Wait 2 seconds
4. Send SIGKILL if still running
5. Clean up PID file

**Fallback:** If no PID file, search for process on the default port.

---

### `kimari status`

Check the current status of the Kimari server.

```bash
cd cli && python kimari_cli.py status
```

**Output:**
```
Kimari Server Status

  [OK]   Process running (PID: 12345)
  [OK]   Health: healthy
  [INFO] Model: Kimari-4B-Q5_K_M.gguf
  [INFO] Context: 16384 tokens
```

---

### `kimari chat "<message>"`

Send a chat message and receive a response.

```bash
# Basic chat
cd cli && python kimari_cli.py chat "Hello, Kimari!"
cd cli && python kimari_cli.py chat "Explain async/await in Python"

# With specific profile
cd cli && python kimari_cli.py chat "Write a REST API" --profile gtx1080
```

**Behavior:**
1. Build chat completion request with system prompt
2. Send POST to `/v1/chat/completions`
3. Display the assistant's response
4. Show token usage statistics

**Options:**
| Option | Short | Description | Default |
|--------|-------|-------------|---------|
| `--profile` | `-p` | GPU profile name | Config default |

---

### `kimari bench --profile <name>`

Run a performance benchmark measuring tokens per second and time to first token.

```bash
cd cli && python kimari_cli.py bench --profile gtx1060
cd cli && python kimari_cli.py bench --profile gtx1080
```

**Measured metrics:**
- Time to first token (TTFT) in milliseconds
- Total generation time in seconds
- Tokens generated
- Tokens per second (throughput)

**Output:**
```
Kimari Benchmark — GTX 1060 (6 GB)

  Results:
  Time to first token: 850 ms
  Generation time:     12.45 s
  Tokens generated:    187
  Speed:               15.0 tokens/s

  [OK] Performance: 15.0 t/s — Good
```

**Options:**
| Option | Short | Description | Default |
|--------|-------|-------------|---------|
| `--profile` | `-p` | GPU profile name | Config default |

---

### `kimari fit --model <path> --ctx <size>`

Calculate the KimariFit score for a model on your hardware.

```bash
# Auto-detect GPU
cd cli && python kimari_cli.py fit --model models/Kimari-4B-Q4_K_M.gguf --ctx 8192

# Manual VRAM specification
cd cli && python kimari_cli.py fit --model models/Kimari-4B-Q4_K_M.gguf --ctx 8192 --vram 6.0

# Different context sizes
cd cli && python kimari_cli.py fit -m models/Kimari-4B-Q5_K_M.gguf -c 16384
```

**Options:**
| Option | Short | Required | Description | Default |
|--------|-------|----------|-------------|---------|
| `--model` | `-m` | Yes | Path to GGUF model | — |
| `--ctx` | `-c` | No | Context size in tokens | 8192 |
| `--vram` | — | No | GPU VRAM in GB | Auto-detect |

---

### `kimari models`

List all available GGUF model files in the `models/` directory.

```bash
cd cli && python kimari_cli.py models
```

**Output:**
```
Available Models

  Kimari-4B-Q4_K_M.gguf  (2.25 GB)
  Kimari-4B-Q5_K_M.gguf  (2.75 GB)
  Kimari-4B-IQ4_XS.gguf  (1.90 GB)

  Total: 3 model(s)
```

---

### `kimari profiles`

List all configured GPU profiles.

```bash
cd cli && python kimari_cli.py profiles
```

**Output:**
```
GPU Profiles
Default: gtx1060

  gtx1060 (default)
    GPU:         GTX 1060 (6 GB)
    Model:       models/Kimari-4B-Q4_K_M.gguf
    Context:     8,192 tokens
    Quantization:Q4_K_M
    Batch:       256 (ubatch: 128)
    Port:        11435
    Notes:       Base profile. Optimal quality/speed balance for 6 GB VRAM.

  gtx1080
    GPU:         GTX 1080 (8 GB)
    ...
```

---

## Global Options

| Option | Description |
|--------|-------------|
| `--version` | Show version and exit |
| `--help` | Show help message |

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | Error or warning |
| 2 | Invalid arguments |

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `CUDA_VISIBLE_DEVICES` | GPU device index | 0 |
| `KIMARI_ROOT` | Project root directory | Auto-detected |
| `KIMARI_CONFIG` | Path to config file | `config/kimari.profiles.json` |
| `KIMARI_PID_FILE` | Path to PID file | `server/kimari.pid` |

## Design Principles

1. **Fail Fast** — Validate inputs and dependencies before starting operations
2. **Clear Errors** — Show what went wrong and how to fix it
3. **No Surprises** — Print what's happening at each step
4. **Colored Output** — Green for OK, yellow for warnings, red for errors
5. **Zero Dependencies** — Only requires `requests` beyond stdlib

---

*See [00-02_kimarifit_formula.md](00-02_kimarifit_formula.md) for details on the fit scoring algorithm.*
