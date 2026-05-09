# Kimari Models

This directory is where you place your GGUF model files.

## Important

**Model weights are NOT versioned in this repository.** They are excluded via `.gitignore`.

## How to Obtain Models

### Official Kimari Models (planned — not yet available)

Kimari-4B is the target model under development. Weights will be released on the
[Kimari GitHub releases](https://github.com/smouj/kimari-local-ai/releases) page
when ready. There is no ETA — see `MODEL_CARD.md` for details.

### Test Models (for runtime validation)

Before the official Kimari model is ready, you can use any compatible GGUF model
for testing. The `test` profile in `config/kimari.profiles.json` expects a model
at:

```
models/tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf
```

**Recommended test models (any will work):**

| Model | Params | Quant | Download |
|-------|--------|-------|----------|
| Llama 3.2 1B Instruct | 1B | Q4_K_M | [HuggingFace](https://huggingface.co/bartowski/Llama-3.2-1B-Instruct-GGUF) |
| SmolLM3 1.7B | 1.7B | Q4_K_M | [HuggingFace](https://huggingface.co/HuggingFaceTB/SmolLM3-1.7B-GGUF) |
| Qwen3-4B | 4B | Q4_K_M | [HuggingFace](https://huggingface.co/Qwen/Qwen3-4B-GGUF) |
| Llama 3.2 3B Instruct | 3B | Q4_K_M | [HuggingFace](https://huggingface.co/bartowski/Llama-3.2-3B-Instruct-GGUF) |
| Phi-3.5 Mini | 3.8B | Q4_K_M | [HuggingFace](https://huggingface.co/microsoft/Phi-3.5-mini-instruct-GGUF) |

### Quick Setup for Test Profile

```bash
# Create models directory
mkdir -p models

# Download Llama 3.2 1B (small, good for testing)
wget -O models/tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf \
  "https://huggingface.co/bartowski/Llama-3.2-1B-Instruct-GGUF/resolve/main/Llama-3.2-1B-Instruct-Q4_K_M.gguf"

# Start with test profile
python3 cli/kimari_cli.py start --profile test
```

> **Any compatible GGUF file works.** Just rename it to `tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf`,
> or create a custom profile in `config/kimari.profiles.json` pointing to your file.

## Profile Naming Convention

The profiles in `config/kimari.profiles.json` reference specific model filenames:

| Profile | Expected Model File |
|---------|-------------------|
| `gtx1060` | `models/Kimari-4B-Q4_K_M.gguf` |
| `gtx1080` | `models/Kimari-4B-Q5_K_M.gguf` |
| `turbo` | `models/Kimari-4B-IQ4_XS.gguf` |
| `test` | `models/tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf` |

Until the official Kimari-4B weights are released, only the `test` profile
is usable out of the box. For other profiles, rename any compatible GGUF to match,
or edit the profile config to point to your file.

## File Sizes (estimated)

Typical sizes for 4B parameter models at various quantization levels:

| Quantization | Est. Size | Profile |
|-------------|-----------|---------|
| Q4_K_M | ~3.1 GiB | gtx1060 |
| Q5_K_M | ~3.8 GiB | gtx1080 |
| IQ4_XS | ~2.8 GiB | turbo |
| Q8_0 | ~5.0 GiB | (custom) |
| F16 | ~7.5 GiB | (custom) |

> **Note:** These sizes are approximate and vary by model architecture. Actual
> file sizes may differ depending on the base model and tokenizer.
