# Kimari — Service Status

> **Last updated:** v0.1.2-alpha
> **Document ID:** 00-10

---

## Current Release: v0.1.2-alpha

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
| `kimari models` | ✅ Working | Lists available GGUF models in `models/` |
| `kimari profiles` | ✅ Working | Lists and describes hardware profiles |
| `kimari pull <name>` | ✅ Working | Downloads GGUF models from HuggingFace |
| `kimari pull --list` | ✅ Working | Lists models available for download |
| **Config system** | ✅ Working | JSON-based profiles with schema validation |
| **GPU profiles** | ✅ Working | gtx1060, gtx1080, turbo, test, docker profiles |
| **Scripts** | ✅ Working | Linux/Windows launch, healthcheck, smoke-test, build scripts |
| **Open WebUI** | ✅ Working | Docker compose integration with dedicated profile |
| **Automated CI** | ✅ Working | py_compile, bash syntax, JSON config, schema validation, pytest, CLI smoke test |
| **Pytest suite** | ✅ Working | 50+ tests covering config, profiles, detection, state, CLI smoke |
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

### v0.1.2 — Alpha (current)
- [x] CLI with core subcommands
- [x] Profile-based configuration with JSON schema
- [x] Basic website
- [x] System health checks
- [x] Documentation foundation
- [x] Automated CI (compile, lint, config, schema, pytest)
- [x] Test profile for runtime validation
- [x] `kimari pull` (model download)
- [x] `--model`, `--host`, `--port`, `--ctx` overrides for `kimari start`
- [x] Docker/Open WebUI profile
- [x] Pytest test suite
- [x] Benchmark result schema and templates
- [x] CUDA documentation unified

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

2. **NVIDIA-only CUDA** — AMD (ROCm) and Apple Silicon (Metal) backends are not
   yet implemented. Only NVIDIA CUDA is supported.

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
kimari doctor
```

This reports:
- GPU detection and VRAM
- CUDA toolkit version
- Python version and dependencies
- llama.cpp build status
- Config file validity
- Recommended profile
