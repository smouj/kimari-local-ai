# Kimari Local Runtime Setup

## Document: 00-04 Local Runtime Configuration
**Version:** 0.1.0
**Status:** Draft
**Last Updated:** 2025

---

## Overview

This document covers setting up the llama.cpp runtime that powers Kimari. It includes instructions for building from source, installing pre-built binaries, CUDA configuration, and performance tuning.

## Prerequisites

### Hardware Requirements

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| GPU | NVIDIA GTX 1060 (6 GB) | NVIDIA GTX 1080 (8 GB) |
| RAM | 8 GB | 16 GB |
| Disk | 5 GB free | 10 GB free (SSD recommended) |
| CPU | 4 cores | 6+ cores |

### Software Requirements

| Software | Version | Purpose |
|----------|---------|---------|
| NVIDIA Driver | 525+ | GPU support |
| CUDA Toolkit | 11.0+ | Building llama.cpp (optional for pre-built) |
| Python | 3.10+ | Kimari CLI |
| CMake | 3.18+ | Building from source |
| Git | 2.x | Cloning repos |

## Installation Methods

### Method 1: Pre-built Binary (Recommended for Quick Start)

1. **Download llama.cpp releases** from [GitHub](https://github.com/ggerganov/llama.cpp/releases)
2. Choose the CUDA-enabled build for your platform
3. Extract `llama-server` to `server/bin/`

```bash
# Linux
mkdir -p server/bin
# Download and extract the appropriate release
# Place llama-server in server/bin/
chmod +x server/bin/llama-server
```

### Method 2: Build from Source (Recommended for Performance)

```bash
# Use Kimari's build script
bash scripts/linux/build-llamacpp-cuda.sh
```

This script will:
1. Clone llama.cpp if not present
2. Detect your GPU architecture
3. Configure with CUDA support
4. Build with optimizations
5. Install to `server/bin/`

### Method 3: Install via Package Manager

```bash
# On some systems, llama.cpp is available via package managers
# Check if available for your distro

# Arch Linux (AUR)
yay -S llama.cpp-cuda

# Then symlink to Kimari's server/bin/
```

## CUDA Configuration

### Verify CUDA Installation

```bash
# Check NVIDIA driver
nvidia-smi

# Check CUDA compiler (if building from source)
nvcc --version

# Check CUDA runtime
python3 -c "import torch; print(torch.cuda.is_available())"  # if PyTorch installed
```

### GPU Architecture

llama.cpp needs to be compiled for your specific GPU architecture. The build script auto-detects this:

| GPU | Compute Capability | Flag |
|-----|-------------------|------|
| GTX 1060 | sm_61 | `-DLLAMA_CUDA_ARCH=61` |
| GTX 1070 | sm_61 | `-DLLAMA_CUDA_ARCH=61` |
| GTX 1080 | sm_61 | `-DLLAMA_CUDA_ARCH=61` |
| RTX 2060 | sm_75 | `-DLLAMA_CUDA_ARCH=75` |
| RTX 3060 | sm_86 | `-DLLAMA_CUDA_ARCH=86` |
| RTX 4060 | sm_89 | `-DLLAMA_CUDA_ARCH=89` |

If auto-detection fails, set it manually:

```bash
cd server/llama.cpp/build/cuda
cmake .. -DLLAMA_CUDA=ON -DLLAMA_CUDA_ARCH=61  # for GTX 1060/1080
make -j$(nproc)
```

## Model Setup

### Downloading Models

Models are not included in this repository. Download GGUF-quantized models from trusted sources:

**Hugging Face (Recommended):**
```bash
# Example: Download a 3B-4B GGUF model
# Visit https://huggingface.co/ and search for GGUF models
# Use huggingface-cli or wget

# Example with huggingface-cli
pip install huggingface-hub
huggingface-cli download <org>/<model> --local-dir models/
```

**Recommended Models for Kimari:**

| Model | Params | Q4_K_M Size | Source |
|-------|--------|-------------|--------|
| Llama 3.2 3B | 3B | ~2 GB | Meta (Hugging Face) |
| Qwen2.5 3B | 3B | ~2 GB | Alibaba (Hugging Face) |
| Phi-3 Mini 3.8B | 3.8B | ~2.5 GB | Microsoft (Hugging Face) |

### Model Naming Convention

Place models in the `models/` directory with this naming convention:

```
models/
├── Kimari-4B-Q4_K_M.gguf       # Base model, Q4 quantization
├── Kimari-4B-Q5_K_M.gguf       # Base model, Q5 quantization
├── Kimari-4B-IQ4_XS.gguf       # Base model, IQ4 turbo quantization
└── Kimari-4B-Instruct-Q4_K_M.gguf  # Instruct-tuned variant
```

## Performance Tuning

### Context Size

Context size directly affects VRAM usage:

| Context | KV Cache (4B model) | Available for GTX 1060 | Available for GTX 1080 |
|---------|--------------------|-----------------------|-----------------------|
| 4,096 | ~0.5 GB | ~4.0 GB for model | ~6.0 GB for model |
| 8,192 | ~1.0 GB | ~3.5 GB for model | ~5.5 GB for model |
| 16,384 | ~2.0 GB | ~2.5 GB for model | ~4.5 GB for model |
| 32,768 | ~4.0 GB | Not feasible | ~2.5 GB for model |

### Batch Size

- **Batch size (`-b`)**: Number of tokens processed per step. Larger = faster but more VRAM
- **Ubatch size (`-ub`)**: Actual batch size sent to GPU. Should be ≤ batch size

**Recommendations:**
| GPU | Batch | Ubatch |
|-----|-------|--------|
| GTX 1060 (6 GB) | 256 | 128 |
| GTX 1080 (8 GB) | 512 | 256 |

### Flash Attention

Enable flash attention for better performance:
```bash
--flash-attn
```
This reduces memory usage for attention computation and speeds up inference.

### KV Cache Type

KV cache can be quantized to save VRAM:

| Type | VRAM per token | Quality | Use Case |
|------|---------------|---------|----------|
| f16 | Standard | Best | Default for most profiles |
| q8_0 | ~50% less | Very good | Extended context |
| q4_0 | ~75% less | Acceptable | Maximum context |

### Thread Count

Set based on CPU cores (not GPU):
```bash
-t $(nproc)  # Use all cores
-t 4         # Use 4 cores (leave some for system)
```

### NUMA Awareness

On multi-socket systems:
```bash
# Bind to specific NUMA node
numactl --cpunodebind=0 --membind=0 llama-server ...
```

## Troubleshooting

### "CUDA out of memory"

1. Reduce context size (`-c`)
2. Use lower quantization (Q3_K_M instead of Q4_K_M)
3. Reduce batch size (`-b`, `-ub`)
4. Use quantized KV cache (`--cache-type-k q8_0`)

### "llama-server not found"

```bash
# Build from source
bash scripts/linux/build-llamacpp-cuda.sh

# Or add to PATH
export PATH="$PWD/server/bin:$PATH"
```

### Slow Inference

1. Verify CUDA is being used (check `nvidia-smi` during inference)
2. Enable flash attention (`--flash-attn`)
3. Increase batch size if VRAM allows
4. Check GPU thermal throttling
5. Ensure `nvidia-smi -pm 1` (persistence mode) is enabled

### "illegal memory access"

1. Update NVIDIA driver to latest stable
2. Rebuild llama.cpp with correct GPU architecture
3. Disable flash attention temporarily (`--no-flash-attn`)

## Monitoring

### During Inference

```bash
# Watch GPU usage in real-time
watch -n 0.5 nvidia-smi

# Or use nvtop
sudo apt install nvtop
nvtop
```

### Server Logs

```bash
# Kimari logs
tail -f server/kimari.log

# Check memory usage
nvidia-smi --query-gpu=memory.used,memory.total --format=csv -l 1
```

---

*For more information on llama.cpp options, see: https://github.com/ggerganov/llama.cpp*
