# Kimari Local AI — Roadmap

## v0.1.3-alpha (Released)

- ✅ Modular Python package (`kimari/`) with `pyproject.toml`
- ✅ `kimari info` command — installation info and paths
- ✅ `kimari config path/show/validate/migrate` subcommands
- ✅ `config_version` field and migration system
- ✅ `--json` output for `doctor`, `info`, `profiles`, `models`, `status`
- ✅ Model registry with `family`, `status`, `expected_vram_gb`, `sha256`
- ✅ `kimari pull --all` for bulk downloads
- ✅ Resume support and SHA256 hash verification for model downloads
- ✅ `kimari models --downloaded/--status/--json`
- ✅ `kimari fit --vram` override for machines without GPU
- ✅ Benchmark TTFT measurement via streaming
- ✅ Security warnings for `0.0.0.0` binding
- ✅ `SECURITY.md` and `PRIVACY.md`
- ✅ `docs/COMPARISON.md` — objective comparison with alternatives
- ✅ `docs/WEB_UI_PLAN.md` — web UI roadmap
- ✅ `docs/PROJECT_STRUCTURE.md` — codebase organization
- ✅ Test suite updated for new package structure
- ✅ CI with Python 3.10/3.11/3.12 matrix
- ✅ Install scripts (`install-dev.sh`, `install-dev.ps1`, `check-env.py`)

## v0.1.4-alpha (Released)

- ✅ Fixed test profile model path (tinyllama instead of non-existent Kimari-base-test)
- ✅ Fixed PRIVACY.md path references to match actual file locations
- ✅ Fixed CI workflow YAML syntax error in lint-scripts job
- ✅ Removed duplicate model entry in `kimari.models.json`
- ✅ `kimari bench --vram` override for systems without GPU detection
- ✅ `llama_cpp_version` detection in benchmark output
- ✅ `benchmarks/SCHEMA.md` — documented benchmark result JSON schema
- ✅ `scripts/linux/build-llamacpp-rocm.sh` — AMD ROCm build support
- ✅ Enhanced test coverage (config migration, security validation, hash verification)
- ✅ CI improvements: build-package job, ruff format check, HTTPS URL validation
- ✅ SECURITY.md updated with optional API authentication section
- ✅ COMPARISON.md updated with ROCm mention
- ✅ Fixed all documentation references to match actual model paths
- ✅ Updated docs/PROJECT_STRUCTURE.md with new files

## v0.1.5-alpha (Released)

- ✅ Default profile changed to `test` for seamless first-run experience
- ✅ `kimari/py.typed` created (PEP 561 marker)
- ✅ `scripts/common/check-env.py` — cross-platform environment check
- ✅ `scripts/linux/start-kimari.sh` — prefers `kimari` command, defaults to `test` profile
- ✅ ASCII banner fixed to clearly read "KIMARI"
- ✅ ROCm marked as **experimental** in documentation
- ✅ All documentation dates corrected from 2025 to 2026
- ✅ SHA256 verification note added (hashes not yet pinned in registry)
- ✅ README and GETTING_STARTED updated for new default flow

## v0.1.6-alpha (Released)

- ✅ `kimari start` works without `--profile` (uses default from config)
- ✅ All `default_profile` fallbacks changed from `"gtx1060"` to `"test"`
- ✅ Fixed `test` profile `estimated_model_size_gb` (2.5 → 0.7, coherent with registry)
- ✅ `make bench` now uses `--profile test`; added `bench-1080` and `bench-1060`
- ✅ Removed `bc` dependency from `install-dev.sh` (uses Python version check)
- ✅ CLI error messages simplified ("Start it first: kimari start" instead of "--profile")
- ✅ ROCm detection in `check-env.py` (experimental, not equivalent to CUDA)
- ✅ CI: dry-run without `--profile`, `py.typed` in wheel verification
- ✅ New tests: default_profile, py.typed existence, profile size coherence, start without profile

## v0.1.7-alpha (Released)

- ✅ Ruff lint/format cleanup — all 115+ warnings fixed, `ruff check` and `ruff format --check` pass
- ✅ Makefile fixed with proper tabs (was 8 spaces)
- ✅ CI shell quoting fix (pip install with `>=` now quoted)
- ✅ New CI job: `validate-makefile` (make -n dry-run, bench)
- ✅ New CI job: `installed-cli-smoke` (tests `kimari` entry point after pip install)
- ✅ New CI step: package contents validation (no unwanted files in wheel)
- ✅ Windows scripts updated: prefer `kimari start`, default profile `test`
- ✅ Python type annotations: `Optional[X]` → `X | None` throughout
- ✅ `ci-local` now runs ruff check + ruff format --check

## v0.1.8-alpha (Current)

- ✅ GitHub topics — 20 discovery topics added (ai, llm, local-ai, gguf, cuda, openai-compatible-api, etc.)
- ✅ pyproject.toml keywords — 12 targeted discovery keywords
- ✅ RELEASE_CHECKLIST.md — pre-release validation checklist with TestPyPI workflow
- ✅ scripts/release/check-release.py — automated release validation script
- ✅ CI release-check job — runs check-release.py in CI
- ✅ TestPyPI publishing documentation (manual workflow)

## v0.1.9-alpha (Planned)

- TestPyPI real validation (actual upload and install test)
- Real SHA256 hashes if computable reliably
- WSL2 installation guide
- More robust Windows launcher
- Optional `kimari setup` interactive command

## v0.2.0-alpha

- Local REST API via FastAPI (`kimari api`)
- VRAM reporting in real-time
- Benchmark result comparison
- Improved documentation for IDE integration

## v0.3.0-alpha

- Minimal web dashboard (status, start/stop, model list, logs)
- Based on `docs/WEB_UI_PLAN.md`
- React/Tailwind or Svelte frontend

## v0.4.0-alpha

- PWA with model management
- Benchmark launcher from web UI
- Diagnostics export

## v0.5.0-alpha

- Tauri desktop application
- System tray integration
- Native notifications

## v1.0.0

- Stable API
- Production-ready desktop app
- Community benchmarks and model contributions
- Full documentation in multiple languages
