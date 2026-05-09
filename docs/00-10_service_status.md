# Kimari — Service Status

> **Last updated:** v0.1.4-alpha
> **Document ID:** 00-10

---

## Current Release: v0.1.4-alpha

Kimari is in early alpha. The project provides a local-first LLM toolkit focused on
GPU benchmarking, model management, and inference server orchestration for
consumer-grade NVIDIA GPUs. **No model weights are shipped** — users can download
models via `kimari pull` or provide their own GGUF files. The Kimari-4B target model
is planned but not yet released.

---

## What Works

| Component | Status | Notes |
|-----------|--------|-------|
| **CLI (`kimari`)** | ✅ Functional alpha | All core subcommands implemented |
| `kimari doctor` | ✅ Working | System health checks (GPU, CUDA, Python, llama.cpp) |
| `kimari start --profile <name>` | ✅ Working | Starts llama.cpp server with profile-based config |
| `kimari start --model/--host/--port/--ctx` | ✅ Working | Override profile settings without editing config |
| `kimari stop` | ✅ Working | Graceful server shutdown |
| `kimari status` | ✅ Working | Shows server state, PID, uptime, health |
| `kimari chat` | ✅ Working | Interactive REPL chat and single-message mode |
| `kimari bench --profile <name>` | ✅ Working | Token throughput benchmark with `--output` flag |
| `kimari fit --model <path> --ctx <n>` | ✅ Working | KimariFit score for any GGUF model |
| `kimari models` | ✅ Working | Lists available GGUF models in `models/`, `--json`, `--downloaded` |
| `kimari profiles` | ✅ Working | Lists and describes hardware profiles, `--json` |
| `kimari pull <name>` | ✅ Working | Downloads GGUF models from HuggingFace with resume and SHA256 |
| `kimari pull --list` | ✅ Working | Lists models available for download |
| `kimari pull --all` | ✅ Working | Downloads all models from registry |
| `kimari info` | ✅ Working | Shows version, paths, profiles, endpoint info |
| `kimari config path` | ✅ Working | Prints config file path |
| `kimari config show` | ✅ Working | Displays full configuration (`--json` supported) |
| `kimari config validate` | ✅ Working | Validates config against JSON Schema |
| `kimari config migrate` | ✅ Working | Migrates config to current version with backup |
| **Config system** | ✅ Working | JSON-based profiles with schema validation, migration, and `--json` output |
| **GPU profiles** | ✅ Working | gtx1060, gtx1080, turbo, test, docker profiles |
| **Scripts** | ✅ Working | Linux/Windows launch, healthcheck, smoke-test, build scripts |
| **Open WebUI** | ✅ Working | Docker compose integration with dedicated profile |
| **Automated CI** | ✅ Working | py_compile, bash syntax, JSON config, schema validation, pytest, CLI smoke test |
| **Pytest suite** | ✅ Working | 83 tests covering config, profiles, detection, state, CLI smoke, migration, security |
| **Benchmark schema** | ✅ Working | Standardized result format with templates |
| **Website/PWA** | 📋 Planned | Open WebUI available now; own PWA planned for v0.2 |

---

## What's Pending

| Feature | Priority | Status |
|---------|----------|--------|
| Kimari-4B model weights | High | Target model under development; not released yet |
| Real GPU benchmarks | High | Values in profiles are estimated, not measured |
| Fine-tuning pipeline | High | Dataset spec written; training pipeline not built |
| PWA (own web app) | Medium | Planned for v0.2 |
| Tauri desktop app | Medium | Design spec written; implementation not started |
| VRAM usage reporting | Low | Planned — requires nvidia-smi/psutil integration |
| Multi-GPU support | Low | Single-GPU only for now |
| Streaming API in CLI | Low | llama.cpp supports it; CLI doesn't expose it yet |
| `kimari eval` command | Low | Evaluation suite exists but no CLI command yet |

---

## Roadmap

### v0.1.0 — Alpha
- [x] CLI with core subcommands
- [x] Profile-based configuration with JSON schema
- [x] Basic website
- [x] System health checks
- [x] Documentation foundation

### v0.1.1 — Alpha
- [x] Version constants, JSON Schema validation, requirements-dev, Makefile

### v0.1.2 — Alpha
- [x] `kimari pull` (model download)
- [x] `--model`, `--host`, `--port`, `--ctx` overrides for `kimari start`
- [x] Docker/Open WebUI profile
- [x] Pytest test suite
- [x] Benchmark result schema and templates
- [x] Automated CI (compile, lint, config, schema, pytest)

### v0.1.3 — Alpha
- [x] Modular Python package (`pip install -e .`)
- [x] `kimari info` and `kimari config` commands
- [x] Config migration system with `config_version`
- [x] Model registry with extended metadata
- [x] SHA256 hash verification and resume support
- [x] `--json` output for all commands
- [x] SECURITY.md and PRIVACY.md

### v0.1.4 — Alpha (current)
- [x] `kimari bench --vram` override
- [x] AMD ROCm build script
- [x] Enhanced test coverage (83 tests)
- [x] CI improvements (build-package, ruff format, HTTPS validation)

### v0.2 — Beta
- [ ] Real GPU benchmark data for all supported cards
- [ ] Kimari-4B base model selection and release
- [ ] Streaming chat responses in CLI
- [ ] PWA (own lightweight web app)
- [ ] VRAM usage reporting in `kimari status`
- [ ] `kimari eval` command for evaluation suite

### v0.5 — Release Candidate
- [ ] Fine-tuning pipeline
- [ ] Kimari-4B instruction-tuned release
- [ ] Multi-GPU orchestration
- [ ] Tauri desktop app MVP
- [ ] Full PWA with offline mode
- [ ] RAG support
- [ ] Tool/function calling

### v1.0 — Stable
- [ ] Production-ready CLI
- [ ] Comprehensive documentation
- [ ] Plugin system for custom profiles
- [ ] Community model registry
- [ ] Automated CI/CD with GPU testing
- [ ] Authentication for network deployment

---

## Known Limitations

1. **Single GPU only** — Kimari currently targets one NVIDIA GPU per machine.
   Multi-GPU setups are not supported.

2. **NVIDIA-focused** — AMD ROCm build script is available (`scripts/linux/build-llamacpp-rocm.sh`)
   but not tested. Apple Silicon (Metal) is not supported.

3. **Benchmark data is estimated** — The benchmark values in profiles are
   projected estimates, not measured values. Real benchmarks are a priority for
   v0.2.

4. **Kimari-4B not released** — The gtx1060/gtx1080 profiles reference Kimari-4B
   GGUF files which are not yet available. Use `kimari pull test` or `--model` to
   override with any compatible GGUF.

5. **No fine-tuning yet** — The `kimari fit` command currently recommends
   profiles but does not perform actual model training. The fine-tuning pipeline
   is planned for v0.5.

6. **Linux/Windows only** — macOS is not currently a target platform due to the
   CUDA requirement.

7. **No authentication** — The local server does not require authentication.
   This is acceptable for local-only use but limits network deployment.

8. **Limited concurrency** — The server handles one request at a time by default.
   Concurrent request support depends on llama.cpp configuration.

---

## How to Check Status

Run the built-in diagnostics:

```bash
kimari doctor          # Full system diagnostics
kimari info            # Installation info (version, paths, profiles)
kimari status          # Server status
kimari config validate # Validate configuration
```
