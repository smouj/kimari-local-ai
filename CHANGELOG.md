# Changelog

All notable changes to Kimari Local AI will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.9-alpha] — 2026-05-11

### Added
- **GitHub Pages revamp** — Complete overhaul of `docs/index.html`: improved hero with explicit GPU mention, alpha honesty strip ("Kimari is the framework. Kimari-4B is not released yet."), reordered sections (Quick Start before Features), new Hardware Targets section, Trust section ("What We Don't Claim"), topics chips, improved footer with doc links, additional docs in grid (WSL2, Publishing, Release Checklist, Roadmap)
- **SEO and social metadata** — Added canonical URL, meta keywords, Open Graph tags (og:title, og:description, og:type, og:url, og:image), Twitter Card tags (twitter:card, twitter:title, twitter:description, twitter:image), and JSON-LD SoftwareApplication structured data to `docs/index.html`
- **Accessibility improvements** — Hamburger button changed to `<button>` with `aria-label`, `aria-expanded`, `aria-controls`; navigation has `aria-label`; terminal tabs have `role="tablist"`/`role="tab"`/`role="tabpanel"` with `aria-selected`; all external links use `rel="noopener noreferrer"`; images have descriptive `alt` text
- **docs/INSTALL_WSL2.md** — Complete WSL2 installation guide covering: Windows 10/11 requirements, Ubuntu setup, NVIDIA driver notes, CUDA on WSL, clone/install/build/pull/start flow, Open WebUI optional setup, and troubleshooting (nvidia-smi missing, nvcc missing, llama-server missing, port busy, model not found, CUDA OOM)
- **docs/PUBLISHING.md** — Manual publishing guide for TestPyPI and PyPI: pre-publish checklist, clean/build/check/upload workflow, TestPyPI install verification in clean venv, production PyPI steps, GitHub release/tag creation, API token configuration, .pypirc setup, and common issues
- **RELEASE_CHECKLIST.md improved** — Added checks for: GitHub Pages review, SEO metadata, WSL2 guide, publishing guide, README links to Release Checklist, ROADMAP current version marking, no false claims, GitHub topics accuracy, TestPyPI result recording
- **scripts/release/check-release.py improved** — Now 10 validation categories (was 7): added README links to Release Checklist check, ROADMAP "Current" marking check, docs/index.html version presence, canonical URL, og:title, og:image checks, docs/INSTALL_WSL2.md existence, docs/PUBLISHING.md existence, RELEASE_CHECKLIST.md existence, and "Kimari-4B released" false claim detection
- **New tests** — `tests/test_release_v019.py` with 12 tests: index.html version, canonical URL, Open Graph metadata, Twitter Card, JSON-LD, WSL2 guide existence, WSL2 troubleshooting, publishing guide existence, TestPyPI mention, release check script, README Kimari-4B honesty

### Changed
- **Version bumped** to `0.1.9-alpha`
- **Section order in GitHub Pages** — Quick Start now appears before Features for better conversion
- **docs/index.html version strings** — All terminal output examples updated to v0.1.9-alpha

## [0.1.8-alpha] — 2026-05-10

### Added
- **GitHub topics** — Added 20 discovery topics to the repository (ai, openai, llm, local-ai, local-llm, on-device-ai, offline-ai, self-hosted-ai, llama-cpp, gguf, quantization, llm-inference, cuda, nvidia-gpu, gtx1060, gtx1080, consumer-gpu, openai-compatible-api, open-webui, openclaw)
- **pyproject.toml keywords** — Updated from 6 generic keywords to 12 targeted discovery keywords: ai, llm, local-ai, local-llm, llama-cpp, gguf, cuda, nvidia, openai-compatible-api, open-webui, consumer-gpu, quantization
- **RELEASE_CHECKLIST.md** — Pre-release validation checklist covering version consistency, testing, CLI validation, build/package verification, content review, and publishing steps (including TestPyPI workflow)
- **scripts/release/check-release.py** — Automated release validation script that checks: version consistency (pyproject.toml vs __init__.py), README badge, CHANGELOG entry, ROADMAP entry, default_profile=="test", py.typed existence, no GGUF files tracked, no unsafe paths in models registry, no runtime artifacts in project root
- **CI release-check job** — New CI job that runs `python scripts/release/check-release.py` to catch release hygiene issues before merge
- **TestPyPI publishing documentation** — Added step-by-step TestPyPI workflow to RELEASE_CHECKLIST.md (manual only, no automated PyPI publishing from CI)

### Changed
- **Version bumped** to `0.1.8-alpha`

## [0.1.7-alpha] — 2026-05-09

### Changed
- **Ruff lint cleanup** — Fixed all 115+ ruff warnings across `kimari/` and `tests/`. Both `ruff check` and `ruff format --check` now pass with zero errors
- **Makefile** — Rewrote with proper tabs (was 8 spaces, which broke `make`). Added `format-check` step to `ci-local`. Now `make -n` passes for all targets
- **CI quoting fix** — Added quotes around `pip install "ruff>=0.5.0"` and `"jsonschema>=4.0.0"` in `.github/workflows/ci.yml` to prevent shell redirection
- **Windows scripts** — Updated `start-kimari-1060.ps1`, `start-kimari-1080.ps1`, `launch-kimari.bat`, and `healthcheck.ps1` to prefer `kimari start` command with `python -m` fallback. Changed `healthcheck.ps1` default profile from `"gtx1060"` to `"test"`
- **Version bumped** to `0.1.7-alpha`

### Added
- **New CI job: `validate-makefile`** — Runs `make -n` on key targets to catch tab/syntax issues
- **New CI job: `installed-cli-smoke`** — Tests `kimari --version`, `kimari info`, `kimari start --dry-run`, `kimari config validate` via the installed entry point (after `pip install -e .`)
- **New CI step: package contents validation** — Verifies wheel doesn't contain `models/`, `.kimari/`, `kimari-server.log`, or other runtime artifacts
- **New test: `test_installed_kimari_entry_point`** — Verifies `kimari` entry point is correctly defined in `pyproject.toml`
- **`ci-local` Makefile target** — Now runs 5 steps: validate-config, py_compile, ruff check, ruff format --check, pytest

### Fixed
- **Makefile tabs** — All recipe lines now use real tabs instead of 8 spaces. `make` commands now work correctly
- **Python type annotations** — Migrated from `Optional[X]` to `X | None` throughout (Python 3.10+ requirement)
- **Unused imports** — Removed `socket`, `pathlib.Path`, `load_models_registry`, `verify_model_hash`, `platform`, `os`, `sys`, `json`, `tempfile`, `load_config` from files where they were unused
- **F-strings without placeholders** — Removed extraneous `f` prefix from 8+ strings
- **Context managers** — `open(LOG_FILE, "w")` now uses `with` statement; removed unnecessary `"r"` mode from `open()` calls
- **Exception chaining** — Added `from None` to `raise SystemExit(1)` in except clauses for cleaner tracebacks

## [0.1.6-alpha] — 2026-05-09

### Added
- **`kimari start` without `--profile`** — The `--profile` flag is now optional for `kimari start`. When omitted, the default profile from config is used (currently `test`). This enables the ideal first-run flow: `kimari pull test` → `kimari start`
- **ROCm detection in `check-env.py`** — Both `scripts/common/check-env.py` and `scripts/linux/check-env.py` now detect `hipcc` and report "ROCm: available (experimental)". ROCm is never presented as equivalent to CUDA
- **New Makefile targets:** `bench-1080`, `bench-1060`, `dry-run`
- **New CI smoke test:** `kimari start --dry-run` (without `--profile`) verifies the default profile works
- **New CI packaging test:** Verifies `kimari/py.typed` is included in the built wheel
- **New test file:** `tests/test_hardening_v016.py` with tests for:
  - `default_profile == "test"` assertion
  - `kimari/py.typed` existence
  - Test profile model size coherence with registry
  - `kimari start --dry-run` without `--profile`
  - Bench defaults to `test` profile

### Changed
- **`make bench`** — Now uses `--profile test` instead of `--profile gtx1080`. Added `bench-1080` and `bench-1060` targets for specific profiles
- **`scripts/linux/install-dev.sh`** — Removed `bc` dependency for Python version check. Now uses `sys.version_info >= (3, 10)` directly via Python
- **CLI error messages** — Changed "Start it first: kimari start --profile \<profile\>" to "Start it first: kimari start" in chat and logs commands
- **`doctor` recommendation** — Changed from `kimari start --profile <profile>` to `kimari start`
- **All `config.get("default_profile", "gtx1060")` fallbacks** — Changed to `config.get("default_profile", "test")` throughout CLI code
- **`config/kimari.profiles.json`** — Fixed `estimated_model_size_gb` for `test` profile from `2.5` to `0.7` (coherent with `kimari.models.json` registry)
- **`scripts/linux/install-dev.sh`** — Updated quick-start hints to use `kimari start --dry-run` instead of `kimari start --profile test --dry-run`
- **Version bumped** to `0.1.6-alpha`

### Fixed
- **Profile size inconsistency** — `test` profile `estimated_model_size_gb` was 2.5 but TinyLlama Q4_K_M is 0.7 GB per registry. Now coherent at 0.7
- **Makefile bench default** — Was using `gtx1080` profile but alpha experience centers on `test`. Now `make bench` uses `test`
- **`bc` dependency** — `install-dev.sh` required `bc` which is not always installed on minimal systems. Replaced with pure Python check

## [0.1.5-alpha] — 2026-05-09

### Added
- **`kimari/py.typed`** — PEP 561 type marker for the `kimari` package
- **`scripts/common/check-env.py`** — Cross-platform environment check script (moved from `scripts/linux/`)
- **New default profile: `test`** — The default profile is now `test` (TinyLlama) instead of `gtx1060` during alpha, since Kimari-4B is not yet published

### Changed
- **Default profile changed to `test`** — `kimari start` now uses the `test` profile by default, ensuring first-run success after `kimari pull test`. The `gtx1060` profile remains available for when Kimari-4B is released
- **`scripts/linux/start-kimari.sh`** — Now prefers the installed `kimari` command, falls back to `python3 -m kimari.cli.main`. Default profile changed from `gtx1060` to `test`
- **ASCII banner** — Replaced the ambiguous ASCII art with a clear "KIMARI" block-letter banner
- **ROCm support** — Marked as **experimental** in documentation. AMD ROCm builds are available via `scripts/linux/build-llamacpp-rocm.sh` but are not yet tested at parity with CUDA
- **Dates corrected** — All changelog entries and documentation dates updated from `2025` to `2026`
- **Version bumped** to `0.1.5-alpha`

### Fixed
- **`pyproject.toml`** — Now correctly ships `kimari/py.typed` (previously declared but missing from the package)
- **`scripts/windows/install-dev.ps1`** — No longer references `scripts/linux/check-env.py`; uses `scripts/common/check-env.py` instead
- **`scripts/linux/install-dev.sh`** — Updated to use `scripts/common/check-env.py`
- **README.md** — Fixed `check-env.py` path reference

### Documentation
- README.md updated to reflect `test` as default profile and streamlined first-run flow
- GETTING_STARTED.md updated with clearer instructions
- docs/COMPARISON.md — ROCm marked as experimental, date corrected
- docs/PROJECT_STRUCTURE.md — Updated with `scripts/common/` directory and `kimari/py.typed`
- PRIVACY.md — "Last updated" corrected to 2026
- Added SHA256 verification note: model hashes in the registry are not yet pinned; verification is supported but not enforced

## [0.1.4-alpha] — 2026-05-09

### Added
- **`kimari bench --vram`** — Override VRAM in GiB for benchmark output on systems without GPU
- **`llama_cpp_version`** — Detects llama.cpp version in benchmark output (via `llama-server --version`)
- **`benchmarks/SCHEMA.md`** — Documented the standardized benchmark result JSON schema
- **`scripts/linux/build-llamacpp-rocm.sh`** — Build llama.cpp with AMD ROCm/HIP support
  - Configurable `KIMARI_AMDGPU_TARGETS` env var (default: gfx900 through gfx1101)
  - Same pinned ref approach as CUDA build script
- **CI improvements:**
  - `build-package` job — builds the package with `python -m build` and validates with `twine check`
  - `ruff format --check` step in lint-python job
  - HTTPS URL validation in models registry validation step
- **Enhanced test coverage:**
  - Config migration tests (`test_migrate_config_current_no_changes`)
  - Security validation tests (`test_validate_config_catches_0000_host`, `test_validate_config_catches_absolute_path`, `test_validate_config_catches_invalid_port`)
  - Model hash verification tests (`test_verify_model_hash_unknown_model`, `test_pull_all_models_runs`)
  - Total: 83 tests (up from 77)
- **SECURITY.md** — Added "Optional API Authentication (Future)" section with nginx workaround example
- **COMPARISON.md** — Added AMD ROCm build script mention in llama.cpp comparison and "When NOT to Use" section

### Fixed
- **Test profile model path** — Changed from non-existent `Kimari-base-test-Q4_K_M.gguf` to `tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf` (matches `kimari pull test`)
- **PRIVACY.md** — Fixed incorrect file paths (`server/kimari.pid` → `.kimari-server.pid`, `server/kimari.log` → `kimari-server.log`)
- **CI workflow** — Fixed YAML syntax error in `lint-scripts` job (missing `steps:` key)
- **Model registry** — Removed duplicate `qwen3-4b-q4` entry (identical to `recommended`)
- **Documentation** — Fixed all remaining references to old model name across docs, models/README.md, and index.html

### Changed
- Version bumped to 0.1.4-alpha
- ROADMAP.md updated — v0.1.3-alpha marked as released, v0.1.4-alpha as current
- docs/PROJECT_STRUCTURE.md updated with new files (SCHEMA.md, build-llamacpp-rocm.sh)
- Makefile updated with `build-rocm` target

## [0.1.3-alpha] — 2026-05-09

### Added
- **Modular Python package** (`kimari/`) with proper `__init__.py` modules
  - `kimari/cli/main.py` — CLI argument parsing and command dispatch
  - `kimari/core/constants.py` — Paths, version, ASCII art
  - `kimari/core/state.py` — Server state management
  - `kimari/core/errors.py` — Log error pattern detection
  - `kimari/core/detection.py` — GPU, CUDA, llama-server detection
  - `kimari/config/loader.py` — Config loading, validation, migration
  - `kimari/models/registry.py` — Model registry, downloads, hash verification
  - `kimari/profiles/manager.py` — Profile listing and display
  - `kimari/benchmarks/bench.py` — Benchmark runner with TTFT
  - `kimari/benchmarks/kimarifit.py` — KimariFit score calculation
  - `kimari/utils/colors.py` — Terminal color helpers
- **`pyproject.toml`** — Package configuration with `kimari` entry point
  - Install with `pip install -e .` or `pip install -e ".[dev]"`
  - `kimari` command available after install
- **New CLI commands:**
  - `kimari info` — Show version, paths, profiles, endpoint (no API call)
  - `kimari info --json` — JSON output for IDEs/agents
  - `kimari config path` — Print config file absolute path
  - `kimari config show` — Display full configuration
  - `kimari config show --json` — JSON config output
  - `kimari config validate` — Validate config against JSON Schema
  - `kimari config migrate` — Migrate config to current version with backup
  - `kimari config migrate --dry-run` — Preview migration changes
  - `kimari models --json` — Structured model listing
  - `kimari models --downloaded` — List only downloaded models
  - `kimari models --status recommended|experimental` — Filter by status
  - `kimari profiles --json` — JSON profile output
  - `kimari pull --all` — Download all models from registry
- **Config migration system** with `config_version` field (v2)
  - Automatic backup before migration
  - Security validation: `0.0.0.0` warning, port range check, absolute path detection
- **Enhanced model registry** (`kimari.models.json` v2):
  - New fields: `family`, `status`, `expected_vram_gb`, `license`, `source`, `sha256`
  - Model status: `test`, `recommended`, `experimental`, `planned`
- **Model download improvements:**
  - Resume support for interrupted downloads
  - SHA256 hash verification after download
  - Progress bar with ETA and speed
  - HTTPS warning for HTTP URLs
- **Benchmark improvements:**
  - Time-to-first-token (TTFT) measurement via streaming
  - More prompts including Spanish technical questions
  - Results saved with `<profile>-<date>.json` naming
- **KimariFit `--vram` override** for machines without GPU detection
- **`doctor` improvements:** CUDA version detection, config version check, security warning for `0.0.0.0`
- **Security warnings** when binding to `0.0.0.0` (not `docker` profile)
- **Backward compatibility:** `cli/kimari_cli.py` remains as thin wrapper

### Changed
- CLI now invoked via `python -m kimari.cli.main` or `kimari` command
- Makefile updated to use new package paths
- CI workflow updated with Python 3.10/3.11/3.12 matrix
- Config schema updated: `config_version` required, port minimum raised to 1024
- Tests updated to import from `kimari.*` package modules
- `requirements-dev.txt` unchanged; `pyproject.toml` defines runtime deps

### Documentation
- **`docs/PROJECT_STRUCTURE.md`** — Codebase organization guide
- **`docs/COMPARISON.md`** — Honest comparison with Ollama, LM Studio, llama.cpp, etc.
- **`docs/WEB_UI_PLAN.md`** — Realistic plan for web UI (v0.2–v1.0)
- **`SECURITY.md`** — Security policy, port risks, hash verification, vulnerability reporting
- **`PRIVACY.md`** — Privacy policy (no telemetry, local-first, data deletion)
- **`scripts/linux/install-dev.sh`** — Development setup script
- **`scripts/windows/install-dev.ps1`** — Windows development setup
- **`scripts/linux/check-env.py`** — Environment verification script
- README.md updated with new commands, pip install instructions, and links
- ROADMAP.md updated with v0.1.3-alpha changes and future plans

## [0.1.2-alpha] — 2026-05-08

### Added
- `kimari pull` command for downloading GGUF models from registry
- `kimari pull --list` to list available models
- `kimari pull --dry-run` and `--force` flags
- Model registry in `config/kimari.models.json`
- `docker` profile for Open WebUI integration
- `--model`, `--host`, `--port`, `--ctx` overrides for `kimari start`
- Smart model fallback messages (scan `models/` for alternatives)
- `--output` flag for `kimari bench` to save structured JSON results
- `--json` output for `kimari doctor` and `kimari status`
- `--daemon` flag for `kimari start`
- Benchmark result templates in `benchmarks/templates/`
- Benchmark prompts in `benchmarks/prompts/` (including Spanish technical)
- `GETTING_STARTED.md` for quick start
- `ROADMAP.md` and `CHANGELOG.md`
- Issue/PR templates in `.github/`
- Pytest test suite (9 test files, 39+ tests)
- CI workflow with config validation, py_compile, and pytest
- `make ci-local`, `make test`, `make lint` targets

## [0.1.1-alpha] — 2026-05-07

### Added
- Version constant `KIMARI_VERSION` in CLI
- JSON Schema validation for profiles (`kimari.profiles.schema.json`)
- `additionalProperties: false` in schema
- Required `endpoints` in server config
- Expanded `cache_type_k/v` and `gpu_layers` enums
- `requirements-dev.txt` with pytest, ruff, jsonschema
- Makefile with common development targets
- Documentation in `docs/` (vision, architecture, KimariFit, etc.)

## [0.1.0-alpha] — 2026-05-06

### Added
- Initial release of Kimari Local AI
- CLI: `doctor`, `start`, `stop`, `status`, `chat`, `bench`, `fit`, `models`, `profiles`, `logs`
- GPU profiles: `gtx1060`, `gtx1080`, `turbo`, `test`
- llama.cpp server management with PID tracking
- Error pattern detection from logs (OOM, CUDA errors, port busy)
- Interactive chat mode
- KimariFit VRAM estimation and scoring
- OpenAI-compatible API via llama-server
