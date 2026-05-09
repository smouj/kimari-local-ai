#!/usr/bin/env bash
set -euo pipefail

# =============================================================================
# Kimari — Smoke Tests
# =============================================================================
# Runs a comprehensive set of smoke tests against the Kimari server.
# Tests health endpoint and basic chat completion functionality.
#
# Usage:
#   bash smoke-test.sh
#
# Exit codes:
#   0 — All tests passed
#   1 — One or more tests failed
# =============================================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HOST="127.0.0.1"
PORT="11435"
PASS=0
FAIL=0
TOTAL=2

# Color helpers
green() { echo -e "\033[1;32m$*\033[0m"; }
red()   { echo -e "\033[1;31m$*\033[0m"; }
bold()  { echo -e "\033[1m$*\033[0m"; }

echo "========================================"
bold "  Kimari Smoke Tests"
echo "  Target: $HOST:$PORT"
echo "========================================"
echo ""

# --- Test 1: Healthcheck -----------------------------------------------
echo -n "[1/$TOTAL] Healthcheck... "
if curl -sf --max-time 5 "http://$HOST:$PORT/health" > /dev/null 2>&1; then
    green "PASS"
    PASS=$((PASS + 1))
else
    red "FAIL"
    echo "         Server is not responding on port $PORT"
    FAIL=$((FAIL + 1))
fi

# --- Test 2: Chat Completion -------------------------------------------
echo -n "[2/$TOTAL] Chat completion... "
RESPONSE=$(curl -sf --max-time 60 "http://$HOST:$PORT/v1/chat/completions" \
    -H "Content-Type: application/json" \
    -d '{"model":"kimari","messages":[{"role":"user","content":"Say OK"}],"max_tokens":16}' 2>/dev/null) || true

if [ -n "$RESPONSE" ] && echo "$RESPONSE" | grep -q '"content"'; then
    green "PASS"
    PASS=$((PASS + 1))
else
    red "FAIL"
    echo "         No valid chat response received"
    FAIL=$((FAIL + 1))
fi

# --- Summary -----------------------------------------------------------
echo ""
echo "========================================"
if [ "$FAIL" -eq 0 ]; then
    green "  All $TOTAL tests passed!"
else
    red "  Results: $PASS passed, $FAIL failed"
fi
echo "========================================"

[ "$FAIL" -eq 0 ] || exit 1
