# Private Run Artifacts — What Stays Local vs What Can Be Committed

> **Document Type:** Artifact classification guide for private training runs
> **Version:** v0.1.22-alpha
> **Date:** 2026-05-23
> **Status:** Active — governs what training artifacts may leave the training environment

---

## Purpose

This document provides a clear, unambiguous classification of every artifact produced during a private SFT training run. It defines what must stay on the training machine, what may be committed to the repository (with conditions), and how to review artifacts before committing.

**When in doubt, leave it out.** If you are unsure whether an artifact can be committed, do not commit it. Seek review first.

---

## ⚠️ Safety Principle

**No weights, no private data, no raw outputs, no sensitive paths in Git.**

Training artifacts exist on a spectrum from "safe to commit" (metadata, configs) to "absolutely never commit" (adapter weights, optimizer states, raw eval outputs). This document classifies every known artifact type.

---

## Files That Stay Local Only — NEVER Commit

These artifacts must **never** be committed to the Git repository. They must stay on the training machine or in private backup storage.

| Artifact | Location Pattern | Why It Must Stay Local | Gitignore Pattern |
|----------|-----------------|----------------------|-------------------|
| **`adapter_model.safetensors`** | `training/adapters/**/*.safetensors` | Binary LoRA weight data — proprietary, large, not for distribution | `training/adapters/**/*.safetensors` |
| **`adapter_model.bin`** | `training/adapters/**/*.bin` | Legacy weight format — same concerns as safetensors | `training/adapters/**/*.bin` |
| **Training checkpoints** | `training/adapters/**/checkpoint-*/` | Intermediate optimizer states and weight snapshots — large, redundant | `training/adapters/**/checkpoint-*/` |
| **Optimizer states** | `training/adapters/**/*.pt` | `optimizer.pt`, `rng_state.pth`, `scheduler.pt` — training state only | `training/adapters/**/*.pt` |
| **`training_args.bin`** | `training/adapters/**/*.bin` | Binary training arguments — not human-readable, redundant with config | `training/adapters/**/*.bin` |
| **Raw eval outputs** | `eval/results/*-raw.json` | Contains full model responses with potentially private prompts and sensitive outputs | `eval/results/*-raw.json` |
| **TensorBoard logs** | `training/adapters/**/runs/` | Binary event files, not useful in Git, viewable locally | `training/adapters/**/runs/` |
| **WandB local cache** | `wandb/` | May contain experiment data, API keys, or public dashboard references | `wandb/` |
| **Scheduler states** | `training/adapters/**/*.pt` | Training state not needed post-training | (covered by `**/*.pt`) |
| **Merged model files** | `training/adapters/*-merged/` | Full model weights after adapter merge — very large | `training/adapters/*-merged/` |
| **GGUF exports** | `models/kimari-*.gguf` | Quantized model files for inference — large binary | `models/kimari-*.gguf` |
| **Training data copies** | `training/adapters/**/*.jsonl` | License restrictions; data should come from `dataset/build/` | `training/adapters/**/*.jsonl` |
| **Heavy log files** | `training/adapters/**/*.log` | Potentially large, not useful for repository consumers | `training/adapters/**/*.log` |

---

## Files That CAN Be Committed — With Sanitization

These artifacts **may** be committed to the repository, but only after meeting the specified conditions. Each has a sanitization requirement.

### MANIFEST.yaml

| Field | Conditions |
|-------|-----------|
| `adapter_name` | ✅ Always safe — just a name string |
| `base_model` | ✅ Always safe — HuggingFace model ID |
| `method` | ✅ Always safe — "sft" or "orpo" |
| `lora_config` | ✅ Always safe — hyperparameters only |
| `training_config` | ✅ Always safe — repo-relative path |
| `dataset_build` | ✅ Always safe — repo-relative path |
| `training_date` | ✅ Always safe — date string |
| `status` | ✅ Always safe — "private" / "pending_preview" |
| `preview_gate_state` | ✅ Always safe — must be "BLOCKED" |
| `hashes` | ✅ Always safe — SHA-256 hash strings only |
| **Local absolute paths** | ❌ **MUST BE REMOVED** — replace `/workspace/...`, `/home/user/...` with relative paths |
| **Weight data** | ❌ **MUST NOT BE PRESENT** — no binary data in manifest |

**Sanitization process:**

```bash
# Copy and sanitize
cp training/adapters/kimari-smollm3-sft-v0/MANIFEST.yaml /tmp/MANIFEST_sanitized.yaml

# Remove absolute paths
sed -i 's|/workspace/kimari-local-ai/||g' /tmp/MANIFEST_sanitized.yaml
sed -i 's|/home/[^/]*/kimari-local-ai/||g' /tmp/MANIFEST_sanitized.yaml

# Verify no sensitive content remains
rg '/workspace' /tmp/MANIFEST_sanitized.yaml   # Should find nothing
rg '/home/' /tmp/MANIFEST_sanitized.yaml       # Should find nothing
rg 'hf_' /tmp/MANIFEST_sanitized.yaml          # Should find no tokens
rg 'secret' /tmp/MANIFEST_sanitized.yaml       # Should find no secrets
```

### eval_summary.json

| Field | Conditions |
|-------|-----------|
| `run_id` | ✅ Always safe |
| `model_label` | ✅ Always safe |
| `kimari_version` | ✅ Always safe |
| `prompt_count` | ✅ Always safe — aggregate count only |
| `category_counts` | ✅ Always safe — category names and counts |
| `score_status` | ✅ Always safe — must be "manual_review_required" |
| `manual_review_required` | ✅ Always safe — boolean |
| `safety_regression_detected` | ✅ Always safe — boolean |
| **`prompt`** | ❌ **MUST BE STRIPPED** — eval prompts may contain proprietary or sensitive instructions |
| **`response`** | ❌ **MUST BE STRIPPED** — model responses may contain real data, paths, or credentials |
| **Local paths** | ❌ **MUST BE REMOVED** — no filesystem paths |
| **Invented scores** | ❌ **MUST NOT BE ADDED** — use `create_eval_summary.py` which never invents scores |

**Sanitization process:**

```bash
# Use the dedicated script — it strips prompts, responses, and local paths
python eval/scripts/create_eval_summary.py \
    --input eval/results/adapter-smollm3-sft-v0-q4km.json \
    --output eval/results/adapter-smollm3-sft-v0-q4km-summary.json
```

### compare_summary.json

| Field | Conditions |
|-------|-----------|
| Category-level comparisons | ✅ Safe — aggregate "improved/regressed/unchanged" per category |
| Overall improvement flag | ✅ Safe — boolean |
| Safety regression flag | ✅ Safe — boolean |
| **Private prompt content** | ❌ **MUST BE STRIPPED** — no prompt text in comparisons |
| **Raw model responses** | ❌ **MUST BE STRIPPED** — no response text |
| **Local paths** | ❌ **MUST BE REMOVED** — no filesystem paths |

**Sanitization process:**

```bash
# Manually review and strip private content
# Ensure only category-level aggregates remain
# Remove any "prompt" or "response" fields
# Remove any absolute paths
```

### adapter_config.json

| Field | Conditions |
|-------|-----------|
| `r`, `lora_alpha`, `lora_dropout` | ✅ Always safe — hyperparameters |
| `target_modules` | ✅ Always safe — module names |
| `task_type` | ✅ Always safe — "CAUSAL_LM" |
| `base_model_name_or_path` | ⚠️ **Check** — replace absolute paths with HuggingFace model IDs |

---

## Pre-Commit Review Checklist

Before committing any artifact from a private training run, verify **every** item:

- [ ] **No weight files** — no `.safetensors`, `.bin`, `.pt`, `.gguf` files in the commit
- [ ] **No checkpoints** — no `checkpoint-*/` directories in the commit
- [ ] **No raw eval outputs** — no files containing `prompt` or `response` fields with actual content
- [ ] **No absolute paths** — no `/workspace/`, `/home/`, `/usr/`, or any machine-specific paths
- [ ] **No HF tokens** — no `hf_` strings anywhere in the committed files
- [ ] **No API keys** — no `api_key`, `token`, `secret`, `password` strings
- [ ] **No private prompts** — eval summaries must use `create_eval_summary.py` output
- [ ] **No invented scores** — `score_status` must be `"manual_review_required"` until human review
- [ ] **Gate state is BLOCKED** — manifest must have `preview_gate_state: BLOCKED`
- [ ] **No HF upload allowed** — manifest must have `hf_upload_allowed: false`
- [ ] **No public release allowed** — manifest must have `public_release_allowed: false`
- [ ] **No user data** — no names, emails, internal URLs, or identifying information
- [ ] **Only repo-relative paths** — all paths use relative references from repo root

### Quick verification commands

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

# Verify only expected files are staged
git diff --cached --name-only
```

---

## What Happens If You Accidentally Commit

If you accidentally commit a file that should stay local:

1. **Do NOT push.** If the commit has not been pushed, you can safely amend or reset.
2. **If already pushed**, follow the procedure in `docs/PRIVATE_RUN_FAILURES.md` under "Accidental raw outputs committed".
3. **Rotate any exposed credentials** immediately (HF tokens, API keys).
4. **Record the incident** in the adapter manifest notes.

```bash
# If not yet pushed — remove the file from the commit
git reset HEAD path/to/sensitive/file
git commit --amend

# If pushed — use git filter-branch or BFG to rewrite history
# See docs/PRIVATE_RUN_FAILURES.md for detailed recovery
```

---

## Reference: PRIVATE_EVAL_RESULTS_POLICY.md

This document complements `docs/PRIVATE_EVAL_RESULTS_POLICY.md`, which specifically governs evaluation result artifacts. The key principles from that policy are:

| Principle | From PRIVATE_EVAL_RESULTS_POLICY.md |
|-----------|-------------------------------------|
| No raw prompts | Eval prompts may contain proprietary instructions — never commit prompt text |
| No raw responses | Model responses may contain real data or credentials — never commit response text |
| No invented scores | `score_status` is always `"manual_review_required"` until human review |
| No local paths | Only `run_id` and `model_label` identify the run, no filesystem paths |
| No tokens | No authentication or API information in eval results |
| Use `create_eval_summary.py` | The script strips sensitive fields automatically |

**When this document and PRIVATE_EVAL_RESULTS_POLICY.md conflict, the more restrictive rule applies.**

---

## Summary Table

| Artifact | Can Commit? | Conditions |
|----------|------------|------------|
| `adapter_model.safetensors` | ❌ NEVER | Binary weights — always stays local |
| `adapter_model.bin` | ❌ NEVER | Binary weights — always stays local |
| `optimizer.pt` / `rng_state.pth` | ❌ NEVER | Training state — always stays local |
| `checkpoint-*/` | ❌ NEVER | Intermediate training state — always stays local |
| `runs/` (TensorBoard) | ❌ NEVER | Binary event files — always stays local |
| `wandb/` | ❌ NEVER | Experiment tracking cache — always stays local |
| Raw eval outputs | ❌ NEVER | Contains prompts + responses — always stays local |
| `MANIFEST.yaml` | ⚠️ CONDITIONAL | Must sanitize: no absolute paths, no weight data |
| `eval_summary.json` | ⚠️ CONDITIONAL | Must sanitize: no prompts, no responses, no paths |
| `compare_summary.json` | ⚠️ CONDITIONAL | Must sanitize: no private prompt content, no paths |
| `adapter_config.json` | ⚠️ CONDITIONAL | Must sanitize: replace absolute paths with HF model IDs |
| `all_results.json` | ⚠️ CONDITIONAL | Training metrics only — verify no sensitive content |
| Training config (`.yaml`) | ✅ YES | Already in repo, no sanitization needed |
| Run manifest (`.yaml`) | ✅ YES | Metadata only, already in repo |

---

## Related Documents

| Document | Relationship |
|----------|-------------|
| [PRIVATE_EVAL_RESULTS_POLICY.md](PRIVATE_EVAL_RESULTS_POLICY.md) | Specific policy for eval result artifacts |
| [ADAPTER_ARTIFACT_POLICY.md](ADAPTER_ARTIFACT_POLICY.md) | What can and cannot be committed, naming conventions, hash recording |
| [ADAPTER_PREVIEW_GATE.md](ADAPTER_PREVIEW_GATE.md) | State machine for adapter release — all adapters start BLOCKED |
| [PRIVATE_RUN_FAILURES.md](PRIVATE_RUN_FAILURES.md) | Troubleshooting guide including accidental commits |
| [REMOTE_GPU_RUNPOD_GUIDE.md](REMOTE_GPU_RUNPOD_GUIDE.md) | Guide for running on RunPod — references this document for what to copy |
| [PRIVATE_TRAINING_RUNBOOK.md](PRIVATE_TRAINING_RUNBOOK.md) | Step-by-step runbook for first private SFT |
| [PRIVATE_SFT_EXECUTION_CHECKLIST.md](PRIVATE_SFT_EXECUTION_CHECKLIST.md) | Pre-flight checklist for SFT run |
| [MODEL_HASHING.md](MODEL_HASHING.md) | SHA-256 hash procedures for model files |

---

*This document classifies every artifact from a private training run as either "stays local" or "may be committed with conditions." When in doubt, leave it out. The most restrictive rule always applies. No weights, no private data, no raw outputs, no sensitive paths in Git.*
