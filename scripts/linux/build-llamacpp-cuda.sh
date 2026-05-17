#!/usr/bin/env bash
set -euo pipefail

# =============================================================================
# Kimari — Build llama.cpp with CUDA Support
# =============================================================================
# Builds llama.cpp from source with CUDA acceleration enabled.
# Copies the resulting llama-server binary to the Kimari project root.
#
# Requirements:
#   - CMake >= 3.14
#   - GCC >= 9 (or Clang >= 10)
#   - CUDA Toolkit >= 11.8 (11.0 best-effort)
#   - Git
# =============================================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$(dirname "$SCRIPT_DIR")")"
LLAMACPP_DIR="$PROJECT_ROOT/deps/llama.cpp"
BUILD_DIR="$LLAMACPP_DIR/build"
INSTALL_DIR="$PROJECT_ROOT/bin"

# Pin llama.cpp to a specific release for reproducibility.
# Override with: KIMARI_LLAMA_CPP_REF=master bash scripts/linux/build-llamacpp-cuda.sh
DEFAULT_LLAMA_CPP_REF="b4683"
KIMARI_LLAMA_CPP_REF="${KIMARI_LLAMA_CPP_REF:-$DEFAULT_LLAMA_CPP_REF}"

# Override CUDA architecture for specific GPU generations.
# Examples:
#   KIMARI_CUDA_ARCH=61  — Pascal (GTX 1060, GTX 1080)
#   KIMARI_CUDA_ARCH=75  — Turing (RTX 2060, RTX 2070)
#   KIMARI_CUDA_ARCH=86  — Ampere (RTX 3060, RTX 3070)
# If not set, CMake defaults are used (usually all supported architectures).
KIMARI_CUDA_ARCH="${KIMARI_CUDA_ARCH:-}"

# ---------------------------------------------------------------------------
# Color helpers
# ---------------------------------------------------------------------------
info()  { echo -e "\033[1;34m[INFO]\033[0m  $*"; }
ok()    { echo -e "\033[1;32m[OK]\033[0m    $*"; }
warn()  { echo -e "\033[1;33m[WARN]\033[0m  $*"; }
error() { echo -e "\033[1;31m[ERROR]\033[0m $*" >&2; }

# ---------------------------------------------------------------------------
# 1. Check prerequisites
# ---------------------------------------------------------------------------
info "Checking prerequisites..."

check_cmd() {
    if command -v "$1" >/dev/null 2>&1; then
        ok "$1 found: $(command -v "$1")"
    else
        error "$1 not found. Please install $2."
        exit 1
    fi
}

check_cmd cmake    "cmake >= 3.14  (sudo apt install cmake)"
check_cmd gcc      "gcc >= 9      (sudo apt install gcc g++)"
check_cmd git      "git            (sudo apt install git)"

if command -v nvcc >/dev/null 2>&1; then
    CUDA_VERSION=$(nvcc --version 2>/dev/null | grep "release" | sed -n 's/.*release \([0-9.]*\).*/\1/p')
    ok "CUDA found: $CUDA_VERSION"
else
    error "nvcc not found. Please install the CUDA Toolkit (>= 11.8)."
    echo "  https://developer.nvidia.com/cuda-downloads" >&2
    exit 1
fi

# ---------------------------------------------------------------------------
# 2. Clone llama.cpp if not present
# ---------------------------------------------------------------------------
if [ -d "$LLAMACPP_DIR/.git" ]; then
    info "llama.cpp already cloned at $LLAMACPP_DIR"
    cd "$LLAMACPP_DIR"
    info "Checking out ref: $KIMARI_LLAMA_CPP_REF"
    git fetch origin && git checkout "$KIMARI_LLAMA_CPP_REF" || warn "Could not checkout ref (offline?). Using existing source."
else
    info "Cloning llama.cpp into $LLAMACPP_DIR ..."
    git clone --branch "$KIMARI_LLAMA_CPP_REF" https://github.com/ggerganov/llama.cpp.git "$LLAMACPP_DIR"
    cd "$LLAMACPP_DIR"
fi

info "Using llama.cpp ref: $KIMARI_LLAMA_CPP_REF ($(git rev-parse --short HEAD))"

# ---------------------------------------------------------------------------
# 3. Build with CUDA
# ---------------------------------------------------------------------------
info "Configuring build with CUDA support..."
mkdir -p "$BUILD_DIR"
cd "$BUILD_DIR"

CMAKE_ARGS=(
    -DGGML_CUDA=ON
    -DGGML_CUDA_F16=ON
    -DCMAKE_BUILD_TYPE=Release
    -DCMAKE_INSTALL_PREFIX="$INSTALL_DIR"
)

if [ -n "$KIMARI_CUDA_ARCH" ]; then
    info "CUDA architecture override: sm_${KIMARI_CUDA_ARCH} (KIMARI_CUDA_ARCH=$KIMARI_CUDA_ARCH)"
    CMAKE_ARGS+=("-DCMAKE_CUDA_ARCHITECTURES=${KIMARI_CUDA_ARCH}")
fi

cmake .. "${CMAKE_ARGS[@]}"

info "Compiling llama.cpp (this may take 10-30 minutes)..."
NPROC=$(nproc 2>/dev/null || echo 4)
cmake --build . --config Release -j"$NPROC"

# ---------------------------------------------------------------------------
# 4. Copy binaries
# ---------------------------------------------------------------------------
mkdir -p "$INSTALL_DIR"
cp -v "$BUILD_DIR/bin/llama-server" "$PROJECT_ROOT/llama-server" 2>/dev/null || \
    cp -v "$BUILD_DIR/llama-server"   "$PROJECT_ROOT/llama-server" 2>/dev/null || {
        error "llama-server binary not found after build."
        error "Looked in: $BUILD_DIR/bin/llama-server, $BUILD_DIR/llama-server"
        exit 1
    }

ok "llama-server copied to $PROJECT_ROOT/llama-server"

# ---------------------------------------------------------------------------
# 5. Validate build
# ---------------------------------------------------------------------------
if [ -x "$PROJECT_ROOT/llama-server" ]; then
    ok "llama-server is executable"
    # Try --version (some builds support it)
    if "$PROJECT_ROOT/llama-server" --version >/dev/null 2>&1; then
        LLAMA_VERSION=$("$PROJECT_ROOT/llama-server" --version 2>&1 | head -1)
        ok "llama-server version: $LLAMA_VERSION"
    else
        info "llama-server built successfully (version flag not available)"
    fi
else
    error "llama-server is not executable after build"
    exit 1
fi

# ---------------------------------------------------------------------------
# 6. Summary
# ---------------------------------------------------------------------------
echo ""
echo "============================================="
ok  "Build completed successfully!"
echo "============================================="
echo "  Binary:    $PROJECT_ROOT/llama-server"
if [ -n "$KIMARI_CUDA_ARCH" ]; then
    echo "  CUDA:      enabled (sm_${KIMARI_CUDA_ARCH}, compute capability ${KIMARI_CUDA_ARCH})"
else
    echo "  CUDA:      enabled (sm_${CUDA_VERSION:-unknown}, default architectures)"
fi
echo "  Install:   $INSTALL_DIR"
echo ""
echo "Next step:"
echo "  bash scripts/linux/start-kimari.sh gtx1080"
echo "============================================="
