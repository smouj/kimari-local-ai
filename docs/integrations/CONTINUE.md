# Continue.dev Integration

## Overview
Continue is an open-source AI code assistant for VS Code and JetBrains. Kimari provides a local OpenAI-compatible backend for Continue's chat and edit features.

## Configuration

Add Kimari as a model provider in your Continue configuration (`~/.continue/config.yaml` or VS Code settings):

```yaml
models:
  - title: Kimari Local
    provider: openai
    apiBase: http://127.0.0.1:11435/v1
    apiKey: kimari-local
    model: kimari
    roles:
      - chat
      - edit
```

## Start Kimari for Continue

```bash
kimari start --profile ide-local
```

Or use the test profile during alpha:

```bash
kimari start --profile test
```

## Important Notes

- **Chat and Edit roles**: Kimari works well for chat and edit. Autocomplete may be slow on consumer GPUs unless using a small model.
- **Temperature**: For coding assistance, lower temperature (0.2–0.4) is recommended. Configure this in Continue's model settings.
- **Context window**: Consumer GPUs have limited context. Keep conversations focused for best results.
- **API key**: The `apiKey` is a dummy value. Kimari does not enforce authentication by default.

## Verification

```bash
# Check Kimari is running
curl http://127.0.0.1:11435/v1/models

# Test a completion
curl http://127.0.0.1:11435/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model":"kimari","messages":[{"role":"user","content":"Write a Python hello world"}]}'
```

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Connection refused | Run `kimari start` first |
| Slow autocomplete | Disable autocomplete role; keep only chat and edit |
| Context too short | Use `kimari optimize --profile ide-local` for tuning |
| Model not found | Run `kimari pull test` then `kimari start` |
