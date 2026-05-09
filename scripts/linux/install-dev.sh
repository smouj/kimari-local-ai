#!/usr/bin/env bash
# install-dev.sh — Install Kimari Local AI development environment
# Usage: bash scripts/linux/install-dev.sh

set -euo pipefail

echo "╔══════════════════════════════════════════════╗"
echo "║  Kimari Local AI — Dev Environment Setup     ║"
echo "╚══════════════════════════════════════════════╝"
echo ""

# Check Python version
PYTHON=${PYTHON:-python3}
if ! command -v "$PYTHON" &>/dev/null; then
    echo "[ERROR] Python 3 not found. Install Python 3.10+ and try again."
    exit 1
fi

PY_VERSION=$($PYTHON -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
echo "[INFO] Python version: $PY_VERSION"

if [ "$(echo "$PY_VERSION < 3.10" | bc -l)" -eq 1 ]; then
    echo "[ERROR] Python 3.10+ required. Found: $PY_VERSION"
    exit 1
fi

# Install dev dependencies
echo ""
echo "[1/3] Installing Python dependencies..."
pip install -r requirements-dev.txt

# Install kimari in editable mode
echo ""
echo "[2/3] Installing kimari package (editable)..."
pip install -e ".[dev]"

# Check environment
echo ""
echo "[3/3] Checking environment..."
$PYTHON scripts/linux/check-env.py || true

echo ""
echo "✓ Development environment ready!"
echo ""
echo "Quick start:"
echo "  kimari doctor          # Check system"
echo "  kimari pull test       # Download test model"
echo "  kimari start --profile test --dry-run  # Preview start"
echo "  make test              # Run tests"
echo "  make ci-local          # Run full CI locally"
