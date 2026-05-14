#!/usr/bin/env bash
set -euo pipefail

REPO_URL="https://github.com/smouj/kimari-local-ai.git"
TARGET_DIR="${KIMARI_INSTALL_DIR:-$HOME/kimari-local-ai}"
DEV=0
WITH_DASHBOARD=0
WITH_TEST_MODEL=0
NO_VENV=0
YES=0
DRY_RUN=0

log() { printf '%s\n' "$*"; }
run() {
  if [[ "$DRY_RUN" == "1" ]]; then
    printf '[dry-run] %q' "$1"
    shift || true
    for arg in "$@"; do printf ' %q' "$arg"; done
    printf '\n'
  else
    "$@"
  fi
}
usage() {
  cat <<'EOF'
Kimari Local AI installer

Usage:
  install.sh [--dev] [--with-dashboard] [--with-test-model] [--no-venv] [--yes] [--dry-run]

Examples:
  curl -fsSL https://raw.githubusercontent.com/smouj/kimari-local-ai/main/install.sh | bash
  curl -fsSL https://raw.githubusercontent.com/smouj/kimari-local-ai/main/install.sh | bash -s -- --with-dashboard --with-test-model --yes
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --dev) DEV=1 ;;
    --with-dashboard) WITH_DASHBOARD=1 ;;
    --with-test-model) WITH_TEST_MODEL=1 ;;
    --no-venv) NO_VENV=1 ;;
    --yes) YES=1 ;;
    --dry-run) DRY_RUN=1 ;;
    -h|--help) usage; exit 0 ;;
    *) log "Unknown option: $1"; usage; exit 2 ;;
  esac
  shift
done

OS_NAME="$(uname -s 2>/dev/null || true)"
if [[ "$OS_NAME" != "Linux" ]]; then
  log "Kimari install.sh supports Linux/WSL2. Detected: ${OS_NAME:-unknown}"
  exit 1
fi
if grep -qi microsoft /proc/version 2>/dev/null; then
  log "Detected WSL2/Linux environment."
else
  log "Detected Linux environment."
fi

command -v python3 >/dev/null 2>&1 || { log "Python 3.10+ is required."; exit 1; }
python3 - <<'PY'
import sys
if sys.version_info < (3, 10):
    raise SystemExit("Python >= 3.10 is required")
print(f"Python {sys.version.split()[0]} OK")
PY
command -v git >/dev/null 2>&1 || { log "git is required. Install git first."; exit 1; }

if [[ -f "pyproject.toml" ]] && grep -q "kimari-local-ai" pyproject.toml && [[ -d "kimari" ]]; then
  REPO_DIR="$PWD"
  log "Using existing Kimari checkout: $REPO_DIR"
else
  REPO_DIR="$TARGET_DIR"
  if [[ ! -d "$REPO_DIR/.git" ]]; then
    run git clone "$REPO_URL" "$REPO_DIR"
  else
    log "Using existing checkout: $REPO_DIR"
  fi
  cd "$REPO_DIR"
fi

if [[ "$NO_VENV" != "1" ]]; then
  run python3 -m venv .venv
  # shellcheck disable=SC1091
  if [[ "$DRY_RUN" != "1" ]]; then source .venv/bin/activate; fi
fi

if [[ "$DEV" == "1" ]]; then
  run python3 -m pip install -e '.[dev]'
else
  run python3 -m pip install -e .
fi

run python3 -m kimari --version
run python3 -m kimari doctor --quick || true
run python3 -m kimari setup --write --yes

if [[ "$WITH_TEST_MODEL" == "1" ]]; then
  run python3 -m kimari pull test
else
  log "Skipping model download (use --with-test-model to download the small test model)."
fi

if [[ "$WITH_DASHBOARD" == "1" ]]; then
  run python3 -m kimari gateway setup --yes
else
  log "Skipping dashboard setup (use --with-dashboard to install dashboard dependencies)."
fi

cat <<'EOF'

Kimari Local AI installed successfully!

Next:
  kimari console
  kimari doctor --deep
  kimari pull test
  kimari start
  kimari gateway start --open
EOF
