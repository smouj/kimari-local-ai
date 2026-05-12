# Collection Seed Plan

> Proposed reference GGUF models for the `kimari-compatible-gguf-models` Collection.

**Collection URL**: https://huggingface.co/collections/Smouj013/kimari-compatible-gguf-models-6a0352c75d2bfeff34d51e66

**Important**: These are NOT official Kimari models. They are community/reference models that Kimari can help run locally.

## Proposed Models

| Model | Repo | License | Size | VRAM (Q4_K_M) | Kimari Profile | Notes |
|-------|------|---------|------|---------------|----------------|-------|
| TinyLlama 1.1B | https://huggingface.co/TheBloke/TinyLlama-1.1B-Chat-v1.0-GGUF | Apache 2.0 | 1.1B | ~1.5 GB | `test` | Current test/validation model |
| Qwen2.5 1.5B | https://huggingface.co/Qwen/Qwen2.5-1.5B-Instruct-GGUF | Apache 2.0 | 1.5B | ~2 GB | `test` | Good small model |
| SmolLM2 1.7B | https://huggingface.co/HuggingFaceTB/SmolLM2-1.7B-Instruct-GGUF | Apache 2.0 | 1.7B | ~2 GB | `test` | Lightweight, HF official |
| Llama 3.2 1B | https://huggingface.co/hugging-quants/Llama-3.2-1B-Instruct-Q4_K_M-GGUF | Llama 3.2 Community | 1B | ~1.5 GB | `test` | Popular, small variant |
| Llama 3.2 3B | https://huggingface.co/hugging-quants/Llama-3.2-3B-Instruct-Q4_K_M-GGUF | Llama 3.2 Community | 3B | ~3 GB | `gtx1060` | Popular, 6GB+ GPUs |

## Selection Criteria

1. **GGUF format** — compatible with llama.cpp/llama-server
2. **Small size** — 1B-4B parameters, fits 6GB VRAM at Q4_K_M
3. **Clear license** — Apache 2.0, MIT, or permissive community license
4. **Available on HF** — downloadable without special access
5. **No false claims** — must not be listed as "official Kimari model"

## What NOT to Include

❌ Models larger than 8B (won't fit GTX 1060)
❌ Models with unclear or restrictive licenses
❌ Any model labeled as "official Kimari model"
❌ Kimari-4B (not released yet)

## How to Add to Collection

```bash
hf collections add-item Smouj013/kimari-compatible-gguf-models-6a0352c75d2bfeff34d51e66 --item=<repo-id>
```

## Validation

Run the seed validator before adding:

```bash
python scripts/huggingface/validate_collection_seed.py --input huggingface/collections/kimari-compatible-gguf.seed.example.json --json
```