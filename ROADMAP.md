# Kimari Local AI — Roadmap

## v0.1.2-alpha (Current)
- [x] CLI: doctor, start, stop, status, chat, bench, fit, models, profiles, logs
- [x] `kimari pull` — model download command
- [x] `--model`, `--host`, `--port`, `--ctx` overrides for `kimari start`
- [x] Model fallback when GGUF not found
- [x] Pytest test suite
- [x] Docker/Open WebUI profile
- [x] Benchmark result schema
- [x] CUDA documentation unified
- [ ] Kimari-4B model weights (planned separately)

## v0.2 (Next)
- [ ] Kimari-4B model release
- [ ] PWA web interface (lightweight, no Docker needed)
- [ ] VRAM usage reporting in `kimari status`
- [ ] `kimari eval` command for running evaluation suite
- [ ] Model auto-detection and profile recommendation
- [ ] Configuration wizard for new users

## v0.5
- [ ] Multi-model serving
- [ ] RAG (Retrieval-Augmented Generation) support
- [ ] Tool/function calling
- [ ] Model fine-tuning pipeline
- [ ] Community benchmark database

## v1.0
- [ ] Tauri desktop application
- [ ] Plugin system
- [ ] Multi-GPU support
- [ ] Production-ready authentication for network deployment
- [ ] Comprehensive documentation and tutorials
