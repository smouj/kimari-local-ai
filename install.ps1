param(
    [switch]$Dev,
    [switch]$WithDashboard,
    [switch]$WithTestModel,
    [switch]$NoVenv,
    [switch]$Yes,
    [switch]$DryRun
)

$ErrorActionPreference = "Stop"
$RepoUrl = "https://github.com/smouj/kimari-local-ai.git"
$TargetDir = if ($env:KIMARI_INSTALL_DIR) { $env:KIMARI_INSTALL_DIR } else { Join-Path $HOME "kimari-local-ai" }

function Invoke-Step {
    param([string]$Label, [scriptblock]$Command)
    Write-Host $Label
    if (-not $DryRun) { & $Command }
}

if ($PSVersionTable.PSVersion.Major -lt 5) {
    throw "PowerShell 5+ is required."
}

$python = Get-Command python -ErrorAction SilentlyContinue
if (-not $python) { $python = Get-Command py -ErrorAction SilentlyContinue }
if (-not $python) { throw "Python 3.10+ is required." }
& $python.Source -c "import sys; raise SystemExit(0 if sys.version_info >= (3,10) else 1)"
if ($LASTEXITCODE -ne 0) { throw "Python >= 3.10 is required." }

$git = Get-Command git -ErrorAction SilentlyContinue
if (-not $git) { throw "Git is required. Install Git for Windows first." }

if ((Test-Path "pyproject.toml") -and (Test-Path "kimari")) {
    $RepoDir = (Get-Location).Path
    Write-Host "Using existing Kimari checkout: $RepoDir"
} else {
    $RepoDir = $TargetDir
    if (-not (Test-Path (Join-Path $RepoDir ".git"))) {
        Invoke-Step "Cloning Kimari..." { git clone $RepoUrl $RepoDir }
    } else {
        Write-Host "Using existing checkout: $RepoDir"
    }
    Set-Location $RepoDir
}

if (-not $NoVenv) {
    Invoke-Step "Creating virtual environment..." { & $python.Source -m venv .venv }
    if (-not $DryRun) { . .\.venv\Scripts\Activate.ps1 }
}

if ($Dev) {
    Invoke-Step "Installing Kimari (dev)..." { python -m pip install -e ".[dev]" }
} else {
    Invoke-Step "Installing Kimari..." { python -m pip install -e . }
}

Invoke-Step "Verifying version..." { python -m kimari --version }
Invoke-Step "Running quick doctor..." { python -m kimari doctor --quick }
Invoke-Step "Writing initial config..." { python -m kimari setup --write --yes }

if ($WithTestModel) {
    Invoke-Step "Downloading test model..." { python -m kimari pull test }
} else {
    Write-Host "Skipping model download (use -WithTestModel to download the small test model)."
}

if ($WithDashboard) {
    Invoke-Step "Setting up Gateway dashboard..." { python -m kimari gateway setup --yes }
} else {
    Write-Host "Skipping dashboard setup (use -WithDashboard to install dashboard dependencies)."
}

Write-Host ""
Write-Host "Kimari Local AI installed successfully!"
Write-Host ""
Write-Host "Next:"
Write-Host "  kimari console"
Write-Host "  kimari doctor --deep"
Write-Host "  kimari pull test"
Write-Host "  kimari start"
Write-Host "  kimari gateway start --open"
