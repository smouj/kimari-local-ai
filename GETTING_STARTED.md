# Getting Started with Kimari Local AI

> **10-minute guide to running your first local AI model**

## Prerequisites

- **NVIDIA GPU** (GTX 1060 6GB or better)
- **CUDA Toolkit** 11.8+ ([Download](https://developer.nvidia.com/cuda-downloads))
- **Python** 3.10+
- **Git**
- **8 GB+** system RAM

## Step 1: Clone and Install

```bash
git clone https://github.com/smouj/kimari-local-ai.git
cd kimari-local-ai
pip install -r cli/requirements.txt
```

## Step 2: Run Diagnostics

```bash
python cli/kimari_cli.py doctor
```

This checks your GPU, CUDA, and system setup. Warnings are OK for testing — only FAIL items need fixing.

## Step 3: Download a Model

```bash
# Download the tiny test model (~0.7 GB)
python cli/kimari_cli.py pull test

# Or download a more capable model (~2.7 GB)
python cli/kimari_cli.py pull recommended
```

See all available models:
```bash
python cli/kimari_cli.py pull --list
```

## Step 4: Start the Server

```bash
# With the test profile
python cli/kimari_cli.py start --profile test --daemon

# Or specify a different model
python cli/kimari_cli.py start --profile test --model models/tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf --daemon
```

## Step 5: Chat!

```bash
# Single message
python cli/kimari_cli.py chat "Explain Docker in one paragraph"

# Interactive mode
python cli/kimari_cli.py chat
```

## Step 6: Open WebUI (Optional)

```bash
# Start with Docker profile so Open WebUI can reach the API
python cli/kimari_cli.py stop
python cli/kimari_cli.py start --profile docker --daemon

# Launch Open WebUI
make webui-up

# Open http://localhost:3000
```

## Troubleshooting

### "Model not found"
Run `kimari pull test` or place any GGUF file in `models/`.

### "llama-server not found"
Build it: `bash scripts/linux/build-llamacpp-cuda.sh`
Or set: `export LLAMA_SERVER=/path/to/llama-server`

### "CUDA out of memory"
Use a smaller model or reduce context:
```bash
python cli/kimari_cli.py start --profile test --ctx 2048 --daemon
```

## What Works Today

| Feature | Status |
|---------|--------|
| CLI (doctor, start, stop, status, chat, bench, fit, pull) | ✅ Works |
| llama.cpp runtime with CUDA | ✅ Works |
| Model download (kimari pull) | ✅ Works |
| Open WebUI integration | ✅ Works via Docker |
| Continue IDE integration | ✅ Config ready |
| Kimari-4B model | 🔨 Planned (not released yet) |

## Next Steps

- Read the [full README](README.md)
- Check [GPU profiles](config/kimari.profiles.json)
- Run benchmarks: `python cli/kimari_cli.py bench --profile test --json`
- Calculate KimariFit: `python cli/kimari_cli.py fit --model models/your-model.gguf --ctx 8192`
