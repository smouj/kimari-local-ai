# Private SFT Run Commands — First Execution Reference

> **Document Type:** Command reference for the first private SFT execution
> **Version:** v0.1.22-alpha
> **Date:** 2026-05-22
> **Status:** Active — governs the exact commands for the first private SFT run

---

## Purpose

This document lists every command expected during the first private supervised fine-tuning (SFT) execution in Kimari Local AI. It serves as a single, authoritative reference for the operator running the first private training cycle — from environment setup through security scanning.

**All commands use safe placeholders.** No real tokens, keys, paths to private data, or actual run identifiers appear in this document. Replace placeholders with real values only on the training machine at execution time.

---

## Warnings

> **READ BEFORE EXECUTING ANY COMMAND.**

| # | Warning |
|---|---------|
| 1 | **Never run real training in CI.** CI validates with `--dry-run` only. Real training requires a GPU machine and must never be triggered by automated pipelines. |
| 2 | **Never commit adapter weights.** The `training/adapters/` directory is gitignored. Adapter `.safetensors` files, checkpoints, and merged model weights must never enter the Git repository. See `docs/ADAPTER_ARTIFACT_POLICY.md`. |
| 3 | **Never commit raw eval outputs.** Raw eval JSON files contain prompts and model responses. Only sanitized summaries produced by `create_eval_summary.py` may be committed. See `docs/PRIVATE_EVAL_RESULTS_POLICY.md`. |
| 4 | **Preview gate stays BLOCKED.** Completing training does NOT advance the adapter out of the BLOCKED state. All gate transitions require explicit human decisions. See `docs/ADAPTER_PREVIEW_GATE.md`. |
| 5 | **Kimari-4B is NOT published.** No model named "Kimari-4B" exists in any public registry. Do not reference it in commits, configs, or documentation as if it were a released artifact. |
| 6 | **Run `scan_for_secrets.py` before committing anything.** The secrets scanner must pass on all staged files before any push. See Command 11 below. |

---

## Cross-References

| Document | Relationship |
|----------|-------------|
| [FIRST_PRIVATE_SFT_HANDOFF.md](FIRST_PRIVATE_SFT_HANDOFF.md) | Handoff checklist for transferring the first SFT run to an operator |
| [HF_TOKEN_SAFETY.md](HF_TOKEN_SAFETY.md) | Rules for handling Hugging Face tokens during private runs |
| [PRIVATE_TRAINING_RUNBOOK.md](PRIVATE_TRAINING_RUNBOOK.md) | Full step-by-step runbook that these commands belong to |
| [ADAPTER_PREVIEW_GATE.md](ADAPTER_PREVIEW_GATE.md) | State machine governing adapter release — all adapters start BLOCKED |
| [ADAPTER_ARTIFACT_POLICY.md](ADAPTER_ARTIFACT_POLICY.md) | What can and cannot be committed; naming conventions |
| [PRIVATE_EVAL_RESULTS_POLICY.md](PRIVATE_EVAL_RESULTS_POLICY.md) | What eval results can and cannot be committed |
| [PRIVATE_SFT_EXECUTION_CHECKLIST.md](PRIVATE_SFT_EXECUTION_CHECKLIST.md) | Pre-flight checklist to complete before running any command here |
| [BASELINE_EVAL_PLAN.md](BASELINE_EVAL_PLAN.md) | Detailed plan for baseline evaluation of SmolLM3-3B |

---

## Command 1: Setup Environment

### Command

```bash
# Create an isolated training virtual environment
python3 -m venv .venv-training

# Activate the environment
source .venv-training/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install PyTorch with CUDA support
# Adjust --index-url for your CUDA version (cu121 = CUDA 12.1, cu124 = CUDA 12.4)
pip install torch --index-url https://download.pytorch.org/whl/cu121

# Install training dependencies
pip install transformers datasets peft trl accelerate bitsandbytes pyyaml

# Install Kimari package in development mode
pip install -e .

# Verify CUDA
python -c "import torch; print(f'CUDA available: {torch.cuda.is_available()}'); print(f'GPU: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else \"N/A\"}')"
```

### What It Does

Prepares an isolated Python virtual environment with all dependencies required for SFT training. The final verification step confirms that PyTorch can see the GPU and that CUDA is functional.

### Expected Output Summary

```
CUDA available: True
GPU: <your_gpu_name>
```

If `CUDA available: False`, do not proceed. Resolve GPU driver or CUDA toolkit issues first.

### Safety Notes

- **Do not install training dependencies in your system Python or development venv.** Keep training isolated to prevent dependency conflicts.
- **Do not use `--break-system-packages`** or `sudo pip install`.
- Verify the PyTorch CUDA version matches your installed CUDA toolkit.

---

## Command 2: Build Dataset

### Command

```bash
python training/scripts/build_dataset_mix.py \
    --sft dataset/v0/sft_v0.jsonl \
    --preference dataset/v0/preference_v0.jsonl \
    --holdout dataset/v0/eval_holdout.jsonl \
    --output-dir dataset/build/kimari-v0 \
    --shuffle \
    --seed 42 \
    --report
```

### What It Does

Reads the raw v0 dataset files (SFT, preference, and holdout), validates each record for required fields, splits into train/eval partitions, shuffles with a fixed seed for reproducibility, and writes partitioned files plus a `report.json` to the output directory.

### Expected Output Summary

```
Kimari Dataset Mix Builder
========================================

Validating SFT dataset...
  Input: N | Valid: N | Invalid: 0

Validating preference dataset...
  Input: N | Valid: N | Invalid: 0

Splitting datasets...
  Train ratio: 0.9 | Eval ratio: 0.1 | Shuffle: True | Seed: 42
  SFT: N train / N eval
  Preference: N train / N eval

Wrote N SFT train records to dataset/build/kimari-v0/sft.train.jsonl
Wrote N SFT eval records to dataset/build/kimari-v0/sft.eval.jsonl
Wrote N preference train records to dataset/build/kimari-v0/preference.train.jsonl
Wrote N preference eval records to dataset/build/kimari-v0/preference.eval.jsonl
Copied holdout (N records) to dataset/build/kimari-v0/holdout.jsonl
Wrote report to dataset/build/kimari-v0/report.json

Done.
```

### Safety Notes

- Ensure all dataset files in `dataset/v0/` are **synthetic and MIT-compatible**. No private data, secrets, or copyrighted content is allowed.
- If `Invalid` count is > 0, investigate and fix the source data before proceeding.
- The `--seed 42` flag ensures reproducibility. Do not omit it for the first run.

---

## Command 3: Preflight Check

### Command

```bash
python training/scripts/preflight_private_sft.py \
    --run-config training/configs/private_sft_run.v0.yaml \
    --json
```

### What It Does

Runs a comprehensive preflight validation before training begins. Checks: environment (Python version, CUDA, GPU memory), dataset availability and integrity, run config validity (`public_release_allowed: false`, `hf_upload_allowed: false`), disk space sufficiency, and dependency availability. The `--json` flag produces machine-readable output for scripting.

### Expected Output Summary

```json
{
  "status": "PASS",
  "checks": {
    "python_version": "PASS",
    "cuda_available": "PASS",
    "gpu_memory_mb": 24576,
    "gpu_memory_pass": true,
    "dataset_sft_exists": true,
    "dataset_preference_exists": true,
    "dataset_holdout_exists": true,
    "run_config_valid": true,
    "public_release_allowed": false,
    "hf_upload_allowed": false,
    "disk_space_gb": 85.3,
    "disk_space_pass": true,
    "dependencies": "PASS"
  }
}
```

If `status` is not `PASS`, address the failing checks before continuing.

### Safety Notes

- **Do not proceed to Command 5 if preflight fails.** All checks must pass.
- The `--json` output is safe to commit (contains no secrets), but raw preflight output from a failed run should be reviewed for leaked paths before committing.
- Verify that `public_release_allowed` and `hf_upload_allowed` are both `false` in the output.

---

## Command 4: Print Training Command Preview

### Command

```bash
python training/scripts/run_training_command_preview.py \
    --json
```

### What It Does

Prints the exact training command that will be executed (including all resolved arguments from the run config and SFT config), without launching training. This is a read-only preview to confirm the command before committing to a GPU run. The `--json` flag produces structured output.

### Expected Output Summary

```json
{
  "command": "accelerate launch training/scripts/train_sft_lora.py --config training/configs/kimari_sft_lora.v0.example.yaml",
  "resolved_config": {
    "base_model": "HuggingFaceTB/SmolLM3-3B",
    "output_dir": "training/adapters/kimari-smollm3-sft-v0",
    "num_train_epochs": 2,
    "per_device_train_batch_size": 4,
    "gradient_accumulation_steps": 4,
    "learning_rate": 2e-4,
    "lora_rank": 32,
    "lora_alpha": 64
  },
  "estimated_vram_gb": 14.2,
  "estimated_time_hours": "3-6"
}
```

### Safety Notes

- This command **does not train**. It only prints the command that would be run.
- Verify the `resolved_config` output matches your expectations before proceeding.
- Check `estimated_vram_gb` against your available GPU memory.

---

## Command 5: Real Training Command (Placeholder — Not Actual Execution)

### Command

```bash
# ╔══════════════════════════════════════════════════════════════╗
# ║  THIS IS A PLACEHOLDER. DO NOT RUN IN CI. GPU REQUIRED.    ║
# ╚══════════════════════════════════════════════════════════════╝

accelerate launch training/scripts/train_sft_lora.py \
    --config training/configs/kimari_sft_lora.v0.example.yaml
```

### What It Does

Launches the actual SFT training using Accelerate for multi-GPU or single-GPU distributed training. The `kimari_sft_lora.v0.example.yaml` config defines: base model, LoRA parameters (rank, alpha, dropout), dataset paths, training hyperparameters (epochs, batch size, learning rate), and output directory.

**This command requires a GPU with sufficient VRAM and must only be run on the training machine.**

### Expected Output Summary

```
[2026-XX-XX HH:MM:SS] Loading model HuggingFaceTB/SmolLM3-3B...
[2026-XX-XX HH:MM:SS] Applying LoRA adapter (r=32, alpha=64)...
[2026-XX-XX HH:MM:SS] Loading dataset from dataset/build/kimari-v0/sft.train.jsonl...
[2026-XX-XX HH:MM:SS] Starting training...
  Step 10/NNN | Loss: X.XXXX | LR: X.XXXXXX
  Step 20/NNN | Loss: X.XXXX | LR: X.XXXXXX
  ...
[2026-XX-XX HH:MM:SS] Training complete.
[2026-XX-XX HH:MM:SS] Adapter saved to training/adapters/kimari-smollm3-sft-v0/
```

### Safety Notes

- **NEVER run this command in CI.** CI uses `--dry-run` only.
- **NEVER commit the output directory** (`training/adapters/kimari-smollm3-sft-v0/`). It is gitignored.
- Monitor loss curves during training. If loss spikes to NaN or diverges, stop training immediately.
- On CUDA OOM, reduce `gradient_accumulation_steps` or enable gradient checkpointing.
- **Preview gate remains BLOCKED** after training completes. No automatic state transition.

---

## Command 6: Baseline Eval

### Command

```bash
python eval/scripts/run_baseline_eval_plan.py \
    --dry-run \
    --json
```

### What It Does

Plans and validates a baseline evaluation run against the unmodified base model (SmolLM3-3B). The `--dry-run` flag shows the evaluation plan (prompts, endpoint, output path) without executing any evaluations. The `--json` flag produces structured output. This must be run **before** training (Command 5) to establish a comparison baseline.

### Expected Output Summary

```json
{
  "plan": "baseline_eval",
  "model": "smollm3-3b",
  "prompts_file": "eval/kimarifit_prompts.jsonl",
  "endpoint": "http://127.0.0.1:8080/v1",
  "output_path": "eval/results/baseline-smollm3-q4km.json",
  "num_prompts": 35,
  "dry_run": true,
  "status": "PLAN_VALID"
}
```

To execute the actual baseline eval (requires llama-server running with base model):

```bash
python eval/scripts/run_baseline_eval_plan.py \
    --endpoint http://127.0.0.1:8080/v1 \
    --model smollm3-3b \
    --output eval/results/baseline-smollm3-q4km.json \
    --json
```

### Safety Notes

- **Always run baseline eval before SFT training.** You need a baseline to compare against.
- The `--dry-run` output is safe to commit (no model responses).
- Full baseline eval results (`eval/results/baseline-smollm3-q4km.json`) contain prompts and responses — **do not commit raw results**. Use `create_eval_summary.py` (Command 9) to produce a committable summary.
- Ensure llama-server is bound to `127.0.0.1` only, never `0.0.0.0`.

---

## Command 7: Adapter Eval

### Command

```bash
python eval/scripts/run_adapter_eval_plan.py \
    --dry-run \
    --json
```

### What It Does

Plans and validates an evaluation run against the fine-tuned adapter. The `--dry-run` flag shows the evaluation plan without executing. This is run **after** training (Command 5) and after the adapter has been merged and served locally.

### Expected Output Summary

```json
{
  "plan": "adapter_eval",
  "adapter": "kimari-smollm3-sft-v0",
  "prompts_file": "eval/kimarifit_prompts.jsonl",
  "endpoint": "http://127.0.0.1:8080/v1",
  "output_path": "eval/results/adapter-smollm3-sft-v0-q4km.json",
  "baseline_path": "eval/results/baseline-smollm3-q4km.json",
  "num_prompts": 35,
  "dry_run": true,
  "status": "PLAN_VALID"
}
```

To execute the actual adapter eval:

```bash
python eval/scripts/run_adapter_eval_plan.py \
    --endpoint http://127.0.0.1:8080/v1 \
    --model kimari-smollm3-sft-v0 \
    --output eval/results/adapter-smollm3-sft-v0-q4km.json \
    --baseline eval/results/baseline-smollm3-q4km.json \
    --json
```

### Safety Notes

- **Do not commit raw adapter eval results.** They contain prompts and model responses.
- Use `create_eval_summary.py` (Command 9) to produce a sanitized, committable summary.
- The adapter must be merged, converted to GGUF, and served via llama-server before this eval can execute.
- Verify the endpoint is `127.0.0.1` only — never expose the model server publicly.

---

## Command 8: Create Adapter Manifest

### Command

```bash
python training/scripts/create_adapter_manifest.py \
    --run-config training/configs/private_sft_run.v0.yaml \
    --adapter-dir training/adapters/kimari-smollm3-sft-v0 \
    --output training/adapters/kimari-smollm3-sft-v0/MANIFEST.yaml \
    --dry-run \
    --json
```

### What It Does

Generates the adapter manifest from the run config and the adapter directory contents. Records: adapter name, training run ID, base model, LoRA parameters, file hashes (SHA-256), file sizes, training metadata, and preview gate state. The `--dry-run` flag previews the manifest without writing to disk. The `--json` flag produces structured output.

**The manifest automatically sets:**
- `preview_gate_state: BLOCKED`
- `public_release_allowed: false`
- `hf_upload_allowed: false`

To write the manifest for real (after reviewing the dry-run output):

```bash
python training/scripts/create_adapter_manifest.py \
    --run-config training/configs/private_sft_run.v0.yaml \
    --adapter-dir training/adapters/kimari-smollm3-sft-v0 \
    --output training/adapters/kimari-smollm3-sft-v0/MANIFEST.yaml
```

### Expected Output Summary (dry-run)

```json
{
  "adapter_name": "kimari-smollm3-sft-v0",
  "run_id": "kimari-smollm3-sft-v0-private-001",
  "base_model": "HuggingFaceTB/SmolLM3-3B",
  "preview_gate_state": "BLOCKED",
  "public_release_allowed": false,
  "hf_upload_allowed": false,
  "adapter_files": [
    {"name": "adapter_config.json", "sha256": "<hash>", "size_bytes": 1234},
    {"name": "adapter_model.safetensors", "sha256": "<hash>", "size_bytes": 56789012}
  ],
  "dry_run": true,
  "status": "PREVIEW_VALID"
}
```

### Safety Notes

- **Creating a manifest does NOT advance the preview gate.** The adapter remains BLOCKED.
- The `--dry-run` output may contain file hashes and paths — review before committing the JSON output.
- The manifest file (`MANIFEST.yaml`) may be committed, but **never** the adapter weight files it references.
- Verify that `preview_gate_state` is `BLOCKED`, `public_release_allowed` is `false`, and `hf_upload_allowed` is `false` in the output.

---

## Command 9: Create Eval Summary

### Command

```bash
python eval/scripts/create_eval_summary.py \
    --input eval/results/adapter-smollm3-sft-v0-q4km.json \
    --output eval/results/adapter-smollm3-sft-v0-q4km-summary.json \
    --json
```

### What It Does

Reads the raw adapter evaluation results and produces a sanitized summary that strips all sensitive fields (prompts, model responses, full generation text). The output contains only aggregate scores, per-category pass/fail counts, and metadata — nothing that could leak prompt content or model outputs.

This is the **only** eval output format that may be committed to the repository. See `docs/PRIVATE_EVAL_RESULTS_POLICY.md`.

### Expected Output Summary

```json
{
  "adapter": "kimari-smollm3-sft-v0",
  "baseline": "smollm3-3b-q4km",
  "evaluation_date": "2026-XX-XX",
  "categories": {
    "python": {"pass": 3, "total": 5, "change_vs_baseline": "+1"},
    "typescript": {"pass": 2, "total": 4, "change_vs_baseline": "0"},
    "bash": {"pass": 2, "total": 3, "change_vs_baseline": "+1"},
    "docker": {"pass": 1, "total": 2, "change_vs_baseline": "0"},
    "linux_troubleshooting": {"pass": 2, "total": 3, "change_vs_baseline": "+1"},
    "windows_troubleshooting": {"pass": 1, "total": 2, "change_vs_baseline": "0"},
    "spanish_technical": {"pass": 2, "total": 3, "change_vs_baseline": "+1"},
    "json_mode": {"pass": 2, "total": 3, "change_vs_baseline": "0"},
    "openclaw_agent": {"pass": 1, "total": 2, "change_vs_baseline": "+1"},
    "local_security": {"pass": 3, "total": 3, "change_vs_baseline": "0"}
  },
  "safety_regression_detected": false,
  "overall_improvement": true,
  "sanitized": true,
  "contains_raw_prompts": false,
  "contains_raw_responses": false
}
```

### Safety Notes

- **Only the `--output` file from this command may be committed.** Never commit the `--input` file (raw eval results).
- Verify the output has `sanitized: true`, `contains_raw_prompts: false`, and `contains_raw_responses: false`.
- The summary follows the format defined in `eval/templates/eval_summary.template.json`.
- Even the sanitized summary should be reviewed for inadvertent leaks before committing.

---

## Command 10: Create Private Run Record

### Command

```bash
python training/scripts/create_private_run_record.py \
    --run-config training/configs/private_sft_run.v0.yaml \
    --dry-run \
    --json
```

### What It Does

Creates a formal run record documenting the first private SFT execution. Records: run ID, start/end timestamps, training hyperparameters, dataset version, eval outcomes, manifest hash, and final preview gate state. The `--dry-run` flag previews the record without writing. The `--json` flag produces structured output.

This record serves as the auditable artifact for the first training run.

To write the record for real:

```bash
python training/scripts/create_private_run_record.py \
    --run-config training/configs/private_sft_run.v0.yaml \
    --output training/runs/kimari-smollm3-sft-v0-private-001.json
```

### Expected Output Summary (dry-run)

```json
{
  "run_id": "kimari-smollm3-sft-v0-private-001",
  "run_type": "private_sft",
  "base_model": "HuggingFaceTB/SmolLM3-3B",
  "dataset_version": "v0",
  "preview_gate_state": "BLOCKED",
  "public_release_allowed": false,
  "hf_upload_allowed": false,
  "manifest_created": true,
  "eval_summary_created": true,
  "secrets_scan_passed": null,
  "dry_run": true,
  "status": "PREVIEW_VALID"
}
```

### Safety Notes

- The run record may be committed, but it must NOT contain adapter weights, model outputs, or raw prompts.
- Verify `preview_gate_state: BLOCKED` in the output.
- The `secrets_scan_passed` field should be set to `true` only after Command 11 passes.
- This record is a companion to the adapter manifest (Command 8) and eval summary (Command 9).

---

## Command 11: Scan Secrets

### Command

```bash
python scripts/security/scan_for_secrets.py \
    --paths README.md docs training eval tests \
    --json
```

### What It Does

Scans the specified directories and files for leaked secrets: API keys, tokens, passwords, private keys, and other sensitive patterns. Checks common secret formats (Hugging Face tokens, AWS keys, GitHub tokens, generic base64 blobs above a length threshold) and produces a structured report.

**This command MUST be run before committing anything** from the first private SFT run.

### Expected Output Summary

```json
{
  "scan_id": "scan-XXXXXXXX",
  "paths_scanned": ["README.md", "docs", "training", "eval", "tests"],
  "files_scanned": 142,
  "secrets_found": 0,
  "suspicious_patterns": 0,
  "results": [],
  "status": "PASS"
}
```

If `secrets_found > 0`:

```json
{
  "scan_id": "scan-XXXXXXXX",
  "paths_scanned": ["README.md", "docs", "training", "eval", "tests"],
  "files_scanned": 142,
  "secrets_found": 1,
  "suspicious_patterns": 1,
  "results": [
    {
      "file": "training/configs/REDACTED.yaml",
      "line": 14,
      "type": "possible_hf_token",
      "severity": "HIGH",
      "context": "hf_token: hf_***REDACTED***"
    }
  ],
  "status": "FAIL"
}
```

### Safety Notes

- **If the scan returns `FAIL`, do NOT commit.** Resolve all findings first.
- Even if the scan passes, review the `suspicious_patterns` count. Investigate any non-zero value.
- Add any false-positive patterns to the scanner's allowlist (documented in `scripts/security/`), but never silence real findings.
- Run this scan as the **last step** before every commit during the private training workflow.
- The `--json` output from a passing scan is safe to reference in the run record (Command 10).

---

## Command Execution Order

Commands must be executed in this order. Do not skip or reorder steps.

| Step | Command | Key Flag | GPU Required | Can Run in CI |
|------|---------|----------|--------------|---------------|
| 1 | Setup environment | — | No (verify only) | Partial (install, no CUDA verify) |
| 2 | Build dataset | `--report` | No | Yes |
| 3 | Preflight check | `--json` | No | Yes |
| 4 | Training command preview | `--json` | No | Yes |
| 5 | Real training | — | **Yes** | **No** |
| 6 | Baseline eval | `--dry-run --json` | No (dry-run) | Yes (dry-run only) |
| 7 | Adapter eval | `--dry-run --json` | No (dry-run) | Yes (dry-run only) |
| 8 | Create manifest | `--dry-run --json` | No | Yes (dry-run) |
| 9 | Create eval summary | `--json` | No | Partial |
| 10 | Create run record | `--dry-run --json` | No | Yes (dry-run) |
| 11 | Scan secrets | `--json` | No | Yes |

**Steps 6–7 actual execution** (without `--dry-run`) requires the model server running and is GPU-adjacent but does not need the training GPU.

---

## Quick Reference: What Never To Do

| # | Rule | Consequence |
|---|------|-------------|
| 1 | Never run real training in CI | CI has no GPU; training will fail or produce garbage |
| 2 | Never commit adapter weights | Violates `ADAPTER_ARTIFACT_POLICY.md`; leaks private artifacts |
| 3 | Never commit raw eval outputs | Contains prompts + responses; violates `PRIVATE_EVAL_RESULTS_POLICY.md` |
| 4 | Never advance preview gate automatically | All transitions require explicit human decisions |
| 5 | Never reference "Kimari-4B" as published | No such model exists publicly; creates false impressions |
| 6 | Never skip `scan_for_secrets.py` before commit | Leaked tokens/keys could compromise the project |
| 7 | Never bind model servers to `0.0.0.0` | Exposes unauthenticated inference endpoint |
| 8 | Never use WandB in public mode | Leaks training metadata to third parties |

---

## Related Documents

| Document | Relationship |
|----------|-------------|
| [FIRST_PRIVATE_SFT_HANDOFF.md](FIRST_PRIVATE_SFT_HANDOFF.md) | Handoff checklist for the operator running these commands |
| [HF_TOKEN_SAFETY.md](HF_TOKEN_SAFETY.md) | Rules for handling Hugging Face tokens during private runs |
| [PRIVATE_TRAINING_RUNBOOK.md](PRIVATE_TRAINING_RUNBOOK.md) | Full step-by-step runbook — these commands are extracted from it |
| [ADAPTER_PREVIEW_GATE.md](ADAPTER_PREVIEW_GATE.md) | State machine for adapter release — all adapters start BLOCKED |
| [ADAPTER_ARTIFACT_POLICY.md](ADAPTER_ARTIFACT_POLICY.md) | What can and cannot be committed |
| [PRIVATE_EVAL_RESULTS_POLICY.md](PRIVATE_EVAL_RESULTS_POLICY.md) | What eval results can and cannot be committed |
| [PRIVATE_SFT_EXECUTION_CHECKLIST.md](PRIVATE_SFT_EXECUTION_CHECKLIST.md) | Pre-flight checklist to complete before running any command here |
| [BASELINE_EVAL_PLAN.md](BASELINE_EVAL_PLAN.md) | Detailed plan for baseline evaluation |
| [PRIVATE_RUN_ARTIFACTS.md](PRIVATE_RUN_ARTIFACTS.md) | Classification of artifacts produced by private training runs |
| [PRIVATE_RUN_FAILURES.md](PRIVATE_RUN_FAILURES.md) | Failure modes and troubleshooting for private training runs |
| [SFT_TO_ORPO_DECISION.md](SFT_TO_ORPO_DECISION.md) | Decision framework for proceeding to ORPO after SFT |

---

*This document governs the exact commands for the first private SFT execution in Kimari Local AI. All commands use safe placeholders. No adapter may be published without passing the ADAPTER_PREVIEW_GATE. Run `scan_for_secrets.py` before every commit.*
