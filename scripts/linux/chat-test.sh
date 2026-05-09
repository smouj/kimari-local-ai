#!/usr/bin/env bash
# =============================================================================
# Kimari — Chat Test
# =============================================================================
# Sends a test chat completion request to the Kimari server and displays
# the full JSON response.
#
# Usage:
#   bash chat-test.sh
#
# The test prompt asks the model to respond in Spanish about Kimari itself,
# exercising both language and domain knowledge.
# =============================================================================

HOST="127.0.0.1"
PORT="11435"
TIMEOUT=60

echo "Sending test message to Kimari..."
echo ""

RESPONSE=$(curl -sf --max-time "$TIMEOUT" \
    "http://$HOST:$PORT/v1/chat/completions" \
    -H "Content-Type: application/json" \
    -d '{
        "model": "kimari",
        "messages": [
            {"role": "system", "content": "Eres un asistente técnico útil. Responde de forma concisa."},
            {"role": "user", "content": "Responde en español: ¿Qué es Kimari y para qué sirve?"}
        ],
        "temperature": 0.7,
        "max_tokens": 256
    }' 2>/dev/null)

if [ -n "$RESPONSE" ]; then
    echo "$RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$RESPONSE"
    echo ""
    echo "---"
    CONTENT=$(echo "$RESPONSE" | python3 -c "import sys,json; print(json.load(sys.stdin)['choices'][0]['message']['content'])" 2>/dev/null || echo "(could not extract content)")
    echo "Response text:"
    echo "$CONTENT"
else
    echo "✗ No response received. Is Kimari running?"
    exit 1
fi
