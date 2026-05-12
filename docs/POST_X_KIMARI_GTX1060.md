# X (Twitter) Posts — Kimari GTX 1060

> Ready-to-use posts for X/Twitter. Edit before posting.

**Rules**: No Kimari-4B release claims. No fake benchmarks. No tokens/paths.

---

## Short (EN)

```
🧠 Kimari Local AI: run LLMs on a 2016 GTX 1060 GPU

228 tok/s prompt | 73 tok/s generation
OpenAI-compatible endpoint on localhost
Works with Open WebUI, OpenClaw, Continue.dev

Test model: TinyLlama 1.1B Q4_K_M
Kimari-4B: not released yet

→ github.com/smouj/kimari-local-ai
→ huggingface.co/spaces/kimari-ai/kimari-fit-lab
```

## Short (ES)

```
🧠 Kimari Local AI: LLMs locales en una GTX 1060 de 2016

228 tok/s prompt | 73 tok/s generación
Endpoint OpenAI-compatible en localhost
Funciona con Open WebUI, OpenClaw, Continue.dev

Modelo test: TinyLlama 1.1B Q4_K_M
Kimari-4B: aún no publicado

→ github.com/smouj/kimari-local-ai
→ huggingface.co/spaces/kimari-ai/kimari-fit-lab
```

## Technical (EN)

```
Kimari Local AI — open-source framework for running LLMs on consumer GPUs 🧠

What's validated on a real GTX 1060 6GB (WSL2, CUDA 12.0):

• llama-server with CUDA: 228 tok/s prompt, 73 tok/s generation
• OpenAI-compatible endpoint: /v1/chat/completions
• Integrations: Open WebUI, OpenClaw, Continue.dev
• CLI: kimari doctor --deep, kimari start --profile test

HF Space (GPU compat checker):
huggingface.co/spaces/kimari-ai/kimari-fit-lab

⚠️ Kimari-4B is NOT released. No weights available.
Test model: TinyLlama 1.1B Q4_K_M

github.com/smouj/kimari-local-ai
```

## Thread (EN)

```
🧵 Thread: Kimari Local AI — running local LLMs on old consumer GPUs

1/5

Kimari is an open-source CLI framework that makes local LLM inference accessible on GPUs like the GTX 1060 (2016). No cloud. No API keys. Your hardware, your model.

2/5

Validated on a real GTX 1060 6GB with CUDA:
• Prompt: 228 tok/s
• Generation: 73 tok/s
• Model: TinyLlama 1.1B Q4_K_M
• llama-server compiled for compute capability 6.1

3/5

Kimari provides an OpenAI-compatible endpoint on localhost:
• /v1/chat/completions
• /v1/models
• /health

Works with Open WebUI, OpenClaw, Continue.dev, and any OpenAI client.

4/5

Hugging Face presence:
• Space: GPU compatibility checker → huggingface.co/spaces/kimari-ai/kimari-fit-lab
• Org Card: huggingface.co/spaces/kimari-ai/README
• Collection: compatible GGUF models for old GPUs

5/5

⚠️ Important disclaimers:
• Kimari-4B is NOT released yet (no weights, no adapters)
• Performance numbers are for TinyLlama, not Kimari-4B
• Gate is BLOCKED — alpha status
• No training performed

github.com/smouj/kimari-local-ai
```

## Table Version (EN)

```
Kimari Local AI on GTX 1060 6GB 🔬

| Metric | CUDA | CPU |
|--------|------|-----|
| Prompt tok/s | 228 | 77 |
| Gen tok/s | 73 | 33 |

Model: TinyLlama 1.1B Q4_K_M (NOT Kimari-4B)
Endpoint: OpenAI-compatible on localhost
Integrations: Open WebUI, OpenClaw, Continue.dev

⚠️ Kimari-4B not released | Gate BLOCKED

github.com/smouj/kimari-local-ai
```