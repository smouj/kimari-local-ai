# Changelog

All notable changes to Kimari Local AI will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.16-alpha] — 2026-05-18

### Added
- **Experimental FastAPI API skeleton** (`kimari/api/`) — `app.py`, `schemas.py`, `server.py`; opt-in via `kimari api --experimental`; does NOT start a real server yet
- **Optional `api` dependency in `pyproject.toml`** — `pip install kimari-local-ai[api]` installs FastAPI + uvicorn; core install remains lightweight
- **`kimari api --experimental` command** — Registers the API subcommand; `--dry-run` validates configuration without requiring FastAPI installed
- **API endpoints (experimental)** — Health (`GET /health`), status (`GET /status`), config (`GET /config`), profiles (`GET /profiles`), models (`GET /models`), optimize (`POST /optimize`), perf dry-run (`POST /perf/dry-run`)
- **Server start/stop return 501** — `POST /server/start` and `POST /server/stop` return HTTP 501 (Not Implemented) — planned for a future release
- **Experimental auth middleware** — Bearer token middleware present but not enforced by default; uses existing `kimari/security/tokens.py`
- **docs/API_EXPERIMENTAL.md** — Documents the current experimental status, available endpoints, installation, and usage
- **docs/PYPI_RELEASE_GATE.md** — Defines the process and criteria that must be satisfied before publishing to the real PyPI; prevents premature publishing
- **docs/MODEL_HASHING.md** — Comprehensive guide for model hash verification, pinning, and registry management
- **docs/BENCHMARK_SUBMISSIONS.md** — Guide for submitting benchmark results; documents format, validation, and community workflow
- **Benchmark examples for GTX 1060/1080** — `benchmarks/examples/perf-result.gtx1060.example.json` and `benchmarks/examples/perf-result.gtx1080.example.json`
- **Windows packaging improvements** — Enhanced `scripts/windows/` scripts with better error handling and venv management
- **Release-check improvements** — `scripts/release/check-release.py` expanded from 24 to 28 validation categories; added v0.1.16 API experimental, Windows packaging, release-check improvements, and content integrity re-check sections
- **New tests** (`tests/test_release_v0116.py`) — Tests for API module existence, optional dependency, experimental command, documentation files, benchmark examples, no false claims

### Changed
- **Version bumped** to `0.1.16-alpha`
- **`scripts/release/check-release.py`** — Renumbered all sections from /24 to /28; added sections [25/28] v0.1.16 API experimental, [26/28] Windows packaging improvements, [27/28] release-check improvements, [28/28] content integrity re-check
- **RELEASE_CHECKLIST.md** — Added v0.1.16 Checks section with API experimental dry-run, api extra dependency, new docs, benchmark examples, PyPI release gate, and no-false-claim checks
- **ROADMAP.md** — v0.1.15-alpha marked as Released; v0.1.16-alpha marked as Current; v0.1.17-alpha Planned section added
- **docs/API_PLAN.md** — Updated status note to reflect v0.1.16-alpha experimental implementation; added OpenAPI draft sync note; added security section mention
- **docs/API_OPENAPI_DRAFT.yaml** — Synced server URL to `http://127.0.0.1:11436`; added `x-experimental: true` to BearerAuth; marked POST /server/start and POST /server/stop as returning 501; added operationId and descriptions

## [0.1.15-alpha] — 2026-05-17

### Fixed
- **P0: `start_server()` model path resolution** — Replaced `PROJECT_ROOT / effective_model` with `resolve_model_path()` in the real startup path. Previously, only `--dry-run` used the resolver; the real path assumed repo-root, breaking wheel installs

### Added
- **Robust `resolve_model_path()`** — New public helper that resolves models in order: absolute path → CWD-relative → user models dir → repo-root models/ → fallback to user models dir. Works correctly when installed from wheel (no repo root)
- **`kimari setup --write --yes`** — Non-interactive mode for setup write; skips confirmation when `--yes` is provided
- **`kimari setup --write` confirmation** — Without `--yes`, requires interactive confirmation on TTY; in non-interactive environments, `--yes` is mandatory
- **Setup preview before write** — Shows summary (config_path, backup_path, selected_profile, integration, models_dir, state_dir) before writing
- **`preview_setup_changes()`** and **`apply_setup_changes()`** — New functions in `kimari/setup/writer.py` with atomic write (write .tmp then rename)
- **`kimari models pin-hash --yes`** — Non-interactive confirmation for hash pinning
- **`kimari models pin-hash --dry-run`** — Shows the patch that would be applied without writing
- **Benchmark result sharing format** — `benchmarks/RESULT_FORMAT.md` documents the JSON structure for sharing performance results; `benchmarks/examples/perf-result.example.json` provides a template
- **Windows wheel packaging scripts** — `scripts/windows/build-wheel.ps1`, `scripts/windows/install-from-wheel.ps1`, `scripts/windows/install-from-testpypi.ps1`
- **Reverse proxy auth refinement** — `docs/REVERSE_PROXY_AUTH.md` updated with Caddy `reverse_proxy` with header check, nginx `map` for Authorization, diagram (client → proxy auth → Kimari/llama-server on 127.0.0.1), "Do not expose llama-server directly" section
- **OpenAPI 3.1 draft** — `docs/API_OPENAPI_DRAFT.yaml` with planned endpoints (health, status, config, profiles, models, server start/stop, optimize, perf dry-run); marked as draft, not implemented
- **TestPyPI validation** — Documented in `docs/PUBLISHING.md` with result or credentials-unavailable notice
- **New tests** (`tests/test_release_v0115.py`) — Tests for resolve_model_path, setup --write --yes, pin-hash --dry-run, benchmark format, OpenAPI draft, Windows scripts, release check

### Changed
- **Version bumped** to `0.1.15-alpha`
- **`kimari/setup/writer.py`** — Added `preview_setup_changes()`, `apply_setup_changes()`, `confirm_setup_write()`, atomic write (write .tmp then rename)
- **`kimari/cli/main.py`** — `run_setup()` now supports `--yes` flag with confirmation prompt; `pin_model_hash()` now supports `--yes` and `--dry-run`
- **`scripts/release/check-release.py`** — Added checks for resolve_model_path helper, start_server not using PROJECT_ROOT directly, benchmark result format, OpenAPI draft, Windows wheel scripts, README mentions
- **README.md** — Added sections: model path resolution, setup --write --yes, pin-hash workflow, benchmark sharing, Windows wheel install
- **docs/index.html** — Updated for v0.1.15-alpha focus areas

## [0.1.14-alpha] — 2026-05-16

### Added
- **`kimari setup --write`** — Persists detected configuration to user config dir with automatic timestamped backup; `--json` output includes `would_write`, `written`, `config_path`, `backup_path`; no config written without explicit `--write` flag
- **Setup persistence module** (`kimari/setup/writer.py`) — `build_setup_patch()`, `write_setup_config()`, `backup_config()`, `load_setup_summary()`; pure functions, testable with `tmp_path`, no new dependencies
- **`kimari models hash <path>`** — Computes SHA256 hash of a local GGUF file; `--json` output includes `path`, `sha256`, `size_bytes`, `file_exists`
- **`kimari models verify <model-id-or-path>`** — Verifies model hash against registry; reports `match`, `mismatch`, `not_pinned`, or `computed_only`; `--json` output
- **`kimari models pin-hash <model-id>`** — Pins computed SHA256 to user registry; dry-run by default; `--write` creates backup before modifying; `--json` output
- **`get_effective_models_registry()`** — Returns merged registry (user overrides packaged defaults)
- **Reverse proxy auth guide** (`docs/REVERSE_PROXY_AUTH.md`) — nginx and Caddy examples with Bearer token validation; warning that `llama-server` does not apply auth natively; troubleshooting for 401, connection refused, wrong port, CORS
- **API plan** (`docs/API_PLAN.md`) — Technical design for v0.2.0-alpha FastAPI REST API (`kimari api`); 9 proposed endpoints; optional Bearer token auth; architecture diagram; risks and testing plan; NOT implemented yet
- **`docs/PUBLISHING.md`** — Added v0.1.14 TestPyPI actual validation section with checklist, result table, and validation commands
- **`scripts/windows/README.md`** — Added sections for wheel/TestPyPI install, `kimari setup --write`, auth tokens, and model hash verification
- **RELEASE_CHECKLIST.md** — Added Setup Write-Mode, SHA256 Tooling, and New Documentation check sections; added `setup --write`, `models hash`, `models verify` checks in Packaging & CI and Content Review sections
- **`scripts/release/check-release.py`** — Added 3 new validation categories (21 total): Setup write-mode & SHA256 tooling, New documentation files, Content integrity v0.1.14 re-check; added `_no_invented_hashes()` helper
- **New tests** (`tests/test_release_v0114.py`) — Tests for version consistency, setup writer, SHA256 tooling, documentation, README links, release check improvements, and no false claims

### Changed
- **Version bumped** to `0.1.14-alpha`
- **`kimari/cli/main.py`** — Added `--write` flag to setup parser; added `models hash`, `models verify`, `models pin-hash` subcommands; setup `run_setup()` now accepts `write` parameter and integrates with `kimari/setup/writer.py`
- **`kimari/models/registry.py`** — Added `compute_model_hash()`, `verify_model_hash_v2()`, `pin_model_hash()`, `get_effective_models_registry()`; added `datetime` and `shutil` imports
- **`README.md`** — Added setup write-mode and model hash verification sections; added links to REVERSE_PROXY_AUTH.md and API_PLAN.md; updated version badge
- **`docs/index.html`** — Updated version references to v0.1.14-alpha; added reverse proxy auth and API plan doc cards; updated status section

### Added
- **Code of Conduct** (`CODE_OF_CONDUCT.md`) — Based on Contributor Covenant 3.0; covers issues, PRs, discussions, GitHub Pages, docs, integrations; private reporting via email (no public issues); TODO: replace with dedicated contact before broad launch
- **Support guide** (`SUPPORT.md`) — Where to get help, what goes in GitHub Issues vs Discussions vs SECURITY.md vs CODE_OF_CONDUCT.md; links to WSL2 guide, publishing guide, integration docs; no guaranteed commercial support during alpha
- **Governance document** (`GOVERNANCE.md`) — Project maintained by Smouj; technical decisions by maintainer; contributions via PR; acceptance criteria; security and conduct priority; versioning and release process
- **Maintainers document** (`MAINTAINERS.md`) — Smouj (@smouj) as maintainer with responsibilities; how to become a maintainer in the future
- **Issue templates** — `.github/ISSUE_TEMPLATE/bug_report.yml` (OS, Python, GPU, CUDA/ROCm, version, logs), `feature_request.yml`, `performance_report.yml` (model, quantization, profile, tokens/s, TTFT, VRAM/RAM), `integration_request.yml` (OpenClaw/Hermes/Continue/Open WebUI/other), `config.yml` (disables blank issues, links to security, conduct, discussions)
- **Improved PR template** (`.github/pull_request_template.md`) — Expanded checklist: tests, ruff, docs, changelog, no GGUF, no secrets, no false claims, no unsafe 0.0.0.0, default_profile check, release-check
- **`wheel-install-smoke` CI job** — Builds wheel, installs in clean venv, tests `kimari --version`, `config path`, `setup --json`, `start --dry-run`, `token create/show/delete`, verifies defaults JSON in wheel
- **`MANIFEST.in`** — Includes community files (CODE_OF_CONDUCT.md, CONTRIBUTING.md, SUPPORT.md, GOVERNANCE.md, MAINTAINERS.md, etc.) in sdist; excludes GGUF, .kimari/, logs, dist/build
- **RELEASE_CHECKLIST.md** — Added "Community & Contribution" and "Packaging & CI" sections with new checks
- **`scripts/release/check-release.py`** — Added 3 new validation categories (18 total): Community & contribution files, Packaging & CI, Content integrity re-check
- **New tests** (`tests/test_release_v0113.py`) — 40+ tests covering community files, issue templates, PR template, packaging, CI, README links, version consistency, no false claims

### Changed
- **Version bumped** to `0.1.13-alpha`
- **`pyproject.toml`** — `license = "MIT"` (SPDX format, replacing `{text = "MIT"}`); removed `License :: OSI Approved :: MIT License` classifier (superseded by SPDX expression)
- **`CONTRIBUTING.md`** — Rewritten with 9 non-negotiable rules table, GPU profile and integration proposal processes, CHANGELOG/ROADMAP update instructions, expanded PR checklist, links to Code of Conduct and GOVERNANCE.md
- **`README.md`** — Added "Community & Contribution" section linking to CODE_OF_CONDUCT.md, CONTRIBUTING.md, SUPPORT.md, SECURITY.md, GOVERNANCE.md, MAINTAINERS.md, Issue Templates
- **`docs/index.html`** — Added "Community" section with cards linking to Code of Conduct, Contributing, Support, Security, Governance, GitHub Issues; added Community nav link
- **`docs/PUBLISHING.md`** — Added "v0.1.13 TestPyPI Actual Validation" section with checklist, result table, and validation commands

## [0.1.12-alpha] — 2026-05-14

### Added
- **Packaged defaults** (`kimari/defaults/`) — Default profiles, schema, and models registry now ship inside the wheel as `package-data`; copied to user config dir on first use when no config exists
- **User path management** (`kimari/core/paths.py`) — Platform-aware paths for config (`~/.config/kimari/`), state (`~/.local/state/kimari/`), cache (`~/.cache/kimari/`), and models (`~/.local/share/kimari/models/`); Windows support (`%APPDATA%\Kimari\`, `%LOCALAPPDATA%\Kimari\`); `KIMARI_HOME`, `KIMARI_CONFIG_DIR`, `KIMARI_STATE_DIR`, `KIMARI_CACHE_DIR`, `KIMARI_MODELS_DIR` environment variable overrides
- **Config resolution chain** — `load_config()` now resolves: (1) user config dir → (2) repo-root `config/` → (3) packaged defaults; no longer requires "run from repo root"
- **`kimari config path` command** — Shows the active config file path (user, repo, or packaged default)
- **Short flag support in strict-flags** — `parse_supported_flags()` now extracts short flags (`-m`, `-c`, `-ngl`, `-b`, `-ub`, `-t`) from `llama-server --help` output; `SHORT_TO_LONG` alias mapping ensures `--strict-flags` no longer produces false positives for base command flags
- **`pyproject.toml` package-data** — Now includes `kimari/defaults/*.json` so the wheel contains default configs

### Changed
- **Version bumped** to `0.1.12-alpha`
- **Config loader** (`kimari/config/loader.py`) — Refactored to use `_resolve_config_path()` with 3-tier resolution; `_ensure_user_config()` copies defaults to user dir on first use
- **Model registry** (`kimari/models/registry.py`) — Uses `_resolve_models_registry_path()` with same 3-tier resolution; `_resolve_model_target()` checks user models dir and repo-root; `scan_models_dir_for_gguf()` scans both directories
- **State module** (`kimari/core/state.py`) — State files now live in user state dir; `KIMARI_STATE_DIR` override supported
- **Token module** (`kimari/security/tokens.py`) — Auth tokens now stored in user state dir (not `PROJECT_ROOT/.kimari/`); `KIMARI_STATE_DIR` override supported
- **Constants** (`kimari/core/constants.py`) — Path constants now resolve via `kimari.core.paths`; `PROJECT_ROOT` retained for backward compatibility and development
- **CLI** (`kimari/cli/main.py`) — Model path resolution uses `_resolve_model_path()` checking user models dir then repo-root; `load_config()` called unconditionally (no longer gated on `CONFIG_PATH.exists()`)
- **`pyproject.toml`** — `package-data` updated to include `defaults/*.json`

## [0.1.11-alpha] — 2026-05-13

### Added
- **`kimari setup` command** — Guided environment detection: OS, Python, GPU, CUDA, ROCm (experimental), llama-server, local GGUF models; recommends profile and next steps; supports `--dry-run`, `--json`, `--profile`, `--integration` (openclaw/hermes/continue)
- **Runtime flag detection** (`kimari/runtime/llama_flags.py`) — Detects llama-server supported flags via `--help` parsing; `detect_llama_server_help()`, `detect_llama_server_version()`, `parse_supported_flags()`, `supports_flag()`, `filter_unsupported_flags()`
- **`--strict-flags` option** on `kimari start` — When used with `--dry-run`, checks if llama-server supports all profile flags; fails on unsupported flags in strict mode, warns otherwise
- **Local auth tokens** (`kimari/security/tokens.py`) — `kimari token create/show/delete`; saves to `.kimari/auth.json`; uses `secrets.token_urlsafe(32)`; documented as "prepared for future Kimari API / reverse proxy use" (llama-server does not apply auth natively)
- **Windows launcher script** (`scripts/windows/kimari-launcher.ps1`) — Comprehensive PowerShell launcher: venv setup, pip install, doctor, model pull, server start
- **Windows doctor script** (`scripts/windows/kimari-doctor.ps1`) — PowerShell diagnostic: Python, CUDA, llama-server, models, port checks with troubleshooting advice
- **Windows scripts README** (`scripts/windows/README.md`) — Documentation for all Windows helper scripts
- **TestPyPI validation section** in `docs/PUBLISHING.md` — Step-by-step TestPyPI validation checklist for v0.1.11

### Changed
- **Version bumped** to `0.1.11-alpha`
- **RELEASE_CHECKLIST.md** — Added checks for setup, strict-flags, token, Windows scripts, flag detection
- **scripts/release/check-release.py** — Added 13th validation category for runtime/security modules; added README checks for setup/strict-flags/token; added index.html checks for setup/strict-flags/token

## [0.1.10-alpha] — 2026-05-12

### Added
- **Performance estimation module** (`kimari/performance/`) — Pure functions for VRAM estimation, RAM estimation, and settings recommendation with confidence levels and warnings
  - `estimate_vram_usage()` — Estimates VRAM using formula: model_gpu_part + kv_cache + compute_overhead + cuda_overhead with KV dtype factors (f16, q8_0, q4_0, q4_1, f32)
  - `estimate_ram_usage()` — Estimates RAM with mmap/no-mmap paths and OS margins
  - `recommend_context()` — Finds largest fitting context size from safe VRAM budget
  - `recommend_kv_cache()` — Recommends KV cache types based on VRAM headroom
  - `recommend_batch()` — Safe/balanced/fast batch profiles with VRAM scaling
  - `recommend_gpu_layers()` — Full or partial GPU offload recommendations
  - `recommend_profile_settings()` — Combines all recommendations into complete profile
- **GGUF metadata reader** (`kimari/performance/gguf_metadata.py`) — Lightweight reader for GGUFv2/v3 files, extracts n_layer, n_embd, n_head, context_length, architecture; graceful fallback to defaults
- **`kimari optimize` command** — Analyzes a profile and recommends optimal settings (ctx, batch, ubatch, cache types, gpu_layers, flash_attn, parallel, VRAM/RAM estimates, warnings); supports `--json` and `--mode` (safe/balanced/fast/ide/agent)
- **`kimari perf` command** — Performance diagnostic helper; `--dry-run` shows recommendations, `--matrix` shows all modes, `--json` for structured output
- **8 new GPU profiles** — `gtx1060-safe`, `gtx1060-fast`, `gtx1080-balanced`, `gtx1080-longctx`, `ide-local`, `agent-local`, `openclaw-local`, `hermes-local`
- **New profile fields** — `performance_mode` (safe/balanced/fast/longctx/ide/agent), `flash_attn` (auto/on/off), `parallel`, `mlock`, `no_mmap`
- **`build_server_cmd` extended** — Now adds `--flash-attn`, `--parallel`, `--mlock`, `--no-mmap` flags when profile defines them
- **Config version 3** — Migration adds new performance fields to existing profiles
- **OpenClaw integration** — `docs/integrations/OPENCLAW.md` with Chat Completions configuration and `config/integrations/openclaw.kimari.example.json`
- **Hermes Agent integration** — `docs/integrations/HERMES.md` with endpoint configuration and `config/integrations/hermes.kimari.example.yaml`
- **Continue.dev integration** — `docs/integrations/CONTINUE.md` with YAML config for chat/edit roles and `config/integrations/continue.kimari.example.yaml`
- **Generic OpenAI-compatible client guide** — `docs/integrations/OPENAI_COMPATIBLE_CLIENTS.md` with curl, Python, Node.js examples, Open WebUI notes, and troubleshooting

### Changed
- **Version bumped** to `0.1.10-alpha`
- **JSON Schema** updated to v3 — allows hyphens in profile names, adds `performance_mode`, `flash_attn`, `parallel`, `mlock`, `no_mmap` properties
- **GTX 1060 safe VRAM budget** — Now uses 82% (4.9 GB) instead of 87% (5.2 GB) for more conservative estimation
- **GTX 1080 safe VRAM budget** — Now uses 86% (6.8 GB) instead of 87% (7.0 GB)

### Fixed
- **Config validation** — Schema now accepts new performance fields and profile names with hyphens

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
