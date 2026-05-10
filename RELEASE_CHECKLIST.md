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

## Post-Release

- [ ] GitHub topics still accurate (20 topics, lowercase, hyphens)
- [ ] `docs/index.html` live site reflects new version
- [ ] ROADMAP.md next version entry created
- [ ] TestPyPI validation result recorded (if attempted)
- [ ] GitHub release tag pushed
