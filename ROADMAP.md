# Kimari Local AI — Roadmap

## v0.1.3-alpha (Current)

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

## v0.1.4-alpha (Planned)

- Extended test coverage (config migration, model hash verification)
- Windows/WSL installation improvements
- Advanced security: optional API authentication token
- Model download progress with ETA
- `kimari eval` command for evaluation suite
- Package published on PyPI (or TestPyPI)
- More models in registry

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
