# Kimari vs. Other Local LLM Tools

**An honest, fact-based comparison.** Kimari is alpha software (v0.1.4-alpha). It is not production-ready, not as feature-complete as the tools below, and should be evaluated accordingly. This document exists to help you pick the right tool for your situation — even if that tool isn't Kimari.

---

## Tools Compared

| Tool | One-Line Summary |
|------|-----------------|
| **Kimari** | CLI-first local AI optimized for old consumer GPUs |
| **Ollama** | Popular model runner with simple CLI and built-in API |
| **LM Studio** | Polished desktop app for discovering and running models |
| **llama.cpp** | The raw C++ inference engine (no wrapper) |
| **text-generation-webui** | Feature-rich web UI for local LLMs (oobabooga) |
| **KoboldCpp** | Lightweight llama.cpp wrapper with built-in web UI |
| **Open WebUI** | Full-featured web chat frontend for Ollama/any OpenAI API |

---

## At a Glance

| Criterion | Kimari | Ollama | LM Studio |
|-----------|--------|--------|-----------|
| Primary objective | Maximize useful AI on old consumer GPUs | Simplest way to run LLMs locally | Discover, configure, and chat with models via GUI |
| Ease of installation | Medium — clone repo, pip install, build llama.cpp | Easy — one-line installer | Easy — download .dmg/.exe/AppImage |
| OpenAI-compatible API | Yes (via llama-server) | Yes (built-in) | Yes (built-in) |
| Offline / local-first | Yes | Yes | Mostly (model discovery needs internet) |
| Privacy | Full local, zero telemetry | Full local, minimal telemetry opt-in | Local inference; app phones home for model hub |
| Old GPU support (GTX 1060/1080) | **First-class** — dedicated profiles, KimariFit scoring | Works, but no GPU-specific tuning | Works, but no guidance per GPU model |
| Benchmark capabilities | Built-in `bench` and `fit` commands | No built-in benchmarking | No built-in benchmarking |
| Maturity level | **Alpha** | Mature (v0.5+, large community) | Mature (v0.3+, commercial backing) |

| Criterion | llama.cpp | text-generation-webui | KoboldCpp | Open WebUI |
|-----------|-----------|----------------------|-----------|------------|
| Primary objective | Maximum inference performance, minimal abstraction | All-in-one web UI for local LLMs | Easy llama.cpp with a web UI on top | Chat frontend for any OpenAI-compatible backend |
| Ease of installation | Medium — build from source or grab binary | Medium — pip/conda, many deps | Easy — single executable download | Medium — Docker or pip, needs a backend |
| OpenAI-compatible API | Yes (llama-server) | Partial (extensions) | Yes | N/A — consumes an API, doesn't serve one |
| Offline / local-first | Yes | Yes | Yes | Yes (with local backend) |
| Privacy | Full local | Full local | Full local | Full local (with local backend) |
| Old GPU support (GTX 1060/1080) | Works — you tune flags manually | Works — you configure manually | Works — some presets | N/A — depends on backend |
| Benchmark capabilities | Manual via custom prompts/scripts | No built-in benchmarking | Basic token counting | No built-in benchmarking |
| Maturity level | Very mature | Mature | Mature | Mature |

---

## Detailed Comparisons

### Kimari vs. Ollama

Ollama is the most popular local LLM runner and for good reason: the installation experience is near-zero-friction, the CLI is intuitive, and the model library is large. It auto-detects GPU and picks reasonable defaults.

**Where Ollama wins:**
- One-command install. No building, no C++ compilation.
- Large curated model library with `ollama pull`.
- Multi-model serving (keep several models loaded).
- Built-in REST API on `localhost:11434` — well-documented.
- Massive community, extensive integrations.

**Where Kimari wins:**
- GPU-specific profiles (GTX 1060, GTX 1080) with tuned batch sizes, context limits, and quantization targets. Ollama picks sensible defaults but does not optimize per GPU model.
- KimariFit scoring — know whether a model will fit your VRAM *before* you try to load it. Ollama gives you an OOM error after the fact.
- Built-in benchmark command (`kimari bench`) for measuring tokens/s and TTFT on your actual hardware.
- Explicit about old hardware — every default is designed around 6–8 GB VRAM.

**Honest assessment:** If you have a modern GPU (RTX 3060+) and want the smoothest experience, use Ollama. If you are on a GTX 1060 or 1080 and want someone to have already solved the "which quant at which context won't OOM" problem for you, Kimari is worth trying.

---

### Kimari vs. LM Studio

LM Studio offers a beautiful desktop GUI for browsing Hugging Face, downloading GGUF models, and chatting with them. It's the easiest on-ramp for non-technical users.

**Where LM Studio wins:**
- Polished GUI — no terminal needed.
- Built-in model search and download from Hugging Face.
- Hardware auto-detection with visual VRAM usage indicator.
- Cross-platform (Windows, macOS, Linux).
- No build steps — download and run.

**Where Kimari wins:**
- CLI-first and scriptable — fits into dev workflows, CI, and automation.
- KimariFit scoring gives a numeric predict-before-you-run metric. LM Studio shows VRAM usage *after* loading.
- GPU profiles are explicit and auditable (JSON config files). LM Studio's auto-detection is opaque.
- Open source (MIT). LM Studio is source-available but not OSI-approved open source.

**Honest assessment:** If you want a GUI and don't care about scripting or old GPU optimization, LM Studio is the better choice today. If you want CLI automation and GPU-specific tuning, Kimari is more aligned — but be aware it's alpha.

---

### Kimari vs. llama.cpp (Raw)

llama.cpp is the engine under Kimari's hood. It provides maximum control and maximum performance with minimum abstraction.

**Where llama.cpp wins:**
- No overhead, no wrapper, no opinions. You control every flag.
- First to support new quantization formats, attention types, and hardware.
- Most mature and battle-tested inference engine in the ecosystem.
- Can be used as a library (C/C++/Python bindings).

**Where Kimari wins:**
- You don't have to memorize `llama-server` flags like `-ngl`, `-b`, `-ub`, `-c`, `-nkvo`, `--mlock`, etc. GPU profiles encode this knowledge.
- `kimari doctor` validates your CUDA setup before you start.
- `kimari fit` tells you if a model+context combo will OOM before you launch the server.
- `kimari bench` automates performance measurement with standard prompts.
- `kimari pull` downloads models from a curated registry.
- Experimental AMD ROCm build script (`scripts/linux/build-llamacpp-rocm.sh`) for non-NVIDIA GPUs.

**Honest assessment:** If you are comfortable with llama.cpp and know which flags to set, you don't need Kimari. Kimari's value is in encoding that expertise so you don't have to rediscover it. Power users may prefer the raw control of llama.cpp directly.

---

### Kimari vs. text-generation-webui (oobabooga)

text-generation-webui is the Swiss Army knife of local LLMs: it supports multiple backends (llama.cpp, ExLlamaV2, Transformers), has a full web UI, and exposes many tuning parameters.

**Where text-generation-webui wins:**
- Supports multiple inference backends, not just llama.cpp.
- Rich web UI with chat, notebook, and parameter-tuning modes.
- Extensions system (LoRA training, TTS, STT, multimodal, etc.).
- Large community and plugin ecosystem.
- Fine-tuning and training support built in.

**Where Kimari wins:**
- Much simpler setup — fewer dependencies, no conda environment needed.
- CLI-native rather than GUI-native — better for scripting and headless servers.
- GPU profiles remove the need to manually tune parameters.
- KimariFit scoring is unique; no equivalent in text-generation-webui.
- Lighter weight — doesn't bundle features you may not need.

**Honest assessment:** If you want maximum control over inference parameters, multi-backend support, or fine-tuning, text-generation-webui is far more capable. If you want a focused, opinionated tool that just works on old GPUs, Kimari is simpler — but far less feature-rich.

---

### Kimari vs. KoboldCpp

KoboldCpp is a lightweight, single-executable llama.cpp wrapper with a built-in web UI. It's designed to be the simplest way to get a local LLM running with a GUI.

**Where KoboldCpp wins:**
- Single executable — no Python, no build step, no dependencies.
- Built-in web UI for chat — no separate frontend needed.
- Preset configurations for common hardware tiers.
- Supports GGUF, and can run on CPU-only systems.
- Very low barrier to entry.

**Where Kimari wins:**
- KimariFit scoring — predict VRAM fit before launching.
- CLI-first design supports automation, scripting, and CI.
- Structured benchmark framework with standard prompts.
- Model registry with `kimari pull` for reproducible setups.
- More explicit and auditable profile configuration.

**Honest assessment:** If you want the fastest path from zero to chatting with a model in a browser, KoboldCpp is hard to beat. If you care about CLI workflows, reproducible profiles, or benchmarking, Kimari offers more structure. Kimari does not yet have a built-in web UI.

---

### Kimari vs. Open WebUI (Standalone)

Open WebUI is a full-featured chat interface — think "local ChatGPT" — that connects to any OpenAI-compatible backend (Ollama, llama.cpp server, Kimari, etc.).

**Where Open WebUI wins:**
- Best-in-class web chat UI with conversations, personas, document upload, and RAG.
- Mature, actively developed, large community.
- Works with any backend — not tied to one tool.
- User management, authentication, and multi-user support.
- Rich ecosystem of community tools and plugins.

**Where Kimari wins:**
- Kimari is a full stack (runtime + CLI + profiles + scoring). Open WebUI is only the frontend — you still need a backend.
- KimariFit scoring and GPU profiles have no equivalent in Open WebUI.
- CLI automation and scripting.
- Benchmark framework.

**Honest assessment:** These tools are complementary, not competing. Kimari can serve as the backend (`kimari start`) that Open WebUI connects to. Use Kimari for inference + GPU optimization; use Open WebUI when you need a rich web chat experience. See the project's [Open WebUI integration guide](../README.md#open-webui-integration) for setup instructions.

---

## When to Use Kimari

- You have a **GTX 1060 (6 GB)** or **GTX 1080 (8 GB)** and want pre-tuned profiles that work out of the box.
- You want to **predict whether a model will fit** your VRAM before loading it (KimariFit).
- You prefer **CLI-first workflows** and want to script local AI into your dev environment.
- You want a **benchmark framework** to compare models on your actual hardware.
- You want **reproducible model setups** via `kimari pull` from a curated registry.
- You care about **open source (MIT)** and want to inspect/modify every layer.

## When NOT to Use Kimari

- **You need a GUI now.** Kimari has no built-in web UI yet (use Open WebUI or LM Studio instead).
- **You need production stability.** Kimari is alpha — APIs may change, bugs are expected.
- **You have a modern GPU (RTX 3060+).** The GPU profiles and KimariFit scoring are most valuable on old hardware. On modern GPUs, Ollama or llama.cpp work great without optimization help.
- **You need multi-model serving.** Kimari runs one model at a time.
- **You need fine-tuning or training.** Kimari does not include training tools yet.
- **You need RAG, tool-calling, or agents.** These are not yet supported.
- **You're on macOS or CPU-only.** Kimari is NVIDIA + CUDA focused, with experimental ROCm support via `scripts/linux/build-llamacpp-rocm.sh`. If you're on Apple Silicon, Ollama or llama.cpp are better options.

---

## Feature Matrix

| Feature | Kimari | Ollama | LM Studio | llama.cpp | text-gen-webui | KoboldCpp | Open WebUI |
|---------|--------|--------|-----------|-----------|----------------|-----------|------------|
| Built-in CLI | Yes | Yes | No | Yes (binary) | No | No | No |
| Built-in Web UI | No (Open WebUI via Docker) | Partial (API only) | Yes | No | Yes | Yes | Yes |
| GPU profiles per model | Yes | No | Auto-detect only | No | No | Presets | N/A |
| Predict VRAM fit before load | Yes (KimariFit) | No | Visual indicator after load | No | No | No | No |
| Benchmark framework | Yes | No | No | Manual | No | No | No |
| Model registry / pull | Yes | Yes | Yes (Hugging Face) | No | Yes (Hugging Face) | No | No |
| OpenAI-compatible API | Yes | Yes | Yes | Yes (llama-server) | Partial | Yes | Consumes API |
| Fine-tuning support | Planned | No | No | No | Yes | No | No |
| Multi-model serving | No | Yes | Yes | No | No | No | N/A |
| NVIDIA old GPU focus | First-class | Supported | Supported | Supported | Supported | Supported | N/A |
| macOS / Apple Silicon | No | Yes | Yes | Yes | Yes | Yes | Yes |
| CPU-only support | No | Yes | Yes | Yes | Yes | Yes | N/A |
| Open source (OSI) | Yes (MIT) | Yes (MIT) | Source-available | Yes (MIT) | Yes (AGPL) | Yes (AGPL) | Yes (MIT) |
| Maturity | Alpha | Mature | Mature | Very Mature | Mature | Mature | Mature |

---

## The Bottom Line

Kimari is alpha software with a specific mission: **make local LLMs work well on old consumer NVIDIA GPUs**. Its unique contributions — GPU-specific profiles, KimariFit scoring, and a CLI-first benchmark framework — solve real pain points that other tools address only partially or not at all.

But alpha means alpha. If you need stability, a GUI, multi-model serving, or broad hardware support, the mature tools listed above are better choices today. Kimari is the right tool when your hardware is the constraint and you want someone to have already done the tuning work for you.

The local AI ecosystem is not zero-sum. Kimari uses llama.cpp under the hood, integrates with Open WebUI for the chat interface, and exposes the same OpenAI-compatible API that every other tool expects. Pick what fits your situation — and if that's not Kimari yet, check back as the project matures.

---

*Last updated: 2025-03-05 · Kimari v0.1.4-alpha*
