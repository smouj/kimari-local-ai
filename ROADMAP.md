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

## v0.1.12-alpha (Released)

- ✅ Packaged defaults (`kimari/defaults/`) ship inside wheel
- ✅ User path management (`kimari/core/paths.py`) with platform-aware dirs
- ✅ Config resolution chain: user → repo-root → packaged defaults
- ✅ Short flag support in strict-flags (`-m`, `-c`, `-ngl`, `-b`, `-ub`, `-t`)
- ✅ State/tokens in user directories (not PROJECT_ROOT)
- ✅ `KIMARI_HOME` and per-path environment variable overrides
- ✅ `pyproject.toml` package-data includes `defaults/*.json`
- ✅ `kimari config path` shows active config location
- ✅ No "run from repo root" requirement after install

## v0.1.13-alpha (Released)

- ✅ Code of Conduct (CODE_OF_CONDUCT.md) — Contributor Covenant 3.0
- ✅ Support guide (SUPPORT.md) — help channels and scope
- ✅ Contributing guide improved — 9 non-negotiable rules, proposal processes
- ✅ Governance document (GOVERNANCE.md) — project decisions and structure
- ✅ Maintainers document (MAINTAINERS.md) — maintainer responsibilities
- ✅ Issue templates — bug report, feature request, performance report, integration request, config.yml
- ✅ Improved PR template — expanded checklist with community standards
- ✅ Packaging polish — SPDX license format, no more setuptools warnings
- ✅ MANIFEST.in — community files included in sdist
- ✅ `wheel-install-smoke` CI job — builds and tests wheel in clean venv
- ✅ TestPyPI readiness documentation updated
- ✅ README community section added
- ✅ GitHub Pages community section added
- ✅ check-release.py expanded to 18 validation categories
- ✅ RELEASE_CHECKLIST.md expanded with community and packaging checks

## v0.1.14-alpha (Released)

- ✅ `kimari setup --write` — persist detected configuration with backup
- ✅ Setup persistence module (`kimari/setup/writer.py`)
- ✅ `kimari models hash <path>` — compute SHA256 of local GGUF file
- ✅ `kimari models verify <model-id>` — verify against registry (not_pinned/match/mismatch)
- ✅ `kimari models pin-hash <model-id>` — pin hash to user registry (dry-run default)
- ✅ `get_effective_models_registry()` — user registry overrides packaged defaults
- ✅ No invented SHA256 hashes in packaged defaults (all null until explicitly pinned)
- ✅ Reverse proxy auth guide (`docs/REVERSE_PROXY_AUTH.md`) — nginx/Caddy examples
- ✅ API plan (`docs/API_PLAN.md`) — FastAPI REST API design for v0.2.0-alpha
- ✅ TestPyPI validation section in PUBLISHING.md
- ✅ Windows README updated with wheel/TestPyPI install, setup --write, models hash
- ✅ check-release.py expanded to 21 validation categories
- ✅ RELEASE_CHECKLIST.md expanded with setup write-mode and SHA256 tooling checks

## v0.1.15-alpha (Released)

- ✅ **P0 fix:** `start_server()` uses `resolve_model_path()` instead of `PROJECT_ROOT / effective_model`
- ✅ Robust `resolve_model_path()` — absolute, CWD-relative, user models dir, repo-root, fallback
- ✅ Setup write-mode UX — `--yes` flag, confirmation prompt, preview summary
- ✅ Setup writer improvements — `preview_setup_changes()`, `apply_setup_changes()`, atomic write
- ✅ SHA256 pin-hash workflow — `--yes`, `--dry-run`, confirmation prompt
- ✅ Benchmark result sharing format (`benchmarks/RESULT_FORMAT.md`, example JSON)
- ✅ Windows wheel packaging scripts (`build-wheel.ps1`, `install-from-wheel.ps1`, `install-from-testpypi.ps1`)
- ✅ Reverse proxy auth refinement — diagrams, Caddy/nginx map examples
- ✅ OpenAPI 3.1 draft (`docs/API_OPENAPI_DRAFT.yaml`)
- ✅ TestPyPI validation documented
- ✅ check-release.py and RELEASE_CHECKLIST expanded

## v0.1.16-alpha (Released)

- ✅ Experimental FastAPI API skeleton (`kimari/api/`) — `app.py`, `schemas.py`, `server.py`
- ✅ Optional `api` dependency in `pyproject.toml` (`pip install kimari-local-ai[api]`)
- ✅ `kimari api --experimental` command with `--dry-run` support
- ✅ API endpoints: health, status, config, profiles, models, optimize, perf/dry-run
- ✅ Server start/stop return 501 (planned, not implemented yet)
- ✅ Experimental auth middleware (not enforced by default)
- ✅ `docs/API_EXPERIMENTAL.md` — experimental API status and usage
- ✅ `docs/PYPI_RELEASE_GATE.md` — PyPI publishing gate process
- ✅ `docs/MODEL_HASHING.md` — model hash verification guide
- ✅ `docs/BENCHMARK_SUBMISSIONS.md` — benchmark submission workflow
- ✅ Benchmark examples for GTX 1060/1080
- ✅ Windows packaging improvements
- ✅ Release-check script expanded to 28 validation categories
- ✅ New tests for v0.1.16 features

## v0.1.17-alpha (Released)

- ✅ MODEL_CARD.md professional rewrite — "Planned / Training Design" status, base candidates, evaluation targets
- ✅ docs/MODEL_TRAINING_PLAN.md — 7-phase training pipeline (selection → SFT → DPO/ORPO → eval → GGUF → HF → registry)
- ✅ docs/MODEL_BASE_SELECTION.md — SmolLM3-3B, Qwen2.5-3B-Instruct, Llama 3.2 3B comparison
- ✅ MODEL_LICENSES.md improved — SmolLM3, Qwen, Llama candidate license details
- ✅ dataset/README.md rewritten — SFT/Preference JSONL schemas, forbidden data policy
- ✅ dataset/schema/ — sft.schema.json and preference.schema.json
- ✅ training/ — README, configs (SFT LoRA, ORPO), scripts (prepare_dataset.py, train_sft_lora.py)
- ✅ eval/ — README and 35 KimariFit prompts across 10 categories
- ✅ docs/HUGGINGFACE_RELEASE.md — Pre-upload checklist and HF model card template
- ✅ Release-check expanded to 35 validation categories
- ✅ New tests for v0.1.17 features

## v0.1.18-alpha (Released)

- ✅ docs/MODEL_DECISION_RECORD.md — ADR-001 for base model selection with weighted scoring
- ✅ training/configs/base_candidates.yaml — 3 candidates with metadata, risk levels, scoring criteria
- ✅ training/scripts/select_base_model.py — CLI scoring and ranking tool
- ✅ dataset/samples/sft_seed.jsonl — 30 synthetic SFT samples across 10 categories
- ✅ dataset/samples/preference_seed.jsonl — 20 synthetic preference pairs
- ✅ training/scripts/prepare_dataset.py enhanced — --dedupe, --min-chars, --max-chars, --require-tags, --report
- ✅ training/scripts/build_dataset_mix.py — Dataset mix builder with schema validation
- ✅ eval/kimarifit.py — Dry-run and live evaluation harness
- ✅ eval/rubrics/kimarifit_rubric.md — 9-criteria scoring rubric
- ✅ eval/results/.gitkeep — Results directory placeholder
- ✅ training/scripts/train_sft_lora.py improved — Enhanced --dry-run with training plan
- ✅ training/scripts/export_gguf_plan.py — GGUF export planning tool
- ✅ docs/FIRST_TRAINING_RUN.md — Step-by-step guide for first training run
- ✅ Release-check expanded to 38 validation categories
- ✅ New tests for v0.1.18 features

## v0.1.19-alpha (Released)

- ✅ SmolLM3-3B accepted for first private SFT candidate
- ✅ Base model acceptance document (docs/BASE_MODEL_ACCEPTANCE.md)
- ✅ Dataset v0 (SFT + preference + eval holdout)
- ✅ Training readiness validation script (validate_training_ready.py)
- ✅ KimariFit scoring plan with dimensions
- ✅ v0 training configs (SFT LoRA + ORPO)
- ✅ First private training run guide
- ✅ HF placeholder plan
- ✅ Release-check improvements

## v0.1.20-alpha (Released)

- ✅ MODEL_CARD checklist and version history fixes
- ✅ Baseline eval plan for SmolLM3-3B without fine-tuning
- ✅ Adapter artifact policy (what can/cannot be committed)
- ✅ Private SFT run manifest (private_sft_run.v0.yaml)
- ✅ Private SFT dry-run validation script
- ✅ Full v0 pipeline dry-run orchestration
- ✅ Private training runbook
- ✅ Adapter preview gate (BLOCKED by default)
- ✅ Compare runs tool (baseline vs adapter)
- ✅ .gitignore updated for training artifacts

## v0.1.21-alpha (Released)

- ✅ Adapter manifest template (training/templates/adapter_manifest.template.yaml)
- ✅ Adapter manifest creation script (training/scripts/create_adapter_manifest.py)
- ✅ Private SFT execution checklist
- ✅ SFT→ORPO decision framework
- ✅ Private eval results policy
- ✅ Eval summary template (eval/templates/eval_summary.template.json)
- ✅ Eval summary creation script (eval/scripts/create_eval_summary.py)
- ✅ Compare runs improvements (verdict, summary-output)
- ✅ Release-check improvements

## v0.1.22-alpha (Released)

- ✅ Remote GPU execution guide (RunPod / local GPU)
- ✅ Training requirements (separated dependencies)
- ✅ Preflight script (check SFT readiness)
- ✅ Postrun script (orchestrate post-training steps)
- ✅ Private execution config template
- ✅ Private run artifacts policy (what stays local vs committed)
- ✅ Private run failures troubleshooting
- ✅ Training command preview script
- ✅ Baseline eval plan script
- ✅ Adapter eval plan script
- ✅ train_sft_lora.py improvements (--print-command, --estimate-only, --require-dataset)
- ✅ Release-check improvements

## v0.1.23-alpha (Current)

- ✅ Postrun --json fix (passes --json to create_eval_summary subprocess)
- ✅ Preflight dataset_build_dir from run_config with fallback
- ✅ Screenshots documentation (docs/SCREENSHOTS.md)
- ✅ Screenshot assets policy (naming conventions, formats, no secrets)
- ✅ Screenshot placeholders (planned captures checklist)
- ✅ README and GitHub Pages screenshots section
- ✅ Release-check improvements

## v0.1.24-alpha (Planned)

- Execute first private SFT manually outside CI
- Record local adapter manifest
- Run baseline and adapter eval
- Produce sanitized eval summary
- Optionally add real screenshots from safe terminal captures
- Decide ORPO/DPO next step

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
