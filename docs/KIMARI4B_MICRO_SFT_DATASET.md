# Kimari-4B Micro SFT Dataset

> **kimari-fit-v0** — Curated dataset for first private adapter run.

## Overview

| Field | Value |
|-------|-------|
| **Name** | kimari-fit-v0 |
| **Format** | JSONL (`prompt`, `response`) |
| **Record count** | 72 |
| **Categories** | cuda_gpu, coding, kimari, technical |
| **Source** | Synthetic/curated |
| **SHA256** | 2a7f55ef157e1be68d1e01daa715d9ae |
| **Private data** | false |
| **Tokens/secrets** | false |

## Categories

| Category | Description | Count |
|----------|-------------|-------|
| **cuda_gpu** | CUDA, GPU, nvidia-smi, compute capability | ~20 |
| **coding** | Python, Bash, scripts, API usage | ~15 |
| **kimari** | Kimari CLI, profiles, configuration, endpoints | ~25 |
| **technical** | Linux, WSL2, systemd, troubleshooting | ~12 |

## Content Focus

- Spanish technical questions and answers
- Linux/WSL2 administration
- CUDA/GPU troubleshooting
- Python/Bash code snippets
- OpenAI-compatible local API usage
- Kimari safety: no false claims, Kimari-4B not released

## Limitations

- Small dataset (72 examples) — intended for validation, not production
- Synthetic/curated — not from real user interactions
- Spanish-focused with some English technical terms
- Not representative of all possible queries

## What This Is NOT

- ❌ A production training dataset
- ❌ Real user data
- ❌ Benchmark data
- ❌ Sufficient for a full model release
- ❌ Contains private data or tokens

## Gate

**BLOCKED** — This dataset is for private validation only. Not for public release.