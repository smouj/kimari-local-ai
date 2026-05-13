# Changelog

All notable changes to Kimari Local AI will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).
## [0.1.54-alpha] - 2026-05-13

### Added
- `eval/configs/kimari_eval_v1_baseline_vs_adapter_subset10.yaml` — subset10 eval config
- `reports/evals/kimari_v0154_baseline_vs_adapter_subset10/` — results directory
- `docs/KIMARI_EVAL_V0154_RESULT.md` — eval result documentation
- Real baseline vs adapter evaluation on HF Jobs (subset_size=10)
- Version bump: 0.1.53-alpha → 0.1.54-alpha

### Note
- No training executed
- No raw eval outputs committed
- No public benchmark claims
- Gate: BLOCKED

## [0.1.53-alpha] - 2026-05-13

### Added
- `eval/configs/kimari_eval_v1_baseline_vs_adapter.yaml` — eval config for baseline vs adapter comparison
- `eval/scripts/hf_jobs_run_kimari_eval.py` — HF Jobs eval runner (dry-run default, safe flags)
- `eval/scripts/compare_kimari_eval_runs.py` — compare baseline vs adapter summaries
- `eval/scripts/validate_kimari_eval_summary.py` — summary validator
- `eval/templates/kimari_eval_summary.template.json` — summary schema
- `docs/KIMARI_EVAL_BASELINE_VS_ADAPTER_RUN.md` — run documentation
- `docs/KIMARI_EVAL_REVIEW_PROTOCOL.md` — manual review protocol
- `reports/evals/kimari_v0153_baseline_vs_adapter/` — result placeholders
- Version bump: 0.1.52-alpha → 0.1.53-alpha

### Note
- No training executed in this version
- No HF Jobs submitted (eval infrastructure only)
- No adapter or GGUF generated
- Eval results are pending — no benchmark claims
- Gate: BLOCKED


## [0.1.49-alpha] - 2026-05-13
## [0.1.52-alpha] - 2026-05-13

### Added
- `eval/kimari_private_v1/` — 104 eval cases across 7 categories (Spanish technical, coding, server ops, local LLM/GGUF, agents, refusal/safety, style)
- `eval/schema/kimari_eval_item.schema.json` — JSON Schema for eval items
- `eval/scripts/validate_kimari_eval.py` — dataset validator
- `eval/scripts/run_kimari_eval.py` — eval harness (dry-run + endpoint modes)
- `docs/KIMARI_EVAL_PRIVATE_V1.md` — eval documentation
- `docs/KIMARIFIT_SCORE_PLAN.md` — scoring framework (experimental)
- `docs/BASELINE_VS_ADAPTER_EVAL_PLAN.md` — comparison plan
- `reports/evals/baseline_qwen25_15b/README.md` — baseline plan
- `reports/evals/baseline_qwen25_15b/baseline_plan.json` — baseline config
- Version bump: 0.1.51-alpha → 0.1.52-alpha

### Note
- No training executed in this version
- No HF Jobs submitted
- No adapter or GGUF generated
- Eval dataset is private, for internal use only
- No benchmark claims
- Gate: BLOCKED

## [0.1.51-alpha] - 2026-05-13

### Added
- `training/configs/hf_jobs_kimari4b_micro_sft_persisted.v0.yaml` — persisted micro SFT config
- `training/scripts/hf_jobs_micro_sft_persisted.py` — HF Jobs runner with private repo upload
- `training/scripts/run_micro_sft_persisted_uv.py` — UV-compatible training script (PEP 723)
- `training/scripts/check_private_adapter_load.py` — adapter load check script
- `training/scripts/create_hf_jobs_micro_sft_persisted_summary.py` — summary creator
- `training/scripts/validate_hf_jobs_micro_sft_persisted_summary.py` — summary validator
- `training/templates/hf_jobs_micro_sft_persisted_summary.template.json` — summary template
- `docs/KIMARI4B_PRIVATE_ADAPTER_REPO.md` — private repo policy
- `docs/KIMARI4B_MICRO_SFT_PERSISTED_RUN.md` — run documentation
- `docs/KIMARI4B_PRIVATE_ADAPTER_LOAD_CHECK.md` — load check docs
- `docs/KIMARI4B_MICRO_SFT_PERSISTED_RESULT.md` — result doc
- `docs/KIMARI4B_MICRO_SFT_PERSISTED_RESULT_SUMMARY.json` — result summary
- Private HF repo `Smouj013/kimari4b-micro-sft-adapter-v0` created and adapter uploaded
- Version bump: 0.1.50-alpha → 0.1.51-alpha

### Deployed
- **Job 6a03a25e72518a06598ffae0 — COMPLETED ✅**
- GPU: NVIDIA A10G, 22.3 GB
- Base model: Qwen/Qwen2.5-1.5B-Instruct
- PyTorch: 2.11.0+cu130, transformers: 5.8.0, peft: 0.19.1, trl: 1.4.0
- Training: 20 steps, loss 5.005 → 4.228
- **adapter_persisted_private: true** (uploaded to private HF repo)
- **adapter_load_check: true** (adapter loads and generates text)
- **generation_success: true**
- adapter_hash: 26a8190dab52f816157da467369ae88f
- adapter_size: 4,372,840 bytes
- Estimated cost: ~$0.50

### Safety
- Gate remains BLOCKED
- adapter_committed_public: false
- hf_public_upload_performed: false
- gguf_generated: false
- No raw logs committed
- No tokens
- No billing info

## [0.1.50-alpha] - 2026-05-13

### Added
- `training/scripts/hash_dataset.py` — compute file and normalized SHA256 for dataset files
- `training/scripts/package_private_adapter.py` — package adapter artifacts for private repo
- `training/scripts/validate_private_artifact_repo.py` — validate private repo structure
- `docs/KIMARI4B_MICRO_SFT_RESULT_REVIEW.md` — post-run review
- `docs/KIMARI4B_ADAPTER_PERSISTENCE_STRATEGY.md` — adapter persistence strategy
- `docs/PRIVATE_ARTIFACT_REPO_POLICY.md` — private repo policy
- `docs/KIMARI4B_NEXT_RUN_PLAN.md` — next run plan with adapter retrieval
- Dataset hash inconsistency fixed (config now uses `f8ce140b...` matching actual file)
- `docs/KIMARI4B_MICRO_SFT_RESULT_SUMMARY.json` — updated with explicit `dataset_file_sha256` and `dataset_normalized_sha256` fields
- Private repo created: `smouj/kimari-4b-artifacts` (private, Git LFS for safetensors)

### Changed
- Version bump: 0.1.49-alpha → 0.1.50-alpha
- README badge updated to v0.1.50-alpha
- docs/index.html version updated to v0.1.50-alpha

### Safety
- Gate remains BLOCKED
- No adapter committed
- No HF upload
- No GGUF
- No public weights


### Added
- `dataset/build/kimari-fit-v0/sft_micro.jsonl` — 72 curated examples (Spanish technical, CUDA, Linux, Python, Kimari API)
- `dataset/build/kimari-fit-v0/report.json` — dataset report (hash, count, categories)
- `docs/KIMARI4B_MICRO_SFT_DATASET.md` — dataset documentation
- `training/configs/hf_jobs_kimari4b_micro_sft_real.v0.yaml` — micro SFT config (a10g-small, 20min, LoRA r=8)
- `training/scripts/hf_jobs_micro_sft_real.py` — HF Jobs micro SFT wrapper (dry-run default, --allow-submit --yes required)
- `training/templates/hf_jobs_micro_sft_real_summary.template.json` — summary template
- `training/scripts/create_hf_jobs_micro_sft_real_summary.py` — summary creator
- `training/scripts/validate_hf_jobs_micro_sft_real_summary.py` — summary validator
- `docs/HF_JOBS_MICRO_SFT_REAL_RUN.md` — real run documentation
- `docs/KIMARI4B_MICRO_SFT_RESULT.md` — result doc (COMPLETED)
- `docs/KIMARI4B_MICRO_SFT_RESULT_SUMMARY.json` — sanitized result summary
- check-release.py v0.1.49 checks (22/22 pass)
- tests/test_release_v0149.py (17 tests)

### Deployed
- HF Jobs micro SFT: **Job 6a038ec87618f125ee2b7984 — COMPLETED**
- Flavor: a10g-small (NVIDIA A10G, 22.3 GB VRAM, CUDA 12.4)
- Base model: Qwen/Qwen2.5-1.5B-Instruct (Apache 2.0)
- Docker: pytorch/pytorch:2.5.1-cuda12.4-cudnn9-devel
- Dataset: kimari-fit-v0 (72 examples)
- Loss: 2.62 (step 0) → 3.19 (step 5)
- Estimated cost: ~$0.35
- 4 failed attempts before success (PyTorch/transformers version incompatibilities)

### Safety
- Gate remains BLOCKED
- training_performed: true, adapter_generated: true
- adapter_committed: false, hf_upload_performed: false
- No GGUF generated, no push_to_hub
- No raw logs committed, no tokens, no billing info

## [0.1.48-alpha] - 2026-05-12

### Added
- `docs/HF_JOBS_SMOKE_REAL_RESULT.md` — real smoke test results (GPU detected, no training)
- `training/configs/hf_jobs_kimari4b_smoke.v0.yaml` — HF Jobs smoke config (a10g-small, 5min timeout)
- `training/scripts/check_hf_jobs_access.py` — access gate checker
- `training/scripts/hf_jobs_private_run.py` — HF Jobs runner (--allow-submit --yes required)
- `training/scripts/hf_jobs_status.py` — job status and sanitized logs
- `training/scripts/create_hf_jobs_smoke_summary.py` — sanitized summary creator
- `training/scripts/validate_hf_jobs_smoke_summary.py` — summary validator
- `training/results/hf_jobs_smoke_summary.json` — sanitized smoke result
- check-release.py v0.1.48 checks (smoke result, training=false, adapter=false)
- tests/test_release_v0148.py

### Deployed
- HF Jobs smoke: `6a036dd772518a06598ff86f` (python:3.12-slim, COMPLETED)
- HF Jobs smoke: `6a036f1a7618f125ee2b78f2` (pytorch:2.1.0-cuda12.1, COMPLETED)
- GPU detected: NVIDIA A10G, 22.3 GB VRAM, CUDA 12.1
- Cost: ~$0.05 total

### Safety
- Gate remains BLOCKED
- No training performed
- No adapter generated
- No GGUF exported
- No HF upload
- No raw logs committed
- No billing/plan info in docs

## [0.1.47-alpha] - 2026-05-12

### Added
- `docs/KIMARI4B_FIRST_PRIVATE_ADAPTER_RUN.md` — first private adapter run documentation
- `training/configs/kimari4b_private_adapter_run.v0.yaml` — private adapter run config
- `training/scripts/run_kimari4b_private_adapter.py` — adapter runner (dry-run default, --allow-train --yes required)
- `training/scripts/preflight_kimari4b_adapter.py` — preflight checks (config, dataset, CUDA, gitignore, gate)
- `training/templates/kimari4b_adapter_manifest.template.json` — adapter artifact manifest template
- `training/scripts/create_kimari4b_adapter_manifest.py` — manifest creator (hashes, no private paths)
- `eval/scripts/evaluate_kimari4b_adapter.py` — eval script (baseline vs adapter, dry-run default)
- `docs/KIMARI4B_ADAPTER_EVAL_PLAN.md` — eval plan (KimariFit, safety, Spanish, coding)
- `docs/KIMARI4B_RELEASE_GATE.md` — gate states (BLOCKED → PRIVATE_ADAPTER_READY → ... → PUBLIC_PREVIEW_ALLOWED)
- README "Kimari-4B private adapter work" section
- docs/index.html "Kimari-4B private adapter pipeline" card
- `.gitignore` hardened (adapters, safetensors, gguf, checkpoints, wandb, runs, raw_eval)
- check-release.py v0.1.47 checks (safety flags, no push_to_hub, no artifacts tracked)
- tests/test_release_v0147.py

### Safety
- Gate remains BLOCKED — no automatic gate transitions
- No adapter/GGUF/safetensors committed or uploaded
- No HF upload, no push_to_hub
- Runner defaults to dry-run, requires --allow-train --yes for real training
- All configs: hf_upload_allowed=false, public_release_allowed=false, gguf_export_allowed=false
- Preflight verifies: gitignore, no HF upload, gate BLOCKED
- Kimari-4B still "not released"

## [0.1.46-alpha] - 2026-05-12

### Added
- `docs/COLLECTION_SEED_PLAN.md` — proposed reference GGUF models for Collection
- `huggingface/collections/kimari-compatible-gguf.seed.example.json` — 5 entry seed example
- `scripts/huggingface/validate_collection_seed.py` — seed validator with `--input` and `--json`
- `docs/PUBLIC_LAUNCH_PACK.md` — consolidated launch material for X/Reddit/HF/GitHub
- `docs/POST_X_KIMARI_GTX1060.md` — X posts in English/Spanish, short/technical/thread
- `docs/REDDIT_POST_KIMARI.md` — Reddit posts, humble and technical versions
- `docs/HUGGINGFACE_COMMUNITY_POST.md` — HF community announce post
- `docs/GTX1060_SHOWCASE.md` updated with public screenshot status section
- README "Public showcase" section with links
- docs/index.html "Public launch pack ready" card
- check-release.py v0.1.46 checks (launch pack, collection seed, no official_kimari_model)
- tests/test_release_v0146.py

### Safety
- Gate remains BLOCKED
- No HF upload of weights, adapters, or GGUF files
- No training performed
- No HF Jobs executed
- No tokens or private data in any file
- No Kimari-4B release claims
- All collection seed entries: official_kimari_model=false
- Screenshots: no real screenshots committed (only manifest template)

## [0.1.45-alpha] - 2026-05-12

### Added
- `docs/HUGGINGFACE_DEPLOYMENT_STATUS.md` — HF deployment documentation with URLs and status
- `docs/HUGGINGFACE_COLLECTIONS.md` — collection guide for reference GGUF models
- `docs/SOCIAL_PROOF_SNIPPETS.md` — short texts for GitHub, X, Reddit, HF community
- README section for Hugging Face presence (Space, Org Card, Collection)
- docs/index.html card: "Hugging Face Space live"
- `docs/HUGGINGFACE_SPACE_KIMARI_FIT_LAB.md` updated with deployed status and URLs
- `docs/HUGGINGFACE_ORG_CARD.md` updated with deployed status and URLs
- `docs/LOCAL_SHOWCASE_CHECKLIST.md` updated with pre-publish checklist
- check-release.py checks for v0.1.45 (HF deployment doc, Space URL, no billing/plan)
- tests/test_release_v0145.py

### Deployed
- Hugging Face Space: https://huggingface.co/spaces/kimari-ai/kimari-fit-lab (RUNNING)
- Organization Card: https://huggingface.co/spaces/kimari-ai/README (updated)
- Collection: https://huggingface.co/collections/Smouj013/kimari-compatible-gguf-models-6a0352c75d2bfeff34d51e66

### Safety
- Gate remains BLOCKED
- No HF upload of weights, adapters, or GGUF files
- No training performed
- No HF Jobs executed
- No tokens or private data in any file
- No Kimari-4B release claims
- Space does not execute models
- Collection contains reference models, not official Kimari models

## [0.1.44-alpha] - 2026-05-12

### Added
- `docs/GTX1060_SHOWCASE.md` — GTX 1060 local showcase documentation
- `docs/assets/screenshots/gtx1060-wsl2/` — screenshot directory with README and manifest
- `docs/assets/screenshots/gtx1060-wsl2/manifest.example.json` — screenshot manifest template
- `scripts/docs/validate_screenshot_manifest.py` — screenshot manifest validator
- `huggingface/kimari-fit-lab/` — HF Space pack (Gradio GPU compatibility checker)
- `huggingface/kimari-fit-lab/app.py` — Gradio app for GPU/model compatibility lookup
- `huggingface/kimari-fit-lab/README.md` — Space README
- `huggingface/kimari-fit-lab/requirements.txt` — Space dependencies
- `docs/HUGGINGFACE_SPACE_KIMARI_FIT_LAB.md` — HF Space deployment guide
- `docs/HUGGINGFACE_ORG_CARD.md` — Organization card draft for kimari-ai
- README visual validation section with GTX 1060 benchmark table
- docs/index.html enhanced hero with validation badges
- check-release.py checks for v0.1.44 (showcase docs, HF Space, org card, screenshot manifest)
- tests/test_release_v0144.py

### Safety
- Gate remains BLOCKED
- No HF upload performed
- No training performed
- No real screenshots committed (only manifest template)
- No tokens, API keys, or private data in any file
- No Kimari-4B release claims

## [0.1.43-alpha] - 2026-05-12

### Added
- `docs/LOCAL_INTEGRATION_VALIDATION.md` — local integration validation guide
- `docs/OPENWEBUI_LOCAL_SETUP.md` — Open WebUI setup with Kimari
- `docs/OPENCLAW_LOCAL_SETUP.md` — OpenClaw setup with Kimari
- `docs/CONTINUE_LOCAL_SETUP.md` — Continue.dev setup with Kimari
- `docs/LOCAL_SHOWCASE_CHECKLIST.md` — public screenshot checklist
- `scripts/integrations/validate_local_openai_endpoint.py` — endpoint validator script
- `kimari integrations generate` — `--all --json` output with base_url, model, notes
- `kimari integrations validate` — validate local OpenAI-compatible endpoint
- README section for local integrations validated
- docs/index.html card: "Works with local AI tools"
- check-release.py checks for v0.1.43 (integration docs, no API keys, endpoint validator)
- tests/test_release_v0143.py (15 tests)

### Fixed
- Doctor `--profile test` suggestion improved when default model missing

### Safety
- Gate remains BLOCKED
- No HF upload performed
- No training performed
- No tokens or private data in integration docs
- No API key values in any committed file

## [0.1.42-alpha] - 2026-05-12

### Added
- `build_hf_jobs_command_args()` in `hf_jobs_private_run.py` — returns `list[str]` for safe subprocess invocation
- `--dry-run --json` output now includes `hf_jobs_command_args`, `command_arg_count`, `submit_uses_arg_list: true`
- `docs/LOCAL_OPENAI_ENDPOINT_TEST.md` — documented local OpenAI-compatible endpoint validation
- README section for local endpoint validation on GTX 1060
- docs/index.html card for OpenAI-compatible local endpoint
- docs/SCREENSHOTS.md recommended captures for local endpoint

### Fixed
- `hf_jobs_private_run.py` submit path now uses `command_args` (list[str]) instead of `hf_cmd.split()` — no shell injection risk
- `check-release.py` historical version checks no longer hardcode exact version strings — eliminates cosmetic FAIL on version bumps
- `check-release.py` benchmark results check correctly excludes `*.example.json` and `*.template.json`
- Doctor/status message suggests `--profile test` when default model file is missing

### Safety
- Gate remains BLOCKED
- No HF upload performed
- No training performed
- No tokens or private account data committed
- `shell=True` removed from all subprocess calls in `hf_jobs_private_run.py`

## [0.1.41-alpha] - 2026-03-06

### Added
- `docs/HF_JOBS_ACCESS.md` — generic documentation for HF Jobs access requirements (no private account details)
- `docs/HF_JOBS_FALLBACK_RUNNERS.md` — alternative GPU runners when HF Jobs is unavailable
- `training/scripts/check_hf_jobs_access.py` — programmatic check for HF Jobs access (handles 403, timeout, unauthenticated)
- `--require-jobs-access` flag in `hf_jobs_private_run.py` — blocks submission if Jobs access unavailable (does NOT block `--dry-run` or `--print-command`)

### Fixed
- `check-release.py` benchmark false positive: `*.example.json` and `*.template.json` no longer flagged as real measured results
- Privacy safeguard: all docs and code avoid mentioning personal plan, billing, Pro subscription, or private account details

### Safety
- Gate remains BLOCKED
- No HF upload performed
- No training performed
- No tokens or private account data in any committed file
- `check_hf_jobs_access.py` sanitizes all output (no tokens, no billing info)

## [0.1.40-alpha] - 2026-03-06

### Added
- `docs/GTX1060_LOCAL_RUNTIME_RESULT.md` — honest, sanitized documentation of first real GTX 1060 inference result
- `benchmarks/results/gtx1060-tinyllama-wsl2.example.json` — machine-readable local runtime validation (TinyLlama, NOT Kimari-4B)
- `detect_cuda_version_detailed()` in `detection.py` — returns CUDA version with detection source (nvcc, nvidia-smi, or fallback path)
- `detect_compute_capability_from_llama_server()` in `detection.py` — extracts GPU compute capability from llama-server output as fallback when PyTorch is not installed
- `check_gpu_cuda_info()` in `check_training_stack.py` — reports GPU name, compute capability, CUDA version and source even without PyTorch installed
- README section "Validated Locally on GTX 1060" with CUDA vs CPU-only comparison table
- docs/index.html GTX 1060 local validation card with performance metrics
- docs/SCREENSHOTS.md recommended captures list for GTX 1060 validation

### Fixed
- `doctor --deep` compute capability fallback: if PyTorch not installed, now tries llama-server to detect compute capability (e.g., "6.1 (via llama-server)")
- `detect_cuda_version()` now falls back to parsing nvidia-smi header "CUDA Version: X.Y" when nvcc is not available
- `check_training_stack.py` reports GPU/CUDA info (gpu_name, compute_capability, cuda_version_source) even without PyTorch

### Safety
- Gate remains BLOCKED
- No Kimari-4B weights tested or published
- GTX 1060 result uses TinyLlama test model only

## [0.1.39-alpha] - 2026-03-06

### Fixed
- Recovery merge now protects critical fields from being overwritten by incomplete user config — an incomplete config with `profiles: {}` no longer destroys valid profile data from packaged defaults
- `default_profile` from incomplete user config is only accepted if it exists in the defaults profiles dict; otherwise, the defaults value is kept
- JSON schema now includes `setup_info`, `integrations`, `paths` properties — eliminates `doctor --deep` "Additional properties not allowed" warning

### Added
- `merge_user_config_onto_defaults_safely(defaults, user_config)` helper — safe merge that never lets incomplete user config overwrite `version`, `config_version`, `profiles`, or `server` fields
- `_PROTECTED_FIELDS` constant — fields always taken from defaults during recovery merge
- `_SAFE_USER_FIELDS` constant — fields safe to carry over from incomplete user config
- `tests/test_release_v0139.py` — Test suite for v0.1.39-alpha safe merge behavior

### Changed
- `write_setup_config()` and `apply_setup_changes()` now use `merge_user_config_onto_defaults_safely()` instead of `_base.update(config)` for recovery merges
- Writer module docstring updated with second invariant about safe merge

### Safety
- Gate remains BLOCKED

## [0.1.38-alpha] - 2026-03-05

### Fixed
- Setup writer never starts from empty dict (was producing incomplete configs with missing `version`, `profiles`, `default_profile` keys)
- Recommended profile now resolves to safe fallback if original doesn't exist in available profiles

### Added
- `is_config_complete()` helper — checks user config has required keys (`version`, `profiles`, `default_profile`)
- `load_base_config_for_setup()` helper — loads a safe base config to merge into instead of starting from `{}`
- `resolve_recommended_profile()` helper — returns recommended profile or safe fallback if profile doesn't exist
- `kimari setup --write --yes --reset-user-config` flag for safe config regeneration from packaged defaults
- `kimari setup --json` now includes `resolved_profile`, `user_config_complete`, `recovery_needed`, `config_would_be_valid` fields

### Improved
- `kimari doctor --deep` now detects incomplete user config and suggests recovery command (`kimari setup --write --yes --reset-user-config`)

### Safety
- Gate remains BLOCKED

## [0.1.37-alpha] - 2026-06-03

### Added
- `check_gpu_compute_capability()` in `kimari/doctor/deep.py` — Detects GPU compute capability and warns about Pascal GPUs (sm_61) with incompatible PyTorch cu128/cu130 builds
- `check_gpu_arch_compatibility()` in `training/scripts/check_training_stack.py` — Same Pascal/cu128+ incompatibility check in training stack checker (check #15)
- `kimari doctor --deep` now includes GPU Compute Capability check after CUDA/NVIDIA check
- Pascal GPU compatibility documentation in `docs/INSTALL_WSL2.md` (Step 5b + troubleshooting)
- Pascal GPU compatibility documentation in `docs/INSTALL_MATRIX.md` (GPU Notes subsection)
- Pascal GPU compatibility documentation in `docs/TRAINING_STACK_COMPATIBILITY.md` (Section 6b)
- `tests/test_release_v0137.py` — Test suite for v0.1.37-alpha

### Changed
- `check_training_stack.py` now performs 15 checks (was 14), with `gpu_arch_compatibility` as check #15
- `docs/TRAINING_STACK_COMPATIBILITY.md` version updated to v0.1.37-alpha
- `docs/INSTALL_MATRIX.md` updated with Pascal GPU compatibility table

### Fixed
- Critical bug: `validate_config()` in `kimari/config/loader.py` no longer crashes with `UnboundLocalError` when `jsonschema` is not installed — returns clear error message with install instructions instead
- Pascal GPU (GTX 1060/1070/1080) users now get automatic warning when running `kimari doctor --deep` or `check_training_stack.py --json` with incompatible PyTorch cu128/cu130 builds
- No training in CI. No adapters committed. No HF upload. Gate still BLOCKED.

## [0.1.36-alpha] - 2026-06-03

### Added
- `resolve_smoke_gate()` function in `hf_jobs_micro_sft.py` — unified smoke gate resolution from explicit path, default /tmp, or override
- `docs/HF_JOBS_SMOKE_GATE.md` — Smoke gate documentation explaining explicit path, /tmp fallback, and override
- JSON output now includes `smoke_gate_source`, `smoke_gate_validated`, `smoke_gate_message`, `smoke_summary_path` fields
- `tests/test_release_v0136.py` — Test suite for v0.1.36-alpha

### Changed
- `hf_jobs_micro_sft.py` — Replaced dual smoke gate checks (`check_smoke_summary_validated()` + `--require-smoke-summary`) with single `resolve_smoke_gate()` function
- `hf_jobs_micro_sft.py` — Submit uses ONLY `resolve_smoke_gate()` result (no duplicate checks)
- `hf_jobs_micro_sft.py` — `--print-command` and `--dry-run` are unblocked by smoke gate
- `docs/HF_JOBS_MICRO_SFT_RUNBOOK.md` — Added section about `--require-smoke-summary` with explicit path
- `RELEASE_CHECKLIST.md` — Added v0.1.36 checks
- `scripts/release/check-release.py` — Added v0.1.36 validation checks

### Fixed
- Critical bug: explicit `--require-smoke-summary PATH` no longer blocked by missing `/tmp/hf_jobs_smoke_summary.json`
- Submit path no longer checks smoke gate twice (was checking both `check_smoke_summary_validated()` and `--require-smoke-summary`)
- No training in CI. No adapters committed. No HF upload. Gate still BLOCKED.

## [0.1.35-alpha] - 2026-06-03

### Added
- `training/scripts/create_micro_sft_execution_record.py` — Generates sanitized micro SFT execution records
- `training/scripts/validate_micro_sft_execution_record.py` — Validates execution records for safety (gate BLOCKED, no adapter committed, no HF upload, no raw logs, no tokens)
- `docs/HF_JOBS_MICRO_SFT_EXECUTION_RECORD.md` — Execution record template and documentation
- `docs/HF_JOBS_MICRO_SFT_RUNBOOK.md` — Step-by-step runbook for HF Jobs micro SFT execution

### Changed
- `hf_jobs_micro_sft.py` — Added --require-smoke-summary flag, submit blocked without validated smoke summary unless --override-smoke-gate
- README, docs/index.html, docs/HF_JOBS_MICRO_SFT_RUN.md, docs/KIMARI4B_PRIVATE_SFT_RUN.md updated with version references

### Fixed
- No training in CI. No adapters committed. No HF upload. No raw logs. Gate still BLOCKED. Execution record ensures safe capture of micro SFT results.

## [0.1.34-alpha] - 2026-06-03

### Added
- `training/scripts/check_training_stack.py` — Training stack compatibility checker (no downloads, no training, no network calls)
  - Checks Python version, torch, transformers, datasets, peft, trl, accelerate imports and versions
  - Inspects TrainingArguments and SFTTrainer signatures for parameter compatibility
  - Reports whether TrainingArguments accepts max_seq_length (should be False)
  - Reports whether SFTTrainer accepts tokenizer/processing_class/dataset_text_field/max_seq_length
  - `--json` for structured output, `--verbose` for detailed parameter listings
- `training/scripts/train_sft_lora.py` TRL/SFTTrainer compatibility hardening
  - `build_training_arguments(config, output_dir, eval_dataset_exists)` — Builds TrainingArguments WITHOUT max_seq_length, with eval_strategy/evaluation_strategy fallback
  - `build_sft_trainer(model, training_args, train_dataset, eval_dataset, tokenizer, config)` — Inspects SFTTrainer signature, supports tokenizer and processing_class, passes max_seq_length and dataset_text_field conditionally
  - `prepare_sft_dataset(dataset, tokenizer)` — Converts messages column to text via chat template, supports text column directly, clear error if neither exists
  - Removed max_seq_length from TrainingArguments (not a valid parameter)
- `docs/TRAINING_STACK_COMPATIBILITY.md` — Documentation for training stack versions, compatibility issues, and check_training_stack usage

### Changed
- `training/requirements-training.txt` — Updated with reasonable version ranges for TRL/SFTTrainer compatibility
- `docs/HF_JOBS_MICRO_SFT_RUN.md` — Added mandatory check_training_stack step before micro SFT execution
- `training/configs/hf_jobs_kimari4b_micro_sft.v0.yaml` — Added check_training_stack.py command before train_sft_lora.py
- `training/scripts/validate_micro_sft_readiness.py` — Added check_training_stack and no hf upload command validation
- `RELEASE_CHECKLIST.md` — Added v0.1.34 checks
- `scripts/release/check-release.py` — Added v0.1.34 validation checks
- README, docs/index.html, docs/MICRO_SFT_IMPLEMENTATION.md updated with version references

### Fixed
- TrainingArguments no longer receives max_seq_length (was incorrect, would fail at runtime)
- SFTTrainer compatibility layer prevents TypeError on newer TRL versions (tokenizer → processing_class)
- Dataset with "messages" column now properly converted to text for SFTTrainer
- No training in CI. No adapters committed. No HF upload. Gate still BLOCKED. Training stack compatibility hardened before first real micro SFT.

## [0.1.33-alpha] - 2026-06-02

### Added
- `training/scripts/train_sft_lora.py` now supports real micro SFT training with LoRA/QLoRA
  - New CLI flags: --dataset-path, --eval-dataset-path, --output-dir, --max-steps, --eval-steps, --save-steps, --logging-steps, --per-device-train-batch-size, --gradient-accumulation-steps, --learning-rate, --max-seq-length, --micro-run, --yes
  - `apply_cli_overrides()` function to merge CLI args with YAML config
  - `run_sft_training()` function for actual LoRA SFT training (imports torch/transformers/peft/trl only when training)
  - CI guard: training blocked when CI=true
  - Training requires --micro-run --yes (double confirmation)
  - No --token argument. No push_to_hub. report_to="none". Gate BLOCKED.
  - --show-supported-flags lists all flags without importing torch
- `training/scripts/validate_micro_sft_readiness.py` — Pre-flight validation for micro SFT config safety
- `docs/MICRO_SFT_IMPLEMENTATION.md` — Documentation for micro SFT training implementation

### Changed
- `training/configs/hf_jobs_kimari4b_micro_sft.v0.yaml` updated with --micro-run --yes in training command
- `docs/HF_JOBS_MICRO_SFT_RUN.md` updated with micro-run real training support
- README updated with micro SFT training implementation status
- `docs/index.html` updated with micro SFT training block
- `RELEASE_CHECKLIST.md` updated with v0.1.33 checks
- `scripts/release/check-release.py` updated with v0.1.33 validation checks

### Fixed
- train_sft_lora.py no longer calls unsupported flags from hf_jobs config — all flags now properly supported
- Training loop is no longer a skeleton — real LoRA SFT training is implemented
- No training performed in CI. No adapters committed. No HF upload. Gate still BLOCKED. Micro SFT pipeline ready for real execution.

## [0.1.32-alpha] - 2026-06-02

### Added
- `docs/HF_JOBS_MICRO_SFT_RUN.md` — Guide for running micro SFT on HF Jobs (pipeline validation, not release)
- `docs/HF_JOBS_MICRO_SFT_RESULT.md` — Micro SFT result template and sanitized record (status: pending)
- `training/configs/hf_jobs_kimari4b_micro_sft.v0.yaml` — Config for micro SFT (10 steps, a10g-small, $10 cap, gate BLOCKED)
- `training/scripts/hf_jobs_micro_sft.py` — CLI wrapper for micro SFT submission (--dry-run, --print-command, --allow-submit --yes, --override-smoke-gate, no --token)
- `training/templates/hf_jobs_micro_sft_summary.template.json` — Template for sanitized micro SFT summary
- `training/scripts/create_hf_jobs_micro_sft_summary.py` — CLI to generate sanitized micro SFT summaries
- `training/scripts/validate_hf_jobs_micro_sft_summary.py` — CLI to validate micro SFT summary safety (adapter_committed=false, hf_upload_performed=false, gate BLOCKED)

### Changed
- `docs/HF_JOBS_SMOKE_RUNBOOK.md` updated with micro SFT after smoke validation note
- `docs/KIMARI4B_PRIVATE_SFT_RUN.md` updated with micro SFT path section
- `docs/KIMARI4B_FIRST_RUN_CHECKLIST.md` updated with micro SFT checklist items
- README updated with HF Jobs micro SFT section
- `docs/index.html` updated with micro SFT private path
- `RELEASE_CHECKLIST.md` updated with v0.1.32 checks
- `scripts/release/check-release.py` updated with v0.1.32 validation checks

### Fixed
- No training performed in this version. No adapters committed. No HF upload. Gate still BLOCKED. Micro SFT pipeline prepared but not executed.

## [0.1.31-alpha] - 2026-06-02

### Added
- `docs/HF_JOBS_SMOKE_EXECUTION_RECORD.md` — Smoke test execution record template and result (status: pending)
- `training/templates/hf_jobs_smoke_execution_record.template.json` — Template for sanitized smoke execution record
- `training/scripts/validate_hf_jobs_smoke_summary.py` — CLI to validate smoke summary safety (training_performed=false, gate BLOCKED, no tokens)
- `hf_jobs_status.py` now sanitizes stderr when `--sanitize-logs` is used
- `hf_jobs_status.py` now uses `hf jobs logs --tail N` directly when available for more efficient log retrieval

### Changed
- `docs/HF_JOBS_SMOKE_RUNBOOK.md` updated with validate_hf_jobs_smoke_summary step and smoke-must-pass-before-micro-SFT gate
- `docs/HF_JOBS_PRIVATE_RUN.md` updated with "Smoke must pass before micro SFT" section
- README updated with HF Jobs smoke execution status section
- `docs/index.html` updated with smoke execution validation block
- `RELEASE_CHECKLIST.md` updated with v0.1.31 checks
- `scripts/release/check-release.py` updated with v0.1.31 validation checks

### Fixed
- No training performed. No adapters generated. No HF upload. Gate still BLOCKED.

## [0.1.30-alpha] - 2026-06-01

### Added
- `docs/HF_JOBS_SMOKE_RESULT.md` — Smoke test result template and sanitized summary
- `training/scripts/create_hf_jobs_smoke_summary.py` — CLI to generate sanitized smoke test summaries
- `docs/HF_JOBS_SMOKE_RUNBOOK.md` — Step-by-step runbook for executing HF Jobs smoke test
- `--sanitize-logs` flag in `hf_jobs_status.py` to strip tokens/api keys from log output

### Changed
- `docs/HF_JOBS_PRIVATE_RUN.md` updated with smoke result summary and log sanitization guidance
- README updated with HF Jobs smoke test status section
- `docs/index.html` updated with HF Jobs smoke test block
- `RELEASE_CHECKLIST.md` updated with v0.1.30 checks
- `scripts/release/check-release.py` updated with v0.1.30 validation checks

### Fixed
- No training performed. No adapters generated. No HF upload. Gate still BLOCKED.

## [0.1.29-alpha] — 2026-05-31

### Added
- **docs/HF_JOBS_PRIVATE_RUN.md** — Guide for running Kimari-4B smoke tests on Hugging Face Jobs; HF login requirements, budget guidance ($10), recommended flavors (A10G/L4 for smoke, A100 for training only), forbidden actions, security checklist; no training, no upload, no export, gate BLOCKED
- **docs/HF_JOBS_RESULT_HANDOFF.md** — Guide for bringing sanitized results from HF Jobs to the repo; what to bring (job ID, smoke summary, sanitized logs), what NOT to bring (adapters, checkpoints, GGUF, raw logs, tokens), sanitization process, emergency token response
- **training/configs/hf_jobs_kimari4b_smoke.v0.yaml** — Config for HF Jobs smoke test; job_name, image (pytorch/pytorch:2.6.0-cuda12.4-cudnn9-devel), flavor (a10g-small), max_budget_usd: 10, allow_training: false, allow_hf_upload: false, commands (nvidia-smi, torch cuda check, git clone, pip install, dataset dry-run, SFT dry-run), forbidden actions list
- **training/scripts/hf_jobs_private_run.py** — CLI wrapper for HF Jobs smoke test submission; --config, --print-command, --dry-run, --json, --allow-submit, --yes; by default does NOT submit; requires --allow-submit AND --yes for submission; no --token flag; verifies hf CLI and auth; captures job ID; no file uploads
- **training/scripts/hf_jobs_status.py** — Read-only CLI for checking HF Jobs status; --job-id, --json, --logs, --tail; uses hf jobs inspect/logs; does not modify or cancel jobs; no tokens as arguments
- **training/templates/hf_jobs_smoke_summary.template.json** — Template for sanitized HF Jobs smoke test summary; job_id, flavor, image, status, gpu_detected, torch_cuda_available, repo_installed, dataset_dryrun_passed, sft_dryrun_passed, training_performed: false, adapter_generated: false, hf_upload_performed: false, gate_state: BLOCKED
- **training/scripts/validate_private_sft_commands.py** — CLI to validate generated private SFT commands against train_sft_lora.py supported flags; --command-json, --training-script, --json; detects unsupported flags; verifies gate BLOCKED, public_release_allowed=false, hf_upload_allowed=false; checks no HF upload commands

### Changed
- **Version bumped** to `0.1.29-alpha`
- **training/configs/kimari4b_private_sft_run.v0.yaml** — Renamed `expected_artifacts` to `expected_local_artifacts`; renamed `forbidden_artifacts` to `forbidden_commit_artifacts`; added `local_only: true`, `commit_allowed: false`, `publish_allowed: false`, `artifact_policy_note`
- **training/scripts/kimari4b_private_sft_command.py** — Removed unsupported flags (--dataset-path, --eval-dataset-path, --output-dir) from training_real command; training_real now only uses --config; added command_compatibility_note, command_compatibility_status, unsupported_flags_removed fields to output
- **training/scripts/train_sft_lora.py** — Added --show-supported-flags and --json flags; --show-supported-flags lists all supported CLI flags without importing torch/transformers; works before PyYAML check
- **docs/KIMARI4B_PRIVATE_SFT_RUN.md** — Added Section 11: HF Jobs smoke test path; updated version to v0.1.29-alpha
- **docs/KIMARI4B_FIRST_RUN_CHECKLIST.md** — Added HF Jobs login, smoke test before training, budget confirmed, no --token in CLI, validate_private_sft_commands.py items; updated version to v0.1.29-alpha
- **docs/HF_TOKEN_SAFETY.md** — Added Section 9: HF Jobs token usage (no --token in saved commands, prefer local login, review logs before sharing, sanitize outputs); renumbered sections 9→10 and 10→11; updated version to v0.1.29-alpha
- **README.md** — Added Hugging Face Jobs private smoke test section; updated version badge and references to v0.1.29-alpha
- **docs/index.html** — Updated hero badge and What's New section for v0.1.29-alpha; added HF Jobs smoke test block
- **RELEASE_CHECKLIST.md** — Added v0.1.29 Checks section
- **scripts/release/check-release.py** — Extended with v0.1.29 checks (HF_JOBS_PRIVATE_RUN, HF_JOBS_RESULT_HANDOFF, hf_jobs config, hf_jobs_private_run.py, hf_jobs_status.py, smoke summary template, no --token flag, allow-submit + yes required, allow_training false, allow_hf_upload false, gate BLOCKED, command compatibility, validate_private_sft_commands)
- **ROADMAP.md** — v0.1.28-alpha marked as Released; v0.1.29-alpha marked as Current; v0.1.30-alpha Planned

### Added
- **tests/test_release_v0129.py** — Comprehensive tests for v0.1.29 artifacts

## [0.1.28-alpha] — 2026-05-30

### Added
- **docs/KIMARI4B_PRIVATE_SFT_RUN.md** — Full execution guide for the first private SFT run of Kimari-4B; base model (SmolLM3-3B), dataset (v0), method (LoRA/QLoRA), hardware recommendations, exact commands, what stays local, what summaries can be committed, gate stays BLOCKED, no HF upload
- **training/configs/kimari4b_private_sft_run.v0.yaml** — Run manifest for first private SFT; run_id, status=planned, base_model, dataset_build_dir, sft_config, output_dir, preview_gate_state=BLOCKED, public_release_allowed=false, hf_upload_allowed=false, expected_artifacts, forbidden_artifacts
- **training/scripts/kimari4b_private_sft_command.py** — CLI command generator for Kimari-4B first private SFT; `--config`, `--json`, `--markdown`; generates environment setup, dataset build, preflight, training dry-run, real training, baseline eval, adapter eval, manifest, summary, secret scan, forbidden actions; no actual training
- **docs/KIMARI4B_FIRST_RUN_CHECKLIST.md** — Pre-flight checklist for first private SFT; security, license, dataset, baseline eval, hardware, output directory, adapter manifest, eval summary, no HF upload, gate BLOCKED
- **eval/scripts/kimari4b_eval_plan.py** — CLI eval plan generator; `--baseline-label`, `--adapter-label`, `--json`, `--markdown`; generates baseline eval plan, adapter eval plan, compare command, summary command, manual review checklist; no scores unless results provided
- **docs/KIMARI4B_EVAL_CRITERIA.md** — Evaluation criteria for Kimari-4B; coding, sysadmin, Spanish technical, JSON validity, agent usefulness, safety, local hardware awareness, no false claims, no unsafe public exposure advice, regression vs baseline
- **training/templates/kimari4b_private_summary.template.json** — Template for sanitized training summary; run_id, base_model, dataset_id, adapter_local_only, baseline_eval_summary, adapter_eval_summary, comparison_status, manual_review_required, safety_regression_detected, preview_gate_state=BLOCKED, public_release_allowed=false, hf_upload_allowed=false

### Changed
- **Version bumped** to `0.1.28-alpha`
- **docs/FIRST_PRIVATE_SFT_HANDOFF.md** — Added Section 9: Kimari-4B specific handoff notes (what to bring from GPU, what NOT to bring, how to clean summaries, scan_for_secrets on Kimari-4B artifacts); updated version and date
- **docs/ADAPTER_PREVIEW_GATE.md** — Added Kimari-4B first private run section (current status: BLOCKED, minimum conditions for BLOCKED → PENDING, no automatic transitions); updated version and date
- **README.md** — Added Kimari-4B first private SFT run section with links to all new docs, scripts, and templates; updated version badge and alpha notice to v0.1.28-alpha
- **docs/index.html** — Updated hero badge and What's New section for v0.1.28-alpha; added private SFT preparation, first run checklist, command generator, eval plan chips; added status table rows for v0.1.28
- **RELEASE_CHECKLIST.md** — Added v0.1.28 Checks section
- **scripts/release/check-release.py** — Extended with v0.1.28 checks (KIMARI4B_PRIVATE_SFT_RUN, KIMARI4B_FIRST_RUN_CHECKLIST, KIMARI4B_EVAL_CRITERIA, kimari4b_private_sft_run.v0.yaml, kimari4b_private_sft_command.py, kimari4b_eval_plan.py, kimari4b_private_summary.template.json, MODEL_CARD says no public weights, no GGUF/adapters/weights tracked, gate BLOCKED)
- **ROADMAP.md** — v0.1.27-alpha marked as Released; v0.1.28-alpha marked as Current; v0.1.29-alpha Planned

### Added
- **kimari/console/ module** — `render.py` with `render_status_table()`, `render_doctor_table()`, `render_gateway_summary()`, `render_next_steps()`; no external dependencies (no rich); clean ASCII/Unicode simple output; Windows compatible
- **kimari/integrations/ module** — `config_generator.py` with `generate_openwebui_config()`, `generate_openclaw_config()`, `generate_hermes_config()`, `generate_continue_config()`, `sanitize_config()`, `validate_local_base_url()`; default base_url http://127.0.0.1:11435/v1; no tokens; no API keys; no writing by default
- **`kimari integrations generate` command** — Generates configuration snippets for Open WebUI, OpenClaw, Hermes, and Continue.dev; `--target` for specific tool; `--all` for all; `--json` for structured output; `--write --output <path>` for explicit file writing; `--base-url` override; rejects non-local base_url with strong warning; rejects sensitive output paths without `--force`
- **Improved `kimari status` human output** — Structured table with aligned key-value pairs; Version, Config, Models, Default profile, Server, Gateway, Preview gate fields; "Next steps" section; `--json` output unchanged
- **Improved `kimari doctor --deep` human output** — Structured PASS/WARN/FAIL table with ✓/⚠/✗ icons; padded names; summary line (N PASS, M WARN, K FAIL); auto-generated "Suggested next steps" from WARN/FAIL items; `--json` output unchanged
- **docs/INTEGRATION_CONFIG_GENERATOR.md** — Guide for integration config generator; supported targets; usage examples; example JSON outputs (no tokens); security (localhost only, --write requires --output); validation with doctor/status
- **docs/GATEWAY_PROTOTYPE_PLAN.md** — Phased gateway prototype plan; 5 phases from dry-run CLI to dashboard/web UI; endpoints by phase; security per phase; gateway does NOT serve OpenAI-compatible endpoints
- **docs/CONSOLE_UX.md** — Console output style guide; no rich dependency; JSON vs human output; PASS/WARN/FAIL format; next steps; emoji policy; Windows compatibility
- **scripts/docs/generate_safe_cli_screenshots_plan.py** — Generates plan for CLI screenshot captures; 6 plans (status, doctor --deep, gateway --plan, integrations generate --all, benchmark --dry-run, update check); `--json` and `--markdown` output; safety notes; no actual screenshots
- **Updated docs/SCREENSHOTS.md** — Added 6 new CLI screenshot sections; added screenshot plan script reference; added rule: no real screenshots without review

### Changed
- **Version bumped** to `0.1.27-alpha`
- **Gateway wording corrected** — `kimari/gateway/plan.py` and `docs/GATEWAY_PLAN.md` now correctly state that the gateway helps configure and monitor the llama-server OpenAI-compatible endpoint (not that the gateway serves OpenAI-compatible endpoints itself)
- **README.md** — Added cleaner console output, integration config generator, gateway prototype plan sections; updated version badge and references to v0.1.27-alpha
- **docs/index.html** — Updated hero badge and What's New section for v0.1.27-alpha; added console polish, integration config generator, gateway prototype plan, safe screenshots plan feature cards
- **RELEASE_CHECKLIST.md** — Added v0.1.27 Checks section
- **scripts/release/check-release.py** — Extended with v0.1.27 checks (console render.py, integrations config_generator.py, INTEGRATION_CONFIG_GENERATOR.md, GATEWAY_PROTOTYPE_PLAN.md, CONSOLE_UX.md, generate_safe_cli_screenshots_plan.py, gateway wording, integration configs contain no tokens, no weights/GGUF/adapters, gate BLOCKED)
- **ROADMAP.md** — v0.1.26-alpha marked as Released; v0.1.27-alpha marked as Current; v0.1.28-alpha Planned

## [0.1.26-alpha] — 2026-05-28

### Added
- **Secret scanner hardening** — `scripts/security/scan_for_secrets.py` no longer skips security guide files entirely; instead scans them line-by-line allowing safe placeholders (hf_..., hf_your_token_here, <HF_TOKEN>, your-api-key, sk-..., <token>, <API_KEY>); added `--include-history-note` flag for git history check reminder; version 1.1.0
- **docs/SECRET_SCAN_POLICY.md** — Comprehensive policy for what the scanner detects, allowed placeholders, how to mark placeholders, how to review git history, emergency steps for real tokens
- **kimari/performance/measured_benchmark.py** — Module for measured benchmarks against OpenAI-compatible endpoints; `build_chat_completion_payload()`, `measure_chat_completion()`, `calculate_tokens_per_second()`, `sanitize_benchmark_result()`, `validate_measured_result()`; only uses `requests`; never invents metrics; score_status="measured" only for real responses
- **`kimari benchmark --measure`** — Experimental measured benchmark command; requires --endpoint, --model, --yes flags; sends real chat completion requests; records tokens/s, elapsed time, usage data; uses benchmarks/prompts/local_benchmark_prompts.jsonl; results sanitized; clear errors on connection failure (no stacktrace)
- **docs/MEASURED_BENCHMARKS.md** — Guide for running measured benchmarks; supported endpoints; privacy guidelines; result sanitization; sharing via performance_report issue template
- **benchmarks/prompts/local_benchmark_prompts.jsonl** — 8 safe benchmark prompts (greeting, structured-output, coding-python, bash, spanish-technical, docker, linux); no private data
- **benchmarks/results/.gitkeep** — Results directory for measured benchmark output (*.json gitignored)
- **benchmarks/examples/.gitkeep** — Example results directory (committable)
- **kimari/doctor/deep.py** — Deep diagnostic module with 9 checks (Python, Paths, Config, Models Dir, llama-server, Default Profile, Secret Scanner, Benchmark Prompts, Preview Gate); all pure/safe functions; PASS/WARN/FAIL status
- **`kimari doctor --deep`** — CLI command for extended diagnostics; `--json` for machine-readable output; no model execution, no downloads, no GPU required
- **docs/DOCTOR_DEEP.md** — Guide for deep diagnostics; what it checks; how to interpret PASS/WARN/FAIL; usage; common resolutions
- **`kimari gateway` command** — Dry-run gateway controller with --dry-run, --status, --plan, --json; dry-run only, no real server started
- **`kimari update check` command** — Version check with --online, --json; offline by default, never auto-updates or auto-installs
- **Enhanced `kimari status`** — Now includes version, config path, models dir, default profile, gateway state, preview gate state fields
- **Enhanced `kimari doctor --deep`** — 5 new checks: Kimari Version, CUDA/NVIDIA (best-effort, not required), Packaged Defaults, Gateway Module, Integration Docs; total 14 checks
- **kimari/gateway/ module** — `state.py` and `plan.py` for gateway state management and dry-run planning; no real server startup
- **kimari/update/ module** — `check.py` for offline/online version checking; never auto-installs
- **docs/GATEWAY_PLAN.md** — Gateway local controller design and planned endpoints
- **docs/UPDATE.md** — Update guide and version management
- **docs/INSTALL_MATRIX.md** — Installation methods and platform support matrix
- **docs/OPENWEBUI_OPENCLAW_QUICK_CONFIG.md** — Quick configuration guide for Open WebUI, OpenClaw, Hermes
- **Gateway planned endpoints** — GET /health, /status, /profiles, /models, /config, /logs, /integrations; POST /server/start, /server/stop, /benchmark/run
- **Default gateway host 127.0.0.1:11436** — Localhost only, never 0.0.0.0
- **New tests** (`tests/test_release_v0126.py`)

### Changed
- **Version bumped** to `0.1.26-alpha`
- **scripts/security/scan_for_secrets.py** — No longer skips security guide files entirely; scans them line-by-line; allows safe placeholders; added --include-history-note; version 1.1.0
- **kimari/performance/benchmark_plan.py** — Updated warnings to reference measured benchmark availability in v0.1.26-alpha; updated tune --apply blocked reason
- **kimari/cli/main.py** — Added doctor --deep, benchmark --measure with --endpoint/--model/--yes/--output; tune --apply still blocked with updated message
- **docs/PERFORMANCE_TUNING_PLAN.md** — Added three-phase separation: estimated planning, measured benchmark, future auto-tuning
- **README.md** — Added measured benchmark experimental, doctor --deep, secret scan policy, tune apply still blocked sections
- **docs/index.html** — Added measured benchmark, doctor deep, secret scanner hardening cards
- **RELEASE_CHECKLIST.md** — Added v0.1.26 Checks section
- **scripts/release/check-release.py** — Added v0.1.26 checks (SECRET_SCAN_POLICY, MEASURED_BENCHMARKS, DOCTOR_DEEP, measured_benchmark.py, doctor/deep.py, benchmark prompts, results gitignored, tune --apply blocked, gate BLOCKED)
- **ROADMAP.md** — v0.1.25-alpha marked as Released; v0.1.26-alpha marked as Current; v0.1.27-alpha Planned

## [0.1.25-alpha] — 2026-05-27

### Added
- **docs/HF_TOKEN_SAFETY.md** — Comprehensive guide for safe Hugging Face token handling; never paste tokens in chat/issues/commits/logs/screenshots; use environment variables; tokens of minimum privilege; revoke exposed tokens immediately; use `huggingface-cli login` only in secure local environment; don't save tokens in the repo; don't include tokens in screenshots; don't upload anything to HF until preview gate allows; detecting committed tokens via scan_for_secrets.py; what to do if a token is accidentally committed
- **scripts/security/scan_for_secrets.py** — CLI secret scanner that searches for HF tokens (hf_...), OpenAI API keys (sk-...), api_key assignments, password assignments, token assignments, private keys (PEM), AWS access keys, Bearer tokens in headers, and sensitive paths (/home/username/, /Users/username/, C:\Users\username\); --paths for file/directory scanning; --json for structured output; supports documented false positives via inline markers; no external dependencies
- **docs/FIRST_PRIVATE_SFT_HANDOFF.md** — Guide for bringing sanitized results from RunPod/local GPU to the repo; what can be committed (reviewed manifest, eval summary, compare summary, private run record, screenshots); what must remain local (adapters, checkpoints, GGUF, raw outputs); handoff process with security checklist; secret scanning before commit; review checklist; emergency procedures for accidental commits
- **docs/PRIVATE_SFT_RUN_COMMANDS.md** — Guide listing all expected commands for first private SFT execution; setup env, build dataset, preflight, training command preview, real training command, baseline eval, adapter eval, create manifest, create eval summary, create private run record, scan secrets; each command with safe placeholders, description, and safety notes
- **docs/PERFORMANCE_TUNING_PLAN.md** — Plan for moving from estimation to real, reproducible local measurement; defines what to measure (tokens/s, TTFT, VRAM, RAM, context, batch/ubatch, cache types, gpu_layers, flash_attn, mmap/mlock, stability); target hardware profiles (gtx1060-safe, gtx1080-balanced, ide-local, agent-local); benchmark matrix (context × batch × cache combos); dry-run workflow; auto-tuning plan; explicit "what we do NOT do" section; no invented benchmarks
- **kimari/performance/benchmark_plan.py** — Pure benchmark plan generation module; generates BenchmarkPlan and BenchmarkCell dataclasses; generate_benchmark_plan() creates recommended settings and full parameter matrix; generate_tune_recommendation() creates tune recommendations using existing estimator; no side effects, no network calls, no model execution; --apply blocked with clear error
- **`kimari benchmark` command** — CLI subcommand for benchmark plan generation; `--dry-run` (default) generates estimated plan without executing models; `--profile` for specific GPU profile; `--matrix` for full parameter matrix; `--measure` (requires running server, for future use); `--json` for structured output; output includes measured:false and tokens_per_second:null for dry-runs; never claims measured results from estimation
- **`kimari tune` command** — CLI subcommand for recommended settings; `--dry-run` (default) shows recommendations from estimation; `--profile` for specific GPU profile; `--apply` intentionally BLOCKED in v0.1.25-alpha (planned for v0.1.26); `--json` for structured output; includes disclaimer that results are estimates not measurements
- **docs/SHOWCASE_PLAN.md** — Plan for presenting Kimari honestly and attractively; README visual plan (Performance & Benchmarking, Security, Showcase sections); GitHub Pages visual plan (benchmark/tune/secret scanner cards); HF placeholder docs-only plan; Reddit/GitHub launch checklist; explicit "what we do NOT do" section (no fake benchmarks, no Kimari-4B published claims, no screenshots with tokens)

### Changed
- **Version bumped** to `0.1.25-alpha`
- **training/scripts/create_private_run_record.py** — Hardened with expanded path rejection (Linux /home/username/, macOS /Users/username/, Windows C:\Users\username\); added suspicious string detection in summaries (hf_ tokens, api_key, password, token assignments, private keys); added `security_scan_status` field to output record (clean/suspicious_patterns_detected); added `security_scan_warnings` list; rejects writes when suspicious patterns detected (dry-run still outputs JSON)
- **docs/SAFE_SCREENSHOT_CAPTURE.md** — Updated naming examples to use real Kimari commands (kimari setup --json, kimari optimize --profile test --json, kimari start --dry-run, kimari api --dry-run, preflight/postrun scripts) instead of non-existent ones; added HF_TOKEN_SAFETY reference in rules summary
- **docs/SCREENSHOTS.md** — Added HF_TOKEN_SAFETY reference in safe screenshot capture section
- **README.md** — Added HF Token Safety Guide link; added Private SFT Handoff link; added Private SFT Run Commands link; added Secret Hygiene section with scan command; added benchmark and tune command sections; added Performance Tuning Plan link; added Showcase Plan link; added "Benchmark dry-run" and "Tune dry-run" to Works Today; updated version to v0.1.25-alpha
- **docs/index.html** — Updated hero badge to "Security hardening, performance foundation, showcase prep"; added benchmark dry-run, tune dry-run, and showcase plan chips; added "New: Benchmark & Tune Commands" section with visual cards; updated Kimari-4B roadmap with CLI dry-run availability
- **RELEASE_CHECKLIST.md** — Added v0.1.25 Checks section (19 items: HF_TOKEN_SAFETY, scan_for_secrets, FIRST_PRIVATE_SFT_HANDOFF, PRIVATE_SFT_RUN_COMMANDS, path rejection for Linux/macOS/Windows, suspicious pattern detection, security_scan_status, real commands in screenshots, HF_TOKEN_SAFETY references, README links, no HF tokens in repo, no weights, gate BLOCKED)
- **scripts/release/check-release.py** — Added section [51/55] v0.1.25 secret hygiene & secure handoff checks; added section [52/55] v0.1.25 performance & showcase checks; HF_TOKEN_SAFETY.md exists; scan_for_secrets.py exists; FIRST_PRIVATE_SFT_HANDOFF.md exists; PRIVATE_SFT_RUN_COMMANDS.md exists; PERFORMANCE_TUNING_PLAN.md exists; SHOWCASE_PLAN.md exists; benchmark_plan.py exists; README mentions benchmark and tune commands; no fake benchmark numbers; benchmark --dry-run --json works with measured:false; tune --dry-run --json works with apply_blocked:true; create_private_run_record.py has security_scan_status and suspicious pattern detection; SAFE_SCREENSHOT_CAPTURE.md references HF_TOKEN_SAFETY; SCREENSHOTS.md references HF_TOKEN_SAFETY; README links to new docs; no real HF token in README/CHANGELOG; no adapter/weights/GGUF tracked; default_profile=test; gate BLOCKED
- **ROADMAP.md** — v0.1.24-alpha marked as Released; v0.1.25-alpha marked as Current; v0.1.26-alpha Planned (real measured benchmarks, auto-tuning experimental, doctor --deep, Open WebUI/OpenClaw one-command config, reviewed screenshots)

### Added
- **docs/FIRST_PRIVATE_SFT_RECORD.md** — Guide for registering a private SFT run without committing sensitive outputs; documents run_id, base model, dataset hash, training config, hardware/runtime summary, adapter manifest (local only), eval/compare summaries, preview gate state (BLOCKED), blocked actions, what can be committed, what must remain local
- **training/templates/private_sft_run_record.template.json** — Committable template for private SFT run records; gate.state=BLOCKED, public_release_allowed=false, hf_upload_allowed=false; all real values replaced with PLACEHOLDER or null
- **training/scripts/create_private_run_record.py** — CLI script to generate private SFT run records; --run-config, --manifest, --eval-summary, --compare-summary, --output, --dry-run, --json; computes SHA256 of manifest/summary files if they exist; rejects absolute home directory paths; gate always BLOCKED; works without PyYAML
- **docs/SAFE_SCREENSHOT_CAPTURE.md** — Guide for capturing safe terminal screenshots; pre-capture checklist (clean terminal, no private paths, no tokens/secrets), during-capture guidelines (dark theme, readable font, consistent window size), post-capture review (secrets check, benchmark review, Kimari-4B status), recommended dimensions, allowed formats (PNG/WebP), naming convention, alt text requirements
- **scripts/docs/generate_cli_screenshot_text.py** — CLI tool that generates safe text blocks for screenshot captures; supports --kind setup|optimize|preflight|training_preview|baseline_eval|postrun; --output for file writing; --json for structured output; no private paths, no tokens, no real benchmarks, no user-specific data
- **docs/assets/screenshots/examples/** — 5 safe text example files (kimari-setup-json, kimari-preflight-private-sft, kimari-training-command-preview, kimari-baseline-eval-plan, kimari-postrun-dryrun); can be used as basis for generating real captures; no secrets, no private paths, no benchmarks

### Changed
- **Version bumped** to `0.1.24-alpha`
- **README.md** — Added First Private Run Record section with links to template, script, and docs; added Safe Screenshot Capture link; added screenshot text examples reference; updated version badge and alpha notice
- **docs/index.html** — Updated hero badge and What's New section for v0.1.24-alpha; added private run record, safe screenshot capture, CLI screenshot text generator, screenshot text examples chips; added v0.1.24 status table rows; updated project status description
- **docs/SCREENSHOTS.md** — Added Safe Screenshot Capture section with link to SAFE_SCREENSHOT_CAPTURE.md; added CLI Text Examples section with links to example files and generator command; added Replacing Placeholders section with 6-step process
- **RELEASE_CHECKLIST.md** — Added v0.1.24 Checks section (19 items: run record docs, template, script, safe capture, text generator, examples, no secrets, no adapters, gate BLOCKED)
- **scripts/release/check-release.py** — Expanded with v0.1.24 checks (FIRST_PRIVATE_SFT_RECORD, run record template JSON/gate/public_release/hf_upload, create_private_run_record, SAFE_SCREENSHOT_CAPTURE, generate_cli_screenshot_text, 5 screenshot example txt files, no secrets in examples, SCREENSHOTS.md references, README links, no oversized screenshots, no adapter/weights/GGUF, preview gate BLOCKED, no false claims)
- **ROADMAP.md** — v0.1.23-alpha marked as Released; v0.1.24-alpha marked as Current; v0.1.25-alpha Planned (first private SFT execution, adapter manifest, sanitized eval summary, ORPO/DPO decision, reviewed screenshots)

## [0.1.23-alpha] — 2026-05-25

### Fixed
- **training/scripts/postrun_private_sft.py** — `step_create_eval_summary` now passes `--json` to the `create_eval_summary.py` subprocess directly in the command list, instead of appending `--json` to the command string after execution

### Changed
- **training/scripts/preflight_private_sft.py** — Reads `dataset_build_dir` from run_config YAML when available; falls back to `dataset/build/kimari-v0/report.json` when not specified. Adds `dataset_build_dir`, `dataset_report_path`, and `dataset_build_dir_source` fields to JSON output. Reuses parsed YAML data to avoid double-parsing.
- **Version bumped** to `0.1.23-alpha`
- **README.md** — Added Screenshots & CLI Preview section with link to docs/SCREENSHOTS.md; updated version badge and references to v0.1.23-alpha
- **docs/index.html** — Updated hero badge and What's New section for v0.1.23-alpha; added CLI Preview section with code cards; updated status table with v0.1.22/v0.1.23 entries; added link to SCREENSHOTS.md
- **RELEASE_CHECKLIST.md** — Added v0.1.23 Checks section (postrun --json, preflight dataset_build_dir, screenshots docs, no secrets, no benchmarks, README/index links)
- **scripts/release/check-release.py** — Expanded with v0.1.23 checks (postrun --json passthrough, preflight dataset_build_dir, SCREENSHOTS.md, screenshots assets README/PLACEHOLDER, no secrets in screenshot docs, no benchmark claims, README/index.html screenshots references, no weight files, preview gate BLOCKED, no false claims)

### Added
- **docs/SCREENSHOTS.md** — Screenshots gallery and CLI preview documentation; illustrative code blocks for setup, optimize, preflight, training command preview, baseline eval plan, postrun; screenshot policy and planned screenshots table; no secrets, no real training outputs, no benchmarks, Kimari-4B not released
- **docs/assets/screenshots/README.md** — Screenshot naming conventions (kimari-<command>.png), allowed formats (PNG/WebP), recommended dimensions, content guidelines (no secrets, no fake UI, no benchmarks), optimization policy, review checklist
- **docs/assets/screenshots/PLACEHOLDER.md** — Checklist of 7 planned screenshots with capture guidelines; no fake data, no invented UI
- **New tests** (`tests/test_release_v0123.py`) — Tests for postrun --json fix, preflight dataset_build_dir from run_config, preflight fallback, screenshots docs existence/content, README screenshots section, index.html screenshots section, release-check, no tracked artifacts, version consistency

## [0.1.22-alpha] — 2026-05-24

### Added
- **docs/REMOTE_GPU_RUNPOD_GUIDE.md** — Guide for running first private SFT on RunPod or similar GPU cloud; GPU recommendations (RTX 4090, L40S, A100), VRAM estimates, step-by-step setup, safety reminders, cost/storage estimates
- **training/requirements-training.txt** — Separated training dependencies (torch, transformers, datasets, accelerate, peft, trl, safetensors, pyyaml, sentencepiece, protobuf); not installed in CI by default
- **training/scripts/preflight_private_sft.py** — CLI preflight check for private SFT readiness; checks Python version, torch/CUDA availability, training deps, dataset build, gitignore, gate BLOCKED; --strict mode; --json output; works without torch installed
- **training/scripts/postrun_private_sft.py** — CLI post-training orchestration; calls create_adapter_manifest, create_eval_summary, compare_runs; verifies gate BLOCKED; suggests next steps; dry-run by default; --json output
- **training/configs/private_sft_execution.example.yaml** — Execution config template for remote/local GPU; provider, GPU type, VRAM, HF cache, commands (build_dataset, preflight, train, eval, postrun)
- **docs/PRIVATE_RUN_ARTIFACTS.md** — Classification of training artifacts: what stays local (adapter weights, checkpoints, optimizer states, raw eval outputs, TensorBoard, WandB) vs what can be committed if sanitized (MANIFEST.yaml, eval_summary.json, compare_summary.json); pre-commit review checklist
- **docs/PRIVATE_RUN_FAILURES.md** — Troubleshooting guide for 10 failure modes (OOM, CUDA unavailable, tokenizer failure, dataset validation, PEFT/TRL mismatch, eval endpoint, hash mismatch, accidental raw outputs, abort procedure, recovery)
- **training/scripts/run_training_command_preview.py** — CLI for training command preview; recommended_command, recommended_environment, expected_outputs, forbidden_commit_patterns, safety_warnings; --json output
- **eval/scripts/run_baseline_eval_plan.py** — CLI for baseline eval planning; model_label, prompts, categories, recommended_endpoint, score_status manual_review_required; --dry-run; --json output
- **eval/scripts/run_adapter_eval_plan.py** — CLI for adapter eval planning; same structure as baseline; baseline_available check, compare_with_baseline step; --dry-run; --json output
- **RELEASE_CHECKLIST.md** — Added v0.1.22 Checks section
- **scripts/release/check-release.py** — Expanded with v0.1.22 checks (REMOTE_GPU_RUNPOD_GUIDE, requirements-training, preflight script, postrun script, private execution config, private run artifacts/failures docs, training command preview, baseline/adapter eval plan scripts, no adapter/weights/GGUF tracked, preview gate BLOCKED)
- **New tests** (`tests/test_release_v0122.py`) — Tests for preflight, postrun, training command preview, baseline/adapter eval plans, private execution config, private artifacts/failures docs, requirements-training, train_sft_lora improvements, release-check

### Changed
- **Version bumped** to `0.1.22-alpha`
- **training/scripts/train_sft_lora.py** — Added --print-command (print recommended training command), --estimate-only (print step estimation JSON), --require-dataset (fail if dataset missing), output_dir gitignored validation, warning: "Real training must not run in CI"
- **docs/PRIVATE_TRAINING_RUNBOOK.md** — Added preflight_private_sft, run_training_command_preview, baseline/adapter eval plan, postrun_private_sft, remote GPU guide references
- **docs/ADAPTER_ARTIFACT_POLICY.md** — Added PRIVATE_RUN_ARTIFACTS.md, postrun_private_sft.py, checklist before committing summaries
- **docs/BASELINE_EVAL_PLAN.md** — Added run_baseline_eval_plan.py, run_adapter_eval_plan.py, compare_runs.py comparison
- **docs/SFT_TO_ORPO_DECISION.md** — Added ORPO decision deferred until postrun summary, manual_review_required blocks ORPO, safety_regression_detected blocks ORPO
- **README.md** — Added remote GPU guide, training requirements, preflight/postrun scripts, private run artifacts/failures references; updated version to v0.1.22-alpha
- **docs/index.html** — Updated hero badge and What's New section for v0.1.22-alpha; remote GPU execution, preflight/postrun, training requirements, private run artifacts, no public weights, preview gate BLOCKED
- **ROADMAP.md** — v0.1.21-alpha marked as Released; v0.1.22-alpha marked as Current; v0.1.23-alpha Planned

## [0.1.21-alpha] — 2026-05-23

### Added
- **training/templates/adapter_manifest.template.yaml** — Template for adapter manifest files; includes adapter_name, run_id, base_model, dataset_id, training_config, LoRA parameters, training timestamps, adapter files/hashes, eval_results, baseline_results, preview_gate_state (BLOCKED), public_release_allowed (false), hf_upload_allowed (false), state_history, notes
- **training/scripts/create_adapter_manifest.py** — CLI script to generate adapter manifests from template; --run-config, --adapter-dir, --output, --dry-run, --json; rejects suspicious files (.safetensors/.bin/.pt/.pth/.ckpt/.gguf); enforces preview_gate_state=BLOCKED, public_release_allowed=false, hf_upload_allowed=false; works without PyYAML
- **docs/PRIVATE_SFT_EXECUTION_CHECKLIST.md** — Practical pre-flight checklist for first private SFT; GPU environment, license review, dataset validation, baseline eval plan, run config review, output_dir gitignored, storage, no WandB public, no HF upload, manifest creation, KimariFit eval, preview gate stays BLOCKED
- **docs/SFT_TO_ORPO_DECISION.md** — Decision framework for whether ORPO/DPO proceeds after SFT; safety regression → no ORPO; coding/sysadmin improvement without safety regression → consider ORPO; overfitting → expand dataset; baseline surpasses adapter → review dataset/config; ORPO only if preference_v0 has sufficient quality; DPO/ORPO never runs in CI
- **docs/PRIVATE_EVAL_RESULTS_POLICY.md** — What eval results can be committed; anonymous summaries, category counts, manual review status, hashes OK; no private prompts, no local paths, no tokens, no sensitive outputs, no unreviewed benchmark claims
- **eval/templates/eval_summary.template.json** — Committable eval summary template; run_id, model_label, kimari_version, prompt_count, category_counts, score_status, manual_review_required, safety_regression_detected, false_claims_detected, reviewer, notes; no raw private prompts
- **eval/scripts/create_eval_summary.py** — CLI script for sanitizing raw eval results into committable summaries; --input, --output, --json; strips raw prompt/response fields; marks manual_review_required if no scores; never invents scores
- **tests/fixtures/private_eval_raw.json** — Synthetic fixture with raw outputs for testing eval result sanitization
- **RELEASE_CHECKLIST.md** — Added v0.1.21 Checks section
- **scripts/release/check-release.py** — Expanded with v0.1.21 checks (adapter manifest template, create_adapter_manifest, PRIVATE_SFT_EXECUTION_CHECKLIST, SFT_TO_ORPO_DECISION, PRIVATE_EVAL_RESULTS_POLICY, eval summary template, create_eval_summary, compare_runs summary-output, preview gate BLOCKED, no adapter/weight files tracked)
- **New tests** (`tests/test_release_v0121.py`) — Tests for adapter manifest template, create_adapter_manifest, eval summary template, create_eval_summary, compare_runs verdicts, preview gate BLOCKED, no adapter/weights/GGUF tracked

### Changed
- **Version bumped** to `0.1.21-alpha`
- **eval/scripts/compare_runs.py** — Added --summary-output for committable eval summaries; added comparison verdict (insufficient_data, candidate_better, candidate_worse, mixed, manual_review_required); safety_regression_detected in candidate → verdict=candidate_worse; never invents scores
- **docs/PRIVATE_TRAINING_RUNBOOK.md** — Added references to create_adapter_manifest.py, create_eval_summary.py, SFT_TO_ORPO_DECISION, PRIVATE_EVAL_RESULTS_POLICY, adapter manifest template
- **docs/ADAPTER_ARTIFACT_POLICY.md** — Added manifest template path, create_adapter_manifest.py usage, manifest committable if no sensitive paths/weights, adapter files never committed
- **docs/ADAPTER_PREVIEW_GATE.md** — Added manifest template and eval summary template references; safety_regression_detected field; creating manifest does NOT advance the gate
- **docs/BASELINE_EVAL_PLAN.md** — Added create_eval_summary.py usage, compare_runs --summary-output, eval summary template references
- **README.md** — Added adapter manifest template, private SFT execution checklist, SFT→ORPO decision, private eval results policy, eval summary template references; updated version to v0.1.21-alpha
- **docs/index.html** — Updated hero badge and What's New section for v0.1.21-alpha; added adapter manifest, execution checklist, SFT→ORPO decision, eval summary policy, preview gate BLOCKED chips
- **ROADMAP.md** — v0.1.20-alpha marked as Released; v0.1.21-alpha marked as Current; v0.1.22-alpha Planned

## [0.1.20-alpha] — 2026-05-22

### Added
- **MODEL_CARD.md checklist fix** — "Training data curated" split into "Seed dataset v0 prepared and documented → In Progress" and "Full training dataset curated → Not started"; version history updated for v0.1.19-alpha
- **docs/BASELINE_EVAL_PLAN.md** — Baseline evaluation plan for SmolLM3-3B before SFT; categories (coding, bash, docker, linux, windows, spanish technical, integrations, security, no false claims); outputs in eval/results/; not committed by default; manual_review_required
- **docs/ADAPTER_ARTIFACT_POLICY.md** — Defines private adapter lifecycle; storage in training/adapters/; gitignore rules for safetensors/optimizer/checkpoints/logs; naming convention (kimari-smollm3-sft-v0); what can/cannot be committed; release gate before publication
- **docs/PRIVATE_TRAINING_RUNBOOK.md** — Step-by-step runbook for first private SFT; environment setup → dataset build → baseline eval → SFT → adapter save → KimariFit eval → ORPO decision; no publication without gate
- **docs/ADAPTER_PREVIEW_GATE.md** — Criteria for transitioning adapter from private to preview; states (BLOCKED, PENDING, APPROVED_FOR_PRIVATE_TESTING, APPROVED_FOR_PUBLIC_PREVIEW); default BLOCKED; 10+ requirements including license verification, baseline comparison, safety review
- **training/configs/private_sft_run.v0.yaml** — Run manifest for first private SFT; run_id, status=planned, base_model, dataset paths, output_dir, public_release_allowed=false, hf_upload_allowed=false
- **training/scripts/run_private_sft_dryrun.py** — CLI dry-run validation for private SFT; validates dataset build, base model, output_dir gitignored, no public/HF release; prints commands, expected outputs, blocked actions; --json output
- **training/scripts/build_v0_pipeline.py** — Orchestrates full v0 pipeline dry-run; validate_training_ready → build_dataset_mix → train_sft_lora --dry-run → export_gguf_plan --dry-run → kimarifit --score-plan; --dry-run --json; no heavy outputs
- **eval/baseline/README.md** — Baseline eval documentation; SmolLM3-3B before fine-tuning; outputs not committed; how to compare with adapter
- **eval/scripts/compare_runs.py** — CLI tool for comparing baseline vs adapter eval results; --baseline --candidate --json; counts categories, missing outputs, manual_review_required; no invented scores; returns comparison_status
- **tests/fixtures/baseline_eval_result.json** — Synthetic baseline eval fixture for compare_runs testing
- **tests/fixtures/adapter_eval_result.json** — Synthetic adapter eval fixture for compare_runs testing
- **RELEASE_CHECKLIST.md** — Added v0.1.20 Checks section
- **scripts/release/check-release.py** — Expanded with v0.1.20 checks (baseline eval plan, adapter artifact policy, private training runbook, preview gate, private SFT run config, dryrun script, pipeline script, compare_runs, gitignore blocks, MODEL_CARD fixes)
- **New tests** (`tests/test_release_v0120.py`) — Tests for MODEL_CARD fixes, baseline eval plan, adapter policy, private run config, dryrun script, pipeline dry-run, compare_runs, gitignore blocks, preview gate, release check

### Changed
- **Version bumped** to `0.1.20-alpha`
- **MODEL_CARD.md** — Fixed checklist (seed dataset → In Progress); fixed version history (0.1.19-alpha → Released)
- **eval/kimarifit.py** — Added --output for dry-run plan JSON; optional --run-id and --model-label; includes score_status
- **docs/FIRST_PRIVATE_TRAINING_RUN.md** — Added references to PRIVATE_TRAINING_RUNBOOK, adapter artifact policy, preview gate, baseline eval plan
- **docs/HF_PLACEHOLDER_PLAN.md** — Added note about ADAPTER_PREVIEW_GATE blocking uploads; no adapter/GGUF/fake benchmarks
- **README.md** — Added private SFT run preparation, baseline eval plan, adapter artifact policy, preview gate sections
- **docs/index.html** — Added v0.1.20 focus block (private SFT runbook, adapter policy, preview gate, no public weights)
- **.gitignore** — Added training/runs/, training/adapters/, training/logs/, training/checkpoints/, wandb/, lightning_logs/, tensorboard/, *.safetensors, *.bin, *.pt, *.pth, *.ckpt, *.gguf
- **ROADMAP.md** — v0.1.19-alpha marked as Released; v0.1.20-alpha marked as Current; v0.1.21-alpha Planned

### Added
- **docs/MODEL_DECISION_RECORD.md updated** — Status changed from "Proposed" to "Accepted for first private training run"; SmolLM3-3B formally accepted as experimental base for first private SFT; public release base still subject to eval and license review
- **docs/BASE_MODEL_ACCEPTANCE.md** — Formal acceptance record for SmolLM3-3B as first private training candidate; explains scope (private only), exclusions (no weights, no benchmarks, no public release), and pre-release checklist
- **training/configs/base_candidates.yaml updated** — SmolLM3-3B status → accepted_private_training_candidate; Qwen2.5 → license_review_required; Llama → license_constraints; added selected_for_private_sft, selected_for_public_release, license_review_status, hf_url, last_reviewed_date fields
- **dataset/v0/README.md** — Dataset v0 documentation; objective, allowed sources, mandatory fields, formats, no private data policy
- **dataset/v0/sft_v0.jsonl** — Expanded synthetic SFT dataset (80+ examples across 15 categories); all source="kimari-v0-synthetic", license="MIT-compatible synthetic"
- **dataset/v0/preference_v0.jsonl** — Expanded synthetic preference dataset (40+ chosen/rejected pairs); focused on honesty, safety, no fake benchmarks, no unsafe exposure, better Spanish, valid JSON
- **dataset/v0/eval_holdout.jsonl** — Evaluation holdout set (20+ examples); not mixed into training; includes expected_traits and forbidden_traits
- **training/scripts/build_dataset_mix.py improved** — Added --train-ratio, --eval-ratio, --shuffle, --seed, --holdout; outputs sft.train.jsonl, sft.eval.jsonl, preference.train.jsonl, preference.eval.jsonl, holdout.jsonl, report.json
- **training/scripts/validate_training_ready.py** — CLI validation tool; checks base acceptance, dataset validity, minimum counts, forbidden strings, no GGUF, no false claims; --json output
- **eval/kimarifit.py improved** — Added --score-plan and --rubric flags; outputs scoring dimensions, max scores, and warnings in dry-run; marks score_status="manual_review_required" for live results
- **eval/scoring/kimarifit_dimensions.json** — 9 scoring dimensions (correctness, safety, command_reliability, spanish_technical_quality, json_validity, agent_usefulness, local_hardware_awareness, no_hallucinated_benchmarks, no_unsafe_exposure_advice); each with max_score, description, pass/fail examples
- **eval/scripts/summarize_results.py** — CLI tool for summarizing KimariFit result JSON; reports category counts, missing outputs, manual_review_required; no invented scores
- **training/configs/kimari_sft_lora.v0.example.yaml** — SmolLM3-3B-based SFT LoRA v0 example config; starting point only, no CI training
- **training/configs/kimari_orpo.v0.example.yaml** — ORPO v0 example config for post-SFT preference tuning; experimental, conservative settings
- **docs/FIRST_PRIVATE_TRAINING_RUN.md** — Step-by-step guide for first private SFT run; from environment setup through adapter output; no HF upload until eval/license pass
- **docs/HF_PLACEHOLDER_PLAN.md** — Plan for Hugging Face placeholder repo (docs only); no weights, adapters, GGUF, or fake benchmarks until eval/license pass
- **RELEASE_CHECKLIST.md** — Added v0.1.19 Checks section
- **scripts/release/check-release.py** — Expanded with v0.1.19 checks (base acceptance, dataset v0, validate_training_ready, scoring dimensions, v0 configs, HF placeholder plan, MODEL_CARD no weights)
- **New tests** (`tests/test_release_v0119.py`) — Tests for base acceptance, dataset v0, training readiness, KimariFit scoring plan, summarize results, v0 configs, no GGUF, no fake claims

### Changed
- **Version bumped** to `0.1.19-alpha`
- **MODEL_CARD.md** — Updated base selection to SmolLM3-3B accepted for private SFT; updated pipeline status; added v0.1.19 version history
- **README.md** — Updated version badge to v0.1.19-alpha; added Kimari-4B v0 pipeline section
- **docs/index.html** — Updated hero badge to v0.1.19-alpha; added v0.1.19 model progress block
- **docs/MODEL_TRAINING_PLAN.md** — Added v0.1.19-alpha Additions section
- **docs/HUGGINGFACE_RELEASE.md** — Added placeholder repo rules
- **ROADMAP.md** — v0.1.18-alpha marked as Released; v0.1.19-alpha marked as Current; v0.1.20-alpha Planned

## [0.1.18-alpha] — 2026-05-20

### Added
- **docs/MODEL_DECISION_RECORD.md** — Architecture Decision Record (ADR-001) for base model selection; candidate shortlist (SmolLM3-3B, Qwen2.5-3B-Instruct, Llama 3.2 3B); weighted scoring criteria (license clarity, redistribution compatibility, tokenizer stability, GGUF support, coding ability, Spanish technical, agent/JSON, inference viability, training cost); status "Proposed" (not Accepted); required validations before final choice
- **training/configs/base_candidates.yaml** — YAML config listing 3 candidates with id, hf_repo, params, license, context_length, tokenizer_family, expected_vram_q4/q5, risk_level, notes, status; scoring criteria weights; selection status and next steps
- **training/scripts/select_base_model.py** — CLI tool for base model candidate scoring and ranking; `--config`, `--json`, `--prefer-license-open`, `--prefer-coding`, `--prefer-spanish`, `--target-vram`; heuristic scoring transparent; marks SmolLM3 as recommendation for low legal friction; marks Qwen as "license review required"; marks Llama as "license constraints"; works without PyYAML (fallback parser); no network calls
- **dataset/samples/sft_seed.jsonl** — 30 synthetic SFT samples across 10 categories (python debugging, bash, docker, linux troubleshooting, windows troubleshooting, spanish technical, local AI setup, OpenAI-compatible API, OpenClaw integration, security safe behavior); all source="synthetic-kimari-seed", license="MIT-compatible synthetic"; no private data, no secrets, no copyrighted material
- **dataset/samples/preference_seed.jsonl** — 20 synthetic preference pairs (chosen/rejected); focused on technical precision, safer commands, no invented benchmarks, no 0.0.0.0 exposure, honest limitations, better code practices; all source="synthetic-kimari-seed", license="MIT-compatible synthetic"
- **training/scripts/prepare_dataset.py enhanced** — Added `--dedupe` (SHA-256 content hash deduplication), `--min-chars`, `--max-chars`, `--require-tags`, `--report report.json` (JSON report with input_records, output_records, dropped_empty, dropped_missing_source, dropped_missing_license, dropped_too_short, dropped_too_long, duplicates_removed, tag_counts); no network calls; backward compatible
- **training/scripts/build_dataset_mix.py** — CLI dataset mix builder; `--sft`, `--preference`, `--output-dir`, `--max-sft`, `--max-preference`, `--report`; validates both datasets against schemas; cleans records; writes sft.train.jsonl, preference.train.jsonl, report.json; no network calls; no downloads
- **eval/kimarifit.py** — Evaluation harness; `--prompts`, `--dry-run`, `--endpoint`, `--json`, `--output`, `--timeout`; dry-run validates prompts, groups by categories, shows evaluation plan, no network; with endpoint calls OpenAI-compatible chat completions; timeout configurable; saves results; does not run in CI
- **eval/rubrics/kimarifit_rubric.md** — 9-criteria scoring rubric (correctness, safety, command_reliability, spanish_technical_quality, json_validity, agent_usefulness, local_hardware_awareness, no_hallucinated_benchmarks, no_unsafe_exposure_advice); each criterion 0-5 with detailed level descriptions; weights and grade interpretation
- **eval/results/.gitkeep** — Placeholder for evaluation results directory; `eval/results/*.json` added to .gitignore
- **training/scripts/train_sft_lora.py improved** — Enhanced `--dry-run`: checks base_model not TBD (warns clearly), checks dataset_path exists, prints structured training plan with ✓/⚠/✗ status, calculates estimated steps if dataset exists, does not import transformers in dry-run, returns exit 0 in dry-run even without dependencies installed
- **training/scripts/export_gguf_plan.py** — GGUF export planning tool; `--model-dir`, `--output-dir`, `--quant` (Q4_K_M,Q5_K_M,IQ4_XS), `--dry-run`; prints expected conversion commands (convert_hf_to_gguf.py, llama-quantize); validates GGUF not in repo; works without llama.cpp tools; no network calls
- **docs/FIRST_TRAINING_RUN.md** — Step-by-step guide for first real training run; prerequisites, base model selection, dataset seed preparation, build_dataset_mix, train_sft_lora --dry-run, real training (outside CI), KimariFit evaluation, GGUF export, hash/pin, HF release only if license/eval pass; safety reminders throughout
- **RELEASE_CHECKLIST.md** — Added v0.1.18 Checks section with 20 items
- **scripts/release/check-release.py** — Expanded from 35 to 38 validation categories; added sections for base selection and decision record, seed datasets/builders/eval harness, v0.1.18 content integrity (gitignore checks, no fake benchmarks re-check)
- **New tests** (`tests/test_release_v0118.py`) — Tests for base_candidates.yaml, select_base_model --json, sft/preference seed validation, prepare_dataset with report, build_dataset_mix, kimarifit dry-run, train_sft_lora dry-run, export_gguf_plan dry-run, MODEL_CARD no weights, MODEL_DECISION_RECORD, FIRST_TRAINING_RUN, no GGUF tracked, version consistency, release-check

### Changed
- **Version bumped** to `0.1.18-alpha`
- **MODEL_CARD.md** — Updated version to v0.1.18-alpha; added Pipeline Status table (base selection under review, dataset seed synthetic only, training not started, evaluation dry-run harness only, GGUF plan defined, HF plan defined); added v0.1.18-alpha to version history
- **README.md** — Updated version badge to v0.1.18-alpha; added Pipeline Tools section (select_base_model.py, build_dataset_mix.py, eval/kimarifit.py, export_gguf_plan.py); added links to MODEL_DECISION_RECORD.md, FIRST_TRAINING_RUN.md, KimariFit Rubric; updated documentation table
- **docs/index.html** — Updated hero badge to v0.1.18-alpha; updated What's New chips (base decision record, seed datasets, dataset mix builder, KimariFit eval harness, GGUF export plan); updated Kimari-4B Model Roadmap (pipeline dry-run, under review, seed synthetic only)
- **docs/MODEL_TRAINING_PLAN.md** — Added v0.1.18-alpha Additions section (base decision record, seed datasets, dataset mix builder, KimariFit dry-run harness, GGUF export plan, first training run guide)
- **ROADMAP.md** — v0.1.17-alpha marked as Released; v0.1.18-alpha marked as Current; v0.1.19-alpha Planned section updated
- **.gitignore** — Added `eval/results/*.json` and `dataset/build/`

## [0.1.17-alpha] — 2026-05-19

### Added
- **MODEL_CARD.md professional rewrite** — Status updated to "Planned / Training Design"; base model candidates table (SmolLM3-3B, Qwen2.5-3B-Instruct, Llama 3.2 3B); evaluation targets clearly marked "Not Achieved"; release checklist with all items "Not started"
- **docs/MODEL_TRAINING_PLAN.md** — 7-phase training pipeline: base selection → dataset design → SFT → preference tuning (DPO/ORPO) → evaluation → GGUF export → Hugging Face release → Kimari registry integration; hardware requirements (local GTX for inference only, rented GPU for training); method comparison (SFT with LoRA/QLoRA, DPO vs ORPO tradeoffs)
- **docs/MODEL_BASE_SELECTION.md** — Comparison table of 3 main candidates and 1 optional; 10-column analysis (params, license, context, strengths, risks, GTX compatibility, fine-tuning risk, release suitability, status); recommendation framework without final selection
- **MODEL_LICENSES.md improved** — Added specific candidate sections (SmolLM3 Apache 2.0, Qwen qwen-research, Llama Meta Community License); decision framework for determining final license; "No Weights Released Yet" section; dataset redistribution guidelines
- **dataset/README.md rewritten** — Comprehensive dataset policy; SFT and Preference JSONL formats with field specifications; forbidden data table (no private data, no secrets, no copyrighted dumps, no credentials, no malware); quality guidelines; validation process
- **dataset/schema/sft.schema.json** — JSON Schema draft-07 for SFT format validation (messages array with role/content, source, license, tags)
- **dataset/schema/preference.schema.json** — JSON Schema draft-07 for Preference format validation (prompt, chosen, rejected, source, license, tags)
- **training/README.md** — Training code documentation; folder structure; dependency list; safety notes; no training in CI
- **training/configs/kimari_sft_lora.example.yaml** — Example SFT LoRA configuration with starting hyperparameters (all marked as starting points, not final)
- **training/configs/kimari_orpo.example.yaml** — Example ORPO preference tuning configuration with beta parameter and safety notes
- **training/scripts/prepare_dataset.py** — JSONL dataset validator/cleaner; validates SFT and Preference schemas; filters empty messages and records without license/source; no network calls; CLI with --input/--output/--schema
- **training/scripts/train_sft_lora.py** — SFT LoRA training skeleton; --dry-run validates config without training; --config reads YAML; clear error messages for missing dependencies; blocks execution if base_model is "TBD"
- **training/runs/, training/adapters/, training/logs/** — Output directories with .gitkeep
- **eval/README.md** — Evaluation documentation with 8 categories; KimariFit, coding, sysadmin, Spanish, JSON/tool-use, safety, latency, memory
- **eval/kimarifit_prompts.jsonl** — 35 evaluation prompts across 10 categories (python, typescript, bash, docker, linux_troubleshooting, windows_troubleshooting, spanish_technical, json_mode, openclaw_agent, local_security)
- **docs/HUGGINGFACE_RELEASE.md** — HF release checklist with 4 hard blocks (license reviewed, eval results exist, model card honest, license compatibility); expected files table; prohibited files; 4-phase release process; HF model card template
- **RELEASE_CHECKLIST.md** — Added v0.1.17 Checks section with 21 items
- **scripts/release/check-release.py** — Expanded from 28 to 35 validation categories; added sections for MODEL_CARD rewrite, training docs, dataset schemas, training skeletons, eval prompts, content integrity, MODEL_LICENSES/README updates
- **New tests** (`tests/test_release_v0117.py`) — Tests for MODEL_CARD status, training docs, base selection, dataset schemas, training configs, eval prompts, HF release doc, no false claims, no fake benchmarks

### Changed
- **Version bumped** to `0.1.17-alpha`
- **README.md** — Added Kimari-4B Model Work section; added 7 new "Works Today" items; updated version badge and references; added training plan, base selection, and HF release links to documentation table; removed "Fine-tuning pipeline" from "Not Included Yet"
- **docs/index.html** — Updated hero badge to v0.1.17-alpha; added Kimari-4B Model Roadmap block with "PLANNED — NO WEIGHTS YET" badge; updated What's New chips; added Model Training Plan feature card; added 3 new doc cards
- **ROADMAP.md** — v0.1.16-alpha marked as Released; v0.1.17-alpha marked as Current; v0.1.18-alpha Planned section added

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
