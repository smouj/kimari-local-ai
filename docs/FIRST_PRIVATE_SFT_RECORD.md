# First Private SFT Run Record — Registration Template

> **Document Type:** Private SFT run record specification  
> **Version:** v0.1.22-alpha  
> **Date:** 2026-05-23  
> **Status:** Active — governs how a first private SFT run is registered without committing sensitive outputs

---

## Purpose

Every private supervised fine-tuning (SFT) run must be registered in a **run record** — a structured document that captures what was trained, how, where, and under what constraints. The run record provides:

1. **Traceability** — A durable, timestamped record that a training run occurred, what inputs it used, and what it produced.
2. **Reproducibility** — Enough metadata to reconstruct the training conditions (base model, dataset, config, hardware) without exposing the outputs.
3. **Audit trail** — A verifiable chain from dataset build hash through training config to evaluation result, allowing future reviewers to confirm that no steps were skipped or altered.
4. **Controlled visibility** — The run record is designed so that a **sanitized subset** can be committed to the repository (for transparency and history) while all sensitive artifacts (weights, raw eval outputs, logs) remain strictly local.

The run record does **not** replace the adapter manifest (`MANIFEST.yaml`), the eval summary, or the comparison summary. It is a **top-level registration** that ties those artifacts together and establishes the context in which they were produced.

> **Core principle:** The run record exists to prove the run happened and to describe it — never to distribute its outputs. No weights are published. No secrets are exposed. The preview gate stays BLOCKED.

---

## Run Record Fields

Each field below must be present in the private SFT run record. Fields marked **LOCAL ONLY** must never appear in any committed version of this document.

### 1. `run_id`

A unique identifier for this training run.

**Format:** `kimari-<base>-<method>-<version>-<access>-<sequence>`

| Component | Value | Notes |
|-----------|-------|-------|
| `<base>` | `smollm3` | Short name of the base model |
| `<method>` | `sft` | Training method |
| `<version>` | `v0` | Dataset/config version |
| `<access>` | `private` | Always `private` for first-run records |
| `<sequence>` | `001` | Zero-padded sequence number |

**Example:** `kimari-smollm3-sft-v0-private-001`

**Generation rule:** The `run_id` is set in the run config (`training/configs/private_sft_run.v0.yaml`) before training begins. It must not change after the run starts. If the run is re-executed, increment the sequence number (e.g., `002`).

---

### 2. Base Model

The pretrained model from which the adapter was derived.

| Field | Value |
|-------|-------|
| **Model ID** | `HuggingFaceTB/SmolLM3-3B` |
| **License** | Apache 2.0 |
| **Acceptance record** | `docs/BASE_MODEL_ACCEPTANCE.md` |
| **Scope** | Private SFT candidate only — no public distribution authorized |

---

### 3. Dataset Build Hash / Report

Reference to the dataset build that was used as training input.

| Field | Description |
|-------|-------------|
| **Build directory** | `dataset/build/kimari-v0/` |
| **Build report** | `dataset/build/kimari-v0/report.json` |
| **SHA-256 of report** | Compute and record: `sha256sum dataset/build/kimari-v0/report.json` |
| **Builder script** | `training/scripts/build_dataset_mix.py` |
| **Build command** | `python training/scripts/build_dataset_mix.py --sft dataset/v0/sft_v0.jsonl --preference dataset/v0/preference_v0.jsonl --holdout dataset/v0/eval_holdout.jsonl --output-dir dataset/build/kimari-v0 --shuffle --seed 42 --report` |

The dataset build hash ties the run record to an exact, reproducible snapshot of the training data. If the dataset is rebuilt (different seed, additional records, corrected entries), the hash will change and a new `run_id` sequence should be used.

---

### 4. Training Config

Reference to the training configuration used for this run.

| Field | Description |
|-------|-------------|
| **SFT config** | `training/configs/kimari_sft_lora.v0.example.yaml` |
| **Run config** | `training/configs/private_sft_run.v0.yaml` |
| **Key settings** | `base_model`, `lora_rank`, `lora_alpha`, `learning_rate`, `num_train_epochs`, `batch_size`, `dataset_path` |
| **Config hash** | Compute and record: `sha256sum training/configs/kimari_sft_lora.v0.example.yaml` |

The training config is already in the repository. The hash provides a tamper-evident reference: if the config is modified after the run, the hash will not match.

---

### 5. Hardware Summary

Record the hardware environment used for training.

| Field | Example Value | How to Obtain |
|-------|--------------|---------------|
| **GPU** | e.g., `NVIDIA RTX 3090` | `nvidia-smi --query-gpu=name --format=csv,noheader` |
| **VRAM** | e.g., `24576 MiB` | `nvidia-smi --query-gpu=memory.total --format=csv,noheader` |
| **CUDA version** | e.g., `12.1` | `nvcc --version` or `nvidia-smi` (driver/runtime version) |
| **Driver version** | e.g., `535.104.05` | `nvidia-smi --query-gpu=driver_version --format=csv,noheader` |
| **OS** | e.g., `Ubuntu 22.04` | `uname -a` |
| **Python version** | e.g., `3.10.12` | `python --version` |
| **PyTorch version** | e.g., `2.1.0+cu121` | `python -c "import torch; print(torch.__version__)"` |

> **Note:** These are example values. Record the actual values from the training machine at the time of the run.

---

### 6. Runtime Summary

Timestamps and duration for the training run.

| Field | Format | Example |
|-------|--------|---------|
| **Start time** | ISO 8601 UTC | `2026-05-23T14:30:00Z` |
| **End time** | ISO 8601 UTC | `2026-05-23T18:45:00Z` |
| **Duration** | `HH:MM:SS` | `04:15:00` |

Record these from the training logs or the `trainer_state.json` produced by the training framework. Use UTC timestamps to avoid timezone ambiguity.

---

### 7. Adapter Manifest Local Path — **LOCAL ONLY**

The adapter manifest is generated after training by `create_adapter_manifest.py`.

| Field | Value |
|-------|-------|
| **Manifest path** | `training/adapters/kimari-smollm3-sft-v0/MANIFEST.yaml` |
| **Commitment status** | **LOCAL ONLY — never committed** |

The manifest contains references to the adapter directory, which includes weight files. While the manifest itself can be sanitized and committed (see `docs/PRIVATE_RUN_ARTIFACTS.md`), the local absolute path to the manifest must never appear in a committed document. In the sanitized version, replace absolute paths with repo-relative paths.

> **⚠️ This path must NOT appear in any committed version of this run record.**

---

### 8. Eval Summary Path

The sanitized eval summary produced by `create_eval_summary.py`.

| Field | Value |
|-------|-------|
| **Sanitized summary** | `eval/results/adapter-smollm3-sft-v0-q4km-summary.json` |
| **Generator script** | `eval/scripts/create_eval_summary.py` |
| **Template** | `eval/templates/eval_summary.template.json` |
| **Commitment status** | May be committed after sanitization (no prompts, no responses, no local paths) |

The eval summary contains only aggregate metadata: `run_id`, `model_label`, `kimari_version`, `prompt_count`, `category_counts`, `score_status`, `manual_review_required`, and `safety_regression_detected`. It is generated by `create_eval_summary.py`, which strips all `prompt` and `response` fields automatically.

**Raw eval output** (e.g., `eval/results/adapter-smollm3-sft-v0-q4km.json`) is **LOCAL ONLY** and must never be committed. See `docs/PRIVATE_EVAL_RESULTS_POLICY.md`.

---

### 9. Compare Summary Path

The comparison summary showing adapter vs. baseline results at the category level.

| Field | Value |
|-------|-------|
| **Compare summary** | `eval/results/comparison-sft-v0-vs-baseline-summary.json` |
| **Generator script** | `eval/scripts/compare_runs.py` |
| **Baseline reference** | `eval/results/baseline-smollm3-q4km.json` |
| **Commitment status** | May be committed after sanitization (no prompt content, no raw responses, no local paths) |

The compare summary contains only category-level aggregates: "improved," "regressed," or "unchanged" per category, plus the overall improvement flag and safety regression flag. No individual prompt text or model response text is included.

**Raw comparison output** is **LOCAL ONLY** and must never be committed.

---

### 10. Preview Gate State

The preview gate state for this run.

| Field | Value |
|-------|-------|
| **`preview_gate_state`** | **`BLOCKED`** |
| **Reason** | First private SFT run — no evaluation review or gate transition has been performed |

The preview gate state is **always `BLOCKED`** for a first private SFT run. This is the default state defined in `docs/ADAPTER_PREVIEW_GATE.md`. No automatic transitions are possible. The adapter cannot move to `PENDING` until a human explicitly verifies:

1. License is verified for the current use
2. No secrets or data issues in the adapter
3. Adapter size is recorded
4. Adapter hash is recorded

**The gate does not advance as a side effect of recording the run.** Recording the run is documentation, not a release action.

---

### 11. Blocked Actions

The following actions are **explicitly blocked** for this private SFT run. These blocks are absolute and cannot be overridden by the run record alone.

| # | Blocked Action | Why It Is Blocked |
|---|---------------|-------------------|
| 1 | **Upload to Hugging Face** | No weights may be uploaded to any public or private HF repository. `hf_upload_allowed: false`. |
| 2 | **Public release** | No distribution of the adapter, merged model, or GGUF exports. `public_release_allowed: false`. |
| 3 | **Claim benchmark scores** | No public claims about model performance until formal evaluation is completed and verified. |
| 4 | **Share adapter externally** | No sharing with anyone outside the project until the preview gate advances to `APPROVED_FOR_PRIVATE_TESTING`. |
| 5 | **Distribute GGUF quantizations** | No quantized model files may be distributed via any channel. |
| 6 | **Commit raw eval outputs** | Files containing prompt text or model response text must never be committed to Git. |
| 7 | **Commit adapter weights** | `.safetensors`, `.bin`, `.pt`, `.gguf` files must never be committed to Git. |
| 8 | **Publish as "Kimari-4B"** | Kimari-4B is NOT published. No public reference to this run constitutes a release. |

> **These blocks are non-negotiable for private runs.** Only the `ADAPTER_PREVIEW_GATE` can lift them, and only through explicit human decisions at each transition.

---

### 12. What Can Be Committed

Only the following **sanitized metadata** from the run record may be committed to the repository:

| Artifact | Conditions for Commit |
|----------|----------------------|
| **Run record (this document)** | Sanitized version only — remove all LOCAL ONLY fields, absolute paths, and any hardware-specific identifying information |
| **MANIFEST.yaml** | Must sanitize: remove all absolute paths, replace with repo-relative paths; verify no weight data is present; confirm `preview_gate_state: BLOCKED` |
| **eval_summary.json** | Must use `create_eval_summary.py` output — strips prompts, responses, and local paths automatically |
| **compare_summary.json** | Must sanitize: no private prompt content, no raw responses, no local paths — only category-level aggregates |
| **adapter_config.json** | Must sanitize: replace absolute `base_model_name_or_path` with HuggingFace model ID |
| **all_results.json** | Training metrics only — verify no sensitive content before committing |
| **Training config (`.yaml`)** | Already in repository; no sanitization needed |
| **Dataset build report hash** | The SHA-256 hash string of `report.json` may be recorded; the report itself is already in the repo |

**Pre-commit verification** (from `docs/PRIVATE_RUN_ARTIFACTS.md`):

```bash
# Check staged files for sensitive content
git diff --cached | rg -i 'hf_[a-zA-Z]'        # No HF tokens
git diff --cached | rg '/workspace/'             # No RunPod paths
git diff --cached | rg '/home/[a-z]'             # No home directory paths
git diff --cached | rg '\.safetensors'           # No weight files
git diff --cached | rg '\.bin'                   # No binary files
git diff --cached | rg '\.pt'                    # No PyTorch files
git diff --cached | rg 'checkpoint-'             # No checkpoints
git diff --cached | rg '"prompt"'                # No raw prompts
git diff --cached | rg '"response"'              # No raw responses
```

---

### 13. What Must Remain Local

The following artifacts must **never** leave the training machine or be committed to any repository:

| Artifact | Location Pattern | Why It Must Stay Local |
|----------|-----------------|----------------------|
| **LoRA adapter weights** | `training/adapters/**/*.safetensors` | Proprietary binary weight data — not for distribution |
| **Legacy weight files** | `training/adapters/**/*.bin` | Same concerns as safetensors |
| **Training checkpoints** | `training/adapters/**/checkpoint-*/` | Intermediate optimizer states and weight snapshots |
| **Optimizer states** | `training/adapters/**/*.pt` | `optimizer.pt`, `rng_state.pth`, `scheduler.pt` — training state only |
| **Merged model files** | `training/adapters/*-merged/` | Full model weights after adapter merge — very large |
| **GGUF exports** | `models/kimari-*.gguf` | Quantized model files for inference — large binary |
| **Raw eval outputs** | `eval/results/*-raw.json` | Contains full model responses with potentially private prompts |
| **Raw comparison outputs** | `eval/results/comparison-*-raw.json` | May contain prompt text or response text |
| **TensorBoard logs** | `training/adapters/**/runs/` | Binary event files, not useful in Git |
| **WandB local cache** | `wandb/` | May contain experiment data or API keys |
| **Training data copies** | `training/adapters/**/*.jsonl` | License restrictions; data should come from `dataset/build/` |
| **Heavy log files** | `training/adapters/**/*.log` | Potentially large, may contain sensitive information |
| **Model weights (base)** | HuggingFace cache or download directory | Base model weights are never committed — downloaded at training time |

> **When in doubt, leave it out.** If you are unsure whether an artifact can be committed, do not commit it. Seek review first. See `docs/PRIVATE_RUN_ARTIFACTS.md` for the full classification.

---

## Run Record Template

Below is the canonical template for the first private SFT run record. Copy this template and fill in the actual values after the training run completes.

```yaml
# FIRST_PRIVATE_SFT_RUN_RECORD
# This record registers the first private SFT run.
# It does NOT authorize any distribution or publication.

run_id: kimari-smollm3-sft-v0-private-001
record_version: "1.0"
record_date: "YYYY-MM-DD"              # Date this record was created

base_model:
  model_id: "HuggingFaceTB/SmolLM3-3B"
  license: "Apache 2.0"
  acceptance_record: "docs/BASE_MODEL_ACCEPTANCE.md"

dataset_build:
  build_dir: "dataset/build/kimari-v0/"
  report_path: "dataset/build/kimari-v0/report.json"
  report_sha256: ""                     # Fill: sha256sum dataset/build/kimari-v0/report.json
  builder_script: "training/scripts/build_dataset_mix.py"

training_config:
  sft_config: "training/configs/kimari_sft_lora.v0.example.yaml"
  run_config: "training/configs/private_sft_run.v0.yaml"
  sft_config_sha256: ""                # Fill: sha256sum of the SFT config

hardware:                               # LOCAL ONLY — remove absolute paths before committing
  gpu: ""                              # e.g., "NVIDIA RTX 3090"
  vram: ""                             # e.g., "24576 MiB"
  cuda_version: ""                     # e.g., "12.1"
  driver_version: ""                   # e.g., "535.104.05"
  os: ""                               # e.g., "Ubuntu 22.04"
  python_version: ""                   # e.g., "3.10.12"
  pytorch_version: ""                  # e.g., "2.1.0+cu121"

runtime:
  start_time: ""                       # ISO 8601 UTC, e.g., "2026-05-23T14:30:00Z"
  end_time: ""                         # ISO 8601 UTC, e.g., "2026-05-23T18:45:00Z"
  duration: ""                         # HH:MM:SS, e.g., "04:15:00"

adapter_manifest_local_path: ""        # LOCAL ONLY — never commit this field
                                         # e.g., "training/adapters/kimari-smollm3-sft-v0/MANIFEST.yaml"

eval_summary_path: "eval/results/adapter-smollm3-sft-v0-q4km-summary.json"
compare_summary_path: "eval/results/comparison-sft-v0-vs-baseline-summary.json"

preview_gate_state: BLOCKED            # Always BLOCKED for private runs

blocked_actions:
  hf_upload: true                      # No upload to Hugging Face
  public_release: true                 # No public distribution
  benchmark_claims: true               # No public benchmark claims
  external_sharing: true               # No sharing outside the project
  gguf_distribution: true              # No quantized model distribution
  commit_raw_eval: true                # No raw eval outputs in Git
  commit_weights: true                 # No weight files in Git
  publish_kimari_4b: true              # Kimari-4B is NOT published

can_commit:
  - "Sanitized run record (this document, with LOCAL ONLY fields removed)"
  - "Sanitized MANIFEST.yaml (no absolute paths, preview_gate_state: BLOCKED)"
  - "eval_summary.json (generated by create_eval_summary.py)"
  - "compare_summary.json (category-level aggregates only)"
  - "adapter_config.json (with HuggingFace model ID replacing absolute paths)"
  - "all_results.json (training metrics only, verify no sensitive content)"
  - "Training config YAML files (already in repository)"

must_remain_local:
  - "adapter_model.safetensors — LoRA adapter weights"
  - "adapter_model.bin — Legacy weight format"
  - "checkpoint-*/ — Training checkpoints"
  - "optimizer.pt, rng_state.pth, scheduler.pt — Optimizer states"
  - "*-merged/ — Merged model weights"
  - "kimari-*.gguf — GGUF quantized exports"
  - "*-raw.json — Raw eval and comparison outputs"
  - "runs/ — TensorBoard event files"
  - "wandb/ — WandB local cache"
  - "**/*.log — Training log files"
```

---

## Safety Rules

These rules are absolute for any private SFT run record:

| # | Rule |
|---|------|
| 1 | **No real training is done in CI.** Training requires GPU hardware. CI only validates with `--dry-run`. |
| 2 | **No weights are published.** Adapter weights, merged models, and GGUF exports stay local. |
| 3 | **Preview gate stays BLOCKED.** The gate does not advance automatically. No run record field overrides the gate. |
| 4 | **No HF uploads.** `hf_upload_allowed: false` is permanent for private runs. |
| 5 | **Kimari-4B is NOT published.** This run record does not constitute a release. |
| 6 | **No secrets or tokens.** No `hf_` strings, API keys, passwords, or authentication tokens in any committed artifact. |
| 7 | **No raw eval outputs committed.** Only summaries produced by `create_eval_summary.py` may be committed. |
| 8 | **No absolute paths committed.** Replace `/workspace/...`, `/home/...` with repo-relative paths. |
| 9 | **No invented scores.** `score_status` is always `"manual_review_required"` until human review. |
| 10 | **Private runs only.** Nothing goes public without gate approval through `docs/ADAPTER_PREVIEW_GATE.md`. |

---

## Related Documents

| Document | Relationship |
|----------|-------------|
| [PRIVATE_RUN_ARTIFACTS.md](PRIVATE_RUN_ARTIFACTS.md) | Full classification of what stays local vs. what can be committed |
| [ADAPTER_PREVIEW_GATE.md](ADAPTER_PREVIEW_GATE.md) | State machine governing adapter release — all adapters start BLOCKED |
| [ADAPTER_ARTIFACT_POLICY.md](ADAPTER_ARTIFACT_POLICY.md) | Naming conventions, hash recording, and artifact commitment policy |
| [FIRST_PRIVATE_TRAINING_RUN.md](FIRST_PRIVATE_TRAINING_RUN.md) | Step-by-step guide for the first private SFT training run |
| [PRIVATE_TRAINING_RUNBOOK.md](PRIVATE_TRAINING_RUNBOOK.md) | Detailed runbook covering environment setup through ORPO decision |
| [PRIVATE_SFT_EXECUTION_CHECKLIST.md](PRIVATE_SFT_EXECUTION_CHECKLIST.md) | Pre-flight checklist that must be completed before training |
| [PRIVATE_EVAL_RESULTS_POLICY.md](PRIVATE_EVAL_RESULTS_POLICY.md) | Policy for what eval results can and cannot be committed |
| [BASE_MODEL_ACCEPTANCE.md](BASE_MODEL_ACCEPTANCE.md) | Formal acceptance record authorizing SmolLM3-3B for private training |
| [MODEL_HASHING.md](MODEL_HASHING.md) | SHA-256 hash procedures for model and config files |
| [PRIVATE_RUN_FAILURES.md](PRIVATE_RUN_FAILURES.md) | Failure modes and troubleshooting for private training runs |
| [BASELINE_EVAL_PLAN.md](BASELINE_EVAL_PLAN.md) | Baseline evaluation of SmolLM3-3B before fine-tuning |
| [HUGGINGFACE_RELEASE.md](HUGGINGFACE_RELEASE.md) | Full release process for when public release is authorized |

---

*This document specifies how to register a first private SFT run without committing sensitive outputs. No weights are published. The preview gate stays BLOCKED. No HF uploads. Kimari-4B is NOT published. This is for PRIVATE runs only — nothing goes public without gate approval.*
