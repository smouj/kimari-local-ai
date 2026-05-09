# Kimari Models

This directory is where you place your GGUF model files.

## Important

**Model weights are NOT versioned in this repository.** They are excluded via `.gitignore`.

## How to Obtain Models

### Official Kimari Models (when available)

Download from the [Kimari releases](https://github.com/kimari-ai/kimari-local-ai/releases) page.

### Provisional Test Models

Before the official Kimari model is ready, you can use any compatible GGUF model:

- **Qwen3-4B** — Excellent multilingual support
- **SmolLM3-3B** — Lightweight and fast
- **Llama-3.2-3B** — Strong general performance
- **Phi-3.5-mini** — Good reasoning capabilities

## Naming Convention

Place models here with this naming pattern:

```
models/
├── Kimari-4B-Q4_K_M.gguf        # GTX 1060 profile
├── Kimari-4B-Q5_K_M.gguf        # GTX 1080 profile
├── Kimari-4B-IQ4_XS.gguf        # Turbo profile
└── README.md                     # This file
```

When using provisional models, rename them to match the profile configuration in `config/kimari.profiles.json`.

## Download Example

```bash
# Example: Download Qwen3-4B GGUF from Hugging Face
wget https://huggingface.co/Qwen/Qwen3-4B-GGUF/resolve/main/qwen3-4b-q4_k_m.gguf \
  -O models/Kimari-4B-Q4_K_M.gguf
```

## File Sizes

Typical sizes for 4B parameter models:

| Quantization | Size | Profile |
|-------------|------|---------|
| Q4_K_M | ~3.1 GiB | gtx1060 |
| Q5_K_M | ~3.8 GiB | gtx1080 |
| IQ4_XS | ~2.8 GiB | turbo |
| Q8_0 | ~5.0 GiB | (custom) |
| F16 | ~7.5 GiB | (custom) |
