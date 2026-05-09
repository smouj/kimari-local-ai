# Kimari — Tech Stack Compatibility

> **Last updated:** v0.1.4-alpha
> **Document ID:** 00-11

---

## Supported GPUs

Kimari targets **consumer-grade NVIDIA GPUs** with CUDA compute capability 6.1+.

| GPU | VRAM | Compute Cap. | Status | Notes |
|-----|------|-------------|--------|-------|
| GTX 1060 (6 GB) | 6 GB | 6.1 | ✅ Supported | Minimum spec; Q4_K_M models only |
| GTX 1070 (8 GB) | 8 GB | 6.1 | ✅ Supported | Q4_K_M to Q5_K_M |
| GTX 1080 (8 GB) | 8 GB | 6.1 | ✅ Supported | Q4_K_M to Q5_K_M |
| GTX 1080 Ti (11 GB) | 11 GB | 6.1 | ✅ Supported | Q5_K_M to Q6_K |
| RTX 2060 (6 GB) | 6 GB | 7.5 | ✅ Supported | Same limits as GTX 1060 |
| RTX 2060 Super (8 GB) | 8 GB | 7.5 | ✅ Supported | |
| RTX 2070 (8 GB) | 8 GB | 7.5 | ✅ Supported | |
| RTX 2080 (8 GB) | 8 GB | 7.5 | ✅ Supported | |
| RTX 2080 Ti (11 GB) | 11 GB | 7.5 | ✅ Supported | |
| RTX 3050 (8 GB) | 8 GB | 8.6 | ✅ Supported | |
| RTX 3060 (12 GB) | 12 GB | 8.6 | ✅ Supported | Sweet spot for 7B Q8_0 |
| RTX 3060 Ti (8 GB) | 8 GB | 8.6 | ✅ Supported | |
| RTX 3070 (8 GB) | 8 GB | 8.6 | ✅ Supported | |
| RTX 3070 Ti (8 GB) | 8 GB | 8.6 | ✅ Supported | |
| RTX 3080 (10 GB) | 10 GB | 8.6 | ✅ Supported | |
| RTX 3080 Ti (12 GB) | 12 GB | 8.6 | ✅ Supported | |
| RTX 3090 (24 GB) | 24 GB | 8.6 | ✅ Supported | Can run 13B Q4_K_M |
| RTX 4060 (8 GB) | 8 GB | 8.9 | ✅ Supported | |
| RTX 4060 Ti (16 GB) | 16 GB | 8.9 | ✅ Supported | Good for 13B Q4_K_M |
| RTX 4070 (12 GB) | 12 GB | 8.9 | ✅ Supported | |
| RTX 4070 Ti (12 GB) | 12 GB | 8.9 | ✅ Supported | |
| RTX 4080 (16 GB) | 16 GB | 8.9 | ✅ Supported | |
| RTX 4090 (24 GB) | 24 GB | 8.9 | ✅ Supported | Can run 13B+ at higher quants |
| RTX 4090 D (24 GB) | 24 GB | 8.9 | ✅ Supported | China-export variant |

### Unsupported GPUs

| GPU | Reason |
|-----|--------|
| GTX 900 series and older | Compute capability < 6.1 |
| AMD Radeon (all) | No CUDA support; ROCm build script available but untested |
| Intel Arc (all) | Not tested; no CUDA support |
| Apple M1/M2/M3/M4 | No CUDA; Metal backend not yet implemented |

---

## Operating System Support

| OS | Version | Status | Notes |
|----|---------|--------|-------|
| Ubuntu | 20.04 LTS | ✅ Primary | Best-tested platform |
| Ubuntu | 22.04 LTS | ✅ Primary | Recommended |
| Ubuntu | 24.04 LTS | ✅ Supported | May need manual CUDA install |
| Debian | 11 (Bullseye) | ✅ Supported | |
| Debian | 12 (Bookworm) | ✅ Supported | |
| Fedora | 39+ | ⚠️ Experimental | May need NVIDIA repo setup |
| Windows | 10 (21H2+) | ✅ Supported | Via WSL2 or native |
| Windows | 11 | ✅ Supported | Via WSL2 or native |
| WSL2 | Ubuntu 22.04 | ✅ Supported | Requires WSLg for GPU passthrough |
| macOS | Any | ❌ Not supported | No CUDA on Apple Silicon |

---

## CUDA Toolkit Versions

| CUDA Version | GCC Compatible | Status |
|-------------|----------------|--------|
| 11.8 | GCC 9 – 11 | ✅ Supported (minimum) |
| 12.1 | GCC 9 – 12 | ✅ Recommended |
| 12.4 | GCC 9 – 13 | ✅ Supported (latest tested) |
| 12.6+ | GCC 9 – 13 | ⚠️ Untested |

### Installation

```bash
# Ubuntu — CUDA 12.1
sudo apt install nvidia-cuda-toolkit

# Or via NVIDIA's official repo:
wget https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2204/x86_64/cuda-keyring_1.1-1_all.deb
sudo dpkg -i cuda-keyring_1.1-1_all.deb
sudo apt update && sudo apt install cuda-toolkit-12-1
```

---

## Python Versions

| Python | Status | Notes |
|--------|--------|-------|
| 3.10.x | ✅ Supported | Minimum version |
| 3.11.x | ✅ Recommended | Best performance |
| 3.12.x | ✅ Supported | Tested |
| 3.13.x | ⚠️ Experimental | Some C extensions may not build |
| 3.9 and older | ❌ Not supported | llama.cpp Python bindings require 3.10+ |

### Dependencies

```
# pyproject.toml (pip install -e .)
requests>=2.31.0

# requirements-dev.txt (pip install -e ".[dev]")
pytest>=7.0
ruff>=0.1.0
jsonschema>=4.0
```

---

## llama.cpp Build Requirements

### Build Tools

| Tool | Minimum Version |
|------|----------------|
| CMake | 3.16+ |
| GCC | 9+ (Linux) |
| MSVC | 2019+ (Windows) |
| Make | 4.2+ (optional) |
| NVIDIA driver | 525.60+ (Linux), 528.33+ (Windows) |

### Build Commands

```bash
# Clone
git clone https://github.com/ggerganov/llama.cpp.git
cd llama.cpp

# Build with CUDA
cmake -B build -DGGML_CUDA=ON
cmake --build build -j$(nproc)

# The resulting binary:
./build/bin/llama-server --help
```

### Build Options

| CMake Flag | Description | Default |
|-----------|-------------|---------|
| `GGML_CUDA=ON` | Enable CUDA GPU acceleration | OFF |
| `GGML_CUDA_F16=ON` | Use FP16 for prompt processing (faster) | OFF |
| `LLAMA_CURL=ON` | Enable remote model download | OFF |
| `LLAMA_BUILD_SERVER=ON` | Build the HTTP server | ON |
| `CMAKE_BUILD_TYPE=Release` | Optimized build | Release |

---

## Memory Requirements by Profile

| Profile | Model Size | Quantization | GPU VRAM | System RAM |
|---------|-----------|-------------|----------|------------|
| `gtx1060` | ~4B | Q4_K_M | 6 GB | 8 GB |
| `gtx1080` | ~4B | Q5_K_M | 8 GB | 8 GB |
| `turbo` | ~4B | IQ4_XS | 6 GB | 8 GB |
| `test` | 1.1B | Q4_K_M | 6 GB | 8 GB |
| `docker` | ~4B | Q4_K_M | 6 GB | 8 GB |

> VRAM estimates include model weights + KV cache for profile-specific context windows.
> Larger contexts require additional VRAM (~0.5 GB per 2048 tokens).

---

## Known Incompatibilities

| Issue | Affected | Workaround |
|-------|----------|------------|
| NVIDIA driver 525.x on Ubuntu 24.04 | Ubuntu 24.04 | Upgrade to driver 535+ via `ubuntu-drivers` |
| CUDA 12.4 with GCC 14 | Fedora 40 | Use GCC 13: `sudo dnf install gcc-toolset-13` |
| WSL2 GPU passthrough | Windows 11 builds < 22621 | Update Windows to latest build |
| llama.cpp with MSVC and CUDA | Visual Studio 2022 v17.8+ | Use v17.7 or build with Ninja |
| RTX 40-series + old driver | Driver < 535 | Update NVIDIA driver |
| 6 GB VRAM + 13B model | GTX 1060, RTX 2060 | Use 7B models only |
| `--cont-batching` with 1 GPU | All | Requires multiple GPUs; omit the flag |
