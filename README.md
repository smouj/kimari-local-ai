<p align="center">
  <img src="docs/assets/kimari-logo.png" alt="Kimari" width="180">
</p>

<h1 align="center">Kimari</h1>

<p align="center">
  <strong>Local AI for Consumer GPUs</strong><br>
  <em>No cloud · No subscriptions · Your data stays on your machine</em>
</p>

<p align="center">
  <a href="https://github.com/smouj/kimari-local-ai/actions/workflows/ci.yml">
    <img src="https://github.com/smouj/kimari-local-ai/actions/workflows/ci.yml/badge.svg" alt="CI">
  </a>
  <a href="LICENSE">
    <img src="https://img.shields.io/badge/license-MIT-00d4aa.svg" alt="MIT License">
  </a>
  <img src="https://img.shields.io/badge/python-3.10+-2ea043.svg" alt="Python 3.10+">
  <img src="https://img.shields.io/badge/cuda-11.8+-76b900.svg" alt="CUDA 11.8+">
  <img src="https://img.shields.io/badge/runtime-llama.cpp-orange.svg" alt="llama.cpp">
  <img src="https://img.shields.io/badge/API-OpenAI--compatible-00d4aa.svg" alt="OpenAI-compatible API">
  <img src="https://img.shields.io/badge/version-v0.1.5--alpha-9b59b6.svg" alt="v0.1.5-alpha">
  <a href="https://github.com/smouj/kimari-local-ai">
    <img src="https://img.shields.io/github/stars/smouj/kimari-local-ai?style=social" alt="GitHub stars">
  </a>
</p>

---

## 🌟 Overview

Kimari is an open-source framework for running powerful language models locally on consumer-grade NVIDIA GPUs. It delivers maximum useful intelligence per GiB of VRAM through intelligent quantization, the KimariFit scoring system, and pre-tuned GPU profiles — so you don't have to be an ML engineer to get great performance from older hardware.

> **⚠️ Alpha Software** — Kimari Local AI is in active early development (v0.1.5-alpha). Expect rough edges, breaking changes between versions, and missing features. The project is usable today but not yet production-ready.

**Important:** Kimari is the *framework*, not the model. **Kimari-4B** is a target model currently under development — it is **not yet released**. Until the final fine-tuned weights are available, Kimari can run any compatible GGUF model (Qwen3, SmolLM3, Llama 3.2, TinyLlama, etc.) on consumer hardware — specifically **NVIDIA GTX 1060 (6 GB)** and **GTX 1080 (8 GB)**.

Built on top of [llama.cpp](https://github.com/ggerganov/llama.cpp), Kimari provides an OpenAI-compatible API, a full-featured CLI, and integrations for Open WebUI and Continue (VS Code / JetBrains).

---

## 📊 Project Status

> **Kimari Local AI v0.1.5-alpha**

### ✅ Works Today

- **CLI** — `doctor`, `info`, `start`, `stop`, `status`, `chat`, `bench`, `fit`, `models`, `profiles`, `logs`, `pull`
- **Config management** — `config path`, `config show`, `config validate`, `config migrate`
- **Modular Python package** (`kimari/`) — installable via `pip install -e .`
- **llama.cpp runtime** with CUDA acceleration
- **OpenAI-compatible API** — `http://127.0.0.1:11435/v1`
- **Model downloads** — `kimari pull` with resume and SHA256 verification
- **Profile overrides** — `--model`, `--host`, `--port`, `--ctx`
- **JSON output** — `--json` flag for all commands (IDE and agent friendly)
- **Background mode** — `--daemon` flag for `kimari start`
- **Open WebUI integration** (Docker)
- **Continue.dev IDE integration** (VS Code / JetBrains)
- **KimariFit scoring system** with `--vram` override
- **Benchmark framework** with TTFT measurement
- **Security warnings** for `0.0.0.0` binding
- **Experimental AMD ROCm** build support

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

---

## 🚀 Quick Start

### Prerequisites

| Requirement | Minimum |
|-------------|---------|
| NVIDIA GPU | GTX 1060 6 GB or better |
| CUDA Toolkit | 11.8+ |
| Python | 3.10+ |
| System RAM | 8 GB+ |
| Git | Any recent version |

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/smouj/kimari-local-ai.git
cd kimari-local-ai

# 2. Install the package
pip install -e .

# 3. Run system diagnostics
kimari doctor

# 4. Download a test model
kimari pull test

# 5. Start the server (uses 'test' profile by default)
kimari start

# 6. Chat with the model
kimari chat "Hello, Kimari!"
```

> **Note:** The `test` profile is the default during alpha, using TinyLlama 1.1B. After `kimari pull test`, `kimari start` works without specifying `--profile`. The `gtx1060` and `gtx1080` profiles are ready for when Kimari-4B is released — or you can use `--model` to point to your own GGUF file.

### Linux (Ubuntu 22.04+)

```bash
# Install system dependencies
sudo apt update
sudo apt install -y build-essential cmake nvidia-cuda-toolkit git

# Build llama.cpp with CUDA support
bash scripts/linux/build-llamacpp-cuda.sh

# Install Kimari
pip install -e .

# Verify setup
kimari doctor
```

### Development Setup

```bash
# Install with dev dependencies
pip install -e ".[dev]"

# Or use the setup script
bash scripts/linux/install-dev.sh

# Verify environment
python scripts/common/check-env.py
```

### Manual Install (no pip)

If you prefer not to use `pip install -e .`, you can run Kimari directly:

```bash
pip install -r cli/requirements.txt
python -m kimari.cli.main doctor
python -m kimari.cli.main pull test
python -m kimari.cli.main start
```

---

## 🎮 GPU Profiles

Pre-configured settings optimized for specific GPU models. No manual tuning required — just pick a profile and go.

| Profile | GPU | VRAM | Quantization | Context | Host | Status |
|---------|-----|------|-------------|---------|------|--------|
| `test` ⭐ | Any 6 GB+ | 6 GB | Q4_K_M | 4,096 | `127.0.0.1` | **Default (alpha)** |
| `gtx1060` | GTX 1060 | 6 GB | Q4_K_M | 8,192 | `127.0.0.1` | Requires Kimari-4B |
| `gtx1080` | GTX 1080 | 8 GB | Q5_K_M | 16,384 | `127.0.0.1` | Requires Kimari-4B |
| `turbo` | 6 GB+ | 6 GB | IQ4_XS | 8,192 | `127.0.0.1` | Requires Kimari-4B |
| `docker` | Open WebUI | 6 GB | Q4_K_M | 4,096 | `0.0.0.0` | ⚠️ Network-exposed |

> ⭐ The `test` profile is the default during alpha. When Kimari-4B is published, `gtx1060` will become the new default.

---

## ⌨️ CLI Commands

### Diagnostics & Info

```bash
kimari doctor                                        # System diagnostics (CUDA, GPU, llama-server)
kimari doctor --json                                 # JSON output for automation/IDEs
kimari info                                          # Installation info (version, paths, profiles)
kimari info --json                                   # JSON info output
```

### Server Management

```bash
kimari start                                         # Start server (default: test profile)
kimari start --profile gtx1080                       # Start with a specific GPU profile
kimari start --dry-run                               # Preview command without running
kimari start --host 0.0.0.0 --port 8080              # Override host and port
kimari start --daemon                                # Start in background
kimari stop                                          # Stop running server
kimari status                                        # Check server status
kimari status --json                                 # JSON status output
kimari logs                                          # Show server logs
kimari logs --follow                                 # Tail logs in real time
```

### Models

```bash
kimari pull test                                      # Download test model (TinyLlama 1.1B)
kimari pull recommended                               # Download recommended model (Qwen3-4B)
kimari pull --all                                     # Download all available models
kimari pull --list                                    # List available models in registry
kimari pull test --dry-run                            # Preview download (no transfer)
kimari models                                         # List downloaded models
kimari models --json                                  # JSON model listing
kimari models --downloaded                            # Show only downloaded models
```

> **SHA256 verification:** `kimari pull` supports SHA256 hash verification after download. However, model hashes in the registry are **not yet pinned** — verification is supported but not currently enforced. This will be updated in a future release.

### Profiles & Configuration

```bash
kimari profiles                                       # List GPU profiles
kimari profiles --json                                # JSON profile output
kimari config path                                    # Print config file path
kimari config show                                    # Display full configuration
kimari config show --json                             # JSON config output
kimari config validate                                # Validate config against schema
kimari config migrate                                 # Migrate config to current version
kimari config migrate --dry-run                       # Preview migration changes
```

### Chat & Benchmarks

```bash
kimari chat "Your message here"                       # Send a single message
kimari chat                                          # Interactive chat mode
kimari bench --profile test                           # Run benchmarks (tokens/s, TTFT)
kimari bench --profile gtx1080 --vram 8.0             # Override VRAM manually
kimari bench --profile test --json                    # JSON benchmark output
kimari fit --model models/file.gguf --ctx 8192        # Calculate KimariFit score
kimari fit --model models/file.gguf --vram 8.0        # Override VRAM for KimariFit
```

---

## 📐 KimariFit Score

The KimariFit formula measures useful intelligence density per GiB of VRAM. It answers a simple question: *"Will this model run well on my GPU?"*

```
M_total ≈ S_GGUF + C/9709 + overhead
```

| Score | Rating | Meaning |
|:-----:|--------|---------|
| 90–100 | 🟢 **Optimal** | Model fits perfectly. Best performance expected. |
| 70–89 | 🟡 **Good** | Minor compromises. Works well for most tasks. |
| 50–69 | 🟠 **Usable** | Significant quantization. Acceptable for basic use. |
| < 50 | 🔴 **Poor** | Will be slow or OOM. Not recommended. |

```bash
# Calculate fit for a specific model and GPU
kimari fit --model models/your-model.gguf --ctx 8192

# Override VRAM on systems without GPU detection
kimari fit --model models/your-model.gguf --vram 8.0
```

See [docs/00-02_kimarifit_formula.md](docs/00-02_kimarifit_formula.md) for the full formula and methodology.

---

## 🏗️ Architecture

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

| Layer | Technology | Status |
|-------|-----------|--------|
| **CLI** | Python 3.10+ command-line interface | ✅ Available |
| **Open WebUI** | Full-featured web chat interface (Docker) | ✅ Available |
| **Continue** | AI coding assistant for VS Code and JetBrains | ✅ Available |
| **ROCm** | AMD GPU support via HIP/ROCm build | 🧪 Experimental |
| **Local API** | FastAPI REST API for programmatic access | 🔨 Planned (v0.2) |
| **Web Dashboard** | Minimal status/controls UI | 🔨 Planned (v0.3) |

---

## 📚 Documentation

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

---

## 🌐 Open WebUI Integration

Run a full-featured web chat interface alongside Kimari:

```bash
# 1. Start Kimari with the docker profile (listens on 0.0.0.0)
kimari start --profile docker --daemon

# 2. Launch Open WebUI
make webui-up

# 3. Open in browser → http://localhost:3000
```

> ⚠️ **Security Warning:** Binding to `0.0.0.0` makes the API accessible from other machines on your network. Only use this on trusted local networks. See [SECURITY.md](SECURITY.md) for details.

---

## 🤝 Contributing

We welcome contributions! Whether it's bug reports, feature requests, documentation improvements, or code — every contribution matters.

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

---

## ⚖️ License

This project is licensed under the MIT License — see [LICENSE](LICENSE) for details.

Model weights are not included in this repository. See [MODEL_LICENSES.md](MODEL_LICENSES.md) for information about model licensing.

---

## 🙏 Acknowledgments

- [llama.cpp](https://github.com/ggerganov/llama.cpp) — Inference runtime engine
- [GGUF format](https://github.com/ggerganov/ggml) — Efficient model quantization format
- [Ollama](https://github.com/ollama/ollama) — Inspiration for open-source AI tooling
- [Continue](https://continue.dev) — Open-source AI code assistant
- [Open WebUI](https://github.com/open-webui/open-webui) — Web interface for LLMs

---

<p align="center">
  Made by <a href="https://x.com/smouj013"><strong>Smouj</strong></a> · <a href="https://github.com/smouj/kimari-local-ai">GitHub</a> · <a href="https://smouj.github.io/kimari-local-ai/">Website</a>
</p>
