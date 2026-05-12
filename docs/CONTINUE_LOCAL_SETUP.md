# Continue.dev Local Setup

> **How to connect Continue.dev (VS Code extension) to Kimari Local AI's OpenAI-compatible endpoint.**

## ⚠️ Important

- Uses **TinyLlama 1.1B Q4_K_M** as the validation model — **NOT Kimari-4B**.
- No API key is required for localhost connections.
- TinyLlama is a small model — code completions will be limited in quality.

## Prerequisites

- Kimari Local AI installed and TinyLlama model downloaded
- Continue.dev extension installed in VS Code
- llama-server running on `127.0.0.1:11435`

## Step 1: Start Kimari

```bash
cd ~/.openclaw/workspace/kimari-local-ai
source .venv/bin/activate
kimari start --profile test
```

## Step 2: Configure Continue.dev

Open Continue.dev settings (`.continue/config.json` in your project or global config):

```json
{
  "models": [
    {
      "title": "Kimari Local (TinyLlama)",
      "provider": "openai",
      "model": "tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf",
      "apiBase": "http://127.0.0.1:11435/v1",
      "apiKey": "placeholder-no-key-required"
    }
  ],
  "tabAutocompleteModel": {
    "title": "Kimari Local (TinyLlama)",
    "provider": "openai",
    "model": "tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf",
    "apiBase": "http://127.0.0.1:11435/v1",
    "apiKey": "placeholder-no-key-required"
  }
}
```

> **Note:** `apiKey` is set to `placeholder-no-key-required` as a placeholder because Continue.dev requires a non-empty value. Kimari's local endpoint does not validate API keys.

## Step 3: Use in VS Code

1. Open the Continue.dev sidebar (⌘+L or Ctrl+L)
2. Select **Kimari Local (TinyLlama)** from the model dropdown
3. Ask questions or request code completions

## Limitations

- **TinyLlama 1.1B** is a small model: responses are short and quality is limited
- **No streaming** support in some configurations
- **Context window**: 4096 tokens (test profile)
- **Not Kimari-4B**: When Kimari-4B is released, update the model name

## Common Errors

| Error | Cause | Solution |
|-------|-------|----------|
| `Connection refused` | Kimari not started | Run `kimari start --profile test` |
| `401 Unauthorized` | API key issue | Use `placeholder-no-key-required` as placeholder |
| `Model not found` | Wrong model name | Check with `curl http://127.0.0.1:11435/v1/models` |
| Poor completions | TinyLlama limitations | Expected — Kimari-4B will improve this |

## No Claims

- Continue.dev connects to Kimari's local endpoint using TinyLlama.
- **Kimari-4B is not released.** When available, update the model in config.
- No API keys, tokens, or private data are committed.