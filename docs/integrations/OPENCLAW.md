# OpenClaw Integration

## Overview
OpenClaw supports local OpenAI-compatible providers via `baseUrl`, `apiKey`, and `api` configuration. Kimari works as a Chat Completions backend.

## Recommended Configuration

Create or update your OpenClaw configuration:

```json
{
  "baseUrl": "http://127.0.0.1:11435/v1",
  "apiKey": "kimari-local",
  "api": "openai-completions",
  "timeoutSeconds": 300
}
```

## Start Kimari for OpenClaw

```bash
kimari start --profile openclaw-local
```

Or use the test profile during alpha:

```bash
kimari start --profile test
```

## Important Notes

- **Use Chat Completions**: Kimari exposes the `/v1/chat/completions` endpoint. Do NOT configure OpenClaw to use the Responses API — it is not yet supported by Kimari's llama-server backend.
- **Use 127.0.0.1**: Never expose Kimari on 0.0.0.0 unless you are using Docker and understand the security implications.
- **Timeout**: Local inference is slower than cloud APIs. Set `timeoutSeconds` to at least 300 (5 minutes).
- **Model size**: Smaller or heavily quantized models may degrade context quality and security against prompt injection. This is a known limitation of local models, not specific to Kimari.
- **API key**: The `apiKey` field is a dummy value. Kimari does not enforce authentication by default. If you need auth, consider an nginx reverse proxy.

## Verification

```bash
# Check server is running
curl http://127.0.0.1:11435/v1/models

# Test a completion
curl http://127.0.0.1:11435/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model":"kimari","messages":[{"role":"user","content":"Hello"}]}'
```

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Connection refused | Run `kimari start` first |
| Timeout | Increase `timeoutSeconds` or reduce context size |
| Model not found | Run `kimari pull test` then `kimari start` |
| Slow responses | Try `kimari optimize --profile openclaw-local` for tuning advice |
