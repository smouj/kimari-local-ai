# Hugging Face Organization Card: kimari-ai

> Recommended public text for the `kimari-ai` Hugging Face organization card.

---

## Kimari AI

**Open-source framework for running local LLMs on consumer NVIDIA GPUs.**

### What is Kimari?

Kimari is a Python CLI framework that makes it easy to run local LLM inference on consumer hardware — specifically NVIDIA GTX 1060 (6GB) and GTX 1080 (8GB) GPUs and above. It's built on llama.cpp with CUDA acceleration and provides an OpenAI-compatible API endpoint.

### What works now?

- ✅ **Local inference validated on GTX 1060**: 228 tok/s prompt, 73 tok/s generation with TinyLlama 1.1B Q4_K_M
- ✅ **OpenAI-compatible endpoint**: `/v1/chat/completions`, `/v1/models`, `/health`
- ✅ **Local integrations**: Open WebUI, OpenClaw, Continue.dev
- ✅ **CUDA acceleration**: llama-server compiled for consumer GPUs
- ✅ **CLI tools**: `kimari doctor --deep`, `kimari start --profile test`, `kimari integrations generate`

### Kimari-4B Status

**Kimari-4B is not released yet.** No weights, adapters, GGUF files, or checkpoints are available publicly.

The "Kimari-4B" name refers to a planned fine-tuned model that will be the recommended default for the Kimari framework. Until it's released, Kimari runs any compatible GGUF model (TinyLlama, Qwen, Llama, etc.).

### Roadmap

| Stage | Status |
|-------|--------|
| Framework CLI | ✅ Alpha (v0.1.44) |
| Local inference (GTX 1060) | ✅ Validated |
| OpenAI-compatible endpoint | ✅ Validated |
| Kimari-4B fine-tuning | 🔜 Planned (gate BLOCKED) |
| Kimari-4B weights release | 🔜 Planned (gate BLOCKED) |
| HF Spaces demo | 📋 Prepared |

### Links

- **GitHub**: [smouj/kimari-local-ai](https://github.com/smouj/kimari-local-ai)
- **Docs**: [smouj.github.io/kimari-local-ai](https://smouj.github.io/kimari-local-ai/)
- **License**: MIT

### Gate Status

**BLOCKED** — Kimari is in active early development. No weights, no public releases, no training performed.

---

*Last updated: 2026-05-12*