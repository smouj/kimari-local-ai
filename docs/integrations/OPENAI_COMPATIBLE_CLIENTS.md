# OpenAI-Compatible Clients

Kimari exposes an OpenAI-compatible API endpoint suitable for local clients.

## Connection values

- Base URL: `http://127.0.0.1:11435/v1`
- API key: any local dummy key (for example `kimari-local`)
- Recommended endpoint: `/v1/chat/completions`

## Minimal curl check

\`\`\`bash
curl -s http://127.0.0.1:11435/v1/models
\`\`\`

## Example chat request

\`\`\`bash
curl -s http://127.0.0.1:11435/v1/chat/completions \\\
  -H "Content-Type: application/json" \\\
  -d '{
    "model": "tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf",
    "messages": [{"role":"user","content":"Hola"}]
  }'
\`\`\`

## Related docs

- `docs/CLI_REFERENCE.md`
- `docs/OPENWEBUI_OPENCLAW_QUICK_CONFIG.md`
