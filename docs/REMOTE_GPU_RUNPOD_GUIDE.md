# Remote GPU RunPod Guide — First Private SFT

> **Document Type:** Step-by-step guide for running the first private SFT on RunPod or similar GPU cloud
> **Version:** v0.1.22-alpha
> **Date:** 2026-05-23
> **Status:** Active — governs remote GPU training execution

---

## Purpose

This guide covers running the first private supervised fine-tuning (SFT) of SmolLM3-3B on a remote GPU cloud provider such as RunPod, Lambda Labs, Vast.ai, or similar. It is specifically designed for developers who do not have a local GPU with sufficient VRAM for LoRA training.

**This is a private training run.** The output adapter is for internal evaluation only. No weights are published, no benchmarks are claimed, and no public release is authorized without passing the `ADAPTER_PREVIEW_GATE`.

---

## ⚠️ Safety Warnings

> **READ BEFORE PROCEEDING.**

- **Private training only.** The adapter output is for internal evaluation — not public distribution.
- **Do NOT upload weights** to Hugging Face or any other platform until the ADAPTER_PREVIEW_GATE is satisfied.
- **Do NOT commit adapters** to the Git repository. See `docs/ADAPTER_ARTIFACT_POLICY.md`.
- **Do NOT claim benchmark scores** until a formal evaluation is completed and verified.
- **Do NOT train in CI.** Real training requires GPU hardware. CI validates with `--dry-run` only.
- **Do NOT bind servers to 0.0.0.0** without authentication.
- **Do NOT use private user data, secrets, or copyrighted content** in training data.
- **Do NOT publish** without explicit approval through `docs/ADAPTER_PREVIEW_GATE.md`.
- **DO NOT commit training outputs.** See `docs/PRIVATE_RUN_ARTIFACTS.md` for what stays local.
- **DO NOT upload to Hugging Face.** See `docs/ADAPTER_ARTIFACT_POLICY.md`.

---

## Recommended GPU Types

| GPU | VRAM | LoRA on SmolLM3-3B | QLoRA on SmolLM3-3B | Approx. Cost/hr (RunPod) | Notes |
|-----|------|---------------------|----------------------|--------------------------|-------|
| **RTX 4090** | 24 GB | ✅ Comfortable | ✅ Comfortable | ~$0.74 | **Best value for 3B LoRA** |
| **L40S** | 48 GB | ✅ Overkill | ✅ Overkill | ~$1.25 | Great if also planning ORPO/DPO |
| **A100 40GB** | 40 GB | ✅ Comfortable | ✅ Comfortable | ~$1.29 | Enterprise reliability |
| **A100 80GB** | 80 GB | ✅ Overkill | ✅ Overkill | ~$2.21 | Only if planning multi-GPU or larger models |
| RTX 3090 | 24 GB | ✅ Works | ✅ Works | ~$0.50 | Budget option, check availability |
| RTX 4080 | 16 GB | ⚠️ Tight for LoRA | ✅ Works with QLoRA | ~$0.54 | LoRA may need gradient checkpointing |

**Recommendation:** Start with an **RTX 4090 (24 GB)** for the first SFT LoRA run. It provides the best balance of cost, VRAM, and availability.

---

## Expected VRAM Usage — SmolLM3-3B with LoRA

| Configuration | Base Model VRAM | LoRA Adapter VRAM | Gradients + Optimizer | Total Estimated | Fits 24 GB? |
|---------------|-----------------|--------------------|-----------------------|-----------------|-------------|
| LoRA (r=32, bf16) | ~6 GB | ~0.2 GB | ~4–6 GB | **~12–14 GB** | ✅ Yes, comfortably |
| LoRA (r=32, fp32 optimizer) | ~6 GB | ~0.2 GB | ~8–10 GB | **~16–18 GB** | ✅ Yes, with room |
| QLoRA (4-bit, r=32) | ~2 GB | ~0.2 GB | ~3–4 GB | **~6–8 GB** | ✅ Yes, plenty of room |
| LoRA + gradient checkpointing | ~6 GB | ~0.2 GB | ~3–4 GB | **~10–12 GB** | ✅ Yes, conservatively |

> **Note:** These are estimates. Actual VRAM depends on sequence length, batch size, and gradient accumulation settings. Always monitor `nvidia-smi` during the first few training steps.

---

## Step 1: Provision a GPU Instance on RunPod

### 1a: Create a RunPod account

1. Go to [runpod.io](https://runpod.io) and create an account
2. Add a payment method
3. Navigate to **GPU Cloud** → **Deploy**

### 1b: Select GPU and template

- **GPU:** RTX 4090 (24 GB) or better
- **Template:** PyTorch 2.1+ (Ubuntu 22.04) — or a blank Ubuntu with Python 3.10+
- **Storage:** Minimum **50 GB** container disk (model weights ~6 GB + dataset + adapter + checkpoints)
- **Ports:** No public ports needed for training

> **⚠️ Safety reminder:** Do NOT expose Jupyter or SSH ports publicly. Use RunPod's built-in terminal or SSH tunnel.

### 1c: Start the instance

1. Click **Deploy**
2. Wait for the instance to reach **Running** status
3. Open the **Jupyter Lab** or **Terminal** interface from the RunPod console

---

## Step 2: Python 3.10+ Setup

### 2a: Verify Python version

```bash
python3 --version
# Must be 3.10 or higher
```

If Python 3.10+ is not available:

```bash
# Ubuntu/Debian
sudo add-apt-repository ppa:deadsnakes/ppa -y
sudo apt update
sudo apt install python3.10 python3.10-venv python3.10-dev -y
```

### 2b: Verify CUDA

```bash
nvidia-smi
# Should show GPU name, driver version, CUDA version

nvcc --version
# Should match CUDA version from nvidia-smi
```

> **⚠️ If `nvidia-smi` fails or shows no GPU, the instance was not provisioned correctly. Terminate and recreate.**

---

## Step 3: Create Virtual Environment

### 3a: Create an isolated training venv

```bash
# Clone the repository (or mount your storage volume)
cd /workspace  # RunPod default workspace
git clone https://github.com/smouj/kimari-local-ai.git
cd kimari-local-ai

# Create a dedicated training virtual environment
python3 -m venv .venv-training

# Activate
source .venv-training/bin/activate

# Upgrade pip
pip install --upgrade pip setuptools wheel
```

### 3b: Install PyTorch with CUDA support

```bash
# Check CUDA version from nvidia-smi output
# CUDA 12.1 (most common on RunPod):
pip install torch --index-url https://download.pytorch.org/whl/cu121

# CUDA 12.4:
# pip install torch --index-url https://download.pytorch.org/whl/cu124

# Verify
python -c "import torch; print(f'PyTorch: {torch.__version__}'); print(f'CUDA available: {torch.cuda.is_available()}'); print(f'GPU: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else \"N/A\"}')"
```

> **⚠️ If `CUDA available: False`, your PyTorch was installed without CUDA support. Reinstall with the correct `--index-url`.**

---

## Step 4: Install Repo + Training Extras

### 4a: Install training dependencies

```bash
# Install training-specific dependencies (separated from runtime)
pip install -r training/requirements-training.txt
```

This installs: `torch`, `transformers`, `datasets`, `accelerate`, `peft`, `trl`, `safetensors`, `pyyaml`, `sentencepiece`, `protobuf`.

> **Why separated?** Training dependencies (PyTorch, PEFT, TRL) are heavy and not needed for the runtime CLI. See `training/requirements-training.txt` for per-dependency rationale.

### 4b: Install Kimari package in development mode

```bash
pip install -e .
```

### 4c: Verify all dependencies

```bash
python -c "
import torch; print(f'torch: {torch.__version__}')
import transformers; print(f'transformers: {transformers.__version__}')
import datasets; print(f'datasets: {datasets.__version__}')
import peft; print(f'peft: {peft.__version__}')
import trl; print(f'trl: {trl.__version__}')
import accelerate; print(f'accelerate: {accelerate.__version__}')
import safetensors; print(f'safetensors: {safetensors.__version__}')
print('All training dependencies installed.')
"
```

---

## Step 5: Configure HF Cache Outside Repo

Hugging Face downloads model weights to a cache directory. On RunPod, you want this cache on the persistent `/workspace` volume, not inside the container's temporary storage.

### 5a: Set HF_HOME environment variable

```bash
# Create a cache directory on persistent storage
mkdir -p /workspace/.cache/huggingface

# Set environment variables
export HF_HOME=/workspace/.cache/huggingface
export HF_HUB_CACHE=/workspace/.cache/huggingface/hub
export CUDA_HOME=/usr/local/cuda  # Adjust if needed

# Add to .bashrc for persistence
echo 'export HF_HOME=/workspace/.cache/huggingface' >> ~/.bashrc
echo 'export HF_HUB_CACHE=/workspace/.cache/huggingface/hub' >> ~/.bashrc
echo 'export CUDA_HOME=/usr/local/cuda' >> ~/.bashrc
source ~/.bashrc
```

### 5b: Verify cache configuration

```bash
echo "HF_HOME: $HF_HOME"
echo "HF_HUB_CACHE: $HF_HUB_CACHE"
echo "CUDA_HOME: $CUDA_HOME"
```

> **⚠️ If `HF_HOME` is not set, model weights will be downloaded to `~/.cache/huggingface` which may be on temporary storage and lost when the instance stops.**

### 5c: Disable WandB (unless explicitly using it)

```bash
export WANDB_MODE=disabled
echo 'export WANDB_MODE=disabled' >> ~/.bashrc
```

> **⚠️ Do not leave WandB in "online" mode on a rented GPU. It may upload training data to a public dashboard.**

---

## Step 6: Build Dataset v0

Build the training-ready dataset from the v0 source files.

```bash
# Ensure training venv is active
source .venv-training/bin/activate

# Build the dataset mix
python training/scripts/build_dataset_mix.py \
    --sft dataset/v0/sft_v0.jsonl \
    --preference dataset/v0/preference_v0.jsonl \
    --holdout dataset/v0/eval_holdout.jsonl \
    --output-dir dataset/build/kimari-v0 \
    --shuffle \
    --seed 42 \
    --report
```

**Verify the build:**

```bash
# Check the report
python -m json.tool dataset/build/kimari-v0/report.json

# Verify files exist
ls -la dataset/build/kimari-v0/
```

> **⚠️ Ensure all dataset files in `dataset/v0/` are synthetic and MIT-compatible. No private data, secrets, or copyrighted content.**

---

## Step 7: Run Dry-Run Validation

Validate the training pipeline without actually training.

### 7a: Validate training readiness

```bash
python training/scripts/validate_training_ready.py \
    --base-config training/configs/base_candidates.yaml \
    --sft dataset/v0/sft_v0.jsonl \
    --preference dataset/v0/preference_v0.jsonl \
    --holdout dataset/v0/eval_holdout.jsonl \
    --json
```

### 7b: Dry-run the SFT configuration

```bash
python training/scripts/train_sft_lora.py \
    --dry-run \
    --config training/configs/kimari_sft_lora.v0.example.yaml
```

Expected output: the script should print "DRY RUN" and exit successfully.

### 7c: Run the pre-flight script

```bash
python training/scripts/preflight_private_sft.py \
    --run-config training/configs/private_sft_run.v0.yaml \
    --json
```

This checks:
- Run config exists and is valid
- GPU and CUDA are available
- Dataset files exist and pass validation
- SFT config is valid
- Output directory is gitignored or outside repo
- No HF upload is configured
- Preview gate starts as BLOCKED

> **⚠️ Do NOT proceed to Step 8 if any dry-run or pre-flight check fails. Fix all errors before continuing.**

---

## Step 8: Execute Real Training Manually

> **⚠️ This step requires GPU hardware and MUST NOT run in CI.**

### 8a: Review the execution config

```bash
# Copy and customize the execution config for your environment
cp training/configs/private_sft_execution.example.yaml \
   training/configs/private_sft_execution.runpod.yaml

# Edit for your environment
# - Set gpu_type (e.g., RTX 4090)
# - Set expected_vram_gb (e.g., 24)
# - Set hf_cache_dir (e.g., /workspace/.cache/huggingface)
# - Set output_dir (e.g., training/adapters/kimari-smollm3-sft-v0)
# - Set dataset_build_dir (e.g., dataset/build/kimari-v0)
```

### 8b: Run SFT training

```bash
# Ensure training environment is active
source .venv-training/bin/activate

# Ensure HF cache is configured
export HF_HOME=/workspace/.cache/huggingface
export WANDB_MODE=disabled

# Run SFT training with LoRA
python training/scripts/train_sft_lora.py \
    --config training/configs/kimari_sft_lora.v0.example.yaml
```

### 8c: Monitor training

During training, monitor in a **separate terminal**:

```bash
# GPU utilization and temperature
watch -n 5 nvidia-smi

# Training loss (check the output directory for logs)
ls -la training/adapters/kimari-smollm3-sft-v0/

# Disk space
df -h /workspace
```

**What to watch for:**

| Metric | Expected | Problem |
|--------|----------|---------|
| GPU utilization | > 90% during steps | < 50% → data loading bottleneck |
| GPU temperature | < 85°C | > 90°C → thermal throttling risk |
| Training loss | Steady decrease | Spikes/NaN → learning rate too high |
| Disk space | > 10 GB free | Running out → reduce `save_steps` or clear old checkpoints |

### 8d: Training time estimates

| GPU | LoRA on SmolLM3-3B (2 epochs) | QLoRA on SmolLM3-3B (2 epochs) |
|-----|-------------------------------|----------------------------------|
| RTX 4090 | ~30–60 min | ~20–40 min |
| L40S | ~25–50 min | ~15–35 min |
| A100 40GB | ~20–40 min | ~12–30 min |

> **Note:** Actual time depends on dataset size, sequence length, and batch size. These are rough estimates for ~100 SFT samples.

---

## Step 9: Post-Run Validation

### 9a: Run the post-run script

```bash
python training/scripts/postrun_private_sft.py \
    --run-config training/configs/private_sft_run.v0.yaml \
    --adapter-dir training/adapters/kimari-smollm3-sft-v0 \
    --dry-run \
    --json
```

This checks:
- Adapter files exist
- Adapter config is valid
- No unexpected files in the adapter directory
- Hashes can be computed
- Preview gate remains BLOCKED
- No HF upload configured

### 9b: Verify adapter output

```bash
# Check adapter directory contents
ls -la training/adapters/kimari-smollm3-sft-v0/

# Expected files:
# adapter_model.safetensors  — LoRA adapter weights (DO NOT commit)
# adapter_config.json        — LoRA configuration
# tokenizer.json             — Tokenizer from base model
# tokenizer_config.json      — Tokenizer configuration
# special_tokens_map.json    — Special tokens mapping
# trainer_state.json         — Training state
# all_results.json           — Training results summary
```

### 9c: Record hashes

```bash
sha256sum training/adapters/kimari-smollm3-sft-v0/adapter_model.safetensors
sha256sum training/adapters/kimari-smollm3-sft-v0/adapter_config.json
```

### 9d: Create adapter manifest

```bash
python training/scripts/create_adapter_manifest.py \
    --run-config training/configs/private_sft_run.v0.yaml \
    --adapter-dir training/adapters/kimari-smollm3-sft-v0 \
    --output training/adapters/kimari-smollm3-sft-v0/MANIFEST.yaml
```

Verify the manifest has:
- `preview_gate_state: BLOCKED`
- `public_release_allowed: false`
- `hf_upload_allowed: false`

---

## Step 10: Copy Only Sanitized Results

> **⚠️ NEVER copy raw adapter weights, optimizer states, checkpoints, or raw eval outputs off the GPU machine. Only sanitized metadata leaves the training environment.**

### 10a: Files that CAN be copied (sanitized)

| File | Conditions | Purpose |
|------|-----------|---------|
| `MANIFEST.yaml` | Must NOT contain sensitive local paths (e.g., `/workspace/...`). Replace with relative paths. | Records adapter metadata and gate state |
| `eval_summary.json` | Must NOT contain raw prompts or model responses. Use `create_eval_summary.py`. | Records aggregate eval results |
| `compare_summary.json` | Must NOT contain private prompt content. | Records baseline vs adapter comparison |
| `adapter_config.json` | Contains only LoRA hyperparameters (rank, alpha, target modules). | Documents adapter architecture |
| `all_results.json` | Training metrics only (loss, runtime). No weights. | Records training outcome |

### 10b: How to sanitize the manifest

```bash
# Copy manifest and remove sensitive paths
cp training/adapters/kimari-smollm3-sft-v0/MANIFEST.yaml /tmp/MANIFEST_sanitized.yaml

# Edit to replace absolute paths with relative paths
# Example: /workspace/kimari-local-ai/training/adapters/... → training/adapters/...
sed -i 's|/workspace/kimari-local-ai/||g' /tmp/MANIFEST_sanitized.yaml

# Verify no sensitive paths remain
rg '/workspace' /tmp/MANIFEST_sanitized.yaml  # Should find nothing
rg '/home/' /tmp/MANIFEST_sanitized.yaml      # Should find nothing
rg 'hf_' /tmp/MANIFEST_sanitized.yaml         # Should find no tokens
```

### 10c: How to sanitize eval results

```bash
python eval/scripts/create_eval_summary.py \
    --input eval/results/adapter-smollm3-sft-v0-q4km.json \
    --output eval/results/adapter-smollm3-sft-v0-q4km-summary.json
```

This strips all `prompt` and `response` fields. See `docs/PRIVATE_EVAL_RESULTS_POLICY.md`.

### 10d: Transfer sanitized files off the GPU machine

```bash
# Use scp (from your local machine)
scp user@gpu-host:/tmp/MANIFEST_sanitized.yaml ./training/adapters/kimari-smollm3-sft-v0/MANIFEST.yaml
scp user@gpu-host:/tmp/eval_summary.json ./eval/results/

# Or use RunPod's file browser to download
# Or use a private S3 bucket
```

> **⚠️ NEVER use public file sharing services (Google Drive public links, Dropbox public folders, etc.) to transfer adapter artifacts.**

---

## DO NOT Upload to Hugging Face

**Under no circumstances should any training output be uploaded to Hugging Face during this run.**

- Do not create a Hugging Face repository with model files
- Do not use `huggingface-cli upload` or `push_to_hub`
- Do not claim the model is "released" or "available"
- Do not publish benchmark scores

The `hf_upload_allowed: false` flag in the run config enforces this. See `docs/ADAPTER_PREVIEW_GATE.md` for the release state machine.

---

## DO NOT Commit Training Outputs

**The following must NEVER be committed to Git:**

- `adapter_model.safetensors` — LoRA adapter weights
- `optimizer.pt` / `rng_state.pth` — Optimizer states
- `checkpoint-*/` — Training checkpoints
- `runs/` — TensorBoard event files
- `wandb/` — WandB local cache
- Raw eval output files with prompt/response content

See `docs/PRIVATE_RUN_ARTIFACTS.md` for the complete list of what stays local and what can be committed.

---

## Pre-Flight and Post-Run Scripts Reference

| Script | Purpose | When to Run |
|--------|---------|-------------|
| `training/scripts/validate_training_ready.py` | Validates dataset, config, and environment before training | Before dry-run |
| `training/scripts/preflight_private_sft.py` | Comprehensive pre-flight check (GPU, CUDA, dataset, config, gitignore, gate) | After dry-run, before real training |
| `training/scripts/build_dataset_mix.py` | Builds the training-ready dataset from v0 sources | Before dry-run |
| `training/scripts/train_sft_lora.py --dry-run` | Validates training pipeline without training | After dataset build |
| `training/scripts/create_adapter_manifest.py` | Generates adapter manifest with BLOCKED state | After training completes |
| `training/scripts/postrun_private_sft.py` | Post-run validation (files, hashes, gate state, no upload) | After manifest creation |
| `eval/scripts/create_eval_summary.py` | Strips sensitive fields from eval results | Before copying results off GPU |

---

## Storage Estimates

| Item | Size | Notes |
|------|------|-------|
| SmolLM3-3B weights (fp16) | ~6 GB | Downloaded from HF Hub |
| LoRA adapter output | ~50–200 MB | Depends on rank and target modules |
| Training checkpoints (2–3) | ~1–3 GB | Each checkpoint is roughly the adapter size |
| Dataset v0 | ~1–5 MB | JSONL files, very small |
| Built dataset | ~1–5 MB | Processed JSONL files |
| Eval results | ~100 KB–1 MB | Small JSON files |
| Python venv | ~3–5 GB | Training dependencies |
| **Total recommended storage** | **~50 GB** | Comfortable margin for all of the above |

### Disk usage during training

```bash
# Monitor disk usage during training
du -sh /workspace/*
df -h /workspace
```

---

## Cost Estimates

| GPU | Cost/hr (RunPod) | Estimated Training Time | Estimated Total Cost |
|-----|-------------------|------------------------|---------------------|
| RTX 4090 | ~$0.74 | 30–60 min | **~$0.40–0.75** |
| L40S | ~$1.25 | 25–50 min | **~$0.55–1.05** |
| A100 40GB | ~$1.29 | 20–40 min | **~$0.45–0.90** |

**Additional costs:**

| Item | Cost | Notes |
|------|------|-------|
| RunPod storage | ~$0.10/GB/month | Persistent storage |
| Data transfer | Usually free | Inbound data on RunPod |
| Instance boot time | ~2–5 min | Not billable on most providers |

> **Tip:** Budget for 2× the estimated training time to account for setup, debugging, and a potential re-run. Total budget for first run: **~$2–5**.

---

## Safety Reminders

Throughout the entire process, keep these rules in mind:

1. **Private training only** — the adapter is for internal evaluation, not distribution
2. **No HF upload** — do not upload weights to any platform
3. **No committing weights** — adapter files stay out of Git
4. **No benchmark claims** — do not publish or claim scores
5. **No public file sharing** — use secure transfer methods only
6. **No binding to 0.0.0.0** — keep all servers on 127.0.0.1
7. **No secrets in data** — no private keys, tokens, or credentials in training data
8. **Gate stays BLOCKED** — no automatic transitions, see `docs/ADAPTER_PREVIEW_GATE.md`
9. **Sanitize before copying** — replace absolute paths, strip prompts/responses
10. **Terminate the instance** — shut down the GPU instance when not actively training

---

## Termination Checklist

Before terminating the RunPod instance:

- [ ] Adapter manifest created and sanitized
- [ ] Eval summaries (if any) sanitized and transferred
- [ ] Hashes recorded locally
- [ ] No unsaved work in the terminal
- [ ] No adapter weights accidentally committed to Git
- [ ] No sensitive data left on the instance's temporary storage
- [ ] WANDB_MODE was disabled (no public uploads occurred)
- [ ] Preview gate remains BLOCKED

---

## Related Documents

| Document | Relationship |
|----------|-------------|
| [PRIVATE_TRAINING_RUNBOOK.md](PRIVATE_TRAINING_RUNBOOK.md) | Step-by-step runbook for first private SFT |
| [FIRST_PRIVATE_TRAINING_RUN.md](FIRST_PRIVATE_TRAINING_RUN.md) | General private training guide |
| [ADAPTER_ARTIFACT_POLICY.md](ADAPTER_ARTIFACT_POLICY.md) | What can and cannot be committed |
| [ADAPTER_PREVIEW_GATE.md](ADAPTER_PREVIEW_GATE.md) | State machine for adapter release |
| [PRIVATE_RUN_ARTIFACTS.md](PRIVATE_RUN_ARTIFACTS.md) | What stays local vs what can be committed |
| [PRIVATE_RUN_FAILURES.md](PRIVATE_RUN_FAILURES.md) | Troubleshooting guide for private run failures |
| [PRIVATE_EVAL_RESULTS_POLICY.md](PRIVATE_EVAL_RESULTS_POLICY.md) | What eval results can be committed |
| [PRIVATE_SFT_EXECUTION_CHECKLIST.md](PRIVATE_SFT_EXECUTION_CHECKLIST.md) | Pre-flight checklist for SFT run |
| [BASE_MODEL_ACCEPTANCE.md](BASE_MODEL_ACCEPTANCE.md) | Formal acceptance record for SmolLM3-3B |
| [SFT_TO_ORPO_DECISION.md](SFT_TO_ORPO_DECISION.md) | Decision framework for proceeding to ORPO |
| [training/requirements-training.txt](../training/requirements-training.txt) | Separated training dependencies |
| [training/configs/private_sft_execution.example.yaml](../training/configs/private_sft_execution.example.yaml) | Execution config template |

---

*This guide governs running the first private SFT on a remote GPU cloud. The output adapter is for internal evaluation only. No weights are published without passing the ADAPTER_PREVIEW_GATE. Every step requires human judgment and verification. Terminate GPU instances when not in use.*
