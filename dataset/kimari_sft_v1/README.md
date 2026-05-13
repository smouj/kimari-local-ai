# Kimari SFT v1 Dataset

> **Version**: v0.1.59-alpha  
> **Status**: Seed (320+ examples)  
> **Gate**: BLOCKED — No training yet  
> **Last updated**: 2026-05-13

## Overview

The Kimari SFT v1 dataset is the first supervised fine-tuning dataset for Kimari models. It contains high-quality Spanish and bilingual technical Q&A examples across 8 categories.

## Structure

```
dataset/kimari_sft_v1/
├── sources/
│   ├── spanish_technical.jsonl    — Spanish technical Q&A
│   ├── coding_debug.jsonl         — Programming debugging
│   ├── server_ops.jsonl            — Linux/sysadmin operations
│   ├── local_llm_cuda_gguf.jsonl  — Local AI, CUDA, GGUF, VRAM
│   ├── openclaw_agents.jsonl       — OpenClaw/agent workflows
│   ├── safety_refusal.jsonl       — Safety and refusal behavior
│   ├── json_tooling.jsonl         — JSON/tool use/formatting
│   └── style_consistency.jsonl    — Kimari style consistency
├── manifest.yaml                  — Dataset manifest
├── license_manifest.yaml           — License manifest per source
├── LICENSE_NOTES.md                — License documentation
└── README.md                       — This file
```

## Build Output

```
dataset/build/kimari_sft_v1/
├── train.jsonl          — Training split (90%)
├── validation.jsonl     — Validation split (10%)
├── dataset_summary.json — Statistics and metadata
├── license_manifest.json — License manifest (build output)
└── quality_report.json  — Quality validation report
```

## Categories

| Category | ID Prefix | Target | Focus |
|----------|-----------|--------|-------|
| Spanish Technical | `spanish_technical_` | 40 | DNS, SSL, Docker, systemd, bash |
| Coding Debug | `coding_debug_` | 40 | Python, JS, Git, Docker, SQL |
| Server Ops | `server_ops_` | 40 | Process, disk, user, network, logs |
| Local LLM/CUDA/GGUF | `local_llm_cuda_gguf_` | 40 | llama.cpp, CUDA, VRAM, GGUF |
| OpenClaw/Agents | `openclaw_agents_` | 40 | Setup, workflows, tools, skills |
| Safety/Refusal | `safety_refusal_` | 40 | Harmful refusal, privacy, redirect |
| JSON/Tooling | `json_tooling_` | 40 | Structured output, API, schema |
| Style Consistency | `style_consistency_` | 40 | Tone, vocabulary, formatting |

## Schema

Each example follows the `kimari_sft_item.schema.json` schema:

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
    {"role": "system", "content": "Eres Kimari..."},
    {"role": "user", "content": "..."},
    {"role": "assistant", "content": "..."}
  ]
}
```

## Quality Criteria

| Score | Meaning |
|-------|---------|
| 5 | Excellent — verified, factual, complete |
| 4 | Good — mostly correct, minor gaps |
| 3 | Acceptable — usable but needs review |
| 2 | Draft — needs significant work |
| 1 | Placeholder — not for training |

All examples in this dataset are quality_score 4 or 5.

## What This Dataset Does NOT Contain

- **No PII** — No personal information, real names, addresses, emails
- **No tokens** — No API keys, passwords, auth tokens
- **No private logs** — No real server logs or chat histories
- **No copyrighted content** — All content is project-owned or permissive-license
- **No model outputs** — No outputs from closed-source models without permission
- **No false claims** — No claims that Kimari-4B is released or available
- **No benchmarks** — No public benchmark claims

## Build & Validate

```bash
# Validate dataset
python dataset/scripts/validate_kimari_sft_v1.py --dataset-dir dataset/kimari_sft_v1 --json

# Build train/validation splits
python dataset/scripts/build_kimari_sft_v1.py \
  --dataset-dir dataset/kimari_sft_v1 \
  --output-dir dataset/build/kimari_sft_v1 \
  --train-ratio 0.9 \
  --seed 42 \
  --json
```

## License

All examples are `project-owned` (Apache 2.0) unless otherwise noted in the license manifest. See `LICENSE_NOTES.md` for details.

## Safety

- **Gate**: BLOCKED
- **No training** has been executed with this dataset
- **No HF Jobs** have been submitted
- **No public weights** or adapters have been published
- This dataset is for internal review only