# HF Jobs Fallback Runners

If Hugging Face Jobs is not available for your account, you can still validate Kimari using alternative GPU runners.

## Fallback Options

### 1. Local GTX 1060 Smoke

The simplest fallback — run the smoke test locally on your GPU.

**Requirements:**
- NVIDIA GPU with CUDA support
- llama-server compiled with CUDA
- A test GGUF model (TinyLlama)

**Steps:**
```bash
kimari doctor --deep
kimari start --profile test --dry-run
kimari start --profile test
```

**Result:** Local inference validation (see `docs/GTX1060_LOCAL_RUNTIME_RESULT.md` for example)

### 2. RunPod

Rent a GPU instance for testing.

**Steps:**
1. Create a RunPod account
2. Launch a GPU pod (RTX 4090, A100, etc.)
3. SSH into the pod
4. Clone and install Kimari
5. Run smoke validation

**Artifacts that can be committed:**
- Sanitized summary JSONs (with `gate_state: BLOCKED`, `training_performed: false`)
- Result documentation (following safe screenshot guidelines)

**Artifacts that must NOT be committed:**
- Raw logs with tokens/paths
- Adapter files (.safetensors, .bin, .pt)
- Model files (.gguf)
- Any file containing private data

### 3. Generic SSH GPU VM

Use any cloud GPU provider (AWS, GCP, Lambda Labs, etc.).

**Steps:**
1. Provision a GPU VM
2. Install NVIDIA drivers + CUDA
3. Install Kimari
4. Run smoke validation

### 4. Docker Local Testing

Run llama-server in Docker with GPU passthrough.

**Steps:**
```bash
docker run --gpus all -v ~/.config/kimari:/root/.config/kimari ...
```

## Gate Status

All fallback runners maintain the same gate policy:

- Gate state: **BLOCKED**
- Training: not performed
- HF upload: not performed
- Adapter commit: not performed

## Which Artifacts Can Enter the Repo

| Artifact | Can Commit? | Notes |
|----------|-------------|-------|
| Sanitized summary JSON | ✅ | Must have `gate_state: BLOCKED` |
| Example/template JSON | ✅ | `.example.json` / `.template.json` |
| Documentation | ✅ | No private data |
| Raw logs | ❌ | May contain tokens/paths |
| Adapter files | ❌ | .safetensors, .bin, .pt, .pth |
| Model files | ❌ | .gguf |
| Checkpoint files | ❌ | Any training checkpoint |

## Safety

- No tokens in any committed file
- No billing/plan/subscription details in any committed file
- No private account information
- Gate remains BLOCKED for all results
