# Kimari AI

> Current framework version: v0.1.63-alpha
> Status: alpha framework, public model gate BLOCKED

## Kimari Local AI — Local AI for older NVIDIA GPUs.

Kimari Local AI is an open-source, local-first framework for running GGUF language models on consumer NVIDIA GPUs. It combines llama.cpp CUDA inference, a practical CLI, GPU profiles, local configuration helpers, and an OpenAI-compatible endpoint for tools such as Open WebUI, OpenClaw, and Continue.dev.

Kimari is the framework. **Kimari-4B is not released yet.**

## What works today

| Area | Status |
|---|---|
| GTX 1060 local runtime validation | ✅ Validated with a TinyLlama test model |
| llama.cpp CUDA runtime | ✅ Validated locally |
| Local OpenAI-compatible endpoint | ✅ `/v1/models` and `/v1/chat/completions` validated |
| Open WebUI integration docs | ✅ Available |
| OpenClaw integration docs | ✅ Available |
| Continue.dev integration docs | ✅ Available |
| HF Jobs GPU smoke | ✅ Completed |
| Private micro SFT pipeline | ✅ Completed privately |
| Private adapter persistence | ✅ Completed in a private repo |
| KimariEval Private v1 | ✅ Created, 104 private cases across 7 categories |
| Subset10 private completion/integrity eval | ✅ Completed, not scored, manual review required |

## What is not released

The following are **not** public:

- Kimari-4B public weights
- public Kimari-4B adapters
- official Kimari-4B GGUF files
- public benchmark claims
- production-ready guarantees

Any reference to Kimari-4B is a roadmap or private-pipeline reference unless explicitly stated otherwise.

## Quick start

```bash
# Check local environment
kimari doctor --deep

# Download the small test model
kimari pull test

# Start the local endpoint with the test profile
kimari start --profile test
```

Then connect local tools to:

```txt
http://127.0.0.1:11435/v1
```

## Resources

- GitHub: https://github.com/smouj/kimari-local-ai
- Documentation: https://smouj.github.io/kimari-local-ai/
- Space: https://huggingface.co/spaces/kimari-ai/kimari-fit-lab
- Reference GGUF Collection: https://huggingface.co/collections/Smouj013/kimari-compatible-gguf-models-6a0352c75d2bfeff34d51e66

## Gate

Preview gate: **BLOCKED**

No public weights, adapters, GGUF files, or public benchmark claims are published from this project at this stage.
