# Hugging Face Collections: kimari-compatible-gguf-models

> **Collection URL**: https://huggingface.co/collections/Smouj013/kimari-compatible-gguf-models-6a0352c75d2bfeff34d51e66

## Purpose

This collection lists **community/reference GGUF models** that Kimari Local AI can help run locally on consumer hardware. It is a convenience guide, not an official endorsement.

## Important Disclaimers

⚠️ These are **NOT official Kimari models**.
⚠️ Kimari-4B is **NOT included** — it is not released yet.
⚠️ These models are listed for reference only.
⚠️ Each model has its own license — check before using.

## Current Collection

| Model | Size | VRAM (Q4_K_M) | Notes |
|-------|------|---------------|-------|
| TinyLlama 1.1B | 1.1B | ~1.5 GB | Test/validation model used by Kimari |
| Qwen2.5 1.5B | 1.5B | ~2 GB | Good for 4GB+ GPUs |
| Qwen2.5 3B | 3B | ~3 GB | Good for 6GB+ GPUs |
| Llama 3.2 3B | 3B | ~3 GB | Good for 6GB+ GPUs |

> More models will be added as they are tested with Kimari profiles.

## Criteria for Adding Models

Models added to this collection must meet:

1. **GGUF format** — compatible with llama.cpp/llama-server
2. **Small to medium size** — 1B-8B parameters recommended for 6-8GB GPUs
3. **Reasonable VRAM** — should fit in 6-8GB at Q4_K_M quantization
4. **Clear license** — permissive or community license (Apache 2.0, MIT, etc.)
5. **No false claims** — must not be listed as "official Kimari model"

## How to Add a Model

1. Find the model on Hugging Face
2. Verify it meets the criteria above
3. Add it via the HF Collections UI or CLI:
   ```bash
   hf collections add-item Smouj013/kimari-compatible-gguf-models-6a0352c75d2bfeff34d51e66 --item=<model-repo-id>
   ```
4. Update this document with the new entry

## How NOT to Use This Collection

❌ Do not present these as Kimari official releases
❌ Do not claim Kimari-4B is available
❌ Do not use for benchmark claims about Kimari-4B
❌ Do not add models without verifying their license

## Gate Status

**BLOCKED** — Kimari-4B is not released. This collection contains reference models only.