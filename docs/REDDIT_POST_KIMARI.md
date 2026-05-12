# Reddit Posts — Kimari Local AI

> Ready-to-use posts for Reddit. Edit before posting.

**Rules**: No spam. No Kimari-4B release claims. No fake benchmarks. Be humble.

---

## Technical Version

**Title**: Kimari Local AI — open-source framework for running LLMs on GTX 1060 GPUs

**Body**:

I've been working on Kimari, a Python CLI framework for running local LLM inference on consumer NVIDIA GPUs — specifically targeting the GTX 1060 (6GB) and GTX 1080 (8GB).

**What works:**

- ✅ Validated on real GTX 1060 6GB (WSL2 Ubuntu, CUDA 12.0)
- ✅ 228 tok/s prompt, 73 tok/s generation (CUDA vs 77/33 CPU)
- ✅ OpenAI-compatible endpoint: /v1/chat/completions, /v1/models, /health
- ✅ Integrations: Open WebUI, OpenClaw, Continue.dev
- ✅ Hugging Face Space: GPU compatibility checker

**What doesn't exist yet:**

- ❌ Kimari-4B model weights (the planned target model)
- ❌ No weights, adapters, or GGUF files published
- ❌ Gate is BLOCKED — alpha status, no training performed

The framework uses llama-server with CUDA acceleration. You pick a profile based on your GPU, and it configures the server automatically. Test model is TinyLlama 1.1B Q4_K_M.

**Links:**

- GitHub: https://github.com/smouj/kimari-local-ai
- HF Space: https://huggingface.co/spaces/kimari-ai/kimari-fit-lab
- License: MIT

I'm sharing this early because I'd love feedback on the approach — framework first, model later. The idea is to make local inference dead simple for people with old gaming GPUs.

---

## Humble Version

**Title**: Built a small CLI tool for running local LLMs on old GPUs (GTX 1060). Feedback welcome.

**Body**:

Hey everyone,

I put together a small open-source CLI that makes it easier to run local LLMs on consumer GPUs. I tested it on my GTX 1060 6GB and it works:

- ~228 tok/s prompt processing, ~73 tok/s generation using CUDA
- OpenAI-compatible API endpoint on localhost
- Works with Open WebUI, Continue.dev, etc.

It's called Kimari. It's very early (alpha, v0.1.46) and there's no custom model yet — I'm using TinyLlama 1.1B for testing.

The goal is "framework first, model later." I want the tooling to be solid before even thinking about training a model.

MIT licensed, Python, built on llama.cpp. Would appreciate any feedback.

https://github.com/smouj/kimari-local-ai

---

## Suggested Subreddits

| Subreddit | Type | Notes |
|-----------|------|-------|
| r/LocalLLaMA | Primary | Best fit, local inference focus |
| r/MachineLearning | Secondary | Academic angle |
| r/opensource | Optional | Open source angle |
| r/Python | Optional | CLI/tool angle |
| r/nvidia | Optional | GPU/hardware angle |

**Posting tips:**

- Post to one subreddit at a time (not spam)
- Wait for feedback before cross-posting
- Respond to comments honestly
- Don't overstate capabilities
- Mention TinyLlama explicitly, not Kimari-4B
- If someone asks "can it run Kimari-4B?" → say "Kimari-4B doesn't exist yet"