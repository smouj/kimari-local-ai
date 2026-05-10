# Windows Scripts for Kimari Local AI

This directory contains PowerShell and batch scripts to help you set up, diagnose, and run Kimari Local AI on Windows.

## Prerequisites

| Requirement | Minimum Version | How to Check |
|---|---|---|
| **Python** | 3.10+ | `python --version` |
| **PowerShell** | 5.1+ | `$PSVersionTable.PSVersion` |
| **NVIDIA GPU + CUDA** | CUDA 11.0+ | `nvidia-smi` |
| **llama-server** | Any | `llama-server --version` or see below |

> **Note:** CUDA is recommended for GPU-accelerated inference. Kimari can run in CPU-only mode without CUDA, but performance will be significantly lower.

## Execution Policy

PowerShell restricts script execution by default. Before running any `.ps1` script, set the execution policy for your user:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

This allows locally-created scripts to run and requires a digital signature for downloaded scripts. You only need to do this once.

If you prefer not to change the policy, you can bypass it per invocation:

```powershell
powershell -ExecutionPolicy Bypass -File .\kimari-launcher.ps1
```

## Quick Start

The fastest way to get Kimari running on Windows:

```powershell
cd kimari-local-ai
.\scripts\windows\kimari-launcher.ps1
```

This single command will:

1. Create and activate a Python virtual environment (`.venv/`)
2. Install Kimari in editable mode (`pip install -e .`)
3. Run system diagnostics (`kimari doctor`)
4. Download a test model if none is found (`kimari pull test`)
5. Start the Kimari server (`kimari start`)

### Launcher Options

| Parameter | Description | Default |
|---|---|---|
| `-SkipVenv` | Skip virtual environment creation/activation | Off |
| `-SkipInstall` | Skip `pip install -e .` | Off |
| `-SkipDoctor` | Skip `kimari doctor` diagnostic | Off |
| `-SkipPull` | Skip model download step | Off |
| `-Profile <name>` | Server profile to use (e.g., `gtx1060`) | Default from config |
| `-Daemon` | Start server in background mode | Off |
| `-VenvPath <path>` | Custom virtual environment path | `.venv` in project root |

**Examples:**

```powershell
# Full setup and launch
.\scripts\windows\kimari-launcher.ps1

# Skip venv/install for rapid relaunch
.\scripts\windows\kimari-launcher.ps1 -SkipVenv -SkipInstall

# Launch with GTX 1060 profile in background
.\scripts\windows\kimari-launcher.ps1 -Profile gtx1060 -Daemon

# Use a custom venv location
.\scripts\windows\kimari-launcher.ps1 -VenvPath C:\venvs\kimari
```

## Diagnostics

Run the diagnostic script to check your system before starting Kimari:

```powershell
.\scripts\windows\kimari-doctor.ps1
```

This checks:

| Check | What It Verifies |
|---|---|
| **Python** | Python 3.10+ is installed and on PATH |
| **CUDA** | NVIDIA GPU and CUDA toolkit are available |
| **llama-server** | The llama-server binary is findable |
| **Models** | At least one GGUF model exists in `models/` |
| **Port** | Port 11435 is available for the server |

The script provides detailed troubleshooting advice for each failing check. It exits with code `0` if all checks pass, or `1` if problems are found.

### Diagnostic Options

| Parameter | Description | Default |
|---|---|---|
| `-Port <number>` | Port to check | `11435` |
| `-Json` | Output results as JSON | Off |

**Examples:**

```powershell
# Standard diagnostics
.\scripts\windows\kimari-doctor.ps1

# Check a custom port
.\scripts\windows\kimari-doctor.ps1 -Port 8080

# JSON output for scripting
.\scripts\windows\kimari-doctor.ps1 -Json
$result = .\scripts\windows\kimari-doctor.ps1 -Json | ConvertFrom-Json
if ($result.all_ok) { Write-Host "All checks passed!" }
```

## Individual Script Descriptions

| Script | Purpose |
|---|---|
| `kimari-launcher.ps1` | Full setup + launch workflow (venv, install, doctor, pull, start) |
| `kimari-doctor.ps1` | System diagnostics with troubleshooting advice |
| `install-dev.ps1` | Install development dependencies and Kimari in editable mode |
| `launch-kimari.bat` | Batch file to start server + open browser (simple, no setup) |
| `start-kimari-1060.ps1` | Start Kimari with the GTX 1060 6GB profile |
| `start-kimari-1080.ps1` | Start Kimari with the GTX 1080 8GB profile |
| `healthcheck.ps1` | Check if the Kimari server is healthy via `/health` endpoint |

### install-dev.ps1

Sets up the development environment:

```powershell
.\scripts\windows\install-dev.ps1
```

Installs dev dependencies from `requirements-dev.txt`, installs Kimari in editable mode with `[dev]` extras, and runs the environment check script.

### launch-kimari.bat

A simple batch file for users who prefer Command Prompt over PowerShell:

```cmd
scripts\windows\launch-kimari.bat
```

Starts the Kimari server in a minimized window, waits for it to be ready, and opens the browser.

### start-kimari-1060.ps1 / start-kimari-1080.ps1

Quick-launch scripts for specific GPU profiles:

```powershell
.\scripts\windows\start-kimari-1060.ps1    # GTX 1060 6GB profile
.\scripts\windows\start-kimari-1080.ps1    # GTX 1080 8GB profile
```

These scripts prefer the `kimari` CLI command if available, falling back to `python -m kimari.cli.main`.

### healthcheck.ps1

Checks server health by querying the `/health` endpoint:

```powershell
.\scripts\windows\healthcheck.ps1
```

Returns exit code `0` if healthy, `1` if not responding.

## Common Troubleshooting

### Python not found

```
[FAIL] Python not found
```

**Solution:** Install Python 3.10 or later from [python.org](https://www.python.org/downloads/). During installation, **check "Add Python to PATH"**. After installing, restart your terminal.

### CUDA not detected

```
[WARN] CUDA: Not detected
```

**Solution:** Install the [CUDA Toolkit](https://developer.nvidia.com/cuda-downloads) from NVIDIA. Select Windows > x86_64 > your version > exe (local). Also ensure your NVIDIA GPU drivers are up to date. If you don't have an NVIDIA GPU, Kimari can run in CPU-only mode (much slower).

### llama-server not found

```
[FAIL] llama-server: Not found
```

**Solutions (pick one):**

1. **Build from source:**
   ```powershell
   git clone https://github.com/ggerganov/llama.cpp
   cd llama.cpp
   cmake -B build -DGGML_CUDA=ON
   cmake --build build --config Release
   # Copy llama-server.exe to the Kimari project root
   copy build\bin\Release\llama-server.exe C:\path\to\kimari-local-ai\
   ```

2. **Set the LLAMA_SERVER environment variable:**
   ```powershell
   $env:LLAMA_SERVER = "C:\path\to\llama-server.exe"
   # Or set permanently:
   [Environment]::SetEnvironmentVariable("LLAMA_SERVER", "C:\path\to\llama-server.exe", "User")
   ```

3. **Download a pre-built binary** from [llama.cpp releases](https://github.com/ggerganov/llama.cpp/releases).

### Port 11435 occupied

```
[WARN] Port: 11435 in use
```

**Solutions:**

1. Stop the existing Kimari server: `kimari stop`
2. Kill the process using the port:
   ```powershell
   # Find the process
   Get-NetTCPConnection -LocalPort 11435
   # Kill it
   Stop-Process -Id <PID> -Force
   ```
3. Use a different port: `kimari start --port 8080`
4. Edit `config/kimari.profiles.json` and change the `port` value in your profile.

### No GGUF model found

```
[WARN] No GGUF models found in models/
```

**Solution:** Download the test model:

```powershell
kimari pull test
```

Or manually download a `.gguf` file from [Hugging Face](https://huggingface.co/models?search=gguf) and place it in the `models/` directory.

### Virtual environment activation fails

```
[FAIL] Failed to activate virtual environment
```

**Solution:** This is usually an execution policy issue. Run:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

Then retry the launcher.

### pip install fails

```
[FAIL] pip install failed
```

**Solutions:**

1. Ensure you're in the Kimari project root directory.
2. Try upgrading pip first: `python -m pip install --upgrade pip`
3. Install manually: `pip install -e .`
4. If behind a proxy, configure pip: `pip config set global.proxy http://proxy:port`

## Installing from Wheel or TestPyPI

### From a Built Wheel

If you have a pre-built `.whl` file:

```powershell
# Create a virtual environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Install from the wheel
pip install .\dist\kimari_local_ai-0.1.14a0-py3-none-any.whl

# Verify
kimari --version
```

### From TestPyPI (When Available)

```powershell
# Create a virtual environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Install from TestPyPI
pip install -i https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ kimari-local-ai

# Verify
kimari --version
```

> **Note:** TestPyPI may not have the latest version immediately. Check the [TestPyPI project page](https://test.pypi.org/project/kimari-local-ai/) for availability.

## Setup and Configuration

### Guided Setup

Kimari can detect your environment and recommend the best configuration:

```powershell
# Detect environment and show recommendations
kimari setup

# JSON output for automation
kimari setup --json

# Persist detected configuration to your user config directory
kimari setup --write
```

The `--write` flag creates a backup before writing and persists the recommended profile, integration settings, and hardware summary.

### Auth Tokens

Create a local auth token for future API or reverse proxy use:

```powershell
# Generate a new token
kimari token create

# Show the current token
kimari token show

# Delete the token
kimari token delete
```

> **Note:** These tokens are prepared for future Kimari API / reverse proxy use. `llama-server` does not apply auth natively. See [docs/REVERSE_PROXY_AUTH.md](../../docs/REVERSE_PROXY_AUTH.md) for reverse proxy setup.

### Model Hash Verification

Verify the integrity of downloaded models:

```powershell
# Compute SHA256 hash of a local model file
kimari models hash .\models\tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf

# Verify a model against the registry
kimari models verify test

# Pin a model's hash to your user registry (dry-run by default)
kimari models pin-hash test
```
