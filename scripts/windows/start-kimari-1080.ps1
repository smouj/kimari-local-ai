# =============================================================================
# Kimari — Start with GTX 1080 Profile (Windows PowerShell)
# =============================================================================

$ErrorActionPreference = "Stop"
$KIMARI_ROOT = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$CONFIG_FILE = Join-Path $KIMARI_ROOT "config\kimari.profiles.json"
$PROFILE = "gtx1080"

Write-Host "=== Kimari — Starting with profile: $PROFILE ===" -ForegroundColor Cyan

# --- Read config ---
if (-not (Test-Path $CONFIG_FILE)) {
    Write-Host "[ERROR] Config not found: $CONFIG_FILE" -ForegroundColor Red
    exit 1
}

$config = Get-Content $CONFIG_FILE | ConvertFrom-Json
$profileData = $config.profiles.$PROFILE

$MODEL_PATH = Join-Path $KIMARI_ROOT $profileData.model
$CTX = $profileData.ctx
$BATCH = $profileData.batch
$UBATCH = $profileData.ubatch
$CACHE_K = $profileData.cache_type_k
$CACHE_V = $profileData.cache_type_v
$HOST = $profileData.host
$PORT = $profileData.port
$GPU_LAYERS = $profileData.gpu_layers
$THREADS = $profileData.threads

Write-Host "[INFO] Model:   $MODEL_PATH"
Write-Host "[INFO] Context: $CTX tokens"
Write-Host "[INFO] Host:    ${HOST}:${PORT}"
Write-Host ""

# --- Validate model ---
if (-not (Test-Path $MODEL_PATH)) {
    Write-Host "[ERROR] Model not found: $MODEL_PATH" -ForegroundColor Red
    Write-Host "[INFO] Place your GGUF model in the models\ directory" -ForegroundColor Yellow
    exit 1
}

# --- Find llama-server ---
$llamaServer = $null
if (Get-Command llama-server -ErrorAction SilentlyContinue) {
    $llamaServer = "llama-server"
} elseif (Test-Path (Join-Path $KIMARI_ROOT "server\bin\llama-server.exe")) {
    $llamaServer = Join-Path $KIMARI_ROOT "server\bin\llama-server.exe"
}

if (-not $llamaServer) {
    Write-Host "[ERROR] llama-server not found in PATH or server\bin\" -ForegroundColor Red
    Write-Host "[INFO] Download pre-built binaries or compile with CMake + CUDA" -ForegroundColor Yellow
    exit 1
}

# --- Start server ---
Write-Host "[INFO] Starting llama-server ..." -ForegroundColor Green

$env:CUDA_VISIBLE_DEVICES = "0"

& $llamaServer `
    -m $MODEL_PATH `
    -c $CTX `
    -b $BATCH `
    -ub $UBATCH `
    --flash-attn `
    -ngl $GPU_LAYERS `
    -t $THREADS `
    --cache-type-k $CACHE_K `
    --cache-type-v $CACHE_V `
    --host $HOST `
    --port $PORT
