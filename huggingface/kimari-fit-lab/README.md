---
title: Kimari Fit Lab
emoji: 🔬
colorFrom: purple
colorTo: blue
sdk: gradio
sdk_version: 5.34.2
app_file: app.py
pinned: false
license: mit
---

# Kimari Fit Lab

Static compatibility helper for Kimari Local AI v0.1.69-alpha.

This Space does **not** run models, does **not** download models, and does **not** use API keys. It estimates compatibility from GPU/VRAM/RAM and suggests safe local commands.

## Current Status (v0.1.69-alpha)

| Milestone | Status |
|---|---|
| GTX 1060 local runtime | ✅ Validated with TinyLlama test model |
| llama-server CUDA | ✅ Validated |
| OpenAI-compatible endpoint | ✅ Validated |
| Open WebUI / OpenClaw / Continue docs | ✅ Available |
| HF Jobs GPU smoke | ✅ Completed |
| Private micro SFT | ✅ Completed privately |
| KimariEval Private v1 | ✅ Created, 104 private cases |
| Subset10 private completion/integrity eval | ✅ Completed, not scored |
| Kimari-4B public release | ❌ NOT released |

**Kimari-4B is not released yet.** No public weights, public adapters, or official Kimari-4B GGUF files are available.

## Links

- GitHub: https://github.com/smouj/kimari-local-ai
- Docs: https://smouj.github.io/kimari-local-ai/
- Org Card: https://huggingface.co/spaces/kimari-ai/README
- Reference GGUF Collection: https://huggingface.co/collections/Smouj013/kimari-compatible-gguf-models-6a0352c75d2bfeff34d51e66

Gate: **BLOCKED**. No public benchmark claims.
