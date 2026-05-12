# Public Launch Pack

> Consolidated material for launching Kimari Local AI publicly.

**Key message**: Kimari Local AI runs real local inference on a GTX 1060 6GB. Framework first. Kimari-4B later.

## Central Claims

1. ✅ **GTX 1060 6GB validated** — 228 tok/s prompt, 73 tok/s generation (TinyLlama 1.1B Q4_K_M)
2. ✅ **OpenAI-compatible endpoint** — `/v1/chat/completions`, `/v1/models`, `/health`
3. ✅ **CUDA acceleration** — llama-server compiled for consumer GPUs
4. ✅ **Local integrations** — Open WebUI, OpenClaw, Continue.dev
5. ✅ **Hugging Face Space live** — GPU compatibility checker

## Disclaimers

- ❌ Kimari-4B is **not released yet** — no weights, no adapters, no GGUF files
- ❌ No training has been performed
- ❌ No benchmarks for Kimari-4B (it doesn't exist yet)
- ❌ Gate is **BLOCKED** — alpha status
- ⚠️ All performance numbers are for **TinyLlama 1.1B Q4_K_M**, NOT Kimari-4B

## Assets

| Asset | Link |
|-------|------|
| **GitHub** | https://github.com/smouj/kimari-local-ai |
| **HF Space** | https://huggingface.co/spaces/kimari-ai/kimari-fit-lab |
| **HF Org Card** | https://huggingface.co/spaces/kimari-ai/README |
| **HF Collection** | https://huggingface.co/collections/Smouj013/kimari-compatible-gguf-models-6a0352c75d2bfeff34d51e66 |
| **GTX 1060 Showcase** | [docs/GTX1060_SHOWCASE.md](GTX1060_SHOWCASE.md) |

## Posts

| Platform | Doc |
|----------|-----|
| **X / Twitter** | [POST_X_KIMARI_GTX1060.md](POST_X_KIMARI_GTX1060.md) |
| **Reddit** | [REDDIT_POST_KIMARI.md](REDDIT_POST_KIMARI.md) |
| **Hugging Face Community** | [HUGGINGFACE_COMMUNITY_POST.md](HUGGINGFACE_COMMUNITY_POST.md) |

## Short Technical Card

```
Kimari Local AI v0.1.46-alpha
─────────────────────────────
Framework for local LLM inference on consumer NVIDIA GPUs

✅ Validated: GTX 1060 6GB (228/73 tok/s with CUDA)
✅ Endpoint:  OpenAI-compatible on localhost
✅ Integrations: Open WebUI, OpenClaw, Continue.dev
✅ Space: huggingface.co/spaces/kimari-ai/kimari-fit-lab

⚠️ Kimari-4B: Not released yet
⚠️ Gate: BLOCKED (alpha)

github.com/smouj/kimari-local-ai
```

## Before Posting Checklist

- [ ] No tokens, API keys, or session cookies in post text
- [ ] No private paths (`/home/username/`)
- [ ] No claims that Kimari-4B is released
- [ ] No fake benchmarks
- [ ] No billing/plan information
- [ ] Model specified as TinyLlama (not Kimari-4B)
- [ ] Gate status mentioned as BLOCKED
- [ ] Links verified and working