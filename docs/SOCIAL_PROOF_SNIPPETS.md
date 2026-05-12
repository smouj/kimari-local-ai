# Social Proof Snippets

> Short, honest texts for sharing Kimari Local AI publicly.

**Rules**: No fake benchmarks. No Kimari-4B release claims. No tokens or private data. Gate is BLOCKED.

---

## GitHub README Snippet

```markdown
## Validated on GTX 1060 6GB

Kimari has been tested on a real NVIDIA GeForce GTX 1060 6GB (WSL2 Ubuntu 24.04) with llama-server CUDA:

- Prompt processing: 228 tok/s (CUDA) vs 77 tok/s (CPU)
- Generation: 73 tok/s (CUDA) vs 33 tok/s (CPU)
- Model: TinyLlama 1.1B Q4_K_M (test model, NOT Kimari-4B)
- OpenAI-compatible endpoint: /v1/chat/completions, /v1/models, /health

Try it: `kimari start --profile test`

⚠️ Kimari-4B is not yet released. No weights, adapters, or GGUF files are available.
```

---

## X (Twitter) Post

```
🧠 Kimari Local AI runs on a GTX 1060 (2016 GPU!) with CUDA acceleration:

228 tok/s prompt | 73 tok/s generation
OpenAI-compatible endpoint on localhost
Works with Open WebUI, OpenClaw, Continue.dev

Test model: TinyLlama 1.1B Q4_K_M
Kimari-4B: not released yet

github.com/smouj/kimari-local-ai
```

---

## Reddit Post (r/LocalLLaMA)

```
Title: Kimari Local AI — Open-source framework for running LLMs on old GTX 1060 GPUs

I've been working on Kimari, a CLI framework that makes it easy to run local LLM inference on consumer GPUs — specifically the GTX 1060 6GB and GTX 1080 8GB.

What works:
- ✅ Validated on real GTX 1060 6GB (WSL2 Ubuntu)
- ✅ 228 tok/s prompt processing, 73 tok/s generation with CUDA
- ✅ OpenAI-compatible endpoint (/v1/chat/completions, /v1/models, /health)
- ✅ Integrations with Open WebUI, OpenClaw, Continue.dev
- ✅ Hugging Face Space demo: kimari-ai/kimari-fit-lab

What doesn't work yet:
- ❌ Kimari-4B is not released (the target model)
- ❌ No weights, adapters, or GGUF files published
- ❌ Gate is BLOCKED — no training, no upload

The framework uses llama-server with CUDA and comes with profiles for different GPU tiers. Test model is TinyLlama 1.1B Q4_K_M.

github.com/smouj/kimari-local-ai
```

---

## Hugging Face Community Post

```
Kimari Local AI — run LLMs on your GTX 1060 🔬

Kimari is an open-source CLI framework for running local LLMs on consumer NVIDIA GPUs (GTX 1060 6GB+). It's built on llama.cpp with CUDA acceleration and provides an OpenAI-compatible API endpoint.

Live demo: https://huggingface.co/spaces/kimari-ai/kimari-fit-lab

What's validated:
- GTX 1060 6GB local inference (228 tok/s prompt, 73 tok/s generation)
- OpenAI-compatible endpoint on localhost
- Open WebUI, OpenClaw, Continue.dev integrations

What's NOT available yet:
- Kimari-4B model weights (not released)
- No training, no upload

The HF Space is a GPU compatibility checker — it doesn't run any model. Try it to see if your GPU fits.
```

---

## Key Messages

Always include these points:

1. **Framework is usable** — CLI, profiles, CUDA, endpoint work
2. **Tested on real hardware** — GTX 1060, actual tok/s numbers
3. **Kimari-4B is NOT released** — no weights, no GGUF, no adapters
4. **Open source** — MIT license, GitHub
5. **Honest benchmarks only** — TinyLlama numbers, not Kimari-4B claims