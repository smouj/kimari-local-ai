<#
.SYNOPSIS
    Comprehensive launcher for Kimari Local AI on Windows.
.DESCRIPTION
    This script automates the full Kimari setup and launch workflow:
      1. Optionally creates/activates a Python virtual environment
      2. Installs Kimari in editable mode (pip install -e .)
      3. Runs system diagnostics (kimari doctor)
      4. Downloads a test model if none found (kimari pull test)
      5. Starts the Kimari server (kimari start)

    Each step provides clear, colored output and handles errors gracefully.
.PARAMETER SkipVenv
    Skip virtual environment creation/activation. Useful if you already
    have an active venv or prefer a global install.
.PARAMETER SkipInstall
    Skip the pip install -e . step. Useful for rapid relaunching.
.PARAMETER SkipDoctor
    Skip the kimari doctor diagnostic step.
.PARAMETER SkipPull
    Skip the model pull step even if no model is found.
.PARAMETER Profile
    Profile name to use when starting the server (default: test).
.PARAMETER Daemon
    Start the server in daemon/background mode.
.PARAMETER VenvPath
    Path to the virtual environment directory (default: .venv in project root).
.EXAMPLE
    .\kimari-launcher.ps1
    Full workflow: venv + install + doctor + pull + start.
.EXAMPLE
    .\kimari-launcher.ps1 -SkipVenv -SkipInstall
    Skip venv and install, just doctor + pull + start.
.EXAMPLE
    .\kimari-launcher.ps1 -Profile gtx1060 -Daemon
    Launch with GTX 1060 profile in background mode.
.NOTES
    Requires Python 3.10+ and PowerShell 5.1+.
    If you get an execution policy error, run:
      Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
#>

[CmdletBinding()]
param(
    [switch]$SkipVenv,
    [switch]$SkipInstall,
    [switch]$SkipDoctor,
    [switch]$SkipPull,
    [string]$Profile = "",
    [switch]$Daemon,
    [string]$VenvPath = ""
)

$ErrorActionPreference = "Stop"

# ─── Helper Functions ──────────────────────────────────────────────────────────

function Write-Step {
    param([string]$Message)
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host "  $Message" -ForegroundColor Cyan
    Write-Host "========================================" -ForegroundColor Cyan
}

function Write-Ok {
    param([string]$Message)
    Write-Host "  [OK]   $Message" -ForegroundColor Green
}

function Write-Warn {
    param([string]$Message)
    Write-Host "  [WARN] $Message" -ForegroundColor Yellow
}

function Write-Fail {
    param([string]$Message)
    Write-Host "  [FAIL] $Message" -ForegroundColor Red
}

function Write-Info {
    param([string]$Message)
    Write-Host "  [INFO] $Message" -ForegroundColor Cyan
}

function Write-Detail {
    param([string]$Message)
    Write-Host "         $Message" -ForegroundColor Gray
}

function Test-Command {
    param([string]$Name)
    return [bool](Get-Command $Name -ErrorAction SilentlyContinue)
}

# ─── Project Root ──────────────────────────────────────────────────────────────

$KIMARI_ROOT = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
if (-not $VenvPath) {
    $VenvPath = Join-Path $KIMARI_ROOT ".venv"
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Magenta
Write-Host "  Kimari Local AI - Launcher" -ForegroundColor Magenta
Write-Host "========================================" -ForegroundColor Magenta
Write-Host "  Project: $KIMARI_ROOT" -ForegroundColor Gray
Write-Host "  Venv:    $VenvPath" -ForegroundColor Gray
Write-Host ""

# ─── Step 0: Check Python ──────────────────────────────────────────────────────

Write-Step "Step 0/5 — Checking Python"

$pythonCmd = $null
foreach ($cmd in @("python", "python3", "py")) {
    if (Test-Command $cmd) {
        try {
            $ver = & $cmd --version 2>&1
            $verStr = $ver.ToString()
            if ($verStr -match "(\d+)\.(\d+)") {
                $major = [int]$Matches[1]
                $minor = [int]$Matches[2]
                if ($major -gt 3 -or ($major -eq 3 -and $minor -ge 10)) {
                    $pythonCmd = $cmd
                    Write-Ok "Found: $verStr ($cmd)"
                    break
                } else {
                    Write-Warn "$cmd is $verStr (need 3.10+)"
                }
            }
        } catch {
            # Skip this command
        }
    }
}

if (-not $pythonCmd) {
    Write-Fail "Python 3.10+ not found."
    Write-Detail "Install Python from: https://www.python.org/downloads/"
    Write-Detail "Make sure to check 'Add Python to PATH' during installation."
    exit 1
}

# ─── Step 1: Virtual Environment ──────────────────────────────────────────────

if (-not $SkipVenv) {
    Write-Step "Step 1/5 — Virtual Environment"

    if (Test-Path (Join-Path $VenvPath "Scripts\Activate.ps1")) {
        Write-Ok "Virtual environment exists at: $VenvPath"
        Write-Info "Activating..."
        try {
            & (Join-Path $VenvPath "Scripts\Activate.ps1")
            Write-Ok "Virtual environment activated."
        } catch {
            Write-Fail "Failed to activate virtual environment: $_"
            Write-Detail "Try running: Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser"
            exit 1
        }
    } else {
        Write-Info "Creating virtual environment at: $VenvPath"
        try {
            & $pythonCmd -m venv $VenvPath
            Write-Ok "Virtual environment created."
            & (Join-Path $VenvPath "Scripts\Activate.ps1")
            Write-Ok "Virtual environment activated."
            # Update pythonCmd to use venv python
            $pythonCmd = Join-Path $VenvPath "Scripts\python.exe"
        } catch {
            Write-Fail "Failed to create virtual environment: $_"
            Write-Detail "Ensure you have the 'venv' module available."
            Write-Detail "On some systems, install it with: python -m pip install virtualenv"
            exit 1
        }
    }
} else {
    Write-Step "Step 1/5 — Virtual Environment (SKIPPED)"
    Write-Info "Skipping venv creation/activation as requested."
}

# ─── Step 2: Install Kimari ───────────────────────────────────────────────────

if (-not $SkipInstall) {
    Write-Step "Step 2/5 — Installing Kimari"

    Set-Location $KIMARI_ROOT

    Write-Info "Running: pip install -e ."
    try {
        & $pythonCmd -m pip install -e . 2>&1 | ForEach-Object {
            # Only show key lines to reduce noise
            if ($_ -match "(Successfully|ERROR|Requirement already satisfied|Installing collected)" -or
                $_ -match "(Building|Preparing|Running setup)") {
                Write-Host "         $_" -ForegroundColor Gray
            }
        }
        Write-Ok "Kimari package installed."
    } catch {
        Write-Fail "pip install failed: $_"
        Write-Detail "Try manually: $pythonCmd -m pip install -e ."
        exit 1
    }
} else {
    Write-Step "Step 2/5 — Installing Kimari (SKIPPED)"
    Write-Info "Skipping install as requested."
}

# ─── Step 3: Doctor ───────────────────────────────────────────────────────────

if (-not $SkipDoctor) {
    Write-Step "Step 3/5 — System Diagnostics"

    Write-Info "Running: kimari doctor"
    try {
        $doctorOutput = & $pythonCmd -m kimari.cli.main doctor 2>&1
        $doctorOutput | ForEach-Object { Write-Host "         $_" }
        Write-Ok "Diagnostics complete."
    } catch {
        Write-Warn "kimari doctor reported issues (non-fatal for launcher)."
        Write-Detail "You can run 'kimari doctor' manually for details."
    }
} else {
    Write-Step "Step 3/5 — System Diagnostics (SKIPPED)"
    Write-Info "Skipping doctor as requested."
}

# ─── Step 4: Pull Model ──────────────────────────────────────────────────────

if (-not $SkipPull) {
    Write-Step "Step 4/5 — Model Check"

    $modelsDir = Join-Path $KIMARI_ROOT "models"
    $ggufFiles = @()

    if (Test-Path $modelsDir) {
        $ggufFiles = Get-ChildItem -Path $modelsDir -Filter "*.gguf" -ErrorAction SilentlyContinue
    }

    if ($ggufFiles.Count -gt 0) {
        Write-Ok "Found $($ggufFiles.Count) GGUF model(s) in models/"
        foreach ($f in $ggufFiles) {
            $sizeMB = [math]::Round($f.Length / 1MB, 1)
            Write-Detail "$($f.Name) ($sizeMB MB)"
        }
    } else {
        Write-Info "No GGUF models found. Downloading test model..."
        Write-Info "Running: kimari pull test"
        try {
            & $pythonCmd -m kimari.cli.main pull test 2>&1 | ForEach-Object {
                Write-Host "         $_"
            }
            Write-Ok "Test model downloaded."
        } catch {
            Write-Fail "Failed to download test model: $_"
            Write-Detail "Try manually: kimari pull test"
            Write-Detail "Or place a GGUF model file in the models/ directory."
            exit 1
        }
    }
} else {
    Write-Step "Step 4/5 — Model Check (SKIPPED)"
    Write-Info "Skipping model pull as requested."
}

# ─── Step 5: Start Server ─────────────────────────────────────────────────────

Write-Step "Step 5/5 — Starting Kimari"

$startArgs = @("-m", "kimari.cli.main", "start")
if ($Profile) {
    $startArgs += @("--profile", $Profile)
}
if ($Daemon) {
    $startArgs += "--daemon"
}

$cmdDisplay = "$pythonCmd $($startArgs -join ' ')"
Write-Info "Running: $cmdDisplay"

try {
    & $pythonCmd @startArgs
} catch {
    Write-Fail "Server failed to start: $_"
    Write-Detail "Check the log file: kimari-server.log"
    Write-Detail "Run diagnostics: kimari doctor"
    Write-Detail "Try dry-run: kimari start --dry-run"
    exit 1
}

# ─── Summary ──────────────────────────────────────────────────────────────────

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "  Kimari Launcher Complete" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
