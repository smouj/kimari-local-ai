# OpenClaw Integration

Kimari can be used as an OpenAI-compatible backend for OpenClaw.

## Endpoint

- Base URL: `http://127.0.0.1:11435/v1`
- API style: Chat Completions (`/v1/chat/completions`)
- API key: use a local dummy value (for example `kimari-local`)

## Start Kimari

\`\`\`bash
kimari start --profile openclaw-local
\`\`\`

## OpenClaw config

Use the example config at:

- `config/integrations/openclaw.kimari.example.json`

## Verify

\`\`\`bash
curl -s http://127.0.0.1:11435/health
curl -s http://127.0.0.1:11435/v1/models
\`\`\`

For full quick setup across tools, see:

- `docs/OPENWEBUI_OPENCLAW_QUICK_CONFIG.md`
