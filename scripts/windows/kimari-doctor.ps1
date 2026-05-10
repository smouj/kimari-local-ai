<#
.SYNOPSIS
    Diagnostic script for Kimari Local AI on Windows.
.DESCRIPTION
    Performs comprehensive system checks to verify that Kimari can run:
      1. Python installation (3.10+)
      2. CUDA availability (nvidia-smi)
      3. llama-server binary availability
      4. GGUF model files in models/
      5. Port 11435 availability

    Provides detailed troubleshooting advice for each failing check.
    Returns exit code 0 if all checks pass, 1 if any problems are found.
.PARAMETER Port
    Port number to check (default: 11435).
.PARAMETER Json
    Output results as JSON for programmatic consumption.
.EXAMPLE
    .\kimari-doctor.ps1
    Run all diagnostic checks with human-readable output.
.EXAMPLE
    .\kimari-doctor.ps1 -Json
    Output diagnostic results as JSON.
.EXAMPLE
    .\kimari-doctor.ps1 -Port 8080
    Check a custom port instead of the default 11435.
.NOTES
    Requires PowerShell 5.1+.
    If you get an execution policy error, run:
      Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
#>

[CmdletBinding()]
param(
    [int]$Port = 11435,
    [switch]$Json
)

$ErrorActionPreference = "Stop"

# ─── Helper Functions ──────────────────────────────────────────────────────────

function Write-CheckOk {
    param([string]$Label, [string]$Message)
    Write-Host ("  {0,-20} " -f $Label) -NoNewline
    Write-Host "[OK]   " -ForegroundColor Green -NoNewline
    Write-Host $Message
}

function Write-CheckWarn {
    param([string]$Label, [string]$Message)
    Write-Host ("  {0,-20} " -f $Label) -NoNewline
    Write-Host "[WARN] " -ForegroundColor Yellow -NoNewline
    Write-Host $Message
}

function Write-CheckFail {
    param([string]$Label, [string]$Message)
    Write-Host ("  {0,-20} " -f $Label) -NoNewline
    Write-Host "[FAIL] " -ForegroundColor Red -NoNewline
    Write-Host $Message
}

function Write-Advice {
    param([string[]]$Lines)
    foreach ($line in $Lines) {
        Write-Host "         $line" -ForegroundColor Yellow
    }
}

# ─── Project Root ──────────────────────────────────────────────────────────────

$KIMARI_ROOT = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)

# ─── Results Tracking ──────────────────────────────────────────────────────────

$results = @{
    python     = @{ status = "unknown"; detail = "" }
    cuda       = @{ status = "unknown"; detail = "" }
    llama      = @{ status = "unknown"; detail = "" }
    model      = @{ status = "unknown"; detail = "" }
    port       = @{ status = "unknown"; detail = "" }
    problems   = 0
}

# ─── Header ────────────────────────────────────────────────────────────────────

if (-not $Json) {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Magenta
    Write-Host "  Kimari Local AI - Diagnostics" -ForegroundColor Magenta
    Write-Host "========================================" -ForegroundColor Magenta
    Write-Host "  Project: $KIMARI_ROOT" -ForegroundColor Gray
    Write-Host ""
}

# ─── Check 1: Python Installation ─────────────────────────────────────────────

$pythonCmd = $null
$pythonVersion = ""

foreach ($cmd in @("python", "python3", "py")) {
    try {
        $ver = & $cmd --version 2>&1
        $verStr = $ver.ToString().Trim()
        if ($verStr -match "(\d+)\.(\d+)\.(\d+)") {
            $major = [int]$Matches[1]
            $minor = [int]$Matches[2]
            $pythonVersion = $verStr
            if ($major -gt 3 -or ($major -eq 3 -and $minor -ge 10)) {
                $pythonCmd = $cmd
            }
            break
        }
    } catch {
        # Command not found, try next
    }
}

if ($pythonCmd) {
    $results.python.status = "ok"
    $results.python.detail = "$pythonVersion ($pythonCmd)"
    if (-not $Json) {
        Write-CheckOk "Python" "$pythonVersion ($pythonCmd)"
    }
} elseif ($pythonVersion) {
    $results.python.status = "fail"
    $results.python.detail = "Found $pythonVersion but need 3.10+"
    $results.problems++
    if (-not $Json) {
        Write-CheckFail "Python" "Found $pythonVersion but need 3.10+"
        Write-Advice @(
            "Install Python 3.10 or later from: https://www.python.org/downloads/",
            "During installation, check 'Add Python to PATH'.",
            "After installing, restart your terminal and re-run this script."
        )
    }
} else {
    $results.python.status = "fail"
    $results.python.detail = "Not found"
    $results.problems++
    if (-not $Json) {
        Write-CheckFail "Python" "Not found"
        Write-Advice @(
            "Python is not installed or not on PATH.",
            "Download from: https://www.python.org/downloads/",
            "During installation, check 'Add Python to PATH'.",
            "After installing, restart your terminal and re-run this script."
        )
    }
}

# ─── Check 2: CUDA Availability ───────────────────────────────────────────────

$cudaFound = $false
$cudaDetail = ""

if (Get-Command "nvidia-smi" -ErrorAction SilentlyContinue) {
    try {
        $nvidiaOut = & nvidia-smi --query-gpu=name,driver_version,memory.total --format=csv,noheader 2>&1
        if ($LASTEXITCODE -eq 0 -or $nvidiaOut -match "^\s*") {
            $cudaFound = $true
            # Parse GPU info
            $gpuLines = $nvidiaOut -split "`n" | Where-Object { $_.Trim() -ne "" }
            if ($gpuLines.Count -gt 0) {
                $firstLine = $gpuLines[0].Trim()
                $cudaDetail = "GPU: $firstLine"
            } else {
                $cudaDetail = "nvidia-smi available"
            }

            # Try to get CUDA version
            try {
                $cudaVerOut = & nvidia-smi --query-gpu=compute_cap --format=csv,noheader 2>&1
                if ($cudaVerOut -and $cudaVerOut.Trim() -ne "") {
                    $cudaDetail += " (Compute: $($cudaVerOut.Trim()))"
                }
            } catch {
                # Non-critical, skip
            }
        }
    } catch {
        # nvidia-smi exists but failed
    }
}

# Also check nvcc as an alternative indicator
if (-not $cudaFound -and (Get-Command "nvcc" -ErrorAction SilentlyContinue)) {
    try {
        $nvccOut = & nvcc --version 2>&1
        $cudaFound = $true
        $cudaDetail = "CUDA toolkit found (nvcc available)"
        if ($nvccOut -match "release (\S+)") {
            $cudaDetail += " (CUDA $($Matches[1]))"
        }
    } catch {
        # Skip
    }
}

if ($cudaFound) {
    $results.cuda.status = "ok"
    $results.cuda.detail = $cudaDetail
    if (-not $Json) {
        Write-CheckOk "CUDA" $cudaDetail
    }
} else {
    $results.cuda.status = "warn"
    $results.cuda.detail = "Not detected"
    $results.problems++
    if (-not $Json) {
        Write-CheckWarn "CUDA" "Not detected"
        Write-Advice @(
            "No NVIDIA GPU or CUDA toolkit detected.",
            "Install CUDA Toolkit from: https://developer.nvidia.com/cuda-downloads",
            "Select: Windows > x86_64 > your version > exe (local)",
            "After installing, restart your terminal.",
            "",
            "If you have an AMD GPU, see: scripts/linux/build-llamacpp-rocm.sh",
            "If you have no GPU, Kimari can still run in CPU-only mode (slower)."
        )
    }
}

# ─── Check 3: llama-server Availability ───────────────────────────────────────

$llamaServerPath = $null
$llamaDetail = ""

# Check environment variables first
$envPaths = @($env:LLAMA_SERVER, $env:KIMARI_LLAMA_SERVER)
foreach ($ep in $envPaths) {
    if ($ep -and (Test-Path $ep)) {
        $llamaServerPath = $ep
        $llamaDetail = "Found via env var: $ep"
        break
    }
}

# Check PATH
if (-not $llamaServerPath) {
    foreach ($cmd in @("llama-server", "llama_server")) {
        $found = Get-Command $cmd -ErrorAction SilentlyContinue
        if ($found) {
            $llamaServerPath = $found.Source
            $llamaDetail = "Found in PATH: $($found.Source)"
            break
        }
    }
}

# Check project-local locations
if (-not $llamaServerPath) {
    $localPaths = @(
        (Join-Path $KIMARI_ROOT "llama-server.exe"),
        (Join-Path $KIMARI_ROOT "llama-server"),
        (Join-Path $KIMARI_ROOT "bin\llama-server.exe"),
        (Join-Path $KIMARI_ROOT "bin\llama-server"),
        (Join-Path $KIMARI_ROOT "deps\llama.cpp\build\bin\llama-server.exe"),
        (Join-Path $KIMARI_ROOT "deps\llama.cpp\build\bin\Release\llama-server.exe")
    )
    foreach ($lp in $localPaths) {
        if (Test-Path $lp) {
            $llamaServerPath = $lp
            $llamaDetail = "Found locally: $lp"
            break
        }
    }
}

if ($llamaServerPath) {
    # Try to get version
    $versionStr = ""
    try {
        $verOut = & $llamaServerPath --version 2>&1
        if ($verOut -match "version\s+(\S+)") {
            $versionStr = " (v$($Matches[1]))"
        }
    } catch {
        # Non-critical
    }

    $results.llama.status = "ok"
    $results.llama.detail = "$llamaDetail$versionStr"
    if (-not $Json) {
        Write-CheckOk "llama-server" "$llamaDetail$versionStr"
    }
} else {
    $results.llama.status = "fail"
    $results.llama.detail = "Not found"
    $results.problems++
    if (-not $Json) {
        Write-CheckFail "llama-server" "Not found"
        Write-Advice @(
            "llama-server is required to run Kimari but was not found.",
            "",
            "Searched in order:",
            "  1. %LLAMA_SERVER% environment variable",
            "  2. %KIMARI_LLAMA_SERVER% environment variable",
            "  3. llama-server in PATH",
            "  4. llama-server.exe in project root",
            "  5. bin\llama-server.exe",
            "  6. deps\llama.cpp\build\bin\llama-server.exe",
            "",
            "How to get llama-server:",
            "  Option A: Build from source",
            "    git clone https://github.com/ggerganov/llama.cpp",
            "    cd llama.cpp && cmake -B build -DGGML_CUDA=ON && cmake --build build --config Release",
            "    Copy build\bin\Release\llama-server.exe to the Kimari project root.",
            "",
            "  Option B: Set the LLAMA_SERVER environment variable",
            "    `$env:LLAMA_SERVER = 'C:\path\to\llama-server.exe'",
            "    Or set it permanently in System Properties > Environment Variables.",
            "",
            "  Option C: Use a pre-built binary from llama.cpp releases",
            "    https://github.com/ggerganov/llama.cpp/releases"
        )
    }
}

# ─── Check 4: GGUF Models ─────────────────────────────────────────────────────

$modelsDir = Join-Path $KIMARI_ROOT "models"
$ggufFiles = @()

if (Test-Path $modelsDir) {
    $ggufFiles = @(Get-ChildItem -Path $modelsDir -Filter "*.gguf" -ErrorAction SilentlyContinue)
}

if ($ggufFiles.Count -gt 0) {
    $modelNames = ($ggufFiles | ForEach-Object {
        $sizeMB = [math]::Round($_.Length / 1MB, 1)
        "$($_.Name) ($sizeMB MB)"
    }) -join ", "

    $results.model.status = "ok"
    $results.model.detail = "$($ggufFiles.Count) model(s): $modelNames"
    if (-not $Json) {
        Write-CheckOk "Models" "$($ggufFiles.Count) GGUF model(s) found"
        foreach ($f in $ggufFiles) {
            $sizeMB = [math]::Round($f.Length / 1MB, 1)
            Write-Host "         $($f.Name) ($sizeMB MB)" -ForegroundColor Gray
        }
    }
} else {
    $results.model.status = "warn"
    $results.model.detail = "No GGUF models found"
    $results.problems++
    if (-not $Json) {
        Write-CheckWarn "Models" "No GGUF models found in models/"
        Write-Advice @(
            "No model files found in: $modelsDir",
            "",
            "Download a test model with:",
            "  kimari pull test",
            "",
            "Or manually place a .gguf file in the models/ directory.",
            "Recommended models for 6GB VRAM: Q4_K_M quantization, 1-4B parameters.",
            "",
            "Popular sources:",
            "  https://huggingface.co/models?search=gguf",
            "  https://huggingface.co/TheBloke"
        )
    }
}

# ─── Check 5: Port Availability ───────────────────────────────────────────────

$portInUse = $false
$portDetail = ""

try {
    $connections = Get-NetTCPConnection -LocalPort $Port -ErrorAction SilentlyContinue
    if ($connections) {
        $portInUse = $true
        # Find what's using it
        $procIds = $connections | Select-Object -ExpandProperty OwningProcess -Unique
        $procNames = @()
        foreach ($pid in $procIds) {
            try {
                $proc = Get-Process -Id $pid -ErrorAction SilentlyContinue
                if ($proc) {
                    $procNames += "$($proc.ProcessName) (PID: $pid)"
                }
            } catch {
                $procNames += "PID: $pid"
            }
        }
        $portDetail = "In use by: $($procNames -join ', ')"
    } else {
        $portDetail = "Port $Port is available"
    }
} catch {
    # Get-NetTCPConnection may not be available on older PowerShell
    # Fallback: try netstat
    try {
        $netstatOut = & netstat -ano 2>&1 | Select-String ":$Port\s"
        if ($netstatOut) {
            $portInUse = $true
            $portDetail = "Port $Port is in use (detected via netstat)"
        } else {
            $portDetail = "Port $Port is available"
        }
    } catch {
        $portDetail = "Could not check port status"
    }
}

if (-not $portInUse) {
    $results.port.status = "ok"
    $results.port.detail = $portDetail
    if (-not $Json) {
        Write-CheckOk "Port" $portDetail
    }
} else {
    $results.port.status = "warn"
    $results.port.detail = $portDetail
    $results.problems++
    if (-not $Json) {
        Write-CheckWarn "Port" $portDetail
        Write-Advice @(
            "Port $Port is already in use.",
            "",
            "Options:",
            "  1. Stop the existing server: kimari stop",
            "  2. Kill the process using the port:",
            "     Stop-Process -Id <PID> -Force",
            "  3. Use a different port by editing config/kimari.profiles.json",
            "     Change the 'port' value in your active profile.",
            "  4. Override at launch: kimari start --port <other-port>"
        )
    }
}

# ─── Bonus: Kimari CLI Check ──────────────────────────────────────────────────

if (-not $Json) {
    Write-Host ""
    Write-Host "--- Additional Info ---" -ForegroundColor DarkGray

    # Kimari version
    if (Get-Command "kimari" -ErrorAction SilentlyContinue) {
        try {
            $kimariVer = & kimari --version 2>&1
            Write-Host "  Kimari CLI: $kimariVer" -ForegroundColor Gray
        } catch {
            Write-Host "  Kimari CLI: installed (version unknown)" -ForegroundColor Gray
        }
    } elseif ($pythonCmd) {
        try {
            $kimariVer = & $pythonCmd -m kimari.cli.main --version 2>&1
            Write-Host "  Kimari CLI: $kimariVer (via $pythonCmd)" -ForegroundColor Gray
        } catch {
            Write-Host "  Kimari CLI: not installed" -ForegroundColor Gray
        }
    }

    # Config file
    $configFile = Join-Path $KIMARI_ROOT "config\kimari.profiles.json"
    if (Test-Path $configFile) {
        Write-Host "  Config: $configFile" -ForegroundColor Gray
    } else {
        Write-Host "  Config: NOT FOUND at $configFile" -ForegroundColor Red
    }

    # Models directory
    Write-Host "  Models dir: $modelsDir" -ForegroundColor Gray
}

# ─── Summary ──────────────────────────────────────────────────────────────────

$okCount = ($results.GetEnumerator() | Where-Object { $_.Value.status -eq "ok" }).Count
$warnCount = ($results.GetEnumerator() | Where-Object { $_.Value.status -eq "warn" }).Count
$failCount = ($results.GetEnumerator() | Where-Object { $_.Value.status -eq "fail" }).Count

if ($Json) {
    $jsonOutput = @{
        checks = @{
            python       = $results.python
            cuda         = $results.cuda
            llama_server = $results.llama
            model        = $results.model
            port         = $results.port
        }
        summary = @{
            ok   = $okCount
            warn = $warnCount
            fail = $failCount
        }
        project_root = $KIMARI_ROOT
        all_ok       = ($results.problems -eq 0)
    } | ConvertTo-Json -Depth 5
    Write-Output $jsonOutput
} else {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Magenta
    Write-Host "  Diagnostic Summary" -ForegroundColor Magenta
    Write-Host "========================================" -ForegroundColor Magenta
    Write-Host ""
    Write-Host "  OK:   $okCount" -ForegroundColor Green
    Write-Host "  WARN: $warnCount" -ForegroundColor Yellow
    Write-Host "  FAIL: $failCount" -ForegroundColor Red
    Write-Host ""

    if ($failCount -gt 0) {
        Write-Host "  Critical issues found. Fix FAIL items before starting Kimari." -ForegroundColor Red
        Write-Host ""
        exit 1
    } elseif ($warnCount -gt 0) {
        Write-Host "  Warnings present. Kimari may work with limitations." -ForegroundColor Yellow
        Write-Host "  Review the advice above for each warning." -ForegroundColor Yellow
        Write-Host ""
        exit 1
    } else {
        Write-Host "  All checks passed! Ready to start Kimari." -ForegroundColor Green
        Write-Host ""
        Write-Host "  Next steps:" -ForegroundColor Cyan
        Write-Host "    kimari start           # Start with default profile"
        Write-Host "    kimari start --profile gtx1060  # Start with specific profile"
        Write-Host ""
        exit 0
    }
}
