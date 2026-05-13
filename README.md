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
  <img src="https://img.shields.io/badge/version-0.1.65--alpha-9b59b6.svg" alt="v0.1.65-alpha">
  <a href="https://github.com/smouj/kimari-local-ai">
    <img src="https://img.shields.io/github/stars/smouj/kimari-local-ai?style=social" alt="GitHub stars">
  </a>
</p>

---

## 🌟 Overview

Kimari is an open-source framework for running powerful language models locally on consumer-grade NVIDIA GPUs. It delivers maximum useful intelligence per GiB of VRAM through intelligent quantization, the KimariFit scoring system, and pre-tuned GPU profiles — so you don't have to be an ML engineer to get great performance from older hardware.

> **⚠️ Alpha Software** — Kimari Local AI is in active early development (v0.1.65-alpha). Expect rough edges, breaking changes between versions, and missing features. The project is usable today but not yet production-ready.

**Important:** Kimari is the *framework*, not the model. **Kimari-4B** is a target model currently under development — it is **not yet released**. Until the final fine-tuned weights are available, Kimari can run any compatible GGUF model (Qwen3, SmolLM3, Llama 3.2, TinyLlama, etc.) on consumer hardware — specifically **NVIDIA GTX 1060 (6 GB)** and **GTX 1080 (8 GB)**.

Built on top of [llama.cpp](https://github.com/ggerganov/llama.cpp), Kimari provides an OpenAI-compatible API, a full-featured CLI, and integrations for Open WebUI and Continue (VS Code / JetBrains).

---

## 📊 Project Status

> **Kimari Local AI v0.1.65-alpha**

### 🔗 Public Resources

- **Hugging Face Space**: https://huggingface.co/spaces/kimari-ai/kimari-fit-lab
- **Hugging Face Org Card**: https://huggingface.co/spaces/kimari-ai/README
- **Reference GGUF Collection**: https://huggingface.co/collections/Smouj013/kimari-compatible-gguf-models-6a0352c75d2bfeff34d51e66
- **GitHub Pages Docs**: https://smouj.github.io/kimari-local-ai/


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
- **Performance optimization** — `kimari optimize` recommends optimal settings per GPU profile
- **Performance diagnostics** — `kimari perf` shows tuning matrix for all modes
- **OpenClaw integration** — Chat Completions backend for AI agents
- **Hermes Agent integration** — Local OpenAI-compatible backend
- **Continue.dev integration** — IDE coding assistant (VS Code / JetBrains)
- **Guided setup** — `kimari setup` detects your environment and recommends configuration
- **Setup write-mode** — `kimari setup --write` persists detected configuration with automatic backup
- **Runtime flag validation** — `kimari start --dry-run --strict-flags` checks llama-server compatibility
- **Local auth tokens** — `kimari token create` prepares tokens for future API/reverse proxy use
- **Model hash verification** — `kimari models hash/verify` computes and checks SHA256 hashes of local GGUF files
- **Windows helper scripts** — PowerShell launcher and doctor for Windows users
- **Model path resolution** — `resolve_model_path()` finds models from absolute path, CWD, user models dir, repo root, or fallback
- **Non-interactive setup** — `kimari setup --write --yes` writes config without prompt
- **Hash pinning workflow** — `kimari models pin-hash` with `--dry-run` / `--write` / `--yes` flags
- **Benchmark result sharing** — standardized format in `benchmarks/RESULT_FORMAT.md`
- **Windows wheel install** — PowerShell scripts for wheel build, install, and TestPyPI install
- **Experimental API** — `kimari api --experimental` on port 11436 (unstable)
- **PyPI release gate** — documented criteria, status PENDING
- **Model hashing docs** — full workflow in `docs/MODEL_HASHING.md`
- **Benchmark submissions** — community workflow in `docs/BENCHMARK_SUBMISSIONS.md`
- **Windows packaging** — scripts and docs in `scripts/windows/`
- **Model training plan** — 7-phase training pipeline for Kimari-4B in `docs/MODEL_TRAINING_PLAN.md`
- **Base model selection** — Candidate comparison in `docs/MODEL_BASE_SELECTION.md`
- **Dataset policy and schemas** — SFT/Preference JSONL formats with validation in `dataset/`
- **Training skeletons** — LoRA SFT and ORPO configs with `--dry-run` in `training/`
- **Evaluation prompt seed** — 35 KimariFit prompts across 10 categories in `eval/kimarifit_prompts.jsonl`
- **Hugging Face release plan** — Pre-upload checklist in `docs/HUGGINGFACE_RELEASE.md`
- **MODEL_CARD professional rewrite** — Honest "Planned / Training Design" status with base candidates
- **Benchmark dry-run** — `kimari benchmark --dry-run` generates benchmark plans without execution
- **Tune dry-run** — `kimari tune --dry-run` recommends optimal settings from estimation
- **Measured benchmark (experimental)** — `kimari benchmark --measure --endpoint URL --model NAME --yes` runs real benchmarks against OpenAI-compatible servers; requires `--yes` flag; supports `--output`; fails cleanly on connection error; no results saved by default; see docs/MEASURED_BENCHMARKS.md
- **Doctor deep** — `kimari doctor --deep` runs 14 deep diagnostic checks with structured PASS/WARN/FAIL table and suggested next steps; supports `--json`; no GPU required, no model execution; run before benchmark or training to verify environment
- **Secret scanner hardening** — Security guides are now scanned line-by-line instead of being skipped entirely
- **Gateway plan** — `kimari gateway --dry-run` shows planned gateway configuration; `--status --json` shows gateway status; `--plan --json` shows planned endpoints; no real server yet (dry-run only); default 127.0.0.1:11436; see docs/GATEWAY_PLAN.md
- **Update check** — `kimari update check` shows current version (offline); `--online` checks GitHub for latest release; `--json` output; never auto-updates; see docs/UPDATE.md
- **Quick config** — See docs/OPENWEBUI_OPENCLAW_QUICK_CONFIG.md for Open WebUI, OpenClaw, and Hermes one-command integration setup
- **Benchmark prompts** — Standard safe prompts in `benchmarks/prompts/local_benchmark_prompts.jsonl`
- **Cleaner console output** — `kimari status` and `kimari doctor --deep` now show structured, aligned tables with PASS/WARN/FAIL status and suggested next steps
- **Integration config generator** — `kimari integrations generate --target openwebui --json` generates configuration snippets for Open WebUI, OpenClaw, Hermes, and Continue.dev; no tokens, localhost only by default
- **Gateway prototype plan** — See docs/GATEWAY_PROTOTYPE_PLAN.md for the phased gateway evolution from dry-run to full local controller

### 🔨 Planned

- **Kimari-4B** — Target model under development. Training plan defined, base selection underway. **No weights, adapters, or GGUF files exist. Preview gate is BLOCKED.** Weights not yet available.
- **HF Jobs micro SFT execution record** — no weights committed, no public release, gate BLOCKED
- **Local REST API** — FastAPI-based API for programmatic access (v0.2)
- **Web Dashboard** — Minimal status/controls UI (v0.3)
- **VRAM reporting** — Real-time memory usage in `kimari status`

### ❌ Not Included Yet

- Multi-model serving
- RAG support
- Tool/function calling
- Authentication/authorization for API
- macOS / CPU-only support

---

## Validated Locally on GTX 1060

> **Local runtime validation** — Kimari has been tested on a real NVIDIA GeForce GTX 1060 6GB (WSL2 Ubuntu 24.04) with llama-server CUDA:

| Metric | CUDA GTX 1060 | CPU-only |
|--------|---------------|----------|
| Prompt processing | 228 tok/s | 77 tok/s |
| Token generation | 73 tok/s | 33 tok/s |
| Model VRAM | 1221 MiB | — |

| Detail | Value |
|--------|-------|
| **GPU** | NVIDIA GeForce GTX 1060 6GB |
| **OS** | WSL2 Ubuntu 24.04 |
| **Model** | TinyLlama 1.1B Q4_K_M (**NOT Kimari-4B**) |
| **Backend** | llama-server CUDA (compute 6.1) |
| **Kimari-4B** | Not released |

- ⚠️ This is a local validation using a test model. No claims about Kimari-4B.
- 📄 Full showcase: [docs/GTX1060_SHOWCASE.md](docs/GTX1060_SHOWCASE.md)
- 📄 Runtime details: [docs/GTX1060_LOCAL_RUNTIME_RESULT.md](docs/GTX1060_LOCAL_RUNTIME_RESULT.md)

### Local OpenAI-Compatible Endpoint

> After starting `kimari start --profile test`, the server exposes an OpenAI-compatible API:

```bash
# Health check
curl http://127.0.0.1:11435/health
# {"status":"ok"}

# List models
curl http://127.0.0.1:11435/v1/models

# Chat completion
curl http://127.0.0.1:11435/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model":"tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf","messages":[{"role":"user","content":"Hello"}],"max_tokens":50}'

# Stop server
kimari stop
```

See [docs/LOCAL_OPENAI_ENDPOINT_TEST.md](docs/LOCAL_OPENAI_ENDPOINT_TEST.md) for full details.

> **Note:** The `test` profile uses TinyLlama, not Kimari-4B.

### Local Integrations Validated

> Kimari's OpenAI-compatible endpoint works with popular local AI tools:

| Tool | Status | Config |
|------|--------|--------|
| **Open WebUI** | ✅ Validated | See [docs/OPENWEBUI_LOCAL_SETUP.md](docs/OPENWEBUI_LOCAL_SETUP.md) |
| **OpenClaw** | ✅ Validated | See [docs/OPENCLAW_LOCAL_SETUP.md](docs/OPENCLAW_LOCAL_SETUP.md) |
| **Continue.dev** | ✅ Documented | See [docs/CONTINUE_LOCAL_SETUP.md](docs/CONTINUE_LOCAL_SETUP.md) |
| **curl / OpenAI clients** | ✅ Validated | See [docs/LOCAL_OPENAI_ENDPOINT_TEST.md](docs/LOCAL_OPENAI_ENDPOINT_TEST.md) |

> **Note:** All integrations use the TinyLlama validation model. Kimari-4B is not yet released.

### Hugging Face Presence

> Kimari is on Hugging Face with a live demo Space:

| Resource | Link |
|----------|------|
| **Space (GPU Checker)** | [kimari-ai/kimari-fit-lab](https://huggingface.co/spaces/kimari-ai/kimari-fit-lab) |
| **Organization Card** | [kimari-ai/README](https://huggingface.co/spaces/kimari-ai/README) |
| **Compatible Models Collection** | [Smouj013/kimari-compatible-gguf-models](https://huggingface.co/collections/Smouj013/kimari-compatible-gguf-models-6a0352c75d2bfeff34d51e66) |

> **Note:** The Space does not run any model. The collection contains reference/community GGUF models, not official Kimari models. Kimari-4B is not yet released. Gate: BLOCKED.

### Public Showcase

> Ready-to-use launch material for sharing Kimari:

| Asset | Link |
|-------|------|
| **HF Space** | [kimari-ai/kimari-fit-lab](https://huggingface.co/spaces/kimari-ai/kimari-fit-lab) |
| **Org Card** | [kimari-ai/README](https://huggingface.co/spaces/kimari-ai/README) |
| **Collection** | [kimari-compatible-gguf-models](https://huggingface.co/collections/Smouj013/kimari-compatible-gguf-models-6a0352c75d2bfeff34d51e66) |
| **GTX 1060 Showcase** | [docs/GTX1060_SHOWCASE.md](docs/GTX1060_SHOWCASE.md) |
| **Launch Pack** | [docs/PUBLIC_LAUNCH_PACK.md](docs/PUBLIC_LAUNCH_PACK.md) |
| **X Posts** | [docs/POST_X_KIMARI_GTX1060.md](docs/POST_X_KIMARI_GTX1060.md) |
| **Reddit Posts** | [docs/REDDIT_POST_KIMARI.md](docs/REDDIT_POST_KIMARI.md) |
| **HF Community Post** | [docs/HUGGINGFACE_COMMUNITY_POST.md](docs/HUGGINGFACE_COMMUNITY_POST.md) |

### Kimari-4B Private Adapter Work

> Private micro SFT completed. Private adapter persisted. KimariEval Private v1 created.

| Resource | Link |
|----------|------|
| **Adapter Run Doc** | [docs/KIMARI4B_FIRST_PRIVATE_ADAPTER_RUN.md](docs/KIMARI4B_FIRST_PRIVATE_ADAPTER_RUN.md) |
| **Adapter Persistence** | [docs/KIMARI4B_ADAPTER_PERSISTENCE_STRATEGY.md](docs/KIMARI4B_ADAPTER_PERSISTENCE_STRATEGY.md) |
| **Persisted Result** | [docs/KIMARI4B_MICRO_SFT_PERSISTED_RESULT.md](docs/KIMARI4B_MICRO_SFT_PERSISTED_RESULT.md) |
| **Release Gate** | [docs/KIMARI4B_RELEASE_GATE.md](docs/KIMARI4B_RELEASE_GATE.md) |
| **Eval Plan** | [docs/KIMARI4B_ADAPTER_EVAL_PLAN.md](docs/KIMARI4B_ADAPTER_EVAL_PLAN.md) |
| **KimariEval v1** | [docs/KIMARI_EVAL_PRIVATE_V1.md](docs/KIMARI_EVAL_PRIVATE_V1.md) |
| **Baseline vs Adapter** | [docs/KIMARI_EVAL_BASELINE_VS_ADAPTER_RUN.md](docs/KIMARI_EVAL_BASELINE_VS_ADAPTER_RUN.md) |
| **Review Protocol** | [docs/KIMARI_EVAL_REVIEW_PROTOCOL.md](docs/KIMARI_EVAL_REVIEW_PROTOCOL.md) |

> **Note**: Private adapter on `Smouj013/kimari4b-micro-sft-adapter-v0`. Not public. Kimari-4B is not yet released. Gate is BLOCKED.

### Micro SFT Real (HF Jobs)

> First real micro SFT training on HF Jobs (a10g-small, 72 examples, 20 steps).

| Resource | Link |
|----------|------|
| **Micro SFT Run Doc** | [docs/HF_JOBS_MICRO_SFT_REAL_RUN.md](docs/HF_JOBS_MICRO_SFT_REAL_RUN.md) |
| **Micro SFT Result** | [docs/KIMARI4B_MICRO_SFT_RESULT.md](docs/KIMARI4B_MICRO_SFT_RESULT.md) |
| **Persisted Result** | [docs/KIMARI4B_MICRO_SFT_PERSISTED_RESULT.md](docs/KIMARI4B_MICRO_SFT_PERSISTED_RESULT.md) |
| **Dataset** | [dataset/build/kimari-fit-v0/sft_micro.jsonl](dataset/build/kimari-fit-v0/sft_micro.jsonl) |

> **Note**: Adapter persisted to private HF repo `Smouj013/kimari4b-micro-sft-adapter-v0`. Not public. Gate BLOCKED.

## Open-License Model Policy

Kimari is committed to using **only permissive-license base models** for official releases. This means Apache 2.0, MIT, BSD, or equivalent.

| Role | Base Model | License |
|-----|-----------|--------|
| Kimari Runtime 1.5B | `Qwen/Qwen2.5-1.5B-Instruct` | Apache 2.0 |
| Kimari Core 3B | `HuggingFaceTB/SmolLM3-3B` | Apache 2.0 |
| Kimari-4B candidate | `Qwen/Qwen3-4B-Instruct-2507` | Apache 2.0 |

**We do not use** non-commercial, research-only, or custom-restrictive bases for official public models. Full policy: [`KIMARI_OPEN_LICENSE_POLICY.md`](docs/KIMARI_OPEN_LICENSE_POLICY.md) · License matrix: [`KIMARI_BASE_MODEL_LICENSE_MATRIX.md`](docs/KIMARI_BASE_MODEL_LICENSE_MATRIX.md)

## Open-License Base Bakeoff Status

The v0.1.58-alpha bakeoff is a gated, open-license selection workflow for Kimari Runtime/Core/Kimari-4B base candidates.

- Config: [`eval/configs/open_base_bakeoff_v1.yaml`](eval/configs/open_base_bakeoff_v1.yaml)
- Runner: [`eval/scripts/run_open_base_bakeoff.py`](eval/scripts/run_open_base_bakeoff.py)
- Summary template: [`eval/templates/open_base_bakeoff_summary.template.json`](eval/templates/open_base_bakeoff_summary.template.json)
- Summary validator: [`eval/scripts/validate_open_base_bakeoff_summary.py`](eval/scripts/validate_open_base_bakeoff_summary.py)
- Result doc: [`docs/KIMARI_OPEN_BASE_BAKEOFF_RESULT.md`](docs/KIMARI_OPEN_BASE_BAKEOFF_RESULT.md)
- Decision doc: [`docs/KIMARI_BASE_SELECTION_DECISION.md`](docs/KIMARI_BASE_SELECTION_DECISION.md)

**Safety status:** no training executed, no HF Jobs executed, no public weights/adapters/GGUF files, no public benchmark claims, only permissive-license bases evaluated, gate **BLOCKED**.

---

## Kimari SFT v1 Dataset

Kimari SFT v1 is the current dataset seed for the next training lane. It is structured around **8 categories** and **320+ examples**, with schema validation and build tooling tracked in-repo.

- Dataset docs: [`docs/KIMARI_SFT_V1_DATASET.md`](docs/KIMARI_SFT_V1_DATASET.md)
- Quality guide: [`docs/KIMARI_SFT_V1_QUALITY_GUIDE.md`](docs/KIMARI_SFT_V1_QUALITY_GUIDE.md)
- Schema: [`dataset/schema/kimari_sft_item.schema.json`](dataset/schema/kimari_sft_item.schema.json)
- Validator: [`dataset/scripts/validate_kimari_sft_v1.py`](dataset/scripts/validate_kimari_sft_v1.py)
- Builder: [`dataset/scripts/build_kimari_sft_v1.py`](dataset/scripts/build_kimari_sft_v1.py)
- License manifest: `license_manifest.yaml` + `license_manifest.json` with per-source attribution

**Status:** built with validate + build scripts. No training has been executed yet; gate **BLOCKED**.

## Kimari Runtime 1.5B SFT v1

First QLoRA SFT v1 run on Qwen2.5-1.5B-Instruct (Apache-2.0) with the Kimari SFT v1 seed dataset. Training is executed; adapter is **private only** — not released publicly.

- Config: [`training/configs/kimari_runtime_15b_sft_v1.yaml`](training/configs/kimari_runtime_15b_sft_v1.yaml)
- Plan: [`docs/KIMARI_RUNTIME_15B_SFT_V1_PLAN.md`](docs/KIMARI_RUNTIME_15B_SFT_V1_PLAN.md)
- Result: [`docs/KIMARI_RUNTIME_15B_SFT_V1_RESULT.md`](docs/KIMARI_RUNTIME_15B_SFT_V1_RESULT.md)
- Artifact policy: [`docs/KIMARI_RUNTIME_15B_SFT_V1_ARTIFACT_POLICY.md`](docs/KIMARI_RUNTIME_15B_SFT_V1_ARTIFACT_POLICY.md)
- Preflight: [`training/scripts/preflight_sft_v1.py`](training/scripts/preflight_sft_v1.py)
- Command preview: [`training/scripts/sft_v1_command_preview.py`](training/scripts/sft_v1_command_preview.py)
- HF Jobs wrapper: [`training/scripts/hf_jobs_sft_v1.py`](training/scripts/hf_jobs_sft_v1.py)
- Run summary creator: [`training/scripts/create_sft_v1_run_summary.py`](training/scripts/create_sft_v1_run_summary.py)
- Run summary validator: [`training/scripts/validate_sft_v1_run_summary.py`](training/scripts/validate_sft_v1_run_summary.py)

**Status:** SFT v1 first real short run completed. Adapter private. No public release. Gate **BLOCKED**.

---

## HF Jobs Smoke Tests

> **HF Jobs smoke tests require Jobs access** in the authenticated Hugging Face account. If HF Jobs is unavailable, use [local GTX validation](docs/GTX1060_LOCAL_RUNTIME_RESULT.md) or [fallback runners](docs/HF_JOBS_FALLBACK_RUNNERS.md).

Check access with:
```bash
python training/scripts/check_hf_jobs_access.py --json
```

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
>
> The `test` profile is the default during alpha. When Kimari-4B is published, `gtx1060` will become the new default. Performance-tuned profiles (`gtx1060-safe`, `gtx1060-fast`, etc.) are available for specific use cases.

---

## ⌨️ CLI Commands

### Diagnostics & Info

```bash
kimari doctor                                        # System diagnostics (CUDA, GPU, llama-server)
kimari doctor --deep                                 # 14 deep diagnostic checks (Python, version, paths, config, models, packaged defaults, llama-server, CUDA/NVIDIA, default profile, secret scanner, benchmark prompts, gateway module, integration docs, preview gate)
kimari doctor --deep --json                         # Deep diagnostics as JSON
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

### Guided Setup

```bash
kimari setup                              # Detect environment and recommend configuration
kimari setup --json                       # JSON output for automation
kimari setup --write                      # Persist detected configuration to user config dir
kimari setup --write --yes                # Non-interactive: shows preview, writes without prompt
kimari setup --integration openclaw       # Recommend OpenClaw integration
kimari setup --dry-run                    # Preview without detection
```

### Model Hash Verification

```bash
kimari models hash <path>                 # Compute SHA256 hash of a local GGUF file
kimari models hash <path> --json          # JSON output
kimari models verify <model-id-or-path>   # Verify model hash against registry
kimari models verify <model-id> --json    # JSON output
kimari models pin-hash <model-id>                # Preview pinning hash (dry-run)
kimari models pin-hash <model-id> --dry-run      # Preview patch without writing
kimari models pin-hash <model-id> --write         # Write with confirmation
kimari models pin-hash <model-id> --write --yes   # Write without prompt
```

> **Note:** SHA256 hashes in the registry are not yet pinned. `kimari models verify` will report "hash not pinned" until hashes are explicitly set. Use `pin-hash --write` to compute and pin real hashes. Use `--dry-run` to preview the patch, `--yes` to skip the confirmation prompt.

### Token Management

```bash
kimari token create                       # Generate a local auth token
kimari token show                         # Display the current token
kimari token delete                       # Remove the token
```

### Gateway (Dry-Run Only)

```bash
kimari gateway --dry-run                  # Show planned gateway configuration
kimari gateway --status --json            # Show gateway status (planned)
kimari gateway --plan --json              # Show planned endpoints
```

> **Note:** No real server yet — dry-run only. Default: `127.0.0.1:11436` (localhost only). See [docs/GATEWAY_PLAN.md](docs/GATEWAY_PLAN.md) for the gateway design.

### Update Check

```bash
kimari update check                       # Show current version (offline)
kimari update check --online              # Check GitHub for latest release
kimari update check --json                # JSON output
```

> **Note:** Kimari never auto-updates. `--online` checks GitHub only when explicitly requested. See [docs/UPDATE.md](docs/UPDATE.md) for details.

### Integration Config Generator

```bash
kimari integrations generate --target openwebui --json   # Open WebUI config snippet
kimari integrations generate --target openclaw --json    # OpenClaw config snippet
kimari integrations generate --target hermes --json      # Hermes agent config snippet
kimari integrations generate --target continue --json    # Continue.dev config snippet
kimari integrations generate --all --json                # All integration configs
```

> **Note:** Configs contain no tokens or API keys. Default base_url is `http://127.0.0.1:11435/v1` (localhost only). Use `--write --output /path/to/file.json` to save to a specific path. See [docs/INTEGRATION_CONFIG_GENERATOR.md](docs/INTEGRATION_CONFIG_GENERATOR.md) for details.

---

## ⚡ Performance Tuning

Kimari includes tools to help you find the best settings for your GPU without guesswork.

### `kimari optimize`

Analyzes your profile and recommends optimal settings for VRAM, context, batch sizes, and cache types:

```bash
kimari optimize                              # Analyze default profile
kimari optimize --profile gtx1060            # Optimize for GTX 1060
kimari optimize --profile test --mode fast   # Fast mode recommendations
kimari optimize --profile test --json        # JSON output for automation
```

### `kimari perf`

Shows a performance matrix across all modes (safe, balanced, fast, ide, agent):

```bash
kimari perf --profile test --dry-run         # Default mode overview
kimari perf --profile gtx1060 --matrix       # All modes compared
kimari perf --profile test --json --dry-run  # JSON output
```

### `kimari benchmark`

Generate a benchmark plan without executing models (dry-run by default):

```bash
kimari benchmark --dry-run                        # Show estimated plan for default profile
kimari benchmark --profile gtx1060-safe --dry-run # Plan for a specific profile
kimari benchmark --matrix --dry-run --json        # Full parameter matrix as JSON
kimari benchmark --measure --endpoint <url> --model <name> --yes  # Measured benchmark against running server (--yes required)
kimari benchmark --measure --endpoint <url> --model <name> --yes --output results.json  # Save results to file
```

### `kimari tune`

Get recommended settings based on VRAM/RAM estimation:

```bash
kimari tune --dry-run                       # Recommendations for default profile
kimari tune --profile gtx1060-safe --json   # JSON output for automation
```

> **Note:** `kimari tune --apply` is intentionally **blocked** in v0.1.26-alpha. Auto-apply will be enabled once measured benchmarks are validated.
>
> See [Performance Tuning Plan](docs/PERFORMANCE_TUNING_PLAN.md) for the full measurement and tuning roadmap.

### Performance Profiles

| Profile | GPU | Mode | Cache | Context | Use Case |
|---------|-----|------|-------|---------|----------|
| `gtx1060-safe` | GTX 1060 | safe | q8_0/q8_0 | 4,096 | Maximum stability, no OOM |
| `gtx1060-fast` | GTX 1060 | fast | q8_0/q8_0 | 8,192 | Speed priority |
| `gtx1080-balanced` | GTX 1080 | balanced | q8_0/f16 | 8,192 | Quality/speed balance |
| `gtx1080-longctx` | GTX 1080 | balanced | q8_0/q8_0 | 16,384 | Long conversations |
| `ide-local` | Any 6 GB+ | ide | q8_0/q8_0 | 4,096 | Continue, Cursor, VS Code |
| `agent-local` | Any 6 GB+ | agent | q8_0/q8_0 | 4,096 | OpenClaw, Hermes |
| `openclaw-local` | Any 6 GB+ | agent | q8_0/q8_0 | 4,096 | OpenClaw integration |
| `hermes-local` | Any 6 GB+ | agent | q8_0/q8_0 | 4,096 | Hermes Agent integration |

> All new profiles use TinyLlama during alpha. When Kimari-4B is released, the GPU-specific profiles will use it by default.

## 🔧 Guided Setup & Validation

Kimari can detect your environment and recommend the best configuration.

### `kimari setup`

Detects your OS, GPU, CUDA, llama-server binary, and local models, then recommends a profile and next steps:

```bash
kimari setup                              # Full environment detection
kimari setup --json                       # JSON output for automation
kimari setup --write                      # Persist detected configuration with backup
kimari setup --integration openclaw       # Recommend OpenClaw integration
kimari setup --integration hermes         # Recommend Hermes integration
kimari setup --integration continue       # Recommend Continue IDE integration
kimari setup --dry-run                    # Preview without detection
```

With `--write`, Kimari persists the recommended profile, integration settings, and hardware summary to your user config directory. A timestamped backup is created before any changes.

### Recovering from Incomplete Setup Config

If `kimari doctor --deep` warns about an incomplete user config (missing `version`, `profiles`, or `default_profile`), you can regenerate a safe, complete configuration:

```bash
kimari setup --write --yes --reset-user-config
```

This flag regenerates the user config from packaged defaults, creating a timestamped backup of the existing config first. Use this when a previous `kimari setup --write` produced an incomplete configuration due to the empty-dict bug fixed in v0.1.38-alpha.

### Model Hash Verification

Verify the integrity of your downloaded models:

```bash
kimari models hash ./models/model.gguf    # Compute SHA256 of a local GGUF file
kimari models verify test                 # Verify model against registry
kimari models pin-hash test --write       # Pin real hash to user registry
```

SHA256 hashes in the registry are currently `null` (not yet pinned). Use `pin-hash --write` to compute and pin real hashes for your local files.

### Runtime Flag Validation

Check if your llama-server binary supports the flags your profile requires:

```bash
kimari start --dry-run --strict-flags     # Fail on unsupported flags
```

Without `--strict-flags`, unsupported flags produce warnings. With it, they cause an error.

### Local Auth Tokens

Prepare auth tokens for future Kimari API or reverse proxy use:

```bash
kimari token create                       # Generate a local auth token
kimari token show                         # Display the current token
kimari token delete                       # Remove the token
```

> **Note:** These tokens are prepared for future Kimari API / reverse proxy use. `llama-server` does not apply auth natively.

### Packaged Defaults & User Paths

Kimari works when installed from PyPI — no need to run from the repo root:

- **Config** lives in your user config directory (`~/.config/kimari/` on Linux/macOS, `%APPDATA%\Kimari\` on Windows)
- **State** (PID, logs, tokens) lives in your user state directory
- **Models** are stored in your user data directory
- **Packaged defaults** ship inside the wheel and are copied to your user config on first use

```bash
kimari config path                         # Show where your config lives
export KIMARI_HOME=~/.kimari               # Override all paths at once
export KIMARI_CONFIG_DIR=/etc/kimari       # Override config dir only
```

### Model Path Resolution

`resolve_model_path()` locates model files by searching in order:

1. **Absolute path** — used as-is if the model path is already absolute
2. **CWD-relative** — resolved relative to the current working directory
3. **User models dir** — the platform-specific user data models directory
4. **Repo-root** — the `models/` directory under the project root (editable installs)
5. **Fallback** — returns the original path if nothing is found

This ensures models are found correctly whether Kimari is installed from a wheel, run from the repo, or configured with custom paths.

### Benchmark Result Sharing

Share benchmark results using the standardized format defined in `benchmarks/RESULT_FORMAT.md`. This makes it easy to compare performance across hardware:

- Follow the JSON schema in `benchmarks/RESULT_FORMAT.md`
- Include GPU, model, quantization, context size, tokens/s, and TTFT
- Submit results via PR to `benchmarks/results/`

### Windows Wheel Install

Windows users can install from a built wheel or TestPyPI using the new PowerShell scripts:

```powershell
# Build a wheel locally
.\scripts\windows\build-wheel.ps1

# Install from a built wheel
.\scripts\windows\install-from-wheel.ps1

# Install from TestPyPI
.\scripts\windows\install-from-testpypi.ps1
```

## 🧪 Experimental API

An experimental REST API is available for testing. It is **not** the planned v0.2 FastAPI server — it is a separate, unstable endpoint.

```bash
pip install "kimari-local-ai[api]"
kimari api --experimental
# Listens on http://127.0.0.1:11436
```

> ⚠️ **Experimental** — This API may change or be removed without notice. Not for production use.
>
> See [docs/API_EXPERIMENTAL.md](docs/API_EXPERIMENTAL.md) for details.

## 🔐 PyPI Release Gate

The PyPI publishing workflow is documented but **not yet active**. Status: **PENDING**. No package is published on real PyPI.

See [docs/PYPI_RELEASE_GATE.md](docs/PYPI_RELEASE_GATE.md) for the gate criteria and current status.

## #️⃣ Model Hashing

Verify model integrity and pin SHA256 hashes to the registry:

```bash
kimari models hash <path>          # Compute SHA256 of a GGUF file
kimari models verify <model-id>    # Verify against registry
kimari models pin-hash <model-id>  # Pin hash (--dry-run / --write / --yes)
```

See [docs/MODEL_HASHING.md](docs/MODEL_HASHING.md) for the full workflow.

## 📤 Benchmark Submissions

Share benchmark results with the community using the standardized format. Submit via PR to `benchmarks/results/`.

See [docs/BENCHMARK_SUBMISSIONS.md](docs/BENCHMARK_SUBMISSIONS.md) for the community workflow and format.

## 🪟 Windows Install

PowerShell scripts for building, installing, and testing on Windows:

```powershell
.\scripts\windows\build-wheel.ps1
.\scripts\windows\install-from-wheel.ps1
```

See [scripts/windows/README.md](scripts/windows/README.md) for details.

## 🧠 Kimari-4B Model Work

Kimari-4B is the project's target model — a 3B–4B class local coding/sysadmin/agent assistant designed for consumer GPUs.

> **Status: Planned / Training Design** — No weights released yet. SmolLM3-3B accepted for first private SFT candidate. v0.1.49-alpha — HF Jobs access gate, smoke test preparation, privacy safeguards. No weights. No public release.

### What's Ready

- **[MODEL_CARD.md](MODEL_CARD.md)** — Professional model card with honest status, base candidates, and evaluation targets
- **[Training Plan](docs/MODEL_TRAINING_PLAN.md)** — 7-phase pipeline (selection → SFT → DPO/ORPO → eval → GGUF → HF → registry)
- **[Base Selection](docs/MODEL_BASE_SELECTION.md)** — SmolLM3-3B, Qwen2.5-3B-Instruct, Llama 3.2 3B comparison
- **[Base Decision Record](docs/MODEL_DECISION_RECORD.md)** — ADR with scoring criteria for base model selection
- **[Model Licenses](MODEL_LICENSES.md)** — License layers for code, weights, and base models
- **[Dataset Policy](dataset/README.md)** — SFT and Preference JSONL schemas with validation
- **[Hugging Face Release](docs/HUGGINGFACE_RELEASE.md)** — Pre-upload checklist and HF model card template
- **[First Training Run](docs/FIRST_TRAINING_RUN.md)** — Step-by-step guide for first training run
- **[KimariFit Rubric](eval/rubrics/kimarifit_rubric.md)** — Evaluation criteria and scoring rubric

### Pipeline Tools

- **`select_base_model.py`** — Scores and ranks base model candidates by license, capability, and hardware criteria
- **`build_dataset_mix.py`** — Validates and builds training-ready dataset mixes from SFT and preference seeds
- **`eval/kimarifit.py`** — Dry-run and live evaluation harness for KimariFit prompts
- **`export_gguf_plan.py`** — Plans GGUF export quantizations without requiring llama.cpp tools

### Base Model Candidates

| Candidate | License | Strength | Risk |
|-----------|---------|----------|------|
| SmolLM3-3B | Apache 2.0 | ✅ Accepted for private training | Less coding capability |
| Qwen2.5-3B-Instruct | qwen-research | Strong coding/JSON/multilingual | License review required |
| Llama 3.2 3B | Meta Community | Strong general performance | Redistribution constraints |

> SmolLM3-3B accepted for first private SFT. See [Base Model Acceptance](docs/BASE_MODEL_ACCEPTANCE.md) and [docs/MODEL_BASE_SELECTION.md](docs/MODEL_BASE_SELECTION.md) for the full comparison.

### v0 Pipeline

- **SmolLM3-3B accepted** for first private SFT candidate (see [Base Model Acceptance](docs/BASE_MODEL_ACCEPTANCE.md))
- **Dataset v0** — Synthetic SFT + preference + eval holdout in `dataset/v0/`
- **Training readiness validator** — `validate_training_ready.py` checks all prerequisites
- **v0 training configs** — SFT LoRA and ORPO example configs for SmolLM3-3B
- **KimariFit scoring dimensions** — 9 evaluation dimensions defined
- **[First Private Training Run](docs/FIRST_PRIVATE_TRAINING_RUN.md)** — Step-by-step guide
- **[Baseline Eval Plan](docs/BASELINE_EVAL_PLAN.md)** — Evaluate SmolLM3-3B before SFT
- **[Adapter Artifact Policy](docs/ADAPTER_ARTIFACT_POLICY.md)** — What can/cannot be committed from training
- **[Adapter Preview Gate](docs/ADAPTER_PREVIEW_GATE.md)** — Criteria for private→preview transition (currently BLOCKED)
- **[Private Training Runbook](docs/PRIVATE_TRAINING_RUNBOOK.md)** — Full runbook for first private SFT
- **[Adapter Manifest Template](training/templates/adapter_manifest.template.yaml)** — Template for recording adapter metadata
- **[Private SFT Execution Checklist](docs/PRIVATE_SFT_EXECUTION_CHECKLIST.md)** — Pre-flight checklist for first private SFT
- **[SFT→ORPO Decision](docs/SFT_TO_ORPO_DECISION.md)** — Decision framework for proceeding to ORPO after SFT
- **[Private Eval Results Policy](docs/PRIVATE_EVAL_RESULTS_POLICY.md)** — What eval results can be committed
- **[Eval Summary Template](eval/templates/eval_summary.template.json)** — Committable eval summary format
- **[Remote GPU RunPod Guide](docs/REMOTE_GPU_RUNPOD_GUIDE.md)** — Execute private SFT on RunPod or local GPU
- **[Training Requirements](training/requirements-training.txt)** — Separated training dependencies
- **[Preflight Script](training/scripts/preflight_private_sft.py)** — Check SFT readiness before training
- **[Postrun Script](training/scripts/postrun_private_sft.py)** — Orchestrate post-training steps
- **[Private Run Artifacts](docs/PRIVATE_RUN_ARTIFACTS.md)** — What stays local vs what can be committed
- **[Private Run Failures](docs/PRIVATE_RUN_FAILURES.md)** — Troubleshooting guide for training failures
- **[First Private SFT Record](docs/FIRST_PRIVATE_SFT_RECORD.md)** — How to register a private SFT run safely
- **[Private Run Record Template](training/templates/private_sft_run_record.template.json)** — Committable run record template
- **[Safe Screenshot Capture](docs/SAFE_SCREENSHOT_CAPTURE.md)** — Guide for capturing safe terminal screenshots
- **[HF Token Safety](docs/HF_TOKEN_SAFETY.md)** — Guide for safe Hugging Face token handling
- **[Private SFT Handoff](docs/FIRST_PRIVATE_SFT_HANDOFF.md)** — How to bring sanitized results from RunPod/local to repo
- **[Private SFT Run Commands](docs/PRIVATE_SFT_RUN_COMMANDS.md)** — Expected commands for first private SFT execution

### Kimari-4B First Private SFT Run

- **[KIMARI4B_PRIVATE_SFT_RUN.md](docs/KIMARI4B_PRIVATE_SFT_RUN.md)** — Full execution guide for the first private SFT run
- **[KIMARI4B_FIRST_RUN_CHECKLIST.md](docs/KIMARI4B_FIRST_RUN_CHECKLIST.md)** — Pre-flight checklist specific to Kimari-4B
- **[KIMARI4B_EVAL_CRITERIA.md](docs/KIMARI4B_EVAL_CRITERIA.md)** — Evaluation criteria for Kimari-4B adapter assessment
- **[Private run config](training/configs/kimari4b_private_sft_run.v0.yaml)** — Run manifest for first private SFT
- **[Command script](training/scripts/kimari4b_private_sft_command.py)** — Generates exact training commands (`--config`, `--json`, `--markdown`)
- **[Eval plan script](eval/scripts/kimari4b_eval_plan.py)** — Generates baseline and adapter eval plans (`--baseline-label`, `--adapter-label`, `--json`, `--markdown`)
- **[Summary template](training/templates/kimari4b_private_summary.template.json)** — Template for sanitized training summary

### Hugging Face Jobs Private Smoke Test

- **[HF_JOBS_PRIVATE_RUN.md](docs/HF_JOBS_PRIVATE_RUN.md)** — Guide for running Kimari-4B smoke tests on Hugging Face Jobs
- **[HF_JOBS_RESULT_HANDOFF.md](docs/HF_JOBS_RESULT_HANDOFF.md)** — How to bring sanitized results from HF Jobs
- **[HF Jobs smoke config](training/configs/hf_jobs_kimari4b_smoke.v0.yaml)** — Config for GPU/torch/repo/dataset/SFT dry-run validation
- **[hf_jobs_private_run.py](training/scripts/hf_jobs_private_run.py)** — CLI wrapper for HF Jobs submission (`--dry-run`, `--print-command`, `--allow-submit --yes`)
- **[hf_jobs_status.py](training/scripts/hf_jobs_status.py)** — Read-only CLI for checking HF Jobs status
- **[Smoke summary template](training/templates/hf_jobs_smoke_summary.template.json)** — Template for sanitized smoke test summary
- **[validate_private_sft_commands.py](training/scripts/validate_private_sft_commands.py)** — Validates generated commands against supported flags

> **No public weights. No GGUF. Gate BLOCKED.** HF Jobs is used for smoke tests only — no training, no upload, no export. The first private SFT run is planned but not yet executed. Only sanitized metadata summaries may be committed after human review.

### HF Jobs Smoke Test Result

- **[HF_JOBS_SMOKE_RESULT.md](docs/HF_JOBS_SMOKE_RESULT.md)** — Smoke test result template and sanitized summary (status: pending)
- **[HF_JOBS_SMOKE_RUNBOOK.md](docs/HF_JOBS_SMOKE_RUNBOOK.md)** — Step-by-step runbook for executing the first HF Jobs smoke test
- **[HF_JOBS_SMOKE_EXECUTION_RECORD.md](docs/HF_JOBS_SMOKE_EXECUTION_RECORD.md)** — Smoke execution record (status: pending)
- **[create_hf_jobs_smoke_summary.py](training/scripts/create_hf_jobs_smoke_summary.py)** — CLI to generate sanitized smoke test summaries
- **[validate_hf_jobs_smoke_summary.py](training/scripts/validate_hf_jobs_smoke_summary.py)** — CLI to validate smoke summary safety
- **[Smoke execution record template](training/templates/hf_jobs_smoke_execution_record.template.json)** — Template for sanitized execution record

> **No smoke test executed yet.** Status: pending. No training performed. No weights. Gate BLOCKED. Smoke must pass before micro SFT.

### HF Jobs Micro SFT Pipeline

- **[HF_JOBS_MICRO_SFT_RUN.md](docs/HF_JOBS_MICRO_SFT_RUN.md)** — Guide for running micro SFT on HF Jobs
- **[HF_JOBS_MICRO_SFT_RESULT.md](docs/HF_JOBS_MICRO_SFT_RESULT.md)** — Micro SFT result (status: completed, adapter ephemeral)
- **[MICRO_SFT_IMPLEMENTATION.md](docs/MICRO_SFT_IMPLEMENTATION.md)** — Micro SFT training implementation docs
- **[Micro SFT config](training/configs/hf_jobs_kimari4b_micro_sft.v0.yaml)** — Config for micro SFT (10 steps, gate BLOCKED)
- **[hf_jobs_micro_sft.py](training/scripts/hf_jobs_micro_sft.py)** — CLI wrapper for micro SFT submission
- **[Micro SFT summary template](training/templates/hf_jobs_micro_sft_summary.template.json)** — Template for sanitized summary
- **[create_hf_jobs_micro_sft_summary.py](training/scripts/create_hf_jobs_micro_sft_summary.py)** — Generate sanitized summaries
- **[validate_hf_jobs_micro_sft_summary.py](training/scripts/validate_hf_jobs_micro_sft_summary.py)** — Validate summary safety
- **[validate_micro_sft_readiness.py](training/scripts/validate_micro_sft_readiness.py)** — Pre-flight config validation

> **Micro SFT training now supported.** `train_sft_lora.py` supports real micro-run training with `--micro-run --yes`. New flags: `--dataset-path`, `--eval-dataset-path`, `--output-dir`, `--max-steps`, `--eval-steps`, `--save-steps`, `--logging-steps`, `--per-device-train-batch-size`, `--gradient-accumulation-steps`, `--learning-rate`, `--max-seq-length`. Training requires `--micro-run --yes`. CI blocks training. No HF upload. No `--token`. `push_to_hub=false`. `report_to="none"`. No public weights. No GGUF. Gate BLOCKED.

> No weights released yet. No real benchmarks. SmolLM3 is accepted for private training only. Preview gate is BLOCKED.

### Training Approach

1. **SFT with LoRA/QLoRA** on selected base model
2. **Preference tuning** (DPO or ORPO) after SFT
3. **Evaluation** with KimariFit prompts and safety checks
4. **GGUF export** (Q4_K_M, Q5_K_M, IQ4_XS)
5. **Hugging Face release** if license and eval pass

> Local GTX 1060/1080 is for inference/testing only. Training requires rented GPU (RTX 4090+, A100).
> See [docs/MODEL_TRAINING_PLAN.md](docs/MODEL_TRAINING_PLAN.md) for details.

---

## 📸 Screenshots & CLI Preview

Visual overview of Kimari's command-line tools. All outputs are illustrative — no secrets, no real training outputs, no benchmarks claimed.

See [docs/SCREENSHOTS.md](docs/SCREENSHOTS.md) for the full gallery with code examples. See [docs/SAFE_SCREENSHOT_CAPTURE.md](docs/SAFE_SCREENSHOT_CAPTURE.md) for the safe screenshot capture guide.

**Planned screenshots:** `kimari setup --json`, `preflight_private_sft.py --json`, `run_training_command_preview.py --json`, `postrun_private_sft.py --dry-run --json`, `kimari optimize --profile test --json`, GitHub Pages landing.

**Screenshots plan:** See `generate_safe_cli_screenshots_plan.py` for the scripted CLI screenshot capture plan with safety checks.

**CLI text examples** are available in [docs/assets/screenshots/examples/](docs/assets/screenshots/examples/) — safe text blocks for generating captures.

## 📋 First Private Run Record

When the first private SFT is executed, a run record captures the essential metadata without exposing sensitive outputs:

- **Run record template** — [training/templates/private_sft_run_record.template.json](training/templates/private_sft_run_record.template.json)
- **Run record creation script** — `training/scripts/create_private_run_record.py --dry-run --json`
- **Documentation** — [docs/FIRST_PRIVATE_SFT_RECORD.md](docs/FIRST_PRIVATE_SFT_RECORD.md)

> **What can be committed:** Sanitized metadata (run_id, base_model, hardware summary, gate state).
> **What must remain local:** Adapter weights, checkpoints, raw eval outputs, local paths.
> **Preview gate stays BLOCKED** — no public release, no HF upload.

## 🔐 Secret Hygiene

Before any real training execution, ensure no tokens or secrets reach the repository:

- **[HF Token Safety Guide](docs/HF_TOKEN_SAFETY.md)** — How to handle Hugging Face tokens safely
- **Secret scanner** — `python scripts/security/scan_for_secrets.py --paths README.md docs training eval tests --json`
- **Private SFT handoff** — [docs/FIRST_PRIVATE_SFT_HANDOFF.md](docs/FIRST_PRIVATE_SFT_HANDOFF.md) — How to bring sanitized results to repo
- **[Performance Tuning Plan](docs/PERFORMANCE_TUNING_PLAN.md)** — Roadmap for moving from estimation to real measured benchmarks
- **[Secret Scan Policy](docs/SECRET_SCAN_POLICY.md)** — Line-by-line scanning policy for security guides

> **Never commit tokens, API keys, or private paths.** If a token is exposed, revoke it immediately.

---

## 🔌 IDE & Agent Integrations

Kimari works as a local backend for AI coding assistants and autonomous agents via its OpenAI-compatible API.

| Integration | Config | Recommended Profile |
|-------------|--------|--------------------|
| [OpenClaw](docs/integrations/OPENCLAW.md) | `config/integrations/openclaw.kimari.example.json` | `openclaw-local` |
| [Hermes Agent](docs/integrations/HERMES.md) | `config/integrations/hermes.kimari.example.yaml` | `hermes-local` |
| [Continue.dev](docs/integrations/CONTINUE.md) | `config/integrations/continue.kimari.example.yaml` | `ide-local` |
| [Any OpenAI client](docs/integrations/OPENAI_COMPATIBLE_CLIENTS.md) | — | Any |

All integrations use **Chat Completions** (`/v1/chat/completions`). Responses API is not yet supported.

See [docs/integrations/](docs/integrations/) for detailed setup guides.

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
| **Continue** | AI coding assistant for VS Code and JetBrains | ✅ Available (Chat + Edit) |
| **OpenClaw** | AI agent framework with local model support | ✅ Available (Chat Completions) |
| **Hermes** | AI agent supporting OpenAI-compatible servers | ✅ Available (Chat Completions) |
| **Runtime Validation** | llama-server flag detection and compatibility checks | ✅ Available |
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
| [Release Checklist](RELEASE_CHECKLIST.md) | Pre-release validation checklist |
| [Security](SECURITY.md) | Security policy and best practices |
| [Privacy](PRIVACY.md) | Privacy policy (no telemetry) |
| [OpenClaw Integration](docs/integrations/OPENCLAW.md) | Connect OpenClaw to Kimari's local API |
| [Hermes Integration](docs/integrations/HERMES.md) | Connect Hermes Agent to Kimari |
| [Continue Integration](docs/integrations/CONTINUE.md) | Use Kimari as IDE coding assistant |
| [OpenAI-Compatible Clients](docs/integrations/OPENAI_COMPATIBLE_CLIENTS.md) | Generic client integration guide |
| [Reverse Proxy Auth](docs/REVERSE_PROXY_AUTH.md) | nginx/Caddy auth setup for local API |
| [Experimental API](docs/API_EXPERIMENTAL.md) | Experimental REST API (port 11436) |
| [PyPI Release Gate](docs/PYPI_RELEASE_GATE.md) | PyPI publishing gate criteria and status |
| [Model Hashing](docs/MODEL_HASHING.md) | SHA256 hash verification and pinning workflow |
| [Benchmark Submissions](docs/BENCHMARK_SUBMISSIONS.md) | Community benchmark submission workflow |
| [Model Training Plan](docs/MODEL_TRAINING_PLAN.md) | 7-phase training pipeline for Kimari-4B |
| [Base Model Selection](docs/MODEL_BASE_SELECTION.md) | Candidate comparison and selection criteria |
| [Base Decision Record](docs/MODEL_DECISION_RECORD.md) | ADR for base model selection with scoring |
| [Hugging Face Release](docs/HUGGINGFACE_RELEASE.md) | HF release checklist and model card template |
| [First Training Run](docs/FIRST_TRAINING_RUN.md) | Step-by-step guide for first training run |
| [API Plan (v0.2)](docs/API_PLAN.md) | FastAPI REST API design for v0.2 |
| [Screenshots & CLI Preview](docs/SCREENSHOTS.md) | CLI output examples and screenshot gallery |
| [Safe Screenshot Capture](docs/SAFE_SCREENSHOT_CAPTURE.md) | Guide for capturing safe terminal screenshots |
| [First Private SFT Record](docs/FIRST_PRIVATE_SFT_RECORD.md) | How to register a private SFT run safely |
| [HF Token Safety](docs/HF_TOKEN_SAFETY.md) | Safe Hugging Face token handling guide |
| [Private SFT Handoff](docs/FIRST_PRIVATE_SFT_HANDOFF.md) | How to bring sanitized results to repo safely |
| [Private SFT Run Commands](docs/PRIVATE_SFT_RUN_COMMANDS.md) | Expected commands for first private SFT execution |
| [Performance Tuning Plan](docs/PERFORMANCE_TUNING_PLAN.md) | Roadmap for real measured benchmarks and auto-tuning |
| [Secret Scan Policy](docs/SECRET_SCAN_POLICY.md) | Line-by-line scanning policy for security guides |
| [Measured Benchmarks](docs/MEASURED_BENCHMARKS.md) | Real benchmark execution against OpenAI-compatible servers |
| [Doctor Deep](docs/DOCTOR_DEEP.md) | Extended diagnostics documentation |
| [Gateway Plan](docs/GATEWAY_PLAN.md) | Local controller design, dry-run only, 127.0.0.1:11436 |
| [Update Check](docs/UPDATE.md) | Version checking, offline by default, never auto-updates |
| [Open WebUI/OpenClaw Quick Config](docs/OPENWEBUI_OPENCLAW_QUICK_CONFIG.md) | One-command integration setup for Open WebUI, OpenClaw, and Hermes |
| [Integration Config Generator](docs/INTEGRATION_CONFIG_GENERATOR.md) | Generate configuration snippets for local AI tools |
| [Gateway Prototype Plan](docs/GATEWAY_PROTOTYPE_PLAN.md) | Phased gateway evolution from dry-run to local controller |
| [Console UX](docs/CONSOLE_UX.md) | Terminal output style guide |
| [Showcase Plan](docs/SHOWCASE_PLAN.md) | How to present Kimari honestly and attractively |

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

## 🏛️ Community & Contribution

- **Code of Conduct** — [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) (Contributor Covenant 3.0)
- **Contributing Guide** — [CONTRIBUTING.md](CONTRIBUTING.md) (setup, rules, PR process)
- **Support** — [SUPPORT.md](SUPPORT.md) (where to get help)
- **Security** — [SECURITY.md](SECURITY.md) (vulnerability reporting)
- **Governance** — [GOVERNANCE.md](GOVERNANCE.md) (project decisions and structure)
- **Maintainers** — [MAINTAINERS.md](MAINTAINERS.md) (project maintainers)
- **Issue Templates** — Use GitHub Issues for bug reports, feature requests, performance reports, and integration requests

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

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
