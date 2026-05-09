# Changelog

All notable changes to Kimari Local AI will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.2-alpha] - 2025-03-04

### Added
- `kimari pull` command for downloading GGUF models from HuggingFace
- `kimari pull --list` to list available models
- `kimari pull <name> --dry-run` to preview download
- `kimari pull <name> --force` to redownload
- `--model <path>` override for `kimari start`
- `--host <host>` override for `kimari start`
- `--port <port>` override for `kimari start`
- `--ctx <tokens>` override for `kimari start`
- Smart model fallback: suggests `kimari pull test` or available GGUF files
- `docker` GPU profile for Open WebUI usage (binds 0.0.0.0)
- Pytest test suite (`tests/`)
- Benchmark result schema and templates
- `GETTING_STARTED.md` — 10-minute quickstart guide
- `ROADMAP.md` — project roadmap
- `CHANGELOG.md` — this file
- `KIMARI_LLAMA_CPP_REF` variable in build script for reproducible builds
- CUDA compatibility table in documentation
- `--output` flag for `kimari bench` to save results to file

### Fixed
- Unified CUDA version documentation (recommended: 11.8+, best-effort: 11.0+)
- Build script now pins llama.cpp to a specific ref for reproducibility
- Model not found errors now include actionable next steps

### Changed
- Version bumped from 0.1.1-alpha to 0.1.2-alpha

## [0.1.1-alpha] - 2025-02-28

### Added
- `KIMARI_VERSION` constant in CLI
- `--dry-run` flag for `kimari start`
- JSON Schema validation for profiles config
- `requirements-dev.txt` with jsonschema, pytest, ruff
- CI workflow with py_compile, schema validation, CLI smoke tests
- `Makefile` with validate-config, validate-schema, install-dev targets

### Fixed
- Service status doc: `kimari logs` / `--json` marked as Implemented
- Quick Start in README uses `--profile test`

## [0.1.0-alpha] - 2025-02-15

### Added
- Initial alpha release
- CLI: doctor, start, stop, status, logs, chat, bench, fit, models, profiles
- GPU profiles: gtx1060, gtx1080, turbo, test
- OpenAI-compatible API via llama-server
- Open WebUI Docker integration
- Continue.dev IDE integration config
- KimariFit scoring system
- Evaluation suite (eval/)
- Documentation (12 docs)
