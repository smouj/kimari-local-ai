# Kimari Local AI — WSL2 Installation Guide

Complete guide for running Kimari on Windows 10/11 using WSL2 (Windows Subsystem for Linux).

## Prerequisites

| Requirement | Minimum |
|-------------|---------|
| Windows | 10 (build 19044+) or 11 |
| WSL2 | Installed and configured |
| NVIDIA GPU | GTX 1060 6 GB or better |
| NVIDIA Driver | 525+ (Windows side) |
| CUDA on WSL | Supported via NVIDIA CUDA on WSL |
| Disk Space | 5 GB+ (models need more) |

## Step 1: Install WSL2

Open PowerShell as Administrator:

```powershell
wsl --install
```

Restart your computer when prompted. This installs Ubuntu by default.

Verify WSL2 is running:

```powershell
wsl --status
# Should show: Default Version: 2
```

If you already have WSL1, upgrade:

```powershell
wsl --set-default-version 2
```

## Step 2: Set Up Ubuntu

Launch Ubuntu from the Start menu or run:

```powershell
wsl -d Ubuntu
```

Update packages:

```bash
sudo apt update && sudo apt upgrade -y
```

Install build dependencies:

```bash
sudo apt install -y build-essential cmake git python3 python3-pip python3-venv
```

## Step 3: NVIDIA Driver and CUDA on WSL

**On the Windows side**, install the latest NVIDIA Game Ready or Studio Driver:
- Download from: https://www.nvidia.com/Download/index.aspx
- Version 525+ is required for CUDA on WSL2

**Inside WSL2**, verify GPU access:

```bash
nvidia-smi
```

You should see your GPU listed. If not:

1. Make sure the Windows NVIDIA driver is up to date
2. Make sure you're running WSL2 (not WSL1): `wsl -l -v`
3. Restart WSL: `wsl --shutdown` then relaunch

**Note:** You do NOT need to install the NVIDIA driver inside WSL2. The Windows driver provides CUDA access through WSL2.

## Step 4: CUDA Toolkit (WSL2)

Install the CUDA toolkit for WSL2:

```bash
# Add NVIDIA package repository
wget https://developer.download.nvidia.com/compute/cuda/repos/wsl-ubuntu/x86_64/cuda-keyring_1.1-1_all.deb
sudo dpkg -i cuda-keyring_1.1-1_all.deb
sudo apt update
sudo apt install -y cuda-toolkit-12-4
rm cuda-keyring_1.1-1_all.deb
```

Verify:

```bash
nvcc --version
```

## Step 5: Clone and Install Kimari

```bash
# Clone the repository
git clone https://github.com/smouj/kimari-local-ai.git
cd kimari-local-ai

# Install Kimari
pip install -e .

# Or with dev dependencies
pip install -e ".[dev]"
```

## Step 6: Build llama.cpp with CUDA

```bash
bash scripts/linux/build-llamacpp-cuda.sh
```

This builds llama-server with CUDA acceleration. It may take 5-10 minutes.

## Step 7: Verify Setup

```bash
kimari doctor
```

Expected output:
- OS: Linux (WSL2)
- GPU: Your NVIDIA GPU
- CUDA: Available
- llama-server: Found
- Port: 11435 available

## Step 8: Download a Test Model

```bash
kimari pull test
```

This downloads TinyLlama 1.1B (approximately 800 MB), which fits on any 6 GB GPU.

## Step 9: Start the Server

```bash
kimari start
```

The server starts on `http://127.0.0.1:11435` using the `test` profile by default.

## Step 10: Chat with the Model

```bash
kimari chat "Hello, Kimari!"
```

Or open the API endpoint in a tool like Open WebUI.

## Optional: Open WebUI Integration

If you want a full web chat interface:

```bash
# Start Kimari with docker profile
kimari start --profile docker --daemon

# Launch Open WebUI
make webui-up
```

Open your browser at `http://localhost:3000`.

> **Note:** Open WebUI runs in Docker Desktop. Make sure Docker Desktop is running with WSL2 backend enabled (Settings → General → "Use the WSL 2 based engine").

## Troubleshooting

### `nvidia-smi` not found inside WSL2

- Make sure you're running WSL2, not WSL1: `wsl -l -v`
- Update the Windows NVIDIA driver to 525+
- Restart WSL: `wsl --shutdown` then relaunch Ubuntu
- Do NOT install nvidia drivers inside WSL2 — they come from Windows

### `nvcc` not found

- Install the CUDA toolkit for WSL2 (Step 4)
- Add to PATH: `echo 'export PATH=/usr/local/cuda/bin:$PATH' >> ~/.bashrc && source ~/.bashrc`

### `llama-server` not found

- Run the build script: `bash scripts/linux/build-llamacpp-cuda.sh`
- If build fails, check that cmake and build-essential are installed
- Set the path manually: `export LLAMA_SERVER=/path/to/llama-server`

### Port 11435 busy

```bash
# Find what's using the port
sudo lsof -i :11435

# Kill the process if needed
kimari stop
```

### Model not found

```bash
# Download the test model first
kimari pull test

# Verify it exists
ls -la models/tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf
```

### CUDA out of memory

- Use the `test` profile (TinyLlama, only 0.7 GB VRAM)
- Reduce context: `kimari start --ctx 2048`
- Check GPU memory: `nvidia-smi`

## File Access

WSL2 can access Windows files at `/mnt/c/`, and Windows can access WSL files at `\\wsl$\Ubuntu\`.

However, for performance, **clone and run Kimari inside the WSL2 filesystem** (not under `/mnt/c/`).

## Next Steps

- [Getting Started](../GETTING_STARTED.md) — 10-minute quick start guide
- [Architecture](00-03_architecture.md) — How Kimari works
- [Roadmap](../ROADMAP.md) — Future plans
