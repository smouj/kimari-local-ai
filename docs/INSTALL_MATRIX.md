# Kimari Installation Matrix

Complete reference for all supported installation methods and platforms.

---

## Installation Methods

| Method | Command | Status | Notes |
|--------|---------|--------|-------|
| Dev install (editable) | `git clone https://github.com/smouj/kimari-local-ai.git && cd kimari-local-ai && pip install -e .` | Working | Recommended for development |
| Wheel install | `pip install dist/kimari_local_ai-*.whl` | Working | For production installs |
| TestPyPI | `pip install -i https://test.pypi.org/simple/ kimari-local-ai` | Planned | Not yet published |
| PyPI | `pip install kimari-local-ai` | Planned | Not yet published |

## Platform Support

| Platform | Method | Status | Notes |
|----------|--------|--------|-------|
| Linux (CUDA) | Same as dev/wheel | Working | Best experience |
| Windows (native) | Same as dev/wheel | Working | Requires Python 3.10+ |
| WSL2 | Same as dev/wheel + CUDA | Working | Recommended for Windows users. See [INSTALL_WSL2.md](INSTALL_WSL2.md) |
| ROCm (AMD) | Same as dev/wheel | Experimental | `hipcc` must be available |

---

## Prerequisites

| Requirement | Minimum | Recommended |
|-------------|---------|-------------|
| Python | 3.10+ | 3.11 or 3.12 |
| pip | Latest | Latest |
| git | 2.30+ | Latest |
| NVIDIA GPU | GTX 1060 6 GB | GTX 1080 8 GB or better |
| NVIDIA Driver | 525+ | Latest Game Ready/Studio |
| CUDA | 11.x+ | 12.x |
| Disk space | 5 GB | 20 GB+ (for models) |

## GPU Notes

- **NVIDIA GPU with CUDA 11.x+** is recommended for GPU-accelerated inference
- Kimari targets consumer GPUs (GTX 1060 6 GB and above)
- CPU-only inference works but is significantly slower
- AMD GPUs require ROCm and `hipcc` — see ROCm section below

### Pascal GPU Compatibility (GTX 1060/1070/1080)

Pascal GPUs (compute capability sm_61) require the **PyTorch cu126 legacy build**. PyTorch cu128 and cu130 dropped sm_61 support.

| GPU Series | Compute Capability | PyTorch Build |
|------------|-------------------|---------------|
| GTX 1060 / 1070 / 1080 / 1080 Ti | sm_61 | cu126 legacy |
| GTX 1650+ / RTX 2060+ | sm_75+ | cu128 / cu130 (default) |

**Install PyTorch cu126 for Pascal GPUs:**

```bash
pip install torch==2.7.1 --index-url https://download.pytorch.org/whl/cu126
```

> **Why:** PyTorch builds cu128+ compile kernels for sm_75+ (Turing and later). On sm_61 GPUs, `torch.cuda.is_available()` returns `True` but training fails with `RuntimeError`. The cu126 build includes sm_61 kernels. Run `kimari doctor --deep` to check compatibility automatically.

## llama-server Build

llama-server must be built separately — it is NOT included in the pip package.

### Linux / WSL2 (CUDA)

```bash
bash scripts/linux/build-llamacpp-cuda.sh
```

### Linux (ROCm)

```bash
bash scripts/linux/build-llamacpp-rocm.sh
```

### Verify

```bash
which llama-server
# or
kimari doctor
```

## Post-Install Steps

### 1. Verify Installation

```bash
kimari --version
kimari doctor
```

### 2. Initial Setup

```bash
kimari setup
```

Configuration is auto-generated on first run with sensible defaults. The default profile is `test` (TinyLlama 1.1B Q4_K_M) which works on any 6 GB GPU.

### 3. Download a Model

```bash
# Download the test model (800 MB, fits on any 6 GB GPU)
kimari pull test
```

### 4. Start the Server

```bash
kimari start
```

### 5. Verify Everything Works

```bash
kimari doctor --deep
```

---

## Detailed Method Instructions

### Dev Install (Editable)

Best for contributors and developers who want to modify Kimari source code.

```bash
# Clone the repository
git clone https://github.com/smouj/kimari-local-ai.git
cd kimari-local-ai

# Install with dev dependencies (recommended)
pip install -e ".[dev]"

# Or install without dev dependencies
pip install -e .

# Verify
kimari --version
```

**Advantages:**
- Edit source code and changes take effect immediately
- Run tests with `pytest`
- Lint with `ruff`

**Updating:**
```bash
git pull
pip install -e .
```

### Wheel Install

Best for production or stable installations where you don't need to edit source.

```bash
# Build the wheel (if building from source)
python -m build

# Install the wheel
pip install dist/kimari_local_ai-*.whl

# Verify
kimari --version
```

**Advantages:**
- Clean installation — no source tree needed
- Reproducible installs
- No risk of accidental source modifications

**Updating:**
```bash
pip install --upgrade path/to/dist/kimari_local_ai-*.whl
```

### TestPyPI Install

For testing pre-release versions published to TestPyPI.

```bash
pip install --index-url https://test.pypi.org/simple/ \
  --extra-index-url https://pypi.org/simple/ \
  kimari-local-ai
```

> **Note**: TestPyPI publication is planned but not yet available. This method will work once the first version is uploaded.

### PyPI Install

For stable public releases.

```bash
pip install kimari-local-ai
```

> **Note**: Kimari is not yet published on PyPI. This method will work after the first stable release.

---

## Platform-Specific Notes

### Linux (CUDA) — Best Experience

Linux with NVIDIA CUDA provides the best Kimari experience:

```bash
# Full setup
git clone https://github.com/smouj/kimari-local-ai.git
cd kimari-local-ai
pip install -e ".[dev]"
bash scripts/linux/build-llamacpp-cuda.sh
kimari setup
kimari pull test
kimari start
```

Verify GPU acceleration:
```bash
nvidia-smi
kimari doctor
```

### Windows (Native)

Windows with native Python works but has some limitations:

```powershell
# Install Python 3.10+ from python.org
# Then in PowerShell:
git clone https://github.com/smouj/kimari-local-ai.git
cd kimari-local-ai
pip install -e .
```

**Limitations:**
- llama-server process handling differs on Windows (no SIGTERM)
- Some scripts in `scripts/linux/` are not available
- Use `scripts/windows/` for Windows-specific scripts

**Windows Scripts:**

| Script | Purpose |
|--------|---------|
| `scripts/windows/install-dev.ps1` | Dev installation |
| `scripts/windows/install-from-wheel.ps1` | Wheel installation |
| `scripts/windows/install-from-testpypi.ps1` | TestPyPI installation |
| `scripts/windows/start-kimari.ps1` | Start Kimari |
| `scripts/windows/healthcheck.ps1` | Health check |
| `scripts/windows/kimari-doctor.ps1` | Doctor check |

### WSL2 — Recommended for Windows Users

WSL2 provides the best Windows experience because it runs a Linux environment with full CUDA support.

See the complete guide: [INSTALL_WSL2.md](INSTALL_WSL2.md)

Quick start:
```bash
# In WSL2 Ubuntu
git clone https://github.com/smouj/kimari-local-ai.git
cd kimari-local-ai
pip install -e .
bash scripts/linux/build-llamacpp-cuda.sh
kimari setup
kimari pull test
kimari start
```

**Key WSL2 requirements:**
- Windows 10 build 19044+ or Windows 11
- NVIDIA Driver 525+ (Windows side)
- WSL2 with Ubuntu
- CUDA toolkit for WSL2

### ROCm (AMD) — Experimental

ROCm support is experimental. It requires `hipcc` to be available.

```bash
# Build llama-server with ROCm
bash scripts/linux/build-llamacpp-rocm.sh

# Verify
which hipcc
kimari doctor
```

**Known limitations:**
- Only tested on limited AMD GPU models
- Performance may vary significantly
- Not all llama.cpp features are supported on ROCm
- Build may fail on some AMD GPU architectures

---

## Troubleshooting

### `kimari` command not found

Ensure the install directory is in your PATH:
```bash
python -m pip show kimari-local-ai
python -c "import kimari; print(kimari.__file__)"
```

### `llama-server` not found

Build it separately:
```bash
bash scripts/linux/build-llamacpp-cuda.sh
```

Or set the path manually:
```bash
export LLAMA_SERVER=/path/to/llama-server
```

### CUDA not detected

```bash
nvidia-smi  # Check GPU is visible
nvcc --version  # Check CUDA toolkit
kimari doctor  # Check Kimari's detection
```

### Port 11435 busy

```bash
kimari stop
# Or find what's using it:
sudo lsof -i :11435
```

---

*See also: [INSTALL_WSL2.md](INSTALL_WSL2.md), [GETTING_STARTED.md](../GETTING_STARTED.md), [CHANGELOG.md](../CHANGELOG.md)*
