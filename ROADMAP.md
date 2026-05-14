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

## v0.1.23-alpha (Released)

- ✅ Postrun --json fix (passes --json to create_eval_summary subprocess)
- ✅ Preflight dataset_build_dir from run_config with fallback
- ✅ Screenshots documentation (docs/SCREENSHOTS.md)
- ✅ Screenshot assets policy (naming conventions, formats, no secrets)
- ✅ Screenshot placeholders (planned captures checklist)
- ✅ README and GitHub Pages screenshots section
- ✅ Release-check improvements

## v0.1.24-alpha (Released)

- ✅ Private SFT run record documentation (docs/FIRST_PRIVATE_SFT_RECORD.md)
- ✅ Private run record template (training/templates/private_sft_run_record.template.json)
- ✅ create_private_run_record script with --dry-run --json
- ✅ Safe screenshot capture guide (docs/SAFE_SCREENSHOT_CAPTURE.md)
- ✅ CLI screenshot text generator (scripts/docs/generate_cli_screenshot_text.py)
- ✅ Screenshot text examples (docs/assets/screenshots/examples/)
- ✅ Release-check improvements
- ✅ Tests for v0.1.24 artifacts

## v0.1.25-alpha (Released)

- ✅ HF token safety guide (docs/HF_TOKEN_SAFETY.md)
- ✅ Secret scanner script (scripts/security/scan_for_secrets.py)
- ✅ Private run record hardening (more path rejection, suspicious string detection, security_scan_status)
- ✅ Screenshot command cleanup (SAFE_SCREENSHOT_CAPTURE.md uses real commands)
- ✅ Private SFT handoff guide (docs/FIRST_PRIVATE_SFT_HANDOFF.md)
- ✅ Private SFT run commands guide (docs/PRIVATE_SFT_RUN_COMMANDS.md)
- ✅ Performance tuning plan (docs/PERFORMANCE_TUNING_PLAN.md)
- ✅ Benchmark plan module (kimari/performance/benchmark_plan.py)
- ✅ `kimari benchmark --dry-run` command (estimates only, no execution)
- ✅ `kimari tune --dry-run` command (recommendations only, --apply blocked)
- ✅ Showcase plan (docs/SHOWCASE_PLAN.md)
- ✅ README and GitHub Pages updated with benchmark/tune/showcase sections
- ✅ Release-check improvements
- ✅ Tests for v0.1.25 artifacts

## v0.1.26-alpha (Released)

- ✅ Measured benchmark prototype (`kimari benchmark --measure`)
- ✅ `kimari doctor --deep` extended diagnostics
- ✅ Secret scanner hardening (line-by-line, safe placeholders)
- ✅ Benchmark prompts (8 safe prompts in JSONL)
- ✅ Benchmark result writer (sanitized, gitignored output)
- ✅ Gateway dry-run module and commands (`kimari gateway --dry-run`, `--status`, `--plan`, `--json`)
- ✅ Update check module and commands (`kimari update check`, `--online`, `--json`)
- ✅ Enhanced status with gateway/preview gate fields
- ✅ Enhanced doctor --deep with 5 new checks (Kimari Version, CUDA/NVIDIA, Packaged Defaults, Gateway Module, Integration Docs)
- ✅ docs/GATEWAY_PLAN.md
- ✅ docs/UPDATE.md
- ✅ docs/INSTALL_MATRIX.md
- ✅ docs/OPENWEBUI_OPENCLAW_QUICK_CONFIG.md

## v0.1.27-alpha (Released)

- ✅ Console render module (kimari/console/render.py)
- ✅ Improved `kimari status` human output
- ✅ Improved `kimari doctor --deep` human output  
- ✅ Integration config generator (kimari/integrations/config_generator.py)
- ✅ `kimari integrations generate` command
- ✅ Gateway wording corrected (gateway helps configure llama-server, not serve endpoints)
- ✅ docs/INTEGRATION_CONFIG_GENERATOR.md
- ✅ docs/GATEWAY_PROTOTYPE_PLAN.md
- ✅ docs/CONSOLE_UX.md
- ✅ Safe CLI screenshots plan script
- ✅ Updated docs/SCREENSHOTS.md

## v0.1.28-alpha (Released)

- ✅ Kimari-4B first private SFT run guide (docs/KIMARI4B_PRIVATE_SFT_RUN.md)
- ✅ Private SFT run config (training/configs/kimari4b_private_sft_run.v0.yaml)
- ✅ Private SFT command generator (training/scripts/kimari4b_private_sft_command.py)
- ✅ First run checklist (docs/KIMARI4B_FIRST_RUN_CHECKLIST.md)
- ✅ Eval plan script (eval/scripts/kimari4b_eval_plan.py)
- ✅ Eval criteria (docs/KIMARI4B_EVAL_CRITERIA.md)
- ✅ Summary template (training/templates/kimari4b_private_summary.template.json)
- ✅ Updated FIRST_PRIVATE_SFT_HANDOFF.md with Kimari-4B specific section
- ✅ Updated ADAPTER_PREVIEW_GATE.md with Kimari-4B BLOCKED status

## v0.1.29-alpha (Released)

- ✅ HF Jobs private smoke wrapper and config
- ✅ Command compatibility fix (unsupported flags removed)
- ✅ train_sft_lora --show-supported-flags
- ✅ validate_private_sft_commands script
- ✅ hf_jobs_private_run and hf_jobs_status scripts
- ✅ HF Jobs smoke summary template
- ✅ HF_JOBS_PRIVATE_RUN and HF_JOBS_RESULT_HANDOFF docs
- ✅ Artifact field naming fix (expected_local_artifacts, forbidden_commit_artifacts)

## v0.1.30-alpha (Released)

- ✅ HF Jobs smoke test result template and sanitized summary (docs/HF_JOBS_SMOKE_RESULT.md)
- ✅ Smoke test summary generator CLI (training/scripts/create_hf_jobs_smoke_summary.py)
- ✅ HF Jobs smoke test runbook (docs/HF_JOBS_SMOKE_RUNBOOK.md)
- ✅ --sanitize-logs flag in hf_jobs_status.py
- ✅ Version bumped to v0.1.30-alpha

## v0.1.31-alpha (Released)

- ✅ HF Jobs smoke execution record doc and template
- ✅ Smoke summary validator CLI (validate_hf_jobs_smoke_summary.py)
- ✅ Hardened hf_jobs_status.py (stderr sanitization, --tail via HF CLI)
- ✅ Smoke must pass before micro SFT gate
- ✅ Version bumped to v0.1.31-alpha

## v0.1.32-alpha (Released)

- ✅ HF Jobs micro SFT run guide (docs/HF_JOBS_MICRO_SFT_RUN.md)
- ✅ Micro SFT config (training/configs/hf_jobs_kimari4b_micro_sft.v0.yaml)
- ✅ Micro SFT wrapper CLI (training/scripts/hf_jobs_micro_sft.py)
- ✅ Micro SFT summary template and generator
- ✅ Micro SFT summary validator
- ✅ Micro SFT result doc (docs/HF_JOBS_MICRO_SFT_RESULT.md)
- ✅ Updated runbook, private SFT guide, and checklist
- ✅ Version bumped to v0.1.32-alpha

## v0.1.33-alpha (Released)

- ✅ train_sft_lora.py supports real micro SFT training with LoRA/QLoRA
- ✅ New CLI flags: --dataset-path, --eval-dataset-path, --output-dir, --max-steps, --eval-steps, --save-steps, --logging-steps, --per-device-train-batch-size, --gradient-accumulation-steps, --learning-rate, --max-seq-length, --micro-run, --yes
- ✅ apply_cli_overrides() merges CLI args with YAML config
- ✅ run_sft_training() implements real LoRA SFT training loop
- ✅ CI guard blocks training when CI=true
- ✅ Training requires --micro-run --yes (double confirmation)
- ✅ No --token argument. No push_to_hub. report_to="none".
- ✅ validate_micro_sft_readiness.py for pre-flight config validation
- ✅ docs/MICRO_SFT_IMPLEMENTATION.md
- ✅ hf_jobs config includes --micro-run --yes
- ✅ Gate BLOCKED

## v0.1.34-alpha (Released)

- ✅ Training stack compatibility checker (check_training_stack.py)
- ✅ TRL/SFTTrainer compatibility hardening (build_training_arguments, build_sft_trainer, prepare_sft_dataset)
- ✅ Removed max_seq_length from TrainingArguments (passed to SFTTrainer instead)
- ✅ Dataset formatting: messages → text conversion, text column direct support
- ✅ docs/TRAINING_STACK_COMPATIBILITY.md
- ✅ HF Jobs config includes check_training_stack before training
- ✅ Gate BLOCKED

## v0.1.35-alpha (Released)

- ✅ Micro SFT execution record (create/validate scripts, docs)
- ✅ hf_jobs_micro_sft.py smoke-gated submit (--require-smoke-summary)
- ✅ HF Jobs micro SFT runbook
- ✅ Gate BLOCKED

## v0.1.36-alpha (Released)

- ✅ resolve_smoke_gate() — unified smoke gate resolution (explicit path, /tmp fallback, override)
- ✅ Critical bug fix: explicit --require-smoke-summary PATH no longer blocked by missing /tmp file
- ✅ Submit uses single smoke gate check (no duplicate)
- ✅ docs/HF_JOBS_SMOKE_GATE.md
- ✅ Gate BLOCKED

## v0.1.37-alpha (Released)

- ✅ Fixed validate_config() UnboundLocalError when jsonschema not installed
- ✅ Added check_gpu_compute_capability() to kimari doctor --deep
- ✅ Added check_gpu_arch_compatibility() to check_training_stack.py (check #15)
- ✅ Pascal GPU (GTX 1060/1070/1080) + PyTorch cu126 compatibility docs
- ✅ Updated INSTALL_WSL2.md, INSTALL_MATRIX.md, TRAINING_STACK_COMPATIBILITY.md
- ✅ Gate BLOCKED

## v0.1.38-alpha (Released)

- ✅ Fixed setup writer never starts from empty dict (was producing incomplete configs)
- ✅ Fixed recommended profile resolves to safe fallback if original doesn't exist
- ✅ Added `is_config_complete()`, `load_base_config_for_setup()`, `resolve_recommended_profile()` helpers
- ✅ Added `kimari setup --write --yes --reset-user-config` flag for safe config regeneration
- ✅ Added `kimari setup --json` fields: resolved_profile, user_config_complete, recovery_needed, config_would_be_valid
- ✅ Improved `kimari doctor --deep` detects incomplete user config and suggests recovery command
- ✅ Gate BLOCKED

## v0.1.53-alpha (Released)

- ✅ KimariEval Private v1 baseline vs adapter infrastructure
- ✅ HF public presence synced to repo state
- ✅ Organization Card, Space README, Collection docs aligned
- ✅ Private adapter persisted; no public weights, no GGUF
- Gate BLOCKED — no benchmark claims

## v0.1.56-alpha (Released)

- ✅ Hugging Face public polish and consistency hardening
- ✅ Public version consistency script
- ✅ Org card and Space README synced from package version
- ✅ Kimari Fit Lab improved as static compatibility helper
- ✅ Collection docs clarify reference/community GGUF only
- ✅ Kimari-4B placeholder card prepared but not published
- ✅ Kimari-4B remains private pipeline / not released
- Gate BLOCKED — no public weights, no public adapters, no GGUF, no benchmark claims

## v0.1.57-alpha (Released)

- ✅ Open-license model policy (Apache 2.0 bases only)
- ✅ Base model license matrix (approved + blocked)
- ✅ Open base bakeoff plan (Qwen2.5-1.5B, SmolLM2-1.7B, SmolLM3-3B, Qwen3-4B)
- ✅ SFT v1 dataset license plan (1,400–1,700 examples, all permissive)
- ✅ SFT v1 training plan (Runtime 1.5B, Core 3B, 4B candidate)
- ✅ Release gate updated (license review required)
- ✅ GitHub Pages reconciliation (no stale versions)
- ✅ Environment status, run history, HF profile docs
- ✅ Public pages and state consistency checkers
- Gate BLOCKED — no training, no HF Jobs, no public weights

## v0.1.54-alpha (Released)

- ✅ Baseline vs adapter eval subset10 on HF Jobs
- ✅ Eval result summary + validation
- ✅ No raw outputs, no benchmark claims
- Gate BLOCKED

## v0.1.78-alpha (Current)

Status: benchmark-honesty eval hardening; gate remains BLOCKED.

- ✅ Added 6 new benchmark-honesty eval cases (refuse-016 through refuse-021).
- ✅ Cases target the exact failure pattern from refuse-010 (affirming unverified benchmarks).
- ✅ Dataset now has 110 items across 7 categories, with 10 benchmark-honesty cases.
- 🚫 No new training run yet; these cases prepare for v0.1.79+ training data fix.
- 🚫 Gate BLOCKED; no subset60/full104, GGUF, public weights, or benchmark claim.

Next: v0.1.79-alpha should retrain with expanded dataset and re-evaluate on the safety slice.

## v0.1.77-alpha

Status: completed private subset30 manual review; gate remains BLOCKED.

- ✅ Reviewed 30/30 private subset30 items using the validated private artifact.
- ✅ Accepted adapter wins: 14; rejected adapter wins: 6; accepted baseline wins: 9.
- ⚠️ Decision: `safety_fix_required` due benchmark-honesty failure in a reviewed safety case.
- 🚫 No subset60/full104, GGUF, public weights, or benchmark claim until the safety fix is addressed and re-reviewed.

Next: v0.1.78-alpha should harden benchmark-honesty refusal behavior and rerun the targeted safety slice before broader evaluation.

## v0.1.76-alpha

- ✅ Version bump for private eval artifact persistence hardening
- ✅ Added upload/validation tools for private raw artifacts
- ✅ Added subset30 config with `raw_outputs_private_required: true`
- ✅ Reran subset30 scoring job `6a0590cce48bea4538b9c7b9` after hardening
- ✅ Private artifact uploaded and validated; manual review available next
- No public weights, no GGUF, no public benchmarks
- Gate BLOCKED

## v0.1.75-alpha (Released)

- ✅ Private raw-output retrieval + manual review execution attempt
- ✅ Private review directory created outside public repo (`~/kimari-private-review/v0175/`)
- ✅ HF bucket inspected for scoring job `6a052f5ce48bea4538b9c37d`
- ✅ Sanitized manual review generator added (`create_manual_review_from_private_raw.py`)
- ✅ Summary records `manual_review_status=blocked_missing_raw_outputs`
- ⚠️ Expected `raw_outputs_private.json` was not retrievable from the recorded bucket path
- No public weights, no GGUF, no public benchmarks
- Gate BLOCKED

## v0.1.74-alpha (Released)

- ✅ Private manual-review gate prepared
- ✅ Sanitized manual review summary + template
- ✅ Manual review validator
- ✅ Manual review doc
- ✅ Run history updated for 500-step SFT + subset30 scoring
- ⚠️ Raw outputs not found locally; manual review remained pending outside public repo
- No public weights, no GGUF, no public benchmarks
- Gate BLOCKED

## v0.1.73-alpha (Released)

- 🔧 SFT v1 eval subset10 execution (in progress)
- Eval load check + generation check
- Baseline vs adapter comparison on subset10
- Summary sanitized results
- Ready_for_subset30 determination
- No public weights, no GGUF, no public benchmarks
- Gate BLOCKED

## v0.1.65-alpha (Released)

- ✅ Eval subset10 infrastructure: load checker, eval runner, summary template/validator
- ✅ Adapter load checker: `eval/scripts/check_sft_v1_adapter_load.py`
- ✅ Eval runner: `eval/scripts/run_sft_v1_eval.py` (dry-run default, --allow-submit --yes required)
- ✅ Summary template + validator for sanitized eval results
- ✅ Eval result doc + report directory
- ✅ check-release.py v0.1.65 checks
- ✅ tests/test_release_v0165.py
- No training executed, no HF Jobs submitted
- No public weights, no GGUF, no public benchmarks
- Gate BLOCKED

## v0.1.64-alpha (Released)

- ✅ SFT v1 result reconciliation: run history updated
- ✅ check-release.py v0.1.62 checks now conditional (PENDING vs COMPLETED)
- ✅ Eval readiness config: `eval/configs/kimari_runtime_15b_sft_v1_eval_subset10.yaml`
- ✅ Eval readiness validator: `eval/scripts/validate_sft_v1_eval_readiness.py`
- ✅ Eval plan document: `docs/KIMARI_RUNTIME_15B_SFT_V1_EVAL_PLAN.md`
- ✅ check-release.py v0.1.64 checks
- ✅ tests/test_release_v0164.py
- No training executed, no HF Jobs submitted
- No public weights, no GGUF, no public benchmarks
- Gate BLOCKED

## v0.1.63-alpha (Released)

- ✅ SFT v1 real short run completed (Job `6a0501dae48bea4538b9c17a`, a10g-small)
- ✅ Training results: 10 steps micro-run, loss 2.753→2.652 (eval), accuracy 52.08%
- ✅ Result summary validated (`docs/assets/results/sft_v1_run_summary.json`)
- ✅ Dataset build files tracked in git
- ✅ HF Jobs command syntax fixed (positional IMAGE, bash -c, git clone, --micro-run --yes)
- ✅ Config keys fixed (dataset_path/eval_dataset_path)
- ✅ Preflight supports dataset_path/eval_dataset_path
- ✅ check-release.py v0.1.63 checks
- No public weights, no GGUF, no public benchmarks
- Gate BLOCKED

## v0.1.62-alpha (Released)

- ✅ Result doc placeholder corrected (training_performed=false, not true)
- ✅ HF Jobs wrapper: preflight runs BEFORE training (was incorrectly after)
- ✅ HF Jobs wrapper: execution_order, preflight_before_training, training_after_preflight in dry-run JSON
- ✅ HF Jobs wrapper: validate_execution_order() blocks submit if preflight is after training
- ✅ check-release.py v0.1.62 checks
- No training executed, no HF Jobs submitted
- Gate BLOCKED

## v0.1.61-alpha (Released)

- ✅ SFT v1 real short run execution (100 steps, QLoRA, Qwen2.5-1.5B-Instruct)
- ✅ Run summary creator (`training/scripts/create_sft_v1_run_summary.py`)
- ✅ Run summary validator (`training/scripts/validate_sft_v1_run_summary.py`)
- ✅ SFT v1 result doc (`docs/KIMARI_RUNTIME_15B_SFT_V1_RESULT.md`)
- ✅ Completed summary template (`training/templates/sft_v1_completed_summary.template.json`)
- ✅ HF Jobs wrapper: real submission allowed with safeguards
- Adapter: private only, not committed to public repo
- No GGUF generation, no public weights, no public benchmarks
- Gate BLOCKED

## v0.1.60-alpha (Released)

- ✅ SFT v1 training config (`training/configs/kimari_runtime_15b_sft_v1.yaml`)
- ✅ Preflight script (`training/scripts/preflight_sft_v1.py`)
- ✅ Command preview (`training/scripts/sft_v1_command_preview.py`)
- ✅ HF Jobs dry-run wrapper (`training/scripts/hf_jobs_sft_v1.py`)
- ✅ Run summary template (`training/templates/sft_v1_run_summary.template.json`)
- ✅ Runtime 1.5B SFT v1 plan (`docs/KIMARI_RUNTIME_15B_SFT_V1_PLAN.md`)
- ✅ Artifact policy (`docs/KIMARI_RUNTIME_15B_SFT_V1_ARTIFACT_POLICY.md`)
- ✅ check-release.py v0.1.60 checks
- No training executed — dry-run configuration only
- No HF Jobs submitted
- No adapters or GGUF generated
- Gate BLOCKED

## v0.1.59-alpha (Released)

- ✅ Kimari SFT v1 dataset structure (8 categories, 320+ examples)
- ✅ Dataset schema (`dataset/schema/kimari_sft_item.schema.json`)
- ✅ Dataset validator (`dataset/scripts/validate_kimari_sft_v1.py`)
- ✅ Dataset builder (`dataset/scripts/build_kimari_sft_v1.py`)
- ✅ License manifest (`license_manifest.yaml` + `license_manifest.json`)
- ✅ Quality guide (`docs/KIMARI_SFT_V1_QUALITY_GUIDE.md`)
- ✅ Dataset documentation (`docs/KIMARI_SFT_V1_DATASET.md`)
- ✅ SFT v1 dataset license plan updated with real dataset reference
- ✅ SFT v1 training deferred to v0.1.60-alpha
- Gate BLOCKED — no training, no HF Jobs, no public weights, no adapters, no GGUF

## v0.1.58-alpha (Released)

- ✅ Open-license base bakeoff config (`eval/configs/open_base_bakeoff_v1.yaml`)
- ✅ Bakeoff runner (`eval/scripts/run_open_base_bakeoff.py`)
- ✅ Bakeoff summary template (`eval/templates/open_base_bakeoff_summary.template.json`)
- ✅ Bakeoff summary validator (`eval/scripts/validate_open_base_bakeoff_summary.py`)
- ✅ Bakeoff result doc (`docs/KIMARI_OPEN_BASE_BAKEOFF_RESULT.md`)
- ✅ Base selection decision doc (`docs/KIMARI_BASE_SELECTION_DECISION.md`)
- ✅ README bakeoff status section
- ✅ docs/index.html bakeoff status card
- Gate BLOCKED — no training, no HF Jobs, no public weights, no public benchmark claims

## v0.1.52-alpha

- ✅ KimariEval Private v1: 104 cases across 7 categories
- ✅ Eval validator + harness (dry-run + endpoint)
- ✅ Baseline vs adapter eval plan
- ✅ KimariFit score plan (experimental)
- ✅ No training, no HF Jobs, no adapter, no GGUF
- Gate BLOCKED — no benchmark claims

## v0.1.51-alpha

- ✅ Second micro SFT completed (Job 6a03a25e72518a06598ffae0)
- ✅ adapter_persisted_private: true (uploaded to Smouj013/kimari4b-micro-sft-adapter-v0)
- ✅ adapter_load_check: true (adapter loads and generates text)
- ✅ Private HF repo created and adapter uploaded
- ✅ UV-compatible training script (PEP 723)
- ✅ PyTorch 2.11.0+cu130, transformers 5.8.0, peft 0.19.1, trl 1.4.0
- ✅ Loss: 5.005 → 4.228 (20 steps, inline dataset)
- Gate BLOCKED — no public release, no benchmark claims

## v0.1.50-alpha

- ✅ Micro SFT completed (Job 6a038ec87618f125ee2b7984)
- ✅ Dataset hash inconsistency fixed
- ✅ hash_dataset.py script for computing file/normalized SHA256
- ✅ Adapter persistence strategy doc
- ✅ Private artifact repo policy
- ✅ Package adapter script (dry-run default)
- ✅ Next run plan with adapter retrieval
- ✅ Private repo smouj/kimari-4b-artifacts created
- ✅ Post-run review doc
- Gate BLOCKED — no public weights, no adapter eval yet

## v0.1.49-alpha

- ✅ Micro SFT dataset (72 examples, Spanish technical + CUDA + Python + Kimari API)
- ✅ HF Jobs micro SFT config (a10g-small, 20min timeout, LoRA r=8, Qwen2.5-1.5B)
- ✅ HF Jobs micro SFT wrapper (dry-run default, --allow-submit --yes)
- ✅ **Job 6a038ec87618f125ee2b7984 COMPLETED** — training_performed=true, adapter_generated=true
- ✅ Summary template + validator (0 errors)
- ✅ PyTorch 2.5.1 + transformers>=4.46 = working combo
- ✅ 4 failed attempts (PyTorch/transformers version incompatibilities)
- ✅ Estimated cost: ~$0.35
- ✅ Gate BLOCKED — no adapter committed, no upload, no GGUF

## v0.1.48-alpha

- ✅ HF Jobs smoke test COMPLETED
- ✅ GPU detected: NVIDIA A10G, 22.3 GB VRAM, CUDA 12.1
- ✅ PyTorch 2.1.0 with CUDA works on a10g-small
- ✅ No training, no adapter, no upload
- ✅ Access gate script
- ✅ Smoke runner (--allow-submit --yes required)
- ✅ Summary creator + validator
- ✅ Gate BLOCKED

## v0.1.47-alpha

- ✅ Kimari-4B private adapter pipeline
- ✅ Training config (safety flags: no upload, no public, no GGUF)
- ✅ Runner (dry-run default, --allow-train --yes required)
- ✅ Preflight checks
- ✅ Adapter manifest template + creator
- ✅ Eval plan + script
- ✅ Release gate doc (no auto-transitions)
- ✅ .gitignore hardened
- ✅ Gate BLOCKED — Kimari-4B not released

## v0.1.46-alpha

- ✅ Collection seed plan + validator + example JSON
- ✅ Public launch pack (X/Reddit/HF/GitHub)
- ✅ X posts (short/technical/thread, EN/ES)
- ✅ Reddit posts (technical/humble)
- ✅ HF community post
- ✅ README "Public showcase" section
- ✅ Screenshots: manifest template only (no real captures yet)
- ✅ Gate BLOCKED

## v0.1.45-alpha

- ✅ `docs/HUGGINGFACE_DEPLOYMENT_STATUS.md` — HF deployment documented with URLs
- ✅ `docs/HUGGINGFACE_COLLECTIONS.md` — collection guide for reference GGUF models
- ✅ `docs/SOCIAL_PROOF_SNIPPETS.md` — short texts for GitHub/X/Reddit/HF
- ✅ README Hugging Face presence section
- ✅ docs/index.html "Hugging Face Space live" card
- ✅ Space deployed: kimari-ai/kimari-fit-lab (RUNNING)
- ✅ Org Card updated: kimari-ai/README
- ✅ Collection created: Smouj013/kimari-compatible-gguf-models
- ✅ Gate BLOCKED

## v0.1.44-alpha

- ✅ `docs/GTX1060_SHOWCASE.md` — local showcase documentation
- ✅ `docs/assets/screenshots/gtx1060-wsl2/` — screenshot directory with manifest
- ✅ `scripts/docs/validate_screenshot_manifest.py` — screenshot manifest validator
- ✅ `huggingface/kimari-fit-lab/` — HF Space pack (Gradio compatibility checker)
- ✅ `docs/HUGGINGFACE_SPACE_KIMARI_FIT_LAB.md` — Space deployment guide
- ✅ `docs/HUGGINGFACE_ORG_CARD.md` — Organization card draft
- ✅ README visual validation section
- ✅ docs/index.html enhanced hero
- ✅ Gate BLOCKED

## v0.1.43-alpha

- ✅ `docs/LOCAL_INTEGRATION_VALIDATION.md` — local integration validation guide
- ✅ `docs/OPENWEBUI_LOCAL_SETUP.md` — Open WebUI setup
- ✅ `docs/OPENCLAW_LOCAL_SETUP.md` — OpenClaw setup
- ✅ `docs/CONTINUE_LOCAL_SETUP.md` — Continue.dev setup
- ✅ `docs/LOCAL_SHOWCASE_CHECKLIST.md` — public screenshot checklist
- ✅ `scripts/integrations/validate_local_openai_endpoint.py` — endpoint validator
- ✅ `kimari integrations generate` — `--all --json` with base_url, model, notes
- ✅ `kimari integrations validate` — validate local endpoint
- ✅ README local integrations section
- ✅ docs/index.html "Works with local AI tools" card
- ✅ Gate BLOCKED

## v0.1.42-alpha

- ✅ `build_hf_jobs_command_args()` — safe `list[str]` command construction for subprocess
- ✅ `hf_jobs_private_run.py` submit uses arg list, not `hf_cmd.split()` and not `shell=True`
- ✅ `check-release.py` historical version checks no longer hardcode exact versions
- ✅ `check-release.py` benchmark exclusion of `*.example.json` and `*.template.json`
- ✅ Doctor/status suggests `--profile test` when default model missing
- ✅ `docs/LOCAL_OPENAI_ENDPOINT_TEST.md` — local endpoint validation guide
- ✅ README local endpoint GTX 1060 validation section
- ✅ docs/index.html OpenAI-compatible endpoint card
- ✅ docs/SCREENSHOTS.md local endpoint captures
- ✅ Gate BLOCKED

## v0.1.41-alpha

- ✅ `docs/HF_JOBS_ACCESS.md` — generic HF Jobs access documentation (no private details)
- ✅ `docs/HF_JOBS_FALLBACK_RUNNERS.md` — alternative GPU runners
- ✅ `training/scripts/check_hf_jobs_access.py` — programmatic Jobs access check (403 handling, sanitized output)
- ✅ `hf_jobs_private_run.py` supports `--require-jobs-access` (blocks submit only, not dry-run/print-command)
- ✅ `check-release.py` benchmark false positive fix (`*.example.json` ignored)
- ✅ Privacy safeguard: no Pro/billing/subscription details in any committed file
- ✅ Gate BLOCKED

## v0.1.40-alpha (Released)

- ✅ GTX 1060 local runtime validation documented (TinyLlama, NOT Kimari-4B)
- ✅ `docs/GTX1060_LOCAL_RUNTIME_RESULT.md` — honest, sanitized result documentation
- ✅ `benchmarks/results/gtx1060-tinyllama-wsl2.example.json` — machine-readable validation result
- ✅ `detect_compute_capability_from_llama_server()` — fallback compute capability when PyTorch not installed
- ✅ `detect_cuda_version_detailed()` — CUDA version with detection source (nvcc/nvidia-smi)
- ✅ `doctor --deep` compute capability now tries llama-server fallback
- ✅ `check_training_stack.py` reports GPU/CUDA info even without PyTorch
- ✅ README "Validated Locally on GTX 1060" section with CUDA vs CPU-only table
- ✅ docs/index.html GTX 1060 validation card
- ✅ Gate BLOCKED

## v0.1.39-alpha (Released)

- ✅ Fixed recovery merge protects critical fields from incomplete user config (`profiles: {}` no longer destroys valid defaults)
- ✅ Added `merge_user_config_onto_defaults_safely()` helper with protected/safe field separation
- ✅ `default_profile` from incomplete config only accepted if it exists in defaults profiles
- ✅ `write_setup_config()` and `apply_setup_changes()` use safe merge instead of `_base.update(config)`
- ✅ JSON schema updated with `setup_info`, `integrations`, `paths` properties — fixes `doctor --deep` "Additional properties not allowed" warning
- ✅ Gate BLOCKED

## v0.2.0-alpha (Planned)

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
