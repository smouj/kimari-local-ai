# Project Truth — What Kimari Is and Isn't

> This document exists to prevent confusion, inflated expectations, and unfair criticism.

## What Kimari Is

- A **local AI framework and CLI** for running language models on consumer NVIDIA GPUs.
- A **GGUF/llama.cpp workflow** designed for older GPUs (GTX 1060, GTX 1080).
- A **local OpenAI-compatible endpoint** helper that manages llama-server lifecycle.
- A **Gateway Dashboard** for monitoring and managing the local AI environment.
- An **integration tool** for Open WebUI, Continue.dev, OpenClaw, and Hermes.
- **Open-source** (MIT license). Python + TypeScript/Next.js stack.
- **Local-first.** No cloud dependency. No telemetry. No subscriptions.

## What Kimari Is NOT

- **Not a new inference engine.** Kimari uses llama.cpp under the hood. It organizes, diagnoses, configures, profiles, documents and integrates llama.cpp for hardware-limited users.
- **Not a public Kimari-4B model.** No Kimari-4B weights, adapters or GGUF files are publicly available. The gate is `BLOCKED`.
- **Not a production server.** This is alpha software. Useful today, but not production-ready.
- **Not a benchmark leaderboard.** No public benchmark claims are made. Performance numbers shown in documentation are validated test results (TinyLlama), not Kimari-4B benchmarks.
- **Not a replacement for Ollama, LM Studio or text-generation-webui.** Kimari is a complementary tool focused on older GPU optimization and honest alpha development.

## Current State (v0.1.87-alpha)

| Area | Status |
|---|---|
| Framework / CLI | ✅ Usable alpha |
| Local GGUF runtime | ✅ Working (with llama-server) |
| OpenAI-compatible endpoint | ✅ Working |
| GTX 1060 validation | ✅ Validated with TinyLlama test model |
| Gateway Dashboard | ✅ Local preview (127.0.0.1:3105) |
| One-command install | ✅ install.sh / install.ps1 |
| Private adapter experiments | 🔒 Private (SFT v2 on SmolLM3-3B) |
| Private manual review | 🔒 Completed (safety_fix_required) |
| Public Kimari-4B weights | ❌ Not released |
| Public GGUF Kimari model | ❌ Not released |
| Public benchmark claims | ❌ None |
| Release gate | 🔒 BLOCKED |

## Label Legend

Throughout Kimari documentation and the GitHub Pages site, you will see data labeled as:

| Label | Meaning |
|---|---|
| `VALIDATED` | Measured result from real hardware, reproducible |
| `ESTIMATED` | Reasoned projection based on similar hardware/models |
| `SIMULATED UI` | Visual demo without real data backend |
| `PLANNED` | Feature exists only in roadmap |
| `NOT RELEASED` | Exists privately but not available publicly |

When in doubt about a claim, assume it is **NOT VALIDATED** unless explicitly marked `VALIDATED`.

## Safety Commitments

- No telemetry. No phone home. No analytics on user machines.
- Default bind is `127.0.0.1`. Non-local bind requires explicit flag.
- No public Kimari-4B weights until safety regressions are fixed.
- No benchmark claims without reproducible validation.
- No GGUF export until manual review passes without safety issues.
- Model registry hashes will be pinned before models reach `recommended` status.

---

*This document is a living commitment to honesty. If any claim becomes inaccurate, this file will be updated before the next public commit.*
