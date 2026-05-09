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

# Install as editable package (provides the `kimari` command)
pip install -e .

# Or include dev dependencies (pytest, ruff, jsonschema)
pip install -e ".[dev]"
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

> **SHA256 verification:** `kimari pull` supports hash verification, but model hashes in the registry are not yet pinned. Verification will be enforced once hashes are added in a future release.

## Step 4: Start the Server

```bash
# Start with the default profile (test)
kimari start

# Or specify a profile explicitly
kimari start --profile test

# Preview the command without running it
kimari start --dry-run

# Start in background (daemon mode)
kimari start --daemon
```

> **Note:** The default profile is `test` during alpha (uses TinyLlama 1.1B). You don't need to specify `--profile test` — `kimari start` works out of the box after `kimari pull test`. The `gtx1060` and `gtx1080` profiles will become the defaults once Kimari-4B is released.

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
| `ModuleNotFoundError: requests` | Run `pip install -e .` to install all dependencies |
| Wrong profile used | Default is `test` during alpha. Use `--profile gtx1060` for Kimari-4B when available |

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
kimari start               # Start server (default: test profile)
kimari chat                # Chat with model
kimari status              # Check server status
kimari stop                # Stop server
kimari config validate     # Validate configuration
kimari models              # List models
kimari profiles            # List GPU profiles
```
