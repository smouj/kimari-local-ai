# Hermes Agent Integration

## Overview
Hermes Agent supports Ollama, vLLM, and any OpenAI-compatible server, including llama.cpp server. Kimari fits as a local Chat Completions backend.

## Configuration

Point Hermes to Kimari's OpenAI-compatible endpoint:

- **Endpoint**: `http://127.0.0.1:11435/v1`
- **API key**: `kimari-local` (dummy, no auth enforced)
- **API type**: OpenAI Chat Completions
- **Timeout**: Set high (300+ seconds) — local inference is slower than cloud

## Start Kimari for Hermes

```bash
kimari start --profile hermes-local
```

Or use the test profile during alpha:

```bash
kimari start --profile test
```

## Important Notes

- Kimari uses **Chat Completions** (`/v1/chat/completions`). Configure Hermes to use OpenAI-compatible server mode.
- Quantized models will have lower quality than full-precision cloud models. Adjust expectations accordingly.
- Local inference latency depends on GPU capability. Use `kimari optimize` to find the best settings for your hardware.

## Verification

```bash
curl http://127.0.0.1:11435/v1/models
```

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Connection refused | `kimari start` first |
| Timeout | Increase timeout or use `kimari optimize` for faster settings |
| Quality issues | Use less aggressive quantization if VRAM allows |
