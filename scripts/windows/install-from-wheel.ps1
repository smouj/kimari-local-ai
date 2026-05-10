# install-from-wheel.ps1 — Install Kimari Local AI from a local wheel file
# Usage: powershell -ExecutionPolicy Bypass -File scripts\windows\install-from-wheel.ps1 -WheelPath dist\kimari_local_ai-0.1.15-py3-none-any.whl
#        powershell -ExecutionPolicy Bypass -File scripts\windows\install-from-wheel.ps1 -WheelPath dist\kimari_local_ai-0.1.15-py3-none-any.whl -VenvPath .venv

[CmdletBinding()]
param(
    [Parameter(Mandatory = $true, HelpMessage = "Path to the .whl file to install")]
    [string]$WheelPath,

    [Parameter(Mandatory = $false, HelpMessage = "Path to create/activate a virtual environment")]
    [string]$VenvPath
)

$ErrorActionPreference = "Stop"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Kimari Local AI - Install from Wheel" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# --- Validate Python 3.10+ ---
Write-Host "[0/5] Validating Python version..." -ForegroundColor Yellow

$pythonCmd = "python"
$pyVersion = $null

try {
    $pyVersionRaw = & python --version 2>&1
    if ($pyVersionRaw -match "Python (\d+)\.(\d+)") {
        $pyMajor = [int]$Matches[1]
        $pyMinor = [int]$Matches[2]
        if ($pyMajor -lt 3 -or ($pyMajor -eq 3 -and $pyMinor -lt 10)) {
            Write-Host "[ERROR] Python 3.10+ is required. Detected: $pyVersionRaw" -ForegroundColor Red
            Write-Host "  Download Python 3.10+ from https://www.python.org/downloads/" -ForegroundColor Red
            exit 1
        }
        $pyVersion = "$pyMajor.$pyMinor"
        Write-Host "  Python version: $pyVersionRaw" -ForegroundColor Green
    } else {
        Write-Host "[WARN] Could not parse Python version from: $pyVersionRaw" -ForegroundColor Yellow
    }
} catch {
    Write-Host "[ERROR] Python not found. Install Python 3.10+ and ensure it is on PATH." -ForegroundColor Red
    exit 1
}

# --- Validate wheel path ---
if (-not (Test-Path $WheelPath)) {
    Write-Host "[ERROR] Wheel file not found: $WheelPath" -ForegroundColor Red
    exit 1
}

$WheelPath = (Resolve-Path $WheelPath).Path
Write-Host "  Wheel: $WheelPath" -ForegroundColor White

# --- Step 1: Create venv if requested ---
if ($VenvPath) {
    Write-Host ""
    Write-Host "[1/5] Creating virtual environment at $VenvPath..." -ForegroundColor Yellow

    & python -m venv $VenvPath
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[ERROR] Failed to create virtual environment." -ForegroundColor Red
        exit 1
    }

    # Activate the venv
    $activateScript = Join-Path $VenvPath "Scripts\Activate.ps1"
    if (-not (Test-Path $activateScript)) {
        Write-Host "[ERROR] Activation script not found: $activateScript" -ForegroundColor Red
        exit 1
    }

    . $activateScript
    Write-Host "  Virtual environment created and activated." -ForegroundColor Green
} else {
    Write-Host ""
    Write-Host "[1/5] Skipping venv creation (no -VenvPath provided)." -ForegroundColor Yellow
    Write-Host "  TIP: Use -VenvPath .venv to install in an isolated environment." -ForegroundColor DarkGray
}

# --- Step 2: Install the wheel ---
Write-Host ""
Write-Host "[2/5] Installing wheel..." -ForegroundColor Yellow

& python -m pip install --quiet $WheelPath
if ($LASTEXITCODE -ne 0) {
    Write-Host "[ERROR] Failed to install wheel." -ForegroundColor Red
    exit 1
}
Write-Host "  Wheel installed successfully." -ForegroundColor Green

# --- Step 3: Verify installation ---
Write-Host ""
Write-Host "[3/5] Verifying installation..." -ForegroundColor Yellow

Write-Host "  Running: kimari --version" -ForegroundColor Gray
& kimari --version
if ($LASTEXITCODE -ne 0) {
    Write-Host "[WARN] kimari --version failed (may need PATH restart)" -ForegroundColor Yellow
    Write-Host "  Fallback: python -m kimari.cli.main --version" -ForegroundColor DarkGray
} else {
    Write-Host "  kimari --version OK" -ForegroundColor Green
}

Write-Host ""
Write-Host "  Running: kimari setup --json" -ForegroundColor Gray
& kimari setup --json
if ($LASTEXITCODE -ne 0) {
    Write-Host "[WARN] kimari setup --json failed" -ForegroundColor Yellow
} else {
    Write-Host "  kimari setup --json OK" -ForegroundColor Green
}

# --- Step 4: Dry-run start ---
Write-Host ""
Write-Host "[4/5] Dry-run start..." -ForegroundColor Yellow

Write-Host "  Running: kimari start --dry-run" -ForegroundColor Gray
& kimari start --dry-run
if ($LASTEXITCODE -ne 0) {
    Write-Host "[WARN] kimari start --dry-run failed" -ForegroundColor Yellow
} else {
    Write-Host "  Dry-run passed." -ForegroundColor Green
}

# --- Step 5: Check CUDA / llama-server ---
Write-Host ""
Write-Host "[5/5] Checking CUDA and llama-server..." -ForegroundColor Yellow

$cudaAvailable = $false
$llamaServerAvailable = $false

try {
    $nvidiaSmi = & nvidia-smi --query-gpu=name --format=csv,noheader 2>&1
    if ($LASTEXITCODE -eq 0) {
        $cudaAvailable = $true
        Write-Host "  CUDA: Detected ($nvidiaSmi)" -ForegroundColor Green
    }
} catch {
    # nvidia-smi not available
}

if (-not $cudaAvailable) {
    Write-Host "  CUDA: Not detected" -ForegroundColor Yellow
    Write-Host "  Kimari can run in CPU-only mode, but GPU acceleration is much faster." -ForegroundColor Yellow
    Write-Host "  Install CUDA Toolkit from https://developer.nvidia.com/cuda-downloads" -ForegroundColor DarkGray
}

try {
    $llamaVer = & llama-server --version 2>&1
    if ($LASTEXITCODE -eq 0) {
        $llamaServerAvailable = $true
        Write-Host "  llama-server: Detected" -ForegroundColor Green
    }
} catch {
    # llama-server not on PATH
}

if (-not $llamaServerAvailable) {
    # Check LLAMA_SERVER env var
    $llamaEnv = $env:LLAMA_SERVER
    if ($llamaEnv -and (Test-Path $llamaEnv)) {
        $llamaServerAvailable = $true
        Write-Host "  llama-server: Detected via LLAMA_SERVER env ($llamaEnv)" -ForegroundColor Green
    } else {
        Write-Host "  llama-server: Not found" -ForegroundColor Yellow
        Write-Host "  Without llama-server, you cannot start GPU inference." -ForegroundColor Yellow
        Write-Host "  Build from source: https://github.com/ggerganov/llama.cpp" -ForegroundColor DarkGray
        Write-Host "  Or set env: `$env:LLAMA_SERVER = 'C:\path\to\llama-server.exe'" -ForegroundColor DarkGray
    }
}

# --- Summary ---
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Installation Complete" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "  Installed from: $WheelPath" -ForegroundColor Green
if ($VenvPath) {
    Write-Host "  Virtual env:    $VenvPath" -ForegroundColor Green
}
Write-Host ""
Write-Host "  Next steps:" -ForegroundColor Yellow
Write-Host "    kimari doctor          # Check system requirements"
Write-Host "    kimari pull test       # Download test model"
Write-Host "    kimari start           # Start the server"
Write-Host ""
Write-Host "  NOTE: Models are NOT auto-downloaded. Run 'kimari pull test' to get a model." -ForegroundColor Yellow

# --- PowerShell ExecutionPolicy Note ---
Write-Host ""
Write-Host "NOTE: If you encountered execution policy errors, run one of:" -ForegroundColor Yellow
Write-Host "  Set-ExecutionPolicy -Scope CurrentUser RemoteSigned" -ForegroundColor White
Write-Host "  powershell -ExecutionPolicy Bypass -File <script.ps1>" -ForegroundColor White
