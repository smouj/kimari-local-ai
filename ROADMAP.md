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

## v0.1.4-alpha (Current)

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

## v0.1.5-alpha (Planned)

- Windows/WSL installation improvements
- `kimari eval` command for evaluation suite
- Package published on PyPI (or TestPyPI)
- More models in registry
- Advanced security: optional API authentication token implementation

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
