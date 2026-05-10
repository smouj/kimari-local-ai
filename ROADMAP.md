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

## v0.1.8-alpha (Released)

- ✅ GitHub topics — 20 discovery topics added (ai, llm, local-ai, gguf, cuda, openai-compatible-api, etc.)
- ✅ pyproject.toml keywords — 12 targeted discovery keywords
- ✅ RELEASE_CHECKLIST.md — pre-release validation checklist with TestPyPI workflow
- ✅ scripts/release/check-release.py — automated release validation script
- ✅ CI release-check job — runs check-release.py in CI
- ✅ TestPyPI publishing documentation (manual workflow)

## v0.1.9-alpha (Released)

- ✅ GitHub Pages revamp — hero, alpha honesty strip, Quick Start before Features, Hardware Targets, Trust section, topics chips, improved footer
- ✅ SEO/social metadata — canonical URL, Open Graph, Twitter Cards, JSON-LD SoftwareApplication
- ✅ Accessibility — aria labels, role attributes, semantic button, alt text
- ✅ docs/INSTALL_WSL2.md — complete WSL2 installation guide with troubleshooting
- ✅ docs/PUBLISHING.md — manual TestPyPI/PyPI publishing guide
- ✅ RELEASE_CHECKLIST.md — added SEO, WSL2, publishing, GitHub Pages checks
- ✅ check-release.py — 10 validation categories including SEO, docs, false claim detection

## v0.1.10-alpha (Released)

- ✅ Performance estimation module — VRAM/RAM estimation with confidence levels and warnings
- ✅ GGUF metadata reader — Lightweight reader for model architecture data
- ✅ `kimari optimize` command — Profile analysis with mode-based recommendations
- ✅ `kimari perf` command — Performance diagnostic with matrix mode
- ✅ 8 new GPU profiles — gtx1060-safe, gtx1060-fast, gtx1080-balanced, gtx1080-longctx, ide-local, agent-local, openclaw-local, hermes-local
- ✅ New profile fields — performance_mode, flash_attn, parallel, mlock, no_mmap
- ✅ Extended build_server_cmd — --flash-attn, --parallel, --mlock, --no-mmap flags
- ✅ OpenClaw integration — docs + config example
- ✅ Hermes Agent integration — docs + config example
- ✅ Continue.dev integration — docs + config example
- ✅ Generic OpenAI-compatible client guide — curl, Python, Node.js, troubleshooting

## v0.1.11-alpha (Released)

- ✅ `kimari setup` guided environment detection command
- ✅ Runtime flag detection (`kimari/runtime/llama_flags.py`)
- ✅ `--strict-flags` option on `kimari start`
- ✅ Local auth tokens (`kimari token create/show/delete`)
- ✅ Windows launcher and doctor PowerShell scripts
- ✅ TestPyPI validation checklist in docs/PUBLISHING.md
- ✅ Release-check improvements for new modules

## v0.1.12-alpha (Current)

- ✅ Packaged defaults (`kimari/defaults/`) ship inside wheel
- ✅ User path management (`kimari/core/paths.py`) with platform-aware dirs
- ✅ Config resolution chain: user → repo-root → packaged defaults
- ✅ Short flag support in strict-flags (`-m`, `-c`, `-ngl`, `-b`, `-ub`, `-t`)
- ✅ State/tokens in user directories (not PROJECT_ROOT)
- ✅ `KIMARI_HOME` and per-path environment variable overrides
- ✅ `pyproject.toml` package-data includes `defaults/*.json`
- ✅ `kimari config path` shows active config location
- ✅ No "run from repo root" requirement after install

## v0.1.13-alpha (Planned)

- Actual TestPyPI upload/install verification
- `kimari setup` write-mode (persist detected settings)
- Real SHA256 hashes if computable reliably
- Windows installer packaging
- Optional reverse proxy auth guide
- FastAPI planning for v0.2

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
