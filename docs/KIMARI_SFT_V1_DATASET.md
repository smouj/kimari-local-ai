# Kimari SFT v1 Dataset

> **Version**: v0.1.59-alpha  
> **Status**: Seed (320 examples)  
> **Gate**: BLOCKED — No training yet  
> **Last updated**: 2026-05-13

## Purpose

The Kimari SFT v1 dataset provides supervised fine-tuning data for Kimari model lines:

- **Runtime 1.5B** — Fast, technical Spanish assistant
- **Core 3B** — Balanced capability
- **4B Candidate** — Higher capability

This dataset focuses on **Spanish technical assistance** with the Kimari persona: direct, helpful, no filler, honest about uncertainty.

## Categories

| Category | Items | Focus |
|----------|-------|-------|
| Spanish Technical | 40 | DNS, SSL, Docker, systemd, bash, SSH, PostgreSQL |
| Coding Debug | 40 | Python, JS, Git, Docker, SQL, API debugging |
| Server Ops | 40 | Process, disk, user, network, log, cron management |
| Local LLM / CUDA / GGUF | 40 | llama.cpp, CUDA, VRAM, GGUF, hardware, serving |
| OpenClaw / Agents | 40 | Setup, workflows, tools, skills, debugging |
| Safety / Refusal | 40 | Harmful request refusal, privacy, safe alternatives |
| JSON / Tooling | 40 | Structured output, API, schema, config, error handling |
| Style Consistency | 40 | Tone, vocabulary, honesty, formatting, conciseness |

**Total: 320 examples (seed stage)**

## Format

Each example is a JSON object in JSONL format:

```json
{
  "id": "spanish_technical_001",
  "category": "spanish_technical",
  "language": "es",
  "source": "kimari-authored",
  "license": "project-owned",
  "quality_score": 5,
  "tags": ["dns", "networking", "troubleshooting"],
  "messages": [
    {"role": "system", "content": "Eres Kimari, un asistente técnico..."},
    {"role": "user", "content": "..."},
    {"role": "assistant", "content": "..."}
  ]
}
```

## License

All examples are **project-owned** (Apache 2.0). No data from external sources with unclear licensing.

## What This Dataset Does NOT Contain

- ❌ No PII (personal information, real names, emails)
- ❌ No tokens (API keys, passwords, auth tokens)
- ❌ No private logs or chat histories
- ❌ No copyrighted content without clear license
- ❌ No outputs from closed-source models without permission
- ❌ No claims that Kimari-4B is released or available
- ❌ No public benchmark claims
- ❌ No destructive commands without safety warnings

## Build & Validate

```bash
# Validate
python dataset/scripts/validate_kimari_sft_v1.py --dataset-dir dataset/kimari_sft_v1 --json

# Build train/validation splits
python dataset/scripts/build_kimari_sft_v1.py \
  --dataset-dir dataset/kimari_sft_v1 \
  --output-dir dataset/build/kimari_sft_v1 \
  --train-ratio 0.9 --seed 42 --json
```

## Safety

- **Gate**: BLOCKED
- **No training** has been executed with this dataset
- **No HF Jobs** have been submitted
- **No public weights** or adapters have been published
- This dataset is for internal review only