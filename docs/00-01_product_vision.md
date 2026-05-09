# Kimari Product Vision

## Document: 00-01 Product Vision
**Version:** 0.1.0
**Status:** Draft
**Last Updated:** 2025

---

## Executive Summary

Kimari is an open-source local AI platform designed to make capable language models accessible on consumer-grade hardware. Our mission is to democratize AI by enabling anyone with a mid-range GPU to run, fine-tune, and benefit from local AI — without cloud dependencies, subscriptions, or data privacy concerns.

## Vision Statement

> "AI that runs on your desk, not in someone else's data center."

We believe that the next wave of AI adoption will be driven by local deployment. As models become more efficient and hardware more capable, the economics of local AI will surpass cloud-only solutions for many use cases. Kimari is positioned to be the platform that makes this transition seamless.

## Goals

### Primary Goals

1. **Run on Consumer Hardware** — Full AI capabilities on GPUs as modest as a GTX 1060 (6 GB)
2. **Zero Configuration** — Works out of the box with sensible defaults and auto-detection
3. **Privacy First** — All processing is local; no data leaves the user's machine
4. **Open Source** — MIT licensed; no lock-in, no hidden telemetry
5. **Developer Friendly** — CLI, API, and IDE integrations that feel natural

### Secondary Goals

6. **Cross-Platform** — First-class Linux and Windows support
7. **Extensible** — Plugin system for additional capabilities
8. **Community Driven** — Profiles, skills, and models contributed by the community
9. **Educational** — Transparent about how models work and their limitations

## Target Audience

### Primary Users

| Segment | Description | Typical Hardware |
|---------|-------------|-----------------|
| **Indie Developers** | Solo developers building side projects | GTX 1060–1080, 8–16 GB RAM |
| **Students** | CS/AI students learning LLMs | GTX 1060, 8 GB RAM |
| **Privacy-Conscious Professionals** | Lawyers, doctors, researchers | GTX 1080–RTX 3060 |
| **IT Professionals** | Sysadmins, DevOps engineers | GTX 1060+, Linux workstations |

### Secondary Users

| Segment | Description |
|---------|-------------|
| **Small Teams** | Startups that can't justify API costs |
| **Offline Users** | Users in areas with unreliable internet |
| **AI Enthusiasts** | Hobbyists experimenting with local models |
| **Educators** | Teaching AI without cloud dependencies |

## Market Position

### Comparison with Existing Solutions

| Feature | Kimari | Ollama | LM Studio | Text Generation WebUI |
|---------|--------|--------|-----------|----------------------|
| **Consumer GPU Focus** | ★★★★★ | ★★★ | ★★ | ★★ |
| **Auto GPU Detection** | ★★★★★ | ★★★ | ★★★★ | ★★★ |
| **GPU Profiles** | ★★★★★ | ★★ | ★★★ | ★★ |
| **KimariFit Scoring** | ★★★★★ | — | — | — |
| **CLI** | ★★★★ | ★★★★★ | ★★ | ★ |
| **Web UI** | Via Open WebUI | Built-in | Built-in | Built-in |
| **IDE Integration** | ★★★★★ (Continue) | ★★★ | ★★ | ★ |
| **Fine-Tuning Tools** | Planned | ★★ | ★ | ★★★★ |
| **Windows Support** | ★★★★ | ★★★ | ★★★★★ | ★★★ |
| **Bilingual (EN/ES)** | ★★★★ | ★★ | ★★ | ★ |

### Our Differentiators

1. **KimariFit Score** — A unique scoring system that predicts model performance on your specific hardware before you even start
2. **Consumer GPU Profiles** — Pre-configured settings for specific GPU models (not just VRAM tiers)
3. **Bilingual Focus** — First-class English and technical Spanish support
4. **Skill System** — Define and evaluate model capabilities across domains
5. **Lightweight** — Minimal dependencies; Python + llama.cpp is all you need

## Philosophy

### What We Believe

- **Local is the future** — As models shrink and hardware improves, local AI will become the default
- **Privacy is a feature, not a compromise** — Local processing isn't a limitation; it's an advantage
- **Accessible hardware is enough** — You don't need an A100 to do useful AI work
- **Open source wins** — Transparency and community collaboration produce better software
- **Simplicity over features** — A tool that works out of the box beats a tool with a thousand options

### What We Don't Do

- We don't send telemetry or analytics
- We don't require an internet connection
- We don't bundle unnecessary dependencies
- We don't lock you into a proprietary format
- We don't distribute model weights (licensing and size reasons)

## Success Metrics

| Metric | v0.1 Target | v1.0 Target |
|--------|-------------|-------------|
| Tokens/second (GTX 1060) | > 15 t/s | > 25 t/s |
| Time to first token | < 2s | < 1s |
| Supported GPU profiles | 3 | 10+ |
| Benchmark pass rate | 70% | 90% |
| GitHub stars | — | 1,000 |
| Active contributors | 1 | 10+ |

## Roadmap Overview

### Phase 1: Foundation (v0.1 — Current)
- Core CLI with doctor, start, stop, chat commands
- GPU profiles for GTX 1060 and GTX 1080
- llama.cpp integration with CUDA
- KimariFit scoring system
- Open WebUI compatibility

### Phase 2: Enhancement (v0.2)
- Additional GPU profiles (RTX series)
- Benchmark framework and prompts
- Evaluation suite
- Windows improvements
- Documentation and tutorials

### Phase 3: Intelligence (v0.5)
- Fine-tuned model (Kimari-4B-Instruct)
- Coding-specialized variant
- Technical Spanish improvements
- Agent capabilities
- PWA frontend

### Phase 4: Platform (v1.0)
- Desktop app (Tauri)
- Plugin system
- Model marketplace
- Multi-GPU support
- Community hub

---

*This document is a living artifact. It will be updated as the project evolves.*
