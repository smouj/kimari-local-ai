# Kimari — Runtime Validation Guide

> **Document ID:** 11_NEXT
> **Purpose:** Step-by-step guide to validate a full Kimari runtime from scratch.

---

## Overview

This guide walks you through building llama.cpp with CUDA, configuring Kimari,
starting the server, and verifying every component works. Follow each step in
order. If any step fails, refer to the [Troubleshooting](#troubleshooting)
section at the end.

---

## Step 1: Prerequisites Checklist

Before starting, verify your system meets all requirements.

```bash
# Check NVIDIA GPU is detected
nvidia-smi
```

**Expected output:**
```
+-----------------------------------------------------------------------------+
| NVIDIA-SMI 535.129.03   Driver Version: 535.129.03   CUDA Version: 12.4   |
|-------------------------------+----------------------+----------------------+
| GPU  Name        Persistence-M| Bus-Id        Disp.A | Volatile Uncorr. ECC |
| Fan  Temp  Perf  Pwr:Usage/Cap|         Memory-Usage | GPU-Util  Compute M. |
|===============================+======================+======================|
|   0  NVIDIA GeForce ...  Off  | 00000000:01:00.0  On |                  N/A |
|  0%   45C    P8    15W / 200W |     50MiB /  12288MiB |      0%      Default |
+-------------------------------+----------------------+----------------------+
```

```bash
# Check CUDA toolkit is installed
nvcc --version
```

**Expected output:**
```
nvcc: NVIDIA (R) Cuda compiler driver
Copyright (c) 2005-2023 NVIDIA Corporation
Cuda compilation tools, release 12.1, V12.1.105
```

```bash
# Check Python version (3.10+)
python3 --version
```

**Expected output:**
```
Python 3.11.6
```

```bash
# Check CMake is installed (3.16+)
cmake --version
```

**Expected output:**
```
cmake version 3.28.1
```

```bash
# Check build essentials (GCC 9+)
gcc --version
```

**Expected output:**
```
gcc (Ubuntu 13.2.0-5ubuntu1) 13.2.0
```

**If any check fails**, install the missing dependency before proceeding. See
[00-11_tech_stack_compatibility.md](./00-11_tech_stack_compatibility.md) for
detailed version requirements.

---

## Step 2: Build llama.cpp with CUDA

Clone and build llama.cpp with GPU acceleration.

```bash
# Clone the repository
git clone https://github.com/ggerganov/llama.cpp.git
cd llama.cpp

# Configure with CUDA support
cmake -B build -DGGML_CUDA=ON -DGGML_CUDA_F16=ON -DLLAMA_BUILD_SERVER=ON

# Build (use all available CPU cores)
cmake --build build -j$(nproc)
```

**Expected output (last lines):**
```
[100%] Built target llama-server
[100%] Built target llama-cli
```

**Verify the binary exists:**
```bash
./build/bin/llama-server --version
```

**Expected output:**
```
llama-server version 0.0.0 (built with cc 13.2.0)
```

**Verify CUDA is active:**
```bash
./build/bin/llama-server --help 2>&1 | rg -i cuda
```

**Expected output should mention CUDA or GPU:**
```
  --gpu-layers N        Number of layers to offload to GPU ...
```

---

## Step 3: Run `kimari doctor`

Install the Kimari CLI dependencies and run the health check.

```bash
# Navigate to the Kimari project
cd /path/to/kimari-repo

# Install Python dependencies
pip install -r cli/requirements.txt

# Run system diagnostics
python3 cli/kimari_cli.py doctor
```

**Expected output:**
```
╔══════════════════════════════════════════╗
║          KIMARI SYSTEM DOCTOR            ║
╠══════════════════════════════════════════╣
║ GPU .............. NVIDIA GeForce ...  ✅ ║
║ VRAM ............. 12288 MB            ✅ ║
║ CUDA ............. 12.1                ✅ ║
║ Python ........... 3.11.6              ✅ ║
║ llama.cpp ........ found               ✅ ║
║ Config file ...... valid               ✅ ║
╠══════════════════════════════════════════╣
║ OVERALL .......... ALL CHECKS PASSED    ✅ ║
╚══════════════════════════════════════════╝
```

---

## Step 4: Download a Test GGUF Model

Download a small test model from HuggingFace.

```bash
# Create models directory
mkdir -p models

# Download a small test model (Llama 3.2 1B, Q4_K_M)
wget -O models/Llama-3.2-1B-Q4_K_M.gguf \
  "https://huggingface.co/bartowski/Llama-3.2-1B-Instruct-GGUF/resolve/main/Llama-3.2-1B-Instruct-Q4_K_M.gguf"
```

**Expected output:**
```
Saving to: 'models/Llama-3.2-1B-Q4_K_M.gguf'
models/Llama-3.2-1B-Q4_K_M.gguf  100%[===================>]  800MB  12.3MB/s  in 65s
```

**Verify the file:**
```bash
ls -lh models/Llama-3.2-1B-Q4_K_M.gguf
```

**Expected output:**
```
-rw-r--r-- 1 user user 800M Jun 15 10:00 models/Llama-3.2-1B-Q4_K_M.gguf
```

---

## Step 5: Start Server with `kimari start`

Launch the llama.cpp server through Kimari.

```bash
python3 cli/kimari_cli.py start --model models/Llama-3.2-1B-Q4_K_M.gguf --port 11435
```

**Expected output:**
```
[INFO] Loading model: models/Llama-3.2-1B-Q4_K_M.gguf
[INFO] GPU layers: 17/17
[INFO] Context size: 4096
[INFO] Server starting on http://127.0.0.1:11435
[INFO] Model loaded successfully
llama-server listening on http://127.0.0.1:11435
```

> The server will keep running in the foreground. Open a **new terminal** for
> the remaining steps.

---

## Step 6: Verify with Healthcheck

Run the healthcheck to confirm the server is responding.

**Linux:**
```bash
bash scripts/linux/healthcheck.sh
```

**Or manually:**
```bash
curl -s http://127.0.0.1:11435/health
```

**Expected output:**
```json
{"status":"ok"}
```

**Check loaded model:**
```bash
curl -s http://127.0.0.1:11435/v1/models
```

**Expected output:**
```json
{
  "data": [
    {
      "id": "Llama-3.2-1B-Q4_K_M",
      "object": "model",
      "owned_by": "local",
      "context_length": 4096
    }
  ]
}
```

---

## Step 7: Test Chat via CLI

Use Kimari's interactive chat to verify the model responds.

```bash
python3 cli/kimari_cli.py chat --url http://127.0.0.1:11435
```

**Type a test prompt:**
```
You: What is 2 + 2?
```

**Expected response:**
```
Kimari: 2 + 2 = 4
```

**Exit the chat:**
```
You: /exit
```

**Expected output:**
```
[INFO] Chat session ended. Goodbye!
```

---

## Step 8: Test Chat via API (curl)

Send a direct API request to verify the OpenAI-compatible endpoint.

```bash
curl -s http://127.0.0.1:11435/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "Llama-3.2-1B-Q4_K_M",
    "messages": [
      {"role": "user", "content": "Say hello in exactly 3 words."}
    ],
    "max_tokens": 20,
    "temperature": 0.3
  }' | python3 -m json.tool
```

**Expected output:**
```json
{
  "id": "chatcmpl-abc123",
  "object": "chat.completion",
  "created": 1718000000,
  "model": "Llama-3.2-1B-Q4_K_M",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "Hello there friend"
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 15,
    "completion_tokens": 4,
    "total_tokens": 19
  }
}
```

---

## Step 9: Run Benchmarks

Measure token throughput to validate GPU performance.

```bash
python3 cli/kimari_cli.py bench --url http://127.0.0.1:11435 --model Llama-3.2-1B-Q4_K_M
```

**Expected output:**
```
╔══════════════════════════════════════════╗
║         KIMARI BENCHMARK RESULTS         ║
╠══════════════════════════════════════════╣
║ Model ....... Llama-3.2-1B-Q4_K_M       ║
║ GPU ......... NVIDIA GeForce RTX 3060    ║
║ VRAM ........ 12288 MB                   ║
╠══════════════════════════════════════════╣
║ Prompt eval  ..... XX.X t/s             ║
║ Token gen ....... XX.X t/s              ║
║ Total time ....... X.Xs                 ║
╚══════════════════════════════════════════╝
```

> The actual numbers depend on your GPU. As a rough guide:
> - **GTX 1060 (6 GB):** ~10–20 t/s prompt eval, ~15–25 t/s generation
> - **RTX 3060 (12 GB):** ~50–80 t/s prompt eval, ~30–50 t/s generation
> - **RTX 4090 (24 GB):** ~200+ t/s prompt eval, ~80+ t/s generation

---

## Step 10: Interpret Results

Use this checklist to determine if your setup is healthy:

| Metric | Healthy Range | Action if Low |
|--------|--------------|---------------|
| Prompt eval (t/s) | Varies by GPU (see table above) | Check CUDA is active, GPU layers = all |
| Token gen (t/s) | Varies by GPU | Reduce context size, check VRAM usage |
| VRAM utilization | 70–95% of total VRAM | Expected; means model fits in GPU |
| CPU usage | Low (<30%) during inference | If high, GPU offload may not be working |
| Time to first token | <3s | If slow, reduce model size or use lower quant |

**Check GPU offload is working:**
```bash
nvidia-smi
```

You should see the llama.cpp process using significant GPU memory:

```
+-----------------------------------------------------------------------------+
| Processes:                                                                  |
|  GPU   GI   CI        PID   Type   Process name                  GPU Memory |
|        ID   ID                                                   Usage      |
|=============================================================================|
|    0   N/A  N/A      1234      G   /path/to/llama-server            4500MiB |
+-----------------------------------------------------------------------------+
```

---

## Step 11: Troubleshooting Common Issues

### "CUDA error: no kernel image is available"

**Cause:** The CUDA arch for your GPU is not included in the build.

**Fix:**
```bash
cmake -B build -DGGML_CUDA=ON -DCMAKE_CUDA_ARCHITECTURES=native
cmake --build build -j$(nproc)
```

---

### "Address already in use" (port 11435)

**Cause:** Another instance of the server is running.

**Fix:**
```bash
# Find the process using port 11435
lsof -i :11435

# Kill it
kill -9 <PID>
```

---

### "Model too large for GPU"

**Cause:** The model requires more VRAM than available.

**Fix:**
- Use a lower quantization (Q4_K_M instead of Q8_0)
- Reduce the context size: `--ctx-size 2048`
- Use a smaller model (1B instead of 7B)

```bash
# Example: reduce context to 2048
python3 cli/kimari_cli.py start --model models/Llama-3.2-1B-Q4_K_M.gguf --ctx-size 2048
```

---

### "llama.cpp: command not found"

**Cause:** The binary is not in your PATH, or the build failed.

**Fix:**
```bash
# Check if binary exists
ls -la /path/to/llama.cpp/build/bin/llama-server

# Add to PATH or use full path
export PATH="/path/to/llama.cpp/build/bin:$PATH"
```

---

### "nvidia-smi: command not found"

**Cause:** NVIDIA drivers are not installed.

**Fix (Ubuntu):**
```bash
sudo ubuntu-drivers autoinstall
sudo reboot
```

---

### "nvcc: command not found" (but nvidia-smi works)

**Cause:** CUDA toolkit is installed but not in PATH.

**Fix:**
```bash
echo 'export PATH=/usr/local/cuda/bin:$PATH' >> ~/.bashrc
echo 'export LD_LIBRARY_PATH=/usr/local/cuda/lib64:$LD_LIBRARY_PATH' >> ~/.bashrc
source ~/.bashrc
```

---

### Slow inference (high CPU, low GPU usage)

**Cause:** GPU offload is not active.

**Fix:**
```bash
# Rebuild with CUDA explicitly
cd llama.cpp
cmake -B build -DGGML_CUDA=ON -DGGML_CUDA_F16=ON
cmake --build build -j$(nproc)

# Verify CUDA is listed in build output:
cmake -B build -DGGML_CUDA=ON 2>&1 | rg -i cuda
```

---

### Server starts but returns 502 / connection refused

**Cause:** Server not listening on the expected port.

**Fix:**
```bash
# Check what port the server is actually listening on
ss -tlnp | rg llama

# Verify the port matches your client config
curl -v http://127.0.0.1:11435/health
```

---

## Quick Validation Script

Run this one-liner to validate the full pipeline:

```bash
bash scripts/linux/smoke-test.sh
```

This script automates healthcheck, chat test, and benchmark in a single run.

---

## Summary

| Step | Command | Pass Criteria |
|------|---------|---------------|
| 1. Prerequisites | `nvidia-smi && nvcc --version && python3 --version` | All commands succeed |
| 2. Build llama.cpp | `cmake -B build -DGGML_CUDA=ON && cmake --build build` | Binary exists |
| 3. Doctor | `python3 cli/kimari_cli.py doctor` | All checks ✅ |
| 4. Download model | `wget ...` | File exists, ~800 MB |
| 5. Start server | `python3 cli/kimari_cli.py start` | "Server starting" message |
| 6. Healthcheck | `curl http://127.0.0.1:11435/health` | `{"status":"ok"}` |
| 7. CLI chat | `python3 cli/kimari_cli.py chat` | Model responds |
| 8. API chat | `curl .../v1/chat/completions` | Valid JSON response |
| 9. Benchmark | `python3 cli/kimari_cli.py bench` | Token rates displayed |
