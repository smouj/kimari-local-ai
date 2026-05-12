# Kimari Local AI

**Local AI for older NVIDIA GPUs.**

Kimari is an open-source framework for running local LLMs on consumer NVIDIA GPUs such as GTX 1060 6GB and GTX 1080 8GB.

It provides:

- GGUF runtime workflows with llama.cpp
- CUDA-aware setup and diagnostics
- GPU-specific profiles
- OpenAI-compatible local endpoint
- Open WebUI / OpenClaw / Continue.dev integration docs
- KimariFit evaluation tooling
- Private training and evaluation pipeline for future Kimari models

> Current framework version: v0.1.53-alpha
> Status: usable alpha framework, not production-ready.

---

## What works today

| Milestone | Status |
|-----------|--------|
| GTX 1060 6GB local runtime | ✅ Validated |
| llama-server CUDA | ✅ Validated |
| TinyLlama GGUF test model | ✅ Validated |
| Local `/v1/chat/completions` endpoint | ✅ Validated |
| HF Jobs GPU smoke | ✅ Completed |
| First micro SFT | ✅ Completed (private, ephemeral) |
| Private adapter persistence | ✅ Completed (private repo) |
| Adapter load check | ✅ Completed |
| KimariEval Private v1 | ✅ Created (104 cases, 7 categories) |
| Baseline vs adapter eval infrastructure | ✅ Ready |
| Kimari-4B public release | ❌ NOT released |

---

## Kimari-4B status

Kimari-4B is **not released yet**.

Current model work is private and experimental:

- Private micro SFT completed
- Private adapter persisted to `Smouj013/kimari4b-micro-sft-adapter-v0`
- Adapter load check completed
- Private evaluation harness created (KimariEval Private v1)
- Baseline vs adapter evaluation infrastructure ready

No public artifacts:

- ❌ No public weights
- ❌ No public adapters
- ❌ No public GGUF
- ❌ No public benchmark claims

Preview gate: **BLOCKED**

---

## Hugging Face resources

| Resource | Link |
|----------|------|
| **Space** | [kimari-ai/kimari-fit-lab](https://huggingface.co/spaces/kimari-ai/kimari-fit-lab) |
| **Organization Card** | [kimari-ai/README](https://huggingface.co/spaces/kimari-ai/README) |
| **Reference Collection** | [Smouj013/kimari-compatible-gguf-models](https://huggingface.co/collections/Smouj013/kimari-compatible-gguf-models-6a0352c75d2bfeff34d51e66) |

The reference collection contains community/reference GGUF models that Kimari can help run locally. They are **not official Kimari models**.

---

## Repository

GitHub: https://github.com/smouj/kimari-local-ai

License: MIT
Status: active alpha development