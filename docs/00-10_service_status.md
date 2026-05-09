# Kimari — Service Status

> **Last updated:** v0.1-alpha
> **Document ID:** 00-10

---

## Current Release: v0.1-alpha

Kimari is in early alpha. The project provides a local-first LLM toolkit focused on
GPU benchmarking, model management, and inference server orchestration for
consumer-grade NVIDIA GPUs.

---

## What Works

| Component | Status | Notes |
|-----------|--------|-------|
| **CLI (`kimari`)** | ✅ Functional | All core subcommands implemented |
| `kimari doctor` | ✅ Working | System health checks (GPU, CUDA, Python, llama.cpp) |
| `kimari start` | ✅ Working | Starts llama.cpp server with profile-based config |
| `kimari stop` | ✅ Working | Graceful server shutdown |
| `kimari status` | ✅ Working | Shows server state, PID, uptime, memory usage |
| `kimari chat` | ✅ Working | Interactive REPL chat against the running server |
| `kimari bench` | ✅ Working | Token throughput benchmark (prompt eval + generation) |
| `kimari fit` | ✅ Working | Profile recommendation based on detected GPU |
| `kimari models` | ✅ Working | Lists available / recommended GGUF models |
| `kimari profiles` | ✅ Working | Lists and describes hardware profiles |
| **Config system** | ✅ Working | JSON-based profiles (`kimari.profiles.json`) |
| **Scripts** | ✅ Working | Linux/Windows launch, healthcheck, smoke-test, build scripts |
| **Website** | ✅ Working | Landing page with project info and PWA support |

---

## What's Pending

| Feature | Priority | Status |
|---------|----------|--------|
| Real GPU benchmarks | High | Placeholder values; need actual measured data |
| Actual model training / fine-tuning | High | Dataset spec written; training pipeline not built |
| PWA offline support | Medium | Basic PWA shell; offline caching incomplete |
| Tauri desktop app | Medium | Design spec written; implementation not started |
| Multi-GPU support | Low | Single-GPU only for now |
| Model download manager | Medium | Manual download; no integrated fetch |
| Streaming API | Low | llama.cpp supports it; CLI doesn't expose it yet |
| Automated CI/CD | Low | No test pipeline yet |

---

## Roadmap

### v0.1 — Alpha (current)
- [x] CLI with core subcommands
- [x] Profile-based configuration
- [x] Basic website
- [x] System health checks
- [x] Documentation foundation

### v0.2 — Beta
- [ ] Real GPU benchmark data for all supported cards
- [ ] Integrated model download (`kimari pull`)
- [ ] Streaming chat responses
- [ ] Improved error messages and recovery suggestions
- [ ] Basic test suite

### v0.5 — Release Candidate
- [ ] Fine-tuning pipeline (`kimari fit` with real training)
- [ ] Multi-GPU orchestration
- [ ] Tauri desktop app MVP
- [ ] Full PWA with offline mode
- [ ] User guide and tutorial content

### v1.0 — Stable
- [ ] Production-ready CLI
- [ ] Comprehensive documentation
- [ ] Plugin system for custom profiles
- [ ] Community model registry
- [ ] Automated CI/CD with GPU testing

---

## Known Limitations

1. **Single GPU only** — Kimari currently targets one NVIDIA GPU per machine.
   Multi-GPU setups are not supported.

2. **NVIDIA-only CUDA** — AMD (ROCm) and Apple Silicon (Metal) backends are not
   yet implemented. Only NVIDIA CUDA is supported.

3. **Benchmark data is estimated** — The benchmark values in profiles are
   projected estimates, not measured values. Real benchmarks are a priority for
   v0.2.

4. **No model download integration** — Users must manually download GGUF files
   from HuggingFace or other sources. An integrated downloader is planned.

5. **No fine-tuning yet** — The `kimari fit` command currently recommends
   profiles but does not perform actual model training.

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
