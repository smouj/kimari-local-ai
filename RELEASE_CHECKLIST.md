# Release Checklist

Use this checklist before publishing any Kimari Local AI release.

## Version & Metadata

- [ ] Version bumped in `pyproject.toml`
- [ ] Version bumped in `kimari/__init__.py` (`__version__`)
- [ ] README.md version badge updated
- [ ] `docs/index.html` version references updated

## Changelog & Roadmap

- [ ] `CHANGELOG.md` entry added for the new version (Keep a Changelog format)
- [ ] `ROADMAP.md` updated — previous version marked "Released", new version marked "Current"

## Testing

- [ ] `python -m pytest tests/ -q` — all tests pass
- [ ] `ruff check kimari/ tests/` — zero lint errors
- [ ] `ruff format --check kimari/ tests/` — zero format errors
- [ ] `make ci-local` — full local CI passes

## CLI Validation

- [ ] `python -m kimari.cli.main --version` — prints correct version
- [ ] `python -m kimari.cli.main start --dry-run` — works without `--profile`
- [ ] `pip install -e .` — installs without errors
- [ ] `kimari --version` — installed entry point works
- [ ] `kimari start --dry-run` — installed entry point works
- [ ] `kimari optimize --profile test --json` — returns valid JSON
- [ ] `kimari perf --profile test --dry-run` — runs without error
- [ ] `kimari setup --dry-run` works
- [ ] `kimari setup --json` returns valid JSON
- [ ] `kimari start --dry-run --strict-flags` works or warns correctly
- [ ] `kimari token create/show/delete` tested with tmp dir or safe environment
- [ ] `kimari setup --write --yes` writes config without prompt
- [ ] `kimari setup --write` (without --yes) prompts for confirmation
- [ ] `kimari models pin-hash <model-id> --dry-run` shows patch
- [ ] `kimari models pin-hash <model-id> --write` with tmp registry

## Setup Write-Mode

- [ ] `kimari setup --write` tested with KIMARI_HOME temporal
- [ ] Config backup created when writing to existing config
- [ ] `kimari setup --json` includes would_write/written/config_path/backup_path
- [ ] Setup writer module exists (kimari/setup/writer.py)
- [ ] No config written without `--write` flag

## SHA256 Tooling

- [ ] `kimari models hash <path>` computes SHA256 of local file
- [ ] `kimari models verify <model-id>` detects hash not pinned
- [ ] `kimari models verify <model-id>` detects match/mismatch with registry
- [ ] `kimari models pin-hash <model-id>` dry-run by default
- [ ] `kimari models pin-hash <model-id> --write` creates backup before modifying user registry
- [ ] No invented hashes (sha256 null until explicitly pinned)

## New Documentation

- [ ] `docs/REVERSE_PROXY_AUTH.md` exists
- [ ] `docs/API_PLAN.md` exists
- [ ] `docs/PUBLISHING.md` updated with v0.1.14 TestPyPI section
- [ ] `scripts/windows/README.md` updated with wheel/TestPyPI install, setup --write, models hash

## Build & Package

- [ ] `python -m build` — builds without errors
- [ ] `twine check dist/*` — no warnings or errors
- [ ] Wheel contains `kimari/py.typed`
- [ ] Wheel does **not** contain `models/*.gguf`, `.kimari/`, `kimari-server.log`, or `.kimari-server.pid`

## Release Validation Script

- [ ] `python scripts/release/check-release.py` — all checks pass

## Content Review

- [ ] Kimari-4B is **not** advertised as published/released
- [ ] ROCm is marked as **experimental** (not stable)
- [ ] SHA256 verification is **not** marked as enforced if hashes are still `null`
- [ ] `default_profile` is `"test"` in `config/kimari.profiles.json`
- [ ] No GGUF files are tracked in git
- [ ] GitHub Pages (`docs/index.html`) checked locally or via file review
- [ ] `docs/index.html` SEO metadata is present (canonical, og:title, og:image)
- [ ] `docs/INSTALL_WSL2.md` is up to date
- [ ] `docs/PUBLISHING.md` is up to date
- [ ] README links to Release Checklist
- [ ] ROADMAP marks current version as "Current"
- [ ] No "Kimari-4B released" false claim anywhere
- [ ] docs/integrations/OPENCLAW.md exists and mentions Chat Completions (not Responses API)
- [ ] docs/integrations/HERMES.md exists
- [ ] docs/integrations/CONTINUE.md exists
- [ ] docs/integrations/OPENAI_COMPATIBLE_CLIENTS.md exists
- [ ] config/integrations/ directory with example configs exists
- [ ] No "Responses API supported" false claim anywhere
- [ ] README mentions `kimari setup --write`
- [ ] README mentions `models hash` and `models verify`
- [ ] README links to reverse proxy auth guide
- [ ] README links to API plan
- [ ] README mentions `setup --write --yes`
- [ ] README mentions `pin-hash` workflow
- [ ] Model path resolver tested
- [ ] start_server uses resolve_model_path()
- [ ] benchmarks/RESULT_FORMAT.md exists
- [ ] benchmarks/examples/perf-result.example.json exists
- [ ] docs/API_OPENAPI_DRAFT.yaml exists
- [ ] Windows wheel scripts exist (scripts/windows/build-wheel.ps1, install-from-wheel.ps1, install-from-testpypi.ps1)
- [ ] docs/PUBLISHING.md contains v0.1.15 TestPyPI section
- [ ] `default_profile` is still `"test"`
- [ ] No "Kimari-4B released" false claim anywhere
- [ ] No "Responses API supported" false claim anywhere
- [ ] New profiles exist (gtx1060-safe, gtx1060-fast, gtx1080-balanced, gtx1080-longctx, ide-local, agent-local, openclaw-local, hermes-local)
- [ ] Windows scripts exist (scripts/windows/kimari-launcher.ps1, kimari-doctor.ps1)
- [ ] llama-server flag detection tests pass
- [ ] TestPyPI validation result documented if executed
- [ ] README mentions `kimari setup`
- [ ] README mentions `--strict-flags`
- [ ] README mentions `kimari token create`

## Community & Contribution

- [ ] `CODE_OF_CONDUCT.md` exists
- [ ] Conduct contact reviewed (TODO: replace with dedicated private contact before broad public launch)
- [ ] `CONTRIBUTING.md` exists and is up to date
- [ ] `SUPPORT.md` exists
- [ ] `GOVERNANCE.md` exists
- [ ] `MAINTAINERS.md` exists
- [ ] Issue templates exist (bug_report.yml, feature_request.yml, performance_report.yml, integration_request.yml, config.yml)
- [ ] PR template exists (.github/pull_request_template.md)
- [ ] README links to Code of Conduct / Contributing / Support
- [ ] docs/index.html mentions Community / Code of Conduct / Contributing

## Packaging & CI

- [ ] `pyproject.toml` license uses SPDX format (no setuptools deprecation warning)
- [ ] `MANIFEST.in` includes community files in sdist
- [ ] `wheel-install-smoke` CI job exists and passes
- [ ] Wheel contains `kimari/defaults/*.json` (packaged defaults)
- [ ] `pip install dist/*.whl` works in clean venv
- [ ] `kimari --version` works from wheel install
- [ ] `kimari config path` works from wheel install
- [ ] `kimari setup --json` works from wheel install
- [ ] `kimari start --dry-run` works from wheel install
- [ ] `kimari token create/show/delete` works from wheel install
- [ ] `kimari setup --write` works from wheel install
- [ ] `kimari models hash` works from wheel install
- [ ] No PyPI real without TestPyPI validated
- [ ] No hashes invented in registry

## Publishing (Manual)

### TestPyPI (Pre-release Validation)

Before publishing to the real PyPI, validate the package on TestPyPI:

```bash
# 1. Build the package
python -m build

# 2. Check with twine
twine check dist/*

# 3. Upload to TestPyPI
twine upload --repository testpypi dist/*

# 4. Verify the package installs correctly from TestPyPI
pip install -i https://test.pypi.org/simple/ kimari-local-ai
```

> **Note:** This is manual for now. Do not configure automated PyPI publishing from CI until TestPyPI has been validated at least once.

### PyPI (Production)

Do **not** upload to the real PyPI until TestPyPI validation passes and the version is confirmed working:

```bash
# Only after successful TestPyPI validation
twine upload dist/*
```

### GitHub Release

- [ ] GitHub Release created with notes from CHANGELOG
- [ ] Git tag created: `git tag v0.1.X-alpha && git push origin v0.1.X-alpha`

## v0.1.16 Checks

- [ ] API experimental dry-run works (`kimari api --experimental --dry-run`)
- [ ] api extra dependency documented in `pyproject.toml` (`[project.optional-dependencies]` includes `api`)
- [ ] `docs/API_EXPERIMENTAL.md` exists
- [ ] `docs/PYPI_RELEASE_GATE.md` exists
- [ ] `docs/MODEL_HASHING.md` exists
- [ ] `docs/BENCHMARK_SUBMISSIONS.md` exists
- [ ] Benchmark examples exist (`benchmarks/examples/perf-result.gtx1060.example.json`, `perf-result.gtx1080.example.json`)
- [ ] No PyPI real without release gate approved (`docs/PYPI_RELEASE_GATE.md` process followed)
- [ ] `kimari api --dry-run` works without fastapi installed (graceful fallback)
- [ ] `kimari/api/app.py`, `kimari/api/schemas.py`, `kimari/api/server.py` exist
- [ ] `kimari api --experimental` command registers correctly
- [ ] API endpoints return expected responses (health, status, config, profiles, models, optimize, perf/dry-run)
- [ ] Server start/stop endpoints return 501 (planned, not implemented)
- [ ] Experimental auth middleware present but not enforced by default
- [ ] `default_profile` is still `"test"`
- [ ] No "Kimari-4B released" false claim anywhere
- [ ] No "Responses API supported" false claim anywhere

## v0.1.17 Checks

- [ ] MODEL_CARD.md exists and says "Planned / Not Released" or "Training Design" (not released)
- [ ] docs/MODEL_TRAINING_PLAN.md exists
- [ ] docs/MODEL_BASE_SELECTION.md exists
- [ ] MODEL_LICENSES.md exists and mentions SmolLM3, Qwen, Llama candidates
- [ ] dataset/README.md exists with dataset policy
- [ ] dataset/schema/sft.schema.json exists and parses as valid JSON
- [ ] dataset/schema/preference.schema.json exists and parses as valid JSON
- [ ] training/README.md exists
- [ ] training/configs/kimari_sft_lora.example.yaml exists
- [ ] training/configs/kimari_orpo.example.yaml exists
- [ ] training/scripts/prepare_dataset.py exists and supports --help
- [ ] training/scripts/train_sft_lora.py exists and supports --dry-run
- [ ] eval/README.md exists
- [ ] eval/kimarifit_prompts.jsonl exists and each line is valid JSON
- [ ] docs/HUGGINGFACE_RELEASE.md exists
- [ ] No GGUF files tracked in git
- [ ] No claim that Kimari-4B is released
- [ ] No fake MMLU/HumanEval numbers in MODEL_CARD
- [ ] No weights or model files committed
- [ ] No HF API keys or secrets in any file
- [ ] `default_profile` is still `"test"`

## v0.1.18 Checks

- [ ] docs/MODEL_DECISION_RECORD.md exists and says "Proposed" (not "Accepted")
- [ ] training/configs/base_candidates.yaml exists and lists all 3 candidates
- [ ] training/scripts/select_base_model.py exists and `--json` works
- [ ] dataset/samples/sft_seed.jsonl exists and each line is valid JSON with required fields
- [ ] dataset/samples/preference_seed.jsonl exists and each line is valid JSON with required fields
- [ ] training/scripts/build_dataset_mix.py works with sample data and tmp output
- [ ] training/scripts/prepare_dataset.py supports `--dedupe`, `--min-chars`, `--max-chars`, `--require-tags`, `--report`
- [ ] eval/kimarifit.py `--dry-run --json` works
- [ ] eval/rubrics/kimarifit_rubric.md exists
- [ ] training/scripts/export_gguf_plan.py `--dry-run` works
- [ ] docs/FIRST_TRAINING_RUN.md exists
- [ ] eval/results/.gitkeep exists
- [ ] eval/results/*.json in .gitignore
- [ ] dataset/build/ in .gitignore
- [ ] No real evaluation results committed
- [ ] No weights or GGUF files committed
- [ ] MODEL_CARD.md still says no weights released
- [ ] No fake benchmark numbers in MODEL_CARD
- [ ] `default_profile` is still `"test"`
- [ ] No "Kimari-4B released" false claim anywhere

## v0.1.19 Checks

- [ ] docs/BASE_MODEL_ACCEPTANCE.md exists and says "private training" (not public release)
- [ ] dataset/v0/ directory exists with sft_v0.jsonl, preference_v0.jsonl, eval_holdout.jsonl
- [ ] dataset/v0/README.md exists with dataset policy
- [ ] training/scripts/validate_training_ready.py exists and --json works
- [ ] eval/scoring/kimarifit_dimensions.json exists and parses as valid JSON
- [ ] eval/scripts/summarize_results.py exists and --json works on synthetic data
- [ ] training/configs/kimari_sft_lora.v0.example.yaml exists
- [ ] training/configs/kimari_orpo.v0.example.yaml exists
- [ ] docs/FIRST_PRIVATE_TRAINING_RUN.md exists
- [ ] docs/HF_PLACEHOLDER_PLAN.md exists
- [ ] MODEL_CARD.md says no weights released
- [ ] No GGUF files tracked in git
- [ ] No fake benchmark numbers in MODEL_CARD
- [ ] base_candidates.yaml has accepted_private_training_candidate status
- [ ] SmolLM3 selected_for_private_sft: true
- [ ] SmolLM3 selected_for_public_release: false
- [ ] `default_profile` is still `"test"`
- [ ] No "Kimari-4B released" false claim anywhere

## v0.1.20 Checks

- [ ] docs/BASELINE_EVAL_PLAN.md exists
- [ ] docs/ADAPTER_ARTIFACT_POLICY.md exists
- [ ] docs/PRIVATE_TRAINING_RUNBOOK.md exists
- [ ] docs/ADAPTER_PREVIEW_GATE.md exists and says BLOCKED as default
- [ ] training/configs/private_sft_run.v0.yaml exists with public_release_allowed: false
- [ ] training/scripts/run_private_sft_dryrun.py exists and --json works
- [ ] training/scripts/build_v0_pipeline.py exists and --dry-run --json works
- [ ] eval/baseline/README.md exists
- [ ] eval/scripts/compare_runs.py exists and --json works with fixtures
- [ ] .gitignore blocks training/adapters/, training/runs/, *.safetensors, *.gguf
- [ ] MODEL_CARD.md checklist fixed (seed dataset In Progress, full dataset Not started)
- [ ] MODEL_CARD.md version history updated (0.1.19-alpha → Released)
- [ ] eval/kimarifit.py supports --run-id and --model-label
- [ ] No GGUF files tracked in git
- [ ] No adapter/weight files tracked in git
- [ ] No "Kimari-4B released" false claim anywhere

## v0.1.21 Checks

- [ ] training/templates/adapter_manifest.template.yaml exists
- [ ] training/scripts/create_adapter_manifest.py exists and --dry-run --json works
- [ ] docs/PRIVATE_SFT_EXECUTION_CHECKLIST.md exists
- [ ] docs/SFT_TO_ORPO_DECISION.md exists
- [ ] docs/PRIVATE_EVAL_RESULTS_POLICY.md exists
- [ ] eval/templates/eval_summary.template.json exists and parses as valid JSON
- [ ] eval/scripts/create_eval_summary.py exists and --json works with fixtures
- [ ] eval/scripts/compare_runs.py supports --summary-output and verdict logic
- [ ] docs/ADAPTER_PREVIEW_GATE.md mentions BLOCKED as default
- [ ] docs/ADAPTER_PREVIEW_GATE.md mentions safety_regression_detected
- [ ] docs/ADAPTER_ARTIFACT_POLICY.md mentions adapter manifest template
- [ ] docs/PRIVATE_TRAINING_RUNBOOK.md references create_adapter_manifest.py and SFT_TO_ORPO_DECISION
- [ ] No adapter files (.safetensors, .bin, .pt, .pth, .ckpt, .gguf) tracked in git
- [ ] No fake benchmark claims anywhere
- [ ] Preview gate remains BLOCKED
- [ ] `default_profile` is still `"test"`
- [ ] No "Kimari-4B released" false claim anywhere

## v0.1.22 Checks

- [ ] docs/REMOTE_GPU_RUNPOD_GUIDE.md exists
- [ ] training/requirements-training.txt exists
- [ ] training/scripts/preflight_private_sft.py exists and --json works without torch
- [ ] training/scripts/postrun_private_sft.py exists and --dry-run --json works with fake paths
- [ ] training/configs/private_sft_execution.example.yaml exists
- [ ] docs/PRIVATE_RUN_ARTIFACTS.md exists
- [ ] docs/PRIVATE_RUN_FAILURES.md exists
- [ ] training/scripts/run_training_command_preview.py exists and --json works
- [ ] eval/scripts/run_baseline_eval_plan.py exists and --dry-run --json works
- [ ] eval/scripts/run_adapter_eval_plan.py exists and --dry-run --json works
- [ ] train_sft_lora.py supports --print-command and --estimate-only
- [ ] No training outputs committed
- [ ] No adapter/weight files tracked in git
- [ ] Preview gate still BLOCKED
- [ ] `default_profile` is still `"test"`
- [ ] No "Kimari-4B released" false claim anywhere

## v0.1.23 Checks

- [ ] postrun_private_sft.py passes --json to create_eval_summary subprocess correctly
- [ ] preflight_private_sft.py reads dataset_build_dir from run_config if available
- [ ] preflight_private_sft.py falls back to default dataset/build/kimari-v0/report.json
- [ ] docs/SCREENSHOTS.md exists
- [ ] docs/assets/screenshots/README.md exists with naming conventions and policy
- [ ] docs/assets/screenshots/PLACEHOLDER.md exists with planned screenshots checklist
- [ ] No secrets in screenshot docs/placeholders
- [ ] No benchmark claims in screenshot docs
- [ ] README.md links to docs/SCREENSHOTS.md
- [ ] docs/index.html mentions screenshots/CLI preview
- [ ] No adapter/weight files tracked in git
- [ ] Preview gate still BLOCKED
- [ ] `default_profile` is still `"test"`
- [ ] No "Kimari-4B released" false claim anywhere

## v0.1.24 Checks

- [ ] docs/FIRST_PRIVATE_SFT_RECORD.md exists
- [ ] training/templates/private_sft_run_record.template.json exists and parses as valid JSON
- [ ] training/scripts/create_private_run_record.py exists and --dry-run --json works
- [ ] Run record template has gate.state = "BLOCKED"
- [ ] Run record template has public_release_allowed = false
- [ ] Run record template has hf_upload_allowed = false
- [ ] docs/SAFE_SCREENSHOT_CAPTURE.md exists
- [ ] scripts/docs/generate_cli_screenshot_text.py exists and --kind setup --json works
- [ ] docs/assets/screenshots/examples/*.txt exist (5 files)
- [ ] Screenshot examples contain no token/password/api_key/private key patterns
- [ ] docs/SCREENSHOTS.md references SAFE_SCREENSHOT_CAPTURE
- [ ] docs/SCREENSHOTS.md references screenshot examples
- [ ] README.md links to FIRST_PRIVATE_SFT_RECORD.md
- [ ] README.md links to SAFE_SCREENSHOT_CAPTURE.md
- [ ] No screenshots above reasonable size if images exist
- [ ] No adapter/weights/GGUF tracked in git
- [ ] Preview gate still BLOCKED
- [ ] `default_profile` is still `"test"`
- [ ] No "Kimari-4B released" false claim anywhere

## v0.1.25 Checks

- [ ] docs/HF_TOKEN_SAFETY.md exists
- [ ] scripts/security/scan_for_secrets.py exists and --paths README.md docs --json works
- [ ] scan_for_secrets.py reports no critical findings on scanned paths
- [ ] docs/FIRST_PRIVATE_SFT_HANDOFF.md exists
- [ ] docs/PRIVATE_SFT_RUN_COMMANDS.md exists
- [ ] create_private_run_record.py rejects /home/user/ paths
- [ ] create_private_run_record.py rejects /Users/user/ paths (macOS)
- [ ] create_private_run_record.py rejects C:\Users\user\ paths (Windows)
- [ ] create_private_run_record.py detects suspicious patterns in summaries
- [ ] create_private_run_record.py includes security_scan_status field
- [ ] SAFE_SCREENSHOT_CAPTURE.md uses real commands (not nonexistent ones)
- [ ] docs/SCREENSHOTS.md references HF_TOKEN_SAFETY
- [ ] README.md links to HF_TOKEN_SAFETY.md
- [ ] README.md links to FIRST_PRIVATE_SFT_HANDOFF.md
- [ ] No HF token pattern (hf_...) in any tracked file
- [ ] No adapter/weights/GGUF tracked in git
- [ ] Preview gate still BLOCKED
- [ ] `default_profile` is still `"test"`
- [ ] No "Kimari-4B released" false claim anywhere
- [ ] docs/PERFORMANCE_TUNING_PLAN.md exists
- [ ] docs/SHOWCASE_PLAN.md exists
- [ ] kimari/performance/benchmark_plan.py exists
- [ ] kimari benchmark --dry-run --json works and returns measured: false
- [ ] kimari tune --dry-run --json works and returns apply_blocked: true
- [ ] kimari tune --apply is blocked (exits with error)
- [ ] benchmark plan output does not contain measured scores
- [ ] README mentions 'benchmark' and 'tune' commands
- [ ] No fake benchmark claims in PERFORMANCE_TUNING_PLAN.md

## v0.1.26 Checks

- [ ] Secret scanner hardened: security guide files are scanned line-by-line, not skipped
- [ ] scan_for_secrets.py allows safe placeholders (hf_..., hf_your_token_here, <HF_TOKEN>, your-api-key, sk-..., <token>, <API_KEY>)
- [ ] scan_for_secrets.py has --include-history-note flag
- [ ] scan_for_secrets.py version is 1.1.0
- [ ] docs/SECRET_SCAN_POLICY.md exists
- [ ] docs/MEASURED_BENCHMARKS.md exists
- [ ] docs/DOCTOR_DEEP.md exists
- [ ] kimari/performance/measured_benchmark.py exists
- [ ] kimari/doctor/deep.py exists
- [ ] kimari/doctor/__init__.py exists
- [ ] benchmark prompts exist (benchmarks/prompts/local_benchmark_prompts.jsonl)
- [ ] benchmarks/results/.gitkeep exists
- [ ] benchmarks/results/*.json is in .gitignore
- [ ] No measured results committed to git
- [ ] kimari benchmark --measure requires --yes flag
- [ ] kimari benchmark --measure requires --endpoint flag
- [ ] kimari benchmark --measure requires --model flag
- [ ] kimari benchmark --measure handles endpoint failure without stacktrace
- [ ] kimari doctor --deep --json works
- [ ] kimari tune --apply is still blocked
- [ ] tune --apply returns apply_blocked: true
- [ ] No fake benchmark numbers anywhere
- [ ] docs/PERFORMANCE_TUNING_PLAN.md has three-phase separation
- [ ] Preview gate still BLOCKED
- [ ] default_profile is still "test"
- [ ] No "Kimari-4B released" false claim anywhere
- [ ] No adapter/weights/GGUF tracked in git
- [ ] README mentions measured benchmark, doctor --deep, secret scan policy
- [ ] kimari gateway --dry-run works
- [ ] kimari gateway --status --json works
- [ ] kimari gateway --plan --json works
- [ ] kimari update check works offline
- [ ] kimari update check --json works
- [ ] kimari update check --online works (or fails gracefully)
- [ ] kimari status --json includes gateway and preview_gate fields
- [ ] doctor --deep includes CUDA/NVIDIA, Gateway Module, Integration Docs checks
- [ ] docs/GATEWAY_PLAN.md exists
- [ ] docs/UPDATE.md exists
- [ ] docs/INSTALL_MATRIX.md exists
- [ ] docs/OPENWEBUI_OPENCLAW_QUICK_CONFIG.md exists
- [ ] kimari/gateway/ module exists with __init__.py, state.py, plan.py
- [ ] kimari/update/ module exists with __init__.py, check.py
- [ ] Gateway never starts a real server
- [ ] Update never auto-installs anything
- [ ] No 0.0.0.0 binding in gateway defaults

## v0.1.27 Checks

- [ ] `kimari status` human output shows structured table
- [ ] `kimari doctor --deep` human output shows PASS/WARN/FAIL table with suggested next steps
- [ ] `kimari integrations generate --all --json` works
- [ ] `kimari integrations generate --target openwebui --json` works
- [ ] `kimari integrations generate --target openclaw --json` works
- [ ] `kimari integrations generate --target hermes --json` works
- [ ] `kimari integrations generate --target continue --json` works
- [ ] Integration configs contain no token/API key fields
- [ ] `kimari integrations generate --target openwebui --base-url http://example.com` shows non-local warning
- [ ] `kimari integrations generate --target openwebui --write` without --output is rejected
- [ ] Gateway wording does not claim gateway serves OpenAI-compatible API
- [ ] docs/GATEWAY_PLAN.md does not claim gateway provides OpenAI-compatible endpoints
- [ ] docs/INTEGRATION_CONFIG_GENERATOR.md exists
- [ ] docs/GATEWAY_PROTOTYPE_PLAN.md exists
- [ ] docs/CONSOLE_UX.md exists
- [ ] scripts/docs/generate_safe_cli_screenshots_plan.py exists and --json works
- [ ] kimari/console/render.py exists
- [ ] kimari/integrations/config_generator.py exists
- [ ] Screenshot plan generator works
- [ ] Preview gate still BLOCKED
- [ ] `default_profile` is still "test"
- [ ] No "Kimari-4B released" false claim anywhere
- [ ] No adapter/weights/GGUF tracked in git

## v0.1.28 Checks

- [ ] docs/KIMARI4B_PRIVATE_SFT_RUN.md exists
- [ ] docs/KIMARI4B_FIRST_RUN_CHECKLIST.md exists
- [ ] docs/KIMARI4B_EVAL_CRITERIA.md exists
- [ ] training/configs/kimari4b_private_sft_run.v0.yaml exists and parses correctly
- [ ] training/configs/kimari4b_private_sft_run.v0.yaml has public_release_allowed: false
- [ ] training/configs/kimari4b_private_sft_run.v0.yaml has hf_upload_allowed: false
- [ ] training/configs/kimari4b_private_sft_run.v0.yaml has preview_gate_state: BLOCKED
- [ ] training/scripts/kimari4b_private_sft_command.py exists and --json works
- [ ] training/scripts/kimari4b_private_sft_command.py --markdown works
- [ ] eval/scripts/kimari4b_eval_plan.py exists and --json works
- [ ] eval/scripts/kimari4b_eval_plan.py --markdown works
- [ ] training/templates/kimari4b_private_summary.template.json exists and parses as valid JSON
- [ ] Summary template has preview_gate_state: BLOCKED
- [ ] Summary template has public_release_allowed: false
- [ ] Summary template has hf_upload_allowed: false
- [ ] Summary template has manual_review_required: true
- [ ] docs/FIRST_PRIVATE_SFT_HANDOFF.md has Kimari-4B specific section
- [ ] docs/ADAPTER_PREVIEW_GATE.md has Kimari-4B first private run section
- [ ] ADAPTER_PREVIEW_GATE.md says Kimari-4B remains BLOCKED
- [ ] README.md mentions Kimari-4B first private SFT run
- [ ] README.md links to KIMARI4B_PRIVATE_SFT_RUN.md
- [ ] docs/index.html mentions Kimari-4B private SFT preparation
- [ ] MODEL_CARD.md still says no public weights
- [ ] No GGUF/adapter/weight files tracked in git
- [ ] No false Kimari-4B release claims anywhere
- [ ] Preview gate still BLOCKED
- [ ] `default_profile` is still "test"

## v0.1.29 Checks

- [ ] docs/HF_JOBS_PRIVATE_RUN.md exists
- [ ] docs/HF_JOBS_RESULT_HANDOFF.md exists
- [ ] training/configs/hf_jobs_kimari4b_smoke.v0.yaml exists
- [ ] training/scripts/hf_jobs_private_run.py exists
- [ ] training/scripts/hf_jobs_status.py exists
- [ ] training/templates/hf_jobs_smoke_summary.template.json exists
- [ ] training/scripts/validate_private_sft_commands.py exists
- [ ] hf_jobs_private_run.py does not accept --token
- [ ] hf_jobs_private_run.py requires --allow-submit and --yes for submission
- [ ] hf_jobs_private_run.py --dry-run does not submit
- [ ] hf_jobs_private_run.py --print-command works
- [ ] Smoke config has allow_training: false
- [ ] Smoke config has allow_hf_upload: false
- [ ] train_sft_lora.py --show-supported-flags --json works
- [ ] kimari4b_private_sft_run.v0.yaml has expected_local_artifacts (not expected_artifacts)
- [ ] kimari4b_private_sft_run.v0.yaml has forbidden_commit_artifacts (not forbidden_artifacts)
- [ ] kimari4b_private_sft_run.v0.yaml has local_only: true
- [ ] Command generator training_real has no --dataset-path, --eval-dataset-path, --output-dir
- [ ] validate_private_sft_commands validates generated JSON
- [ ] hf_jobs_status.py is read-only
- [ ] HF_TOKEN_SAFETY.md has HF Jobs section
- [ ] KIMARI4B_PRIVATE_SFT_RUN.md has HF Jobs smoke test section
- [ ] KIMARI4B_FIRST_RUN_CHECKLIST.md has HF Jobs items
- [ ] Gate still BLOCKED
- [ ] `default_profile` is still "test"
- [ ] No "Kimari-4B released" false claim anywhere

## Post-Release

- [ ] GitHub topics still accurate (20 topics, lowercase, hyphens)
- [ ] `docs/index.html` live site reflects new version
- [ ] ROADMAP.md next version entry created
- [ ] TestPyPI validation result recorded (if attempted)
- [ ] GitHub release tag pushed
