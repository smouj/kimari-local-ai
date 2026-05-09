# Getting Started with Kimari Local AI

> Get from zero to running inference in under 10 minutes.

## Prerequisites

| Requirement | Minimum | Recommended |
|-------------|---------|-------------|
| NVIDIA GPU | GTX 1060 6GB | GTX 1080 8GB+ |
| CUDA Toolkit | 11.8 | 12.4 |
| Python | 3.10 | 3.12 |
| System RAM | 8 GB | 16 GB |
| Disk space | 5 GB | 10 GB |

## Step 1: Install

```bash
# Clone the repository
git clone https://github.com/smouj/kimari-local-ai.git
cd kimari-local-ai

# Option A: Install as package (recommended)
pip install -e .

# Option B: Install dependencies only
pip install -r cli/requirements.txt
```

## Step 2: Check Your System

```bash
kimari doctor
```

This checks your GPU, CUDA, Python version, and configuration. Some warnings are expected if you don't have a GPU in your current environment.

## Step 3: Download a Model

```bash
# Download the test model (TinyLlama 1.1B, ~700 MB)
kimari pull test

# List all available models
kimari pull --list

# Download the recommended model (Qwen3-4B, ~2.7 GB)
kimari pull recommended
```

## Step 4: Start the Server

```bash
# Start with the test profile
kimari start --profile test

# Or preview the command without running it
kimari start --profile test --dry-run

# Start in background (daemon mode)
kimari start --profile test --daemon
```

## Step 5: Chat

```bash
# Single message
kimari chat "Explain Docker containers briefly"

# Interactive mode
kimari chat
```

## Step 6: Open WebUI (Optional)

```bash
# Start with Docker profile (listens on 0.0.0.0)
kimari start --profile docker --daemon

# Launch Open WebUI
make webui-up

# Open http://localhost:3000 in your browser
```

> ⚠️ **Security:** The `docker` profile binds to `0.0.0.0`, which makes the API accessible from other machines on your network. Only use this on trusted local networks.

## Troubleshooting

| Problem | Solution |
|---------|----------|
| `llama-server not found` | Build it: `bash scripts/linux/build-llamacpp-cuda.sh` or set `LLAMA_SERVER=/path/to/binary` |
| `Model not found` | Run `kimari pull test` or use `--model models/your-model.gguf` |
| `Port 11435 in use` | Run `kimari stop` or use `--port 8080` |
| No GPU detected | Install NVIDIA drivers and CUDA Toolkit. Use `kimari fit --vram 6.0` for manual VRAM |
| `ModuleNotFoundError: requests` | Run `pip install -r cli/requirements.txt` |

## Next Steps

- Read the [README](README.md) for full command reference
- Check [docs/COMPARISON.md](docs/COMPARISON.md) to compare Kimari with alternatives
- See [docs/PROJECT_STRUCTURE.md](docs/PROJECT_STRUCTURE.md) to understand the codebase
- Read [SECURITY.md](SECURITY.md) for security best practices

## Quick Reference

```bash
kimari doctor              # Check system
kimari info                # Show installation info
kimari pull test           # Download test model
kimari start --profile test  # Start server
kimari chat                # Chat with model
kimari status              # Check server status
kimari stop                # Stop server
kimari config validate     # Validate configuration
kimari models              # List models
kimari profiles            # List GPU profiles
```
