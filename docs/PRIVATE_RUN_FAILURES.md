# Private Run Failures — Troubleshooting Guide

> **Document Type:** Troubleshooting guide for private training run failures
> **Version:** v0.1.22-alpha
> **Date:** 2026-05-23
> **Status:** Active — reference for diagnosing and recovering from training failures

---

## Purpose

This document provides a structured troubleshooting reference for common failure modes encountered during private SFT training runs. Each failure mode includes the symptom, likely cause, fix, and prevention strategy.

**Key principle:** When a training run fails, the preview gate remains **BLOCKED**. A failed run does not produce a committable artifact. Do not advance the gate after recovering — start over and verify the fix.

---

## Failure Mode 1: OOM During Training

### Symptom

- Training crashes with `torch.cuda.OutOfMemoryError`
- `nvidia-smi` shows 100% VRAM usage before crash
- Error message: `CUDA out of memory. Tried to allocate X.XX GiB`
- May occur at different points: first forward pass, gradient accumulation, or checkpoint saving

### Cause

| Possible Cause | How to Confirm |
|---------------|----------------|
| Batch size too large for available VRAM | Check `per_device_train_batch_size` in config — default may be too high |
| Sequence length too long | Check `max_seq_length` — 4096 requires significantly more VRAM than 2048 |
| LoRA rank too high | Check `lora_r` — r=32 uses more VRAM than r=16 |
| Gradient checkpointing not enabled | Check config — without it, all activations are stored in VRAM |
| Accumulated optimizer states | If resuming from checkpoint, old optimizer states may be loaded |
| Other processes using GPU | Run `nvidia-smi` — check for other Python processes or X server |

### Fix

**Immediate (reduce VRAM usage):**

```bash
# Option 1: Reduce batch size
# Edit training/configs/kimari_sft_lora.v0.example.yaml
# per_device_train_batch_size: 1  (was 2 or 4)
# gradient_accumulation_steps: 16  (increase to compensate)

# Option 2: Enable gradient checkpointing
# Edit the config to add:
# gradient_checkpointing: true

# Option 3: Reduce sequence length
# max_seq_length: 2048  (was 4096)

# Option 4: Reduce LoRA rank
# lora_r: 16  (was 32)
# lora_alpha: 32  (was 64)

# Option 5: Switch to QLoRA (4-bit quantization)
# Use bitsandbytes with 4-bit quantization
# See docs/MODEL_TRAINING_PLAN.md for QLoRA config
```

**After fixing, re-run from scratch:**

```bash
# Clear the old output directory
rm -rf training/adapters/kimari-smollm3-sft-v0/

# Re-run dry-run first
python training/scripts/train_sft_lora.py \
    --dry-run \
    --config training/configs/kimari_sft_lora.v0.example.yaml

# Then re-run training
python training/scripts/train_sft_lora.py \
    --config training/configs/kimari_sft_lora.v0.example.yaml
```

### Prevention

- Run `nvidia-smi` before training to confirm available VRAM
- Use the VRAM estimates in `docs/REMOTE_GPU_RUNPOD_GUIDE.md`
- Start with conservative settings (batch_size=1, gradient_checkpointing=true)
- Monitor VRAM during the first few training steps with `watch nvidia-smi`
- Use QLoRA on GPUs with 16 GB VRAM or less

---

## Failure Mode 2: CUDA Unavailable

### Symptom

- `torch.cuda.is_available()` returns `False`
- Error: `CUDA not available. Training requires a GPU.`
- `nvidia-smi` fails with `command not found` or `NVIDIA-SMI has failed`
- Training falls back to CPU (extremely slow) or crashes

### Cause

| Possible Cause | How to Confirm |
|---------------|----------------|
| PyTorch installed without CUDA support | `python -c "import torch; print(torch.version.cuda)"` returns `None` |
| NVIDIA driver not installed | `nvidia-smi` returns `command not found` |
| Wrong PyTorch index URL | Installed CPU-only PyTorch instead of CUDA version |
| GPU instance not provisioned correctly | RunPod template missing GPU passthrough |
| CUDA version mismatch | `nvcc --version` version ≠ PyTorch CUDA version |
| Docker container without NVIDIA runtime | `docker run --gpus all` was not used |

### Fix

**On RunPod:**

```bash
# Verify GPU is visible
nvidia-smi

# If nvidia-smi works but PyTorch doesn't see CUDA:
pip uninstall torch
pip install torch --index-url https://download.pytorch.org/whl/cu121  # Match your CUDA version

# Verify
python -c "import torch; print(f'CUDA: {torch.cuda.is_available()}, Device: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else \"N/A\"}')"
```

**If nvidia-smi fails entirely:**

```bash
# The instance was likely provisioned without GPU passthrough
# Terminate and recreate with a GPU-enabled template
# On RunPod: ensure you selected a GPU instance, not CPU-only
```

### Prevention

- Always verify `nvidia-smi` and `torch.cuda.is_available()` before training
- Install PyTorch with the correct `--index-url` for your CUDA version
- Use a PyTorch template when creating the RunPod instance
- Check CUDA compatibility: PyTorch CUDA version ≤ driver CUDA version

---

## Failure Mode 3: Tokenizer Load Failure

### Symptom

- Error: `OSError: Can't load tokenizer for 'HuggingFaceTB/SmolLM3-3B'`
- Error: `ConnectionError` or `HTTPError` during model download
- Error: `UnicodeDecodeError` when reading tokenizer files
- Training script exits during model/tokenizer initialization

### Cause

| Possible Cause | How to Confirm |
|---------------|----------------|
| No internet access on GPU instance | `curl -I https://huggingface.co` fails |
| HF Hub rate limiting | Repeated downloads without authentication |
| Corrupted cache | `ls $HF_HOME/hub/` — check for partial/incomplete files |
| `sentencepiece` not installed | `python -c "import sentencepiece"` fails |
| `protobuf` not installed | `python -c "import protobuf"` fails |
| Wrong model name in config | Typo in `base_model` field of training config |
| HF access token required (gated models) | Model requires authentication but no token set |

### Fix

```bash
# Check internet access
curl -I https://huggingface.co

# Clear corrupted HF cache
rm -rf $HF_HOME/hub/models--HuggingFaceTB--SmolLM3-3B/

# Verify dependencies
pip install sentencepiece protobuf

# Pre-download the tokenizer to verify it works
python -c "
from transformers import AutoTokenizer
tokenizer = AutoTokenizer.from_pretrained('HuggingFaceTB/SmolLM3-3B')
print(f'Tokenizer loaded: vocab_size={tokenizer.vocab_size}')
"

# If gated model (SmolLM3-3B is Apache 2.0, but check):
# huggingface-cli login
# Then re-run training
```

### Prevention

- Pre-download the tokenizer before starting the full training run
- Verify internet access on the GPU instance before training
- Set `HF_HOME` to persistent storage so downloads survive instance restarts
- Install `sentencepiece` and `protobuf` as part of setup (in `training/requirements-training.txt`)

---

## Failure Mode 4: Dataset Validation Failure

### Symptom

- `validate_training_ready.py` exits with errors
- `build_dataset_mix.py` reports invalid records
- Training starts but produces garbage output or NaN loss immediately
- Error: `KeyError: 'instruction'` or `KeyError: 'output'`

### Cause

| Possible Cause | How to Confirm |
|---------------|----------------|
| Missing required fields in SFT data | `python -c "import json; [print(k) for r in [json.loads(l) for l in open('dataset/v0/sft_v0.jsonl')] for k in ['instruction','output','source','license'] if k not in r]"` |
| Invalid JSON in JSONL files | `python -c "import json; [json.loads(l) for i, l in enumerate(open('dataset/v0/sft_v0.jsonl'))]"` — will fail on bad lines |
| Empty dataset file | `wc -l dataset/v0/sft_v0.jsonl` — should have content |
| Duplicate entries | Run `build_dataset_mix.py --report` — check for duplicates in report |
| Forbidden strings in data | Run `validate_training_ready.py --json` — checks for tokens, secrets |
| Wrong dataset path in config | Check `dataset_path` in SFT config matches built dataset location |

### Fix

```bash
# Run validation to identify specific issues
python training/scripts/validate_training_ready.py \
    --base-config training/configs/base_candidates.yaml \
    --sft dataset/v0/sft_v0.jsonl \
    --preference dataset/v0/preference_v0.jsonl \
    --holdout dataset/v0/eval_holdout.jsonl \
    --json

# Fix identified issues in the source dataset files
# Then rebuild:
python training/scripts/build_dataset_mix.py \
    --sft dataset/v0/sft_v0.jsonl \
    --preference dataset/v0/preference_v0.jsonl \
    --holdout dataset/v0/eval_holdout.jsonl \
    --output-dir dataset/build/kimari-v0 \
    --shuffle \
    --seed 42 \
    --report

# Re-validate
python training/scripts/validate_training_ready.py \
    --base-config training/configs/base_candidates.yaml \
    --sft dataset/v0/sft_v0.jsonl \
    --preference dataset/v0/preference_v0.jsonl \
    --holdout dataset/v0/eval_holdout.jsonl \
    --json
```

### Prevention

- Always validate datasets before training
- Run `build_dataset_mix.py --report` and review the report
- Use schema validation for all JSONL files
- Never manually edit dataset files without re-validating

---

## Failure Mode 5: PEFT/TRL Version Mismatch

### Symptom

- Error: `ImportError: cannot import name 'SFTTrainer' from 'trl'`
- Error: `AttributeError: module 'peft' has no attribute 'LoraConfig'`
- Error: `TypeError: __init__() got an unexpected keyword argument`
- Training starts but produces incorrect or unstable results
- LoRA adapter config is incompatible with the installed PEFT version

### Cause

| Possible Cause | How to Confirm |
|---------------|----------------|
| `peft` version too old | `pip show peft` — check version against `>=0.7.0` |
| `trl` version too old | `pip show trl` — check version against `>=0.7.0` |
| `transformers` version incompatible with `peft`/`trl` | Version pinning conflict |
| Mixed installation sources | Some packages from conda, others from pip |
| Cached incompatible version | `pip list | grep -E 'peft|trl|transformers'` — check all versions |

### Fix

```bash
# Upgrade all training dependencies together
pip install --upgrade transformers>=4.36.0 peft>=0.7.0 trl>=0.7.0 accelerate>=0.25.0

# Verify versions are compatible
python -c "
import transformers; print(f'transformers: {transformers.__version__}')
import peft; print(f'peft: {peft.__version__}')
import trl; print(f'trl: {trl.__version__}')
import accelerate; print(f'accelerate: {accelerate.__version__}')
"

# If still failing, create a fresh venv
python3 -m venv .venv-training-clean
source .venv-training-clean/bin/activate
pip install --upgrade pip
pip install torch --index-url https://download.pytorch.org/whl/cu121
pip install -r training/requirements-training.txt
pip install -e .
```

### Prevention

- Always install training dependencies from `training/requirements-training.txt`
- Pin versions after the first successful run (replace `>=` with `==`)
- Use a fresh virtual environment for each training run
- Do not mix conda and pip installations
- Verify all versions after installation

---

## Failure Mode 6: Eval Endpoint Unavailable

### Symptom

- `kimarifit.py` fails with `ConnectionError` or `ConnectionRefusedError`
- Error: `Cannot connect to http://127.0.0.1:8080/v1`
- Eval script times out waiting for responses
- Baseline or adapter evaluation cannot proceed

### Cause

| Possible Cause | How to Confirm |
|---------------|----------------|
| `llama-server` not running | `curl http://127.0.0.1:8080/v1/models` fails |
| Wrong port configured | `ss -tlnp | grep 8080` — check which port is listening |
| Model not loaded in llama-server | Check llama-server logs for load errors |
| Server crashed during eval | `ps aux | grep llama-server` — check if process is alive |
| Firewall blocking localhost | Unlikely on a single machine, but check `iptables` |
| Server bound to wrong host | Check `--host` flag — should be `127.0.0.1` |

### Fix

```bash
# Check if llama-server is running
ps aux | grep llama-server

# If not running, start it:
./llama-server \
    -m models/smollm3-3b-q4_k_m.gguf \
    --port 8080 \
    --host 127.0.0.1 \
    -c 8192 \
    -ngl 99

# Verify it's responding
curl http://127.0.0.1:8080/v1/models

# If port is wrong, adjust in the eval command:
python eval/kimarifit.py \
    --prompts eval/kimarifit_prompts.jsonl \
    --endpoint http://127.0.0.1:8080/v1 \
    --model smollm3-3b \
    --output eval/results/baseline-smollm3-q4km.json

# If model fails to load in llama-server, check:
ls -la models/smollm3-3b-q4_k_m.gguf  # File exists?
file models/smollm3-3b-q4_k_m.gguf     # Valid GGUF?
```

### Prevention

- Start `llama-server` and verify it responds before running eval
- Use a health check: `curl -s http://127.0.0.1:8080/v1/models | python -m json.tool`
- Keep llama-server running in a separate terminal or `tmux` session
- Use `--timeout` flag in eval scripts to avoid indefinite hangs

---

## Failure Mode 7: Adapter Manifest Hash Mismatch

### Symptom

- `postrun_private_sft.py` reports hash mismatch
- `sha256sum` of `adapter_model.safetensors` differs from the manifest
- `check-release.py` flags inconsistent hashes
- Adapter file appears corrupted after transfer between machines

### Cause

| Possible Cause | How to Confirm |
|---------------|----------------|
| File corrupted during transfer | Compare `sha256sum` on source and destination machines |
| File modified after manifest creation | Check file modification time vs manifest creation time |
| Wrong file hashed | Verify the path in the manifest matches the actual file |
| Git LFS or other transformation | Check if Git or any tool modified the binary file |
| Incomplete write (disk full) | `ls -la` — check file size matches expected |
| Endianness or encoding issue | Unlikely with SHA-256, but possible with very old tools |

### Fix

```bash
# Re-compute hashes
sha256sum training/adapters/kimari-smollm3-sft-v0/adapter_model.safetensors
sha256sum training/adapters/kimari-smollm3-sft-v0/adapter_config.json

# Re-generate the manifest
python training/scripts/create_adapter_manifest.py \
    --run-config training/configs/private_sft_run.v0.yaml \
    --adapter-dir training/adapters/kimari-smollm3-sft-v0 \
    --output training/adapters/kimari-smollm3-sft-v0/MANIFEST.yaml

# If the file is corrupted (hash doesn't match source):
# The training run must be considered invalid.
# Re-run training from scratch.
# Gate stays BLOCKED.
```

### Prevention

- Compute and record hashes immediately after training completes
- Verify hashes after any file transfer
- Use `sha256sum -c` to verify integrity after transfers
- Do not modify adapter files between training and hash recording

---

## Failure Mode 8: Accidental Raw Outputs Committed

### Symptom

- Git diff shows files that should not be committed (`.safetensors`, raw eval outputs, etc.)
- CI fails on check-release checks for suspicious content
- PR reviewer flags sensitive content
- `git log` shows a commit with adapter weights or raw eval data

### Cause

| Possible Cause | How to Confirm |
|---------------|----------------|
| Forgot to check `.gitignore` coverage | `git status training/adapters/` — shows uncommitted adapter files |
| Accidentally staged a large file | `git diff --cached --name-only` — check for unexpected files |
| `.gitignore` pattern missing | `git check-ignore training/adapters/kimari-smollm3-sft-v0/adapter_model.safetensors` — should be ignored |
| Used `git add .` instead of selective staging | Review `git diff --cached` for unexpected files |
| Eval results contain prompt/response fields | Check file contents for `"prompt":` or `"response":` keys |

### Fix

**If not yet pushed:**

```bash
# Unstage the file
git reset HEAD path/to/sensitive/file

# Amend the commit
git commit --amend

# Or reset the entire commit
git reset --soft HEAD~1
# Re-stage only safe files
git add <safe-files-only>
git commit -m "message"
```

**If already pushed:**

```bash
# CRITICAL: This is a security incident.

# Step 1: Rotate any exposed credentials immediately
# - If HF tokens were in the committed files: regenerate at huggingface.co/settings/tokens
# - If API keys were exposed: rotate them immediately

# Step 2: Remove the file from Git history
# Using git filter-branch (slow but reliable):
git filter-branch --force --index-filter \
    'git rm --cached --ignore-unmatch path/to/sensitive/file' \
    --prune-empty -- --all

# Or using BFG Repo-Cleaner (faster):
# java -jar bfg.jar --delete-files adapter_model.safetensors
# git reflog expire --expire=now --all && git gc --prune=now --aggressive

# Step 3: Force push the cleaned history
git push origin --force --all

# Step 4: Record the incident
# Add a note to the adapter manifest:
# incident: "Raw output accidentally committed on YYYY-MM-DD, removed and history rewritten"

# Step 5: Verify
git log --all --full-history -- path/to/sensitive/file
# Should return nothing
```

### Prevention

- Review `git diff --cached --name-only` before every commit
- Use selective `git add` instead of `git add .`
- Ensure `.gitignore` covers all sensitive patterns:
  ```
  training/adapters/**/*.safetensors
  training/adapters/**/*.bin
  training/adapters/**/*.pt
  training/adapters/**/checkpoint-*/
  training/adapters/**/runs/
  wandb/
  eval/results/*-raw.json
  ```
- Run `check-release.py` before pushing
- Use pre-commit hooks if available

---

## Failure Mode 9: How to Abort and Keep Gate BLOCKED

### When to Abort

Abort the training run if:

- Training loss shows NaN or diverges uncontrollably
- OOM errors persist after reducing batch size and enabling gradient checkpointing
- CUDA errors are not recoverable
- Dataset quality issues are discovered mid-training
- Safety concerns are identified in the training data
- The GPU instance is about to expire or become unavailable
- Any other unrecoverable error occurs

### Aborting Safely

```bash
# Step 1: Stop the training process
# If running in foreground: Ctrl+C
# If running in background:
kill <PID>

# Step 2: Verify the process is stopped
ps aux | grep train_sft_lora

# Step 3: Record the abort in the adapter directory (if it exists)
mkdir -p training/adapters/kimari-smollm3-sft-v0/

cat > training/adapters/kimari-smollm3-sft-v0/ABORT_RECORD.md << 'EOF'
# Training Abort Record

- **Date:** $(date)
- **Reason:** [Describe why the run was aborted]
- **Step:** [Last completed training step, if known]
- **Loss:** [Last observed loss value, if known]
- **GPU:** [GPU type and VRAM]
- **Error:** [Error message or description]

This run was aborted. The adapter output is incomplete and should not be used.
Preview gate state: BLOCKED.
EOF

# Step 4: Verify the gate remains BLOCKED
# Check the run config:
grep 'preview_gate_state\|public_release_allowed\|hf_upload_allowed' \
    training/configs/private_sft_run.v0.yaml

# Step 5: Do NOT create a manifest for the aborted run
# Do NOT advance the preview gate
# Do NOT commit any artifacts from the aborted run
```

### Post-Abort Actions

1. **Diagnose the failure** — identify the root cause using this guide
2. **Fix the issue** — adjust config, dataset, or environment
3. **Clear the adapter directory** — `rm -rf training/adapters/kimari-smollm3-sft-v0/`
4. **Re-run from scratch** — start with dry-run, then pre-flight, then real training
5. **Gate remains BLOCKED** — no state change from the abort

---

## Failure Mode 10: Recovery Procedures

### Scenario A: Training interrupted (machine crash, timeout, manual abort)

```
1. Verify GPU instance is still available (or provision a new one)
2. Re-clone the repository if needed
3. Re-create the virtual environment
4. Re-install dependencies: pip install -r training/requirements-training.txt
5. Re-build dataset: python training/scripts/build_dataset_mix.py ...
6. Re-run dry-run: python training/scripts/train_sft_lora.py --dry-run ...
7. Re-run pre-flight: python training/scripts/preflight_private_sft.py ...
8. Re-run training from scratch: python training/scripts/train_sft_lora.py ...
9. Do NOT resume from partial checkpoints — they may be corrupt
10. Gate stays BLOCKED
```

### Scenario B: Bad training results (loss diverged, safety regression)

```
1. Record the bad results in a local file (not committed)
2. Review the training config for issues:
   - Learning rate too high? → reduce to 1.0e-4
   - Epochs too many? → try 1 epoch instead of 2
   - LoRA rank too high? → try r=16 instead of r=32
   - Dataset quality issues? → review dataset/v0/ files
3. Adjust config and re-run from scratch
4. Gate stays BLOCKED
5. Do NOT advance the gate for the failed run
```

### Scenario C: Sensitive data discovered in training output

```
1. Stop training immediately
2. Review the dataset for the source of the sensitive data
3. Remove the sensitive data from dataset/v0/ source files
4. Re-validate: python training/scripts/validate_training_ready.py ...
5. Re-build: python training/scripts/build_dataset_mix.py ...
6. Re-train from scratch
7. If sensitive data was already committed to Git:
   → Follow "Accidental raw outputs committed" procedure above
8. Gate stays BLOCKED
```

### Scenario D: Hash mismatch after training

```
1. Re-compute hashes: sha256sum training/adapters/.../adapter_model.safetensors
2. Compare with manifest values
3. If mismatch confirmed:
   - File may be corrupted → training run is invalid
   - Delete adapter directory and re-train from scratch
   - Gate stays BLOCKED
4. If hashes match on re-computation:
   - Manifest had stale values → re-generate manifest
   - python training/scripts/create_adapter_manifest.py ...
   - Gate stays BLOCKED
```

### Scenario E: RunPod instance expired before training completed

```
1. The training output is lost (on temporary storage)
2. If HF_HOME was on persistent storage (/workspace):
   - Model downloads are cached and won't need re-downloading
3. Provision a new GPU instance
4. Re-clone the repository
5. Re-create the virtual environment
6. Re-install dependencies
7. Re-build dataset
8. Re-run training from scratch
9. Gate stays BLOCKED
10. Consider using tmux or nohup for longer training runs
```

---

## Quick Reference: Failure → Gate State

| Failure Type | Gate State After Failure | Can Resume? | Must Re-run? |
|-------------|------------------------|-------------|--------------|
| OOM during training | BLOCKED | No | Yes, with adjusted config |
| CUDA unavailable | BLOCKED | After fixing CUDA | Possibly |
| Tokenizer load failure | BLOCKED | After fixing deps | No (pre-training) |
| Dataset validation failure | BLOCKED | After fixing data | No (pre-training) |
| PEFT/TRL version mismatch | BLOCKED | After upgrading | No (pre-training) |
| Eval endpoint unavailable | BLOCKED | After restarting server | No (eval only) |
| Hash mismatch | BLOCKED | No | Yes (data integrity) |
| Accidental raw output commit | BLOCKED | After cleaning Git | Depends |
| Training abort (any reason) | BLOCKED | No | Yes, from scratch |

**In all cases, the preview gate remains BLOCKED.** There is no failure mode that advances the gate. See `docs/ADAPTER_PREVIEW_GATE.md`.

---

## Related Documents

| Document | Relationship |
|----------|-------------|
| [ADAPTER_PREVIEW_GATE.md](ADAPTER_PREVIEW_GATE.md) | Gate state machine — all adapters start BLOCKED |
| [ADAPTER_ARTIFACT_POLICY.md](ADAPTER_ARTIFACT_POLICY.md) | What can and cannot be committed |
| [PRIVATE_RUN_ARTIFACTS.md](PRIVATE_RUN_ARTIFACTS.md) | What stays local vs what can be committed |
| [PRIVATE_EVAL_RESULTS_POLICY.md](PRIVATE_EVAL_RESULTS_POLICY.md) | What eval results can be committed |
| [REMOTE_GPU_RUNPOD_GUIDE.md](REMOTE_GPU_RUNPOD_GUIDE.md) | Guide for running on RunPod |
| [PRIVATE_TRAINING_RUNBOOK.md](PRIVATE_TRAINING_RUNBOOK.md) | Step-by-step runbook for first private SFT |
| [PRIVATE_SFT_EXECUTION_CHECKLIST.md](PRIVATE_SFT_EXECUTION_CHECKLIST.md) | Pre-flight checklist |
| [MODEL_TRAINING_PLAN.md](MODEL_TRAINING_PLAN.md) | Full training plan including hardware estimates |
| [SFT_TO_ORPO_DECISION.md](SFT_TO_ORPO_DECISION.md) | Decision framework for proceeding to ORPO |

---

*This troubleshooting guide covers the most common failure modes for private training runs. In every case, the preview gate remains BLOCKED after a failure. When in doubt, abort the run, diagnose the issue, fix it, and re-run from scratch. Never advance the gate after a failed run.*
