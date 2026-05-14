## v0.1.77-alpha — Private subset30 manual review completed

- [x] pyproject.toml version is 0.1.77-alpha
- [x] kimari/__init__.py version is 0.1.77-alpha
- [x] Private raw artifact downloaded outside the public repository
- [x] 30/30 subset30 items manually reviewed
- [x] Sanitized manual review summary updated
- [x] Decision recorded as `safety_fix_required`
- [x] Gate remains BLOCKED
- [x] No public benchmark claim
- [x] No public weights or GGUF
- [x] No raw outputs committed

Validation:
- [x] `python eval/scripts/validate_manual_review_summary.py --summary reports/evals/kimari_runtime_15b_500step_subset30/manual_review_summary.json --json`
- [x] `pytest tests/test_release_v0177.py -q`
- [x] `ruff check kimari/ tests/ training/ eval/ scripts/ dataset/`
- [x] `ruff format --check kimari/ tests/ training/ eval/ scripts/ dataset/`
- [x] `python scripts/release/check-release.py`

# Release Checklist


## v0.1.76-alpha — Private eval artifact persistence fix

- [x] pyproject.toml version is 0.1.76-alpha
- [x] kimari/__init__.py version is 0.1.76-alpha
- [x] `upload_private_eval_artifacts.py` exists
- [x] `validate_private_eval_artifacts.py` exists
- [x] subset30 config exists
- [x] subset30 config has `raw_outputs_private_required: true`
- [x] artifact persistence summary exists
- [x] artifact summary has `raw_outputs_private_uploaded` explicit
- [x] artifact summary has `manual_review_available` explicit
- [x] raw_outputs_committed=false
- [x] public_benchmark_allowed=false
- [x] no raw_outputs_private.json tracked in public repo
- [x] no public GGUF
- [x] no public weights
- [x] gate BLOCKED

## v0.1.75-alpha — Private raw retrieval + manual review execution attempt

- [x] pyproject.toml version is 0.1.75-alpha
- [x] kimari/__init__.py version is 0.1.75-alpha
- [x] private review directory exists outside public repo
- [x] HF bucket path inspected for `raw_outputs_private.json`
- [x] manual review doc exists
- [x] manual review summary exists
- [x] manual review generator exists
- [x] manual review validator passes
- [x] manual_review_status is explicit
- [x] decision is explicit
- [x] raw_outputs_committed=false
- [x] public_benchmark_allowed=false
- [x] no raw outputs tracked
- [x] no public GGUF
- [x] no public weights
- [x] gate BLOCKED
- [x] decision `blocked_missing_raw_outputs` if private raw artifact cannot be retrieved

## v0.1.74-alpha — Private manual review gate

- [x] pyproject.toml version is 0.1.74-alpha
- [x] kimari/__init__.py version is 0.1.74-alpha
- [x] manual review doc exists
- [x] manual review summary exists
- [x] manual review validator passes
- [x] raw_outputs_committed=false
- [x] public_benchmark_allowed=false
- [x] no raw outputs tracked
- [x] no public GGUF
- [x] no public weights
- [x] gate BLOCKED
- [x] decision inconclusive pending private raw-output review

Use this checklist before publishing any Kimari Local AI release.

## v0.1.62 Checks — SFT v1 pre-submit hardening

- [ ] Result doc placeholder does NOT claim training_performed=true
- [ ] Result doc placeholder does NOT claim adapter_generated=true
- [ ] Result doc status is PENDING (not COMPLETED)
- [ ] HF Jobs wrapper: preflight runs before training in execution_order
- [ ] HF Jobs wrapper: preflight_before_training=true in dry-run JSON
- [ ] HF Jobs wrapper: training_after_preflight=true in dry-run JSON
- [ ] HF Jobs wrapper: validate_execution_order() blocks bad order
- [ ] No --token *** in any training script
- [ ] No shell=True or .split() in subprocess calls
- [ ] Gate BLOCKED

## v0.1.61 Checks — First SFT v1 real short run

- [ ] SFT v1 run result doc exists (`docs/KIMARI_RUNTIME_15B_SFT_V1_RESULT.md`)
- [ ] Run summary validator exists (`training/scripts/validate_sft_v1_run_summary.py`)
- [ ] Run summary creator exists (`training/scripts/create_sft_v1_run_summary.py`)
- [ ] Completed summary template exists
- [ ] training_performed=true in summary (if run completed)
- [ ] adapter_committed_public=false
- [ ] hf_public_upload_performed=false
- [ ] gguf_generated=false
- [ ] raw_logs_committed=false
- [ ] public_benchmark_allowed=false
- [ ] gate_state=BLOCKED
- [ ] No safetensors/GGUF tracked in git
- [ ] No raw logs committed
- [ ] No public benchmark claims
- [ ] Preflight passes
- [ ] Summary validator passes
- [ ] Gate BLOCKED

## v0.1.60 Checks — SFT v1 training configuration + dry-run

- [ ] `training/configs/kimari_runtime_15b_sft_v1.yaml` exists
- [ ] Base model is Apache-2.0 (Qwen/Qwen2.5-1.5B-Instruct)
- [ ] `training/scripts/preflight_sft_v1.py` exists
- [ ] `training/scripts/sft_v1_command_preview.py` exists
- [ ] `training/scripts/hf_jobs_sft_v1.py` exists
- [ ] `training/templates/sft_v1_run_summary.template.json` exists
- [ ] Preflight passes with --strict
- [ ] Command preview generates local + HF Jobs dry-run commands
- [ ] HF Jobs wrapper defaults to dry-run
- [ ] No --token arg in any training script
- [ ] No shell=True or .split() in subprocess calls
- [ ] Dataset train/validation files exist and are valid
- [ ] Config has push_to_hub=false, report_to=none, gate_state=BLOCKED
- [ ] Config has public_release_allowed=false, hf_public_upload_allowed=false
- [ ] Config has gguf_export_allowed=false
- [ ] No training performed
- [ ] No adapter or GGUF files committed or uploaded
- [ ] No HF Jobs submitted
- [ ] Gate BLOCKED

## v0.1.59 Checks — Kimari SFT v1 dataset

- [ ] `dataset/sft_v1/` exists
- [ ] `dataset/schema/kimari_sft_item.schema.json` exists
- [ ] `dataset/scripts/validate_kimari_sft_v1.py` exists
- [ ] `dataset/scripts/build_kimari_sft_v1.py` exists
- [ ] license manifest exists (`license_manifest.yaml` + `license_manifest.json`)
- [ ] build output exists
- [ ] no blocked licenses in manifest
- [ ] no secrets in dataset, manifests, or generated build output
- [ ] no PII in dataset, manifests, or generated build output
- [ ] no Kimari-4B released claim
- [ ] no training run executed
- [ ] no HF Jobs executed
- [ ] no public weights, adapters, or GGUF files
- [ ] gate BLOCKED

## v0.1.58 Checks — Open-license base bakeoff

- [ ] `eval/configs/open_base_bakeoff_v1.yaml` exists
- [ ] `eval/scripts/run_open_base_bakeoff.py` exists
- [ ] `eval/scripts/validate_open_base_bakeoff_summary.py` exists
- [ ] `eval/templates/open_base_bakeoff_summary.template.json` exists
- [ ] bakeoff runner --dry-run works
- [ ] bakeoff summary validator passes on pending summary
- [ ] only permissive-license candidates in allowed list
- [ ] no blocked model marked as allowed
- [ ] no public benchmark claim
- [ ] no raw outputs committed
- [ ] gate BLOCKED
- [ ] Kimari-4B not released

## v0.1.57 Checks — Open-license policy + bakeoff readiness

- [x] `docs/KIMARI_OPEN_LICENSE_POLICY.md` exists
- [x] open-license policy approves only permissive Apache 2.0 bases for official public models
- [x] open-license policy blocks non-commercial, research-only, and custom-restrictive bases for public Kimari models
- [x] `docs/KIMARI_BASE_MODEL_LICENSE_MATRIX.md` exists
- [x] base model license matrix includes approved and blocked candidates
- [x] `docs/KIMARI_OPEN_BASE_BAKEOFF_PLAN.md` exists
- [x] bakeoff plan includes Qwen2.5-1.5B, SmolLM2-1.7B, SmolLM3-3B, and Qwen3-4B
- [x] `docs/KIMARI_SFT_V1_DATASET_LICENSE_PLAN.md` exists
- [x] SFT v1 dataset license plan requires permissive sources and 1,400–1,700 examples
- [x] `docs/KIMARI_SFT_V1_TRAINING_PLAN.md` exists
- [x] SFT v1 training plan covers Runtime 1.5B, Core 3B, and 4B candidate lanes
- [x] `docs/ENVIRONMENT_STATUS.md` exists
- [x] `docs/KIMARI4B_RUN_HISTORY.md` exists
- [x] `scripts/release/check_public_pages_content.py` exists
- [x] `scripts/release/check_state_consistency.py` exists
- [x] Release gate remains BLOCKED
- [x] No training executed
- [x] No HF Jobs executed
- [x] No public weights/adapters/GGUF files
- [x] No public benchmark claims

## v0.1.56 Checks — Hugging Face public polish + consistency hardening

- [x] `scripts/release/check_public_version_consistency.py` exists
- [x] public version consistency reads version from `pyproject.toml`
- [x] no future dates remain in `CHANGELOG.md`
- [x] README badge uses the current version
- [x] `docs/index.html` visible status uses the current version
- [x] `docs/HUGGINGFACE_ORG_CARD.md` has current version and professional positioning
- [x] `huggingface/kimari-fit-lab/README.md` has current version
- [x] Kimari-4B is clearly marked not released
- [x] no public weights/adapters/GGUF claims
- [x] no public benchmark claims
- [x] Collection docs say reference/community models are not official Kimari models
- [x] `docs/HUGGINGFACE_PROFILE_SMOUJ013.md` exists
- [x] `docs/BRAND_ASSETS_PLAN.md` exists
- [x] `docs/KIMARI_FLOW_DIAGRAM.md` exists
- [x] `docs/KIMARI4B_PLACEHOLDER_MODEL_CARD.md` exists and is not published automatically
- [x] Kimari Fit Lab remains static: no model execution, no downloads, no API keys
- [x] Gate remains BLOCKED


## v0.1.54 Checks

- [x] `eval/configs/kimari_eval_v1_baseline_vs_adapter_subset10.yaml` exists
- [x] subset10 config uses `subset_size: 10`, `temperature: 0.2`, `max_tokens: 256`
- [x] subset10 config keeps `raw_outputs_commit_allowed: false`
- [x] subset10 config keeps `public_benchmark_allowed: false`
- [x] subset10 config keeps `manual_review_required: true`
- [x] subset10 config keeps `gate_state: BLOCKED`
- [x] HF Jobs subset10 run completed (`6a03be047618f125ee2b7a5a`)
- [x] `reports/evals/kimari_v0154_baseline_vs_adapter_subset10/summary.json` exists
- [x] summary has `raw_outputs_committed: false`
- [x] summary has `public_benchmark_allowed: false`
- [x] summary has `manual_review_required: true`
- [x] summary has `gate_state: BLOCKED`
- [x] summary has `score_status: not_scored`
- [x] result doc exists (`docs/KIMARI_EVAL_V0154_RESULT.md`)
- [x] no raw outputs committed
- [x] no public benchmark claims
- [x] no public weights
- [x] no public GGUF
- [x] Kimari-4B remains not released
- [x] Gate remains BLOCKED

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

## v0.1.30 Checks

- [ ] docs/HF_JOBS_SMOKE_RESULT.md exists
- [ ] docs/HF_JOBS_SMOKE_RUNBOOK.md exists
- [ ] training/scripts/create_hf_jobs_smoke_summary.py exists
- [ ] create_hf_jobs_smoke_summary.py --status pending --json works
- [ ] create_hf_jobs_smoke_summary.py --status completed --json works
- [ ] Summary has training_performed=false
- [ ] Summary has adapter_generated=false
- [ ] Summary has hf_upload_performed=false
- [ ] Summary has gate_state=BLOCKED
- [ ] hf_jobs_status.py has --sanitize-logs flag
- [ ] hf_jobs_status.py sanitizes fake token in logs
- [ ] HF_JOBS_PRIVATE_RUN.md mentions smoke result summary
- [ ] HF_JOBS_PRIVATE_RUN.md mentions log sanitization
- [ ] README mentions HF Jobs smoke test status
- [ ] No raw logs committed
- [ ] training_performed=false in smoke result doc
- [ ] adapter_generated=false in smoke result doc
- [ ] hf_upload_performed=false in smoke result doc
- [ ] Gate still BLOCKED
- [ ] `default_profile` is still "test"
- [ ] No "Kimari-4B released" false claim anywhere

## v0.1.31 Checks

- [ ] docs/HF_JOBS_SMOKE_EXECUTION_RECORD.md exists
- [ ] training/templates/hf_jobs_smoke_execution_record.template.json exists and parses as valid JSON
- [ ] training/scripts/validate_hf_jobs_smoke_summary.py exists and --json works
- [ ] validate_hf_jobs_smoke_summary accepts safe summary
- [ ] validate_hf_jobs_smoke_summary rejects training_performed=true
- [ ] validate_hf_jobs_smoke_summary rejects adapter_generated=true
- [ ] validate_hf_jobs_smoke_summary rejects hf_upload_performed=true
- [ ] validate_hf_jobs_smoke_summary rejects token-like strings
- [ ] hf_jobs_status.py sanitizes stderr when --sanitize-logs
- [ ] hf_jobs_status.py uses --tail flag directly in hf jobs logs
- [ ] Smoke summary says training_performed=false
- [ ] Smoke summary says adapter_generated=false
- [ ] Smoke summary says hf_upload_performed=false
- [ ] Smoke summary says gate_state=BLOCKED
- [ ] Execution record template has gate_state=BLOCKED
- [ ] Execution record template has training_performed=false
- [ ] Execution record template has stderr_sanitized=true
- [ ] No raw logs committed
- [ ] No weights/GGUF/adapters committed
- [ ] HF_JOBS_SMOKE_RUNBOOK.md mentions validate_hf_jobs_smoke_summary
- [ ] HF_JOBS_SMOKE_RUNBOOK.md mentions smoke must pass before micro SFT
- [ ] HF_JOBS_PRIVATE_RUN.md has "Smoke must pass before micro SFT" section
- [ ] HF_JOBS_PRIVATE_RUN.md mentions stderr sanitization
- [ ] HF_JOBS_PRIVATE_RUN.md mentions validate_hf_jobs_smoke_summary
- [ ] Gate still BLOCKED
- [ ] `default_profile` is still "test"
- [ ] No "Kimari-4B released" false claim anywhere

## v0.1.32 Checks

- [ ] docs/HF_JOBS_MICRO_SFT_RUN.md exists
- [ ] docs/HF_JOBS_MICRO_SFT_RESULT.md exists
- [ ] training/configs/hf_jobs_kimari4b_micro_sft.v0.yaml exists
- [ ] training/scripts/hf_jobs_micro_sft.py exists
- [ ] training/scripts/create_hf_jobs_micro_sft_summary.py exists
- [ ] training/scripts/validate_hf_jobs_micro_sft_summary.py exists
- [ ] training/templates/hf_jobs_micro_sft_summary.template.json exists
- [ ] hf_jobs_micro_sft.py --dry-run --json works
- [ ] hf_jobs_micro_sft.py --print-command works
- [ ] Submit requires --allow-submit --yes (blocked without both)
- [ ] hf_jobs_micro_sft.py has no --token argument
- [ ] Micro SFT config has allow_hf_upload=false
- [ ] Micro SFT config has preview_gate_state=BLOCKED
- [ ] create_hf_jobs_micro_sft_summary.py generates safe summary
- [ ] validate_hf_jobs_micro_sft_summary.py rejects hf_upload_performed=true
- [ ] validate_hf_jobs_micro_sft_summary.py rejects adapter_committed=true
- [ ] validate_hf_jobs_micro_sft_summary.py rejects gate_state != BLOCKED
- [ ] No adapter/GGUF/checkpoint/raw logs committed
- [ ] Gate BLOCKED
- [ ] No Kimari-4B released claim
- [ ] default_profile still "test"

## v0.1.33 Checks

- [ ] train_sft_lora.py supports --dataset-path, --eval-dataset-path, --output-dir, --max-steps, --eval-steps, --save-steps, --logging-steps, --per-device-train-batch-size, --gradient-accumulation-steps, --learning-rate, --max-seq-length, --micro-run, --yes
- [ ] `python training/scripts/train_sft_lora.py --show-supported-flags --json` lists all micro SFT flags
- [ ] Real training requires --micro-run --yes (blocked without both)
- [ ] Training blocked when CI=true
- [ ] `python training/scripts/validate_micro_sft_readiness.py --config training/configs/hf_jobs_kimari4b_micro_sft.v0.yaml --json` works and returns ready: true
- [ ] train_sft_lora.py has no --token argument
- [ ] run_sft_training exists in train_sft_lora.py
- [ ] apply_cli_overrides exists in train_sft_lora.py
- [ ] push_to_hub is never true (always false in training args)
- [ ] report_to is "none" in training args
- [ ] docs/MICRO_SFT_IMPLEMENTATION.md exists
- [ ] training/configs/hf_jobs_kimari4b_micro_sft.v0.yaml command includes --micro-run --yes
- [ ] No adapter/GGUF/checkpoint/raw logs committed
- [ ] Gate BLOCKED
- [ ] No Kimari-4B released claim
- [ ] default_profile still "test"

## v0.1.34 Checks

- [ ] training/scripts/check_training_stack.py exists and --json works without downloading models
- [ ] train_sft_lora.py has build_training_arguments function
- [ ] train_sft_lora.py has build_sft_trainer function
- [ ] train_sft_lora.py has prepare_sft_dataset function
- [ ] max_seq_length is NOT passed to TrainingArguments in train_sft_lora.py
- [ ] max_seq_length IS passed to SFTTrainer (via build_sft_trainer) when supported
- [ ] docs/TRAINING_STACK_COMPATIBILITY.md exists
- [ ] HF Jobs config includes check_training_stack.py command before training
- [ ] validate_micro_sft_readiness.py checks for check_training_stack.py in commands
- [ ] validate_micro_sft_readiness.py checks no hf upload in commands
- [ ] prepare_sft_dataset handles messages column
- [ ] prepare_sft_dataset handles text column
- [ ] build_training_arguments uses eval_strategy/evaluation_strategy fallback
- [ ] build_sft_trainer supports tokenizer and processing_class
- [ ] No adapter/GGUF/checkpoint/raw logs committed
- [ ] Gate BLOCKED
- [ ] No Kimari-4B released claim
- [ ] default_profile still "test"

## v0.1.35 Checks

- [ ] docs/HF_JOBS_MICRO_SFT_EXECUTION_RECORD.md exists
- [ ] training/scripts/create_micro_sft_execution_record.py works with --json
- [ ] training/scripts/validate_micro_sft_execution_record.py works with --json
- [ ] hf_jobs_micro_sft.py has --require-smoke-summary flag
- [ ] Submit blocked without --require-smoke-summary (unless --override-smoke-gate)
- [ ] docs/HF_JOBS_MICRO_SFT_RUNBOOK.md exists
- [ ] create_micro_sft_execution_record always sets adapter_committed=false
- [ ] create_micro_sft_execution_record always sets hf_upload_performed=false
- [ ] create_micro_sft_execution_record always sets gate_state=BLOCKED
- [ ] validate_micro_sft_execution_record rejects gate != BLOCKED
- [ ] validate_micro_sft_execution_record rejects adapter_committed=true
- [ ] validate_micro_sft_execution_record rejects hf_upload_performed=true
- [ ] validate_micro_sft_execution_record rejects raw_logs_committed=true
- [ ] No adapter/GGUF/checkpoint/raw logs committed
- [ ] Gate BLOCKED
- [ ] No Kimari-4B released claim
- [ ] default_profile still "test"

## v0.1.36 Checks

- [ ] resolve_smoke_gate function exists in hf_jobs_micro_sft.py
- [ ] Explicit smoke summary path has priority over default /tmp
- [ ] Default /tmp fallback is documented
- [ ] Override documented with warning
- [ ] Submit uses one smoke gate path (no duplicate)
- [ ] hf_jobs_micro_sft.py JSON output includes smoke_gate_source
- [ ] hf_jobs_micro_sft.py JSON output includes smoke_gate_validated
- [ ] hf_jobs_micro_sft.py JSON output includes smoke_gate_message
- [ ] hf_jobs_micro_sft.py JSON output includes smoke_summary_path
- [ ] docs/HF_JOBS_SMOKE_GATE.md exists
- [ ] docs/HF_JOBS_MICRO_SFT_RUNBOOK.md mentions --require-smoke-summary with explicit path
- [ ] No duplicate final smoke gate logic in hf_jobs_micro_sft.py
- [ ] check_smoke_summary_validated is NOT called in submit path
- [ ] Gate BLOCKED
- [ ] No Kimari-4B released claim
- [ ] default_profile still "test"

## v0.1.37 Checks

- [ ] validate_config() does not crash with UnboundLocalError when jsonschema is missing
- [ ] validate_config() returns clear error message when jsonschema is not installed
- [ ] check_gpu_compute_capability() exists in kimari/doctor/deep.py
- [ ] check_gpu_compute_capability() is in run_deep_checks() results
- [ ] check_gpu_arch_compatibility() exists in training/scripts/check_training_stack.py
- [ ] check_gpu_arch_compatibility() is in run_all_checks() results (check #15)
- [ ] GPU arch warning extracted to warnings list in check_training_stack
- [ ] docs/INSTALL_WSL2.md mentions Pascal/cu126/sm_61
- [ ] docs/INSTALL_MATRIX.md mentions Pascal/cu126/sm_61
- [ ] docs/TRAINING_STACK_COMPATIBILITY.md mentions Pascal/cu126/sm_61
- [ ] tests/test_release_v0137.py exists and passes
- [ ] pyproject.toml version is 0.1.37-alpha
- [ ] kimari/__init__.py __version__ is 0.1.37-alpha
- [ ] CHANGELOG.md has [0.1.37-alpha] entry
- [ ] ROADMAP.md marks v0.1.37-alpha as Current, v0.1.36-alpha as Released
- [ ] No adapter/GGUF/checkpoint/raw logs committed
- [ ] Gate BLOCKED
- [ ] No Kimari-4B released claim
- [ ] default_profile still "test"

## v0.1.38 Checks

- [ ] Setup writer never starts from `{}` (uses `load_base_config_for_setup()`)
- [ ] Config has `version` after `kimari setup --write`
- [ ] Config has `profiles` after `kimari setup --write`
- [ ] Config has `default_profile` after `kimari setup --write`
- [ ] `default_profile` exists in `profiles` after `kimari setup --write`
- [ ] `kimari setup --write --yes --reset-user-config` regenerates config from packaged defaults
- [ ] `--reset-user-config` creates backup before overwriting
- [ ] `is_config_complete()` returns `false` for config missing `version`
- [ ] `is_config_complete()` returns `false` for config missing `profiles`
- [ ] `is_config_complete()` returns `false` for config missing `default_profile`
- [ ] `is_config_complete()` returns `true` for complete config
- [ ] `resolve_recommended_profile()` returns safe fallback when recommended profile doesn't exist
- [ ] `kimari setup --json` includes `resolved_profile` field
- [ ] `kimari setup --json` includes `user_config_complete` field
- [ ] `kimari setup --json` includes `recovery_needed` field
- [ ] `kimari setup --json` includes `config_would_be_valid` field
- [ ] `kimari doctor --deep` detects incomplete user config
- [ ] `kimari doctor --deep` suggests recovery command for incomplete config
- [ ] Incomplete user config recovery documented in README
- [ ] Incomplete user config recovery documented in INSTALL_WSL2.md
- [ ] Gate BLOCKED
- [ ] No Kimari-4B released claim
- [ ] default_profile still "test"

## v0.1.39 Checks

- [ ] `merge_user_config_onto_defaults_safely()` function exists in `kimari/setup/writer.py`
- [ ] `_PROTECTED_FIELDS` constant includes `version`, `config_version`, `profiles`, `server`
- [ ] `_SAFE_USER_FIELDS` constant includes `setup_info`, `integrations`, `paths`
- [ ] Recovery merge does NOT use `_base.update(config)` pattern
- [ ] Incomplete user config with `profiles: {}` does NOT overwrite defaults profiles
- [ ] Incomplete user config with wrong `version` does NOT overwrite defaults version
- [ ] Incomplete user config with wrong `config_version` does NOT overwrite defaults
- [ ] Incomplete user config with wrong `server` does NOT overwrite defaults server
- [ ] Invalid `default_profile` from incomplete user config is rejected (keeps defaults value)
- [ ] Valid `default_profile` from incomplete user config is accepted if it exists in defaults profiles
- [ ] Safe user fields (`setup_info`, `integrations`, `paths`) are preserved from user config
- [ ] `write_setup_config()` uses `merge_user_config_onto_defaults_safely()` for recovery
- [ ] `apply_setup_changes()` uses `merge_user_config_onto_defaults_safely()` for recovery
- [ ] `tests/test_release_v0139.py` exists and passes
- [ ] pyproject.toml version is 0.1.39-alpha
- [ ] kimari/__init__.py __version__ is 0.1.39-alpha
- [ ] CHANGELOG.md has [0.1.39-alpha] entry
- [ ] ROADMAP.md marks v0.1.39-alpha as Current, v0.1.38-alpha as Released
- [ ] No adapter/GGUF/checkpoint/raw logs committed
- [ ] Gate BLOCKED
- [ ] No Kimari-4B released claim
- [ ] default_profile still "test"

## v0.1.40 Checks

- [ ] `docs/GTX1060_LOCAL_RUNTIME_RESULT.md` exists
- [ ] `benchmarks/results/gtx1060-tinyllama-wsl2.example.json` exists and parses as valid JSON
- [ ] Benchmark JSON has `kimari4b: false`
- [ ] Benchmark JSON has `result_type: local_runtime_validation`
- [ ] Benchmark JSON has `measured: true`
- [ ] Benchmark JSON has `public_claim_allowed: limited`
- [ ] GTX1060 result doc mentions TinyLlama (NOT Kimari-4B)
- [ ] No "Kimari-4B benchmark" claim in GTX1060 result doc
- [ ] `detect_compute_capability_from_llama_server()` exists in `kimari/core/detection.py`
- [ ] `detect_cuda_version_detailed()` exists in `kimari/core/detection.py`
- [ ] `doctor --deep` compute capability fallback uses llama-server when PyTorch unavailable
- [ ] `detect_cuda_version()` falls back to nvidia-smi header parsing
- [ ] `check_training_stack.py` has `check_gpu_cuda_info()` function
- [ ] `check_gpu_cuda_info()` works without PyTorch installed
- [ ] README includes "Validated Locally on GTX 1060" section
- [ ] README CUDA vs CPU-only comparison table present
- [ ] README says NOT Kimari-4B in GTX 1060 section
- [ ] docs/index.html has GTX 1060 validation card
- [ ] docs/SCREENSHOTS.md has GTX 1060 recommended captures section
- [ ] pyproject.toml version is 0.1.40-alpha
- [ ] kimari/__init__.py __version__ is 0.1.40-alpha
- [ ] CHANGELOG.md has [0.1.40-alpha] entry
- [ ] ROADMAP.md marks v0.1.40-alpha as Current, v0.1.39-alpha as Released
- [ ] No adapter/GGUF/checkpoint/raw logs committed
- [ ] Gate BLOCKED
- [ ] No "Kimari-4B released" false claim anywhere
- [ ] default_profile still "test"

## v0.1.53 Checks

- [ ] eval config exists (YAML with safety flags)
- [ ] eval config safety flags all false/correct
- [ ] HF eval runner exists (dry-run default)
- [ ] HF eval runner requires --allow-submit --yes
- [ ] HF eval runner has no --token arg
- [ ] HF eval runner has no shell=True
- [ ] compare script exists
- [ ] summary validator exists
- [ ] summary template exists
- [ ] pending report placeholder exists
- [ ] summary validator enforces no raw outputs
- [ ] no raw eval outputs committed
- [ ] no safetensors in public repo
- [ ] no GGUF in public repo
- [ ] Gate BLOCKED

## v0.1.53 HF Sync Checks

- [ ] docs/HUGGINGFACE_ORG_CARD.md version matches pyproject.toml
- [ ] docs/HUGGINGFACE_ORG_CARD.md does not contain v0.1.28-alpha
- [ ] docs/HUGGINGFACE_ORG_CARD.md mentions Kimari-4B not released
- [ ] docs/HUGGINGFACE_ORG_CARD.md mentions gate BLOCKED
- [ ] docs/HUGGINGFACE_DEPLOYMENT_STATUS.md has current version
- [ ] README.md links HF Space
- [ ] README.md says Kimari-4B not released
- [ ] no "Kimari-4B released" in any doc
- [ ] no public adapter/GGUF claim
- [ ] HF Space README mentions version and not released
- [ ] docs/index.html has KimariEval card

## v0.1.52 Checks

- [ ] eval private dataset exists (7 categories, 100+ cases)
- [ ] eval validator exists and passes
- [ ] eval harness exists (dry-run + endpoint)
- [ ] eval schema exists
- [ ] baseline plan exists
- [ ] score_status = not_scored in dry-run output
- [ ] manual_review_required = true
- [ ] no_benchmark_claim = true
- [ ] no invented scores
- [ ] no safetensors in public repo
- [ ] no GGUF in public repo
- [ ] Gate BLOCKED

## v0.1.51 Checks

- [ ] Persisted config exists
- [ ] Private adapter repo documented
- [ ] Runner dry-run default, requires --allow-submit --yes
- [ ] No --token arg in runner
- [ ] No shell=True in runner
- [ ] No command string split in runner
- [ ] Summary template exists
- [ ] Summary creator exists
- [ ] Summary validator exists
- [ ] adapter_committed_public false in summary
- [ ] hf_public_upload_performed false in summary
- [ ] gguf_generated false in summary
- [ ] gate_state BLOCKED in summary
- [ ] Load check script exists
- [ ] Private repo policy doc exists
- [ ] No safetensors in public repo
- [ ] No GGUF in public repo (excl deps)
- [ ] Gate BLOCKED

## v0.1.50 Checks

- [ ] Dataset hash script exists (hash_dataset.py)
- [ ] No contradictory dataset hashes between config and summary
- [ ] KIMARI4B_MICRO_SFT_RESULT_REVIEW.md exists
- [ ] KIMARI4B_ADAPTER_PERSISTENCE_STRATEGY.md exists
- [ ] PRIVATE_ARTIFACT_REPO_POLICY.md exists
- [ ] package_private_adapter.py defaults to dry-run
- [ ] validate_private_artifact_repo.py exists
- [ ] KIMARI4B_NEXT_RUN_PLAN.md exists
- [ ] No *.safetensors tracked in public repo
- [ ] No *.gguf tracked in public repo
- [ ] Gate BLOCKED

## v0.1.49 Checks

- [ ] Micro SFT dataset exists (sft_micro.jsonl)
- [ ] Micro SFT dataset report valid (no private data, no tokens)
- [ ] Micro SFT config exists with safety flags false
- [ ] HF Jobs micro SFT runner exists
- [ ] Runner dry-run default, requires --allow-submit --yes
- [ ] Micro SFT result doc exists
- [ ] training_performed field exists
- [ ] adapter_committed false
- [ ] hf_upload_performed false
- [ ] gguf_generated false
- [ ] No raw logs committed
- [ ] Gate BLOCKED

## v0.1.48 Checks

- [ ] `docs/HF_JOBS_SMOKE_REAL_RESULT.md` exists
- [ ] `training/results/hf_jobs_smoke_summary.json` exists and is sanitized
- [ ] Smoke summary training_performed=false
- [ ] Smoke summary adapter_generated=false
- [ ] Smoke summary hf_upload_performed=false
- [ ] No raw logs committed
- [ ] Gate BLOCKED

## v0.1.47 Checks

- [ ] Private adapter config exists with safety flags
- [ ] Runner dry-run default, requires --allow-train --yes
- [ ] Preflight script exists
- [ ] Adapter manifest template exists
- [ ] Manifest creator script exists
- [ ] Eval plan exists
- [ ] Eval script exists
- [ ] Release gate doc exists
- [ ] .gitignore protects artifacts
- [ ] No adapter/GGUF/safetensors committed
- [ ] No push_to_hub in config
- [ ] Gate BLOCKED

## v0.1.46 Checks

- [x] `docs/PUBLIC_LAUNCH_PACK.md` exists
- [x] `docs/POST_X_KIMARI_GTX1060.md` exists
- [x] `docs/REDDIT_POST_KIMARI.md` exists
- [x] `docs/HUGGINGFACE_COMMUNITY_POST.md` exists
- [x] Collection seed exists (`huggingface/collections/`)
- [x] Collection seed validator exists
- [x] All seed entries `official_kimari_model=false`
- [x] No Kimari-4B release claims in posts
- [x] No fake benchmarks in posts
- [x] Screenshots manifest safe (no real captures if not reviewed)
- [x] Gate BLOCKED

## v0.1.45 Checks

- [x] `docs/HUGGINGFACE_DEPLOYMENT_STATUS.md` exists
- [x] README links to Hugging Face Space
- [x] README says Kimari-4B not released
- [x] Collection doc says reference/community models, not official
- [x] No billing/plan mentions in docs
- [x] No tokens in docs
- [x] No model weights uploaded
- [x] Gate BLOCKED
- [x] No HF Jobs executed
- [x] No training performed

## v0.1.44 Checks

- [x] `docs/GTX1060_SHOWCASE.md` exists
- [x] `docs/assets/screenshots/gtx1060-wsl2/manifest.example.json` exists
- [x] `scripts/docs/validate_screenshot_manifest.py` exists
- [x] `huggingface/kimari-fit-lab/app.py` exists
- [x] `huggingface/kimari-fit-lab/README.md` exists
- [x] `docs/HUGGINGFACE_SPACE_KIMARI_FIT_LAB.md` exists
- [x] `docs/HUGGINGFACE_ORG_CARD.md` exists
- [x] README mentions GTX 1060 local validation
- [x] README says Kimari-4B not released
- [x] No screenshots with tokens or private paths
- [x] No fake benchmarks
- [x] Gate BLOCKED
- [x] No HF upload
- [x] No training

## v0.1.43 Checks

- [x] `docs/LOCAL_INTEGRATION_VALIDATION.md` exists
- [x] `docs/OPENWEBUI_LOCAL_SETUP.md` exists
- [x] `docs/OPENCLAW_LOCAL_SETUP.md` exists
- [x] `docs/CONTINUE_LOCAL_SETUP.md` exists
- [x] `docs/LOCAL_SHOWCASE_CHECKLIST.md` exists
- [x] `scripts/integrations/validate_local_openai_endpoint.py` exists
- [x] No API key values in any integration doc
- [x] `kimari integrations generate --all --json` outputs open-webui/openclaw/continue/hermes configs
- [x] `kimari integrations validate` supports --json output
- [x] README mentions local integrations (Open WebUI, OpenClaw, Continue.dev)
- [x] README/docs do not claim Kimari-4B is released
- [x] pyproject.toml version >= 0.1.43-alpha
- [x] kimari/__init__.py __version__ >= 0.1.43-alpha
- [x] CHANGELOG.md has [0.1.43-alpha] entry
- [x] ROADMAP.md mentions v0.1.43-alpha
- [x] Gate BLOCKED
- [x] No HF upload performed
- [x] No training performed

## v0.1.42 Checks

- [x] `build_hf_jobs_command_args()` exists in `hf_jobs_private_run.py`
- [x] `hf_cmd.split()` not used in submit path
- [x] `shell=True` not used in `hf_jobs_private_run.py`
- [x] Submit uses `subprocess.run(hf_cmd_args, ...)` (arg list, not string)
- [x] `--dry-run --json` includes `hf_jobs_command_args` and `command_arg_count`
- [x] `check-release.py` has no false version hardcode FAIL
- [x] `docs/LOCAL_OPENAI_ENDPOINT_TEST.md` exists
- [x] README mentions `profile test` for TinyLlama validation model
- [x] README/docs do not claim Kimari-4B is released
- [x] Doctor/status suggests `--profile test` when default model missing
- [x] pyproject.toml version >= 0.1.42-alpha
- [x] kimari/__init__.py __version__ >= 0.1.42-alpha
- [x] CHANGELOG.md has [0.1.42-alpha] entry
- [x] ROADMAP.md mentions v0.1.42-alpha
- [x] No adapter/GGUF/checkpoint/raw logs committed
- [x] Gate BLOCKED
- [x] No HF upload performed
- [x] No training performed
- [x] No "Kimari-4B released" false claim anywhere
- [x] default_profile still "test"

## v0.1.41 Checks

- [x] `docs/HF_JOBS_ACCESS.md` exists
- [x] `docs/HF_JOBS_FALLBACK_RUNNERS.md` exists
- [x] `training/scripts/check_hf_jobs_access.py` exists
- [x] `check_hf_jobs_access.py` handles 403 Forbidden safely
- [x] `check_hf_jobs_access.py` returns `can_continue_to_smoke` field
- [x] `check_hf_jobs_access.py` does not expose tokens or billing info
- [x] `hf_jobs_private_run.py` supports `--require-jobs-access`
- [x] `--require-jobs-access` does NOT block `--dry-run` or `--print-command`
- [x] Benchmark `*.example.json` false positive fixed in check-release
- [x] `benchmarks/results/gtx1060-tinyllama-wsl2.example.json` not flagged as real result
- [x] No "Pro subscription active" in any committed file
- [x] No "Smouj013 has Pro" in any committed file
- [x] No "billing active" or "paid account" in any committed file
- [x] docs mention generic HF Jobs access only (no private plan details)
- [x] README includes HF Jobs smoke test access note
- [x] pyproject.toml version >= 0.1.41-alpha
- [x] kimari/__init__.py __version__ >= 0.1.41-alpha
- [x] CHANGELOG.md has [0.1.41-alpha] entry
- [x] ROADMAP.md mentions v0.1.41-alpha
- [x] No adapter/GGUF/checkpoint/raw logs committed
- [x] Gate BLOCKED
- [x] No "Kimari-4B released" false claim anywhere
- [x] default_profile still "test"

## Post-Release

- [ ] GitHub topics still accurate (20 topics, lowercase, hyphens)
- [ ] `docs/index.html` live site reflects new version
- [ ] ROADMAP.md next version entry created
- [ ] TestPyPI validation result recorded (if attempted)
- [ ] GitHub release tag pushed

## v0.1.63 Checks

- [x] SFT v1 micro-run completed (Job 6a0501dae48bea4538b9c17a)
- [x] Result summary JSON validated
- [x] Result doc COMPLETED (not PENDING)
- [x] training_performed=true in summary
- [x] adapter_generated=true in summary
- [x] adapter_committed=false
- [x] hf_public_upload_performed=false
- [x] gguf_generated=false
- [x] gate_state=BLOCKED
- [x] HF Jobs command syntax fixed (positional IMAGE, bash -c, git clone, --micro-run --yes)
- [x] Config: dataset_path/eval_dataset_path (not dataset_train)
- [x] Dataset build files tracked in git
- [x] pyproject.toml version = 0.1.63-alpha
- [x] kimari/__init__.py __version__ = 0.1.63-alpha
- [x] No adapter/GGUF/checkpoint/raw logs committed
- [x] Gate BLOCKED
- [x] No "Kimari-4B released" false claim anywhere

## v0.1.64 Checks

- [x] check-release.py v0.1.62 checks conditional on result doc status
- [x] check-release clean (0 FAIL)
- [x] SFT v1 result doc says COMPLETED
- [x] SFT v1 result doc says 10 steps (micro-run, not final model)
- [x] SFT v1 result doc says no public benchmark
- [x] Run history updated with micro-run entry
- [x] Eval subset10 config exists
- [x] Eval readiness validator passes
- [x] Eval plan doc exists
- [x] No training executed, no HF Jobs submitted
- [x] No public weights/GGUF
- [x] No benchmark público
- [x] Gate BLOCKED
- [x] pyproject.toml version = 0.1.64-alpha
- [x] kimari/__init__.py __version__ = 0.1.64-alpha

## v0.1.65 Checks

- [x] Eval subset10 infrastructure: load checker, eval runner, summary template/validator
- [x] Adapter load checker dry-run passes
- [x] Eval runner dry-run passes
- [x] Summary validator passes
- [x] Eval result doc exists (PENDING status)
- [x] Report directory + summary exists
- [x] check-release.py v0.1.65 checks
- [x] tests/test_release_v0165.py
- [x] No training executed, no HF Jobs submitted
- [x] No public weights/GGUF
- [x] Gate BLOCKED

## v0.1.66 Checks

- [x] SFT v1 eval subset10 — BLOCKED on adapter availability
- [x] Adapter from micro-run NOT persisted (adapter_committed=false)
- [x] Eval result doc documents blocker
- [x] Eval plan documents blocker
- [x] Report summary has status=blocked, ready_for_subset30=false
- [x] Load checker exists (dry-run only)
- [x] Eval runner exists (dry-run only)
- [x] Summary validator passes
- [x] check-release.py v0.1.66 checks
- [x] tests/test_release_v0166.py
- [x] No training executed
- [x] No public weights/GGUF
- [x] Gate BLOCKED
- [x] ready_for_subset30=false
