# Hugging Face Community Post

> Ready-to-use post for Hugging Face community. Edit before posting.

**Rules**: No Kimari-4B release claims. Ask for feedback, don't sell.

---

## Post

**Title**: Kimari Local AI — run LLMs on your GTX 1060 🔬

**Body**:

Hey HF community! 👋

I've been working on **Kimari**, an open-source CLI framework for running local LLM inference on consumer NVIDIA GPUs. I just deployed a live Space and would love your feedback.

### What Kimari does

Kimari makes it easy to run local LLMs on old gaming GPUs:

- **CLI framework**: `kimari start --profile gtx1060` configures llama-server with CUDA automatically
- **OpenAI-compatible endpoint**: Drop-in replacement for OpenAI API on localhost
- **GPU profiles**: Pre-configured for GTX 1060 (6GB), GTX 1080 (8GB), RTX 2060, etc.
- **Integrations**: Works with Open WebUI, OpenClaw, Continue.dev

### What I've validated

On a real **GTX 1060 6GB** (WSL2 Ubuntu, CUDA 12.0):

| Metric | CUDA | CPU |
|--------|------|-----|
| Prompt tok/s | 228 | 77 |
| Generation tok/s | 73 | 33 |

Test model: **TinyLlama 1.1B Q4_K_M**

### Hugging Face presence

- **Space**: [kimari-ai/kimari-fit-lab](https://huggingface.co/spaces/kimari-ai/kimari-fit-lab) — GPU compatibility checker (doesn't run models, just checks if your GPU fits)
- **Org Card**: [kimari-ai/README](https://huggingface.co/spaces/kimari-ai/README)
- **Collection**: [kimari-compatible-gguf-models](https://huggingface.co/collections/Smouj013/kimari-compatible-gguf-models-6a0352c75d2bfeff34d51e66) — reference GGUF models for local inference

### Framework vs. Model

**Important**: Kimari-4B is the planned target model, but it's **not released yet**. No weights, no adapters, no GGUF files exist. The framework works with any compatible GGUF model (currently tested with TinyLlama).

The approach is **framework first, model later** — make the tooling solid before training.

### What I'd love feedback on

1. Is the "framework first" approach sensible for the HF community?
2. What models would you want in the compatibility collection?
3. Any suggestions for the GPU compatibility checker Space?
4. What's the best path to a first community model?

### Links

- **GitHub**: https://github.com/smouj/kimari-local-ai
- **License**: MIT
- **Status**: Alpha (gate BLOCKED — no training, no uploads)

Thanks for reading! 🙏