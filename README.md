<p align="center">
  <img src="docs/assets/kimari-logo.png" alt="Kimari" width="200">
</p>

<h1 align="center">Kimari</h1>

<p align="center">
  <strong>Local AI for Consumer GPUs</strong>
</p>

<p align="center">
  <a href="LICENSE">MIT License</a> ·
  <a href="https://github.com/smouj/kimari-local-ai">GitHub</a> ·
  <a href="https://smouj.github.io/kimari-local-ai/"><img src="https://img.shields.io/badge/website-kimari-00d4aa.svg" alt="Kimari Website"></a> ·
  <a href="https://x.com/smouj013"><img src="https://img.shields.io/badge/X-@smouj013-black.svg" alt="X"></a> ·
  [![CI](https://github.com/smouj/kimari-local-ai/actions/workflows/ci.yml/badge.svg)](https://github.com/smouj/kimari-local-ai/actions/workflows/ci.yml)
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-blue.svg" alt="MIT License"></a>
  <a href="https://www.python.org/downloads/"><img src="https://img.shields.io/badge/python-3.10+-green.svg" alt="Python 3.10+"></a>
  <a href="https://developer.nvidia.com/cuda-downloads"><img src="https://img.shields.io/badge/cuda-11.8+-76b900.svg" alt="CUDA 11.8+"></a>
  <a href="https://github.com/ggerganov/llama.cpp"><img src="https://img.shields.io/badge/runtime-llama.cpp-orange.svg" alt="llama.cpp"></a>
  <a href="#"><img src="https://img.shields.io/badge/API-OpenAI--compatible-00d4aa.svg" alt="OpenAI-compatible API"></a>
</p>

---

## Overview

Kimari is an open-source framework for running powerful language models locally on consumer-grade NVIDIA GPUs. No cloud. No subscriptions. Your data stays on your machine.

**Important:** Kimari is the *framework*, not the model. Kimari-4B is a **target model** currently under development (planned — not released yet). Until the final fine-tuned weights are released, Kimari can run any compatible GGUF model (Qwen3, SmolLM3, Llama 3.2, etc.) on consumer hardware — specifically **NVIDIA GTX 1060 (6 GB)** and **GTX 1080 (8 GB)** — delivering maximum useful intelligence per GiB of VRAM through intelligent quantization and the KimariFit scoring system.

Built on top of [llama.cpp](https://github.com/ggerganov/llama.cpp), Kimari provides an OpenAI-compatible API, a full-featured CLI, and integrations for Open WebUI and Continue (VS Code / JetBrains).

## Project Status

> **Kimari Local AI v0.1.4-alpha**

### ✅ Works Today
- CLI: `doctor`, `info`, `start`, `stop`, `status`, `chat`, `bench`, `fit`, `models`, `profiles`, `logs`, `pull`
- Config management: `config path`, `config show`, `config validate`, `config migrate`
- Modular Python package (`kimari/`) — installable via `pip install -e .`
- llama.cpp runtime with CUDA acceleration
- OpenAI-compatible API (`http://127.0.0.1:11435/v1`)
- Model download via `kimari pull` with resume and SHA256 verification
- Profile overrides: `--model`, `--host`, `--port`, `--ctx`
- JSON output for all commands (`--json`) — IDE and agent friendly
- Open WebUI integration (Docker)
- Continue.dev IDE integration
- KimariFit scoring system with `--vram` override
- Benchmark framework with TTFT measurement
- `kimari bench --vram` override for systems without GPU detection
- Security warnings for `0.0.0.0` binding

### 🔨 Planned
- **Kimari-4B** — Target model under development. Weights not yet available.
- **Local REST API** — FastAPI-based API for programmatic access (v0.2)
- **Web Dashboard** — Minimal status/controls UI (v0.3)
- **VRAM reporting** — Real-time memory usage in `kimari status`

### ❌ Not Included Yet
- Multi-model serving
- RAG support
- Tool/function calling
- Authentication/authorization for API
- Fine-tuning pipeline
- macOS / CPU-only support

## Quick Start

### Prerequisites

- NVIDIA GPU (GTX 1060 6GB or better recommended)
- CUDA Toolkit 11.8+
- Python 3.10+
- Git
- 8 GB+ system RAM

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/smouj/kimari-local-ai.git
cd kimari-local-ai

# 2. Install (option A: pip install)
pip install -e .

# 3. Run system diagnostics
kimari doctor

# 4. Download a test model
kimari pull test

# 5. Start the server
kimari start --profile test

# 6. Chat with the model
kimari chat "Hello, Kimari!"
```

### Alternative: Manual install (no pip)

```bash
pip install -r cli/requirements.txt
python -m kimari.cli.main doctor
python -m kimari.cli.main pull test
python -m kimari.cli.main start --profile test
```

> **Note:** The `test` profile is the only profile usable out of the box. The `gtx1060` and `gtx1080` profiles require the Kimari-4B GGUF model (not yet published) — or you can use `--model` to point to your own GGUF file.

### Linux (Ubuntu 22.04+)

```bash
# Install system dependencies
sudo apt update
sudo apt install -y build-essential cmake nvidia-cuda-toolkit git

# Build llama.cpp with CUDA support
bash scripts/linux/build-llamacpp-cuda.sh

# Install Kimari
pip install -e .

# Run diagnostics
kimari doctor
```

### Development Setup

```bash
# Install with dev dependencies
pip install -e ".[dev]"

# Or use the setup script
bash scripts/linux/install-dev.sh

# Verify environment
python scripts/linux/check-env.py
```

## GPU Profiles

Pre-configured settings optimized for specific GPU models. No manual tuning required.

| Profile | GPU | VRAM | Quantization | Context | Host |
|---------|-----|------|-------------|---------|------|
| `gtx1060` | GTX 1060 | 6 GB | Q4_K_M | 8,192 | 127.0.0.1 |
| `gtx1080` | GTX 1080 | 8 GB | Q5_K_M | 16,384 | 127.0.0.1 |
| `turbo` | 6 GB+ | 6 GB | IQ4_XS | 8,192 | 127.0.0.1 |
| `test` | Any 6 GB+ | 6 GB | Q4_K_M | 4,096 | 127.0.0.1 |
| `docker` | Open WebUI | 6 GB | Q4_K_M | 4,096 | 0.0.0.0 |

## CLI Commands

```bash
# Diagnostics and info
kimari doctor                                        # System diagnostics (CUDA, GPU, llama-server)
kimari doctor --json                                 # JSON output for automation/IDEs
kimari info                                          # Installation info (version, paths, profiles)
kimari info --json                                   # JSON info output

# Server management
kimari start --profile gtx1080                       # Start server
kimari start --profile test --dry-run                # Preview command without running
kimari start --profile test --host 0.0.0.0 --port 8080  # Override host and port
kimari start --profile gtx1080 --daemon              # Start in background
kimari stop                                          # Stop server
kimari status                                        # Check server status
kimari status --json                                 # JSON status output
kimari logs                                          # Show server logs
kimari logs --follow                                 # Tail logs

# Models
kimari pull test                                      # Download test model
kimari pull recommended                               # Download recommended model
kimari pull --all                                     # Download all models
kimari pull --list                                    # List available models
kimari pull test --dry-run                            # Preview download
kimari models                                         # List downloaded models
kimari models --json                                  # JSON output
kimari models --downloaded                            # Only downloaded models

# Profiles and configuration
kimari profiles                                       # List GPU profiles
kimari profiles --json                                # JSON output
kimari config path                                    # Print config file path
kimari config show                                    # Show full configuration
kimari config show --json                             # JSON config output
kimari config validate                                # Validate against schema
kimari config migrate                                 # Migrate to current version
kimari config migrate --dry-run                       # Preview migration

# Chat and benchmarks
kimari chat "Your message here"                       # Send a single message
kimari chat                                          # Interactive chat mode
kimari bench --profile gtx1080                        # Run benchmarks (tokens/s, TTFT)
kimari bench --profile gtx1080 --vram 8.0              # Override VRAM manually
kimari bench --profile test --json                    # JSON benchmark output
kimari fit --model models/file.gguf --ctx 8192        # KimariFit score
kimari fit --model models/file.gguf --vram 8.0        # Override VRAM manually
```

## KimariFit Score

The KimariFit formula measures useful intelligence density per GiB of VRAM. It answers: *"Will this model run well on my GPU?"*

```
M_total ≈ S_GGUF + C/9709 + overhead
```

| Score | Rating | Meaning |
|-------|--------|---------|
| 90–100 | 🟢 Optimal | Model fits perfectly. Best performance expected. |
| 70–89 | 🟡 Good | Minor compromises. Works well for most tasks. |
| 50–69 | 🟠 Usable | Significant quantization. Acceptable for basic use. |
| < 50 | 🔴 Poor | Will be slow or OOM. Not recommended. |

```bash
kimari fit --model models/your-model.gguf --ctx 8192
kimari fit --model models/your-model.gguf --vram 8.0  # Manual VRAM override
```

See [docs/00-02_kimarifit_formula.md](docs/00-02_kimarifit_formula.md) for the full formula.

## Architecture

```
┌─────────────────────────────────────────────┐
│  GGUF Quantized Model (any compatible GGUF) │
├─────────────────────────────────────────────┤
│  llama.cpp Runtime + CUDA Acceleration      │
├─────────────────────────────────────────────┤
│  llama-server (OpenAI-compatible API)       │
│  http://127.0.0.1:11435/v1                  │
├─────────────────────────────────────────────┤
│  CLI · Open WebUI · Continue (IDE)          │
└─────────────────────────────────────────────┘
```

- **CLI** — Python 3.10+ command-line interface for all operations
- **Open WebUI** — Full-featured web chat interface (Docker)
- **Continue** — AI coding assistant for VS Code and JetBrains
- **Local API** — Planned FastAPI REST API (v0.2)
- **Web Dashboard** — Planned minimal UI (v0.3)

## Documentation

| Document | Description |
|----------|-------------|
| [Getting Started](GETTING_STARTED.md) | 10-minute quick start guide |
| [Project Structure](docs/PROJECT_STRUCTURE.md) | Codebase organization and modules |
| [Product Vision](docs/00-01_product_vision.md) | Project goals, philosophy, and differentiation |
| [KimariFit Formula](docs/00-02_kimarifit_formula.md) | Hardware scoring system explained |
| [Architecture](docs/00-03_architecture.md) | System design and data flow |
| [Comparison](docs/COMPARISON.md) | Kimari vs. Ollama, LM Studio, and others |
| [Web UI Plan](docs/WEB_UI_PLAN.md) | Future web dashboard roadmap |
| [Roadmap](ROADMAP.md) | Version milestones and plans |
| [Changelog](CHANGELOG.md) | Version history |
| [Security](SECURITY.md) | Security policy and best practices |
| [Privacy](PRIVACY.md) | Privacy policy (no telemetry) |

## Open WebUI Integration

```bash
# 1. Start Kimari with the docker profile (listens on 0.0.0.0)
kimari start --profile docker --daemon

# 2. Launch Open WebUI
make webui-up

# 3. Open in browser → http://localhost:3000
```

> ⚠️ **Security Warning:** Binding to `0.0.0.0` makes the API accessible from other machines on your network. Only use this on trusted local networks. See [SECURITY.md](SECURITY.md) for details.

## Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

This project is licensed under the MIT License — see [LICENSE](LICENSE) for details.

Model weights are not included in this repository. See [MODEL_LICENSES.md](MODEL_LICENSES.md) for information about model licensing.

## Acknowledgments

- [llama.cpp](https://github.com/ggerganov/llama.cpp) — Inference runtime engine
- [GGUF format](https://github.com/ggerganov/ggml) — Efficient model format
- [Ollama](https://github.com/ollama/ollama) — Inspiration for open-source AI tooling
- [Continue](https://continue.dev) — Open-source AI code assistant
- [Open WebUI](https://github.com/open-webui/open-webui) — Web interface for LLMs

---

<p align="center">
  Created by <a href="https://x.com/smouj013">Smouj</a> · <a href="https://github.com/smouj/kimari-local-ai">GitHub</a>
</p>
